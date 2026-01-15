---
description: Value permanent or temporary easements using percentage of fee (5-35%), income capitalization, and before/after methods - for utility transmission, pipeline, transit corridor, access, and telecom easements
argument-hint: <input-json-path>
allowed-tools: Read, Write, Bash, Edit
---

You are an easement valuation specialist providing comprehensive appraisal analysis for utility transmission lines, pipelines, transit corridors, access easements, and telecom sites. Your task is to value easements using three technical methodologies and reconcile to a supportable value conclusion.

## Purpose

Value easements for infrastructure projects using:

1. **Percentage of Fee Method** - Voltage-based percentages (5-35%) applied to fee simple land value
2. **Income Capitalization Method** - Rental equivalent capitalized to present value
3. **Before/After Comparison Method** - Property value impact analysis

## Input

The user will provide:
- **Input JSON path** (REQUIRED) - Path to easement valuation input file

**Arguments**: {{args}}

**Example:**
```
/easement-valuation /workspaces/lease-abstract/.claude/skills/easement-valuation-methods/sample_500kv_transmission.json
/easement-valuation /path/to/pipeline_easement_input.json --output /path/to/results.json
```

## Input File Format

Create JSON file with this structure:

```json
{
  "property": {
    "address": "Legal description or municipal address",
    "total_acres": 250,
    "fee_simple_value": 8750000,
    "zoning": "Agricultural",
    "highest_and_best_use": "Cash crop farming"
  },
  "easement": {
    "type": "utility_transmission",
    "voltage_kv": 500,
    "area_acres": 4.0,
    "width_meters": 80,
    "term": "perpetual",
    "restrictions": [
      "no_buildings",
      "no_trees",
      "height_restrictions"
    ],
    "hbu_impact": "moderate",
    "easement_rent_factor": 0.40
  },
  "market_parameters": {
    "cap_rate": 0.07,
    "annual_rent_per_acre": 250
  }
}
```

### Easement Types

- `utility_transmission` - Electric transmission lines (voltage-based percentages)
- `pipeline` - Natural gas, crude oil, petroleum products, water, sewer
- `telecom` - Fiber optic, cell tower sites, antenna easements
- `transit` - Heavy rail, light rail, bus rapid transit corridors
- `access` - Access rights, shared driveways, right-of-way to landlocked parcels

### Voltage-Based Percentages (Transmission Lines)

**Base percentage by voltage:**
- **69kV**: 10-15% (20-30m width)
- **115kV**: 12-18% (30-40m width)
- **230kV**: 15-20% (45-60m width)
- **500kV**: 20-25% (80-100m width)

**Adjustments** (+/- 1-5%):
- Width impact (wider corridors = higher %)
- Restrictions (no buildings, no trees, height limits)
- Term (perpetual vs. temporary)
- Highest and best use impact (precludes development = +8%)

### Restrictions Options

Common restrictions to include in `restrictions` array:
- `no_buildings` - No structures permitted (+2%)
- `no_trees` - Tree removal required (+1.5%)
- `height_restrictions` - Height limitations (+1%)
- `access_limitations` - Restricted property access (+1.5%)
- `excavation_prohibited` - No digging permitted (+1%)

### HBU Impact Levels

Impact to highest and best use:
- `none` - Minimal impact to HBU (-2%)
- `minor` - Some impact but HBU still achievable (0%)
- `moderate` - Moderate impact to HBU (+2%)
- `major` - Significant impact to HBU (+5%)
- `precludes_development` - Prevents development entirely (+8%)

### Term Options

- `perpetual` - No expiry, runs with land (0% adjustment)
- `temporary` - Temporary easement (see `term_years` for adjustment)

If `temporary`, include `term_years`:
- 1-5 years: -8% adjustment
- 6-10 years: -5% adjustment
- 11-25 years: -3% adjustment
- 26+ years: -1% adjustment (approaching perpetual)

## Process

### Step 1: Parse Arguments and Load Input

