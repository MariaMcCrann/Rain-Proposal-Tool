"""
Realistic fake RFQ extraction result — used when TEST_MODE=1 in .env.
Zero API cost. Designed to look like a real Rain Consulting stormwater project.
"""

FIXTURE_EXTRACTED = {
    "project_title": "Epsom Road Drainage Investigation – Concept Design",
    "project_type": "Stormwater drainage investigation and concept design",
    "background": (
        "The City of Greater Bendigo has identified repeated surface flooding along Epsom Road "
        "between McIvor Highway and Holdsworth Road following significant rainfall events. "
        "Council is seeking engineering services to investigate the existing drainage system, "
        "assess flood risk to affected properties, and develop a concept design for upgrade works."
    ),
    "site_address": "Epsom Road, Epsom VIC 3551 (between McIvor Highway and Holdsworth Road)",
    "phases": [
        {
            "phase_name": "Phase 1 – Drainage Investigation and Data Review",
            "deliverables": [
                "Review of existing drainage infrastructure, as-constructed plans, and flood complaints data",
                "Site inspection and condition assessment of existing culverts and pits",
                "Review of Council's stormwater master plan and any existing hydraulic models",
                "Desktop flood risk assessment against 5%, 2%, and 1% AEP events",
                "Stakeholder briefing note summarising findings",
            ],
        },
        {
            "phase_name": "Phase 2 – Hydraulic Modelling",
            "deliverables": [
                "Development of TUFLOW 1D/2D hydraulic model of the Epsom Road catchment",
                "Calibration and validation against known flood events where data available",
                "Modelling of existing conditions for 10%, 5%, 2%, and 1% AEP events",
                "Identification of overland flow paths and flood affectation extents",
                "Hydraulic model report",
            ],
        },
        {
            "phase_name": "Phase 3 – Concept Design and Reporting",
            "deliverables": [
                "Development of two concept design options for drainage upgrade",
                "Preliminary cost estimate for each option (±30%)",
                "Options assessment against Council's criteria (cost, constructability, environmental impact)",
                "Concept design drawings (A3 format)",
                "Final drainage investigation and concept design report",
                "Presentation of findings to Council engineering team",
            ],
        },
    ],
    "authority_requirements": [
        "City of Greater Bendigo Stormwater Management Plan 2021",
        "Australian Rainfall and Runoff (ARR) 2019 guidelines",
        "DELWP Urban Stormwater – Best Practice Environmental Management Guidelines",
        "Loddon Mallee Regional Catchment Strategy",
        "Planning Scheme Clause 56.07 – Integrated Water Management",
    ],
    "key_dates": {
        "rfq_received_date": "14 June 2026",
        "submission_deadline": "11 July 2026",
        "anticipated_start": "August 2026",
    },
    "budget_signals": "Fee cap of $45,000 (ex. GST) as stated in RFQ",
    "contact": {
        "name": "James Hartley",
        "email": "j.hartley@bendigo.vic.gov.au",
        "phone": "03 5434 6000",
        "company": "City of Greater Bendigo",
    },
    "extraction_notes": [
        "Fee cap of $45,000 ex GST is stated — worth confirming whether Phase 2 hydraulic modelling can be delivered within this given the TUFLOW requirement.",
        "RFQ does not specify whether an existing TUFLOW model is available — confirm with Council before scoping modelling effort.",
        "Submission deadline is 11 July (10 days away) — flag internally.",
    ],
}

FIXTURE_ESTIMATE = """Rough fee estimate (TEST MODE — not real)
─────────────────────────────────────────
Phase 1 – Investigation & Data Review      ~$8,000 – $10,000
Phase 2 – Hydraulic Modelling             ~$18,000 – $22,000
Phase 3 – Concept Design & Reporting      ~$12,000 – $15,000
─────────────────────────────────────────
TOTAL (indicative)                        ~$38,000 – $47,000 ex GST

Note: Client fee cap is $45,000 ex GST. Modelling scope should
be confirmed before finalising the fee.
"""

FIXTURE_SECTIONS = {
    "executive_summary": "Rain Consulting is pleased to submit this proposal for the Epsom Road Drainage Investigation and Concept Design. Our team brings extensive experience in hydraulic modelling and drainage design across the Greater Bendigo region.",
    "project_understanding": "We understand Council is seeking to address recurring surface flooding on Epsom Road through a structured investigation, hydraulic assessment, and concept design process.",
    "methodology": "Our approach follows a three-phase structure aligned with Council's brief, commencing with data review and site investigation before progressing to hydraulic modelling and concept design development.",
}
