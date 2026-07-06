from typing import List

from .models import RFQExtract, SiteResearch, ProposalSections


def _join_clean(items: List[str]) -> List[str]:
    cleaned = []
    for item in items or []:
        item = (item or "").strip()
        if item and item not in cleaned:
            cleaned.append(item)
    return cleaned


def write_project_understanding(rfq: RFQExtract, research: SiteResearch | None = None) -> str:
    research = research or SiteResearch()

    parts = []

    if rfq.background:
        parts.append(rfq.background)

    if rfq.project_type or rfq.site_address:
        address = research.address or rfq.site_address or "the subject site"
        project_type = rfq.project_type or "the proposed development"
        parts.append(
            f"The commission relates to {project_type.lower()} at {address}."
        )

    authority_parts = []

    if research.council:
        authority_parts.append(f"the {research.council}")
    if research.cma:
        authority_parts.append(f"the {research.cma}")
    if research.water_authority:
        authority_parts.append(f"{research.water_authority}")

    if authority_parts:
        parts.append(
            "The assessment will need to consider the requirements of "
            + ", ".join(authority_parts)
            + ", together with the relevant planning scheme and stormwater/floodplain requirements."
        )

    if not parts:
        return (
            "The project understanding is based on the RFQ documentation provided. "
            "Further confirmation of the site context, planning controls and authority requirements "
            "is recommended before finalising the proposal."
        )

    return "\n\n".join(parts)


def write_scope_of_services(rfq: RFQExtract) -> str:
    if rfq.scope_summary:
        return rfq.scope_summary

    if rfq.phases:
        phase_names = ", ".join([p.name for p in rfq.phases if p.name])
        return f"The proposed scope of services includes the tasks described in {phase_names}."

    return "The proposed scope of services is based on the RFQ documentation provided."


def default_assumptions(rfq: RFQExtract, research: SiteResearch | None = None) -> List[str]:
    research = research or SiteResearch()

    assumptions = [
        "The scope is based on the RFQ documentation and information available at the time of proposal preparation.",
        "The client will provide all relevant background reports, survey data, engineering drawings and previous modelling files where available.",
        "One consolidated round of client comments is allowed for each key deliverable unless otherwise agreed.",
        "Authority consultation is limited to reasonable liaison required to progress the agreed scope.",
        "Planning controls and overlays are to be confirmed using VicPlan before final issue.",
    ]

    if research.latitude and research.longitude:
        assumptions.append(
            f"The site location has been interpreted using the coordinates {research.latitude}, {research.longitude}."
        )

    return assumptions


def default_exclusions() -> List[str]:
    return [
        "Detailed civil design is excluded unless expressly included in the agreed scope.",
        "Preparation of planning application forms or lodgement fees is excluded.",
        "Survey, geotechnical investigation, environmental assessment and cultural heritage assessment are excluded.",
        "Legal advice, land acquisition advice and formal planning advice are excluded.",
        "Major model recalibration or reconstruction is excluded unless specifically included.",
        "Attendance at VCAT, panel hearings or expert witness services is excluded unless separately agreed.",
    ]


def collect_deliverables(rfq: RFQExtract) -> List[str]:
    deliverables = []

    for phase in rfq.phases or []:
        for item in phase.deliverables:
            deliverables.append(item)

    deliverables.extend(rfq.deliverables)

    if not deliverables:
        deliverables = [
            "Technical memorandum or report summarising the assessment approach, findings and recommendations.",
            "Supporting calculations, figures and mapping as required for the agreed scope.",
            "Advice suitable for client and authority review.",
        ]

    return _join_clean(deliverables)[:20]


def collect_authority_requirements(rfq: RFQExtract, research: SiteResearch | None = None) -> List[str]:
    research = research or SiteResearch()

    requirements = list(rfq.authority_requirements or [])

    if research.council:
        requirements.append(f"Council: {research.council}")

    if research.cma:
        requirements.append(f"Catchment Management Authority: {research.cma}")

    if research.water_authority:
        requirements.append(f"Water Authority: {research.water_authority}")

    if research.traditional_owners:
        requirements.append(f"Traditional Owners: {research.traditional_owners}")

    if research.planning and research.planning.notes:
        requirements.extend(research.planning.notes)

    return _join_clean(requirements)


def write_proposal_sections(
    rfq: RFQExtract,
    research: SiteResearch | None = None,
) -> ProposalSections:
    research = research or SiteResearch()

    return ProposalSections(
        project_understanding=write_project_understanding(rfq, research),
        scope_of_services=write_scope_of_services(rfq),
        assumptions=default_assumptions(rfq, research),
        exclusions=default_exclusions(),
        deliverables=collect_deliverables(rfq),
        authority_requirements=collect_authority_requirements(rfq, research),
    )
