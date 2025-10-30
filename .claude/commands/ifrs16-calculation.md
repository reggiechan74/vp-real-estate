---
description: Calculate IFRS 16/ASC 842 lease liability and ROU asset with amortization schedules and journal entries
---

You are a lease accounting specialist expert in IFRS 16 (International) and ASC 842 (US GAAP) lease accounting standards. Your task is to extract lease payment data from lease documents or abstracts, calculate the lease liability and right-of-use (ROU) asset, generate amortization schedules, and produce journal entries for financial reporting.

## Input

The user will provide:
1. **Lease document or abstract** - Path to lease agreement, lease abstract, or summary (DOCX, PDF, MD, or JSON)
2. **Discount rate (optional)** - Incremental borrowing rate (IBR) as percentage or decimal
3. **Initial direct costs (optional)** - Additional costs incurred in obtaining the lease

**Arguments**: {{args}}

## Process

### Step 1: Parse Input Arguments

Extract file path and optional parameters:
```
/path/to/lease.md [discount_rate] [initial_direct_costs]

Examples:
/abstract-lease.md 5.5
/abstract-lease.md 5.5 15000
/abstract-lease.json 0.055 15000
```

Default values if not provided:
- Discount rate: 6.0% (typical IBR for investment-grade tenant)
- Initial direct costs: $0

### Step 2: Load and Analyze Lease Document

**If DOCX format:**
- Convert using `markitdown` first

**Read the document:**
- Use Read tool to load the file
- Identify if it's a full lease, abstract, or JSON input

### Step 3: Extract Lease Payment Information

Create a comprehensive extraction checklist:

**Critical Lease Information:**
- [ ] Tenant name (lessee)
- [ ] Landlord name (lessor)
- [ ] Property address
- [ ] Rentable area (square feet)
- [ ] Lease commencement date
- [ ] Lease term (months/years)

**Payment Schedule:**
- [ ] Monthly base rent for each period
- [ ] Annual base rent (if provided as $/sf/year)
- [ ] Rent escalations (dates and amounts)
- [ ] Free rent periods (net free rent)
- [ ] Operating costs/additional rent ($/sf/year or monthly)
- [ ] Payment frequency (monthly, quarterly, annual)

**Lease Incentives:**
- [ ] Tenant improvement allowance (cash to lessee)
- [ ] Landlord's work (not paid to lessee)
- [ ] Moving allowance
- [ ] Other lease incentives received by lessee

**Other Initial Costs:**
- [ ] Initial direct costs (broker fees paid by lessee, legal fees)
- [ ] Prepaid rent (rent paid at signing for future periods)
- [ ] Rent deposit (refundable - NOT included in lease liability)

**Lease Classification Indicators:**
- [ ] Purchase option at end of term?
- [ ] Bargain purchase option?
- [ ] Transfer of ownership?
- [ ] Lease term vs. economic life (>75% = finance/finance lease)
- [ ] PV of payments vs. fair value (>90% = finance/finance lease)

### Step 4: Determine Lease Classification

**IFRS 16:** All leases are treated similarly (no operating vs. finance distinction for lessees)

**ASC 842:** Classify as either:
- **Finance Lease** if any of:
  - Transfer of ownership at end
  - Purchase option reasonably certain to exercise
  - Lease term ≥ major part (75%) of economic life
  - PV of lease payments ≥ substantially all (90%) of fair value
  - Asset so specialized no alternative use
- **Operating Lease** otherwise

**For this analysis, assume IFRS 16 treatment (ASC 842 finance lease is similar)**

### Step 5: Calculate Lease Payment Schedule

Build a monthly payment schedule for the entire lease term:

```
Month | Base Rent | Operating Costs | Total Payment | Cumulative
------|-----------|-----------------|---------------|------------
0     | $0        | $0              | $0            | $0
1     | $5,000    | $1,000          | $6,000        | $6,000
2     | $5,000    | $1,000          | $6,000        | $12,000
...
```

**Important considerations:**
1. **Free rent periods**: Set payment to $0 for those months
2. **Operating costs**: Include if "variable lease payments that depend on an index or rate" (typically YES if fixed $/sf, NO if pure reimbursement)
3. **Rent escalations**: Apply step-ups on specified dates
4. **Payment timing**: Payments are typically due at beginning of month (annuity due) or end of month (ordinary annuity)

