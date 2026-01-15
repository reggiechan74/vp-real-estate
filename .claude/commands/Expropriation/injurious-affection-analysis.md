---
description: Quantify construction and proximity damages (noise, dust, vibration, traffic, visual, business losses) from infrastructure projects
---

# Injurious Affection Analysis

Quantify comprehensive damages from construction activities and permanent proximity impacts including noise modeling (dBA levels), dust assessment (PM2.5/PM10), vibration damage (PPV thresholds), traffic disruption, visual impairment, and business losses with detailed impact analysis.

## Calculator Integration

**Python Calculator**: `.claude/skills/injurious-affection-assessment/injurious_affection_calculator.py`
**Skill**: `injurious-affection-assessment`
**Related Skills**: `expropriation-compensation-entitlement-analysis`, `ontario-expropriations-act-statutory-interpretation`
**Calculator Modules**:
- `impacts/noise.py` - Noise modeling with dBA attenuation and receptor sensitivity
- `impacts/dust.py` - PM2.5/PM10 assessment and cleaning cost quantification
- `impacts/vibration.py` - PPV thresholds for structural, cosmetic, and annoyance impacts
- `impacts/traffic.py` - Delay costs and business access impairment
- `impacts/business.py` - Revenue loss analysis and operating cost increases
- `impacts/visual.py` - View loss and aesthetic degradation valuation

## Purpose

Generate detailed technical assessment of injurious affection damages from infrastructure projects, including:
- **Temporary construction impacts** - Noise, dust, vibration, traffic disruption during construction period
- **Permanent proximity impacts** - Visual impairment, operational noise, safety perception impacts
- **Business losses** - Revenue reduction, customer access impairment, operating cost increases
- **Technical measurements** - dBA noise modeling, particulate matter levels, peak particle velocity
- **Market evidence** - Paired sales analysis, hedonic regression for permanent impacts
- **Mitigation costs** - Temporary relocation, marketing campaigns, remediation expenses

## Usage

```bash
/injurious-affection-analysis <impact-data-path> [--output <report-path>]
```

## Arguments

- `<impact-data-path>`: Path to impact assessment JSON file (or PDF to extract from)
- `[--output]`: Optional output path for impact report (default: timestamped in Reports/)

## Input Format

The impact assessment JSON should include:

```json
{
  "property_address": "42 Maple Street, Toronto, ON M4E 2V8",
  "property": {
    "property_type": "residential",
    "property_value": 850000,
    "rental_income_monthly": 2400,
    "distance_to_construction_m": 40,
    "number_of_units": 2,
    "background_noise_dba": 52
  },
  "construction": {
    "duration_months": 6,
    "equipment": [
      {
        "equipment_type": "pile_driver",
        "dba_at_15m": 95,
        "hours_per_day": 4,
        "days_per_week": 5
      },
      {
        "equipment_type": "excavator",
        "dba_at_15m": 80,
        "hours_per_day": 8,
        "days_per_week": 5
      }
    ],
    "dust_impact_zone": "high",
    "vibration_ppv_mms": 8.5,
    "traffic_reduction_pct": 0.0,
    "construction_hours_per_day": 8,
    "night_work": false
  },
  "business_impacts": {
    "has_business_loss": false,
    "baseline_monthly_revenue": 0,
    "construction_period_revenues": [],
    "parking_spaces_lost": 0,
    "signage_blocked": false
  },
  "permanent_impacts": {
    "has_permanent_impact": false,
    "view_premium_before_pct": 0,
    "view_retention_pct": 100,
    "operational_noise_increase_dba": 0,
    "safety_stigma_discount_pct": 0
  },
  "market_parameters": {
    "residential_noise_moderate_rent_reduction_pct": 7.5,
    "residential_noise_severe_rent_reduction_pct": 20.0,
    "dust_cleaning_cost_weekly": 200,
    "vibration_annoyance_rent_reduction_pct": 10.0,
    "cosmetic_repair_cost_per_location": 1200
  }
}
```

## Workflow

1. **Load and validate input**
   - Read impact assessment data from JSON or extract from PDF
   - Validate required fields and technical parameters
   - Load skill: `injurious-affection-assessment`

2. **Run modular calculator**
   ```bash
   cd .claude/skills/injurious-affection-assessment
   python injurious_affection_calculator.py <input-json> --output results.json --verbose
   ```

