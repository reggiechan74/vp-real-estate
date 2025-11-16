---
description: Calculate ROW area, encumbrance impact, and easement compensation for transmission line, pipeline, and transit corridors
argument-hint: <corridor-specs> [property-data]
allowed-tools: Read, Write, Bash
---

You are a right-of-way valuation specialist for infrastructure projects. Your task is to calculate ROW area from corridor specifications, assess property encumbrance impacts, and determine fair easement compensation using multiple valuation methods.

## Input

The user will provide:
1. **Corridor specifications** (REQUIRED) - Corridor type, width, length, voltage/capacity, restrictions
2. **Property data** (REQUIRED) - Property details, ownership, current use, market value
3. **Comparable sales (optional)** - Sales of properties with similar easements

**Arguments**: {{args}}

**Example:**
```
/right-of-way-analysis "115kV transmission, 40m width, 2.5km length" "/path/to/property_data.pdf"
/right-of-way-analysis "/path/to/corridor_specs.json" "/path/to/property_appraisal.pdf"
/right-of-way-analysis "36-inch gas pipeline, 25m width, 1.8km" "50 acre farm, $10,000/acre, Class 1 soil"
```

## Corridor Type Classification

### Utility Transmission Lines

**Voltage-Specific Widths:**
- **69kV**: 20-30m width (distribution voltage)
- **115kV**: 30-40m width (sub-transmission)
- **230kV**: 45-60m width (transmission)
- **500kV**: 80-100m width (high voltage transmission)

**Typical Restrictions:**
- Tower footprints: no buildings, permanent structures
- Safety clearance zones: no tall vegetation, equipment height limits
- Access strips: periodic maintenance vehicle access
- Agricultural impacts: restricted irrigation equipment, field division

**Percentage of Fee Range:** 10-25% (voltage-dependent)

### Pipeline Corridors

**Product-Specific Widths:**
- **Water/Sewer**: 10-15m width (low pressure, minimal risk)
- **Natural Gas (low pressure)**: 15-20m width (<1,000 kPa)
- **Natural Gas (high pressure)**: 20-30m width (>1,000 kPa)
- **Crude Oil/Petroleum**: 30-40m width (safety setbacks, spill risk)

**Typical Restrictions:**
- Pipeline corridor: no buildings, no deep excavation, no permanent structures
- Safety buffer zones: restricted construction, foundation limitations
- Access requirements: maintenance vehicle access, emergency access
- Agricultural impacts: depth restrictions for deep tillage, irrigation limitations

**Percentage of Fee Range:** 15-30% (product risk-dependent)

### Transit Corridors

**Mode-Specific Widths:**
- **Light Rail (LRT)**: 20-30m width (surface or elevated)
- **Subway (underground)**: 15-25m width (subsurface easement + access)
- **Commuter Rail**: 30-50m width (including safety setbacks)
- **Bus Rapid Transit (BRT)**: 15-20m width (dedicated lanes)

**Typical Restrictions:**
- Track corridor: exclusive use, no encroachments
- Safety setbacks: fencing requirements, access restrictions
- Noise/vibration buffers: building setbacks, foundation requirements
- Access limitations: grade separations, crossing restrictions

**Percentage of Fee Range:** 20-35% (depends on surface vs. subsurface, noise/vibration impacts)

## Process

### Step 1: Parse Input Arguments

Extract corridor and property information from arguments:

**From Corridor Specs (Argument 1):**
- Corridor type: transmission / pipeline / transit / access
- Width (meters)
- Length (meters or kilometers)
- Voltage (kV) or capacity specification
- Product type (for pipelines: gas/oil/water)
- Transit mode (for transit: LRT/subway/commuter rail)

**From Property Data (Argument 2):**
- Property address
- Total property size (acres or hectares)
- Fee simple market value ($/acre or total)
- Current use (agricultural, residential, industrial)
- Soil classification (if agricultural)
- Highest and best use
- Zoning

**Validation:**
- If fewer than 2 arguments provided, ERROR and request both corridor specs and property data
- If corridor width/length missing, prompt for required dimensions

### Step 2: Calculate ROW Area

**ROW Area Calculation:**

```
ROW Area (hectares) = Width (meters) × Length (meters) ÷ 10,000
ROW Area (acres) = ROW Area (hectares) × 2.471
```

