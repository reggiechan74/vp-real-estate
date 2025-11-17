"""
Conflict Detection Module
Geometric conflict detection and severity classification for utility conflicts
"""

from typing import Dict, List, Any, Tuple
import math


class ConflictSeverity:
    """Conflict severity levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ConflictType:
    """Types of utility conflicts"""
    HORIZONTAL_CLEARANCE = "Horizontal clearance violation"
    VERTICAL_CLEARANCE = "Vertical clearance violation"
    PROTECTION_ZONE = "Protection zone encroachment"
    CROSSING = "Direct crossing/intersection"
    PARALLEL_PROXIMITY = "Parallel proximity conflict"


def calculate_distance(point1: Dict[str, float], point2: Dict[str, float]) -> float:
    """
    Calculate Euclidean distance between two points

    Args:
        point1: Dictionary with x, y coordinates
        point2: Dictionary with x, y coordinates

    Returns:
        Distance in meters
    """
    dx = point1['x'] - point2['x']
    dy = point1['y'] - point2['y']
    return math.sqrt(dx**2 + dy**2)


def detect_conflicts(
    project_alignment: Dict[str, Any],
    utilities: List[Dict[str, Any]],
    design_constraints: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Detect geometric conflicts between project and existing utilities

    Args:
        project_alignment: Project alignment data
        utilities: List of existing utilities
        design_constraints: Design clearance requirements

    Returns:
        List of conflict dictionaries
    """
    conflicts = []

    project_location = project_alignment.get('location', {})
    h_clearance_min = design_constraints.get('horizontal_clearance_min', 5.0)
    v_clearance_min = design_constraints.get('vertical_clearance_min', 3.0)
    protection_zone = design_constraints.get('protection_zone_width', 10.0)

    for utility in utilities:
        utility_conflicts = _check_utility_conflicts(
            utility,
            project_location,
            h_clearance_min,
            v_clearance_min,
            protection_zone
        )
        conflicts.extend(utility_conflicts)

    return conflicts


def _check_utility_conflicts(
    utility: Dict[str, Any],
    project_location: Dict[str, Any],
    h_clearance_min: float,
    v_clearance_min: float,
    protection_zone: float
) -> List[Dict[str, Any]]:
    """Check conflicts for a single utility"""
    conflicts = []

    utility_location = utility.get('location', {})

    # Calculate horizontal distance
    if 'x' in project_location and 'x' in utility_location:
        h_distance = calculate_distance(project_location, utility_location)

        # Check horizontal clearance
        if h_distance < h_clearance_min:
            conflicts.append({
                'utility_id': utility.get('owner', 'Unknown') + ' - ' + utility.get('utility_type', 'Unknown'),
                'utility_type': utility.get('utility_type'),
                'owner': utility.get('owner'),
                'conflict_type': ConflictType.HORIZONTAL_CLEARANCE,
                'distance': h_distance,
                'required_clearance': h_clearance_min,
                'shortfall': h_clearance_min - h_distance,
                'severity': None  # Will be set by classify_severity
            })

        # Check protection zone
        protection_required = _get_protection_zone_width(utility)
        if h_distance < protection_required:
            conflicts.append({
                'utility_id': utility.get('owner', 'Unknown') + ' - ' + utility.get('utility_type', 'Unknown'),
                'utility_type': utility.get('utility_type'),
                'owner': utility.get('owner'),
                'conflict_type': ConflictType.PROTECTION_ZONE,
                'distance': h_distance,
                'required_clearance': protection_required,
                'shortfall': protection_required - h_distance,
                'severity': None
            })

    # Check vertical clearance for buried utilities
    if 'depth' in utility and 'excavation_depth' in project_location:
        v_distance = abs(utility['depth'] - project_location['excavation_depth'])

        if v_distance < v_clearance_min:
            conflicts.append({
                'utility_id': utility.get('owner', 'Unknown') + ' - ' + utility.get('utility_type', 'Unknown'),
                'utility_type': utility.get('utility_type'),
                'owner': utility.get('owner'),
                'conflict_type': ConflictType.VERTICAL_CLEARANCE,
                'distance': v_distance,
                'required_clearance': v_clearance_min,
                'shortfall': v_clearance_min - v_distance,
                'severity': None
            })

    # Check overhead clearance for transmission lines
    if utility.get('utility_type') in ['Transmission line', 'Distribution line']:
        clearance_required = utility.get('clearance_required', 10.0)
        project_height = project_location.get('height', 0)

        if project_height > 0:
            # Simplified - assumes utility at fixed height
            utility_height = utility.get('height', 20.0)
            v_clearance = abs(utility_height - project_height)

            if v_clearance < clearance_required:
                conflicts.append({
                    'utility_id': utility.get('owner', 'Unknown') + ' - ' + utility.get('utility_type', 'Unknown'),
                    'utility_type': utility.get('utility_type'),
                    'owner': utility.get('owner'),
                    'conflict_type': ConflictType.VERTICAL_CLEARANCE,
                    'distance': v_clearance,
                    'required_clearance': clearance_required,
                    'shortfall': clearance_required - v_clearance,
                    'severity': None
                })

    # Classify severity for all conflicts
    for conflict in conflicts:
        conflict['severity'] = classify_severity(conflict, utility)

    return conflicts


