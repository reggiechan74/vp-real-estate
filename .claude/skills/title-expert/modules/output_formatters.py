#!/usr/bin/env python3
"""
Output Formatters Module

Generate markdown reports and JSON outputs for title analysis results.
"""

import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import pytz


def generate_markdown_report(
    property_id: str,
    property_address: str,
    parsed_instruments: Dict,
    encumbrance_analysis: Dict,
    validation_results: Dict,
    marketability: Dict,
    value_impact: Dict,
    warnings: List[str],
    data_quality: Dict
) -> str:
    """
    Generate comprehensive markdown report.

    Args:
        property_id: Property identifier
        property_address: Property address
        parsed_instruments: Parsed instruments results
        encumbrance_analysis: Encumbrance analysis results
        validation_results: Registration validation results
        marketability: Marketability assessment results
        value_impact: Value impact calculation
        warnings: Validation warnings
        data_quality: Data quality assessment

    Returns:
        Markdown formatted report
    """
    sections = []

    # Header
    sections.append(_format_header(property_id, property_address))

    # Executive Summary
    sections.append(_format_executive_summary(
        marketability,
        value_impact,
        validation_results,
        encumbrance_analysis
    ))

    # Critical Issues (if any)
    critical = encumbrance_analysis.get('critical_issues', [])
    if critical or validation_results.get('summary', {}).get('critical_defects', 0) > 0:
        sections.append(_format_critical_issues(critical, validation_results))

    # Marketability Assessment
    sections.append(_format_marketability_section(marketability, value_impact))

    # Encumbrance Summary
    sections.append(_format_encumbrance_summary(encumbrance_analysis))

    # Detailed Encumbrance Analysis
    sections.append(_format_encumbrance_details(encumbrance_analysis))

    # Registration Validation
    sections.append(_format_validation_section(validation_results))

    # Registered Instruments
    sections.append(_format_instruments_section(parsed_instruments))

    # Recommendations
    sections.append(_format_recommendations(
        marketability,
        encumbrance_analysis,
        validation_results
    ))

    # Data Quality
    if data_quality.get('quality_score', 100) < 90:
        sections.append(_format_data_quality(data_quality, warnings))

    # Footer
    sections.append(_format_footer())

    return '\n\n'.join(sections)


def _format_header(property_id: str, property_address: str) -> str:
    """Format document header."""
    eastern = pytz.timezone('America/New_York')
    now = datetime.now(eastern)
    timestamp = now.strftime('%B %d, %Y at %I:%M %p %Z')

    return f"""# Title Analysis Report

**Property:** {property_address}
**PIN/Identifier:** {property_id}
**Report Date:** {timestamp}

---"""


def _format_executive_summary(
    marketability: Dict,
    value_impact: Dict,
    validation: Dict,
    encumbrances: Dict
) -> str:
    """Format executive summary section."""
    rating = marketability.get('rating', 'UNKNOWN')
    score = marketability.get('overall_score', 0)
    likely_discount = value_impact.get('likely_discount_pct', 0)

    summary = marketability.get('summary', '')
    validity_status = validation.get('validity', {}).get('status', 'UNKNOWN')

    total_encs = encumbrances.get('summary', {}).get('total', 0)
    critical_count = len(encumbrances.get('critical_issues', []))

    return f"""## Executive Summary

**Marketability Rating:** {rating} ({score:.1f}/100)

**Registration Status:** {validity_status}

**Estimated Value Impact:** {likely_discount:.1f}% discount

{summary}

**Key Findings:**
- {total_encs} registered encumbrance(s) identified
- {critical_count} critical issue(s) requiring immediate attention
- {validation.get('summary', {}).get('total_defects', 0)} registration defect(s) detected

**Buyer Pool Impact:** {marketability.get('buyer_pool', {}).get('description', 'Unknown')}

**Financing Availability:** {marketability.get('financing_availability', {}).get('availability', 'Unknown')}"""


def _format_critical_issues(critical: List[Dict], validation: Dict) -> str:
    """Format critical issues section."""
    section = "## Critical Issues Requiring Immediate Attention\n\n"

    if critical:
        section += "### Critical Encumbrances\n\n"
        for idx, issue in enumerate(critical, 1):
            section += f"{idx}. **{issue['type']}** (Instrument: {issue['instrument_number']})\n"
            section += f"   - Description: {issue['description']}\n"
            section += f"   - Value Impact: {issue['value_impact']['likely']:.1f}%\n"
            section += f"   - Priority: {issue['priority']}\n"
            section += "   - **Recommended Actions:**\n"
            for action in issue['recommended_actions']:
                section += f"     - {action}\n"
            section += "\n"

    critical_defects = validation.get('categorized', {}).get('critical', [])
    if critical_defects:
        section += "### Critical Registration Defects\n\n"
        for idx, defect in enumerate(critical_defects, 1):
            section += f"{idx}. **{defect['defect']}** (Instrument: {defect['instrument']})\n"
            section += f"   - Impact: {defect['impact']}\n"
            section += f"   - Remedy: {defect['remedy']}\n\n"

    return section


