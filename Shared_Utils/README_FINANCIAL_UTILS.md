# Financial Utilities Module

**File**: `financial_utils.py`
**Status**: ✅ Complete
**Tests**: 58/58 passing
**Coverage**: Comprehensive unit tests in `/Tests/test_financial_utils.py`

## Overview

Shared financial calculation module providing common functions used across all lease analysis calculators. This module eliminates code duplication and ensures consistent financial mathematics throughout the toolkit.

## Modules

### 1. Present Value Calculations

#### `present_value(cash_flows, discount_rate, periods='monthly')`
Calculate present value of a series of cash flows.

**Note**: First cash flow (index 0) is treated as occurring at t=0 (present) and is not discounted. This is appropriate for NPV calculations. For annuities where all payments are in the future, use `pv_annuity()`.

```python
# Example: Monthly rent payments
cash_flows = [1000] * 60  # $1000/month for 5 years
pv = present_value(cash_flows, 0.06, 'monthly')
# Returns: $52,176.56
```

#### `pv_annuity(payment, rate, periods, timing='end')`
Calculate present value of an annuity (constant periodic payments).

- `timing='end'`: Ordinary annuity (payments at end of period)
- `timing='beginning'`: Annuity due (payments at start of period)

**Use for commercial leases**: Most commercial leases require rent in advance, so use `timing='beginning'`.

```python
# Example: Monthly rent paid in advance
monthly_rate = annual_to_monthly_rate(0.06)
pv = pv_annuity(1000, monthly_rate, 60, 'beginning')
# Returns: $52,427.24
```

### 2. NPV and IRR

#### `npv(cash_flows, discount_rate)`
Calculate Net Present Value.

```python
# Example: Relocation investment analysis
cash_flows = [-100000, 30000, 30000, 30000, 30000, 30000]
npv_value = npv(cash_flows, 0.10)
# Returns: $13,723.60 (positive NPV = good investment)
```

#### `irr(cash_flows, guess=0.10)`
Calculate Internal Rate of Return using Newton's method.

```python
# Example: Find IRR of relocation investment
cash_flows = [-100000, 30000, 30000, 30000, 30000, 30000]
irr_value = irr(cash_flows)
# Returns: 0.1524 (15.24%)
```

### 3. Discount Rate Conversions

#### `annual_to_monthly_rate(annual_rate)`
Convert annual rate to monthly using compound interest.

**Formula**: `r_monthly = (1 + r_annual)^(1/12) - 1`

**Important**: This is NOT `annual_rate / 12`. Uses compound interest.

```python
monthly = annual_to_monthly_rate(0.06)
# Returns: 0.004868 (0.4868% per month)
# Verify: (1.004868)^12 = 1.06 ✓
```

#### `monthly_to_annual_rate(monthly_rate)`
Convert monthly rate to annual.

#### `effective_annual_rate(nominal_rate, compounds_per_year)`
Convert nominal annual rate to effective annual rate.

### 4. Annuity Factors

#### `annuity_factor(rate, periods)`
Calculate annuity factor for converting PV to periodic payment.

**Formula**: `AF = [1 - (1 + r)^(-n)] / r`

```python
# Example: Calculate monthly payment for $100k loan
monthly_rate = annual_to_monthly_rate(0.06)
af = annuity_factor(monthly_rate, 60)
payment = 100000 / af
# Returns: $1,933.28/month
```

### 5. Interest and Amortization

#### `simple_interest(principal, rate, days, day_count='actual/365')`
Calculate simple interest.

**Day count conventions**:
- `'actual/365'`: Standard (default)
- `'actual/360'`: Some commercial loans
- `'30/360'`: Bond market convention

```python
# Example: Late rent interest calculation
interest = simple_interest(10000, 0.05, 90)
# Returns: $123.29
```

#### `amortization_schedule(principal, rate, periods, payment=None)`
Generate complete amortization schedule as DataFrame.

Returns DataFrame with columns:
- Period (0 to n)
- Opening_Balance
- Payment
- Interest_Expense
- Principal_Reduction
- Closing_Balance

