#!/usr/bin/env python3
"""
Relative Valuation Calculator - Multi-Criteria Competitive Positioning Analysis

This module implements a weighted ranking system to determine a subject property's
competitive position within its market comparable set. The methodology ranks properties
from 1 (best) to X (worst) across 9 key variables, then calculates weighted scores
to identify which properties offer the best value proposition to tenants.

Usage:
    python relative_valuation_calculator.py --input data.json --output report.md
    python relative_valuation_calculator.py --input data.json --output-json results.json
    python relative_valuation_calculator.py --interactive

Author: Claude Code
Date: November 5, 2025
Version: 1.0.0 (Phase 1 - MVP)
"""

import json
import argparse
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List, Dict, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import sys


@dataclass
class Property:
    """Represents a commercial property in the competitive analysis."""
    address: str
    unit: str
    year_built: int
    clear_height_ft: float
    pct_office_space: float
    parking_ratio: float
    available_sf: float
    net_asking_rent: float
    tmi: float
    class_: int  # 1=A, 2=B, 3=C
    distance_km: float
    area_difference: float = 0.0  # Calculated dynamically
    is_subject: bool = False
    landlord: str = ""

    # Additional property details (used in ranking if available)
    shipping_doors_tl: int = 0  # Truck-level doors
    shipping_doors_di: int = 0  # Drive-in doors
    availability_date: str = ""
    power_amps: int = 0
    trailer_parking: bool = False
    secure_shipping: bool = False
    excess_land: bool = False

    # New optional fields (Phase 2 enhancements - Batch 1)
    bay_depth_ft: float = 0.0  # Bay depth from Bay Size field
    lot_size_acres: float = 0.0  # Lot size in acres
    hvac_coverage: int = 3  # Ordinal: Y=1, Part=2, N=3
    sprinkler_type: int = 3  # Ordinal: ESFR=1, Standard=2, None=3
    building_age_years: int = 0  # Calculated: analysis_year - year_built
    rail_access: bool = False  # Rail siding availability
    crane: bool = False  # Overhead crane capability
    occupancy_status: int = 2  # Ordinal: Vacant=1, Tenant=2

    # Phase 2 enhancements - Batch 2
    grade_level_doors: int = 0  # Grade-level doors (courier/small truck access)
    days_on_market: int = 0  # Days on market (landlord motivation)
    zoning: str = ""  # Zoning classification

    # Ranking results
    rank_year_built: int = 0
    rank_clear_height: int = 0
    rank_pct_office: int = 0
    rank_parking: int = 0
    rank_distance: int = 0
    rank_net_rent: int = 0
    rank_tmi: int = 0
    rank_class: int = 0
    rank_area_diff: int = 0
    rank_shipping_doors_tl: int = 0
    rank_shipping_doors_di: int = 0
    rank_power: int = 0
    rank_trailer_parking: int = 0
    rank_secure_shipping: int = 0
    rank_excess_land: int = 0
    rank_bay_depth: int = 0
    rank_lot_size: int = 0
    rank_hvac_coverage: int = 0
    rank_sprinkler_type: int = 0
    rank_building_age: int = 0
    rank_rail_access: int = 0
    rank_crane: int = 0
    rank_occupancy_status: int = 0
    rank_grade_level_doors: int = 0
    rank_days_on_market: int = 0
    rank_zoning: int = 0

    weighted_score: float = 0.0
    final_rank: int = 0


@dataclass
class CompetitiveAnalysis:
    """Results of competitive positioning analysis."""
    analysis_date: str
    market: str
    total_properties: int
    subject_property: Dict[str, Any]
    top_competitors: List[Dict[str, Any]]
    gap_analysis: Dict[str, Any]
    sensitivity_scenarios: List[Dict[str, Any]]
    all_properties: List[Dict[str, Any]]
    weights_used: Dict[str, float]  # Actual weights used in analysis


def load_comparable_data(json_path: str) -> Dict[str, Any]:
    """
    Load comparable data from JSON file.

    Automatically loads default weights if not provided in the input JSON.

    Args:
        json_path: Path to JSON file containing comparable data

    Returns:
        Dictionary with analysis_date, market, subject_property, comparables, weights

    Raises:
        FileNotFoundError: If JSON file doesn't exist
        json.JSONDecodeError: If JSON is malformed
    """
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)

        # Validate required fields (except weights - will be auto-loaded if missing)
        required_fields = ['analysis_date', 'market', 'subject_property', 'comparables']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # AUTO-LOAD DEFAULT WEIGHTS IF MISSING
        if 'weights' not in data or not data['weights']:
            print("[INFO] No weights specified in input JSON - loading default persona weights")
            data['weights'] = get_tenant_persona_weights(persona="default")

        return data

    except FileNotFoundError:
        print(f"Error: File not found: {json_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {json_path}: {e}")
        sys.exit(1)


def calculate_area_differences(properties: List[Dict[str, Any]], subject_sf: float) -> List[Dict[str, Any]]:
    """
    Calculate absolute difference in area between each property and subject.

    If area_difference is already present in the property data, it will be used as-is.
    This allows for pre-calculated area differences (e.g., from Excel template).

    Args:
        properties: List of property dictionaries
        subject_sf: Square footage of subject property

    Returns:
        List of properties with area_difference field added (if not already present)
    """
    for prop in properties:
        # Only calculate if not already provided
        if 'area_difference' not in prop or prop['area_difference'] is None:
            prop['area_difference'] = abs(prop['available_sf'] - subject_sf)

    return properties


def rank_variable(values: List[float], ascending: bool = True) -> List[int]:
    """
    Rank values from 1 (best) to X (worst), handling ties with minimum rank.

    Uses "competition ranking" (1-2-2-4 method) where tied values receive
    the same rank equal to the minimum position. Matches Excel RANK function.

    Args:
        values: List of numeric values to rank
        ascending: True if lower value = better rank (e.g., rent, distance)
                   False if higher value = better rank (e.g., parking, clear height)

    Returns:
        List of ranks (1 to len(values)), matching input order

    Example:
        values = [10.0, 8.5, 9.0, 8.5]
        ascending = True
        returns = [4, 1, 3, 1]  # Ties get minimum rank
    """
    n = len(values)

    # Create list of (value, original_index) tuples
    indexed_values = [(val, idx) for idx, val in enumerate(values)]

    # Sort by value (ascending or descending based on parameter)
    indexed_values.sort(key=lambda x: x[0], reverse=not ascending)

    # Assign ranks, handling ties with minimum rank (competition ranking)
    # This matches Excel's RANK function behavior
    ranks = [0] * n
    i = 0
    while i < n:
        # Find all values tied with current value
        current_value = indexed_values[i][0]
        j = i
        while j < n and indexed_values[j][0] == current_value:
            j += 1

        # All tied values get the minimum rank (first position)
        # This is the "competition ranking" or "1224" method
        min_rank = i + 1

        for k in range(i, j):
            ranks[indexed_values[k][1]] = min_rank

        i = j

    return ranks


