# Relative Valuation Calculator

**Multi-Criteria Decision Analysis (MCDA) for Commercial Real Estate Competitive Positioning**

## Overview

The Relative Valuation Calculator is a Python-based ranking engine that performs competitive positioning analysis for commercial real estate properties. It uses a weighted ranking methodology to determine where a subject property stands relative to market comparables, helping answer the critical question: **"At our current asking price, are we competitive enough to win deals?"**

## Methodology

The calculator implements a 4-step Multi-Criteria Decision Analysis (MCDA) framework:

### 1. Data Collection
Extract 9 key variables from comparable properties:
- **Year Built** (8% weight)
- **Clear Height** (10% weight)
- **% Office Space** (10% weight)
- **Parking Ratio** (15% weight) - spaces per 1,000 SF
- **Distance from Subject** (10% weight)
- **Net Asking Rent** (16% weight - highest)
- **TMI** (14% weight) - tenant operating costs
- **Class** (7% weight) - A/B/C
- **Area Difference** (10% weight) - size match to subject

### 2. Independent Ranking
Each variable is ranked independently from 1 (best) to X (worst):
- **Lower value = Rank 1**: Rent, TMI, Distance, Class, Area Difference
- **Higher value = Rank 1**: Clear Height, Parking, Year Built

Ties are handled using average rank methodology.

### 3. Weighted Scoring
Calculate aggregate score for each property:

```
Weighted Score = Σ(rank × weight) for all 9 variables
```

**Lower weighted score = better competitive position**

### 4. Final Competitive Ranking
Sort properties by weighted score ascending:
- **Rank #1-3**: Highly Competitive (70-90% win probability)
- **Rank #4-10**: Moderately Competitive (50-70% win probability)
- **Rank #11+**: Not Competitive (<50% win probability)

## Critical Interpretation

If your subject property ranks **#7**, this means:
- **6 other properties offer better value** at current pricing
- You are **NOT competitive** at your asking price
- You must lower rent/TMI or improve offerings to reach Rank #1-3

The calculator provides sensitivity analysis showing exactly how much you need to adjust pricing to achieve Rank #3 (competitive threshold).

## Installation

Requires Python 3.8+ with:
```bash
pip install pandas
```

No other dependencies required. The calculator is a standalone Python script.

## Usage

### Command-Line Interface

**Generate Markdown Report:**
```bash
python relative_valuation_calculator.py --input data.json --output report.md
```

**Generate JSON Results:**
```bash
python relative_valuation_calculator.py --input data.json --output-json results.json
```

**Generate Both:**
```bash
python relative_valuation_calculator.py \
  --input data.json \
  --output report.md \
  --output-json results.json
```

### Input JSON Schema

```json
{
  "analysis_date": "2025-11-05",
  "market": "Greater Toronto Area - Industrial",
  "subject_property": {
    "address": "123 Main Street",
    "unit": "Unit 5",
    "year_built": 1985,
    "clear_height_ft": 16,
    "pct_office_space": 0.20,
    "parking_ratio": 1.5,
    "available_sf": 2200,
    "distance_km": 0.0,
    "net_asking_rent": 9.50,
    "tmi": 5.50,
    "class": 2,
    "is_subject": true
  },
  "comparables": [
    {
      "address": "456 Industrial Ave",
      "unit": "Suite 100",
      "year_built": 1990,
      "clear_height_ft": 18,
      "pct_office_space": 0.15,
      "parking_ratio": 2.0,
      "available_sf": 2500,
      "distance_km": 2.5,
      "net_asking_rent": 9.00,
      "tmi": 5.00,
      "class": 2,
      "is_subject": false
    }
  ],
  "weights": {
    "year_built": 0.08,
    "clear_height_ft": 0.10,
    "pct_office_space": 0.10,
    "parking_ratio": 0.15,
    "distance_km": 0.10,
    "net_asking_rent": 0.16,
    "tmi": 0.14,
    "class": 0.07,
    "area_difference": 0.10
  }
}
```

**Important Field Requirements:**
- `distance_km`: Must be `0.0` for subject property (center point)
- `is_subject`: Must be `true` for subject, `false` for comparables
- `class`: 1 (Class A), 2 (Class B), 3 (Class C)
- `weights`: Must sum to 1.0
- All rent values in $/SF/year