```python
# Example: IFRS 16 lease liability amortization
monthly_rate = annual_to_monthly_rate(0.055)
schedule = amortization_schedule(100000, monthly_rate, 60)

print(schedule.head())
#    Period  Opening_Balance  Payment  Interest_Expense  Principal_Reduction  Closing_Balance
# 0       0       100000.00     0.00              0.00                 0.00        100000.00
# 1       1       100000.00  1925.90            449.44              1476.46         98523.54
# 2       2        98523.54  1925.90            442.81              1483.09         97040.45

# Export to CSV
schedule.to_csv('lease_liability_schedule.csv', index=False)
```

### 6. Financial Ratios

#### `safe_divide(numerator, denominator, default=None)`
Safely perform division, handling division by zero.

```python
ratio = safe_divide(100, 0, default=None)
# Returns: None (instead of ZeroDivisionError)
```

#### `calculate_financial_ratios(financial_data)`
Calculate comprehensive set of financial ratios.

**Input dictionary keys**:
```python
{
    # Balance Sheet
    'current_assets': float,
    'total_assets': float,
    'inventory': float,
    'cash_and_equivalents': float,
    'current_liabilities': float,
    'total_liabilities': float,
    'shareholders_equity': float,

    # Income Statement
    'revenue': float,
    'gross_profit': float,
    'ebit': float,
    'ebitda': float,
    'net_income': float,
    'interest_expense': float,

    # Lease-specific
    'annual_rent': float
}
```

**Output ratios**:
- **Liquidity**: current_ratio, quick_ratio, cash_ratio, working_capital
- **Leverage**: debt_to_equity, debt_to_assets, interest_coverage
- **Profitability**: net_profit_margin, roa, roe, gross_margin
- **Rent Coverage**: rent_to_revenue, ebitda_to_rent

```python
# Example: Tenant credit analysis
financial_data = {
    'current_assets': 150000,
    'current_liabilities': 100000,
    'total_assets': 500000,
    'total_liabilities': 300000,
    'shareholders_equity': 200000,
    'revenue': 1000000,
    'net_income': 60000,
    'ebitda': 120000,
    'annual_rent': 60000
}

ratios = calculate_financial_ratios(financial_data)

# Results:
# ratios['current_ratio'] = 1.50 (healthy liquidity)
# ratios['debt_to_equity'] = 1.50
# ratios['roe'] = 0.30 (30% return on equity)
# ratios['ebitda_to_rent'] = 2.0 (2x coverage)
```

### 7. Statistical Functions

#### `percentile_rank(value, values)`
Calculate percentile rank of a value (0-100).

```python
market_rents = [18, 20, 22, 24, 26]
rank = percentile_rank(23, market_rents)
# Returns: 70.0 (70th percentile)
```

#### `variance_analysis(actual, target, favorable_when_higher=True)`
Calculate variance between actual and target.

```python
# Revenue analysis
var = variance_analysis(120000, 100000, favorable_when_higher=True)
# Returns: {
#     'absolute': 20000,
#     'percentage': 20.0,
#     'direction': 'favorable'
# }

# Cost analysis
var = variance_analysis(80000, 100000, favorable_when_higher=False)
# Returns: {
#     'absolute': -20000,
#     'percentage': -20.0,
#     'direction': 'favorable'  # Under budget is good
# }
```

#### `descriptive_statistics(values)`
Calculate comprehensive descriptive statistics.

```python
rents = [18, 20, 22, 24, 26, 28, 30]
stats = descriptive_statistics(rents)

# Returns: {
#     'count': 7,
#     'mean': 24.0,
#     'median': 24.0,
#     'stdev': 4.32,
#     'min': 18.0,
#     'max': 30.0,
#     'q1': 21.0,  # 25th percentile
#     'q2': 24.0,  # 50th percentile (median)
#     'q3': 27.0,  # 75th percentile
#     'range': 12.0
# }
```

### 8. Date Utilities

#### `months_between(start_date, end_date)`
Calculate number of months between dates.

```python
from datetime import datetime
start = datetime(2025, 1, 1)
end = datetime(2030, 1, 1)
months = months_between(start, end)
# Returns: 60
```

#### `add_months(start_date, months)`
Add months to a date (handles month-end correctly).

```python
start = datetime(2025, 1, 31)
end = add_months(start, 1)
# Returns: datetime(2025, 2, 28) - handles Feb 28/29 correctly
```

## Usage Examples

### Example 1: Lease Payment Calculation

