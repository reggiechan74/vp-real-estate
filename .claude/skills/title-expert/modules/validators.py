#!/usr/bin/env python3
"""
Input Validation Module for Title Analyzer

Validates input data structure, required fields, data types, and logical consistency.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple


def load_and_validate_input(input_path: str) -> Tuple[Dict, List[str]]:
    """
    Load and validate title analysis input data.

    Args:
        input_path: Path to JSON input file

    Returns:
        Tuple of (validated_data, warnings)

    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If validation fails
    """
    # Load JSON
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_file, 'r') as f:
        data = json.load(f)

    # Validate structure
    warnings = []

    # Required top-level fields
    required_fields = ['property_identifier', 'property_address']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")

    # Validate property identifier
    if not data['property_identifier'] or not isinstance(data['property_identifier'], str):
        raise ValueError("property_identifier must be a non-empty string")

    # Validate registered instruments (optional but should be a list)
    if 'registered_instruments' in data:
        if not isinstance(data['registered_instruments'], list):
            raise ValueError("registered_instruments must be a list")

        for idx, instrument in enumerate(data['registered_instruments']):
            warnings.extend(_validate_instrument(instrument, idx))
    else:
        data['registered_instruments'] = []
        warnings.append("No registered instruments provided")

    # Validate encumbrances (optional)
    if 'encumbrances' in data:
        if not isinstance(data['encumbrances'], list):
            raise ValueError("encumbrances must be a list")
    else:
        data['encumbrances'] = []

    # Validate restrictions (optional)
    if 'restrictions' in data:
        if not isinstance(data['restrictions'], list):
            raise ValueError("restrictions must be a list")
    else:
        data['restrictions'] = []

    # Validate defects (optional)
    if 'defects' in data:
        if not isinstance(data['defects'], list):
            raise ValueError("defects must be a list")
    else:
        data['defects'] = []

    # Validate analysis parameters (optional)
    if 'analysis_parameters' not in data:
        data['analysis_parameters'] = {
            'marketability_thresholds': {
                'high_impact': 15.0,  # % value reduction
                'medium_impact': 5.0,
                'low_impact': 0.0
            },
            'critical_instrument_types': [
                'Lien',
                'Mortgage',
                'Court Order',
                'Notice of Security Interest'
            ]
        }

    return data, warnings


def _validate_instrument(instrument: Dict, index: int) -> List[str]:
    """
    Validate a single registered instrument.

    Args:
        instrument: Instrument dictionary
        index: Index in instruments list

    Returns:
        List of warning messages
    """
    warnings = []

    # Check required fields
    required = ['instrument_number', 'instrument_type']
    for field in required:
        if field not in instrument:
            warnings.append(
                f"Instrument {index}: Missing required field '{field}'"
            )

    # Check recommended fields
    recommended = [
        'parties',
        'description',
        'registration_date'
    ]
    for field in recommended:
        if field not in instrument or not instrument[field]:
            warnings.append(
                f"Instrument {index} ({instrument.get('instrument_number', 'Unknown')}): "
                f"Missing recommended field '{field}'"
            )

    # Validate instrument type
    valid_types = [
        'Easement',
        'Covenant',
        'Restriction',
        'Lien',
        'Mortgage',
        'Lease',
        'Right of Way',
        'Encroachment',
        'Notice',
        'Court Order',
        'Building Scheme',
        'Notice of Security Interest',
        'Caution',
        'Certificate of Pending Litigation',
        'Other'
    ]

    if 'instrument_type' in instrument:
        if instrument['instrument_type'] not in valid_types:
            warnings.append(
                f"Instrument {index}: Unknown instrument_type "
                f"'{instrument['instrument_type']}' (will be treated as 'Other')"
            )

    # Validate parties structure
    if 'parties' in instrument:
        if not isinstance(instrument['parties'], dict):
            warnings.append(
                f"Instrument {index}: 'parties' should be a dict with "
                f"'grantor' and 'grantee' keys"
            )
        else:
            if 'grantor' not in instrument['parties']:
                warnings.append(
                    f"Instrument {index}: Missing 'grantor' in parties"
                )
            if 'grantee' not in instrument['parties']:
                warnings.append(
                    f"Instrument {index}: Missing 'grantee' in parties"
                )

    # Validate registration date format (basic check)
    if 'registration_date' in instrument:
        date_str = instrument['registration_date']
        if not isinstance(date_str, str) or len(date_str) < 8:
            warnings.append(
                f"Instrument {index}: registration_date should be in "
                f"YYYY-MM-DD format"
            )

    return warnings


def validate_output_paths(output_md: str = None, output_json: str = None) -> None:
    """
    Validate output file paths are writable.

    Args:
        output_md: Markdown output path
        output_json: JSON output path

    Raises:
        ValueError: If output paths are invalid
    """
    if output_md:
        output_md_path = Path(output_md)
        if output_md_path.exists() and not output_md_path.is_file():
            raise ValueError(f"Output path exists but is not a file: {output_md}")

        # Check parent directory exists
        if not output_md_path.parent.exists():
            raise ValueError(
                f"Output directory does not exist: {output_md_path.parent}"
            )

    if output_json:
        output_json_path = Path(output_json)
        if output_json_path.exists() and not output_json_path.is_file():
            raise ValueError(f"Output path exists but is not a file: {output_json}")

        if not output_json_path.parent.exists():
            raise ValueError(
                f"Output directory does not exist: {output_json_path.parent}"
            )


def validate_instrument_data_quality(instruments: List[Dict]) -> Dict:
    """
    Assess data quality of registered instruments.

    Args:
        instruments: List of instrument dictionaries

    Returns:
        Data quality assessment dictionary
    """
    total = len(instruments)
    if total == 0:
        return {
            'quality_score': 0.0,
            'completeness': 0.0,
            'issues': ['No instruments to analyze']
        }

    # Count fields present
    complete_count = 0
    partial_count = 0
    minimal_count = 0

    for instrument in instruments:
        score = 0
        # Required fields (2 points each)
        if instrument.get('instrument_number'):
            score += 2
        if instrument.get('instrument_type'):
            score += 2

        # Recommended fields (1 point each)
        if instrument.get('parties'):
            score += 1
        if instrument.get('description'):
            score += 1
        if instrument.get('registration_date'):
            score += 1
        if instrument.get('area_affected'):
            score += 1

        # Classify based on score
        if score >= 7:  # All fields
            complete_count += 1
        elif score >= 4:  # Required + some recommended
            partial_count += 1
        else:  # Minimal
            minimal_count += 1

    completeness = (complete_count * 100 + partial_count * 60 + minimal_count * 20) / total

    issues = []
    if complete_count < total * 0.5:
        issues.append(
            f"Only {complete_count}/{total} instruments have complete data"
        )
    if minimal_count > total * 0.2:
        issues.append(
            f"{minimal_count} instruments have minimal data (may affect analysis)"
        )

    return {
        'quality_score': completeness,
        'completeness': f"{completeness:.1f}%",
        'complete': complete_count,
        'partial': partial_count,
        'minimal': minimal_count,
        'total': total,
        'issues': issues
    }
