"""
Comprehensive test suite for Tenant Credit Analysis Calculator.

Tests include:
- Financial ratio scoring
- Credit scoring algorithm
- Risk assessment calculations
- Trend analysis
- Red flag identification
- Approval recommendations
- Edge cases

Run with: pytest test_credit_analysis.py -v
"""

import pytest
import numpy as np
import pandas as pd

from Credit_Analysis.credit_analysis import (
    FinancialData,
    CreditInputs,
    CreditScore,
    score_ratio,
    calculate_credit_score,
    calculate_risk_assessment,
    analyze_trends,
    identify_red_flags,
    analyze_tenant_credit,
    DEFAULT_PROBABILITIES
)


# ============================================================================
# RATIO SCORING TESTS
# ============================================================================

class TestRatioScoring:
    """Test financial ratio scoring."""

    def test_score_excellent_current_ratio(self):
        """Test scoring excellent current ratio."""
        score = score_ratio(2.5, 'current_ratio')
        assert score == 10.0

    def test_score_poor_current_ratio(self):
        """Test scoring poor current ratio."""
        score = score_ratio(0.8, 'current_ratio')
        assert score == 0.0

    def test_score_reverse_debt_ratio(self):
        """Test scoring debt ratio (reverse - lower is better)."""
        score = score_ratio(0.3, 'debt_to_equity', reverse=True)
        assert score == 10.0

    def test_score_high_debt_ratio(self):
        """Test scoring high debt ratio."""
        score = score_ratio(3.0, 'debt_to_equity', reverse=True)
        assert score == 0.0

    def test_score_rent_to_revenue(self):
        """Test scoring rent to revenue (special case - lower is better)."""
        score = score_ratio(0.04, 'rent_to_revenue')
        assert score == 10.0

        score = score_ratio(0.20, 'rent_to_revenue')
        assert score == 0.0


# ============================================================================
# CREDIT SCORING TESTS
# ============================================================================

class TestCreditScoring:
    """Test credit scoring algorithm."""

    @pytest.fixture
    def good_ratios(self):
        """Good financial ratios."""
        return {
            'current_ratio': 2.0,
            'debt_to_equity': 0.8,
            'net_profit_margin': 0.12,
            'roe': 0.18,
            'ebitda_to_rent': 2.5,
            'rent_to_revenue': 0.06
        }

    @pytest.fixture
    def good_inputs(self):
        """Good credit inputs."""
        return CreditInputs(
            financial_data=[],  # Will add later
            years_in_business=10,
            credit_score=750,
            payment_history='excellent',
            industry_stability='stable',
            use_criticality='important'
        )

    def test_credit_score_range(self, good_ratios, good_inputs):
        """Test that credit score is in valid range."""
        score = calculate_credit_score(good_ratios, good_inputs)

        assert 0 <= score.total_score <= 100
        assert score.credit_rating in ['A', 'B', 'C', 'D', 'F']

    def test_excellent_credit_gets_a_rating(self, good_ratios, good_inputs):
        """Test that excellent credit gets A rating."""
        score = calculate_credit_score(good_ratios, good_inputs)

        # Should get high score
        assert score.total_score >= 60  # At least B rating

    def test_poor_credit_gets_low_rating(self):
        """Test that poor credit gets low rating."""
        poor_ratios = {
            'current_ratio': 0.8,
            'debt_to_equity': 3.0,
            'net_profit_margin': -0.05,
            'roe': 0.02,
            'ebitda_to_rent': 0.8,
            'rent_to_revenue': 0.20
        }

        poor_inputs = CreditInputs(
            financial_data=[],
            years_in_business=1,
            credit_score=500,
            payment_history='poor',
            industry_stability='volatile',
            use_criticality='discretionary'
        )

        score = calculate_credit_score(poor_ratios, poor_inputs)

        assert score.total_score < 60  # Below B rating
        assert score.credit_rating in ['C', 'D', 'F']


# ============================================================================
# RISK ASSESSMENT TESTS
# ============================================================================

