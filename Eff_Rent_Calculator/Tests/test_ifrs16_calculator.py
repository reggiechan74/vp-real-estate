"""
Comprehensive test suite for IFRS 16 / ASC 842 Lease Accounting Calculator.

Tests include:
- Lease liability calculations
- ROU asset calculations
- Amortization schedules
- Depreciation schedules
- Annual summaries
- Sensitivity analysis
- CSV export
- Edge cases

Run with: pytest test_ifrs16_calculator.py -v
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime
import os

from IFRS16_Calculator.ifrs16_calculator import (
    LeaseInputs,
    calculate_lease_liability,
    calculate_rou_asset,
    calculate_ifrs16,
    generate_liability_amortization,
    generate_rou_depreciation,
    create_annual_summary,
    sensitivity_analysis,
    export_to_csv
)
from Shared_Utils.financial_utils import annual_to_monthly_rate


# ============================================================================
# LEASE LIABILITY TESTS
# ============================================================================

class TestLeaseLiability:
    """Test lease liability calculations."""

    def test_constant_payments_beginning(self):
        """Test liability with constant payments at beginning of period."""
        payments = [1000] * 60
        liability, monthly_rate = calculate_lease_liability(
            payments=payments,
            annual_rate=0.06,
            payment_timing='beginning'
        )

        # With annuity due (beginning), first payment not discounted
        # Verify monthly rate conversion
        expected_monthly_rate = annual_to_monthly_rate(0.06)
        assert abs(monthly_rate - expected_monthly_rate) < 0.000001

        # Liability should be around $51,700-$52,500
        assert 51000 < liability < 53000

    def test_constant_payments_end(self):
        """Test liability with constant payments at end of period."""
        payments = [1000] * 60
        liability_end, _ = calculate_lease_liability(
            payments=payments,
            annual_rate=0.06,
            payment_timing='end'
        )

        liability_begin, _ = calculate_lease_liability(
            payments=payments,
            annual_rate=0.06,
            payment_timing='beginning'
        )

        # End of period should be higher (60 payments vs 59 for beginning)
        # Beginning excludes first payment since it's made at commencement
        assert liability_end > liability_begin

    def test_variable_payments(self):
        """Test liability with variable payment schedule."""
        # Payments escalate 3% annually
        payments = []
        base_payment = 1000
        for year in range(5):
            monthly_payment = base_payment * (1.03 ** year)
            payments.extend([monthly_payment] * 12)

        liability, _ = calculate_lease_liability(
            payments=payments,
            annual_rate=0.06,
            payment_timing='beginning'
        )

        # Should be higher than constant $1000 payments
        constant_liability, _ = calculate_lease_liability(
            payments=[1000] * 60,
            annual_rate=0.06,
            payment_timing='beginning'
        )

        assert liability > constant_liability

    def test_free_rent_periods(self):
        """Test liability with free rent periods."""
        payments = [0] * 3 + [1000] * 57  # 3 months free rent

        liability_with_free, _ = calculate_lease_liability(
            payments=payments,
            annual_rate=0.06,
            payment_timing='beginning'
        )

        liability_no_free, _ = calculate_lease_liability(
            payments=[1000] * 60,
            annual_rate=0.06,
            payment_timing='beginning'
        )

        # Free rent should reduce liability
        assert liability_with_free < liability_no_free


# ============================================================================
# ROU ASSET TESTS
# ============================================================================

class TestROUAsset:
    """Test ROU asset calculations."""

    def test_basic_rou_asset(self):
        """Test basic ROU asset calculation."""
        liability = 100000
        rou_asset, components = calculate_rou_asset(
            lease_liability=liability,
            initial_direct_costs=0,
            prepaid_rent=0,
            lease_incentives=0
        )

        # With no adjustments, ROU asset = liability
        assert rou_asset == liability
        assert components['lease_liability'] == liability
        assert components['total_rou_asset'] == liability

    def test_rou_with_initial_costs(self):
        """Test ROU asset with initial direct costs."""
        liability = 100000
        initial_costs = 15000

        rou_asset, components = calculate_rou_asset(
            lease_liability=liability,
            initial_direct_costs=initial_costs
        )

        # ROU asset should increase by initial costs
        assert rou_asset == liability + initial_costs
        assert components['initial_direct_costs'] == initial_costs

    def test_rou_with_incentives(self):
        """Test ROU asset with lease incentives."""
        liability = 100000
        incentives = 25000

        rou_asset, components = calculate_rou_asset(
            lease_liability=liability,
            lease_incentives=incentives
        )

        # ROU asset should decrease by incentives
        assert rou_asset == liability - incentives
        assert components['lease_incentives'] == -incentives

    def test_rou_with_all_adjustments(self):
        """Test ROU asset with all adjustments."""
        liability = 100000
        initial_costs = 15000
        prepaid = 5000
        incentives = 25000

        rou_asset, components = calculate_rou_asset(
            lease_liability=liability,
            initial_direct_costs=initial_costs,
            prepaid_rent=prepaid,
            lease_incentives=incentives
        )

        expected = liability + initial_costs + prepaid - incentives
        assert rou_asset == expected
        assert components['total_rou_asset'] == expected


# ============================================================================
# AMORTIZATION SCHEDULE TESTS
# ============================================================================

class TestAmortizationSchedule:
    """Test lease liability amortization schedule."""

    def test_amortization_final_balance_zero(self):
        """Test that amortization ends at zero balance."""
        payments = [1000] * 60
        liability, monthly_rate = calculate_lease_liability(
            payments, 0.06, 'beginning'
        )

        schedule = generate_liability_amortization(
            initial_liability=liability,
            monthly_payments=payments,
            monthly_rate=monthly_rate,
            commencement_date=datetime(2025, 1, 1),
            payment_timing='beginning'
        )

        # Final balance should be zero (within rounding)
        final_balance = schedule.iloc[-1]['Closing_Balance']
        assert abs(final_balance) < 10.0  # Within $10 (rounding)

    def test_amortization_total_principal(self):
        """Test that total principal reduction equals total payments."""
        payments = [1000] * 60
        liability, monthly_rate = calculate_lease_liability(
            payments, 0.06, 'beginning'
        )

        schedule = generate_liability_amortization(
            initial_liability=liability,
            monthly_payments=payments,
            monthly_rate=monthly_rate,
            commencement_date=datetime(2025, 1, 1),
            payment_timing='beginning'
        )

        total_principal = schedule['Principal_Reduction'].sum()
        total_payments = sum(payments)

        # For annuity due: Total principal = all payments (including first at commencement)
        # This equals initial liability + first payment
        expected = liability + payments[0]
        assert abs(total_principal - expected) < 1.0  # Within $1

    def test_amortization_interest_decreases(self):
        """Test that interest expense decreases over time."""
        payments = [1000] * 60
        liability, monthly_rate = calculate_lease_liability(
            payments, 0.06, 'beginning'
        )

        schedule = generate_liability_amortization(
            initial_liability=liability,
            monthly_payments=payments,
            monthly_rate=monthly_rate,
            commencement_date=datetime(2025, 1, 1),
            payment_timing='beginning'
        )

        # Exclude period 0
        interest_expenses = schedule[schedule['Period'] > 0]['Interest_Expense'].tolist()

        # Interest should generally decrease (allow for small variations)
        first_half_avg = np.mean(interest_expenses[:30])
        second_half_avg = np.mean(interest_expenses[30:])

        assert first_half_avg > second_half_avg

    def test_amortization_cumulative(self):
        """Test cumulative interest and principal tracking."""
        payments = [1000] * 60
        liability, monthly_rate = calculate_lease_liability(
            payments, 0.06, 'beginning'
        )

        schedule = generate_liability_amortization(
            initial_liability=liability,
            monthly_payments=payments,
            monthly_rate=monthly_rate,
            commencement_date=datetime(2025, 1, 1),
            payment_timing='beginning'
        )

        # Final cumulative values
        final_cum_interest = schedule.iloc[-1]['Cumulative_Interest']
        final_cum_principal = schedule.iloc[-1]['Cumulative_Principal']

        # Should equal sum of respective columns
        total_interest = schedule['Interest_Expense'].sum()
        total_principal = schedule['Principal_Reduction'].sum()

        assert abs(final_cum_interest - total_interest) < 0.10  # Within 10 cents
        assert abs(final_cum_principal - total_principal) < 0.10  # Within 10 cents


# ============================================================================
# DEPRECIATION SCHEDULE TESTS
# ============================================================================

class TestDepreciationSchedule:
    """Test ROU asset depreciation schedule."""

    def test_depreciation_straight_line(self):
        """Test straight-line depreciation."""
        rou_asset = 100000
        term = 60

        schedule = generate_rou_depreciation(
            initial_rou_asset=rou_asset,
            lease_term_months=term,
            commencement_date=datetime(2025, 1, 1)
        )

        # Monthly depreciation should be constant (except final month)
        depreciation_expenses = schedule[schedule['Period'] > 0]['Depreciation_Expense'].tolist()
        regular_depreciation = depreciation_expenses[:-1]  # Exclude final month

        # All regular periods should have same depreciation
        expected_monthly = rou_asset / term
        for depreciation in regular_depreciation[:-1]:  # Check most periods
            assert abs(depreciation - expected_monthly) < 0.50  # Within $0.50

    def test_depreciation_final_nbv_zero(self):
        """Test that final net book value is zero."""
        schedule = generate_rou_depreciation(
            initial_rou_asset=100000,
            lease_term_months=60,
            commencement_date=datetime(2025, 1, 1)
        )

        final_nbv = schedule.iloc[-1]['Closing_NBV']
        assert abs(final_nbv) < 0.01  # Within 1 cent

    def test_depreciation_accumulated(self):
        """Test accumulated depreciation equals ROU asset."""
        rou_asset = 100000

        schedule = generate_rou_depreciation(
            initial_rou_asset=rou_asset,
            lease_term_months=60,
            commencement_date=datetime(2025, 1, 1)
        )

        final_accumulated = schedule.iloc[-1]['Accumulated_Depreciation']
        assert abs(final_accumulated - rou_asset) < 0.01


# ============================================================================
# FULL CALCULATION TESTS
# ============================================================================

class TestFullCalculation:
    """Test complete IFRS 16 calculation."""

    @pytest.fixture
    def simple_lease_inputs(self):
        """Simple lease for testing."""
        return LeaseInputs(
            monthly_payments=[1000] * 60,
            annual_discount_rate=0.06,
            tenant_name="Test Tenant",
            property_address="Test Property",
            payment_timing='beginning'
        )

    def test_full_calculation_runs(self, simple_lease_inputs):
        """Test that full calculation completes without errors."""
        result = calculate_ifrs16(simple_lease_inputs)

        # Check all required outputs exist
        assert result.initial_lease_liability > 0
        assert result.initial_rou_asset > 0
        assert result.total_interest_expense > 0
        assert result.total_depreciation > 0
        assert isinstance(result.amortization_schedule, pd.DataFrame)
        assert isinstance(result.depreciation_schedule, pd.DataFrame)
        assert isinstance(result.annual_summary, pd.DataFrame)

    def test_total_cost_components(self, simple_lease_inputs):
        """Test that total lease cost = interest + depreciation."""
        result = calculate_ifrs16(simple_lease_inputs)

        expected_cost = result.total_interest_expense + result.total_depreciation
        assert abs(result.total_lease_cost - expected_cost) < 0.01

    def test_cash_vs_accrual(self, simple_lease_inputs):
        """Test relationship between cash paid and accrual expense."""
        result = calculate_ifrs16(simple_lease_inputs)

        total_cash = sum(simple_lease_inputs.monthly_payments)
        total_accrual = result.total_lease_cost

        # Total cash should be higher than accrual (interest < cash for liability)
        # But depends on initial costs/incentives
        # At minimum, check they're in reasonable relationship
        assert 0.5 < total_accrual / total_cash < 1.5

    def test_with_initial_costs(self):
        """Test calculation with initial direct costs."""
        inputs = LeaseInputs(
            monthly_payments=[1000] * 60,
            annual_discount_rate=0.06,
            initial_direct_costs=15000,
            payment_timing='beginning'
        )

        result = calculate_ifrs16(inputs)

        # ROU asset should be higher than liability
        assert result.initial_rou_asset > result.initial_lease_liability
        assert result.initial_rou_asset == result.initial_lease_liability + 15000

    def test_with_incentives(self):
        """Test calculation with lease incentives."""
        inputs = LeaseInputs(
            monthly_payments=[1000] * 60,
            annual_discount_rate=0.06,
            lease_incentives=25000,
            payment_timing='beginning'
        )

        result = calculate_ifrs16(inputs)

        # ROU asset should be lower than liability
        assert result.initial_rou_asset < result.initial_lease_liability
        assert result.initial_rou_asset == result.initial_lease_liability - 25000


# ============================================================================
# ANNUAL SUMMARY TESTS
# ============================================================================

class TestAnnualSummary:
    """Test annual summary generation."""

    def test_annual_aggregation(self):
        """Test that annual summary correctly aggregates monthly data."""
        inputs = LeaseInputs(
            monthly_payments=[1000] * 60,
            annual_discount_rate=0.06,
            payment_timing='beginning'
        )

        result = calculate_ifrs16(inputs)

        # Check year 1
        year1 = result.annual_summary[result.annual_summary['Year'] == 1].iloc[0]

        assert year1['Cash_Paid'] == 12000  # 12 months × $1000

    def test_annual_summary_totals(self):
        """Test that annual summary totals match overall totals."""
        inputs = LeaseInputs(
            monthly_payments=[1000] * 60,
            annual_discount_rate=0.06,
            payment_timing='beginning'
        )

        result = calculate_ifrs16(inputs)

        # Sum of annual interest should equal total interest
        total_annual_interest = result.annual_summary['Interest_Expense'].sum()
        assert abs(total_annual_interest - result.total_interest_expense) < 1.0

        # Sum of annual depreciation should equal total depreciation
        total_annual_deprec = result.annual_summary['Depreciation_Expense'].sum()
        assert abs(total_annual_deprec - result.total_depreciation) < 1.0


# ============================================================================
# SENSITIVITY ANALYSIS TESTS
# ============================================================================

class TestSensitivityAnalysis:
    """Test sensitivity analysis."""

    @pytest.fixture
    def base_inputs(self):
        """Base case for sensitivity analysis."""
        return LeaseInputs(
            monthly_payments=[1000] * 60,
            annual_discount_rate=0.06,
            payment_timing='beginning'
        )

    def test_sensitivity_rate_increase_decreases_liability(self, base_inputs):
        """Test that higher discount rate decreases liability."""
        sensitivity = sensitivity_analysis(base_inputs, rate_variations=[0, 0.01])

        base_case = sensitivity[sensitivity['Scenario'] == 'Base Case'].iloc[0]
        higher_rate = sensitivity[sensitivity['Scenario'] == 'Rate +1.0%'].iloc[0]

        # Higher discount rate = lower present value = lower liability
        assert higher_rate['Lease_Liability'] < base_case['Lease_Liability']

    def test_sensitivity_term_longer_increases_liability(self, base_inputs):
        """Test that longer term increases liability."""
        sensitivity = sensitivity_analysis(
            base_inputs,
            rate_variations=[0],
            term_variations=[0, 12]
        )

        base_case = sensitivity[sensitivity['Scenario'] == 'Base Case'].iloc[0]
        longer_term = sensitivity[sensitivity['Scenario'] == 'Term +12 months'].iloc[0]

        # Longer term = more payments = higher liability
        assert longer_term['Lease_Liability'] > base_case['Lease_Liability']

    def test_sensitivity_variance_calculation(self, base_inputs):
        """Test that variance from base is calculated correctly."""
        sensitivity = sensitivity_analysis(base_inputs)

        base_case = sensitivity[sensitivity['Scenario'] == 'Base Case'].iloc[0]
        assert base_case['Variance_from_Base'] == 0

        # Term variations should have significant non-zero variance
        # (Rate variations may have near-zero variance when no initial costs/incentives,
        #  because total cost = total payments regardless of discount rate)
        term_scenarios = sensitivity[sensitivity['Scenario'].str.contains('Term', na=False)]
        for idx, row in term_scenarios.iterrows():
            assert abs(row['Variance_from_Base']) > 100  # Term changes significantly affect cost


# ============================================================================
# CSV EXPORT TESTS
# ============================================================================

class TestCSVExport:
    """Test CSV export functionality."""

    def test_csv_export_creates_files(self, tmp_path):
        """Test that CSV export creates all required files."""
        inputs = LeaseInputs(
            monthly_payments=[1000] * 60,
            annual_discount_rate=0.06,
            tenant_name="TestCorp",
            payment_timing='beginning'
        )

        result = calculate_ifrs16(inputs)

        files = export_to_csv(result, output_dir=str(tmp_path))

        # Check all files created
        assert 'amortization' in files
        assert 'depreciation' in files
        assert 'annual_summary' in files

        # Verify files exist
        for file_path in files.values():
            assert os.path.exists(file_path)

    def test_csv_export_content_valid(self, tmp_path):
        """Test that exported CSV files have valid content."""
        inputs = LeaseInputs(
            monthly_payments=[1000] * 60,
            annual_discount_rate=0.06,
            tenant_name="TestCorp",
            payment_timing='beginning'
        )

        result = calculate_ifrs16(inputs)
        files = export_to_csv(result, output_dir=str(tmp_path))

        # Read amortization file
        amort_df = pd.read_csv(files['amortization'])
        # For annuity due with 60 payments: Period 0 + 59 amortization periods = 60 rows
        assert len(amort_df) == 60
        assert 'Opening_Balance' in amort_df.columns
        assert 'Interest_Expense' in amort_df.columns


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_single_payment(self):
        """Test lease with single payment."""
        inputs = LeaseInputs(
            monthly_payments=[10000],
            annual_discount_rate=0.06,
            payment_timing='beginning'
        )

        result = calculate_ifrs16(inputs)

        # With single payment at beginning, liability = 0 (payment made at commencement)
        assert result.initial_lease_liability == 0

    def test_very_short_term(self):
        """Test very short lease term."""
        inputs = LeaseInputs(
            monthly_payments=[1000] * 3,
            annual_discount_rate=0.06,
            payment_timing='beginning'
        )

        result = calculate_ifrs16(inputs)

        # Should complete without error
        assert result.initial_lease_liability > 0
        # For annuity due with 3 payments: Period 0 + 2 amortization periods = 3 rows
        assert len(result.amortization_schedule) == 3

    def test_zero_discount_rate_error(self):
        """Test that zero discount rate raises error."""
        with pytest.raises(ValueError):
            LeaseInputs(
                monthly_payments=[1000] * 60,
                annual_discount_rate=0.0,
                payment_timing='beginning'
            )

    def test_mismatched_payment_term(self):
        """Test error when payment count doesn't match term."""
        with pytest.raises(ValueError):
            LeaseInputs(
                monthly_payments=[1000] * 60,
                annual_discount_rate=0.06,
                lease_term_months=48,  # Mismatch!
                payment_timing='beginning'
            )


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
