#!/usr/bin/env python3
"""
Score-to-Price Mapping Module for MCDA Sales Comparison

Transforms composite MCDA scores into indicated market values using:
- Linear interpolation between bracketing comparables
- OLS regression with confidence intervals
- Monotonic regression (isotonic) for small samples
- Theil-Sen robust regression for outlier tolerance
- Leave-one-out cross-validation for stability assessment

Author: Claude Code
Version: 1.0.0
Date: 2025-12-16
"""

import statistics
import math
from typing import Dict, List, Tuple, Any, Optional


# =============================================================================
# LINEAR INTERPOLATION
# =============================================================================

def interpolate_value(
    subject_score: float,
    comparables: List[Dict[str, Any]],
    subject_building_sf: float
) -> Dict[str, Any]:
    """
    Linear interpolation between bracketing comparables.

    Finds the two comparables that bracket the subject's composite score
    and linearly interpolates to determine indicated PSF value.

    Args:
        subject_score: Subject property's composite score (lower = better)
        comparables: List of comparables with 'score' and 'price_psf' keys
        subject_building_sf: Subject property's building size in SF

    Returns:
        Dictionary with:
        - indicated_value_psf: Interpolated price per SF
        - indicated_value_total: Total indicated value
        - lower_bracket: Comparable with score just below subject
        - upper_bracket: Comparable with score just above subject
        - interpolation_factor: Position between brackets (0-1)
        - confidence: 'high' if bracketed, 'low'/'extrapolated' otherwise
    """
    if not comparables:
        return {
            'indicated_value_psf': None,
            'indicated_value_total': None,
            'lower_bracket': None,
            'upper_bracket': None,
            'interpolation_factor': None,
            'confidence': 'insufficient_data'
        }

    # Sort comparables by score (ascending - lower score = better = higher price)
    sorted_comps = sorted(comparables, key=lambda x: x['score'])

    # Handle all same score
    if len(set(c['score'] for c in sorted_comps)) == 1:
        avg_price = statistics.mean([c['price_psf'] for c in sorted_comps])
        return {
            'indicated_value_psf': avg_price,
            'indicated_value_total': avg_price * subject_building_sf,
            'lower_bracket': sorted_comps[0],
            'upper_bracket': sorted_comps[-1],
            'interpolation_factor': 0.5,
            'confidence': 'medium'
        }

    # Find bracketing comparables
    lower_bracket = None
    upper_bracket = None

    for comp in sorted_comps:
        if comp['score'] <= subject_score:
            lower_bracket = comp
        if comp['score'] >= subject_score and upper_bracket is None:
            upper_bracket = comp

    # Handle extrapolation cases
    if lower_bracket is None:
        # Subject is better than all comparables - extrapolate from top two
        lower_bracket = sorted_comps[0]
        upper_bracket = sorted_comps[1] if len(sorted_comps) > 1 else sorted_comps[0]
        confidence = 'extrapolated'
    elif upper_bracket is None:
        # Subject is worse than all comparables - extrapolate from bottom two
        lower_bracket = sorted_comps[-2] if len(sorted_comps) > 1 else sorted_comps[-1]
        upper_bracket = sorted_comps[-1]
        confidence = 'extrapolated'
    else:
        confidence = 'high' if lower_bracket != upper_bracket else 'exact_match'

    # Calculate interpolation
    score_range = upper_bracket['score'] - lower_bracket['score']

    if score_range == 0:
        # Exact match - return the price
        interpolation_factor = 0.0
        indicated_psf = lower_bracket['price_psf']
    else:
        # Calculate interpolation factor
        interpolation_factor = (subject_score - lower_bracket['score']) / score_range

        # Interpolate price (note: lower score = higher price, so we invert the factor)
        price_range = lower_bracket['price_psf'] - upper_bracket['price_psf']
        indicated_psf = lower_bracket['price_psf'] - (interpolation_factor * price_range)

    # Clamp interpolation factor for reporting
    display_factor = max(0.0, min(1.0, interpolation_factor))

    return {
        'indicated_value_psf': indicated_psf,
        'indicated_value_total': indicated_psf * subject_building_sf,
        'lower_bracket': lower_bracket,
        'upper_bracket': upper_bracket,
        'interpolation_factor': display_factor,
        'confidence': confidence
    }


# =============================================================================
# REGRESSION VALUE MAPPING
# =============================================================================