def detect_available_variables(properties: List[Dict[str, Any]]) -> Dict[str, bool]:
    """
    Detect which optional variables have data across the property set.

    A variable is considered "available" if:
    - For numeric fields: at least 50% of properties have non-zero values
    - For boolean fields: at least one property has True
    - For string fields: at least 50% have non-empty strings

    Args:
        properties: List of property dictionaries

    Returns:
        Dictionary mapping variable names to availability (True/False)
    """
    total = len(properties)
    threshold = total * 0.5  # 50% threshold

    # Core variables (always included)
    available = {
        'building_age_years': True,  # Replaces year_built - more intuitive
        'clear_height_ft': True,
        'pct_office_space': True,
        'parking_ratio': True,
        'distance_km': True,
        'net_asking_rent': True,
        'tmi': True,
        'class': True,
        'area_difference': True
    }

    # Optional variables (existing) - check if data is available
    # Shipping doors TL
    tl_count = sum(1 for p in properties if p.get('shipping_doors_tl', 0) > 0)
    available['shipping_doors_tl'] = tl_count >= threshold

    # Shipping doors DI
    di_count = sum(1 for p in properties if p.get('shipping_doors_di', 0) > 0)
    available['shipping_doors_di'] = di_count >= threshold

    # Power
    power_count = sum(1 for p in properties if p.get('power_amps', 0) > 0)
    available['power_amps'] = power_count >= threshold

    # Trailer parking (boolean)
    trailer_count = sum(1 for p in properties if p.get('trailer_parking', False))
    available['trailer_parking'] = trailer_count > 0

    # Secure shipping (boolean)
    secure_count = sum(1 for p in properties if p.get('secure_shipping', False))
    available['secure_shipping'] = secure_count > 0

    # Excess land (boolean)
    excess_count = sum(1 for p in properties if p.get('excess_land', False))
    available['excess_land'] = excess_count > 0

    # Optional variables (new) - Phase 2 enhancements
    # Bay depth
    bay_count = sum(1 for p in properties if p.get('bay_depth_ft', 0) > 0)
    available['bay_depth_ft'] = bay_count >= threshold

    # Lot size
    lot_count = sum(1 for p in properties if p.get('lot_size_acres', 0) > 0)
    available['lot_size_acres'] = lot_count >= threshold

    # HVAC coverage (ordinal - always include if at least 50% have non-default values)
    hvac_count = sum(1 for p in properties if p.get('hvac_coverage', 3) < 3)
    available['hvac_coverage'] = hvac_count >= threshold

    # Sprinkler type (ordinal - always include if at least 50% have non-default values)
    sprinkler_count = sum(1 for p in properties if p.get('sprinkler_type', 3) < 3)
    available['sprinkler_type'] = sprinkler_count >= threshold

    # Rail access (boolean)
    rail_count = sum(1 for p in properties if p.get('rail_access', False))
    available['rail_access'] = rail_count > 0

    # Crane (boolean)
    crane_count = sum(1 for p in properties if p.get('crane', False))
    available['crane'] = crane_count > 0

    # Occupancy status (ordinal - always include if at least 50% have non-default values)
    occupancy_count = sum(1 for p in properties if p.get('occupancy_status', 2) < 2)
    available['occupancy_status'] = occupancy_count >= threshold

    # Phase 2 fields - Batch 2
    # Grade level doors
    grade_level_count = sum(1 for p in properties if p.get('grade_level_doors', 0) > 0)
    available['grade_level_doors'] = grade_level_count >= threshold

    # Days on market
    dom_count = sum(1 for p in properties if p.get('days_on_market', 0) > 0)
    available['days_on_market'] = dom_count >= threshold

    # Zoning (string - available if at least 50% have non-empty values)
    zoning_count = sum(1 for p in properties if p.get('zoning', '').strip())
    available['zoning'] = zoning_count >= threshold

    return available


def get_tenant_persona_weights(persona: str = "default",
                               config_path: Optional[str] = None) -> Dict[str, float]:
    """
    Get weight profiles tailored to specific tenant personas.

    Now loads from weights_config.json. Falls back to hardcoded defaults
    if config file unavailable.

    Args:
        persona: Tenant type - "default", "3pl", "manufacturing", "office"
        config_path: Optional path to custom weights configuration file

    Returns:
        Dictionary of variable weights optimized for the tenant persona
    """
    # Try loading from external config (package-relative first, then absolute)
    get_weights = None
    import_error: Optional[Exception] = None

    try:
        from .weights_loader import get_persona_weights as get_weights  # type: ignore
    except ImportError as exc:
        try:
            from weights_loader import get_persona_weights as get_weights  # type: ignore
        except ImportError as exc_abs:
            import_error = exc_abs
        else:
            import_error = exc
    else:
        import_error = None

    if get_weights:
        try:
            weights = get_weights(persona, config_path)
            print(f"[INFO] Loaded persona '{persona}' from weights_config.json")
            return weights
        except Exception as e:
            print(f"[WARNING] Could not load weights config: {e}")
    else:
        detail = f" ({import_error})" if import_error else ""
        print(f"[WARNING] weights_loader module not found{detail}")

    # Fallback to hardcoded defaults
    print("[INFO] Using hardcoded default weights")
    # Default/balanced weights (25 variables)
    default_weights = {
        # Core variables
        'net_asking_rent': 0.11,
        'parking_ratio': 0.09,
        'tmi': 0.09,
        'clear_height_ft': 0.07,
        'pct_office_space': 0.06,
        'distance_km': 0.07,
        'area_difference': 0.07,
        'building_age_years': 0.04,
        'class': 0.05,
        # Optional variables
        'shipping_doors_tl': 0.04,
        'shipping_doors_di': 0.03,
        'power_amps': 0.03,
        'trailer_parking': 0.02,
        'secure_shipping': 0.00,
        'excess_land': 0.00,
        'bay_depth_ft': 0.04,
        'lot_size_acres': 0.03,
        'hvac_coverage': 0.03,
        'sprinkler_type': 0.03,
        'rail_access': 0.02,
        'crane': 0.02,
        'occupancy_status': 0.00,
        'grade_level_doors': 0.02,
        'days_on_market': 0.02,
        'zoning': 0.02
    }

    # 3PL/Distribution tenant profile
    # Emphasizes: Bay depth, clear height, shipping doors, trailer parking
    # De-emphasizes: Office space, class, HVAC
    threepl_weights = {
        'net_asking_rent': 0.12,
        'parking_ratio': 0.08,
        'tmi': 0.09,
        'clear_height_ft': 0.10,  # +3%
        'pct_office_space': 0.02,  # -4%
        'distance_km': 0.08,
        'area_difference': 0.07,
        'building_age_years': 0.03,
        'class': 0.02,  # -3%
        'shipping_doors_tl': 0.06,  # +2%
        'shipping_doors_di': 0.04,  # +1%
        'power_amps': 0.02,
        'trailer_parking': 0.04,  # +2%
        'secure_shipping': 0.00,
        'excess_land': 0.00,
        'bay_depth_ft': 0.07,  # +3%
        'lot_size_acres': 0.04,
        'hvac_coverage': 0.01,  # -2%
        'sprinkler_type': 0.04,  # +1%
        'rail_access': 0.01,
        'crane': 0.01,
        'occupancy_status': 0.00,
        'grade_level_doors': 0.01,
        'days_on_market': 0.02,
        'zoning': 0.02
    }

    # Manufacturing tenant profile
    # Emphasizes: Clear height, power, crane, rail access, bay depth
    # De-emphasizes: Office space, class, distance
    manufacturing_weights = {
        'net_asking_rent': 0.09,
        'parking_ratio': 0.08,
        'tmi': 0.08,
        'clear_height_ft': 0.09,  # +2%
        'pct_office_space': 0.03,  # -3%
        'distance_km': 0.04,  # -3%
        'area_difference': 0.07,
        'building_age_years': 0.05,
        'class': 0.03,  # -2%
        'shipping_doors_tl': 0.05,  # +1%
        'shipping_doors_di': 0.03,
        'power_amps': 0.05,  # +2%
        'trailer_parking': 0.02,
        'secure_shipping': 0.00,
        'excess_land': 0.00,
        'bay_depth_ft': 0.06,  # +2%
        'lot_size_acres': 0.04,
        'hvac_coverage': 0.02,  # -1%
        'sprinkler_type': 0.03,
        'rail_access': 0.04,  # +2%
        'crane': 0.05,  # +3%
        'occupancy_status': 0.00,
        'grade_level_doors': 0.01,
        'days_on_market': 0.02,
        'zoning': 0.02
    }

    # Office tenant profile
    # Emphasizes: Office space, class, HVAC, distance, parking
    # De-emphasizes: Clear height, bay depth, shipping doors, crane, rail
    office_weights = {
        'net_asking_rent': 0.13,  # +2%
        'parking_ratio': 0.12,  # +3%
        'tmi': 0.10,  # +1%
        'clear_height_ft': 0.02,  # -5%
        'pct_office_space': 0.12,  # +6%
        'distance_km': 0.10,  # +3%
        'area_difference': 0.08,
        'building_age_years': 0.05,
        'class': 0.08,  # +3%
        'shipping_doors_tl': 0.01,  # -3%
        'shipping_doors_di': 0.01,  # -2%
        'power_amps': 0.02,
        'trailer_parking': 0.00,  # -2%
        'secure_shipping': 0.00,
        'excess_land': 0.00,
        'bay_depth_ft': 0.00,  # -4%
        'lot_size_acres': 0.02,
        'hvac_coverage': 0.06,  # +3%
        'sprinkler_type': 0.02,  # -1%
        'rail_access': 0.00,  # -2%
        'crane': 0.00,  # -2%
        'occupancy_status': 0.00,
        'grade_level_doors': 0.02,
        'days_on_market': 0.02,
        'zoning': 0.02
    }

    personas = {
        "default": default_weights,
        "3pl": threepl_weights,
        "manufacturing": manufacturing_weights,
        "office": office_weights
    }

    return personas.get(persona.lower(), default_weights)


