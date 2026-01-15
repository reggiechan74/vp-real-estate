#!/usr/bin/env python3
"""
MCDA Sales Comparison Calculator

Multi-Criteria Decision Analysis for fee simple property valuation
using ordinal ranking methodology.

Pipeline:
1. Load and validate comparable sales data
2. Rank all properties (including subject) on each characteristic
3. Apply weighted scores to create composite rankings
4. Map composite scores to value indication via interpolation/regression
5. Generate comprehensive analysis output

Author: Claude Code
Version: 1.0.0
Date: 2025-12-16
"""

import json
import argparse
import statistics
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path

# Import local modules
from validation import validate_input_data, validate_all_comparables, validate_time_adjustment
from weight_profiles import (
    get_sales_weight_profile,
    get_variable_directions,
    allocate_dynamic_weights,
    get_profile_for_property_type
)
from score_to_price import interpolate_value, regression_value, reconcile_methods


# =============================================================================
# CONDITION ENCODING
# =============================================================================

CONDITION_ENCODING = {
    'excellent': 1,
    'very_good': 2,
    'good': 3,
    'average': 4,
    'fair': 5,
    'poor': 6
}


# =============================================================================
# PROPERTY RANKING
# =============================================================================

def rank_properties(
    properties: List[Dict[str, Any]],
    variable: str,
    direction: str
) -> Dict[str, float]:
    """
    Rank properties on a single variable.

    Args:
        properties: List of property dictionaries
        variable: Variable name to rank on
        direction: 'higher_is_better', 'lower_is_better', or 'closer_to_subject'

    Returns:
        Dictionary mapping property address to rank (1 = best)
    """
    # Extract values for ranking
    values = []
    for prop in properties:
        address = prop.get('address', 'Unknown')
        value = prop.get(variable)

        # Handle condition encoding
        if variable == 'condition' and isinstance(value, str):
            value = CONDITION_ENCODING.get(value.lower(), 4)

        # Handle boolean variables
        if isinstance(value, bool):
            value = 1 if value else 0

        if value is not None:
            values.append((address, float(value)))

    if not values:
        # Return equal ranks if no data
        return {prop.get('address', 'Unknown'): len(properties) / 2 for prop in properties}

    # Sort based on direction
    if direction == 'higher_is_better':
        # Higher value = better = lower rank number
        sorted_values = sorted(values, key=lambda x: x[1], reverse=True)
    elif direction == 'lower_is_better':
        # Lower value = better = lower rank number
        sorted_values = sorted(values, key=lambda x: x[1])
    else:
        # closer_to_subject - handled separately
        sorted_values = sorted(values, key=lambda x: x[1])

    # Assign ranks with tie handling (average rank)
    rankings = {}
    i = 0
    while i < len(sorted_values):
        # Find all ties at this position
        current_value = sorted_values[i][1]
        tie_start = i
        while i < len(sorted_values) and sorted_values[i][1] == current_value:
            i += 1
        tie_end = i

        # Average rank for ties (ranks are 1-indexed)
        avg_rank = (tie_start + 1 + tie_end) / 2

        for j in range(tie_start, tie_end):
            rankings[sorted_values[j][0]] = avg_rank

    # Fill in missing properties with last rank
    last_rank = len(sorted_values) + 1
    for prop in properties:
        address = prop.get('address', 'Unknown')
        if address not in rankings:
            rankings[address] = last_rank

    return rankings


# =============================================================================
# COMPOSITE SCORE CALCULATION
# =============================================================================

def calculate_composite_scores(
    properties: List[Dict[str, Any]],
    weights: Dict[str, float]
) -> Dict[str, float]:
    """
    Calculate weighted composite scores for all properties.

    Args:
        properties: List of property dictionaries
        weights: Dictionary of variable weights (must sum to 1.0)

    Returns:
        Dictionary mapping property address to composite score
    """
    directions = get_variable_directions()

    # Calculate ranks for each variable
    all_rankings = {}
    for variable, weight in weights.items():
        if weight > 0:
            direction = directions.get(variable, 'higher_is_better')
            all_rankings[variable] = rank_properties(properties, variable, direction)

    # Calculate weighted composite score for each property
    composite_scores = {}
    for prop in properties:
        address = prop.get('address', 'Unknown')
        weighted_sum = 0.0

        for variable, weight in weights.items():
            if variable in all_rankings and weight > 0:
                rank = all_rankings[variable].get(address, len(properties))
                weighted_sum += weight * rank

        composite_scores[address] = weighted_sum

    return composite_scores


