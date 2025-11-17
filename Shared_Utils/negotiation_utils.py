#!/usr/bin/env python3
"""
Negotiation Utilities Module
Provides shared functions for negotiation analysis, BATNA/ZOPA calculations,
and settlement strategy optimization.

Used by:
- negotiation_settlement_calculator.py
- settlement_analyzer.py
- negotiation_strategy_planner.py
"""

from typing import Dict, List, Optional, Tuple
import statistics


def calculate_batna(
    hearing_probabilities: Dict[str, float],
    hearing_costs: Dict[str, float]
) -> Dict:
    """
    Calculate Best Alternative to Negotiated Agreement (expropriation hearing).

    BATNA represents the expected value of proceeding to hearing rather than
    settling through negotiation.

    Args:
        hearing_probabilities: Dict with outcome probabilities
            {
                'low_award': 0.2,    # Probability of low valuation
                'mid_award': 0.5,    # Probability of mid valuation
                'high_award': 0.3    # Probability of high valuation
            }
        hearing_costs: Dict with cost estimates
            {
                'low_award_amount': 100000,
                'mid_award_amount': 150000,
                'high_award_amount': 200000,
                'legal_fees': 50000,
                'expert_fees': 30000,
                'time_cost': 10000  # Staff time, delays
            }

    Returns:
        Dict containing BATNA analysis
            {
                'expected_award': 155000,
                'total_costs': 90000,
                'net_batna': 245000,  # Total expected cost to buyer
                'breakdown': {...},
                'probabilities': {...}
            }
    """
    # Calculate expected award
    expected_award = sum(
        hearing_probabilities.get(outcome, 0) * hearing_costs.get(f"{outcome}_amount", 0)
        for outcome in ['low_award', 'mid_award', 'high_award']
    )

    # Calculate total costs
    total_costs = sum(
        hearing_costs.get(cost, 0)
        for cost in ['legal_fees', 'expert_fees', 'time_cost']
    )

    # Net BATNA is total expected cost to buyer (award + costs)
    net_batna = expected_award + total_costs

    # Calculate variance (risk measure)
    award_amounts = [
        hearing_costs.get(f"{outcome}_amount", 0)
        for outcome in ['low_award', 'mid_award', 'high_award']
    ]
    probabilities = [
        hearing_probabilities.get(outcome, 0)
        for outcome in ['low_award', 'mid_award', 'high_award']
    ]

    # Weighted variance
    variance = sum(
        p * (amount - expected_award) ** 2
        for p, amount in zip(probabilities, award_amounts)
    )
    std_dev = variance ** 0.5

    return {
        'expected_award': round(expected_award, 2),
        'total_costs': round(total_costs, 2),
        'net_batna': round(net_batna, 2),
        'standard_deviation': round(std_dev, 2),
        'coefficient_of_variation': round(std_dev / expected_award, 4) if expected_award > 0 else 0,
        'breakdown': {
            'legal_fees': hearing_costs.get('legal_fees', 0),
            'expert_fees': hearing_costs.get('expert_fees', 0),
            'time_cost': hearing_costs.get('time_cost', 0)
        },
        'probabilities': hearing_probabilities,
        'award_range': {
            'low': hearing_costs.get('low_award_amount', 0),
            'mid': hearing_costs.get('mid_award_amount', 0),
            'high': hearing_costs.get('high_award_amount', 0)
        }
    }


def calculate_zopa(buyer_max: float, seller_min: float) -> Dict:
    """
    Calculate Zone of Possible Agreement.

    ZOPA is the range where both parties' interests overlap. A deal is only
    possible when buyer_max >= seller_min.

    Args:
        buyer_max: Maximum buyer is willing to pay
        seller_min: Minimum seller is willing to accept

    Returns:
        Dict containing ZOPA analysis
            {
                'exists': True,
                'lower_bound': 150000,  # Seller's minimum
                'upper_bound': 200000,  # Buyer's maximum
                'midpoint': 175000,
                'range': 50000,
                'buyer_surplus_at_midpoint': 25000,
                'seller_surplus_at_midpoint': 25000
            }
    """
    exists = buyer_max >= seller_min

    if not exists:
        return {
            'exists': False,
            'lower_bound': seller_min,
            'upper_bound': buyer_max,
            'gap': round(seller_min - buyer_max, 2),
            'message': 'No ZOPA - seller minimum exceeds buyer maximum'
        }

    midpoint = (buyer_max + seller_min) / 2
    zopa_range = buyer_max - seller_min

    return {
        'exists': True,
        'lower_bound': round(seller_min, 2),
        'upper_bound': round(buyer_max, 2),
        'midpoint': round(midpoint, 2),
        'range': round(zopa_range, 2),
        'buyer_surplus_at_midpoint': round(buyer_max - midpoint, 2),
        'seller_surplus_at_midpoint': round(midpoint - seller_min, 2),
        'negotiation_leverage': {
            'buyer': round((buyer_max - midpoint) / zopa_range, 4) if zopa_range > 0 else 0.5,
            'seller': round((midpoint - seller_min) / zopa_range, 4) if zopa_range > 0 else 0.5
        }
    }


