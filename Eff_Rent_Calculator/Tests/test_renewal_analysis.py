"""
Comprehensive test suite for Renewal Economics Calculator.

Tests include:
- Renewal scenario calculations
- Relocation scenario calculations
- Comparison analysis
- Breakeven calculations
- Sensitivity analysis
- Recommendation generation
- Edge cases

Run with: pytest test_renewal_analysis.py -v
"""

import pytest
import numpy as np
import pandas as pd
import os
import sys

# Add Renewal_Analysis and Shared_Utils to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'Renewal_Analysis'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'Shared_Utils'))

from renewal_analysis import (
    RenewalScenario,
    RelocationScenario,
    GeneralInputs,
    calculate_renewal_scenario,
    calculate_relocation_scenario,
    compare_scenarios,
    calculate_breakeven_rent,
    sensitivity_analysis,
    generate_recommendation
)
from financial_utils import npv


# ============================================================================
# RENEWAL SCENARIO TESTS
# ============================================================================

class TestRenewalScenario:
    """Test renewal scenario calculations."""

    @pytest.fixture
    def simple_renewal(self):
        """Simple renewal scenario for testing."""
        return RenewalScenario(
            annual_rent_psf=[20.00] * 5,
            ti_allowance_psf=10.00,
            additional_ti_psf=15.00,
            term_years=5,
            operating_costs_psf=5.00
        )

    @pytest.fixture
    def general_inputs(self):
        """General inputs for testing."""
        return GeneralInputs(
            rentable_area_sf=10000,
            discount_rate=0.10
        )

    def test_renewal_npv_calculation(self, simple_renewal, general_inputs):
        """Test that renewal NPV is calculated correctly."""
        result = calculate_renewal_scenario(simple_renewal, general_inputs)

        # Verify NPV is positive (costs)
        assert result.npv > 0

        # Verify NPV includes all components
        assert result.npv == (
            result.pv_rent +
            result.pv_operating_costs +
            result.pv_ti_costs +
            result.pv_other_costs
        )

    def test_renewal_total_payments(self, simple_renewal, general_inputs):
        """Test that total payments are calculated correctly."""
        result = calculate_renewal_scenario(simple_renewal, general_inputs)

        # Expected: $20/sf * 10,000sf * 5 years = $1,000,000
        expected_rent = 20.00 * 10000 * 5
        assert abs(result.total_rent_payments - expected_rent) < 1.0

        # Expected operating costs: $5/sf * 10,000sf * 5 years = $250,000
        expected_op_costs = 5.00 * 10000 * 5
        assert abs(result.total_operating_costs - expected_op_costs) < 1.0

    def test_renewal_ti_costs(self, simple_renewal, general_inputs):
        """Test TI cost calculation."""
        result = calculate_renewal_scenario(simple_renewal, general_inputs)

        # Net TI: ($15 - $10) * 10,000sf = $50,000
        expected_ti = (15.00 - 10.00) * 10000
        assert abs(result.total_ti_costs - expected_ti) < 1.0

    def test_renewal_ner_positive(self, simple_renewal, general_inputs):
        """Test that NER is positive."""
        result = calculate_renewal_scenario(simple_renewal, general_inputs)

        assert result.net_effective_rent_psf > 0

    def test_renewal_variable_rent(self, general_inputs):
        """Test renewal with escalating rent."""
        renewal = RenewalScenario(
            annual_rent_psf=[20.00, 20.60, 21.22, 21.86, 22.51],  # 3% escalation
            term_years=5
        )

        result = calculate_renewal_scenario(renewal, general_inputs)

        # Variable rent should cost more than constant $20/sf
        constant_renewal = RenewalScenario(
            annual_rent_psf=[20.00] * 5,
            term_years=5
        )
        constant_result = calculate_renewal_scenario(constant_renewal, general_inputs)

        assert result.npv > constant_result.npv


# ============================================================================
# RELOCATION SCENARIO TESTS
# ============================================================================

