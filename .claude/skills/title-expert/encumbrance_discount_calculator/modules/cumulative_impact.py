"""
Cumulative Impact Analysis Module
Calculates individual and cumulative discounts from multiple encumbrances
"""

from typing import List, Dict, Optional
from .validators import get_default_impact_percentage, get_encumbrance_range


def calculate_individual_discounts(
    encumbrances: List[Dict],
    property_area: float,
    unencumbered_value: float
) -> List[Dict]:
    """
    Calculate individual discount for each encumbrance.

    Args:
        encumbrances: List of encumbrance data
        property_area: Total property area in acres
        unencumbered_value: Unencumbered fee simple value

    Returns:
        List of encumbrance analysis with calculated discounts
    """
    results = []

    for idx, enc in enumerate(encumbrances, 1):
        enc_type = enc['type']
        enc_area = enc['area_acres']

        # Get impact percentage (use provided or default)
        if 'impact_percentage' in enc and enc['impact_percentage'] is not None:
            impact_pct = enc['impact_percentage']
        else:
            impact_pct = get_default_impact_percentage(enc_type)

        impact_decimal = impact_pct / 100

        # Get valid range for this encumbrance type
        ranges = get_encumbrance_range(enc_type)

        # Calculate area impact
        area_ratio = enc_area / property_area if property_area > 0 else 0

        # Calculate value discount
        # Method: Discount applies to encumbered area proportion
        encumbered_area_value = unencumbered_value * area_ratio
        discount_amount = encumbered_area_value * impact_decimal

        # Store analysis
        analysis = {
            'number': idx,
            'type': enc_type,
            'description': enc.get('description', ranges['description']),
            'area_acres': enc_area,
            'area_ratio': area_ratio,
            'impact_percentage': impact_pct,
            'impact_decimal': impact_decimal,
            'encumbered_area_value': encumbered_area_value,
            'discount_amount': discount_amount,
            'typical_range': {
                'min': ranges['min'] * 100,
                'max': ranges['max'] * 100,
                'typical': ranges['typical'] * 100
            },
            'metadata': {
                'voltage': enc.get('voltage'),
                'width_feet': enc.get('width_feet'),
                'length_feet': enc.get('length_feet')
            }
        }

        results.append(analysis)

    return results


def calculate_cumulative_discount(
    individual_discounts: List[Dict],
    method: str = 'multiplicative'
) -> Dict:
    """
    Calculate cumulative discount from multiple encumbrances.

    Cumulative discount formula: Value × (1-D₁) × (1-D₂) × (1-D₃)

    This reflects that each encumbrance reduces the remaining value,
    not the original value (conservative approach preventing double-counting).

    Args:
        individual_discounts: List of individual encumbrance analyses
        method: Calculation method
            'multiplicative' - (1-D₁) × (1-D₂) × (1-D₃) [DEFAULT, most common]
            'additive' - D₁ + D₂ + D₃ (simple sum, less conservative)
            'geometric_mean' - Geometric mean of discounts

    Returns:
        Dictionary with cumulative analysis results
    """
    if not individual_discounts:
        return {
            'method': method,
            'total_discount_amount': 0,
            'cumulative_discount_percentage': 0,
            'value_multiplier': 1.0,
            'breakdown': []
        }

    # Extract discount percentages (as decimals)
    discount_decimals = [d['impact_decimal'] for d in individual_discounts]

    if method == 'multiplicative':
        # Cumulative: (1-D₁) × (1-D₂) × (1-D₃)
        value_multiplier = 1.0
        for discount in discount_decimals:
            value_multiplier *= (1 - discount)

        cumulative_discount_pct = (1 - value_multiplier) * 100

    elif method == 'additive':
        # Simple sum: D₁ + D₂ + D₃
        cumulative_discount_decimal = sum(discount_decimals)
        cumulative_discount_pct = cumulative_discount_decimal * 100
        value_multiplier = 1 - cumulative_discount_decimal

    elif method == 'geometric_mean':
        # Geometric mean
        import numpy as np
        geo_mean = np.prod([(1 - d) for d in discount_decimals]) ** (1/len(discount_decimals))
        cumulative_discount_pct = (1 - geo_mean) * 100
        value_multiplier = geo_mean

    else:
        raise ValueError(f"Unknown method: {method}")

    # Calculate total discount amount
    total_discount = sum(d['discount_amount'] for d in individual_discounts)

    # Build step-by-step breakdown
    breakdown = []
    remaining_value_multiplier = 1.0

    for idx, disc in enumerate(individual_discounts, 1):
        discount_decimal = disc['impact_decimal']
        remaining_value_multiplier *= (1 - discount_decimal)

        step = {
            'step': idx,
            'encumbrance_type': disc['type'],
            'discount_percentage': disc['impact_percentage'],
            'remaining_value_multiplier': remaining_value_multiplier,
            'cumulative_discount_so_far': (1 - remaining_value_multiplier) * 100
        }
        breakdown.append(step)

    return {
        'method': method,
        'total_discount_amount': total_discount,
        'cumulative_discount_percentage': cumulative_discount_pct,
        'value_multiplier': value_multiplier,
        'breakdown': breakdown,
        'method_comparison': _compare_methods(discount_decimals) if len(discount_decimals) > 1 else None
    }


