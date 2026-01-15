# Negotiation Expert Infrastructure

Specialized calculators for infrastructure acquisition negotiations including settlement analysis and strategy planning.

## Overview

This toolkit provides two complementary calculators:

1. **Negotiation Settlement Calculator** (`negotiation_settlement_calculator.py`)
   - Quantifies settlement economics (BATNA, ZOPA, expected value)
   - Calculates hearing costs and settlement trade-offs
   - Performs risk-adjusted NPV analysis

2. **Negotiation Strategy Planner** (`negotiation_strategy_planner.py`) **[NEW]**
   - Analyzes owner psychology and motivations
   - Develops negotiation approach and tactics
   - Recommends opening offers and concession strategies
   - Identifies leverage points

## Features

### Negotiation Strategy Planner

**Purpose**: Develop comprehensive negotiation strategy based on owner psychology, property characteristics, and settlement economics.

**Key Capabilities**:
- Owner psychology profiling (5 owner types)
- Holdout risk assessment (0-30 scale)
- BATNA/ZOPA calculation
- Opening offer recommendation
- Concession strategy (diminishing concessions pattern)
- Leverage analysis
- Communication strategy tailored to owner type
- 3-phase negotiation plan

**Owner Types Identified**:
1. `RATIONAL_INVESTOR` - Business decision, data-driven
2. `LEGACY_HOLDER` - Multi-generational, emotional attachment
3. `OPERATING_BUSINESS` - Property critical to operations
4. `FINANCIAL_DISTRESS` - Motivated seller, cash constraints
5. `SOPHISTICATED_HOLDOUT` - Experienced, strategic negotiator

**Output**:
- Owner analysis and communication strategy
- Holdout risk score (0-30) with probability
- BATNA and ZOPA ranges
- Settlement range (opening → target → walkaway)
- Concession plan (4-5 rounds with tactical notes)
- Leverage points (buyer vs owner advantages)
- 3-phase negotiation plan
- Recommended tactics and messaging

## Usage

### Negotiation Strategy Planner

```bash
# Basic usage
python negotiation_strategy_planner.py samples/sample_2_urban_station.json

# With verbose output
python negotiation_strategy_planner.py samples/sample_2_urban_station.json --verbose

# Save to file
python negotiation_strategy_planner.py samples/sample_2_urban_station.json \
    --output strategy_report.json --verbose
```

**Example Output (Verbose)**:

```
================================================================================
NEGOTIATION STRATEGY PLANNER
================================================================================

STEP 2: OWNER PSYCHOLOGY ANALYSIS
Owner Type: SOPHISTICATED_HOLDOUT
Sophistication: HIGH
Primary Motivation: Maximize value through process knowledge
Communication Approach: evidence_based_professional

STEP 3: HOLDOUT RISK ASSESSMENT
Risk Score: 24/30
Risk Level: CRITICAL
Holdout Probability: 70.0%

STEP 7: OPENING OFFER STRATEGY
Recommended Opening: $4,104,000.00
Rationale: 5% below target - very high holdout risk

STEP 8: CONCESSION STRATEGY
Round 1: $4,104,000.00 (+$0.00) - Opening offer
Round 2: $4,212,000.00 (+$108,000.00) - 50% of remaining gap
Round 3: $4,239,000.00 (+$27,000.00) - 25% of remaining gap
Round 4: $4,249,125.00 (+$10,125.00) - 12% of remaining gap
Round 5: $4,320,000.00 (+$70,875.00) - Final offer

STEP 9: LEVERAGE POINTS
Buyer Advantages: (none - tough negotiation!)

Owner Advantages:
  - Buyer has timeline pressure while owner can wait
  - Sophisticated owner with process knowledge
  - Rising market favors waiting
  - High political visibility limits tactics

STEP 10: NEGOTIATION STRATEGY
Approach: COLLABORATIVE_PROBLEM_SOLVING
Communication: evidence_based_professional
Timeline: Aggressive with defined milestones
```

## Input Schema

### Negotiation Strategy Planner Input

Required sections:
1. `property_info` - Property identification and characteristics
2. `valuation` - Market value, seller minimum, appraisal range
3. `owner_profile` - Psychology, motivation, sophistication, alternatives
4. `hearing_analysis` - BATNA probabilities and costs

Optional sections:
- `project_context` - Timeline, budget, political sensitivity
- `market_conditions` - Trends, comparables

**Key Owner Profile Fields**:

```json
{
  "owner_profile": {
    "motivation": {
      "financial_need": "low|medium|high",          // Inverse - high need = lower holdout
      "emotional_attachment": "low|medium|high",     // High = higher holdout
      "business_impact": "minimal|moderate|critical" // Critical = higher holdout
    },
    "sophistication": {
      "real_estate_experience": "low|medium|high",
      "legal_representation": true,
      "previous_negotiations": 8
    },
    "alternatives": {
      "relocation_options": "many|some|limited|none",  // Fewer = higher holdout
      "financial_flexibility": "low|medium|high",
      "timeline_pressure": "low|medium|high"           // High pressure = lower holdout
    }
  }
}
```

