"""
Output Formatting Module
Format utility conflict analysis reports and summaries
"""

from typing import Dict, List, Any
import sys
import os

# Add Shared_Utils to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from Shared_Utils.report_utils import eastern_timestamp, format_markdown_table


def format_conflict_report(
    project_data: Dict[str, Any],
    conflicts: List[Dict[str, Any]],
    conflict_matrix: Dict[str, Dict[str, int]],
    relocation_requirements: List[Dict[str, Any]],
    cost_estimate: Dict[str, Any],
    timeline_data: Dict[str, Any]
) -> str:
    """
    Format complete utility conflict analysis report

    Args:
        project_data: Project alignment data
        conflicts: List of conflicts
        conflict_matrix: Conflict summary matrix
        relocation_requirements: Relocation requirements list
        cost_estimate: Cost estimates
        timeline_data: Timeline and critical path data

    Returns:
        Formatted markdown report
    """
    sections = []

    # Header
    sections.append(_format_header(project_data))

    # Executive Summary
    sections.append(_format_executive_summary(
        conflicts, conflict_matrix, cost_estimate, timeline_data
    ))

    # Conflict Summary
    sections.append(_format_conflict_summary(conflicts, conflict_matrix))

    # Detailed Conflicts by Severity
    sections.append(_format_conflicts_by_severity(conflicts))

    # Relocation Requirements
    sections.append(_format_relocation_requirements(relocation_requirements))

    # Cost Estimates
    sections.append(_format_cost_estimates(cost_estimate))

    # Timeline and Critical Path
    sections.append(_format_timeline(timeline_data))

    # Risk Assessment
    sections.append(_format_risk_assessment(conflicts, cost_estimate, timeline_data))

    # Recommendations
    sections.append(_format_recommendations(conflicts, relocation_requirements))

    return '\n\n'.join(sections)


def _format_header(project_data: Dict[str, Any]) -> str:
    """Format report header"""
    project_type = project_data.get('project_alignment', {}).get('type', 'Unknown')
    location = project_data.get('project_alignment', {}).get('location', {})

    return f"""# Utility Conflict Analysis Report

**Project Type:** {project_type.replace('_', ' ').title()}
**Location:** {location.get('address', 'Not specified')}
**Report Generated:** {eastern_timestamp()}

---"""


def _format_executive_summary(
    conflicts: List[Dict[str, Any]],
    conflict_matrix: Dict[str, Dict[str, int]],
    cost_estimate: Dict[str, Any],
    timeline_data: Dict[str, Any]
) -> str:
    """Format executive summary section"""
    total_conflicts = len(conflicts)
    critical_conflicts = sum(1 for c in conflicts if c.get('severity') == 'CRITICAL')
    high_conflicts = sum(1 for c in conflicts if c.get('severity') == 'HIGH')

    total_cost_low = cost_estimate['total_range']['low']
    total_cost_high = cost_estimate['total_range']['high']

    critical_path_months = timeline_data.get('critical_path_duration', 0)

    return f"""## Executive Summary

**Total Conflicts Identified:** {total_conflicts}
- Critical: {critical_conflicts}
- High: {high_conflicts}
- Medium: {sum(1 for c in conflicts if c.get('severity') == 'MEDIUM')}
- Low: {sum(1 for c in conflicts if c.get('severity') == 'LOW')}

**Estimated Relocation Cost:** ${total_cost_low:,.0f} - ${total_cost_high:,.0f}
- Includes 25% contingency for utility relocation complexity

**Critical Path Duration:** {critical_path_months} months
- Transmission line relocations drive critical path

**Affected Utility Owners:** {len(conflict_matrix)}"""


