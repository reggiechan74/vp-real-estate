#!/usr/bin/env python3
"""
Test Suite for Infrastructure Cost Calculator

Tests all modules and integration points.
"""

import sys
import os
import json
import unittest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from modules.validators import (
    validate_input,
    validate_construction_costs,
    validate_depreciation_data
)
from modules.replacement_cost import calculate_replacement_cost_new
from modules.depreciation_analysis import (
    calculate_physical_depreciation,
    calculate_functional_obsolescence,
    calculate_external_obsolescence,
    calculate_total_depreciation
)
from modules.cost_reconciliation import reconcile_with_market
from infrastructure_cost_calculator import calculate_infrastructure_cost


class TestValidators(unittest.TestCase):
    """Test input validation module."""

    def test_validate_construction_costs_valid(self):
        """Test valid construction costs."""
        costs = {
            'materials': 150000,
            'labor': 80000,
            'overhead_percentage': 0.15,
            'profit_percentage': 0.12
        }
        valid, errors = validate_construction_costs(costs)
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)

    def test_validate_construction_costs_missing_field(self):
        """Test missing required field."""
        costs = {
            'materials': 150000,
            'labor': 80000,
            # Missing overhead_percentage and profit_percentage
        }
        valid, errors = validate_construction_costs(costs)
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)

    def test_validate_construction_costs_negative_value(self):
        """Test negative cost values."""
        costs = {
            'materials': -150000,  # Negative
            'labor': 80000,
            'overhead_percentage': 0.15,
            'profit_percentage': 0.12
        }
        valid, errors = validate_construction_costs(costs)
        self.assertFalse(valid)

    def test_validate_depreciation_data_valid(self):
        """Test valid depreciation data."""
        data = {
            'age_years': 15,
            'effective_age_years': 12,
            'economic_life_years': 50,
            'physical_condition': 'Good',
            'functional_obsolescence': 0,
            'external_obsolescence': 0
        }
        valid, errors = validate_depreciation_data(data)
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)

    def test_validate_depreciation_effective_age_exceeds_economic_life(self):
        """Test effective age > economic life."""
        data = {
            'age_years': 15,
            'effective_age_years': 60,  # Exceeds economic life
            'economic_life_years': 50,
            'functional_obsolescence': 0,
            'external_obsolescence': 0
        }
        valid, errors = validate_depreciation_data(data)
        self.assertFalse(valid)


class TestReplacementCost(unittest.TestCase):
    """Test replacement cost calculation module."""

    def test_calculate_rcn_basic(self):
        """Test basic RCN calculation."""
        costs = {
            'materials': 150000,
            'labor': 80000,
            'overhead_percentage': 0.15,
            'profit_percentage': 0.12
        }
        result = calculate_replacement_cost_new(costs)

        # Direct costs
        self.assertEqual(result['materials'], 150000)
        self.assertEqual(result['labor'], 80000)
        self.assertEqual(result['direct_costs'], 230000)

        # Overhead: 230000 * 0.15 = 34500
        self.assertEqual(result['overhead'], 34500)

        # Subtotal: 230000 + 34500 = 264500
        self.assertEqual(result['subtotal'], 264500)

        # Profit: 264500 * 0.12 = 31740
        self.assertEqual(result['profit'], 31740)

        # RCN: 264500 + 31740 = 296240
        self.assertEqual(result['replacement_cost_new'], 296240)

    def test_calculate_rcn_zero_overhead_profit(self):
        """Test RCN with zero overhead and profit."""
        costs = {
            'materials': 100000,
            'labor': 50000,
            'overhead_percentage': 0,
            'profit_percentage': 0
        }
        result = calculate_replacement_cost_new(costs)

        # RCN should equal direct costs
        self.assertEqual(result['replacement_cost_new'], 150000)


