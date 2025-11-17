#!/usr/bin/env python3
"""
Income Approach Land Valuation Calculator
Calculates land value using income capitalization approach with market rent analysis,
cap rate selection (market extraction, band of investment, buildup), and reconciliation
with sales comparison approach.

Architecture: Thin orchestration layer (<400 lines) with modular components
Author: Claude Code
Created: 2025-11-17
"""

import json
import sys
import os
from typing import Dict, Any, Optional
import argparse

# Add shared utils to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from Shared_Utils.report_utils import eastern_timestamp

# Import local modules
from modules import (
    validate_input_data,
    analyze_market_rent,
    select_capitalization_rate,
    reconcile_with_sales_comparison,
    format_report
)


def calculate_noi(
    market_rent: float,
    operating_expenses: Dict[str, float]
) -> Dict[str, float]:
    """
    Calculate Net Operating Income.

    Args:
        market_rent: Annual market rent
        operating_expenses: Dict with property_tax, insurance, maintenance

    Returns:
        Dictionary with:
            - gross_income: Market rent
            - total_operating_expenses: Sum of all expenses
            - noi: Net operating income
            - expense_breakdown: Individual expense items
    """
    total_expenses = sum(operating_expenses.values())
    noi = market_rent - total_expenses

    return {
        'gross_income': market_rent,
        'total_operating_expenses': total_expenses,
        'noi': noi,
        'expense_breakdown': operating_expenses
    }


def calculate_income_value(noi: float, cap_rate: float) -> float:
    """
    Calculate land value by income approach.

    Formula: Value = NOI / Cap Rate

    Args:
        noi: Net operating income
        cap_rate: Capitalization rate (as decimal)

    Returns:
        Land value
    """
    if cap_rate <= 0:
        raise ValueError(f"Cap rate must be positive, got {cap_rate}")

    return noi / cap_rate


