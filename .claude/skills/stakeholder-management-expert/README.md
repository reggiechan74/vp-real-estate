# Stakeholder Management Expert

Expert in stakeholder consultation analysis, feedback summarization, sentiment analysis, and response strategy development.

## Quick Start

```bash
# Run consultation summarizer with sample data
cd /workspaces/lease-abstract/.claude/skills/stakeholder-management-expert
python consultation_summarizer.py samples/sample_1_station_public_meeting.json --verbose

# Specify output location
python consultation_summarizer.py input.json --output custom_report.md

# Generate JSON output
python consultation_summarizer.py input.json --format json
```

## Tools

### 1. Consultation Summarizer

Analyzes stakeholder feedback from public meetings and generates response strategy.

**Input:** JSON file with meeting info, comments, and theme categories

**Output:** Comprehensive markdown or JSON report with:
- Meeting attendance and demographics
- Theme categorization (frequency-weighted)
- Sentiment analysis (support/opposition/neutral/mixed)
- Response strategy recommendations
- Commitments tracking matrix
- Key representative quotes

**Example Output:**
```
Consultation summary generated: Reports/2025-11-16_191331_consultation_summary_north_transit_station_project.md

--- Summary Statistics ---
Total Comments: 86
Themes Identified: 10
Overall Sentiment: Strong opposition
Response Strategies: 10
Commitments Tracked: 50

Top 3 Themes:
  1. Construction Impact - 31 comments (27.2%)
  2. Traffic - 25 comments (21.9%)
  3. Accessibility - 11 comments (9.6%)
```

## Features

### Theme Categorization
- Keyword-based theme classification
- Multi-category comment identification
- Frequency weighting by theme
- Uncategorized comment tracking

### Sentiment Analysis
- Support/opposition/neutral/mixed classification
- Overall sentiment assessment
- Net sentiment calculation
- Representative quote extraction

### Response Strategy
- Priority-based strategy generation
- Tactical recommendations for each theme
- Commitment tracking and monitoring
- Response templates by theme type

### NLP Analysis
- Key phrase extraction
- Emotion indicator detection
- Question vs. statement classification
- Suggestion vs. concern detection

## Input Format

See `consultation_input_schema.json` for complete schema.

### Minimal Example
```json
{
  "meeting_info": {
    "meeting_date": "2025-10-15",
    "attendance": 85
  },
  "comments": [
    "Concerned about traffic during construction",
    "Support this project!",
    ...
  ],
  "theme_categories": {
    "Traffic": ["traffic", "congestion", "parking"],
    "Support": ["support", "favor", "positive"]
  }
}
```

### Complete Example
```json
{
  "meeting_info": {
    "meeting_date": "2025-10-15",
    "meeting_type": "public_meeting",
    "attendance": 85,
    "location": "Community Center",
    "project_name": "Transit Station Project",
    "phase": "preliminary_design"
  },
  "demographics": {
    "residents": 52,
    "business_owners": 18,
    "property_owners": 10
  },
  "comments": [...],
  "theme_categories": {...},
  "priorities": {
    "Traffic": 1,
    "Business Impact": 2
  },
  "output_options": {
    "include_quotes": true,
    "max_quotes_per_sentiment": 5,
    "include_commitments": true,
    "output_format": "markdown"
  }
}
```

## Module Structure

```
stakeholder-management-expert/
├── README.md                             # This file
├── SKILL.md                              # Detailed skill documentation
├── consultation_summarizer.py            # Main calculator
├── consultation_input_schema.json        # JSON Schema validation
├── modules/
│   ├── __init__.py                       # Package initialization
│   ├── validators.py                     # Input validation
│   ├── nlp_processing.py                 # Natural language processing
│   └── output_formatters.py              # Report formatting
└── samples/
    └── sample_1_station_public_meeting.json  # Sample transit meeting
```

## Shared Utilities

This skill uses shared utilities from `/workspaces/lease-abstract/Shared_Utils/`:

### stakeholder_utils.py
- `categorize_themes()` - Theme categorization with keyword matching
- `sentiment_analysis()` - Sentiment classification
- `frequency_weighting()` - Theme frequency analysis
- `generate_response_strategy()` - Strategy generation
- `commitments_matrix()` - Commitment extraction
- `extract_key_quotes()` - Representative quote selection

### report_utils.py
- `format_markdown_table()` - Markdown table formatting
- `eastern_timestamp()` - Eastern Time timestamp generation

## Use Cases

### Transit Infrastructure Projects
- Public consultations for new stations
- Route alignment feedback sessions
- Construction impact meetings

### Real Estate Development
- Community consultations for major projects
- Rezoning application feedback
- Stakeholder roundtables

### Infrastructure Projects
- Highway expansion consultations
- Utility corridor feedback
- Environmental assessment meetings

### Expropriation Projects
- Public information centres
- Affected party consultations
- Compensation discussions

## Integration

Works well with:
- **Transit Station Site Acquisition Strategy** - Stakeholder concerns inform site selection
- **Expropriation Timeline Expert** - Consultation requirements and schedules
- **Briefing Note Expert** - Convert summary to executive briefing
- **Agricultural Easement Negotiation** - Rural stakeholder management

## Output Examples

### Summary Statistics
```
Total Comments: 86
Themes Identified: 10
Overall Sentiment: Strong opposition (net: -18)
Support: 15 (17.4%)
Opposition: 33 (38.4%)
Neutral: 34 (39.5%)
```

### Top Themes
```
1. Construction Impact - 31 comments (27.2%)
2. Traffic - 25 comments (21.9%)
3. Accessibility - 11 comments (9.6%)
```

### Response Strategies
```
High Priority:
- Traffic: Prepare detailed traffic management plan
- Construction Impact: Phase construction to minimize disruption
- Business Impact: Establish business liaison program

Medium Priority:
- Property Values: Present market research on transit impacts
- Safety: Enhanced security measures during/after construction
```

## Testing

Run the sample to verify installation:
```bash
python consultation_summarizer.py samples/sample_1_station_public_meeting.json --verbose
```

Expected output:
- Report generated in `/workspaces/lease-abstract/Reports/`
- 10 themes identified
- 86 comments analyzed
- 50 commitments tracked

## Schema Validation

Input is validated against `consultation_input_schema.json` (JSON Schema Draft 2020-12).

Required fields:
- `meeting_info.meeting_date` (YYYY-MM-DD format)
- `meeting_info.attendance` (integer >= 0)
- `comments` (array of strings, min 1 item)
- `theme_categories` (object with keyword arrays)

Optional fields:
- `demographics` - Attendee breakdown
- `priorities` - Theme priority levels (1-5)
- `output_options` - Output customization

## Best Practices

### Theme Definition
1. Use 8-12 themes (not too many, not too few)
2. Include comprehensive keyword lists (synonyms, variations)
3. Avoid overlapping themes
4. Test with sample data and refine

### Priority Assignment
1. Priority 1: Critical concerns, high frequency
2. Priority 2: Important concerns, significant impact
3. Priority 3: Standard concerns, moderate impact
4. Priority 4-5: Minor concerns, informational

### Commitment Tracking
1. Document all commitments (even informal)
2. Assign clear responsibility
3. Set realistic deadlines
4. Track and communicate status

## Limitations

- Keyword-based classification (may miss nuanced comments)
- Simple sentiment analysis (no deep learning)
- English language only
- Text input only (no verbal feedback analysis)

## Future Enhancements

- Machine learning classification
- Advanced NLP sentiment analysis
- Multilingual support
- Trend analysis across multiple meetings
- Geographic clustering
- Stakeholder segmentation

---

**Version:** 1.0
**Last Updated:** 2025-11-17
**Author:** Reggie Chan, CFA, FRICS
