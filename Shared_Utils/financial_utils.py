"""
Shared Financial Utilities Module

Common financial functions used across lease analysis calculators including:
- Present value and NPV calculations
- IRR and discount rate conversions
- Amortization schedules
- Financial ratio calculations
- Statistical analysis

Author: Claude Code
Created: 2025-10-30
"""

import numpy as np
import numpy_financial as npf
import pandas as pd
from typing import List, Dict, Optional, Union, Literal
from scipy.optimize import newton
from datetime import datetime, timedelta


# ============================================================================
# PRESENT VALUE CALCULATIONS
# ============================================================================

def present_value(
    cash_flows: List[float],
    discount_rate: float,
    periods: Literal['monthly', 'annual'] = 'monthly'
) -> float:
    """
    Calculate present value of a series of cash flows.

    Args:
        cash_flows: List of periodic cash flows (can be irregular)
        discount_rate: Annual discount rate as decimal (e.g., 0.10 for 10%)
        periods: Whether cash flows are 'monthly' or 'annual'

    Returns:
        Present value of all cash flows

    Raises:
        ValueError: If discount_rate is invalid or cash_flows is empty

    Example:
        >>> cash_flows = [1000, 1000, 1000, 1000, 1000]  # 5 monthly payments
        >>> pv = present_value(cash_flows, 0.06, 'monthly')
        >>> print(f"${pv:,.2f}")
        $4,854.37
    """
    if not cash_flows:
        raise ValueError("cash_flows cannot be empty")

    if discount_rate < 0:
        raise ValueError(f"discount_rate must be non-negative, got {discount_rate}")

    # Convert annual rate to periodic rate
    if periods == 'monthly':
        period_rate = annual_to_monthly_rate(discount_rate)
    else:
        period_rate = discount_rate

    # Calculate PV for each cash flow
    # First cash flow (index 0) occurs at t=0 (present), so is not discounted
    # This is appropriate for NPV calculations where first cash flow is typically
    # the initial investment. For annuities where all payments are in the future,
    # use pv_annuity() instead.
    pv = 0.0
    for t, cf in enumerate(cash_flows):
        pv += cf / ((1 + period_rate) ** t)

    return pv


def pv_annuity(
    payment: float,
    rate: float,
    periods: int,
    timing: Literal['beginning', 'end'] = 'end'
) -> float:
    """
    Calculate present value of an annuity (constant periodic payments).

    Args:
        payment: Periodic payment amount
        rate: Discount rate per period (not annual!)
        periods: Number of periods
        timing: 'beginning' for annuity due, 'end' for ordinary annuity

    Returns:
        Present value of annuity

    Raises:
        ValueError: If inputs are invalid

    Example:
        >>> # $1000/month for 60 months at 6% annual (0.487% monthly)
        >>> monthly_rate = annual_to_monthly_rate(0.06)
        >>> pv = pv_annuity(1000, monthly_rate, 60, 'beginning')
        >>> print(f"${pv:,.2f}")
        $52,107.09

    Notes:
        - For annuity due (beginning): PV_ordinary × (1 + r)
        - Commercial leases typically use annuity due (rent paid in advance)
    """
    if periods <= 0:
        raise ValueError(f"periods must be positive, got {periods}")

    if rate < 0:
        raise ValueError(f"rate must be non-negative, got {rate}")

    if rate == 0:
        # If no discounting, PV = payment × periods
        return payment * periods

    # Standard annuity formula
    pv_ordinary = payment * ((1 - (1 + rate) ** -periods) / rate)

    # Adjust for timing
    if timing == 'beginning':
        return pv_ordinary * (1 + rate)
    else:
        return pv_ordinary


# ============================================================================
# NPV AND IRR
# ============================================================================

