"""
Marketability Discount Module
Analyzes impact of encumbrances on property marketability and buyer pool
"""

from typing import Dict, List, Optional


def analyze_buyer_pool(
    property_data: Dict,
    encumbrances: List[Dict],
    individual_discounts: List[Dict]
) -> Dict:
    """
    Analyze impact on buyer pool and marketability.

    Encumbrances reduce buyer pool by:
    - Limiting financing options (lenders often discount encumbered properties)
    - Reducing developer interest (limits buildable area)
    - Creating uncertainty (easement terms, future use restrictions)
    - Reducing appeal to owner-occupants

    Args:
        property_data: Property details
        encumbrances: List of encumbrances
        individual_discounts: Calculated discounts

    Returns:
        Buyer pool analysis
    """
    total_area = property_data['total_area_acres']
    total_encumbered = sum(e['area_acres'] for e in encumbrances)
    encumbered_ratio = total_encumbered / total_area if total_area > 0 else 0

    # Assess buyer pool impact by encumbrance type
    buyer_pool_impacts = []
    has_major_encumbrance = False

    for enc in encumbrances:
        enc_type = enc['type']

        if enc_type in ['transmission_easement', 'pipeline_easement']:
            has_major_encumbrance = True
            buyer_pool_impacts.append({
                'type': enc_type,
                'impact_level': 'High',
                'description': 'Significant reduction in buyer pool - limits financing, development, and owner-occupant appeal'
            })

        elif enc_type == 'conservation_easement':
            has_major_encumbrance = True
            buyer_pool_impacts.append({
                'type': enc_type,
                'impact_level': 'Very High',
                'description': 'Severe buyer pool restriction - primarily conservation buyers'
            })

        elif enc_type in ['drainage_easement', 'access_easement']:
            buyer_pool_impacts.append({
                'type': enc_type,
                'impact_level': 'Low to Moderate',
                'description': 'Moderate reduction in buyer appeal, minimal financing impact'
            })

        else:
            buyer_pool_impacts.append({
                'type': enc_type,
                'impact_level': 'Moderate',
                'description': 'Some reduction in buyer pool and financing options'
            })

    # Determine overall buyer pool impact
    if has_major_encumbrance or encumbered_ratio > 0.25:
        overall_impact = 'High'
        buyer_pool_reduction_pct = 40  # 40% reduction in potential buyers
    elif encumbered_ratio > 0.10:
        overall_impact = 'Moderate'
        buyer_pool_reduction_pct = 20  # 20% reduction
    else:
        overall_impact = 'Low'
        buyer_pool_reduction_pct = 10  # 10% reduction

    return {
        'overall_impact': overall_impact,
        'buyer_pool_reduction_percentage': buyer_pool_reduction_pct,
        'encumbered_ratio': encumbered_ratio,
        'has_major_encumbrance': has_major_encumbrance,
        'buyer_pool_impacts': buyer_pool_impacts,
        'financing_impact': _assess_financing_impact(encumbrances, encumbered_ratio),
        'marketing_challenges': _identify_marketing_challenges(encumbrances, property_data)
    }


def calculate_marketability_discount(
    buyer_pool_analysis: Dict,
    base_value: float,
    method: str = 'conservative'
) -> Dict:
    """
    Calculate marketability discount based on buyer pool analysis.

    Marketability discount reflects:
    - Longer marketing time
    - Smaller buyer pool
    - Reduced financing options
    - Increased transaction uncertainty

    Args:
        buyer_pool_analysis: Buyer pool impact analysis
        base_value: Base property value (after encumbrance discounts)
        method: Calculation method
            'conservative' - Higher discount (default)
            'moderate' - Mid-range discount
            'optimistic' - Lower discount

    Returns:
        Marketability discount calculation
    """
    overall_impact = buyer_pool_analysis['overall_impact']
    buyer_pool_reduction = buyer_pool_analysis['buyer_pool_reduction_percentage']

    # Determine marketability discount range by impact level
    discount_ranges = {
        'Very High': {'conservative': 0.15, 'moderate': 0.12, 'optimistic': 0.08},
        'High': {'conservative': 0.10, 'moderate': 0.07, 'optimistic': 0.05},
        'Moderate': {'conservative': 0.05, 'moderate': 0.04, 'optimistic': 0.03},
        'Low': {'conservative': 0.03, 'moderate': 0.02, 'optimistic': 0.01}
    }

    # Get discount percentage
    discount_pct = discount_ranges.get(
        overall_impact,
        {'conservative': 0.05, 'moderate': 0.03, 'optimistic': 0.02}
    )[method]

    # Calculate discount amount
    discount_amount = base_value * discount_pct

    # Estimate time on market impact
    time_impact = _estimate_time_on_market(overall_impact)

    return {
        'method': method,
        'overall_impact': overall_impact,
        'discount_percentage': discount_pct * 100,
        'discount_amount': discount_amount,
        'adjusted_value': base_value - discount_amount,
        'buyer_pool_reduction_percentage': buyer_pool_reduction,
        'time_on_market_impact': time_impact,
        'method_comparison': {
            'conservative': {
                'discount_pct': discount_ranges[overall_impact]['conservative'] * 100,
                'discount_amount': base_value * discount_ranges[overall_impact]['conservative']
            },
            'moderate': {
                'discount_pct': discount_ranges[overall_impact]['moderate'] * 100,
                'discount_amount': base_value * discount_ranges[overall_impact]['moderate']
            },
            'optimistic': {
                'discount_pct': discount_ranges[overall_impact]['optimistic'] * 100,
                'discount_amount': base_value * discount_ranges[overall_impact]['optimistic']
            }
        }
    }


