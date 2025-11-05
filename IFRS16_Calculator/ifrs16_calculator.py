"""
IFRS 16 / ASC 842 Lease Accounting Calculator

Calculates lease liability, right-of-use (ROU) asset, and generates complete
amortization and depreciation schedules for lease accounting under IFRS 16
and ASC 842 standards.

Key Features:
- Lease liability calculation using present value
- ROU asset calculation
- Monthly amortization schedules with interest expense
- Straight-line depreciation schedules
- Annual summaries
- Sensitivity analysis
- CSV export capability

Author: Claude Code
Created: 2025-10-30
GitHub Issue: #3
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Literal
from datetime import datetime
from dataclasses import dataclass

from Shared_Utils.financial_utils import (
    pv_annuity,
    annual_to_monthly_rate,
    amortization_schedule as create_amortization_schedule,
    present_value
)


@dataclass
class LeaseInputs:
    """
    Input parameters for IFRS 16 lease accounting calculation.
    """
    # Payment schedule
    monthly_payments: List[float]  # List of monthly payments (can vary)

    # Discount rate
    annual_discount_rate: float  # Annual rate (e.g., 0.055 for 5.5%)

    # Initial costs and incentives
    initial_direct_costs: float = 0.0  # Costs to obtain lease
    prepaid_rent: float = 0.0  # Rent paid at commencement
    lease_incentives: float = 0.0  # Cash incentives received

    # Lease term
    lease_term_months: int = None  # Auto-calculated from payments if None

    # Payment timing
    payment_timing: Literal['beginning', 'end'] = 'beginning'  # Annuity due vs ordinary

    # Metadata
    tenant_name: str = "Tenant"
    property_address: str = "Property"
    commencement_date: Optional[datetime] = None

    def __post_init__(self):
        """Validate and set defaults."""
        if self.lease_term_months is None:
            self.lease_term_months = len(self.monthly_payments)

        if len(self.monthly_payments) != self.lease_term_months:
            raise ValueError(
                f"Payment schedule length ({len(self.monthly_payments)}) must match "
                f"lease term ({self.lease_term_months} months)"
            )

        if self.annual_discount_rate <= 0:
            raise ValueError("Discount rate must be positive")

        if self.commencement_date is None:
            self.commencement_date = datetime.now()


@dataclass
class LeaseAccountingResult:
    """
    Complete results of IFRS 16 lease accounting calculation.
    """
    # Summary values
    initial_lease_liability: float
    initial_rou_asset: float
    total_interest_expense: float
    total_depreciation: float
    total_lease_cost: float

    # Schedules
    amortization_schedule: pd.DataFrame  # Lease liability schedule
    depreciation_schedule: pd.DataFrame  # ROU asset schedule
    annual_summary: pd.DataFrame  # Year-by-year summary

    # Components
    lease_liability_components: Dict[str, float]
    rou_asset_components: Dict[str, float]

    # Input parameters
    inputs: LeaseInputs
    monthly_discount_rate: float


# ============================================================================
# CORE CALCULATIONS
# ============================================================================

def calculate_lease_liability(
    payments: List[float],
    annual_rate: float,
    payment_timing: Literal['beginning', 'end'] = 'beginning'
) -> Tuple[float, float]:
    """
    Calculate initial lease liability as present value of future lease payments.

    Args:
        payments: List of monthly lease payments
        annual_rate: Annual discount rate (e.g., 0.055 for 5.5%)
        payment_timing: 'beginning' for annuity due, 'end' for ordinary annuity

    Returns:
        Tuple of (lease_liability, monthly_rate)

    Notes:
        - IFRS 16 and ASC 842 require using annuity due (payments at beginning)
          because rent is typically paid in advance
        - If payments vary, uses present_value() function
        - If payments are constant, uses pv_annuity() for efficiency
    """
    monthly_rate = annual_to_monthly_rate(annual_rate)

    # For IFRS 16: When payments are at beginning of period (annuity due),
    # the FIRST payment is made at commencement and is NOT part of the lease liability.
    # The liability is only for the REMAINING payments.

    if payment_timing == 'beginning':
        # First payment made at commencement - not included in liability
        if len(payments) == 1:
            # Only one payment - no liability after payment
            liability = 0
        elif len(set(payments[1:])) == 1:
            # Remaining payments are constant
            liability = pv_annuity(
                payment=payments[1],
                rate=monthly_rate,
                periods=len(payments) - 1,
                timing='end'  # Remaining payments are at end of each period
            )
        else:
            # Variable remaining payments
            liability = 0
            for t in range(1, len(payments)):
                liability += payments[t] / ((1 + monthly_rate) ** t)
    else:
        # Ordinary annuity - all payments in future
        if len(set(payments)) == 1:
            liability = pv_annuity(
                payment=payments[0],
                rate=monthly_rate,
                periods=len(payments),
                timing='end'
            )
        else:
            liability = 0
            for t in range(len(payments)):
                liability += payments[t] / ((1 + monthly_rate) ** (t + 1))

    return liability, monthly_rate


def calculate_rou_asset(
    lease_liability: float,
    initial_direct_costs: float = 0.0,
    prepaid_rent: float = 0.0,
    lease_incentives: float = 0.0
) -> Tuple[float, Dict[str, float]]:
    """
    Calculate right-of-use (ROU) asset.

    Formula (IFRS 16 / ASC 842):
        ROU Asset = Lease Liability
                  + Initial Direct Costs
                  + Prepaid Rent
                  - Lease Incentives Received

    Args:
        lease_liability: Initial lease liability
        initial_direct_costs: Costs to obtain the lease (broker fees, legal)
        prepaid_rent: Rent payments made at or before commencement
        lease_incentives: Cash incentives received from lessor

    Returns:
        Tuple of (rou_asset, components_dict)
    """
    rou_asset = (
        lease_liability +
        initial_direct_costs +
        prepaid_rent -
        lease_incentives
    )

    components = {
        'lease_liability': lease_liability,
        'initial_direct_costs': initial_direct_costs,
        'prepaid_rent': prepaid_rent,
        'lease_incentives': -lease_incentives,  # Negative because it reduces asset
        'total_rou_asset': rou_asset
    }

    return rou_asset, components


def generate_liability_amortization(
    initial_liability: float,
    monthly_payments: List[float],
    monthly_rate: float,
    commencement_date: datetime,
    payment_timing: Literal['beginning', 'end'] = 'beginning'
) -> pd.DataFrame:
    """
    Generate complete lease liability amortization schedule.

    For each period:
        Interest Expense = Opening Balance × Monthly Rate
        Payment = Scheduled payment for period
        Principal Reduction = Payment - Interest Expense
        Closing Balance = Opening Balance - Principal Reduction

    Args:
        initial_liability: Initial lease liability
        monthly_payments: List of monthly lease payments
        monthly_rate: Monthly discount rate
        commencement_date: Lease commencement date
        payment_timing: Payment at beginning or end of period

    Returns:
        DataFrame with complete amortization schedule
    """
    periods = len(monthly_payments)
    schedule = []

    balance = initial_liability
    cumulative_interest = 0.0
    cumulative_principal = 0.0

    # Period 0 - Commencement
    current_date = commencement_date

    if payment_timing == 'beginning':
        # For annuity due: First payment made at commencement
        first_payment = monthly_payments[0]
        schedule.append({
            'Period': 0,
            'Date': current_date.strftime('%Y-%m-%d'),
            'Opening_Balance': 0.0,  # Before recognition
            'Payment': first_payment,
            'Interest_Expense': 0.0,
            'Principal_Reduction': first_payment,
            'Closing_Balance': initial_liability,  # Liability after first payment
            'Cumulative_Interest': 0.0,
            'Cumulative_Principal': first_payment
        })
        cumulative_principal = first_payment
    else:
        # For ordinary annuity: No payment at commencement
        schedule.append({
            'Period': 0,
            'Date': current_date.strftime('%Y-%m-%d'),
            'Opening_Balance': initial_liability,
            'Payment': 0.0,
            'Interest_Expense': 0.0,
            'Principal_Reduction': 0.0,
            'Closing_Balance': initial_liability,
            'Cumulative_Interest': 0.0,
            'Cumulative_Principal': 0.0
        })

    # Periods 1 to N
    # For annuity due, we've already processed payment 0, so process payments 1-59
    # For ordinary annuity, process payments 0-59
    payment_start_idx = 1 if payment_timing == 'beginning' else 0

    for period in range(1, periods + 1):
        # Calculate date using add_months from financial_utils
        # For now, just format as Month N
        date_str = f"Month {period}"

        opening = balance

        # Get the appropriate payment
        payment_idx = payment_start_idx + period - 1
        if payment_idx >= len(monthly_payments):
            break  # No more payments
        payment = monthly_payments[payment_idx]

        if payment_timing == 'beginning':
            # Payment at beginning of period
            # For IFRS 16: Payment first, then interest accrues on remaining balance
            principal_reduction = payment
            balance_after_payment = opening - principal_reduction
            interest = balance_after_payment * monthly_rate
            closing = balance_after_payment + interest - interest  # Simplifies to balance_after_payment
            # Wait, that doesn't work. Let me reconsider.

            # Actually for annuity due in IFRS 16:
            # Opening balance gets payment applied, reducing it
            # Then interest expense accrues on the net balance
            # But wait - the amortization should have interest accrue BEFORE payment

            # Let me use the standard approach:
            # Interest expense = Opening balance × rate
            # Cash payment = Fixed payment amount
            # Principal reduction = Payment - Interest
            # Closing = Opening - Principal

            interest = opening * monthly_rate
            principal_reduction = payment - interest
            closing = opening - principal_reduction
        else:
            # Payment at end of period - standard approach
            interest = opening * monthly_rate
            principal_reduction = payment - interest
            closing = opening - principal_reduction

        # Handle final period rounding to force zero balance
        if period == periods and abs(closing) < 10:
            # Adjust final principal to close to exactly zero
            principal_reduction = opening + interest - payment
            closing = 0.0

        cumulative_interest += interest
        cumulative_principal += principal_reduction

        schedule.append({
            'Period': period,
            'Date': date_str,
            'Opening_Balance': opening,
            'Payment': payment,
            'Interest_Expense': interest,
            'Principal_Reduction': principal_reduction,
            'Closing_Balance': closing,
            'Cumulative_Interest': cumulative_interest,
            'Cumulative_Principal': cumulative_principal
        })

        balance = closing

    df = pd.DataFrame(schedule)

    # Round to 2 decimal places for currency
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].round(2)

    return df


def generate_rou_depreciation(
    initial_rou_asset: float,
    lease_term_months: int,
    commencement_date: datetime
) -> pd.DataFrame:
    """
    Generate ROU asset depreciation schedule (straight-line).

    Monthly Depreciation = ROU Asset / Lease Term (months)

    Args:
        initial_rou_asset: Initial ROU asset value
        lease_term_months: Lease term in months
        commencement_date: Lease commencement date

    Returns:
        DataFrame with depreciation schedule
    """
    monthly_depreciation = initial_rou_asset / lease_term_months

    schedule = []
    accumulated = 0.0
    net_book_value = initial_rou_asset

    # Period 0 - Commencement
    schedule.append({
        'Period': 0,
        'Date': commencement_date.strftime('%Y-%m-%d'),
        'Opening_NBV': initial_rou_asset,
        'Depreciation_Expense': 0.0,
        'Accumulated_Depreciation': 0.0,
        'Closing_NBV': initial_rou_asset
    })

    # Periods 1 to N
    for period in range(1, lease_term_months + 1):
        opening_nbv = net_book_value
        depreciation = monthly_depreciation

        # Final period - depreciate remaining balance
        if period == lease_term_months:
            depreciation = net_book_value

        accumulated += depreciation
        net_book_value -= depreciation

        schedule.append({
            'Period': period,
            'Date': f"Month {period}",
            'Opening_NBV': opening_nbv,
            'Depreciation_Expense': depreciation,
            'Accumulated_Depreciation': accumulated,
            'Closing_NBV': net_book_value
        })

    df = pd.DataFrame(schedule)

    # Round to 2 decimal places
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].round(2)

    return df


def create_annual_summary(
    amortization: pd.DataFrame,
    depreciation: pd.DataFrame,
    commencement_date: datetime
) -> pd.DataFrame:
    """
    Create year-by-year summary of lease accounting.

    Args:
        amortization: Lease liability amortization schedule
        depreciation: ROU asset depreciation schedule
        commencement_date: Lease commencement date

    Returns:
        DataFrame with annual summary
    """
    # Add year column to both schedules
    amort = amortization.copy()
    deprec = depreciation.copy()

    # Calculate year for each period (12 months per year)
    amort['Year'] = (amort['Period'] - 1) // 12 + 1
    deprec['Year'] = (deprec['Period'] - 1) // 12 + 1

    # Aggregate by year
    annual_amort = amort[amort['Period'] > 0].groupby('Year').agg({
        'Payment': 'sum',
        'Interest_Expense': 'sum',
        'Principal_Reduction': 'sum'
    }).reset_index()

    annual_deprec = deprec[deprec['Period'] > 0].groupby('Year').agg({
        'Depreciation_Expense': 'sum'
    }).reset_index()

    # Merge
    annual = pd.merge(annual_amort, annual_deprec, on='Year')

    # Calculate total lease expense
    annual['Total_Lease_Expense'] = (
        annual['Interest_Expense'] + annual['Depreciation_Expense']
    )

    # Add cash paid
    annual['Cash_Paid'] = annual['Payment']

    # Reorder columns
    annual = annual[[
        'Year',
        'Cash_Paid',
        'Interest_Expense',
        'Depreciation_Expense',
        'Total_Lease_Expense',
        'Principal_Reduction'
    ]]

    # Round
    numeric_cols = annual.select_dtypes(include=[np.number]).columns
    annual[numeric_cols] = annual[numeric_cols].round(2)

    return annual


# ============================================================================
# MAIN CALCULATION FUNCTION
# ============================================================================

def calculate_ifrs16(inputs: LeaseInputs) -> LeaseAccountingResult:
    """
    Perform complete IFRS 16 / ASC 842 lease accounting calculation.

    Args:
        inputs: LeaseInputs object with all required parameters

    Returns:
        LeaseAccountingResult with all calculations and schedules
    """
    # 1. Calculate lease liability
    lease_liability, monthly_rate = calculate_lease_liability(
        payments=inputs.monthly_payments,
        annual_rate=inputs.annual_discount_rate,
        payment_timing=inputs.payment_timing
    )

    # 2. Calculate ROU asset
    rou_asset, rou_components = calculate_rou_asset(
        lease_liability=lease_liability,
        initial_direct_costs=inputs.initial_direct_costs,
        prepaid_rent=inputs.prepaid_rent,
        lease_incentives=inputs.lease_incentives
    )

    # 3. Generate amortization schedule
    amortization = generate_liability_amortization(
        initial_liability=lease_liability,
        monthly_payments=inputs.monthly_payments,
        monthly_rate=monthly_rate,
        commencement_date=inputs.commencement_date,
        payment_timing=inputs.payment_timing
    )

    # 4. Generate depreciation schedule
    depreciation = generate_rou_depreciation(
        initial_rou_asset=rou_asset,
        lease_term_months=inputs.lease_term_months,
        commencement_date=inputs.commencement_date
    )

    # 5. Create annual summary
    annual_summary = create_annual_summary(
        amortization=amortization,
        depreciation=depreciation,
        commencement_date=inputs.commencement_date
    )

    # 6. Calculate totals
    total_interest = amortization['Interest_Expense'].sum()
    total_depreciation = depreciation['Depreciation_Expense'].sum()
    total_payments = sum(inputs.monthly_payments)
    total_cost = total_interest + total_depreciation

    # 7. Create liability components dict
    liability_components = {
        'present_value_of_payments': lease_liability,
        'monthly_discount_rate': monthly_rate,
        'annual_discount_rate': inputs.annual_discount_rate,
        'payment_timing': inputs.payment_timing
    }

    return LeaseAccountingResult(
        initial_lease_liability=lease_liability,
        initial_rou_asset=rou_asset,
        total_interest_expense=total_interest,
        total_depreciation=total_depreciation,
        total_lease_cost=total_cost,
        amortization_schedule=amortization,
        depreciation_schedule=depreciation,
        annual_summary=annual_summary,
        lease_liability_components=liability_components,
        rou_asset_components=rou_components,
        inputs=inputs,
        monthly_discount_rate=monthly_rate
    )


# ============================================================================
# SENSITIVITY ANALYSIS
# ============================================================================

def sensitivity_analysis(
    base_inputs: LeaseInputs,
    rate_variations: List[float] = [-0.02, -0.01, 0, 0.01, 0.02],
    term_variations: List[int] = [-12, 0, 12]
) -> pd.DataFrame:
    """
    Perform sensitivity analysis on discount rate and lease term.

    Args:
        base_inputs: Base case lease inputs
        rate_variations: List of rate adjustments (e.g., [-0.02, 0, 0.02] for ±2%)
        term_variations: List of term adjustments in months

    Returns:
        DataFrame with sensitivity results
    """
    results = []

    base_result = calculate_ifrs16(base_inputs)

    # Rate sensitivity
    for rate_adj in rate_variations:
        if rate_adj == 0:
            # Base case
            results.append({
                'Scenario': 'Base Case',
                'Discount_Rate': f"{base_inputs.annual_discount_rate:.2%}",
                'Lease_Term_Months': base_inputs.lease_term_months,
                'Lease_Liability': base_result.initial_lease_liability,
                'ROU_Asset': base_result.initial_rou_asset,
                'Total_Interest': base_result.total_interest_expense,
                'Total_Depreciation': base_result.total_depreciation,
                'Total_Cost': base_result.total_lease_cost,
                'Variance_from_Base': 0.0
            })
        else:
            # Adjusted rate
            adj_inputs = LeaseInputs(
                monthly_payments=base_inputs.monthly_payments.copy(),
                annual_discount_rate=base_inputs.annual_discount_rate + rate_adj,
                initial_direct_costs=base_inputs.initial_direct_costs,
                prepaid_rent=base_inputs.prepaid_rent,
                lease_incentives=base_inputs.lease_incentives,
                payment_timing=base_inputs.payment_timing
            )
            adj_result = calculate_ifrs16(adj_inputs)

            results.append({
                'Scenario': f"Rate {rate_adj:+.1%}",
                'Discount_Rate': f"{adj_inputs.annual_discount_rate:.2%}",
                'Lease_Term_Months': adj_inputs.lease_term_months,
                'Lease_Liability': adj_result.initial_lease_liability,
                'ROU_Asset': adj_result.initial_rou_asset,
                'Total_Interest': adj_result.total_interest_expense,
                'Total_Depreciation': adj_result.total_depreciation,
                'Total_Cost': adj_result.total_lease_cost,
                'Variance_from_Base': adj_result.total_lease_cost - base_result.total_lease_cost
            })

    # Term sensitivity (if variations requested)
    for term_adj in term_variations:
        if term_adj == 0:
            continue  # Already have base case

        new_term = base_inputs.lease_term_months + term_adj
        if new_term <= 0:
            continue

        # Adjust payment schedule
        if term_adj > 0:
            # Extend term - add payments
            last_payment = base_inputs.monthly_payments[-1]
            adj_payments = base_inputs.monthly_payments.copy() + [last_payment] * term_adj
        else:
            # Shorten term - remove payments
            adj_payments = base_inputs.monthly_payments[:new_term]

        adj_inputs = LeaseInputs(
            monthly_payments=adj_payments,
            annual_discount_rate=base_inputs.annual_discount_rate,
            initial_direct_costs=base_inputs.initial_direct_costs,
            prepaid_rent=base_inputs.prepaid_rent,
            lease_incentives=base_inputs.lease_incentives,
            payment_timing=base_inputs.payment_timing
        )
        adj_result = calculate_ifrs16(adj_inputs)

        results.append({
            'Scenario': f"Term {term_adj:+d} months",
            'Discount_Rate': f"{adj_inputs.annual_discount_rate:.2%}",
            'Lease_Term_Months': adj_inputs.lease_term_months,
            'Lease_Liability': adj_result.initial_lease_liability,
            'ROU_Asset': adj_result.initial_rou_asset,
            'Total_Interest': adj_result.total_interest_expense,
            'Total_Depreciation': adj_result.total_depreciation,
            'Total_Cost': adj_result.total_lease_cost,
            'Variance_from_Base': adj_result.total_lease_cost - base_result.total_lease_cost
        })

    df = pd.DataFrame(results)

    # Round numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].round(2)

    return df


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def export_to_csv(result: LeaseAccountingResult, output_dir: str = "."):
    """
    Export all schedules to CSV files.

    Args:
        result: LeaseAccountingResult object
        output_dir: Directory to save CSV files

    Returns:
        Dict of filenames created
    """
    tenant = result.inputs.tenant_name.replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d")

    files = {}

    # Amortization schedule
    amort_file = f"{output_dir}/{tenant}_lease_liability_amortization_{timestamp}.csv"
    result.amortization_schedule.to_csv(amort_file, index=False)
    files['amortization'] = amort_file

    # Depreciation schedule
    deprec_file = f"{output_dir}/{tenant}_rou_asset_depreciation_{timestamp}.csv"
    result.depreciation_schedule.to_csv(deprec_file, index=False)
    files['depreciation'] = deprec_file

    # Annual summary
    annual_file = f"{output_dir}/{tenant}_annual_summary_{timestamp}.csv"
    result.annual_summary.to_csv(annual_file, index=False)
    files['annual_summary'] = annual_file

    return files


# ============================================================================
# DISPLAY / REPORTING FUNCTIONS
# ============================================================================

def print_summary(result: LeaseAccountingResult):
    """Print formatted summary of IFRS 16 calculation."""
    print("\n" + "="*80)
    print("IFRS 16 / ASC 842 LEASE ACCOUNTING CALCULATION")
    print("="*80)

    print(f"\nTenant: {result.inputs.tenant_name}")
    print(f"Property: {result.inputs.property_address}")
    print(f"Commencement: {result.inputs.commencement_date.strftime('%Y-%m-%d')}")
    print(f"Lease Term: {result.inputs.lease_term_months} months ({result.inputs.lease_term_months/12:.1f} years)")
    print(f"Discount Rate: {result.inputs.annual_discount_rate:.2%} annual ({result.monthly_discount_rate:.4%} monthly)")

    print("\n" + "-"*80)
    print("INITIAL RECOGNITION")
    print("-"*80)

    print(f"\nLease Liability: ${result.initial_lease_liability:,.2f}")
    print(f"\nROU Asset Components:")
    for key, value in result.rou_asset_components.items():
        if key != 'total_rou_asset':
            print(f"  {key.replace('_', ' ').title():.<40} ${value:>12,.2f}")
    print(f"  {'Total ROU Asset':.<40} ${result.initial_rou_asset:>12,.2f}")

    print("\n" + "-"*80)
    print("TOTAL LEASE COST OVER TERM")
    print("-"*80)

    print(f"\nTotal Interest Expense: ${result.total_interest_expense:,.2f}")
    print(f"Total Depreciation Expense: ${result.total_depreciation:,.2f}")
    print(f"Total Lease Expense: ${result.total_lease_cost:,.2f}")

    total_payments = sum(result.inputs.monthly_payments)
    print(f"\nTotal Cash Payments: ${total_payments:,.2f}")
    print(f"Difference (non-cash): ${result.total_lease_cost - total_payments:,.2f}")

    print("\n" + "-"*80)
    print("ANNUAL SUMMARY")
    print("-"*80)
    print("\n" + result.annual_summary.to_string(index=False))

    print("\n" + "="*80)


if __name__ == "__main__":
    # Example calculation
    print("IFRS 16 Calculator - Example Calculation\n")

    # Example: 5-year lease, $10,000/month, 5.5% discount rate
    example_inputs = LeaseInputs(
        monthly_payments=[10000] * 60,  # $10k/month for 60 months
        annual_discount_rate=0.055,
        initial_direct_costs=15000,
        lease_incentives=25000,
        tenant_name="Example Corp",
        property_address="123 Main Street",
        payment_timing='beginning'
    )

    result = calculate_ifrs16(example_inputs)

    print_summary(result)

    print("\n" + "="*80)
    print("SENSITIVITY ANALYSIS")
    print("="*80)

    sensitivity = sensitivity_analysis(example_inputs)
    print("\n" + sensitivity.to_string(index=False))

    print("\n✓ Example calculation complete!")
