#!/usr/bin/env python3
"""
Unit Tests for Income Approach Land Valuation Calculator
Tests all modules: validators, rent_analysis, cap_rate_selection, income_reconciliation
"""

import unittest
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules import (
    validate_input_data,
    analyze_market_rent,
    select_capitalization_rate,
    reconcile_with_sales_comparison
)

from land_capitalization_calculator import (
    calculate_noi,
    calculate_income_value,
    process_valuation
)


class TestValidators(unittest.TestCase):
    """Test input validation module."""

    def setUp(self):
        """Set up valid test data."""
        self.valid_data = {
            "site_type": "Test Site",
            "land_rent": {
                "annual_rent": 12000,
                "lease_term": 20,
                "escalations": "3% per 5 years"
            },
            "market_data": {
                "comparable_rents": [
                    {"location": "Comp 1", "annual_rent": 10000},
                    {"location": "Comp 2", "annual_rent": 14000}
                ],
                "cap_rate_range": {"low": 0.06, "high": 0.09},
                "comparable_sales": [
                    {"sale_price": 150000, "noi": 10500}
                ]
            },
            "operating_expenses": {
                "property_tax": 2000,
                "insurance": 800,
                "maintenance": 1200
            }
        }

    def test_valid_input(self):
        """Test that valid input passes validation."""
        result = validate_input_data(self.valid_data)
        self.assertEqual(result, self.valid_data)

    def test_missing_top_level_field(self):
        """Test that missing top-level field raises error."""
        invalid_data = self.valid_data.copy()
        del invalid_data['site_type']

        with self.assertRaises(ValueError) as context:
            validate_input_data(invalid_data)

        self.assertIn("Missing required field: site_type", str(context.exception))

    def test_invalid_annual_rent(self):
        """Test that invalid annual_rent raises error."""
        invalid_data = self.valid_data.copy()
        invalid_data['land_rent']['annual_rent'] = -1000

        with self.assertRaises(ValueError) as context:
            validate_input_data(invalid_data)

        self.assertIn("annual_rent must be positive", str(context.exception))

    def test_invalid_cap_rate_range(self):
        """Test that invalid cap rate range raises error."""
        invalid_data = self.valid_data.copy()
        invalid_data['market_data']['cap_rate_range']['low'] = 0.09
        invalid_data['market_data']['cap_rate_range']['high'] = 0.06

        with self.assertRaises(ValueError) as context:
            validate_input_data(invalid_data)

        self.assertIn("low must be less than high", str(context.exception))

    def test_empty_comparable_rents(self):
        """Test that empty comparable_rents raises error."""
        invalid_data = self.valid_data.copy()
        invalid_data['market_data']['comparable_rents'] = []

        with self.assertRaises(ValueError) as context:
            validate_input_data(invalid_data)

        self.assertIn("must contain at least one comparable", str(context.exception))


class TestRentAnalysis(unittest.TestCase):
    """Test market rent analysis module."""

    def setUp(self):
        """Set up test data."""
        self.data = {
            "land_rent": {
                "annual_rent": 12000
            },
            "market_data": {
                "comparable_rents": [
                    {"location": "Comp 1", "annual_rent": 10000},
                    {"location": "Comp 2", "annual_rent": 14000},
                    {"location": "Comp 3", "annual_rent": 11500},
                    {"location": "Comp 4", "annual_rent": 13200}
                ]
            }
        }

    def test_rent_statistics(self):
        """Test that rent statistics are calculated correctly."""
        result = analyze_market_rent(self.data)

        stats = result['rent_statistics']
        self.assertEqual(stats['count'], 4)
        self.assertEqual(stats['min'], 10000)
        self.assertEqual(stats['max'], 14000)
        self.assertEqual(stats['median'], 12350)  # (11500 + 13200) / 2

    def test_subject_within_range(self):
        """Test that subject rent within range is used."""
        result = analyze_market_rent(self.data)

        self.assertEqual(result['concluded_market_rent'], 12000)
        self.assertIn("within market range", result['conclusion_method'])

    def test_subject_outside_range(self):
        """Test that subject rent outside range uses median."""
        self.data['land_rent']['annual_rent'] = 20000  # Way above range

        result = analyze_market_rent(self.data)

        self.assertEqual(result['concluded_market_rent'], 12350)  # Median
        self.assertIn("outside market range", result['conclusion_method'])


class TestCapRateSelection(unittest.TestCase):
    """Test capitalization rate selection module."""

    def setUp(self):
        """Set up test data."""
        self.data = {
            "market_data": {
                "cap_rate_range": {"low": 0.06, "high": 0.09},
                "comparable_sales": [
                    {"location": "Sale 1", "sale_price": 150000, "noi": 10500},
                    {"location": "Sale 2", "sale_price": 180000, "noi": 13500},
                    {"location": "Sale 3", "sale_price": 165000, "noi": 12000}
                ]
            }
        }

    def test_market_extraction(self):
        """Test market extraction cap rates."""
        result = select_capitalization_rate(self.data)

        extraction = result['market_extraction']
        self.assertEqual(len(extraction['comparable_sales']), 3)

        # Check calculated cap rates
        sale1_cap = extraction['comparable_sales'][0]['cap_rate']
        self.assertAlmostEqual(sale1_cap, 10500 / 150000, places=4)

    def test_concluded_cap_rate_within_range(self):
        """Test that concluded cap rate is within market range."""
        result = select_capitalization_rate(self.data)

        concluded = result['concluded_cap_rate']
        self.assertGreaterEqual(concluded, 0.06)
        self.assertLessEqual(concluded, 0.09)

    def test_band_of_investment(self):
        """Test band of investment calculation."""
        self.data['market_data']['financing'] = {
            'ltv': 0.75,
            'debt_yield': 0.055,
            'equity_yield': 0.12
        }

        result = select_capitalization_rate(self.data)

        band = result['band_of_investment']
        self.assertIsNotNone(band)

        # Manual calculation: (0.75 * 0.055) + (0.25 * 0.12) = 0.07125
        expected = (0.75 * 0.055) + (0.25 * 0.12)
        self.assertAlmostEqual(band['calculated_cap_rate'], expected, places=4)

    def test_buildup_method(self):
        """Test buildup method calculation."""
        self.data['market_data']['risk_components'] = {
            'risk_free_rate': 0.04,
            'liquidity_premium': 0.01,
            'inflation_premium': 0.02,
            'business_risk': 0.02
        }

        result = select_capitalization_rate(self.data)

        buildup = result['buildup_method']
        self.assertIsNotNone(buildup)

        # Manual calculation: 0.04 + 0.01 + 0.02 + 0.02 = 0.09
        expected = 0.04 + 0.01 + 0.02 + 0.02
        self.assertAlmostEqual(buildup['calculated_cap_rate'], expected, places=4)


