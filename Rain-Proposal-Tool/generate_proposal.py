# generate_proposal.py

import os
from datetime import datetime
from typing import Any, Dict

from extract_rfq import extract_rfq
from research_site import research_site
from draft_proposal_doc import create_draft_proposal_doc


def build_project_understanding(extracted: Dict[str, Any], research: Dict[str, Any]) -> str:
    """
    Creates a RAIN-style project understanding summary.
    Keeps it polished, practical, and proposal-ready.
    """

    address = (
        research.get("site_address")
        or extracted.get("site_address")
        or "the site"
    )

    project_type = extracted.get("project_type", "hydrological engineering services")

    if "avalon" in address.lower():
        return (
            f"RAIN Consulting understands the project involves the completion of hydrological "
            f"engineering services for the proposed industrial subdivision at {address}. "
            f"The site forms part of the Greater Avalon Employment Precinct and is understood "
            f"to be subject to Development Plan Overlay 50.\n\n"
            f"Previous phases of the hydrological assessment have established the catchment "
            f"analysis and preliminary concept design. This commission focuses on completing "
            f"the remaining water-related documentation required to support the planning and "
            f"approval process.\n\n"
            f"The scope is expected to include coordination with the relevant authorities, "
            f"confirmation of applicable planning controls, and preparation of the hydrological "
            f"inputs required to address the development plan requirements."
        )

    return (
        f"RAIN Consulting understands the project involves {project_type.lower()} "
        f"for the site at {address}.\n\n"
        f"The purpose of this commission is to review the available project information, "
        f"confirm the relevant site constraints and authority requirements, and prepare the "
        f"technical inputs required to support the planning and approval process.\n\n"
        f"The scope is expected to include coordination with relevant authorities, confirmation "
        f"of applicable planning controls, and preparation of the engineering documentation "
        f"required for the project."
    )


def build_scope_of_services(extracted: Dict[str, Any]) -> str:
    """
    Creates a clean scope summary from the RFQ.
    """

    file_name = extracted.get("file_name", "the RFQ")
    site_address = extracted.get("site_address", "the site")

    return (
        f"The scope of services has been prepared based on the information provided in "
        f"{file_name} for {site_address}.\n\n"
        f"The proposed services are expected to include review of the supplied background "
        f"information, confirmation of hydrological and stormwater requirements, coordination "
        f"with relevant authorities where required, and preparation of the technical outputs "
        f"needed to support the next stage of the project."
    )


def build_proposal_sections(extracted: Dict[str, Any], research: Dict[str, Any]) -> Dict[str, Any]:
    """
    Builds the content dictionary used by draft_proposal_doc.py.
    """

    return {
        "project_understanding": build_project_understanding(extracted, research),
        "scope_of_services": build_scope_of_services(extracted),
        "preliminary_site_research": research,
    }


def generate_proposal(uploaded_file_path: str, output_folder: str = "uploads") -> str:
    """
    Main proposal generation function.

    Steps:
    1. Extract RFQ text and basic project details.
    2. Research site/address details.
    3. Build proposal sections.
    4. Create Word document.
    """

    extracted = extract_rfq(uploaded_file_path)

    full_text = extracted.get("full_text", "")
    research = research_site(full_text, extracted)

    sections = build_proposal_sections(extracted, research)

    os.makedirs(output_folder, exist_ok=True)

    site_address = research.get("site_address", "Draft Proposal")
    safe_name = site_address.replace("/", "-").replace("\\", "-").replace(",", "")
    safe_name = " ".join(safe_name.split())

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_path = os.path.join(output_folder, f"{safe_name} - Draft Proposal {timestamp}.docx")

    create_draft_proposal_doc(
        output_path=output_path,
        extracted=extracted,
        research=research,
        sections=sections,
    )

    return output_path