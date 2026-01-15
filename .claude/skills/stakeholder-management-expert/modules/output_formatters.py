#!/usr/bin/env python3
"""
Output Formatting Module for Consultation Summarizer
Formats analysis results as markdown reports or JSON.
"""

import json
from typing import Dict, List
from datetime import datetime
import pytz


def format_markdown_report(
    meeting_info: Dict,
    categorization: Dict,
    sentiment: Dict,
    weighted_themes: Dict,
    strategies: List[Dict],
    commitments: List[Dict],
    demographics: Dict = None,
    key_quotes: Dict = None
) -> str:
    """
    Format complete consultation summary as markdown report.

    Args:
        meeting_info: Meeting metadata
        categorization: Theme categorization results
        sentiment: Sentiment analysis results
        weighted_themes: Frequency-weighted themes
        strategies: Response strategies
        commitments: Commitments tracking matrix
        demographics: Optional demographics breakdown
        key_quotes: Optional key quotes by sentiment

    Returns:
        Markdown formatted report
    """
    # Build report sections
    report = _format_header(meeting_info, demographics)
    report += _format_attendance_demographics(meeting_info, demographics)
    report += _format_overview_stats(categorization, sentiment)
    report += _format_sentiment_analysis(sentiment)
    report += _format_key_themes(weighted_themes, categorization)

    if key_quotes:
        report += _format_key_quotes(key_quotes)

    report += _format_response_strategies(strategies)

    if commitments:
        report += _format_commitments_matrix(commitments)

    report += _format_next_steps()

    return report


def _format_header(meeting_info: Dict, demographics: Dict = None) -> str:
    """Format document header."""
    project_name = meeting_info.get('project_name', 'Stakeholder Consultation')
    meeting_date = meeting_info.get('meeting_date', 'Unknown')
    meeting_type = meeting_info.get('meeting_type', 'public_meeting').replace('_', ' ').title()

    # Generate timestamp
    eastern = pytz.timezone('America/New_York')
    now = datetime.now(eastern)
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S %Z')

    header = f"# Stakeholder Consultation Summary\n\n"
    header += f"## {project_name}\n\n"
    header += "---\n\n"
    header += f"**Meeting Type:** {meeting_type}\n\n"
    header += f"**Meeting Date:** {meeting_date}\n\n"

    if 'location' in meeting_info:
        header += f"**Location:** {meeting_info['location']}\n\n"

    if 'phase' in meeting_info:
        phase = meeting_info['phase'].replace('_', ' ').title()
        header += f"**Project Phase:** {phase}\n\n"

    header += f"**Report Generated:** {timestamp}\n\n"
    header += "---\n\n"

    return header


def _format_attendance_demographics(meeting_info: Dict, demographics: Dict = None) -> str:
    """Format attendance and demographics section."""
    section = "## Attendance\n\n"

    attendance = meeting_info.get('attendance', 0)
    section += f"**Total Attendance:** {attendance} people\n\n"

    if demographics:
        section += "### Demographic Breakdown\n\n"

        demo_data = []
        for category, count in demographics.items():
            category_name = category.replace('_', ' ').title()
            pct = (count / attendance * 100) if attendance > 0 else 0
            demo_data.append(f"- **{category_name}:** {count} ({pct:.1f}%)")

        section += "\n".join(demo_data) + "\n\n"

    return section


def _format_overview_stats(categorization: Dict, sentiment: Dict) -> str:
    """Format overview statistics."""
    stats = categorization['statistics']
    sentiment_counts = sentiment['sentiment_counts']

    section = "## Overview Statistics\n\n"

    section += f"**Total Comments Received:** {stats['total_feedback']}\n\n"
    section += f"**Categorized Comments:** {stats['categorized_count']} ({stats['categorization_rate']}%)\n\n"
    section += f"**Uncategorized Comments:** {stats['uncategorized_count']}\n\n"
    section += f"**Themes Identified:** {stats['categories_found']}\n\n"

    # Sentiment overview
    section += "### Sentiment Overview\n\n"
    section += f"**Overall Sentiment:** {sentiment['overall_sentiment']}\n\n"
    section += f"- Support: {sentiment_counts.get('support', 0)}\n"
    section += f"- Opposition: {sentiment_counts.get('opposition', 0)}\n"
    section += f"- Neutral: {sentiment_counts.get('neutral', 0)}\n"
    section += f"- Mixed: {sentiment_counts.get('mixed', 0)}\n\n"

    return section


def _format_sentiment_analysis(sentiment: Dict) -> str:
    """Format detailed sentiment analysis."""
    section = "## Sentiment Analysis\n\n"

    sentiment_counts = sentiment['sentiment_counts']
    sentiment_pcts = sentiment['sentiment_percentages']

    # Build sentiment table data
    from Shared_Utils.report_utils import format_markdown_table

    table_data = []
    for sentiment_type in ['support', 'opposition', 'neutral', 'mixed']:
        count = sentiment_counts.get(sentiment_type, 0)
        pct = sentiment_pcts.get(sentiment_type, 0)

        table_data.append({
            'sentiment': sentiment_type.capitalize(),
            'count': count,
            'percentage': f"{pct}%"
        })

    section += format_markdown_table(
        table_data,
        ['sentiment', 'count', 'percentage'],
        ['left', 'right', 'right']
    ) + "\n\n"

    # Overall assessment
    section += f"**Overall Assessment:** {sentiment['overall_sentiment']}\n\n"
    section += f"**Net Sentiment:** {sentiment['net_sentiment']} (support - opposition)\n\n"

    return section