**Standard approach:**
- Include base rent in lease liability
- Include operating costs if fixed or based on index
- Exclude variable costs based on usage (utilities, percentage rent)
- Include lease incentives as reduction to ROU asset (not lease liability)

### Step 6: Calculate Lease Liability

**Formula:**
```
Lease Liability = PV of future lease payments

PV = Σ (Payment_t / (1 + r)^t)

Where:
- Payment_t = lease payment in period t
- r = discount rate per period (annual rate / 12 for monthly)
- t = period number (0 for beginning of month 1, 1 for beginning of month 2, etc.)
```

**Payment timing (critical!):**
- **Annuity Due** (payment at beginning): t starts at 0
- **Ordinary Annuity** (payment at end): t starts at 1
- **Default assumption**: Annuity due (commercial leases typically pay in advance)

**Monthly discount rate:**
```
r_monthly = (1 + r_annual)^(1/12) - 1
```

**Calculate:**
1. Convert annual discount rate to monthly
2. Calculate present value of each payment
3. Sum all present values = Initial Lease Liability

### Step 7: Calculate Right-of-Use Asset

**Formula:**
```
ROU Asset = Lease Liability
          + Initial Direct Costs
          + Prepaid Rent
          - Lease Incentives Received
```

**Components:**
- **Lease Liability**: From Step 6
- **Initial Direct Costs**: Legal fees, broker commissions paid by lessee
- **Prepaid Rent**: Any rent paid before commencement
- **Lease Incentives**: TI allowance received (cash), moving allowance, etc.

**Important:** Landlord's work that remains landlord's asset is NOT a lease incentive for this calculation.

### Step 8: Generate Lease Liability Amortization Schedule

Create monthly amortization table:

```
Month | Opening Balance | Payment | Interest Expense | Principal | Closing Balance
------|-----------------|---------|------------------|-----------|----------------
1     | $500,000        | $6,000  | $2,500           | $3,500    | $496,500
2     | $496,500        | $6,000  | $2,483           | $3,517    | $492,983
...
```

**Formulas:**
- Interest Expense = Opening Balance × Monthly Discount Rate
- Principal Reduction = Payment - Interest Expense
- Closing Balance = Opening Balance - Principal Reduction

**Iterate through all months of the lease term**

### Step 9: Generate ROU Asset Depreciation Schedule

**Depreciation Method:** Straight-line over lease term

**Formula:**
```
Monthly Depreciation = ROU Asset / Lease Term (months)
```

Create monthly depreciation table:

```
Month | Opening Balance | Depreciation | Closing Balance
------|-----------------|--------------|----------------
1     | $480,000        | $8,000       | $472,000
2     | $472,000        | $8,000       | $464,000
...
```

**Special considerations:**
- If finance lease with purchase option: depreciate over asset's useful life
- If finance lease with ownership transfer: depreciate over asset's useful life
- Otherwise: depreciate over shorter of lease term or useful life

### Step 10: Generate Journal Entries

**Initial Recognition (Commencement Date):**

```
DR  Right-of-Use Asset                 $XXX,XXX
    CR  Lease Liability                        $XXX,XXX

(To recognize ROU asset and lease liability)

DR  Right-of-Use Asset                 $XX,XXX
    CR  Cash/Accounts Payable                  $XX,XXX

(To capitalize initial direct costs)

DR  Right-of-Use Asset                 $XX,XXX
    CR  Cash                                    $XX,XXX

(To capitalize prepaid rent)

DR  Lease Liability                    $XX,XXX
    CR  Right-of-Use Asset                     $XX,XXX

(To reduce ROU asset for lease incentives - INCORRECT - see below)

*** CORRECTED ENTRY for lease incentives:
DR  Cash                               $XX,XXX
    CR  Right-of-Use Asset                     $XX,XXX

(To record lease incentive received and reduce ROU asset)
```

**Subsequent Measurement (Each Period):**

