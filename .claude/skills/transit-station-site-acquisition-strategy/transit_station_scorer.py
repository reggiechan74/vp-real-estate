#!/usr/bin/env python3
"""
Transit Station Site Scoring Calculator

Scores and compares transit station site alternatives using TOD principles and
acquisition complexity analysis.

Scoring Categories:
1. TOD Potential (0-100, higher is better) - Density, mix, walkability, development potential
2. Multi-Modal Connections (0-100, higher is better) - Bus, bike, pedestrian, parking
3. Property Acquisition Complexity (0-100, LOWER is better) - Ownership, conflicts, environmental
4. Community Impact (0-100, LOWER is better) - Displacement, gentrification, heritage
5. Holdout Risk (0-30, LOWER is better) - Owner motivation, sophistication, alternatives

Author: Claude Code
Version: 1.0.0
Date: 2025-11-15
"""

import json
import sys
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime


# ==============================================================================
# DATA STRUCTURES
# ==============================================================================

@dataclass
class SiteIdentification:
    """Site identification information"""
    site_id: str
    site_name: str
    location: str
    station_type: str  # "urban", "suburban", "greenfield"
    description: str = ""


@dataclass
class TODCharacteristics:
    """Transit-Oriented Development characteristics"""
    # Existing density
    population_density_per_ha: float  # People per hectare
    employment_density_per_ha: float  # Jobs per hectare

    # Land use mix
    number_of_uses: int  # 1=single, 2=two, 3+=mixed
    jobs_housing_ratio: float  # Jobs:housing ratio

    # Walkability
    sidewalk_coverage_pct: float  # Percentage with sidewalks
    crossings_quality: str  # "poor", "adequate", "excellent"
    intersection_density_per_km2: float  # Intersections per km²

    # Development potential
    underutilized_land_pct: float  # Percentage underutilized
    zoning_supportiveness: str  # "restrictive", "moderate", "supportive"


@dataclass
class MultiModalConnections:
    """Multi-modal transportation connections"""
    # Bus integration
    bus_routes_within_200m: int
    bus_terminal_location: str  # "onsite", "adjacent", "remote"

    # Cycling
    bike_network_quality: str  # "none", "some", "complete"
    bike_parking_spaces: int

    # Pedestrian
    walkshed_population_800m: int  # Population within 800m

    # Parking
    kiss_ride_spaces: int
    park_ride_spaces: Optional[int] = None  # None for urban stations
    is_urban_station: bool = False  # Bonus for car-free focus


@dataclass
class AcquisitionComplexity:
    """Property acquisition complexity factors"""
    # Ownership
    number_of_owners: int

    # Land use conflicts
    households_displaced: int
    businesses_displaced: int
    institutional_impacts: int  # Schools, places of worship, heritage

    # Environmental
    contamination_level: str  # "minimal", "moderate", "severe"
    wetland_archaeological_count: int

    # Legal
    easements_covenants_count: int
    complex_tenancies_count: int
    litigation_title_disputes: int


@dataclass
class CommunityImpact:
    """Community impact assessment"""
    # Direct displacement
    total_households_displaced: int
    low_income_households: int
    senior_households: int
    disability_households: int

    # Gentrification risk
    neighborhood_income_level: str  # "high_income", "middle_income", "low_income"
    existing_displacement_pressure: bool

    # Cultural/heritage
    has_community_ties: bool  # Ethnic enclaves, multi-generational
    heritage_resources_count: int

    # Community support
    community_support_level: str  # "support", "mixed", "opposition"


@dataclass
class HoldoutRisk:
    """Holdout risk for critical parcels"""
    owner_motivation: str  # "willing", "neutral", "reluctant", "ideological"
    owner_sophistication: str  # "unsophisticated", "moderate", "sophisticated", "serial_holdout"
    owner_alternatives: str  # "strong", "some", "few", "none"


