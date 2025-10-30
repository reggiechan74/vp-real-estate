---
description: Analyze lease deal economics using the Ponzi Rental Rate framework - extracts terms, runs NPV/NER analysis, generates investment report
---

You are a commercial real estate financial analyst specializing in lease deal analysis using the Ponzi Rental Rate (PRR) framework. Your task is to extract financial terms from lease documents and quotes, generate a JSON input file, run the effective rent calculator, and produce an investment analysis report.

## Input

The user will provide:
1. **Lease document or offer** - Path to lease agreement, offer letter, or term sheet (DOCX, PDF, or MD)
2. **Quotes/invoices (optional)** - Path to landlord's work quotes, TI estimates, or cost breakdowns (PDF)

**Arguments**: {{args}}

## Process

### Step 1: Parse Input Arguments

Extract file paths from the arguments:
- First file should be the lease document
- Subsequent files are quotes/cost documents
- If only one file provided, proceed with lease document only

Example:
```
/path/to/lease-offer.pdf /path/to/ti-quote.pdf /path/to/landlord-work.pdf
```

### Step 2: Load and Analyze Documents

**For Lease Document:**
1. If DOCX, convert using `markitdown` first
2. Read the document using the Read tool
3. Extract ALL financial terms (see extraction checklist below)

**For Quote/Cost Documents:**
1. Read each PDF using the Read tool
2. Extract cost line items, totals, and scope descriptions

### Step 3: Extract Financial Terms

Create a comprehensive extraction checklist. Extract the following from the lease document:

**Property Information:**
- [ ] Building name/address
- [ ] Unit number
- [ ] Rentable area (square feet)
- [ ] Building GLA (if multi-tenant)
- [ ] Property type (Industrial/Office)

**Tenant Information:**
- [ ] Tenant legal name
- [ ] Trade name (if different)

**Lease Terms:**
- [ ] Lease commencement date
- [ ] Lease term (months)
- [ ] Fixturing/early access period (months)
- [ ] Operating costs per square foot (annual)
- [ ] Lease expiry date

**Rent Schedule:**
- [ ] Year 1 rent ($/sf/year)
- [ ] Year 2 rent ($/sf/year)
- [ ] Year 3 rent ($/sf/year)
- [ ] ... continue for all years
- [ ] Escalation method (fixed %, CPI, market review)
- [ ] Notes on rent structure

**Tenant Incentives:**
- [ ] Tenant improvement allowance ($/sf or total)
- [ ] Landlord's work total ($)
- [ ] Amortized tenant work ($)
- [ ] Net free rent (months)
- [ ] Gross free rent (months)
- [ ] Moving allowance ($)
- [ ] Other inducements ($)

**Leasing Costs:**
- [ ] Listing agent commission ($/sf or %)
- [ ] Tenant rep commission ($/sf or %)
- [ ] PM override fee ($)
- [ ] Other costs ($)

**Financial Assumptions:**
- [ ] Discount rate (if specified, otherwise use 10%)

**Investment Parameters (if available):**
- [ ] Acquisition cost ($/sf or total)
- [ ] Going-in LTV (loan-to-value ratio)
- [ ] Mortgage amortization period (months)
- [ ] Dividend yield
- [ ] Interest cost
- [ ] Principal payment rate
- [ ] Building allocation percentage (typically 40%)
- [ ] Remaining building depreciation (years)

**From Quotes/Cost Documents:**
- [ ] Landlord's work breakdown
- [ ] TI construction costs
- [ ] Any additional capital expenditures
- [ ] Scope of work descriptions

### Step 4: Calculate Derived Values

Based on extracted information, calculate:

1. **Rent Schedule Normalization:**
   - If rent given monthly → multiply by 12 to get annual $/sf
   - If rent given as total → divide by area to get $/sf
   - Create array of 10 years (extend if lease is longer)

2. **Commission Calculations:**
   - If given as % of rent → calculate $/sf: `(avg_rent * term_years * commission_%)`
   - Standard defaults if missing:
     - Listing agent: 3-5% or $3-5/sf
     - Tenant rep: 5-10% or $5-10/sf

