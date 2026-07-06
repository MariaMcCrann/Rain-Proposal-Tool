"""
Proposal Engine V2

This package contains the next-generation proposal engine for the
RAIN Proposal Tool.

Modules
-------
models.py
    Shared data models.

text_utils.py
    Text cleaning and helper utilities.

rfq_extractor.py
    Extract structured engineering information from RFQs.

site_research.py
    Performs site lookup, geocoding and authority research.

proposal_writer.py
    Generates proposal sections.

docx_builder.py
    Creates the Word proposal document.

test_engine.py
    Runs the complete pipeline for testing.
"""

__version__ = "2.0.0"

from .models import (
    RFQExtract,
    SiteResearch,
    ProposalSections,
    ProjectPhase,
    PlanningInfo,
    ContactInfo,
)

from .rfq_extractor import extract_rfq_data
from .site_research import research_site
from .proposal_writer import write_proposal_sections
from .docx_builder import build_proposal_docx
from .document_intelligence import analyse_document, build_rfq_from_intelligence
__all__ = [
    "RFQExtract",
    "SiteResearch",
    "ProposalSections",
    "ProjectPhase",
    "PlanningInfo",
    "ContactInfo",
    "extract_rfq_data",
    "research_site",
    "write_proposal_sections",
    "build_proposal_docx",
    "analyse_document",
    "build_rfq_from_intelligence",
]
