#!/usr/bin/env python3
"""
Utility Conflict Analyzer
Thin orchestration layer for utility conflict detection and relocation analysis

ARCHITECTURE:
- Main file: Thin orchestration (<400 lines)
- modules/: All business logic
- Shared_Utils/: Reusable financial, timeline, report utilities

USAGE:
    python utility_conflict_analyzer.py <input.json> [--output report.md] [--verbose]

INPUT: JSON with project alignment, existing utilities, design constraints
OUTPUT: Conflict analysis report with relocation requirements and costs
"""

import json
import sys
import os
import argparse
from typing import Dict, List, Any

# Add parent directories to path for imports
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

# Import modules
from modules import (
    validate_input_data,
    sanitize_input,
    detect_conflicts,
    generate_conflict_matrix,
    get_conflicts_by_severity,
    generate_relocation_requirements,
    estimate_relocation_costs,
    format_conflict_report
)

# Import Shared_Utils
from Shared_Utils.timeline_utils import calculate_critical_path
from Shared_Utils.report_utils import eastern_timestamp


def load_input_data(input_path: str) -> Dict[str, Any]:
    """
    Load and validate input JSON data

    Args:
        input_path: Path to input JSON file

    Returns:
        Validated input data dictionary

    Raises:
        FileNotFoundError: If input file doesn't exist
        json.JSONDecodeError: If JSON is invalid
        ValueError: If validation fails
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_path, 'r') as f:
        data = json.load(f)

    # Validate input
    is_valid, errors = validate_input_data(data)
    if not is_valid:
        error_msg = "Input validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
        raise ValueError(error_msg)

    # Sanitize and normalize
    return sanitize_input(data)


def analyze_utility_conflicts(input_data: Dict[str, Any], verbose: bool = False) -> Dict[str, Any]:
    """
    Main analysis workflow

    Args:
        input_data: Validated input data
        verbose: Print progress messages

    Returns:
        Complete analysis results dictionary
    """
    if verbose:
        print("Starting utility conflict analysis...")

    # Extract data
    project_alignment = input_data['project_alignment']
    utilities = input_data['existing_utilities']
    design_constraints = input_data.get('design_constraints', {})

    # Step 1: Detect conflicts
    if verbose:
        print(f"Analyzing {len(utilities)} utilities for conflicts...")

    conflicts = detect_conflicts(project_alignment, utilities, design_constraints)

    if verbose:
        print(f"Found {len(conflicts)} conflicts")

    # Step 2: Generate conflict matrix
    conflict_matrix = generate_conflict_matrix(conflicts)
    conflicts_by_severity = get_conflicts_by_severity(conflicts)

    # Step 3: Generate relocation requirements
    if verbose:
        print("Generating relocation requirements...")

    relocation_requirements = generate_relocation_requirements(conflicts, utilities)

    # Step 4: Estimate costs
    if verbose:
        print("Estimating relocation costs...")

    cost_estimate = estimate_relocation_costs(relocation_requirements, utilities)

    # Step 5: Calculate timeline and critical path
    if verbose:
        print("Calculating critical path timeline...")

    timeline_data = _calculate_project_timeline(relocation_requirements)

    if verbose:
        print("Analysis complete")

    return {
        'project_data': input_data,
        'conflicts': conflicts,
        'conflict_matrix': conflict_matrix,
        'conflicts_by_severity': conflicts_by_severity,
        'relocation_requirements': relocation_requirements,
        'cost_estimate': cost_estimate,
        'timeline_data': timeline_data,
        'summary': {
            'total_conflicts': len(conflicts),
            'critical_conflicts': len(conflicts_by_severity['CRITICAL']),
            'high_conflicts': len(conflicts_by_severity['HIGH']),
            'estimated_cost_range': {
                'low': cost_estimate['total_range']['low'],
                'high': cost_estimate['total_range']['high']
            },
            'critical_path_months': timeline_data['critical_path_duration']
        }
    }


def _calculate_project_timeline(relocation_requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate project timeline and critical path

    Args:
        relocation_requirements: List of relocation requirements

    Returns:
        Timeline data with critical path
    """
    # Build tasks and dependencies
    tasks = []
    dependencies = []

    # Add design phase
    tasks.append({
        'id': 'design',
        'name': 'Preliminary Design',
        'duration': 60,  # 2 months in days
        'optimistic': 45,
        'most_likely': 60,
        'pessimistic': 75
    })

    # Add utility coordination
    tasks.append({
        'id': 'coordination',
        'name': 'Utility Owner Coordination',
        'duration': 90,  # 3 months in days
        'optimistic': 60,
        'most_likely': 90,
        'pessimistic': 120
    })
    dependencies.append(('design', 'coordination'))

    # Add each utility relocation
    for idx, req in enumerate(relocation_requirements):
        # Parse duration (e.g., "12-18 months" -> 18)
        duration_str = req['estimated_duration']
        if '-' in duration_str:
            duration_months = int(duration_str.split('-')[1].split()[0])
        else:
            duration_months = int(duration_str.split()[0])

        duration_days = duration_months * 30
        task_id = f"utility_{idx}"

        tasks.append({
            'id': task_id,
            'name': f"{req['owner']} - {req['relocation_type']}",
            'duration': duration_days,
            'optimistic': int(duration_days * 0.8),
            'most_likely': duration_days,
            'pessimistic': int(duration_days * 1.3),
            'critical_path_impact': req.get('critical_path_impact', False)
        })
        dependencies.append(('coordination', task_id))

    # Calculate critical path if we have dependencies
    if len(tasks) > 0:
        critical_path_result = calculate_critical_path(tasks, dependencies)
        critical_path_days = critical_path_result['project_duration']
        critical_path_months = critical_path_days / 30
    else:
        critical_path_months = 0

    # Get critical activities
    critical_activities = [
        {
            'name': t['name'],
            'duration': t['duration'] / 30,  # Convert back to months
            'dependencies': [dep[0] for dep in dependencies if dep[1] == t['id']]
        }
        for t in tasks if t.get('critical_path_impact', False)
    ]

    return {
        'activities': tasks,
        'critical_path_duration': int(critical_path_months),
        'critical_activities': critical_activities,
        'total_duration': int(critical_path_months)
    }


