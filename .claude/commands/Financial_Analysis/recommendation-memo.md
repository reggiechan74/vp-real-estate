---
name: recommendation-memo
description: Generate VTS Recommendation Memo for lease approval with tenant analysis, financial covenant review, and deal terms comparison
arguments:
  - name: offer-to-lease
    description: Path to the offer to lease or lease agreement document (PDF/DOCX)
    required: true
  - name: financial-statements
    description: Path to tenant financial statements (PDF/DOCX)
    required: false
  - name: credit-check
    description: Path to tenant credit check report (PDF/DOCX)
    required: false
  - name: market-comps
    description: Path to market comparables data (PDF/DOCX/JSON)
    required: false
---

# VTS Recommendation Memo for Approval

You are tasked with generating a comprehensive VTS Recommendation Memo for lease approval based on the provided documents.

## Required Document

**Offer to Lease / Lease Agreement**: `{offer-to-lease}`

## Optional Supporting Documents

**Tenant Financial Statements**: `{financial-statements}` (if provided)
**Tenant Credit Check**: `{credit-check}` (if provided)
**Market Comparables**: `{market-comps}` (if provided)

---

## Extraction & Analysis Instructions

### Phase 1: Extract Key Information

#### From Offer to Lease / Lease Agreement

Extract the following deal terms:
- **Tenant Name** (legal entity name)
- **Entity Type** (sole proprietorship, partnership, corporation)
- **Indemnifier/Guarantor** (if any) and entity type
- **Premises**: Address, unit number, square footage (rentable and usable if available)
- **Lease Term**: Commencement date, expiry date, total months/years
- **Base Rent**: Annual $/sf and total annual rent
- **Rent Schedule**: Year-by-year escalations
- **TMI/Additional Rent**: Annual estimate
- **Security Deposit**: Amount, form (cash, LC, etc.)
- **Free Rent Period**: Months of abatement, timing
- **Tenant Improvements**: Landlord contribution ($/sf or total), tenant work allowance
- **Renewal Options**: Number of terms, notice period, rent determination method
- **Use Clause**: Permitted use
- **Special Provisions**: Any material deal terms from Schedule G or special clauses

#### From Tenant Financial Statements (if provided)

Extract and calculate:
- **Reporting Period**: Most recent fiscal year-end
- **Statement Type**: Audited, reviewed, or notice to reader (NTR)
- **Revenue**: Total annual revenue
- **EBITDA** or **Net Income**
- **Total Assets** and **Total Liabilities**
- **Current Assets** and **Current Liabilities**
- **Cash and Cash Equivalents**
- **Working Capital**: Current Assets - Current Liabilities
- **Key Ratios**:
  - Current Ratio: Current Assets ÷ Current Liabilities
  - Debt-to-Equity: Total Liabilities ÷ Equity
  - EBITDA to Rent Coverage: EBITDA ÷ Proposed Annual Rent
- **Cash Flow Analysis**: Operating cash flow trend (if multi-year statements available)
- **Liquidity Assessment**: Cash reserves relative to rent obligations

**Financial Solvency & Manipulation Scores**:
- If statements are **audited or reviewed**: No need to calculate Z-score or M-score
- If statements are **NTR or manually generated and appear suspect**: Calculate Altman Z-score (financial solvency) and Beneish M-score (financial manipulation detection)

#### From Credit Check Report (if provided)

Extract:
- **Credit Score** (Equifax, Dun & Bradstreet, etc.)
- **Payment History**: Trade references, payment behavior
- **Public Records**: Liens, judgments, bankruptcies
- **Credit Recommendations**: Any flags or concerns

#### From Market Comparables (if provided)

Extract recent comparable transactions:
- Property address
- Lease date
- Square footage
- Base rent ($/sf)
- TMI ($/sf)
- Total occupancy cost
- Free rent periods
- TI allowances
- Lease term
- Building class and location

### Phase 2: Research & Context Gathering

1. **Tenant Business Description**:
   - If available, search for the tenant's website (use WebSearch if needed)
   - Extract business description from "About Us" or similar section
   - Determine: Years in operation, business type, geographic presence

2. **Space Vacancy History**:
   - Note current vacancy status of the premises
   - If vacant: Duration of vacancy
   - Previous tenant (if known from context or provided)

3. **Deal History**:
   - Note if this is the 1st, 2nd, or nth deal attempt on this unit
   - Any previous dead deals or rejected offers

4. **Budget Context**:
   - If budget information is available in supporting documents, extract budgeted rent and NER
   - If no budget available, note this explicitly

---

## Phase 3: Generate VTS Recommendation Memo

Create a comprehensive recommendation memo following this structure:

### 1. TENANT PROFILE

