"""
Shared Financial Utilities

Common financial calculation functions used across all lease analysis calculators.

Modules:
- financial_utils: NPV, IRR, PV, rate conversions, ratios, statistics, amortization

Author: Claude Code
Created: 2025-10-30
"""

from .financial_utils import (
    # Present value
    present_value,
    pv_annuity,

    # NPV and IRR
    npv,
    irr,

    # Rate conversions
    annual_to_monthly_rate,
    monthly_to_annual_rate,
    effective_annual_rate,

    # Annuity
    annuity_factor,

    # Interest and amortization
    simple_interest,
    amortization_schedule,

    # Financial ratios
    safe_divide,
    calculate_financial_ratios,

    # Statistics
    percentile_rank,
    variance_analysis,
    descriptive_statistics,

    # Date utilities
    months_between,
    add_months
)

__all__ = [
    'present_value',
    'pv_annuity',
    'npv',
    'irr',
    'annual_to_monthly_rate',
    'monthly_to_annual_rate',
    'effective_annual_rate',
    'annuity_factor',
    'simple_interest',
    'amortization_schedule',
    'safe_divide',
    'calculate_financial_ratios',
    'percentile_rank',
    'variance_analysis',
    'descriptive_statistics',
    'months_between',
    'add_months'
]
