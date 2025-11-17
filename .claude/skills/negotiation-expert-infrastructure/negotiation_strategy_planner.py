#!/usr/bin/env python3
"""
Negotiation Strategy Planner
Develops negotiation approach and settlement strategy based on owner psychology,
property characteristics, and market conditions.

Uses:
- Shared_Utils/negotiation_utils.py (BATNA, ZOPA, concession strategy)
- Shared_Utils/risk_utils.py (holdout risk assessment)
- modules/owner_profiling.py (owner psychology analysis)
- modules/negotiation_tactics.py (opening offers, tactics)

Example usage:
    python negotiation_strategy_planner.py samples/sample_2_urban_station.json --output strategy_report.json --verbose
"""

import sys
import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add parent directories to path for imports
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(current_dir))

from Shared_Utils.negotiation_utils import (
    calculate_batna,
    calculate_zopa,
    optimal_settlement_range,
    calculate_concession_strategy
)
from Shared_Utils.risk_utils import assess_holdout_risk

from modules.owner_profiling import analyze_owner_psychology, recommend_communication_strategy
from modules.negotiation_tactics import (
    recommend_opening_offer,
    generate_concession_plan,
    identify_leverage_points
)


def load_input_data(input_path: str) -> Dict:
    """Load and validate input JSON."""
    try:
        with open(input_path, 'r') as f:
            data = json.load(f)

        # Validate required sections
        required = ['property_info', 'valuation', 'owner_profile', 'hearing_analysis']
        missing = [field for field in required if field not in data]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

        return data

    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")


def analyze_negotiation_context(data: Dict) -> Dict:
    """
    Analyze the overall negotiation context.

    Returns context analysis including:
    - Property type and characteristics
    - Project urgency and timeline
    - Market conditions
    - Stakeholder considerations
    """
    property_info = data.get('property_info', {})
    project_context = data.get('project_context', {})

    # Determine property complexity
    property_type = property_info.get('property_type', 'unknown')
    size_sqft = property_info.get('size_sqft', 0)

    if property_type in ['commercial', 'industrial', 'mixed_use']:
        complexity = 'high'
    elif size_sqft > 50000:
        complexity = 'high'
    elif size_sqft > 10000:
        complexity = 'medium'
    else:
        complexity = 'low'

    # Assess urgency
    timeline = project_context.get('timeline_pressure', 'medium')
    urgency_map = {
        'critical': 'CRITICAL - Immediate action required',
        'high': 'HIGH - Time-sensitive negotiations',
        'medium': 'MODERATE - Standard timeline',
        'low': 'LOW - Flexible timeline'
    }
    urgency = urgency_map.get(timeline, 'MODERATE')

    # Project phase
    phase = project_context.get('project_phase', 'early_stage')

    return {
        'property_complexity': complexity,
        'project_urgency': urgency,
        'project_phase': phase,
        'timeline_pressure': timeline,
        'property_type': property_type,
        'property_size': size_sqft,
        'critical_factors': []
    }


def develop_negotiation_strategy(
    owner_analysis: Dict,
    holdout_risk: Dict,
    batna: Dict,
    zopa: Dict,
    settlement_range: Dict,
    context: Dict
) -> Dict:
    """
    Develop comprehensive negotiation strategy.

    Integrates:
    - Owner psychology
    - Holdout risk
    - BATNA/ZOPA analysis
    - Settlement ranges
    - Context factors
    """
    strategy = {
        'approach': None,
        'primary_tactics': [],
        'communication_style': None,
        'key_messages': [],
        'risk_mitigation': [],
        'timeline_strategy': None
    }

    # Determine overall approach based on holdout risk
    risk_level = holdout_risk.get('risk_level', 'MEDIUM')

    if risk_level in ['CRITICAL', 'HIGH']:
        strategy['approach'] = 'COLLABORATIVE_PROBLEM_SOLVING'
        strategy['primary_tactics'] = [
            'Emphasize value creation over value claiming',
            'Use calibrated questions to uncover constraints',
            'Build rapport through accusation audit and labeling',
            'Focus on long-term relationship'
        ]
    elif risk_level == 'MEDIUM':
        strategy['approach'] = 'BALANCED_COMPETITIVE'
        strategy['primary_tactics'] = [
            'Evidence-based anchoring with market data',
            'Strategic concessions to build momentum',
            'Calibrated questions to test flexibility',
            'Professional but firm stance'
        ]
    else:  # LOW
        strategy['approach'] = 'COMPETITIVE_RATIONAL'
        strategy['primary_tactics'] = [
            'Strong opening with market evidence',
            'Minimal concessions',
            'Focus on BATNA strength',
            'Time pressure if appropriate'
        ]

    # Communication style
    owner_type = owner_analysis.get('owner_type', 'rational_investor')
    comm_strategy = owner_analysis.get('communication_strategy', {})

    strategy['communication_style'] = comm_strategy.get('primary_approach', 'professional')
    strategy['key_messages'] = comm_strategy.get('key_messages', [])

    # Risk mitigation from holdout assessment
    strategy['risk_mitigation'] = holdout_risk.get('mitigation_strategies', [])

    # Timeline strategy
    timeline_pressure = context.get('timeline_pressure', 'medium')
    if timeline_pressure == 'critical':
        strategy['timeline_strategy'] = 'Fast-track negotiations with authority to settle'
    elif timeline_pressure == 'high':
        strategy['timeline_strategy'] = 'Aggressive timeline with defined milestones'
    else:
        strategy['timeline_strategy'] = 'Patient approach allowing time for relationship building'

    return strategy


