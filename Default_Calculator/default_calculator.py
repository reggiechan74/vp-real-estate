#!/usr/bin/env python3
"""
Default Damage Calculator - Quantifies Landlord Damages from Tenant Default

Calculates:
- Accelerated rent (NPV of remaining lease term)
- Re-leasing costs (TI, commissions, legal fees)
- Lost rent during downtime
- Mitigation credit from re-leasing
- Bankruptcy scenarios (trustee rejection, preference periods)

Author: Claude Code
Version: 1.0.0
Date: 2025-11-06
"""

import json
import sys
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from pathlib import Path


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class LeaseTerms:
    """
    Lease terms extracted from lease agreement

    All financial values in dollars unless otherwise noted
    """
    property_address: str
    tenant_name: str
    landlord_name: str

    # Rent schedule
    current_monthly_rent: float
    current_annual_rent: float
    rentable_area_sf: float
    rent_per_sf: float

    # Lease term
    lease_commencement_date: date
    lease_expiry_date: date
    remaining_months: int

    # Additional rent
    additional_rent_annual: float = 0.0  # Taxes, opex, CAM

    # Security deposit
    security_deposit: float = 0.0

    # Default provisions
    monetary_default_cure_days: int = 5
    non_monetary_default_cure_days: int = 15

    # Re-leasing assumptions
    market_rent_sf: float = 0.0  # Current market rent
    ti_allowance_sf: float = 15.0  # Tenant improvement allowance
    leasing_commission_pct: float = 0.05  # 5% of lease value
    legal_fees: float = 5000.0
    downtime_months: int = 6  # Expected vacancy period

    # Discount rate for NPV calculations
    discount_rate_annual: float = 0.10  # 10% default

    def __post_init__(self):
        """Validate lease terms"""
        if self.current_monthly_rent <= 0:
            raise ValueError(f"Invalid monthly rent: {self.current_monthly_rent}")
        if self.rentable_area_sf <= 0:
            raise ValueError(f"Invalid rentable area: {self.rentable_area_sf}")
        if self.remaining_months < 0:
            raise ValueError(f"Invalid remaining months: {self.remaining_months}")
        if not 0 <= self.discount_rate_annual <= 1:
            raise ValueError(f"Discount rate must be 0-1: {self.discount_rate_annual}")


@dataclass
class DefaultEvent:
    """
    Details of tenant default event
    """
    default_date: date
    default_type: str  # "monetary" or "non-monetary"
    description: str
    amount_owing: float = 0.0  # For monetary defaults
    cure_period_days: int = 0
    cure_deadline: Optional[date] = None

    def __post_init__(self):
        """Validate default event"""
        if self.default_type not in ["monetary", "non-monetary"]:
            raise ValueError(f"Invalid default type: {self.default_type}")
        if self.default_type == "monetary" and self.amount_owing <= 0:
            raise ValueError(f"Monetary default requires positive amount: {self.amount_owing}")


@dataclass
class DamageCalculation:
    """
    Calculated damages from tenant default

    All amounts are positive (costs to landlord)
    """
    # Immediate damages
    unpaid_rent: float = 0.0
    unpaid_additional_rent: float = 0.0
    late_fees: float = 0.0

    # Future damages (NPV)
    accelerated_rent_npv: float = 0.0
    lost_rent_downtime: float = 0.0

    # Re-leasing costs
    ti_costs: float = 0.0
    leasing_commissions: float = 0.0
    legal_fees: float = 0.0
    marketing_costs: float = 0.0

    # Mitigation credits (reduce damages)
    security_deposit_credit: float = 0.0
    re_lease_rent_credit_npv: float = 0.0  # PV of new lease rent

    # Net damages
    gross_damages: float = 0.0
    total_credits: float = 0.0
    net_damages: float = 0.0

    def calculate_totals(self):
        """Calculate gross, credits, and net damages"""
        self.gross_damages = (
            self.unpaid_rent +
            self.unpaid_additional_rent +
            self.late_fees +
            self.accelerated_rent_npv +
            self.lost_rent_downtime +
            self.ti_costs +
            self.leasing_commissions +
            self.legal_fees +
            self.marketing_costs
        )

        self.total_credits = (
            self.security_deposit_credit +
            self.re_lease_rent_credit_npv
        )

        self.net_damages = self.gross_damages - self.total_credits

        return self


