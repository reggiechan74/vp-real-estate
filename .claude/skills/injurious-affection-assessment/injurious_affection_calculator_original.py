#!/usr/bin/env python3
"""
Injurious Affection Calculator - Quantifies Damages from Construction and Proximity Impacts

Calculates comprehensive damages from:
- Noise impacts (dBA levels, duration, receptor sensitivity)
- Dust and air quality (PM2.5/PM10, cleaning costs)
- Vibration damage (PPV thresholds, repair costs)
- Traffic disruption (lost sales, access costs)
- Visual impairment (permanent impacts)
- Business losses (temporary and ongoing)

Based on Ontario expropriation law and construction impact assessment methodologies.

Author: Claude Code
Version: 1.0.0
Date: 2025-11-15
"""

import json
import sys
import math
from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from typing import List, Optional, Dict, Any, Literal
from pathlib import Path


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class PropertyDetails:
    """
    Property characteristics for impact assessment
    """
    property_type: Literal['residential', 'commercial', 'industrial']
    property_value: float  # Market value ($)
    rental_income_monthly: float = 0.0  # Monthly rental income ($)
    distance_to_construction_m: float = 0.0  # Distance to construction (meters)
    number_of_units: int = 1  # For multi-unit residential
    business_type: Optional[str] = None  # e.g., "restaurant", "retail", "office"
    annual_revenue: float = 0.0  # For business loss calculations
    background_noise_dba: float = 50.0  # Ambient noise level (dBA)


@dataclass
class ConstructionActivity:
    """
    Construction activities causing impacts
    """
    duration_months: float  # Total construction duration
    equipment: List[Dict[str, Any]] = field(default_factory=list)  # Equipment list
    dust_impact_zone: Literal['high', 'moderate', 'low'] = 'moderate'
    vibration_ppv_mms: float = 0.0  # Peak particle velocity (mm/s)
    traffic_reduction_pct: float = 0.0  # % reduction in traffic/access
    construction_hours_per_day: int = 8  # Hours per day
    night_work: bool = False  # Construction during night hours


@dataclass
class NoiseEquipment:
    """
    Individual equipment noise characteristics
    """
    equipment_type: str  # e.g., "pile_driver", "jackhammer"
    dba_at_15m: float  # Sound level at 15 meters
    hours_per_day: float  # Operating hours per day
    days_per_week: int = 5  # Operating days per week


@dataclass
class MarketParameters:
    """
    Market parameters for valuation
    """
    # Noise impact thresholds
    residential_moderate_threshold_dba: float = 65.0
    residential_severe_threshold_dba: float = 75.0
    commercial_moderate_threshold_dba: float = 70.0
    commercial_severe_threshold_dba: float = 80.0
    industrial_threshold_dba: float = 85.0

    # Rent reduction percentages
    residential_moderate_rent_reduction_pct: float = 0.075  # 7.5%
    residential_severe_rent_reduction_pct: float = 0.20  # 20%
    commercial_moderate_rent_reduction_pct: float = 0.055  # 5.5%
    commercial_severe_rent_reduction_pct: float = 0.125  # 12.5%

    # Dust cleaning costs
    residential_cleaning_cost: float = 200.0  # Per cleaning event
    commercial_cleaning_cost: float = 1000.0  # Per cleaning event
    high_impact_cleaning_frequency_weeks: int = 1  # Weekly for high impact
    moderate_impact_cleaning_frequency_weeks: int = 2  # Bi-weekly
    low_impact_cleaning_frequency_weeks: int = 4  # Monthly

    # Vibration repair costs (cosmetic damage)
    cosmetic_repair_cost_per_incident: float = 2500.0
    structural_repair_multiplier: float = 10.0  # Structural is 10x cosmetic

    # Traffic disruption
    sales_conversion_rate: float = 0.02  # 2% of traffic converts to sales
    average_transaction_value: float = 50.0
    gross_margin_pct: float = 0.40  # 40% margin

    # Capitalization rate for permanent impacts
    capitalization_rate: float = 0.08  # 8% cap rate


