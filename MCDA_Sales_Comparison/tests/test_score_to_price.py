#!/usr/bin/env python3
"""
Test Suite for MCDA Sales Comparison Score-to-Price Module

Tests cover:
- Linear interpolation between bracketing comparables
- OLS regression for price prediction
- Monotonic regression for small samples
- Theil-Sen robust regression
- Leave-one-out cross-validation
- Method reconciliation

TDD Approach: Write tests first, then implement score_to_price.py
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


# =============================================================================
# TEST DATA FIXTURES
# =============================================================================

@pytest.fixture
def sample_comparables():
    """Sample comparables with scores and prices for testing"""
    return [
        {'id': 'COMP_1', 'score': 2.50, 'price_psf': 100.00, 'price_total': 4850000, 'building_sf': 48500},
        {'id': 'COMP_2', 'score': 3.20, 'price_psf': 92.00, 'price_total': 4600000, 'building_sf': 50000},
        {'id': 'COMP_3', 'score': 3.80, 'price_psf': 85.00, 'price_total': 4250000, 'building_sf': 50000},
        {'id': 'COMP_4', 'score': 4.50, 'price_psf': 76.00, 'price_total': 3800000, 'building_sf': 50000},
        {'id': 'COMP_5', 'score': 5.00, 'price_psf': 70.00, 'price_total': 3500000, 'building_sf': 50000},
    ]


@pytest.fixture
def subject_property():
    """Sample subject property"""
    return {'building_sf': 50000}


# =============================================================================
# INTERPOLATION TESTS
# =============================================================================

class TestInterpolateValue:
    """Tests for interpolate_value() function"""

    def test_interpolation_between_brackets(self, sample_comparables, subject_property):
        """Subject score between two comparables should interpolate correctly"""
        from score_to_price import interpolate_value

        subject_score = 3.50  # Between COMP_2 (3.20) and COMP_3 (3.80)
        result = interpolate_value(subject_score, sample_comparables, subject_property['building_sf'])

        # Should interpolate between $92/SF and $85/SF
        assert result['indicated_value_psf'] is not None
        assert 85.0 <= result['indicated_value_psf'] <= 92.0
        assert result['lower_bracket']['id'] == 'COMP_2'
        assert result['upper_bracket']['id'] == 'COMP_3'

    def test_interpolation_exact_match(self, sample_comparables, subject_property):
        """Subject score matching a comparable should return that price"""
        from score_to_price import interpolate_value

        subject_score = 3.20  # Exact match with COMP_2
        result = interpolate_value(subject_score, sample_comparables, subject_property['building_sf'])

        # Should return COMP_2's price exactly
        assert result['indicated_value_psf'] == pytest.approx(92.0, rel=0.01)

    def test_interpolation_extrapolation_low(self, sample_comparables, subject_property):
        """Subject score better than all comparables should extrapolate"""
        from score_to_price import interpolate_value

        subject_score = 2.00  # Better than best comparable (2.50)
        result = interpolate_value(subject_score, sample_comparables, subject_property['building_sf'])

        # Should extrapolate above $100/SF
        assert result['indicated_value_psf'] > 100.0
        assert result['confidence'] in ('low', 'extrapolated')

    def test_interpolation_extrapolation_high(self, sample_comparables, subject_property):
        """Subject score worse than all comparables should extrapolate"""
        from score_to_price import interpolate_value

        subject_score = 5.50  # Worse than worst comparable (5.00)
        result = interpolate_value(subject_score, sample_comparables, subject_property['building_sf'])

        # Should extrapolate below $70/SF
        assert result['indicated_value_psf'] < 70.0

    def test_interpolation_calculates_total_value(self, sample_comparables, subject_property):
        """Should calculate indicated total value from PSF"""
        from score_to_price import interpolate_value

        subject_score = 3.50
        result = interpolate_value(subject_score, sample_comparables, subject_property['building_sf'])

        expected_total = result['indicated_value_psf'] * subject_property['building_sf']
        assert result['indicated_value_total'] == pytest.approx(expected_total, rel=0.01)

    def test_interpolation_factor_calculated(self, sample_comparables, subject_property):
        """Interpolation factor should be between 0 and 1 for bracketed values"""
        from score_to_price import interpolate_value

        subject_score = 3.50
        result = interpolate_value(subject_score, sample_comparables, subject_property['building_sf'])

        assert 0.0 <= result['interpolation_factor'] <= 1.0


# =============================================================================
# REGRESSION TESTS
# =============================================================================

class TestRegressionValue:
    """Tests for regression_value() function"""

    def test_ols_regression_basic(self, sample_comparables, subject_property):
        """OLS regression should provide value estimate"""
        from score_to_price import regression_value

        subject_score = 3.50
        result = regression_value(subject_score, sample_comparables, subject_property['building_sf'], method='ols')

        assert result['indicated_value_psf'] is not None
        assert result['r_squared'] > 0.5  # Should fit well with monotonic data
        assert result['method_used'] == 'ols'

    def test_ols_negative_slope(self, sample_comparables, subject_property):
        """OLS should show negative slope (higher score = lower price)"""
        from score_to_price import regression_value

        result = regression_value(3.50, sample_comparables, subject_property['building_sf'], method='ols')

        assert result['beta'] < 0  # Negative slope expected

    def test_monotone_regression(self, sample_comparables, subject_property):
        """Monotonic regression should enforce monotonicity"""
        from score_to_price import regression_value

        subject_score = 3.50
        result = regression_value(subject_score, sample_comparables, subject_property['building_sf'], method='monotone')

        assert result['indicated_value_psf'] is not None
        assert result['method_used'] == 'monotone'

    def test_theil_sen_regression(self, sample_comparables, subject_property):
        """Theil-Sen should be robust to outliers"""
        from score_to_price import regression_value

        # Add an outlier
        comps_with_outlier = sample_comparables.copy()
        comps_with_outlier.append({
            'id': 'OUTLIER', 'score': 3.00, 'price_psf': 150.00,  # Way above normal
            'price_total': 7500000, 'building_sf': 50000
        })

        result = regression_value(3.50, comps_with_outlier, subject_property['building_sf'], method='theil_sen')

        # Theil-Sen should be less affected by outlier
        assert result['method_used'] == 'theil_sen'
        assert result['indicated_value_psf'] is not None

    def test_confidence_interval(self, sample_comparables, subject_property):
        """Should calculate 95% confidence interval"""
        from score_to_price import regression_value

        result = regression_value(3.50, sample_comparables, subject_property['building_sf'], method='ols')

        assert 'confidence_interval_95' in result
        low, high = result['confidence_interval_95']
        assert low < result['indicated_value_psf'] < high

    def test_std_error_calculated(self, sample_comparables, subject_property):
        """Should calculate standard error of estimate"""
        from score_to_price import regression_value

        result = regression_value(3.50, sample_comparables, subject_property['building_sf'], method='ols')

        assert 'std_error' in result
        assert result['std_error'] >= 0

    def test_residuals_returned(self, sample_comparables, subject_property):
        """Should return residuals for each comparable"""
        from score_to_price import regression_value

        result = regression_value(3.50, sample_comparables, subject_property['building_sf'], method='ols')

        assert 'residuals' in result
        assert len(result['residuals']) == len(sample_comparables)


# =============================================================================
# LEAVE-ONE-OUT TESTS
# =============================================================================

class TestLeaveOneOut:
    """Tests for leave-one-out cross-validation"""

    def test_loo_r_squared(self, sample_comparables, subject_property):
        """LOO R² should be calculated"""
        from score_to_price import regression_value

        result = regression_value(3.50, sample_comparables, subject_property['building_sf'], method='ols')

        assert 'loo_r_squared' in result
        # LOO R² is typically lower than regular R²
        assert result['loo_r_squared'] <= result['r_squared'] + 0.1

    def test_loo_value_range(self, sample_comparables, subject_property):
        """LOO should provide subject value range across iterations"""
        from score_to_price import regression_value

        result = regression_value(3.50, sample_comparables, subject_property['building_sf'], method='ols')

        assert 'loo_value_range_psf' in result
        low, high = result['loo_value_range_psf']
        # Value should be within LOO range
        assert low <= result['indicated_value_psf'] <= high or abs(result['indicated_value_psf'] - (low + high) / 2) < 10


# =============================================================================
# RECONCILIATION TESTS
# =============================================================================

class TestReconcileMethods:
    """Tests for reconcile_methods() function"""

    def test_reconcile_returns_weighted_average(self, sample_comparables, subject_property):
        """Reconciliation should return weighted average of methods"""
        from score_to_price import interpolate_value, regression_value, reconcile_methods

        subject_score = 3.50
        building_sf = subject_property['building_sf']

        interp = interpolate_value(subject_score, sample_comparables, building_sf)
        regress = regression_value(subject_score, sample_comparables, building_sf, method='ols')
        result = reconcile_methods(interp, regress, building_sf)

        assert result['indicated_value_psf'] is not None
        assert result['indicated_value_total'] is not None

        # Reconciled value should be between the two methods
        values = [interp['indicated_value_psf'], regress['indicated_value_psf']]
        assert min(values) - 5 <= result['indicated_value_psf'] <= max(values) + 5

    def test_reconcile_includes_weights(self, sample_comparables, subject_property):
        """Reconciliation should report method weights"""
        from score_to_price import interpolate_value, regression_value, reconcile_methods

        subject_score = 3.50
        building_sf = subject_property['building_sf']

        interp = interpolate_value(subject_score, sample_comparables, building_sf)
        regress = regression_value(subject_score, sample_comparables, building_sf, method='ols')
        result = reconcile_methods(interp, regress, building_sf)

        assert 'method_weights' in result
        assert 'interpolation' in result['method_weights']
        assert 'regression' in result['method_weights']
        # Weights should sum to 1.0
        assert sum(result['method_weights'].values()) == pytest.approx(1.0, rel=0.01)

    def test_reconcile_includes_rationale(self, sample_comparables, subject_property):
        """Reconciliation should include rationale for weighting"""
        from score_to_price import interpolate_value, regression_value, reconcile_methods

        subject_score = 3.50
        building_sf = subject_property['building_sf']

        interp = interpolate_value(subject_score, sample_comparables, building_sf)
        regress = regression_value(subject_score, sample_comparables, building_sf, method='ols')
        result = reconcile_methods(interp, regress, building_sf)

        assert 'reconciliation_rationale' in result
        assert len(result['reconciliation_rationale']) > 0

    def test_reconcile_favors_interpolation_for_small_n(self, subject_property):
        """With small sample, interpolation should be weighted higher"""
        from score_to_price import interpolate_value, regression_value, reconcile_methods

        # Only 3 comparables
        small_sample = [
            {'id': 'C1', 'score': 2.5, 'price_psf': 100, 'price_total': 5000000, 'building_sf': 50000},
            {'id': 'C2', 'score': 3.5, 'price_psf': 90, 'price_total': 4500000, 'building_sf': 50000},
            {'id': 'C3', 'score': 4.5, 'price_psf': 80, 'price_total': 4000000, 'building_sf': 50000},
        ]

        subject_score = 3.0
        building_sf = subject_property['building_sf']

        interp = interpolate_value(subject_score, small_sample, building_sf)
        regress = regression_value(subject_score, small_sample, building_sf, method='ols')
        result = reconcile_methods(interp, regress, building_sf)

        # For small samples, interpolation should have higher weight
        assert result['method_weights']['interpolation'] >= result['method_weights']['regression']


# =============================================================================
# OUTLIER DETECTION TESTS
# =============================================================================

class TestOutlierDetection:
    """Tests for outlier detection in regression"""

    def test_outliers_identified(self, subject_property):
        """Outliers (>2 std dev) should be identified"""
        from score_to_price import regression_value

        # Create tight linear comparables with one extreme outlier
        comps_with_outlier = [
            {'id': 'C1', 'score': 2.0, 'price_psf': 100.0, 'price_total': 5000000, 'building_sf': 50000},
            {'id': 'C2', 'score': 3.0, 'price_psf': 90.0, 'price_total': 4500000, 'building_sf': 50000},
            {'id': 'C3', 'score': 4.0, 'price_psf': 80.0, 'price_total': 4000000, 'building_sf': 50000},
            {'id': 'C4', 'score': 5.0, 'price_psf': 70.0, 'price_total': 3500000, 'building_sf': 50000},
            # Extreme outlier - $200/SF when expected would be ~$85
            {'id': 'OUTLIER', 'score': 3.5, 'price_psf': 200.0, 'price_total': 10000000, 'building_sf': 50000}
        ]

        result = regression_value(3.50, comps_with_outlier, subject_property['building_sf'], method='ols')

        assert 'outliers' in result
        # The extreme outlier should be detected
        outlier_ids = [o['id'] for o in result['outliers']]
        assert 'OUTLIER' in outlier_ids


# =============================================================================
# EDGE CASES
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling"""

    def test_minimum_comparables(self, subject_property):
        """Should handle minimum (3) comparables"""
        from score_to_price import interpolate_value, regression_value

        min_sample = [
            {'id': 'C1', 'score': 2.0, 'price_psf': 100, 'price_total': 5000000, 'building_sf': 50000},
            {'id': 'C2', 'score': 3.0, 'price_psf': 90, 'price_total': 4500000, 'building_sf': 50000},
            {'id': 'C3', 'score': 4.0, 'price_psf': 80, 'price_total': 4000000, 'building_sf': 50000},
        ]

        subject_score = 2.5
        building_sf = subject_property['building_sf']

        interp = interpolate_value(subject_score, min_sample, building_sf)
        regress = regression_value(subject_score, min_sample, building_sf, method='ols')

        assert interp['indicated_value_psf'] is not None
        assert regress['indicated_value_psf'] is not None

    def test_all_same_score(self, subject_property):
        """Should handle all comparables with same score"""
        from score_to_price import interpolate_value

        same_score = [
            {'id': 'C1', 'score': 3.0, 'price_psf': 95, 'price_total': 4750000, 'building_sf': 50000},
            {'id': 'C2', 'score': 3.0, 'price_psf': 90, 'price_total': 4500000, 'building_sf': 50000},
            {'id': 'C3', 'score': 3.0, 'price_psf': 85, 'price_total': 4250000, 'building_sf': 50000},
        ]

        subject_score = 3.0
        result = interpolate_value(subject_score, same_score, subject_property['building_sf'])

        # Should return average of prices
        assert result['indicated_value_psf'] == pytest.approx(90.0, rel=0.05)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
