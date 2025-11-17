#!/usr/bin/env python3
"""
Comprehensive Test Suite for Rail Easement Calculator

Tests rail-specific functionality:
1. Rail type-based percentage calculation
2. Rail alignment adjustments (elevated, at-grade, subway/tunnel, trench)
3. Train frequency impacts
4. Grade crossing safety adjustments
5. Vibration impact assessments
6. Noise barrier considerations
7. Service hours and diesel emissions
8. Rail-specific reconciliation weights

Author: Claude Code
Created: 2025-11-17
Updated: 2025-11-17 (added alignment tests)
Version: 2.0.1
"""

import unittest
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from rail_easement_calculator import RailEasementCalculator


class TestRailTypeTiers(unittest.TestCase):
    """Test rail type-based percentage calculation."""

    def test_heavy_rail_freight_percentage(self):
        """Test heavy rail freight gets 25.0% base percentage."""
        calc = RailEasementCalculator({
            'property': {'total_acres': 50, 'fee_simple_value': 2500000},
            'easement': {'rail_type': 'heavy_rail_freight', 'area_acres': 5},
            'market_parameters': {'cap_rate': 0.06}
        })
        self.assertEqual(calc.get_base_percentage(), 25.0)

    def test_heavy_rail_passenger_percentage(self):
        """Test heavy rail passenger gets 23.0% base percentage."""
        calc = RailEasementCalculator({
            'property': {'total_acres': 50, 'fee_simple_value': 2500000},
            'easement': {'rail_type': 'heavy_rail_passenger', 'area_acres': 5},
            'market_parameters': {'cap_rate': 0.06}
        })
        self.assertEqual(calc.get_base_percentage(), 23.0)

    def test_light_rail_percentage(self):
        """Test light rail gets 20.0% base percentage."""
        calc = RailEasementCalculator({
            'property': {'total_acres': 20, 'fee_simple_value': 1500000},
            'easement': {'rail_type': 'light_rail', 'area_acres': 3},
            'market_parameters': {'cap_rate': 0.05}
        })
        self.assertEqual(calc.get_base_percentage(), 20.0)

    def test_subway_surface_percentage(self):
        """Test subway surface gets 22.0% base percentage."""
        calc = RailEasementCalculator({
            'property': {'total_acres': 10, 'fee_simple_value': 3000000},
            'easement': {'rail_type': 'subway_surface', 'area_acres': 2},
            'market_parameters': {'cap_rate': 0.055}
        })
        self.assertEqual(calc.get_base_percentage(), 22.0)

    def test_bus_rapid_transit_percentage(self):
        """Test BRT gets 15.0% base percentage."""
        calc = RailEasementCalculator({
            'property': {'total_acres': 30, 'fee_simple_value': 1800000},
            'easement': {'rail_type': 'bus_rapid_transit', 'area_acres': 4},
            'market_parameters': {'cap_rate': 0.05}
        })
        self.assertEqual(calc.get_base_percentage(), 15.0)

    def test_missing_rail_type_raises_error(self):
        """Test missing rail_type parameter raises clear error."""
        with self.assertRaises(ValueError) as context:
            calc = RailEasementCalculator({
                'property': {'total_acres': 50, 'fee_simple_value': 2500000},
                'easement': {'area_acres': 5},
                'market_parameters': {'cap_rate': 0.06}
            })
            calc.get_base_percentage()

        self.assertIn('rail_type', str(context.exception))
        self.assertIn('REQUIRED', str(context.exception).upper())

    def test_invalid_rail_type_raises_error(self):
        """Test invalid rail_type raises error with valid options."""
        with self.assertRaises(ValueError) as context:
            calc = RailEasementCalculator({
                'property': {'total_acres': 50, 'fee_simple_value': 2500000},
                'easement': {'rail_type': 'invalid_type', 'area_acres': 5},
                'market_parameters': {'cap_rate': 0.06}
            })
            calc.get_base_percentage()

        self.assertIn('Invalid rail_type', str(context.exception))
        self.assertIn('heavy_rail_freight', str(context.exception))


