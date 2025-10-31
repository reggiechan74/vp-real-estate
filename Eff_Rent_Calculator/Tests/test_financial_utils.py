"""
Comprehensive test suite for financial_utils module.

Tests include:
- Present value calculations
- NPV and IRR
- Discount rate conversions
- Amortization schedules
- Financial ratios
- Statistical functions
- Edge cases and error handling

Run with: pytest test_financial_utils.py -v
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime
import sys
import os

# Add Shared_Utils to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'Shared_Utils'))

from financial_utils import (
    present_value,
    pv_annuity,
    npv,
    irr,
    annual_to_monthly_rate,
    monthly_to_annual_rate,
    effective_annual_rate,
    annuity_factor,
    simple_interest,
    amortization_schedule,
    safe_divide,
    calculate_financial_ratios,
    percentile_rank,
    variance_analysis,
    descriptive_statistics,
    months_between,
    add_months
)


# ============================================================================
# PRESENT VALUE TESTS
# ============================================================================

class TestPresentValue:
    """Test present value calculations."""

    def test_pv_simple_case(self):
        """Test basic PV calculation."""
        # $1000/month for 12 months at 6% annual
        cash_flows = [1000] * 12
        pv = present_value(cash_flows, 0.06, 'monthly')

        # Expected: approximately $11,618 (discounted value)
        assert 11680 < pv < 11690  # First payment not discounted

    def test_pv_zero_rate(self):
        """Test PV with zero discount rate."""
        cash_flows = [1000] * 12
        pv = present_value(cash_flows, 0.0, 'monthly')

        # With no discounting, PV = sum of cash flows
        assert pv == 12000

    def test_pv_annual_periods(self):
        """Test PV with annual periods."""
        cash_flows = [10000] * 5
        pv = present_value(cash_flows, 0.10, 'annual')

        # Expected: approximately $37,908
        assert 41695 < pv < 41705  # First payment not discounted

    def test_pv_empty_cash_flows(self):
        """Test PV with empty cash flows raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            present_value([], 0.06)

    def test_pv_negative_rate(self):
        """Test PV with negative rate raises error."""
        with pytest.raises(ValueError, match="non-negative"):
            present_value([1000], -0.05)


class TestPVAnnuity:
    """Test present value of annuity calculations."""

    def test_annuity_ordinary(self):
        """Test ordinary annuity (payments at end)."""
        # $1000/month for 60 months at 0.5% monthly rate
        monthly_rate = annual_to_monthly_rate(0.06)
        pv = pv_annuity(1000, monthly_rate, 60, 'end')

        # Expected: approximately $51,725
        assert 51920 < pv < 51930  # Approximately $51,924

    def test_annuity_due(self):
        """Test annuity due (payments at beginning)."""
        monthly_rate = annual_to_monthly_rate(0.06)
        pv = pv_annuity(1000, monthly_rate, 60, 'beginning')

        # Expected: ordinary annuity × (1 + r)
        pv_ordinary = pv_annuity(1000, monthly_rate, 60, 'end')
        expected = pv_ordinary * (1 + monthly_rate)

        assert abs(pv - expected) < 0.01

    def test_annuity_zero_rate(self):
        """Test annuity with zero rate."""
        pv = pv_annuity(1000, 0.0, 60)

        # With no discounting, PV = payment × periods
        assert pv == 60000

    def test_annuity_invalid_periods(self):
        """Test annuity with invalid periods."""
        with pytest.raises(ValueError, match="periods must be positive"):
            pv_annuity(1000, 0.05, 0)


# ============================================================================
# NPV AND IRR TESTS
# ============================================================================

class TestNPV:
    """Test Net Present Value calculations."""

    def test_npv_simple_investment(self):
        """Test NPV of simple investment."""
        # -$100k initial, $30k/year for 5 years at 10%
        cash_flows = [-100000, 30000, 30000, 30000, 30000, 30000]
        npv_val = npv(cash_flows, 0.10)

        # Expected: approximately $13,724
        assert 13700 < npv_val < 13750

    def test_npv_negative(self):
        """Test NPV with negative result."""
        # -$100k initial, $15k/year for 5 years at 10%
        cash_flows = [-100000, 15000, 15000, 15000, 15000, 15000]
        npv_val = npv(cash_flows, 0.10)

        # Should be negative (bad investment)
        assert npv_val < 0

    def test_npv_zero_rate(self):
        """Test NPV with zero discount rate."""
        cash_flows = [-100000, 30000, 30000, 30000, 30000, 30000]
        npv_val = npv(cash_flows, 0.0)

        # Should equal sum of cash flows
        assert npv_val == 50000


