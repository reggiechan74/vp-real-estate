# MLS Data Extraction Slash Command - Implementation Plan

**Date**: 2025-11-05
**Branch**: feature/enhance-valuation-variables
**Purpose**: Extract enhanced MLS field set to structured CSV/Excel format for analysis

---

## EXECUTIVE SUMMARY

Create a new slash command `/Financial_Analysis:extract-mls` that extracts all 23 valuation variables plus broker comments from MLS PDF reports into a structured spreadsheet format (CSV or Excel).

**Key Benefits**:
- Streamlines data entry for comparative analysis
- Captures all enhanced variables (bay depth, lot size, HVAC, sprinklers, etc.)
- Preserves broker comments for qualitative insights
- Enables bulk import into valuation calculator
- Professional Excel formatting for client delivery

---

## SCOPE

### In Scope
- Extract all 23 valuation variables (9 core + 14 optional)
- Extract broker comments/remarks fields
- Support both CSV (simple) and Excel (formatted) output
- Handle multiple properties from single PDF (batch extraction)
- Robust parsing with fallback for missing fields
- Eastern Time timestamps for output filenames
- Save to `Reports/` folder with standard naming convention

### Out of Scope (Phase 2)
- Automatic distance calculation (use existing `/relative-valuation` workflow)
- Data validation/quality checks (assume clean MLS data)
- Integration with CRM systems
- Web scraping from MLS websites
- Image extraction (photos, floor plans)

---

## INPUT SPECIFICATION

### Command Syntax
```bash
/extract-mls <pdf-path> [--format=csv|excel] [--subject=<address>]
```

**Parameters**:
- `<pdf-path>` (required): Path to MLS PDF report
- `--format` (optional): Output format, default `excel`
  - `csv`: Plain CSV file
  - `excel`: Formatted XLSX with headers, filters, column sizing
- `--subject` (optional): Address of subject property to mark with `is_subject=true`

**Example**:
```bash
/extract-mls /path/to/Mississauga_100-400k_sf_for_lease.pdf --format=excel --subject="2550 Stanfield"
```

---

## OUTPUT SPECIFICATION

### File Naming Convention
**Format**: `YYYY-MM-DD_HHMMSS_mls_extraction_<market>.{csv|xlsx}` (Eastern Time)

**Example**: `2025-11-05_183047_mls_extraction_mississauga.csv`

### Output Location
`Reports/` folder (consistent with other financial analysis outputs)

---

## FIELD MAPPING

### Core Variables (9 fields)

| Column Name | Data Type | MLS Source Field | Example | Notes |
|-------------|-----------|------------------|---------|-------|
| `address` | String | Address | "2550 Stanfield Rd, Mississauga, ON L4Y 1S2, Canada" | Complete geocodable format |
| `unit` | String | Unit/Suite | "Opt 2" | Separate from address |
| `available_sf` | Integer | Area | 186559 | Rentable square footage |
| `net_asking_rent` | Float | $/SF Net or Rent | 13.95 | Net asking rent per SF |
| `tmi` | Float | Addl Rent or T.M.I. | 3.01 | Additional rent/TMI per SF |
| `year_built` | Integer | Yr Blt | 2020 | Year constructed |
| `clear_height_ft` | Float | Clear Ht | 34.0 | Clear height in feet |
| `pct_office_space` | Float | % Office | 0.03 | Percentage (0.03 = 3%) |
| `parking_ratio` | Float | Parking/1000 | 1.0 | Spaces per 1,000 SF |
| `class` | Integer | Class | 2 | A=1, B=2, C=3 |

### Existing Optional Variables (6 fields)

| Column Name | Data Type | MLS Source Field | Example | Notes |
|-------------|-----------|------------------|---------|-------|
| `shipping_doors_tl` | Integer | Truck Level or Ship (TL) | 16 | Truck-level doors |
| `shipping_doors_di` | Integer | Drive-In or Ship (DI) | 3 | Drive-in doors |
| `power_amps` | Integer | Power | 3000 | Electrical service in amps |
| `trailer_parking` | Boolean | Trailer Pkg or Outside Pkg | true | Trailer parking available |
| `secure_shipping` | Boolean | Secure Ship | false | Secure/enclosed shipping |
| `excess_land` | Boolean | Excess Land | false | Additional developable land |

### New Optional Variables (8 fields)

| Column Name | Data Type | MLS Source Field | Example | Extraction Logic |
|-------------|-----------|------------------|---------|------------------|
| `bay_depth_ft` | Float | Bay Size | 55.0 | Parse "55 x 52" → 55.0 (regex) |
| `lot_size_acres` | Float | Lot Irreg or Lot Size Area | 11.112 | Parse acres or convert sq ft |
| `hvac_coverage` | Integer | A/C | 1 | Y=1, Part=2, N=3 (ordinal) |
| `sprinkler_type` | Integer | Sprinklers + Client Remks | 1 | ESFR=1, Standard=2, None=3 |
| `building_age_years` | Integer | Calculated | 5 | 2025 - year_built |
| `rail_access` | Boolean | Rail | false | Y/N boolean |
| `crane` | Boolean | Crane | false | Y/N boolean |
| `occupancy_status` | Integer | Occup | 1 | Vacant=1, Tenant=2 (ordinal) |

