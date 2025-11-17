#!/usr/bin/env python3
"""
Output Formatters Module
Provides functions for formatting environmental risk assessment reports.

Author: Claude Code
Created: 2025-11-17
"""

from typing import Dict, List, Optional
import logging
import sys
import os

# Add Shared_Utils to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from Shared_Utils.report_utils import (
    eastern_timestamp,
    format_markdown_table,
    generate_executive_summary,
    generate_document_header,
    format_number
)

logger = logging.getLogger(__name__)


def format_risk_summary(risk_score: Dict) -> str:
    """
    Format contamination risk summary section.

    Args:
        risk_score: Output from score_contamination_risk()

    Returns:
        Markdown formatted risk summary
    """
    total_score = risk_score.get('total_score', 0)
    risk_level = risk_score.get('risk_level', 'MEDIUM')
    breakdown = risk_score.get('breakdown', {})
    factors = risk_score.get('factors', [])
    recommendations = risk_score.get('recommendations', [])

    summary = "## Contamination Risk Assessment\n\n"
    summary += f"**Overall Risk Level:** {risk_level}\n\n"
    summary += f"**Risk Score:** {total_score}/100\n\n"

    # Score breakdown
    summary += "### Risk Score Breakdown\n\n"
    summary += format_markdown_table(
        [
            {
                'category': 'Contamination Severity',
                'score': breakdown.get('contamination_severity_score', 0),
                'max': 30
            },
            {
                'category': 'Regulatory Complexity',
                'score': breakdown.get('regulatory_complexity_score', 0),
                'max': 25
            },
            {
                'category': 'Remediation Feasibility',
                'score': breakdown.get('remediation_feasibility_score', 0),
                'max': 25
            },
            {
                'category': 'Financial Impact',
                'score': breakdown.get('financial_impact_score', 0),
                'max': 20
            }
        ],
        ['category', 'score', 'max'],
        ['left', 'center', 'center']
    )
    summary += "\n\n"

    # Key factors
    if factors:
        summary += "### Key Risk Factors\n\n"
        for factor in factors:
            summary += f"- {factor}\n"
        summary += "\n"

    # Recommendations
    if recommendations:
        summary += "### Risk Mitigation Recommendations\n\n"
        for i, recommendation in enumerate(recommendations, start=1):
            summary += f"{i}. {recommendation}\n"
        summary += "\n"

    return summary


def format_cleanup_cost_report(
    cleanup_costs: Dict,
    npv_costs: Optional[Dict] = None
) -> str:
    """
    Format cleanup cost analysis section.

    Args:
        cleanup_costs: Output from estimate_cleanup_costs()
        npv_costs: Optional output from calculate_npv_cleanup_costs()

    Returns:
        Markdown formatted cost report
    """
    recommended_scenario = cleanup_costs.get('recommended_scenario', 'remediation')
    scenarios = cleanup_costs.get('scenarios', {})
    total_range = cleanup_costs.get('total_range', {})
    most_likely = cleanup_costs.get('most_likely', 0)

    report = "## Cleanup Cost Analysis\n\n"
    report += f"**Recommended Approach:** {recommended_scenario.replace('_', ' ').title()}\n\n"

    # Cost summary
    report += "### Cost Summary\n\n"
    report += format_markdown_table(
        [
            {
                'measure': 'Low Estimate',
                'amount': total_range.get('low', 0)
            },
            {
                'measure': 'Most Likely',
                'amount': most_likely
            },
            {
                'measure': 'High Estimate',
                'amount': total_range.get('high', 0)
            }
        ],
        ['measure', 'amount'],
        ['left', 'right']
    )
    report += "\n\n"

    # NPV analysis if provided
    if npv_costs:
        report += "### Net Present Value Analysis\n\n"
        report += f"**Discount Rate:** {npv_costs.get('discount_rate', 0)*100:.1f}%\n\n"
        report += f"**Payment Timing:** {npv_costs.get('payment_timing', 'upfront').title()}\n\n"

        report += format_markdown_table(
            [
                {
                    'measure': 'NPV - Low',
                    'amount': npv_costs.get('npv_low', 0)
                },
                {
                    'measure': 'NPV - Most Likely',
                    'amount': npv_costs.get('npv_most_likely', 0)
                },
                {
                    'measure': 'NPV - High',
                    'amount': npv_costs.get('npv_high', 0)
                }
            ],
            ['measure', 'amount'],
            ['left', 'right']
        )
        report += "\n\n"

    # Scenario comparison
    report += "### Cleanup Scenario Comparison\n\n"

    scenario_rows = []
    for scenario_name, scenario_data in scenarios.items():
        scenario_rows.append({
            'scenario': scenario_data.get('description', scenario_name),
            'cost_range': f"${scenario_data.get('cost_low', 0):,.0f} - ${scenario_data.get('cost_high', 0):,.0f}",
            'timeline': f"{scenario_data.get('timeline_months', 0)} months"
        })

    report += format_markdown_table(
        scenario_rows,
        ['scenario', 'cost_range', 'timeline'],
        ['left', 'right', 'center']
    )
    report += "\n\n"

    # Suitable conditions for recommended scenario
    recommended_data = scenarios.get(recommended_scenario, {})
    if 'suitable_for' in recommended_data:
        report += f"**{recommended_scenario.replace('_', ' ').title()} Suitable For:** {recommended_data['suitable_for']}\n\n"

    return report


