# Relative Valuation Calculator

**Multi-Criteria Decision Analysis (MCDA) for Commercial Real Estate Competitive Positioning**

## Overview

The Relative Valuation Calculator is a Python-based ranking engine that performs competitive positioning analysis for commercial real estate properties. It uses a weighted ranking methodology to determine where a subject property stands relative to market comparables, helping answer the critical question: **"At our current asking price, are we competitive enough to win deals?"**

## Methodology

The calculator implements a 4-step Multi-Criteria Decision Analysis (MCDA) framework:

### 1. Data Collection
Extract up to **25 variables** from comparable properties:
- **9 Core Variables** (65% weight) - Required: building age, clear height, office %, parking, distance, rent, TMI, class, area difference
- **16 Optional Variables** (35% weight) - Shipping doors, power, bay depth, lot size, HVAC, sprinklers, rail, crane, occupancy, grade-level doors, days on market, zoning, trailer parking, secure shipping, excess land

Variables with insufficient data in comparables automatically redistribute their weight to remaining variables.

### 2. Independent Ranking
Each variable is ranked independently from 1 (best) to X (worst):
- **Lower value = Rank 1**: Rent, TMI, Distance, Class, Area Difference
- **Higher value = Rank 1**: Clear Height, Parking, Year Built

Ties are handled using average rank methodology.

### 3. Weighted Scoring
Calculate aggregate score for each property:

```
Weighted Score = Σ(rank × weight) for all available variables (up to 25)
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

**Show All Competitors (Full Report):**
```bash
# By default, reports show top 10 competitors
# Use --full to show ALL properties (useful for large datasets like 123 properties)
python relative_valuation_calculator.py \
  --input data.json \
  --output report.md \
  --full
```

### Distance Calculation (Optional)

If your input JSON doesn't have `distance_km` values (common with MLS comp sheets), use the distance calculator:

```bash
# Set your API key (get free key at https://distancematrix.ai/)
export DISTANCEMATRIX_API_KEY=your_key_here

# Calculate distances from subject to all comparables
python calculate_distances.py \
  --input data.json \
  --output data_with_distances.json \
  --verbose

# Then run the relative valuation analysis
python relative_valuation_calculator.py \
  --input data_with_distances.json \
  --output report.md
```

**API Details:**
- **Provider**: Distancematrix.ai (https://distancematrix.ai/)
- **Free Tier**: 1,000 distance calculations/month
- **Method**: Driving distance via road network
- **Accuracy**: Uses Google Maps data

**Alternative: Skip Distance Variable**
If you don't want to use the API, set all distances to 0 and exclude distance from weights:
```json
{
  "weights": {
    "distance_km": 0.00,  // Exclude distance (0% weight)
    "net_asking_rent": 0.18,  // Increase other weights to compensate
    // ... adjust other weights to sum to 1.0
  }
}
```

### Input JSON Schema

**📄 Schema Template:** See `schema_template.json` for complete JSON template with all 25 variables

**📖 Field Documentation:** See `SCHEMA.md` for:
- Complete field reference tables (core + optional variables)
- Filter types and usage
- Weight distribution explanation
- Critical requirements and validation rules
- Usage examples with tenant personas

**Quick Start:** Copy `schema_template.json` and populate with your data, or use the simplified structure below for core variables only.

### Output

**Markdown Report Includes:**
1. **Executive Summary** - Rank, score, competitive status
2. **Subject Property Analysis** - Details and variable rankings
3. **Competitors** - Best value propositions in market
   - Default: Top 10 competitors
   - With `--full`: All competitors (entire comparison set)
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

## Getting Started

To create your first analysis:

1. **Copy the schema template:**
   ```bash
   cp schema_template.json my_analysis.json
   ```

2. **Populate with your data** - See `SCHEMA.md` for field documentation

3. **Run the analysis:**
   ```bash
   python relative_valuation_calculator.py \
     --input my_analysis.json \
     --output report.md
   ```

4. **Optional: Use tenant persona weights:**
   ```bash
   python relative_valuation_calculator.py \
     --input my_analysis.json \
     --output report.md \
     --persona 3pl
   ```

## Validation

The calculator has been validated against the original Excel template used to develop the methodology. Results match within ±0.01 tolerance for weighted scores and rankings.

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

## Enhancements (Implemented)

The following enhancements have been implemented:
- ✅ **25-Variable Model**: Expanded from 9 to 25 variables (9 core + 16 optional)
- ✅ **Tenant Personas**: Pre-configured weight profiles (default, 3PL, manufacturing, office)
- ✅ **Must-Have Filters**: Pre-ranking filters for deal-breaker requirements
- ✅ **Dynamic Weights**: Automatic weight redistribution when optional variables unavailable
- ✅ **Distance API**: Automated distance calculations via Distancematrix.ai

## Future Enhancements

- **ML Calibration**: Outcome-based weight optimization from historical deals
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

**Phase 2** - Released 2025-11-06
- 25-variable MCDA ranking engine (9 core + 16 optional)
- Tenant persona weight profiles (default, 3PL, manufacturing, office)
- Must-have filters with 5 filter types
- Dynamic weight redistribution
- PDF → JSON → Report workflow
- Command-line interface with persona support