@dataclass
class NoiseImpactResult:
    """
    Results from noise impact assessment
    """
    noise_level_at_property_dba: float
    impact_severity: str  # "none", "moderate", "severe"
    rent_reduction_pct: float
    duration_months: float
    monthly_rental_loss: float
    total_noise_damage: float
    equipment_breakdown: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class DustImpactResult:
    """
    Results from dust impact assessment
    """
    impact_zone: str  # "high", "moderate", "low"
    cleaning_frequency_weeks: int
    cleaning_cost_per_event: float
    number_of_cleanings: int
    total_dust_damage: float
    health_impact_cost: float = 0.0  # Additional health-related costs


@dataclass
class VibrationImpactResult:
    """
    Results from vibration damage assessment
    """
    peak_particle_velocity_mms: float
    damage_threshold: str  # "none", "cosmetic", "structural"
    repair_cost_estimate: float
    total_vibration_damage: float


@dataclass
class TrafficImpactResult:
    """
    Results from traffic disruption assessment
    """
    traffic_reduction_pct: float
    baseline_traffic_daily: float
    lost_traffic_daily: float
    lost_sales_daily: float
    lost_profit_daily: float
    duration_months: float
    total_traffic_damage: float


@dataclass
class BusinessLossResult:
    """
    Results from business loss assessment
    """
    baseline_revenue_monthly: float
    revenue_reduction_pct: float
    lost_revenue_monthly: float
    lost_profit_monthly: float
    duration_months: float
    total_business_loss: float
    mitigation_efforts: List[str] = field(default_factory=list)


@dataclass
class VisualImpactResult:
    """
    Results from permanent visual impact assessment
    """
    visual_impact_description: str
    property_value_reduction_pct: float
    permanent_value_loss: float
    capitalized_impact: float


@dataclass
class InjuriousAffectionSummary:
    """
    Complete summary of all injurious affection damages
    """
    # Input details
    property_address: str
    property_type: str
    property_value: float
    assessment_date: str

    # Impact results
    noise_impact: NoiseImpactResult
    dust_impact: DustImpactResult
    vibration_impact: VibrationImpactResult
    traffic_impact: TrafficImpactResult
    business_loss: BusinessLossResult
    visual_impact: Optional[VisualImpactResult] = None

    # Total damages
    total_temporary_damages: float = 0.0
    total_permanent_damages: float = 0.0
    total_injurious_affection: float = 0.0

    # Breakdown by category
    damages_by_category: Dict[str, float] = field(default_factory=dict)

    def calculate_totals(self):
        """Calculate total damages across all categories"""
        # Temporary damages (construction period)
        self.total_temporary_damages = (
            self.noise_impact.total_noise_damage +
            self.dust_impact.total_dust_damage +
            self.vibration_impact.total_vibration_damage +
            self.traffic_impact.total_traffic_damage +
            self.business_loss.total_business_loss
        )

        # Permanent damages
        self.total_permanent_damages = 0.0
        if self.visual_impact:
            self.total_permanent_damages = self.visual_impact.capitalized_impact

        # Total injurious affection
        self.total_injurious_affection = (
            self.total_temporary_damages +
            self.total_permanent_damages
        )

        # Category breakdown
        self.damages_by_category = {
            'noise': self.noise_impact.total_noise_damage,
            'dust': self.dust_impact.total_dust_damage,
            'vibration': self.vibration_impact.total_vibration_damage,
            'traffic': self.traffic_impact.total_traffic_damage,
            'business_loss': self.business_loss.total_business_loss,
            'visual_permanent': self.total_permanent_damages
        }


# ============================================================================
# NOISE IMPACT CALCULATIONS
# ============================================================================

def calculate_noise_attenuation(dba_at_15m: float, distance_m: float) -> float:
    """
    Calculate noise level at distance using 6 dBA per doubling rule

    Args:
        dba_at_15m: Noise level at 15 meters (dBA)
        distance_m: Distance to receptor (meters)

    Returns:
        Noise level at receptor distance (dBA)
    """
    if distance_m <= 0:
        raise ValueError(f"Distance must be positive: {distance_m}")

    # Number of doublings from 15m to target distance
    # Each doubling reduces noise by 6 dBA
    doublings = math.log2(distance_m / 15.0)
    attenuation = 6.0 * doublings

    noise_at_distance = dba_at_15m - attenuation

    return max(0, noise_at_distance)  # Can't go below 0


