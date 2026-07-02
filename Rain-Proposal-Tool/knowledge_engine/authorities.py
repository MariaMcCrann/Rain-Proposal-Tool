# research_engine/authorities.py

from pathlib import Path
import csv

DATA_FILE = Path(__file__).parent / "data" / "authority_lookup.csv"


def get_authorities(location: dict) -> dict:
    """
    Returns the council, CMA and water authority for a location.

    Currently uses a local CSV lookup.
    Later this can be replaced with Vicmap or GIS services.
    """

    council = location.get("council")

    if not council:
        return {
            "council": None,
            "cma": None,
            "water_authority": None,
            "source": "Placeholder"
        }

    if not DATA_FILE.exists():
        return {
            "council": council,
            "cma": None,
            "water_authority": None,
            "source": "CSV not found"
        }

    with open(DATA_FILE, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["Council"].strip().lower() == council.strip().lower():
                return {
                    "council": row["Council"],
                    "cma": row["CMA"],
                    "water_authority": row["Water Authority"],
                    "source": "Local CSV"
                }

    return {
        "council": council,
        "cma": None,
        "water_authority": None,
        "source": "Council not found in CSV"
    }