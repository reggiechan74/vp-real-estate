# Infrastructure Cost Approach Calculator

Complete modular calculator for infrastructure asset valuation using the cost approach methodology.

## Overview

The cost approach values infrastructure assets based on the principle of substitution: a prudent investor would pay no more for a property than the cost to acquire a substitute property of equivalent utility.

**Formula:**
```
Value = Replacement Cost New (RCN) - Total Depreciation

Where:
  RCN = Direct Costs (Materials + Labor) + Overhead + Profit
  Total Depreciation = Physical + Functional + External Obsolescence
```

## Architecture

### Modular Design

The calculator follows a **thin orchestration layer** architecture with specialized modules:

```
infrastructure_cost_calculator.py (main, <400 lines)
│
├── modules/
│   ├── __init__.py              # Module exports
│   ├── validators.py            # Input validation and schema verification
│   ├── replacement_cost.py      # RCN calculation (materials, labor, overhead, profit)
│   ├── depreciation_analysis.py # Physical, functional, external obsolescence
│   ├── cost_reconciliation.py   # Market reconciliation and confidence scoring
│   └── output_formatters.py     # Report generation and markdown formatting
│
├── samples/
│   ├── transmission_tower.json  # 500kV transmission tower (with market data)
│   ├── pipeline_segment.json    # 36" pipeline, 5.5km (no market data)
│   └── substation.json          # 230/115kV substation (limited market data)
│
└── Shared_Utils/                # Imported from parent project
    ├── financial_utils.py       # NPV, IRR, amortization (not used yet)
    └── report_utils.py          # Timestamps, markdown tables, headers
```

## Usage

### Command Line

```bash
# Basic calculation
python infrastructure_cost_calculator.py samples/transmission_tower.json

# With verbose output
python infrastructure_cost_calculator.py samples/transmission_tower.json --verbose

# Custom output path with timestamp
python infrastructure_cost_calculator.py samples/transmission_tower.json \
  --output Reports/2025-11-17_143022_tower_valuation.md \
  --verbose

# JSON output for further processing
python infrastructure_cost_calculator.py samples/transmission_tower.json \
  --json results.json \
  --verbose
```

### Python API

```python
import json
from infrastructure_cost_calculator import calculate_infrastructure_cost
from modules.output_formatters import format_cost_report

# Load input data
with open('samples/transmission_tower.json') as f:
    data = json.load(f)

# Calculate
results = calculate_infrastructure_cost(data, verbose=True)

# Generate report
report = format_cost_report(
    results['input_data'],
    results['rcn_results'],
    results['physical_depreciation'],
    results['functional_obsolescence'],
    results['external_obsolescence'],
    results['total_depreciation'],
    results['reconciliation']
)

# Access results
print(f"RCN: ${results['rcn_results']['replacement_cost_new']:,.2f}")
print(f"Depreciated Cost: ${results['total_depreciation']['depreciated_replacement_cost']:,.2f}")
print(f"Reconciled Value: ${results['reconciliation']['reconciled_value']:,.2f}")
print(f"Confidence: {results['confidence']['rating']}")
```

## Input Format

### JSON Schema

```json
{
  "asset_type": "Transmission tower | Pipeline | Substation | Other infrastructure",

  "specifications": {
    "voltage": "500kV",
    "height_meters": 45,
    "foundation_type": "Caisson",
    "location": "Rural Ontario",
    "installation_year": 2010
  },

  "construction_costs": {
    "materials": 150000,
    "labor": 80000,
    "overhead_percentage": 0.15,     // 15% (typical range: 12-18%)
    "profit_percentage": 0.12        // 12% (typical range: 10-15%)
  },

  "depreciation": {
    "age_years": 15,                 // Actual age
    "effective_age_years": 12,       // Age reflecting condition
    "economic_life_years": 50,       // Total expected life
    "physical_condition": "Good",    // Excellent | Good | Fair | Poor | Very Poor
    "functional_obsolescence": 0,    // Dollar amount or percentage (0-1)
    "external_obsolescence": 0       // Dollar amount or percentage (0-1)
  },

  "market_data": {                   // Optional
    "comparable_sales": [
      {
        "sale_price": 180000,
        "asset_type": "Transmission tower",
        "sale_date": "2024-06-15",
        "location": "Southwestern Ontario",
        "condition": "Good",
        "notes": "Similar 500kV tower, 14 years old"
      }
    ]
  }
}
```

### Required Fields