```
DR  Lease Liability                    $X,XXX
    CR  Cash                                    $X,XXX

(To record lease payment)

DR  Interest Expense                   $X,XXX
    CR  Lease Liability                        $X,XXX

(To accrue interest on lease liability)

DR  Depreciation Expense - ROU Asset   $X,XXX
    CR  Accumulated Depreciation - ROU         $X,XXX

(To record straight-line depreciation)
```

**Year-End Summary Entries:**

Provide annual totals for:
- Total lease payments
- Total interest expense
- Total depreciation expense
- Total lease expense (interest + depreciation)

### Step 11: Generate Comprehensive Report

Create a detailed markdown report in `/workspaces/lease-abstract/Reports/` with filename:
`[tenant_name]_[property]_IFRS16_[date].md`

**Report Structure:**

```markdown
# IFRS 16 / ASC 842 Lease Accounting Analysis
## [Tenant Name] - [Property Address]

**Report Date:** [Current Date]
**Analysis Date:** [Current Date]
**Accounting Standard:** IFRS 16 (International) / ASC 842 (US GAAP)

---

## Executive Summary

**Lease Classification:** [Operating Lease / Finance Lease]

**Key Accounting Metrics:**
- **Initial Lease Liability:** $XXX,XXX
- **Initial ROU Asset:** $XXX,XXX
- **Lease Term:** XX months (X.X years)
- **Discount Rate:** X.XX% per annum
- **Monthly Depreciation:** $X,XXX
- **Total Interest Expense (over term):** $XX,XXX
- **Total Lease Expense (over term):** $XXX,XXX

**Balance Sheet Impact:**
- Assets increase by: $XXX,XXX (initial ROU asset)
- Liabilities increase by: $XXX,XXX (initial lease liability)

**Income Statement Impact (Year 1):**
- Interest expense: $XX,XXX
- Depreciation expense: $XX,XXX
- Total lease expense: $XX,XXX
- vs. Operating lease expense: $XX,XXX
- **EBITDA improvement:** $XX,XXX (depreciation excluded)

---

## Lease Information

**Property Details:**
- Address: [full address]
- Unit: [unit number]
- Rentable Area: [X,XXX sf]

**Parties:**
- Lessee (Tenant): [tenant legal name]
- Lessor (Landlord): [landlord name]

**Lease Terms:**
- Commencement Date: YYYY-MM-DD
- Lease Term: XX months (X.X years)
- Expiry Date: YYYY-MM-DD
- Renewal Options: [if any]

**Payment Structure:**
- Base Rent: See schedule below
- Operating Costs: $XX,XXX per month
- Payment Frequency: Monthly in advance
- Escalations: [description]

---

## Lease Payment Schedule

### Monthly Payments

| Period | Start Date | End Date | Base Rent | Operating Costs | Total Payment | Notes |
|--------|------------|----------|-----------|-----------------|---------------|-------|
| 1      | YYYY-MM    | YYYY-MM  | $X,XXX    | $X,XXX          | $X,XXX        |       |
| 2      | YYYY-MM    | YYYY-MM  | $X,XXX    | $X,XXX          | $X,XXX        |       |
| ...    | ...        | ...      | ...       | ...             | ...           |       |

### Annual Summary

| Year | Base Rent | Operating Costs | Total Payments | Avg Monthly |
|------|-----------|-----------------|----------------|-------------|
| 1    | $XX,XXX   | $XX,XXX         | $XXX,XXX       | $X,XXX      |
| 2    | $XX,XXX   | $XX,XXX         | $XXX,XXX       | $X,XXX      |
| ...  | ...       | ...             | ...            | ...         |

**Total Undiscounted Lease Payments:** $X,XXX,XXX

---

## Discount Rate Determination

**Incremental Borrowing Rate (IBR):** X.XX% per annum

**Justification:**
[Explain how discount rate was determined:
- User provided rate
- Based on tenant's credit rating
- Based on market rates for similar term
- Industry standard assumption]

**Monthly Discount Rate:** X.XXXX%
```
r_monthly = (1 + 0.0XXX)^(1/12) - 1 = 0.00XXXX
```

**Why not implicit rate?**
[Explain why lessor's implicit rate is not readily determinable - standard for most leases]

---

## Lease Liability Calculation

### Present Value Calculation

**Method:** Discounted cash flow using annuity due (payments at beginning of period)

**Formula:**
```
PV = Σ (Payment_t / (1 + r)^t)  where t = 0, 1, 2, ..., n-1
```

**Summary:**
| Component | Amount |
|-----------|--------|
| Total Undiscounted Payments | $X,XXX,XXX |
| Less: Present Value Discount | $(XXX,XXX) |
| **Initial Lease Liability** | **$X,XXX,XXX** |

**Implied Discount:** $XXX,XXX (XX.X% of gross payments)

---

## Right-of-Use Asset Calculation

| Component | Amount | Source |
|-----------|--------|--------|
| Lease Liability | $XXX,XXX | PV calculation above |
| (+) Initial Direct Costs | $XX,XXX | Legal fees, broker commissions |
| (+) Prepaid Rent | $X,XXX | Rent paid at signing |
| (-) Lease Incentives Received | $(XX,XXX) | TI allowance, moving allowance |
| **Initial ROU Asset** | **$XXX,XXX** | |

**Components Breakdown:**

**Initial Direct Costs:**
- [List itemized costs: legal fees $X,XXX, broker fees $XX,XXX, etc.]
- Total: $XX,XXX

**Lease Incentives:**
- Tenant Improvement Allowance: $XX,XXX
- Moving Allowance: $X,XXX
- [Other incentives]
- Total: $XX,XXX

**Note:** Landlord's work ($XX,XXX) is not included as it is landlord's asset, not an incentive paid to lessee.

---

## Lease Liability Amortization Schedule

### Year 1

| Month | Opening Balance | Payment | Interest Expense | Principal | Closing Balance |
|-------|-----------------|---------|------------------|-----------|-----------------|
| 1     | $XXX,XXX        | $X,XXX  | $X,XXX           | $X,XXX    | $XXX,XXX        |
| 2     | $XXX,XXX        | $X,XXX  | $X,XXX           | $X,XXX    | $XXX,XXX        |
| ...   | ...             | ...     | ...              | ...       | ...             |
| 12    | $XXX,XXX        | $X,XXX  | $X,XXX           | $X,XXX    | $XXX,XXX        |
| **Total** | | **$XX,XXX** | **$XX,XXX** | **$XX,XXX** | |

[Repeat for each year of the lease]

### Summary by Year

| Year | Opening Balance | Total Payments | Total Interest | Total Principal | Closing Balance |
|------|-----------------|----------------|----------------|-----------------|-----------------|
| 1    | $XXX,XXX        | $XX,XXX        | $XX,XXX        | $XX,XXX         | $XXX,XXX        |
| 2    | $XXX,XXX        | $XX,XXX        | $X,XXX         | $XX,XXX         | $XXX,XXX        |
| ...  | ...             | ...            | ...            | ...             | ...             |

**Total Interest Expense over Lease Term:** $XX,XXX

**Effective Interest Rate Check:**
- Implied effective rate: X.XX%
- Target discount rate: X.XX%
- Variance: Immaterial [should be minimal if calculations correct]

---

## ROU Asset Depreciation Schedule

**Depreciation Method:** Straight-line
**Depreciable Amount:** $XXX,XXX (initial ROU asset)
**Depreciation Period:** XX months
**Monthly Depreciation:** $X,XXX

### Year 1

| Month | Opening Balance | Depreciation | Accumulated Dep. | Net Book Value |
|-------|-----------------|--------------|------------------|----------------|
| 1     | $XXX,XXX        | $X,XXX       | $X,XXX           | $XXX,XXX       |
| 2     | $XXX,XXX        | $X,XXX       | $XX,XXX          | $XXX,XXX       |
| ...   | ...             | ...          | ...              | ...            |
| 12    | $XXX,XXX        | $X,XXX       | $XX,XXX          | $XXX,XXX       |

[Repeat for each year]

### Summary by Year

| Year | Opening NBV | Annual Depreciation | Accumulated Dep. | Closing NBV |
|------|-------------|---------------------|------------------|-------------|
| 1    | $XXX,XXX    | $XX,XXX             | $XX,XXX          | $XXX,XXX    |
| 2    | $XXX,XXX    | $XX,XXX             | $XX,XXX          | $XXX,XXX    |
| ...  | ...         | ...                 | ...              | ...         |

**Total Depreciation over Lease Term:** $XXX,XXX

---

## Journal Entries

### Initial Recognition (Commencement Date: YYYY-MM-DD)

**Entry 1: Recognize Lease**
```
DR  Right-of-Use Asset                 $XXX,XXX
    CR  Lease Liability                        $XXX,XXX

