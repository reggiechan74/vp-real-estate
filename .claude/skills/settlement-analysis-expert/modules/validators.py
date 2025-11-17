#!/usr/bin/env python3
"""
Input validation for settlement analysis calculator.
Validates JSON inputs against schema and business rules.
"""

from typing import Dict, List, Tuple
import json


def validate_input(data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate settlement analysis input data.

    Args:
        data: Input data dictionary

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Required fields
    required_fields = ['case_id', 'settlement_offer', 'hearing_probabilities', 'hearing_costs']
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    if errors:
        return False, errors

    # Validate settlement amounts
    settlement_offer = data.get('settlement_offer', 0)
    if settlement_offer <= 0:
        errors.append("settlement_offer must be greater than 0")

    counteroffer = data.get('counteroffer')
    if counteroffer is not None and counteroffer <= 0:
        errors.append("counteroffer must be greater than 0")

    buyer_max = data.get('buyer_max_settlement')
    if buyer_max is not None and buyer_max <= 0:
        errors.append("buyer_max_settlement must be greater than 0")

    # Validate probabilities
    prob_valid, prob_errors = validate_probabilities(data.get('hearing_probabilities', {}))
    if not prob_valid:
        errors.extend(prob_errors)

    # Validate hearing costs
    hearing_costs = data.get('hearing_costs', {})
    required_cost_fields = ['low_award_amount', 'mid_award_amount', 'high_award_amount',
                            'legal_fees', 'expert_fees']
    for field in required_cost_fields:
        if field not in hearing_costs:
            errors.append(f"Missing required hearing_costs field: {field}")
        elif hearing_costs[field] < 0:
            errors.append(f"{field} cannot be negative")

    # Validate award amounts are in ascending order
    if all(f in hearing_costs for f in ['low_award_amount', 'mid_award_amount', 'high_award_amount']):
        low = hearing_costs['low_award_amount']
        mid = hearing_costs['mid_award_amount']
        high = hearing_costs['high_award_amount']

        if not (low <= mid <= high):
            errors.append("Award amounts must be in ascending order: low <= mid <= high")

    # Validate owner profile if provided
    if 'owner_profile' in data:
        owner_valid, owner_errors = validate_owner_profile(data['owner_profile'])
        if not owner_valid:
            errors.extend(owner_errors)

    # Validate case factors if provided
    if 'case_factors' in data:
        case_valid, case_errors = validate_case_factors(data['case_factors'])
        if not case_valid:
            errors.extend(case_errors)

    # Validate discount rate if provided
    discount_rate = data.get('discount_rate')
    if discount_rate is not None:
        if discount_rate < 0 or discount_rate > 1:
            errors.append("discount_rate must be between 0 and 1")

    return len(errors) == 0, errors


def validate_probabilities(probabilities: Dict) -> Tuple[bool, List[str]]:
    """
    Validate probability distribution.

    Args:
        probabilities: Dict with low_award, mid_award, high_award probabilities

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Check required fields
    required = ['low_award', 'mid_award', 'high_award']
    for field in required:
        if field not in probabilities:
            errors.append(f"Missing probability field: {field}")
            return False, errors

    # Validate each probability
    for field in required:
        prob = probabilities[field]
        if not isinstance(prob, (int, float)):
            errors.append(f"{field} must be a number")
        elif prob < 0 or prob > 1:
            errors.append(f"{field} must be between 0 and 1, got {prob}")

    # Validate probabilities sum to 1.0
    total = sum(probabilities[field] for field in required)
    if abs(total - 1.0) > 0.01:
        errors.append(f"Probabilities must sum to 1.0, got {total:.3f}")

    return len(errors) == 0, errors


def validate_owner_profile(profile: Dict) -> Tuple[bool, List[str]]:
    """
    Validate owner profile data.

    Args:
        profile: Owner profile dictionary

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Valid enum values
    valid_enums = {
        'financial_need': ['low', 'medium', 'high'],
        'emotional_attachment': ['low', 'medium', 'high'],
        'business_impact': ['minimal', 'moderate', 'critical'],
        'real_estate_experience': ['low', 'medium', 'high'],
        'relocation_options': ['many', 'some', 'limited', 'none'],
        'financial_flexibility': ['low', 'medium', 'high'],
        'timeline_pressure': ['low', 'medium', 'high']
    }

    # Validate motivation fields
    if 'motivation' in profile:
        motivation = profile['motivation']
        for field in ['financial_need', 'emotional_attachment', 'business_impact']:
            if field in motivation:
                if motivation[field] not in valid_enums[field]:
                    errors.append(f"Invalid {field}: must be one of {valid_enums[field]}")

    # Validate sophistication fields
    if 'sophistication' in profile:
        sophistication = profile['sophistication']

        if 'real_estate_experience' in sophistication:
            if sophistication['real_estate_experience'] not in valid_enums['real_estate_experience']:
                errors.append(f"Invalid real_estate_experience: must be one of {valid_enums['real_estate_experience']}")

        if 'legal_representation' in sophistication:
            if not isinstance(sophistication['legal_representation'], bool):
                errors.append("legal_representation must be a boolean")

        if 'previous_negotiations' in sophistication:
            if not isinstance(sophistication['previous_negotiations'], int) or sophistication['previous_negotiations'] < 0:
                errors.append("previous_negotiations must be a non-negative integer")

    # Validate alternatives fields
    if 'alternatives' in profile:
        alternatives = profile['alternatives']
        for field in ['relocation_options', 'financial_flexibility', 'timeline_pressure']:
            if field in alternatives:
                if alternatives[field] not in valid_enums[field]:
                    errors.append(f"Invalid {field}: must be one of {valid_enums[field]}")

    return len(errors) == 0, errors


def validate_case_factors(factors: Dict) -> Tuple[bool, List[str]]:
    """
    Validate case factors data.

    Args:
        factors: Case factors dictionary

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Validate numeric fields
    if 'valuation_gap' in factors:
        if factors['valuation_gap'] < 0:
            errors.append("valuation_gap cannot be negative")

    if 'property_value' in factors:
        if factors['property_value'] < 0:
            errors.append("property_value cannot be negative")

    # Validate enum fields
    if 'owner_risk_profile' in factors:
        if factors['owner_risk_profile'] not in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']:
            errors.append("owner_risk_profile must be LOW, MEDIUM, HIGH, or CRITICAL")

    if 'legal_complexity' in factors:
        if factors['legal_complexity'] not in ['low', 'medium', 'high']:
            errors.append("legal_complexity must be low, medium, or high")

    if 'precedent_clarity' in factors:
        if factors['precedent_clarity'] not in ['clear', 'mixed', 'unclear']:
            errors.append("precedent_clarity must be clear, mixed, or unclear")

    if 'jurisdiction_history' in factors:
        if factors['jurisdiction_history'] not in ['owner_favorable', 'neutral', 'buyer_favorable']:
            errors.append("jurisdiction_history must be owner_favorable, neutral, or buyer_favorable")

    return len(errors) == 0, errors
