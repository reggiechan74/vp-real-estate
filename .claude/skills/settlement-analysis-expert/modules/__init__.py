"""
Settlement Analysis Calculator Modules
Modular components for settlement scenario analysis.
"""

from .validators import validate_input, validate_probabilities
from .calculations import (
    calculate_settlement_scenarios,
    calculate_hearing_expected_value,
    calculate_net_benefit
)
from .analysis import (
    analyze_settlement_vs_hearing,
    calculate_zopa_analysis,
    generate_concession_strategy
)
from .output_formatters import (
    format_analysis_report,
    format_executive_summary,
    format_scenario_comparison
)

__all__ = [
    # Validators
    'validate_input',
    'validate_probabilities',

    # Calculations
    'calculate_settlement_scenarios',
    'calculate_hearing_expected_value',
    'calculate_net_benefit',

    # Analysis
    'analyze_settlement_vs_hearing',
    'calculate_zopa_analysis',
    'generate_concession_strategy',

    # Output Formatters
    'format_analysis_report',
    'format_executive_summary',
    'format_scenario_comparison'
]