def assess_noise_impact(
    property_details: PropertyDetails,
    construction: ConstructionActivity,
    params: MarketParameters
) -> NoiseImpactResult:
    """
    Assess noise impact and calculate damages

    Args:
        property_details: Property characteristics
        construction: Construction activities
        params: Market parameters

    Returns:
        NoiseImpactResult with detailed assessment
    """
    equipment_breakdown = []
    max_noise_level = property_details.background_noise_dba

    # Calculate noise from each piece of equipment
    for equip_data in construction.equipment:
        equip = NoiseEquipment(**equip_data)

        noise_at_property = calculate_noise_attenuation(
            equip.dba_at_15m,
            property_details.distance_to_construction_m
        )

        equipment_breakdown.append({
            'equipment_type': equip.equipment_type,
            'dba_at_15m': equip.dba_at_15m,
            'dba_at_property': noise_at_property,
            'hours_per_day': equip.hours_per_day,
            'days_per_week': equip.days_per_week
        })

        # Use maximum noise level (worst case)
        max_noise_level = max(max_noise_level, noise_at_property)

    # Determine impact severity based on property type
    impact_severity = "none"
    rent_reduction_pct = 0.0

    if property_details.property_type == 'residential':
        # Check for night work (more severe impact)
        night_multiplier = 1.5 if construction.night_work else 1.0

        if max_noise_level >= params.residential_severe_threshold_dba:
            impact_severity = "severe"
            rent_reduction_pct = params.residential_severe_rent_reduction_pct * night_multiplier
        elif max_noise_level >= params.residential_moderate_threshold_dba:
            impact_severity = "moderate"
            rent_reduction_pct = params.residential_moderate_rent_reduction_pct * night_multiplier

    elif property_details.property_type == 'commercial':
        if max_noise_level >= params.commercial_severe_threshold_dba:
            impact_severity = "severe"
            rent_reduction_pct = params.commercial_severe_rent_reduction_pct
        elif max_noise_level >= params.commercial_moderate_threshold_dba:
            impact_severity = "moderate"
            rent_reduction_pct = params.commercial_moderate_rent_reduction_pct

    elif property_details.property_type == 'industrial':
        if max_noise_level >= params.industrial_threshold_dba:
            impact_severity = "moderate"
            rent_reduction_pct = 0.03  # 3% for industrial

    # Cap reduction at reasonable maximum
    rent_reduction_pct = min(rent_reduction_pct, 0.30)  # Max 30% reduction

    # Calculate monetary damages
    monthly_rental_loss = (
        property_details.rental_income_monthly *
        property_details.number_of_units *
        rent_reduction_pct
    )

    total_noise_damage = monthly_rental_loss * construction.duration_months

    return NoiseImpactResult(
        noise_level_at_property_dba=max_noise_level,
        impact_severity=impact_severity,
        rent_reduction_pct=rent_reduction_pct,
        duration_months=construction.duration_months,
        monthly_rental_loss=monthly_rental_loss,
        total_noise_damage=total_noise_damage,
        equipment_breakdown=equipment_breakdown
    )


# ============================================================================
# DUST IMPACT CALCULATIONS
# ============================================================================

def assess_dust_impact(
    property_details: PropertyDetails,
    construction: ConstructionActivity,
    params: MarketParameters
) -> DustImpactResult:
    """
    Assess dust impact and calculate cleaning costs

    Args:
        property_details: Property characteristics
        construction: Construction activities
        params: Market parameters

    Returns:
        DustImpactResult with cleaning cost estimates
    """
    impact_zone = construction.dust_impact_zone

    # Determine cleaning frequency and cost
    if impact_zone == 'high':
        cleaning_frequency_weeks = params.high_impact_cleaning_frequency_weeks
    elif impact_zone == 'moderate':
        cleaning_frequency_weeks = params.moderate_impact_cleaning_frequency_weeks
    else:  # low
        cleaning_frequency_weeks = params.low_impact_cleaning_frequency_weeks

    # Select cleaning cost by property type
    if property_details.property_type == 'residential':
        cleaning_cost = params.residential_cleaning_cost
    else:
        cleaning_cost = params.commercial_cleaning_cost

    # Calculate number of cleanings
    duration_weeks = construction.duration_months * 4.33  # Average weeks per month
    number_of_cleanings = int(duration_weeks / cleaning_frequency_weeks)

    # Total cleaning costs
    total_cleaning_cost = (
        cleaning_cost *
        number_of_cleanings *
        property_details.number_of_units
    )

    # Health impacts (only for severe cases in high impact zones)
    health_impact_cost = 0.0
    if (impact_zone == 'high' and
        property_details.property_type == 'residential' and
        construction.duration_months >= 6):
        # Conservative estimate for potential health impacts
        health_impact_cost = 5000.0 * property_details.number_of_units

    total_dust_damage = total_cleaning_cost + health_impact_cost

    return DustImpactResult(
        impact_zone=impact_zone,
        cleaning_frequency_weeks=cleaning_frequency_weeks,
        cleaning_cost_per_event=cleaning_cost,
        number_of_cleanings=number_of_cleanings,
        total_dust_damage=total_dust_damage,
        health_impact_cost=health_impact_cost
    )


