---
description: Systematic evaluation of transit station site alternatives using TOD principles, multi-modal connectivity, acquisition complexity, community impact, and holdout risk assessment
argument-hint: <site-input-json> [--output <report-path>]
allowed-tools: Read, Write, Bash, Edit
---

# Transit Station Site Scoring

Comprehensive scoring framework for evaluating and comparing transit station site alternatives. Systematically assesses TOD potential, multi-modal connections, property acquisition complexity, community impacts, and holdout risk to identify optimal sites.

## Calculator Integration

**Python Calculator**: `.claude/skills/transit-station-site-acquisition-strategy/transit_station_scorer.py`
**Input Schema**: `.claude/skills/transit-station-site-acquisition-strategy/transit_station_site_input_schema.json`
**Scoring Config**: `.claude/skills/transit-station-site-acquisition-strategy/config/scoring_criteria.py`

**Skills**: `transit-station-site-acquisition-strategy`
**Related Skills**: `katy` (Transit Corridor Specialist agent - strategic TOD advice)
**Related Agents**: Katy (Transit corridor planning, station typology, TOD implementation)

## Purpose

Score transit station sites across 5 normalized categories (0-100 scale):

1. **TOD Potential** (0-100, higher better): Density, mix, walkability, development potential
2. **Multi-Modal Connections** (0-100, higher better): Bus, bike, pedestrian, parking integration
3. **Property Acquisition Complexity** (0-100, LOWER better): Ownership, displacement, environmental, legal
4. **Community Impact** (0-100, LOWER better): Displacement, gentrification, heritage, support
5. **Holdout Risk** (0-30, LOWER better): Owner motivation, sophistication, alternatives

**Normalization Note**: Raw component scores are normalized to 0-100:
- TOD Potential: Raw max 126.5 → 100
- Multi-Modal Connections: Raw max 95 → 100
- Acquisition Complexity: Already 0-100 (no normalization)
- Community Impact: Already 0-100 (no normalization)
- Holdout Risk: 0-30 scale (labeled correctly as /30)

**Composite Scores**:
- **Desirability**: (TOD + Multi-Modal) / 2
- **Feasibility**: 100 - ((Complexity + Community) / 2)
- **Overall**: 40% Desirability + 40% Feasibility + 20% Holdout (inverted)

## Usage

```bash
/transit-station-scoring <site-input-json> [--output <report-path>]
```

**Arguments**: {{args}}

## Input Format

Create JSON file with 6 sections following schema:

```json
{
  "site_identification": {
    "site_id": "SITE-A",
    "site_name": "Downtown Main Station",
    "location": "Main Street & 1st Avenue, Downtown Core",
    "station_type": "urban",
    "description": "Urban infill site in established downtown"
  },
  "tod_characteristics": {
    "population_density_per_ha": 280.0,
    "employment_density_per_ha": 195.0,
    "number_of_uses": 3,
    "jobs_housing_ratio": 1.2,
    "sidewalk_coverage_pct": 95.0,
    "crossings_quality": "excellent",
    "intersection_density_per_km2": 145.0,
    "underutilized_land_pct": 35.0,
    "zoning_supportiveness": "supportive"
  },
  "multi_modal_connections": {
    "bus_routes_within_200m": 12,
    "bus_terminal_location": "onsite",
    "bike_network_quality": "complete",
    "bike_parking_spaces": 250,
    "walkshed_population_800m": 45000,
    "kiss_ride_spaces": 25,
    "park_ride_spaces": null,
    "is_urban_station": true
  },
  "acquisition_complexity": {
    "number_of_owners": 18,
    "households_displaced": 32,
    "businesses_displaced": 12,
    "institutional_impacts": 1,
    "contamination_level": "moderate",
    "wetland_archaeological_count": 1,
    "easements_covenants_count": 8,
    "complex_tenancies_count": 4,
    "litigation_title_disputes": 2
  },
  "community_impact": {
    "total_households_displaced": 32,
    "low_income_households": 18,
    "senior_households": 8,
    "disability_households": 3,
    "neighborhood_income_level": "middle_income",
    "existing_displacement_pressure": true,
    "has_community_ties": true,
    "heritage_resources_count": 1,
    "community_support_level": "mixed"
  },
  "holdout_risk": {
    "owner_motivation": "reluctant",
    "owner_sophistication": "sophisticated",
    "owner_alternatives": "few"
  }
}
```