def regression_value(
    subject_score: float,
    comparables: List[Dict[str, Any]],
    subject_building_sf: float,
    method: str = 'ols'
) -> Dict[str, Any]:
    """
    Fit price vs. score regression and predict subject value.

    Methods:
    - 'ols': Ordinary least squares
    - 'monotone': Isotonic regression (enforces decreasing price with score)
    - 'theil_sen': Robust slope estimate (resistant to outliers)

    Args:
        subject_score: Subject property's composite score
        comparables: List of comparables with 'score' and 'price_psf' keys
        subject_building_sf: Subject property's building size
        method: Regression method ('ols', 'monotone', 'theil_sen')

    Returns:
        Dictionary with regression results and predictions
    """
    if len(comparables) < 2:
        return {
            'indicated_value_psf': None,
            'indicated_value_total': None,
            'alpha': None,
            'beta': None,
            'r_squared': 0.0,
            'std_error': None,
            'confidence_interval_95': (None, None),
            'residuals': [],
            'outliers': [],
            'loo_r_squared': None,
            'loo_value_range_psf': (None, None),
            'method_used': method
        }

    # Extract scores and prices
    scores = [c['score'] for c in comparables]
    prices = [c['price_psf'] for c in comparables]
    n = len(scores)

    # Fit regression based on method
    if method == 'monotone':
        alpha, beta, fitted_prices = _fit_isotonic(scores, prices)
        method_used = 'monotone'
    elif method == 'theil_sen':
        alpha, beta = _fit_theil_sen(scores, prices)
        method_used = 'theil_sen'
    else:
        alpha, beta = _fit_ols(scores, prices)
        method_used = 'ols'

    # Calculate predicted value for subject
    indicated_psf = alpha + beta * subject_score

    # Calculate residuals
    predictions = [alpha + beta * s for s in scores]
    residuals = []
    for i, comp in enumerate(comparables):
        residuals.append({
            'id': comp.get('id', f'COMP_{i}'),
            'actual': prices[i],
            'predicted': predictions[i],
            'residual': prices[i] - predictions[i]
        })

    # Calculate R-squared
    mean_price = statistics.mean(prices)
    ss_tot = sum((p - mean_price) ** 2 for p in prices)
    ss_res = sum((p - pred) ** 2 for p, pred in zip(prices, predictions))
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    # Calculate standard error
    if n > 2:
        mse = ss_res / (n - 2)
        std_error = math.sqrt(mse)
    else:
        std_error = 0.0

    # Calculate 95% confidence interval
    if std_error > 0 and n > 2:
        # t-value for 95% CI (approximate for small n)
        t_val = 2.0 + 4.0 / n  # Rough approximation
        margin = t_val * std_error * math.sqrt(1 + 1/n + (subject_score - statistics.mean(scores))**2 / sum((s - statistics.mean(scores))**2 for s in scores)) if ss_tot > 0 else t_val * std_error
        ci_low = indicated_psf - margin
        ci_high = indicated_psf + margin
    else:
        ci_low = indicated_psf
        ci_high = indicated_psf

    # Identify outliers using MAD (Median Absolute Deviation) - robust to outliers
    # MAD threshold: |residual - median| > 3 * MAD (roughly equivalent to 2 std dev for normal)
    outliers = []
    residual_values = [r['residual'] for r in residuals]
    if len(residual_values) >= 3:
        median_resid = statistics.median(residual_values)
        abs_devs = sorted([abs(r - median_resid) for r in residual_values])
        mad = statistics.median(abs_devs)

        # Handle edge case where MAD=0 (many identical residuals)
        # Use mean absolute deviation from median as fallback
        if mad == 0:
            mean_abs_dev = statistics.mean(abs_devs) if abs_devs else 0
            mad_threshold = 2.5 * mean_abs_dev if mean_abs_dev > 0 else std_error * 2
        else:
            # Scale factor 1.4826 converts MAD to approximate std dev for normal distribution
            mad_threshold = 3.0 * mad * 1.4826

        for r in residuals:
            if abs(r['residual'] - median_resid) > mad_threshold:
                outliers.append(r)

    # Leave-one-out cross-validation
    loo_r_squared, loo_values = _calculate_loo(scores, prices, subject_score, method)

    return {
        'indicated_value_psf': indicated_psf,
        'indicated_value_total': indicated_psf * subject_building_sf,
        'alpha': alpha,
        'beta': beta,
        'r_squared': r_squared,
        'std_error': std_error,
        'confidence_interval_95': (ci_low, ci_high),
        'residuals': residuals,
        'outliers': outliers,
        'loo_r_squared': loo_r_squared,
        'loo_value_range_psf': (min(loo_values), max(loo_values)) if loo_values else (indicated_psf, indicated_psf),
        'method_used': method_used
    }


