---
description: Phase I/II ESA summary with contamination risk, cleanup costs, regulatory pathway, and liability assessment
argument-hint: <site-data-json> [--output <report-path>]
allowed-tools: Read, Write, Bash
---

# Environmental Due Diligence

Generate comprehensive environmental risk assessment for property acquisitions including Phase I/II ESA interpretation, contamination risk scoring, cleanup cost estimation, regulatory pathway analysis, and liability allocation recommendations.

## Usage

```bash
# Basic usage with JSON input
/environmental-due-diligence path/to/site_data.json

# With custom output path
/environmental-due-diligence path/to/site_data.json --output Reports/2025-11-17_environmental_analysis.md
```

## Input Structure

The input JSON should follow the `environmental_input_schema.json` specification:

```json
{
  "site_address": "123 Industrial Ave",
  "phase_1_esa": {
    "findings": ["AST present", "Historical dry cleaner use"],
    "recs": [
      {
        "description": "Underground storage tank",
        "severity": "HIGH",
        "location": "Northeast corner"
      }
    ],
    "data_gaps": ["Historical chain of title incomplete"]
  },
  "phase_2_esa": {
    "soil_samples": [
      {
        "sample_id": "SS-01",
        "location": "Former UST area",
        "depth_m": 2.5,
        "contaminants": ["Petroleum hydrocarbons"],
        "exceedance": true
      }
    ],
    "groundwater_samples": [],
    "exceedances": [
      {
        "contaminant": "Petroleum F2",
        "location": "SS-01",
        "measured_value": 850,
        "standard_limit": 260,
        "exceedance_factor": 3.27,
        "description": "Tier 1 Table 3 exceedance",
        "severity": "HIGH"
      }
    ],
    "contaminants": ["Petroleum hydrocarbons", "VOCs"]
  },
  "cleanup_scenarios": {
    "risk_assessment": {
      "cost_low": 50000,
      "cost_high": 150000,
      "description": "Risk assessment only"
    },
    "remediation": {
      "cost_low": 200000,
      "cost_high": 500000,
      "description": "Full excavation and disposal"
    },
    "brownfield": {
      "cost_low": 500000,
      "cost_high": 1000000,
      "description": "Comprehensive brownfield redevelopment"
    }
  }
}
```

## Workflow

This command executes the following workflow:

1. **Validate Input**: Validates JSON against schema
2. **Load ESA Data**: Parses Phase I and Phase II ESA findings
3. **Score Contamination Risk**: Calculates risk score (0-100) based on:
   - Contamination severity (30%)
   - Regulatory complexity (25%)
   - Remediation feasibility (25%)
   - Financial impact (20%)
4. **Estimate Cleanup Costs**: Analyzes cost scenarios with NPV calculations
5. **Determine Regulatory Pathway**: Maps MOE approval pathway and timeline
6. **Recommend Liability Allocation**: Structures vendor indemnity, holdback, insurance
7. **Calculate Price Adjustment**: NPV-based acquisition price discount
8. **Generate Report**: Timestamped markdown report in Reports/

## Output

The command generates:

- **Contamination Risk Summary**: HIGH/MEDIUM/LOW with score breakdown
- **Cleanup Cost Analysis**: Range estimates with NPV for each scenario
- **Regulatory Pathway**: MOE approval process and timeline (0-24 months)
- **Liability Allocation**: Vendor indemnity, holdback %, insurance recommendations
- **Acquisition Price Adjustment**: Recommended discount based on cleanup NPV
- **Timestamped Report**: `Reports/YYYY-MM-DD_HHMMSS_environmental_risk_{site}.md`

## Related Skills

- **environmental-due-diligence-expert**: Auto-loaded for environmental analysis
- **settlement-analysis-expert**: For valuation disputes
- **expropriation-compensation-entitlement-analysis**: For government acquisitions

## Calculator

Uses: `.claude/skills/environmental-due-diligence-expert/environmental_risk_calculator.py`
