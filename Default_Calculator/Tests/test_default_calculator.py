#!/usr/bin/env python3
"""
Comprehensive Test Suite for Default Damage Calculator

Tests all calculation functions, edge cases, and integration scenarios.

Author: Claude Code
Version: 1.0.0
Date: 2025-11-06
"""

import unittest
import sys
from datetime import date, timedelta
from pathlib import Path

# Add parent directory to path to import calculator
sys.path.insert(0, str(Path(__file__).parent.parent))

from default_calculator import (
    LeaseTerms,
    DefaultEvent,
    DamageCalculation,
    BankruptcyScenario,
    DefaultAnalysisResults,
    calculate_accelerated_rent_npv,
    calculate_re_leasing_costs,
    calculate_mitigation_credit,
    calculate_bankruptcy_claims,
    calculate_default_damages
)


# ============================================================================
# TEST DATA FIXTURES
# ============================================================================

def create_sample_lease(
    monthly_rent: float = 25000.0,
    remaining_months: int = 36,
    market_rent_sf: float = 7.0
) -> LeaseTerms:
    """Create sample lease terms for testing"""
    return LeaseTerms(
        property_address="123 Test St, City, ON",
        tenant_name="Test Tenant Inc.",
        landlord_name="Test Landlord Corp.",
        current_monthly_rent=monthly_rent,
        current_annual_rent=monthly_rent * 12,
        rentable_area_sf=50000,
        rent_per_sf=monthly_rent * 12 / 50000,
        lease_commencement_date=date(2023, 1, 1),
        lease_expiry_date=date(2028, 12, 31),
        remaining_months=remaining_months,
        additional_rent_annual=75000.0,
        security_deposit=50000.0,
        monetary_default_cure_days=5,
        non_monetary_default_cure_days=15,
        market_rent_sf=market_rent_sf,
        ti_allowance_sf=15.0,
        leasing_commission_pct=0.05,
        legal_fees=5000.0,
        downtime_months=6,
        discount_rate_annual=0.10
    )


def create_monetary_default(amount: float = 25000.0) -> DefaultEvent:
    """Create sample monetary default for testing"""
    return DefaultEvent(
        default_date=date.today(),
        default_type="monetary",
        description="Failure to pay rent",
        amount_owing=amount,
        cure_period_days=5,
        cure_deadline=date.today() + timedelta(days=5)
    )


def create_non_monetary_default() -> DefaultEvent:
    """Create sample non-monetary default for testing"""
    return DefaultEvent(
        default_date=date.today(),
        default_type="non-monetary",
        description="Unauthorized alterations to premises",
        amount_owing=0.0,
        cure_period_days=15,
        cure_deadline=date.today() + timedelta(days=15)
    )


# ============================================================================
# UNIT TESTS: ACCELERATED RENT NPV
# ============================================================================

class TestAcceleratedRentNPV(unittest.TestCase):
    """Test NPV calculation for accelerated rent claims"""

    def test_zero_remaining_months(self):
        """Zero remaining months should return 0"""
        npv = calculate_accelerated_rent_npv(
            monthly_rent=25000,
            additional_rent_monthly=6250,
            remaining_months=0,
            discount_rate_annual=0.10
        )
        self.assertEqual(npv, 0.0)

    def test_one_month_remaining(self):
        """One month remaining should be approximately one month's rent"""
        monthly_rent = 25000
        additional_rent = 6250
        total_monthly = monthly_rent + additional_rent

        npv = calculate_accelerated_rent_npv(
            monthly_rent=monthly_rent,
            additional_rent_monthly=additional_rent,
            remaining_months=1,
            discount_rate_annual=0.10
        )

        # Should be slightly less than total due to discounting
        self.assertLess(npv, total_monthly)
        self.assertGreater(npv, total_monthly * 0.99)  # Within 1%

    def test_twelve_months_remaining(self):
        """12 months should discount to less than 12x monthly rent"""
        monthly_rent = 25000
        additional_rent = 6250
        total_monthly = monthly_rent + additional_rent
        total_undiscounted = total_monthly * 12

        npv = calculate_accelerated_rent_npv(
            monthly_rent=monthly_rent,
            additional_rent_monthly=additional_rent,
            remaining_months=12,
            discount_rate_annual=0.10
        )

        # NPV should be less than undiscounted total
        self.assertLess(npv, total_undiscounted)
        # Should be at least 90% of undiscounted (rough check)
        self.assertGreater(npv, total_undiscounted * 0.90)

    def test_zero_discount_rate(self):
        """Zero discount rate should equal undiscounted total"""
        monthly_rent = 25000
        additional_rent = 6250
        total_monthly = monthly_rent + additional_rent
        months = 12

        npv = calculate_accelerated_rent_npv(
            monthly_rent=monthly_rent,
            additional_rent_monthly=additional_rent,
            remaining_months=months,
            discount_rate_annual=0.0
        )

        expected = total_monthly * months
        self.assertAlmostEqual(npv, expected, places=2)

    def test_longer_term_greater_discount(self):
        """Longer term should have proportionally greater discount effect"""
        monthly_rent = 25000
        additional_rent = 6250

        npv_12m = calculate_accelerated_rent_npv(
            monthly_rent, additional_rent, 12, 0.10
        )
        npv_36m = calculate_accelerated_rent_npv(
            monthly_rent, additional_rent, 36, 0.10
        )

        # 36-month NPV should be less than 3x the 12-month NPV due to discounting
        self.assertLess(npv_36m, npv_12m * 3.0)


