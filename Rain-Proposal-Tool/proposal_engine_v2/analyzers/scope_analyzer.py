import re

from .types import AnalyzerResult
from ..text_utils import clean_text, clean_line, get_lines, truncate


ACTION_WORDS = [
    "prepare",
    "undertake",
    "develop",
    "review",
    "assess",
    "provide",
    "design",
    "model",
    "calculate",
    "confirm",
    "complete",
    "liaise",
    "submit",
    "report",
    "inspect",
    "analyse",
    "analyze",
    "investigate",
]


SCOPE_HEADINGS = [
    "scope",
    "scope of works",
    "services",
    "services required",
    "required services",
    "consultant scope",
]


class ScopeAnalyzer:

    name = "Scope Analyzer"

    def analyse(self, full_text: str) -> AnalyzerResult:

        result = AnalyzerResult(self.name)

        text = clean_text(full_text)

        scope = self._find_scope(text)
        deliverables = self._find_deliverables(text)

        result.add(
            "scope_summary",
            scope["text"],
            scope["confidence"],
            scope["source"],
        )

        result.add(
            "deliverables",
            deliverables["items"],
            deliverables["confidence"],
            deliverables["source"],
        )

        return result

    # -------------------------------------------------------------

    def _find_scope(self, text):

        for heading in SCOPE_HEADINGS:

            pattern = (
                rf"{heading}\s*[:\n]"
                rf"(.+?)"
                rf"(?=\n\s*(?:deliverables|fees|program|timeline|phase|requirements)\b|\Z)"
            )

            match = re.search(
                pattern,
                text,
                re.IGNORECASE | re.DOTALL,
            )

            if match:

                value = truncate(match.group(1), 1200)

                if len(value) > 30:

                    return {
                        "text": value,
                        "confidence": 0.92,
                        "source": clean_line(match.group(0)[:300]),
                    }

        return {
            "text": "",
            "confidence": 0.0,
            "source": "",
        }

    # -------------------------------------------------------------

    def _find_deliverables(self, text):

        deliverables = []

        source = ""

        for line in get_lines(text):

            lower = line.lower()

            if any(
                lower.startswith(word)
                or f" {word} " in lower
                for word in ACTION_WORDS
            ):

                if (
                    15 <= len(line) <= 220
                    and line not in deliverables
                ):

                    deliverables.append(line)

                    if not source:
                        source = line

            if len(deliverables) >= 20:
                break

        confidence = 0.90 if deliverables else 0.0

        return {
            "items": deliverables,
            "confidence": confidence,
            "source": source,
        }