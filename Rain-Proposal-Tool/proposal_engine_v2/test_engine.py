from .rfq_extractor import extract_rfq_data
from .site_research import research_site
from .proposal_writer import write_proposal_sections
from .docx_builder import build_proposal_docx


def run_engine_test(full_text: str, output_path: str = "outputs/V2_test_proposal.docx"):
    rfq = extract_rfq_data(full_text)
    research = research_site(rfq.site_address)
    sections = write_proposal_sections(rfq, research)

    build_proposal_docx(
        output_path=output_path,
        rfq=rfq,
        research=research,
        sections=sections,
    )

    return {
        "rfq": rfq,
        "research": research,
        "sections": sections,
        "output_path": output_path,
    }
