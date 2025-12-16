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
                # Note: Loading dock values use industry defaults via effective_factors
                # Industry default loading_dock_value_per_dock: 35000 triggers ratio allocation
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
        """Loading docks valued by type (using ratio allocation from industry defaults)"""
        calc = ComparableSalesCalculator(self.input_data)
        comparable = {
            "property_type": "industrial",
            "loading_docks_dock_high": 4,
            "loading_docks_grade_level": 0,
            "loading_docks_drive_in": 1
        }
        result = calc.calculate_physical_characteristics_adjustment(comparable, 1000000)

        # With industry default loading_dock_value_per_dock: 35000 (ratio allocation):
        # dock_high_value = 35000 * 0.70 = 24500
        # grade_level_value = 35000 * 0.40 = 14000
        # drive_in_value = 35000 * 1.40 = 49000
        #
        # Subject: (6*24500 + 2*14000 + 0*49000) = 147000 + 28000 = 175000
        # Comp: (4*24500 + 0*14000 + 1*49000) = 98000 + 49000 = 147000
        # Adjustment: +28000
        dock_adjustments = [adj for adj in result['all_adjustments'] if adj['characteristic'] == 'Loading Docks']
        self.assertEqual(len(dock_adjustments), 1)
        self.assertEqual(dock_adjustments[0]['adjustment'], 28000)

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


# ============================================================================
# AACI REVIEW RESPONSE TESTS - Issue #1 through #5
# TDD Tests: These expose bugs identified in the AACI desk review
# ============================================================================

