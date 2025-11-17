#!/usr/bin/env python3
"""
Timeline Utilities Module
Provides shared functions for critical path analysis, PERT/CPM scheduling,
resource allocation, and timeline risk assessment.

Used by:
- project_timeline_calculator.py
- timeline_generator.py
- land_assembly_calculator.py
"""

from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque


def calculate_critical_path(
    tasks: List[Dict],
    dependencies: List[Tuple[str, str]]
) -> Dict:
    """
    Calculate critical path using PERT/CPM methodology.

    Args:
        tasks: List of task dicts
            [
                {
                    'id': 'A',
                    'name': 'Obtain approval',
                    'duration': 30,  # days
                    'optimistic': 20,
                    'most_likely': 30,
                    'pessimistic': 45
                },
                ...
            ]
        dependencies: List of (predecessor, successor) tuples
            [('A', 'B'), ('A', 'C'), ('B', 'D'), ...]

    Returns:
        Dict containing critical path analysis
            {
                'critical_path': ['A', 'B', 'D', 'F'],
                'project_duration': 120,
                'task_details': {
                    'A': {
                        'early_start': 0,
                        'early_finish': 30,
                        'late_start': 0,
                        'late_finish': 30,
                        'total_float': 0,
                        'is_critical': True
                    },
                    ...
                }
            }
    """
    # Build task dict for easy lookup
    task_dict = {task['id']: task for task in tasks}

    # Build adjacency lists
    successors = defaultdict(list)
    predecessors = defaultdict(list)
    for pred, succ in dependencies:
        successors[pred].append(succ)
        predecessors[succ].append(pred)

    # Forward pass - calculate early start/finish
    early_start = {}
    early_finish = {}
    task_order = _topological_sort(tasks, dependencies)

    for task_id in task_order:
        task = task_dict[task_id]
        duration = task.get('duration', 0)

        # Early start is max of predecessor early finishes
        if task_id in predecessors and predecessors[task_id]:
            early_start[task_id] = max(
                early_finish[pred] for pred in predecessors[task_id]
            )
        else:
            early_start[task_id] = 0

        early_finish[task_id] = early_start[task_id] + duration

    # Project duration is max early finish
    project_duration = max(early_finish.values()) if early_finish else 0

    # Backward pass - calculate late start/finish
    late_start = {}
    late_finish = {}

    for task_id in reversed(task_order):
        task = task_dict[task_id]
        duration = task.get('duration', 0)

        # Late finish is min of successor late starts
        if task_id in successors and successors[task_id]:
            late_finish[task_id] = min(
                late_start[succ] for succ in successors[task_id]
            )
        else:
            late_finish[task_id] = project_duration

        late_start[task_id] = late_finish[task_id] - duration

    # Calculate float and identify critical path
    task_details = {}
    critical_tasks = []

    for task_id in task_dict:
        total_float = late_start[task_id] - early_start[task_id]
        is_critical = abs(total_float) < 0.01  # Floating point tolerance

        if is_critical:
            critical_tasks.append(task_id)

        task_details[task_id] = {
            'name': task_dict[task_id].get('name'),
            'duration': task_dict[task_id].get('duration'),
            'early_start': round(early_start[task_id], 2),
            'early_finish': round(early_finish[task_id], 2),
            'late_start': round(late_start[task_id], 2),
            'late_finish': round(late_finish[task_id], 2),
            'total_float': round(total_float, 2),
            'free_float': round(_calculate_free_float(
                task_id, early_finish, successors, early_start
            ), 2),
            'is_critical': is_critical
        }

    # Build critical path sequence
    critical_path = _build_critical_path_sequence(
        critical_tasks, dependencies, task_order
    )

    return {
        'critical_path': critical_path,
        'project_duration': round(project_duration, 2),
        'task_details': task_details,
        'num_critical_tasks': len(critical_tasks),
        'num_total_tasks': len(tasks),
        'critical_path_percentage': round(
            len(critical_tasks) / len(tasks) * 100, 1
        ) if tasks else 0
    }


def _topological_sort(tasks: List[Dict], dependencies: List[Tuple[str, str]]) -> List[str]:
    """Topological sort using Kahn's algorithm."""
    # Build adjacency list and in-degree count
    successors = defaultdict(list)
    in_degree = {task['id']: 0 for task in tasks}

    for pred, succ in dependencies:
        successors[pred].append(succ)
        in_degree[succ] = in_degree.get(succ, 0) + 1

    # Start with tasks that have no predecessors
    queue = deque([task['id'] for task in tasks if in_degree[task['id']] == 0])
    result = []

    while queue:
        task_id = queue.popleft()
        result.append(task_id)

        for successor in successors[task_id]:
            in_degree[successor] -= 1
            if in_degree[successor] == 0:
                queue.append(successor)

    return result


