import re
from typing import List

from .models import ContactInfo, ProjectPhase, RFQExtract
from .text_utils import clean_text, clean_line, get_lines, first_regex_match, collapse_spaces, truncate
from .section_finder import get_section_text, get_section_bodies

ADDRESS_WORDS = [
    "road", "rd", "street", "st", "avenue", "ave", "drive", "dr",
    "court", "ct", "crescent", "cres", "lane", "ln", "place", "pl",
    "highway", "hwy", "parade", "pde", "way", "boulevard", "blvd",
    "terrace", "tce", "close", "cl",
]


BAD_ADDRESS_PHRASES = [
    "specific data",
    "soil and landscape",
    "background",
    "scope",
    "proposal",
    "deliverables",
    "methodology",
    "assessment",
    "hydrological engineering scope",
    "phase",
]


def looks_like_street_address(value: str) -> bool:
    value = clean_line(value)
    if not value or len(value) > 140:
        return False

    value_l = value.lower()

    if any(phrase in value_l for phrase in BAD_ADDRESS_PHRASES):
        return False

    has_number = bool(re.search(r"\b\d{1,6}[a-zA-Z]?\b", value))
    has_road_word = any(re.search(rf"\b{re.escape(word)}\b", value_l) for word in ADDRESS_WORDS)

    return has_number and has_road_word


def clean_address(value: str) -> str:
    value = collapse_spaces(value)

    junk = [
        "Hydrological Engineering Scope Of Works",
        "Hydrological Engineering Scope of Works",
        "Scope Of Works",
        "Scope of Works",
        ".pdf",
        "pdf",
        "v1",
        "v2",
    ]

    for item in junk:
        value = re.sub(re.escape(item), "", value, flags=re.IGNORECASE)

    value = collapse_spaces(value).strip(" -,_.")

    if value and "vic" not in value.lower() and "victoria" not in value.lower():
        value += " VIC"

    return value


def extract_site_address(full_text: str) -> str:
    text = clean_text(full_text)
    lines = get_lines(text)

    labelled_patterns = [
        r"(?:site address|property address|subject site|site location|project address|location)\s*[:\-|]\s*(.+)",
        r"(?:address)\s*[:\-|]\s*(.+)",
    ]

    labelled = first_regex_match(labelled_patterns, text)
    if labelled and looks_like_street_address(labelled):
        return clean_address(labelled)

    street_pattern = re.compile(
        r"\b\d{1,6}[A-Za-z]?\s+[A-Za-z0-9 '\-]+?\s+"
        r"(?:Road|Rd|Street|St|Avenue|Ave|Drive|Dr|Court|Ct|Crescent|Cres|Lane|Ln|Place|Pl|"
        r"Highway|Hwy|Parade|Pde|Way|Boulevard|Blvd|Terrace|Tce|Close|Cl)"
        r"(?:,\s*[A-Za-z '\-]+)?(?:\s+VIC|\s+Victoria)?(?:\s+\d{4})?",
        re.IGNORECASE,
    )

    candidates = []

    for line in lines:
        for match in street_pattern.finditer(line):
            candidate = clean_address(match.group(0))
            if looks_like_street_address(candidate):
                candidates.append(candidate)

    if candidates:
        return max(candidates, key=len)

    return ""


def extract_project_title(full_text: str, site_address: str = "") -> str:
    text = clean_text(full_text)

    matched = first_regex_match(
        [
            r"(?:project title|project name)\s*[:\-|]\s*(.+)",
            r"(?:re|subject)\s*[:\-|]\s*(.+)",
        ],
        text,
    )

    if matched and 8 <= len(matched) <= 160:
        return matched

    if site_address:
        return f"{site_address} - Hydrological Engineering Services"

    for line in get_lines(text):
        if line.startswith("--- Source file:"):
            continue
        if 8 <= len(line) <= 160:
            return line

    return "Untitled Project"


def extract_project_type(full_text: str) -> str:
    text_l = clean_text(full_text).lower()

    if "industrial subdivision" in text_l:
        return "Industrial subdivision"
    if "residential subdivision" in text_l:
        return "Residential subdivision"
    if "subdivision" in text_l:
        return "Subdivision"
    if "development plan overlay" in text_l or "dpo" in text_l:
        return "Development planning / hydrological assessment"
    if "stormwater management" in text_l:
        return "Stormwater management assessment"
    if "flood" in text_l:
        return "Flood assessment"
    if "hydrological" in text_l or "hydrology" in text_l:
        return "Hydrological engineering services"

    return "Engineering services"


