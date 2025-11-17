#!/usr/bin/env python3
"""
Phasing Strategy Module for Land Assembly Calculator
Implements phasing logic using shared land_assembly_utils
"""

import sys
from pathlib import Path

# Add parent directory to path for shared utilities
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'Shared_Utils'))

from land_assembly_utils import calculate_phasing_strategy
from typing import Dict, List


def generate_phasing_strategy(parcels: List[Dict], priorities: Dict) -> Dict:
    """
    Generate acquisition phasing strategy.

    Wrapper around shared calculate_phasing_strategy function.

    Args:
        parcels: List of parcel dictionaries
        priorities: Priority weights dict

    Returns:
        Phasing strategy dict with phases and parallel tracks
    """
    return calculate_phasing_strategy(parcels, priorities)


def format_phasing_output(phasing_result: Dict) -> str:
    """
    Format phasing strategy for markdown output.

    Args:
        phasing_result: Result from calculate_phasing_strategy

    Returns:
        Formatted markdown string
    """
    output = []

    output.append("## Acquisition Phasing Strategy\n")
    output.append(f"**Total Parcels:** {phasing_result['total_parcels']}\n")
    output.append(f"**Total Estimated Duration:** {phasing_result['total_duration_estimate_days']} days ({phasing_result['total_duration_estimate_days'] / 30:.1f} months)\n")

    # Phases
    for phase in phasing_result['phases']:
        output.append(f"\n### Phase {phase['phase']}: {phase['rationale']}")
        output.append(f"- **Parcels:** {phase['count']}")
        output.append(f"- **Average Priority Score:** {phase['avg_priority_score']}")
        output.append(f"- **Estimated Duration:** {phase['estimated_duration_days']} days")
        output.append(f"- **Parallel Track:** {'Yes' if phase['parallel_track'] else 'No'}")

        # Criticality breakdown
        breakdown = phase['criticality_breakdown']
        output.append(f"- **Criticality Breakdown:**")
        for level, count in sorted(breakdown.items(), key=lambda x: ['critical', 'high', 'medium', 'low'].index(x[0]) if x[0] in ['critical', 'high', 'medium', 'low'] else 99):
            output.append(f"  - {level.capitalize()}: {count}")

        # Show first 5 parcel IDs
        parcel_ids = phase['parcels'][:5]
        if len(phase['parcels']) > 5:
            parcel_ids_str = ', '.join(parcel_ids) + f' ... (+{len(phase["parcels"]) - 5} more)'
        else:
            parcel_ids_str = ', '.join(parcel_ids)
        output.append(f"- **Sample Parcels:** {parcel_ids_str}")

    # Parallel tracks
    if phasing_result.get('parallel_tracks'):
        output.append("\n### Parallel Acquisition Tracks\n")
        for track in phasing_result['parallel_tracks']:
            output.append(f"**{track['track_name']}:** {track['rationale']}")
            output.append(f"- Parcels: {', '.join(track['parcels'])}\n")

    # Top priority parcels
    if phasing_result.get('scored_parcels'):
        output.append("\n### Top 10 Priority Parcels\n")
        output.append("| Rank | Parcel ID | Priority Score | Criticality | Holdout Risk | Complexity |")
        output.append("|------|-----------|----------------|-------------|--------------|------------|")

        for i, parcel in enumerate(phasing_result['scored_parcels'][:10], 1):
            output.append(
                f"| {i} | {parcel['id']} | {parcel['priority_score']:.1f} | "
                f"{parcel.get('criticality', 'N/A')} | {parcel.get('holdout_risk', 0):.2f} | "
                f"{parcel.get('complexity', 'N/A')} |"
            )

    return '\n'.join(output)


def get_phase_for_parcel(parcel_id: str, phasing_result: Dict) -> int:
    """
    Get the phase number for a specific parcel.

    Args:
        parcel_id: Parcel ID to lookup
        phasing_result: Result from calculate_phasing_strategy

    Returns:
        Phase number (1-4) or 0 if not found
    """
    for phase in phasing_result['phases']:
        if parcel_id in phase['parcels']:
            return phase['phase']
    return 0


def get_critical_path_parcels(phasing_result: Dict) -> List[str]:
    """
    Extract critical path parcels (Phase 1).

    Args:
        phasing_result: Result from calculate_phasing_strategy

    Returns:
        List of critical parcel IDs
    """
    for phase in phasing_result['phases']:
        if phase['phase'] == 1:
            return phase['parcels']
    return []
