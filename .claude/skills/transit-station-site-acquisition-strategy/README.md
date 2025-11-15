# Transit Station Site Scoring Calculator

Systematic evaluation and comparison of transit station site alternatives using Transit-Oriented Development (TOD) principles, acquisition complexity analysis, and community impact assessment.

## Overview

This calculator scores and ranks potential transit station sites across 5 comprehensive categories, providing an objective framework for site selection decisions that balance transportation benefits with acquisition feasibility and community impacts.

## Scoring Categories

### 1. TOD Potential (0-100 points, higher is better)

Evaluates the site's ability to support transit-oriented development and maximize ridership.

**Components:**
- **Population Density** (0-25 pts): People per hectare within 800m walkshed
  - <50: 0-5 pts (low)
  - 50-150: 6-15 pts (medium)
  - 150-300: 16-20 pts (high)
  - >300: 21-25 pts (very high)

- **Employment Density** (0-25 pts): Jobs per hectare within 800m walkshed
  - <20: 0-5 pts (low)
  - 20-75: 6-15 pts (medium)
  - 75-150: 16-20 pts (high)
  - >150: 21-25 pts (very high)

- **Land Use Mix** (0-20 pts): Diversity of uses (residential, commercial, office, institutional)
  - Single-use: 0-5 pts
  - Two uses: 6-10 pts
  - Mixed-use (3+): 11-20 pts

- **Walkability** (0-20 pts): Pedestrian infrastructure quality
  - Sidewalk coverage, crossing quality, intersection density

- **Development Potential** (0-35 pts): Future growth capacity
  - Underutilized land percentage, zoning supportiveness

### 2. Multi-Modal Connections (0-100 points, higher is better)

Evaluates integration with other transportation modes and accessibility.

**Components:**
- **Bus Integration** (0-30 pts): Routes within 200m, terminal location
- **Cycling Infrastructure** (0-20 pts): Bike network quality, parking capacity
- **Pedestrian Catchment** (0-30 pts): Population within 800m walkshed
- **Auto Parking** (0-20 pts): Kiss-and-ride, park-and-ride facilities

### 3. Property Acquisition Complexity (0-100 points, LOWER is better)

Evaluates difficulty and cost of property acquisition.

**Components:**
- **Ownership Fragmentation** (0-40 pts): Number of property owners
  - 1-2 owners: 0-5 pts (simple)
  - 3-5 owners: 6-15 pts (moderate)
  - 6-15 owners: 16-30 pts (complex)
  - >15 owners: 31-40 pts (very complex)

- **Land Use Conflicts** (0-30 pts): Residential and business displacement
- **Environmental Constraints** (0-20 pts): Contamination, wetlands, archaeology
- **Legal Encumbrances** (0-10 pts): Easements, tenancies, litigation

### 4. Community Impact (0-100 points, LOWER is better)

Evaluates social and cultural impacts on affected communities.

**Components:**
- **Direct Displacement** (0-40 pts): Households displaced, with multipliers for vulnerable populations
- **Gentrification Risk** (0-30 pts): Based on neighborhood income level and existing displacement pressure
- **Cultural/Heritage** (0-20 pts): Community ties, heritage resources
- **Community Support** (0-10 pts): Support, mixed, or opposition

### 5. Holdout Risk (0-30 points, LOWER is better)

Assesses risk that critical property owners will refuse to sell at reasonable prices.

**Components:**
- **Owner Motivation** (0-10 pts): Willing, neutral, reluctant, ideological
- **Owner Sophistication** (0-10 pts): Unsophisticated, moderate, sophisticated, serial holdout
- **Alternative Options** (0-10 pts): Strength of alternative site options

## Composite Scores

The calculator generates three composite scores:

1. **Desirability Score** (0-100): Average of TOD Potential and Multi-Modal Connections
   - Measures transportation and planning benefits

2. **Feasibility Score** (0-100): Inverse of average Complexity and Community Impact
   - Formula: `100 - ((Complexity + Community Impact) / 2)`
   - Measures ease of acquisition and implementation

3. **Overall Score** (0-100): Weighted average combining all factors
   - Formula: `(Desirability × 40%) + (Feasibility × 40%) + (Holdout Risk × 20%)`
   - Holdout risk normalized: `100 - (Holdout × 100 / 30)`

## Recommendation Tiers