## Shared Utilities Integration

Uses shared modules from `/Shared_Utils/`:

- `negotiation_utils.py`:
  - `calculate_batna()` - BATNA calculation with expected value
  - `calculate_zopa()` - Zone of possible agreement
  - `optimal_settlement_range()` - Target, floor, ceiling recommendations
  - `calculate_concession_strategy()` - Diminishing concessions (50%, 25%, 12.5% pattern)

- `risk_utils.py`:
  - `assess_holdout_risk()` - Holdout probability from owner profile (0-30 scale)

## Modules

### `modules/owner_profiling.py`

Owner psychology analysis:

```python
from modules.owner_profiling import (
    analyze_owner_psychology,
    recommend_communication_strategy,
    predict_negotiation_behavior
)

# Classify owner type and identify motivations
owner_analysis = analyze_owner_psychology(owner_profile)
# Returns: owner_type, sophistication_level, primary_motivation, key_concerns

# Tailor communication approach
comm_strategy = recommend_communication_strategy(owner_analysis)
# Returns: tone, key_messages, rapport_tactics, negotiation_techniques

# Predict response to offer scenario
prediction = predict_negotiation_behavior(owner_analysis, offer_scenario)
# Returns: likely_response, probabilities, predicted_counter
```

**Owner Types**:
- `RATIONAL_INVESTOR` - Professional, data-driven approach
- `LEGACY_HOLDER` - Relationship-first, respectful empathetic tone
- `OPERATING_BUSINESS` - Problem-solving, practical focus
- `FINANCIAL_DISTRESS` - Expedited supportive, emphasize certainty
- `SOPHISTICATED_HOLDOUT` - Evidence-based professional, detailed analytical

### `modules/negotiation_tactics.py`

Tactical recommendations:

```python
from modules.negotiation_tactics import (
    recommend_opening_offer,
    generate_concession_plan,
    identify_leverage_points
)

# Calculate optimal opening position
opening = recommend_opening_offer(settlement_range, owner_analysis, holdout_risk, context)
# Returns: recommended_opening, rationale, messaging, supporting_evidence

# Generate concession plan (4-5 rounds)
concession_plan = generate_concession_plan(opening_offer, target, risk_level)
# Returns: List of rounds with tactical notes and techniques

# Analyze leverage
leverage = identify_leverage_points(data, batna, zopa, owner_analysis, context)
# Returns: buyer_advantages, owner_advantages, leverage_balance, recommendations
```

## Sample Files

### `sample_2_urban_station.json` **[NEW]**

Urban commercial property acquisition for transit station:
- **Property**: 450 King Street West, Toronto - 12,500 sqft commercial
- **Valuation**: $4.25M market value, $4.1M seller minimum
- **Owner**: Sophisticated investor, 18 years ownership, high experience
- **Holdout Risk**: CRITICAL (24/30) - 70% holdout probability
- **Challenge**: No financial pressure, rising market, legal representation
- **Context**: High political visibility, timeline pressure, partial taking

**Demonstrates**:
- SOPHISTICATED_HOLDOUT owner type
- High holdout risk (24/30)
- Buyer disadvantage (owner has most leverage)
- Conservative opening strategy (5% below target)
- Collaborative problem-solving approach
- Evidence-based professional communication

### `sample_1_farmer_easement.json`

Agricultural easement negotiation - see Negotiation Settlement Calculator.

## Negotiation Techniques Reference

The strategy planner integrates with negotiation-expert skill techniques:

### Recommended by Owner Type

**LEGACY_HOLDER**:
- Accusation audit: "You probably think..."
- Labeling: "It seems like this property has deep family history..."
- Tactical empathy and relationship building
- Respectful, patient approach

**SOPHISTICATED_HOLDOUT**:
- Evidence-based anchoring with market data
- Calibrated questions: "How do you arrive at..."
- Professional directness about BATNA
- Detailed analytical presentation

**OPERATING_BUSINESS**:
- Calibrated questions: "What would make the transition work..."
- Problem-solving focus on business continuity
- Creative solutions (phased moves, temp facilities)
- Practical evidence style

**FINANCIAL_DISTRESS**:
- Emphasize settlement speed and certainty
- Contrast with hearing delays and costs
- Payment structure flexibility
- Supportive but efficient

**RATIONAL_INVESTOR**:
- Market evidence and comparable data
- Cost-benefit analysis
- Professional businesslike tone
- Data-driven approach

## Integration with Settlement Calculator

**Workflow**:

1. **Strategy Planner** (this tool) - Develop approach
   - Analyze owner psychology
   - Calculate BATNA/ZOPA
   - Recommend opening offer and tactics