**Example:**
- Width: 40 meters
- Length: 2,500 meters (2.5 km)
- ROW Area = 40m × 2,500m ÷ 10,000 = 10 hectares = 24.71 acres

**Encumbrance Percentage:**
```
Encumbrance % = (ROW Area ÷ Total Property Area) × 100%
```

**Example:**
- ROW Area: 24.71 acres
- Property Size: 100 acres
- Encumbrance: 24.71 ÷ 100 = 24.71% of property

### Step 3: Load Property and Market Data

**Read property documents:**
1. If PDF/DOCX provided, use Read tool to extract:
   - Legal description and address
   - Property size and boundaries
   - Current use and improvements
   - Market value or recent appraisal
   - Annual income (if income-producing)
   - Soil classification (if agricultural)
   - Zoning and development potential

2. If manual input provided, parse text for same information

**Market Parameters:**
- Identify comparable sales with similar easements (if available)
- Extract annual land rent per acre (if agricultural or income-producing)
- Determine appropriate capitalization rate:
  - Perpetual easements: 4-6%
  - Long-term easements (50+ years): 5-7%
  - Medium-term easements (20-49 years): 6-8%

### Step 4: Determine Valuation Method and Parameters

**Select Percentage of Fee:**

Based on corridor type and characteristics:

**Utility Transmission:**
- 69kV: 10-15%
- 115kV: 12-18%
- 230kV: 15-20%
- 500kV: 20-25%

**Adjustments:**
- +2-5% if multiple towers per acre
- +2-5% if agricultural impacts severe (irrigation, field division)
- +1-3% if regular maintenance access required
- -2-5% if minimal restrictions, infrequent access

**Pipeline:**
- Water/sewer: 15-20%
- Natural gas (low pressure): 15-20%
- Natural gas (high pressure): 20-25%
- Petroleum products: 25-30%

**Adjustments:**
- +3-5% if shallow depth (more restrictive)
- +5-10% if building prohibitions extend beyond corridor
- +2-5% if cathodic protection equipment sites
- -2-5% if deep burial, minimal surface impact

**Transit:**
- LRT (surface): 25-30%
- Subway (subsurface): 20-25%
- Commuter rail: 30-35%
- BRT: 20-25%

**Adjustments:**
- +5-10% if noise/vibration impacts severe
- +5-10% if access severely restricted (land-locking)
- +3-5% if visual/aesthetic impact significant
- -5-10% if subsurface only with surface rights retained

**Income Capitalization Method:**

If property is income-producing (agricultural, commercial):

1. **Calculate annual income loss:**
   - Determine annual rent per acre without easement
   - Calculate percentage productivity loss from easement
   - Annual income loss = Annual rent × Productivity loss % × ROW acres

2. **Capitalize to present value:**
   - Select capitalization rate (4-8% based on easement term and risk)
   - Easement value = Annual income loss ÷ Cap rate

**Before/After Method:**

If recent appraisal or comparable sales available:

1. **Fee simple value before easement:** Total property value
2. **Fee simple value after easement:** Appraised value with easement encumbrance
3. **Easement value = Before value - After value**

### Step 5: Generate JSON Input File

Create a JSON file following the easement valuation calculator schema:

