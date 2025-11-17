"""
Output Formatting Module
Formats encumbrance discount analysis results into professional reports
"""

from typing import Dict, List, Optional
import sys
import os

# Add Shared_Utils to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../..')))
from Shared_Utils.report_utils import eastern_timestamp, format_markdown_table


def format_report(
    property_data: Dict,
    individual_discounts: List[Dict],
    cumulative_discount: Dict,
    development_potential: Dict,
    residual_value: Dict,
    buyer_pool_analysis: Dict,
    marketability_discount: Dict,
    agricultural_impacts: Optional[Dict] = None,
    paired_sales: Optional[Dict] = None
) -> str:
    """
    Format complete encumbrance discount analysis report.

    Args:
        property_data: Property details
        individual_discounts: Individual encumbrance analyses
        cumulative_discount: Cumulative discount calculation
        development_potential: Development analysis
        residual_value: Residual value calculation
        buyer_pool_analysis: Buyer pool impact
        marketability_discount: Marketability discount
        agricultural_impacts: Optional agricultural income analysis
        paired_sales: Optional paired sales analysis

    Returns:
        Formatted markdown report
    """
    timestamp = eastern_timestamp()

    report = f"""# Encumbrance Discount Valuation Analysis

**Report Date:** {timestamp}

---

## Property Summary

**PIN:** {property_data['pin']}
**Address:** {property_data['address']}
**Total Area:** {property_data['total_area_acres']:.2f} acres
**Unencumbered Value:** ${property_data['unencumbered_value']:,.2f}
**Zoning:** {property_data.get('zoning', 'Not specified')}
**Highest & Best Use:** {property_data.get('highest_best_use', 'Not specified')}

---

## Executive Summary

{_format_executive_summary(
    property_data,
    cumulative_discount,
    residual_value,
    marketability_discount
)}

---

## Individual Encumbrance Analysis

{_format_individual_encumbrances(individual_discounts)}

---

## Cumulative Discount Calculation

{_format_cumulative_discount(cumulative_discount, property_data['unencumbered_value'])}

---

## Development Potential Impact

{_format_development_potential(development_potential)}

---

## Marketability Analysis

{_format_marketability_analysis(buyer_pool_analysis, marketability_discount)}

---

## Final Valuation Summary

{_format_final_valuation(
    property_data['unencumbered_value'],
    cumulative_discount,
    marketability_discount,
    residual_value
)}

"""

    # Add optional sections
    if agricultural_impacts:
        report += f"""---

## Agricultural Income Capitalization

{_format_agricultural_impacts(agricultural_impacts)}

"""

    if paired_sales:
        report += f"""---

## Paired Sales Analysis

{_format_paired_sales(paired_sales)}

"""

    # Add methodology section
    report += """---

## Methodology & Assumptions

### Encumbrance Discount Approach

**Individual Discounts:**
- Transmission easements: 5-15% of affected area value
- Pipeline easements: 10-20% of affected area value
- Drainage easements: 2-8% of affected area value
- Access easements: 2-8% of affected area value
- Conservation easements: 20-50% of affected area value

**Cumulative Discount Formula:**
```
Value × (1-D₁) × (1-D₂) × (1-D₃)
```

This multiplicative approach prevents double-counting and reflects that each encumbrance reduces the remaining value, not the original value.

### Development Potential Adjustment

Development potential considers:
- Restricted buildable area
- Subdivision limitations
- Access and circulation constraints
- Marketability to developers

### Marketability Discount

Marketability discount reflects:
- Reduced buyer pool
- Extended marketing time
- Limited financing options
- Transaction uncertainty

---

## Report Certification

This analysis applies standard valuation methodologies for encumbered properties:
- Percentage of fee method for easement valuation
- Cumulative discount calculation (multiplicative method)
- Development potential analysis (residual method)
- Marketability adjustments based on buyer pool impact

**Prepared by:** Encumbrance Discount Calculator
**Analysis Date:** {timestamp}

---

*This report is for information purposes only and does not constitute a formal appraisal.*
"""

    return report


