---
description: Before/after method for partial acquisitions with severance damages and injurious affection assessment
---

# Partial Taking Analysis

Comprehensive before/after analysis for partial property acquisitions, quantifying market value loss, severance damages to remainder, and injurious affection from construction and proximity impacts.

## Calculator Integration

**Python Calculators**:
- `.claude/skills/severance-damages-quantification/severance_calculator.py`
- `.claude/skills/injurious-affection-assessment/injurious_affection_calculator.py`

**Skills**: `severance-damages-quantification`, `injurious-affection-assessment`
**Related Skills**: `expropriation-compensation-entitlement-analysis`, `comparable-sales-adjustment-methodology`
**Shared Utils**: `Shared_Utils/financial_utils.py` (NPV, capitalization)

## Purpose

Calculate total compensation for partial property takings using:
1. **Before/After Method**: Whole property value before vs. remainder value after
2. **Severance Damages**: Access impairment, shape irregularity, utility impairment, farm operation disruption
3. **Injurious Affection**: Noise, dust, vibration, traffic, business losses, visual impacts

Formula: Total = Market Value Taken + Severance Damages + Injurious Affection

## Usage

```bash
/partial-taking-analysis <property-data> <taking-details> [--severance-type <type>] [--output <report-path>]
```

## Arguments

- `<property-data>`: Path to property data JSON (before taking)
- `<taking-details>`: Path to taking details JSON (area taken, after configuration)
- `[--severance-type]`: Primary severance type: access_impairment | shape_irregularity | utility_impairment | farm_operation_disruption
- `[--output]`: Optional output path for report

## Input Format

**Property Before Taking:**
```json
{
  "property_before": {
    "address": "Rural Route 2, Farmland Property",
    "total_area_acres": 100,
    "land_value_per_acre": 25000,
    "total_value_before": 2500000,
    "current_use": "agricultural",
    "zoning": "agricultural",
    "frontage_ft": 1320,
    "depth_ft": 3300,
    "road_classification": "collector",
    "access_points": 2
  },
  "taking_details": {
    "area_taken_acres": 15,
    "taking_location": "bisects_property",
    "new_configuration": {
      "parcel_a_acres": 42.5,
      "parcel_b_acres": 42.5,
      "frontage_lost_ft": 0,
      "creates_separate_parcels": true
    }
  },
  "severance_impacts": {
    "type": "farm_operation_disruption",
    "field_divisions_created": 2,
    "equipment_access_impaired": true,
    "irrigation_system_severed": true,
    "annual_operating_cost_increase": 15000
  },
  "injurious_affection": {
    "construction_period_months": 18,
    "equipment_types": ["excavator", "pile_driver", "concrete_truck"],
    "work_hours": "7am_to_7pm",
    "dust_generation": "high",
    "traffic_disruption_pct": 25
  }
}
```

## Workflow

1. **Load and validate inputs**
   - Property before taking (whole property)
   - Taking details and after configuration
   - Severance and injurious affection parameters

2. **Calculate market value component**
   - Value before taking: Whole property value
   - Value after taking: Sum of remainder parcels
   - Direct market value loss: Before - After

3. **Run severance damages calculator**
   ```bash
   cd .claude/skills/severance-damages-quantification
   python severance_calculator.py <severance-input.json> --output severance_results.json
   ```

   Severance types calculated:
   - **Access impairment**: Frontage loss, landlocked parcels, time-distance costs
   - **Shape irregularity**: Geometric inefficiency, buildable area reduction
   - **Utility impairment**: Severed infrastructure, relocation costs
   - **Farm operation disruption**: Field divisions, equipment access, irrigation impacts

4. **Run injurious affection calculator**
   ```bash
   cd .claude/skills/injurious-affection-assessment
   python injurious_affection_calculator.py <impacts-input.json> --output impacts_results.json
   ```

   Impact types calculated:
   - **Noise**: dBA modeling, distance attenuation, rent reduction
   - **Dust**: PM2.5/PM10 concentrations, cleaning costs
   - **Vibration**: PPV thresholds, structural damage
   - **Traffic**: Access disruption, lost sales
   - **Business losses**: Revenue reduction, fixed cost continuation
   - **Visual**: Permanent value impairment

5. **Aggregate total compensation**
   - Market value loss (before - after)
   - Severance damages (remainder impairment)
   - Injurious affection (construction + permanent impacts)
   - Total compensation = Sum of all components