def _fit_ols(scores: List[float], prices: List[float]) -> Tuple[float, float]:
    """Fit ordinary least squares regression."""
    n = len(scores)
    mean_x = statistics.mean(scores)
    mean_y = statistics.mean(prices)

    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(scores, prices))
    denominator = sum((x - mean_x) ** 2 for x in scores)

    if denominator == 0:
        beta = 0
    else:
        beta = numerator / denominator

    alpha = mean_y - beta * mean_x
    return alpha, beta


def _fit_isotonic(scores: List[float], prices: List[float]) -> Tuple[float, float, List[float]]:
    """
    Fit isotonic (monotonic) regression.

    Enforces monotonically decreasing prices as scores increase.
    Uses pool adjacent violators algorithm (PAVA).
    """
    # Sort by score
    sorted_pairs = sorted(zip(scores, prices), key=lambda x: x[0])
    sorted_scores = [p[0] for p in sorted_pairs]
    sorted_prices = [p[1] for p in sorted_pairs]

    # Pool Adjacent Violators Algorithm for monotone decreasing
    fitted = sorted_prices.copy()
    n = len(fitted)

    # Iterate until monotonic
    changed = True
    while changed:
        changed = False
        i = 0
        while i < n - 1:
            if fitted[i] < fitted[i + 1]:  # Violation of decreasing
                # Pool and average
                avg = (fitted[i] + fitted[i + 1]) / 2
                fitted[i] = avg
                fitted[i + 1] = avg
                changed = True
            i += 1

    # Fit linear regression to monotonic values for alpha/beta
    alpha, beta = _fit_ols(sorted_scores, fitted)

    return alpha, beta, fitted


def _fit_theil_sen(scores: List[float], prices: List[float]) -> Tuple[float, float]:
    """
    Fit Theil-Sen robust regression.

    Uses median of all pairwise slopes - resistant to outliers.
    """
    n = len(scores)
    if n < 2:
        return statistics.mean(prices) if prices else 0, 0

    # Calculate all pairwise slopes
    slopes = []
    for i in range(n):
        for j in range(i + 1, n):
            if scores[j] != scores[i]:
                slope = (prices[j] - prices[i]) / (scores[j] - scores[i])
                slopes.append(slope)

    if not slopes:
        beta = 0
    else:
        beta = statistics.median(slopes)

    # Intercept is median of (y - beta*x)
    intercepts = [y - beta * x for x, y in zip(scores, prices)]
    alpha = statistics.median(intercepts)

    return alpha, beta


def _calculate_loo(
    scores: List[float],
    prices: List[float],
    subject_score: float,
    method: str
) -> Tuple[float, List[float]]:
    """
    Calculate leave-one-out cross-validation metrics.

    Returns:
        Tuple of (LOO R², list of subject predictions across iterations)
    """
    n = len(scores)
    if n < 3:
        return 0.0, []

    loo_errors = []
    subject_predictions = []

    for i in range(n):
        # Leave one out
        loo_scores = scores[:i] + scores[i+1:]
        loo_prices = prices[:i] + prices[i+1:]

        # Fit model without observation i
        if method == 'monotone':
            alpha, beta, _ = _fit_isotonic(loo_scores, loo_prices)
        elif method == 'theil_sen':
            alpha, beta = _fit_theil_sen(loo_scores, loo_prices)
        else:
            alpha, beta = _fit_ols(loo_scores, loo_prices)

        # Predict left-out observation
        predicted = alpha + beta * scores[i]
        loo_errors.append((prices[i] - predicted) ** 2)

        # Predict subject
        subject_predictions.append(alpha + beta * subject_score)

    # Calculate LOO R²
    mean_price = statistics.mean(prices)
    ss_tot = sum((p - mean_price) ** 2 for p in prices)
    ss_loo = sum(loo_errors)
    loo_r_squared = 1 - (ss_loo / ss_tot) if ss_tot > 0 else 0.0

    return loo_r_squared, subject_predictions


# =============================================================================
# METHOD RECONCILIATION
# =============================================================================

