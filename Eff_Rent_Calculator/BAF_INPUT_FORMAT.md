# BAF Calculator - JSON Input Format Guide

This document describes the JSON input format for the BAF (Business Approval Form) Calculator.

## Quick Start

```bash
# Run with your input file
python3 baf_calculator.py your_deal.json

# Save results to specific output file
python3 baf_calculator.py your_deal.json -o custom_results.json

# Suppress console output (only save to file)
python3 baf_calculator.py your_deal.json -o results.json --no-print
```

## Input File Structure

The JSON input file contains all parameters needed for lease analysis. All sections are optional and will use default values if not provided.

### Complete Template

```json
{
  "deal_name": "Deal Name (shown in reports)",

  "property_info": {
    "property_type": "industrial",
    "building_name": "Building Name",
    "unit_number": "Unit/Suite Number",
    "area_sf": 10000.0,
    "gla_building_sf": 50000.0
  },

  "tenant_info": {
    "tenant_name": "Tenant Legal Name",
    "trade_name": "DBA/Trade Name",
    "contact": "Contact Person",
    "phone": "Phone Number",
    "email": "Email Address"
  },

  "lease_terms": {
    "lease_start_date": "2024-01-01",
    "lease_term_months": 120,
    "fixturing_term_months": 3,
    "operating_costs_psf": 14.14
  },

  "rent_schedule": {
    "description": "Description of rent structure",
    "rent_psf_by_year": [15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0],
    "months_per_period": [12, 12, 12, 12, 12, 12, 12, 12, 12, 12],
    "notes": "Additional notes"
  },

  "incentives": {
    "tenant_cash_allowance_psf": 30.0,
    "landlord_work_total": 0.0,
    "amortized_tenant_work": 0.0,
    "net_free_rent_months": 3.0,
    "gross_free_rent_months": 0.0,
    "notes": "TI allowance and free rent details"
  },

  "leasing_costs": {
    "listing_agent_commission_psf": 0.0,
    "tenant_rep_commission_psf": 0.0,
    "listing_agent_year1_pct": 0.06,
    "listing_agent_subsequent_pct": 0.025,
    "tenant_rep_year1_pct": 0.06,
    "tenant_rep_subsequent_pct": 0.025,
    "pm_override_fee": 0.0,
    "notes": "Use EITHER office method (psf) OR industrial method (pct), not both"
  },

  "financial_assumptions": {
    "nominal_discount_rate": 0.10,
    "notes": "10% discount rate"
  },

  "investment_parameters": {
    "acquisition_cost": 5000000.0,
    "going_in_ltv": 0.60,
    "mortgage_amortization_months": 300,
    "dividend_yield": 0.0675,
    "interest_cost": 0.0302,
    "principal_payment_rate": 0.026713,
    "notes": "Investment parameters for breakeven analysis"
  }
}
```

## Field Descriptions

### property_info

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `property_type` | string | No | Property type: "industrial" or "office" | "industrial" |
| `building_name` | string | No | Building name | "Industrial Park East" |
| `unit_number` | string | No | Unit/suite identifier | "Suite 1200" |
| `area_sf` | number | Yes | Rentable area in square feet | 10000.0 |
| `gla_building_sf` | number | No | Gross leasable area of building (for breakeven calcs) | 58679.0 |

**Note on property_type:** This field is informational only. The calculator automatically detects which commission method to use based on which commission fields are populated (`_psf` for office, `_pct` for industrial).

