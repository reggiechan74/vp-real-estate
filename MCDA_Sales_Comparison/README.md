# MCDA Sales Comparison Calculator

Multi-Criteria Decision Analysis (MCDA) for fee simple property valuation using ordinal ranking methodology.

## Overview

This calculator uses **ordinal ranking** rather than traditional dollar adjustments to value properties. All properties (subject + comparables) are ranked on each characteristic, then weighted scores map to indicated value via interpolation and regression.

### Why MCDA?

| Traditional DCA | MCDA Ordinal Ranking |
|-----------------|----------------------|
| Requires paired sales for adjustment rates | Relative rankings are more stable |
| Sensitive to sequential adjustment order | Weights can be customized by property type |
| Can compound errors across many adjustments | Score-to-price mapping via interpolation/regression |
| Harder with heterogeneous comparables | Handles diverse comparable sets well |

## Quick Start

```bash
cd MCDA_Sales_Comparison

# Run with sample data
python mcda_sales_calculator.py sample_input.json --verbose

# Run with custom weight profile
python mcda_sales_calculator.py sample_input.json --profile industrial_logistics

# Save output to file
python mcda_sales_calculator.py sample_input.json --output results.json
```

## Installation

No additional dependencies required - uses Python standard library only.

```bash
# Run tests
python -m pytest tests/ -v

# All 74 tests should pass
```

## Input Format

```json
{
  "analysis_date": "2025-12-16",
  "valuation_date": "2025-01-15",
  "market_area": "Greater Hamilton Industrial",
  "property_type": "industrial",
  "subject_property": {
    "address": "2550 Industrial Parkway North, Hamilton, ON",
    "building_sf": 50000,
    "clear_height_feet": 28,
    "loading_docks_total": 6,
    "effective_age_years": 15,
    "condition": "average",
    "location_score": 75,
    "highway_frontage": true
  },
  "comparable_sales": [
    {
      "id": "COMP_1",
      "address": "2480 Industrial Parkway North",
      "sale_price": 4650000,
      "sale_date": "2024-09-15",
      "building_sf": 48500,
      "clear_height_feet": 28,
      "condition": "average",
      "location_score": 76,
      "property_rights": "fee_simple",
      "financing": {"type": "cash"},
      "conditions_of_sale": {"arms_length": true}
    }
  ],
  "market_parameters": {
    "appreciation_rate_annual": 3.5
  }
}
```

### Required Fields

| Field | Subject | Comparables |
|-------|---------|-------------|
| `address` | ✓ | ✓ |
| `building_sf` | ✓ | ✓ |
| `sale_price` | - | ✓ |
| `sale_date` | - | ✓ |

### Minimum Comparables

At least **3 valid arm's length sales** required.

## Weight Profiles

### Industrial Default

```
location_score:       20%  (Higher is better)
clear_height_feet:    15%  (Higher is better)
condition:            15%  (Lower is better - ordinal)
effective_age_years:  15%  (Lower is better)
loading_docks_total:  10%  (Higher is better)
highway_frontage:     10%  (Higher is better)
lot_size_acres:        5%  (Higher is better)
building_size_sf:      5%  (Closer to subject)
office_finish_pct:     5%  (Higher is better)
```

### Industrial Logistics

Higher weights on dock count, clear height, and highway access for distribution centers.

### Industrial Manufacturing

Adds weights for power capacity and crane systems.

### Office Default

Emphasizes location, building class, and parking ratio.

## Output

```json
{
  "subject_property": {
    "address": "2550 Industrial Parkway North, Hamilton, ON",
    "building_sf": 50000,
    "composite_score": 3.079
  },
  "value_indication": {
    "indicated_value_psf": 92.96,
    "indicated_value_total": 4648009,
    "value_range_psf": [87.69, 98.53],
    "interpolation": {
      "indicated_psf": 93.83,
      "confidence": "high",
      "lower_bracket": "COMP_1",
      "upper_bracket": "COMP_4"
    },
    "regression": {
      "indicated_psf": 92.30,
      "method": "ols",
      "r_squared": 0.928,
      "beta": -7.55
    },
    "reconciliation": {
      "method_weights": {"interpolation": 0.43, "regression": 0.57},
      "rationale": "Strong model fit (R²=0.93) supports regression"
    }
  }
}
```

## Methodology

### 1. Property Ranking

For each characteristic, all properties (subject + comparables) are ranked from best to worst:

- **Higher is better**: Clear height, dock count, location score
- **Lower is better**: Age, condition (ordinal scale)
- **Tie handling**: Average rank assigned to tied properties

### 2. Composite Score

Weighted sum of variable ranks:

```
Score = Σ (weight_i × rank_i)
```

Lower score = better property = expected higher price.

### 3. Score-to-Price Mapping

**Interpolation**: Finds comparables that bracket subject's score and linearly interpolates.

**Regression**: Fits OLS/monotonic/Theil-Sen regression of price vs. score.

### 4. Reconciliation

Weights interpolation and regression results based on:
- Sample size (small n favors interpolation)
- R² (high R² favors regression)
- Bracket confidence (tight brackets favor interpolation)

## Module Structure

```
MCDA_Sales_Comparison/
├── __init__.py
├── mcda_sales_calculator.py    # Main calculator with CLI
├── validation.py               # Input validation
├── weight_profiles.py          # Weight profile definitions
├── score_to_price.py           # Interpolation and regression
├── sample_input.json           # Example input file
├── README.md                   # This file
└── tests/
    ├── __init__.py
    ├── test_validation.py      # 20 tests
    ├── test_weight_profiles.py # 17 tests
    ├── test_score_to_price.py  # 22 tests
    └── test_mcda_calculator.py # 15 tests
```

## Test Coverage

```bash
$ python -m pytest tests/ -v
# 74 passed in 0.13s
```

| Module | Tests | Coverage |
|--------|-------|----------|
| validation.py | 20 | PSF ranges, transactions, time, monotonicity |
| weight_profiles.py | 17 | Profiles, normalization, dynamic allocation |
| score_to_price.py | 22 | Interpolation, regression, reconciliation |
| mcda_sales_calculator.py | 15 | Ranking, composite scores, full pipeline |

## Related Commands

- `/mcda-sales-comparison` - Slash command for this calculator
- `/comparable-sales-analysis` - Traditional DCA with dollar adjustments
- `/relative-valuation` - MCDA for competitive positioning (leasing)

## Author

Claude Code - December 2025
