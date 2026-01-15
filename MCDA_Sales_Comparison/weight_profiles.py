#!/usr/bin/env python3
"""
Weight Profiles for MCDA Sales Comparison

Provides sales-specific weight profiles for different property types:
- Industrial (default, logistics, manufacturing)
- Office (default)
- Retail (default)

Key differences from leasing weights:
- Sales focus on physical characteristics over rent/TMI
- Location is weighted higher for permanence
- Condition/age more important than in leasing

Author: Claude Code
Version: 1.0.0
Date: 2025-12-16
"""

from typing import Dict, Any, Optional


# =============================================================================
# SALES WEIGHT PROFILES
# =============================================================================

SALES_WEIGHT_PROFILES = {
    # -------------------------------------------------------------------------
    # INDUSTRIAL PROFILES
    # -------------------------------------------------------------------------
    'industrial_default': {
        'location_score': 0.20,       # Location/accessibility
        'clear_height_feet': 0.15,    # Functional utility
        'condition': 0.15,            # Physical condition (ordinal)
        'effective_age_years': 0.15,  # Economic life remaining
        'loading_docks_total': 0.10,  # Dock + grade level doors
        'highway_frontage': 0.10,     # Visibility/access
        'lot_size_acres': 0.05,       # Land component
        'building_size_sf': 0.05,     # Size differential (closer to subject)
        'office_finish_pct': 0.05     # Office buildout %
    },

    'industrial_logistics': {
        'location_score': 0.15,       # Less critical for logistics
        'clear_height_feet': 0.20,    # Critical for racking
        'condition': 0.12,
        'effective_age_years': 0.12,
        'loading_docks_total': 0.15,  # Critical for throughput
        'highway_frontage': 0.12,     # Highway access important
        'lot_size_acres': 0.08,       # Trailer staging
        'building_size_sf': 0.03,
        'office_finish_pct': 0.03     # Minimal office needed
    },

    'industrial_manufacturing': {
        'location_score': 0.15,
        'clear_height_feet': 0.18,
        'condition': 0.15,
        'effective_age_years': 0.12,
        'loading_docks_total': 0.08,
        'highway_frontage': 0.08,
        'lot_size_acres': 0.06,
        'building_size_sf': 0.05,
        'power_amps': 0.08,           # Manufacturing-specific
        'crane': 0.05                 # Manufacturing-specific
    },

    # -------------------------------------------------------------------------
    # OFFICE PROFILES
    # -------------------------------------------------------------------------
    'office_default': {
        'location_score': 0.25,       # Location premium for office
        'building_class': 0.18,       # Class A/B/C
        'condition': 0.15,
        'effective_age_years': 0.12,
        'parking_ratio': 0.12,        # Critical for suburban
        'floor_plate_efficiency': 0.08,
        'ceiling_height': 0.05,
        'building_size_sf': 0.05
    },

    # -------------------------------------------------------------------------
    # RETAIL PROFILES
    # -------------------------------------------------------------------------
    'retail_default': {
        'location_score': 0.30,       # Location is everything
        'traffic_count': 0.15,
        'frontage_feet': 0.12,
        'condition': 0.12,
        'effective_age_years': 0.10,
        'parking_ratio': 0.10,
        'building_size_sf': 0.06,
        'ceiling_height': 0.05
    }
}


# =============================================================================
# VARIABLE DIRECTION CONFIGURATION
# =============================================================================

VARIABLE_DIRECTIONS = {
    # Higher value = better property (ascending=False for ranking)
    'location_score': 'higher_is_better',
    'clear_height_feet': 'higher_is_better',
    'loading_docks_total': 'higher_is_better',
    'highway_frontage': 'higher_is_better',  # Boolean: True > False
    'lot_size_acres': 'higher_is_better',
    'parking_ratio': 'higher_is_better',
    'power_amps': 'higher_is_better',
    'crane': 'higher_is_better',  # Boolean
    'floor_plate_efficiency': 'higher_is_better',
    'ceiling_height': 'higher_is_better',
    'traffic_count': 'higher_is_better',
    'frontage_feet': 'higher_is_better',
    'office_finish_pct': 'higher_is_better',

    # Lower value = better property (ascending=True for ranking)
    'effective_age_years': 'lower_is_better',
    'condition': 'lower_is_better',  # Ordinal: excellent=1, good=2, avg=3, fair=4, poor=5
    'building_class': 'lower_is_better',  # A=1, B=2, C=3

    # Closer to subject = better (special handling)
    'building_size_sf': 'closer_to_subject'
}


