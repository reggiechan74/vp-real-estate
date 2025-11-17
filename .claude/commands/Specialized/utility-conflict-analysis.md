---
description: Utility conflict analysis identifying relocations, protection requirements, coordination needs, and relocation costs for infrastructure projects
argument-hint: <design-plans-json> [--output <report-path>]
allowed-tools: Read, Write, Bash
---

# Utility Conflict Analysis

Systematic utility conflict detection, relocation requirements analysis, cost estimation, and coordination timeline development for infrastructure projects.

## Usage

```bash
# Basic usage with JSON input
/utility-conflict-analysis path/to/project_design.json

# With custom output path
/utility-conflict-analysis path/to/project_design.json --output Reports/2025-11-17_utility_conflicts.md
```

## Input Structure

The input JSON should follow the `utility_conflict_input_schema.json` specification:

```json
{
  "project_alignment": {
    "type": "transit_station",
    "name": "Main Street Station",
    "location": {
      "x": 0,
      "y": 0,
      "excavation_depth": 15
    },
    "description": "Light rail transit station with underground platform"
  },
  "existing_utilities": [
    {
      "utility_type": "Gas main",
      "owner": "Enbridge",
      "size": "12-inch high pressure",
      "location": {
        "x": 100,
        "y": 50
      },
      "depth": 3.5,
      "criticality": "CRITICAL"
    },
    {
      "utility_type": "Transmission line",
      "owner": "Hydro One",
      "voltage": "115kV",
      "location": {
        "x": 150,
        "y": 75
      },
      "clearance_required": 10,
      "height": 25
    }
  ],
  "design_constraints": {
    "horizontal_clearance_min": 5,
    "vertical_clearance_min": 3,
    "protection_zone_width": 10
  }
}
```

## Workflow

This command executes the following workflow:

1. **Validate Input**: Validates JSON against schema
2. **Detect Conflicts**: Identifies geometric conflicts (horizontal/vertical/protection zone)
3. **Classify Severity**: CRITICAL/HIGH/MEDIUM/LOW based on clearance violations
4. **Generate Relocation Requirements**: Design requirements by utility type
5. **Estimate Costs**: Calculate relocation cost ranges by utility:
   - Transmission: $600K-$3.5M/km (by voltage)
   - Gas: $200K-$1M/km (by pressure)
   - Water/Sewer: $250-$1,200/meter (by diameter)
   - Telecom: $150-$600/meter
6. **Develop Timeline**: PERT/CPM critical path with coordination milestones
7. **Assess Risks**: Schedule delays, cost overruns, coordination failures
8. **Generate Report**: Timestamped markdown report with conflict matrix

## Output

The command generates:

- **Conflict Matrix**: Utility, conflict type, severity, distance/clearance
- **Relocation Requirements**: By utility with design specs and approval agencies
- **Cost Estimate Range**: By utility and total (low/high with 25% contingency)
- **Coordination Timeline**: Critical path showing 12-month workflow
- **Risk Assessment**: Schedule, cost, and coordination risks with mitigation
- **Timestamped Report**: `Reports/YYYY-MM-DD_HHMMSS_utility_conflicts_{project}.md`

## Related Skills

- **right-of-way-expert**: Auto-loaded for utility analysis
- **expropriation-timeline-expert**: For statutory deadline integration
- **land-assembly-expert**: For multi-parcel coordination

## Calculator

Uses: `.claude/skills/right-of-way-expert/utility_conflict_analyzer.py`