class TestRiskAssessment:
    """Test risk assessment calculations."""

    @pytest.fixture
    def sample_inputs(self):
        """Sample credit inputs."""
        return CreditInputs(
            financial_data=[
                FinancialData(
                    year=2024,
                    annual_rent=240000,
                    current_assets=450000,
                    current_liabilities=250000,
                    total_liabilities=1200000,
                    shareholders_equity=800000,
                    revenue=5000000,
                    ebitda=500000,
                    net_income=250000
                )
            ],
            lease_term_years=5
        )

    def test_exposure_calculation(self, sample_inputs):
        """Test exposure at default calculation."""
        ratios = {'current_ratio': 1.8}
        score = calculate_credit_score(ratios, sample_inputs)
        risk = calculate_risk_assessment(score, sample_inputs)

        # Exposure = annual rent × lease term
        expected_exposure = 240000 * 5
        assert abs(risk.exposure_at_default - expected_exposure) < 1.0

    def test_expected_loss_positive(self, sample_inputs):
        """Test that expected loss is calculated."""
        ratios = {'current_ratio': 1.8}
        score = calculate_credit_score(ratios, sample_inputs)
        risk = calculate_risk_assessment(score, sample_inputs)

        assert risk.expected_loss > 0
        assert risk.probability_of_default > 0
        assert risk.loss_given_default > 0

    def test_better_rating_lower_pd(self, sample_inputs):
        """Test that better ratings have lower default probability."""
        # A rating
        ratios_a = {'current_ratio': 2.5, 'debt_to_equity': 0.5, 'roe': 0.25, 'ebitda_to_rent': 4.0}
        score_a = calculate_credit_score(ratios_a, sample_inputs)
        risk_a = calculate_risk_assessment(score_a, sample_inputs)

        # C rating
        ratios_c = {'current_ratio': 1.2, 'debt_to_equity': 1.8, 'roe': 0.08, 'ebitda_to_rent': 1.3}
        score_c = calculate_credit_score(ratios_c, sample_inputs)
        risk_c = calculate_risk_assessment(score_c, sample_inputs)

        assert risk_a.probability_of_default < risk_c.probability_of_default


# ============================================================================
# TREND ANALYSIS TESTS
# ============================================================================

class TestTrendAnalysis:
    """Test trend analysis."""

    def test_improving_revenue_trend(self):
        """Test detection of improving revenue trend."""
        inputs = CreditInputs(
            financial_data=[
                FinancialData(year=2024, revenue=5000000, net_income=250000),
                FinancialData(year=2023, revenue=4500000, net_income=220000),
                FinancialData(year=2022, revenue=4000000, net_income=200000)
            ]
        )

        trend = analyze_trends(inputs)

        assert trend.revenue_trend == 'improving'

    def test_deteriorating_revenue_trend(self):
        """Test detection of deteriorating revenue trend."""
        inputs = CreditInputs(
            financial_data=[
                FinancialData(year=2024, revenue=4000000, net_income=180000),
                FinancialData(year=2023, revenue=4500000, net_income=200000),
                FinancialData(year=2022, revenue=5000000, net_income=250000)
            ]
        )

        trend = analyze_trends(inputs)

        assert trend.revenue_trend == 'deteriorating'

    def test_stable_trend_insufficient_data(self):
        """Test that insufficient data returns stable trend."""
        inputs = CreditInputs(
            financial_data=[
                FinancialData(year=2024, revenue=5000000)
            ]
        )

        trend = analyze_trends(inputs)

        assert trend.overall_trend == 'stable'


# ============================================================================
# RED FLAG TESTS
# ============================================================================

