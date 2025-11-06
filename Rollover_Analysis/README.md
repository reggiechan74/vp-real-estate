# Portfolio Lease Rollover Analysis Calculator

**Version**: 1.0.0
**Date**: 2025-11-06
**Author**: Claude Code

---

## Overview

The Rollover Analysis Calculator provides comprehensive portfolio lease expiration risk analysis with:

- **Expiry Schedule Aggregation** - Lease rollover by year/quarter
- **Concentration Risk Identification** - CRITICAL/HIGH/MODERATE risk flags
- **Renewal Priority Scoring** - 0-1 normalized weighted scoring
- **Scenario Modeling** - Optimistic/Base/Pessimistic with NPV discounting
- **Executive-Ready Reports** - Beautiful markdown with actionable recommendations

---

## Quick Start

### 1. Basic Usage

```bash
# Run analysis and generate JSON results
python rollover_calculator.py rollover_inputs/sample_portfolio.json

# Generate markdown report
python report_generator.py rollover_inputs/sample_portfolio.json
```

### 2. Custom Output Paths

```bash
# Specify custom output path
python rollover_calculator.py portfolio.json results.json
python report_generator.py portfolio.json report.md
```

---

## Input Format

### JSON Structure

```json
{
  "portfolio_name": "ABC Industrial Portfolio",
  "analysis_date": "2025-11-06",
  "leases": [
    {
      "property_address": "123 Main St, City, ST",
      "tenant_name": "Acme Corp",
      "rentable_area_sf": 50000,
      "current_annual_rent": 750000,
      "lease_expiry_date": "2027-06-30",
      "renewal_options": ["2032-06-30"],
      "tenant_credit_rating": "BBB",
      "below_market_pct": -15.5
    }
  ],
  "assumptions": {
    "discount_rate": 0.10,
    "renewal_rate_optimistic": 0.80,
    "renewal_rate_base": 0.65,
    "renewal_rate_pessimistic": 0.50,
    "downtime_months": {
      "optimistic": 1,
      "base": 3,
      "pessimistic": 6
    },
    "market_rent_sf": 16.50,
    "market_rent_growth_annual": 0.025,
    "ti_allowance_sf": 15.00,
    "leasing_commission_pct": 0.05
  }
}
```

### Required Fields

**Per Lease:**
- `property_address` (string) - Property location
- `tenant_name` (string) - Tenant legal name
- `rentable_area_sf` (number) - Rentable square footage
- `current_annual_rent` (number) - Current annual base rent
- `lease_expiry_date` (date) - Lease expiration date (YYYY-MM-DD)
- `renewal_options` (array) - List of renewal option dates
- `tenant_credit_rating` (string) - Credit rating (AAA to D, or NR)
- `below_market_pct` (number) - % below/above market (negative = below market opportunity)

**Portfolio Level:**
- `portfolio_name` (string) - Portfolio identifier
- `analysis_date` (date) - Analysis as-of date (YYYY-MM-DD)
- `assumptions` (object) - Analysis assumptions (all optional, defaults provided)

---

## Priority Scoring Algorithm

### Formula

```
Priority Score = (Rent% × 0.40) + (Urgency × 0.30) + (Below Market × 0.20) + (Credit Risk × 0.10)
```

### Components (0-1 Normalized)

1. **Rent %** (40% weight):
   ```
   Rent% = min(lease_rent / portfolio_rent, 1.0)
   ```
   - Larger leases score higher
   - Capped at 100% to prevent dominance

2. **Urgency** (30% weight):
   ```
   Urgency = 1 - min(months_to_expiry / 24, 1.0)
   ```
   - 24-month window (leases >24 months out score 0)
   - Expiring today = 1.0, 12 months = 0.5, 24+ months = 0.0

3. **Below Market** (20% weight):
   ```
   Below Market = min(abs(below_market_pct) / 20, 1.0)
   ```
   - 20% below market = 1.0 (maximum opportunity)
   - Uses absolute value (both below and above market are opportunities)

4. **Credit Risk** (10% weight):
   ```
   Credit Risk = credit_rating_to_score(rating)
   ```
   - AAA = 0.0 (lowest risk)
   - D = 1.0 (highest risk)
   - NR (Not Rated) = 0.7 (assumes below investment grade)

### Credit Rating Map

| Rating | Score | Category |
|--------|-------|----------|
| AAA | 0.00 | Investment Grade |
| AA+/AA/AA- | 0.05-0.15 | Investment Grade |
| A+/A/A- | 0.15-0.25 | Investment Grade |
| BBB+/BBB/BBB- | 0.35-0.45 | Investment Grade |
| BB+/BB/BB- | 0.55-0.65 | High Yield |
| B+/B/B- | 0.75-0.85 | High Yield |
| CCC/CC/C/D | 0.95-1.00 | Distressed |
| NR | 0.70 | Not Rated |

---

## Scenario Modeling

### Three Scenarios

1. **Optimistic**
   - 80% renewal rate
   - 1 month downtime (even on renewals)
   - Best-case market conditions

2. **Base**
   - 65% renewal rate
   - 3 months downtime
   - Typical market conditions

3. **Pessimistic**
   - 50% renewal rate
   - 6 months downtime
   - Weak market conditions

### NPV Discounting

