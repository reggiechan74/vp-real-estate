"""
Test Suite for Real Options Valuation Calculator

Validates Black-Scholes implementation against known results from:
- Published Black-Scholes calculators
- Academic examples
- Manual calculations

Author: Claude Code
Date: 2025-11-06
"""

import pytest
import math
from scipy.stats import norm
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from option_valuation import (
    cumulative_normal_distribution,
    black_scholes_d1_d2,
    black_scholes_call,
    black_scholes_put,
    calculate_option_greeks,
    OptionParameters,
    value_option,
    sensitivity_analysis_volatility,
    sensitivity_analysis_market_rent,
    sensitivity_analysis_time_decay
)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def approx_equal(a: float, b: float, tolerance: float = 0.01) -> bool:
    """Check if two values are approximately equal within tolerance"""
    return abs(a - b) < tolerance


# =============================================================================
# TEST CUMULATIVE NORMAL DISTRIBUTION
# =============================================================================

class TestCumulativeNormalDistribution:
    """Test cumulative normal distribution accuracy"""

    def test_cdf_standard_values(self):
        """Test N(x) for standard values"""
        # N(0) should be 0.5
        assert approx_equal(cumulative_normal_distribution(0), 0.5, 0.0001)

        # N(-∞) approaches 0
        assert cumulative_normal_distribution(-10) < 0.0001

        # N(+∞) approaches 1
        assert cumulative_normal_distribution(10) > 0.9999

    def test_cdf_known_values(self):
        """Test against known cumulative normal values"""
        # From standard normal table
        test_cases = [
            (0.0, 0.5000),
            (1.0, 0.8413),
            (1.96, 0.9750),
            (2.0, 0.9772),
            (-1.0, 0.1587),
            (-1.96, 0.0250),
        ]

        for x, expected in test_cases:
            result = cumulative_normal_distribution(x)
            assert approx_equal(result, expected, 0.0001), \
                f"N({x}) = {result}, expected {expected}"

    def test_cdf_symmetry(self):
        """Test N(-x) = 1 - N(x)"""
        test_values = [0.5, 1.0, 1.5, 2.0, 2.5]

        for x in test_values:
            n_pos = cumulative_normal_distribution(x)
            n_neg = cumulative_normal_distribution(-x)
            assert approx_equal(n_pos + n_neg, 1.0, 0.0001), \
                f"N({x}) + N({-x}) should equal 1.0"


# =============================================================================
# TEST d1 AND d2 CALCULATIONS
# =============================================================================

class TestD1D2Calculations:
    """Test Black-Scholes d1 and d2 calculations"""

    def test_d1_d2_basic(self):
        """Test d1 and d2 calculation with known values"""
        # Example: S=100, K=100, T=1, r=0.05, σ=0.20
        # Expected from published calculators:
        # d1 ≈ 0.35, d2 ≈ 0.15

        S, K, T, r, sigma = 100, 100, 1.0, 0.05, 0.20
        d1, d2 = black_scholes_d1_d2(S, K, T, r, sigma)

        assert approx_equal(d1, 0.35, 0.01)
        assert approx_equal(d2, 0.15, 0.01)

    def test_d1_d2_relationship(self):
        """Test d2 = d1 - σ√T"""
        S, K, T, r, sigma = 100, 95, 0.5, 0.05, 0.25

        d1, d2 = black_scholes_d1_d2(S, K, T, r, sigma)

        expected_d2 = d1 - sigma * math.sqrt(T)
        assert approx_equal(d2, expected_d2, 0.0001)

    def test_d1_d2_at_the_money(self):
        """Test when S = K (at-the-money)"""
        S, K, T, r, sigma = 100, 100, 1.0, 0.05, 0.20

        d1, d2 = black_scholes_d1_d2(S, K, T, r, sigma)

        # At the money, d1 should be approximately (r + σ²/2)T / (σ√T)
        expected_d1 = (r + 0.5 * sigma**2) * T / (sigma * math.sqrt(T))
        assert approx_equal(d1, expected_d1, 0.0001)

    def test_d1_d2_errors(self):
        """Test error handling for invalid inputs"""
        with pytest.raises(ValueError):
            black_scholes_d1_d2(100, 100, 0, 0.05, 0.20)  # T = 0

        with pytest.raises(ValueError):
            black_scholes_d1_d2(100, 100, 1, 0.05, 0)  # σ = 0

        with pytest.raises(ValueError):
            black_scholes_d1_d2(-100, 100, 1, 0.05, 0.20)  # S < 0


