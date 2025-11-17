#!/usr/bin/env python3
"""
Analysis Module for Negotiation Settlement Calculator
Risk analysis, settlement comparison, and strategy generation
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Add Shared_Utils to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "Shared_Utils"))
from risk_utils import assess_holdout_risk
from negotiation_utils import (
    hearing_cost_benefit,
    calculate_concession_strategy as shared_concession_strategy
)

logger = logging.getLogger(__name__)


def analyze_holdout_risk(owner_profile: Optional[Dict] = None) -> Dict:
    """
    Analyze holdout risk from owner profile.

    Wrapper around shared utility with enhanced logging.

    Args:
        owner_profile: Dict with owner characteristics (motivation, sophistication, alternatives)

    Returns:
        Dict with holdout risk assessment (score, level, probability, mitigation)
    """
    if owner_profile is None:
        logger.warning("No owner profile provided - using default risk assessment")
        return {
            'total_score': 15,
            'risk_level': 'MEDIUM',
            'holdout_probability': 0.30,
            'message': 'Default risk profile - no owner data provided'
        }

    logger.info("Analyzing holdout risk from owner profile")

    risk_assessment = assess_holdout_risk(owner_profile)

    logger.info(f"Holdout risk: {risk_assessment['risk_level']} (score: {risk_assessment['total_score']}/30, probability: {risk_assessment['holdout_probability']:.1%})")

    return risk_assessment


def analyze_settlement_vs_hearing(
    settlement_offer: float,
    batna_net: float,
    legal_costs_to_settle: float = 5000.0,
    settlement_risk: float = 0.1
) -> Dict:
    """
    Cost-benefit analysis of settlement vs. hearing.

    Wrapper around shared utility with enhanced logging.

    Args:
        settlement_offer: Proposed settlement amount
        batna_net: Net BATNA (expected cost of hearing)
        legal_costs_to_settle: Legal costs to complete settlement
        settlement_risk: Risk that settlement falls through

    Returns:
        Dict with cost-benefit analysis and recommendation
    """
    logger.info(f"Analyzing settlement (${settlement_offer:,.2f}) vs. hearing (${batna_net:,.2f})")

    costs = {
        'legal_fees_to_settle': legal_costs_to_settle,
        'settlement_risk': settlement_risk
    }

    analysis = hearing_cost_benefit(settlement_offer, batna_net, costs)

    logger.info(f"Recommendation: {analysis['recommendation']} - Net benefit: ${analysis['net_benefit_of_settlement']:,.2f}")

    return analysis


def generate_concession_strategy(
    opening_offer: float,
    target_settlement: float,
    num_rounds: int = 3
) -> Dict:
    """
    Generate concession strategy from opening to target.

    Wrapper around shared utility with enhanced formatting.

    Args:
        opening_offer: Opening offer amount
        target_settlement: Target settlement amount
        num_rounds: Number of negotiation rounds

    Returns:
        Dict with concession rounds and strategy
    """
    logger.info(f"Generating concession strategy - Open: ${opening_offer:,.2f}, Target: ${target_settlement:,.2f}, Rounds: {num_rounds}")

    rounds = shared_concession_strategy(opening_offer, target_settlement, num_rounds)

    # Calculate strategy metrics
    total_movement = target_settlement - opening_offer
    largest_concession = max(r['concession'] for r in rounds[1:]) if len(rounds) > 1 else 0
    smallest_concession = min(r['concession'] for r in rounds[1:] if r['concession'] > 0) if len(rounds) > 1 else 0

    strategy = {
        'rounds': rounds,
        'total_rounds': len(rounds),
        'total_movement': round(total_movement, 2),
        'largest_concession': round(largest_concession, 2),
        'smallest_concession': round(smallest_concession, 2),
        'pattern': 'diminishing' if len(rounds) > 1 else 'single_offer',
        'strategy_notes': [
            f"Start at ${opening_offer:,.2f} (opening offer)",
            f"Target ${target_settlement:,.2f} over {num_rounds} rounds",
            "Use diminishing concessions to signal approaching limit",
            f"Final concession should be small (${smallest_concession:,.2f}) to show you're at your limit"
        ]
    }

    logger.info(f"Concession strategy generated - {len(rounds)} rounds, total movement: ${total_movement:,.2f}")

    return strategy


def analyze_negotiation_power(
    buyer_max: float,
    seller_min: float,
    batna_buyer: float,
    batna_seller: Optional[float] = None
) -> Dict:
    """
    Analyze relative negotiation power between parties.

    Args:
        buyer_max: Maximum buyer is willing to pay
        seller_min: Minimum seller is willing to accept
        batna_buyer: Buyer's BATNA (expected cost of hearing)
        batna_seller: Seller's BATNA (expected award from hearing)

    Returns:
        Dict with power analysis and leverage indicators
    """
    logger.info("Analyzing relative negotiation power")

    # If seller's BATNA not provided, estimate it
    if batna_seller is None:
        # Estimate: seller expects midpoint of buyer's BATNA range
        batna_seller = batna_buyer * 0.75  # Assume seller expects 75% of buyer's BATNA

    # Calculate power metrics
    buyer_batna_strength = (buyer_max - batna_buyer) / buyer_max if buyer_max > 0 else 0
    seller_batna_strength = (batna_seller - seller_min) / batna_seller if batna_seller > 0 else 0

    # Determine who has stronger position
    if buyer_batna_strength > seller_batna_strength:
        advantage = "BUYER"
        advantage_degree = abs(buyer_batna_strength - seller_batna_strength)
    elif seller_batna_strength > buyer_batna_strength:
        advantage = "SELLER"
        advantage_degree = abs(seller_batna_strength - buyer_batna_strength)
    else:
        advantage = "BALANCED"
        advantage_degree = 0

    # Determine advantage level
    if advantage_degree > 0.3:
        advantage_level = "STRONG"
    elif advantage_degree > 0.15:
        advantage_level = "MODERATE"
    else:
        advantage_level = "SLIGHT"

    analysis = {
        'buyer_batna_strength': round(buyer_batna_strength, 3),
        'seller_batna_strength': round(seller_batna_strength, 3),
        'advantage': advantage,
        'advantage_level': advantage_level if advantage != "BALANCED" else None,
        'advantage_degree': round(advantage_degree, 3),
        'buyer_walkaway': round(batna_buyer, 2),
        'seller_walkaway': round(batna_seller, 2),
        'interpretation': _interpret_power_balance(
            advantage, advantage_level, buyer_batna_strength, seller_batna_strength
        )
    }

    logger.info(f"Negotiation power: {advantage} advantage ({advantage_level if advantage != 'BALANCED' else 'BALANCED'})")

    return analysis


def _interpret_power_balance(
    advantage: str,
    advantage_level: Optional[str],
    buyer_strength: float,
    seller_strength: float
) -> str:
    """Generate interpretation of power balance."""

    if advantage == "BALANCED":
        return (
            "Both parties have similar BATNA strength. Neither has significant leverage. "
            "Settlement likely to occur near ZOPA midpoint. "
            "Focus on creating value and building rapport."
        )

    elif advantage == "BUYER":
        if advantage_level == "STRONG":
            return (
                f"Buyer has strong negotiating position (BATNA strength: {buyer_strength:.1%} vs {seller_strength:.1%}). "
                "Buyer can be aggressive in negotiation. "
                "Open below ZOPA midpoint and concede slowly. "
                "Seller has limited alternatives."
            )
        elif advantage_level == "MODERATE":
            return (
                f"Buyer has moderate advantage (BATNA strength: {buyer_strength:.1%} vs {seller_strength:.1%}). "
                "Can negotiate from position of strength but avoid being too aggressive. "
                "Open at favorable position but be prepared to move toward midpoint."
            )
        else:  # SLIGHT
            return (
                f"Buyer has slight advantage (BATNA strength: {buyer_strength:.1%} vs {seller_strength:.1%}). "
                "Leverage is minimal. "
                "Negotiate fairly and focus on relationship. "
                "Small advantage may disappear if seller finds alternatives."
            )

    else:  # SELLER
        if advantage_level == "STRONG":
            return (
                f"Seller has strong negotiating position (BATNA strength: {seller_strength:.1%} vs {buyer_strength:.1%}). "
                "Buyer has weak position. "
                "May need to offer near seller's minimum or risk losing deal. "
                "Consider improving your BATNA before negotiating."
            )
        elif advantage_level == "MODERATE":
            return (
                f"Seller has moderate advantage (BATNA strength: {seller_strength:.1%} vs {buyer_strength:.1%}). "
                "Buyer negotiating from weaker position. "
                "Be prepared to settle above ZOPA midpoint. "
                "Focus on non-price terms where possible."
            )
        else:  # SLIGHT
            return (
                f"Seller has slight advantage (BATNA strength: {seller_strength:.1%} vs {buyer_strength:.1%}). "
                "Relatively balanced negotiation. "
                "Settlement near midpoint likely. "
                "Small concessions may secure agreement."
            )


def calculate_negotiation_efficiency(
    final_settlement: float,
    initial_offer: float,
    num_rounds: int,
    total_negotiation_time_hours: float
) -> Dict:
    """
    Calculate efficiency metrics for negotiation process.

    Args:
        final_settlement: Final agreed settlement amount
        initial_offer: Initial offer amount
        num_rounds: Number of negotiation rounds
        total_negotiation_time_hours: Total time spent negotiating

    Returns:
        Dict with efficiency metrics
    """
    total_movement = abs(final_settlement - initial_offer)
    avg_movement_per_round = total_movement / num_rounds if num_rounds > 0 else 0
    time_per_round = total_negotiation_time_hours / num_rounds if num_rounds > 0 else 0

    # Efficiency score (lower rounds and time = more efficient)
    # Benchmark: 3 rounds, 6 hours = 100 points
    rounds_efficiency = (3 / num_rounds) * 50 if num_rounds > 0 else 0
    time_efficiency = (6 / total_negotiation_time_hours) * 50 if total_negotiation_time_hours > 0 else 0
    total_efficiency = min(rounds_efficiency + time_efficiency, 100)

    return {
        'total_movement': round(total_movement, 2),
        'num_rounds': num_rounds,
        'avg_movement_per_round': round(avg_movement_per_round, 2),
        'total_time_hours': round(total_negotiation_time_hours, 2),
        'time_per_round_hours': round(time_per_round, 2),
        'efficiency_score': round(total_efficiency, 1),
        'benchmark': 'Efficient negotiation: 3 rounds, 6 hours',
        'interpretation': _interpret_efficiency(total_efficiency, num_rounds, total_negotiation_time_hours)
    }


def _interpret_efficiency(score: float, rounds: int, time: float) -> str:
    """Interpret negotiation efficiency."""
    if score >= 80:
        return f"Highly efficient negotiation ({rounds} rounds, {time:.1f} hours)"
    elif score >= 60:
        return f"Moderately efficient negotiation ({rounds} rounds, {time:.1f} hours)"
    elif score >= 40:
        return f"Below average efficiency ({rounds} rounds, {time:.1f} hours) - consider streamlining process"
    else:
        return f"Inefficient negotiation ({rounds} rounds, {time:.1f} hours) - significant time/effort invested"
