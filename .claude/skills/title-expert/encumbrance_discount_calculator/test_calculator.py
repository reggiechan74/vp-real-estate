#!/usr/bin/env python3
"""
Test script for encumbrance discount calculator
Validates all calculation methods and output formats
"""

import sys
import os
import json

# Add parent to path
sys.path.insert(0, os.path.dirname(__file__))

from encumbrance_discount_calculator import run_encumbrance_analysis


def test_simple_drainage():
    """Test simple drainage easement calculation."""
    print("\n" + "="*80)
    print("TEST 1: Simple Drainage Easement")
    print("="*80)

    input_data = {
        "property": {
            "pin": "TEST-001",
            "address": "Test Property 1",
            "total_area_acres": 10.0,
            "unencumbered_value": 500000
        },
        "encumbrances": [
            {
                "type": "drainage_easement",
                "area_acres": 0.8,
                "impact_percentage": 5
            }
        ]
    }

    results = run_encumbrance_analysis(input_data, verbose=False)

    # Validate results (use abs for floating point comparison)
    assert abs(results['cumulative_discount']['cumulative_discount_percentage'] - 5.0) < 0.01
    assert abs(results['individual_discounts'][0]['discount_amount'] - 2000.0) < 0.01
    assert results['final_value'] > 450000  # After marketability discount

    print(f"✓ Cumulative discount: {results['cumulative_discount']['cumulative_discount_percentage']:.2f}%")
    print(f"✓ Final value: ${results['final_value']:,.2f}")
    print("✓ PASSED")


def test_multiple_encumbrances():
    """Test multiplicative method with multiple encumbrances."""
    print("\n" + "="*80)
    print("TEST 2: Multiple Encumbrances (Multiplicative Method)")
    print("="*80)

    input_data = {
        "property": {
            "pin": "TEST-002",
            "address": "Test Property 2",
            "total_area_acres": 100.0,
            "unencumbered_value": 1200000
        },
        "encumbrances": [
            {"type": "transmission_easement", "area_acres": 5.0, "impact_percentage": 10},
            {"type": "pipeline_easement", "area_acres": 3.0, "impact_percentage": 15},
            {"type": "drainage_easement", "area_acres": 2.0, "impact_percentage": 5}
        ]
    }

    results = run_encumbrance_analysis(input_data, method='multiplicative', verbose=False)

    # Validate multiplicative calculation: (1-0.10) × (1-0.15) × (1-0.05) = 0.72675
    # Cumulative discount: 1 - 0.72675 = 0.27325 = 27.325%
    expected_discount = 27.32  # Rounded

    assert abs(results['cumulative_discount']['cumulative_discount_percentage'] - expected_discount) < 0.1

    print(f"✓ Expected discount: ~{expected_discount}%")
    print(f"✓ Actual discount: {results['cumulative_discount']['cumulative_discount_percentage']:.2f}%")
    print(f"✓ Final value: ${results['final_value']:,.2f}")
    print("✓ PASSED")


def test_additive_method():
    """Test additive method calculation."""
    print("\n" + "="*80)
    print("TEST 3: Additive Method Comparison")
    print("="*80)

    input_data = {
        "property": {
            "pin": "TEST-003",
            "address": "Test Property 3",
            "total_area_acres": 100.0,
            "unencumbered_value": 1000000
        },
        "encumbrances": [
            {"type": "transmission_easement", "area_acres": 5.0, "impact_percentage": 10},
            {"type": "pipeline_easement", "area_acres": 3.0, "impact_percentage": 15}
        ]
    }

    # Test multiplicative
    results_mult = run_encumbrance_analysis(input_data, method='multiplicative', verbose=False)

    # Test additive
    results_add = run_encumbrance_analysis(input_data, method='additive', verbose=False)

    # Additive should be higher discount: 10% + 15% = 25%
    # Multiplicative should be lower: (1-0.10) × (1-0.15) = 0.765 → 23.5% discount

    assert results_add['cumulative_discount']['cumulative_discount_percentage'] == 25.0
    assert abs(results_mult['cumulative_discount']['cumulative_discount_percentage'] - 23.5) < 0.1

    print(f"✓ Additive discount: {results_add['cumulative_discount']['cumulative_discount_percentage']:.2f}%")
    print(f"✓ Multiplicative discount: {results_mult['cumulative_discount']['cumulative_discount_percentage']:.2f}%")
    print("✓ PASSED")