Based on overall score:
- **≥75**: HIGHLY RECOMMENDED - Strong benefits and feasibility
- **60-74**: RECOMMENDED - Good balance of benefits and feasibility
- **45-59**: CONSIDER WITH CAUTION - Moderate challenges present
- **<45**: NOT RECOMMENDED - Significant challenges outweigh benefits

## Installation

```bash
cd .claude/skills/transit-station-site-acquisition-strategy/calculators/transit_station_scoring
chmod +x transit_station_scorer.py
```

## Usage

### Basic Usage

```bash
./transit_station_scorer.py samples/site_a_urban_infill.json
```

### Output

The calculator produces:
1. **Console Report**: Summary of scores, composite scores, and recommendations
2. **JSON Results File**: Detailed breakdown saved to `{SITE_ID}_scoring_results_{timestamp}.json`

### Example Output

```
================================================================================
TRANSIT STATION SITE SCORING: Downtown Commerce Station
================================================================================

SCORING RESULTS:
--------------------------------------------------------------------------------
TOD Potential:               121.5/100  (higher is better)
Multi-Modal Connections:      85.5/100  (higher is better)
Acquisition Complexity:       68.5/100  (LOWER is better)
Community Impact:             53.0/100  (LOWER is better)
Holdout Risk:                 12.0/30   (LOWER is better)

COMPOSITE SCORES:
--------------------------------------------------------------------------------
Desirability Score:          103.5/100
Feasibility Score:            39.2/100
OVERALL SCORE:                69.1/100

RECOMMENDATION:
--------------------------------------------------------------------------------
RECOMMENDED - Good balance of benefits and feasibility

Key Strengths:
  ✓ Excellent TOD potential (122/100)
  ✓ Strong multi-modal connections (86/100)

Key Challenges:
  ⚠ High acquisition complexity (68/100)
  ⚠ Significant community impact (53/100)
```

## Sample Sites

Four sample sites are included to demonstrate different scenarios:

### Site A: Downtown Commerce Station (Urban Infill)
- **Type**: Urban core redevelopment
- **Overall Score**: 69.1/100 - RECOMMENDED
- **Profile**: Excellent TOD potential and multi-modal connections, but complex acquisition with multiple owners and moderate residential displacement
- **Key Challenge**: Balancing high transit benefits with acquisition complexity

### Site B: Meadowlands Greenfield Station
- **Type**: Greenfield development
- **Overall Score**: 71.9/100 - RECOMMENDED (Highest Overall)
- **Profile**: Low existing density but simple acquisition from single landowner with minimal community impact
- **Key Challenge**: Building ridership in low-density area

### Site C: Historic Chinatown Station (Complex Urban)
- **Type**: Dense urban ethnic neighborhood
- **Overall Score**: 47.7/100 - CONSIDER WITH CAUTION
- **Profile**: Exceptional TOD and multi-modal scores, but very high complexity (22 owners), significant displacement (65 households), and community opposition
- **Key Challenge**: Severe acquisition and community impacts may outweigh transportation benefits

### Site D: Oakridge Town Centre Station (Balanced Suburban)
- **Type**: Established suburban town centre
- **Overall Score**: 65.7/100 - RECOMMENDED
- **Profile**: Moderate scores across all categories - typical suburban TOD opportunity
- **Key Challenge**: No exceptional strengths but no severe weaknesses

### Key Insights from Sample Sites

**Best Overall**: Site B (Greenfield) - 71.9/100
- Demonstrates that simple acquisition and low community impact can offset lower TOD scores

**Best TOD Potential**: Site A (Urban Infill) - 121.5/100
- Shows exceptional existing density and mixed-use can exceed scoring maximums

**Easiest Acquisition**: Site B (Greenfield) - 28.5/100 complexity
- Single landowner makes execution straightforward

**Lowest Community Impact**: Site B (Greenfield) - 10.0/100 impact
- Minimal displacement of 1 household

**Most Challenging**: Site C (Complex Urban) - 47.7/100
- Despite best TOD potential, acquisition complexity and community impact severely reduce feasibility

## Comparing Multiple Sites

To compare all sample sites:

```python
import json
import glob

# Load all results
results = []
for f in glob.glob('SITE-*_scoring_results_*.json'):
    with open(f) as file:
        results.append(json.load(file))

# Sort by overall score
results.sort(key=lambda x: x['overall_score'], reverse=True)

# Print comparison
for r in results:
    print(f"{r['site_name']}: {r['overall_score']:.1f}/100 - {r['recommendation']}")
```

