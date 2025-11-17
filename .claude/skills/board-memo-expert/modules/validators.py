#!/usr/bin/env python3
"""
Board Memo Input Validators Module
Validates board memo inputs including financial data, risk assessments, and governance requirements.
"""

from typing import Dict, List, Tuple, Optional


def validate_financial_breakdown(financial_data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate financial breakdown totals match and all required fields present.

    Args:
        financial_data: Financial data dict from input
            {
                'total_cost': 250000,
                'breakdown': {
                    'acquisition': 200000,
                    'legal': 30000,
                    'expert': 20000
                },
                'contingency': 25000,
                'contingency_pct': 0.10
            }

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Check required fields
    if 'total_cost' not in financial_data:
        errors.append("Missing required field: total_cost")
        return False, errors

    if 'breakdown' not in financial_data:
        errors.append("Missing required field: breakdown")
        return False, errors

    total_cost = financial_data['total_cost']
    breakdown = financial_data['breakdown']

    # Validate breakdown totals
    breakdown_sum = sum(breakdown.values())

    # Allow 1% tolerance for rounding
    tolerance = total_cost * 0.01
    if abs(breakdown_sum - total_cost) > tolerance:
        errors.append(
            f"Breakdown sum (${breakdown_sum:,.2f}) does not match "
            f"total_cost (${total_cost:,.2f})"
        )

    # Validate contingency if present
    if 'contingency' in financial_data and 'contingency_pct' in financial_data:
        contingency = financial_data['contingency']
        contingency_pct = financial_data['contingency_pct']

        expected_pct = contingency / total_cost if total_cost > 0 else 0

        if abs(expected_pct - contingency_pct) > 0.01:  # 1% tolerance
            errors.append(
                f"Contingency percentage ({contingency_pct:.2%}) does not match "
                f"calculated value ({expected_pct:.2%})"
            )

    # Validate all breakdown values are non-negative
    for category, amount in breakdown.items():
        if amount < 0:
            errors.append(f"Negative amount in breakdown: {category} = ${amount:,.2f}")

    return len(errors) == 0, errors


def validate_risk_assessment(risks: List[Dict]) -> Tuple[bool, List[str]]:
    """
    Validate risk assessment data structure and severity levels.

    Args:
        risks: List of risk dicts
            [
                {
                    'risk': 'Holdout owner',
                    'severity': 'HIGH',
                    'probability': 0.6,
                    'impact': 'Project delay',
                    'mitigation': 'Early engagement'
                }
            ]

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    valid_severities = {'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'}

    if not risks:
        # Empty risk list is valid - no risks identified
        return True, []

    for idx, risk in enumerate(risks):
        # Check required fields
        if 'risk' not in risk:
            errors.append(f"Risk {idx}: Missing 'risk' description")
            continue

        if 'severity' not in risk:
            errors.append(f"Risk {idx} ({risk['risk']}): Missing severity level")
            continue

        # Validate severity level
        severity = risk['severity'].upper() if isinstance(risk['severity'], str) else risk['severity']
        if severity not in valid_severities:
            errors.append(
                f"Risk {idx} ({risk['risk']}): Invalid severity '{risk['severity']}'. "
                f"Must be one of: {', '.join(valid_severities)}"
            )

        # Validate probability if present
        if 'probability' in risk:
            prob = risk['probability']
            if not isinstance(prob, (int, float)) or prob < 0 or prob > 1:
                errors.append(
                    f"Risk {idx} ({risk['risk']}): Probability must be between 0 and 1, got {prob}"
                )

    return len(errors) == 0, errors


def validate_governance_requirements(governance: Dict) -> Tuple[bool, List[str]]:
    """
    Validate governance and approval requirements.

    Args:
        governance: Governance data dict
            {
                'approval_type': 'authorization',
                'recommendation': 'Approve acquisition',
                'resolution_draft': '...',
                'authority_limits': {...}
            }

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    valid_approval_types = {'authorization', 'ratification', 'information_only', 'delegation'}

    # Check required fields
    if 'approval_type' not in governance:
        errors.append("Missing required field: approval_type")
    else:
        approval_type = governance['approval_type']
        if approval_type not in valid_approval_types:
            errors.append(
                f"Invalid approval_type '{approval_type}'. "
                f"Must be one of: {', '.join(valid_approval_types)}"
            )

    if 'recommendation' not in governance:
        errors.append("Missing required field: recommendation")
    elif not governance['recommendation'] or len(governance['recommendation'].strip()) == 0:
        errors.append("Recommendation cannot be empty")

    # Validate authority limits if present
    if 'authority_limits' in governance:
        limits = governance['authority_limits']

        valid_levels = {'staff', 'ceo', 'board_committee', 'full_board'}
        if 'approval_level' in limits:
            level = limits['approval_level']
            if level not in valid_levels:
                errors.append(
                    f"Invalid approval_level '{level}'. "
                    f"Must be one of: {', '.join(valid_levels)}"
                )

    return len(errors) == 0, errors


def validate_complete_input(input_data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate complete board memo input data.

    Args:
        input_data: Complete input dict with project, financial, risks, governance

    Returns:
        Tuple of (is_valid, all_error_messages)
    """
    all_errors = []

    # Check top-level required sections
    required_sections = ['project', 'financial', 'risks', 'governance']
    for section in required_sections:
        if section not in input_data:
            all_errors.append(f"Missing required section: {section}")

    if all_errors:
        return False, all_errors

    # Validate project section
    project = input_data['project']
    required_project_fields = ['name', 'description', 'rationale', 'urgency']
    for field in required_project_fields:
        if field not in project or not project[field]:
            all_errors.append(f"Project section missing required field: {field}")

    # Validate urgency level
    valid_urgencies = {'low', 'medium', 'high', 'critical'}
    if 'urgency' in project and project['urgency'] not in valid_urgencies:
        all_errors.append(
            f"Invalid urgency level '{project['urgency']}'. "
            f"Must be one of: {', '.join(valid_urgencies)}"
        )

    # Validate financial section
    is_valid, financial_errors = validate_financial_breakdown(input_data['financial'])
    all_errors.extend(financial_errors)

    # Validate risks section
    is_valid, risk_errors = validate_risk_assessment(input_data['risks'])
    all_errors.extend(risk_errors)

    # Validate governance section
    is_valid, governance_errors = validate_governance_requirements(input_data['governance'])
    all_errors.extend(governance_errors)

    return len(all_errors) == 0, all_errors


def validate_npv_inputs(npv_data: Optional[Dict]) -> Tuple[bool, List[str]]:
    """
    Validate NPV analysis inputs if present.

    Args:
        npv_data: Optional NPV analysis dict
            {
                'discount_rate': 0.08,
                'cash_flows': [-100000, 30000, 30000, 30000, 30000],
                'npv': 13723,
                'irr': 0.1524
            }

    Returns:
        Tuple of (is_valid, error_messages)
    """
    if npv_data is None:
        return True, []  # NPV analysis is optional

    errors = []

    # Validate discount rate
    if 'discount_rate' in npv_data:
        rate = npv_data['discount_rate']
        if not isinstance(rate, (int, float)) or rate < 0 or rate > 1:
            errors.append(f"Discount rate must be between 0 and 1, got {rate}")

    # Validate cash flows
    if 'cash_flows' in npv_data:
        cash_flows = npv_data['cash_flows']
        if not isinstance(cash_flows, list) or len(cash_flows) < 2:
            errors.append("Cash flows must be a list with at least 2 values")

        # Check for non-numeric values
        if not all(isinstance(cf, (int, float)) for cf in cash_flows):
            errors.append("All cash flows must be numeric values")

    # Validate IRR if present
    if 'irr' in npv_data:
        irr = npv_data['irr']
        if not isinstance(irr, (int, float)):
            errors.append(f"IRR must be numeric, got {type(irr)}")

    return len(errors) == 0, errors
