#!/usr/bin/env python3
"""
Board Memo Output Formatters Module
Formats different sections of board approval memo including alternatives analysis,
timeline visualization, and financial summary tables.
"""

from typing import Dict, List, Optional


def format_alternatives_analysis(alternatives: List[Dict]) -> str:
    """
    Format alternatives considered section.

    Args:
        alternatives: List of alternative approach dicts
            [
                {
                    'name': 'Alternative A',
                    'pros': ['Pro 1', 'Pro 2'],
                    'cons': ['Con 1', 'Con 2'],
                    'rejected_reason': 'Why rejected'
                }
            ]

    Returns:
        Formatted markdown text
    """
    if not alternatives:
        return ""

    text = "## Alternatives Considered\n\n"

    for idx, alt in enumerate(alternatives, start=1):
        text += f"### Alternative {idx}: {alt.get('name', 'Unnamed')}\n\n"

        # Pros
        if 'pros' in alt and alt['pros']:
            text += "**Advantages:**\n"
            for pro in alt['pros']:
                text += f"- {pro}\n"
            text += "\n"

        # Cons
        if 'cons' in alt and alt['cons']:
            text += "**Disadvantages:**\n"
            for con in alt['cons']:
                text += f"- {con}\n"
            text += "\n"

        # Rejection reason
        if 'rejected_reason' in alt:
            text += f"**Reason Not Selected:** {alt['rejected_reason']}\n\n"

        text += "---\n\n"

    return text


def format_timeline_section(timeline: Optional[Dict]) -> str:
    """
    Format timeline and milestones section.

    Args:
        timeline: Timeline dict with milestones
            {
                'decision_deadline': '2025-12-15',
                'implementation_start': '2026-01-01',
                'key_milestones': [...]
            }

    Returns:
        Formatted markdown text
    """
    if not timeline:
        return ""

    text = "## Timeline\n\n"

    # Decision deadline
    if 'decision_deadline' in timeline:
        text += f"**Board Decision Required By:** {timeline['decision_deadline']}\n\n"

    # Implementation start
    if 'implementation_start' in timeline:
        text += f"**Planned Implementation Start:** {timeline['implementation_start']}\n\n"

    # Key milestones
    if 'key_milestones' in timeline and timeline['key_milestones']:
        text += "### Key Milestones\n\n"

        # Sort by target date
        milestones = sorted(
            timeline['key_milestones'],
            key=lambda x: x.get('target_date', '9999-12-31')
        )

        for milestone in milestones:
            milestone_name = milestone.get('milestone', 'Unnamed milestone')
            target_date = milestone.get('target_date', 'TBD')
            is_critical = milestone.get('is_critical', False)

            critical_marker = " *(Critical Path)*" if is_critical else ""
            text += f"- **{milestone_name}**: {target_date}{critical_marker}\n"

        text += "\n"

    return text


def format_npv_analysis(npv_data: Optional[Dict]) -> str:
    """
    Format NPV analysis section if present.

    Args:
        npv_data: NPV analysis dict
            {
                'discount_rate': 0.08,
                'cash_flows': [-100000, 30000, 30000, 30000],
                'npv': 13723,
                'irr': 0.1524
            }

    Returns:
        Formatted markdown text
    """
    if not npv_data:
        return ""

    text = "### Financial Analysis (NPV)\n\n"

    # Discount rate
    if 'discount_rate' in npv_data:
        text += f"**Discount Rate:** {npv_data['discount_rate']:.2%}\n\n"

    # NPV
    if 'npv' in npv_data:
        npv_value = npv_data['npv']
        npv_indicator = "POSITIVE" if npv_value > 0 else "NEGATIVE"
        text += f"**Net Present Value:** ${npv_value:,.2f} ({npv_indicator})\n\n"

    # IRR
    if 'irr' in npv_data:
        text += f"**Internal Rate of Return:** {npv_data['irr']:.2%}\n\n"

    # Cash flows table
    if 'cash_flows' in npv_data:
        text += "**Projected Cash Flows:**\n\n"
        text += "| Year | Cash Flow |\n"
        text += "| :---: | ---: |\n"

        for idx, cf in enumerate(npv_data['cash_flows']):
            year_label = "Initial" if idx == 0 else f"Year {idx}"
            text += f"| {year_label} | ${cf:,.2f} |\n"

        text += "\n"

    return text


def format_payback_analysis(financial: Dict) -> str:
    """
    Format payback period analysis if present.

    Args:
        financial: Financial data dict

    Returns:
        Formatted markdown text
    """
    if 'payback_period_years' not in financial:
        return ""

    payback = financial['payback_period_years']
    text = f"**Payback Period:** {payback:.1f} years\n\n"

    return text


def format_metadata_header(metadata: Optional[Dict]) -> str:
    """
    Format document metadata header.

    Args:
        metadata: Metadata dict
            {
                'prepared_by': 'Acquisition Team',
                'date_prepared': '2025-11-16',
                'board_meeting_date': '2025-12-15',
                'confidentiality': 'confidential'
            }

    Returns:
        Formatted markdown text
    """
    if not metadata:
        return ""

    text = "---\n\n"

    if 'prepared_by' in metadata:
        text += f"**Prepared By:** {metadata['prepared_by']}\n\n"

    if 'date_prepared' in metadata:
        text += f"**Date Prepared:** {metadata['date_prepared']}\n\n"

    if 'board_meeting_date' in metadata:
        text += f"**Board Meeting Date:** {metadata['board_meeting_date']}\n\n"

    if 'confidentiality' in metadata:
        confidentiality_labels = {
            'public': 'Public',
            'confidential': 'Confidential',
            'restricted': 'Restricted - Board Only',
            'in_camera': 'In Camera - Confidential'
        }
        label = confidentiality_labels.get(
            metadata['confidentiality'],
            metadata['confidentiality']
        )
        text += f"**Classification:** {label}\n\n"

    text += "---\n\n"
    return text


def format_urgency_indicator(urgency: str) -> str:
    """
    Format urgency indicator with appropriate emphasis.

    Args:
        urgency: Urgency level (low, medium, high, critical)

    Returns:
        Formatted urgency text
    """
    urgency_text = {
        'low': 'Standard timeline - decision can be deferred',
        'medium': 'Decision required within 30 days',
        'high': 'Time-sensitive - decision required within 2 weeks',
        'critical': '**URGENT** - Immediate decision required'
    }

    return urgency_text.get(urgency, 'Standard timeline')


def format_funding_source_detail(financial: Dict) -> str:
    """
    Format detailed funding source information.

    Args:
        financial: Financial data dict

    Returns:
        Formatted markdown text
    """
    text = ""

    funding_source = financial.get('funding_source', 'operating_budget')

    funding_labels = {
        'operating_budget': 'Operating Budget',
        'capital_budget': 'Capital Budget',
        'debt': 'Debt Financing',
        'reserves': 'Accumulated Reserves',
        'mixed': 'Mixed Sources'
    }

    text += f"**Funding Source:** {funding_labels.get(funding_source, funding_source)}\n\n"

    # Budget authority if present
    if 'budget_authority' in financial and financial['budget_authority']:
        text += f"**Budget Authority:** {financial['budget_authority']}\n\n"

    return text


def format_background_section(project: Dict) -> str:
    """
    Format project background section if present.

    Args:
        project: Project data dict

    Returns:
        Formatted markdown text
    """
    if 'background' not in project or not project['background']:
        return ""

    text = "## Background\n\n"
    text += f"{project['background']}\n\n"

    return text
