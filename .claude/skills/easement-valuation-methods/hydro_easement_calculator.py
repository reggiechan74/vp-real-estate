#!/usr/bin/env python3
"""
Hydro/Utility Transmission Easement Calculator - MARKET-ALIGNED v2.1

Specialized calculator for overhead transmission line easements (69kV - 500kV).

VERSION 2.1 (2025-11-17): Updated to MARKET-ALIGNED values based on IRWA standards
(25-50% permanent easement range) and documented market evidence.

Domain-specific features (MARKET-ALIGNED):
- Voltage-based percentage ranges (69kV: 28%, 500kV: 37.5%)
- EMF concern adjustments: +4% (230kV), +5% (500kV) - research-backed
- Tower placement: +1% per tower (max +5%) - permanent impact
- Vegetation management: +2.5% - ongoing restrictions
- Access road: +2% - permanent land take
- Building proximity: +4% - marketability impact

Voltage tiers (MARKET-ALIGNED):
- 500kV+:  35-40% (37.5% base) - ultra-high voltage, maximum EMF concerns
- 230kV:   32-38% (35.0% base) - high voltage, significant EMF
- 115kV:   28-36% (32.0% base) - moderate voltage
- 69kV:    25-31% (28.0% base) - standard distribution voltage
- <69kV:   25-28% (25.0% base) - minimum market range

Research basis: IRWA 25-50% range, EMF perception studies (+3-5%), market evidence

Supports: easement-valuation-methods skill
Used by: Alexi (Expropriation Appraisal Expert), Shadi (Utility Corridor Agent)

Author: Claude Code
Created: 2025-11-17
Updated: 2025-11-17 (v2.1 - market-aligned)
Version: 2.1.0
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict

# Import base class
from easement_calculator_base import EasementCalculatorBase


class HydroEasementCalculator(EasementCalculatorBase):
    """
    Hydro/utility transmission easement valuation calculator.

    Implements voltage-based percentage methodology and hydro-specific adjustments.
    """

    def get_base_percentage(self) -> float:
        """
        Get base percentage for transmission line by voltage.

        Voltage-based ranges reflect:
        - Corridor width requirements
        - Construction and maintenance impact
        - Safety setbacks and clearances
        - Property use limitations
        - Market data from utility corridor transactions

        Returns:
            float: Base percentage (e.g., 17.5 for 17.5%)

        Raises:
            ValueError: If voltage_kv parameter is missing
        """
        voltage = self.easement_data.get('voltage_kv')

        if voltage is None:
            raise ValueError(
                "Hydro easement calculator requires 'voltage_kv' parameter. "
                "Specify transmission line voltage (e.g., 69, 115, 230, 500)"
            )

        # Voltage-based percentage tiers (MARKET-ALIGNED: 25-50% range per IRWA)
        if voltage >= 500:
            return 37.5  # 35-40% for 500kV (very wide corridor: 100-120m, highest EMF concerns)
        elif voltage >= 230:
            return 35.0  # 32-38% for 230kV (wide corridor: 60-80m, significant EMF)
        elif voltage >= 115:
            return 32.0  # 28-36% for 115kV (moderate corridor: 40-50m)
        elif voltage >= 69:
            return 28.0  # 25-31% for 69kV (standard corridor: 20-30m)
        else:
            return 25.0  # 25-28% for lower voltage (<69kV) - minimum market range

    def get_domain_specific_adjustments(self) -> Dict[str, float]:
        """
        Get hydro-specific percentage adjustments.

        Hydro-specific factors:
        1. EMF concerns (high voltage health perception)
        2. Tower placement impacts (foundation size, land fragmentation)
        3. Vegetation management (tree clearing, ongoing maintenance)
        4. Access road requirements (construction and maintenance access)

        Returns:
            Dict[str, float]: {adjustment_name: percentage_value}
        """
        adjustments = {}

        # EMF concerns (high voltage lines) - MARKET-ALIGNED
        voltage = self.easement_data.get('voltage_kv', 0)
        if voltage >= 500:
            # Ultra-high voltage (500kV+): Field magnitudes >10kV/m documented
            # Public perception of health risks significantly affects marketability
            adjustments['emf_concern'] = 5.0  # +5% for 500kV+ EMF perception (per research)
        elif voltage >= 230:
            # High voltage lines (230kV+): Documented EMF concerns
            # Research supports +3% to +5% range for public perception impacts
            adjustments['emf_concern'] = 4.0  # +4% for 230kV EMF perception

        # Tower placement impacts - MARKET-ALIGNED
        tower_count = self.easement_data.get('tower_count', 0)
        if tower_count > 0:
            # Each tower:
            # - Requires large foundation (10-20m diameter)
            # - Fragments land (reduces parcel efficiency)
            # - Permanent structure (prevents development)
            # Market evidence: Towers create permanent visual and functional impact
            adjustments['tower_placement'] = min(tower_count * 1.0, 5.0)  # +1% per tower (max +5%)

        # Vegetation management restrictions - MARKET-ALIGNED
        if 'vegetation_restrictions' in self.easement_data:
            restrictions = self.easement_data['vegetation_restrictions']
            if isinstance(restrictions, list) and len(restrictions) > 0:
                # Ongoing tree clearing and height restrictions
                # Affects property aesthetics, agricultural use, and development
                adjustments['vegetation_management'] = 2.5  # +2.5% for vegetation restrictions

        # Access road requirements - MARKET-ALIGNED
        if self.easement_data.get('requires_access_road', False):
            # Permanent access road for construction and maintenance
            # Additional land take, fragmentation, and ongoing disruption
            adjustments['access_road'] = 2.0  # +2% for access road requirement

        # Proximity to buildings/residential use - MARKET-ALIGNED
        distance_to_buildings = self.easement_data.get('distance_to_buildings_m', 999)
        if distance_to_buildings < 50 and voltage >= 230:
            # High voltage line very close to buildings (<50m)
            # Significant marketability impact, buyer resistance, perception issues
            adjustments['proximity_impact'] = 4.0  # +4% for close proximity to buildings

        return adjustments

    def _get_dynamic_weights(self) -> Dict[str, float]:
        """
        Hydro-specific reconciliation weights.

        Transmission easements favor percentage of fee method because:
        - Extensive market data available by voltage tier
        - Industry-standard percentage ranges well-established
        - Voltage is a strong predictor of easement value

        Returns:
            Dict with weights and reasoning
        """
        # Allow user override
        user_weights = self.market_data.get('reconciliation_weights')
        if user_weights:
            return user_weights

        # Hydro transmission: Percentage of fee dominant
        return {
            'percentage_of_fee': 0.50,       # Strongest (extensive market data by voltage)
            'income_capitalization': 0.30,   # Supportive (productivity loss quantifiable)
            'before_after': 0.20,            # Confirmatory (property-specific impacts)
            'reasoning': 'Hydro Transmission: Percentage of fee strongest (extensive market data by voltage tier, industry-standard ranges)'
        }


def main():
    """Main execution function for hydro easement calculator."""
    parser = argparse.ArgumentParser(
        description='Calculate hydro/utility transmission easement value (69kV-500kV)'
    )
    parser.add_argument('input_file', help='Path to input JSON file with voltage_kv parameter')
    parser.add_argument('--output', '-o', help='Path to output JSON file (optional)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Print detailed output')

    args = parser.parse_args()

    # Load input
    with open(args.input_file, 'r') as f:
        input_data = json.load(f)

    # Validate hydro-specific parameters
    if 'voltage_kv' not in input_data.get('easement', {}):
        print("ERROR: Hydro easement calculator requires 'voltage_kv' parameter")
        print("\nExpected input format:")
        print("""
{
  "property": {...},
  "easement": {
    "type": "utility_transmission",
    "voltage_kv": 230,
    "area_acres": 5,
    "tower_count": 2,
    ...
  },
  "market_parameters": {...}
}
        """)
        sys.exit(1)

    # Calculate
    calculator = HydroEasementCalculator(input_data)
    results = calculator.calculate_all_methods()

    # Output
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results written to {args.output}")

    if args.verbose or not args.output:
        print(json.dumps(results, indent=2))

    # Print summary
    voltage = input_data['easement'].get('voltage_kv', 0)
    print(f"\n{'='*80}")
    print(f"HYDRO TRANSMISSION EASEMENT VALUATION (v2.0)")
    print(f"{'='*80}")
    print(f"Property: {input_data['property'].get('address', 'N/A')}")
    print(f"Voltage: {voltage}kV")
    print(f"Classification: {results['easement_classification']}")
    print(f"Area: {input_data['easement']['area_acres']:.2f} acres")

    if results['easement_classification'] == 'Temporary Construction Easement (TCE)':
        tce = results['valuation_method']
        print(f"\nTCE Rate-of-Return Method:")
        print(f"  Duration:              {tce['duration_days']} days ({tce['duration_category']})")
        print(f"  Annual Rate:           {tce['annual_rate']:.1%}")
        print(f"  Rental Value:          ${tce['rental_value']:>12,.0f}")
        print(f"  Restoration Costs:     ${tce['restoration_costs']:>12,.0f}")
        print(f"  Business Losses:       ${tce['business_losses']:>12,.0f}")
        print(f"\nTotal TCE Value:         ${tce['total_tce_value']:>12,.0f}")
    else:
        methods = results['valuation_methods']
        print(f"\nValuation Methods:")
        print(f"  Percentage of Fee:      ${methods['percentage_of_fee']['easement_value']:>12,.0f}")
        print(f"    - Base: {methods['percentage_of_fee']['base_percentage']:.1f}%")
        print(f"    - Final: {methods['percentage_of_fee']['final_percentage']:.1f}%")
        print(f"  Income Capitalization:  ${methods['income_capitalization']['easement_value']:>12,.0f}")
        print(f"  Before/After:           ${methods['before_after']['easement_value']:>12,.0f}")

        recon = results['reconciliation']
        print(f"\nReconciliation:")
        print(f"  Weights: {recon['weights']['percentage_of_fee']:.0%} / {recon['weights']['income_capitalization']:.0%} / {recon['weights']['before_after']:.0%}")
        print(f"  Reasoning: {recon['weighting_reasoning']}")
        print(f"\nReconciled Value:        ${recon['reconciled_value']:>12,.0f}")
        print(f"Value Range:             ${recon['value_range']['low']:>12,.0f} - ${recon['value_range']['high']:>12,.0f}")

    print(f"{'='*80}\n")


if __name__ == '__main__':
    main()
