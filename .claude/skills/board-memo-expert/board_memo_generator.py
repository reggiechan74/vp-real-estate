#!/usr/bin/env python3
"""
Board Approval Memo Generator
Generates comprehensive board approval memos with executive summary, financial impact,
risk assessment, and formal resolution language.

Usage:
    python board_memo_generator.py input.json --output Reports/2025-11-16_143022_board_memo.md

Input: JSON file conforming to board_memo_input_schema.json
Output: Markdown formatted board memo with all required sections
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict

# Add Shared_Utils to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / 'Shared_Utils'))

from report_utils import (
    generate_executive_summary,
    format_financial_summary,
    eastern_timestamp,
    generate_document_header,
    format_risk_assessment
)
from financial_utils import npv

# Import local modules
sys.path.insert(0, str(Path(__file__).resolve().parent))
from modules.validators import validate_complete_input, validate_npv_inputs
from modules.governance import (
    generate_resolution_language,
    format_approval_recommendation,
    format_compliance_requirements,
    format_authority_limits,
    format_stakeholder_consultation
)
from modules.output_formatters import (
    format_alternatives_analysis,
    format_timeline_section,
    format_npv_analysis,
    format_payback_analysis,
    format_metadata_header,
    format_urgency_indicator,
    format_funding_source_detail,
    format_background_section
)


def generate_board_memo(input_data: Dict) -> str:
    """
    Generate complete board approval memo from input data.

    Args:
        input_data: Complete input dict with project, financial, risks, governance sections

    Returns:
        Markdown formatted board memo
    """
    # Validate input
    is_valid, errors = validate_complete_input(input_data)
    if not is_valid:
        raise ValueError(f"Input validation failed:\n" + "\n".join(f"  - {e}" for e in errors))

    # Extract sections
    project = input_data['project']
    financial = input_data['financial']
    risks = input_data['risks']
    governance = input_data['governance']
    timeline = input_data.get('timeline')
    metadata = input_data.get('metadata')

    # Build memo
    memo = ""

    # Document header
    memo += generate_document_header(
        title="Board Approval Memorandum",
        subtitle=project['name'],
        metadata={
            'prepared_by': metadata.get('prepared_by', 'Management') if metadata else 'Management',
            'date': metadata.get('date_prepared', eastern_timestamp(include_time=False)) if metadata else eastern_timestamp(include_time=False)
        }
    )

    # Metadata header if present
    if metadata:
        memo += format_metadata_header(metadata)

    # Executive Summary
    memo += generate_executive_summary(
        data={
            'issue': f"Board approval requested for {project['name']}",
            'recommendation': governance['recommendation'],
            'rationale': project['rationale'],
            'urgency': project['urgency'],
            'financial_impact': financial['total_cost']
        },
        template='decision'
    )

    # Urgency indicator
    memo += f"**Timeline:** {format_urgency_indicator(project['urgency'])}\n\n"

    # Background (if present)
    memo += format_background_section(project)

    # Project Overview
    memo += "## Project Overview\n\n"
    memo += f"{project['description']}\n\n"

    # Strategic Rationale
    memo += "### Strategic Rationale\n\n"
    memo += f"{project['rationale']}\n\n"

    # Alternatives Considered (if present)
    if 'alternatives_considered' in project and project['alternatives_considered']:
        memo += format_alternatives_analysis(project['alternatives_considered'])

    # Financial Impact
    memo += format_financial_summary(
        financial_data={
            'total_cost': financial['total_cost'],
            'breakdown': financial['breakdown'],
            'contingency': financial.get('contingency', 0),
            'contingency_pct': financial.get('contingency_pct', 0)
        },
        format_type='detailed'
    )

    # Funding source
    memo += format_funding_source_detail(financial)

    # NPV analysis (if present)
    if 'npv_analysis' in financial and financial['npv_analysis']:
        is_valid, npv_errors = validate_npv_inputs(financial['npv_analysis'])
        if is_valid:
            memo += format_npv_analysis(financial['npv_analysis'])
        else:
            print(f"Warning: NPV analysis validation failed: {npv_errors}", file=sys.stderr)

    # Payback period (if present)
    memo += format_payback_analysis(financial)

    # Risk Assessment
    memo += format_risk_assessment(risks)

    # Timeline (if present)
    if timeline:
        memo += format_timeline_section(timeline)

    # Governance sections
    memo += format_approval_recommendation(governance)

    # Compliance requirements
    memo += format_compliance_requirements(governance)

    # Authority limits
    memo += format_authority_limits(governance)

    # Stakeholder consultation
    memo += format_stakeholder_consultation(governance)

    # Board Resolution
    memo += "## Proposed Board Resolution\n\n"
    memo += generate_resolution_language(governance, project, financial)
    memo += "\n\n"

    # Footer
    memo += "---\n\n"
    memo += f"*Generated on {eastern_timestamp(include_time=False)}*\n"

    return memo


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description='Generate board approval memo from JSON input',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate board memo
  python board_memo_generator.py input.json

  # Specify output file
  python board_memo_generator.py input.json --output Reports/2025-11-16_143022_board_memo.md

  # Validate input only
  python board_memo_generator.py input.json --validate-only
        """
    )

    parser.add_argument(
        'input_file',
        type=str,
        help='Path to JSON input file'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Output file path (default: auto-generated in Reports/)',
        default=None
    )

    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Validate input only without generating memo'
    )

    args = parser.parse_args()

    # Load input
    try:
        with open(args.input_file, 'r') as f:
            input_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate input
    is_valid, errors = validate_complete_input(input_data)

    if not is_valid:
        print("Input validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)

    print("✓ Input validation passed")

    if args.validate_only:
        print("Validation complete (--validate-only flag set)")
        sys.exit(0)

    # Generate memo
    try:
        memo = generate_board_memo(input_data)
    except Exception as e:
        print(f"Error generating board memo: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        # Auto-generate filename
        project_name = input_data['project']['name'].lower().replace(' ', '_')
        filename = f"{eastern_timestamp()}_board_memo_{project_name}.md"
        output_path = Path(__file__).resolve().parent.parent.parent.parent / 'Reports' / filename

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write output
    try:
        with open(output_path, 'w') as f:
            f.write(memo)
        print(f"✓ Board memo generated: {output_path}")
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)

    # Print summary
    print("\nSummary:")
    print(f"  Project: {input_data['project']['name']}")
    print(f"  Total Cost: ${input_data['financial']['total_cost']:,.2f}")
    print(f"  Approval Type: {input_data['governance']['approval_type']}")
    print(f"  Urgency: {input_data['project']['urgency']}")
    print(f"  Risks Identified: {len(input_data['risks'])}")


if __name__ == '__main__':
    main()