```python
import json

# Parse arguments
args = {{args}}
if not args or len(args) < 1:
    print("ERROR: Input JSON file path required")
    print("Usage: /easement-valuation <input-json-path> [--output <output-path>]")
    exit(1)

input_file = args[0]
output_file = args[1] if len(args) > 1 and args[1] != '--output' else None

# Read input JSON
with open(input_file, 'r') as f:
    input_data = json.load(f)
```

### Step 2: Run Easement Calculator

Execute the Python calculator:

```bash
cd /workspaces/lease-abstract/.claude/skills/easement-valuation-methods

python3 easement_calculator.py <input-json-path> --output <output-json-path> --verbose
```

**Command Structure:**
- `input-json-path` - Path to input JSON file
- `--output` or `-o` - Path to save results JSON (optional)
- `--verbose` or `-v` - Print detailed output (optional)

**Example:**
```bash
cd /workspaces/lease-abstract/.claude/skills/easement-valuation-methods

python3 easement_calculator.py sample_500kv_transmission.json \
  --output /workspaces/lease-abstract/Reports/easement_valuation_results.json \
  --verbose
```

### Step 3: Parse Calculator Output

The calculator produces:

**Console Summary:**
```
================================================================================
EASEMENT VALUATION SUMMARY
================================================================================
Property: 250 acres agricultural land, Concession Road 5, Wellington County, ON
Easement Type: utility_transmission
Area: 4.00 acres

Methods:
  Percentage of Fee:      $      360,000
  Income Capitalization:  $      114,286
  Before/After:           $      360,000

Reconciled Value:        $      300,000
Value Range:             $      114,286 - $      360,000
================================================================================
```

**JSON Results** (if --output specified):
```json
{
  "valuation_methods": {
    "percentage_of_fee": {
      "method": "Percentage of Fee",
      "base_percentage": 22.5,
      "adjustments": {
        "width": 2.0,
        "restrictions": 5.0,
        "term": 0.0,
        "highest_and_best_use": 2.0
      },
      "final_percentage": 31.5,
      "fee_simple_value_per_acre": 35000,
      "easement_area_acres": 4.0,
      "easement_value": 360000
    },
    "income_capitalization": {
      "annual_rent_per_acre": 250,
      "easement_area_acres": 4.0,
      "annual_rent_gross": 1000,
      "easement_rent_factor": 0.40,
      "adjusted_annual_rent": 400,
      "cap_rate": 0.07,
      "easement_value": 114286
    },
    "before_after": {
      "value_before": 8750000,
      "value_after": 8390000,
      "easement_value": 360000,
      "percentage_loss": 4.11
    }
  },
  "reconciliation": {
    "weights": {
      "percentage_of_fee": 0.50,
      "income_capitalization": 0.30,
      "before_after": 0.20
    },
    "reconciled_value": 300000,
    "value_range": {
      "low": 114286,
      "high": 360000
    }
  }
}
```

### Step 4: Generate Markdown Appraisal Report

Create comprehensive appraisal report in `/workspaces/lease-abstract/Reports/` with filename:
`YYYY-MM-DD_HHMMSS_easement_valuation_[property_identifier].md`

**CRITICAL**: Use Eastern Time timestamp prefix per repository standards.

**Report Structure:**

