# IFRS 16 / ASC 842 Lease Accounting Calculator

**File**: `ifrs16_calculator.py`
**Status**: ✅ Complete
**Tests**: 31/31 passing (100%)
**Coverage**: Comprehensive unit tests in `Tests/test_ifrs16_calculator.py`

## Overview

Complete lease accounting calculator implementing IFRS 16 (International) and ASC 842 (US GAAP) standards. Calculates lease liability, right-of-use (ROU) asset, and generates complete amortization and depreciation schedules.

## Quick Start

```python
from ifrs16_calculator import LeaseInputs, calculate_ifrs16, print_summary

# Define lease parameters
inputs = LeaseInputs(
    monthly_payments=[10000] * 60,  # $10k/month for 5 years
    annual_discount_rate=0.055,     # 5.5% incremental borrowing rate
    initial_direct_costs=15000,     # Broker fees, legal costs
    lease_incentives=25000,         # Landlord cash incentive
    tenant_name="Example Corp",
    property_address="123 Main Street",
    payment_timing='beginning'      # Rent paid in advance
)

# Calculate
result = calculate_ifrs16(inputs)

# Display summary
print_summary(result)

# Access results
print(f"Lease Liability: ${result.initial_lease_liability:,.2f}")
print(f"ROU Asset: ${result.initial_rou_asset:,.2f}")
print(f"Total Interest Expense: ${result.total_interest_expense:,.2f}")
```

## Core Concepts

### IFRS 16 vs ASC 842

Both standards have converged on lease accounting treatment:

| Aspect | IFRS 16 | ASC 842 | Implementation |
|--------|---------|---------|----------------|
| **Lessee accounting** | Single model | Finance/Operating split | Single model (works for both) |
| **Lease liability** | PV of payments | PV of payments | ✓ Implemented |
| **ROU asset** | Liability + costs - incentives | Same | ✓ Implemented |
| **Discount rate** | Rate implicit or IBR | Same | ✓ User provides |
| **Depreciation** | Straight-line or usage | Straight-line | ✓ Straight-line |

**Note**: This calculator uses the single model approach which is required under IFRS 16 and can be used for finance leases under ASC 842. For ASC 842 operating leases, additional adjustments may be needed.

### Payment Timing

**Annuity Due (Beginning of Period)** - Default for commercial leases:
- First payment made at lease commencement
- First payment is NOT included in lease liability (already paid)
- Liability = PV of remaining 59 payments (for 60-month lease)
- Most commercial leases use this timing

**Ordinary Annuity (End of Period)** - Less common:
- All payments are future obligations
- Liability = PV of all 60 payments
- Sometimes used for equipment leases

### Key Formulas

#### Lease Liability (Annuity Due)
```
For constant payments:
  Lease Liability = PV of (n-1) payments at end of period

For variable payments:
  Lease Liability = Σ [Payment_t / (1 + r)^t] for t = 1 to n-1

Where:
  - First payment (t=0) excluded because paid at commencement
  - r = monthly discount rate
  - n = total number of payments
```

#### ROU Asset
```
ROU Asset = Lease Liability
          + Initial Direct Costs    (broker fees, legal)
          + Prepaid Rent           (advance payments)
          - Lease Incentives       (cash from landlord)
```

#### Monthly Amortization
```
For each period t:
  Interest Expense = Opening Balance × Monthly Rate
  Principal Reduction = Payment - Interest Expense
  Closing Balance = Opening Balance - Principal Reduction
```

#### Monthly Depreciation
```
Monthly Depreciation = ROU Asset / Lease Term (months)

Accumulated Depreciation = Σ Monthly Depreciation
Net Book Value = ROU Asset - Accumulated Depreciation
```

## Main Functions

### 1. calculate_ifrs16()

Complete end-to-end calculation.

