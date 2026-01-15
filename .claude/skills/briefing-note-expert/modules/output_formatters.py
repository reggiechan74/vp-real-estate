#!/usr/bin/env python3
"""
Briefing Note Output Formatting Module
Generates executive-ready markdown briefing notes
"""

from typing import Dict, List, Optional
import sys
import os

# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
skills_dir = os.path.dirname(os.path.dirname(current_dir))
root_dir = os.path.dirname(os.path.dirname(skills_dir))
sys.path.insert(0, root_dir)

from Shared_Utils.report_utils import (
    generate_document_header,
    format_financial_summary,
    format_risk_assessment,
    generate_action_items,
    format_markdown_table
)

from .analysis import (
    analyze_decision_urgency,
    analyze_alternatives,
    analyze_strategic_alignment,
    generate_executive_recommendation,
    calculate_overall_risk_score
)


def format_issue_section(data: Dict) -> str:
    """
    Format the issue/decision required section.

    Args:
        data: Briefing note input data

    Returns:
        Formatted markdown section
    """
    issue = data.get('issue', '')
    urgency_analysis = analyze_decision_urgency(data)

    section = "## Issue / Decision Required\n\n"
    section += f"{issue}\n\n"

    # Add urgency indicator
    urgency_level = urgency_analysis['urgency_level']
    urgency_emoji = {
        'low': '🟢',
        'medium': '🟡',
        'high': '🔴'
    }

    section += f"**Urgency:** {urgency_emoji.get(urgency_level, '')} {urgency_level.upper()}"

    if urgency_analysis['key_constraints']:
        section += f" - {urgency_analysis['key_constraints'][0]}"

    section += "\n\n"

    return section


def format_background_section(data: Dict) -> str:
    """
    Format background and context section.

    Args:
        data: Briefing note input data

    Returns:
        Formatted markdown section
    """
    background = data.get('background', {})
    context = background.get('context', '')
    project_timeline = background.get('project_timeline', {})
    stakeholders = background.get('stakeholders', [])

    section = "## Background and Context\n\n"

    # Add context
    section += f"{context}\n\n"

    # Add timeline if available
    if project_timeline:
        section += "### Project Timeline\n\n"

        if 'start_date' in project_timeline:
            section += f"**Project Start:** {project_timeline['start_date']}\n\n"

        if 'critical_deadline' in project_timeline:
            section += f"**Critical Deadline:** {project_timeline['critical_deadline']}\n\n"

        # Add key milestones
        milestones = project_timeline.get('key_milestones', [])
        if milestones:
            section += "**Key Milestones:**\n\n"

            milestone_data = []
            for m in milestones:
                status_icon = {
                    'completed': '✅',
                    'in_progress': '🔄',
                    'pending': '⏳'
                }
                milestone_data.append({
                    'milestone': m.get('milestone', ''),
                    'date': m.get('date', ''),
                    'status': f"{status_icon.get(m.get('status', 'pending'), '')} {m.get('status', 'pending').replace('_', ' ').title()}"
                })

            section += format_markdown_table(
                milestone_data,
                ['milestone', 'date', 'status'],
                ['left', 'center', 'center']
            )
            section += "\n\n"

    # Add stakeholders if available
    if stakeholders:
        section += "### Key Stakeholders\n\n"

        stakeholder_data = []
        for s in stakeholders:
            position_icon = {
                'supportive': '✅',
                'neutral': '➖',
                'opposed': '❌',
                'unknown': '❓'
            }
            stakeholder_data.append({
                'name': s.get('name', ''),
                'role': s.get('role', ''),
                'position': f"{position_icon.get(s.get('position', 'neutral'), '')} {s.get('position', 'neutral').title()}"
            })

        section += format_markdown_table(
            stakeholder_data,
            ['name', 'role', 'position'],
            ['left', 'left', 'center']
        )
        section += "\n\n"

    return section


def format_analysis_section(data: Dict) -> str:
    """
    Format analysis section with financial summary and alternatives.

    Args:
        data: Briefing note input data

    Returns:
        Formatted markdown section
    """
    section = "## Analysis\n\n"

    # Financial summary
    financial = data.get('financial_summary', {})
    section += format_financial_summary(financial, 'detailed')
    section += "\n"

    # Budget comparison if available
    budget_comparison = financial.get('budget_comparison', {})
    if budget_comparison:
        section += "### Budget Comparison\n\n"

        approved = budget_comparison.get('approved_budget', 0)
        variance = budget_comparison.get('variance', 0)
        variance_pct = budget_comparison.get('variance_pct', 0)

        section += f"**Approved Budget:** ${approved:,.2f}\n\n"
        section += f"**Total Cost:** ${financial.get('total_cost', 0):,.2f}\n\n"

        variance_indicator = "⚠️" if variance > 0 else "✅"
        section += f"**Variance:** {variance_indicator} ${abs(variance):,.2f} "
        section += f"({'over' if variance > 0 else 'under'} budget, {abs(variance_pct):.1f}%)\n\n"

    # Funding source
    funding = financial.get('funding_source', '')
    if funding:
        section += f"**Funding Source:** {funding}\n\n"

    # Strategic analysis
    analysis_data = data.get('analysis', {})
    strategic_analysis = analyze_strategic_alignment(data)

    if strategic_analysis['alignment_summary']:
        section += "### Strategic Alignment\n\n"
        section += f"{strategic_analysis['alignment_summary']}\n\n"

    # Alternatives comparison
    alternatives_analysis = analyze_alternatives(data)

    if alternatives_analysis['alternatives_count'] > 0:
        section += "### Alternatives Considered\n\n"

        alternatives = analysis_data.get('alternatives_considered', [])

        for alt in alternatives:
            section += f"**{alt.get('alternative', 'Unnamed Alternative')}**\n\n"

            if alt.get('cost'):
                cost_diff = alt['cost'] - financial.get('total_cost', 0)
                cost_diff_pct = (cost_diff / financial.get('total_cost', 1) * 100)
                section += f"- Cost: ${alt['cost']:,.2f} "
                if cost_diff != 0:
                    section += f"({'$' + f'{abs(cost_diff):,.0f}' + ' more' if cost_diff > 0 else '$' + f'{abs(cost_diff):,.0f}' + ' less'}, {abs(cost_diff_pct):.1f}%)"
                section += "\n"

            if alt.get('timeline_impact'):
                section += f"- Timeline Impact: {alt['timeline_impact']}\n"

            if alt.get('pros'):
                section += f"- Pros: {', '.join(alt['pros'])}\n"

            if alt.get('cons'):
                section += f"- Cons: {', '.join(alt['cons'])}\n"

            section += "\n"

        # Add comparison table
        if alternatives_analysis['cost_comparison']:
            section += "**Cost Comparison Summary:**\n\n"
            section += format_markdown_table(
                alternatives_analysis['cost_comparison'],
                ['alternative', 'cost', 'cost_vs_recommended', 'timeline_impact'],
                ['left', 'right', 'right', 'left']
            )
            section += "\n\n"

    return section


