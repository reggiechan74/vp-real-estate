#!/usr/bin/env python3
"""
Negotiation Settlement Calculator

Calculates BATNA, ZOPA, probability-weighted EV, and optimal settlement range
for property acquisition negotiations.

Uses modular architecture with separate validation, calculation, analysis, and formatting modules.

Supports: negotiation-expert skill (infrastructure acquisitions)
Used by: Acquisition teams, negotiators, project managers

Author: Claude Code
Created: 2025-11-17
Version: 1.0.0
"""

import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules import (
    validate_input_data,
    calculate_batna_analysis,
    calculate_zopa_analysis,
    calculate_probability_weighted_scenarios,
    calculate_optimal_settlement,
    analyze_holdout_risk,
    analyze_settlement_vs_hearing,
    generate_concession_strategy,
    format_settlement_report,
    format_executive_summary
)


class NegotiationSettlementCalculator:
    """
    Main calculator class for negotiation settlement analysis.

    Orchestrates BATNA/ZOPA calculations, risk assessment, and strategy generation.
    """

    def __init__(self, input_data: Dict, verbose: bool = False):
        """
        Initialize calculator with input data.

        Args:
            input_data: Input dictionary with negotiation parameters
            verbose: Enable verbose logging
        """
        self.data = input_data
        self.results = {}

        # Configure logging
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        self.logger.info("Negotiation Settlement Calculator initialized")

    def validate(self) -> bool:
        """
        Validate input data.

        Returns:
            True if valid, False otherwise
        """
        self.logger.info("Validating input data")

        is_valid, errors = validate_input_data(self.data)

        if not is_valid:
            self.logger.error("Input validation failed:")
            for error in errors:
                self.logger.error(f"  - {error}")
            return False

        self.logger.info("Input validation passed")
        return True

    def calculate(self) -> Dict:
        """
        Run complete negotiation settlement analysis.

        Returns:
            Dict with all calculation results
        """
        self.logger.info("Starting negotiation settlement calculations")

        # Extract input parameters
        buyer_max = self.data['buyer_max']
        seller_min = self.data['seller_min']
        hearing_prob = self.data['hearing_probabilities']
        hearing_costs = self.data['hearing_costs']
        owner_profile = self.data.get('owner_profile')
        settlement_offer = self.data.get('settlement_offer')
        confidence = self.data.get('confidence_level', 0.8)

        # 1. Calculate BATNA
        self.logger.info("Step 1: Calculating BATNA")
        batna = calculate_batna_analysis(hearing_prob, hearing_costs)
        self.results['batna'] = batna

        # 2. Calculate ZOPA
        self.logger.info("Step 2: Calculating ZOPA")
        zopa = calculate_zopa_analysis(buyer_max, seller_min)
        self.results['zopa'] = zopa

        # 3. Probability-weighted scenarios
        self.logger.info("Step 3: Analyzing probability-weighted scenarios")
        scenario_analysis = calculate_probability_weighted_scenarios(
            buyer_max,
            seller_min,
            batna['net_batna'],
            settlement_offer
        )
        self.results['scenario_analysis'] = scenario_analysis

        # 4. Optimal settlement range (only if ZOPA exists)
        if zopa['exists']:
            self.logger.info("Step 4: Calculating optimal settlement range")
            optimal = calculate_optimal_settlement(batna['net_batna'], zopa, confidence)
            self.results['optimal_settlement'] = optimal
        else:
            self.logger.warning("No ZOPA - skipping optimal settlement calculation")
            self.results['optimal_settlement'] = {
                'error': 'No ZOPA exists',
                'recommendation': 'Proceed to hearing or walk away'
            }

        # 5. Holdout risk assessment (if owner profile provided)
        if owner_profile:
            self.logger.info("Step 5: Assessing holdout risk")
            holdout_risk = analyze_holdout_risk(owner_profile)
            self.results['holdout_risk'] = holdout_risk

        # 6. Settlement vs. hearing analysis (if settlement offer provided)
        if settlement_offer and zopa['exists']:
            self.logger.info("Step 6: Analyzing settlement vs. hearing")
            legal_costs = self.data.get('legal_costs_to_settle', 5000.0)
            comparison = analyze_settlement_vs_hearing(
                settlement_offer,
                batna['net_batna'],
                legal_costs
            )
            self.results['settlement_vs_hearing'] = comparison

        # 7. Generate concession strategy (if ZOPA exists)
        if zopa['exists'] and 'optimal_settlement' in self.results:
            optimal = self.results['optimal_settlement']
            if 'opening_offer' in optimal and 'target' in optimal:
                self.logger.info("Step 7: Generating concession strategy")
                num_rounds = self.data.get('num_negotiation_rounds', 3)
                concession_strategy = generate_concession_strategy(
                    optimal['opening_offer'],
                    optimal['target'],
                    num_rounds
                )
                self.results['concession_strategy'] = concession_strategy

        # 8. Generate recommendation
        self.logger.info("Step 8: Generating recommendation")
        recommendation = self._generate_recommendation()
        self.results['recommendation'] = recommendation

        # Add metadata
        self.results['metadata'] = {
            'calculation_date': datetime.now().isoformat(),
            'calculator_version': '1.0.0',
            'input_summary': {
                'buyer_max': buyer_max,
                'seller_min': seller_min,
                'batna_net': batna['net_batna']
            }
        }

        self.logger.info("Negotiation settlement calculations complete")

        return self.results

    def _generate_recommendation(self) -> Dict:
        """Generate overall recommendation based on all analyses."""
        batna = self.results.get('batna', {})
        zopa = self.results.get('zopa', {})
        optimal = self.results.get('optimal_settlement', {})
        holdout = self.results.get('holdout_risk', {})

        if not zopa.get('exists'):
            return {
                'recommendation': 'PROCEED TO HEARING',
                'rationale': f"No zone of possible agreement exists. Seller minimum (${zopa['lower_bound']:,.2f}) exceeds buyer maximum (${zopa['upper_bound']:,.2f}) by ${zopa.get('gap', 0):,.2f}.",
                'confidence': 'HIGH',
                'action_items': [
                    {
                        'action': 'Proceed to expropriation hearing',
                        'responsible': 'Legal Team',
                        'deadline': 'As per statutory timeline',
                        'priority': 'HIGH'
                    },
                    {
                        'action': 'Prepare expert valuation reports',
                        'responsible': 'Appraisal Team',
                        'deadline': 'Before hearing',
                        'priority': 'HIGH'
                    }
                ]
            }

        # ZOPA exists - recommend settlement
        target = optimal.get('target', zopa.get('midpoint', 0))
        savings = batna.get('net_batna', 0) - target

        # Assess confidence based on holdout risk
        if holdout and holdout.get('risk_level') in ['HIGH', 'CRITICAL']:
            confidence = 'MEDIUM'
            rationale_suffix = f" However, holdout risk is {holdout['risk_level']} ({holdout.get('holdout_probability', 0):.0%} probability), which may complicate negotiations."
        else:
            confidence = 'HIGH'
            rationale_suffix = ""

        return {
            'recommendation': 'SETTLE',
            'rationale': f"Settlement at ${target:,.2f} saves ${savings:,.2f} compared to hearing (${batna['net_batna']:,.2f}). ZOPA exists with range of ${zopa['range']:,.2f}.{rationale_suffix}",
            'confidence': confidence,
            'target_amount': target,
            'savings_vs_hearing': savings,
            'action_items': [
                {
                    'action': f"Make opening offer of ${optimal.get('opening_offer', target):,.2f}",
                    'responsible': 'Negotiation Team',
                    'deadline': 'Immediately',
                    'priority': 'HIGH'
                },
                {
                    'action': f"Target settlement at ${target:,.2f}",
                    'responsible': 'Negotiation Team',
                    'deadline': 'Within 30 days',
                    'priority': 'HIGH'
                },
                {
                    'action': f"Walk away if settlement exceeds ${optimal.get('walkaway', batna['net_batna']):,.2f}",
                    'responsible': 'Project Manager',
                    'deadline': 'N/A',
                    'priority': 'MEDIUM'
                }
            ]
        }

    def generate_report(self, property_description: str = "Property Acquisition") -> str:
        """
        Generate markdown report.

        Args:
            property_description: Description of property/acquisition

        Returns:
            Markdown formatted report
        """
        self.logger.info("Generating settlement analysis report")

        # Add action items to results
        if 'recommendation' in self.results and 'action_items' in self.results['recommendation']:
            self.results['action_items'] = self.results['recommendation']['action_items']

        report = format_settlement_report(self.results, property_description)

        self.logger.info("Report generation complete")

        return report


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Calculate negotiation settlement strategy using BATNA/ZOPA analysis'
    )
    parser.add_argument('input_file', help='Path to input JSON file')
    parser.add_argument('--output', '-o', help='Path to output JSON file (optional)')
    parser.add_argument('--report', '-r', help='Path to output markdown report (optional)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Print detailed output')
    parser.add_argument('--property', '-p', default='Property Acquisition',
                       help='Property description for report')

    args = parser.parse_args()

    # Load input
    try:
        with open(args.input_file, 'r') as f:
            input_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file not found: {args.input_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}")
        sys.exit(1)

    # Create calculator
    calculator = NegotiationSettlementCalculator(input_data, verbose=args.verbose)

    # Validate input
    if not calculator.validate():
        print("ERROR: Input validation failed. See log for details.")
        sys.exit(1)

    # Calculate
    try:
        results = calculator.calculate()
    except Exception as e:
        print(f"ERROR: Calculation failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

    # Output JSON results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results written to {args.output}")

    # Output markdown report
    if args.report:
        report = calculator.generate_report(args.property)
        with open(args.report, 'w') as f:
            f.write(report)
        print(f"Report written to {args.report}")

    # Print summary to console
    print(f"\n{'='*80}")
    print(f"NEGOTIATION SETTLEMENT ANALYSIS")
    print(f"{'='*80}")
    print(f"Property: {args.property}")
    print(f"\nKey Metrics:")
    print(f"  Buyer Maximum:       ${input_data['buyer_max']:>12,.0f}")
    print(f"  Seller Minimum:      ${input_data['seller_min']:>12,.0f}")
    print(f"  Net BATNA (Hearing): ${results['batna']['net_batna']:>12,.0f}")

    if results['zopa']['exists']:
        print(f"\nZOPA:")
        print(f"  Range:               ${results['zopa']['lower_bound']:>12,.0f} - ${results['zopa']['upper_bound']:>12,.0f}")
        print(f"  Midpoint:            ${results['zopa']['midpoint']:>12,.0f}")

        if 'optimal_settlement' in results and 'target' in results['optimal_settlement']:
            print(f"\nOptimal Settlement:")
            print(f"  Opening Offer:       ${results['optimal_settlement']['opening_offer']:>12,.0f}")
            print(f"  Target:              ${results['optimal_settlement']['target']:>12,.0f}")
            print(f"  Walkaway:            ${results['optimal_settlement']['walkaway']:>12,.0f}")
    else:
        print(f"\nNo ZOPA - Gap:       ${results['zopa'].get('gap', 0):>12,.0f}")

    print(f"\nRecommendation:      {results['recommendation']['recommendation']}")
    print(f"Confidence:          {results['recommendation']['confidence']}")
    print(f"\n{results['recommendation']['rationale']}")
    print(f"{'='*80}\n")

    if args.verbose:
        print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