3. **Operating Costs:**
   - Industrial default: $4-10/sf
   - Office default: $10-20/sf
   - Extract from "Additional Rent" or "Operating Costs" sections

4. **Investment Parameters (if property data available):**
   - Use building allocation: 40% (standard)
   - Use remaining depreciation: 15-25 years (estimate based on building age)
   - Use standard REIT parameters:
     - LTV: 50-60%
     - Dividend yield: 6-7%
     - Interest cost: 3-5%

### Step 5: Generate JSON Input File

Create a JSON file following this structure:

```json
{
  "deal_name": "[Property Address] - [Tenant Name] - [Term] Year Lease",
  "property_info": {
    "building_name": "extracted value",
    "unit_number": "extracted value",
    "area_sf": 0.0,
    "gla_building_sf": 0.0
  },
  "tenant_info": {
    "tenant_name": "extracted value",
    "trade_name": "extracted value"
  },
  "lease_terms": {
    "lease_start_date": "YYYY-MM-DD",
    "lease_term_months": 0,
    "fixturing_term_months": 0,
    "operating_costs_psf": 0.0
  },
  "rent_schedule": {
    "description": "Brief description of rent structure",
    "rent_psf_by_year": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    "months_per_period": [12, 12, 12, 12, 12, 12, 12, 12, 12, 12],
    "notes": "Any notes on escalations or special rent terms"
  },
  "incentives": {
    "tenant_cash_allowance_psf": 0.0,
    "landlord_work_total": 0.0,
    "amortized_tenant_work": 0.0,
    "net_free_rent_months": 0.0,
    "gross_free_rent_months": 0.0,
    "notes": "Summary of incentives"
  },
  "leasing_costs": {
    "listing_agent_commission_psf": 0.0,
    "tenant_rep_commission_psf": 0.0,
    "pm_override_fee": 0.0,
    "other_costs": 0.0,
    "notes": "Commission structure"
  },
  "financial_assumptions": {
    "nominal_discount_rate": 0.10,
    "notes": "10% standard discount rate"
  },
  "investment_parameters": {
    "acquisition_cost": 0.0,
    "going_in_ltv": 0.0,
    "mortgage_amortization_months": 300,
    "dividend_yield": 0.0675,
    "interest_cost": 0.0,
    "principal_payment_rate": 0.0,
    "notes": "Investment parameters if property data available"
  }
}
```

**Important Data Quality Notes:**
1. All rent values should be **annual $/sf**, not monthly
2. All monetary values in dollars, not cents
3. All percentages as decimals (10% = 0.10)
4. All time periods in months
5. Use 0.0 or null for missing values - DO NOT make up data
6. Add detailed notes explaining assumptions or missing data

**Save the JSON file as:**
`/workspaces/lease-abstract/Eff_Rent_Calculator/deals/[tenant_name]_[date]_input.json`

Create the `deals/` directory if it doesn't exist.

### Step 6: Run the Effective Rent Calculator

Execute the calculator using Bash tool:

```bash
cd /workspaces/lease-abstract/Eff_Rent_Calculator
python3 eff_rent_calculator.py deals/[filename]_input.json -o deals/[filename]_results.json
```

Capture the console output for the markdown report.

### Step 7: Generate Markdown Report

Create a comprehensive markdown report in `/workspaces/lease-abstract/Reports/` with filename:
`[tenant_name]_[property]_[date]_analysis.md`

**Report Structure:**