**Schema Documentation**: See `.claude/skills/transit-station-site-acquisition-strategy/transit_station_site_input_schema.json` for complete field definitions and thresholds.

## Workflow

1. **Parse input arguments**
   - Extract site input JSON path
   - Extract optional output report path
   - Validate file exists

2. **Load site data**
   ```bash
   # Read JSON and validate against schema
   Read <site-input-json>
   ```

3. **Run scoring calculator**
   ```bash
   cd /workspaces/lease-abstract/.claude/skills/transit-station-site-acquisition-strategy
   python transit_station_scorer.py <site-input-json> --output <results.json>
   ```

   Calculator outputs:
   - Individual category scores with breakdowns
   - Composite scores (desirability, feasibility, overall)
   - 4-tier recommendation
   - Key strengths and challenges

4. **Generate comparison report** (if multiple sites)
   - Rank sites by overall score
   - Compare category scores side-by-side
   - Identify trade-offs and optimization opportunities
   - Recommend preferred alternative

5. **Create markdown report**
   - Site scoring summary
   - Category breakdown analysis
   - Comparative analysis (if multiple sites)
   - Strategic recommendations
   - Mitigation strategies for challenges

   Save to: `/workspaces/lease-abstract/Reports/YYYY-MM-DD_HHMMSS_transit_station_scoring_<site_id>.md`

## Example Commands

### Single Site Scoring

```bash
# Score greenfield suburban site
/transit-station-scoring .claude/skills/transit-station-site-acquisition-strategy/samples/site_b_suburban_greenfield.json

# Score urban infill site
/transit-station-scoring .claude/skills/transit-station-site-acquisition-strategy/samples/site_a_urban_infill.json

# Score complex urban site with custom output
/transit-station-scoring samples/site_c_complex_urban.json --output Reports/2025-11-15_143000_site_c_analysis.md
```

### Multi-Site Comparison

```bash
# Compare all four sample sites
/transit-station-scoring samples/site_a_urban_infill.json samples/site_b_suburban_greenfield.json samples/site_c_complex_urban.json samples/site_d_balanced_suburban.json --compare

# Compare top two alternatives
/transit-station-scoring finalist_site_1.json finalist_site_2.json --compare --output comparison_report.md
```

## Output

**Console Summary:**

```
================================================================================
TRANSIT STATION SITE SCORING: Meadowlands Greenfield Station
================================================================================

SCORING RESULTS:
--------------------------------------------------------------------------------
TOD Potential:              36.0/100  (higher is better)
Multi-Modal Connections:    65.8/100  (higher is better)
Acquisition Complexity:     28.5/100  (LOWER is better)
Community Impact:           10.0/100  (LOWER is better)
Holdout Risk:                3.0/30   (LOWER is better)

COMPOSITE SCORES:
--------------------------------------------------------------------------------
Desirability Score:         50.9/100
Feasibility Score:          80.8/100
OVERALL SCORE:              70.7/100

RECOMMENDATION:
--------------------------------------------------------------------------------
RECOMMENDED - Good balance of benefits and feasibility

Key Strengths:
  ✓ Low acquisition complexity (28/100)
  ✓ Minimal community impact (10/100)
  ✓ Low holdout risk (3/30)

Key Challenges:
  ⚠ Limited TOD potential (36/100)

================================================================================

✓ Assessment complete. Detailed results saved to site_b_scoring_results.json
```

## Sample Site Performance

**Benchmarking from 4 sample sites** (`.claude/skills/transit-station-site-acquisition-strategy/samples/`):

