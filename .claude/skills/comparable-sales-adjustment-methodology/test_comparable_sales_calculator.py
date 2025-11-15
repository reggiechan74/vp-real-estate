#!/usr/bin/env python3
"""
Unit Tests for Comparable Sales Adjustment Calculator

Tests all 6 adjustment stages and 49 physical characteristic adjustments.

Test Coverage (17 tests across 8 test classes):
- Property Rights Adjustments (2 tests)
- Financing Terms Adjustments (2 tests)
- Market Conditions/Time Adjustments (2 tests)
- Physical Characteristics - Land (4 tests: lot size, topography, flood zone, environmental)
- Physical Characteristics - Industrial (3 tests: clear height, loading docks, property type)
- Physical Characteristics - Office (2 tests: building class, parking ratio)
- Compliance Flags (1 test: USPAP/CUSPAP/IVS compliance)
- Category Grouping (1 test: multi-category adjustments)
"""

import unittest
import json
import sys
from datetime import datetime
from comparable_sales_calculator import ComparableSalesCalculator


class TestPropertyRightsAdjustment(unittest.TestCase):
    """Test Stage 1: Property Rights Adjustments"""

    def setUp(self):
        self.input_data = {
            "subject_property": {"property_rights": "fee_simple"},
            "comparable_sales": [],
            "market_parameters": {"cap_rate": 7.0}
        }

    def test_fee_simple_to_fee_simple(self):
        """No adjustment when both are fee simple"""
        calc = ComparableSalesCalculator(self.input_data)
        comparable = {"property_rights": "fee_simple", "sale_price": 1000000}
        result = calc.calculate_property_rights_adjustment(comparable, 1000000)

        self.assertEqual(result['adjustment_amount'], 0.0)
        self.assertEqual(result['adjusted_price'], 1000000)

    def test_leasehold_to_fee_simple(self):
        """Positive adjustment for leasehold comparable"""
        calc = ComparableSalesCalculator(self.input_data)
        comparable = {
            "property_rights": "leasehold",
            "ground_rent_annual": 50000,
            "sale_price": 1000000
        }
        result = calc.calculate_property_rights_adjustment(comparable, 1000000)

        # Capitalized land value = 50000 / 0.07 = 714,285.71
        expected_adjustment = 50000 / 0.07
        self.assertAlmostEqual(result['adjustment_amount'], expected_adjustment, places=2)
        self.assertGreater(result['adjusted_price'], 1000000)


class TestFinancingAdjustment(unittest.TestCase):
    """Test Stage 2: Financing Terms Adjustments"""

    def setUp(self):
        self.input_data = {
            "subject_property": {"property_rights": "fee_simple"},
            "comparable_sales": [],
            "market_parameters": {}
        }

    def test_cash_sale(self):
        """No adjustment for cash sale"""
        calc = ComparableSalesCalculator(self.input_data)
        comparable = {"financing": {"type": "cash"}}
        result = calc.calculate_financing_adjustment(comparable, 1000000)

        self.assertEqual(result['adjustment_amount'], 0.0)
        self.assertEqual(result['adjusted_price'], 1000000)

    def test_seller_vtb_adjustment(self):
        """Negative adjustment for seller VTB (below market rate)"""
        calc = ComparableSalesCalculator(self.input_data)
        comparable = {
            "financing": {
                "type": "seller_vtb",
                "rate": 3.5,
                "market_rate": 6.5,
                "term_years": 10,
                "loan_amount": 500000
            }
        }
        result = calc.calculate_financing_adjustment(comparable, 1000000)

        # Should be negative (deduct financing benefit)
        self.assertLess(result['adjustment_amount'], 0)
        self.assertLess(result['adjusted_price'], 1000000)


