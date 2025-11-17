# Board Memo Expert

Expert in preparing comprehensive board approval memoranda for infrastructure projects, land acquisitions, and capital expenditures.

## Overview

This skill provides complete board approval documentation including:
- Executive summaries (decision-focused)
- Strategic rationale and alternatives analysis
- Financial impact with NPV/IRR analysis
- Multi-level risk assessment with mitigation strategies
- Formal board resolution language
- Compliance requirements tracking
- Stakeholder consultation documentation

## Files

### Core Generator
- `board_memo_generator.py` - Main generator script
- `board_memo_input_schema.json` - JSON Schema validation (Draft-07)

### Modules
- `modules/validators.py` - Input validation (financial, risk, governance)
- `modules/governance.py` - Board resolution language generation
- `modules/output_formatters.py` - Section formatting utilities

### Samples
- `samples/sample_1_transmission_corridor.json` - Complex land assembly example

## Usage

### Basic Usage

```bash
# Generate board memo from JSON input
python board_memo_generator.py samples/sample_1_transmission_corridor.json

# Specify output file
python board_memo_generator.py input.json --output Reports/2025-11-16_143022_board_memo.md

# Validate input only
python board_memo_generator.py input.json --validate-only
```

### Input Structure

Required sections:
- `project`: Name, description, rationale, urgency, alternatives
- `financial`: Total cost, breakdown, funding source, NPV (optional)
- `risks`: List of risks with severity, probability, mitigation
- `governance`: Approval type, recommendation, resolution language

Optional sections:
- `timeline`: Decision deadline, milestones
- `metadata`: Prepared by, date, confidentiality

See `board_memo_input_schema.json` for complete specification.

## Output Structure

1. **Executive Summary** - Decision-focused (1-2 paragraphs)
2. **Project Overview** - Description and strategic rationale
3. **Alternatives Considered** - Pros/cons analysis
4. **Financial Impact** - Detailed breakdown, NPV, funding source
5. **Risk Assessment** - Multi-level with mitigation strategies
6. **Timeline** - Critical milestones
7. **Recommendation** - Clear approval recommendation
8. **Compliance Requirements** - Regulatory obligations
9. **Board Resolution** - Formal resolution language

## Approval Types

**Authorization** (prospective approval):
```
BE IT RESOLVED that the Board authorizes management to proceed with [PROJECT]
at a total cost not to exceed $[AMOUNT] from [FUNDING SOURCE]...
```

**Ratification** (retrospective approval):
```
BE IT RESOLVED that the Board ratifies the actions of management in proceeding
with [ACTION] at a total cost of $[AMOUNT]...
```

**Delegation** (authority granting):
```
BE IT RESOLVED that the Board delegates authority to the CEO to approve
expenditures related to [CATEGORY] up to $[LIMIT]...
```

**Information Only**:
```
BE IT RESOLVED that the Board acknowledges receipt of information regarding
[PROJECT]...
```

## Risk Severity Levels

- **CRITICAL**: Probability >70%, threatens project viability
- **HIGH**: Probability 50-70%, significant delay/cost overrun
- **MEDIUM**: Probability 30-50%, moderate impact
- **LOW**: Probability <30%, minimal impact

## Shared Utilities

Integrates with:
- `Shared_Utils/report_utils.py` - Executive summary, financial formatting, risk tables
- `Shared_Utils/financial_utils.py` - NPV calculation validation
- `Shared_Utils/risk_utils.py` - Risk assessment (optional)

## Validation

All inputs validated against JSON schema:
- Financial breakdown totals match
- Risk severity levels valid
- Governance approval types valid
- NPV inputs consistent (if provided)

## Example: Transmission Corridor Acquisition

See `samples/sample_1_transmission_corridor.json` for a complete example including:
- $12.2M land acquisition (12 agricultural properties)
- 3 identified alternatives with rejection rationale
- 5 risks (HIGH, MEDIUM, LOW severity)
- NPV analysis (negative NPV for infrastructure project)
- Authorization resolution with $1.5M contract delegation
- 8 critical milestones over 18-month timeline
- Comprehensive stakeholder consultation summary

## Best Practices

### Executive Summary
- First sentence: "Board approval requested for [PROJECT]"
- Clear recommendation (not "approve as presented")
- Explicit financial impact
- Urgency indicator

### Financial Impact
- Full cost disclosure (no hidden costs)
- Specific funding source (not "available funds")
- NPV honesty (explain negative NPV if infrastructure)
- 10-20% contingency for complex projects

### Risk Assessment
- No surprises (over-disclose vs. under-disclose)
- Specific mitigation (not "monitor closely")
- Financial impact quantified
- Residual risk acknowledged

### Resolution Language
- Use "not to exceed" cost ceilings
- Specify funding source explicitly
- Define delegation limits clearly
- Include reporting requirements

## Integration with Other Skills

Complementary skills:
- `expropriation-compensation-entitlement-analysis` - Validates compensation methodology
- `settlement-analysis-expert` - Informs negotiation vs. expropriation decisions
- `injurious-affection-assessment` - Quantifies disturbance damages
- `comparable-sales-adjustment-methodology` - Supports market value analysis

## Testing

```bash
# Validate sample input
python board_memo_generator.py samples/sample_1_transmission_corridor.json --validate-only

# Generate sample memo
python board_memo_generator.py samples/sample_1_transmission_corridor.json

# Check output
cat Reports/2025-11-16_*_board_memo_*.md
```

## Schema Compliance

JSON Schema Draft-07 validation ensures:
- All required fields present
- Valid enumerated values (urgency, severity, approval_type)
- Numeric ranges (probability 0-1, percentages, costs)
- Date format validation
- Nested object structure integrity

## Common Mistakes to Avoid

1. ❌ Vague recommendations → ✅ Specific action requested
2. ❌ "Estimated cost: $10-15M" → ✅ "Total cost: $12.2M"
3. ❌ "No significant risks" → ✅ Multi-level risk assessment
4. ❌ Generic resolution → ✅ Precise authorization with limits
5. ❌ Missing compliance → ✅ Complete regulatory checklist
6. ❌ Unrealistic timelines → ✅ Base/aggressive/worst case scenarios

## License

Part of the lease-abstract commercial real estate analysis toolkit.
