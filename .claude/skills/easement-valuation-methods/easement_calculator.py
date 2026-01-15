#!/usr/bin/env python3
"""
Easement Valuation Calculator

Calculates easement value using three methodologies:
1. Percentage of Fee Method (5-35% based on easement characteristics)
2. Income Capitalization Method (rental basis)
3. Before/After Comparison Method

Supports: easement-valuation-methods skill
Used by: Alexi (Expropriation Appraisal Expert), Shadi (Utility Corridor Agent)

Author: Claude Code
Created: 2025-11-15
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Literal
from datetime import datetime

# Add Shared_Utils to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "Shared_Utils"))
from financial_utils import pv_annuity, npv, annual_to_monthly_rate


class EasementCalculator:
    """Calculate easement value using multiple methodologies."""

    def __init__(self, input_data: Dict):
        """Initialize calculator with input data."""
        self.data = input_data
        self.property_data = input_data['property']
        self.easement_data = input_data['easement']
        self.market_data = input_data['market_parameters']
        self.results = {}

    def calculate_percentage_of_fee(self) -> Dict:
        """
        Calculate easement value as percentage of fee simple value.

        Percentage ranges based on easement characteristics:
        - Utility type and voltage
        - Width and restrictions
        - Term (permanent vs temporary)
        - Impact on highest and best use
        """
        fee_simple_value = self.property_data['fee_simple_value']
        easement_area_acres = self.easement_data['area_acres']

        # Base percentage by easement type
        easement_type = self.easement_data['type']
        voltage = self.easement_data.get('voltage_kv', 0)

        base_percentages = {
            'utility_transmission': self._get_transmission_percentage(voltage),
            'pipeline': self._get_pipeline_percentage(),
            'telecom': self._get_telecom_percentage(),
            'transit': self._get_transit_percentage(),
            'access': self._get_access_percentage()
        }

        base_pct = base_percentages.get(easement_type, 15.0)

        # Adjustments
        width_adjustment = self._calculate_width_adjustment()
        restriction_adjustment = self._calculate_restriction_adjustment()
        term_adjustment = self._calculate_term_adjustment()
        hbu_adjustment = self._calculate_hbu_impact_adjustment()

        # Final percentage
        final_percentage = base_pct + width_adjustment + restriction_adjustment + term_adjustment + hbu_adjustment

        # Clamp to reasonable range (5-35%)
        final_percentage = max(5.0, min(35.0, final_percentage))

        # Calculate value
        value_per_acre = fee_simple_value / self.property_data['total_acres']
        easement_value = value_per_acre * easement_area_acres * (final_percentage / 100)

        return {
            'method': 'Percentage of Fee',
            'base_percentage': base_pct,
            'adjustments': {
                'width': width_adjustment,
                'restrictions': restriction_adjustment,
                'term': term_adjustment,
                'highest_and_best_use': hbu_adjustment
            },
            'final_percentage': final_percentage,
            'fee_simple_value_per_acre': value_per_acre,
            'easement_area_acres': easement_area_acres,
            'easement_value': easement_value
        }

    def _get_transmission_percentage(self, voltage: int) -> float:
        """Get base percentage for transmission line by voltage."""
        if voltage >= 500:
            return 22.5  # 20-25% for 500kV
        elif voltage >= 230:
            return 17.5  # 15-20% for 230kV
        elif voltage >= 115:
            return 15.0  # 12-18% for 115kV
        elif voltage >= 69:
            return 12.5  # 10-15% for 69kV
        else:
            return 10.0  # Lower voltage

    def _get_pipeline_percentage(self) -> float:
        """Get base percentage for pipeline easements."""
        pipe_type = self.easement_data.get('pipeline_type', 'natural_gas')

        percentages = {
            'crude_oil': 18.0,      # 15-20%
            'natural_gas': 15.0,    # 12-18%
            'water': 12.0,          # 10-15%
            'sewer': 10.0           # 8-12%
        }
        return percentages.get(pipe_type, 15.0)

    def _get_telecom_percentage(self) -> float:
        """Get base percentage for telecom easements."""
        return 8.0  # 5-10% typical for fiber optic/telecom

    def _get_transit_percentage(self) -> float:
        """Get base percentage for transit corridors."""
        transit_type = self.easement_data.get('transit_type', 'rail')

        percentages = {
            'heavy_rail': 25.0,     # 20-30%
            'light_rail': 20.0,     # 18-25%
            'bus_rapid_transit': 15.0  # 12-18%
        }
        return percentages.get(transit_type, 20.0)

    def _get_access_percentage(self) -> float:
        """Get base percentage for access easements."""
        return 12.0  # 10-15% for access easements

    def _calculate_width_adjustment(self) -> float:
        """Calculate adjustment based on easement width."""
        width_m = self.easement_data.get('width_meters', 0)

        # Wider easements have greater impact
        if width_m >= 100:
            return 3.0  # Very wide (500kV corridors)
        elif width_m >= 60:
            return 2.0  # Wide (230kV corridors)
        elif width_m >= 40:
            return 1.0  # Moderate (115kV corridors)
        elif width_m >= 20:
            return 0.0  # Standard (69kV corridors)
        else:
            return -1.0  # Narrow (telecom, utilities)

    def _calculate_restriction_adjustment(self) -> float:
        """Calculate adjustment based on use restrictions."""
        restrictions = self.easement_data.get('restrictions', [])

        adjustment = 0.0

        restriction_impacts = {
            'no_buildings': 2.0,
            'no_trees': 1.5,
            'height_restrictions': 1.0,
            'access_limitations': 1.5,
            'excavation_prohibited': 1.0
        }

        for restriction in restrictions:
            adjustment += restriction_impacts.get(restriction, 0.0)

        return min(adjustment, 5.0)  # Cap at +5%

    def _calculate_term_adjustment(self) -> float:
        """Calculate adjustment based on easement term."""
        term = self.easement_data.get('term', 'perpetual')

        if term == 'perpetual':
            return 0.0  # No adjustment
        elif term == 'temporary':
            years = self.easement_data.get('term_years', 10)
            if years <= 5:
                return -8.0  # Very temporary
            elif years <= 10:
                return -5.0  # Short term
            elif years <= 25:
                return -3.0  # Medium term
            else:
                return -1.0  # Long term (approaching perpetual)
        return 0.0

    def _calculate_hbu_impact_adjustment(self) -> float:
        """Calculate adjustment based on impact to highest and best use."""
        hbu_impact = self.easement_data.get('hbu_impact', 'moderate')

        impacts = {
            'none': -2.0,          # Minimal impact to HBU
            'minor': 0.0,          # Some impact but HBU still achievable
            'moderate': 2.0,       # Moderate impact to HBU
            'major': 5.0,          # Significant impact to HBU
            'precludes_development': 8.0  # Prevents development entirely
        }

        return impacts.get(hbu_impact, 2.0)

    def calculate_income_capitalization(self) -> Dict:
        """
        Calculate easement value using income capitalization method.

        Based on rental equivalent approach - what would annual rent be
        for this easement, capitalized to present value.
        """
        easement_area_acres = self.easement_data['area_acres']

        # Annual rent per acre (market-based)
        annual_rent_per_acre = self.market_data.get('annual_rent_per_acre')

        if annual_rent_per_acre is None:
            # Estimate from comparable land rents if not provided
            annual_rent_per_acre = self._estimate_rental_rate()

        annual_rent = annual_rent_per_acre * easement_area_acres

        # Capitalization rate
        cap_rate = self.market_data['cap_rate']

        # Easement adjustment factor (easement rent typically 30-50% of full land rent)
        easement_factor = self.easement_data.get('easement_rent_factor', 0.40)

        adjusted_annual_rent = annual_rent * easement_factor

        # Capitalize to value
        easement_value = adjusted_annual_rent / cap_rate

        return {
            'method': 'Income Capitalization',
            'annual_rent_per_acre': annual_rent_per_acre,
            'easement_area_acres': easement_area_acres,
            'annual_rent_gross': annual_rent,
            'easement_rent_factor': easement_factor,
            'adjusted_annual_rent': adjusted_annual_rent,
            'cap_rate': cap_rate,
            'easement_value': easement_value
        }

    def _estimate_rental_rate(self) -> float:
        """Estimate annual rent per acre based on land value and cap rate."""
        fee_simple_value = self.property_data['fee_simple_value']
        total_acres = self.property_data['total_acres']
        cap_rate = self.market_data['cap_rate']

        value_per_acre = fee_simple_value / total_acres
        estimated_rent_per_acre = value_per_acre * cap_rate

        return estimated_rent_per_acre

    def calculate_before_after(self) -> Dict:
        """
        Calculate easement value using before/after comparison method.

        Property value before easement - Property value after easement = Easement value
        """
        # Value before (from input)
        value_before = self.property_data['fee_simple_value']

        # Value after (requires analysis of impact)
        # This can come from input or be calculated
        value_after_input = self.property_data.get('value_after_easement')

        if value_after_input is not None:
            value_after = value_after_input
        else:
            # Estimate value after based on percentage of fee method
            pct_method = self.calculate_percentage_of_fee()
            value_after = value_before - pct_method['easement_value']

        easement_value = value_before - value_after

        # As percentage
        percentage_loss = (easement_value / value_before) * 100

        return {
            'method': 'Before/After Comparison',
            'value_before': value_before,
            'value_after': value_after,
            'easement_value': easement_value,
            'percentage_loss': percentage_loss
        }

    def calculate_all_methods(self) -> Dict:
        """Calculate easement value using all three methods."""
        pct_method = self.calculate_percentage_of_fee()
        income_method = self.calculate_income_capitalization()
        before_after_method = self.calculate_before_after()

        # Reconciliation - typically weight percentage of fee most heavily
        weights = {
            'percentage_of_fee': 0.50,
            'income_capitalization': 0.30,
            'before_after': 0.20
        }

        reconciled_value = (
            pct_method['easement_value'] * weights['percentage_of_fee'] +
            income_method['easement_value'] * weights['income_capitalization'] +
            before_after_method['easement_value'] * weights['before_after']
        )

        return {
            'property': self.property_data,
            'easement': self.easement_data,
            'market_parameters': self.market_data,
            'valuation_methods': {
                'percentage_of_fee': pct_method,
                'income_capitalization': income_method,
                'before_after': before_after_method
            },
            'reconciliation': {
                'weights': weights,
                'reconciled_value': reconciled_value,
                'value_range': {
                    'low': min(pct_method['easement_value'],
                              income_method['easement_value'],
                              before_after_method['easement_value']),
                    'high': max(pct_method['easement_value'],
                               income_method['easement_value'],
                               before_after_method['easement_value'])
                }
            },
            'calculation_date': datetime.now().isoformat(),
            'calculator_version': '1.0.0'
        }


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Calculate easement value using percentage of fee, income capitalization, and before/after methods'
    )
    parser.add_argument('input_file', help='Path to input JSON file')
    parser.add_argument('--output', '-o', help='Path to output JSON file (optional)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Print detailed output')

    args = parser.parse_args()

    # Load input
    with open(args.input_file, 'r') as f:
        input_data = json.load(f)

    # Calculate
    calculator = EasementCalculator(input_data)
    results = calculator.calculate_all_methods()

    # Output
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results written to {args.output}")

    if args.verbose or not args.output:
        print(json.dumps(results, indent=2))

    # Print summary
    print(f"\n{'='*80}")
    print(f"EASEMENT VALUATION SUMMARY")
    print(f"{'='*80}")
    print(f"Property: {input_data['property'].get('address', 'N/A')}")
    print(f"Easement Type: {input_data['easement']['type']}")
    print(f"Area: {input_data['easement']['area_acres']:.2f} acres")
    print(f"\nMethods:")
    print(f"  Percentage of Fee:      ${results['valuation_methods']['percentage_of_fee']['easement_value']:>12,.0f}")
    print(f"  Income Capitalization:  ${results['valuation_methods']['income_capitalization']['easement_value']:>12,.0f}")
    print(f"  Before/After:           ${results['valuation_methods']['before_after']['easement_value']:>12,.0f}")
    print(f"\nReconciled Value:        ${results['reconciliation']['reconciled_value']:>12,.0f}")
    print(f"Value Range:             ${results['reconciliation']['value_range']['low']:>12,.0f} - ${results['reconciliation']['value_range']['high']:>12,.0f}")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    main()
