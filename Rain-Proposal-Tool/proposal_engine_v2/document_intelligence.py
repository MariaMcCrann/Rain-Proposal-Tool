from .models import RFQExtract, ProjectPhase, ContactInfo
from .analyzers.address_analyzer import AddressAnalyzer
from .analyzers.project_analyzer import ProjectAnalyzer
from .analyzers.scope_analyzer import ScopeAnalyzer


def analyse_document(full_text: str) -> dict:
    address_result = AddressAnalyzer().analyse(full_text)
    site_address = address_result.get_value("site_address", "")

    project_result = ProjectAnalyzer().analyse(
        full_text,
        site_address=site_address,
    )

    scope_result = ScopeAnalyzer().analyse(full_text)

    return {
        "address": address_result,
        "project": project_result,
        "scope": scope_result,
    }


def build_rfq_from_intelligence(full_text: str) -> RFQExtract:
    intelligence = analyse_document(full_text)

    address = intelligence["address"]
    project = intelligence["project"]
    scope = intelligence["scope"]

    deliverables = scope.get_value("deliverables", [])

    notes = []

    for group in intelligence.values():
        for field in group.low_confidence_fields():
            notes.append(
                f"Low confidence: {group.analyzer_name} could not confidently identify {field}."
            )

    phases = []
    project_stage = project.get_value("project_stage", "")

    if project_stage and deliverables:
        phases.append(
            ProjectPhase(
                name=project_stage,
                deliverables=deliverables,
            )
        )
    elif deliverables:
        phases.append(
            ProjectPhase(
                name="Scope of Works",
                deliverables=deliverables,
            )
        )

    return RFQExtract(
        project_title=project.get_value("project_title", "Untitled Project"),
        project_type=project.get_value("project_type", "Engineering services"),
        site_address=address.get_value("site_address", ""),
        background=project.get_value("background", ""),
        scope_summary=scope.get_value("scope_summary", ""),
        phases=phases,
        deliverables=deliverables,
        authority_requirements=[],
        contact=ContactInfo(),
        extraction_notes=notes,
        full_text=full_text,
    )