"""
Input Validation Utilities for Comparable Sales Adjustment Modules

Provides standardized validation for property data inputs to prevent
runtime errors and ensure data quality in adjustment calculations.

CUSPAP 2024 Compliant - Rule 6.2.15 (data analysis requirements)
"""

import logging
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger(__name__)


class ValidationResult:
    """Result of input validation with warnings and errors."""

    def __init__(self):
        self.is_valid: bool = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.missing_fields: List[str] = []
        self.invalid_values: Dict[str, Any] = {}

    def add_error(self, message: str):
        """Add an error (makes validation fail)."""
        self.is_valid = False
        self.errors.append(message)

    def add_warning(self, message: str):
        """Add a warning (validation still passes)."""
        self.warnings.append(message)

    def add_missing_field(self, field: str):
        """Track missing field for disclosure."""
        self.missing_fields.append(field)

    def add_invalid_value(self, field: str, value: Any):
        """Track invalid value for disclosure."""
        self.invalid_values[field] = value

    def __bool__(self) -> bool:
        return self.is_valid


def safe_get_numeric(data: Dict, key: str, default: float = 0.0) -> float:
    """
    Safely extract numeric value from dictionary.

    Args:
        data: Source dictionary
        key: Key to extract
        default: Default value if key missing or invalid

    Returns:
        Numeric value or default
    """
    value = data.get(key, default)
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        logger.warning(f"Invalid numeric value for {key}: {value}, using default {default}")
        return default


def safe_get_positive(data: Dict, key: str, default: float = 0.0) -> float:
    """
    Safely extract positive numeric value (returns 0 if negative).

    Args:
        data: Source dictionary
        key: Key to extract
        default: Default value if key missing or invalid

    Returns:
        Non-negative numeric value
    """
    value = safe_get_numeric(data, key, default)
    return max(0.0, value)


def safe_get_string(data: Dict, key: str, default: str = '') -> str:
    """
    Safely extract string value from dictionary.

    Args:
        data: Source dictionary
        key: Key to extract
        default: Default value if key missing

    Returns:
        String value or default
    """
    value = data.get(key, default)
    if value is None:
        return default
    return str(value)


def safe_get_bool(data: Dict, key: str, default: bool = False) -> bool:
    """
    Safely extract boolean value from dictionary.

    Args:
        data: Source dictionary
        key: Key to extract
        default: Default value if key missing

    Returns:
        Boolean value or default
    """
    value = data.get(key, default)
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', 'yes', '1', 'y')
    return bool(value)


def validate_property_data(
    data: Dict,
    required_fields: List[str],
    property_label: str = 'property'
) -> ValidationResult:
    """
    Validate property data has required fields.

    Args:
        data: Property data dictionary
        required_fields: List of required field names
        property_label: Label for error messages

    Returns:
        ValidationResult with errors and warnings
    """
    result = ValidationResult()

    if not data:
        result.add_error(f"{property_label} data is empty or None")
        return result

    for field in required_fields:
        if field not in data or data[field] is None:
            result.add_missing_field(field)
            result.add_warning(f"Missing {field} for {property_label}")

    return result


def validate_adjustment_inputs(
    subject: Dict,
    comparable: Dict,
    base_price: float,
    market_params: Dict
) -> Tuple[bool, List[str]]:
    """
    Validate standard adjustment function inputs.

    Args:
        subject: Subject property dictionary
        comparable: Comparable sale dictionary
        base_price: Base price for adjustments
        market_params: Market parameters dictionary

    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []

    if not subject:
        errors.append("Subject property data is required")

    if not comparable:
        errors.append("Comparable property data is required")

    if base_price is None or base_price <= 0:
        errors.append(f"Invalid base_price: {base_price}")

    if market_params is None:
        errors.append("Market parameters are required (can be empty dict)")

    return len(errors) == 0, errors


def validate_comparable_for_adjustment(
    subject: Dict,
    comparable: Dict,
    characteristic: str
) -> Tuple[bool, str]:
    """
    Check if comparable has sufficient data for a specific adjustment.

    Args:
        subject: Subject property
        comparable: Comparable property
        characteristic: The characteristic being adjusted

    Returns:
        Tuple of (can_adjust, reason if not)
    """
    # Define required fields per characteristic
    required_fields = {
        'size': ['size_sf', 'building_sf'],
        'lot_size': ['lot_size_acres'],
        'clear_height': ['clear_height_feet'],
        'loading_docks': ['loading_docks_dock_high', 'loading_docks_grade_level'],
        'condition': ['condition'],
        'age': ['year_built', 'effective_age_years'],
        'parking': ['parking_spaces_per_1000sf', 'parking_ratio'],
        'building_class': ['building_class'],
    }

    fields_to_check = required_fields.get(characteristic, [])

    for field in fields_to_check:
        subject_has = subject.get(field) is not None
        comp_has = comparable.get(field) is not None

        if subject_has or comp_has:
            return True, ""

    if fields_to_check:
        return False, f"Neither property has {characteristic} data ({fields_to_check})"

    return True, ""  # Unknown characteristic - assume ok


def clamp_adjustment_percent(
    value: float,
    min_pct: float = -50.0,
    max_pct: float = 50.0,
    characteristic: str = 'adjustment'
) -> Tuple[float, Optional[str]]:
    """
    Clamp adjustment percentage to reasonable bounds.

    Args:
        value: Adjustment percentage
        min_pct: Minimum allowed percentage
        max_pct: Maximum allowed percentage
        characteristic: Name for logging

    Returns:
        Tuple of (clamped_value, warning_message or None)
    """
    if value < min_pct:
        warning = f"{characteristic} clamped from {value:.1f}% to {min_pct:.1f}%"
        logger.warning(warning)
        return min_pct, warning

    if value > max_pct:
        warning = f"{characteristic} clamped from {value:.1f}% to {max_pct:.1f}%"
        logger.warning(warning)
        return max_pct, warning

    return value, None


def clamp_adjustment_amount(
    value: float,
    base_price: float,
    max_pct_of_base: float = 50.0,
    characteristic: str = 'adjustment'
) -> Tuple[float, Optional[str]]:
    """
    Clamp adjustment amount to reasonable bounds (as % of base price).

    Args:
        value: Adjustment amount in dollars
        base_price: Base price for percentage calculation
        max_pct_of_base: Maximum allowed as % of base price
        characteristic: Name for logging

    Returns:
        Tuple of (clamped_value, warning_message or None)
    """
    if base_price <= 0:
        return value, None

    max_amount = base_price * (max_pct_of_base / 100)
    min_amount = -max_amount

    if value < min_amount:
        warning = f"{characteristic} clamped from ${value:,.0f} to ${min_amount:,.0f}"
        logger.warning(warning)
        return min_amount, warning

    if value > max_amount:
        warning = f"{characteristic} clamped from ${value:,.0f} to ${max_amount:,.0f}"
        logger.warning(warning)
        return max_amount, warning

    return value, None
