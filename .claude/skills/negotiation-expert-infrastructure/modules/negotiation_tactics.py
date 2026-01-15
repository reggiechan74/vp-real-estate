#!/usr/bin/env python3
"""
Negotiation Tactics Module

Provides tactical recommendations for opening offers, concession strategies,
and leverage analysis.

Functions:
- recommend_opening_offer(): Calculate optimal opening position
- generate_concession_plan(): Create diminishing concession strategy
- identify_leverage_points(): Analyze negotiation leverage
"""

from typing import Dict, List
import sys
from pathlib import Path

# Add Shared_Utils to path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from Shared_Utils.negotiation_utils import calculate_concession_strategy


def recommend_opening_offer(
    settlement_range: Dict,
    owner_analysis: Dict,
    holdout_risk: Dict,
    context: Dict
) -> Dict:
    """
    Recommend opening offer based on settlement range, owner psychology, and context.

    Strategy:
    - Low holdout risk: Aggressive opening (30-40% below target)
    - Medium holdout risk: Moderate opening (20-30% below target)
    - High holdout risk: Conservative opening (10-20% below target)

    Also considers:
    - Owner sophistication (sophisticated = less room to negotiate up)
    - Timeline pressure (urgent = start higher to close faster)
    - Relationship importance (legacy holder = start fairer)

    Args:
        settlement_range: Output from optimal_settlement_range()
        owner_analysis: Output from analyze_owner_psychology()
        holdout_risk: Output from assess_holdout_risk()
        context: Output from analyze_negotiation_context()

    Returns:
        Dict with opening offer recommendation
            {
                'recommended_opening': 155000,
                'rationale': '25% below target - moderate holdout risk',
                'negotiation_room': 20000,
                'messaging': [...],
                'supporting_evidence': [...]
            }
    """
    target = settlement_range.get('target', 0)
    floor = settlement_range.get('floor', 0)

    risk_level = holdout_risk.get('risk_level', 'MEDIUM')
    owner_type = owner_analysis.get('owner_type', 'RATIONAL_INVESTOR')
    sophistication = owner_analysis.get('sophistication_level', 'MEDIUM')
    timeline = context.get('timeline_pressure', 'medium')

    # Base opening percentage below target
    if risk_level in ['CRITICAL', 'HIGH']:
        opening_pct = 0.85  # 15% below target (conservative)
    elif risk_level == 'MEDIUM':
        opening_pct = 0.75  # 25% below target (moderate)
    else:  # LOW
        opening_pct = 0.65  # 35% below target (aggressive)

    # Adjust for owner type
    if owner_type == 'LEGACY_HOLDER':
        opening_pct += 0.10  # Start fairer to build relationship
    elif owner_type == 'SOPHISTICATED_HOLDOUT':
        opening_pct += 0.05  # Less room to negotiate with sophisticated owners
    elif owner_type == 'FINANCIAL_DISTRESS':
        opening_pct -= 0.05  # Can start lower with motivated seller

    # Adjust for timeline
    if timeline == 'critical':
        opening_pct += 0.15  # Start higher to close faster
    elif timeline == 'high':
        opening_pct += 0.10

    # Adjust for sophistication
    if sophistication == 'HIGH':
        opening_pct += 0.05

    # Cap adjustments
    opening_pct = max(0.60, min(opening_pct, 0.95))

    # Calculate opening offer
    recommended_opening = target * opening_pct

    # Ensure it's above floor
    if floor > 0:
        recommended_opening = max(recommended_opening, floor * 0.95)

    negotiation_room = target - recommended_opening

    # Build rationale
    risk_desc = {
        'CRITICAL': 'very high holdout risk - conservative opening required',
        'HIGH': 'high holdout risk - limited room to negotiate',
        'MEDIUM': 'moderate holdout risk - balanced approach',
        'LOW': 'low holdout risk - aggressive opening possible'
    }

    rationale = f"{int((1 - opening_pct) * 100)}% below target - {risk_desc.get(risk_level, 'balanced approach')}"

    # Messaging recommendations
    messaging = []

    if owner_type == 'LEGACY_HOLDER':
        messaging.append('Lead with respect for property history before discussing numbers')
        messaging.append('Use accusation audit: "You probably think this offer is low given your family\'s history here..."')
        messaging.append('Frame as starting point for fair discussion, not final number')

    elif owner_type == 'SOPHISTICATED_HOLDOUT':
        messaging.append('Present comprehensive market evidence with opening offer')
        messaging.append('Anchor strongly with comparable sales data')
        messaging.append('Be direct about BATNA to establish credibility')

    elif owner_type == 'OPERATING_BUSINESS':
        messaging.append('Emphasize support for business transition before price discussion')
        messaging.append('Ask calibrated questions: "What would make the transition work for your operations?"')
        messaging.append('Frame price in context of total transition package')

    elif owner_type == 'FINANCIAL_DISTRESS':
        messaging.append('Emphasize speed and certainty benefits')
        messaging.append('Offer quick close timeline and payment options')
        messaging.append('Compare to delays and costs of hearing process')

    else:  # RATIONAL_INVESTOR
        messaging.append('Lead with market comparable analysis')
        messaging.append('Present evidence-based valuation methodology')
        messaging.append('Frame as fair market value based on objective data')

    # Timeline-specific messaging
    if timeline == 'critical':
        messaging.append('Express project timeline needs clearly')
        messaging.append('Offer premium for quick settlement if appropriate')

    # Supporting evidence
    supporting_evidence = [
        'Market comparable sales analysis',
        'Professional appraisal report',
        'Project overview and timeline'
    ]

    if owner_type == 'OPERATING_BUSINESS':
        supporting_evidence.append('Relocation assistance plan')
        supporting_evidence.append('Business transition timeline options')

    if sophistication == 'HIGH':
        supporting_evidence.append('Detailed valuation methodology')
        supporting_evidence.append('Hearing cost analysis (BATNA)')

    return {
        'recommended_opening': round(recommended_opening, 0),
        'opening_as_pct_of_target': round(opening_pct, 3),
        'rationale': rationale,
        'negotiation_room': round(negotiation_room, 0),
        'negotiation_room_pct': round((negotiation_room / target) * 100, 1) if target > 0 else 0,
        'messaging': messaging,
        'supporting_evidence': supporting_evidence,
        'adjustments': {
            'base_risk_adjustment': risk_level,
            'owner_type_adjustment': owner_type,
            'timeline_adjustment': timeline,
            'sophistication_adjustment': sophistication
        }
    }


