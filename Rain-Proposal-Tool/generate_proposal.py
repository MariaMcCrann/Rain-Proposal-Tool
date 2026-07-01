"""
Generates comprehensive proposal content for all 23 sections described
in Flow_steps_R01.txt. Takes the extracted JSON and optional research
results, calls Claude, and returns a structured dict of section content
ready for the docx builder to format.

This is a separate Claude call from the extraction step - it's the
"write the actual proposal" step, not the "understand the RFQ" step.
"""

import os
import json
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are an experienced civil engineering proposal coordinator for Rain Consulting,
a Melbourne-based water engineering consultancy. You write professional, commercially strong fee
proposals for hydrological, hydraulic, drainage, stormwater, and integrated water management projects.

Your proposals are:
- Detailed enough to justify the fee and protect Rain commercially
- Written in concise engineering language with Australian English spelling
- Structured to clearly separate confirmed scope, assumed scope, optional scope and excluded scope
- Specific about variation triggers and scope protection assumptions
- Honest about gaps: if information is missing, you write "Not provided" and explain why it matters

You never make up facts. You write in a professional consulting tone. You do not write marketing waffle."""


def generate_proposal_content(extracted: dict, research: dict | None = None) -> dict:
    """
    Returns a dict with one key per proposal section. Each value is a
    string of ready-to-format prose (plain text, no markdown headers -
    the docx builder adds those). Bullet points use a leading dash "-"
    so the docx builder can detect and format them as real Word bullets.

    Fee structure section intentionally returns a structured placeholder
    (list of phase names) rather than numbers - amounts are filled
    manually in the Excel fee tracker.
    """
    phases = extracted.get("phases", [])
    research = research or {}

    # Build the user message with all available context
    context_parts = [
        f"PROJECT TITLE: {extracted.get('project_title', 'Not provided')}",
        f"PROJECT TYPE: {extracted.get('project_type', 'Not provided')}",
        f"BACKGROUND: {extracted.get('background', 'Not provided')}",
        f"SITE/LOCATION: {extracted.get('site_address', 'Not provided')}",
        f"CLIENT: {extracted.get('contact', {}).get('company', 'Not provided')}",
        f"CLIENT CONTACT: {extracted.get('contact', {}).get('name', 'Not provided')}",
        f"KEY DATES: {json.dumps(extracted.get('key_dates', {}), indent=2)}",
        f"AUTHORITY REQUIREMENTS: {json.dumps(extracted.get('authority_requirements', []), indent=2)}",
        "",
        "PHASES AND DELIVERABLES:",
    ]
    for phase in phases:
        context_parts.append(f"  {phase.get('phase_name', 'Phase')}:")
        for d in phase.get("deliverables", []):
            context_parts.append(f"    - {d}")

    if research:
        context_parts += [
            "",
            "PLANNING RESEARCH RESULTS:",
            f"  Traditional Owners: {research.get('traditional_owners', 'Not researched')}",
            f"  Council: {research.get('council', 'Not researched')}",
            f"  CMA: {research.get('cma', 'Not researched')}",
            f"  Water Authority: {research.get('water_authority', 'Not researched')}",
            f"  Planning Controls: {research.get('planning_controls', 'Not researched')}",
            f"  Existing Models: {research.get('existing_models', 'Not researched')}",
        ]
        if research.get("gaps"):
            context_parts.append(f"  Gaps requiring manual confirmation: {', '.join(research['gaps'])}")

    if extracted.get("extraction_notes"):
        context_parts += ["", "EXTRACTION NOTES (flagged during document reading):"]
        for note in extracted["extraction_notes"]:
            context_parts.append(f"  - {note}")

    context = "\n".join(context_parts)

    user_message = f"""Using the project information below, write the content for a Rain Consulting fee proposal.

{context}

Write content for each of the following sections. Start each section with its exact label on its own line
(e.g. "##SECTION: executive_summary"), followed immediately by the section content. Use plain paragraphs
and bullet points starting with "- " for lists. Do not use markdown headers inside sections — just prose
and "- " bullets. Write every section even if information is limited — use "Not provided — [explain why
this matters]" for genuinely missing facts, and use professional engineering judgement for methodology
and assumptions that are standard for this type of project.

Sections to write:

##SECTION: executive_summary
2-3 paragraphs: what Rain proposes to do, for whom, on what site, under what regulatory framework,
and what the key deliverables are. Do not include fee amounts.

##SECTION: project_understanding
Our understanding of the project brief, site context, development type, approval pathway, and
why these services are required now. Reference the specific RFQ/brief received and the phases requested.

##SECTION: site_and_planning_context
Site description, location, area, land use, development type, planning scheme, zone, overlays (DPO,
SBO, LSIO, FO, etc.). Use the research results if available. Flag anything not confirmed.

##SECTION: traditional_owners_and_authority
Traditional Owners and RAP acknowledgement. List all relevant authorities (council, CMA, water
authority, EPA where relevant). Include their specific role in approving each phase.