def format_summary_table(
    property_data: Dict,
    cumulative_discount: Dict,
    residual_value: Dict,
    marketability_discount: Dict
) -> str:
    """
    Format concise summary table for quick reference.

    Args:
        property_data: Property details
        cumulative_discount: Cumulative discount
        residual_value: Residual value
        marketability_discount: Marketability discount

    Returns:
        Formatted summary table
    """
    data = [
        {'item': 'Property', 'value': property_data['address']},
        {'item': 'Total Area', 'value': f"{property_data['total_area_acres']:.2f} acres"},
        {'item': 'Unencumbered Value', 'value': f"${property_data['unencumbered_value']:,.2f}"},
        {'item': 'Encumbrance Discount', 'value': f"{cumulative_discount['cumulative_discount_percentage']:.2f}%"},
        {'item': 'Value After Encumbrances', 'value': f"${residual_value['base_residual_value']:,.2f}"},
        {'item': 'Marketability Discount', 'value': f"{marketability_discount['discount_percentage']:.2f}%"},
        {'item': 'Final Adjusted Value', 'value': f"${marketability_discount['adjusted_value']:,.2f}"},
        {'item': 'Total Discount', 'value': f"${property_data['unencumbered_value'] - marketability_discount['adjusted_value']:,.2f}"},
        {'item': 'Total Discount %', 'value': f"{((property_data['unencumbered_value'] - marketability_discount['adjusted_value']) / property_data['unencumbered_value'] * 100):.2f}%"}
    ]

    return format_markdown_table(
        data=data,
        columns=['item', 'value']
    )


def _format_executive_summary(
    property_data: Dict,
    cumulative_discount: Dict,
    residual_value: Dict,
    marketability_discount: Dict
) -> str:
    """Format executive summary section."""
    total_discount = property_data['unencumbered_value'] - marketability_discount['adjusted_value']
    total_discount_pct = (total_discount / property_data['unencumbered_value'] * 100)

    summary = f"""The subject property at {property_data['address']} comprises {property_data['total_area_acres']:.2f} acres with an unencumbered fee simple value of ${property_data['unencumbered_value']:,.2f}.

The property is affected by multiple encumbrances that reduce its market value through:
1. **Direct encumbrance discounts:** {cumulative_discount['cumulative_discount_percentage']:.2f}% reduction (${property_data['unencumbered_value'] - residual_value['base_residual_value']:,.2f})
2. **Marketability discount:** {marketability_discount['discount_percentage']:.2f}% reduction (${marketability_discount['discount_amount']:,.2f})

**Final Adjusted Value:** ${marketability_discount['adjusted_value']:,.2f}

**Total Discount:** ${total_discount:,.2f} ({total_discount_pct:.2f}% reduction from unencumbered value)
"""
    return summary


def _format_individual_encumbrances(individual_discounts: List[Dict]) -> str:
    """Format individual encumbrance analysis section."""
    output = ""

    for disc in individual_discounts:
        output += f"""### Encumbrance #{disc['number']}: {disc['type'].replace('_', ' ').title()}

**Description:** {disc['description']}
**Affected Area:** {disc['area_acres']:.2f} acres ({disc['area_ratio']*100:.1f}% of property)
**Impact Percentage:** {disc['impact_percentage']:.1f}%
**Typical Range:** {disc['typical_range']['min']:.1f}% - {disc['typical_range']['max']:.1f}%

**Valuation:**
- Encumbered area value: ${disc['encumbered_area_value']:,.2f}
- Discount amount: ${disc['discount_amount']:,.2f}

"""

        # Add metadata if available
        metadata = disc['metadata']
        if any(metadata.values()):
            output += "**Additional Details:**\n"
            if metadata['voltage']:
                output += f"- Voltage: {metadata['voltage']}\n"
            if metadata['width_feet']:
                output += f"- Width: {metadata['width_feet']:.1f} feet\n"
            if metadata['length_feet']:
                output += f"- Length: {metadata['length_feet']:.1f} feet\n"
            output += "\n"

    return output