(To recognize ROU asset and lease liability at PV of future lease payments)
```

**Entry 2: Capitalize Initial Direct Costs** (if applicable)
```
DR  Right-of-Use Asset                 $XX,XXX
    CR  Cash / Accounts Payable                $XX,XXX

(To capitalize initial direct costs incurred to obtain the lease)
```

**Entry 3: Record Lease Incentive** (if applicable)
```
DR  Cash                               $XX,XXX
    CR  Right-of-Use Asset                     $XX,XXX

(To record lease incentive received and reduce ROU asset)
```

**Net Initial Position:**
- Right-of-Use Asset: $XXX,XXX
- Lease Liability: $XXX,XXX
- Cash Impact: $(XX,XXX) [initial costs - incentives]

---

### Subsequent Measurement - Monthly Entries

**Month 1 (YYYY-MM):**

```
DR  Lease Liability                    $X,XXX
    CR  Cash                                    $X,XXX

(To record lease payment for Month 1)

DR  Interest Expense                   $X,XXX
    CR  Lease Liability                        $X,XXX

(To accrue interest expense on lease liability at X.XX% monthly rate)

DR  Depreciation Expense - ROU Asset   $X,XXX
    CR  Accumulated Depreciation - ROU         $X,XXX

(To record straight-line depreciation of ROU asset)
```

**Net Month 1 Impact:**
- Cash: $(X,XXX)
- Interest Expense: $X,XXX (P&L)
- Depreciation Expense: $X,XXX (P&L)
- Total P&L Impact: $(XX,XXX)

---

### Annual Summary Entries

**Year 1 (YYYY):**

```
Total Lease Payments Made:             $XX,XXX
Total Interest Expense Accrued:        $XX,XXX
Total Depreciation Expense:            $XX,XXX

