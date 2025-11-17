"""
Input Validation Module
Validates JSON input structure and data integrity for income approach land valuation
"""

from typing import Dict, List, Optional, Any
import sys


def validate_input_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate input data structure and values.

    Args:
        data: Input dictionary with site_type, land_rent, market_data, operating_expenses

    Returns:
        Validated data dictionary

    Raises:
        ValueError: If validation fails
    """
    errors = []

    # Required top-level keys
    required_keys = ['site_type', 'land_rent', 'market_data', 'operating_expenses']
    for key in required_keys:
        if key not in data:
            errors.append(f"Missing required field: {key}")

    if errors:
        raise ValueError("Validation errors:\n" + "\n".join(f"  - {e}" for e in errors))

    # Validate land_rent
    errors.extend(_validate_land_rent(data['land_rent']))

    # Validate market_data
    errors.extend(_validate_market_data(data['market_data']))

    # Validate operating_expenses
    errors.extend(_validate_operating_expenses(data['operating_expenses']))

    if errors:
        raise ValueError("Validation errors:\n" + "\n".join(f"  - {e}" for e in errors))

    return data


def _validate_land_rent(land_rent: Dict[str, Any]) -> List[str]:
    """Validate land_rent section."""
    errors = []

    if 'annual_rent' not in land_rent:
        errors.append("land_rent.annual_rent is required")
    elif not isinstance(land_rent['annual_rent'], (int, float)):
        errors.append("land_rent.annual_rent must be a number")
    elif land_rent['annual_rent'] <= 0:
        errors.append("land_rent.annual_rent must be positive")

    if 'lease_term' not in land_rent:
        errors.append("land_rent.lease_term is required")
    elif not isinstance(land_rent['lease_term'], int):
        errors.append("land_rent.lease_term must be an integer")
    elif land_rent['lease_term'] <= 0:
        errors.append("land_rent.lease_term must be positive")

    return errors


def _validate_market_data(market_data: Dict[str, Any]) -> List[str]:
    """Validate market_data section."""
    errors = []

    # Validate comparable_rents
    if 'comparable_rents' not in market_data:
        errors.append("market_data.comparable_rents is required")
    elif not isinstance(market_data['comparable_rents'], list):
        errors.append("market_data.comparable_rents must be a list")
    elif len(market_data['comparable_rents']) == 0:
        errors.append("market_data.comparable_rents must contain at least one comparable")
    else:
        for idx, comp in enumerate(market_data['comparable_rents']):
            if 'annual_rent' not in comp:
                errors.append(f"comparable_rents[{idx}].annual_rent is required")
            elif not isinstance(comp['annual_rent'], (int, float)):
                errors.append(f"comparable_rents[{idx}].annual_rent must be a number")
            elif comp['annual_rent'] <= 0:
                errors.append(f"comparable_rents[{idx}].annual_rent must be positive")

    # Validate cap_rate_range
    if 'cap_rate_range' not in market_data:
        errors.append("market_data.cap_rate_range is required")
    else:
        cap_range = market_data['cap_rate_range']
        if 'low' not in cap_range:
            errors.append("market_data.cap_rate_range.low is required")
        elif not isinstance(cap_range['low'], (int, float)):
            errors.append("market_data.cap_rate_range.low must be a number")
        elif cap_range['low'] <= 0 or cap_range['low'] >= 1:
            errors.append("market_data.cap_rate_range.low must be between 0 and 1")

        if 'high' not in cap_range:
            errors.append("market_data.cap_rate_range.high is required")
        elif not isinstance(cap_range['high'], (int, float)):
            errors.append("market_data.cap_rate_range.high must be a number")
        elif cap_range['high'] <= 0 or cap_range['high'] >= 1:
            errors.append("market_data.cap_rate_range.high must be between 0 and 1")

        if 'low' in cap_range and 'high' in cap_range:
            if cap_range['low'] >= cap_range['high']:
                errors.append("market_data.cap_rate_range.low must be less than high")

    # Validate comparable_sales
    if 'comparable_sales' not in market_data:
        errors.append("market_data.comparable_sales is required")
    elif not isinstance(market_data['comparable_sales'], list):
        errors.append("market_data.comparable_sales must be a list")
    elif len(market_data['comparable_sales']) == 0:
        errors.append("market_data.comparable_sales must contain at least one sale")
    else:
        for idx, sale in enumerate(market_data['comparable_sales']):
            if 'sale_price' not in sale:
                errors.append(f"comparable_sales[{idx}].sale_price is required")
            elif not isinstance(sale['sale_price'], (int, float)):
                errors.append(f"comparable_sales[{idx}].sale_price must be a number")
            elif sale['sale_price'] <= 0:
                errors.append(f"comparable_sales[{idx}].sale_price must be positive")

            if 'noi' not in sale:
                errors.append(f"comparable_sales[{idx}].noi is required")
            elif not isinstance(sale['noi'], (int, float)):
                errors.append(f"comparable_sales[{idx}].noi must be a number")
            elif sale['noi'] <= 0:
                errors.append(f"comparable_sales[{idx}].noi must be positive")

    return errors


def _validate_operating_expenses(operating_expenses: Dict[str, Any]) -> List[str]:
    """Validate operating_expenses section."""
    errors = []

    required_expenses = ['property_tax', 'insurance', 'maintenance']
    for expense in required_expenses:
        if expense not in operating_expenses:
            errors.append(f"operating_expenses.{expense} is required")
        elif not isinstance(operating_expenses[expense], (int, float)):
            errors.append(f"operating_expenses.{expense} must be a number")
        elif operating_expenses[expense] < 0:
            errors.append(f"operating_expenses.{expense} must be non-negative")

    return errors
