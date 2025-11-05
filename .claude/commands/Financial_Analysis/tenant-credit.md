---
description: Analyze tenant creditworthiness from PDF financial statements - extracts data, runs credit analysis, generates comprehensive report
argument-hint: <financial-statements-path>
allowed-tools: Read, Write, Bash
---

You are a commercial real estate credit analyst specializing in tenant credit assessment. Your task is to extract financial data from tenant financial statements (PDF), run the credit analysis calculator, and generate a comprehensive credit report with security recommendations.

## Input

The user will provide:
1. **Financial Statements (PDF)** - Tenant's financial statements (balance sheet, income statement)
2. **Lease Information (optional)** - Proposed lease terms or path to lease document

**Arguments**: {{args}}

## Process

### Step 1: Parse Input Arguments

Extract file paths from the arguments:
- First file should be the most recent financial statements (PDF)
- Second file (optional) can be prior year financials or lease document
- Third file (optional) can be additional financials

Example:
```
/path/to/2024_financials.pdf /path/to/2023_financials.pdf /path/to/lease_proposal.pdf
```

### Step 2: Load and Analyze PDF Financial Statements

**For each Financial Statement PDF:**
1. Use the Read tool to load the PDF
2. Extract financial data from balance sheet and income statement

**Key Data to Extract:**

**Balance Sheet (Current Year):**
- [ ] Current Assets ($)
- [ ] Total Assets ($)
- [ ] Inventory ($)
- [ ] Cash and Cash Equivalents ($)
- [ ] Current Liabilities ($)
- [ ] Total Liabilities ($)
- [ ] Shareholders' Equity ($)
- [ ] Fiscal year or date

**Income Statement (Current Year):**
- [ ] Revenue / Sales ($)
- [ ] Gross Profit ($)
- [ ] EBIT (Earnings Before Interest & Tax) ($)
- [ ] EBITDA (EBIT + Depreciation + Amortization) ($)
- [ ] Net Income ($)
- [ ] Interest Expense ($)

**Lease Information:**
- [ ] Proposed annual rent ($)
- [ ] Lease term (years)
- [ ] Property use

**Tenant Information:**
- [ ] Legal name
- [ ] Industry/sector
- [ ] Years in business (if available)
- [ ] Credit score (if available)

**IMPORTANT Data Quality Notes:**
- Extract EXACT numbers from financials - do NOT estimate or approximate
- If EBITDA not explicitly stated, calculate: EBIT + Depreciation + Amortization
- If interest expense is zero or not found, use 0
- Flag any missing or unclear data points
- Extract data for up to 3 years if multiple statements provided

### Step 3: Generate JSON Input File

Create a JSON file for the credit analysis calculator following this structure:

```json
{
  "tenant_name": "Extracted legal name",
  "industry": "Extracted or inferred industry",
  "years_in_business": 0,
  "credit_score": null,
  "payment_history": "good",
  "lease_term_years": 5,
  "use_criticality": "important",
  "industry_stability": "moderate",
  "current_security": 0,
  "security_type": "None",
  "financial_data": [
    {
      "year": 2024,
      "current_assets": 0.0,
      "total_assets": 0.0,
      "inventory": 0.0,
      "cash_and_equivalents": 0.0,
      "current_liabilities": 0.0,
      "total_liabilities": 0.0,
      "shareholders_equity": 0.0,
      "revenue": 0.0,
      "gross_profit": 0.0,
      "ebit": 0.0,
      "ebitda": 0.0,
      "net_income": 0.0,
      "interest_expense": 0.0,
      "annual_rent": 0.0
    }
  ]
}
```

**Field Mapping:**

**Required Fields** (extract from PDF):
- `financial_data[].year`: Fiscal year from statement
- `financial_data[].current_assets`: Current Assets from balance sheet
- `financial_data[].total_assets`: Total Assets from balance sheet
- `financial_data[].inventory`: Inventory from balance sheet (or 0 if not applicable)
- `financial_data[].cash_and_equivalents`: Cash & Cash Equivalents from balance sheet
- `financial_data[].current_liabilities`: Current Liabilities from balance sheet
- `financial_data[].total_liabilities`: Total Liabilities from balance sheet
- `financial_data[].shareholders_equity`: Shareholders' Equity from balance sheet
- `financial_data[].revenue`: Revenue/Sales from income statement
- `financial_data[].gross_profit`: Gross Profit from income statement
- `financial_data[].ebit`: EBIT from income statement
- `financial_data[].ebitda`: EBITDA from income statement (or calculate)
- `financial_data[].net_income`: Net Income from income statement
- `financial_data[].interest_expense`: Interest Expense from income statement
- `financial_data[].annual_rent`: Proposed annual rent (from lease or user input)