```json
{
  "corridor_specifications": {
    "corridor_type": "utility_transmission | pipeline | transit | access",
    "voltage_kv": 115.0,
    "pipeline_type": "natural_gas | crude_oil | water | sewer",
    "transit_type": "light_rail | heavy_rail | bus_rapid_transit",
    "width_meters": 40.0,
    "length_meters": 2500.0,
    "row_area_hectares": 10.0,
    "row_area_acres": 24.71,
    "term": "perpetual | temporary",
    "term_years": null,
    "restrictions": [
      "no_buildings",
      "no_trees",
      "height_restrictions",
      "access_limitations",
      "excavation_prohibited"
    ],
    "notes": "Corridor description and special characteristics"
  },
  "property": {
    "address": "Property address",
    "total_acres": 100.0,
    "fee_simple_value": 1000000.0,
    "fee_simple_value_per_acre": 10000.0,
    "zoning": "Agricultural",
    "highest_and_best_use": "Row crop agriculture",
    "current_use": "Corn and soybean rotation",
    "soil_class": "Class 1",
    "value_after_easement": 950000.0,
    "encumbrance_percentage": 24.71,
    "notes": "Property description and characteristics"
  },
  "easement": {
    "type": "utility_transmission",
    "voltage_kv": 115.0,
    "area_acres": 24.71,
    "width_meters": 40.0,
    "term": "perpetual",
    "restrictions": [
      "no_buildings",
      "no_trees",
      "height_restrictions",
      "access_limitations"
    ],
    "hbu_impact": "minor | moderate | major | precludes_development",
    "easement_rent_factor": 0.20,
    "notes": "20% productivity loss estimated from tower footprints and restricted planting zones"
  },
  "market_parameters": {
    "cap_rate": 0.045,
    "annual_rent_per_acre": 300.0,
    "comparable_sales": [
      {
        "address": "Comparable property 1",
        "total_acres": 95.0,
        "sale_price": 950000.0,
        "sale_date": "2024-06-15",
        "easement_present": true,
        "easement_type": "utility_transmission",
        "easement_voltage_kv": 115.0,
        "easement_acres": 20.0,
        "notes": "Similar transmission easement, Class 1 soil"
      }
    ],
    "notes": "Market data sources and assumptions"
  },
  "valuation_methods": {
    "percentage_of_fee": {
      "base_percentage": 0.15,
      "adjustments": [
        {"factor": "tower_density", "adjustment": 0.02, "reason": "3 towers on easement area"},
        {"factor": "agricultural_impact", "adjustment": 0.03, "reason": "Irrigation system relocation required"}
      ],
      "adjusted_percentage": 0.20,
      "notes": "115kV base 15%, adjusted for tower density and agricultural impacts"
    },
    "income_capitalization": {
      "annual_rent_per_acre": 300.0,
      "productivity_loss_percentage": 0.20,
      "annual_income_loss": 1482.6,
      "cap_rate": 0.045,
      "notes": "Perpetual easement, low risk utility operator"
    },
    "before_after": {
      "value_before": 1000000.0,
      "value_after": 950000.0,
      "notes": "Before/after values from appraisal or market extraction"
    }
  },
  "analysis_metadata": {
    "analysis_date": "2025-11-15",
    "analyst": "Claude Code - ROW Analysis",
    "valuation_date": "2025-11-15",
    "property_inspection_date": null,
    "sources": [
      "Property appraisal by [Appraiser Name], [Date]",
      "Corridor specifications from [Utility/Agency Name]",
      "Agricultural rent data from [Source]"
    ],
    "notes": "Analysis conducted for [Purpose] - negotiation / expropriation / acquisition"
  }
}
```

**Save the JSON file as:**
`/workspaces/lease-abstract/.claude/skills/easement-valuation-methods/row_inputs/[property_name]_[corridor_type]_input.json`

Create the directory if it doesn't exist.

### Step 6: Run the Easement Valuation Calculator

Execute the calculator using Bash tool:

```bash
cd /workspaces/lease-abstract/.claude/skills/easement-valuation-methods
python3 easement_valuation_calculator.py row_inputs/[filename]_input.json -o row_outputs/[filename]_results.json --verbose
```

**Note:** If `easement_valuation_calculator.py` does not exist yet, this command will document the expected workflow. The calculator should be created as part of the easement-valuation-methods skill implementation.

Capture the console output for the markdown report.

### Step 7: Generate Markdown Report

Create a comprehensive markdown report in `/workspaces/lease-abstract/Reports/` with filename:
`YYYY-MM-DD_HHMMSS_row_analysis_[property_name]_[corridor_type].md` (timestamp in Eastern Time)

**Report Structure:**

