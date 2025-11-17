# Title Analyzer

Comprehensive title search analysis for real property, including registered instruments parsing, encumbrance analysis, registration validation, and marketability assessment.

## Features

### Core Analysis

- **Registered Instruments Parsing**
  - Classify instruments by type (easements, covenants, liens, mortgages, leases)
  - Assign legal priority based on registration date
  - Extract parties, descriptions, and area affected
  - Flag critical instruments requiring immediate attention

- **Encumbrance Analysis**
  - Assess impact severity (CRITICAL, HIGH, MEDIUM, LOW)
  - Identify use restrictions (building, height, setback, access, drainage)
  - Determine enforcement risk and priority
  - Calculate value impact ranges (min/max/likely percentages)
  - Recommend remedial actions

- **Registration Validation**
  - Detect defects in party information (missing grantor/grantee)
  - Validate legal descriptions and instrument numbers
  - Check type-specific requirements (lien amounts, mortgage principals, lease terms)
  - Assess overall registration validity (VALID, NEEDS_REVIEW, QUESTIONABLE, INVALID)

- **Marketability Assessment**
  - Calculate marketability score (0-100)
  - Rate marketability (EXCELLENT, GOOD, FAIR, POOR, UNMARKETABLE)
  - Assess buyer pool impact (percentage of typical market)
  - Evaluate financing availability (READILY AVAILABLE, LIMITED, NOT AVAILABLE)
  - Estimate liquidity impact

- **Value Impact Calculation**
  - Estimate market value discount ranges
  - Combine encumbrance-specific impacts with overall marketability
  - Provide interpretation (minimal, moderate, significant, severe)

## Installation

No additional dependencies required beyond standard Python 3.7+ libraries:
- `json`
- `pathlib`
- `datetime`
- `pytz`
- `typing`
- `re`

## Usage

### Basic Usage

```bash
# Analyze title and output to stdout
python title_analyzer.py input.json

# Generate markdown report
python title_analyzer.py input.json --output report.md

# Generate both markdown and JSON outputs
python title_analyzer.py input.json --output report.md --json results.json

# Auto-generate timestamped outputs in Reports/ directory
python title_analyzer.py input.json --auto-output
```

### Command Line Arguments

```
positional arguments:
  input                 Path to input JSON file

optional arguments:
  -h, --help            Show help message
  --output, -o          Path to markdown output file (optional)
  --json, -j            Path to JSON output file (optional)
  --auto-output, -a     Auto-generate output filenames with timestamp
  --verbose, -v         Verbose output with full error traces
```

## Input Format

### Required Fields

```json
{
  "property_identifier": "PIN 12345-6789 (LT)",
  "property_address": "100 Industrial Road, Toronto, ON"
}
```

### Registered Instruments

```json
{
  "registered_instruments": [
    {
      "instrument_number": "AT1234567",
      "instrument_type": "Easement",
      "parties": {
        "grantor": "Owner Name",
        "grantee": "Utility Company"
      },
      "description": "Hydro transmission easement",
      "registration_date": "1985-03-15",
      "area_affected": "2.5 acres along eastern boundary"
    }
  ]
}
```

**Instrument Types:**
- Easement / Right of Way / ROW
- Covenant / Restrictive Covenant / Building Scheme
- Restriction / Use Restriction
- Lien / Construction Lien / Mechanic's Lien
- Mortgage / Charge
- Lease
- Encroachment
- Notice / Notice of Security Interest
- Court Order
- Caution
- Certificate of Pending Litigation / CPL

### Optional Fields