def _format_cumulative_discount(cumulative_discount: Dict, unencumbered_value: float) -> str:
    """Format cumulative discount calculation section."""
    method = cumulative_discount['method']

    output = f"""**Method:** {method.replace('_', ' ').title()}

**Calculation:**
"""

    # Show step-by-step breakdown
    for step in cumulative_discount['breakdown']:
        output += f"Step {step['step']} - {step['encumbrance_type']}: "
        output += f"{step['discount_percentage']:.1f}% discount → "
        output += f"Value multiplier = {step['remaining_value_multiplier']:.4f} "
        output += f"(cumulative discount: {step['cumulative_discount_so_far']:.2f}%)\n"

    output += f"""
**Final Results:**
- Cumulative discount percentage: {cumulative_discount['cumulative_discount_percentage']:.2f}%
- Value multiplier: {cumulative_discount['value_multiplier']:.4f}
- Total discount amount: ${cumulative_discount['total_discount_amount']:,.2f}
- Value after encumbrances: ${unencumbered_value * cumulative_discount['value_multiplier']:,.2f}
"""

    # Add method comparison if available
    if cumulative_discount.get('method_comparison'):
        output += "\n**Method Comparison:**\n\n"
        comp = cumulative_discount['method_comparison']

        for method_name, method_data in comp.items():
            output += f"- **{method_name.replace('_', ' ').title()}:** "
            output += f"{method_data['discount_percentage']:.2f}% discount "
            output += f"(multiplier: {method_data['value_multiplier']:.4f}) - "
            output += f"{method_data['description']}\n"

    return output


def _format_development_potential(development_potential: Dict) -> str:
    """Format development potential analysis section."""
    output = f"""**Buildable Area Analysis:**
- Total area: {development_potential['total_area_acres']:.2f} acres
- Encumbered area: {development_potential['encumbered_area_acres']:.2f} acres ({development_potential['encumbered_ratio']*100:.1f}%)
- Restricted buildable area: {development_potential['restricted_buildable_area_acres']:.2f} acres
- Effective buildable area: {development_potential['effective_buildable_area_acres']:.2f} acres
- Buildable ratio: {development_potential['buildable_ratio']*100:.1f}%

**Zoning & Use:**
- Zoning: {development_potential['zoning']}
- Highest & Best Use: {development_potential['highest_best_use']}

**Subdivision Impact:**
- Max potential lots (unencumbered): {development_potential['subdivision_impact']['max_potential_lots']}
- Estimated lots (with encumbrances): {development_potential['subdivision_impact']['estimated_lots_with_encumbrance']}
- Lot reduction: {development_potential['subdivision_impact']['lot_reduction']} ({development_potential['subdivision_impact']['lot_reduction_percentage']:.1f}%)
- Feasibility: {development_potential['subdivision_impact']['subdivision_feasibility']}

**Access Impact:**
- Impact level: {development_potential['access_impact']['impact_level']}
- {development_potential['access_impact']['description']}

**Development Constraints:**
"""

    for constraint in development_potential['development_constraints']:
        output += f"- {constraint}\n"

    return output


def _format_marketability_analysis(buyer_pool_analysis: Dict, marketability_discount: Dict) -> str:
    """Format marketability analysis section."""
    output = f"""**Buyer Pool Impact:**
- Overall impact: {buyer_pool_analysis['overall_impact']}
- Buyer pool reduction: {buyer_pool_analysis['buyer_pool_reduction_percentage']}%
- Encumbered ratio: {buyer_pool_analysis['encumbered_ratio']*100:.1f}%

**Impact by Encumbrance:**
"""

    for impact in buyer_pool_analysis['buyer_pool_impacts']:
        output += f"- **{impact['type'].replace('_', ' ').title()}** ({impact['impact_level']}): {impact['description']}\n"

    financing = buyer_pool_analysis['financing_impact']
    output += f"""
**Financing Impact:**
- Impact level: {financing['impact_level']}
- LTV reduction: {financing['ltv_reduction_percentage']}%
- Typical LTV range: {financing['typical_ltv_range']}
- {financing['description']}

**Marketing Challenges:**
"""

    for challenge in buyer_pool_analysis['marketing_challenges']:
        output += f"- {challenge}\n"

    tom = marketability_discount['time_on_market_impact']
    output += f"""
**Time on Market Impact:**
- Baseline: {tom['baseline_days']} days
- Additional time: {tom['additional_days']} days
- Total estimated: {tom['total_days']} days
- {tom['description']}

**Marketability Discount:**
- Method: {marketability_discount['method'].title()}
- Discount percentage: {marketability_discount['discount_percentage']:.2f}%
- Discount amount: ${marketability_discount['discount_amount']:,.2f}
- Adjusted value: ${marketability_discount['adjusted_value']:,.2f}
"""

    return output