def format_recommendation_section(data: Dict) -> str:
    """
    Format recommendation section.

    Args:
        data: Briefing note input data

    Returns:
        Formatted markdown section
    """
    return generate_executive_recommendation(data)


def format_risk_section(data: Dict) -> str:
    """
    Format risk assessment section.

    Args:
        data: Briefing note input data

    Returns:
        Formatted markdown section
    """
    risks = data.get('risks', [])

    if not risks:
        return "## Risk Assessment\n\n*No significant risks identified.*\n\n"

    # Calculate overall risk score
    overall = calculate_overall_risk_score(risks)

    section = "## Risk Assessment\n\n"
    section += f"**Overall Risk Level:** {overall['risk_level']} (Score: {overall['overall_score']}/100)\n\n"

    if overall['critical_count'] + overall['high_count'] + overall['medium_count'] + overall['low_count'] > 0:
        section += f"**Risk Summary:** "
        summary_parts = []
        if overall['critical_count'] > 0:
            summary_parts.append(f"{overall['critical_count']} Critical")
        if overall['high_count'] > 0:
            summary_parts.append(f"{overall['high_count']} High")
        if overall['medium_count'] > 0:
            summary_parts.append(f"{overall['medium_count']} Medium")
        if overall['low_count'] > 0:
            summary_parts.append(f"{overall['low_count']} Low")

        section += ", ".join(summary_parts) + "\n\n"

    # Use shared risk formatting
    section += format_risk_assessment(risks)

    return section


def format_action_items_section(data: Dict) -> str:
    """
    Format action items section.

    Args:
        data: Briefing note input data

    Returns:
        Formatted markdown section
    """
    items = data.get('action_items', [])

    if not items:
        return ""

    return generate_action_items(items, include_timeline=True)


def format_approvals_section(data: Dict) -> str:
    """
    Format approvals required section.

    Args:
        data: Briefing note input data

    Returns:
        Formatted markdown section
    """
    approvals = data.get('approvals_required', [])

    if not approvals:
        return ""

    section = "## Approvals Required\n\n"

    approval_data = []
    for approval in approvals:
        approval_data.append({
            'authority': approval.get('authority', ''),
            'level': approval.get('level', ''),
            'threshold': f"${approval.get('threshold', 0):,.0f}" if 'threshold' in approval else 'N/A',
            'timing': approval.get('timing', 'TBD')
        })

    section += format_markdown_table(
        approval_data,
        ['authority', 'level', 'threshold', 'timing'],
        ['left', 'left', 'right', 'left']
    )
    section += "\n\n"

    return section


def generate_briefing_note(data: Dict) -> str:
    """
    Generate complete briefing note in markdown format.

    Args:
        data: Briefing note input data

    Returns:
        Complete markdown briefing note
    """
    # Generate header
    metadata = data.get('metadata', {})
    project_name = data.get('project_name', 'Project')

    header_metadata = {}
    if 'date' in metadata:
        header_metadata['Date'] = metadata['date']
    if 'prepared_by' in metadata:
        header_metadata['Prepared By'] = metadata['prepared_by']
    if 'department' in metadata:
        header_metadata['Department'] = metadata['department']
    if 'classification' in metadata:
        header_metadata['Classification'] = metadata['classification']

    briefing_note = generate_document_header(
        title="EXECUTIVE BRIEFING NOTE",
        subtitle=project_name,
        metadata=header_metadata if header_metadata else None
    )

    # Add sections
    briefing_note += format_issue_section(data)
    briefing_note += format_background_section(data)
    briefing_note += format_analysis_section(data)
    briefing_note += format_recommendation_section(data)
    briefing_note += format_risk_section(data)

    approvals = format_approvals_section(data)
    if approvals:
        briefing_note += approvals

    action_items = format_action_items_section(data)
    if action_items:
        briefing_note += action_items

    # Add distribution list if provided
    distribution = metadata.get('distribution_list', [])
    if distribution:
        briefing_note += "## Distribution\n\n"
        for recipient in distribution:
            briefing_note += f"- {recipient}\n"
        briefing_note += "\n"

    return briefing_note
