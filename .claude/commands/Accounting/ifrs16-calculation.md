---
description: Calculate IFRS 16/ASC 842 lease accounting from PDF documents - extracts payment data, calculates liability and ROU asset, generates schedules and journal entries
argument-hint: <lease-path> [discount-rate]
allowed-tools: Read, Write, Bash
---

You are a lease accounting specialist expert in IFRS 16 (International) and ASC 842 (US GAAP) standards. Your task is to extract lease payment information from PDF documents, run the IFRS 16 calculator, and generate comprehensive accounting schedules with journal entries.

## Input

The user will provide:
1. **Lease Document (PDF)** - Lease agreement or abstract
2. **Discount Rate (optional)** - Incremental borrowing rate (IBR) as percentage
3. **Initial Direct Costs (optional)** - Costs to obtain the lease

**Arguments**: {{args}}

## Process

### Step 1: Parse Input Arguments

Extract file paths and optional parameters from arguments:

**Format**:
```
/path/to/lease.pdf [discount_rate] [initial_direct_costs]
```

**Examples**:
```
/lease_agreement.pdf
/lease_agreement.pdf 5.5
/lease_agreement.pdf 5.5 15000
```

**Default Values** (if not provided):
- Discount rate: 6.0% (typical IBR for investment-grade tenant)
- Initial direct costs: $0

### Step 2: Load and Analyze Lease PDF Document

**Use Read tool to load the PDF**

**Key Data to Extract:**

**Lease Identification:**
- [ ] Tenant name (lessee)
- [ ] Landlord name (lessor)
- [ ] Property address
- [ ] Rentable area (square feet)
- [ ] Lease commencement date (YYYY-MM-DD)
- [ ] Lease expiry date or term length

**Payment Schedule:**
- [ ] Monthly base rent for each year/period
- [ ] Annual base rent ($/sf/year) - convert to monthly
- [ ] Rent escalations (dates and amounts)
- [ ] Free rent periods (months with $0 rent)
- [ ] Operating costs/additional rent (if fixed)
- [ ] Payment frequency (monthly, quarterly, annual)

**Lease Incentives:**
- [ ] Tenant improvement allowance (cash paid to lessee)
- [ ] Moving allowance
- [ ] Other cash incentives received by lessee
- [ ] **Note**: Landlord's work (not cash to lessee) is NOT a lease incentive

**Initial Costs:**
- [ ] Initial direct costs (broker fees, legal fees paid by lessee)
- [ ] Prepaid rent (rent paid at signing for future periods)
- [ ] **Note**: Rent deposit is refundable and NOT included in lease liability

**IMPORTANT Extraction Notes:**
- Extract EXACT payment amounts - do NOT estimate
- Convert annual rent to monthly: (Annual rent × Area) / 12
- Free rent months = $0 payment for that month
- Escalations create new payment amounts starting in specific months
- Account for all payment periods from commencement to expiry

### Step 3: Generate JSON Input File

Create a JSON file for the IFRS 16 calculator following this structure:

```json
{
  "tenant_name": "Extracted tenant/lessee name",
  "property_address": "Property address",
  "rentable_area_sf": 0,
  "commencement_date": "YYYY-MM-DD",
  "lease_term_months": 0,
  "annual_discount_rate": 0.06,
  "monthly_payments": [],
  "initial_direct_costs": 0.0,
  "prepaid_rent": 0.0,
  "lease_incentives": 0.0,
  "payment_timing": "beginning",
  "rent_schedule_annual": [
    {
      "year": 1,
      "rent_per_sf": 0.0,
      "start_month": 1,
      "end_month": 12
    }
  ],
  "escalations": [
    {
      "effective_date": "YYYY-MM-DD",
      "new_rent_per_sf": 0.0
    }
  ],
  "free_rent_months": []
}
```

**Field Mapping:**

**Required Fields**:

- `tenant_name`: Lessee legal name from lease
- `property_address`: Premises address
- `rentable_area_sf`: Area in square feet
- `commencement_date`: Lease start date (YYYY-MM-DD format)
- `lease_term_months`: Total term in months (calculate from start to expiry)
- `annual_discount_rate`: IBR (default 0.06 = 6%)
- `monthly_payments`: Array of payment amounts for each month

