# Expropriation Timeline Expert

Expert in calculating critical path project timelines using PERT/CPM methodology with statutory deadline integration for expropriation projects.

## Overview

This calculator provides comprehensive project timeline analysis using:

- **Critical Path Method (CPM)**: Identifies longest sequence of dependent tasks
- **PERT Analysis**: Three-point time estimates (optimistic/most_likely/pessimistic)
- **Statutory Deadline Tracking**: Integration with Ontario Expropriations Act deadlines
- **Risk Assessment**: Timeline risks, deadline compliance, float analysis
- **Resource Planning**: Staff, consultant, and budget requirements
- **Dependency Analysis**: Complexity metrics and bottleneck identification
- **Gantt Visualization**: Text-based timeline charts

## Features

### Critical Path Analysis
- Forward/backward pass calculations
- Early start/finish and late start/finish times
- Total float and free float calculations
- Critical path sequence identification

### PERT Methodology
- Expected time: (O + 4M + P) / 6
- Standard deviation: (P - O) / 6
- Project variance (sum of critical path variances)
- 90% and 95% confidence intervals

### OEA Statutory Deadlines
- 3-month registration deadline (s.9)
- Form 2 service timing (best practice)
- Form 7 service timing (s.11)
- Buffer analysis and risk assessment

### Resource Requirements
- Total staff-days and budget
- Peak resource requirements
- Consultant utilization by type
- Resource timeline by task

## Installation

No installation required. The calculator uses Python 3 standard library plus:
- `Shared_Utils/timeline_utils.py` - Critical path calculations
- `Shared_Utils/report_utils.py` - Report formatting

## Usage

### Command Line

**Basic usage**:
```bash
python project_timeline_calculator.py samples/sample_1_simple_acquisition.json
```

**Specify output location**:
```bash
python project_timeline_calculator.py input.json -o Reports/my_analysis.md
```

**JSON output format**:
```bash
python project_timeline_calculator.py input.json -f json -o results.json
```

**Verbose output**:
```bash
python project_timeline_calculator.py input.json -v
```

### Input Format

Create a JSON file with project tasks, dependencies, and deadlines:

```json
{
  "project_name": "Transit Station Property Acquisition",
  "approval_date": "2025-03-15",
  "tasks": [
    {
      "id": "A",
      "name": "Obtain Expropriation Approval",
      "duration": 30,
      "optimistic": 20,
      "most_likely": 30,
      "pessimistic": 45,
      "resources": {
        "staff": 2,
        "consultants": {"legal": 1},
        "budget": 15000
      }
    }
  ],
  "dependencies": [
    ["A", "B"]
  ],
  "statutory_deadlines": {
    "G": 90
  },
  "buffer_days": 10
}
```

See `samples/sample_1_simple_acquisition.json` for a complete example.

### Output Report

The calculator generates a markdown report with:

1. **Executive Summary**: Duration, critical path %, confidence interval, risk summary
2. **Critical Path Analysis**: Sequence of critical tasks with schedule
3. **Statutory Deadlines**: OEA milestone dates and compliance status
4. **Risk Assessment**: Timeline risks by severity (CRITICAL/HIGH/MEDIUM/LOW)
5. **Task Details Table**: All tasks with early/late dates, float, criticality
6. **Gantt Chart**: Text-based visualization
7. **Resource Requirements**: Total and peak resources
8. **Dependency Analysis**: Complexity metrics

## Modules

The calculator follows a modular architecture:

### `validators.py`
- Input validation against JSON schema
- Task validation (required fields, PERT estimates)
- Dependency validation (circular dependency detection)
- Deadline validation

### `critical_path.py`
- PERT/CPM calculations using Shared_Utils
- PERT expected time and variance
- Project confidence intervals
- Task enrichment with PERT metrics

### `dependencies.py`
- Dependency graph construction
- Predecessor/successor analysis
- Ancestor/descendant tracking
- Complexity metrics (density, bottlenecks)

### `statutory_deadlines.py`
- OEA registration deadline (s.9)
- Form 2/7 service dates (s.11)
- Days remaining calculation
- Risk assessment (buffer analysis)
- Milestone generation

### `output_formatters.py`
- Markdown report generation
- JSON output formatting
- Executive summary
- Risk assessment formatting
- Gantt chart generation

## Examples

### Sample 1: Simple Acquisition

