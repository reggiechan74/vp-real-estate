#!/usr/bin/env python3
"""
Registration Validation Module

Validate registration compliance, detect defects in legal descriptions,
signatures, parties, and registration procedures.
"""

from typing import Dict, List
import re


def validate_registration(instruments: List[Dict], defects: List[Dict]) -> Dict:
    """
    Comprehensive registration validation.

    Args:
        instruments: List of registered instruments
        defects: Known defects from input

    Returns:
        Dictionary with validation results
    """
    all_defects = []

    # Validate each instrument
    for idx, instrument in enumerate(instruments):
        inst_defects = detect_instrument_defects(instrument, idx)
        all_defects.extend(inst_defects)

    # Add known defects from input
    for defect in defects:
        all_defects.append(_format_known_defect(defect))

    # Categorize defects
    categorized = _categorize_defects(all_defects)

    # Assess overall validity
    validity = _assess_registration_validity(categorized)

    return {
        'defects': all_defects,
        'categorized': categorized,
        'validity': validity,
        'summary': {
            'total_defects': len(all_defects),
            'critical_defects': len(categorized['critical']),
            'major_defects': len(categorized['major']),
            'minor_defects': len(categorized['minor']),
            'overall_status': validity['status']
        }
    }


def detect_instrument_defects(instrument: Dict, index: int) -> List[Dict]:
    """
    Detect registration defects in a single instrument.

    Args:
        instrument: Instrument dictionary
        index: Index in instruments list

    Returns:
        List of detected defects
    """
    defects = []

    # Check parties
    parties_defects = _check_parties_defects(instrument, index)
    defects.extend(parties_defects)

    # Check legal description
    desc_defects = _check_description_defects(instrument, index)
    defects.extend(desc_defects)

    # Check registration date
    date_defects = _check_date_defects(instrument, index)
    defects.extend(date_defects)

    # Check instrument number
    num_defects = _check_instrument_number_defects(instrument, index)
    defects.extend(num_defects)

    # Check type-specific requirements
    type_defects = _check_type_specific_defects(instrument, index)
    defects.extend(type_defects)

    return defects


def _check_parties_defects(instrument: Dict, index: int) -> List[Dict]:
    """
    Check for defects in party information.

    Args:
        instrument: Instrument dictionary
        index: Index

    Returns:
        List of party-related defects
    """
    defects = []
    inst_num = instrument.get('instrument_number', f'Instrument {index}')

    parties = instrument.get('parties', {})

    # Missing parties
    if not parties:
        defects.append({
            'instrument': inst_num,
            'category': 'Parties',
            'severity': 'MAJOR',
            'defect': 'No party information provided',
            'impact': 'Cannot determine grantor/grantee',
            'remedy': 'Obtain party information from land registry'
        })
        return defects

    # Missing grantor
    if 'grantor' not in parties or not parties['grantor']:
        defects.append({
            'instrument': inst_num,
            'category': 'Parties',
            'severity': 'CRITICAL',
            'defect': 'Missing grantor',
            'impact': 'Instrument may be void for uncertainty',
            'remedy': 'Verify grantor identity and update registration'
        })

    # Missing grantee
    if 'grantee' not in parties or not parties['grantee']:
        defects.append({
            'instrument': inst_num,
            'category': 'Parties',
            'severity': 'CRITICAL',
            'defect': 'Missing grantee',
            'impact': 'Instrument may be void for uncertainty',
            'remedy': 'Verify grantee identity and update registration'
        })

    # Check for suspicious party names
    for party_type in ['grantor', 'grantee']:
        if party_type in parties:
            party_name = parties[party_type]
            if len(party_name) < 3:
                defects.append({
                    'instrument': inst_num,
                    'category': 'Parties',
                    'severity': 'MAJOR',
                    'defect': f'Incomplete {party_type} name: "{party_name}"',
                    'impact': 'May indicate data entry error',
                    'remedy': 'Verify party name against original registration'
                })

    return defects


