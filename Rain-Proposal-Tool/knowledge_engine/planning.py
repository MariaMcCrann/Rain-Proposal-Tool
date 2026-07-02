# research_engine/planning.py

def get_planning_controls(location: dict) -> dict:
    return {
        "planning_scheme": None,
        "zone": None,
        "overlays": [],
        "sbo": False,
        "lsio": False,
        "fo": False,
        "dpo": False,
        "source": "VicPlan / Vicmap Planning REST API"
    }