```python
from ifrs16_calculator import LeaseInputs, calculate_ifrs16

inputs = LeaseInputs(
    monthly_payments=[10000] * 60,
    annual_discount_rate=0.055,
    initial_direct_costs=15000,
    lease_incentives=25000,
    payment_timing='beginning'
)

result = calculate_ifrs16(inputs)

# Access results
print(f"Initial liability: ${result.initial_lease_liability:,.2f}")
print(f"Initial ROU asset: ${result.initial_rou_asset:,.2f}")
print(f"Total interest: ${result.total_interest_expense:,.2f}")
print(f"Total depreciation: ${result.total_depreciation:,.2f}")

# Access schedules
amortization = result.amortization_schedule  # DataFrame
depreciation = result.depreciation_schedule  # DataFrame
annual_summary = result.annual_summary       # DataFrame
```

**Returns**: `LeaseAccountingResult` object with:
- `initial_lease_liability`: Initial lease liability
- `initial_rou_asset`: Initial ROU asset
- `total_interest_expense`: Total interest over lease term
- `total_depreciation`: Total depreciation over lease term
- `total_lease_cost`: Total P&L expense
- `amortization_schedule`: Monthly liability amortization (DataFrame)
- `depreciation_schedule`: Monthly ROU depreciation (DataFrame)
- `annual_summary`: Year-by-year summary (DataFrame)

### 2. calculate_lease_liability()

Calculate lease liability only.

```python
from ifrs16_calculator import calculate_lease_liability

payments = [10000] * 60
liability, monthly_rate = calculate_lease_liability(
    payments=payments,
    annual_rate=0.055,
    payment_timing='beginning'
)

print(f"Lease liability: ${liability:,.2f}")
print(f"Monthly rate: {monthly_rate:.4%}")
```

**Key behavior**:
- For `payment_timing='beginning'`: First payment excluded from liability
- For `payment_timing='end'`: All payments included in liability
- Handles variable payment schedules
- Returns both liability and calculated monthly rate

### 3. calculate_rou_asset()

Calculate ROU asset from liability and adjustments.

```python
from ifrs16_calculator import calculate_rou_asset

rou_asset, components = calculate_rou_asset(
    lease_liability=517575.53,
    initial_direct_costs=15000,
    prepaid_rent=0,
    lease_incentives=25000
)

print(f"ROU Asset: ${rou_asset:,.2f}")
print(f"Components: {components}")
```

**Components returned**:
```python
{
    'lease_liability': 517575.53,
    'initial_direct_costs': 15000.00,
    'prepaid_rent': 0.00,
    'lease_incentives': -25000.00,  # Negative because reduces asset
    'total_rou_asset': 507575.53
}
```

### 4. generate_liability_amortization()

Generate complete amortization schedule.

```python
from ifrs16_calculator import generate_liability_amortization
from datetime import datetime

schedule = generate_liability_amortization(
    initial_liability=517575.53,
    monthly_payments=[10000] * 60,
    monthly_rate=0.004472,
    commencement_date=datetime(2025, 1, 1),
    payment_timing='beginning'
)

print(schedule.head())
```

**Schedule columns**:
- `Period`: 0 to n (0 = commencement)
- `Date`: Date or "Month N"
- `Opening_Balance`: Lease liability at start of period
- `Payment`: Cash payment for the period
- `Interest_Expense`: Interest expense for the period
- `Principal_Reduction`: Reduction in liability
- `Closing_Balance`: Lease liability at end of period
- `Cumulative_Interest`: Running total of interest
- `Cumulative_Principal`: Running total of principal

**Key features**:
- Period 0 shows commencement (first payment for annuity due)
- Final balance rounds to zero
- All amounts rounded to 2 decimal places

### 5. generate_rou_depreciation()

Generate straight-line depreciation schedule.

```python
from ifrs16_calculator import generate_rou_depreciation
from datetime import datetime

schedule = generate_rou_depreciation(
    initial_rou_asset=507575.53,
    lease_term_months=60,
    commencement_date=datetime(2025, 1, 1)
)

print(schedule.head())
```

**Schedule columns**:
- `Period`: 0 to n
- `Date`: Date or "Month N"
- `Opening_NBV`: Net book value at start
- `Depreciation_Expense`: Monthly depreciation
- `Accumulated_Depreciation`: Cumulative depreciation
- `Closing_NBV`: Net book value at end

**Key features**:
- Constant monthly depreciation (straight-line)
- Final period depreciation adjusted to reach zero NBV
- Period 0 shows initial recognition (no depreciation)

