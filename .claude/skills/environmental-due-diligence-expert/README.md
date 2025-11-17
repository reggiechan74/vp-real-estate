# Environmental Risk Assessment Calculator

Comprehensive environmental contamination risk assessment tool for commercial real estate acquisitions. Analyzes Phase I/II Environmental Site Assessment (ESA) findings to score risk, estimate cleanup costs, determine regulatory pathways, and recommend liability allocation strategies.

## Overview

The Environmental Risk Assessment Calculator provides:

- **Contamination Risk Scoring** (0-100 scale, HIGH/MEDIUM/LOW)
- **Cleanup Cost Estimation** (risk assessment, remediation, brownfield scenarios)
- **Regulatory Pathway Analysis** (Ontario MOE requirements, timelines)
- **Liability Allocation Recommendations** (indemnities, holdbacks, insurance, price adjustments)
- **NPV Analysis** of environmental costs
- **Timestamped Markdown Reports** (Reports/ directory)

## Architecture

The calculator uses a **modular architecture** following best practices:

```
environmental-due-diligence-expert/
├── environmental_risk_calculator.py    # Main orchestration (thin layer)
├── modules/
│   ├── __init__.py                     # Module exports
│   ├── validators.py                   # Input validation
│   ├── environmental_assessment.py     # Phase I/II ESA parsing, risk scoring
│   ├── cleanup_cost_estimation.py      # Cost estimation, NPV calculation
│   ├── regulatory_pathway.py           # MOE pathways, timelines, requirements
│   └── output_formatters.py            # Report formatting
├── samples/                            # Sample input files
├── tests/                              # Unit tests
└── README.md                           # This file
```

**Imports from Shared_Utils:**
- `financial_utils`: `npv()`, `present_value()`
- `risk_utils`: `monte_carlo_simulation()`, `sensitivity_analysis()`
- `report_utils`: `eastern_timestamp()`, `format_markdown_table()`, `generate_executive_summary()`

## Usage

### Command Line

```bash
python environmental_risk_calculator.py <input_json_path> [options]

Options:
  --output PATH           Output path for markdown report (default: Reports/TIMESTAMP_environmental_risk_*.md)
  --json-output PATH      Output path for JSON results
  --discount-rate RATE    Discount rate for NPV (default: 0.055 = 5.5%)
  --verbose               Enable verbose logging
```

### Examples

```bash
# Basic usage
python environmental_risk_calculator.py samples/sample_industrial_contamination.json

# With custom output
python environmental_risk_calculator.py samples/sample_industrial_contamination.json \
  --output my_report.md \
  --json-output results.json

# With custom discount rate
python environmental_risk_calculator.py samples/sample_industrial_contamination.json \
  --discount-rate 0.06
```

## Input Format

### JSON Structure

```json
{
  "site_address": "123 Industrial Ave",
  "phase_1_esa": {
    "findings": ["AST present", "Historical dry cleaner"],
    "recs": [
      {
        "description": "Soil staining near AST - potential petroleum release",
        "severity": "HIGH",
        "location": "Northwest corner"
      }
    ],
    "data_gaps": ["No groundwater monitoring wells"]
  },
  "phase_2_esa": {
    "soil_samples": [
      {
        "sample_id": "SS-01",
        "location": "AST area",
        "depth_m": 1.5,
        "contaminants": ["F2 Petroleum Hydrocarbons"],
        "exceedance": true
      }
    ],
    "groundwater_samples": [
      {
        "sample_id": "GW-01",
        "location": "Downgradient",
        "depth_m": 4.5,
        "contaminants": ["PCE"],
        "exceedance": true
      }
    ],
    "exceedances": [
      {
        "contaminant": "F2 Petroleum Hydrocarbons",
        "location": "AST area soil",
        "measured_value": 3500,
        "standard_limit": 150,
        "exceedance_factor": 23.3,
        "description": "Petroleum hydrocarbons exceed Table 3 standards by 23x",
        "severity": "HIGH"
      }
    ],
    "contaminants": ["Petroleum hydrocarbons", "VOCs", "PCE"]
  },
  "cleanup_scenarios": {
    "risk_assessment": {
      "cost_low": 50000,
      "cost_high": 150000,
      "description": "Phase II ESA + Risk Assessment only"
    },
    "remediation": {
      "cost_low": 200000,
      "cost_high": 500000,
      "description": "Active remediation (excavation, soil treatment)"
    },
    "brownfield": {
      "cost_low": 500000,
      "cost_high": 1000000,
      "description": "Brownfield redevelopment (extensive remediation)"
    }
  }
}
```

### Field Descriptions

**phase_1_esa:**
- `findings`: General observations from Phase I ESA
- `recs`: Recognized Environmental Conditions (RECs) requiring follow-up
- `data_gaps`: Information gaps requiring further investigation

**phase_2_esa:**
- `soil_samples`: Soil sample results
- `groundwater_samples`: Groundwater sample results
- `exceedances`: Contaminants exceeding regulatory standards
- `contaminants`: List of detected contaminants

