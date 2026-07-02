"""
Run with:  python app.py
Then open: http://localhost:5000

Requires ANTHROPIC_API_KEY set in the environment (or in .env).

Modes:
  quick  — extract_rfq only → show project details, phases, deliverables. ~20-40s.
  full   — full pipeline: extract + research (optional) + proposal doc + fee template. ~1-2 min.

Cost-saving options (set in .env):
  TEST_MODE=1   — skips all API calls, returns a realistic fixture. Zero cost. Good for UI testing.
  USE_HAIKU=1   — switches all models to claude-haiku-4-5 (~20x cheaper). Good for real flow testing.
"""

import os
import uuid
import traceback
from flask import Flask, request, render_template, send_file
from dotenv import load_dotenv

load_dotenv()  # loads ANTHROPIC_API_KEY and other vars from .env

TEST_MODE = os.environ.get("TEST_MODE", "0") == "1"
USE_HAIKU = os.environ.get("USE_HAIKU", "0") == "1"

if USE_HAIKU:
    os.environ["RAIN_MODEL"] = "claude-haiku-4-5"

from ingest import extract_text, ScannedPdfError, UnsupportedFileError
from extract_rfq import extract_rfq
from fill_fee_template import fill_phased_template, rough_fee_estimate
from quotient_url import build_quotient_prefill_url
from draft_proposal_doc import generate_draft_proposal
from research_site import research_site
from generate_proposal import generate_proposal_content

if TEST_MODE:
    from test_fixture import FIXTURE_EXTRACTED, FIXTURE_ESTIMATE, FIXTURE_SECTIONS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
TEMPLATE_XLSX = os.path.join(BASE_DIR, "Rain_Project_Fee_Tracker_Template.xlsx")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20MB


@app.route("/", methods=["GET"])
def index():
    return render_template(
        "index.html",
        test_mode=TEST_MODE,
        use_haiku=USE_HAIKU,
    )


@app.route("/process", methods=["POST"])
def process():
    mode = request.form.get("mode", "quick")  # "quick" or "full"

    # ── TEST MODE — no API calls, no file needed ─────────────────────────────
    if TEST_MODE:
        extracted = FIXTURE_EXTRACTED
        warnings = ["⚠️ TEST MODE — this is fixture data, not a real extraction."]

        if mode == "quick":
            return render_template(
                "result.html",
                extracted=extracted,
                warnings=warnings,
                mode="quick",
                source_files=["test_fixture.rfq"],
                estimate_text=None,
                quotient_url=None,
                download_filename=None,
                docx_filename=None,
                include_research=False,
                test_mode=True,
            )

        return render_template(
            "result.html",
            extracted=extracted,
            warnings=warnings,
            mode="full",
            source_files=["test_fixture.rfq"],
            estimate_text=FIXTURE_ESTIMATE,
            quotient_url="#",
            download_filename=None,
            docx_filename=None,
            include_research=False,
            test_mode=True,
        )

    # ── NORMAL MODE — real file required ─────────────────────────────────────
    uploaded_files = [f for f in request.files.getlist("rfq_file") if f and f.filename]
    if not uploaded_files:
        return render_template("index.html", error="No file selected.", test_mode=False, use_haiku=USE_HAIKU)

    run_id = uuid.uuid4().hex[:8]
    text_sections = []
    skipped = []

    for uploaded in uploaded_files:
        upload_path = os.path.join(UPLOAD_DIR, f"{run_id}_{uploaded.filename}")
        uploaded.save(upload_path)
        try:
            file_text = extract_text(upload_path)
            text_sections.append(f"--- Source file: {uploaded.filename} ---\n{file_text}")
        except ScannedPdfError as e:
            skipped.append(f"{uploaded.filename}: {e}")
        except UnsupportedFileError as e:
            skipped.append(f"{uploaded.filename}: {e}")
        except Exception:
            skipped.append(f"{uploaded.filename}: couldn't read ({traceback.format_exc(limit=1).strip()})")

    if not text_sections:
        return render_template(
            "index.html",
            error="None of the uploaded files could be read:\n" + "\n".join(skipped),
            test_mode=False,
            use_haiku=USE_HAIKU,
        )

    combined_text = "\n\n".join(text_sections)

    try:
        extracted = extract_rfq(combined_text)
    except Exception as e:
        return render_template("index.html", error=f"Extraction failed: {e}", test_mode=False, use_haiku=USE_HAIKU)

    warnings = list(skipped)

    # ── QUICK MODE ────────────────────────────────────────────────────────────
    if mode == "quick":
        return render_template(
            "result.html",
            extracted=extracted,
            warnings=warnings,
            mode="quick",
            source_files=[f.filename for f in uploaded_files],
            estimate_text=None,
            quotient_url=None,
            download_filename=None,
            docx_filename=None,
            include_research=False,
            test_mode=False,
        )

    # ── FULL MODE ─────────────────────────────────────────────────────────────
    output_filename = f"{run_id}_fee_template.xlsx"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    fill_warnings = fill_phased_template(TEMPLATE_XLSX, output_path, extracted)
    warnings += fill_warnings

    include_research = request.form.get("include_research") == "1"
    research = None
    if include_research:
        try:
            research = research_site(extracted)
            if research.get("gaps"):
                for gap in research["gaps"]:
                    warnings.append(f"Planning research gap: {gap}")
        except Exception as e:
            warnings.append(f"Planning research failed: {e}")

    sections = {}
    try:
        sections = generate_proposal_content(extracted, research)
    except Exception as e:
        warnings.append(f"Proposal content generation failed: {e}")

    docx_filename = f"{run_id}_draft_proposal.docx"
    docx_path = os.path.join(OUTPUT_DIR, docx_filename)
    try:
        generate_draft_proposal(extracted, sections, docx_path, research)
    except Exception as e:
        warnings.append(f"Draft proposal document failed to generate: {e}")
        docx_filename = None

    estimate_text = rough_fee_estimate(extracted)
    quotient_url = build_quotient_prefill_url(extracted)

    return render_template(
        "result.html",
        extracted=extracted,
        warnings=warnings,
        estimate_text=estimate_text,
        quotient_url=quotient_url,
        download_filename=output_filename,
        docx_filename=docx_filename,
        source_files=[f.filename for f in uploaded_files],
        include_research=include_research,
        mode="full",
        test_mode=False,
    )


@app.route("/download/<filename>")
def download(filename):
    if not filename or filename == "None":
        return "No file was generated for download.", 404

    path = os.path.join(OUTPUT_FOLDER, filename)

    if not os.path.exists(path):
        return f"File not found: {filename}", 404

    return send_file(path, as_attachment=True, download_name=filename)


if __name__ == "__main__":
    if TEST_MODE:
        print(">>> TEST MODE ON — no API calls will be made.")
    elif USE_HAIKU:
        print(">>> USE_HAIKU ON — using claude-haiku-4-5 (cheaper).")
    if not TEST_MODE and not os.environ.get("ANTHROPIC_API_KEY"):
        print("WARNING: ANTHROPIC_API_KEY is not set — extraction will fail.")
    app.run(debug=True, port=5000)
