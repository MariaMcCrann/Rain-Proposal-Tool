# knowledge_engine/planning.py

def get_planning_controls(location: dict) -> dict:
    """
    Temporary placeholder.

    Later this function will connect to VicPlan / Vicmap Planning data.
    """

    return {
        "planning_scheme": None,
        "zone": None,
        "overlays": [],
        "sbo": False,
        "lsio": False,
        "fo": False,
        "dpo": False,
        "source": "Placeholder",
        "notes": [
            "Planning controls have not been automatically checked yet.",
            "Verify planning controls manually in VicPlan before issuing the proposal."
        ]
    }