def _compare_methods(discount_decimals: List[float]) -> Dict:
    """
    Compare different cumulative discount calculation methods.

    Args:
        discount_decimals: List of individual discounts (as decimals)

    Returns:
        Comparison of multiplicative, additive, and geometric mean methods
    """
    import numpy as np

    # Multiplicative (standard)
    mult_multiplier = np.prod([1 - d for d in discount_decimals])
    mult_discount = (1 - mult_multiplier) * 100

    # Additive (simple sum)
    add_discount = sum(discount_decimals) * 100
    add_multiplier = 1 - sum(discount_decimals)

    # Geometric mean
    geo_multiplier = np.prod([1 - d for d in discount_decimals]) ** (1/len(discount_decimals))
    geo_discount = (1 - geo_multiplier) * 100

    return {
        'multiplicative': {
            'discount_percentage': mult_discount,
            'value_multiplier': mult_multiplier,
            'description': 'Standard method - most conservative'
        },
        'additive': {
            'discount_percentage': add_discount,
            'value_multiplier': add_multiplier,
            'description': 'Simple sum - may overstate discount'
        },
        'geometric_mean': {
            'discount_percentage': geo_discount,
            'value_multiplier': geo_multiplier,
            'description': 'Geometric average - middle ground'
        }
    }


def calculate_paired_sales_adjustment(
    paired_sales: List[Dict],
    property_area: float
) -> Optional[Dict]:
    """
    Calculate encumbrance discount from paired sales analysis.

    Compares sales with and without encumbrances to derive market-supported discount.

    Args:
        paired_sales: List of comparable sales data
        property_area: Subject property area in acres

    Returns:
        Paired sales analysis results or None if insufficient data
    """
    if not paired_sales or len(paired_sales) < 2:
        return None

    # Separate encumbered vs unencumbered sales
    encumbered_sales = [s for s in paired_sales if s.get('has_encumbrance', False)]
    unencumbered_sales = [s for s in paired_sales if not s.get('has_encumbrance', False)]

    if not encumbered_sales or not unencumbered_sales:
        return None

    # Calculate average price per acre for each group
    encumbered_avg_ppa = sum(s['sale_price'] / s['area_acres'] for s in encumbered_sales) / len(encumbered_sales)
    unencumbered_avg_ppa = sum(s['sale_price'] / s['area_acres'] for s in unencumbered_sales) / len(unencumbered_sales)

    # Calculate discount percentage
    discount_ppa = unencumbered_avg_ppa - encumbered_avg_ppa
    discount_percentage = (discount_ppa / unencumbered_avg_ppa * 100) if unencumbered_avg_ppa > 0 else 0

    return {
        'encumbered_sales_count': len(encumbered_sales),
        'unencumbered_sales_count': len(unencumbered_sales),
        'encumbered_avg_price_per_acre': encumbered_avg_ppa,
        'unencumbered_avg_price_per_acre': unencumbered_avg_ppa,
        'discount_per_acre': discount_ppa,
        'discount_percentage': discount_percentage,
        'encumbered_sales': encumbered_sales,
        'unencumbered_sales': unencumbered_sales
    }
