#!/usr/bin/env python3
"""
Output Formatting Module
Formats timeline analysis results for reports and visualization.
"""

import sys
from pathlib import Path
from typing import Dict, List

# Add Shared_Utils to path
shared_utils_path = Path(__file__).resolve().parents[4] / 'Shared_Utils'
if str(shared_utils_path) not in sys.path:
    sys.path.insert(0, str(shared_utils_path))

import report_utils


def format_timeline_report(
    project_name: str,
    analysis_results: Dict,
    include_gantt: bool = True
) -> str:
    """
    Format complete timeline analysis report.

    Args:
        project_name: Project name
        analysis_results: Complete analysis results dict
        include_gantt: Include Gantt chart visualization (default True)

    Returns:
        Markdown formatted report
    """
    report = []

    # Header
    metadata = {
        'Project': project_name,
        'Analysis Date': report_utils.eastern_timestamp(include_time=False),
        'Generated': report_utils.eastern_timestamp()
    }
    report.append(report_utils.generate_document_header(
        'Expropriation Project Timeline Analysis',
        'Critical Path Schedule with OEA Statutory Deadlines',
        metadata
    ))

    # Executive Summary
    report.append(format_executive_summary(analysis_results))

    # Critical Path Summary
    report.append(format_critical_path_summary(analysis_results))

    # Statutory Deadlines
    if 'statutory_analysis' in analysis_results:
        report.append(format_statutory_deadlines(analysis_results['statutory_analysis']))

    # Risk Assessment
    if 'risks' in analysis_results:
        report.append(report_utils.format_risk_assessment(analysis_results['risks']))

    # Task Details
    report.append(format_task_details_table(analysis_results))

    # Gantt Chart
    if include_gantt and 'gantt_data' in analysis_results:
        report.append(report_utils.format_timeline_gantt(analysis_results['gantt_data']))

    # Resource Requirements
    if 'resources' in analysis_results:
        report.append(format_resource_summary(analysis_results['resources']))

    # Dependency Analysis
    if 'dependency_analysis' in analysis_results:
        report.append(format_dependency_analysis(analysis_results['dependency_analysis']))

    return '\n'.join(report)


def format_executive_summary(results: Dict) -> str:
    """Format executive summary section."""
    summary = "## Executive Summary\n\n"

    critical_path = results.get('critical_path_analysis', {})
    project_duration = critical_path.get('project_duration', 0)
    num_critical = critical_path.get('num_critical_tasks', 0)
    num_total = critical_path.get('num_total_tasks', 0)

    summary += f"**Project Duration:** {project_duration:.0f} days\n\n"
    summary += f"**Critical Path:** {num_critical} of {num_total} tasks ({critical_path.get('critical_path_percentage', 0):.1f}%)\n\n"

    # PERT confidence interval
    if 'confidence_interval' in results:
        ci = results['confidence_interval']
        summary += f"**Duration Range (90% confidence):** {ci['lower_bound']:.0f} - {ci['upper_bound']:.0f} days\n\n"

    # Risk summary
    risks = results.get('risks', [])
    critical_risks = [r for r in risks if r.get('severity') == 'CRITICAL']
    high_risks = [r for r in risks if r.get('severity') == 'HIGH']

    if critical_risks or high_risks:
        summary += f"**Timeline Risks:** {len(critical_risks)} critical, {len(high_risks)} high\n\n"
    else:
        summary += "**Timeline Risks:** No critical or high risks identified\n\n"

    return summary


def format_critical_path_summary(results: Dict) -> str:
    """Format critical path summary section."""
    summary = "## Critical Path Analysis\n\n"

    cp_analysis = results.get('critical_path_analysis', {})
    critical_path = cp_analysis.get('critical_path', [])

    summary += "**Critical Path Sequence:**\n\n"

    task_details = cp_analysis.get('task_details', {})
    for idx, task_id in enumerate(critical_path, start=1):
        task = task_details.get(task_id, {})
        name = task.get('name', task_id)
        duration = task.get('duration', 0)
        early_start = task.get('early_start', 0)
        early_finish = task.get('early_finish', 0)

        summary += f"{idx}. **{name}** (ID: {task_id})\n"
        summary += f"   - Duration: {duration:.0f} days\n"
        summary += f"   - Schedule: Day {early_start:.0f} - Day {early_finish:.0f}\n\n"

    return summary


