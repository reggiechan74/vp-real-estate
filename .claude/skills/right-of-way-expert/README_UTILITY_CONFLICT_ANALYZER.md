# Utility Conflict Analyzer

Modular calculator for detecting utility conflicts, generating relocation requirements, and estimating costs for infrastructure projects.

## Architecture

**Modular Design** - Thin orchestration layer with specialized modules:

```
utility_conflict_analyzer.py    # Main orchestrator (<400 lines)
modules/
  ├── __init__.py               # Module exports
  ├── validators.py             # Input validation
  ├── conflict_detection.py     # Geometric conflict detection
  ├── relocation_design.py      # Relocation requirements by utility type
  ├── cost_estimation.py        # Cost estimation with ranges
  └── output_formatters.py      # Report formatting
```

**Shared Utilities Integration:**
- `Shared_Utils.timeline_utils` - Critical path calculation (PERT/CPM)
- `Shared_Utils.report_utils` - Markdown formatting and timestamps

## Features

### Conflict Detection
- **Geometric Analysis**: Horizontal/vertical clearance violations
- **Protection Zones**: Utility-specific protection zone encroachment
- **Severity Classification**: CRITICAL/HIGH/MEDIUM/LOW based on utility type and shortfall
- **Conflict Matrix**: Summary by utility owner and severity

### Relocation Requirements
- **Type-Specific Design**: Custom requirements by utility type
  - Transmission lines (44kV - 500kV)
  - Gas pipelines (low/medium/high pressure, transmission)
  - Water mains and sewers (by diameter)
  - Telecom (fiber optic, copper, coax)
- **Approval Agencies**: Required permits and approvals
- **Duration Estimates**: Realistic timelines by complexity
- **Critical Path Impact**: Flag critical path activities

### Cost Estimation
- **Range Estimates**: Low/high cost ranges for uncertainty
- **Unit Costs**:
  - Transmission lines: $600K-$3.5M/km (by voltage)
  - Gas pipelines: $200K-$1M/km (by pressure)
  - Water/sewer: $250-$1,200/m (by diameter)
  - Telecom: $150-$600/m (by type)
- **Contingency**: 25% contingency for complexity
- **Cost Breakdown**: By owner and utility type

### Timeline Analysis
- **Critical Path**: PERT/CPM methodology
- **Activity Dependencies**: Sequential workflow
- **Risk Assessment**: Schedule and cost risks
- **Coordination Timeline**: Owner coordination sequence

## Usage

### Command Line

```bash
# Basic usage
python utility_conflict_analyzer.py input.json

# Custom output path
python utility_conflict_analyzer.py input.json --output report.md

# Verbose mode
python utility_conflict_analyzer.py input.json --verbose
```

### Input Format

```json
{
  "project_alignment": {
    "type": "transit_station",
    "location": {
      "address": "Project location",
      "x": 0,
      "y": 0,
      "excavation_depth": 25,
      "height": 0
    }
  },
  "existing_utilities": [
    {
      "utility_type": "Transmission line",
      "owner": "Hydro One",
      "voltage": "115kV",
      "location": {"x": 15, "y": 5},
      "height": 18,
      "clearance_required": 10,
      "relocation_length_km": 0.3
    },
    {
      "utility_type": "Gas main",
      "owner": "Enbridge",
      "size": "12-inch high pressure",
      "location": {"x": 8, "y": 3},
      "depth": 3.5,
      "relocation_length_km": 0.2
    }
  ],
  "design_constraints": {
    "horizontal_clearance_min": 5.0,
    "vertical_clearance_min": 3.0,
    "protection_zone_width": 10.0
  }
}
```

### Valid Utility Types

**Electric:**
- Transmission line
- Distribution line

**Gas:**
- Gas main
- Gas service

**Water/Sewer:**
- Water main
- Water service
- Sanitary sewer
- Storm sewer

**Telecom:**
- Telecom conduit
- Fiber optic
- Cable TV

