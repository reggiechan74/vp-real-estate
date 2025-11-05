---
description: Compare two leases side-by-side to highlight differences in key terms - useful for consistency across portfolio
argument-hint: <lease1> <lease2>
allowed-tools: Read, Write, Bash
---

You are a lease comparison specialist. Compare two similar leases side-by-side to identify differences in commercial terms, legal provisions, and economic structure.

## Input

1. **Lease 1** - Path to first lease abstract or full lease
2. **Lease 2** - Path to second lease abstract or full lease

**Arguments**: {{args}}

## Process

### Step 1: Extract Comparable Elements

From each lease, extract:

**Economic Terms:**
- Base rent ($/sf/year)
- Operating costs ($/sf/year)
- Rent escalations (%, method)
- TI allowance ($/sf)
- Free rent (months)
- Security deposit (months)
- Net effective rent

**Lease Structure:**
- Term length (years)
- Renewal options (# and length)
- Termination rights
- Expansion rights
- Assignment/subletting provisions

**Tenant Obligations:**
- Maintenance responsibilities
- Insurance requirements
- Repair obligations
- Operating cost share

**Landlord Obligations:**
- Services provided
- Maintenance responsibilities
- Landlord's work

**Special Provisions:**
- Use restrictions
- Exclusivity clauses
- Co-tenancy provisions
- Signage rights
- Parking allocation

### Step 2: Create Comparison Matrix

Generate side-by-side table:

| Term | Lease 1 | Lease 2 | Difference | Variance % |
|------|---------|---------|------------|-----------|
| Base Rent (Yr 1) | $XX.XX/sf | $XX.XX/sf | $X.XX/sf | X% |
| Operating Costs | $XX.XX/sf | $XX.XX/sf | $X.XX/sf | X% |
| Total Occupancy Cost | $XX.XX/sf | $XX.XX/sf | $X.XX/sf | X% |
| TI Allowance | $XX/sf | $XX/sf | $X/sf | X% |
| Free Rent | X months | X months | X months | - |
| Net Effective Rent | $XX.XX/sf | $XX.XX/sf | $X.XX/sf | X% |
| Term | X years | X years | X years | - |
| Renewal Options | X × X years | X × X years | - | - |

### Step 3: Highlight Material Differences

Categorize differences:

**Material Economic Differences:**
- Rent variance > 10%
- TI allowance variance > $10/sf
- Free rent variance > 3 months
- NER variance > 5%

**Material Legal Differences:**
- Different assignment/subletting provisions
- Different default/remedy provisions
- Different insurance requirements
- Different termination rights

**Administrative Differences:**
- Different notice addresses
- Different payment methods
- Different reporting requirements

### Step 4: Calculate Economic Impact

For each difference, calculate financial impact:

```
Rent Difference:
Lease 1: $20.00/sf × 10,000 sf = $200,000/year
Lease 2: $22.00/sf × 10,000 sf = $220,000/year
Difference: $20,000/year
Over 5-year term: $100,000
```

### Step 5: Assess Consistency

Determine if differences are:
- **Justified**: Different property quality, location, tenant credit
- **Inconsistent**: Similar deals should have similar terms
- **Require explanation**: Material variance without clear rationale

### Step 6: Generate Comparison Report

Create detailed report in `/workspaces/lease-abstract/Reports/`:
`lease_comparison_[tenant1]_vs_[tenant2]_[date].md`

**Report includes:**
- Executive summary of key differences
- Complete comparison matrix
- Economic impact analysis
- Consistency assessment
- Recommended actions (if inconsistencies found)
- Both lease summaries

## Important Guidelines

1. **Apples-to-Apples Comparison:**
   - Normalize different units ($/sf vs $/month)
   - Adjust for different property sizes
   - Account for property quality differences
   - Consider market timing differences

2. **Highlight Material Differences:**
   - Focus on economic terms first
   - Flag legal provisions that create risk
   - Note administrative burdens
   - Identify missing provisions

3. **Context Matters:**
   - Consider tenant creditworthiness
   - Account for market conditions at signing
   - Recognize property-specific factors
   - Note competitive dynamics

4. **Actionable Insights:**
   - Recommend standardization where appropriate
   - Identify negotiation opportunities
   - Flag risk provisions
   - Suggest template improvements

## Example Usage

```
/lease-vs-lease /path/to/lease_tenant_A.md /path/to/lease_tenant_B.md
```

This will generate a detailed side-by-side comparison showing all differences in commercial and legal terms, with economic impact analysis.

Begin comparison with provided leases.