**Minimum required:**
- `asset_type`
- `construction_costs` (materials, labor, overhead_percentage, profit_percentage)
- `depreciation` (age_years, effective_age_years, economic_life_years)

**Optional:**
- `specifications` - Asset details for documentation
- `market_data` - Comparable sales for reconciliation
- `physical_condition` - Defaults to 'Good' if not provided
- `functional_obsolescence` - Defaults to 0
- `external_obsolescence` - Defaults to 0

## Calculation Methodology

### 1. Replacement Cost New (RCN)

**Direct Costs:**
- Materials cost
- Labor cost
- Sum = Direct Costs

**Indirect Costs:**
- Overhead = Direct Costs × Overhead % (typically 12-18%)
- Profit = (Direct Costs + Overhead) × Profit % (typically 10-15%)

**Total RCN:**
```
RCN = Materials + Labor + Overhead + Profit
```

**Example:**
```
Materials:     $150,000
Labor:         $ 80,000
Direct Costs:  $230,000

Overhead (15%): $ 34,500
Subtotal:       $264,500

Profit (12%):   $ 31,740
RCN:            $296,240
```

### 2. Physical Depreciation

**Age/Life Method (Primary):**
```
Physical Depreciation = (Effective Age ÷ Economic Life) × RCN
Remaining Life = Economic Life - Effective Age
```

**Condition Validation:**
- Excellent: ~5% depreciation
- Good: ~15% depreciation
- Fair: ~35% depreciation
- Poor: ~60% depreciation
- Very Poor: ~85% depreciation

System flags significant variance (>10%) between age/life and condition methods for review.

**Example:**
```
Effective Age:  12 years
Economic Life:  50 years
Remaining Life: 38 years (76% remaining)

Depreciation Rate: 12 ÷ 50 = 24%
Physical Depreciation: $296,240 × 24% = $71,098
```

### 3. Functional Obsolescence

Reflects design inefficiency, excess capacity, or technological obsolescence.

**Severity Levels:**
- None: 0%
- Minor: <5% (slight excess capacity, minor inefficiencies)
- Moderate: 5-15% (inefficient design, outdated but functional)
- Substantial: 15-30% (major design limitations, obsolete technology)
- Severe: >30% (fundamentally flawed design, unsupported technology)

**Input:** Dollar amount or percentage (0-1)

### 4. External Obsolescence

Reflects market conditions, regulatory changes, economic factors, or location issues.

**Severity Levels:**
- None: 0%
- Minor: <5% (minor regulatory changes, temporary market softness)
- Moderate: 5-15% (new regulations, declining demand)
- Substantial: 15-30% (major restrictions, significant market decline)
- Severe: >30% (regulatory prohibition, market collapse, stranded asset)

**Input:** Dollar amount or percentage (0-1)

### 5. Total Depreciation

```
Total Depreciation = Physical + Functional + External
Depreciated Replacement Cost = RCN - Total Depreciation
```

**Breakdown Analysis:**
- Physical %: Physical ÷ Total × 100
- Functional %: Functional ÷ Total × 100
- External %: External ÷ Total × 100

### 6. Market Reconciliation

When comparable sales are available, reconciles cost approach with market evidence.

**Reconciliation Rules:**

**Close Agreement (<10% variance):**
- Reconciled = Average of cost and market
- Confidence: High
- Method: "Average of cost and market (close agreement)"

**Cost High (>20% over market):**
- Reconciled = Market × 1.05 (slight weight to cost)
- Confidence: Medium
- Method: "Market approach emphasized (cost appears high)"
- Note: Consider additional functional/external obsolescence

**Market High (>20% over cost):**
- Reconciled = Weighted average (verify market data quality)
- Confidence: Low
- Method: "Weighted average (verify market data quality)"
- Note: Unusual - verify comparable quality and special purchaser

**Moderate Variance (10-20%):**
- Reconciled = 60% market + 40% cost
- Confidence: Medium-High
- Method: "Weighted average (60% market, 40% cost)"

### 7. Confidence Scoring

Confidence score (0-100) based on:

**Market Data (+/- 20 points):**
- 5+ comparables: +20 (Strong)
- 3-4 comparables: +15 (Good)
- 1-2 comparables: +10 (Limited)
- 0 comparables: -15 (None)

**Depreciation Quality (+/- 15 points):**
- Condition documented (Excellent/Good/Fair): +10
- Condition poor but documented: +5
- Condition not documented: -5

**Age/Life Reasonableness (+/- 10 points):**
- Age/life ratio 0-80%: +10 (Reasonable)
- Age/life ratio >80%: 0 (Questionable)

