#!/usr/bin/env python3
"""
Unit and Integration Tests for Portfolio Rollover Analysis Calculator

Test Coverage:
- Credit rating mapping (all grades including NR)
- Priority scoring algorithm (normalized components)
- Expiry schedule aggregation
- Risk level criteria
- Scenario modeling with NPV
- Edge cases (empty, single, 0%, 100%)

Author: Claude Code
Version: 1.0.0
Date: 2025-11-06
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from datetime import date
from rollover_calculator import (
    Lease,
    Assumptions,
    PortfolioInput,
    credit_rating_to_score,
    calculate_expiry_schedule,
    calculate_priority_scores,
    calculate_scenario_analysis,
    calculate_rollover_analysis
)


class TestCreditRatingMapping(unittest.TestCase):
    """Test credit rating to risk score conversion"""

    def test_investment_grade_aaa(self):
        """AAA should map to 0.0 (lowest risk)"""
        self.assertEqual(credit_rating_to_score('AAA'), 0.0)
        self.assertEqual(credit_rating_to_score('aaa'), 0.0)  # Case insensitive

    def test_investment_grade_aa(self):
        """AA ratings should map to 0.05-0.15"""
        self.assertEqual(credit_rating_to_score('AA+'), 0.05)
        self.assertEqual(credit_rating_to_score('AA'), 0.10)
        self.assertEqual(credit_rating_to_score('AA-'), 0.15)

    def test_investment_grade_a(self):
        """A ratings should map to 0.15-0.25"""
        self.assertEqual(credit_rating_to_score('A+'), 0.15)
        self.assertEqual(credit_rating_to_score('A'), 0.20)
        self.assertEqual(credit_rating_to_score('A-'), 0.25)

    def test_investment_grade_bbb(self):
        """BBB ratings should map to 0.35-0.45"""
        self.assertEqual(credit_rating_to_score('BBB+'), 0.35)
        self.assertEqual(credit_rating_to_score('BBB'), 0.40)
        self.assertEqual(credit_rating_to_score('BBB-'), 0.45)

    def test_high_yield_bb(self):
        """BB ratings (high yield) should map to 0.55-0.65"""
        self.assertEqual(credit_rating_to_score('BB+'), 0.55)
        self.assertEqual(credit_rating_to_score('BB'), 0.60)
        self.assertEqual(credit_rating_to_score('BB-'), 0.65)

    def test_high_yield_b(self):
        """B ratings should map to 0.75-0.85"""
        self.assertEqual(credit_rating_to_score('B+'), 0.75)
        self.assertEqual(credit_rating_to_score('B'), 0.80)
        self.assertEqual(credit_rating_to_score('B-'), 0.85)

    def test_distressed(self):
        """Distressed ratings should map to 0.95-1.0"""
        self.assertEqual(credit_rating_to_score('CCC+'), 0.90)
        self.assertEqual(credit_rating_to_score('CCC'), 0.95)
        self.assertEqual(credit_rating_to_score('D'), 1.00)

    def test_not_rated(self):
        """Not rated should map to 0.70 (below investment grade assumption)"""
        self.assertEqual(credit_rating_to_score('NR'), 0.70)
        self.assertEqual(credit_rating_to_score(''), 0.70)
        self.assertEqual(credit_rating_to_score(None), 0.70)

    def test_unknown_rating(self):
        """Unknown ratings should default to 0.70 (NR)"""
        self.assertEqual(credit_rating_to_score('UNKNOWN'), 0.70)
        self.assertEqual(credit_rating_to_score('XYZ'), 0.70)


class TestPriorityScoring(unittest.TestCase):
    """Test priority scoring algorithm"""

    def setUp(self):
        """Create sample portfolio for testing"""
        self.analysis_date = date(2025, 11, 6)

    def test_normalized_rent_pct_never_exceeds_one(self):
        """Rent % should never exceed 1.0 (capped by min function)"""
        # Create portfolio with one dominant lease
        lease1 = Lease(
            property_address="Large Property",
            tenant_name="Big Tenant",
            rentable_area_sf=100000,
            current_annual_rent=9000000,  # 90% of portfolio
            lease_expiry_date=date(2026, 12, 31),
            renewal_options=[],
            tenant_credit_rating="AAA",
            below_market_pct=0.0
        )

        lease2 = Lease(
            property_address="Small Property",
            tenant_name="Small Tenant",
            rentable_area_sf=10000,
            current_annual_rent=1000000,  # 10% of portfolio
            lease_expiry_date=date(2026, 12, 31),
            renewal_options=[],
            tenant_credit_rating="AAA",
            below_market_pct=0.0
        )

        portfolio = PortfolioInput(
            portfolio_name="Test",
            analysis_date=self.analysis_date,
            leases=[lease1, lease2],
            assumptions=Assumptions()
        )

        scores = calculate_priority_scores(portfolio)

        # All rent_pct values should be <= 1.0
        for score in scores:
            self.assertLessEqual(score.rent_pct, 1.0)

        # Large lease should have rent_pct = 0.9 (9M / 10M)
        large_lease_score = [s for s in scores if s.lease.tenant_name == "Big Tenant"][0]
        self.assertAlmostEqual(large_lease_score.rent_pct, 0.9, places=2)

    def test_urgency_24_month_window(self):
        """Urgency should use 24-month window"""
        # Lease expiring in 12 months = 0.5 urgency
        lease = Lease(
            property_address="Test",
            tenant_name="Test",
            rentable_area_sf=50000,
            current_annual_rent=500000,
            lease_expiry_date=date(2026, 11, 6),  # 12 months from analysis date
            renewal_options=[],
            tenant_credit_rating="BBB",
            below_market_pct=0.0
        )

        portfolio = PortfolioInput(
            portfolio_name="Test",
            analysis_date=self.analysis_date,
            leases=[lease],
            assumptions=Assumptions()
        )

        scores = calculate_priority_scores(portfolio)
        # 12 months / 24 = 0.5, so 1 - 0.5 = 0.5
        self.assertAlmostEqual(scores[0].urgency, 0.5, places=2)

    def test_urgency_beyond_24_months(self):
        """Leases beyond 24 months should have 0 urgency"""
        lease = Lease(
            property_address="Test",
            tenant_name="Test",
            rentable_area_sf=50000,
            current_annual_rent=500000,
            lease_expiry_date=date(2028, 11, 6),  # 36 months away
            renewal_options=[],
            tenant_credit_rating="BBB",
            below_market_pct=0.0
        )

        portfolio = PortfolioInput(
            portfolio_name="Test",
            analysis_date=self.analysis_date,
            leases=[lease],
            assumptions=Assumptions()
        )

        scores = calculate_priority_scores(portfolio)
        # 36 months > 24, so urgency = 0
        self.assertEqual(scores[0].urgency, 0.0)

    def test_below_market_20_percent_cap(self):
        """Below market should cap at 1.0 for 20% below market"""
        lease = Lease(
            property_address="Test",
            tenant_name="Test",
            rentable_area_sf=50000,
            current_annual_rent=500000,
            lease_expiry_date=date(2027, 6, 30),
            renewal_options=[],
            tenant_credit_rating="BBB",
            below_market_pct=-20.0  # 20% below market
        )

        portfolio = PortfolioInput(
            portfolio_name="Test",
            analysis_date=self.analysis_date,
            leases=[lease],
            assumptions=Assumptions()
        )

        scores = calculate_priority_scores(portfolio)
        # 20% / 20% = 1.0
        self.assertEqual(scores[0].below_market, 1.0)

    def test_below_market_10_percent(self):
        """10% below market should be 0.5"""
        lease = Lease(
            property_address="Test",
            tenant_name="Test",
            rentable_area_sf=50000,
            current_annual_rent=500000,
            lease_expiry_date=date(2027, 6, 30),
            renewal_options=[],
            tenant_credit_rating="BBB",
            below_market_pct=-10.0
        )

        portfolio = PortfolioInput(
            portfolio_name="Test",
            analysis_date=self.analysis_date,
            leases=[lease],
            assumptions=Assumptions()
        )

        scores = calculate_priority_scores(portfolio)
        # 10% / 20% = 0.5
        self.assertEqual(scores[0].below_market, 0.5)

    def test_weighted_priority_score(self):
        """Priority score should be weighted sum of components"""
        lease = Lease(
            property_address="Test",
            tenant_name="Test",
            rentable_area_sf=50000,
            current_annual_rent=500000,  # Will be 100% of portfolio
            lease_expiry_date=date(2026, 11, 6),  # 12 months = 0.5 urgency
            renewal_options=[],
            tenant_credit_rating="BBB",  # 0.40 credit risk
            below_market_pct=-10.0  # 0.5 below market
        )

        portfolio = PortfolioInput(
            portfolio_name="Test",
            analysis_date=self.analysis_date,
            leases=[lease],
            assumptions=Assumptions()
        )

        scores = calculate_priority_scores(portfolio)

        # Expected: (1.0 × 0.40) + (0.5 × 0.30) + (0.5 × 0.20) + (0.40 × 0.10)
        # = 0.40 + 0.15 + 0.10 + 0.04 = 0.69
        expected = (1.0 * 0.40) + (0.5 * 0.30) + (0.5 * 0.20) + (0.40 * 0.10)
        self.assertAlmostEqual(scores[0].priority_score, expected, places=2)

    def test_priority_ranking_sorted_descending(self):
        """Leases should be ranked by priority score (highest first)"""
        lease1 = Lease(
            property_address="Low Priority",
            tenant_name="Low",
            rentable_area_sf=10000,
            current_annual_rent=100000,
            lease_expiry_date=date(2029, 12, 31),  # Far away
            renewal_options=[],
            tenant_credit_rating="AAA",
            below_market_pct=0.0
        )

        lease2 = Lease(
            property_address="High Priority",
            tenant_name="High",
            rentable_area_sf=100000,
            current_annual_rent=1000000,
            lease_expiry_date=date(2026, 3, 31),  # Soon
            renewal_options=[],
            tenant_credit_rating="B",
            below_market_pct=-15.0
        )

        portfolio = PortfolioInput(
            portfolio_name="Test",
            analysis_date=self.analysis_date,
            leases=[lease1, lease2],
            assumptions=Assumptions()
        )

        scores = calculate_priority_scores(portfolio)

        # High priority should be rank 1
        self.assertEqual(scores[0].lease.tenant_name, "High")
        self.assertEqual(scores[0].rank, 1)
        # Low priority should be rank 2
        self.assertEqual(scores[1].lease.tenant_name, "Low")
        self.assertEqual(scores[1].rank, 2)


class TestExpirySchedule(unittest.TestCase):
    """Test expiry schedule aggregation"""

    def setUp(self):
        self.analysis_date = date(2025, 11, 6)

    def test_single_year_aggregation(self):
        """Leases in same year should aggregate correctly"""
        lease1 = Lease(
            property_address="Property 1",
            tenant_name="Tenant 1",
            rentable_area_sf=50000,
            current_annual_rent=500000,
            lease_expiry_date=date(2026, 3, 31),
            renewal_options=[],
            tenant_credit_rating="BBB",
            below_market_pct=0.0
        )

        lease2 = Lease(
            property_address="Property 2",
            tenant_name="Tenant 2",
            rentable_area_sf=30000,
            current_annual_rent=300000,
            lease_expiry_date=date(2026, 9, 30),
            renewal_options=[],
            tenant_credit_rating="A",
            below_market_pct=0.0
        )

        portfolio = PortfolioInput(
            portfolio_name="Test",
            analysis_date=self.analysis_date,
            leases=[lease1, lease2],
            assumptions=Assumptions()
        )

        schedule = calculate_expiry_schedule(portfolio)

        self.assertEqual(len(schedule), 1)
        self.assertEqual(schedule[0].year, 2026)
        self.assertEqual(schedule[0].lease_count, 2)
        self.assertEqual(schedule[0].total_sf, 80000)
        self.assertEqual(schedule[0].total_annual_rent, 800000)

    def test_multi_year_aggregation(self):
        """Leases across multiple years should create separate entries"""
        leases = [
            Lease("P1", "T1", 50000, 500000, date(2026, 12, 31), [], "BBB", 0.0),
            Lease("P2", "T2", 30000, 300000, date(2027, 12, 31), [], "A", 0.0),
            Lease("P3", "T3", 20000, 200000, date(2028, 12, 31), [], "AA", 0.0)
        ]

        portfolio = PortfolioInput(
            portfolio_name="Test",
            analysis_date=self.analysis_date,
            leases=leases,
            assumptions=Assumptions()
        )

        schedule = calculate_expiry_schedule(portfolio)

        self.assertEqual(len(schedule), 3)
        self.assertEqual([s.year for s in schedule], [2026, 2027, 2028])

    def test_risk_level_critical(self):
        """Year with >30% should be CRITICAL"""
        # 2 leases: one large (70%), one small (30%)
        lease1 = Lease("P1", "T1", 70000, 700000, date(2026, 12, 31), [], "BBB", 0.0)
        lease2 = Lease("P2", "T2", 30000, 300000, date(2027, 12, 31), [], "A", 0.0)

        portfolio = PortfolioInput(
            portfolio_name="Test",
            analysis_date=self.analysis_date,
            leases=[lease1, lease2],
            assumptions=Assumptions()
        )

        schedule = calculate_expiry_schedule(portfolio)

        # 2026 has 70% SF = CRITICAL
        year_2026 = [s for s in schedule if s.year == 2026][0]
        self.assertEqual(year_2026.risk_level, "CRITICAL")
        self.assertGreater(year_2026.pct_of_portfolio_sf, 30)

    def test_risk_level_high(self):
        """Year with 20-30% should be HIGH"""
        # 4 leases of 25% each
        leases = [
            Lease("P1", "T1", 25000, 250000, date(2026, 12, 31), [], "BBB", 0.0),
            Lease("P2", "T2", 25000, 250000, date(2027, 12, 31), [], "A", 0.0),
            Lease("P3", "T3", 25000, 250000, date(2028, 12, 31), [], "AA", 0.0),
            Lease("P4", "T4", 25000, 250000, date(2029, 12, 31), [], "A", 0.0)
        ]

        portfolio = PortfolioInput(
            portfolio_name="Test",
            analysis_date=self.analysis_date,
            leases=leases,
            assumptions=Assumptions()
        )

        schedule = calculate_expiry_schedule(portfolio)

        # Each year has 25% = HIGH
        for item in schedule:
            self.assertEqual(item.risk_level, "HIGH")
            self.assertGreater(item.pct_of_portfolio_sf, 20)
            self.assertLess(item.pct_of_portfolio_sf, 30)

    def test_risk_level_moderate(self):
        """Year with <20% should be MODERATE"""
        # 10 leases of 10% each
        leases = [
            Lease(f"P{i}", f"T{i}", 10000, 100000, date(2026 + i, 12, 31), [], "BBB", 0.0)
            for i in range(10)
        ]

        portfolio = PortfolioInput(
            portfolio_name="Test",
            analysis_date=self.analysis_date,
            leases=leases,
            assumptions=Assumptions()
        )

        schedule = calculate_expiry_schedule(portfolio)

        # Each year has 10% = MODERATE
        for item in schedule:
            self.assertEqual(item.risk_level, "MODERATE")
            self.assertLess(item.pct_of_portfolio_sf, 20)

    def test_cumulative_percentages(self):
        """Cumulative percentages should sum to 100%"""
        leases = [
            Lease("P1", "T1", 30000, 300000, date(2026, 12, 31), [], "BBB", 0.0),
            Lease("P2", "T2", 40000, 400000, date(2027, 12, 31), [], "A", 0.0),
            Lease("P3", "T3", 30000, 300000, date(2028, 12, 31), [], "AA", 0.0)
        ]

        portfolio = PortfolioInput(
            portfolio_name="Test",
            analysis_date=self.analysis_date,
            leases=leases,
            assumptions=Assumptions()
        )

        schedule = calculate_expiry_schedule(portfolio)

        # Last year should have 100% cumulative
        self.assertAlmostEqual(schedule[-1].cumulative_pct_sf, 100.0, places=1)
        self.assertAlmostEqual(schedule[-1].cumulative_pct_rent, 100.0, places=1)


class TestScenarioModeling(unittest.TestCase):
    """Test scenario modeling with NPV"""

    def setUp(self):
        self.analysis_date = date(2025, 11, 6)
        self.lease = Lease(
            property_address="Test Property",
            tenant_name="Test Tenant",
            rentable_area_sf=100000,
            current_annual_rent=1000000,
            lease_expiry_date=date(2026, 12, 31),
            renewal_options=[],
            tenant_credit_rating="BBB",
            below_market_pct=0.0
        )

    def test_three_scenarios_generated(self):
        """Should generate optimistic, base, and pessimistic scenarios"""
        portfolio = PortfolioInput(
            portfolio_name="Test",
            analysis_date=self.analysis_date,
            leases=[self.lease],
            assumptions=Assumptions()
        )

        schedule = calculate_expiry_schedule(portfolio)
        scenarios = calculate_scenario_analysis(portfolio, schedule)

        self.assertEqual(len(scenarios), 3)
        names = [s.scenario_name for s in scenarios]
        self.assertIn("Optimistic", names)
        self.assertIn("Base", names)
        self.assertIn("Pessimistic", names)

    def test_scenario_specific_downtime(self):
        """Scenarios should use different downtime months"""
        portfolio = PortfolioInput(
            portfolio_name="Test",
            analysis_date=self.analysis_date,
            leases=[self.lease],
            assumptions=Assumptions()
        )

        schedule = calculate_expiry_schedule(portfolio)
        scenarios = calculate_scenario_analysis(portfolio, schedule)

        optimistic = [s for s in scenarios if s.scenario_name == "Optimistic"][0]
        base = [s for s in scenarios if s.scenario_name == "Base"][0]
        pessimistic = [s for s in scenarios if s.scenario_name == "Pessimistic"][0]

        self.assertEqual(optimistic.downtime_months, 1)
        self.assertEqual(base.downtime_months, 3)
        self.assertEqual(pessimistic.downtime_months, 6)

        total_sf = sum(lease.rentable_area_sf for lease in portfolio.leases)
        total_rent = sum(lease.current_annual_rent for lease in portfolio.leases)

        # FIXED: Expected vacancy SF reflects churn rate (1 - renewal_rate), not total portfolio
        # Optimistic: 80% renewal → 20% churn
        self.assertAlmostEqual(optimistic.expected_vacancy_sf, total_sf * 0.20, places=1)
        # Base: 65% renewal → 35% churn
        self.assertAlmostEqual(base.expected_vacancy_sf, total_sf * 0.35, places=1)
        # Pessimistic: 50% renewal → 50% churn
        self.assertAlmostEqual(pessimistic.expected_vacancy_sf, total_sf * 0.50, places=1)

        # Expected vacancy rent uses weighted downtime (churn * full downtime + renewal * renewal downtime)
        # With renewal_downtime_months = 0 (default), only churning tenants contribute to vacancy rent
        self.assertAlmostEqual(
            optimistic.expected_vacancy_rent,
            total_rent * 0.20 * (optimistic.downtime_months / 12.0),  # 20% churn with 1 month downtime
            places=2
        )
        self.assertAlmostEqual(
            base.expected_vacancy_rent,
            total_rent * 0.35 * (base.downtime_months / 12.0),  # 35% churn with 3 months downtime
            places=2
        )
        self.assertAlmostEqual(
            pessimistic.expected_vacancy_rent,
            total_rent * 0.50 * (pessimistic.downtime_months / 12.0),  # 50% churn with 6 months downtime
            places=2
        )

    def test_scenario_specific_renewal_rates(self):
        """Scenarios should use different renewal rates"""
        portfolio = PortfolioInput(
            portfolio_name="Test",
            analysis_date=self.analysis_date,
            leases=[self.lease],
            assumptions=Assumptions()
        )

        schedule = calculate_expiry_schedule(portfolio)
        scenarios = calculate_scenario_analysis(portfolio, schedule)

        optimistic = [s for s in scenarios if s.scenario_name == "Optimistic"][0]
        base = [s for s in scenarios if s.scenario_name == "Base"][0]
        pessimistic = [s for s in scenarios if s.scenario_name == "Pessimistic"][0]

        self.assertEqual(optimistic.renewal_rate, 0.80)
        self.assertEqual(base.renewal_rate, 0.65)
        self.assertEqual(pessimistic.renewal_rate, 0.50)

    def test_noi_impact_is_negative(self):
        """NOI impact should be negative (lost rent)"""
        portfolio = PortfolioInput(
            portfolio_name="Test",
            analysis_date=self.analysis_date,
            leases=[self.lease],
            assumptions=Assumptions()
        )

        schedule = calculate_expiry_schedule(portfolio)
        scenarios = calculate_scenario_analysis(portfolio, schedule)

        # All scenarios should have negative NOI impact
        for scenario in scenarios:
            self.assertLess(scenario.noi_impact_npv, 0)

    def test_pessimistic_worse_than_optimistic(self):
        """Pessimistic should have larger negative impact than optimistic"""
        portfolio = PortfolioInput(
            portfolio_name="Test",
            analysis_date=self.analysis_date,
            leases=[self.lease],
            assumptions=Assumptions()
        )

        schedule = calculate_expiry_schedule(portfolio)
        scenarios = calculate_scenario_analysis(portfolio, schedule)

        optimistic = [s for s in scenarios if s.scenario_name == "Optimistic"][0]
        pessimistic = [s for s in scenarios if s.scenario_name == "Pessimistic"][0]

        # Pessimistic should be more negative (worse)
        self.assertLess(pessimistic.noi_impact_npv, optimistic.noi_impact_npv)

    def test_multi_lease_renewal_counts(self):
        """Multi-lease portfolios should floor renewal counts per scenario"""
        leases = [
            Lease(
                property_address=f"Property {i}",
                tenant_name=f"Tenant {i}",
                rentable_area_sf=50000,
                current_annual_rent=250000,
                lease_expiry_date=date(2026 + i, 12, 31),
                renewal_options=[],
                tenant_credit_rating="BBB",
                below_market_pct=0.0
            )
            for i in range(3)
        ]

        portfolio = PortfolioInput(
            portfolio_name="Multi Lease",
            analysis_date=self.analysis_date,
            leases=leases,
            assumptions=Assumptions()
        )

        schedule = calculate_expiry_schedule(portfolio)
        scenarios = calculate_scenario_analysis(portfolio, schedule)

        optimistic = [s for s in scenarios if s.scenario_name == "Optimistic"][0]
        base = [s for s in scenarios if s.scenario_name == "Base"][0]
        pessimistic = [s for s in scenarios if s.scenario_name == "Pessimistic"][0]

        # int(3 × 0.80) = 2 renewals, remaining lease rolls to new tenant
        self.assertEqual(optimistic.leases_renewed, 2)
        self.assertEqual(optimistic.leases_new_tenant, 1)

        # int(3 × 0.65) = 1 renewal, 2 new tenants
        self.assertEqual(base.leases_renewed, 1)
        self.assertEqual(base.leases_new_tenant, 2)

        # int(3 × 0.50) = 1 renewal after flooring, 2 new tenants
        self.assertEqual(pessimistic.leases_renewed, 1)
        self.assertEqual(pessimistic.leases_new_tenant, 2)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""

    def test_empty_portfolio_raises_error(self):
        """Empty portfolio should raise ValueError"""
        portfolio = PortfolioInput(
            portfolio_name="Empty",
            analysis_date=date(2025, 11, 6),
            leases=[],
            assumptions=Assumptions()
        )

        with self.assertRaises(ValueError):
            calculate_rollover_analysis(portfolio)

    def test_single_lease_portfolio(self):
        """Single lease portfolio should work correctly"""
        lease = Lease(
            property_address="Only Property",
            tenant_name="Only Tenant",
            rentable_area_sf=100000,
            current_annual_rent=1000000,
            lease_expiry_date=date(2026, 12, 31),
            renewal_options=[],
            tenant_credit_rating="BBB",
            below_market_pct=0.0
        )

        portfolio = PortfolioInput(
            portfolio_name="Single",
            analysis_date=date(2025, 11, 6),
            leases=[lease],
            assumptions=Assumptions()
        )

        results = calculate_rollover_analysis(portfolio)

        self.assertEqual(len(results.priority_ranking), 1)
        self.assertEqual(results.priority_ranking[0].rank, 1)
        self.assertEqual(len(results.expiry_schedule), 1)

    def test_all_same_year_expiry(self):
        """All leases expiring in same year should aggregate correctly"""
        leases = [
            Lease(f"P{i}", f"T{i}", 10000, 100000, date(2026, 12, 31), [], "BBB", 0.0)
            for i in range(5)
        ]

        portfolio = PortfolioInput(
            portfolio_name="Same Year",
            analysis_date=date(2025, 11, 6),
            leases=leases,
            assumptions=Assumptions()
        )

        results = calculate_rollover_analysis(portfolio)

        self.assertEqual(len(results.expiry_schedule), 1)
        self.assertEqual(results.expiry_schedule[0].year, 2026)
        self.assertEqual(results.expiry_schedule[0].lease_count, 5)
        self.assertEqual(results.expiry_schedule[0].pct_of_portfolio_sf, 100.0)

    def test_invalid_rentable_area_raises_error(self):
        """Negative or zero area should raise ValueError"""
        with self.assertRaises(ValueError):
            Lease(
                property_address="Bad",
                tenant_name="Bad",
                rentable_area_sf=-1000,  # Negative
                current_annual_rent=100000,
                lease_expiry_date=date(2026, 12, 31),
                renewal_options=[],
                tenant_credit_rating="BBB",
                below_market_pct=0.0
            )

    def test_invalid_rent_raises_error(self):
        """Negative rent should raise ValueError"""
        with self.assertRaises(ValueError):
            Lease(
                property_address="Bad",
                tenant_name="Bad",
                rentable_area_sf=10000,
                current_annual_rent=-100000,  # Negative
                lease_expiry_date=date(2026, 12, 31),
                renewal_options=[],
                tenant_credit_rating="BBB",
                below_market_pct=0.0
            )

    def test_missing_credit_rating_defaults_to_nr(self):
        """Missing credit rating should default to NR"""
        lease = Lease(
            property_address="Test",
            tenant_name="Test",
            rentable_area_sf=10000,
            current_annual_rent=100000,
            lease_expiry_date=date(2026, 12, 31),
            renewal_options=[],
            tenant_credit_rating="",  # Empty
            below_market_pct=0.0
        )

        self.assertEqual(lease.tenant_credit_rating, "NR")

    def test_zero_percent_renewal_rate(self):
        """0% renewal rate should result in all leases going to new tenants"""
        lease = Lease(
            property_address="Test",
            tenant_name="Test",
            rentable_area_sf=100000,
            current_annual_rent=1000000,
            lease_expiry_date=date(2026, 12, 31),
            renewal_options=[],
            tenant_credit_rating="BBB",
            below_market_pct=0.0
        )

        assumptions = Assumptions()
        assumptions.renewal_rate_base = 0.0  # 0% renewals

        portfolio = PortfolioInput(
            portfolio_name="Zero Renewal",
            analysis_date=date(2025, 11, 6),
            leases=[lease],
            assumptions=assumptions
        )

        schedule = calculate_expiry_schedule(portfolio)
        scenarios = calculate_scenario_analysis(portfolio, schedule)

        base = [s for s in scenarios if s.scenario_name == "Base"][0]
        self.assertEqual(base.leases_renewed, 0)
        self.assertEqual(base.leases_new_tenant, 1)

    def test_100_percent_renewal_rate(self):
        """100% renewal rate should result in all leases renewing"""
        lease = Lease(
            property_address="Test",
            tenant_name="Test",
            rentable_area_sf=100000,
            current_annual_rent=1000000,
            lease_expiry_date=date(2026, 12, 31),
            renewal_options=[],
            tenant_credit_rating="BBB",
            below_market_pct=0.0
        )

        assumptions = Assumptions()
        assumptions.renewal_rate_base = 1.0  # 100% renewals

        portfolio = PortfolioInput(
            portfolio_name="Full Renewal",
            analysis_date=date(2025, 11, 6),
            leases=[lease],
            assumptions=assumptions
        )

        schedule = calculate_expiry_schedule(portfolio)
        scenarios = calculate_scenario_analysis(portfolio, schedule)

        base = [s for s in scenarios if s.scenario_name == "Base"][0]
        self.assertEqual(base.leases_renewed, 1)
        self.assertEqual(base.leases_new_tenant, 0)


class TestIntegration(unittest.TestCase):
    """Integration tests using realistic portfolios"""

    def test_full_analysis_workflow(self):
        """Complete end-to-end analysis should produce valid results"""
        # Create realistic 5-lease portfolio
        leases = [
            Lease("123 Main", "Acme", 50000, 500000, date(2026, 6, 30), [], "BBB", -10.0),
            Lease("456 Oak", "Beta", 75000, 750000, date(2027, 3, 31), [], "A", 5.0),
            Lease("789 Elm", "Gamma", 60000, 600000, date(2026, 12, 31), [], "BB", -15.0),
            Lease("321 Pine", "Delta", 40000, 400000, date(2028, 9, 30), [], "A-", 0.0),
            Lease("555 Maple", "Epsilon", 80000, 800000, date(2027, 6, 30), [], "BBB+", -8.0)
        ]

        portfolio = PortfolioInput(
            portfolio_name="Integration Test",
            analysis_date=date(2025, 11, 6),
            leases=leases,
            assumptions=Assumptions()
        )

        results = calculate_rollover_analysis(portfolio)

        # Validate results structure
        self.assertIsNotNone(results)
        self.assertEqual(results.portfolio_name, "Integration Test")
        self.assertEqual(len(results.priority_ranking), 5)
        self.assertGreater(len(results.expiry_schedule), 0)
        self.assertEqual(len(results.scenarios), 3)

        # Validate priority ranking is sorted
        for i in range(len(results.priority_ranking) - 1):
            self.assertGreaterEqual(
                results.priority_ranking[i].priority_score,
                results.priority_ranking[i+1].priority_score
            )

        # Validate ranks are sequential
        for i, score in enumerate(results.priority_ranking, start=1):
            self.assertEqual(score.rank, i)


def run_tests():
    """Run all tests and print results"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCreditRatingMapping))
    suite.addTests(loader.loadTestsFromTestCase(TestPriorityScoring))
    suite.addTests(loader.loadTestsFromTestCase(TestExpirySchedule))
    suite.addTests(loader.loadTestsFromTestCase(TestScenarioModeling))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
