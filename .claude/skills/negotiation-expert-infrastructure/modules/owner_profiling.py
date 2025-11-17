#!/usr/bin/env python3
"""
Owner Psychology Profiling Module

Analyzes owner characteristics to develop communication and negotiation strategies.

Functions:
- analyze_owner_psychology(): Classify owner type and motivations
- recommend_communication_strategy(): Tailor approach to owner psychology
- predict_negotiation_behavior(): Anticipate owner responses
"""

from typing import Dict, List


def analyze_owner_psychology(owner_profile: Dict) -> Dict:
    """
    Analyze owner psychology to classify owner type and identify key motivations.

    Owner Types:
    - RATIONAL_INVESTOR: Business decision, minimal emotion
    - LEGACY_HOLDER: Multi-generational, high emotional attachment
    - OPERATING_BUSINESS: Property critical to operations
    - FINANCIAL_DISTRESS: Motivated seller, cash constraints
    - SOPHISTICATED_HOLDOUT: Experienced, knows process, strategic

    Args:
        owner_profile: Dict with owner characteristics
            {
                'ownership_duration_years': 25,
                'motivation': {
                    'financial_need': 'low',
                    'emotional_attachment': 'high',
                    'business_impact': 'moderate'
                },
                'sophistication': {
                    'real_estate_experience': 'medium',
                    'legal_representation': True,
                    'previous_negotiations': 2
                },
                'alternatives': {
                    'relocation_options': 'limited',
                    'financial_flexibility': 'high',
                    'timeline_pressure': 'low'
                }
            }

    Returns:
        Dict containing owner analysis
            {
                'owner_type': 'LEGACY_HOLDER',
                'sophistication_level': 'MEDIUM',
                'primary_motivation': 'Preserve family legacy',
                'secondary_motivations': [...],
                'negotiation_style': 'Collaborative but resistant',
                'key_concerns': [...],
                'decision_factors': {...}
            }
    """
    motivation = owner_profile.get('motivation', {})
    sophistication = owner_profile.get('sophistication', {})
    alternatives = owner_profile.get('alternatives', {})
    ownership_years = owner_profile.get('ownership_duration_years', 0)

    # Classify owner type
    financial_need = motivation.get('financial_need', 'medium')
    emotional_attachment = motivation.get('emotional_attachment', 'medium')
    business_impact = motivation.get('business_impact', 'moderate')
    experience = sophistication.get('real_estate_experience', 'medium')

    # Decision matrix
    if financial_need == 'high':
        owner_type = 'FINANCIAL_DISTRESS'
        primary_motivation = 'Need liquidity quickly'
        negotiation_style = 'Cooperative but desperate'

    elif business_impact == 'critical':
        owner_type = 'OPERATING_BUSINESS'
        primary_motivation = 'Protect business continuity'
        negotiation_style = 'Resistant but pragmatic'

    elif ownership_years >= 20 and emotional_attachment == 'high':
        owner_type = 'LEGACY_HOLDER'
        primary_motivation = 'Preserve family legacy and fair treatment'
        negotiation_style = 'Principled and relationship-focused'

    elif experience == 'high' and sophistication.get('legal_representation', False):
        owner_type = 'SOPHISTICATED_HOLDOUT'
        primary_motivation = 'Maximize value through process knowledge'
        negotiation_style = 'Strategic and analytical'

    else:
        owner_type = 'RATIONAL_INVESTOR'
        primary_motivation = 'Maximize financial outcome'
        negotiation_style = 'Professional and data-driven'

    # Sophistication level
    if experience == 'high' and sophistication.get('previous_negotiations', 0) >= 3:
        sophistication_level = 'HIGH'
    elif experience == 'medium' or sophistication.get('legal_representation', False):
        sophistication_level = 'MEDIUM'
    else:
        sophistication_level = 'LOW'

    # Identify key concerns
    key_concerns = []

    if emotional_attachment == 'high':
        key_concerns.append('Fair and respectful treatment')
        key_concerns.append('Recognition of non-financial value')

    if business_impact in ['moderate', 'critical']:
        key_concerns.append('Business relocation and continuity')
        key_concerns.append('Timeline for transition')

    if financial_need == 'high':
        key_concerns.append('Quick payment and certainty')
    elif financial_need == 'low' and alternatives.get('financial_flexibility') == 'high':
        key_concerns.append('Maximum compensation value')

    if alternatives.get('relocation_options') in ['limited', 'none']:
        key_concerns.append('Assistance finding suitable replacement property')

    if sophistication_level == 'HIGH':
        key_concerns.append('Process fairness and legal rights')

    # Secondary motivations
    secondary_motivations = []

    if financial_need == 'medium':
        secondary_motivations.append('Fair market compensation')

    if alternatives.get('timeline_pressure') == 'high':
        secondary_motivations.append('Fast resolution')
    elif alternatives.get('timeline_pressure') == 'low':
        secondary_motivations.append('Time to evaluate options')

    if ownership_years >= 10:
        secondary_motivations.append('Respect for property history')

    # Decision factors
    decision_factors = {
        'price_sensitivity': 'HIGH' if financial_need in ['medium', 'high'] else 'MODERATE',
        'timeline_sensitivity': alternatives.get('timeline_pressure', 'medium').upper(),
        'relationship_importance': 'HIGH' if owner_type == 'LEGACY_HOLDER' else 'MODERATE',
        'process_knowledge': sophistication_level,
        'legal_orientation': 'HIGH' if sophistication.get('legal_representation', False) else 'MODERATE'
    }

    return {
        'owner_type': owner_type,
        'sophistication_level': sophistication_level,
        'primary_motivation': primary_motivation,
        'secondary_motivations': secondary_motivations,
        'negotiation_style': negotiation_style,
        'key_concerns': key_concerns,
        'decision_factors': decision_factors,
        'ownership_duration_years': ownership_years
    }


