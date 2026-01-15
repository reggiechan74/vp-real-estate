# Comparable Sales JSON Validator

## Overview

`validate_comparables.py` is a comprehensive validation script designed to verify LLM-extracted comparable sales data against the JSON schema and perform additional quality checks.

**Purpose**: Catch and optionally auto-fix common LLM extraction errors before processing with the comparable sales calculator.

## Features

### ✅ Schema Validation
- Validates against `comparable_sales_input_schema.json`
- Checks required fields are present
- Verifies data types (string, number, boolean, array, object)
- Validates numeric ranges and constraints
- Enforces enum value restrictions

### 🔧 Auto-Fix Capabilities

The validator can automatically correct common LLM extraction issues:

1. **Date Format Normalization**
   - `"03/15/2024"` → `"2024-03-15"`
   - `"January 15, 2025"` → `"2025-01-15"`
   - `"15-01-2025"` → `"2025-01-15"`

2. **Enum Value Normalization**
   - `"Fee Simple"` → `"fee_simple"`
   - `"Industrial"` → `"industrial"`
   - `"Seller VTB"` → `"seller_vtb"`
   - `"LEED Gold"` → `"leed_gold"`

3. **String to Number Conversion**
   - `"5.2"` → `5.2`
   - `"50,000"` → `50000`
   - `"$4,500,000"` → `4500000`

4. **Boolean Conversion**
   - `"true"` → `true`
   - `"Yes"` → `true`
   - `"false"` → `false`
   - `"No"` → `false`

5. **Null Removal**
   - Removes `null` values that cause schema violations

### 📊 Semantic Validation

Beyond schema compliance, the validator checks:

- **Sale dates vs valuation date**: Warns if comparable sale occurred after valuation date
- **Property type consistency**: Warns if industrial-specific fields present on office property (or vice versa)
- **Financing completeness**: Warns if seller VTB financing is missing required fields (market_rate, term_years, loan_amount)

### 🎯 Data Quality Checks

- **Sale price reasonableness**: Flags prices < $100K or > $500M
- **Price per SF analysis**: Warns if < $10/SF or > $1,000/SF
- **Missing recommended parameters**: Suggests optional market parameters that improve accuracy

## Usage

### Basic Validation

```bash
python validate_comparables.py input.json
```

**Output**: Pass/fail status with detailed error messages

### Auto-Fix Common Issues

```bash
python validate_comparables.py input.json --fix --output fixed.json
```

**Output**:
- Corrected JSON saved to `fixed.json`
- Report of all fixes applied
- Remaining errors/warnings (if any)

### Verbose Mode

```bash
python validate_comparables.py input.json --verbose
```

**Output**: Detailed error messages including problematic values

### Custom Schema Location

```bash
python validate_comparables.py input.json --schema /path/to/custom_schema.json
```

## Command-Line Options

| Option | Description |
|--------|-------------|
| `input_file` | Path to JSON file to validate (required) |
| `--schema PATH` | Path to JSON schema file (default: `comparable_sales_input_schema.json`) |
| `--fix` | Attempt to auto-fix common LLM extraction issues |
| `--output PATH` | Path to save corrected JSON (only used with `--fix`) |
| `--verbose` | Show detailed error messages and fix details |

## Exit Codes

- `0`: Validation passed (no errors)
- `1`: Validation failed (errors present)

**Note**: Warnings do not cause validation failure (exit code 0).

## Validation Report

The validator generates a structured report with three sections:

### 1. Auto-Fixes Applied (if `--fix` used)

```
🔧 AUTO-FIXES APPLIED: 10
   • Date format: "03/15/2024" → "2024-03-15"
   • Enum format: "Industrial" → "industrial"
   • String to int: "50,000" → 50000
   ...
```

### 2. Errors (schema violations)

```
ERRORS:
──────────────────────────────────────────────────────────────────────

1. [SCHEMA_VIOLATION] subject_property → topography
   'Level' is not one of ['severely_sloped', 'moderately_sloped', 'gently_sloped', 'level']
   Value: Level
```

