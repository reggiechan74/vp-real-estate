# Weights Configuration Guide

**Version**: 2.0
**Last Updated**: November 6, 2025

---

## Overview

The Relative Valuation Calculator now supports **external weight configuration files**, allowing you to customize tenant persona weights without modifying code.

### Benefits

✅ **Easy Customization**: Edit JSON file instead of Python code
✅ **Multiple Personas**: Store default, 3PL, manufacturing, office profiles in one file
✅ **Version Control**: Track weight changes over time with git
✅ **Validation**: Automatic validation ensures weights sum to 100%
✅ **Fallback**: Hardcoded defaults if config file unavailable
✅ **Documentation**: Self-documenting with descriptions and rationale

---

## Quick Start

### 1. Use Default Config

The calculator automatically loads from `weights_config.json`:

```bash
python relative_valuation_calculator.py \
  --input data.json \
  --output report.md \
  --persona default
```

### 2. List Available Personas

```bash
python weights_loader.py --list
```

**Output:**
```
Available Personas:
------------------------------------------------------------

default: Default/Balanced
  Balanced weight profile for general industrial tenants

3pl: 3PL/Distribution
  Optimized for third-party logistics and distribution operations

manufacturing: Manufacturing
  Optimized for manufacturing operations requiring heavy power

office: Office/Flex
  Optimized for office or flex space with high office component
```

### 3. View Persona Weights

```bash
python weights_loader.py --show 3pl
```

**Output:**
```
============================================================
PERSONA: 3PL/Distribution
============================================================

Optimized for third-party logistics and distribution operations

RATIONALE: Emphasizes bay depth, clear height, shipping doors, and trailer parking

WEIGHTS (sorted by importance):
Variable                    Weight                           Bar
------------------------------------------------------------
net_asking_rent             12.0% ████████████████████████
clear_height_ft             10.0% ████████████████████
tmi                          9.0% ██████████████████
distance_km                  8.0% ████████████████
parking_ratio                8.0% ████████████████
bay_depth_ft                 7.0% ██████████████
area_difference              7.0% ██████████████
...
------------------------------------------------------------
TOTAL                      100.0%
============================================================
```

### 4. Validate Config File

```bash
python weights_loader.py --validate
```

**Output:**
```
✓ Config valid: 4 personas loaded
  - default: Default/Balanced (total weight: 1.0000)
  - 3pl: 3PL/Distribution (total weight: 1.0000)
  - manufacturing: Manufacturing (total weight: 1.0000)
  - office: Office/Flex (total weight: 1.0000)
```

---

## Configuration File Structure

### File Location

**Default**: `Relative_Valuation/weights_config.json`

**Custom Path**:
```bash
# Option 1: Environment variable
export WEIGHTS_CONFIG_PATH=/path/to/custom_weights.json

# Option 2: Command-line argument (future enhancement)
python relative_valuation_calculator.py --weights-config /path/to/custom_weights.json
```

### File Format (JSON)

```json
{
  "version": "2.0",
  "last_updated": "2025-11-06",
  "description": "Weight configurations for tenant personas",

  "personas": {
    "custom_persona": {
      "name": "Custom Persona Name",
      "description": "What this persona represents",
      "rationale": "Why these weights were chosen",
      "weights": {
        "core_variables": {
          "net_asking_rent": 0.11,
          "parking_ratio": 0.09,
          "tmi": 0.09,
          // ... all 9 core variables required
        },
        "optional_variables": {
          "shipping_doors_tl": 0.04,
          "bay_depth_ft": 0.04,
          // ... 16 optional variables (can be 0.00)
        }
      }
    }
  },

  "validation": {
    "total_weight_tolerance": 0.001,
    "min_weight": 0.00,
    "max_weight": 0.25
  }
}
```

---

## Creating Custom Personas

### Example: E-Commerce Distribution Center

E-commerce tenants prioritize fast order fulfillment, so they value:
- **High clear height** (dense vertical storage)
- **Excellent shipping door ratio** (high throughput)
- **Immediate occupancy** (seasonal demand)
- **Less emphasis on office space** (minimal on-site staff)

**Step 1**: Copy default persona in `weights_config.json`

