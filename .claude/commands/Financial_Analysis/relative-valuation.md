---
description: Multi-criteria competitive positioning analysis - ranks subject against comparables using up to 15 weighted variables (core + optional), generates strategic pricing recommendations with landscape PDF output
argument-hint: <pdf-or-json-path> [--full]
allowed-tools: Read, Write, Bash
---

# Relative Valuation: Competitive Positioning Analysis

**Automated PDF → JSON → Python → Report workflow for Multi-Criteria Decision Analysis (MCDA)**

You are executing the **/relative-valuation** slash command. You are an expert in **Relative Valuation** and **Competitive Positioning Analysis** for commercial real estate, specializing in Multi-Criteria Decision Analysis (MCDA).

## Objective

Determine where the subject property ranks relative to market comparables and provide strategic pricing recommendations to achieve Top 3 competitive positioning (70-90% deal-winning probability).

## Core Methodology: MCDA Framework

### The Variable System: Core (9) + Optional (16) = Up to 25 Total

**Dynamic Weighting**: The system uses 9 core variables (always included) plus 16 optional variables (included only if sufficient data is available - 50% threshold for numeric fields, at least one True for boolean fields). When optional variables are missing, their weights are redistributed proportionally among available variables.

#### Full Variable Set (When All Data Available - 25 Variables)

| Variable | Weight | Type | Rationale |
|----------|--------|------|-----------|
| **Net Asking Rent** | 11% | Core | **Most critical** - Direct impact on tenant budget |
| **Parking Ratio** | 10% | Core | **Second most critical** - Often deal-breaker for industrial/office |
| **TMI** | 9% | Core | Affects total occupancy cost |
| **Clear Height** | 7% | Core | Critical for industrial operations |
| **% Office Space** | 7% | Core | Mix affects usability |
| **Distance** | 7% | Core | Location convenience |
| **Area Difference** | 7% | Core | Size match to tenant needs |
| **Building Age** | 4% | Core | Replaces Year Built - more intuitive condition proxy |
| **Class** | 5% | Core | A/B/C quality tier |
| **Bay Depth** | 5% | Optional | Racking efficiency, trailer access |
| **Shipping Doors (TL)** | 4% | Optional | Truck-level loading capacity |
| **Lot Size (Acres)** | 4% | Optional | Expansion potential, outdoor storage |
| **Shipping Doors (DI)** | 3% | Optional | Drive-in door access |
| **Power** | 3% | Optional | Electrical capacity (amps) |
| **HVAC Coverage** | 3% | Optional | Climate control for products/workers |
| **Sprinkler Type** | 3% | Optional | ESFR = insurance savings + high-piled storage |
| **Trailer Parking** | 2% | Optional | Trailer storage availability |
| **Rail Access** | 2% | Optional | Deal-breaker for bulk commodities |
| **Crane** | 2% | Optional | Heavy manufacturing essential |
| **Occupancy Status** | 0% | Optional | Vacant = immediate occupancy (low priority) |
| **Grade Level Doors** | 2% | Optional | Courier vans, small truck access |
| **Days on Market** | 2% | Optional | Landlord motivation indicator |
| **Zoning** | 2% | Optional | Permitted use restrictions |
| **Secure Shipping** | 0% | Optional | Secure loading areas (rarely available) |
| **Excess Land** | 0% | Optional | Expansion/outdoor storage (rarely available) |

**Note**: When optional variables are unavailable, the system automatically adjusts weights. For example, if only the 9 core variables are present, they receive proportionally higher weights that still sum to 100%.

### Competitive Tiers

| Rank | Status | Win Probability | Action Required |
|------|--------|----------------|-----------------|
| **#1-3** | ✅ Highly Competitive | 70-90% | Maintain position |
| **#4-10** | ⚠️ Moderately Competitive | 50-70% | Consider adjustments |
| **#11+** | ❌ Not Competitive | <50% | **Urgent** price reduction needed |

**The "Top 3 Rule"**: You must be Rank #1, #2, or #3 to win deals consistently.

If you're outside the Top 3:
1. Tenants will prioritize competitors offering better value
2. Your property becomes "backup option" not primary choice
3. Longer vacancy periods and weaker negotiating position
4. May need to offer additional concessions beyond price

### Ranking Rules

