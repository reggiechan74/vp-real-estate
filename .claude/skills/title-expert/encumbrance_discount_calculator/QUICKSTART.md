# Encumbrance Discount Calculator - Quick Start Guide

## Installation

No installation required - uses existing Python environment with Shared_Utils.

## 5-Minute Quick Start

### 1. Run a Sample Calculation

```bash
cd .claude/skills/title-expert/encumbrance_discount_calculator
python encumbrance_discount_calculator.py sample_inputs/simple_drainage_example.json
```

**Output:**
```
✓ Report saved to: Reports/2025-11-17_143022_encumbrance_discount_55555_1111.md

VALUATION SUMMARY
| Property               | 1250 Industrial Parkway, Business District |
| Unencumbered Value     | $500,000.00                                |
| Final Adjusted Value   | $460,750.00                                |
| Total Discount         | $39,250.00 (7.85%)                        |
```

### 2. Create Your Own Input File

**my_property.json:**
```json
{
  "property": {
    "pin": "12345-6789",
    "address": "Your Property Address",
    "total_area_acres": 50.0,
    "unencumbered_value": 600000
  },
  "encumbrances": [
    {
      "type": "transmission_easement",
      "area_acres": 3.0,
      "impact_percentage": 10
    }
  ]
}
```

### 3. Run Your Calculation

```bash
python encumbrance_discount_calculator.py my_property.json --verbose
```

## Common Use Cases

### Case 1: Single Encumbrance

**Scenario:** Industrial property with drainage easement

```json
{
  "property": {
    "pin": "001-001",
    "address": "1000 Industrial Rd",
    "total_area_acres": 10.0,
    "unencumbered_value": 500000
  },
  "encumbrances": [
    {
      "type": "drainage_easement",
      "area_acres": 0.5,
      "impact_percentage": 5
    }
  ]
}
```

**Expected Result:** ~$488,000 (2.4% discount)

---

### Case 2: Multiple Encumbrances (Agricultural)

**Scenario:** Farm with transmission line and ongoing crop losses

```json
{
  "property": {
    "pin": "002-002",
    "address": "500 Farm Road",
    "total_area_acres": 100.0,
    "unencumbered_value": 1200000,
    "zoning": "Agricultural"
  },
  "encumbrances": [
    {
      "type": "transmission_easement",
      "area_acres": 5.0,
      "voltage": "500kV",
      "impact_percentage": 12
    }
  ],
  "agricultural_impacts": {
    "annual_crop_loss": 8000,
    "cap_rate": 0.05
  }
}
```

**Expected Result:** ~$1,050,000 (12.5% discount + capitalized crop loss)

---

### Case 3: Complex Development Site

**Scenario:** Development site with multiple restrictions

```json
{
  "property": {
    "pin": "003-003",
    "address": "200 Development Blvd",
    "total_area_acres": 50.0,
    "unencumbered_value": 2000000,
    "zoning": "Residential",
    "highest_best_use": "Residential subdivision (10 lots)"
  },
  "encumbrances": [
    {
      "type": "conservation_easement",
      "area_acres": 20.0,
      "impact_percentage": 35
    },
    {
      "type": "access_easement",
      "area_acres": 1.0,
      "impact_percentage": 5
    }
  ]
}
```

**Expected Result:** ~$1,150,000 (42.5% discount)

## Command-Line Options

### Basic Usage
```bash
python encumbrance_discount_calculator.py input.json
```

### With Verbose Output
```bash
python encumbrance_discount_calculator.py input.json --verbose
```

### Specify Calculation Method
```bash
# Multiplicative (default) - most conservative
python encumbrance_discount_calculator.py input.json --method multiplicative

# Additive - simple sum
python encumbrance_discount_calculator.py input.json --method additive

# Geometric mean - middle ground
python encumbrance_discount_calculator.py input.json --method geometric_mean
```

### Marketability Discount Method
```bash
# Conservative (default) - higher discount
python encumbrance_discount_calculator.py input.json --marketability conservative

# Moderate - mid-range
python encumbrance_discount_calculator.py input.json --marketability moderate

# Optimistic - lower discount
python encumbrance_discount_calculator.py input.json --marketability optimistic
```

### Export Options
```bash
# Custom report location
python encumbrance_discount_calculator.py input.json --output my_report.md

# Export JSON results
python encumbrance_discount_calculator.py input.json --json results.json

# Both
python encumbrance_discount_calculator.py input.json \
  --output report.md \
  --json results.json
```

## Encumbrance Types

| Type | Typical Impact | Use When |
|------|----------------|----------|
| transmission_easement | 10% (5-15%) | High-voltage power lines |
| pipeline_easement | 15% (10-20%) | Oil/gas/water pipelines |
| drainage_easement | 5% (2-8%) | Stormwater/drainage |
| access_easement | 5% (2-8%) | Shared access rights |
| conservation_easement | 35% (20-50%) | Conservation restrictions |
| telecom_easement | 6% (3-10%) | Cell towers, fiber |

