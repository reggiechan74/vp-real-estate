"""
Parameter Name Mapping for Comparable Sales Adjustments

This module resolves the naming mismatch between:
1. PairedSalesAnalyzer output (derived factor names)
2. Adjustment module inputs (market_params keys)

CUSPAP Compliance: Ensures derived market evidence is correctly applied.

The Problem:
- PairedSalesAnalyzer derives factors with names like 'clear_height_per_foot_per_sf'
- Adjustment modules expect parameters like 'clear_height_value_per_foot_per_sf'
- Without mapping, derived factors are silently ignored and defaults used instead

Author: Claude Code
Created: 2025-12-16
"""

from typing import Dict, Any, Optional, Tuple, List
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# CANONICAL MAPPING: Derived Name -> Module Parameter Name
# ============================================================================
# Left side: Names from PairedSalesAnalyzer.get_adjustment_factors()['factors']
# Right side: Names expected by adjustment modules (market_params keys)

DERIVED_TO_MODULE = {
    # -------------------------------------------------------------------------
    # Time/Market Conditions
    # -------------------------------------------------------------------------
    'appreciation_rate_annual_pct': 'appreciation_rate_annual',

    # -------------------------------------------------------------------------
    # Size Adjustments
    # -------------------------------------------------------------------------
    'size_adjustment_pct_per_10000sf': 'size_adjustment_pct_per_10000sf',

    # -------------------------------------------------------------------------
    # Location
    # -------------------------------------------------------------------------
    'highway_frontage_premium_pct': 'highway_frontage_premium_pct',

    # -------------------------------------------------------------------------
    # Condition/Age
    # -------------------------------------------------------------------------
    'condition_per_level_pct': 'condition_adjustment_pct_per_level',
    'age_depreciation_pct_per_year': 'annual_depreciation_pct',

    # -------------------------------------------------------------------------
    # Industrial Building
    # -------------------------------------------------------------------------
    'clear_height_per_foot_per_sf': 'clear_height_value_per_foot_per_sf',
    'loading_dock_value': 'loading_dock_value_per_dock',
    'rail_spur_premium': 'rail_spur_premium',

    # -------------------------------------------------------------------------
    # Office Building
    # -------------------------------------------------------------------------
    'building_class_per_level_pct': 'building_class_adjustment_pct_per_level',
}

# Reverse mapping for validation and debugging
MODULE_TO_DERIVED = {v: k for k, v in DERIVED_TO_MODULE.items()}


def map_derived_factors_to_module_params(
    derived_factors: Dict[str, Any],
    log_mappings: bool = True
) -> Dict[str, Any]:
    """
    Convert derived factor dictionary to module-compatible market_params.

    Args:
        derived_factors: Output from PairedSalesAnalyzer.get_adjustment_factors()['factors']
        log_mappings: If True, log each successful mapping

    Returns:
        Dictionary with module-compatible parameter names and values

    Example:
        derived = {'clear_height_per_foot_per_sf': {'value': 5.59, 'confidence': 'medium'}}
        mapped = map_derived_factors_to_module_params(derived)
        # Returns: {'clear_height_value_per_foot_per_sf': 5.59}
    """
    mapped_params = {}
    unmapped = []
    mapped_count = 0

    for derived_name, factor_info in derived_factors.items():
        # Handle submarket_differentials specially - pass through unchanged
        if derived_name == 'submarket_differentials':
            if isinstance(factor_info, dict):
                mapped_params['submarket_differentials'] = factor_info.get('values', factor_info)
            else:
                mapped_params['submarket_differentials'] = factor_info
            if log_mappings:
                logger.info(f"Passed through submarket_differentials")
            continue

        # Check if we have a mapping for this derived name
        if derived_name not in DERIVED_TO_MODULE:
            unmapped.append(derived_name)
            continue

        module_name = DERIVED_TO_MODULE[derived_name]

        # Extract the value from factor_info
        # Priority: 'value' > 'reconciled' > 'mean' > direct value
        if isinstance(factor_info, dict):
            value = (factor_info.get('value') or
                     factor_info.get('reconciled') or
                     factor_info.get('mean'))
            confidence = factor_info.get('confidence', 'unknown')
            market_supported = factor_info.get('market_supported', True)
        else:
            # Direct value (not wrapped in dict)
            value = factor_info
            confidence = 'unknown'
            market_supported = True

        # Only use market-supported values with valid confidence
        if value is not None and confidence != 'insufficient':
            mapped_params[module_name] = value
            mapped_count += 1

            if log_mappings:
                logger.info(
                    f"Mapped: {derived_name} -> {module_name} = {value} "
                    f"(confidence: {confidence}, market_supported: {market_supported})"
                )

    if unmapped and log_mappings:
        logger.warning(f"Unmapped derived factors (no module equivalent): {unmapped}")

    if log_mappings:
        logger.info(f"Parameter mapping complete: {mapped_count} factors mapped")

    return mapped_params


