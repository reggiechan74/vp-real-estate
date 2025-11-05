# Relative Valuation: Competitive Positioning Analysis

**Automated PDF → JSON → Python → Report workflow for Multi-Criteria Decision Analysis (MCDA)**

You are executing the **/relative-valuation** slash command. Your task is to perform a complete competitive positioning analysis using the relative valuation methodology.

## Objective

Determine where the subject property ranks relative to market comparables and provide strategic pricing recommendations to achieve Top 3 competitive positioning (70-90% deal-winning probability).

## Workflow Steps

### Step 1: Activate Relative Valuation Expert Skill

First, load the relative valuation expert skill to access specialized methodology knowledge:

```
Use Skill tool: relative-valuation-expert
```

### Step 2: Extract Data from PDF Documents

The user will provide one or more PDF documents containing:
- Subject property details
- Comparable property data (CoStar reports, broker packages, market surveys)

**Your tasks:**
1. Extract all properties with the following attributes:
   - Address & Unit
   - Year Built
   - Clear Height (ft)
   - % Office Space
   - Parking Ratio (spaces per 1,000 SF)
   - Available SF
   - Distance from Subject (km) - Calculate or estimate if not provided
   - Net Asking Rent ($/SF/year)
   - TMI ($/SF/year)
   - Class (A/B/C)

2. Identify which property is the subject property (distance = 0)

3. If distance data is missing:
   - Note: "Distance calculations deferred - using estimated values"
   - Use approximate distances based on address locations
   - Flag for manual review

### Step 3: Create Input JSON File

Build a properly formatted JSON file following this schema:

```json
{
  "analysis_date": "YYYY-MM-DD",
  "market": "Market Name - Property Type",
  "subject_property": {
    "address": "...",
    "unit": "...",
    "year_built": 0,
    "clear_height_ft": 0.0,
    "pct_office_space": 0.0,
    "parking_ratio": 0.0,
    "available_sf": 0,
    "distance_km": 0.0,
    "net_asking_rent": 0.0,
    "tmi": 0.0,
    "class": 2,
    "is_subject": true
  },
  "comparables": [
    {
      "address": "...",
      "unit": "...",
      "year_built": 0,
      "clear_height_ft": 0.0,
      "pct_office_space": 0.0,
      "parking_ratio": 0.0,
      "available_sf": 0,
      "distance_km": 0.0,
      "net_asking_rent": 0.0,
      "tmi": 0.0,
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

**Critical Requirements:**
- Subject property MUST have `distance_km: 0.0` and `is_subject: true`
- All comparables MUST have `is_subject: false`
- Class values: 1 (A), 2 (B), 3 (C)
- Weights MUST sum to 1.0
- All rent/TMI values in $/SF/year (convert monthly to annual if needed)
- Parking ratio in spaces per 1,000 SF (convert if needed)

**Save to**: `Reports/YYYY-MM-DD_HHMMSS_relative_valuation_input.json`

### Step 4: Run Python Calculator

Execute the relative valuation calculator:

```bash
python3 Relative_Valuation/relative_valuation_calculator.py \
  --input Reports/YYYY-MM-DD_HHMMSS_relative_valuation_input.json \
  --output Reports/YYYY-MM-DD_HHMMSS_relative_valuation_report.md \
  --output-json Reports/YYYY-MM-DD_HHMMSS_relative_valuation_output.json
```

This generates:
- **Markdown Report**: Complete analysis with recommendations
- **JSON Output**: Structured results for programmatic use

### Step 5: Interpret Results Using Expert Knowledge

After the calculator runs, analyze the results and provide strategic guidance:

1. **Summarize Competitive Position**
   - Subject property rank (e.g., "#7 out of 25")
   - Weighted score
   - Competitive tier (Highly/Moderately/Not Competitive)

2. **Identify Key Strengths and Weaknesses**
   - Which variables rank well (Top 5)?
   - Which variables rank poorly (Bottom 5)?
   - Highlight highest-weighted variables (rent, parking, TMI)

3. **Provide Strategic Recommendations**
   - If Rank #1-3: Maintain position, defend pricing
   - If Rank #4-10: Recommend specific pricing adjustments to reach Top 3
   - If Rank #11+: Flag urgent need for repositioning

4. **Run Sensitivity Analysis**
   - Show exactly how much rent/TMI reduction needed to achieve Rank #3
   - Present 2-3 scenarios (rent only, TMI only, combined)
   - Calculate impact on landlord's effective rent if relevant

5. **Consider Non-Price Levers**
   - If price reduction not feasible, suggest alternatives:
     - Increased TI allowance
     - Free rent periods
     - Operating cost caps
     - Lease flexibility (termination rights, expansion options)

### Step 6: Generate Executive Summary

Create a concise executive summary for the user:

```markdown
## EXECUTIVE SUMMARY: COMPETITIVE POSITIONING

**Subject Property**: [Address]
**Analysis Date**: [Date]
**Market**: [Market Name]

### Current Position
- **Rank**: #X out of Y properties
- **Weighted Score**: XX.XX (lower is better)
- **Status**: [Highly/Moderately/Not] Competitive
- **Deal-Winning Probability**: XX-XX%

### Key Findings
1. [Top strength - e.g., "Best net rent in market ($8.95 vs. avg $9.50)"]
2. [Key weakness - e.g., "Below-average parking ratio (1.5 vs. avg 2.0)"]
3. [Critical insight - e.g., "6 properties offer better overall value"]

### Strategic Recommendation
[Action-oriented recommendation based on rank tier]

### Next Steps
1. [Immediate action - e.g., "Reduce rent to $8.75 to achieve Rank #3"]
2. [Secondary action - e.g., "Monitor top 3 competitors weekly"]
3. [Long-term - e.g., "Consider capital investment in parking expansion"]
```

## Error Handling

**If insufficient data:**
- Request additional information from user
- Document assumptions made (e.g., "Parking ratio assumed at 1.5 based on typical industrial standards")
- Flag data quality issues in final report

**If calculator fails:**
- Validate JSON schema is correct
- Check that weights sum to 1.0
- Verify subject property has distance_km: 0.0
- Confirm all required fields are present

**If results are unexpected:**
- Review data extraction for errors (e.g., monthly rent entered instead of annual)
- Verify comparable properties are truly comparable (same market, property type)
- Check for outliers that may skew rankings

## Output Files

All files must use timestamp prefix `YYYY-MM-DD_HHMMSS`:

1. **Input JSON**: `Reports/YYYY-MM-DD_HHMMSS_relative_valuation_input.json`
2. **Output JSON**: `Reports/YYYY-MM-DD_HHMMSS_relative_valuation_output.json`
3. **Markdown Report**: `Reports/YYYY-MM-DD_HHMMSS_relative_valuation_report.md`

## Example Usage

```
User: "Analyze competitive positioning for 2798 Thamesgate Dr using this CoStar report"
[Attaches PDF]