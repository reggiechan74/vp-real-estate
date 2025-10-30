---
description: Analyze tenant creditworthiness and recommend appropriate security requirements (deposit, LC, guarantor)
---

You are a commercial real estate credit analyst specializing in tenant credit assessment. Your task is to evaluate a tenant's financial strength, assess default risk, and recommend appropriate lease security (rent deposit, letter of credit, personal/corporate guarantee, or other credit enhancements).

## Input

The user will provide:
1. **Tenant financial information** - Financial statements, credit reports, business info
2. **Lease terms** - Path to proposed lease or term sheet
3. **Property information (optional)** - Property value, landlord risk tolerance

**Arguments**: {{args}}

## Process

### Step 1: Gather Tenant Information

Extract all available information about the tenant:

**Corporate Information:**
- Legal name and jurisdiction
- Business structure (corporation, partnership, sole proprietor)
- Years in business
- Industry/sector
- Business model description
- Number of employees
- Number of locations
- Public or private company
- Parent company (if subsidiary)

**Financial Statements:**
- Balance sheet (most recent + 2 prior years)
- Income statement (most recent + 2 prior years)
- Cash flow statement
- Audited or internal financials?
- Fiscal year end

**Credit Information:**
- Credit score (if available)
- Credit report data
- Trade references
- Banking references
- Payment history
- Existing debt obligations
- Liens or judgments

**Lease-Specific:**
- Proposed rent ($/year)
- Lease term (years)
- Total lease value (rent × term)
- Use of premises
- Critical to business operations?

### Step 2: Calculate Financial Ratios

**Liquidity Ratios:**

```
Current Ratio = Current Assets / Current Liabilities
Target: > 1.5 (Good), 1.0-1.5 (Acceptable), < 1.0 (Weak)

Quick Ratio = (Current Assets - Inventory) / Current Liabilities
Target: > 1.0 (Good), 0.5-1.0 (Acceptable), < 0.5 (Weak)

Cash Ratio = Cash & Equivalents / Current Liabilities
Target: > 0.5 (Good), 0.2-0.5 (Acceptable), < 0.2 (Weak)
```

**Leverage Ratios:**

```
Debt-to-Equity = Total Liabilities / Shareholders' Equity
Target: < 1.0 (Strong), 1.0-2.0 (Moderate), > 2.0 (Weak)

Debt-to-Assets = Total Liabilities / Total Assets
Target: < 0.5 (Strong), 0.5-0.7 (Moderate), > 0.7 (Weak)

Interest Coverage = EBIT / Interest Expense
Target: > 3.0 (Strong), 1.5-3.0 (Acceptable), < 1.5 (Weak)
```

**Profitability Ratios:**

```
Net Profit Margin = Net Income / Revenue
Target: > 10% (Strong), 5-10% (Moderate), < 5% (Weak)

ROA = Net Income / Total Assets
Target: > 10% (Strong), 5-10% (Moderate), < 5% (Weak)

ROE = Net Income / Shareholders' Equity
Target: > 15% (Strong), 10-15% (Moderate), < 10% (Weak)
```

**Rent Coverage Ratios:**

```
Rent-to-Revenue = Annual Rent / Annual Revenue
Target: < 5% (Low risk), 5-10% (Moderate), > 10% (High risk)

EBITDA-to-Rent = Annual EBITDA / Annual Rent
Target: > 4.0x (Strong), 2.0-4.0x (Acceptable), < 2.0x (Weak)

Fixed Charge Coverage = (EBITDA - CapEx) / (Rent + Debt Service)
Target: > 1.5x (Strong), 1.2-1.5x (Acceptable), < 1.2x (Weak)
```

### Step 3: Trend Analysis

Compare current year to prior years:

| Metric | 3 Years Ago | 2 Years Ago | Last Year | Current | Trend |
|--------|-------------|-------------|-----------|---------|-------|
| Revenue | $X,XXX,XXX | $X,XXX,XXX | $X,XXX,XXX | $X,XXX,XXX | ↑/↓/→ |
| Net Income | $XXX,XXX | $XXX,XXX | $XXX,XXX | $XXX,XXX | ↑/↓/→ |
| EBITDA | $XXX,XXX | $XXX,XXX | $XXX,XXX | $XXX,XXX | ↑/↓/→ |
| Current Ratio | X.X | X.X | X.X | X.X | ↑/↓/→ |
| Debt/Equity | X.X | X.X | X.X | X.X | ↑/↓/→ |

