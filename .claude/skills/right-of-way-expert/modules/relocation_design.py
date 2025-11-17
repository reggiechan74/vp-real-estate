"""
Relocation Design Module
Generate relocation design requirements by utility type
"""

from typing import Dict, List, Any


def generate_relocation_requirements(
    conflicts: List[Dict[str, Any]],
    utilities: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Generate relocation requirements for conflicting utilities

    Args:
        conflicts: List of detected conflicts
        utilities: List of all utilities

    Returns:
        List of relocation requirement dictionaries
    """
    requirements = []

    # Get unique utilities that have conflicts
    conflicting_utilities = _get_conflicting_utilities(conflicts, utilities)

    for utility in conflicting_utilities:
        requirement = _generate_utility_relocation(utility, conflicts)
        requirements.append(requirement)

    return requirements


def _get_conflicting_utilities(
    conflicts: List[Dict[str, Any]],
    utilities: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Get list of utilities that have conflicts"""
    conflicting_ids = set()
    for conflict in conflicts:
        conflicting_ids.add(conflict['utility_id'])

    conflicting_utilities = []
    for utility in utilities:
        utility_id = utility.get('owner', 'Unknown') + ' - ' + utility.get('utility_type', 'Unknown')
        if utility_id in conflicting_ids:
            conflicting_utilities.append(utility)

    return conflicting_utilities


def _generate_utility_relocation(
    utility: Dict[str, Any],
    conflicts: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Generate relocation requirements for a single utility"""
    utility_type = utility.get('utility_type', 'Unknown')
    utility_id = utility.get('owner', 'Unknown') + ' - ' + utility_type

    # Get conflicts for this utility
    utility_conflicts = [c for c in conflicts if c['utility_id'] == utility_id]
    max_severity = _get_max_severity(utility_conflicts)

    # Get type-specific requirements
    if 'Transmission line' in utility_type:
        design_req = _transmission_line_relocation(utility, utility_conflicts)
    elif 'Distribution line' in utility_type:
        design_req = _distribution_line_relocation(utility, utility_conflicts)
    elif 'Gas' in utility_type:
        design_req = _gas_pipeline_relocation(utility, utility_conflicts)
    elif 'Water' in utility_type or 'sewer' in utility_type:
        design_req = _watermain_sewer_relocation(utility, utility_conflicts)
    elif 'Telecom' in utility_type or 'Fiber' in utility_type or 'Cable' in utility_type:
        design_req = _telecom_relocation(utility, utility_conflicts)
    else:
        design_req = _generic_relocation(utility, utility_conflicts)

    return {
        'utility_id': utility_id,
        'utility_type': utility_type,
        'owner': utility.get('owner'),
        'conflict_count': len(utility_conflicts),
        'max_severity': max_severity,
        'relocation_type': design_req['relocation_type'],
        'design_requirements': design_req['requirements'],
        'approval_agencies': design_req['approvals'],
        'estimated_duration': design_req['duration'],
        'critical_path_impact': design_req['critical_path']
    }


def _get_max_severity(conflicts: List[Dict[str, Any]]) -> str:
    """Get maximum severity from list of conflicts"""
    severity_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']

    for severity in severity_order:
        if any(c.get('severity') == severity for c in conflicts):
            return severity

    return 'LOW'


def _transmission_line_relocation(
    utility: Dict[str, Any],
    conflicts: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Relocation requirements for transmission lines"""
    voltage = utility.get('voltage', '115kV')

    if voltage == '500kV':
        duration = '24-36 months'
        critical_path = True
    elif voltage == '230kV':
        duration = '18-24 months'
        critical_path = True
    else:
        duration = '12-18 months'
        critical_path = True

    return {
        'relocation_type': 'Overhead transmission line relocation',
        'requirements': [
            f'{voltage} transmission line design and engineering',
            'Tower foundation design and geotechnical investigation',
            'Environmental assessment and approvals',
            'New right-of-way acquisition',
            'Clearance from adjacent properties and structures',
            'Protection and shoring during construction',
            'Temporary power arrangements during cutover',
            'Load transfer and system reliability studies'
        ],
        'approvals': [
            'Hydro One / utility owner engineering approval',
            'Ministry of Energy approvals',
            'Environmental Assessment Act compliance',
            'Municipal building permits',
            'IESO (Independent Electricity System Operator) approval',
            'Technical Standards and Safety Authority (TSSA)'
        ],
        'duration': duration,
        'critical_path': critical_path
    }


def _distribution_line_relocation(
    utility: Dict[str, Any],
    conflicts: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Relocation requirements for distribution lines"""
    return {
        'relocation_type': 'Distribution line relocation',
        'requirements': [
            'Distribution line design (overhead or underground)',
            'Pole/duct bank design',
            'Service connections rerouting',
            'Temporary power during relocation',
            'Coordination with customers for service interruption',
            'Protection of existing services during construction'
        ],
        'approvals': [
            'Local distribution company (LDC) approval',
            'Electrical Safety Authority (ESA) permits',
            'Municipal road occupancy permits',
            'Service interruption notices to customers'
        ],
        'duration': '6-12 months',
        'critical_path': True
    }


def _gas_pipeline_relocation(
    utility: Dict[str, Any],
    conflicts: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Relocation requirements for gas pipelines"""
    size = utility.get('size', 'Unknown')

    if 'high pressure' in size.lower() or 'transmission' in size.lower():
        duration = '12-18 months'
        critical_path = True
        requirements = [
            'High pressure gas pipeline design',
            'Pressure testing and integrity assessment',
            'Cathodic protection system design',
            'Emergency shutdown procedures',
            'Hot tap connections for tie-ins',
            'Pressure monitoring during construction'
        ]
    else:
        duration = '6-9 months'
        critical_path = False
        requirements = [
            'Gas distribution main design',
            'Service connections rerouting',
            'Pressure testing',
            'Cathodic protection',
            'Customer notifications'
        ]

    return {
        'relocation_type': 'Gas pipeline relocation',
        'requirements': requirements,
        'approvals': [
            'Enbridge Gas / utility owner approval',
            'Technical Standards and Safety Authority (TSSA) permits',
            'Ministry of Environment approval (if required)',
            'Municipal road occupancy permits',
            'Ontario One Call locates'
        ],
        'duration': duration,
        'critical_path': critical_path
    }


def _watermain_sewer_relocation(
    utility: Dict[str, Any],
    conflicts: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Relocation requirements for water mains and sewers"""
    utility_type = utility.get('utility_type', '')

    if 'Water' in utility_type:
        relocation_type = 'Watermain relocation'
        specific_requirements = [
            'Watermain hydraulic analysis',
            'Fire flow testing',
            'Pressure testing and disinfection',
            'Service connections relocation',
            'Valve and hydrant installation',
            'Temporary water supply during construction'
        ]
    else:
        relocation_type = 'Sewer relocation'
        specific_requirements = [
            'Sewer hydraulic capacity analysis',
            'Invert elevation design',
            'Manhole design and construction',
            'Service lateral connections',
            'CCTV inspection',
            'Temporary pumping if required'
        ]

    return {
        'relocation_type': relocation_type,
        'requirements': specific_requirements,
        'approvals': [
            'Municipality / Region engineering approval',
            'Ministry of Environment permits (if required)',
            'Road occupancy permits',
            'Watermain / sewer use by-law compliance'
        ],
        'duration': '4-8 months',
        'critical_path': False
    }


def _telecom_relocation(
    utility: Dict[str, Any],
    conflicts: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Relocation requirements for telecom infrastructure"""
    return {
        'relocation_type': 'Telecom infrastructure relocation',
        'requirements': [
            'Fiber optic / copper cable design',
            'Duct bank or conduit installation',
            'Splice vault locations',
            'Service interruption coordination',
            'Cable testing and certification',
            'As-built documentation'
        ],
        'approvals': [
            'Bell / Rogers / telecom owner approval',
            'Canadian Radio-television and Telecommunications Commission (CRTC) notification',
            'Municipal road occupancy permits',
            'Customer service interruption notices'
        ],
        'duration': '3-6 months',
        'critical_path': False
    }


def _generic_relocation(
    utility: Dict[str, Any],
    conflicts: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Generic relocation requirements for other utilities"""
    return {
        'relocation_type': 'Utility relocation',
        'requirements': [
            'Engineering design and drawings',
            'Protection or relocation plan',
            'Coordination with utility owner',
            'Construction methodology',
            'Quality assurance and testing'
        ],
        'approvals': [
            'Utility owner approval',
            'Municipal permits',
            'Ontario One Call locates'
        ],
        'duration': '3-6 months',
        'critical_path': False
    }