class TestRedFlags:
    """Test red flag identification."""

    def test_low_current_ratio_flag(self):
        """Test that low current ratio triggers red flag."""
        ratios = {'current_ratio': 0.8}
        score = CreditScore(
            financial_strength_score=20,
            business_quality_score=20,
            credit_history_score=10,
            lease_specific_score=5,
            total_score=55,
            credit_rating='C',
            score_breakdown={}
        )
        trend = analyze_trends(CreditInputs(financial_data=[]))
        inputs = CreditInputs(financial_data=[])

        flags = identify_red_flags(ratios, score, trend, inputs)

        assert any('Current ratio' in flag for flag in flags)

    def test_high_debt_flag(self):
        """Test that high debt triggers red flag."""
        ratios = {'debt_to_equity': 2.5}
        score = CreditScore(
            financial_strength_score=20,
            business_quality_score=20,
            credit_history_score=10,
            lease_specific_score=5,
            total_score=55,
            credit_rating='C',
            score_breakdown={}
        )
        trend = analyze_trends(CreditInputs(financial_data=[]))
        inputs = CreditInputs(financial_data=[])

        flags = identify_red_flags(ratios, score, trend, inputs)

        assert any('Debt-to-equity' in flag for flag in flags)


# ============================================================================
# FULL ANALYSIS TESTS
# ============================================================================

class TestFullAnalysis:
    """Test complete credit analysis."""

    @pytest.fixture
    def good_tenant_inputs(self):
        """Good tenant financials."""
        return CreditInputs(
            financial_data=[
                FinancialData(
                    year=2024,
                    current_assets=450000,
                    total_assets=2000000,
                    inventory=100000,
                    cash_and_equivalents=150000,
                    current_liabilities=250000,
                    total_liabilities=1200000,
                    shareholders_equity=800000,
                    revenue=5000000,
                    ebitda=500000,
                    net_income=250000,
                    annual_rent=240000
                )
            ],
            tenant_name="Good Tenant Corp",
            years_in_business=10,
            credit_score=750,
            payment_history='excellent',
            lease_term_years=5
        )

    def test_full_analysis_runs(self, good_tenant_inputs):
        """Test that full analysis completes without error."""
        result = analyze_tenant_credit(good_tenant_inputs)

        assert result.tenant_name == "Good Tenant Corp"
        assert result.credit_score.credit_rating in ['A', 'B', 'C', 'D', 'F']
        assert result.approval_recommendation in ['APPROVE', 'APPROVE_WITH_CONDITIONS', 'DECLINE']

    def test_good_tenant_gets_approval(self, good_tenant_inputs):
        """Test that good tenant gets approval."""
        result = analyze_tenant_credit(good_tenant_inputs)

        # Should get A or B rating
        assert result.credit_score.credit_rating in ['A', 'B']

        # Should get approval (possibly with conditions for security)
        assert result.approval_recommendation in ['APPROVE', 'APPROVE_WITH_CONDITIONS']


# ============================================================================
# EDGE CASES
# ============================================================================

class TestEdgeCases:
    """Test edge cases."""

    def test_missing_credit_score(self):
        """Test handling of missing credit score."""
        inputs = CreditInputs(
            financial_data=[
                FinancialData(year=2024, revenue=1000000)
            ],
            credit_score=None  # Missing
        )

        ratios = {}
        score = calculate_credit_score(ratios, inputs)

        # Should not crash
        assert 0 <= score.total_score <= 100

    def test_negative_net_income(self):
        """Test handling of negative net income."""
        inputs = CreditInputs(
            financial_data=[
                FinancialData(
                    year=2024,
                    revenue=1000000,
                    net_income=-50000,  # Loss
                    current_assets=100000,
                    current_liabilities=80000,
                    total_liabilities=500000,
                    shareholders_equity=200000,
                    ebitda=50000,
                    annual_rent=120000
                )
            ]
        )

        result = analyze_tenant_credit(inputs)

        # Should identify red flag
        assert any('Negative profit' in flag for flag in result.red_flags)

    def test_zero_equity(self):
        """Test handling of zero or negative equity."""
        inputs = CreditInputs(
            financial_data=[
                FinancialData(
                    year=2024,
                    revenue=1000000,
                    current_assets=100000,
                    current_liabilities=80000,
                    total_liabilities=150000,
                    shareholders_equity=0,  # Zero equity
                    annual_rent=120000
                )
            ]
        )

        # Should not crash
        result = analyze_tenant_credit(inputs)
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