@dataclass
class SiteScoreSummary:
    """Complete scoring summary for a site"""
    site_id: str
    site_name: str

    # Individual scores
    tod_score: float  # 0-100, higher is better
    tod_breakdown: Dict[str, float]

    multi_modal_score: float  # 0-100, higher is better
    multi_modal_breakdown: Dict[str, float]

    complexity_score: float  # 0-100, LOWER is better
    complexity_breakdown: Dict[str, float]

    community_impact_score: float  # 0-100, LOWER is better
    community_impact_breakdown: Dict[str, float]

    holdout_risk_score: float  # 0-30, LOWER is better
    holdout_risk_breakdown: Dict[str, float]

    # Composite scores
    desirability_score: float  # (TOD + Multi-Modal) / 2
    feasibility_score: float  # 100 - ((Complexity + Community) / 2)
    overall_score: float  # Weighted average

    # Interpretation
    recommendation: str
    key_strengths: List[str]
    key_challenges: List[str]


# ==============================================================================
# SCORING FUNCTIONS
# ==============================================================================

def score_tod_potential(tod: TODCharacteristics) -> tuple[float, Dict[str, float]]:
    """
    Score TOD potential (0-100 points, higher is better)

    Returns:
        (total_score, breakdown_dict)
    """
    breakdown = {}

    # Population density (0-25 points)
    if tod.population_density_per_ha < 50:
        pop_score = 2.5
    elif tod.population_density_per_ha < 150:
        pop_score = 10.5
    elif tod.population_density_per_ha < 300:
        pop_score = 18
    else:
        pop_score = 23
    breakdown['population_density'] = pop_score

    # Employment density (0-25 points)
    if tod.employment_density_per_ha < 20:
        emp_score = 2.5
    elif tod.employment_density_per_ha < 75:
        emp_score = 10.5
    elif tod.employment_density_per_ha < 150:
        emp_score = 18
    else:
        emp_score = 23
    breakdown['employment_density'] = emp_score

    # Land use mix (0-20 points)
    use_mix_map = {1: 2.5, 2: 8, 3: 15.5}
    use_mix_score = use_mix_map.get(min(tod.number_of_uses, 3), 15.5)

    # Jobs-housing balance
    ratio = tod.jobs_housing_ratio
    if (0.75 <= ratio <= 1.5):
        balance_score = 8
    else:
        balance_score = 2.5
    breakdown['land_use_mix'] = use_mix_score + balance_score

    # Walkability (0-20 points)
    # Sidewalk coverage
    if tod.sidewalk_coverage_pct < 50:
        sidewalk_score = 2.5
    elif tod.sidewalk_coverage_pct < 80:
        sidewalk_score = 8
    else:
        sidewalk_score = 13

    # Crossings
    crossing_map = {"poor": 1, "adequate": 3.5, "excellent": 5}
    crossing_score = crossing_map.get(tod.crossings_quality, 3.5)

    # Intersection density
    if tod.intersection_density_per_km2 < 80:
        intersection_score = 1.5
    elif tod.intersection_density_per_km2 < 120:
        intersection_score = 5
    else:
        intersection_score = 8.5
    breakdown['walkability'] = sidewalk_score + crossing_score + intersection_score

    # Development potential (0-35 points)
    if tod.underutilized_land_pct < 10:
        land_score = 5
    elif tod.underutilized_land_pct < 30:
        land_score = 15.5
    else:
        land_score = 25.5

    zoning_map = {"restrictive": 1, "moderate": 3.5, "supportive": 5}
    zoning_score = zoning_map.get(tod.zoning_supportiveness, 3.5)
    breakdown['development_potential'] = land_score + zoning_score

    # Calculate raw total
    raw_total = sum(breakdown.values())

    # Normalize to 0-100 scale (max possible = 126.5)
    TOD_MAX = 126.5
    normalized_total = (raw_total / TOD_MAX) * 100

    # Normalize breakdown values proportionally
    normalized_breakdown = {k: (v / TOD_MAX) * 100 for k, v in breakdown.items()}

    return normalized_total, normalized_breakdown


