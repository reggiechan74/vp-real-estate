"""
Scoring criteria and thresholds for transit station site evaluation

Based on Transit-Oriented Development (TOD) principles and transit planning best practices.
All scoring thresholds documented in transit-station-site-acquisition-strategy SKILL.md
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class ScoringCriteria:
    """All scoring thresholds and criteria for transit station site evaluation"""

    # =========================================================================
    # TOD POTENTIAL SCORING (0-100 points, higher is better)
    # =========================================================================

    # Population density thresholds (people/hectare → points)
    POPULATION_DENSITY_THRESHOLDS: List[Tuple[float, float, float]] = (
        (0, 50, (0, 5)),       # <50: 0-5 points (low)
        (50, 150, (6, 15)),    # 50-150: 6-15 points (medium)
        (150, 300, (16, 20)),  # 150-300: 16-20 points (high)
        (300, float('inf'), (21, 25))  # >300: 21-25 points (very high)
    )

    # Employment density thresholds (jobs/hectare → points)
    EMPLOYMENT_DENSITY_THRESHOLDS: List[Tuple[float, float, float]] = (
        (0, 20, (0, 5)),
        (20, 75, (6, 15)),
        (75, 150, (16, 20)),
        (150, float('inf'), (21, 25))
    )

    # Land use mix scoring
    LAND_USE_MIX_POINTS: Dict[int, Tuple[int, int]] = {
        1: (0, 5),      # Single-use
        2: (6, 10),     # Two uses
        3: (11, 20)     # Three+ uses
    }

    # Jobs-housing balance ratio scoring
    JOBS_HOUSING_BALANCE_GOOD: Tuple[float, float] = (0.75, 1.5)  # Balanced ratio range
    JOBS_HOUSING_BALANCE_POINTS_GOOD: Tuple[int, int] = (6, 10)
    JOBS_HOUSING_BALANCE_POINTS_POOR: Tuple[int, int] = (0, 5)

    # Walkability - sidewalk coverage
    SIDEWALK_COVERAGE_THRESHOLDS: List[Tuple[float, Tuple[int, int]]] = [
        (50, (0, 5)),      # <50%
        (80, (6, 10)),     # 50-80%
        (100, (11, 15))    # >80%
    ]

    # Intersection density (intersections/km²)
    INTERSECTION_DENSITY_THRESHOLDS: List[Tuple[float, Tuple[int, int]]] = [
        (80, (0, 3)),
        (120, (4, 6)),
        (float('inf'), (7, 10))
    ]

    # Development potential - underutilized land percentage
    UNDERUTILIZED_LAND_THRESHOLDS: List[Tuple[float, Tuple[int, int]]] = [
        (10, (0, 10)),     # <10%
        (30, (11, 20)),    # 10-30%
        (100, (21, 30))    # >30%
    ]

    # Zoning supportiveness
    ZONING_POINTS: Dict[str, int] = {
        'restrictive': 2,      # Low-density residential
        'moderate': 4,         # Mid-rise mixed-use permitted
        'supportive': 5        # High-density mixed-use as-of-right
    }

    # =========================================================================
    # MULTI-MODAL CONNECTIONS SCORING (0-100 points, higher is better)
    # =========================================================================

    # Bus route integration (number of routes within 200m)
    BUS_ROUTES_THRESHOLDS: List[Tuple[int, Tuple[int, int]]] = [
        (2, (0, 5)),
        (5, (6, 15)),
        (10, (16, 25)),
        (999, (26, 30))
    ]

    # Bus terminal feasibility
    BUS_TERMINAL_POINTS: Dict[str, int] = {
        'onsite': 5,
        'adjacent': 3,
        'remote': 0
    }

    # Cycling infrastructure
    BIKE_NETWORK_POINTS: Dict[str, Tuple[int, int]] = {
        'none': (0, 0),
        'some': (5, 10),
        'complete': (11, 15)
    }

    # Bike parking capacity
    BIKE_PARKING_THRESHOLDS: List[Tuple[int, int]] = [
        (20, 0),
        (100, 2),
        (500, 4),
        (99999, 5)
    ]

    # Pedestrian catchment (800m walkshed population)
    WALKSHED_POPULATION_THRESHOLDS: List[Tuple[int, Tuple[int, int]]] = [
        (2000, (0, 5)),
        (10000, (6, 15)),
        (30000, (16, 25)),
        (999999, (26, 30))
    ]

    # Kiss-and-ride capacity
    KISS_RIDE_THRESHOLDS: List[Tuple[int, int]] = [
        (0, 0),
        (20, 5),
        (50, 10),
        (99999, 15)
    ]

    # Park-and-ride capacity (suburban stations)
    PARK_RIDE_THRESHOLDS: List[Tuple[int, Tuple[int, int]]] = [
        (200, (0, 3)),
        (500, (4, 8)),
        (99999, (9, 15))
    ]

    URBAN_STATION_BONUS: int = 5  # Bonus for car-free focus

    # =========================================================================
    # PROPERTY ACQUISITION COMPLEXITY (0-100 points, LOWER is better)
    # =========================================================================

    # Number of property owners
    OWNERSHIP_COMPLEXITY_THRESHOLDS: List[Tuple[int, Tuple[int, int]]] = [
        (2, (0, 5)),       # 1-2 owners: simple
        (5, (6, 15)),      # 3-5 owners: moderate
        (15, (16, 30)),    # 6-15 owners: complex
        (99999, (31, 40))  # >15 owners: very complex
    ]

    # Residential displacement
    RESIDENTIAL_DISPLACEMENT_THRESHOLDS: List[Tuple[int, Tuple[int, int]]] = [
        (0, (0, 0)),
        (10, (5, 10)),
        (50, (11, 20)),
        (99999, (21, 30))
    ]

    # Business displacement
    BUSINESS_DISPLACEMENT_THRESHOLDS: List[Tuple[int, Tuple[int, int]]] = [
        (0, (0, 0)),
        (5, (3, 7)),
        (20, (8, 15)),
        (99999, (16, 25))
    ]

    # Institutional/heritage impacts
    INSTITUTIONAL_IMPACT_POINTS: int = 10  # Per institution

    # Environmental contamination
    CONTAMINATION_POINTS: Dict[str, Tuple[int, int]] = {
        'minimal': (0, 2),
        'moderate': (3, 8),      # Phase II required
        'severe': (9, 15)        # Remediation >$1M
    }

    # Wetlands/archaeological
    ENVIRONMENTAL_CONSTRAINT_POINTS: int = 7  # Average 5-10 points

    # Legal encumbrances
    EASEMENT_POINTS: Tuple[int, int] = (2, 5)
    TENANCY_POINTS: Tuple[int, int] = (3, 7)
    LITIGATION_POINTS: Tuple[int, int] = (5, 10)

    # =========================================================================
    # COMMUNITY IMPACT SCORING (0-100 points, LOWER is better)
    # =========================================================================

    # Direct displacement - households
    HOUSEHOLD_DISPLACEMENT_THRESHOLDS: List[Tuple[int, Tuple[int, int]]] = [
        (0, (0, 0)),
        (10, (5, 15)),
        (50, (16, 30)),
        (99999, (31, 40))
    ]

    # Vulnerable population multipliers (additional points)
    LOW_INCOME_POINTS_PER_10: int = 5
    SENIORS_POINTS_PER_10: int = 3
    DISABILITIES_POINTS_PER_5: int = 5

    # Gentrification risk
    GENTRIFICATION_RISK_POINTS: Dict[str, Tuple[int, int]] = {
        'high_income': (0, 0),         # Low gentrification risk
        'middle_income': (5, 10),      # Moderate risk
        'low_income': (15, 25)         # High risk
    }

    # Existing displacement pressure
    DISPLACEMENT_PRESSURE_POINTS: Tuple[int, int] = (5, 10)

    # Cultural/heritage significance
    COMMUNITY_TIES_POINTS: Tuple[int, int] = (5, 10)
    HERITAGE_RESOURCES_POINTS: Tuple[int, int] = (5, 15)

    # Community support/opposition
    COMMUNITY_SUPPORT_POINTS: Dict[str, int] = {
        'support': 0,
        'mixed': 5,
        'opposition': 10
    }

    # =========================================================================
    # HOLDOUT RISK ASSESSMENT (0-30 points, LOWER is better)
    # =========================================================================

    # Owner motivation
    MOTIVATION_POINTS: Dict[str, Tuple[int, int]] = {
        'willing': (0, 2),
        'neutral': (3, 5),
        'reluctant': (6, 8),
        'ideological': (9, 10)
    }

    # Owner sophistication
    SOPHISTICATION_POINTS: Dict[str, Tuple[int, int]] = {
        'unsophisticated': (0, 2),
        'moderate': (3, 5),
        'sophisticated': (6, 8),
        'serial_holdout': (9, 10)
    }

    # Alternative options
    ALTERNATIVES_POINTS: Dict[str, Tuple[int, int]] = {
        'strong': (0, 2),
        'some': (3, 5),
        'few': (6, 8),
        'none': (9, 10)
    }

    # Holdout risk interpretation
    HOLDOUT_RISK_LEVELS: Dict[str, Tuple[int, int]] = {
        'low': (0, 10),
        'moderate': (11, 20),
        'high': (21, 30)
    }


# Global instance
SCORING_CRITERIA = ScoringCriteria()
