"""
Income Reconciliation Module
Reconciles income approach value with sales comparison approach
"""

from typing import Dict, List, Optional, Any


def reconcile_with_sales_comparison(
    noi: float,
    cap_rate: float,
    income_value: float,
    data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Reconcile income approach value with sales comparison approach.

    Args:
        noi: Net operating income
        cap_rate: Concluded capitalization rate
        income_value: Value by income approach (NOI / Cap Rate)
        data: Input data dictionary

    Returns:
        Dictionary with:
            - income_approach_value: Value by income approach
            - sales_comparison_value: Value by sales comparison (if provided)
            - reconciliation: Variance analysis and final value
            - sensitivity_analysis: Impact of cap rate changes
    """
    market_data = data['market_data']

    # ========================================================================
    # Sales Comparison Value (if provided)
    # ========================================================================
    sales_comparison_value = None
    if 'sales_comparison_value' in market_data:
        sales_comparison_value = market_data['sales_comparison_value']
    elif 'comparable_sales' in market_data and market_data['comparable_sales']:
        # Estimate from comparable sales average
        sale_prices = [sale['sale_price'] for sale in market_data['comparable_sales']]
        sales_comparison_value = sum(sale_prices) / len(sale_prices)

    # ========================================================================
    # Reconciliation
    # ========================================================================
    reconciliation = {
        'income_approach_value': income_value
    }

    if sales_comparison_value:
        variance = income_value - sales_comparison_value
        variance_pct = (variance / sales_comparison_value) * 100

        # Determine which value to give more weight
        if abs(variance_pct) <= 10:
            # Within 10% - use income approach
            final_value = income_value
            weight_rationale = "Income and sales comparison approaches within 10%. Income approach selected."
        elif abs(variance_pct) <= 20:
            # 10-20% variance - use average
            final_value = (income_value + sales_comparison_value) / 2
            weight_rationale = "Income and sales comparison approaches differ by 10-20%. Average of both methods used."
        else:
            # >20% variance - investigate
            final_value = income_value
            weight_rationale = f"Income and sales comparison approaches differ by {abs(variance_pct):.1f}%. Further investigation recommended. Income approach used pending review."

        reconciliation.update({
            'sales_comparison_value': sales_comparison_value,
            'variance_absolute': variance,
            'variance_percentage': variance_pct,
            'final_value': final_value,
            'weight_rationale': weight_rationale
        })
    else:
        reconciliation.update({
            'sales_comparison_value': None,
            'final_value': income_value,
            'weight_rationale': "Sales comparison data not provided. Income approach value used."
        })

    # ========================================================================
    # Sensitivity Analysis
    # ========================================================================
    # Show impact of ±0.5% cap rate change
    sensitivity = []
    for adjustment in [-0.005, -0.0025, 0, 0.0025, 0.005]:
        adjusted_cap_rate = cap_rate + adjustment
        adjusted_value = noi / adjusted_cap_rate
        variance_from_base = adjusted_value - income_value

        sensitivity.append({
            'cap_rate_adjustment': adjustment,
            'adjusted_cap_rate': adjusted_cap_rate,
            'value': adjusted_value,
            'variance_from_base': variance_from_base,
            'variance_percentage': (variance_from_base / income_value) * 100
        })

    return {
        'reconciliation': reconciliation,
        'sensitivity_analysis': sensitivity
    }
