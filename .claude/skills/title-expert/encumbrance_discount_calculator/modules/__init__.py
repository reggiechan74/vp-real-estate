"""
Encumbrance Discount Calculator Modules
Shared validation, calculation, and formatting utilities
"""

from .validators import validate_input, EncumbranceInput
from .cumulative_impact import calculate_cumulative_discount, calculate_individual_discounts
from .residual_analysis import calculate_residual_value, analyze_development_potential
from .marketability import calculate_marketability_discount, analyze_buyer_pool
from .output_formatters import format_report, format_summary_table

__all__ = [
    'validate_input',
    'EncumbranceInput',
    'calculate_cumulative_discount',
    'calculate_individual_discounts',
    'calculate_residual_value',
    'analyze_development_potential',
    'calculate_marketability_discount',
    'analyze_buyer_pool',
    'format_report',
    'format_summary_table'
]