class TestNOICalculation(unittest.TestCase):
    """Test NOI calculation."""

    def test_noi_calculation(self):
        """Test that NOI is calculated correctly."""
        operating_expenses = {
            'property_tax': 2000,
            'insurance': 800,
            'maintenance': 1200
        }

        result = calculate_noi(12000, operating_expenses)

        self.assertEqual(result['gross_income'], 12000)
        self.assertEqual(result['total_operating_expenses'], 4000)
        self.assertEqual(result['noi'], 8000)


class TestIncomeValue(unittest.TestCase):
    """Test income value calculation."""

    def test_income_value_calculation(self):
        """Test that income value is calculated correctly."""
        value = calculate_income_value(8000, 0.0727)

        # 8000 / 0.0727 ≈ 110,041
        self.assertAlmostEqual(value, 110041.27, places=1)

    def test_zero_cap_rate_raises_error(self):
        """Test that zero cap rate raises error."""
        with self.assertRaises(ValueError):
            calculate_income_value(8000, 0.0)

    def test_negative_cap_rate_raises_error(self):
        """Test that negative cap rate raises error."""
        with self.assertRaises(ValueError):
            calculate_income_value(8000, -0.05)


class TestReconciliation(unittest.TestCase):
    """Test reconciliation module."""

    def setUp(self):
        """Set up test data."""
        self.data = {
            "market_data": {
                "sales_comparison_value": 160000,
                "comparable_sales": []
            }
        }

    def test_reconciliation_within_10_percent(self):
        """Test reconciliation when values within 10%."""
        # Income value: 110,000, Sales: 120,000 (9.1% difference)
        result = reconcile_with_sales_comparison(8000, 0.0727, 110000, {
            "market_data": {"sales_comparison_value": 120000}
        })

        recon = result['reconciliation']
        # Should use income approach
        self.assertEqual(recon['final_value'], 110000)

    def test_reconciliation_10_to_20_percent(self):
        """Test reconciliation when values 10-20% apart."""
        # Income value: 110,000, Sales: 140,000 (27.3% difference on sales base)
        # Actually (140000-110000)/140000 = 21.4%, but our code uses sales as denominator
        result = reconcile_with_sales_comparison(8000, 0.0727, 110000, {
            "market_data": {"sales_comparison_value": 135000}
        })

        recon = result['reconciliation']
        # Should use average: (110000 + 135000) / 2 = 122500
        self.assertEqual(recon['final_value'], 122500)

    def test_sensitivity_analysis(self):
        """Test that sensitivity analysis is generated."""
        result = reconcile_with_sales_comparison(8000, 0.0727, 110041.27, self.data)

        sensitivity = result['sensitivity_analysis']
        self.assertEqual(len(sensitivity), 5)  # -0.5%, -0.25%, 0%, +0.25%, +0.5%

        # Check base case (0% adjustment)
        base_case = [s for s in sensitivity if s['cap_rate_adjustment'] == 0][0]
        self.assertAlmostEqual(base_case['value'], 110041.27, places=1)


class TestEndToEnd(unittest.TestCase):
    """End-to-end integration tests."""

    def test_full_valuation_process(self):
        """Test complete valuation workflow."""
        # Load sample input
        sample_file = os.path.join(
            os.path.dirname(__file__),
            '../samples/simple_land_lease_input.json'
        )

        with open(sample_file, 'r') as f:
            data = json.load(f)

        validated_data = validate_input_data(data)
        results = process_valuation(validated_data, verbose=False)

        # Check that all key components are present
        self.assertIn('market_rent_analysis', results)
        self.assertIn('cap_rate_analysis', results)
        self.assertIn('noi_calculation', results)
        self.assertIn('income_approach_value', results)
        self.assertIn('final_concluded_value', results)

        # Check that values are reasonable
        self.assertGreater(results['final_concluded_value'], 0)
        self.assertGreater(results['income_approach_value'], 0)


def run_tests():
    """Run all tests with detailed output."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestValidators))
    suite.addTests(loader.loadTestsFromTestCase(TestRentAnalysis))
    suite.addTests(loader.loadTestsFromTestCase(TestCapRateSelection))
    suite.addTests(loader.loadTestsFromTestCase(TestNOICalculation))
    suite.addTests(loader.loadTestsFromTestCase(TestIncomeValue))
    suite.addTests(loader.loadTestsFromTestCase(TestReconciliation))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEnd))

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code)