def allocate_dynamic_weights(available_vars: Dict[str, bool],
                            base_weights: Dict[str, float]) -> Dict[str, float]:
    """
    Dynamically allocate weights based on which variables have data.

    Base weight allocation (when all optional vars available):
    - Net Rent: 14%
    - Parking: 13%
    - TMI: 12%
    - Clear Height: 9%
    - % Office: 9%
    - Distance: 9%
    - Area Diff: 9%
    - Year Built: 7%
    - Class: 6%
    - Shipping TL: 4%
    - Shipping DI: 3%
    - Power: 3%
    - Trailer Parking: 2%
    - Secure Shipping: 2%
    - Excess Land: 2%
    Total: 100%

    If optional variables are missing, their weights are redistributed
    proportionally among available variables.

    Args:
        available_vars: Dictionary of variable availability
        base_weights: Base weights from input (may be overridden)

    Returns:
        Adjusted weights that sum to 1.0
    """
    # Define default weights when no custom schema provided (25 variables total)
    # Core variables (9): 65% total
    # Existing optional (6): 12% total
    # Phase 1 optional (7): 17% total
    # Phase 2 optional (3): 6% total
    default_weights = {
        # Core variables (65%)
        'net_asking_rent': 0.11,
        'parking_ratio': 0.09,
        'tmi': 0.09,
        'clear_height_ft': 0.07,
        'pct_office_space': 0.06,
        'distance_km': 0.07,
        'area_difference': 0.07,
        'building_age_years': 0.04,  # Replaces year_built
        'class': 0.05,
        # Existing optional variables (12%)
        'shipping_doors_tl': 0.04,
        'shipping_doors_di': 0.03,
        'power_amps': 0.03,
        'trailer_parking': 0.02,
        'secure_shipping': 0.00,  # No data in typical datasets
        'excess_land': 0.00,  # No data in typical datasets
        # Phase 1 optional variables (17%)
        'bay_depth_ft': 0.04,
        'lot_size_acres': 0.03,
        'hvac_coverage': 0.03,
        'sprinkler_type': 0.03,
        'rail_access': 0.02,
        'crane': 0.02,
        'occupancy_status': 0.00,  # Tracked for filtering
        # Phase 2 optional variables (6%)
        'grade_level_doors': 0.02,
        'days_on_market': 0.02,
        'zoning': 0.02
    }

    # Helper to normalise a provided weight mapping to sum to 1.0
    def normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
        clean_weights = {
            key: float(value)
            for key, value in weights.items()
            if value is not None
        }

        if not clean_weights:
            return {}

        # Detect percentage style inputs (e.g., 16 for 16%)
        if any(abs(val) > 1 for val in clean_weights.values()):
            clean_weights = {k: v / 100.0 for k, v in clean_weights.items()}

        total = sum(clean_weights.values())
        if total <= 0:
            return {}

        return {k: v / total for k, v in clean_weights.items()}

    # Establish baseline weights: either custom (normalised) or defaults
    normalized_custom = normalize_weights(base_weights or {})
    if normalized_custom:
        baseline_weights = normalized_custom.copy()
        # Ensure all known variables exist in baseline (default to 0 for unspecified)
        for var in default_weights:
            baseline_weights.setdefault(var, 0.0)
    else:
        baseline_weights = default_weights.copy()

    # Guarantee every available variable has an entry
    for var in available_vars:
        baseline_weights.setdefault(var, 0.0)

    # Normalise baseline to avoid drift when defaults are extended
    baseline_total = sum(baseline_weights.values())
    if baseline_total <= 0:
        # If everything zero, fall back to equal weighting among available vars
        available_count = sum(1 for is_avail in available_vars.values() if is_avail)
        if available_count == 0:
            return {}
        equal_weight = round(1.0 / available_count, 4)
        return {
            var: equal_weight
            for var, is_avail in available_vars.items()
            if is_avail
        }

    baseline_weights = {
        k: v / baseline_total
        for k, v in baseline_weights.items()
    }

    # Restrict to variables that are actually available
    available_weights = {
        var: baseline_weights.get(var, 0.0)
        for var, is_avail in available_vars.items()
        if is_avail
    }

    total_available = sum(available_weights.values())
    if total_available <= 0:
        num_available = len(available_weights)
        if num_available == 0:
            return {}
        equal_weight = round(1.0 / num_available, 4)
        return {var: equal_weight for var in available_weights}

    return {
        var: round(weight / total_available, 4)
        for var, weight in available_weights.items()
    }


def calculate_weighted_score(property_data: Dict[str, Any],
                              ranks: Dict[str, int],
                              weights: Dict[str, float]) -> float:
    """
    Calculate weighted score = Σ(rank × weight) for all variables.

    Lower weighted score = better competitive position (fewer negative rank points).

    Args:
        property_data: Property dictionary with all attributes
        ranks: Dictionary of variable ranks (e.g., {'year_built': 20, 'clear_height_ft': 44})
        weights: Dictionary of variable weights (e.g., {'year_built': 0.08, 'clear_height_ft': 0.10})

    Returns:
        Weighted score (float)

    Example:
        ranks = {'year_built': 54, 'clear_height_ft': 44, 'pct_office_space': 73,
                 'parking_ratio': 3, 'distance_km': 44, 'net_asking_rent': 7,
                 'tmi': 59, 'class': 15, 'area_difference': 68}
        weights = {'year_built': 0.08, 'clear_height_ft': 0.10, 'pct_office_space': 0.10,
                   'parking_ratio': 0.15, 'distance_km': 0.10, 'net_asking_rent': 0.16,
                   'tmi': 0.14, 'class': 0.07, 'area_difference': 0.10}

        Score = (54×0.08) + (44×0.10) + (73×0.10) + (3×0.15) + (44×0.10) +
                (7×0.16) + (59×0.14) + (15×0.07) + (68×0.10)
              = 4.32 + 4.4 + 7.3 + 0.45 + 4.4 + 1.12 + 8.26 + 1.05 + 6.8
              = 38.10
    """
    score = 0.0

    # Variable name mapping from weights dict to ranks dict
    # Weights use shortened names, ranks use full field names from property
    variable_mapping = {
        'building_age_years': 'building_age_years',
        'clear_height_ft': 'clear_height_ft',
        'pct_office_space': 'pct_office_space',
        'parking_ratio': 'parking_ratio',
        'distance_km': 'distance_km',
        'net_asking_rent': 'net_asking_rent',
        'tmi': 'tmi',
        'class': 'class',
        'area_difference': 'area_difference',
        'shipping_doors_tl': 'shipping_doors_tl',
        'shipping_doors_di': 'shipping_doors_di',
        'power_amps': 'power_amps',
        'trailer_parking': 'trailer_parking',
        'secure_shipping': 'secure_shipping',
        'excess_land': 'excess_land',
        'bay_depth_ft': 'bay_depth_ft',
        'lot_size_acres': 'lot_size_acres',
        'hvac_coverage': 'hvac_coverage',
        'sprinkler_type': 'sprinkler_type',
        'rail_access': 'rail_access',
        'crane': 'crane',
        'occupancy_status': 'occupancy_status',
        'grade_level_doors': 'grade_level_doors',
        'days_on_market': 'days_on_market',
        'zoning': 'zoning'
    }

    for weight_key, rank_key in variable_mapping.items():
        if weight_key in weights and rank_key in ranks:
            score += ranks[rank_key] * weights[weight_key]

    return round(score, 2)