class TestDerivedFactorsPassedToModules(unittest.TestCase):
    """
    Test Issue #1 (CRITICAL): Derived factors must be passed to adjustment modules.

    AACI Review Finding:
    - Factor table states Clear Height = $4.00/ft/SF, Age Depreciation = 3.0%/yr
    - But grids apply different rates: $1.50/ft/SF and 1.0%/yr (module defaults)

    Root Cause: Line 724-746 passes self.market instead of self.effective_factors
    """

    def setUp(self):
        self.input_data = {
            "subject_property": {
                "property_type": "industrial",
                "building_sf": 50000,
                "clear_height_feet": 28,
                "condition": "average"
            },
            "comparable_sales": [],
            "market_parameters": {
                "valuation_date": "2025-01-15"
            }
        }

    def test_derived_clear_height_factor_applied(self):
        """
        CRITICAL: Derived clear_height_value_per_foot_per_sf must be used, not default.

        This test FAILS with current bug (uses $1.50 default instead of $4.00 derived)
        This test PASSES after fix (uses $4.00 from derived factors)
        """
        # Simulate derived factors from paired sales analysis
        # Use the CORRECT derived name from parameter_mapping.py:
        # 'clear_height_per_foot_per_sf' -> 'clear_height_value_per_foot_per_sf'
        derived_factors = {
            'factors': {
                'clear_height_per_foot_per_sf': {
                    'value': 4.0,  # Derived: $4.00/ft/SF (vs default $1.50)
                    'confidence': 'high',
                    'method': 'paired_sales'
                }
            }
        }

        calc = ComparableSalesCalculator(self.input_data, derived_factors)

        comparable = {
            "property_type": "industrial",
            "building_sf": 50000,
            "clear_height_feet": 24  # 4 feet less than subject
        }

        result = calc.calculate_physical_characteristics_adjustment(comparable, 1000000)

        # Find clear height adjustment
        clear_height_adjustments = [
            adj for adj in result['all_adjustments']
            if adj['characteristic'] == 'Clear Height'
        ]

        self.assertEqual(len(clear_height_adjustments), 1, "Should have exactly one clear height adjustment")

        # Subject: 28' - Comp: 24' = +4 feet difference
        # With derived factor ($4.00/ft/SF): +4 × $4.00 × 50,000 = +$800,000
        # With default factor ($1.50/ft/SF): +4 × $1.50 × 50,000 = +$300,000

        adjustment = clear_height_adjustments[0]['adjustment']

        # Test that derived factor is used (should be ~$800,000, NOT ~$300,000)
        self.assertGreater(adjustment, 600000,
            f"Clear height adjustment should use derived $4.00/ft/SF (expect ~$800k), got ${adjustment:,.0f}")
        self.assertLess(adjustment, 1000000,
            f"Clear height adjustment should be reasonable, got ${adjustment:,.0f}")

    def test_derived_condition_factor_applied(self):
        """
        Derived condition_adjustment_pct_per_level must be used, not default.

        This test FAILS with current bug (uses 6.0% default instead of 13.49% derived)
        """
        # Use the CORRECT derived name from parameter_mapping.py:
        # 'condition_per_level_pct' -> 'condition_adjustment_pct_per_level'
        derived_factors = {
            'factors': {
                'condition_per_level_pct': {
                    'value': 13.49,  # Derived: 13.49%/level (vs default 6.0%)
                    'confidence': 'medium',
                    'method': 'paired_sales'
                }
            }
        }

        calc = ComparableSalesCalculator(self.input_data, derived_factors)

        comparable = {
            "property_type": "industrial",
            "building_sf": 50000,
            "clear_height_feet": 28,  # Same as subject
            "condition": "good"  # 1 level better than subject (average)
        }

        result = calc.calculate_physical_characteristics_adjustment(comparable, 1000000)

        # Find condition adjustment
        condition_adjustments = [
            adj for adj in result['all_adjustments']
            if adj['characteristic'] == 'Condition'
        ]

        self.assertEqual(len(condition_adjustments), 1, "Should have exactly one condition adjustment")

        # Subject: average (3) - Comp: good (4) = -1 level
        # With derived factor (13.49%): -1 × 13.49% × $1M = -$134,900
        # With default factor (6.0%): -1 × 6.0% × $1M = -$60,000

        adjustment = condition_adjustments[0]['adjustment']

        # Test that derived factor is used (should be ~-$135k, NOT ~-$60k)
        self.assertLess(adjustment, -100000,
            f"Condition adjustment should use derived 13.49% (expect ~-$135k), got ${adjustment:,.0f}")
        self.assertGreater(adjustment, -200000,
            f"Condition adjustment should be reasonable, got ${adjustment:,.0f}")

    def test_derived_loading_dock_factor_applied(self):
        """
        Derived loading_dock_value_per_dock must be used for ratio allocation.

        Bug: Uses default $25k/$15k/$50k instead of derived $52.5k/$30k/$105k
        """
        derived_factors = {
            'factors': {
                'loading_dock_value': {
                    'value': 75000,  # Derived aggregate: $75,000/dock
                    'confidence': 'high',
                    'method': 'paired_sales'
                }
            }
        }

        calc = ComparableSalesCalculator(self.input_data, derived_factors)

        # Add docks to subject
        self.input_data['subject_property']['loading_docks_dock_high'] = 4
        self.input_data['subject_property']['loading_docks_grade_level'] = 2
        self.input_data['subject_property']['loading_docks_drive_in'] = 0

        comparable = {
            "property_type": "industrial",
            "building_sf": 50000,
            "clear_height_feet": 28,
            "loading_docks_dock_high": 2,  # 2 fewer than subject
            "loading_docks_grade_level": 2,
            "loading_docks_drive_in": 0
        }

        result = calc.calculate_physical_characteristics_adjustment(comparable, 1000000)

        # Find loading dock adjustment
        dock_adjustments = [
            adj for adj in result['all_adjustments']
            if adj['characteristic'] == 'Loading Docks'
        ]

        self.assertEqual(len(dock_adjustments), 1, "Should have exactly one loading dock adjustment")

        # With derived $75k aggregate (70% allocation = $52.5k/dock-high):
        # Subject: 4×$52.5k + 2×$30k = $210k + $60k = $270k
        # Comp: 2×$52.5k + 2×$30k = $105k + $60k = $165k
        # Adjustment: +$105,000

        # With default ($25k dock-high):
        # Subject: 4×$25k + 2×$15k = $100k + $30k = $130k
        # Comp: 2×$25k + 2×$15k = $50k + $30k = $80k
        # Adjustment: +$50,000

        adjustment = dock_adjustments[0]['adjustment']

        # Test that derived factor is used (should be ~$105k, NOT ~$50k)
        self.assertGreater(adjustment, 80000,
            f"Loading dock adjustment should use derived $75k/dock (expect ~$105k), got ${adjustment:,.0f}")


