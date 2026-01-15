#!/usr/bin/env python3
"""
Statutory Deadlines Module
Ontario Expropriations Act deadline calculations and risk assessment.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional


def calculate_registration_deadline(approval_date: str) -> Dict:
    """
    Calculate 3-month registration deadline per OEA s.9(2).

    Args:
        approval_date: Approval date (YYYY-MM-DD)

    Returns:
        Dict with deadline information
    """
    approval = datetime.fromisoformat(approval_date)

    # Add 90 calendar days
    deadline = approval + timedelta(days=90)

    # Recommended deadline (5-day buffer)
    recommended = approval + timedelta(days=85)

    return {
        'approval_date': approval_date,
        'statutory_deadline': deadline.strftime('%Y-%m-%d'),
        'recommended_deadline': recommended.strftime('%Y-%m-%d'),
        'total_days': 90,
        'buffer_days': 5,
        'statute_reference': 'Expropriations Act, R.S.O. 1990, c. E.26, s. 9(2)'
    }


def calculate_form_2_service_date(registration_date: str, service_method: str = 'personal') -> Dict:
    """
    Calculate Form 2 service date (best practice 30 days before registration).

    Args:
        registration_date: Planned registration date (YYYY-MM-DD)
        service_method: 'personal' or 'registered_mail'

    Returns:
        Dict with service date information
    """
    registration = datetime.fromisoformat(registration_date)

    # Best practice: 30 days before registration
    service_date = registration - timedelta(days=30)

    # If registered mail, add 5 days for delivery
    if service_method == 'registered_mail':
        service_date = service_date - timedelta(days=5)

    return {
        'registration_date': registration_date,
        'service_method': service_method,
        'recommended_service_date': service_date.strftime('%Y-%m-%d'),
        'days_before_registration': 30,
        'delivery_buffer': 5 if service_method == 'registered_mail' else 0,
        'note': 'Best practice (not statutory requirement)'
    }


def calculate_form_7_service_date(possession_date: str, service_method: str = 'personal') -> Dict:
    """
    Calculate Form 7 service date (statutory 30 days minimum per OEA s.11).

    Args:
        possession_date: Planned possession date (YYYY-MM-DD)
        service_method: 'personal' or 'registered_mail'

    Returns:
        Dict with service date information
    """
    possession = datetime.fromisoformat(possession_date)

    # Statutory minimum: 30 days before possession
    statutory_deadline = possession - timedelta(days=30)

    # If registered mail, add 5 days for delivery
    if service_method == 'registered_mail':
        recommended_date = statutory_deadline - timedelta(days=5)
    else:
        recommended_date = statutory_deadline

    return {
        'possession_date': possession_date,
        'service_method': service_method,
        'statutory_deadline': statutory_deadline.strftime('%Y-%m-%d'),
        'recommended_service_date': recommended_date.strftime('%Y-%m-%d'),
        'minimum_days': 30,
        'delivery_buffer': 5 if service_method == 'registered_mail' else 0,
        'statute_reference': 'Expropriations Act, R.S.O. 1990, c. E.26, s. 11(1)'
    }


def calculate_days_remaining(approval_date: str, current_date: Optional[str] = None) -> Dict:
    """
    Calculate days remaining until statutory deadline.

    Args:
        approval_date: Approval date (YYYY-MM-DD)
        current_date: Current date (YYYY-MM-DD), defaults to today

    Returns:
        Dict with days remaining and urgency level
    """
    approval = datetime.fromisoformat(approval_date)

    if current_date:
        current = datetime.fromisoformat(current_date)
    else:
        current = datetime.now()

    # Calculate deadline
    deadline = approval + timedelta(days=90)

    # Days remaining
    days_remaining = (deadline - current).days

    # Determine urgency level
    if days_remaining > 60:
        urgency = 'GREEN'
        status = 'Routine monitoring'
    elif days_remaining > 30:
        urgency = 'YELLOW'
        status = 'Moderate concern - weekly checks'
    elif days_remaining > 15:
        urgency = 'ORANGE'
        status = 'Significant concern - daily monitoring'
    elif days_remaining > 7:
        urgency = 'RED'
        status = 'Critical - crisis mode'
    else:
        urgency = 'CRITICAL'
        status = 'Emergency - weekend work authorized'

    return {
        'approval_date': approval_date,
        'current_date': current.strftime('%Y-%m-%d'),
        'statutory_deadline': deadline.strftime('%Y-%m-%d'),
        'days_remaining': days_remaining,
        'urgency_level': urgency,
        'status': status,
        'percentage_elapsed': round((90 - days_remaining) / 90 * 100, 1)
    }


def assess_deadline_risk(
    task_late_finish: float,
    statutory_deadline: float,
    buffer_days: int = 10
) -> Dict:
    """
    Assess risk of missing statutory deadline.

    Args:
        task_late_finish: Task late finish time (days from start)
        statutory_deadline: Statutory deadline (days from start)
        buffer_days: Minimum buffer days required (default 10)

    Returns:
        Dict with risk assessment
    """
    buffer = statutory_deadline - task_late_finish

    if buffer < 0:
        severity = 'CRITICAL'
        risk_level = 'VERY_HIGH'
        message = f"Task finishes {abs(buffer):.0f} days AFTER statutory deadline"
    elif buffer < 5:
        severity = 'HIGH'
        risk_level = 'HIGH'
        message = f"Only {buffer:.0f} days buffer before statutory deadline"
    elif buffer < buffer_days:
        severity = 'MEDIUM'
        risk_level = 'MEDIUM'
        message = f"{buffer:.0f} days buffer (below {buffer_days}-day minimum)"
    else:
        severity = 'LOW'
        risk_level = 'LOW'
        message = f"{buffer:.0f} days buffer (adequate)"

    return {
        'task_late_finish': round(task_late_finish, 2),
        'statutory_deadline': round(statutory_deadline, 2),
        'buffer_days': round(buffer, 2),
        'severity': severity,
        'risk_level': risk_level,
        'message': message,
        'compliant': buffer >= 0
    }


def generate_oea_timeline_milestones(approval_date: str) -> List[Dict]:
    """
    Generate standard OEA timeline milestones.

    Args:
        approval_date: Approval date (YYYY-MM-DD)

    Returns:
        List of milestone dicts
    """
    approval = datetime.fromisoformat(approval_date)

    milestones = []

    # Milestone 1: Approval received
    milestones.append({
        'name': 'Approval Received',
        'date': approval_date,
        'days_from_approval': 0,
        'description': 'Expropriation approval obtained from approving authority'
    })

    # Milestone 2: Form 2 service (recommended)
    form_2_date = (approval + timedelta(days=55)).strftime('%Y-%m-%d')
    milestones.append({
        'name': 'Form 2 Service (Recommended)',
        'date': form_2_date,
        'days_from_approval': 55,
        'description': 'Serve Notice of Application for Approval (30 days before registration)'
    })

    # Milestone 3: Registration (recommended)
    reg_date = (approval + timedelta(days=85)).strftime('%Y-%m-%d')
    milestones.append({
        'name': 'Plan Registration (Recommended)',
        'date': reg_date,
        'days_from_approval': 85,
        'description': 'Register expropriation plan (5-day buffer before deadline)'
    })

    # Milestone 4: Registration deadline
    deadline_date = (approval + timedelta(days=90)).strftime('%Y-%m-%d')
    milestones.append({
        'name': 'Registration Deadline (STATUTORY)',
        'date': deadline_date,
        'days_from_approval': 90,
        'description': 'Statutory deadline per OEA s.9(2) - approval expires if not registered'
    })

    return milestones
