# RELATIVE VALUATION MODEL - PHASE 1 IMPLEMENTATION PLAN

**Plan Date**: November 5, 2025
**Objective**: Deliver simple, production-ready competitive positioning analysis
**Scope**: PDFs In → Competitive Ranking Report Out
**Timeline**: 2-3 weeks (MVP), extensible for future enhancements

---

## EXECUTIVE SUMMARY

**Phase 1 Goal**: Create a **minimum viable product (MVP)** that accepts PDF comparable evidence and produces a competitive positioning report showing where the subject property ranks in the market.

**Core Principle**: **Simplicity over sophistication** - defer advanced features (ML calibration, persona questionnaires, non-linear scoring) to Phase 2+.

**User Workflow**:
```
User provides PDFs (broker packages, CoStar exports)
         ↓
Claude extracts data to structured JSON
         ↓
Python calculator computes rankings
         ↓
Markdown report shows competitive position + pricing recommendations
```

**Deliverables**:
1. **Python Calculator** - Core ranking engine
2. **Expert Skill** - Guidance on methodology and interpretation
3. **Slash Command** - Automated workflow (PDF → Report)
4. **Sample Input/Output** - Template and example report

---

## PHASE 1 SCOPE

### **IN SCOPE** ✅

**Core Features**:
- Data extraction from PDFs (comparable evidence)
- Standard weighting schema (16% Net Rent, 15% Parking, etc.)
- Linear ranking (1=best to X=worst for each variable)
- Weighted score calculation
- Final competitive ranking (1 to X)
- Sensitivity analysis (rent reduction scenarios to achieve Top 3)
- Markdown report with:
  - Subject property ranking and score
  - Top 10 competitors
  - Gap analysis to Rank #3
  - Recommended pricing adjustments
  - Sample data table

**Data Model**:
- 9 core variables (from Excel template):
  - Year Built
  - Clear Height (ft)
  - % Office Space
  - Parking Ratio (spaces/1,000sf)
  - Distance from Subject (km)
  - Net Asking Rent ($/sf)
  - TMI ($/sf)
  - Class (A=1, B=2, C=3)
  - Difference in Area SF

**Input Format**:
- JSON (primary) - structured data ready for calculator
- PDF (via slash command) - Claude extracts to JSON first
- Subject JSON entry must include `distance_km: 0`, the weights dictionary must reuse the exact field names (`net_asking_rent`, `clear_height_ft`, etc.), and distances for comparables can be sourced via Distancematrix.ai’s nonprofit/free tier (quick setup, 1,000 elements/month) or Google Maps Distance Matrix API so long as values are stored in kilometers.

**Output Format**:
- Markdown report (timestamped in `Reports/` folder)
- Optional: CSV export of full rankings

---

### **OUT OF SCOPE** ⏸️ (Deferred to Phase 2+)

**Advanced Features** (saved as enhancement roadmap):
- ❌ Outcome-based calibration loop (quarterly ML weight updates)
- ❌ Non-linear scoring (piecewise curves, z-score normalization)
- ❌ Qualitative override layer (reputation, amenities scoring)
- ❌ Tenant persona questionnaire (dynamic weight selection)
- ❌ Gross effective rent calculations (TI allowances, free rent)
- ❌ Database persistence (SQLite/DuckDB)
- ❌ API integration (CoStar, LoopNet data pulls)
- ❌ Portfolio batch processing (multiple properties at once)
- ❌ Interactive dashboards or visualizations

**Rationale**: These are valuable but add complexity. Phase 1 proves the core concept and delivers immediate value. Once users validate the methodology, we layer in sophistication.

---

## ARCHITECTURE

### **Component Overview**

```
┌─────────────────────────────────────────────────────────────┐
│  USER INPUTS                                                 │
│  - PDF comparable evidence (broker packages, CoStar)         │
│  - Subject property details                                  │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│  SLASH COMMAND: /relative-valuation                          │
│  - Claude extracts data from PDFs                            │
│  - Generates structured JSON input                           │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│  PYTHON CALCULATOR: relative_valuation_calculator.py         │
│  1. Load comparable data (JSON)                              │
│  2. Apply standard weights (16% Rent, 15% Parking, etc.)     │
│  3. Rank each variable independently (1=best to X=worst)     │
│  4. Calculate weighted scores (Σ rank × weight)              │
│  5. Re-rank by weighted score                                │
│  6. Run sensitivity scenarios                                │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│  MARKDOWN REPORT                                             │
│  - Subject ranking (#7 out of 123)                           │
│  - Competitive status (NOT COMPETITIVE)                      │
│  - Top 10 competitors with scores                            │
│  - Gap to Rank #3 (2.30 points)                              │
│  - Recommended actions (reduce rent $0.75/sf)                │
│  - Sensitivity scenarios                                     │
└─────────────────────────────────────────────────────────────┘
```