def _calculate_free_float(
    task_id: str,
    early_finish: Dict[str, float],
    successors: Dict[str, List[str]],
    early_start: Dict[str, float]
) -> float:
    """Calculate free float for a task."""
    if task_id not in successors or not successors[task_id]:
        return 0  # No successors = free float is 0

    min_successor_early_start = min(
        early_start[succ] for succ in successors[task_id]
    )
    return min_successor_early_start - early_finish[task_id]


def _build_critical_path_sequence(
    critical_tasks: List[str],
    dependencies: List[Tuple[str, str]],
    task_order: List[str]
) -> List[str]:
    """Build ordered sequence of critical path tasks."""
    # Build dependency graph for critical tasks only
    critical_set = set(critical_tasks)
    critical_deps = [
        (pred, succ) for pred, succ in dependencies
        if pred in critical_set and succ in critical_set
    ]

    # Build successors map for critical tasks
    successors = defaultdict(list)
    for pred, succ in critical_deps:
        successors[pred].append(succ)

    # Find start task (no predecessors among critical tasks)
    predecessors = set(succ for _, succ in critical_deps)
    start_tasks = [t for t in critical_tasks if t not in predecessors]

    if not start_tasks:
        return sorted(critical_tasks)  # Fallback

    # Follow path from start
    path = []
    current = start_tasks[0]
    visited = set()

    while current and current not in visited:
        path.append(current)
        visited.add(current)
        # Move to successor
        if current in successors:
            current = successors[current][0] if successors[current] else None
        else:
            current = None

    return path


def calculate_resource_requirements(
    timeline: Dict,
    task_resources: Dict[str, Dict]
) -> Dict:
    """
    Calculate resource requirements by phase (staff, consultants, budget).

    Args:
        timeline: Timeline dict from calculate_critical_path()
        task_resources: Dict mapping task_id to resource requirements
            {
                'A': {
                    'staff': 2,
                    'consultants': {'legal': 1, 'appraisal': 0},
                    'budget': 50000
                },
                ...
            }

    Returns:
        Dict containing resource allocation analysis
            {
                'total_resources': {...},
                'peak_resources': {...},
                'resource_timeline': [...],
                'cost_by_phase': {...}
            }
    """
    task_details = timeline.get('task_details', {})

    # Calculate resources over time
    resource_timeline = []
    total_staff_days = 0
    total_budget = 0
    consultant_usage = defaultdict(float)

    for task_id, details in task_details.items():
        if task_id not in task_resources:
            continue

        resources = task_resources[task_id]
        duration = details['duration']

        # Accumulate totals
        staff = resources.get('staff', 0)
        total_staff_days += staff * duration
        total_budget += resources.get('budget', 0)

        # Track consultant usage
        for consultant_type, count in resources.get('consultants', {}).items():
            consultant_usage[consultant_type] += count * duration

        # Add to timeline
        resource_timeline.append({
            'task_id': task_id,
            'task_name': details['name'],
            'start': details['early_start'],
            'finish': details['early_finish'],
            'duration': duration,
            'staff': staff,
            'consultants': resources.get('consultants', {}),
            'budget': resources.get('budget', 0),
            'is_critical': details['is_critical']
        })

    # Sort by start time
    resource_timeline.sort(key=lambda x: x['start'])

    # Find peak resource usage
    peak_staff = max((r['staff'] for r in resource_timeline), default=0)
    peak_consultants = {}
    for r in resource_timeline:
        for cons_type, count in r.get('consultants', {}).items():
            peak_consultants[cons_type] = max(
                peak_consultants.get(cons_type, 0), count
            )

    return {
        'total_resources': {
            'staff_days': round(total_staff_days, 2),
            'budget': round(total_budget, 2),
            'consultant_days': {k: round(v, 2) for k, v in consultant_usage.items()}
        },
        'peak_resources': {
            'staff': peak_staff,
            'consultants': peak_consultants
        },
        'resource_timeline': resource_timeline,
        'project_duration': timeline.get('project_duration', 0)
    }


