#!/usr/bin/env python3
"""
Input Validation Module
Provides validation functions beyond JSON schema validation.

Author: Claude Code
Created: 2025-11-17
"""

from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def validate_input_data(data: Dict) -> Tuple[bool, Optional[str]]:
    """
    Validate complete input data structure.

    Args:
        data: Complete input data dictionary

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check required top-level keys
    required_keys = ['site_address']
    for key in required_keys:
        if key not in data:
            return False, f"Missing required field: {key}"

    # Validate site address
    if not data.get('site_address') or len(str(data['site_address']).strip()) == 0:
        return False, "Site address cannot be empty"

    # Validate Phase I ESA if present
    if 'phase_1_esa' in data:
        is_valid, error = validate_phase_esa_data(data['phase_1_esa'], phase=1)
        if not is_valid:
            return False, f"Phase I ESA validation error: {error}"

    # Validate Phase II ESA if present
    if 'phase_2_esa' in data:
        is_valid, error = validate_phase_esa_data(data['phase_2_esa'], phase=2)
        if not is_valid:
            return False, f"Phase II ESA validation error: {error}"

    # Validate cleanup scenarios if present
    if 'cleanup_scenarios' in data:
        is_valid, error = validate_cleanup_scenarios(data['cleanup_scenarios'])
        if not is_valid:
            return False, f"Cleanup scenarios validation error: {error}"

    return True, None


def validate_phase_esa_data(esa_data: Dict, phase: int = 1) -> Tuple[bool, Optional[str]]:
    """
    Validate Phase I or Phase II ESA data structure.

    Args:
        esa_data: ESA data dictionary
        phase: ESA phase (1 or 2)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if phase == 1:
        # Phase I ESA validation
        if 'findings' in esa_data:
            if not isinstance(esa_data['findings'], list):
                return False, "Phase I 'findings' must be a list"

        if 'recs' in esa_data:
            if not isinstance(esa_data['recs'], list):
                return False, "Phase I 'recs' must be a list"

            # Validate REC structure
            for i, rec in enumerate(esa_data['recs']):
                if not isinstance(rec, dict):
                    return False, f"REC {i+1} must be a dictionary"
                if 'description' not in rec:
                    return False, f"REC {i+1} missing 'description' field"

        if 'data_gaps' in esa_data:
            if not isinstance(esa_data['data_gaps'], list):
                return False, "Phase I 'data_gaps' must be a list"

    elif phase == 2:
        # Phase II ESA validation
        if 'soil_samples' in esa_data:
            if not isinstance(esa_data['soil_samples'], list):
                return False, "Phase II 'soil_samples' must be a list"

            # Validate sample structure
            for i, sample in enumerate(esa_data['soil_samples']):
                if not isinstance(sample, dict):
                    return False, f"Soil sample {i+1} must be a dictionary"

        if 'groundwater_samples' in esa_data:
            if not isinstance(esa_data['groundwater_samples'], list):
                return False, "Phase II 'groundwater_samples' must be a list"

            # Validate sample structure
            for i, sample in enumerate(esa_data['groundwater_samples']):
                if not isinstance(sample, dict):
                    return False, f"Groundwater sample {i+1} must be a dictionary"

        if 'exceedances' in esa_data:
            if not isinstance(esa_data['exceedances'], list):
                return False, "Phase II 'exceedances' must be a list"

        if 'contaminants' in esa_data:
            if not isinstance(esa_data['contaminants'], list):
                return False, "Phase II 'contaminants' must be a list"

    return True, None


def validate_cleanup_scenarios(scenarios: Dict) -> Tuple[bool, Optional[str]]:
    """
    Validate cleanup scenario cost ranges.

    Args:
        scenarios: Dictionary of cleanup scenarios with cost ranges

    Returns:
        Tuple of (is_valid, error_message)
    """
    scenario_types = ['risk_assessment', 'remediation', 'brownfield']

    for scenario_type in scenario_types:
        if scenario_type in scenarios:
            scenario = scenarios[scenario_type]

            if not isinstance(scenario, dict):
                return False, f"{scenario_type} must be a dictionary"

            # Validate cost range
            if 'cost_low' in scenario and 'cost_high' in scenario:
                cost_low = scenario['cost_low']
                cost_high = scenario['cost_high']

                # Check types
                if not isinstance(cost_low, (int, float)):
                    return False, f"{scenario_type} cost_low must be a number"
                if not isinstance(cost_high, (int, float)):
                    return False, f"{scenario_type} cost_high must be a number"

                # Check range logic
                if cost_low < 0:
                    return False, f"{scenario_type} cost_low cannot be negative"
                if cost_high < 0:
                    return False, f"{scenario_type} cost_high cannot be negative"
                if cost_low > cost_high:
                    return False, f"{scenario_type} cost_low cannot exceed cost_high"

    return True, None


def validate_discount_rate(discount_rate: float) -> Tuple[bool, Optional[str]]:
    """
    Validate discount rate is within reasonable bounds.

    Args:
        discount_rate: Discount rate as decimal (e.g., 0.055 for 5.5%)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(discount_rate, (int, float)):
        return False, "Discount rate must be a number"

    if discount_rate < 0:
        return False, "Discount rate cannot be negative"

    if discount_rate > 1.0:
        return False, "Discount rate appears to be entered as percentage (should be decimal, e.g., 0.055 not 5.5)"

    # Warn if unusual (but don't fail)
    if discount_rate > 0.25:
        logger.warning(f"Discount rate {discount_rate*100:.1f}% is unusually high")
    elif discount_rate < 0.01:
        logger.warning(f"Discount rate {discount_rate*100:.1f}% is unusually low")

    return True, None