def recommend_communication_strategy(owner_analysis: Dict) -> Dict:
    """
    Recommend communication approach based on owner psychology.

    Tailors:
    - Primary communication channel
    - Tone and style
    - Key messages
    - Rapport-building tactics
    - Evidence presentation

    Args:
        owner_analysis: Output from analyze_owner_psychology()

    Returns:
        Dict with communication recommendations
            {
                'primary_approach': 'relationship_first',
                'tone': 'respectful_empathetic',
                'key_messages': [...],
                'rapport_tactics': [...],
                'evidence_style': 'conversational',
                'meeting_structure': {...}
            }
    """
    owner_type = owner_analysis.get('owner_type', 'RATIONAL_INVESTOR')
    sophistication = owner_analysis.get('sophistication_level', 'MEDIUM')
    key_concerns = owner_analysis.get('key_concerns', [])

    strategy = {
        'primary_approach': None,
        'tone': None,
        'key_messages': [],
        'rapport_tactics': [],
        'evidence_style': None,
        'meeting_structure': {},
        'negotiation_techniques': []
    }

    # Tailor by owner type
    if owner_type == 'LEGACY_HOLDER':
        strategy['primary_approach'] = 'relationship_first'
        strategy['tone'] = 'respectful_empathetic'
        strategy['key_messages'] = [
            'Acknowledge property history and family significance',
            'Emphasize fair process and treatment',
            'Commit to respectful transition timeline',
            'Offer relocation assistance and support'
        ]
        strategy['rapport_tactics'] = [
            'Use accusation audit to show understanding of attachment',
            'Label emotions: "It seems like this property has deep family history..."',
            'Ask about property story before discussing numbers',
            'Build trust through transparency and patience'
        ]
        strategy['evidence_style'] = 'conversational'
        strategy['meeting_structure'] = {
            'pace': 'slow',
            'relationship_building_time': '40% of first meeting',
            'recommended_meetings': 3
        }
        strategy['negotiation_techniques'] = [
            'Accusation audit',
            'Labeling',
            'Tactical empathy',
            'Collaborative problem-solving'
        ]

    elif owner_type == 'OPERATING_BUSINESS':
        strategy['primary_approach'] = 'problem_solving'
        strategy['tone'] = 'professional_pragmatic'
        strategy['key_messages'] = [
            'Understand business continuity concerns',
            'Flexible transition timeline options',
            'Relocation and operational support available',
            'Minimize business disruption'
        ]
        strategy['rapport_tactics'] = [
            'Focus on operational needs first',
            'Ask calibrated questions: "What would make the transition work for your operations?"',
            'Propose creative solutions (phased moves, temp facilities)',
            'Show expertise in business relocations'
        ]
        strategy['evidence_style'] = 'practical'
        strategy['meeting_structure'] = {
            'pace': 'moderate',
            'focus': 'solutions_oriented',
            'recommended_meetings': 2
        }
        strategy['negotiation_techniques'] = [
            'Calibrated questions',
            'Value creation',
            'Options and alternatives',
            'Mirroring to understand constraints'
        ]

    elif owner_type == 'SOPHISTICATED_HOLDOUT':
        strategy['primary_approach'] = 'evidence_based_professional'
        strategy['tone'] = 'professional_analytical'
        strategy['key_messages'] = [
            'Transparent process and fair market analysis',
            'Comprehensive comparable data',
            'Clear legal framework and rights',
            'Mutually beneficial settlement'
        ]
        strategy['rapport_tactics'] = [
            'Respect their knowledge and process understanding',
            'Present strong market evidence upfront',
            'Be direct about BATNA and alternatives',
            'Engage on analytical/legal level'
        ]
        strategy['evidence_style'] = 'detailed_analytical'
        strategy['meeting_structure'] = {
            'pace': 'efficient',
            'focus': 'data_driven',
            'recommended_meetings': 2
        }
        strategy['negotiation_techniques'] = [
            'Evidence-based anchoring',
            'Calibrated questions',
            'No-oriented questions',
            'Professional directness'
        ]

    elif owner_type == 'FINANCIAL_DISTRESS':
        strategy['primary_approach'] = 'expedited_supportive'
        strategy['tone'] = 'supportive_solution_focused'
        strategy['key_messages'] = [
            'Quick settlement timeline available',
            'Fair compensation with fast payment',
            'Support services for transition',
            'Certainty vs hearing risk and delay'
        ]
        strategy['rapport_tactics'] = [
            'Acknowledge time pressure without exploiting',
            'Offer payment structure options',
            'Emphasize certainty and speed benefits',
            'Provide resources and referrals'
        ]
        strategy['evidence_style'] = 'straightforward'
        strategy['meeting_structure'] = {
            'pace': 'fast',
            'focus': 'settlement_benefits',
            'recommended_meetings': 1
        }
        strategy['negotiation_techniques'] = [
            'Emphasize BATNA costs and delays',
            'Offer structured payments if needed',
            'Fast timeline as value',
            'Certainty vs uncertainty framing'
        ]

    else:  # RATIONAL_INVESTOR
        strategy['primary_approach'] = 'market_evidence_based'
        strategy['tone'] = 'professional_businesslike'
        strategy['key_messages'] = [
            'Fair market value based on comparables',
            'Transparent valuation methodology',
            'Efficient negotiation process',
            'Settlement benefits vs hearing costs'
        ]
        strategy['rapport_tactics'] = [
            'Lead with strong market data',
            'Anchor with comparable evidence',
            'Appeal to business logic',
            'Clear cost-benefit analysis'
        ]
        strategy['evidence_style'] = 'data_driven'
        strategy['meeting_structure'] = {
            'pace': 'moderate',
            'focus': 'value_analysis',
            'recommended_meetings': 2
        }
        strategy['negotiation_techniques'] = [
            'Evidence-based anchoring',
            'Calibrated questions',
            'Cost-benefit framing',
            'Professional efficiency'
        ]

    # Add sophistication-specific adjustments
    if sophistication == 'HIGH':
        strategy['key_messages'].append('Respect for process knowledge and legal rights')
        strategy['evidence_style'] = 'detailed_analytical'

    if sophistication == 'LOW':
        strategy['key_messages'].append('Clear explanation of process and rights')
        strategy['rapport_tactics'].append('Educational approach to build trust')

    # Address specific concerns
    for concern in key_concerns:
        if 'relocation' in concern.lower():
            strategy['rapport_tactics'].append('Offer comprehensive relocation support')
        if 'fair' in concern.lower() or 'respect' in concern.lower():
            strategy['rapport_tactics'].append('Emphasize process fairness and transparency')

    return strategy