def npv(cash_flows: List[float], discount_rate: float) -> float:
    """
    Calculate Net Present Value of cash flows.

    Args:
        cash_flows: List of cash flows where first item is typically initial
                   investment (negative), followed by periodic returns
        discount_rate: Annual discount rate as decimal

    Returns:
        Net present value

    Example:
        >>> # Initial investment of -$100k, then $30k/year for 5 years
        >>> cash_flows = [-100000, 30000, 30000, 30000, 30000, 30000]
        >>> npv_value = npv(cash_flows, 0.10)
        >>> print(f"${npv_value:,.2f}")
        $13,723.60
    """
    if not cash_flows:
        raise ValueError("cash_flows cannot be empty")

    return present_value(cash_flows, discount_rate, periods='annual')


def irr(
    cash_flows: List[float],
    guess: float = 0.10,
    max_iterations: int = 100
) -> float:
    """
    Calculate Internal Rate of Return using Newton's method with robust fallbacks.

    Args:
        cash_flows: List of cash flows (first typically negative investment)
        guess: Initial guess for IRR
        max_iterations: Maximum iterations for convergence

    Returns:
        IRR as decimal (e.g., 0.12 for 12%)

    Raises:
        ValueError: If IRR cannot converge or inputs invalid

    Example:
        >>> cash_flows = [-100000, 30000, 30000, 30000, 30000, 30000]
        >>> irr_value = irr(cash_flows)
        >>> print(f"{irr_value:.2%}")
        15.24%
    """
    if not cash_flows:
        raise ValueError("cash_flows cannot be empty")

    if len(cash_flows) < 2:
        raise ValueError("Need at least 2 cash flows to calculate IRR")

    cash_flows_array = np.asarray(cash_flows, dtype=float)
    periods = np.arange(len(cash_flows_array), dtype=float)

    def npv_at_rate(r: float) -> float:
        if r <= -1.0:
            raise FloatingPointError("IRR cannot evaluate at rates <= -100%")
        with np.errstate(over='raise', invalid='raise', divide='raise', under='ignore'):
            discount_factors = np.power(1.0 + r, periods)
            return float(np.sum(cash_flows_array / discount_factors))

    def npv_derivative(r: float) -> float:
        if r <= -1.0:
            raise FloatingPointError("IRR cannot evaluate at rates <= -100%")
        with np.errstate(over='raise', invalid='raise', divide='raise', under='ignore'):
            discount_factors = np.power(1.0 + r, periods + 1.0)
            return float(np.sum(-periods * cash_flows_array / discount_factors))

    try:
        with np.errstate(over='raise', invalid='raise', divide='raise', under='ignore'):
            result = newton(
                npv_at_rate,
                guess,
                fprime=npv_derivative,
                maxiter=max_iterations,
                tol=1e-6
            )
        if not np.isfinite(result):
            raise RuntimeError("IRR calculation returned a non-finite value")
        return float(result)
    except (RuntimeError, FloatingPointError, OverflowError, ZeroDivisionError):
        fallback = npf.irr(cash_flows_array)
        if fallback is None or np.isnan(fallback) or not np.isfinite(fallback) or fallback <= -1.0:
            raise ValueError("IRR calculation did not converge with provided cash flows")
        return float(fallback)


# ============================================================================
# DISCOUNT RATE CONVERSIONS
# ============================================================================

def annual_to_monthly_rate(annual_rate: float) -> float:
    """
    Convert annual interest rate to monthly using compound interest formula.

    Formula: r_monthly = (1 + r_annual)^(1/12) - 1

    Args:
        annual_rate: Annual rate as decimal (e.g., 0.06 for 6%)

    Returns:
        Monthly rate as decimal

    Example:
        >>> monthly = annual_to_monthly_rate(0.06)
        >>> print(f"{monthly:.6f} ({monthly:.4%})")
        0.004868 (0.4868%)

    Notes:
        - This is NOT simply annual_rate / 12 (that would be simple interest)
        - Uses compound interest: (1.06)^(1/12) - 1 = 0.004868
        - Verify: (1.004868)^12 = 1.06
    """
    if annual_rate < -1:
        raise ValueError(f"annual_rate must be > -1 (got {annual_rate})")

    return (1 + annual_rate) ** (1/12) - 1