6. **Generate comprehensive report**
   - Before/after property analysis
   - Severance damages breakdown
   - Injurious affection assessment
   - Total compensation summary
   - Mitigation recommendations

## Example

```bash
# Farm bisection with equipment access issues
/partial-taking-analysis farm_samples/rural_farm_before.json farm_samples/bisection_taking.json --severance-type farm_operation_disruption

# Highway frontage loss
/partial-taking-analysis commercial_samples/highway_property.json commercial_samples/frontage_taking.json --severance-type access_impairment
```

## Output Format

**Console Summary:**
```
================================================================================
PARTIAL TAKING COMPENSATION ANALYSIS
Property: Rural Route 2, Farmland Property (100 acres)
================================================================================

BEFORE/AFTER VALUATION:
--------------------------------------------------------------------------------
Value Before Taking (100 acres):           $2,500,000
Value After Taking (85 acres, 2 parcels):  $1,850,000
Direct Market Value Loss:                  $  650,000

SEVERANCE DAMAGES TO REMAINDER:
--------------------------------------------------------------------------------
Farm Operation Disruption:                 $  788,400
  - Field division costs:                  $   18,000
  - Equipment access (capitalized):        $  450,000
  - Irrigation system severance:           $  200,000
  - Annual operating cost increase:        $  120,400 (NPV 50 years)

INJURIOUS AFFECTION:
--------------------------------------------------------------------------------
Construction Impacts (18 months):          $  125,000
  - Noise impacts:                         $   45,000
  - Dust/cleaning costs:                   $   30,000
  - Traffic disruption:                    $   35,000
  - Business losses:                       $   15,000

Permanent Impacts:                         $   50,000
  - Visual impairment:                     $   50,000

Total Injurious Affection:                 $  175,000

TOTAL COMPENSATION:
================================================================================
Market Value Loss:                         $  650,000
Severance Damages:                         $  788,400
Injurious Affection:                       $  175,000
--------------------------------------------------------------------------------
TOTAL COMPENSATION:                        $1,613,400
================================================================================

✓ Report saved to: Reports/2025-11-15_151234_partial_taking_rural_farm.md
```

## Calculator Output Structure

Combined output from both calculators:

```json
{
  "total_compensation": 1613400,
  "market_value_component": {
    "value_before": 2500000,
    "value_after": 1850000,
    "direct_loss": 650000
  },
  "severance_damages": {
    "total": 788400,
    "farm_operation_disruption": {
      "field_division_costs": 18000,
      "equipment_access_npv": 450000,
      "irrigation_severance": 200000,
      "operating_cost_increase_npv": 120400
    }
  },
  "injurious_affection": {
    "total": 175000,
    "construction_impacts": 125000,
    "permanent_impacts": 50000,
    "breakdown": {
      "noise": 45000,
      "dust": 30000,
      "traffic": 35000,
      "business": 15000,
      "visual": 50000
    }
  },
  "recommendation": "Total compensation $1,613,400 reflects market value loss plus significant severance damages from farm bisection and operating cost increases. Mitigation through improved access design could reduce severance by $150K."
}
```

## Related Commands

- `/expropriation-compensation` - For full takings under OEA
- `/injurious-affection-analysis` - Detailed construction impact assessment
- `/easement-valuation` - For easement-only acquisitions

## Related Calculators

- `severance_calculator.py` - Remainder impairment (access, shape, utility, farm ops)
- `injurious_affection_calculator.py` - Construction and proximity impacts
- `Shared_Utils/financial_utils.py` - NPV, capitalization calculations

## Related Skills

- **severance-damages-quantification** - Access, shape, utility, farm operation impacts
- **injurious-affection-assessment** - Construction impacts (noise, dust, vibration, traffic, business, visual)
- **expropriation-compensation-entitlement-analysis** - Legal framework for partial takings
- **comparable-sales-adjustment-methodology** - Market value before/after analysis

## Notes

- Before/after method is standard for partial takings
- Severance damages compensate for impairment to remainder, not taking itself
- Injurious affection covers temporary (construction) and permanent (proximity) impacts
- All impacts must be reasonably foreseeable and caused by the taking
- NPV calculations typically use 50-year horizon for agricultural easements
- Mitigation measures can reduce severance damages if implemented
