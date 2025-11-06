---
description: Analyze lease expiry timeline across portfolio - visualize expiry cliff risk, identify renewal priorities, forecast vacancy
argument-hint: <portfolio-data-path>
allowed-tools: Read, Write, Bash
---

# Rollover Analysis: Portfolio Lease Expiration Risk Assessment

**Automated JSON → Python → Report workflow for portfolio rollover risk analysis**

You are executing the **/rollover-analysis** slash command. You are an expert in **Portfolio Lease Administration** and **Rollover Risk Analysis**, specializing in lease expiration concentration risk and renewal priority scoring.

## Objective

Analyze lease expiration dates across a real estate portfolio to identify:
1. **Concentration risk** - Years with >30% of portfolio expiring (CRITICAL)
2. **Renewal priorities** - Which leases need immediate attention (0-1 normalized scoring)
3. **Scenario modeling** - NOI impact under optimistic/base/pessimistic renewal rates
4. **Strategic recommendations** - Actionable renewal strategy

## Input

**Arguments**: {{args}}

The user will provide:
1. **Portfolio data** - Path to JSON file OR multiple lease abstracts
2. **Format**: JSON (preferred) or Markdown lease abstracts

## Workflow Steps

### Step 1: Extract Portfolio Data

**If JSON provided**: Load directly and proceed to Step 4

**If lease abstracts provided**: Extract from each lease:
- Property address
- Tenant name
- Rentable area (SF)
- Current annual rent (total, not $/SF)
- Lease expiry date (YYYY-MM-DD)
- Renewal options (array of dates)
- Tenant credit rating (AAA to D or NR)
- Below market % (negative if below market)

### Step 2: Create Input JSON

Build JSON file following schema:

```json
{
  "portfolio_name": "Portfolio Name",
  "analysis_date": "YYYY-MM-DD",
  "leases": [
    {
      "property_address": "123 Main St, City, State",
      "tenant_name": "Acme Corp",
      "rentable_area_sf": 50000,
      "current_annual_rent": 750000,
      "lease_expiry_date": "2027-06-30",
      "renewal_options": ["2032-06-30"],
      "tenant_credit_rating": "BBB",
      "below_market_pct": -15.5
    }
  ],
  "assumptions": {
    "discount_rate": 0.10,
    "renewal_rate_optimistic": 0.80,
    "renewal_rate_base": 0.65,
    "renewal_rate_pessimistic": 0.50,
    "downtime_months": {
      "optimistic": 1,
      "base": 3,
      "pessimistic": 6
    },
    "market_rent_sf": 16.50,
    "market_rent_growth_annual": 0.025,
    "ti_allowance_sf": 15.00,
    "leasing_commission_pct": 0.05
  }
}
```

**Save to**: `Rollover_Analysis/rollover_inputs/YYYY-MM-DD_HHMMSS_[portfolio_name].json`

### Step 3: Run Python Calculator

Execute the rollover calculator:

```bash
python3 Rollover_Analysis/rollover_calculator.py \
  Rollover_Analysis/rollover_inputs/YYYY-MM-DD_HHMMSS_[portfolio_name].json

# Output: *_results.json (automatically generated)
```

This generates JSON results with:
- Expiry schedule by year (with risk levels)
- Priority rankings (0-1 normalized scores)
- Scenario analysis (optimistic/base/pessimistic)
- All metrics in machine-readable format

### Step 4: Generate Markdown Report

Execute the report generator:

```bash
python3 Rollover_Analysis/report_generator.py \
  Rollover_Analysis/rollover_inputs/YYYY-MM-DD_HHMMSS_[portfolio_name].json \
  /workspaces/lease-abstract/Reports/YYYY-MM-DD_HHMMSS_rollover_analysis_[portfolio_name].md
```

This generates executive-ready markdown report with:
- Executive summary with portfolio overview
- Expiry schedule table with risk flags (🔴 CRITICAL, 🟠 HIGH, 🟢 MODERATE)
- Top 10 priority leases with component scores
- Scenario analysis with NPV-discounted NOI impact
- Recommended actions (immediate vs strategic)

### Step 5: Interpret Results

After the calculator runs, provide strategic guidance:

#### 1. **Assess Concentration Risk**

**CRITICAL RISK** (🔴): >30% of portfolio (SF or rent) expiring in single year
- **Action**: Urgent intervention required
- **Tactics**: Stagger renewal negotiations, consider early renewals with extensions, diversify lease expiry profile

**HIGH RISK** (🟠): 20-30% expiring in single year
- **Action**: Proactive renewal strategy needed
- **Tactics**: Begin renewals 12-18 months early, prepare for potential vacancy

**MODERATE RISK** (🟢): <20% expiring
- **Action**: Standard renewal processes
- **Tactics**: Monitor, engage tenants 6-12 months before expiry

#### 2. **Identify Priority Leases**

Priority score formula (0-1 normalized):
```
Priority = (Rent% × 0.40) + (Urgency × 0.30) + (Below Market × 0.20) + (Credit Risk × 0.10)
```

