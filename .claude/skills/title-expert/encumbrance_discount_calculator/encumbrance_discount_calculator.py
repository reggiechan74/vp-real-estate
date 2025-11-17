#!/usr/bin/env python3
"""
Encumbrance Discount Valuation Calculator
Calculates percentage of fee discounts for easements and encumbrances

Author: Claude Code
Created: 2025-11-17
"""

import json
import sys
import os
from typing import Dict, Optional

# Add parent directories to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from Shared_Utils.financial_utils import npv
from Shared_Utils.report_utils import eastern_timestamp

# Import calculator modules
from modules.validators import validate_input
from modules.cumulative_impact import (
    calculate_individual_discounts,
    calculate_cumulative_discount,
    calculate_paired_sales_adjustment
)
from modules.residual_analysis import (
    analyze_development_potential,
    calculate_residual_value
)
from modules.marketability import (
    analyze_buyer_pool,
    calculate_marketability_discount
)
from modules.output_formatters import format_report, format_summary_table


def calculate_agricultural_income_capitalization(
    agricultural_impacts: Dict
) -> Dict:
    """
    Calculate present value of ongoing agricultural losses.

    Uses income capitalization: PV = Annual Loss / Cap Rate

    Args:
        agricultural_impacts: Agricultural impact data
            {
                'annual_crop_loss': 5000,
                'cap_rate': 0.05,
                'operational_inefficiency_pct': 10
            }

    Returns:
        Capitalized value calculation
    """
    annual_loss = agricultural_impacts['annual_crop_loss']
    cap_rate = agricultural_impacts['cap_rate']

    # Capitalize annual loss into perpetuity
    capitalized_value = annual_loss / cap_rate

    # Add operational inefficiency if provided
    operational_inefficiency = agricultural_impacts.get('operational_inefficiency_pct', 0)
    inefficiency_adjustment = capitalized_value * (operational_inefficiency / 100)

    total_impact = capitalized_value + inefficiency_adjustment

    return {
        'annual_crop_loss': annual_loss,
        'cap_rate': cap_rate,
        'capitalized_value': capitalized_value,
        'operational_inefficiency_pct': operational_inefficiency,
        'inefficiency_adjustment': inefficiency_adjustment,
        'total_impact': total_impact
    }


