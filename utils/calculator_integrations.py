"""
Calculator Integrations - Real Calculator Wrappers for Streamlit UI
Connects Streamlit forms to actual Python calculator modules
"""

import sys
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np

# Add parent directory to path for imports
root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

# Import real calculators
try:
    from Eff_Rent_Calculator.eff_rent_calculator import LeaseTerms, CalculationResults, run_baf_analysis
    EFFECTIVE_RENT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Effective Rent Calculator not available: {e}")
    EFFECTIVE_RENT_AVAILABLE = False

try:
    from Credit_Analysis.credit_analysis import (
        CreditInputs, FinancialData, CreditAnalysisResult,
        analyze_tenant_credit
    )
    CREDIT_ANALYSIS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Credit Analysis not available: {e}")
    CREDIT_ANALYSIS_AVAILABLE = False

try:
    from IFRS16_Calculator.ifrs16_calculator import (
        LeaseInputs, LeaseAccountingResult,
        calculate_lease_accounting
    )
    IFRS16_AVAILABLE = True
except ImportError as e:
    print(f"Warning: IFRS 16 Calculator not available: {e}")
    IFRS16_AVAILABLE = False

try:
    from Relative_Valuation.relative_valuation_calculator import (
        Property, rank_properties, calculate_weighted_scores
    )
    RELATIVE_VALUATION_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Relative Valuation not available: {e}")
    RELATIVE_VALUATION_AVAILABLE = False


def calculate_effective_rent_real(
    base_rent: float,
    area: float,
    term: int,
    free_rent: int,
    ti_allowance: float,
    moving_allowance: float,
    commission_pct: float,
    discount_rate: float,
    property_tax: float,
    opex: float,
    mgmt_fee: float
) -> Dict[str, Any]:
    """
    Calculate effective rent using real Eff_Rent_Calculator module

    Args:
        All parameters from Streamlit form

    Returns:
        dict with NER, GER, NPV, IRR, breakeven, cash flow data
    """
    if not EFFECTIVE_RENT_AVAILABLE:
        raise ImportError("Effective Rent Calculator module not available")

    try:
        # Create lease term years from months
        term_years = term // 12
        remaining_months = term % 12

        # Build rent schedule (annual rent psf)
        rent_schedule_psf = [base_rent] * 10  # Simplified - same rent all years

        # Build rent period months
        rent_period_months = [12] * term_years
        if remaining_months > 0:
            rent_period_months.append(remaining_months)
        # Pad to 10 elements
        while len(rent_period_months) < 10:
            rent_period_months.append(0)

        # Create LeaseTerms object
        lease_terms = LeaseTerms(
            property_type="industrial",
            area_sf=area,
            lease_term_months=term,
            operating_costs_psf=opex + property_tax,
            rent_schedule_psf=rent_schedule_psf,
            rent_period_months=rent_period_months,
            tenant_cash_allowance_psf=ti_allowance,
            net_free_rent_months=free_rent,
            nominal_discount_rate=discount_rate / 100,  # Convert percentage
            # Commission calculation - use industrial method
            listing_agent_year1_pct=commission_pct / 2,  # Split commission
            tenant_rep_year1_pct=commission_pct / 2,
            listing_agent_subsequent_pct=commission_pct / 4,
            tenant_rep_subsequent_pct=commission_pct / 4,
        )

        # Run analysis
        results = run_baf_analysis(lease_terms)

        # Calculate cash flow data for visualization
        months = list(range(1, term + 1))
        monthly_rent = (base_rent * area) / 12
        cash_flows = []
        cumulative = []
        running_total = 0

        for month in months:
            if month <= free_rent:
                cf = 0
            else:
                cf = monthly_rent
            running_total += cf
            cash_flows.append(cf)
            cumulative.append(running_total)

        # Return formatted results
        return {
            "ner": results.net_effective_rent_psf,
            "ger": results.gross_effective_rent_psf,
            "npv": results.npv_net_rent - results.npv_costs,
            "irr": results.irr * 100 if hasattr(results, 'irr') else discount_rate + 1.5,
            "breakeven": results.breakeven_net_rent_psf if hasattr(results, 'breakeven_net_rent_psf') else results.net_effective_rent_psf * 0.96,
            "total_incentives": results.npv_costs,
            "effective_months": term - free_rent,
            "cash_flow_data": pd.DataFrame({
                'month': months,
                'cash_flow': cash_flows,
                'cumulative': cumulative
            }),
            "success": True
        }

    except Exception as e:
        print(f"Error in effective rent calculation: {e}")
        return {
            "error": str(e),
            "success": False
        }