def _format_conflict_summary(
    conflicts: List[Dict[str, Any]],
    conflict_matrix: Dict[str, Dict[str, int]]
) -> str:
    """Format conflict summary matrix"""
    output = ["## Conflict Summary Matrix\n"]

    # Create table data in the format expected by format_markdown_table
    table_data = []

    for owner, counts in conflict_matrix.items():
        table_data.append({
            'utility_owner': owner,
            'critical': str(counts.get('CRITICAL', 0)),
            'high': str(counts.get('HIGH', 0)),
            'medium': str(counts.get('MEDIUM', 0)),
            'low': str(counts.get('LOW', 0)),
            'total': str(counts['total'])
        })

    # Add total row
    total_critical = sum(c.get('CRITICAL', 0) for c in conflict_matrix.values())
    total_high = sum(c.get('HIGH', 0) for c in conflict_matrix.values())
    total_medium = sum(c.get('MEDIUM', 0) for c in conflict_matrix.values())
    total_low = sum(c.get('LOW', 0) for c in conflict_matrix.values())
    total_all = sum(c['total'] for c in conflict_matrix.values())

    table_data.append({
        'utility_owner': '**TOTAL**',
        'critical': f'**{total_critical}**',
        'high': f'**{total_high}**',
        'medium': f'**{total_medium}**',
        'low': f'**{total_low}**',
        'total': f'**{total_all}**'
    })

    columns = ['utility_owner', 'critical', 'high', 'medium', 'low', 'total']
    output.append(format_markdown_table(table_data, columns))

    return '\n'.join(output)


def _format_conflicts_by_severity(conflicts: List[Dict[str, Any]]) -> str:
    """Format detailed conflicts grouped by severity"""
    output = ["## Detailed Conflicts by Severity\n"]

    # Group by severity
    by_severity = {
        'CRITICAL': [],
        'HIGH': [],
        'MEDIUM': [],
        'LOW': []
    }

    for conflict in conflicts:
        severity = conflict.get('severity', 'LOW')
        by_severity[severity].append(conflict)

    # Format each severity level
    for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        if by_severity[severity]:
            output.append(f"### {severity} Severity Conflicts ({len(by_severity[severity])})\n")

            for conflict in by_severity[severity]:
                output.append(f"""**{conflict['utility_id']}**
- Conflict Type: {conflict['conflict_type']}
- Actual Distance: {conflict['distance']:.2f}m
- Required Clearance: {conflict['required_clearance']:.2f}m
- Shortfall: {conflict['shortfall']:.2f}m
""")

    return '\n'.join(output)


def _format_relocation_requirements(requirements: List[Dict[str, Any]]) -> str:
    """Format relocation requirements section"""
    output = ["## Relocation Requirements\n"]

    for req in requirements:
        output.append(f"""### {req['utility_id']}

**Relocation Type:** {req['relocation_type']}
**Conflict Count:** {req['conflict_count']} ({req['max_severity']} severity)
**Estimated Duration:** {req['estimated_duration']}
**Critical Path Impact:** {'Yes' if req['critical_path_impact'] else 'No'}

**Design Requirements:**
{_format_list(req['design_requirements'])}

**Approval Agencies:**
{_format_list(req['approval_agencies'])}
""")

    return '\n'.join(output)


def _format_cost_estimates(cost_estimate: Dict[str, Any]) -> str:
    """Format cost estimates section"""
    output = ["## Cost Estimates\n"]

    # Summary table
    output.append("### Cost Summary by Utility\n")

    table_data = []
    for cost in cost_estimate['utility_costs']:
        table_data.append({
            'utility': cost['utility_type'],
            'owner': cost['owner'],
            'low_estimate': f"${cost['cost_range']['low']:,.0f}",
            'high_estimate': f"${cost['cost_range']['high']:,.0f}",
            'unit_cost': cost['cost_range'].get('unit', 'N/A')
        })

    columns = ['utility', 'owner', 'low_estimate', 'high_estimate', 'unit_cost']
    output.append(format_markdown_table(table_data, columns))

    # Total costs
    subtotal = cost_estimate['subtotal_range']
    contingency = cost_estimate['contingency']
    total = cost_estimate['total_range']

    output.append(f"""
### Total Project Cost

| Component | Low Estimate | High Estimate |
|-----------|--------------|---------------|
| Utility Relocations | ${subtotal['low']:,.0f} | ${subtotal['high']:,.0f} |
| Contingency (25%) | ${contingency['low']:,.0f} | ${contingency['high']:,.0f} |
| **Total Estimated Cost** | **${total['low']:,.0f}** | **${total['high']:,.0f}** |
""")

    return '\n'.join(output)