### **File Structure**

```
Relative_Valuation/
├── relative_valuation_calculator.py   # Core ranking engine
├── sample_input.json                  # Example comparable data
├── sample_output.json                 # Example calculation results
└── README.md                          # Module documentation

.claude/skills/
└── relative-valuation-expert.md       # Methodology guidance skill

.claude/commands/Financial_Analysis/
└── relative-valuation.md              # Automated workflow slash command

Reports/
└── YYYY-MM-DD_HHMMSS_relative_valuation_[property].md
```

---

## DELIVERABLE 1: PYTHON CALCULATOR

### **File**: `Relative_Valuation/relative_valuation_calculator.py`

**Purpose**: Core ranking engine that takes comparable data and outputs competitive rankings.

### **Input Schema** (JSON)

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
      "address": "2798 Thamesgate Dr",
      "unit": "7",
      "landlord": "The Hamtor Group Inc.",
      "year_built": 1990,
      "clear_height_ft": 16,
      "pct_office_space": 0.15,
      "parking_ratio": 1.5,
      "available_sf": 3224,
      "distance_km": 13.4,
      "net_asking_rent": 8.95,
      "tmi": 6.94,
      "class": 2,
      "is_subject": false
    },
    {
      "address": "1320 Mid-Way Blvd",
      "unit": "19",
      "landlord": "2435328 Ontario Ltd.",
      "year_built": 1990,
      "clear_height_ft": 18,
      "pct_office_space": 0.40,
      "parking_ratio": 1.17,
      "available_sf": 1618,
      "distance_km": 6.8,
      "net_asking_rent": 8.95,
      "tmi": 6.10,
      "class": 2,
      "is_subject": false
    }
    // ... more comparables
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

### **Output Schema** (JSON)

```json
{
  "analysis_date": "2025-11-05",
  "market": "Greater Toronto Area - Industrial",
  "total_properties": 123,
  "subject_property": {
    "address": "123 Main Street",
    "unit": "Unit 5",
    "weighted_score": 38.61,
    "final_rank": 7,
    "competitive_status": "MARGINALLY COMPETITIVE",
    "deal_winning_probability": "30-50%"
  },
  "top_competitors": [
    {
      "rank": 1,
      "address": "5484 Tomken Rd",
      "unit": "24",
      "weighted_score": 34.18,
      "net_asking_rent": 8.75,
      "tmi": 4.25,
      "gross_rent": 13.00
    }
    // ... top 10
  ],
  "gap_analysis": {
    "gap_to_rank_3": 2.30,
    "rank_3_score": 36.31,
    "rank_3_property": "2500 Meadowpine Blvd, Unit 6"
  },
  "sensitivity_scenarios": [
    {
      "scenario": "Net Rent Reduction",
      "reduction_amount": 0.75,
      "new_net_asking_rent": 8.75,
      "estimated_new_rank": 3,
      "estimated_new_score": 36.31
    },
    {
      "scenario": "TMI Reduction",
      "reduction_amount": 0.75,
      "new_tmi": 4.75,
      "estimated_new_rank": 4,
      "estimated_new_score": 36.47
    }
  ],
  "all_properties": [
    // Full dataset with ranks
  ]
}
```

### **Key Functions**

```python
def load_comparable_data(json_path: str) -> dict:
    """Load comparable data from JSON file."""

def calculate_area_differences(properties: list, subject_sf: float) -> list:
    """Calculate |Subject SF - Comparable SF| for each property."""

def rank_variable(values: list, ascending: bool = True) -> list:
    """
    Rank values 1 (best) to X (worst).

    Args:
        values: List of numeric values
        ascending: True if lower value = better rank (e.g., rent, distance)
                   False if higher value = better rank (e.g., parking, clear height)

    Returns:
        List of ranks (1 to len(values))
    """

def calculate_weighted_score(ranks: dict, weights: dict) -> float:
    """
    Calculate weighted score = Σ(rank × weight).

    Args:
        ranks: Dict of variable ranks {'net_asking_rent': 5, 'parking_ratio': 47, ...}
        weights: Dict of variable weights {'net_asking_rent': 0.16, 'parking_ratio': 0.15, ...}

    Returns:
        Weighted score (lower = better competitive position)
    """

def run_sensitivity_analysis(subject: dict, comparables: list, weights: dict) -> list:
    """
    Run rent/TMI reduction scenarios to calculate rank improvements.

    Returns:
        List of scenarios with estimated new ranks
    """

def generate_competitive_report(results: dict, output_path: str):
    """Generate markdown report with rankings and recommendations."""
```