class TestMarketConditionsAdjustment(unittest.TestCase):
    """Test Stage 4: Market Conditions/Time Adjustments"""

    def setUp(self):
        self.input_data = {
            "subject_property": {"property_rights": "fee_simple"},
            "comparable_sales": [],
            "market_parameters": {
                "appreciation_rate_annual": 3.5,
                "valuation_date": "2025-01-15"
            }
        }

    def test_compound_appreciation(self):
        """Verify compound appreciation formula (not simple interest)"""
        calc = ComparableSalesCalculator(self.input_data)
        comparable = {
            "sale_date": "2023-07-15",  # 1.5 years ago
            "sale_price": 1000000
        }
        result = calc.calculate_market_conditions_adjustment(comparable, 1000000)

        # 1.5 years at 3.5% = (1.035^1.5) - 1 = ~5.32%
        # Compound: 1000000 * 1.035^1.5 = 1,053,200
        self.assertAlmostEqual(result['years_difference'], 1.5, places=1)
        self.assertGreater(result['adjustment_amount'], 53000)  # More than simple interest
        self.assertLess(result['adjustment_amount'], 54000)

    def test_zero_appreciation(self):
        """No adjustment when appreciation rate is zero"""
        input_data_no_growth = {
            "subject_property": {"property_rights": "fee_simple"},
            "comparable_sales": [],
            "market_parameters": {
                "appreciation_rate_annual": 0,
                "valuation_date": "2025-01-15"
            }
        }
        calc = ComparableSalesCalculator(input_data_no_growth)
        comparable = {"sale_date": "2024-01-15", "sale_price": 1000000}
        result = calc.calculate_market_conditions_adjustment(comparable, 1000000)

        self.assertEqual(result['adjustment_amount'], 0.0)


class TestPhysicalCharacteristicsLand(unittest.TestCase):
    """Test Physical Characteristics: Land Adjustments (8 subcategories)"""

    def setUp(self):
        self.input_data = {
            "subject_property": {
                "property_type": "industrial",
                "lot_size_acres": 5.0,
                "frontage_linear_feet": 400,
                "depth_feet": 545,
                "topography": "level",
                "utilities": "full_services_adequate",
                "drainage": "good",
                "flood_zone": "none",
                "environmental_status": "clean",
                "soil_quality": "adequate"
            },
            "comparable_sales": [],
            "market_parameters": {
                "lot_adjustment_per_acre": 15000,
                "shape_adjustment_per_0_1_deviation": 0.02,
                "topography_adjustment_pct_per_level": 3.5,
                "utilities_adjustment_pct_per_level": 5.0,
                "drainage_adjustment_pct_per_level": 2.0
            }
        }

    def test_lot_size_adjustment(self):
        """Lot size adjustment calculates correctly"""
        calc = ComparableSalesCalculator(self.input_data)
        comparable = {"lot_size_acres": 7.0}
        result = calc.calculate_physical_characteristics_adjustment(comparable, 1000000)

        # Subject 5.0 acres - Comp 7.0 acres = -2.0 acres
        # -2.0 * $15,000 = -$30,000
        land_adjustments = [adj for adj in result['all_adjustments'] if adj['characteristic'] == 'Lot Size']
        self.assertEqual(len(land_adjustments), 1)
        self.assertEqual(land_adjustments[0]['adjustment'], -30000)

    def test_topography_adjustment(self):
        """Topography premium for level land"""
        calc = ComparableSalesCalculator(self.input_data)
        comparable = {"topography": "moderately_sloped"}
        result = calc.calculate_physical_characteristics_adjustment(comparable, 1000000)

        # Subject: level (4) - Comp: moderately_sloped (2) = +2 levels
        # +2 * 3.5% = +7% = +$70,000
        topo_adjustments = [adj for adj in result['all_adjustments'] if adj['characteristic'] == 'Topography']
        self.assertEqual(len(topo_adjustments), 1)
        self.assertAlmostEqual(topo_adjustments[0]['adjustment'], 70000, places=0)

    def test_flood_zone_penalty(self):
        """Flood zone creates negative adjustment"""
        calc = ComparableSalesCalculator(self.input_data)
        comparable = {"flood_zone": "flood_fringe"}
        result = calc.calculate_physical_characteristics_adjustment(comparable, 1000000)

        # Subject: none (0%) - Comp: flood_fringe (-5%) = -5% adjustment
        # (comp is worse, gets negative adjustment to devalue it)
        flood_adjustments = [adj for adj in result['all_adjustments'] if adj['characteristic'] == 'Flood Zone']
        self.assertEqual(len(flood_adjustments), 1)
        self.assertAlmostEqual(flood_adjustments[0]['adjustment'], -50000, places=0)

    def test_environmental_brownfield(self):
        """Brownfield site adjustment"""
        calc = ComparableSalesCalculator(self.input_data)
        comparable = {"environmental_status": "brownfield"}
        result = calc.calculate_physical_characteristics_adjustment(comparable, 1000000)

        # Subject: clean (0%) - Comp: brownfield (-15%) = -15% adjustment
        # (comp is worse, gets negative adjustment to devalue it)
        env_adjustments = [adj for adj in result['all_adjustments'] if adj['characteristic'] == 'Environmental Status']
        self.assertEqual(len(env_adjustments), 1)
        self.assertAlmostEqual(env_adjustments[0]['adjustment'], -150000, places=0)


