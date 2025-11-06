# Extract MLS Data to Excel

**Purpose**: Extract all property data from MLS PDF reports into a beautifully formatted Excel spreadsheet.

**Magic**: One command. Perfect output. Zero configuration.

---

## Command

Extract MLS property data and create professional Excel spreadsheet:

**Arguments**:
1. `<pdf-path>` - Path to MLS PDF report
2. `[--subject="partial address"]` - Optional: Partial address to identify subject property

**Example**:
```bash
/extract-mls Mississauga_industrial.pdf --subject="2550 Stanfield"
```

---

## Workflow

You will execute the following steps to create a perfect Excel extraction:

### Step 1: Read the PDF

Use the Read tool to read the MLS PDF file. This will give you the full text content to extract from.

### Step 2: Extract Property Data

Extract ALL properties from the PDF into a JSON structure. For each property, extract these 34 fields:

#### Critical Fields (Always Extract)
1. **address** - Full street address
2. **unit** - Unit/suite number (empty string if not applicable)
3. **available_sf** - Available square footage (integer)
4. **net_asking_rent** - Net asking rent in $/SF/year (float, e.g., 13.95)
5. **tmi** - TMI/operating costs in $/SF/year (float, e.g., 3.01)
6. **year_built** - Year property was built (integer, e.g., 2024)
7. **clear_height_ft** - Clear ceiling height in feet (float, e.g., 34.0)
8. **pct_office_space** - Percentage of space that is office (float 0-1, e.g., 0.03 for 3%)
9. **parking_ratio** - Parking spaces per 1,000 SF (float, e.g., 2.5)
10. **class** - Building class: 1=A, 2=B, 3=C (integer)

#### Optional Fields (Extract if Available)
11. **shipping_doors_tl** - Number of truck-level shipping doors (integer)
12. **shipping_doors_di** - Number of drive-in shipping doors (integer)
13. **power_amps** - Electrical power in amps (integer)
14. **bay_depth_ft** - Bay depth in feet (parse from "Bay Size: 55 x 52" → 55.0)
15. **lot_size_acres** - Lot size in acres (convert sq ft to acres if needed: ÷ 43,560)
16. **hvac_coverage** - HVAC coverage: 1=Yes, 2=Partial, 3=No (integer)
17. **sprinkler_type** - Sprinkler type: 1=ESFR, 2=Standard, 3=None (integer)
18. **rail_access** - Rail siding available: true/false (boolean)
19. **crane** - Overhead crane available: true/false (boolean)
20. **occupancy_status** - 1=Vacant, 2=Occupied (integer)
21. **trailer_parking** - Trailer parking available: true/false (boolean)
22. **secure_shipping** - Secure shipping available: true/false (boolean)
23. **excess_land** - Excess land available: true/false (boolean)
24. **grade_level_doors** - Number of grade-level doors (integer)
25. **days_on_market** - Days property has been on market (integer)
26. **zoning** - Zoning classification (string, e.g., "M1", "I2")

#### Metadata Fields
27. **availability_date** - When space is available (string, e.g., "Immediate", "Q3 2025")
28. **mls_number** - MLS listing number (string)
29. **broker_name** - Listing broker name (string)
30. **client_remarks** - Marketing remarks (string, truncate to 500 chars)
31. **is_subject** - Is this the subject property? (boolean) - AUTO-DETECT or use --subject flag
32. **reported_market** - Market name (string, e.g., "Mississauga Industrial")
33. **report_generated_at** - When the report was generated (string)
34. **source_pdf** - PDF filename (string)

### Step 3: Auto-Detect Subject Property

**Auto-detection logic**:
1. First check: Look for "Subject" keyword in client_remarks field
2. If --subject flag provided: Fuzzy match against address (case-insensitive partial match)
3. Default: If no subject found, mark first property as subject

Set `is_subject: true` for exactly ONE property.

### Step 4: Calculate Derived Fields

For each property, calculate:
- **gross_rent** = net_asking_rent + tmi
- **building_age_years** = current_year - year_built (use 2025 as current year)