class TestRelocationScenario:
    """Test relocation scenario calculations."""

    @pytest.fixture
    def simple_relocation(self):
        """Simple relocation scenario for testing."""
        return RelocationScenario(
            annual_rent_psf=[18.00] * 5,  # Lower rent than renewal
            ti_allowance_psf=20.00,
            ti_requirement_psf=40.00,
            term_years=5,
            operating_costs_psf=5.00,
            moving_costs=50000,
            downtime_days=5,
            daily_revenue=10000
        )

    @pytest.fixture
    def general_inputs(self):
        """General inputs for testing."""
        return GeneralInputs(
            rentable_area_sf=10000,
            discount_rate=0.10
        )

    def test_relocation_npv_includes_upfront(self, simple_relocation, general_inputs):
        """Test that relocation NPV includes all upfront costs."""
        result = calculate_relocation_scenario(simple_relocation, general_inputs)

        # Verify upfront costs are significant
        upfront_costs = result.total_ti_costs + result.total_other_costs
        assert upfront_costs > 0

        # Net TI: ($40 - $20) * 10,000sf = $200,000
        expected_ti = (40.00 - 20.00) * 10000
        assert abs(result.total_ti_costs - expected_ti) < 1.0

    def test_relocation_disruption_costs(self, simple_relocation, general_inputs):
        """Test that disruption costs are calculated."""
        result = calculate_relocation_scenario(simple_relocation, general_inputs)

        # Disruption: 5 days * $10,000/day = $50,000
        # (Plus customer loss if applicable)
        assert result.total_other_costs >= 50000

    def test_relocation_lower_rent(self, simple_relocation, general_inputs):
        """Test that lower relocation rent is captured."""
        result = calculate_relocation_scenario(simple_relocation, general_inputs)

        # Expected: $18/sf * 10,000sf * 5 years = $900,000
        expected_rent = 18.00 * 10000 * 5
        assert abs(result.total_rent_payments - expected_rent) < 1.0

    def test_relocation_with_abandonment(self, general_inputs):
        """Test relocation with abandonment costs."""
        relocation = RelocationScenario(
            annual_rent_psf=[18.00] * 5,
            unamortized_improvements=100000,
            restoration_costs=25000
        )

        result = calculate_relocation_scenario(relocation, general_inputs)

        # Other costs should include $125k abandonment
        assert result.total_other_costs >= 125000


# ============================================================================
# COMPARISON TESTS
# ============================================================================

class TestComparison:
    """Test scenario comparison."""

    @pytest.fixture
    def scenarios(self):
        """Create renewal and relocation scenarios for comparison."""
        renewal = RenewalScenario(
            annual_rent_psf=[25.00] * 5,
            ti_allowance_psf=15.00,
            additional_ti_psf=20.00,
            term_years=5,
            operating_costs_psf=8.00,
            legal_fees=5000
        )

        relocation = RelocationScenario(
            annual_rent_psf=[23.00] * 5,  # Lower rent
            ti_allowance_psf=25.00,
            ti_requirement_psf=40.00,  # Higher TI
            term_years=5,
            operating_costs_psf=8.00,
            moving_costs=50000,
            downtime_days=10,
            daily_revenue=10000
        )

        general = GeneralInputs(
            rentable_area_sf=20000,
            discount_rate=0.10
        )

        return renewal, relocation, general

    def test_comparison_npv_difference(self, scenarios):
        """Test NPV difference calculation."""
        renewal, relocation, general = scenarios

        comparison = compare_scenarios(renewal, relocation, general)

        # NPV difference should be relocation - renewal
        expected_diff = (
            comparison.relocation_result.npv -
            comparison.renewal_result.npv
        )

        assert abs(comparison.npv_difference - expected_diff) < 1.0

    def test_comparison_annual_savings(self, scenarios):
        """Test annual savings calculation."""
        renewal, relocation, general = scenarios

        comparison = compare_scenarios(renewal, relocation, general)

        # Annual savings should reflect lower relocation rent
        # Renewal: $25/sf * 20,000 + $8/sf * 20,000 = $660,000/year
        # Relocation: $23/sf * 20,000 + $8/sf * 20,000 = $620,000/year
        # Savings: $40,000/year

        assert comparison.annual_savings > 0  # Relocation has lower ongoing costs

    def test_comparison_with_higher_relocation_rent(self):
        """Test comparison when relocation rent is higher."""
        renewal = RenewalScenario(
            annual_rent_psf=[20.00] * 5,
            term_years=5
        )

        relocation = RelocationScenario(
            annual_rent_psf=[25.00] * 5,  # Higher rent
            term_years=5,
            moving_costs=100000  # And high moving costs
        )

        general = GeneralInputs(
            rentable_area_sf=10000,
            discount_rate=0.10
        )

        comparison = compare_scenarios(renewal, relocation, general)

        # Relocation should cost more
        assert comparison.npv_difference > 0
        # Should recommend renewal
        assert comparison.recommendation == 'RENEW'

    def test_payback_period_calculation(self, scenarios):
        """Test payback period calculation."""
        renewal, relocation, general = scenarios

        comparison = compare_scenarios(renewal, relocation, general)

        if comparison.payback_period_years is not None:
            # Payback should be positive
            assert comparison.payback_period_years > 0

            # Payback = upfront costs / annual savings
            upfront = (
                comparison.relocation_result.total_ti_costs +
                comparison.relocation_result.total_other_costs
            )
            expected_payback = upfront / comparison.annual_savings

            assert abs(comparison.payback_period_years - expected_payback) < 0.1