def _check_description_defects(instrument: Dict, index: int) -> List[Dict]:
    """
    Check for defects in legal description.

    Args:
        instrument: Instrument dictionary
        index: Index

    Returns:
        List of description-related defects
    """
    defects = []
    inst_num = instrument.get('instrument_number', f'Instrument {index}')

    description = instrument.get('description', '')

    # Missing description
    if not description:
        defects.append({
            'instrument': inst_num,
            'category': 'Description',
            'severity': 'MAJOR',
            'defect': 'No description provided',
            'impact': 'Cannot assess scope of encumbrance',
            'remedy': 'Obtain full description from registry'
        })
        return defects

    # Very short description (likely incomplete)
    if len(description) < 20:
        defects.append({
            'instrument': inst_num,
            'category': 'Description',
            'severity': 'MINOR',
            'defect': 'Description appears incomplete',
            'impact': 'May lack important details',
            'remedy': 'Review full registered document'
        })

    # Check for area description if it's an easement
    if instrument.get('classified_type') == 'Easement':
        area = instrument.get('area_affected', '')
        if not area:
            defects.append({
                'instrument': inst_num,
                'category': 'Description',
                'severity': 'MAJOR',
                'defect': 'Easement missing area description',
                'impact': 'Cannot determine extent of easement',
                'remedy': 'Survey to establish easement boundaries'
            })

    return defects


def _check_date_defects(instrument: Dict, index: int) -> List[Dict]:
    """
    Check for defects in registration date.

    Args:
        instrument: Instrument dictionary
        index: Index

    Returns:
        List of date-related defects
    """
    defects = []
    inst_num = instrument.get('instrument_number', f'Instrument {index}')

    reg_date = instrument.get('registration_date', '')

    # Missing date
    if not reg_date:
        defects.append({
            'instrument': inst_num,
            'category': 'Registration',
            'severity': 'MAJOR',
            'defect': 'Missing registration date',
            'impact': 'Cannot determine priority',
            'remedy': 'Obtain date from land registry'
        })
        return defects

    # Validate date format
    date_pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(date_pattern, reg_date):
        defects.append({
            'instrument': inst_num,
            'category': 'Registration',
            'severity': 'MINOR',
            'defect': f'Invalid date format: {reg_date}',
            'impact': 'May affect priority determination',
            'remedy': 'Verify and correct date format'
        })

    return defects


def _check_instrument_number_defects(instrument: Dict, index: int) -> List[Dict]:
    """
    Check for defects in instrument number.

    Args:
        instrument: Instrument dictionary
        index: Index

    Returns:
        List of instrument number defects
    """
    defects = []
    inst_num = instrument.get('instrument_number', '')

    # Missing number
    if not inst_num:
        defects.append({
            'instrument': f'Index {index}',
            'category': 'Registration',
            'severity': 'CRITICAL',
            'defect': 'Missing instrument number',
            'impact': 'Cannot verify registration',
            'remedy': 'Obtain instrument number from registry'
        })
        return defects

    # Very short number (likely incomplete)
    if len(inst_num) < 4:
        defects.append({
            'instrument': inst_num,
            'category': 'Registration',
            'severity': 'MAJOR',
            'defect': f'Instrument number appears incomplete: {inst_num}',
            'impact': 'May not be valid registry reference',
            'remedy': 'Verify complete instrument number'
        })

    return defects


def _check_type_specific_defects(instrument: Dict, index: int) -> List[Dict]:
    """
    Check for type-specific registration defects.

    Args:
        instrument: Instrument dictionary
        index: Index

    Returns:
        List of type-specific defects
    """
    defects = []
    inst_num = instrument.get('instrument_number', f'Instrument {index}')
    inst_type = instrument.get('classified_type', '')

    # Liens should have amount
    if inst_type == 'Lien':
        if 'amount' not in instrument and 'value' not in instrument:
            defects.append({
                'instrument': inst_num,
                'category': 'Type-Specific',
                'severity': 'MAJOR',
                'defect': 'Lien missing amount claimed',
                'impact': 'Cannot assess financial impact',
                'remedy': 'Obtain lien details including amount'
            })

    # Mortgages should have principal amount
    if inst_type == 'Mortgage':
        if 'principal' not in instrument and 'amount' not in instrument:
            defects.append({
                'instrument': inst_num,
                'category': 'Type-Specific',
                'severity': 'MAJOR',
                'defect': 'Mortgage missing principal amount',
                'impact': 'Cannot assess financial encumbrance',
                'remedy': 'Obtain mortgage details'
            })

    # Leases should have term information
    if inst_type == 'Lease':
        if 'term' not in instrument and 'expiry' not in instrument:
            defects.append({
                'instrument': inst_num,
                'category': 'Type-Specific',
                'severity': 'MINOR',
                'defect': 'Lease missing term/expiry information',
                'impact': 'Cannot assess duration of encumbrance',
                'remedy': 'Review lease for term details'
            })

    return defects