def _format_key_themes(weighted_themes: Dict, categorization: Dict) -> str:
    """Format key themes and concerns."""
    section = "## Key Themes and Concerns\n\n"

    themes = weighted_themes['weighted_themes']
    categorized = categorization['categorized_feedback']

    from Shared_Utils.report_utils import format_markdown_table

    # Build themes table
    table_data = []
    for theme in themes:
        table_data.append({
            'rank': theme['rank'],
            'theme': theme['theme'],
            'comments': theme['count'],
            'percentage': f"{theme['percentage']}%"
        })

    section += format_markdown_table(
        table_data,
        ['rank', 'theme', 'comments', 'percentage'],
        ['center', 'left', 'right', 'right']
    ) + "\n\n"

    # Top 3 themes detail
    section += "### Top 3 Themes (Detailed)\n\n"

    for theme_data in weighted_themes['top_3_themes']:
        theme = theme_data['theme']
        count = theme_data['count']

        section += f"#### {theme} ({count} comments)\n\n"

        # Show sample comments
        if theme in categorized:
            samples = categorized[theme][:3]  # First 3 comments
            for sample in samples:
                section += f"- \"{sample['text']}\"\n"
            section += "\n"

    return section


def _format_key_quotes(key_quotes: Dict) -> str:
    """Format key representative quotes."""
    section = "## Key Representative Quotes\n\n"

    for sentiment_type in ['support', 'opposition', 'neutral']:
        if sentiment_type in key_quotes and key_quotes[sentiment_type]:
            section += f"### {sentiment_type.capitalize()}\n\n"

            for quote in key_quotes[sentiment_type]:
                section += f"> \"{quote['text']}\"\n\n"

    return section


def _format_response_strategies(strategies: List[Dict]) -> str:
    """Format response strategies section."""
    section = "## Response Strategy Recommendations\n\n"

    # Group by priority
    high_priority = [s for s in strategies if s['priority'] in [1, 2]]
    medium_priority = [s for s in strategies if s['priority'] == 3]
    low_priority = [s for s in strategies if s['priority'] in [4, 5]]

    for priority_name, priority_list in [
        ("High Priority", high_priority),
        ("Medium Priority", medium_priority),
        ("Low Priority", low_priority)
    ]:
        if priority_list:
            section += f"### {priority_name}\n\n"

            for strategy in priority_list:
                theme = strategy['theme']
                count = strategy['comment_count']
                strat_text = strategy['strategy']
                tactics = strategy['tactics']

                section += f"#### {theme} ({count} comments)\n\n"
                section += f"**Strategy:** {strat_text}\n\n"
                section += "**Tactics:**\n"

                for tactic in tactics:
                    section += f"- {tactic}\n"

                section += "\n"

    return section


def _format_commitments_matrix(commitments: List[Dict]) -> str:
    """Format commitments tracking matrix."""
    if not commitments:
        return ""

    section = "## Commitments Tracking Matrix\n\n"

    from Shared_Utils.report_utils import format_markdown_table

    table_data = []
    for commit in commitments:
        table_data.append({
            'theme': commit['theme'],
            'commitment': commit['commitment'][:100],  # Truncate for table
            'responsible': commit['responsible_party'],
            'deadline': commit['deadline'],
            'status': commit['status']
        })

    section += format_markdown_table(
        table_data,
        ['theme', 'commitment', 'responsible', 'deadline', 'status'],
        ['left', 'left', 'left', 'center', 'center']
    ) + "\n\n"

    return section


def _format_next_steps() -> str:
    """Format next steps section."""
    section = "## Recommended Next Steps\n\n"

    section += "1. **Circulate Summary:** Distribute this summary to project team and stakeholders\n"
    section += "2. **Implement High Priority Responses:** Address top concerns immediately\n"
    section += "3. **Track Commitments:** Monitor and fulfill all commitments made\n"
    section += "4. **Follow-up Communication:** Provide written response to key concerns\n"
    section += "5. **Schedule Next Consultation:** Plan follow-up meeting to report progress\n\n"

    return section


def format_json_output(
    meeting_info: Dict,
    categorization: Dict,
    sentiment: Dict,
    weighted_themes: Dict,
    strategies: List[Dict],
    commitments: List[Dict]
) -> str:
    """
    Format results as JSON.

    Args:
        meeting_info: Meeting metadata
        categorization: Theme categorization
        sentiment: Sentiment analysis
        weighted_themes: Weighted themes
        strategies: Response strategies
        commitments: Commitments matrix

    Returns:
        JSON string
    """
    output = {
        'meeting_info': meeting_info,
        'statistics': categorization['statistics'],
        'sentiment_analysis': {
            'overall_sentiment': sentiment['overall_sentiment'],
            'sentiment_counts': sentiment['sentiment_counts'],
            'sentiment_percentages': sentiment['sentiment_percentages'],
            'net_sentiment': sentiment['net_sentiment']
        },
        'themes': weighted_themes['weighted_themes'],
        'top_3_themes': weighted_themes['top_3_themes'],
        'response_strategies': strategies,
        'commitments': commitments
    }

    return json.dumps(output, indent=2)
