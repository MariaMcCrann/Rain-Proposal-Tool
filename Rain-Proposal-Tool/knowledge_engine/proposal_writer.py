# knowledge_engine/proposal_writer.py


def write_proposal_sections(extracted: dict, research: dict | None = None) -> dict:
    project_title = extracted.get("project_title", "Draft Engineering Proposal")
    background = extracted.get("background", "")
    phases = extracted.get("phases", [])
    authorities = extracted.get("authority_requirements", [])

    research = research or {}

    if not background:
        background_parts = []
        for phase in phases:
            for item in phase.get("deliverables", []):
                cleaned = (item or "").strip()
                if cleaned and cleaned.lower() not in {"project background", "background"}:
                    background_parts.append(cleaned)
                if len(background_parts) >= 5:
                    break
            if len(background_parts) >= 5:
                break
        background = " ".join(background_parts)

    scope_parts = []
    for phase in phases:
        phase_name = (phase.get("phase_name") or "Project phase").strip()
        items = [str(item).strip() for item in phase.get("deliverables", []) if str(item).strip()]
        if items:
            scope_parts.append(phase_name + "\n" + "\n".join(f"• {item}" for item in items))
        else:
            scope_parts.append(phase_name)

    scope_of_services = "\n\n".join(scope_parts) or extracted.get("scope_summary", "")

    research_authorities = research.get("authorities", {})
    planning = research.get("planning_controls", {})

    sections = {
        "executive_summary": (
            f"This proposal has been prepared for {project_title}. "
            "The scope has been developed based on the RFQ information provided, "
            "including the nominated project background, required deliverables and approval requirements."
        ),

        "project_understanding": background or extracted.get("scope_summary", ""),
        "scope_of_services": scope_of_services,

        "methodology": [],
        "authority_requirements": [],
        "assumptions": [],
        "exclusions": [],
        "research_summary": [],
    }

    for phase in phases:
        name = phase.get("phase_name", "Project phase")
        sections["methodology"].append(name)

        for item in phase.get("deliverables", []):
            sections["methodology"].append(f"- {item}")

    for item in authorities:
        sections["authority_requirements"].append(item)

    if research_authorities:
        if research_authorities.get("council"):
            sections["research_summary"].append(
                f"Council: {research_authorities.get('council')}"
            )
        if research_authorities.get("cma"):
            sections["research_summary"].append(
                f"CMA: {research_authorities.get('cma')}"
            )
        if research_authorities.get("water_authority"):
            sections["research_summary"].append(
                f"Water authority: {research_authorities.get('water_authority')}"
            )

    if planning:
        sections["research_summary"].append(
            "Planning controls: preliminary only. Verify manually in VicPlan before issue."
        )

    sections["assumptions"] = [
        "The scope is based on information provided in the RFQ and any attached documents.",
        "Existing survey, LiDAR, GIS, drainage asset data and previous studies will be made available by the client where relevant.",
        "Authority review periods are excluded unless specifically stated.",
        "The proposal remains subject to confirmation of available background information and stakeholder requirements.",
    ]

    sections["exclusions"] = [
        "Detailed design is excluded unless expressly included in the nominated project phases.",
        "Construction documentation, tender support and construction phase services are excluded unless stated.",
        "Specialist environmental, geotechnical, traffic, ecological or cultural heritage advice is excluded unless stated.",
        "Authority application fees, external review fees and third-party costs are excluded.",
    ]

    return sections