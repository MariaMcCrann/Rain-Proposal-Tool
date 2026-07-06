import re

from .types import AnalyzerResult
from ..text_utils import clean_text, clean_line, get_lines, truncate


PROJECT_TYPE_RULES = [
    ("Industrial subdivision", ["industrial subdivision"]),
    ("Residential subdivision", ["residential subdivision"]),
    ("Subdivision", ["subdivision"]),
    ("Development planning / hydrological assessment", ["development plan overlay", "dpo"]),
    ("Stormwater management assessment", ["stormwater management", "stormwater strategy"]),
    ("Flood assessment", ["flood assessment", "flood study", "flood modelling"]),
    ("Hydrological engineering services", ["hydrological", "hydrology"]),
]


BACKGROUND_KEYWORDS = [
    "proposed",
    "development",
    "subdivision",
    "site",
    "planning",
    "stormwater",
    "flood",
    "hydrological",
    "overlay",
    "phase",
]


class ProjectAnalyzer:
    name = "Project Analyzer"

    def analyse(self, full_text: str, site_address: str = "") -> AnalyzerResult:
        result = AnalyzerResult(self.name)
        text = clean_text(full_text)

        title, title_score, title_source = self._find_project_title(text, site_address)
        project_type, type_score, type_source = self._find_project_type(text)
        background, bg_score, bg_source = self._find_background(text)
        stage, stage_score, stage_source = self._find_project_stage(text)

        result.add("project_title", title, title_score, title_source)
        result.add("project_type", project_type, type_score, type_source)
        result.add("background", background, bg_score, bg_source)
        result.add("project_stage", stage, stage_score, stage_source)

        return result

    def _find_project_title(self, text: str, site_address: str):
        patterns = [
            r"(?:project title|project name)\s*[:\-|]\s*(.+)",
            r"(?:re|subject)\s*[:\-|]\s*(.+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                title = clean_line(match.group(1))
                title = re.split(r"[\r\n]", title)[0].strip()
                if 8 <= len(title) <= 160:
                    return title, 0.90, match.group(0)

        if site_address:
            return f"{site_address} - Hydrological Engineering Services", 0.82, site_address

        for line in get_lines(text):
            if line.startswith("--- Source file:"):
                continue
            if 12 <= len(line) <= 140:
                return line, 0.55, line

        return "Untitled Project", 0.20, ""

    def _find_project_type(self, text: str):
        text_l = text.lower()

        for project_type, keywords in PROJECT_TYPE_RULES:
            for keyword in keywords:
                idx = text_l.find(keyword)
                if idx >= 0:
                    source = text[max(0, idx - 80): idx + 180]
                    return project_type, 0.90, clean_line(source)

        return "Engineering services", 0.45, ""

    def _find_background(self, text: str):
        patterns = [
            r"(?:project background|background|introduction|project overview|overview)\s*[:\n]\s*(.+?)(?=\n\s*(?:scope|services|deliverables|methodology|phase|requirements|fees|program|timeline)\b|\Z)",
            r"(?:development description|project description)\s*[:\n]\s*(.+?)(?=\n\s*(?:scope|services|deliverables|methodology|phase|requirements|fees|program|timeline)\b|\Z)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                value = truncate(match.group(1), 1200)
                if len(value) > 40:
                    return value, 0.88, clean_line(match.group(0)[:300])

        useful_lines = []

        for line in get_lines(text):
            line_l = line.lower()
            if any(k in line_l for k in BACKGROUND_KEYWORDS) and len(line) > 40:
                useful_lines.append(line)
            if len(useful_lines) >= 5:
                break

        if useful_lines:
            value = truncate(" ".join(useful_lines), 1200)
            return value, 0.62, useful_lines[0]

        return "", 0.0, ""

    def _find_project_stage(self, text: str):
        phase_matches = re.findall(r"\bphase\s*\d+\b", text, re.IGNORECASE)

        if phase_matches:
            unique = []
            for item in phase_matches:
                item = clean_line(item.title())
                if item not in unique:
                    unique.append(item)

            value = ", ".join(unique[:8])
            return value, 0.85, value

        stage_match = re.search(r"\b(stage\s*\d+)\b", text, re.IGNORECASE)
        if stage_match:
            return clean_line(stage_match.group(1).title()), 0.75, stage_match.group(0)

        return "", 0.0, ""