def run_encumbrance_analysis(
    input_data: Dict,
    method: str = 'multiplicative',
    marketability_method: str = 'conservative',
    verbose: bool = False
) -> Dict:
    """
    Run complete encumbrance discount analysis.

    Args:
        input_data: Input data dictionary
        method: Cumulative discount method
            'multiplicative' - (1-D₁) × (1-D₂) × (1-D₃) [DEFAULT]
            'additive' - D₁ + D₂ + D₃
            'geometric_mean' - Geometric mean
        marketability_method: Marketability discount method
            'conservative' - Higher discount [DEFAULT]
            'moderate' - Mid-range
            'optimistic' - Lower discount
        verbose: Print detailed progress

    Returns:
        Complete analysis results dictionary
    """
    if verbose:
        print("=" * 80)
        print("ENCUMBRANCE DISCOUNT VALUATION CALCULATOR")
        print("=" * 80)
        print()

    # Step 1: Validate input
    if verbose:
        print("STEP 1: Validating input data...")

    is_valid, errors, validated_data = validate_input(input_data)

    if not is_valid:
        print("\n❌ VALIDATION ERRORS:")
        for error in errors:
            print(f"   - {error}")
        raise ValueError("Input validation failed")

    if verbose:
        print("✓ Input validation passed")
        print()

    # Extract validated data
    property_data = validated_data['property']
    encumbrances = validated_data['encumbrances']
    agricultural_impacts = validated_data.get('agricultural_impacts')
    paired_sales = validated_data.get('paired_sales')

    # Step 2: Calculate individual encumbrance discounts
    if verbose:
        print("STEP 2: Calculating individual encumbrance discounts...")

    individual_discounts = calculate_individual_discounts(
        encumbrances,
        property_data['total_area_acres'],
        property_data['unencumbered_value']
    )

    if verbose:
        for disc in individual_discounts:
            print(f"  Encumbrance #{disc['number']} ({disc['type']}): "
                  f"{disc['impact_percentage']:.1f}% → ${disc['discount_amount']:,.2f}")
        print()

    # Step 3: Calculate cumulative discount
    if verbose:
        print(f"STEP 3: Calculating cumulative discount (method: {method})...")

    cumulative_discount = calculate_cumulative_discount(
        individual_discounts,
        method=method
    )

    if verbose:
        print(f"  Cumulative discount: {cumulative_discount['cumulative_discount_percentage']:.2f}%")
        print(f"  Total discount amount: ${cumulative_discount['total_discount_amount']:,.2f}")
        print()

    # Step 4: Analyze development potential
    if verbose:
        print("STEP 4: Analyzing development potential impact...")

    development_potential = analyze_development_potential(
        property_data,
        encumbrances,
        individual_discounts
    )

    if verbose:
        print(f"  Buildable ratio: {development_potential['buildable_ratio']*100:.1f}%")
        print(f"  Subdivision feasibility: {development_potential['subdivision_impact']['subdivision_feasibility']}")
        print()

    # Step 5: Calculate residual value
    if verbose:
        print("STEP 5: Calculating residual land value...")

    residual_value = calculate_residual_value(
        property_data['unencumbered_value'],
        development_potential,
        cumulative_discount
    )

    if verbose:
        print(f"  Base residual: ${residual_value['base_residual_value']:,.2f}")
        print(f"  Final residual: ${residual_value['final_residual_value']:,.2f}")
        print()

    # Step 6: Analyze buyer pool and marketability
    if verbose:
        print("STEP 6: Analyzing buyer pool and marketability impact...")

    buyer_pool_analysis = analyze_buyer_pool(
        property_data,
        encumbrances,
        individual_discounts
    )

    if verbose:
        print(f"  Overall impact: {buyer_pool_analysis['overall_impact']}")
        print(f"  Buyer pool reduction: {buyer_pool_analysis['buyer_pool_reduction_percentage']}%")
        print()

    # Step 7: Calculate marketability discount
    if verbose:
        print(f"STEP 7: Calculating marketability discount (method: {marketability_method})...")

    marketability_discount = calculate_marketability_discount(
        buyer_pool_analysis,
        residual_value['base_residual_value'],
        method=marketability_method
    )

    if verbose:
        print(f"  Marketability discount: {marketability_discount['discount_percentage']:.2f}%")
        print(f"  Discount amount: ${marketability_discount['discount_amount']:,.2f}")
        print()

    # Step 8: Optional - Agricultural income capitalization
    agricultural_analysis = None
    if agricultural_impacts:
        if verbose:
            print("STEP 8: Calculating agricultural income capitalization...")

        agricultural_analysis = calculate_agricultural_income_capitalization(
            agricultural_impacts
        )

        if verbose:
            print(f"  Annual crop loss: ${agricultural_analysis['annual_crop_loss']:,.2f}")
            print(f"  Capitalized value: ${agricultural_analysis['capitalized_value']:,.2f}")
            print()

    # Step 9: Optional - Paired sales analysis
    paired_sales_analysis = None
    if paired_sales:
        if verbose:
            print("STEP 9: Analyzing paired sales comparables...")

        paired_sales_analysis = calculate_paired_sales_adjustment(
            paired_sales,
            property_data['total_area_acres']
        )

        if verbose and paired_sales_analysis:
            print(f"  Market-derived discount: {paired_sales_analysis['discount_percentage']:.2f}%")
            print()

    # Compile results
    results = {
        'timestamp': eastern_timestamp(),
        'property': property_data,
        'individual_discounts': individual_discounts,
        'cumulative_discount': cumulative_discount,
        'development_potential': development_potential,
        'residual_value': residual_value,
        'buyer_pool_analysis': buyer_pool_analysis,
        'marketability_discount': marketability_discount,
        'agricultural_analysis': agricultural_analysis,
        'paired_sales_analysis': paired_sales_analysis,
        'final_value': marketability_discount['adjusted_value'],
        'total_discount_amount': property_data['unencumbered_value'] - marketability_discount['adjusted_value'],
        'total_discount_percentage': ((property_data['unencumbered_value'] - marketability_discount['adjusted_value']) / property_data['unencumbered_value'] * 100)
    }

    if verbose:
        print("=" * 80)
        print("FINAL RESULTS")
        print("=" * 80)
        print(f"Unencumbered value: ${property_data['unencumbered_value']:,.2f}")
        print(f"Final adjusted value: ${results['final_value']:,.2f}")
        print(f"Total discount: ${results['total_discount_amount']:,.2f} ({results['total_discount_percentage']:.2f}%)")
        print("=" * 80)
        print()

    return results