```json
"ecommerce": {
  "name": "E-Commerce Distribution",
  "description": "Optimized for e-commerce fulfillment centers",
  "rationale": "Emphasizes clear height, shipping doors, bay depth, and immediate occupancy for seasonal ramp-up",
  "weights": {
    "core_variables": {
      "net_asking_rent": 0.10,      // ↓ Slightly less important (will pay premium for features)
      "parking_ratio": 0.07,         // ↓ Less staff on-site
      "tmi": 0.09,
      "clear_height_ft": 0.12,       // ↑ Critical for dense storage
      "pct_office_space": 0.01,      // ↓ Minimal office needs
      "distance_km": 0.06,           // ↓ Less important (can be suburban)
      "area_difference": 0.08,
      "building_age_years": 0.02,    // ↓ Don't care about age if functional
      "class": 0.01                  // ↓ Don't care about class
    },
    "optional_variables": {
      "shipping_doors_tl": 0.08,     // ↑ High throughput critical
      "shipping_doors_di": 0.05,     // ↑ Van/small truck access
      "power_amps": 0.02,
      "trailer_parking": 0.03,
      "secure_shipping": 0.00,
      "excess_land": 0.00,
      "bay_depth_ft": 0.08,          // ↑ 53' trailer access
      "lot_size_acres": 0.03,
      "hvac_coverage": 0.02,
      "sprinkler_type": 0.04,        // ↑ Insurance critical
      "rail_access": 0.00,           // ↓ No rail needed
      "crane": 0.00,                 // ↓ No crane needed
      "occupancy_status": 0.05,      // ↑ Immediate occupancy critical
      "grade_level_doors": 0.03,     // ↑ Last-mile delivery
      "days_on_market": 0.01,
      "zoning": 0.02
    }
  }
}
```

**Step 2**: Validate

```bash
python weights_loader.py --validate
```

**Step 3**: Test

```bash
python relative_valuation_calculator.py \
  --input mississauga_data.json \
  --persona ecommerce \
  --output ecommerce_report.md
```

### Example: Cold Storage Facility

Cold storage tenants have unique requirements:

**Custom Weights**:
```json
"cold_storage": {
  "name": "Cold Storage/Refrigerated",
  "rationale": "Heavy power for refrigeration, strong construction for insulation",
  "weights": {
    "core_variables": {
      "net_asking_rent": 0.08,       // ↓ Will pay premium for right features
      "parking_ratio": 0.06,
      "tmi": 0.12,                   // ↑ Electricity costs critical
      "clear_height_ft": 0.10,       // ↑ Vertical storage efficiency
      "pct_office_space": 0.02,
      "distance_km": 0.05,
      "area_difference": 0.07,
      "building_age_years": 0.06,    // ↑ Newer = better insulation
      "class": 0.04
    },
    "optional_variables": {
      "shipping_doors_tl": 0.06,
      "shipping_doors_di": 0.02,
      "power_amps": 0.10,            // ↑ Heavy electrical for refrigeration
      "trailer_parking": 0.03,
      "bay_depth_ft": 0.05,
      "lot_size_acres": 0.02,
      "hvac_coverage": 0.00,         // ↓ Irrelevant (custom HVAC)
      "sprinkler_type": 0.04,
      "occupancy_status": 0.03,
      "grade_level_doors": 0.02,
      "days_on_market": 0.02,
      "zoning": 0.01
    }
  }
}
```

---

## Weight Allocation Guidelines

### Rule 1: Core Variables Must Sum to 60-70%

Core variables are always available, so they should represent the majority of weight:

```
Recommended Core Allocation:
  net_asking_rent:     10-14%  (most critical)
  tmi:                  8-12%  (occupancy cost)
  parking_ratio:        7-12%  (essential for most uses)
  clear_height_ft:      5-10%  (storage efficiency)
  distance_km:          5-10%  (location preference)
  area_difference:      5-10%  (size match)
  pct_office_space:     2-12%  (varies by tenant type)
  building_age_years:   2-6%   (quality indicator)
  class:                2-8%   (prestige factor)
  ────────────────────────────
  TOTAL CORE:          60-70%
```

### Rule 2: Optional Variables Should Sum to 30-40%

Optional variables may be missing from datasets, so limit total allocation:

```
Recommended Optional Allocation:
  High Priority (3-8% each):
    - shipping_doors_tl
    - bay_depth_ft
    - power_amps (manufacturing)
    - hvac_coverage (office)

  Medium Priority (2-4% each):
    - shipping_doors_di
    - lot_size_acres
    - sprinkler_type
    - trailer_parking

  Low Priority (0-2% each):
    - crane, rail_access (niche requirements)
    - occupancy_status (filtering only)
    - days_on_market (soft signal)
  ────────────────────────────
  TOTAL OPTIONAL:      30-40%
```

### Rule 3: No Single Variable Should Exceed 20%

Prevents over-weighting any one factor:

```
✓ Good: net_asking_rent = 14%
✗ Bad:  net_asking_rent = 30%  (too dominant)
```

### Rule 4: Zero-Weight Variables Are Acceptable

Use `0.00` for variables not relevant to persona:

```json
"office": {
  "weights": {
    "crane": 0.00,              // Office tenants don't need cranes
    "rail_access": 0.00,        // Office tenants don't need rail
    "bay_depth_ft": 0.00,       // Bay depth irrelevant for office
    "trailer_parking": 0.00     // No trailer parking needed
  }
}
```

The dynamic redistribution algorithm will exclude these from calculation.

---

## Validation Rules

### Automatic Validation

The `weights_loader.py` module validates:

1. **Structure**: All required keys present (`personas`, `weights`, `core_variables`)
2. **Core Variables**: All 9 core variables present with numeric weights
3. **Total Weight**: Sum of all weights = 1.0 (within tolerance)
4. **Range**: All weights between 0.0 and 1.0 (or 0-100 if percentages)
5. **Types**: All weights are numeric (int or float)

### Tolerance Settings

```json
"validation": {
  "total_weight_tolerance": 0.001,  // ±0.001 from 1.0 acceptable
  "min_weight": 0.00,               // Minimum allowed weight
  "max_weight": 0.25                // Maximum allowed weight (prevents over-concentration)
}
```

**Example Error Messages**:

```
[ERROR] Persona 'custom' missing required core variables: ['tmi', 'class']

[ERROR] Persona '3pl': weights sum to 1.0234, expected 1.0 (tolerance: 0.001)

[ERROR] Persona 'manufacturing': weight for 'power_amps' is negative: -0.03
```

### Manual Validation

```bash
# Validate current config
python weights_loader.py --validate

# Validate custom config
python weights_loader.py --validate --config /path/to/custom.json
```

---

## Integration with Calculator

### Current Integration (Manual)

**Update `relative_valuation_calculator.py`** to use config loader:

```python
from weights_loader import get_persona_weights

def get_tenant_persona_weights(persona: str = "default") -> Dict[str, float]:
    """
    Get weight profiles tailored to specific tenant personas.

    Now loads from weights_config.json instead of hardcoded values.
    """
    try:
        # Try loading from config file
        weights = get_persona_weights(persona)
        print(f"[INFO] Loaded persona '{persona}' from weights_config.json")
        return weights
    except Exception as e:
        print(f"[WARNING] Could not load config: {e}")
        print("[INFO] Falling back to hardcoded defaults")

        # Fallback to original hardcoded weights
        if persona == "3pl":
            return {
                'net_asking_rent': 0.12,
                'parking_ratio': 0.08,
                # ... rest of hardcoded 3PL weights
            }
        # ... other personas

        # Default fallback
        return {
            'net_asking_rent': 0.11,
            'parking_ratio': 0.09,
            # ... rest of hardcoded default weights
        }
```

### Future Enhancement (CLI Argument)

```python
# In argument parser
parser.add_argument('--weights-config', type=str,
                   help='Path to custom weights configuration file')

# In main()
weights = get_persona_weights(
    persona=args.persona,
    config_path=args.weights_config
)
```

**Usage**:
```bash
python relative_valuation_calculator.py \
  --input data.json \
  --persona ecommerce \
  --weights-config /path/to/custom_weights.json \
  --output report.md
```

---

## Best Practices

### 1. Document Your Rationale

Always include `description` and `rationale` fields:

```json
{
  "name": "Last-Mile Delivery",
  "description": "Optimized for urban last-mile delivery hubs",
  "rationale": "Emphasizes immediate occupancy, grade-level doors for van access, and proximity to urban centers. De-emphasizes traditional industrial features like clear height and bay depth."
}
```

### 2. Version Your Config Files

Use semantic versioning and track changes:

```json
{
  "version": "2.1",
  "last_updated": "2025-12-01",
  "changelog": [
    "2.1 (2025-12-01): Increased parking weight for manufacturing persona",
    "2.0 (2025-11-06): Initial external config implementation"
  ]
}
```

### 3. Test Before Deploying

Run validation and spot-check results:

```bash
# Validate config
python weights_loader.py --validate --config new_weights.json

# Show persona summary
python weights_loader.py --show custom --config new_weights.json

# Run test analysis
python relative_valuation_calculator.py \
  --input test_data.json \
  --persona custom \
  --weights-config new_weights.json \
  --output test_report.md
```

### 4. Export for Documentation

Generate standalone persona files for sharing:

```bash
python weights_loader.py \
  --export 3pl \
  --output 3pl_weights.json \
  --config weights_config.json
```

**Output** (`3pl_weights.json`):
```json
{
  "persona": "3pl",
  "name": "3PL/Distribution",
  "description": "Optimized for third-party logistics...",
  "weights": {
    "net_asking_rent": 0.12,
    "clear_height_ft": 0.10,
    ...
  },
  "total": 1.0
}
```

### 5. Keep Backups

Before making significant changes:

```bash
cp weights_config.json weights_config.json.backup
```

Or use git:

```bash
git add Relative_Valuation/weights_config.json
git commit -m "Update 3PL persona weights: increase bay_depth +2%"
```

---

## Troubleshooting

### Issue: "Config file not found"

**Problem**: `weights_config.json` not in expected location

**Solution**:
1. Check current directory: `ls Relative_Valuation/weights_config.json`
2. Set environment variable: `export WEIGHTS_CONFIG_PATH=/full/path/to/weights_config.json`
3. Use absolute path in code

### Issue: "Weights sum to 0.9876, expected 1.0"

**Problem**: Weights don't sum to exactly 1.0

**Solution**:
1. Add up all weights manually
2. Adjust largest weight to compensate
3. Use online calculator for precision

**Example**:
```
Current sum: 0.9876
Adjustment needed: 1.0 - 0.9876 = 0.0124

Current net_asking_rent: 0.11
Adjusted: 0.11 + 0.0124 = 0.1224 (12.24%)
```

### Issue: "Persona 'custom' not found"

**Problem**: Typo in persona name or persona doesn't exist

**Solution**:
```bash
# List available personas
python weights_loader.py --list

# Check for typos (case-sensitive!)
# ✓ Good: --persona 3pl
# ✗ Bad:  --persona 3PL  (uppercase)
```

### Issue: "Invalid JSON in weights config"

**Problem**: Syntax error in JSON file

**Solution**:
1. Validate JSON online: https://jsonlint.com/
2. Check for:
   - Missing commas
   - Trailing commas (not allowed in JSON)
   - Unclosed brackets
   - Unquoted keys

**Common Errors**:
```json
// ✗ Bad: Trailing comma
{
  "name": "Custom",
  "description": "Test",  // ← Trailing comma before }
}

// ✓ Good: No trailing comma
{
  "name": "Custom",
  "description": "Test"
}
```

---

## Examples

### Example 1: Regional Weight Differences

**GTA Market** (high competition, expensive land):
```json
"gta_default": {
  "weights": {
    "net_asking_rent": 0.14,    // ↑ Price-sensitive market
    "parking_ratio": 0.08,      // ↓ Limited parking supply
    "distance_km": 0.09         // ↑ Location critical (traffic)
  }
}
```

**Rural Market** (abundant land, lower costs):
```json
"rural_default": {
  "weights": {
    "net_asking_rent": 0.09,    // ↓ Lower absolute costs
    "lot_size_acres": 0.06,     // ↑ More land available
    "distance_km": 0.04         // ↓ Less critical (less traffic)
  }
}
```

### Example 2: Quarterly Weight Calibration

Track market evolution over time:

**Q1 2025** (tight market):
```json
"default_q1_2025": {
  "weights": {
    "occupancy_status": 0.05,   // ↑ Immediate occupancy premium
    "days_on_market": 0.03      // ↑ Landlord motivation matters
  }
}
```

**Q3 2025** (softening market):
```json
"default_q3_2025": {
  "weights": {
    "occupancy_status": 0.00,   // ↓ More options available
    "days_on_market": 0.01,     // ↓ Less relevant
    "net_asking_rent": 0.13     // ↑ More negotiating power
  }
}
```

---

## Schema Reference

See `weights_config_schema.json` for complete JSON Schema Draft 2020-12 validation.

**Key Schema Rules**:

1. **Persona IDs**: Must be lowercase alphanumeric with underscores (`^[a-z0-9_]+$`)
2. **Weights**: Must be between 0 and 100 (auto-detects decimal vs percentage)
3. **Required Core Variables**: All 9 must be present
4. **Optional Variables**: Can be omitted (defaults to 0.0)

---

## CLI Reference

### `weights_loader.py` Commands

```bash
# List all personas
python weights_loader.py --list

# Show persona weights
python weights_loader.py --show PERSONA [--config PATH]

# Export persona to file
python weights_loader.py --export PERSONA --output PATH [--config PATH]

# Validate config
python weights_loader.py --validate [--config PATH]
```

### Environment Variables

```bash
# Set custom config path
export WEIGHTS_CONFIG_PATH=/path/to/weights.json

# Weights loader will automatically use this path
python weights_loader.py --list
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-05 | Hardcoded weights in `get_tenant_persona_weights()` |
| 2.0 | 2025-11-06 | External config file support with `weights_loader.py` |

---

## See Also

- **RANKING_METHODOLOGY.md**: Detailed explanation of ranking algorithm
- **SCHEMA.md**: Complete variable reference and data requirements
- **README.md**: General usage guide for relative valuation calculator

---

**For questions or issues, contact the Lease Analysis Toolkit team.**