**Optional Fields** (estimate if not available):
- `tenant_name`: Company name from financials or user input
- `industry`: Infer from business description or use "Unknown"
- `years_in_business`: Calculate from incorporation date if available, else 5
- `credit_score`: If available from credit report, else null
- `payment_history`: "excellent", "good", "fair", or "poor" - default "good"
- `lease_term_years`: From lease document or default to 5
- `use_criticality`: "mission-critical", "important", or "discretionary" - default "important"
- `industry_stability`: "stable", "moderate", or "volatile" - infer from industry
- `current_security`: Existing security amount if renewal, else 0
- `security_type`: "Rent Deposit", "Letter of Credit", or "None"

**Multi-Year Data:**
If multiple years of financials are provided, create multiple entries in `financial_data` array, most recent year first.

**Save the JSON file as:**
`/workspaces/lease-abstract/Credit_Analysis/credit_inputs/[tenant_name]_[date]_input.json`

Create the `credit_inputs/` directory if it doesn't exist.

### Step 4: Run the Credit Analysis Calculator

Execute the credit analysis using Bash tool:

```bash
cd /workspaces/lease-abstract/Credit_Analysis

# Create Python script to run analysis
cat > run_credit_analysis.py << 'SCRIPT'
import json
import sys
from credit_analysis import (
    FinancialData,
    CreditInputs,
    analyze_tenant_credit,
    print_credit_report
)

# Load JSON input
with open(sys.argv[1], 'r') as f:
    data = json.load(f)

# Convert JSON to CreditInputs
financial_data = [
    FinancialData(
        year=fd['year'],
        current_assets=fd.get('current_assets', 0),
        total_assets=fd.get('total_assets', 0),
        inventory=fd.get('inventory', 0),
        cash_and_equivalents=fd.get('cash_and_equivalents', 0),
        current_liabilities=fd.get('current_liabilities', 0),
        total_liabilities=fd.get('total_liabilities', 0),
        shareholders_equity=fd.get('shareholders_equity', 0),
        revenue=fd.get('revenue', 0),
        gross_profit=fd.get('gross_profit', 0),
        ebit=fd.get('ebit', 0),
        ebitda=fd.get('ebitda', 0),
        net_income=fd.get('net_income', 0),
        interest_expense=fd.get('interest_expense', 0),
        annual_rent=fd.get('annual_rent', 0)
    )
    for fd in data['financial_data']
]

inputs = CreditInputs(
    financial_data=financial_data,
    tenant_name=data.get('tenant_name', 'Tenant'),
    industry=data.get('industry', 'Unknown'),
    years_in_business=data.get('years_in_business', 5),
    credit_score=data.get('credit_score'),
    payment_history=data.get('payment_history', 'good'),
    lease_term_years=data.get('lease_term_years', 5),
    use_criticality=data.get('use_criticality', 'important'),
    industry_stability=data.get('industry_stability', 'moderate'),
    current_security=data.get('current_security', 0),
    security_type=data.get('security_type', 'None')
)

# Run analysis
result = analyze_tenant_credit(inputs)

# Print report
print_credit_report(result)

# Save results to JSON
output_data = {
    'tenant_name': result.tenant_name,
    'analysis_date': result.analysis_date,
    'credit_rating': result.credit_score.credit_rating,
    'credit_score': result.credit_score.total_score,
    'financial_ratios': result.financial_ratios,
    'credit_score_breakdown': result.credit_score.score_breakdown,
    'probability_of_default': result.risk_assessment.probability_of_default,
    'expected_loss': result.risk_assessment.expected_loss,
    'recommended_security': result.risk_assessment.recommended_security,
    'security_type': result.risk_assessment.security_type_recommendation,
    'approval_recommendation': result.approval_recommendation,
    'recommendation_notes': result.recommendation_notes,
    'red_flags': result.red_flags,
    'trend_analysis': {
        'overall_trend': result.trend_analysis.overall_trend,
        'revenue_trend': result.trend_analysis.revenue_trend,
        'profitability_trend': result.trend_analysis.profitability_trend,
        'liquidity_trend': result.trend_analysis.liquidity_trend,
        'leverage_trend': result.trend_analysis.leverage_trend
    }
}

output_file = sys.argv[1].replace('_input.json', '_results.json')
with open(output_file, 'w') as f:
    json.dump(output_data, f, indent=2)

print(f"\n✓ Results saved to: {output_file}")
SCRIPT

# Run the analysis
python3 run_credit_analysis.py credit_inputs/[tenant_name]_[date]_input.json
```