# =============================================================================
# TEST BLACK-SCHOLES CALL OPTION
# =============================================================================

class TestBlackScholesCall:
    """Test Black-Scholes call option pricing"""

    def test_call_basic_example(self):
        """Test call with known result from published calculator"""
        # Example from Black-Scholes calculator:
        # S=100, K=100, T=1, r=5%, σ=20%
        # Expected call value ≈ $10.45

        S, K, T, r, sigma = 100, 100, 1.0, 0.05, 0.20
        call_value = black_scholes_call(S, K, T, r, sigma)

        assert approx_equal(call_value, 10.45, 0.10)

    def test_call_in_the_money(self):
        """Test deep in-the-money call"""
        # S=150, K=100, very likely to exercise
        S, K, T, r, sigma = 150, 100, 1.0, 0.05, 0.20
        call_value = black_scholes_call(S, K, T, r, sigma)

        # Should be worth at least intrinsic value S - K*e^(-rT)
        intrinsic_value = S - K * math.exp(-r * T)
        assert call_value >= intrinsic_value

    def test_call_out_of_money(self):
        """Test deep out-of-the-money call"""
        # S=50, K=100, unlikely to exercise
        S, K, T, r, sigma = 50, 100, 1.0, 0.05, 0.20
        call_value = black_scholes_call(S, K, T, r, sigma)

        # Should be small but positive
        assert call_value > 0
        assert call_value < 5  # Should be much less than intrinsic value

    def test_call_zero_volatility(self):
        """Test call approaches intrinsic value as volatility → 0"""
        # With zero volatility, option value = max(S - Ke^(-rT), 0)
        S, K, T, r = 110, 100, 1.0, 0.05

        # Can't actually use σ=0 (raises error), but very small σ
        call_value = black_scholes_call(S, K, T, r, 0.01)
        intrinsic_value = max(S - K * math.exp(-r * T), 0)

        assert approx_equal(call_value, intrinsic_value, 0.50)

    def test_call_time_value(self):
        """Test that longer time increases call value"""
        S, K, r, sigma = 100, 100, 0.05, 0.20

        call_1yr = black_scholes_call(S, K, 1.0, r, sigma)
        call_2yr = black_scholes_call(S, K, 2.0, r, sigma)

        assert call_2yr > call_1yr  # More time = more value

    def test_call_volatility_increases_value(self):
        """Test that higher volatility increases call value"""
        S, K, T, r = 100, 100, 1.0, 0.05

        call_10pct = black_scholes_call(S, K, T, r, 0.10)
        call_30pct = black_scholes_call(S, K, T, r, 0.30)

        assert call_30pct > call_10pct  # More volatility = more value


# =============================================================================
# TEST BLACK-SCHOLES PUT OPTION
# =============================================================================

class TestBlackScholesPut:
    """Test Black-Scholes put option pricing"""

    def test_put_basic_example(self):
        """Test put with known result"""
        # S=100, K=100, T=1, r=5%, σ=20%
        # Expected put value ≈ $5.57 (from put-call parity)

        S, K, T, r, sigma = 100, 100, 1.0, 0.05, 0.20
        put_value = black_scholes_put(S, K, T, r, sigma)

        assert approx_equal(put_value, 5.57, 0.10)

    def test_put_call_parity(self):
        """Test put-call parity: C - P = S - Ke^(-rT)"""
        S, K, T, r, sigma = 100, 95, 1.0, 0.05, 0.25

        call_value = black_scholes_call(S, K, T, r, sigma)
        put_value = black_scholes_put(S, K, T, r, sigma)

        parity_lhs = call_value - put_value
        parity_rhs = S - K * math.exp(-r * T)

        assert approx_equal(parity_lhs, parity_rhs, 0.01)

    def test_put_in_the_money(self):
        """Test deep in-the-money put"""
        # S=50, K=100, very likely to exercise
        S, K, T, r, sigma = 50, 100, 1.0, 0.05, 0.20
        put_value = black_scholes_put(S, K, T, r, sigma)

        # Should be worth at least intrinsic value Ke^(-rT) - S
        intrinsic_value = K * math.exp(-r * T) - S
        assert put_value >= intrinsic_value

    def test_put_out_of_money(self):
        """Test deep out-of-the-money put"""
        # S=150, K=100, unlikely to exercise
        S, K, T, r, sigma = 150, 100, 1.0, 0.05, 0.20
        put_value = black_scholes_put(S, K, T, r, sigma)

        # Should be small but positive
        assert put_value > 0
        assert put_value < 5


