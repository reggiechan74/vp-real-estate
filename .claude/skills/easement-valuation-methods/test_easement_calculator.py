#!/usr/bin/env python3
"""
Comprehensive Test Suite for Easement Valuation Calculator v2.0

Tests all enhancements:
- TCE rate-of-return method
- Fixed income capitalization (productivity_loss_pct)
- Dynamic reconciliation weights
- Sensitivity analysis

Author: Claude Code
Created: 2025-11-17
"""

import unittest
import json
from pathlib import Path
from hydro_easement_calculator import HydroEasementCalculator


class TestPercentageOfFeeMethod(unittest.TestCase):
    """Test suite for Percentage of Fee Method"""

    def test_500kv_transmission_base_percentage(self):
        calc = HydroEasementCalculator({
            "property": {"total_acres": 100, "fee_simple_value": 1000000},
            "easement": {"voltage_kv": 500, "area_acres": 5},
            "market_parameters": {"cap_rate": 0.10}
        })
        self.assertEqual(calc.get_base_percentage(), 22.5)
        calc = HydroEasementCalculator({
            "property": {"total_acres": 100, "fee_simple_value": 1000000},
            "easement": {"voltage_kv": 500, "area_acres": 5},
            "market_parameters": {"cap_rate": 0.10}
        })
        self.assertEqual(calc.get_base_percentage(), 22.5)
        calc = HydroEasementCalculator({
            "property": {"total_acres": 100, "fee_simple_value": 1000000},
            "easement": {"voltage_kv": 500, "area_acres": 5},
            "market_parameters": {"cap_rate": 0.10}
        })
        self.assertEqual(calc.get_base_percentage(), 22.5)
        calc = HydroEasementCalculator({
            "property": {"total_acres": 100, "fee_simple_value": 1000000},
            "easement": {"voltage_kv": 500, "area_acres": 5},
            "market_parameters": {"cap_rate": 0.10}
        })
        self.assertEqual(calc.get_base_percentage(), 22.5)
        calc = HydroEasementCalculator({
            "property": {"total_acres": 100, "fee_simple_value": 1000000},
            "easement": {"voltage_kv": 500, "area_acres": 5},
            "market_parameters": {"cap_rate": 0.10}
        })
        self.assertEqual(calc.get_base_percentage(), 22.5)
        calc = HydroEasementCalculator({
            "property": {"total_acres": 100, "fee_simple_value": 1000000},
            "easement": {"voltage_kv": 500, "area_acres": 5},
            "market_parameters": {"cap_rate": 0.10}
        })
        self.assertEqual(calc.get_base_percentage(), 22.5)
        calc = HydroEasementCalculator({
            "property": {"total_acres": 100, "fee_simple_value": 1000000},
            "easement": {"voltage_kv": 500, "area_acres": 5},
            "market_parameters": {"cap_rate": 0.10}
        })
        self.assertEqual(calc.get_base_percentage(), 22.5)
        calc = HydroEasementCalculator({
            "property": {"total_acres": 100, "fee_simple_value": 1000000},
            "easement": {"voltage_kv": 500, "area_acres": 5},
            "market_parameters": {"cap_rate": 0.10}
        })
        self.assertEqual(calc.get_base_percentage(), 22.5)
    def test_230kv_transmission_base_percentage(self):
        """Test 230kV gets 17.5% base percentage"""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 1000000},
            'easement': {'type': 'utility_transmission', 'voltage_kv': 230, 'area_acres': 10},
            'market_parameters': {'cap_rate': 0.07}
        })
        self.assertEqual(calc._get_transmission_percentage(230), 17.5)

    def test_width_adjustment_very_wide(self):
        """Test width adjustment for 100m+ corridor"""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 1000000},
            'easement': {'type': 'utility_transmission', 'voltage_kv': 500, 'area_acres': 10, 'width_meters': 100},
            'market_parameters': {'cap_rate': 0.07}
        })
        self.assertEqual(calc._calculate_width_adjustment(), 3.0)

    def test_restriction_adjustment_multiple(self):
        """Test restriction adjustment with multiple restrictions"""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 1000000},
            'easement': {
                'type': 'utility_transmission',
                'voltage_kv': 230,
                'area_acres': 10,
                'restrictions': ['no_buildings', 'no_trees', 'height_restrictions']
            },
            'market_parameters': {'cap_rate': 0.07}
        })
        # no_buildings (2.0) + no_trees (1.5) + height_restrictions (1.0) = 4.5
        self.assertEqual(calc._calculate_restriction_adjustment(), 4.5)

    def test_percentage_clamps_to_max_35(self):
        """Test final percentage clamped to 35% maximum"""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 1000000},
            'easement': {
                'type': 'utility_transmission',
                'voltage_kv': 500,  # 22.5% base
                'area_acres': 10,
                'width_meters': 100,  # +3%
                'restrictions': ['no_buildings', 'no_trees', 'height_restrictions', 'access_limitations', 'excavation_prohibited'],  # +5% (capped)
                'hbu_impact': 'precludes_development'  # +8%
            },
            'market_parameters': {'cap_rate': 0.07}
        })
        result = calc.calculate_percentage_of_fee()
        # 22.5 + 3 + 5 + 8 = 38.5, clamped to 35
        self.assertEqual(result['final_percentage'], 35.0)


