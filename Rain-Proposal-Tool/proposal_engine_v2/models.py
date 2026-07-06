from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List


@dataclass
class ContactInfo:
    name: str = ""
    company: str = ""
    email: str = ""
    phone: str = ""


@dataclass
class ProjectPhase:
    name: str = ""
    deliverables: List[str] = field(default_factory=list)


@dataclass
class PlanningInfo:
    zone: str = ""
    overlays: List[str] = field(default_factory=list)
    dpo: str = ""
    sbo: str = ""
    lsio: str = ""
    fo: str = ""
    notes: List[str] = field(default_factory=list)


@dataclass
class SiteResearch:
    address: str = ""
    latitude: str = ""
    longitude: str = ""
    council: str = ""
    traditional_owners: str = ""
    cma: str = ""
    water_authority: str = ""
    planning: PlanningInfo = field(default_factory=PlanningInfo)
    notes: List[str] = field(default_factory=list)


@dataclass
class RFQExtract:
    project_title: str = ""
    project_type: str = ""
    site_address: str = ""
    background: str = ""
    scope_summary: str = ""
    phases: List[ProjectPhase] = field(default_factory=list)
    deliverables: List[str] = field(default_factory=list)
    authority_requirements: List[str] = field(default_factory=list)
    contact: ContactInfo = field(default_factory=ContactInfo)
    extraction_notes: List[str] = field(default_factory=list)
    full_text: str = ""


@dataclass
class ProposalSections:
    project_understanding: str = ""
    scope_of_services: str = ""
    assumptions: List[str] = field(default_factory=list)
    exclusions: List[str] = field(default_factory=list)
    deliverables: List[str] = field(default_factory=list)
    authority_requirements: List[str] = field(default_factory=list)


def to_dict(obj: Any) -> Dict[str, Any]:
    return asdict(obj)