**Format**:
> [Tenant Legal Name] is a [sole proprietorship/partnership/corporation] that engages in [business description extracted from website or documents] and has been operating for [X years] in [general location/region or specific address if known].

**If Indemnifier/Guarantor exists**:
> The Indemnifier, being [Indemnifier Legal Name], is a [entity type] that engages in [business description].

### 2. FINANCIAL COVENANT & CREDIT ANALYSIS

Provide a detailed but concise assessment covering:

**Financial Statements Summary**:
- Statement type (audited/reviewed/NTR) and period
- Revenue and profitability metrics
- Balance sheet strength (assets, liabilities, equity)
- Working capital and liquidity position
- Key financial ratios with interpretation

**Credit Assessment**:
- Credit score and rating interpretation
- Payment history and trade references
- Public records or red flags
- Overall credit risk assessment

**Cash Flow & Rent Affordability**:
- Describe cash flow in general terms
- **Critical Analysis**: Can the tenant's cash flow support the proposed annual rent of $[X]?
- Compare to existing rent if known (typically new rent is higher)
- EBITDA-to-rent coverage ratio and adequacy assessment

**Z-Score & M-Score** (if calculated):
- Altman Z-score result and interpretation (>2.99 = safe zone, 1.81-2.99 = grey zone, <1.81 = distress zone)
- Beneish M-score result and interpretation (>-2.22 suggests possible manipulation)
- Recommendation based on scores

**Overall Financial Covenant Conclusion**:
> Based on the financial analysis, [Tenant Name]'s financial position is [strong/adequate/weak] with [key strengths] and [key concerns if any]. The tenant [is/is not] financially capable of meeting the lease obligations.

### 3. PREMISES DESCRIPTION

**Current Status**:
- Address and unit number
- Rentable square footage
- Current occupancy status (vacant or occupied)
- If vacant: Duration of vacancy (e.g., "vacant for 8 months since [Previous Tenant] vacated")
- Previous tenant information if available

### 4. DEAL HISTORY & CONTEXT

- Unit listing status (listed on [date] or not listed)
- Number of previous deal attempts: "This is the [1st/2nd/nth] deal in play since the unit was listed"
- Summary of any previous dead deals and reasons for failure (if known)

### 5. MULTIPLE OFFERS COMPARISON (if applicable)

If multiple offers were received:
- Create comparison table showing:
  - Offer A vs Offer B vs Recommended Offer
  - Key terms: Rent, term, free rent, TI, security, total consideration
- **Analysis**: Why this offer was selected over others
- Trade-offs and decision rationale

### 6. PROPOSED DEAL TERMS vs. MARKET

**Deal Summary**:
| Term | Proposed Deal |
|------|---------------|
| Base Rent | $[X]/sf/year |
| TMI | $[Y]/sf/year |
| Total Occupancy Cost | $[Z]/sf/year |
| Lease Term | [X] years |
| Free Rent | [X] months |
| TI Allowance | $[X]/sf or $[Y] total |
| Security Deposit | $[X] or [form] |

**Market Comparables Summary**:

Create a table of recent comparable transactions:

| Property | Date | SF | Rent ($/sf) | TMI ($/sf) | Total ($/sf) | Free Rent | TI ($/sf) | Term |
|----------|------|-----|-------------|------------|--------------|-----------|-----------|------|
| [Address 1] | [Date] | [SF] | $[X] | $[Y] | $[Z] | [X] mo | $[Y] | [X] yr |
| [Address 2] | [Date] | [SF] | $[X] | $[Y] | $[Z] | [X] mo | $[Y] | [X] yr |
| **Proposed Deal** | **[Date]** | **[SF]** | **$[X]** | **$[Y]** | **$[Z]** | **[X] mo** | **$[Y]** | **[X] yr** |

**Market Positioning Analysis**:
- Is the proposed rent at/above/below market?
- How do concessions (free rent, TI) compare to market norms?
- Are there any market-driven adjustments or compromises?
- Reference VTS analysis tab comps if available
- **Conclusion**: This deal is [at market/above market/below market] based on recent transactions in [same building/similar buildings in portfolio/submarket].

### 7. PROPOSED DEAL TERMS vs. BUDGET & NER ANALYSIS

**Budget Comparison** (if budget available):
| Metric | Budget | Proposed | Variance |
|--------|--------|----------|----------|
| Base Rent ($/sf) | $[X] | $[Y] | $[Z] or [%] |
| Net Effective Rent | $[X] | $[Y] | $[Z] or [%] |
| Total Consideration | $[X] | $[Y] | $[Z] or [%] |

**If no budget**:
> No formal budget was established for this unit because [reason: new development, opportunistic deal, market-driven negotiation, etc.].

