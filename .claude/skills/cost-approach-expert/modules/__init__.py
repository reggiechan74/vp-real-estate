"""
Infrastructure Cost Calculator - Modular Components

Provides specialized modules for cost approach valuation:
- validators: Input validation and schema verification
- replacement_cost: Replacement cost new (RCN) estimation
- depreciation_analysis: Physical, functional, and external obsolescence
- cost_reconciliation: Reconcile with market approach
- output_formatters: Report formatting and generation
"""

from .validators import validate_input, validate_construction_costs
from .replacement_cost import calculate_replacement_cost_new
from .depreciation_analysis import (
    calculate_physical_depreciation,
    calculate_functional_obsolescence,
    calculate_external_obsolescence,
    calculate_total_depreciation
)
from .cost_reconciliation import reconcile_with_market
from .output_formatters import format_cost_report, format_summary_table

__all__ = [
    'validate_input',
    'validate_construction_costs',
    'calculate_replacement_cost_new',
    'calculate_physical_depreciation',
    'calculate_functional_obsolescence',
    'calculate_external_obsolescence',
    'calculate_total_depreciation',
    'reconcile_with_market',
    'format_cost_report',
    'format_summary_table'
]