# ============================================================================
# VIBRATION IMPACT CALCULATIONS
# ============================================================================

def assess_vibration_impact(
    construction: ConstructionActivity,
    params: MarketParameters
) -> VibrationImpactResult:
    """
    Assess vibration damage and estimate repair costs

    PPV (Peak Particle Velocity) thresholds:
    - Cosmetic damage: 5-12 mm/s
    - Structural damage: >12 mm/s

    Args:
        construction: Construction activities
        params: Market parameters

    Returns:
        VibrationImpactResult with damage assessment
    """
    ppv = construction.vibration_ppv_mms

    damage_threshold = "none"
    repair_cost = 0.0

    if ppv >= 12.0:
        damage_threshold = "structural"
        repair_cost = (
            params.cosmetic_repair_cost_per_incident *
            params.structural_repair_multiplier
        )
    elif ppv >= 5.0:
        damage_threshold = "cosmetic"
        repair_cost = params.cosmetic_repair_cost_per_incident

    return VibrationImpactResult(
        peak_particle_velocity_mms=ppv,
        damage_threshold=damage_threshold,
        repair_cost_estimate=repair_cost,
        total_vibration_damage=repair_cost
    )


# ============================================================================
# TRAFFIC DISRUPTION CALCULATIONS
# ============================================================================

def assess_traffic_impact(
    property_details: PropertyDetails,
    construction: ConstructionActivity,
    params: MarketParameters
) -> TrafficImpactResult:
    """
    Assess traffic disruption and calculate lost sales

    Only applicable to commercial/retail properties

    Args:
        property_details: Property characteristics
        construction: Construction activities
        params: Market parameters

    Returns:
        TrafficImpactResult with lost sales estimates
    """
    if property_details.property_type != 'commercial':
        # No traffic impact for non-commercial
        return TrafficImpactResult(
            traffic_reduction_pct=0.0,
            baseline_traffic_daily=0.0,
            lost_traffic_daily=0.0,
            lost_sales_daily=0.0,
            lost_profit_daily=0.0,
            duration_months=0.0,
            total_traffic_damage=0.0
        )

    # Estimate baseline traffic from annual revenue
    # Working backwards: Revenue = Traffic × Conversion × Avg Transaction
    baseline_annual_sales = property_details.annual_revenue

    if baseline_annual_sales > 0:
        baseline_daily_sales = baseline_annual_sales / 365
        baseline_daily_transactions = baseline_daily_sales / params.average_transaction_value
        baseline_traffic_daily = baseline_daily_transactions / params.sales_conversion_rate
    else:
        # Use default estimate if no revenue provided
        baseline_traffic_daily = 1000.0  # Default assumption

    # Calculate lost traffic
    lost_traffic_daily = baseline_traffic_daily * construction.traffic_reduction_pct

    # Convert to lost sales
    lost_transactions = lost_traffic_daily * params.sales_conversion_rate
    lost_sales_daily = lost_transactions * params.average_transaction_value

    # Calculate lost profit (margin × sales)
    lost_profit_daily = lost_sales_daily * params.gross_margin_pct

    # Total over construction period
    days_in_period = construction.duration_months * 30.42  # Average days/month
    total_traffic_damage = lost_profit_daily * days_in_period

    return TrafficImpactResult(
        traffic_reduction_pct=construction.traffic_reduction_pct,
        baseline_traffic_daily=baseline_traffic_daily,
        lost_traffic_daily=lost_traffic_daily,
        lost_sales_daily=lost_sales_daily,
        lost_profit_daily=lost_profit_daily,
        duration_months=construction.duration_months,
        total_traffic_damage=total_traffic_damage
    )


