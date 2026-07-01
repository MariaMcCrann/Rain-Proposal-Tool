# Rain Proposal Tool

Overview

This repository contains the Rain-Proposal-Tool project — a collection of scripts and helpers for ingesting RFQs and generating proposal documents (Python + minimal frontend templates).

Repository layout

- `Rain-Proposal-Tool/` — project folder (now tracked as normal files in this repo)
- Top-level scripts: `app.py`, `generate_proposal.py`, `ingest.py`, `extract_rfq.py`, etc.
- `static/`, `templates/` — frontend assets and HTML templates
- `Rain-Proposal-Tool/node_modules_1/` — vendored JS helper package (not tracked)

Requirements

- Python 3.10+ recommended
- Install Python requirements listed in `requirements` (plain pip file)

Quick start

1. Create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements
```

2. Run the app locally (example):

```powershell
python app.py
```

Development notes

- The previous repository contained `Rain-Proposal-Tool` as an embedded Git repo (gitlink). This repository has been converted so the `Rain-Proposal-Tool` directory is now tracked directly.
- Large generated or installed artifacts such as `node_modules/`, Python virtual environments, and `__pycache__` are ignored via `.gitignore`.
- If you see files that should be ignored but are tracked, run:

```powershell
git rm -r --cached Rain-Proposal-Tool
git add Rain-Proposal-Tool -A
git commit -m "chore: remove ignored files from Rain-Proposal-Tool"
git push origin master
```

Contributing

- Please open issues or pull requests on the remote repository.
- Follow standard GitHub flow: create a branch, make changes, add tests or example usage, and open a PR.

License

Add license information here (e.g., MIT) if you want this project licensed publicly.

Contact

For questions, contact the repository owner.