3. **Parse detailed impact results**
   - Noise impact assessment (dBA modeling, attenuation calculations)
   - Dust and air quality impacts (cleaning costs, health impacts)
   - Vibration damage analysis (PPV thresholds, repair costs)
   - Traffic disruption costs (delay costs, access impairment)
   - Business loss quantification (revenue analysis, causation)
   - Visual impact valuation (view loss, aesthetic degradation)

4. **Generate comprehensive impact report**
   - Executive summary with total damages by category
   - Technical analysis for each impact type
   - Noise modeling with distance attenuation calculations
   - Vibration assessment against structural/cosmetic thresholds
   - Business loss documentation with comparative revenue analysis
   - Permanent impact valuation using market evidence
   - Mitigation costs and recommendations

5. **Calculate total injurious affection**
   - Aggregate temporary construction impacts
   - Capitalize permanent proximity impacts
   - Apply mitigation credits where applicable
   - Generate total damage assessment

6. **Return formatted report**
   - Save to Reports/ with timestamp prefix
   - Display summary with technical metrics
   - Provide detailed methodology and calculations

## Example

```bash
# Residential construction impact assessment
/injurious-affection-analysis expropriation_samples/residential_construction_impact.json

# Commercial traffic and business loss analysis
/injurious-affection-analysis expropriation_samples/commercial_traffic_impact.json

# With custom output path
/injurious-affection-analysis expropriation_samples/industrial_vibration_damage.json --output Reports/2025-11-15_injurious_affection_123_industrial.md

# Direct calculator usage with verbose output
cd .claude/skills/injurious-affection-assessment
python injurious_affection_calculator.py sample_residential_construction_impact.json --output results.json --verbose
```

## Output Format

**Console Summary:**
```
================================================================================
INJURIOUS AFFECTION DAMAGE ASSESSMENT
Property: 42 Maple Street, Toronto, ON M4E 2V8
================================================================================

CONSTRUCTION PERIOD IMPACTS (6 months):
--------------------------------------------------------------------------------
Noise Impact Assessment:
  Equipment Noise at Property (40m):
    - Pile driver (95 dBA @ 15m):        87.4 dBA (Severe - Residential)
    - Excavator (80 dBA @ 15m):          72.4 dBA (Moderate)
    - Concrete mixer (78 dBA @ 15m):     70.4 dBA (Moderate)
  Background noise:                      52.0 dBA
  Noise increase:                        +35.4 dBA (Severe impact)

  Rent Reduction (20% severe impact):    $28,800
    - Monthly rental income: $2,400
    - Duration: 6 months
    - Impact: $2,400 × 20% × 6 = $28,800

Dust Impact Assessment:
  Impact zone:                           High (0-50m from construction)
  Duration:                              6 months (26 weeks)

  Cleaning costs:                        $5,200
    - Weekly cleaning: $200/week
    - Weeks: 26 weeks
    - Total: $200 × 26 = $5,200

Vibration Impact Assessment:
  Peak Particle Velocity (PPV):          8.5 mm/s
  Threshold assessment:
    - Annoyance threshold (1.0 mm/s):    EXCEEDED (very annoying)
    - Cosmetic damage (12 mm/s):         Below threshold (no damage)
    - Structural damage (20 mm/s):       Well below threshold

  Annoyance compensation:                $1,440
    - Rent reduction: 10% × $2,400/month × 6 months = $1,440

Traffic Disruption:
  Access impact:                         None reported
  Delay costs:                           $0

CONSTRUCTION IMPACTS SUBTOTAL:           $35,440
--------------------------------------------------------------------------------

BUSINESS LOSSES:
  Revenue loss:                          $0 (no business operation)
  Operating cost increases:              $0
  Mitigation costs:                      $0

BUSINESS LOSS SUBTOTAL:                  $0
--------------------------------------------------------------------------------

PERMANENT PROXIMITY IMPACTS:
  Visual impact (view loss):             $0 (no permanent view obstruction)
  Operational noise impact:              $0 (no ongoing noise source)
  Safety perception stigma:              $0 (no proximity hazard)

PERMANENT IMPACTS SUBTOTAL:              $0
--------------------------------------------------------------------------------

TOTAL INJURIOUS AFFECTION DAMAGES:       $35,440
================================================================================

IMPACT BREAKDOWN BY TYPE:
  Noise impacts:                         $28,800 (81.3%)
  Dust/air quality:                      $5,200  (14.7%)
  Vibration:                             $1,440  (4.1%)
  Traffic disruption:                    $0      (0.0%)
  Business losses:                       $0      (0.0%)
  Visual/permanent:                      $0      (0.0%)

TECHNICAL METRICS:
  Noise increase:                        +35.4 dBA (Severe)
  Dust impact zone:                      High (0-50m)
  Vibration PPV:                         8.5 mm/s (Annoying, no damage)
  Construction duration:                 6 months (180 days)

ASSESSMENT CONFIDENCE:                   High
  ✓ Noise modeling validated with distance attenuation
  ✓ Vibration PPV below damage thresholds
  ✓ Dust impact zone consistent with construction proximity
  ✓ No business operation - revenue loss not applicable

✓ Report saved to: Reports/2025-11-15_143022_injurious_affection_42_maple.md
```