```markdown
# Right-of-Way Easement Analysis Report

**Property:** [Property Address]
**Corridor Type:** [Type] - [Voltage/Product/Mode]
**Analysis Date:** [Current Date]
**Valuation Date:** [Valuation Date]
**Purpose:** [Negotiation / Expropriation / Acquisition]

---

## Executive Summary

**Corridor Specifications:**
- Type: [Transmission Line / Pipeline / Transit]
- Specifications: [115kV / 36" Gas / LRT]
- Width: [X] meters
- Length: [X] meters / km
- ROW Area: **[X.XX] hectares ([X.XX] acres)**

**Property Impact:**
- Total Property: [XXX] acres
- ROW Encumbrance: [XX.X%] of property
- Current Use: [Agricultural / Residential / Industrial]

**Easement Value Range:**

| Valuation Method | Value Estimate | $/Acre (ROW) | % of Fee |
|------------------|----------------|--------------|----------|
| Percentage of Fee | $XXX,XXX | $X,XXX | XX% |
| Income Capitalization | $XXX,XXX | $X,XXX | XX% |
| Before/After | $XXX,XXX | $X,XXX | XX% |
| **Reconciled Value** | **$XXX,XXX** | **$X,XXX** | **XX%** |

**Recommended Compensation:** $XXX,XXX to $XXX,XXX

---

## Corridor Analysis

### ROW Dimensions and Area Calculation

**Corridor Specifications:**
- Corridor Type: [Transmission Line / Pipeline / Transit]
- Voltage/Capacity: [115kV / 36" diameter / 2 tracks]
- Width: [40] meters ([131] feet)
- Length: [2,500] meters ([2.5] km / [1.55] miles)

**ROW Area Calculation:**
```
ROW Area = Width × Length ÷ 10,000
ROW Area = 40m × 2,500m ÷ 10,000
ROW Area = 10 hectares
ROW Area = 10 ha × 2.471 = 24.71 acres
```

**Encumbrance Percentage:**
```
Total Property: 100 acres
ROW Area: 24.71 acres
Encumbrance: 24.71 ÷ 100 = 24.71% of property
```

### Use Restrictions

**Prohibited Activities within ROW:**
- [✓] No buildings or permanent structures
- [✓] No trees or tall vegetation (height restrictions)
- [✓] No deep excavation without approval
- [✓] Height restrictions for equipment and structures
- [✓] Access limitations (locked gates, controlled entry)

**Permitted Activities within ROW:**
- [✓] Agricultural use (with restrictions)
- [✓] Grazing (subject to safety clearances)
- [✓] Surface parking or gravel areas
- [Specify other permitted uses]

**Agricultural Impact Assessment:**
- Tower/facility footprints: [X] acres (permanent loss)
- Restricted planting zones: [X] acres (partial loss)
- Field division impact: [Describe impact on equipment efficiency]
- Irrigation system impact: [Relocation required / Limited / None]
- Estimated productivity loss: [XX%]

---

## Property Characteristics

**Legal Description:**
[Full legal description from property documents]

**Property Details:**
- Address: [Full address]
- Total Area: [XXX] acres ([XX] hectares)
- Zoning: [Agricultural / Residential / Industrial]
- Current Use: [Description]
- Highest and Best Use: [Description]

**Physical Characteristics:**
- Topography: [Level / Rolling / Hilly]
- Soil Class: [Class 1 / 2 / 3] (if agricultural)
- Drainage: [Excellent / Good / Fair / Poor]
- Access: [Highway frontage / Secondary road / Private road]
- Services: [Hydro, water, sewer availability]

**Improvements:**
- Dwelling: [Yes/No - Description]
- Outbuildings: [List buildings and structures]
- Agricultural improvements: [Drainage tile, fencing, etc.]
- Other: [Any other improvements]

**Market Value:**
- Fee Simple Value: $[XXX,XXX] ($[X,XXX]/acre)
- Source: [Recent appraisal / Recent sale / Market analysis]
- Valuation Date: [Date]

**Income Analysis** (if income-producing):
- Annual Gross Income: $[XXX,XXX]
- Annual Net Income: $[XXX,XXX]
- Capitalization Rate: [X.X%]
- Indicated Value: $[XXX,XXX]

---

## Valuation Analysis

### Method 1: Percentage of Fee

**Base Percentage Selection:**

Corridor Type: [Transmission Line]
Voltage/Specification: [115kV]
Base Percentage Range: [12-18%]
Selected Base Percentage: [15%]

**Justification:**
[Explain selection within range - consider typical market percentages for this corridor type]

**Adjustment Factors:**

| Factor | Adjustment | Justification |
|--------|------------|---------------|
| Tower Density | +2.0% | 3 towers on easement area (high density) |
| Agricultural Impact | +3.0% | Irrigation system relocation required, field division |
| Access Frequency | +1.0% | Regular maintenance access 4x per year |
| Safety Buffer | +0.0% | Standard width, no excess buffer |
| **Total Adjustments** | **+6.0%** | |
| **Adjusted Percentage** | **21.0%** | Base 15% + 6% adjustments |

**Calculation:**

```
ROW Area: 24.71 acres
Fee Simple Value: $10,000/acre
Easement % of Fee: 21.0%

