# research_site.py

import re
import requests
from typing import Any, Dict, Optional


ADDRESS_RE = re.compile(
    r"\b\d{1,5}\s+[A-Za-z0-9'\- ]+\s+"
    r"(?:Road|Rd|Street|St|Avenue|Ave|Drive|Dr|Court|Ct|Lane|Ln|Way|Place|Pl|"
    r"Crescent|Cres|Highway|Hwy|Parade|Pde|Terrace|Tce|Close|Cl)"
    r",?\s+[A-Za-z'\- ]+"
    r"(?:,?\s+VIC|,?\s+Victoria)?\b",
    re.IGNORECASE,
)


def clean_site_address(raw: str) -> str:
    """
    Cleans a raw address so the proposal does not use the PDF title as the site address.
    Example:
    '15 Avalon Road, Avalon Hydrological Engineering Scope Of Works VIC'
    becomes:
    '15 Avalon Road, Avalon VIC'
    """

    if not raw:
        return ""

    raw = raw.replace("\n", " ")
    raw = re.sub(r"\s+", " ", raw).strip()

    match = ADDRESS_RE.search(raw)
    if match:
        address = match.group(0).strip()
    else:
        address = raw

    junk_phrases = [
        "Hydrological Engineering Scope Of Works",
        "Hydrological Engineering Scope of Works",
        "Scope Of Works",
        "Scope of Works",
        "Phase 1",
        "Phase 2",
        "Phase 3",
        "Phase 4",
        "Phase 5",
        "v1",
        "v2",
        ".pdf",
        "pdf",
    ]

    for phrase in junk_phrases:
        address = re.sub(re.escape(phrase), "", address, flags=re.IGNORECASE)

    address = re.sub(r"\s+", " ", address).strip(" -,_.")

    if address and "VIC" not in address.upper() and "VICTORIA" not in address.upper():
        address += " VIC"

    return address


def extract_site_address(text: str, fallback: str = "") -> str:
    """
    Finds the best project address from the RFQ text.
    Uses fallback only if no address is found in the body text.
    """

    combined = f"{text or ''}\n{fallback or ''}"

    match = ADDRESS_RE.search(combined)
    if match:
        return clean_site_address(match.group(0))

    return clean_site_address(fallback)


def geocode_address(address: str) -> Dict[str, Any]:
    """
    Gets latitude and longitude using OpenStreetMap Nominatim.
    No API key required.
    """

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
        "User-Agent": "RAIN-Proposal-Drafter/1.0"
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
            "raw": result,
        }

    except Exception as error:
        return {
            "error": str(error)
        }


def infer_victorian_authorities(address: str, geocode: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    """
    Practical authority fallback.
    This prevents blank proposal tables when online research does not return clean data.

    Add more project locations here over time.
    """

    geocode = geocode or {}

    combined = " ".join([
        address or "",
        geocode.get("display_name", "") or "",
    ]).lower()

    if "avalon" in combined:
        return {
            "council": "City of Greater Geelong",
            "traditional_owners": "Wadawurrung Traditional Owners Aboriginal Corporation",
            "cma": "Corangamite Catchment Management Authority",
            "water_authority": "Barwon Water",
        }

    return {
        "council": "",
        "traditional_owners": "",
        "cma": "",
        "water_authority": "",
    }


def research_site(text: str, extracted: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Main function used by the proposal generator.

    Inputs:
    - text: full extracted RFQ text
    - extracted: dictionary from extract_rfq.py

    Output:
    - clean site research dictionary used by draft_proposal_doc.py
    """

    extracted = extracted or {}

    fallback_address = (
        extracted.get("site_address")
        or extracted.get("location")
        or extracted.get("project_location")
        or extracted.get("project_title")
        or ""
    )

    site_address = extract_site_address(text, fallback_address)

    geocode = geocode_address(site_address)
    authorities = infer_victorian_authorities(site_address, geocode)

    return {
        "site_address": site_address or "Not identified",
        "latitude": geocode.get("latitude") or "Not identified",
        "longitude": geocode.get("longitude") or "Not identified",

        "council": authorities.get("council") or "Not identified",
        "traditional_owners": authorities.get("traditional_owners") or "Not identified",
        "cma": authorities.get("cma") or "Not identified",
        "water_authority": authorities.get("water_authority") or "Not identified",

        "zone": "To be confirmed from VicPlan",
        "dpo": "DPO50, subject to confirmation from VicPlan",
        "sbo": "To be confirmed from VicPlan",
        "lsio": "To be confirmed from VicPlan",
        "fo": "To be confirmed from VicPlan",
        "planning_source": "VicPlan / planning research",
    }