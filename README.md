# Rain Proposal Tool

This workspace contains the `Rain-Proposal-Tool` project and related helper scripts for generating proposal documents from RFQs.

Contents
- `Rain-Proposal-Tool/` — project folder (note: currently an embedded repository in this parent repo)
- `app.py`, `generate_proposal.py`, `ingest.py`, etc. — Python scripts used by the tool
- `static/`, `templates/`, `docx/` — static assets, HTML templates, and docx helper package

Quick start

1. Create a Python virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements
```

2. Run the app (example):

```powershell
python app.py
```

Notes
- This repository currently contains the `Rain-Proposal-Tool` folder as an embedded Git repository (a gitlink). If you intended to include the full project contents in this remote rather than as a submodule, remove the embedded repo from the index and re-add files:

```powershell
git rm --cached Rain-Proposal-Tool
git add Rain-Proposal-Tool/* -A
git commit -m "Add Rain-Proposal-Tool contents"
```

- Edit this `README.md` with more detailed usage, license, and contribution instructions as needed.
