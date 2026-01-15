# Alex Pitt Demonstration Files

**Purpose:** Sample input files for demonstrating hydro corridor appraisal automation capabilities.

## Files Overview

### Hydro Easement Valuation Samples

| File | Voltage | Property | Use Case |
|------|---------|----------|----------|
| `hydro_500kv_agricultural.json` | 500 kV | 250-acre farm | High-voltage corridor |
| `hydro_230kv_rural_residential.json` | 230 kV | 50-acre rural lot | Medium-voltage |
| `hydro_115kv_commercial.json` | 115 kV | 10-acre commercial | Lower-voltage urban |

### Comparable Sales Samples

| File | Property Type | Comparables | Use Case |
|------|---------------|-------------|----------|
| `comps_agricultural_land.json` | Agricultural | 4 sales | Before/after land valuation |
| `comps_rural_residential.json` | Rural residential | 3 sales | Residential corridor |

## Running Demonstrations

### Easement Valuation

```bash
# 500kV transmission line easement
/easement-valuation Repository_Dev_Plans/AP_Demo/hydro_500kv_agricultural.json

# 230kV through rural residential
/easement-valuation Repository_Dev_Plans/AP_Demo/hydro_230kv_rural_residential.json

# 115kV commercial property
/easement-valuation Repository_Dev_Plans/AP_Demo/hydro_115kv_commercial.json
```

### Comparable Sales Analysis

```bash
# Agricultural land valuation (for before/after)
/comparable-sales-analysis Repository_Dev_Plans/AP_Demo/comps_agricultural_land.json

# Rural residential land valuation
/comparable-sales-analysis Repository_Dev_Plans/AP_Demo/comps_rural_residential.json
```

## Key Demonstration Points

1. **Voltage-Based Percentages** - Show how 500kV vs 115kV affects the base percentage
2. **Three-Method Reconciliation** - Percentage of fee, income cap, before/after
3. **Adjustment Quantification** - The "Arrow Converter" for comparable sales
4. **USPAP/CUSPAP Compliance** - Validation of gross/net adjustment limits
5. **Defensible Methodology** - Documentation for litigation support