### 3. Warnings (quality issues)

```
WARNINGS:
──────────────────────────────────────────────────────────────────────

1. ⚠️  [INCOMPLETE_FINANCING] comparable_sales[1].financing
   Seller VTB financing missing fields: market_rate, term_years, loan_amount
   Value: 789 Elm Street

2. ℹ️  [MISSING_RECOMMENDED] market_parameters
   Recommended parameters missing: location_premium_per_point, lot_adjustment_per_acre
   Value: May result in less accurate adjustments
```

## Error Types

| Type | Severity | Description |
|------|----------|-------------|
| `SCHEMA_VIOLATION` | ERROR | Field violates JSON schema constraints |
| `FUTURE_SALE` | WARNING | Sale date is after valuation date |
| `FIELD_MISMATCH` | WARNING | Property-type specific field on wrong property type |
| `INCOMPLETE_FINANCING` | WARNING | VTB financing missing required fields |
| `SUSPICIOUS_VALUE` | WARNING | Value seems unreasonable (e.g., very high/low price) |
| `MISSING_RECOMMENDED` | INFO | Optional but recommended parameters missing |

## Example Workflow

### Step 1: LLM Extraction

LLM extracts comparable sales data to `llm_extracted.json`:

```json
{
  "subject_property": {
    "address": "123 Main Street",
    "property_type": "Industrial",
    "property_rights": "Fee Simple",
    "lot_size_acres": "5.2"
  },
  "comparable_sales": [...],
  "market_parameters": {
    "appreciation_rate_annual": "3.5",
    "valuation_date": "January 15, 2025",
    "cap_rate": "7.0"
  }
}
```

**Issues**: Capitalized enums, string numbers, non-standard date format

### Step 2: Validate and Fix

```bash
python validate_comparables.py llm_extracted.json --fix --output clean.json --verbose
```

**Output**:
```
======================================================================
COMPARABLE SALES JSON VALIDATION REPORT
======================================================================

⚠️  VALIDATION PASSED WITH WARNINGS - 1 warning(s)

🔧 AUTO-FIXES APPLIED: 5
   • Date format: "January 15, 2025" → "2025-01-15"
   • Enum format: "Industrial" → "industrial"
   • Enum format: "Fee Simple" → "fee_simple"
   • String to float: "5.2" → 5.2
   • String to float: "3.5" → 3.5

──────────────────────────────────────────────────────────────────────
WARNINGS:
──────────────────────────────────────────────────────────────────────

1. ℹ️ [MISSING_RECOMMENDED] market_parameters
   Recommended parameters missing: location_premium_per_point

======================================================================

💾 Corrected JSON saved to: clean.json
```

### Step 3: Run Calculator

```bash
python comparable_sales_calculator.py clean.json --verbose
```

**Result**: Calculator processes clean, schema-compliant JSON.

## Integration with LLM Pipeline

### Python Integration

```python
import json
from validate_comparables import ComparableValidator

# Load LLM-extracted data
with open('llm_output.json') as f:
    llm_data = json.load(f)

# Validate and fix
validator = ComparableValidator()
is_valid, corrected_data = validator.validate(llm_data, fix=True)

# Check results
if is_valid:
    print("✅ Validation passed")
    # Save corrected data
    with open('corrected.json', 'w') as f:
        json.dump(corrected_data, f, indent=2)
else:
    print("❌ Validation failed")
    validator.print_report(verbose=True)

# Always check warnings
if validator.warnings:
    print(f"⚠️  {len(validator.warnings)} warnings present")
    for warning in validator.warnings:
        print(f"  - {warning['message']}")
```

### Bash Pipeline

