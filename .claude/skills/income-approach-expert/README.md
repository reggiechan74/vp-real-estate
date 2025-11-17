# Income Approach Land Valuation Calculator

Calculates land value using income capitalization approach with market rent analysis, cap rate selection (market extraction, band of investment, buildup), and reconciliation with sales comparison approach.

## Architecture

**Modular Design:** Thin orchestration layer (<400 lines) with specialized modules

```
land_capitalization_calculator.py   # Main orchestration (<400 lines)
├── modules/
│   ├── __init__.py                 # Package exports
│   ├── validators.py               # Input validation
│   ├── rent_analysis.py            # Market rent analysis
│   ├── cap_rate_selection.py      # Cap rate selection (3 methods)
│   ├── income_reconciliation.py   # Reconciliation with sales comparison
│   └── output_formatters.py       # Report formatting
├── samples/
│   ├── telecom_tower_site_input.json
│   └── simple_land_lease_input.json
└── tests/
    └── test_land_capitalization_calculator.py
```

**Shared Utilities Integration:**
- `Shared_Utils/financial_utils.py` - NPV, IRR calculations
- `Shared_Utils/report_utils.py` - Timestamped reports, markdown formatting

## Features

### 1. Market Rent Analysis
- Comparable rent data processing
- Statistical analysis (mean, median, range)
- Subject rent comparison
- Market rent conclusion with rationale

### 2. Capitalization Rate Selection

**Three Methods:**

1. **Market Extraction** (Primary)
   - Extract cap rates from comparable sales
   - Formula: Cap Rate = NOI ÷ Sale Price
   - Statistical analysis of extracted rates

2. **Band of Investment** (Supporting)
   - Mortgage-equity analysis
   - Formula: (LTV% × Debt Yield) + (Equity% × Equity Yield)
   - Requires financing data in input

3. **Buildup Method** (Supporting)
   - Risk-based cap rate construction
   - Formula: Risk-Free + Liquidity + Inflation + Business Risk
   - Requires risk components in input

### 3. Income Capitalization
- Net Operating Income (NOI) calculation
- Land value by income approach
- Formula: Value = NOI ÷ Cap Rate

### 4. Reconciliation
- Compare income approach vs. sales comparison
- Variance analysis
- Final value conclusion with weighting rationale

### 5. Sensitivity Analysis
- Impact of ±0.5% cap rate changes
- Value variance percentage
- Risk assessment

## Input Structure

```json
{
  "site_type": "Telecom Tower Site",
  "land_rent": {
    "annual_rent": 12000,
    "lease_term": 20,
    "escalations": "3% per 5 years"
  },
  "market_data": {
    "comparable_rents": [
      {
        "location": "Downtown site #1",
        "annual_rent": 10000
      }
    ],
    "cap_rate_range": {
      "low": 0.06,
      "high": 0.09
    },
    "comparable_sales": [
      {
        "location": "Similar site A",
        "sale_price": 150000,
        "noi": 10500
      }
    ],
    "sales_comparison_value": 160000,
    "financing": {
      "ltv": 0.75,
      "debt_yield": 0.055,
      "equity_yield": 0.12
    },
    "risk_components": {
      "risk_free_rate": 0.04,
      "liquidity_premium": 0.01,
      "inflation_premium": 0.02,
      "business_risk": 0.02
    }
  },
  "operating_expenses": {
    "property_tax": 2000,
    "insurance": 800,
    "maintenance": 1200
  }
}
```

## Usage

### Command Line

```bash
# Basic usage
python land_capitalization_calculator.py input.json

# With verbose output
python land_capitalization_calculator.py input.json --verbose

# Generate markdown report
python land_capitalization_calculator.py input.json --report

# Save JSON results
python land_capitalization_calculator.py input.json --output results.json

# All options
python land_capitalization_calculator.py input.json --verbose --report --output results.json
```

### Example

```bash
# Telecom tower site valuation
python land_capitalization_calculator.py \
  samples/telecom_tower_site_input.json \
  --verbose \
  --report

# Output:
# ============================================================
# INCOME APPROACH LAND VALUATION CALCULATOR
# ============================================================
#
# [1/5] Analyzing market rent...
#   ✓ Concluded market rent: $12,000.00
#   ✓ Based on 4 comparables
#
# [2/5] Selecting capitalization rate...
#   ✓ Concluded cap rate: 7.27%
#   ✓ Market range: 6.00% - 9.00%
#
# [3/5] Calculating Net Operating Income...
#   ✓ Market rent: $12,000.00
#   ✓ Operating expenses: $4,000.00
#   ✓ NOI: $8,000.00
#
# [4/5] Calculating land value by income approach...
#   ✓ Income approach value: $110,000.00
#
# [5/5] Reconciling with sales comparison approach...
#   ✓ Final concluded value: $110,000.00
#
# ✓ Report generated: Reports/2025-11-16_195707_income_approach_telecom_tower_site.md
```

## Output

### JSON Results

