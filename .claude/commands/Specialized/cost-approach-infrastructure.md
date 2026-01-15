---
description: Cost approach valuation for specialized infrastructure (transmission towers, telecom sites, substations) using replacement cost new less depreciation
argument-hint: <construction-data-json> [--output <report-path>]
allowed-tools: Read, Write, Bash
---

# Cost Approach Infrastructure Valuation

Value specialized infrastructure using replacement cost new less depreciation (physical, functional, external obsolescence) with market reconciliation.

## Usage

```bash
# Basic usage with JSON input
/cost-approach-infrastructure path/to/construction_data.json

# With custom output path
/cost-approach-infrastructure path/to/construction_data.json --output Reports/2025-11-17_infrastructure_valuation.md
```

## Input Structure

The input JSON should follow the `infrastructure_cost_input_schema.json` specification:

```json
{
  "asset_type": "Transmission tower",
  "specifications": {
    "voltage": "500kV",
    "height_meters": 45,
    "foundation_type": "Caisson",
    "conductor_type": "ACSR",
    "number_of_circuits": 2
  },
  "construction_costs": {
    "materials": 150000,
    "labor": 80000,
    "overhead_percentage": 0.15,
    "profit_percentage": 0.12
  },
  "depreciation": {
    "age_years": 15,
    "effective_age_years": 12,
    "economic_life_years": 50,
    "physical_condition": "Good",
    "functional_obsolescence": 0,
    "external_obsolescence": 0
  },
  "market_data": {
    "comparable_sales": [
      {
        "sale_price": 185000,
        "asset_type": "Transmission tower",
        "sale_date": "2024-03-15",
        "condition": "Good",
        "location": "Similar rural setting"
      }
    ]
  }
}
```

## Workflow

This command executes the following workflow:

1. **Validate Input**: Validates JSON against schema
2. **Calculate Replacement Cost New (RCN)**:
   - Direct costs: Materials + Labor
   - Overhead: 12-18% of direct costs
   - Profit: 10-15% of subtotal
3. **Analyze Physical Depreciation**:
   - Age/Life method: (Effective Age ÷ Economic Life) × RCN
   - Observed condition method: Based on physical condition rating
4. **Assess Functional Obsolescence**:
   - Design inefficiency (curable/incurable)
   - Excess capacity
   - Operational deficiencies
5. **Assess External Obsolescence**:
   - Market conditions
   - Regulatory changes
   - Economic factors
6. **Calculate Depreciated Replacement Cost**: RCN - Total Depreciation
7. **Reconcile with Market**: Compare with comparable sales (if available)
8. **Generate Report**: Timestamped markdown report with breakdown

## Output

The command generates:

- **Replacement Cost New (RCN)**: Materials, labor, overhead, profit breakdown
- **Physical Depreciation**: Age/life calculation and condition adjustment
- **Functional Obsolescence**: Design/capacity/operational issues (if any)
- **External Obsolescence**: Market/regulatory/economic factors (if any)
- **Depreciated Replacement Cost**: RCN less total depreciation
- **Market Reconciliation**: Variance analysis with comparable sales
- **Confidence Assessment**: 7-factor confidence score (0-100)
- **Timestamped Report**: `Reports/YYYY-MM-DD_HHMMSS_cost_approach_{asset_type}.md`

## Related Skills

- **cost-approach-expert**: Auto-loaded for cost approach valuation
- **comparable-sales-adjustment-methodology**: For market reconciliation
- **transmission-line-technical-specifications**: For technical parameters

## Calculator

Uses: `.claude/skills/cost-approach-expert/infrastructure_cost_calculator.py`
