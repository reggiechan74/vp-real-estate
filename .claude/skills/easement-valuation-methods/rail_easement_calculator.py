#!/usr/bin/env python3
"""
Rail/Transit Corridor Easement Calculator - MARKET-ALIGNED v2.1

Specialized calculator for rail and transit corridor easements.

VERSION 2.1 (2025-11-17): Updated to MARKET-ALIGNED values based on rail vibration
research (44% exceed limits), noise impact studies, and subsurface market evidence.

Domain-specific features (MARKET-ALIGNED):
- Rail type-based percentage ranges (heavy rail freight: 40%, light rail: 35%)
- Rail alignment: Elevated (+3%), at-grade (baseline), subway/tunnel (-8%), trench (-3%)
- Train frequency: +3% (20-50/day), +5% (>50/day) - "significantly negative impact" (research)
- Vibration: +5% (<30m heavy rail), +3% (<50m any rail) - "price depreciation" documented
- No noise barriers: +4% - 31% of projects exceed noise limits
- Extended hours: +2.5% - sleep disruption impacts

Rail types (MARKET-ALIGNED):
- Heavy Rail Freight:    38-45% (40% base) - hazmat, vibration, safety, noise
- Heavy Rail Passenger:  35-42% (38% base) - high frequency, constant noise
- Subway (Surface):      35-40% (37% base) - very frequent service, vibration
- Light Rail:            32-38% (35% base) - moderate noise, urban integration
- Bus Rapid Transit:     25-32% (28% base) - lower impact, dedicated corridor

Research basis:
- Rail vibration studies: 44% of 1,604 track sections (9 countries) exceed vibration limits
- Noise research: 31% exceed noise limits, "significantly negative impact on housing values"
- Subsurface evidence: -50% typical for tunnel easements (surface remains usable)

Supports: easement-valuation-methods skill
Used by: Katy (Transit Corridor Specialist)

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


class RailEasementCalculator(EasementCalculatorBase):
    """
    Rail/transit corridor easement valuation calculator.

    Implements rail type-based percentage methodology and rail-specific adjustments.
    """

    def get_base_percentage(self) -> float:
        """
        Get base percentage for rail corridor by rail type.

        Rail type ranges reflect:
        - Noise and vibration impacts
        - Train frequency (daily service levels)
        - Safety setbacks and grade crossing risks
        - Property marketability impacts
        - Market data from rail corridor transactions

        Returns:
            float: Base percentage (e.g., 25.0 for 25%)

        Raises:
            ValueError: If rail_type parameter is missing
        """
        rail_type = self.easement_data.get('rail_type')

        if rail_type is None:
            raise ValueError(
                "Rail easement calculator requires 'rail_type' parameter. "
                "Valid values: 'heavy_rail_freight', 'heavy_rail_passenger', 'light_rail', "
                "'subway_surface', 'bus_rapid_transit'"
            )

        # Rail type-based percentage tiers (MARKET-ALIGNED: 25-50% range per IRWA)
        percentages = {
            'heavy_rail_freight': 40.0,      # 38-45% (high noise, vibration, safety, hazmat concerns)
            'heavy_rail_passenger': 38.0,    # 35-42% (high frequency, better mitigation but constant noise)
            'light_rail': 35.0,              # 32-38% (moderate noise, urban integration, frequent service)
            'subway_surface': 37.0,          # 35-40% (very frequent service, noise/vibration impacts)
            'bus_rapid_transit': 28.0        # 25-32% (lower impact than rail, but dedicated corridor)
        }

        base_pct = percentages.get(rail_type)
        if base_pct is None:
            raise ValueError(
                f"Invalid rail_type '{rail_type}'. Valid values: "
                f"{', '.join(percentages.keys())}"
            )

        return base_pct

    def get_domain_specific_adjustments(self) -> Dict[str, float]:
        """
        Get rail-specific percentage adjustments.

        Rail-specific factors:
        1. Alignment (elevated, at-grade, subway/tunnel, trench)
        2. Train frequency (trains per day)
        3. Noise impact (proximity to noise-sensitive uses)
        4. Vibration (proximity to buildings, soil conditions)
        5. Grade crossings (safety concerns, traffic disruption)
        6. Service hours (24-hour service vs. limited hours)

        Returns:
            Dict[str, float]: {adjustment_name: percentage_value}
        """
        adjustments = {}

        # 1. Rail alignment (surface vs. subsurface) - MARKET-ALIGNED
        alignment = self.easement_data.get('rail_alignment', 'at_grade')

        if alignment == 'elevated':
            # Elevated rail/guideway: Higher impact
            # - Visual obstruction (views blocked by elevated structure)
            # - Shadow casting (reduces sunlight, property desirability)
            # - Noise projection (sound travels further from elevated position)
            # - Structural presence (columns, supports on/near property)
            adjustments['elevated_alignment'] = 3.0  # +3% (increased from +2% per market evidence)

        elif alignment == 'subway_tunnel':
            # Subway/tunnel: SIGNIFICANT LOWER impact (subsurface)
            # - Surface remains fully usable (buildings, parking, landscaping)
            # - Noise substantially buffered by earth cover
            # - Vibration reduced (though still present)
            # - No visual impact (underground structure)
            # Market evidence: Subsurface easements typically -50% of fee
            # Research shows property value preservation with subsurface alignment
            adjustments['subway_tunnel_alignment'] = -8.0  # -8% (increased from -3% per research)

        elif alignment == 'trench':
            # Trench/cut: Moderate reduction (partially subsurface)
            # - Some surface disruption (access restrictions near edges)
            # - Noise partially buffered by trench walls
            # - Visual impact reduced vs. at-grade
            # - More usable than at-grade, less than full tunnel
            adjustments['trench_alignment'] = -3.0  # -3% (increased from -1%)

        # at_grade: No adjustment (baseline - standard rail corridor impact)

        # 2. Train frequency impact - MARKET-ALIGNED
        trains_per_day = self.easement_data.get('trains_per_day', 0)
        if trains_per_day > 50:
            # Very high frequency (>50 trains/day)
            # Constant noise, limited quiet periods
            # Research: "Significantly negative impact on housing values"
            adjustments['high_frequency'] = 5.0  # +5% (increased from +3% per research)
        elif trains_per_day > 20:
            # Moderate-high frequency (20-50 trains/day)
            # Research: Discount increases with noise nuisance levels
            adjustments['moderate_frequency'] = 3.0  # +3% (increased from +1.5%)

        # 2. Grade crossing safety and traffic disruption
        grade_crossings = self.easement_data.get('grade_crossings', 0)
        if grade_crossings > 0:
            # At-grade crossings:
            # - Safety concerns (vehicle-train collisions)
            # - Traffic disruption (crossing gates, delays)
            # - Liability concerns for adjacent property
            adjustments['grade_crossing_safety'] = min(grade_crossings * 1.0, 3.0)  # +1% per crossing (max +3%)

        # 3. Vibration impact (proximity to buildings) - MARKET-ALIGNED
        distance_to_buildings = self.easement_data.get('distance_to_buildings_m', 100)
        rail_type = self.easement_data.get('rail_type', '')

        if distance_to_buildings < 30 and 'heavy_rail' in rail_type:
            # Heavy rail within 30m of buildings
            # Research: "Price depreciation of over-track real estate property"
            # 44% of rail sections exceed vibration limits (1,604 sections studied)
            # Significant structural damage risk, marketability severely impacted
            adjustments['vibration_impact'] = 5.0  # +5% (increased from +2.5% per research)
        elif distance_to_buildings < 50:
            # Within 50m of buildings (any rail type)
            # Perceptible vibration, marketability impact
            # Research: Ground-borne vibration "negatively affects property values"
            adjustments['vibration_impact'] = 3.0  # +3% (increased from +1.5%)

        # 4. Noise mitigation absence - MARKET-ALIGNED
        has_noise_barriers = self.easement_data.get('has_noise_barriers', False)
        if not has_noise_barriers and trains_per_day > 10:
            # No noise barriers with significant train frequency
            # Full noise impact on adjacent property
            # 31% of rail projects exceed ground-borne noise limits (research)
            adjustments['no_noise_mitigation'] = 4.0  # +4% (increased from +2%)

        # 5. Service hours (24-hour operation) - MARKET-ALIGNED
        service_hours_per_day = self.easement_data.get('service_hours_per_day', 16)
        if service_hours_per_day >= 20:
            # 24-hour or near 24-hour service
            # No quiet nighttime periods, sleep disruption, health impacts
            adjustments['extended_hours'] = 2.5  # +2.5% (increased from +1.5%)

        # 6. Electrified vs. diesel
        is_electrified = self.easement_data.get('is_electrified', True)
        if not is_electrified and 'heavy_rail' in rail_type:
            # Diesel heavy rail
            # Additional air quality concerns (particulates, fumes)
            adjustments['diesel_emissions'] = 1.0  # +1%

        # 7. Freight vs. passenger safety perception
        if rail_type == 'heavy_rail_freight':
            # Freight rail carries hazardous materials
            # Public perception of risk (derailment, spills)
            hazmat_traffic = self.easement_data.get('hazmat_traffic', False)
            if hazmat_traffic:
                adjustments['hazmat_risk_perception'] = 1.5  # +1.5%

        return adjustments

    def _get_dynamic_weights(self) -> Dict[str, float]:
        """
        Rail-specific reconciliation weights.

        Rail easements favor percentage of fee method because:
        - Rail type is a strong predictor (freight vs. passenger vs. light rail)
        - Noise and vibration impacts are property-specific (before/after supportive)
        - Limited rental market data (income approach less reliable)

        Returns:
            Dict with weights and reasoning
        """
        # Allow user override
        user_weights = self.market_data.get('reconciliation_weights')
        if user_weights:
            return user_weights

        # Rail corridor: Percentage of fee dominant, before/after supportive
        return {
            'percentage_of_fee': 0.50,       # Strongest (rail type is strong predictor)
            'income_capitalization': 0.20,   # Weakest (limited rental market data)
            'before_after': 0.30,            # Supportive (property-specific noise/vibration impacts)
            'reasoning': 'Rail Corridor: Percentage of fee strongest (rail type predictor), before/after supportive (property-specific noise/vibration impacts)'
        }


def main():
    """Main execution function for rail easement calculator."""
    parser = argparse.ArgumentParser(
        description='Calculate rail/transit corridor easement value'
    )
    parser.add_argument('input_file', help='Path to input JSON file with rail_type parameter')
    parser.add_argument('--output', '-o', help='Path to output JSON file (optional)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Print detailed output')

    args = parser.parse_args()

    # Load input
    with open(args.input_file, 'r') as f:
        input_data = json.load(f)

    # Validate rail-specific parameters
    if 'rail_type' not in input_data.get('easement', {}):
        print("ERROR: Rail easement calculator requires 'rail_type' parameter")
        print("\nExpected input format:")
        print("""
{
  "property": {...},
  "easement": {
    "type": "rail",
    "rail_type": "heavy_rail_freight",
    "area_acres": 3,
    "trains_per_day": 40,
    "grade_crossings": 1,
    "distance_to_buildings_m": 25,
    ...
  },
  "market_parameters": {...}
}
        """)
        print("\nValid rail_type values:")
        print("  - heavy_rail_freight")
        print("  - heavy_rail_passenger")
        print("  - light_rail")
        print("  - subway_surface")
        print("  - bus_rapid_transit")
        sys.exit(1)

    # Calculate
    calculator = RailEasementCalculator(input_data)
    results = calculator.calculate_all_methods()

    # Output
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results written to {args.output}")

    if args.verbose or not args.output:
        print(json.dumps(results, indent=2))

    # Print summary
    rail_type = input_data['easement'].get('rail_type', 'N/A')
    trains_per_day = input_data['easement'].get('trains_per_day', 0)
    print(f"\n{'='*80}")
    print(f"RAIL CORRIDOR EASEMENT VALUATION (v2.0)")
    print(f"{'='*80}")
    print(f"Property: {input_data['property'].get('address', 'N/A')}")
    print(f"Rail Type: {rail_type.replace('_', ' ').title()}")
    print(f"Train Frequency: {trains_per_day} trains/day")
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