def generate_report(analysis_results: Dict[str, Any]) -> str:
    """
    Generate formatted markdown report

    Args:
        analysis_results: Complete analysis results

    Returns:
        Formatted markdown report string
    """
    return format_conflict_report(
        project_data=analysis_results['project_data'],
        conflicts=analysis_results['conflicts'],
        conflict_matrix=analysis_results['conflict_matrix'],
        relocation_requirements=analysis_results['relocation_requirements'],
        cost_estimate=analysis_results['cost_estimate'],
        timeline_data=analysis_results['timeline_data']
    )


def save_results(
    analysis_results: Dict[str, Any],
    output_path: str = None,
    verbose: bool = False
) -> str:
    """
    Save analysis results to files

    Args:
        analysis_results: Complete analysis results
        output_path: Optional output path for markdown report
        verbose: Print progress messages

    Returns:
        Path to saved markdown report
    """
    # Generate report
    report = generate_report(analysis_results)

    # Determine output path
    if output_path is None:
        timestamp = eastern_timestamp().replace(':', '').replace('-', '').replace(' ', '_')
        output_path = f"/workspaces/lease-abstract/Reports/{timestamp}_utility_conflict_analysis.md"

    # Ensure Reports directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save markdown report
    with open(output_path, 'w') as f:
        f.write(report)

    if verbose:
        print(f"\nReport saved to: {output_path}")

    # Also save JSON results
    json_path = output_path.replace('.md', '.json')
    with open(json_path, 'w') as f:
        json.dump(analysis_results, f, indent=2, default=str)

    if verbose:
        print(f"JSON data saved to: {json_path}")

    return output_path


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Utility Conflict Analyzer - Detect conflicts and estimate relocation costs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze utility conflicts
  python utility_conflict_analyzer.py input.json

  # Save to specific output file
  python utility_conflict_analyzer.py input.json --output report.md

  # Verbose mode
  python utility_conflict_analyzer.py input.json --verbose
        """
    )

    parser.add_argument(
        'input_file',
        help='Path to input JSON file with project and utility data'
    )

    parser.add_argument(
        '--output', '-o',
        help='Output path for markdown report (default: auto-generated in Reports/)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Print verbose progress messages'
    )

    args = parser.parse_args()

    try:
        # Load input data
        if args.verbose:
            print(f"Loading input from: {args.input_file}")

        input_data = load_input_data(args.input_file)

        # Run analysis
        analysis_results = analyze_utility_conflicts(input_data, verbose=args.verbose)

        # Save results
        report_path = save_results(
            analysis_results,
            output_path=args.output,
            verbose=args.verbose
        )

        # Print summary
        summary = analysis_results['summary']
        print(f"\n{'='*60}")
        print("UTILITY CONFLICT ANALYSIS SUMMARY")
        print(f"{'='*60}")
        print(f"Total Conflicts: {summary['total_conflicts']}")
        print(f"  - Critical: {summary['critical_conflicts']}")
        print(f"  - High: {summary['high_conflicts']}")
        print(f"\nEstimated Cost: ${summary['estimated_cost_range']['low']:,.0f} - ${summary['estimated_cost_range']['high']:,.0f}")
        print(f"Critical Path: {summary['critical_path_months']} months")
        print(f"\nReport: {report_path}")
        print(f"{'='*60}\n")

        return 0

    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in input file: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