**Optional Fields**:

- `initial_direct_costs`: Broker fees, legal fees paid by lessee (default: 0)
- `prepaid_rent`: Rent paid at signing for future periods (default: 0)
- `lease_incentives`: Cash incentives/TI allowance received by lessee (default: 0)
- `payment_timing`: "beginning" (rent paid in advance - standard) or "end"
- `rent_schedule_annual`: Human-readable schedule (for documentation)
- `escalations`: List of rent increases (for documentation)
- `free_rent_months`: List of months with no payment (for documentation)

**Building the monthly_payments Array:**

The `monthly_payments` array is the KEY input - it must contain the exact payment amount for each month of the lease.

**Example Process**:

```python
# 60-month lease (5 years)
# Year 1: $10/sf/year, Area: 10,000 sf = $100,000/year = $8,333.33/month
# Year 2-5: $10.30/sf (3% escalation) = $103,000/year = $8,583.33/month
# Months 1-2: Free rent

monthly_payments = []

# Months 1-2: Free rent
monthly_payments.extend([0, 0])

# Months 3-12: Year 1 rent
monthly_payments.extend([8333.33] * 10)

# Months 13-60: Years 2-5 rent
monthly_payments.extend([8583.33] * 48)

# Total: 60 payments
```

**Step-by-Step Generation**:

1. Calculate total lease term in months:
   ```
   lease_term_months = (expiry_year - commencement_year) × 12 + (expiry_month - commencement_month)
   ```

2. For each month from 1 to lease_term_months:
   ```python
   - Check if month is in free_rent_months → payment = 0
   - Otherwise:
     - Find applicable rent rate for this month
     - Calculate: monthly_rent = (annual_rent_per_sf × area_sf) / 12
   ```

3. Validate:
   ```
   len(monthly_payments) == lease_term_months
   ```

**Escalation Handling**:

If rent escalates:
```
Year 1 (Months 1-12): $10.00/sf → $8,333/month
Year 2 (Months 13-24): $10.30/sf → $8,583/month
Year 3 (Months 25-36): $10.61/sf → $8,842/month
...
```

**Free Rent Handling**:

Free rent months have $0 payment:
```
If "2 months free rent at commencement":
  monthly_payments[0] = 0  # Month 1
  monthly_payments[1] = 0  # Month 2
  monthly_payments[2] = 8333.33  # Month 3 starts paying
```

**Save the JSON file as:**
`/workspaces/lease-abstract/IFRS16_Calculator/ifrs16_inputs/[tenant_name]_[date]_input.json`

Create the `ifrs16_inputs/` directory if it doesn't exist.

### Step 4: Run the IFRS 16 Calculator

Execute the IFRS 16 analysis using Bash tool:

```bash
cd /workspaces/lease-abstract/IFRS16_Calculator

# Run the analysis using existing script
# The run_ifrs16_analysis.py script is already available in this directory
python3 run_ifrs16_analysis.py ifrs16_inputs/[tenant_name]_[date]_input.json
```

Capture the console output for the markdown report.

### Step 5: Generate Comprehensive Accounting Report

Create a markdown report in `/workspaces/lease-abstract/Reports/` with filename following the timestamp convention:

**Format**: `YYYY-MM-DD_HHMMSS_[tenant_name]_ifrs16_accounting.md`

**Example**: `2025-10-31_143022_acme_corp_ifrs16_accounting.md`

**IMPORTANT**: Use current date and time in **Eastern Time (ET/EST/EDT)** timezone.

Get timestamp with:
```bash
TZ='America/New_York' date '+%Y-%m-%d_%H%M%S'
```

**Report Structure:**