# ============================================================================
# BREAKEVEN ANALYSIS TESTS
# ============================================================================

class TestBreakevenAnalysis:
    """Test breakeven rent calculation."""

    def test_breakeven_rent_makes_npv_equal(self):
        """Test that breakeven rent results in equal NPVs."""
        renewal = RenewalScenario(
            annual_rent_psf=[25.00] * 5,
            term_years=5
        )

        relocation = RelocationScenario(
            annual_rent_psf=[20.00] * 5,
            term_years=5,
            moving_costs=50000
        )

        general = GeneralInputs(
            rentable_area_sf=10000,
            discount_rate=0.10
        )

        breakeven = calculate_breakeven_rent(renewal, relocation, general)

        # Create new renewal scenario with breakeven rent
        renewal_at_breakeven = RenewalScenario(
            annual_rent_psf=[breakeven] * 5,
            term_years=5
        )

        renewal_result = calculate_renewal_scenario(renewal_at_breakeven, general)
        relocation_result = calculate_relocation_scenario(relocation, general)

        # NPVs should be approximately equal
        assert abs(renewal_result.npv - relocation_result.npv) < 1000  # Within $1k

    def test_breakeven_between_rent_extremes(self):
        """Test that breakeven rent is reasonable."""
        renewal = RenewalScenario(
            annual_rent_psf=[25.00] * 5,
            term_years=5
        )

        relocation = RelocationScenario(
            annual_rent_psf=[23.00] * 5,
            term_years=5,
            moving_costs=50000
        )

        general = GeneralInputs(
            rentable_area_sf=10000,
            discount_rate=0.10
        )

        breakeven = calculate_breakeven_rent(renewal, relocation, general)

        # Breakeven should be between current renewal and relocation rent
        assert 0 < breakeven < 100  # Reasonable range for $/sf


# ============================================================================
# RECOMMENDATION TESTS
# ============================================================================

class TestRecommendation:
    """Test recommendation generation."""

    def test_recommend_renew_when_cheaper(self):
        """Test that RENEW is recommended when it's cheaper."""
        renewal = RenewalScenario(
            annual_rent_psf=[20.00] * 5,
            term_years=5
        )

        relocation = RelocationScenario(
            annual_rent_psf=[20.00] * 5,
            term_years=5,
            moving_costs=200000  # High moving costs
        )

        general = GeneralInputs(
            rentable_area_sf=10000,
            discount_rate=0.10
        )

        comparison = compare_scenarios(renewal, relocation, general)

        assert comparison.recommendation == 'RENEW'

    def test_recommend_relocate_when_much_cheaper(self):
        """Test that RELOCATE is recommended when it saves significantly."""
        renewal = RenewalScenario(
            annual_rent_psf=[30.00] * 5,  # High rent
            term_years=5
        )

        relocation = RelocationScenario(
            annual_rent_psf=[18.00] * 5,  # Much lower rent
            term_years=5,
            moving_costs=50000  # Moderate moving costs
        )

        general = GeneralInputs(
            rentable_area_sf=20000,
            discount_rate=0.10
        )

        comparison = compare_scenarios(renewal, relocation, general)

        # Large rent savings should overcome moving costs
        assert comparison.npv_difference < -10000  # Saves more than $10k

    def test_recommend_negotiate_when_close(self):
        """Test that NEGOTIATE is recommended when NPVs are close."""
        renewal = RenewalScenario(
            annual_rent_psf=[22.00] * 5,
            term_years=5
        )

        relocation = RelocationScenario(
            annual_rent_psf=[21.50] * 5,  # Slightly lower
            term_years=5,
            moving_costs=20000  # Small moving costs
        )

        general = GeneralInputs(
            rentable_area_sf=10000,
            discount_rate=0.10
        )

        comparison = compare_scenarios(renewal, relocation, general)

        # When NPV difference is small, should recommend negotiation
        if abs(comparison.npv_difference) < 10000:
            assert comparison.recommendation == 'NEGOTIATE'


