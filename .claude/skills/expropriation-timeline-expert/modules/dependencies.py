#!/usr/bin/env python3
"""
Dependency Resolution Module
Handles task dependency analysis and relationship tracking.
"""

from typing import Dict, List, Set
from collections import defaultdict


def build_dependency_graph(dependencies: List[List[str]]) -> Dict[str, List[str]]:
    """
    Build adjacency list for task dependencies.

    Args:
        dependencies: List of [predecessor, successor] pairs

    Returns:
        Dict mapping task_id to list of successor task_ids
    """
    graph = defaultdict(list)

    for pred, succ in dependencies:
        graph[pred].append(succ)

    return dict(graph)


def find_predecessors(task_id: str, dependencies: List[List[str]]) -> List[str]:
    """
    Find all immediate predecessors of a task.

    Args:
        task_id: Task ID to find predecessors for
        dependencies: List of [predecessor, successor] pairs

    Returns:
        List of predecessor task IDs
    """
    predecessors = []

    for pred, succ in dependencies:
        if succ == task_id:
            predecessors.append(pred)

    return predecessors


def find_successors(task_id: str, dependencies: List[List[str]]) -> List[str]:
    """
    Find all immediate successors of a task.

    Args:
        task_id: Task ID to find successors for
        dependencies: List of [predecessor, successor] pairs

    Returns:
        List of successor task IDs
    """
    successors = []

    for pred, succ in dependencies:
        if pred == task_id:
            successors.append(succ)

    return successors


def find_all_ancestors(task_id: str, dependencies: List[List[str]]) -> Set[str]:
    """
    Find all ancestor tasks (transitive predecessors).

    Args:
        task_id: Task ID to find ancestors for
        dependencies: List of [predecessor, successor] pairs

    Returns:
        Set of all ancestor task IDs
    """
    ancestors = set()
    to_process = [task_id]

    while to_process:
        current = to_process.pop()
        preds = find_predecessors(current, dependencies)

        for pred in preds:
            if pred not in ancestors:
                ancestors.add(pred)
                to_process.append(pred)

    return ancestors


def find_all_descendants(task_id: str, dependencies: List[List[str]]) -> Set[str]:
    """
    Find all descendant tasks (transitive successors).

    Args:
        task_id: Task ID to find descendants for
        dependencies: List of [predecessor, successor] pairs

    Returns:
        Set of all descendant task IDs
    """
    descendants = set()
    to_process = [task_id]

    while to_process:
        current = to_process.pop()
        succs = find_successors(current, dependencies)

        for succ in succs:
            if succ not in descendants:
                descendants.add(succ)
                to_process.append(succ)

    return descendants


def identify_start_tasks(task_ids: Set[str], dependencies: List[List[str]]) -> List[str]:
    """
    Identify tasks with no predecessors (project start tasks).

    Args:
        task_ids: Set of all task IDs
        dependencies: List of [predecessor, successor] pairs

    Returns:
        List of start task IDs
    """
    has_predecessors = {succ for _, succ in dependencies}
    start_tasks = [task_id for task_id in task_ids if task_id not in has_predecessors]

    return sorted(start_tasks)


def identify_end_tasks(task_ids: Set[str], dependencies: List[List[str]]) -> List[str]:
    """
    Identify tasks with no successors (project end tasks).

    Args:
        task_ids: Set of all task IDs
        dependencies: List of [predecessor, successor] pairs

    Returns:
        List of end task IDs
    """
    has_successors = {pred for pred, _ in dependencies}
    end_tasks = [task_id for task_id in task_ids if task_id not in has_successors]

    return sorted(end_tasks)


def analyze_dependency_complexity(tasks: List[Dict], dependencies: List[List[str]]) -> Dict:
    """
    Analyze dependency complexity metrics.

    Args:
        tasks: List of task dicts
        dependencies: List of [predecessor, successor] pairs

    Returns:
        Dict with complexity metrics
    """
    task_ids = {task['id'] for task in tasks}

    # Count predecessors and successors per task
    pred_counts = defaultdict(int)
    succ_counts = defaultdict(int)

    for pred, succ in dependencies:
        pred_counts[succ] += 1
        succ_counts[pred] += 1

    # Find max
    max_preds = max(pred_counts.values()) if pred_counts else 0
    max_succs = max(succ_counts.values()) if succ_counts else 0

    # Identify bottlenecks
    bottleneck_tasks = [
        task_id for task_id in task_ids
        if pred_counts[task_id] >= 3 or succ_counts[task_id] >= 3
    ]

    return {
        'total_tasks': len(tasks),
        'total_dependencies': len(dependencies),
        'avg_dependencies_per_task': round(len(dependencies) / len(tasks), 2) if tasks else 0,
        'max_predecessors': max_preds,
        'max_successors': max_succs,
        'start_tasks': identify_start_tasks(task_ids, dependencies),
        'end_tasks': identify_end_tasks(task_ids, dependencies),
        'bottleneck_tasks': sorted(bottleneck_tasks),
        'dependency_density': round(len(dependencies) / (len(tasks) ** 2), 3) if tasks else 0
    }