**Obsolescence Documentation (+5 points):**
- Functional or external documented: +5

**Rating Scale:**
- 85-100: Very High
- 70-84: High
- 55-69: Medium-High
- 40-54: Medium
- 25-39: Low-Medium
- 0-24: Low

## Output

### Markdown Report

Comprehensive report includes:

1. **Executive Summary**
   - RCN, total depreciation, depreciated cost
   - Market reconciliation (if available)
   - Confidence level and notes

2. **Asset Information**
   - Asset type and specifications

3. **Replacement Cost New**
   - Detailed breakdown table
   - Step-by-step calculation

4. **Depreciation Analysis**
   - Physical depreciation (age/life + condition)
   - Functional obsolescence (severity + examples)
   - External obsolescence (severity + examples)
   - Total depreciation summary table

5. **Market Reconciliation**
   - Market statistics (mean, median, range, std dev)
   - Comparable sales detail
   - Variance analysis
   - Reconciliation method and confidence

6. **Valuation Conclusion**
   - Cost approach summary
   - Final reconciled value
   - Confidence level

7. **Methodology Notes**
   - Cost approach principles
   - Formula documentation

### JSON Results

Complete results dictionary:
```json
{
  "input_data": {...},
  "rcn_results": {
    "materials": 150000,
    "labor": 80000,
    "direct_costs": 230000,
    "overhead": 34500,
    "overhead_percentage": 0.15,
    "subtotal": 264500,
    "profit": 31740,
    "profit_percentage": 0.12,
    "replacement_cost_new": 296240
  },
  "physical_depreciation": {...},
  "functional_obsolescence": {...},
  "external_obsolescence": {...},
  "total_depreciation": {...},
  "reconciliation": {...},
  "confidence": {...},
  "timestamp": "2025-11-17_143022"
}
```

## Examples

### Example 1: Transmission Tower (with market data)

**Input:**
- Asset: 500kV transmission tower, 15 years old
- RCN: $296,240
- Depreciation: 24% physical only
- Market: 3 comparable sales ($172k - $195k)

**Output:**
- Depreciated Cost: $225,142
- Market Median: $180,000
- Variance: +25% (cost higher)
- Reconciled Value: $189,000
- Confidence: 85/100 (Very High)

### Example 2: Pipeline (no market data)

**Input:**
- Asset: 36" pipeline, 5.5km, 20 years old
- RCN: $7,192,100
- Depreciation: 30% physical + $75k functional + $150k external
- Market: No comparables

**Output:**
- Total Depreciation: $2,382,630 (33%)
- Depreciated Cost: $4,809,470
- Reconciled Value: $4,809,470 (cost only)
- Confidence: 50/100 (Medium)

### Example 3: Substation (high depreciation)

**Input:**
- Asset: 230/115kV substation, 30 years old
- RCN: $16,530,000
- Depreciation: 70% physical + $500k functional + $250k external
- Market: 2 comparable sales ($6.8M - $7.5M)

**Output:**
- Total Depreciation: $12,321,000 (75%)
- Depreciated Cost: $4,209,000
- Market Median: $7,150,000
- Variance: -41% (cost lower - unusual)
- Reconciled Value: $5,889,950 (weighted)
- Confidence: 40/100 (Low - verify market data)

## Module Details

### validators.py

**Functions:**
- `validate_input(data)` - Complete input validation
- `validate_construction_costs(costs)` - Cost data validation
- `validate_depreciation_data(depreciation)` - Depreciation validation
- `validate_market_data(market_data)` - Comparable sales validation
- `validate_specifications(specs)` - Specifications validation

**Validation Rules:**
- Required fields present
- Numeric values non-negative
- Percentages in 0-1 range
- Effective age ≤ economic life
- Physical condition in valid set
- Comparable sales have required fields

### replacement_cost.py

**Functions:**
- `calculate_replacement_cost_new(costs)` - Core RCN calculation
- `calculate_unit_rcn(total, quantity, unit)` - Unit cost calculation
- `adjust_rcn_for_inflation(base, base_year, current_year, rate)` - Inflation adjustment
- `calculate_rcn_with_premium(base, premium_pct, reason)` - Premium for special circumstances

**Components:**
- Direct costs (materials + labor)
- Overhead (12-18% typical)
- Profit (10-15% typical)

### depreciation_analysis.py