```json
{
  "site_type": "Telecom Tower Site",
  "valuation_date": "2025-11-16",
  "market_rent_analysis": {
    "concluded_market_rent": 12000,
    "rent_statistics": {
      "mean": 12175,
      "median": 12350,
      "min": 10000,
      "max": 14000
    }
  },
  "cap_rate_analysis": {
    "concluded_cap_rate": 0.0727,
    "market_extraction": {...},
    "band_of_investment": {...},
    "buildup_method": {...}
  },
  "noi_calculation": {
    "gross_income": 12000,
    "total_operating_expenses": 4000,
    "noi": 8000
  },
  "income_approach_value": 110000,
  "reconciliation": {
    "income_approach_value": 110000,
    "sales_comparison_value": 160000,
    "variance_percentage": -31.2,
    "final_value": 110000
  },
  "sensitivity_analysis": [...]
}
```

### Markdown Report

Report includes:
1. **Executive Summary** - Concluded value, key inputs, methodology
2. **Market Rent Analysis** - Comparables table, statistics, conclusion
3. **Capitalization Rate Selection** - All three methods with reconciliation
4. **NOI Calculation** - Income and expense breakdown
5. **Land Value by Income Approach** - Capitalization formula
6. **Reconciliation** - Comparison with sales approach
7. **Sensitivity Analysis** - Cap rate impact table
8. **Assumptions and Limiting Conditions**

**Report Location:** `Reports/YYYY-MM-DD_HHMMSS_income_approach_{site_type}.md`

## Testing

```bash
# Run all unit tests
python tests/test_land_capitalization_calculator.py

# Expected output:
# test_empty_comparable_rents ... ok
# test_invalid_annual_rent ... ok
# test_invalid_cap_rate_range ... ok
# test_valid_input ... ok
# test_rent_statistics ... ok
# test_market_extraction ... ok
# test_band_of_investment ... ok
# test_buildup_method ... ok
# test_noi_calculation ... ok
# test_income_value_calculation ... ok
# test_reconciliation_within_10_percent ... ok
# test_sensitivity_analysis ... ok
# test_full_valuation_process ... ok
#
# Ran 20 tests in 0.058s
# OK
```

## Validation Rules

### Required Fields
- `site_type` - Site description
- `land_rent.annual_rent` - Positive number
- `land_rent.lease_term` - Positive integer
- `market_data.comparable_rents` - At least 1 comparable
- `market_data.cap_rate_range` - Low < High, both 0-1
- `market_data.comparable_sales` - At least 1 sale
- `operating_expenses.property_tax` - Non-negative
- `operating_expenses.insurance` - Non-negative
- `operating_expenses.maintenance` - Non-negative

### Optional Fields
- `land_rent.escalations` - Description only
- `market_data.sales_comparison_value` - For reconciliation
- `market_data.financing` - For band of investment method
- `market_data.risk_components` - For buildup method

## Methodology

### 1. Market Rent Analysis
- If subject rent within comparable range → Use subject rent
- If subject rent outside comparable range → Use market median
- Report variance from market median

### 2. Cap Rate Selection
- **Primary:** Market extraction median
- **Validation:** Must be within cap_rate_range
- **Supporting:** Band of investment and buildup (if data provided)
- Report variance between methods

### 3. Reconciliation Logic
- **Within 10% variance:** Use income approach value
- **10-20% variance:** Use average of both approaches
- **>20% variance:** Use income approach, flag for investigation

### 4. Sensitivity Analysis
- Test: -0.5%, -0.25%, 0%, +0.25%, +0.5% cap rate adjustments
- Show value impact and percentage variance
- Highlight risk exposure

## Example Use Cases

1. **Telecom Tower Sites** - Cell tower land leases with long-term contracts
2. **Commercial Land Leases** - Ground leases for retail/office developments
3. **Industrial Land Leases** - Warehouse and distribution center sites
4. **Agricultural Easements** - Transmission line or pipeline corridors
5. **Parking Lot Leases** - Surface parking ground leases

## Dependencies

```
Python 3.8+
├── json (stdlib)
├── sys (stdlib)
├── os (stdlib)
├── argparse (stdlib)
├── statistics (stdlib)
└── Shared_Utils
    ├── report_utils (eastern_timestamp, format_markdown_table)
    └── financial_utils (optional: npv, irr for extensions)
```

## Error Handling

- **Input Validation:** Comprehensive validation with detailed error messages
- **Calculation Errors:** Zero/negative cap rate detection
- **Missing Data:** Graceful handling of optional fields
- **File I/O:** Clear error messages for missing/invalid files

## Extensibility

**Future Enhancements:**
- Multiple income scenarios (base, upside, downside)
- Lease escalation modeling over time
- Tax impact analysis
- Direct capitalization vs. DCF comparison
- Monte Carlo risk analysis
- Market rent adjustments (size, location, condition)

## License

Part of the Commercial Real Estate Lease Analysis Toolkit
Created: 2025-11-17
Author: Claude Code

---

**Related Tools:**
- `easement_valuation_calculator.py` - Permanent/temporary easement valuation
- `comparable_sales_calculator.py` - Sales comparison approach
- `settlement_analysis_calculator.py` - Settlement vs. hearing analysis