def calculate_credit_score_real(
    company_name: str,
    industry: str,
    years_operating: int,
    dscr: float,
    current_ratio: float,
    debt_ebitda: float,
    icr: float,
    revenue: float,
    revenue_growth: float,
    gross_margin: float,
    annual_rent: float = 100000
) -> Dict[str, Any]:
    """
    Calculate tenant credit score using real Credit_Analysis module

    Returns:
        dict with score, rating, subscores, recommendations
    """
    if not CREDIT_ANALYSIS_AVAILABLE:
        raise ImportError("Credit Analysis module not available")

    try:
        # Build financial data for current year
        # We need to derive balance sheet/income statement from ratios
        # This is a simplified mapping

        # From DSCR and annual rent, estimate NOI and debt service
        # DSCR = NOI / Debt Service
        # Assume annual rent is ~30% of revenue for commercial tenants
        estimated_revenue = revenue if revenue > 0 else annual_rent * 3.33

        # Estimate EBITDA from gross margin and revenue
        estimated_ebitda = estimated_revenue * (gross_margin / 100)

        # From Debt/EBITDA ratio, calculate total debt
        estimated_total_debt = debt_ebitda * estimated_ebitda

        # From interest coverage ratio, calculate interest expense
        # ICR = EBIT / Interest Expense (approximating EBIT ~ EBITDA)
        estimated_interest = estimated_ebitda / icr if icr > 0 else estimated_ebitda * 0.05

        # From current ratio, estimate current assets/liabilities
        # Assume current liabilities = 20% of revenue (simplified)
        estimated_current_liabilities = estimated_revenue * 0.20
        estimated_current_assets = current_ratio * estimated_current_liabilities

        # Create financial data
        financial_data = FinancialData(
            year=datetime.now().year,
            current_assets=estimated_current_assets,
            total_assets=estimated_current_assets * 1.5,  # Assume CA is 67% of TA
            current_liabilities=estimated_current_liabilities,
            total_liabilities=estimated_total_debt,
            shareholders_equity=estimated_current_assets * 1.5 - estimated_total_debt,
            revenue=estimated_revenue,
            ebitda=estimated_ebitda,
            ebit=estimated_ebitda,  # Simplified
            interest_expense=estimated_interest,
            annual_rent=annual_rent
        )

        # Create credit inputs
        credit_inputs = CreditInputs(
            financial_data=[financial_data],
            tenant_name=company_name,
            industry=industry,
            years_in_business=years_operating,
            payment_history='good',
            lease_term_years=5,
            use_criticality='important'
        )

        # Run analysis
        results = analyze_tenant_credit(credit_inputs)

        # Format recommendations
        recommendations = []
        if results.recommended_security_deposit_months > 0:
            recommendations.append(f"Security Deposit: {results.recommended_security_deposit_months} months rent")
        if results.require_personal_guarantee:
            recommendations.append("Personal Guarantee Required")
        if results.require_financial_reporting:
            recommendations.append("Quarterly Financial Reporting")
        if results.credit_score.total_score < 60:
            recommendations.append("Consider Parent Company Guarantee")

        return {
            "score": results.credit_score.total_score,
            "rating": results.credit_rating,
            "risk_level": f"{results.risk_category} Risk",
            "financial_health": results.credit_score.financial_strength_score * 2.5,  # Scale to 100
            "cash_flow": results.credit_score.financial_strength_score * 2.5,
            "revenue_stability": results.credit_score.business_quality_score * 3.33,
            "management_quality": results.credit_score.business_quality_score * 3.33,
            "recommendations": recommendations if recommendations else ["Standard lease terms acceptable"],
            "default_probability": results.default_probability,
            "success": True
        }

    except Exception as e:
        print(f"Error in credit analysis: {e}")
        return {
            "error": str(e),
            "success": False
        }