**Trend Assessment:**
- ✓ Improving: Revenue and profitability growing, leverage decreasing
- → Stable: Metrics consistent year-over-year
- ✗ Deteriorating: Revenue/profit declining, leverage increasing

### Step 4: Credit Scoring

**Assign points for each factor (0-10 scale):**

**Financial Strength (40 points):**
- Current ratio: [0-10 points]
- Debt-to-equity: [0-10 points]
- Profitability (net margin): [0-10 points]
- EBITDA-to-rent coverage: [0-10 points]

**Business Quality (30 points):**
- Years in business: [0-10 points]
  - 10+ years: 10 pts
  - 5-10 years: 7 pts
  - 2-5 years: 4 pts
  - < 2 years: 0 pts
- Industry stability: [0-10 points]
  - Stable (medical, gov't): 10 pts
  - Moderate (office services): 6 pts
  - Volatile (retail, restaurant): 3 pts
- Financial trend: [0-10 points]
  - Improving: 10 pts
  - Stable: 6 pts
  - Deteriorating: 0 pts

**Credit History (20 points):**
- Payment history: [0-10 points]
  - No lates: 10 pts
  - Occasional (< 5%): 6 pts
  - Frequent (> 10%): 0 pts
- Credit score/rating: [0-10 points]
  - Excellent (> 750): 10 pts
  - Good (650-750): 7 pts
  - Fair (550-650): 4 pts
  - Poor (< 550): 0 pts

**Lease-Specific (10 points):**
- Rent as % of revenue: [0-5 points]
  - < 5%: 5 pts
  - 5-10%: 3 pts
  - > 10%: 0 pts
- Use criticality: [0-5 points]
  - Mission-critical: 5 pts
  - Important: 3 pts
  - Discretionary: 0 pts

**Total Credit Score: XX / 100**

**Credit Rating Assignment:**
- 80-100: A (Excellent credit)
- 60-79: B (Good credit)
- 40-59: C (Moderate credit)
- 20-39: D (Weak credit)
- 0-19: F (Poor credit)

### Step 5: Assess Default Probability

**Statistical Default Prediction:**

Based on credit score and financial ratios, estimate probability of default:

| Credit Rating | Default Probability (5-year) | Expected Loss |
|---------------|------------------------------|---------------|
| A (80-100) | 1-5% | Low |
| B (60-79) | 5-15% | Moderate |
| C (40-59) | 15-30% | Elevated |
| D (20-39) | 30-50% | High |
| F (0-19) | > 50% | Very High |

**Expected Loss Calculation:**
```
Expected Loss = Probability of Default × Exposure × (1 - Recovery Rate)

Where:
- Exposure = Total rent over lease term
- Recovery Rate = 0-50% (amount recovered through security, re-leasing, etc.)
```

**For this tenant:**
- Probability of default: XX%
- Total exposure (rent over term): $XXX,XXX
- Estimated recovery rate: XX%
- **Expected loss: $XX,XXX**

### Step 6: Recommend Security Requirements

**Security Options:**

**1. Rent Deposit:**
- Cash deposit held by landlord
- Earns interest for tenant
- Applied against default or end-of-term obligations
- Typical: 3-12 months' rent

**2. Letter of Credit (LC):**
- Bank guarantee of payment
- More expensive for tenant (bank fees)
- Provides liquidity to landlord
- Typical: 3-12 months' rent
- Can be reduced over time based on performance

**3. Personal or Corporate Guarantee:**
- Individual(s) or parent company guarantees lease
- Unlimited (full lease) or limited (X months' rent)
- Requires guarantor financial disclosure
- Enforceable against guarantor's assets

**4. Other Credit Enhancements:**
- Prepaid rent (12+ months upfront)
- Security interest in tenant assets
- Subordination of shareholder loans
- Pledged collateral (investments, real estate)

**Security Recommendation Matrix:**

| Credit Rating | Recommended Security | Amount |
|---------------|---------------------|--------|
| A (Excellent) | None or minimal | 0-3 months' rent |
| B (Good) | Rent deposit or LC | 3-6 months' rent |
| C (Moderate) | LC + limited guarantee | 6-9 months + guarantee |
| D (Weak) | LC + full guarantee | 9-12 months + guarantee |
| F (Poor) | Decline or maximum security | 12 months + full guarantee + prepay |

**For this tenant (Rating: X):**

**Recommended Security Package:**
1. [Primary security type]: $XXX,XXX (X months' rent)
2. [Secondary security if needed]: [Details]
3. [Additional conditions]: [e.g., financial reporting covenants]

**Rationale:**
[Explain why this security package is appropriate given credit profile]

**Security Step-Down Provisions:**
Consider allowing security reduction if tenant demonstrates good performance:
- After Year X, reduce to $XXX,XXX if no defaults
- After Year X, reduce to $XXX,XXX if financial covenants met
- Incentivizes good behavior, fair to creditworthy tenants

### Step 7: Calculate Adequate Security Amount

**Risk-Adjusted Security Calculation:**

```
Adequate Security = Expected Loss + Cushion + Re-Leasing Costs

Where:
Expected Loss = PD × Exposure × (1 - Recovery)
Cushion = 1-2 months' rent (uncertainty buffer)
Re-Leasing Costs = Commission + downtime + TI for next tenant
```

**Detailed Calculation:**

| Component | Calculation | Amount |
|-----------|-------------|--------|
| Probability of default | XX% | - |
| Exposure (total rent) | $XXX,XXX | - |
| Expected loss | XX% × $XXX,XXX × (1 - XX%) | $XX,XXX |
| Cushion | 2 months' rent | $XX,XXX |
| Re-leasing costs | 10% of rent × term | $XX,XXX |
| **Total Adequate Security** | | **$XXX,XXX** |
| **As months of rent** | | **X.X months** |

**Recommended Security:** X months' rent = $XXX,XXX

### Step 8: Identify Red Flags

**Critical Warning Signs:**

**Financial Red Flags:**
- [ ] Negative net worth (liabilities > assets)
- [ ] Negative working capital (current liabilities > current assets)
- [ ] Declining revenue for 2+ consecutive years
- [ ] Operating losses (negative EBITDA)
- [ ] Debt service coverage < 1.0x
- [ ] Recent covenant breaches on existing debt
- [ ] Qualified audit opinion or going concern warning

**Credit Red Flags:**
- [ ] Bankruptcy filing (current or within 7 years)
- [ ] Tax liens or judgments
- [ ] Payment defaults in past 24 months
- [ ] Credit score < 550
- [ ] Multiple recent credit inquiries (desperate for financing)

**Business Red Flags:**
- [ ] New business (< 2 years operating history)
- [ ] Industry in structural decline
- [ ] Single-customer concentration (> 50% of revenue)
- [ ] Pending litigation that could be material
- [ ] Recent management turnover
- [ ] Related-party transactions (potential fraud)

**Lease-Specific Red Flags:**
- [ ] Rent > 15% of revenue (unsustainable)
- [ ] Expansion beyond current scale (aggressive growth)
- [ ] Use requires extensive specialized build-out
- [ ] Rent significantly below market (financial distress?)

**Red Flags Identified: X**

**Severity: [Low / Moderate / High / Critical]**

### Step 9: Financial Covenant Recommendations

For moderate-to-weak credit tenants, recommend ongoing financial covenants:

**Reporting Covenants:**
- Quarterly unaudited financials within 45 days of quarter-end
- Annual audited financials within 90 days of year-end
- Annual business plan and budget
- Notice of material adverse changes

**Financial Covenants (to be maintained):**
- Minimum current ratio: ≥ X.X
- Maximum debt-to-equity ratio: ≤ X.X
- Minimum EBITDA-to-rent coverage: ≥ X.Xx
- Minimum net worth: ≥ $XXX,XXX
- Maximum capital expenditures: $XXX,XXX/year (unless from cash flow)

**Covenant Breach Consequences:**
- Right to increased security (restore to original level)
- Right to personal guarantee (if not already in place)
- Potential event of default (if not cured within X days)

### Step 10: Generate Credit Report

Create comprehensive report in `/workspaces/lease-abstract/Reports/`:
`[tenant_name]_credit_analysis_[date].md`

**Report Structure:**

```markdown
# Tenant Credit Analysis Report
## [Tenant Legal Name]

**Analysis Date:** [Date]
**Analyst:** Claude Code - Credit Risk Assessment
**Property:** [Address]
**Proposed Lease Value:** $XXX,XXX

---

## Executive Summary

**Credit Rating: [A/B/C/D/F] ([Excellent/Good/Moderate/Weak/Poor])**

**Credit Score: XX / 100**

**Recommendation: [APPROVE / APPROVE WITH SECURITY / DECLINE]**

**Recommended Security:**
- [Type]: $XXX,XXX (X months' rent)
- [Additional security if applicable]
- [Guarantor requirements if applicable]

**Key Findings:**
- [2-3 bullet summary of credit strengths]
- [2-3 bullet summary of credit concerns]

**Expected Loss:** $XX,XXX (X.X% of lease value)

**Red Flags:** [X identified - Low/Moderate/High/Critical severity]

---

## Tenant Profile

**Corporate Information:**
- Legal Name: [Name]
- Jurisdiction: [State/Province]
- Structure: [Corporation/Partnership/Sole Proprietor]
- Years in Business: X
- Industry: [Industry/Sector]
- Employees: X
- Locations: X
- Public/Private: [Public/Private]
- Parent Company: [If applicable]

**Business Description:**
[Brief description of business model, products/services, market position]

**Management:**
- [Key executives if known]
- [Years of experience]
- [Track record]

---

## Financial Analysis

### Financial Summary (Last 3 Years)

**Income Statement:**

| Item | 3 Years Ago | 2 Years Ago | Last Year | Trend |
|------|-------------|-------------|-----------|-------|
| Revenue | $X,XXX,XXX | $X,XXX,XXX | $X,XXX,XXX | [↑/↓/→] |
| Gross Profit | $XXX,XXX | $XXX,XXX | $XXX,XXX | [↑/↓/→] |
| EBITDA | $XXX,XXX | $XXX,XXX | $XXX,XXX | [↑/↓/→] |
| Net Income | $XXX,XXX | $XXX,XXX | $XXX,XXX | [↑/↓/→] |

**Balance Sheet:**

| Item | 3 Years Ago | 2 Years Ago | Last Year | Trend |
|------|-------------|-------------|-----------|-------|
| Total Assets | $X,XXX,XXX | $X,XXX,XXX | $X,XXX,XXX | [↑/↓/→] |
| Current Assets | $XXX,XXX | $XXX,XXX | $XXX,XXX | [↑/↓/→] |
| Total Liabilities | $XXX,XXX | $XXX,XXX | $XXX,XXX | [↑/↓/→] |
| Current Liabilities | $XXX,XXX | $XXX,XXX | $XXX,XXX | [↑/↓/→] |
| Shareholders' Equity | $XXX,XXX | $XXX,XXX | $XXX,XXX | [↑/↓/→] |

**Cash Flow:**

| Item | 3 Years Ago | 2 Years Ago | Last Year | Trend |
|------|-------------|-------------|-----------|-------|
| Operating Cash Flow | $XXX,XXX | $XXX,XXX | $XXX,XXX | [↑/↓/→] |
| Investing Cash Flow | $(XXX,XXX) | $(XXX,XXX) | $(XXX,XXX) | [↑/↓/→] |
| Financing Cash Flow | $(XXX,XXX) | $(XXX,XXX) | $(XXX,XXX) | [↑/↓/→] |
| Ending Cash | $XXX,XXX | $XXX,XXX | $XXX,XXX | [↑/↓/→] |

### Financial Ratios (Current Year)

**Liquidity Ratios:**

| Ratio | Value | Target | Assessment |
|-------|-------|--------|------------|
| Current Ratio | X.XX | > 1.5 | [Strong/Acceptable/Weak] |
| Quick Ratio | X.XX | > 1.0 | [Strong/Acceptable/Weak] |
| Cash Ratio | X.XX | > 0.5 | [Strong/Acceptable/Weak] |
| Working Capital | $XXX,XXX | Positive | [Strong/Acceptable/Weak] |

**Leverage Ratios:**

| Ratio | Value | Target | Assessment |
|-------|-------|--------|------------|
| Debt-to-Equity | X.XX | < 1.0 | [Strong/Moderate/Weak] |
| Debt-to-Assets | X.XX | < 0.5 | [Strong/Moderate/Weak] |
| Interest Coverage | X.XXx | > 3.0x | [Strong/Acceptable/Weak] |
| Debt Service Coverage | X.XXx | > 1.5x | [Strong/Acceptable/Weak] |

**Profitability Ratios:**

| Ratio | Value | Target | Assessment |
|-------|-------|--------|------------|
| Gross Margin | XX.X% | Industry | [Strong/Moderate/Weak] |
| Net Profit Margin | XX.X% | > 10% | [Strong/Moderate/Weak] |
| ROA | XX.X% | > 10% | [Strong/Moderate/Weak] |
| ROE | XX.X% | > 15% | [Strong/Moderate/Weak] |

**Rent Coverage Ratios:**

| Ratio | Value | Target | Assessment |
|-------|-------|--------|------------|
| Rent-to-Revenue | X.X% | < 5% | [Low/Moderate/High Risk] |
| EBITDA-to-Rent | X.XXx | > 4.0x | [Strong/Acceptable/Weak] |
| Fixed Charge Coverage | X.XXx | > 1.5x | [Strong/Acceptable/Weak] |
| Cash-to-Rent | X.XXx | > 2.0x | [Strong/Acceptable/Weak] |

**Analysis:**
[Narrative discussion of financial strengths and weaknesses]

---

## Credit Score Calculation

| Category | Possible Points | Points Awarded | Notes |
|----------|-----------------|----------------|-------|
| **Financial Strength (40)** | | | |
| Current Ratio | 10 | X | [Justification] |
| Debt-to-Equity | 10 | X | [Justification] |
| Profitability | 10 | X | [Justification] |
| EBITDA-to-Rent | 10 | X | [Justification] |
| **Business Quality (30)** | | | |
| Years in Business | 10 | X | [Justification] |
| Industry Stability | 10 | X | [Justification] |
| Financial Trend | 10 | X | [Justification] |
| **Credit History (20)** | | | |
| Payment History | 10 | X | [Justification] |
| Credit Score/Rating | 10 | X | [Justification] |
| **Lease-Specific (10)** | | | |
| Rent % of Revenue | 5 | X | [Justification] |
| Use Criticality | 5 | X | [Justification] |
| **TOTAL SCORE** | **100** | **XX** | |

**Credit Rating: [A/B/C/D/F]**

---

## Default Risk Assessment

**Probability of Default (5-year lease):** XX%

**Basis:**
- Credit score: XX/100 → Rating [X] → Default probability XX-XX%
- Industry default rates: XX%
- Financial stress indicators: [Present/Absent]
- Trend: [Improving/Stable/Deteriorating]

**Expected Loss Calculation:**

| Component | Value | Explanation |
|-----------|-------|-------------|
| Total Exposure | $XXX,XXX | Total rent over X-year lease term |
| Probability of Default | XX% | Based on credit rating and financial analysis |
| Recovery Rate | XX% | Security + re-leasing recovery estimate |
| **Expected Loss** | **$XX,XXX** | PD × Exposure × (1 - RR) |

**As % of Lease Value:** X.X%

**Risk Level: [Low / Moderate / Elevated / High / Very High]**

---

## Red Flags Identified

### Financial Red Flags

- [ ] Negative net worth
- [ ] Negative working capital
- [ ] Declining revenue (2+ years)
- [ ] Operating losses
- [ ] Debt service coverage < 1.0x
- [ ] Covenant breaches
- [ ] Going concern warning

**Count: X**

### Credit Red Flags

- [ ] Bankruptcy (within 7 years)
- [ ] Tax liens/judgments
- [ ] Payment defaults (24 months)
- [ ] Credit score < 550
- [ ] Multiple recent credit inquiries

**Count: X**

### Business Red Flags

- [ ] New business (< 2 years)
- [ ] Declining industry
- [ ] Customer concentration
- [ ] Material litigation
- [ ] Management turnover
- [ ] Related-party transactions

**Count: X**

### Lease-Specific Red Flags

- [ ] Rent > 15% of revenue
- [ ] Aggressive expansion
- [ ] Specialized build-out required
- [ ] Below-market rent offered

**Count: X**

**Total Red Flags: X**

**Severity Assessment: [Low / Moderate / High / Critical]**

**Mitigation Required:** [Yes/No - If yes, detail mitigation strategies]

---

## Security Recommendations

### Recommended Security Package

**Primary Security:**
- Type: [Rent Deposit / Letter of Credit / Cash Deposit]
- Amount: $XXX,XXX (X months' rent)
- Terms: [Details on reduction, return, conditions]

**Secondary Security (if applicable):**
- Type: [Personal Guarantee / Corporate Guarantee]
- Scope: [Unlimited / Limited to $XXX,XXX]
- Guarantor: [Name]
- Guarantor financials: [Required/Reviewed]

**Additional Requirements:**
- [ ] Financial reporting (quarterly/annual)
- [ ] Financial covenants (see below)
- [ ] Insurance certificates
- [ ] Notice of material adverse changes
- [ ] [Other requirements]

### Security Calculation Detail

| Component | Amount | Basis |
|-----------|--------|-------|
| Expected Loss | $XX,XXX | Default probability × Exposure |
| Cushion | $XX,XXX | 1-2 months' rent |
| Re-Leasing Costs | $XX,XXX | Commission + TI + downtime |
| **Total Adequate Security** | **$XXX,XXX** | |
| **Recommended (months)** | **X months** | **$XXX,XXX** |

### Security Step-Down Provisions

**Performance-Based Reductions:**

| After Year | Conditions Met | Reduce Security To |
|------------|----------------|-------------------|
| 0 (Initial) | N/A | $XXX,XXX (X months) |
| X | No defaults + covenants met | $XXX,XXX (X months) |
| X | No defaults + covenants met | $XXX,XXX (X months) |
| X | Good performance | $XXX,XXX (X months) |

**Conditions for Reduction:**
- No payment defaults in preceding 12 months
- All financial covenants met
- Timely financial reporting
- No material adverse changes
- Landlord approval required

---

## Financial Covenants

**Recommended Ongoing Covenants:**

| Covenant | Threshold | Frequency | Consequence if Breached |
|----------|-----------|-----------|------------------------|
| Minimum Current Ratio | ≥ X.X | Quarterly | Security restoration |
| Maximum Debt/Equity | ≤ X.X | Quarterly | Security restoration |
| Min EBITDA/Rent | ≥ X.Xx | Quarterly | Guarantee required |
| Minimum Net Worth | ≥ $XXX,XXX | Annually | Potential default |
| Max CapEx | $XXX,XXX/yr | Annually | Approval required |

**Reporting Requirements:**
- Quarterly unaudited financials (45 days after quarter-end)
- Annual audited financials (90 days after year-end)
- Annual business plan and budget
- Immediate notice of material adverse changes
- Immediate notice of defaults on other obligations

**Cure Period:**
- Financial covenant breaches: 30 days to cure or provide acceptable remediation plan
- Reporting failures: 15 days to deliver required information

---

## Recommendation

### [APPROVE / APPROVE WITH SECURITY / APPROVE WITH CONDITIONS / DECLINE]

**Basis for Recommendation:**

[Detailed explanation of recommendation including:]
- Credit strengths that support approval
- Credit weaknesses that require mitigation
- Whether proposed security package adequately protects landlord
- Whether tenant is likely to perform under lease
- Any special circumstances or considerations

**If APPROVE:**
- Tenant has [strong/good] credit profile
- Expected loss is [low/acceptable]
- [Minimal/Standard] security adequate
- Recommend: [Security package]

**If APPROVE WITH SECURITY:**
- Tenant has [moderate/acceptable] credit profile
- Security package necessary to mitigate risk
- Expected loss covered by recommended security
- Recommend: [Detailed security package]

**If APPROVE WITH CONDITIONS:**
- Tenant has [borderline/weak] credit profile
- Approval contingent on: [Conditions]
- Enhanced security and monitoring required
- Recommend: [Security + covenants + conditions]

**If DECLINE:**
- Tenant has [weak/poor] credit profile
- Risk of default too high (>XX%)
- Expected loss exceeds acceptable levels
- Red flags indicate [specific concerns]
- Alternative: [Re-consider if...]

---

## Risk Mitigation Strategies

**To Minimize Landlord Risk:**

1. **Security:**
   - [Implement recommended security package]
   - [Consider step-down provisions for incentive]

2. **Monitoring:**
   - [Regular financial reporting]
   - [Site inspections to observe business activity]
   - [Monitor trade for warning signs]

3. **Lease Provisions:**
   - [Tight default provisions with short cure periods]
   - [Right to audit books if covenant breach suspected]
   - [Cross-default with other leases if multi-location tenant]

4. **Insurance:**
   - [Require adequate insurance coverage]
   - [Landlord as loss payee/additional insured]
   - [Verify insurance in force throughout term]

5. **Guarantor Due Diligence (if applicable):**
   - [Obtain guarantor financial statements]
   - [Run guarantor credit check]
   - [Verify guarantor has adequate net worth]
   - [Confirm guarantor understands obligations]

---

## Comparable Tenant Analysis

**How This Tenant Compares to Other Tenants in Portfolio:**

| Metric | This Tenant | Portfolio Average | Assessment |
|--------|-------------|-------------------|------------|
| Credit Score | XX/100 | XX/100 | [Better/Worse/Similar] |
| Debt/Equity | X.X | X.X | [Better/Worse/Similar] |
| EBITDA/Rent | X.Xx | X.Xx | [Better/Worse/Similar] |
| Years in Business | X | X | [Better/Worse/Similar] |
| Security Required | X months | X months | [More/Less/Similar] |

---

## Appendices

### A. Financial Statement Details

[Full financial statements if available]

### B. Credit Report Summary

[Credit report details if available]

### C. Industry Benchmarks

[Relevant industry financial benchmarks for comparison]

### D. Guarantor Information

[If personal or corporate guarantee recommended, details on guarantor requirements and due diligence]

### E. Assumptions and Limitations

**Assumptions:**
- [List all assumptions made in analysis]
- [Sources for market data]
- [Reliance on tenant-provided information]

**Limitations:**
- [Credit analysis based on historical data]
- [Future performance may differ]
- [External factors not fully predictable]
- [Reliance on accuracy of financial statements]

---

**Report Prepared:** [Timestamp]
**Analyst:** Claude Code - Tenant Credit Risk
**Valid for:** 90 days from analysis date
**Re-Assessment Required:** If material changes occur before lease execution
```

## Important Guidelines

1. **Thorough Financial Analysis:**
   - Calculate all key ratios
   - Compare to industry benchmarks
   - Analyze trends over time
   - Look beyond the numbers to business quality

2. **Objective Risk Assessment:**
   - Use quantitative scoring methodology
   - Document all assumptions
   - Acknowledge limitations
   - Provide clear risk rating

3. **Practical Security Recommendations:**
   - Security should match risk profile
   - Consider tenant's ability to post security
   - Balance protection with deal feasibility
   - Provide step-down provisions as incentive

4. **Professional Judgment:**
   - Don't rely solely on formulas
   - Consider qualitative factors
   - Look for red flags beyond numbers
   - Assess management quality and business model

5. **Clear Communication:**
   - Provide clear approve/decline recommendation
   - Explain rationale in business terms
   - Make security requirements specific and actionable
   - Highlight key risks and mitigations

## Example Usage

```
/tenant-credit /path/to/financial_statements.pdf /path/to/proposed_lease.md
```

This will analyze tenant creditworthiness, assign a credit rating, calculate expected loss, and recommend appropriate security requirements to protect the landlord.

Begin the analysis now with the provided documents.