### Metadata & Comments (6 fields)

| Column Name | Data Type | MLS Source Field | Example | Notes |
|-------------|-----------|------------------|---------|-------|
| `availability_date` | String | Avail | "Immediate" | Date or "Immediate" |
| `days_on_market` | Integer | DOM | 119 | Days on market |
| `mls_number` | String | ML# or MLS# | "C1234567" | MLS listing number |
| `broker_name` | String | List Off or Agent | "CBRE Limited" | Listing broker |
| `client_remarks` | Text | Client Remks | "ESFR sprinklers, new LED..." | Marketing description |
| `is_subject` | Boolean | Derived | true | Matched against --subject parameter |

**Total Columns**: 32

---

## TECHNICAL APPROACH

### Technology Stack

**Option A: CSV Output (Simple)**
- Python `csv` module
- Minimal dependencies
- Fast processing
- Good for bulk data import

**Option B: Excel Output (Recommended)**
- Python `openpyxl` library
- Professional formatting:
  - Header row: bold, background color, freeze panes
  - Auto-filter enabled on all columns
  - Column width auto-sizing
  - Number formatting (currency for rent/TMI, integers for SF)
  - Conditional formatting for `is_subject` row (highlight)
- Better for client delivery

### PDF Extraction Strategy

**Use existing markitdown pipeline**:
```python
import subprocess
import json

# Step 1: Convert PDF to markdown
subprocess.run(['markitdown', pdf_path, '-o', 'temp.md'])

# Step 2: Parse markdown tables
# MLS PDFs typically have structured tables - one row per property

# Step 3: Map fields using field mapping table above

# Step 4: Apply extraction logic (regex, conversions, lookups)

# Step 5: Write to CSV or Excel
```

**Alternative**: If markitdown struggles with MLS table structure, use `pdfplumber` for direct table extraction:
```python
import pdfplumber

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
        # Process tables...
```

---

## IMPLEMENTATION STEPS

### Phase 1: Command Setup
1. Create `.claude/commands/Financial_Analysis/extract-mls.md`
2. Define command parameters and workflow
3. Add command documentation to README

### Phase 2: Extraction Logic
4. Create `MLS_Extractor/` directory
5. Implement `extract_mls.py` with:
   - PDF parsing (markitdown or pdfplumber)
   - Field extraction using mapping table
   - Robust parsing functions (bay depth, lot size, etc.)
   - Subject property matching logic
6. Create unit tests for extraction functions

### Phase 3: Output Formatting
7. Implement CSV writer
8. Implement Excel writer with formatting:
   ```python
   from openpyxl import Workbook
   from openpyxl.styles import Font, PatternFill, Alignment
   from openpyxl.utils import get_column_letter

   # Create workbook
   wb = Workbook()
   ws = wb.active
   ws.title = "MLS Extraction"

   # Write headers
   headers = ['address', 'unit', 'available_sf', ...]
   ws.append(headers)

   # Format header row
   header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
   header_font = Font(bold=True, color='FFFFFF')
   for cell in ws[1]:
       cell.fill = header_fill
       cell.font = header_font

   # Freeze header row
   ws.freeze_panes = 'A2'

   # Enable auto-filter
   ws.auto_filter.ref = ws.dimensions

   # Auto-size columns
   for column in ws.columns:
       max_length = max(len(str(cell.value or '')) for cell in column)
       ws.column_dimensions[get_column_letter(column[0].column)].width = max_length + 2
   ```

9. Add conditional formatting for subject property row:
   ```python
   from openpyxl.formatting.rule import Rule
   from openpyxl.styles.differential import DifferentialStyle

   # Highlight subject property in yellow
   yellow_fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')
   # Apply to rows where is_subject = TRUE
   ```

### Phase 4: Integration
10. Update slash command to call extraction script
11. Test with Mississauga dataset (23 properties)
12. Validate all 32 fields extract correctly
13. Test both CSV and Excel outputs

### Phase 5: Documentation
14. Update command help text
15. Add usage examples to documentation
16. Document field mapping table
17. Create troubleshooting guide

---

## EXAMPLE OUTPUT

