#!/usr/bin/env python3
"""
Comprehensive Test Suite for Hydro Easement Calculator

Tests hydro-specific functionality:
1. Voltage-based percentage calculation (69kV - 500kV)
2. EMF concern adjustments (≥230kV)
3. Tower placement impacts
4. Vegetation management restrictions
5. Access road requirements
6. Building proximity impacts
7. Hydro-specific reconciliation weights

Author: Claude Code
Created: 2025-11-17
Version: 2.0.0
"""

import unittest
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from hydro_easement_calculator import HydroEasementCalculator


class TestHydroVoltageTiers(unittest.TestCase):
    """Test voltage-based percentage calculation."""

    def test_500kv_base_percentage(self):
        """Test 500kV transmission gets 22.5% base percentage."""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 1000000},
            'easement': {'voltage_kv': 500, 'area_acres': 5},
            'market_parameters': {'cap_rate': 0.10}
        })
        self.assertEqual(calc.get_base_percentage(), 22.5)

    def test_230kv_base_percentage(self):
        """Test 230kV transmission gets 17.5% base percentage."""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 1000000},
            'easement': {'voltage_kv': 230, 'area_acres': 5},
            'market_parameters': {'cap_rate': 0.10}
        })
        self.assertEqual(calc.get_base_percentage(), 17.5)

    def test_115kv_base_percentage(self):
        """Test 115kV transmission gets 15.0% base percentage."""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 1000000},
            'easement': {'voltage_kv': 115, 'area_acres': 5},
            'market_parameters': {'cap_rate': 0.10}
        })
        self.assertEqual(calc.get_base_percentage(), 15.0)

    def test_69kv_base_percentage(self):
        """Test 69kV transmission gets 12.5% base percentage."""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 1000000},
            'easement': {'voltage_kv': 69, 'area_acres': 5},
            'market_parameters': {'cap_rate': 0.10}
        })
        self.assertEqual(calc.get_base_percentage(), 12.5)

    def test_low_voltage_base_percentage(self):
        """Test <69kV transmission gets 10.0% base percentage."""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 1000000},
            'easement': {'voltage_kv': 44, 'area_acres': 5},
            'market_parameters': {'cap_rate': 0.10}
        })
        self.assertEqual(calc.get_base_percentage(), 10.0)

    def test_missing_voltage_raises_error(self):
        """Test missing voltage_kv parameter raises clear error."""
        with self.assertRaises(ValueError) as context:
            calc = HydroEasementCalculator({
                'property': {'total_acres': 100, 'fee_simple_value': 1000000},
                'easement': {'area_acres': 5},
                'market_parameters': {'cap_rate': 0.10}
            })
            calc.get_base_percentage()

        self.assertIn('voltage_kv', str(context.exception))
        self.assertIn('REQUIRED', str(context.exception).upper())