def _format_marketability_section(marketability: Dict, value_impact: Dict) -> str:
    """Format marketability assessment section."""
    rating = marketability.get('rating', 'UNKNOWN')
    scores = marketability.get('component_scores', {})
    buyer_pool = marketability.get('buyer_pool', {})

    section = f"""## Marketability Assessment

**Overall Rating:** {rating}

**Component Scores:**
| Component | Score | Status |
| :--- | ---: | :--- |
| Encumbrances | {scores.get('encumbrances', 0):.1f}/100 | {_score_status(scores.get('encumbrances', 0))} |
| Registration | {scores.get('defects', 0):.1f}/100 | {_score_status(scores.get('defects', 0))} |
| Financing | {scores.get('financing', 0):.1f}/100 | {_score_status(scores.get('financing', 0))} |
| Liquidity | {scores.get('liquidity', 0):.1f}/100 | {_score_status(scores.get('liquidity', 0))} |

### Value Impact

**Estimated Market Value Discount:**
- Minimum: {value_impact.get('min_discount_pct', 0):.1f}%
- Likely: {value_impact.get('likely_discount_pct', 0):.1f}%
- Maximum: {value_impact.get('max_discount_pct', 0):.1f}%

{value_impact.get('interpretation', '')}

### Buyer Pool Analysis

**Estimated Buyer Pool:** {buyer_pool.get('estimated_percentage', 0)}% of typical market

**Likely Buyer Types:**"""

    for buyer_type in buyer_pool.get('buyer_types', []):
        section += f"\n- {buyer_type}"

    return section


def _score_status(score: float) -> str:
    """Convert score to status label."""
    if score >= 85:
        return 'Excellent'
    elif score >= 70:
        return 'Good'
    elif score >= 50:
        return 'Fair'
    elif score >= 30:
        return 'Poor'
    else:
        return 'Critical'


def _format_encumbrance_summary(encumbrances: Dict) -> str:
    """Format encumbrance summary section."""
    summary = encumbrances.get('summary', {})

    section = f"""## Encumbrance Summary

**Total Encumbrances:** {summary.get('total', 0)}

**By Severity:**"""

    severity_counts = summary.get('by_severity', {})
    for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        count = severity_counts.get(severity, 0)
        if count > 0:
            section += f"\n- {severity}: {count}"

    section += f"\n\n**Action Required:** {summary.get('action_required_count', 0)} encumbrance(s)\n"
    section += f"**Average Value Impact:** {summary.get('average_value_impact', 0):.1f}%"

    return section


def _format_encumbrance_details(encumbrances: Dict) -> str:
    """Format detailed encumbrance list."""
    all_encs = encumbrances.get('encumbrances', [])

    if not all_encs:
        return "## Detailed Encumbrance Analysis\n\nNo encumbrances identified."

    section = "## Detailed Encumbrance Analysis\n\n"

    # Group by severity
    for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        severity_encs = [e for e in all_encs if e['severity'] == severity]

        if severity_encs:
            section += f"### {severity} Priority Encumbrances\n\n"

            for enc in severity_encs:
                section += f"**{enc['type']}** - {enc['instrument_number']}\n"
                section += f"- **Description:** {enc['description']}\n"
                section += f"- **Priority:** {enc['priority']}\n"
                section += f"- **Value Impact:** {enc['value_impact']['min']:.1f}% - {enc['value_impact']['max']:.1f}%\n"
                section += f"- **Registration Date:** {enc.get('registration_date', 'Unknown')}\n"

                # Use restrictions
                restrictions = enc.get('use_restrictions', {})
                active_restrictions = [k.replace('_', ' ').title() for k, v in restrictions.items() if v]
                if active_restrictions:
                    section += f"- **Use Restrictions:** {', '.join(active_restrictions)}\n"

                # Actions
                if enc.get('requires_action'):
                    section += "- **Actions Required:**\n"
                    for action in enc.get('recommended_actions', []):
                        section += f"  - {action}\n"

                section += "\n"

    return section


def _format_validation_section(validation: Dict) -> str:
    """Format registration validation section."""
    validity = validation.get('validity', {})
    summary = validation.get('summary', {})

    section = f"""## Registration Validation

**Overall Status:** {validity.get('status', 'UNKNOWN')}

**Marketable Title:** {'Yes' if validity.get('marketable', False) else 'No'}

{validity.get('message', '')}

**Defects Summary:**
- Critical: {summary.get('critical_defects', 0)}
- Major: {summary.get('major_defects', 0)}
- Minor: {summary.get('minor_defects', 0)}

**Recommendation:** {validity.get('recommendation', 'Obtain legal review')}"""

    # List defects if present
    categorized = validation.get('categorized', {})

    for severity in ['critical', 'major']:
        defects = categorized.get(severity, [])
        if defects:
            section += f"\n\n### {severity.upper()} Defects\n\n"
            for defect in defects:
                section += f"**{defect['defect']}** (Instrument: {defect['instrument']})\n"
                section += f"- Category: {defect['category']}\n"
                section += f"- Impact: {defect['impact']}\n"
                section += f"- Remedy: {defect['remedy']}\n\n"

    return section


