"""
Capitalization Rate Selection Module
Selects cap rate using market extraction, band of investment, and buildup methods
"""

from typing import Dict, List, Optional, Any
import statistics


def select_capitalization_rate(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Select capitalization rate using three methods:
    1. Market extraction: NOI / Sale Price
    2. Band of investment: (LTV% × Debt Yield) + (Equity% × Equity Yield)
    3. Buildup: Risk-free + Liquidity + Inflation + Business Risk

    Args:
        data: Validated input data dictionary

    Returns:
        Dictionary with:
            - market_extraction: Cap rates from comparable sales
            - band_of_investment: Band of investment calculation (if data provided)
            - buildup_method: Buildup calculation (if data provided)
            - concluded_cap_rate: Final cap rate selection
            - rationale: Explanation of selection
    """
    market_data = data['market_data']
    comparable_sales = market_data['comparable_sales']
    cap_rate_range = market_data['cap_rate_range']

    # ========================================================================
    # METHOD 1: Market Extraction
    # ========================================================================
    extraction_rates = []
    for sale in comparable_sales:
        cap_rate = sale['noi'] / sale['sale_price']
        extraction_rates.append({
            'sale_price': sale['sale_price'],
            'noi': sale['noi'],
            'cap_rate': cap_rate,
            'location': sale.get('location', 'Not specified')
        })

    extracted_cap_rates = [r['cap_rate'] for r in extraction_rates]
    market_extraction_stats = {
        'mean': statistics.mean(extracted_cap_rates),
        'median': statistics.median(extracted_cap_rates),
        'min': min(extracted_cap_rates),
        'max': max(extracted_cap_rates),
        'count': len(extracted_cap_rates)
    }

    # ========================================================================
    # METHOD 2: Band of Investment (if financing data provided)
    # ========================================================================
    band_of_investment = None
    if 'financing' in market_data:
        financing = market_data['financing']
        ltv = financing.get('ltv', 0.75)  # Default 75% LTV
        debt_yield = financing.get('debt_yield', 0.055)  # Default 5.5%
        equity_yield = financing.get('equity_yield', 0.12)  # Default 12%

        band_cap_rate = (ltv * debt_yield) + ((1 - ltv) * equity_yield)
        band_of_investment = {
            'ltv': ltv,
            'debt_yield': debt_yield,
            'equity_yield': equity_yield,
            'calculated_cap_rate': band_cap_rate
        }

    # ========================================================================
    # METHOD 3: Buildup Method (if risk components provided)
    # ========================================================================
    buildup_method = None
    if 'risk_components' in market_data:
        risk = market_data['risk_components']
        risk_free = risk.get('risk_free_rate', 0.04)  # Default 4%
        liquidity = risk.get('liquidity_premium', 0.01)  # Default 1%
        inflation = risk.get('inflation_premium', 0.02)  # Default 2%
        business_risk = risk.get('business_risk', 0.02)  # Default 2%

        buildup_cap_rate = risk_free + liquidity + inflation + business_risk
        buildup_method = {
            'risk_free_rate': risk_free,
            'liquidity_premium': liquidity,
            'inflation_premium': inflation,
            'business_risk': business_risk,
            'calculated_cap_rate': buildup_cap_rate
        }

    # ========================================================================
    # RECONCILE AND CONCLUDE
    # ========================================================================
    # Primary reliance on market extraction
    # Band of investment and buildup as support

    concluded_cap_rate = market_extraction_stats['median']
    rationale = f"Market extraction median ({concluded_cap_rate:.2%}) selected as primary indicator. "

    # Validate against range
    if concluded_cap_rate < cap_rate_range['low']:
        concluded_cap_rate = cap_rate_range['low']
        rationale += f"Adjusted to market range minimum ({cap_rate_range['low']:.2%})."
    elif concluded_cap_rate > cap_rate_range['high']:
        concluded_cap_rate = cap_rate_range['high']
        rationale += f"Adjusted to market range maximum ({cap_rate_range['high']:.2%})."
    else:
        rationale += "Within acceptable market range."

    # Compare with other methods if available
    if band_of_investment:
        variance_band = abs(concluded_cap_rate - band_of_investment['calculated_cap_rate'])
        rationale += f" Band of investment method ({band_of_investment['calculated_cap_rate']:.2%}) "
        rationale += f"variance: {variance_band:.2%}."

    if buildup_method:
        variance_buildup = abs(concluded_cap_rate - buildup_method['calculated_cap_rate'])
        rationale += f" Buildup method ({buildup_method['calculated_cap_rate']:.2%}) "
        rationale += f"variance: {variance_buildup:.2%}."

    return {
        'market_extraction': {
            'comparable_sales': extraction_rates,
            'statistics': market_extraction_stats
        },
        'band_of_investment': band_of_investment,
        'buildup_method': buildup_method,
        'concluded_cap_rate': concluded_cap_rate,
        'cap_rate_range': cap_rate_range,
        'rationale': rationale
    }