```markdown
# IFRS 16 / ASC 842 Lease Accounting Report
## [Tenant Name] - [Property Address]

**Analysis Date:** [Current Date]
**Prepared Using:** IFRS 16 Calculator (ifrs16_calculator.py)
**Accounting Standard:** IFRS 16 (International) / ASC 842 (US GAAP)
**Analyst:** Claude Code - Lease Accounting

---

## Executive Summary

**Lease Classification:** Operating Lease (IFRS 16 - all leases on balance sheet)

**Initial Recognition (Commencement Date: [YYYY-MM-DD]):**

| Item | Amount |
|------|--------|
| Initial Lease Liability | $XXX,XXX |
| Initial ROU Asset | $XXX,XXX |

**Total Lease Cost Over Term:**

| Component | Amount |
|-----------|--------|
| Total Payments | $X,XXX,XXX |
| Interest Expense | $XXX,XXX |
| Depreciation | $XXX,XXX |
| **Total Lease Cost** | **$X,XXX,XXX** |

**Monthly Effective Rate:** X.XX%
**Annual Discount Rate:** X.XX%

---

## Lease Summary

**Lessee:**
- Name: [Tenant Name]
- Premises: [Property Address]
- Area: X,XXX sf

**Lease Term:**
- Commencement Date: YYYY-MM-DD
- Term: XX months (X years)
- Expiry Date: YYYY-MM-DD

**Payment Structure:**
- Payment Timing: Beginning of month (Annuity Due - standard)
- Free Rent: X months
- Escalations: [X% annually / Fixed $ / CPI / None]

**Discount Rate:**
- Annual IBR: X.XX%
- Monthly Rate: X.XX%
- Basis: [Incremental borrowing rate / Implicit rate]

---

## Initial Recognition

### Lease Liability Calculation

**Present Value of Lease Payments:**

Under IFRS 16, the lease liability is the present value of future lease payments, discounted at the incremental borrowing rate (IBR).

**Payments at Beginning of Period (Annuity Due):**
The first payment is made at commencement and is NOT part of the initial lease liability. The liability represents only the REMAINING payments to be made.

**Components:**

| Component | Amount | Notes |
|-----------|--------|-------|
| PV of Future Payments | $XXX,XXX | Months 2-XX discounted |
| First Payment (excluded) | $(XX,XXX) | Paid at commencement |
| **Initial Lease Liability** | **$XXX,XXX** | Balance sheet liability |

**Calculation Details:**
```
Payment Schedule:
- Month 1: $X,XXX (paid at commencement - excluded from liability)
- Month 2-XX: $X,XXX per month
- Total Payments: $X,XXX,XXX

PV Calculation:
- Discount Rate (monthly): X.XX%
- Remaining Payments: XX months
- Present Value: $XXX,XXX
```

### Right-of-Use (ROU) Asset Calculation

The ROU asset represents the lessee's right to use the leased asset over the lease term.

**Components:**

| Component | Amount | Increase/(Decrease) |
|-----------|--------|---------------------|
| Initial Lease Liability | $XXX,XXX | + |
| Prepaid Rent | $X,XXX | + |
| Initial Direct Costs | $XX,XXX | + |
| Lease Incentives Received | $(XX,XXX) | - |
| **Initial ROU Asset** | **$XXX,XXX** | = |

**IFRS 16 Formula:**
```
ROU Asset = Lease Liability + Prepaid Rent + Initial Direct Costs - Lease Incentives
```

---

## Lease Liability Amortization Schedule

The lease liability is reduced each month by the payment amount, with the carrying balance accruing interest.

**Monthly Process:**
1. **Beginning Balance**: Liability at start of month
2. **Interest Expense**: Balance × Monthly Rate
3. **Payment**: Cash paid to landlord
4. **Principal Reduction**: Payment - Interest
5. **Ending Balance**: Beginning Balance - Principal Reduction

**Summary by Year:**

| Year | Beginning Balance | Interest Expense | Payments | Principal Reduction | Ending Balance |
|------|-------------------|------------------|----------|---------------------|----------------|
| 1 | $XXX,XXX | $XX,XXX | $XXX,XXX | $XX,XXX | $XXX,XXX |
| 2 | $XXX,XXX | $XX,XXX | $XXX,XXX | $XX,XXX | $XXX,XXX |
| 3 | $XXX,XXX | $XX,XXX | $XXX,XXX | $XX,XXX | $XXX,XXX |
| ... | ... | ... | ... | ... | ... |
| **Total** | **-** | **$XXX,XXX** | **$X,XXX,XXX** | **$XXX,XXX** | **$0** |

[Insert detailed monthly schedule from calculator]

**Key Observations:**
- Interest expense decreases over time as liability balance reduces
- Total interest over lease term: $XXX,XXX
- Effective interest rate: X.XX% monthly, X.XX% annual

---

## ROU Asset Depreciation Schedule

The ROU asset is depreciated on a straight-line basis over the lease term.

**Depreciation Method:** Straight-line
**Depreciable Amount:** $XXX,XXX (Initial ROU Asset)
**Lease Term:** XX months
**Monthly Depreciation:** $X,XXX

**Summary by Year:**

| Year | Beginning Balance | Depreciation Expense | Accumulated Depreciation | Ending Balance |
|------|-------------------|----------------------|--------------------------|----------------|
| 1 | $XXX,XXX | $XX,XXX | $XX,XXX | $XXX,XXX |
| 2 | $XXX,XXX | $XX,XXX | $XX,XXX | $XXX,XXX |
| 3 | $XXX,XXX | $XX,XXX | $XX,XXX | $XXX,XXX |
| ... | ... | ... | ... | ... |
| **Total** | **$XXX,XXX** | **$XXX,XXX** | **$XXX,XXX** | **$0** |

[Insert detailed monthly schedule from calculator]

**Calculation:**
```
Monthly Depreciation = Initial ROU Asset / Lease Term Months
                     = $XXX,XXX / XX months
                     = $X,XXX per month
