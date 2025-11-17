#!/usr/bin/env python3
"""
Critical Path Method (CPM) Module
Implements PERT/CPM critical path analysis using shared timeline utilities.
"""

import sys
from pathlib import Path
from typing import Dict, List

# Add Shared_Utils to path
shared_utils_path = Path(__file__).resolve().parents[4] / 'Shared_Utils'
if str(shared_utils_path) not in sys.path:
    sys.path.insert(0, str(shared_utils_path))

import timeline_utils
calc_cp = timeline_utils.calculate_critical_path


def calculate_critical_path_analysis(tasks: List[Dict], dependencies: List[List[str]]) -> Dict:
    """
    Calculate critical path using PERT/CPM methodology.

    Delegates to Shared_Utils/timeline_utils.py for computation.

    Args:
        tasks: List of task dicts with id, name, duration
        dependencies: List of [predecessor, successor] pairs

    Returns:
        Critical path analysis dict
    """
    # Convert dependencies to tuple format expected by shared utility
    dep_tuples = [(pred, succ) for pred, succ in dependencies]

    # Calculate using shared utility
    return calc_cp(tasks, dep_tuples)


def calculate_pert_estimates(task: Dict) -> float:
    """
    Calculate PERT expected time: (optimistic + 4*most_likely + pessimistic) / 6

    Args:
        task: Task dict with optimistic, most_likely, pessimistic

    Returns:
        PERT expected time (weighted average)
    """
    if all(k in task for k in ['optimistic', 'most_likely', 'pessimistic']):
        opt = task['optimistic']
        likely = task['most_likely']
        pess = task['pessimistic']

        # PERT expected time formula
        expected = (opt + 4 * likely + pess) / 6
        return round(expected, 2)

    # Fall back to deterministic duration
    return task.get('duration', 0)


def calculate_pert_variance(task: Dict) -> float:
    """
    Calculate PERT variance: ((pessimistic - optimistic) / 6)^2

    Args:
        task: Task dict with optimistic, pessimistic

    Returns:
        PERT variance
    """
    if 'optimistic' in task and 'pessimistic' in task:
        opt = task['optimistic']
        pess = task['pessimistic']

        # PERT variance formula
        variance = ((pess - opt) / 6) ** 2
        return round(variance, 4)

    return 0.0


def calculate_pert_standard_deviation(task: Dict) -> float:
    """
    Calculate PERT standard deviation: (pessimistic - optimistic) / 6

    Args:
        task: Task dict with optimistic, pessimistic

    Returns:
        PERT standard deviation
    """
    if 'optimistic' in task and 'pessimistic' in task:
        opt = task['optimistic']
        pess = task['pessimistic']

        # PERT std dev formula
        std_dev = (pess - opt) / 6
        return round(std_dev, 2)

    return 0.0


def enrich_tasks_with_pert(tasks: List[Dict]) -> List[Dict]:
    """
    Enrich tasks with PERT calculations.

    Calculates expected time, variance, and standard deviation for each task.
    Updates task 'duration' to PERT expected time if PERT estimates provided.

    Args:
        tasks: List of task dicts

    Returns:
        Enriched task list (modifies in place)
    """
    for task in tasks:
        # Calculate PERT metrics
        expected_time = calculate_pert_estimates(task)
        variance = calculate_pert_variance(task)
        std_dev = calculate_pert_standard_deviation(task)

        # Store PERT metrics
        task['pert_expected_time'] = expected_time
        task['pert_variance'] = variance
        task['pert_std_dev'] = std_dev

        # Use PERT expected time as duration if PERT estimates provided
        if all(k in task for k in ['optimistic', 'most_likely', 'pessimistic']):
            task['duration'] = expected_time

    return tasks


def calculate_project_variance(critical_path: List[str], task_dict: Dict[str, Dict]) -> float:
    """
    Calculate total project variance (sum of critical path task variances).

    Args:
        critical_path: List of critical path task IDs
        task_dict: Dict mapping task_id to task dict

    Returns:
        Total project variance
    """
    total_variance = 0.0

    for task_id in critical_path:
        task = task_dict.get(task_id, {})
        total_variance += task.get('pert_variance', 0.0)

    return round(total_variance, 4)


def calculate_project_confidence_interval(
    project_duration: float,
    project_variance: float,
    confidence_level: float = 0.90
) -> Dict:
    """
    Calculate project completion confidence interval.

    Uses normal distribution approximation (valid for large projects).

    Args:
        project_duration: Expected project duration (PERT)
        project_variance: Project variance (sum of critical path variances)
        confidence_level: Confidence level (0.90 = 90%, 0.95 = 95%)

    Returns:
        Dict with lower/upper bounds and probability
    """
    import math

    # Z-scores for common confidence levels
    z_scores = {
        0.90: 1.645,  # 90% confidence
        0.95: 1.960,  # 95% confidence
        0.99: 2.576   # 99% confidence
    }

    z = z_scores.get(confidence_level, 1.645)
    std_dev = math.sqrt(project_variance)

    lower_bound = project_duration - (z * std_dev)
    upper_bound = project_duration + (z * std_dev)

    return {
        'expected_duration': round(project_duration, 2),
        'standard_deviation': round(std_dev, 2),
        'confidence_level': confidence_level,
        'lower_bound': round(lower_bound, 2),
        'upper_bound': round(upper_bound, 2),
        'range': round(upper_bound - lower_bound, 2)
    }
