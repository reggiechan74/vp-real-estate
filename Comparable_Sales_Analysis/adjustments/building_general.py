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
    Building General Adjustments (6 subcategories)

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
    # BUILDING - GENERAL (All Property Types) (6 subcategories)
    # =========================================================================
    
    # 33. AGE / EFFECTIVE AGE
    subject_age = subject.get('effective_age_years', 0)
    comp_age = comparable.get('effective_age_years', 0)
    
    if subject_age != comp_age:
        age_diff = subject_age - comp_age
    
        # Depreciation: 0.5-1.5% per year depending on property type
        annual_depreciation_pct = market_params.get('annual_depreciation_pct', 1.0)
    
        age_adjustment = base_price * (age_diff * annual_depreciation_pct / 100)
    
        adjustments.append({
            'category': 'Building - General',
            'characteristic': 'Age/Effective Age',
            'subject_value': f'{subject_age} years',
            'comp_value': f'{comp_age} years',
            'adjustment': age_adjustment,
            'explanation': f'{age_diff:+} years × {annual_depreciation_pct}% annual depreciation'
        })
    
    # 34. CONSTRUCTION QUALITY
    quality_hierarchy = {'economy': 1, 'standard': 2, 'good': 3, 'superior': 4}
    subject_quality = subject.get('construction_quality', 'standard')
    comp_quality = comparable.get('construction_quality', 'standard')
    
    subject_quality_score = quality_hierarchy.get(subject_quality, 2)
    comp_quality_score = quality_hierarchy.get(comp_quality, 2)
    
    quality_diff = subject_quality_score - comp_quality_score
    
    if quality_diff != 0:
        # Quality differential: 5-10% per level
        quality_adjustment_pct = market_params.get('construction_quality_adjustment_pct_per_level', 7.0)
        quality_adjustment = base_price * (quality_diff * quality_adjustment_pct / 100)
    
        adjustments.append({
            'category': 'Building - General',
            'characteristic': 'Construction Quality',
            'subject_value': subject_quality,
            'comp_value': comp_quality,
            'adjustment': quality_adjustment,
            'explanation': f'{quality_diff:+} levels × {quality_adjustment_pct}%'
        })
    
    # 35. FUNCTIONAL UTILITY / OBSOLESCENCE
    functional_map = {'severe_obsolescence': -15, 'moderate_obsolescence': -8, 'minor_obsolescence': -3, 'adequate': 0, 'superior': 5}
    subject_functional = subject.get('functional_utility', 'adequate')
    comp_functional = comparable.get('functional_utility', 'adequate')
    
    subject_functional_pct = functional_map.get(subject_functional, 0)
    comp_functional_pct = functional_map.get(comp_functional, 0)
    
    if subject_functional_pct != comp_functional_pct:
        functional_adjustment_pct = subject_functional_pct - comp_functional_pct
        functional_adjustment = base_price * (functional_adjustment_pct / 100)
    
        adjustments.append({
            'category': 'Building - General',
            'characteristic': 'Functional Utility',
            'subject_value': subject_functional,
            'comp_value': comp_functional,
            'adjustment': functional_adjustment,
            'explanation': f'Functional utility differential: {functional_adjustment_pct:+.1f}%'
        })
    
    # 36. ENERGY EFFICIENCY (LEED, Green Features)
    energy_map = {'none': 0, 'energy_star': 3, 'leed_certified': 5, 'leed_silver': 8, 'leed_gold': 12, 'leed_platinum': 18}
    subject_energy = subject.get('energy_certification', 'none')
    comp_energy = comparable.get('energy_certification', 'none')
    
    subject_energy_pct = energy_map.get(subject_energy, 0)
    comp_energy_pct = energy_map.get(comp_energy, 0)
    
    if subject_energy_pct != comp_energy_pct:
        energy_adjustment_pct = subject_energy_pct - comp_energy_pct
        energy_adjustment = base_price * (energy_adjustment_pct / 100)
    
        adjustments.append({
            'category': 'Building - General',
            'characteristic': 'Energy Efficiency',
            'subject_value': subject_energy,
            'comp_value': comp_energy,
            'adjustment': energy_adjustment,
            'explanation': f'Green building premium: {energy_adjustment_pct:+.1f}%'
        })
    
    # 37. ARCHITECTURAL STYLE / APPEAL
    architectural_map = {'dated': -5, 'average': 0, 'attractive': 3, 'exceptional': 7}
    subject_arch = subject.get('architectural_appeal', 'average')
    comp_arch = comparable.get('architectural_appeal', 'average')
    
    subject_arch_pct = architectural_map.get(subject_arch, 0)
    comp_arch_pct = architectural_map.get(comp_arch, 0)
    
    if subject_arch_pct != comp_arch_pct:
        arch_adjustment_pct = subject_arch_pct - comp_arch_pct
        arch_adjustment = base_price * (arch_adjustment_pct / 100)
    
        adjustments.append({
            'category': 'Building - General',
            'characteristic': 'Architectural Appeal',
            'subject_value': subject_arch,
            'comp_value': comp_arch,
            'adjustment': arch_adjustment,
            'explanation': f'Architectural appeal differential: {arch_adjustment_pct:+.1f}%'
        })
    
    # 38. HVAC SYSTEM (Type and Efficiency)
    hvac_map = {'none': -10, 'basic': 0, 'modern_standard': 5, 'high_efficiency': 10, 'geothermal': 15}
    subject_hvac = subject.get('hvac_system', 'modern_standard')
    comp_hvac = comparable.get('hvac_system', 'modern_standard')
    
    subject_hvac_pct = hvac_map.get(subject_hvac, 5)
    comp_hvac_pct = hvac_map.get(comp_hvac, 5)
    
    if subject_hvac_pct != comp_hvac_pct:
        hvac_adjustment_pct = subject_hvac_pct - comp_hvac_pct
        hvac_adjustment = base_price * (hvac_adjustment_pct / 100)
    
        adjustments.append({
            'category': 'Building - General',
            'characteristic': 'HVAC System',
            'subject_value': subject_hvac,
            'comp_value': comp_hvac,
            'adjustment': hvac_adjustment,
            'explanation': f'HVAC system differential: {hvac_adjustment_pct:+.1f}%'
        })

    return adjustments