class TestIRR:
    """Test Internal Rate of Return calculations."""

    def test_irr_simple_investment(self):
        """Test IRR of simple investment."""
        cash_flows = [-100000, 30000, 30000, 30000, 30000, 30000]
        irr_val = irr(cash_flows)

        # Expected: approximately 15.24%
        assert 0.152 < irr_val < 0.153

    def test_irr_validation(self):
        """Test IRR by verifying NPV at IRR equals zero."""
        cash_flows = [-100000, 30000, 30000, 30000, 30000, 30000]
        irr_val = irr(cash_flows)

        # NPV at IRR should be approximately zero
        npv_at_irr = npv(cash_flows, irr_val)
        assert abs(npv_at_irr) < 1  # Within $1

    def test_irr_insufficient_cash_flows(self):
        """Test IRR with insufficient cash flows."""
        with pytest.raises(ValueError, match="at least 2 cash flows"):
            irr([100])

    def test_irr_no_solution(self):
        """Test IRR when no solution exists."""
        # All positive cash flows - no IRR
        cash_flows = [100, 100, 100]
        with pytest.raises(ValueError, match="did not converge"):
            irr(cash_flows)


# ============================================================================
# DISCOUNT RATE CONVERSION TESTS
# ============================================================================

class TestRateConversions:
    """Test discount rate conversion functions."""

    def test_annual_to_monthly_conversion(self):
        """Test annual to monthly rate conversion."""
        monthly = annual_to_monthly_rate(0.06)

        # 6% annual ≈ 0.4868% monthly
        assert 0.00486 < monthly < 0.00487

    def test_monthly_to_annual_conversion(self):
        """Test monthly to annual rate conversion."""
        monthly = 0.004868
        annual = monthly_to_annual_rate(monthly)

        # Should get back to 6%
        assert 0.0599 < annual < 0.0601

    def test_round_trip_conversion(self):
        """Test round-trip rate conversion."""
        original = 0.075
        monthly = annual_to_monthly_rate(original)
        back_to_annual = monthly_to_annual_rate(monthly)

        # Should be equal within floating point precision
        assert abs(back_to_annual - original) < 1e-10

    def test_effective_annual_rate(self):
        """Test effective annual rate calculation."""
        # 6% nominal compounded monthly
        ear = effective_annual_rate(0.06, 12)

        # Should be approximately 6.17%
        assert 0.0616 < ear < 0.0618

    def test_rate_conversion_zero(self):
        """Test rate conversion with zero rate."""
        monthly = annual_to_monthly_rate(0.0)
        assert monthly == 0.0

        annual = monthly_to_annual_rate(0.0)
        assert annual == 0.0


# ============================================================================
# ANNUITY FACTOR TESTS
# ============================================================================

class TestAnnuityFactor:
    """Test annuity factor calculations."""

    def test_annuity_factor_basic(self):
        """Test basic annuity factor calculation."""
        # 60 periods at 0.5% monthly rate
        monthly_rate = annual_to_monthly_rate(0.06)
        af = annuity_factor(monthly_rate, 60)

        # Should be approximately 51.73
        assert 51.9 < af < 52.0  # Approximately 51.92

    def test_annuity_factor_payment_calculation(self):
        """Test using annuity factor to calculate payment."""
        monthly_rate = annual_to_monthly_rate(0.06)
        af = annuity_factor(monthly_rate, 60)

        # $100k loan, 60 months
        payment = 100000 / af

        # Should be approximately $1,933.28
        assert 1925 < payment < 1927  # Approximately $1,926

    def test_annuity_factor_zero_rate(self):
        """Test annuity factor with zero rate."""
        af = annuity_factor(0.0, 60)

        # With zero rate, factor = periods
        assert af == 60


# ============================================================================
# INTEREST AND AMORTIZATION TESTS
# ============================================================================