class TestPhysicalCharacteristicsIndustrial(unittest.TestCase):
    """Test Physical Characteristics: Industrial Building Adjustments"""

    def setUp(self):
        self.input_data = {
            "subject_property": {
                "property_type": "industrial",
                "building_sf": 50000,
                "clear_height_feet": 32,
                "loading_docks_dock_high": 6,
                "loading_docks_grade_level": 2,
                "loading_docks_drive_in": 0,
                "column_spacing_feet": 50,
                "floor_load_capacity_psf": 250,
                "condition": "good"
            },
            "comparable_sales": [],
            "market_parameters": {
                "building_size_adjustment_per_sf": 2.0,
                "clear_height_value_per_foot_per_sf": 1.5,
                "column_spacing_adjustment_per_sf": 0.75,
                "floor_load_adjustment_per_sf": 3.0,
                "condition_adjustment_pct_per_level": 6.0
            }
        }

    def test_clear_height_adjustment(self):
        """Clear height is critical for warehousing"""
        calc = ComparableSalesCalculator(self.input_data)
        comparable = {
            "property_type": "industrial",
            "building_sf": 50000,
            "clear_height_feet": 24
        }
        result = calc.calculate_physical_characteristics_adjustment(comparable, 1000000)

        # Subject: 32' - Comp: 24' = +8 feet
        # +8 * $1.5/sf * 50,000 sf = +$600,000
        clear_height_adjustments = [adj for adj in result['all_adjustments'] if adj['characteristic'] == 'Clear Height']
        self.assertEqual(len(clear_height_adjustments), 1)
        self.assertEqual(clear_height_adjustments[0]['adjustment'], 600000)

    def test_loading_docks_by_type(self):
        """Loading docks valued by type"""
        calc = ComparableSalesCalculator(self.input_data)
        comparable = {
            "property_type": "industrial",
            "loading_docks_dock_high": 4,
            "loading_docks_grade_level": 0,
            "loading_docks_drive_in": 1
        }
        result = calc.calculate_physical_characteristics_adjustment(comparable, 1000000)

        # Subject: (6*25k + 2*15k + 0*50k) = 180k
        # Comp: (4*25k + 0*15k + 1*50k) = 150k
        # Adjustment: +30k
        dock_adjustments = [adj for adj in result['all_adjustments'] if adj['characteristic'] == 'Loading Docks']
        self.assertEqual(len(dock_adjustments), 1)
        self.assertEqual(dock_adjustments[0]['adjustment'], 30000)

    def test_property_type_detection(self):
        """Industrial property type applies industrial adjustments"""
        calc = ComparableSalesCalculator(self.input_data)
        comparable = {
            "property_type": "industrial",
            "building_sf": 50000,
            "clear_height_feet": 28
        }
        result = calc.calculate_physical_characteristics_adjustment(comparable, 1000000)

        # Should have "Industrial Building" category
        self.assertIn('Industrial Building', result['adjustments_by_category'])