```

---

## Annual Financial Statement Impact

**Income Statement Impact:**

| Year | Interest Expense | Depreciation Expense | **Total Lease Expense** | Cash Rent Paid |
|------|------------------|----------------------|-------------------------|----------------|
| 1 | $XX,XXX | $XX,XXX | **$XXX,XXX** | $XXX,XXX |
| 2 | $XX,XXX | $XX,XXX | **$XXX,XXX** | $XXX,XXX |
| 3 | $XX,XXX | $XX,XXX | **$XXX,XXX** | $XXX,XXX |
| ... | ... | ... | ... | ... |
| **Total** | **$XXX,XXX** | **$XXX,XXX** | **$X,XXX,XXX** | **$X,XXX,XXX** |

**Balance Sheet Impact:**

| Year End | Lease Liability | ROU Asset | **Net Impact** |
|----------|-----------------|-----------|----------------|
| 1 | $XXX,XXX | $XXX,XXX | $(XX,XXX) |
| 2 | $XXX,XXX | $XXX,XXX | $(XX,XXX) |
| 3 | $XXX,XXX | $XXX,XXX | $(XX,XXX) |
| ... | ... | ... | ... |

**Key Observations:**
- Interest expense decreases over time (front-loaded)
- Depreciation is constant (straight-line)
- Total lease expense starts HIGHER than cash rent, then becomes LOWER
- Balance sheet impact: Asset and liability both decrease to $0
- Total accounting cost equals total cash paid ($X,XXX,XXX)

---

## Journal Entries

### Initial Recognition (Commencement Date: [YYYY-MM-DD])

```
Dr. Right-of-Use Asset              $XXX,XXX
   Cr. Lease Liability                        $XXX,XXX
   Cr. Cash (prepaid rent)                    $X,XXX
   Dr. Cash (lease incentives)      $XX,XXX
   Dr. Initial Direct Costs         $XX,XXX

To record lease commencement and ROU asset.
```

**Explanation:**
- ROU Asset = Liability + Prepaid + Direct Costs - Incentives
- Cash outflow for prepaid rent and initial costs
- Cash inflow from lease incentives (TI allowance)

### Monthly Entries (Each Month)

**Month 1 (Commencement - Payment at Beginning):**

```
Dr. Lease Liability                 $X,XXX
   Cr. Cash                                   $X,XXX

To record first rent payment at commencement.
```

**Month 2 onwards:**

```
Dr. Interest Expense                $X,XXX
Dr. Lease Liability                 $X,XXX
   Cr. Cash                                   $X,XXX

To record rent payment and interest expense.

