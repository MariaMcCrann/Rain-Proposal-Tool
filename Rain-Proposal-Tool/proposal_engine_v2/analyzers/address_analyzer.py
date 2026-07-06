import re
from typing import List

from .types import AnalyzerResult
from ..text_utils import clean_text, clean_line, get_lines


ROAD_TYPES = [
    "Road", "Rd",
    "Street", "St",
    "Avenue", "Ave",
    "Drive", "Dr",
    "Court", "Ct",
    "Lane", "Ln",
    "Place", "Pl",
    "Way",
    "Parade", "Pde",
    "Highway", "Hwy",
    "Boulevard", "Blvd",
    "Terrace", "Tce",
    "Close", "Cl",
    "Circuit", "Cct",
]


STOP_WORDS = [
    "sits within",
    "located within",
    "employment precinct",
    "precinct",
    "subject to",
    "development plan",
    "overlay",
    "scope of works",
    "background",
    "proposal",
]


ADDRESS_PATTERN = re.compile(
    r"\b\d{1,6}[A-Za-z]?\s+"
    r"[A-Za-z0-9'&\- ]+?\s+"
    r"(?:Road|Rd|Street|St|Avenue|Ave|Drive|Dr|Court|Ct|Lane|Ln|Place|Pl|Way|"
    r"Parade|Pde|Highway|Hwy|Boulevard|Blvd|Terrace|Tce|Close|Cl|Circuit|Cct)"
    r"(?:,\s*[A-Za-z' \-]+)?",
    re.IGNORECASE,
)


class AddressAnalyzer:

    name = "Address Analyzer"

    def analyse(self, full_text: str) -> AnalyzerResult:

        result = AnalyzerResult(self.name)

        text = clean_text(full_text)

        candidates = self._find_candidates(text)

        if not candidates:

            result.add(
                "site_address",
                "",
                confidence=0.0,
                notes=["No address candidates found."]
            )

            return result

        best = max(candidates, key=lambda c: c["score"])

        result.add(
            field="site_address",
            value=best["address"],
            confidence=min(best["score"] / 100.0, 1.0),
            source_text=best["source"],
            notes=best["notes"],
        )

        return result

    # --------------------------------------------------------

    def _find_candidates(self, text: str):

        candidates = []

        lines = get_lines(text)

        for line in lines:

            for match in ADDRESS_PATTERN.finditer(line):

                address = clean_line(match.group(0))

                score = 50
                notes = []

                if "," in address:
                    score += 15
                    notes.append("Contains locality separator.")

                if re.search(r"\bVIC\b", line, re.IGNORECASE):
                    score += 10
                    notes.append("State identified.")

                if any(
                    rt.lower() in address.lower()
                    for rt in ROAD_TYPES
                ):
                    score += 20

                lower_line = line.lower()

                stop_index = len(address)

                for stop in STOP_WORDS:

                    idx = lower_line.find(stop)

                    if idx > 0:

                        stop_index = min(stop_index, idx)

                        notes.append(
                            f"Trimmed before '{stop}'."
                        )

                address = line[:stop_index]

                address = self._clean_address(address)

                if len(address) < 8:
                    continue

                candidates.append(
                    {
                        "address": address,
                        "score": score,
                        "source": line,
                        "notes": notes,
                    }
                )

        return candidates

    # --------------------------------------------------------

    def _clean_address(self, value: str) -> str:

        value = clean_line(value)

        value = re.sub(
            r"Hydrological Engineering Scope Of Works",
            "",
            value,
            flags=re.IGNORECASE,
        )

        value = re.sub(
            r"Scope Of Works",
            "",
            value,
            flags=re.IGNORECASE,
        )

        value = re.sub(
            r"\bv\d+\b",
            "",
            value,
            flags=re.IGNORECASE,
        )

        value = re.sub(r"\s+", " ", value)

        value = value.strip(" -,.")

        if (
            value
            and "vic" not in value.lower()
            and "victoria" not in value.lower()
        ):
            value += " VIC"

        return value