Method 1: Apply percentage to ROW area only
Easement Value = 24.71 acres × $10,000/acre × 21.0%
Easement Value = $51,891

Method 2: Apply percentage to total property value
Easement % of Property = 24.71% encumbrance × 21.0% of fee
Total Property Value = $1,000,000
Easement Value = $1,000,000 × 24.71% × 21.0%
Easement Value = $51,891

Both methods yield same result: $51,891
```

**Percentage of Fee Indication:** $51,891 ($2,100/ROW acre)

### Method 2: Income Capitalization

**Income Analysis:**

Property Type: [Agricultural - Row Crops]
Soil Class: [Class 1]
Annual Rent (Fee Simple): $300/acre/year

**Easement Impact on Income:**

| Income Component | Without Easement | With Easement | Loss |
|------------------|------------------|---------------|------|
| Tower footprints | $300/acre | $0/acre | 100% loss on [2] acres |
| Restricted zones | $300/acre | $240/acre | 20% loss on [10] acres |
| Remaining area | $300/acre | $270/acre | 10% loss on [12.71] acres |
| **Weighted Average** | **$300/acre** | **$240/acre** | **20% productivity loss** |

**Annual Income Loss Calculation:**

```
ROW Area: 24.71 acres
Annual Rent (without easement): $300/acre
Productivity Loss: 20%

Annual Income Loss = 24.71 acres × $300/acre × 20%
Annual Income Loss = $1,482.60/year
```

**Capitalization to Present Value:**

```
Easement Term: Perpetual
Easement Holder: [Government / Regulated Utility]
Risk Profile: Low (government/utility operator, perpetual term)
Cap Rate: 4.5%

Easement Value = Annual Income Loss ÷ Cap Rate
Easement Value = $1,482.60 ÷ 0.045
Easement Value = $32,947
```

**Cap Rate Justification:**
- Perpetual easement: -0.5% (longer term, more certainty)
- Government/regulated utility: -0.5% (low risk operator)
- Agricultural income stability: Base 5.5%
- Selected Rate: 4.5%

**Income Capitalization Indication:** $32,947 ($1,334/ROW acre)

### Method 3: Before/After Comparison

**Market Extraction from Comparable Sales:**

**Comparable Sale 1:**
- Address: [Comparable property address]
- Sale Date: [2024-06-15]
- Total Acres: 95 acres
- Sale Price: $950,000 ($10,000/acre)
- Easement: 115kV transmission, 20 acres
- Easement % of Property: 21.1%

**Adjustment Analysis:**

| Characteristic | Subject | Comparable | Adjustment |
|----------------|---------|------------|------------|
| Sale Date | Current | 3 mo ago | +2% |
| Property Size | 100 acres | 95 acres | 0% |
| Soil Class | Class 1 | Class 1 | 0% |
| Location | Highway | Highway | 0% |
| Easement | 24.71 acres | 20 acres | TBD |
| **Adjusted Price/Acre** | - | **$10,200** | - |

**Before/After Analysis:**

```
Comparable without easement (estimated): $10,200/acre × 95 acres = $969,000
Comparable with easement (actual sale): $950,000
Easement Impact: $969,000 - $950,000 = $19,000
Easement Acres: 20 acres
Implied $/ROW Acre: $19,000 ÷ 20 acres = $950/acre
Implied % of Fee: $950 ÷ $10,200 = 9.3% of fee
```

**Application to Subject:**

```
Subject ROW Area: 24.71 acres
Comparable Easement Value: $950/ROW acre
Indicated Easement Value = 24.71 acres × $950/acre
Indicated Easement Value = $23,475

