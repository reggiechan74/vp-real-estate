"""
Comparable Sales Adjustment Module - Site Improvements

Provides 6 site improvement adjustments:
1. Paving / hardscape
2. Fencing / security
3. Site lighting
4. Landscaping
5. Stormwater management
6. Yard area (secured outdoor storage)

CUSPAP 2024 & USPAP 2024 Compliant
"""

import logging
from typing import Dict, List

from .validation import validate_adjustment_inputs

logger = logging.getLogger(__name__)


def calculate_adjustments(
    subject: Dict,
    comparable: Dict,
    base_price: float,
    market_params: Dict,
    property_type: str = 'industrial'
) -> List[Dict]:
    """
    Site Improvements Adjustments (6 subcategories)

    Args:
        subject: Subject property characteristics
        comparable: Comparable sale characteristics
        base_price: Base price after previous adjustments
        market_params: Market parameters for adjustments
        property_type: 'industrial' or 'office'

    Returns:
        List of adjustment dictionaries
    """
    adjustments = []

    # Input validation
    is_valid, errors = validate_adjustment_inputs(subject, comparable, base_price, market_params)
    if not is_valid:
        logger.error(f"Site adjustment validation failed: {errors}")
        return adjustments

    if market_params is None:
        market_params = {}

    # =========================================================================
    # SITE IMPROVEMENTS (6 subcategories)
    # =========================================================================
    
    # 9. PAVING / HARDSCAPE
    subject_paved_acres = subject.get('paved_area_acres', 0)
    comp_paved_acres = comparable.get('paved_area_acres', 0)
    
    if subject_paved_acres != comp_paved_acres:
        paved_diff = subject_paved_acres - comp_paved_acres
    
        # Paving cost: $8-$15/sq ft ($350K-$650K per acre)
        paving_cost_per_acre = market_params.get('paving_cost_per_acre', 500000)
    
        # Depreciate by age/condition
        paving_condition = comparable.get('paving_condition', 'good')
        depreciation_map = {'poor': 0.5, 'fair': 0.7, 'good': 0.85, 'excellent': 1.0}
        paving_depreciation_factor = depreciation_map.get(paving_condition, 0.85)
    
        paving_adjustment = paved_diff * paving_cost_per_acre * paving_depreciation_factor
    
        adjustments.append({
            'category': 'Site Improvements',
            'characteristic': 'Paving/Hardscape',
            'subject_value': f'{subject_paved_acres:.2f} acres paved',
            'comp_value': f'{comp_paved_acres:.2f} acres paved ({paving_condition} condition)',
            'adjustment': paving_adjustment,
            'explanation': f'{paved_diff:+.2f} acres × ${paving_cost_per_acre:,}/acre × {paving_depreciation_factor:.0%} depreciation'
        })
    
    # 10. FENCING / SECURITY
    fence_map = {'none': 0, 'chain_link': 50000, 'vinyl': 75000, 'security_fence': 120000}
    subject_fence = subject.get('fencing', 'none')
    comp_fence = comparable.get('fencing', 'none')
    
    subject_fence_value = fence_map.get(subject_fence, 0)
    comp_fence_value = fence_map.get(comp_fence, 0)
    
    if subject_fence_value != comp_fence_value:
        fence_adjustment = subject_fence_value - comp_fence_value
    
        # Depreciate by age
        fence_age = comparable.get('fence_age_years', 5)
        fence_life = 20  # Typical useful life
        fence_depreciation = max(0, 1 - (fence_age / fence_life))
    
        fence_adjustment = fence_adjustment * fence_depreciation
    
        adjustments.append({
            'category': 'Site Improvements',
            'characteristic': 'Fencing/Security',
            'subject_value': subject_fence,
            'comp_value': comp_fence,
            'adjustment': fence_adjustment,
            'explanation': f'Fence differential: ${subject_fence_value - comp_fence_value:,} × {fence_depreciation:.0%} depreciation'
        })
    
    # 11. SITE LIGHTING
    lighting_map = {'none': 0, 'minimal': 30000, 'adequate': 60000, 'extensive': 100000}
    subject_lighting = subject.get('site_lighting', 'adequate')
    comp_lighting = comparable.get('site_lighting', 'adequate')
    
    subject_lighting_value = lighting_map.get(subject_lighting, 60000)
    comp_lighting_value = lighting_map.get(comp_lighting, 60000)
    
    if subject_lighting_value != comp_lighting_value:
        lighting_adjustment = subject_lighting_value - comp_lighting_value
    
        adjustments.append({
            'category': 'Site Improvements',
            'characteristic': 'Site Lighting',
            'subject_value': subject_lighting,
            'comp_value': comp_lighting,
            'adjustment': lighting_adjustment,
            'explanation': f'Lighting differential: ${lighting_adjustment:+,}'
        })
    
    # 12. LANDSCAPING
    landscaping_map = {'none': 0, 'minimal': 15000, 'moderate': 35000, 'extensive': 75000}
    subject_landscaping = subject.get('landscaping', 'minimal')
    comp_landscaping = comparable.get('landscaping', 'minimal')
    
    subject_landscaping_value = landscaping_map.get(subject_landscaping, 15000)
    comp_landscaping_value = landscaping_map.get(comp_landscaping, 15000)
    
    if subject_landscaping_value != comp_landscaping_value:
        landscaping_adjustment = subject_landscaping_value - comp_landscaping_value
    
        adjustments.append({
            'category': 'Site Improvements',
            'characteristic': 'Landscaping',
            'subject_value': subject_landscaping,
            'comp_value': comp_landscaping,
            'adjustment': landscaping_adjustment,
            'explanation': f'Landscaping differential: ${landscaping_adjustment:+,}'
        })
    
    # 13. STORMWATER MANAGEMENT
    stormwater_map = {'none': -50000, 'basic': 0, 'retention_pond': 80000, 'advanced_system': 150000}
    subject_stormwater = subject.get('stormwater_management', 'basic')
    comp_stormwater = comparable.get('stormwater_management', 'basic')
    
    subject_stormwater_value = stormwater_map.get(subject_stormwater, 0)
    comp_stormwater_value = stormwater_map.get(comp_stormwater, 0)
    
    if subject_stormwater_value != comp_stormwater_value:
        stormwater_adjustment = subject_stormwater_value - comp_stormwater_value
    
        adjustments.append({
            'category': 'Site Improvements',
            'characteristic': 'Stormwater Management',
            'subject_value': subject_stormwater,
            'comp_value': comp_stormwater,
            'adjustment': stormwater_adjustment,
            'explanation': f'Stormwater system differential: ${stormwater_adjustment:+,}'
        })
    
    # 14. YARD AREA (Secured Outdoor Storage)
    subject_yard_acres = subject.get('secured_yard_acres', 0)
    comp_yard_acres = comparable.get('secured_yard_acres', 0)
    
    if subject_yard_acres != comp_yard_acres:
        yard_diff = subject_yard_acres - comp_yard_acres
    
        # Secured yard value: $100K-$200K per acre (fenced, paved, lit)
        yard_value_per_acre = market_params.get('secured_yard_value_per_acre', 150000)
    
        yard_adjustment = yard_diff * yard_value_per_acre
    
        adjustments.append({
            'category': 'Site Improvements',
            'characteristic': 'Secured Yard Area',
            'subject_value': f'{subject_yard_acres:.2f} acres',
            'comp_value': f'{comp_yard_acres:.2f} acres',
            'adjustment': yard_adjustment,
            'explanation': f'{yard_diff:+.2f} acres × ${yard_value_per_acre:,}/acre'
        })

    return adjustments