def score_multi_modal(mm: MultiModalConnections) -> tuple[float, Dict[str, float]]:
    """
    Score multi-modal connections (0-100 points, higher is better)

    Returns:
        (total_score, breakdown_dict)
    """
    breakdown = {}

    # Bus integration (0-30 points)
    routes = mm.bus_routes_within_200m
    if routes <= 2:
        bus_routes_score = 2.5
    elif routes <= 5:
        bus_routes_score = 10.5
    elif routes <= 10:
        bus_routes_score = 20.5
    else:
        bus_routes_score = 28

    terminal_map = {"onsite": 5, "adjacent": 3, "remote": 0}
    terminal_score = terminal_map.get(mm.bus_terminal_location, 0)
    breakdown['bus_integration'] = bus_routes_score + terminal_score

    # Cycling (0-20 points)
    network_map = {"none": 0, "some": 7.5, "complete": 13}
    network_score = network_map.get(mm.bike_network_quality, 7.5)

    spaces = mm.bike_parking_spaces
    if spaces < 20:
        parking_score = 0
    elif spaces < 100:
        parking_score = 2
    elif spaces < 500:
        parking_score = 4
    else:
        parking_score = 5
    breakdown['cycling'] = network_score + parking_score

    # Pedestrian catchment (0-30 points)
    pop = mm.walkshed_population_800m
    if pop < 2000:
        ped_score = 2.5
    elif pop < 10000:
        ped_score = 10.5
    elif pop < 30000:
        ped_score = 20.5
    else:
        ped_score = 28
    breakdown['pedestrian_catchment'] = ped_score

    # Parking (0-20 points)
    kiss = mm.kiss_ride_spaces
    if kiss == 0:
        kiss_score = 0
    elif kiss < 20:
        kiss_score = 5
    elif kiss < 50:
        kiss_score = 10
    else:
        kiss_score = 15

    if mm.is_urban_station:
        park_score = 5  # Bonus for car-free focus
    elif mm.park_ride_spaces is None:
        park_score = 0
    else:
        if mm.park_ride_spaces < 200:
            park_score = 1.5
        elif mm.park_ride_spaces < 500:
            park_score = 6
        else:
            park_score = 12
    breakdown['parking'] = kiss_score + park_score

    # Calculate raw total
    raw_total = sum(breakdown.values())

    # Normalize to 0-100 scale (max possible = 95)
    # Max: Bus 33 (28+5) + Cycling 18 (13+5) + Pedestrian 28 + Parking 15 (or 20 with urban bonus) = 95
    MULTI_MODAL_MAX = 95.0
    normalized_total = (raw_total / MULTI_MODAL_MAX) * 100

    # Normalize breakdown values proportionally
    normalized_breakdown = {k: (v / MULTI_MODAL_MAX) * 100 for k, v in breakdown.items()}

    return normalized_total, normalized_breakdown


def score_acquisition_complexity(ac: AcquisitionComplexity) -> tuple[float, Dict[str, float]]:
    """
    Score acquisition complexity (0-100 points, LOWER is better)

    Returns:
        (total_score, breakdown_dict)
    """
    breakdown = {}

    # Ownership fragmentation (0-40 points)
    owners = ac.number_of_owners
    if owners <= 2:
        ownership_score = 2.5
    elif owners <= 5:
        ownership_score = 10.5
    elif owners <= 15:
        ownership_score = 23
    else:
        ownership_score = 35.5
    breakdown['ownership'] = ownership_score

    # Land use conflicts (0-30 points)
    # Residential displacement
    if ac.households_displaced == 0:
        res_score = 0
    elif ac.households_displaced < 10:
        res_score = 7.5
    elif ac.households_displaced < 50:
        res_score = 15.5
    else:
        res_score = 25.5

    # Business displacement
    if ac.businesses_displaced == 0:
        bus_score = 0
    elif ac.businesses_displaced < 5:
        bus_score = 5
    elif ac.businesses_displaced < 20:
        bus_score = 11.5
    else:
        bus_score = 20.5

    # Institutional impacts
    inst_score = ac.institutional_impacts * 10
    breakdown['land_use_conflicts'] = min(res_score + bus_score + inst_score, 30)

    # Environmental constraints (0-20 points)
    contam_map = {"minimal": 1, "moderate": 5.5, "severe": 12}
    contam_score = contam_map.get(ac.contamination_level, 5.5)
    wetland_score = ac.wetland_archaeological_count * 7
    breakdown['environmental'] = min(contam_score + wetland_score, 20)

    # Legal encumbrances (0-10 points)
    legal_score = (ac.easements_covenants_count * 3.5 +
                   ac.complex_tenancies_count * 5 +
                   ac.litigation_title_disputes * 7.5)
    breakdown['legal'] = min(legal_score, 10)

    total = sum(breakdown.values())
    return total, breakdown