class TestHydroDomainAdjustments(unittest.TestCase):
    """Test hydro-specific percentage adjustments."""

    def test_emf_concern_high_voltage(self):
        """Test EMF concern adjustment for ≥230kV transmission."""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 1000000},
            'easement': {'voltage_kv': 230, 'area_acres': 5},
            'market_parameters': {'cap_rate': 0.10}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertEqual(adjustments.get('emf_concern'), 2.0)

    def test_no_emf_concern_low_voltage(self):
        """Test no EMF concern adjustment for <230kV."""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 1000000},
            'easement': {'voltage_kv': 115, 'area_acres': 5},
            'market_parameters': {'cap_rate': 0.10}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertNotIn('emf_concern', adjustments)

    def test_tower_placement_single_tower(self):
        """Test tower placement adjustment for single tower."""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 1000000},
            'easement': {'voltage_kv': 230, 'area_acres': 5, 'tower_count': 1},
            'market_parameters': {'cap_rate': 0.10}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertEqual(adjustments.get('tower_placement'), 0.5)

    def test_tower_placement_multiple_towers(self):
        """Test tower placement adjustment for multiple towers."""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 1000000},
            'easement': {'voltage_kv': 230, 'area_acres': 5, 'tower_count': 4},
            'market_parameters': {'cap_rate': 0.10}
        })
        adjustments = calc.get_domain_specific_adjustments()
        # 4 towers × 0.5% = 2.0%
        self.assertEqual(adjustments.get('tower_placement'), 2.0)

    def test_tower_placement_capped_at_3_percent(self):
        """Test tower placement adjustment capped at +3%."""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 1000000},
            'easement': {'voltage_kv': 230, 'area_acres': 5, 'tower_count': 10},
            'market_parameters': {'cap_rate': 0.10}
        })
        adjustments = calc.get_domain_specific_adjustments()
        # 10 towers × 0.5% = 5.0%, but capped at 3.0%
        self.assertEqual(adjustments.get('tower_placement'), 3.0)

    def test_vegetation_restrictions(self):
        """Test vegetation management restrictions adjustment."""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 1000000},
            'easement': {
                'voltage_kv': 230,
                'area_acres': 5,
                'vegetation_restrictions': ['tree_clearing', 'height_limits']
            },
            'market_parameters': {'cap_rate': 0.10}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertEqual(adjustments.get('vegetation_management'), 1.5)

    def test_access_road_requirement(self):
        """Test access road requirement adjustment."""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 1000000},
            'easement': {'voltage_kv': 230, 'area_acres': 5, 'requires_access_road': True},
            'market_parameters': {'cap_rate': 0.10}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertEqual(adjustments.get('access_road'), 1.0)

    def test_proximity_to_buildings_high_voltage(self):
        """Test building proximity adjustment for high voltage close to buildings."""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 1000000},
            'easement': {
                'voltage_kv': 230,
                'area_acres': 5,
                'distance_to_buildings_m': 30
            },
            'market_parameters': {'cap_rate': 0.10}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertEqual(adjustments.get('proximity_impact'), 2.5)

    def test_no_proximity_adjustment_far_buildings(self):
        """Test no proximity adjustment when buildings are far."""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 1000000},
            'easement': {
                'voltage_kv': 230,
                'area_acres': 5,
                'distance_to_buildings_m': 100
            },
            'market_parameters': {'cap_rate': 0.10}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertNotIn('proximity_impact', adjustments)

    def test_combined_adjustments(self):
        """Test all hydro-specific adjustments combined."""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 1000000},
            'easement': {
                'voltage_kv': 500,
                'area_acres': 5,
                'tower_count': 2,
                'vegetation_restrictions': ['tree_clearing'],
                'requires_access_road': True,
                'distance_to_buildings_m': 40
            },
            'market_parameters': {'cap_rate': 0.10}
        })
        adjustments = calc.get_domain_specific_adjustments()

        # EMF concern (500kV): +2.0%
        # Tower placement (2 towers): +1.0%
        # Vegetation management: +1.5%
        # Access road: +1.0%
        # Proximity (40m and ≥230kV): +2.5%
        # Total domain adjustments: +8.0%

        total = sum(adjustments.values())
        self.assertEqual(total, 8.0)


class TestHydroReconciliationWeights(unittest.TestCase):
    """Test hydro-specific reconciliation weights."""

    def test_hydro_default_weights(self):
        """Test hydro transmission uses 50/30/20 weights."""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 1000000},
            'easement': {'voltage_kv': 230, 'area_acres': 5},
            'market_parameters': {'cap_rate': 0.10}
        })

        weights = calc._get_dynamic_weights()

        self.assertEqual(weights['percentage_of_fee'], 0.50)
        self.assertEqual(weights['income_capitalization'], 0.30)
        self.assertEqual(weights['before_after'], 0.20)

    def test_hydro_weights_reasoning(self):
        """Test hydro weights include professional reasoning."""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 1000000},
            'easement': {'voltage_kv': 230, 'area_acres': 5},
            'market_parameters': {'cap_rate': 0.10}
        })

        weights = calc._get_dynamic_weights()

        self.assertIn('reasoning', weights)
        self.assertIn('voltage', weights['reasoning'].lower())
        self.assertIn('percentage of fee', weights['reasoning'].lower())

    def test_user_override_weights(self):
        """Test user can override default hydro weights."""
        calc = HydroEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 1000000},
            'easement': {'voltage_kv': 230, 'area_acres': 5},
            'market_parameters': {
                'cap_rate': 0.10,
                'reconciliation_weights': {
                    'percentage_of_fee': 0.60,
                    'income_capitalization': 0.25,
                    'before_after': 0.15
                }
            }
        })

        weights = calc._get_dynamic_weights()

        self.assertEqual(weights['percentage_of_fee'], 0.60)
        self.assertEqual(weights['income_capitalization'], 0.25)
        self.assertEqual(weights['before_after'], 0.15)