def _format_final_valuation(
    unencumbered_value: float,
    cumulative_discount: Dict,
    marketability_discount: Dict,
    residual_value: Dict
) -> str:
    """Format final valuation summary section."""
    data = [
        {'item': 'Unencumbered fee simple value', 'amount': f"${unencumbered_value:,.2f}"},
        {'item': '', 'amount': ''},
        {'item': 'Less: Encumbrance discounts', 'amount': f"-${unencumbered_value - residual_value['base_residual_value']:,.2f}"},
        {'item': f"  ({cumulative_discount['cumulative_discount_percentage']:.2f}%)", 'amount': ''},
        {'item': 'Value after encumbrances', 'amount': f"${residual_value['base_residual_value']:,.2f}"},
        {'item': '', 'amount': ''},
        {'item': 'Less: Marketability discount', 'amount': f"-${marketability_discount['discount_amount']:,.2f}"},
        {'item': f"  ({marketability_discount['discount_percentage']:.2f}%)", 'amount': ''},
        {'item': '', 'amount': ''},
        {'item': '**Final Adjusted Value**', 'amount': f"**${marketability_discount['adjusted_value']:,.2f}**"},
        {'item': '', 'amount': ''},
        {'item': 'Total discount', 'amount': f"${unencumbered_value - marketability_discount['adjusted_value']:,.2f}"},
        {'item': 'Total discount percentage', 'amount': f"{((unencumbered_value - marketability_discount['adjusted_value']) / unencumbered_value * 100):.2f}%"}
    ]

    return format_markdown_table(
        data=data,
        columns=['item', 'amount']
    )


def _format_agricultural_impacts(agricultural_impacts: Dict) -> str:
    """Format agricultural income capitalization section."""
    return f"""**Annual Impacts:**
- Annual crop loss: ${agricultural_impacts['annual_crop_loss']:,.2f}
- Capitalization rate: {agricultural_impacts['cap_rate']*100:.2f}%

**Capitalized Value:**
- Value impact: ${agricultural_impacts['annual_crop_loss'] / agricultural_impacts['cap_rate']:,.2f}

This represents the present value of ongoing annual agricultural productivity losses capitalized in perpetuity.
"""


def _format_paired_sales(paired_sales: Dict) -> str:
    """Format paired sales analysis section."""
    output = f"""**Market Evidence:**
- Encumbered sales analyzed: {paired_sales['encumbered_sales_count']}
- Unencumbered sales analyzed: {paired_sales['unencumbered_sales_count']}

**Average Price per Acre:**
- Unencumbered properties: ${paired_sales['unencumbered_avg_price_per_acre']:,.2f}/acre
- Encumbered properties: ${paired_sales['encumbered_avg_price_per_acre']:,.2f}/acre
- Discount per acre: ${paired_sales['discount_per_acre']:,.2f}/acre

**Market-Derived Discount:** {paired_sales['discount_percentage']:.2f}%

**Comparable Sales:**

**Unencumbered Sales:**
"""

    for sale in paired_sales['unencumbered_sales']:
        output += f"- {sale['address']}: ${sale['sale_price']:,.2f} ({sale['area_acres']:.2f} acres, ${sale['sale_price']/sale['area_acres']:,.2f}/acre) - {sale['sale_date']}\n"

    output += "\n**Encumbered Sales:**\n"

    for sale in paired_sales['encumbered_sales']:
        enc_info = f" - {sale.get('encumbrance_type', 'Unknown')} ({sale.get('encumbrance_area_acres', 0):.2f} acres)" if sale.get('encumbrance_type') else ""
        output += f"- {sale['address']}: ${sale['sale_price']:,.2f} ({sale['area_acres']:.2f} acres, ${sale['sale_price']/sale['area_acres']:,.2f}/acre) - {sale['sale_date']}{enc_info}\n"

    return output
