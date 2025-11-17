"""
Output Formatting Module
Formats calculation results into timestamped markdown reports
"""

from typing import Dict, List, Optional, Any
import sys
import os

# Add parent directory to path for shared utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
from Shared_Utils.report_utils import (
    eastern_timestamp,
    format_markdown_table,
    generate_document_header
)


def format_report(
    site_type: str,
    rent_analysis: Dict[str, Any],
    cap_rate_analysis: Dict[str, Any],
    noi: float,
    income_value: float,
    reconciliation_results: Dict[str, Any]
) -> str:
    """
    Format complete income approach valuation report.

    Args:
        site_type: Type of site (e.g., "Telecom tower site")
        rent_analysis: Market rent analysis results
        cap_rate_analysis: Cap rate selection results
        noi: Net operating income
        income_value: Land value by income approach
        reconciliation_results: Reconciliation and sensitivity analysis

    Returns:
        Markdown formatted report string
    """
    timestamp = eastern_timestamp(include_time=True)

    # ========================================================================
    # Document Header
    # ========================================================================
    report = generate_document_header(
        title="Income Approach Land Valuation",
        subtitle=site_type,
        metadata={
            'valuation_date': eastern_timestamp(include_time=False),
            'report_generated': timestamp,
            'methodology': 'Income Capitalization Approach'
        }
    )

    # ========================================================================
    # Executive Summary
    # ========================================================================
    final_value = reconciliation_results['reconciliation']['final_value']
    concluded_rent = rent_analysis['concluded_market_rent']
    concluded_cap_rate = cap_rate_analysis['concluded_cap_rate']

    report += "## Executive Summary\n\n"
    report += f"**Concluded Land Value:** ${final_value:,.2f}\n\n"
    report += f"**Market Rent:** ${concluded_rent:,.2f} per year\n\n"
    report += f"**Capitalization Rate:** {concluded_cap_rate:.2%}\n\n"
    report += f"**Net Operating Income:** ${noi:,.2f}\n\n"
    report += f"**Methodology:** Income capitalization approach using market rent analysis, "
    report += f"capitalization rate selection from comparable sales, and reconciliation with sales comparison approach.\n\n"

    # ========================================================================
    # Market Rent Analysis
    # ========================================================================
    report += "## Market Rent Analysis\n\n"

    # Comparable rents table
    comp_rents_data = []
    for idx, comp in enumerate(rent_analysis['comparable_rents'], start=1):
        comp_rents_data.append({
            'comparable': f"Comp {idx}",
            'location': comp.get('location', 'Not specified'),
            'annual_rent': comp['annual_rent']
        })

    report += "### Comparable Rents\n\n"
    report += format_markdown_table(
        comp_rents_data,
        ['comparable', 'location', 'annual_rent'],
        ['left', 'left', 'right']
    )
    report += "\n\n"

    # Statistics
    stats = rent_analysis['rent_statistics']
    report += "### Market Rent Statistics\n\n"
    report += f"- **Mean:** ${stats['mean']:,.2f}\n"
    report += f"- **Median:** ${stats['median']:,.2f}\n"
    report += f"- **Range:** ${stats['min']:,.2f} - ${stats['max']:,.2f}\n"
    report += f"- **Number of Comparables:** {stats['count']}\n\n"

    # Conclusion
    report += "### Market Rent Conclusion\n\n"
    report += f"**Concluded Market Rent:** ${concluded_rent:,.2f} per year\n\n"
    report += f"**Method:** {rent_analysis['conclusion_method']}\n\n"
    report += f"**Subject Rent:** ${rent_analysis['subject_rent']:,.2f}\n"
    report += f"**Variance from Market Median:** {rent_analysis['variance_from_market_pct']:+.1f}%\n\n"

    # ========================================================================
    # Capitalization Rate Selection
    # ========================================================================
    report += "## Capitalization Rate Selection\n\n"

    # Method 1: Market Extraction
    report += "### Method 1: Market Extraction\n\n"

    extraction_data = []
    for sale in cap_rate_analysis['market_extraction']['comparable_sales']:
        extraction_data.append({
            'location': sale.get('location', 'Not specified'),
            'sale_price': sale['sale_price'],
            'noi': sale['noi'],
            'cap_rate': f"{sale['cap_rate']:.2%}"
        })

    report += format_markdown_table(
        extraction_data,
        ['location', 'sale_price', 'noi', 'cap_rate'],
        ['left', 'right', 'right', 'center']
    )
    report += "\n\n"

    market_stats = cap_rate_analysis['market_extraction']['statistics']
    report += "**Market Extraction Statistics:**\n"
    report += f"- Mean: {market_stats['mean']:.2%}\n"
    report += f"- Median: {market_stats['median']:.2%}\n"
    report += f"- Range: {market_stats['min']:.2%} - {market_stats['max']:.2%}\n\n"

    # Method 2: Band of Investment (if available)
    if cap_rate_analysis['band_of_investment']:
        report += "### Method 2: Band of Investment\n\n"
        band = cap_rate_analysis['band_of_investment']

        report += f"- **Loan-to-Value (LTV):** {band['ltv']:.1%}\n"
        report += f"- **Debt Yield:** {band['debt_yield']:.2%}\n"
        report += f"- **Equity Yield:** {band['equity_yield']:.2%}\n\n"
        report += f"**Calculation:**\n"
        report += f"```\n"
        report += f"Cap Rate = (LTV × Debt Yield) + (Equity% × Equity Yield)\n"
        report += f"         = ({band['ltv']:.1%} × {band['debt_yield']:.2%}) + ({1-band['ltv']:.1%} × {band['equity_yield']:.2%})\n"
        report += f"         = {band['calculated_cap_rate']:.2%}\n"
        report += f"```\n\n"

    # Method 3: Buildup (if available)
    if cap_rate_analysis['buildup_method']:
        report += "### Method 3: Buildup Method\n\n"
        buildup = cap_rate_analysis['buildup_method']

        report += f"- **Risk-Free Rate:** {buildup['risk_free_rate']:.2%}\n"
        report += f"- **Liquidity Premium:** {buildup['liquidity_premium']:.2%}\n"
        report += f"- **Inflation Premium:** {buildup['inflation_premium']:.2%}\n"
        report += f"- **Business Risk:** {buildup['business_risk']:.2%}\n\n"
        report += f"**Total:** {buildup['calculated_cap_rate']:.2%}\n\n"

    # Conclusion
    report += "### Capitalization Rate Conclusion\n\n"
    report += f"**Concluded Capitalization Rate:** {concluded_cap_rate:.2%}\n\n"
    report += f"**Market Range:** {cap_rate_analysis['cap_rate_range']['low']:.2%} - "
    report += f"{cap_rate_analysis['cap_rate_range']['high']:.2%}\n\n"
    report += f"**Rationale:** {cap_rate_analysis['rationale']}\n\n"

    # ========================================================================
    # NOI Calculation
    # ========================================================================
    report += "## Net Operating Income (NOI)\n\n"
    report += f"```\n"
    report += f"Market Rent:                    ${concluded_rent:>12,.2f}\n"
    report += f"Less: Operating Expenses        ${noi - concluded_rent:>12,.2f}\n"
    report += f"                               {'─' * 20}\n"
    report += f"Net Operating Income:           ${noi:>12,.2f}\n"
    report += f"```\n\n"

    # ========================================================================
    # Land Value by Income Approach
    # ========================================================================
    report += "## Land Value by Income Approach\n\n"
    report += f"```\n"
    report += f"Value = NOI ÷ Capitalization Rate\n"
    report += f"      = ${noi:,.2f} ÷ {concluded_cap_rate:.2%}\n"
    report += f"      = ${income_value:,.2f}\n"
    report += f"```\n\n"

    # ========================================================================
    # Reconciliation
    # ========================================================================
    report += "## Reconciliation with Sales Comparison Approach\n\n"

    recon = reconciliation_results['reconciliation']

    if recon['sales_comparison_value']:
        report += f"- **Income Approach Value:** ${recon['income_approach_value']:,.2f}\n"
        report += f"- **Sales Comparison Value:** ${recon['sales_comparison_value']:,.2f}\n"
        report += f"- **Variance:** ${recon['variance_absolute']:+,.2f} ({recon['variance_percentage']:+.1f}%)\n\n"
        report += f"**Final Value:** ${recon['final_value']:,.2f}\n\n"
        report += f"**Rationale:** {recon['weight_rationale']}\n\n"
    else:
        report += f"**Final Value:** ${recon['final_value']:,.2f}\n\n"
        report += f"**Rationale:** {recon['weight_rationale']}\n\n"

    # ========================================================================
    # Sensitivity Analysis
    # ========================================================================
    report += "## Sensitivity Analysis\n\n"
    report += "### Impact of Capitalization Rate Changes\n\n"

    sensitivity_data = []
    for sens in reconciliation_results['sensitivity_analysis']:
        sensitivity_data.append({
            'cap_rate': f"{sens['adjusted_cap_rate']:.2%}",
            'adjustment': f"{sens['cap_rate_adjustment']:+.2%}",
            'value': sens['value'],
            'variance': f"{sens['variance_percentage']:+.1f}%"
        })

    report += format_markdown_table(
        sensitivity_data,
        ['cap_rate', 'adjustment', 'value', 'variance'],
        ['center', 'center', 'right', 'right']
    )
    report += "\n\n"

    report += "**Note:** Sensitivity analysis shows the impact of ±0.5% changes in capitalization rate "
    report += "on the concluded land value.\n\n"

    # ========================================================================
    # Assumptions and Limiting Conditions
    # ========================================================================
    report += "## Assumptions and Limiting Conditions\n\n"
    report += "1. Market rent analysis based on comparable rental data as provided\n"
    report += "2. Capitalization rate selected from market extraction of comparable sales\n"
    report += "3. Income stream assumed stable and sustainable\n"
    report += "4. Operating expenses based on typical market standards\n"
    report += "5. Valuation assumes fee simple interest\n"
    report += "6. No environmental or legal encumbrances unless noted\n\n"

    # ========================================================================
    # Footer
    # ========================================================================
    report += "---\n\n"
    report += f"*Report generated: {timestamp}*\n\n"
    report += "*Income Approach Land Valuation Calculator v1.0*\n"

    return report