# ============================================================================
# BUSINESS LOSS CALCULATIONS
# ============================================================================

def assess_business_loss(
    property_details: PropertyDetails,
    noise_impact: NoiseImpactResult,
    traffic_impact: TrafficImpactResult,
    construction: ConstructionActivity
) -> BusinessLossResult:
    """
    Assess overall business losses from combined impacts

    Args:
        property_details: Property characteristics
        noise_impact: Noise impact results
        traffic_impact: Traffic impact results
        construction: Construction activities

    Returns:
        BusinessLossResult with total business loss
    """
    baseline_revenue_monthly = property_details.annual_revenue / 12 if property_details.annual_revenue > 0 else 0

    # Estimate revenue reduction from noise impact
    # (Conservative: use half of rent reduction as proxy for revenue impact)
    noise_revenue_reduction_pct = noise_impact.rent_reduction_pct * 0.5

    # Traffic already captured separately, so use noise as baseline
    revenue_reduction_pct = noise_revenue_reduction_pct

    lost_revenue_monthly = baseline_revenue_monthly * revenue_reduction_pct

    # Assume 40% gross margin
    lost_profit_monthly = lost_revenue_monthly * 0.40

    total_business_loss = lost_profit_monthly * construction.duration_months

    # Note: Traffic impact is already calculated separately to avoid double-counting

    mitigation_efforts = []
    if revenue_reduction_pct > 0.10:
        mitigation_efforts.append("Signage to maintain customer awareness")
        mitigation_efforts.append("Extended hours to capture lost traffic")

    return BusinessLossResult(
        baseline_revenue_monthly=baseline_revenue_monthly,
        revenue_reduction_pct=revenue_reduction_pct,
        lost_revenue_monthly=lost_revenue_monthly,
        lost_profit_monthly=lost_profit_monthly,
        duration_months=construction.duration_months,
        total_business_loss=total_business_loss,
        mitigation_efforts=mitigation_efforts
    )


# ============================================================================
# VISUAL IMPACT CALCULATIONS (PERMANENT)
# ============================================================================

def assess_visual_impact(
    property_details: PropertyDetails,
    visual_impact_description: str,
    value_reduction_pct: float,
    params: MarketParameters
) -> VisualImpactResult:
    """
    Assess permanent visual impact damages

    Args:
        property_details: Property characteristics
        visual_impact_description: Description of visual impact
        value_reduction_pct: Estimated property value reduction (decimal)
        params: Market parameters

    Returns:
        VisualImpactResult with capitalized permanent damages
    """
    permanent_value_loss = property_details.property_value * value_reduction_pct

    # Capitalize as permanent annual loss
    # Annual loss = Value reduction × Cap rate
    # Total capitalized = Annual loss / Cap rate = Value reduction
    capitalized_impact = permanent_value_loss

    return VisualImpactResult(
        visual_impact_description=visual_impact_description,
        property_value_reduction_pct=value_reduction_pct,
        permanent_value_loss=permanent_value_loss,
        capitalized_impact=capitalized_impact
    )


# ============================================================================
# MAIN CALCULATION ORCHESTRATOR
# ============================================================================