```markdown
# Lease Deal Analysis: [Tenant Name] - [Property Address]

**Analysis Date:** [Current Date]
**Prepared Using:** Ponzi Rental Rate (PRR) Framework

---

## Executive Summary

[2-3 sentence summary covering: property, tenant, term, proposed NER, investment recommendation]

**Quick Decision:**
- Proposed NER: $X.XX /sf/year
- Fully Levered Breakeven: $X.XX /sf/year
- **Recommendation:** ✓ APPROVE / ✗ REJECT / ⚠ NEGOTIATE
- **Spread:** $X.XX /sf/year [above/below] breakeven

---

## Property & Tenant Information

**Property:**
- Address: [full address]
- Unit: [unit number]
- Rentable Area: [X,XXX sf]
- Building GLA: [XX,XXX sf] ([X.X%] of building)
- Property Type: [Industrial/Office]

**Tenant:**
- Legal Name: [tenant name]
- Trade Name: [trade name if different]
- Proposed Use: [description]

---

## Lease Terms Summary

| Term | Value |
|------|-------|
| Commencement Date | YYYY-MM-DD |
| Lease Term | XX months (X years) |
| Fixturing Period | X months |
| Expiry Date | YYYY-MM-DD |
| Operating Costs | $XX.XX /sf/year |

**Rent Schedule:**

| Year | Rent ($/sf/year) | Monthly Rent | Annual Rent |
|------|------------------|--------------|-------------|
| 1 | $XX.XX | $X,XXX | $XXX,XXX |
| 2 | $XX.XX | $X,XXX | $XXX,XXX |
| ... | ... | ... | ... |

Average Face Rent: $XX.XX /sf/year

**Rent Structure Notes:**
[Description of escalations, market reviews, etc.]

---

## Deal Economics

**Tenant Incentives:**

| Item | Amount | $/sf |
|------|--------|------|
| TI Allowance | $XXX,XXX | $XX.XX |
| Landlord's Work | $XXX,XXX | $XX.XX |
| Net Free Rent | X months | $XX.XX |
| Gross Free Rent | X months | $XX.XX |
| **Total Incentives** | **$XXX,XXX** | **$XX.XX** |

**Leasing Costs:**

| Item | Amount | $/sf |
|------|--------|------|
| Listing Agent Commission | $XX,XXX | $X.XX |
| Tenant Rep Commission | $XXX,XXX | $XX.XX |
| **Total Leasing Costs** | **$XXX,XXX** | **$XX.XX** |

**Total Deal Costs:** $XXX,XXX ($XX.XX /sf)

---

## Financial Analysis Results

[Insert the calculator's console output here]

---

## Investment Assessment

### Net Present Value Analysis

| Metric | Value ($/sf) |
|--------|--------------|
| NPV of Net Rent | $XX.XX |
| NPV of Costs | $(XX.XX) |
| **NPV of Lease Deal** | **$XX.XX** |

### Effective Rent Metrics

| Metric | Lease Term Only | Including Fixturing |
|--------|-----------------|---------------------|
| Net Effective Rent (NER) | $XX.XX /sf/year | $XX.XX /sf/year |
| Gross Effective Rent (GER) | $XX.XX /sf/year | $XX.XX /sf/year |
| Effective Term | X.XX years | X.XX years |

**Metric Definitions:**

- **Net Effective Rent (NER)**: Landlord's perspective - actual cash return after all costs (TI, commissions, free rent). This is the annualized return from the lease after accounting for all landlord investments and concessions.

- **Gross Effective Rent (GER)**: Tenant's perspective - total occupancy cost including base rent and operating costs, minus tenant benefits received (TI allowance, landlord's work, free rent). This represents what the tenant effectively pays per year.

- **Effective Term**: The equivalent lease term if all upfront costs were amortized at the discount rate.

### Breakeven Analysis

| Threshold | Required NER ($/sf/year) | Status |
|-----------|--------------------------|--------|
| Unlevered Breakeven | $X.XX | ✓ MET / ✗ FAIL |
| I/O Levered Breakeven | $X.XX | ✓ MET / ✗ FAIL |
| **Fully Levered Breakeven** | **$X.XX** | **✓ MET / ✗ FAIL** |
| Unlevered w/ Capital Recovery | $X.XX | ✓ MET / ✗ FAIL |
| Fully Levered w/ Capital Recovery | $X.XX | ✓ MET / ✗ FAIL |

**Capital Recovery:**
- Sinking Fund Requirement: $X.XX /sf/year
- Building Depreciation Period: XX years remaining

---

## Investment Recommendation

### Cash Flow Analysis

**Proposed Deal NER:** $XX.XX /sf/year

**Critical Comparison:**
- vs. Fully Levered Breakeven: $XX.XX [above/below] ($X.XX spread)
- vs. Market NER: $XX.XX [above/below] (if market data available)
- vs. Budget NER: $XX.XX [above/below] (if budget available)

### Risk Assessment

**Cash Flow Impact:**
- [Accretive/Dilutive] by $X.XX /sf/year
- Annual cash [surplus/shortfall]: $XXX,XXX
- Over term: $X.XX million [gain/loss]

**Valuation Impact:**
- Face rent average: $XX.XX /sf/year
- [Above/Below] in-place rents (if applicable)
- Precedent rent impact: [Positive/Negative/Neutral]

### Recommendation

**[APPROVE / NEGOTIATE / REJECT]**

[Detailed justification considering:
- Whether NER meets breakeven thresholds
- Spread over breakeven
- Cash flow accretion/dilution
- Strategic considerations
- Market conditions
- Tenant quality/creditworthiness]

**If NEGOTIATE:**
- Target NER: $XX.XX /sf/year
- Suggested adjustments:
  - [Increase rent to $XX.XX in year X]
  - [Reduce TI to $XX.XX /sf]
  - [Reduce free rent to X months]
  - [Extend term to X years]

---

## Sensitivity Analysis

**Impact of Key Variables on NER:**

[If time permits, show impact of:]
- ±$5/sf TI allowance → ±$X.XX NER
- ±1 month free rent → ±$X.XX NER
- ±$1/sf rent → ±$X.XX NER
- ±1 year term → ±$X.XX NER

---

## Appendices

### A. Calculation Methodology

This analysis uses the Ponzi Rental Rate (PRR) framework:

Chan, R. (2015). "Understanding the Ponzi Rental Rate: The Challenges with Using Net Effective Rents to Analyze Prospective Lease Deals within Real Estate Investment Trusts." *Real Estate Finance*, Vol. 32, No. 2, pp. 48-61.

**Key Principles:**
- All cash flows discounted at 10% annually (monthly compounding)
- NER calculated as annuity due of NPV
- Breakeven rates based on actual debt/equity servicing requirements
- Capital recovery via Inwood sinking fund method (FV accumulation)

### B. Assumptions & Limitations

**Assumptions Made:**
[List any assumptions, defaults used, or missing data points]

**Data Sources:**
- Lease document: [filename]
- Quotes/invoices: [filenames]
- Investment parameters: [source or "standard REIT assumptions"]

**Limitations:**
[Note any limitations in the analysis]

### C. Supporting Files

- JSON Input: `Eff_Rent_Calculator/deals/[filename]_input.json`
- JSON Results: `Eff_Rent_Calculator/deals/[filename]_results.json`
- Source Documents: [list document paths]

---

**Report Generated:** [Timestamp]
**Analyst:** Claude Code - Effective Rent Calculator
**Framework:** Ponzi Rental Rate (PRR)
```

