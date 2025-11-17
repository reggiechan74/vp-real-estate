---
description: Develop negotiation approach and settlement range based on owner psychology and property characteristics
argument-hint: <owner-profile-json> [<property-data-json>]
allowed-tools: Read, Write, Bash
---

# Negotiation Strategy Planner

Develop comprehensive negotiation approach and settlement strategy based on owner psychology, property characteristics, and hearing alternatives.

## Calculator Integration

**Python Calculator**: `.claude/skills/negotiation-expert-infrastructure/negotiation_strategy_planner.py`
**Input Schema**: `.claude/skills/negotiation-expert-infrastructure/negotiation_strategy_input_schema.json`
**Skills**: `negotiation-expert-infrastructure`
**Related Skills**: `negotiation-expert`, `agricultural-easement-negotiation-frameworks`, `settlement-analysis-expert`
**Related Agents**: Shadi (farmer negotiations), Katy (transit station negotiations), Alexi (valuation guidance)

## Purpose

Analyze owner psychology to classify owner type (5 types), assess holdout risk (0-30 scale), calculate BATNA/ZOPA, determine optimal settlement range, recommend opening offer strategy, generate concession plan, and develop comprehensive 3-phase negotiation approach.

## Usage

```bash
/negotiation-strategy <owner-profile-json> [<property-data-json>]
```

**Arguments**: {{args}}

## Workflow

1. Read owner profile and property data JSON files
2. Run `python .claude/skills/negotiation-expert-infrastructure/negotiation_strategy_planner.py {{arg0}}`
3. Analyze owner psychology and classify owner type
4. Assess holdout risk from motivation, sophistication, alternatives
5. Calculate BATNA (hearing expected value) and ZOPA
6. Determine optimal settlement range and opening offer
7. Generate concession plan with diminishing concessions (50% → 25% → 12.5%)
8. Recommend communication strategy and negotiation techniques
9. Generate comprehensive negotiation strategy report

## Example Commands

```bash
# Analyze single input file
/negotiation-strategy owner_and_property.json

# Separate owner profile and property data
/negotiation-strategy owner_profile.json property_data.json

# Custom output
/negotiation-strategy samples/farmer_profile.json --output Reports/strategy.md
```

## Output

**Negotiation Strategy Report Sections**:
1. Owner Psychology Analysis (owner type classification, sophistication, motivations)
2. Holdout Risk Assessment (0-30 scale with risk level and probability)
3. BATNA Analysis (hearing expected value, costs, net BATNA)
4. ZOPA Analysis (zone of possible agreement, negotiation leverage)
5. Settlement Range Recommendation (opening, target, floor, ceiling, walkaway)
6. Opening Offer Strategy (risk-adjusted positioning with messaging)
7. Concession Plan (2-4 rounds, diminishing pattern, tactical notes)
8. Communication Strategy (tone, messaging, rapport tactics by owner type)
9. Leverage Analysis (buyer vs. owner advantages)
10. 3-Phase Negotiation Plan (Opening → Negotiation → Closure with techniques)

**Owner Types Identified**:
- RATIONAL_INVESTOR (maximize value, evidence-driven)
- LEGACY_HOLDER (emotional attachment, multi-generational)
- OPERATING_BUSINESS (business continuity critical)
- FINANCIAL_DISTRESS (need liquidity quickly)
- SOPHISTICATED_HOLDOUT (strategic, patient, well-advised)

## Related Commands

- `/settlement-analysis` - Detailed settlement vs. hearing decision analysis
- `/briefing-note` - Include strategy in executive briefing
- `/expropriation-timeline` - Timeline for negotiation phases
