"""
Optional planning research step. Takes extracted project info and uses
Claude with web search to look up:
- Traditional Owners of the site
- Responsible council
- Catchment Management Authority
- Water authority
- Relevant planning scheme
- VicPlan planning controls (zone, DPO, SBO, LSIO, FO, other overlays)
- Known flood / TUFLOW models near the site

Only called when the user opts in via the checkbox on the upload page.
Results are passed into the proposal generation step - they do NOT go
into the Excel fee template.

Each search is tried independently so a failure on one (e.g. VicPlan
is not accessible) doesn't block the others. Failures are recorded in
research["gaps"] and surfaced in the proposal as "Not provided - must
be confirmed."
"""

import os
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

RESEARCH_PROMPT = """You are assisting a civil engineering consulting firm (Rain Consulting, Melbourne) to
prepare a fee proposal. Using the project information below, search the web to find each of the
following. For each item, report what you found AND the source URL. If you genuinely cannot find
something, say "Not found - must be confirmed" and explain briefly why it matters.

Project info:
Site address / location: {site_address}
Project title: {project_title}
Project type: {project_type}

Find and report ALL of the following:

1. TRADITIONAL OWNERS: Who are the Traditional Owners / custodians of the land at or near this site?
   Include the relevant Registered Aboriginal Party (RAP) if in Victoria.

2. RESPONSIBLE COUNCIL: Which local government authority (council) has jurisdiction over this site?

3. CATCHMENT MANAGEMENT AUTHORITY (CMA): Which CMA covers this site?

4. WATER AUTHORITY: Which water authority (e.g. Melbourne Water, Barwon Water, Greater Western Water)
   services or has jurisdiction over this site?

5. PLANNING SCHEME: Which Victorian Planning Scheme applies? What is the current zone?
   What overlays apply (especially DPO, SBO, LSIO, FO, ESO, EMO, BMO, DDO)?
   Use VicPlan (https://vicplan.planningschemes.vic.gov.au) or the council planning portal if possible.
   If you cannot access VicPlan directly, state this clearly.

6. EXISTING FLOOD MODELS: Are there any known flood studies, TUFLOW models, or flood mapping datasets
   for this catchment or nearby watercourses? Check CMA websites, council flood pages, and any
   publicly referenced studies.

Report each finding clearly under its numbered heading. Be factual - do not guess. If something
cannot be confirmed from public sources, say so explicitly."""


def research_site(extracted: dict) -> dict:
    """
    Returns a dict with keys matching the 6 research areas above, plus
    a "gaps" list of items that couldn't be found and need manual follow-up.
    Returns an empty-ish dict with the gap flagged if the search fails
    entirely.
    """
    site_address = extracted.get("site_address", "")
    project_title = extracted.get("project_title", "")
    project_type = extracted.get("project_type", "")

    if not site_address and not project_title:
        return {
            "traditional_owners": "Not searched — no site address or project title extracted from the RFQ.",
            "council": "Not searched",
            "cma": "Not searched",
            "water_authority": "Not searched",
            "planning_controls": "Not searched",
            "existing_models": "Not searched",
            "gaps": ["No site address or project title available to search against — complete the RFQ extraction first."],
        }

    prompt = RESEARCH_PROMPT.format(
        site_address=site_address or "Not stated",
        project_title=project_title or "Not stated",
        project_type=project_type or "Not stated",
    )

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4000,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{"role": "user", "content": prompt}],
        )
        raw_text = "\n".join(
            block.text for block in response.content if hasattr(block, "text") and block.text
        )
    except Exception as e:
        return {
            "traditional_owners": f"Search failed: {e}",
            "council": "Search failed",
            "cma": "Search failed",
            "water_authority": "Search failed",
            "planning_controls": "Search failed",
            "existing_models": "Search failed",
            "gaps": [f"Planning research step failed entirely: {e}"],
            "raw": "",
        }

    # Parse the raw text into sections
    result = _parse_research(raw_text)
    result["raw"] = raw_text
    return result


def _parse_research(text: str) -> dict:
    """
    Loosely parse the numbered sections out of the model's response.
    We keep the raw text too so nothing is lost if the parse is rough.
    """
    sections = {
        "traditional_owners": "",
        "council": "",
        "cma": "",
        "water_authority": "",
        "planning_controls": "",
        "existing_models": "",
        "gaps": [],
    }

    markers = [
        ("1.", "traditional_owners"),
        ("2.", "council"),
        ("3.", "cma"),
        ("4.", "water_authority"),
        ("5.", "planning_controls"),
        ("6.", "existing_models"),
    ]

    lines = text.splitlines()
    current_key = None
    buffer = []

    for line in lines:
        matched = False
        for prefix, key in markers:
            if line.strip().startswith(prefix) and ("TRADITIONAL" in line.upper() or
               "COUNCIL" in line.upper() or "CMA" in line.upper() or
               "WATER" in line.upper() or "PLANNING" in line.upper() or
               "MODEL" in line.upper() or "FLOOD" in line.upper()):
                if current_key and buffer:
                    sections[current_key] = " ".join(buffer).strip()
                current_key = key
                buffer = [line]
                matched = True
                break
        if not matched and current_key:
            buffer.append(line)

    if current_key and buffer:
        sections[current_key] = " ".join(buffer).strip()

    # Identify gaps - anything that says "not found" or "not accessible"
    for key, val in sections.items():
        if key == "gaps":
            continue
        if any(phrase in val.lower() for phrase in ["not found", "cannot access", "could not", "not provided", "unclear"]):
            sections["gaps"].append(f"{key.replace('_', ' ').title()}: requires manual confirmation")

    return sections
