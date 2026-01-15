"""
Stakeholder Management Expert - Modules Package
Provides validation, NLP processing, and output formatting for consultation analysis.
"""

from .validators import (
    validate_input,
    validate_demographics,
    validate_output_options
)

from .nlp_processing import (
    extract_key_phrases,
    identify_emotion_indicators,
    calculate_reading_level,
    analyze_question_statements,
    detect_suggestion_vs_concern
)

from .output_formatters import (
    format_markdown_report,
    format_json_output
)

__all__ = [
    # Validators
    'validate_input',
    'validate_demographics',
    'validate_output_options',

    # NLP Processing
    'extract_key_phrases',
    'identify_emotion_indicators',
    'calculate_reading_level',
    'analyze_question_statements',
    'detect_suggestion_vs_concern',

    # Output Formatters
    'format_markdown_report',
    'format_json_output'
]