| Rank | Site | Overall | TOD | Multi-Modal | Complexity | Community | Holdout | Recommendation |
|------|------|---------|-----|-------------|------------|-----------|---------|----------------|
| 1 | **Site B: Greenfield** | **70.7** | 36.0 | 65.8 | 28.5 ↓ | 10.0 ↓ | 3.0 ↓ | RECOMMENDED - Good feasibility |
| 2 | **Site A: Urban** | **64.9** | 83.6 | 84.2 | 69.3 | 36.5 | 20.0 | CONSIDER - High TOD, high complexity |
| 3 | **Site D: Balanced** | **63.3** | 61.2 | 73.7 | 39.8 ↓ | 25.5 | 12.0 | RECOMMENDED - Balanced trade-offs |
| 4 | **Site C: Complex** | **44.2** | 83.6 | 84.2 | 69.3 | 78.5 | 27.5 | CAUTION - High impacts |

**Legend**: ↓ = Lower is better for this metric

**Insights**:
- **Site B (Greenfield)** wins on feasibility despite lower TOD potential
- **Site A (Urban)** has highest TOD but faces acquisition/community challenges
- **Site D (Balanced Suburban)** offers middle ground across all factors
- **Site C (Complex Urban)** shows that TOD alone doesn't overcome community/holdout issues

## Scoring Categories Detail

### 1. TOD Potential (0-100, higher better)

**Components** (normalized from raw max 126.5):
- **Density** (50 points): Population + employment density
  - Population: <50/ha (low) → >300/ha (very high)
  - Employment: <20/ha (low) → >150/ha (very high)
- **Land Use Mix** (20 points): Number of uses + jobs-housing balance
  - Single-use (low) → Mixed-use 3+ (high)
  - Balanced ratio 0.75-1.5 (ideal)
- **Walkability** (26.5 points): Sidewalks + crossings + intersection density
  - Sidewalk coverage <50% (poor) → >80% (good)
  - Crossings poor/adequate/excellent
  - Intersection density <80/km² (low) → >120/km² (high)
- **Development Potential** (30.5 points): Underutilized land + zoning
  - Underutilized <10% (low) → >30% (high)
  - Zoning restrictive → supportive

### 2. Multi-Modal Connections (0-100, higher better)

**Components** (normalized from raw max 95):
- **Bus Integration** (33 points): Routes + terminal location
  - Routes: 0-2 (poor) → >10 (excellent)
  - Terminal: onsite (best) → remote (worst)
- **Cycling** (18 points): Network quality + parking spaces
  - Network: none → complete protected tracks
  - Parking: <20 (minimal) → >500 (excellent)
- **Pedestrian** (28 points): 800m walkshed population
  - <2,000 (low) → >30,000 (very high)
- **Parking** (20 points max): Kiss-ride + Park-ride OR urban bonus
  - Kiss-ride: 0 → >50 spaces
  - Park-ride: <200 → >500 spaces (suburban)
  - Urban bonus: +5 for car-free focus

### 3. Property Acquisition Complexity (0-100, LOWER better)

**Components**:
- **Ownership** (40 points): Number of owners
  - 1-2 (simple) → >15 (very complex)
- **Land Use Conflicts** (30 points): Residential + business + institutional displacement
  - Each category adds complexity
- **Environmental** (20 points): Contamination + wetlands/archaeological
  - Minimal/moderate/severe contamination
  - Each wetland/archaeological constraint adds 5-10 points
- **Legal** (10 points): Easements + tenancies + litigation
  - Each encumbrance adds 2-10 points

### 4. Community Impact (0-100, LOWER better)

**Components**:
- **Direct Displacement** (40 points): Total households + vulnerable populations
  - Base: 0 → >50 households
  - Vulnerable multipliers: Low-income, seniors, disabilities
- **Gentrification Risk** (30 points): Neighborhood income + existing pressure
  - High-income (low risk) → low-income (high risk)
  - Existing displacement pressure adds 5-10 points
