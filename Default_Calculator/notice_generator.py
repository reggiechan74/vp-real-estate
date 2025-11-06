#!/usr/bin/env python3
"""
Default Notice Generator - Generates Formal Notice of Default

Creates legally-formatted default notices with:
- Statement of default and cure period
- Itemized damage breakdown
- Demand for payment/performance
- Reservation of rights

Author: Claude Code
Version: 1.0.0
Date: 2025-11-06
"""

import sys
from datetime import datetime, date, timedelta
from pathlib import Path
from default_calculator import (
    DefaultAnalysisResults,
    load_default_scenario_from_json,
    calculate_default_damages
)


def get_eastern_timestamp() -> str:
    """Generate YYYY-MM-DD_HHMMSS timestamp (local time as proxy for Eastern)"""
    return datetime.now().strftime("%Y-%m-%d_%H%M%S")


def generate_default_notice(results: DefaultAnalysisResults, jurisdiction: str = "Ontario") -> str:
    """
    Generate formal notice of default

    Args:
        results: Default analysis results from calculator
        jurisdiction: Jurisdiction for legal citations (default: Ontario)

    Returns:
        Markdown-formatted default notice
    """
    lease = results.lease_terms
    default = results.default_event
    damages = results.damage_calculation

    notice = []

    # ========================================================================
    # HEADER
    # ========================================================================
    notice.append(f"# NOTICE OF DEFAULT")
    notice.append(f"")
    notice.append(f"**Date**: {datetime.now().strftime('%B %d, %Y')}")
    notice.append(f"")
    notice.append(f"**TO**: {lease.tenant_name}")
    notice.append(f"")
    notice.append(f"**FROM**: {lease.landlord_name}")
    notice.append(f"")
    notice.append(f"**RE**: Lease dated as of {lease.lease_commencement_date.strftime('%B %d, %Y')}")
    notice.append(f"      Property: {lease.property_address}")
    notice.append(f"")
    notice.append(f"---")
    notice.append(f"")

    # ========================================================================
    # STATEMENT OF DEFAULT
    # ========================================================================
    notice.append(f"## NOTICE IS HEREBY GIVEN THAT:")
    notice.append(f"")
    notice.append(f"1. You are the Tenant under the above-referenced Lease (the \"**Lease**\") for the premises located at {lease.property_address} (the \"**Premises**\").")
    notice.append(f"")
    notice.append(f"2. You are currently in **DEFAULT** of the Lease as follows:")
    notice.append(f"")
    notice.append(f"   **Default Type**: {default.default_type.upper()}")
    notice.append(f"   ")
    notice.append(f"   **Default Date**: {default.default_date.strftime('%B %d, %Y')}")
    notice.append(f"   ")
    notice.append(f"   **Description**: {default.description}")
    notice.append(f"")

    if default.default_type == "monetary":
        notice.append(f"   **Amount Owing**: ${default.amount_owing:,.2f}")
        notice.append(f"")

    # ========================================================================
    # CURE PERIOD
    # ========================================================================
    if default.cure_deadline:
        cure_deadline_str = default.cure_deadline.strftime('%B %d, %Y')
    else:
        cure_days = default.cure_period_days if default.cure_period_days > 0 else (
            lease.monetary_default_cure_days if default.default_type == "monetary"
            else lease.non_monetary_default_cure_days
        )
        cure_deadline = date.today() + timedelta(days=cure_days)
        cure_deadline_str = cure_deadline.strftime('%B %d, %Y')

    notice.append(f"## DEMAND FOR CURE")
    notice.append(f"")
    notice.append(f"Pursuant to the terms of the Lease, you are required to remedy the above default **on or before {cure_deadline_str}** (the \"**Cure Deadline**\").")
    notice.append(f"")

    if default.default_type == "monetary":
        notice.append(f"To cure this default, you must immediately pay the Landlord the full amount owing of **${default.amount_owing:,.2f}**, plus any additional rent, late fees, and interest that may accrue.")
    else:
        notice.append(f"To cure this default, you must immediately cease the conduct described above and fully remedy any breach of the Lease terms.")

    notice.append(f"")
    notice.append(f"Payment should be made by certified check or wire transfer to:")
    notice.append(f"")
    notice.append(f"   {lease.landlord_name}")
    notice.append(f"   [Payment Address]")
    notice.append(f"   [Wire Instructions]")
    notice.append(f"")
    notice.append(f"---")
    notice.append(f"")

    # ========================================================================
    # DAMAGES STATEMENT
    # ========================================================================
    notice.append(f"## NOTICE OF DAMAGES")
    notice.append(f"")
    notice.append(f"**IF YOU FAIL TO CURE THE DEFAULT BY THE CURE DEADLINE**, the Landlord may elect to terminate the Lease and pursue all remedies available at law or in equity, including damages.")
    notice.append(f"")
    notice.append(f"The Landlord's damages resulting from your default are calculated as follows:")
    notice.append(f"")

    # ========================================================================
    # DAMAGE BREAKDOWN TABLE
    # ========================================================================
    notice.append(f"### Itemized Damages")
    notice.append(f"")
    notice.append(f"| Category | Description | Amount |")
    notice.append(f"|----------|-------------|--------|")

    # Immediate damages
    if damages.unpaid_rent > 0:
        notice.append(f"| **Immediate** | Unpaid Rent | ${damages.unpaid_rent:,.2f} |")
    if damages.unpaid_additional_rent > 0:
        notice.append(f"| **Immediate** | Unpaid Additional Rent | ${damages.unpaid_additional_rent:,.2f} |")
    if damages.late_fees > 0:
        notice.append(f"| **Immediate** | Late Fees | ${damages.late_fees:,.2f} |")

    # Future damages
    if damages.accelerated_rent_npv > 0:
        notice.append(f"| **Future** | Accelerated Rent (NPV) | ${damages.accelerated_rent_npv:,.2f} |")
    if damages.lost_rent_downtime > 0:
        notice.append(f"| **Future** | Lost Rent During Vacancy | ${damages.lost_rent_downtime:,.2f} |")

    # Re-leasing costs
    if damages.ti_costs > 0:
        notice.append(f"| **Re-leasing** | Tenant Improvements | ${damages.ti_costs:,.2f} |")
    if damages.leasing_commissions > 0:
        notice.append(f"| **Re-leasing** | Leasing Commissions | ${damages.leasing_commissions:,.2f} |")
    if damages.legal_fees > 0:
        notice.append(f"| **Re-leasing** | Legal Fees | ${damages.legal_fees:,.2f} |")

    notice.append(f"| | | |")
    notice.append(f"| **GROSS DAMAGES** | | **${damages.gross_damages:,.2f}** |")
    notice.append(f"")

    # Credits
    if damages.total_credits > 0:
        notice.append(f"### Credits and Mitigation")
        notice.append(f"")
        notice.append(f"| Category | Description | Amount |")
        notice.append(f"|----------|-------------|--------|")

        if damages.security_deposit_credit > 0:
            notice.append(f"| **Credit** | Security Deposit Applied | $(${damages.security_deposit_credit:,.2f}) |")
        if damages.re_lease_rent_credit_npv > 0:
            notice.append(f"| **Credit** | Re-lease Rent Credit (NPV) | $(${damages.re_lease_rent_credit_npv:,.2f}) |")

        notice.append(f"| | | |")
        notice.append(f"| **TOTAL CREDITS** | | **$(${damages.total_credits:,.2f})** |")
        notice.append(f"")

    # Net damages
    notice.append(f"### Net Damages Claimed")
    notice.append(f"")
    notice.append(f"| **NET DAMAGES** | | **${damages.net_damages:,.2f}** |")
    notice.append(f"")
    notice.append(f"---")
    notice.append(f"")

    # ========================================================================
    # CALCULATION NOTES
    # ========================================================================
    notice.append(f"### Calculation Methodology")
    notice.append(f"")
    notice.append(f"**Accelerated Rent**: Present value of remaining lease payments ({lease.remaining_months} months) discounted at {lease.discount_rate_annual:.1%} per annum.")
    notice.append(f"")
    notice.append(f"**Lost Rent During Vacancy**: Estimated {lease.downtime_months} months vacancy at current monthly rent of ${lease.current_monthly_rent:,.2f}.")
    notice.append(f"")
    notice.append(f"**Re-leasing Costs**: Tenant improvements (${lease.ti_allowance_sf:.2f}/SF × {lease.rentable_area_sf:,.0f} SF), leasing commissions ({lease.leasing_commission_pct:.1%} of new lease value), and legal fees.")
    notice.append(f"")
    notice.append(f"**Mitigation Credit**: Landlord has duty to mitigate damages by re-letting the Premises. Credit reflects present value of anticipated rent from new tenant.")
    notice.append(f"")
    notice.append(f"---")
    notice.append(f"")

    # ========================================================================
    # BANKRUPTCY SCENARIO
    # ========================================================================
    if results.bankruptcy_scenarios:
        bk = results.bankruptcy_scenarios[0]
        notice.append(f"## BANKRUPTCY CONSIDERATIONS")
        notice.append(f"")
        notice.append(f"If Tenant files for bankruptcy protection:")
        notice.append(f"")
        notice.append(f"- **Priority Claim (60 days)**: ${bk.priority_claim_60_days:,.2f}")
        notice.append(f"- **Unsecured Claim (§502(b)(6) cap)**: ${bk.unsecured_claim:,.2f}")
        notice.append(f"- **Expected Recovery** (at {bk.unsecured_recovery_rate:.0%} unsecured rate): ${bk.expected_recovery:,.2f}")
        notice.append(f"- **Expected Loss**: ${bk.expected_loss:,.2f}")
        notice.append(f"")
        notice.append(f"**Preference Period**: Payments made within {bk.preference_period_days} days of bankruptcy filing (approximately ${bk.payments_at_risk:,.2f}) may be subject to clawback as preferential transfers.")
        notice.append(f"")
        notice.append(f"---")
        notice.append(f"")

    # ========================================================================
    # RESERVATION OF RIGHTS
    # ========================================================================
    notice.append(f"## RESERVATION OF RIGHTS")
    notice.append(f"")
    notice.append(f"This Notice of Default is provided to you as required under the Lease. **Nothing in this notice shall be construed as a waiver of any of the Landlord's rights or remedies under the Lease, at law, or in equity.**")
    notice.append(f"")
    notice.append(f"The Landlord expressly reserves all rights and remedies, including without limitation:")
    notice.append(f"")
    notice.append(f"1. The right to terminate the Lease")
    notice.append(f"2. The right to re-enter and take possession of the Premises")
    notice.append(f"3. The right to pursue an action for damages")
    notice.append(f"4. The right to seek injunctive relief")
    notice.append(f"5. The right to apply security deposits and other credits")
    notice.append(f"6. All other rights and remedies available under the Lease or applicable law")
    notice.append(f"")
    notice.append(f"The damage amounts set forth above are preliminary estimates and do not constitute a limitation on the Landlord's actual damages, which may increase based on market conditions, actual re-leasing costs, and other factors.")
    notice.append(f"")
    notice.append(f"---")
    notice.append(f"")

    # ========================================================================
    # LEGAL CITATIONS
    # ========================================================================
    if jurisdiction == "Ontario":
        notice.append(f"## LEGAL FRAMEWORK")
        notice.append(f"")
        notice.append(f"This notice is provided pursuant to:")
        notice.append(f"")
        notice.append(f"- *Commercial Tenancies Act*, R.S.O. 1990, c. L.7, s. 19")
        notice.append(f"- Terms of the Lease")
        notice.append(f"- Common law principles of landlord and tenant")
        notice.append(f"")
        notice.append(f"Tenant is advised to seek independent legal counsel regarding this notice and your obligations under the Lease.")
        notice.append(f"")

    # ========================================================================
    # CONTACT INFORMATION
    # ========================================================================
    notice.append(f"---")
    notice.append(f"")
    notice.append(f"## CONTACT INFORMATION")
    notice.append(f"")
    notice.append(f"Questions regarding this notice should be directed to:")
    notice.append(f"")
    notice.append(f"**{lease.landlord_name}**")
    notice.append(f"")
    notice.append(f"[Property Manager Name]")
    notice.append(f"[Phone]")
    notice.append(f"[Email]")
    notice.append(f"")
    notice.append(f"---")
    notice.append(f"")
    notice.append(f"**Delivered**: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    notice.append(f"")
    notice.append(f"**Generated by**: Default Damage Calculator v1.0.0")
    notice.append(f"")

    return "\n".join(notice)


def main():
    """Command-line interface for notice generation"""
    if len(sys.argv) < 2:
        print("Usage: python notice_generator.py <input.json> [output.md] [jurisdiction]")
        print("\nExample:")
        print("  python notice_generator.py default_scenario.json")
        print("  python notice_generator.py default_scenario.json notice.md Ontario")
        sys.exit(1)

    input_path = sys.argv[1]
    jurisdiction = sys.argv[3] if len(sys.argv) > 3 else "Ontario"

    # Generate output path with timestamp
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
    else:
        timestamp = get_eastern_timestamp()
        tenant_name = Path(input_path).stem.replace("_", "-")
        output_path = f"../../Reports/{timestamp}_default_notice_{tenant_name}.md"

    print(f"Loading default scenario from: {input_path}")
    lease, default = load_default_scenario_from_json(input_path)

    print(f"Calculating damages...")
    results = calculate_default_damages(lease, default)

    print(f"Generating default notice...")
    notice = generate_default_notice(results, jurisdiction)

    # Ensure Reports directory exists
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"Saving notice to: {output_path}")
    with open(output_path, 'w') as f:
        f.write(notice)

    print(f"\n✅ Default notice generated successfully!")
    print(f"\nKey details:")
    print(f"  - Tenant: {lease.tenant_name}")
    print(f"  - Property: {lease.property_address}")
    print(f"  - Default: {default.default_type} ({default.default_date.strftime('%B %d, %Y')})")
    print(f"  - Net damages: ${results.damage_calculation.net_damages:,.2f}")
    print(f"  - Jurisdiction: {jurisdiction}")


if __name__ == '__main__':
    main()