def _get_protection_zone_width(utility: Dict[str, Any]) -> float:
    """
    Get required protection zone width based on utility type

    Args:
        utility: Utility dictionary

    Returns:
        Protection zone width in meters
    """
    utility_type = utility.get('utility_type', '')

    # High pressure gas and transmission lines need larger zones
    if 'Transmission' in utility_type or 'High pressure' in utility.get('size', ''):
        return 30.0
    elif 'Gas' in utility_type:
        return 15.0
    elif utility_type in ['Transmission line', 'Distribution line']:
        voltage = utility.get('voltage', '')
        if '500kV' in voltage:
            return 50.0
        elif '230kV' in voltage:
            return 30.0
        elif '115kV' in voltage:
            return 20.0
        else:
            return 15.0
    elif 'Water main' in utility_type or 'sewer' in utility_type:
        return 10.0
    else:
        return 5.0


def classify_severity(conflict: Dict[str, Any], utility: Dict[str, Any]) -> str:
    """
    Classify conflict severity based on utility type and clearance shortfall

    Args:
        conflict: Conflict dictionary
        utility: Utility dictionary

    Returns:
        Severity level (CRITICAL/HIGH/MEDIUM/LOW)
    """
    utility_type = utility.get('utility_type', '')
    shortfall = conflict.get('shortfall', 0)
    conflict_type = conflict.get('conflict_type', '')

    # CRITICAL: High-risk utilities with significant conflicts
    critical_utilities = ['Transmission line', 'Gas main']
    if any(critical in utility_type for critical in critical_utilities):
        if shortfall > 5.0 or conflict_type == ConflictType.CROSSING:
            return ConflictSeverity.CRITICAL
        elif shortfall > 2.0:
            return ConflictSeverity.HIGH

    # HIGH: Medium-risk utilities or significant clearance violations
    high_risk_utilities = ['Distribution line', 'Gas service', 'Water main']
    if any(high_risk in utility_type for high_risk in high_risk_utilities):
        if shortfall > 3.0:
            return ConflictSeverity.HIGH
        elif shortfall > 1.0:
            return ConflictSeverity.MEDIUM

    # MEDIUM: Moderate conflicts or low-risk utilities
    if shortfall > 2.0:
        return ConflictSeverity.MEDIUM

    # LOW: Minor clearance violations
    return ConflictSeverity.LOW


def generate_conflict_matrix(conflicts: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
    """
    Generate conflict summary matrix by utility owner and severity

    Args:
        conflicts: List of conflicts

    Returns:
        Matrix dictionary with counts by owner and severity
    """
    matrix = {}

    for conflict in conflicts:
        owner = conflict.get('owner', 'Unknown')
        severity = conflict.get('severity', 'UNKNOWN')

        if owner not in matrix:
            matrix[owner] = {
                'CRITICAL': 0,
                'HIGH': 0,
                'MEDIUM': 0,
                'LOW': 0,
                'total': 0
            }

        matrix[owner][severity] = matrix[owner].get(severity, 0) + 1
        matrix[owner]['total'] += 1

    return matrix


def get_conflicts_by_severity(conflicts: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group conflicts by severity level

    Args:
        conflicts: List of conflicts

    Returns:
        Dictionary with conflicts grouped by severity
    """
    grouped = {
        ConflictSeverity.CRITICAL: [],
        ConflictSeverity.HIGH: [],
        ConflictSeverity.MEDIUM: [],
        ConflictSeverity.LOW: []
    }

    for conflict in conflicts:
        severity = conflict.get('severity', ConflictSeverity.LOW)
        grouped[severity].append(conflict)

    return grouped


def get_conflicts_by_owner(conflicts: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group conflicts by utility owner

    Args:
        conflicts: List of conflicts

    Returns:
        Dictionary with conflicts grouped by owner
    """
    grouped = {}

    for conflict in conflicts:
        owner = conflict.get('owner', 'Unknown')
        if owner not in grouped:
            grouped[owner] = []
        grouped[owner].append(conflict)

    return grouped
