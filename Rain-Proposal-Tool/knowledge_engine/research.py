# research_engine/research.py

from .geocode import geocode_address
from .planning import get_planning_controls
from .authorities import get_authorities


def run_research(address: str) -> dict:
    """
    Main research function.

    Input:
        address: project address as text

    Output:
        dictionary containing research results
    """

    if not address:
        return {
            "address": None,
            "coordinates": None,
            "authorities": {},
            "planning_controls": {},
            "confidence": "low",
            "notes": ["No address was provided."]
        }

    location = geocode_address(address)

    authorities = get_authorities(location)
    planning_controls = get_planning_controls(location)

    return {
        "address": address,
        "coordinates": location,
        "authorities": authorities,
        "planning_controls": planning_controls,
        "confidence": "draft",
        "notes": [
            "Research engine result is preliminary.",
            "Planning controls should be verified against VicPlan before issuing the proposal."
        ]
    }