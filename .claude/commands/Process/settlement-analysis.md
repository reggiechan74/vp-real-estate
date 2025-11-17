---
description: Analyze settlement scenarios vs. hearing risk with probability-weighted outcomes and expected value comparison
argument-hint: <offer-counteroffer-json> [--output <report-path>]
allowed-tools: Read, Write, Bash
---

# Settlement Analysis

Analyze settlement scenarios vs. hearing risk with probability-weighted expected value comparison and BATNA/ZOPA analysis.

## Calculator Integration

**Python Calculator**: `.claude/skills/settlement-analysis-expert/settlement_analyzer.py`
**Input Schema**: `.claude/skills/settlement-analysis-expert/settlement_input_schema.json`
**Skills**: `settlement-analysis-expert`
**Related Skills**: `negotiation-expert-infrastructure`, `expropriation-compensation-entitlement-analysis`
**Related Agents**: Christi (legal risk assessment), Alexi (valuation range analysis), Katy/Shadi (project context)

## Purpose

Comprehensive settlement vs. hearing decision analysis. Calculate BATNA (Best Alternative to Negotiated Agreement), analyze ZOPA (Zone of Possible Agreement), compare settlement scenarios using probability-weighted expected value, assess owner holdout risk and litigation risk, perform sensitivity analysis, and generate clear recommendation (SETTLE, PROCEED TO HEARING, or NEGOTIATE FURTHER).

## Usage

```bash
/settlement-analysis <offer-counteroffer-json> [--output <report-path>]
```

**Arguments**: {{args}}

## Workflow

1. Read settlement offer and hearing analysis JSON file
2. Run `python .claude/skills/settlement-analysis-expert/settlement_analyzer.py {{arg0}}`
3. Calculate BATNA (expected hearing award + costs)
4. Analyze ZOPA (buyer max vs. seller min)
5. Compare settlement scenarios (offer, counteroffer, midpoint) using probability-weighted EV
6. Assess owner holdout risk (0-30 scale)
7. Assess litigation risk (probability, duration, costs)
8. Perform sensitivity analysis on key variables
9. Generate recommendation with confidence level
10. Create comprehensive settlement analysis report

## Example Commands

```bash
# Analyze settlement offer
/settlement-analysis offer_counteroffer.json

# Custom output path
/settlement-analysis samples/transmission_easement.json --output Reports/settlement.md
```

## Output

**Settlement Analysis Report Sections**:
1. Executive Summary (recommendation, rationale, financial impact, confidence)
2. Settlement Scenarios Comparison (offer vs. counteroffer vs. midpoint vs. hearing)
3. BATNA Analysis (expected award, total costs, net BATNA, variance/std dev)
4. ZOPA Analysis (zone identification, optimal range, negotiation leverage)
5. Probability-Weighted Expected Value (EV across all scenarios, best/worst case)
6. Owner Holdout Risk Assessment (0-30 scale, risk level, mitigation strategies)
7. Litigation Risk Assessment (probability, expected duration/costs)
8. Sensitivity Analysis (variable impact on total cost)
9. Recommendation (SETTLE/HEARING/NEGOTIATE with confidence level)
10. Action Items (prioritized next steps)

**Decision Framework**:
- **SETTLE (HIGH confidence)**: Net benefit > $50K, ZOPA exists, owner risk manageable
- **SETTLE (MEDIUM confidence)**: Net benefit $20K-$50K, marginal ZOPA
- **NEGOTIATE FURTHER**: Net benefit < $20K, scores in neutral range
- **PROCEED TO HEARING**: Settlement > BATNA, no ZOPA, high valuation gap

**Key Metrics**:
- Net BATNA (total expected cost of hearing)
- Settlement total cost (offer + legal fees to settle)
- Net benefit of settlement (savings vs. hearing)
- ZOPA bounds (lower/upper) and midpoint
- Holdout risk score and probability
- Litigation probability and expected duration
- Overall recommendation with confidence level (HIGH/MEDIUM/LOW)

## Related Commands

- `/negotiation-strategy` - Develop negotiation approach after analysis
- `/briefing-note` - Convert analysis to executive briefing
- `/expropriation-timeline` - Timeline implications of hearing vs. settlement
