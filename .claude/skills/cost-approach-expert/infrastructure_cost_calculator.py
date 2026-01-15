#!/usr/bin/env python3
"""
Infrastructure Cost Approach Calculator

Calculates depreciated replacement cost for infrastructure assets using:
- Replacement Cost New (RCN) estimation
- Physical depreciation (age/life method)
- Functional obsolescence
- External obsolescence
- Market reconciliation (if comparables available)

Usage:
    python infrastructure_cost_calculator.py input.json --output report.md --verbose

Author: Claude Code
Created: 2025-11-17
"""

import json
import sys
import os
import argparse
from typing import Dict, Optional

# Add modules to path
sys.path.insert(0, os.path.dirname(__file__))

# Import modular components
from modules.validators import (
    validate_input,
    validate_market_data,
    validate_specifications
)
from modules.replacement_cost import calculate_replacement_cost_new
from modules.depreciation_analysis import (
    calculate_physical_depreciation,
    calculate_functional_obsolescence,
    calculate_external_obsolescence,
    calculate_total_depreciation
)
from modules.cost_reconciliation import (
    reconcile_with_market,
    calculate_confidence_score
)
from modules.output_formatters import format_cost_report, format_summary_table

# Import shared utilities
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from Shared_Utils.report_utils import eastern_timestamp


