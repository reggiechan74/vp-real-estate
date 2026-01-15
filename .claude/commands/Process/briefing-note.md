---
description: Generate executive briefing note (1-2 pages, decision-focused) for infrastructure acquisition projects
argument-hint: <input-json> [--output <report-path>]
allowed-tools: Read, Write, Bash
---

# Briefing Note Generator

Generate executive briefing note for infrastructure acquisition projects requiring board or executive approval.

## Calculator Integration

**Python Calculator**: `.claude/skills/briefing-note-expert/briefing_note_generator.py`
**Input Schema**: `.claude/skills/briefing-note-expert/briefing_note_input_schema.json`
**Skills**: `briefing-note-expert`
**Related Skills**: `negotiation-expert`, `settlement-analysis-expert`, `board-memo-expert`
**Related Agents**: Katy (transit corridor), Shadi (transmission corridor), Christi (legal compliance)

## Purpose

Generate concise executive briefing note (1-2 pages) for infrastructure acquisition projects. Focus on decision-making with clear issue statement, financial summary, risk assessment, and actionable recommendations.

## Usage

```bash
/briefing-note <input-json> [--output <report-path>]
```

**Arguments**: {{args}}

## Workflow

1. Read and validate JSON input file
2. Run `python .claude/skills/briefing-note-expert/briefing_note_generator.py {{arg0}}`
3. Generate timestamped markdown report in `Reports/`
4. Display success message with file path

## Example Commands

```bash
# Basic usage (auto-generates output in Reports/)
/briefing-note acquisition_summary.json

# Custom output path
/briefing-note samples/transit_station.json --output Reports/briefing.md
```

## Output

**Console**: Success message with analysis summary (urgency, strategic alignment, risk score)

**Report Sections**:
1. Issue / Decision Required (with urgency indicator 🔴/🟡/🟢)
2. Background and Context
3. Financial Summary (breakdown table, budget variance)
4. Analysis (strategic benefits, alternatives comparison)
5. Recommendation (with rationale and confidence)
6. Risk Assessment (grouped by severity)
7. Approvals Required
8. Action Items (prioritized)

## Related Commands

- `/board-memo` - Formal board approval memo with governance language
- `/settlement-analysis` - Settlement vs. hearing decision analysis
- `/negotiation-strategy` - Negotiation approach planning
