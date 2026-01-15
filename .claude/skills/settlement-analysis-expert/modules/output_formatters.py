#!/usr/bin/env python3
"""
Output formatting for settlement analysis reports.
Generate markdown reports with executive summaries and recommendations.
"""

import sys
from pathlib import Path
from typing import Dict, List

# Add Shared_Utils to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'Shared_Utils'))

from report_utils import (
    generate_executive_summary,
    format_markdown_table,
    eastern_timestamp,
    generate_document_header,
    format_number
)


def format_analysis_report(
    case_id: str,
    analysis: Dict,
    hearing_batna: Dict,
    settlement_scenarios: List[Dict],
    zopa_analysis: Dict = None,
    owner_risk: Dict = None,
    litigation_risk: Dict = None
) -> str:
    """
    Format comprehensive settlement analysis report.

    Args:
        case_id: Case identifier
        analysis: Settlement vs. hearing analysis
        hearing_batna: BATNA analysis
        settlement_scenarios: List of settlement scenarios
        zopa_analysis: Optional ZOPA analysis
        owner_risk: Optional owner holdout risk assessment
        litigation_risk: Optional litigation risk assessment

    Returns:
        Markdown formatted report
    """
    report = []

    # Header
    report.append(generate_document_header(
        title="Settlement Analysis Report",
        subtitle=f"Case {case_id}",
        metadata={
            'generated': eastern_timestamp(),
            'recommendation': analysis['recommendation']
        }
    ))

    # Executive Summary
    exec_summary = generate_executive_summary({
        'issue': f'Settlement negotiation for {case_id}',
        'recommendation': analysis['recommendation'],
        'rationale': analysis['rationale'],
        'urgency': 'high',
        'financial_impact': analysis['settlement_total']
    })
    report.append(exec_summary)

    # Recommendation Detail
    report.append("## Recommendation Detail\n\n")
    report.append(f"**Decision:** {analysis['recommendation']}\n\n")
    report.append(f"**Confidence Level:** {analysis['confidence']}\n\n")
    report.append(f"**Rationale:** {analysis['rationale']}\n\n")

    # Financial Summary
    report.append("## Financial Summary\n\n")
    report.append(format_markdown_table(
        [
            {
                'scenario': 'Settlement',
                'total_cost': analysis['settlement_total'],
                'probability': 'Deterministic',
                'notes': 'Current offer plus legal fees'
            },
            {
                'scenario': 'Hearing',
                'total_cost': analysis['hearing_total'],
                'probability': 'Probability-Weighted',
                'notes': 'Expected award plus costs'
            }
        ],
        ['scenario', 'total_cost', 'probability', 'notes'],
        ['left', 'right', 'center', 'left']
    ))
    report.append("\n\n")

    report.append(f"**Net Benefit of Settlement:** {format_number(analysis['net_benefit'], 'currency')}\n\n")
    report.append(f"**Savings Percentage:** {analysis['savings_percentage']:.1f}%\n\n")

    # Hearing Risk Analysis
    report.append("## Hearing Risk Analysis\n\n")
    report.append(f"**Expected Award:** {format_number(hearing_batna['expected_award'], 'currency')}\n\n")
    report.append(f"**Total Costs:** {format_number(hearing_batna['total_costs'], 'currency')}\n\n")
    report.append(f"**Net BATNA:** {format_number(hearing_batna['net_batna'], 'currency')}\n\n")

    report.append("**Award Range:**\n")
    award_range = hearing_batna.get('award_range', {})
    report.append(f"- Low: {format_number(award_range.get('low', 0), 'currency')}\n")
    report.append(f"- Mid: {format_number(award_range.get('mid', 0), 'currency')}\n")
    report.append(f"- High: {format_number(award_range.get('high', 0), 'currency')}\n\n")

    report.append(f"**Uncertainty (Std Dev):** {format_number(hearing_batna.get('standard_deviation', 0), 'currency')}\n\n")

    # Settlement Scenarios
    if settlement_scenarios:
        report.append("## Settlement Scenarios\n\n")
        report.append(format_markdown_table(
            [
                {
                    'scenario': s['name'],
                    'cost': s['cost'],
                    'probability': f"{s['probability']*100:.0f}%",
                    'description': s['description']
                }
                for s in settlement_scenarios
            ],
            ['scenario', 'cost', 'probability', 'description'],
            ['left', 'right', 'center', 'left']
        ))
        report.append("\n\n")

    # ZOPA Analysis
    if zopa_analysis:
        report.append("## Zone of Possible Agreement (ZOPA)\n\n")
        zopa = zopa_analysis.get('zopa', {})

        if zopa.get('exists'):
            report.append(f"**ZOPA Exists:** Yes\n\n")
            report.append(f"**Range:** {format_number(zopa['lower_bound'], 'currency')} - {format_number(zopa['upper_bound'], 'currency')}\n\n")
            report.append(f"**Midpoint:** {format_number(zopa['midpoint'], 'currency')}\n\n")

            optimal = zopa_analysis.get('optimal_range', {})
            if optimal and 'target' in optimal:
                report.append("**Optimal Settlement Range:**\n")
                report.append(f"- Opening Offer: {format_number(optimal['opening_offer'], 'currency')}\n")
                report.append(f"- Target: {format_number(optimal['target'], 'currency')}\n")
                report.append(f"- Walkaway: {format_number(optimal['walkaway'], 'currency')}\n\n")
        else:
            report.append(f"**ZOPA Exists:** No\n\n")
            report.append(f"**Gap:** {format_number(zopa.get('gap', 0), 'currency')}\n\n")
            report.append("**Implication:** Settlement may not be viable at current positions\n\n")

    # Owner Risk Assessment
    if owner_risk:
        report.append("## Owner Holdout Risk Assessment\n\n")
        report.append(f"**Risk Level:** {owner_risk.get('risk_level', 'MEDIUM')}\n\n")
        report.append(f"**Holdout Probability:** {owner_risk.get('holdout_probability', 0.3)*100:.0f}%\n\n")
        report.append(f"**Risk Score:** {owner_risk.get('total_score', 0)}/30\n\n")

        breakdown = owner_risk.get('breakdown', {})
        if breakdown:
            report.append("**Score Breakdown:**\n")
            report.append(f"- Motivation: {breakdown.get('motivation_score', 0)}\n")
            report.append(f"- Sophistication: {breakdown.get('sophistication_score', 0)}\n")
            report.append(f"- Alternatives: {breakdown.get('alternatives_score', 0)}\n\n")

        factors = owner_risk.get('factors', [])
        if factors:
            report.append("**Key Risk Factors:**\n")
            for factor in factors:
                report.append(f"- {factor}\n")
            report.append("\n")

        mitigation = owner_risk.get('mitigation_strategies', [])
        if mitigation:
            report.append("**Mitigation Strategies:**\n")
            for strategy in mitigation:
                report.append(f"- {strategy}\n")
            report.append("\n")

    # Litigation Risk Assessment
    if litigation_risk:
        report.append("## Litigation Risk Assessment\n\n")
        report.append(f"**Litigation Probability:** {litigation_risk.get('litigation_probability', 0.5)*100:.0f}%\n\n")
        report.append(f"**Expected Duration:** {litigation_risk.get('expected_duration_months', 12):.1f} months\n\n")
        report.append(f"**Expected Cost:** {format_number(litigation_risk.get('expected_cost', 0), 'currency')}\n\n")

        risk_factors = litigation_risk.get('risk_factors', [])
        if risk_factors:
            report.append("**Risk Factors:**\n")
            for factor in risk_factors:
                report.append(f"- {factor}\n")
            report.append("\n")

    return "".join(report)


