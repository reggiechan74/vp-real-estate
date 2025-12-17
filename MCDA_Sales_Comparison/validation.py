#!/usr/bin/env python3
"""
Validation Module for MCDA Sales Comparison

Provides sales-specific validation functions:
- Sale price validation (PSF ranges by property type)
- Transaction validation (property rights, financing, conditions of sale)
- Cash equivalent adjustments
- Time/market condition adjustments
- Monotonicity validation for score-to-price mapping
- Input data schema validation (JSON Schema Draft 2020-12)

Author: Claude Code
Version: 1.1.0
Date: 2025-12-17
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

# JSON Schema validation (optional - graceful degradation if not installed)
try:
    from jsonschema import validate, ValidationError, Draft202012Validator
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False

# Shared schema location (unified schema for both DCA and MCDA calculators)
SHARED_SCHEMA_PATH = Path(__file__).parent.parent / "Shared_Utils" / "schemas" / "comparable_sales_input_schema.json"


# =============================================================================
# PROPERTY TYPE CONFIGURATION
# =============================================================================

# Typical PSF ranges by property type (CAD)
PRICE_PSF_RANGES = {
    'industrial': {'min': 20, 'max': 500},
    'office': {'min': 50, 'max': 1000},
    'retail': {'min': 100, 'max': 1500}
}


# =============================================================================
# SALE PRICE VALIDATION
# =============================================================================

def validate_sale_price(comparable: Dict[str, Any]) -> List[str]:
    """
    Validate sale price is within typical range for property type.

    Args:
        comparable: Dictionary with sale_price, building_sf, and optionally property_type

    Returns:
        List of warning/error messages (empty if valid)
    """
    errors = []

    sale_price = comparable.get('sale_price', 0)
    building_sf = comparable.get('building_sf', 0)
    property_type = comparable.get('property_type', 'industrial').lower()

    if building_sf <= 0:
        errors.append("Building SF must be greater than 0")
        return errors

    if sale_price <= 0:
        errors.append("Sale price must be greater than 0")
        return errors

    price_psf = sale_price / building_sf

    # Get range for property type (default to industrial if unknown)
    ranges = PRICE_PSF_RANGES.get(property_type, PRICE_PSF_RANGES['industrial'])

    if price_psf < ranges['min'] or price_psf > ranges['max']:
        errors.append(
            f"Sale price ${price_psf:.2f}/SF outside typical range "
            f"(${ranges['min']}-${ranges['max']}/SF for {property_type})"
        )

    return errors


# =============================================================================
# TRANSACTION VALIDATION
# =============================================================================

def validate_transaction(comparable: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """
    Validate transaction details for Stage 1-3 adjustments.

    Checks:
    - Property rights (fee simple, leased fee, leasehold)
    - Financing (cash, conventional, seller VTB)
    - Conditions of sale (arm's length)

    Args:
        comparable: Dictionary with transaction details

    Returns:
        Tuple of (errors, warnings)
        - Errors: Issues that should exclude the comparable
        - Warnings: Issues that may require adjustment
    """
    errors = []
    warnings = []

    # Property rights check
    property_rights = comparable.get('property_rights', 'fee_simple')
    if property_rights != 'fee_simple':
        warnings.append(f"Non-fee simple interest: {property_rights}")

    # Financing check
    financing = comparable.get('financing', {})
    financing_type = financing.get('type', 'cash') if isinstance(financing, dict) else 'cash'

    if financing_type == 'seller_vtb':
        warnings.append("Seller financing may require cash equivalent adjustment")
    elif financing_type not in ('cash', 'conventional'):
        warnings.append(f"Non-standard financing: {financing_type}")

    # Conditions of sale check
    conditions = comparable.get('conditions_of_sale', {})
    arms_length = conditions.get('arms_length', True) if isinstance(conditions, dict) else True

    if not arms_length:
        errors.append("Non-arm's length sale - exclude from analysis")

    return errors, warnings


# =============================================================================
# CASH EQUIVALENT ADJUSTMENT
# =============================================================================

def compute_cash_equivalent(comparable: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return cash-equivalent price if financing is non-market.

    Applies percentage adjustment to sale price to normalize to cash terms.

    Args:
        comparable: Dictionary with sale_price and optional cash_equivalent_adjustment_pct

    Returns:
        Dictionary with:
        - cash_equivalent_price: Adjusted price
        - adjustment_pct: Percentage applied
        - note: Explanation of adjustment
    """
    sale_price = comparable.get('sale_price', 0)
    adjustment_pct = comparable.get('cash_equivalent_adjustment_pct')

    # Handle missing or None adjustment
    if adjustment_pct is None:
        adjustment_pct = 0

    # Calculate adjusted price
    adjusted_price = sale_price * (1 + adjustment_pct / 100)

    return {
        'cash_equivalent_price': adjusted_price,
        'adjustment_pct': adjustment_pct,
        'note': "Adjusted for non-market financing" if adjustment_pct != 0 else "No adjustment applied"
    }


# =============================================================================
# TIME ADJUSTMENT
# =============================================================================

def validate_time_adjustment(comparable: Dict[str, Any], valuation_date: str) -> Dict[str, Any]:
    """
    Calculate time adjustment if needed.

    Time adjustments account for market conditions changes between sale date
    and valuation date. Typically applied when difference > 3 months.

    Args:
        comparable: Dictionary with sale_date
        valuation_date: Target valuation date (YYYY-MM-DD)

    Returns:
        Dictionary with:
        - months_difference: Number of months between sale and valuation
        - requires_time_adjustment: True if adjustment needed (>3 months)
        - suggested_adjustment_pct: Suggested adjustment (approx 3.5%/year)
    """
    try:
        sale_date = datetime.strptime(comparable['sale_date'], '%Y-%m-%d')
        val_date = datetime.strptime(valuation_date, '%Y-%m-%d')
    except (KeyError, ValueError) as e:
        return {
            'months_difference': 0,
            'requires_time_adjustment': False,
            'suggested_adjustment_pct': 0,
            'error': str(e)
        }

    # Calculate months difference (positive = sale before valuation)
    days_diff = (val_date - sale_date).days
    months_diff = days_diff / 30.44  # Average days per month

    # Determine if adjustment needed (threshold: 3 months)
    requires_adjustment = abs(months_diff) > 3

    # Calculate suggested adjustment (approx 3.5%/year = 0.3%/month)
    if requires_adjustment:
        suggested_pct = months_diff * 0.3
    else:
        suggested_pct = 0

    return {
        'months_difference': months_diff,
        'requires_time_adjustment': requires_adjustment,
        'suggested_adjustment_pct': suggested_pct
    }


# =============================================================================
# MONOTONICITY VALIDATION
# =============================================================================

def validate_monotonicity(scores_prices: List[Tuple[float, float]]) -> Dict[str, Any]:
    """
    Check monotonic decreasing relationship (better score -> higher price).

    In MCDA, lower composite score = better property = higher price.
    Violations indicate the model may not fit well, suggesting need
    for monotonic regression or alternative fitting method.

    Args:
        scores_prices: List of (score, price) tuples, sorted by score ascending

    Returns:
        Dictionary with:
        - violations: Count of monotonicity violations
        - requires_monotone_fit: True if violations detected
    """
    if len(scores_prices) < 2:
        return {'violations': 0, 'requires_monotone_fit': False}

    # Sort by score ascending
    sorted_data = sorted(scores_prices, key=lambda x: x[0])

    violations = 0
    for i in range(1, len(sorted_data)):
        current_score, current_price = sorted_data[i]
        prev_score, prev_price = sorted_data[i - 1]

        # If score increased (worse property) but price also increased, that's a violation
        # Expected: higher score -> lower price
        if current_score > prev_score and current_price > prev_price:
            violations += 1

    return {
        'violations': violations,
        'requires_monotone_fit': violations > 0
    }


# =============================================================================
# JSON SCHEMA VALIDATION
# =============================================================================

def load_unified_schema(schema_path: Path = None) -> Optional[Dict]:
    """
    Load the unified JSON schema for comparable sales input.

    Args:
        schema_path: Custom schema path (defaults to shared location)

    Returns:
        Schema dictionary, or None if not available
    """
    path = schema_path or SHARED_SCHEMA_PATH

    if not path.exists():
        return None

    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def validate_against_schema(
    data: Dict[str, Any],
    schema_path: Path = None,
    strict: bool = False
) -> Tuple[bool, List[str]]:
    """
    Validate input data against the unified JSON schema.

    Uses the shared schema that is compatible with both Traditional DCA
    (Comparable_Sales_Analysis) and MCDA (MCDA_Sales_Comparison) calculators.

    Args:
        data: Input data dictionary to validate
        schema_path: Custom schema path (defaults to shared location)
        strict: If True, raise exception on schema errors; if False, return errors

    Returns:
        Tuple of (is_valid, error_messages)
        - is_valid: True if data passes schema validation
        - error_messages: List of validation error descriptions
    """
    errors = []

    # Check if jsonschema is available
    if not JSONSCHEMA_AVAILABLE:
        errors.append("WARNING: jsonschema library not installed - skipping schema validation")
        return True, errors  # Graceful degradation - don't block on missing dependency

    # Load schema
    schema = load_unified_schema(schema_path)
    if schema is None:
        path = schema_path or SHARED_SCHEMA_PATH
        errors.append(f"WARNING: Schema file not found at {path} - skipping schema validation")
        return True, errors  # Graceful degradation

    # Validate
    try:
        validate(instance=data, schema=schema)
        return True, []
    except ValidationError as e:
        # Extract meaningful error message
        error_path = " -> ".join(str(p) for p in e.absolute_path) if e.absolute_path else "root"
        error_msg = f"Schema validation failed at '{error_path}': {e.message}"
        errors.append(error_msg)

        if strict:
            raise

        return False, errors


# =============================================================================
# INPUT DATA VALIDATION
# =============================================================================

def validate_input_data(data: Dict[str, Any], use_schema: bool = True) -> List[str]:
    """
    Validate complete input data structure.

    Performs two levels of validation:
    1. JSON Schema validation (if use_schema=True and jsonschema available)
    2. Semantic validation for MCDA-specific requirements

    Required fields:
    - analysis_date (root level, or defaults to today)
    - valuation_date (root level OR in market_parameters)
    - subject_property (with address, building_sf)
    - comparable_sales (minimum 3)

    Supports unified schema for both Traditional DCA and MCDA calculators.

    Args:
        data: Input data dictionary
        use_schema: If True, run JSON Schema validation first (default: True)

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    # 1. JSON Schema validation (optional, graceful degradation)
    if use_schema:
        schema_valid, schema_errors = validate_against_schema(data, strict=False)
        # Only add schema errors that are actual errors (not warnings)
        for err in schema_errors:
            if not err.startswith("WARNING:"):
                errors.append(err)

    # 2. Semantic validation (MCDA-specific requirements)
    # Check for required structural fields
    if 'subject_property' not in data:
        errors.append("Missing required field: subject_property")
    if 'comparable_sales' not in data:
        errors.append("Missing required field: comparable_sales")

    # Flexible date handling for unified schema compatibility
    # valuation_date: Accept from root OR market_parameters
    valuation_date = data.get('valuation_date')
    if not valuation_date:
        market_params = data.get('market_parameters', {})
        valuation_date = market_params.get('valuation_date')

    if not valuation_date:
        errors.append("Missing required field: valuation_date (provide at root or in market_parameters)")

    # analysis_date: Accept from root OR default to today (no error)
    # This allows DCA-style inputs that don't have analysis_date

    if errors:
        return errors

    # Validate subject property
    subject = data.get('subject_property', {})
    if not subject.get('address'):
        errors.append("Subject property must have an address")
    if not subject.get('building_sf') or subject.get('building_sf', 0) <= 0:
        errors.append("Subject property must have valid building_sf > 0")

    # Validate comparable sales
    comparables = data.get('comparable_sales', [])
    if len(comparables) < 3:
        errors.append(f"Minimum 3 comparable sales required, got {len(comparables)}")

    # Validate each comparable
    for i, comp in enumerate(comparables):
        comp_errors = []

        if not comp.get('address'):
            comp_errors.append("missing address")
        if not comp.get('sale_price') or comp.get('sale_price', 0) <= 0:
            comp_errors.append("missing or invalid sale_price")
        if not comp.get('sale_date'):
            comp_errors.append("missing sale_date")
        if not comp.get('building_sf') or comp.get('building_sf', 0) <= 0:
            comp_errors.append("missing or invalid building_sf")

        if comp_errors:
            errors.append(f"Comparable {i + 1}: {', '.join(comp_errors)}")

    return errors


# =============================================================================
# COMPREHENSIVE VALIDATION
# =============================================================================

def validate_all_comparables(
    comparables: List[Dict[str, Any]],
    valuation_date: str,
    property_type: str = 'industrial'
) -> Dict[str, Any]:
    """
    Run all validations on comparable set.

    Args:
        comparables: List of comparable sale dictionaries
        valuation_date: Target valuation date
        property_type: Property type for PSF range validation

    Returns:
        Dictionary with:
        - valid_comparables: List of comparables passing validation
        - excluded_comparables: List of excluded comparables with reasons
        - warnings: Aggregate list of warnings
        - summary: Validation summary statistics
    """
    valid_comps = []
    excluded_comps = []
    all_warnings = []

    for comp in comparables:
        comp_copy = comp.copy()
        comp_copy['property_type'] = property_type

        # Validate sale price
        price_errors = validate_sale_price(comp_copy)

        # Validate transaction
        trans_errors, trans_warnings = validate_transaction(comp)

        # Check time adjustment
        time_info = validate_time_adjustment(comp, valuation_date)

        # Aggregate warnings
        comp_warnings = price_errors + trans_warnings
        if time_info.get('requires_time_adjustment'):
            comp_warnings.append(
                f"Time adjustment recommended: {time_info['months_difference']:.1f} months "
                f"(~{time_info['suggested_adjustment_pct']:.1f}%)"
            )

        # Determine if excluded
        if trans_errors:
            excluded_comps.append({
                'comparable': comp,
                'reasons': trans_errors
            })
        else:
            valid_comps.append(comp)
            all_warnings.extend([f"{comp.get('address', 'Unknown')}: {w}" for w in comp_warnings])

    return {
        'valid_comparables': valid_comps,
        'excluded_comparables': excluded_comps,
        'warnings': all_warnings,
        'summary': {
            'total_submitted': len(comparables),
            'valid_count': len(valid_comps),
            'excluded_count': len(excluded_comps),
            'warnings_count': len(all_warnings)
        }
    }


if __name__ == '__main__':
    # Quick self-test
    print("MCDA Sales Comparison - Validation Module")
    print("Run with pytest for full test suite")

    # Example validation
    test_comp = {
        'sale_price': 4650000,
        'building_sf': 48500,
        'property_type': 'industrial',
        'property_rights': 'fee_simple',
        'financing': {'type': 'cash'},
        'conditions_of_sale': {'arms_length': True},
        'sale_date': '2024-09-15'
    }

    print(f"\nTest comparable PSF: ${test_comp['sale_price'] / test_comp['building_sf']:.2f}")
    print(f"Price validation: {validate_sale_price(test_comp)}")
    print(f"Transaction validation: {validate_transaction(test_comp)}")
    print(f"Time adjustment: {validate_time_adjustment(test_comp, '2025-01-15')}")