### **Command-Line Interface**

```bash
# Run with JSON input
python relative_valuation_calculator.py \
  --input sample_input.json \
  --output Reports/2025-11-05_125603_relative_valuation_123_main_st.md

# Run with manual inputs (interactive mode)
python relative_valuation_calculator.py --interactive

# Output JSON results only (no markdown report)
python relative_valuation_calculator.py \
  --input sample_input.json \
  --output-json results.json
```

---

## DELIVERABLE 2: EXPERT SKILL

### **File**: `.claude/skills/relative-valuation-expert.md`

**Purpose**: Provide guidance on methodology, interpretation, and strategic recommendations.

### **Frontmatter**

```yaml
---
name: relative-valuation-expert
description: Multi-criteria competitive positioning analysis for commercial real estate - determines subject property's market rank to inform pricing and deal-winning strategy
tags: [commercial-real-estate, competitive-analysis, market-positioning, pricing-strategy, deal-competitiveness]
capability: Provides specialized expertise in relative valuation methodology using weighted ranking system to assess competitive position and recommend pricing adjustments for lease transactions
proactive: true
---
```

### **Skill Content Structure**

1. **Core Methodology Overview**
   - Four-step framework (Data → Weighting → Ranking → Scoring)
   - Critical interpretation: Rank #7 = NOT competitive
   - Rule: Must be Rank #1-3 to win deals

2. **Variable Definitions & Weighting**
   - 9 core variables with descriptions
   - Standard weight schema (16% Net Rent, 15% Parking, etc.)
   - Rationale for each weight

3. **Ranking Rules**
   - Variables where lower = better (rent, TMI, distance)
   - Variables where higher = better (parking, clear height)
   - Handling Year Built (newer = better rank)