def _format_known_defect(defect: Dict) -> Dict:
    """
    Format a known defect from input.

    Args:
        defect: Defect dictionary from input

    Returns:
        Formatted defect dictionary
    """
    return {
        'instrument': defect.get('instrument', 'Unknown'),
        'category': defect.get('category', 'General'),
        'severity': defect.get('severity', 'MEDIUM'),
        'defect': defect.get('description', 'Unspecified defect'),
        'impact': defect.get('impact', 'Potential registration issue'),
        'remedy': defect.get('remedy', 'Legal review recommended')
    }


def _categorize_defects(defects: List[Dict]) -> Dict:
    """
    Categorize defects by severity.

    Args:
        defects: List of all defects

    Returns:
        Dictionary with categorized defects
    """
    categorized = {
        'critical': [],
        'major': [],
        'minor': []
    }

    for defect in defects:
        severity = defect.get('severity', 'MINOR')
        if severity == 'CRITICAL':
            categorized['critical'].append(defect)
        elif severity == 'MAJOR':
            categorized['major'].append(defect)
        else:
            categorized['minor'].append(defect)

    return categorized


def _assess_registration_validity(categorized: Dict) -> Dict:
    """
    Assess overall registration validity.

    Args:
        categorized: Categorized defects

    Returns:
        Validity assessment dictionary
    """
    critical_count = len(categorized['critical'])
    major_count = len(categorized['major'])
    minor_count = len(categorized['minor'])

    # Determine status
    if critical_count > 0:
        status = 'INVALID'
        message = f'{critical_count} critical defects found - immediate legal review required'
        marketable = False
    elif major_count > 3:
        status = 'QUESTIONABLE'
        message = f'{major_count} major defects found - legal review recommended before proceeding'
        marketable = False
    elif major_count > 0:
        status = 'NEEDS_REVIEW'
        message = f'{major_count} major defects and {minor_count} minor defects - review recommended'
        marketable = True  # With caveats
    elif minor_count > 5:
        status = 'MINOR_ISSUES'
        message = f'{minor_count} minor defects - acceptable but should be noted'
        marketable = True
    else:
        status = 'VALID'
        message = 'No significant registration defects identified'
        marketable = True

    return {
        'status': status,
        'message': message,
        'marketable': marketable,
        'critical_count': critical_count,
        'major_count': major_count,
        'minor_count': minor_count,
        'recommendation': _get_validity_recommendation(status)
    }


def _get_validity_recommendation(status: str) -> str:
    """
    Get recommendation based on validity status.

    Args:
        status: Validity status

    Returns:
        Recommendation string
    """
    recommendations = {
        'INVALID': 'Do not proceed with transaction until critical defects are resolved. Immediate legal intervention required.',
        'QUESTIONABLE': 'Proceed with extreme caution. Obtain legal opinion on defects before closing.',
        'NEEDS_REVIEW': 'Acceptable to proceed with conditions. Address major defects before or at closing.',
        'MINOR_ISSUES': 'Proceed normally. Note minor issues for future reference.',
        'VALID': 'Clear to proceed with transaction.'
    }

    return recommendations.get(status, 'Obtain legal review.')


def detect_defects(instruments: List[Dict]) -> List[Dict]:
    """
    Convenience function to detect all defects.

    Args:
        instruments: List of instruments

    Returns:
        List of all detected defects
    """
    all_defects = []
    for idx, instrument in enumerate(instruments):
        defects = detect_instrument_defects(instrument, idx)
        all_defects.extend(defects)

    return all_defects