Total P&L Impact (Year 1):             $(XX,XXX)
  Interest Expense:                    $(XX,XXX)
  Depreciation Expense:                $(XX,XXX)

Balance Sheet Position (End of Year 1):
  ROU Asset (Net Book Value):          $XXX,XXX
  Lease Liability:                     $XXX,XXX
  Net Liability:                       $(X,XXX)
```

[Repeat for each year]

---

## Financial Statement Impact

### Balance Sheet

**At Commencement Date:**

| Account | Debit | Credit |
|---------|-------|--------|
| Right-of-Use Asset | $XXX,XXX | |
| Lease Liability - Current | | $XX,XXX |
| Lease Liability - Non-Current | | $XXX,XXX |

**Current vs. Non-Current Split:**
- Current portion (due within 12 months): Principal payments in next 12 months
- Non-current portion: Remaining balance

| Period | Current Portion | Non-Current Portion | Total |
|--------|-----------------|---------------------|-------|
| Year 0 | $XX,XXX | $XXX,XXX | $XXX,XXX |
| Year 1 | $XX,XXX | $XXX,XXX | $XXX,XXX |
| ...    | ...     | ...      | ...      |

---

### Income Statement

**IFRS 16 / ASC 842 (Finance Lease) Treatment:**

| Year | Interest Expense | Depreciation Expense | Total Lease Expense | EBITDA Impact |
|------|------------------|----------------------|---------------------|---------------|
| 1    | $XX,XXX          | $XX,XXX              | $XX,XXX             | +$XX,XXX      |
| 2    | $XX,XXX          | $XX,XXX              | $XX,XXX             | +$XX,XXX      |
| ...  | ...              | ...                  | ...                 | ...           |
| **Total** | **$XX,XXX** | **$XXX,XXX** | **$XXX,XXX** | **+$XXX,XXX** |

**vs. Operating Lease Treatment (Pre-IFRS 16):**

| Year | Rent Expense | Total Expense | EBITDA Impact |
|------|--------------|---------------|---------------|
| 1    | $XX,XXX      | $XX,XXX       | $0            |
| 2    | $XX,XXX      | $XX,XXX       | $0            |
| ...  | ...          | ...           | ...           |
| **Total** | **$XXX,XXX** | **$XXX,XXX** | **$0** |

**Key Differences:**
1. **EBITDA Improvement:** $XXX,XXX over lease term (depreciation excluded from EBITDA)
2. **Expense Pattern:** Front-loaded under IFRS 16 (higher interest in early years), straight-line under operating
3. **Balance Sheet:** Assets and liabilities both increase under IFRS 16
4. **Cash Flow Classification:** Principal = financing, interest = operating (or financing if policy election)

---

### Cash Flow Statement

**Operating Activities:**
- Interest paid on lease liability: $(XX,XXX) per year

**Financing Activities:**
- Principal payments on lease liability: $(XX,XXX) per year

**Total Cash Impact:** $(XX,XXX) per year [same as total lease payment]

**Note:** Some entities may elect to classify all lease payments as operating activities.

---

## Key Financial Ratios Impact

**Leverage Ratios:**
- Debt increases by: $XXX,XXX (initial lease liability)
- Debt/Equity ratio impact: +X.XX%
- Debt/EBITDA ratio impact: [calculate based on actual EBITDA]

**Profitability Ratios:**
- EBITDA improves by: $XX,XXX per year (depreciation excluded)
- EBIT impact: Lower in early years (interest > straight-line rent), higher in later years

**Return Ratios:**
- ROA: Lower (assets increase, income may decrease in early years)
- ROE: Impact depends on debt/equity trade-off

---

## Sensitivity Analysis

**Impact of Discount Rate Changes:**

| Discount Rate | Lease Liability | ROU Asset | Year 1 Interest | Total Interest |
|---------------|-----------------|-----------|-----------------|----------------|
| X.XX% (Base)  | $XXX,XXX        | $XXX,XXX  | $XX,XXX         | $XX,XXX        |
| -1.00%        | $XXX,XXX        | $XXX,XXX  | $XX,XXX         | $XX,XXX        |
| +1.00%        | $XXX,XXX        | $XXX,XXX  | $XX,XXX         | $XX,XXX        |
| +2.00%        | $XXX,XXX        | $XXX,XXX  | $XX,XXX         | $XX,XXX        |

**Impact of Lease Term Changes:**

| Scenario | Lease Term | Lease Liability | Total Interest | Total Expense |
|----------|------------|-----------------|----------------|---------------|
| Base     | XX months  | $XXX,XXX        | $XX,XXX        | $XXX,XXX      |
| +12 months | XX months | $XXX,XXX        | $XX,XXX        | $XXX,XXX      |
| -12 months | XX months | $XXX,XXX        | $XX,XXX        | $XXX,XXX      |

---

## Disclosure Requirements

### IFRS 16 Required Disclosures

**Quantitative:**
1. Carrying amount of ROU assets by class
2. Additions to ROU assets
3. Depreciation charge for ROU assets
4. Lease liability maturity analysis
5. Total cash outflow for leases
6. Interest expense on lease liabilities

**Qualitative:**
1. Nature of leasing activities
2. Future cash outflows for off-balance sheet commitments
3. Restrictions or covenants imposed by leases
4. Sale and leaseback transactions

**For this lease:**
- Lease classification: [Operating/Finance]
- Total ROU assets: $XXX,XXX
- Total lease liabilities: $XXX,XXX
- Maturity profile: [see table below]

### Lease Liability Maturity Analysis

| Period | Principal Due | Interest Due | Total Payment |
|--------|---------------|--------------|---------------|
| Year 1 | $XX,XXX | $XX,XXX | $XX,XXX |
| Year 2 | $XX,XXX | $X,XXX | $XX,XXX |
| Year 3 | $XX,XXX | $X,XXX | $XX,XXX |
| Year 4 | $XX,XXX | $X,XXX | $XX,XXX |
| Year 5+ | $XX,XXX | $X,XXX | $XX,XXX |
| **Total** | **$XXX,XXX** | **$XX,XXX** | **$XXX,XXX** |

---

## Appendices

### A. Calculation Methodology

**Standards Referenced:**
- IFRS 16 - Leases (International Accounting Standards Board)
- ASC 842 - Leases (Financial Accounting Standards Board - US GAAP)

**Key Accounting Policies:**
1. **Lease identification:** Contract conveys right to control use of identified asset
2. **Discount rate:** Incremental borrowing rate (implicit rate not readily determinable)
3. **Lease term:** Non-cancellable period plus reasonably certain extension options
4. **Lease payments:** Fixed payments including in-substance fixed payments
5. **ROU asset measurement:** Lease liability + initial costs + prepayments - incentives
6. **Depreciation:** Straight-line over shorter of lease term or useful life
7. **Interest:** Effective interest method applied to lease liability

**Software/Tools Used:**
- Claude Code IFRS 16 Calculator
- Manual verification of present value calculations

### B. Assumptions & Limitations

**Assumptions:**
1. Discount rate: X.XX% per annum
   - [How determined: user input / tenant credit rating / market rate]
2. Payment timing: Beginning of month (annuity due)
   - [Typical for commercial leases]
3. Operating costs: [Included / Excluded] from lease liability
   - [Included if fixed or index-based, excluded if variable reimbursement]
4. Lease term: [XX months] with [no extensions / possible extensions]
   - [Extension options not included if not reasonably certain to exercise]
5. Initial direct costs: $XX,XXX
   - [List components or state "none"]

**Limitations:**
1. Tax implications not addressed (consult tax advisor)
2. Deferred tax impact not calculated
3. Foreign exchange implications not considered (if applicable)
4. Portfolio-level disclosures not included
5. Transition adjustments not covered (assumes new lease)

**Data Quality:**
- Source document: [filename]
- Extraction confidence: [High / Medium / Low]
- Items requiring verification: [list any uncertain items]

### C. Supporting Files

**Generated Files:**
- IFRS 16 Calculation Report: `Reports/[filename]_IFRS16_[date].md`
- Lease Liability Amortization Schedule (CSV): `Reports/[filename]_amortization.csv`
- ROU Asset Depreciation Schedule (CSV): `Reports/[filename]_depreciation.csv`
- Journal Entries (CSV): `Reports/[filename]_journal_entries.csv`

**Source Documents:**
- Lease document: [path to file]
- Lease abstract: [path if used]

### D. Contact & Review

**Prepared by:** Claude Code - IFRS 16 Calculator
**Review required by:** [Tenant's controller / CFO / external auditor]
**Next steps:**
1. Review extracted lease terms for accuracy
2. Verify discount rate is appropriate for entity
3. Confirm initial direct costs and lease incentives
4. Validate against general ledger
5. Prepare required note disclosures
6. Coordinate with external auditors

---

## Practical Implementation Checklist

**For Accounting Team:**
- [ ] Review and verify all extracted lease terms
- [ ] Confirm discount rate with treasury/finance team
- [ ] Validate initial direct costs (gather invoices)
- [ ] Confirm lease incentives received (bank statements)
- [ ] Set up ROU asset and lease liability accounts in GL
- [ ] Create recurring journal entry template for monthly entries
- [ ] Configure amortization schedules in lease accounting software
- [ ] Prepare note disclosures for financial statements
- [ ] Coordinate with tax team on deductibility implications
- [ ] Brief external auditors on lease accounting

**For Month-End Close:**
- [ ] Record lease payment (debit lease liability, credit cash)
- [ ] Accrue interest expense (debit interest, credit lease liability)
- [ ] Record depreciation (debit expense, credit accumulated depreciation)
- [ ] Update current vs. non-current split for balance sheet
- [ ] Reconcile lease liability balance to amortization schedule
- [ ] Reconcile ROU asset NBV to depreciation schedule

---

**Report Generated:** [Timestamp]
**Analyst:** Claude Code - IFRS 16/ASC 842 Calculator
**Standards:** IFRS 16 (International) / ASC 842 (US GAAP)
**Version:** 1.0
```