4. **Competitive Tiers & Actions**
   - Tier 1 (Rank #1-3): HOLD pricing, maximize rent
   - Tier 2 (Rank #4-10): REDUCE rent or increase incentives
   - Tier 3 (Rank #11-20): AGGRESSIVE pricing reduction
   - Tier 4 (Rank #21+): Reposition or exit

5. **Sensitivity Analysis**
   - How to calculate rent reduction needed to achieve Top 3
   - Formula: (Gap Points ÷ Net Rent Weight) × Avg $/Rank

6. **Report Interpretation**
   - Reading weighted scores
   - Understanding gap analysis
   - Implementing recommendations

7. **Common Mistakes to Avoid**
   - Assuming Rank #7 is "good" (it's not)
   - Ignoring structural disadvantages (can't fix with price alone)
   - Not validating with market intelligence

8. **Workflow Guidance**
   - When to run analysis (new listing, competitive change, 90-day review)
   - How to extract data from PDFs
   - How to validate rankings with brokers

---

## DELIVERABLE 3: SLASH COMMAND

### **File**: `.claude/commands/Financial_Analysis/relative-valuation.md`

**Purpose**: Automated workflow from PDF inputs to competitive positioning report.

### **Command Structure**

```markdown
---
description: Analyze competitive market position using multi-criteria weighted ranking - determines subject property's rank vs comparables and recommends pricing adjustments to win deals
examples:
  - "/relative-valuation path/to/comparable_evidence.pdf"
  - "/relative-valuation path/to/costar_export.pdf --subject-address '123 Main St'"
---

# Relative Valuation Analysis

You are performing a **competitive positioning analysis** using the Relative Valuation Model methodology.

## Objective

Determine where the subject property ranks competitively in its market and recommend pricing adjustments to achieve **Rank #1-3** (required to win deals with 70-90% probability).

## Workflow

### Step 1: Extract Comparable Data from PDFs

The user has provided PDF files containing comparable evidence (broker packages, CoStar exports, market surveys).

**Extract the following data for EACH comparable property** (including subject):

1. **Address** - Full street address
2. **Unit** - Unit/suite number
3. **Landlord** - Property owner (optional)
4. **Year Built** - Construction year
5. **Clear Height (ft)** - Ceiling height in feet
6. **% Office Space** - Percentage of SF that is office (0.0-1.0)
7. **Parking Ratio** - Parking spaces per 1,000 SF
8. **Available SF** - Square footage available for lease
9. **Distance from Subject (km)** - Distance between comparable and subject property
10. **Net Asking Rent ($/sf)** - Base rent before operating costs
11. **TMI ($/sf)** - Taxes, Maintenance, Insurance (operating costs)
12. **Class** - Building quality tier (A=1, B=2, C=3)

**IMPORTANT**:
- Identify which property is the SUBJECT PROPERTY (the one being analyzed)
- Subject property should have `distance_km: 0` (it's the center point)
- Calculate distances for all comparables FROM the subject property location
- Automated workflow for distances: the quickest path is Distancematrix.ai’s nonprofit/free tier (1,000 elements/month, 1 req/sec). Call `https://api.distancematrix.ai/distancematrix` with the subject address as `origins` and each comparable as `destinations`, parse `rows[].elements[].distance.value` (meters), divide by 1,000 for `distance_km`, and keep the access token in `DISTANCEMATRIX_API_KEY`. Google Maps Distance Matrix or Mapbox Directions remain viable alternatives when higher quotas or traffic modeling are required.

### Step 2: Generate JSON Input File

Create a JSON file following this structure:

```json
{
  "analysis_date": "YYYY-MM-DD",
  "market": "Market Name - Property Type",
  "subject_property": {
    "address": "...",
    "unit": "...",
    "year_built": ...,
    "clear_height_ft": ...,
    "pct_office_space": ...,
    "parking_ratio": ...,
    "available_sf": ...,
    "distance_km": 0.0,
    "net_asking_rent": ...,
    "tmi": ...,
    "class": ...,
    "is_subject": true
  },
  "comparables": [
    {
      "address": "...",
      "unit": "...",
      "landlord": "...",
      "year_built": ...,
      "clear_height_ft": ...,
      "pct_office_space": ...,
      "parking_ratio": ...,
      "available_sf": ...,
      "distance_km": ...,
      "net_asking_rent": ...,
      "tmi": ...,
      "class": ...,
      "is_subject": false
    }
    // ... all comparables
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

Save this to: `/workspaces/lease-abstract/Relative_Valuation/input_YYYY-MM-DD_HHMMSS.json`

### Step 3: Run Python Calculator

Execute the calculator:

```bash
python /workspaces/lease-abstract/Relative_Valuation/relative_valuation_calculator.py \
  --input /workspaces/lease-abstract/Relative_Valuation/input_YYYY-MM-DD_HHMMSS.json \
  --output /workspaces/lease-abstract/Reports/YYYY-MM-DD_HHMMSS_relative_valuation_[property_name].md
```

### Step 4: Review and Summarize Results

After the calculator completes:

1. **Read the generated markdown report**
2. **Summarize key findings** for the user:
   - Subject property's final rank (e.g., #7 out of 123)
   - Competitive status (Market Leader, Competitive, Marginally Competitive, Not Competitive)
   - Deal-winning probability
   - Gap to Rank #3
   - **RECOMMENDED ACTION** (specific rent reduction or incentive increase)

3. **Provide strategic interpretation**:
   - If Rank #1-3: Congratulate - hold or increase pricing
   - If Rank #4-10: Explain NOT competitive, must take action
   - If Rank #11+: Explain serious competitive disadvantage, major action required

4. **Present the report path** so user can review full analysis

## Critical Interpretation

**IMPORTANT**:
- **Rank #1-3** = Competitive (70-90% win probability)
- **Rank #4-10** = NOT Competitive (30-50% win probability) → Action required
- **Rank #11+** = Serious disadvantage (<25% win probability) → Major intervention

**If subject is NOT Rank #1-3**, emphasize that:
> "Your property is NOT competitive at current pricing. [X] other properties offer better value.
> To win deals, you must reduce rent by $[Y]/sf OR offer $[Z]/sf in TI allowances to move into Top 3."

## Example Output Message

"I've completed the relative valuation analysis for [Subject Property].

**KEY FINDINGS:**

**Competitive Position**: Rank #7 out of 123 comparables
**Weighted Score**: 38.61 (lower is better)
**Status**: ⚠️ **MARGINALLY COMPETITIVE** - NOT in Top 3
**Deal-Winning Probability**: 30-50%

**PROBLEM**: 6 other properties offer superior value at their asking prices. Tenants shopping the market will shortlist those properties first.

**RECOMMENDED ACTION**:
Reduce net asking rent by **$0.75/sf** (from $9.50/sf → $8.75/sf)
- This will move your property to **Rank #3**
- Expected improvement: Weighted Score 38.61 → 36.31
- New deal-winning probability: **70-80%**

**Top 3 Competitors** (your pricing targets):
1. 5484 Tomken Rd Unit 24 - $8.75/sf net (Score: 34.18)
2. 2179 Dunwin Dr Unit 3 - $8.95/sf net (Score: 36.09)
3. 2500 Meadowpine Unit 6 - $9.00/sf net (Score: 36.31)

Full analysis report: `Reports/2025-11-05_125603_relative_valuation_123_main_st.md`"
```

---

## DELIVERABLE 4: SAMPLE DATA

### **File**: `Relative_Valuation/sample_input.json`

Use the data from the Excel template (first 20-30 properties) to create a realistic sample.

### **File**: `Relative_Valuation/sample_output.json`

Pre-calculated results from sample input for validation.

---

## IMPLEMENTATION TIMELINE

### **Week 1: Core Calculator**

**Days 1-2**: Setup & Data Model
- Create `Relative_Valuation/` module directory
- Define JSON input/output schemas
- Write data loading functions
- Create sample input JSON from Excel data

**Days 3-4**: Ranking Engine
- Implement `rank_variable()` function
- Implement `calculate_area_differences()` function
- Implement `calculate_weighted_score()` function
- Write unit tests for ranking logic

**Day 5**: Sensitivity Analysis
- Implement `run_sensitivity_analysis()` function
- Test scenarios (rent reduction, TMI reduction)

### **Week 2: Report Generation & Skill**

**Days 1-2**: Report Generator
- Implement `generate_competitive_report()` function
- Create markdown template
- Format tables, sensitivity scenarios
- Test with sample data

**Days 3-4**: Expert Skill
- Write `.claude/skills/relative-valuation-expert.md`
- Include methodology, interpretation, strategic guidance
- Add examples and common mistakes

**Day 5**: Testing & Documentation
- Run end-to-end test with sample data
- Write `Relative_Valuation/README.md`
- Document all functions with docstrings

### **Week 3: Slash Command & Polish**

**Days 1-2**: Slash Command
- Write `.claude/commands/Financial_Analysis/relative-valuation.md`
- Test PDF extraction workflow
- Validate JSON generation

**Days 3-4**: User Testing
- Run with real comparable PDFs
- Validate rankings against Excel
- Refine report formatting

**Day 5**: Documentation & Delivery
- Update main README.md
- Update CHANGELOG.md (Version 1.3.0)
- Create user guide with examples

---

## TESTING STRATEGY

### **Unit Tests**

Test each function independently:

```python
def test_rank_variable_ascending():
    """Test ranking where lower value = Rank 1 (e.g., rent)."""
    values = [10.0, 8.5, 9.0, 12.0]
    expected_ranks = [3, 1, 2, 4]
    assert rank_variable(values, ascending=True) == expected_ranks

def test_rank_variable_descending():
    """Test ranking where higher value = Rank 1 (e.g., parking)."""
    values = [1.5, 2.0, 0.8, 1.2]
    expected_ranks = [2, 1, 4, 3]
    assert rank_variable(values, ascending=False) == expected_ranks

def test_weighted_score_calculation():
    """Test weighted score calculation."""
    ranks = {
        'net_asking_rent': 5,
        'parking_ratio': 47,
        'tmi': 117,
        'clear_height_ft': 44
    }
    weights = {
        'net_asking_rent': 0.16,
        'parking_ratio': 0.15,
        'tmi': 0.14,
        'clear_height_ft': 0.10
    }
    # Expected: (5*0.16) + (47*0.15) + (117*0.14) + (44*0.10) = 0.8 + 7.05 + 16.38 + 4.4 = 28.63
    assert calculate_weighted_score(ranks, weights) == pytest.approx(28.63)
```

### **Integration Test**

Run full workflow with sample data and validate output:

```bash
python relative_valuation_calculator.py \
  --input Relative_Valuation/sample_input.json \
  --output Reports/test_output.md

# Validate:
# 1. Subject property ranked #7
# 2. Weighted score = 38.61
# 3. Top 3 competitors present
# 4. Sensitivity scenarios calculated
# 5. Markdown report generated
```

### **Excel Validation**

Compare Python calculator results against Excel template:
- Load same 123 properties
- Verify ranks match for all variables
- Verify weighted scores match (±0.01 tolerance)
- Verify final rankings match

---

## SUCCESS CRITERIA

Phase 1 is complete when:

✅ **Functional**:
1. Calculator accepts JSON input and produces correct rankings
2. Results match Excel template calculations (validated on 20+ properties)
3. Markdown report is clear, actionable, and professionally formatted
4. Slash command successfully extracts data from PDFs and runs analysis
5. Skill provides helpful guidance on methodology and interpretation

✅ **Documented**:
6. README.md explains usage with examples
7. All functions have docstrings
8. Sample input/output files demonstrate workflow

✅ **User Experience**:
9. User can go from PDF to report in <10 minutes
10. Report clearly states: "You are Rank #X - you are/are not competitive"
11. Recommended actions are specific and quantified ("Reduce rent by $0.75/sf")

---

## FUTURE ENHANCEMENTS (Phase 2+)

**Saved for later** (from advanced enhancements in methodology report):

### **Phase 2: Advanced Analytics**
- Outcome-based calibration loop (ML weight updates)
- Non-linear scoring (piecewise curves, z-scores)
- Qualitative override layer (reputation, amenities)

### **Phase 3: Operational Efficiency**
- Tenant persona questionnaire (auto-select weights)
- Gross effective rent calculations (TI allowances, free rent)
- Portfolio batch processing (analyze 10+ properties at once)

### **Phase 4: Integration & Automation**
- Database persistence (SQLite/DuckDB)
- API integration (CoStar, LoopNet data pulls)
- Interactive dashboards (web UI)
- Real-time market monitoring (alert when ranking changes)

---

## DELIVERABLE CHECKLIST

Before marking Phase 1 complete, ensure:

- [ ] `Relative_Valuation/relative_valuation_calculator.py` created and tested
- [ ] `Relative_Valuation/sample_input.json` created from Excel data
- [ ] `Relative_Valuation/sample_output.json` pre-calculated results
- [ ] `Relative_Valuation/README.md` module documentation
- [ ] `.claude/skills/relative-valuation-expert.md` skill created
- [ ] `.claude/commands/Financial_Analysis/relative-valuation.md` slash command created
- [ ] Sample report generated: `Reports/YYYY-MM-DD_HHMMSS_relative_valuation_sample.md`
- [ ] Unit tests written and passing (10+ tests)
- [ ] Excel validation completed (results match ±0.01)
- [ ] End-to-end test with real PDF completed
- [ ] User guide section added to main README.md
- [ ] CHANGELOG.md updated (Version 1.3.0)

---

## RISKS & MITIGATION

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **PDF extraction fails** for complex broker packages | High | Medium | Provide manual JSON input fallback; improve extraction prompts iteratively |
| **Rankings don't match Excel** due to tie-handling | Medium | Low | Use RANK.AVG() for ties; document tie-breaking rules clearly |
| **User misinterprets Rank #7 as "good"** | High | Medium | Make report messaging VERY CLEAR: "NOT COMPETITIVE" in bold, explain 6 properties are better |
| **Incomplete comparable data** (missing parking, TMI) | Medium | High | Allow optional fields; flag missing data in report; use defaults where reasonable |
| **Weights don't match user's market** | Medium | Medium | Provide weight customization in JSON; document standard schema; defer persona questionnaire to Phase 2 |

---

## CONCLUSION

Phase 1 delivers a **simple, production-ready tool** that proves the methodology and provides immediate value:

**Value Proposition**:
- **For landlords**: Know exactly where you stand competitively and what price adjustment wins deals
- **For brokers**: Quantify competitive positioning for clients with data-driven recommendations
- **For asset managers**: Optimize portfolio pricing systematically vs gut feel

**What makes it successful**:
1. **Simplicity**: PDFs → Report (no complex setup)
2. **Clarity**: "You are Rank #7 = NOT competitive, reduce rent by $0.75/sf"
3. **Actionability**: Specific, quantified recommendations
4. **Validation**: Results match proven Excel methodology
5. **Extensibility**: Clean architecture ready for Phase 2 enhancements

Once Phase 1 is validated by users, we layer in the sophisticated features (ML calibration, persona questionnaires, effective rent) that transform this into a best-in-class competitive intelligence platform.

---

**END OF PHASE 1 IMPLEMENTATION PLAN**

*Next Step: Begin Week 1, Days 1-2 - Setup & Data Model*
