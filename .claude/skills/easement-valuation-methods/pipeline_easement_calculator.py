#!/usr/bin/env python3
"""
Pipeline Corridor Easement Calculator - MARKET-ALIGNED v2.1

Specialized calculator for pipeline easements (subsurface and surface).

VERSION 2.1 (2025-11-17): Updated to MARKET-ALIGNED values based on IRWA analysis
(61.4% weighted impact for 16" pipeline) and subsurface market evidence (-50% typical).

Domain-specific features (MARKET-ALIGNED):
- Pipeline type-based percentage ranges (crude oil: 38%, natural gas: 35%, water: 26%)
- High pressure adjustment: +4% (>1000 psi) - rupture risk
- Depth: Shallow (<1m) +3%, Deep (>3m) -5% - subsurface allows surface use
- Diameter: Large (750-1000mm) +3%, Very large (>1000mm) +5% - ROW impact
- Water proximity: Crude oil <100m +4%, Any <100m +2% - environmental stigma
- Aging infrastructure (>40 years): +2.5% - liability concerns

Pipeline types (MARKET-ALIGNED):
- Crude Oil Transmission:    35-42% (38% base) - environmental risk, stigma
- Natural Gas Transmission:  32-39% (35% base) - explosion risk, safety setbacks
- Natural Gas Distribution:  25-32% (28% base) - lower pressure, urban
- Water Transmission:        25-29% (26% base) - lower risk, essential utility
- Sewer:                     25-28% (25% base) - minimum market range, gravity

Research basis:
- IRWA analysis: 61.4% weighted impact for 16" pipeline (85% over diameter + 24" risk area)
- Market evidence: 25-50% permanent easement range, 50% of easement land value typical
- Subsurface evidence: -50% typical for deep burial allowing full surface use

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


class PipelineEasementCalculator(EasementCalculatorBase):
    """
    Pipeline corridor easement valuation calculator.

    Implements pipeline type and pressure-based percentage methodology and pipeline-specific adjustments.
    """

    def get_base_percentage(self) -> float:
        """
        Get base percentage for pipeline by type and pressure.

        Pipeline type ranges reflect:
        - Product transported (crude oil, natural gas, water, sewer)
        - Operating pressure (transmission vs. distribution)
        - Safety setbacks and leak risk
        - Environmental impact potential
        - Regulatory requirements (pipeline safety regulations)

        Returns:
            float: Base percentage (e.g., 16.0 for 16%)

        Raises:
            ValueError: If pipeline_type parameter is missing
        """
        pipe_type = self.easement_data.get('pipeline_type')

        if pipe_type is None:
            raise ValueError(
                "Pipeline easement calculator requires 'pipeline_type' parameter. "
                "Valid values: 'crude_oil_transmission', 'natural_gas_transmission', "
                "'natural_gas_distribution', 'water_transmission', 'sewer'"
            )

        # Pipeline type-based percentage tiers (MARKET-ALIGNED: 25-50% range per IRWA)
        # Research: IRWA analysis shows 61.4% weighted impact for 16" pipeline
        # Market evidence: 25-50% of affected land value typical
        base_percentages = {
            'crude_oil_transmission': 38.0,      # 35-42% (high pressure, leak risk, environmental concerns)
            'natural_gas_transmission': 35.0,    # 32-39% (high pressure, safety setbacks, explosion risk)
            'natural_gas_distribution': 28.0,    # 25-32% (lower pressure, but still hazardous)
            'water_transmission': 26.0,          # 25-29% (lower risk, but still restricts use)
            'sewer': 25.0                        # 25-28% (minimum market range, gravity flow)
        }

        base_pct = base_percentages.get(pipe_type)
        if base_pct is None:
            raise ValueError(
                f"Invalid pipeline_type '{pipe_type}'. Valid values: "
                f"{', '.join(base_percentages.keys())}"
            )

        # Pressure adjustment (transmission pressure = higher percentage) - MARKET-ALIGNED
        pressure_psi = self.easement_data.get('pressure_psi', 0)
        if pressure_psi > 1000 and 'transmission' in pipe_type:
            # High pressure transmission (>1000 psi)
            # Greater safety setbacks, larger ROW, increased rupture risk
            base_pct += 4.0  # +4% for high pressure (increased from +2%)

        return base_pct

    def get_domain_specific_adjustments(self) -> Dict[str, float]:
        """
        Get pipeline-specific percentage adjustments.

        Pipeline-specific factors:
        1. Burial depth (shallow = higher impact, deep = lower impact)
        2. Diameter (larger pipe = larger ROW and construction impact)
        3. Leak detection systems (modern safety = lower risk)
        4. Cathodic protection (corrosion prevention)
        5. Access road requirements
        6. Proximity to water bodies (environmental risk)

        Returns:
            Dict[str, float]: {adjustment_name: percentage_value}
        """
        adjustments = {}

        # 1. Burial depth impact - MARKET-ALIGNED
        depth_m = self.easement_data.get('depth_meters', 1.5)
        if depth_m < 1.0:
            # Shallow burial (<1m)
            # Restricts cultivation, excavation, tree planting
            # Higher interference with land use
            adjustments['shallow_burial'] = 3.0  # +3% (increased from +1.5%)
        elif depth_m > 3.0:
            # Deep burial (>3m)
            # Research: Subsurface easements typically -50% of fee value
            # Less surface impact, allows full surface use in many cases
            # Property owner retains reasonable use
            adjustments['deep_burial'] = -5.0  # -5% (increased from -0.5% per research)

        # 2. Diameter impact (larger pipe = larger ROW) - MARKET-ALIGNED
        diameter_mm = self.easement_data.get('diameter_mm', 300)
        # Research: IRWA shows pipe diameter + 24" risk area = 85% impact over that zone
        if diameter_mm > 1000:
            # Very large diameter (>1000mm / 40")
            # Massive ROW, major construction impact, significant land fragmentation
            adjustments['very_large_diameter'] = 5.0  # +5% (increased from +2%)
        elif diameter_mm > 750:
            # Large diameter (750-1000mm / 30-40")
            # Wider ROW for construction and maintenance
            # Greater land take and restrictions
            adjustments['large_diameter'] = 3.0  # +3% (increased from +1%)

        # 3. Leak detection and monitoring systems
        has_leak_detection = self.easement_data.get('has_leak_detection', False)
        if has_leak_detection:
            # Modern SCADA (Supervisory Control and Data Acquisition)
            # Automated leak detection reduces risk perception
            adjustments['leak_detection_systems'] = -0.5  # -0.5% (risk mitigation)

        # 4. Cathodic protection (corrosion prevention)
        has_cathodic_protection = self.easement_data.get('has_cathodic_protection', True)
        if not has_cathodic_protection:
            # No cathodic protection = higher corrosion risk
            # Particularly important for older pipelines
            adjustments['no_corrosion_protection'] = 1.0  # +1%

        # 5. Access road requirements - MARKET-ALIGNED
        requires_access_road = self.easement_data.get('requires_access_road', False)
        if requires_access_road:
            # Permanent access road for maintenance
            # Additional land take beyond pipeline ROW, ongoing disruption
            adjustments['access_road'] = 2.5  # +2.5% (increased from +1%)

        # 6. Proximity to water bodies (environmental risk) - MARKET-ALIGNED
        distance_to_water_m = self.easement_data.get('distance_to_water_m', 999)
        pipe_type = self.easement_data.get('pipeline_type', '')

        if distance_to_water_m < 100 and 'crude_oil' in pipe_type:
            # Oil pipeline within 100m of watercourse
            # High environmental risk, regulatory scrutiny
            # Significant liability concerns, property stigma
            adjustments['water_proximity_risk'] = 4.0  # +4% (increased from +2%)
        elif distance_to_water_m < 100:
            # Any pipeline within 100m of watercourse
            # Environmental risk, regulatory oversight
            adjustments['water_proximity'] = 2.0  # +2% (increased from +1%)

        # 7. Horizontal directional drilling (HDD) vs. open cut
        installation_method = self.easement_data.get('installation_method', 'open_cut')
        if installation_method == 'hdd':
            # HDD = less surface disturbance, faster restoration
            # Lower impact on agricultural operations
            adjustments['hdd_installation'] = -0.5  # -0.5%

        # 8. ROW width vs. standard
        row_width_m = self.easement_data.get('width_meters', 20)
        if row_width_m > 30:
            # Extra-wide ROW (>30m)
            # May indicate multiple pipelines or special conditions
            adjustments['extra_wide_row'] = 1.5  # +1.5%

        # 9. Pipeline age and condition - MARKET-ALIGNED
        pipeline_age_years = self.easement_data.get('pipeline_age_years', 10)
        if pipeline_age_years > 40:
            # Old pipeline (>40 years)
            # Higher maintenance frequency, leak risk perception
            # Property owner liability concerns, insurance issues
            adjustments['aging_infrastructure'] = 2.5  # +2.5% (increased from +1%)

        # 10. Regulatory class location (populated area = stricter requirements) - MARKET-ALIGNED
        class_location = self.easement_data.get('class_location', 1)
        if class_location >= 3:
            # Class 3 or 4 (residential/urban area)
            # Stricter safety requirements, more frequent inspections
            # Higher public concern, property value impact
            adjustments['high_consequence_area'] = 3.0  # +3% (increased from +1.5%)

        return adjustments

    def _get_dynamic_weights(self) -> Dict[str, float]:
        """
        Pipeline-specific reconciliation weights.

        Pipeline easements favor percentage of fee with balanced support:
        - Pipeline type and pressure are strong predictors
        - Subsurface nature means income loss is quantifiable (farm productivity)
        - Before/after captures property-specific access restrictions

        Returns:
            Dict with weights and reasoning
        """
        # Allow user override
        user_weights = self.market_data.get('reconciliation_weights')
        if user_weights:
            return user_weights

        # Pipeline: Balanced approach with slight percentage of fee preference
        return {
            'percentage_of_fee': 0.45,       # Strongest (pipeline type/pressure predictor)
            'income_capitalization': 0.30,   # Supportive (agricultural productivity loss)
            'before_after': 0.25,            # Supportive (property-specific access restrictions)
            'reasoning': 'Pipeline: Percentage of fee strongest (pipeline type/pressure predictor), balanced support from income and before/after methods'
        }


def main():
    """Main execution function for pipeline easement calculator."""
    parser = argparse.ArgumentParser(
        description='Calculate pipeline corridor easement value'
    )
    parser.add_argument('input_file', help='Path to input JSON file with pipeline_type parameter')
    parser.add_argument('--output', '-o', help='Path to output JSON file (optional)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Print detailed output')

    args = parser.parse_args()

    # Load input
    with open(args.input_file, 'r') as f:
        input_data = json.load(f)

    # Validate pipeline-specific parameters
    if 'pipeline_type' not in input_data.get('easement', {}):
        print("ERROR: Pipeline easement calculator requires 'pipeline_type' parameter")
        print("\nExpected input format:")
        print("""
{
  "property": {...},
  "easement": {
    "type": "pipeline",
    "pipeline_type": "natural_gas_transmission",
    "area_acres": 2,
    "pressure_psi": 1200,
    "diameter_mm": 600,
    "depth_meters": 1.5,
    ...
  },
  "market_parameters": {...}
}
        """)
        print("\nValid pipeline_type values:")
        print("  - crude_oil_transmission")
        print("  - natural_gas_transmission")
        print("  - natural_gas_distribution")
        print("  - water_transmission")
        print("  - sewer")
        sys.exit(1)

    # Calculate
    calculator = PipelineEasementCalculator(input_data)
    results = calculator.calculate_all_methods()

    # Output
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results written to {args.output}")

    if args.verbose or not args.output:
        print(json.dumps(results, indent=2))

    # Print summary
    pipe_type = input_data['easement'].get('pipeline_type', 'N/A')
    pressure = input_data['easement'].get('pressure_psi', 0)
    diameter = input_data['easement'].get('diameter_mm', 0)
    print(f"\n{'='*80}")
    print(f"PIPELINE EASEMENT VALUATION (v2.0)")
    print(f"{'='*80}")
    print(f"Property: {input_data['property'].get('address', 'N/A')}")
    print(f"Pipeline Type: {pipe_type.replace('_', ' ').title()}")
    print(f"Pressure: {pressure} psi")
    print(f"Diameter: {diameter} mm ({diameter/25.4:.1f} inches)")
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
