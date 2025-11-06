#!/usr/bin/env python3
"""
Portfolio Lease Rollover Analysis - Markdown Report Generator

Generates executive-ready markdown reports from rollover analysis results.

Author: Claude Code
Version: 1.0.0
Date: 2025-11-06
"""

import sys
from datetime import datetime
from pathlib import Path
from rollover_calculator import (
    RolloverAnalysisResults,
    load_portfolio_from_json,
    calculate_rollover_analysis
)


def get_eastern_timestamp() -> str:
    """Generate YYYY-MM-DD_HHMMSS timestamp (local time as proxy for Eastern)"""
    return datetime.now().strftime("%Y-%m-%d_%H%M%S")


def generate_markdown_report(results: RolloverAnalysisResults) -> str:
    """
    Generate executive-ready markdown report from rollover analysis results

    Report includes:
    - Executive summary with key metrics
    - Expiry schedule table with risk flags
    - Top 10 priority leases
    - Scenario analysis with NOI impact
    - Recommended actions
    """

    report = []

    # ========================================================================
    # HEADER
    # ========================================================================
    report.append(f"# Portfolio Lease Rollover Analysis")
    report.append(f"")
    report.append(f"**Portfolio**: {results.portfolio_name}")
    report.append(f"**Analysis Date**: {results.analysis_date.strftime('%B %d, %Y')}")
    report.append(f"**Report Generated**: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    report.append(f"")
    report.append(f"---")
    report.append(f"")

    # ========================================================================
    # EXECUTIVE SUMMARY
    # ========================================================================
    report.append(f"## Executive Summary")
    report.append(f"")
    report.append(f"### Portfolio Overview")
    report.append(f"")
    report.append(f"- **Total Leases**: {len(results.priority_ranking)}")
    report.append(f"- **Total Area**: {results.total_area_sf:,.0f} SF")
    report.append(f"- **Total Annual Rent**: ${results.total_annual_rent:,.0f}")
    report.append(f"- **Average Rent**: ${results.total_annual_rent / results.total_area_sf:.2f}/SF")
    report.append(f"")

    # Count risk years
    critical_years = [item for item in results.expiry_schedule if item.risk_level == "CRITICAL"]
    high_years = [item for item in results.expiry_schedule if item.risk_level == "HIGH"]
    moderate_years = [item for item in results.expiry_schedule if item.risk_level == "MODERATE"]

    report.append(f"### Rollover Risk Assessment")
    report.append(f"")
    if critical_years:
        report.append(f"⚠️ **CRITICAL RISK**: {len(critical_years)} year(s) with >30% of portfolio expiring")
        for item in critical_years:
            report.append(f"   - {item.year}: {item.pct_of_portfolio_sf:.1f}% SF, {item.pct_of_portfolio_rent:.1f}% rent ({item.lease_count} leases)")
    if high_years:
        report.append(f"")
        report.append(f"🔶 **HIGH RISK**: {len(high_years)} year(s) with 20-30% of portfolio expiring")
        for item in high_years:
            report.append(f"   - {item.year}: {item.pct_of_portfolio_sf:.1f}% SF, {item.pct_of_portfolio_rent:.1f}% rent ({item.lease_count} leases)")
    if moderate_years:
        report.append(f"")
        report.append(f"✓ **MODERATE RISK**: {len(moderate_years)} year(s) with <20% of portfolio expiring")

    report.append(f"")
    report.append(f"---")
    report.append(f"")

    # ========================================================================
    # EXPIRY SCHEDULE
    # ========================================================================
    report.append(f"## Lease Expiry Schedule")
    report.append(f"")
    report.append(f"| Year | # Leases | Total SF | Total Rent | % SF | % Rent | Cumulative SF | Cumulative Rent | Risk Level |")
    report.append(f"|------|----------|----------|------------|------|--------|---------------|-----------------|------------|")

    for item in results.expiry_schedule:
        risk_icon = {
            "CRITICAL": "🔴",
            "HIGH": "🟠",
            "MODERATE": "🟢"
        }.get(item.risk_level, "⚪")

        report.append(
            f"| {item.year} | "
            f"{item.lease_count} | "
            f"{item.total_sf:,.0f} | "
            f"${item.total_annual_rent:,.0f} | "
            f"{item.pct_of_portfolio_sf:.1f}% | "
            f"{item.pct_of_portfolio_rent:.1f}% | "
            f"{item.cumulative_pct_sf:.1f}% | "
            f"{item.cumulative_pct_rent:.1f}% | "
            f"{risk_icon} {item.risk_level} |"
        )

    report.append(f"")
    report.append(f"---")
    report.append(f"")

    # ========================================================================
    # PRIORITY RANKING (TOP 10)
    # ========================================================================
    report.append(f"## Renewal Priority Ranking")
    report.append(f"")
    report.append(f"Leases ranked by weighted priority score (0-1 scale):")
    report.append(f"")
    report.append(f"- **Rent %** (40%): Lease rent as % of portfolio")
    report.append(f"- **Urgency** (30%): Time to expiry (24-month window)")
    report.append(f"- **Below Market** (20%): Opportunity for rent adjustment")
    report.append(f"- **Credit Risk** (10%): Tenant credit rating risk")
    report.append(f"")

    report.append(f"### Top 10 Priority Leases")
    report.append(f"")
    report.append(f"| Rank | Tenant | Property | Expiry | Rent | Score | Components |")
    report.append(f"|------|--------|----------|--------|------|-------|------------|")

    for score in results.priority_ranking[:10]:
        components = (
            f"R:{score.rent_pct:.2f} "
            f"U:{score.urgency:.2f} "
            f"B:{score.below_market:.2f} "
            f"C:{score.credit_risk:.2f}"
        )

        report.append(
            f"| {score.rank} | "
            f"{score.lease.tenant_name} | "
            f"{score.lease.property_address[:30]}... | "
            f"{score.lease.lease_expiry_date.strftime('%b %Y')} | "
            f"${score.lease.current_annual_rent:,.0f} | "
            f"**{score.priority_score:.3f}** | "
            f"{components} |"
        )

    report.append(f"")
    report.append(f"**Component Explanation**:")
    report.append(f"- R = Rent % (higher = larger lease)")
    report.append(f"- U = Urgency (higher = expiring sooner)")
    report.append(f"- B = Below Market (higher = bigger opportunity)")
    report.append(f"- C = Credit Risk (higher = weaker credit)")
    report.append(f"")
    report.append(f"---")
    report.append(f"")

    # ========================================================================
    # SCENARIO ANALYSIS
    # ========================================================================
    report.append(f"## Scenario Analysis")
    report.append(f"")
    report.append(f"Three scenarios model different renewal rate and downtime assumptions:")
    report.append(f"")

    report.append(f"| Scenario | Renewal Rate | Downtime (months) | Renewed | New Tenant | Vacancy Rent | NOI Impact (NPV) |")
    report.append(f"|----------|--------------|-------------------|---------|------------|--------------|------------------|")

    for scenario in results.scenarios:
        noi_color = "🟢" if scenario.noi_impact_npv > -1000000 else ("🟠" if scenario.noi_impact_npv > -2500000 else "🔴")

        report.append(
            f"| **{scenario.scenario_name}** | "
            f"{scenario.renewal_rate:.0%} | "
            f"{scenario.downtime_months} | "
            f"{scenario.leases_renewed} | "
            f"{scenario.leases_new_tenant} | "
            f"${scenario.expected_vacancy_rent:,.0f} | "
            f"{noi_color} $(${abs(scenario.noi_impact_npv):,.0f}) |"
        )

    report.append(f"")
    report.append(f"**Notes**:")
    report.append(f"- NOI Impact discounted to present value at 10% discount rate")
    report.append(f"- All leases have minimum downtime (even renewals require 1 month)")
    report.append(f"- Vacancy rent = lost rent during downtime period")
    report.append(f"")
    report.append(f"---")
    report.append(f"")

    # ========================================================================
    # RECOMMENDED ACTIONS
    # ========================================================================
    report.append(f"## Recommended Actions")
    report.append(f"")

    # Identify immediate priorities (expiring within 12 months)
    immediate_priorities = [
        score for score in results.priority_ranking
        if (score.lease.lease_expiry_date.year - results.analysis_date.year) * 12 +
           (score.lease.lease_expiry_date.month - results.analysis_date.month) <= 12
    ]

    if immediate_priorities:
        report.append(f"### Immediate Actions (Next 12 Months)")
        report.append(f"")
        report.append(f"{len(immediate_priorities)} lease(s) expiring within 12 months require immediate attention:")
        report.append(f"")
        for score in immediate_priorities[:5]:  # Top 5
            months_to_expiry = (
                (score.lease.lease_expiry_date.year - results.analysis_date.year) * 12 +
                (score.lease.lease_expiry_date.month - results.analysis_date.month)
            )
            report.append(f"{score.rank}. **{score.lease.tenant_name}** ({score.lease.property_address[:40]}...)")
            report.append(f"   - Expires: {score.lease.lease_expiry_date.strftime('%B %Y')} ({months_to_expiry} months)")
            report.append(f"   - Annual Rent: ${score.lease.current_annual_rent:,.0f}")
            report.append(f"   - Credit: {score.lease.tenant_credit_rating}")
            report.append(f"   - Action: {'Renegotiate below-market rent' if score.lease.below_market_pct < 0 else 'Maximize renewal terms'}")
            report.append(f"")

    # Strategic priorities (high score but not immediate)
    strategic_priorities = [
        score for score in results.priority_ranking[:10]
        if score not in immediate_priorities
    ]

    if strategic_priorities:
        report.append(f"### Strategic Priorities (12-24 Months)")
        report.append(f"")
        report.append(f"Begin renewal discussions early for these high-priority leases:")
        report.append(f"")
        for score in strategic_priorities[:5]:  # Top 5
            report.append(f"{score.rank}. **{score.lease.tenant_name}** - Expires {score.lease.lease_expiry_date.strftime('%B %Y')}")

    report.append(f"")

    # Critical years
    if critical_years:
        report.append(f"### Portfolio Concentration Risk")
        report.append(f"")
        for item in critical_years:
            report.append(f"- **{item.year}**: {item.lease_count} leases ({item.pct_of_portfolio_sf:.1f}% SF) expiring")
            report.append(f"  - **Risk**: Significant vacancy exposure if renewal rates disappoint")
            report.append(f"  - **Mitigation**: Stagger renewal negotiations, consider early renewals with extensions")

    report.append(f"")
    report.append(f"---")
    report.append(f"")

    # ========================================================================
    # METHODOLOGY
    # ========================================================================
    report.append(f"## Methodology")
    report.append(f"")
    report.append(f"### Priority Scoring Algorithm")
    report.append(f"")
    report.append(f"```")
    report.append(f"Priority Score = (Rent% × 0.40) + (Urgency × 0.30) + (Below Market × 0.20) + (Credit Risk × 0.10)")
    report.append(f"")
    report.append(f"Where:")
    report.append(f"  Rent% = min(lease_rent / portfolio_rent, 1.0)")
    report.append(f"  Urgency = 1 - min(months_to_expiry / 24, 1.0)")
    report.append(f"  Below Market = min(abs(below_market_pct) / 20, 1.0)")
    report.append(f"  Credit Risk = credit_rating_to_score(rating)  # 0=AAA, 1=D, 0.7=NR")
    report.append(f"```")
    report.append(f"")
    report.append(f"### Scenario Modeling")
    report.append(f"")
    report.append(f"- **Optimistic**: 80% renewal rate, 1 month downtime")
    report.append(f"- **Base**: 65% renewal rate, 3 months downtime")
    report.append(f"- **Pessimistic**: 50% renewal rate, 6 months downtime")
    report.append(f"")
    report.append(f"NOI impacts discounted to present value using 10% annual discount rate.")
    report.append(f"")
    report.append(f"### Risk Level Criteria")
    report.append(f"")
    report.append(f"- **CRITICAL**: >30% of portfolio (SF or rent) expiring in single year")
    report.append(f"- **HIGH**: 20-30% of portfolio expiring")
    report.append(f"- **MODERATE**: <20% of portfolio expiring")
    report.append(f"")
    report.append(f"---")
    report.append(f"")

    # ========================================================================
    # FOOTER
    # ========================================================================
    report.append(f"## Disclaimer")
    report.append(f"")
    report.append(f"This analysis is for informational purposes only and does not constitute professional advice. ")
    report.append(f"All recommendations should be independently verified by qualified real estate and legal professionals. ")
    report.append(f"Actual renewal outcomes may vary based on market conditions, tenant circumstances, and negotiation outcomes.")
    report.append(f"")
    report.append(f"---")
    report.append(f"")
    report.append(f"**Report Generated by**: Rollover Analysis Calculator v1.0.0")
    report.append(f"")

    return "\n".join(report)


def main():
    """Command-line interface for report generation"""
    if len(sys.argv) < 2:
        print("Usage: python report_generator.py <input.json> [output.md]")
        print("\nExample:")
        print("  python report_generator.py portfolio.json")
        print("  python report_generator.py portfolio.json report.md")
        sys.exit(1)

    input_path = sys.argv[1]

    # Generate output path with timestamp
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
    else:
        timestamp = get_eastern_timestamp()
        portfolio_name = Path(input_path).stem
        output_path = f"../../Reports/{timestamp}_rollover_analysis_{portfolio_name}.md"

    print(f"Loading portfolio from: {input_path}")
    portfolio = load_portfolio_from_json(input_path)

    print(f"Running analysis...")
    results = calculate_rollover_analysis(portfolio)

    print(f"Generating markdown report...")
    report = generate_markdown_report(results)

    # Ensure Reports directory exists
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"Saving report to: {output_path}")
    with open(output_path, 'w') as f:
        f.write(report)

    print(f"\n✅ Report generated successfully!")
    print(f"\nKey findings:")
    print(f"  - {len(results.expiry_schedule)} years analyzed")
    print(f"  - {sum(1 for item in results.expiry_schedule if item.risk_level == 'CRITICAL')} CRITICAL risk years")
    print(f"  - {sum(1 for item in results.expiry_schedule if item.risk_level == 'HIGH')} HIGH risk years")
    print(f"  - Top priority: {results.priority_ranking[0].lease.tenant_name} (Score: {results.priority_ranking[0].priority_score:.3f})")


if __name__ == '__main__':
    main()
