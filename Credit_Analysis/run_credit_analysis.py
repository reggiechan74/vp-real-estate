import json
import sys
from credit_analysis import (
    FinancialData,
    CreditInputs,
    analyze_tenant_credit,
    print_credit_report
)

# Load JSON input
with open(sys.argv[1], 'r') as f:
    data = json.load(f)

# Convert JSON to CreditInputs
financial_data = [
    FinancialData(
        year=fd['year'],
        current_assets=fd.get('current_assets', 0),
        total_assets=fd.get('total_assets', 0),
        inventory=fd.get('inventory', 0),
        cash_and_equivalents=fd.get('cash_and_equivalents', 0),
        current_liabilities=fd.get('current_liabilities', 0),
        total_liabilities=fd.get('total_liabilities', 0),
        shareholders_equity=fd.get('shareholders_equity', 0),
        revenue=fd.get('revenue', 0),
        gross_profit=fd.get('gross_profit', 0),
        ebit=fd.get('ebit', 0),
        ebitda=fd.get('ebitda', 0),
        net_income=fd.get('net_income', 0),
        interest_expense=fd.get('interest_expense', 0),
        annual_rent=fd.get('annual_rent', 0)
    )
    for fd in data['financial_data']
]

inputs = CreditInputs(
    financial_data=financial_data,
    tenant_name=data.get('tenant_name', 'Tenant'),
    industry=data.get('industry', 'Unknown'),
    years_in_business=data.get('years_in_business', 5),
    credit_score=data.get('credit_score'),
    payment_history=data.get('payment_history', 'good'),
    lease_term_years=data.get('lease_term_years', 5),
    use_criticality=data.get('use_criticality', 'important'),
    industry_stability=data.get('industry_stability', 'moderate'),
    current_security=data.get('current_security', 0),
    security_type=data.get('security_type', 'None')
)

# Run analysis
result = analyze_tenant_credit(inputs)

# Print report
print_credit_report(result)

# Save results to JSON
output_data = {
    'tenant_name': result.tenant_name,
    'analysis_date': result.analysis_date,
    'credit_rating': result.credit_score.credit_rating,
    'credit_score': result.credit_score.total_score,
    'financial_ratios': result.financial_ratios,
    'credit_score_breakdown': result.credit_score.score_breakdown,
    'probability_of_default': result.risk_assessment.probability_of_default,
    'expected_loss': result.risk_assessment.expected_loss,
    'recommended_security': result.risk_assessment.recommended_security,
    'security_type': result.risk_assessment.security_type_recommendation,
    'approval_recommendation': result.approval_recommendation,
    'recommendation_notes': result.recommendation_notes,
    'red_flags': result.red_flags,
    'trend_analysis': {
        'overall_trend': result.trend_analysis.overall_trend,
        'revenue_trend': result.trend_analysis.revenue_trend,
        'profitability_trend': result.trend_analysis.profitability_trend,
        'liquidity_trend': result.trend_analysis.liquidity_trend,
        'leverage_trend': result.trend_analysis.leverage_trend
    }
}

output_file = sys.argv[1].replace('_input.json', '_results.json')
with open(output_file, 'w') as f:
    json.dump(output_data, f, indent=2)

print(f"\n✓ Results saved to: {output_file}")
