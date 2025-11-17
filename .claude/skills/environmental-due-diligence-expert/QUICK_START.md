# Environmental Risk Calculator - Quick Start Guide

## 1-Minute Overview

Analyze environmental contamination risk from Phase I/II ESA reports to get:
- Risk score (HIGH/MEDIUM/LOW)
- Cleanup costs ($0 - $1M+)
- Regulatory timeline (0-24 months)
- Liability recommendations (indemnity, holdback, insurance, pricing)

## Quick Start

```bash
# Run analysis
python environmental_risk_calculator.py samples/sample_industrial_contamination.json

# Output: Reports/YYYY-MM-DD_HHMMSS_environmental_risk_*.md
```

## Sample Scenarios

### HIGH Risk - Industrial Contamination
```bash
python environmental_risk_calculator.py samples/sample_industrial_contamination.json
```
- **Risk:** HIGH (75/100)
- **Cleanup:** $500K - $1.2M (brownfield remediation)
- **Timeline:** 8 months (Tier 1 RSC filing)
- **Recommendations:** Comprehensive indemnity, 200% holdback, pollution insurance

### MEDIUM Risk - Metal Fabrication
```bash
python environmental_risk_calculator.py samples/sample_medium_risk.json
```
- **Risk:** MEDIUM (45/100)
- **Cleanup:** $150K - $350K (localized remediation)
- **Timeline:** 8 months (Tier 1 RSC filing)
- **Recommendations:** Standard indemnity with cap, 150% holdback

### LOW Risk - Clean Office
```bash
python environmental_risk_calculator.py samples/sample_clean_site.json
```
- **Risk:** LOW (10/100)
- **Cleanup:** $0 - $5K (documentation only)
- **Timeline:** 0 months (no MOE filing)
- **Recommendations:** Standard reps/warranties, minimal holdback

## Input Template

Create `my_site.json`:

```json
{
  "site_address": "Your Property Address",
  "phase_1_esa": {
    "findings": ["Finding 1", "Finding 2"],
    "recs": [
      {"description": "REC description", "severity": "HIGH"}
    ],
    "data_gaps": []
  },
  "phase_2_esa": {
    "soil_samples": [],
    "groundwater_samples": [],
    "exceedances": [
      {
        "contaminant": "Contaminant name",
        "measured_value": 1000,
        "standard_limit": 100,
        "exceedance_factor": 10,
        "severity": "HIGH"
      }
    ],
    "contaminants": ["List", "of", "contaminants"]
  },
  "cleanup_scenarios": {
    "remediation": {
      "cost_low": 100000,
      "cost_high": 500000
    }
  }
}
```

Then run:
```bash
python environmental_risk_calculator.py my_site.json
```

## Key Options

```bash
# Custom output location
python environmental_risk_calculator.py input.json --output my_report.md

# JSON results (for integration)
python environmental_risk_calculator.py input.json --json-output results.json

# Custom discount rate (default 5.5%)
python environmental_risk_calculator.py input.json --discount-rate 0.06

# Verbose logging
python environmental_risk_calculator.py input.json --verbose
```

## Understanding the Output

### Risk Score (0-100)
- **70-100:** HIGH - Comprehensive indemnity, insurance required
- **40-69:** MEDIUM - Standard indemnity with cap, holdback recommended
- **0-39:** LOW - Standard reps/warranties sufficient

### Cleanup Scenarios
- **Risk Assessment:** $50K-$150K, 3 months (Phase II + assessment only)
- **Remediation:** $100K-$500K, 6-12 months (excavation, soil treatment)
- **Brownfield:** $200K-$1M+, 12-24 months (comprehensive remediation)

### Ontario Regulatory Pathways
- **Clean Site:** No filing, 0 months
- **Tier 1 RSC:** Risk assessment, 6-8 months, $35K-$80K
- **Tier 2 RSC:** Site-specific assessment, 12-16 months, $150K-$300K

### Liability Recommendations

**HIGH Risk:**
- Comprehensive vendor indemnity (indefinite)
- 200% holdback (3-phase release)
- Pollution liability insurance ($2M+ coverage, 10 years)
- Purchase price discount: NPV of cleanup to high estimate

**MEDIUM Risk:**
- Standard indemnity with cap (150% of high estimate, 5-7 years)
- 150% holdback (2-phase release)
- Consider pollution insurance (optional)
- Purchase price discount: NPV of cleanup

**LOW Risk:**
- Standard reps/warranties (2-3 years)
- Minimal holdback
- No insurance required
- Minimal price adjustment

## Common Use Cases

### Pre-Acquisition Due Diligence
1. Get Phase I/II ESA reports from environmental consultant
2. Extract findings into JSON format
3. Run calculator to quantify risk and costs
4. Use recommendations in purchase agreement negotiation

### Liability Negotiation
- Calculate appropriate holdback amount (150-200% of cleanup)
- Determine indemnity cap and duration
- Assess need for environmental insurance
- Justify purchase price discount

### Board Approval Memo
- Include risk score and cleanup cost range
- Attach regulatory timeline
- Reference liability recommendations
- Append full markdown report

### Insurance Underwriting
- Risk score guides premium
- Cleanup cost range determines coverage amount
- Regulatory complexity affects policy terms

## Troubleshooting

**Error: "Input validation failed"**
- Check JSON syntax (use jsonlint.com)
- Ensure all required fields present
- Verify numeric values for costs

**Error: "Discount rate appears to be percentage"**
- Use decimal format: 0.055 not 5.5
- Range: 0.01 to 0.25 (1% to 25%)

**No markdown report generated**
- Check Reports/ directory permissions
- Verify output path is writable
- Review verbose logs (--verbose flag)

## Next Steps

1. **Review README.md** - Complete documentation
2. **Examine samples/** - Three real-world scenarios
3. **Read module docs** - Understand methodology
4. **Customize scenarios** - Adjust cost ranges for your market

## Architecture Notes

**Modular Design:**
- `validators.py` - Input validation
- `environmental_assessment.py` - ESA parsing, risk scoring
- `cleanup_cost_estimation.py` - Cost estimation, NPV
- `regulatory_pathway.py` - MOE pathways, timelines
- `output_formatters.py` - Report generation

**Shared_Utils Integration:**
- `financial_utils`: NPV, present value
- `risk_utils`: Monte Carlo, sensitivity analysis
- `report_utils`: Timestamps, markdown tables

**Code Quality:**
- Type hints on all functions
- Google-style docstrings
- Comprehensive error handling
- DEBUG/INFO logging

## Support

See `README.md` for:
- Complete API documentation
- Detailed methodology
- Module function reference
- Input schema specification
- Best practices guide

---

**Version:** 1.0
**Created:** 2025-11-17
**Author:** Claude Code
