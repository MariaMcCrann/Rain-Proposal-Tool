# extract_rfq.py

import os
import re
from typing import Dict, Any

from pypdf import PdfReader
from docx import Document

from research_site import extract_site_address


def read_pdf_text(file_path: str) -> str:
    text_parts = []

    reader = PdfReader(file_path)

    for page in reader.pages:
        page_text = page.extract_text() or ""
        text_parts.append(page_text)

    return "\n".join(text_parts).strip()


def read_docx_text(file_path: str) -> str:
    doc = Document(file_path)
    text_parts = []

    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            text_parts.append(paragraph.text.strip())

    for table in doc.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if cells:
                text_parts.append(" | ".join(cells))

    return "\n".join(text_parts).strip()


def read_uploaded_file_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return read_pdf_text(file_path)

    if ext == ".docx":
        return read_docx_text(file_path)

    if ext in [".txt", ".md"]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    raise ValueError(f"Unsupported file type: {ext}")


def clean_project_title(filename: str) -> str:
    name = os.path.basename(filename)
    name = os.path.splitext(name)[0]
    name = name.replace("_", " ").replace("-", " ")
    name = re.sub(r"\s+", " ", name).strip()
    return name


def extract_project_type(text: str) -> str:
    text_l = text.lower()

    if "subdivision" in text_l:
        return "Subdivision"
    if "industrial" in text_l:
        return "Industrial development"
    if "residential" in text_l:
        return "Residential development"
    if "stormwater" in text_l:
        return "Stormwater assessment"
    if "flood" in text_l:
        return "Flood assessment"
    if "hydrological" in text_l or "hydrology" in text_l:
        return "Hydrological engineering services"

    return "Engineering services"


def extract_scope_summary(text: str) -> str:
    """
    Keeps this simple and stable.
    The proposal writer can expand this later.
    """

    text_l = text.lower()

    if "phase 3" in text_l or "phase 4" in text_l or "phase 5" in text_l:
        return "Hydrological engineering services for remaining project phases."

    if "scope of works" in text_l:
        return "Engineering scope of works based on the RFQ."

    return "Engineering services based on the RFQ."


def extract_rfq(file_path: str) -> Dict[str, Any]:
    """
    Main RFQ extractor.

    Returns:
    - full_text
    - project_title
    - site_address
    - project_type
    - scope_summary
    """

    full_text = read_uploaded_file_text(file_path)
    project_title = clean_project_title(file_path)

    site_address = extract_site_address(full_text, project_title)

    extracted = {
        "file_name": os.path.basename(file_path),
        "project_title": project_title,
        "site_address": site_address,
        "project_type": extract_project_type(full_text),
        "scope_summary": extract_scope_summary(full_text),
        "full_text": full_text,
    }

    return extracted

def _derive_project_title(full_text: str) -> str:
    if not full_text:
        return "Untitled Project"

    patterns = [
        r"(?:project\s*title|project\s*name|project)\s*[:\-]\s*(.+)",
        r"(?:re|subject)\s*[:\-]\s*(.+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            title = re.split(r"[\r\n]", title)[0].strip()
            if title:
                return title

    for line in full_text.splitlines():
        line = line.strip()
        if line:
            return line[:120]

    return "Untitled Project"

def extract_rfq_data(full_text: str) -> Dict[str, Any]:
    """
    Extracts RFQ fields directly from already-extracted text (e.g. text
    already read from one or more uploaded files and combined by the
    caller). Unlike extract_rfq(), this does not read files from disk.

    Returns:
    - full_text
    - project_title
    - site_address
    - project_type
    - scope_summary
    """
    project_title = _derive_project_title(full_text)
    site_address = extract_site_address(full_text, project_title)

    return {
        "project_title": project_title,
        "site_address": site_address,
        "project_type": extract_project_type(full_text),
        "scope_summary": extract_scope_summary(full_text),
        "full_text": full_text,
    }