```json
{
  "restrictions": [
    {
      "type": "Zoning Restriction",
      "description": "Property zoned Employment Industrial (EI)",
      "date": "2019-05-01"
    }
  ],
  "encumbrances": [
    {
      "type": "Easement",
      "description": "Utility easement",
      "reference": "Plan 123",
      "priority": "First Priority",
      "date": "1980-01-01"
    }
  ],
  "defects": [
    {
      "instrument": "AT6789012",
      "category": "Parties",
      "severity": "MAJOR",
      "description": "Missing grantor identification",
      "impact": "Instrument may be defective",
      "remedy": "Obtain legal opinion"
    }
  ],
  "analysis_parameters": {
    "marketability_thresholds": {
      "high_impact": 15.0,
      "medium_impact": 5.0,
      "low_impact": 0.0
    },
    "critical_instrument_types": [
      "Lien",
      "Mortgage",
      "Court Order",
      "Notice of Security Interest"
    ]
  }
}
```

## Output

### Markdown Report Sections

1. **Executive Summary**
   - Marketability rating and score
   - Registration status
   - Estimated value impact
   - Key findings
   - Buyer pool and financing availability

2. **Critical Issues** (if any)
   - Critical encumbrances requiring immediate attention
   - Critical registration defects
   - Recommended actions

3. **Marketability Assessment**
   - Component scores (encumbrances, registration, financing, liquidity)
   - Value impact estimates (min/max/likely)
   - Buyer pool analysis
   - Likely buyer types

4. **Encumbrance Summary**
   - Total count by severity
   - Action required count
   - Average value impact

5. **Detailed Encumbrance Analysis**
   - Grouped by severity (CRITICAL, HIGH, MEDIUM, LOW)
   - Type, description, priority, value impact
   - Use restrictions
   - Recommended actions

6. **Registration Validation**
   - Overall status and marketability
   - Defects by severity
   - Recommendations

7. **Registered Instruments**
   - Summary by type
   - Priority order table
   - Registration date ranges

8. **Recommendations**
   - Prioritized action items
   - Remediation strategies

9. **Data Quality Assessment** (if quality < 90%)
   - Completeness score
   - Issues and warnings

### JSON Output Structure

```json
{
  "metadata": {
    "property_id": "...",
    "property_address": "...",
    "analysis_date": "2025-11-17T...",
    "analyzer_version": "1.0.0"
  },
  "marketability": {
    "overall_score": 49.5,
    "rating": "POOR",
    "component_scores": { ... },
    "buyer_pool": { ... },
    "recommendations": [ ... ]
  },
  "value_impact": {
    "min_discount_pct": 18.0,
    "max_discount_pct": 35.0,
    "likely_discount_pct": 26.5,
    "basis": "...",
    "interpretation": "..."
  },
  "encumbrances": {
    "summary": { ... },
    "critical": [ ... ],
    "high": [ ... ],
    "all": [ ... ]
  },
  "validation": { ... },
  "instruments": { ... },
  "data_quality": { ... },
  "warnings": [ ... ]
}
```

## Scoring Methodology

### Marketability Score (0-100)

**Component Weights:**
- Encumbrances: 35%
- Registration Defects: 30%
- Financing Availability: 20%
- Liquidity: 15%

**Encumbrance Scoring:**
- Start at 100
- Deduct 30 points per CRITICAL issue
- Deduct 15 points per HIGH issue
- Deduct 5 points per MEDIUM issue
- Deduct 1 point per LOW issue

**Registration Scoring:**
- VALID: 100 points
- MINOR_ISSUES: 85 points
- NEEDS_REVIEW: 60 points
- QUESTIONABLE: 30 points
- INVALID: 0 points

