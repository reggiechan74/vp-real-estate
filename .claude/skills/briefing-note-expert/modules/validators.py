#!/usr/bin/env python3
"""
Briefing Note Input Validation Module
Validates briefing note inputs against schema requirements
"""

from typing import Dict, List, Tuple, Optional
from datetime import datetime


def validate_briefing_note_input(data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate briefing note input data.

    Args:
        data: Briefing note input dictionary

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Required fields
    required_fields = ['project_name', 'issue', 'background', 'financial_summary', 'recommendation']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Missing required field: {field}")

    # Validate background structure
    if 'background' in data:
        bg = data['background']
        if not isinstance(bg, dict):
            errors.append("Background must be an object")
        else:
            if 'context' not in bg or not bg['context']:
                errors.append("Background.context is required")
            if 'project_timeline' not in bg:
                errors.append("Background.project_timeline is required")

    # Validate financial summary
    if 'financial_summary' in data:
        fs = data['financial_summary']
        if not isinstance(fs, dict):
            errors.append("Financial_summary must be an object")
        else:
            if 'total_cost' not in fs:
                errors.append("Financial_summary.total_cost is required")
            elif not isinstance(fs['total_cost'], (int, float)) or fs['total_cost'] < 0:
                errors.append("Financial_summary.total_cost must be a positive number")

            # Validate breakdown if provided
            if 'breakdown' in fs and fs['breakdown']:
                breakdown_total = sum(fs['breakdown'].values())
                if abs(breakdown_total - fs['total_cost']) > 1.0:  # Allow small rounding errors
                    errors.append(
                        f"Breakdown total (${breakdown_total:,.2f}) does not match "
                        f"total_cost (${fs['total_cost']:,.2f})"
                    )

    # Validate urgency if provided
    if 'urgency' in data:
        valid_urgency = ['low', 'medium', 'high']
        if data['urgency'] not in valid_urgency:
            errors.append(f"Urgency must be one of: {', '.join(valid_urgency)}")

    # Validate risks if provided
    if 'risks' in data and data['risks']:
        for idx, risk in enumerate(data['risks']):
            if 'risk' not in risk:
                errors.append(f"Risk {idx+1}: 'risk' field is required")
            if 'severity' not in risk:
                errors.append(f"Risk {idx+1}: 'severity' field is required")
            elif risk['severity'] not in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']:
                errors.append(f"Risk {idx+1}: severity must be LOW, MEDIUM, HIGH, or CRITICAL")

            if 'probability' in risk:
                if not isinstance(risk['probability'], (int, float)) or not (0 <= risk['probability'] <= 1):
                    errors.append(f"Risk {idx+1}: probability must be between 0 and 1")

    # Validate action items if provided
    if 'action_items' in data and data['action_items']:
        for idx, item in enumerate(data['action_items']):
            if 'action' not in item:
                errors.append(f"Action item {idx+1}: 'action' field is required")
            if 'responsible' not in item:
                errors.append(f"Action item {idx+1}: 'responsible' field is required")

            if 'priority' in item and item['priority'] not in ['LOW', 'MEDIUM', 'HIGH']:
                errors.append(f"Action item {idx+1}: priority must be LOW, MEDIUM, or HIGH")

    # Validate dates if provided
    date_fields = [
        ('background.project_timeline.start_date', lambda d: d.get('background', {}).get('project_timeline', {}).get('start_date')),
        ('background.project_timeline.critical_deadline', lambda d: d.get('background', {}).get('project_timeline', {}).get('critical_deadline')),
        ('metadata.date', lambda d: d.get('metadata', {}).get('date'))
    ]

    for field_name, getter in date_fields:
        date_str = getter(data)
        if date_str:
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                errors.append(f"{field_name} must be in YYYY-MM-DD format")

    is_valid = len(errors) == 0
    return is_valid, errors


def validate_financial_consistency(financial_summary: Dict) -> Tuple[bool, List[str]]:
    """
    Validate financial data consistency.

    Args:
        financial_summary: Financial summary dictionary

    Returns:
        Tuple of (is_valid, warning_messages)
    """
    warnings = []

    # Check contingency consistency
    if 'contingency' in financial_summary and 'contingency_pct' in financial_summary:
        total = financial_summary.get('total_cost', 0)
        contingency = financial_summary['contingency']
        contingency_pct = financial_summary['contingency_pct']

        expected_contingency = total * contingency_pct
        if abs(contingency - expected_contingency) > 1.0:  # Allow small rounding
            warnings.append(
                f"Contingency amount (${contingency:,.2f}) does not match "
                f"contingency_pct ({contingency_pct*100:.1f}% of ${total:,.2f} = ${expected_contingency:,.2f})"
            )

    # Check budget variance consistency
    if 'budget_comparison' in financial_summary:
        bc = financial_summary['budget_comparison']
        if 'approved_budget' in bc and 'variance' in bc:
            total = financial_summary.get('total_cost', 0)
            budget = bc['approved_budget']
            variance = bc['variance']

            expected_variance = total - budget
            if abs(variance - expected_variance) > 1.0:
                warnings.append(
                    f"Budget variance (${variance:,.2f}) does not match "
                    f"total_cost - approved_budget (${expected_variance:,.2f})"
                )

        if 'variance' in bc and 'variance_pct' in bc and 'approved_budget' in bc:
            variance = bc['variance']
            variance_pct = bc['variance_pct']
            budget = bc['approved_budget']

            expected_pct = (variance / budget * 100) if budget > 0 else 0
            if abs(variance_pct - expected_pct) > 0.1:
                warnings.append(
                    f"Variance percentage ({variance_pct:.2f}%) does not match "
                    f"calculated percentage ({expected_pct:.2f}%)"
                )

    is_valid = len(warnings) == 0
    return is_valid, warnings


def validate_timeline_logic(background: Dict) -> Tuple[bool, List[str]]:
    """
    Validate timeline logic and sequencing.

    Args:
        background: Background dictionary with timeline

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    if 'project_timeline' not in background:
        return True, []

    timeline = background['project_timeline']

    # Check start_date < critical_deadline
    if 'start_date' in timeline and 'critical_deadline' in timeline:
        try:
            start = datetime.strptime(timeline['start_date'], '%Y-%m-%d')
            deadline = datetime.strptime(timeline['critical_deadline'], '%Y-%m-%d')

            if start >= deadline:
                errors.append("Start date must be before critical deadline")
        except ValueError:
            pass  # Date format errors caught in main validation

    # Check milestone sequencing
    if 'key_milestones' in timeline and timeline['key_milestones']:
        milestones = timeline['key_milestones']
        prev_date = None

        for idx, milestone in enumerate(milestones):
            if 'date' in milestone:
                try:
                    current_date = datetime.strptime(milestone['date'], '%Y-%m-%d')

                    # Warn if milestones are not sequential (but don't error)
                    if prev_date and current_date < prev_date:
                        errors.append(
                            f"Milestone {idx+1} ({milestone.get('milestone', 'unnamed')}) "
                            f"is dated before previous milestone"
                        )

                    prev_date = current_date
                except ValueError:
                    errors.append(f"Milestone {idx+1}: invalid date format")

    is_valid = len(errors) == 0
    return is_valid, errors


def validate_risk_assessment(risks: List[Dict]) -> Tuple[bool, List[str]]:
    """
    Validate risk assessment completeness and logic.

    Args:
        risks: List of risk dictionaries

    Returns:
        Tuple of (is_valid, warning_messages)
    """
    warnings = []

    if not risks:
        warnings.append("No risks identified - consider adding risk assessment")
        return False, warnings

    # Check for critical/high risks without mitigation
    for idx, risk in enumerate(risks):
        severity = risk.get('severity')
        mitigation = risk.get('mitigation', '')

        if severity in ['CRITICAL', 'HIGH'] and not mitigation:
            warnings.append(
                f"Risk {idx+1} ({risk.get('risk', 'unnamed')}) is {severity} "
                f"but has no mitigation strategy"
            )

        # Check for high severity but low probability inconsistency
        if severity in ['CRITICAL', 'HIGH']:
            prob = risk.get('probability', 0.5)
            if prob < 0.1:
                warnings.append(
                    f"Risk {idx+1}: {severity} severity but very low probability ({prob*100:.0f}%) "
                    f"- verify consistency"
                )

        # Check for risk owner on high severity risks
        if severity in ['CRITICAL', 'HIGH'] and 'owner' not in risk:
            warnings.append(
                f"Risk {idx+1}: {severity} risk should have assigned owner"
            )

    # Check severity distribution
    severity_counts = {}
    for risk in risks:
        severity = risk.get('severity', 'MEDIUM')
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

    # Warn if all risks are same severity
    if len(severity_counts) == 1:
        warnings.append(
            f"All risks have same severity ({list(severity_counts.keys())[0]}) "
            f"- consider more granular assessment"
        )

    is_valid = len(warnings) == 0
    return is_valid, warnings