# =============================================================================
# TEST OPTION GREEKS
# =============================================================================

class TestOptionGreeks:
    """Test option Greeks calculations"""

    def test_call_delta_range(self):
        """Test call delta is between 0 and 1"""
        S, K, T, r, sigma = 100, 100, 1.0, 0.05, 0.20
        d1, d2 = black_scholes_d1_d2(S, K, T, r, sigma)
        greeks = calculate_option_greeks('call', S, K, T, r, sigma, d1, d2)

        assert 0 <= greeks.delta <= 1

    def test_put_delta_range(self):
        """Test put delta is between -1 and 0"""
        S, K, T, r, sigma = 100, 100, 1.0, 0.05, 0.20
        d1, d2 = black_scholes_d1_d2(S, K, T, r, sigma)
        greeks = calculate_option_greeks('put', S, K, T, r, sigma, d1, d2)

        assert -1 <= greeks.delta <= 0

    def test_gamma_positive(self):
        """Test gamma is always positive"""
        test_cases = [
            (80, 100),   # Out of money
            (100, 100),  # At the money
            (120, 100),  # In the money
        ]

        T, r, sigma = 1.0, 0.05, 0.20

        for S, K in test_cases:
            d1, d2 = black_scholes_d1_d2(S, K, T, r, sigma)
            greeks = calculate_option_greeks('call', S, K, T, r, sigma, d1, d2)
            assert greeks.gamma > 0

    def test_vega_positive(self):
        """Test vega is always positive (both call and put)"""
        S, K, T, r, sigma = 100, 100, 1.0, 0.05, 0.20
        d1, d2 = black_scholes_d1_d2(S, K, T, r, sigma)

        call_greeks = calculate_option_greeks('call', S, K, T, r, sigma, d1, d2)
        put_greeks = calculate_option_greeks('put', S, K, T, r, sigma, d1, d2)

        assert call_greeks.vega > 0
        assert put_greeks.vega > 0

    def test_theta_negative_for_call(self):
        """Test theta is negative for long call (time decay)"""
        S, K, T, r, sigma = 100, 100, 1.0, 0.05, 0.20
        d1, d2 = black_scholes_d1_d2(S, K, T, r, sigma)
        greeks = calculate_option_greeks('call', S, K, T, r, sigma, d1, d2)

        # Time decay should be negative (option loses value as time passes)
        assert greeks.theta < 0

    def test_rho_positive_for_call(self):
        """Test rho is positive for call (benefits from higher rates)"""
        S, K, T, r, sigma = 100, 100, 1.0, 0.05, 0.20
        d1, d2 = black_scholes_d1_d2(S, K, T, r, sigma)
        greeks = calculate_option_greeks('call', S, K, T, r, sigma, d1, d2)

        # Call value increases with interest rates
        assert greeks.rho > 0

    def test_rho_negative_for_put(self):
        """Test rho is negative for put (hurt by higher rates)"""
        S, K, T, r, sigma = 100, 100, 1.0, 0.05, 0.20
        d1, d2 = black_scholes_d1_d2(S, K, T, r, sigma)
        greeks = calculate_option_greeks('put', S, K, T, r, sigma, d1, d2)

        # Put value decreases with interest rates
        assert greeks.rho < 0


# =============================================================================
# TEST OPTION VALUATION INTEGRATION
# =============================================================================

