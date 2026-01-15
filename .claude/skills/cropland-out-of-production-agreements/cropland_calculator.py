#!/usr/bin/env python3
"""
Cropland Out of Production Calculator

Calculates ongoing annual impacts and compares one-time vs. annual compensation
for transmission lines, pipelines, and infrastructure on agricultural land.

Based on Ontario Federation of Agriculture (OFA) guidance and Alberta Surface Rights Board model.

Impact Categories:
1. Internal headlands loss
2. Aerial spraying restrictions
3. Precision agriculture interference
4. Labor increases
5. Weed control expenses
6. Equipment damage risk
7. Irrigation restrictions (if applicable)

Supports: cropland-out-of-production-agreements skill
Used by: Shadi (Utility Corridor Agent), Alexi (Appraisal Expert)

Author: Claude Code
Created: 2025-11-15
"""

import sys
import json
import argparse
import math
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add Shared_Utils to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "Shared_Utils"))
from financial_utils import pv_annuity, npv


class CroplandCalculator:
    """Calculate cropland out of production compensation."""

    # Alberta 2021 rates (Hart v ATCO Electric Ltd)
    ALBERTA_RATES_2021 = {
        'cultivated': 1380.0,      # $/tower/year
        'uncultivated': 552.0,     # $/tower/year
        'headlands': 690.0         # $/tower/year
    }

    def __init__(self, input_data: Dict):
        """Initialize calculator with input data."""
        self.data = input_data
        self.farm = input_data['farm_details']
        self.infrastructure = input_data['infrastructure']
        self.compensation_offer = input_data['compensation_offer']
        self.impacts = input_data['ongoing_impacts']
        self.financial = input_data['financial_parameters']

    def calculate_headlands_loss(self) -> Dict:
        """
        Calculate annual loss from internal headlands around towers.

        Headlands = turning space required around each tower where farming
        continues but productivity is reduced 30-50%.
        """
        tower_count = self.infrastructure['tower_count']
        headland_radius_m = self.impacts['headland_radius_m']
        productivity_loss_pct = self.impacts['headland_productivity_loss_pct']
        net_income_per_acre = self.farm['net_income_per_acre']

        # Calculate headland area per tower (circle)
        headland_area_m2_per_tower = math.pi * (headland_radius_m ** 2)
        total_headland_area_m2 = headland_area_m2_per_tower * tower_count

        # Convert to acres (1 acre = 4046.86 m²)
        total_headland_area_acres = total_headland_area_m2 / 4046.86

        # Annual loss
        annual_loss = (total_headland_area_acres *
                      (productivity_loss_pct / 100) *
                      net_income_per_acre)

        return {
            'category': 'Internal Headlands Loss',
            'tower_count': tower_count,
            'headland_radius_m': headland_radius_m,
            'headland_area_per_tower_m2': headland_area_m2_per_tower,
            'total_headland_area_acres': total_headland_area_acres,
            'productivity_loss_pct': productivity_loss_pct,
            'net_income_per_acre': net_income_per_acre,
            'annual_loss': annual_loss
        }

    def calculate_aerial_spray_restrictions(self) -> Dict:
        """
        Calculate annual cost from aerial spraying restrictions.

        Aerial spraying prohibited within 15-30m of conductors.
        Must ground-spray ROW area instead (10× cost, 3× time).
        """
        if not self.impacts.get('aerial_spray_restriction', False):
            return {
                'category': 'Aerial Spraying Restrictions',
                'applicable': False,
                'annual_cost': 0.0
            }

        row_width_m = self.infrastructure['row_width_m']
        crossing_length_km = self.infrastructure['crossing_length_km']

        # ROW area requiring ground spray
        row_area_m2 = row_width_m * (crossing_length_km * 1000)
        row_area_hectares = row_area_m2 / 10000

        # Cost differential
        ground_spray_cost = self.impacts['ground_spray_cost_per_ha']
        aerial_spray_cost = self.impacts['aerial_spray_cost_per_ha']
        cost_differential = ground_spray_cost - aerial_spray_cost

        annual_cost = row_area_hectares * cost_differential

        return {
            'category': 'Aerial Spraying Restrictions',
            'applicable': True,
            'row_width_m': row_width_m,
            'crossing_length_km': crossing_length_km,
            'row_area_hectares': row_area_hectares,
            'ground_spray_cost_per_ha': ground_spray_cost,
            'aerial_spray_cost_per_ha': aerial_spray_cost,
            'cost_differential_per_ha': cost_differential,
            'annual_cost': annual_cost
        }

    def calculate_precision_ag_interference(self) -> Dict:
        """
        Calculate annual cost from GPS interference and overlapping inputs.

        High-voltage conductors cause GPS signal distortion.
        Auto-steer malfunction = manual steering = 5-10% input overlap.
        """
        if not self.impacts.get('precision_ag_interference', False):
            return {
                'category': 'Precision Agriculture Interference',
                'applicable': False,
                'annual_cost': 0.0
            }

        gps_interference_width_m = self.impacts['gps_interference_width_m']
        crossing_length_km = self.infrastructure['crossing_length_km']

        # Interference zone area
        interference_area_m2 = gps_interference_width_m * (crossing_length_km * 1000)
        interference_area_hectares = interference_area_m2 / 10000

        # Overlapping inputs
        overlap_pct = self.impacts['overlap_pct']
        input_costs_per_ha = self.impacts['input_costs_per_ha']

        annual_cost = interference_area_hectares * input_costs_per_ha * (overlap_pct / 100)

        return {
            'category': 'Precision Agriculture Interference',
            'applicable': True,
            'gps_interference_width_m': gps_interference_width_m,
            'crossing_length_km': crossing_length_km,
            'interference_area_hectares': interference_area_hectares,
            'overlap_pct': overlap_pct,
            'input_costs_per_ha': input_costs_per_ha,
            'annual_cost': annual_cost
        }

    def calculate_labor_increases(self) -> Dict:
        """
        Calculate annual labor cost increases from farming around towers.

        Planting/harvest 10-15% slower, spraying 20-30% slower, tillage 5-10% slower.
        """
        labor_increase_pct = self.impacts['labor_increase_pct']
        hourly_labor_cost = self.impacts['hourly_labor_cost']
        total_acres = self.farm['total_acres']

        # Estimate annual farm labor hours (rough: 8-12 hours/acre/year for cash crops)
        hours_per_acre_per_year = 10  # Conservative estimate
        baseline_annual_hours = total_acres * hours_per_acre_per_year

        # Additional hours from towers
        additional_hours = baseline_annual_hours * (labor_increase_pct / 100)

        annual_cost = additional_hours * hourly_labor_cost

        return {
            'category': 'Labor Increases',
            'total_acres': total_acres,
            'estimated_baseline_hours_per_year': baseline_annual_hours,
            'labor_increase_pct': labor_increase_pct,
            'additional_hours_per_year': additional_hours,
            'hourly_labor_cost': hourly_labor_cost,
            'annual_cost': annual_cost
        }

    def calculate_weed_control(self) -> Dict:
        """
        Calculate annual weed control expenses at tower footprints.

        Cannot spray within 2-3m of tower legs. Manual control required.
        """
        tower_count = self.infrastructure['tower_count']
        weed_control_per_tower = self.impacts['weed_control_per_tower']

        annual_cost = tower_count * weed_control_per_tower

        return {
            'category': 'Weed Control Expenses',
            'tower_count': tower_count,
            'cost_per_tower': weed_control_per_tower,
            'annual_cost': annual_cost
        }

    def calculate_equipment_damage_risk(self) -> Dict:
        """
        Calculate expected annual cost from equipment damage risk.

        Guy wires, anchor points create collision hazards.
        Expected value = towers × probability × average damage.
        """
        tower_count = self.infrastructure['tower_count']
        damage_probability_pct = self.impacts['equipment_damage_probability_pct']
        average_damage_cost = self.impacts['average_damage_cost']

        expected_annual_cost = (tower_count *
                               (damage_probability_pct / 100) *
                               average_damage_cost)

        return {
            'category': 'Equipment Damage Risk',
            'tower_count': tower_count,
            'annual_collision_probability_pct': damage_probability_pct,
            'average_damage_cost': average_damage_cost,
            'expected_annual_cost': expected_annual_cost
        }

    def calculate_total_annual_impacts(self) -> Dict:
        """Calculate total annual impacts from all categories."""
        headlands = self.calculate_headlands_loss()
        aerial_spray = self.calculate_aerial_spray_restrictions()
        precision_ag = self.calculate_precision_ag_interference()
        labor = self.calculate_labor_increases()
        weed_control = self.calculate_weed_control()
        equipment_damage = self.calculate_equipment_damage_risk()

        impacts = [headlands, aerial_spray, precision_ag, labor, weed_control, equipment_damage]

        total_annual_cost = sum([
            headlands['annual_loss'],
            aerial_spray['annual_cost'],
            precision_ag['annual_cost'],
            labor['annual_cost'],
            weed_control['annual_cost'],
            equipment_damage['expected_annual_cost']
        ])

        return {
            'breakdown': impacts,
            'total_annual_cost': total_annual_cost
        }

    def calculate_npv_annual_compensation(self, annual_amount: float) -> float:
        """
        Calculate NPV of annual compensation over infrastructure lifespan.

        Uses annuity factor approach: NPV = Annual × Annuity Factor
        """
        lifespan_years = self.infrastructure['lifespan_years']
        discount_rate = self.financial['discount_rate_pct'] / 100

        # Annuity factor: (1 - (1 + r)^-n) / r
        if discount_rate == 0:
            annuity_factor = lifespan_years
        else:
            annuity_factor = (1 - (1 + discount_rate) ** -lifespan_years) / discount_rate

        npv_value = annual_amount * annuity_factor

        return npv_value

    def calculate_ontario_model(self) -> Dict:
        """Calculate compensation under Ontario Hydro One current practice."""
        one_time_easement = self.compensation_offer['one_time_easement']
        theoretical_profit_6yr = self.compensation_offer['theoretical_profit_6yr']
        total_one_time = self.compensation_offer['total_one_time']

        return {
            'model': 'Ontario Hydro One (Current Practice)',
            'one_time_easement_payment': one_time_easement,
            'theoretical_profit_loss_6yr': theoretical_profit_6yr,
            'total_compensation': total_one_time,
            'annual_ongoing_compensation': 0.0,
            'npv_total_compensation': total_one_time
        }

    def calculate_alberta_model(self) -> Dict:
        """
        Calculate compensation under Alberta Surface Rights Board model.

        Annual per-structure payments based on tower classification.
        """
        tower_classification = self.infrastructure['tower_classification']

        cultivated_count = tower_classification.get('cultivated', 0)
        uncultivated_count = tower_classification.get('uncultivated', 0)
        headlands_count = tower_classification.get('headlands', 0)

        annual_compensation = (
            cultivated_count * self.ALBERTA_RATES_2021['cultivated'] +
            uncultivated_count * self.ALBERTA_RATES_2021['uncultivated'] +
            headlands_count * self.ALBERTA_RATES_2021['headlands']
        )

        # NPV of annual payments
        npv_annual = self.calculate_npv_annual_compensation(annual_compensation)

        # One-time payments (typical Alberta additional payments)
        one_time_easement = self.compensation_offer.get('one_time_easement', 0)

        total_npv = one_time_easement + npv_annual

        return {
            'model': 'Alberta Surface Rights Board (2021 Rates)',
            'tower_classification': tower_classification,
            'rates_per_tower_per_year': self.ALBERTA_RATES_2021,
            'annual_compensation': annual_compensation,
            'one_time_easement_payment': one_time_easement,
            'lifespan_years': self.infrastructure['lifespan_years'],
            'discount_rate_pct': self.financial['discount_rate_pct'],
            'npv_annual_compensation': npv_annual,
            'npv_total_compensation': total_npv
        }

    def calculate_farmer_required_model(self) -> Dict:
        """
        Calculate compensation required to cover actual ongoing impacts.

        Based on calculated annual costs, what annual compensation is needed?
        """
        annual_impacts = self.calculate_total_annual_impacts()
        total_annual_cost = annual_impacts['total_annual_cost']

        # NPV of required annual compensation
        npv_annual_required = self.calculate_npv_annual_compensation(total_annual_cost)

        # One-time payment from Ontario offer
        one_time_from_offer = self.compensation_offer['one_time_easement']

        # Total required compensation
        total_required_npv = one_time_from_offer + npv_annual_required

        return {
            'model': 'Farmer Required (Based on Actual Impacts)',
            'annual_impacts': annual_impacts,
            'required_annual_compensation': total_annual_cost,
            'one_time_easement_payment': one_time_from_offer,
            'npv_required_annual_compensation': npv_annual_required,
            'npv_total_compensation_required': total_required_npv
        }

    def calculate_comparison(self) -> Dict:
        """Compare all compensation models."""
        ontario = self.calculate_ontario_model()
        alberta = self.calculate_alberta_model()
        farmer_required = self.calculate_farmer_required_model()

        # Calculate shortfalls
        ontario_shortfall = farmer_required['npv_total_compensation_required'] - ontario['npv_total_compensation']
        alberta_vs_ontario = alberta['npv_total_compensation'] - ontario['npv_total_compensation']
        farmer_vs_alberta = farmer_required['npv_total_compensation_required'] - alberta['npv_total_compensation']

        return {
            'farm': self.farm,
            'infrastructure': self.infrastructure,
            'financial_parameters': self.financial,
            'compensation_models': {
                'ontario_current': ontario,
                'alberta_surface_rights': alberta,
                'farmer_required': farmer_required
            },
            'comparison': {
                'ontario_vs_required_shortfall': ontario_shortfall,
                'ontario_vs_required_shortfall_pct': (ontario_shortfall / farmer_required['npv_total_compensation_required']) * 100,
                'alberta_vs_ontario_difference': alberta_vs_ontario,
                'alberta_vs_ontario_multiplier': alberta['npv_total_compensation'] / ontario['npv_total_compensation'] if ontario['npv_total_compensation'] > 0 else 0,
                'farmer_required_vs_alberta_shortfall': farmer_vs_alberta,
                'farmer_required_vs_alberta_shortfall_pct': (farmer_vs_alberta / farmer_required['npv_total_compensation_required']) * 100 if farmer_vs_alberta > 0 else 0
            },
            'sensitivity_analysis': self.calculate_sensitivity(),
            'calculation_date': datetime.now().isoformat(),
            'calculator_version': '1.0.0'
        }

    def calculate_sensitivity(self) -> Dict:
        """
        Perform sensitivity analysis on key variables.

        Test impact of ±20% change in:
        - Discount rate
        - Crop prices (net income/acre)
        - Tower count
        """
        baseline = self.calculate_farmer_required_model()
        baseline_annual = baseline['required_annual_compensation']
        baseline_npv = baseline['npv_total_compensation_required']

        # Discount rate sensitivity
        original_rate = self.financial['discount_rate_pct']

        self.financial['discount_rate_pct'] = original_rate * 0.8  # -20%
        low_rate_npv = self.calculate_farmer_required_model()['npv_total_compensation_required']

        self.financial['discount_rate_pct'] = original_rate * 1.2  # +20%
        high_rate_npv = self.calculate_farmer_required_model()['npv_total_compensation_required']

        self.financial['discount_rate_pct'] = original_rate  # Reset

        # Crop price sensitivity
        original_income = self.farm['net_income_per_acre']

        self.farm['net_income_per_acre'] = original_income * 0.8  # -20%
        low_income_result = self.calculate_farmer_required_model()

        self.farm['net_income_per_acre'] = original_income * 1.2  # +20%
        high_income_result = self.calculate_farmer_required_model()

        self.farm['net_income_per_acre'] = original_income  # Reset

        # Tower count sensitivity
        original_towers = self.infrastructure['tower_count']

        self.infrastructure['tower_count'] = int(original_towers * 0.8)  # -20%
        low_towers_result = self.calculate_farmer_required_model()

        self.infrastructure['tower_count'] = int(original_towers * 1.2)  # +20%
        high_towers_result = self.calculate_farmer_required_model()

        self.infrastructure['tower_count'] = original_towers  # Reset

        return {
            'baseline': {
                'annual_compensation': baseline_annual,
                'npv_total': baseline_npv
            },
            'discount_rate': {
                'variable': 'discount_rate_pct',
                'baseline_value': original_rate,
                'low_scenario': {
                    'value': original_rate * 0.8,
                    'npv_total': low_rate_npv,
                    'change_pct': ((low_rate_npv - baseline_npv) / baseline_npv) * 100
                },
                'high_scenario': {
                    'value': original_rate * 1.2,
                    'npv_total': high_rate_npv,
                    'change_pct': ((high_rate_npv - baseline_npv) / baseline_npv) * 100
                }
            },
            'crop_prices': {
                'variable': 'net_income_per_acre',
                'baseline_value': original_income,
                'low_scenario': {
                    'value': original_income * 0.8,
                    'annual_compensation': low_income_result['required_annual_compensation'],
                    'npv_total': low_income_result['npv_total_compensation_required'],
                    'change_pct': ((low_income_result['npv_total_compensation_required'] - baseline_npv) / baseline_npv) * 100
                },
                'high_scenario': {
                    'value': original_income * 1.2,
                    'annual_compensation': high_income_result['required_annual_compensation'],
                    'npv_total': high_income_result['npv_total_compensation_required'],
                    'change_pct': ((high_income_result['npv_total_compensation_required'] - baseline_npv) / baseline_npv) * 100
                }
            },
            'tower_count': {
                'variable': 'tower_count',
                'baseline_value': original_towers,
                'low_scenario': {
                    'value': int(original_towers * 0.8),
                    'annual_compensation': low_towers_result['required_annual_compensation'],
                    'npv_total': low_towers_result['npv_total_compensation_required'],
                    'change_pct': ((low_towers_result['npv_total_compensation_required'] - baseline_npv) / baseline_npv) * 100
                },
                'high_scenario': {
                    'value': int(original_towers * 1.2),
                    'annual_compensation': high_towers_result['required_annual_compensation'],
                    'npv_total': high_towers_result['npv_total_compensation_required'],
                    'change_pct': ((high_towers_result['npv_total_compensation_required'] - baseline_npv) / baseline_npv) * 100
                }
            }
        }


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Calculate cropland out of production compensation and compare Ontario vs Alberta models'
    )
    parser.add_argument('input_file', help='Path to input JSON file')
    parser.add_argument('--output', '-o', help='Path to output JSON file (optional)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Print detailed output')

    args = parser.parse_args()

    # Load input
    with open(args.input_file, 'r') as f:
        input_data = json.load(f)

    # Calculate
    calculator = CroplandCalculator(input_data)
    results = calculator.calculate_comparison()

    # Output
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results written to {args.output}")

    if args.verbose or not args.output:
        print(json.dumps(results, indent=2))

    # Print summary
    ontario = results['compensation_models']['ontario_current']
    alberta = results['compensation_models']['alberta_surface_rights']
    farmer = results['compensation_models']['farmer_required']
    comparison = results['comparison']

    print(f"\n{'='*80}")
    print(f"CROPLAND OUT OF PRODUCTION COMPENSATION ANALYSIS")
    print(f"{'='*80}")
    print(f"Farm: {results['farm']['total_acres']} acres, {results['farm']['crop_type']}")
    print(f"Infrastructure: {results['infrastructure']['type']}, {results['infrastructure']['voltage']}")
    print(f"Towers: {results['infrastructure']['tower_count']}, Lifespan: {results['infrastructure']['lifespan_years']} years")
    print(f"\nCOMPENSATION MODELS (NPV):")
    print(f"{'─'*80}")
    print(f"Ontario Current Practice:    ${ontario['npv_total_compensation']:>15,.0f}")
    print(f"  One-time payment:          ${ontario['total_compensation']:>15,.0f}")
    print(f"  Annual ongoing:            ${ontario['annual_ongoing_compensation']:>15,.0f}/year")
    print()
    print(f"Alberta Surface Rights:      ${alberta['npv_total_compensation']:>15,.0f}")
    print(f"  One-time payment:          ${alberta['one_time_easement_payment']:>15,.0f}")
    print(f"  Annual ongoing:            ${alberta['annual_compensation']:>15,.0f}/year")
    print(f"  NPV of annual (50yr):      ${alberta['npv_annual_compensation']:>15,.0f}")
    print()
    print(f"Farmer Required (Actual):    ${farmer['npv_total_compensation_required']:>15,.0f}")
    print(f"  One-time payment:          ${farmer['one_time_easement_payment']:>15,.0f}")
    print(f"  Annual required:           ${farmer['required_annual_compensation']:>15,.0f}/year")
    print(f"  NPV of annual (50yr):      ${farmer['npv_required_annual_compensation']:>15,.0f}")
    print(f"\nCOMPARISON:")
    print(f"{'─'*80}")
    print(f"Ontario vs Required:         ${comparison['ontario_vs_required_shortfall']:>15,.0f} shortfall ({comparison['ontario_vs_required_shortfall_pct']:.1f}%)")
    print(f"Alberta vs Ontario:          ${comparison['alberta_vs_ontario_difference']:>15,.0f} higher ({comparison['alberta_vs_ontario_multiplier']:.1f}× multiplier)")
    if comparison['farmer_required_vs_alberta_shortfall'] > 0:
        print(f"Required vs Alberta:         ${comparison['farmer_required_vs_alberta_shortfall']:>15,.0f} shortfall ({comparison['farmer_required_vs_alberta_shortfall_pct']:.1f}%)")
    else:
        print(f"Required vs Alberta:         Alberta model EXCEEDS farmer needs by ${abs(comparison['farmer_required_vs_alberta_shortfall']):>,.0f}")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    main()