def calculate_injurious_affection(
    property_details: PropertyDetails,
    construction: ConstructionActivity,
    params: MarketParameters,
    property_address: str = "",
    visual_impact_data: Optional[Dict[str, Any]] = None
) -> InjuriousAffectionSummary:
    """
    Calculate complete injurious affection damages

    Args:
        property_details: Property characteristics
        construction: Construction activities
        params: Market parameters
        property_address: Property address
        visual_impact_data: Optional visual impact parameters

    Returns:
        InjuriousAffectionSummary with complete damage assessment
    """
    # Assess each impact category
    noise_impact = assess_noise_impact(property_details, construction, params)
    dust_impact = assess_dust_impact(property_details, construction, params)
    vibration_impact = assess_vibration_impact(construction, params)
    traffic_impact = assess_traffic_impact(property_details, construction, params)
    business_loss = assess_business_loss(
        property_details, noise_impact, traffic_impact, construction
    )

    # Optional: Visual impact (permanent)
    visual_impact = None
    if visual_impact_data:
        visual_impact = assess_visual_impact(
            property_details,
            visual_impact_data.get('description', ''),
            visual_impact_data.get('value_reduction_pct', 0.0),
            params
        )

    # Create summary
    summary = InjuriousAffectionSummary(
        property_address=property_address or "Property",
        property_type=property_details.property_type,
        property_value=property_details.property_value,
        assessment_date=datetime.now().strftime('%Y-%m-%d'),
        noise_impact=noise_impact,
        dust_impact=dust_impact,
        vibration_impact=vibration_impact,
        traffic_impact=traffic_impact,
        business_loss=business_loss,
        visual_impact=visual_impact
    )

    # Calculate totals
    summary.calculate_totals()

    return summary


# ============================================================================
# JSON I/O
# ============================================================================

def load_from_json(json_path: str) -> tuple:
    """
    Load input parameters from JSON file

    Expected structure:
    {
        "property": {...},
        "construction": {...},
        "market_parameters": {...},  # Optional
        "visual_impact": {...}  # Optional
    }

    Returns:
        Tuple of (PropertyDetails, ConstructionActivity, MarketParameters, visual_impact_data)
    """
    with open(json_path, 'r') as f:
        data = json.load(f)

    property_details = PropertyDetails(**data['property'])
    construction = ConstructionActivity(**data['construction'])

    # Load market parameters or use defaults
    if 'market_parameters' in data:
        params = MarketParameters(**data['market_parameters'])
    else:
        params = MarketParameters()

    visual_impact_data = data.get('visual_impact')
    property_address = data.get('property_address', '')

    return property_details, construction, params, visual_impact_data, property_address


def save_to_json(summary: InjuriousAffectionSummary, output_path: str):
    """
    Save results to JSON file

    Args:
        summary: InjuriousAffectionSummary results
        output_path: Path to output JSON file
    """
    # Convert to dictionary
    results_dict = asdict(summary)

    with open(output_path, 'w') as f:
        json.dump(results_dict, f, indent=2)


# ============================================================================
# COMMAND-LINE INTERFACE
# ============================================================================