- **Cultural/Heritage** (20 points): Community ties + heritage resources
  - Ethnic enclaves, multi-generational residents
  - Each heritage resource adds 5-15 points
- **Community Support** (10 points): Support → opposition
  - Support (0) → Opposition (10)

### 5. Holdout Risk (0-30, LOWER better)

**Components**:
- **Owner Motivation** (0-10): Willing → ideological
- **Owner Sophistication** (0-10): Unsophisticated → serial holdout
- **Owner Alternatives** (0-10): Strong alternatives → no alternatives (critical parcel)

**Risk Interpretation**:
- **0-10**: Low risk (likely good faith negotiation)
- **11-20**: Moderate risk (may require mediation or premium)
- **21-30**: High risk (plan for expropriation)

## Recommendation Tiers

**Overall Score Interpretation**:
- **≥75**: HIGHLY RECOMMENDED - Strong overall performance
- **60-74**: RECOMMENDED - Good balance of benefits and feasibility
- **45-59**: CONSIDER WITH CAUTION - Moderate challenges present
- **<45**: NOT RECOMMENDED - Significant obstacles

## Related Commands

- `/katy` - Invoke Katy agent for strategic TOD and corridor planning advice
- `/partial-taking-analysis` - Analyze property acquisition impacts and compensation
- `/expropriation-timeline` - Track statutory deadlines for acquisition

## Related Calculators

- `.claude/skills/severance-damages-quantification/` - Quantify severance damages for partial takings
- `.claude/skills/injurious-affection-assessment/` - Assess construction and proximity impacts
- `.claude/skills/comparable-sales-adjustment-methodology/` - Value land parcels using comparables

## Related Skills

- `transit-station-site-acquisition-strategy` - Overall framework (auto-loads with this command)
- `katy` - Transit corridor specialist agent for strategic guidance
- `expropriation-compensation-entitlement-analysis` - Legal compensation framework
- `transit-corridor-acquisition-planning` - Multi-station corridor strategy

## Notes

1. **Normalized Scoring**: TOD and Multi-Modal scores are normalized from raw maximums (126.5 and 95) to 0-100 scale for consistency with other categories

2. **Inverted Scoring**: Acquisition Complexity, Community Impact, and Holdout Risk are scored LOWER is better - higher scores indicate more challenges

3. **Composite Weighting**:
   - Desirability = (TOD + Multi-Modal) / 2
   - Feasibility = 100 - ((Complexity + Community) / 2)
   - Overall = 40% Desirability + 40% Feasibility + 20% Holdout

4. **Strategic Trade-offs**:
   - High TOD sites often have high acquisition complexity (urban infill)
   - Greenfield sites score low on TOD but high on feasibility
   - Balanced suburban sites may offer best overall compromise

5. **Multiple Site Analysis**: When comparing sites, consider:
   - Can low TOD be addressed through future development?
   - Are acquisition challenges surmountable with budget/time?
   - Is community opposition manageable through engagement?
   - Can holdout risk be mitigated through design alternatives?

6. **Schema Validation**: Input JSON must conform to schema in `transit_station_site_input_schema.json` - see schema for complete field definitions and validation rules

## Implementation Guidelines

1. **Data Quality**:
   - Use empirical data where possible (census, GIS, property records)
   - Document assumptions and data sources
   - Update scores as better data becomes available

2. **Sensitivity Analysis**:
   - Test how score changes with different assumptions
   - Identify which factors have biggest impact
   - Consider uncertainty ranges for key inputs

3. **Stakeholder Communication**:
   - Present scores in context of local priorities
   - Explain trade-offs clearly (e.g., TOD vs. feasibility)
   - Use visual comparisons for multi-site analysis

4. **Iterative Refinement**:
   - Initial scores identify strengths/weaknesses
   - Explore mitigation strategies for challenges
   - Re-score after design refinements or engagement

Begin the transit station site scoring analysis now with the provided inputs.
