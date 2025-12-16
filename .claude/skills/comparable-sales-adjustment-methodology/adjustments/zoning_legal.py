"""
Comparable Sales Adjustment Module
Auto-extracted from comparable_sales_calculator.py
"""

from typing import Dict, List

def calculate_adjustments(
    subject: Dict,
    comparable: Dict,
    base_price: float,
    market_params: Dict,
    property_type: str = 'industrial'
) -> List[Dict]:
    """
    Zoning and Legal Adjustments (5 subcategories)

    Args:
        subject: Subject property characteristics
        comparable: Comparable sale characteristics
        base_price: Base price after previous adjustments
        market_params: Market parameters for adjustments

    Returns:
        List of adjustment dictionaries
    """
    adjustments = []

    # =========================================================================
    # ZONING / LEGAL (5 subcategories)
    # =========================================================================
    
    # 45. ZONING CLASSIFICATION
    # This is highly market-specific, using permitted use value mapping
    zoning_value_map = market_params.get('zoning_value_map', {})
    
    subject_zoning = subject.get('zoning', '')
    comp_zoning = comparable.get('zoning', '')
    
    if subject_zoning and comp_zoning and subject_zoning != comp_zoning:
        subject_zoning_value_pct = zoning_value_map.get(subject_zoning, 0)
        comp_zoning_value_pct = zoning_value_map.get(comp_zoning, 0)
    
        if subject_zoning_value_pct != comp_zoning_value_pct:
            zoning_adjustment_pct = subject_zoning_value_pct - comp_zoning_value_pct
            zoning_adjustment = base_price * (zoning_adjustment_pct / 100)
    
            adjustments.append({
                'category': 'Zoning/Legal',
                'characteristic': 'Zoning Classification',
                'subject_value': subject_zoning,
                'comp_value': comp_zoning,
                'adjustment': zoning_adjustment,
                'explanation': f'Zoning value differential: {zoning_adjustment_pct:+.1f}%'
            })
    
    # 46. FLOOR AREA RATIO (FAR) / DEVELOPMENT POTENTIAL
    subject_far = subject.get('floor_area_ratio', 0)
    comp_far = comparable.get('floor_area_ratio', 0)

    if subject_far > 0 and comp_far > 0:
        far_diff = subject_far - comp_far

        # Higher FAR = more development potential
        # Value: Market-dependent, typically $5-$15/sf of additional buildable area
        far_value_per_buildable_sf = market_params.get('far_value_per_buildable_sf', 10.0)

        # Calculate additional buildable area based on lot size
        # FIX: Get lot_size_acres from subject property (was undefined)
        subject_lot_acres = subject.get('lot_size_acres', 0)
        if subject_lot_acres > 0:
            subject_lot_sf = subject_lot_acres * 43560
            additional_buildable_sf = far_diff * subject_lot_sf

            far_adjustment = additional_buildable_sf * far_value_per_buildable_sf

            adjustments.append({
                'category': 'Zoning/Legal',
                'characteristic': 'Floor Area Ratio',
                'subject_value': f'{subject_far:.2f} FAR',
                'comp_value': f'{comp_far:.2f} FAR',
                'adjustment': far_adjustment,
                'explanation': f'{far_diff:+.2f} FAR × {subject_lot_sf:,.0f} sf lot × ${far_value_per_buildable_sf}/sf buildable'
            })
    
    # 47. VARIANCE / SPECIAL USE PERMIT
    subject_variance = subject.get('has_variance', False)
    comp_variance = comparable.get('has_variance', False)
    
    if subject_variance != comp_variance:
        # Variance value: Depends on what it permits
        # Typical: 5-15% premium if variance enables profitable use
        variance_premium_pct = market_params.get('variance_premium_pct', 8.0)
        variance_adjustment = base_price * (variance_premium_pct / 100)
    
        if not subject_variance:  # Comparable has variance, subject doesn't
            variance_adjustment = -variance_adjustment
    
    
        adjustments.append({
            'category': 'Zoning/Legal',
            'characteristic': 'Variance/Special Permit',
            'subject_value': 'Yes' if subject_variance else 'No',
            'comp_value': 'Yes' if comp_variance else 'No',
            'adjustment': variance_adjustment,
            'explanation': f'Variance premium: {variance_premium_pct}% of property value'
        })
    
    # 48. NON-CONFORMING USE (Grandfathered)
    subject_nonconforming = subject.get('non_conforming_use', False)
    comp_nonconforming = comparable.get('non_conforming_use', False)
    
    if subject_nonconforming != comp_nonconforming:
        # Non-conforming use: Can be premium or penalty depending on market
        # If profitable use: Premium (can't be replicated)
        # If limiting: Penalty (restricts future use)
        nonconforming_adjustment_pct = market_params.get('nonconforming_use_adjustment_pct', 5.0)  # Can be positive or negative
    
        nonconforming_adjustment = base_price * (nonconforming_adjustment_pct / 100)
    
        if not subject_nonconforming:  # Comparable has non-conforming, subject doesn't
            nonconforming_adjustment = -nonconforming_adjustment
    
    
        adjustments.append({
            'category': 'Zoning/Legal',
            'characteristic': 'Non-Conforming Use',
            'subject_value': 'Yes' if subject_nonconforming else 'No',
            'comp_value': 'Yes' if comp_nonconforming else 'No',
            'adjustment': nonconforming_adjustment,
            'explanation': f'Non-conforming use adjustment: {nonconforming_adjustment_pct:+.1f}%'
        })
    
    # 49. LOT COVERAGE / BUILDING COVERAGE RATIO
    subject_coverage = subject.get('lot_coverage_pct', 0)
    comp_coverage = comparable.get('lot_coverage_pct', 0)
    
    if subject_coverage > 0 and comp_coverage > 0:
        coverage_diff = subject_coverage - comp_coverage
    
        # Higher existing coverage = less future expansion potential
        # But also = more current improvements
        # Net effect: Depends on market demand for expansion vs. current use
        # Typically minor adjustment unless extreme difference
    
        if abs(coverage_diff) >= 15:  # Material difference (>15%)
            # If subject has significantly more coverage: Minor premium for current improvements
            # If comp has more coverage: Adjust for lack of expansion in comparable
            coverage_adjustment_pct = (coverage_diff / 10) * 0.5  # 0.5% per 10% coverage
    
            coverage_adjustment = base_price * (coverage_adjustment_pct / 100)
    
            adjustments.append({
                'category': 'Zoning/Legal',
                'characteristic': 'Lot Coverage',
                'subject_value': f'{subject_coverage}% covered',
                'comp_value': f'{comp_coverage}% covered',
                'adjustment': coverage_adjustment,
                'explanation': f'Lot coverage differential: {coverage_diff:+}% ({coverage_adjustment_pct:+.1f}% value impact)'
            })

    return adjustments
