#!/usr/bin/env python3
"""
Title Parsing Module

Parse registered instruments, classify by type, extract key attributes,
and organize by priority.
"""

from typing import Dict, List
from datetime import datetime


def parse_registered_instruments(instruments: List[Dict]) -> Dict:
    """
    Parse and categorize registered instruments.

    Args:
        instruments: List of raw instrument dictionaries

    Returns:
        Dictionary with parsed and categorized instruments
    """
    parsed = {
        'by_type': {},
        'by_priority': [],
        'critical': [],
        'non_critical': [],
        'summary': {}
    }

    # Categorize by type
    for instrument in instruments:
        inst_type = classify_instrument(instrument)
        instrument['classified_type'] = inst_type

        if inst_type not in parsed['by_type']:
            parsed['by_type'][inst_type] = []

        parsed['by_type'][inst_type].append(instrument)

    # Sort by registration date (priority)
    sorted_instruments = sorted(
        instruments,
        key=lambda x: x.get('registration_date', '9999-12-31')
    )

    # Assign priority numbers
    for idx, instrument in enumerate(sorted_instruments, start=1):
        instrument['priority_number'] = idx
        parsed['by_priority'].append(instrument)

        # Flag critical instruments
        if _is_critical_instrument(instrument):
            parsed['critical'].append(instrument)
        else:
            parsed['non_critical'].append(instrument)

    # Generate summary
    parsed['summary'] = {
        'total_instruments': len(instruments),
        'by_type_count': {k: len(v) for k, v in parsed['by_type'].items()},
        'critical_count': len(parsed['critical']),
        'earliest_date': sorted_instruments[0].get('registration_date') if sorted_instruments else None,
        'latest_date': sorted_instruments[-1].get('registration_date') if sorted_instruments else None
    }

    return parsed


def classify_instrument(instrument: Dict) -> str:
    """
    Classify instrument into standardized categories.

    Args:
        instrument: Instrument dictionary

    Returns:
        Standardized instrument type
    """
    raw_type = instrument.get('instrument_type', 'Other')

    # Standardize common variations
    type_mapping = {
        'Easement': 'Easement',
        'Right of Way': 'Easement',
        'ROW': 'Easement',
        'Covenant': 'Covenant',
        'Restrictive Covenant': 'Covenant',
        'Building Scheme': 'Covenant',
        'Restriction': 'Restriction',
        'Use Restriction': 'Restriction',
        'Lien': 'Lien',
        'Construction Lien': 'Lien',
        "Mechanic's Lien": 'Lien',
        'Mortgage': 'Mortgage',
        'Charge': 'Mortgage',
        'Lease': 'Lease',
        'Encroachment': 'Encroachment',
        'Notice': 'Notice',
        'Notice of Security Interest': 'Security Interest',
        'Court Order': 'Court Order',
        'Caution': 'Caution',
        'Certificate of Pending Litigation': 'Litigation Notice',
        'CPL': 'Litigation Notice'
    }

    return type_mapping.get(raw_type, 'Other')


def extract_parties(instrument: Dict) -> Dict:
    """
    Extract and normalize party information.

    Args:
        instrument: Instrument dictionary

    Returns:
        Dictionary with normalized party information
    """
    parties = instrument.get('parties', {})

    return {
        'grantor': parties.get('grantor', 'Unknown'),
        'grantee': parties.get('grantee', 'Unknown'),
        'grantor_type': _classify_party_type(parties.get('grantor', '')),
        'grantee_type': _classify_party_type(parties.get('grantee', ''))
    }


def _classify_party_type(party_name: str) -> str:
    """
    Classify party as individual, corporation, government, etc.

    Args:
        party_name: Party name string

    Returns:
        Party type classification
    """
    if not party_name or party_name == 'Unknown':
        return 'Unknown'

    name_lower = party_name.lower()

    # Government entities
    govt_keywords = [
        'province', 'crown', 'ministry', 'municipality', 'city', 'town',
        'township', 'region', 'county', 'hydro', 'commission', 'authority',
        'canada', 'ontario', 'federal'
    ]
    if any(keyword in name_lower for keyword in govt_keywords):
        return 'Government'

    # Corporations
    corp_keywords = ['inc', 'ltd', 'corp', 'company', 'limited', 'llc']
    if any(keyword in name_lower for keyword in corp_keywords):
        return 'Corporation'

    # Utilities
    utility_keywords = ['hydro', 'gas', 'electric', 'telecom', 'bell', 'rogers']
    if any(keyword in name_lower for keyword in utility_keywords):
        return 'Utility'

    # Default to individual
    return 'Individual'


def _is_critical_instrument(instrument: Dict) -> bool:
    """
    Determine if instrument is critical (requires immediate attention).

    Args:
        instrument: Instrument dictionary

    Returns:
        True if critical, False otherwise
    """
    critical_types = [
        'Lien',
        'Mortgage',
        'Court Order',
        'Security Interest',
        'Litigation Notice',
        'Caution'
    ]

    classified_type = instrument.get('classified_type', '')

    # Type-based criticality
    if classified_type in critical_types:
        return True

    # Description-based criticality
    description = instrument.get('description', '').lower()
    critical_keywords = [
        'default',
        'foreclosure',
        'litigation',
        'pending',
        'dispute',
        'breach',
        'violation',
        'unpaid',
        'arrears'
    ]

    if any(keyword in description for keyword in critical_keywords):
        return True

    return False


def calculate_registration_age(registration_date: str) -> Dict:
    """
    Calculate age of registered instrument.

    Args:
        registration_date: Date string (YYYY-MM-DD)

    Returns:
        Dictionary with age metrics
    """
    if not registration_date:
        return {
            'years': None,
            'months': None,
            'age_category': 'Unknown'
        }

    try:
        reg_date = datetime.strptime(registration_date, '%Y-%m-%d')
        today = datetime.now()
        delta = today - reg_date

        years = delta.days / 365.25
        months = delta.days / 30.44

        # Categorize
        if years > 50:
            category = 'Historic (50+ years)'
        elif years > 20:
            category = 'Long-standing (20-50 years)'
        elif years > 5:
            category = 'Established (5-20 years)'
        else:
            category = 'Recent (< 5 years)'

        return {
            'years': round(years, 1),
            'months': round(months, 1),
            'days': delta.days,
            'age_category': category
        }

    except ValueError:
        return {
            'years': None,
            'months': None,
            'age_category': 'Invalid Date'
        }


def extract_area_information(instrument: Dict) -> Dict:
    """
    Extract and normalize area/location information.

    Args:
        instrument: Instrument dictionary

    Returns:
        Dictionary with area information
    """
    area_affected = instrument.get('area_affected', '')

    # Try to extract numeric area if present
    area_value = None
    area_unit = None

    if area_affected:
        import re
        # Match patterns like "2.5 acres", "100 sq ft", "0.5 hectares"
        pattern = r'(\d+\.?\d*)\s*(acre|hectare|sq\s?ft|sq\s?m|ha|ac)'
        match = re.search(pattern, area_affected.lower())

        if match:
            area_value = float(match.group(1))
            area_unit = match.group(2).strip()

    return {
        'raw_description': area_affected,
        'area_value': area_value,
        'area_unit': area_unit,
        'affects_entire_property': 'entire' in area_affected.lower() or 'whole' in area_affected.lower(),
        'affects_partial': bool(area_value) or 'portion' in area_affected.lower()
    }
