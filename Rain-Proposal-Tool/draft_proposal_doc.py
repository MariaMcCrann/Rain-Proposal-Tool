"""
Python wrapper around draft_proposal_doc.js. Now passes a richer JSON
containing the extracted project data, generated section content, and
optional research results.
"""

import json
import subprocess
import tempfile
import os

SCRIPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "draft_proposal_doc.js")


def generate_draft_proposal(extracted: dict, sections: dict, output_path: str, research: dict | None = None) -> None:
    payload = {
        "extracted": extracted,
        "sections": sections,
        "research": research,
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(payload, f)
        input_path = f.name
    try:
        try:
            result = subprocess.run(
                ["node", SCRIPT_PATH, input_path, output_path],
                capture_output=True, text=True, timeout=60,
            )
        except FileNotFoundError:
            raise RuntimeError(
                "Node.js isn't installed (or isn't on your PATH) - the draft proposal document needs it. "
                "Run 'node --version' in your terminal to check. Everything else (the Excel fee template, "
                "extraction, rough estimate) works fine without it - this only affects the .docx download."
            )
        if result.returncode != 0:
            raise RuntimeError(f"Draft proposal generation failed: {result.stderr}")
    finally:
        os.unlink(input_path)
