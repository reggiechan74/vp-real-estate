"""
Environmental Risk Assessment Calculator Modules

Provides modular components for environmental due diligence risk assessment:
- validators: Input validation beyond JSON schema
- environmental_assessment: Phase I/II ESA parsing and REC identification
- cleanup_cost_estimation: Cleanup cost range calculation
- regulatory_pathway: MOE approval pathway and timeline
- output_formatters: Report formatting

Author: Claude Code
Created: 2025-11-17
"""

from .validators import (
    validate_input_data,
    validate_phase_esa_data,
    validate_cleanup_scenarios
)

from .environmental_assessment import (
    parse_phase_i_findings,
    parse_phase_ii_results,
    identify_recognized_environmental_conditions,
    score_contamination_risk
)

from .cleanup_cost_estimation import (
    estimate_cleanup_costs,
    calculate_npv_cleanup_costs,
    estimate_cost_by_scenario
)

from .regulatory_pathway import (
    determine_regulatory_pathway,
    estimate_regulatory_timeline,
    generate_approval_requirements
)

from .output_formatters import (
    format_risk_summary,
    format_cleanup_cost_report,
    format_regulatory_timeline,
    format_liability_recommendations,
    generate_markdown_report
)

__all__ = [
    # Validators
    'validate_input_data',
    'validate_phase_esa_data',
    'validate_cleanup_scenarios',

    # Environmental Assessment
    'parse_phase_i_findings',
    'parse_phase_ii_results',
    'identify_recognized_environmental_conditions',
    'score_contamination_risk',

    # Cleanup Cost Estimation
    'estimate_cleanup_costs',
    'calculate_npv_cleanup_costs',
    'estimate_cost_by_scenario',

    # Regulatory Pathway
    'determine_regulatory_pathway',
    'estimate_regulatory_timeline',
    'generate_approval_requirements',

    # Output Formatters
    'format_risk_summary',
    'format_cleanup_cost_report',
    'format_regulatory_timeline',
    'format_liability_recommendations',
    'generate_markdown_report'
]