**Detailed Report** (markdown file in Reports/):
- Property identification and characteristics
- Construction activity description and timeline
- **Noise Impact Analysis**:
  - Equipment inventory with dBA levels at source
  - Distance attenuation calculations (6 dBA per doubling rule)
  - Noise at property boundary with receptor sensitivity
  - Impact classification (moderate/severe) and rent reduction
- **Dust and Air Quality Assessment**:
  - Impact zone determination (high/moderate/low)
  - PM2.5/PM10 considerations for health-sensitive receptors
  - Cleaning cost quantification (frequency × unit cost)
- **Vibration Damage Analysis**:
  - PPV measurements and threshold comparison
  - Structural damage risk assessment (cosmetic vs. structural)
  - Annoyance compensation calculation
  - Pre-construction condition documentation requirements
- **Traffic Disruption Costs**:
  - Detour analysis and delay quantification
  - Business access impairment (parking, signage)
  - Value of time calculations
- **Business Loss Documentation**:
  - Comparative revenue analysis (baseline vs. construction period)
  - Causation analysis and control factors
  - Operating cost increases
  - Mitigation efforts and costs
- **Permanent Impact Valuation**:
  - View premium analysis (before/after methodology)
  - Operational noise increase and market discount
  - Safety perception stigma (market evidence)
  - Paired sales analysis or hedonic regression
- Total damage summary with supporting calculations
- Methodology and technical standards
- Recommendations for impact mitigation

## Calculator Output Structure

The calculator returns:
```json
{
  "total_damages": 35440,
  "construction_impacts": {
    "noise_impact": 28800,
    "dust_impact": 5200,
    "vibration_impact": 1440,
    "traffic_impact": 0,
    "subtotal": 35440
  },
  "business_losses": {
    "revenue_loss": 0,
    "operating_cost_increases": 0,
    "mitigation_costs": 0,
    "subtotal": 0
  },
  "permanent_impacts": {
    "visual_impact": 0,
    "operational_noise_impact": 0,
    "safety_stigma_discount": 0,
    "subtotal": 0
  },
  "technical_metrics": {
    "noise_analysis": {
      "equipment_noise_at_property": [
        {
          "equipment": "pile_driver",
          "dba_at_source": 95.0,
          "distance_m": 40,
          "dba_at_property": 87.4,
          "impact_level": "severe"
        },
        {
          "equipment": "excavator",
          "dba_at_source": 80.0,
          "distance_m": 40,
          "dba_at_property": 72.4,
          "impact_level": "moderate"
        }
      ],
      "background_noise_dba": 52.0,
      "noise_increase_dba": 35.4,
      "impact_classification": "severe"
    },
    "vibration_analysis": {
      "ppv_mms": 8.5,
      "annoyance_threshold": 1.0,
      "cosmetic_damage_threshold": 12.0,
      "structural_damage_threshold": 20.0,
      "damage_risk": "no_damage",
      "annoyance_level": "very_annoying"
    },
    "dust_analysis": {
      "impact_zone": "high",
      "distance_m": 40,
      "cleaning_frequency": "weekly",
      "weeks": 26
    }
  },
  "property_details": {
    "address": "42 Maple Street, Toronto, ON M4E 2V8",
    "property_type": "residential",
    "property_value": 850000,
    "distance_to_construction_m": 40
  },
  "construction_details": {
    "duration_months": 6,
    "construction_hours_per_day": 8,
    "night_work": false,
    "equipment_count": 3
  }
}
```

