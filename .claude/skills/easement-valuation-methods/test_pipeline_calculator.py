#!/usr/bin/env python3
"""
Comprehensive Test Suite for Pipeline Easement Calculator

Tests pipeline-specific functionality:
1. Pipeline type and pressure-based percentage calculation
2. Burial depth adjustments
3. Diameter impact assessments
4. Leak detection systems
5. Water proximity concerns
6. Pipeline age and condition
7. Pipeline-specific reconciliation weights

Author: Claude Code
Created: 2025-11-17
Version: 2.0.0
"""

import unittest
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from pipeline_easement_calculator import PipelineEasementCalculator


class TestPipelineTypeTiers(unittest.TestCase):
    """Test pipeline type-based percentage calculation."""

    def test_crude_oil_transmission_percentage(self):
        """Test crude oil transmission gets 18.0% base."""
        calc = PipelineEasementCalculator({
            'property': {'total_acres': 200, 'fee_simple_value': 3000000},
            'easement': {
                'pipeline_type': 'crude_oil_transmission',
                'area_acres': 5,
                'pressure_psi': 800
            },
            'market_parameters': {'cap_rate': 0.05}
        })
        base = calc.get_base_percentage()
        self.assertEqual(base, 18.0)

    def test_crude_oil_high_pressure_adjustment(self):
        """Test crude oil transmission with high pressure gets +2%."""
        calc = PipelineEasementCalculator({
            'property': {'total_acres': 200, 'fee_simple_value': 3000000},
            'easement': {
                'pipeline_type': 'crude_oil_transmission',
                'area_acres': 5,
                'pressure_psi': 1200
            },
            'market_parameters': {'cap_rate': 0.05}
        })
        base = calc.get_base_percentage()
        self.assertEqual(base, 20.0)  # 18.0 + 2.0 for >1000 psi

    def test_natural_gas_transmission_percentage(self):
        """Test natural gas transmission gets 16.0% base."""
        calc = PipelineEasementCalculator({
            'property': {'total_acres': 150, 'fee_simple_value': 2250000},
            'easement': {
                'pipeline_type': 'natural_gas_transmission',
                'area_acres': 4,
                'pressure_psi': 900
            },
            'market_parameters': {'cap_rate': 0.05}
        })
        base = calc.get_base_percentage()
        self.assertEqual(base, 16.0)

    def test_natural_gas_distribution_percentage(self):
        """Test natural gas distribution gets 12.0% base."""
        calc = PipelineEasementCalculator({
            'property': {'total_acres': 50, 'fee_simple_value': 1500000},
            'easement': {
                'pipeline_type': 'natural_gas_distribution',
                'area_acres': 2,
                'pressure_psi': 150
            },
            'market_parameters': {'cap_rate': 0.055}
        })
        base = calc.get_base_percentage()
        self.assertEqual(base, 12.0)

    def test_water_transmission_percentage(self):
        """Test water transmission gets 11.0% base."""
        calc = PipelineEasementCalculator({
            'property': {'total_acres': 100, 'fee_simple_value': 1200000},
            'easement': {
                'pipeline_type': 'water_transmission',
                'area_acres': 3
            },
            'market_parameters': {'cap_rate': 0.05}
        })
        base = calc.get_base_percentage()
        self.assertEqual(base, 11.0)

    def test_sewer_percentage(self):
        """Test sewer gets 10.0% base."""
        calc = PipelineEasementCalculator({
            'property': {'total_acres': 75, 'fee_simple_value': 900000},
            'easement': {
                'pipeline_type': 'sewer',
                'area_acres': 2
            },
            'market_parameters': {'cap_rate': 0.05}
        })
        base = calc.get_base_percentage()
        self.assertEqual(base, 10.0)

    def test_missing_pipeline_type_raises_error(self):
        """Test missing pipeline_type parameter raises clear error."""
        with self.assertRaises(ValueError) as context:
            calc = PipelineEasementCalculator({
                'property': {'total_acres': 200, 'fee_simple_value': 3000000},
                'easement': {'area_acres': 5},
                'market_parameters': {'cap_rate': 0.05}
            })
            calc.get_base_percentage()

        self.assertIn('pipeline_type', str(context.exception))
        self.assertIn('REQUIRED', str(context.exception).upper())