class TestOptionValuation:
    """Test complete option valuation workflow"""

    def test_renewal_option_valuation(self):
        """Test valuation of a renewal option (call)"""
        # Renewal option: Right to renew 50K SF for 5 years at $15/sf
        # Market rent: $16/sf
        # Time to exercise: 5 years
        # Volatility: 12%
        # Risk-free rate: 5%

        params = OptionParameters(
            option_type='call',
            option_name='Renewal Option - 5 Years',
            underlying_value=50000 * 16 * 5,  # Market rent × Area × Term
            strike_price=50000 * 15 * 5,     # Renewal rent × Area × Term
            time_to_expiration=5.0,
            volatility=0.12,
            risk_free_rate=0.05,
            rentable_area_sf=50000,
            option_term_years=5.0
        )

        result = value_option(params)

        # Assertions
        assert result.option_value > 0
        assert result.option_value_per_sf is not None
        assert result.option_value_per_sf > 0
        assert 0 <= result.probability_itm <= 100
        assert result.option_type == 'call'
        assert result.option_name == params.option_name

        # Greeks should be populated
        assert result.greeks.delta > 0
        assert result.greeks.gamma > 0
        assert result.greeks.vega > 0
        assert result.greeks.theta < 0  # Time decay

    def test_expansion_option_with_utilization(self):
        """Test expansion option with utilization adjustment"""
        # Expansion option: Right to add 10K SF at $14/sf
        # Market rent: $16/sf
        # Utilization probability: 60%

        params = OptionParameters(
            option_type='call',
            option_name='Expansion Option - 10K SF',
            underlying_value=10000 * 16 * 5,
            strike_price=10000 * 14 * 5,
            time_to_expiration=3.0,
            volatility=0.12,
            risk_free_rate=0.05,
            utilization_probability=0.60,
            rentable_area_sf=50000  # Base space
        )

        result = value_option(params)

        # Value should be adjusted by utilization
        assert result.option_value > 0

        # Compare to 100% utilization
        params_full = OptionParameters(
            option_type='call',
            option_name='Expansion (100% utilization)',
            underlying_value=10000 * 16 * 5,
            strike_price=10000 * 14 * 5,
            time_to_expiration=3.0,
            volatility=0.12,
            risk_free_rate=0.05,
            utilization_probability=1.0,
            rentable_area_sf=50000
        )

        result_full = value_option(params_full)

        # 60% utilization should be 60% of full value
        assert approx_equal(result.option_value, result_full.option_value * 0.60, 0.01)

    def test_termination_option_valuation(self):
        """Test termination option (put)"""
        # Termination option: Right to exit in year 3
        # Remaining term: 7 years
        # Current rent: $17/sf (above market)
        # Market rent: $15/sf
        # Termination fee: $50,000

        params = OptionParameters(
            option_type='put',
            option_name='Early Termination Option',
            underlying_value=50000 * 15 * 7,  # Market rent for remaining term
            strike_price=50000 * 17 * 7,      # Contract rent for remaining term
            time_to_expiration=3.0,
            volatility=0.12,
            risk_free_rate=0.05,
            termination_fee=50000,
            rentable_area_sf=50000
        )

        result = value_option(params)

        # Put option should have positive value
        assert result.option_value > 0
        assert result.option_type == 'put'

        # Put delta should be negative
        assert result.greeks.delta < 0


# =============================================================================
# TEST SENSITIVITY ANALYSIS
# =============================================================================

class TestSensitivityAnalysis:
    """Test sensitivity analysis functions"""

    def test_volatility_sensitivity(self):
        """Test that higher volatility increases option value"""
        params = OptionParameters(
            option_type='call',
            option_name='Test Option',
            underlying_value=100,
            strike_price=100,
            time_to_expiration=1.0,
            volatility=0.20,
            risk_free_rate=0.05
        )

        vol_scenarios = [0.10, 0.20, 0.30]
        results = sensitivity_analysis_volatility(params, vol_scenarios)

        # Values should increase with volatility
        assert len(results) == 3
        assert results[0]['option_value'] < results[1]['option_value']
        assert results[1]['option_value'] < results[2]['option_value']

    def test_market_rent_sensitivity_call(self):
        """Test call value increases with higher market rent"""
        params = OptionParameters(
            option_type='call',
            option_name='Test Call',
            underlying_value=100,
            strike_price=100,
            time_to_expiration=1.0,
            volatility=0.20,
            risk_free_rate=0.05
        )

        market_changes = [-0.20, 0.0, 0.20]
        results = sensitivity_analysis_market_rent(params, market_changes)

        # Call value should increase with market rent
        assert len(results) == 3
        assert results[0]['option_value'] < results[1]['option_value']
        assert results[1]['option_value'] < results[2]['option_value']

    def test_time_decay(self):
        """Test option value decays as time passes"""
        params = OptionParameters(
            option_type='call',
            option_name='Test Option',
            underlying_value=100,
            strike_price=100,
            time_to_expiration=5.0,
            volatility=0.20,
            risk_free_rate=0.05
        )

        time_points = [5.0, 4.0, 3.0, 2.0, 1.0]
        results = sensitivity_analysis_time_decay(params, time_points)

        # Value should decrease as expiration approaches
        assert len(results) == 5
        values = [r['option_value'] for r in results]

        # Each successive value should be lower
        for i in range(len(values) - 1):
            assert values[i] > values[i + 1], \
                f"Time decay failed: value at T={time_points[i]} should be > T={time_points[i+1]}"


