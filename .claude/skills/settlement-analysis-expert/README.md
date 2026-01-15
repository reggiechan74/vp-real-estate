# Settlement Analysis Expert

Expert skill for settlement scenario analysis vs. expropriation hearing risk with probability-weighted outcomes.

## Quick Start

```bash
# Run analysis with sample data
python settlement_analyzer.py samples/sample_1_transmission_easement.json

# Generate report to file
python settlement_analyzer.py samples/sample_1_transmission_easement.json --output report.md

# JSON output for programmatic use
python settlement_analyzer.py samples/sample_1_transmission_easement.json --json
```

## What This Calculator Does

Analyzes settlement scenarios vs. proceeding to expropriation hearing by:

1. **Calculating BATNA** (Best Alternative to Negotiated Agreement)
   - Probability-weighted expected hearing award
   - Total hearing costs (legal + expert + time)
   - Uncertainty metrics (standard deviation, coefficient of variation)

2. **Evaluating Settlement Scenarios**
   - Current offer, counteroffer, midpoint scenarios
   - Probability-weighted comparison
   - Net benefit and savings analysis

3. **Determining ZOPA** (Zone of Possible Agreement)
   - Identifies overlap between buyer max and seller min
   - Calculates optimal settlement range (opening, target, walkaway)
   - Generates concession strategy

4. **Assessing Risks**
   - Owner holdout risk (0-30 scale)
   - Litigation probability
   - Expected hearing duration and costs

5. **Making Recommendations**
   - SETTLE / PROCEED TO HEARING / NEUTRAL
   - Confidence level (HIGH/MEDIUM/LOW)
   - Supporting rationale and financial analysis

## Directory Structure

```
settlement-analysis-expert/
├── settlement_analyzer.py          # Main calculator (thin orchestration)
├── settlement_input_schema.json    # JSON Schema Draft 2020-12
├── modules/                         # Modular components
│   ├── __init__.py
│   ├── validators.py                # Input validation
│   ├── calculations.py              # Settlement & hearing calculations
│   ├── analysis.py                  # Decision analysis & risk assessment
│   └── output_formatters.py         # Report generation
├── samples/                         # Sample inputs
│   └── sample_1_transmission_easement.json
├── SKILL.md                         # Complete skill documentation
└── README.md                        # This file
```

## Modular Architecture (Issue #21)

This calculator follows the modular design pattern:

- **Thin orchestration layer**: `settlement_analyzer.py` coordinates modules
- **Separate concerns**: Validation, calculations, analysis, formatting in separate modules
- **Shared utilities**: Leverages `negotiation_utils`, `risk_utils`, `financial_utils`, `report_utils`
- **Testable**: Each module can be tested independently

## Input Requirements

**Required**:
- `case_id`: Case identifier
- `settlement_offer`: Current settlement offer amount
- `hearing_probabilities`: {low_award, mid_award, high_award} must sum to 1.0
- `hearing_costs`: {low/mid/high_award_amount, legal_fees, expert_fees}

**Optional**:
- `counteroffer`: Owner's counteroffer (enables ZOPA analysis)
- `owner_profile`: Enables holdout risk assessment
- `case_factors`: Enables litigation risk assessment
- `settlement_costs`: {legal_fees_to_settle, settlement_risk}

See `settlement_input_schema.json` for full schema.

## Output

**Markdown Report** (default):
- Executive summary with recommendation
- Financial comparison (settlement vs. hearing)
- Hearing risk analysis with award range
- Settlement scenarios comparison
- ZOPA analysis (if counteroffer provided)
- Owner holdout risk assessment (if profile provided)
- Litigation risk assessment (if factors provided)

**JSON Output** (`--json` flag):
- Complete analysis results in structured JSON
- Suitable for programmatic use or further processing

## Sample Output

```
# Settlement Analysis Report

## Case HYDRO-2025-001

**Recommendation:** SETTLE
**Confidence Level:** HIGH
**Rationale:** Settlement saves $96,500 vs. hearing

## Financial Summary
- Settlement Total: $185,000
- Hearing Total: $281,500
- Net Benefit: $96,500 (34.3% savings)
```

## Shared Utilities Integration

**negotiation_utils.py**:
- `calculate_batna()`: Hearing expected value
- `calculate_zopa()`: Zone of possible agreement
- `optimal_settlement_range()`: Negotiation strategy
- `calculate_concession_strategy()`: Diminishing concessions

**risk_utils.py**:
- `assess_holdout_risk()`: Owner holdout scoring
- `litigation_risk_assessment()`: Litigation probability
- `sensitivity_analysis()`: Variable impact analysis

**financial_utils.py**:
- `npv()`: Net present value
- `safe_divide()`: Zero-safe division

**report_utils.py**:
- `generate_executive_summary()`: Decision summaries
- `format_markdown_table()`: Scenario tables
- `eastern_timestamp()`: Report timestamps

## Key Concepts

**BATNA**: Best Alternative to Negotiated Agreement (hearing outcome)
- Represents buyer's walkaway point
- Total expected cost if settlement fails

**ZOPA**: Zone of Possible Agreement
- Overlap between buyer max and seller min
- Settlement only possible if ZOPA exists

**Holdout Risk**: Probability owner refuses settlement
- Scored 0-30 based on motivation, sophistication, alternatives
- Higher score = higher probability of forcing hearing

**Expected Value**: Probability-weighted outcome
- Accounts for uncertainty in hearing awards
- Includes risk premium for uncertainty

## For More Information

See `SKILL.md` for complete documentation including:
- Detailed decision framework
- Recommendation thresholds
- Risk scoring methodology
- Negotiation best practices
- Integration with other skills
- Expert guidance on settlement vs. hearing decisions
