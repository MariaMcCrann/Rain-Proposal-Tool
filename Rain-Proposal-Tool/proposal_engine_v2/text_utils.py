import re
from typing import List, Optional


def clean_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\x00", " ")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def clean_line(line: str) -> str:
    line = re.sub(r"\s+", " ", line or "").strip()
    return line.strip(" -:|•\t")


def get_lines(text: str) -> List[str]:
    return [
        clean_line(line)
        for line in clean_text(text).splitlines()
        if clean_line(line)
    ]


def first_regex_match(patterns: List[str], text: str) -> Optional[str]:
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            value = clean_line(match.group(1))
            if value:
                return value
    return None


def collapse_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def truncate(value: str, limit: int = 1200) -> str:
    value = collapse_spaces(value)
    if len(value) <= limit:
        return value
    return value[:limit].rstrip() + "..."
