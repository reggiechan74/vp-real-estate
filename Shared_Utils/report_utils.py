#!/usr/bin/env python3
"""
Report Generation Utilities Module
Provides shared functions for executive summaries, markdown formatting,
financial summaries, timestamps, and risk assessments.

Used by:
- All report generators (briefing_note_generator.py, board_memo_generator.py, etc.)
- All calculators (for consistent markdown output)
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import pytz


def generate_executive_summary(
    data: Dict,
    template: str = 'decision'
) -> str:
    """
    Generate executive summary (1-2 paragraphs, decision-focused).

    Args:
        data: Dict with summary data
            {
                'issue': 'Transit station property acquisition',
                'recommendation': 'Settle at $185,000',
                'rationale': 'Saves $60,000 vs hearing',
                'urgency': 'high',  # low/medium/high
                'financial_impact': 185000
            }
        template: Summary template type
            'decision' - Decision-focused (default)
            'status' - Status update
            'analysis' - Analysis summary

    Returns:
        Markdown formatted executive summary string
    """
    issue = data.get('issue', 'Project')
    recommendation = data.get('recommendation', 'Proceed as planned')
    rationale = data.get('rationale', '')
    urgency = data.get('urgency', 'medium')
    financial_impact = data.get('financial_impact', 0)

    if template == 'decision':
        summary = f"## Executive Summary\n\n"
        summary += f"**Issue:** {issue}\n\n"
        summary += f"**Recommendation:** {recommendation}\n\n"

        if rationale:
            summary += f"**Rationale:** {rationale}\n\n"

        if financial_impact:
            summary += f"**Financial Impact:** ${financial_impact:,.2f}\n\n"

        urgency_text = {
            'low': 'Decision can be deferred',
            'medium': 'Decision required within 30 days',
            'high': 'Immediate decision required'
        }
        summary += f"**Urgency:** {urgency_text.get(urgency, 'Standard timeline')}\n\n"

    elif template == 'status':
        summary = f"## Status Update\n\n"
        summary += f"**Project:** {issue}\n\n"
        summary += f"**Status:** {recommendation}\n\n"

        if rationale:
            summary += f"**Progress:** {rationale}\n\n"

    else:  # analysis
        summary = f"## Analysis Summary\n\n"
        summary += f"**Subject:** {issue}\n\n"
        summary += f"**Conclusion:** {recommendation}\n\n"

        if rationale:
            summary += f"**Key Findings:** {rationale}\n\n"

    return summary


def format_markdown_table(
    data: List[Dict],
    columns: List[str],
    align: Optional[List[str]] = None
) -> str:
    """
    Format data as markdown table.

    Args:
        data: List of row dicts
            [
                {'task': 'Appraisal', 'duration': 30, 'cost': 5000},
                {'task': 'Negotiation', 'duration': 60, 'cost': 10000}
            ]
        columns: List of column keys to include (in order)
            ['task', 'duration', 'cost']
        align: Optional list of alignments ('left', 'center', 'right')
            ['left', 'center', 'right']

    Returns:
        Markdown table string
    """
    if not data or not columns:
        return ""

    # Default alignment
    if align is None:
        align = ['left'] * len(columns)

    # Build header
    header_values = [col.replace('_', ' ').title() for col in columns]
    header_row = "| " + " | ".join(header_values) + " |"

    # Build separator
    align_chars = {
        'left': ':---',
        'center': ':---:',
        'right': '---:'
    }
    sep_row = "| " + " | ".join(
        align_chars.get(a, ':---') for a in align
    ) + " |"

    # Build data rows
    data_rows = []
    for row in data:
        values = []
        for col in columns:
            value = row.get(col, '')

            # Format based on type
            if isinstance(value, float):
                # Check if it's currency (large numbers)
                if value >= 1000:
                    formatted = f"${value:,.2f}"
                else:
                    formatted = f"{value:.2f}"
            elif isinstance(value, int):
                if col in ['cost', 'budget', 'value', 'amount']:
                    formatted = f"${value:,}"
                else:
                    formatted = f"{value:,}"
            else:
                formatted = str(value)

            values.append(formatted)

        data_rows.append("| " + " | ".join(values) + " |")

    # Combine all rows
    table = "\n".join([header_row, sep_row] + data_rows)
    return table


def format_financial_summary(
    financial_data: Dict,
    format_type: str = 'detailed'
) -> str:
    """
    Format financial data (currency, percentages, ratios).

    Args:
        financial_data: Dict with financial metrics
            {
                'total_cost': 250000,
                'breakdown': {
                    'acquisition': 200000,
                    'legal': 30000,
                    'expert': 20000
                },
                'contingency': 25000,
                'contingency_pct': 0.10
            }
        format_type: Output format
            'detailed' - Full breakdown (default)
            'summary' - High-level only
            'comparison' - Side-by-side comparison

    Returns:
        Markdown formatted financial summary
    """
    total = financial_data.get('total_cost', 0)
    breakdown = financial_data.get('breakdown', {})
    contingency = financial_data.get('contingency', 0)
    contingency_pct = financial_data.get('contingency_pct', 0)

    if format_type == 'detailed':
        summary = "### Financial Summary\n\n"
        summary += f"**Total Cost:** ${total:,.2f}\n\n"

        if breakdown:
            summary += "**Cost Breakdown:**\n"
            for item, amount in breakdown.items():
                pct = (amount / total * 100) if total > 0 else 0
                summary += f"- {item.replace('_', ' ').title()}: ${amount:,.2f} ({pct:.1f}%)\n"
            summary += "\n"

        if contingency > 0:
            summary += f"**Contingency:** ${contingency:,.2f} ({contingency_pct*100:.1f}%)\n\n"

    elif format_type == 'summary':
        summary = f"**Total Cost:** ${total:,.2f}"
        if contingency > 0:
            summary += f" (includes ${contingency:,.2f} contingency)"

    else:  # comparison
        summary = "### Cost Comparison\n\n"
        summary += format_markdown_table(
            [{'category': k.replace('_', ' ').title(), 'amount': v} for k, v in breakdown.items()],
            ['category', 'amount'],
            ['left', 'right']
        )

    return summary


def eastern_timestamp(include_time: bool = True) -> str:
    """
    Generate Eastern Time timestamp (YYYY-MM-DD_HHMMSS or YYYY-MM-DD).

    Args:
        include_time: Include time component (default True)

    Returns:
        Timestamp string
            With time: '2025-11-16_143022'
            Without time: '2025-11-16'
    """
    eastern = pytz.timezone('America/New_York')
    now = datetime.now(eastern)

    if include_time:
        return now.strftime('%Y-%m-%d_%H%M%S')
    else:
        return now.strftime('%Y-%m-%d')


def generate_recommendation_section(
    scores: Dict,
    thresholds: Dict
) -> str:
    """
    Generate recommendation based on scoring thresholds.

    Args:
        scores: Dict with calculated scores
            {'settlement_score': 85, 'hearing_score': 62}
        thresholds: Dict with threshold rules
            {
                'settlement_recommended': 75,
                'hearing_recommended': 50,
                'neutral_range': (60, 75)
            }

    Returns:
        Markdown formatted recommendation section
    """
    settlement_score = scores.get('settlement_score', 0)
    hearing_score = scores.get('hearing_score', 0)

    settlement_threshold = thresholds.get('settlement_recommended', 75)
    hearing_threshold = thresholds.get('hearing_recommended', 50)

    recommendation = "## Recommendation\n\n"

    if settlement_score >= settlement_threshold:
        recommendation += f"**Recommendation:** SETTLE\n\n"
        recommendation += f"**Score:** {settlement_score}/100\n\n"
        recommendation += "**Rationale:** Settlement score exceeds threshold. "
        recommendation += "Settlement offers better value than proceeding to hearing.\n\n"

    elif hearing_score >= hearing_threshold and settlement_score < settlement_threshold:
        recommendation += f"**Recommendation:** PROCEED TO HEARING\n\n"
        recommendation += f"**Score:** Hearing {hearing_score}/100, Settlement {settlement_score}/100\n\n"
        recommendation += "**Rationale:** Hearing score indicates better expected value. "
        recommendation += "Settlement offer insufficient.\n\n"

    else:
        recommendation += f"**Recommendation:** NEUTRAL - NEGOTIATE FURTHER\n\n"
        recommendation += f"**Scores:** Settlement {settlement_score}/100, Hearing {hearing_score}/100\n\n"
        recommendation += "**Rationale:** Scores in neutral range. "
        recommendation += "Continue negotiations to improve settlement terms.\n\n"

    return recommendation


def format_risk_assessment(risks: List[Dict]) -> str:
    """
    Format risk assessment with severity and mitigation.

    Args:
        risks: List of risk dicts
            [
                {
                    'risk': 'Holdout owner',
                    'severity': 'HIGH',
                    'probability': 0.6,
                    'impact': 'Project delay',
                    'mitigation': 'Early engagement, premium offer'
                },
                ...
            ]

    Returns:
        Markdown formatted risk assessment
    """
    if not risks:
        return "## Risk Assessment\n\nNo significant risks identified.\n\n"

    assessment = "## Risk Assessment\n\n"

    # Group by severity
    critical = [r for r in risks if r.get('severity') == 'CRITICAL']
    high = [r for r in risks if r.get('severity') == 'HIGH']
    medium = [r for r in risks if r.get('severity') == 'MEDIUM']
    low = [r for r in risks if r.get('severity') == 'LOW']

    if critical:
        assessment += "### Critical Risks\n\n"
        for risk in critical:
            assessment += _format_single_risk(risk)
        assessment += "\n"

    if high:
        assessment += "### High Risks\n\n"
        for risk in high:
            assessment += _format_single_risk(risk)
        assessment += "\n"

    if medium:
        assessment += "### Medium Risks\n\n"
        for risk in medium:
            assessment += _format_single_risk(risk)
        assessment += "\n"

    if low:
        assessment += "### Low Risks\n\n"
        for risk in low:
            assessment += _format_single_risk(risk)
        assessment += "\n"

    return assessment


def _format_single_risk(risk: Dict) -> str:
    """Format a single risk entry."""
    risk_text = f"**{risk.get('risk', 'Unknown Risk')}**\n"

    if 'probability' in risk:
        risk_text += f"- Probability: {risk['probability']*100:.0f}%\n"

    if 'impact' in risk:
        risk_text += f"- Impact: {risk['impact']}\n"

    if 'mitigation' in risk:
        risk_text += f"- Mitigation: {risk['mitigation']}\n"

    risk_text += "\n"
    return risk_text


def format_timeline_gantt(tasks: List[Dict]) -> str:
    """
    Format timeline as simple text-based Gantt chart.

    Args:
        tasks: List of task dicts with start/finish dates
            [
                {'name': 'Appraisal', 'start': 0, 'finish': 30},
                {'name': 'Negotiation', 'start': 30, 'finish': 90},
                ...
            ]

    Returns:
        Markdown formatted Gantt chart
    """
    if not tasks:
        return ""

    # Find max finish to determine scale
    max_finish = max(task.get('finish', 0) for task in tasks)
    scale = max(max_finish // 50, 1)  # Each character = scale days

    gantt = "### Timeline (Gantt Chart)\n\n"
    gantt += f"*Scale: Each '=' represents {scale} days*\n\n"

    for task in tasks:
        name = task.get('name', 'Task')
        start = task.get('start', 0)
        finish = task.get('finish', 0)
        is_critical = task.get('is_critical', False)

        # Calculate bar length
        duration = finish - start
        bar_length = max(int(duration / scale), 1)
        start_offset = int(start / scale)

        # Build bar
        spacer = " " * start_offset
        bar_char = "█" if is_critical else "="
        bar = bar_char * bar_length

        gantt += f"{name:<20} {spacer}{bar} ({duration:.0f} days)\n"

    gantt += "\n"
    return gantt


def generate_action_items(
    items: List[Dict],
    include_timeline: bool = True
) -> str:
    """
    Generate action items section.

    Args:
        items: List of action item dicts
            [
                {
                    'action': 'Obtain board approval',
                    'responsible': 'VP Acquisitions',
                    'deadline': '2025-12-15',
                    'priority': 'HIGH'
                },
                ...
            ]
        include_timeline: Include deadline column (default True)

    Returns:
        Markdown formatted action items
    """
    if not items:
        return "## Action Items\n\nNo action items.\n\n"

    action_section = "## Action Items\n\n"

    # Group by priority
    high = [i for i in items if i.get('priority') == 'HIGH']
    medium = [i for i in items if i.get('priority') == 'MEDIUM']
    low = [i for i in items if i.get('priority') == 'LOW']

    for priority_name, priority_items in [('High Priority', high), ('Medium Priority', medium), ('Low Priority', low)]:
        if priority_items:
            action_section += f"### {priority_name}\n\n"

            for idx, item in enumerate(priority_items, start=1):
                action = item.get('action', '')
                responsible = item.get('responsible', 'TBD')
                deadline = item.get('deadline', 'TBD')

                action_section += f"{idx}. **{action}**\n"
                action_section += f"   - Responsible: {responsible}\n"

                if include_timeline:
                    action_section += f"   - Deadline: {deadline}\n"

                action_section += "\n"

    return action_section


def format_number(value: float, format_type: str = 'currency') -> str:
    """
    Format numbers consistently.

    Args:
        value: Number to format
        format_type: Type of formatting
            'currency' - $1,234.56
            'percentage' - 12.3%
            'ratio' - 1.23
            'integer' - 1,234

    Returns:
        Formatted string
    """
    if format_type == 'currency':
        return f"${value:,.2f}"
    elif format_type == 'percentage':
        return f"{value:.1f}%"
    elif format_type == 'ratio':
        return f"{value:.2f}"
    elif format_type == 'integer':
        return f"{int(value):,}"
    else:
        return str(value)


def generate_document_header(
    title: str,
    subtitle: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> str:
    """
    Generate standard document header.

    Args:
        title: Document title
        subtitle: Optional subtitle
        metadata: Optional metadata dict
            {'date': '2025-11-16', 'prepared_by': 'Acquisition Team', ...}

    Returns:
        Markdown formatted header
    """
    header = f"# {title}\n\n"

    if subtitle:
        header += f"## {subtitle}\n\n"

    if metadata:
        header += "---\n\n"
        for key, value in metadata.items():
            header += f"**{key.replace('_', ' ').title()}:** {value}\n\n"
        header += "---\n\n"

    return header