### Output

**Markdown Report Includes:**
1. **Executive Summary** - Rank, score, competitive status
2. **Subject Property Analysis** - Details and variable rankings
3. **Top 10 Competitors** - Best value propositions in market
4. **Gap Analysis** - Distance to Rank #3 threshold
5. **Sensitivity Scenarios** - Pricing adjustments needed
6. **Strategic Recommendations** - Action items based on rank tier
7. **Methodology** - Explanation of ranking framework

**JSON Output Includes:**
- Complete property data with all rankings
- Weighted scores and final ranks
- Gap analysis metrics
- Sensitivity scenarios
- Full methodology for transparency

## Sample Data

Sample files are included for testing:
- `sample_input.json` - 25 properties from May 2020 GTA industrial market
- `sample_output.json` - Pre-calculated results
- `sample_report.md` - Generated markdown report

**Run sample analysis:**
```bash
python relative_valuation_calculator.py \
  --input sample_input.json \
  --output test_report.md
```

## Validation

The calculator has been validated against the original Excel template used to develop the methodology. Results match within ±0.01 tolerance for weighted scores and rankings.

**Test against Excel:**
```bash
python relative_valuation_calculator.py \
  --input sample_input.json \
  --output-json test_output.json

# Compare test_output.json against sample_output.json
# Weighted scores should match within 0.01
```

## Ranking Rules

### Variables Ranked Ascending (Lower Value = Better)
- **Net Asking Rent** - Lower rent more competitive
- **TMI** - Lower operating costs more attractive
- **Distance** - Closer to subject location preferred
- **Class** - 1 (A) beats 2 (B) beats 3 (C)
- **Area Difference** - Smaller size mismatch preferred

### Variables Ranked Descending (Higher Value = Better)
- **Clear Height** - Higher ceilings preferred for industrial
- **Parking Ratio** - More parking better
- **Year Built** - Newer buildings preferred
- **% Office Space** - More office space usually preferred

## Limitations

1. **Assumes Linear Preferences**: Variables ranked independently without interaction effects
2. **Fixed Weights**: Standard weights may not apply to all tenant personas
3. **No Qualitative Factors**: Doesn't account for:
   - Building quality/condition
   - Landlord reputation
   - Property management quality
   - Specific tenant requirements
4. **Market-Specific**: Weights calibrated for GTA industrial market (May 2020)
5. **Point-in-Time**: Reflects market conditions at analysis date

## Phase 2 Enhancements (Future)

The following features are planned for future versions:
- **Custom Weights**: Tenant persona-based weight adjustments
- **ML Calibration**: Outcome-based weight optimization
- **Qualitative Overrides**: Manual adjustments for special factors
- **Distance API**: Automated distance calculations via Distancematrix.ai
- **PDF Extraction**: Automated data extraction from comp packages
- **Database Integration**: Portfolio tracking and historical analysis

## Technical Details

**Core Functions:**
- `load_comparable_data()` - Load and validate JSON input
- `calculate_area_differences()` - Compute size match scores
- `rank_variable()` - Rank values with tie-handling
- `calculate_weighted_score()` - Compute aggregate scores
- `run_sensitivity_analysis()` - Calculate pricing adjustments
- `generate_competitive_report()` - Create markdown report
- `run_analysis()` - Main orchestration function

**Data Structures:**
- `Property` dataclass - Holds property attributes and rankings
- `CompetitiveAnalysis` dataclass - Results container

## License

Proprietary - Commercial Real Estate Lease Management Toolkit

## References

- **Methodology Documentation**: `/Reports/2025-11-05_122834_relative_valuation_methodology_framework.md`
- **Implementation Plan**: `/Reports/2025-11-05_125603_relative_valuation_phase1_implementation_plan.md`
- **Original Excel Template**: `/skillsdevdocs/Relative Valuation Template for newsletter.xlsx`

## Support

For issues or questions about the calculator:
1. Review sample files and methodology documentation
2. Validate input JSON schema matches specification
3. Check that weights sum to 1.0
4. Verify subject property has `distance_km: 0.0` and `is_subject: true`

## Version

**Phase 1 MVP** - Released 2025-11-05
- Core ranking engine
- PDF → JSON → Report workflow
- 9 variables with standard weights
- Command-line interface
- Sample data validation