@dataclass
class BankruptcyScenario:
    """
    Bankruptcy-specific damage calculations

    Models trustee rejection under bankruptcy law
    """
    scenario_name: str

    # Trustee rejection claims
    priority_claim_60_days: float = 0.0  # 60-day priority rent claim
    administrative_claim: float = 0.0  # Post-petition rent
    unsecured_claim: float = 0.0  # Balance of damages

    # Recovery estimates
    priority_recovery_rate: float = 1.0  # Usually 100%
    administrative_recovery_rate: float = 1.0  # Usually 100%
    unsecured_recovery_rate: float = 0.20  # Typically 10-30%

    expected_recovery: float = 0.0
    expected_loss: float = 0.0

    # Preference period considerations
    preference_period_days: int = 90
    payments_at_risk: float = 0.0  # Payments within 90 days

    def calculate_expected_recovery(self, gross_damages: float):
        """Calculate expected recovery in bankruptcy"""
        self.expected_recovery = (
            self.priority_claim_60_days * self.priority_recovery_rate +
            self.administrative_claim * self.administrative_recovery_rate +
            self.unsecured_claim * self.unsecured_recovery_rate
        )

        self.expected_loss = gross_damages - self.expected_recovery

        return self


@dataclass
class DefaultAnalysisResults:
    """
    Complete results of default damage analysis
    """
    lease_terms: LeaseTerms
    default_event: DefaultEvent
    damage_calculation: DamageCalculation
    bankruptcy_scenarios: List[BankruptcyScenario]

    analysis_date: date
    analysis_notes: List[str] = field(default_factory=list)


# ============================================================================
# DAMAGE CALCULATION FUNCTIONS
# ============================================================================

def calculate_accelerated_rent_npv(
    monthly_rent: float,
    additional_rent_monthly: float,
    remaining_months: int,
    discount_rate_annual: float
) -> float:
    """
    Calculate NPV of accelerated rent claim

    Landlord can claim present value of all remaining lease payments
    after tenant default, subject to mitigation duty.

    Args:
        monthly_rent: Base monthly rent
        additional_rent_monthly: Additional rent (taxes, opex) per month
        remaining_months: Months remaining on lease term
        discount_rate_annual: Annual discount rate (e.g., 0.10 for 10%)

    Returns:
        Present value of remaining lease payments
    """
    if remaining_months <= 0:
        return 0.0

    monthly_rate = (1 + discount_rate_annual) ** (1/12) - 1
    total_monthly_rent = monthly_rent + additional_rent_monthly

    # NPV of annuity formula
    if monthly_rate == 0:
        npv = total_monthly_rent * remaining_months
    else:
        npv = total_monthly_rent * (1 - (1 + monthly_rate) ** -remaining_months) / monthly_rate

    return npv


def calculate_re_leasing_costs(
    rentable_area_sf: float,
    ti_allowance_sf: float,
    market_rent_annual: float,
    lease_term_years: int,
    leasing_commission_pct: float,
    legal_fees: float
) -> Dict[str, float]:
    """
    Calculate costs to re-lease the premises

    Includes:
    - Tenant improvements (TI)
    - Leasing commissions (% of lease value)
    - Legal fees for new lease

    Args:
        rentable_area_sf: Rentable square footage
        ti_allowance_sf: TI allowance per SF
        market_rent_annual: Annual market rent for new lease
        lease_term_years: Expected term for new lease
        leasing_commission_pct: Commission as % of total lease value
        legal_fees: Legal fees for new lease

    Returns:
        Dictionary with ti_costs, commissions, legal_fees, total
    """
    ti_costs = rentable_area_sf * ti_allowance_sf
    lease_value = market_rent_annual * lease_term_years
    commissions = lease_value * leasing_commission_pct

    return {
        "ti_costs": ti_costs,
        "commissions": commissions,
        "legal_fees": legal_fees,
        "total": ti_costs + commissions + legal_fees
    }


def calculate_mitigation_credit(
    market_rent_monthly: float,
    remaining_months: int,
    downtime_months: int,
    discount_rate_annual: float
) -> float:
    """
    Calculate NPV of mitigation credit from re-leasing

    Landlord has duty to mitigate damages by re-leasing premises.
    Credit = PV of new lease rent that overlaps with old lease term.

    Args:
        market_rent_monthly: Monthly rent for new lease
        remaining_months: Months remaining on old lease
        downtime_months: Expected months until re-lease
        discount_rate_annual: Annual discount rate

    Returns:
        Present value of mitigation credit
    """
    if downtime_months >= remaining_months:
        # Can't re-lease before old lease expires
        return 0.0

    overlap_months = remaining_months - downtime_months

    if overlap_months <= 0:
        return 0.0

    monthly_rate = (1 + discount_rate_annual) ** (1/12) - 1

    # PV of rent starting after downtime period
    discount_factor = (1 + monthly_rate) ** -downtime_months

    if monthly_rate == 0:
        pv_rent = market_rent_monthly * overlap_months
    else:
        pv_rent = market_rent_monthly * (1 - (1 + monthly_rate) ** -overlap_months) / monthly_rate

    return pv_rent * discount_factor


