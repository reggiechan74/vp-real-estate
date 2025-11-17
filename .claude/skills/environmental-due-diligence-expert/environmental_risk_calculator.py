#!/usr/bin/env python3
"""
Environmental Risk Assessment Calculator
Analyzes environmental contamination risk from Phase I/II ESA findings.

Usage:
    python environmental_risk_calculator.py <input_json_path> [--output <report_path>] [--discount-rate 0.055]

Args:
    input_json_path: Path to input JSON file with ESA data
    --output: Optional output path for markdown report
    --discount-rate: Discount rate for NPV calculation (default 5.5%)
    --verbose: Enable verbose logging

Input JSON Structure:
    {
        "site_address": "123 Industrial Ave",
        "phase_1_esa": {
            "findings": ["AST present", "Historical dry cleaner"],
            "recs": [...],
            "data_gaps": [...]
        },
        "phase_2_esa": {
            "soil_samples": [{...}],
            "groundwater_samples": [{...}],
            "exceedances": [...],
            "contaminants": ["Petroleum hydrocarbons", "VOCs"]
        },
        "cleanup_scenarios": {
            "risk_assessment": {"cost_low": 50000, "cost_high": 150000},
            "remediation": {"cost_low": 200000, "cost_high": 500000},
            "brownfield": {"cost_low": 500000, "cost_high": 1000000}
        }
    }

Output:
    - Contamination risk score (HIGH/MEDIUM/LOW)
    - Cleanup cost estimates with NPV
    - Regulatory pathway and timeline
    - Liability allocation recommendations
    - Markdown report in Reports/ directory

Author: Claude Code
Created: 2025-11-17
"""

import json
import sys
import os
import argparse
import logging
from typing import Dict, Optional

# Add parent directories to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Import from modules
from modules.validators import (
    validate_input_data,
    validate_discount_rate
)
from modules.environmental_assessment import (
    parse_phase_i_findings,
    parse_phase_ii_results,
    identify_recognized_environmental_conditions,
    score_contamination_risk
)
from modules.cleanup_cost_estimation import (
    estimate_cleanup_costs,
    calculate_npv_cleanup_costs
)
from modules.regulatory_pathway import (
    determine_regulatory_pathway,
    estimate_regulatory_timeline,
    generate_approval_requirements,
    calculate_total_regulatory_costs
)
from modules.output_formatters import (
    format_risk_summary,
    format_cleanup_cost_report,
    format_regulatory_timeline,
    format_liability_recommendations,
    generate_markdown_report
)

# Import from Shared_Utils
from Shared_Utils.report_utils import eastern_timestamp


