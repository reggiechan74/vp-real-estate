"""
Market Rent Analysis Module
Analyzes comparable rents, applies adjustments, and concludes market rent
"""

from typing import Dict, List, Optional, Any
import statistics


def analyze_market_rent(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze market rent using comparable rents and adjustments.

    Args:
        data: Validated input data dictionary

    Returns:
        Dictionary with:
            - comparable_rents: List of comparable rent data
            - statistics: Mean, median, range of comps
            - adjustments: Applied adjustments (if any)
            - concluded_rent: Market rent conclusion
    """
    land_rent = data['land_rent']
    market_data = data['market_data']
    comparable_rents = market_data['comparable_rents']

    # Extract rent values
    rent_values = [comp['annual_rent'] for comp in comparable_rents]

    # Calculate statistics
    stats = {
        'mean': statistics.mean(rent_values),
        'median': statistics.median(rent_values),
        'min': min(rent_values),
        'max': max(rent_values),
        'count': len(rent_values),
        'range': max(rent_values) - min(rent_values)
    }

    # Subject property rent
    subject_rent = land_rent['annual_rent']

    # Compare subject to market
    # If subject rent is within market range, use it as market rent
    # Otherwise, use market median as conclusion
    if stats['min'] <= subject_rent <= stats['max']:
        concluded_rent = subject_rent
        conclusion_method = "Subject rent within market range"
    else:
        concluded_rent = stats['median']
        conclusion_method = "Market median (subject rent outside market range)"

    # Calculate variance from market
    variance_from_market = ((subject_rent - stats['median']) / stats['median']) * 100

    return {
        'comparable_rents': comparable_rents,
        'rent_statistics': stats,
        'subject_rent': subject_rent,
        'concluded_market_rent': concluded_rent,
        'conclusion_method': conclusion_method,
        'variance_from_market_pct': variance_from_market,
        'adjustments_applied': []  # Placeholder for future adjustment logic
    }
