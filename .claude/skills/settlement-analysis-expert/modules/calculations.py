#!/usr/bin/env python3
"""
Settlement scenario calculations.
Calculate expected values, scenarios, and cost-benefit analysis.
"""

import sys
from pathlib import Path
from typing import Dict, List

# Add Shared_Utils to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'Shared_Utils'))

from negotiation_utils import calculate_batna, probability_weighted_ev, hearing_cost_benefit
from financial_utils import npv


def calculate_settlement_scenarios(
    settlement_offer: float,
    counteroffer: float = None,
    settlement_costs: Dict = None
) -> List[Dict]:
    """
    Calculate settlement scenarios with probabilities.

    Args:
        settlement_offer: Current settlement offer
        counteroffer: Owner's counteroffer (optional)
        settlement_costs: Dict with settlement costs

    Returns:
        List of settlement scenarios with costs and probabilities
    """
    legal_fees = 0
    if settlement_costs:
        legal_fees = settlement_costs.get('legal_fees_to_settle', 5000)

    scenarios = []

    # Scenario 1: Settle at current offer
    scenarios.append({
        'name': 'Settle at offer',
        'cost': settlement_offer + legal_fees,
        'probability': 0.4 if counteroffer else 0.6,
        'description': f'Settle at ${settlement_offer:,.0f} plus ${legal_fees:,.0f} legal fees'
    })

    # Scenario 2: Settle at counteroffer (if provided)
    if counteroffer:
        scenarios.append({
            'name': 'Settle at counteroffer',
            'cost': counteroffer + legal_fees,
            'probability': 0.3,
            'description': f'Settle at ${counteroffer:,.0f} plus ${legal_fees:,.0f} legal fees'
        })

        # Scenario 3: Settle at midpoint
        midpoint = (settlement_offer + counteroffer) / 2
        scenarios.append({
            'name': 'Settle at midpoint',
            'cost': midpoint + legal_fees,
            'probability': 0.3,
            'description': f'Settle at midpoint ${midpoint:,.0f} plus ${legal_fees:,.0f} legal fees'
        })

    return scenarios


def calculate_hearing_expected_value(
    hearing_probabilities: Dict,
    hearing_costs: Dict
) -> Dict:
    """
    Calculate expected value of proceeding to hearing.

    Args:
        hearing_probabilities: Dict with outcome probabilities
        hearing_costs: Dict with cost estimates

    Returns:
        Dict containing BATNA analysis from negotiation_utils
    """
    return calculate_batna(hearing_probabilities, hearing_costs)


def calculate_net_benefit(
    settlement_total: float,
    hearing_batna: Dict,
    settlement_costs: Dict = None
) -> Dict:
    """
    Calculate net benefit of settlement vs. hearing.

    Args:
        settlement_total: Total cost of settlement
        hearing_batna: BATNA dict from calculate_hearing_expected_value
        settlement_costs: Optional settlement costs dict

    Returns:
        Dict containing cost-benefit analysis
    """
    hearing_total = hearing_batna['net_batna']

    costs = {
        'legal_fees_to_hearing': hearing_batna['breakdown']['legal_fees'],
        'expert_fees_to_hearing': hearing_batna['breakdown']['expert_fees'],
        'time_cost_to_hearing': hearing_batna['breakdown']['time_cost'],
        'legal_fees_to_settle': 0,
        'settlement_risk': 0.1
    }

    if settlement_costs:
        costs['legal_fees_to_settle'] = settlement_costs.get('legal_fees_to_settle', 5000)
        costs['settlement_risk'] = settlement_costs.get('settlement_risk', 0.1)

    # Calculate using hearing_cost_benefit from negotiation_utils
    # But we need to back out the settlement amount from settlement_total
    settlement_amount = settlement_total - costs['legal_fees_to_settle']

    return hearing_cost_benefit(
        settlement_offer=settlement_amount,
        hearing_ev=hearing_total,
        costs=costs
    )


def calculate_scenario_comparison(
    settlement_scenarios: List[Dict],
    hearing_batna: Dict
) -> Dict:
    """
    Compare all scenarios (settlement + hearing) with probability weighting.

    Args:
        settlement_scenarios: List of settlement scenarios
        hearing_batna: BATNA analysis for hearing

    Returns:
        Dict containing probability-weighted expected value analysis
    """
    # Combine settlement scenarios with hearing scenario
    all_scenarios = settlement_scenarios.copy()

    # Add hearing scenario
    all_scenarios.append({
        'name': 'Proceed to hearing',
        'cost': hearing_batna['net_batna'],
        'probability': 0.0,  # Will be normalized
        'description': f"Expected hearing cost ${hearing_batna['net_batna']:,.0f}"
    })

    # Normalize probabilities to sum to 1.0
    total_prob = sum(s['probability'] for s in all_scenarios)
    if total_prob > 0:
        for scenario in all_scenarios:
            scenario['probability'] = scenario['probability'] / total_prob

    # Calculate probability-weighted expected value
    return probability_weighted_ev(all_scenarios)


def calculate_savings_analysis(
    settlement_amount: float,
    hearing_batna: Dict,
    settlement_costs: Dict = None
) -> Dict:
    """
    Calculate savings from settlement vs. hearing.

    Args:
        settlement_amount: Proposed settlement amount
        hearing_batna: BATNA analysis
        settlement_costs: Optional settlement costs

    Returns:
        Dict with savings analysis
    """
    legal_fees = 5000
    if settlement_costs:
        legal_fees = settlement_costs.get('legal_fees_to_settle', 5000)

    settlement_total = settlement_amount + legal_fees
    hearing_total = hearing_batna['net_batna']

    savings = hearing_total - settlement_total
    savings_pct = (savings / hearing_total * 100) if hearing_total > 0 else 0

    return {
        'settlement_total': round(settlement_total, 2),
        'hearing_total': round(hearing_total, 2),
        'absolute_savings': round(savings, 2),
        'savings_percentage': round(savings_pct, 2),
        'recommendation': 'SETTLE' if savings > 0 else 'PROCEED TO HEARING',
        'breakeven_settlement': round(hearing_total - legal_fees, 2)
    }