def run_sensitivity_analysis(subject: Dict[str, Any],
                              all_properties: List[Dict[str, Any]],
                              weights: Dict[str, float],
                              subject_weighted_score: float,
                              rank_3_score: float) -> List[Dict[str, Any]]:
    """
    Run rent/TMI reduction scenarios to calculate rank improvements.

    Calculates how much rent or TMI reduction is needed to move subject property
    to Rank #3 (competitive threshold).

    Args:
        subject: Subject property dictionary
        all_properties: List of all properties (for re-ranking simulation)
        weights: Variable weights
        subject_weighted_score: Current weighted score of subject
        rank_3_score: Weighted score of property ranked #3

    Returns:
        List of scenario dictionaries with estimated impacts
    """
    scenarios = []

    # Calculate gap to Rank #3
    gap_points = subject_weighted_score - rank_3_score

    if gap_points <= 0:
        # Already at or better than Rank #3
        return scenarios

    # Scenario 1: Net Rent Reduction
    # Net rent weighted at 16%, so gap_points / 0.16 = rank improvement needed
    # Estimate: Each ~$0.05/sf reduction = ~1 rank improvement (market dependent)
    # Conservative estimate: Use $0.05/sf per rank
    net_rent_weight = weights.get('net_asking_rent', 0.16)
    ranks_needed = gap_points / net_rent_weight if net_rent_weight > 0 else 0
    rent_reduction = round(ranks_needed * 0.05, 2)  # $0.05/sf per rank

    scenarios.append({
        "scenario": "Net Rent Reduction",
        "reduction_amount": rent_reduction,
        "new_net_asking_rent": round(subject['net_asking_rent'] - rent_reduction, 2),
        "estimated_new_rank": 3,
        "estimated_new_score": round(rank_3_score, 2),
        "explanation": f"Reduce rent by ${rent_reduction}/sf to close {gap_points:.2f} point gap"
    })

    # Scenario 2: TMI Reduction
    # TMI weighted at 14%
    tmi_weight = weights.get('tmi', 0.14)
    ranks_needed_tmi = gap_points / tmi_weight if tmi_weight > 0 else 0
    tmi_reduction = round(ranks_needed_tmi * 0.05, 2)

    scenarios.append({
        "scenario": "TMI Reduction",
        "reduction_amount": tmi_reduction,
        "new_tmi": round(subject['tmi'] - tmi_reduction, 2),
        "estimated_new_rank": 4,  # TMI has less weight than rent, so might only get to #4
        "estimated_new_score": round(rank_3_score + 0.2, 2),
        "explanation": f"Reduce TMI by ${tmi_reduction}/sf (negotiate with property manager)"
    })

    # Scenario 3: Combined Rent + TMI Reduction (smaller amounts)
    combined_rent_reduction = round(rent_reduction * 0.5, 2)
    combined_tmi_reduction = round(tmi_reduction * 0.5, 2)

    scenarios.append({
        "scenario": "Combined Rent + TMI Reduction",
        "rent_reduction": combined_rent_reduction,
        "tmi_reduction": combined_tmi_reduction,
        "new_net_asking_rent": round(subject['net_asking_rent'] - combined_rent_reduction, 2),
        "new_tmi": round(subject['tmi'] - combined_tmi_reduction, 2),
        "estimated_new_rank": 3,
        "estimated_new_score": round(rank_3_score, 2),
        "explanation": f"Split adjustment: ${combined_rent_reduction}/sf rent + ${combined_tmi_reduction}/sf TMI"
    })

    return scenarios