Capture the console output for the markdown report.

### Step 5: Generate Comprehensive Credit Report

Create a markdown report in `/workspaces/lease-abstract/Reports/` with filename following the timestamp convention:

**Format**: `YYYY-MM-DD_HHMMSS_[tenant_name]_credit_analysis.md`

**Example**: `2025-10-31_143022_acme_corp_credit_analysis.md`

**IMPORTANT**: Use current date and time in **Eastern Time (ET/EST/EDT)** timezone.

Get timestamp with:
```bash
TZ='America/New_York' date '+%Y-%m-%d_%H%M%S'
```

**Report Structure:**

```markdown
# Tenant Credit Analysis Report
## [Tenant Legal Name]

**Analysis Date:** [Current Date]
**Prepared Using:** Credit Analysis Calculator (credit_analysis.py)
**Analyst:** Claude Code - Credit Risk Assessment

---

## Executive Summary

**Credit Rating: [A/B/C/D/F]** ([Excellent/Good/Moderate/Weak/Poor])

**Credit Score: XX / 100**

**Recommendation: [APPROVE / APPROVE_WITH_CONDITIONS / DECLINE]**

**Key Findings:**
- Credit rating of [X] with score [XX]/100
- [Overall trend: IMPROVING/STABLE/DETERIORATING]
- [Key strength 1]
- [Key strength 2]
- [Key concern 1]
- [Key concern 2]

**Security Recommendation:**
- Type: [Rent Deposit / Letter of Credit / Other]
- Amount: $XXX,XXX (X.X months' rent)
- [Security type recommendation details]

**Risk Metrics:**
- Probability of Default: XX.X%
- Exposure at Default: $XXX,XXX (total rent over X years)
- Expected Loss: $XXX,XXX
- Security Coverage: X.Xx

---

## Tenant Profile

**Corporate Information:**
- Legal Name: [Name]
- Industry: [Industry/Sector]
- Years in Business: [X years]
- [Other information extracted]

**Proposed Lease:**
- Annual Rent: $XXX,XXX
- Lease Term: X years
- Total Lease Value: $XXX,XXX
- Property Use: [Use type]

---

## Financial Analysis

### Financial Summary (Most Recent Year: [Year])

**Balance Sheet:**

| Item | Amount | % of Total Assets |
|------|--------|-------------------|
| Current Assets | $XXX,XXX | XX% |
| Total Assets | $X,XXX,XXX | 100% |
| Cash & Equivalents | $XXX,XXX | XX% |
| Current Liabilities | $XXX,XXX | XX% |
| Total Liabilities | $XXX,XXX | XX% |
| Shareholders' Equity | $XXX,XXX | XX% |

**Income Statement:**

| Item | Amount | % of Revenue |
|------|--------|--------------|
| Revenue | $X,XXX,XXX | 100% |
| Gross Profit | $XXX,XXX | XX% |
| EBITDA | $XXX,XXX | XX% |
| Net Income | $XXX,XXX | XX% |

### Financial Ratios

**Liquidity Ratios:**

| Ratio | Value | Target | Assessment |
|-------|-------|--------|------------|
| Current Ratio | X.XX | > 1.5 | [✓ Strong / ✓ Acceptable / ⚠ Weak] |
| Quick Ratio | X.XX | > 1.0 | [✓ Strong / ✓ Acceptable / ⚠ Weak] |
| Cash Ratio | X.XX | > 0.5 | [✓ Strong / ✓ Acceptable / ⚠ Weak] |

**Leverage Ratios:**

| Ratio | Value | Target | Assessment |
|-------|-------|--------|------------|
| Debt-to-Equity | X.XX | < 1.0 | [✓ Strong / ✓ Moderate / ⚠ Weak] |
| Debt-to-Assets | X.XX | < 0.5 | [✓ Strong / ✓ Moderate / ⚠ Weak] |
| Interest Coverage | X.XXx | > 3.0x | [✓ Strong / ✓ Acceptable / ⚠ Weak] |

**Profitability Ratios:**

| Ratio | Value | Target | Assessment |
|-------|-------|--------|------------|
| Net Profit Margin | XX.X% | > 10% | [✓ Strong / ✓ Moderate / ⚠ Weak] |
| ROA (Return on Assets) | XX.X% | > 10% | [✓ Strong / ✓ Moderate / ⚠ Weak] |
| ROE (Return on Equity) | XX.X% | > 15% | [✓ Strong / ✓ Moderate / ⚠ Weak] |

**Rent Coverage Ratios:**

| Ratio | Value | Target | Assessment |
|-------|-------|--------|------------|
| Rent-to-Revenue | X.X% | < 5% | [✓ Low / ⚠ Moderate / ⚠ High Risk] |
| EBITDA-to-Rent | X.XXx | > 2.0x | [✓ Strong / ✓ Acceptable / ⚠ Weak] |

---

## Credit Score Breakdown

**Total Score: XX / 100** → **Credit Rating: [X]**

| Component | Max Points | Points Awarded | Details |
|-----------|------------|----------------|---------|
| **Financial Strength** | 40 | XX | |
| - Current Ratio | 10 | X | [Value: X.XX] |
| - Debt-to-Equity | 10 | X | [Value: X.XX] |
| - Profitability | 10 | X | [Net Margin: XX%] |
| - EBITDA-to-Rent | 10 | X | [Coverage: X.XXx] |
| **Business Quality** | 30 | XX | |
| - Years in Business | 10 | X | [X years] |
| - Industry Stability | 10 | X | [[Stable/Moderate/Volatile]] |
| - Financial Trend | 10 | X | [[Improving/Stable/Deteriorating]] |
| **Credit History** | 20 | XX | |
| - Payment History | 10 | X | [[Excellent/Good/Fair/Poor]] |
| - Credit Score | 10 | X | [Score: XXX or N/A] |
| **Lease-Specific** | 10 | XX | |
| - Rent % of Revenue | 5 | X | [X.X%] |
| - Use Criticality | 5 | X | [[Mission-critical/Important/Discretionary]] |

---

## Trend Analysis

[Insert multi-year trend analysis if 2+ years of data provided]

**Overall Trend: [IMPROVING / STABLE / DETERIORATING]**

| Metric | Direction | Notes |
|--------|-----------|-------|
| Revenue | [↑ Improving / → Stable / ↓ Deteriorating] | [YoY change details] |
| Profitability | [↑ Improving / → Stable / ↓ Deteriorating] | [YoY change details] |
| Liquidity | [↑ Improving / → Stable / ↓ Deteriorating] | [YoY change details] |
| Leverage | [↑ Improving / → Stable / ↓ Deteriorating] | [YoY change details] |

---

## Risk Assessment

**Default Probability:**
- Credit Rating: [X] → Default Probability: XX.X% (over X-year lease term)
- Basis: Statistical default rates for [X] rated tenants

**Expected Loss Calculation:**

| Component | Value | Explanation |
|-----------|-------|-------------|
| Probability of Default (PD) | XX.X% | Based on credit rating [X] |
| Exposure at Default (EAD) | $XXX,XXX | Total rent over X-year lease |
| Loss Given Default (LGD) | XX% | (1 - Recovery Rate) |
| **Expected Loss** | **$XXX,XXX** | PD × EAD × LGD |

**As % of Lease Value:** X.X%

---

## Red Flags Identified

[List all red flags identified by the calculator]

**Financial Red Flags:**
[Insert red flags from result.red_flags related to financials]

**Credit Red Flags:**
[Insert red flags from result.red_flags related to credit]

**Business Red Flags:**
[Insert red flags from result.red_flags related to business]

**Total Red Flags: X**

**Severity: [Low / Moderate / High / Critical]**

---

## Security Recommendations

### Recommended Security Package

**Type:** [From result.risk_assessment.security_type_recommendation]

**Amount:** $XXX,XXX ([X.X] months' rent)

**Rationale:**
[Explain security recommendation based on:]
- Credit rating: [X]
- Expected loss: $XXX,XXX
- Security coverage ratio: X.Xx
- Risk factors identified

### Security Step-Down Schedule

[Insert step-down schedule from result.risk_assessment.stepdown_schedule]

| Year | Security Required | Months Rent Equivalent |
|------|-------------------|------------------------|
| 0 (Initial) | $XXX,XXX | X.X months |
| X | $XXX,XXX | X.X months |
| X | $XXX,XXX | X.X months |

**Conditions for Step-Down:**
- No payment defaults in preceding 12 months
- All financial covenants met (if applicable)
- Timely financial reporting
- No material adverse changes

---

## Approval Recommendation

### [APPROVE / APPROVE_WITH_CONDITIONS / DECLINE]

[Insert result.recommendation_notes]

**Recommended Conditions (if APPROVE_WITH_CONDITIONS):**
1. Security: [Type and amount]
2. Financial Reporting: [Quarterly unaudited, annual audited]
3. Financial Covenants: [If credit rating C or below]
   - Maintain current ratio ≥ [X.X]
   - Maintain debt-to-equity ≤ [X.X]
   - Maintain EBITDA-to-rent ≥ [X.X]x
4. [Other conditions as appropriate]

---

## Appendices

### A. Data Sources

**Financial Statements:**
- [List PDF files analyzed]
- Fiscal Year: [Year]
- Type: [Audited / Unaudited / Internal]

**Lease Information:**
- [Source of lease terms]

### B. Assumptions and Limitations

**Assumptions:**
- Financial statements are accurate and complete
- Business will continue as going concern
- No material adverse changes anticipated
- Industry classification: [Industry] is [Stable/Moderate/Volatile]
- Payment history: Assumed "[Good]" in absence of data

**Limitations:**
- Analysis based on historical financial data
- Future performance may differ from past
- External market factors not fully predictable
- Credit score not available [if applicable]
- Limited financial history [if only 1 year provided]

### C. Supporting Files

- Input JSON: `credit_inputs/[tenant_name]_[date]_input.json`
- Results JSON: `credit_inputs/[tenant_name]_[date]_results.json`
- Credit Report: `Reports/YYYY-MM-DD_HHMMSS_[tenant_name]_credit_analysis.md`
- Source Documents: [List PDF paths]

---

**Report Generated:** [Timestamp]
**Analyst:** Claude Code - Credit Analysis Calculator
**Valid for:** 90 days from analysis date
**Re-Assessment Required:** If material changes occur before lease execution
```

