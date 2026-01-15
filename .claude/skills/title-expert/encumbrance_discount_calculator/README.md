# Encumbrance Discount Valuation Calculator

Modular calculator for valuing property encumbrances (easements, rights-of-way) using percentage of fee, income capitalization, and paired sales methods.

## Features

- **Individual Encumbrance Analysis**: Calculate discount for each encumbrance based on type-specific ranges
- **Cumulative Discount Calculation**: Apply multiplicative discount formula: Value × (1-D₁) × (1-D₂) × (1-D₃)
- **Development Potential Assessment**: Analyze impact on buildable area, subdivision, and access
- **Residual Value Analysis**: Calculate residual land value after encumbrances
- **Marketability Discount**: Assess buyer pool reduction and financing impact
- **Agricultural Income Capitalization**: Capitalize ongoing crop losses (optional)
- **Paired Sales Analysis**: Market-based discount validation (optional)

## Architecture

```
encumbrance_discount_calculator/
├── encumbrance_discount_calculator.py  # Main orchestration (<400 lines)
├── modules/
│   ├── __init__.py
│   ├── validators.py                   # Input validation
│   ├── cumulative_impact.py           # Cumulative discount calculations
│   ├── residual_analysis.py           # Development potential analysis
│   ├── marketability.py               # Buyer pool & marketability
│   └── output_formatters.py           # Report generation
├── sample_inputs/
│   ├── transmission_pipeline_example.json
│   ├── conservation_easement_example.json
│   └── simple_drainage_example.json
└── README.md
```

## Encumbrance Types & Typical Ranges

| Encumbrance Type | Typical Range | Typical Impact | Description |
|------------------|---------------|----------------|-------------|
| Transmission easement | 5-15% | 10% | High-voltage power lines |
| Pipeline easement | 10-20% | 15% | Oil/gas/water pipelines |
| Drainage easement | 2-8% | 5% | Stormwater/municipal drainage |
| Access easement | 2-8% | 5% | Shared access rights |
| Conservation easement | 20-50% | 35% | Development restrictions |
| Telecom easement | 3-10% | 6% | Cell towers, fiber optic |

## Usage

### Command Line

```bash
# Basic usage
python encumbrance_discount_calculator.py input.json

# Specify cumulative discount method
python encumbrance_discount_calculator.py input.json --method multiplicative

# Conservative marketability discount (default)
python encumbrance_discount_calculator.py input.json --marketability conservative

# Output to specific file
python encumbrance_discount_calculator.py input.json --output report.md

# Export JSON results
python encumbrance_discount_calculator.py input.json --json results.json

# Verbose output
python encumbrance_discount_calculator.py input.json --verbose
```

### Python API

```python
from encumbrance_discount_calculator import run_encumbrance_analysis

# Load input data
input_data = {
    "property": {
        "pin": "12345-6789",
        "address": "100 Farm Road",
        "total_area_acres": 100.0,
        "unencumbered_value": 1200000,
        "zoning": "Agricultural",
        "highest_best_use": "Agricultural"
    },
    "encumbrances": [
        {
            "type": "transmission_easement",
            "area_acres": 5.0,
            "voltage": "500kV",
            "impact_percentage": 10
        }
    ]
}

# Run analysis
results = run_encumbrance_analysis(
    input_data,
    method='multiplicative',
    marketability_method='conservative',
    verbose=True
)

# Access results
print(f"Final value: ${results['final_value']:,.2f}")
print(f"Total discount: {results['total_discount_percentage']:.2f}%")
```

## Input Format

### Required Fields

```json
{
  "property": {
    "pin": "12345-6789",
    "address": "100 Farm Road",
    "total_area_acres": 100.0,
    "unencumbered_value": 1200000
  },
  "encumbrances": [
    {
      "type": "transmission_easement",
      "area_acres": 5.0,
      "impact_percentage": 10
    }
  ]
}
```

### Optional Fields

```json
{
  "property": {
    "zoning": "Agricultural",
    "highest_best_use": "Agricultural with subdivision potential"
  },
  "encumbrances": [
    {
      "voltage": "500kV",
      "width_feet": 150,
      "length_feet": 1452,
      "description": "Custom description"
    }
  ],
  "agricultural_impacts": {
    "annual_crop_loss": 5000,
    "cap_rate": 0.05,
    "operational_inefficiency_pct": 10
  },
  "paired_sales": [
    {
      "address": "200 Farm Road",
      "sale_price": 1150000,
      "sale_date": "2024-06-15",
      "area_acres": 95.0,
      "has_encumbrance": false
    }
  ]
}
```

## Calculation Methods

### 1. Individual Encumbrance Discount