def calculate_bankruptcy_claims(
    monthly_rent: float,
    additional_rent_monthly: float,
    remaining_months: int,
    gross_damages: float
) -> BankruptcyScenario:
    """
    Calculate bankruptcy-specific claims under trustee rejection

    Bankruptcy Code § 502(b)(6) caps landlord claims:
    - Greater of 1 year rent OR 15% of remaining rent (max 3 years)
    - Plus actual damages for 60 days post-rejection

    Args:
        monthly_rent: Base monthly rent
        additional_rent_monthly: Additional rent per month
        remaining_months: Months remaining on lease
        gross_damages: Total gross damages calculated

    Returns:
        BankruptcyScenario with priority, administrative, and unsecured claims
    """
    total_monthly = monthly_rent + additional_rent_monthly

    # Priority claim: 60 days post-rejection rent
    priority_claim = total_monthly * 2  # 2 months

    # Cap calculation under § 502(b)(6)
    one_year_rent = total_monthly * 12
    fifteen_pct_rent = total_monthly * min(remaining_months, 36) * 0.15
    statutory_cap = max(one_year_rent, fifteen_pct_rent)

    # Unsecured claim limited to statutory cap
    unsecured_claim = max(0.0, min(gross_damages - priority_claim, statutory_cap))

    scenario = BankruptcyScenario(
        scenario_name="Trustee Rejection",
        priority_claim_60_days=priority_claim,
        administrative_claim=0.0,  # Assumes rejection immediately
        unsecured_claim=unsecured_claim,
        priority_recovery_rate=1.0,
        administrative_recovery_rate=1.0,
        unsecured_recovery_rate=0.20,  # Conservative 20% estimate
        preference_period_days=90,
        payments_at_risk=total_monthly * 3  # Last 3 months payments
    )

    scenario.calculate_expected_recovery(gross_damages)

    return scenario