def generate_competitive_report(results: CompetitiveAnalysis, output_path: str, full: bool = False):
    """
    Generate professional markdown report with rankings and recommendations.

    Args:
        results: CompetitiveAnalysis dataclass with all analysis results
        output_path: Path to output markdown file
        full: If True, show all competitors; if False, show top 10 only (default)
    """
    subject = results.subject_property

    # Determine competitive status and deal-winning probability
    rank = subject['final_rank']
    if rank <= 3:
        status = "HIGHLY COMPETITIVE"
        probability = "70-90%"
        status_emoji = "✅"
        interpretation = "Your property is in the TOP 3 - you are well-positioned to win deals at current pricing."
    elif rank <= 10:
        status = "MARGINALLY COMPETITIVE"
        probability = "30-50%"
        status_emoji = "⚠️"
        interpretation = f"{rank - 3} properties offer better value. You MUST reduce rent or increase incentives to compete."
    elif rank <= 20:
        status = "WEAK POSITION"
        probability = "10-25%"
        status_emoji = "❌"
        interpretation = f"SERIOUS COMPETITIVE DISADVANTAGE. {rank - 3} properties offer superior value - major price reduction required."
    else:
        status = "NOT COMPETITIVE"
        probability = "<10%"
        status_emoji = "🚫"
        interpretation = f"FUNDAMENTALLY UNCOMPETITIVE. Consider repositioning, capital investment, or exit strategy."

    report = f"""# RELATIVE VALUATION ANALYSIS - COMPETITIVE POSITIONING REPORT

**Report Date**: {results.analysis_date}
**Market**: {results.market}
**Total Comparables Analyzed**: {results.total_properties}
**Subject Property**: {subject['address']} {subject.get('unit', '')}

---

## 🎯 EXECUTIVE SUMMARY

### **Competitive Position**

| Metric | Value |
|--------|-------|
| **Final Ranking** | **#{subject['final_rank']} out of {results.total_properties}** |
| **Weighted Score** | **{subject['weighted_score']:.2f}** (lower is better) |
| **Competitive Status** | {status_emoji} **{status}** |
| **Deal-Winning Probability** | **{probability}** |

### **Interpretation**

{interpretation}

---

## 📊 SUBJECT PROPERTY ANALYSIS

### **Property Details**

| Attribute | Value |
|-----------|-------|
| **Address** | {subject['address']} |
| **Unit** | {subject.get('unit', 'N/A')} |
| **Year Built** | {subject.get('year_built', 'N/A')} |
| **Clear Height** | {subject.get('clear_height_ft', 'N/A')} ft |
| **% Office Space** | {subject.get('pct_office_space', 0) * 100:.1f}% |
| **Parking Ratio** | {subject.get('parking_ratio', 'N/A')} spaces/1,000 sf |
| **Available SF** | {subject.get('available_sf', 'N/A'):,.0f} |
| **Net Asking Rent** | ${subject.get('net_asking_rent', 0):.2f}/sf |
| **TMI** | ${subject.get('tmi', 0):.2f}/sf |
| **Gross Rent** | ${(subject.get('net_asking_rent', 0) + subject.get('tmi', 0)):.2f}/sf |
| **Class** | {'A' if subject.get('class', 2) == 1 else 'B' if subject.get('class', 2) == 2 else 'C'} |"""

    # Add optional fields if available
    if subject.get('shipping_doors_tl'):
        report += f"\n| **Shipping Doors (Truck-Level)** | {subject.get('shipping_doors_tl', 0)} |"
    if subject.get('shipping_doors_di'):
        report += f"\n| **Shipping Doors (Drive-In)** | {subject.get('shipping_doors_di', 0)} |"
    if subject.get('power_amps'):
        report += f"\n| **Power** | {subject.get('power_amps', 0)} amps |"
    if subject.get('availability_date'):
        report += f"\n| **Availability Date** | {subject.get('availability_date', '')} |"
    report += f"\n| **Trailer Parking** | {'Yes' if subject.get('trailer_parking', False) else 'No'} |"
    report += f"\n| **Secure Shipping** | {'Yes' if subject.get('secure_shipping', False) else 'No'} |"
    report += f"\n| **Excess Land** | {'Yes' if subject.get('excess_land', False) else 'No'} |"

    report += f"""

### **Variable Rankings**

| Variable | Rank | Interpretation |
|----------|------|----------------|
| Building Age | {subject.get('rank_building_age', 'N/A')} | {'Excellent' if subject.get('rank_building_age', 999) <= 20 else 'Good' if subject.get('rank_building_age', 999) <= 50 else 'Moderate' if subject.get('rank_building_age', 999) <= 80 else 'Poor'} |
| Clear Height | {subject.get('rank_clear_height', 'N/A')} | {'Excellent' if subject.get('rank_clear_height', 999) <= 20 else 'Good' if subject.get('rank_clear_height', 999) <= 50 else 'Moderate' if subject.get('rank_clear_height', 999) <= 80 else 'Poor'} |
| % Office Space | {subject.get('rank_pct_office', 'N/A')} | {'Excellent' if subject.get('rank_pct_office', 999) <= 20 else 'Good' if subject.get('rank_pct_office', 999) <= 50 else 'Moderate' if subject.get('rank_pct_office', 999) <= 80 else 'Poor'} |
| Parking Ratio | {subject.get('rank_parking', 'N/A')} | {'Excellent' if subject.get('rank_parking', 999) <= 20 else 'Good' if subject.get('rank_parking', 999) <= 50 else 'Moderate' if subject.get('rank_parking', 999) <= 80 else 'Poor'} |
| Distance | {subject.get('rank_distance', 'N/A')} | Subject property (0 km - center point) |
| **Net Rent** | **{subject.get('rank_net_rent', 'N/A')}** | **16% weight - most critical for competitiveness** |
| **TMI** | **{subject.get('rank_tmi', 'N/A')}** | **14% weight - affects total occupancy cost** |
| Class | {subject.get('rank_class', 'N/A')} | {'Excellent' if subject.get('rank_class', 999) <= 20 else 'Good' if subject.get('rank_class', 999) <= 50 else 'Moderate' if subject.get('rank_class', 999) <= 80 else 'Poor'} |
| Area Difference | {subject.get('rank_area_diff', 'N/A')} | {'Excellent' if subject.get('rank_area_diff', 999) <= 20 else 'Good' if subject.get('rank_area_diff', 999) <= 50 else 'Moderate' if subject.get('rank_area_diff', 999) <= 80 else 'Poor'} size match |

**Lower rank number = better competitive position for that variable.**

---

## 🏆 {'ALL' if full else 'TOP 10'} COMPETITORS

These properties offer the best value propositions in the market:

| Rank | Property | Area (SF) | Net Rent | TMI | Gross Rent | Clear Ht | Ship TL | Ship DI | Power | Trailer | Avail Date | Score |
|------|----------|-----------|----------|-----|------------|----------|---------|---------|-------|---------|------------|-------|
"""

    # Add competitors (top 10 or all based on --full flag)
    competitors_to_show = results.all_properties if full else results.top_competitors
    for comp in competitors_to_show:
        # Format optional fields
        area_sf = f"{comp.get('available_sf', 0):,.0f}"
        clear_ht = f"{comp.get('clear_height_ft', 0):.0f} ft"
        ship_tl = comp.get('shipping_doors_tl', 0) if comp.get('shipping_doors_tl') else '-'
        ship_di = comp.get('shipping_doors_di', 0) if comp.get('shipping_doors_di') else '-'
        power = f"{comp.get('power_amps', 0)}" if comp.get('power_amps') else '-'
        trailer = 'Yes' if comp.get('trailer_parking', False) else 'No'
        avail = comp.get('availability_date', '-')

        report += f"| {comp['final_rank']} | {comp['address']} {comp.get('unit', '')} | {area_sf} | ${comp.get('net_asking_rent', 0):.2f} | ${comp.get('tmi', 0):.2f} | ${comp.get('gross_rent', 0):.2f} | {clear_ht} | {ship_tl} | {ship_di} | {power} | {trailer} | {avail} | {comp['weighted_score']:.2f} |\n"

    # Gap Analysis - wrap in no-break div to keep together
    gap = results.gap_analysis
    report += f"""

---

<div class="no-break">

## 📉 GAP ANALYSIS

### **Distance to Competitive Threshold (Rank #3)**

| Metric | Value |
|--------|-------|
| **Subject Weighted Score** | {subject['weighted_score']:.2f} |
| **Rank #3 Weighted Score** | {gap.get('rank_3_score', 'N/A'):.2f} |
| **Rank #3 Property** | {gap.get('rank_3_property', 'N/A')} |
| **Gap to Close** | **{gap.get('gap_to_rank_3', 0):.2f} points** |

**To achieve Rank #3 and become competitive, subject must improve weighted score by {gap.get('gap_to_rank_3', 0):.2f} points.**

</div>

---

## 💡 RECOMMENDED ACTIONS

### **Sensitivity Analysis: Pricing Adjustments to Achieve Rank #3**

"""

    # Add sensitivity scenarios
    for i, scenario in enumerate(results.sensitivity_scenarios, 1):
        report += f"### **Option {i}: {scenario['scenario']}**\n\n"

        if 'reduction_amount' in scenario:
            report += f"- **Reduction**: ${scenario['reduction_amount']:.2f}/sf\n"
            if 'new_net_asking_rent' in scenario:
                report += f"- **New Net Rent**: ${scenario['new_net_asking_rent']:.2f}/sf\n"
            if 'new_tmi' in scenario:
                report += f"- **New TMI**: ${scenario['new_tmi']:.2f}/sf\n"

        if 'rent_reduction' in scenario and 'tmi_reduction' in scenario:
            report += f"- **Rent Reduction**: ${scenario['rent_reduction']:.2f}/sf\n"
            report += f"- **TMI Reduction**: ${scenario['tmi_reduction']:.2f}/sf\n"
            report += f"- **New Net Rent**: ${scenario['new_net_asking_rent']:.2f}/sf\n"
            report += f"- **New TMI**: ${scenario['new_tmi']:.2f}/sf\n"

        report += f"- **Estimated New Rank**: #{scenario['estimated_new_rank']}\n"
        report += f"- **Estimated New Score**: {scenario['estimated_new_score']:.2f}\n"
        report += f"- **Explanation**: {scenario.get('explanation', '')}\n\n"

    # Final recommendations
    if rank <= 3:
        recommendation = """### **RECOMMENDATION: HOLD OR INCREASE PRICING**

Your property is in the Top 3 - you have strong competitive positioning. Consider:
- **Hold current pricing** and maintain selectivity on tenant quality
- **Increase rent by $0.25-0.50/sf** if market velocity is strong
- **Minimize concessions** - offer standard TI only (no above-market incentives)
- **Favor landlord-friendly lease terms** (shorter free rent, higher deposits)
"""
    elif rank <= 10:
        recommendation = f"""### **RECOMMENDATION: REDUCE PRICING OR INCREASE INCENTIVES**

You are ranked #{rank} - **{rank - 3} properties offer better value**. To compete effectively:
- **Implement Option 1** (recommended): Reduce net rent by indicated amount
- **Alternative**: Offer above-market TI allowance (${gap.get('gap_to_rank_3', 0) * 5:.2f}/sf)
- **Alternative**: Increase free rent period (add {int(gap.get('gap_to_rank_3', 0) / 2)} months)
- **Monitor market**: Re-run analysis in 60 days if no LOI activity
"""
    else:
        recommendation = f"""### **RECOMMENDATION: AGGRESSIVE PRICING REDUCTION OR REPOSITIONING**

You are ranked #{rank} - **SERIOUS COMPETITIVE DISADVANTAGE**. Consider:
- **Aggressive rent reduction**: ${gap.get('gap_to_rank_3', 0) * 0.10:.2f}/sf or more
- **Capital investment**: Address structural weaknesses (parking, clear height, building age)
- **Reposition**: Convert to alternative use (self-storage, last-mile delivery, etc.)
- **Exit strategy**: Sell to value-add investor or owner-user

Price reduction alone may not be sufficient to overcome structural disadvantages.
"""

    report += recommendation

    # Methodology footnote
    # Calculate total weight to prove it equals 100%
    total_weight = sum(results.weights_used.values())

    # Sort weights by importance (descending)
    sorted_weights = sorted(results.weights_used.items(), key=lambda x: -x[1])

    # Build weights table
    weights_table = "\n| Variable | Weight |\n|----------|--------|\n"
    for var_name, weight in sorted_weights:
        # Format variable name for display
        display_name = var_name.replace('_', ' ').title()
        weights_table += f"| {display_name} | {weight:.1%} |\n"

    # Add total row
    weights_table += f"| **TOTAL** | **{total_weight:.1%}** |\n"

    report += f"""
---

## 📖 METHODOLOGY

This analysis uses a **multi-criteria weighted ranking system** to objectively assess competitive position:

1. **Data Collection**: Extract property attributes from comparable evidence
2. **Variable Weighting**: Assign importance weights based on tenant priorities
3. **Independent Ranking**: Rank each variable 1 (best) to X (worst) across all properties
4. **Weighted Score Calculation**: Sum of (rank × weight) for all variables
5. **Final Re-Ranking**: Sort properties by weighted score (lower = better)

### **Weights Used in This Analysis**

{weights_table}

✅ **Weights sum to {total_weight:.1%}** - calculation verified

**Lower weighted score = fewer negative rank points = better competitive position**

---

## ⚠️ LIMITATIONS

- Model excludes qualitative factors (landlord reputation, property management quality, amenities)
- Weights represent average tenant priorities; individual tenants may weight factors differently
- Asking rents may not reflect net effective rents after concessions
- Rankings are point-in-time snapshots; market conditions change

**Validation**: Always confirm model results with market intelligence from brokers and recent lease transactions.

---

**END OF REPORT**

*Generated by: Relative Valuation Calculator v1.0.0*
*Analysis Date: {results.analysis_date}*
*Report Generated: {datetime.now(ZoneInfo('America/New_York')).strftime('%Y-%m-%d %H:%M:%S')} ET*
"""

    # Write report to file
    with open(output_path, 'w') as f:
        f.write(report)

    print(f"\n✅ Report generated: {output_path}")


