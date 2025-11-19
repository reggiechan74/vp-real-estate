"""
Dummy calculation functions for UI demonstration
These will be replaced with actual calculator integrations in Phase 2
"""

import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta


def calculate_effective_rent(base_rent, area, term, free_rent, ti_allowance,
                             moving_allowance, commission_pct, discount_rate,
                             property_tax, opex, mgmt_fee):
    """
    Placeholder for Effective Rent calculation

    Returns: dict with NER, GER, NPV, IRR, breakeven
    """
    time.sleep(1.5)  # Simulate processing

    # Mock calculations (simplified)
    total_ti = ti_allowance * area
    total_commission = (base_rent * area * (term / 12)) * (commission_pct / 100)
    total_incentives = total_ti + moving_allowance + total_commission

    # Free rent impact
    effective_months = term - free_rent
    annual_rent = base_rent * area
    total_rent = annual_rent * (term / 12)

    # Net Effective Rent (simplified)
    ner = (total_rent - total_incentives) / area / (term / 12)
    ger = total_rent / area / (term / 12)

    # NPV (very simplified)
    npv = total_rent / ((1 + discount_rate / 100) ** (term / 12))

    # IRR (mock calculation)
    irr = discount_rate + np.random.uniform(1.0, 2.5)

    # Breakeven
    breakeven = ner * 0.96

    return {
        "ner": round(ner, 2),
        "ger": round(ger, 2),
        "npv": round(npv, 2),
        "irr": round(irr, 2),
        "breakeven": round(breakeven, 2),
        "total_incentives": round(total_incentives, 2),
        "effective_months": effective_months
    }


def generate_cash_flow_data(base_rent, area, term, free_rent):
    """
    Generate monthly cash flow data for visualization

    Returns: DataFrame with month, cash_flow, cumulative
    """
    months = list(range(1, term + 1))
    cash_flows = []
    cumulative = []

    monthly_rent = (base_rent * area) / 12
    running_total = 0

    for month in months:
        if month <= free_rent:
            cf = 0
        else:
            cf = monthly_rent

        running_total += cf
        cash_flows.append(cf)
        cumulative.append(running_total)

    return pd.DataFrame({
        'month': months,
        'cash_flow': cash_flows,
        'cumulative': cumulative
    })


def calculate_credit_score(dscr, current_ratio, debt_ebitda, revenue_growth,
                           gross_margin, years_operating, industry):
    """
    Placeholder for Tenant Credit Analysis

    Returns: dict with score, rating, subscores, recommendations
    """
    time.sleep(1.2)

    # Weighted scoring (simplified)
    financial_health = min((dscr * 20) + (current_ratio * 10), 100)
    cash_flow_score = min(dscr * 15, 100)
    revenue_stability = min((revenue_growth * 0.5) + (gross_margin * 0.3), 100)
    management_score = min(years_operating * 5, 100)

    # Overall score
    overall_score = (
        financial_health * 0.30 +
        cash_flow_score * 0.25 +
        revenue_stability * 0.25 +
        management_score * 0.20
    )

    # Rating
    if overall_score >= 80:
        rating = "A"
        risk_level = "Low Risk"
    elif overall_score >= 60:
        rating = "B"
        risk_level = "Acceptable Risk"
    elif overall_score >= 40:
        rating = "C"
        risk_level = "Elevated Risk"
    else:
        rating = "D"
        risk_level = "High Risk"

    # Recommendations
    recommendations = []
    if overall_score < 70:
        recommendations.append("Personal Guarantee Required")
    if dscr < 1.5:
        recommendations.append(f"Security Deposit: {6 if dscr < 1.25 else 3} months rent")
    if overall_score < 60:
        recommendations.append("Quarterly Financial Reporting")
        recommendations.append("Consider Parent Company Guarantee")
    if revenue_growth < 5:
        recommendations.append("Monitor revenue trends closely")

    return {
        "score": round(overall_score, 1),
        "rating": rating,
        "risk_level": risk_level,
        "financial_health": round(financial_health, 1),
        "cash_flow": round(cash_flow_score, 1),
        "revenue_stability": round(revenue_stability, 1),
        "management_quality": round(management_score, 1),
        "recommendations": recommendations
    }


