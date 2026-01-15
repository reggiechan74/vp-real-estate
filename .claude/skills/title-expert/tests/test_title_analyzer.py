#!/usr/bin/env python3
"""
Unit tests for Title Analyzer

Tests core functionality of all modules.
"""

import sys
import json
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'modules'))

from validators import load_and_validate_input, validate_instrument_data_quality
from title_parsing import parse_registered_instruments, classify_instrument
from encumbrance_analysis import analyze_encumbrances, assess_encumbrance_impact
from registration_validation import validate_registration, detect_instrument_defects
from marketability_assessment import assess_marketability, calculate_value_impact


def test_validators():
    """Test input validation."""
    print("Testing validators...")

    # Create minimal test input
    test_input = {
        "property_identifier": "TEST-001",
        "property_address": "123 Test Street",
        "registered_instruments": []
    }

    # Save to temp file
    temp_file = Path(__file__).parent / "temp_test_input.json"
    with open(temp_file, 'w') as f:
        json.dump(test_input, f)

    try:
        data, warnings = load_and_validate_input(str(temp_file))
        assert data['property_identifier'] == "TEST-001"
        assert 'analysis_parameters' in data  # Should be added by default
        print("  ✓ Validators passed")
    finally:
        temp_file.unlink()


def test_title_parsing():
    """Test title parsing."""
    print("Testing title parsing...")

    instruments = [
        {
            "instrument_number": "A1",
            "instrument_type": "Easement",
            "registration_date": "2020-01-01"
        },
        {
            "instrument_number": "A2",
            "instrument_type": "Lien",
            "registration_date": "2021-01-01"
        }
    ]

    result = parse_registered_instruments(instruments)

    assert result['summary']['total_instruments'] == 2
    assert 'Easement' in result['by_type']
    assert len(result['critical']) >= 1  # Lien should be critical
    print("  ✓ Title parsing passed")


def test_encumbrance_analysis():
    """Test encumbrance analysis."""
    print("Testing encumbrance analysis...")

    instruments = [
        {
            "instrument_number": "L1",
            "instrument_type": "Lien",
            "classified_type": "Lien",
            "description": "Construction lien for unpaid work",
            "registration_date": "2024-01-01",
            "priority_number": 1
        }
    ]

    result = analyze_encumbrances(instruments, [], [])

    assert result['summary']['total'] > 0
    assert len(result['critical_issues']) > 0
    print("  ✓ Encumbrance analysis passed")


def test_registration_validation():
    """Test registration validation."""
    print("Testing registration validation...")

    # Good instrument
    good_inst = {
        "instrument_number": "AB123456",
        "instrument_type": "Easement",
        "parties": {
            "grantor": "John Doe",
            "grantee": "Utility Co"
        },
        "description": "Utility easement for power transmission",
        "registration_date": "2020-01-15"
    }

    # Bad instrument (missing grantor)
    bad_inst = {
        "instrument_number": "AB999999",
        "instrument_type": "Lien",
        "parties": {
            "grantee": "Contractor"
        },
        "registration_date": "2024-01-01"
    }

    defects_good = detect_instrument_defects(good_inst, 0)
    defects_bad = detect_instrument_defects(bad_inst, 1)

    assert len(defects_bad) > len(defects_good)  # Bad instrument should have more defects
    print("  ✓ Registration validation passed")


def test_marketability_assessment():
    """Test marketability assessment."""
    print("Testing marketability assessment...")

    # Create mock analysis results
    encumbrance_analysis = {
        'summary': {
            'total': 2,
            'by_severity': {'MEDIUM': 2},
            'action_required_count': 0,
            'average_value_impact': 5.0
        },
        'critical_issues': [],
        'high_issues': [],
        'encumbrances': []
    }

    validation_results = {
        'validity': {
            'status': 'VALID',
            'marketable': True
        },
        'summary': {
            'total_defects': 0,
            'critical_defects': 0
        }
    }

    property_data = {
        'property_identifier': 'TEST',
        'property_address': 'Test Address'
    }

    result = assess_marketability(
        encumbrance_analysis,
        validation_results,
        property_data
    )

    assert 'overall_score' in result
    assert 'rating' in result
    assert result['overall_score'] >= 0 and result['overall_score'] <= 100
    print("  ✓ Marketability assessment passed")


def test_value_impact():
    """Test value impact calculation."""
    print("Testing value impact calculation...")

    marketability = {
        'rating': 'GOOD',
        'overall_score': 75.0
    }

    encumbrance_analysis = {
        'summary': {
            'average_value_impact': 5.0
        }
    }

    result = calculate_value_impact(marketability, encumbrance_analysis)

    assert 'min_discount_pct' in result
    assert 'max_discount_pct' in result
    assert 'likely_discount_pct' in result
    assert result['min_discount_pct'] <= result['likely_discount_pct'] <= result['max_discount_pct']
    print("  ✓ Value impact calculation passed")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("Running Title Analyzer Tests")
    print("="*60 + "\n")

    try:
        test_validators()
        test_title_parsing()
        test_encumbrance_analysis()
        test_registration_validation()
        test_marketability_assessment()
        test_value_impact()

        print("\n" + "="*60)
        print("All tests passed! ✓")
        print("="*60 + "\n")
        return 0

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
