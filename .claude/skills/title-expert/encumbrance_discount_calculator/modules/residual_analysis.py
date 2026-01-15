"""
Residual Development Potential Analysis Module
Analyzes how encumbrances affect future development potential and land value
"""

from typing import Dict, List, Optional


def analyze_development_potential(
    property_data: Dict,
    encumbrances: List[Dict],
    individual_discounts: List[Dict]
) -> Dict:
    """
    Analyze impact of encumbrances on development potential.

    Encumbrances can limit:
    - Buildable area
    - Subdivision potential
    - Access and circulation
    - Marketability to developers

    Args:
        property_data: Property details (zoning, size, HBU)
        encumbrances: List of encumbrances
        individual_discounts: Calculated individual discounts

    Returns:
        Development potential analysis
    """
    total_area = property_data['total_area_acres']
    zoning = property_data.get('zoning', 'Unknown')
    hbu = property_data.get('highest_best_use', 'Unknown')

    # Calculate total encumbered area
    total_encumbered_area = sum(e['area_acres'] for e in encumbrances)
    encumbered_ratio = total_encumbered_area / total_area if total_area > 0 else 0

    # Calculate effective buildable area
    # Some encumbrances (like underground utilities) may not prevent building
    # Others (like transmission easements) typically prohibit structures
    restricted_area = 0
    for enc in encumbrances:
        enc_type = enc['type']
        enc_area = enc['area_acres']

        # Estimate building restrictions by type
        if enc_type in ['transmission_easement', 'pipeline_easement']:
            restricted_area += enc_area  # Full restriction
        elif enc_type in ['drainage_easement', 'access_easement']:
            restricted_area += enc_area * 0.5  # Partial restriction
        elif enc_type == 'conservation_easement':
            restricted_area += enc_area  # Full restriction
        elif enc_type == 'telecom_easement':
            restricted_area += enc_area * 0.3  # Minimal restriction

    effective_buildable_area = total_area - restricted_area
    buildable_ratio = effective_buildable_area / total_area if total_area > 0 else 0

    # Assess subdivision impact
    subdivision_impact = _assess_subdivision_impact(
        total_area,
        encumbrances,
        property_data
    )

    # Assess access and circulation
    access_impact = _assess_access_impact(encumbrances)

    return {
        'total_area_acres': total_area,
        'encumbered_area_acres': total_encumbered_area,
        'encumbered_ratio': encumbered_ratio,
        'restricted_buildable_area_acres': restricted_area,
        'effective_buildable_area_acres': effective_buildable_area,
        'buildable_ratio': buildable_ratio,
        'zoning': zoning,
        'highest_best_use': hbu,
        'subdivision_impact': subdivision_impact,
        'access_impact': access_impact,
        'development_constraints': _identify_development_constraints(
            encumbrances,
            property_data
        )
    }


def calculate_residual_value(
    unencumbered_value: float,
    development_potential: Dict,
    cumulative_discount: Dict
) -> Dict:
    """
    Calculate residual land value after accounting for encumbrances.

    Uses residual method:
    Residual Value = Unencumbered Value × (1 - Cumulative Discount) × Development Factor

    Args:
        unencumbered_value: Fee simple value without encumbrances
        development_potential: Development analysis results
        cumulative_discount: Cumulative discount calculation

    Returns:
        Residual value analysis
    """
    # Base residual value (after encumbrance discounts)
    value_multiplier = cumulative_discount['value_multiplier']
    base_residual = unencumbered_value * value_multiplier

    # Development potential adjustment
    buildable_ratio = development_potential['buildable_ratio']
    development_multiplier = 0.8 + (0.2 * buildable_ratio)  # 80-100% range

    # Final residual value
    final_residual = base_residual * development_multiplier

    # Calculate total discount
    total_discount_amount = unencumbered_value - final_residual
    total_discount_pct = (total_discount_amount / unencumbered_value * 100) if unencumbered_value > 0 else 0

    return {
        'unencumbered_value': unencumbered_value,
        'base_residual_value': base_residual,
        'development_multiplier': development_multiplier,
        'final_residual_value': final_residual,
        'total_discount_amount': total_discount_amount,
        'total_discount_percentage': total_discount_pct,
        'breakdown': {
            'encumbrance_discount': cumulative_discount['cumulative_discount_percentage'],
            'development_adjustment': (1 - development_multiplier) * 100,
            'total_discount': total_discount_pct
        }
    }