**cleanup_scenarios:**
- Cost ranges for different remediation approaches
- Used to calculate most likely costs and NPV

## Risk Scoring Methodology

**Total Score:** 0-100 (weighted components)

### 1. Contamination Severity (0-30 points)
- Exceedances count
- Contaminant types (VOCs, heavy metals = high risk)
- Severity assessment from Phase II

### 2. Regulatory Complexity (0-25 points)
- Clean Site: 0 points
- Tier 1 Risk Assessment: 10-15 points
- Tier 2 Site-Specific: 15-20 points
- Groundwater contamination: +5 points

### 3. Remediation Feasibility (0-25 points)
- Groundwater contamination: +10 points (harder to remediate)
- Multiple contaminant types: +5-8 points
- High exceedance factors: +7 points

### 4. Financial Impact (0-20 points)
- $100K-$200K: 5 points
- $200K-$500K: 10 points
- $500K-$1M: 15 points
- $1M+: 20 points

### Risk Levels
- **HIGH:** 70-100 points
- **MEDIUM:** 40-69 points
- **LOW:** 0-39 points

## Cleanup Cost Scenarios

### Risk Assessment Only
- **Cost:** $50K - $150K
- **Timeline:** 2-3 months
- **Suitable For:** Minor contamination, low risk levels
- **Approach:** Phase II ESA + Risk Assessment, no active remediation

### Remediation
- **Cost:** $100K - $500K
- **Timeline:** 6-12 months
- **Suitable For:** Moderate contamination, localized impacts
- **Approach:** Excavation, soil treatment, groundwater monitoring

### Brownfield Redevelopment
- **Cost:** $200K - $1M+
- **Timeline:** 12-24 months
- **Suitable For:** Severe contamination, regulatory complexity
- **Approach:** Comprehensive remediation, ongoing groundwater treatment, Risk Management Measures

## Regulatory Pathways (Ontario)

### Clean Site
- **Filing Required:** No
- **Timeline:** 0 months
- **Requirements:** Maintain ESA reports, update environmental records

### Tier 1 Risk Assessment
- **Filing Required:** Yes (Record of Site Condition)
- **Timeline:** 6 months (8 months with contingency)
- **Requirements:**
  - Retain Qualified Person (QP)
  - File RSC with MOE
  - Conduct Tier 1 risk assessment
  - Obtain Certificate of Property Use
- **Cost:** $35K - $80K

### Tier 2 Site-Specific Risk Assessment
- **Filing Required:** Yes
- **Timeline:** 12 months (16 months with contingency)
- **Requirements:**
  - Retain QP
  - Site-specific risk assessment
  - Remedial action plan (if needed)
  - Risk management measures implementation
  - File RSC with MOE
  - Obtain Certificate of Property Use
- **Cost:** $150K - $300K (regulatory only, excluding cleanup)

## Liability Allocation Recommendations

### Vendor Environmental Indemnity

**HIGH Risk:**
- Comprehensive indemnity required
- Scope: All pre-existing conditions, cost overruns, third-party claims, fines
- Duration: Indefinite (no sunset clause)

**MEDIUM Risk:**
- Standard indemnity with cap
- Cap: 150% of high cleanup estimate
- Duration: 5-7 years post-closing

**LOW Risk:**
- Standard environmental reps and warranties
- Duration: 2-3 years post-closing

### Purchase Price Holdback

**HIGH Risk:**
- Holdback: 200% of estimated cleanup costs
- Release: 3 phases (50% @ Certificate, 30% @ 12mo, 20% @ 24mo)

**MEDIUM Risk:**
- Holdback: 150% of estimated cleanup costs
- Release: 2 phases (60% @ completion, 40% @ 12mo)

**LOW Risk:**
- Minimal or no holdback

### Environmental Insurance

**HIGH Risk:**
- **Required:** Pollution Legal Liability (PLL) Insurance
- **Coverage:** 2x high cleanup estimate
- **Term:** 10 years
- **Premium:** $25K - $75K annually

**MEDIUM Risk:**
- **Recommended:** PLL Insurance (optional)
- **Coverage:** 1.5x high estimate
- **Term:** 5-7 years
- **Premium:** $15K - $35K annually

**LOW Risk:**
- Not required (standard property insurance sufficient)

### Purchase Price Adjustment

**HIGH/MEDIUM Risk:**
- **Discount:** NPV of cleanup costs to high estimate
- **Alternative (As-Is Sale):** 130% of high estimate

**LOW Risk:**
- Minimal adjustment (reflect Phase II costs only)

## Output

### Markdown Report
- Executive summary
- ESA findings summary
- Risk assessment with score breakdown
- Cleanup cost analysis (with NPV)
- Regulatory pathway and timeline
- Liability allocation recommendations
- Generated in `Reports/YYYY-MM-DD_HHMMSS_environmental_risk_*.md`