def probability_weighted_ev(scenarios: List[Dict]) -> Dict:
    """
    Calculate probability-weighted expected value across scenarios.

    Args:
        scenarios: List of scenario dicts
            [
                {'name': 'Settle at offer', 'cost': 180000, 'probability': 0.4},
                {'name': 'Settle at counteroffer', 'cost': 200000, 'probability': 0.3},
                {'name': 'Proceed to hearing', 'cost': 250000, 'probability': 0.3}
            ]

    Returns:
        Dict containing expected value analysis
            {
                'expected_value': 205000,
                'scenarios': [...],
                'best_case': {...},
                'worst_case': {...},
                'variance': 625000000,
                'std_dev': 25000
            }
    """
    if not scenarios:
        return {'error': 'No scenarios provided'}

    # Validate probabilities sum to 1.0
    total_prob = sum(s.get('probability', 0) for s in scenarios)
    if abs(total_prob - 1.0) > 0.01:
        return {
            'error': f'Probabilities must sum to 1.0, got {total_prob}',
            'scenarios': scenarios
        }

    # Calculate expected value
    expected_value = sum(
        s.get('cost', 0) * s.get('probability', 0)
        for s in scenarios
    )

    # Find best and worst cases
    best_case = min(scenarios, key=lambda s: s.get('cost', float('inf')))
    worst_case = max(scenarios, key=lambda s: s.get('cost', 0))

    # Calculate variance and standard deviation
    variance = sum(
        s.get('probability', 0) * (s.get('cost', 0) - expected_value) ** 2
        for s in scenarios
    )
    std_dev = variance ** 0.5

    return {
        'expected_value': round(expected_value, 2),
        'scenarios': scenarios,
        'best_case': {
            'name': best_case.get('name'),
            'cost': best_case.get('cost'),
            'probability': best_case.get('probability')
        },
        'worst_case': {
            'name': worst_case.get('name'),
            'cost': worst_case.get('cost'),
            'probability': worst_case.get('probability')
        },
        'variance': round(variance, 2),
        'std_dev': round(std_dev, 2),
        'coefficient_of_variation': round(std_dev / expected_value, 4) if expected_value > 0 else 0,
        'range': round(worst_case.get('cost', 0) - best_case.get('cost', 0), 2)
    }


def hearing_cost_benefit(
    settlement_offer: float,
    hearing_ev: float,
    costs: Dict[str, float]
) -> Dict:
    """
    Cost-benefit analysis of settlement vs. hearing.

    Args:
        settlement_offer: Proposed settlement amount
        hearing_ev: Expected value of hearing outcome (from calculate_batna)
        costs: Dict with cost details
            {
                'legal_fees_to_hearing': 50000,
                'expert_fees_to_hearing': 30000,
                'time_cost_to_hearing': 10000,
                'legal_fees_to_settle': 5000,
                'settlement_risk': 0.1  # Risk settlement fails
            }

    Returns:
        Dict containing cost-benefit analysis
            {
                'settlement_total_cost': 185000,
                'hearing_total_cost': 245000,
                'net_benefit_of_settlement': 60000,
                'recommendation': 'SETTLE',
                'breakeven_settlement': 155000,
                'savings_percentage': 24.5
            }
    """
    # Calculate total cost of settlement
    settlement_total = settlement_offer + costs.get('legal_fees_to_settle', 0)

    # Calculate total cost of hearing (already includes legal/expert fees)
    hearing_total = hearing_ev

    # Net benefit of settlement (positive = settlement better)
    net_benefit = hearing_total - settlement_total

    # Breakeven settlement amount (where settlement cost = hearing cost)
    breakeven = hearing_ev - costs.get('legal_fees_to_settle', 0)

    # Determine recommendation
    if net_benefit > 0:
        recommendation = 'SETTLE'
        rationale = f'Settlement saves ${net_benefit:,.2f} vs. hearing'
    elif net_benefit < -10000:  # Material negative
        recommendation = 'PROCEED TO HEARING'
        rationale = f'Hearing saves ${abs(net_benefit):,.2f} vs. settlement'
    else:
        recommendation = 'NEUTRAL'
        rationale = 'Costs are roughly equivalent'

    return {
        'settlement_total_cost': round(settlement_total, 2),
        'hearing_total_cost': round(hearing_total, 2),
        'net_benefit_of_settlement': round(net_benefit, 2),
        'recommendation': recommendation,
        'rationale': rationale,
        'breakeven_settlement': round(breakeven, 2),
        'savings_percentage': round((net_benefit / hearing_total) * 100, 2) if hearing_total > 0 else 0,
        'risk_adjusted_benefit': round(
            net_benefit * (1 - costs.get('settlement_risk', 0)), 2
        )
    }


