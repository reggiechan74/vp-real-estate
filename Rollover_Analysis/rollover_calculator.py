#!/usr/bin/env python3
"""
Portfolio Lease Rollover Analysis Calculator

Analyzes lease expiration risk across a real estate portfolio with:
- Expiry schedule aggregation by year/quarter
- Concentration risk identification
- Renewal priority scoring
- Scenario modeling (optimistic/base/pessimistic)
- NPV-discounted NOI impact analysis

Author: Claude Code
Version: 1.0.0
Date: 2025-11-06
"""

import json
import sys
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from pathlib import Path


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Lease:
    """Individual lease in the portfolio"""
    property_address: str
    tenant_name: str
    rentable_area_sf: float
    current_annual_rent: float
    lease_expiry_date: date
    renewal_options: List[date]
    tenant_credit_rating: str
    below_market_pct: float  # Negative = below market opportunity

    def __post_init__(self):
        """Validate lease data"""
        if self.rentable_area_sf <= 0:
            raise ValueError(f"Invalid rentable area: {self.rentable_area_sf}")
        if self.current_annual_rent < 0:
            raise ValueError(f"Invalid annual rent: {self.current_annual_rent}")
        if not self.tenant_credit_rating:
            self.tenant_credit_rating = "NR"


@dataclass
class Assumptions:
    """Portfolio analysis assumptions"""
    discount_rate: float = 0.10
    renewal_rate_optimistic: float = 0.80
    renewal_rate_base: float = 0.65
    renewal_rate_pessimistic: float = 0.50
    downtime_months: Dict[str, int] = field(default_factory=lambda: {
        "optimistic": 1,
        "base": 3,
        "pessimistic": 6
    })
    market_rent_sf: float = 16.50
    market_rent_growth_annual: float = 0.025
    ti_allowance_sf: float = 15.00
    leasing_commission_pct: float = 0.05

    def __post_init__(self):
        """Validate assumptions"""
        if not (0 < self.discount_rate < 1):
            raise ValueError(f"Discount rate must be between 0 and 1: {self.discount_rate}")
        if not all(0 <= r <= 1 for r in [
            self.renewal_rate_optimistic,
            self.renewal_rate_base,
            self.renewal_rate_pessimistic
        ]):
            raise ValueError("Renewal rates must be between 0 and 1")


@dataclass
class PortfolioInput:
    """Complete portfolio rollover analysis input"""
    portfolio_name: str
    analysis_date: date
    leases: List[Lease]
    assumptions: Assumptions

    @property
    def total_area_sf(self) -> float:
        """Total portfolio area"""
        return sum(lease.rentable_area_sf for lease in self.leases)

    @property
    def total_annual_rent(self) -> float:
        """Total portfolio rent"""
        return sum(lease.current_annual_rent for lease in self.leases)


@dataclass
class ExpiryScheduleItem:
    """Expiry schedule for a single year"""
    year: int
    lease_count: int
    total_sf: float
    total_annual_rent: float
    pct_of_portfolio_sf: float
    pct_of_portfolio_rent: float
    cumulative_pct_sf: float
    cumulative_pct_rent: float
    risk_level: str  # MODERATE, HIGH, CRITICAL

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "year": self.year,
            "lease_count": self.lease_count,
            "total_sf": self.total_sf,
            "total_annual_rent": self.total_annual_rent,
            "pct_of_portfolio_sf": round(self.pct_of_portfolio_sf, 2),
            "pct_of_portfolio_rent": round(self.pct_of_portfolio_rent, 2),
            "cumulative_pct_sf": round(self.cumulative_pct_sf, 2),
            "cumulative_pct_rent": round(self.cumulative_pct_rent, 2),
            "risk_level": self.risk_level
        }


@dataclass
class PriorityScore:
    """Priority score for a single lease"""
    lease: Lease
    rent_pct: float  # 0-1
    urgency: float  # 0-1
    below_market: float  # 0-1
    credit_risk: float  # 0-1
    priority_score: float  # 0-1
    rank: int

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "property_address": self.lease.property_address,
            "tenant_name": self.lease.tenant_name,
            "lease_expiry_date": self.lease.lease_expiry_date.isoformat(),
            "annual_rent": self.lease.current_annual_rent,
            "rent_pct": round(self.rent_pct, 4),
            "urgency": round(self.urgency, 4),
            "below_market": round(self.below_market, 4),
            "credit_risk": round(self.credit_risk, 4),
            "priority_score": round(self.priority_score, 4),
            "rank": self.rank
        }


