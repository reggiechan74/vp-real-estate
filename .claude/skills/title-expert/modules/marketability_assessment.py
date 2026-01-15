#!/usr/bin/env python3
"""
Marketability Assessment Module

Assess property marketability based on title defects, encumbrances,
buyer pool impact, financing availability, and liquidity.
"""

from typing import Dict, List


def assess_marketability(
    encumbrance_analysis: Dict,
    validation_results: Dict,
    property_data: Dict
) -> Dict:
    """
    Comprehensive marketability assessment.

    Args:
        encumbrance_analysis: Results from encumbrance analysis
        validation_results: Results from registration validation
        property_data: Property information

    Returns:
        Marketability assessment dictionary
    """
    # Score components
    encumbrance_score = _score_encumbrances(encumbrance_analysis)
    defect_score = _score_defects(validation_results)
    financing_score = _score_financing_availability(encumbrance_analysis)
    liquidity_score = _score_liquidity(encumbrance_analysis, validation_results)

    # Calculate overall score (0-100, higher = more marketable)
    weights = {
        'encumbrances': 0.35,
        'defects': 0.30,
        'financing': 0.20,
        'liquidity': 0.15
    }

    overall_score = (
        encumbrance_score * weights['encumbrances'] +
        defect_score * weights['defects'] +
        financing_score * weights['financing'] +
        liquidity_score * weights['liquidity']
    )

    # Determine marketability rating
    rating = _get_marketability_rating(overall_score)

    # Calculate buyer pool impact
    buyer_pool = _assess_buyer_pool_impact(
        encumbrance_analysis,
        validation_results,
        overall_score
    )

    # Generate recommendations
    recommendations = _generate_marketability_recommendations(
        rating,
        encumbrance_analysis,
        validation_results
    )

    return {
        'overall_score': round(overall_score, 1),
        'rating': rating,
        'component_scores': {
            'encumbrances': round(encumbrance_score, 1),
            'defects': round(defect_score, 1),
            'financing': round(financing_score, 1),
            'liquidity': round(liquidity_score, 1)
        },
        'buyer_pool': buyer_pool,
        'financing_availability': _assess_financing_details(encumbrance_analysis),
        'recommendations': recommendations,
        'summary': _generate_marketability_summary(rating, overall_score)
    }


def _score_encumbrances(encumbrance_analysis: Dict) -> float:
    """
    Score based on encumbrances (0-100, higher = better).

    Args:
        encumbrance_analysis: Encumbrance analysis results

    Returns:
        Score (0-100)
    """
    summary = encumbrance_analysis.get('summary', {})
    severity_counts = summary.get('by_severity', {})

    # Start at 100, deduct points
    score = 100.0

    # Deduct for critical issues (30 points each)
    critical = severity_counts.get('CRITICAL', 0)
    score -= critical * 30

    # Deduct for high severity (15 points each)
    high = severity_counts.get('HIGH', 0)
    score -= high * 15

    # Deduct for medium severity (5 points each)
    medium = severity_counts.get('MEDIUM', 0)
    score -= medium * 5

    # Deduct for low severity (1 point each)
    low = severity_counts.get('LOW', 0)
    score -= low * 1

    return max(score, 0.0)


def _score_defects(validation_results: Dict) -> float:
    """
    Score based on registration defects (0-100, higher = better).

    Args:
        validation_results: Validation results

    Returns:
        Score (0-100)
    """
    validity = validation_results.get('validity', {})
    status = validity.get('status', 'VALID')

    # Map status to score
    status_scores = {
        'VALID': 100.0,
        'MINOR_ISSUES': 85.0,
        'NEEDS_REVIEW': 60.0,
        'QUESTIONABLE': 30.0,
        'INVALID': 0.0
    }

    return status_scores.get(status, 50.0)


def _score_financing_availability(encumbrance_analysis: Dict) -> float:
    """
    Score based on financing availability (0-100, higher = better).

    Args:
        encumbrance_analysis: Encumbrance analysis results

    Returns:
        Score (0-100)
    """
    score = 100.0

    # Check for financing impediments
    critical_issues = encumbrance_analysis.get('critical_issues', [])
    high_issues = encumbrance_analysis.get('high_issues', [])

    # Critical issues severely impact financing
    for issue in critical_issues:
        if issue['type'] in ['Lien', 'Litigation Notice', 'Court Order']:
            score -= 40  # Lenders won't finance with active liens/litigation

    # High issues moderately impact financing
    for issue in high_issues:
        if issue['type'] == 'Mortgage':
            score -= 10  # Existing mortgages (if not discharged)
        elif issue['type'] == 'Easement':
            score -= 5  # Major easements may concern lenders

    return max(score, 0.0)


