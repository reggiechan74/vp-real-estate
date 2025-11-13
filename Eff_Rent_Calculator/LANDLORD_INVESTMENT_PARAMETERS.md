# Landlord Investment Parameters Database

## Overview

The landlord investment parameters database provides a centralized repository of investment assumptions for different landlord entities. This allows the effective rent calculator to automatically look up the correct breakeven thresholds based on the landlord identified in a lease or offer to lease.

## Purpose

Different landlord entities have different capital structures, cost of capital, and investment criteria:

- **REITs** typically use moderate leverage (50-60% LTV) and target 6-7% dividend yields
- **Private Equity** may use higher leverage (60-70% LTV) and demand higher equity returns (8-10%)
- **Institutional** investors (pension funds) often use lower leverage (40-50% LTV) and accept lower returns
- **Private Owners** vary widely based on financing availability and return requirements

By maintaining a database of landlord-specific parameters, we ensure breakeven analysis accurately reflects each landlord's actual cost of capital.

## Files

| File | Purpose |
|------|---------|
| `landlord_investment_parameters_schema.json` | JSON Schema defining the structure and validation rules |
| `landlord_investment_parameters.json` | Database of landlord entities and their investment parameters |
| `LANDLORD_INVESTMENT_PARAMETERS.md` | This documentation file |

## Database Structure

### Top Level

```json
{
  "version": "1.0.0",
  "last_updated": "2025-11-13",
  "notes": "Optional notes about the database",
  "landlords": [ /* array of landlord entities */ ]
}
```

### Landlord Entity

Each landlord entity includes:

```json
{
  "landlord_legal_name": "ABC Industrial Properties Inc.",
  "landlord_aliases": ["ABC Industrial", "ABC IP Inc."],
  "landlord_type": "REIT",
  "primary_asset_class": "Industrial",
  "active": true,
  "notes": "Optional notes",
  "investment_parameters": { /* default parameters */ },
  "properties": [ /* optional property-specific overrides */ ]
}
```

### Investment Parameters

Standard parameters for breakeven analysis:

```json
{
  "default_acquisition_cost_psf": 150.0,
  "going_in_ltv": 0.55,
  "mortgage_amortization_months": 300,
  "dividend_yield": 0.0675,
  "interest_cost": 0.04,
  "principal_payment_rate": 0.026713,
  "building_allocation_pct": 0.40,
  "default_remaining_depreciation_years": 20,
  "nominal_discount_rate": 0.10,
  "notes": "Optional notes about these parameters"
}
```

### Property-Specific Parameters

For properties with known acquisition costs:

```json
{
  "property_address": "2500 Logistics Way, City A, ST 1C1 1C1",
  "property_name": "Logistics Way Distribution Center",
  "acquisition_cost": 60000000.0,
  "acquisition_cost_psf": 150.0,
  "acquisition_date": "2023-06-15",
  "gla_sf": 400000.0,
  "year_built": 2018,
  "property_specific_parameters": {
    "going_in_ltv": 0.55,
    "interest_cost": 0.04,
    "remaining_depreciation_years": 32
  },
  "notes": "Property-specific notes"
}
```

## How It Works

### Automatic Matching Process

When processing a lease or offer to lease:

1. **Extract landlord name** from the "PARTIES" or "LANDLORD" section of the lease document

2. **Search database** for exact match on `landlord_legal_name`

3. **Check aliases** if no exact match found (fuzzy matching on `landlord_aliases`)

4. **Extract property address** from lease document

5. **Check property-specific parameters** if property address matches a known property

6. **Apply parameters** to the deal JSON:
   - Use property-specific parameters if available
   - Otherwise use landlord default parameters
   - If no match found, use system defaults or require manual input

### Matching Priority

Parameters are applied in this order (highest priority first):

1. **Property-specific overrides** (if property address matches)
2. **Landlord default parameters** (if landlord name matches)
3. **System defaults** (if no match found)

### Example Matching

**Lease Document:**
```
LANDLORD: ABC Industrial Properties Inc.
Property Address: 2500 Logistics Way, City A, ST 1C1 1C1
```