### Step 8: Summary Output

After creating all files, provide the user with:

1. **Files Created:**
   - JSON input file path
   - JSON results file path
   - Markdown report path

2. **Quick Summary:**
   - Proposed NER
   - Fully Levered Breakeven
   - Recommendation
   - Key issues/concerns

3. **Next Steps:**
   - Review detailed report
   - Verify extracted terms against source documents
   - Adjust assumptions if needed and re-run

## Important Guidelines

1. **Data Extraction Quality:**
   - Be thorough - extract ALL financial terms
   - Flag missing/unclear data in notes fields
   - Never fabricate data - use null or 0.0 for missing values
   - Always explain assumptions in notes

2. **Calculation Accuracy:**
   - Verify rent is annual $/sf (not monthly)
   - Ensure commission calculations are correct
   - Double-check all unit conversions

3. **Professional Output:**
   - Use clear, concise business language
   - Provide actionable recommendations
   - Include enough detail for decision-makers
   - Flag risks and uncertainties

4. **Error Handling:**
   - If calculator fails, report the error clearly
   - If documents are unclear, request clarification
   - If critical data is missing, note in report and provide sensitivity analysis

## Example Usage

```
/effective-rent /path/to/lease-proposal.pdf /path/to/ti-quote.pdf
```

This will:
1. Extract terms from lease proposal
2. Extract costs from TI quote
3. Generate JSON input file
4. Run effective rent calculator
5. Create comprehensive markdown report in /Reports

Begin the analysis now with the provided documents.