class TestIncomeCapitalizationMethod(unittest.TestCase):
    """Test suite for Income Capitalization Method"""

    def test_productivity_loss_calculation(self):
        """Test productivity_loss_pct parameter (FIXED in v2.0)"""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 1200000},
            'easement': {
                'type': 'utility_transmission',
                'voltage_kv': 230,
                'area_acres': 15,
                'productivity_loss_pct': 0.20  # 20% loss
            },
            'market_parameters': {'cap_rate': 0.045, 'annual_rent_per_acre': 300}
        })
        result = calc.calculate_income_capitalization()

        # Annual rent: $300 × 15 acres = $4,500
        # Loss: $4,500 × 20% = $900
        # Capitalized: $900 ÷ 4.5% = $20,000
        self.assertAlmostEqual(result['annual_rent_gross'], 4500, places=0)
        self.assertAlmostEqual(result['annual_rent_loss'], 900, places=0)
        self.assertAlmostEqual(result['easement_value'], 20000, places=0)

    def test_backward_compatibility_easement_rent_factor(self):
        """Test backward compatibility with old easement_rent_factor parameter"""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 1200000},
            'easement': {
                'type': 'utility_transmission',
                'voltage_kv': 230,
                'area_acres': 15,
                'easement_rent_factor': 0.20  # Old parameter name
            },
            'market_parameters': {'cap_rate': 0.045, 'annual_rent_per_acre': 300}
        })
        result = calc.calculate_income_capitalization()

        # Should still work with old parameter
        self.assertAlmostEqual(result['easement_value'], 20000, places=0)


class TestTCERateOfReturnMethod(unittest.TestCase):
    """Test suite for TCE Rate-of-Return Method (NEW in v2.0)"""

    def test_tce_detection_explicit(self):
        """Test TCE detection with term='tce'"""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 2, 'fee_simple_value': 400000},
            'easement': {'type': 'access', 'area_acres': 2, 'term': 'tce', 'duration_days': 90},
            'market_parameters': {'cap_rate': 0.10}
        })
        self.assertTrue(calc.is_temporary_construction_easement())

    def test_tce_detection_temporary_short_duration(self):
        """Test TCE detection with term='temporary' and duration < 3 years"""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 2, 'fee_simple_value': 400000},
            'easement': {'type': 'access', 'area_acres': 2, 'term': 'temporary', 'duration_days': 180},
            'market_parameters': {'cap_rate': 0.10}
        })
        self.assertTrue(calc.is_temporary_construction_easement())

    def test_tce_industrial_90_days(self):
        """Test TCE calculation for 90-day industrial easement (from SKILL.md)"""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 2, 'fee_simple_value': 400000},
            'easement': {
                'type': 'access',
                'area_acres': 2,
                'term': 'tce',
                'duration_days': 90,
                'restoration_costs': 15000,
                'business_losses': 8000
            },
            'market_parameters': {'cap_rate': 0.10, 'tce_annual_rate': 0.10}
        })
        result = calc.calculate_tce_rate_of_return()

        # Expected: $400,000 × 10% × (90÷365) = $9,863
        self.assertAlmostEqual(result['rental_value'], 9863, places=0)
        self.assertEqual(result['restoration_costs'], 15000)
        self.assertEqual(result['business_losses'], 8000)
        # Total: $9,863 + $15,000 + $8,000 = $32,863
        self.assertAlmostEqual(result['total_tce_value'], 32863, places=0)

    def test_tce_agricultural_180_days(self):
        """Test TCE calculation for 180-day agricultural easement (from SKILL.md)"""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 1000000},
            'easement': {
                'type': 'access',
                'area_acres': 5,
                'term': 'tce',
                'duration_days': 180,
                'restoration_costs': 3000,
                'business_losses': 1500
            },
            'market_parameters': {'cap_rate': 0.07, 'tce_annual_rate': 0.06}  # Conservative 6%
        })
        result = calc.calculate_tce_rate_of_return()

        # Land value per acre: $1,000,000 ÷ 100 = $10,000
        # Affected value: $10,000 × 5 acres = $50,000
        # Rental: $50,000 × 6% × (180÷365) = $1,479
        self.assertAlmostEqual(result['affected_land_value'], 50000, places=0)
        self.assertAlmostEqual(result['rental_value'], 1479, places=0)
        # Total: $1,479 + $3,000 + $1,500 = $5,979
        self.assertAlmostEqual(result['total_tce_value'], 5979, places=0)

    def test_tce_duration_category_short(self):
        """Test duration categorization: < 30 days = short"""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 2, 'fee_simple_value': 400000},
            'easement': {'type': 'access', 'area_acres': 2, 'term': 'tce', 'duration_days': 15},
            'market_parameters': {'cap_rate': 0.10}
        })
        result = calc.calculate_tce_rate_of_return()
        self.assertEqual(result['duration_category'], 'short')

    def test_tce_duration_category_medium(self):
        """Test duration categorization: 30-365 days = medium"""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 2, 'fee_simple_value': 400000},
            'easement': {'type': 'access', 'area_acres': 2, 'term': 'tce', 'duration_days': 180},
            'market_parameters': {'cap_rate': 0.10}
        })
        result = calc.calculate_tce_rate_of_return()
        self.assertEqual(result['duration_category'], 'medium')

    def test_tce_duration_category_long(self):
        """Test duration categorization: > 365 days = long"""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 2, 'fee_simple_value': 400000},
            'easement': {'type': 'access', 'area_acres': 2, 'term': 'tce', 'duration_days': 730},
            'market_parameters': {'cap_rate': 0.10}
        })
        result = calc.calculate_tce_rate_of_return()
        self.assertEqual(result['duration_category'], 'long')


