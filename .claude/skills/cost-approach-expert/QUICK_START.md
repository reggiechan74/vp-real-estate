# Quick Start Guide - Infrastructure Cost Calculator

## Installation

No installation required - uses Python standard library only.

## Basic Usage

### 1. Prepare Input JSON

```json
{
  "asset_type": "Transmission tower",
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
  }
}
```

### 2. Run Calculator

```bash
python infrastructure_cost_calculator.py input.json --verbose
```

### 3. View Results

Results saved to `Reports/YYYY-MM-DD_HHMMSS_cost_approach_[asset_type].md`

## Common Scenarios

### Scenario 1: Simple Asset (No Market Data)

**Use Case:** Value a transmission tower using cost approach only.

```bash
python infrastructure_cost_calculator.py samples/transmission_tower.json
```

**Expected Output:**
- RCN calculation
- Physical depreciation (age/life method)
- No market reconciliation
- Confidence: Medium (no market data)

### Scenario 2: Asset with Comparable Sales

**Use Case:** Value with market validation.

Add to input JSON:
```json
{
  "market_data": {
    "comparable_sales": [
      {
        "sale_price": 180000,
        "asset_type": "Transmission tower",
        "condition": "Good"
      }
    ]
  }
}
```

**Expected Output:**
- Cost approach value
- Market reconciliation
- Variance analysis
- Confidence: High (with market data)

### Scenario 3: Asset with Functional/External Obsolescence

**Use Case:** Asset has design issues or market problems.

```json
{
  "depreciation": {
    "age_years": 20,
    "effective_age_years": 18,
    "economic_life_years": 60,
    "physical_condition": "Good",
    "functional_obsolescence": 75000,     // Design inefficiency
    "external_obsolescence": 150000       // Regulatory changes
  }
}
```

**Expected Output:**
- Total depreciation = Physical + Functional + External
- Breakdown by category
- Severity assessments

## Quick Reference

### Physical Condition Options

- `"Excellent"` - Nearly new condition (~5% depreciation)
- `"Good"` - Well maintained, normal wear (~15% depreciation)
- `"Fair"` - Some deferred maintenance (~35% depreciation)
- `"Poor"` - Significant deferred maintenance (~60% depreciation)
- `"Very Poor"` - Near end of life (~85% depreciation)

### Typical Overhead/Profit Ranges

- **Overhead:** 12-18% (use 15% as default)
- **Profit:** 10-15% (use 12% as default)

### Obsolescence Input

Can be specified as:
- **Dollar amount:** `"functional_obsolescence": 75000`
- **Percentage:** `"functional_obsolescence": 0.10` (10%)

### Economic Life by Asset Type

- **Transmission towers:** 40-60 years
- **Pipelines:** 50-75 years
- **Substations:** 40-60 years
- **Pumping stations:** 30-50 years
- **Access roads:** 20-40 years

## Output Files

### Markdown Report

Complete valuation report with:
- Executive summary
- Asset specifications
- RCN calculation breakdown
- Depreciation analysis
- Market reconciliation (if applicable)
- Valuation conclusion
- Methodology notes

**Location:** `Reports/YYYY-MM-DD_HHMMSS_cost_approach_[asset].md`

### JSON Results (Optional)

Machine-readable results for further processing.

**Generate:**
```bash
python infrastructure_cost_calculator.py input.json --json results.json
```

## Command Line Options

```bash
# Basic run
python infrastructure_cost_calculator.py input.json

# Verbose output (shows all calculations)
python infrastructure_cost_calculator.py input.json --verbose

# Custom output path
python infrastructure_cost_calculator.py input.json \
  --output Reports/2025-11-17_143022_my_report.md

# JSON output
python infrastructure_cost_calculator.py input.json \
  --json results.json

# Both markdown and JSON
python infrastructure_cost_calculator.py input.json \
  --output report.md \
  --json results.json \
  --verbose
```

## Validation Rules