Or using % of fee:
Subject Fee Value: $10,000/acre
Comparable % of Fee: 9.3%
Indicated Easement Value = 24.71 acres × $10,000 × 9.3%
Indicated Easement Value = $22,980
```

**Before/After Indication:** $23,000 to $23,500 ($950/ROW acre, 9.3% of fee)

**Note:** This method shows lower value than Percentage of Fee and Income methods, possibly due to:
- Comparable sale reflects buyer/seller perceptions rather than technical analysis
- Comparable may have less severe agricultural impacts
- Market participants may undervalue easement impacts
- Should be weighted lower in reconciliation

### Reconciliation of Values

**Summary of Indications:**

| Valuation Method | Easement Value | $/ROW Acre | % of Fee | Weight | Weighted Value |
|------------------|----------------|------------|----------|--------|----------------|
| Percentage of Fee | $51,891 | $2,100 | 21.0% | 40% | $20,756 |
| Income Capitalization | $32,947 | $1,334 | 13.3% | 40% | $13,179 |
| Before/After | $23,475 | $950 | 9.5% | 20% | $4,695 |
| **Reconciled Value** | **$38,630** | **$1,564** | **15.6%** | **100%** | **$38,630** |

**Reconciliation Logic:**

**Percentage of Fee (40% weight):**
- Most widely accepted method for utility easements
- Well-supported by market studies and industry standards
- Adjustments clearly documented and justified
- Appropriate for perpetual easements with clear restrictions

**Income Capitalization (40% weight):**
- Most relevant for income-producing agricultural property
- Directly measures economic impact to landowner
- Conservative cap rate selection (4.5%)
- Reflects actual productivity loss from easement

**Before/After (20% weight):**
- Limited comparable sales data available
- Market participants may not fully recognize easement impacts
- Useful as reality check but less weight given data limitations
- Single comparable requires more adjustment

**Final Value Conclusion:**

Based on analysis of all three methods and consideration of:
- Corridor type and restrictions (115kV transmission, perpetual)
- Property characteristics (agricultural, Class 1 soil, productive)
- Easement impacts (tower footprints, field division, irrigation)
- Market evidence (limited but supportive)

**Easement Value Range: $35,000 to $42,000**
**Most Probable Value: $38,500 (rounded)**

This represents **15.6% of fee simple value** for the affected 24.71 acres, or **$1,558 per ROW acre**.

---

## Additional Considerations

### Temporary Construction Easement

If temporary construction easement required:

**Construction Period:** [12 months]
**Construction Area:** [30 meters width × 2,500 meters = 18.5 acres]
**Agricultural Impact:** [One full growing season lost]

**Compensation Calculation:**
```
Construction Area: 18.5 acres
Annual Gross Revenue: $300/acre
Growing Seasons Lost: 1.0
Temporary Easement Value = 18.5 × $300 × 1.0 = $5,550