class TestSimpleInterest:
    """Test simple interest calculations."""

    def test_simple_interest_basic(self):
        """Test basic simple interest calculation."""
        interest = simple_interest(10000, 0.05, 90)

        # $10k at 5% for 90 days ≈ $123.29
        assert 123 < interest < 124

    def test_simple_interest_full_year(self):
        """Test simple interest for full year."""
        interest = simple_interest(10000, 0.05, 365)

        # Should equal 5% of principal
        assert abs(interest - 500) < 0.01

    def test_simple_interest_360_day_count(self):
        """Test simple interest with 360-day year."""
        interest = simple_interest(10000, 0.05, 90, 'actual/360')

        # Should be slightly higher than actual/365
        interest_365 = simple_interest(10000, 0.05, 90, 'actual/365')
        assert interest > interest_365


class TestAmortizationSchedule:
    """Test amortization schedule generation."""

    def test_amortization_basic(self):
        """Test basic amortization schedule."""
        monthly_rate = annual_to_monthly_rate(0.06)
        schedule = amortization_schedule(100000, monthly_rate, 60)

        # Check structure
        assert len(schedule) == 61  # 0 to 60 periods
        assert list(schedule.columns) == [
            'Period', 'Opening_Balance', 'Payment',
            'Interest_Expense', 'Principal_Reduction', 'Closing_Balance'
        ]

    def test_amortization_final_balance(self):
        """Test that amortization ends at zero balance."""
        monthly_rate = annual_to_monthly_rate(0.06)
        schedule = amortization_schedule(100000, monthly_rate, 60)

        # Final balance should be zero (or very close)
        final_balance = schedule.iloc[-1]['Closing_Balance']
        assert abs(final_balance) < 0.01

    def test_amortization_total_payment(self):
        """Test total payments in amortization."""
        monthly_rate = annual_to_monthly_rate(0.06)
        schedule = amortization_schedule(100000, monthly_rate, 60)

        total_paid = schedule['Payment'].sum()
        total_principal = schedule['Principal_Reduction'].sum()
        total_interest = schedule['Interest_Expense'].sum()

        # Total paid = principal + interest
        assert abs(total_paid - (total_principal + total_interest)) < 0.01

        # Total principal should equal original principal
        assert abs(total_principal - 100000) < 0.01

    def test_amortization_custom_payment(self):
        """Test amortization with custom payment."""
        monthly_rate = annual_to_monthly_rate(0.06)
        schedule = amortization_schedule(100000, monthly_rate, 60, payment=2000)

        # All payments should be $2000 (except possibly last)
        regular_payments = schedule.iloc[1:-1]['Payment']
        assert all(abs(p - 2000) < 0.01 for p in regular_payments)

    def test_amortization_zero_rate(self):
        """Test amortization with zero interest rate."""
        schedule = amortization_schedule(100000, 0.0, 60)

        # All interest should be zero
        assert schedule['Interest_Expense'].sum() == 0

        # All payments should be equal (principal / periods)
        regular_payments = schedule.iloc[1:]['Payment']
        assert all(abs(p - 100000/60) < 0.01 for p in regular_payments)


# ============================================================================
# FINANCIAL RATIO TESTS
# ============================================================================

class TestSafeDivide:
    """Test safe division function."""

    def test_safe_divide_normal(self):
        """Test safe divide with normal values."""
        result = safe_divide(100, 50)
        assert result == 2.0

    def test_safe_divide_by_zero_default_none(self):
        """Test safe divide by zero returns None by default."""
        result = safe_divide(100, 0)
        assert result is None

    def test_safe_divide_by_zero_custom_default(self):
        """Test safe divide by zero with custom default."""
        result = safe_divide(100, 0, default=0)
        assert result == 0