def process_valuation(data: Dict[str, Any], verbose: bool = False) -> Dict[str, Any]:
    """
    Main orchestration function for income approach land valuation.

    Args:
        data: Validated input data dictionary
        verbose: Print progress messages

    Returns:
        Complete results dictionary
    """
    if verbose:
        print("\n" + "="*60)
        print("INCOME APPROACH LAND VALUATION CALCULATOR")
        print("="*60)

    # ========================================================================
    # Step 1: Market Rent Analysis
    # ========================================================================
    if verbose:
        print("\n[1/5] Analyzing market rent...")

    rent_analysis = analyze_market_rent(data)

    if verbose:
        print(f"  ✓ Concluded market rent: ${rent_analysis['concluded_market_rent']:,.2f}")
        print(f"  ✓ Based on {rent_analysis['rent_statistics']['count']} comparables")

    # ========================================================================
    # Step 2: Capitalization Rate Selection
    # ========================================================================
    if verbose:
        print("\n[2/5] Selecting capitalization rate...")

    cap_rate_analysis = select_capitalization_rate(data)

    if verbose:
        print(f"  ✓ Concluded cap rate: {cap_rate_analysis['concluded_cap_rate']:.2%}")
        print(f"  ✓ Market range: {cap_rate_analysis['cap_rate_range']['low']:.2%} - "
              f"{cap_rate_analysis['cap_rate_range']['high']:.2%}")

    # ========================================================================
    # Step 3: Calculate NOI
    # ========================================================================
    if verbose:
        print("\n[3/5] Calculating Net Operating Income...")

    noi_calculation = calculate_noi(
        rent_analysis['concluded_market_rent'],
        data['operating_expenses']
    )

    if verbose:
        print(f"  ✓ Market rent: ${noi_calculation['gross_income']:,.2f}")
        print(f"  ✓ Operating expenses: ${noi_calculation['total_operating_expenses']:,.2f}")
        print(f"  ✓ NOI: ${noi_calculation['noi']:,.2f}")

    # ========================================================================
    # Step 4: Calculate Income Value
    # ========================================================================
    if verbose:
        print("\n[4/5] Calculating land value by income approach...")

    income_value = calculate_income_value(
        noi_calculation['noi'],
        cap_rate_analysis['concluded_cap_rate']
    )

    if verbose:
        print(f"  ✓ Income approach value: ${income_value:,.2f}")

    # ========================================================================
    # Step 5: Reconciliation and Sensitivity Analysis
    # ========================================================================
    if verbose:
        print("\n[5/5] Reconciling with sales comparison approach...")

    reconciliation_results = reconcile_with_sales_comparison(
        noi_calculation['noi'],
        cap_rate_analysis['concluded_cap_rate'],
        income_value,
        data
    )

    final_value = reconciliation_results['reconciliation']['final_value']

    if verbose:
        print(f"  ✓ Final concluded value: ${final_value:,.2f}")

    # ========================================================================
    # Compile Results
    # ========================================================================
    results = {
        'site_type': data['site_type'],
        'valuation_date': eastern_timestamp(include_time=False),
        'market_rent_analysis': rent_analysis,
        'cap_rate_analysis': cap_rate_analysis,
        'noi_calculation': noi_calculation,
        'income_approach_value': income_value,
        'reconciliation': reconciliation_results['reconciliation'],
        'sensitivity_analysis': reconciliation_results['sensitivity_analysis'],
        'final_concluded_value': final_value
    }

    if verbose:
        print("\n" + "="*60)
        print("CALCULATION COMPLETE")
        print("="*60)
        print(f"\nFinal Land Value: ${final_value:,.2f}\n")

    return results


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Income Approach Land Valuation Calculator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python land_capitalization_calculator.py input.json

  # With verbose output
  python land_capitalization_calculator.py input.json --verbose

  # Specify output file
  python land_capitalization_calculator.py input.json --output results.json

  # Generate markdown report
  python land_capitalization_calculator.py input.json --report
        """
    )

    parser.add_argument(
        'input_file',
        help='Path to input JSON file'
    )

    parser.add_argument(
        '--output',
        '-o',
        help='Output JSON file path (default: print to stdout)',
        default=None
    )

    parser.add_argument(
        '--report',
        '-r',
        help='Generate markdown report in Reports/ directory',
        action='store_true'
    )

    parser.add_argument(
        '--verbose',
        '-v',
        help='Print detailed progress messages',
        action='store_true'
    )

    args = parser.parse_args()

    # ========================================================================
    # Load and Validate Input
    # ========================================================================
    try:
        with open(args.input_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in input file: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        validated_data = validate_input_data(data)
    except ValueError as e:
        print(f"ERROR: Input validation failed:\n{e}", file=sys.stderr)
        sys.exit(1)

    # ========================================================================
    # Process Valuation
    # ========================================================================
    try:
        results = process_valuation(validated_data, verbose=args.verbose)
    except Exception as e:
        print(f"ERROR: Calculation failed: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

    # ========================================================================
    # Output Results
    # ========================================================================
    # JSON output
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        if args.verbose:
            print(f"\n✓ Results saved to: {args.output}")
    elif not args.report:
        # Print to stdout if no output file and not generating report
        print(json.dumps(results, indent=2))

    # ========================================================================
    # Generate Markdown Report
    # ========================================================================
    if args.report:
        report_content = format_report(
            results['site_type'],
            results['market_rent_analysis'],
            results['cap_rate_analysis'],
            results['noi_calculation']['noi'],
            results['income_approach_value'],
            {
                'reconciliation': results['reconciliation'],
                'sensitivity_analysis': results['sensitivity_analysis']
            }
        )

        # Create Reports directory if it doesn't exist
        reports_dir = os.path.join(
            os.path.dirname(__file__),
            '../../../Reports'
        )
        os.makedirs(reports_dir, exist_ok=True)

        # Generate filename with timestamp
        timestamp = eastern_timestamp(include_time=True)
        site_type_slug = results['site_type'].lower().replace(' ', '_')[:30]
        report_filename = f"{timestamp}_income_approach_{site_type_slug}.md"
        report_path = os.path.join(reports_dir, report_filename)

        with open(report_path, 'w') as f:
            f.write(report_content)

        print(f"\n✓ Report generated: {report_path}")


if __name__ == "__main__":
    main()