# ============================================================================
# UNIT TESTS: RE-LEASING COSTS
# ============================================================================

class TestReLeasingCosts(unittest.TestCase):
    """Test re-leasing cost calculations"""

    def test_basic_calculation(self):
        """Basic re-leasing cost should include TI, commissions, legal"""
        costs = calculate_re_leasing_costs(
            rentable_area_sf=50000,
            ti_allowance_sf=15.0,
            market_rent_annual=350000,
            lease_term_years=5,
            leasing_commission_pct=0.05,
            legal_fees=5000
        )

        # TI = 50000 × 15 = 750,000
        self.assertEqual(costs["ti_costs"], 750000)

        # Commissions = 350000 × 5 × 0.05 = 87,500
        self.assertEqual(costs["commissions"], 87500)

        # Legal = 5000
        self.assertEqual(costs["legal_fees"], 5000)

        # Total
        self.assertEqual(costs["total"], 750000 + 87500 + 5000)

    def test_zero_ti_allowance(self):
        """Zero TI allowance should only include commissions and legal"""
        costs = calculate_re_leasing_costs(
            rentable_area_sf=50000,
            ti_allowance_sf=0.0,
            market_rent_annual=350000,
            lease_term_years=5,
            leasing_commission_pct=0.05,
            legal_fees=5000
        )

        self.assertEqual(costs["ti_costs"], 0.0)
        self.assertGreater(costs["commissions"], 0)
        self.assertEqual(costs["total"], costs["commissions"] + costs["legal_fees"])

    def test_commission_rate_impact(self):
        """Higher commission rate should increase total costs"""
        costs_5pct = calculate_re_leasing_costs(
            50000, 15.0, 350000, 5, 0.05, 5000
        )
        costs_10pct = calculate_re_leasing_costs(
            50000, 15.0, 350000, 5, 0.10, 5000
        )

        self.assertGreater(costs_10pct["commissions"], costs_5pct["commissions"])
        self.assertGreater(costs_10pct["total"], costs_5pct["total"])


# ============================================================================
# UNIT TESTS: MITIGATION CREDIT
# ============================================================================

class TestMitigationCredit(unittest.TestCase):
    """Test mitigation credit calculations"""

    def test_downtime_exceeds_remaining(self):
        """No mitigation if downtime exceeds remaining term"""
        credit = calculate_mitigation_credit(
            market_rent_monthly=30000,
            remaining_months=6,
            downtime_months=12,
            discount_rate_annual=0.10
        )
        self.assertEqual(credit, 0.0)

    def test_downtime_equals_remaining(self):
        """No mitigation if downtime equals remaining term"""
        credit = calculate_mitigation_credit(
            market_rent_monthly=30000,
            remaining_months=6,
            downtime_months=6,
            discount_rate_annual=0.10
        )
        self.assertEqual(credit, 0.0)

    def test_immediate_re_lease(self):
        """Immediate re-lease (0 downtime) should maximize credit"""
        market_rent = 30000
        remaining = 12

        credit = calculate_mitigation_credit(
            market_rent_monthly=market_rent,
            remaining_months=remaining,
            downtime_months=0,
            discount_rate_annual=0.10
        )

        # Should be close to market_rent × remaining (slightly less due to discount)
        undiscounted = market_rent * remaining
        self.assertLess(credit, undiscounted)
        self.assertGreater(credit, undiscounted * 0.90)

    def test_higher_market_rent_greater_credit(self):
        """Higher market rent should increase mitigation credit"""
        credit_low = calculate_mitigation_credit(
            market_rent_monthly=25000,
            remaining_months=12,
            downtime_months=3,
            discount_rate_annual=0.10
        )
        credit_high = calculate_mitigation_credit(
            market_rent_monthly=35000,
            remaining_months=12,
            downtime_months=3,
            discount_rate_annual=0.10
        )

        self.assertGreater(credit_high, credit_low)


