---
description: Summarize stakeholder feedback and response strategy from public meetings and written submissions
argument-hint: <consultation-data-json> [--output <report-path>]
allowed-tools: Read, Write, Bash
---

# Public Consultation Summary

Summarize stakeholder feedback from public meetings and generate prioritized response strategy.

## Calculator Integration

**Python Calculator**: `.claude/skills/stakeholder-management-expert/consultation_summarizer.py`
**Input Schema**: `.claude/skills/stakeholder-management-expert/consultation_input_schema.json`
**Skills**: `stakeholder-management-expert`
**Related Skills**: `briefing-note-expert`, `board-memo-expert`
**Related Agents**: Katy (transit public meetings, community engagement)

## Purpose

Analyze stakeholder feedback from public consultation meetings and written submissions. Categorize themes, perform sentiment analysis, weight by frequency, generate response strategies, and track commitments made during consultation.

## Usage

```bash
/public-consultation-summary <consultation-data-json> [--output <report-path>]
```

**Arguments**: {{args}}

## Workflow

1. Read consultation data JSON file
2. Run `python .claude/skills/stakeholder-management-expert/consultation_summarizer.py {{arg0}}`
3. Categorize comments into themes using keyword matching
4. Analyze sentiment (support/opposition/neutral/mixed)
5. Weight themes by frequency and generate response strategies
6. Extract and track commitments made
7. Generate comprehensive consultation summary report

## Example Commands

```bash
# Analyze public meeting feedback
/public-consultation-summary consultation_data.json

# Custom output path
/public-consultation-summary samples/station_meeting.json --output Reports/consultation_summary.md
```

## Output

**Consultation Summary Sections**:
1. Meeting Attendance and Demographics
2. Overview Statistics (total comments, themes, categorization rate)
3. Sentiment Analysis (support/opposition/neutral breakdown with net sentiment)
4. Key Themes and Concerns (ranked by frequency with sample comments)
5. Key Representative Quotes (by sentiment category)
6. Response Strategy Recommendations (High/Medium/Low priority with tactics)
7. Commitments Tracking Matrix (all commitments with deadlines and responsible parties)
8. Recommended Next Steps

**Analysis Output**:
- Total comments processed
- Themes identified (10-15 typical)
- Overall sentiment assessment (Strong opposition → Strong support)
- Top 3 themes by frequency
- Response strategies by priority level
- Commitments tracked

## Related Commands

- `/briefing-note` - Convert summary to executive briefing
- `/board-memo` - Include consultation in board approval memo
- `/expropriation-timeline` - Schedule follow-up consultation activities