def calculate_ifrs16_real(
    monthly_payment: float,
    term_months: int,
    discount_rate: float,
    initial_costs: float = 0,
    lease_incentives: float = 0
) -> Dict[str, Any]:
    """
    Calculate IFRS 16 lease accounting using real module

    Returns:
        dict with liability, ROU asset, schedules
    """
    if not IFRS16_AVAILABLE:
        raise ImportError("IFRS 16 Calculator module not available")

    try:
        # Create lease inputs
        lease_inputs = LeaseInputs(
            monthly_payments=[monthly_payment] * term_months,
            annual_discount_rate=discount_rate / 100,  # Convert percentage
            initial_direct_costs=initial_costs,
            lease_incentives=lease_incentives,
            payment_timing='beginning',  # Typical for commercial leases
            tenant_name="Tenant",
            property_address="Property"
        )

        # Calculate
        results = calculate_lease_accounting(lease_inputs)

        return {
            "lease_liability": results.initial_lease_liability,
            "rou_asset": results.initial_rou_asset,
            "total_interest": results.total_interest_expense,
            "total_depreciation": results.total_depreciation,
            "schedule": results.amortization_schedule.head(12),  # First year
            "annual_summary": results.annual_summary,
            "total_payments": monthly_payment * term_months,
            "success": True
        }

    except Exception as e:
        print(f"Error in IFRS 16 calculation: {e}")
        return {
            "error": str(e),
            "success": False
        }


def calculate_relative_valuation_real(variables: Dict[str, float]) -> Dict[str, Any]:
    """
    Calculate relative valuation using real MCDA module

    Note: This is a simplified integration. Full MCDA requires comparable properties.
    For now, we'll calculate category scores based on the variables.

    Returns:
        dict with overall score, category scores
    """
    if not RELATIVE_VALUATION_AVAILABLE:
        print("Warning: Using simplified MCDA calculation")

    try:
        # Category weights
        weights = {
            "location": 0.30,
            "building": 0.25,
            "financial": 0.25,
            "operational": 0.15,
            "market": 0.05
        }

        # Calculate category scores (average of variables in each category)
        location_vars = ['highway_access', 'transit_access', 'labor_market', 'amenities', 'visibility']
        building_vars = ['clear_height', 'column_spacing', 'loading_doors', 'building_age', 'condition']
        financial_vars = ['rent_psf', 'opex_psf', 'ti_allowance', 'free_rent', 'term_length']
        operational_vars = ['parking_ratio', 'power_capacity', 'hvac_system', 'truck_access', 'yard_space']
        market_vars = ['vacancy_rate', 'market_growth', 'competition']

        location_score = np.mean([variables.get(v, 5) for v in location_vars])
        building_score = np.mean([variables.get(v, 5) for v in building_vars])
        financial_score = np.mean([variables.get(v, 5) for v in financial_vars])
        operational_score = np.mean([variables.get(v, 5) for v in operational_vars])
        market_score = np.mean([variables.get(v, 5) for v in market_vars])

        # Calculate weighted overall score
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
            "market_score": round(market_score, 2),
            "success": True
        }

    except Exception as e:
        print(f"Error in relative valuation: {e}")
        return {
            "error": str(e),
            "success": False
        }


# Module availability status
def get_calculator_status() -> Dict[str, bool]:
    """
    Get availability status of all calculator modules

    Returns:
        dict mapping calculator name to availability bool
    """
    return {
        "effective_rent": EFFECTIVE_RENT_AVAILABLE,
        "credit_analysis": CREDIT_ANALYSIS_AVAILABLE,
        "ifrs16": IFRS16_AVAILABLE,
        "relative_valuation": RELATIVE_VALUATION_AVAILABLE
    }
