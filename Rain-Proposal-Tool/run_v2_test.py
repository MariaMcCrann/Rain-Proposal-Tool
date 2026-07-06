import os
from ingest import extract_text
from proposal_engine_v2 import (
    extract_rfq_data,
    research_site,
    write_proposal_sections,
    build_proposal_docx,
)

INPUT_FILE = "test_files/15 Avalon Rd - Hydrological Scope of Works (Phase 3 - 5) v1.pdf"
OUTPUT_FILE = "outputs/V2_test_proposal.docx"

os.makedirs("outputs", exist_ok=True)

text = extract_text(INPUT_FILE)

rfq = extract_rfq_data(text)
research = research_site(rfq.site_address)
sections = write_proposal_sections(rfq, research)

build_proposal_docx(
    output_path=OUTPUT_FILE,
    rfq=rfq,
    research=research,
    sections=sections,
)

print("Project title:", rfq.project_title)
print("Address:", rfq.site_address)
print("Council:", research.council)
print("Traditional Owners:", research.traditional_owners)
print("Created:", OUTPUT_FILE)