```markdown
# Easement Valuation Report

**Property:** [Property Address]
**Easement Type:** [Type and Description]
**Appraisal Date:** [Current Date]
**Appraiser:** Claude Code - Easement Valuation Calculator

---

## Executive Summary

**Property Description:**
- Address: [property address]
- Total Area: [X] acres
- Fee Simple Value: $[X,XXX,XXX]
- Zoning: [zoning]
- Highest and Best Use: [HBU description]

**Easement Description:**
- Type: [utility_transmission/pipeline/telecom/transit/access]
- Area: [X.XX] acres
- Width: [XX] meters
- Term: [Perpetual/Temporary - XX years]
- Voltage (if transmission): [XXX] kV

**Valuation Conclusion:**
- **Reconciled Easement Value: $[XXX,XXX]**
- Value Range: $[XXX,XXX] - $[XXX,XXX]
- As Percentage of Fee: [X.X%]

---

## 1. Property Identification

**Legal Description:**
[Legal description or municipal address]

**Physical Characteristics:**
- Total Area: [XXX] acres
- Zoning: [Agricultural/Industrial/Residential]
- Current Use: [Description]
- Highest and Best Use: [Analysis]

**Fee Simple Value:**
- Total Property Value: $[X,XXX,XXX]
- Value Per Acre: $[XX,XXX]
- Valuation Date: [Date]

---

## 2. Easement Description

**Easement Characteristics:**
- Type: [Full description]
- Area Affected: [X.XX] acres ([X.X%] of total property)
- Width: [XX] meters
- Term: [Perpetual/Temporary - XX years]

**Technical Details:**
[For transmission lines:]
- Voltage: [XXX] kV
- Number of Circuits: [X]
- Tower Configuration: [Description]

[For pipelines:]
- Product Type: [Natural gas/Crude oil/etc.]
- Diameter: [XX] inches
- Burial Depth: [X] meters
- Safety Buffer: [XX] meters

**Restrictions:**
- [List each restriction with description]
- [Impact on property use]

**Impact to Highest and Best Use:**
- Impact Level: [None/Minor/Moderate/Major/Precludes Development]
- Analysis: [Description of how easement affects property's HBU]

---

## 3. Valuation Methodology

Three approaches applied:

### 3.1 Percentage of Fee Method

**Base Percentage:**
- Easement Type: [Type]
[If transmission:]
- Voltage: [XXX] kV
- Base Percentage Range: [XX-XX%]
- Selected Base: **[XX.X%]**

**Adjustments:**
| Factor | Adjustment | Reasoning |
|--------|-----------|-----------|
| Width ([XX]m) | +[X.X%] | [Wider/Standard/Narrow] corridor |
| Restrictions | +[X.X%] | [List key restrictions] |
| Term | +/-[X.X%] | [Perpetual/Temporary XX years] |
| HBU Impact | +[X.X%] | [Impact level and description] |
| **Total Adjustments** | **+[X.X%]** | |

**Final Percentage:** [XX.X%]

**Calculation:**
```
Fee Simple Value per Acre:    $[XX,XXX]
Easement Area:                 [X.XX] acres
Final Percentage:              [XX.X%]

Easement Value = $[XX,XXX] × [X.XX] acres × [XX.X%]
               = $[XXX,XXX]
```

**Percentage of Fee Value: $[XXX,XXX]**

### 3.2 Income Capitalization Method

**Rental Equivalent Approach:**

Market rental data:
- Annual Rent per Acre (comparable land): $[XXX]/acre
- Easement Area: [X.XX] acres
- Gross Annual Rent Equivalent: $[X,XXX]

**Easement Adjustment:**
- Easement Rent Factor: [40%] (typical for permanent easements)
- Adjusted Annual Rent: $[XXX]

**Capitalization:**
- Capitalization Rate: [X.X%]
  - Risk-free rate: [X.X%]
  - Risk premium: [X.X%]
  - Perpetual easement adjustment: [X.X%]

**Calculation:**
```
Adjusted Annual Rent:          $[XXX]
Capitalization Rate:           [X.X%]

Easement Value = $[XXX] ÷ [0.0X]
               = $[XXX,XXX]
```

**Income Capitalization Value: $[XXX,XXX]**

### 3.3 Before/After Comparison Method

**Property Value Analysis:**

**Before Easement:**
- Fee Simple Value: $[X,XXX,XXX]
- Highest and Best Use: [Description]

**After Easement:**
- Estimated Value: $[X,XXX,XXX]
- Impact to HBU: [Description]
- Remaining utility: [Analysis]

**Value Impact:**
```
Value Before:                  $[X,XXX,XXX]
Value After:                   $[X,XXX,XXX]

Easement Value = $[X,XXX,XXX] - $[X,XXX,XXX]
               = $[XXX,XXX]