def _assess_financing_impact(
    encumbrances: List[Dict],
    encumbered_ratio: float
) -> Dict:
    """
    Assess impact on financing availability and terms.

    Args:
        encumbrances: List of encumbrances
        encumbered_ratio: Ratio of encumbered area to total

    Returns:
        Financing impact assessment
    """
    has_major_encumbrance = any(
        e['type'] in ['transmission_easement', 'pipeline_easement', 'conservation_easement']
        for e in encumbrances
    )

    if has_major_encumbrance or encumbered_ratio > 0.25:
        impact_level = 'High'
        ltv_reduction = 10  # 10% lower loan-to-value
        description = (
            'Significant financing challenges: Lower LTV ratios, higher interest rates, '
            'reduced lender pool, may require specialized lenders'
        )
    elif encumbered_ratio > 0.10:
        impact_level = 'Moderate'
        ltv_reduction = 5  # 5% lower LTV
        description = (
            'Moderate financing impact: Some lenders may reduce LTV, '
            'require additional documentation'
        )
    else:
        impact_level = 'Low'
        ltv_reduction = 0
        description = 'Minimal financing impact, most lenders will finance'

    return {
        'impact_level': impact_level,
        'ltv_reduction_percentage': ltv_reduction,
        'description': description,
        'typical_ltv_range': f'{75-ltv_reduction}-{80-ltv_reduction}%'
    }


def _identify_marketing_challenges(
    encumbrances: List[Dict],
    property_data: Dict
) -> List[str]:
    """
    Identify specific marketing challenges from encumbrances.

    Args:
        encumbrances: List of encumbrances
        property_data: Property details

    Returns:
        List of marketing challenge descriptions
    """
    challenges = []

    # Check for visibility issues
    has_transmission = any(e['type'] == 'transmission_easement' for e in encumbrances)
    if has_transmission:
        challenges.append(
            'Visual impact: Transmission towers/lines reduce aesthetic appeal'
        )

    # Check for safety concerns
    has_pipeline = any(e['type'] == 'pipeline_easement' for e in encumbrances)
    if has_pipeline:
        challenges.append(
            'Safety perception: Pipeline easements raise buyer safety concerns'
        )

    # Check for use restrictions
    has_conservation = any(e['type'] == 'conservation_easement' for e in encumbrances)
    if has_conservation:
        challenges.append(
            'Severe use restrictions: Conservation easements limit buyer universe to conservation-minded purchasers'
        )

    # General marketability challenges
    total_encumbered = sum(e['area_acres'] for e in encumbrances)
    total_area = property_data['total_area_acres']
    encumbered_ratio = total_encumbered / total_area if total_area > 0 else 0

    if encumbered_ratio > 0.20:
        challenges.append(
            f'Significant encumbered area: {encumbered_ratio*100:.1f}% of property affected'
        )

    if len(encumbrances) > 2:
        challenges.append(
            f'Multiple encumbrances: {len(encumbrances)} separate easements complicate due diligence'
        )

    # Financing challenges
    challenges.append(
        'Reduced financing options: Not all lenders accept encumbered properties'
    )

    # Disclosure requirements
    challenges.append(
        'Enhanced disclosure requirements: Easement terms must be fully disclosed'
    )

    return challenges


def _estimate_time_on_market(overall_impact: str) -> Dict:
    """
    Estimate time on market impact from marketability issues.

    Args:
        overall_impact: Overall marketability impact level

    Returns:
        Time on market estimation
    """
    time_ranges = {
        'Very High': {
            'baseline_days': 120,
            'additional_days': 180,
            'total_days': 300,
            'description': 'Significantly extended marketing period (6-12+ months)'
        },
        'High': {
            'baseline_days': 90,
            'additional_days': 90,
            'total_days': 180,
            'description': 'Extended marketing period (4-6 months)'
        },
        'Moderate': {
            'baseline_days': 90,
            'additional_days': 30,
            'total_days': 120,
            'description': 'Moderately extended marketing period (3-4 months)'
        },
        'Low': {
            'baseline_days': 90,
            'additional_days': 0,
            'total_days': 90,
            'description': 'Normal marketing period (2-3 months)'
        }
    }

    return time_ranges.get(
        overall_impact,
        time_ranges['Moderate']
    )