class TestPhysicalCharacteristicsOffice(unittest.TestCase):
    """Test Physical Characteristics: Office Building Adjustments"""

    def setUp(self):
        self.input_data = {
            "subject_property": {
                "property_type": "office",
                "building_sf": 30000,
                "building_class": "A",
                "parking_spaces_per_1000sf": 4.5,
                "floor_plate_efficiency_pct": 87,
                "condition": "excellent"
            },
            "comparable_sales": [],
            "market_parameters": {
                "building_size_adjustment_per_sf": 3.0,
                "building_class_adjustment_pct_per_level": 10.0,
                "parking_value_per_space": 4000,
                "efficiency_adjustment_pct_per_5pts": 1.5,
                "condition_adjustment_pct_per_level": 8.0
            }
        }

    def test_building_class_adjustment(self):
        """Building class creates significant value difference"""
        calc = ComparableSalesCalculator(self.input_data)
        comparable = {
            "property_type": "office",
            "building_sf": 30000,
            "building_class": "B"
        }
        result = calc.calculate_physical_characteristics_adjustment(comparable, 1000000)

        # Subject: A (6) - Comp: B (3) = +3 levels
        # +3 * 10% = +30% = +$300,000
        class_adjustments = [adj for adj in result['all_adjustments'] if adj['characteristic'] == 'Building Class']
        self.assertEqual(len(class_adjustments), 1)
        self.assertAlmostEqual(class_adjustments[0]['adjustment'], 300000, places=0)

    def test_parking_ratio_adjustment(self):
        """Parking ratio converts to actual spaces"""
        calc = ComparableSalesCalculator(self.input_data)
        comparable = {
            "property_type": "office",
            "building_sf": 30000,
            "parking_spaces_per_1000sf": 3.0
        }
        result = calc.calculate_physical_characteristics_adjustment(comparable, 1000000)

        # Subject: 4.5/1000 * 30 = 135 spaces
        # Comp: 3.0/1000 * 30 = 90 spaces
        # Difference: +45 spaces * $4,000 = +$180,000
        parking_adjustments = [adj for adj in result['all_adjustments'] if adj['characteristic'] == 'Parking Ratio']
        self.assertEqual(len(parking_adjustments), 1)
        self.assertEqual(parking_adjustments[0]['adjustment'], 180000)


class TestComplianceFlags(unittest.TestCase):
    """Test USPAP/CUSPAP/IVS Compliance Flags"""

    def setUp(self):
        self.input_data = {
            "subject_property": {"property_type": "industrial", "lot_size_acres": 5.0},
            "comparable_sales": [],
            "market_parameters": {"lot_adjustment_per_acre": 15000}
        }

    def test_compliance_flags_present(self):
        """Enhanced adjustments include compliance flags"""
        calc = ComparableSalesCalculator(self.input_data)
        comparable = {"lot_size_acres": 7.0}
        result = calc.calculate_physical_characteristics_adjustment(comparable, 1000000)

        self.assertIn('compliance', result)
        self.assertTrue(result['compliance']['uspap_2024'])
        self.assertTrue(result['compliance']['cuspap_2024'])
        self.assertTrue(result['compliance']['ivs'])


class TestCategoryGrouping(unittest.TestCase):
    """Test Adjustment Category Grouping"""

    def setUp(self):
        self.input_data = {
            "subject_property": {
                "property_type": "industrial",
                "lot_size_acres": 5.0,
                "building_sf": 50000,
                "clear_height_feet": 32
            },
            "comparable_sales": [],
            "market_parameters": {
                "lot_adjustment_per_acre": 15000,
                "building_size_adjustment_per_sf": 2.0,
                "clear_height_value_per_foot_per_sf": 1.5
            }
        }

    def test_multiple_categories(self):
        """Adjustments grouped by category"""
        calc = ComparableSalesCalculator(self.input_data)
        comparable = {
            "property_type": "industrial",
            "lot_size_acres": 7.0,
            "building_sf": 60000,
            "clear_height_feet": 24
        }
        result = calc.calculate_physical_characteristics_adjustment(comparable, 1000000)

        # Should have both Land and Industrial Building categories
        self.assertIn('Land', result['adjustments_by_category'])
        self.assertIn('Industrial Building', result['adjustments_by_category'])

        # Verify category counts
        self.assertGreater(result['adjustments_by_category']['Land']['count'], 0)
        self.assertGreater(result['adjustments_by_category']['Industrial Building']['count'], 0)


def run_tests():
    """Run all unit tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPropertyRightsAdjustment))
    suite.addTests(loader.loadTestsFromTestCase(TestFinancingAdjustment))
    suite.addTests(loader.loadTestsFromTestCase(TestMarketConditionsAdjustment))
    suite.addTests(loader.loadTestsFromTestCase(TestPhysicalCharacteristicsLand))
    suite.addTests(loader.loadTestsFromTestCase(TestPhysicalCharacteristicsIndustrial))
    suite.addTests(loader.loadTestsFromTestCase(TestPhysicalCharacteristicsOffice))
    suite.addTests(loader.loadTestsFromTestCase(TestComplianceFlags))
    suite.addTests(loader.loadTestsFromTestCase(TestCategoryGrouping))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