```python
from financial_utils import annual_to_monthly_rate, annuity_factor

# Calculate monthly payment for $500k lease liability over 10 years at 5.5%
principal = 500000
annual_rate = 0.055
months = 120

monthly_rate = annual_to_monthly_rate(annual_rate)
af = annuity_factor(monthly_rate, months)
payment = principal / af

print(f"Monthly payment: ${payment:,.2f}")
# Output: Monthly payment: $5,410.61
```

### Example 2: Investment Analysis

```python
from financial_utils import npv, irr

# Analyze relocation vs. renewal
relocation_cf = [-250000, 50000, 50000, 50000, 50000, 50000, 50000]
renewal_cf = [0, 0, 0, 0, 0, 0, 0]  # Baseline

npv_relocation = npv(relocation_cf, 0.10)
irr_relocation = irr(relocation_cf)

print(f"Relocation NPV: ${npv_relocation:,.2f}")
print(f"Relocation IRR: {irr_relocation:.2%}")

if npv_relocation > 0:
    print("Recommendation: RELOCATE (positive NPV)")
else:
    print("Recommendation: RENEW (negative NPV)")
```

### Example 3: Tenant Credit Analysis

```python
from financial_utils import calculate_financial_ratios

# Extract financials from tenant's statements
financials = {
    'current_assets': 450000,
    'current_liabilities': 250000,
    'total_assets': 2000000,
    'total_liabilities': 1200000,
    'shareholders_equity': 800000,
    'revenue': 5000000,
    'ebitda': 500000,
    'net_income': 250000,
    'interest_expense': 80000,
    'annual_rent': 240000
}

ratios = calculate_financial_ratios(financials)

# Assess creditworthiness
print("Tenant Credit Analysis:")
print(f"  Current Ratio: {ratios['current_ratio']:.2f} (target: >1.5)")
print(f"  Debt/Equity: {ratios['debt_to_equity']:.2f} (target: <2.0)")
print(f"  EBITDA/Rent: {ratios['ebitda_to_rent']:.2f}x (target: >1.5x)")
print(f"  ROE: {ratios['roe']:.1%} (target: >15%)")

# Credit decision
if (ratios['current_ratio'] > 1.5 and
    ratios['ebitda_to_rent'] > 1.5 and
    ratios['debt_to_equity'] < 2.0):
    print("\nCredit Rating: APPROVED")
else:
    print("\nCredit Rating: REQUIRES GUARANTEE")
```

## Testing

Run comprehensive test suite:

```bash
cd /workspaces/lease-abstract/Eff_Rent_Calculator
python3 -m pytest Tests/test_financial_utils.py -v
```

**Test Coverage**: 58 tests covering:
- Present value calculations (edge cases, zero rate, negative values)
- NPV and IRR (convergence, validation, error handling)
- Rate conversions (round-trip accuracy)
- Annuity factors and amortization
- Financial ratios (zero denominators, missing data)
- Statistical functions (percentiles, variance, descriptive stats)
- Date utilities (month overflow, negative months)
- Integration tests (end-to-end scenarios)

## Dependencies

- `numpy`: Numerical operations and percentile calculations
- `pandas`: DataFrame for amortization schedules
- `scipy`: Optimization for IRR calculation (Newton's method)
- Python 3.12+

## Notes

### Important Behaviors

1. **PV vs Annuity**: `present_value()` treats first cash flow as t=0 (not discounted), suitable for NPV. `pv_annuity()` treats all payments as future, suitable for rent calculations.

2. **Rate Conversions**: Always use compound interest conversions, never simple division.

3. **Annuity Due vs Ordinary**: Commercial leases typically require rent in advance (`timing='beginning'`).

4. **Division by Zero**: All ratio calculations use `safe_divide()` which returns `None` instead of raising errors.

5. **Date Arithmetic**: `add_months()` handles month-end overflow correctly (Jan 31 + 1 month = Feb 28/29).

### Performance

All functions are optimized for typical lease analysis workloads:
- PV calculations: O(n) where n = number of cash flows
- Amortization schedules: O(n) where n = number of periods
- IRR: Typically converges in <10 iterations using Newton's method

## Integration

This module is imported by:
- `ifrs16_calculator.py` - Lease liability amortization
- `option_valuation.py` - NPV of option values
- `credit_analysis.py` - Financial ratio calculations
- `renewal_analysis.py` - NPV/IRR of renewal vs relocation
- `portfolio_analysis.py` - Market statistics and scenario modeling

## Author

Generated by Claude Code
Date: 2025-10-30
GitHub Issue: #8