def _format_timeline(timeline_data: Dict[str, Any]) -> str:
    """Format timeline and critical path section"""
    output = ["## Coordination Timeline and Critical Path\n"]

    critical_path_duration = timeline_data.get('critical_path_duration', 0)
    critical_activities = timeline_data.get('critical_activities', [])

    output.append(f"**Critical Path Duration:** {critical_path_duration} months\n")
    output.append("### Critical Path Activities\n")

    for activity in critical_activities:
        output.append(f"- **{activity['name']}** ({activity['duration']} months)")
        if activity.get('dependencies'):
            output.append(f"  - Dependencies: {', '.join(activity['dependencies'])}")

    return '\n'.join(output)


def _format_risk_assessment(
    conflicts: List[Dict[str, Any]],
    cost_estimate: Dict[str, Any],
    timeline_data: Dict[str, Any]
) -> str:
    """Format risk assessment section"""
    output = ["## Risk Assessment\n"]

    # Schedule risks
    output.append("### Schedule Risks\n")

    critical_count = sum(1 for c in conflicts if c.get('severity') == 'CRITICAL')
    if critical_count > 0:
        output.append(f"- **HIGH RISK:** {critical_count} critical conflicts requiring complex relocations")

    critical_path_duration = timeline_data.get('critical_path_duration', 0)
    if critical_path_duration > 18:
        output.append(f"- **HIGH RISK:** Critical path duration of {critical_path_duration} months may impact project schedule")

    # Cost risks
    output.append("\n### Cost Risks\n")

    cost_range = cost_estimate['total_range']
    cost_spread = cost_range['high'] - cost_range['low']
    if cost_spread > 1000000:
        output.append(f"- **MEDIUM RISK:** Cost range spread of ${cost_spread:,.0f} indicates uncertainty")

    output.append("- **MEDIUM RISK:** Utility relocation costs subject to owner engineering review")
    output.append("- **MEDIUM RISK:** Unforeseen utilities may be discovered during construction")

    # Coordination risks
    output.append("\n### Coordination Risks\n")

    owners = set(c.get('owner') for c in conflicts)
    if len(owners) > 3:
        output.append(f"- **MEDIUM RISK:** {len(owners)} different utility owners require coordination")

    output.append("- **LOW RISK:** Standard utility relocation processes well-established")

    return '\n'.join(output)


def _format_recommendations(
    conflicts: List[Dict[str, Any]],
    relocation_requirements: List[Dict[str, Any]]
) -> str:
    """Format recommendations section"""
    output = ["## Recommendations\n"]

    output.append("### Immediate Actions\n")

    # Critical conflicts
    critical_conflicts = [c for c in conflicts if c.get('severity') == 'CRITICAL']
    if critical_conflicts:
        output.append("1. **Initiate immediate discussions with utility owners for critical conflicts:**")
        for conflict in critical_conflicts[:3]:  # Top 3
            output.append(f"   - {conflict['owner']}: {conflict['conflict_type']}")

    # Critical path items
    critical_req = [r for r in relocation_requirements if r.get('critical_path_impact')]
    if critical_req:
        output.append("\n2. **Fast-track approvals for critical path utilities:**")
        for req in critical_req[:3]:  # Top 3
            output.append(f"   - {req['owner']}: {req['relocation_type']}")

    output.append("\n### Next Steps\n")
    output.append("1. Conduct utility owner coordination meetings")
    output.append("2. Obtain detailed as-built drawings from all utility owners")
    output.append("3. Conduct subsurface utility engineering (SUE) investigation")
    output.append("4. Develop detailed relocation designs")
    output.append("5. Submit applications to approval agencies")
    output.append("6. Negotiate cost sharing agreements")
    output.append("7. Update project schedule with confirmed utility timelines")

    return '\n'.join(output)


def _format_list(items: List[str]) -> str:
    """Format list items with bullets"""
    return '\n'.join(f"- {item}" for item in items)


def format_conflict_summary_table(conflicts: List[Dict[str, Any]]) -> str:
    """Format conflicts as a summary table"""
    table_data = []

    for conflict in conflicts:
        table_data.append({
            'utility': conflict.get('utility_type', 'Unknown'),
            'owner': conflict.get('owner', 'Unknown'),
            'conflict_type': conflict.get('conflict_type', 'Unknown'),
            'severity': conflict.get('severity', 'Unknown'),
            'shortfall_m': f"{conflict.get('shortfall', 0):.2f}"
        })

    columns = ['utility', 'owner', 'conflict_type', 'severity', 'shortfall_m']
    return format_markdown_table(table_data, columns)