### 6. create_annual_summary()

Create year-by-year summary.

```python
from ifrs16_calculator import create_annual_summary

annual = create_annual_summary(
    amortization=amortization_schedule,
    depreciation=depreciation_schedule,
    commencement_date=datetime(2025, 1, 1)
)

print(annual)
```

**Summary columns**:
- `Year`: Lease year (1 to n)
- `Cash_Paid`: Total cash payments
- `Interest_Expense`: Total interest expense
- `Depreciation_Expense`: Total depreciation
- `Total_Lease_Expense`: Interest + Depreciation
- `Principal_Reduction`: Total liability reduction

### 7. sensitivity_analysis()

Test impact of discount rate and term variations.

```python
from ifrs16_calculator import sensitivity_analysis

sensitivity = sensitivity_analysis(
    base_inputs,
    rate_variations=[-0.02, -0.01, 0, 0.01, 0.02],  # ±2%, ±1%, base
    term_variations=[-12, 0, 12]  # ±1 year, base
)

print(sensitivity)
```

**Output columns**:
- `Scenario`: Description (e.g., "Rate +1.0%", "Term -12 months")
- `Discount_Rate`: Annual rate for scenario
- `Lease_Term_Months`: Term for scenario
- `Lease_Liability`: Initial liability
- `ROU_Asset`: Initial ROU asset
- `Total_Interest`: Interest over term
- `Total_Depreciation`: Depreciation over term
- `Total_Cost`: Total P&L expense
- `Variance_from_Base`: Difference from base case

**Key insights**:
- Higher discount rate → Lower liability/asset
- Longer term → Higher liability/asset
- **Important**: When no initial costs/incentives, total cost ≈ total payments regardless of discount rate!

### 8. export_to_csv()

Export all schedules to CSV files.

```python
from ifrs16_calculator import export_to_csv

files = export_to_csv(result, output_dir="./output")

print(f"Files created: {files}")
# {
#     'amortization': './output/Example_Corp_lease_liability_amortization_20251030.csv',
#     'depreciation': './output/Example_Corp_rou_asset_depreciation_20251030.csv',
#     'annual_summary': './output/Example_Corp_annual_summary_20251030.csv'
# }
```

## Usage Examples

### Example 1: Simple 5-Year Office Lease

```python
from ifrs16_calculator import LeaseInputs, calculate_ifrs16, print_summary

# Typical office lease: $5,000/month, 5 years, 5.5% IBR
inputs = LeaseInputs(
    monthly_payments=[5000] * 60,
    annual_discount_rate=0.055,
    tenant_name="ABC Corp",
    property_address="Office Building",
    payment_timing='beginning'
)

result = calculate_ifrs16(inputs)
print_summary(result)
```

**Output**:
```
Initial Recognition:
  Lease Liability: $258,787.77
  ROU Asset: $258,787.77

Total Lease Cost (5 years):
  Interest Expense: $36,212.23
  Depreciation: $258,787.77
  Total: $295,000.00

Cash Payments: $300,000.00
Difference: ($5,000.00)  # First payment made at commencement
```

### Example 2: Lease with Incentive and Tenant Improvements

```python
# Landlord provides $50k incentive, tenant pays $30k in legal/broker fees
inputs = LeaseInputs(
    monthly_payments=[8000] * 60,
    annual_discount_rate=0.06,
    initial_direct_costs=30000,   # Legal, broker fees
    lease_incentives=50000,        # Landlord cash incentive
    payment_timing='beginning'
)

result = calculate_ifrs16(inputs)

print(f"Lease Liability: ${result.initial_lease_liability:,.2f}")
print(f"ROU Asset: ${result.initial_rou_asset:,.2f}")
# ROU Asset = Liability + 30k - 50k = Liability - 20k
```

### Example 3: Variable Rent with Annual Escalations

```python
# Base rent $10k/month, 3% annual escalation
payments = []
for year in range(5):
    monthly_rent = 10000 * (1.03 ** year)
    payments.extend([monthly_rent] * 12)

inputs = LeaseInputs(
    monthly_payments=payments,
    annual_discount_rate=0.055,
    payment_timing='beginning'
)

result = calculate_ifrs16(inputs)
# Handles variable payment schedule automatically
```