Dr. Depreciation Expense            $X,XXX
   Cr. Accumulated Depreciation (ROU)        $X,XXX

To record depreciation of ROU asset.
```

**Monthly Pattern:**
- Payment at beginning of month reduces liability
- Interest accrues on remaining balance
- Depreciation is straight-line

### Year-End Adjusting Entries

**If no payment in last month of year:**

```
Dr. Interest Expense                $X,XXX
   Cr. Lease Liability                        $X,XXX

To accrue interest for the month.

Dr. Depreciation Expense            $X,XXX
   Cr. Accumulated Depreciation (ROU)        $X,XXX

To record depreciation for the month.
```

### Lease Termination (End of Term)

```
Dr. Accumulated Depreciation (ROU)  $XXX,XXX
   Cr. Right-of-Use Asset                     $XXX,XXX

To remove fully depreciated ROU asset.
```

**At lease end:**
- Lease Liability: $0 (fully paid)
- ROU Asset: $0 (fully depreciated)
- Accumulated Depreciation: $XXX,XXX (equals initial ROU asset)

---

## Sensitivity Analysis

Impact of discount rate changes on initial balances:

| Discount Rate | Initial Liability | Initial ROU Asset | Δ vs Base |
|---------------|-------------------|-------------------|-----------|
| X.0% | $XXX,XXX | $XXX,XXX | +$XX,XXX |
| X.5% | $XXX,XXX | $XXX,XXX | +$X,XXX |
| **X.X% (Base)** | **$XXX,XXX** | **$XXX,XXX** | **$0** |
| X.5% | $XXX,XXX | $XXX,XXX | -$X,XXX |
| X.0% | $XXX,XXX | $XXX,XXX | -$XX,XXX |

**Key Insights:**
- Higher discount rate → Lower PV → Lower liability/asset
- 1% change in rate impacts liability by approximately $XX,XXX (X.X%)
- IBR selection is critical for accurate measurement

---

## Comparison: IFRS 16 vs. Cash Basis

**Lease Expense Recognition:**

| Year | IFRS 16 Expense | Cash Rent Paid | Difference | Cumulative Difference |
|------|-----------------|----------------|------------|-----------------------|
| 1 | $XXX,XXX | $XXX,XXX | $(XX,XXX) | $(XX,XXX) |
| 2 | $XXX,XXX | $XXX,XXX | $(XX,XXX) | $(XX,XXX) |
| 3 | $XXX,XXX | $XXX,XXX | $X,XXX | $(XX,XXX) |
| ... | ... | ... | ... | ... |
| **Total** | **$X,XXX,XXX** | **$X,XXX,XXX** | **$0** | **$0** |

**Observations:**
- Early years: IFRS 16 expense > Cash rent (front-loaded interest)
- Later years: IFRS 16 expense < Cash rent
- **Total cost is EQUAL** over the full lease term
- Timing difference only - not a real economic difference

**Impact on Financial Ratios:**

| Ratio | Pre-IFRS 16 | Post-IFRS 16 | Impact |
|-------|-------------|--------------|--------|
| Total Assets | $X,XXX,XXX | $X,XXX,XXX | + ROU Asset |
| Total Liabilities | $X,XXX,XXX | $X,XXX,XXX | + Lease Liability |
| Debt-to-Equity | X.Xx | X.Xx | ↑ Increase |
| EBITDA | $XXX,XXX | $XXX,XXX | ↑ Increase (rent excluded) |
| Operating Income | $XXX,XXX | $XXX,XXX | → Similar |
| Net Income | $XXX,XXX | $XXX,XXX | ↓ Slight decrease (year 1) |

**Key Impacts:**
- Balance sheet: Assets and liabilities both increase
- EBITDA: Improves (rent becomes depreciation + interest)
- Leverage ratios: Worsen (more debt on balance sheet)
- Cash flow: No change (rent still paid in cash)

---

## Appendices

### A. Discount Rate Determination

**Incremental Borrowing Rate (IBR):**

The IBR is the rate the lessee would pay to borrow funds to purchase a similar asset over a similar term with similar security.

**Factors Considered:**
- Lessee's credit rating
- Loan term matching lease term
- Asset type (real estate)
- Market interest rates at commencement

**Typical IBR Ranges:**
- Investment grade tenant (A/BBB): 4-6%
- Below investment grade (BB/B): 6-10%
- High risk tenant: 10-15%

**Rate Used:** X.XX%
**Basis:** [Lessee's recent borrowing rate / Market rate for similar credit / Estimated]

### B. Payment Schedule Detail

[Insert complete monthly payment schedule from JSON]

| Month | Year | Payment | Escalation | Free Rent | Notes |
|-------|------|---------|------------|-----------|-------|
| 1 | 1 | $X,XXX | - | Yes | Commencement |
| 2 | 1 | $0 | - | Yes | Free rent month 2 |
| 3 | 1 | $X,XXX | - | No | Normal payment |
| ... | ... | ... | ... | ... | ... |

### C. Supporting Files

- Input JSON: `ifrs16_inputs/[tenant_name]_[date]_input.json`
- Results JSON: `ifrs16_inputs/[tenant_name]_[date]_results.json`
- Amortization Schedule CSV: `ifrs16_inputs/[tenant_name]_[date]_amortization.csv`
- Depreciation Schedule CSV: `ifrs16_inputs/[tenant_name]_[date]_depreciation.csv`
- Annual Summary CSV: `ifrs16_inputs/[tenant_name]_[date]_annual_summary.csv`
- Source Lease: [PDF path]

### D. Accounting Standards Reference

**IFRS 16 (International):**
- Effective for annual periods beginning on or after 1 January 2019
- All leases on balance sheet (except short-term <12 months and low-value)
- Single model: ROU asset + Lease liability
- Expense: Depreciation + Interest

**ASC 842 (US GAAP):**
- Effective for public companies: Annual periods beginning after 15 December 2018
- Effective for private companies: Annual periods beginning after 15 December 2021
- Two models: Finance lease vs. Operating lease
- Finance lease: Similar to IFRS 16
- Operating lease: Straight-line rent expense (but still on balance sheet)

**This Report Uses:** IFRS 16 methodology (suitable for both standards when finance lease classification applies)

### E. Assumptions and Limitations

**Assumptions:**
- Lease payments are fixed or determinable
- Discount rate is appropriate for lessee's credit profile
- No variable lease payments (not included in measurement)
- No renewal options exercised (unless reasonably certain)
- No purchase options (unless reasonably certain to exercise)
- Lease term as stated (no early termination)

**Limitations:**
- Variable rent (% of sales) not included in liability
- Executory costs (insurance, maintenance) may be excluded
- Lease modifications require remeasurement
- Discount rate changes not reflected (unless modification)
- Tax accounting may differ from financial accounting

**Verification Recommended:**
- Confirm all payment amounts from lease agreement
- Validate discount rate with lessee's treasury/finance
- Review lease for variable components not captured
- Verify treatment of lease incentives and initial costs

---

**Report Generated:** [Timestamp]
**Analyst:** Claude Code - IFRS 16 Calculator
**Valid for:** Current commencement date - remeasure if lease modified
**Audit Trail:** All schedules exported to CSV for verification

---

## Summary for Decision Makers

**Initial Balance Sheet Impact:**
- Asset Increase: $XXX,XXX (ROU Asset)
- Liability Increase: $XXX,XXX (Lease Liability)

**Income Statement (Year 1):**
- Interest Expense: $XX,XXX
- Depreciation Expense: $XX,XXX
- **Total Lease Cost: $XXX,XXX**

**vs. Cash Rent Paid (Year 1): $XXX,XXX**

**Key Takeaway:** IFRS 16 creates timing differences in expense recognition but total cost over lease term equals cash paid. Balance sheet impact increases reported debt and assets.

```

