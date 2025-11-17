#!/usr/bin/env python3
"""
Title Analyzer - Comprehensive Title Search Analysis

Analyzes registered instruments, encumbrances, registration defects, and
assesses property marketability with value impact estimates.

Usage:
    python title_analyzer.py <input.json> [--output report.md] [--json results.json]

Features:
    - Parse registered instruments (easements, covenants, liens, restrictions)
    - Analyze encumbrance impact (type, priority, use restrictions, value impact)
    - Detect registration defects (improper descriptions, missing parties, signatures)
    - Assess marketability (buyer pool impact, liquidity, financing availability)
    - Calculate value impact estimates (percentage discounts)
    - Recommend remedial actions (discharges, postponements, rectifications)

Author: Claude Code
Date: November 17, 2025
Version: 1.0.0
"""

import sys
import argparse
from pathlib import Path
from typing import Dict

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / 'modules'))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'Shared_Utils'))

# Import modules
from validators import (
    load_and_validate_input,
    validate_output_paths,
    validate_instrument_data_quality
)
from title_parsing import parse_registered_instruments
from encumbrance_analysis import analyze_encumbrances
from registration_validation import validate_registration
from marketability_assessment import (
    assess_marketability,
    calculate_value_impact
)
from output_formatters import (
    generate_markdown_report,
    generate_json_output,
    save_markdown_report,
    save_json_output,
    get_eastern_timestamp
)


def run_title_analysis(input_data: Dict) -> Dict:
    """
    Run complete title analysis.

    Args:
        input_data: Validated input data dictionary

    Returns:
        Dictionary containing all analysis results
    """
    print("Starting title analysis...")

    # Extract data
    instruments = input_data['registered_instruments']
    restrictions = input_data.get('restrictions', [])
    encumbrances = input_data.get('encumbrances', [])
    defects = input_data.get('defects', [])
    property_data = {
        'property_identifier': input_data['property_identifier'],
        'property_address': input_data['property_address']
    }

    # 1. Parse registered instruments
    print("Parsing registered instruments...")
    parsed_instruments = parse_registered_instruments(instruments)
    print(f"  - Parsed {parsed_instruments['summary']['total_instruments']} instruments")
    print(f"  - Identified {len(parsed_instruments['critical'])} critical instruments")

    # 2. Analyze encumbrances
    print("Analyzing encumbrances...")
    encumbrance_analysis = analyze_encumbrances(
        parsed_instruments['by_priority'],
        restrictions,
        encumbrances
    )
    print(f"  - Total encumbrances: {encumbrance_analysis['summary']['total']}")
    print(f"  - Critical issues: {len(encumbrance_analysis['critical_issues'])}")
    print(f"  - High severity: {len(encumbrance_analysis['high_issues'])}")

    # 3. Validate registration
    print("Validating registration compliance...")
    validation_results = validate_registration(
        parsed_instruments['by_priority'],
        defects
    )
    print(f"  - Registration status: {validation_results['validity']['status']}")
    print(f"  - Defects found: {validation_results['summary']['total_defects']}")

    # 4. Assess marketability
    print("Assessing marketability...")
    marketability = assess_marketability(
        encumbrance_analysis,
        validation_results,
        property_data
    )
    print(f"  - Marketability rating: {marketability['rating']}")
    print(f"  - Overall score: {marketability['overall_score']:.1f}/100")

    # 5. Calculate value impact
    print("Calculating value impact...")
    value_impact = calculate_value_impact(
        marketability,
        encumbrance_analysis
    )
    print(f"  - Estimated discount: {value_impact['likely_discount_pct']:.1f}%")
    print(f"  - Range: {value_impact['min_discount_pct']:.1f}% - {value_impact['max_discount_pct']:.1f}%")

    # 6. Assess data quality
    print("Assessing data quality...")
    data_quality = validate_instrument_data_quality(instruments)
    print(f"  - Quality score: {data_quality['completeness']}")

    return {
        'parsed_instruments': parsed_instruments,
        'encumbrance_analysis': encumbrance_analysis,
        'validation_results': validation_results,
        'marketability': marketability,
        'value_impact': value_impact,
        'data_quality': data_quality
    }