**Ascending Rank (Lower Value = Rank 1):**
- Net Asking Rent - Lower rent wins
- TMI - Lower operating costs wins
- Distance - Closer to subject wins
- Class - 1 (A) beats 2 (B) beats 3 (C)
- Area Difference - Smaller mismatch wins

**Descending Rank (Higher Value = Rank 1):**
- Clear Height - Higher ceilings win
- Parking Ratio - More parking wins
- Year Built - Newer buildings win
- % Office Space - More office usually wins

### Tie Handling

Use **average rank method**:
- If 3 properties tie for ranks 5, 6, 7
- Assign all three rank = (5 + 6 + 7) / 3 = 6.0

## Sensitivity Analysis

### Pricing Adjustments to Achieve Rank #3

Calculate how much rent and/or TMI must be reduced:

**Three Scenarios:**
1. **Rent Reduction Only** - Lower net asking rent, TMI unchanged
2. **TMI Reduction Only** - Lower operating costs, rent unchanged
3. **Combined Reduction** - Adjust both rent and TMI

**Formula:**
```
Points to improve = Subject Score - Rank #3 Score
Points from rent reduction = (Rank improvement × 0.16)
Points from TMI reduction = (Rank improvement × 0.14)
```

### Example Sensitivity Analysis

**Current Position:**
- Subject Rank: #7, Score: 45.2
- Rank #3 Score: 38.5
- Gap: 6.7 points

