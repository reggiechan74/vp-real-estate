#!/usr/bin/env python3
"""
Calculations Module for Negotiation Settlement Calculator
Core calculation functions using shared utilities
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Add Shared_Utils to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "Shared_Utils"))
from negotiation_utils import (
    calculate_batna,
    calculate_zopa,
    probability_weighted_ev,
    optimal_settlement_range
)

logger = logging.getLogger(__name__)


def calculate_batna_analysis(
    hearing_probabilities: Dict[str, float],
    hearing_costs: Dict[str, float]
) -> Dict:
    """
    Calculate BATNA (Best Alternative to Negotiated Agreement) analysis.

    Wrapper around shared utility with enhanced logging.

    Args:
        hearing_probabilities: Probability distribution for hearing outcomes
        hearing_costs: Cost estimates for hearing

    Returns:
        Dict with BATNA analysis including expected award, costs, net BATNA
    """
    logger.info("Calculating BATNA analysis")
    logger.debug(f"Hearing probabilities: {hearing_probabilities}")
    logger.debug(f"Hearing costs: {hearing_costs}")

    batna_result = calculate_batna(hearing_probabilities, hearing_costs)

    logger.info(f"BATNA calculation complete - Net BATNA: ${batna_result['net_batna']:,.2f}")

    return batna_result


def calculate_zopa_analysis(buyer_max: float, seller_min: float) -> Dict:
    """
    Calculate ZOPA (Zone of Possible Agreement) analysis.

    Wrapper around shared utility with enhanced logging.

    Args:
        buyer_max: Maximum buyer is willing to pay
        seller_min: Minimum seller is willing to accept

    Returns:
        Dict with ZOPA analysis including bounds, midpoint, surplus
    """
    logger.info(f"Calculating ZOPA - Buyer max: ${buyer_max:,.2f}, Seller min: ${seller_min:,.2f}")

    zopa_result = calculate_zopa(buyer_max, seller_min)

    if zopa_result['exists']:
        logger.info(f"ZOPA exists - Range: ${zopa_result['lower_bound']:,.2f} to ${zopa_result['upper_bound']:,.2f}")
    else:
        logger.warning(f"No ZOPA - Gap of ${zopa_result.get('gap', 0):,.2f}")

    return zopa_result


def calculate_probability_weighted_scenarios(
    buyer_max: float,
    seller_min: float,
    batna_net: float,
    settlement_offer: Optional[float] = None
) -> Dict:
    """
    Calculate probability-weighted expected value across negotiation scenarios.

    Args:
        buyer_max: Maximum buyer is willing to pay
        seller_min: Minimum seller is willing to accept
        batna_net: Net BATNA (expected cost of hearing)
        settlement_offer: Optional proposed settlement amount

    Returns:
        Dict with expected value analysis across scenarios
    """
    logger.info("Calculating probability-weighted scenarios")

    # Define scenarios based on ZOPA and BATNA
    zopa = calculate_zopa(buyer_max, seller_min)

    scenarios = []

    if zopa['exists']:
        # Scenario 1: Settle at seller's minimum (best case for buyer)
        scenarios.append({
            'name': 'Settle at seller minimum',
            'cost': seller_min,
            'probability': 0.25  # 25% chance
        })

        # Scenario 2: Settle at midpoint (most likely)
        scenarios.append({
            'name': 'Settle at ZOPA midpoint',
            'cost': zopa['midpoint'],
            'probability': 0.40  # 40% chance
        })

        # Scenario 3: Settle near buyer's maximum
        scenarios.append({
            'name': 'Settle near buyer maximum',
            'cost': buyer_max * 0.95,
            'probability': 0.20  # 20% chance
        })

        # Scenario 4: Proceed to hearing
        scenarios.append({
            'name': 'Proceed to hearing',
            'cost': batna_net,
            'probability': 0.15  # 15% chance of negotiation failure
        })

    else:
        # No ZOPA - higher probability of hearing
        scenarios.append({
            'name': 'Attempt settlement at buyer max',
            'cost': buyer_max,
            'probability': 0.30  # 30% chance seller accepts
        })

        scenarios.append({
            'name': 'Proceed to hearing',
            'cost': batna_net,
            'probability': 0.70  # 70% chance if no ZOPA
        })

    # If settlement offer provided, add as scenario
    if settlement_offer is not None:
        # Recalculate probabilities to include settlement offer
        if zopa['exists'] and zopa['lower_bound'] <= settlement_offer <= zopa['upper_bound']:
            # Settlement within ZOPA - higher acceptance probability
            scenarios = [
                {
                    'name': f'Accept current offer (${settlement_offer:,.0f})',
                    'cost': settlement_offer,
                    'probability': 0.60
                },
                {
                    'name': 'Counter and settle higher',
                    'cost': (settlement_offer + buyer_max) / 2,
                    'probability': 0.25
                },
                {
                    'name': 'Proceed to hearing',
                    'cost': batna_net,
                    'probability': 0.15
                }
            ]

    ev_result = probability_weighted_ev(scenarios)

    logger.info(f"Expected value across scenarios: ${ev_result['expected_value']:,.2f}")

    return ev_result


def calculate_optimal_settlement(
    batna_net: float,
    zopa: Dict,
    confidence: float = 0.8
) -> Dict:
    """
    Calculate optimal settlement range and strategy.

    Wrapper around shared utility with enhanced logging.

    Args:
        batna_net: Net BATNA (total expected cost to buyer)
        zopa: ZOPA dict from calculate_zopa()
        confidence: Confidence level for range (0.0 to 1.0)

    Returns:
        Dict with optimal settlement recommendations
    """
    logger.info(f"Calculating optimal settlement range (confidence: {confidence})")

    optimal = optimal_settlement_range(batna_net, zopa, confidence)

    if 'error' in optimal:
        logger.warning(f"Cannot determine optimal settlement: {optimal['error']}")
    else:
        logger.info(f"Optimal target: ${optimal['target']:,.2f}, Range: ${optimal['floor']:,.2f} - ${optimal['ceiling']:,.2f}")

    return optimal


def calculate_settlement_value(
    buyer_max: float,
    seller_min: float,
    batna_net: float,
    method: str = 'midpoint'
) -> Dict:
    """
    Calculate settlement value using various methods.

    Args:
        buyer_max: Maximum buyer is willing to pay
        seller_min: Minimum seller is willing to accept
        batna_net: Net BATNA (expected cost of hearing)
        method: Calculation method
            'midpoint' - ZOPA midpoint
            'batna_adjusted' - Adjust based on BATNA
            'proportional' - Proportional to leverage

    Returns:
        Dict with calculated settlement value and rationale
    """
    logger.info(f"Calculating settlement value using method: {method}")

    zopa = calculate_zopa(buyer_max, seller_min)

    if not zopa['exists']:
        return {
            'method': method,
            'settlement_value': None,
            'error': 'No ZOPA exists',
            'recommendation': f'Offer up to ${buyer_max:,.2f} or proceed to hearing'
        }

    if method == 'midpoint':
        value = zopa['midpoint']
        rationale = "ZOPA midpoint - equal surplus for both parties"

    elif method == 'batna_adjusted':
        # Adjust midpoint based on how BATNA compares to ZOPA
        if batna_net < zopa['upper_bound']:
            # BATNA is attractive - can be more aggressive
            value = zopa['midpoint'] - (zopa['midpoint'] - zopa['lower_bound']) * 0.25
            rationale = "BATNA is attractive - negotiate closer to seller minimum"
        else:
            # BATNA is unattractive - settle higher to avoid hearing
            value = zopa['midpoint'] + (zopa['upper_bound'] - zopa['midpoint']) * 0.25
            rationale = "BATNA is unattractive - willing to pay more to avoid hearing"

    elif method == 'proportional':
        # Proportional split based on negotiating leverage
        buyer_leverage = zopa['negotiation_leverage']['buyer']
        value = zopa['lower_bound'] + (zopa['range'] * buyer_leverage)
        rationale = f"Proportional split based on negotiating leverage ({buyer_leverage:.1%} to buyer)"

    else:
        return {
            'method': method,
            'settlement_value': None,
            'error': f'Unknown method: {method}'
        }

    # Ensure value is within ZOPA
    value = max(zopa['lower_bound'], min(value, zopa['upper_bound']))

    return {
        'method': method,
        'settlement_value': round(value, 2),
        'rationale': rationale,
        'buyer_surplus': round(buyer_max - value, 2),
        'seller_surplus': round(value - seller_min, 2),
        'zopa_bounds': {
            'lower': zopa['lower_bound'],
            'upper': zopa['upper_bound']
        }
    }
