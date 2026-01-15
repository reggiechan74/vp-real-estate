"""
Expropriation Timeline Expert - Modules Package

Provides modular components for critical path analysis with statutory deadline integration.
"""

from .validators import validate_timeline_input, validate_tasks, validate_dependencies
from .critical_path import (
    calculate_critical_path_analysis,
    enrich_tasks_with_pert,
    calculate_project_variance,
    calculate_project_confidence_interval
)
from .dependencies import (
    build_dependency_graph,
    find_predecessors,
    find_successors,
    analyze_dependency_complexity
)
from .statutory_deadlines import (
    calculate_registration_deadline,
    calculate_form_2_service_date,
    calculate_form_7_service_date,
    calculate_days_remaining,
    assess_deadline_risk,
    generate_oea_timeline_milestones
)
from .output_formatters import (
    format_timeline_report,
    format_json_output,
    generate_output_filename
)

__all__ = [
    # Validators
    'validate_timeline_input',
    'validate_tasks',
    'validate_dependencies',

    # Critical Path
    'calculate_critical_path_analysis',
    'enrich_tasks_with_pert',
    'calculate_project_variance',
    'calculate_project_confidence_interval',

    # Dependencies
    'build_dependency_graph',
    'find_predecessors',
    'find_successors',
    'analyze_dependency_complexity',

    # Statutory Deadlines
    'calculate_registration_deadline',
    'calculate_form_2_service_date',
    'calculate_form_7_service_date',
    'calculate_days_remaining',
    'assess_deadline_risk',
    'generate_oea_timeline_milestones',

    # Output Formatters
    'format_timeline_report',
    'format_json_output',
    'generate_output_filename',
]