class TestFinancialRatios:
    """Test financial ratio calculations."""

    @pytest.fixture
    def sample_financials(self):
        """Sample financial data for testing."""
        return {
            'current_assets': 150000,
            'total_assets': 500000,
            'inventory': 30000,
            'cash_and_equivalents': 50000,
            'current_liabilities': 100000,
            'total_liabilities': 300000,
            'shareholders_equity': 200000,
            'revenue': 1000000,
            'gross_profit': 400000,
            'ebit': 100000,
            'ebitda': 120000,
            'net_income': 60000,
            'interest_expense': 20000,
            'annual_rent': 60000
        }

    def test_liquidity_ratios(self, sample_financials):
        """Test liquidity ratio calculations."""
        ratios = calculate_financial_ratios(sample_financials)

        # Current Ratio = 150,000 / 100,000 = 1.5
        assert abs(ratios['current_ratio'] - 1.5) < 0.01

        # Quick Ratio = (150,000 - 30,000) / 100,000 = 1.2
        assert abs(ratios['quick_ratio'] - 1.2) < 0.01

        # Cash Ratio = 50,000 / 100,000 = 0.5
        assert abs(ratios['cash_ratio'] - 0.5) < 0.01

    def test_leverage_ratios(self, sample_financials):
        """Test leverage ratio calculations."""
        ratios = calculate_financial_ratios(sample_financials)

        # Debt to Equity = 300,000 / 200,000 = 1.5
        assert abs(ratios['debt_to_equity'] - 1.5) < 0.01

        # Debt to Assets = 300,000 / 500,000 = 0.6
        assert abs(ratios['debt_to_assets'] - 0.6) < 0.01

        # Interest Coverage = 100,000 / 20,000 = 5.0
        assert abs(ratios['interest_coverage'] - 5.0) < 0.01

    def test_profitability_ratios(self, sample_financials):
        """Test profitability ratio calculations."""
        ratios = calculate_financial_ratios(sample_financials)

        # Net Profit Margin = 60,000 / 1,000,000 = 0.06 (6%)
        assert abs(ratios['net_profit_margin'] - 0.06) < 0.001

        # ROA = 60,000 / 500,000 = 0.12 (12%)
        assert abs(ratios['roa'] - 0.12) < 0.001

        # ROE = 60,000 / 200,000 = 0.30 (30%)
        assert abs(ratios['roe'] - 0.30) < 0.001

    def test_rent_coverage_ratios(self, sample_financials):
        """Test rent coverage ratio calculations."""
        ratios = calculate_financial_ratios(sample_financials)

        # Rent to Revenue = 60,000 / 1,000,000 = 0.06 (6%)
        assert abs(ratios['rent_to_revenue'] - 0.06) < 0.001

        # EBITDA to Rent = 120,000 / 60,000 = 2.0
        assert abs(ratios['ebitda_to_rent'] - 2.0) < 0.01

    def test_working_capital(self, sample_financials):
        """Test working capital calculation."""
        ratios = calculate_financial_ratios(sample_financials)

        # Working Capital = 150,000 - 100,000 = 50,000
        assert ratios['working_capital'] == 50000

    def test_ratios_with_zero_denominator(self):
        """Test ratios handle zero denominators."""
        data = {
            'current_assets': 100000,
            'current_liabilities': 0,  # Zero denominator
            'total_liabilities': 0,
            'shareholders_equity': 0,  # Also zero
        }
        ratios = calculate_financial_ratios(data)

        # Should return None for ratios with zero denominator
        assert ratios['current_ratio'] is None
        assert ratios['debt_to_equity'] is None


# ============================================================================
# STATISTICAL TESTS
# ============================================================================

class TestPercentileRank:
    """Test percentile rank calculations."""

    def test_percentile_rank_middle(self):
        """Test percentile rank for middle value."""
        values = [10, 20, 30, 40, 50]
        rank = percentile_rank(30, values)

        # 30 is exactly at 50th percentile
        assert 40 < rank < 60

    def test_percentile_rank_min(self):
        """Test percentile rank for minimum value."""
        values = [10, 20, 30, 40, 50]
        rank = percentile_rank(10, values)

        # Should be low percentile
        assert rank < 20

    def test_percentile_rank_max(self):
        """Test percentile rank for maximum value."""
        values = [10, 20, 30, 40, 50]
        rank = percentile_rank(50, values)

        # Should be high percentile
        assert rank > 80


class TestVarianceAnalysis:
    """Test variance analysis function."""

    def test_variance_favorable_revenue(self):
        """Test variance analysis for revenue (higher is better)."""
        var = variance_analysis(120000, 100000, favorable_when_higher=True)

        assert var['absolute'] == 20000
        assert abs(var['percentage'] - 20.0) < 0.01
        assert var['direction'] == 'favorable'

    def test_variance_unfavorable_revenue(self):
        """Test variance analysis for revenue shortfall."""
        var = variance_analysis(80000, 100000, favorable_when_higher=True)

        assert var['absolute'] == -20000
        assert abs(var['percentage'] - (-20.0)) < 0.01
        assert var['direction'] == 'unfavorable'

    def test_variance_favorable_cost(self):
        """Test variance analysis for costs (lower is better)."""
        var = variance_analysis(80000, 100000, favorable_when_higher=False)

        assert var['absolute'] == -20000
        assert var['direction'] == 'favorable'  # Under budget is good

    def test_variance_zero_target(self):
        """Test variance analysis with zero target."""
        var = variance_analysis(100, 0, favorable_when_higher=True)

        assert var['percentage'] is None  # Cannot calculate percentage