# =============================================================================
# MAIN ANALYSIS FUNCTION
# =============================================================================

def run_analysis(
    input_data: Dict[str, Any],
    weight_profile: Optional[str] = None,
    regression_method: str = 'ols'
) -> Dict[str, Any]:
    """
    Run complete MCDA sales comparison analysis.

    Args:
        input_data: Input data dictionary with subject and comparables
        weight_profile: Weight profile name (default: auto-detect from property type)
        regression_method: Regression method ('ols', 'monotone', 'theil_sen')

    Returns:
        Complete analysis results dictionary
    """
    # Extract components
    subject = input_data['subject_property']
    comparables = input_data['comparable_sales']

    # Property type: check root level first, then subject_property (unified schema support)
    property_type = input_data.get('property_type')
    if not property_type:
        property_type = subject.get('property_type', 'industrial')

    # Valuation date: check root level first, then market_parameters (unified schema support)
    valuation_date = input_data.get('valuation_date')
    if not valuation_date:
        market_params = input_data.get('market_parameters', {})
        valuation_date = market_params.get('valuation_date', datetime.now().strftime('%Y-%m-%d'))

    # Validate comparables
    validation_result = validate_all_comparables(comparables, valuation_date, property_type)
    valid_comps = validation_result['valid_comparables']

    # Get weight profile
    if weight_profile:
        weights = get_sales_weight_profile(weight_profile)
    else:
        weights = get_profile_for_property_type(property_type)

    # Determine available variables and adjust weights
    available_vars = {}
    for var in weights.keys():
        has_data = any(var in comp and comp[var] is not None for comp in valid_comps)
        available_vars[var] = has_data

    adjusted_weights = allocate_dynamic_weights(available_vars, weights)

    # Combine subject and comparables for ranking
    all_properties = valid_comps + [subject]

    # Calculate composite scores
    composite_scores = calculate_composite_scores(all_properties, adjusted_weights)

    # Get subject score
    subject_score = composite_scores[subject['address']]
    subject_sf = subject['building_sf']

    # Prepare comparables with scores and PSF for score-to-price mapping
    scored_comps = []
    comparable_analysis = []

    for comp in valid_comps:
        address = comp['address']
        score = composite_scores[address]
        price_psf = comp['sale_price'] / comp['building_sf']

        # Get variable ranks for this comparable
        variable_ranks = {}
        directions = get_variable_directions()
        for var in adjusted_weights.keys():
            if var in available_vars and available_vars[var]:
                direction = directions.get(var, 'higher_is_better')
                rankings = rank_properties(all_properties, var, direction)
                variable_ranks[var] = rankings.get(address, 0)

        scored_comps.append({
            'id': comp.get('id', address[:20]),
            'score': score,
            'price_psf': price_psf,
            'price_total': comp['sale_price'],
            'building_sf': comp['building_sf']
        })

        comparable_analysis.append({
            'id': comp.get('id', address[:20]),
            'address': address,
            'sale_price': comp['sale_price'],
            'sale_date': comp['sale_date'],
            'building_sf': comp['building_sf'],
            'price_psf': round(price_psf, 2),
            'composite_score': round(score, 3),
            'variable_ranks': variable_ranks
        })

    # Score-to-price mapping
    interpolation_result = interpolate_value(subject_score, scored_comps, subject_sf)
    regression_result = regression_value(subject_score, scored_comps, subject_sf, method=regression_method)
    reconciled = reconcile_methods(interpolation_result, regression_result, subject_sf)

    # Build value indication
    value_indication = {
        'indicated_value_psf': round(reconciled['indicated_value_psf'], 2),
        'indicated_value_total': round(reconciled['indicated_value_total'], 0),
        'value_range_psf': (
            round(min(interpolation_result['indicated_value_psf'], regression_result['indicated_value_psf']) * 0.95, 2),
            round(max(interpolation_result['indicated_value_psf'], regression_result['indicated_value_psf']) * 1.05, 2)
        ),
        'value_range_total': (
            round(reconciled['indicated_value_total'] * 0.95, 0),
            round(reconciled['indicated_value_total'] * 1.05, 0)
        ),
        'interpolation': {
            'indicated_psf': round(interpolation_result['indicated_value_psf'], 2),
            'confidence': interpolation_result['confidence'],
            'lower_bracket': interpolation_result.get('lower_bracket', {}).get('id'),
            'upper_bracket': interpolation_result.get('upper_bracket', {}).get('id')
        },
        'regression': {
            'indicated_psf': round(regression_result['indicated_value_psf'], 2),
            'method': regression_result['method_used'],
            'r_squared': round(regression_result['r_squared'], 3),
            'beta': round(regression_result['beta'], 4)
        },
        'reconciliation': {
            'method_weights': reconciled['method_weights'],
            'rationale': reconciled['reconciliation_rationale']
        }
    }

    # Build analysis summary (with unified schema fallbacks)
    market_params = input_data.get('market_parameters', {})
    market_area = input_data.get('market_area') or market_params.get('market_area', 'Unknown')

    analysis_summary = {
        'analysis_date': input_data.get('analysis_date', datetime.now().strftime('%Y-%m-%d')),
        'valuation_date': valuation_date,
        'market_area': market_area,
        'property_type': property_type,
        'comparables_submitted': len(comparables),
        'comparables_used': len(valid_comps),
        'comparables_excluded': validation_result['summary']['excluded_count'],
        'weights_profile': weight_profile or f'{property_type}_default',
        'regression_method': regression_method,
        'methodology': 'MCDA Ordinal Ranking with Score-to-Price Mapping',
        'warnings': validation_result['warnings']
    }

    return {
        'subject_property': {
            'address': subject['address'],
            'building_sf': subject['building_sf'],
            'composite_score': round(subject_score, 3)
        },
        'comparable_analysis': comparable_analysis,
        'composite_scores': {k: round(v, 3) for k, v in composite_scores.items()},
        'value_indication': value_indication,
        'analysis_summary': analysis_summary
    }


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """Command-line interface for MCDA Sales Comparison."""
    parser = argparse.ArgumentParser(
        description='MCDA Sales Comparison Calculator - Ordinal Ranking DCA',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python mcda_sales_calculator.py input.json
  python mcda_sales_calculator.py input.json --output results.json
  python mcda_sales_calculator.py input.json --profile industrial_logistics
  python mcda_sales_calculator.py input.json --regression monotone --verbose
        """
    )

    parser.add_argument('input', help='Input JSON file path')
    parser.add_argument('--output', '-o', help='Output JSON file path')
    parser.add_argument('--profile', '-p', help='Weight profile name')
    parser.add_argument('--regression', '-r',
                        choices=['ols', 'monotone', 'theil_sen'],
                        default='ols',
                        help='Regression method (default: ols)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Print detailed output')

    args = parser.parse_args()

    # Load input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return 1

    with open(input_path) as f:
        input_data = json.load(f)

    # Validate input
    errors = validate_input_data(input_data)
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")
        return 1

    # Run analysis
    if args.verbose:
        print(f"Running MCDA Sales Comparison Analysis...")
        print(f"  Subject: {input_data['subject_property']['address']}")
        print(f"  Comparables: {len(input_data['comparable_sales'])}")

    results = run_analysis(
        input_data,
        weight_profile=args.profile,
        regression_method=args.regression
    )

    # Output results
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        if args.verbose:
            print(f"\nResults saved to: {output_path}")
    else:
        print(json.dumps(results, indent=2))

    # Print summary
    if args.verbose:
        vi = results['value_indication']
        print(f"\n{'='*60}")
        print(f"VALUE INDICATION")
        print(f"{'='*60}")
        print(f"  Indicated Value: ${vi['indicated_value_psf']:.2f}/SF")
        print(f"  Total Value: ${vi['indicated_value_total']:,.0f}")
        print(f"  Value Range: ${vi['value_range_psf'][0]:.2f} - ${vi['value_range_psf'][1]:.2f}/SF")
        print(f"{'='*60}")

    return 0


if __name__ == '__main__':
    exit(main())