def _format_instruments_section(parsed: Dict) -> str:
    """Format registered instruments section."""
    summary = parsed.get('summary', {})

    section = f"""## Registered Instruments

**Total Instruments:** {summary.get('total_instruments', 0)}

**Registration Period:** {summary.get('earliest_date', 'Unknown')} to {summary.get('latest_date', 'Unknown')}

**By Type:**"""

    by_type = summary.get('by_type_count', {})
    for inst_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
        section += f"\n- {inst_type}: {count}"

    # Detailed list by priority
    section += "\n\n### Priority Order\n\n"
    section += "| Priority | Type | Instrument # | Registration Date |\n"
    section += "| :--- | :--- | :--- | :--- |\n"

    by_priority = parsed.get('by_priority', [])
    for inst in by_priority[:20]:  # Limit to first 20
        priority = inst.get('priority_number', 'N/A')
        inst_type = inst.get('classified_type', 'Unknown')
        inst_num = inst.get('instrument_number', 'N/A')
        reg_date = inst.get('registration_date', 'Unknown')
        section += f"| {priority} | {inst_type} | {inst_num} | {reg_date} |\n"

    if len(by_priority) > 20:
        section += f"\n*Showing first 20 of {len(by_priority)} instruments*"

    return section


def _format_recommendations(
    marketability: Dict,
    encumbrances: Dict,
    validation: Dict
) -> str:
    """Format recommendations section."""
    recommendations = marketability.get('recommendations', [])

    section = "## Recommendations\n\n"

    if not recommendations:
        section += "No specific recommendations at this time.\n"
        return section

    for idx, rec in enumerate(recommendations, 1):
        section += f"{idx}. {rec}\n"

    return section


def _format_data_quality(data_quality: Dict, warnings: List[str]) -> str:
    """Format data quality section."""
    section = f"""## Data Quality Assessment

**Quality Score:** {data_quality.get('completeness', 'Unknown')}

**Completeness:**
- Complete: {data_quality.get('complete', 0)} instruments
- Partial: {data_quality.get('partial', 0)} instruments
- Minimal: {data_quality.get('minimal', 0)} instruments

**Issues:**"""

    for issue in data_quality.get('issues', []):
        section += f"\n- {issue}"

    if warnings:
        section += "\n\n**Validation Warnings:**"
        for warning in warnings[:10]:  # Limit to 10
            section += f"\n- {warning}"

    return section


def _format_footer() -> str:
    """Format report footer."""
    return """---

**Disclaimer:** This analysis is based on the registered instruments provided and may not reflect all title issues. A complete title search and legal opinion should be obtained before finalizing any transaction.

**Generated by:** Title Analyzer v1.0.0"""


def generate_json_output(
    property_id: str,
    property_address: str,
    parsed_instruments: Dict,
    encumbrance_analysis: Dict,
    validation_results: Dict,
    marketability: Dict,
    value_impact: Dict,
    warnings: List[str],
    data_quality: Dict
) -> Dict:
    """
    Generate JSON output.

    Args:
        All analysis results

    Returns:
        Dictionary for JSON serialization
    """
    eastern = pytz.timezone('America/New_York')
    now = datetime.now(eastern)

    return {
        'metadata': {
            'property_id': property_id,
            'property_address': property_address,
            'analysis_date': now.isoformat(),
            'analyzer_version': '1.0.0'
        },
        'marketability': marketability,
        'value_impact': value_impact,
        'encumbrances': {
            'summary': encumbrance_analysis.get('summary', {}),
            'critical': encumbrance_analysis.get('critical_issues', []),
            'high': encumbrance_analysis.get('high_issues', []),
            'all': encumbrance_analysis.get('encumbrances', [])
        },
        'validation': validation_results,
        'instruments': {
            'summary': parsed_instruments.get('summary', {}),
            'by_priority': parsed_instruments.get('by_priority', [])
        },
        'data_quality': data_quality,
        'warnings': warnings
    }


def save_markdown_report(report: str, output_path: str) -> None:
    """
    Save markdown report to file.

    Args:
        report: Markdown report string
        output_path: Output file path
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        f.write(report)

    print(f"\nMarkdown report saved: {output_file}")


def save_json_output(data: Dict, output_path: str) -> None:
    """
    Save JSON output to file.

    Args:
        data: Data dictionary
        output_path: Output file path
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2, default=str)

    print(f"JSON output saved: {output_file}")


def get_eastern_timestamp(include_time: bool = True) -> str:
    """
    Get Eastern Time timestamp.

    Args:
        include_time: Include time component

    Returns:
        Timestamp string
    """
    eastern = pytz.timezone('America/New_York')
    now = datetime.now(eastern)

    if include_time:
        return now.strftime('%Y-%m-%d_%H%M%S')
    else:
        return now.strftime('%Y-%m-%d')
