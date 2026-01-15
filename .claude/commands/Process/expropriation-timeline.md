---
description: Generate critical path timeline with Ontario Expropriations Act regulatory deadlines using PERT/CPM methodology
argument-hint: <project-milestones-json> [--output <report-path>]
allowed-tools: Read, Write, Bash
---

# Expropriation Timeline Generator

Generate critical path timeline with Ontario Expropriations Act statutory deadlines using PERT/CPM methodology.

## Calculator Integration

**Python Calculator**: `.claude/skills/expropriation-timeline-expert/timeline_generator.py`
**Input Schema**: `.claude/skills/expropriation-timeline-expert/timeline_generator_input_schema.json`
**Skills**: `expropriation-timeline-expert`
**Related Skills**: `expropriation-statutory-deadline-tracking`, `forms-1-12-completeness-verification`
**Related Agents**: Stevi (compliance and deadline watchdog), Christi (legal procedures), Katy/Shadi (project planning)

## Purpose

Calculate critical path schedule for expropriation projects with OEA statutory deadlines. Uses PERT/CPM methodology for forward/backward pass analysis, identifies critical tasks, calculates float, flags deadline risks, and generates resource requirements.

## Usage

```bash
/expropriation-timeline <project-milestones-json> [--output <report-path>]
```

**Arguments**: {{args}}

## Workflow

1. Read project timeline JSON with tasks, dependencies, and deadlines
2. Run `python .claude/skills/expropriation-timeline-expert/timeline_generator.py {{arg0}}`
3. Calculate critical path using PERT/CPM methodology
4. Identify statutory deadline compliance (3-month registration, Form 2 service)
5. Assess resource requirements (staff, consultants, budget)
6. Flag timeline risks and generate Gantt chart
7. Generate comprehensive timeline report

## Example Commands

```bash
# Generate timeline
/expropriation-timeline project_milestones.json

# Custom output
/expropriation-timeline samples/transit_corridor_timeline.json --output Reports/timeline.md
```

## Output

**Timeline Report Sections**:
1. Critical Path Analysis (task sequence, project duration, PERT estimates)
2. Task Details Table (early/late start/finish, total float, criticality)
3. Gantt Chart (text-based visualization with critical path highlighted)
4. Resource Requirements (staff-days, consultant-days, budget by phase)
5. Risk Assessment (statutory deadline compliance, no-float risks, bottlenecks)
6. Key Milestones (target dates for critical events)
7. Scenario Analysis (best/likely/worst case durations)

**Key Metrics**:
- Project duration (days, with 90% confidence interval)
- Critical path tasks (% of total)
- Statutory deadline compliance (PASS/AT RISK/FAIL)
- Total resource requirements (staff, consultants, budget)
- Risk flags (Critical → High → Medium → Low)

## Related Commands

- `/briefing-note` - Include timeline in executive briefing
- `/board-memo` - Include timeline in board approval memo
- `/land-assembly` - Multi-parcel timeline with phasing