### Example 4: Free Rent Period

```python
# 3 months free rent, then $10k/month for 57 months
payments = [0, 0, 0] + [10000] * 57

inputs = LeaseInputs(
    monthly_payments=payments,
    annual_discount_rate=0.055,
    payment_timing='beginning'
)

result = calculate_ifrs16(inputs)
# Free rent periods included in calculation
```

### Example 5: Export to Excel-Ready CSV

```python
from ifrs16_calculator import calculate_ifrs16, export_to_csv
import pandas as pd

result = calculate_ifrs16(inputs)

# Export all schedules
files = export_to_csv(result, output_dir="./reports")

# Read back in Excel or pandas
amortization = pd.read_csv(files['amortization'])
depreciation = pd.read_csv(files['depreciation'])
annual = pd.read_csv(files['annual_summary'])
```

### Example 6: Sensitivity Analysis for Decision Making

```python
from ifrs16_calculator import sensitivity_analysis

# Compare impact of negotiating different terms
sensitivity = sensitivity_analysis(
    base_inputs,
    rate_variations=[0, 0.005, 0.01],  # Base, +0.5%, +1%
    term_variations=[0, -12, -24]      # Base, 1 year shorter, 2 years shorter
)

print(sensitivity[['Scenario', 'Lease_Liability', 'Total_Cost', 'Variance_from_Base']])
```

## Integration with Financial Utilities

The IFRS 16 calculator uses these functions from `financial_utils.py`:

```python
from financial_utils import (
    pv_annuity,              # Calculate PV of constant payment stream
    annual_to_monthly_rate,  # Convert annual rate to monthly (compound interest)
    present_value            # Calculate PV of variable payments
)
```

## Validation

### Test Coverage

**31 comprehensive tests** covering:
- ✅ Lease liability calculation (constant, variable, free rent)
- ✅ ROU asset calculation (with/without adjustments)
- ✅ Amortization schedules (final balance, principal totals, interest patterns)
- ✅ Depreciation schedules (straight-line, final NBV)
- ✅ Full calculation integration
- ✅ Annual summaries
- ✅ Sensitivity analysis
- ✅ CSV export
- ✅ Edge cases (single payment, short terms, errors)

Run tests:
```bash
cd /workspaces/lease-abstract/Eff_Rent_Calculator
python3 -m pytest Tests/test_ifrs16_calculator.py -v
```

### Excel Validation

Key validation points:
- ✅ Monthly rate conversion matches Excel `=(1+annual_rate)^(1/12)-1`
- ✅ PV calculations match Excel `PV()` function
- ✅ Amortization matches Excel amortization tables
- ✅ Final balances round to zero (within $10)

## Journal Entries

### Initial Recognition (Commencement Date)

```
Dr. Right-of-Use Asset               $507,575.53
    Cr. Lease Liability                           $517,575.53
    Cr. Cash (incentive received)                  $25,000.00
Dr. Right-of-Use Asset (initial costs) $15,000.00
    Cr. Cash                                       $15,000.00

Dr. Lease Liability (first payment)  $10,000.00
    Cr. Cash                                       $10,000.00
```

### Monthly Entries (Periods 1-60)

```
For each month:

Dr. Lease Liability                  $[Payment]
    Cr. Cash                                      $[Payment]

Dr. Interest Expense                 $[Interest]
    Cr. Lease Liability                           $[Interest]

Dr. Depreciation Expense             $[Depreciation]
    Cr. Accumulated Depreciation - ROU            $[Depreciation]
```

### End of Lease

```
Dr. Accumulated Depreciation - ROU   $507,575.53
    Cr. Right-of-Use Asset                        $507,575.53

Final lease liability should be $0.00
```

## Financial Statement Impact

### Balance Sheet

**Assets**:
```
Right-of-Use Asset (gross)               $507,575.53
Less: Accumulated Depreciation           ($XX,XXX.XX)
Right-of-Use Asset (net)                 $XXX,XXX.XX
```

