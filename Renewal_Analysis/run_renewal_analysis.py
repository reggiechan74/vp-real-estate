import json
import sys
from datetime import datetime
from Renewal_Analysis.renewal_analysis import (
    RenewalScenario,
    RelocationScenario,
    GeneralInputs,
    compare_scenarios,
    calculate_breakeven_rent,
    sensitivity_analysis,
    print_comparison_report
)

# Load JSON input
with open(sys.argv[1], 'r') as f:
    data = json.load(f)

# Convert JSON to calculator inputs
# Extract rent psf values from rent_schedule
renewal_rents = [rs['rent_per_sf'] for rs in data['renewal_scenario']['rent_schedule']]
relocation_rents = [rs['rent_per_sf'] for rs in data['relocation_scenario']['rent_schedule']]

# Average operating costs (calculator uses single value)
renewal_op_costs = sum([rs['operating_costs_per_sf'] for rs in data['renewal_scenario']['rent_schedule']]) / len(data['renewal_scenario']['rent_schedule'])
relocation_op_costs = sum([rs['operating_costs_per_sf'] for rs in data['relocation_scenario']['rent_schedule']]) / len(data['relocation_scenario']['rent_schedule'])

renewal = RenewalScenario(
    annual_rent_psf=renewal_rents,
    term_years=data['renewal_scenario']['term_years'],
    ti_allowance_psf=abs(data['renewal_scenario']['ti_allowance_per_sf']),  # Make positive
    additional_ti_psf=data['renewal_scenario']['tenant_funded_ti_per_sf'],
    operating_costs_psf=renewal_op_costs,
    legal_fees=data['renewal_scenario']['legal_fees'],
    renovation_costs_psf=data['renewal_scenario']['renovation_cost_per_sf']
)

relocation = RelocationScenario(
    annual_rent_psf=relocation_rents,
    term_years=data['relocation_scenario']['term_years'],
    ti_allowance_psf=abs(data['relocation_scenario']['ti_allowance_per_sf']),  # Make positive
    ti_requirement_psf=data['relocation_scenario']['tenant_funded_ti_per_sf'],
    operating_costs_psf=relocation_op_costs,
    moving_costs=data['relocation_scenario']['moving_costs'],
    it_moving_costs=data['relocation_scenario']['it_relocation_costs'],
    downtime_days=data['relocation_scenario']['downtime_days'],
    daily_revenue=data['relocation_scenario']['daily_revenue'],
    customer_loss_pct=data['relocation_scenario']['customer_loss_pct'],
    unamortized_improvements=data['relocation_scenario']['unamortized_improvements'],
    restoration_costs=data['relocation_scenario']['restoration_costs'],
    legal_fees=data['relocation_scenario']['legal_fees']
)

general = GeneralInputs(
    rentable_area_sf=data['rentable_area'],
    discount_rate=data['discount_rate']
)

# Run comparison analysis
print(f"\nAnalyzing Renewal vs. Relocation for: {data['tenant_name']}")
print(f"Property: {data['current_location']}")
print(f"Area: {data['rentable_area']:,} sf\n")

comparison = compare_scenarios(renewal, relocation, general)

# Print report
print_comparison_report(comparison)

# Calculate breakeven
breakeven_rent = calculate_breakeven_rent(renewal, relocation, general)
print(f"\nBreakeven Analysis:")
print(f"  Renewal rent would need to increase to ${breakeven_rent:.2f}/sf")
print(f"  before relocation becomes cheaper.")

# Run sensitivity analysis
sensitivity = sensitivity_analysis(renewal, relocation, general)
print(f"\nSensitivity Analysis Complete")
print(f"  Tested variations in rent, TI costs, and disruption costs")

# Save results to JSON
output_data = {
    'tenant_name': data['tenant_name'],
    'analysis_date': datetime.now().strftime('%Y-%m-%d'),
    'recommendation': comparison.recommendation,
    'renewal_npv': comparison.renewal_result.npv,
    'relocation_npv': comparison.relocation_result.npv,
    'npv_difference': comparison.npv_difference,
    'npv_savings_from_renewal': -comparison.npv_difference,  # Negative of difference
    'renewal_ner': comparison.renewal_result.net_effective_rent_psf,
    'relocation_ner': comparison.relocation_result.net_effective_rent_psf,
    'ner_difference': comparison.ner_difference_psf,
    'relocation_irr': comparison.relocation_irr if comparison.relocation_irr else None,
    'breakeven_rent_psf': comparison.breakeven_rent_psf if comparison.breakeven_rent_psf else None,
    'current_margin_psf': comparison.current_margin_psf if comparison.current_margin_psf else None,
    'payback_years': comparison.payback_period_years if comparison.payback_period_years else None,
    'annual_savings': comparison.annual_savings,
    'renewal_details': {
        'total_cash_outflows': comparison.renewal_result.total_cash_outflows,
        'rent_payments': comparison.renewal_result.total_rent_payments,
        'operating_costs': comparison.renewal_result.total_operating_costs,
        'ti_costs': comparison.renewal_result.total_ti_costs,
        'other_costs': comparison.renewal_result.total_other_costs
    },
    'relocation_details': {
        'total_cash_outflows': comparison.relocation_result.total_cash_outflows,
        'rent_payments': comparison.relocation_result.total_rent_payments,
        'operating_costs': comparison.relocation_result.total_operating_costs,
        'ti_costs': comparison.relocation_result.total_ti_costs,
        'other_costs': comparison.relocation_result.total_other_costs
    },
    'sensitivity_analysis': {
        'note': 'Sensitivity analysis results from calculator',
        'summary': sensitivity.to_dict() if sensitivity is not None else {}
    }
}

output_file = sys.argv[1].replace('_input.json', '_results.json')
with open(output_file, 'w') as f:
    json.dump(output_data, f, indent=2)

print(f"\n✓ Results saved to: {output_file}")
