# Briefing Note Expert

Executive briefing note generator for infrastructure acquisition projects.

## Overview

Generates concise (1-2 page) executive briefing notes that synthesize complex acquisition decisions into clear recommendations for board approval or executive authorization.

**Key Features:**
- Decision-focused structure (Issue → Background → Analysis → Recommendation → Risk → Actions)
- Automated financial analysis with budget variance tracking
- Strategic alignment scoring and alternatives comparison
- Risk assessment with overall risk scoring
- Action items with priority and accountability
- Executive-ready markdown output

## Quick Start

```bash
# Generate briefing note from sample
python briefing_note_generator.py samples/sample_1_transit_station_acquisition.json

# Specify output location
python briefing_note_generator.py input.json --output Reports/my_briefing.md

# Verbose mode (detailed analysis)
python briefing_note_generator.py input.json --verbose
```

## Input Requirements

**Minimum required fields:**
- `project_name`: Project identifier
- `issue`: Decision required
- `background`: Context and timeline
- `financial_summary`: Total cost and breakdown
- `recommendation`: Primary recommendation

**Optional fields:**
- `urgency`: low/medium/high (default: medium)
- `analysis`: Strategic rationale, alternatives, benefits, precedents
- `risks`: Risk assessment with severity and mitigation
- `action_items`: Next steps with owners and deadlines
- `approvals_required`: Authorization requirements
- `metadata`: Prepared by, department, date, classification

See `briefing_note_input_schema.json` for complete schema.

## File Structure

```
briefing-note-expert/
├── briefing_note_generator.py          # Main generator script
├── briefing_note_input_schema.json     # JSON schema validation
├── modules/
│   ├── validators.py                   # Input validation
│   ├── analysis.py                     # Decision analysis
│   └── output_formatters.py            # Markdown formatting
├── samples/
│   └── sample_1_transit_station_acquisition.json
├── SKILL.md                            # Complete documentation
└── README.md                           # This file
```

## Module Descriptions

### validators.py

**Purpose:** Input validation and consistency checks

**Functions:**
- `validate_briefing_note_input()`: Schema and required field validation
- `validate_financial_consistency()`: Cost breakdown and variance checks
- `validate_timeline_logic()`: Date sequencing and milestone ordering
- `validate_risk_assessment()`: Risk completeness and mitigation checks

**Validation Levels:**
- **Errors**: Block generation (missing required fields, invalid data types)
- **Warnings**: Flag issues but allow generation (inconsistent percentages, missing mitigations)

### analysis.py

**Purpose:** Decision analysis and scoring

**Functions:**
- `analyze_decision_urgency()`: Urgency scoring (0-100) based on timeline and constraints
- `analyze_alternatives()`: Cost comparison and key differentiators
- `analyze_strategic_alignment()`: Strategic score (0-100) from benefits and precedents
- `calculate_overall_risk_score()`: Weighted risk scoring with severity distribution
- `generate_executive_recommendation()`: Synthesized recommendation text

**Scoring Framework:**

**Urgency Score (0-100):**
- Base: 30 (low), 60 (medium), 90 (high)
- +10 for critical deadline
- +5 for multiple pending milestones

**Strategic Score (0-100):**
- Base: 50
- +15 for strategic rationale (>50 chars)
- +20 for 3+ benefits, +10 for 1-2 benefits
- +15 for 2+ precedents, +10 for 1 precedent

**Overall Risk Score (0-100):**
- Weighted by severity: Critical (100), High (70), Medium (40), Low (15)
- Multiplied by probability (0-1)
- Averaged across all risks

### output_formatters.py

**Purpose:** Markdown generation and formatting

**Functions:**
- `format_issue_section()`: Issue with urgency indicator (🔴/🟡/🟢)
- `format_background_section()`: Context, timeline tables, stakeholder tables
- `format_analysis_section()`: Financial summary, budget comparison, alternatives
- `format_recommendation_section()`: Recommendation with strategic context
- `format_risk_section()`: Risks grouped by severity (Critical → High → Medium → Low)
- `format_action_items_section()`: Actions grouped by priority
- `format_approvals_section()`: Authorization requirements table
- `generate_briefing_note()`: Complete markdown document

**Formatting Standards:**
- Tables for timelines, stakeholders, cost comparisons, approvals
- Icons for status (✅/🔄/⏳) and position (✅/➖/❌)
- Currency formatting with 2 decimals
- Percentage breakdowns for cost categories
- Color coding for urgency (🔴 HIGH, 🟡 MEDIUM, 🟢 LOW)

## Output Format

**File Naming:** `YYYY-MM-DD_HHMMSS_briefing_note_[project_name].md`

**Location:** `Reports/` directory with timestamp prefix