class TestHydroIntegrationWorkflows(unittest.TestCase):
    """Test complete hydro valuation workflows."""

    def test_230kv_agricultural_complete(self):
        """Test complete 230kV agricultural easement valuation."""
        calc = HydroEasementCalculator({
            'property': {
                'address': '100 acres agricultural',
                'total_acres': 100,
                'fee_simple_value': 1200000
            },
            'easement': {
                'voltage_kv': 230,
                'area_acres': 15,
                'width_meters': 60,
                'tower_count': 2,
                'vegetation_restrictions': ['tree_clearing'],
                'restrictions': ['no_buildings', 'height_restrictions'],
                'hbu_impact': 'moderate',
                'productivity_loss_pct': 0.20
            },
            'market_parameters': {
                'cap_rate': 0.045,
                'annual_rent_per_acre': 300
            }
        })

        result = calc.calculate_all_methods()

        # Verify calculation completed
        self.assertEqual(result['easement_classification'], 'Permanent Easement')
        self.assertIn('valuation_methods', result)
        self.assertIn('reconciliation', result)
        self.assertIn('sensitivity_analysis', result)

        # Verify percentage of fee includes EMF adjustment
        pct_method = result['valuation_methods']['percentage_of_fee']
        self.assertEqual(pct_method['base_percentage'], 17.5)  # 230kV
        self.assertIn('emf_concern', pct_method['adjustments'])
        self.assertEqual(pct_method['adjustments']['emf_concern'], 2.0)

        # Verify hydro-specific weights used
        self.assertEqual(result['reconciliation']['weights']['percentage_of_fee'], 0.50)

    def test_500kv_industrial_complete(self):
        """Test complete 500kV industrial easement valuation."""
        calc = HydroEasementCalculator({
            'property': {
                'address': '50 acres industrial',
                'total_acres': 50,
                'fee_simple_value': 2500000
            },
            'easement': {
                'voltage_kv': 500,
                'area_acres': 10,
                'width_meters': 100,
                'tower_count': 3,
                'requires_access_road': True,
                'distance_to_buildings_m': 45,
                'restrictions': ['no_buildings', 'no_trees', 'height_restrictions'],
                'hbu_impact': 'major',
                'productivity_loss_pct': 0.25
            },
            'market_parameters': {
                'cap_rate': 0.06,
                'annual_rent_per_acre': 5000
            }
        })

        result = calc.calculate_all_methods()

        # Verify 500kV base percentage
        pct_method = result['valuation_methods']['percentage_of_fee']
        self.assertEqual(pct_method['base_percentage'], 22.5)

        # Verify multiple domain adjustments applied
        adjustments = pct_method['adjustments']
        self.assertEqual(adjustments['emf_concern'], 2.0)           # 500kV
        self.assertEqual(adjustments['tower_placement'], 1.5)       # 3 towers
        self.assertEqual(adjustments['access_road'], 1.0)
        self.assertEqual(adjustments['proximity_impact'], 2.5)      # <50m to buildings

    def test_69kv_residential_complete(self):
        """Test complete 69kV residential area easement valuation."""
        calc = HydroEasementCalculator({
            'property': {
                'address': '5 acres residential',
                'total_acres': 5,
                'fee_simple_value': 750000
            },
            'easement': {
                'voltage_kv': 69,
                'area_acres': 1,
                'width_meters': 20,
                'tower_count': 1,
                'restrictions': ['no_buildings'],
                'hbu_impact': 'major',
                'productivity_loss_pct': 0.30
            },
            'market_parameters': {
                'cap_rate': 0.05
            }
        })

        result = calc.calculate_all_methods()

        # Verify 69kV base percentage
        pct_method = result['valuation_methods']['percentage_of_fee']
        self.assertEqual(pct_method['base_percentage'], 12.5)

        # Verify NO EMF adjustment (<230kV)
        self.assertNotIn('emf_concern', pct_method['adjustments'])


class TestHydroTCE(unittest.TestCase):
    """Test hydro TCE scenarios."""

    def test_hydro_tce_90day_construction(self):
        """Test 90-day TCE for transmission line construction."""
        calc = HydroEasementCalculator({
            'property': {
                'address': '10 acres industrial',
                'total_acres': 10,
                'fee_simple_value': 500000
            },
            'easement': {
                'voltage_kv': 230,
                'area_acres': 3,
                'term': 'tce',
                'duration_days': 90,
                'restoration_costs': 20000,
                'business_losses': 10000
            },
            'market_parameters': {
                'cap_rate': 0.08,
                'tce_annual_rate': 0.12
            }
        })

        result = calc.calculate_all_methods()

        # Verify TCE classification
        self.assertEqual(result['easement_classification'], 'Temporary Construction Easement (TCE)')

        # Verify TCE calculation
        tce_method = result['valuation_method']
        self.assertEqual(tce_method['method'], 'TCE Rate-of-Return')
        self.assertEqual(tce_method['duration_days'], 90)
        self.assertEqual(tce_method['annual_rate'], 0.12)

        # Calculate expected rental: $150,000 (3 acres × $50,000/acre) × 12% × (90÷365) = $4,438
        expected_rental = (500000 / 10) * 3 * 0.12 * (90 / 365)
        self.assertAlmostEqual(tce_method['rental_value'], expected_rental, places=0)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
