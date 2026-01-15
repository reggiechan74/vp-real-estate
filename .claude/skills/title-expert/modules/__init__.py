"""
Title Analyzer Modules

Modular components for title search analysis and marketability assessment.
"""

__version__ = "1.0.0"

# Import key functions for easy access
from .validators import load_and_validate_input
from .title_parsing import parse_registered_instruments, classify_instrument
from .encumbrance_analysis import analyze_encumbrances, assess_priority
from .registration_validation import validate_registration, detect_defects
from .marketability_assessment import assess_marketability, calculate_value_impact
from .output_formatters import (
    generate_markdown_report,
    generate_json_output,
    save_markdown_report,
    save_json_output
)

__all__ = [
    'load_and_validate_input',
    'parse_registered_instruments',
    'classify_instrument',
    'analyze_encumbrances',
    'assess_priority',
    'validate_registration',
    'detect_defects',
    'assess_marketability',
    'calculate_value_impact',
    'generate_markdown_report',
    'generate_json_output',
    'save_markdown_report',
    'save_json_output'
]