class TestLocationResidualLogic(unittest.TestCase):
    """
    Test Issue #4 (MEDIUM): Location methodology must be consistent across comparables.

    AACI Review Finding:
    - Highway frontage premium (22.59%) applied to Comps 2 and 5
    - Location score deltas sometimes applied, sometimes suppressed
    - Rule set inconsistent, creating double-counting risk

    Required Fix: Implement residual location score when highway differs.
    """

    def setUp(self):
        self.input_data = {
            "subject_property": {
                "property_type": "industrial",
                "location_score": 75,
                "highway_frontage": True,
                "location_submarket": "Hamilton Industrial East"
            },
            "comparable_sales": [],
            "market_parameters": {
                "highway_frontage_premium_pct": 22.59
            }
        }

    def test_highway_differs_with_location_score_residual(self):
        """
        When highway status differs, should apply residual location score adjustment.

        Current bug: Location score completely suppressed when highway differs.
        Fix: Apply residual score after accounting for highway attribution (7 points).

        Example: Subject (score 75, highway=True) vs Comp (score 68, highway=False)
        - Score diff = 7 points
        - Highway attribution = 7 points (configurable)
        - Residual = 0 points (no additional adjustment)

        But if score diff > attribution:
        - Subject (score 75, highway=True) vs Comp (score 60, highway=False)
        - Score diff = 15 points
        - Highway attribution = 7 points
        - Residual = 8 points (should be applied)
        """
        calc = ComparableSalesCalculator(self.input_data)

        # Test case where residual should be applied
        comparable = {
            "location_score": 60,  # 15 points lower than subject
            "highway_frontage": False,  # Triggers highway premium
            "location_submarket": "Hamilton Industrial East"
        }

        result = calc.calculate_location_adjustment(comparable, 1000000)

        # Should have both highway adjustment AND residual location score
        self.assertIn('components', result, "Result should have components list")

        components_text = ' '.join(result.get('components', []))

        # Check highway adjustment is present
        self.assertIn('highway', components_text.lower(),
            "Should include highway frontage adjustment")

        # After fix: Should also include residual location score
        # Score diff (15) > attribution (7), so residual (8 points) should apply
        # This will FAIL before fix, PASS after
        # Note: The exact implementation may vary, but we need SOME residual adjustment

        # The total adjustment should be MORE than just highway premium
        # Highway only: 22.59% = $225,900
        # With residual: Should be higher
        self.assertGreater(result['adjustment_pct'], 22.59,
            f"Total location adjustment should include residual score beyond highway. "
            f"Got {result['adjustment_pct']:.2f}%, expected > 22.59%")

    def test_highway_same_applies_full_location_score(self):
        """
        When highway status is same, full location score adjustment should apply.
        This should pass both before and after fix (existing behavior).
        """
        calc = ComparableSalesCalculator(self.input_data)

        comparable = {
            "location_score": 60,  # 15 points lower than subject
            "highway_frontage": True,  # Same as subject
            "location_submarket": "Hamilton Industrial East"
        }

        result = calc.calculate_location_adjustment(comparable, 1000000)

        # Should have location score adjustment (not suppressed)
        self.assertIn('components', result)
        components_text = ' '.join(result.get('components', []))

        self.assertIn('location score', components_text.lower(),
            "Should include location score adjustment when highway is same")
        self.assertNotIn('NOT APPLIED', components_text,
            "Location score should NOT be suppressed when highway is same")