def calculate_infrastructure_cost(input_data: Dict, verbose: bool = False) -> Dict:
    """
    Calculate infrastructure asset value using cost approach.

    Args:
        input_data: Complete input dictionary with:
            - asset_type: Type of infrastructure
            - specifications: Asset specifications (optional)
            - construction_costs: Materials, labor, overhead, profit
            - depreciation: Age, life, condition, obsolescence
            - market_data: Comparable sales (optional)
        verbose: Print progress messages

    Returns:
        Dictionary with complete analysis results

    Raises:
        ValueError: If input validation fails

    Example:
        >>> with open('input.json') as f:
        ...     data = json.load(f)
        >>> results = calculate_infrastructure_cost(data, verbose=True)
        >>> print(f"Value: ${results['reconciliation']['reconciled_value']:,.2f}")
    """
    if verbose:
        print("=" * 70)
        print("INFRASTRUCTURE COST APPROACH CALCULATOR")
        print("=" * 70)
        print()

    # Step 1: Validate input
    if verbose:
        print("Step 1: Validating input data...")

    valid, errors = validate_input(input_data)
    if not valid:
        error_msg = "Input validation failed:\n" + "\n".join(f"  - {err}" for err in errors)
        raise ValueError(error_msg)

    # Validate optional data
    market_valid, market_errors = validate_market_data(input_data.get('market_data'))
    if not market_valid:
        print(f"Warning: Market data validation issues:\n" + "\n".join(f"  - {err}" for err in market_errors))

    specs_valid, specs_errors = validate_specifications(input_data.get('specifications'))
    if not specs_valid:
        print(f"Warning: Specifications validation issues:\n" + "\n".join(f"  - {err}" for err in specs_errors))

    if verbose:
        print("  ✓ Input validation passed")
        print()

    # Step 2: Calculate Replacement Cost New (RCN)
    if verbose:
        print("Step 2: Calculating Replacement Cost New (RCN)...")

    rcn_results = calculate_replacement_cost_new(input_data['construction_costs'])

    if verbose:
        print(f"  Materials:      ${rcn_results['materials']:>12,.2f}")
        print(f"  Labor:          ${rcn_results['labor']:>12,.2f}")
        print(f"  Direct Costs:   ${rcn_results['direct_costs']:>12,.2f}")
        print(f"  Overhead ({rcn_results['overhead_percentage']:.1%}):  ${rcn_results['overhead']:>12,.2f}")
        print(f"  Profit ({rcn_results['profit_percentage']:.1%}):    ${rcn_results['profit']:>12,.2f}")
        print(f"  ---")
        print(f"  RCN:            ${rcn_results['replacement_cost_new']:>12,.2f}")
        print()

    # Step 3: Calculate Physical Depreciation
    if verbose:
        print("Step 3: Calculating Physical Depreciation...")

    physical_dep = calculate_physical_depreciation(
        input_data['depreciation'],
        rcn_results['replacement_cost_new']
    )

    if verbose:
        print(f"  Method:         {physical_dep['method']}")
        print(f"  Effective Age:  {physical_dep['effective_age']} years")
        print(f"  Economic Life:  {physical_dep['economic_life']} years")
        print(f"  Remaining Life: {physical_dep['remaining_life']} years ({physical_dep['percent_remaining']:.1f}%)")
        print(f"  Condition:      {physical_dep['condition_rating']}")
        print(f"  Depreciation:   ${physical_dep['physical_depreciation']:>12,.2f} ({physical_dep['depreciation_rate']:.1%})")
        if physical_dep.get('variance_significant'):
            print(f"  ⚠️  {physical_dep['recommendation']}")
        print()

    # Step 4: Calculate Functional Obsolescence
    if verbose:
        print("Step 4: Calculating Functional Obsolescence...")

    functional_obs = calculate_functional_obsolescence(
        input_data['depreciation'].get('functional_obsolescence', 0),
        rcn_results['replacement_cost_new'],
        input_data.get('specifications')
    )

    if verbose:
        print(f"  Severity:       {functional_obs['severity']}")
        print(f"  Description:    {functional_obs['description']}")
        print(f"  Obsolescence:   ${functional_obs['functional_obsolescence']:>12,.2f} ({functional_obs['obsolescence_rate']:.1%})")
        print()

    # Step 5: Calculate External Obsolescence
    if verbose:
        print("Step 5: Calculating External Obsolescence...")

    external_obs = calculate_external_obsolescence(
        input_data['depreciation'].get('external_obsolescence', 0),
        rcn_results['replacement_cost_new'],
        input_data.get('market_data')
    )

    if verbose:
        print(f"  Severity:       {external_obs['severity']}")
        print(f"  Description:    {external_obs['description']}")
        print(f"  Obsolescence:   ${external_obs['external_obsolescence']:>12,.2f} ({external_obs['obsolescence_rate']:.1%})")
        print()

    # Step 6: Calculate Total Depreciation
    if verbose:
        print("Step 6: Calculating Total Depreciation...")

    total_dep = calculate_total_depreciation(
        physical_dep,
        functional_obs,
        external_obs,
        rcn_results['replacement_cost_new']
    )

    if verbose:
        print(f"  Physical:       ${total_dep['physical_depreciation']:>12,.2f} ({total_dep['breakdown_percentages']['physical']:.1f}%)")
        print(f"  Functional:     ${total_dep['functional_obsolescence']:>12,.2f} ({total_dep['breakdown_percentages']['functional']:.1f}%)")
        print(f"  External:       ${total_dep['external_obsolescence']:>12,.2f} ({total_dep['breakdown_percentages']['external']:.1f}%)")
        print(f"  ---")
        print(f"  Total Depr:     ${total_dep['total_depreciation']:>12,.2f} ({total_dep['total_depreciation_rate']:.1%})")
        print(f"  Depreciated RC: ${total_dep['depreciated_replacement_cost']:>12,.2f}")
        print()

    # Step 7: Reconcile with Market (if data available)
    if verbose:
        print("Step 7: Market Reconciliation...")

    reconciliation = reconcile_with_market(
        total_dep['depreciated_replacement_cost'],
        input_data.get('market_data'),
        input_data.get('asset_type', '')
    )

    if verbose:
        if reconciliation.get('market_approach_available'):
            print(f"  Comparables:    {reconciliation['relevant_sales_count']}")
            print(f"  Market Median:  ${reconciliation['market_statistics']['median']:>12,.2f}")
            print(f"  Cost Value:     ${reconciliation['cost_approach_value']:>12,.2f}")
            print(f"  Variance:       ${reconciliation['variance_amount']:>12,.2f} ({reconciliation['variance_percentage']:+.1f}%)")
            print(f"  Method:         {reconciliation['reconciliation_method']}")
            print(f"  ---")
            print(f"  Reconciled:     ${reconciliation['reconciled_value']:>12,.2f}")
            print(f"  Confidence:     {reconciliation['confidence_level']}")
        else:
            print(f"  Market data not available - using cost approach only")
            print(f"  Indicated Value: ${reconciliation['reconciled_value']:>12,.2f}")
        print()

    # Step 8: Calculate Confidence Score
    confidence = calculate_confidence_score(
        total_dep['depreciated_replacement_cost'],
        input_data.get('market_data'),
        input_data['depreciation']
    )

    if verbose:
        print("Step 8: Confidence Assessment...")
        print(f"  Score:          {confidence['score']}/100 ({confidence['rating']})")
        print(f"  Interpretation: {confidence['interpretation']}")
        print()
        print("=" * 70)
        print()

    # Return complete results
    return {
        'input_data': input_data,
        'rcn_results': rcn_results,
        'physical_depreciation': physical_dep,
        'functional_obsolescence': functional_obs,
        'external_obsolescence': external_obs,
        'total_depreciation': total_dep,
        'reconciliation': reconciliation,
        'confidence': confidence,
        'timestamp': eastern_timestamp()
    }


