# Income Approach Land Valuation - Quick Start Guide

## 1. Run a Sample Calculation (30 seconds)

```bash
cd .claude/skills/income-approach-expert

# Telecom tower site example
python land_capitalization_calculator.py \
  samples/telecom_tower_site_input.json \
  --verbose \
  --report

# Result: $110,000 land value
# Report: Reports/2025-11-16_HHMMSS_income_approach_telecom_tower_site.md
```

## 2. Create Your Input File (5 minutes)

**Minimum Required:**
```json
{
  "site_type": "Your Site Description",
  "land_rent": {
    "annual_rent": 12000,
    "lease_term": 20,
    "escalations": "Description"
  },
  "market_data": {
    "comparable_rents": [
      {"location": "Comp 1", "annual_rent": 10000}
    ],
    "cap_rate_range": {"low": 0.06, "high": 0.09},
    "comparable_sales": [
      {"location": "Sale 1", "sale_price": 150000, "noi": 10500}
    ]
  },
  "operating_expenses": {
    "property_tax": 2000,
    "insurance": 800,
    "maintenance": 1200
  }
}
```

**Full Featured (with all optional data):**
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
      {"location": "Comp 1", "annual_rent": 10000},
      {"location": "Comp 2", "annual_rent": 14000}
    ],
    "cap_rate_range": {"low": 0.06, "high": 0.09},
    "comparable_sales": [
      {"location": "Sale 1", "sale_price": 150000, "noi": 10500},
      {"location": "Sale 2", "sale_price": 180000, "noi": 13500}
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

## 3. Run Your Calculation

```bash
# Generate report only
python land_capitalization_calculator.py your_input.json --report

# Save JSON + generate report
python land_capitalization_calculator.py your_input.json \
  --output results.json \
  --report \
  --verbose
```

## 4. Understand the Output

### Console Output (--verbose)
```
============================================================
INCOME APPROACH LAND VALUATION CALCULATOR
============================================================

[1/5] Analyzing market rent...
  ✓ Concluded market rent: $12,000.00
  ✓ Based on 4 comparables

[2/5] Selecting capitalization rate...
  ✓ Concluded cap rate: 7.27%
  ✓ Market range: 6.00% - 9.00%

[3/5] Calculating Net Operating Income...
  ✓ Market rent: $12,000.00
  ✓ Operating expenses: $4,000.00
  ✓ NOI: $8,000.00

[4/5] Calculating land value by income approach...
  ✓ Income approach value: $110,000.00

[5/5] Reconciling with sales comparison approach...
  ✓ Final concluded value: $110,000.00
```

### JSON Output (results.json)
```json
{
  "final_concluded_value": 110000,
  "income_approach_value": 110000,
  "market_rent_analysis": {
    "concluded_market_rent": 12000
  },
  "cap_rate_analysis": {
    "concluded_cap_rate": 0.0727
  },
  "noi_calculation": {
    "noi": 8000
  }
}
```

### Markdown Report
- Executive Summary with final value
- Market Rent Analysis (comparables table)
- Cap Rate Selection (3 methods)
- NOI Calculation
- Land Value by Income Approach
- Reconciliation with Sales Comparison
- Sensitivity Analysis (±0.5% cap rate)

## 5. Common Use Cases

### Telecom Tower Site
```bash
python land_capitalization_calculator.py \
  samples/telecom_tower_site_input.json \
  --report
```

### Commercial Ground Lease
```bash
python land_capitalization_calculator.py \
  samples/simple_land_lease_input.json \
  --report
```

### Pipeline/Transmission Easement
```json
{
  "site_type": "Pipeline Easement",
  "land_rent": {
    "annual_rent": 5000,
    "lease_term": 30,
    "escalations": "CPI annual"
  },
  "market_data": {
    "comparable_rents": [
      {"location": "Similar pipeline 1", "annual_rent": 4800},
      {"location": "Similar pipeline 2", "annual_rent": 5200}
    ],
    "cap_rate_range": {"low": 0.07, "high": 0.10},
    "comparable_sales": [
      {"location": "Pipeline ROW sale", "sale_price": 60000, "noi": 4500}
    ]
  },
  "operating_expenses": {
    "property_tax": 500,
    "insurance": 200,
    "maintenance": 300
  }
}
```

## 6. Troubleshooting

### Error: "Missing required field: X"
**Solution:** Check input JSON has all required fields (see Section 2)

### Error: "annual_rent must be positive"
**Solution:** Ensure all numeric values are positive numbers

### Error: "cap_rate_range.low must be less than high"
**Solution:** Swap low and high values in cap_rate_range

### Warning: "Income and sales differ by >20%"
**Solution:** Review comparable sales data or investigate market variance

## 7. Next Steps

- **Read full documentation:** See `README.md`
- **Run tests:** `python tests/test_land_capitalization_calculator.py`
- **Review sample reports:** Check `Reports/` directory
- **Explore modules:** See `modules/` for calculation details

## 8. Getting Help

```bash
# Display help
python land_capitalization_calculator.py --help

# Run with verbose output to see calculation steps
python land_capitalization_calculator.py input.json --verbose

# Check input validation
python -c "
import json
from modules import validate_input_data

with open('your_input.json') as f:
    data = json.load(f)

validate_input_data(data)
print('✓ Input validation passed')
"
```

---

**Total Time:** 10 minutes from start to finished report

**Support:** See `README.md` for full documentation
