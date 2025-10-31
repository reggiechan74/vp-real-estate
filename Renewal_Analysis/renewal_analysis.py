"""
Renewal Economics Calculator

Performs comprehensive financial analysis comparing lease renewal vs. relocation.
Calculates NPV, IRR, NER, breakeven points, and provides investment recommendations.

Key Features:
- NPV analysis for both renewal and relocation scenarios
- Net Effective Rent (NER) calculation
- Internal Rate of Return (IRR) for relocation investment
- Breakeven analysis (solve for rent equality)
- Payback period calculation
- Sensitivity analysis on key variables
- Investment recommendation

Author: Claude Code
Created: 2025-10-30
GitHub Issue: #5
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Literal
from dataclasses import dataclass
import sys
import os

# Import financial utilities from Shared_Utils
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Shared_Utils'))
from financial_utils import (
    npv,
    irr,
    annual_to_monthly_rate,
    annuity_factor,
    safe_divide
)


@dataclass
class RenewalScenario:
    """
    Input parameters for lease renewal scenario.
    """
    # Rent schedule
    annual_rent_psf: List[float]  # Annual rent $/sf for each year

    # Tenant improvements
    ti_allowance_psf: float = 0.0      # TI allowance from landlord ($/sf)
    additional_ti_psf: float = 0.0      # Additional TI required ($/sf)

    # Term
    term_years: int = 5

    # Operating costs (if not included in rent)
    operating_costs_psf: float = 0.0   # Annual operating costs ($/sf)

    # Other renewal costs
    legal_fees: float = 0.0             # Legal fees for renewal
    renovation_costs_psf: float = 0.0   # Refresh/renovation costs ($/sf)

    # Metadata
    scenario_name: str = "Renewal"


@dataclass
class RelocationScenario:
    """
    Input parameters for relocation scenario.
    """
    # Rent schedule
    annual_rent_psf: List[float]  # Annual rent $/sf for each year

    # Tenant improvements
    ti_allowance_psf: float = 0.0       # TI allowance from landlord ($/sf)
    ti_requirement_psf: float = 0.0     # TI required for new space ($/sf)

    # Term
    term_years: int = 5

    # Operating costs (if not included in rent)
    operating_costs_psf: float = 0.0   # Annual operating costs ($/sf)

    # Relocation-specific costs
    moving_costs: float = 0.0           # Physical moving costs ($)
    it_moving_costs: float = 0.0        # IT/telecom relocation ($)
    signage_costs: float = 0.0          # New signage ($)

    # Disruption costs
    downtime_days: float = 0.0          # Business downtime (days)
    daily_revenue: float = 0.0          # Average daily revenue ($)
    customer_loss_pct: float = 0.0      # % of customers lost during move

    # Abandonment costs
    unamortized_improvements: float = 0.0  # Improvements abandoned at old location ($)
    restoration_costs: float = 0.0         # Cost to restore old premises ($)

    # Leasing costs
    legal_fees: float = 0.0             # Legal fees for new lease
    due_diligence_costs: float = 0.0    # Site surveys, environmental, etc.
    broker_fees: float = 0.0            # If tenant pays broker

    # Metadata
    scenario_name: str = "Relocation"


@dataclass
class GeneralInputs:
    """
    General parameters for both scenarios.
    """
    rentable_area_sf: float             # Rentable area (sf)
    discount_rate: float = 0.10         # Annual discount rate (10% default)
    current_rent_psf: float = 0.0       # Current rent for comparison ($/sf)
    market_rent_psf: float = 0.0        # Current market rent ($/sf)


@dataclass
class ScenarioResult:
    """
    Results for a single scenario (renewal or relocation).
    """
    scenario_name: str

    # NPV components
    total_rent_payments: float          # Total rent over term
    total_operating_costs: float        # Total operating costs
    total_ti_costs: float               # Total TI costs (net of allowance)
    total_other_costs: float            # Legal, moving, disruption, etc.
    total_cash_outflows: float          # Sum of all costs

    # Present value analysis
    pv_rent: float                      # PV of rent payments
    pv_operating_costs: float           # PV of operating costs
    pv_ti_costs: float                  # PV of TI costs
    pv_other_costs: float               # PV of other costs
    npv: float                          # Total NPV of scenario

    # Effective rent
    net_effective_rent_psf: float       # NER ($/sf/year)
    gross_effective_rent_psf: float     # GER including operating costs

    # Cash flows
    annual_cash_flows: List[float]      # Annual cash outflows

    # Detailed breakdown
    cost_breakdown: Dict[str, float]


@dataclass
class ComparisonResult:
    """
    Comparison of renewal vs. relocation scenarios.
    """
    renewal_result: ScenarioResult
    relocation_result: ScenarioResult

    # Comparison metrics
    npv_difference: float               # Relocation NPV - Renewal NPV (negative = relocation costs more)
    ner_difference_psf: float           # Relocation NER - Renewal NER

    # Investment metrics
    relocation_irr: Optional[float]     # IRR of relocation investment
    payback_period_years: Optional[float]  # Years to recover relocation costs
    annual_savings: float               # Annual cash flow savings (if positive)

    # Breakeven analysis
    breakeven_rent_psf: Optional[float]  # Renewal rent at which NPVs are equal
    current_margin_psf: Optional[float]  # Buffer in current renewal offer

    # Recommendation
    recommendation: Literal['RENEW', 'RELOCATE', 'NEGOTIATE']
    recommendation_notes: str


# ============================================================================
# SCENARIO CALCULATIONS
# ============================================================================

def calculate_renewal_scenario(
    renewal: RenewalScenario,
    general: GeneralInputs
) -> ScenarioResult:
    """
    Calculate NPV and effective rent for renewal scenario.

    Args:
        renewal: Renewal scenario parameters
        general: General parameters

    Returns:
        ScenarioResult with NPV, NER, and cost breakdown
    """
    area = general.rentable_area_sf
    years = renewal.term_years
    rate = general.discount_rate

    # Calculate annual cash flows
    annual_cash_flows = []
    total_rent = 0.0
    total_op_costs = 0.0

    for year in range(years):
        # Get rent for this year
        if year < len(renewal.annual_rent_psf):
            rent_psf = renewal.annual_rent_psf[year]
        else:
            # Use last year's rent if schedule doesn't extend full term
            rent_psf = renewal.annual_rent_psf[-1]

        rent_payment = rent_psf * area
        op_costs = renewal.operating_costs_psf * area

        annual_cash_flow = rent_payment + op_costs
        annual_cash_flows.append(annual_cash_flow)

        total_rent += rent_payment
        total_op_costs += op_costs

    # TI costs (upfront at year 0)
    net_ti_psf = renewal.additional_ti_psf - renewal.ti_allowance_psf
    net_ti_cost = max(0, net_ti_psf * area)
    renovation_cost = renewal.renovation_costs_psf * area
    total_ti = net_ti_cost + renovation_cost

    # Other costs
    other_costs = renewal.legal_fees

    # Total cash outflows
    total_cash = total_rent + total_op_costs + total_ti + other_costs

    # Calculate present values
    # Rent and operating costs: annualized cash flows
    pv_cash_flows = npv(annual_cash_flows, rate)

    # Split into rent and operating costs proportionally
    if (total_rent + total_op_costs) > 0:
        rent_fraction = total_rent / (total_rent + total_op_costs)
        pv_rent = pv_cash_flows * rent_fraction
        pv_op_costs = pv_cash_flows * (1 - rent_fraction)
    else:
        pv_rent = 0.0
        pv_op_costs = 0.0

    # TI and other costs at t=0 (no discounting needed)
    pv_ti = total_ti
    pv_other = other_costs

    # Total NPV (all costs are positive outflows)
    total_npv = pv_rent + pv_op_costs + pv_ti + pv_other

    # Calculate NER
    # NER = NPV / area / annuity_factor
    monthly_rate = annual_to_monthly_rate(rate)
    af = annuity_factor(monthly_rate, years * 12)
    ner_psf = total_npv / area / af if area > 0 and af > 0 else 0.0

    # GER includes operating costs
    ger_psf = ner_psf  # Already included in NPV

    # Cost breakdown
    breakdown = {
        'rent_payments': total_rent,
        'operating_costs': total_op_costs,
        'ti_costs': total_ti,
        'legal_fees': renewal.legal_fees,
        'renovation_costs': renovation_cost,
        'total': total_cash
    }

    return ScenarioResult(
        scenario_name=renewal.scenario_name,
        total_rent_payments=total_rent,
        total_operating_costs=total_op_costs,
        total_ti_costs=total_ti,
        total_other_costs=other_costs,
        total_cash_outflows=total_cash,
        pv_rent=pv_rent,
        pv_operating_costs=pv_op_costs,
        pv_ti_costs=pv_ti,
        pv_other_costs=pv_other,
        npv=total_npv,
        net_effective_rent_psf=ner_psf,
        gross_effective_rent_psf=ger_psf,
        annual_cash_flows=annual_cash_flows,
        cost_breakdown=breakdown
    )


def calculate_relocation_scenario(
    relocation: RelocationScenario,
    general: GeneralInputs
) -> ScenarioResult:
    """
    Calculate NPV and effective rent for relocation scenario.

    Args:
        relocation: Relocation scenario parameters
        general: General parameters

    Returns:
        ScenarioResult with NPV, NER, and cost breakdown
    """
    area = general.rentable_area_sf
    years = relocation.term_years
    rate = general.discount_rate

    # Calculate annual cash flows (rent + operating costs)
    annual_cash_flows = []
    total_rent = 0.0
    total_op_costs = 0.0

    for year in range(years):
        # Get rent for this year
        if year < len(relocation.annual_rent_psf):
            rent_psf = relocation.annual_rent_psf[year]
        else:
            rent_psf = relocation.annual_rent_psf[-1]

        rent_payment = rent_psf * area
        op_costs = relocation.operating_costs_psf * area

        annual_cash_flow = rent_payment + op_costs
        annual_cash_flows.append(annual_cash_flow)

        total_rent += rent_payment
        total_op_costs += op_costs

    # TI costs (upfront at year 0)
    net_ti_psf = relocation.ti_requirement_psf - relocation.ti_allowance_psf
    net_ti_cost = max(0, net_ti_psf * area)

    # Moving costs
    moving_cost_total = (
        relocation.moving_costs +
        relocation.it_moving_costs +
        relocation.signage_costs
    )

    # Disruption costs
    disruption_cost = (
        relocation.downtime_days * relocation.daily_revenue +
        relocation.customer_loss_pct * relocation.daily_revenue * 365  # Annual revenue * loss %
    )

    # Abandonment costs
    abandonment_cost = (
        relocation.unamortized_improvements +
        relocation.restoration_costs
    )

    # Leasing costs
    leasing_cost = (
        relocation.legal_fees +
        relocation.due_diligence_costs +
        relocation.broker_fees
    )

    # Total upfront costs
    total_upfront = (
        net_ti_cost +
        moving_cost_total +
        disruption_cost +
        abandonment_cost +
        leasing_cost
    )

    total_ti = net_ti_cost
    total_other = total_upfront - total_ti

    # Total cash outflows
    total_cash = total_rent + total_op_costs + total_upfront

    # Calculate present values
    pv_cash_flows = npv(annual_cash_flows, rate)

    # Split into rent and operating costs
    if (total_rent + total_op_costs) > 0:
        rent_fraction = total_rent / (total_rent + total_op_costs)
        pv_rent = pv_cash_flows * rent_fraction
        pv_op_costs = pv_cash_flows * (1 - rent_fraction)
    else:
        pv_rent = 0.0
        pv_op_costs = 0.0

    # Upfront costs at t=0 (no discounting)
    pv_ti = total_ti
    pv_other = total_other

    # Total NPV
    total_npv = pv_rent + pv_op_costs + pv_ti + pv_other

    # Calculate NER
    monthly_rate = annual_to_monthly_rate(rate)
    af = annuity_factor(monthly_rate, years * 12)
    ner_psf = total_npv / area / af if area > 0 and af > 0 else 0.0

    ger_psf = ner_psf

    # Cost breakdown
    breakdown = {
        'rent_payments': total_rent,
        'operating_costs': total_op_costs,
        'ti_costs': net_ti_cost,
        'moving_costs': moving_cost_total,
        'disruption_costs': disruption_cost,
        'abandonment_costs': abandonment_cost,
        'leasing_costs': leasing_cost,
        'total': total_cash
    }

    return ScenarioResult(
        scenario_name=relocation.scenario_name,
        total_rent_payments=total_rent,
        total_operating_costs=total_op_costs,
        total_ti_costs=total_ti,
        total_other_costs=total_other,
        total_cash_outflows=total_cash,
        pv_rent=pv_rent,
        pv_operating_costs=pv_op_costs,
        pv_ti_costs=pv_ti,
        pv_other_costs=pv_other,
        npv=total_npv,
        net_effective_rent_psf=ner_psf,
        gross_effective_rent_psf=ger_psf,
        annual_cash_flows=annual_cash_flows,
        cost_breakdown=breakdown
    )


# ============================================================================
# COMPARISON AND ANALYSIS
# ============================================================================

def compare_scenarios(
    renewal: RenewalScenario,
    relocation: RelocationScenario,
    general: GeneralInputs
) -> ComparisonResult:
    """
    Compare renewal vs. relocation scenarios.

    Args:
        renewal: Renewal scenario
        relocation: Relocation scenario
        general: General parameters

    Returns:
        ComparisonResult with comparison metrics and recommendation
    """
    # Calculate both scenarios
    renewal_result = calculate_renewal_scenario(renewal, general)
    relocation_result = calculate_relocation_scenario(relocation, general)

    # NPV difference (negative = relocation costs more)
    npv_diff = relocation_result.npv - renewal_result.npv

    # NER difference
    ner_diff = relocation_result.net_effective_rent_psf - renewal_result.net_effective_rent_psf

    # Calculate IRR of relocation investment
    # IRR: Initial outlay = upfront relocation costs, annual savings = difference in cash flows
    relocation_upfront = (
        relocation_result.total_ti_costs +
        relocation_result.total_other_costs
    )

    # Annual cash flow difference (renewal cash flow - relocation cash flow)
    # Negative = relocation saves money
    annual_diff_flows = []
    max_years = max(len(renewal_result.annual_cash_flows), len(relocation_result.annual_cash_flows))

    for year in range(max_years):
        renewal_cf = renewal_result.annual_cash_flows[year] if year < len(renewal_result.annual_cash_flows) else 0
        reloc_cf = relocation_result.annual_cash_flows[year] if year < len(relocation_result.annual_cash_flows) else 0
        annual_diff_flows.append(renewal_cf - reloc_cf)

    # Calculate average annual savings
    annual_savings = np.mean(annual_diff_flows) if annual_diff_flows else 0.0

    # IRR calculation: [-upfront, +savings year 1, +savings year 2, ...]
    irr_cash_flows = [-relocation_upfront] + annual_diff_flows

    try:
        relocation_irr = irr(irr_cash_flows) if relocation_upfront > 0 else None
    except:
        relocation_irr = None

    # Payback period
    if annual_savings > 0:
        payback_years = relocation_upfront / annual_savings
    else:
        payback_years = None  # Never pays back

    # Breakeven analysis
    # Solve for renewal rent where NPV(renewal) = NPV(relocation)
    breakeven_rent = calculate_breakeven_rent(renewal, relocation, general)

    # Current margin (if breakeven calculated)
    if breakeven_rent is not None and len(renewal.annual_rent_psf) > 0:
        current_margin = renewal.annual_rent_psf[0] - breakeven_rent
    else:
        current_margin = None

    # Generate recommendation
    recommendation, notes = generate_recommendation(
        renewal_result,
        relocation_result,
        npv_diff,
        annual_savings,
        relocation_irr,
        payback_years
    )

    return ComparisonResult(
        renewal_result=renewal_result,
        relocation_result=relocation_result,
        npv_difference=npv_diff,
        ner_difference_psf=ner_diff,
        relocation_irr=relocation_irr,
        payback_period_years=payback_years,
        annual_savings=annual_savings,
        breakeven_rent_psf=breakeven_rent,
        current_margin_psf=current_margin,
        recommendation=recommendation,
        recommendation_notes=notes
    )


def calculate_breakeven_rent(
    renewal: RenewalScenario,
    relocation: RelocationScenario,
    general: GeneralInputs
) -> Optional[float]:
    """
    Calculate renewal rent ($/sf) where NPV(renewal) = NPV(relocation).

    Uses binary search to find breakeven rent.

    Args:
        renewal: Renewal scenario
        relocation: Relocation scenario
        general: General parameters

    Returns:
        Breakeven rent ($/sf) or None if not found
    """
    # Calculate relocation NPV (fixed)
    reloc_result = calculate_relocation_scenario(relocation, general)
    target_npv = reloc_result.npv

    # Binary search for breakeven rent
    # Assume constant rent (use first year as template)
    low_rent = 0.0
    high_rent = 200.0  # $200/sf should be high enough for most cases
    tolerance = 0.001  # Tighter tolerance for better convergence
    max_iterations = 200  # More iterations for convergence

    for iteration in range(max_iterations):
        mid_rent = (low_rent + high_rent) / 2

        # Create test renewal scenario with mid_rent
        test_renewal = RenewalScenario(
            annual_rent_psf=[mid_rent] * renewal.term_years,
            ti_allowance_psf=renewal.ti_allowance_psf,
            additional_ti_psf=renewal.additional_ti_psf,
            term_years=renewal.term_years,
            operating_costs_psf=renewal.operating_costs_psf,
            legal_fees=renewal.legal_fees,
            renovation_costs_psf=renewal.renovation_costs_psf
        )

        test_result = calculate_renewal_scenario(test_renewal, general)

        # Check if close enough
        if abs(test_result.npv - target_npv) < tolerance * target_npv:
            return mid_rent

        # Adjust search range
        if test_result.npv < target_npv:
            low_rent = mid_rent
        else:
            high_rent = mid_rent

    # Return best estimate if didn't converge
    return (low_rent + high_rent) / 2


def generate_recommendation(
    renewal_result: ScenarioResult,
    relocation_result: ScenarioResult,
    npv_difference: float,
    annual_savings: float,
    irr: Optional[float],
    payback_years: Optional[float]
) -> Tuple[Literal['RENEW', 'RELOCATE', 'NEGOTIATE'], str]:
    """
    Generate investment recommendation based on analysis.

    Args:
        renewal_result: Renewal scenario result
        relocation_result: Relocation scenario result
        npv_difference: NPV difference (relocation - renewal)
        annual_savings: Annual cash flow savings
        irr: IRR of relocation investment
        payback_years: Payback period

    Returns:
        Tuple of (recommendation, notes)

    Note: NPV represents total COSTS, so higher NPV = more expensive.
    """
    notes = []

    # NPV comparison (higher NPV = higher costs = worse)
    if npv_difference > 10000:  # Relocation costs $10k+ more in NPV
        notes.append(f"Relocation costs ${npv_difference:,.0f} more in NPV terms.")
        primary_rec = 'RENEW'
    elif npv_difference < -10000:  # Relocation costs $10k+ less in NPV
        notes.append(f"Relocation saves ${abs(npv_difference):,.0f} in NPV terms.")
        primary_rec = 'RELOCATE'
    else:
        notes.append(f"NPV difference is minimal (${abs(npv_difference):,.0f}).")
        primary_rec = 'NEGOTIATE'

    # Annual cash flow
    if annual_savings > 0:
        notes.append(f"Relocation provides ${annual_savings:,.0f}/year in cash flow savings.")
    elif annual_savings < 0:
        notes.append(f"Renewal provides ${abs(annual_savings):,.0f}/year in cash flow savings.")

    # IRR
    if irr is not None:
        if irr > 0.15:  # 15% IRR threshold
            notes.append(f"Relocation IRR of {irr:.1%} exceeds 15% hurdle rate.")
            if primary_rec == 'RENEW':
                primary_rec = 'NEGOTIATE'  # Strong IRR suggests reconsidering
        elif irr > 0:
            notes.append(f"Relocation IRR of {irr:.1%} is positive but below 15% hurdle.")
        else:
            notes.append(f"Relocation IRR is negative ({irr:.1%}), indicating poor investment.")

    # Payback period
    if payback_years is not None:
        if payback_years < 3:
            notes.append(f"Payback period of {payback_years:.1f} years is attractive (<3 years).")
        elif payback_years < 5:
            notes.append(f"Payback period of {payback_years:.1f} years is moderate.")
        else:
            notes.append(f"Payback period of {payback_years:.1f} years is long (>5 years).")
    else:
        notes.append("Relocation does not have positive payback.")

    # Qualitative factors
    notes.append("\nConsider qualitative factors:")
    notes.append("- Strategic location advantages")
    notes.append("- Brand/visibility impact")
    notes.append("- Employee commute/satisfaction")
    notes.append("- Future growth capacity")
    notes.append("- Market conditions and alternatives")

    recommendation_text = " ".join(notes)

    return primary_rec, recommendation_text


# ============================================================================
# SENSITIVITY ANALYSIS
# ============================================================================

def sensitivity_analysis(
    renewal: RenewalScenario,
    relocation: RelocationScenario,
    general: GeneralInputs,
    variables: List[str] = ['rent', 'ti', 'disruption'],
    variation_pct: float = 0.10  # ±10% default
) -> pd.DataFrame:
    """
    Perform sensitivity analysis on key variables.

    Args:
        renewal: Renewal scenario
        relocation: Relocation scenario
        general: General parameters
        variables: Variables to test ('rent', 'ti', 'disruption', 'moving')
        variation_pct: Percentage variation (e.g., 0.10 for ±10%)

    Returns:
        DataFrame with sensitivity results
    """
    results = []

    # Base case
    base_comparison = compare_scenarios(renewal, relocation, general)

    results.append({
        'Variable': 'Base Case',
        'Variation': '0%',
        'Renewal_NPV': base_comparison.renewal_result.npv,
        'Relocation_NPV': base_comparison.relocation_result.npv,
        'NPV_Difference': base_comparison.npv_difference,
        'Recommendation': base_comparison.recommendation
    })

    # Rent sensitivity
    if 'rent' in variables:
        for mult in [1 - variation_pct, 1 + variation_pct]:
            # Adjust renewal rent
            adj_renewal = RenewalScenario(
                annual_rent_psf=[r * mult for r in renewal.annual_rent_psf],
                ti_allowance_psf=renewal.ti_allowance_psf,
                additional_ti_psf=renewal.additional_ti_psf,
                term_years=renewal.term_years,
                operating_costs_psf=renewal.operating_costs_psf,
                legal_fees=renewal.legal_fees,
                renovation_costs_psf=renewal.renovation_costs_psf
            )

            comp = compare_scenarios(adj_renewal, relocation, general)

            results.append({
                'Variable': 'Renewal Rent',
                'Variation': f"{(mult - 1) * 100:+.0f}%",
                'Renewal_NPV': comp.renewal_result.npv,
                'Relocation_NPV': comp.relocation_result.npv,
                'NPV_Difference': comp.npv_difference,
                'Recommendation': comp.recommendation
            })

    # TI sensitivity (relocation)
    if 'ti' in variables:
        for mult in [1 - variation_pct, 1 + variation_pct]:
            adj_relocation = RelocationScenario(
                annual_rent_psf=relocation.annual_rent_psf.copy(),
                ti_allowance_psf=relocation.ti_allowance_psf,
                ti_requirement_psf=relocation.ti_requirement_psf * mult,
                term_years=relocation.term_years,
                operating_costs_psf=relocation.operating_costs_psf,
                moving_costs=relocation.moving_costs,
                it_moving_costs=relocation.it_moving_costs,
                signage_costs=relocation.signage_costs,
                downtime_days=relocation.downtime_days,
                daily_revenue=relocation.daily_revenue,
                customer_loss_pct=relocation.customer_loss_pct,
                unamortized_improvements=relocation.unamortized_improvements,
                restoration_costs=relocation.restoration_costs,
                legal_fees=relocation.legal_fees,
                due_diligence_costs=relocation.due_diligence_costs,
                broker_fees=relocation.broker_fees
            )

            comp = compare_scenarios(renewal, adj_relocation, general)

            results.append({
                'Variable': 'Relocation TI',
                'Variation': f"{(mult - 1) * 100:+.0f}%",
                'Renewal_NPV': comp.renewal_result.npv,
                'Relocation_NPV': comp.relocation_result.npv,
                'NPV_Difference': comp.npv_difference,
                'Recommendation': comp.recommendation
            })

    # Disruption sensitivity
    if 'disruption' in variables:
        for mult in [1 - variation_pct, 1 + variation_pct]:
            adj_relocation = RelocationScenario(
                annual_rent_psf=relocation.annual_rent_psf.copy(),
                ti_allowance_psf=relocation.ti_allowance_psf,
                ti_requirement_psf=relocation.ti_requirement_psf,
                term_years=relocation.term_years,
                operating_costs_psf=relocation.operating_costs_psf,
                moving_costs=relocation.moving_costs,
                it_moving_costs=relocation.it_moving_costs,
                signage_costs=relocation.signage_costs,
                downtime_days=relocation.downtime_days * mult,
                daily_revenue=relocation.daily_revenue,
                customer_loss_pct=relocation.customer_loss_pct * mult,
                unamortized_improvements=relocation.unamortized_improvements,
                restoration_costs=relocation.restoration_costs,
                legal_fees=relocation.legal_fees,
                due_diligence_costs=relocation.due_diligence_costs,
                broker_fees=relocation.broker_fees
            )

            comp = compare_scenarios(renewal, adj_relocation, general)

            results.append({
                'Variable': 'Disruption Costs',
                'Variation': f"{(mult - 1) * 100:+.0f}%",
                'Renewal_NPV': comp.renewal_result.npv,
                'Relocation_NPV': comp.relocation_result.npv,
                'NPV_Difference': comp.npv_difference,
                'Recommendation': comp.recommendation
            })

    df = pd.DataFrame(results)

    # Round numeric columns
    numeric_cols = ['Renewal_NPV', 'Relocation_NPV', 'NPV_Difference']
    df[numeric_cols] = df[numeric_cols].round(2)

    return df


# ============================================================================
# REPORTING
# ============================================================================

def print_comparison_report(comparison: ComparisonResult):
    """Print formatted comparison report."""
    print("\n" + "="*80)
    print("RENEWAL vs. RELOCATION ECONOMIC ANALYSIS")
    print("="*80)

    # Renewal scenario
    print("\n" + "-"*80)
    print(f"SCENARIO 1: {comparison.renewal_result.scenario_name.upper()}")
    print("-"*80)

    r = comparison.renewal_result
    print(f"\nTotal Cash Outflows: ${r.total_cash_outflows:,.2f}")
    print(f"  Rent payments: ${r.total_rent_payments:,.2f}")
    print(f"  Operating costs: ${r.total_operating_costs:,.2f}")
    print(f"  TI costs: ${r.total_ti_costs:,.2f}")
    print(f"  Other costs: ${r.total_other_costs:,.2f}")

    print(f"\nNet Present Value: ${r.npv:,.2f}")
    print(f"Net Effective Rent: ${r.net_effective_rent_psf:,.2f} /sf/year")

    # Relocation scenario
    print("\n" + "-"*80)
    print(f"SCENARIO 2: {comparison.relocation_result.scenario_name.upper()}")
    print("-"*80)

    rl = comparison.relocation_result
    print(f"\nTotal Cash Outflows: ${rl.total_cash_outflows:,.2f}")
    print(f"  Rent payments: ${rl.total_rent_payments:,.2f}")
    print(f"  Operating costs: ${rl.total_operating_costs:,.2f}")
    print(f"  TI costs: ${rl.total_ti_costs:,.2f}")
    print(f"  Other costs: ${rl.total_other_costs:,.2f}")

    print(f"\nNet Present Value: ${rl.npv:,.2f}")
    print(f"Net Effective Rent: ${rl.net_effective_rent_psf:,.2f} /sf/year")

    # Comparison
    print("\n" + "-"*80)
    print("COMPARISON & INVESTMENT METRICS")
    print("-"*80)

    print(f"\nNPV Difference (Relocation - Renewal): ${comparison.npv_difference:,.2f}")
    if comparison.npv_difference > 0:
        print(f"  → Relocation costs ${comparison.npv_difference:,.2f} MORE")
    else:
        print(f"  → Relocation saves ${abs(comparison.npv_difference):,.2f}")

    print(f"\nNER Difference: ${comparison.ner_difference_psf:,.2f} /sf/year")

    if comparison.relocation_irr is not None:
        print(f"\nRelocation IRR: {comparison.relocation_irr:.2%}")

    if comparison.payback_period_years is not None:
        print(f"Payback Period: {comparison.payback_period_years:.1f} years")
    else:
        print("Payback Period: Never (no positive cash flows)")

    print(f"\nAnnual Savings (Relocation vs Renewal): ${comparison.annual_savings:,.2f}")

    if comparison.breakeven_rent_psf is not None:
        print(f"\nBreakeven Renewal Rent: ${comparison.breakeven_rent_psf:,.2f} /sf/year")
        if comparison.current_margin_psf is not None:
            print(f"Current Margin: ${comparison.current_margin_psf:,.2f} /sf/year")

    # Recommendation
    print("\n" + "="*80)
    print(f"RECOMMENDATION: {comparison.recommendation}")
    print("="*80)
    print(f"\n{comparison.recommendation_notes}")

    print("\n" + "="*80)


if __name__ == "__main__":
    # Example analysis
    print("Renewal Economics Calculator - Example Analysis\n")

    # Example: Company considering renewal vs. relocation
    renewal = RenewalScenario(
        annual_rent_psf=[25.00, 25.75, 26.50, 27.25, 28.00],  # 3% annual escalation
        ti_allowance_psf=15.00,
        additional_ti_psf=20.00,  # Need $20/sf, landlord gives $15
        term_years=5,
        operating_costs_psf=8.00,
        legal_fees=5000
    )

    relocation = RelocationScenario(
        annual_rent_psf=[23.00, 23.69, 24.40, 25.13, 25.88],  # 3% escalation, lower base
        ti_allowance_psf=25.00,
        ti_requirement_psf=40.00,  # Need $40/sf buildout
        term_years=5,
        operating_costs_psf=8.00,
        moving_costs=50000,
        it_moving_costs=25000,
        downtime_days=10,
        daily_revenue=10000,
        customer_loss_pct=0.02,  # Lose 2% of customers
        unamortized_improvements=75000,
        legal_fees=15000,
        due_diligence_costs=10000
    )

    general = GeneralInputs(
        rentable_area_sf=20000,
        discount_rate=0.10,
        current_rent_psf=24.00,
        market_rent_psf=23.00
    )

    # Run comparison
    comparison = compare_scenarios(renewal, relocation, general)

    # Print report
    print_comparison_report(comparison)

    # Sensitivity analysis
    print("\n" + "="*80)
    print("SENSITIVITY ANALYSIS")
    print("="*80)

    sensitivity = sensitivity_analysis(renewal, relocation, general)
    print("\n" + sensitivity.to_string(index=False))

    print("\n✓ Example analysis complete!")