# ============================================================================
# UNIT TESTS: BANKRUPTCY CLAIMS
# ============================================================================

class TestBankruptcyClaims(unittest.TestCase):
    """Test bankruptcy scenario calculations"""

    def test_priority_claim_calculation(self):
        """Priority claim should be 60 days (2 months) rent"""
        monthly_rent = 25000
        additional_rent = 6250
        total_monthly = monthly_rent + additional_rent

        scenario = calculate_bankruptcy_claims(
            monthly_rent=monthly_rent,
            additional_rent_monthly=additional_rent,
            remaining_months=36,
            gross_damages=1000000
        )

        expected_priority = total_monthly * 2
        self.assertEqual(scenario.priority_claim_60_days, expected_priority)

    def test_statutory_cap_one_year(self):
        """Statutory cap should be greater of 1 year or 15% of remaining"""
        monthly_rent = 25000
        additional_rent = 6250
        total_monthly = monthly_rent + additional_rent

        # 12 months remaining: 15% = 1.8 months < 12 months
        scenario = calculate_bankruptcy_claims(
            monthly_rent=monthly_rent,
            additional_rent_monthly=additional_rent,
            remaining_months=12,
            gross_damages=500000
        )

        one_year_rent = total_monthly * 12
        # Unsecured claim should be capped at 1 year rent minus priority
        self.assertLessEqual(
            scenario.unsecured_claim,
            one_year_rent
        )

    def test_expected_recovery_calculation(self):
        """Expected recovery should weight claims by recovery rates"""
        scenario = calculate_bankruptcy_claims(
            monthly_rent=25000,
            additional_rent_monthly=6250,
            remaining_months=36,
            gross_damages=1000000
        )

        # Priority at 100% + unsecured at 20%
        expected = (
            scenario.priority_claim_60_days * 1.0 +
            scenario.unsecured_claim * 0.20
        )

        self.assertAlmostEqual(scenario.expected_recovery, expected, places=2)

    def test_expected_loss_equals_shortfall(self):
        """Expected loss should equal gross damages minus expected recovery"""
        gross_damages = 1000000

        scenario = calculate_bankruptcy_claims(
            monthly_rent=25000,
            additional_rent_monthly=6250,
            remaining_months=36,
            gross_damages=gross_damages
        )

        expected_loss = gross_damages - scenario.expected_recovery
        self.assertAlmostEqual(scenario.expected_loss, expected_loss, places=2)

    def test_unsecured_claim_floors_at_zero(self):
        """Unsecured claim should never be negative when priority exceeds damages"""
        scenario = calculate_bankruptcy_claims(
            monthly_rent=1000,
            additional_rent_monthly=0,
            remaining_months=12,
            gross_damages=1500  # Less than 60-day priority claim
        )

        self.assertEqual(scenario.priority_claim_60_days, 2000)
        self.assertEqual(scenario.unsecured_claim, 0.0)


# ============================================================================
# INTEGRATION TESTS: FULL DAMAGE CALCULATION
# ============================================================================