```bash
#!/bin/bash

# Step 1: LLM extraction (your custom script)
python extract_with_llm.py input.pdf > llm_extracted.json

# Step 2: Validate and fix
python validate_comparables.py llm_extracted.json --fix --output clean.json

# Step 3: Check exit code
if [ $? -eq 0 ]; then
    echo "✅ Validation passed, running calculator..."
    python comparable_sales_calculator.py clean.json --verbose
else
    echo "❌ Validation failed, manual review required"
    exit 1
fi
```

## Common LLM Extraction Errors

Based on real-world LLM extraction patterns, the validator handles:

### 1. Capitalization Issues
- LLMs often capitalize proper nouns: `"Fee Simple"` instead of `"fee_simple"`
- **Fix**: Auto-normalize to lowercase with underscores

### 2. Date Formatting
- LLMs may output natural language dates: `"March 15, 2024"`
- **Fix**: Auto-convert to ISO 8601 format (`YYYY-MM-DD`)

### 3. Numeric Strings
- LLMs sometimes quote numbers: `"5.2"` instead of `5.2`
- LLMs may include formatting: `"$4,500,000"` or `"50,000 SF"`
- **Fix**: Auto-convert to numeric types, removing commas and currency symbols

### 4. Boolean Strings
- LLMs output text booleans: `"true"`, `"Yes"`, `"Y"`
- **Fix**: Auto-convert to JSON booleans (`true`/`false`)

### 5. Incomplete Nested Objects
- LLMs may extract partial financing details for VTB transactions
- **Fix**: Warn user to collect missing fields (market_rate, term_years, loan_amount)

### 6. Property Type Confusion
- LLMs may include industrial fields (clear_height_feet) on office properties
- **Fix**: Warn user of field mismatches (won't auto-delete, preserves data)

## Testing

The repository includes sample files for testing:

```bash
# Test valid industrial sample
python validate_comparables.py sample_industrial_rail_yard.json
# Expected: ✅ VALIDATION PASSED

# Test valid office samples
python validate_comparables.py sample_office_class_a.json
python validate_comparables.py sample_office_class_b.json
python validate_comparables.py sample_office_class_c.json
# Expected: ✅ VALIDATION PASSED (may have INFO warnings)
```

## Limitations

### What the Validator CANNOT Fix

1. **Missing required fields**: Cannot invent data
2. **Nonsensical values**: Cannot determine if "1000 sq ft" should be "10,000 sq ft"
3. **Structural JSON errors**: Cannot fix malformed JSON (use `json.tool` first)
4. **Semantic incorrectness**: Cannot verify if address/price/date match reality

### Manual Review Still Required For

- Suspicious values flagged in warnings
- Missing required fields
- Extremely high/low prices per SF
- Future sale dates
- Incomplete VTB financing details

## Troubleshooting

### "Schema file not found"

**Problem**: `comparable_sales_input_schema.json` not in current directory

**Solution**:
```bash
# Run from the correct directory
cd /path/to/comparable-sales-adjustment-methodology

# Or specify schema path
python validate_comparables.py input.json --schema /path/to/schema.json
```

### "Invalid JSON in input file"

**Problem**: Input file has malformed JSON

**Solution**:
```bash
# Validate JSON syntax first
python -m json.tool input.json

# Fix JSON syntax errors manually, then rerun validator
```

### Auto-fixes not working as expected

**Problem**: Some values still failing validation after `--fix`

**Possible causes**:
1. Value cannot be auto-corrected (e.g., nonsense enum value)
2. Structural issue (wrong data type, e.g., array instead of object)
3. Missing data (validator won't invent values)

**Solution**: Review errors in verbose mode and fix manually

## Performance

- **Typical validation time**: < 100ms for files with 1-10 comparables
- **Memory usage**: Minimal (loads entire JSON into memory)
- **Scalability**: Tested with up to 20 comparables (schema limit)

## Requirements

```bash
pip install jsonschema
```

**Version compatibility**: Requires Python 3.8+ and jsonschema >= 4.0

---

**Last Updated**: 2025-01-15
**Version**: 1.0.0
**Maintained By**: VP Real Estate - Comparable Sales Methodology Team
