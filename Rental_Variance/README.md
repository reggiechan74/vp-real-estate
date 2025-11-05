# Rental Variance Analysis

Decompose rental revenue variances into rate, area, and term components for commercial lease portfolio analysis.

## Overview

This module performs three-way variance decomposition to analyze the difference between budgeted and actual rental revenue. Based on proven Excel methodology, it breaks down total variance into its constituent parts:

1. **Rate Variance** - Impact of rental rate changes ($/sf/year)
2. **Area Variance** - Impact of leased area changes (square feet)
3. **Term Variance** - Impact of lease timing changes (months)

## Theoretical Foundation

### Core Formula

```
Total Variance = Actual Revenue - Budgeted Revenue
               = (A × B × C) - (D × E × F)

Where:
  A = Actual Rate ($/sf/year)
  B = Actual Area (sf)
  C = Actual Term (months)
  D = Budgeted Rate ($/sf/year)
  E = Budgeted Area (sf)
  F = Budgeted Term (months)
```

### Variance Decomposition

```
Rate Variance = (B × C) × (A - D)
              = Actual Area × Actual Term × Rate Difference

Area Variance = (C × D) × (B - E)
              = Budget Rate × Actual Term × Area Difference

Term Variance = (D × E) × (C - F)
              = Budget Rate × Budget Area × Term Difference
```

### Mathematical Proof

```
Total = (BC)(A-D) + (CD)(B-E) + (DE)(C-F)
      = ABC - BCD + BCD - CDE + CDE - DEF
      = ABC - DEF ✓
```

## Usage

### Command Line

```bash
# Basic usage
python3 rental_variance_calculator.py input.json

# With output file
python3 rental_variance_calculator.py input.json -o results.json

# Verbose mode (detailed tenant breakdown)
python3 rental_variance_calculator.py input.json -v
```

### Slash Command

```bash
# From Excel/CSV file
/rental-variance /path/to/variance_data.xlsx

# Manual input (prompts for data)
/rental-variance

# With specific period
/rental-variance /path/to/data.csv 2024-12-31
```

## Input Format

JSON file structure:

```json
{
  "analysis_date": "2004-12-31",
  "period_start": "2004-01-01",
  "period_end": "2004-12-31",
  "period_months": 12,
  "property_info": {
    "property_name": "Sample Property",
    "total_gla_sf": 6400.0
  },
  "variance_items": [
    {
      "tenant_name": "Tenant A",
      "unit_number": "Unit 101",
      "actual": {
        "start_date": "2004-01-01",
        "end_date": "2007-12-31",
        "term_months": 12.0,
        "rate_psf_year": 11.0,
        "area_sf": 900.0
      },
      "budget": {
        "start_date": "2004-02-01",
        "end_date": "2005-12-31",
        "term_months": 11.0,
        "rate_psf_year": 10.0,
        "area_sf": 1000.0
      },
      "manual_adjustment": 0.0,
      "notes": "Optional notes about this variance"
    }
  ],
  "notes": "Overall analysis notes"
}
```

### Important Data Requirements

- **Rates**: Annual $/sf/year (not monthly)
- **Terms**: Months (including partial months)
- **Areas**: Square feet
- **Dates**: ISO format (YYYY-MM-DD)
- **Manual Adjustments**: Use 0.0 if none

## Output Format

The calculator produces:

1. **Console Output**: Formatted summary with reconciliation
2. **JSON Results**: Detailed variance calculations by tenant
3. **Markdown Report** (via slash command): Comprehensive analysis document

### Sample Output