def validate_factor_application(
    market_params: Dict[str, Any],
    derived_factors: Dict[str, Any],
    tolerance: float = 0.01
) -> Dict[str, Any]:
    """
    Validate that derived factors were correctly applied to market_params.

    This is a diagnostic function to verify the mapping worked correctly.

    Args:
        market_params: The effective market parameters being used
        derived_factors: The derived factors from paired sales analysis
        tolerance: Acceptable difference for float comparison (default 1%)

    Returns:
        Validation report with:
        - matched: List of parameters that match derived values
        - missing_in_params: Derived factors not present in market_params
        - using_defaults: Parameters where derived value differs from applied
        - total_derived: Count of derived factors
        - total_applied: Count successfully applied
    """
    report = {
        'matched': [],
        'missing_in_params': [],
        'using_defaults': [],
        'total_derived': 0,
        'total_applied': 0,
        'validation_passed': True
    }

    # Get mapped derived factors
    mapped = map_derived_factors_to_module_params(derived_factors, log_mappings=False)
    report['total_derived'] = len(mapped)

    for module_param, derived_value in mapped.items():
        if module_param == 'submarket_differentials':
            # Skip submarket_differentials - complex nested structure
            continue

        if module_param in market_params:
            applied_value = market_params[module_param]

            # Compare values
            if derived_value is not None and applied_value is not None:
                if isinstance(derived_value, (int, float)) and isinstance(applied_value, (int, float)):
                    # Numeric comparison with tolerance
                    if abs(applied_value - derived_value) / max(abs(derived_value), 1) <= tolerance:
                        report['matched'].append({
                            'param': module_param,
                            'value': applied_value
                        })
                        report['total_applied'] += 1
                    else:
                        report['using_defaults'].append({
                            'param': module_param,
                            'derived': derived_value,
                            'applied': applied_value,
                            'reason': 'Value mismatch - default may have been used'
                        })
                        report['validation_passed'] = False
                else:
                    # Non-numeric comparison
                    if applied_value == derived_value:
                        report['matched'].append({
                            'param': module_param,
                            'value': applied_value
                        })
                        report['total_applied'] += 1
                    else:
                        report['using_defaults'].append({
                            'param': module_param,
                            'derived': derived_value,
                            'applied': applied_value,
                            'reason': 'Value mismatch'
                        })
                        report['validation_passed'] = False
        else:
            report['missing_in_params'].append({
                'param': module_param,
                'derived_value': derived_value
            })
            report['validation_passed'] = False

    return report


