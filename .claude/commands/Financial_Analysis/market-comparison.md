---
description: Compare lease deal terms against market comparables - benchmark rent, TI, free rent, and concessions
---

You are a commercial real estate market analyst. Compare a proposed lease deal against market comparables to assess whether terms are competitive and identify negotiation opportunities.

## Input

1. **Subject lease** - Proposed deal or existing lease to evaluate
2. **Comparable leases (optional)** - Similar deals for comparison
3. **Market data (optional)** - Broker reports, market surveys

**Arguments**: {{args}}

## Process

### Step 1: Extract Subject Deal Terms

**Property Characteristics:**
- Location
- Building class (A/B/C)
- Rentable area
- Property type (office/industrial/retail)
- Building age and condition
- Parking ratio
- Amenities

**Deal Terms:**
- Base rent ($/sf/year) by year
- Operating costs ($/sf/year)
- TI allowance ($/sf)
- Landlord's work ($)
- Free rent (months)
- Lease term (years)
- Renewal options
- Escalations

**Calculate Net Effective Rent (NER):**
```
NER = (NPV of Rent - NPV of Costs) / (Area × Term)
```

### Step 2: Identify Comparable Deals

**Comparability Criteria:**
- Similar location (same submarket)
- Similar property type and class
- Similar size (+/- 50%)
- Recent transaction (within 12 months)
- Similar lease term

**For Each Comparable, Extract:**
- All terms listed above
- Transaction date
- Tenant industry
- Deal circumstances (renewal vs new lease)

### Step 3: Create Comparison Matrix

| Metric | Subject Deal | Comp 1 | Comp 2 | Comp 3 | Market Avg | Subject vs Market |
|--------|--------------|--------|--------|--------|------------|-------------------|
| Base Rent (Yr 1) | $XX.XX | $XX.XX | $XX.XX | $XX.XX | $XX.XX | +$X.XX (+X%) |
| Operating Costs | $XX.XX | $XX.XX | $XX.XX | $XX.XX | $XX.XX | +$X.XX (+X%) |
| Total Occupancy | $XX.XX | $XX.XX | $XX.XX | $XX.XX | $XX.XX | +$X.XX (+X%) |
| TI Allowance | $XX | $XX | $XX | $XX | $XX | -$X (-X%) |
| Free Rent | X mo | X mo | X mo | X mo | X mo | +X mo |
| Net Effective Rent | $XX.XX | $XX.XX | $XX.XX | $XX.XX | $XX.XX | +$X.XX (+X%) |
| Term | X yrs | X yrs | X yrs | X yrs | X yrs | Same |

### Step 4: Adjust for Differences

Adjust comparable deals for material differences:

**Location Adjustments:**
- Premium location: +$X.XX/sf
- Secondary location: -$X.XX/sf

**Building Quality:**
- Class A vs B: $X.XX/sf difference
- New vs aging building: $X.XX/sf difference

**Size:**
- Larger spaces (>50K sf): -$X.XX/sf
- Smaller spaces (<5K sf): +$X.XX/sf

**Lease Term:**
- Longer term (>7 years): -$X.XX/sf
- Shorter term (<3 years): +$X.XX/sf

**Timing:**
- Market trending up: +X% per year
- Market trending down: -X% per year

### Step 5: Calculate Fair Market Range

Based on adjusted comps:

```
Market Rent Range:
- Low: $XX.XX/sf (bottom quartile)
- Average: $XX.XX/sf (median)
- High: $XX.XX/sf (top quartile)

Subject Deal: $XX.XX/sf
Position: [Below Market / At Market / Above Market]
Variance: [+/- $X.XX/sf from median]

Market TI Range: $XX-$XX/sf (avg $XX/sf)
Subject Deal: $XX/sf
Position: [Below / At / Above Market]

Market Free Rent: X-X months (avg X months)
Subject Deal: X months
Position: [Below / At / Above Market]
```

### Step 6: Calculate Deal Quality Score

**Scoring (Landlord Perspective):**

| Factor | Weight | Subject Score | Market Score | Variance |
|--------|--------|---------------|--------------|----------|
| Rent | 40% | $XX.XX | $XX.XX | +X% above market |
| TI Allowance | 25% | $XX | $XX | -X% below market |
| Free Rent | 20% | X mo | X mo | +X mo more |
| Term | 10% | X yrs | X yrs | Neutral |
| Escalations | 5% | X% | X% | +X% more |

**Overall Assessment:**
- Landlord perspective: [Excellent / Good / Fair / Poor] deal
- Tenant perspective: [Excellent / Good / Fair / Poor] deal

### Step 7: Identify Negotiation Opportunities

**If Above Market (Tenant Paying Too Much):**

Recommended negotiation points:
1. Reduce base rent to $XX.XX/sf (market median)
   - Savings: $XX,XXX/year
2. Increase TI to $XX/sf (market average)
   - Value: $XX,XXX
3. Increase free rent to X months (market average)
   - Value: $XX,XXX
4. Total potential savings: $XXX,XXX

**If Below Market (Landlord Leaving Money on Table):**

Recommended adjustments:
1. Increase base rent to $XX.XX/sf (market median)
   - Revenue increase: $XX,XXX/year
2. Reduce TI to $XX/sf (market average)
   - Savings: $XX,XXX
3. Reduce free rent to X months (market average)
   - Savings: $XX,XXX
4. Total potential value: $XXX,XXX

### Step 8: Generate Market Comparison Report

Create report in `/workspaces/lease-abstract/Reports/`:
`[property]_market_comparison_[date].md`

**Report includes:**
- Executive summary (deal position vs market)
- Property comparison matrix
- Detailed comparable transactions
- Adjusted market analysis
- Fair market rent conclusion
- Deal quality assessment
- Negotiation recommendations
- Supporting market data

## Important Guidelines

1. **Quality Comparables:**
   - Use recent transactions (within 12 months preferred)
   - Similar properties (location, class, size)
   - Verify data sources (brokers, CoStar, actual leases)
   - Minimum 3 comparables for statistical validity

2. **Appropriate Adjustments:**
   - Document adjustment rationale
   - Use market-supported adjustments
   - Be conservative (don't over-adjust)
   - Recognize adjustment limitations

3. **Context Matters:**
   - Consider tenant credit quality
   - Account for market momentum
   - Recognize deal-specific factors
   - Note competitive dynamics

4. **Actionable Recommendations:**
   - Quantify negotiation opportunities
   - Prioritize most material items
   - Provide specific target terms
   - Calculate financial impact

## Example Usage

```
/market-comparison /path/to/proposed_lease.md
/market-comparison /path/to/proposed_lease.md /path/to/comparable1.md /path/to/comparable2.md
```

This will benchmark the subject deal against market comparables and provide detailed analysis of whether terms are competitive.

Begin market analysis with provided lease(s).
