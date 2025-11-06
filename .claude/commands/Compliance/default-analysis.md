---
description: Assess potential lease defaults, calculate cure periods, analyze landlord remedies, and draft default notices
argument-hint: <lease-path> <default-description>
allowed-tools: WebSearch, WebFetch, Read, Write, Bash
---

# Default Analysis: Tenant Default & Damage Quantification

**Automated JSON → Python → Report workflow for default damage calculation and notice generation**

You are executing the **/default-analysis** slash command. You are an expert in **Commercial Lease Enforcement** and **Default Remedies**, specializing in damage quantification and formal notice preparation.

## Objective

When tenant defaults on lease obligations:
1. **Quantify damages** - Calculate accelerated rent, re-leasing costs, lost rent, mitigation credits
2. **Model bankruptcy scenarios** - Expected recovery under §502(b)(6) (US) or BIA (Canada)
3. **Generate formal notice** - Legally-formatted default notice with damage breakdown
4. **Provide strategic guidance** - Recommend optimal remedy path

## Input

**Arguments**: {{args}}

The user will provide:
1. **Lease document or abstract** - Path to lease with default provisions
2. **Default description** - What breach occurred (monetary, non-monetary, insolvency)
3. **Supporting documentation (optional)** - Payment records, evidence

## Workflow Steps

### Step 1: Extract Lease Terms from Document

Extract key data for damage calculation:

**Core Terms**:
- Property address
- Tenant legal name
- Landlord legal name
- Current monthly rent (base rent)
- Current annual rent
- Rentable area (SF)
- Rent per SF
- Lease commencement date
- Lease expiry date
- Remaining months on lease

**Additional Information**:
- Additional rent annual (taxes, opex, CAM)
- Security deposit amount
- Monetary default cure period (typically 5-10 days)
- Non-monetary default cure period (typically 15-30 days)

**Market Assumptions** (for damage calculation):
- Market rent per SF (current market rate)
- TI allowance per SF (for new tenant)
- Leasing commission % (typically 5%)
- Legal fees for new lease (typically $5,000-$15,000)
- Expected downtime months (vacancy before re-lease)
- Discount rate annual (typically 10% for NPV calculations)

### Step 2: Identify Default Type and Create Input JSON

**Default Types**:
- **Monetary**: Non-payment of rent, additional rent, charges
- **Non-Monetary**: Unauthorized alterations, prohibited use, failure to insure, etc.
- **Insolvency**: Bankruptcy filing, receivership, assignment for creditors

Build JSON file:

```json
{
  "lease_terms": {
    "property_address": "123 Industrial Parkway, Mississauga, ON L5T 2K9",
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
    "description": "Failure to pay base rent for November 2025",
    "amount_owing": 25000.00,
    "cure_period_days": 5,
    "cure_deadline": "2025-11-11"
  }
}
```

**Save to**: `Default_Calculator/default_inputs/YYYY-MM-DD_HHMMSS_[tenant_name]_default.json`

### Step 3: Run Python Damage Calculator

Execute the default calculator:

```bash
python3 Default_Calculator/default_calculator.py \
  Default_Calculator/default_inputs/YYYY-MM-DD_HHMMSS_[tenant_name]_default.json

# Output: *_results.json (automatically generated in same directory)
```

This calculates:
1. **Accelerated Rent (NPV)** - Present value of remaining lease payments
2. **Re-leasing Costs** - TI allowance, commissions, legal fees
3. **Lost Rent** - Downtime before re-leasing (monthly rent × downtime months)
4. **Mitigation Credits** - Security deposit + re-lease rent offset (NPV)
5. **Bankruptcy Scenarios** - §502(b)(6) statutory caps, expected recovery

**Example Output**:
```
Gross damages: $1,957,077
Total credits: $789,387
Net damages: $1,167,690

Bankruptcy expected recovery: $137,500
Bankruptcy expected loss: $1,819,577
```

### Step 4: Generate Default Notice

Execute the notice generator:

```bash
python3 Default_Calculator/notice_generator.py \
  Default_Calculator/default_inputs/YYYY-MM-DD_HHMMSS_[tenant_name]_default.json \
  /workspaces/lease-abstract/Reports/YYYY-MM-DD_HHMMSS_default_notice_[tenant_name].md \
  [jurisdiction]

# jurisdiction: "Ontario", "Alberta", "New York", etc. (default: "Ontario")
```

This generates formal notice with:
- **Header**: Date, parties, lease reference
- **Statement of Default**: Type, date, description, amount owing
- **Cure Demand**: Cure deadline, payment instructions
- **Damage Breakdown**: Itemized table (immediate, future, re-leasing costs, credits)
- **Bankruptcy Warning**: Expected recovery if tenant files bankruptcy
- **Reservation of Rights**: Preserves all landlord remedies
- **Legal Framework**: Jurisdiction-specific citations

### Step 5: Research Applicable Legislation (If Required)

**IMPORTANT**: If the default involves complex statutory issues or if you need to cite specific legislation in the notice, use WebSearch and WebFetch to research current law.

