# Effective Rent Calculator

A Python tool for calculating Net Effective Rent (NER), Gross Effective Rent (GER), and comprehensive lease deal analysis including NPV calculations, breakeven analysis, and capital recovery requirements.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run with an input file
python3 eff_rent_calculator.py baf_input_simple.json

# Output is displayed in console and saved to JSON
```

## Files

- **eff_rent_calculator.py** - Main calculator script
- **baf_input_simple.json** - Simple example input template
- **baf_input_example.json** - Complete example (10-year industrial lease)
- **baf_input_test2.json** - Complex example with varied rent schedule
- **BAF_INPUT_FORMAT.md** - Complete JSON format documentation (580+ lines)
- **requirements.txt** - Python dependencies

## Key Calculations

The calculator computes:

**NPV Analysis:**
- NPV of Net Rent (present value of all rent payments)
- NPV of Costs (TI allowance, commissions, free rent)
- NPV of Lease Deal (net rent minus costs)

**Effective Rent:**
- Net Effective Rent (NER) - lease term only and with fixturing period
- Gross Effective Rent (GER) - NER plus operating costs

**Breakeven Analysis:**
- Unlevered, Interest-Only Levered, and Fully Levered breakeven NER
- Capital recovery requirements (Inwood sinking fund method)

**Investment Assessment:**
- Compares proposed NER against all breakeven thresholds
- Pass/fail analysis for investment decision criteria

## Theoretical Foundation

This calculator implements the **Ponzi Rental Rate (PRR)** framework, which provides objective breakeven rental rates based on acquisition cost and financing terms rather than subjective market-based budgets.

**Academic Reference:**

Chan, R. (2015). "Understanding the Ponzi Rental Rate: The Challenges with Using Net Effective Rents to Analyze Prospective Lease Deals within Real Estate Investment Trusts." *Real Estate Finance*, Vol. 32, No. 2, pp. 48-61.

**Key Concepts from the Paper:**

The PRR framework addresses a fundamental flaw in conventional lease analysis: comparing proposed deals only against budgeted NER without considering the actual cash requirements of the property. The framework recognizes that REITs must account for:

1. **Explicit Cash Flows** (within lease term):
   - Dividend distributions to unit holders
   - Mortgage interest payments
   - Mortgage principal repayments

2. **Implicit Non-Cash Items** (over building life):
   - Physical building depreciation over remaining useful life
   - Replacement cost via sinking fund (Inwood method)

The calculator implements four breakeven thresholds:

- **Unlevered Breakeven NER**: Dividends only
- **I/O Levered Breakeven NER**: Dividends + Interest
- **Fully Levered Breakeven NER**: Dividends + Interest + Principal
- **With Capital Recovery**: Above + Sinking fund for building replacement

**Critical Insight:** The Inwood sinking fund method calculates the periodic payment needed to **accumulate** to the building replacement cost (FV method), not to recover a past cost (PV method). This ensures true cash flow neutrality over the asset's life.

## Calculation Methodology

### Net Effective Rent (NER) - Landlord's Perspective

NER represents the **landlord's actual cash return** after accounting for all costs:

```
NER = Annuity due of (NPV of rent received - All landlord costs)
```

**Landlord Costs Include:**
- Tenant Improvement allowance
- Landlord's work
- Leasing commissions (listing agent + tenant rep)
- Free rent (net or gross)
- PM override fees

**Free Rent Treatment:**
- **Net Free Rent**: Landlord loses base rent but tenant still pays operating costs
  - Cost to landlord: PV of base rent only during free period
- **Gross Free Rent**: Landlord loses base rent AND operating costs (tenant pays nothing)
  - Cost to landlord: PV of (base rent + operating costs) during free period

### Gross Effective Rent (GER) - Tenant's Perspective

GER represents the **tenant's total occupancy cost** including operating expenses:

```
GER = Annuity due of (NPV of rent + NPV of operating costs - Tenant benefits)
```

**Tenant Benefits Include (NOT landlord costs):**
- Tenant Improvement allowance received
- Landlord's work provided
- Free rent benefit (net or gross)
- Amortized tenant work contribution

**Excluded from Tenant Benefits:**
- Leasing commissions (landlord pays these, not tenant)
- PM override fees (landlord's internal cost)

**Free Rent Treatment (Critical Nuance):**
- **Net Free Rent**: Tenant pays $0 base rent but DOES pay operating costs
  - Benefit to tenant: PV of base rent saved
  - Operating costs stream: Full lease term (no adjustment)
- **Gross Free Rent**: Tenant pays NOTHING (no base rent, no operating costs)
  - Benefit to tenant: PV of (base rent + operating costs) saved
  - Operating costs stream: Adjusted to exclude free period (avoid double-counting)

**Why This Matters:**

If gross free rent operating costs weren't excluded from the op cost stream, they would be counted twice:
1. Once in the full operating cost calculation
2. Again in the `gross_free_rent_pv` benefit

This would artificially lower the tenant's effective cost.

### Commission Structures - Industrial vs Office

The calculator supports two different commission calculation methods based on property type:

#### Industrial Commissions (Percentage of Net Rent)

Industrial leasing commissions are calculated as a **percentage of each year's net rent**:

```
Year 1: Commission = Year 1 rent × year1_pct
Years 2+: Commission = Each year's rent × subsequent_pct
```

**Typical Structure:**
- Listing agent: 4-6% year 1, 2-3% subsequent years
- Tenant rep: 4-6% year 1, 2-3% subsequent years

**Example:** 10-year lease at $15/sf base rent, 5% year 1, 2.5% subsequent
- Listing agent commission:
  - Year 1: $15/sf × 10,000 sf × 5% = $7,500
  - Years 2-10: $15/sf × 10,000 sf × 2.5% × 9 years = $33,750
  - Total: $41,250 ($4.13/sf)

**Why This Makes Sense:** Industrial rents are typically lower per square foot, so percentage-based commissions tied to actual rent ensure brokers are compensated fairly as rents escalate.

#### Office Commissions (Flat $/sf per Year)

Office leasing commissions are calculated as a **flat amount per square foot multiplied by lease years**:

```
Total Commission = $/sf rate × lease term in years
```

**Typical Structure:**
- Listing agent: $1.50 - $3.00 /sf/year
- Tenant rep: $1.50 - $3.00 /sf/year

**Example:** 5-year lease at $2/sf per year each side
- Listing agent: $2/sf × 5 years = $10/sf ($50,000 on 5,000 sf)
- Tenant rep: $2/sf × 5 years = $10/sf ($50,000 on 5,000 sf)
- Total: $20/sf ($100,000)

**Why This Makes Sense:** Office rents are higher, and the flat $/sf method provides predictable costs regardless of rent escalations.

**Implementation Note:** The calculator automatically detects which method to use based on which JSON fields are populated. Use `_year1_pct` and `_subsequent_pct` fields for industrial, or `_commission_psf` fields for office.

## Usage

```bash
python3 eff_rent_calculator.py <input_file.json>
```

### Optional Arguments

```bash
# Specify output file location
python3 eff_rent_calculator.py input.json -o custom_output.json

