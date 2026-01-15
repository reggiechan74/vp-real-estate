"""
Cost Reconciliation Module

Reconciles cost approach value with market approach (if comparable sales available).
"""

from typing import Dict, List, Optional


def reconcile_with_market(
    depreciated_replacement_cost: float,
    market_data: Optional[Dict] = None,
    asset_type: str = ''
) -> Dict:
    """
    Reconcile cost approach with market sales (if available).

    Cost approach provides upper bound (replacement cost).
    Market approach provides actual transaction evidence.

    Args:
        depreciated_replacement_cost: Depreciated replacement cost from cost approach
        market_data: Optional dictionary with comparable sales
        asset_type: Type of asset being valued

    Returns:
        Dictionary with reconciliation analysis

    Example:
        >>> market = {'comparable_sales': [
        ...     {'sale_price': 180000, 'asset_type': 'Transmission tower'},
        ...     {'sale_price': 195000, 'asset_type': 'Transmission tower'}
        ... ]}
        >>> reconciliation = reconcile_with_market(179716, market)
        >>> print(f"Reconciled value: ${reconciliation['reconciled_value']:,.2f}")
        Reconciled value: $182,000.00
    """
    if market_data is None or not market_data.get('comparable_sales'):
        # No market data - cost approach is only indication
        return {
            'cost_approach_value': depreciated_replacement_cost,
            'market_approach_available': False,
            'reconciled_value': depreciated_replacement_cost,
            'reconciliation_method': 'Cost approach only (no market data)',
            'confidence_level': 'Medium',
            'notes': (
                'Market data not available. Cost approach provides replacement cost indication. '
                'Consider seeking comparable sales to validate conclusion.'
            )
        }

    # Extract comparable sales
    comparable_sales = market_data.get('comparable_sales', [])

    # Filter comparables by asset type (if specified)
    if asset_type:
        relevant_sales = [
            sale for sale in comparable_sales
            if sale.get('asset_type', '').lower() == asset_type.lower()
        ]
    else:
        relevant_sales = comparable_sales

    if not relevant_sales:
        return {
            'cost_approach_value': depreciated_replacement_cost,
            'market_approach_available': False,
            'comparable_sales_count': len(comparable_sales),
            'relevant_sales_count': 0,
            'reconciled_value': depreciated_replacement_cost,
            'reconciliation_method': 'Cost approach only (no relevant comparables)',
            'confidence_level': 'Medium',
            'notes': f'No comparable sales found for {asset_type}. Using cost approach.'
        }

    # Calculate market statistics
    sale_prices = [sale.get('sale_price', 0) for sale in relevant_sales]
    market_stats = _calculate_market_statistics(sale_prices)

    # Compare cost approach to market
    cost_value = depreciated_replacement_cost
    market_median = market_stats['median']

    variance = cost_value - market_median
    variance_pct = (variance / market_median * 100) if market_median > 0 else 0

    # Reconciliation logic
    if abs(variance_pct) <= 10:
        # Close agreement (<10% variance)
        reconciled_value = (cost_value + market_median) / 2
        reconciliation_method = 'Average of cost and market (close agreement)'
        confidence_level = 'High'
        notes = f'Cost approach and market approach closely aligned (variance: {variance_pct:.1f}%)'

    elif cost_value > market_median * 1.20:
        # Cost significantly higher (>20%)
        # Market typically preferred when cost is high
        reconciled_value = market_median * 1.05  # Give slight weight to cost
        reconciliation_method = 'Market approach emphasized (cost appears high)'
        confidence_level = 'Medium'
        notes = (
            f'Cost approach {variance_pct:.1f}% higher than market. '
            'Market data given greater weight. Consider functional/external obsolescence.'
        )

    elif market_median > cost_value * 1.20:
        # Market significantly higher (>20%)
        # Unusual - verify market data quality
        reconciled_value = (cost_value * 1.10 + market_median) / 2
        reconciliation_method = 'Weighted average (verify market data quality)'
        confidence_level = 'Low'
        notes = (
            f'Market {variance_pct:.1f}% higher than cost. Unusual situation. '
            'Verify comparable quality and special purchaser considerations.'
        )

    else:
        # Moderate variance (10-20%)
        # Weight both approaches
        reconciled_value = (cost_value * 0.4 + market_median * 0.6)
        reconciliation_method = 'Weighted average (60% market, 40% cost)'
        confidence_level = 'Medium-High'
        notes = f'Moderate variance ({variance_pct:.1f}%). Both approaches considered with market emphasized.'

    return {
        'cost_approach_value': cost_value,
        'market_approach_available': True,
        'comparable_sales_count': len(comparable_sales),
        'relevant_sales_count': len(relevant_sales),
        'market_statistics': market_stats,
        'variance_amount': variance,
        'variance_percentage': variance_pct,
        'reconciled_value': reconciled_value,
        'reconciliation_method': reconciliation_method,
        'confidence_level': confidence_level,
        'notes': notes,
        'comparable_sales_detail': _format_comparable_sales(relevant_sales)
    }


