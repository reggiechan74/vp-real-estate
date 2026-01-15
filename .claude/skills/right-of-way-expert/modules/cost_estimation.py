"""
Cost Estimation Module
Estimate relocation costs by utility type with ranges and contingencies
"""

from typing import Dict, List, Any, Tuple


def estimate_relocation_costs(
    relocation_requirements: List[Dict[str, Any]],
    utilities: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Estimate relocation costs for all utilities

    Args:
        relocation_requirements: List of relocation requirements
        utilities: List of utilities with technical details

    Returns:
        Cost estimate dictionary with ranges and breakdown
    """
    utility_costs = []
    total_low = 0
    total_high = 0

    for requirement in relocation_requirements:
        # Find matching utility for detailed specs
        utility = _find_utility(requirement['utility_id'], utilities)

        cost_estimate = _estimate_utility_cost(requirement, utility)
        utility_costs.append(cost_estimate)

        total_low += cost_estimate['cost_range']['low']
        total_high += cost_estimate['cost_range']['high']

    # Apply project contingency
    contingency_rate = 0.25  # 25% contingency for utility relocations

    return {
        'utility_costs': utility_costs,
        'subtotal_range': {
            'low': total_low,
            'high': total_high
        },
        'contingency': {
            'rate': contingency_rate,
            'low': total_low * contingency_rate,
            'high': total_high * contingency_rate
        },
        'total_range': {
            'low': total_low * (1 + contingency_rate),
            'high': total_high * (1 + contingency_rate)
        },
        'cost_breakdown': _generate_cost_breakdown(utility_costs)
    }


def _find_utility(utility_id: str, utilities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Find utility by ID"""
    for utility in utilities:
        uid = utility.get('owner', 'Unknown') + ' - ' + utility.get('utility_type', 'Unknown')
        if uid == utility_id:
            return utility
    return {}


def _estimate_utility_cost(
    requirement: Dict[str, Any],
    utility: Dict[str, Any]
) -> Dict[str, Any]:
    """Estimate cost for single utility relocation"""
    utility_type = requirement.get('utility_type', 'Unknown')

    if 'Transmission line' in utility_type:
        cost_range = _transmission_line_cost(utility)
    elif 'Distribution line' in utility_type:
        cost_range = _distribution_line_cost(utility)
    elif 'Gas' in utility_type:
        cost_range = _gas_pipeline_cost(utility)
    elif 'Water' in utility_type or 'sewer' in utility_type:
        cost_range = _watermain_sewer_cost(utility)
    elif 'Telecom' in utility_type or 'Fiber' in utility_type or 'Cable' in utility_type:
        cost_range = _telecom_cost(utility)
    else:
        cost_range = {'low': 50000, 'high': 150000, 'unit': 'lump sum'}

    return {
        'utility_id': requirement['utility_id'],
        'utility_type': utility_type,
        'owner': requirement.get('owner'),
        'cost_range': cost_range,
        'cost_drivers': _get_cost_drivers(utility_type),
        'assumptions': _get_cost_assumptions(utility_type)
    }


def _transmission_line_cost(utility: Dict[str, Any]) -> Dict[str, float]:
    """Cost estimate for transmission line relocation"""
    voltage = utility.get('voltage', '115kV')
    length_km = utility.get('relocation_length_km', 1.0)

    # Cost per km by voltage level
    cost_per_km = {
        '500kV': {'low': 2500000, 'high': 3500000},
        '230kV': {'low': 1500000, 'high': 2500000},
        '115kV': {'low': 800000, 'high': 1500000},
        '44kV': {'low': 600000, 'high': 1000000}
    }

    rates = cost_per_km.get(voltage, cost_per_km['115kV'])

    return {
        'low': rates['low'] * length_km,
        'high': rates['high'] * length_km,
        'unit': f'${rates["low"]:,.0f}-${rates["high"]:,.0f}/km',
        'length_km': length_km
    }


def _distribution_line_cost(utility: Dict[str, Any]) -> Dict[str, float]:
    """Cost estimate for distribution line relocation"""
    length_m = utility.get('relocation_length_m', 100)
    is_underground = utility.get('underground', False)

    if is_underground:
        cost_per_m = {'low': 800, 'high': 1500}
    else:
        cost_per_m = {'low': 400, 'high': 800}

    return {
        'low': cost_per_m['low'] * length_m,
        'high': cost_per_m['high'] * length_m,
        'unit': f'${cost_per_m["low"]}-${cost_per_m["high"]}/meter',
        'length_m': length_m,
        'configuration': 'Underground' if is_underground else 'Overhead'
    }


def _gas_pipeline_cost(utility: Dict[str, Any]) -> Dict[str, float]:
    """Cost estimate for gas pipeline relocation"""
    size = utility.get('size', 'Unknown')
    length_km = utility.get('relocation_length_km', 0.5)

    # Cost per km by pressure and size
    if 'high pressure' in size.lower() or 'transmission' in size.lower():
        cost_per_km = {'low': 600000, 'high': 1000000}
    elif 'medium pressure' in size.lower():
        cost_per_km = {'low': 300000, 'high': 600000}
    else:
        cost_per_km = {'low': 200000, 'high': 400000}

    return {
        'low': cost_per_km['low'] * length_km,
        'high': cost_per_km['high'] * length_km,
        'unit': f'${cost_per_km["low"]:,.0f}-${cost_per_km["high"]:,.0f}/km',
        'length_km': length_km
    }


def _watermain_sewer_cost(utility: Dict[str, Any]) -> Dict[str, float]:
    """Cost estimate for watermain or sewer relocation"""
    utility_type = utility.get('utility_type', '')
    length_m = utility.get('relocation_length_m', 100)
    diameter_mm = utility.get('diameter_mm', 300)

    # Base cost per meter by diameter
    if diameter_mm >= 600:
        cost_per_m = {'low': 600, 'high': 1200}
    elif diameter_mm >= 400:
        cost_per_m = {'low': 400, 'high': 800}
    elif diameter_mm >= 200:
        cost_per_m = {'low': 300, 'high': 600}
    else:
        cost_per_m = {'low': 250, 'high': 500}

    # Sewer is typically more expensive due to grade requirements
    if 'sewer' in utility_type.lower():
        cost_per_m['low'] = int(cost_per_m['low'] * 1.2)
        cost_per_m['high'] = int(cost_per_m['high'] * 1.2)

    return {
        'low': cost_per_m['low'] * length_m,
        'high': cost_per_m['high'] * length_m,
        'unit': f'${cost_per_m["low"]}-${cost_per_m["high"]}/meter',
        'length_m': length_m,
        'diameter_mm': diameter_mm
    }


def _telecom_cost(utility: Dict[str, Any]) -> Dict[str, float]:
    """Cost estimate for telecom relocation"""
    length_m = utility.get('relocation_length_m', 100)
    is_fiber = 'Fiber' in utility.get('utility_type', '')

    if is_fiber:
        cost_per_m = {'low': 300, 'high': 600}
    else:
        cost_per_m = {'low': 150, 'high': 300}

    return {
        'low': cost_per_m['low'] * length_m,
        'high': cost_per_m['high'] * length_m,
        'unit': f'${cost_per_m["low"]}-${cost_per_m["high"]}/meter',
        'length_m': length_m,
        'type': 'Fiber optic' if is_fiber else 'Copper/Coax'
    }


def _get_cost_drivers(utility_type: str) -> List[str]:
    """Get cost drivers for utility type"""
    if 'Transmission' in utility_type:
        return [
            'Voltage level and conductor size',
            'Tower foundation requirements',
            'Right-of-way acquisition costs',
            'Environmental mitigation',
            'Load transfer complexity'
        ]
    elif 'Gas' in utility_type:
        return [
            'Pipeline diameter and pressure rating',
            'Cathodic protection system',
            'Pressure testing requirements',
            'Hot tap connection complexity',
            'Service interruption costs'
        ]
    elif 'Water' in utility_type or 'sewer' in utility_type:
        return [
            'Pipe diameter and material',
            'Depth of burial',
            'Service connections',
            'Dewatering requirements',
            'Traffic management'
        ]
    elif 'Telecom' in utility_type or 'Fiber' in utility_type:
        return [
            'Duct bank vs. direct bury',
            'Number of cables/fibers',
            'Splice vault requirements',
            'Service interruption coordination',
            'Testing and certification'
        ]
    else:
        return [
            'Length of relocation',
            'Depth and location',
            'Construction access',
            'Owner coordination'
        ]


def _get_cost_assumptions(utility_type: str) -> List[str]:
    """Get cost assumptions for utility type"""
    common = [
        'Costs in 2025 Canadian dollars',
        'Assumes normal soil conditions',
        'Includes engineering, construction, and testing',
        'Excludes property acquisition costs'
    ]

    if 'Transmission' in utility_type:
        specific = [
            'Overhead construction (not underground)',
            'Standard tower spacing',
            'Normal conductor requirements'
        ]
    elif 'Gas' in utility_type:
        specific = [
            'Includes cathodic protection',
            'Standard depth of cover',
            'Normal pressure testing'
        ]
    else:
        specific = [
            'Standard construction methods',
            'Normal working hours'
        ]

    return common + specific


def _generate_cost_breakdown(utility_costs: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """Generate cost breakdown by owner"""
    breakdown = {}

    for cost in utility_costs:
        owner = cost.get('owner', 'Unknown')
        if owner not in breakdown:
            breakdown[owner] = {'low': 0, 'high': 0, 'count': 0}

        breakdown[owner]['low'] += cost['cost_range']['low']
        breakdown[owner]['high'] += cost['cost_range']['high']
        breakdown[owner]['count'] += 1

    return breakdown