def run_lease_abstraction(uploaded_file, lease_type):
    """
    Placeholder for Lease Abstraction (24 sections)

    Returns: dict with all 24 sections
    """
    time.sleep(2.5)

    abstract = {
        "1. Basic Information": {
            "Landlord": "ABC Properties Inc.",
            "Tenant": "XYZ Corporation",
            "Property Address": "123 Industrial Parkway, City, State 12345",
            "Lease Type": lease_type,
            "Commencement Date": "2025-01-01",
            "Expiry Date": "2030-12-31",
            "Lease Term": "60 months (5 years)"
        },
        "2. Premises": {
            "Rentable Area": "10,000 SF",
            "Measurement Standard": "BOMA Method A" if lease_type == "Industrial" else "BOMA Office Standard",
            "Use Clause": "Warehousing, distribution, and ancillary office use",
            "Exclusivity": "None"
        },
        "3. Rent Schedule": {
            "Year 1-2": "$25.00/SF ($250,000/year)",
            "Year 3-4": "$26.25/SF ($262,500/year)",
            "Year 5": "$27.50/SF ($275,000/year)",
            "Escalation Type": "Fixed annual increases",
            "Payment": "Monthly in advance on the 1st"
        },
        "4. Additional Rent": {
            "Operating Expenses": "Proportionate share of actual costs",
            "Property Taxes": "Proportionate share of actual taxes",
            "Utilities": "Tenant pays directly",
            "Base Year": "N/A (Net lease)",
            "CAP": "None"
        },
        "5. Proportionate Share": {
            "Calculation": "10,000 SF / 50,000 SF Total",
            "Percentage": "20%",
            "Basis": "Rentable Area"
        },
        "6. Security Deposit": {
            "Amount": "$25,000 (1 month base rent)",
            "Form": "Cash",
            "Return Conditions": "Within 30 days of expiry, less deductions",
            "Interest": "Non-interest bearing"
        },
        "7. Tenant Improvements": {
            "TI Allowance": "$25/SF ($250,000 total)",
            "Landlord Work": "Base building delivered as-is",
            "Tenant Work": "All improvements per approved plans",
            "Approval Process": "Plans require landlord approval (15 business days)",
            "Excess Costs": "Tenant responsible"
        },
        "8. Renewal Options": {
            "Number of Options": "2 options",
            "Term": "5 years each",
            "Notice Period": "12 months prior to expiry",
            "Rent": "Fair Market Value (FMV), arbitration if no agreement",
            "Other Terms": "Same terms and conditions"
        },
        "9. Expansion Options": {
            "Right": "ROFR on adjacent 5,000 SF unit",
            "Notice": "10 business days to match third-party offer",
            "Conditions": "No default, same lease terms"
        },
        "10. Termination Options": {
            "Early Termination": "None",
            "Kick-out Clause": "N/A",
            "Other": "Standard default remedies only"
        },
        "11. Assignment & Subletting": {
            "Assignment": "Permitted with landlord consent (not unreasonably withheld)",
            "Subletting": "Permitted with landlord consent",
            "Recapture Rights": "Landlord may recapture if >50% of premises subleased",
            "Profit Sharing": "50/50 split of excess rent",
            "Conditions": "Tenant remains liable, assignee creditworthy"
        },
        "12. Use Restrictions": {
            "Permitted Use": "Warehousing, distribution, light assembly",
            "Prohibited Uses": "Hazardous materials (except de minimis), noxious activities",
            "Hours": "24/7 access permitted",
            "Compliance": "All laws and regulations"
        },
        "13. Exclusivity Clauses": {
            "Tenant Exclusivity": "None",
            "Landlord Restrictions": "None",
            "Radius Restrictions": "N/A"
        },
        "14. Parking": {
            "Spaces": "20 spaces (2 per 1,000 SF)",
            "Location": "Surface lot adjacent to building",
            "Cost": "Included in base rent",
            "Reserved": "2 executive spaces reserved"
        },
        "15. Signage": {
            "Exterior": "Building directory and monument sign (proportionate share of cost)",
            "Interior": "At tenant's expense per building standards",
            "Approval": "Landlord approval required for all signage"
        },
        "16. Insurance Requirements": {
            "CGL": "$5,000,000 occurrence / $5,000,000 aggregate",
            "Property": "Replacement cost coverage for tenant improvements and contents",
            "Business Interruption": "12 months coverage",
            "Additional Insured": "Landlord and property manager",
            "Proof": "Certificates due 10 days before commencement"
        },
        "17. Environmental Obligations": {
            "Tenant Obligations": "No hazardous materials except de minimis office supplies",
            "Environmental Audit": "Phase I ESA required at tenant's cost if requested",
            "Indemnity": "Tenant indemnifies landlord for tenant-caused contamination",
            "Reporting": "Immediate notice of spills or releases"
        },
        "18. Default Provisions": {
            "Monetary Default": "5 business days to cure after notice",
            "Non-Monetary Default": "30 days to cure (10 days for hazardous conditions)",
            "Notice Requirements": "Written notice to tenant's address",
            "Persistent Breach": "3+ defaults in 12 months = immediate termination right"
        },
        "19. Remedies": {
            "Landlord Remedies": "Termination, re-entry, distress, damages, acceleration",
            "Tenant Damages": "Unamortized TI, leasing costs, re-leasing costs, rent differential",
            "Mitigation": "Landlord required to mitigate damages",
            "Legal Fees": "Prevailing party recovers legal costs"
        },
        "20. Indemnification": {
            "Tenant Indemnity": "Tenant indemnifies landlord for claims arising from tenant's use",
            "Landlord Indemnity": "Limited to gross negligence or willful misconduct",
            "Insurance": "Indemnity backed by insurance requirements",
            "Survival": "Indemnity survives lease termination"
        },
        "21. SNDA": {
            "Subordination": "Lease subordinate to existing and future mortgages",
            "Non-Disturbance": "Tenant entitled to SNDA from lender",
            "Attornment": "Tenant attorns to purchaser/lender upon foreclosure",
            "Estoppel": "Tenant provides estoppel within 10 business days"
        },
        "22. Critical Dates": {
            "Commencement": "2025-01-01",
            "First Rent Payment": "2025-01-01",
            "Free Rent Ends": "2025-03-31 (3 months)",
            "First Renewal Notice": "2028-12-31 (12 months before expiry)",
            "Lease Expiry": "2030-12-31"
        },
        "23. Special Provisions (Schedule G)": {
            "Custom Terms": [
                "Rent abatement: 3 months at commencement",
                "Landlord to repair roof (estimate $50K) before occupancy",
                "Tenant may install 10-ton crane at tenant's cost",
                "Property manager: ABC Property Management (5% fee)",
                "Landlord's approval timelines: 15 business days (deemed approved if no response)"
            ]
        },
        "24. Exhibits/Schedules": {
            "Schedule A": "Legal Description",
            "Schedule B": "Site Plan",
            "Schedule C": "Work Letter / TI Specifications",
            "Schedule D": "Deposit Terms (Letter of Credit)",
            "Schedule E": "Environmental Compliance Certificate",
            "Schedule F": "Rules and Regulations",
            "Schedule G": "Special Provisions (see above)",
            "Schedule H": "Indemnity Agreement (Personal Guarantee)",
            "Schedule I": "Pre-Authorized Debit Form",
            "Schedule J": "Letter of Credit Terms"
        }
    }

    return abstract