def apply_must_have_filters(properties: List[Dict[str, Any]], filters: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Filter properties based on must-have requirements.

    Args:
        properties: List of property dictionaries
        filters: Dictionary of minimum requirements (e.g., {"rail_access": True, "clear_height_ft_min": 32})

    Returns:
        Tuple of (filtered properties, excluded properties)
    """
    if not filters:
        return properties, []

    filtered = []
    excluded = []

    for prop in properties:
        include = True
        exclusion_reasons = []

        # Check each filter criterion
        for field, required_value in filters.items():
            # Handle minimum value filters (e.g., clear_height_ft_min)
            if field.endswith('_min'):
                base_field = field[:-4]  # Remove '_min' suffix
                actual_value = prop.get(base_field, 0)
                if actual_value < required_value:
                    include = False
                    exclusion_reasons.append(f"{base_field} {actual_value} < {required_value} (minimum)")

            # Handle maximum value filters (e.g., days_on_market_max)
            elif field.endswith('_max'):
                base_field = field[:-4]  # Remove '_max' suffix
                actual_value = prop.get(base_field, float('inf'))
                if actual_value > required_value:
                    include = False
                    exclusion_reasons.append(f"{base_field} {actual_value} > {required_value} (maximum)")

            # Handle boolean filters (must be True)
            elif isinstance(required_value, bool) and required_value:
                actual_value = prop.get(field, False)
                if not actual_value:
                    include = False
                    exclusion_reasons.append(f"{field} is required")

            # Handle exact match filters (e.g., zoning must equal "M1")
            elif isinstance(required_value, str):
                actual_value = prop.get(field, '').strip().upper()
                required_str = str(required_value).strip().upper()
                if actual_value != required_str:
                    include = False
                    exclusion_reasons.append(f"{field} '{actual_value}' != '{required_str}'")

            # Handle ordinal filters (e.g., sprinkler_type must be <= 1 for ESFR)
            elif isinstance(required_value, (int, float)) and not field.endswith('_min') and not field.endswith('_max'):
                actual_value = prop.get(field, float('inf'))
                if actual_value > required_value:
                    include = False
                    exclusion_reasons.append(f"{field} {actual_value} > {required_value}")

        if include:
            filtered.append(prop)
        else:
            prop['exclusion_reasons'] = exclusion_reasons
            excluded.append(prop)

    return filtered, excluded


def run_analysis(data: Dict[str, Any]) -> CompetitiveAnalysis:
    """
    Run complete relative valuation analysis.

    Args:
        data: Dictionary with analysis_date, market, subject_property, comparables, weights

    Returns:
        CompetitiveAnalysis results object
    """
    print("\n🔍 Running Relative Valuation Analysis...")

    # Extract components
    analysis_date = data['analysis_date']
    market = data['market']
    subject_data = data['subject_property']
    comparables_data = data['comparables']
    weights = data['weights']

    # Combine subject + comparables into single list
    all_properties_data = [subject_data] + comparables_data

    # Calculate building_age_years from year_built if not already provided
    from datetime import datetime
    analysis_year = int(analysis_date.split('-')[0]) if analysis_date else datetime.now().year
    for prop in all_properties_data:
        if 'year_built' in prop and prop.get('year_built'):
            # Calculate building age if not already provided
            if not prop.get('building_age_years'):
                prop['building_age_years'] = analysis_year - prop['year_built']

    # Apply must-have filters if specified
    filters = data.get('filters', {})
    if filters:
        print(f"\n   Applying must-have filters...")
        filtered_properties, excluded_properties = apply_must_have_filters(all_properties_data, filters)
        print(f"   {len(excluded_properties)} properties excluded by filters")
        for excl in excluded_properties:
            print(f"      - {excl['address']}: {', '.join(excl['exclusion_reasons'])}")
        all_properties_data = filtered_properties

    # Calculate area differences
    subject_sf = subject_data['available_sf']
    all_properties_data = calculate_area_differences(all_properties_data, subject_sf)

    print(f"\n   Loaded {len(all_properties_data)} properties for analysis")
    print(f"   Subject: {subject_data['address']} {subject_data.get('unit', '')}")

    # Detect available optional variables
    print("\n   Detecting available variables...")
    available_vars = detect_available_variables(all_properties_data)
    num_available = sum(1 for v in available_vars.values() if v)
    print(f"   Using {num_available} of 25 possible variables")

    # Allocate weights dynamically based on available data
    dynamic_weights = allocate_dynamic_weights(available_vars, weights)
    print(f"   Dynamic weights calculated:")
    for var, weight in sorted(dynamic_weights.items(), key=lambda x: -x[1]):
        print(f"      {var}: {weight:.1%}")

    # Extract values for each variable
    building_ages = [p.get('building_age_years', 0) for p in all_properties_data]
    clear_heights = [p['clear_height_ft'] for p in all_properties_data]
    pct_offices = [p['pct_office_space'] for p in all_properties_data]
    parking_ratios = [p['parking_ratio'] for p in all_properties_data]
    distances = [p['distance_km'] for p in all_properties_data]
    net_rents = [p['net_asking_rent'] for p in all_properties_data]
    tmis = [p['tmi'] for p in all_properties_data]
    classes = [p.get('class', 2) for p in all_properties_data]
    area_diffs = [p['area_difference'] for p in all_properties_data]

    # Rank each variable
    # Variables where LOWER = BETTER (ascending=True): rent, TMI, distance, class, area_diff, building_age, hvac_coverage, sprinkler_type, occupancy_status
    # Variables where HIGHER = BETTER (ascending=False): clear_height, parking, % office, shipping doors, power, boolean amenities, bay_depth, lot_size
    print("\n   Ranking variables...")

    ranks_building_age = rank_variable(building_ages, ascending=True)  # Newer (lower age) = better
    ranks_clear_height = rank_variable(clear_heights, ascending=False)  # Higher = better
    ranks_pct_office = rank_variable(pct_offices, ascending=False)  # Higher = better (for office users)
    ranks_parking = rank_variable(parking_ratios, ascending=False)  # More parking = better
    ranks_distance = rank_variable(distances, ascending=True)  # Closer (lower km) = better
    ranks_net_rent = rank_variable(net_rents, ascending=True)  # Lower rent = better
    ranks_tmi = rank_variable(tmis, ascending=True)  # Lower TMI = better
    ranks_class = rank_variable(classes, ascending=True)  # Lower class number (A=1) = better
    ranks_area_diff = rank_variable(area_diffs, ascending=True)  # Smaller difference = better

    # Rank optional variables if available
    ranks_shipping_tl = None
    ranks_shipping_di = None
    ranks_power = None
    ranks_trailer_parking = None
    ranks_secure_shipping = None
    ranks_excess_land = None

    if available_vars.get('shipping_doors_tl', False):
        shipping_tl_values = [p.get('shipping_doors_tl', 0) for p in all_properties_data]
        ranks_shipping_tl = rank_variable(shipping_tl_values, ascending=False)  # More doors = better

    if available_vars.get('shipping_doors_di', False):
        shipping_di_values = [p.get('shipping_doors_di', 0) for p in all_properties_data]
        ranks_shipping_di = rank_variable(shipping_di_values, ascending=False)  # More doors = better

    if available_vars.get('power_amps', False):
        power_values = [p.get('power_amps', 0) for p in all_properties_data]
        ranks_power = rank_variable(power_values, ascending=False)  # More power = better

    if available_vars.get('trailer_parking', False):
        trailer_values = [1 if p.get('trailer_parking', False) else 0 for p in all_properties_data]
        ranks_trailer_parking = rank_variable(trailer_values, ascending=False)  # True = better

    if available_vars.get('secure_shipping', False):
        secure_values = [1 if p.get('secure_shipping', False) else 0 for p in all_properties_data]
        ranks_secure_shipping = rank_variable(secure_values, ascending=False)  # True = better

    if available_vars.get('excess_land', False):
        excess_values = [1 if p.get('excess_land', False) else 0 for p in all_properties_data]
        ranks_excess_land = rank_variable(excess_values, ascending=False)  # True = better

    # Rank new optional variables (Phase 2 enhancements)
    ranks_bay_depth = None
    ranks_lot_size = None
    ranks_hvac_coverage = None
    ranks_sprinkler_type = None
    ranks_rail_access = None
    ranks_crane = None
    ranks_occupancy_status = None

    if available_vars.get('bay_depth_ft', False):
        bay_depth_values = [p.get('bay_depth_ft', 0) for p in all_properties_data]
        ranks_bay_depth = rank_variable(bay_depth_values, ascending=False)  # Deeper = better

    if available_vars.get('lot_size_acres', False):
        lot_size_values = [p.get('lot_size_acres', 0) for p in all_properties_data]
        ranks_lot_size = rank_variable(lot_size_values, ascending=False)  # Larger = better

    if available_vars.get('hvac_coverage', False):
        hvac_values = [p.get('hvac_coverage', 3) for p in all_properties_data]
        ranks_hvac_coverage = rank_variable(hvac_values, ascending=True)  # Y=1 better than N=3

    if available_vars.get('sprinkler_type', False):
        sprinkler_values = [p.get('sprinkler_type', 3) for p in all_properties_data]
        ranks_sprinkler_type = rank_variable(sprinkler_values, ascending=True)  # ESFR=1 better than None=3

    if available_vars.get('rail_access', False):
        rail_values = [1 if p.get('rail_access', False) else 0 for p in all_properties_data]
        ranks_rail_access = rank_variable(rail_values, ascending=False)  # True = better

    if available_vars.get('crane', False):
        crane_values = [1 if p.get('crane', False) else 0 for p in all_properties_data]
        ranks_crane = rank_variable(crane_values, ascending=False)  # True = better

    if available_vars.get('occupancy_status', False):
        occupancy_values = [p.get('occupancy_status', 2) for p in all_properties_data]
        ranks_occupancy_status = rank_variable(occupancy_values, ascending=True)  # Vacant=1 better than Tenant=2

    # Rank Phase 2 Batch 2 variables
    ranks_grade_level_doors = None
    ranks_days_on_market = None
    ranks_zoning = None

    if available_vars.get('grade_level_doors', False):
        grade_level_values = [p.get('grade_level_doors', 0) for p in all_properties_data]
        ranks_grade_level_doors = rank_variable(grade_level_values, ascending=False)  # More doors = better

    if available_vars.get('days_on_market', False):
        dom_values = [p.get('days_on_market', 0) for p in all_properties_data]
        ranks_days_on_market = rank_variable(dom_values, ascending=False)  # Higher DOM = more motivated landlord = better for tenant

    if available_vars.get('zoning', False):
        # For zoning, we'll treat it as a categorical variable
        # Properties with the same zoning get the same rank
        # Lower alphabetical order = better rank (e.g., M1 better than M3)
        zoning_values = [p.get('zoning', '').strip().upper() for p in all_properties_data]
        # Create a mapping of unique zoning types to ranks
        unique_zonings = sorted(set(z for z in zoning_values if z))
        zoning_rank_map = {z: i + 1 for i, z in enumerate(unique_zonings)}
        # Assign ranks, with empty zoning getting worst rank
        worst_rank = len(unique_zonings) + 1
        ranks_zoning = [zoning_rank_map.get(z, worst_rank) if z else worst_rank for z in zoning_values]

    # Calculate weighted scores
    print("   Calculating weighted scores...")
    for i, prop in enumerate(all_properties_data):
        # Build ranks_dict with core variables
        ranks_dict = {
            'building_age_years': ranks_building_age[i],
            'clear_height_ft': ranks_clear_height[i],
            'pct_office_space': ranks_pct_office[i],
            'parking_ratio': ranks_parking[i],
            'distance_km': ranks_distance[i],
            'net_asking_rent': ranks_net_rent[i],
            'tmi': ranks_tmi[i],
            'class': ranks_class[i],
            'area_difference': ranks_area_diff[i]
        }

        # Add existing optional variable ranks if available
        if ranks_shipping_tl is not None:
            ranks_dict['shipping_doors_tl'] = ranks_shipping_tl[i]
        if ranks_shipping_di is not None:
            ranks_dict['shipping_doors_di'] = ranks_shipping_di[i]
        if ranks_power is not None:
            ranks_dict['power_amps'] = ranks_power[i]
        if ranks_trailer_parking is not None:
            ranks_dict['trailer_parking'] = ranks_trailer_parking[i]
        if ranks_secure_shipping is not None:
            ranks_dict['secure_shipping'] = ranks_secure_shipping[i]
        if ranks_excess_land is not None:
            ranks_dict['excess_land'] = ranks_excess_land[i]

        # Add new optional variable ranks if available
        if ranks_bay_depth is not None:
            ranks_dict['bay_depth_ft'] = ranks_bay_depth[i]
        if ranks_lot_size is not None:
            ranks_dict['lot_size_acres'] = ranks_lot_size[i]
        if ranks_hvac_coverage is not None:
            ranks_dict['hvac_coverage'] = ranks_hvac_coverage[i]
        if ranks_sprinkler_type is not None:
            ranks_dict['sprinkler_type'] = ranks_sprinkler_type[i]
        if ranks_rail_access is not None:
            ranks_dict['rail_access'] = ranks_rail_access[i]
        if ranks_crane is not None:
            ranks_dict['crane'] = ranks_crane[i]
        if ranks_occupancy_status is not None:
            ranks_dict['occupancy_status'] = ranks_occupancy_status[i]

        # Add Phase 2 Batch 2 variable ranks if available
        if ranks_grade_level_doors is not None:
            ranks_dict['grade_level_doors'] = ranks_grade_level_doors[i]
        if ranks_days_on_market is not None:
            ranks_dict['days_on_market'] = ranks_days_on_market[i]
        if ranks_zoning is not None:
            ranks_dict['zoning'] = ranks_zoning[i]

        # Assign core variable ranks to property
        prop['rank_building_age'] = int(ranks_building_age[i])
        prop['rank_clear_height'] = int(ranks_clear_height[i])
        prop['rank_pct_office'] = int(ranks_pct_office[i])
        prop['rank_parking'] = int(ranks_parking[i])
        prop['rank_distance'] = int(ranks_distance[i])
        prop['rank_net_rent'] = int(ranks_net_rent[i])
        prop['rank_tmi'] = int(ranks_tmi[i])
        prop['rank_class'] = int(ranks_class[i])
        prop['rank_area_diff'] = int(ranks_area_diff[i])

        # Assign existing optional variable ranks to property
        prop['rank_shipping_doors_tl'] = int(ranks_shipping_tl[i]) if ranks_shipping_tl else 0
        prop['rank_shipping_doors_di'] = int(ranks_shipping_di[i]) if ranks_shipping_di else 0
        prop['rank_power'] = int(ranks_power[i]) if ranks_power else 0
        prop['rank_trailer_parking'] = int(ranks_trailer_parking[i]) if ranks_trailer_parking else 0
        prop['rank_secure_shipping'] = int(ranks_secure_shipping[i]) if ranks_secure_shipping else 0
        prop['rank_excess_land'] = int(ranks_excess_land[i]) if ranks_excess_land else 0

        # Assign new optional variable ranks to property
        prop['rank_bay_depth'] = int(ranks_bay_depth[i]) if ranks_bay_depth else 0
        prop['rank_lot_size'] = int(ranks_lot_size[i]) if ranks_lot_size else 0
        prop['rank_hvac_coverage'] = int(ranks_hvac_coverage[i]) if ranks_hvac_coverage else 0
        prop['rank_sprinkler_type'] = int(ranks_sprinkler_type[i]) if ranks_sprinkler_type else 0
        prop['rank_rail_access'] = int(ranks_rail_access[i]) if ranks_rail_access else 0
        prop['rank_crane'] = int(ranks_crane[i]) if ranks_crane else 0
        prop['rank_occupancy_status'] = int(ranks_occupancy_status[i]) if ranks_occupancy_status else 0

        # Assign Phase 2 Batch 2 variable ranks to property
        prop['rank_grade_level_doors'] = int(ranks_grade_level_doors[i]) if ranks_grade_level_doors else 0
        prop['rank_days_on_market'] = int(ranks_days_on_market[i]) if ranks_days_on_market else 0
        prop['rank_zoning'] = int(ranks_zoning[i]) if ranks_zoning else 0

        # Calculate weighted score using DYNAMIC weights
        prop['weighted_score'] = calculate_weighted_score(prop, ranks_dict, dynamic_weights)

    # Sort by weighted score (ascending - lower is better)
    all_properties_data.sort(key=lambda x: x['weighted_score'])

    # Assign final ranks
    for i, prop in enumerate(all_properties_data):
        prop['final_rank'] = i + 1
        prop['gross_rent'] = round(prop['net_asking_rent'] + prop['tmi'], 2)

    print("   Final rankings assigned")

    # Find subject property
    subject_result = next((p for p in all_properties_data if p.get('is_subject', False)), None)
    if not subject_result:
        raise ValueError("Subject property not found in results (check is_subject flag)")

    subject_rank = subject_result['final_rank']
    print(f"\n   ✅ Subject Property Rank: #{subject_rank} out of {len(all_properties_data)}")
    print(f"   Weighted Score: {subject_result['weighted_score']:.2f}")

    # Get top 10 competitors
    top_10 = all_properties_data[:10]

    # Gap analysis
    if len(all_properties_data) >= 3:
        rank_3_property = all_properties_data[2]
        gap_to_rank_3 = subject_result['weighted_score'] - rank_3_property['weighted_score']
        gap_analysis = {
            'gap_to_rank_3': round(gap_to_rank_3, 2),
            'rank_3_score': round(rank_3_property['weighted_score'], 2),
            'rank_3_property': f"{rank_3_property['address']} {rank_3_property.get('unit', '')}"
        }
    else:
        gap_analysis = {
            'gap_to_rank_3': 0.0,
            'rank_3_score': 0.0,
            'rank_3_property': 'N/A'
        }

    # Run sensitivity analysis
    print("\n   Running sensitivity analysis...")
    sensitivity_scenarios = run_sensitivity_analysis(
        subject_result,
        all_properties_data,
        weights,
        subject_result['weighted_score'],
        gap_analysis['rank_3_score']
    )

    # Build results object
    results = CompetitiveAnalysis(
        analysis_date=analysis_date,
        market=market,
        total_properties=len(all_properties_data),
        subject_property=subject_result,
        top_competitors=top_10,
        gap_analysis=gap_analysis,
        sensitivity_scenarios=sensitivity_scenarios,
        all_properties=all_properties_data,
        weights_used=dynamic_weights
    )

    return results


def main():
    """Main entry point for command-line interface."""
    parser = argparse.ArgumentParser(
        description='Relative Valuation Calculator - Competitive Positioning Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate markdown report (top 10 competitors)
  python relative_valuation_calculator.py --input data.json --output report.md

  # Generate markdown report with ALL competitors
  python relative_valuation_calculator.py --input data.json --output report.md --full

  # Generate JSON results only
  python relative_valuation_calculator.py --input data.json --output-json results.json

  # Generate both markdown and JSON with full competitor list
  python relative_valuation_calculator.py --input data.json --output report.md --output-json results.json --full
        """
    )

    parser.add_argument('--input', required=True, help='Path to JSON input file')
    parser.add_argument('--output', help='Path to output markdown report (optional)')
    parser.add_argument('--output-json', help='Path to output JSON results (optional)')
    parser.add_argument('--full', action='store_true', help='Show all competitors in report (default: top 10 only)')
    parser.add_argument('--persona', choices=['default', '3pl', 'manufacturing', 'office'], default='default',
                        help='Tenant persona for weight optimization: default (balanced), 3pl (distribution focus), manufacturing (heavy industry), office (professional services)')
    parser.add_argument('--weights-config', type=str,
                        help='Path to custom weights configuration file (default: weights_config.json)')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode (not implemented in Phase 1)')

    args = parser.parse_args()

    if args.interactive:
        print("❌ Interactive mode not implemented in Phase 1")
        sys.exit(1)

    if not args.output and not args.output_json:
        print("❌ Error: Must specify --output (markdown) or --output-json (JSON results)")
        sys.exit(1)

    # Load data
    print(f"\n📂 Loading data from: {args.input}")
    data = load_comparable_data(args.input)

    # Apply tenant persona weights if specified
    if args.persona != 'default' or args.weights_config:
        persona_weights = get_tenant_persona_weights(args.persona, args.weights_config)
        data['weights'] = persona_weights
        if args.weights_config:
            print(f"   Using {args.persona.upper()} tenant persona weight profile from {args.weights_config}")
        else:
            print(f"   Using {args.persona.upper()} tenant persona weight profile")

    # Run analysis
    results = run_analysis(data)

    # Generate outputs
    if args.output_json:
        with open(args.output_json, 'w') as f:
            json.dump(asdict(results), f, indent=2, default=str)
        print(f"✅ JSON results saved: {args.output_json}")

    if args.output:
        generate_competitive_report(results, args.output, full=args.full)

    print("\n✅ Analysis complete!\n")


if __name__ == '__main__':
    main()