**High Priority (Score >0.30)**:
- Large leases (high rent %)
- Expiring soon (high urgency)
- Below market opportunities (high below market %)
- Credit-challenged tenants (high credit risk)

**Action Plan by Priority**:
- **Immediate (12 months)**: Top 3-5 priority leases expiring within 12 months
- **Strategic (12-24 months)**: High-priority leases in 12-24 month window
- **Monitor**: Lower priority leases beyond 24 months

#### 3. **Evaluate Scenario Impact**

**Optimistic** (80% renewal, 1 month downtime):
- Best-case NOI impact
- Use for financial planning baseline

**Base** (65% renewal, 3 months downtime):
- Realistic expectation
- Use for budgeting and forecasting

**Pessimistic** (50% renewal, 6 months downtime):
- Stress test scenario
- Prepare contingency plans

**NPV Discounting**: All scenarios use 10% discount rate (configurable) to reflect time value of money

#### 4. **Strategic Recommendations**

**If CRITICAL year concentration**:
```markdown
## URGENT: CRITICAL CONCENTRATION RISK

**Problem**: 2026 has 35% of portfolio expiring (4 leases, 235K SF)

**Risk**: If renewal rates disappoint, significant vacancy exposure

**Recommended Actions**:
1. **Immediate**: Begin renewal negotiations for all 4 leases NOW (12-18 months early)
2. **Stagger expirations**: Offer early renewals with 2027-2028 expiration dates
3. **Market backfill plan**: Prepare leasing strategy for worst-case vacancies
4. **Financial stress test**: Model 50% renewal rate impact on NOI

**Timeline**:
- Now - 3 months: Engage all 4 tenants, assess renewal likelihood
- 3-6 months: Negotiate renewal terms, consider incentives
- 6-12 months: Execute renewals or begin backfill marketing
```

**If HIGH renewal opportunity** (below-market leases):
```markdown
## OPPORTUNITY: BELOW-MARKET RENT CAPTURE

**Identified**: 3 leases significantly below market (-15% to -18%)

**Opportunity**: $450K annual rent increase potential

**Recommended Approach**:
1. **Market Analysis**: Validate current market rates (obtain 3 comparables)
2. **Renewal Negotiation**: Target rent at market (phased step-ups acceptable)
3. **Value Proposition**: Emphasize renewal benefits (no downtime, no TI costs, continuity)
4. **Walk-Away Price**: Know your minimum acceptable rent before negotiating

**Expected Outcome**: 60-80% of market rent increase achievable
```

### Step 6: Generate Executive Summary

Create concise summary for portfolio manager:

```markdown
## EXECUTIVE SUMMARY: PORTFOLIO ROLLOVER ANALYSIS

**Portfolio**: [Name]
**Analysis Date**: [Date]
**Total Leases**: X

### Rollover Risk Assessment

⚠️ **CRITICAL RISK**: X year(s) with >30% of portfolio expiring
   - [Year]: X% SF, X% rent (X leases)

🔶 **HIGH RISK**: X year(s) with 20-30% expiring
   - [Year]: X% SF, X% rent (X leases)

✓ **MODERATE RISK**: X year(s) with <20% expiring

### Top 3 Priority Leases

1. **[Tenant Name]** - Expires [Date] (Score: 0.XX)
   - [Rent]: $XXX,XXX annual
   - [Reason]: Below-market rent, large tenant, expiring soon
   - **Action**: Renegotiate rent to market

2. **[Tenant Name]** - Expires [Date] (Score: 0.XX)
   ...

### Scenario Analysis

- **Optimistic**: $(XXX,XXX) NOI impact (80% renewal)
- **Base**: $(XXX,XXX) NOI impact (65% renewal)
- **Pessimistic**: $(XXX,XXX) NOI impact (50% renewal)

### Strategic Recommendation

[Action-oriented recommendation based on concentration risk and priorities]

### Next Steps

1. [Immediate action]
2. [Follow-up actions]
3. [Long-term strategy]
```

## Output Files

All files use timestamp prefix `YYYY-MM-DD_HHMMSS` in **Eastern Time (ET)**:

1. **Input JSON**: `Rollover_Analysis/rollover_inputs/YYYY-MM-DD_HHMMSS_[portfolio].json`
2. **Results JSON**: `Rollover_Analysis/rollover_inputs/YYYY-MM-DD_HHMMSS_[portfolio]_results.json`
3. **Markdown Report**: `Reports/YYYY-MM-DD_HHMMSS_rollover_analysis_[portfolio].md`

## Methodology Reference

See `Rollover_Analysis/README.md` for:
- Priority scoring algorithm details
- Credit rating mapping (AAA to D)
- Scenario modeling assumptions
- Risk level criteria
- Best practices

## Example Usage

```
User: "Analyze rollover risk for ABC Industrial Portfolio using these lease abstracts"
[Provides 10 lease abstract files]

ARGUMENTS: ABC Industrial Portfolio /path/to/leases/*.md