class TestFullDamageCalculation(unittest.TestCase):
    """Test complete end-to-end damage calculations"""

    def test_monetary_default_calculation(self):
        """Monetary default should calculate all damages correctly"""
        lease = create_sample_lease()
        default = create_monetary_default(amount=25000)

        results = calculate_default_damages(lease, default)

        # Should have unpaid rent
        self.assertEqual(results.damage_calculation.unpaid_rent, 25000)

        # Should have accelerated rent NPV
        self.assertGreater(results.damage_calculation.accelerated_rent_npv, 0)

        # Should have re-leasing costs
        self.assertGreater(results.damage_calculation.ti_costs, 0)
        self.assertGreater(results.damage_calculation.leasing_commissions, 0)
        self.assertGreater(results.damage_calculation.legal_fees, 0)

        # Should have lost rent
        self.assertGreater(results.damage_calculation.lost_rent_downtime, 0)

        # Should have credits
        self.assertEqual(results.damage_calculation.security_deposit_credit, 50000)
        self.assertGreater(results.damage_calculation.re_lease_rent_credit_npv, 0)

        # Net damages should be gross minus credits
        self.assertEqual(
            results.damage_calculation.net_damages,
            results.damage_calculation.gross_damages - results.damage_calculation.total_credits
        )

    def test_non_monetary_default_calculation(self):
        """Non-monetary default should not include unpaid rent"""
        lease = create_sample_lease()
        default = create_non_monetary_default()

        results = calculate_default_damages(lease, default)

        # Should NOT have unpaid rent
        self.assertEqual(results.damage_calculation.unpaid_rent, 0.0)

        # Should still have other damages
        self.assertGreater(results.damage_calculation.accelerated_rent_npv, 0)
        self.assertGreater(results.damage_calculation.gross_damages, 0)

    def test_short_remaining_term(self):
        """Short remaining term should reduce accelerated rent"""
        lease = create_sample_lease(remaining_months=3)
        default = create_monetary_default()

        results = calculate_default_damages(lease, default)

        # Accelerated rent should be relatively small
        self.assertLess(results.damage_calculation.accelerated_rent_npv, 100000)

    def test_zero_remaining_term(self):
        """Zero remaining term still carries downtime and re-leasing costs"""
        lease = create_sample_lease(remaining_months=0)
        default = create_monetary_default()

        results = calculate_default_damages(lease, default)

        # Should have no accelerated rent
        self.assertEqual(results.damage_calculation.accelerated_rent_npv, 0.0)

        # Should have no mitigation credit
        self.assertEqual(results.damage_calculation.re_lease_rent_credit_npv, 0.0)

        # Re-leasing costs and downtime remain applicable despite zero term
        self.assertGreater(results.damage_calculation.ti_costs, 0.0)
        self.assertGreater(results.damage_calculation.lost_rent_downtime, 0.0)
        self.assertGreater(results.damage_calculation.net_damages, 0.0)

    def test_higher_market_rent_increases_mitigation(self):
        """Higher market rent should increase mitigation credit"""
        lease_low = create_sample_lease(market_rent_sf=6.0)  # Below current
        lease_high = create_sample_lease(market_rent_sf=8.0)  # Above current
        default = create_monetary_default()

        results_low = calculate_default_damages(lease_low, default)
        results_high = calculate_default_damages(lease_high, default)

        # Higher market rent should have higher mitigation credit
        self.assertGreater(
            results_high.damage_calculation.re_lease_rent_credit_npv,
            results_low.damage_calculation.re_lease_rent_credit_npv
        )

        # Therefore net damages should be lower
        self.assertLess(
            results_high.damage_calculation.net_damages,
            results_low.damage_calculation.net_damages
        )

    def test_bankruptcy_scenario_included(self):
        """Results should include bankruptcy scenario"""
        lease = create_sample_lease()
        default = create_monetary_default()

        results = calculate_default_damages(lease, default)

        # Should have at least one bankruptcy scenario
        self.assertGreater(len(results.bankruptcy_scenarios), 0)

        # Scenario should have valid claims
        bk = results.bankruptcy_scenarios[0]
        self.assertGreater(bk.priority_claim_60_days, 0)
        self.assertGreater(bk.unsecured_claim, 0)
        self.assertGreater(bk.expected_recovery, 0)
        self.assertGreater(bk.expected_loss, 0)


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""

    def test_invalid_monthly_rent(self):
        """Negative monthly rent should raise ValueError"""
        with self.assertRaises(ValueError):
            LeaseTerms(
                property_address="Test",
                tenant_name="Test",
                landlord_name="Test",
                current_monthly_rent=-1000,
                current_annual_rent=12000,
                rentable_area_sf=10000,
                rent_per_sf=1.0,
                lease_commencement_date=date(2023, 1, 1),
                lease_expiry_date=date(2028, 1, 1),
                remaining_months=60
            )

    def test_invalid_rentable_area(self):
        """Zero rentable area should raise ValueError"""
        with self.assertRaises(ValueError):
            LeaseTerms(
                property_address="Test",
                tenant_name="Test",
                landlord_name="Test",
                current_monthly_rent=1000,
                current_annual_rent=12000,
                rentable_area_sf=0,
                rent_per_sf=1.0,
                lease_commencement_date=date(2023, 1, 1),
                lease_expiry_date=date(2028, 1, 1),
                remaining_months=60
            )

    def test_invalid_discount_rate(self):
        """Discount rate >1 should raise ValueError"""
        with self.assertRaises(ValueError):
            LeaseTerms(
                property_address="Test",
                tenant_name="Test",
                landlord_name="Test",
                current_monthly_rent=1000,
                current_annual_rent=12000,
                rentable_area_sf=10000,
                rent_per_sf=1.0,
                lease_commencement_date=date(2023, 1, 1),
                lease_expiry_date=date(2028, 1, 1),
                remaining_months=60,
                discount_rate_annual=1.5  # Invalid: >1
            )

    def test_invalid_default_type(self):
        """Invalid default type should raise ValueError"""
        with self.assertRaises(ValueError):
            DefaultEvent(
                default_date=date.today(),
                default_type="invalid_type",
                description="Test",
                amount_owing=0
            )

    def test_monetary_default_zero_amount(self):
        """Monetary default with zero amount should raise ValueError"""
        with self.assertRaises(ValueError):
            DefaultEvent(
                default_date=date.today(),
                default_type="monetary",
                description="Test",
                amount_owing=0.0  # Invalid for monetary default
            )

    def test_very_long_remaining_term(self):
        """Very long remaining term should still calculate correctly"""
        lease = create_sample_lease(remaining_months=240)  # 20 years
        default = create_monetary_default()

        results = calculate_default_damages(lease, default)

        # Should have large accelerated rent (but discounted)
        self.assertGreater(results.damage_calculation.accelerated_rent_npv, 0)

        # Should be less than undiscounted total
        undiscounted = (lease.current_monthly_rent + lease.additional_rent_annual / 12) * 240
        self.assertLess(results.damage_calculation.accelerated_rent_npv, undiscounted)

    def test_zero_security_deposit(self):
        """Zero security deposit should still calculate correctly"""
        lease = create_sample_lease()
        lease.security_deposit = 0.0
        default = create_monetary_default()

        results = calculate_default_damages(lease, default)

        # Should have no security deposit credit
        self.assertEqual(results.damage_calculation.security_deposit_credit, 0.0)

        # But should still have other credits
        self.assertGreater(results.damage_calculation.re_lease_rent_credit_npv, 0)


