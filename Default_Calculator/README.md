# Default Damage Calculator

**Version**: 1.0.0
**Date**: 2025-11-06
**Author**: Claude Code

---

## Overview

The Default Damage Calculator quantifies landlord damages from tenant default, including:

- **Accelerated Rent** - NPV of remaining lease payments
- **Re-leasing Costs** - TI allowance, leasing commissions, legal fees
- **Lost Rent** - Downtime during vacancy period
- **Mitigation Credits** - Security deposit and re-lease rent offset
- **Bankruptcy Scenarios** - Trustee rejection claims under §502(b)(6)
- **Formal Notices** - Default notice generation with damage breakdown

---

## Quick Start

### 1. Calculate Damages

```bash
# Run damage analysis
python default_calculator.py default_inputs/sample_default_monetary.json

# Output: sample_default_monetary_results.json
```

### 2. Generate Default Notice

```bash
# Generate formal notice of default
python notice_generator.py default_inputs/sample_default_monetary.json

# Output: Reports/YYYY-MM-DD_HHMMSS_default_notice_*.md
```

### 3. Run Tests

```bash
cd Tests
python test_default_calculator.py
```

---

## Input Format

### JSON Structure

```json
{
  "lease_terms": {
    "property_address": "123 Industrial Parkway, Mississauga, ON",
    "tenant_name": "Acme Distribution Ltd.",
    "landlord_name": "Industrial Properties Inc.",

    "current_monthly_rent": 25000.00,
    "current_annual_rent": 300000.00,
    "rentable_area_sf": 50000,
    "rent_per_sf": 6.00,

    "lease_commencement_date": "2023-01-01",
    "lease_expiry_date": "2028-12-31",
    "remaining_months": 36,

    "additional_rent_annual": 75000.00,
    "security_deposit": 50000.00,

    "monetary_default_cure_days": 5,
    "non_monetary_default_cure_days": 15,

    "market_rent_sf": 7.00,
    "ti_allowance_sf": 15.00,
    "leasing_commission_pct": 0.05,
    "legal_fees": 5000.00,
    "downtime_months": 6,

    "discount_rate_annual": 0.10
  },

  "default_event": {
    "default_date": "2025-11-01",
    "default_type": "monetary",
    "description": "Failure to pay base rent",
    "amount_owing": 25000.00,
    "cure_period_days": 5,
    "cure_deadline": "2025-11-11"
  }
}
```

### Required Fields

**Lease Terms:**
- `property_address` (string) - Property location
- `tenant_name` (string) - Tenant legal name
- `landlord_name` (string) - Landlord legal name
- `current_monthly_rent` (number) - Current monthly base rent
- `current_annual_rent` (number) - Annual base rent
- `rentable_area_sf` (number) - Rentable square footage
- `rent_per_sf` (number) - Rent per square foot
- `lease_commencement_date` (date) - Lease start date (YYYY-MM-DD)
- `lease_expiry_date` (date) - Lease expiration date
- `remaining_months` (number) - Months remaining on lease term

**Default Event:**
- `default_date` (date) - Date of default
- `default_type` (string) - "monetary" or "non-monetary"
- `description` (string) - Description of default
- `amount_owing` (number) - Amount owing (required for monetary defaults)

**Optional Fields:**
- `additional_rent_annual` (number) - Taxes, opex, CAM (default: 0)
- `security_deposit` (number) - Security deposit amount (default: 0)
- `market_rent_sf` (number) - Current market rent/SF (default: 0)
- `ti_allowance_sf` (number) - TI allowance/SF (default: 15.00)
- `leasing_commission_pct` (number) - Commission % (default: 0.05)
- `legal_fees` (number) - Legal fees for new lease (default: 5000)
- `downtime_months` (number) - Expected vacancy (default: 6)
- `discount_rate_annual` (number) - NPV discount rate (default: 0.10)

---

## Damage Calculation Methodology

