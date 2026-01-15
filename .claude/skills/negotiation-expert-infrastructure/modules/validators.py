#!/usr/bin/env python3
"""
Input Validation Module for Negotiation Settlement Calculator
Validates input data structure and values before calculations
"""

from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def validate_input_data(data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate negotiation settlement input data.

    Args:
        data: Input dictionary with negotiation parameters

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Required fields
    required_fields = ['buyer_max', 'seller_min', 'hearing_probabilities', 'hearing_costs']
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    if errors:
        return False, errors

    # Validate buyer_max and seller_min
    buyer_max = data.get('buyer_max')
    seller_min = data.get('seller_min')

    if not isinstance(buyer_max, (int, float)) or buyer_max <= 0:
        errors.append(f"buyer_max must be a positive number, got: {buyer_max}")

    if not isinstance(seller_min, (int, float)) or seller_min <= 0:
        errors.append(f"seller_min must be a positive number, got: {seller_min}")

    # Validate hearing_probabilities
    hearing_prob = data.get('hearing_probabilities', {})
    required_outcomes = ['low_award', 'mid_award', 'high_award']

    for outcome in required_outcomes:
        if outcome not in hearing_prob:
            errors.append(f"Missing hearing probability: {outcome}")
        elif not isinstance(hearing_prob[outcome], (int, float)):
            errors.append(f"hearing_probabilities.{outcome} must be a number")
        elif not 0 <= hearing_prob[outcome] <= 1:
            errors.append(f"hearing_probabilities.{outcome} must be between 0 and 1")

    # Check probabilities sum to 1.0
    if hearing_prob:
        total_prob = sum(hearing_prob.get(o, 0) for o in required_outcomes)
        if abs(total_prob - 1.0) > 0.01:
            errors.append(f"hearing_probabilities must sum to 1.0, got: {total_prob:.3f}")

    # Validate hearing_costs
    hearing_costs = data.get('hearing_costs', {})
    required_costs = ['low_award_amount', 'mid_award_amount', 'high_award_amount',
                     'legal_fees', 'expert_fees', 'time_cost']

    for cost in required_costs:
        if cost not in hearing_costs:
            errors.append(f"Missing hearing cost: {cost}")
        elif not isinstance(hearing_costs[cost], (int, float)):
            errors.append(f"hearing_costs.{cost} must be a number")
        elif hearing_costs[cost] < 0:
            errors.append(f"hearing_costs.{cost} cannot be negative")

    # Validate award amounts are ordered
    if not errors:
        low = hearing_costs.get('low_award_amount', 0)
        mid = hearing_costs.get('mid_award_amount', 0)
        high = hearing_costs.get('high_award_amount', 0)

        if not (low <= mid <= high):
            errors.append(f"Award amounts must be ordered: low <= mid <= high (got: {low}, {mid}, {high})")

    # Validate owner_profile (optional)
    if 'owner_profile' in data:
        owner_errors = _validate_owner_profile(data['owner_profile'])
        errors.extend(owner_errors)

    # Validate settlement_offer (optional)
    if 'settlement_offer' in data:
        settlement = data['settlement_offer']
        if not isinstance(settlement, (int, float)) or settlement <= 0:
            errors.append(f"settlement_offer must be a positive number, got: {settlement}")

    # Validate confidence_level (optional)
    if 'confidence_level' in data:
        conf = data['confidence_level']
        if not isinstance(conf, (int, float)) or not 0 < conf <= 1:
            errors.append(f"confidence_level must be between 0 and 1, got: {conf}")

    is_valid = len(errors) == 0
    return is_valid, errors


def _validate_owner_profile(profile: Dict) -> List[str]:
    """Validate owner_profile structure."""
    errors = []

    if not isinstance(profile, dict):
        errors.append("owner_profile must be a dictionary")
        return errors

    # Validate motivation
    if 'motivation' in profile:
        motivation = profile['motivation']
        if not isinstance(motivation, dict):
            errors.append("owner_profile.motivation must be a dictionary")
        else:
            valid_levels = ['low', 'medium', 'high']

            if 'financial_need' in motivation:
                if motivation['financial_need'] not in valid_levels:
                    errors.append(f"motivation.financial_need must be one of {valid_levels}")

            if 'emotional_attachment' in motivation:
                if motivation['emotional_attachment'] not in valid_levels:
                    errors.append(f"motivation.emotional_attachment must be one of {valid_levels}")

            if 'business_impact' in motivation:
                valid_impacts = ['minimal', 'moderate', 'critical']
                if motivation['business_impact'] not in valid_impacts:
                    errors.append(f"motivation.business_impact must be one of {valid_impacts}")

    # Validate sophistication
    if 'sophistication' in profile:
        soph = profile['sophistication']
        if not isinstance(soph, dict):
            errors.append("owner_profile.sophistication must be a dictionary")
        else:
            if 'real_estate_experience' in soph:
                valid_levels = ['low', 'medium', 'high']
                if soph['real_estate_experience'] not in valid_levels:
                    errors.append(f"sophistication.real_estate_experience must be one of {valid_levels}")

            if 'legal_representation' in soph:
                if not isinstance(soph['legal_representation'], bool):
                    errors.append("sophistication.legal_representation must be boolean")

            if 'previous_negotiations' in soph:
                if not isinstance(soph['previous_negotiations'], int) or soph['previous_negotiations'] < 0:
                    errors.append("sophistication.previous_negotiations must be non-negative integer")

    # Validate alternatives
    if 'alternatives' in profile:
        alt = profile['alternatives']
        if not isinstance(alt, dict):
            errors.append("owner_profile.alternatives must be a dictionary")
        else:
            if 'relocation_options' in alt:
                valid_options = ['many', 'some', 'limited', 'none']
                if alt['relocation_options'] not in valid_options:
                    errors.append(f"alternatives.relocation_options must be one of {valid_options}")

            if 'financial_flexibility' in alt:
                valid_levels = ['low', 'medium', 'high']
                if alt['financial_flexibility'] not in valid_levels:
                    errors.append(f"alternatives.financial_flexibility must be one of {valid_levels}")

            if 'timeline_pressure' in alt:
                valid_levels = ['low', 'medium', 'high']
                if alt['timeline_pressure'] not in valid_levels:
                    errors.append(f"alternatives.timeline_pressure must be one of {valid_levels}")

    return errors


def validate_scenario_probabilities(scenarios: List[Dict]) -> Tuple[bool, List[str]]:
    """
    Validate scenario probability data.

    Args:
        scenarios: List of scenario dictionaries

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    if not isinstance(scenarios, list):
        errors.append("scenarios must be a list")
        return False, errors

    if len(scenarios) == 0:
        errors.append("scenarios list cannot be empty")
        return False, errors

    total_prob = 0.0

    for idx, scenario in enumerate(scenarios):
        if not isinstance(scenario, dict):
            errors.append(f"Scenario {idx} must be a dictionary")
            continue

        # Required fields
        if 'name' not in scenario:
            errors.append(f"Scenario {idx} missing 'name' field")

        if 'cost' not in scenario:
            errors.append(f"Scenario {idx} missing 'cost' field")
        elif not isinstance(scenario['cost'], (int, float)):
            errors.append(f"Scenario {idx} 'cost' must be a number")
        elif scenario['cost'] < 0:
            errors.append(f"Scenario {idx} 'cost' cannot be negative")

        if 'probability' not in scenario:
            errors.append(f"Scenario {idx} missing 'probability' field")
        elif not isinstance(scenario['probability'], (int, float)):
            errors.append(f"Scenario {idx} 'probability' must be a number")
        elif not 0 <= scenario['probability'] <= 1:
            errors.append(f"Scenario {idx} 'probability' must be between 0 and 1")
        else:
            total_prob += scenario['probability']

    # Check probabilities sum to 1.0
    if not errors and abs(total_prob - 1.0) > 0.01:
        errors.append(f"Scenario probabilities must sum to 1.0, got: {total_prob:.3f}")

    is_valid = len(errors) == 0
    return is_valid, errors