**Financing Scoring:**
- Start at 100
- Deduct 40 points for liens/litigation (lenders won't finance)
- Deduct 10 points for existing mortgages
- Deduct 5 points for major easements

**Liquidity Scoring:**
- Start at 100
- Deduct 40 points if unmarketable
- Deduct 30 points if >10 encumbrances (very complex)
- Deduct 15 points if 6-10 encumbrances (moderately complex)
- Deduct 5 points if 3-5 encumbrances (slightly complex)

### Marketability Ratings

- **EXCELLENT** (85-100): Clean title, minimal encumbrances, all buyer types
- **GOOD** (70-84): Some encumbrances, manageable, most buyer types
- **FAIR** (50-69): Moderate issues, limited buyer pool, financing with conditions
- **POOR** (30-49): Significant issues, severely limited buyer pool, difficult financing
- **UNMARKETABLE** (0-29): Critical defects, minimal buyer interest, remediation required

### Value Impact Estimates

**Base Discounts by Rating:**
- EXCELLENT: 0-2%
- GOOD: 2-8%
- FAIR: 8-18%
- POOR: 18-35%
- UNMARKETABLE: 35-60%

**Adjustments:**
- Add encumbrance-specific impacts
- Use higher of base or encumbrance total
- Calculate min/max/likely ranges

## Architecture

### Modular Design

```
title_analyzer.py          # Main orchestration (<400 lines)
├── modules/
│   ├── __init__.py                      # Module exports
│   ├── validators.py                    # Input validation
│   ├── title_parsing.py                 # Parse registered instruments
│   ├── encumbrance_analysis.py          # Analyze encumbrances
│   ├── registration_validation.py       # Validate registration
│   ├── marketability_assessment.py      # Assess marketability
│   └── output_formatters.py             # Generate reports
└── samples/
    ├── example_title_input.json         # Sample input
    ├── example_report.md                # Sample markdown output
    └── example_results.json             # Sample JSON output
```

### Module Responsibilities

**validators.py**
- Load and validate JSON input
- Check required fields and data types
- Assess data quality and completeness
- Validate output paths

**title_parsing.py**
- Parse and categorize instruments by type
- Assign priority based on registration date
- Extract parties, areas, dates
- Calculate registration age
- Flag critical instruments

**encumbrance_analysis.py**
- Analyze encumbrance impact and severity
- Assess use restrictions
- Determine priority and enforcement risk
- Estimate value impact ranges
- Generate recommended actions

**registration_validation.py**
- Detect party defects (missing grantor/grantee)
- Validate legal descriptions
- Check instrument numbers and dates
- Assess type-specific requirements
- Determine overall registration validity

**marketability_assessment.py**
- Calculate marketability score (0-100)
- Assess buyer pool impact
- Evaluate financing availability
- Estimate liquidity
- Generate recommendations

**output_formatters.py**
- Generate markdown reports
- Create JSON outputs
- Format tables and sections
- Add timestamps and metadata

## Examples

### Example 1: Industrial Property with Easements

**Input:** Property with hydro transmission easement, restrictive covenant, and drainage easement

**Output:**
- Marketability: GOOD (72.5/100)
- Value Impact: 8.2% discount
- Critical Issues: None
- Registration Status: VALID

### Example 2: Property with Construction Lien

**Input:** Property with active construction lien for $45,000

**Output:**
- Marketability: POOR (49.5/100)
- Value Impact: 26.5% discount
- Critical Issues: 1 (construction lien)
- Registration Status: NEEDS_REVIEW
- Recommendation: Resolve lien before marketing

### Example 3: Complex Title with Multiple Issues

**Input:** Property with multiple easements, mortgage, lease, and defective registration

**Output:**
- Marketability: FAIR (58.0/100)
- Value Impact: 15.3% discount
- Critical Issues: 0
- High Issues: 2
- Registration Status: QUESTIONABLE
- Buyer Pool: 40% of typical market

## Testing

```bash
# Run with sample input
python title_analyzer.py samples/example_title_input.json

# Generate test outputs
python title_analyzer.py samples/example_title_input.json \
  --output samples/test_report.md \
  --json samples/test_results.json

# Verbose mode for debugging
python title_analyzer.py samples/example_title_input.json --verbose
```

## Version History

**Version 1.0.0** (November 17, 2025)
- Initial release
- Complete modular architecture
- Comprehensive marketability assessment
- Value impact calculation
- Registration validation
- Full markdown and JSON reporting

## License

Part of the lease-abstract project.

## Author

Claude Code - Infrastructure Acquisition Analysis Tools