class TestPipelineDomainAdjustments(unittest.TestCase):
    """Test pipeline-specific percentage adjustments."""

    def test_shallow_burial_adjustment(self):
        """Test shallow burial (<1m) adjustment."""
        calc = PipelineEasementCalculator({
            'property': {'total_acres': 200, 'fee_simple_value': 3000000},
            'easement': {
                'pipeline_type': 'natural_gas_transmission',
                'area_acres': 5,
                'depth_meters': 0.8
            },
            'market_parameters': {'cap_rate': 0.05}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertEqual(adjustments.get('shallow_burial'), 1.5)

    def test_deep_burial_adjustment(self):
        """Test deep burial (>3m) adjustment."""
        calc = PipelineEasementCalculator({
            'property': {'total_acres': 200, 'fee_simple_value': 3000000},
            'easement': {
                'pipeline_type': 'natural_gas_transmission',
                'area_acres': 5,
                'depth_meters': 3.5
            },
            'market_parameters': {'cap_rate': 0.05}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertEqual(adjustments.get('deep_burial'), -0.5)

    def test_large_diameter_adjustment(self):
        """Test large diameter (>750mm) adjustment."""
        calc = PipelineEasementCalculator({
            'property': {'total_acres': 200, 'fee_simple_value': 3000000},
            'easement': {
                'pipeline_type': 'crude_oil_transmission',
                'area_acres': 5,
                'diameter_mm': 800
            },
            'market_parameters': {'cap_rate': 0.05}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertEqual(adjustments.get('large_diameter'), 1.0)

    def test_very_large_diameter_adjustment(self):
        """Test very large diameter (>1000mm) adjustment."""
        calc = PipelineEasementCalculator({
            'property': {'total_acres': 200, 'fee_simple_value': 3000000},
            'easement': {
                'pipeline_type': 'crude_oil_transmission',
                'area_acres': 5,
                'diameter_mm': 1200
            },
            'market_parameters': {'cap_rate': 0.05}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertEqual(adjustments.get('very_large_diameter'), 2.0)

    def test_leak_detection_systems(self):
        """Test leak detection systems mitigation."""
        calc = PipelineEasementCalculator({
            'property': {'total_acres': 200, 'fee_simple_value': 3000000},
            'easement': {
                'pipeline_type': 'natural_gas_transmission',
                'area_acres': 5,
                'has_leak_detection': True
            },
            'market_parameters': {'cap_rate': 0.05}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertEqual(adjustments.get('leak_detection_systems'), -0.5)

    def test_no_cathodic_protection(self):
        """Test no cathodic protection adjustment."""
        calc = PipelineEasementCalculator({
            'property': {'total_acres': 200, 'fee_simple_value': 3000000},
            'easement': {
                'pipeline_type': 'natural_gas_transmission',
                'area_acres': 5,
                'has_cathodic_protection': False
            },
            'market_parameters': {'cap_rate': 0.05}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertEqual(adjustments.get('no_corrosion_protection'), 1.0)

    def test_access_road_requirement(self):
        """Test access road requirement adjustment."""
        calc = PipelineEasementCalculator({
            'property': {'total_acres': 200, 'fee_simple_value': 3000000},
            'easement': {
                'pipeline_type': 'natural_gas_transmission',
                'area_acres': 5,
                'requires_access_road': True
            },
            'market_parameters': {'cap_rate': 0.05}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertEqual(adjustments.get('access_road'), 1.0)

    def test_water_proximity_crude_oil(self):
        """Test water proximity for crude oil pipeline."""
        calc = PipelineEasementCalculator({
            'property': {'total_acres': 200, 'fee_simple_value': 3000000},
            'easement': {
                'pipeline_type': 'crude_oil_transmission',
                'area_acres': 5,
                'distance_to_water_m': 75
            },
            'market_parameters': {'cap_rate': 0.05}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertEqual(adjustments.get('water_proximity_risk'), 2.0)

    def test_water_proximity_other_pipeline(self):
        """Test water proximity for non-crude pipeline."""
        calc = PipelineEasementCalculator({
            'property': {'total_acres': 200, 'fee_simple_value': 3000000},
            'easement': {
                'pipeline_type': 'natural_gas_transmission',
                'area_acres': 5,
                'distance_to_water_m': 80
            },
            'market_parameters': {'cap_rate': 0.05}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertEqual(adjustments.get('water_proximity'), 1.0)

    def test_hdd_installation_method(self):
        """Test HDD installation method mitigation."""
        calc = PipelineEasementCalculator({
            'property': {'total_acres': 200, 'fee_simple_value': 3000000},
            'easement': {
                'pipeline_type': 'natural_gas_transmission',
                'area_acres': 5,
                'installation_method': 'hdd'
            },
            'market_parameters': {'cap_rate': 0.05}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertEqual(adjustments.get('hdd_installation'), -0.5)

    def test_extra_wide_row(self):
        """Test extra-wide ROW adjustment."""
        calc = PipelineEasementCalculator({
            'property': {'total_acres': 200, 'fee_simple_value': 3000000},
            'easement': {
                'pipeline_type': 'natural_gas_transmission',
                'area_acres': 5,
                'width_meters': 35
            },
            'market_parameters': {'cap_rate': 0.05}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertEqual(adjustments.get('extra_wide_row'), 1.5)

    def test_aging_infrastructure(self):
        """Test aging infrastructure adjustment."""
        calc = PipelineEasementCalculator({
            'property': {'total_acres': 200, 'fee_simple_value': 3000000},
            'easement': {
                'pipeline_type': 'natural_gas_transmission',
                'area_acres': 5,
                'pipeline_age_years': 45
            },
            'market_parameters': {'cap_rate': 0.05}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertEqual(adjustments.get('aging_infrastructure'), 1.0)

    def test_high_consequence_area(self):
        """Test high consequence area (Class 3/4) adjustment."""
        calc = PipelineEasementCalculator({
            'property': {'total_acres': 200, 'fee_simple_value': 3000000},
            'easement': {
                'pipeline_type': 'natural_gas_transmission',
                'area_acres': 5,
                'class_location': 3
            },
            'market_parameters': {'cap_rate': 0.05}
        })
        adjustments = calc.get_domain_specific_adjustments()
        self.assertEqual(adjustments.get('high_consequence_area'), 1.5)

    def test_combined_adjustments_high_risk(self):
        """Test combined adjustments for high-risk pipeline."""
        calc = PipelineEasementCalculator({
            'property': {'total_acres': 300, 'fee_simple_value': 4500000},
            'easement': {
                'pipeline_type': 'crude_oil_transmission',
                'area_acres': 8,
                'pressure_psi': 1200,
                'diameter_mm': 1000,
                'depth_meters': 0.9,
                'has_leak_detection': False,
                'has_cathodic_protection': False,
                'distance_to_water_m': 60,
                'pipeline_age_years': 42,
                'class_location': 3
            },
            'market_parameters': {'cap_rate': 0.05}
        })
        adjustments = calc.get_domain_specific_adjustments()

        # Shallow burial: +1.5%
        # Large diameter (>750mm): +1.0%
        # No cathodic protection: +1.0%
        # Water proximity (crude <100m): +2.0%
        # Aging infrastructure (>40 years): +1.0%
        # High consequence area (Class 3): +1.5%
        # Total domain adjustments: +8.0%

        total = sum(adjustments.values())
        self.assertEqual(total, 8.0)


class TestPipelineReconciliationWeights(unittest.TestCase):
    """Test pipeline-specific reconciliation weights."""

    def test_pipeline_default_weights(self):
        """Test pipeline corridors use 45/30/25 weights."""
        calc = PipelineEasementCalculator({
            'property': {'total_acres': 200, 'fee_simple_value': 3000000},
            'easement': {
                'pipeline_type': 'natural_gas_transmission',
                'area_acres': 5
            },
            'market_parameters': {'cap_rate': 0.05}
        })

        weights = calc._get_dynamic_weights()

        self.assertEqual(weights['percentage_of_fee'], 0.45)
        self.assertEqual(weights['income_capitalization'], 0.30)
        self.assertEqual(weights['before_after'], 0.25)

    def test_pipeline_weights_reasoning(self):
        """Test pipeline weights include professional reasoning."""
        calc = PipelineEasementCalculator({
            'property': {'total_acres': 200, 'fee_simple_value': 3000000},
            'easement': {
                'pipeline_type': 'natural_gas_transmission',
                'area_acres': 5
            },
            'market_parameters': {'cap_rate': 0.05}
        })

        weights = calc._get_dynamic_weights()

        self.assertIn('reasoning', weights)
        self.assertIn('pipeline', weights['reasoning'].lower())


class TestPipelineIntegrationWorkflows(unittest.TestCase):
    """Test complete pipeline valuation workflows."""

    def test_natural_gas_transmission_complete(self):
        """Test complete natural gas transmission easement valuation."""
        calc = PipelineEasementCalculator({
            'property': {
                'address': '200 acres agricultural',
                'total_acres': 200,
                'fee_simple_value': 3000000
            },
            'easement': {
                'pipeline_type': 'natural_gas_transmission',
                'area_acres': 5,
                'width_meters': 20,
                'pressure_psi': 1200,
                'diameter_mm': 600,
                'depth_meters': 1.5,
                'has_leak_detection': True,
                'has_cathodic_protection': True,
                'distance_to_water_m': 250,
                'installation_method': 'open_cut',
                'pipeline_age_years': 15,
                'class_location': 2,
                'restrictions': ['excavation_prohibited'],
                'hbu_impact': 'minor',
                'productivity_loss_pct': 0.15
            },
            'market_parameters': {
                'cap_rate': 0.05,
                'annual_rent_per_acre': 400
            }
        })

        result = calc.calculate_all_methods()

        # Verify calculation completed
        self.assertEqual(result['easement_classification'], 'Permanent Easement')

        # Verify natural gas transmission base with pressure adjustment
        pct_method = result['valuation_methods']['percentage_of_fee']
        self.assertEqual(pct_method['base_percentage'], 18.0)  # 16.0 + 2.0 for >1000 psi

        # Verify pipeline-specific adjustments
        adjustments = pct_method['adjustments']
        self.assertEqual(adjustments.get('leak_detection_systems'), -0.5)  # Modern SCADA

        # Verify pipeline-specific weights
        self.assertEqual(result['reconciliation']['weights']['percentage_of_fee'], 0.45)
        self.assertEqual(result['reconciliation']['weights']['income_capitalization'], 0.30)

    def test_crude_oil_high_risk_complete(self):
        """Test complete crude oil transmission with environmental concerns."""
        calc = PipelineEasementCalculator({
            'property': {
                'address': '300 acres agricultural near river',
                'total_acres': 300,
                'fee_simple_value': 4500000
            },
            'easement': {
                'pipeline_type': 'crude_oil_transmission',
                'area_acres': 8,
                'width_meters': 25,
                'pressure_psi': 1400,
                'diameter_mm': 900,
                'depth_meters': 1.2,
                'has_leak_detection': True,
                'has_cathodic_protection': True,
                'distance_to_water_m': 75,  # Close to watercourse
                'requires_access_road': True,
                'pipeline_age_years': 25,
                'class_location': 2,
                'restrictions': ['excavation_prohibited', 'no_buildings'],
                'hbu_impact': 'moderate',
                'productivity_loss_pct': 0.20
            },
            'market_parameters': {
                'cap_rate': 0.05,
                'annual_rent_per_acre': 500
            }
        })

        result = calc.calculate_all_methods()

        # Verify crude oil base with pressure adjustment
        pct_method = result['valuation_methods']['percentage_of_fee']
        self.assertEqual(pct_method['base_percentage'], 20.0)  # 18.0 + 2.0 for >1000 psi

        # Verify environmental risk adjustments
        adjustments = pct_method['adjustments']
        self.assertEqual(adjustments['water_proximity_risk'], 2.0)  # Crude oil <100m to water
        self.assertEqual(adjustments['access_road'], 1.0)
        self.assertEqual(adjustments.get('leak_detection_systems'), -0.5)  # Risk mitigation

    def test_water_transmission_municipal_complete(self):
        """Test complete water transmission easement valuation."""
        calc = PipelineEasementCalculator({
            'property': {
                'address': '100 acres residential/agricultural',
                'total_acres': 100,
                'fee_simple_value': 2000000
            },
            'easement': {
                'pipeline_type': 'water_transmission',
                'area_acres': 3,
                'width_meters': 15,
                'diameter_mm': 750,
                'depth_meters': 2.5,
                'has_leak_detection': False,  # Water - less critical
                'has_cathodic_protection': True,
                'installation_method': 'hdd',
                'restrictions': ['excavation_prohibited'],
                'hbu_impact': 'minor',
                'productivity_loss_pct': 0.10
            },
            'market_parameters': {
                'cap_rate': 0.05,
                'annual_rent_per_acre': 800
            }
        })

        result = calc.calculate_all_methods()

        # Verify water transmission base
        pct_method = result['valuation_methods']['percentage_of_fee']
        self.assertEqual(pct_method['base_percentage'], 11.0)

        # Verify HDD installation mitigation
        adjustments = pct_method['adjustments']
        self.assertEqual(adjustments.get('hdd_installation'), -0.5)


class TestPipelineTCE(unittest.TestCase):
    """Test pipeline TCE scenarios."""

    def test_pipeline_tce_construction(self):
        """Test 180-day TCE for pipeline construction."""
        calc = PipelineEasementCalculator({
            'property': {
                'address': '150 acres agricultural',
                'total_acres': 150,
                'fee_simple_value': 2250000
            },
            'easement': {
                'pipeline_type': 'natural_gas_transmission',
                'area_acres': 4,
                'term': 'tce',
                'duration_days': 180,
                'restoration_costs': 30000,
                'business_losses': 25000
            },
            'market_parameters': {
                'cap_rate': 0.05,
                'tce_annual_rate': 0.10
            }
        })

        result = calc.calculate_all_methods()

        # Verify TCE classification
        self.assertEqual(result['easement_classification'], 'Temporary Construction Easement (TCE)')

        # Verify TCE calculation
        tce_method = result['valuation_method']
        self.assertEqual(tce_method['duration_days'], 180)
        self.assertEqual(tce_method['annual_rate'], 0.10)

        # Calculate expected rental: $60,000 (4 acres × $15,000/acre) × 10% × (180÷365) = $2,959
        expected_rental = (2250000 / 150) * 4 * 0.10 * (180 / 365)
        self.assertAlmostEqual(tce_method['rental_value'], expected_rental, places=0)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