def optimal_settlement_range(
    batna: float,
    zopa: Dict,
    confidence: float = 0.8
) -> Dict:
    """
    Recommend optimal settlement range based on BATNA and ZOPA.

    Args:
        batna: Net BATNA (total expected cost to buyer from hearing)
        zopa: ZOPA dict from calculate_zopa()
        confidence: Confidence level for range (0.0 to 1.0)
            0.8 = recommend within 80% of ZOPA range

    Returns:
        Dict containing settlement recommendations
            {
                'target': 175000,
                'floor': 160000,   # Don't go below this
                'ceiling': 190000,  # Don't go above this
                'opening_offer': 155000,
                'walkaway': 200000,
                'strategy': 'Start at opening, target midpoint, walk at ceiling'
            }
    """
    if not zopa.get('exists'):
        return {
            'error': 'No ZOPA exists',
            'batna': batna,
            'recommendation': 'Proceed to hearing - no settlement range available'
        }

    zopa_lower = zopa.get('lower_bound', 0)
    zopa_upper = zopa.get('upper_bound', 0)
    zopa_mid = zopa.get('midpoint', 0)

    # Adjust target based on confidence
    # Higher confidence = narrower range around midpoint
    range_factor = 1 - confidence
    adjustment = (zopa_upper - zopa_lower) * range_factor / 2

    target = zopa_mid
    floor = zopa_mid - adjustment
    ceiling = zopa_mid + adjustment

    # Opening offer should be below floor (leave room to negotiate up)
    opening_offer = zopa_lower + (floor - zopa_lower) * 0.5

    # Walkaway point is BATNA or ZOPA upper, whichever is lower
    walkaway = min(batna, zopa_upper)

    return {
        'target': round(target, 2),
        'floor': round(floor, 2),
        'ceiling': round(ceiling, 2),
        'opening_offer': round(opening_offer, 2),
        'walkaway': round(walkaway, 2),
        'confidence_level': confidence,
        'strategy': f'Open at ${opening_offer:,.2f}, target ${target:,.2f}, walk at ${walkaway:,.2f}',
        'negotiation_room': {
            'from_opening_to_target': round(target - opening_offer, 2),
            'from_target_to_walkaway': round(walkaway - target, 2)
        },
        'zopa_utilization': round(
            (ceiling - floor) / (zopa_upper - zopa_lower), 4
        ) if (zopa_upper - zopa_lower) > 0 else 0
    }


def calculate_concession_strategy(
    opening: float,
    target: float,
    num_rounds: int = 3
) -> List[Dict]:
    """
    Calculate a concession strategy from opening to target.

    Uses diminishing concessions pattern (larger concessions early,
    smaller concessions later to signal approaching limit).

    Args:
        opening: Opening offer amount
        target: Target settlement amount
        num_rounds: Number of negotiation rounds (default 3)

    Returns:
        List of concession rounds
            [
                {'round': 1, 'offer': 155000, 'concession': 0, 'message': 'Opening'},
                {'round': 2, 'offer': 167500, 'concession': 12500, 'message': '50% of gap'},
                {'round': 3, 'offer': 173750, 'concession': 6250, 'message': '25% of gap'},
                {'round': 4, 'offer': 175000, 'concession': 1250, 'message': 'Final offer'}
            ]
    """
    if num_rounds < 1:
        num_rounds = 1

    total_gap = target - opening

    rounds = []
    current_offer = opening
    remaining_gap = total_gap

    # Round 1: Opening offer
    rounds.append({
        'round': 1,
        'offer': round(opening, 2),
        'concession': 0,
        'concession_pct': 0,
        'message': 'Opening offer'
    })

    # Subsequent rounds: Diminishing concessions
    # Pattern: 50%, 25%, 12.5%, 6.25% of remaining gap
    for i in range(1, num_rounds):
        concession_rate = 0.5 ** i
        concession = remaining_gap * concession_rate
        current_offer += concession
        remaining_gap -= concession

        rounds.append({
            'round': i + 1,
            'offer': round(current_offer, 2),
            'concession': round(concession, 2),
            'concession_pct': round(concession_rate * 100, 1),
            'message': f'{concession_rate * 100:.0f}% of remaining gap'
        })

    # Final round: Target
    if current_offer < target:
        final_concession = target - current_offer
        rounds.append({
            'round': len(rounds) + 1,
            'offer': round(target, 2),
            'concession': round(final_concession, 2),
            'concession_pct': round((final_concession / total_gap) * 100, 1),
            'message': 'Final offer - at target'
        })

    return rounds
