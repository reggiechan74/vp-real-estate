#!/usr/bin/env python3
"""
Executive Briefing Note Generator
Generates executive briefing notes (1-2 pages, decision-focused) for infrastructure acquisition projects

Usage:
    python briefing_note_generator.py input.json [--output briefing_note.md] [--verbose]

Input Schema:
    See briefing_note_input_schema.json for complete schema definition

Output:
    Executive briefing note in markdown format with:
    - Issue/decision required
    - Background and context
    - Analysis with financial summary
    - Recommendation with risk assessment
    - Action items and timeline
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, Optional
import os

# Add directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
modules_dir = os.path.join(current_dir, 'modules')
skills_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(os.path.dirname(skills_dir))

sys.path.insert(0, modules_dir)
sys.path.insert(0, root_dir)

from modules.validators import (
    validate_briefing_note_input,
    validate_financial_consistency,
    validate_timeline_logic,
    validate_risk_assessment
)

from modules.analysis import (
    analyze_decision_urgency,
    analyze_alternatives,
    analyze_strategic_alignment,
    calculate_overall_risk_score
)

from modules.output_formatters import generate_briefing_note

from Shared_Utils.report_utils import eastern_timestamp


def load_input_data(input_path: str) -> Dict:
    """
    Load and parse input JSON file.

    Args:
        input_path: Path to input JSON file

    Returns:
        Parsed input data dictionary

    Raises:
        FileNotFoundError: If input file doesn't exist
        json.JSONDecodeError: If input is not valid JSON
    """
    input_file = Path(input_path)

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data


def validate_input(data: Dict, verbose: bool = False) -> bool:
    """
    Validate input data against schema and business rules.

    Args:
        data: Input data dictionary
        verbose: Print detailed validation messages

    Returns:
        True if validation passes, False otherwise
    """
    all_valid = True

    # Schema validation
    is_valid, errors = validate_briefing_note_input(data)

    if not is_valid:
        print("❌ VALIDATION ERRORS:")
        for error in errors:
            print(f"   - {error}")
        all_valid = False
    elif verbose:
        print("✅ Schema validation passed")

    # Financial consistency validation
    if 'financial_summary' in data:
        is_valid, warnings = validate_financial_consistency(data['financial_summary'])
        if not is_valid and verbose:
            print("⚠️  FINANCIAL WARNINGS:")
            for warning in warnings:
                print(f"   - {warning}")

    # Timeline logic validation
    if 'background' in data:
        is_valid, errors = validate_timeline_logic(data['background'])
        if not is_valid:
            print("❌ TIMELINE ERRORS:")
            for error in errors:
                print(f"   - {error}")
            all_valid = False
        elif verbose:
            print("✅ Timeline validation passed")

    # Risk assessment validation
    if 'risks' in data:
        is_valid, warnings = validate_risk_assessment(data['risks'])
        if not is_valid and verbose:
            print("⚠️  RISK ASSESSMENT WARNINGS:")
            for warning in warnings:
                print(f"   - {warning}")

    return all_valid


def generate_output_filename(data: Dict, output_path: Optional[str] = None) -> str:
    """
    Generate output filename with timestamp prefix.

    Args:
        data: Input data dictionary
        output_path: Optional output path provided by user

    Returns:
        Output file path
    """
    if output_path:
        return output_path

    # Generate filename from project name
    project_name = data.get('project_name', 'briefing_note')
    # Sanitize filename
    safe_name = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in project_name)
    safe_name = safe_name.replace(' ', '_').lower()

    # Add timestamp prefix
    timestamp = eastern_timestamp(include_time=True)
    filename = f"{timestamp}_briefing_note_{safe_name}.md"

    # Save to Reports directory
    reports_dir = Path(__file__).parent.parent.parent.parent / 'Reports'
    reports_dir.mkdir(exist_ok=True)

    return str(reports_dir / filename)


def print_summary(data: Dict, verbose: bool = False):
    """
    Print summary of analysis results.

    Args:
        data: Input data dictionary
        verbose: Print detailed summary
    """
    print("\n" + "="*70)
    print("BRIEFING NOTE ANALYSIS SUMMARY")
    print("="*70)

    # Project info
    print(f"\nProject: {data.get('project_name', 'N/A')}")
    print(f"Issue: {data.get('issue', 'N/A')}")

    # Financial summary
    financial = data.get('financial_summary', {})
    total_cost = financial.get('total_cost', 0)
    print(f"\nTotal Cost: ${total_cost:,.2f}")

    budget_comparison = financial.get('budget_comparison', {})
    if budget_comparison.get('approved_budget'):
        variance = budget_comparison.get('variance', 0)
        variance_pct = budget_comparison.get('variance_pct', 0)
        print(f"Budget Variance: ${abs(variance):,.2f} ({'over' if variance > 0 else 'under'} budget, {abs(variance_pct):.1f}%)")

    # Urgency analysis
    urgency_analysis = analyze_decision_urgency(data)
    print(f"\nUrgency: {urgency_analysis['urgency_level'].upper()} (Score: {urgency_analysis['urgency_score']}/100)")

    # Strategic analysis
    strategic_analysis = analyze_strategic_alignment(data)
    print(f"Strategic Alignment: {strategic_analysis['strategic_score']}/100")
    print(f"Benefits Identified: {strategic_analysis['benefits_count']}")
    print(f"Precedents: {strategic_analysis['precedents_count']}")

    # Alternatives analysis
    alternatives_analysis = analyze_alternatives(data)
    print(f"Alternatives Evaluated: {alternatives_analysis['alternatives_count']}")

    # Risk analysis
    risks = data.get('risks', [])
    if risks:
        risk_score = calculate_overall_risk_score(risks)
        print(f"\nOverall Risk: {risk_score['risk_level']} (Score: {risk_score['overall_score']}/100)")
        print(f"Risk Distribution: {risk_score['critical_count']} Critical, {risk_score['high_count']} High, {risk_score['medium_count']} Medium, {risk_score['low_count']} Low")

    # Action items
    action_items = data.get('action_items', [])
    if action_items:
        high_priority = len([a for a in action_items if a.get('priority') == 'HIGH'])
        print(f"\nAction Items: {len(action_items)} total, {high_priority} high priority")

    # Recommendation
    print(f"\nRecommendation: {data.get('recommendation', 'N/A')}")

    if verbose:
        print("\n" + "-"*70)
        print("DETAILED ANALYSIS")
        print("-"*70)

        # Key constraints
        if urgency_analysis['key_constraints']:
            print("\nKey Constraints:")
            for constraint in urgency_analysis['key_constraints']:
                print(f"  - {constraint}")

        # Key differentiators
        if alternatives_analysis['key_differentiators']:
            print("\nKey Differentiators:")
            for diff in alternatives_analysis['key_differentiators']:
                print(f"  - {diff}")

        # Top risks
        if risks:
            print("\nTop Risks:")
            sorted_risks = sorted(risks, key=lambda r: {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}.get(r.get('severity', 'MEDIUM'), 2), reverse=True)
            for risk in sorted_risks[:3]:
                print(f"  - [{risk.get('severity')}] {risk.get('risk')}")

    print("\n" + "="*70 + "\n")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Generate executive briefing note for infrastructure acquisition projects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python briefing_note_generator.py samples/sample_1_transit_station_acquisition.json
  python briefing_note_generator.py input.json --output Reports/my_briefing_note.md
  python briefing_note_generator.py input.json --verbose

Output:
  Executive briefing note (1-2 pages) with timestamp prefix in Reports/ directory
        """
    )

    parser.add_argument(
        'input_file',
        help='Path to input JSON file (see briefing_note_input_schema.json)'
    )

    parser.add_argument(
        '--output', '-o',
        help='Output file path (default: auto-generated with timestamp in Reports/)',
        default=None
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Print detailed analysis and validation messages'
    )

    args = parser.parse_args()

    try:
        # Load input data
        print(f"Loading input file: {args.input_file}")
        data = load_input_data(args.input_file)

        if args.verbose:
            print(f"✅ Loaded {len(data.keys())} top-level fields")

        # Validate input
        print("\nValidating input data...")
        if not validate_input(data, verbose=args.verbose):
            print("\n❌ Validation failed. Please fix errors and try again.")
            sys.exit(1)

        # Print analysis summary
        print_summary(data, verbose=args.verbose)

        # Generate briefing note
        print("Generating briefing note...")
        briefing_note = generate_briefing_note(data)

        # Generate output filename
        output_file = generate_output_filename(data, args.output)

        # Write output
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(briefing_note)

        print(f"\n✅ SUCCESS!")
        print(f"Briefing note generated: {output_path}")
        print(f"File size: {output_path.stat().st_size:,} bytes")

        # Print preview if verbose
        if args.verbose:
            print("\n" + "="*70)
            print("BRIEFING NOTE PREVIEW (first 20 lines)")
            print("="*70)
            lines = briefing_note.split('\n')[:20]
            for line in lines:
                print(line)
            if len(briefing_note.split('\n')) > 20:
                print("...")
            print("="*70)

    except FileNotFoundError as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)

    except json.JSONDecodeError as e:
        print(f"\n❌ JSON ERROR: {e}")
        print(f"   Invalid JSON in input file: {args.input_file}")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