def generate_concession_plan(
    opening_offer: float,
    target: float,
    risk_level: str
) -> List[Dict]:
    """
    Generate concession plan from opening to target.

    Uses diminishing concessions (50%, 25%, 12.5% pattern) from Shared_Utils.

    Adjusts number of rounds based on risk level:
    - HIGH/CRITICAL: More rounds (slower pace)
    - MEDIUM: Standard 3-4 rounds
    - LOW: Fewer rounds (faster pace)

    Args:
        opening_offer: Opening offer amount
        target: Target settlement amount
        risk_level: Holdout risk level (LOW/MEDIUM/HIGH/CRITICAL)

    Returns:
        List of concession rounds with tactical notes
    """
    # Determine number of rounds based on risk
    if risk_level in ['CRITICAL', 'HIGH']:
        num_rounds = 4  # More rounds for difficult negotiations
    elif risk_level == 'MEDIUM':
        num_rounds = 3  # Standard
    else:  # LOW
        num_rounds = 2  # Faster pace

    # Use shared utility function
    concession_rounds = calculate_concession_strategy(
        opening_offer,
        target,
        num_rounds
    )

    # Add tactical notes to each round
    for i, round_data in enumerate(concession_rounds):
        if i == 0:
            round_data['tactical_note'] = 'Anchor with market evidence. Set collaborative tone.'
            round_data['technique'] = 'Evidence-based anchoring + Accusation audit if appropriate'

        elif i == 1:
            round_data['tactical_note'] = 'First meaningful concession. Shows good faith movement.'
            round_data['technique'] = 'Calibrated questions to understand constraints'

        elif i == 2:
            round_data['tactical_note'] = 'Substantial progress shown. Slow pace of concessions.'
            round_data['technique'] = 'Labeling + Mirroring to build rapport'

        elif i == 3:
            round_data['tactical_note'] = 'Small concession signals approaching limit.'
            round_data['technique'] = 'No-oriented questions to test flexibility'

        else:
            round_data['tactical_note'] = 'Final position. Emphasize BATNA if needed.'
            round_data['technique'] = 'Professional firmness + Value creation through structure'

    # Add overall strategy note
    strategy_note = {
        'CRITICAL': 'Patient approach with many small concessions. Build trust through consistency.',
        'HIGH': 'Deliberate pace. Make them work for each concession.',
        'MEDIUM': 'Balanced approach. Show movement but maintain discipline.',
        'LOW': 'Efficient pace. Fewer rounds but clear progression to close.'
    }

    # Don't insert metadata as list item - just return the rounds
    # Caller can access metadata separately if needed
    return concession_rounds