def calculate_default_damages(
    lease: LeaseTerms,
    default: DefaultEvent
) -> DefaultAnalysisResults:
    """
    Calculate complete damage analysis for tenant default

    Quantifies:
    1. Unpaid rent and immediate damages
    2. Accelerated rent (NPV of remaining term)
    3. Re-leasing costs (TI, commissions, legal)
    4. Lost rent during downtime
    5. Mitigation credits (security deposit, re-lease rent)
    6. Bankruptcy scenarios

    Args:
        lease: Lease terms extracted from lease agreement
        default: Details of default event

    Returns:
        Complete default analysis with damages and scenarios
    """
    damages = DamageCalculation()

    # ========================================================================
    # 1. IMMEDIATE DAMAGES
    # ========================================================================
    if default.default_type == "monetary":
        damages.unpaid_rent = default.amount_owing

    # ========================================================================
    # 2. ACCELERATED RENT (NPV)
    # ========================================================================
    additional_rent_monthly = lease.additional_rent_annual / 12

    damages.accelerated_rent_npv = calculate_accelerated_rent_npv(
        monthly_rent=lease.current_monthly_rent,
        additional_rent_monthly=additional_rent_monthly,
        remaining_months=lease.remaining_months,
        discount_rate_annual=lease.discount_rate_annual
    )

    # ========================================================================
    # 3. RE-LEASING COSTS
    # ========================================================================
    market_rent_annual = lease.market_rent_sf * lease.rentable_area_sf
    new_lease_term_years = min(5, lease.remaining_months / 12)  # Assume 5-year new lease

    re_leasing = calculate_re_leasing_costs(
        rentable_area_sf=lease.rentable_area_sf,
        ti_allowance_sf=lease.ti_allowance_sf,
        market_rent_annual=market_rent_annual,
        lease_term_years=new_lease_term_years,
        leasing_commission_pct=lease.leasing_commission_pct,
        legal_fees=lease.legal_fees
    )

    damages.ti_costs = re_leasing["ti_costs"]
    damages.leasing_commissions = re_leasing["commissions"]
    damages.legal_fees = re_leasing["legal_fees"]

    # ========================================================================
    # 4. LOST RENT DURING DOWNTIME
    # ========================================================================
    damages.lost_rent_downtime = lease.current_monthly_rent * lease.downtime_months

    # ========================================================================
    # 5. MITIGATION CREDITS
    # ========================================================================
    damages.security_deposit_credit = lease.security_deposit

    market_rent_monthly = market_rent_annual / 12
    damages.re_lease_rent_credit_npv = calculate_mitigation_credit(
        market_rent_monthly=market_rent_monthly,
        remaining_months=lease.remaining_months,
        downtime_months=lease.downtime_months,
        discount_rate_annual=lease.discount_rate_annual
    )

    # ========================================================================
    # 6. CALCULATE NET DAMAGES
    # ========================================================================
    damages.calculate_totals()

    # ========================================================================
    # 7. BANKRUPTCY SCENARIOS
    # ========================================================================
    bankruptcy_scenario = calculate_bankruptcy_claims(
        monthly_rent=lease.current_monthly_rent,
        additional_rent_monthly=additional_rent_monthly,
        remaining_months=lease.remaining_months,
        gross_damages=damages.gross_damages
    )

    # ========================================================================
    # 8. ANALYSIS NOTES
    # ========================================================================
    notes = [
        f"Default date: {default.default_date.strftime('%B %d, %Y')}",
        f"Default type: {default.default_type}",
        f"Remaining lease term: {lease.remaining_months} months",
        f"Current monthly rent: ${lease.current_monthly_rent:,.2f}",
        f"Discount rate: {lease.discount_rate_annual:.1%}",
        f"Expected downtime: {lease.downtime_months} months"
    ]

    if lease.market_rent_sf > 0:
        notes.append(f"Market rent: ${lease.market_rent_sf:.2f}/SF (${market_rent_annual:,.0f}/year)")

    return DefaultAnalysisResults(
        lease_terms=lease,
        default_event=default,
        damage_calculation=damages,
        bankruptcy_scenarios=[bankruptcy_scenario],
        analysis_date=date.today(),
        analysis_notes=notes
    )


# ============================================================================
# JSON INPUT/OUTPUT
# ============================================================================

def load_default_scenario_from_json(json_path: str) -> tuple[LeaseTerms, DefaultEvent]:
    """
    Load lease terms and default event from JSON file

    Expected JSON structure:
    {
      "lease_terms": { ... },
      "default_event": { ... }
    }
    """
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Parse lease terms
    lease_data = data["lease_terms"]
    lease = LeaseTerms(
        property_address=lease_data["property_address"],
        tenant_name=lease_data["tenant_name"],
        landlord_name=lease_data["landlord_name"],
        current_monthly_rent=float(lease_data["current_monthly_rent"]),
        current_annual_rent=float(lease_data["current_annual_rent"]),
        rentable_area_sf=float(lease_data["rentable_area_sf"]),
        rent_per_sf=float(lease_data["rent_per_sf"]),
        lease_commencement_date=datetime.strptime(lease_data["lease_commencement_date"], "%Y-%m-%d").date(),
        lease_expiry_date=datetime.strptime(lease_data["lease_expiry_date"], "%Y-%m-%d").date(),
        remaining_months=int(lease_data["remaining_months"]),
        additional_rent_annual=float(lease_data.get("additional_rent_annual", 0.0)),
        security_deposit=float(lease_data.get("security_deposit", 0.0)),
        monetary_default_cure_days=int(lease_data.get("monetary_default_cure_days", 5)),
        non_monetary_default_cure_days=int(lease_data.get("non_monetary_default_cure_days", 15)),
        market_rent_sf=float(lease_data.get("market_rent_sf", 0.0)),
        ti_allowance_sf=float(lease_data.get("ti_allowance_sf", 15.0)),
        leasing_commission_pct=float(lease_data.get("leasing_commission_pct", 0.05)),
        legal_fees=float(lease_data.get("legal_fees", 5000.0)),
        downtime_months=int(lease_data.get("downtime_months", 6)),
        discount_rate_annual=float(lease_data.get("discount_rate_annual", 0.10))
    )

    # Parse default event
    default_data = data["default_event"]
    default = DefaultEvent(
        default_date=datetime.strptime(default_data["default_date"], "%Y-%m-%d").date(),
        default_type=default_data["default_type"],
        description=default_data["description"],
        amount_owing=float(default_data.get("amount_owing", 0.0)),
        cure_period_days=int(default_data.get("cure_period_days", 0)),
        cure_deadline=datetime.strptime(default_data["cure_deadline"], "%Y-%m-%d").date() if "cure_deadline" in default_data else None
    )

    return lease, default