def reconcile_methods(
    interpolation: Dict[str, Any],
    regression: Dict[str, Any],
    subject_building_sf: float
) -> Dict[str, Any]:
    """
    Reconcile interpolation and regression results.

    Weighting factors consider:
    - Sample size (small n favors interpolation)
    - R² (high R² favors regression)
    - Bracket confidence (tight brackets favor interpolation)

    Args:
        interpolation: Results from interpolate_value()
        regression: Results from regression_value()
        subject_building_sf: Subject building size for total value

    Returns:
        Dictionary with reconciled value and methodology weights
    """
    interp_psf = interpolation.get('indicated_value_psf')
    regress_psf = regression.get('indicated_value_psf')

    # Handle missing values
    if interp_psf is None and regress_psf is None:
        return {
            'indicated_value_psf': None,
            'indicated_value_total': None,
            'method_weights': {'interpolation': 0.0, 'regression': 0.0},
            'reconciliation_rationale': 'Insufficient data for both methods'
        }
    elif interp_psf is None:
        return {
            'indicated_value_psf': regress_psf,
            'indicated_value_total': regress_psf * subject_building_sf,
            'method_weights': {'interpolation': 0.0, 'regression': 1.0},
            'reconciliation_rationale': 'Only regression available'
        }
    elif regress_psf is None:
        return {
            'indicated_value_psf': interp_psf,
            'indicated_value_total': interp_psf * subject_building_sf,
            'method_weights': {'interpolation': 1.0, 'regression': 0.0},
            'reconciliation_rationale': 'Only interpolation available'
        }

    # Calculate weighting factors
    r_squared = regression.get('r_squared', 0)
    confidence = interpolation.get('confidence', 'medium')
    n_residuals = len(regression.get('residuals', []))

    # Base weights
    interp_weight = 0.50
    regress_weight = 0.50

    # Adjust for sample size (small n favors interpolation)
    if n_residuals < 5:
        interp_weight += 0.15
        regress_weight -= 0.15
    elif n_residuals >= 10:
        interp_weight -= 0.10
        regress_weight += 0.10

    # Adjust for R² (high R² favors regression)
    if r_squared > 0.80:
        regress_weight += 0.10
        interp_weight -= 0.10
    elif r_squared < 0.50:
        regress_weight -= 0.15
        interp_weight += 0.15

    # Adjust for interpolation confidence
    if confidence == 'high':
        interp_weight += 0.05
    elif confidence in ('low', 'extrapolated'):
        interp_weight -= 0.10
        regress_weight += 0.10

    # Normalize weights
    total = interp_weight + regress_weight
    interp_weight /= total
    regress_weight /= total

    # Calculate weighted average
    reconciled_psf = interp_weight * interp_psf + regress_weight * regress_psf

    # Build rationale
    rationale_parts = []
    if n_residuals < 7:
        rationale_parts.append(f"Small sample (n={n_residuals}) favors interpolation")
    if r_squared > 0.70:
        rationale_parts.append(f"Strong model fit (R²={r_squared:.2f}) supports regression")
    if confidence == 'high':
        rationale_parts.append("Subject well-bracketed by comparables")
    elif confidence == 'extrapolated':
        rationale_parts.append("Subject outside comparable range - extrapolation required")

    rationale = '; '.join(rationale_parts) if rationale_parts else 'Standard weighting applied'

    return {
        'indicated_value_psf': reconciled_psf,
        'indicated_value_total': reconciled_psf * subject_building_sf,
        'method_weights': {
            'interpolation': round(interp_weight, 2),
            'regression': round(regress_weight, 2)
        },
        'reconciliation_rationale': rationale
    }


if __name__ == '__main__':
    print("MCDA Sales Comparison - Score-to-Price Module")
    print("Run with pytest for full test suite")

    # Example usage
    sample_comps = [
        {'id': 'C1', 'score': 2.5, 'price_psf': 100, 'price_total': 5000000, 'building_sf': 50000},
        {'id': 'C2', 'score': 3.5, 'price_psf': 90, 'price_total': 4500000, 'building_sf': 50000},
        {'id': 'C3', 'score': 4.5, 'price_psf': 80, 'price_total': 4000000, 'building_sf': 50000},
    ]

    print("\nInterpolation for subject score 3.0:")
    result = interpolate_value(3.0, sample_comps, 50000)
    print(f"  Indicated PSF: ${result['indicated_value_psf']:.2f}")
    print(f"  Confidence: {result['confidence']}")

    print("\nOLS Regression for subject score 3.0:")
    result = regression_value(3.0, sample_comps, 50000, method='ols')
    print(f"  Indicated PSF: ${result['indicated_value_psf']:.2f}")
    print(f"  R²: {result['r_squared']:.3f}")
    print(f"  Slope: ${result['beta']:.2f}/score point")
