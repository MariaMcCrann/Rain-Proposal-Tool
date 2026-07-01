// Builds the full Rain Consulting fee proposal docx from generated section
// content. Receives a rich JSON with all 23 sections pre-written by Claude
// (generate_proposal.py) - this script's job is pure formatting, not writing.
//
// Usage: node draft_proposal_doc.js <input.json> <output.docx>

const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, BorderStyle, WidthType, ShadingType,
  LevelFormat, Header, PageNumber, NumberFormat,
} = require("docx");

const [,, inputPath, outputPath] = process.argv;
const data = JSON.parse(fs.readFileSync(inputPath, "utf8"));
const extracted = data.extracted || {};
const sections = data.sections || {};
const research = data.research || null;

// ── colours ──────────────────────────────────────────────────────────────────
const RAIN_TEAL   = "2C5F5F";
const RAIN_AMBER  = "C87818";
const WARN_AMBER  = "B45309";
const LIGHT_GREY  = "F5F5F5";
const MID_GREY    = "CCCCCC";

// ── numbering (bullets) ───────────────────────────────────────────────────────
const numbering = {
  config: [{
    reference: "bullets",
    levels: [{
      level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 720, hanging: 360 } } },
    }],
  }],
};

// ── helpers ───────────────────────────────────────────────────────────────────
function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    children: [new TextRun({ text, color: RAIN_TEAL })],
    spacing: { before: 360, after: 120 },
  });
}
function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    children: [new TextRun({ text, color: RAIN_TEAL, bold: true })],
    spacing: { before: 240, after: 80 },
  });
}
function h3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    children: [new TextRun({ text, italics: true })],
    spacing: { before: 160, after: 60 },
  });
}
function body(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({ text, ...opts })],
    spacing: { after: 120 },
  });
}
function bullet(text) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    children: [new TextRun(text)],
    spacing: { after: 80 },
  });
}
function spacer() {
  return new Paragraph({ children: [new TextRun("")], spacing: { after: 80 } });
}
function pageBreak() {
  return new Paragraph({ pageBreakBefore: true, children: [new TextRun("")] });
}
function draftWatermark(text) {
  return new Paragraph({
    children: [new TextRun({ text, bold: true, color: WARN_AMBER })],
    spacing: { after: 160 },
  });
}

// Parse a section's text into paragraphs and bullet runs
function renderSection(text) {
  if (!text) return [body("[Content not generated — check extraction and try again]", { italics: true, color: "888888" })];
  const blocks = [];
  for (const line of text.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed) { blocks.push(spacer()); continue; }
    // Pipe-delimited table rows (compliance matrix, scope risk check, etc.)
    if (trimmed.startsWith("-") && trimmed.includes(" | ")) {
      const cols = trimmed.replace(/^-\s*/, "").split(" | ");
      blocks.push(new Paragraph({
        children: [
          new TextRun({ text: cols[0] || "", bold: true }),
          ...cols.slice(1).flatMap((c, i) => [
            new TextRun({ text: " — ", color: MID_GREY }),
            new TextRun({ text: c }),
          ]),
        ],

        numbering: { reference: "bullets", level: 0 },
        spacing: { after: 80 },
      }));
    } else if (trimmed.startsWith("- ")) {
      blocks.push(bullet(trimmed.slice(2)));
    } else if (trimmed.startsWith("Task Name:") || trimmed.startsWith("Purpose:") ||
               trimmed.startsWith("Description:") || trimmed.startsWith("Deliverables:") ||
               trimmed.startsWith("Exclusions:") || trimmed.startsWith("Variation triggers:") ||
               trimmed.startsWith("Assumptions:")) {
      const colon = trimmed.indexOf(":");
      blocks.push(new Paragraph({
        children: [
          new TextRun({ text: trimmed.slice(0, colon + 1) + " ", bold: true }),
          new TextRun({ text: trimmed.slice(colon + 1).trim() }),
        ],
        spacing: { after: 80 },
      }));
    } else {
      blocks.push(body(trimmed));
    }
  }
  return blocks;
}