## Input Data Format

Input files must follow the JSON schema defined in `transit_station_site_input_schema.json`.

### Required Sections

1. **site_identification**: Site ID, name, location, station type
2. **tod_characteristics**: Density, land use mix, walkability, development potential
3. **multi_modal_connections**: Bus, bike, pedestrian, parking
4. **acquisition_complexity**: Ownership, displacement, environmental, legal
5. **community_impact**: Displacement, gentrification, heritage, support
6. **holdout_risk**: Owner motivation, sophistication, alternatives

### Example Input

```json
{
  "site_identification": {
    "site_id": "SITE-001",
    "site_name": "Main & Elm Station",
    "location": "Main Street & Elm Avenue",
    "station_type": "urban",
    "description": "Downtown mixed-use site"
  },
  "tod_characteristics": {
    "population_density_per_ha": 280.0,
    "employment_density_per_ha": 165.0,
    "number_of_uses": 4,
    "jobs_housing_ratio": 1.2,
    "sidewalk_coverage_pct": 95.0,
    "crossings_quality": "excellent",
    "intersection_density_per_km2": 145.0,
    "underutilized_land_pct": 35.0,
    "zoning_supportiveness": "supportive"
  },
  // ... other sections
}
```

See `samples/*.json` for complete examples.

## Methodology

### Scoring Philosophy

1. **Evidence-Based**: All thresholds derived from TOD and transit planning best practices
2. **Balanced**: Equally weights desirability (transit benefits) and feasibility (acquisition challenges)
3. **Transparent**: All scoring criteria documented in `config/scoring_criteria.py`
4. **Objective**: Systematic scoring reduces bias in site selection

### Interpreting Results

**High Desirability + High Feasibility** (e.g., Site B)
- Ideal scenario: Good transit benefits with manageable acquisition
- Recommendation: Proceed with confidence

**High Desirability + Low Feasibility** (e.g., Site C)
- Trade-off scenario: Excellent transit benefits but difficult acquisition
- Recommendation: Weigh benefits against costs; consider alternatives

**Low Desirability + High Feasibility** (e.g., Hypothetical greenfield with poor access)
- Poor value scenario: Easy to acquire but limited transit benefits
- Recommendation: Avoid unless strategic reasons justify

**Moderate Across Categories** (e.g., Site D)
- Typical scenario: No exceptional strengths or weaknesses
- Recommendation: Solid choice for standard TOD implementation

## Limitations

1. **Scoring ranges can exceed 100**: Sites with exceptional characteristics (e.g., very high density) may score >100 on individual categories. This is intentional to distinguish truly exceptional sites.

2. **Context-specific weights**: The 40/40/20 weighting may not suit all contexts. Adjust if needed for specific projects.

3. **Qualitative factors**: Some factors (e.g., political support, funding availability) cannot be easily quantified but may significantly impact site selection.

4. **Data quality**: Scores are only as good as input data. Verify all inputs through site visits and stakeholder consultation.

## Technical Details

- **Language**: Python 3.7+
- **Dependencies**: Standard library only (json, dataclasses, pathlib, datetime)
- **File Size**: ~710 lines (single-file implementation for simplicity)
- **Schema Standard**: JSON Schema Draft 2020-12
- **Output Format**: Timestamped JSON files with full scoring breakdown

## Future Enhancements

Potential improvements for v2.0.0:
- Modular architecture (separate scoring modules like injurious-affection-assessment)
- Configurable weights for composite scoring
- Multi-site comparison visualizations
- Sensitivity analysis for key variables
- Integration with GIS data sources
- PDF report generation

## References

- Transit-Oriented Development principles from transit-station-site-acquisition-strategy SKILL.md
- ANSI/BOMA measurement standards for area calculations
- Ontario Expropriations Act for acquisition complexity assessment
- Community impact assessment best practices

## Version History

### Version 1.0.0 (2025-11-15)
- Initial release
- 5 scoring categories with detailed breakdowns
- 3 composite scores (desirability, feasibility, overall)
- Recommendation engine with 4 tiers
- 4 sample sites demonstrating diverse scenarios
- JSON Schema validation
- Comprehensive documentation

---

For questions or issues, refer to the parent skill documentation: `../../SKILL.md`