**Scenario 1: Rent Reduction**
- Reduce rent from $9.50 to $8.75 (-$0.75)
- Improves rent rank from 8 to 3
- Gain: 5 ranks × 0.16 = 0.80 points
- New score: 44.4 (still rank #6)
- **Not sufficient** - need more aggressive reduction

**Scenario 2: Combined Approach**
- Reduce rent from $9.50 to $8.50 (-$1.00)
- Reduce TMI from $5.50 to $4.75 (-$0.75)
- Combined gain: 2.1 points
- New score: 43.1 (achieves rank #3)
- **Recommended**

## Strategic Recommendations by Rank Tier

### Rank #1-3: Maintain Competitive Position

**Strategy:** Defend market position
- Monitor competitors closely for price changes
- Highlight value proposition in marketing
- Can afford to hold firm on pricing
- Focus on service quality and tenant experience

**Tactics:**
- Weekly comp monitoring
- Emphasize unique advantages (e.g., best parking ratio)
- Leverage "Top 3" status in negotiations
- Consider selective rent increases if demand strong

### Rank #4-10: Improve to Top 3

**Strategy:** Tactical adjustments to reach competitive threshold
- Calculate exact pricing needed for Rank #3
- Evaluate non-price improvements (e.g., TI allowance, free rent)
- Reassess if market position sustainable

**Tactics:**
- Run sensitivity analysis for multiple scenarios
- Consider 1-2 rank improvement vs. aggressive move to Top 3
- Package price adjustment with lease term extension
- Target improvement in highest-weighted variables (rent, parking, TMI)

### Rank #11+: Urgent Repositioning Required

**Strategy:** Aggressive intervention needed
- Property fundamentally overpriced for market
- High risk of extended vacancy
- Need immediate price correction or major incentives

**Tactics:**
- **Immediate** rent reduction to achieve Top 10
- Consider substantial TI allowance or free rent periods
- May need to accept below-market deal to secure tenant
- Reassess property positioning - wrong market segment?

## Non-Price Levers

### When Price Reduction Not Feasible

If you cannot lower rent/TMI, improve competitive position through:

1. **Tenant Improvements (TI)**
   - Increase TI allowance by $10-20/SF
   - Reduces effective rent without changing face rate
   - Calculated: TI ÷ Lease Term = Effective rent reduction

2. **Free Rent**
   - Offer 3-6 months free rent
   - Reduces effective rent while maintaining face rate
   - Better for landlord accounting vs. lower base rent

3. **Operating Cost Caps**
   - Cap TMI escalations at 2-3% annually
   - Reduces tenant's long-term occupancy cost risk
   - Improves TMI ranking indirectly

4. **Lease Flexibility**
   - Early termination options
   - Expansion/contraction rights
   - Renewal options with fixed rates
   - Adds value without changing base economics

5. **Service Enhancements**
   - Improved property management
   - Enhanced common areas
   - Better security/parking lot maintenance
   - Builds goodwill but doesn't change rankings

## Limitations and Cautions

### When Relative Valuation Doesn't Apply

**Not suitable for:**
- Unique properties with no true comparables
- Specialized industrial (e.g., cold storage, food processing)
- Build-to-suit requirements
- Properties with significant qualitative advantages (e.g., Fortune 500 landlord)

### Methodology Assumptions

1. **Linear Preferences** - Variables ranked independently (no interaction effects)
2. **Fixed Weights** - Standard weights may not match specific tenant persona
3. **No Qualitative Factors** - Doesn't account for:
   - Building condition beyond age
   - Landlord reputation
   - Property management quality
   - Intangible tenant preferences

### Data Quality Requirements

**Garbage in, garbage out:**
- Comparables must be **truly comparable** (same submarket, property type, size range)
- Data must be **current** (30-90 days old maximum)
- Ensure **apples-to-apples** comparison (net vs gross rent, same measurement standards)

## Tenant Persona Weight Profiles

The calculator includes built-in weight profiles optimized for different tenant types. Use the `--persona` CLI parameter or specify persona in analysis request.

### Available Personas:

#### 1. **Default (Balanced)**
- Standard weights suitable for mixed-use or when tenant type unknown
- Balanced emphasis across all variables

#### 2. **3PL/Distribution** (`--persona 3pl`)
- **Emphasizes**: Bay depth (7%), clear height (10%), shipping doors TL (6%), trailer parking (4%)
- **De-emphasizes**: Office space (2%), class (2%), HVAC (1%)
- **Rationale**: Distribution users prioritize operational efficiency and logistics infrastructure

#### 3. **Manufacturing** (`--persona manufacturing`)
- **Emphasizes**: Clear height (10%), power (6%), crane (5%), bay depth (7%), rail access (4%)
- **De-emphasizes**: Office space (3%), class (3%), distance (4%)
- **Rationale**: Manufacturing users need power, lifting capability, and less concern for office amenities or commute distance

#### 4. **Office** (`--persona office`)
- **Emphasizes**: Office space (12%), parking (12%), rent (13%), HVAC (6%), class (8%), distance (10%)
- **De-emphasizes**: Clear height (2%), bay depth (0%), shipping doors (1% each), crane (0%), rail (0%), trailer parking (0%)
- **Rationale**: Office tenants prioritize professional image, employee amenities, commute convenience

### Usage Example:
```bash
python relative_valuation_calculator.py --input data.json --output report.md --persona 3pl
```

## Must-Have Filters

Filter out properties that don't meet minimum requirements **before** ranking. This ensures the analysis only considers viable options.

### Filter Types:

1. **Minimum Value Filters** (suffix: `_min`)
   - Example: `"clear_height_ft_min": 32` - Excludes properties with <32 ft clear height
   - Example: `"bay_depth_ft_min": 54` - Requires 54'+ bays for 53' trailers

2. **Maximum Value Filters** (suffix: `_max`)
   - Example: `"days_on_market_max": 180` - Excludes stale listings >180 days

3. **Boolean Filters**
   - Example: `"rail_access": true` - Only includes properties with rail sidings
   - Example: `"crane": true` - Requires overhead crane

4. **Exact Match Filters** (strings)
   - Example: `"zoning": "M1"` - Only M1 zoned properties

5. **Ordinal Filters** (integers)
   - Example: `"sprinkler_type": 1` - Only ESFR sprinklers (1=ESFR, 2=Standard, 3=None)
   - Example: `"hvac_coverage": 1` - Full HVAC only (1=Y, 2=Part, 3=N)

### JSON Schema:
```json
{
  "filters": {
    "rail_access": true,
    "clear_height_ft_min": 36,
    "sprinkler_type": 1,
    "zoning": "M2",
    "days_on_market_max": 90
  }
}
```

### Example Output:
```
Applying must-have filters...
3 properties excluded by filters
   - 520 Abilene Dr: clear_height_ft 30.0 < 36.0 (minimum)
   - 6975 Pacific Cir: rail_access is required
   - 2550 Stanfield Rd: zoning 'M1' != 'M2'
```

**When to Use Filters:**
- **Rail users**: Filter `"rail_access": true` (eliminates 98% of market)
- **High-piled storage**: Filter `"sprinkler_type": 1` (ESFR only)
- **Heavy manufacturing**: Filter `"crane": true`, `"power_amps_min": 1000`
- **53' trailer operations**: Filter `"bay_depth_ft_min": 54`

## Key Communication Language

### When Communicating Results to Landlord

**If Rank #1-3:**
> "Your property is **highly competitive** at current pricing. You're well-positioned to win deals at 70-90% probability. Maintain your pricing strategy and focus on execution."

**If Rank #4-10:**
> "Your property is **moderately competitive** but outside the critical Top 3. Consider tactical adjustments—a $0.50/SF rent reduction could move you from Rank #7 to Rank #3 and improve deal-winning probability from 50% to 85%."

**If Rank #11+:**
> "Your property is **not competitive** at current pricing. You're asking $1.50/SF above market-leading options. Tenants will default to competitors offering better value. Immediate price correction is required to avoid extended vacancy."

### When Communicating Results to Tenant Representative

**If Subject (Client's Target) Ranks #1-3:**
> "This property offers **excellent value** relative to market. It ranks in the Top 3 out of X comparables. You're getting competitive pricing—I recommend moving forward with lease negotiations."

**If Subject Ranks #4-10:**
> "This property is **decent but not optimal**. Several options offer better value at current pricing. Use this analysis to negotiate a rent reduction. That would move it into the competitive Top 3."

**If Subject Ranks #11+:**
> "This property is **overpriced** for the market. Landlord is asking significantly above competitive alternatives. I recommend pursuing Top 3 properties OR negotiating aggressively for substantial rent reduction."

## Red Flags and Common Mistakes

### Don't Make These Errors

1. **Ignoring the Top 3 Rule**
   - "We're Rank #5, close enough" → No, you're losing deals to Rank #1-3
   - Must take action to reach Top 3, not settle for "close"

2. **Focusing Only on Rent**
   - Rent is 16% weight, TMI is 14% → Combined 30%
   - Parking (15%) nearly as important as rent
   - Consider multi-variable improvements

3. **Using Stale Data**
   - Market changes rapidly
   - Comps from 6 months ago may not reflect current conditions
   - Re-run analysis monthly during active leasing

4. **Ignoring Ties**
   - If Rank #1 and #2 have same weighted score → Dead heat
   - Winning will come down to non-quantitative factors
   - Prepare to compete on service, reputation, deal structure

5. **Over-Relying on Model**
   - RV is a tool, not a crystal ball
   - Qualitative factors matter: landlord reputation, building condition, location prestige
   - Use RV to inform strategy, not replace judgment

## Workflow Steps

### Step 1: Extract Data from PDF Documents

The user will provide one or more PDF documents containing:
- Subject property details
- Comparable property data (CoStar reports, broker packages, market surveys)

**Your tasks:**
1. Extract all properties with the following **core attributes** (always required):
   - **Address & Unit** - ⚠️ **CRITICAL**: Extract COMPLETE addresses for distance API compatibility:
     - **Required Format**: `"Street Address, City, Province PostalCode, Country"`
     - **Example**: `"2550 Stanfield Rd, Mississauga, ON L4Y 1S2, Canada"`
     - **Components**:
       - Street address (e.g., "2550 Stanfield Rd")
       - City (e.g., "Mississauga")
       - Province as **two-letter code** (e.g., "ON" not "Ontario")
       - Postal code with space (e.g., "L4Y 1S2" not "L4Y1S2")
       - Country ("Canada")
     - **Separators**: Use commas between components
     - **Unit**: Store separately in "unit" field, NOT appended to address
     - **Why**: Distance calculation API requires complete geocodable addresses
   - **Year Built**
   - **Clear Height** (ft)
   - **% Office Space** - ⚠️ **CRITICAL**: PDF shows "% Warehouse Space" - you MUST convert:
     - Formula: `% Office = (100 - % Warehouse) / 100`
     - Example: 89% warehouse → (100-89)/100 = **0.11** (store as decimal)
     - Never store as whole number (11.0 is WRONG, 0.11 is correct)
   - **Parking Ratio** (spaces per 1,000 SF)
   - **Available SF**
   - **Distance from Subject** (km) - Calculate automatically using distance API (Step 3)
   - **Net Asking Rent** ($/SF/year)
   - **TMI** ($/SF/year)
   - **Class** (A/B/C) - Map to integers: A=1, B=2, C=3

2. Extract **optional attributes** if available (used in ranking if ≥50% of properties have data):
   - **Shipping Doors** - Format "X TL Y DI" in PDF:
     - Extract X as `shipping_doors_tl` (truck-level doors)
     - Extract Y as `shipping_doors_di` (drive-in doors)
   - **Power** (amps) - Extract number as `power_amps`
   - **Availability Date** - Extract as string: "Immediate", "Jan-26", "Q4 2025", etc.
   - **Trailer Parking** - "Yes" or blank → boolean (true if "Yes", false otherwise)
   - **Secure Shipping** - "Yes" or "Y" or blank → boolean (true if present, false otherwise)
   - **Excess Land** - "Yes" or blank → boolean (true if "Yes", false otherwise)
   - **Bay Depth** - Parse from "Bay Size" field (e.g., "55 x 52" → 55.0) as `bay_depth_ft`
   - **Lot Size** - Extract from "Lot Irreg" or "Lot Size Area", convert to acres as `lot_size_acres`
   - **HVAC Coverage** - Extract from "A/C" field: Y=1, Part=2, N=3 (ordinal) as `hvac_coverage`
   - **Sprinkler Type** - Check "Sprinklers" + "Client Remks" for ESFR: ESFR=1, Standard=2, None=3 (ordinal) as `sprinkler_type`
   - **Year Built** - Extract year as integer as `year_built` (building age calculated automatically)
   - **Rail Access** - Extract from "Rail" field: Y/N → boolean as `rail_access`
   - **Crane** - Extract from "Crane" field: Y/N → boolean as `crane`
   - **Occupancy Status** - Extract from "Occup" field: Vacant=1, Tenant=2 (ordinal) as `occupancy_status`
   - **Grade Level Doors** - Extract from "Grade Level" field as integer as `grade_level_doors`
   - **Days on Market** - Extract from "DOM" field as integer as `days_on_market`
   - **Zoning** - Extract from "Zoning" field as string as `zoning`

3. Identify which property is the subject property (distance = 0)

4. If distance data is missing:
   - Note: "Distance calculations deferred - using estimated values"
   - Use approximate distances based on address locations
   - Flag for manual review

### Step 2: Create Input JSON File

Build a properly formatted JSON file following this schema:

```json
{
  "analysis_date": "YYYY-MM-DD",
  "market": "Market Name - Property Type",
  "subject_property": {
    "address": "2550 Stanfield Rd, Mississauga, ON L4Y 1S2, Canada",
    "unit": "Opt 2",
    "year_built": 0,
    "clear_height_ft": 0.0,
    "pct_office_space": 0.11,  // ⚠️ DECIMAL: 11% = 0.11, NOT 11.0
    "parking_ratio": 0.0,
    "available_sf": 0,
    "distance_km": 0.0,
    "net_asking_rent": 0.0,
    "tmi": 0.0,
    "class": 2,
    "is_subject": true,
    "landlord": "...",
    "shipping_doors_tl": 0,      // Optional: truck-level doors
    "shipping_doors_di": 0,      // Optional: drive-in doors
    "availability_date": "",     // Optional: "Immediate", "Jan-26", etc.
    "power_amps": 0,             // Optional: electrical capacity
    "trailer_parking": false,    // Optional: boolean
    "secure_shipping": false,    // Optional: boolean
    "excess_land": false,        // Optional: boolean
    "bay_depth_ft": 0.0,         // Optional: bay depth in feet
    "lot_size_acres": 0.0,       // Optional: lot size in acres
    "hvac_coverage": 3,          // Optional: Y=1, Part=2, N=3 (ordinal)
    "sprinkler_type": 3,         // Optional: ESFR=1, Standard=2, None=3 (ordinal)
    "rail_access": false,        // Optional: boolean
    "crane": false,              // Optional: boolean
    "occupancy_status": 2,       // Optional: Vacant=1, Tenant=2 (ordinal)
    "grade_level_doors": 0,      // Optional: grade-level doors count
    "days_on_market": 0,         // Optional: days on market
    "zoning": ""                 // Optional: zoning classification (e.g., "M1", "M2")
  },
  "comparables": [
    {
      "address": "795 Hazelhurst Rd, Mississauga, ON L5J 2Z6, Canada",
      "unit": "",
      "year_built": 0,
      "clear_height_ft": 0.0,
      "pct_office_space": 0.09,  // ⚠️ DECIMAL: 9% = 0.09, NOT 9.0
      "parking_ratio": 0.0,
      "available_sf": 0,
      "distance_km": 0.0,
      "net_asking_rent": 0.0,
      "tmi": 0.0,
      "class": 2,
      "is_subject": false,
      "landlord": "...",
      "shipping_doors_tl": 0,
      "shipping_doors_di": 0,
      "availability_date": "",
      "power_amps": 0,
      "trailer_parking": false,
      "secure_shipping": false,
      "excess_land": false,
      "bay_depth_ft": 0.0,
      "lot_size_acres": 0.0,
      "hvac_coverage": 3,
      "sprinkler_type": 3,
      "rail_access": false,
      "crane": false,
      "occupancy_status": 2,
      "grade_level_doors": 0,
      "days_on_market": 0,
      "zoning": ""
    }
  ],
  "filters": {
    // Optional: Must-have requirements (Phase 2)
    // Example filters (remove or adjust as needed):
    // "rail_access": true,             // Only properties with rail access
    // "clear_height_ft_min": 36,       // Minimum 36 ft clear height
    // "sprinkler_type": 1,             // Only ESFR sprinklers
    // "days_on_market_max": 180,       // Exclude stale listings
    // "zoning": "M2"                   // Only M2 zoning
  },
  "weights": {
    "building_age_years": 0.04,
    "clear_height_ft": 0.07,
    "pct_office_space": 0.06,
    "parking_ratio": 0.09,
    "distance_km": 0.07,
    "net_asking_rent": 0.11,
    "tmi": 0.09,
    "class": 0.05,
    "area_difference": 0.07,
    "shipping_doors_tl": 0.04,
    "shipping_doors_di": 0.03,
    "power_amps": 0.03,
    "trailer_parking": 0.02,
    "bay_depth_ft": 0.04,
    "lot_size_acres": 0.03,
    "hvac_coverage": 0.03,
    "sprinkler_type": 0.03,
    "rail_access": 0.02,
    "crane": 0.02,
    "occupancy_status": 0.00,
    "grade_level_doors": 0.02,
    "days_on_market": 0.02,
    "zoning": 0.02
  }
}
```

**Critical Requirements:**
- **Address MUST be complete and geocodable**: Format: `"Street, City, Province PostalCode, Country"`
  - Example: `"2550 Stanfield Rd, Mississauga, ON L4Y 1S2, Canada"`
  - Province as two-letter code (ON not Ontario)
  - Postal code with space (L4Y 1S2 not L4Y1S2)
  - Unit stored separately, NOT appended to address
- Subject property MUST have `distance_km: 0.0` and `is_subject: true`
- All comparables MUST have `is_subject: false`
- **pct_office_space MUST be decimal**: 11% = 0.11, NOT 11.0 (PDF shows warehouse %, convert first!)
- Class values: 1 (A), 2 (B), 3 (C)
- Weights MUST sum to 1.0
- All rent/TMI values in $/SF/year (convert monthly to annual if needed)
- Optional fields can be omitted or set to defaults: 0 for numbers, false for booleans, empty string for dates
- Parking ratio in spaces per 1,000 SF (convert if needed)

**Save to**: `Reports/YYYY-MM-DD_HHMMSS_relative_valuation_input.json`

### Step 3: Calculate Distances (If Missing)

If the PDF doesn't contain distance data, automatically calculate driving distances using the distance calculator:

```bash
# Check if DISTANCEMATRIX_API_KEY is set
if [ -z "$DISTANCEMATRIX_API_KEY" ]; then
  echo "WARNING: DISTANCEMATRIX_API_KEY not set. Skipping distance calculations."
  echo "Set API key: export DISTANCEMATRIX_API_KEY=your_key_here"
  echo "Get free API key at https://distancematrix.ai/ (1,000 elements/month free)"
else
  # Calculate distances and update JSON in place
  python3 Relative_Valuation/calculate_distances.py \
    --input Reports/YYYY-MM-DD_HHMMSS_relative_valuation_input.json \
    --output Reports/YYYY-MM-DD_HHMMSS_relative_valuation_input.json \
    --verbose
fi
```

**What this does:**
- Identifies the subject property (distance_km = 0.0)
- Calls Distancematrix.ai API to calculate driving distances for all comparables
- Updates the JSON file in place with accurate distance_km values
- Shows progress for each property

**API Key Setup:**
```bash
# Get free API key at https://distancematrix.ai/
export DISTANCEMATRIX_API_KEY=your_key_here
```

**If API key not available:**
- Script will skip distance calculations
- Properties will keep initial distance_km values (set to 0.0)
- Analysis will proceed but distance ranking may be inaccurate
- **Recommended:** Manually estimate distances or note limitation in report

### Step 4: Run Python Calculator

Execute the relative valuation calculator:

```bash
# Standard report (top 10 competitors)
python3 Relative_Valuation/relative_valuation_calculator.py \
  --input Reports/YYYY-MM-DD_HHMMSS_relative_valuation_input.json \
  --output Reports/YYYY-MM-DD_HHMMSS_relative_valuation_report.md \
  --output-json Reports/YYYY-MM-DD_HHMMSS_relative_valuation_output.json

# Full report (all competitors) - use for large datasets (50+ properties)
python3 Relative_Valuation/relative_valuation_calculator.py \
  --input Reports/YYYY-MM-DD_HHMMSS_relative_valuation_input.json \
  --output Reports/YYYY-MM-DD_HHMMSS_relative_valuation_report.md \
  --output-json Reports/YYYY-MM-DD_HHMMSS_relative_valuation_output.json \
  --full
```

This generates:
- **Markdown Report**: Complete analysis with recommendations
  - By default: Shows top 10 competitors
  - With `--full`: Shows all competitors (useful for large datasets like 123 properties)
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

All files must use timestamp prefix `YYYY-MM-DD_HHMMSS` in **Eastern Time (ET)**:

**Format**: `YYYY-MM-DD_HHMMSS` where timestamp is in Eastern Time (America/New_York)
**Example**: `2025-11-05_225428` (November 5, 2025 at 10:54:28 PM ET)

1. **Input JSON**: `Reports/YYYY-MM-DD_HHMMSS_relative_valuation_input.json`
2. **Output JSON**: `Reports/YYYY-MM-DD_HHMMSS_relative_valuation_output.json`
3. **Markdown Report**: `Reports/YYYY-MM-DD_HHMMSS_relative_valuation_report.md`
4. **PDF Report (Landscape)**: `Reports/YYYY-MM-DD_HHMMSS_relative_valuation_report.pdf`

### PDF Generation (Landscape Format)

After generating the markdown report, convert to PDF in **landscape** orientation with professional styling to accommodate the expanded competitor table with all columns:

```bash
pandoc Reports/YYYY-MM-DD_HHMMSS_relative_valuation_report.md \
  -o Reports/YYYY-MM-DD_HHMMSS_relative_valuation_report.pdf \
  --css Relative_Valuation/pdf_style.css \
  --pdf-engine=wkhtmltopdf \
  --pdf-engine-opt=--orientation --pdf-engine-opt=Landscape \
  --pdf-engine-opt=--margin-top --pdf-engine-opt=5mm \
  --pdf-engine-opt=--margin-bottom --pdf-engine-opt=5mm \
  --pdf-engine-opt=--margin-left --pdf-engine-opt=8mm \
  --pdf-engine-opt=--margin-right --pdf-engine-opt=8mm
```

**Styling Features**:
- **Landscape orientation**: 11" × 8.5" (US Letter landscape)
- **Tight margins**: 5mm top/bottom, 8mm left/right (maximizes table width)
- **Modern sans-serif font**: Segoe UI / Arial (clean, readable)
- **Compact tables**: 8pt font for table data, zebra striping for readability
- **Professional headings**: Bold, hierarchical sizing

**Note**: Landscape orientation with tight margins is essential because the competitor table includes 13 columns (Rank, Property, Area (SF), Net Rent, TMI, Gross Rent, Clear Ht, Ship TL, Ship DI, Power, Trailer, Avail Date, Score).

**For wider paper**: If table still doesn't fit, use legal size (8.5" × 14"):
```bash
--pdf-engine-opt=--page-size --pdf-engine-opt=Legal
```

## Example Usage

```
User: "Analyze competitive positioning for 7381 Pacific Circ using this CoStar report"
[Attaches PDF]

ARGUMENTS: --full 7381 Pacific Circ Mississauga is subject property /workspaces/lease-abstract/skillsdevdocs/availabilities.pdf

Assistant:
1. Extracts 70 properties from PDF
2. Creates relative_valuation_input.json
3. Runs distance calculator to calculate distances from subject property
4. Runs Python calculator with --full flag (dataset has 70 comparables)
5. Interprets results: Subject ranks based on analysis
6. Provides executive summary with actionable recommendations
```

---

**You are now executing this slash command. Begin with Step 1 (extract data from PDF).**