All NOI impacts are discounted to present value:

```
NPV = Σ (NOI_delta_t / (1 + discount_rate)^t)
```

Default discount rate: 10% annual

### Minimum Downtime

**All leases have minimum 1-month downtime**, even on renewals, to account for:
- Tenant improvements
- Legal documentation
- Move-in coordination

---

## Risk Level Criteria

| Risk Level | Criteria | Flag |
|-----------|----------|------|
| **CRITICAL** | >30% of portfolio (SF or rent) expiring in single year | 🔴 |
| **HIGH** | 20-30% of portfolio expiring | 🟠 |
| **MODERATE** | <20% of portfolio expiring | 🟢 |

---

## Output Files

### 1. JSON Results

**File**: `*_results.json`

Contains:
- Expiry schedule by year
- Priority ranking for all leases
- Scenario analysis results
- All metrics in machine-readable format

### 2. Markdown Report

**File**: `Reports/YYYY-MM-DD_HHMMSS_rollover_analysis_*.md`

Contains:
- Executive summary with key findings
- Expiry schedule table
- Top 10 priority leases
- Scenario comparison
- Recommended actions (immediate vs strategic)
- Methodology documentation

---

## Examples

### Example 1: Simple Analysis

```bash
# Analyze 10-lease portfolio
python rollover_calculator.py my_portfolio.json

# Output: my_portfolio_results.json
```

### Example 2: Full Report

```bash
# Generate executive report
python report_generator.py my_portfolio.json

# Output: Reports/2025-11-06_173000_rollover_analysis_my_portfolio.md
```

### Example 3: Custom Assumptions

Edit JSON input to change assumptions:

```json
{
  "assumptions": {
    "discount_rate": 0.12,  // Higher discount rate (12%)
    "renewal_rate_base": 0.70,  // More optimistic base case
    "downtime_months": {
      "optimistic": 1,
      "base": 2,  // Faster turnaround
      "pessimistic": 4
    }
  }
}
```

---

## Programmatic Usage

### Python API

```python
from rollover_calculator import (
    load_portfolio_from_json,
    calculate_rollover_analysis
)

# Load portfolio
portfolio = load_portfolio_from_json('portfolio.json')

# Run analysis
results = calculate_rollover_analysis(portfolio)

# Access results
print(f"Total leases: {len(results.priority_ranking)}")
print(f"Critical years: {sum(1 for item in results.expiry_schedule if item.risk_level == 'CRITICAL')}")

# Top priority lease
top_lease = results.priority_ranking[0]
print(f"Top priority: {top_lease.lease.tenant_name} (Score: {top_lease.priority_score:.3f})")

# Scenario comparison
for scenario in results.scenarios:
    print(f"{scenario.scenario_name}: NOI Impact = ${scenario.noi_impact_npv:,.0f}")
```

---

## Testing

### Unit Tests

```bash
cd Tests
python -m pytest test_rollover_calculator.py -v
```

### Sample Data

Included sample portfolio with 10 leases demonstrating:
- Critical year concentration (2026: 35% SF)
- Mixed credit ratings (AAA to NR)
- Various expiry dates (2026-2029)
- Below-market opportunities

---

## Dependencies

- Python 3.12+
- Standard library only (no external dependencies)

### Optional

- `pytest` (for running tests)
- `jsonschema` (for JSON validation)

---

## Limitations

1. **No Market Dynamics**: Assumes static market rent and renewal rates
2. **Simplified Downtime**: Uses constant downtime per scenario (doesn't vary by property type)
3. **Credit Risk**: Uses rating as proxy (doesn't incorporate financials, guarantees, etc.)
4. **No Seasonality**: Doesn't account for Q4 lease expiry concentration patterns

---

## Best Practices

1. **Update Regularly**: Run analysis quarterly to track changing risk profile
2. **Validate Assumptions**: Review discount rate, renewal rates, downtime with asset management team
3. **Cross-Reference**: Compare priority scores with property manager assessments
4. **Monitor Triggers**: Set alerts for leases entering 12-month window
5. **Document Decisions**: Save reports with renewal negotiation decisions

---

## Troubleshooting

### Common Errors

**Error: "Invalid rentable area"**
- Cause: Negative or zero rentable_area_sf
- Fix: Ensure all areas are positive numbers

**Error: "Discount rate must be between 0 and 1"**
- Cause: Discount rate entered as percentage (e.g., 10 instead of 0.10)
- Fix: Use decimal format (0.10 for 10%)

**Error: "date data does not match format"**
- Cause: Incorrect date format
- Fix: Use YYYY-MM-DD format (e.g., "2027-06-30")

### Performance

- **Small portfolios** (<50 leases): <1 second
- **Medium portfolios** (50-200 leases): 1-3 seconds
- **Large portfolios** (200+ leases): 3-10 seconds

---

## Support

**GitHub Issues**: https://github.com/reggiechan74/leasing-expert/issues
**Documentation**: See `METHODOLOGY.md` for calculation details

---

## Version History

### v1.0.0 (2025-11-06)
- Initial release
- Expiry schedule aggregation
- Priority scoring with 0-1 normalization
- Scenario modeling with NPV discounting
- Markdown report generation

---

## License

Apache License 2.0 - See LICENSE file for details.