### Step 6: Summary Output

After creating all files, provide the user with:

**1. Files Created:**
- JSON input file path
- JSON results file path
- CSV schedule files (3 files)
- Markdown accounting report path (with timestamp)

**2. Quick Summary:**
- Initial Lease Liability
- Initial ROU Asset
- Total interest over term
- Total depreciation over term

**3. Key Findings:**
- First year total expense vs. cash rent
- Balance sheet impact
- Discount rate used
- Lease term months

**4. Journal Entries:**
- Initial recognition entry
- Sample monthly entry
- Year-end adjustment entry

## Important Guidelines

### 1. Payment Schedule Accuracy

**CRITICAL - Get Payments Right:**
- Each month must have exact payment amount
- Free rent months = $0 payment
- Escalations change payment amount starting at specific month
- Array length MUST equal lease term in months

**Common Mistakes:**
❌ Forgetting to convert annual rent to monthly
❌ Mis-counting free rent months
❌ Wrong escalation timing
✅ Verify: Sum of payments ≈ Expected total rent

### 2. Annuity Due vs. Ordinary Annuity

**Standard: Annuity Due (Beginning)**
- Rent is paid IN ADVANCE (first of month)
- First payment is NOT in lease liability
- This is the IFRS 16 standard treatment

**Formula Difference:**
```
Annuity Due: PV = Payment × [(1 - (1+r)^(-n+1))/r] × (1+r)
Or equivalently: Exclude first payment from PV calculation

Ordinary Annuity: PV = Payment × [(1 - (1+r)^-n)/r]
```