class TestRailDomainAdjustments(unittest.TestCase):
    """Test rail-specific percentage adjustments."""

    def test_high_frequency_adjustment(self):
        """Test high frequency adjustment for >50 trains/day."""
        calc = RailEasementCalculator({
            'property': {'total_acres': 50, 'fee_simple_value': 2500000},
            'easement': {
                'rail_type': 'heavy_rail_freight',
                'area_acres': 5,
                'trains_per_day': 60
            },
            'market_parameters': {'cap_rate': 0.06}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertEqual(adjustments.get('high_frequency'), 3.0)

    def test_moderate_frequency_adjustment(self):
        """Test moderate frequency adjustment for 20-50 trains/day."""
        calc = RailEasementCalculator({
            'property': {'total_acres': 50, 'fee_simple_value': 2500000},
            'easement': {
                'rail_type': 'heavy_rail_freight',
                'area_acres': 5,
                'trains_per_day': 35
            },
            'market_parameters': {'cap_rate': 0.06}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertEqual(adjustments.get('moderate_frequency'), 1.5)

    def test_grade_crossing_single(self):
        """Test grade crossing adjustment for single crossing."""
        calc = RailEasementCalculator({
            'property': {'total_acres': 50, 'fee_simple_value': 2500000},
            'easement': {
                'rail_type': 'heavy_rail_freight',
                'area_acres': 5,
                'grade_crossings': 1
            },
            'market_parameters': {'cap_rate': 0.06}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertEqual(adjustments.get('grade_crossing_safety'), 1.0)

    def test_grade_crossing_multiple(self):
        """Test grade crossing adjustment for multiple crossings."""
        calc = RailEasementCalculator({
            'property': {'total_acres': 50, 'fee_simple_value': 2500000},
            'easement': {
                'rail_type': 'heavy_rail_freight',
                'area_acres': 5,
                'grade_crossings': 2
            },
            'market_parameters': {'cap_rate': 0.06}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertEqual(adjustments.get('grade_crossing_safety'), 2.0)

    def test_grade_crossing_capped(self):
        """Test grade crossing adjustment capped at +3%."""
        calc = RailEasementCalculator({
            'property': {'total_acres': 50, 'fee_simple_value': 2500000},
            'easement': {
                'rail_type': 'heavy_rail_freight',
                'area_acres': 5,
                'grade_crossings': 5
            },
            'market_parameters': {'cap_rate': 0.06}
        })
        adjustments = calc.get_domain_specific_adjustments()
        # 5 crossings × 1% = 5%, capped at 3%
        self.assertEqual(adjustments.get('grade_crossing_safety'), 3.0)

    def test_vibration_heavy_rail_close(self):
        """Test vibration impact for heavy rail <30m to buildings."""
        calc = RailEasementCalculator({
            'property': {'total_acres': 50, 'fee_simple_value': 2500000},
            'easement': {
                'rail_type': 'heavy_rail_freight',
                'area_acres': 5,
                'distance_to_buildings_m': 25
            },
            'market_parameters': {'cap_rate': 0.06}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertEqual(adjustments.get('vibration_impact'), 2.5)

    def test_vibration_any_rail_moderate(self):
        """Test vibration impact for any rail <50m to buildings."""
        calc = RailEasementCalculator({
            'property': {'total_acres': 20, 'fee_simple_value': 1500000},
            'easement': {
                'rail_type': 'light_rail',
                'area_acres': 3,
                'distance_to_buildings_m': 45
            },
            'market_parameters': {'cap_rate': 0.05}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertEqual(adjustments.get('vibration_impact'), 1.5)

    def test_no_noise_mitigation(self):
        """Test no noise barriers with significant frequency."""
        calc = RailEasementCalculator({
            'property': {'total_acres': 50, 'fee_simple_value': 2500000},
            'easement': {
                'rail_type': 'heavy_rail_passenger',
                'area_acres': 5,
                'has_noise_barriers': False,
                'trains_per_day': 30
            },
            'market_parameters': {'cap_rate': 0.06}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertEqual(adjustments.get('no_noise_mitigation'), 2.0)

    def test_extended_hours_24hour_service(self):
        """Test extended hours adjustment for 24-hour service."""
        calc = RailEasementCalculator({
            'property': {'total_acres': 50, 'fee_simple_value': 2500000},
            'easement': {
                'rail_type': 'subway_surface',
                'area_acres': 3,
                'service_hours_per_day': 24
            },
            'market_parameters': {'cap_rate': 0.055}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertEqual(adjustments.get('extended_hours'), 1.5)

    def test_diesel_emissions(self):
        """Test diesel emissions adjustment for non-electrified heavy rail."""
        calc = RailEasementCalculator({
            'property': {'total_acres': 50, 'fee_simple_value': 2500000},
            'easement': {
                'rail_type': 'heavy_rail_freight',
                'area_acres': 5,
                'is_electrified': False
            },
            'market_parameters': {'cap_rate': 0.06}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertEqual(adjustments.get('diesel_emissions'), 1.0)

    def test_hazmat_risk_perception(self):
        """Test hazmat risk perception for freight rail."""
        calc = RailEasementCalculator({
            'property': {'total_acres': 50, 'fee_simple_value': 2500000},
            'easement': {
                'rail_type': 'heavy_rail_freight',
                'area_acres': 5,
                'hazmat_traffic': True
            },
            'market_parameters': {'cap_rate': 0.06}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertEqual(adjustments.get('hazmat_risk_perception'), 1.5)

    def test_combined_adjustments_freight(self):
        """Test all rail-specific adjustments combined for freight corridor."""
        calc = RailEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 5000000},
            'easement': {
                'rail_type': 'heavy_rail_freight',
                'area_acres': 10,
                'trains_per_day': 60,
                'grade_crossings': 2,
                'distance_to_buildings_m': 20,
                'has_noise_barriers': False,
                'is_electrified': False,
                'hazmat_traffic': True
            },
            'market_parameters': {'cap_rate': 0.06}
        })
        adjustments = calc.get_domain_specific_adjustments()

        # High frequency: +3.0%
        # Grade crossings (2): +2.0%
        # Vibration (<30m heavy rail): +2.5%
        # No noise barriers: +2.0%
        # Diesel emissions: +1.0%
        # Hazmat risk: +1.5%
        # Total: +12.0%

        total = sum(adjustments.values())
        self.assertEqual(total, 12.0)

    def test_elevated_alignment_adjustment(self):
        """Test elevated rail alignment gets +2% adjustment."""
        calc = RailEasementCalculator({
            'property': {'total_acres': 50, 'fee_simple_value': 2500000},
            'easement': {
                'rail_type': 'light_rail',
                'area_acres': 3,
                'rail_alignment': 'elevated'
            },
            'market_parameters': {'cap_rate': 0.06}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertEqual(adjustments.get('elevated_alignment'), 2.0)

    def test_at_grade_alignment_no_adjustment(self):
        """Test at-grade alignment has no adjustment (baseline)."""
        calc = RailEasementCalculator({
            'property': {'total_acres': 50, 'fee_simple_value': 2500000},
            'easement': {
                'rail_type': 'light_rail',
                'area_acres': 3,
                'rail_alignment': 'at_grade'
            },
            'market_parameters': {'cap_rate': 0.06}
        })
        adjustments = calc.get_domain_specific_adjustments()
        # at_grade should not have an alignment adjustment (baseline = 0%)
        self.assertNotIn('elevated_alignment', adjustments)
        self.assertNotIn('subway_tunnel_alignment', adjustments)
        self.assertNotIn('trench_alignment', adjustments)

    def test_subway_tunnel_alignment_adjustment(self):
        """Test subway/tunnel alignment gets -3% adjustment (subsurface)."""
        calc = RailEasementCalculator({
            'property': {'total_acres': 10, 'fee_simple_value': 3000000},
            'easement': {
                'rail_type': 'subway_surface',
                'area_acres': 2,
                'rail_alignment': 'subway_tunnel'
            },
            'market_parameters': {'cap_rate': 0.055}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertEqual(adjustments.get('subway_tunnel_alignment'), -3.0)

    def test_trench_alignment_adjustment(self):
        """Test trench/cut alignment gets -1% adjustment (partially subsurface)."""
        calc = RailEasementCalculator({
            'property': {'total_acres': 30, 'fee_simple_value': 1800000},
            'easement': {
                'rail_type': 'heavy_rail_passenger',
                'area_acres': 4,
                'rail_alignment': 'trench'
            },
            'market_parameters': {'cap_rate': 0.06}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertEqual(adjustments.get('trench_alignment'), -1.0)

    def test_default_alignment_is_at_grade(self):
        """Test that omitting rail_alignment defaults to at_grade (no adjustment)."""
        calc = RailEasementCalculator({
            'property': {'total_acres': 50, 'fee_simple_value': 2500000},
            'easement': {
                'rail_type': 'light_rail',
                'area_acres': 3
                # rail_alignment not specified - should default to 'at_grade'
            },
            'market_parameters': {'cap_rate': 0.06}
        })
        adjustments = calc.get_domain_specific_adjustments()
        # Should behave like at_grade (no alignment adjustment)
        self.assertNotIn('elevated_alignment', adjustments)
        self.assertNotIn('subway_tunnel_alignment', adjustments)
        self.assertNotIn('trench_alignment', adjustments)


class TestRailReconciliationWeights(unittest.TestCase):
    """Test rail-specific reconciliation weights."""

    def test_rail_default_weights(self):
        """Test rail corridors use 50/20/30 weights."""
        calc = RailEasementCalculator({
            'property': {'total_acres': 50, 'fee_simple_value': 2500000},
            'easement': {'rail_type': 'heavy_rail_freight', 'area_acres': 5},
            'market_parameters': {'cap_rate': 0.06}
        })

        weights = calc._get_dynamic_weights()

        self.assertEqual(weights['percentage_of_fee'], 0.50)
        self.assertEqual(weights['income_capitalization'], 0.20)
        self.assertEqual(weights['before_after'], 0.30)

    def test_rail_weights_reasoning(self):
        """Test rail weights include professional reasoning."""
        calc = RailEasementCalculator({
            'property': {'total_acres': 50, 'fee_simple_value': 2500000},
            'easement': {'rail_type': 'heavy_rail_freight', 'area_acres': 5},
            'market_parameters': {'cap_rate': 0.06}
        })

        weights = calc._get_dynamic_weights()

        self.assertIn('reasoning', weights)
        self.assertIn('rail', weights['reasoning'].lower())
        self.assertIn('noise', weights['reasoning'].lower() or 'vibration' in weights['reasoning'].lower())


class TestRailIntegrationWorkflows(unittest.TestCase):
    """Test complete rail valuation workflows."""

    def test_heavy_freight_complete(self):
        """Test complete heavy rail freight corridor valuation."""
        calc = RailEasementCalculator({
            'property': {
                'address': '100 acres industrial/agricultural',
                'total_acres': 100,
                'fee_simple_value': 5000000
            },
            'easement': {
                'rail_type': 'heavy_rail_freight',
                'area_acres': 10,
                'width_meters': 30,
                'trains_per_day': 40,
                'grade_crossings': 1,
                'distance_to_buildings_m': 60,
                'has_noise_barriers': False,
                'is_electrified': False,
                'hazmat_traffic': True,
                'restrictions': ['no_buildings', 'excavation_prohibited'],
                'hbu_impact': 'major',
                'productivity_loss_pct': 0.25
            },
            'market_parameters': {
                'cap_rate': 0.06,
                'annual_rent_per_acre': 2500
            }
        })

        result = calc.calculate_all_methods()

        # Verify calculation completed
        self.assertEqual(result['easement_classification'], 'Permanent Easement')

        # Verify heavy rail freight base
        pct_method = result['valuation_methods']['percentage_of_fee']
        self.assertEqual(pct_method['base_percentage'], 25.0)

        # Verify rail-specific adjustments
        adjustments = pct_method['adjustments']
        self.assertEqual(adjustments['moderate_frequency'], 1.5)  # 40 trains/day
        self.assertEqual(adjustments['grade_crossing_safety'], 1.0)  # 1 crossing
        self.assertEqual(adjustments['no_noise_mitigation'], 2.0)  # No barriers, >10 trains
        self.assertEqual(adjustments['diesel_emissions'], 1.0)
        self.assertEqual(adjustments['hazmat_risk_perception'], 1.5)

        # Verify rail-specific weights
        self.assertEqual(result['reconciliation']['weights']['percentage_of_fee'], 0.50)
        self.assertEqual(result['reconciliation']['weights']['before_after'], 0.30)

    def test_light_rail_urban_complete(self):
        """Test complete light rail urban corridor valuation."""
        calc = RailEasementCalculator({
            'property': {
                'address': '20 acres commercial/residential',
                'total_acres': 20,
                'fee_simple_value': 8000000
            },
            'easement': {
                'rail_type': 'light_rail',
                'area_acres': 3,
                'width_meters': 20,
                'trains_per_day': 120,
                'grade_crossings': 3,
                'distance_to_buildings_m': 15,
                'has_noise_barriers': True,
                'service_hours_per_day': 20,
                'is_electrified': True,
                'restrictions': ['no_buildings', 'height_restrictions'],
                'hbu_impact': 'precludes_development',
                'productivity_loss_pct': 0.35
            },
            'market_parameters': {
                'cap_rate': 0.055,
                'annual_rent_per_acre': 15000
            }
        })

        result = calc.calculate_all_methods()

        # Verify light rail base
        pct_method = result['valuation_methods']['percentage_of_fee']
        self.assertEqual(pct_method['base_percentage'], 20.0)

        # Verify high frequency impact
        adjustments = pct_method['adjustments']
        self.assertEqual(adjustments['high_frequency'], 3.0)  # >50 trains/day
        self.assertEqual(adjustments['grade_crossing_safety'], 3.0)  # 3 crossings (capped)
        self.assertEqual(adjustments['vibration_impact'], 1.5)  # <50m to buildings
        self.assertEqual(adjustments['extended_hours'], 1.5)  # 20 hours/day

    def test_brt_corridor_complete(self):
        """Test complete BRT corridor valuation."""
        calc = RailEasementCalculator({
            'property': {
                'address': '30 acres commercial',
                'total_acres': 30,
                'fee_simple_value': 6000000
            },
            'easement': {
                'rail_type': 'bus_rapid_transit',
                'area_acres': 4,
                'width_meters': 15,
                'trains_per_day': 25,  # "trains" for BRT = buses
                'grade_crossings': 0,
                'restrictions': ['access_limitations'],
                'hbu_impact': 'moderate',
                'productivity_loss_pct': 0.15
            },
            'market_parameters': {
                'cap_rate': 0.05,
                'annual_rent_per_acre': 10000
            }
        })

        result = calc.calculate_all_methods()

        # Verify BRT base (lower impact)
        pct_method = result['valuation_methods']['percentage_of_fee']
        self.assertEqual(pct_method['base_percentage'], 15.0)


class TestRailTCE(unittest.TestCase):
    """Test rail TCE scenarios."""

    def test_rail_tce_construction(self):
        """Test 120-day TCE for rail construction."""
        calc = RailEasementCalculator({
            'property': {
                'address': '20 acres commercial',
                'total_acres': 20,
                'fee_simple_value': 4000000
            },
            'easement': {
                'rail_type': 'light_rail',
                'area_acres': 4,
                'term': 'tce',
                'duration_days': 120,
                'restoration_costs': 50000,
                'business_losses': 75000
            },
            'market_parameters': {
                'cap_rate': 0.055,
                'tce_annual_rate': 0.15  # Higher rate for urban disruption
            }
        })

        result = calc.calculate_all_methods()

        # Verify TCE classification
        self.assertEqual(result['easement_classification'], 'Temporary Construction Easement (TCE)')

        # Verify TCE calculation
        tce_method = result['valuation_method']
        self.assertEqual(tce_method['duration_days'], 120)
        self.assertEqual(tce_method['annual_rate'], 0.15)

        # Calculate expected rental: $800,000 (4 acres × $200,000/acre) × 15% × (120÷365) = $39,452
        expected_rental = (4000000 / 20) * 4 * 0.15 * (120 / 365)
        self.assertAlmostEqual(tce_method['rental_value'], expected_rental, places=0)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