def compare_documents(doc1_name, doc2_name, comparison_type):
    """
    Placeholder for Document Comparison

    Returns: list of differences with impact analysis
    """
    time.sleep(1.8)

    differences = [
        {
            "section": "Base Rent",
            "document_a": "$25.00/SF",
            "document_b": "$27.00/SF",
            "change": "+$2.00/SF (+8%)",
            "impact": "Positive - Rent increase of $20,000/year",
            "severity": "medium"
        },
        {
            "section": "Lease Term",
            "document_a": "5 years",
            "document_b": "7 years",
            "change": "+2 years",
            "impact": "Requires board approval - Extended lease commitment",
            "severity": "high"
        },
        {
            "section": "Free Rent",
            "document_a": "2 months",
            "document_b": "3 months",
            "change": "+1 month",
            "impact": "Negative - Additional $22,500 rent abatement",
            "severity": "medium"
        },
        {
            "section": "TI Allowance",
            "document_a": "$20/SF",
            "document_b": "$25/SF",
            "change": "+$5/SF",
            "impact": "Negative - Additional $50,000 capital required",
            "severity": "high"
        },
        {
            "section": "Security Deposit",
            "document_a": "3 months rent",
            "document_b": "1 month rent",
            "change": "-2 months",
            "impact": "Negative - Reduced security by $50,000",
            "severity": "medium"
        },
        {
            "section": "Renewal Options",
            "document_a": "1 x 5 years",
            "document_b": "2 x 5 years",
            "change": "+1 option",
            "impact": "Positive - Enhanced tenant retention potential",
            "severity": "low"
        }
    ]

    return differences


