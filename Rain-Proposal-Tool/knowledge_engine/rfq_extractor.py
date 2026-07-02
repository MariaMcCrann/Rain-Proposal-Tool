# knowledge_engine/rfq_extractor.py

import re


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def find_first(patterns, text, default=""):
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
    return default


def extract_address(text: str) -> str:
    patterns = [
        r"(\d+\s+[A-Za-z0-9\s\-']+\s+(?:Road|Rd|Street|St|Avenue|Ave|Drive|Dr|Court|Ct|Lane|Ln|Highway|Hwy)\s*,?\s*[A-Za-z\s]+)",
        r"Project\s+Location[:\s]+(.+)",
        r"Site\s+Location[:\s]+(.+)",
        r"Address[:\s]+(.+)",
    ]
    return find_first(patterns, text)


def extract_project_title(text: str, address: str = "") -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for line in lines[:12]:
        if "scope of works" in line.lower() or "proposal" in line.lower():
            return line

    if address:
        return f"{address} Engineering Proposal"

    return "Draft Engineering Proposal"


def extract_client(text: str) -> str:
    if "livv.com.au" in text.lower() or "livv developments" in text.lower():
        return "Livv Developments"

    return find_first([
        r"Client[:\s]+(.+)",
        r"Prepared for[:\s]+(.+)",
    ], text, "Not stated")


def extract_background(text: str) -> str:
    match = re.search(
        r"1\.\s*Project Background(.*?)(?:2\.\s*Scope of Works|Scope of Works)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if match:
        return match.group(1).strip()

    paragraphs = text.split("\n\n")
    for p in paragraphs:
        if len(p) > 120:
            return p.strip()

    return "Project background not clearly stated in the RFQ."


def extract_phases(text: str) -> list:
    phases = []

    phase_pattern = re.compile(
        r"(Phase\s+\d+(?:\.\d+)?[:\s\-]+.*?)(?=Phase\s+\d+(?:\.\d+)?[:\s\-]+|3\.\s*Deliverables|$)",
        re.IGNORECASE | re.DOTALL,
    )

    for match in phase_pattern.finditer(text):
        block = match.group(1).strip()
        lines = [line.strip(" •-\t") for line in block.splitlines() if line.strip()]

        phase_name = lines[0] if lines else "Unnamed phase"
        deliverables = []

        for line in lines[1:]:
            if len(line) > 8:
                deliverables.append(line)

        phases.append({
            "phase_name": phase_name,
            "deliverables": deliverables[:12],
        })

    if not phases:
        phases.append({
            "phase_name": "Scope of Works",
            "deliverables": ["Review RFQ and confirm required engineering scope."],
        })

    return phases


def extract_authorities(text: str) -> list:
    authorities = []

    known_terms = {
        "CoGG": "City of Greater Geelong",
        "CCMA": "Corangamite Catchment Management Authority",
        "Barwon Water": "Barwon Water",
        "VicPlan": "VicPlan planning controls",
        "DPO": "Development Plan Overlay",
        "ARR": "Australian Rainfall and Runoff",
        "MUSIC": "MUSIC stormwater quality modelling",
        "RORB": "RORB hydrologic modelling",
        "TUFLOW": "TUFLOW hydraulic modelling",
    }

    for term, label in known_terms.items():
        if term.lower() in text.lower():
            authorities.append(label)

    return list(dict.fromkeys(authorities))


def extract_fee_basis(text: str) -> list:
    items = []

    if "fixed fee" in text.lower():
        items.append("Fixed fee components identified.")
    if "t&m" in text.lower() or "time and materials" in text.lower():
        items.append("Time and materials component identified.")
    if "acea" in text.lower() or "sliding scale" in text.lower():
        items.append("ACEA sliding scale / percentage fee basis identified.")

    return items


def extract_rfq_data(text: str) -> dict:
    text = clean_text(text)

    address = extract_address(text)
    project_title = extract_project_title(text, address)

    return {
        "project_title": project_title,
        "client": extract_client(text),
        "site_address": address,
        "site_location": address,
        "background": extract_background(text),
        "phases": extract_phases(text),
        "authority_requirements": extract_authorities(text),
        "fee_basis_notes": extract_fee_basis(text),
        "raw_text_preview": text[:3000],
    }