**Breakeven NER Analysis**:
- Calculate or reference breakeven Net Effective Rent
- Compare proposed deal NER to breakeven
- **Conclusion**: This deal is [accretive/dilutive] to the portfolio
  - If **accretive**: NER exceeds breakeven by $[X]/sf or [Y%]
  - If **dilutive**: NER is below breakeven by $[X]/sf or [Y%]

**If Deal is Dilutive**:
Provide additional justification:
- Reasons for supporting the deal despite being dilutive:
  - Portfolio stabilization strategy
  - Tenant quality and long-term relationship
  - Market conditions requiring competitive positioning
  - Alternative uses limited
- Mitigation strategies implemented:
  - Shorter lease term to allow for market re-positioning ([X] years instead of [Y] years)
  - Reduced TI allowance
  - Enhanced security provisions
  - Other concessions minimized

### 8. RECOMMENDATION

**Overall Recommendation**: [APPROVE / APPROVE WITH CONDITIONS / REJECT]

**Rationale**:
- Summarize key strengths of the deal (tenant quality, market positioning, economic returns)
- Address any concerns or risks and how they are mitigated
- Confirm alignment with portfolio strategy and asset plan

**Conditions** (if applicable):
- Enhanced security requirements
- Personal guarantees or indemnities
- Financial reporting covenants
- Other conditions precedent to execution

---

## Phase 4: Document Checklist

Generate a checklist of approval documents required:

### Required Approval Documents

- [ ] **Tenant Financial Statements** - [Most recent fiscal year] [audited/reviewed/NTR]
- [ ] **Tenant Credit Check** - [Provider] dated [Date]
- [ ] **Market Comparables** - [Number] comparable transactions analyzed
- [ ] **Draft Waiver** (if applicable) - Waiver of [specific provisions]
- [ ] **Final Executed Offer to Lease** - Signed by tenant on [Date], landlord approval pending

**Document Status**:
- All required: [Complete / Pending: [list missing documents]]

---

## Output Format

**File Naming**: `Reports/YYYY-MM-DD_HHMMSS_recommendation_memo_[tenant_name].md`

**Report Structure**:
```markdown
# VTS RECOMMENDATION MEMO FOR APPROVAL

**Property**: [Address, Unit]
**Tenant**: [Legal Name]
**Prepared By**: Claude Code
**Date**: [YYYY-MM-DD]
**Recommendation**: [APPROVE / APPROVE WITH CONDITIONS / REJECT]

---

## 1. TENANT PROFILE
[Content as specified above]

## 2. FINANCIAL COVENANT & CREDIT ANALYSIS
[Content as specified above]

## 3. PREMISES DESCRIPTION
[Content as specified above]

## 4. DEAL HISTORY & CONTEXT
[Content as specified above]

## 5. MULTIPLE OFFERS COMPARISON
[Content as specified above if applicable]

## 6. PROPOSED DEAL TERMS vs. MARKET
[Content as specified above]

## 7. PROPOSED DEAL TERMS vs. BUDGET & NER ANALYSIS
[Content as specified above]

## 8. RECOMMENDATION
[Content as specified above]

---

## APPROVAL DOCUMENTS CHECKLIST
[Checklist as specified above]

---

**Prepared using Claude Code Lease Management Toolkit**
**Report Date**: [Timestamp]
```

---

## Execution Steps

1. **Extract all data** from the offer to lease and supporting documents
2. **Research tenant** business description if website URL can be inferred or found
3. **Analyze financials** and calculate ratios, Z-score/M-score if needed
4. **Compare to market** using provided comps or reference typical market ranges
5. **Calculate NER** and determine if deal is accretive or dilutive
6. **Generate memo** following the exact structure above
7. **Create checklist** of approval documents with status
8. **Save report** to `Reports/` with proper timestamp naming convention

---

## Critical Requirements

- **Tenant entity description** must include business type, years operating, and location
- **Financial analysis** must address cash flow adequacy for proposed rent
- **Market comparison** must reference specific comparable transactions
- **NER analysis** must clearly state if deal is accretive or dilutive
- **If dilutive**: Must provide justification and mitigation strategies
- **If no budget**: Must explain why
- **If multiple offers**: Must explain why this offer was selected
- **All dollar amounts** should be presented consistently ($/sf annual and total $ where applicable)
- **All tables** must be properly formatted in Markdown
- **Recommendation** must be clear and supported by analysis

---

## Notes

- Use professional, executive-level language suitable for approval committees
- Be objective and balanced in risk assessment
- Highlight both strengths and concerns
- Provide actionable recommendations
- Ensure all analysis is data-driven and referenced
- If data is missing or unavailable, explicitly note this and explain impact on recommendation
