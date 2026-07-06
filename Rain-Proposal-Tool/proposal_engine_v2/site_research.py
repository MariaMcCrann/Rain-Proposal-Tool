import re
from typing import Dict, Any

import requests

from .models import SiteResearch, PlanningInfo
from .text_utils import collapse_spaces


def clean_research_address(address: str) -> str:
    address = collapse_spaces(address)
    address = address.strip(" -,_.")

    junk_phrases = [
        "Hydrological Engineering Scope Of Works",
        "Hydrological Engineering Scope of Works",
        "Scope Of Works",
        "Scope of Works",
        ".pdf",
        "pdf",
        "v1",
        "v2",
    ]

    for phrase in junk_phrases:
        address = re.sub(re.escape(phrase), "", address, flags=re.IGNORECASE)

    address = collapse_spaces(address).strip(" -,_.")

    if address and "vic" not in address.lower() and "victoria" not in address.lower():
        address += " VIC"

    return address


def geocode_address(address: str) -> Dict[str, Any]:
    if not address:
        return {}

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": address,
        "format": "json",
        "limit": 1,
        "countrycodes": "au",
        "addressdetails": 1,
    }

    headers = {
        "User-Agent": "RAIN-Proposal-Tool-V2/1.0"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        results = response.json()

        if not results:
            return {}

        result = results[0]

        return {
            "latitude": result.get("lat", ""),
            "longitude": result.get("lon", ""),
            "display_name": result.get("display_name", ""),
            "address": result.get("address", {}),
            "raw": result,
        }

    except Exception as error:
        return {"error": str(error)}


VICTORIAN_LOCATION_LOOKUP = {
    "avalon": {
        "council": "City of Greater Geelong",
        "traditional_owners": "Wadawurrung Traditional Owners Aboriginal Corporation",
        "cma": "Corangamite Catchment Management Authority",
        "water_authority": "Barwon Water",
        "planning_scheme": "Greater Geelong Planning Scheme",
        "planning_notes": [
            "Planning controls should be confirmed using VicPlan before final issue.",
            "Development Plan Overlay and flood-related overlays should be reviewed against the subject land parcel.",
        ],
    },
    "bendigo": {
        "council": "City of Greater Bendigo",
        "traditional_owners": "Dja Dja Wurrung Clans Aboriginal Corporation",
        "cma": "North Central Catchment Management Authority",
        "water_authority": "Coliban Water",
        "planning_scheme": "Greater Bendigo Planning Scheme",
        "planning_notes": [
            "Planning controls should be confirmed using VicPlan before final issue.",
        ],
    },
    "flora hill": {
        "council": "City of Greater Bendigo",
        "traditional_owners": "Dja Dja Wurrung Clans Aboriginal Corporation",
        "cma": "North Central Catchment Management Authority",
        "water_authority": "Coliban Water",
        "planning_scheme": "Greater Bendigo Planning Scheme",
        "planning_notes": [
            "Planning controls should be confirmed using VicPlan before final issue.",
        ],
    },
    "kennington": {
        "council": "City of Greater Bendigo",
        "traditional_owners": "Dja Dja Wurrung Clans Aboriginal Corporation",
        "cma": "North Central Catchment Management Authority",
        "water_authority": "Coliban Water",
        "planning_scheme": "Greater Bendigo Planning Scheme",
        "planning_notes": [
            "Planning controls should be confirmed using VicPlan before final issue.",
        ],
    },
}


def infer_location_key(address: str, geocode: Dict[str, Any]) -> str:
    combined = " ".join(
        [
            address or "",
            geocode.get("display_name", "") or "",
            " ".join(str(v) for v in geocode.get("address", {}).values()),
        ]
    ).lower()

    for key in VICTORIAN_LOCATION_LOOKUP:
        if key in combined:
            return key

    return ""


def infer_planning_info(location_data: Dict[str, Any]) -> PlanningInfo:
    notes = list(location_data.get("planning_notes", []))

    planning_scheme = location_data.get("planning_scheme", "")
    if planning_scheme:
        notes.insert(0, f"Relevant planning scheme: {planning_scheme}.")

    return PlanningInfo(
        zone="To be confirmed from VicPlan",
        overlays=[],
        dpo="To be confirmed from VicPlan",
        sbo="To be confirmed from VicPlan",
        lsio="To be confirmed from VicPlan",
        fo="To be confirmed from VicPlan",
        notes=notes,
    )


def research_site(address: str) -> SiteResearch:
    clean_address = clean_research_address(address)

    notes = []

    if not clean_address:
        return SiteResearch(
            notes=["No address was provided for site research."]
        )

    geocode = geocode_address(clean_address)

    if geocode.get("error"):
        notes.append(f"Geocoding failed: {geocode.get('error')}")

    if not geocode.get("latitude") or not geocode.get("longitude"):
        notes.append("Coordinates were not identified from the address.")

    location_key = infer_location_key(clean_address, geocode)
    location_data = VICTORIAN_LOCATION_LOOKUP.get(location_key, {})

    if not location_data:
        notes.append("Council, Traditional Owners, CMA and water authority were not inferred. Confirm manually.")

    planning = infer_planning_info(location_data)

    return SiteResearch(
        address=clean_address,
        latitude=geocode.get("latitude", ""),
        longitude=geocode.get("longitude", ""),
        council=location_data.get("council", ""),
        traditional_owners=location_data.get("traditional_owners", ""),
        cma=location_data.get("cma", ""),
        water_authority=location_data.get("water_authority", ""),
        planning=planning,
        notes=notes,
    )