def format_statutory_deadlines(statutory_analysis: Dict) -> str:
    """Format statutory deadlines section."""
    section = "## Statutory Deadlines (Ontario Expropriations Act)\n\n"

    # Registration deadline
    if 'registration_deadline' in statutory_analysis:
        reg = statutory_analysis['registration_deadline']
        section += "### 3-Month Registration Deadline (s.9)\n\n"
        section += f"- **Approval Date:** {reg['approval_date']}\n"
        section += f"- **Statutory Deadline:** {reg['statutory_deadline']} (90 days)\n"
        section += f"- **Recommended Deadline:** {reg['recommended_deadline']} ({reg['buffer_days']}-day buffer)\n\n"

    # Days remaining
    if 'days_remaining' in statutory_analysis:
        remaining = statutory_analysis['days_remaining']
        section += "### Timeline Status\n\n"
        section += f"- **Current Date:** {remaining['current_date']}\n"
        section += f"- **Days Remaining:** {remaining['days_remaining']} days\n"
        section += f"- **Urgency Level:** {remaining['urgency_level']}\n"
        section += f"- **Status:** {remaining['status']}\n"
        section += f"- **Percentage Elapsed:** {remaining['percentage_elapsed']:.1f}%\n\n"

    # Milestones
    if 'milestones' in statutory_analysis:
        section += "### Key Milestones\n\n"
        milestones = statutory_analysis['milestones']

        milestone_rows = [
            {
                'milestone': m['name'],
                'date': m['date'],
                'days': m['days_from_approval']
            }
            for m in milestones
        ]

        section += report_utils.format_markdown_table(
            milestone_rows,
            ['milestone', 'date', 'days'],
            ['left', 'center', 'center']
        )
        section += "\n\n"

    return section


def format_task_details_table(results: Dict) -> str:
    """Format task details table."""
    section = "## Task Details\n\n"

    cp_analysis = results.get('critical_path_analysis', {})
    task_details = cp_analysis.get('task_details', {})

    if not task_details:
        return section + "No task details available.\n\n"

    # Build table rows
    rows = []
    for task_id, details in sorted(task_details.items()):
        rows.append({
            'id': task_id,
            'name': details.get('name', ''),
            'duration': details.get('duration', 0),
            'early_start': details.get('early_start', 0),
            'early_finish': details.get('early_finish', 0),
            'total_float': details.get('total_float', 0),
            'critical': 'Yes' if details.get('is_critical') else 'No'
        })

    section += report_utils.format_markdown_table(
        rows,
        ['id', 'name', 'duration', 'early_start', 'early_finish', 'total_float', 'critical'],
        ['left', 'left', 'center', 'center', 'center', 'center', 'center']
    )
    section += "\n\n"

    return section


def format_resource_summary(resources: Dict) -> str:
    """Format resource requirements summary."""
    section = "## Resource Requirements\n\n"

    total = resources.get('total_resources', {})
    peak = resources.get('peak_resources', {})

    section += "### Total Resources\n\n"
    section += f"- **Staff Days:** {total.get('staff_days', 0):,.1f}\n"
    section += f"- **Budget:** ${total.get('budget', 0):,.2f}\n"

    consultant_days = total.get('consultant_days', {})
    if consultant_days:
        section += f"- **Consultant Days:**\n"
        for cons_type, days in consultant_days.items():
            section += f"  - {cons_type.title()}: {days:,.1f} days\n"

    section += "\n### Peak Resources\n\n"
    section += f"- **Peak Staff:** {peak.get('staff', 0)} concurrent\n"

    peak_consultants = peak.get('consultants', {})
    if peak_consultants:
        section += f"- **Peak Consultants:**\n"
        for cons_type, count in peak_consultants.items():
            section += f"  - {cons_type.title()}: {count} concurrent\n"

    section += "\n"

    return section


def format_dependency_analysis(dep_analysis: Dict) -> str:
    """Format dependency complexity analysis."""
    section = "## Dependency Analysis\n\n"

    section += f"**Total Tasks:** {dep_analysis.get('total_tasks', 0)}\n\n"
    section += f"**Total Dependencies:** {dep_analysis.get('total_dependencies', 0)}\n\n"
    section += f"**Average Dependencies per Task:** {dep_analysis.get('avg_dependencies_per_task', 0):.2f}\n\n"
    section += f"**Dependency Density:** {dep_analysis.get('dependency_density', 0):.3f}\n\n"

    start_tasks = dep_analysis.get('start_tasks', [])
    end_tasks = dep_analysis.get('end_tasks', [])
    bottlenecks = dep_analysis.get('bottleneck_tasks', [])

    section += f"**Start Tasks (no predecessors):** {', '.join(start_tasks) if start_tasks else 'None'}\n\n"
    section += f"**End Tasks (no successors):** {', '.join(end_tasks) if end_tasks else 'None'}\n\n"

    if bottlenecks:
        section += f"**Bottleneck Tasks (3+ dependencies):** {', '.join(bottlenecks)}\n\n"

    return section


def format_json_output(results: Dict) -> str:
    """
    Format results as JSON string.

    Args:
        results: Analysis results dict

    Returns:
        JSON string
    """
    import json
    return json.dumps(results, indent=2, default=str)


def generate_output_filename(project_name: str, format: str = 'md') -> str:
    """
    Generate timestamped output filename.

    Args:
        project_name: Project name
        format: Output format ('md', 'json')

    Returns:
        Filename with timestamp prefix
    """
    timestamp = report_utils.eastern_timestamp()
    safe_name = project_name.lower().replace(' ', '_').replace('/', '_')
    return f"{timestamp}_timeline_{safe_name}.{format}"