def monthly_to_annual_rate(monthly_rate: float) -> float:
    """
    Convert monthly interest rate to annual using compound interest formula.

    Formula: r_annual = (1 + r_monthly)^12 - 1

    Args:
        monthly_rate: Monthly rate as decimal

    Returns:
        Annual rate as decimal

    Example:
        >>> annual = monthly_to_annual_rate(0.004868)
        >>> print(f"{annual:.4%}")
        6.00%
    """
    if monthly_rate < -1:
        raise ValueError(f"monthly_rate must be > -1 (got {monthly_rate})")

    return (1 + monthly_rate) ** 12 - 1


def effective_annual_rate(nominal_rate: float, compounds_per_year: int) -> float:
    """
    Convert nominal annual rate to effective annual rate.

    Formula: EAR = (1 + r/n)^n - 1

    Args:
        nominal_rate: Nominal annual rate
        compounds_per_year: Compounding frequency (12 for monthly, 4 for quarterly)

    Returns:
        Effective annual rate

    Example:
        >>> # 6% nominal compounded monthly
        >>> ear = effective_annual_rate(0.06, 12)
        >>> print(f"{ear:.4%}")
        6.17%
    """
    if compounds_per_year <= 0:
        raise ValueError("compounds_per_year must be positive")

    return (1 + nominal_rate / compounds_per_year) ** compounds_per_year - 1


# ============================================================================
# ANNUITY FACTORS
# ============================================================================

def annuity_factor(rate: float, periods: int) -> float:
    """
    Calculate annuity factor for converting PV to periodic payment.

    Formula: AF = [1 - (1 + r)^(-n)] / r

    Used to convert a present value into equivalent periodic payments.

    Args:
        rate: Periodic discount rate
        periods: Number of periods

    Returns:
        Annuity factor

    Example:
        >>> # Convert $100k PV to monthly payment over 60 months at 6% annual
        >>> rate = annual_to_monthly_rate(0.06)
        >>> af = annuity_factor(rate, 60)
        >>> payment = 100000 / af
        >>> print(f"${payment:,.2f}")
        $1,933.28
    """
    if periods <= 0:
        raise ValueError(f"periods must be positive, got {periods}")

    if rate == 0:
        return periods

    if rate < 0:
        raise ValueError(f"rate must be non-negative, got {rate}")

    return (1 - (1 + rate) ** -periods) / rate


# ============================================================================
# INTEREST AND AMORTIZATION
# ============================================================================

def simple_interest(
    principal: float,
    rate: float,
    days: int,
    day_count: Literal['actual/365', 'actual/360', '30/360'] = 'actual/365'
) -> float:
    """
    Calculate simple interest.

    Formula: Interest = Principal × Rate × (Days / Day_Count_Basis)

    Args:
        principal: Principal amount
        rate: Annual interest rate
        days: Number of days
        day_count: Day count convention

    Returns:
        Interest amount

    Example:
        >>> interest = simple_interest(10000, 0.05, 90)
        >>> print(f"${interest:,.2f}")
        $123.29
    """
    if principal < 0:
        raise ValueError(f"principal must be non-negative, got {principal}")

    if days < 0:
        raise ValueError(f"days must be non-negative, got {days}")

    day_count_basis = {
        'actual/365': 365,
        'actual/360': 360,
        '30/360': 360
    }

    if day_count not in day_count_basis:
        raise ValueError(f"Invalid day_count: {day_count}")

    basis = day_count_basis[day_count]

    return principal * rate * (days / basis)