def predict_negotiation_behavior(owner_analysis: Dict, offer_scenario: Dict) -> Dict:
    """
    Predict owner response to offer scenarios.

    Args:
        owner_analysis: Output from analyze_owner_psychology()
        offer_scenario: Dict with offer details
            {
                'offer_amount': 250000,
                'market_value': 280000,
                'seller_minimum': 270000,
                'offer_as_pct_of_minimum': 92.6
            }

    Returns:
        Dict with predicted responses
            {
                'likely_response': 'COUNTEROFFER',
                'probability_accept': 0.2,
                'probability_counter': 0.6,
                'probability_reject': 0.2,
                'predicted_counter': 275000,
                'reasoning': [...],
                'recommended_next_move': '...'
            }
    """
    owner_type = owner_analysis.get('owner_type', 'RATIONAL_INVESTOR')
    sophistication = owner_analysis.get('sophistication_level', 'MEDIUM')
    decision_factors = owner_analysis.get('decision_factors', {})

    offer_amount = offer_scenario.get('offer_amount', 0)
    seller_minimum = offer_scenario.get('seller_minimum', 0)
    market_value = offer_scenario.get('market_value', 0)

    # Calculate offer position
    if seller_minimum > 0:
        offer_pct = (offer_amount / seller_minimum) * 100
    else:
        offer_pct = 100

    # Predict response based on offer level and owner type
    if offer_pct >= 100:  # At or above minimum
        probability_accept = 0.7
        probability_counter = 0.2
        probability_reject = 0.1
        likely_response = 'ACCEPT'
        predicted_counter = offer_amount * 1.05  # Small increase

    elif offer_pct >= 90:  # 90-100% of minimum
        if owner_type == 'FINANCIAL_DISTRESS':
            probability_accept = 0.5
            probability_counter = 0.4
            probability_reject = 0.1
        elif owner_type == 'SOPHISTICATED_HOLDOUT':
            probability_accept = 0.2
            probability_counter = 0.7
            probability_reject = 0.1
        else:
            probability_accept = 0.3
            probability_counter = 0.6
            probability_reject = 0.1

        likely_response = 'COUNTEROFFER'
        predicted_counter = (offer_amount + seller_minimum) / 2

    elif offer_pct >= 75:  # 75-90% of minimum
        if owner_type == 'FINANCIAL_DISTRESS':
            probability_accept = 0.2
            probability_counter = 0.7
            probability_reject = 0.1
        elif owner_type == 'SOPHISTICATED_HOLDOUT':
            probability_accept = 0.05
            probability_counter = 0.6
            probability_reject = 0.35
        else:
            probability_accept = 0.1
            probability_counter = 0.7
            probability_reject = 0.2

        likely_response = 'COUNTEROFFER'
        predicted_counter = seller_minimum

    else:  # Below 75% of minimum
        probability_accept = 0.05
        probability_counter = 0.4
        probability_reject = 0.55
        likely_response = 'REJECT'
        predicted_counter = market_value

    # Adjust for sophistication
    if sophistication == 'HIGH':
        probability_counter += 0.1
        probability_reject += 0.05
        probability_accept -= 0.15

    # Build reasoning
    reasoning = []
    reasoning.append(f"Offer is {offer_pct:.1f}% of seller's minimum")
    reasoning.append(f"Owner type: {owner_type}")
    reasoning.append(f"Sophistication: {sophistication}")

    if decision_factors.get('price_sensitivity') == 'HIGH':
        reasoning.append("High price sensitivity - more likely to negotiate")

    if decision_factors.get('timeline_sensitivity') == 'HIGH':
        reasoning.append("Timeline pressure - may accept lower offer")
        probability_accept += 0.1

    if decision_factors.get('process_knowledge') == 'HIGH':
        reasoning.append("Process knowledge - will use BATNA leverage")

    # Recommended next move
    if likely_response == 'ACCEPT':
        next_move = 'Prepare to close quickly with minimal additional negotiation'
    elif likely_response == 'COUNTEROFFER':
        next_move = f'Prepare for counter around ${predicted_counter:,.0f}. Have second offer ready at higher amount with supporting evidence.'
    else:  # REJECT
        next_move = 'Be prepared to justify offer with market evidence or increase substantially. Consider if relationship damaged.'

    return {
        'likely_response': likely_response,
        'probability_accept': round(probability_accept, 2),
        'probability_counter': round(probability_counter, 2),
        'probability_reject': round(probability_reject, 2),
        'predicted_counter': round(predicted_counter, 0),
        'reasoning': reasoning,
        'recommended_next_move': next_move
    }