**Other:**
- Street lighting
- Traffic signal
- Hydro vault
- Gas valve
- Water valve

### Valid Project Types

- `transit_station`
- `transit_corridor`
- `highway_expansion`
- `pipeline`
- `transmission_line`
- `building_foundation`
- `underground_parking`
- `tunnel`
- `subway`

## Output

### Markdown Report

Comprehensive report with:

1. **Executive Summary**
   - Total conflicts by severity
   - Cost estimate range
   - Critical path duration
   - Affected owners

2. **Conflict Summary Matrix**
   - Conflicts by owner and severity
   - Total counts

3. **Detailed Conflicts**
   - Grouped by severity
   - Conflict type, distance, shortfall

4. **Relocation Requirements**
   - Design requirements
   - Approval agencies
   - Duration estimates

5. **Cost Estimates**
   - By utility and owner
   - Total with contingency

6. **Timeline**
   - Critical path activities
   - Duration estimates

7. **Risk Assessment**
   - Schedule risks
   - Cost risks
   - Coordination risks

8. **Recommendations**
   - Immediate actions
   - Next steps

### JSON Output

Complete analysis results in JSON format for downstream processing.

## Examples

### Transit Station

```bash
python utility_conflict_analyzer.py samples/transit_station_input.json
```

**Output:**
- 8 conflicts detected (2 CRITICAL, 1 HIGH)
- $789K - $1.5M cost estimate
- 23-month critical path
- 5 utility owners affected

### Pipeline Corridor

```bash
python utility_conflict_analyzer.py samples/pipeline_corridor_input.json
```

**Output:**
- Multiple corridor conflicts
- Long-distance relocation costs
- Extended timeline for coordination

## Testing

```bash
# Run all tests
python -m pytest .claude/skills/right-of-way-expert/tests/test_utility_conflict_analyzer.py -v

# Run specific test class
python -m pytest .claude/skills/right-of-way-expert/tests/test_utility_conflict_analyzer.py::TestValidators -v
```

**Test Coverage:**
- Input validation
- Conflict detection
- Severity classification
- Relocation requirements
- Cost estimation
- Full workflow integration

## Module Details

### validators.py

**Functions:**
- `validate_input_data(data)` - Validate input structure
- `sanitize_input(data)` - Normalize and apply defaults
- `validate_utility_location(location)` - Validate coordinates

**Validation Rules:**
- Required keys: `project_alignment`, `existing_utilities`
- Valid utility types and project types
- Numeric constraints (clearances, depths)
- Location coordinate validation

### conflict_detection.py

**Functions:**
- `detect_conflicts(alignment, utilities, constraints)` - Find all conflicts
- `classify_severity(conflict, utility)` - Classify severity level
- `generate_conflict_matrix(conflicts)` - Summary matrix
- `get_conflicts_by_severity(conflicts)` - Group by severity
- `get_conflicts_by_owner(conflicts)` - Group by owner

**Conflict Types:**
- Horizontal clearance violation
- Vertical clearance violation
- Protection zone encroachment
- Direct crossing/intersection
- Parallel proximity conflict

**Severity Logic:**
- CRITICAL: High-risk utilities + significant shortfall (>5m)
- HIGH: Medium-risk utilities + moderate shortfall (>3m)
- MEDIUM: Low-risk utilities or moderate shortfall (>2m)
- LOW: Minor violations (<2m)

### relocation_design.py

**Functions:**
- `generate_relocation_requirements(conflicts, utilities)` - Generate requirements

**Relocation Types:**
- Overhead transmission line relocation
- Distribution line relocation
- Gas pipeline relocation
- Watermain relocation
- Sewer relocation
- Telecom infrastructure relocation

**Requirements Include:**
- Design and engineering specifications
- Approval agencies and permits
- Duration estimates
- Critical path impact flag

### cost_estimation.py

**Functions:**
- `estimate_relocation_costs(requirements, utilities)` - Estimate costs