def extract_background(full_text: str) -> str:
    section_text = get_section_text(full_text, "background")

    if section_text:
        return truncate(section_text, 1200)

    text = clean_text(full_text)

    useful_lines = []
    keywords = [
        "proposed", "development", "subdivision", "site", "planning",
        "hydrological", "stormwater", "flood", "phase", "overlay",
    ]

    for line in get_lines(text):
        line_l = line.lower()
        if any(k in line_l for k in keywords) and len(line) > 40:
            useful_lines.append(line)
        if len(useful_lines) >= 5:
            break

    return truncate(" ".join(useful_lines), 1200)


def extract_scope_summary(full_text: str) -> str:
    section_text = get_section_text(full_text, "scope")

    if section_text:
        return truncate(section_text, 1200)

    return f"{extract_project_type(full_text)} based on the RFQ documentation."


def extract_deliverables(full_text: str) -> List[str]:
    lines = get_lines(full_text)

    deliverables = []
    keywords = [
        "prepare", "undertake", "review", "develop", "provide", "assess",
        "model", "calculate", "document", "report", "meeting", "submission",
        "liaise", "confirm",
    ]

    for line in lines:
        line_l = line.lower()
        if any(line_l.startswith(k) or f" {k} " in line_l for k in keywords):
            if 15 <= len(line) <= 240 and line not in deliverables:
                deliverables.append(line)

        if len(deliverables) >= 14:
            break

    return deliverables


def extract_phases(full_text: str) -> List[ProjectPhase]:
    lines = get_lines(full_text)
    phases = []
    current = None

    phase_heading = re.compile(r"^(phase\s*\d+[^\n:]*)(?:[:\-])?", re.IGNORECASE)

    for line in lines:
        heading = phase_heading.match(line)

        if heading:
            if current:
                phases.append(current)

            current = ProjectPhase(name=clean_line(heading.group(1)), deliverables=[])

            remainder = clean_line(line[heading.end():])
            if remainder:
                current.deliverables.append(remainder)

            continue

        if current:
            if len(line) > 8 and not line.lower().startswith(("page ", "figure ", "table ")):
                if len(current.deliverables) < 10:
                    current.deliverables.append(line)

    if current:
        phases.append(current)

    if phases:
        return phases[:8]

    deliverables = extract_deliverables(full_text)
    if deliverables:
        return [ProjectPhase(name="Scope of Works", deliverables=deliverables)]

    return []


def extract_authority_requirements(full_text: str) -> List[str]:
    section_text = get_section_text(full_text, "authority_requirements")
    lines = get_lines(section_text or full_text)

    keywords = [
        "planning scheme", "development plan overlay", "dpo", "council",
        "authority", "melbourne water", "cma", "catchment management",
        "stormwater management", "flood", "sbo", "lsio", "fo",
        "australian rainfall and runoff", "arr2019", "water sensitive urban design",
    ]

    results = []

    for line in lines:
        line_l = line.lower()
        if any(k in line_l for k in keywords):
            if 15 <= len(line) <= 280 and line not in results:
                results.append(line)

        if len(results) >= 14:
            break

    return results

def extract_contact(full_text: str) -> ContactInfo:
    text = clean_text(full_text)
    contact = ContactInfo()

    email = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    if email:
        contact.email = email.group(0)

    phone = re.search(r"(?:\+?61|0)[\d\s().-]{8,}\d", text)
    if phone:
        contact.phone = clean_line(phone.group(0))

    name = first_regex_match(
        [
            r"(?:contact person|contact name|attention|attn)\s*[:\-|]\s*(.+)",
            r"(?:prepared by|request from)\s*[:\-|]\s*(.+)",
        ],
        text,
    )
    if name and len(name) <= 80:
        contact.name = name

    company = first_regex_match(
        [
            r"(?:company|organisation|organization|client)\s*[:\-|]\s*(.+)",
        ],
        text,
    )
    if company and len(company) <= 120:
        contact.company = company

    return contact


def extract_rfq_data(full_text: str) -> RFQExtract:
    text = clean_text(full_text)

    site_address = extract_site_address(text)
    project_title = extract_project_title(text, site_address)
    background = extract_background(text)
    phases = extract_phases(text)
    deliverables = extract_deliverables(text)

    notes = []

    if not site_address:
        notes.append("No reliable street address was found in the RFQ text.")

    if not background:
        notes.append("No clear project background section was found.")

    if not phases and not deliverables:
        notes.append("No clear phases or deliverables were found.")

    return RFQExtract(
        project_title=project_title,
        project_type=extract_project_type(text),
        site_address=site_address,
        background=background,
        scope_summary=extract_scope_summary(text),
        phases=phases,
        deliverables=deliverables,
        authority_requirements=extract_authority_requirements(text),
        contact=extract_contact(text),
        extraction_notes=notes,
        full_text=text,
    )