**Matching Logic:**
1. Find landlord: "ABC Industrial Properties Inc." → MATCH
2. Find property: "2500 Logistics Way, City A, ST 1C1 1C1" → MATCH
3. Use property-specific parameters:
   - `acquisition_cost`: $60,000,000
   - `acquisition_cost_psf`: $150/sf
   - `going_in_ltv`: 0.55
   - `interest_cost`: 0.04
   - `remaining_depreciation_years`: 32 (building is 7 years old)

## Parameter Definitions

### Financial Parameters

| Parameter | Description | Typical Range | Example |
|-----------|-------------|---------------|---------|
| `default_acquisition_cost_psf` | Default property value ($/sf) if unknown | $100-$500/sf | 150.0 |
| `going_in_ltv` | Loan-to-value ratio | 40-70% | 0.55 (55%) |
| `mortgage_amortization_months` | Amortization period | 20-30 years | 300 (25 years) |
| `dividend_yield` | Required equity return | 6-10% | 0.0675 (6.75%) |
| `interest_cost` | Mortgage interest rate | 3-6% | 0.04 (4%) |
| `principal_payment_rate` | Principal payment rate | Calculated | 0.026713 |
| `building_allocation_pct` | Building % of property value | 35-45% | 0.40 (40%) |
| `default_remaining_depreciation_years` | Building depreciation period | 15-30 years | 20 |
| `nominal_discount_rate` | NPV discount rate | 8-12% | 0.10 (10%) |

### Landlord Types

| Type | Description | Typical Characteristics |
|------|-------------|------------------------|
| `REIT` | Real Estate Investment Trust | Moderate leverage (50-60% LTV), 6-7% dividend yield |
| `Private Equity` | PE fund or private investor | Higher leverage (60-70% LTV), 8-10% returns |
| `Institutional` | Pension fund, insurance company | Lower leverage (40-50% LTV), 5-6% returns |
| `Private Owner` | Individual or family office | Variable, often higher leverage and returns |
| `Fund` | Commingled fund | Depends on fund structure |
| `Pension Fund` | Direct pension investment | Very conservative, low leverage |
| `Government` | Government entity | Minimal/no leverage, low returns |
| `Other` | Other entity type | Variable |

### Asset Classes

| Asset Class | Typical Characteristics |
|-------------|------------------------|
| `Industrial` | Lower leverage, 9-11% discount rates |
| `Office` | Moderate leverage, 8-10% discount rates |
| `Retail` | Higher risk, 10-12% discount rates |
| `Multi-Family` | High leverage (70-80% LTV), 7-9% discount |
| `Mixed-Use` | Blended characteristics |
| `Other` | Variable |

## Maintaining the Database

### Adding a New Landlord

1. **Gather information:**
   - Legal entity name (exact match from lease documents)
   - Alternative names/aliases
   - Landlord type (REIT, Private Equity, etc.)
   - Primary asset class

2. **Determine investment parameters:**
   - If REIT: Review public filings for leverage ratios, cost of debt, dividend yield
   - If Private: Estimate based on financing terms and return requirements
   - If Institutional: Conservative assumptions (lower leverage, lower returns)

3. **Add to database:**
   ```json
   {
     "landlord_legal_name": "New Landlord Legal Name Inc.",
     "landlord_aliases": ["Short Name", "DBA Name"],
     "landlord_type": "REIT",
     "primary_asset_class": "Industrial",
     "active": true,
     "notes": "Source of parameters and date",
     "investment_parameters": {
       "default_acquisition_cost_psf": 150.0,
       "going_in_ltv": 0.55,
       "mortgage_amortization_months": 300,
       "dividend_yield": 0.0675,
       "interest_cost": 0.04,
       "principal_payment_rate": 0.026713,
       "building_allocation_pct": 0.40,
       "default_remaining_depreciation_years": 20,
       "nominal_discount_rate": 0.10,
       "notes": "Updated Q4 2025 based on public filings"
     },
     "properties": []
   }
   ```

4. **Validate:**
   ```bash
   # Validate JSON syntax
   cat landlord_investment_parameters.json | jq .

   # Validate against schema (if JSON schema validator installed)
   jsonschema -i landlord_investment_parameters.json landlord_investment_parameters_schema.json
   ```

### Adding a Property to Existing Landlord

When a landlord acquires a new property with known parameters:

```json
{
  "property_address": "1000 Main Street, City B, ST 2B2 2B2",
  "property_name": "Main Street Industrial Park",
  "acquisition_cost": 50000000.0,
  "acquisition_cost_psf": 125.0,
  "acquisition_date": "2025-08-15",
  "gla_sf": 400000.0,
  "year_built": 2015,
  "property_specific_parameters": {
    "going_in_ltv": 0.60,
    "interest_cost": 0.045,
    "remaining_depreciation_years": 25
  },
  "notes": "Acquired August 2025 at 60% LTV due to favorable financing"
}
```

### Updating Parameters

Investment parameters should be reviewed and updated:

- **Quarterly:** For active landlords with changing capital structures
- **Annually:** For stable landlords
- **As Needed:** When landlord refinances, changes strategy, or reports new cost of capital

**Update checklist:**
1. Review landlord's latest financial statements or public filings
2. Check current debt costs (interest rates may change significantly)
3. Verify dividend/distribution yield
4. Update `last_updated` date at top of database
5. Add notes explaining what changed and why

### Deactivating a Landlord

If a landlord entity merges, sells, or dissolves:

```json
{
  "landlord_legal_name": "Former Landlord Inc.",
  "active": false,
  "notes": "Merged with XYZ REIT effective 2025-06-30. Use XYZ REIT parameters for new deals."
}
```

## Integration with Effective Rent Calculator

### Manual Integration (Current)

When creating a deal JSON file, reference the landlord database:

1. Open `landlord_investment_parameters.json`
2. Find the landlord by name
3. Copy investment parameters to your deal JSON:

```json
{
  "deal_name": "My Deal",
  "property_info": { ... },
  "tenant_info": { ... },
  "lease_terms": { ... },
  "investment_parameters": {
    "acquisition_cost": 60000000.0,
    "going_in_ltv": 0.55,
    "mortgage_amortization_months": 300,
    "dividend_yield": 0.0675,
    "interest_cost": 0.04,
    "principal_payment_rate": 0.026713
  }
}
```

### Automated Integration (Future Enhancement)

The effective rent calculator could be enhanced to:

1. Accept a `landlord_name` field in the deal JSON
2. Automatically load `landlord_investment_parameters.json`
3. Search for matching landlord
4. Auto-populate investment parameters
5. Fall back to manual parameters if no match found

**Example future usage:**
```json
{
  "deal_name": "Tech Distribution - 2500 Logistics Way",
  "landlord_name": "ABC Industrial Properties Inc.",
  "property_address": "2500 Logistics Way, City A, ST 1C1 1C1",
  "property_info": { ... },
  "investment_parameters": "auto"
}
```

The calculator would:
- Find "ABC Industrial Properties Inc." in database
- Find property "2500 Logistics Way"
- Use property-specific acquisition cost ($60M)
- Use property-specific parameters where available
- Use landlord defaults for remaining parameters

## Examples

### Example 1: REIT with Known Property

**Scenario:** Analyzing a lease at a property owned by ABC Industrial Properties Inc., which we acquired in 2023 for $60M.

**Database Entry:**
```json
{
  "landlord_legal_name": "ABC Industrial Properties Inc.",
  "investment_parameters": {
    "default_acquisition_cost_psf": 150.0,
    "going_in_ltv": 0.55,
    "dividend_yield": 0.0675,
    "interest_cost": 0.04,
    "nominal_discount_rate": 0.10
  },
  "properties": [
    {
      "property_address": "2500 Logistics Way, City A, ST 1C1 1C1",
      "acquisition_cost": 60000000.0,
      "acquisition_cost_psf": 150.0,
      "gla_sf": 400000.0,
      "year_built": 2018
    }
  ]
}
```

**Result:** Calculator uses actual acquisition cost ($60M) and landlord's standard parameters (55% LTV, 6.75% dividend yield, 4% interest).

### Example 2: Private Owner with No Property Data

**Scenario:** Analyzing a lease for a private landlord where we don't know the acquisition cost.

**Database Entry:**
```json
{
  "landlord_legal_name": "Pacific Private Holdings Ltd.",
  "investment_parameters": {
    "default_acquisition_cost_psf": 120.0,
    "going_in_ltv": 0.65,
    "dividend_yield": 0.08,
    "interest_cost": 0.05,
    "nominal_discount_rate": 0.11
  },
  "properties": []
}
```