## Related Commands

- `/expropriation-compensation` - For complete statutory compensation (s.13 + s.18 + s.18(2) + s.20)
- `/partial-taking-analysis` - For partial acquisitions with severance damages
- `/easement-valuation` - For permanent easement impacts on property value

## Related Calculators

- `injurious_affection_calculator.py` - Main impact quantification calculator (modular v2.0)
- `expropriation_compensation_calculator.py` - Integrates injurious affection into total compensation
- `impacts/noise.py` - dBA modeling with distance attenuation and receptor sensitivity
- `impacts/dust.py` - PM2.5/PM10 assessment and cleaning cost calculation
- `impacts/vibration.py` - PPV threshold analysis and damage assessment
- `impacts/traffic.py` - Delay costs and business access quantification
- `impacts/business.py` - Revenue loss analysis and operating cost increases
- `impacts/visual.py` - View premium analysis and aesthetic degradation

## Related Skills

- **injurious-affection-assessment** - Technical methodology for impact quantification
- **expropriation-compensation-entitlement-analysis** - Legal framework for s.18(2) injurious affection
- **ontario-expropriations-act-statutory-interpretation** - OEA compliance and case law

## Notes

### Noise Impact Modeling
- **Distance attenuation**: Sound decreases approximately 6 dBA per doubling of distance
- **dBA scale**: A-weighted decibels approximate human hearing sensitivity
- **Residential thresholds**: Moderate impact 65-75 dBA daytime, Severe >75 dBA or >60 dBA nighttime
- **Commercial thresholds**: Moderate 70-80 dBA, Severe >80 dBA
- **Equipment typical levels** (at 15m): Pile driver 95-105 dBA, Jackhammer 85-95 dBA, Excavator 75-85 dBA

### Vibration Thresholds
- **PPV (Peak Particle Velocity)**: Measured in mm/s
- **Structural damage**: Historic buildings 5-12 mm/s, Modern residential 12-20 mm/s, Commercial 20-50 mm/s
- **Cosmetic damage**: Cracks in plaster/drywall at 5-12 mm/s depending on building condition
- **Annoyance**: Barely perceptible 0.15-0.3 mm/s, Distinctly perceptible 0.3-1.0 mm/s, Annoying 1.0-10 mm/s
- **Pre-construction survey**: Essential to establish baseline condition for damage claims

### Dust and Air Quality
- **PM2.5**: Particles <2.5 micrometers, Ontario 24-hour standard 27 μg/m³ (respirable, health concern)
- **PM10**: Particles <10 micrometers, Ontario 24-hour standard 50 μg/m³ (coarse dust)
- **Impact zones**: High 0-50m (visible deposition), Moderate 50-150m, Low 150-300m
- **Health impacts**: Document medical costs for vulnerable populations (elderly, COPD, asthma)

### Business Loss Documentation
- **Causation critical**: Correlate revenue reduction with construction timeline, use control locations
- **Baseline establishment**: Historical comparison (3-year average), industry benchmarks, comparable locations
- **Mitigation duty**: Claimant must demonstrate reasonable efforts to minimize losses
- **Variable costs**: Deduct avoided costs (typically 30-40% for retail/restaurant) from revenue loss

### Permanent Impact Valuation
- **View premium**: Water view 15-40%, City skyline 10-25%, Green space 5-15%
- **Operational noise**: +10 dBA = 5-10% reduction, +15-20 dBA = 10-20% reduction, +25 dBA = 20-30% reduction
- **Safety stigma**: Transmission lines 5-15%, Pipelines 5-10%, Rail corridors 8-15%
- **Market evidence required**: Paired sales analysis or hedonic regression, mere perception insufficient

### Technical Standards
- All calculations comply with Ontario expropriation law and construction impact assessment best practices
- Noise modeling follows ISO 9613-2 (outdoor sound propagation)
- Vibration assessment based on DIN 4150 and BS 7385 standards
- Business loss analysis requires comparative revenue documentation and causation proof
- Permanent impacts require market evidence (paired sales, expert appraisal, hedonic regression)
