"""
Address Normalizer Module

Standardizes address formats for consistent geocoding results.
Expands abbreviations, adds province/country context, and cleans whitespace.
"""

import re
from typing import Optional


# Common Canadian address abbreviations
STREET_ABBREVIATIONS = {
    r"\bSt\b": "Street",
    r"\bAve\b": "Avenue",
    r"\bBlvd\b": "Boulevard",
    r"\bDr\b": "Drive",
    r"\bRd\b": "Road",
    r"\bCrt\b": "Court",
    r"\bCt\b": "Court",
    r"\bPl\b": "Place",
    r"\bCres\b": "Crescent",
    r"\bCr\b": "Crescent",
    r"\bTce\b": "Terrace",
    r"\bTerr\b": "Terrace",
    r"\bLn\b": "Lane",
    r"\bPky\b": "Parkway",
    r"\bPkwy\b": "Parkway",
    r"\bHwy\b": "Highway",
    r"\bCir\b": "Circle",
    r"\bSq\b": "Square",
    r"\bGdn\b": "Garden",
    r"\bGdns\b": "Gardens",
    r"\bGate\b": "Gate",
    r"\bPath\b": "Path",
    r"\bWay\b": "Way",
    r"\bTrl\b": "Trail",
    r"\bMews\b": "Mews",
    r"\bGrv\b": "Grove",
    r"\bHts\b": "Heights",
}

DIRECTION_ABBREVIATIONS = {
    r"\bN\b": "North",
    r"\bS\b": "South",
    r"\bE\b": "East",
    r"\bW\b": "West",
    r"\bNE\b": "Northeast",
    r"\bNW\b": "Northwest",
    r"\bSE\b": "Southeast",
    r"\bSW\b": "Southwest",
}

UNIT_ABBREVIATIONS = {
    r"\bSte\b": "Suite",
    r"\bApt\b": "Apartment",
    r"\bUnit\b": "Unit",
    r"\bFl\b": "Floor",
    r"\bFlr\b": "Floor",
    r"\bRm\b": "Room",
    r"\bBldg\b": "Building",
}

# Ontario municipalities for recognition
ONTARIO_MUNICIPALITIES = [
    "Toronto",
    "Ottawa",
    "Mississauga",
    "Brampton",
    "Hamilton",
    "London",
    "Markham",
    "Vaughan",
    "Kitchener",
    "Windsor",
    "Richmond Hill",
    "Oakville",
    "Burlington",
    "Greater Sudbury",
    "Oshawa",
    "Barrie",
    "St. Catharines",
    "Cambridge",
    "Kingston",
    "Guelph",
    "Thunder Bay",
    "Waterloo",
    "Whitby",
    "Ajax",
    "Milton",
    "Newmarket",
    "Peterborough",
    "Sarnia",
    "Niagara Falls",
    "Sault Ste. Marie",
    "Brantford",
    "North Bay",
    "Belleville",
    "Pickering",
    "Aurora",
    "Welland",
    "Stouffville",
    "Caledon",
    "Clarington",
    "Halton Hills",
    "Innisfil",
    "Bradford",
    "East Gwillimbury",
    "King",
    "Uxbridge",
    "Scugog",
    "Georgina",
]


def normalize_address(address: str, expand_abbreviations: bool = True) -> str:
    """
    Standardize address format for geocoding.

    - Expand common abbreviations (optional)
    - Add Ontario, Canada if no province specified
    - Remove extra whitespace
    - Standardize formatting

    Args:
        address: Raw address string
        expand_abbreviations: Whether to expand street/direction abbreviations

    Returns:
        Normalized address string
    """
    if not address:
        return ""

    result = address.strip()

    # Expand abbreviations if requested
    if expand_abbreviations:
        # Expand street type abbreviations (case-insensitive)
        for abbr, full in STREET_ABBREVIATIONS.items():
            result = re.sub(abbr, full, result, flags=re.IGNORECASE)

        # Expand direction abbreviations
        for abbr, full in DIRECTION_ABBREVIATIONS.items():
            result = re.sub(abbr, full, result, flags=re.IGNORECASE)

        # Expand unit abbreviations
        for abbr, full in UNIT_ABBREVIATIONS.items():
            result = re.sub(abbr, full, result, flags=re.IGNORECASE)

    # Add Ontario if no province specified
    if not re.search(r"\b(ON|Ontario)\b", result, re.IGNORECASE):
        # Check if it already ends with Canada
        if not re.search(r"\bCanada\b", result, re.IGNORECASE):
            result = f"{result}, Ontario, Canada"
        else:
            # Insert Ontario before Canada
            result = re.sub(
                r",?\s*Canada\s*$", ", Ontario, Canada", result, flags=re.IGNORECASE
            )
    elif not re.search(r"\bCanada\b", result, re.IGNORECASE):
        result = f"{result}, Canada"

    # Clean whitespace (multiple spaces to single)
    result = " ".join(result.split())

    # Normalize punctuation (no double commas, proper spacing after commas)
    result = re.sub(r",+", ",", result)
    result = re.sub(r",\s*", ", ", result)
    result = result.strip(", ")

    return result


def extract_municipality(address: str) -> Optional[str]:
    """
    Extract municipality name from address if present.

    Args:
        address: Address string

    Returns:
        Municipality name or None
    """
    address_lower = address.lower()

    for municipality in ONTARIO_MUNICIPALITIES:
        if municipality.lower() in address_lower:
            return municipality

    return None


def extract_postal_code(address: str) -> Optional[str]:
    """
    Extract Canadian postal code from address.

    Canadian postal code format: A1A 1A1 (letter-digit-letter space digit-letter-digit)

    Args:
        address: Address string

    Returns:
        Postal code or None
    """
    # Canadian postal code pattern
    pattern = r"[A-Za-z]\d[A-Za-z]\s*\d[A-Za-z]\d"
    match = re.search(pattern, address)

    if match:
        # Normalize format (uppercase, single space)
        code = match.group().upper()
        code = re.sub(r"\s+", "", code)
        return f"{code[:3]} {code[3:]}"

    return None


def standardize_address_components(address: str) -> dict:
    """
    Parse address into standardized components.

    Args:
        address: Full address string

    Returns:
        Dictionary with address components
    """
    components = {
        "street_number": None,
        "street_name": None,
        "unit": None,
        "municipality": None,
        "province": None,
        "postal_code": None,
        "country": None,
    }

    # Extract postal code
    components["postal_code"] = extract_postal_code(address)

    # Extract municipality
    components["municipality"] = extract_municipality(address)

    # Check for province
    if re.search(r"\b(ON|Ontario)\b", address, re.IGNORECASE):
        components["province"] = "Ontario"

    # Check for country
    if re.search(r"\bCanada\b", address, re.IGNORECASE):
        components["country"] = "Canada"

    # Extract street number (first numeric sequence)
    street_num_match = re.match(r"^(\d+[-\d]*)", address.strip())
    if street_num_match:
        components["street_number"] = street_num_match.group(1)

    # Extract unit number (e.g., Unit 5, Suite 200, #3)
    unit_match = re.search(
        r"(?:Unit|Suite|Apt|Apartment|#)\s*(\d+\w*)", address, re.IGNORECASE
    )
    if unit_match:
        components["unit"] = unit_match.group(1)

    return components