def format_regulatory_timeline(
    pathway_data: Dict,
    timeline_data: Dict,
    approval_requirements: Optional[List[Dict]] = None
) -> str:
    """
    Format regulatory pathway and timeline section.

    Args:
        pathway_data: Output from determine_regulatory_pathway()
        timeline_data: Output from estimate_regulatory_timeline()
        approval_requirements: Optional output from generate_approval_requirements()

    Returns:
        Markdown formatted regulatory timeline
    """
    pathway = pathway_data.get('pathway', 'Unknown')
    filing_required = pathway_data.get('filing_required', False)
    complexity = pathway_data.get('complexity', 'MEDIUM')

    section = "## Regulatory Pathway Analysis\n\n"
    section += f"**Pathway:** {pathway}\n\n"
    section += f"**Complexity:** {complexity}\n\n"
    section += f"**MOE Filing Required:** {'Yes' if filing_required else 'No'}\n\n"

    # Description
    description = pathway_data.get('description', '')
    if description:
        section += f"**Description:** {description}\n\n"

    # Requirements
    requirements = pathway_data.get('requirements', [])
    if requirements:
        section += "### Regulatory Requirements\n\n"
        for i, req in enumerate(requirements, start=1):
            section += f"{i}. {req}\n"
        section += "\n"

    # Timeline
    total_months = timeline_data.get('total_months', 0)
    total_with_contingency = timeline_data.get('total_with_contingency', 0)
    contingency_months = timeline_data.get('contingency_months', 0)

    if total_months > 0:
        section += "### Timeline Estimate\n\n"
        section += f"**Base Timeline:** {total_months} months\n\n"
        section += f"**With Contingency:** {total_with_contingency} months ({contingency_months} months buffer)\n\n"

        # Phase breakdown
        phases = timeline_data.get('phases', [])
        if phases:
            section += "#### Timeline Phases\n\n"

            phase_rows = []
            cumulative = 0
            for phase in phases:
                duration = phase.get('duration_months', 0)
                cumulative += duration
                phase_rows.append({
                    'phase': phase.get('phase', 'Unknown'),
                    'duration': f"{duration:.1f} months",
                    'cumulative': f"{cumulative:.1f} months",
                    'critical': 'Yes' if phase.get('critical', False) else 'No'
                })

            section += format_markdown_table(
                phase_rows,
                ['phase', 'duration', 'cumulative', 'critical'],
                ['left', 'center', 'center', 'center']
            )
            section += "\n\n"

    # Approval requirements with costs
    if approval_requirements:
        section += "### Approval Requirements & Costs\n\n"

        req_rows = []
        for req in approval_requirements:
            req_rows.append({
                'requirement': req.get('requirement', ''),
                'timing': req.get('timing', 'TBD'),
                'cost': f"${req.get('cost_estimate', 0):,.0f}",
                'mandatory': 'Yes' if req.get('mandatory', False) else 'Optional'
            })

        section += format_markdown_table(
            req_rows,
            ['requirement', 'timing', 'cost', 'mandatory'],
            ['left', 'center', 'right', 'center']
        )
        section += "\n\n"

    return section