@dataclass
class ScenarioResult:
    """Scenario analysis result"""
    scenario_name: str
    renewal_rate: float
    downtime_months: int
    leases_renewed: int
    leases_new_tenant: int
    expected_vacancy_sf: float
    expected_vacancy_rent: float
    noi_impact_npv: float

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "scenario_name": self.scenario_name,
            "renewal_rate": round(self.renewal_rate, 2),
            "downtime_months": self.downtime_months,
            "leases_renewed": self.leases_renewed,
            "leases_new_tenant": self.leases_new_tenant,
            "expected_vacancy_sf": round(self.expected_vacancy_sf, 0),
            "expected_vacancy_rent": round(self.expected_vacancy_rent, 0),
            "noi_impact_npv": round(self.noi_impact_npv, 0)
        }


@dataclass
class RolloverAnalysisResults:
    """Complete rollover analysis results"""
    portfolio_name: str
    analysis_date: date
    total_area_sf: float
    total_annual_rent: float
    expiry_schedule: List[ExpiryScheduleItem]
    priority_ranking: List[PriorityScore]
    scenarios: List[ScenarioResult]

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "portfolio_name": self.portfolio_name,
            "analysis_date": self.analysis_date.isoformat(),
            "total_area_sf": round(self.total_area_sf, 0),
            "total_annual_rent": round(self.total_annual_rent, 0),
            "expiry_schedule": [item.to_dict() for item in self.expiry_schedule],
            "priority_ranking": [score.to_dict() for score in self.priority_ranking],
            "scenarios": [scenario.to_dict() for scenario in self.scenarios]
        }


# ============================================================================
# CREDIT RATING MAPPING
# ============================================================================

def credit_rating_to_score(rating: str) -> float:
    """
    Map credit rating to 0-1 risk score (0=best, 1=worst)

    Investment Grade (0.0-0.45):
    - AAA to BBB-

    High Yield / Speculative (0.55-0.99):
    - BB+ to D

    Not Rated: 0.70 (assumes below investment grade)
    """
    rating_map = {
        # Investment Grade
        'AAA': 0.00, 'AA+': 0.05, 'AA': 0.10, 'AA-': 0.15,
        'A+': 0.15, 'A': 0.20, 'A-': 0.25,
        'BBB+': 0.35, 'BBB': 0.40, 'BBB-': 0.45,
        # High Yield
        'BB+': 0.55, 'BB': 0.60, 'BB-': 0.65,
        'B+': 0.75, 'B': 0.80, 'B-': 0.85,
        'CCC+': 0.90, 'CCC': 0.95, 'CCC-': 0.95,
        'CC': 0.98, 'C': 0.99, 'D': 1.00,
        # Not Rated
        'NR': 0.70, '': 0.70, None: 0.70
    }

    normalized_rating = rating.strip().upper() if rating else 'NR'
    return rating_map.get(normalized_rating, 0.70)  # Default to NR if unknown


# ============================================================================
# CORE CALCULATIONS
# ============================================================================

def calculate_expiry_schedule(
    portfolio: PortfolioInput
) -> List[ExpiryScheduleItem]:
    """
    Aggregate lease expiries by year

    Returns schedule with:
    - Lease counts
    - Total SF and rent
    - Portfolio percentages
    - Cumulative percentages
    - Risk levels (MODERATE/HIGH/CRITICAL)
    """
    # Group leases by expiry year
    expiries_by_year = defaultdict(list)
    for lease in portfolio.leases:
        year = lease.lease_expiry_date.year
        expiries_by_year[year].append(lease)

    # Calculate totals
    total_sf = portfolio.total_area_sf
    total_rent = portfolio.total_annual_rent

    # Build schedule
    schedule = []
    cumulative_sf = 0.0
    cumulative_rent = 0.0

    for year in sorted(expiries_by_year.keys()):
        leases = expiries_by_year[year]
        year_sf = sum(l.rentable_area_sf for l in leases)
        year_rent = sum(l.current_annual_rent for l in leases)

        pct_sf = (year_sf / total_sf * 100) if total_sf > 0 else 0
        pct_rent = (year_rent / total_rent * 100) if total_rent > 0 else 0

        cumulative_sf += year_sf
        cumulative_rent += year_rent

        cumulative_pct_sf = (cumulative_sf / total_sf * 100) if total_sf > 0 else 0
        cumulative_pct_rent = (cumulative_rent / total_rent * 100) if total_rent > 0 else 0

        # Determine risk level
        if pct_sf > 30 or pct_rent > 30:
            risk_level = "CRITICAL"
        elif pct_sf > 20 or pct_rent > 20:
            risk_level = "HIGH"
        else:
            risk_level = "MODERATE"

        schedule.append(ExpiryScheduleItem(
            year=year,
            lease_count=len(leases),
            total_sf=year_sf,
            total_annual_rent=year_rent,
            pct_of_portfolio_sf=pct_sf,
            pct_of_portfolio_rent=pct_rent,
            cumulative_pct_sf=cumulative_pct_sf,
            cumulative_pct_rent=cumulative_pct_rent,
            risk_level=risk_level
        ))

    return schedule