### CSV Format (first 3 rows)
```csv
address,unit,available_sf,net_asking_rent,tmi,year_built,clear_height_ft,pct_office_space,parking_ratio,class,shipping_doors_tl,shipping_doors_di,power_amps,trailer_parking,secure_shipping,excess_land,bay_depth_ft,lot_size_acres,hvac_coverage,sprinkler_type,building_age_years,rail_access,crane,occupancy_status,availability_date,days_on_market,mls_number,broker_name,client_remarks,is_subject
"2550 Stanfield Rd, Mississauga, ON L4Y 1S2, Canada",Opt 2,186559,13.95,3.01,2020,34.0,0.03,1.0,2,16,3,3000,False,False,False,,,2,2,5,False,False,1,Immediate,45,C1234567,CBRE Limited,"Partial A/C, standard sprinklers, excellent access to 401/407",True
"795 Hazelhurst Rd, Mississauga, ON L5J 2Z6, Canada",,215124,1.00,4.00,2021,36.0,0.05,1.2,1,34,2,2000,False,False,False,55.0,6.5,1,1,4,False,False,1,Q2 2026,89,C7654321,JLL,"ESFR sprinklers, full A/C, deep 55' bays ideal for racking",False
"560 Slate Dr, Mississauga, ON L5T 0A1, Canada",,160485,1.00,0.00,2019,40.0,0.02,1.5,1,26,2,,True,False,False,52.0,11.112,1,1,6,False,False,1,Q3 2025,119,C9876543,Cushman & Wakefield,"ESFR, 40' clear, trailer parking, large lot",False
```

### Excel Format
**Sheet Name**: MLS Extraction

**Header Row** (Row 1): Bold white text on dark blue background, frozen
**Filters**: Enabled on all columns
**Column Widths**: Auto-sized to content
**Subject Row**: Yellow highlight background
**Number Formatting**:
- `available_sf`: `#,##0` (no decimals)
- `net_asking_rent`, `tmi`: `$#,##0.00`
- `clear_height_ft`, `bay_depth_ft`: `#,##0.0`
- `pct_office_space`: `0.0%`
- `parking_ratio`, `lot_size_acres`: `#,##0.00`

**Conditional Formatting**:
- `is_subject = TRUE`: Entire row highlighted in yellow

---

## VALIDATION PLAN

### Test Case 1: Mississauga Dataset (23 properties)
**Input**: `skillsdevdocs/Mississauga_100-400k_sf_for_lease.pdf`
**Expected**: 23 rows extracted, all 32 fields populated
**Validation**:
- All addresses in correct geocodable format
- Bay depth parsed for properties with "Bay Size" field
- Lot sizes converted to acres (including sq ft → acre conversion)
- ESFR sprinklers detected from Client Remarks
- Subject property (2550 Stanfield Opt 2) marked with `is_subject=true`

### Test Case 2: Missing Data Handling
**Input**: Property with incomplete MLS data
**Expected**: Empty cells or NULL values, no crash
**Validation**:
- Missing bay size → `bay_depth_ft` = NULL
- Missing lot size → `lot_size_acres` = NULL
- Missing A/C → `hvac_coverage` = 3 (default to N)

### Test Case 3: CSV vs Excel Output
**Input**: Same PDF, generate both formats
**Expected**: Identical data, different formatting
**Validation**:
- CSV: plain text, no formatting
- Excel: formatted headers, filters, column sizing, subject highlight

### Test Case 4: Subject Property Matching
**Input**: `--subject="2550 Stanfield"`
**Expected**: Only rows with "2550 Stanfield" in address get `is_subject=true`
**Validation**:
- Fuzzy matching (partial address match)
- Case-insensitive
- Multiple units at same address handled correctly

---

## ERROR HANDLING

### Scenario 1: PDF Parsing Failure
**Error**: PDF has unusual structure, tables not detected
**Handling**: Log error, fall back to manual extraction prompt for user

### Scenario 2: Missing Required Fields
**Error**: Address or Available SF missing
**Handling**: Skip row, log warning with property identifier

### Scenario 3: Invalid Data Types
**Error**: Clear height = "N/A" (expected float)
**Handling**: Set to NULL, log warning, continue processing

### Scenario 4: Output File Already Exists
**Error**: Timestamp collision (same second)
**Handling**: Append counter suffix: `_mls_extraction_mississauga_1.xlsx`

---

## INTEGRATION WITH EXISTING WORKFLOW

### Current Workflow
1. User runs `/relative-valuation` command
2. Command extracts data and creates JSON input file
3. JSON fed to Python calculator
4. Calculator generates report

### Enhanced Workflow with `/extract-mls`
1. User runs `/extract-mls` to create Excel spreadsheet
2. User reviews/edits spreadsheet (manual QA step)
3. User converts Excel to JSON (new utility script or manual)
4. User runs `/relative-valuation` with JSON input (skip PDF extraction)
5. Calculator generates report

**Alternative**: Direct integration
1. `/extract-mls` generates both Excel (for review) AND JSON (for automation)
2. JSON automatically fed to distance calculator
3. User can run `/relative-valuation` immediately or review Excel first