**Document Structure:**
1. Document Header (title, subtitle, metadata)
2. Issue / Decision Required (with urgency indicator)
3. Background and Context (narrative + tables)
4. Analysis (financial + strategic + alternatives)
5. Recommendation (with rationale and context)
6. Risk Assessment (grouped by severity)
7. Approvals Required (if applicable)
8. Action Items (grouped by priority)
9. Distribution List (if provided)

**Typical Length:** 1-2 pages (aim for under 1,500 words)

## Shared Utilities Integration

**From `Shared_Utils/report_utils.py`:**
- `generate_document_header()`: Standard header formatting
- `format_financial_summary()`: Financial data with percentages
- `format_risk_assessment()`: Risk grouping and formatting
- `generate_action_items()`: Action items with priority grouping
- `format_markdown_table()`: Table generation with alignment
- `eastern_timestamp()`: Timestamp prefix for file naming

**From `Shared_Utils/risk_utils.py`:**
- `assess_holdout_risk()`: Property assembly holdout risk (optional)
- `litigation_risk_assessment()`: Expropriation litigation risk (optional)

## Validation Examples

**Schema Validation:**
```
✅ Schema validation passed
```

**Financial Consistency:**
```
⚠️  FINANCIAL WARNINGS:
   - Breakdown total ($1,820,000) does not match total_cost ($1,850,000)
```

**Timeline Logic:**
```
❌ TIMELINE ERRORS:
   - Start date must be before critical deadline
   - Milestone 3 (Board approval) is dated before previous milestone
```

**Risk Assessment:**
```
⚠️  RISK ASSESSMENT WARNINGS:
   - Risk 2 (Environmental contamination) is HIGH but has no mitigation strategy
   - All risks have same severity (MEDIUM) - consider more granular assessment
```

## Sample Output Preview

```markdown
# EXECUTIVE BRIEFING NOTE

## Transit Station Site Acquisition - Yonge & Eglinton

**Date:** 2025-11-17
**Prepared By:** Sarah Chen, Senior Acquisitions Officer
**Classification:** CONFIDENTIAL

## Issue / Decision Required

Board approval required for $1,850,000 property acquisition to secure transit station site

**Urgency:** 🔴 HIGH - Critical deadline January 31, 2026

## Background and Context

The Yonge-Eglinton Crosstown LRT project requires acquisition of 2550 Yonge Street...

### Project Timeline

| Milestone | Date | Status |
|:----------|:----:|:------:|
| Initial site identification | 2025-01-15 | ✅ Completed |
| Board approval deadline | 2025-11-30 | ⏳ Pending |
...
```

## Best Practices

**For Inputs:**
- Use sample JSON as template
- Ensure cost breakdown sums to total
- Include 2-3 meaningful alternatives
- Assign mitigation to High/Critical risks
- Keep action items to 5-8 maximum
- Verify dates are sequential

**For Outputs:**
- Review for 1-2 page length
- Verify all-in costs for alternatives (not just acquisition)
- Check budget variance is addressed
- Ensure risks have mitigation strategies
- Confirm action items have owners and deadlines

**Common Pitfalls:**
- ❌ Too much detail (10+ page report)
- ❌ Vague recommendations ("Consider acquisition")
- ❌ Hiding budget variance or bad news
- ❌ Alternatives without all-in costs
- ❌ Risks without mitigation strategies
- ❌ Action items without owners

## Integration with Other Skills

**Complementary skills:**
- `land-assembly-expert`: Property assembly strategy
- `settlement-analysis-expert`: Negotiation vs. expropriation
- `transit-station-site-acquisition-strategy`: Site selection
- `expropriation-timeline-expert`: Expropriation timelines

**Workflow:**
1. Use site selection skills to evaluate alternatives
2. Use settlement analysis for negotiation strategy
3. Use briefing-note-expert to synthesize for executive approval
4. Use land assembly for implementation planning

## Testing

```bash
# Test with sample input
python briefing_note_generator.py samples/sample_1_transit_station_acquisition.json --verbose

# Expected output
✅ SUCCESS!
Briefing note generated: Reports/2025-11-16_191541_briefing_note_transit_station_site_acquisition.md
File size: 8,961 bytes
```

## Schema Compliance

All inputs validated against JSON Schema Draft-07:
- Required fields enforcement
- Data type validation (string, number, date, enum)
- Range constraints (probabilities 0-1, percentages 0-1)
- Date format validation (YYYY-MM-DD)
- Enum validation (urgency, severity, priority, position)

See `briefing_note_input_schema.json` for complete specification.

## Related Documentation

- **SKILL.md**: Complete methodology and best practices
- **briefing_note_input_schema.json**: JSON schema specification
- **samples/**: Example inputs for reference

## Version History

- **v1.0** (2025-11-17): Initial implementation
  - Core briefing note structure
  - Financial and strategic analysis
  - Risk scoring and assessment
  - Action items with priority grouping
  - Markdown output with tables and icons