### Step 12: Generate CSV Supporting Files

Create CSV files for easy import into Excel or accounting software:

**1. Amortization Schedule CSV:**
`Reports/[filename]_amortization.csv`

```csv
Month,Date,Opening_Balance,Payment,Interest_Expense,Principal_Reduction,Closing_Balance
1,YYYY-MM-DD,$XXX XXX.XX,$X XXX.XX,$X XXX.XX,$X XXX.XX,$XXX XXX.XX
2,YYYY-MM-DD,$XXX XXX.XX,$X XXX.XX,$X XXX.XX,$X XXX.XX,$XXX XXX.XX
...
```

**2. Depreciation Schedule CSV:**
`Reports/[filename]_depreciation.csv`

```csv
Month,Date,Opening_NBV,Depreciation_Expense,Accumulated_Depreciation,Closing_NBV
1,YYYY-MM-DD,$XXX XXX.XX,$X XXX.XX,$X XXX.XX,$XXX XXX.XX
2,YYYY-MM-DD,$XXX XXX.XX,$X XXX.XX,$XX XXX.XX,$XXX XXX.XX
...
```

**3. Journal Entries CSV:**
`Reports/[filename]_journal_entries.csv`

```csv
Date,Entry_Type,Account,Debit,Credit,Description
YYYY-MM-DD,Initial,"Right-of-Use Asset",$XXX XXX.XX,,"Initial recognition"
YYYY-MM-DD,Initial,"Lease Liability",,$XXX XXX.XX,"Initial recognition"
YYYY-MM-DD,Month_1,"Lease Liability",$X XXX.XX,,"Month 1 payment"
YYYY-MM-DD,Month_1,"Cash",,$X XXX.XX,"Month 1 payment"
...
```