### tenant_info

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tenant_name` | string | No | Legal entity name |
| `trade_name` | string | No | DBA or trade name |
| `contact` | string | No | Contact person |
| `phone` | string | No | Phone number |
| `email` | string | No | Email address |

### lease_terms

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `lease_start_date` | string | No | Lease start date (YYYY-MM-DD) | "2024-01-01" |
| `lease_term_months` | integer | Yes | Lease term in months | 120 |
| `fixturing_term_months` | integer | No | Fixturing/free period before rent starts | 3 |
| `operating_costs_psf` | number | Yes | Annual operating costs per sf | 14.14 |

### rent_schedule

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `description` | string | No | Human-readable rent description | "Graduated: $15-20/sf" |
| `rent_psf_by_year` | array | Yes | Annual rent per sf for each year (up to 10 years) | [15.0, 16.0, 17.0, ...] |
| `months_per_period` | array | No | Months for each rent period (defaults to [12]*10) | [12, 12, 12, ...] |
| `notes` | string | No | Additional notes | "Net rent only" |

**Important Notes:**
- `rent_psf_by_year`: Annual net rent per square foot
- Provide up to 10 years
- For flat rent: `[25.0, 25.0, 25.0, ...]`
- For graduated: `[20.0, 20.0, 22.0, 22.0, 24.0, ...]`
- This is **net rent only** (excludes operating costs)

### incentives

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `tenant_cash_allowance_psf` | number | No | TI allowance in $/sf | 30.0 |
| `landlord_work_total` | number | No | Landlord's work (absolute $) | 100000.0 |
| `amortized_tenant_work` | number | No | Amortized tenant work (absolute $) | 0.0 |
| `net_free_rent_months` | number | No | Months of net free rent | 3.0 |
| `gross_free_rent_months` | number | No | Months of gross free rent | 0.0 |
| `notes` | string | No | Incentive details | "$30/sf TI, 3mo free" |

**Important Notes:**
- `tenant_cash_allowance_psf`: Per square foot amount (will be multiplied by area)
- `landlord_work_total`: Absolute dollar amount

**Free Rent Types (Critical Distinction):**

- `net_free_rent_months`: **Net Free Rent** - Tenant pays $0 base rent but DOES pay operating costs
  - Landlord loses: Base rent only
  - Tenant saves: Base rent only
  - Example: 3 months net free means tenant pays $0 rent but still pays OpEx

- `gross_free_rent_months`: **Gross Free Rent** - Tenant pays NOTHING (no base rent, no operating costs)
  - Landlord loses: Base rent + operating costs
  - Tenant saves: Base rent + operating costs
  - Example: 3 months gross free means tenant pays $0 for everything

**Why It Matters:** These affect NER (landlord's return) and GER (tenant's cost) differently. Gross free rent is more valuable to the tenant and more costly to the landlord.

### leasing_costs

**Two Commission Calculation Methods Supported:**

The calculator supports both office and industrial commission structures. Use **ONE method only** - populate either the `_psf` fields OR the `_pct` fields, not both.

#### Method 1: Office Commissions (Flat $/sf per year)

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `listing_agent_commission_psf` | number | No | Listing agent: $/sf × lease years | 2.0 |
| `tenant_rep_commission_psf` | number | No | Tenant rep: $/sf × lease years | 2.0 |

**Example:** 5-year lease, $2/sf per year each side = $10/sf total each = $20/sf combined

**Typical Office Rates:**
- Listing agent: $1.50 - $3.00 /sf/year
- Tenant rep: $1.50 - $3.00 /sf/year
- Total: $3.00 - $6.00 /sf/year

#### Method 2: Industrial Commissions (Percentage of Net Rent)

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `listing_agent_year1_pct` | number | No | Listing: Year 1 % of rent | 0.06 (6%) |
| `listing_agent_subsequent_pct` | number | No | Listing: Years 2+ % of rent | 0.025 (2.5%) |
| `tenant_rep_year1_pct` | number | No | Tenant rep: Year 1 % of rent | 0.06 (6%) |
| `tenant_rep_subsequent_pct` | number | No | Tenant rep: Years 2+ % of rent | 0.025 (2.5%) |

**Example:** 5-year lease at $10/sf base rent:
- Listing agent: (6% × $10) + (2.5% × $10 × 4 years) = $0.60 + $1.00 = $1.60/sf
- Tenant rep: Same = $1.60/sf
- Total: $3.20/sf

**Typical Industrial Rates:**
- Listing agent: 4-6% year 1, 2-3% subsequent
- Tenant rep: 4-6% year 1, 2-3% subsequent

**How It Works:** Each year's commission is calculated as a percentage of that year's actual rent, then discounted to present value.

#### Both Methods

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `pm_override_fee` | number | No | PM override fee (absolute $) | 5000.0 |

### financial_assumptions

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `nominal_discount_rate` | number | Yes | Annual discount rate (decimal) | 0.10 |

**Important Notes:**
- Use decimal format: 0.10 = 10%
- Typical range: 0.08 - 0.12 (8% - 12%)
- Should match your cost of capital / hurdle rate

### investment_parameters

Required for breakeven analysis. Optional if you only want NER/GER.

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `acquisition_cost` | number | No | Property acquisition cost | 6104553.0 |
| `going_in_ltv` | number | No | Loan-to-value ratio (decimal) | 0.60 |
| `mortgage_amortization_months` | integer | No | Mortgage amortization period | 300 |
| `dividend_yield` | number | No | Required dividend yield (decimal) | 0.0675 |
| `interest_cost` | number | No | Interest rate (decimal) | 0.0302 |
| `principal_payment_rate` | number | No | Principal payment rate (decimal) | 0.026713 |

**Important Notes:**
- All rates in decimal format (0.0675 = 6.75%)
- Used to calculate breakeven rent thresholds
- If not provided, breakeven analysis will show zeros

## Example Input Files

### Example 1: Simple Flat Rent

```json
{
  "deal_name": "Simple 5-Year Office Lease",
  "property_info": {
    "area_sf": 5000.0
  },
  "lease_terms": {
    "lease_term_months": 60,
    "operating_costs_psf": 12.0
  },
  "rent_schedule": {
    "rent_psf_by_year": [25.0, 25.0, 25.0, 25.0, 25.0]
  },
  "incentives": {
    "tenant_cash_allowance_psf": 15.0,
    "net_free_rent_months": 2.0
  },
  "leasing_costs": {
    "listing_agent_commission_psf": 3.0,
    "tenant_rep_commission_psf": 3.0
  },
  "financial_assumptions": {
    "nominal_discount_rate": 0.08
  }
}
```

### Example 2: Graduated Rent with Fixturing

```json
{
  "deal_name": "10-Year Industrial with Graduated Rent",
  "property_info": {
    "area_sf": 25000.0,
    "gla_building_sf": 100000.0
  },
  "lease_terms": {
    "lease_start_date": "2024-06-01",
    "lease_term_months": 120,
    "fixturing_term_months": 6,
    "operating_costs_psf": 8.50
  },
  "rent_schedule": {
    "description": "Graduated: $12-14-16/sf over 10 years",
    "rent_psf_by_year": [12.0, 12.0, 12.0, 14.0, 14.0, 14.0, 16.0, 16.0, 16.0, 16.0]
  },
  "incentives": {
    "tenant_cash_allowance_psf": 25.0,
    "net_free_rent_months": 6.0
  },
  "leasing_costs": {
    "listing_agent_commission_psf": 4.0,
    "tenant_rep_commission_psf": 6.0
  },
  "financial_assumptions": {
    "nominal_discount_rate": 0.09
  },
  "investment_parameters": {
    "acquisition_cost": 10000000.0,
    "going_in_ltv": 0.65,
    "mortgage_amortization_months": 300,
    "dividend_yield": 0.07,
    "interest_cost": 0.035,
    "principal_payment_rate": 0.025
  }
}
```

### Example 3: Minimal Input

```json
{
  "property_info": {
    "area_sf": 10000.0
  },
  "lease_terms": {
    "lease_term_months": 120,
    "operating_costs_psf": 10.0
  },
  "rent_schedule": {
    "rent_psf_by_year": [20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0]
  },
  "financial_assumptions": {
    "nominal_discount_rate": 0.10
  }
}
```

## Output File Structure

When you run the calculator, it automatically generates a results JSON file:

```json
{
  "deal_name": "Deal Name",
  "calculation_date": "2025-10-30 12:34:56",
  "inputs": {
    "property": { ... },
    "lease_terms": { ... },
    "rent_schedule_psf": [15.0, 16.0, ...],
    "discount_rate": 0.10
  },
  "results": {
    "npv_analysis": {
      "npv_net_rent_psf": 97.01,
      "npv_costs_psf": -48.60,
      "npv_lease_deal_psf": 48.41
    },
    "effective_rent": {
      "ner_lease_term_only": 7.61,
      "ner_with_fixturing": 6.78,
      "ger_lease_term_only": 21.75,
      "ger_with_fixturing": 20.92
    },
    "metrics": {
      "effective_term_years": 6.36,
      "incentives_pct_year1_gross": 1.1730,
      "breakeven_months": 14.08
    },
    "breakeven_analysis": {
      "unlevered_breakeven": 7.02,
      "io_levered_breakeven": 5.04,
      "fully_levered_breakeven": 6.46,
      "sinking_fund_requirement_psf": 0.82,
      "unlevered_with_caprec": 7.85,
      "fully_levered_with_caprec": 7.28
    },
    "investment_assessment": {
      "proposed_ner": 7.61,
      "meets_unlevered_breakeven": true,
      "meets_io_levered_breakeven": true,
      "meets_fully_levered_breakeven": true,
      "meets_unlevered_with_caprec": false,
      "meets_fully_levered_with_caprec": true
    },
    "cost_breakdown": {
      "tenant_cash_allowance": 300000.0,
      "listing_agent": 50000.0,
      "tenant_rep": 100000.0,
      "net_free_rent_pv": -35951.24
    }
  }
}
```

## Usage Examples

### Calculate NER/GER for a Deal

```bash
python3 baf_calculator.py my_deal.json
```

Output:
- Prints formatted results to console
- Saves JSON results to `my_deal_results.json`

### Save to Custom Location

```bash
python3 baf_calculator.py my_deal.json -o Reports/deal_analysis.json
```

### Batch Process Multiple Deals

```bash
for file in deals/*.json; do
    python3 baf_calculator.py "$file" -o "results/$(basename $file .json)_results.json"
done
```

### Silent Mode (No Console Output)

```bash
python3 baf_calculator.py my_deal.json -o results.json --no-print
```

## Common Scenarios

### Scenario 1: Flat Rent, No Incentives

**Input:**
- 5,000 sf
- $30/sf flat for 5 years
- $10/sf operating costs
- No TI, no free rent
- 8% discount

**Expected NER:** Close to $30/sf (minimal adjustment since no costs)

### Scenario 2: High TI Allowance

**Input:**
- 10,000 sf
- $20/sf rent for 10 years
- $40/sf TI allowance (high!)
- 3 months free rent
- 10% discount

**Expected NER:** Significantly lower than $20/sf due to high upfront costs

### Scenario 3: Graduated Rent

**Input:**
- 20,000 sf
- Starting at $15/sf, increasing to $25/sf over 10 years
- Moderate TI ($25/sf)
- 6 months free rent during fixturing

**Expected NER:** Between $15-25/sf, adjusted for TI and free rent

## Validation & Error Checking

The calculator validates:
- ✓ JSON syntax is correct
- ✓ Required fields are present
- ✓ Numeric fields are valid numbers
- ✓ Date format is YYYY-MM-DD
- ✗ Does NOT validate business logic (e.g., rent > 0)

Common errors:
```bash
ERROR: Input file not found: deal.json
  → Check file path

ERROR: Invalid JSON in input file
  → Check JSON syntax (commas, quotes, brackets)

ERROR: Failed to load input file: ...
  → Check field names and types
```

## Tips & Best Practices

### Rent Schedule
- Always provide annual rent per sf (not monthly)
- Include full term (extend array if needed)
- Example: 10 years = array of 10 values

### Incentives
- TI allowance: Express as $/sf for consistency
- Free rent: Use "net" for most cases (tenant pays op costs)
- Large landlord work: Use `landlord_work_total` with absolute amount

### Discount Rate
- Match to your cost of capital
- Industrial: typically 9-11%
- Office: typically 8-10%
- Higher rate = lower NPV = lower NER

### Investment Parameters
- Optional - only needed for breakeven analysis
- Use actual property acquisition metrics
- Can leave at defaults for relative comparisons

## Reference: Field Mappings

| JSON Field | Excel Cell | Description |
|------------|------------|-------------|
| `area_sf` | B16 | Rentable area |
| `lease_term_months` | D41 | Lease term |
| `operating_costs_psf` | D42 | Op costs |
| `fixturing_term_months` | D46 | Fixturing period |
| `rent_psf_by_year[0]` | A54 | Year 1 rent |
| `tenant_cash_allowance_psf` | Calc from A70 | TI allowance |
| `nominal_discount_rate` | N22 | Discount rate |

---

**For more information**, see:
- `README.md` - Full documentation
- `baf_input_example.json` - Complete example
- `baf_input_simple.json` - Minimal example