```

**Percentage Loss:** [X.X%] of total property value

**Before/After Value: $[XXX,XXX]**

---

## 4. Reconciliation of Value

**Valuation Methods Summary:**

| Method | Value | Weight | Weighted Value |
|--------|-------|--------|----------------|
| Percentage of Fee | $[XXX,XXX] | 50% | $[XXX,XXX] |
| Income Capitalization | $[XXX,XXX] | 30% | $[XXX,XXX] |
| Before/After | $[XXX,XXX] | 20% | $[XXX,XXX] |
| **Weighted Average** | | | **$[XXX,XXX]** |

**Weighting Rationale:**
- **Percentage of Fee (50%)**: Most reliable method for [easement type], supported by extensive market data and industry standards for [XXX]kV transmission lines / [product type] pipelines.
- **Income Capitalization (30%)**: Provides secondary support based on rental equivalent approach. Market rental data available but less robust than percentage analysis.
- **Before/After (20%)**: Confirmation method based on percentage of fee calculation. Limited paired sales data available for direct market extraction.

**Value Range:**
- Low: $[XXX,XXX]
- High: $[XXX,XXX]
- Spread: $[XXX,XXX] ([XX%])

**Reconciled Value: $[XXX,XXX]**

**Rounded Conclusion: $[XXX,XXX]**

---

## 5. Market Support and Validation

**Voltage-Based Percentage Analysis:**
[For transmission lines:]
- Industry Standard for [XXX]kV: [XX-XX%]
- Reconciled Percentage: [XX.X%]
- Position in Range: [Within/Above/Below] typical range
- Justification: [Explanation of where this falls and why]

**Comparable Easement Transactions:**
[If available:]
| Property | Type | Voltage/Details | Area | % of Fee | $/Acre |
|----------|------|----------------|------|----------|--------|
| Comparable 1 | [Type] | [Details] | [X] ac | [XX%] | $[X,XXX] |
| Comparable 2 | [Type] | [Details] | [X] ac | [XX%] | $[X,XXX] |
| Subject | [Type] | [Details] | [X] ac | [XX%] | $[X,XXX] |

**Market Rent Support:**
- Agricultural land rents: $[XXX]-$[XXX]/acre (comparable area)
- Easement adjustment: [XX-XX%] typical
- Capitalization rates: [X.X-X.X%] for perpetual easements

---

## 6. Conclusion and Certification

**Final Value Conclusion:**

The easement value is concluded at **$[XXX,XXX]**, representing [XX.X%] of the fee simple value of the affected [X.XX] acres, or [X.X%] of the total property value.

This value represents fair market value for a [perpetual/temporary] [easement type] affecting [X.XX] acres of [property type] property as of [date].

**Methodology Compliance:**
- Uniform Standards of Professional Appraisal Practice (USPAP)
- Appraisal Institute Guidelines for Easement Valuation
- International Right of Way Association (IRWA) Best Practices

**Limitations and Assumptions:**
- Fee simple value of $[X,XXX,XXX] is assumed accurate
- Market parameters (cap rate [X.X%], rental rates) based on [source]
- No environmental contamination or adverse conditions assumed
- Easement terms as described in input data
- [Other assumptions]

---

## Appendices

### A. Calculation Summary

```json
[Insert calculator JSON output]
```

### B. Supporting Files

- Input Data: `[path to input JSON]`
- Calculator Output: `[path to output JSON if saved]`
- Calculator Version: 1.0.0

### C. Percentage of Fee Guidelines

**Utility Transmission Lines:**
- 69kV: 10-15% (20-30m width)
- 115kV: 12-18% (30-40m width)
- 230kV: 15-20% (45-60m width)
- 500kV: 20-25% (80-100m width)

**Pipeline Corridors:**
- Natural gas (low pressure): 15-20%
- Natural gas (high pressure): 20-25%
- Crude oil/petroleum: 25-30%
- Hazardous materials: 30%+

**Access Easements:**
- Infrequent access: 5-8%
- Regular access: 8-12%
- Exclusive right-of-way: 12-15%

**Telecom:**
- Fiber optic/cable: 5-10%
- Cell tower sites: Rental income approach preferred

---

**Report Generated:** [Timestamp ET]
**Calculator:** easement_calculator.py v1.0.0
**Framework:** Three-method reconciliation approach
**Skill:** easement-valuation-methods
```

### Step 5: Summary Output

Provide user with:

```
EASEMENT VALUATION COMPLETE

Property: [Address]
Easement: [Type] - [Area] acres

VALUATION RESULTS:
  Percentage of Fee:      $XXX,XXX ([XX.X%])
  Income Capitalization:  $XXX,XXX
  Before/After:           $XXX,XXX

  Reconciled Value:       $XXX,XXX
  Value Range:            $XXX,XXX - $XXX,XXX

FILES CREATED:
  Report: /workspaces/lease-abstract/Reports/YYYY-MM-DD_HHMMSS_easement_valuation_[property].md
  Results: [output JSON path if specified]

METHODOLOGY:
  - Percentage of Fee: [Base XX.X%] + [Adjustments X.X%] = [Final XX.X%]
  - Income Cap: [$XXX/acre rent × X.XX acres × 0.XX factor] ÷ X.X% cap rate
  - Before/After: [$X.XXM before - $X.XXM after]
  - Weighted reconciliation: 50% / 30% / 20%
```

## Workflow

1. **User provides easement input JSON** (property details, easement characteristics, market parameters)
2. **Calculator runs three valuation methods**:
   - Percentage of fee (voltage/type-based with adjustments)
   - Income capitalization (rental equivalent approach)
   - Before/after comparison (value impact analysis)
3. **Reconciles to single value** (weighted: 50% / 30% / 20%)
4. **Generates comprehensive appraisal report** with methodology, calculations, market support

## Example Commands

### 500kV Transmission Line Easement

```bash
/easement-valuation /workspaces/lease-abstract/.claude/skills/easement-valuation-methods/sample_500kv_transmission.json
```

**Input characteristics:**
- Property: 250 acres agricultural, $8.75M value
- Easement: 500kV transmission line
- Area: 4.0 acres
- Width: 80 meters
- Restrictions: No buildings, no trees, height restrictions
- Term: Perpetual

**Expected output:**
- Percentage of Fee: ~$360,000 (31.5% after adjustments)
- Income Cap: ~$114,000 (rental basis)
- Before/After: ~$360,000 (value impact)
- **Reconciled: ~$300,000**

### Pipeline Easement

```bash
/easement-valuation /path/to/pipeline_input.json --output results.json
```

### Access Easement

```bash
/easement-valuation /path/to/access_easement_input.json
```

## Output

**Comprehensive appraisal report includes:**
- Executive summary with reconciled value
- Property and easement description
- Three valuation methods with detailed calculations
- Adjustment analysis and rationale
- Reconciliation with weighting explanation
- Market support and comparable data
- Professional certification language

**JSON results file** (optional) contains:
- All three methods with detailed breakdowns
- Reconciliation weights and value range
- Calculation metadata

## Related Commands

- `/comparable-sales-adjustment` - Paired sales analysis for market extraction
- `/disturbance-damages` - Temporary construction impacts
- `/injurious-affection` - Proximity impacts from infrastructure
- `/severance-damages` - Remainder parcel devaluation

## Related Calculators

- `easement_calculator.py` - This calculator (three methods)
- `comparable_sales_calculator.py` - Market extraction analysis
- `disturbance_damages_calculator.py` - Construction impact valuation

## Related Skills

- `easement-valuation-methods` - Technical expertise on percentage of fee, income cap, before/after methods
- `comparable-sales-adjustment-methodology` - Market extraction from paired sales
- `injurious-affection-assessment` - Proximity impact quantification

## Notes

**Percentage of Fee Standards:**
- Based on IRWA (International Right of Way Association) guidelines
- Voltage-based percentages reflect market extraction from paired sales
- Adjustments reflect property-specific impact factors

**Income Capitalization:**
- Rental equivalent approach for permanent easements
- Easement rent typically 30-50% of fee simple land rent
- Cap rates 4-8% depending on term and risk

**Before/After Method:**
- Requires paired sales analysis or percentage of fee estimation
- Best when comparable properties with/without easements available
- Limited direct market data in many jurisdictions

**Temporary Easements:**
- Short-term (1-5 years) valued as lump-sum disturbance payments
- Not capitalized as perpetual income stream
- Use disturbance damages calculator for construction impacts

Begin the valuation now with the provided input file.