class TestDynamicReconciliationWeights(unittest.TestCase):
    """Test suite for Dynamic Reconciliation Weights (NEW in v2.0)"""

    def test_telecom_weights_income_dominant(self):
        """Test telecom easements favor income approach (50%)"""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 1, 'fee_simple_value': 500000},
            'easement': {'type': 'telecom', 'area_acres': 0.1},
            'market_parameters': {'cap_rate': 0.07}
        })
        weights = calc._get_dynamic_weights()
        self.assertEqual(weights['income_capitalization'], 0.50)
        self.assertEqual(weights['percentage_of_fee'], 0.30)

    def test_transmission_weights_percentage_dominant(self):
        """Test transmission easements favor percentage of fee (50%)"""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 1200000},
            'easement': {'type': 'utility_transmission', 'voltage_kv': 230, 'area_acres': 15},
            'market_parameters': {'cap_rate': 0.045}
        })
        weights = calc._get_dynamic_weights()
        self.assertEqual(weights['percentage_of_fee'], 0.50)
        self.assertEqual(weights['income_capitalization'], 0.30)

    def test_user_override_weights(self):
        """Test user can override default weights"""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 1200000},
            'easement': {'type': 'utility_transmission', 'voltage_kv': 230, 'area_acres': 15},
            'market_parameters': {
                'cap_rate': 0.045,
                'reconciliation_weights': {
                    'percentage_of_fee': 0.60,
                    'income_capitalization': 0.25,
                    'before_after': 0.15
                }
            }
        })
        weights = calc._get_dynamic_weights()
        self.assertEqual(weights['percentage_of_fee'], 0.60)


class TestSensitivityAnalysis(unittest.TestCase):
    """Test suite for Sensitivity Analysis (NEW in v2.0)"""

    def test_cap_rate_sensitivity(self):
        """Test cap rate sensitivity analysis (±1%)"""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 1200000},
            'easement': {
                'type': 'utility_transmission',
                'voltage_kv': 230,
                'area_acres': 15,
                'productivity_loss_pct': 0.20
            },
            'market_parameters': {'cap_rate': 0.045, 'annual_rent_per_acre': 300}
        })
        result = calc.sensitivity_analysis()

        # Should have 3 cap rate scenarios (-1%, 0%, +1%)
        cap_rate_scenarios = [s for s in result['scenarios'] if s['variable'] == 'cap_rate']
        self.assertEqual(len(cap_rate_scenarios), 3)

        # Check values
        values = [s['easement_value'] for s in cap_rate_scenarios]
        # Lower cap rate = higher value, higher cap rate = lower value
        self.assertTrue(values[0] > values[1] > values[2])

    def test_productivity_loss_sensitivity(self):
        """Test productivity loss sensitivity analysis (±5%)"""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 1200000},
            'easement': {
                'type': 'utility_transmission',
                'voltage_kv': 230,
                'area_acres': 15,
                'productivity_loss_pct': 0.20
            },
            'market_parameters': {'cap_rate': 0.045, 'annual_rent_per_acre': 300}
        })
        result = calc.sensitivity_analysis()

        # Should have 3 productivity scenarios (-5%, 0%, +5%)
        prod_scenarios = [s for s in result['scenarios'] if s['variable'] == 'productivity_loss_pct']
        self.assertEqual(len(prod_scenarios), 3)