def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(
        description='Infrastructure Cost Approach Calculator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic calculation
  python infrastructure_cost_calculator.py samples/transmission_tower.json

  # With verbose output and custom report path
  python infrastructure_cost_calculator.py samples/transmission_tower.json \\
    --output Reports/2025-11-17_143022_tower_valuation.md \\
    --verbose

  # JSON output only
  python infrastructure_cost_calculator.py samples/transmission_tower.json \\
    --json results.json \\
    --verbose
        """
    )

    parser.add_argument(
        'input_file',
        help='Input JSON file with asset and cost data'
    )

    parser.add_argument(
        '-o', '--output',
        help='Output markdown report path (default: auto-generated in Reports/)',
        default=None
    )

    parser.add_argument(
        '-j', '--json',
        help='Output JSON results path (optional)',
        default=None
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Print detailed progress and calculations'
    )

    args = parser.parse_args()

    # Read input file
    try:
        with open(args.input_file, 'r') as f:
            input_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}", file=sys.stderr)
        sys.exit(1)

    # Calculate
    try:
        results = calculate_infrastructure_cost(input_data, verbose=args.verbose)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Generate markdown report
    if args.output or not args.json:
        report = format_cost_report(
            results['input_data'],
            results['rcn_results'],
            results['physical_depreciation'],
            results['functional_obsolescence'],
            results['external_obsolescence'],
            results['total_depreciation'],
            results['reconciliation']
        )

        # Determine output path
        if args.output:
            output_path = args.output
        else:
            # Auto-generate in Reports/ with timestamp
            timestamp = eastern_timestamp()
            asset_type = input_data.get('asset_type', 'infrastructure').replace(' ', '_').lower()
            output_path = f"Reports/{timestamp}_cost_approach_{asset_type}.md"

        # Ensure Reports directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)

        # Write report
        with open(output_path, 'w') as f:
            f.write(report)

        print(f"✓ Markdown report saved to: {output_path}")

    # Save JSON results if requested
    if args.json:
        with open(args.json, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"✓ JSON results saved to: {args.json}")

    # Print summary
    if not args.verbose:
        print()
        print("VALUATION SUMMARY")
        print("=" * 70)
        print(f"Asset Type:           {input_data.get('asset_type', 'N/A')}")
        print(f"RCN:                  ${results['rcn_results']['replacement_cost_new']:,.2f}")
        print(f"Total Depreciation:   ${results['total_depreciation']['total_depreciation']:,.2f} ({results['total_depreciation']['total_depreciation_rate']:.1%})")
        print(f"Depreciated RC:       ${results['total_depreciation']['depreciated_replacement_cost']:,.2f}")
        if results['reconciliation'].get('market_approach_available'):
            print(f"Market Reconciled:    ${results['reconciliation']['reconciled_value']:,.2f}")
        print(f"Confidence:           {results['reconciliation']['confidence_level']}")
        print("=" * 70)
        print()


if __name__ == '__main__':
    main()
