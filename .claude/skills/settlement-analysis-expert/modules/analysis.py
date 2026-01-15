#!/usr/bin/env python3
"""
Settlement analysis and strategic planning.
Analyze settlement vs. hearing, calculate ZOPA, and generate strategies.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add Shared_Utils to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'Shared_Utils'))

from negotiation_utils import calculate_zopa, optimal_settlement_range, calculate_concession_strategy
from risk_utils import assess_holdout_risk, litigation_risk_assessment, sensitivity_analysis


def analyze_settlement_vs_hearing(
    settlement_offer: float,
    hearing_batna: Dict,
    settlement_costs: Dict = None
) -> Dict:
    """
    Comprehensive analysis of settlement vs. hearing decision.

    Args:
        settlement_offer: Proposed settlement amount
        hearing_batna: BATNA analysis from calculations module
        settlement_costs: Optional settlement costs

    Returns:
        Dict containing comprehensive decision analysis
    """
    legal_fees = 5000
    if settlement_costs:
        legal_fees = settlement_costs.get('legal_fees_to_settle', 5000)

    settlement_total = settlement_offer + legal_fees
    hearing_total = hearing_batna['net_batna']

    net_benefit = hearing_total - settlement_total

    # Determine recommendation
    if net_benefit > 10000:
        recommendation = 'SETTLE'
        rationale = f'Settlement saves ${net_benefit:,.0f} vs. hearing'
        confidence = 'HIGH'
    elif net_benefit > 0:
        recommendation = 'SETTLE'
        rationale = f'Settlement saves ${net_benefit:,.0f} vs. hearing'
        confidence = 'MEDIUM'
    elif net_benefit > -10000:
        recommendation = 'NEUTRAL'
        rationale = 'Costs are roughly equivalent - continue negotiations'
        confidence = 'LOW'
    else:
        recommendation = 'PROCEED TO HEARING'
        rationale = f'Hearing saves ${abs(net_benefit):,.0f} vs. settlement'
        confidence = 'MEDIUM'

    # Calculate risk-adjusted recommendation
    hearing_risk = hearing_batna.get('standard_deviation', 0)
    risk_premium = hearing_risk * 0.5  # Adjust for risk aversion

    risk_adjusted_benefit = net_benefit - risk_premium

    return {
        'recommendation': recommendation,
        'rationale': rationale,
        'confidence': confidence,
        'settlement_total': round(settlement_total, 2),
        'hearing_total': round(hearing_total, 2),
        'net_benefit': round(net_benefit, 2),
        'risk_adjusted_benefit': round(risk_adjusted_benefit, 2),
        'savings_percentage': round((net_benefit / hearing_total * 100), 2) if hearing_total > 0 else 0,
        'hearing_uncertainty': {
            'standard_deviation': hearing_batna.get('standard_deviation', 0),
            'coefficient_of_variation': hearing_batna.get('coefficient_of_variation', 0),
            'award_range': hearing_batna.get('award_range', {})
        }
    }


def calculate_zopa_analysis(
    settlement_offer: float,
    counteroffer: float,
    hearing_batna: Dict,
    settlement_costs: Dict = None
) -> Dict:
    """
    Calculate Zone of Possible Agreement.

    Args:
        settlement_offer: Buyer's offer
        counteroffer: Seller's counteroffer
        hearing_batna: BATNA analysis
        settlement_costs: Optional settlement costs

    Returns:
        Dict containing ZOPA analysis and optimal range
    """
    # Buyer's maximum is BATNA (total cost of hearing)
    buyer_max = hearing_batna['net_batna']

    # Seller's minimum is their counteroffer (or we estimate it)
    seller_min = counteroffer

    # Calculate ZOPA
    zopa = calculate_zopa(buyer_max, seller_min)

    # Calculate optimal settlement range
    if zopa['exists']:
        optimal_range = optimal_settlement_range(
            batna=buyer_max,
            zopa=zopa,
            confidence=0.8
        )
    else:
        optimal_range = {
            'error': 'No ZOPA exists',
            'gap': zopa.get('gap', 0),
            'recommendation': 'Proceed to hearing - settlement not viable'
        }

    return {
        'zopa': zopa,
        'optimal_range': optimal_range,
        'buyer_position': {
            'current_offer': settlement_offer,
            'maximum': buyer_max,
            'room_to_negotiate': round(buyer_max - settlement_offer, 2)
        },
        'seller_position': {
            'counteroffer': counteroffer,
            'minimum_estimated': seller_min
        }
    }


def generate_concession_strategy(
    opening_offer: float,
    target: float,
    num_rounds: int = 3
) -> Dict:
    """
    Generate negotiation concession strategy.

    Args:
        opening_offer: Initial offer amount
        target: Target settlement amount
        num_rounds: Number of negotiation rounds

    Returns:
        Dict containing concession strategy
    """
    # Calculate concession rounds
    rounds = calculate_concession_strategy(opening_offer, target, num_rounds)

    total_concessions = target - opening_offer

    return {
        'opening_offer': round(opening_offer, 2),
        'target': round(target, 2),
        'total_concessions': round(total_concessions, 2),
        'num_rounds': len(rounds),
        'rounds': rounds,
        'strategy_notes': [
            'Use diminishing concessions pattern (larger early, smaller later)',
            'Signal approaching limit with smaller concessions',
            'Justify each concession with new information or reciprocity',
            'Avoid making first concession without receiving something in return'
        ]
    }


def assess_owner_holdout_risk(owner_profile: Dict) -> Dict:
    """
    Assess risk that owner will hold out and force hearing.

    Args:
        owner_profile: Owner profile data

    Returns:
        Dict containing holdout risk assessment
    """
    if not owner_profile:
        return {
            'total_score': 15,
            'risk_level': 'MEDIUM',
            'holdout_probability': 0.3,
            'note': 'Default risk assessment - no owner profile provided'
        }

    return assess_holdout_risk(owner_profile)


def assess_litigation_risk(case_factors: Dict) -> Dict:
    """
    Assess litigation probability and expected duration.

    Args:
        case_factors: Case characteristics

    Returns:
        Dict containing litigation risk analysis
    """
    if not case_factors:
        return {
            'litigation_probability': 0.5,
            'expected_duration_months': 12,
            'expected_cost': 90000,
            'note': 'Default risk assessment - no case factors provided'
        }

    return litigation_risk_assessment(case_factors)


def perform_sensitivity_analysis(
    base_settlement: float,
    hearing_batna: Dict,
    settlement_costs: Dict = None
) -> Dict:
    """
    Sensitivity analysis showing impact of variable changes.

    Args:
        base_settlement: Base case settlement amount
        hearing_batna: BATNA analysis
        settlement_costs: Optional settlement costs

    Returns:
        Dict containing sensitivity analysis
    """
    legal_fees = 5000
    if settlement_costs:
        legal_fees = settlement_costs.get('legal_fees_to_settle', 5000)

    base_total = base_settlement + legal_fees
    hearing_total = hearing_batna['net_batna']

    # Base case
    base_case = {
        'total_cost': base_total,
        'settlement': base_settlement,
        'legal_costs': legal_fees
    }

    # Test variables at different levels
    variables = {
        'settlement': [
            base_settlement * 0.9,  # -10%
            base_settlement,        # Base
            base_settlement * 1.1   # +10%
        ],
        'legal_costs': [
            legal_fees * 0.8,       # -20%
            legal_fees,             # Base
            legal_fees * 1.2        # +20%
        ]
    }

    ranges = {
        'settlement': (-10, 10),
        'legal_costs': (-20, 20)
    }

    return sensitivity_analysis(base_case, variables, ranges)