class TestIntegrationWorkflows(unittest.TestCase):
    """Integration tests for complete workflows"""

    def test_permanent_easement_complete_workflow(self):
        """Test complete permanent easement valuation workflow"""
        calc = HydroEasementCalculator({
            'property': {
                'address': '100 acres, Class 1 agricultural',
                'total_acres': 100,
                'fee_simple_value': 1200000
            },
            'easement': {
                'type': 'utility_transmission',
                'voltage_kv': 230,
                'area_acres': 15,
                'width_meters': 50,
                'term': 'perpetual',
                'restrictions': ['no_buildings', 'height_restrictions'],
                'hbu_impact': 'moderate',
                'productivity_loss_pct': 0.20
            },
            'market_parameters': {'cap_rate': 0.045, 'annual_rent_per_acre': 300}
        })
        results = calc.calculate_all_methods()

        # Should have all three methods
        self.assertIn('percentage_of_fee', results['valuation_methods'])
        self.assertIn('income_capitalization', results['valuation_methods'])
        self.assertIn('before_after', results['valuation_methods'])

        # Should have reconciliation
        self.assertIn('reconciliation', results)
        self.assertIn('weights', results['reconciliation'])
        self.assertIn('reconciled_value', results['reconciliation'])

        # Should have sensitivity analysis
        self.assertIn('sensitivity_analysis', results)

        # Classification should be permanent
        self.assertEqual(results['easement_classification'], 'Permanent Easement')

    def test_tce_complete_workflow(self):
        """Test complete TCE valuation workflow"""
        calc = HydroEasementCalculator({
            'property': {
                'address': '2 acres industrial',
                'total_acres': 2,
                'fee_simple_value': 400000
            },
            'easement': {
                'type': 'access',
                'area_acres': 2,
                'term': 'tce',
                'duration_days': 90,
                'restoration_costs': 15000,
                'business_losses': 8000
            },
            'market_parameters': {'cap_rate': 0.10, 'tce_annual_rate': 0.10}
        })
        results = calc.calculate_all_methods()

        # Should route to TCE method
        self.assertEqual(results['easement_classification'], 'Temporary Construction Easement (TCE)')
        self.assertIn('valuation_method', results)
        self.assertEqual(results['valuation_method']['method'], 'TCE Rate-of-Return')

        # Should NOT have traditional reconciliation (TCE uses single method)
        self.assertNotIn('valuation_methods', results)
        self.assertNotIn('reconciliation', results)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""

    def test_missing_optional_parameters(self):
        """Test calculator handles missing optional parameters"""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 1000000},
            'easement': {'type': 'access', 'area_acres': 5},  # Minimal required params
            'market_parameters': {'cap_rate': 0.07}
        })
        # Should not raise exception
        result = calc.calculate_all_methods()
        self.assertIsNotNone(result)

    def test_zero_area_acres(self):
        """Test behavior with zero easement area"""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 1000000},
            'easement': {'type': 'access', 'area_acres': 0},
            'market_parameters': {'cap_rate': 0.07}
        })
        result = calc.calculate_percentage_of_fee()
        self.assertEqual(result['easement_value'], 0)


def run_tests():
    """Run all tests and print results"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPercentageOfFeeMethod))
    suite.addTests(loader.loadTestsFromTestCase(TestIncomeCapitalizationMethod))
    suite.addTests(loader.loadTestsFromTestCase(TestTCERateOfReturnMethod))
    suite.addTests(loader.loadTestsFromTestCase(TestDynamicReconciliationWeights))
    suite.addTests(loader.loadTestsFromTestCase(TestSensitivityAnalysis))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationWorkflows))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print(f"\n{'='*80}")
    print(f"TEST SUMMARY")
    print(f"{'='*80}")
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"{'='*80}\n")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