def generate_negotiation_plan(
    strategy: Dict,
    opening_offer: Dict,
    concession_plan: List[Dict],
    settlement_range: Dict,
    leverage_points: Dict
) -> Dict:
    """
    Generate detailed negotiation plan with tactics and messaging.
    """
    plan = {
        'phase_1_opening': {
            'timing': 'Initial contact',
            'actions': [
                'Present opening offer with supporting evidence',
                'Establish credibility through market data',
                'Use accusation audit if appropriate',
                'Set collaborative tone'
            ],
            'offer_amount': opening_offer.get('recommended_opening', 0),
            'supporting_documents': [
                'Market comparable analysis',
                'Property appraisal',
                'Project overview'
            ],
            'key_messages': opening_offer.get('messaging', [])
        },
        'phase_2_negotiation': {
            'timing': 'Active negotiation rounds',
            'actions': [
                'Use calibrated questions to understand constraints',
                'Label concerns to build rapport',
                'Make strategic concessions per plan',
                'Gather information about alternatives'
            ],
            'concession_strategy': concession_plan,
            'techniques': [
                'Mirroring to encourage elaboration',
                'Evidence-based anchoring to defend position',
                'Labeling to de-escalate tension'
            ]
        },
        'phase_3_closure': {
            'timing': 'Final settlement',
            'actions': [
                'Present final offer at target settlement',
                'Emphasize BATNA if needed',
                'Create value through structure (payment terms, timing)',
                'Document agreement immediately'
            ],
            'target_amount': settlement_range.get('target', 0),
            'walkaway_amount': settlement_range.get('walkaway', 0),
            'authority_required': 'Board approval if exceeding target by >10%'
        },
        'leverage_points': leverage_points,
        'contingency_planning': {
            'if_deadlock': [
                'Propose neutral third-party mediation',
                'Offer structured payment alternatives',
                'Revisit underlying interests vs positions'
            ],
            'if_unreasonable_demands': [
                'Reframe using calibrated questions',
                'Present BATNA analysis clearly',
                'Escalate to decision-makers if needed'
            ],
            'if_multiple_owners': [
                'Identify key decision-maker',
                'Address individual concerns separately',
                'Build coalition of the willing'
            ]
        }
    }

    return plan