def setup_logging(verbose: bool = False) -> None:
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def load_input_data(input_path: str) -> Dict:
    """
    Load and validate input JSON data.

    Args:
        input_path: Path to input JSON file

    Returns:
        Validated input data dictionary

    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If JSON is invalid or validation fails
    """
    logger = logging.getLogger(__name__)

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    logger.info(f"Loading input data from: {input_path}")

    with open(input_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in input file: {e}")

    # Validate input data
    is_valid, error_msg = validate_input_data(data)
    if not is_valid:
        raise ValueError(f"Input validation failed: {error_msg}")

    logger.info("Input data validated successfully")
    return data


def run_environmental_risk_assessment(
    input_data: Dict,
    discount_rate: float = 0.055
) -> Dict:
    """
    Run complete environmental risk assessment.

    Args:
        input_data: Validated input data
        discount_rate: Discount rate for NPV (default 5.5%)

    Returns:
        Dict containing all analysis results
    """
    logger = logging.getLogger(__name__)

    # Extract input sections
    site_address = input_data.get('site_address', 'Unknown Site')
    phase_1_data = input_data.get('phase_1_esa')
    phase_2_data = input_data.get('phase_2_esa')
    cleanup_scenarios = input_data.get('cleanup_scenarios')

    results = {
        'site_address': site_address,
        'analysis_timestamp': eastern_timestamp(include_time=True)
    }

    # Step 1: Parse Phase I findings (if present)
    if phase_1_data:
        logger.info("Parsing Phase I ESA findings...")
        phase_1_parsed = parse_phase_i_findings(phase_1_data)
        results['phase_1_summary'] = phase_1_parsed
        logger.info(f"Phase I: {phase_1_parsed['findings_count']} findings, "
                   f"{phase_1_parsed['recs_count']} RECs identified")

    # Step 2: Parse Phase II results (if present)
    if phase_2_data:
        logger.info("Parsing Phase II ESA results...")
        phase_2_parsed = parse_phase_ii_results(phase_2_data)
        results['phase_2_summary'] = phase_2_parsed
        logger.info(f"Phase II: {phase_2_parsed['exceedances_count']} exceedances, "
                   f"{phase_2_parsed['contaminants_count']} contaminants detected")

    # Step 3: Identify all RECs
    logger.info("Identifying Recognized Environmental Conditions...")
    recs = identify_recognized_environmental_conditions(phase_1_data, phase_2_data)
    results['recs'] = recs
    logger.info(f"Total RECs identified: {len(recs)}")

    # Step 4: Score contamination risk
    logger.info("Scoring contamination risk...")
    risk_score = score_contamination_risk(phase_1_data, phase_2_data, cleanup_scenarios)
    results['risk_score'] = risk_score
    logger.info(f"Risk Assessment: {risk_score['risk_level']} "
               f"(Score: {risk_score['total_score']}/100)")

    # Step 5: Estimate cleanup costs
    logger.info("Estimating cleanup costs...")
    cleanup_costs = estimate_cleanup_costs(phase_2_data, cleanup_scenarios)
    results['cleanup_costs'] = cleanup_costs
    logger.info(f"Recommended scenario: {cleanup_costs['recommended_scenario']}")
    logger.info(f"Cost range: ${cleanup_costs['total_range']['low']:,.0f} - "
               f"${cleanup_costs['total_range']['high']:,.0f}")

    # Step 6: Calculate NPV of cleanup costs
    logger.info(f"Calculating NPV (discount rate: {discount_rate*100:.1f}%)...")
    npv_costs = calculate_npv_cleanup_costs(cleanup_costs, discount_rate)
    results['npv_costs'] = npv_costs
    logger.info(f"NPV of cleanup: ${npv_costs['npv_most_likely']:,.0f}")

    # Step 7: Determine regulatory pathway
    logger.info("Determining regulatory pathway...")
    pathway_data = determine_regulatory_pathway(phase_2_data, risk_score['risk_level'])
    results['regulatory_pathway'] = pathway_data
    logger.info(f"Regulatory pathway: {pathway_data['pathway']}")

    # Step 8: Estimate regulatory timeline
    logger.info("Estimating regulatory timeline...")
    timeline_data = estimate_regulatory_timeline(pathway_data)
    results['regulatory_timeline'] = timeline_data
    logger.info(f"Timeline: {timeline_data.get('total_with_contingency', 0)} months "
               f"(with contingency)")

    # Step 9: Generate approval requirements
    logger.info("Generating approval requirements...")
    approval_requirements = generate_approval_requirements(pathway_data, timeline_data)
    results['approval_requirements'] = approval_requirements
    logger.info(f"Approval requirements: {len(approval_requirements)} items")

    # Step 10: Calculate total regulatory costs
    regulatory_costs = calculate_total_regulatory_costs(approval_requirements)
    results['regulatory_costs'] = regulatory_costs
    logger.info(f"Total regulatory costs: ${regulatory_costs['total_estimated']:,.0f}")

    # Step 11: Calculate total environmental costs (cleanup + regulatory)
    results['total_environmental_costs'] = {
        'cleanup_low': cleanup_costs['total_range']['low'],
        'cleanup_high': cleanup_costs['total_range']['high'],
        'cleanup_most_likely': cleanup_costs['most_likely'],
        'regulatory_low': regulatory_costs['total_low'],
        'regulatory_high': regulatory_costs['total_high'],
        'regulatory_estimated': regulatory_costs['total_estimated'],
        'total_low': cleanup_costs['total_range']['low'] + regulatory_costs['total_low'],
        'total_high': cleanup_costs['total_range']['high'] + regulatory_costs['total_high'],
        'total_most_likely': cleanup_costs['most_likely'] + regulatory_costs['total_estimated']
    }

    logger.info(f"Total environmental costs (cleanup + regulatory): "
               f"${results['total_environmental_costs']['total_most_likely']:,.0f}")

    return results


def save_markdown_report(
    results: Dict,
    output_path: Optional[str] = None
) -> str:
    """
    Generate and save markdown report.

    Args:
        results: Analysis results from run_environmental_risk_assessment()
        output_path: Optional custom output path

    Returns:
        Path to saved report
    """
    logger = logging.getLogger(__name__)

    # Generate report
    report = generate_markdown_report(
        site_address=results['site_address'],
        risk_score=results['risk_score'],
        cleanup_costs=results['cleanup_costs'],
        npv_costs=results['npv_costs'],
        pathway_data=results['regulatory_pathway'],
        timeline_data=results['regulatory_timeline'],
        approval_requirements=results['approval_requirements'],
        phase_1_data=results.get('phase_1_summary'),
        phase_2_data=results.get('phase_2_summary')
    )

    # Determine output path
    if output_path is None:
        # Default: Reports/ directory with timestamp
        reports_dir = os.path.join(os.path.dirname(__file__), '../../../Reports')
        os.makedirs(reports_dir, exist_ok=True)

        # Sanitize site address for filename
        site_safe = results['site_address'].replace(' ', '_').replace('/', '_')[:50]
        timestamp = eastern_timestamp(include_time=True)
        filename = f"{timestamp}_environmental_risk_{site_safe}.md"
        output_path = os.path.join(reports_dir, filename)

    # Save report
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    logger.info(f"Markdown report saved: {output_path}")
    return output_path


def save_json_results(
    results: Dict,
    output_path: str
) -> None:
    """
    Save results as JSON.

    Args:
        results: Analysis results
        output_path: Output JSON path
    """
    logger = logging.getLogger(__name__)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    logger.info(f"JSON results saved: {output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Environmental Risk Assessment Calculator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        'input_json',
        help='Path to input JSON file with ESA data'
    )
    parser.add_argument(
        '--output',
        help='Optional output path for markdown report (default: Reports/TIMESTAMP_environmental_risk_*.md)'
    )
    parser.add_argument(
        '--json-output',
        help='Optional output path for JSON results'
    )
    parser.add_argument(
        '--discount-rate',
        type=float,
        default=0.055,
        help='Discount rate for NPV calculation (default: 0.055 = 5.5%%)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    try:
        # Validate discount rate
        is_valid, error_msg = validate_discount_rate(args.discount_rate)
        if not is_valid:
            logger.error(f"Invalid discount rate: {error_msg}")
            sys.exit(1)

        # Load input data
        input_data = load_input_data(args.input_json)

        # Run analysis
        logger.info("Starting environmental risk assessment...")
        results = run_environmental_risk_assessment(input_data, args.discount_rate)

        # Save markdown report
        report_path = save_markdown_report(results, args.output)
        print(f"\nMarkdown report saved: {report_path}")

        # Save JSON results if requested
        if args.json_output:
            save_json_results(results, args.json_output)
            print(f"JSON results saved: {args.json_output}")

        # Print summary
        print("\n" + "="*70)
        print("ENVIRONMENTAL RISK ASSESSMENT SUMMARY")
        print("="*70)
        print(f"Site Address: {results['site_address']}")
        print(f"Risk Level: {results['risk_score']['risk_level']}")
        print(f"Risk Score: {results['risk_score']['total_score']}/100")
        print(f"\nCleanup Costs:")
        print(f"  Low:         ${results['cleanup_costs']['total_range']['low']:>12,.0f}")
        print(f"  Most Likely: ${results['cleanup_costs']['most_likely']:>12,.0f}")
        print(f"  High:        ${results['cleanup_costs']['total_range']['high']:>12,.0f}")
        print(f"\nRegulatory Pathway: {results['regulatory_pathway']['pathway']}")
        print(f"Timeline: {results['regulatory_timeline'].get('total_with_contingency', 0)} months")
        print(f"\nTotal Environmental Costs (Cleanup + Regulatory):")
        print(f"  Low:         ${results['total_environmental_costs']['total_low']:>12,.0f}")
        print(f"  Most Likely: ${results['total_environmental_costs']['total_most_likely']:>12,.0f}")
        print(f"  High:        ${results['total_environmental_costs']['total_high']:>12,.0f}")
        print("="*70 + "\n")

        logger.info("Environmental risk assessment completed successfully")
        sys.exit(0)

    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)
    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
