"""Board Memo Expert Modules"""

from .validators import (
    validate_financial_breakdown,
    validate_risk_assessment,
    validate_governance_requirements,
    validate_complete_input,
    validate_npv_inputs
)

from .governance import (
    generate_resolution_language,
    format_approval_recommendation,
    format_compliance_requirements,
    format_authority_limits,
    format_stakeholder_consultation
)

from .output_formatters import (
    format_alternatives_analysis,
    format_timeline_section,
    format_npv_analysis,
    format_payback_analysis,
    format_metadata_header,
    format_urgency_indicator,
    format_funding_source_detail,
    format_background_section
)

__all__ = [
    # Validators
    'validate_financial_breakdown',
    'validate_risk_assessment',
    'validate_governance_requirements',
    'validate_complete_input',
    'validate_npv_inputs',
    # Governance
    'generate_resolution_language',
    'format_approval_recommendation',
    'format_compliance_requirements',
    'format_authority_limits',
    'format_stakeholder_consultation',
    # Output Formatters
    'format_alternatives_analysis',
    'format_timeline_section',
    'format_npv_analysis',
    'format_payback_analysis',
    'format_metadata_header',
    'format_urgency_indicator',
    'format_funding_source_detail',
    'format_background_section'
]