2. **Settlement Calculator** - Quantify scenarios
   - Expected value of settlement vs hearing
   - Risk-adjusted NPV
   - Sensitivity analysis

**Use Together For**:
- Complex acquisition negotiations
- High-value properties ($1M+)
- Sophisticated/resistant owners
- High political visibility
- Timeline pressure situations

## Output Structure

```json
{
  "property_info": {...},
  "analysis_date": "2025-11-17T00:14:28",
  "context_analysis": {
    "property_complexity": "high",
    "project_urgency": "HIGH",
    "timeline_pressure": "high"
  },
  "owner_analysis": {
    "owner_type": "SOPHISTICATED_HOLDOUT",
    "sophistication_level": "HIGH",
    "primary_motivation": "Maximize value through process knowledge",
    "key_concerns": [...]
  },
  "holdout_risk": {
    "total_score": 24,
    "risk_level": "CRITICAL",
    "holdout_probability": 0.7,
    "mitigation_strategies": [...]
  },
  "batna": {
    "expected_award": 4285000,
    "total_costs": 255000,
    "net_batna": 4540000
  },
  "zopa": {
    "exists": true,
    "lower_bound": 4100000,
    "upper_bound": 4540000,
    "midpoint": 4320000
  },
  "settlement_range": {
    "opening_offer": 4188000,
    "target": 4320000,
    "ceiling": 4364000,
    "walkaway": 4540000
  },
  "opening_offer": {
    "recommended_opening": 4104000,
    "rationale": "5% below target - very high holdout risk",
    "messaging": [...],
    "supporting_evidence": [...]
  },
  "concession_plan": [
    {
      "round": 1,
      "offer": 4104000,
      "concession": 0,
      "tactical_note": "Anchor with market evidence"
    },
    ...
  ],
  "leverage_points": {
    "buyer_advantages": [],
    "owner_advantages": [...],
    "leverage_balance": "STRONGLY_OWNER_FAVORED"
  },
  "negotiation_strategy": {
    "approach": "COLLABORATIVE_PROBLEM_SOLVING",
    "communication_style": "evidence_based_professional",
    "primary_tactics": [...],
    "timeline_strategy": "Aggressive with defined milestones"
  },
  "negotiation_plan": {
    "phase_1_opening": {
      "offer_amount": 4104000,
      "actions": [...],
      "key_messages": [...]
    },
    "phase_2_negotiation": {
      "concession_strategy": [...],
      "techniques": [...]
    },
    "phase_3_closure": {
      "target_amount": 4320000,
      "walkaway_amount": 4540000
    },
    "contingency_planning": {...}
  },
  "recommendations": {
    "primary_approach": "COLLABORATIVE_PROBLEM_SOLVING",
    "opening_offer": 4104000,
    "target_settlement": 4320000,
    "walkaway_point": 4540000,
    "key_tactics": [...],
    "critical_success_factors": [...]
  }
}
```

## When to Use This Tool

**Use Negotiation Strategy Planner when**:
- Developing approach for complex acquisition
- Owner psychology is critical factor
- Need tactical plan with opening offers and concessions
- High holdout risk situation
- Sophisticated or resistant owner
- Political sensitivity requires careful approach

**Use Settlement Calculator when**:
- Comparing settlement scenarios quantitatively
- Need detailed cost-benefit analysis
- Risk-adjusted NPV required
- Multiple settlement options to evaluate

**Use Both when**:
- High-stakes negotiation ($2M+)
- Critical project with timeline pressure
- Sophisticated owner with legal representation
- Need both strategy AND financial justification

## Dependencies

**Python 3.7+**

**Shared Utilities** (automatically imported):
- `Shared_Utils/negotiation_utils.py`
- `Shared_Utils/risk_utils.py`

**Local Modules**:
- `modules/owner_profiling.py`
- `modules/negotiation_tactics.py`

## Related Skills

- `negotiation-expert` - Master skill with all techniques
- `agricultural-easement-negotiation-frameworks` - Farm-specific approaches
- `expropriation-compensation-entitlement-analysis` - Legal framework

## Author Notes

**Strategy Planner Philosophy**:
> "Negotiation success in infrastructure acquisition comes from understanding owner psychology first, then tailoring approach and tactics to their motivations. Numbers matter, but so does relationship and communication style."

**Critical Success Factor**:
> "The opening offer sets the tone. Too aggressive with a sophisticated owner damages relationship. Too conservative with financial distress wastes leverage. Owner profiling gets this right."

**When Leverage is Against You** (like sample_2_urban_station.json):
> "When owner has all the leverage (no pressure, sophisticated, rising market), shift to collaborative problem-solving. Create value through transition support, timeline flexibility, and relationship integrity. You can't muscle a sophisticated holder—you have to make them want to work with you."
