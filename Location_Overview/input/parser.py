"""
Input Parser Module

Detects whether input is an Ontario PIN (Property Identification Number) or a municipal address.
PIN format: 9 consecutive digits (with or without dashes/spaces)
Examples: 123456789, 12345-6789, 12345 6789
"""

import re
from enum import Enum
from typing import Tuple
from dataclasses import dataclass


class InputType(Enum):
    """Type of input provided to the location overview command."""

    PIN = "pin"
    ADDRESS = "address"
    UNKNOWN = "unknown"


@dataclass
class ParsedInput:
    """Result of parsing user input."""

    input_type: InputType
    value: str
    original: str
    is_valid: bool
    validation_message: str = ""


def detect_input_type(input_str: str) -> Tuple[InputType, str]:
    """
    Detect whether input is a PIN or address.

    PIN format: 9 consecutive digits (with or without dashes/spaces)
    Examples: 123456789, 12345-6789, 12345 6789

    Args:
        input_str: Raw user input string

    Returns:
        Tuple of (InputType, cleaned_value)
    """
    if not input_str or not input_str.strip():
        return InputType.UNKNOWN, ""

    # Normalize: remove common separators
    cleaned = re.sub(r"[-\s]", "", input_str.strip())

    # Check for 9-digit PIN
    if re.match(r"^\d{9}$", cleaned):
        return InputType.PIN, cleaned

    # Check for partial PIN (5+4 format like 12345-6789)
    if re.match(r"^\d{5}[-\s]?\d{4}$", input_str.strip()):
        return InputType.PIN, cleaned

    # Otherwise, treat as address
    return InputType.ADDRESS, input_str.strip()


def validate_pin(pin: str) -> Tuple[bool, str]:
    """
    Validate PIN format.

    Ontario PINs:
    - 9 digits total
    - First 5 digits: Block number (must be >= 1)
    - Last 4 digits: Property number within block

    Args:
        pin: 9-digit PIN string

    Returns:
        Tuple of (is_valid, validation_message)
    """
    if not pin:
        return False, "PIN cannot be empty"

    # Remove any separators
    cleaned = re.sub(r"[-\s]", "", pin)

    if not re.match(r"^\d{9}$", cleaned):
        return False, f"PIN must be exactly 9 digits, got {len(cleaned)} characters"

    # Block number (first 5 digits) should be valid
    block = int(cleaned[:5])
    if block < 1:
        return False, "Block number (first 5 digits) must be at least 00001"

    # Property number (last 4 digits) - can be 0000 to 9999
    # No specific validation needed

    return True, "Valid Ontario PIN format"


def parse_input(input_str: str) -> ParsedInput:
    """
    Parse and validate user input.

    Args:
        input_str: Raw user input

    Returns:
        ParsedInput with type, value, and validation status
    """
    if not input_str or not input_str.strip():
        return ParsedInput(
            input_type=InputType.UNKNOWN,
            value="",
            original=input_str or "",
            is_valid=False,
            validation_message="Input cannot be empty",
        )

    input_type, cleaned = detect_input_type(input_str)

    if input_type == InputType.PIN:
        is_valid, message = validate_pin(cleaned)
        return ParsedInput(
            input_type=input_type,
            value=cleaned,
            original=input_str,
            is_valid=is_valid,
            validation_message=message,
        )

    if input_type == InputType.ADDRESS:
        # Basic address validation
        is_valid = len(cleaned) >= 5  # Minimum reasonable address length
        message = "Valid address format" if is_valid else "Address too short"
        return ParsedInput(
            input_type=input_type,
            value=cleaned,
            original=input_str,
            is_valid=is_valid,
            validation_message=message,
        )

    return ParsedInput(
        input_type=InputType.UNKNOWN,
        value=cleaned,
        original=input_str,
        is_valid=False,
        validation_message="Could not determine input type",
    )


def format_pin(pin: str) -> str:
    """
    Format a PIN with standard separator (XXXXX-XXXX).

    Args:
        pin: 9-digit PIN string

    Returns:
        Formatted PIN string
    """
    cleaned = re.sub(r"[-\s]", "", pin)
    if len(cleaned) != 9:
        return pin  # Return original if not valid
    return f"{cleaned[:5]}-{cleaned[5:]}"
