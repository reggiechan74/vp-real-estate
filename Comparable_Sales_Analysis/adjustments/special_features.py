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
    Special Features Adjustments (6 subcategories)

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
    # SPECIAL FEATURES (6 subcategories)
    # =========================================================================
    
    # 39. RAIL SPUR (Industrial)
    if property_type == 'industrial':
        subject_rail = subject.get('rail_spur', False)
        comp_rail = comparable.get('rail_spur', False)
    
        if subject_rail != comp_rail:
            # Rail spur value: $250K-$500K installed
            # Market premium: 5-10% for rail-served industrial
            rail_adjustment_pct = market_params.get('rail_spur_premium_pct', 7.0)
            rail_adjustment = base_price * (rail_adjustment_pct / 100)
    
            if not subject_rail:  # Comparable has rail, subject doesn't
                rail_adjustment = -rail_adjustment
    
    
            adjustments.append({
                'category': 'Special Features',
                'characteristic': 'Rail Spur',
                'subject_value': 'Yes' if subject_rail else 'No',
                'comp_value': 'Yes' if comp_rail else 'No',
                'adjustment': rail_adjustment,
                'explanation': f'Rail spur premium: {rail_adjustment_pct}% of property value'
            })
    
    # 40. CRANE SYSTEMS (Industrial)
    if property_type == 'industrial':
        subject_crane = subject.get('crane_system', 'none')
        comp_crane = comparable.get('crane_system', 'none')
    
        crane_map = {'none': 0, 'jib_crane': 50000, 'bridge_crane_10ton': 150000, 'bridge_crane_20ton': 250000, 'gantry_crane': 400000}
    
        subject_crane_value = crane_map.get(subject_crane, 0)
        comp_crane_value = crane_map.get(comp_crane, 0)
    
        if subject_crane_value != comp_crane_value:
            crane_adjustment = subject_crane_value - comp_crane_value
    
            # Depreciate by age
            crane_age = comparable.get('crane_age_years', 10)
            crane_life = 30  # Typical useful life
            crane_depreciation = max(0, 1 - (crane_age / crane_life))
    
            crane_adjustment = crane_adjustment * crane_depreciation
    
            adjustments.append({
                'category': 'Special Features',
                'characteristic': 'Crane System',
                'subject_value': subject_crane,
                'comp_value': comp_crane,
                'adjustment': crane_adjustment,
                'explanation': f'Crane system differential: ${subject_crane_value - comp_crane_value:,} × {crane_depreciation:.0%} depreciation'
            })
    
    # 41. HEAVY POWER (3-Phase, High Voltage)
    if property_type == 'industrial':
        subject_power_amps = subject.get('electrical_service_amps', 0)
        comp_power_amps = comparable.get('electrical_service_amps', 0)
    
        if subject_power_amps != comp_power_amps:
            power_diff = subject_power_amps - comp_power_amps
    
            # Heavy power (1000+ amps): significant value for manufacturing
            # Premium: $10-$20 per amp for capacity over 400 amps
            if abs(power_diff) >= 200:  # Material difference
                power_value_per_amp = market_params.get('electrical_capacity_value_per_amp', 15.0)
                power_adjustment = power_diff * power_value_per_amp
    
    
                adjustments.append({
                    'category': 'Special Features',
                    'characteristic': 'Electrical Capacity',
                    'subject_value': f'{subject_power_amps} amps',
                    'comp_value': f'{comp_power_amps} amps',
                    'adjustment': power_adjustment,
                    'explanation': f'{power_diff:+} amps × ${power_value_per_amp}/amp'
                })
    
    # 42. TRUCK SCALES (Industrial)
    if property_type == 'industrial':
        subject_scales = subject.get('truck_scales', False)
        comp_scales = comparable.get('truck_scales', False)
    
        if subject_scales != comp_scales:
            # Truck scale value: $50K-$100K installed
            scales_value = market_params.get('truck_scales_value', 75000)
    
            scales_adjustment = scales_value if subject_scales else -scales_value
    
            adjustments.append({
                'category': 'Special Features',
                'characteristic': 'Truck Scales',
                'subject_value': 'Yes' if subject_scales else 'No',
                'comp_value': 'Yes' if comp_scales else 'No',
                'adjustment': scales_adjustment,
                'explanation': f'Truck scales value: ${scales_value:,}'
            })
    
    # 43. SPECIALIZED HVAC (Cleanroom, Temperature Control)
    specialized_hvac_map = {'none': 0, 'temperature_controlled': 100000, 'humidity_controlled': 150000, 'cleanroom_class_100k': 300000, 'cleanroom_class_10k': 600000}
    
    subject_spec_hvac = subject.get('specialized_hvac', 'none')
    comp_spec_hvac = comparable.get('specialized_hvac', 'none')
    
    subject_spec_hvac_value = specialized_hvac_map.get(subject_spec_hvac, 0)
    comp_spec_hvac_value = specialized_hvac_map.get(comp_spec_hvac, 0)
    
    if subject_spec_hvac_value != comp_spec_hvac_value:
        spec_hvac_adjustment = subject_spec_hvac_value - comp_spec_hvac_value
    
        adjustments.append({
            'category': 'Special Features',
            'characteristic': 'Specialized HVAC',
            'subject_value': subject_spec_hvac,
            'comp_value': comp_spec_hvac,
            'adjustment': spec_hvac_adjustment,
            'explanation': f'Specialized HVAC differential: ${spec_hvac_adjustment:+,}'
        })
    
    # 44. BACKUP GENERATOR
    subject_generator = subject.get('backup_generator_kw', 0)
    comp_generator = comparable.get('backup_generator_kw', 0)
    
    if subject_generator != comp_generator:
        generator_diff = subject_generator - comp_generator
    
        # Generator value: $500-$1,000 per kW installed
        generator_value_per_kw = market_params.get('generator_value_per_kw', 750)
    
        generator_adjustment = generator_diff * generator_value_per_kw
    
        adjustments.append({
            'category': 'Special Features',
            'characteristic': 'Backup Generator',
            'subject_value': f'{subject_generator} kW',
            'comp_value': f'{comp_generator} kW',
            'adjustment': generator_adjustment,
            'explanation': f'{generator_diff:+} kW × ${generator_value_per_kw}/kW'
        })

    return adjustments
