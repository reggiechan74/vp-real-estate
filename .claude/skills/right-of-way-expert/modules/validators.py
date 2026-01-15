"""
Input Validation Module
Validates utility conflict analyzer input data structure and values
"""

from typing import Dict, List, Any, Tuple
import json


VALID_UTILITY_TYPES = [
    'Gas main', 'Gas service', 'Transmission line', 'Distribution line',
    'Water main', 'Water service', 'Sanitary sewer', 'Storm sewer',
    'Telecom conduit', 'Fiber optic', 'Cable TV', 'Street lighting',
    'Traffic signal', 'Hydro vault', 'Gas valve', 'Water valve'
]

VALID_PROJECT_TYPES = [
    'transit_station', 'transit_corridor', 'highway_expansion',
    'pipeline', 'transmission_line', 'building_foundation',
    'underground_parking', 'tunnel', 'subway'
]

VOLTAGE_LEVELS = ['44kV', '115kV', '230kV', '500kV']
GAS_PRESSURE_LEVELS = ['Low pressure', 'Medium pressure', 'High pressure', 'Transmission']


def validate_input_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate utility conflict analyzer input data

    Args:
        data: Input data dictionary

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Required top-level keys
    required_keys = ['project_alignment', 'existing_utilities']
    for key in required_keys:
        if key not in data:
            errors.append(f"Missing required key: {key}")

    if errors:
        return False, errors

    # Validate project_alignment
    errors.extend(_validate_project_alignment(data.get('project_alignment', {})))

    # Validate existing_utilities
    errors.extend(_validate_utilities(data.get('existing_utilities', [])))

    # Validate design_constraints (optional but validate if present)
    if 'design_constraints' in data:
        errors.extend(_validate_design_constraints(data['design_constraints']))

    return len(errors) == 0, errors


def _validate_project_alignment(alignment: Dict[str, Any]) -> List[str]:
    """Validate project alignment data"""
    errors = []

    if not isinstance(alignment, dict):
        errors.append("project_alignment must be a dictionary")
        return errors

    # Required fields
    if 'type' not in alignment:
        errors.append("project_alignment missing 'type'")
    elif alignment['type'] not in VALID_PROJECT_TYPES:
        errors.append(f"Invalid project type: {alignment['type']}. Must be one of {VALID_PROJECT_TYPES}")

    if 'location' not in alignment:
        errors.append("project_alignment missing 'location'")
    elif not isinstance(alignment['location'], dict):
        errors.append("project_alignment 'location' must be a dictionary")

    return errors


def _validate_utilities(utilities: List[Dict[str, Any]]) -> List[str]:
    """Validate existing utilities list"""
    errors = []

    if not isinstance(utilities, list):
        errors.append("existing_utilities must be a list")
        return errors

    if len(utilities) == 0:
        errors.append("existing_utilities cannot be empty")
        return errors

    for idx, utility in enumerate(utilities):
        if not isinstance(utility, dict):
            errors.append(f"Utility {idx} must be a dictionary")
            continue

        # Required fields
        if 'utility_type' not in utility:
            errors.append(f"Utility {idx} missing 'utility_type'")
        elif utility['utility_type'] not in VALID_UTILITY_TYPES:
            errors.append(f"Utility {idx} has invalid type: {utility['utility_type']}")

        if 'owner' not in utility:
            errors.append(f"Utility {idx} missing 'owner'")

        if 'location' not in utility:
            errors.append(f"Utility {idx} missing 'location'")
        elif not isinstance(utility['location'], dict):
            errors.append(f"Utility {idx} 'location' must be a dictionary")
        else:
            # Validate location coordinates
            loc = utility['location']
            if 'x' not in loc or 'y' not in loc:
                errors.append(f"Utility {idx} location missing x or y coordinates")
            else:
                if not isinstance(loc['x'], (int, float)):
                    errors.append(f"Utility {idx} location x must be numeric")
                if not isinstance(loc['y'], (int, float)):
                    errors.append(f"Utility {idx} location y must be numeric")

        # Validate type-specific fields
        if utility.get('utility_type') == 'Transmission line':
            if 'voltage' in utility and utility['voltage'] not in VOLTAGE_LEVELS:
                errors.append(f"Utility {idx} has invalid voltage: {utility['voltage']}")
            if 'clearance_required' in utility:
                if not isinstance(utility['clearance_required'], (int, float)) or utility['clearance_required'] < 0:
                    errors.append(f"Utility {idx} clearance_required must be positive number")

        if 'Gas' in utility.get('utility_type', ''):
            if 'size' in utility and not isinstance(utility['size'], str):
                errors.append(f"Utility {idx} size must be string")

        # Validate depth if present
        if 'depth' in utility:
            if not isinstance(utility['depth'], (int, float)) or utility['depth'] < 0:
                errors.append(f"Utility {idx} depth must be positive number")

    return errors


def _validate_design_constraints(constraints: Dict[str, Any]) -> List[str]:
    """Validate design constraints"""
    errors = []

    if not isinstance(constraints, dict):
        errors.append("design_constraints must be a dictionary")
        return errors

    # Validate numeric constraints
    numeric_fields = [
        'horizontal_clearance_min',
        'vertical_clearance_min',
        'protection_zone_width'
    ]

    for field in numeric_fields:
        if field in constraints:
            value = constraints[field]
            if not isinstance(value, (int, float)) or value < 0:
                errors.append(f"design_constraints.{field} must be positive number")

    return errors


def validate_utility_location(location: Dict[str, Any]) -> bool:
    """
    Validate utility location coordinates

    Args:
        location: Location dictionary with x, y coordinates

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(location, dict):
        return False

    required_fields = ['x', 'y']
    for field in required_fields:
        if field not in location:
            return False
        if not isinstance(location[field], (int, float)):
            return False

    return True


def sanitize_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize and normalize input data

    Args:
        data: Raw input data

    Returns:
        Sanitized data dictionary
    """
    sanitized = data.copy()

    # Set default design constraints if not provided
    if 'design_constraints' not in sanitized:
        sanitized['design_constraints'] = {
            'horizontal_clearance_min': 5.0,
            'vertical_clearance_min': 3.0,
            'protection_zone_width': 10.0
        }

    # Normalize utility types (title case)
    if 'existing_utilities' in sanitized:
        for utility in sanitized['existing_utilities']:
            if 'utility_type' in utility:
                utility['utility_type'] = utility['utility_type'].strip()

    return sanitized