**Project**: Transit station property acquisition
**Tasks**: 10 tasks (approval, plan preparation, review, registration, appraisal, Form 2 service)
**Dependencies**: Linear sequence with some parallel work
**Statutory deadline**: Plan registration by day 90

**Result**:
- Project duration: 97 days (PERT expected)
- Critical path: 7 of 10 tasks
- **CRITICAL risk**: Exceeds 90-day statutory deadline by 7 days
- Mitigation required: Crash critical path or fast-track

See `samples/sample_1_simple_acquisition.json`.

## Risk Assessment

### Timeline Risk Types

1. **Statutory Deadline Risk** (CRITICAL)
   - Task finishes after statutory deadline
   - Approval expires if missed
   - Mitigation: Crash schedule, expedite, obtain second approval

2. **Critical Path No-Float Risk** (MEDIUM)
   - Zero schedule flexibility
   - Any delay extends project
   - Mitigation: Add buffer, parallel work, increase resources

3. **Long Duration Risk** (LOW)
   - Task > 60 days (unforeseen delays likely)
   - Mitigation: Break into sub-tasks, weekly monitoring

4. **Dependency Bottleneck Risk** (MEDIUM)
   - Task with 3+ dependencies
   - Delays cascade through project
   - Mitigation: Early coordination, dedicated resources

### Buffer Analysis

```
Buffer = Statutory deadline - Task late finish
```

**Risk levels**:
- CRITICAL: Buffer < 0 (misses deadline)
- HIGH: Buffer 0-5 days (insufficient)
- MEDIUM: Buffer 5-10 days (below minimum)
- LOW: Buffer > 10 days (adequate)

## Integration with Other Skills

**Complementary skills**:

- **expropriation-statutory-deadline-tracking**: Operational monitoring (weekly checks, escalation)
- **expropriation-compensation-entitlement-analysis**: Legal compensation framework
- **land-assembly-expert**: Multi-property acquisition strategy

## Automated Workflow

**PDF → JSON → Python → Report pattern**:

1. User creates JSON input file
2. Schema validation ensures data integrity
3. PERT/CPM analysis computes critical path
4. Risk assessment identifies timeline risks
5. Markdown report generated with Gantt chart
6. Optional JSON export for further analysis

No manual intervention required - fully automated from input to report.

## Limitations

**Current implementation**:
- Finish-to-Start (FS) dependencies only
- Deterministic resource availability
- No automatic resource optimization
- Calendar days only (weekends/holidays not modeled)

**For advanced features**:
- Use project management software (MS Project, Primavera P6)
- Resource optimization algorithms
- Monte Carlo simulation (10,000+ scenarios)
- Earned value analysis

## Schema Validation

Input is validated against `project_timeline_input_schema.json`:

- Required fields: `project_name`, `approval_date`, `tasks`, `dependencies`
- Task fields: `id`, `name`, `duration` (required)
- PERT fields: `optimistic`, `most_likely`, `pessimistic` (all or none)
- Dependencies: `[predecessor, successor]` pairs
- Circular dependency detection
- Deadline validation

## Output Files

**Markdown reports**: Saved to `Reports/` with timestamp prefix
- Format: `YYYY-MM-DD_HHMMSS_timeline_<project_name>.md`
- Example: `2025-11-16_191455_timeline_transit_station_property_acquisition.md`

**JSON output**: Optional structured data export
- Same format as markdown reports
- Suitable for further processing or API integration

## Development

### Adding New Features

1. **New validation rules**: Edit `modules/validators.py`
2. **New calculations**: Edit `modules/critical_path.py` or create new module
3. **New output formats**: Edit `modules/output_formatters.py`
4. **New statutory deadlines**: Edit `modules/statutory_deadlines.py`

### Testing

Run the calculator with sample input:
```bash
python project_timeline_calculator.py samples/sample_1_simple_acquisition.json -v
```

Verify output in `Reports/` directory.

## References

- **PERT/CPM**: Project Management Body of Knowledge (PMBOK)
- **Ontario Expropriations Act**: R.S.O. 1990, c. E.26
- **Critical Path Method**: Linear programming and scheduling theory

## Support

For questions or issues, refer to:
- `SKILL.md` - Detailed methodology documentation
- `project_timeline_input_schema.json` - Input format specification
- Sample files in `samples/` - Working examples