def main():
    """Main entry point for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Encumbrance Discount Valuation Calculator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run analysis from JSON input
  python encumbrance_discount_calculator.py input.json

  # Specify cumulative discount method
  python encumbrance_discount_calculator.py input.json --method additive

  # Conservative marketability discount
  python encumbrance_discount_calculator.py input.json --marketability conservative

  # Output to specific file
  python encumbrance_discount_calculator.py input.json --output report.md

  # Export JSON results
  python encumbrance_discount_calculator.py input.json --json results.json

  # Verbose output
  python encumbrance_discount_calculator.py input.json --verbose
        """
    )

    parser.add_argument('input_file', help='Path to input JSON file')
    parser.add_argument(
        '--method',
        choices=['multiplicative', 'additive', 'geometric_mean'],
        default='multiplicative',
        help='Cumulative discount calculation method (default: multiplicative)'
    )
    parser.add_argument(
        '--marketability',
        choices=['conservative', 'moderate', 'optimistic'],
        default='conservative',
        help='Marketability discount method (default: conservative)'
    )
    parser.add_argument(
        '--output',
        help='Output markdown report file path (default: auto-generated with timestamp)'
    )
    parser.add_argument(
        '--json',
        help='Export JSON results to file'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print detailed progress'
    )

    args = parser.parse_args()

    # Load input file
    try:
        with open(args.input_file, 'r') as f:
            input_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Input file not found: {args.input_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in input file: {e}")
        sys.exit(1)

    # Run analysis
    try:
        results = run_encumbrance_analysis(
            input_data,
            method=args.method,
            marketability_method=args.marketability,
            verbose=args.verbose
        )
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    # Generate report
    report = format_report(
        results['property'],
        results['individual_discounts'],
        results['cumulative_discount'],
        results['development_potential'],
        results['residual_value'],
        results['buyer_pool_analysis'],
        results['marketability_discount'],
        agricultural_impacts=results['agricultural_analysis'],
        paired_sales=results['paired_sales_analysis']
    )

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        # Auto-generate with timestamp
        timestamp = eastern_timestamp().replace(' ', '_').replace(':', '').split('.')[0]
        pin = results['property']['pin'].replace('-', '_')
        output_path = f"Reports/{timestamp}_encumbrance_discount_{pin}.md"

    # Ensure Reports directory exists
    os.makedirs('Reports', exist_ok=True)

    # Write report
    with open(output_path, 'w') as f:
        f.write(report)

    print(f"✓ Report saved to: {output_path}")

    # Export JSON if requested
    if args.json:
        with open(args.json, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"✓ JSON results exported to: {args.json}")

    # Print summary table
    print("\n" + "=" * 80)
    print("VALUATION SUMMARY")
    print("=" * 80)
    print(format_summary_table(
        results['property'],
        results['cumulative_discount'],
        results['residual_value'],
        results['marketability_discount']
    ))


if __name__ == '__main__':
    main()