def generate_reports(
    property_id: str,
    property_address: str,
    results: Dict,
    warnings: list,
    output_md: str = None,
    output_json: str = None
) -> None:
    """
    Generate markdown and JSON reports.

    Args:
        property_id: Property identifier
        property_address: Property address
        results: Analysis results dictionary
        warnings: Validation warnings
        output_md: Markdown output path (optional)
        output_json: JSON output path (optional)
    """
    print("\nGenerating reports...")

    # Generate markdown report
    markdown_report = generate_markdown_report(
        property_id,
        property_address,
        results['parsed_instruments'],
        results['encumbrance_analysis'],
        results['validation_results'],
        results['marketability'],
        results['value_impact'],
        warnings,
        results['data_quality']
    )

    # Save or print markdown
    if output_md:
        save_markdown_report(markdown_report, output_md)
    else:
        # Print to stdout
        print("\n" + "="*80)
        print(markdown_report)
        print("="*80)

    # Generate JSON output
    if output_json:
        json_data = generate_json_output(
            property_id,
            property_address,
            results['parsed_instruments'],
            results['encumbrance_analysis'],
            results['validation_results'],
            results['marketability'],
            results['value_impact'],
            warnings,
            results['data_quality']
        )
        save_json_output(json_data, output_json)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Title Analyzer - Comprehensive Title Search Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic analysis (output to stdout)
    python title_analyzer.py input.json

    # Generate markdown report
    python title_analyzer.py input.json --output report.md

    # Generate both markdown and JSON
    python title_analyzer.py input.json --output report.md --json results.json

    # Auto-generate output filenames with timestamp
    python title_analyzer.py input.json --auto-output
        """
    )

    parser.add_argument(
        'input',
        help='Path to input JSON file'
    )
    parser.add_argument(
        '--output',
        '-o',
        help='Path to markdown output file (optional)'
    )
    parser.add_argument(
        '--json',
        '-j',
        help='Path to JSON output file (optional)'
    )
    parser.add_argument(
        '--auto-output',
        '-a',
        action='store_true',
        help='Auto-generate output filenames with timestamp'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    try:
        # Load and validate input
        print(f"Loading input file: {args.input}")
        input_data, warnings = load_and_validate_input(args.input)

        if warnings:
            print(f"\nValidation warnings ({len(warnings)}):")
            for warning in warnings[:5]:  # Show first 5
                print(f"  - {warning}")
            if len(warnings) > 5:
                print(f"  ... and {len(warnings) - 5} more")

        # Determine output paths
        output_md = args.output
        output_json = args.json

        if args.auto_output:
            timestamp = get_eastern_timestamp()
            base_name = f"{timestamp}_title_analysis"
            output_md = f"Reports/{base_name}.md"
            output_json = f"Reports/{base_name}.json"

        # Validate output paths
        if output_md or output_json:
            validate_output_paths(output_md, output_json)

        # Run analysis
        results = run_title_analysis(input_data)

        # Generate reports
        generate_reports(
            input_data['property_identifier'],
            input_data['property_address'],
            results,
            warnings,
            output_md,
            output_json
        )

        print("\nTitle analysis completed successfully!")

        # Summary output
        print("\n" + "="*80)
        print("ANALYSIS SUMMARY")
        print("="*80)
        print(f"Property: {input_data['property_address']}")
        print(f"Marketability: {results['marketability']['rating']} ({results['marketability']['overall_score']:.1f}/100)")
        print(f"Value Impact: {results['value_impact']['likely_discount_pct']:.1f}% discount")
        print(f"Critical Issues: {len(results['encumbrance_analysis']['critical_issues'])}")
        print(f"Registration Status: {results['validation_results']['validity']['status']}")
        print("="*80)

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Validation error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