### Step 13: Summary Output

After creating all files, provide the user with:

1. **Files Created:**
   - Markdown report path
   - CSV amortization schedule path
   - CSV depreciation schedule path
   - CSV journal entries path

2. **Quick Summary:**
   - Initial Lease Liability
   - Initial ROU Asset
   - Monthly depreciation
   - Year 1 total lease expense
   - Year 1 interest expense
   - EBITDA improvement vs. operating lease treatment

3. **Key Metrics:**
   - Debt/asset ratio impact
   - Present value discount (% of gross payments)
   - Effective interest rate

4. **Next Steps:**
   - Review extracted terms
   - Verify discount rate appropriateness
   - Confirm initial costs and incentives
   - Set up GL accounts
   - Configure recurring journal entries
   - Coordinate with auditors

## Important Guidelines

1. **IFRS 16/ASC 842 Compliance:**
   - Follow standards precisely for lease liability measurement
   - Ensure discount rate is incremental borrowing rate
   - Include only required lease payments in liability
   - Apply annuity due convention for advance payments
   - Straight-line depreciation for ROU asset

2. **Calculation Accuracy:**
   - Use monthly compounding for discount rate
   - Verify present value calculations sum correctly
   - Ensure interest expense uses effective interest method
   - Validate that lease liability amortizes to zero at end
   - Check that ROU asset depreciates to zero (or residual if purchase option)

3. **Data Extraction Quality:**
   - Extract complete payment schedule with all escalations
   - Identify free rent periods correctly
   - Classify payments as fixed vs. variable
   - Separate refundable deposits (not in liability)
   - Verify lease term includes only reasonably certain extensions

4. **Professional Output:**
   - Provide clear, auditable work papers
   - Include all assumptions and judgments
   - Generate ready-to-import CSV files
   - Flag areas requiring management judgment
   - Provide implementation checklist for accounting team

5. **Error Handling:**
   - If lease terms unclear, request clarification
   - If discount rate not provided, explain default choice
   - If payment schedule complex, show detailed calculation
   - If initial costs missing, note assumption of zero

## Example Usage

```
/ifrs16-calculation /path/to/lease_abstract.md 5.5 12000
```

This will:
1. Extract lease payment schedule from abstract
2. Apply 5.5% discount rate
3. Capitalize $12,000 of initial direct costs
4. Calculate lease liability and ROU asset
5. Generate amortization and depreciation schedules
6. Create journal entries for entire lease term
7. Produce comprehensive IFRS 16/ASC 842 report with CSV files

Begin the analysis now with the provided document.