**Liabilities**:
```
Current portion of lease liability       $ 94,529.11  (Year 1 principal)
Long-term lease liability                $423,046.42  (Years 2-5 principal)
Total lease liability                    $517,575.53
```

### Income Statement

**Operating Expenses**:
```
Depreciation - ROU Asset                 $101,515.08  (Year 1)
```

**Interest Expense**:
```
Interest on lease liability              $ 25,470.89  (Year 1)
```

**Total Lease Expense (Year 1)**: $126,985.97

### Cash Flow Statement

```
Operating Activities:
  Net Income                             $XXX,XXX.XX
  Add: Depreciation - ROU Asset          $101,515.08
  Less: Principal payments               ($94,529.11)

Financing Activities:
  Principal payments on lease liability  ($94,529.11)

  Interest payments                      ($25,470.89)
  (Classified as operating or financing depending on policy)
```

## Important Notes

### 1. Discount Rate Selection

**Rate implicit in the lease** (preferred):
- Rate that makes PV of payments + residual value = Fair value of asset
- Often not determinable for real estate leases

**Incremental borrowing rate (IBR)** (most common):
- Rate tenant would pay to borrow funds to purchase similar asset
- Consider: Tenant credit rating, lease term, security/collateral
- Often based on: Corporate bond rate + credit spread

### 2. Lease Term Determination

Include periods covered by:
- ✅ Non-cancellable period
- ✅ Extension options reasonably certain to exercise
- ✅ Termination options reasonably certain NOT to exercise
- ❌ Extension options not reasonably certain
- ❌ Month-to-month holdover periods

### 3. Payment Inclusions

**Include in lease liability**:
- ✅ Fixed rent payments
- ✅ Variable rent based on index/rate (using current rate)
- ✅ Residual value guarantees (expected to pay)
- ✅ Purchase option price (reasonably certain to exercise)
- ✅ Termination penalties (if term reflects termination)

**Exclude from lease liability**:
- ❌ Variable rent based on performance/usage
- ❌ Operating cost reimbursements (if separately stated)
- ❌ Future rent escalations not based on index (recognize as incurred)

### 4. Initial Direct Costs

**Include in ROU asset**:
- ✅ Broker commissions
- ✅ Legal fees for lease negotiation
- ✅ Payments made to obtain the lease

**Exclude from ROU asset**:
- ❌ Internal staff costs
- ❌ Legal fees for lease administration
- ❌ General overhead

### 5. Reassessment

Remeasure lease liability when:
- Lease term changes
- Purchase option assessment changes
- Residual value guarantee changes
- Variable rent based on index/rate changes

Update ROU asset for:
- Changes in lease liability (except variable rent changes)
- Lease modifications

### 6. Short-Term and Low-Value Leases

**Exemptions available** (practical expedient):
- Short-term leases (≤12 months, no purchase option)
- Low-value asset leases (≤$5,000 new value)

If exemption elected:
- Recognize lease payments as expense on straight-line basis
- No lease liability or ROU asset

**This calculator**: Designed for leases that require recognition (not short-term/low-value)

## Limitations

1. **Single model only**: Implements IFRS 16 model (all leases same). For ASC 842 operating leases, expense pattern differs.

2. **Straight-line depreciation only**: Does not support usage-based depreciation methods.

3. **No residual values**: Does not include residual value guarantees or purchase options.

4. **No reassessment**: Initial calculation only; does not handle mid-lease modifications or reassessments.

5. **Monthly periods only**: Designed for monthly payments; annual or quarterly requires adjustment.

6. **No tax calculations**: Does not calculate deferred taxes or tax basis differences.

## Dependencies

```python
import numpy as np           # Numerical operations
import pandas as pd          # DataFrames for schedules
from datetime import datetime
```

Plus custom module:
```python
from financial_utils import pv_annuity, annual_to_monthly_rate, present_value
```

## Author

Generated by Claude Code
Date: 2025-10-30
GitHub Issue: #3

## References

- IFRS 16 Leases (IASB, 2016)
- ASC 842 Leases (FASB, 2016)
- `financial_utils.py` - Shared financial calculation module
- `README_FINANCIAL_UTILS.md` - Financial utilities documentation