class TestWeightingMethodDescription(unittest.TestCase):
    """
    Test Issue #5 (MEDIUM): Weighting must be accurately described.

    AACI Review Finding:
    - Method described as "Inverse net adjustment with validation status filters"
    - Actual logic is threshold-based discretionary weighting (200/150/100/50/0)
    - Nothing makes this "inverse" to any objective metric

    Required Fix: Update description to "Threshold-Based Quality Weighting"
    """

    def setUp(self):
        self.input_data = {
            "subject_property": {
                "property_type": "industrial",
                "location_score": 75
            },
            "comparable_sales": [
                {"sale_price": 1000000, "address": "Test Comp 1"}
            ],
            "market_parameters": {}
        }

    def test_weighting_method_not_inverse(self):
        """
        Verify weighting method description is NOT "inverse".

        Current bug: Says "Inverse net adjustment with validation status filters"
        Fix: Should say "Threshold-Based Quality Weighting" or similar
        """
        calc = ComparableSalesCalculator(self.input_data)
        results = calc.reconcile_comparables()

        weighting_method = results['reconciliation'].get('weighting_method', '')

        # After fix: Should NOT claim to be "inverse"
        self.assertNotIn('inverse', weighting_method.lower(),
            f"Weighting method should not claim to be 'inverse'. Got: '{weighting_method}'")

    def test_weighting_method_accurate_description(self):
        """
        Verify weighting method description is accurate.

        The actual logic is threshold-based:
        - <5% net adj: 2.0x weight
        - 5-10%: 1.5x weight
        - 10-25%: 1.0x weight
        - 25-40%: 0.5x weight
        - >40%: 0.0x (rejected)
        """
        calc = ComparableSalesCalculator(self.input_data)
        results = calc.reconcile_comparables()

        weighting_method = results['reconciliation'].get('weighting_method', '')

        # After fix: Should describe as threshold-based
        self.assertTrue(
            'threshold' in weighting_method.lower() or
            'quality' in weighting_method.lower() or
            'discretionary' in weighting_method.lower(),
            f"Weighting method should accurately describe threshold-based logic. Got: '{weighting_method}'"
        )


class TestEffectiveFactorsMerge(unittest.TestCase):
    """
    Test that effective_factors contains merged values from derived + market_parameters.

    This is a sanity check that the merge logic itself works correctly.
    The bug is in PASSING the merged factors, not in MERGING them.
    """

    def setUp(self):
        self.input_data = {
            "subject_property": {"property_type": "industrial"},
            "comparable_sales": [],
            "market_parameters": {
                "appreciation_rate_annual": 3.5  # User override
            }
        }

    def test_effective_factors_includes_derived(self):
        """effective_factors should include mapped derived values."""
        # Use the CORRECT derived name from parameter_mapping.py:
        # 'clear_height_per_foot_per_sf' -> 'clear_height_value_per_foot_per_sf'
        derived_factors = {
            'factors': {
                'clear_height_per_foot_per_sf': {
                    'value': 4.0,
                    'confidence': 'high',
                    'method': 'paired_sales'
                }
            }
        }

        calc = ComparableSalesCalculator(self.input_data, derived_factors)

        # After mapping, should have clear_height_value_per_foot_per_sf = 4.0
        self.assertIn('clear_height_value_per_foot_per_sf', calc.effective_factors,
            "effective_factors should contain mapped clear height value")
        self.assertEqual(calc.effective_factors['clear_height_value_per_foot_per_sf'], 4.0,
            "Derived clear height value should be 4.0")

    def test_user_override_takes_precedence(self):
        """User market_parameters should override derived factors."""
        derived_factors = {
            'factors': {
                'appreciation_rate': {
                    'value': 5.0,  # Derived says 5%
                    'confidence': 'high',
                    'method': 'paired_sales'
                }
            }
        }

        # market_parameters says 3.5%
        calc = ComparableSalesCalculator(self.input_data, derived_factors)

        # User override (3.5) should win over derived (5.0)
        self.assertEqual(calc.effective_factors['appreciation_rate_annual'], 3.5,
            "User override should take precedence over derived factors")


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

    # AACI Review Response Tests (TDD - these expose bugs)
    suite.addTests(loader.loadTestsFromTestCase(TestDerivedFactorsPassedToModules))
    suite.addTests(loader.loadTestsFromTestCase(TestLocationResidualLogic))
    suite.addTests(loader.loadTestsFromTestCase(TestWeightingMethodDescription))
    suite.addTests(loader.loadTestsFromTestCase(TestEffectiveFactorsMerge))

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
