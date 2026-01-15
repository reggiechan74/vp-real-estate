# Comparable Sales Adjustment Calculator

Expert calculator for technical adjustment grid construction using sequential 6-stage adjustment hierarchy, multiple quantification methodologies, and statistical validation.

## Overview

This calculator applies the industry-standard **6-stage adjustment hierarchy** to comparable sales analysis:

1. **Property Rights** - Convert leasehold to fee simple equivalent
2. **Financing Terms** - Adjust seller financing to cash equivalent
3. **Conditions of Sale** - Normalize non-arm's length transactions
4. **Market Conditions/Time** - Apply market appreciation/depreciation
5. **Location** - Adjust for micro-market differences
6. **Physical Characteristics** - Adjust for size, condition, improvements

Each stage adjusts the price sequentially, with later adjustments applied to the adjusted price from previous stages.

## Features

### Sequential Adjustment Hierarchy

**Why sequence matters**: Some adjustments affect the base from which subsequent adjustments are calculated.

**Example**:
- Sale price: $800,000 (leasehold with $50K/year ground rent)
- Stage 1 (Property Rights): +$1,000,000 → $1,800,000 (fee simple equivalent)
- Stage 2 (Financing): Seller VTB adjustment applied to $1,800,000 (not $800,000)

### Adjustment Quantification Methods

The calculator uses multiple methodologies documented in the skill:

- **Paired Sales Analysis** - Isolation method comparing properties differing in one characteristic
- **Statistical Regression** - Hedonic price modeling (when sufficient data available)
- **Cost Approach** - Depreciated replacement cost for improvements
- **Income Approach** - Rental differential capitalization
- **Professional Judgment** - Documented reasoning when data insufficient

### Validation Rules

Industry-standard validation thresholds:

- **Gross Adjustment** (sum of absolute adjustments):
  - <25%: Acceptable - weight normally
  - 25-30%: Acceptable but approaching limits
  - 30-40%: Caution range - comparable is marginal, reduce weight
  - >40%: Reject - not truly comparable, exclude from analysis

- **Net Adjustment** (sum of signed adjustments):
  - <15%: Preferred range
  - >15%: Flag for review - comparable may be significantly inferior/superior

### Sensitivity Analysis

Tests impact of ±10% variation in key adjustments (adjustments >5%):

```json
{
  "adjustment": "Location",
  "base_adjustment": 780633.70,
  "low_scenario": {
    "adjustment": 702570.33,
    "adjusted_price": 3810105.11,
    "change_pct": -2.01
  },
  "high_scenario": {
    "adjustment": 858697.07,
    "adjusted_price": 3966231.85,
    "change_pct": 2.01
  }
}
```

## Usage

### Basic Usage

```bash
python3 comparable_sales_calculator.py sample_industrial_comps.json
```

### With Output File

```bash
python3 comparable_sales_calculator.py input.json --output results.json
```

### With Sensitivity Analysis

```bash
python3 comparable_sales_calculator.py input.json --sensitivity
```

### Verbose Output (Full JSON)

```bash
python3 comparable_sales_calculator.py input.json --verbose
```

## Input Format

### Subject Property

```json
{
  "subject_property": {
    "address": "2550 Industrial Parkway North, Hamilton, ON",
    "property_rights": "fee_simple",
    "size_sf": 50000,
    "location_score": 85,
    "condition": "average",
    "highway_frontage": true
  }
}
```

**Fields**:
- `property_rights`: `"fee_simple"` or `"leasehold"`
- `size_sf`: Size in square feet
- `location_score`: Numeric score (0-100, higher is better)
- `condition`: `"poor"` | `"fair"` | `"average"` | `"good"` | `"excellent"`
- `highway_frontage`: Boolean (optional)

### Comparable Sales

```json
{
  "comparable_sales": [
    {
      "address": "2300 Industrial Parkway North, Hamilton, ON",
      "sale_price": 4500000,
      "sale_date": "2024-03-15",
      "property_rights": "fee_simple",
      "financing": {
        "type": "cash"
      },
      "conditions_of_sale": {
        "arms_length": true
      },
      "size_sf": 48000,
      "location_score": 90,
      "condition": "good",
      "highway_frontage": true
    }
  ]
}
```