def test_agricultural_impacts():
    """Test agricultural income capitalization."""
    print("\n" + "="*80)
    print("TEST 4: Agricultural Income Capitalization")
    print("="*80)

    input_data = {
        "property": {
            "pin": "TEST-004",
            "address": "Test Farm",
            "total_area_acres": 100.0,
            "unencumbered_value": 1200000
        },
        "encumbrances": [
            {"type": "transmission_easement", "area_acres": 5.0, "impact_percentage": 10}
        ],
        "agricultural_impacts": {
            "annual_crop_loss": 5000,
            "cap_rate": 0.05,
            "operational_inefficiency_pct": 10
        }
    }

    results = run_encumbrance_analysis(input_data, verbose=False)

    # Validate agricultural capitalization
    ag_analysis = results['agricultural_analysis']

    # $5,000 / 0.05 = $100,000 capitalized value
    assert ag_analysis['capitalized_value'] == 100000

    # 10% inefficiency on $100,000 = $10,000
    assert ag_analysis['inefficiency_adjustment'] == 10000

    # Total = $110,000
    assert ag_analysis['total_impact'] == 110000

    print(f"✓ Annual crop loss: ${ag_analysis['annual_crop_loss']:,.2f}")
    print(f"✓ Capitalized value: ${ag_analysis['capitalized_value']:,.2f}")
    print(f"✓ Total impact: ${ag_analysis['total_impact']:,.2f}")
    print("✓ PASSED")


def test_marketability_discount():
    """Test marketability discount calculations."""
    print("\n" + "="*80)
    print("TEST 5: Marketability Discount (Conservative vs Optimistic)")
    print("="*80)

    input_data = {
        "property": {
            "pin": "TEST-005",
            "address": "Test Property 5",
            "total_area_acres": 100.0,
            "unencumbered_value": 1000000
        },
        "encumbrances": [
            {"type": "transmission_easement", "area_acres": 10.0, "impact_percentage": 12}
        ]
    }

    # Test conservative (higher discount)
    results_cons = run_encumbrance_analysis(
        input_data,
        marketability_method='conservative',
        verbose=False
    )

    # Test optimistic (lower discount)
    results_opt = run_encumbrance_analysis(
        input_data,
        marketability_method='optimistic',
        verbose=False
    )

    # Conservative should have higher discount
    assert results_cons['marketability_discount']['discount_percentage'] > \
           results_opt['marketability_discount']['discount_percentage']

    # Conservative should have lower final value
    assert results_cons['final_value'] < results_opt['final_value']

    print(f"✓ Conservative discount: {results_cons['marketability_discount']['discount_percentage']:.2f}%")
    print(f"✓ Optimistic discount: {results_opt['marketability_discount']['discount_percentage']:.2f}%")
    print(f"✓ Conservative final: ${results_cons['final_value']:,.2f}")
    print(f"✓ Optimistic final: ${results_opt['final_value']:,.2f}")
    print("✓ PASSED")


def test_development_potential():
    """Test development potential analysis."""
    print("\n" + "="*80)
    print("TEST 6: Development Potential Analysis")
    print("="*80)

    input_data = {
        "property": {
            "pin": "TEST-006",
            "address": "Test Development Site",
            "total_area_acres": 50.0,
            "unencumbered_value": 800000,
            "zoning": "Residential",
            "highest_best_use": "Residential subdivision (5 lots)"
        },
        "encumbrances": [
            {"type": "conservation_easement", "area_acres": 30.0, "impact_percentage": 40}
        ]
    }

    results = run_encumbrance_analysis(input_data, verbose=False)

    dev_potential = results['development_potential']

    # Validate development analysis
    assert dev_potential['total_area_acres'] == 50.0
    assert dev_potential['encumbered_area_acres'] == 30.0
    assert dev_potential['encumbered_ratio'] == 0.6  # 30/50 = 60%

    # Conservation easement should significantly restrict buildable area
    assert dev_potential['restricted_buildable_area_acres'] == 30.0
    assert dev_potential['buildable_ratio'] < 0.5  # Less than 50% buildable

    print(f"✓ Total area: {dev_potential['total_area_acres']:.2f} acres")
    print(f"✓ Encumbered: {dev_potential['encumbered_ratio']*100:.1f}%")
    print(f"✓ Buildable ratio: {dev_potential['buildable_ratio']*100:.1f}%")
    print(f"✓ Subdivision impact: {dev_potential['subdivision_impact']['subdivision_feasibility']}")
    print("✓ PASSED")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*80)
    print("ENCUMBRANCE DISCOUNT CALCULATOR - TEST SUITE")
    print("="*80)

    tests = [
        test_simple_drainage,
        test_multiple_encumbrances,
        test_additive_method,
        test_agricultural_impacts,
        test_marketability_discount,
        test_development_potential
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ ERROR: {e}")
            failed += 1

    print("\n" + "="*80)
    print("TEST RESULTS")
    print("="*80)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n✓ ALL TESTS PASSED")
        return 0
    else:
        print(f"\n✗ {failed} TEST(S) FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
