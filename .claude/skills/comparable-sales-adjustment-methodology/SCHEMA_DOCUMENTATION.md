# Comparable Sales Input Schema Documentation

## Overview

This JSON Schema validates input files for the comparable sales adjustment methodology calculator, ensuring USPAP 2024 and CUSPAP 2024 compliance.

**Schema Version**: JSON Schema Draft 2020-12
**File**: `comparable_sales_input_schema.json`

## Quick Start

### Validate a JSON file

```python
import json
from jsonschema import validate, ValidationError

# Load schema
with open('comparable_sales_input_schema.json', 'r') as f:
    schema = json.load(f)

# Load and validate your data
with open('your_input_file.json', 'r') as f:
    data = json.load(f)

try:
    validate(instance=data, schema=schema)
    print("✅ Input file is valid")
except ValidationError as e:
    print(f"❌ Validation error: {e.message}")
```

### Using with the calculator

```bash
# The calculator automatically uses this schema for validation
python comparable_sales_calculator.py your_input_file.json --verbose
```

## Structure

### Required Top-Level Properties

1. **subject_property** (object) - Property being valued
2. **comparable_sales** (array) - 1-20 comparable transactions
3. **market_parameters** (object) - Market adjustment parameters

## Subject Property Schema

### Required Fields

- `address` (string, 5-200 chars)
- `property_type` (enum: "industrial" | "office" | "retail" | "multi-family")
- `property_rights` (enum: "fee_simple" | "leasehold" | "leased_fee")

### Optional Fields by Category

#### Land Characteristics (8 subcategories)

| Field | Type | Range | Enum Values |
|-------|------|-------|-------------|
| `lot_size_acres` | number | 0 - 10,000 | - |
| `frontage_linear_feet` | number | 0 - 5,000 | - |
| `depth_feet` | number | 0 - 5,000 | - |
| `topography` | string | - | severely_sloped, moderately_sloped, gently_sloped, level |
| `utilities` | string | - | full_services_adequate, full_services_limited, partial_services, no_services |
| `drainage` | string | - | poor, adequate, good, excellent |
| `flood_zone` | string | - | none, flood_fringe, floodway |
| `environmental_status` | string | - | contaminated, brownfield, wetlands_minor, wetlands_major, clean |
| `soil_quality` | string | - | poor_bearing, adequate, good_bearing, excellent |

#### Site Improvements (6 subcategories)

| Field | Type | Range | Enum Values |
|-------|------|-------|-------------|
| `paved_area_acres` | number | 0+ | - |
| `paving_condition` | string | - | poor, fair, good, excellent |
| `fencing` | string | - | none, chain_link, vinyl, security_fence |
| `fence_age_years` | number | 0 - 50 | - |
| `site_lighting` | string | - | none, minimal, adequate, extensive |
| `landscaping` | string | - | none, minimal, moderate, extensive |
| `stormwater_management` | string | - | none, basic, retention_pond, advanced_system |
| `secured_yard_acres` | number | 0+ | - |

#### General Building Characteristics (6 subcategories)

| Field | Type | Range | Enum Values |
|-------|------|-------|-------------|
| `building_sf` | number | 0 - 10,000,000 | - |
| `effective_age_years` | number | 0 - 200 | - |
| `construction_quality` | string | - | economy, standard, good, superior, exceptional |
| `functional_utility` | string | - | severe_obsolescence, moderate_obsolescence, adequate, superior |
| `energy_certification` | string | - | none, energy_star, leed_certified, leed_silver, leed_gold, leed_platinum |
| `architectural_appeal` | string | - | dated, average, good, exceptional |
| `hvac_system` | string | - | basic, modern_standard, high_efficiency, zoned |

#### Industrial-Specific Characteristics (10 subcategories)

| Field | Type | Range | Notes |
|-------|------|-------|-------|
| `clear_height_feet` | number | 0 - 100 | Critical for warehousing |
| `loading_docks_dock_high` | integer | 0 - 100 | Most valuable type |
| `loading_docks_grade_level` | integer | 0 - 100 | Standard type |
| `loading_docks_drive_in` | integer | 0 - 50 | Premium type |
| `column_spacing_feet` | number | 0 - 200 | Racking efficiency |
| `floor_load_capacity_psf` | number | 0 - 2,000 | Standard: 125 PSF, Heavy: 250+ PSF |
| `office_finish_percentage` | number | 0 - 100 | % of GLA finished as office |
| `bay_depth_feet` | number | 0 - 500 | Modern: 100-150 ft preferred |

#### Office-Specific Characteristics (8 subcategories)

| Field | Type | Range | Enum Values / Notes |
|-------|------|-------|---------------------|
| `building_class` | string | - | C, B-, B, B+, A-, A, A+ |
| `floor_plate_efficiency_pct` | number | 0 - 100 | Rentable/usable ratio |
| `parking_spaces_per_1000sf` | number | 0 - 20 | Typical: 3-5 per 1,000 SF |
| `ceiling_height_feet` | number | 0 - 30 | Standard: 9 ft, Premium: 10-12 ft |
| `elevator_count` | integer | 0 - 50 | - |
| `window_line_percentage` | number | 0 - 100 | % of exterior wall with windows |

#### Special Features (6 subcategories)