### 1. Accelerated Rent (NPV)

Present value of all remaining lease payments from default date to lease expiry.

```
NPV = Σ (Monthly Rent + Additional Rent) / (1 + r)^t
```

Where:
- `r` = Monthly discount rate
- `t` = Month number (1 to remaining_months)

**Example**: 36 months remaining at $31,250/month total rent, 10% discount rate:
```
NPV ≈ $1,042,000 (vs. $1,125,000 undiscounted)
```

### 2. Re-leasing Costs

Costs to re-lease premises to new tenant:

**Tenant Improvements (TI)**:
```
TI Cost = Rentable Area SF × TI Allowance $/SF
```

**Leasing Commissions**:
```
Commission = (Market Rent Annual × New Lease Term Years) × Commission %
```

**Legal Fees**: Fixed amount for new lease preparation

**Example**: 50,000 SF at $15/SF TI, $350k annual rent, 5-year term, 5% commission:
```
TI Cost        = 50,000 × $15.00 = $750,000
Commission     = ($350,000 × 5) × 0.05 = $87,500
Legal Fees     = $5,000
Total Re-lease = $842,500
```

### 3. Lost Rent During Downtime

Rent lost during vacancy period before re-leasing:

```
Lost Rent = Current Monthly Rent × Downtime Months
```

**Example**: $25,000/month × 6 months = $150,000

### 4. Mitigation Credits

Landlord has duty to mitigate damages by re-leasing premises.

**Security Deposit**:
Applied against damages (typically first source of recovery).

**Re-lease Rent Credit (NPV)**:
Present value of new lease rent that overlaps with old lease term.

```
Credit = PV(New Lease Rent) from end of downtime to old lease expiry
```

**Example**: Re-lease at $30k/month after 6-month downtime, 36 months remaining:
- Overlap period: 30 months (36 - 6)
- Credit NPV: ≈ $790,000 at 10% discount rate

### 5. Net Damages

```
Net Damages = Gross Damages - Total Credits
```

**Gross Damages** = Unpaid Rent + Accelerated Rent + Lost Rent + Re-leasing Costs

**Total Credits** = Security Deposit + Re-lease Rent Credit

---

## Bankruptcy Scenarios

### Trustee Rejection under §502(b)(6)

When tenant files bankruptcy, trustee may reject lease. Landlord claim is capped:

**Priority Claim (60 days)**:
```
Priority = 2 months × Total Monthly Rent
```
Recovery: Typically 100% (administrative expense priority)

**Unsecured Claim (Statutory Cap)**:
```
Cap = MAX(1 year rent, 15% × MIN(remaining rent, 3 years rent))
```

**Example**: $31,250/month total rent, 36 months remaining:
- 1 year rent = $375,000
- 15% of 36 months = $168,750
- **Statutory cap** = $375,000 (greater of two)

**Recovery Rates**:
- Priority claim: 100%
- Unsecured claim: 10-30% (typically 20%)

**Example Calculation**:
```
Priority Claim:     $62,500 × 100% = $62,500
Unsecured Claim:   $375,000 × 20%  = $75,000
Expected Recovery:                   $137,500
Expected Loss:     $1,000,000 - $137,500 = $862,500
```

### Preference Period

Payments received within 90 days of bankruptcy filing may be clawed back as preferential transfers.

```
At-Risk Amount = 3 months × Total Monthly Rent
```

---

## Default Notice Generation

### Notice Components

1. **Header**: Date, parties, lease reference
2. **Statement of Default**: Type, date, description, amount owing
3. **Cure Demand**: Cure deadline, required performance
4. **Damage Breakdown**: Itemized table of all damages
5. **Bankruptcy Warning**: Expected recovery in bankruptcy
6. **Reservation of Rights**: Preserves all landlord remedies
7. **Legal Framework**: Jurisdiction-specific citations

### Sample Notice Structure