def _score_liquidity(
    encumbrance_analysis: Dict,
    validation_results: Dict
) -> float:
    """
    Score based on liquidity/marketability to buyers (0-100, higher = better).

    Args:
        encumbrance_analysis: Encumbrance analysis results
        validation_results: Validation results

    Returns:
        Score (0-100)
    """
    score = 100.0

    # Defects reduce liquidity
    validity = validation_results.get('validity', {})
    if not validity.get('marketable', True):
        score -= 40

    # Count encumbrances that reduce buyer pool
    summary = encumbrance_analysis.get('summary', {})
    total_encs = summary.get('total', 0)

    # Deduct for each encumbrance (complexity reduces liquidity)
    if total_encs > 10:
        score -= 30  # Very complex title
    elif total_encs > 5:
        score -= 15  # Moderately complex
    elif total_encs > 2:
        score -= 5   # Slightly complex

    return max(score, 0.0)


def _get_marketability_rating(score: float) -> str:
    """
    Convert score to rating.

    Args:
        score: Marketability score (0-100)

    Returns:
        Rating string
    """
    if score >= 85:
        return 'EXCELLENT'
    elif score >= 70:
        return 'GOOD'
    elif score >= 50:
        return 'FAIR'
    elif score >= 30:
        return 'POOR'
    else:
        return 'UNMARKETABLE'


def _assess_buyer_pool_impact(
    encumbrance_analysis: Dict,
    validation_results: Dict,
    overall_score: float
) -> Dict:
    """
    Assess impact on buyer pool.

    Args:
        encumbrance_analysis: Encumbrance analysis results
        validation_results: Validation results
        overall_score: Overall marketability score

    Returns:
        Buyer pool impact dictionary
    """
    # Estimate percentage of buyer pool that would consider property
    if overall_score >= 85:
        buyer_pool_pct = 90
        description = 'Broad buyer pool - minimal title concerns'
    elif overall_score >= 70:
        buyer_pool_pct = 70
        description = 'Good buyer pool - some buyers may be deterred by encumbrances'
    elif overall_score >= 50:
        buyer_pool_pct = 40
        description = 'Limited buyer pool - many buyers will avoid due to title issues'
    elif overall_score >= 30:
        buyer_pool_pct = 15
        description = 'Severely limited buyer pool - most buyers will not consider'
    else:
        buyer_pool_pct = 5
        description = 'Minimal buyer pool - only sophisticated buyers with legal expertise'

    # Identify buyer types likely to proceed
    buyer_types = _identify_buyer_types(overall_score, encumbrance_analysis)

    return {
        'estimated_percentage': buyer_pool_pct,
        'description': description,
        'buyer_types': buyer_types
    }


def _identify_buyer_types(score: float, encumbrance_analysis: Dict) -> List[str]:
    """
    Identify types of buyers likely to proceed.

    Args:
        score: Marketability score
        encumbrance_analysis: Encumbrance analysis results

    Returns:
        List of buyer type descriptions
    """
    buyer_types = []

    if score >= 85:
        buyer_types = [
            'Retail buyers (homeowners, small investors)',
            'Institutional buyers',
            'Developers',
            'All buyer categories'
        ]
    elif score >= 70:
        buyer_types = [
            'Sophisticated retail buyers',
            'Institutional buyers (with conditions)',
            'Developers familiar with title issues'
        ]
    elif score >= 50:
        buyer_types = [
            'Experienced investors only',
            'Developers with legal resources',
            'Buyers willing to resolve title issues'
        ]
    elif score >= 30:
        buyer_types = [
            'Highly sophisticated buyers only',
            'Buyers with specific use that accommodates encumbrances',
            'Speculative investors at significant discount'
        ]
    else:
        buyer_types = [
            'Minimal buyer interest',
            'Only buyers with ability to resolve critical defects',
            'May require legal remediation before sale'
        ]

    return buyer_types


def _assess_financing_details(encumbrance_analysis: Dict) -> Dict:
    """
    Assess detailed financing availability.

    Args:
        encumbrance_analysis: Encumbrance analysis results

    Returns:
        Financing details dictionary
    """
    critical = encumbrance_analysis.get('critical_issues', [])
    high = encumbrance_analysis.get('high_issues', [])

    # Determine financing availability
    has_liens = any(i['type'] == 'Lien' for i in critical)
    has_litigation = any(i['type'] in ['Litigation Notice', 'Court Order'] for i in critical)
    has_mortgages = any(i['type'] == 'Mortgage' for i in high)

    if has_liens or has_litigation:
        availability = 'NOT AVAILABLE'
        details = 'Standard financing unavailable due to critical title issues'
        lender_types = []
    elif has_mortgages:
        availability = 'LIMITED'
        details = 'Financing available subject to discharge of existing mortgages'
        lender_types = ['Traditional lenders (with conditions)', 'Private lenders']
    else:
        availability = 'READILY AVAILABLE'
        details = 'No significant impediments to standard financing'
        lender_types = ['Traditional lenders', 'Credit unions', 'Private lenders']

    return {
        'availability': availability,
        'details': details,
        'lender_types': lender_types
    }