### Step 5: Create JSON Output

Write extracted data to JSON file in Reports/ folder:

**Format**: `Reports/YYYY-MM-DD_HHMMSS_mls_extraction_input.json` (Eastern Time)

**JSON Structure**:
```json
{
  "extraction_date": "2025-11-06",
  "source_pdf": "Mississauga_industrial.pdf",
  "market": "Mississauga - Industrial (100-400k SF)",
  "total_properties": 23,
  "properties": [
    {
      "is_subject": true,
      "address": "2550 Stanfield Rd, Mississauga, ON L4Y 1S2, Canada",
      "unit": "Suite 200",
      "available_sf": 238501,
      "net_asking_rent": 13.95,
      "tmi": 3.01,
      "gross_rent": 16.96,
      "clear_height_ft": 34.0,
      "building_age_years": 1,
      "year_built": 2024,
      "class": 2,
      "parking_ratio": 2.5,
      "pct_office_space": 0.03,
      "shipping_doors_tl": 29,
      "shipping_doors_di": 3,
      "power_amps": 3000,
      "bay_depth_ft": 55.0,
      "lot_size_acres": 12.5,
      "hvac_coverage": 2,
      "sprinkler_type": 2,
      "rail_access": false,
      "crane": false,
      "occupancy_status": 1,
      "trailer_parking": false,
      "secure_shipping": false,
      "excess_land": false,
      "grade_level_doors": 2,
      "days_on_market": 45,
      "zoning": "M2",
      "availability_date": "Immediate",
      "mls_number": "C5942816",
      "broker_name": "CBRE Limited",
      "client_remarks": "Brand new construction...",
      "reported_market": "Mississauga - Industrial (100-400k SF)",
      "report_generated_at": "2025-11-06",
      "source_pdf": "Mississauga_industrial.pdf"
    }
  ]
}
```

### Step 6: Create Perfect Excel

Run the Python formatter to create the perfect Excel file:

```bash
python MLS_Extractor/excel_formatter.py <json-input-path> <excel-output-path>
```

The formatter will:
- Create professionally formatted Excel with perfect styling
- Highlight subject property in bright yellow (impossible to miss)
- Apply perfect column ordering (most important data first)
- Format numbers correctly (currency, percentages, integers)
- Auto-size columns for perfect readability
- Freeze headers and enable auto-filter

### Step 7: Report Success

Tell the user:

```
✅ Extracted {N} properties from {PDF filename}
✅ Subject property: {address}
✅ Excel file: Reports/{timestamp}_mls_extraction_{market}.xlsx

Open the Excel file to review the data. The subject property is highlighted in yellow.
```

---

## Parsing Rules

### Bay Depth
- Input: "Bay Size: 55 x 52"
- Extract: 55.0 (first number is depth)

### Lot Size
- Input: "Lot: 543,892 SF" → Convert to acres: 543892 / 43560 = 12.5 acres
- Input: "Lot: 12.5 acres" → Use directly: 12.5

### HVAC Coverage
- "Yes", "Y", "100%" → 1
- "Partial", "Part", "50%" → 2
- "No", "N", "0%" → 3

### Sprinkler Type
- "ESFR" → 1
- "Standard", "Conventional" → 2
- "None", "N/A" → 3

### Occupancy Status
- "Vacant", "Available" → 1
- "Occupied", "Tenant in Place" → 2

### Office Percentage
- Input: "97% Warehouse, 3% Office" → pct_office_space = 0.03
- Input: "5% Office" → pct_office_space = 0.05

---

## Error Handling

**If a field is missing or cannot be parsed**:
- Numeric fields → 0
- Boolean fields → false
- String fields → ""
- DO NOT fail the entire extraction

**Quality check**:
- Verify at least 90% of critical fields extracted (10 fields × 90% = 9 fields minimum)
- If quality check fails, warn user but still create Excel

---

## The Test

Before returning to the user, ask yourself:

> **"Would I be proud to send this Excel file to my CEO?"**

If not, iterate until the answer is yes.

---

**Philosophy**: Perfect is the only acceptable standard.

