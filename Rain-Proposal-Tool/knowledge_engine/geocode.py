# knowledge_engine/geocode.py

import requests


def geocode_address(address: str) -> dict:
    if not address:
        return {
            "address": None,
            "lat": None,
            "lon": None,
            "council": None,
            "source": "No address provided"
        }

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": f"{address}, Victoria, Australia",
        "format": "json",
        "addressdetails": 1,
        "limit": 1
    }

    headers = {
        "User-Agent": "RAIN-Proposal-Tool/1.0"
    }

    response = requests.get(url, params=params, headers=headers, timeout=15)
    response.raise_for_status()

    results = response.json()

    if not results:
        return {
            "address": address,
            "formatted_address": None,
            "lat": None,
            "lon": None,
            "suburb": None,
            "postcode": None,
            "council": None,
            "state": "VIC",
            "country": "Australia",
            "source": "Nominatim - no match found"
        }

    result = results[0]
    details = result.get("address", {})

    return {
        "address": address,
        "formatted_address": result.get("display_name"),
        "lat": float(result["lat"]),
        "lon": float(result["lon"]),
        "suburb": details.get("suburb") or details.get("town") or details.get("village"),
        "postcode": details.get("postcode"),
        "council": details.get("municipality") or details.get("county"),
        "state": details.get("state"),
        "country": details.get("country"),
        "source": "OpenStreetMap Nominatim"
    }