**Cost Ranges by Type:**

| Utility Type | Low | High | Unit |
|--------------|-----|------|------|
| 500kV Transmission | $2.5M | $3.5M | /km |
| 230kV Transmission | $1.5M | $2.5M | /km |
| 115kV Transmission | $800K | $1.5M | /km |
| High Pressure Gas | $600K | $1M | /km |
| Medium Pressure Gas | $300K | $600K | /km |
| Water/Sewer (600mm+) | $600 | $1,200 | /m |
| Water/Sewer (400-600mm) | $400 | $800 | /m |
| Distribution Line (UG) | $800 | $1,500 | /m |
| Distribution Line (OH) | $400 | $800 | /m |
| Fiber Optic | $300 | $600 | /m |
| Copper/Coax | $150 | $300 | /m |

**Contingency:** 25% applied to all estimates

### output_formatters.py

**Functions:**
- `format_conflict_report(...)` - Complete report
- `format_conflict_summary_table(conflicts)` - Conflict table

**Report Sections:**
- Header with timestamp
- Executive summary
- Conflict matrix
- Detailed conflicts by severity
- Relocation requirements
- Cost estimates
- Timeline and critical path
- Risk assessment
- Recommendations

## Cost Assumptions

**All estimates assume:**
- 2025 Canadian dollars
- Normal soil conditions
- Standard construction methods
- Includes engineering, construction, testing
- Excludes property acquisition costs
- Standard working hours (no premium time)

**Exclusions:**
- Environmental remediation
- Contaminated soil disposal
- Rock excavation (blasting)
- Dewatering (beyond normal)
- Traffic management (beyond standard)
- Property acquisition/easements

## Timeline Assumptions

**Duration estimates based on:**
- Normal permitting timelines
- Standard utility owner coordination
- No exceptional delays
- Sequential (not parallel) construction
- Standard crew productivity

**Critical path activities:**
- Transmission line relocations (always critical)
- High pressure gas pipelines (always critical)
- Large diameter water/sewer (often critical)

## Risk Factors

**Schedule Risks:**
- Utility owner engineering approval delays
- Unforeseen underground conflicts
- Weather delays (seasonal work)
- Permitting delays
- Material procurement delays

**Cost Risks:**
- Unforeseen subsurface conditions
- Additional utilities discovered
- Changed owner requirements
- Material price escalation
- Labor rate increases

**Coordination Risks:**
- Multiple utility owners
- Conflicting work schedules
- Access restrictions
- Service interruption constraints

## Integration with Existing Skills

This calculator integrates with:

- **right-of-way-expert** skill - Infrastructure corridor acquisition
- **land-assembly-expert** skill - Multi-parcel acquisition
- **expropriation-timeline-expert** skill - Regulatory deadlines
- **negotiation-expert** skill - Utility owner negotiations

## References

**Ontario Regulations:**
- Ontario One Call (locate standards)
- Technical Standards and Safety Authority (TSSA)
- Electrical Safety Authority (ESA)
- Ministry of Environment regulations

**Industry Standards:**
- CSA C22.3 No. 7 (Underground Systems)
- CSA Z662 (Oil and Gas Pipeline Systems)
- AWWA standards (Water Distribution)
- Canadian Electricity Association guidelines

**Typical Owners:**
- Hydro One (transmission)
- Local distribution companies (distribution)
- Enbridge Gas (natural gas)
- Municipal utilities (water/sewer)
- Telecom carriers (Bell, Rogers, etc.)

## Version History

- **v1.0.0** (2025-11-16): Initial release
  - Modular architecture
  - 5 core modules
  - Shared_Utils integration
  - 10 unit tests
  - 2 sample inputs
  - Comprehensive report formatting

## Author

Built as part of the infrastructure acquisition toolkit for right-of-way expert skill.

## License

Internal use only - Part of lease-abstract project infrastructure tools.