def calculate_priority_scores(
    portfolio: PortfolioInput
) -> List[PriorityScore]:
    """
    Calculate renewal priority score for each lease using 0-1 normalized inputs

    Priority = (Rent_Pct × 0.40) + (Urgency × 0.30) + (Below_Market × 0.20) + (Credit_Risk × 0.10)

    All components normalized to 0-1 scale to prevent scale dominance
    """
    total_rent = portfolio.total_annual_rent
    analysis_date = portfolio.analysis_date

    scores = []
    for lease in portfolio.leases:
        # 1. Rent percentage (0-1, capped at 100%)
        rent_pct = min(lease.current_annual_rent / total_rent, 1.0) if total_rent > 0 else 0.0

        # 2. Urgency (0-1, based on 24-month window)
        months_to_expiry = (lease.lease_expiry_date.year - analysis_date.year) * 12 + \
                          (lease.lease_expiry_date.month - analysis_date.month)
        urgency = max(0.0, 1.0 - min(months_to_expiry / 24.0, 1.0))

        # 3. Below market opportunity (0-1, 20% = 1.0)
        below_market = max(0.0, min(abs(lease.below_market_pct) / 20.0, 1.0))

        # 4. Credit risk (0-1 from rating map)
        credit_risk = credit_rating_to_score(lease.tenant_credit_rating)

        # Weighted priority score
        priority_score = (
            rent_pct * 0.40 +
            urgency * 0.30 +
            below_market * 0.20 +
            credit_risk * 0.10
        )

        scores.append(PriorityScore(
            lease=lease,
            rent_pct=rent_pct,
            urgency=urgency,
            below_market=below_market,
            credit_risk=credit_risk,
            priority_score=priority_score,
            rank=0  # Will be assigned after sorting
        ))

    # Sort by priority score (descending) and assign ranks
    scores.sort(key=lambda x: x.priority_score, reverse=True)
    for i, score in enumerate(scores, start=1):
        score.rank = i

    return scores


def calculate_scenario_analysis(
    portfolio: PortfolioInput,
    expiry_schedule: List[ExpiryScheduleItem]
) -> List[ScenarioResult]:
    """
    Model three scenarios (optimistic/base/pessimistic) with NPV-discounted NOI impact

    For each scenario:
    - Apply scenario-specific renewal rate
    - Apply scenario-specific downtime months (minimum 1 month even on renewals)
    - Calculate expected vacancy and lost rent
    - Discount NOI impact to present value
    """
    assumptions = portfolio.assumptions
    analysis_date = portfolio.analysis_date

    scenarios = [
        ("Optimistic", assumptions.renewal_rate_optimistic, assumptions.downtime_months["optimistic"]),
        ("Base", assumptions.renewal_rate_base, assumptions.downtime_months["base"]),
        ("Pessimistic", assumptions.renewal_rate_pessimistic, assumptions.downtime_months["pessimistic"])
    ]

    results = []
    for scenario_name, renewal_rate, downtime_months in scenarios:
        # Calculate renewals vs new tenants
        total_leases = len(portfolio.leases)
        leases_renewed = int(total_leases * renewal_rate)
        leases_new_tenant = total_leases - leases_renewed

        # Calculate expected vacancy
        total_sf = portfolio.total_area_sf
        total_rent = portfolio.total_annual_rent

        # Expected vacancy = all leases have downtime (renewals have minimum 1 month)
        expected_downtime_months = downtime_months
        expected_vacancy_rent = total_rent * (expected_downtime_months / 12.0)

        # Calculate NPV of NOI impact
        # Discount back to analysis date at discount rate
        years_ahead = []
        noi_deltas = []

        for item in expiry_schedule:
            years_to_expiry = item.year - analysis_date.year
            if years_to_expiry > 0:
                years_ahead.append(years_to_expiry)
                # NOI delta = lost rent during downtime
                noi_delta = -item.total_annual_rent * (downtime_months / 12.0)
                noi_deltas.append(noi_delta)

        # Discount to present value
        noi_impact_npv = sum(
            delta / ((1 + assumptions.discount_rate) ** year)
            for year, delta in zip(years_ahead, noi_deltas)
        )

        results.append(ScenarioResult(
            scenario_name=scenario_name,
            renewal_rate=renewal_rate,
            downtime_months=downtime_months,
            leases_renewed=leases_renewed,
            leases_new_tenant=leases_new_tenant,
            expected_vacancy_sf=total_sf,  # All space has downtime
            expected_vacancy_rent=expected_vacancy_rent,
            noi_impact_npv=noi_impact_npv
        ))

    return results


# ============================================================================
# MAIN ANALYSIS FUNCTION
# ============================================================================