def main():
    """Command-line interface for injurious affection calculator"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Injurious Affection Calculator - Construction Impact Assessment'
    )
    parser.add_argument(
        'input_json',
        help='Path to input JSON file with property and construction data'
    )
    parser.add_argument(
        '--output',
        help='Path to output JSON file (default: auto-generated)',
        default=None
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Print detailed results to console'
    )

    args = parser.parse_args()

    # Load inputs
    print(f"Loading parameters from {args.input_json}...")
    property_details, construction, params, visual_impact_data, property_address = load_from_json(args.input_json)
    print(f"  ✓ Loaded property: {property_details.property_type}")
    print(f"  ✓ Construction duration: {construction.duration_months} months")

    # Calculate damages
    print("\nCalculating injurious affection damages...")
    summary = calculate_injurious_affection(
        property_details,
        construction,
        params,
        property_address,
        visual_impact_data
    )

    # Generate output filename if not provided
    if args.output is None:
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        args.output = f'injurious_affection_results_{timestamp}.json'

    # Save results
    print(f"\nSaving results to {args.output}...")
    save_to_json(summary, args.output)
    print("  ✓ Results saved")

    # Print summary
    print("\n" + "=" * 80)
    print("INJURIOUS AFFECTION DAMAGE ASSESSMENT")
    print("=" * 80)
    print(f"Property: {summary.property_address}")
    print(f"Property Type: {summary.property_type}")
    print(f"Property Value: ${summary.property_value:,.2f}")
    print(f"Assessment Date: {summary.assessment_date}")
    print()

    print("TEMPORARY DAMAGES (Construction Period):")
    print("-" * 80)
    print(f"1. Noise Impact:")
    print(f"   Noise Level: {summary.noise_impact.noise_level_at_property_dba:.1f} dBA")
    print(f"   Severity: {summary.noise_impact.impact_severity}")
    print(f"   Rent Reduction: {summary.noise_impact.rent_reduction_pct * 100:.1f}%")
    print(f"   Total Damage: ${summary.noise_impact.total_noise_damage:,.2f}")
    print()

    print(f"2. Dust Impact:")
    print(f"   Impact Zone: {summary.dust_impact.impact_zone}")
    print(f"   Cleanings Required: {summary.dust_impact.number_of_cleanings}")
    print(f"   Cost per Cleaning: ${summary.dust_impact.cleaning_cost_per_event:,.2f}")
    if summary.dust_impact.health_impact_cost > 0:
        print(f"   Health Impact Cost: ${summary.dust_impact.health_impact_cost:,.2f}")
    print(f"   Total Damage: ${summary.dust_impact.total_dust_damage:,.2f}")
    print()

    print(f"3. Vibration Impact:")
    print(f"   Peak Particle Velocity: {summary.vibration_impact.peak_particle_velocity_mms:.1f} mm/s")
    print(f"   Damage Threshold: {summary.vibration_impact.damage_threshold}")
    if summary.vibration_impact.total_vibration_damage > 0:
        print(f"   Repair Cost: ${summary.vibration_impact.repair_cost_estimate:,.2f}")
    print(f"   Total Damage: ${summary.vibration_impact.total_vibration_damage:,.2f}")
    print()

    print(f"4. Traffic Disruption:")
    if summary.traffic_impact.total_traffic_damage > 0:
        print(f"   Traffic Reduction: {summary.traffic_impact.traffic_reduction_pct * 100:.1f}%")
        print(f"   Lost Sales (Daily): ${summary.traffic_impact.lost_sales_daily:,.2f}")
        print(f"   Lost Profit (Daily): ${summary.traffic_impact.lost_profit_daily:,.2f}")
    print(f"   Total Damage: ${summary.traffic_impact.total_traffic_damage:,.2f}")
    print()

    print(f"5. Business Losses:")
    if summary.business_loss.total_business_loss > 0:
        print(f"   Revenue Reduction: {summary.business_loss.revenue_reduction_pct * 100:.1f}%")
        print(f"   Lost Profit (Monthly): ${summary.business_loss.lost_profit_monthly:,.2f}")
        if summary.business_loss.mitigation_efforts:
            print(f"   Mitigation Efforts: {', '.join(summary.business_loss.mitigation_efforts)}")
    print(f"   Total Damage: ${summary.business_loss.total_business_loss:,.2f}")
    print()

    if summary.visual_impact:
        print("PERMANENT DAMAGES:")
        print("-" * 80)
        print(f"Visual Impact: {summary.visual_impact.visual_impact_description}")
        print(f"Value Reduction: {summary.visual_impact.property_value_reduction_pct * 100:.1f}%")
        print(f"Capitalized Impact: ${summary.visual_impact.capitalized_impact:,.2f}")
        print()

    print("TOTAL DAMAGES:")
    print("-" * 80)
    print(f"Temporary Damages: ${summary.total_temporary_damages:,.2f}")
    print(f"Permanent Damages: ${summary.total_permanent_damages:,.2f}")
    print(f"TOTAL INJURIOUS AFFECTION: ${summary.total_injurious_affection:,.2f}")
    print()

    if args.verbose:
        print("DAMAGE BREAKDOWN BY CATEGORY:")
        print("-" * 80)
        for category, amount in summary.damages_by_category.items():
            pct_of_total = (amount / summary.total_injurious_affection * 100) if summary.total_injurious_affection > 0 else 0
            print(f"{category:20s}: ${amount:12,.2f}  ({pct_of_total:5.1f}%)")
        print()

        if summary.noise_impact.equipment_breakdown:
            print("NOISE EQUIPMENT BREAKDOWN:")
            print("-" * 80)
            for equip in summary.noise_impact.equipment_breakdown:
                print(f"{equip['equipment_type']:20s}: {equip['dba_at_15m']:5.1f} dBA @ 15m → "
                      f"{equip['dba_at_property']:5.1f} dBA @ property "
                      f"({equip['hours_per_day']:.1f} hrs/day)")

    print("=" * 80)
    print(f"\n✓ Assessment complete. Results saved to {args.output}")


if __name__ == '__main__':
    main()
