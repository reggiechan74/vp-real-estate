---
description: Board approval memo with comprehensive financial summary and risk analysis for infrastructure acquisitions
argument-hint: <input-json> [--output <report-path>]
allowed-tools: Read, Write, Bash
---

# Board Memo Generator

Generate formal board approval memo with comprehensive financial summary, risk analysis, and board resolution language.

## Calculator Integration

**Python Calculator**: `.claude/skills/board-memo-expert/board_memo_generator.py`
**Input Schema**: `.claude/skills/board-memo-expert/board_memo_input_schema.json`
**Skills**: `board-memo-expert`
**Related Skills**: `briefing-note-expert`, `land-assembly-expert`, `settlement-analysis-expert`
**Related Agents**: Katy (transit governance), Shadi (transmission projects), Christi (legal compliance)

## Purpose

Generate formal board approval memo for major infrastructure acquisitions. Includes executive summary, project rationale, comprehensive financial analysis with NPV, multi-level risk assessment, stakeholder consultation summary, and formal board resolution language.

## Usage

```bash
/board-memo <input-json> [--output <report-path>]
```

**Arguments**: {{args}}

## Workflow

1. Read and validate JSON input file
2. Run `python .claude/skills/board-memo-expert/board_memo_generator.py {{arg0}}`
3. Generate formal board memo with resolution language
4. Save timestamped markdown report in `Reports/`

## Example Commands

```bash
# Generate board memo
/board-memo project_details.json

# Custom output location
/board-memo samples/transmission_corridor.json --output Reports/board_memo.md
```

## Output

**Board Memo Sections**:
1. Executive Summary (1 paragraph, decision-focused)
2. Project Overview and Rationale (public benefit, strategic alignment)
3. Alternatives Analysis (comparison with pros/cons)
4. Financial Impact and Budget (total cost, NPV, funding sources)
5. Risk Assessment and Mitigation (Critical → High → Medium → Low)
6. Project Timeline (milestones over 12-24 months)
7. Stakeholder Consultation Summary (meetings, submissions, sentiment)
8. Approval Recommendation (**BE IT RESOLVED** language)
9. Compliance Requirements (authority limits, delegation)

## Related Commands

- `/briefing-note` - Concise 1-2 page executive briefing
- `/expropriation-timeline` - Critical path timeline analysis
- `/public-consultation-summary` - Stakeholder feedback analysis