def calculate_rollover_analysis(portfolio: PortfolioInput) -> RolloverAnalysisResults:
    """
    Perform complete portfolio rollover analysis

    Returns comprehensive results including:
    - Expiry schedule by year
    - Priority ranking of leases
    - Scenario analysis (optimistic/base/pessimistic)
    """
    # Validate portfolio
    if not portfolio.leases:
        raise ValueError("Portfolio must contain at least one lease")

    # Calculate components
    expiry_schedule = calculate_expiry_schedule(portfolio)
    priority_ranking = calculate_priority_scores(portfolio)
    scenarios = calculate_scenario_analysis(portfolio, expiry_schedule)

    return RolloverAnalysisResults(
        portfolio_name=portfolio.portfolio_name,
        analysis_date=portfolio.analysis_date,
        total_area_sf=portfolio.total_area_sf,
        total_annual_rent=portfolio.total_annual_rent,
        expiry_schedule=expiry_schedule,
        priority_ranking=priority_ranking,
        scenarios=scenarios
    )


# ============================================================================
# JSON I/O
# ============================================================================

def load_portfolio_from_json(json_path: str) -> PortfolioInput:
    """Load portfolio data from JSON file"""
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Parse assumptions
    assumptions_data = data.get('assumptions', {})
    assumptions = Assumptions(
        discount_rate=assumptions_data.get('discount_rate', 0.10),
        renewal_rate_optimistic=assumptions_data.get('renewal_rate_optimistic', 0.80),
        renewal_rate_base=assumptions_data.get('renewal_rate_base', 0.65),
        renewal_rate_pessimistic=assumptions_data.get('renewal_rate_pessimistic', 0.50),
        downtime_months=assumptions_data.get('downtime_months', {
            "optimistic": 1, "base": 3, "pessimistic": 6
        }),
        market_rent_sf=assumptions_data.get('market_rent_sf', 16.50),
        market_rent_growth_annual=assumptions_data.get('market_rent_growth_annual', 0.025),
        ti_allowance_sf=assumptions_data.get('ti_allowance_sf', 15.00),
        leasing_commission_pct=assumptions_data.get('leasing_commission_pct', 0.05)
    )

    # Parse leases
    leases = []
    for lease_data in data['leases']:
        lease = Lease(
            property_address=lease_data['property_address'],
            tenant_name=lease_data['tenant_name'],
            rentable_area_sf=float(lease_data['rentable_area_sf']),
            current_annual_rent=float(lease_data['current_annual_rent']),
            lease_expiry_date=datetime.strptime(lease_data['lease_expiry_date'], '%Y-%m-%d').date(),
            renewal_options=[datetime.strptime(d, '%Y-%m-%d').date() for d in lease_data.get('renewal_options', [])],
            tenant_credit_rating=lease_data.get('tenant_credit_rating', 'NR'),
            below_market_pct=float(lease_data.get('below_market_pct', 0.0))
        )
        leases.append(lease)

    # Parse analysis date
    analysis_date = datetime.strptime(data['analysis_date'], '%Y-%m-%d').date()

    return PortfolioInput(
        portfolio_name=data['portfolio_name'],
        analysis_date=analysis_date,
        leases=leases,
        assumptions=assumptions
    )


def save_results_to_json(results: RolloverAnalysisResults, output_path: str):
    """Save analysis results to JSON file"""
    with open(output_path, 'w') as f:
        json.dump(results.to_dict(), f, indent=2)


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

def main():
    """Command-line interface"""
    if len(sys.argv) < 2:
        print("Usage: python rollover_calculator.py <input.json> [output.json]")
        print("\nExample:")
        print("  python rollover_calculator.py portfolio.json")
        print("  python rollover_calculator.py portfolio.json results.json")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else input_path.replace('.json', '_results.json')

    print(f"Loading portfolio from: {input_path}")
    portfolio = load_portfolio_from_json(input_path)

    print(f"Analyzing portfolio: {portfolio.portfolio_name}")
    print(f"  - {len(portfolio.leases)} leases")
    print(f"  - {portfolio.total_area_sf:,.0f} SF")
    print(f"  - ${portfolio.total_annual_rent:,.0f} annual rent")

    results = calculate_rollover_analysis(portfolio)

    print(f"\nSaving results to: {output_path}")
    save_results_to_json(results, output_path)

    print("\n✅ Analysis complete!")
    print(f"\nKey findings:")
    print(f"  - {len(results.expiry_schedule)} years analyzed")
    print(f"  - {sum(1 for item in results.expiry_schedule if item.risk_level == 'CRITICAL')} CRITICAL risk years")
    print(f"  - {sum(1 for item in results.expiry_schedule if item.risk_level == 'HIGH')} HIGH risk years")
    print(f"\nTop 3 priority leases:")
    for score in results.priority_ranking[:3]:
        print(f"  {score.rank}. {score.lease.tenant_name} - {score.lease.property_address} (Score: {score.priority_score:.3f})")


if __name__ == '__main__':
    main()