def format_liability_recommendations(
    risk_level: str,
    cleanup_costs: Dict,
    pathway_data: Dict
) -> str:
    """
    Format liability allocation recommendations.

    Args:
        risk_level: Overall contamination risk level
        cleanup_costs: Output from estimate_cleanup_costs()
        pathway_data: Output from determine_regulatory_pathway()

    Returns:
        Markdown formatted liability recommendations
    """
    most_likely_cost = cleanup_costs.get('most_likely', 0)
    high_cost = cleanup_costs.get('total_range', {}).get('high', 0)

    section = "## Liability Allocation Recommendations\n\n"

    # Vendor indemnity
    section += "### 1. Vendor Environmental Indemnity\n\n"

    if risk_level == 'HIGH':
        section += "**Recommendation:** Comprehensive vendor indemnity required\n\n"
        section += "**Scope:**\n"
        section += "- All pre-existing environmental conditions\n"
        section += "- Cleanup costs exceeding initial estimates\n"
        section += "- Third-party claims related to contamination\n"
        section += "- Regulatory fines and penalties\n\n"
        section += "**Duration:** Survive closing indefinitely (no sunset clause)\n\n"

    elif risk_level == 'MEDIUM':
        section += "**Recommendation:** Standard vendor indemnity with cap\n\n"
        section += "**Scope:**\n"
        section += "- Pre-existing environmental conditions identified in Phase II\n"
        section += "- Cleanup costs up to agreed cap\n"
        section += "- Regulatory compliance costs\n\n"
        section += f"**Cap:** ${high_cost * 1.5:,.0f} (150% of high estimate)\n\n"
        section += "**Duration:** 5-7 years post-closing\n\n"

    else:  # LOW
        section += "**Recommendation:** Standard environmental representations\n\n"
        section += "**Scope:**\n"
        section += "- Standard environmental reps and warranties\n"
        section += "- No material environmental issues beyond disclosed\n\n"
        section += "**Duration:** 2-3 years post-closing\n\n"

    # Holdback
    section += "### 2. Purchase Price Holdback\n\n"

    if risk_level == 'HIGH':
        holdback_pct = 2.0  # 200%
        holdback_amount = min(most_likely_cost * holdback_pct, high_cost * 1.5)
        section += f"**Recommendation:** ${holdback_amount:,.0f} holdback (200% of estimated cleanup)\n\n"
        section += "**Release Conditions:**\n"
        section += "- Phase 1: 50% released upon MOE Certificate of Property Use\n"
        section += "- Phase 2: 30% released 12 months post-closing if no issues\n"
        section += "- Phase 3: 20% released 24 months post-closing\n\n"

    elif risk_level == 'MEDIUM':
        holdback_pct = 1.5  # 150%
        holdback_amount = most_likely_cost * holdback_pct
        section += f"**Recommendation:** ${holdback_amount:,.0f} holdback (150% of estimated cleanup)\n\n"
        section += "**Release Conditions:**\n"
        section += "- Phase 1: 60% released upon completion of cleanup/RSC filing\n"
        section += "- Phase 2: 40% released 12 months post-closing\n\n"

    else:  # LOW
        section += "**Recommendation:** Minimal or no holdback\n\n"
        section += "Rely on standard representations and warranties.\n\n"

    # Insurance
    section += "### 3. Environmental Insurance\n\n"

    if risk_level == 'HIGH':
        section += "**Recommendation:** Pollution Legal Liability (PLL) Insurance required\n\n"
        section += f"**Coverage Amount:** ${high_cost * 2:,.0f} minimum\n\n"
        section += "**Coverage Period:** 10 years\n\n"
        section += "**Premium Estimate:** $25,000 - $75,000 annually\n\n"
        section += "**Responsibility:** Purchaser (negotiate cost-sharing)\n\n"

    elif risk_level == 'MEDIUM':
        section += "**Recommendation:** Consider PLL Insurance (optional but recommended)\n\n"
        section += f"**Coverage Amount:** ${high_cost * 1.5:,.0f}\n\n"
        section += "**Coverage Period:** 5-7 years\n\n"
        section += "**Premium Estimate:** $15,000 - $35,000 annually\n\n"

    else:  # LOW
        section += "**Recommendation:** Environmental insurance not required\n\n"
        section += "Standard commercial property insurance sufficient.\n\n"

    # Purchase price adjustment
    section += "### 4. Purchase Price Adjustment\n\n"

    if risk_level in ['HIGH', 'MEDIUM']:
        # NPV of cleanup costs as discount
        section += f"**Recommended Discount:** ${most_likely_cost:,.0f} - ${high_cost:,.0f}\n\n"
        section += "**Rationale:** Reflect NPV of cleanup costs and risk premium\n\n"

        # Alternative: As-is sale with larger discount
        alternative_discount = high_cost * 1.3
        section += f"**Alternative (As-Is Sale):** ${alternative_discount:,.0f} discount\n\n"
        section += "**Structure:** Purchaser assumes all environmental risk, larger price reduction in exchange\n\n"

    else:  # LOW
        section += "**Recommended Adjustment:** Minimal (reflect Phase II costs only)\n\n"
        section += "Phase II costs should be credited to purchaser or shared.\n\n"

    return section


