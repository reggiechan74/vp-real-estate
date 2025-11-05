"""
Run IFRS 16 / ASC 842 Lease Accounting Analysis from JSON input.

This script bridges the JSON input format from the /ifrs16-calculation slash command
to the ifrs16_calculator module.

Usage:
    python3 run_ifrs16_analysis.py <input_json_file>

Example:
    python3 run_ifrs16_analysis.py ifrs16_inputs/acme_corp_2025-10-31_input.json

Author: Claude Code
Created: 2025-10-31
GitHub Issue: #3
"""

import json
import sys
import os
from datetime import datetime

from IFRS16_Calculator.ifrs16_calculator import (
    LeaseInputs,
    calculate_ifrs16,
    print_summary,
    export_to_csv
)


def main():
    """Main execution function."""
    if len(sys.argv) < 2:
        print("Error: No input file specified")
        print("Usage: python3 run_ifrs16_analysis.py <input_json_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)

    # Load JSON input
    print(f"\nLoading input from: {input_file}")
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Convert JSON to LeaseInputs
    commencement_date = datetime.strptime(data['commencement_date'], '%Y-%m-%d') if 'commencement_date' in data else datetime.now()

    inputs = LeaseInputs(
        monthly_payments=data['monthly_payments'],
        annual_discount_rate=data['annual_discount_rate'],
        initial_direct_costs=data.get('initial_direct_costs', 0.0),
        prepaid_rent=data.get('prepaid_rent', 0.0),
        lease_incentives=data.get('lease_incentives', 0.0),
        lease_term_months=data.get('lease_term_months', len(data['monthly_payments'])),
        payment_timing=data.get('payment_timing', 'beginning'),
        tenant_name=data.get('tenant_name', 'Tenant'),
        property_address=data.get('property_address', 'Property'),
        commencement_date=commencement_date
    )

    # Run IFRS 16 calculation
    print(f"\nCalculating IFRS 16 Lease Accounting for: {inputs.tenant_name}")
    print(f"Property: {inputs.property_address}")
    print(f"Lease Term: {inputs.lease_term_months} months ({inputs.lease_term_months/12:.1f} years)")
    print(f"Commencement Date: {inputs.commencement_date.strftime('%Y-%m-%d')}")
    print(f"Payment Timing: {inputs.payment_timing.title()}")

    result = calculate_ifrs16(inputs)

    # Print summary
    print_summary(result)

    # Determine output directory and base filename
    input_dir = os.path.dirname(input_file)
    if not input_dir:
        input_dir = "."

    base_filename = os.path.basename(input_file).replace('_input.json', '')

    # Export schedules to CSV
    print("\n" + "="*80)
    print("EXPORTING SCHEDULES")
    print("="*80)

    # Manually create CSV files with correct naming
    amort_file = os.path.join(input_dir, f"{base_filename}_amortization.csv")
    deprec_file = os.path.join(input_dir, f"{base_filename}_depreciation.csv")
    annual_file = os.path.join(input_dir, f"{base_filename}_annual_summary.csv")

    result.amortization_schedule.to_csv(amort_file, index=False)
    result.depreciation_schedule.to_csv(deprec_file, index=False)
    result.annual_summary.to_csv(annual_file, index=False)

    print(f"\n✓ CSV schedules exported:")
    print(f"  - {amort_file}")
    print(f"  - {deprec_file}")
    print(f"  - {annual_file}")

    # Save results to JSON
    output_data = {
        'tenant_name': inputs.tenant_name,
        'property_address': inputs.property_address,
        'commencement_date': inputs.commencement_date.strftime('%Y-%m-%d'),
        'lease_term_months': inputs.lease_term_months,
        'discount_rate': inputs.annual_discount_rate,
        'payment_timing': inputs.payment_timing,

        # Initial balances
        'initial_lease_liability': result.initial_lease_liability,
        'initial_rou_asset': result.initial_rou_asset,

        # Total costs
        'total_interest_expense': result.total_interest_expense,
        'total_depreciation': result.total_depreciation,
        'total_lease_cost': result.total_lease_cost,
        'total_cash_payments': sum(inputs.monthly_payments),

        # Components
        'lease_liability_components': result.lease_liability_components,
        'rou_asset_components': result.rou_asset_components,

        # Rate info
        'monthly_discount_rate': result.monthly_discount_rate,

        # Annual summary
        'annual_summary': result.annual_summary.to_dict('records')
    }

    output_file = input_file.replace('_input.json', '_results.json')
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n✓ Results saved to: {output_file}")

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