def save_results_to_json(results: DefaultAnalysisResults, output_path: str):
    """Save analysis results to JSON file"""

    def date_to_str(obj):
        """Convert date objects to ISO strings for JSON serialization"""
        if isinstance(obj, date):
            return obj.isoformat()
        return obj

    output = {
        "analysis_date": results.analysis_date.isoformat(),
        "lease_terms": {
            "property_address": results.lease_terms.property_address,
            "tenant_name": results.lease_terms.tenant_name,
            "landlord_name": results.lease_terms.landlord_name,
            "current_monthly_rent": results.lease_terms.current_monthly_rent,
            "remaining_months": results.lease_terms.remaining_months
        },
        "default_event": {
            "default_date": results.default_event.default_date.isoformat(),
            "default_type": results.default_event.default_type,
            "description": results.default_event.description,
            "amount_owing": results.default_event.amount_owing
        },
        "damages": {
            "immediate": {
                "unpaid_rent": results.damage_calculation.unpaid_rent,
                "unpaid_additional_rent": results.damage_calculation.unpaid_additional_rent,
                "late_fees": results.damage_calculation.late_fees
            },
            "future": {
                "accelerated_rent_npv": results.damage_calculation.accelerated_rent_npv,
                "lost_rent_downtime": results.damage_calculation.lost_rent_downtime
            },
            "re_leasing_costs": {
                "ti_costs": results.damage_calculation.ti_costs,
                "leasing_commissions": results.damage_calculation.leasing_commissions,
                "legal_fees": results.damage_calculation.legal_fees
            },
            "credits": {
                "security_deposit": results.damage_calculation.security_deposit_credit,
                "re_lease_rent_npv": results.damage_calculation.re_lease_rent_credit_npv
            },
            "totals": {
                "gross_damages": results.damage_calculation.gross_damages,
                "total_credits": results.damage_calculation.total_credits,
                "net_damages": results.damage_calculation.net_damages
            }
        },
        "bankruptcy_scenarios": [
            {
                "scenario_name": scenario.scenario_name,
                "priority_claim_60_days": scenario.priority_claim_60_days,
                "unsecured_claim": scenario.unsecured_claim,
                "expected_recovery": scenario.expected_recovery,
                "expected_loss": scenario.expected_loss,
                "payments_at_risk_90_days": scenario.payments_at_risk
            }
            for scenario in results.bankruptcy_scenarios
        ],
        "analysis_notes": results.analysis_notes
    }

    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def main():
    """Command-line interface for default damage calculator"""
    if len(sys.argv) < 2:
        print("Usage: python default_calculator.py <input.json> [output.json]")
        print("\nExample:")
        print("  python default_calculator.py default_scenario.json")
        print("  python default_calculator.py default_scenario.json results.json")
        sys.exit(1)

    input_path = sys.argv[1]

    # Generate output path
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
    else:
        output_path = str(Path(input_path).with_suffix('')) + "_results.json"

    print(f"Loading default scenario from: {input_path}")
    lease, default = load_default_scenario_from_json(input_path)

    print(f"Calculating damages...")
    results = calculate_default_damages(lease, default)

    print(f"Saving results to: {output_path}")
    save_results_to_json(results, output_path)

    print(f"\n✅ Damage calculation complete!")
    print(f"\nKey findings:")
    print(f"  - Tenant: {lease.tenant_name}")
    print(f"  - Property: {lease.property_address}")
    print(f"  - Default type: {default.default_type}")
    print(f"  - Gross damages: ${results.damage_calculation.gross_damages:,.2f}")
    print(f"  - Total credits: ${results.damage_calculation.total_credits:,.2f}")
    print(f"  - Net damages: ${results.damage_calculation.net_damages:,.2f}")

    if results.bankruptcy_scenarios:
        bk = results.bankruptcy_scenarios[0]
        print(f"\nBankruptcy scenario ({bk.scenario_name}):")
        print(f"  - Expected recovery: ${bk.expected_recovery:,.2f}")
        print(f"  - Expected loss: ${bk.expected_loss:,.2f}")


if __name__ == '__main__':
    main()