def identify_leverage_points(
    data: Dict,
    batna: Dict,
    zopa: Dict,
    owner_analysis: Dict,
    context: Dict
) -> Dict:
    """
    Identify negotiation leverage points for buyer and owner.

    Leverage factors:
    - BATNA strength
    - Timeline pressure
    - Market conditions
    - Owner alternatives
    - Project visibility
    - Legal/procedural advantages

    Args:
        data: Full input data
        batna: BATNA analysis
        zopa: ZOPA analysis
        owner_analysis: Owner psychology analysis
        context: Negotiation context

    Returns:
        Dict with leverage analysis
            {
                'buyer_advantages': [...],
                'owner_advantages': [...],
                'neutral_factors': [...],
                'leverage_balance': 'BUYER_FAVORED',
                'key_leverage_point': '...',
                'recommended_emphasis': [...]
            }
    """
    buyer_advantages = []
    owner_advantages = []
    neutral_factors = []

    owner_profile = data.get('owner_profile', {})
    project_context = data.get('project_context', {})
    market_conditions = data.get('market_conditions', {})

    # Analyze BATNA strength
    net_batna = batna.get('net_batna', 0)
    seller_min = data.get('valuation', {}).get('seller_minimum', 0)

    if seller_min > 0 and net_batna < seller_min * 1.1:
        buyer_advantages.append(f'Strong BATNA position - hearing costs only {((net_batna/seller_min - 1) * 100):.1f}% above seller minimum')
    elif seller_min > 0 and net_batna > seller_min * 1.3:
        owner_advantages.append('Weak buyer BATNA - hearing costs significantly exceed seller expectations')
    else:
        neutral_factors.append('BATNA provides moderate negotiating room')

    # Timeline pressure
    timeline = context.get('timeline_pressure', 'medium')
    owner_timeline = owner_profile.get('alternatives', {}).get('timeline_pressure', 'medium')

    if timeline in ['high', 'critical'] and owner_timeline == 'low':
        owner_advantages.append('Buyer has timeline pressure while owner can wait')
    elif timeline == 'low' and owner_timeline in ['high', 'critical']:
        buyer_advantages.append('Owner has timeline pressure while buyer is flexible')
    else:
        neutral_factors.append('Timeline pressures are balanced')

    # Financial pressure
    financial_need = owner_profile.get('motivation', {}).get('financial_need', 'medium')

    if financial_need == 'high':
        buyer_advantages.append('Owner has high financial need - motivated to settle')
    elif financial_need == 'low':
        owner_advantages.append('Owner has low financial pressure - can afford to wait')

    # Alternatives
    relocation_options = owner_profile.get('alternatives', {}).get('relocation_options', 'some')

    if relocation_options in ['limited', 'none']:
        owner_advantages.append('Limited relocation options increase owner resistance')
    elif relocation_options == 'many':
        buyer_advantages.append('Many relocation alternatives reduce owner leverage')

    # Sophistication
    sophistication = owner_analysis.get('sophistication_level', 'MEDIUM')

    if sophistication == 'HIGH':
        owner_advantages.append('Sophisticated owner with process knowledge and legal counsel')
    elif sophistication == 'LOW':
        buyer_advantages.append('Less sophisticated owner may be more receptive to settlement')

    # Market conditions
    market_trend = market_conditions.get('market_trend', 'stable')

    if market_trend == 'rising':
        owner_advantages.append('Rising market favors waiting for appreciation')
    elif market_trend == 'declining':
        buyer_advantages.append('Declining market creates urgency to sell')
    else:
        neutral_factors.append('Stable market conditions')

    # Business impact
    business_impact = owner_profile.get('motivation', {}).get('business_impact', 'moderate')

    if business_impact == 'critical':
        owner_advantages.append('Critical business impact increases compensation pressure')
    elif business_impact == 'minimal':
        buyer_advantages.append('Minimal business disruption reduces additional claims')

    # Project type leverage
    project_type = project_context.get('project_type', 'transit')
    political_sensitivity = project_context.get('political_sensitivity', 'medium')

    if political_sensitivity == 'high':
        owner_advantages.append('High political visibility limits aggressive tactics')
    elif political_sensitivity == 'low':
        buyer_advantages.append('Low political pressure allows firmer negotiating stance')

    # Calculate leverage balance
    buyer_score = len(buyer_advantages)
    owner_score = len(owner_advantages)

    if buyer_score > owner_score + 2:
        leverage_balance = 'STRONGLY_BUYER_FAVORED'
    elif buyer_score > owner_score:
        leverage_balance = 'BUYER_FAVORED'
    elif owner_score > buyer_score + 2:
        leverage_balance = 'STRONGLY_OWNER_FAVORED'
    elif owner_score > buyer_score:
        leverage_balance = 'OWNER_FAVORED'
    else:
        leverage_balance = 'BALANCED'

    # Identify key leverage point
    if buyer_advantages:
        key_leverage_point = buyer_advantages[0]
        recommended_emphasis = [
            'Lead with strongest leverage point in opening presentation',
            'Use calibrated questions to make owner acknowledge constraints',
            'Present BATNA analysis clearly if it favors buyer'
        ]
    else:
        key_leverage_point = 'Focus on value creation rather than leverage'
        recommended_emphasis = [
            'Emphasize collaborative problem-solving',
            'Create value through transition support and flexibility',
            'Build relationship capital for smoother negotiation'
        ]

    return {
        'buyer_advantages': buyer_advantages,
        'owner_advantages': owner_advantages,
        'neutral_factors': neutral_factors,
        'leverage_balance': leverage_balance,
        'leverage_score': {
            'buyer': buyer_score,
            'owner': owner_score,
            'differential': buyer_score - owner_score
        },
        'key_leverage_point': key_leverage_point,
        'recommended_emphasis': recommended_emphasis
    }