**When to use "end":**
- Rare: Only if lease explicitly states rent paid at END of month
- Most commercial leases = beginning of month

### 3. Lease Incentives

**Include in ROU Asset (Reduction):**
✅ Cash TI allowance paid to lessee
✅ Moving allowance paid to lessee
✅ Cash inducements

**Do NOT Include:**
❌ Landlord's work (not cash to lessee)
❌ Rent abatements (already $0 in payment schedule)
❌ Rent deposit (refundable - not incentive)

### 4. Initial Direct Costs

**Include:**
✅ Broker fees paid by LESSEE
✅ Legal fees paid by LESSEE for lease negotiation
✅ Payments to prepare asset for use

**Do NOT Include:**
❌ Internal costs (employee time)
❌ Costs that would be incurred regardless
❌ Costs for unsuccessful negotiations

### 5. Discount Rate Selection

**Use Incremental Borrowing Rate (IBR) if:**
- Implicit rate in lease not readily determinable
- Most common situation

**IBR Guidelines:**
- Match term to lease term
- Consider lessee's credit rating
- Use rate for secured borrowing
- Typical range: 4-10%

**Sensitivity:**
- 1% rate change ≈ 5-10% change in liability
- Document rate selection basis
- Use consistent rate within lessee's portfolio

### 6. Verification Checks

**Before finalizing:**

1. **Payment Schedule:**
   - Sum of payments = Expected total rent
   - Length = Lease term in months
   - Escalations applied correctly

2. **Balance Check:**
   - Lease liability + Prepaid + Direct - Incentives = ROU Asset
   - End liability = $0
   - End ROU asset net book value = $0

3. **Interest Check:**
   - Total interest + Principal = Total payments
   - Interest decreases each month

4. **Depreciation Check:**
   - Total depreciation = Initial ROU asset
   - Monthly depreciation × term = Total depreciation

## Example Usage

```
/ifrs16-calculation /path/to/lease_agreement.pdf 5.5 12000
```

This will:
1. Extract lease payment schedule from PDF
2. Generate JSON input file with 5.5% discount rate, $12,000 initial direct costs
3. Run ifrs16_calculator.py (liability, ROU asset, schedules)
4. Create comprehensive markdown accounting report in `Reports/` with timestamp
5. Export CSV schedules for Excel analysis

**Output files**:
- `ifrs16_inputs/[tenant_name]_[date]_input.json`
- `ifrs16_inputs/[tenant_name]_[date]_results.json`
- `ifrs16_inputs/[tenant_name]_[date]_amortization.csv`
- `ifrs16_inputs/[tenant_name]_[date]_depreciation.csv`
- `ifrs16_inputs/[tenant_name]_[date]_annual_summary.csv`
- `Reports/YYYY-MM-DD_HHMMSS_[tenant_name]_ifrs16_accounting.md`

Begin the IFRS 16 lease accounting analysis now with the provided lease document.