```
================================================================================
RENTAL VARIANCE ANALYSIS SUMMARY
================================================================================

Property: Sample Property - From Excel Spreadsheet
Period: 2004-01-01 to 2004-12-31 (12 months)

--------------------------------------------------------------------------------
REVENUE SUMMARY
--------------------------------------------------------------------------------
Budget Revenue:        $      21,633.33
Actual Revenue:        $      19,983.33
Total Variance:        $      -1,650.00  (Unfavorable)

--------------------------------------------------------------------------------
VARIANCE DECOMPOSITION
--------------------------------------------------------------------------------
Rate Variance:         $        -183.33  ( 11.1%)
Area Variance:         $       4,166.67  (252.5%)
Term Variance:         $      -5,633.33  (341.4%)
────────────────────────────────────────────────────────────────────────────────
Total (Calculated):    $      -1,650.00

--------------------------------------------------------------------------------
RECONCILIATION CHECK
--------------------------------------------------------------------------------
Sum of Components:     $      -1,650.00
Direct Variance:       $      -1,650.00
Difference:            $           0.00  ✓ RECONCILED
```

## Sample Data

Included sample files based on the original Excel spreadsheet implementation:

- `sample_variance_input.json` - 4 tenant scenarios covering various variance patterns
- `sample_variance_results.json` - Expected calculation results

### Test the Calculator

```bash
cd /workspaces/lease-abstract
python3 Rental_Variance/rental_variance_calculator.py \
  Rental_Variance/sample_variance_input.json \
  -o test_results.json -v
```

## Excel Spreadsheet Source

This implementation is based on a commercial real estate variance analysis spreadsheet (`Rental Variance Analysis.xlsx`) that uses the following formulas:

**Area Variance (Excel)**:
```excel
=($L9*N9/12*$E9)
```

**Rate Variance (Excel)**:
```excel
=(O9/12*$J9*$E9)
```

**Term Variance (Excel)**:
```excel
=($K9*N9/12*$I9)
```

The Python implementation produces **identical results** to the Excel formulas.

## Key Features

✅ **Period-Aware Calculations** - Only counts months within the analysis period
✅ **Three-Way Decomposition** - Isolates rate, area, and term effects
✅ **Manual Adjustments** - Support for lease admin overrides
✅ **Reconciliation Checks** - Validates variance components sum correctly
✅ **Flexible Input** - Excel, CSV, PDF lease documents, or manual entry
✅ **Professional Reports** - Comprehensive markdown reports with actionable insights

## Interpretation Guide

### Variance Signs

**Negative Variance** (Unfavorable - Actual < Budget):
- Rate variance < 0: Actual rate lower than budgeted
- Area variance < 0: Actual area less than budgeted
- Term variance < 0: Actual term shorter than budgeted

**Positive Variance** (Favorable - Actual > Budget):
- Rate variance > 0: Actual rate higher than budgeted
- Area variance > 0: Actual area more than budgeted
- Term variance > 0: Actual term longer than budgeted

### Common Scenarios

**Scenario 1: Rate Increase Offset by Area Decrease**
- Large positive rate variance (favorable)
- Large negative area variance (unfavorable)
- Net variance may be near zero

**Scenario 2: Early Termination**
- Negative term variance (unfavorable)
- Dominates other variance components
- Check lease default provisions

**Scenario 3: Late Commencement**
- Negative term variance (unfavorable)
- Review lease commencement conditions
- Consider free rent periods

## Applications

1. **Budget vs Actual Analysis** - Monthly/quarterly variance reporting
2. **Lease Negotiation Impact** - Quantify negotiation outcomes
3. **Portfolio Performance** - Track leasing trends over time
4. **Forecasting Refinement** - Improve future budget accuracy
5. **Asset Management** - Identify underperforming properties

## Dependencies

- Python 3.6+
- No external dependencies (uses only standard library)

## References

- Original Excel implementation: `Rental Variance Analysis.xlsx`
- Slash command definition: `.claude/commands/Financial_Analysis/rental-variance.md`
- Sample images: `rentaldecomp.jpg`, `first_tenant*.png`

## Authors

Based on commercial real estate best practices and Excel variance analysis methodology.

## License

Part of the Commercial Real Estate Lease Analysis Toolkit.