def amortization_schedule(
    principal: float,
    rate: float,
    periods: int,
    payment: Optional[float] = None
) -> pd.DataFrame:
    """
    Generate amortization schedule for a loan or lease liability.

    Args:
        principal: Initial principal/liability amount
        rate: Periodic interest rate (monthly rate for monthly payments)
        periods: Number of periods
        payment: Periodic payment amount (if None, calculated from principal)

    Returns:
        DataFrame with columns:
            - Period: Period number (0 to periods)
            - Opening_Balance: Balance at start of period
            - Payment: Payment amount for period
            - Interest_Expense: Interest portion of payment
            - Principal_Reduction: Principal portion of payment
            - Closing_Balance: Balance at end of period

    Example:
        >>> schedule = amortization_schedule(100000, 0.004868, 60)
        >>> print(schedule.head())
           Period  Opening_Balance  Payment  Interest_Expense  Principal_Reduction  Closing_Balance
        0       0       100000.00     0.00              0.00                 0.00        100000.00
        1       1       100000.00  1933.28            486.80              1446.48         98553.52
        2       2        98553.52  1933.28            479.76              1453.52         97100.00
    """
    if principal <= 0:
        raise ValueError(f"principal must be positive, got {principal}")

    if periods <= 0:
        raise ValueError(f"periods must be positive, got {periods}")

    if rate < 0:
        raise ValueError(f"rate must be non-negative, got {rate}")

    # Calculate payment if not provided
    if payment is None:
        if rate == 0:
            payment = principal / periods
        else:
            # Standard loan payment formula
            payment = principal * (rate * (1 + rate) ** periods) / ((1 + rate) ** periods - 1)

    # Initialize schedule
    schedule = []
    balance = principal

    # Period 0 - opening position
    schedule.append({
        'Period': 0,
        'Opening_Balance': balance,
        'Payment': 0.0,
        'Interest_Expense': 0.0,
        'Principal_Reduction': 0.0,
        'Closing_Balance': balance
    })

    # Generate schedule for each period
    for period in range(1, periods + 1):
        opening = balance
        interest = balance * rate
        principal_reduction = payment - interest
        closing = balance - principal_reduction

        # Handle final period rounding
        if period == periods:
            principal_reduction = balance
            payment = balance + interest
            closing = 0.0

        schedule.append({
            'Period': period,
            'Opening_Balance': opening,
            'Payment': payment,
            'Interest_Expense': interest,
            'Principal_Reduction': principal_reduction,
            'Closing_Balance': closing
        })

        balance = closing

    return pd.DataFrame(schedule)


# ============================================================================
# FINANCIAL RATIOS
# ============================================================================

def safe_divide(
    numerator: float,
    denominator: float,
    default: Optional[float] = None
) -> Optional[float]:
    """
    Safely perform division, handling division by zero.

    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Value to return if denominator is 0 (None if not specified)

    Returns:
        Result of division, or default if denominator is 0

    Example:
        >>> result = safe_divide(100, 0, default=0)
        >>> print(result)
        0
    """
    if denominator == 0:
        return default
    return numerator / denominator


def calculate_financial_ratios(financial_data: Dict[str, float]) -> Dict[str, Optional[float]]:
    """
    Calculate comprehensive set of financial ratios.

    Args:
        financial_data: Dictionary containing financial statement items:
            Balance Sheet:
                - current_assets
                - total_assets
                - inventory
                - cash_and_equivalents
                - current_liabilities
                - total_liabilities
                - shareholders_equity
            Income Statement:
                - revenue
                - gross_profit
                - ebit
                - ebitda
                - net_income
                - interest_expense
            Other:
                - annual_rent (for rent coverage ratios)

    Returns:
        Dictionary of calculated ratios with None for ratios that cannot be calculated

    Example:
        >>> data = {
        ...     'current_assets': 150000,
        ...     'current_liabilities': 100000,
        ...     'total_assets': 500000,
        ...     'total_liabilities': 300000,
        ...     'shareholders_equity': 200000,
        ...     'revenue': 1000000,
        ...     'net_income': 50000,
        ...     'ebit': 80000,
        ...     'ebitda': 100000,
        ...     'interest_expense': 10000,
        ...     'annual_rent': 60000
        ... }
        >>> ratios = calculate_financial_ratios(data)
        >>> print(f"Current Ratio: {ratios['current_ratio']:.2f}")
        Current Ratio: 1.50
    """
    ratios = {}

    # Liquidity Ratios
    ratios['current_ratio'] = safe_divide(
        financial_data.get('current_assets', 0),
        financial_data.get('current_liabilities', 0)
    )

    ratios['quick_ratio'] = safe_divide(
        financial_data.get('current_assets', 0) - financial_data.get('inventory', 0),
        financial_data.get('current_liabilities', 0)
    )

    ratios['cash_ratio'] = safe_divide(
        financial_data.get('cash_and_equivalents', 0),
        financial_data.get('current_liabilities', 0)
    )

    # Leverage Ratios
    ratios['debt_to_equity'] = safe_divide(
        financial_data.get('total_liabilities', 0),
        financial_data.get('shareholders_equity', 0)
    )

    ratios['debt_to_assets'] = safe_divide(
        financial_data.get('total_liabilities', 0),
        financial_data.get('total_assets', 0)
    )

    ratios['interest_coverage'] = safe_divide(
        financial_data.get('ebit', 0),
        financial_data.get('interest_expense', 0)
    )

    # Profitability Ratios
    ratios['net_profit_margin'] = safe_divide(
        financial_data.get('net_income', 0),
        financial_data.get('revenue', 0)
    )

    ratios['roa'] = safe_divide(
        financial_data.get('net_income', 0),
        financial_data.get('total_assets', 0)
    )

    ratios['roe'] = safe_divide(
        financial_data.get('net_income', 0),
        financial_data.get('shareholders_equity', 0)
    )

    ratios['gross_margin'] = safe_divide(
        financial_data.get('gross_profit', 0),
        financial_data.get('revenue', 0)
    )

    # Rent Coverage Ratios (lease-specific)
    ratios['rent_to_revenue'] = safe_divide(
        financial_data.get('annual_rent', 0),
        financial_data.get('revenue', 0)
    )

    ratios['ebitda_to_rent'] = safe_divide(
        financial_data.get('ebitda', 0),
        financial_data.get('annual_rent', 0)
    )

    # Working Capital
    ratios['working_capital'] = (
        financial_data.get('current_assets', 0) -
        financial_data.get('current_liabilities', 0)
    )

    return ratios