def _assess_subdivision_impact(
    total_area: float,
    encumbrances: List[Dict],
    property_data: Dict
) -> Dict:
    """
    Assess how encumbrances affect subdivision potential.

    Args:
        total_area: Total property area
        encumbrances: List of encumbrances
        property_data: Property details

    Returns:
        Subdivision impact assessment
    """
    # Check if encumbrances bisect the property
    has_linear_encumbrance = any(
        e['type'] in ['transmission_easement', 'pipeline_easement', 'drainage_easement']
        for e in encumbrances
    )

    # Estimate number of potential lots
    # Assume 1 acre minimum lot size (adjust based on zoning)
    max_potential_lots = int(total_area) if total_area > 1 else 1

    # Reduce by encumbered area
    total_encumbered = sum(e['area_acres'] for e in encumbrances)
    effective_subdividable_area = total_area - total_encumbered

    estimated_lots_with_encumbrance = int(effective_subdividable_area) if effective_subdividable_area > 1 else 1

    # Calculate subdivision impact
    lot_reduction = max_potential_lots - estimated_lots_with_encumbrance
    lot_reduction_pct = (lot_reduction / max_potential_lots * 100) if max_potential_lots > 0 else 0

    return {
        'max_potential_lots': max_potential_lots,
        'estimated_lots_with_encumbrance': estimated_lots_with_encumbrance,
        'lot_reduction': lot_reduction,
        'lot_reduction_percentage': lot_reduction_pct,
        'has_linear_encumbrance': has_linear_encumbrance,
        'subdivision_feasibility': 'Limited' if has_linear_encumbrance else 'Moderate'
    }


def _assess_access_impact(encumbrances: List[Dict]) -> Dict:
    """
    Assess impact on property access and circulation.

    Args:
        encumbrances: List of encumbrances

    Returns:
        Access impact assessment
    """
    has_access_easement = any(e['type'] == 'access_easement' for e in encumbrances)
    has_linear_restriction = any(
        e['type'] in ['transmission_easement', 'pipeline_easement', 'drainage_easement']
        for e in encumbrances
    )

    # Assess circulation impact
    if has_access_easement:
        impact_level = 'Moderate'
        description = 'Access easement may restrict ingress/egress options'
    elif has_linear_restriction:
        impact_level = 'Low to Moderate'
        description = 'Linear encumbrances may affect internal circulation'
    else:
        impact_level = 'Low'
        description = 'Minimal impact on access and circulation'

    return {
        'has_access_easement': has_access_easement,
        'has_linear_restriction': has_linear_restriction,
        'impact_level': impact_level,
        'description': description
    }


def _identify_development_constraints(
    encumbrances: List[Dict],
    property_data: Dict
) -> List[str]:
    """
    Identify specific development constraints from encumbrances.

    Args:
        encumbrances: List of encumbrances
        property_data: Property details

    Returns:
        List of development constraint descriptions
    """
    constraints = []

    for enc in encumbrances:
        enc_type = enc['type']
        enc_area = enc['area_acres']

        if enc_type == 'transmission_easement':
            voltage = enc.get('voltage', 'Unknown')
            constraints.append(
                f"Transmission easement ({voltage}): No structures permitted, "
                f"electromagnetic field concerns, reduced buildable area by {enc_area:.2f} acres"
            )

        elif enc_type == 'pipeline_easement':
            constraints.append(
                f"Pipeline easement: No structures or deep excavation permitted, "
                f"safety setbacks required, reduced buildable area by {enc_area:.2f} acres"
            )

        elif enc_type == 'conservation_easement':
            constraints.append(
                f"Conservation easement: Severe development restrictions, "
                f"{enc_area:.2f} acres restricted from development"
            )

        elif enc_type == 'drainage_easement':
            constraints.append(
                f"Drainage easement: Limited building restrictions, "
                f"access required for maintenance, affects {enc_area:.2f} acres"
            )

        elif enc_type == 'access_easement':
            constraints.append(
                f"Access easement: Shared access rights may limit control, "
                f"affects {enc_area:.2f} acres"
            )

    return constraints
