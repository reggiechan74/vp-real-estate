# Relative Valuation JSON Schema Documentation

This document describes the JSON input schema for the relative valuation calculator.

## Schema Template

See `schema_template.json` for a complete, valid JSON template.

## Top-Level Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `analysis_date` | string | Yes | Analysis date in YYYY-MM-DD format (used to calculate building age) |
| `market` | string | Yes | Market description (e.g., "Mississauga Industrial") |
| `subject_property` | object | Yes | The property being analyzed |
| `comparables` | array | Yes | Array of comparable properties |
| `filters` | object | No | Must-have filters (Phase 2) |
| `weights` | object | No | Custom weights (if omitted, uses defaults) |

## Property Object Fields

### Core Fields (Required)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `address` | string | **Complete geocodable address**: "Street, City, Province PostalCode, Country" | `"2550 Stanfield Rd, Mississauga, ON L4Y 1S2, Canada"` |
| `unit` | string | Unit/suite number (empty string if none) | `"Unit 5"`, `""` |
| `year_built` | integer | Year built (building age calculated automatically) | `2020` |
| `clear_height_ft` | float | Clear ceiling height in feet | `32.0` |
| `pct_office_space` | float | **DECIMAL**: Percent office as decimal (11% = 0.11, NOT 11.0) | `0.11` |
| `parking_ratio` | float | Parking spaces per 1,000 SF | `2.5` |
| `available_sf` | integer | Available square footage | `50000` |
| `distance_km` | float | Distance from subject (0.0 for subject property) | `0.0`, `5.2` |
| `net_asking_rent` | float | Net asking rent ($/SF/year) | `9.50` |
| `tmi` | float | Taxes, maintenance, insurance ($/SF/year) | `5.00` |
| `class` | integer | Building class: 1=A, 2=B, 3=C | `2` |
| `is_subject` | boolean | **true** for subject, **false** for comparables | `true`, `false` |
| `landlord` | string | Landlord name | `"ABC Properties"` |

### Optional Fields - Existing (6)

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `shipping_doors_tl` | integer | Truck-level loading doors | `0` |
| `shipping_doors_di` | integer | Drive-in doors | `0` |
| `availability_date` | string | Availability ("Immediate", "Jan-26", etc.) | `""` |
| `power_amps` | integer | Electrical capacity in amps | `0` |
| `trailer_parking` | boolean | Trailer parking available | `false` |
| `secure_shipping` | boolean | Secure shipping area | `false` |
| `excess_land` | boolean | Excess land available | `false` |

### Optional Fields - Phase 1 (7)

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `bay_depth_ft` | float | Bay depth in feet | `0.0` |
| `lot_size_acres` | float | Lot size in acres | `0.0` |
| `hvac_coverage` | integer | HVAC: Y=1, Part=2, N=3 (ordinal) | `3` |
| `sprinkler_type` | integer | Sprinklers: ESFR=1, Standard=2, None=3 (ordinal) | `3` |
| `rail_access` | boolean | Rail siding available | `false` |
| `crane` | boolean | Overhead crane | `false` |
| `occupancy_status` | integer | Occupancy: Vacant=1, Tenant=2 (ordinal) | `2` |

### Optional Fields - Phase 2 (3)

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `grade_level_doors` | integer | Grade-level doors (for vans/small trucks) | `0` |
| `days_on_market` | integer | Days on market | `0` |
| `zoning` | string | Zoning classification | `""` |

## Filters Object (Optional)

Must-have requirements that exclude properties before ranking. See Phase 2 documentation for details.

### Filter Types

1. **Minimum value**: `"field_name_min": value` (e.g., `"clear_height_ft_min": 32`)
2. **Maximum value**: `"field_name_max": value` (e.g., `"days_on_market_max": 180`)
3. **Boolean**: `"field_name": true` (e.g., `"rail_access": true`)
4. **Exact match**: `"field_name": "value"` (e.g., `"zoning": "M2"`)
5. **Ordinal**: `"field_name": value` (e.g., `"sprinkler_type": 1` for ESFR only)

### Example Filters

```json
{
  "filters": {
    "rail_access": true,
    "clear_height_ft_min": 36,
    "sprinkler_type": 1,
    "days_on_market_max": 90,
    "zoning": "M2"
  }
}
```

## Weights Object (Optional)

Custom variable weights (must sum to 1.0). If omitted, uses default weights.

**Default Weights (25 variables):**
- Core (9): 65% total
- Existing optional (6): 12% total
- Phase 1 optional (7): 17% total
- Phase 2 optional (3): 6% total

See `schema_template.json` for complete default weight distribution.

## Critical Requirements

1. **Address format**: Must be complete and geocodable
   - Format: `"Street, City, Province PostalCode, Country"`
   - Province: Two-letter code (ON not Ontario)
   - Postal code: With space (L4Y 1S2 not L4Y1S2)
   - Unit: Store separately, NOT in address string

2. **Subject property**: Must have `distance_km: 0.0` and `is_subject: true`

3. **Comparables**: All must have `is_subject: false`

4. **Percentages**: Use decimals (11% = 0.11, NOT 11.0)
   - This applies to `pct_office_space` and weights

5. **Building age**: Provide `year_built` only; `building_age_years` is calculated automatically

## Usage Example

```bash
# Use default weights
python relative_valuation_calculator.py --input data.json --output report.md

# Use 3PL persona weights
python relative_valuation_calculator.py --input data.json --output report.md --persona 3pl

# Generate both markdown and JSON output
python relative_valuation_calculator.py --input data.json --output report.md --output-json results.json
```

## Tenant Personas

Override default weights with tenant-specific profiles:
- `--persona default` - Balanced (default if not specified)
- `--persona 3pl` - Distribution/logistics focus
- `--persona manufacturing` - Heavy industrial focus
- `--persona office` - Professional services focus

See main documentation for persona weight details.
