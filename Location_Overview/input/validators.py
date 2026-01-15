"""
Input Validators Module

Validation rules for PINs, addresses, and coordinates.
"""

import re
from typing import Tuple, List, Optional
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of a validation check."""

    is_valid: bool
    errors: List[str]
    warnings: List[str]


def validate_coordinates(lat: float, lon: float) -> ValidationResult:
    """
    Validate geographic coordinates for Ontario.

    Ontario boundaries (approximate):
    - Latitude: 41.6° to 56.9° N
    - Longitude: -95.2° to -74.3° W

    Args:
        lat: Latitude
        lon: Longitude

    Returns:
        ValidationResult with validity and any errors/warnings
    """
    errors = []
    warnings = []

    # Check basic coordinate validity
    if not (-90 <= lat <= 90):
        errors.append(f"Invalid latitude {lat}: must be between -90 and 90")
    if not (-180 <= lon <= 180):
        errors.append(f"Invalid longitude {lon}: must be between -180 and 180")

    if errors:
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

    # Check if within Ontario bounds (rough)
    ONTARIO_LAT_MIN = 41.6
    ONTARIO_LAT_MAX = 56.9
    ONTARIO_LON_MIN = -95.2
    ONTARIO_LON_MAX = -74.3

    if not (ONTARIO_LAT_MIN <= lat <= ONTARIO_LAT_MAX):
        errors.append(
            f"Latitude {lat} is outside Ontario bounds ({ONTARIO_LAT_MIN} to {ONTARIO_LAT_MAX})"
        )
    if not (ONTARIO_LON_MIN <= lon <= ONTARIO_LON_MAX):
        errors.append(
            f"Longitude {lon} is outside Ontario bounds ({ONTARIO_LON_MIN} to {ONTARIO_LON_MAX})"
        )

    # Southern Ontario (most common) vs Northern Ontario warning
    if lat > 50.0:
        warnings.append(
            "Location is in Northern Ontario - some data sources may have limited coverage"
        )

    return ValidationResult(
        is_valid=len(errors) == 0, errors=errors, warnings=warnings
    )


def validate_address_format(address: str) -> ValidationResult:
    """
    Validate address format for geocoding.

    Args:
        address: Address string

    Returns:
        ValidationResult
    """
    errors = []
    warnings = []

    if not address or not address.strip():
        errors.append("Address cannot be empty")
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

    address = address.strip()

    # Check minimum length
    if len(address) < 5:
        errors.append("Address is too short - must be at least 5 characters")

    # Check for at least one number (street number)
    if not re.search(r"\d", address):
        warnings.append(
            "Address has no street number - geocoding accuracy may be reduced"
        )

    # Check for potential PO Box (not geocodable to a specific location)
    if re.search(r"\b(P\.?O\.?\s*Box|PO\s*Box)\b", address, re.IGNORECASE):
        warnings.append("PO Box addresses cannot be geocoded to a specific location")

    # Check for potentially incomplete address
    if not re.search(r"[,\s](ON|Ontario)\b", address, re.IGNORECASE):
        warnings.append("No province specified - 'Ontario, Canada' will be appended")

    # Check for ambiguous street names
    common_streets = ["Main", "King", "Queen", "Front", "Yonge", "Dundas"]
    for street in common_streets:
        if re.search(rf"\b{street}\s+(St|Street|Ave|Avenue)\b", address, re.IGNORECASE):
            if not re.search(
                r"\b(Toronto|Mississauga|Ottawa|Hamilton|London|Brampton)\b",
                address,
                re.IGNORECASE,
            ):
                warnings.append(
                    f"'{street}' is a common street name in multiple cities - specify municipality for accuracy"
                )
                break

    return ValidationResult(
        is_valid=len(errors) == 0, errors=errors, warnings=warnings
    )


def validate_pin_format(pin: str) -> ValidationResult:
    """
    Validate Ontario PIN format.

    Args:
        pin: PIN string (should be 9 digits)

    Returns:
        ValidationResult
    """
    errors = []
    warnings = []

    if not pin:
        errors.append("PIN cannot be empty")
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

    # Remove separators for validation
    cleaned = re.sub(r"[-\s]", "", pin)

    # Check for 9 digits
    if not re.match(r"^\d{9}$", cleaned):
        if re.match(r"^\d+$", cleaned):
            errors.append(f"PIN must be exactly 9 digits, got {len(cleaned)}")
        else:
            errors.append("PIN must contain only digits (and optional dashes/spaces)")
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

    # Check block number (first 5 digits)
    block = int(cleaned[:5])
    if block == 0:
        errors.append("Block number (first 5 digits) cannot be 00000")

    # Property number (last 4 digits) - 0000 is valid (unassigned)
    property_num = int(cleaned[5:])
    if property_num == 0:
        warnings.append(
            "Property number is 0000 - this may be an unassigned or special PIN"
        )

    return ValidationResult(
        is_valid=len(errors) == 0, errors=errors, warnings=warnings
    )


def validate_input(
    input_str: str, input_type: Optional[str] = None
) -> ValidationResult:
    """
    General input validation dispatcher.

    Args:
        input_str: User input string
        input_type: Optional type hint ("pin", "address")

    Returns:
        ValidationResult
    """
    if not input_str or not input_str.strip():
        return ValidationResult(
            is_valid=False, errors=["Input cannot be empty"], warnings=[]
        )

    # Auto-detect type if not specified
    if input_type is None:
        cleaned = re.sub(r"[-\s]", "", input_str.strip())
        if re.match(r"^\d{9}$", cleaned):
            input_type = "pin"
        else:
            input_type = "address"

    if input_type == "pin":
        return validate_pin_format(input_str)
    else:
        return validate_address_format(input_str)