**Canada - Key Statutes**:
- **Ontario**: *Commercial Tenancies Act*, R.S.O. 1990, c. L.7
- **Alberta**: *Law of Property Act*, R.S.A. 2000, c. L-7 (Part 4)
- **BC**: *Commercial Tenancy Act*, S.B.C. 2020, c. 4
- **Federal**: *Bankruptcy and Insolvency Act*, R.S.C. 1985, c. B-3

**United States - Key Statutes**:
- **Bankruptcy**: 11 U.S.C. §502(b)(6) (landlord claim cap)
- **State**: Each state has different commercial lease laws

**Research Process**:
1. **WebSearch**: "[Jurisdiction] commercial tenancies act [current year]"
2. **WebFetch**: Extract relevant sections (default provisions, remedies, notice requirements)
3. **Compare**: Lease provisions vs. statutory requirements
4. **Flag**: Any statutory overrides or prohibited lease clauses

**Key Statutory Provisions to Extract**:
- Minimum cure periods (if any)
- Notice requirements (delivery method, format)
- Prohibited remedies (e.g., forcible re-entry, lockout without court order)
- Tenant protections (e.g., relief from forfeiture in Ontario CTA s. 20)
- Mitigation requirements (landlord's duty to re-lease)

### Step 6: Interpret Results and Provide Strategic Guidance

After calculator runs, analyze results:

#### 1. **Assess Damage Magnitude**

**High Exposure** (Net damages >$1M):
- Serious financial risk
- Consider tenant's ability to pay
- May need to accelerate collection efforts
- Weigh litigation costs vs. settlement

**Moderate Exposure** ($250K-$1M):
- Significant but manageable
- Negotiate cure or payment plan
- Security deposit may cover substantial portion

**Low Exposure** (<$250K):
- Security deposit may cover most/all
- Consider cure period and tenant relationship
- May be resolved without litigation

#### 2. **Evaluate Tenant's Financial Position**

**Solvent Tenant**:
- High likelihood of cure if given opportunity
- Consider extending cure period for good tenants
- May negotiate payment plan

**Distressed Tenant**:
- Low likelihood of cure
- Accelerate enforcement
- Draw on security immediately
- Prepare for termination and re-leasing

**Insolvent Tenant** (bankruptcy risk):
- Expected recovery: Use bankruptcy scenario from calculator
- Typical: 7-15% of gross damages in bankruptcy
- **Action**: Accelerate enforcement BEFORE bankruptcy filing
- Consider: Payments within 90 days may be clawed back as preferential transfers

#### 3. **Recommended Remedy Path**

**Step 1: Issue Default Notice** (ALWAYS REQUIRED)
- Formal notice per lease requirements
- State cure deadline clearly
- Include damage calculation (shows seriousness)
- Deliver per lease (registered mail, courier, personal delivery)

**Step 2: Monitor Cure Period**
- Track cure deadline strictly
- Document all communications
- If partial payment: Accept "without prejudice" to preserve rights

**Step 3: If Not Cured (Choose Strategy)**:

**Option A: Terminate & Sue for Damages**
- **When**: Tenant unlikely to cure, poor relationship, want them out
- **Process**: Terminate lease, re-enter, sue for net damages
- **Duty**: MUST mitigate by re-leasing premises
- **Timeline**: 30-90 days to sue, 6-24 months to judgment

**Option B: Continue Lease & Sue for Specific Default**
- **When**: Tenant generally good, isolated default, want to preserve tenancy
- **Process**: Sue for specific amounts owing, keep lease alive
- **Advantage**: Preserve ongoing rent stream
- **Risk**: Further defaults may occur

**Option C: Negotiate Settlement**
- **When**: Tenant distressed but not insolvent, want quick resolution
- **Process**: Payment plan, rent reduction, early termination with negotiated damages
- **Advantage**: Avoid litigation, faster resolution
- **Consideration**: Discount net damages by 20-40% for settlement

#### 4. **Bankruptcy Considerations**

**If Tenant Files Bankruptcy**:
- Calculator shows expected recovery (typically 7-15% of gross damages)
- **Priority Claim**: 60 days rent (typically 100% recovery)
- **Unsecured Claim**: Capped by §502(b)(6) (US) or uncapped (Canada) but low recovery %
- **Preference Risk**: Payments in last 90 days may be clawed back

**Pre-Bankruptcy Strategy**:
- Act quickly while tenant is solvent
- Draw on security deposit immediately
- DO NOT accept payments if bankruptcy imminent (preference risk)
- Consider: Personal guarantees, landlord's liens

### Step 7: Generate Executive Summary

Create concise summary for landlord:

```markdown
## EXECUTIVE SUMMARY: DEFAULT DAMAGE ANALYSIS

**Tenant**: [Name]
**Property**: [Address]
**Default Date**: [Date]
**Default Type**: [Monetary/Non-Monetary/Insolvency]

### Financial Exposure

- **Gross Damages**: $X,XXX,XXX
- **Mitigation Credits**: $(XXX,XXX)
- **Net Damages**: $X,XXX,XXX
- **Security Available**: $XX,XXX
- **Net Exposure**: $X,XXX,XXX

### Bankruptcy Risk Analysis

**If Tenant Files Bankruptcy**:
- Expected Recovery: $XXX,XXX (X% of gross)
- Expected Loss: $X,XXX,XXX
- Recovery Rate: X%

**Recommendation**: [Accelerate enforcement / Monitor situation / Negotiate settlement]

### Recommended Action Plan

**Immediate** (Next 5-10 days):
1. Issue formal default notice (cure deadline: [Date])
2. Draw on security deposit: $XX,XXX
3. Document all evidence of default
4. Prepare termination notice (if cure not received)

**If Not Cured** (After cure deadline):
1. [Terminate lease and re-enter / Continue lease and sue / Negotiate settlement]
2. [Commence legal action for damages]
3. [Begin re-leasing marketing]

**Timeline**:
- Notice delivered: [Date]
- Cure deadline: [Date]
- Termination (if needed): [Date]
- Legal action (if needed): [Date]

### Risk Assessment

**Collection Risk**: [High/Moderate/Low]
**Litigation Risk**: [High/Moderate/Low]
**Re-leasing Risk**: [High/Moderate/Low]

**Overall Recommendation**: [Action-oriented guidance]
```

## Output Files

All files use timestamp prefix `YYYY-MM-DD_HHMMSS` in **Eastern Time (ET)**:

1. **Input JSON**: `Default_Calculator/default_inputs/YYYY-MM-DD_HHMMSS_[tenant]_default.json`
2. **Results JSON**: `Default_Calculator/default_inputs/YYYY-MM-DD_HHMMSS_[tenant]_default_results.json`
3. **Default Notice**: `Reports/YYYY-MM-DD_HHMMSS_default_notice_[tenant].md`

## Damage Calculation Methodology

See `Default_Calculator/METHODOLOGY.md` for complete mathematical framework:

### Accelerated Rent NPV
```
NPV = Σ(t=1 to T) [PMT / (1 + r)^t]

Where:
- PMT = Monthly rent + additional rent
- r = Monthly discount rate
- T = Remaining months
```

### Re-leasing Costs
```
TI Cost = Rentable SF × TI Allowance $/SF
Commission = (Annual Rent × Term Years) × Commission %
Total = TI + Commission + Legal Fees
```

### Mitigation Credit
```
Credit NPV = PV(New Lease Rent, from downtime end to old lease expiry)
```

Landlord has **duty to mitigate** - must make reasonable efforts to re-lease.

### Bankruptcy Cap (§502(b)(6) - United States)
```
Statutory Cap = MAX(1 year rent, 15% × MIN(remaining rent, 3 years rent))

Priority Claim = 60 days rent (100% recovery typically)
Unsecured Claim = MIN(Gross Damages - Priority, Statutory Cap)
Expected Recovery = (Priority × 100%) + (Unsecured × 10-30%)
```

### Canada: No Statutory Cap
- No §502(b)(6) equivalent
- Unsecured claim = full damages (but low recovery %)
- 3-month accelerated rent under BIA s. 65.2
- Typical recovery: 5-20% in CCAA proceedings

## Legal Framework Citations

**Ontario**:
- *Commercial Tenancies Act*, R.S.O. 1990, c. L.7, s. 19 (distress)
- *Commercial Tenancies Act*, s. 20 (relief from forfeiture)
- Common law mitigation duty (*Highway Properties Ltd. v. Kelly, Douglas & Co.*)

**United States**:
- 11 U.S.C. §502(b)(6) (bankruptcy claim cap)
- 11 U.S.C. §365 (executory contract rejection)
- 11 U.S.C. §547 (preference period - 90 days)

## Important Guidelines

1. **Accuracy Critical**: Damages must be calculated precisely for court/negotiation
2. **Mitigation Required**: Landlord MUST attempt to re-lease to minimize damages
3. **Statutory Compliance**: Follow jurisdiction-specific notice requirements
4. **Document Everything**: Evidence of default, notice delivery, mitigation efforts
5. **Act Quickly**: Delay may waive rights or allow bankruptcy filing
6. **Consider Collectability**: Judgment is worthless if tenant insolvent
7. **Professional Review**: Complex defaults should be reviewed by legal counsel

## Example Usage

```
User: "Tenant ABC Corp has not paid rent for 3 months ($75,000 in arrears) at our Mississauga industrial property. Lease expires in 2028."

ARGUMENTS: /path/to/lease_abstract.md "Non-payment of rent: $75,000 arrears (3 months)"
```

This will:
1. Extract lease terms from abstract (rent, expiry, area, etc.)
2. Create damage calculation JSON with default details
3. Run Python calculator to quantify damages (accelerated rent, re-leasing costs, NPV)
4. Generate formal default notice with itemized damage breakdown
5. Provide strategic guidance on remedy selection and bankruptcy risk
6. Create executive summary with recommended action plan

Begin the analysis now with the provided lease and default situation.