def main():
    parser = argparse.ArgumentParser(
        description='Negotiation Strategy Planner - Develop comprehensive negotiation approach',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
    python negotiation_strategy_planner.py samples/sample_2_urban_station.json --output strategy.json --verbose
        """
    )

    parser.add_argument('input', help='Path to input JSON file')
    parser.add_argument('--output', '-o', help='Output JSON file path (optional)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    try:
        # Load input data
        if args.verbose:
            print(f"\n{'='*80}")
            print(f"NEGOTIATION STRATEGY PLANNER")
            print(f"{'='*80}\n")
            print(f"Loading input: {args.input}")

        data = load_input_data(args.input)

        # Extract key sections
        property_info = data.get('property_info', {})
        valuation = data.get('valuation', {})
        owner_profile = data.get('owner_profile', {})
        hearing_analysis = data.get('hearing_analysis', {})
        project_context = data.get('project_context', {})

        # 1. Analyze negotiation context
        if args.verbose:
            print("\n" + "="*80)
            print("STEP 1: ANALYZING NEGOTIATION CONTEXT")
            print("="*80)

        context = analyze_negotiation_context(data)

        if args.verbose:
            print(f"\nProperty: {property_info.get('address', 'N/A')}")
            print(f"Type: {context['property_type']}")
            print(f"Complexity: {context['property_complexity']}")
            print(f"Urgency: {context['project_urgency']}")

        # 2. Owner psychology analysis
        if args.verbose:
            print("\n" + "="*80)
            print("STEP 2: OWNER PSYCHOLOGY ANALYSIS")
            print("="*80)

        owner_analysis = analyze_owner_psychology(owner_profile)
        comm_strategy = recommend_communication_strategy(owner_analysis)
        owner_analysis['communication_strategy'] = comm_strategy

        if args.verbose:
            print(f"\nOwner Type: {owner_analysis.get('owner_type', 'N/A')}")
            print(f"Sophistication: {owner_analysis.get('sophistication_level', 'N/A')}")
            print(f"Primary Motivation: {owner_analysis.get('primary_motivation', 'N/A')}")
            print(f"\nCommunication Approach: {comm_strategy.get('primary_approach', 'N/A')}")

        # 3. Holdout risk assessment
        if args.verbose:
            print("\n" + "="*80)
            print("STEP 3: HOLDOUT RISK ASSESSMENT")
            print("="*80)

        holdout_risk = assess_holdout_risk(owner_profile)

        if args.verbose:
            print(f"\nRisk Score: {holdout_risk.get('total_score', 0)}/30")
            print(f"Risk Level: {holdout_risk.get('risk_level', 'N/A')}")
            print(f"Holdout Probability: {holdout_risk.get('holdout_probability', 0):.1%}")
            if holdout_risk.get('factors'):
                print("\nKey Factors:")
                for factor in holdout_risk['factors']:
                    print(f"  - {factor}")

        # 4. BATNA calculation
        if args.verbose:
            print("\n" + "="*80)
            print("STEP 4: BATNA CALCULATION (Best Alternative)")
            print("="*80)

        hearing_probs = hearing_analysis.get('probabilities', {})
        hearing_costs = hearing_analysis.get('costs', {})

        batna = calculate_batna(hearing_probs, hearing_costs)

        if args.verbose:
            print(f"\nExpected Award: ${batna.get('expected_award', 0):,.2f}")
            print(f"Total Costs: ${batna.get('total_costs', 0):,.2f}")
            print(f"Net BATNA: ${batna.get('net_batna', 0):,.2f}")

        # 5. ZOPA calculation
        if args.verbose:
            print("\n" + "="*80)
            print("STEP 5: ZOPA CALCULATION (Zone of Possible Agreement)")
            print("="*80)

        buyer_max = batna.get('net_batna', 0)
        seller_min = valuation.get('seller_minimum', 0)

        zopa = calculate_zopa(buyer_max, seller_min)

        if args.verbose:
            if zopa.get('exists'):
                print(f"\nZOPA Exists: YES")
                print(f"Range: ${zopa.get('lower_bound', 0):,.2f} - ${zopa.get('upper_bound', 0):,.2f}")
                print(f"Midpoint: ${zopa.get('midpoint', 0):,.2f}")
            else:
                print(f"\nZOPA Exists: NO")
                print(f"Gap: ${zopa.get('gap', 0):,.2f}")

        # 6. Settlement range
        if args.verbose:
            print("\n" + "="*80)
            print("STEP 6: OPTIMAL SETTLEMENT RANGE")
            print("="*80)

        confidence = 0.8  # 80% confidence level
        settlement_range = optimal_settlement_range(buyer_max, zopa, confidence)

        if args.verbose and not settlement_range.get('error'):
            print(f"\nOpening Offer: ${settlement_range.get('opening_offer', 0):,.2f}")
            print(f"Target Settlement: ${settlement_range.get('target', 0):,.2f}")
            print(f"Ceiling (Max): ${settlement_range.get('ceiling', 0):,.2f}")
            print(f"Walkaway: ${settlement_range.get('walkaway', 0):,.2f}")

        # 7. Opening offer recommendation
        if args.verbose:
            print("\n" + "="*80)
            print("STEP 7: OPENING OFFER STRATEGY")
            print("="*80)

        opening_offer = recommend_opening_offer(
            settlement_range,
            owner_analysis,
            holdout_risk,
            context
        )

        if args.verbose:
            print(f"\nRecommended Opening: ${opening_offer.get('recommended_opening', 0):,.2f}")
            print(f"Rationale: {opening_offer.get('rationale', 'N/A')}")

        # 8. Concession plan
        if args.verbose:
            print("\n" + "="*80)
            print("STEP 8: CONCESSION STRATEGY")
            print("="*80)

        concession_plan = generate_concession_plan(
            opening_offer.get('recommended_opening', 0),
            settlement_range.get('target', 0),
            holdout_risk.get('risk_level', 'MEDIUM')
        )

        if args.verbose:
            print("\nConcession Rounds:")
            for round_data in concession_plan:
                print(f"  Round {round_data['round']}: ${round_data['offer']:,.2f} "
                      f"(+${round_data['concession']:,.2f}) - {round_data['message']}")

        # 9. Leverage analysis
        if args.verbose:
            print("\n" + "="*80)
            print("STEP 9: LEVERAGE POINTS")
            print("="*80)

        leverage_points = identify_leverage_points(
            data,
            batna,
            zopa,
            owner_analysis,
            context
        )

        if args.verbose:
            print("\nBuyer Advantages:")
            for adv in leverage_points.get('buyer_advantages', []):
                print(f"  + {adv}")
            print("\nOwner Advantages:")
            for adv in leverage_points.get('owner_advantages', []):
                print(f"  - {adv}")

        # 10. Develop overall strategy
        if args.verbose:
            print("\n" + "="*80)
            print("STEP 10: NEGOTIATION STRATEGY")
            print("="*80)

        strategy = develop_negotiation_strategy(
            owner_analysis,
            holdout_risk,
            batna,
            zopa,
            settlement_range,
            context
        )

        if args.verbose:
            print(f"\nApproach: {strategy.get('approach', 'N/A')}")
            print(f"Communication Style: {strategy.get('communication_style', 'N/A')}")
            print(f"Timeline Strategy: {strategy.get('timeline_strategy', 'N/A')}")

        # 11. Generate negotiation plan
        if args.verbose:
            print("\n" + "="*80)
            print("STEP 11: NEGOTIATION PLAN")
            print("="*80)

        negotiation_plan = generate_negotiation_plan(
            strategy,
            opening_offer,
            concession_plan,
            settlement_range,
            leverage_points
        )

        if args.verbose:
            print("\nPhase 1 - Opening:")
            print(f"  Offer: ${negotiation_plan['phase_1_opening']['offer_amount']:,.2f}")
            print("\nPhase 2 - Negotiation:")
            print(f"  Concession rounds: {len(concession_plan)}")
            print("\nPhase 3 - Closure:")
            print(f"  Target: ${negotiation_plan['phase_3_closure']['target_amount']:,.2f}")
            print(f"  Walkaway: ${negotiation_plan['phase_3_closure']['walkaway_amount']:,.2f}")

        # Compile results
        results = {
            'property_info': property_info,
            'analysis_date': datetime.now().isoformat(),
            'context_analysis': context,
            'owner_analysis': owner_analysis,
            'holdout_risk': holdout_risk,
            'batna': batna,
            'zopa': zopa,
            'settlement_range': settlement_range,
            'opening_offer': opening_offer,
            'concession_plan': concession_plan,
            'leverage_points': leverage_points,
            'negotiation_strategy': strategy,
            'negotiation_plan': negotiation_plan,
            'recommendations': {
                'primary_approach': strategy.get('approach'),
                'opening_offer': opening_offer.get('recommended_opening'),
                'target_settlement': settlement_range.get('target'),
                'walkaway_point': settlement_range.get('walkaway'),
                'key_tactics': strategy.get('primary_tactics'),
                'critical_success_factors': [
                    'Build rapport early through accusation audit',
                    'Use calibrated questions to uncover constraints',
                    'Ground all positions in market evidence',
                    'Make strategic concessions to maintain momentum',
                    'Preserve long-term relationship integrity'
                ]
            }
        }

        # Output results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            if args.verbose:
                print(f"\n{'='*80}")
                print(f"Results saved to: {args.output}")
                print(f"{'='*80}\n")
        else:
            print(json.dumps(results, indent=2))

        return 0

    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
