#!/usr/bin/env python3
"""
Expropriation Project Timeline Calculator

Calculates critical path schedule with OEA statutory deadlines using PERT/CPM methodology.

Features:
- Critical path analysis (CPM)
- PERT time estimates (optimistic/most_likely/pessimistic)
- Statutory deadline tracking (OEA s.9, s.11)
- Risk assessment (deadline compliance, float analysis)
- Resource requirements calculation
- Gantt chart visualization

Author: Claude Code
Version: 1.0.0
Date: 2025-11-17
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add modules to path
modules_path = Path(__file__).resolve().parent / 'modules'
shared_utils_path = Path(__file__).resolve().parents[2] / 'Shared_Utils'

if str(modules_path) not in sys.path:
    sys.path.insert(0, str(modules_path))
if str(shared_utils_path) not in sys.path:
    sys.path.insert(0, str(shared_utils_path))

from validators import validate_timeline_input
from critical_path import (
    calculate_critical_path_analysis,
    enrich_tasks_with_pert,
    calculate_project_variance,
    calculate_project_confidence_interval
)
from dependencies import analyze_dependency_complexity
from statutory_deadlines import (
    calculate_registration_deadline,
    calculate_days_remaining,
    assess_deadline_risk,
    generate_oea_timeline_milestones
)
from output_formatters import (
    format_timeline_report,
    format_json_output,
    generate_output_filename
)
import timeline_utils


def load_input_data(input_path: str) -> Dict:
    """
    Load and validate timeline input data.

    Args:
        input_path: Path to input JSON file

    Returns:
        Validated input data dict

    Raises:
        ValueError: If validation fails
    """
    # Load JSON
    with open(input_path, 'r') as f:
        data = json.load(f)

    # Validate
    is_valid, errors = validate_timeline_input(data)

    if not is_valid:
        error_msg = "Input validation failed:\n" + "\n".join(f"  - {err}" for err in errors)
        raise ValueError(error_msg)

    return data


def calculate_timeline(input_data: Dict) -> Dict:
    """
    Calculate complete timeline analysis.

    Args:
        input_data: Validated input data dict

    Returns:
        Complete analysis results dict
    """
    results = {}

    # Extract input
    project_name = input_data['project_name']
    approval_date = input_data['approval_date']
    tasks = input_data['tasks']
    dependencies = input_data['dependencies']
    statutory_deadlines = input_data.get('statutory_deadlines', {})
    buffer_days = input_data.get('buffer_days', 10)

    # Enrich tasks with PERT calculations
    tasks = enrich_tasks_with_pert(tasks)

    # Calculate critical path
    cp_analysis = calculate_critical_path_analysis(tasks, dependencies)
    results['critical_path_analysis'] = cp_analysis

    # Calculate PERT variance and confidence interval
    task_dict = {task['id']: task for task in tasks}
    critical_path = cp_analysis['critical_path']
    project_variance = calculate_project_variance(critical_path, task_dict)
    project_duration = cp_analysis['project_duration']

    confidence_interval = calculate_project_confidence_interval(
        project_duration,
        project_variance,
        confidence_level=0.90
    )
    results['confidence_interval'] = confidence_interval
    results['project_variance'] = project_variance

    # Statutory deadline analysis
    statutory_analysis = {}

    # Registration deadline
    statutory_analysis['registration_deadline'] = calculate_registration_deadline(approval_date)

    # Days remaining
    statutory_analysis['days_remaining'] = calculate_days_remaining(approval_date)

    # OEA milestones
    statutory_analysis['milestones'] = generate_oea_timeline_milestones(approval_date)

    results['statutory_analysis'] = statutory_analysis

    # Risk assessment
    risks = timeline_utils.identify_risk_flags(
        cp_analysis,
        statutory_deadlines,
        buffer_days
    )

    # Add statutory deadline risks
    task_details = cp_analysis['task_details']
    for task_id, deadline in statutory_deadlines.items():
        if task_id in task_details:
            task = task_details[task_id]
            risk_assessment = assess_deadline_risk(
                task['late_finish'],
                deadline,
                buffer_days
            )

            if risk_assessment['severity'] in ['CRITICAL', 'HIGH', 'MEDIUM']:
                risks.append({
                    'task_id': task_id,
                    'task_name': task['name'],
                    'risk_type': 'STATUTORY_DEADLINE',
                    'severity': risk_assessment['severity'],
                    'late_finish': task['late_finish'],
                    'statutory_deadline': deadline,
                    'buffer': risk_assessment['buffer_days'],
                    'message': risk_assessment['message']
                })

    results['risks'] = risks

    # Resource requirements
    task_resources = {
        task['id']: task.get('resources', {})
        for task in tasks
        if 'resources' in task
    }

    if task_resources:
        resources = timeline_utils.calculate_resource_requirements(cp_analysis, task_resources)
        results['resources'] = resources

    # Dependency analysis
    dep_analysis = analyze_dependency_complexity(tasks, dependencies)
    results['dependency_analysis'] = dep_analysis

    # Gantt chart data
    gantt_data = []
    for task_id, details in task_details.items():
        gantt_data.append({
            'name': f"{details['name']} ({task_id})",
            'start': details['early_start'],
            'finish': details['early_finish'],
            'duration': details['duration'],
            'is_critical': details['is_critical']
        })

    # Sort by start time
    gantt_data.sort(key=lambda x: x['start'])
    results['gantt_data'] = gantt_data

    # Add metadata
    results['metadata'] = {
        'project_name': project_name,
        'approval_date': approval_date,
        'analysis_date': statutory_analysis['days_remaining']['current_date']
    }

    return results


def generate_report(
    results: Dict,
    output_path: Optional[str] = None,
    format: str = 'markdown'
) -> str:
    """
    Generate timeline analysis report.

    Args:
        results: Analysis results dict
        output_path: Optional output file path
        format: Output format ('markdown' or 'json')

    Returns:
        Report content (markdown or JSON string)
    """
    project_name = results['metadata']['project_name']

    if format == 'json':
        content = format_json_output(results)
    else:
        content = format_timeline_report(project_name, results)

    # Write to file if path provided
    if output_path:
        with open(output_path, 'w') as f:
            f.write(content)

    return content


def main():
    """Main entry point for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Calculate expropriation project timeline with critical path analysis'
    )
    parser.add_argument(
        'input_file',
        help='Path to timeline input JSON file'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file path (default: auto-generated in Reports/)'
    )
    parser.add_argument(
        '-f', '--format',
        choices=['markdown', 'json'],
        default='markdown',
        help='Output format (default: markdown)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    try:
        # Load input
        if args.verbose:
            print(f"Loading input from {args.input_file}...")

        input_data = load_input_data(args.input_file)

        # Calculate timeline
        if args.verbose:
            print("Calculating critical path...")

        results = calculate_timeline(input_data)

        # Generate output path if not provided
        output_path = args.output
        if not output_path:
            reports_dir = Path(__file__).resolve().parents[2] / 'Reports'
            reports_dir.mkdir(exist_ok=True)

            filename = generate_output_filename(
                input_data['project_name'],
                'md' if args.format == 'markdown' else 'json'
            )
            output_path = reports_dir / filename

        # Generate report
        if args.verbose:
            print(f"Generating {args.format} report...")

        content = generate_report(results, str(output_path), args.format)

        print(f"\nTimeline analysis complete!")
        print(f"Output written to: {output_path}")

        # Print summary
        cp_analysis = results['critical_path_analysis']
        print(f"\nProject Duration: {cp_analysis['project_duration']:.0f} days")
        print(f"Critical Path: {cp_analysis['num_critical_tasks']} of {cp_analysis['num_total_tasks']} tasks")

        # Print risks
        risks = results.get('risks', [])
        critical_risks = [r for r in risks if r.get('severity') == 'CRITICAL']
        high_risks = [r for r in risks if r.get('severity') == 'HIGH']

        if critical_risks or high_risks:
            print(f"\nTimeline Risks: {len(critical_risks)} critical, {len(high_risks)} high")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