def _generate_marketability_recommendations(
    rating: str,
    encumbrance_analysis: Dict,
    validation_results: Dict
) -> List[str]:
    """
    Generate recommendations to improve marketability.

    Args:
        rating: Marketability rating
        encumbrance_analysis: Encumbrance analysis results
        validation_results: Validation results

    Returns:
        List of recommendations
    """
    recommendations = []

    # Critical issues first
    critical = encumbrance_analysis.get('critical_issues', [])
    if critical:
        recommendations.append(
            f'PRIORITY: Resolve {len(critical)} critical issue(s) before marketing property'
        )
        for issue in critical[:3]:  # Top 3
            recommendations.append(f"  - Discharge/resolve {issue['type']}: {issue['description'][:100]}")

    # Registration defects
    validity = validation_results.get('validity', {})
    if validity.get('status') in ['INVALID', 'QUESTIONABLE']:
        recommendations.append(
            'Obtain legal opinion on registration defects and rectify critical issues'
        )

    # High severity encumbrances
    high = encumbrance_analysis.get('high_issues', [])
    if high:
        recommendations.append(
            f'Address {len(high)} high-severity encumbrance(s) to improve marketability'
        )

    # General recommendations by rating
    if rating == 'UNMARKETABLE':
        recommendations.append(
            'Property currently unmarketable - extensive remediation required before sale'
        )
    elif rating == 'POOR':
        recommendations.append(
            'Expect significant buyer resistance and value discount (20-30%)'
        )
    elif rating == 'FAIR':
        recommendations.append(
            'Market with full disclosure; expect moderate value discount (10-20%)'
        )
    elif rating == 'GOOD':
        recommendations.append(
            'Marketable with minor conditions; minimal value impact (<10%)'
        )
    else:  # EXCELLENT
        recommendations.append(
            'Excellent marketability - proceed with normal marketing strategy'
        )

    return recommendations


def _generate_marketability_summary(rating: str, score: float) -> str:
    """
    Generate marketability summary statement.

    Args:
        rating: Marketability rating
        score: Overall score

    Returns:
        Summary statement
    """
    summaries = {
        'EXCELLENT': f'Property has excellent marketability (score: {score:.1f}/100). Title is clean with minimal encumbrances. Suitable for all buyer types and readily financeable.',
        'GOOD': f'Property has good marketability (score: {score:.1f}/100). Some encumbrances present but manageable. Suitable for most buyer types with standard financing available.',
        'FAIR': f'Property has fair marketability (score: {score:.1f}/100). Moderate title issues present. Buyer pool somewhat limited; financing may require conditions.',
        'POOR': f'Property has poor marketability (score: {score:.1f}/100). Significant title issues present. Limited buyer pool; financing difficult to obtain.',
        'UNMARKETABLE': f'Property is currently unmarketable (score: {score:.1f}/100). Critical title defects require resolution before property can be marketed effectively.'
    }

    return summaries.get(rating, f'Marketability score: {score:.1f}/100')


def calculate_value_impact(
    marketability_assessment: Dict,
    encumbrance_analysis: Dict
) -> Dict:
    """
    Calculate estimated value impact from title issues.

    Args:
        marketability_assessment: Marketability assessment results
        encumbrance_analysis: Encumbrance analysis results

    Returns:
        Value impact dictionary with percentage ranges
    """
    rating = marketability_assessment.get('rating', 'FAIR')
    overall_score = marketability_assessment.get('overall_score', 50)

    # Base discount by rating
    base_discounts = {
        'EXCELLENT': {'min': 0.0, 'max': 2.0},
        'GOOD': {'min': 2.0, 'max': 8.0},
        'FAIR': {'min': 8.0, 'max': 18.0},
        'POOR': {'min': 18.0, 'max': 35.0},
        'UNMARKETABLE': {'min': 35.0, 'max': 60.0}
    }

    base = base_discounts.get(rating, {'min': 5.0, 'max': 15.0})

    # Add encumbrance-specific impacts
    enc_summary = encumbrance_analysis.get('summary', {})
    total_enc_impact = enc_summary.get('average_value_impact', 0.0)

    # Combined impact (use higher of base or encumbrance-specific)
    min_impact = max(base['min'], total_enc_impact * 0.5)
    max_impact = max(base['max'], total_enc_impact * 1.5)

    # Likely impact (midpoint)
    likely_impact = (min_impact + max_impact) / 2

    return {
        'min_discount_pct': round(min_impact, 1),
        'max_discount_pct': round(max_impact, 1),
        'likely_discount_pct': round(likely_impact, 1),
        'basis': f'{rating} marketability rating (score: {overall_score:.1f}/100)',
        'interpretation': _interpret_value_impact(min_impact, max_impact, likely_impact)
    }


def _interpret_value_impact(min_pct: float, max_pct: float, likely_pct: float) -> str:
    """
    Interpret value impact percentage.

    Args:
        min_pct: Minimum discount percentage
        max_pct: Maximum discount percentage
        likely_pct: Likely discount percentage

    Returns:
        Interpretation string
    """
    if likely_pct < 5:
        return 'Minimal value impact - title issues are minor and typical for properties of this type'
    elif likely_pct < 15:
        return 'Moderate value impact - title issues will require buyer concessions but property remains marketable'
    elif likely_pct < 30:
        return 'Significant value impact - title issues substantially reduce market value and buyer pool'
    else:
        return 'Severe value impact - title issues create major obstacles to sale; remediation strongly recommended'