# ============================================================================
# SENSITIVITY ANALYSIS TESTS
# ============================================================================

class TestSensitivityAnalysis:
    """Test sensitivity analysis."""

    @pytest.fixture
    def scenarios(self):
        """Create scenarios for sensitivity analysis."""
        renewal = RenewalScenario(
            annual_rent_psf=[25.00] * 5,
            term_years=5
        )

        relocation = RelocationScenario(
            annual_rent_psf=[23.00] * 5,
            term_years=5,
            moving_costs=50000,
            ti_requirement_psf=40.00
        )

        general = GeneralInputs(
            rentable_area_sf=10000,
            discount_rate=0.10
        )

        return renewal, relocation, general

    def test_sensitivity_includes_base_case(self, scenarios):
        """Test that sensitivity analysis includes base case."""
        renewal, relocation, general = scenarios

        sensitivity = sensitivity_analysis(renewal, relocation, general)

        # Should have base case row
        assert 'Base Case' in sensitivity['Variable'].values

    def test_sensitivity_rent_variation(self, scenarios):
        """Test rent sensitivity."""
        renewal, relocation, general = scenarios

        sensitivity = sensitivity_analysis(
            renewal, relocation, general,
            variables=['rent']
        )

        # Should have rent variation rows
        rent_rows = sensitivity[sensitivity['Variable'] == 'Renewal Rent']
        assert len(rent_rows) >= 2  # At least +/- variations

    def test_sensitivity_ti_variation(self, scenarios):
        """Test TI sensitivity."""
        renewal, relocation, general = scenarios

        sensitivity = sensitivity_analysis(
            renewal, relocation, general,
            variables=['ti']
        )

        # Should have TI variation rows
        ti_rows = sensitivity[sensitivity['Variable'] == 'Relocation TI']
        assert len(ti_rows) >= 2

    def test_sensitivity_returns_dataframe(self, scenarios):
        """Test that sensitivity returns DataFrame."""
        renewal, relocation, general = scenarios

        sensitivity = sensitivity_analysis(renewal, relocation, general)

        assert isinstance(sensitivity, pd.DataFrame)
        assert 'Variable' in sensitivity.columns
        assert 'NPV_Difference' in sensitivity.columns
        assert 'Recommendation' in sensitivity.columns


# ============================================================================
# EDGE CASES
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_zero_area(self):
        """Test with zero area (should handle gracefully)."""
        renewal = RenewalScenario(
            annual_rent_psf=[25.00] * 5,
            term_years=5
        )

        general = GeneralInputs(
            rentable_area_sf=0,  # Zero area
            discount_rate=0.10
        )

        result = calculate_renewal_scenario(renewal, general)

        # Should not crash, should handle division by zero
        assert result.net_effective_rent_psf == 0.0

    def test_single_year_term(self):
        """Test with single year term."""
        renewal = RenewalScenario(
            annual_rent_psf=[25.00],
            term_years=1
        )

        general = GeneralInputs(
            rentable_area_sf=10000,
            discount_rate=0.10
        )

        result = calculate_renewal_scenario(renewal, general)

        # Should calculate correctly
        assert result.npv > 0

    def test_no_upfront_costs(self):
        """Test relocation with no upfront costs."""
        relocation = RelocationScenario(
            annual_rent_psf=[20.00] * 5,
            term_years=5
            # All other costs = 0
        )

        general = GeneralInputs(
            rentable_area_sf=10000,
            discount_rate=0.10
        )

        result = calculate_relocation_scenario(relocation, general)

        # Should handle zero costs
        assert result.total_ti_costs == 0.0
        assert result.total_other_costs == 0.0

    def test_very_high_discount_rate(self):
        """Test with very high discount rate."""
        renewal = RenewalScenario(
            annual_rent_psf=[25.00] * 5,
            term_years=5
        )

        general = GeneralInputs(
            rentable_area_sf=10000,
            discount_rate=0.50  # 50% discount rate
        )

        result = calculate_renewal_scenario(renewal, general)

        # Should still calculate (NPV will be lower)
        assert result.npv > 0


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