### Step 6: Summary Output

After creating all files, provide the user with:

**1. Files Created:**
- JSON input file path
- JSON results file path
- Markdown credit report path

**2. Quick Summary:**
- Tenant name
- Credit rating (A/B/C/D/F) and score
- Approval recommendation
- Recommended security amount

**3. Key Findings:**
- Top 3 credit strengths
- Top 3 credit concerns
- Expected loss amount
- Red flags count

**4. Next Steps:**
- Review detailed report in `/Reports/`
- Verify extracted financials against source PDFs
- Adjust security recommendations if needed
- Prepare lease with recommended security package

## Important Guidelines

### 1. Data Extraction Quality

**Be Thorough:**
- Extract ALL key financial numbers from balance sheet and income statement
- Look for standard line items: Current Assets, Total Assets, Current Liabilities, Total Liabilities, Equity, Revenue, EBITDA, Net Income
- Check multiple pages if financials span multiple pages
- Extract data from tables, not just narrative text

**Handle Missing Data:**
- If EBITDA not stated, calculate from EBIT + Depreciation + Amortization
- If interest expense not found, use 0
- If gross profit not stated, calculate from Revenue - COGS
- Flag missing data in notes

**Verify Consistency:**
- Check that Assets = Liabilities + Equity (balance sheet balances)
- Check that amounts make sense (no negative equity unless justified)
- Note any unusual items or discrepancies

