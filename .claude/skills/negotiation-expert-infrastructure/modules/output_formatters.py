#!/usr/bin/env python3
"""
Output Formatting Module for Negotiation Settlement Calculator
Generate markdown reports and formatted summaries
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Add Shared_Utils to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "Shared_Utils"))
from report_utils import (
    generate_executive_summary,
    format_markdown_table,
    format_financial_summary,
    eastern_timestamp,
    generate_recommendation_section,
    format_risk_assessment,
    generate_action_items,
    generate_document_header
)

logger = logging.getLogger(__name__)


def format_settlement_report(results: Dict, property_description: str = "Property Acquisition") -> str:
    """
    Generate complete settlement analysis report in markdown format.

    Args:
        results: Calculation results dictionary
        property_description: Description of property/acquisition

    Returns:
        Markdown formatted report
    """
    logger.info("Formatting settlement analysis report")

    report = generate_document_header(
        title="Negotiation Settlement Analysis",
        subtitle=property_description,
        metadata={
            'date': eastern_timestamp(include_time=False),
            'analysis_type': 'BATNA/ZOPA Settlement Strategy',
            'calculated': eastern_timestamp(include_time=True)
        }
    )

    # Executive Summary
    exec_summary_data = {
        'issue': property_description,
        'recommendation': results.get('recommendation', {}).get('recommendation', 'Settlement recommended'),
        'rationale': results.get('recommendation', {}).get('rationale', ''),
        'urgency': 'high',
        'financial_impact': results.get('optimal_settlement', {}).get('target', 0)
    }
    report += generate_executive_summary(exec_summary_data, template='decision')

    # BATNA Analysis
    report += _format_batna_section(results.get('batna', {}))

    # ZOPA Analysis
    report += _format_zopa_section(results.get('zopa', {}))

    # Probability-Weighted Scenarios
    if 'scenario_analysis' in results:
        report += _format_scenario_section(results['scenario_analysis'])

    # Optimal Settlement Range
    if 'optimal_settlement' in results:
        report += _format_optimal_settlement_section(results['optimal_settlement'])

    # Holdout Risk Assessment
    if 'holdout_risk' in results:
        report += _format_holdout_risk_section(results['holdout_risk'])

    # Settlement vs. Hearing Analysis
    if 'settlement_vs_hearing' in results:
        report += _format_settlement_comparison_section(results['settlement_vs_hearing'])

    # Concession Strategy
    if 'concession_strategy' in results:
        report += _format_concession_strategy_section(results['concession_strategy'])

    # Negotiation Power Analysis
    if 'power_analysis' in results:
        report += _format_power_analysis_section(results['power_analysis'])

    # Action Items
    if 'action_items' in results:
        report += generate_action_items(results['action_items'], include_timeline=True)

    logger.info("Settlement report formatting complete")

    return report


def format_executive_summary(results: Dict) -> str:
    """
    Generate executive summary section.

    Args:
        results: Calculation results dictionary

    Returns:
        Markdown formatted executive summary
    """
    batna = results.get('batna', {})
    zopa = results.get('zopa', {})
    optimal = results.get('optimal_settlement', {})

    summary = "## Executive Summary\n\n"

    # Key metrics
    summary += "### Key Metrics\n\n"
    summary += f"- **Net BATNA (Hearing Cost):** ${batna.get('net_batna', 0):,.2f}\n"

    if zopa.get('exists'):
        summary += f"- **ZOPA Range:** ${zopa['lower_bound']:,.2f} - ${zopa['upper_bound']:,.2f}\n"
        summary += f"- **Recommended Target:** ${optimal.get('target', zopa.get('midpoint', 0)):,.2f}\n"
    else:
        summary += f"- **No ZOPA:** Gap of ${zopa.get('gap', 0):,.2f}\n"

    summary += "\n"

    # Recommendation
    if zopa.get('exists'):
        summary += "### Recommendation\n\n"
        summary += f"**SETTLE** within the range of ${optimal.get('floor', zopa['lower_bound']):,.2f} to ${optimal.get('ceiling', zopa['upper_bound']):,.2f}\n\n"

        savings = batna.get('net_batna', 0) - optimal.get('target', 0)
        if savings > 0:
            summary += f"Settlement at target saves **${savings:,.2f}** compared to proceeding to hearing.\n\n"
    else:
        summary += "### Recommendation\n\n"
        summary += "**PROCEED TO HEARING** - No zone of possible agreement exists.\n\n"

    return summary


def _format_batna_section(batna: Dict) -> str:
    """Format BATNA analysis section."""
    if not batna:
        return ""

    section = "## BATNA Analysis\n\n"
    section += "**Best Alternative to Negotiated Agreement** (proceeding to expropriation hearing)\n\n"

    section += f"### Expected Hearing Outcome\n\n"
    section += f"- **Expected Award:** ${batna.get('expected_award', 0):,.2f}\n"
    section += f"- **Standard Deviation:** ${batna.get('standard_deviation', 0):,.2f}\n"
    section += f"- **Coefficient of Variation:** {batna.get('coefficient_of_variation', 0):.2%}\n\n"

    # Award range
    award_range = batna.get('award_range', {})
    section += "**Award Range:**\n"
    section += f"- Low: ${award_range.get('low', 0):,.2f}\n"
    section += f"- Mid: ${award_range.get('mid', 0):,.2f}\n"
    section += f"- High: ${award_range.get('high', 0):,.2f}\n\n"

    # Costs
    breakdown = batna.get('breakdown', {})
    section += "### Hearing Costs\n\n"
    section += f"- **Legal Fees:** ${breakdown.get('legal_fees', 0):,.2f}\n"
    section += f"- **Expert Fees:** ${breakdown.get('expert_fees', 0):,.2f}\n"
    section += f"- **Time Costs:** ${breakdown.get('time_cost', 0):,.2f}\n"
    section += f"- **Total Costs:** ${batna.get('total_costs', 0):,.2f}\n\n"

    # Net BATNA
    section += "### Net BATNA (Total Expected Cost)\n\n"
    section += f"**${batna.get('net_batna', 0):,.2f}** (Award + Costs)\n\n"
    section += "This is your walkaway point - you should not settle for more than this amount.\n\n"

    return section


def _format_zopa_section(zopa: Dict) -> str:
    """Format ZOPA analysis section."""
    if not zopa:
        return ""

    section = "## ZOPA Analysis\n\n"
    section += "**Zone of Possible Agreement** - the range where both parties' interests overlap\n\n"

    if zopa.get('exists'):
        section += f"### ZOPA Exists\n\n"
        section += f"- **Lower Bound (Seller Min):** ${zopa['lower_bound']:,.2f}\n"
        section += f"- **Upper Bound (Buyer Max):** ${zopa['upper_bound']:,.2f}\n"
        section += f"- **Midpoint:** ${zopa['midpoint']:,.2f}\n"
        section += f"- **Range:** ${zopa['range']:,.2f}\n\n"

        section += "### Surplus at Midpoint\n\n"
        section += f"- **Buyer Surplus:** ${zopa.get('buyer_surplus_at_midpoint', 0):,.2f}\n"
        section += f"- **Seller Surplus:** ${zopa.get('seller_surplus_at_midpoint', 0):,.2f}\n\n"

        leverage = zopa.get('negotiation_leverage', {})
        section += "### Negotiation Leverage\n\n"
        section += f"- **Buyer:** {leverage.get('buyer', 0):.1%}\n"
        section += f"- **Seller:** {leverage.get('seller', 0):.1%}\n\n"

    else:
        section += f"### No ZOPA\n\n"
        section += f"- **Seller Minimum:** ${zopa['lower_bound']:,.2f}\n"
        section += f"- **Buyer Maximum:** ${zopa['upper_bound']:,.2f}\n"
        section += f"- **Gap:** ${zopa.get('gap', 0):,.2f}\n\n"
        section += f"**{zopa.get('message', 'Settlement unlikely - proceed to hearing')}**\n\n"

    return section


def _format_scenario_section(scenario_analysis: Dict) -> str:
    """Format probability-weighted scenario analysis section."""
    if not scenario_analysis:
        return ""

    section = "## Probability-Weighted Scenarios\n\n"

    section += f"**Expected Value:** ${scenario_analysis.get('expected_value', 0):,.2f}\n\n"

    # Scenarios table
    scenarios = scenario_analysis.get('scenarios', [])
    if scenarios:
        section += format_markdown_table(
            scenarios,
            ['name', 'cost', 'probability'],
            ['left', 'right', 'center']
        )
        section += "\n\n"

    # Best/Worst case
    best = scenario_analysis.get('best_case', {})
    worst = scenario_analysis.get('worst_case', {})

    section += "### Scenario Range\n\n"
    section += f"- **Best Case:** {best.get('name')} - ${best.get('cost', 0):,.2f} ({best.get('probability', 0):.0%} probability)\n"
    section += f"- **Worst Case:** {worst.get('name')} - ${worst.get('cost', 0):,.2f} ({worst.get('probability', 0):.0%} probability)\n"
    section += f"- **Range:** ${scenario_analysis.get('range', 0):,.2f}\n\n"

    section += f"**Standard Deviation:** ${scenario_analysis.get('std_dev', 0):,.2f}\n\n"

    return section


def _format_optimal_settlement_section(optimal: Dict) -> str:
    """Format optimal settlement range section."""
    if not optimal or 'error' in optimal:
        return ""

    section = "## Optimal Settlement Range\n\n"

    section += f"### Recommended Strategy\n\n"
    section += f"- **Opening Offer:** ${optimal.get('opening_offer', 0):,.2f}\n"
    section += f"- **Target Settlement:** ${optimal.get('target', 0):,.2f}\n"
    section += f"- **Floor (Don't go below):** ${optimal.get('floor', 0):,.2f}\n"
    section += f"- **Ceiling (Don't exceed):** ${optimal.get('ceiling', 0):,.2f}\n"
    section += f"- **Walkaway Point:** ${optimal.get('walkaway', 0):,.2f}\n\n"

    section += f"**Strategy:** {optimal.get('strategy', 'N/A')}\n\n"

    room = optimal.get('negotiation_room', {})
    section += "### Negotiation Room\n\n"
    section += f"- **Opening to Target:** ${room.get('from_opening_to_target', 0):,.2f}\n"
    section += f"- **Target to Walkaway:** ${room.get('from_target_to_walkaway', 0):,.2f}\n\n"

    return section


def _format_holdout_risk_section(risk: Dict) -> str:
    """Format holdout risk assessment section."""
    if not risk:
        return ""

    section = "## Holdout Risk Assessment\n\n"

    section += f"### Overall Risk\n\n"
    section += f"- **Risk Score:** {risk.get('total_score', 0)}/30\n"
    section += f"- **Risk Level:** **{risk.get('risk_level', 'UNKNOWN')}**\n"
    section += f"- **Holdout Probability:** {risk.get('holdout_probability', 0):.0%}\n\n"

    breakdown = risk.get('breakdown', {})
    section += "### Risk Breakdown\n\n"
    section += f"- Motivation Score: {breakdown.get('motivation_score', 0)}/12\n"
    section += f"- Sophistication Score: {breakdown.get('sophistication_score', 0)}/10\n"
    section += f"- Alternatives Score: {breakdown.get('alternatives_score', 0)}/8\n\n"

    factors = risk.get('factors', [])
    if factors:
        section += "### Key Risk Factors\n\n"
        for factor in factors:
            section += f"- {factor}\n"
        section += "\n"

    strategies = risk.get('mitigation_strategies', [])
    if strategies:
        section += "### Mitigation Strategies\n\n"
        for strategy in strategies:
            section += f"- {strategy}\n"
        section += "\n"

    return section


def _format_settlement_comparison_section(comparison: Dict) -> str:
    """Format settlement vs. hearing comparison section."""
    if not comparison:
        return ""

    section = "## Settlement vs. Hearing\n\n"

    section += f"### Cost Comparison\n\n"
    section += f"- **Settlement Total Cost:** ${comparison.get('settlement_total_cost', 0):,.2f}\n"
    section += f"- **Hearing Total Cost:** ${comparison.get('hearing_total_cost', 0):,.2f}\n"
    section += f"- **Net Benefit of Settlement:** ${comparison.get('net_benefit_of_settlement', 0):,.2f}\n\n"

    section += f"### Recommendation\n\n"
    section += f"**{comparison.get('recommendation', 'UNKNOWN')}**\n\n"
    section += f"*{comparison.get('rationale', 'N/A')}*\n\n"

    section += f"**Breakeven Settlement:** ${comparison.get('breakeven_settlement', 0):,.2f}\n"
    section += f"**Savings:** {comparison.get('savings_percentage', 0):.1f}%\n\n"

    return section


def _format_concession_strategy_section(strategy: Dict) -> str:
    """Format concession strategy section."""
    if not strategy:
        return ""

    section = "## Concession Strategy\n\n"

    rounds = strategy.get('rounds', [])
    if rounds:
        section += format_markdown_table(
            rounds,
            ['round', 'offer', 'concession', 'concession_pct', 'message'],
            ['center', 'right', 'right', 'center', 'left']
        )
        section += "\n\n"

    section += "### Strategy Notes\n\n"
    for note in strategy.get('strategy_notes', []):
        section += f"- {note}\n"
    section += "\n"

    section += f"**Pattern:** {strategy.get('pattern', 'Unknown')}\n"
    section += f"**Total Movement:** ${strategy.get('total_movement', 0):,.2f}\n\n"

    return section


def _format_power_analysis_section(power: Dict) -> str:
    """Format negotiation power analysis section."""
    if not power:
        return ""

    section = "## Negotiation Power Analysis\n\n"

    section += f"### BATNA Strength\n\n"
    section += f"- **Buyer BATNA Strength:** {power.get('buyer_batna_strength', 0):.1%}\n"
    section += f"- **Seller BATNA Strength:** {power.get('seller_batna_strength', 0):.1%}\n\n"

    section += f"### Power Balance\n\n"
    section += f"- **Advantage:** **{power.get('advantage', 'UNKNOWN')}**\n"

    if power.get('advantage_level'):
        section += f"- **Advantage Level:** {power.get('advantage_level')}\n"

    section += f"- **Advantage Degree:** {power.get('advantage_degree', 0):.1%}\n\n"

    section += f"### Interpretation\n\n"
    section += f"{power.get('interpretation', 'N/A')}\n\n"

    return section


def format_risk_assessment(risks: List[Dict]) -> str:
    """
    Format risk assessment section (wrapper for shared utility).

    Args:
        risks: List of risk dictionaries

    Returns:
        Markdown formatted risk assessment
    """
    from report_utils import format_risk_assessment as shared_format_risk
    return shared_format_risk(risks)
