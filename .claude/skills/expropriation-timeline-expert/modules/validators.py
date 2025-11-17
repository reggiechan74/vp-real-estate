#!/usr/bin/env python3
"""
Input Validation Module
Validates timeline input data against schema requirements.
"""

from typing import Dict, List, Set, Tuple
from datetime import datetime


def validate_timeline_input(data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate complete timeline input data.

    Args:
        data: Timeline input dict

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Required fields
    required = ['project_name', 'approval_date', 'tasks', 'dependencies']
    for field in required:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    if errors:
        return False, errors

    # Validate tasks
    tasks_valid, task_errors = validate_tasks(data.get('tasks', []))
    errors.extend(task_errors)

    # Validate dependencies
    task_ids = {task['id'] for task in data.get('tasks', [])}
    deps_valid, dep_errors = validate_dependencies(
        data.get('dependencies', []),
        task_ids
    )
    errors.extend(dep_errors)

    # Validate approval date
    try:
        datetime.fromisoformat(data['approval_date'])
    except (ValueError, KeyError):
        errors.append(f"Invalid approval_date format: {data.get('approval_date')}")

    # Validate statutory deadlines
    if 'statutory_deadlines' in data:
        deadline_errors = validate_deadlines(
            data['statutory_deadlines'],
            task_ids
        )
        errors.extend(deadline_errors)

    return len(errors) == 0, errors


def validate_tasks(tasks: List[Dict]) -> Tuple[bool, List[str]]:
    """
    Validate task list.

    Args:
        tasks: List of task dicts

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    if not tasks:
        errors.append("Tasks list is empty")
        return False, errors

    task_ids = set()

    for idx, task in enumerate(tasks):
        # Check required fields
        required = ['id', 'name', 'duration']
        for field in required:
            if field not in task:
                errors.append(f"Task {idx}: Missing required field '{field}'")

        # Check task ID uniqueness
        task_id = task.get('id')
        if task_id:
            if task_id in task_ids:
                errors.append(f"Duplicate task ID: {task_id}")
            task_ids.add(task_id)

        # Validate duration
        duration = task.get('duration')
        if duration is not None and duration < 0:
            errors.append(f"Task {task_id}: Duration cannot be negative: {duration}")

        # Validate PERT estimates if provided
        if 'optimistic' in task or 'most_likely' in task or 'pessimistic' in task:
            pert_errors = validate_pert_estimates(task)
            errors.extend([f"Task {task_id}: {err}" for err in pert_errors])

        # Validate resources if provided
        if 'resources' in task:
            resource_errors = validate_resources(task['resources'])
            errors.extend([f"Task {task_id}: {err}" for err in resource_errors])

    return len(errors) == 0, errors


def validate_pert_estimates(task: Dict) -> List[str]:
    """
    Validate PERT time estimates.

    Args:
        task: Task dict with PERT estimates

    Returns:
        List of error messages
    """
    errors = []

    # Check all three are provided
    pert_fields = ['optimistic', 'most_likely', 'pessimistic']
    present = [f for f in pert_fields if f in task]

    if present and len(present) != 3:
        errors.append(f"PERT estimates must include all three values: {pert_fields}")
        return errors

    if len(present) == 3:
        opt = task['optimistic']
        likely = task['most_likely']
        pess = task['pessimistic']

        # Check values are non-negative
        if opt < 0 or likely < 0 or pess < 0:
            errors.append("PERT estimates cannot be negative")

        # Check ordering: optimistic <= most_likely <= pessimistic
        if not (opt <= likely <= pess):
            errors.append(
                f"PERT estimates must satisfy: optimistic ({opt}) <= "
                f"most_likely ({likely}) <= pessimistic ({pess})"
            )

    return errors


def validate_resources(resources: Dict) -> List[str]:
    """
    Validate resource requirements.

    Args:
        resources: Resources dict

    Returns:
        List of error messages
    """
    errors = []

    # Validate staff count
    if 'staff' in resources:
        if not isinstance(resources['staff'], int):
            errors.append(f"Staff must be integer: {resources['staff']}")
        elif resources['staff'] < 0:
            errors.append(f"Staff cannot be negative: {resources['staff']}")

    # Validate consultants
    if 'consultants' in resources:
        if not isinstance(resources['consultants'], dict):
            errors.append("Consultants must be a dictionary")
        else:
            for cons_type, count in resources['consultants'].items():
                if not isinstance(count, int):
                    errors.append(f"Consultant count for '{cons_type}' must be integer: {count}")
                elif count < 0:
                    errors.append(f"Consultant count for '{cons_type}' cannot be negative: {count}")

    # Validate budget
    if 'budget' in resources:
        if not isinstance(resources['budget'], (int, float)):
            errors.append(f"Budget must be numeric: {resources['budget']}")
        elif resources['budget'] < 0:
            errors.append(f"Budget cannot be negative: {resources['budget']}")

    return errors


def validate_dependencies(
    dependencies: List[List[str]],
    valid_task_ids: Set[str]
) -> Tuple[bool, List[str]]:
    """
    Validate task dependencies.

    Args:
        dependencies: List of [predecessor, successor] pairs
        valid_task_ids: Set of valid task IDs

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    for idx, dep in enumerate(dependencies):
        # Check format
        if not isinstance(dep, (list, tuple)) or len(dep) != 2:
            errors.append(f"Dependency {idx}: Must be [predecessor, successor] pair: {dep}")
            continue

        pred, succ = dep

        # Check task IDs exist
        if pred not in valid_task_ids:
            errors.append(f"Dependency {idx}: Unknown predecessor task: {pred}")
        if succ not in valid_task_ids:
            errors.append(f"Dependency {idx}: Unknown successor task: {succ}")

        # Check self-dependency
        if pred == succ:
            errors.append(f"Dependency {idx}: Task cannot depend on itself: {pred}")

    # Check for circular dependencies
    if not errors:
        circular_errors = check_circular_dependencies(dependencies, valid_task_ids)
        errors.extend(circular_errors)

    return len(errors) == 0, errors


def check_circular_dependencies(
    dependencies: List[List[str]],
    task_ids: Set[str]
) -> List[str]:
    """
    Check for circular dependency chains.

    Args:
        dependencies: List of [predecessor, successor] pairs
        task_ids: Set of all task IDs

    Returns:
        List of error messages
    """
    from collections import defaultdict, deque

    errors = []

    # Build adjacency list
    graph = defaultdict(list)
    in_degree = {task_id: 0 for task_id in task_ids}

    for pred, succ in dependencies:
        graph[pred].append(succ)
        in_degree[succ] = in_degree.get(succ, 0) + 1

    # Topological sort using Kahn's algorithm
    queue = deque([task_id for task_id in task_ids if in_degree[task_id] == 0])
    processed = []

    while queue:
        task_id = queue.popleft()
        processed.append(task_id)

        for successor in graph[task_id]:
            in_degree[successor] -= 1
            if in_degree[successor] == 0:
                queue.append(successor)

    # If not all tasks processed, there's a cycle
    if len(processed) != len(task_ids):
        unprocessed = task_ids - set(processed)
        errors.append(f"Circular dependency detected involving tasks: {sorted(unprocessed)}")

    return errors


def validate_deadlines(
    deadlines: Dict[str, float],
    valid_task_ids: Set[str]
) -> List[str]:
    """
    Validate statutory deadlines.

    Args:
        deadlines: Dict mapping task_id to deadline (days from start)
        valid_task_ids: Set of valid task IDs

    Returns:
        List of error messages
    """
    errors = []

    for task_id, deadline in deadlines.items():
        # Check task ID exists
        if task_id not in valid_task_ids:
            errors.append(f"Deadline for unknown task: {task_id}")

        # Check deadline is positive
        if deadline < 0:
            errors.append(f"Deadline for task {task_id} cannot be negative: {deadline}")

    return errors
