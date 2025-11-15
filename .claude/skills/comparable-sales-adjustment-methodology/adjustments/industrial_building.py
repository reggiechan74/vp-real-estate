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
    Industrial Building Adjustments (10 subcategories)

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
    # BUILDING - INDUSTRIAL SPECIFIC (10 subcategories)
    # =========================================================================
    
    # 15. BUILDING SIZE (sq ft)
    subject_building_sf = subject.get('building_sf', 0)
    comp_building_sf = comparable.get('building_sf', 0)
    
    if subject_building_sf > 0 and comp_building_sf > 0:
        building_diff_sf = subject_building_sf - comp_building_sf
    
        # Economies of scale: larger buildings have lower $/sf
        building_adjustment_per_sf = market_params.get('building_size_adjustment_per_sf', 2.0)
    
        building_size_adjustment = building_diff_sf * building_adjustment_per_sf
    
        adjustments.append({
            'category': 'Industrial Building',
            'characteristic': 'Building Size',
            'subject_value': f'{subject_building_sf:,} sq ft',
            'comp_value': f'{comp_building_sf:,} sq ft',
            'adjustment': building_size_adjustment,
            'explanation': f'{building_diff_sf:+,} sq ft × ${building_adjustment_per_sf}/sq ft'
        })
    
    # 16. CLEAR HEIGHT (Critical for warehousing)
    subject_clear_height = subject.get('clear_height_feet', 0)
    comp_clear_height = comparable.get('clear_height_feet', 0)
    
    if subject_clear_height > 0 and comp_clear_height > 0:
        clear_height_diff = subject_clear_height - comp_clear_height
    
        # Clear height premium: $1-$3/sq ft per additional foot above 20'
        # Example: 24' vs 20' clear height = $4/sq ft × building size
        clear_height_value_per_foot = market_params.get('clear_height_value_per_foot_per_sf', 1.5)
    
        clear_height_adjustment = clear_height_diff * clear_height_value_per_foot * comp_building_sf
    
        adjustments.append({
            'category': 'Industrial Building',
            'characteristic': 'Clear Height',
            'subject_value': f'{subject_clear_height} feet',
            'comp_value': f'{comp_clear_height} feet',
            'adjustment': clear_height_adjustment,
            'explanation': f'{clear_height_diff:+} feet × ${clear_height_value_per_foot}/sf × {comp_building_sf:,} sf'
        })
    
    # 17. LOADING DOCKS (Number and Type)
    subject_dock_high = subject.get('loading_docks_dock_high', 0)
    subject_grade_level = subject.get('loading_docks_grade_level', 0)
    subject_drive_in = subject.get('loading_docks_drive_in', 0)
    
    comp_dock_high = comparable.get('loading_docks_dock_high', 0)
    comp_grade_level = comparable.get('loading_docks_grade_level', 0)
    comp_drive_in = comparable.get('loading_docks_drive_in', 0)
    
    # Value per dock type
    dock_high_value = 25000  # Most valuable
    grade_level_value = 15000
    drive_in_value = 50000  # Drive-in doors most valuable for certain uses
    
    subject_dock_value = (subject_dock_high * dock_high_value +
                         subject_grade_level * grade_level_value +
                         subject_drive_in * drive_in_value)
    
    comp_dock_value = (comp_dock_high * dock_high_value +
                      comp_grade_level * grade_level_value +
                      comp_drive_in * drive_in_value)
    
    if subject_dock_value != comp_dock_value:
        loading_dock_adjustment = subject_dock_value - comp_dock_value
    
        subject_total_docks = subject_dock_high + subject_grade_level + subject_drive_in
        comp_total_docks = comp_dock_high + comp_grade_level + comp_drive_in
    
        adjustments.append({
            'category': 'Industrial Building',
            'characteristic': 'Loading Docks',
            'subject_value': f'{subject_total_docks} total ({subject_dock_high} dock-high, {subject_grade_level} grade, {subject_drive_in} drive-in)',
            'comp_value': f'{comp_total_docks} total ({comp_dock_high} dock-high, {comp_grade_level} grade, {comp_drive_in} drive-in)',
            'adjustment': loading_dock_adjustment,
            'explanation': f'Loading dock differential: ${loading_dock_adjustment:+,}'
        })
    
    # 18. COLUMN SPACING (for racking efficiency)
    subject_column_spacing = subject.get('column_spacing_feet', 0)
    comp_column_spacing = comparable.get('column_spacing_feet', 0)
    
    if subject_column_spacing > 0 and comp_column_spacing > 0:
        # Modern warehouse: 50-60' spacing preferred
        # Older: 20-30' spacing (less efficient for racking)
        column_diff = subject_column_spacing - comp_column_spacing
    
        # Value differential: $0.50-$1.00/sf for wider spacing
        if abs(column_diff) >= 10:  # Material difference (10+ feet)
            column_adjustment_per_sf = market_params.get('column_spacing_adjustment_per_sf', 0.75)
            column_adjustment = (column_diff / 10) * column_adjustment_per_sf * comp_building_sf
    
    
            adjustments.append({
                'category': 'Industrial Building',
                'characteristic': 'Column Spacing',
                'subject_value': f'{subject_column_spacing} feet',
                'comp_value': f'{comp_column_spacing} feet',
                'adjustment': column_adjustment,
                'explanation': f'{column_diff:+} feet differential × ${column_adjustment_per_sf}/sf per 10\' × {comp_building_sf:,} sf'
            })
    
    # 19. FLOOR LOAD CAPACITY
    subject_floor_load = subject.get('floor_load_capacity_psf', 0)
    comp_floor_load = comparable.get('floor_load_capacity_psf', 0)
    
    if subject_floor_load > 0 and comp_floor_load > 0:
        floor_load_diff = subject_floor_load - comp_floor_load
    
        # Standard: 125 psf, Heavy: 250-500 psf
        # Premium for heavy floor: $2-$5/sf
        if abs(floor_load_diff) >= 100:  # Material difference
            floor_load_adjustment_per_sf = market_params.get('floor_load_adjustment_per_sf', 3.0)
            floor_load_adjustment = (floor_load_diff / 100) * floor_load_adjustment_per_sf * comp_building_sf
    
    
            adjustments.append({
                'category': 'Industrial Building',
                'characteristic': 'Floor Load Capacity',
                'subject_value': f'{subject_floor_load} psf',
                'comp_value': f'{comp_floor_load} psf',
                'adjustment': floor_load_adjustment,
                'explanation': f'{floor_load_diff:+} psf differential × ${floor_load_adjustment_per_sf}/sf per 100 psf × {comp_building_sf:,} sf'
            })
    
    # 20. OFFICE FINISH PERCENTAGE
    subject_office_pct = subject.get('office_finish_percentage', 0)
    comp_office_pct = comparable.get('office_finish_percentage', 0)
    
    if subject_office_pct != comp_office_pct:
        office_pct_diff = subject_office_pct - comp_office_pct
    
        # Office finish cost: $60-$100/sf vs. warehouse $30-$50/sf
        # Differential: $30-$50/sf
        office_finish_premium_per_sf = market_params.get('office_finish_premium_per_sf', 40.0)
    
        office_adjustment = (office_pct_diff / 100) * office_finish_premium_per_sf * comp_building_sf
    
        adjustments.append({
            'category': 'Industrial Building',
            'characteristic': 'Office Finish %',
            'subject_value': f'{subject_office_pct}% of GLA',
            'comp_value': f'{comp_office_pct}% of GLA',
            'adjustment': office_adjustment,
            'explanation': f'{office_pct_diff:+}% × ${office_finish_premium_per_sf}/sf × {comp_building_sf:,} sf'
        })
    
    # 21. BAY DEPTH
    subject_bay_depth = subject.get('bay_depth_feet', 0)
    comp_bay_depth = comparable.get('bay_depth_feet', 0)
    
    if subject_bay_depth > 0 and comp_bay_depth > 0:
        # Modern warehouse: 100-150' deep preferred
        # Shallow bay (<80'): less efficient
        bay_depth_diff = subject_bay_depth - comp_bay_depth
    
        if abs(bay_depth_diff) >= 20:  # Material difference
            # Adjustment: $0.25-$0.75/sf for deeper bays
            bay_depth_adjustment_per_sf = market_params.get('bay_depth_adjustment_per_sf', 0.50)
            bay_depth_adjustment = (bay_depth_diff / 20) * bay_depth_adjustment_per_sf * comp_building_sf
    
    
            adjustments.append({
                'category': 'Industrial Building',
                'characteristic': 'Bay Depth',
                'subject_value': f'{subject_bay_depth} feet',
                'comp_value': f'{comp_bay_depth} feet',
                'adjustment': bay_depth_adjustment,
                'explanation': f'{bay_depth_diff:+} feet differential × ${bay_depth_adjustment_per_sf}/sf per 20\' × {comp_building_sf:,} sf'
            })
    
    # 22. ESFR SPRINKLER SYSTEM
    subject_esfr = subject.get('esfr_sprinkler', False)
    comp_esfr = comparable.get('esfr_sprinkler', False)
    
    if subject_esfr != comp_esfr:
        # ESFR system cost: $3-$6/sf premium over standard
        esfr_premium_per_sf = market_params.get('esfr_premium_per_sf', 4.0)
        esfr_adjustment = (1 if subject_esfr else -1) * esfr_premium_per_sf * comp_building_sf
    
    
        adjustments.append({
            'category': 'Industrial Building',
            'characteristic': 'ESFR Sprinkler System',
            'subject_value': 'Yes' if subject_esfr else 'No',
            'comp_value': 'Yes' if comp_esfr else 'No',
            'adjustment': esfr_adjustment,
            'explanation': f'ESFR system differential: ${esfr_premium_per_sf}/sf × {comp_building_sf:,} sf'
        })
    
    # 23. TRUCK COURT DEPTH
    subject_truck_court = subject.get('truck_court_depth_feet', 0)
    comp_truck_court = comparable.get('truck_court_depth_feet', 0)
    
    if subject_truck_court != comp_truck_court:
        # Minimum: 120' for trailer maneuvering
        # Preferred: 150-180'
        truck_court_diff = subject_truck_court - comp_truck_court
    
        if abs(truck_court_diff) >= 30:  # Material difference
            # Penalty for inadequate truck court: 2-5% of value
            if subject_truck_court < 120 or comp_truck_court < 120:
                truck_court_adjustment_pct = 3.0  # 3% penalty if below minimum
                truck_court_adjustment = base_price * (truck_court_adjustment_pct / 100)
    
                if subject_truck_court < comp_truck_court:
                    truck_court_adjustment = -truck_court_adjustment
    
    
                adjustments.append({
                    'category': 'Industrial Building',
                    'characteristic': 'Truck Court Depth',
                    'subject_value': f'{subject_truck_court} feet',
                    'comp_value': f'{comp_truck_court} feet',
                    'adjustment': truck_court_adjustment,
                    'explanation': f'Inadequate truck court penalty: {truck_court_adjustment_pct}% of property value'
                })
    
    # 24. CONDITION (Industrial-specific)
    condition_hierarchy = {'poor': 1, 'fair': 2, 'average': 3, 'good': 4, 'excellent': 5}
    subject_condition = subject.get('condition', 'average')
    comp_condition = comparable.get('condition', 'average')
    
    subject_condition_score = condition_hierarchy.get(subject_condition, 3)
    comp_condition_score = condition_hierarchy.get(comp_condition, 3)
    
    condition_diff = subject_condition_score - comp_condition_score
    
    if condition_diff != 0:
        # Industrial: 5-8% per condition level
        condition_adjustment_pct = market_params.get('condition_adjustment_pct_per_level', 6.0)
        condition_adjustment = base_price * (condition_diff * condition_adjustment_pct / 100)
    
        adjustments.append({
            'category': 'Industrial Building',
            'characteristic': 'Condition',
            'subject_value': subject_condition,
            'comp_value': comp_condition,
            'adjustment': condition_adjustment,
            'explanation': f'{condition_diff:+} levels × {condition_adjustment_pct}%'
        })

    return adjustments