def _calculate_market_statistics(sale_prices: List[float]) -> Dict:
    """
    Calculate market statistics from sale prices.

    Args:
        sale_prices: List of comparable sale prices

    Returns:
        Dictionary with mean, median, min, max, std dev
    """
    if not sale_prices:
        return {
            'count': 0,
            'mean': 0,
            'median': 0,
            'min': 0,
            'max': 0,
            'range': 0,
            'std_dev': 0
        }

    import statistics

    count = len(sale_prices)
    mean = statistics.mean(sale_prices)
    median = statistics.median(sale_prices)
    min_price = min(sale_prices)
    max_price = max(sale_prices)
    price_range = max_price - min_price

    # Standard deviation (only if >1 sale)
    std_dev = statistics.stdev(sale_prices) if count > 1 else 0

    return {
        'count': count,
        'mean': mean,
        'median': median,
        'min': min_price,
        'max': max_price,
        'range': price_range,
        'std_dev': std_dev,
        'coefficient_of_variation': (std_dev / mean * 100) if mean > 0 else 0
    }


def _format_comparable_sales(sales: List[Dict]) -> List[Dict]:
    """
    Format comparable sales for reporting.

    Args:
        sales: List of comparable sale dictionaries

    Returns:
        Formatted list of sales with key fields
    """
    formatted = []

    for idx, sale in enumerate(sales, start=1):
        formatted.append({
            'comp_number': idx,
            'sale_price': sale.get('sale_price', 0),
            'asset_type': sale.get('asset_type', 'Unknown'),
            'sale_date': sale.get('sale_date', 'Not provided'),
            'location': sale.get('location', 'Not provided'),
            'condition': sale.get('condition', 'Not provided'),
            'notes': sale.get('notes', '')
        })

    return formatted


def calculate_confidence_score(
    depreciated_replacement_cost: float,
    market_data: Optional[Dict],
    depreciation_data: Dict
) -> Dict:
    """
    Calculate confidence score for valuation conclusion.

    Factors considered:
    - Availability of market data
    - Quality of depreciation estimates
    - Variance between approaches
    - Data currency and relevance

    Args:
        depreciated_replacement_cost: Cost approach value
        market_data: Market approach data
        depreciation_data: Depreciation analysis data

    Returns:
        Dictionary with confidence score and factors

    Example:
        >>> confidence = calculate_confidence_score(179716, market_data, dep_data)
        >>> print(f"Confidence: {confidence['score']}/100 - {confidence['rating']}")
        Confidence: 75/100 - Medium-High
    """
    score = 50  # Start at 50 (neutral)
    factors = []

    # Market data availability (+/- 20 points)
    if market_data and market_data.get('comparable_sales'):
        comp_count = len(market_data['comparable_sales'])
        if comp_count >= 5:
            score += 20
            factors.append(f'Strong market data ({comp_count} comparables): +20')
        elif comp_count >= 3:
            score += 15
            factors.append(f'Good market data ({comp_count} comparables): +15')
        elif comp_count >= 1:
            score += 10
            factors.append(f'Limited market data ({comp_count} comparable): +10')
    else:
        score -= 15
        factors.append('No market data: -15')

    # Depreciation quality (+/- 15 points)
    physical_condition = depreciation_data.get('physical_condition', '')
    if physical_condition in ['Excellent', 'Good', 'Fair']:
        score += 10
        factors.append(f'Physical condition assessed ({physical_condition}): +10')
    elif physical_condition in ['Poor', 'Very Poor']:
        score += 5
        factors.append(f'Condition documented but poor ({physical_condition}): +5')
    else:
        score -= 5
        factors.append('Physical condition not documented: -5')

    # Age/life reasonableness (+/- 10 points)
    effective_age = depreciation_data.get('effective_age_years', 0)
    economic_life = depreciation_data.get('economic_life_years', 1)
    if economic_life > 0:
        age_ratio = effective_age / economic_life
        if 0 <= age_ratio <= 0.8:  # Within expected range
            score += 10
            factors.append(f'Age/life ratio reasonable ({age_ratio:.1%}): +10')
        else:
            score += 0
            factors.append(f'Age/life ratio questionable ({age_ratio:.1%}): 0')

    # Functional/external obsolescence documentation (+/- 5 points)
    func_obs = depreciation_data.get('functional_obsolescence', 0)
    ext_obs = depreciation_data.get('external_obsolescence', 0)
    if func_obs > 0 or ext_obs > 0:
        score += 5
        factors.append('Obsolescence factors documented: +5')

    # Ensure score is within 0-100 range
    score = max(0, min(100, score))

    # Rating
    if score >= 85:
        rating = 'Very High'
    elif score >= 70:
        rating = 'High'
    elif score >= 55:
        rating = 'Medium-High'
    elif score >= 40:
        rating = 'Medium'
    elif score >= 25:
        rating = 'Low-Medium'
    else:
        rating = 'Low'

    return {
        'score': score,
        'rating': rating,
        'factors': factors,
        'interpretation': _get_confidence_interpretation(rating)
    }


def _get_confidence_interpretation(rating: str) -> str:
    """Get interpretation text for confidence rating."""
    interpretations = {
        'Very High': 'Strong market data and well-documented depreciation analysis. High confidence in conclusion.',
        'High': 'Good market support and reasonable depreciation estimates. Reliable conclusion.',
        'Medium-High': 'Adequate market data or depreciation analysis. Conclusion is reasonably reliable.',
        'Medium': 'Limited market data or depreciation estimates have uncertainty. Conclusion is tentative.',
        'Low-Medium': 'Weak market support and/or depreciation assumptions require verification.',
        'Low': 'Insufficient data for reliable conclusion. Additional research recommended.'
    }
    return interpretations.get(rating, 'No interpretation available')