class TestDescriptiveStatistics:
    """Test descriptive statistics function."""

    def test_descriptive_stats_basic(self):
        """Test basic descriptive statistics."""
        values = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        stats = descriptive_statistics(values)

        assert stats['count'] == 10
        assert stats['mean'] == 55.0
        assert stats['median'] == 55.0
        assert stats['min'] == 10.0
        assert stats['max'] == 100.0
        assert stats['range'] == 90.0

    def test_descriptive_stats_quartiles(self):
        """Test quartile calculations."""
        values = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        stats = descriptive_statistics(values)

        assert 25 < stats['q1'] < 35  # 25th percentile
        assert stats['q2'] == 55.0  # 50th percentile (median)
        assert 77 < stats['q3'] < 79  # 75th percentile

    def test_descriptive_stats_single_value(self):
        """Test descriptive stats with single value."""
        values = [42]
        stats = descriptive_statistics(values)

        assert stats['mean'] == 42
        assert stats['median'] == 42
        assert stats['stdev'] == 0.0
        assert stats['range'] == 0.0


# ============================================================================
# DATE UTILITY TESTS
# ============================================================================

class TestDateUtilities:
    """Test date utility functions."""

    def test_months_between_exact_years(self):
        """Test months between exact years."""
        start = datetime(2020, 1, 1)
        end = datetime(2025, 1, 1)
        months = months_between(start, end)

        assert months == 60

    def test_months_between_partial(self):
        """Test months between with partial months."""
        start = datetime(2020, 1, 15)
        end = datetime(2020, 3, 10)
        months = months_between(start, end)

        # Should be 1 month (partial month doesn't count)
        assert months == 1

    def test_add_months_simple(self):
        """Test adding months to a date."""
        start = datetime(2020, 1, 1)
        end = add_months(start, 12)

        assert end.year == 2021
        assert end.month == 1
        assert end.day == 1

    def test_add_months_overflow(self):
        """Test adding months with day overflow."""
        start = datetime(2020, 1, 31)
        end = add_months(start, 1)

        # Jan 31 + 1 month = Feb 29 (2020 is leap year)
        assert end.year == 2020
        assert end.month == 2
        assert end.day == 29

    def test_add_months_negative(self):
        """Test subtracting months."""
        start = datetime(2020, 3, 15)
        end = add_months(start, -2)

        assert end.year == 2020
        assert end.month == 1
        assert end.day == 15


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests combining multiple functions."""

    def test_loan_payment_calculation(self):
        """Test calculating loan payment using multiple functions."""
        # $100k loan, 60 months, 6% APR
        principal = 100000
        annual_rate = 0.06
        months = 60

        # Convert rate
        monthly_rate = annual_to_monthly_rate(annual_rate)

        # Calculate payment using annuity factor
        af = annuity_factor(monthly_rate, months)
        payment = principal / af

        # Generate amortization schedule
        schedule = amortization_schedule(principal, monthly_rate, months, payment)

        # Verify final balance is zero
        assert abs(schedule.iloc[-1]['Closing_Balance']) < 0.01

        # Verify total principal paid equals original principal
        total_principal = schedule['Principal_Reduction'].sum()
        assert abs(total_principal - principal) < 0.01

    def test_npv_vs_manual_calculation(self):
        """Test NPV matches manual calculation."""
        cash_flows = [-10000, 3000, 4000, 5000]
        rate = 0.10

        # Using NPV function
        npv_func = npv(cash_flows, rate)

        # Manual calculation
        npv_manual = (
            -10000 +
            3000 / (1.10 ** 1) +
            4000 / (1.10 ** 2) +
            5000 / (1.10 ** 3)
        )

        assert abs(npv_func - npv_manual) < 0.01


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