```markdown
# NOTICE OF DEFAULT

**TO**: Acme Distribution Ltd.
**FROM**: Industrial Properties Inc.
**RE**: Lease dated January 1, 2023

## NOTICE IS HEREBY GIVEN:

You are in DEFAULT of the Lease...

## DEMAND FOR CURE

Remedy default by [CURE DEADLINE]...

## NOTICE OF DAMAGES

| Category | Description | Amount |
|----------|-------------|--------|
| Immediate | Unpaid Rent | $25,000 |
| Future | Accelerated Rent (NPV) | $1,042,000 |
| Future | Lost Rent | $150,000 |
| Re-leasing | TI Costs | $750,000 |
| Re-leasing | Commissions | $87,500 |
| Re-leasing | Legal | $5,000 |
| **GROSS DAMAGES** | | **$2,059,500** |

### Credits

| Credit | Security Deposit | $(50,000) |
| Credit | Re-lease Rent (NPV) | $(790,000) |
| **NET DAMAGES** | | **$1,219,500** |

## BANKRUPTCY CONSIDERATIONS

Priority Claim: $62,500
Expected Recovery: $137,500
Expected Loss: $862,500

## RESERVATION OF RIGHTS

All rights and remedies preserved...
```

---

## Output Files

### 1. JSON Results

**File**: `*_results.json`

Contains:
- Lease terms summary
- Default event details
- Complete damage breakdown (immediate, future, re-leasing, credits)
- Bankruptcy scenario analysis
- Totals (gross, credits, net)

### 2. Markdown Notice

**File**: `Reports/YYYY-MM-DD_HHMMSS_default_notice_*.md`

Contains:
- Formal legal notice of default
- Itemized damage table
- Cure demand with deadline
- Bankruptcy recovery analysis
- Jurisdiction-specific legal framework

---

## Examples

### Example 1: Monetary Default

```bash
# Calculate damages for unpaid rent
python default_calculator.py default_inputs/sample_default_monetary.json

# Output:
#   Gross damages: $2,059,500
#   Net damages: $1,219,500
#   Expected bankruptcy recovery: $137,500
```

### Example 2: Non-Monetary Default

```json
{
  "default_event": {
    "default_date": "2025-11-01",
    "default_type": "non-monetary",
    "description": "Unauthorized alterations to HVAC system",
    "amount_owing": 0.0,
    "cure_period_days": 15
  }
}
```

### Example 3: Short Remaining Term

```json
{
  "lease_terms": {
    ...
    "remaining_months": 6,
    ...
  }
}
```

Result: Lower accelerated rent, potentially no mitigation credit if downtime exceeds remaining term.

---

## Programmatic Usage

### Python API

```python
from default_calculator import (
    LeaseTerms,
    DefaultEvent,
    calculate_default_damages
)

# Create lease terms
lease = LeaseTerms(
    property_address="123 Test St",
    tenant_name="Test Tenant",
    landlord_name="Test Landlord",
    current_monthly_rent=25000,
    current_annual_rent=300000,
    rentable_area_sf=50000,
    rent_per_sf=6.00,
    lease_commencement_date=date(2023, 1, 1),
    lease_expiry_date=date(2028, 12, 31),
    remaining_months=36,
    additional_rent_annual=75000,
    security_deposit=50000,
    market_rent_sf=7.00,
    downtime_months=6,
    discount_rate_annual=0.10
)

# Create default event
default = DefaultEvent(
    default_date=date(2025, 11, 1),
    default_type="monetary",
    description="Failure to pay rent",
    amount_owing=25000,
    cure_period_days=5
)

# Calculate damages
results = calculate_default_damages(lease, default)

# Access results
print(f"Gross damages: ${results.damage_calculation.gross_damages:,.2f}")
print(f"Net damages: ${results.damage_calculation.net_damages:,.2f}")

# Bankruptcy scenario
bk = results.bankruptcy_scenarios[0]
print(f"Expected recovery: ${bk.expected_recovery:,.2f}")
print(f"Expected loss: ${bk.expected_loss:,.2f}")
```