def score_community_impact(ci: CommunityImpact) -> tuple[float, Dict[str, float]]:
    """
    Score community impact (0-100 points, LOWER is better)

    Returns:
        (total_score, breakdown_dict)
    """
    breakdown = {}

    # Direct displacement (0-40 points)
    households = ci.total_households_displaced
    if households == 0:
        base_score = 0
    elif households < 10:
        base_score = 10
    elif households < 50:
        base_score = 23
    else:
        base_score = 35.5

    # Vulnerable populations
    vulnerable_score = (
        (ci.low_income_households // 10) * 5 +
        (ci.senior_households // 10) * 3 +
        (ci.disability_households // 5) * 5
    )
    breakdown['direct_displacement'] = min(base_score + vulnerable_score, 40)

    # Gentrification risk (0-30 points)
    gentrif_map = {
        "high_income": 0,
        "middle_income": 7.5,
        "low_income": 20
    }
    gentrif_score = gentrif_map.get(ci.neighborhood_income_level, 7.5)

    if ci.existing_displacement_pressure:
        gentrif_score += 7.5
    breakdown['gentrification_risk'] = min(gentrif_score, 30)

    # Cultural/heritage significance (0-20 points)
    cultural_score = 0
    if ci.has_community_ties:
        cultural_score += 7.5
    cultural_score += ci.heritage_resources_count * 10
    breakdown['cultural_heritage'] = min(cultural_score, 20)

    # Community support (0-10 points)
    support_map = {"support": 0, "mixed": 5, "opposition": 10}
    breakdown['community_support'] = support_map.get(ci.community_support_level, 5)

    total = sum(breakdown.values())
    return total, breakdown


def score_holdout_risk(hr: HoldoutRisk) -> tuple[float, Dict[str, float]]:
    """
    Score holdout risk (0-30 points, LOWER is better)

    Returns:
        (total_score, breakdown_dict)
    """
    breakdown = {}

    # Owner motivation
    motiv_map = {"willing": 1, "neutral": 4, "reluctant": 7, "ideological": 9.5}
    breakdown['motivation'] = motiv_map.get(hr.owner_motivation, 4)

    # Owner sophistication
    soph_map = {
        "unsophisticated": 1,
        "moderate": 4,
        "sophisticated": 7,
        "serial_holdout": 9.5
    }
    breakdown['sophistication'] = soph_map.get(hr.owner_sophistication, 4)

    # Alternative options
    alt_map = {"strong": 1, "some": 4, "few": 7, "none": 9.5}
    breakdown['alternatives'] = alt_map.get(hr.owner_alternatives, 4)

    total = sum(breakdown.values())

    # Determine risk level
    if total <= 10:
        risk_level = "Low risk (likely to negotiate in good faith)"
    elif total <= 20:
        risk_level = "Moderate risk (may require mediation or premium)"
    else:
        risk_level = "High risk (likely holdout, plan for expropriation)"
    breakdown['risk_level'] = risk_level

    return total, breakdown


def calculate_composite_scores(tod, multi_modal, complexity, community, holdout) -> Dict[str, float]:
    """Calculate composite scores from individual categories"""
    # Desirability: average of TOD and Multi-Modal (both 0-100, higher is better)
    desirability = (tod + multi_modal) / 2

    # Feasibility: inverse of average complexity and community impact
    # (both 0-100, LOWER is better, so we invert)
    feasibility = 100 - ((complexity + community) / 2)

    # Overall score: weighted average
    # Desirability: 40%, Feasibility: 40%, Holdout: 20% (inverted)
    # Holdout is 0-30, so normalize to 0-100 and invert
    holdout_normalized = 100 - (holdout * 100 / 30)
    overall = (desirability * 0.4 + feasibility * 0.4 + holdout_normalized * 0.2)

    return {
        'desirability': round(desirability, 1),
        'feasibility': round(feasibility, 1),
        'overall': round(overall, 1)
    }


def generate_recommendation(summary: SiteScoreSummary) -> tuple[str, List[str], List[str]]:
    """
    Generate recommendation and key findings

    Returns:
        (recommendation, strengths, challenges)
    """
    strengths = []
    challenges = []

    # Analyze TOD score
    if summary.tod_score >= 80:
        strengths.append(f"Excellent TOD potential ({summary.tod_score:.0f}/100)")
    elif summary.tod_score < 50:
        challenges.append(f"Limited TOD potential ({summary.tod_score:.0f}/100)")

    # Analyze multi-modal
    if summary.multi_modal_score >= 70:
        strengths.append(f"Strong multi-modal connections ({summary.multi_modal_score:.0f}/100)")
    elif summary.multi_modal_score < 40:
        challenges.append(f"Weak multi-modal connections ({summary.multi_modal_score:.0f}/100)")

    # Analyze complexity (lower is better)
    if summary.complexity_score <= 30:
        strengths.append(f"Low acquisition complexity ({summary.complexity_score:.0f}/100)")
    elif summary.complexity_score > 60:
        challenges.append(f"High acquisition complexity ({summary.complexity_score:.0f}/100)")

    # Analyze community impact (lower is better)
    if summary.community_impact_score <= 20:
        strengths.append(f"Minimal community impact ({summary.community_impact_score:.0f}/100)")
    elif summary.community_impact_score > 50:
        challenges.append(f"Significant community impact ({summary.community_impact_score:.0f}/100)")

    # Analyze holdout risk (lower is better)
    if summary.holdout_risk_score <= 10:
        strengths.append(f"Low holdout risk ({summary.holdout_risk_score:.0f}/30)")
    elif summary.holdout_risk_score > 20:
        challenges.append(f"High holdout risk ({summary.holdout_risk_score:.0f}/30)")

    # Overall recommendation
    if summary.overall_score >= 75:
        recommendation = "HIGHLY RECOMMENDED - Strong overall performance"
    elif summary.overall_score >= 60:
        recommendation = "RECOMMENDED - Good balance of benefits and feasibility"
    elif summary.overall_score >= 45:
        recommendation = "CONSIDER WITH CAUTION - Moderate challenges present"
    else:
        recommendation = "NOT RECOMMENDED - Significant obstacles"

    return recommendation, strengths, challenges


# ==============================================================================
# MAIN SCORING FUNCTION
# ==============================================================================

def score_transit_site(
    site_id: SiteIdentification,
    tod: TODCharacteristics,
    multi_modal: MultiModalConnections,
    complexity: AcquisitionComplexity,
    community: CommunityImpact,
    holdout: HoldoutRisk
) -> SiteScoreSummary:
    """
    Calculate complete scoring for a transit station site

    Returns:
        SiteScoreSummary with all scores and recommendations
    """
    # Score each category
    tod_score, tod_breakdown = score_tod_potential(tod)
    mm_score, mm_breakdown = score_multi_modal(multi_modal)
    comp_score, comp_breakdown = score_acquisition_complexity(complexity)
    comm_score, comm_breakdown = score_community_impact(community)
    hold_score, hold_breakdown = score_holdout_risk(holdout)

    # Calculate composite scores
    composite = calculate_composite_scores(
        tod_score, mm_score, comp_score, comm_score, hold_score
    )

    # Create summary
    summary = SiteScoreSummary(
        site_id=site_id.site_id,
        site_name=site_id.site_name,
        tod_score=round(tod_score, 1),
        tod_breakdown=tod_breakdown,
        multi_modal_score=round(mm_score, 1),
        multi_modal_breakdown=mm_breakdown,
        complexity_score=round(comp_score, 1),
        complexity_breakdown=comp_breakdown,
        community_impact_score=round(comm_score, 1),
        community_impact_breakdown=comm_breakdown,
        holdout_risk_score=round(hold_score, 1),
        holdout_risk_breakdown=hold_breakdown,
        desirability_score=composite['desirability'],
        feasibility_score=composite['feasibility'],
        overall_score=composite['overall'],
        recommendation="",
        key_strengths=[],
        key_challenges=[]
    )

    # Generate recommendation
    recommendation, strengths, challenges = generate_recommendation(summary)
    summary.recommendation = recommendation
    summary.key_strengths = strengths
    summary.key_challenges = challenges

    return summary


# ==============================================================================
# JSON I/O
# ==============================================================================

def load_site_from_json(json_path: str) -> tuple:
    """Load site data from JSON file"""
    with open(json_path, 'r') as f:
        data = json.load(f)

    site_id = SiteIdentification(**data['site_identification'])
    tod = TODCharacteristics(**data['tod_characteristics'])
    multi_modal = MultiModalConnections(**data['multi_modal_connections'])
    complexity = AcquisitionComplexity(**data['acquisition_complexity'])
    community = CommunityImpact(**data['community_impact'])
    holdout = HoldoutRisk(**data['holdout_risk'])

    return site_id, tod, multi_modal, complexity, community, holdout


def save_results_to_json(summary: SiteScoreSummary, output_path: str):
    """Save scoring results to JSON file"""
    with open(output_path, 'w') as f:
        json.dump(asdict(summary), f, indent=2)


# ==============================================================================
# COMMAND-LINE INTERFACE
# ==============================================================================

def main():
    """Command-line interface for transit station site scoring"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Transit Station Site Scoring Calculator'
    )
    parser.add_argument(
        'input_json',
        help='Path to site input JSON file'
    )
    parser.add_argument(
        '--output',
        help='Path to output JSON file (default: auto-generated)',
        default=None
    )

    args = parser.parse_args()

    # Load site data
    print(f"Loading site data from {args.input_json}...")
    site_id, tod, mm, complexity, community, holdout = load_site_from_json(args.input_json)
    print(f"  ✓ Loaded site: {site_id.site_name}\n")

    # Score site
    print("Calculating scores...")
    summary = score_transit_site(site_id, tod, mm, complexity, community, holdout)

    # Generate output filename if not provided
    if args.output is None:
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        args.output = f'{site_id.site_id}_scoring_results_{timestamp}.json'

    # Save results
    save_results_to_json(summary, args.output)
    print(f"  ✓ Results saved to {args.output}\n")

    # Print summary
    print("=" * 80)
    print(f"TRANSIT STATION SITE SCORING: {summary.site_name}")
    print("=" * 80)
    print()

    print("SCORING RESULTS:")
    print("-" * 80)
    print(f"TOD Potential:              {summary.tod_score:6.1f}/100  (higher is better)")
    print(f"Multi-Modal Connections:    {summary.multi_modal_score:6.1f}/100  (higher is better)")
    print(f"Acquisition Complexity:     {summary.complexity_score:6.1f}/100  (LOWER is better)")
    print(f"Community Impact:           {summary.community_impact_score:6.1f}/100  (LOWER is better)")
    print(f"Holdout Risk:               {summary.holdout_risk_score:6.1f}/30   (LOWER is better)")
    print()

    print("COMPOSITE SCORES:")
    print("-" * 80)
    print(f"Desirability Score:         {summary.desirability_score:6.1f}/100")
    print(f"Feasibility Score:          {summary.feasibility_score:6.1f}/100")
    print(f"OVERALL SCORE:              {summary.overall_score:6.1f}/100")
    print()

    print("RECOMMENDATION:")
    print("-" * 80)
    print(f"{summary.recommendation}")
    print()

    if summary.key_strengths:
        print("Key Strengths:")
        for strength in summary.key_strengths:
            print(f"  ✓ {strength}")
        print()

    if summary.key_challenges:
        print("Key Challenges:")
        for challenge in summary.key_challenges:
            print(f"  ⚠ {challenge}")
        print()

    print("=" * 80)
    print(f"\n✓ Assessment complete. Detailed results saved to {args.output}")


if __name__ == '__main__':
    main()