# ============================================================================
# DATA VALIDATION TESTS
# ============================================================================

class TestDataValidation(unittest.TestCase):
    """Test data validation and constraints"""

    def test_damage_calculation_totals(self):
        """DamageCalculation.calculate_totals() should compute correctly"""
        damages = DamageCalculation()
        damages.unpaid_rent = 25000
        damages.accelerated_rent_npv = 800000
        damages.lost_rent_downtime = 150000
        damages.ti_costs = 750000
        damages.leasing_commissions = 87500
        damages.legal_fees = 5000
        damages.security_deposit_credit = 50000
        damages.re_lease_rent_credit_npv = 300000

        damages.calculate_totals()

        expected_gross = 25000 + 800000 + 150000 + 750000 + 87500 + 5000
        expected_credits = 50000 + 300000
        expected_net = expected_gross - expected_credits

        self.assertEqual(damages.gross_damages, expected_gross)
        self.assertEqual(damages.total_credits, expected_credits)
        self.assertEqual(damages.net_damages, expected_net)

    def test_bankruptcy_scenario_recovery(self):
        """BankruptcyScenario.calculate_expected_recovery() should compute correctly"""
        scenario = BankruptcyScenario(
            scenario_name="Test",
            priority_claim_60_days=62500,
            unsecured_claim=375000,
            priority_recovery_rate=1.0,
            unsecured_recovery_rate=0.20,
            preference_period_days=90,
            payments_at_risk=93750
        )

        gross_damages = 1000000
        scenario.calculate_expected_recovery(gross_damages)

        expected_recovery = 62500 * 1.0 + 375000 * 0.20
        expected_loss = gross_damages - expected_recovery

        self.assertEqual(scenario.expected_recovery, expected_recovery)
        self.assertEqual(scenario.expected_loss, expected_loss)


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_tests():
    """Run all tests and print summary"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAcceleratedRentNPV))
    suite.addTests(loader.loadTestsFromTestCase(TestReLeasingCosts))
    suite.addTests(loader.loadTestsFromTestCase(TestMitigationCredit))
    suite.addTests(loader.loadTestsFromTestCase(TestBankruptcyClaims))
    suite.addTests(loader.loadTestsFromTestCase(TestFullDamageCalculation))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestDataValidation))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)} ({(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.0f}%)")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    return result


if __name__ == '__main__':
    result = run_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