---

## Testing

### Unit Tests

```bash
cd Tests
python test_default_calculator.py
```

### Test Coverage

- **TestAcceleratedRentNPV** (5 tests) - NPV calculations, discount rates
- **TestReLeasingCosts** (3 tests) - TI, commissions, legal fees
- **TestMitigationCredit** (4 tests) - Re-lease timing, market rent impact
- **TestBankruptcyClaims** (4 tests) - §502(b)(6) caps, recovery rates
- **TestFullDamageCalculation** (7 tests) - End-to-end scenarios
- **TestEdgeCases** (9 tests) - Boundary conditions, invalid inputs
- **TestDataValidation** (2 tests) - Data structure validation

**Total**: 34 tests

---

## Key Legal Considerations

### 1. Mitigation Duty

Landlord has **duty to mitigate** damages by making reasonable efforts to re-lease premises. Failure to mitigate may reduce recovery.

### 2. Accelerated Rent

Most jurisdictions allow landlord to claim **present value** of remaining lease payments, but require discounting to present value.

### 3. Bankruptcy Cap (§502(b)(6))

US Bankruptcy Code caps landlord claims:
- Greater of 1 year rent OR 15% of remaining rent (max 3 years)
- Plus 60-day priority claim

Canada: Different rules under BIA (no statutory cap, but mitigation required).

### 4. Preference Period

Payments within 90 days of bankruptcy filing may be clawed back (US: §547; Canada: BIA s. 95-96).

### 5. Security Deposit

Applied first against damages. May be insufficient to cover full damages in default scenarios.

---

## Assumptions and Limitations

### Assumptions

1. **Discount Rate**: Default 10% annual (adjust based on risk profile)
2. **Downtime**: Default 6 months (varies by market, property type, size)
3. **Market Rent**: User-provided or assumed equal to current rent
4. **New Lease Term**: Assumes 5-year term for commission calculations
5. **Bankruptcy Recovery**: 20% unsecured recovery (conservative estimate)

### Limitations

1. **No Lease Curves**: Assumes flat rent (doesn't model rent steps, CPI escalations)
2. **No Seasonal Effects**: Doesn't account for lease-up seasonality
3. **Simplified Bankruptcy**: Uses basic §502(b)(6) model (doesn't model administrative claims, adequate protection)
4. **No Guarantees**: Doesn't factor in personal guarantees, letters of credit
5. **Single Discount Rate**: Uses single rate (doesn't use different rates for different cash flows)

---

## Best Practices

1. **Update Market Rent**: Use current comparable data for accurate mitigation credits
2. **Document Mitigation**: Keep records of re-leasing efforts to defend against mitigation challenges
3. **Review Cure Periods**: Verify cure periods in lease match input data
4. **Consult Counsel**: This tool provides calculations only; consult legal counsel for notice requirements and enforcement actions
5. **Model Scenarios**: Run multiple scenarios (optimistic/pessimistic downtime, recovery rates)

---

## Troubleshooting

### Common Errors

**Error: "Invalid default type"**
- Cause: default_type must be "monetary" or "non-monetary"
- Fix: Use correct default_type value

**Error: "Monetary default requires positive amount"**
- Cause: amount_owing must be >0 for monetary defaults
- Fix: Specify unpaid amount

**Error: "Discount rate must be 0-1"**
- Cause: Discount rate entered as percentage (e.g., 10 instead of 0.10)
- Fix: Use decimal format (0.10 for 10%)

---

## Version History

### v1.0.0 (2025-11-06)
- Initial release
- Accelerated rent NPV calculation
- Re-leasing cost modeling
- Mitigation credit calculation
- Bankruptcy scenario analysis (§502(b)(6))
- Default notice generation
- Comprehensive test suite (34 tests)

---

## License

Apache License 2.0 - See LICENSE file for details.