**Property Rights**:
- `property_rights`: `"fee_simple"` or `"leasehold"`
- `ground_rent_annual`: Annual ground rent (required if leasehold)

**Financing** (if not cash):
```json
{
  "financing": {
    "type": "seller_vtb",
    "rate": 3.5,
    "market_rate": 6.5,
    "term_years": 10,
    "loan_amount": 1600000
  }
}
```

**Conditions of Sale** (if non-arm's length):
```json
{
  "conditions_of_sale": {
    "arms_length": false,
    "motivation_discount_pct": 12
  }
}
```

### Market Parameters

```json
{
  "market_parameters": {
    "appreciation_rate_annual": 3.5,
    "cap_rate": 7.0,
    "location_premium_highway": 15,
    "location_premium_per_point": 1.0,
    "size_adjustment_per_sf": 3.0,
    "condition_adjustment_pct_per_level": 5.0,
    "valuation_date": "2025-01-15"
  }
}
```

**Fields**:
- `appreciation_rate_annual`: Annual market appreciation % (e.g., 3.5 = 3.5%)
- `cap_rate`: Capitalization rate % for income calculations (e.g., 7.0 = 7%)
- `location_premium_highway`: Premium % for highway frontage (e.g., 15 = 15%)
- `location_premium_per_point`: Premium % per location score point (e.g., 1.0 = 1%)
- `size_adjustment_per_sf`: $/sq ft adjustment for size differences
- `condition_adjustment_pct_per_level`: % adjustment per condition level
- `valuation_date`: ISO date format (YYYY-MM-DD)

## Output Format

### Comparable Results

Each comparable includes:

```json
{
  "comparable": {
    "address": "...",
    "sale_price": 4500000,
    "sale_date": "2024-03-15"
  },
  "adjustment_stages": [
    {
      "stage": 1,
      "name": "Property Rights",
      "adjustment_amount": 0.0,
      "adjustment_pct": 0.0,
      "adjusted_price": 4500000,
      "explanation": "Both subject and comparable are fee simple - no adjustment"
    }
  ],
  "summary": {
    "final_adjusted_price": 4186001.96,
    "gross_adjustment": 577160.28,
    "gross_adjustment_pct": 12.83,
    "net_adjustment": -313998.04,
    "net_adjustment_pct": -6.98
  },
  "validation": {
    "gross_exceeds_25pct": false,
    "gross_exceeds_40pct": false,
    "net_exceeds_15pct": false,
    "status": "ACCEPTABLE",
    "recommendation": "Gross adjustment 12.8% is well within acceptable limits - weight normally"
  },
  "weighting": {
    "weight": 1.5,
    "weighted_value": 6279002.94,
    "rationale": "Increased weight (150%) - small net adjustments (5-10%)"
  }
}
```

### Reconciliation

```json
{
  "reconciliation": {
    "reconciled_value": 4756028.48,
    "value_range": {
      "low": 3888168.48,
      "high": 7035649.91,
      "spread_pct": 80.95
    },
    "weighting_method": "Inverse net adjustment with validation status filters",
    "total_weight": 4.5
  },
  "statistics": {
    "count": 6,
    "mean": 4896796.85,
    "median": 4569660.52,
    "stdev": 1128685.43,
    "min": 3888168.48,
    "max": 7035649.91,
    "q1": 4271895.54,
    "q3": 5001165.98
  }
}
```

## Weighting Scheme

Comparables are weighted based on validation status and net adjustment percentage:

| Validation Status | Net Adjustment | Weight | Rationale |
|------------------|----------------|--------|-----------|
| REJECT | Any | 0.0x | Gross adjustments exceed 40% |
| CAUTION | Any | 0.5x | Gross adjustments in caution range (30-40%) |
| ACCEPTABLE | <5% | 2.0x | Minimal net adjustments |
| ACCEPTABLE | 5-10% | 1.5x | Small net adjustments |
| ACCEPTABLE | >10% | 1.0x | Normal weight |

## Example Output

```
================================================================================
COMPARABLE SALES ADJUSTMENT ANALYSIS
================================================================================
Subject Property: 2550 Industrial Parkway North, Hamilton, ON
Size: 50,000 sq ft
Location Score: 85

COMPARABLE SALES:
────────────────────────────────────────────────────────────────────────────────

Comparable 1: 2300 Industrial Parkway North, Hamilton, ON
  Sale Price:           $      4,500,000
  Sale Date:                 2024-03-15
  Gross Adjustment:               12.8%  ($577,160)
  Net Adjustment:                 -7.0%  ($-313,998)
  Adjusted Price:       $      4,186,002
  Validation:                ACCEPTABLE
  Weight:                           1.5x

Comparable 4: 1200 Burlington Street East, Hamilton, ON
  Sale Price:           $      2,800,000
  Sale Date:                 2023-06-18
  Gross Adjustment:               64.6%  ($1,809,745)
  Net Adjustment:                 64.6%  ($1,809,745)
  Adjusted Price:       $      4,609,745
  Validation:                    REJECT
  Weight:                           0.0x
  Note: Gross adjustment 64.6% exceeds 40% threshold - comparable is NOT truly comparable, do not use

────────────────────────────────────────────────────────────────────────────────
RECONCILIATION:
────────────────────────────────────────────────────────────────────────────────
Adjusted Price Range:    $      3,888,168 - $      7,035,650
Range Spread:                      81.0%
Statistical Mean:        $      4,896,797
Statistical Median:      $      4,569,661
Reconciled Value:        $      4,756,028

Weighting Method: Inverse net adjustment with validation status filters
================================================================================
```

## Dependencies

Uses shared financial utilities from `/workspaces/lease-abstract/Shared_Utils/`:
- `pv_annuity()` - Present value of annuity calculations
- `npv()` - Net present value
- `descriptive_statistics()` - Statistical analysis

## Integration with Skill

This calculator supports the **comparable-sales-adjustment-methodology** skill:

- **Skill location**: `.claude/skills/comparable-sales-adjustment-methodology/`
- **Used by**: Alexi (Expropriation Appraisal Expert), appraisal professionals
- **Activates when**: Constructing detailed comparable sales grids, quantifying adjustments, applying statistical validation, reconciling adjusted sale prices

## Sample Input

See `sample_industrial_comps.json` for a complete example with 6 comparable sales including:
- Fee simple and leasehold properties
- Cash and seller VTB financing
- Arm's length and non-arm's length transactions
- Various locations, sizes, and conditions
- Date range requiring time adjustments

## Technical Notes

### Adjustment Sequencing

Adjustments are applied sequentially in the proper order. Each stage adjusts the price from the previous stage:

```
Sale Price: $800,000
→ Stage 1 (Property Rights): +$1,000,000 → $1,800,000
→ Stage 2 (Financing): -$200,000 → $1,600,000
→ Stage 3 (Conditions): +$100,000 → $1,700,000
→ Stage 4 (Time): +$85,000 → $1,785,000
→ Stage 5 (Location): +$267,750 → $2,052,750
→ Stage 6 (Physical): -$50,000 → $2,002,750 (final)
```

### Gross vs. Net Adjustment

- **Gross Adjustment**: Sum of absolute values (tests whether comparable is truly comparable)
  - Formula: |Adj1| + |Adj2| + ... + |Adj6|
  - Example: |+$100K| + |−$50K| = $150K

- **Net Adjustment**: Sum of signed values (tests whether comparable is inferior/superior)
  - Formula: Adj1 + Adj2 + ... + Adj6
  - Example: +$100K + (−$50K) = +$50K

### Time Adjustment Compounding

Market appreciation is compounded annually:

```
Adjusted Price = Sale Price × (1 + annual_rate)^years
```

Example:
- Sale: $1,000,000 (18 months ago)
- Appreciation: 3.5% annually
- Adjustment: $1,000,000 × (1.035^1.5) = $1,052,729 (+5.3%)

## Version History

- **1.0.0** (2025-11-15): Initial release
  - 6-stage sequential adjustment hierarchy
  - Multiple adjustment quantification methods
  - Statistical validation (gross/net limits)
  - Sensitivity analysis
  - Weighted reconciliation

## Author

Claude Code - Anthropic's official CLI for Claude

## License

Part of the Commercial Real Estate Lease Analysis Toolkit
