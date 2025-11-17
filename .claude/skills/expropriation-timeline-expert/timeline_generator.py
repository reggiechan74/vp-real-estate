#!/usr/bin/env python3
"""
Timeline Generator for Expropriation Projects

Simplified wrapper for slash command use. Generates Gantt charts and milestone
reports for expropriation timelines using critical path analysis.

Uses:
- Shared_Utils/timeline_utils.py - critical path, resource allocation, risk flags
- Shared_Utils/report_utils.py - Gantt charts, document headers, markdown formatting

Author: Claude Code
Version: 1.0.0
Date: 2025-11-17
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta

# Add Shared_Utils to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'Shared_Utils'))

from timeline_utils import (
    calculate_critical_path,
    calculate_resource_requirements,
    identify_risk_flags,
    scenario_analysis
)
from report_utils import (
    generate_document_header,
    format_timeline_gantt,
    format_markdown_table,
    format_risk_assessment,
    eastern_timestamp
)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _get_risk_mitigation(risk_type: str) -> str:
    """
    Get mitigation strategy for a given risk type.

    Args:
        risk_type: Risk type identifier

    Returns:
        Mitigation strategy string
    """
    mitigations = {
        'TIGHT_DEADLINE': 'Expedite task execution, allocate additional resources, escalate to senior management',
        'CRITICAL_PATH_NO_FLOAT': 'Monitor closely, implement early warning system, prepare contingency plan',
        'LONG_DURATION': 'Break into smaller milestones, implement progress tracking, identify acceleration opportunities'
    }
    return mitigations.get(risk_type, 'Monitor and reassess regularly')


# ============================================================================
# MAIN FUNCTIONS
# ============================================================================

def load_input(input_path: str) -> Dict:
    """
    Load and validate timeline input JSON.

    Args:
        input_path: Path to input JSON file

    Returns:
        Dict with validated input data

    Raises:
        ValueError: If input is invalid
    """
    with open(input_path, 'r') as f:
        data = json.load(f)

    # Validate required fields
    required = ['project_name', 'tasks', 'dependencies']
    missing = [f for f in required if f not in data]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    # Validate tasks structure
    for task in data['tasks']:
        if 'id' not in task or 'name' not in task or 'duration' not in task:
            raise ValueError(f"Invalid task structure: {task}")

    # Validate dependencies structure
    for dep in data['dependencies']:
        if len(dep) != 2:
            raise ValueError(f"Invalid dependency structure: {dep}")

    return data


def generate_timeline_report(input_data: Dict) -> str:
    """
    Generate comprehensive timeline report with Gantt chart and milestones.

    Args:
        input_data: Timeline input dict

    Returns:
        Markdown formatted report
    """
    project_name = input_data['project_name']
    tasks = input_data['tasks']
    dependencies = input_data['dependencies']
    deadlines = input_data.get('deadlines', {})
    resource_requirements = input_data.get('resource_requirements', {})
    start_date = input_data.get('start_date', datetime.now().strftime('%Y-%m-%d'))

    # Calculate critical path
    timeline = calculate_critical_path(tasks, dependencies)

    # Generate report header
    report = generate_document_header(
        title=f"Project Timeline Analysis",
        subtitle=project_name,
        metadata={
            'analysis_date': eastern_timestamp(include_time=False),
            'start_date': start_date,
            'project_duration': f"{timeline['project_duration']:.0f} days",
            'critical_path_tasks': f"{timeline['num_critical_tasks']}/{timeline['num_total_tasks']}"
        }
    )

    # Executive summary
    report += "## Executive Summary\n\n"
    report += f"**Project Duration:** {timeline['project_duration']:.0f} days "
    report += f"({timeline['project_duration']/30:.1f} months)\n\n"
    report += f"**Critical Path:** {len(timeline['critical_path'])} tasks "
    report += f"({timeline['critical_path_percentage']:.1f}% of total)\n\n"

    # Calculate end date
    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = start + timedelta(days=timeline['project_duration'])
            report += f"**Estimated Completion:** {end.strftime('%Y-%m-%d')}\n\n"
        except:
            pass

    # Critical path sequence
    report += "## Critical Path\n\n"
    report += "Tasks that directly impact project completion:\n\n"

    critical_path_tasks = []
    for task_id in timeline['critical_path']:
        details = timeline['task_details'][task_id]
        critical_path_tasks.append({
            'task': details['name'],
            'duration': f"{details['duration']:.0f} days",
            'early_start': f"Day {details['early_start']:.0f}",
            'early_finish': f"Day {details['early_finish']:.0f}"
        })

    report += format_markdown_table(
        critical_path_tasks,
        ['task', 'duration', 'early_start', 'early_finish'],
        ['left', 'center', 'center', 'center']
    )
    report += "\n\n"

    # Timeline Gantt chart
    gantt_tasks = []
    for task_id, details in timeline['task_details'].items():
        gantt_tasks.append({
            'name': details['name'],
            'start': details['early_start'],
            'finish': details['early_finish'],
            'is_critical': details['is_critical']
        })

    # Sort by start time
    gantt_tasks.sort(key=lambda x: x['start'])

    report += format_timeline_gantt(gantt_tasks)

    # All tasks with float analysis
    report += "## All Tasks\n\n"

    all_tasks = []
    for task_id in sorted(timeline['task_details'].keys()):
        details = timeline['task_details'][task_id]
        all_tasks.append({
            'id': task_id,
            'task': details['name'],
            'duration': f"{details['duration']:.0f}",
            'float': f"{details['total_float']:.0f}",
            'critical': 'YES' if details['is_critical'] else 'NO'
        })

    report += format_markdown_table(
        all_tasks,
        ['id', 'task', 'duration', 'float', 'critical'],
        ['left', 'left', 'center', 'center', 'center']
    )
    report += "\n\n"
    report += "*Float = Schedule flexibility (days task can be delayed without impacting completion)*\n\n"

    # Resource requirements (if provided)
    if resource_requirements:
        resources = calculate_resource_requirements(timeline, resource_requirements)

        report += "## Resource Requirements\n\n"
        report += f"**Total Staff Days:** {resources['total_resources']['staff_days']:,.0f}\n\n"
        report += f"**Total Budget:** ${resources['total_resources']['budget']:,.2f}\n\n"

        if resources['total_resources']['consultant_days']:
            report += "**Consultant Days:**\n"
            for cons_type, days in resources['total_resources']['consultant_days'].items():
                report += f"- {cons_type.title()}: {days:,.0f} days\n"
            report += "\n"

        report += f"**Peak Staffing:** {resources['peak_resources']['staff']} staff\n\n"

    # Risk analysis (if deadlines provided)
    if deadlines:
        risks = identify_risk_flags(timeline, deadlines)

        if risks:
            # Transform risk format for report_utils
            formatted_risks = []
            for risk in risks:
                formatted_risks.append({
                    'risk': f"{risk.get('task_name', 'Unknown Task')} ({risk.get('risk_type', 'Unknown')})",
                    'severity': risk.get('severity', 'MEDIUM'),
                    'impact': risk.get('message', ''),
                    'mitigation': _get_risk_mitigation(risk.get('risk_type'))
                })
            report += format_risk_assessment(formatted_risks)

    # Scenario analysis
    scenarios = {
        'best_case': 0.8,      # 20% faster
        'likely_case': 1.0,    # Base case
        'worst_case': 1.3      # 30% slower
    }

    scenario_results = scenario_analysis(timeline, scenarios)

    report += "## Scenario Analysis\n\n"

    scenario_table = [
        {
            'scenario': 'Best Case (20% faster)',
            'duration': f"{scenario_results['best_case']['duration']:.0f} days",
            'variance': f"{scenario_results['best_case']['variance']:+.0f} days"
        },
        {
            'scenario': 'Likely Case (base)',
            'duration': f"{scenario_results['likely_case']['duration']:.0f} days",
            'variance': f"{scenario_results['likely_case']['variance']:+.0f} days"
        },
        {
            'scenario': 'Worst Case (30% slower)',
            'duration': f"{scenario_results['worst_case']['duration']:.0f} days",
            'variance': f"{scenario_results['worst_case']['variance']:+.0f} days"
        }
    ]

    report += format_markdown_table(
        scenario_table,
        ['scenario', 'duration', 'variance'],
        ['left', 'center', 'center']
    )
    report += "\n\n"

    report += f"**Range:** {scenario_results['range']:.0f} days "
    report += f"({scenario_results['best_case']['duration']:.0f} - "
    report += f"{scenario_results['worst_case']['duration']:.0f} days)\n\n"

    report += f"**Probability-Weighted Duration:** "
    report += f"{scenario_results['probability_weighted_duration']:.0f} days\n\n"

    # Milestones
    report += "## Key Milestones\n\n"

    milestones = []
    for task_id, details in timeline['task_details'].items():
        # Include critical path tasks and tasks with deadlines as milestones
        if details['is_critical'] or task_id in deadlines:
            milestone_date = 'TBD'
            if start_date:
                try:
                    start = datetime.strptime(start_date, '%Y-%m-%d')
                    milestone = start + timedelta(days=details['early_finish'])
                    milestone_date = milestone.strftime('%Y-%m-%d')
                except:
                    pass

            milestones.append({
                'milestone': details['name'],
                'target_date': milestone_date,
                'day': f"Day {details['early_finish']:.0f}"
            })

    # Sort by completion day
    milestones.sort(key=lambda x: float(x['day'].replace('Day ', '')))

    report += format_markdown_table(
        milestones,
        ['milestone', 'target_date', 'day'],
        ['left', 'center', 'center']
    )
    report += "\n\n"

    return report


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python timeline_generator.py <input_json> [--output <path>]")
        print("\nExample:")
        print("  python timeline_generator.py samples/sample_2_complex_corridor.json")
        print("  python timeline_generator.py input.json --output Reports/timeline.md")
        sys.exit(1)

    input_path = sys.argv[1]

    # Parse output path
    output_path = None
    if '--output' in sys.argv:
        output_idx = sys.argv.index('--output')
        if output_idx + 1 < len(sys.argv):
            output_path = sys.argv[output_idx + 1]

    try:
        # Load input
        print(f"Loading input from {input_path}...")
        input_data = load_input(input_path)

        # Generate report
        print("Generating timeline analysis...")
        report = generate_timeline_report(input_data)

        # Write output
        if output_path:
            with open(output_path, 'w') as f:
                f.write(report)
            print(f"\nReport saved to: {output_path}")
        else:
            print("\n" + "="*80)
            print(report)
            print("="*80)

        print("\nTimeline analysis complete!")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
