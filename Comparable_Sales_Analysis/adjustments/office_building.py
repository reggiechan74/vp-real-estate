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
    Office Building Adjustments (8 subcategories)

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
    # BUILDING - OFFICE SPECIFIC (8 subcategories)
    # =========================================================================
    
    # 25. BUILDING SIZE (sq ft)
    subject_building_sf = subject.get('building_sf', 0)
    comp_building_sf = comparable.get('building_sf', 0)
    
    if subject_building_sf > 0 and comp_building_sf > 0:
        building_diff_sf = subject_building_sf - comp_building_sf
    
        # Office: Economies of scale similar to industrial
        building_adjustment_per_sf = market_params.get('building_size_adjustment_per_sf', 3.0)
    
        building_size_adjustment = building_diff_sf * building_adjustment_per_sf
    
        adjustments.append({
            'category': 'Office Building',
            'characteristic': 'Building Size',
            'subject_value': f'{subject_building_sf:,} sq ft',
            'comp_value': f'{comp_building_sf:,} sq ft',
            'adjustment': building_size_adjustment,
            'explanation': f'{building_diff_sf:+,} sq ft × ${building_adjustment_per_sf}/sq ft'
        })
    
    # 26. FLOOR PLATE EFFICIENCY (RSF/USF Ratio)
    subject_efficiency = subject.get('floor_plate_efficiency_pct', 85.0)
    comp_efficiency = comparable.get('floor_plate_efficiency_pct', 85.0)
    
    if subject_efficiency != comp_efficiency:
        efficiency_diff = subject_efficiency - comp_efficiency
    
        # Typical range: 75-90%
        # 85% is standard, above is premium, below is penalty
        # Value: 1-2% per 5% efficiency points
        efficiency_adjustment_pct_per_5pts = market_params.get('efficiency_adjustment_pct_per_5pts', 1.5)
        efficiency_adjustment = base_price * ((efficiency_diff / 5) * efficiency_adjustment_pct_per_5pts / 100)
    
    
        adjustments.append({
            'category': 'Office Building',
            'characteristic': 'Floor Plate Efficiency',
            'subject_value': f'{subject_efficiency}%',
            'comp_value': f'{comp_efficiency}%',
            'adjustment': efficiency_adjustment,
            'explanation': f'{efficiency_diff:+.1f}% differential × {efficiency_adjustment_pct_per_5pts}% per 5 points'
        })
    
    # 27. PARKING RATIO (spaces per 1,000 sf)
    subject_parking_ratio = subject.get('parking_spaces_per_1000sf', 0)
    comp_parking_ratio = comparable.get('parking_spaces_per_1000sf', 0)
    
    if subject_parking_ratio != comp_parking_ratio:
        parking_diff = subject_parking_ratio - comp_parking_ratio
    
        # Standard: 3.5-4.5 spaces per 1,000 sf
        # Below standard: penalty, above: premium
        # Value: $3,000-$5,000 per space
        parking_value_per_space = market_params.get('parking_value_per_space', 4000)
    
        # Calculate spaces differential based on building size
        spaces_diff = (parking_diff * comp_building_sf) / 1000
    
        parking_adjustment = spaces_diff * parking_value_per_space
    
        adjustments.append({
            'category': 'Office Building',
            'characteristic': 'Parking Ratio',
            'subject_value': f'{subject_parking_ratio:.1f}/1,000 sf',
            'comp_value': f'{comp_parking_ratio:.1f}/1,000 sf',
            'adjustment': parking_adjustment,
            'explanation': f'{spaces_diff:+.0f} spaces × ${parking_value_per_space:,}/space'
        })
    
    # 28. BUILDING CLASS (A/B/C)
    class_hierarchy = {'C': 1, 'B-': 2, 'B': 3, 'B+': 4, 'A-': 5, 'A': 6, 'A+': 7}
    subject_class = subject.get('building_class', 'B')
    comp_class = comparable.get('building_class', 'B')
    
    subject_class_score = class_hierarchy.get(subject_class, 3)
    comp_class_score = class_hierarchy.get(comp_class, 3)
    
    class_diff = subject_class_score - comp_class_score
    
    if class_diff != 0:
        # Each class level: 8-12% differential
        class_adjustment_pct = market_params.get('building_class_adjustment_pct_per_level', 10.0)
        class_adjustment = base_price * (class_diff * class_adjustment_pct / 100)
    
        adjustments.append({
            'category': 'Office Building',
            'characteristic': 'Building Class',
            'subject_value': f'Class {subject_class}',
            'comp_value': f'Class {comp_class}',
            'adjustment': class_adjustment,
            'explanation': f'{class_diff:+} class levels × {class_adjustment_pct}%'
        })
    
    # 29. CEILING HEIGHT
    subject_ceiling_height = subject.get('ceiling_height_feet', 9.0)
    comp_ceiling_height = comparable.get('ceiling_height_feet', 9.0)
    
    if subject_ceiling_height != comp_ceiling_height:
        ceiling_diff = subject_ceiling_height - comp_ceiling_height
    
        # Standard: 9', Modern: 10-12'
        # Premium for higher ceilings: $2-$4/sf per foot
        if abs(ceiling_diff) >= 1:
            ceiling_height_premium_per_sf = market_params.get('ceiling_height_premium_per_sf', 3.0)
            ceiling_adjustment = ceiling_diff * ceiling_height_premium_per_sf * comp_building_sf
    
    
            adjustments.append({
                'category': 'Office Building',
                'characteristic': 'Ceiling Height',
                'subject_value': f'{subject_ceiling_height} feet',
                'comp_value': f'{comp_ceiling_height} feet',
                'adjustment': ceiling_adjustment,
                'explanation': f'{ceiling_diff:+.0f} feet × ${ceiling_height_premium_per_sf}/sf × {comp_building_sf:,} sf'
            })
    
    # 30. ELEVATOR COUNT / CAPACITY
    subject_elevators = subject.get('elevator_count', 0)
    comp_elevators = comparable.get('elevator_count', 0)
    
    if subject_elevators != comp_elevators:
        elevator_diff = subject_elevators - comp_elevators
    
        # Elevator cost: $150K-$250K per elevator installed
        # Value contribution (depreciated): $100K-$150K
        elevator_value = market_params.get('elevator_value_each', 125000)
    
        elevator_adjustment = elevator_diff * elevator_value
    
        adjustments.append({
            'category': 'Office Building',
            'characteristic': 'Elevator Count',
            'subject_value': f'{subject_elevators} elevators',
            'comp_value': f'{comp_elevators} elevators',
            'adjustment': elevator_adjustment,
            'explanation': f'{elevator_diff:+} elevators × ${elevator_value:,} each'
        })
    
    # 31. WINDOW LINE (Perimeter Offices)
    subject_window_pct = subject.get('window_line_percentage', 30)
    comp_window_pct = comparable.get('window_line_percentage', 30)
    
    if subject_window_pct != comp_window_pct:
        window_diff = subject_window_pct - comp_window_pct
    
        # Window line offices command premium
        # Typical: 25-35% of floor area
        # Premium: $5-$10/sf for windowed space
        window_premium_per_sf = market_params.get('window_line_premium_per_sf', 7.0)
    
        window_adjustment = (window_diff / 100) * window_premium_per_sf * comp_building_sf
    
        adjustments.append({
            'category': 'Office Building',
            'characteristic': 'Window Line %',
            'subject_value': f'{subject_window_pct}% perimeter offices',
            'comp_value': f'{comp_window_pct}% perimeter offices',
            'adjustment': window_adjustment,
            'explanation': f'{window_diff:+}% × ${window_premium_per_sf}/sf × {comp_building_sf:,} sf'
        })
    
    # 32. CONDITION (Office-specific)
    condition_hierarchy = {'poor': 1, 'fair': 2, 'average': 3, 'good': 4, 'excellent': 5}
    subject_condition = subject.get('condition', 'average')
    comp_condition = comparable.get('condition', 'average')
    
    subject_condition_score = condition_hierarchy.get(subject_condition, 3)
    comp_condition_score = condition_hierarchy.get(comp_condition, 3)
    
    condition_diff = subject_condition_score - comp_condition_score
    
    if condition_diff != 0:
        # Office: 6-10% per condition level (higher than industrial)
        condition_adjustment_pct = market_params.get('condition_adjustment_pct_per_level', 8.0)
        condition_adjustment = base_price * (condition_diff * condition_adjustment_pct / 100)
    
        adjustments.append({
            'category': 'Office Building',
            'characteristic': 'Condition',
            'subject_value': subject_condition,
            'comp_value': comp_condition,
            'adjustment': condition_adjustment,
            'explanation': f'{condition_diff:+} levels × {condition_adjustment_pct}%'
        })

    return adjustments