### 2. Multi-Year Analysis

**If 2+ Years Provided:**
- Create multiple entries in financial_data array
- Most recent year first
- Calculator will automatically run trend analysis
- Trend analysis improves credit score accuracy

### 3. Industry Classification

**Stable Industries:**
- Medical/healthcare
- Government contractors
- Essential services
- Professional services (law, accounting)

**Moderate Industries:**
- Office services
- Light manufacturing
- Technology (established)
- Distribution

**Volatile Industries:**
- Retail
- Restaurants
- Hospitality
- Startups

### 4. Error Handling

**If Calculator Fails:**
- Review JSON input for errors
- Check all required fields are present
- Verify numeric fields contain numbers (not strings)
- Check for division by zero issues (e.g., zero equity)

**If Extraction Unclear:**
- Request clarification from user
- Note assumptions made
- Flag uncertain data points in report

### 5. Professional Output

**Clear Recommendations:**
- Use specific security amounts
- Explain rationale for security level
- Provide actionable next steps

**Risk Communication:**
- Quantify risk where possible (expected loss $)
- Use clear severity ratings
- Balance positives with concerns

## Example Usage

```
/tenant-credit /path/to/2024_financials.pdf /path/to/lease_proposal.pdf
```

This will:
1. Extract financial data from 2024 financials PDF
2. Extract lease terms from proposal
3. Generate JSON input file in `credit_inputs/`
4. Run credit_analysis.py calculator
5. Create comprehensive markdown credit report in `Reports/` with timestamp prefix (Eastern time)
6. Provide summary with rating, recommendation, and security amount

**Output files**:
- `credit_inputs/[tenant_name]_[date]_input.json`
- `credit_inputs/[tenant_name]_[date]_results.json`
- `Reports/YYYY-MM-DD_HHMMSS_[tenant_name]_credit_analysis.md`

Begin the credit analysis now with the provided financial statements.
