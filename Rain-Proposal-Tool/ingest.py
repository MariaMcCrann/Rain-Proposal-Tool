"""
Turns an uploaded RFQ file into plain text for extract_rfq.py to work on.

Honest limitation: scanned/image PDFs have no text layer, so pdfplumber
will return little or nothing for them. This module detects that case and
flags it rather than silently returning garbage - OCR for scanned PDFs is
not built yet (see SCANNED_PDF_WARNING below).
"""

import os
import pdfplumber
import docx

SCANNED_PDF_WARNING = (
    "This PDF returned almost no extractable text, which usually means it's "
    "a scanned/image PDF rather than a text PDF. OCR isn't wired up yet - "
    "for now, this file can't be processed automatically."
)


class UnsupportedFileError(Exception):
    pass


class ScannedPdfError(Exception):
    pass


def extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".txt":
        with open(file_path, "r", errors="ignore") as f:
            return f.read()

    if ext == ".pdf":
        text_parts = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        text = "\n".join(text_parts)
        if len(text.strip()) < 50:
            raise ScannedPdfError(SCANNED_PDF_WARNING)
        return text

    if ext == ".docx":
        document = docx.Document(file_path)
        return "\n".join(p.text for p in document.paragraphs)

    raise UnsupportedFileError(f"Unsupported file type: {ext}. Use .pdf, .docx, or .txt")