# =============================================================================
# TEST REAL ESTATE EXAMPLES
# =============================================================================

class TestRealEstateExamples:
    """Test real-world commercial real estate scenarios"""

    def test_industrial_renewal_option(self):
        """Test typical industrial renewal option"""
        # Property: 100,000 SF warehouse
        # Market rent: $8.50/sf
        # Renewal rent: $8.00/sf (below market)
        # Renewal term: 5 years
        # Time to renewal: 10 years
        # Volatility: 10% (industrial typically lower)

        params = OptionParameters(
            option_type='call',
            option_name='Industrial Renewal - 100K SF',
            underlying_value=100000 * 8.50 * 5,  # $4.25M
            strike_price=100000 * 8.00 * 5,      # $4.0M
            time_to_expiration=10.0,
            volatility=0.10,
            risk_free_rate=0.04,
            rentable_area_sf=100000,
            option_term_years=5.0
        )

        result = value_option(params)

        # Should have significant value due to below-market renewal rent
        assert result.option_value > 0
        assert result.probability_itm > 50  # Likely to be exercised

    def test_office_expansion_option(self):
        """Test typical office expansion option"""
        # Base space: 20,000 SF office
        # Expansion: Additional 5,000 SF
        # Market rent: $35/sf
        # Expansion rent: $32/sf (discount)
        # Exercise window: 2 years
        # Utilization: 40% (expansion uncertain)
        # Volatility: 15% (office more volatile)

        params = OptionParameters(
            option_type='call',
            option_name='Office Expansion - 5K SF',
            underlying_value=5000 * 35 * 5,  # $875K
            strike_price=5000 * 32 * 5,      # $800K
            time_to_expiration=2.0,
            volatility=0.15,
            risk_free_rate=0.05,
            utilization_probability=0.40,
            rentable_area_sf=20000  # Base space
        )

        result = value_option(params)

        # Value should be adjusted for low utilization
        assert result.option_value > 0
        assert result.option_value_per_sf is not None

        # Even with 40% utilization, should have meaningful value
        assert result.option_value > 10000  # At least $10K value


# =============================================================================
# TEST EDGE CASES
# =============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_deep_in_the_money_call(self):
        """Test deep ITM call (S >> K)"""
        # S = $200, K = $100, essentially guaranteed to exercise
        params = OptionParameters(
            option_type='call',
            option_name='Deep ITM Call',
            underlying_value=200,
            strike_price=100,
            time_to_expiration=1.0,
            volatility=0.20,
            risk_free_rate=0.05
        )

        result = value_option(params)

        # Delta should be close to 1
        assert result.greeks.delta > 0.95

        # Probability ITM should be very high
        assert result.probability_itm > 95

    def test_deep_out_of_money_put(self):
        """Test deep OTM put (S >> K)"""
        # S = $200, K = $100, very unlikely to exercise
        params = OptionParameters(
            option_type='put',
            option_name='Deep OTM Put',
            underlying_value=200,
            strike_price=100,
            time_to_expiration=1.0,
            volatility=0.20,
            risk_free_rate=0.05
        )

        result = value_option(params)

        # Delta should be close to 0
        assert abs(result.greeks.delta) < 0.05

        # Probability ITM should be very low
        assert result.probability_itm < 5

    def test_very_short_term(self):
        """Test option with very short time to expiration"""
        params = OptionParameters(
            option_type='call',
            option_name='Short Term Option',
            underlying_value=100,
            strike_price=100,
            time_to_expiration=0.1,  # 1.2 months
            volatility=0.20,
            risk_free_rate=0.05
        )

        result = value_option(params)

        # Should still compute correctly
        assert result.option_value > 0

        # Theta should be very negative (rapid decay)
        assert result.greeks.theta < -10

    def test_very_long_term(self):
        """Test option with very long time to expiration"""
        params = OptionParameters(
            option_type='call',
            option_name='Long Term Option',
            underlying_value=100,
            strike_price=100,
            time_to_expiration=20.0,  # 20 years
            volatility=0.20,
            risk_free_rate=0.05
        )

        result = value_option(params)

        # Long-term option should have high value
        assert result.option_value > 30

        # For very long-term ATM options with positive rates,
        # K×e^(-rT) becomes very small, so delta approaches 1
        assert result.greeks.delta > 0.8


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