---

## DEPENDENCIES

### Python Libraries
- `markitdown` - Already installed, PDF to markdown conversion
- `openpyxl` - Excel file creation and formatting
- `pdfplumber` - Alternative PDF table extraction (if markitdown insufficient)
- Standard library: `csv`, `json`, `re`, `subprocess`, `datetime`, `zoneinfo`

### Installation
```bash
pip install openpyxl pdfplumber
```

---

## FUTURE ENHANCEMENTS (Phase 2)

### 1. Data Validation Rules
- Flag properties with missing critical fields (address, SF, rent)
- Highlight outliers (rent >2x median, clear height <20 ft)
- Validate postal codes, phone numbers

### 2. Excel Charts & Pivot Tables
- Rent distribution histogram
- Clear height vs area scatter plot
- Property class breakdown pie chart
- Pre-configured pivot table for quick analysis

### 3. Multi-Sheet Workbooks
- Sheet 1: Raw data extraction
- Sheet 2: Summary statistics
- Sheet 3: Data quality report (missing fields, outliers)

### 4. CRM/MLS Integration
- Direct API integration with MLS systems (CREA, TREB)
- Automatic updates when listings change
- Historical price tracking

### 5. Batch Processing
- Process multiple PDFs in single command
- Aggregate into master spreadsheet
- Cross-market comparison (Mississauga vs Brampton vs Vaughan)

---

## SUCCESS CRITERIA

### Functional Requirements
- ✅ Extract all 32 fields from MLS PDF
- ✅ Support CSV and Excel output formats
- ✅ Handle 20+ properties per PDF
- ✅ Robust parsing with 95%+ field accuracy
- ✅ Subject property identification
- ✅ Professional Excel formatting

### Performance Requirements
- ✅ Process 25-property PDF in <30 seconds
- ✅ File size <5 MB for 100 properties

### Quality Requirements
- ✅ Zero crashes on malformed PDFs (graceful degradation)
- ✅ Field accuracy validated against manual extraction (spot check 10%)
- ✅ Excel files open correctly in Microsoft Excel and Google Sheets

---

## TIMELINE ESTIMATE

| Phase | Tasks | Estimated Effort |
|-------|-------|------------------|
| Phase 1 | Command setup, documentation | 2 hours |
| Phase 2 | Extraction logic, parsing functions | 8 hours |
| Phase 3 | Output formatting (CSV + Excel) | 4 hours |
| Phase 4 | Integration, testing | 4 hours |
| Phase 5 | Documentation, examples | 2 hours |
| **Total** | | **20 hours** |

---

## RISKS & MITIGATION

### Risk 1: MLS PDF Format Variations
**Impact**: High - Different brokers use different PDF formats
**Mitigation**:
- Test with multiple MLS providers (CBRE, JLL, Cushman, Colliers)
- Build flexible parser with fallback strategies
- Document known format variations

### Risk 2: Field Mapping Ambiguity
**Impact**: Medium - Field names vary across MLS systems
**Mitigation**:
- Create field alias dictionary (e.g., "Addl Rent" = "T.M.I." = "OpEx")
- Allow user to provide custom field mappings via config file
- Log unmapped fields for manual review

### Risk 3: Excel Library Compatibility
**Impact**: Low - openpyxl may not support all Excel features
**Mitigation**:
- Test in Microsoft Excel, LibreOffice Calc, Google Sheets
- Stick to basic formatting (fonts, colors, filters)
- Avoid advanced features (macros, complex formulas)

---

## DELIVERABLES

### Code
1. `.claude/commands/Financial_Analysis/extract-mls.md` - Slash command definition
2. `MLS_Extractor/extract_mls.py` - Main extraction script
3. `MLS_Extractor/field_parsers.py` - Parsing functions (bay depth, lot size, etc.)
4. `MLS_Extractor/excel_formatter.py` - Excel formatting utilities
5. `MLS_Extractor/tests/` - Unit tests

### Documentation
6. `MLS_Extractor/README.md` - Usage guide
7. `MLS_Extractor/FIELD_MAPPING.md` - Complete field reference
8. Updated `.claude/commands/README.md` - Add `/extract-mls` to command list
9. Example output files in `Reports/` folder

### Testing
10. Test with Mississauga dataset (23 properties)
11. Validation report comparing automated vs manual extraction
12. Excel file sample for review

---

## NEXT STEPS

1. Review and approve this implementation plan
2. Create GitHub issue to track development
3. Set up development environment (install openpyxl, pdfplumber)
4. Implement Phase 1 (command setup)
5. Prototype extraction logic with Mississauga PDF
6. Iterate on field parsing accuracy
7. Build Excel formatter
8. End-to-end testing
9. Documentation and examples
10. Merge to main branch

---

**END OF PLAN**
