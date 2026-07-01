"""
Extracts structured proposal data from a Request for Quote (RFQ) document.

This module assumes you already have plain text from the RFQ (PDF text layer,
OCR output, or a Word doc converted to text). File ingestion is a separate
step - see ingest.py (not built yet).

Requires: pip install anthropic --break-system-packages
Requires: ANTHROPIC_API_KEY environment variable
"""

import os
import json
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# This schema is the contract for everything downstream: the review UI, the
# Excel fee template fill, and the Quotient URL prefill all read from this
# same shape. Change it here, not in three different places.
EXTRACTION_TOOL = {
    "name": "extract_rfq",
    "description": "Extract structured proposal information from a Request for Quote (RFQ) document.",
    "input_schema": {
        "type": "object",
        "properties": {
            "project_title": {
                "type": "string",
                "description": "Short working title for the project, suitable as a quote title",
            },
            "project_type": {
                "type": "string",
                "description": "Category of work, e.g. 'flood mitigation concept design', 'drainage modelling', 'hydraulic assessment'",
            },
            "background": {
                "type": "string",
                "description": "2-4 sentence summary of project context and why the work is needed",
            },
            "site_address": {
                "type": "string",
                "description": "Site, catchment, or location referenced in the RFQ. Empty string if not stated.",
            },
            "phases": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "phase_name": {
                            "type": "string",
                            "description": "Name of this phase/stage, e.g. 'Phase 3.1 Drainage and Stormwater Management Strategy'",
                        },
                        "deliverables": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Distinct deliverables/tasks within this phase, as separate line items",
                        },
                    },
                    "required": ["phase_name", "deliverables"],
                },
                "description": "Deliverables grouped into phases/stages. If the RFQ explicitly describes staged work (Phase 1, Stage 2, etc.), use those groupings and names. If the RFQ does NOT describe explicit phases, return exactly ONE phase containing all deliverables, named after the overall scope - do not invent a staging breakdown that isn't actually in the source document. Staging is a professional judgment call for the proposal writer, not something to fabricate from a flat scope list.",
            },
            "authority_requirements": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Council/authority standards, guidelines, or approval requirements mentioned (e.g. ARR2019, a named council design guide, planning scheme clauses)",
            },
            "key_dates": {
                "type": "object",
                "properties": {
                    "rfq_received_date": {"type": "string", "description": "Empty string if not stated"},
                    "submission_deadline": {"type": "string", "description": "Empty string if not stated"},
                    "anticipated_start": {"type": "string", "description": "Empty string if not stated"},
                },
                "required": ["rfq_received_date", "submission_deadline", "anticipated_start"],
            },
            "budget_signals": {
                "type": "string",
                "description": "Any stated budget, fee cap, or cost expectation. Empty string if none mentioned - do not guess a number.",
            },
            "contact": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "phone": {"type": "string"},
                    "company": {"type": "string"},
                },
                "required": ["name", "email", "phone", "company"],
            },
            "extraction_notes": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Separate, distinct items the human reviewer should specifically check before this becomes a quote - e.g. missing info, ambiguity, contradictions, or signs this document isn't actually an RFQ. Each item should be its own short, self-contained point, not a long paragraph. Empty list if nothing stands out.",
            },
        },
        "required": [
            "project_title",
            "project_type",
            "background",
            "phases",
            "authority_requirements",
            "contact",
            "extraction_notes",
        ],
    },
}

EXTRACTION_PROMPT = """Extract proposal information from this Request for Quote material.

If multiple source documents are included below (marked by "--- Source file: X ---"), first work out which one is the ACTUAL request for services - typically a covering letter, scope of works, or RFQ that is addressed to the consultant and asks them to do something. Other documents (planning scheme schedules, technical guidelines, standards, hazard data, council clauses) are often supporting REFERENCE material that the actual request points to for further detail - e.g. "refer attached DPO50 for full requirements" means DPO50 is background, not the scope itself.

Rules:
- "phases"/"deliverables": extract ONLY from what the actual request asks the consultant to deliver. Do not pull in every technical study or requirement listed in a supporting reference document just because it's mentioned there - a planning scheme schedule for an entire precinct will list far more studies (traffic, ecology, bushfire, landscape, cultural heritage, etc.) than any one consultant's actual scope. If a reference document's items aren't named in the actual request's own scope section, leave them out.
- "authority_requirements" and "background" CAN draw on supporting reference documents, since those legitimately describe the regulatory context the work sits within.
- If a document looks like it's the ONLY one provided and it's clearly a broad reference/schedule rather than an actual request to a consultant (no consultant is asked to do anything specific), note this in "extraction_notes" rather than treating every item it lists as a deliverable.
- If a field isn't explicitly stated, leave it empty (empty string or empty list) - never guess or infer a number, date, or commitment that isn't in the text.
- "phases": group deliverables by phase/stage ONLY if the RFQ explicitly describes staged work. Otherwise return one phase containing everything, named after the overall scope. Deliverables within a phase should be separate, concrete items, not a paraphrase of the whole scope in one sentence.
- "extraction_notes" should be a list of separate, short points - not one long paragraph. Each point should stand alone (e.g. "No submission deadline stated", "Two different site addresses mentioned", "This document is a planning scheme schedule, not a covering RFQ - confirm whether a separate brief exists").

Document(s):
---
{document_text}
---"""


def extract_rfq(document_text: str) -> dict:
    """Takes raw RFQ text, returns a dict matching EXTRACTION_TOOL's input_schema."""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        tools=[EXTRACTION_TOOL],
        tool_choice={"type": "tool", "name": "extract_rfq"},
        messages=[
            {"role": "user", "content": EXTRACTION_PROMPT.format(document_text=document_text)}
        ],
    )
    for block in response.content:
        if block.type == "tool_use" and block.name == "extract_rfq":
            return block.input
    raise ValueError("Model did not return a structured extraction - check the response for refusal text")


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else None
    if not path:
        print("Usage: python extract_rfq.py <path-to-text-file>")
        sys.exit(1)
    with open(path, "r") as f:
        text = f.read()
    result = extract_rfq(text)
    print(json.dumps(result, indent=2))