##SECTION: existing_model_and_data
Summary of existing hydrological/hydraulic models, GIS data, surveys, studies, and reports that
Rain will draw on. Note what the client is to provide and what is assumed available. Flag any gaps.

##SECTION: key_project_background
Previous investigations, existing data, prior phases of work, context that directly influences scope.

##SECTION: scope_risk_check
A short risk assessment covering: scope clarity (high/med/low confidence per phase), key assumptions
that if wrong would trigger variations, data gaps that could delay the project, and regulatory risks
(authority interpretation, methodology workshops, approval timeframes). Use a table format with
dashes: "- [Risk] | [Likelihood] | [Impact] | [Mitigation]"

##SECTION: detailed_scope_of_services
For each phase and task, write: Task Name, Purpose, Description of work, Modelling/assessment
required, Input data required, Key assumptions, Deliverables, Exclusions, Variation triggers.
Be thorough — this section protects Rain commercially. This should be the longest section.

##SECTION: methodology
For each major technical task (hydrological modelling, hydraulic modelling, MUSIC, functional
design, etc.) briefly describe the methodology Rain will use, the standards/guidelines it follows,
and how outputs will be quality-assured.

##SECTION: deliverables
A consolidated list of all formal deliverables across all phases, with format (Word report, PDF,
GIS, CAD, model files, etc.) and review/approval pathway for each.

##SECTION: authority_requirements
List all applicable standards, guidelines, acts, and authority requirements. Group by authority.
Include specific clauses where known (e.g. DPO50 Clause 4.0). Flag anything that may need
interpretation at a methodology workshop.

##SECTION: compliance_matrix
A matrix showing how Rain's proposed scope addresses each requirement in the RFQ or DPO/overlay.
Format as: "- [RFQ/DPO requirement] | [Rain deliverable that addresses it] | [Phase]"

##SECTION: required_input_data
List all data/information Rain requires from the client, council, CMA, and other parties before
commencing each phase. Organise by phase. Flag items critical to programme.

##SECTION: assumptions
All key assumptions Rain is making in preparing this proposal. Cover: supplied data quality,
model fitness for purpose, authority review rounds, design iterations, meeting allowances,
climate change approach, staging, scope of GIS/survey work, and any project-specific items.

##SECTION: exclusions
Everything that is explicitly excluded from Rain's scope. Be specific and commercially protective.
Include exclusions from the RFQ plus standard Rain exclusions (no site survey, no ecological
assessment, no cultural heritage, no geotechnical, no detailed design, etc. unless explicitly in scope).

##SECTION: optional_and_provisional
Items that are not in the base scope but could be added: additional modelling scenarios, extra
authority meetings, supplementary studies, staging variations. Flag which are provisional fee items.

##SECTION: variation_triggers
A strong list of the specific circumstances that would justify a variation to the agreed fee.
Be specific to this project, not generic.

##SECTION: fee_structure
IMPORTANT: Do NOT include any dollar amounts. Instead, list the phases and their fee basis
(Fixed fee / T&M / % fee / Provisional) as confirmed in the RFQ. Note payment terms (monthly
invoicing, full phase payment before deliverable release). Flag any provisional items.

##SECTION: programme
Indicative programme by phase, in weeks from authorisation. List key dependencies (client data
supply, authority review periods, EIA completion, methodology workshops). Note what is outside
Rain's control and excluded from the programme.

##SECTION: draft_proposal_wording
A polished, client-facing introduction suitable for the first paragraphs of the formal proposal
letter or executive page. Should start with "Thank you for the opportunity..." and summarise
Rain's understanding, approach, and key points of differentiation. Professional and engaging but
not marketing-heavy.

##SECTION: readiness_check
A short internal note (NOT for client): Is this proposal ready for pricing? What critical
information is still missing? What should the reviewer confirm before issuing? List as bullet points."""

    response = client.messages.create(
        model=os.environ.get("RAIN_MODEL", "claude-sonnet-4-6"),
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw = "\n".join(
        block.text for block in response.content if hasattr(block, "text") and block.text
    )

    return _parse_sections(raw, phases)


def _parse_sections(text: str, phases: list) -> dict:
    """Parse the ##SECTION: markers into a dict of section_key -> content."""
    sections = {}
    current_key = None
    buffer = []

    for line in text.splitlines():
        if line.startswith("##SECTION:"):
            if current_key is not None:
                sections[current_key] = "\n".join(buffer).strip()
            current_key = line.replace("##SECTION:", "").strip()
            buffer = []
        else:
            buffer.append(line)

    if current_key is not None:
        sections[current_key] = "\n".join(buffer).strip()

    # Always ensure fee_structure has the phase list, regardless of what
    # Claude generated - we never want auto-generated dollar amounts.
    phase_lines = []
    for p in phases:
        phase_lines.append(f"- {p.get('phase_name', 'Phase')} | [Fee to be entered] | Fixed fee")
    sections["fee_structure_phases"] = "\n".join(phase_lines) if phase_lines else "- [Phases to be confirmed]"

    return sections