| Field | Type | Range | Enum Values |
|-------|------|-------|-------------|
| `rail_spur` | boolean | - | Rail access present |
| `crane_system` | string | - | none, jib_crane, bridge_crane_5ton, bridge_crane_10ton, bridge_crane_20ton, gantry_crane |
| `crane_age_years` | number | 0 - 50 | - |
| `electrical_service_amps` | number | 0 - 10,000 | Heavy industrial: 1000-2000A |
| `truck_scales` | boolean | - | Truck scales present |
| `specialized_hvac` | string | - | none, cleanroom, humidity_controlled, temperature_controlled |
| `backup_generator_kw` | number | 0 - 10,000 | Emergency power capacity |

#### Zoning/Legal (5 subcategories)

| Field | Type | Range |
|-------|------|-------|
| `zoning` | string | - |
| `floor_area_ratio` | number | 0 - 50 |
| `has_variance` | boolean | - |
| `non_conforming_use` | boolean | - |
| `lot_coverage_pct` | number | 0 - 100 |

## Comparable Sales Schema

Each comparable sale must include:

### Required Fields

- `address` (string, 5-200 chars)
- `sale_price` (number, 0 - $1,000,000,000)
- `sale_date` (string, YYYY-MM-DD format)
- `property_rights` (enum: fee_simple | leasehold | leased_fee)

### Optional Nested Objects

#### Financing Object

Required: `type` (enum: cash | seller_vtb | conventional | assumable)

Optional:
- `rate` (number, 0-30%) - Financing rate
- `market_rate` (number, 0-30%) - Market rate for comparison
- `term_years` (number, 0-50)
- `loan_amount` (number, 0+)

#### Conditions of Sale Object

Required: `arms_length` (boolean)

Optional:
- `motivation_discount_pct` (number, 0-50%) - Discount due to seller motivation

### Additional Properties

All subject property fields are also valid for comparable sales (same validation rules apply).

## Market Parameters Schema

### Required Fields

- `appreciation_rate_annual` (number, -10% to +20%) - Annual market appreciation
- `valuation_date` (string, YYYY-MM-DD format)
- `cap_rate` (number, 0-20%) - Market capitalization rate

### Optional Adjustment Parameters

All market parameters are optional except the three required fields above. The schema allows additional properties to support custom adjustment factors.

Common parameters include:
- `location_premium_per_point` (number)
- `lot_adjustment_per_acre` (number)
- `building_class_adjustment_pct_per_level` (number)
- `clear_height_value_per_foot_per_sf` (number)
- `parking_value_per_space` (number)

See sample JSON files for complete examples.

## Validation Rules

### Numeric Constraints

- Building size: 0 - 10,000,000 SF
- Lot size: 0 - 10,000 acres
- Effective age: 0 - 200 years
- Sale price: 0 - $1,000,000,000
- Percentages: 0 - 100%
- Interest rates: 0 - 30%

### String Constraints

- Address: 5-200 characters
- Date format: YYYY-MM-DD (ISO 8601)
- All enums are case-sensitive lowercase with underscores

### Array Constraints

- Comparable sales: 1-20 items minimum/maximum

## Comment Fields

The schema allows comment fields starting with `_comment` for documentation purposes. These are ignored by the calculator but help with readability.

Example:
```json
{
  "_comment_land": "===== LAND CHARACTERISTICS =====",
  "lot_size_acres": 5.2,
  "topography": "level"
}
```

## Example: Minimal Valid Input

```json
{
  "subject_property": {
    "address": "123 Main Street, City, ST",
    "property_type": "industrial",
    "property_rights": "fee_simple"
  },
  "comparable_sales": [
    {
      "address": "456 Oak Avenue, City, ST",
      "sale_price": 1500000,
      "sale_date": "2024-06-15",
      "property_rights": "fee_simple"
    }
  ],
  "market_parameters": {
    "appreciation_rate_annual": 3.5,
    "valuation_date": "2025-01-15",
    "cap_rate": 7.0
  }
}
```

## Example: Comprehensive Industrial Input

See `sample_industrial_rail_yard.json` for a complete example with:
- Rail spur access
- 20-ton bridge crane
- Heavy electrical service (1200A)
- Truck scales
- Backup generator (250kW)

## Example: Comprehensive Office Input

See `sample_office_class_a.json`, `sample_office_class_b.json`, or `sample_office_class_c.json` for complete examples covering:
- Building class (C through A+)
- Floor plate efficiency
- Parking ratios
- Elevator counts
- LEED certifications

## Schema Extensions

The `market_parameters` object uses `"additionalProperties": true` to allow custom adjustment factors not explicitly defined in the schema. This provides flexibility for specialized valuation scenarios.

For subject property and comparable sales, additional properties are **not allowed** (`"additionalProperties": false`) to ensure data consistency and catch typos.

## Integration with Calculator

The comparable sales calculator (`comparable_sales_calculator.py`) automatically validates all input files against this schema before processing. Validation errors will halt execution and display detailed error messages.

To bypass validation (not recommended):
```bash
python comparable_sales_calculator.py input.json --no-validate
```

## Compliance Standards

This schema enforces requirements from:
- **USPAP 2024** (Uniform Standards of Professional Appraisal Practice)
- **CUSPAP 2024** (Canadian Uniform Standards of Professional Appraisal Practice)
- **IVS** (International Valuation Standards)

Key compliance features:
- Sequential 6-stage adjustment hierarchy
- Required arm's length transaction disclosure
- Market conditions time adjustment
- Property rights adjustment framework
- Comprehensive physical characteristics taxonomy

---

**Last Updated**: 2025-01-15
**Schema Version**: 1.0.0
**Maintained By**: VP Real Estate - Comparable Sales Methodology Team