**Functions:**
- `calculate_physical_depreciation(data, rcn)` - Age/life + condition methods
- `calculate_functional_obsolescence(value, rcn, specs)` - Design/capacity/technology
- `calculate_external_obsolescence(value, rcn, market)` - Market/regulatory/economic
- `calculate_total_depreciation(physical, functional, external, rcn)` - Combined analysis

**Methods:**
- Physical: Age/life primary, condition validation
- Functional: Severity classification (None to Severe)
- External: Impact classification (None to Severe)
- Flags significant variances for review

### cost_reconciliation.py

**Functions:**
- `reconcile_with_market(depreciated_cost, market_data, asset_type)` - Market reconciliation
- `calculate_confidence_score(depreciated_cost, market_data, depreciation)` - Confidence assessment

**Logic:**
- No market data: Cost approach only (Medium confidence)
- Close agreement: Average (High confidence)
- Cost high: Market emphasized (Medium confidence)
- Market high: Verify quality (Low confidence)
- Moderate variance: Weighted average (Medium-High confidence)

### output_formatters.py

**Functions:**
- `format_cost_report(...)` - Complete markdown report
- `format_summary_table(results)` - One-line summary table
- Multiple private formatting functions for sections

**Features:**
- Professional markdown formatting
- Detailed calculation breakdowns
- Market statistics and comp tables
- Methodology documentation

## Integration with Shared_Utils

**Current Usage:**
```python
from Shared_Utils.report_utils import (
    eastern_timestamp,           # Eastern Time timestamps (YYYY-MM-DD_HHMMSS)
    format_markdown_table,       # Professional markdown tables
    generate_document_header     # Standard report headers
)
```

**Future Integration Opportunities:**
```python
from Shared_Utils.financial_utils import (
    npv,                         # For multi-period income analysis
    irr,                         # For investment return analysis
    descriptive_statistics       # For comparable sales analysis
)
```

## Testing

### Test Samples

Three comprehensive test samples included:

**1. transmission_tower.json**
- 500kV tower, 15 years old, Good condition
- RCN: $296,240
- Physical depreciation only (24%)
- 3 comparable sales (market reconciliation)
- Tests: Complete workflow with market data

**2. pipeline_segment.json**
- 36" pipeline, 5.5km, 20 years old
- RCN: $7,192,100
- Physical (30%) + functional ($75k) + external ($150k)
- No comparables
- Tests: Cost approach only workflow

**3. substation.json**
- 230/115kV, 30 years old, Fair condition
- RCN: $16,530,000
- High depreciation (75%)
- Limited market data (2 comparables)
- Tests: High depreciation + market variance scenarios

### Run Tests

```bash
# Test all samples
python infrastructure_cost_calculator.py samples/transmission_tower.json --verbose
python infrastructure_cost_calculator.py samples/pipeline_segment.json --verbose
python infrastructure_cost_calculator.py samples/substation.json --verbose

# Test JSON output
python infrastructure_cost_calculator.py samples/transmission_tower.json \
  --json test_results.json

# Verify output format
cat test_results.json | python -m json.tool
```

## File Naming Convention

**Reports MUST use timestamp prefix (Eastern Time):**
```
YYYY-MM-DD_HHMMSS_cost_approach_[asset_type].md

Example: 2025-11-17_143022_cost_approach_transmission_tower.md
```

Auto-generated when using `--output` without path or when path is not specified.

## Dependencies

```
Python Standard Library:
- json, sys, os, argparse, typing

Third-party:
- None (uses only standard library + project Shared_Utils)

Project Dependencies:
- Shared_Utils/report_utils.py (timestamps, markdown tables, headers)
- Shared_Utils/financial_utils.py (available but not yet used)
```

## Future Enhancements

**Planned Features:**

1. **Income Approach Integration**
   - Capitalize rental income from easements
   - NPV of revenue streams
   - Cross-validate with cost approach

2. **Inflation Adjustment**
   - Historical cost indexing
   - Construction cost indices by region
   - Time-adjusted RCN

3. **Unit Cost Analysis**
   - Per-meter, per-tower, per-MVA costs
   - Portfolio benchmarking
   - Bulk valuation capabilities

4. **Advanced Market Analysis**
   - Regression analysis of comparables
   - Market trending
   - Geographic adjustments

5. **Sensitivity Analysis**
   - Depreciation rate scenarios
   - Economic life variations
   - Discount rate sensitivity

## License

Part of the lease-abstract project infrastructure valuation toolkit.

---

**Generated:** 2025-11-17
**Author:** Claude Code
**Version:** 1.0.0
