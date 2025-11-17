#!/usr/bin/env python3
"""
Land Assembly Calculator - Multi-Parcel Acquisition Analysis

This calculator implements comprehensive land assembly analysis for 10-100+ parcels,
including phasing strategy, budget analysis, resource allocation, and cost of delay.

Usage:
    python land_assembly_calculator.py <input.json> [--output report.md] [--json results.json]

Features:
    - Acquisition phasing strategy (critical path, parallel tracks)
    - Multi-parcel budget with contingencies
    - Resource allocation planning (appraisers, negotiators, legal)
    - Cost of delay analysis
    - Risk assessment integration

Author: Claude Code
Date: November 17, 2025
Version: 1.0.0
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / 'modules'))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'Shared_Utils'))

# Import modules
from validators import load_and_validate_input
from phasing import (
    generate_phasing_strategy,
    format_phasing_output,
    get_critical_path_parcels
)
from budgeting import (
    calculate_budget,
    calculate_delay_cost,
    calculate_resource_allocation,
    format_budget_output,
    format_resource_output,
    format_delay_cost_output
)
from output_formatters import (
    generate_markdown_report,
    generate_json_output,
    save_json_output,
    save_markdown_report,
    format_summary_table,
    format_warnings,
    get_eastern_timestamp
)


def run_analysis(input_data: Dict) -> Dict:
    """
    Run complete land assembly analysis.

    Args:
        input_data: Validated input data dictionary

    Returns:
        Dictionary containing all analysis results
    """
    parcels = input_data['parcels']
    priorities = input_data['priorities']
    resources = input_data['resources']
    contingencies = input_data['contingencies']
    delay_params = input_data.get('delay_analysis', {})

    # 1. Phasing Strategy
    print("Calculating phasing strategy...")
    phasing_result = generate_phasing_strategy(parcels, priorities)

    # 2. Budget Analysis
    print("Calculating budget...")
    budget_result = calculate_budget(parcels, contingencies)

    # 3. Resource Allocation
    print("Calculating resource allocation...")
    resource_result = calculate_resource_allocation(parcels, resources)

    # 4. Cost of Delay (if critical parcels exist)
    delay_result = None
    critical_parcels = get_critical_path_parcels(phasing_result)
    if critical_parcels and delay_params:
        print("Calculating cost of delay...")
        # Get critical parcel objects
        delayed_parcels = [p for p in parcels if p['id'] in critical_parcels]
        if delayed_parcels:
            delay_result = calculate_delay_cost(delayed_parcels, delay_params)

    return {
        'phasing': phasing_result,
        'budget': budget_result,
        'resources': resource_result,
        'delay': delay_result
    }


def generate_reports(
    project_name: str,
    results: Dict,
    input_data: Dict,
    warnings: List[str],
    output_md: str = None,
    output_json: str = None
):
    """
    Generate markdown and JSON reports.

    Args:
        project_name: Project name
        results: Analysis results dictionary
        input_data: Original input data
        warnings: Validation warnings
        output_md: Markdown output path (optional)
        output_json: JSON output path (optional)
    """
    # Format sections
    phasing_output = format_phasing_output(results['phasing'])
    budget_output = format_budget_output(results['budget'])
    resource_output = format_resource_output(results['resources'])

    delay_output = None
    if results.get('delay'):
        delay_output = format_delay_cost_output(results['delay'])

    # Generate summary
    summary_table = format_summary_table(
        results['phasing'],
        results['budget'],
        results['resources']
    )

    # Metadata
    metadata = {
        'project_type': input_data.get('project_type', 'N/A'),
        'num_parcels': len(input_data['parcels']),
        'total_value': sum(p.get('estimated_value', 0) for p in input_data['parcels'])
    }

    # Generate markdown report
    warnings_output = format_warnings(warnings)

    markdown_sections = []
    if warnings_output:
        markdown_sections.append(warnings_output)
    markdown_sections.append(summary_table)
    markdown_sections.append(phasing_output)
    markdown_sections.append(budget_output)
    markdown_sections.append(resource_output)
    if delay_output:
        markdown_sections.append(delay_output)

    markdown_report = generate_markdown_report(
        project_name,
        '\n---\n'.join(markdown_sections),
        "",  # budget already included
        "",  # resources already included
        None,  # delay already included
        metadata
    )

    # Generate JSON output
    json_output = generate_json_output(
        project_name,
        results['phasing'],
        results['budget'],
        results['resources'],
        results.get('delay'),
        input_data
    )

    # Save outputs
    if output_md:
        save_markdown_report(markdown_report, output_md)
        print(f"Markdown report saved to: {output_md}")
    else:
        # Print to stdout
        print("\n" + "=" * 80)
        print(markdown_report)
        print("=" * 80)

    if output_json:
        save_json_output(json_output, output_json)
        print(f"JSON output saved to: {output_json}")

    return markdown_report, json_output


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Land Assembly Calculator - Multi-parcel acquisition analysis'
    )
    parser.add_argument(
        'input',
        help='Path to input JSON file'
    )
    parser.add_argument(
        '--output',
        help='Path to output markdown report (optional, prints to stdout if not provided)'
    )
    parser.add_argument(
        '--json',
        help='Path to output JSON file (optional)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    try:
        # Load and validate input
        print(f"Loading input from: {args.input}")
        input_data, warnings = load_and_validate_input(args.input)

        if warnings:
            print("\nWarnings:")
            for warning in warnings:
                print(f"  - {warning}")

        # Run analysis
        print("\nRunning analysis...")
        results = run_analysis(input_data)

        # Generate reports
        print("\nGenerating reports...")
        project_name = input_data.get('project_name', 'Land Assembly Project')

        # Auto-generate output paths if not provided
        output_md = args.output
        output_json = args.json

        if not output_md and args.json:
            # If JSON specified but not markdown, still save markdown
            timestamp = get_eastern_timestamp()
            output_md = f"{timestamp}_{project_name.replace(' ', '_').lower()}_report.md"

        generate_reports(
            project_name,
            results,
            input_data,
            warnings,
            output_md,
            output_json
        )

        print("\nAnalysis complete!")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
