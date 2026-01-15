#!/usr/bin/env python3
"""
Encumbrance Analysis Module

Analyze encumbrances, assess impact on use and value, determine priority,
and evaluate enforcement risk.
"""

from typing import Dict, List


def analyze_encumbrances(
    instruments: List[Dict],
    restrictions: List[Dict],
    encumbrances: List[Dict]
) -> Dict:
    """
    Comprehensive encumbrance analysis.

    Args:
        instruments: Parsed registered instruments
        restrictions: Additional restrictions
        encumbrances: Known encumbrances

    Returns:
        Dictionary with encumbrance analysis results
    """
    all_encumbrances = []

    # Analyze registered instruments
    for instrument in instruments:
        if _is_encumbrance(instrument):
            analysis = _analyze_single_encumbrance(instrument)
            all_encumbrances.append(analysis)

    # Analyze additional restrictions
    for restriction in restrictions:
        analysis = _analyze_restriction(restriction)
        all_encumbrances.append(analysis)

    # Analyze separately listed encumbrances
    for encumbrance in encumbrances:
        analysis = _analyze_listed_encumbrance(encumbrance)
        all_encumbrances.append(analysis)

    # Sort by priority and severity
    all_encumbrances.sort(
        key=lambda x: (
            _priority_sort_key(x['priority']),
            _severity_sort_key(x['severity'])
        )
    )

    # Generate summary
    summary = _generate_encumbrance_summary(all_encumbrances)

    return {
        'encumbrances': all_encumbrances,
        'summary': summary,
        'critical_issues': [e for e in all_encumbrances if e['severity'] == 'CRITICAL'],
        'high_issues': [e for e in all_encumbrances if e['severity'] == 'HIGH'],
        'medium_issues': [e for e in all_encumbrances if e['severity'] == 'MEDIUM'],
        'low_issues': [e for e in all_encumbrances if e['severity'] == 'LOW']
    }


def _is_encumbrance(instrument: Dict) -> bool:
    """
    Determine if instrument constitutes an encumbrance.

    Args:
        instrument: Instrument dictionary

    Returns:
        True if encumbrance, False otherwise
    """
    encumbrance_types = [
        'Easement',
        'Covenant',
        'Restriction',
        'Lien',
        'Mortgage',
        'Lease',
        'Encroachment',
        'Security Interest',
        'Court Order',
        'Litigation Notice'
    ]

    return instrument.get('classified_type') in encumbrance_types


def _analyze_single_encumbrance(instrument: Dict) -> Dict:
    """
    Analyze a single encumbrance from registered instrument.

    Args:
        instrument: Instrument dictionary

    Returns:
        Encumbrance analysis dictionary
    """
    inst_type = instrument.get('classified_type', 'Other')
    description = instrument.get('description', '')

    # Assess impact
    impact = assess_encumbrance_impact(inst_type, description, instrument)

    # Determine priority
    priority = assess_priority(instrument)

    # Assess use restrictions
    use_restrictions = assess_use_restrictions(inst_type, description)

    # Estimate value impact
    value_impact = estimate_value_impact(inst_type, impact, use_restrictions)

    return {
        'source': 'registered_instrument',
        'instrument_number': instrument.get('instrument_number', 'N/A'),
        'type': inst_type,
        'description': description[:200],  # Truncate for display
        'priority': priority,
        'severity': impact['severity'],
        'use_restrictions': use_restrictions,
        'value_impact': value_impact,
        'registration_date': instrument.get('registration_date'),
        'parties': instrument.get('parties', {}),
        'requires_action': impact['requires_action'],
        'recommended_actions': impact['recommended_actions']
    }


def _analyze_restriction(restriction: Dict) -> Dict:
    """
    Analyze a use restriction.

    Args:
        restriction: Restriction dictionary

    Returns:
        Encumbrance analysis dictionary
    """
    restriction_type = restriction.get('type', 'General Restriction')
    description = restriction.get('description', '')

    use_restrictions = {
        'building_height': 'height' in description.lower(),
        'setbacks': 'setback' in description.lower(),
        'use_limitations': True,  # All restrictions limit use
        'architectural': 'architect' in description.lower() or 'design' in description.lower()
    }

    # Restrictions typically have medium impact
    severity = 'MEDIUM'
    if any(use_restrictions.values()):
        severity = 'MEDIUM'

    return {
        'source': 'restriction',
        'instrument_number': 'N/A',
        'type': restriction_type,
        'description': description[:200],
        'priority': 'N/A',
        'severity': severity,
        'use_restrictions': use_restrictions,
        'value_impact': {'min': 0.0, 'max': 5.0, 'likely': 2.0},
        'registration_date': restriction.get('date'),
        'parties': {},
        'requires_action': False,
        'recommended_actions': ['Review restriction details with planning consultant']
    }


