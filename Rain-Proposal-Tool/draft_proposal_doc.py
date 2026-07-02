# draft_proposal_doc.py

from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH


def add_heading(doc, text, level=1):
    if not text:
        return
    doc.add_heading(str(text), level=level)


def add_paragraph(doc, text):
    if text:
        doc.add_paragraph(str(text))


def add_bullets(doc, items):
    for item in items or []:
        if item:
            doc.add_paragraph(str(item), style="List Bullet")


def add_key_value_table(doc, rows):
    table = doc.add_table(rows=0, cols=2)
    table.style = "Table Grid"

    for label, value in rows:
        row = table.add_row().cells
        row[0].text = str(label)
        row[1].text = str(value or "Not stated")

    doc.add_paragraph("")


def setup_styles(doc):
    styles = doc.styles

    styles["Normal"].font.name = "Arial"
    styles["Normal"].font.size = Pt(10)

    for style_name in ["Heading 1", "Heading 2", "Heading 3"]:
        style = styles[style_name]
        style.font.name = "Arial"
        style.font.color.rgb = RGBColor(0, 43, 73)


def generate_draft_proposal(extracted, sections, output_path, research=None):
    doc = Document()
    setup_styles(doc)

    research = research or {}
    sections = sections or {}

    project_title = extracted.get("project_title", "Draft Proposal")
    client = extracted.get("client", "Not stated")
    site_address = extracted.get("site_address") or extracted.get("site_location") or "Not stated"

    # Cover
    title = doc.add_heading(project_title, level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    p = doc.add_paragraph("Draft Proposal")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph("")

    add_key_value_table(doc, [
        ("Client", client),
        ("Site / Location", site_address),
        ("Proposal status", "Draft for review"),
    ])

    # Project details
    add_heading(doc, "1. Project Understanding", level=1)
    add_paragraph(doc, sections.get("project_understanding") or extracted.get("background"))

    # Knowledge engine
    add_heading(doc, "2. Preliminary Site Research", level=1)

    authorities = research.get("authorities", {})
    planning = research.get("planning_controls", {})
    coordinates = research.get("coordinates", {})

    add_key_value_table(doc, [
        ("Latitude", coordinates.get("lat")),
        ("Longitude", coordinates.get("lon")),
        ("Council", authorities.get("council")),
        ("CMA", authorities.get("cma")),
        ("Water authority", authorities.get("water_authority")),
        ("SBO", planning.get("sbo")),
        ("LSIO", planning.get("lsio")),
        ("FO", planning.get("fo")),
        ("Planning source", planning.get("source")),
    ])

    add_bullets(doc, research.get("notes", []))
    add_bullets(doc, planning.get("notes", []))

    # Scope
    add_heading(doc, "3. Scope of Services", level=1)

    for phase in extracted.get("phases", []):
        add_heading(doc, phase.get("phase_name", "Project Phase"), level=2)
        add_bullets(doc, phase.get("deliverables", []))

    # Methodology
    add_heading(doc, "4. Methodology", level=1)
    add_bullets(doc, sections.get("methodology", []))

    # Authority requirements
    add_heading(doc, "5. Authority and Standards Requirements", level=1)
    add_bullets(doc, sections.get("authority_requirements") or extracted.get("authority_requirements", []))

    # Fee basis
    add_heading(doc, "6. Fee Basis Notes", level=1)
    add_bullets(doc, extracted.get("fee_basis_notes", []))

    # Assumptions
    add_heading(doc, "7. Assumptions", level=1)
    add_bullets(doc, sections.get("assumptions", []))

    # Exclusions
    add_heading(doc, "8. Exclusions", level=1)
    add_bullets(doc, sections.get("exclusions", []))

    # Closing
    add_heading(doc, "9. Next Steps", level=1)
    add_paragraph(
        doc,
        "Following review of this draft proposal, RAIN Consulting can confirm scope, fee assumptions, "
        "programme, authority inputs and any required exclusions before issuing the final proposal."
    )

    doc.save(output_path)