# =============================================================================
# WEIGHT RETRIEVAL FUNCTIONS
# =============================================================================

def get_sales_weight_profile(profile_name: str) -> Dict[str, float]:
    """
    Get weight profile by name.

    Args:
        profile_name: Name of the profile (e.g., 'industrial_default')

    Returns:
        Dictionary of variable weights (sum to 1.0)
    """
    profile = SALES_WEIGHT_PROFILES.get(profile_name)
    if profile is None:
        # Default to industrial_default for unknown profiles
        profile = SALES_WEIGHT_PROFILES['industrial_default']
    return profile.copy()


def get_variable_directions() -> Dict[str, str]:
    """
    Get variable ranking directions.

    Returns:
        Dictionary mapping variable names to direction:
        - 'higher_is_better': Higher values rank better (ascending=False)
        - 'lower_is_better': Lower values rank better (ascending=True)
        - 'closer_to_subject': Values closer to subject rank better
    """
    return VARIABLE_DIRECTIONS.copy()


# =============================================================================
# WEIGHT NORMALIZATION
# =============================================================================

def normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    """
    Normalize weights to sum to 1.0.

    Handles both decimal (0.20) and percentage (20) inputs.

    Args:
        weights: Dictionary of weights

    Returns:
        Normalized weights summing to 1.0
    """
    if not weights:
        return {}

    # Detect percentage inputs (values > 1)
    if any(abs(v) > 1 for v in weights.values()):
        weights = {k: v / 100.0 for k, v in weights.items()}

    total = sum(weights.values())
    if total <= 0:
        return {}

    return {k: v / total for k, v in weights.items()}


# =============================================================================
# DYNAMIC WEIGHT ALLOCATION
# =============================================================================

def allocate_dynamic_weights(
    available_vars: Dict[str, bool],
    base_weights: Dict[str, float]
) -> Dict[str, float]:
    """
    Dynamically allocate weights based on available data.

    Redistributes weights from unavailable variables to available ones,
    maintaining proportional relationships.

    Args:
        available_vars: Dictionary mapping variable names to availability (True/False)
        base_weights: Base weights to start from

    Returns:
        Adjusted weights that sum to 1.0, excluding unavailable variables
    """
    if not available_vars or not base_weights:
        return {}

    # Filter to available variables
    available_weights = {
        var: base_weights.get(var, 0)
        for var, is_available in available_vars.items()
        if is_available and var in base_weights
    }

    # If no variables available, return empty
    if not available_weights:
        return {}

    # Normalize to sum to 1.0
    total = sum(available_weights.values())
    if total <= 0:
        # Equal weight distribution if all base weights are zero
        num_vars = len(available_weights)
        return {var: 1.0 / num_vars for var in available_weights}

    return {var: weight / total for var, weight in available_weights.items()}


# =============================================================================
# PROFILE BY PROPERTY TYPE
# =============================================================================

def get_profile_for_property_type(
    property_type: str,
    subtype: Optional[str] = None
) -> Dict[str, float]:
    """
    Get appropriate weight profile for property type.

    Args:
        property_type: Primary type ('industrial', 'office', 'retail')
        subtype: Optional subtype ('logistics', 'manufacturing', etc.)

    Returns:
        Weight profile for the property type
    """
    property_type = property_type.lower()
    subtype = subtype.lower() if subtype else 'default'

    profile_name = f"{property_type}_{subtype}"

    # Try specific profile first, then default for type
    if profile_name in SALES_WEIGHT_PROFILES:
        return get_sales_weight_profile(profile_name)
    elif f"{property_type}_default" in SALES_WEIGHT_PROFILES:
        return get_sales_weight_profile(f"{property_type}_default")
    else:
        return get_sales_weight_profile('industrial_default')


if __name__ == '__main__':
    print("MCDA Sales Comparison - Weight Profiles")
    print("\nAvailable profiles:")
    for name, weights in SALES_WEIGHT_PROFILES.items():
        total = sum(weights.values())
        print(f"  {name}: {len(weights)} variables, sum={total:.3f}")

    print("\nIndustrial Default Profile:")
    for var, weight in get_sales_weight_profile('industrial_default').items():
        direction = VARIABLE_DIRECTIONS.get(var, 'unknown')
        print(f"  {var}: {weight:.2%} ({direction})")
