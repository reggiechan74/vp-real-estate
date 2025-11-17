#!/usr/bin/env python3
"""
Settlement Analysis Calculator
Analyze settlement scenarios vs. hearing risk with probability-weighted outcomes.

This is a thin orchestration layer that coordinates the modular components.

Usage:
    python settlement_analyzer.py <input_json_path> [--output <report_path>] [--json]

Example:
    python settlement_analyzer.py samples/sample_1_transmission_easement.json --output report.md
    python settlement_analyzer.py samples/sample_1_transmission_easement.json --json > results.json
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'Shared_Utils'))

from modules import (
    validate_input,
    calculate_settlement_scenarios,
    calculate_hearing_expected_value,
    calculate_net_benefit,
    analyze_settlement_vs_hearing,
    calculate_zopa_analysis,
    generate_concession_strategy,
    format_analysis_report,
    format_executive_summary
)
from modules.analysis import assess_owner_holdout_risk, assess_litigation_risk
from report_utils import eastern_timestamp


def load_input(input_path: str) -> Dict:
    """Load and validate input JSON."""
    with open(input_path, 'r') as f:
        data = json.load(f)

    # Validate input
    is_valid, errors = validate_input(data)
    if not is_valid:
        raise ValueError(f"Input validation failed:\n" + "\n".join(f"  - {e}" for e in errors))

    return data


def run_settlement_analysis(data: Dict) -> Dict:
    """
    Run complete settlement analysis.

    Args:
        data: Validated input data

    Returns:
        Dict containing all analysis results
    """
    # Extract inputs
    case_id = data['case_id']
    settlement_offer = data['settlement_offer']
    counteroffer = data.get('counteroffer')
    hearing_probabilities = data['hearing_probabilities']
    hearing_costs = data['hearing_costs']
    settlement_costs = data.get('settlement_costs', {})
    owner_profile = data.get('owner_profile')
    case_factors = data.get('case_factors')

    # 1. Calculate hearing expected value (BATNA)
    hearing_batna = calculate_hearing_expected_value(
        hearing_probabilities,
        hearing_costs
    )

    # 2. Calculate settlement scenarios
    settlement_scenarios = calculate_settlement_scenarios(
        settlement_offer,
        counteroffer,
        settlement_costs
    )

    # 3. Analyze settlement vs. hearing
    analysis = analyze_settlement_vs_hearing(
        settlement_offer,
        hearing_batna,
        settlement_costs
    )

    # 4. Calculate ZOPA if counteroffer provided
    zopa_analysis = None
    if counteroffer:
        zopa_analysis = calculate_zopa_analysis(
            settlement_offer,
            counteroffer,
            hearing_batna,
            settlement_costs
        )

    # 5. Assess owner holdout risk if profile provided
    owner_risk = None
    if owner_profile:
        owner_risk = assess_owner_holdout_risk(owner_profile)

    # 6. Assess litigation risk if case factors provided
    litigation_risk = None
    if case_factors:
        # Add owner risk profile to case factors if available
        if owner_risk:
            case_factors['owner_risk_profile'] = owner_risk['risk_level']
        litigation_risk = assess_litigation_risk(case_factors)

    # 7. Generate concession strategy if ZOPA exists
    concession_strategy = None
    if zopa_analysis and zopa_analysis['zopa'].get('exists'):
        optimal = zopa_analysis['optimal_range']
        if 'opening_offer' in optimal:
            concession_strategy = generate_concession_strategy(
                optimal['opening_offer'],
                optimal['target'],
                num_rounds=3
            )

    # Compile results
    results = {
        'case_id': case_id,
        'timestamp': eastern_timestamp(),
        'analysis': analysis,
        'hearing_batna': hearing_batna,
        'settlement_scenarios': settlement_scenarios,
        'zopa_analysis': zopa_analysis,
        'owner_risk': owner_risk,
        'litigation_risk': litigation_risk,
        'concession_strategy': concession_strategy
    }

    return results


def generate_report(results: Dict) -> str:
    """Generate markdown report from results."""
    return format_analysis_report(
        case_id=results['case_id'],
        analysis=results['analysis'],
        hearing_batna=results['hearing_batna'],
        settlement_scenarios=results['settlement_scenarios'],
        zopa_analysis=results['zopa_analysis'],
        owner_risk=results['owner_risk'],
        litigation_risk=results['litigation_risk']
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Settlement Analysis Calculator - Analyze settlement vs. hearing scenarios'
    )
    parser.add_argument(
        'input',
        help='Path to input JSON file'
    )
    parser.add_argument(
        '--output',
        help='Path to output markdown report (optional)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON instead of markdown report'
    )

    args = parser.parse_args()

    try:
        # Load and validate input
        data = load_input(args.input)

        # Run analysis
        results = run_settlement_analysis(data)

        # Generate output
        if args.json:
            # JSON output
            output = json.dumps(results, indent=2)
            print(output)
        else:
            # Markdown report
            report = generate_report(results)

            if args.output:
                # Write to file
                with open(args.output, 'w') as f:
                    f.write(report)
                print(f"Report written to {args.output}")
            else:
                # Print to stdout
                print(report)

    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
