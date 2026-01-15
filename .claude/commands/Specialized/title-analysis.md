---
description: Title search analysis identifying encumbrances, easements, restrictions, liens, registration defects, and marketability issues
argument-hint: <title-search-json> [--output <report-path>]
allowed-tools: Read, Write, Bash
---

# Title Analysis

Comprehensive title search analysis identifying registered instruments, encumbrances, registration defects, and marketability impacts for property acquisitions.

## Usage

```bash
# Basic usage with JSON input
/title-analysis path/to/title_search.json

# With custom output path
/title-analysis path/to/title_search.json --output Reports/2025-11-17_title_analysis.md
```

## Input Structure

The input JSON should follow the `title_input_schema.json` specification:

```json
{
  "property_identifier": "PIN 12345-6789",
  "property_address": "100 Industrial Road, Toronto, ON",
  "registered_instruments": [
    {
      "instrument_number": "AB123456",
      "instrument_type": "Easement",
      "parties": {
        "grantor": "John Smith",
        "grantee": "Hydro One Networks Inc."
      },
      "description": "Hydro transmission easement 20m wide",
      "registration_date": "1985-03-15",
      "area_affected": "2.5 acres"
    },
    {
      "instrument_number": "CD789012",
      "instrument_type": "Covenant",
      "parties": {
        "grantor": "Original Developer",
        "grantee": "Municipality"
      },
      "description": "Restriction to industrial use only",
      "registration_date": "1975-06-20"
    }
  ],
  "restrictions": [
    {
      "type": "Zoning",
      "description": "M2 - General Industrial",
      "impact": "Restricts to industrial uses"
    }
  ],
  "encumbrances": [],
  "defects": []
}
```

## Workflow

This command executes the following workflow:

1. **Validate Input**: Validates JSON against schema
2. **Parse Instruments**: Parses all 14+ registered instrument types
3. **Analyze Encumbrances**: Assesses impact severity (CRITICAL/HIGH/MEDIUM/LOW)
4. **Detect Registration Defects**: Identifies missing parties, improper descriptions, signature defects
5. **Assess Marketability**: Calculates 0-100 marketability score across 4 dimensions
6. **Calculate Value Impact**: Estimates percentage discount ranges
7. **Recommend Remedial Actions**: Priority-ranked discharge/postponement/rectification actions
8. **Generate Report**: Timestamped markdown report with encumbrance matrix

## Output

The command generates:

- **Encumbrance Summary Table**: Type, priority, impact, remedial action
- **Critical Issues**: Requiring immediate resolution before closing
- **Marketability Assessment**: EXCELLENT/GOOD/FAIR/POOR/UNMARKETABLE (0-100 score)
- **Recommended Actions**: Priority-ranked discharge, postponement, rectification steps
- **Valuation Impact Estimate**: Percentage discount range (min/likely/max)
- **Timestamped Report**: `Reports/YYYY-MM-DD_HHMMSS_title_analysis_{pin}.md`

## Related Skills

- **title-expert**: Auto-loaded for title analysis
- **easement-valuation-methods**: For valuation impact quantification
- **right-of-way-expert**: For ROW corridor analysis

## Calculators

Uses:
- `.claude/skills/title-expert/title_analyzer.py`
- `.claude/skills/title-expert/encumbrance_discount_calculator.py` (for discount calculation)