Plus:
- Restoration costs: $[X,XXX]
- Crop damage: $[X,XXX]
- Fence repairs: $[X,XXX]
Total Temporary Easement: $[XX,XXX]
```

### Injurious Affection

**Impacts to Remainder Property:**

**Access Impacts:**
- [Describe any access impairment to remainder lands]
- Quantification: $[X,XXX]

**Field Division:**
- [Describe impact on farm equipment efficiency]
- Quantification: $[X,XXX]

**Irrigation System:**
- Relocation required: [Yes/No]
- Cost: $[XX,XXX]
- Ongoing efficiency loss: $[X,XXX]

**Total Injurious Affection:** $[XX,XXX]

### Severance Damages

**Highest and Best Use Impact:**

Before Easement: [Row crop agriculture]
After Easement: [Row crop agriculture - unchanged]
Impact on Development Potential: [Minor - easement area limited]

**Severance Analysis:**

If easement precludes or limits development:
```
Property Value Before (development HBU): $[XX,XXX]/acre
Property Value After (agricultural HBU): $[XX,XXX]/acre
Severance = (Before - After) × Remainder Acres
```

For subject property: [No severance / $XX,XXX severance]

### Total Compensation Summary

| Compensation Component | Amount |
|------------------------|--------|
| Permanent Easement Value | $38,500 |
| Temporary Construction Easement | $[X,XXX] |
| Injurious Affection | $[X,XXX] |
| Severance Damages | $[X,XXX] |
| Disturbance Allowance | $[X,XXX] |
| **Total Compensation** | **$[XXX,XXX]** |

---

## Negotiation Considerations

### Landowner Perspective

**Key Concerns:**
1. **Agricultural productivity loss** - ongoing impact to farm income
2. **Field division** - reduced equipment efficiency, increased operating costs
3. **Irrigation system** - relocation costs and ongoing access issues
4. **Future flexibility** - restrictions on land use and development
5. **Access disruption** - maintenance vehicle access, gates, locks

**Landowner Position:**
- Seek compensation at upper end of range ($42,000+)
- Request additional compensation for:
  - Irrigation system relocation: $[XX,XXX]
  - Fence repairs and gates: $[X,XXX]
  - Annual crop loss during construction: $[X,XXX]
  - Inconvenience and disturbance: $[X,XXX]
- Negotiate favorable access provisions
- Obtain liability protection and indemnification

### Infrastructure Agency Perspective

**Valuation Support:**
- Percentage of fee method at lower end (12-15% for 115kV)
- Before/after market evidence ($23,475)
- Argue minimal agricultural impact (can farm around towers)
- Standard compensation in jurisdiction

**Agency Position:**
- Offer compensation at lower end of range ($35,000)
- Provide standard access protocols
- Limit additional compensation to demonstrated costs
- Seek voluntary agreement to avoid expropriation

### Recommended Settlement Range

**Strong Negotiating Position:** $38,000 to $42,000 for permanent easement
**Realistic Settlement:** $40,000 including:
- Base easement value: $38,500
- Irrigation system contribution: $1,000
- Disturbance allowance: $500

**Plus separate compensation for:**
- Temporary construction easement: $[X,XXX]
- Demonstrated costs (fencing, restoration): Actual invoices

---

## Comparable Sales Summary

**Comparable 1:**
- Address: [Address]
- Sale Date: [Date]
- Property Size: [XX] acres
- Sale Price: $[XXX,XXX] ($[X,XXX]/acre)
- Easement Type: [Type and voltage/product]
- Easement Area: [XX] acres ([XX%] of property)
- Implied Easement Value: $[XX,XXX] ($[X,XXX]/ROW acre)
- Relevance: [High / Medium / Low]
- Notes: [Key characteristics and comparability]

[Repeat for each comparable]

---

## Appendices

### A. Corridor Specifications

**Technical Details:**
[Include detailed corridor specifications, drawings, plans if available]

**Operator Information:**
- Easement Holder: [Utility company / Government agency]
- Contact: [Name, title, phone]
- Project: [Project name and reference number]

### B. Property Valuation Support

**Market Value Documentation:**
- Recent appraisal: [Appraiser, date, value]
- Recent sales: [Comparable fee simple sales]
- Assessment: [Municipal assessment value]
- Income analysis: [Rent comparables, cap rate support]

### C. Agricultural Rent and Cap Rate Support

**Agricultural Rent Data:**
- Source: [Farm Credit Canada / Provincial agriculture ministry / Local farm managers]
- Class 1 soil rent range: $250-$350/acre/year
- Subject area rent: $300/acre/year (mid-range)
- Rent trend: [Stable / Increasing / Decreasing]

**Capitalization Rate Support:**
- Perpetual easement rates: 4-6% (low risk)
- Utility/government operator: 4-5% (high creditworthiness)
- Selected rate: 4.5% (justified)
- Market evidence: [Sales of easement-encumbered properties]

### D. Calculation Methodology

**Percentage of Fee Method:**
- Base percentage selection by corridor type
- Adjustment factors (tower density, agricultural impact, access, buffer)
- Application to ROW area or total property value

**Income Capitalization Method:**
- Annual rent determination (fee simple land)
- Productivity loss calculation (easement impact)
- Annual income loss (rent × productivity loss × area)
- Capitalization (income loss ÷ cap rate)

**Before/After Method:**
- Market extraction from comparable sales
- Adjustment grid for property differences
- Application to subject property

### E. Supporting Documents

**Attached/Referenced:**
- Property appraisal report
- Corridor plans and specifications
- Agricultural rent survey data
- Comparable sales summaries
- Title search and legal description
- Soil classification maps
- [Other supporting documents]

---

**Report Prepared By:** Claude Code - ROW Analysis
**Analysis Date:** [Date]
**Valuation Date:** [Date]
**Purpose:** [Purpose of analysis]
**Intended Use:** [Negotiation / Expropriation / Internal decision-making]

**Disclaimer:** This analysis is prepared for the specific purpose stated above. The value conclusions are subject to the assumptions and limiting conditions outlined in this report. This report should not be relied upon for any other purpose without written consent. Market values and income estimates are based on information available as of the valuation date and may change.
```

### Step 8: Summary Output

After creating all files, provide the user with:

1. **Corridor Summary:**
   - Type: [Transmission / Pipeline / Transit]
   - Specifications: [Voltage/Product/Mode]
   - ROW Area: [X.XX] hectares ([X.XX] acres)
   - Encumbrance: [XX.X%] of property