def _analyze_listed_encumbrance(encumbrance: Dict) -> Dict:
    """
    Analyze separately listed encumbrance.

    Args:
        encumbrance: Encumbrance dictionary

    Returns:
        Encumbrance analysis dictionary
    """
    enc_type = encumbrance.get('type', 'Unknown')
    description = encumbrance.get('description', '')

    # Map to standard types
    type_mapping = {
        'lien': 'Lien',
        'mortgage': 'Mortgage',
        'easement': 'Easement',
        'covenant': 'Covenant',
        'lease': 'Lease'
    }

    standardized_type = type_mapping.get(enc_type.lower(), 'Other')

    # Assess impact
    impact = assess_encumbrance_impact(standardized_type, description, encumbrance)

    return {
        'source': 'listed_encumbrance',
        'instrument_number': encumbrance.get('reference', 'N/A'),
        'type': standardized_type,
        'description': description[:200],
        'priority': encumbrance.get('priority', 'Unknown'),
        'severity': impact['severity'],
        'use_restrictions': assess_use_restrictions(standardized_type, description),
        'value_impact': estimate_value_impact(standardized_type, impact, {}),
        'registration_date': encumbrance.get('date'),
        'parties': encumbrance.get('parties', {}),
        'requires_action': impact['requires_action'],
        'recommended_actions': impact['recommended_actions']
    }


def assess_encumbrance_impact(
    encumbrance_type: str,
    description: str,
    full_data: Dict
) -> Dict:
    """
    Assess impact severity and required actions.

    Args:
        encumbrance_type: Type of encumbrance
        description: Description text
        full_data: Full encumbrance data

    Returns:
        Impact assessment dictionary
    """
    # Critical severity encumbrances
    if encumbrance_type in ['Lien', 'Litigation Notice', 'Court Order']:
        return {
            'severity': 'CRITICAL',
            'requires_action': True,
            'recommended_actions': [
                'Immediate legal review required',
                'Obtain discharge or postponement before closing',
                'Negotiate resolution with lienholder'
            ]
        }

    # High severity
    if encumbrance_type in ['Mortgage', 'Security Interest']:
        return {
            'severity': 'HIGH',
            'requires_action': True,
            'recommended_actions': [
                'Obtain discharge at closing',
                'Verify payout amount',
                'Arrange postponement if necessary'
            ]
        }

    # Medium severity - use restrictions
    if encumbrance_type in ['Covenant', 'Restriction']:
        # Check if restrictive
        restrictive_keywords = ['prohibit', 'restrict', 'limit', 'prevent', 'forbid']
        is_restrictive = any(kw in description.lower() for kw in restrictive_keywords)

        if is_restrictive:
            return {
                'severity': 'MEDIUM',
                'requires_action': True,
                'recommended_actions': [
                    'Review restriction against intended use',
                    'Assess compliance requirements',
                    'Consider application to modify/discharge if necessary'
                ]
            }
        else:
            return {
                'severity': 'LOW',
                'requires_action': False,
                'recommended_actions': [
                    'Review terms for compliance',
                    'Note for future reference'
                ]
            }

    # Easements - depends on scope
    if encumbrance_type == 'Easement':
        area_info = full_data.get('area_affected', '').lower()
        if 'entire' in area_info or 'whole' in area_info:
            severity = 'HIGH'
        else:
            severity = 'MEDIUM'

        return {
            'severity': severity,
            'requires_action': False,
            'recommended_actions': [
                'Survey to confirm easement location',
                'Review development restrictions within easement area',
                'Confirm utility access requirements'
            ]
        }

    # Leases
    if encumbrance_type == 'Lease':
        return {
            'severity': 'MEDIUM',
            'requires_action': True,
            'recommended_actions': [
                'Review lease terms and expiry',
                'Confirm tenant rights',
                'Consider estoppel certificate'
            ]
        }

    # Default - low severity
    return {
        'severity': 'LOW',
        'requires_action': False,
        'recommended_actions': [
            'Review for potential impact',
            'Monitor for changes'
        ]
    }


def assess_priority(instrument: Dict) -> str:
    """
    Assess legal priority of encumbrance.

    Args:
        instrument: Instrument dictionary

    Returns:
        Priority classification
    """
    priority_num = instrument.get('priority_number')

    if priority_num is None:
        return 'Unknown'
    elif priority_num == 1:
        return 'First Priority'
    elif priority_num == 2:
        return 'Second Priority'
    elif priority_num <= 5:
        return f'{priority_num}th Priority'
    else:
        return 'Subsequent Priority'


