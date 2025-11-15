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
    Land Characteristics Adjustments (8 subcategories)

    Args:
        subject: Subject property characteristics
        comparable: Comparable sale characteristics
        base_price: Base price after previous adjustments
        market_params: Market parameters for adjustments

    Returns:
        List of adjustment dictionaries
    """
    adjustments = []

    # 1. LOT SIZE / LAND AREA
    subject_lot_acres = subject.get('lot_size_acres', 0)
    comp_lot_acres = comparable.get('lot_size_acres', 0)
    
    if subject_lot_acres > 0 and comp_lot_acres > 0:
        lot_diff_acres = subject_lot_acres - comp_lot_acres
    
        # Economies of scale: larger parcels have lower $/acre
        lot_adjustment_per_acre = market_params.get('lot_adjustment_per_acre', 15000)
    
        lot_adjustment = lot_diff_acres * lot_adjustment_per_acre
    
        adjustments.append({
            'category': 'Land',
            'characteristic': 'Lot Size',
            'subject_value': f'{subject_lot_acres:.2f} acres',
            'comp_value': f'{comp_lot_acres:.2f} acres',
            'adjustment': lot_adjustment,
            'explanation': f'{lot_diff_acres:+.2f} acres × ${lot_adjustment_per_acre:,}/acre'
        })
    
    # 2. SHAPE / FRONTAGE-TO-DEPTH RATIO
    subject_frontage_ft = subject.get('frontage_linear_feet', 0)
    subject_depth_ft = subject.get('depth_feet', 0)
    comp_frontage_ft = comparable.get('frontage_linear_feet', 0)
    comp_depth_ft = comparable.get('depth_feet', 0)
    
    if all([subject_frontage_ft, subject_depth_ft, comp_frontage_ft, comp_depth_ft]):
        subject_ratio = subject_frontage_ft / subject_depth_ft
        comp_ratio = comp_frontage_ft / comp_depth_ft
    
        # Optimal ratio: 1:3 to 1:5 (higher ratios = more frontage = better for commercial)
        optimal_ratio = 0.25  # 1:4
    
        subject_deviation = abs(subject_ratio - optimal_ratio)
        comp_deviation = abs(comp_ratio - optimal_ratio)
    
        shape_differential = comp_deviation - subject_deviation
    
        if abs(shape_differential) > 0.05:  # Material difference
            # Penalty for poor shape: 2-5% per 0.1 deviation from optimal
            shape_adjustment_factor = market_params.get('shape_adjustment_per_0_1_deviation', 0.02)  # 2%
            shape_adjustment = base_price * (shape_differential * shape_adjustment_factor * 10)
    
    
            adjustments.append({
                'category': 'Land',
                'characteristic': 'Shape/Frontage Ratio',
                'subject_value': f'{subject_ratio:.2f} ({subject_frontage_ft}ft × {subject_depth_ft}ft)',
                'comp_value': f'{comp_ratio:.2f} ({comp_frontage_ft}ft × {comp_depth_ft}ft)',
                'adjustment': shape_adjustment,
                'explanation': f'Shape differential from optimal 1:4 ratio: {shape_differential:+.2f}'
            })
    
    # 3. TOPOGRAPHY
    topography_hierarchy = {'severely_sloped': 1, 'moderately_sloped': 2, 'gently_sloped': 3, 'level': 4}
    subject_topo = subject.get('topography', 'level')
    comp_topo = comparable.get('topography', 'level')
    
    subject_topo_score = topography_hierarchy.get(subject_topo, 4)
    comp_topo_score = topography_hierarchy.get(comp_topo, 4)
    
    topo_diff = subject_topo_score - comp_topo_score
    
    if topo_diff != 0:
        # Level land is preferred: 3-5% premium per level
        topo_adjustment_pct = market_params.get('topography_adjustment_pct_per_level', 3.5)
        topo_adjustment = base_price * (topo_diff * topo_adjustment_pct / 100)
    
        adjustments.append({
            'category': 'Land',
            'characteristic': 'Topography',
            'subject_value': subject_topo,
            'comp_value': comp_topo,
            'adjustment': topo_adjustment,
            'explanation': f'{topo_diff:+} levels × {topo_adjustment_pct}% (level land premium)'
        })
    
    # 4. UTILITIES - AVAILABILITY AND CAPACITY
    utilities_score_map = {
        'full_services_adequate': 4,      # Water, sewer, gas, electric (adequate capacity)
        'full_services_limited': 3,       # All services but limited capacity
        'partial_services': 2,            # Some services available
        'no_services': 1                  # No utilities (well/septic required)
    }
    
    subject_utilities = subject.get('utilities', 'full_services_adequate')
    comp_utilities = comparable.get('utilities', 'full_services_adequate')
    
    subject_utilities_score = utilities_score_map.get(subject_utilities, 4)
    comp_utilities_score = utilities_score_map.get(comp_utilities, 4)
    
    utilities_diff = subject_utilities_score - comp_utilities_score
    
    if utilities_diff != 0:
        # Full services vs. partial/none: significant value impact
        utilities_adjustment_pct = market_params.get('utilities_adjustment_pct_per_level', 5.0)
        utilities_adjustment = base_price * (utilities_diff * utilities_adjustment_pct / 100)
    
        adjustments.append({
            'category': 'Land',
            'characteristic': 'Utilities',
            'subject_value': subject_utilities,
            'comp_value': comp_utilities,
            'adjustment': utilities_adjustment,
            'explanation': f'{utilities_diff:+} levels × {utilities_adjustment_pct}%'
        })
    
    # 5. DRAINAGE
    drainage_hierarchy = {'poor': 1, 'adequate': 2, 'good': 3, 'excellent': 4}
    subject_drainage = subject.get('drainage', 'good')
    comp_drainage = comparable.get('drainage', 'good')
    
    subject_drainage_score = drainage_hierarchy.get(subject_drainage, 3)
    comp_drainage_score = drainage_hierarchy.get(comp_drainage, 3)
    
    drainage_diff = subject_drainage_score - comp_drainage_score
    
    if drainage_diff != 0:
        drainage_adjustment_pct = market_params.get('drainage_adjustment_pct_per_level', 2.0)
        drainage_adjustment = base_price * (drainage_diff * drainage_adjustment_pct / 100)
    
        adjustments.append({
            'category': 'Land',
            'characteristic': 'Drainage',
            'subject_value': subject_drainage,
            'comp_value': comp_drainage,
            'adjustment': drainage_adjustment,
            'explanation': f'{drainage_diff:+} levels × {drainage_adjustment_pct}%'
        })
    
    # 6. FLOOD ZONE
    flood_zone_map = {'none': 0, 'flood_fringe': -5, 'floodway': -15}  # % adjustment
    subject_flood = subject.get('flood_zone', 'none')
    comp_flood = comparable.get('flood_zone', 'none')
    
    subject_flood_pct = flood_zone_map.get(subject_flood, 0)
    comp_flood_pct = flood_zone_map.get(comp_flood, 0)
    
    if subject_flood_pct != comp_flood_pct:
        flood_adjustment_pct = comp_flood_pct - subject_flood_pct
        flood_adjustment = base_price * (flood_adjustment_pct / 100)
    
        adjustments.append({
            'category': 'Land',
            'characteristic': 'Flood Zone',
            'subject_value': subject_flood,
            'comp_value': comp_flood,
            'adjustment': flood_adjustment,
            'explanation': f'Flood zone differential: {flood_adjustment_pct:+.1f}%'
        })
    
    # 7. ENVIRONMENTAL CONSTRAINTS (Wetlands, Contamination)
    environmental_map = {'contaminated': -30, 'brownfield': -15, 'wetlands_minor': -8, 'wetlands_major': -20, 'clean': 0}
    subject_environmental = subject.get('environmental_status', 'clean')
    comp_environmental = comparable.get('environmental_status', 'clean')
    
    subject_env_pct = environmental_map.get(subject_environmental, 0)
    comp_env_pct = environmental_map.get(comp_environmental, 0)
    
    if subject_env_pct != comp_env_pct:
        env_adjustment_pct = comp_env_pct - subject_env_pct
        env_adjustment = base_price * (env_adjustment_pct / 100)
    
        adjustments.append({
            'category': 'Land',
            'characteristic': 'Environmental Status',
            'subject_value': subject_environmental,
            'comp_value': comp_environmental,
            'adjustment': env_adjustment,
            'explanation': f'Environmental constraint differential: {env_adjustment_pct:+.1f}%'
        })
    
    # 8. SOIL/BEARING CAPACITY (for development potential)
    soil_map = {'poor_bearing': -5, 'adequate': 0, 'good_bearing': 3, 'excellent': 5}  # % adjustment
    subject_soil = subject.get('soil_quality', 'adequate')
    comp_soil = comparable.get('soil_quality', 'adequate')
    
    subject_soil_pct = soil_map.get(subject_soil, 0)
    comp_soil_pct = soil_map.get(comp_soil, 0)
    
    if subject_soil_pct != comp_soil_pct:
        soil_adjustment_pct = subject_soil_pct - comp_soil_pct
        soil_adjustment = base_price * (soil_adjustment_pct / 100)
    
        adjustments.append({
            'category': 'Land',
            'characteristic': 'Soil/Bearing Capacity',
            'subject_value': subject_soil,
            'comp_value': comp_soil,
            'adjustment': soil_adjustment,
            'explanation': f'Soil quality differential: {soil_adjustment_pct:+.1f}%'
        })

    return adjustments