### JSON Results (optional)
- Complete analysis results in structured JSON format
- Suitable for integration with other systems

## Sample Files

### sample_industrial_contamination.json
**Profile:** Industrial property with AST and historical dry cleaner
- **Risk Level:** HIGH (75/100)
- **Exceedances:** 4 (petroleum, PCE, TCE, groundwater PCE)
- **Cleanup Cost:** $500K - $1.2M (brownfield scenario)
- **Regulatory:** Tier 1 Risk Assessment, 8 months
- **Total Cost:** $897,500 (cleanup + regulatory)

### sample_clean_site.json
**Profile:** Office building with clean Phase II results
- **Risk Level:** LOW (10/100)
- **Exceedances:** 0
- **Cleanup Cost:** $0 - $5K (documentation only)
- **Regulatory:** Clean Site, no filing required
- **Total Cost:** $2,500

## Testing

Run tests:
```bash
# Test with HIGH risk site
python environmental_risk_calculator.py samples/sample_industrial_contamination.json --verbose

# Test with LOW risk site
python environmental_risk_calculator.py samples/sample_clean_site.json --verbose
```

Expected outputs:
- Exit code 0 on success
- Markdown report in Reports/
- Console summary with key metrics

## Module Documentation

### validators.py
- `validate_input_data()`: Complete input validation
- `validate_phase_esa_data()`: Phase I/II ESA structure validation
- `validate_cleanup_scenarios()`: Cost range validation
- `validate_discount_rate()`: Discount rate bounds checking

### environmental_assessment.py
- `parse_phase_i_findings()`: Extract Phase I findings, RECs, data gaps
- `parse_phase_ii_results()`: Extract Phase II samples, exceedances, contaminants
- `identify_recognized_environmental_conditions()`: Compile all RECs
- `score_contamination_risk()`: Calculate 0-100 risk score with breakdown

### cleanup_cost_estimation.py
- `estimate_cleanup_costs()`: Cost ranges for all scenarios
- `calculate_npv_cleanup_costs()`: NPV calculation with timing options
- `estimate_cost_by_scenario()`: Scenario-specific cost estimation

### regulatory_pathway.py
- `determine_regulatory_pathway()`: MOE pathway selection
- `estimate_regulatory_timeline()`: Timeline with phases and contingency
- `generate_approval_requirements()`: Deliverables, costs, timing
- `calculate_total_regulatory_costs()`: Aggregate regulatory costs

### output_formatters.py
- `format_risk_summary()`: Risk score markdown section
- `format_cleanup_cost_report()`: Cost analysis with NPV
- `format_regulatory_timeline()`: Pathway, timeline, requirements
- `format_liability_recommendations()`: Indemnity, holdback, insurance, pricing
- `generate_markdown_report()`: Complete report assembly

## Dependencies

**Standard Library:**
- `json`, `sys`, `os`, `argparse`, `logging`, `typing`

**Shared_Utils:**
- `financial_utils`: NPV, present value calculations
- `risk_utils`: Monte Carlo simulation, sensitivity analysis
- `report_utils`: Timestamps, markdown formatting, executive summaries

**External:**
- `pytz`: Eastern Time timezone support

## Code Quality

- **Type Hints:** All functions have complete type annotations
- **Docstrings:** Google-style docstrings for all public functions
- **Error Handling:** Comprehensive validation with informative error messages
- **Logging:** DEBUG and INFO level logging throughout
- **Modularity:** Thin orchestration layer, logic in focused modules

## Best Practices

1. **Always validate input data** before running analysis
2. **Use appropriate discount rates** (5-7% typical for environmental costs)
3. **Include contingency** in timeline estimates (MOE processes can vary)
4. **Document assumptions** in liability allocation recommendations
5. **Consider insurance** for HIGH risk properties (not just indemnities)
6. **NPV timing matters** - upfront vs. distributed costs materially impact valuation

## Limitations

- Ontario-specific regulatory framework (MOE pathways)
- Generic cost ranges (site-specific quotes recommended)
- No integration with actual MOE filings
- Assumes commercial/industrial property use
- Does not model brownfield tax incentives

## Future Enhancements

- [ ] Integration with MOE Environmental Site Registry API
- [ ] Monte Carlo simulation for cost uncertainty
- [ ] Sensitivity analysis for key variables
- [ ] Multi-jurisdiction support (other provinces)
- [ ] Brownfield tax incentive calculator
- [ ] Historical contamination database integration
- [ ] PDF report generation (in addition to markdown)

## Version History

**v1.0 (2025-11-17)**
- Initial release
- Modular architecture with 5 modules
- Support for Phase I/II ESA analysis
- Risk scoring (0-100 scale)
- Cleanup cost estimation (3 scenarios)
- Ontario MOE regulatory pathways
- Liability allocation recommendations
- NPV analysis
- Markdown report generation

## Author

Claude Code
Created: 2025-11-17

## License

Proprietary - Part of lease-abstract toolkit