Calculator validates:
- ✓ Required fields present
- ✓ Numeric values non-negative
- ✓ Percentages in 0-1 range
- ✓ Effective age ≤ economic life
- ✓ Physical condition valid
- ✓ Comparable sales structure

**Validation errors stop calculation with clear error messages.**

## Confidence Scoring

Calculator automatically assigns confidence score (0-100):

- **85-100 (Very High):** Strong market data + documented depreciation
- **70-84 (High):** Good market support + reasonable estimates
- **55-69 (Medium-High):** Adequate data or estimates
- **40-54 (Medium):** Limited data or uncertainty
- **25-39 (Low-Medium):** Weak support or verification needed
- **0-24 (Low):** Insufficient data

## Troubleshooting

### Error: "Input validation failed"

**Cause:** Missing required fields or invalid values.

**Fix:** Check error messages for specific issues:
- Ensure all required fields present
- Verify numeric values are positive
- Check percentages are decimals (0.15, not 15)

### Error: "Effective age cannot exceed economic life"

**Cause:** `effective_age_years` > `economic_life_years`

**Fix:** Verify ages are correct. If asset truly exceeds economic life, set `effective_age_years` = `economic_life_years` for 100% depreciation.

### Warning: "Significant variance between age/life and condition methods"

**Cause:** Physical condition assessment doesn't match age-based depreciation (>10% variance).

**Fix:** Review effective age or condition rating. Example:
- Asset is 30 years old (60 year life) = 50% depreciation
- But condition is "Excellent" = ~5% depreciation
- Inconsistency suggests incorrect effective age or condition

### Result: "Market significantly higher than cost"

**Cause:** Market comparable sales >20% higher than depreciated replacement cost (unusual).

**Fix:** Verify:
- Comparable sales are truly comparable
- No special purchaser premiums
- No missing functional/external obsolescence in cost approach

## Examples

### Example 1: New Tower

```json
{
  "asset_type": "Transmission tower",
  "construction_costs": {
    "materials": 200000,
    "labor": 100000,
    "overhead_percentage": 0.15,
    "profit_percentage": 0.12
  },
  "depreciation": {
    "age_years": 2,
    "effective_age_years": 2,
    "economic_life_years": 50,
    "physical_condition": "Excellent",
    "functional_obsolescence": 0,
    "external_obsolescence": 0
  }
}
```

**Result:** Minimal depreciation (~4%), value ≈ RCN

### Example 2: Old Pipeline

```json
{
  "asset_type": "Pipeline",
  "construction_costs": {
    "materials": 5000000,
    "labor": 2500000,
    "overhead_percentage": 0.18,
    "profit_percentage": 0.15
  },
  "depreciation": {
    "age_years": 40,
    "effective_age_years": 45,
    "economic_life_years": 60,
    "physical_condition": "Poor",
    "functional_obsolescence": 200000,
    "external_obsolescence": 300000
  }
}
```

**Result:** High depreciation (75%+), significant obsolescence

### Example 3: Substation with Market Data

```json
{
  "asset_type": "Substation",
  "construction_costs": {
    "materials": 10000000,
    "labor": 5000000,
    "overhead_percentage": 0.16,
    "profit_percentage": 0.14
  },
  "depreciation": {
    "age_years": 25,
    "effective_age_years": 25,
    "economic_life_years": 50,
    "physical_condition": "Good",
    "functional_obsolescence": 0,
    "external_obsolescence": 0
  },
  "market_data": {
    "comparable_sales": [
      {"sale_price": 9500000, "asset_type": "Substation"},
      {"sale_price": 10200000, "asset_type": "Substation"}
    ]
  }
}
```

**Result:** Cost and market reconciled, high confidence

## Testing

```bash
# Run all unit tests
python tests/test_calculator.py

# Test with sample data
python infrastructure_cost_calculator.py samples/transmission_tower.json --verbose
python infrastructure_cost_calculator.py samples/pipeline_segment.json --verbose
python infrastructure_cost_calculator.py samples/substation.json --verbose
```

## Support

See `README.md` for complete documentation.

---

**Quick Start Guide v1.0**
**Last Updated:** 2025-11-17