def identify_risk_flags(
    timeline: Dict,
    deadlines: Dict[str, float],
    buffer_days: int = 10
) -> List[Dict]:
    """
    Flag timeline risks (tight statutory deadlines, approval delays).

    Args:
        timeline: Timeline dict from calculate_critical_path()
        deadlines: Dict mapping task_id to absolute deadline (days from start)
            {'A': 30, 'B': 90, ...}
        buffer_days: Minimum buffer days required (default 10)

    Returns:
        List of risk flags
            [
                {
                    'task_id': 'B',
                    'task_name': 'Form 2 service',
                    'risk_type': 'TIGHT_DEADLINE',
                    'severity': 'HIGH',
                    'late_finish': 92,
                    'deadline': 90,
                    'buffer': -2,
                    'message': 'Task finishes 2 days after statutory deadline'
                },
                ...
            ]
    """
    task_details = timeline.get('task_details', {})
    risks = []

    for task_id, details in task_details.items():
        # Check against absolute deadlines
        if task_id in deadlines:
            deadline = deadlines[task_id]
            late_finish = details['late_finish']
            buffer = deadline - late_finish

            if buffer < buffer_days:
                severity = 'CRITICAL' if buffer < 0 else 'HIGH' if buffer < 5 else 'MEDIUM'
                message = (
                    f"Task finishes {abs(buffer):.0f} days {'after' if buffer < 0 else 'before'} "
                    f"statutory deadline"
                )

                risks.append({
                    'task_id': task_id,
                    'task_name': details['name'],
                    'risk_type': 'TIGHT_DEADLINE',
                    'severity': severity,
                    'late_finish': late_finish,
                    'deadline': deadline,
                    'buffer': round(buffer, 2),
                    'message': message
                })

        # Check critical path tasks with no float
        if details['is_critical'] and details['total_float'] == 0:
            risks.append({
                'task_id': task_id,
                'task_name': details['name'],
                'risk_type': 'CRITICAL_PATH_NO_FLOAT',
                'severity': 'MEDIUM',
                'total_float': 0,
                'message': 'Critical path task with zero schedule flexibility'
            })

        # Check tasks with very long durations (potential delay risk)
        if details['duration'] > 60:  # More than 2 months
            risks.append({
                'task_id': task_id,
                'task_name': details['name'],
                'risk_type': 'LONG_DURATION',
                'severity': 'LOW',
                'duration': details['duration'],
                'message': f"Task duration {details['duration']:.0f} days - monitor for delays"
            })

    # Sort by severity
    severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    risks.sort(key=lambda r: severity_order.get(r['severity'], 99))

    return risks


def calculate_float(task: Dict, critical_path: Dict) -> Dict:
    """
    Calculate total float and free float for tasks.

    Args:
        task: Task dict with id
        critical_path: Critical path dict from calculate_critical_path()

    Returns:
        Dict containing float analysis
    """
    task_id = task.get('id')
    task_details = critical_path.get('task_details', {}).get(task_id, {})

    return {
        'task_id': task_id,
        'task_name': task_details.get('name'),
        'total_float': task_details.get('total_float', 0),
        'free_float': task_details.get('free_float', 0),
        'is_critical': task_details.get('is_critical', False),
        'flexibility': 'None' if task_details.get('is_critical') else
                      'Low' if task_details.get('total_float', 0) < 5 else
                      'Medium' if task_details.get('total_float', 0) < 15 else 'High'
    }


def scenario_analysis(
    base_timeline: Dict,
    scenarios: Dict[str, float]
) -> Dict:
    """
    Best case / likely / worst case timeline scenarios.

    Args:
        base_timeline: Base timeline dict from calculate_critical_path()
        scenarios: Dict with scenario adjustments
            {
                'best_case': 0.8,     # 20% faster
                'likely_case': 1.0,   # Base case
                'worst_case': 1.3     # 30% slower
            }

    Returns:
        Dict containing scenario analysis
            {
                'best_case': {'duration': 96, 'variance': -24},
                'likely_case': {'duration': 120, 'variance': 0},
                'worst_case': {'duration': 156, 'variance': 36},
                'range': 60,
                'probability_weighted_duration': 127.2
            }
    """
    base_duration = base_timeline.get('project_duration', 0)

    results = {}
    for scenario_name, multiplier in scenarios.items():
        scenario_duration = base_duration * multiplier
        variance = scenario_duration - base_duration

        results[scenario_name] = {
            'duration': round(scenario_duration, 2),
            'variance': round(variance, 2),
            'variance_pct': round((variance / base_duration) * 100, 1) if base_duration > 0 else 0
        }

    # Calculate range
    durations = [r['duration'] for r in results.values()]
    duration_range = max(durations) - min(durations)

    # Probability-weighted duration (assume triangular distribution)
    # Best: 20%, Likely: 60%, Worst: 20%
    prob_weights = {
        'best_case': 0.2,
        'likely_case': 0.6,
        'worst_case': 0.2
    }

    weighted_duration = sum(
        results[scenario]['duration'] * prob_weights.get(scenario, 0)
        for scenario in results
    )

    return {
        **results,
        'range': round(duration_range, 2),
        'probability_weighted_duration': round(weighted_duration, 2),
        'confidence_interval_90pct': {
            'lower': round(results.get('best_case', {}).get('duration', 0), 2),
            'upper': round(results.get('worst_case', {}).get('duration', 0), 2)
        }
    }