class TestDepreciationAnalysis(unittest.TestCase):
    """Test depreciation analysis module."""

    def test_physical_depreciation_age_life(self):
        """Test physical depreciation using age/life method."""
        data = {
            'age_years': 15,
            'effective_age_years': 12,
            'economic_life_years': 50,
            'physical_condition': 'Good'
        }
        rcn = 296240

        result = calculate_physical_depreciation(data, rcn)

        # Depreciation rate: 12 / 50 = 0.24
        self.assertAlmostEqual(result['depreciation_rate'], 0.24, places=4)

        # Physical depreciation: 296240 * 0.24 = 71097.60
        self.assertAlmostEqual(result['physical_depreciation'], 71097.60, places=2)

        # Remaining life: 50 - 12 = 38
        self.assertEqual(result['remaining_life'], 38)

    def test_physical_depreciation_fully_depreciated(self):
        """Test asset at end of economic life."""
        data = {
            'age_years': 50,
            'effective_age_years': 50,
            'economic_life_years': 50,
            'physical_condition': 'Very Poor'
        }
        rcn = 296240

        result = calculate_physical_depreciation(data, rcn)

        # Should be 100% depreciated
        self.assertEqual(result['depreciation_rate'], 1.0)
        self.assertEqual(result['physical_depreciation'], rcn)
        self.assertEqual(result['remaining_life'], 0)

    def test_functional_obsolescence_percentage(self):
        """Test functional obsolescence as percentage."""
        result = calculate_functional_obsolescence(0.10, 296240)

        # 10% obsolescence
        self.assertAlmostEqual(result['obsolescence_rate'], 0.10, places=4)
        self.assertAlmostEqual(result['functional_obsolescence'], 29624, places=2)
        self.assertEqual(result['severity'], 'Moderate')

    def test_functional_obsolescence_dollar_amount(self):
        """Test functional obsolescence as dollar amount."""
        result = calculate_functional_obsolescence(15000, 296240)

        # $15,000 obsolescence
        self.assertEqual(result['functional_obsolescence'], 15000)
        self.assertAlmostEqual(result['obsolescence_rate'], 15000 / 296240, places=4)

    def test_external_obsolescence_none(self):
        """Test zero external obsolescence."""
        result = calculate_external_obsolescence(0, 296240)

        self.assertEqual(result['external_obsolescence'], 0)
        self.assertEqual(result['obsolescence_rate'], 0)
        self.assertEqual(result['severity'], 'None')

    def test_total_depreciation(self):
        """Test total depreciation calculation."""
        physical = {
            'physical_depreciation': 71097.60
        }
        functional = {
            'functional_obsolescence': 15000
        }
        external = {
            'external_obsolescence': 25000
        }
        rcn = 296240

        result = calculate_total_depreciation(physical, functional, external, rcn)

        # Total: 71097.60 + 15000 + 25000 = 111097.60
        self.assertAlmostEqual(result['total_depreciation'], 111097.60, places=2)

        # Depreciated cost: 296240 - 111097.60 = 185142.40
        self.assertAlmostEqual(result['depreciated_replacement_cost'], 185142.40, places=2)

        # Breakdown percentages should sum to 100%
        breakdown = result['breakdown_percentages']
        total_pct = breakdown['physical'] + breakdown['functional'] + breakdown['external']
        self.assertAlmostEqual(total_pct, 100, places=1)


class TestCostReconciliation(unittest.TestCase):
    """Test cost reconciliation module."""

    def test_reconciliation_no_market_data(self):
        """Test reconciliation with no market data."""
        result = reconcile_with_market(225142.40, None, 'Transmission tower')

        self.assertFalse(result['market_approach_available'])
        self.assertEqual(result['reconciled_value'], 225142.40)
        self.assertEqual(result['reconciliation_method'], 'Cost approach only (no market data)')

    def test_reconciliation_with_market_data(self):
        """Test reconciliation with comparable sales."""
        market_data = {
            'comparable_sales': [
                {'sale_price': 180000, 'asset_type': 'Transmission tower'},
                {'sale_price': 195000, 'asset_type': 'Transmission tower'},
                {'sale_price': 172000, 'asset_type': 'Transmission tower'}
            ]
        }

        result = reconcile_with_market(225142.40, market_data, 'Transmission tower')

        self.assertTrue(result['market_approach_available'])
        self.assertEqual(result['relevant_sales_count'], 3)

        # Market median should be 180000
        self.assertEqual(result['market_statistics']['median'], 180000)

        # Cost is higher than market
        self.assertGreater(result['cost_approach_value'], result['market_statistics']['median'])

        # Should be reconciled value between cost and market
        self.assertLess(result['reconciled_value'], result['cost_approach_value'])


class TestIntegration(unittest.TestCase):
    """Test complete calculator integration."""

    def test_transmission_tower_sample(self):
        """Test complete calculation with transmission tower sample."""
        # Load sample data
        sample_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'samples',
            'transmission_tower.json'
        )

        with open(sample_path) as f:
            input_data = json.load(f)

        # Calculate
        results = calculate_infrastructure_cost(input_data, verbose=False)

        # Verify key results
        self.assertEqual(results['rcn_results']['replacement_cost_new'], 296240)
        self.assertAlmostEqual(results['total_depreciation']['total_depreciation'], 71097.60, places=2)
        self.assertAlmostEqual(results['total_depreciation']['depreciated_replacement_cost'], 225142.40, places=2)

        # Should have market reconciliation
        self.assertTrue(results['reconciliation']['market_approach_available'])
        self.assertEqual(results['reconciliation']['relevant_sales_count'], 3)

        # Should have confidence score
        self.assertIn('confidence', results)
        self.assertIn('score', results['confidence'])
        self.assertGreaterEqual(results['confidence']['score'], 0)
        self.assertLessEqual(results['confidence']['score'], 100)

    def test_pipeline_sample(self):
        """Test complete calculation with pipeline sample (no market data)."""
        sample_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'samples',
            'pipeline_segment.json'
        )

        with open(sample_path) as f:
            input_data = json.load(f)

        # Calculate
        results = calculate_infrastructure_cost(input_data, verbose=False)

        # Should have no market reconciliation
        self.assertFalse(results['reconciliation']['market_approach_available'])

        # Reconciled value should equal depreciated cost
        self.assertEqual(
            results['reconciliation']['reconciled_value'],
            results['total_depreciation']['depreciated_replacement_cost']
        )


def run_tests():
    """Run all tests."""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == '__main__':
    print("=" * 70)
    print("INFRASTRUCTURE COST CALCULATOR - TEST SUITE")
    print("=" * 70)
    print()

    run_tests()