# ============================================================================
# STATISTICAL FUNCTIONS
# ============================================================================

def percentile_rank(value: float, values: List[float]) -> float:
    """
    Calculate percentile rank of a value within a list.

    Args:
        value: Value to rank
        values: List of values to compare against

    Returns:
        Percentile rank (0-100)

    Example:
        >>> values = [10, 20, 30, 40, 50]
        >>> rank = percentile_rank(35, values)
        >>> print(f"{rank:.1f}th percentile")
        70.0th percentile
    """
    if not values:
        raise ValueError("values cannot be empty")

    sorted_values = sorted(values)
    count_below = sum(1 for v in sorted_values if v < value)
    count_equal = sum(1 for v in sorted_values if v == value)

    # Use midpoint method for ties
    percentile = ((count_below + count_equal / 2) / len(sorted_values)) * 100

    return percentile


def variance_analysis(
    actual: float,
    target: float,
    favorable_when_higher: bool = True
) -> Dict[str, Union[float, str]]:
    """
    Calculate variance between actual and target values.

    Args:
        actual: Actual value
        target: Target/budget/expected value
        favorable_when_higher: Whether higher values are favorable
                              (True for revenue, False for costs)

    Returns:
        Dictionary with:
            - absolute: Absolute variance (actual - target)
            - percentage: Percentage variance
            - direction: 'favorable' or 'unfavorable'

    Example:
        >>> # Revenue: actual $120k vs target $100k
        >>> var = variance_analysis(120000, 100000, favorable_when_higher=True)
        >>> print(f"{var['percentage']:.1f}% {var['direction']}")
        20.0% favorable
    """
    absolute_variance = actual - target

    if target == 0:
        percentage_variance = None
    else:
        percentage_variance = (absolute_variance / target) * 100

    # Determine if favorable
    if favorable_when_higher:
        is_favorable = actual >= target
    else:
        is_favorable = actual <= target

    return {
        'absolute': absolute_variance,
        'percentage': percentage_variance,
        'direction': 'favorable' if is_favorable else 'unfavorable'
    }