def calculate_ifrs16(lease_payments, discount_rate, term_months):
    """
    Placeholder for IFRS 16 / ASC 842 Calculation

    Returns: dict with liability, ROU asset, amortization schedule
    """
    time.sleep(2.0)

    # Simple present value calculation
    monthly_rate = discount_rate / 100 / 12
    periods = term_months

    # Calculate lease liability (PV of payments)
    if isinstance(lease_payments, (int, float)):
        monthly_payment = lease_payments
    else:
        monthly_payment = lease_payments[0] if lease_payments else 25000

    # PV calculation
    pv = monthly_payment * ((1 - (1 + monthly_rate) ** -periods) / monthly_rate)

    lease_liability = round(pv, 2)
    rou_asset = lease_liability  # Simplified - normally includes initial costs

    # Generate amortization schedule
    schedule = []
    balance = lease_liability

    for month in range(1, min(13, periods + 1)):  # First 12 months
        interest = balance * monthly_rate
        principal = monthly_payment - interest
        balance -= principal

        schedule.append({
            "Month": month,
            "Payment": round(monthly_payment, 2),
            "Interest": round(interest, 2),
            "Principal": round(principal, 2),
            "Balance": round(balance, 2)
        })

    return {
        "lease_liability": lease_liability,
        "rou_asset": rou_asset,
        "schedule": pd.DataFrame(schedule),
        "total_payments": monthly_payment * periods,
        "total_interest": (monthly_payment * periods) - lease_liability
    }


def calculate_relative_valuation(variables):
    """
    Placeholder for Relative Valuation (MCDA)

    Args:
        variables: dict of variable scores (0-10)

    Returns: dict with overall score, category scores, rankings
    """
    time.sleep(1.0)

    # Category weights
    weights = {
        "location": 0.30,
        "building": 0.25,
        "financial": 0.25,
        "operational": 0.15,
        "market": 0.05
    }

    # Calculate category scores
    location_score = np.mean([
        variables.get("highway_access", 5),
        variables.get("transit_access", 5),
        variables.get("labor_market", 5),
        variables.get("amenities", 5),
        variables.get("visibility", 5)
    ])

    building_score = np.mean([
        variables.get("clear_height", 5),
        variables.get("column_spacing", 5),
        variables.get("loading_doors", 5),
        variables.get("building_age", 5),
        variables.get("condition", 5)
    ])

    financial_score = np.mean([
        variables.get("rent_psf", 5),
        variables.get("opex_psf", 5),
        variables.get("ti_allowance", 5),
        variables.get("free_rent", 5),
        variables.get("term_length", 5)
    ])

    operational_score = np.mean([
        variables.get("parking_ratio", 5),
        variables.get("power_capacity", 5),
        variables.get("hvac_system", 5),
        variables.get("truck_access", 5),
        variables.get("yard_space", 5)
    ])

    market_score = np.mean([
        variables.get("vacancy_rate", 5),
        variables.get("market_growth", 5),
        variables.get("competition", 5)
    ])

    # Overall weighted score
    overall = (
        location_score * weights["location"] +
        building_score * weights["building"] +
        financial_score * weights["financial"] +
        operational_score * weights["operational"] +
        market_score * weights["market"]
    )

    # Market position
    if overall >= 8.0:
        position = "Premium"
    elif overall >= 6.5:
        position = "Above Average"
    elif overall >= 5.0:
        position = "Average"
    else:
        position = "Below Average"

    return {
        "overall_score": round(overall, 2),
        "market_position": position,
        "location_score": round(location_score, 2),
        "building_score": round(building_score, 2),
        "financial_score": round(financial_score, 2),
        "operational_score": round(operational_score, 2),
        "market_score": round(market_score, 2)
    }


def analyze_default(lease_data, default_description):
    """
    Placeholder for Default Analysis

    Returns: dict with cure period, remedies, damages
    """
    time.sleep(1.5)

    # Determine default type
    is_monetary = any(word in default_description.lower() for word in ['rent', 'payment', 'money', 'pay'])

    cure_days = 5 if is_monetary else 30

    remedies = [
        "Termination of Lease",
        "Re-entry and Possession",
        "Distress (seizure of assets)",
        "Sue for Damages",
        "Acceleration of Rent"
    ]

    # Mock damage calculation
    monthly_rent = 25000
    remaining_months = 24

    damages = {
        "Unamortized TI": 150000,
        "Leasing Commissions": 30000,
        "Re-leasing Costs": 25000,
        "Rent Differential (2 years)": monthly_rent * 12 * 0.15,  # 15% below market
        "Total Estimated Damages": 0
    }
    damages["Total Estimated Damages"] = sum(damages.values())

    return {
        "default_type": "Monetary Default" if is_monetary else "Non-Monetary Default",
        "cure_period_days": cure_days,
        "cure_deadline": (datetime.now() + timedelta(days=cure_days)).strftime("%Y-%m-%d"),
        "available_remedies": remedies,
        "estimated_damages": damages,
        "litigation_risk": "Medium - Tenant may dispute or delay" if not is_monetary else "Low - Clear payment default"
    }