# Suppress console output (JSON only)
python3 eff_rent_calculator.py input.json --no-print
```

## Input File Format

See `BAF_INPUT_FORMAT.md` for complete documentation.

Basic structure:
```json
{
  "deal_name": "Your Deal Name",
  "property_info": {
    "area_sf": 10000.0,
    "gla_building_sf": 50000.0
  },
  "lease_terms": {
    "lease_term_months": 60,
    "fixturing_term_months": 0,
    "operating_costs_psf": 10.0
  },
  "rent_schedule": {
    "rent_psf_by_year": [15.0, 15.0, 16.0, 16.5, 17.0]
  },
  "incentives": {
    "tenant_cash_allowance_psf": 15.0,
    "net_free_rent_months": 2.0
  },
  "financial_assumptions": {
    "nominal_discount_rate": 0.10
  }
}
```

## Output

Results are provided in two formats:

1. **Console Output** - Formatted tables with all calculations
2. **JSON File** - Structured data for integration with other systems

Example output filename: `baf_input_simple_results.json`

## Validation

This calculator has been validated against industry-standard Excel templates with 100% accuracy across all metrics.

## Requirements

- Python 3.8+
- numpy >= 1.24.0
- numpy-financial >= 1.0.0

## Technical Details

- Uses annuity due calculations (payments at beginning of period)
- Monthly compounding for multi-year cash flows
- Inwood sinking fund method for capital recovery (FV accumulation)
- All financial calculations use numpy-financial library