def format_executive_summary(analysis: Dict, hearing_batna: Dict) -> str:
    """
    Format concise executive summary (1-2 paragraphs).

    Args:
        analysis: Settlement vs. hearing analysis
        hearing_batna: BATNA analysis

    Returns:
        Markdown formatted executive summary
    """
    return generate_executive_summary({
        'issue': 'Settlement vs. Hearing Decision',
        'recommendation': analysis['recommendation'],
        'rationale': analysis['rationale'],
        'urgency': 'high',
        'financial_impact': analysis['settlement_total']
    })


def format_scenario_comparison(
    settlement_scenarios: List[Dict],
    hearing_batna: Dict
) -> str:
    """
    Format scenario comparison table.

    Args:
        settlement_scenarios: List of settlement scenarios
        hearing_batna: BATNA analysis

    Returns:
        Markdown formatted scenario comparison
    """
    # Combine scenarios
    all_scenarios = settlement_scenarios.copy()
    all_scenarios.append({
        'name': 'Proceed to Hearing',
        'cost': hearing_batna['net_batna'],
        'probability': 0,
        'description': 'Expected value of hearing outcome'
    })

    comparison = "## Scenario Comparison\n\n"
    comparison += format_markdown_table(
        [
            {
                'scenario': s['name'],
                'cost': s['cost'],
                'probability': f"{s['probability']*100:.0f}%" if s['probability'] > 0 else 'N/A',
                'description': s.get('description', '')
            }
            for s in all_scenarios
        ],
        ['scenario', 'cost', 'probability', 'description'],
        ['left', 'right', 'center', 'left']
    )

    return comparison