function simpleTable(headers, rows, options = {}) {
  const headerRow = new TableRow({
    children: headers.map((h) =>
      new TableCell({
        children: [new Paragraph({ children: [new TextRun({ text: h, bold: true, color: "ffffff" })] })],
        shading: { type: ShadingType.SOLID, color: RAIN_TEAL },
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
      })
    ),
    tableHeader: true,
  });
  const dataRows = rows.map((row, ri) =>
    new TableRow({
      children: row.map((cell) =>
        new TableCell({
          children: [new Paragraph({ children: [new TextRun(cell || "")] })],
          shading: ri % 2 === 0 ? undefined : { type: ShadingType.SOLID, color: LIGHT_GREY },
          margins: { top: 80, bottom: 80, left: 120, right: 120 },
        })
      ),
    })
  );
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    rows: [headerRow, ...dataRows],
    ...options,
  });
}

// ── document assembly ─────────────────────────────────────────────────────────
const children = [];

// Cover page
children.push(
  draftWatermark("DRAFT — FOR INTERNAL REVIEW ONLY. Not for client distribution until reviewed, fees entered, and readiness check cleared."),
  spacer(),
  new Paragraph({
    children: [new TextRun({ text: extracted.project_title || "Project Title", bold: true, size: 48, color: RAIN_TEAL })],
    spacing: { after: 120 },
  }),
  new Paragraph({
    children: [new TextRun({ text: extracted.project_type || "", size: 26, color: "555555" })],
    spacing: { after: 80 },
  }),
  new Paragraph({
    children: [new TextRun({ text: `Client: ${(extracted.contact || {}).company || "Not provided"}`, size: 24 })],
    spacing: { after: 60 },
  }),
  new Paragraph({
    children: [new TextRun({ text: `Site: ${extracted.site_address || "Not provided"}`, size: 24 })],
    spacing: { after: 60 },
  }),
  new Paragraph({
    children: [new TextRun({ text: `Prepared by: Rain Consulting Pty Ltd`, size: 24 })],
    spacing: { after: 60 },
  }),
  new Paragraph({
    children: [new TextRun({ text: `Date: ${new Date().toLocaleDateString("en-AU", { day: "numeric", month: "long", year: "numeric" })}`, size: 24 })],
    spacing: { after: 240 },
  }),
  pageBreak(),
);

// Document control table
children.push(
  h1("Document Control"),
  simpleTable(
    ["Revision", "Date", "Author", "Reviewer", "Status"],
    [["R01", new Date().toLocaleDateString("en-AU"), "Rain Consulting", "[Reviewer]", "DRAFT — Internal only"]]
  ),
  spacer(),
  pageBreak(),
);

// Readiness check (internal, before executive summary so it's seen first on review)
if (sections.readiness_check) {
  children.push(
    h1("Readiness Check (Internal — Remove Before Issuing)"),
    draftWatermark("This section must be removed before the proposal is sent to the client."),
    ...renderSection(sections.readiness_check),
    pageBreak(),
  );
}

// Executive summary
children.push(h1("Executive Summary"), ...renderSection(sections.executive_summary), spacer());

// Project understanding
children.push(h1("Project Understanding"), ...renderSection(sections.project_understanding), spacer());

// Site and planning context
children.push(h1("Site and Planning Context"), ...renderSection(sections.site_and_planning_context));
if (research) {
  children.push(
    h2("Planning Research Summary"),
    body("The following was identified from public sources during proposal preparation. Confirm all details before issuing.", { italics: true }),
    ...[
      ["Traditional Owners / RAP", research.traditional_owners],
      ["Responsible Council", research.council],
      ["Catchment Management Authority", research.cma],
      ["Water Authority", research.water_authority],
      ["Planning Controls", research.planning_controls],
      ["Existing Flood Models", research.existing_models],
    ].flatMap(([label, val]) => [
      new Paragraph({ children: [new TextRun({ text: label + ": ", bold: true }), new TextRun(val || "Not researched")], spacing: { after: 100 } }),
    ]),
  );
  if (research.gaps && research.gaps.length) {
    children.push(h2("Research Gaps — Requires Manual Follow-up"), ...research.gaps.map((g) => bullet(g)));
  }
}
children.push(spacer());