**If not specified, calculator uses typical percentage for type.**

## Understanding the Output

### Console Summary Table
```
| Item                     | Value                     |
|--------------------------|---------------------------|
| Property                 | 100 Farm Road             |
| Total Area               | 100.00 acres              |
| Unencumbered Value       | $1,200,000.00             |
| Encumbrance Discount     | 27.32%                    |
| Value After Encumbrances | $872,100.00               |
| Marketability Discount   | 10.00%                    |
| Final Adjusted Value     | $784,890.00               |
| Total Discount           | $415,110.00               |
| Total Discount %         | 34.59%                    |
```

### Markdown Report Sections

1. **Property Summary** - Basic property details
2. **Executive Summary** - Key findings and final value
3. **Individual Encumbrance Analysis** - Detailed breakdown
4. **Cumulative Discount Calculation** - Step-by-step math
5. **Development Potential Impact** - Buildable area analysis
6. **Marketability Analysis** - Buyer pool assessment
7. **Final Valuation Summary** - Waterfall calculation
8. **Methodology** - Technical documentation

## Common Questions

### Q: What if I don't know the impact percentage?

**A:** Omit it. Calculator uses typical value for encumbrance type.

```json
{
  "type": "transmission_easement",
  "area_acres": 5.0
  // impact_percentage omitted - uses 10% default
}
```

### Q: How is cumulative discount calculated?

**A:** Default multiplicative method:
```
Value × (1-D₁) × (1-D₂) × (1-D₃)

Example:
$1,200,000 × (1-0.10) × (1-0.15) × (1-0.05)
= $1,200,000 × 0.90 × 0.85 × 0.95
= $872,100
```

### Q: What's the difference between methods?

**A:** Three cumulative discount methods:

| Method | Formula | Use Case | Result* |
|--------|---------|----------|---------|
| Multiplicative | (1-D₁)×(1-D₂)×(1-D₃) | Default, most conservative | 27.3% |
| Additive | D₁ + D₂ + D₃ | Simple sum | 30.0% |
| Geometric Mean | [(1-D₁)×(1-D₂)×(1-D₃)]^(1/n) | Middle ground | 28.6% |

*Example with 10%, 15%, 5% discounts

### Q: When should I include agricultural impacts?

**A:** When:
- Property is actively farmed
- Encumbrances cause ongoing crop losses
- Operational inefficiencies (longer field runs, split parcels)

### Q: What are paired sales used for?

**A:** Market validation:
- Compare similar properties with/without encumbrances
- Derive market-supported discount percentage
- Validate calculator results against actual sales

## Validation Messages

### Warnings (Non-Fatal)
```
⚠️  VALIDATION WARNINGS:
   - Encumbrance 1: 12% is outside typical range for transmission_easement (5.0-15.0%)
   - cap_rate 8.0% is outside typical range (3-15%)
```
**Action:** Review values but calculation proceeds.

### Errors (Fatal)
```
❌ VALIDATION ERRORS:
   - Missing required property field: unencumbered_value
   - Encumbrance 2: area_acres must be positive
```
**Action:** Fix input file and retry.

## Testing Your Installation

```bash
# Run test suite
python test_calculator.py

# Expected output:
# ================================================================================
# TEST RESULTS
# ================================================================================
# Passed: 6/6
# Failed: 0/6
#
# ✓ ALL TESTS PASSED
```

## Getting Help

```bash
# Command-line help
python encumbrance_discount_calculator.py --help

# Read documentation
cat README.md           # User guide
cat ARCHITECTURE.md     # Technical architecture
cat DIAGRAM.md          # Visual diagrams
```

## Sample Workflow

```bash
# 1. Copy sample input
cp sample_inputs/transmission_pipeline_example.json my_input.json

# 2. Edit for your property
nano my_input.json

# 3. Run calculation
python encumbrance_discount_calculator.py my_input.json --verbose

# 4. Review report
cat Reports/2025-11-17_*_my_input.md

# 5. Export JSON for further analysis
python encumbrance_discount_calculator.py my_input.json --json analysis.json
```

## Performance Tips

- Single property: Use command line
- Batch processing: Use Python API in loop
- Complex scenarios: Enable --verbose for detailed output
- Production use: Redirect output to log files

## Next Steps

1. Run sample inputs to understand output format
2. Create input file for your property
3. Review generated markdown report
4. Adjust method/marketability settings as needed
5. Export JSON for integration with other tools

---

**Ready to Calculate?**

```bash
cd .claude/skills/title-expert/encumbrance_discount_calculator
python encumbrance_discount_calculator.py sample_inputs/simple_drainage_example.json --verbose
```

For detailed documentation, see:
- **README.md** - Complete user guide
- **ARCHITECTURE.md** - Technical details
- **DIAGRAM.md** - Visual architecture