def assess_use_restrictions(encumbrance_type: str, description: str) -> Dict:
    """
    Identify specific use restrictions.

    Args:
        encumbrance_type: Type of encumbrance
        description: Description text

    Returns:
        Dictionary of use restriction flags
    """
    desc_lower = description.lower()

    return {
        'building_restrictions': any(kw in desc_lower for kw in ['build', 'construct', 'structure']),
        'height_restrictions': 'height' in desc_lower,
        'setback_restrictions': 'setback' in desc_lower,
        'use_type_restrictions': any(kw in desc_lower for kw in ['residential', 'commercial', 'industrial']),
        'access_restrictions': 'access' in desc_lower,
        'drainage_restrictions': 'drain' in desc_lower or 'water' in desc_lower,
        'utility_access': encumbrance_type == 'Easement' and any(kw in desc_lower for kw in ['hydro', 'gas', 'electric', 'sewer', 'water']),
        'environmental_restrictions': any(kw in desc_lower for kw in ['environmental', 'contamination', 'hazard'])
    }


def estimate_value_impact(
    encumbrance_type: str,
    impact_assessment: Dict,
    use_restrictions: Dict
) -> Dict:
    """
    Estimate percentage impact on property value.

    Args:
        encumbrance_type: Type of encumbrance
        impact_assessment: Impact assessment from assess_encumbrance_impact
        use_restrictions: Use restrictions dictionary

    Returns:
        Dictionary with value impact range
    """
    # Base impact by severity
    severity_impact = {
        'CRITICAL': {'min': 20.0, 'max': 50.0},
        'HIGH': {'min': 10.0, 'max': 30.0},
        'MEDIUM': {'min': 2.0, 'max': 15.0},
        'LOW': {'min': 0.0, 'max': 5.0}
    }

    severity = impact_assessment.get('severity', 'LOW')
    base = severity_impact.get(severity, {'min': 0.0, 'max': 5.0})

    # Adjust for use restrictions
    restriction_count = sum(1 for v in use_restrictions.values() if v)
    adjustment = restriction_count * 2.0  # 2% per restriction

    min_impact = base['min']
    max_impact = min(base['max'] + adjustment, 50.0)  # Cap at 50%
    likely_impact = (min_impact + max_impact) / 2

    return {
        'min': round(min_impact, 1),
        'max': round(max_impact, 1),
        'likely': round(likely_impact, 1),
        'basis': f"{severity} severity with {restriction_count} use restrictions"
    }


def _generate_encumbrance_summary(encumbrances: List[Dict]) -> Dict:
    """
    Generate summary statistics.

    Args:
        encumbrances: List of analyzed encumbrances

    Returns:
        Summary dictionary
    """
    if not encumbrances:
        return {
            'total': 0,
            'by_severity': {},
            'action_required_count': 0,
            'average_value_impact': 0.0
        }

    severity_counts = {}
    action_count = 0
    total_value_impact = 0.0

    for enc in encumbrances:
        # Count by severity
        sev = enc['severity']
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

        # Count actions required
        if enc['requires_action']:
            action_count += 1

        # Sum value impact
        total_value_impact += enc['value_impact']['likely']

    avg_impact = total_value_impact / len(encumbrances) if encumbrances else 0.0

    return {
        'total': len(encumbrances),
        'by_severity': severity_counts,
        'action_required_count': action_count,
        'average_value_impact': round(avg_impact, 1),
        'total_value_impact_range': {
            'min': round(sum(e['value_impact']['min'] for e in encumbrances), 1),
            'max': round(sum(e['value_impact']['max'] for e in encumbrances), 1)
        }
    }


def _priority_sort_key(priority: str) -> int:
    """
    Convert priority to sort key.

    Args:
        priority: Priority string

    Returns:
        Integer sort key (lower = higher priority)
    """
    if priority == 'First Priority':
        return 1
    elif priority == 'Second Priority':
        return 2
    elif 'Priority' in priority:
        # Extract number from "Nth Priority"
        try:
            return int(priority.split('th')[0])
        except:
            return 999
    else:
        return 999


def _severity_sort_key(severity: str) -> int:
    """
    Convert severity to sort key.

    Args:
        severity: Severity string

    Returns:
        Integer sort key (lower = more severe)
    """
    severity_order = {
        'CRITICAL': 1,
        'HIGH': 2,
        'MEDIUM': 3,
        'LOW': 4
    }
    return severity_order.get(severity, 5)