// Traditional owners and authority context
children.push(h1("Traditional Owners and Authority Context"), ...renderSection(sections.traditional_owners_and_authority), spacer());

// Existing model and data
children.push(h1("Existing Model and Data Search"), ...renderSection(sections.existing_model_and_data), spacer());

// Key project background
children.push(h1("Key Project Background"), ...renderSection(sections.key_project_background), pageBreak());

// Scope risk check
children.push(
  h1("Scope Risk Check"),
  body("Risk assessment prepared prior to proposal finalisation. Review before pricing.", { italics: true }),
  ...renderSection(sections.scope_risk_check),
  pageBreak(),
);

// Detailed scope
children.push(h1("Detailed Scope of Services"), ...renderSection(sections.detailed_scope_of_services), pageBreak());

// Methodology
children.push(h1("Methodology"), ...renderSection(sections.methodology), spacer());

// Deliverables
children.push(h1("Deliverables"), ...renderSection(sections.deliverables), spacer());

// Authority requirements
children.push(h1("Authority Requirements"), ...renderSection(sections.authority_requirements), spacer());

// Compliance matrix
children.push(
  h1("DPO / RFQ Compliance Matrix"),
  body("Each row maps a stated requirement to Rain's proposed deliverable and the phase in which it is addressed.", { italics: true }),
  ...renderSection(sections.compliance_matrix),
  spacer(),
);

// Required input data
children.push(h1("Required Input Data"), ...renderSection(sections.required_input_data), spacer());

// Assumptions
children.push(h1("Assumptions"), ...renderSection(sections.assumptions), spacer());

// Exclusions
children.push(h1("Exclusions"), ...renderSection(sections.exclusions), spacer());

// Optional and provisional
children.push(h1("Optional and Provisional Items"), ...renderSection(sections.optional_and_provisional), spacer());

// Variation triggers
children.push(h1("Risks, Clarifications and Variation Triggers"), ...renderSection(sections.variation_triggers), pageBreak());

// Fee structure
children.push(
  h1("Recommended Fee Structure"),
  draftWatermark("Fee amounts must be entered manually. This section shows the phase structure and fee basis only."),
);
const feePhaseRows = (sections.fee_structure_phases || "")
  .split("\n").filter((l) => l.trim().startsWith("-"))
  .map((l) => l.replace(/^-\s*/, "").split(" | ").map((s) => s.trim()));
if (feePhaseRows.length) {
  children.push(
    simpleTable(
      ["Phase / Deliverable", "Fee (Exc. GST)", "Fee Basis"],
      feePhaseRows.map((cols) => [cols[0] || "", "[Enter fee]", cols[2] || "Fixed fee"])
    ),
    spacer(),
    bullet("GST is additional at 10%."),
    bullet("Invoicing: monthly progress claims."),
    bullet("Full phase payment required prior to release of deliverables for authority submission."),
    bullet("Payment terms: 14 days from invoice date."),
  );
}
children.push(...renderSection(sections.fee_structure), pageBreak());

// Programme
children.push(h1("Programme and Key Dependencies"), ...renderSection(sections.programme), spacer());

// Draft proposal wording
children.push(
  h1("Draft Proposal Wording"),
  draftWatermark("The following is draft client-facing language. Review and edit before including in the formal proposal."),
  ...renderSection(sections.draft_proposal_wording),
);

// Extraction notes appendix
if ((extracted.extraction_notes || []).length) {
  children.push(
    pageBreak(),
    h1("Appendix — Extraction Notes (Remove Before Issuing)"),
    draftWatermark("These notes were flagged during automatic reading of the RFQ documents. Review and resolve before finalising."),
    ...(extracted.extraction_notes || []).map((n) => bullet(n)),
  );
}

// ── build document ────────────────────────────────────────────────────────────
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial" }, paragraph: { spacing: { before: 360, after: 120 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial" }, paragraph: { spacing: { before: 240, after: 80 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, italics: true, font: "Arial" }, paragraph: { spacing: { before: 160, after: 60 }, outlineLevel: 2 } },
    ],
  },
  numbering,
  sections: [{
    properties: {
      page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } },
    },
    children,
  }],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync(outputPath, buffer);
  console.log(`Written: ${outputPath}`);
});