For each encumbrance:
```
Encumbered Area Value = Total Value × (Encumbered Area / Total Area)
Discount Amount = Encumbered Area Value × Impact Percentage
```

### 2. Cumulative Discount (Multiplicative - Default)

```
Adjusted Value = Unencumbered Value × (1-D₁) × (1-D₂) × (1-D₃)
```

**Example:**
- Unencumbered value: $1,200,000
- Transmission easement: 10% discount
- Pipeline easement: 15% discount
- Drainage easement: 5% discount

```
Adjusted Value = $1,200,000 × (1-0.10) × (1-0.15) × (1-0.05)
               = $1,200,000 × 0.90 × 0.85 × 0.95
               = $872,100
Cumulative Discount = 27.33%
```

### 3. Alternative Methods

**Additive (Simple Sum):**
```
Cumulative Discount = D₁ + D₂ + D₃
Example: 10% + 15% + 5% = 30%
```

**Geometric Mean:**
```
Value Multiplier = [(1-D₁) × (1-D₂) × (1-D₃)]^(1/n)
```

### 4. Development Potential Adjustment

Analyzes impact on:
- Buildable area (structure restrictions)
- Subdivision potential (lot reduction)
- Access and circulation
- Development constraints

### 5. Marketability Discount

Accounts for:
- Reduced buyer pool
- Extended marketing time
- Limited financing options
- Transaction uncertainty

## Sample Inputs

### Transmission + Pipeline (Complex)

```bash
python encumbrance_discount_calculator.py \
  sample_inputs/transmission_pipeline_example.json \
  --verbose
```

**Property:** 100 acres, $1,200,000 unencumbered value
**Encumbrances:** Transmission (5 acres, 10%), Pipeline (3 acres, 15%), Drainage (2 acres, 5%)
**Result:** ~$872,000 after encumbrances, ~$830,000 after marketability discount

### Conservation Easement (High Impact)

```bash
python encumbrance_discount_calculator.py \
  sample_inputs/conservation_easement_example.json \
  --marketability conservative
```

**Property:** 50 acres, $800,000 unencumbered value
**Encumbrances:** Conservation (30 acres, 40%), Access (1.5 acres, 5%)
**Result:** ~$280,000 final value (65% total discount)

### Simple Drainage (Low Impact)

```bash
python encumbrance_discount_calculator.py \
  sample_inputs/simple_drainage_example.json \
  --marketability optimistic
```

**Property:** 10 acres, $500,000 unencumbered value
**Encumbrances:** Drainage (0.8 acres, 5%)
**Result:** ~$496,000 final value (minimal impact)

## Output

### Markdown Report

Timestamped report saved to `Reports/` directory with sections:
1. **Property Summary**: Basic property details
2. **Executive Summary**: Key findings and final value
3. **Individual Encumbrance Analysis**: Detailed breakdown by encumbrance
4. **Cumulative Discount Calculation**: Step-by-step cumulative calculation
5. **Development Potential Impact**: Buildable area, subdivision, constraints
6. **Marketability Analysis**: Buyer pool, financing, marketing challenges
7. **Final Valuation Summary**: Waterfall from unencumbered to final value
8. **Methodology & Assumptions**: Technical documentation

### JSON Export

```json
{
  "timestamp": "2025-11-17 15:30:00 EST",
  "property": {...},
  "individual_discounts": [...],
  "cumulative_discount": {...},
  "development_potential": {...},
  "residual_value": {...},
  "buyer_pool_analysis": {...},
  "marketability_discount": {...},
  "final_value": 830000,
  "total_discount_amount": 370000,
  "total_discount_percentage": 30.83
}
```

## Integration with Shared_Utils

The calculator imports from existing shared utilities:

```python
from Shared_Utils.financial_utils import calculate_npv
from Shared_Utils.report_utils import eastern_timestamp, format_markdown_table
```

## Validation

The calculator validates:
- Required property fields (PIN, address, area, value)
- Positive numeric values (area, price)
- Encumbrance types against known ranges
- Total encumbered area ≤ total property area
- Cap rates within typical ranges (3-15%)
- Date formats (YYYY-MM-DD)

**Warnings** are issued for:
- Impact percentages outside typical range for type
- Unknown encumbrance types
- Unusual cap rates

## Error Handling

```bash
❌ VALIDATION ERRORS:
   - Missing required property field: unencumbered_value
   - Encumbrance 2: area_acres must be positive
   - Total encumbered area (105.00 acres) exceeds property area (100.00 acres)
```

## Dependencies

- Python 3.8+
- numpy
- pandas (via Shared_Utils)
- pytz (for Eastern timezone)

## Author

Created: 2025-11-17
Part of title-expert skill suite