**Result:** Calculator uses default acquisition cost ($120/sf × property area) and private owner's higher return requirements (8% dividend, 11% discount rate).

### Example 3: Unknown Landlord

**Scenario:** Analyzing a lease for a landlord not in the database.

**Approach:**
1. Add landlord to database with estimated parameters
2. Or use system defaults temporarily
3. Flag deal for parameter review before final approval

## Best Practices

### 1. Naming Conventions

**Use exact legal names:**
- ✓ "ABC Industrial Properties Inc."
- ✗ "ABC Industrial"
- ✗ "abc industrial properties"

**Add common variations to aliases:**
```json
"landlord_aliases": [
  "ABC Industrial",
  "ABC IP Inc.",
  "ABC Properties",
  "ABCIP"
]
```

### 2. Parameter Sources

**Document parameter sources in notes:**
```json
"notes": "Parameters from Q3 2025 MD&A. LTV 55% per debt covenants. Dividend yield 6.75% (trailing 12 months). Interest rate 4.0% per 2024 mortgage refinancing."
```

### 3. Regular Updates

**Set calendar reminders:**
- Quarterly: Review REIT parameters (public filings)
- Semi-annually: Review private equity parameters
- Annually: Review all parameters

### 4. Validation

**Before using parameters:**
- Verify they're current (check `last_updated` date)
- Ensure they match property type (industrial vs office)
- Confirm they reflect current market conditions (interest rates change!)

### 5. Overrides

**When to use property-specific overrides:**
- Property acquired recently (use actual cost)
- Property has unique financing (different LTV or rate)
- Property in different market (different cap rate/discount rate)

**When NOT to override:**
- Small variations from landlord average
- Temporary market fluctuations
- Lack of reliable data (use landlord defaults)

## Troubleshooting

### Problem: Landlord not found

**Solutions:**
1. Check spelling of landlord name in lease document
2. Check landlord aliases in database
3. Add landlord to database if truly new
4. Use closest comparable landlord as template

### Problem: Parameters seem outdated

**Solutions:**
1. Check `last_updated` date
2. Review landlord's recent financial filings
3. Update parameters and document source
4. Flag old parameters for quarterly review

### Problem: Multiple landlords (joint venture)

**Solutions:**
1. Create separate entry for JV entity
2. Use weighted average of partner parameters
3. Default to more conservative (lower leverage) partner

### Problem: Property address doesn't match

**Solutions:**
1. Check for typos or formatting differences
2. Standardize address format in database
3. Add property with corrected address
4. Use landlord defaults if property truly unknown

## Future Enhancements

Potential improvements to landlord investment parameters system:

1. **Auto-matching algorithm** in calculator
2. **Fuzzy search** on landlord names (handle typos, variations)
3. **Web interface** for maintaining database
4. **Version control** (track parameter changes over time)
5. **Import from financial databases** (auto-update REIT parameters from public filings)
6. **Multi-currency support** (CAD, USD, etc.)
7. **Property-level cap rates** (use actual cap rate instead of discount rate)
8. **Deal-specific overrides** (one-off parameter adjustments with audit trail)

## Reference

### Schema Validation

Validate the database against the schema:

```bash
# Using Python jsonschema
pip install jsonschema
python -m jsonschema -i landlord_investment_parameters.json landlord_investment_parameters_schema.json

# Using Node.js ajv-cli
npm install -g ajv-cli
ajv validate -s landlord_investment_parameters_schema.json -d landlord_investment_parameters.json
```

### Sample Queries

**Find all REITs:**
```bash
cat landlord_investment_parameters.json | jq '.landlords[] | select(.landlord_type=="REIT") | .landlord_legal_name'
```

**Find landlords with high leverage (>60% LTV):**
```bash
cat landlord_investment_parameters.json | jq '.landlords[] | select(.investment_parameters.going_in_ltv > 0.60) | {name: .landlord_legal_name, ltv: .investment_parameters.going_in_ltv}'
```

**List all properties in database:**
```bash
cat landlord_investment_parameters.json | jq '.landlords[].properties[] | {landlord: .property_name, address: .property_address, cost_psf: .acquisition_cost_psf}'
```

---

**Last Updated:** November 13, 2025
**Version:** 1.0.0
**Maintained By:** Lease Analysis Team
