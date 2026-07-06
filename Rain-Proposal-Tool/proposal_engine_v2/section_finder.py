import re
from dataclasses import dataclass
from typing import Dict, List

from .text_utils import clean_text, clean_line


@dataclass
class DocumentSection:
    heading: str
    body: str


SECTION_ALIASES = {
    "background": [
        "background",
        "project background",
        "introduction",
        "overview",
        "project overview",
        "project description",
        "development description",
    ],
    "scope": [
        "scope",
        "scope of works",
        "services",
        "services required",
        "required services",
        "consultant scope",
    ],
    "deliverables": [
        "deliverables",
        "outputs",
        "reporting",
        "submission requirements",
    ],
    "phases": [
        "phase",
        "staging",
        "project stages",
        "stages",
    ],
    "authority_requirements": [
        "authority requirements",
        "planning requirements",
        "planning controls",
        "approvals",
        "permit requirements",
        "regulatory requirements",
    ],
    "assumptions": [
        "assumptions",
        "information provided",
        "client inputs",
    ],
    "exclusions": [
        "exclusions",
        "out of scope",
        "not included",
    ],
    "program": [
        "program",
        "timeline",
        "timeframe",
        "schedule",
    ],
    "fees": [
        "fees",
        "fee proposal",
        "commercial",
        "pricing",
    ],
}


def normalise_heading(value: str) -> str:
    value = clean_line(value).lower()
    value = re.sub(r"^\d+(\.\d+)*\s+", "", value)
    value = re.sub(r"[^a-z0-9 ]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def classify_heading(heading: str) -> str:
    heading_n = normalise_heading(heading)

    for section_type, aliases in SECTION_ALIASES.items():
        for alias in aliases:
            alias_n = normalise_heading(alias)

            if heading_n == alias_n:
                return section_type

            if heading_n.startswith(alias_n + " "):
                return section_type

            if alias_n in heading_n and len(heading_n) <= 80:
                return section_type

    if re.match(r"phase\s*\d+", heading_n):
        return "phases"

    return ""


def looks_like_heading(line: str) -> bool:
    line = clean_line(line)

    if not line:
        return False

    if len(line) > 100:
        return False

    if line.endswith(".") and len(line.split()) > 6:
        return False

    numbered = bool(re.match(r"^\d+(\.\d+)*\s+[A-Za-z]", line))
    all_caps = line.isupper() and len(line.split()) <= 10
    known = bool(classify_heading(line))
    phase = bool(re.match(r"^phase\s*\d+", line, re.IGNORECASE))

    return numbered or all_caps or known or phase


def split_into_sections(full_text: str) -> List[DocumentSection]:
    text = clean_text(full_text)

    sections: List[DocumentSection] = []
    current_heading = "Document Start"
    current_body: List[str] = []

    for raw_line in text.splitlines():
        line = clean_line(raw_line)

        if not line:
            continue

        if looks_like_heading(line):
            if current_body:
                sections.append(
                    DocumentSection(
                        heading=current_heading,
                        body="\n".join(current_body).strip(),
                    )
                )

            current_heading = line
            current_body = []
        else:
            current_body.append(line)

    if current_body:
        sections.append(
            DocumentSection(
                heading=current_heading,
                body="\n".join(current_body).strip(),
            )
        )

    return sections


def group_sections_by_type(full_text: str) -> Dict[str, List[DocumentSection]]:
    grouped: Dict[str, List[DocumentSection]] = {}

    for section in split_into_sections(full_text):
        section_type = classify_heading(section.heading)

        if not section_type:
            section_type = "other"

        grouped.setdefault(section_type, []).append(section)

    return grouped


def get_section_text(full_text: str, section_type: str) -> str:
    grouped = group_sections_by_type(full_text)
    sections = grouped.get(section_type, [])

    return "\n\n".join(section.body for section in sections if section.body).strip()


def get_section_bodies(full_text: str, section_type: str) -> List[str]:
    grouped = group_sections_by_type(full_text)
    return [section.body for section in grouped.get(section_type, []) if section.body]