def get_factor_source(
    param_name: str,
    derived_factors: Dict[str, Any],
    user_overrides: Dict[str, Any],
    industry_defaults: Dict[str, Any],
    verbose: bool = False
) -> Tuple[Optional[Any], str]:
    """
    Resolve adjustment factor value with explicit source tracking.

    Priority: user_override > derived_factor > industry_default

    This function implements the "fail-loud" approach - it returns the source
    so callers know when defaults are being used (requiring CUSPAP disclosure).

    Args:
        param_name: The module parameter name
        derived_factors: Derived factors from paired sales
        user_overrides: User/appraiser provided overrides
        industry_defaults: Industry default values
        verbose: If True, log the resolution

    Returns:
        Tuple of (value, source) where source is one of:
        - 'user_override': Explicitly provided by user
        - 'market_derived': From paired sales analysis (CUSPAP preferred)
        - 'industry_default': Fallback (requires CUSPAP disclosure)
        - 'not_available': No value available
    """
    # Priority 1: User override (explicit configuration)
    if param_name in user_overrides and user_overrides[param_name] is not None:
        value = user_overrides[param_name]
        if verbose:
            logger.info(f"Factor {param_name}: {value} (source: user_override)")
        return value, 'user_override'

    # Priority 2: Market-derived (from paired sales)
    # Need to reverse-map the module param name to find in derived_factors
    derived_name = MODULE_TO_DERIVED.get(param_name)
    if derived_name and derived_name in derived_factors:
        factor_info = derived_factors[derived_name]
        if isinstance(factor_info, dict):
            value = factor_info.get('value') or factor_info.get('reconciled') or factor_info.get('mean')
            market_supported = factor_info.get('market_supported', True)
            confidence = factor_info.get('confidence', 'unknown')

            if value is not None and market_supported and confidence != 'insufficient':
                if verbose:
                    logger.info(f"Factor {param_name}: {value} (source: market_derived, confidence: {confidence})")
                return value, 'market_derived'
        elif factor_info is not None:
            if verbose:
                logger.info(f"Factor {param_name}: {factor_info} (source: market_derived)")
            return factor_info, 'market_derived'

    # Priority 3: Industry default (REQUIRES CUSPAP DISCLOSURE)
    if param_name in industry_defaults and industry_defaults[param_name] is not None:
        value = industry_defaults[param_name]
        if verbose:
            logger.warning(
                f"Factor {param_name}: {value} (source: industry_default) "
                f"- REQUIRES CUSPAP DISCLOSURE"
            )
        return value, 'industry_default'

    if verbose:
        logger.warning(f"Factor {param_name}: not available from any source")
    return None, 'not_available'


def generate_factor_source_report(
    effective_factors: Dict[str, Any],
    derived_factors: Dict[str, Any],
    user_overrides: Dict[str, Any],
    industry_defaults: Dict[str, Any]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generate a comprehensive report of where each factor value came from.

    This supports CUSPAP disclosure requirements by identifying which
    factors are market-derived vs. industry defaults.

    Returns:
        Dictionary with categorized factor sources:
        - market_derived: Factors from paired sales (preferred)
        - user_override: Factors explicitly set by appraiser
        - industry_default: Factors using defaults (require disclosure)
    """
    report = {
        'market_derived': [],
        'user_override': [],
        'industry_default': [],
        'not_available': []
    }

    for param_name, value in effective_factors.items():
        _, source = get_factor_source(
            param_name, derived_factors, user_overrides, industry_defaults
        )

        report[source].append({
            'parameter': param_name,
            'value': value,
            'derived_name': MODULE_TO_DERIVED.get(param_name)
        })

    return report


# ============================================================================
# DIAGNOSTIC UTILITIES
# ============================================================================

def print_mapping_table():
    """Print the mapping table for debugging."""
    print("\n" + "=" * 70)
    print("DERIVED -> MODULE PARAMETER MAPPING")
    print("=" * 70)
    print(f"{'Derived Name':<40} {'Module Parameter Name':<30}")
    print("-" * 70)
    for derived, module in sorted(DERIVED_TO_MODULE.items()):
        print(f"{derived:<40} {module:<30}")
    print("=" * 70)


if __name__ == '__main__':
    # Test the mapping
    print_mapping_table()

    # Test mapping function
    test_derived = {
        'clear_height_per_foot_per_sf': {'value': 5.59, 'confidence': 'medium'},
        'condition_per_level_pct': {'value': 13.49, 'confidence': 'medium'},
        'age_depreciation_pct_per_year': {'value': 3.0, 'confidence': 'medium'},
    }

    print("\nTest mapping:")
    mapped = map_derived_factors_to_module_params(test_derived)
    for k, v in mapped.items():
        print(f"  {k}: {v}")