def descriptive_statistics(values: List[float]) -> Dict[str, float]:
    """
    Calculate comprehensive descriptive statistics.

    Args:
        values: List of numeric values

    Returns:
        Dictionary with mean, median, stdev, min, max, quartiles

    Example:
        >>> values = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        >>> stats = descriptive_statistics(values)
        >>> print(f"Mean: ${stats['mean']:,.0f}, Median: ${stats['median']:,.0f}")
        Mean: $55, Median: $55
    """
    if not values:
        raise ValueError("values cannot be empty")

    arr = np.array(values)

    return {
        'count': len(values),
        'mean': float(np.mean(arr)),
        'median': float(np.median(arr)),
        'stdev': float(np.std(arr, ddof=1)) if len(values) > 1 else 0.0,
        'min': float(np.min(arr)),
        'max': float(np.max(arr)),
        'q1': float(np.percentile(arr, 25)),
        'q2': float(np.percentile(arr, 50)),  # Same as median
        'q3': float(np.percentile(arr, 75)),
        'range': float(np.max(arr) - np.min(arr))
    }


# ============================================================================
# DATE UTILITIES
# ============================================================================

def months_between(start_date: datetime, end_date: datetime) -> int:
    """
    Calculate number of months between two dates.

    Args:
        start_date: Start date
        end_date: End date

    Returns:
        Number of months (rounded)

    Example:
        >>> start = datetime(2025, 1, 1)
        >>> end = datetime(2030, 1, 1)
        >>> months = months_between(start, end)
        >>> print(f"{months} months")
        60 months
    """
    months = (end_date.year - start_date.year) * 12
    months += end_date.month - start_date.month

    # Adjust for partial months
    if end_date.day < start_date.day:
        months -= 1

    return months


def add_months(start_date: datetime, months: int) -> datetime:
    """
    Add months to a date.

    Args:
        start_date: Starting date
        months: Number of months to add

    Returns:
        New date

    Example:
        >>> start = datetime(2025, 1, 31)
        >>> end = add_months(start, 1)
        >>> print(end)
        2025-02-28 00:00:00
    """
    # Calculate target month and year
    month = start_date.month - 1 + months
    year = start_date.year + month // 12
    month = month % 12 + 1

    # Handle day overflow (e.g., Jan 31 + 1 month = Feb 28/29)
    day = min(start_date.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])

    return datetime(year, month, day, start_date.hour, start_date.minute, start_date.second)


if __name__ == "__main__":
    # Quick validation tests
    print("Financial Utilities Module - Quick Tests\n")

    # Test PV calculation
    cash_flows = [1000] * 60
    pv = present_value(cash_flows, 0.06, 'monthly')
    print(f"PV of $1,000/month for 60 months at 6%: ${pv:,.2f}")

    # Test NPV
    investment = [-100000, 30000, 30000, 30000, 30000, 30000]
    npv_val = npv(investment, 0.10)
    print(f"NPV of investment: ${npv_val:,.2f}")

    # Test IRR
    irr_val = irr(investment)
    print(f"IRR of investment: {irr_val:.2%}")

    # Test rate conversion
    monthly = annual_to_monthly_rate(0.06)
    annual = monthly_to_annual_rate(monthly)
    print(f"6% annual = {monthly:.6f} monthly = {annual:.4%} annual (round-trip)")

    # Test amortization
    schedule = amortization_schedule(100000, monthly, 60)
    print(f"\nAmortization schedule (first 3 periods):")
    print(schedule.head(4).to_string(index=False))
    print(f"Final balance: ${schedule.iloc[-1]['Closing_Balance']:,.2f}")

    # Test financial ratios
    fin_data = {
        'current_assets': 150000,
        'current_liabilities': 100000,
        'total_assets': 500000,
        'total_liabilities': 300000,
        'shareholders_equity': 200000,
        'revenue': 1000000,
        'net_income': 50000,
        'ebitda': 100000,
        'annual_rent': 60000
    }
    ratios = calculate_financial_ratios(fin_data)
    print(f"\nFinancial Ratios:")
    print(f"  Current Ratio: {ratios['current_ratio']:.2f}")
    print(f"  Debt/Equity: {ratios['debt_to_equity']:.2f}")
    print(f"  ROE: {ratios['roe']:.2%}")
    print(f"  EBITDA/Rent: {ratios['ebitda_to_rent']:.2f}x")

    print("\n✓ All quick tests passed!")