2. **Valuation Summary:**
   - Percentage of Fee: $XXX,XXX (XX% of fee)
   - Income Capitalization: $XXX,XXX (XX% of fee)
   - Before/After: $XXX,XXX (XX% of fee)
   - Reconciled Value: $XXX,XXX (XX% of fee)

3. **Files Created:**
   - JSON input file path
   - JSON results file path (if calculator exists)
   - Markdown report path

4. **Recommended Compensation Range:**
   - Low: $XXX,XXX
   - Mid: $XXX,XXX
   - High: $XXX,XXX

5. **Next Steps:**
   - Review detailed valuation report
   - Gather additional comparables if available
   - Consider temporary easement and injurious affection
   - Prepare for negotiation or expropriation proceedings

## Important Guidelines

1. **Accurate ROW Area Calculation:**
   - Always calculate area from width × length
   - Convert units properly (meters to hectares to acres)
   - Verify encumbrance percentage against total property
   - Document calculation clearly in report

2. **Corridor-Specific Parameters:**
   - Use correct percentage of fee range for corridor type
   - Apply voltage-specific or product-specific adjustments
   - Consider access frequency and restrictions
   - Document all adjustment factors

3. **Agricultural Impact Assessment:**
   - Identify tower/facility footprints (100% loss)
   - Assess restricted zones (partial productivity loss)
   - Consider field division and equipment efficiency
   - Evaluate irrigation system impacts
   - Calculate weighted average productivity loss

4. **Multiple Valuation Methods:**
   - Always apply at least two methods (percentage of fee and income)
   - Use before/after if comparable sales available
   - Reconcile with appropriate weighting
   - Document reconciliation logic clearly

5. **Professional Output:**
   - Use clear, objective language
   - Provide well-supported value conclusions
   - Include sensitivity analysis if requested
   - Flag data limitations and assumptions

## Related Commands and Skills

**Related Slash Commands:**
- `/Expropriation/compensation-entitlement` - Legal framework for expropriation compensation
- `/Expropriation/disturbance-damages` - Quantify disturbance and relocation costs
- `/Valuation/comparable-sales` - Detailed comparable sales analysis

**Related Skills:**
- `easement-valuation-methods` - Technical valuation methodology (auto-loaded)
- `agricultural-easement-negotiation-frameworks` - Farm-specific negotiation strategies
- `transmission-line-technical-specifications` - Voltage-specific corridor requirements
- `expropriation-compensation-entitlement-analysis` - Legal compensation framework

**Related Calculators:**
- `easement_valuation_calculator.py` - Core valuation engine
- `comparable_sales_calculator.py` - Statistical adjustment analysis
- `severance_damages_calculator.py` - Highest and best use impact quantification

## Example Usage

### Example 1: Transmission Line ROW

```
/right-of-way-analysis "115kV transmission, 40m width, 2.5km length" "100 acre farm, $10,000/acre, Class 1 soil, corn and soybeans"
```

This will:
1. Calculate ROW area: 40m × 2,500m = 10 ha = 24.71 acres (24.71% encumbrance)
2. Apply 115kV percentage range (12-18%) with adjustments
3. Calculate income loss from agricultural productivity impact
4. Generate easement value: $35,000-$42,000 range
5. Create comprehensive report with three valuation methods

### Example 2: Pipeline Corridor

```
/right-of-way-analysis "36-inch high-pressure natural gas pipeline, 25m width, 1.8km" "/path/to/property_appraisal.pdf"
```

This will:
1. Calculate ROW area: 25m × 1,800m = 4.5 ha = 11.12 acres
2. Extract property details from appraisal PDF
3. Apply pipeline percentage range (20-25%) with product-specific adjustments
4. Calculate easement value based on before/after and percentage of fee
5. Generate report with safety buffer and restriction analysis

### Example 3: LRT Transit Corridor

```
/right-of-way-analysis "/path/to/corridor_specs.json" "/path/to/property_data.json"
```

This will:
1. Load corridor specifications from JSON (LRT, 25m width, 3.2km)
2. Load property data from JSON
3. Calculate ROW area and encumbrance percentage
4. Apply transit percentage range (25-30%) with noise/vibration adjustments
5. Assess impacts to remainder property (access, severance)
6. Generate comprehensive valuation report

Begin the ROW analysis now with the provided corridor and property information.
