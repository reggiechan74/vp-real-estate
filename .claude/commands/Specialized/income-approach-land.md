---
description: Income approach land valuation by capitalizing land rent (telecom sites, agricultural rent, ground leases) with capitalization rate analysis
argument-hint: <rental-data-json> [--output <report-path>]
allowed-tools: Read, Write, Bash
---

# Income Approach Land Valuation

Value land by capitalizing rental income using market rent analysis, capitalization rate selection (3 methods), and reconciliation with sales comparison approach.

## Usage

```bash
# Basic usage with JSON input
/income-approach-land path/to/rental_data.json

# With custom output path
/income-approach-land path/to/rental_data.json --output Reports/2025-11-17_land_valuation.md
```

## Input Structure

The input JSON should follow the `land_rental_input_schema.json` specification:

```json
{
  "site_type": "Telecom tower site",
  "land_rent": {
    "annual_rent": 12000,
    "lease_term": 20,
    "escalations": "3% per 5 years",
    "commencement_date": "2024-01-01"
  },
  "market_data": {
    "comparable_rents": [
      {"location": "Site A - 2km north", "annual_rent": 10000, "lease_term": 15},
      {"location": "Site B - 5km east", "annual_rent": 14000, "lease_term": 20},
      {"location": "Site C - 3km south", "annual_rent": 11500, "lease_term": 20}
    ],
    "cap_rate_range": {
      "low": 0.06,
      "high": 0.09
    },
    "comparable_sales": [
      {"property_id": "Sale 1", "sale_price": 150000, "noi": 10500, "sale_date": "2024-06-15"},
      {"property_id": "Sale 2", "sale_price": 180000, "noi": 12600, "sale_date": "2024-08-20"}
    ],
    "financing": {
      "ltv": 0.75,
      "debt_yield": 0.055,
      "equity_yield": 0.12
    }
  },
  "operating_expenses": {
    "property_tax": 2000,
    "insurance": 800,
    "maintenance": 1200,
    "management_fee": 600
  }
}
```

## Workflow

This command executes the following workflow:

1. **Validate Input**: Validates JSON against schema
2. **Analyze Market Rent**: Reconciles comparable rents to market rent conclusion
3. **Select Capitalization Rate**: Uses 3 methods:
   - **Market Extraction**: Cap Rate = NOI ÷ Sale Price from comparables
   - **Band of Investment**: (LTV% × Debt Yield) + (Equity% × Equity Yield)
   - **Buildup Method**: Risk-free + Liquidity + Inflation + Business Risk
4. **Calculate NOI**: Market Rent - Operating Expenses
5. **Calculate Land Value**: NOI ÷ Cap Rate
6. **Reconcile with Sales**: Compare with sales comparison approach (if available)
7. **Sensitivity Analysis**: Test ±0.5% cap rate impact on value
8. **Generate Report**: Timestamped markdown report with methodology

## Output

The command generates:

- **Market Rent Conclusion**: With comparable rent adjustments
- **Capitalization Rate Analysis**: 3 methods with reconciliation to single rate
- **NOI Calculation**: Gross rent less operating expenses
- **Land Value by Income Approach**: NOI ÷ Cap Rate
- **Reconciliation**: With sales comparison approach (variance analysis)
- **Sensitivity Analysis**: ±0.5% cap rate impact table
- **Timestamped Report**: `Reports/YYYY-MM-DD_HHMMSS_income_approach_{site_type}.md`

## Related Skills

- **income-approach-expert**: Auto-loaded for income valuation
- **easement-valuation-methods**: For easement rent capitalization
- **comparable-sales-adjustment-methodology**: For sales reconciliation

## Calculator

Uses: `.claude/skills/income-approach-expert/land_capitalization_calculator.py`