def generate_markdown_report(
    site_address: str,
    risk_score: Dict,
    cleanup_costs: Dict,
    npv_costs: Optional[Dict],
    pathway_data: Dict,
    timeline_data: Dict,
    approval_requirements: Optional[List[Dict]],
    phase_1_data: Optional[Dict] = None,
    phase_2_data: Optional[Dict] = None
) -> str:
    """
    Generate complete environmental risk assessment markdown report.

    Args:
        site_address: Property address
        risk_score: Output from score_contamination_risk()
        cleanup_costs: Output from estimate_cleanup_costs()
        npv_costs: Output from calculate_npv_cleanup_costs()
        pathway_data: Output from determine_regulatory_pathway()
        timeline_data: Output from estimate_regulatory_timeline()
        approval_requirements: Output from generate_approval_requirements()
        phase_1_data: Optional Phase I ESA data
        phase_2_data: Optional Phase II ESA data

    Returns:
        Complete markdown report
    """
    # Document header
    report = generate_document_header(
        "Environmental Risk Assessment Report",
        site_address,
        {
            'Date': eastern_timestamp(include_time=False),
            'Risk Level': risk_score.get('risk_level', 'MEDIUM'),
            'Regulatory Pathway': pathway_data.get('pathway', 'TBD')
        }
    )

    # Executive summary
    most_likely_cost = cleanup_costs.get('most_likely', 0)
    timeline_months = timeline_data.get('total_with_contingency', 0)

    exec_summary = generate_executive_summary(
        {
            'issue': f'Environmental risk assessment for {site_address}',
            'recommendation': f"{risk_score.get('risk_level', 'MEDIUM')} environmental risk - {pathway_data.get('pathway', 'TBD')} required",
            'rationale': f"Estimated cleanup: ${most_likely_cost:,.0f}, Timeline: {timeline_months} months",
            'urgency': 'high' if risk_score.get('risk_level') == 'HIGH' else 'medium',
            'financial_impact': most_likely_cost
        },
        template='decision'
    )
    report += exec_summary

    # Phase I/II findings summary
    if phase_1_data or phase_2_data:
        report += "## ESA Findings Summary\n\n"

        if phase_1_data:
            findings = phase_1_data.get('findings', [])
            recs = phase_1_data.get('recs', [])
            report += "### Phase I ESA\n\n"
            report += f"**Findings:** {len(findings)}\n\n"
            report += f"**RECs Identified:** {len(recs)}\n\n"

            if findings:
                report += "**Key Findings:**\n"
                for finding in findings[:5]:  # Top 5
                    report += f"- {finding}\n"
                report += "\n"

        if phase_2_data:
            exceedances = phase_2_data.get('exceedances', [])
            contaminants = phase_2_data.get('contaminants', [])
            report += "### Phase II ESA\n\n"
            report += f"**Exceedances:** {len(exceedances)}\n\n"
            report += f"**Contaminants Detected:** {', '.join(contaminants)}\n\n"

            if exceedances:
                report += "**Exceedances:**\n"
                for exc in exceedances[:5]:  # Top 5
                    report += f"- {exc.get('description', str(exc))}\n"
                report += "\n"

    # Risk assessment
    report += format_risk_summary(risk_score)

    # Cleanup costs
    report += format_cleanup_cost_report(cleanup_costs, npv_costs)

    # Regulatory pathway
    report += format_regulatory_timeline(pathway_data, timeline_data, approval_requirements)

    # Liability recommendations
    report += format_liability_recommendations(
        risk_score.get('risk_level', 'MEDIUM'),
        cleanup_costs,
        pathway_data
    )

    # Footer
    report += "---\n\n"
    report += f"*Report generated: {eastern_timestamp(include_time=True)}*\n\n"
    report += "*Environmental Risk Assessment Calculator v1.0*\n"

    return report
