from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class AnalyzerFinding:
    field: str
    value: Any
    confidence: float = 0.0
    source_text: str = ""
    notes: List[str] = field(default_factory=list)

    def is_high_confidence(self) -> bool:
        return self.confidence >= 0.85

    def is_medium_confidence(self) -> bool:
        return 0.60 <= self.confidence < 0.85

    def is_low_confidence(self) -> bool:
        return self.confidence < 0.60


@dataclass
class AnalyzerResult:
    analyzer_name: str
    findings: Dict[str, AnalyzerFinding] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)

    def add(
        self,
        field: str,
        value: Any,
        confidence: float,
        source_text: str = "",
        notes: List[str] | None = None,
    ) -> None:
        self.findings[field] = AnalyzerFinding(
            field=field,
            value=value,
            confidence=max(0.0, min(1.0, confidence)),
            source_text=source_text,
            notes=notes or [],
        )

    def get_value(self, field: str, default: Any = "") -> Any:
        finding = self.findings.get(field)
        if not finding:
            return default
        return finding.value

    def get_confidence(self, field: str) -> float:
        finding = self.findings.get(field)
        if not finding:
            return 0.0
        return finding.confidence

    def low_confidence_fields(self) -> List[str]:
        return [
            field
            for field, finding in self.findings.items()
            if finding.is_low_confidence()
        ]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "analyzer_name": self.analyzer_name,
            "findings": {
                field: {
                    "value": finding.value,
                    "confidence": finding.confidence,
                    "source_text": finding.source_text,
                    "notes": finding.notes,
                }
                for field, finding in self.findings.items()
            },
            "notes": self.notes,
        }