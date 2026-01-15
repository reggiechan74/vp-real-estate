"""
Output Formatting Module

Formats infrastructure cost calculator results as markdown reports and summary tables.
"""

from typing import Dict, List
import sys
import os

# Add parent directory to path for Shared_Utils imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from Shared_Utils.report_utils import (
    eastern_timestamp,
    format_markdown_table,
    generate_document_header
)


def format_cost_report(
    input_data: Dict,
    rcn_results: Dict,
    physical_dep: Dict,
    functional_obs: Dict,
    external_obs: Dict,
    total_dep: Dict,
    reconciliation: Dict
) -> str:
    """
    Format complete cost approach report as markdown.

    Args:
        input_data: Original input data
        rcn_results: Replacement cost new results
        physical_dep: Physical depreciation results
        functional_obs: Functional obsolescence results
        external_obs: External obsolescence results
        total_dep: Total depreciation results
        reconciliation: Market reconciliation results

    Returns:
        Markdown formatted report string

    Example:
        >>> report = format_cost_report(input_data, rcn, phys, func, ext, total, recon)
        >>> with open('report.md', 'w') as f:
        ...     f.write(report)
    """
    timestamp = eastern_timestamp()
    asset_type = input_data.get('asset_type', 'Infrastructure Asset')

    # Document header
    report = generate_document_header(
        title='Infrastructure Cost Approach Valuation',
        subtitle=f'{asset_type}',
        metadata={
            'Generated': timestamp,
            'Method': 'Cost Approach (Replacement Cost New Less Depreciation)',
            'Calculator': 'infrastructure_cost_calculator.py'
        }
    )

    # Executive Summary
    report += _format_executive_summary(rcn_results, total_dep, reconciliation)

    # Asset Information
    report += _format_asset_information(input_data)

    # Replacement Cost New
    report += _format_rcn_section(rcn_results)

    # Depreciation Analysis
    report += _format_depreciation_section(physical_dep, functional_obs, external_obs, total_dep)

    # Market Reconciliation
    report += _format_reconciliation_section(reconciliation)

    # Valuation Conclusion
    report += _format_conclusion_section(total_dep, reconciliation)

    # Methodology Notes
    report += _format_methodology_notes()

    return report


def _format_executive_summary(
    rcn_results: Dict,
    total_dep: Dict,
    reconciliation: Dict
) -> str:
    """Format executive summary section."""
    rcn = rcn_results.get('replacement_cost_new', 0)
    depreciated_cost = total_dep.get('depreciated_replacement_cost', 0)
    reconciled_value = reconciliation.get('reconciled_value', depreciated_cost)
    confidence = reconciliation.get('confidence_level', 'Medium')

    summary = "## Executive Summary\n\n"
    summary += f"**Replacement Cost New (RCN):** ${rcn:,.2f}\n\n"
    summary += f"**Less Total Depreciation:** ${total_dep.get('total_depreciation', 0):,.2f} "
    summary += f"({total_dep.get('total_depreciation_rate', 0):.1%})\n\n"
    summary += f"**Depreciated Replacement Cost:** ${depreciated_cost:,.2f}\n\n"

    if reconciliation.get('market_approach_available'):
        summary += f"**Market Reconciliation:** ${reconciled_value:,.2f}\n\n"
        summary += f"**Reconciliation Method:** {reconciliation.get('reconciliation_method', 'N/A')}\n\n"

    summary += f"**Confidence Level:** {confidence}\n\n"

    if reconciliation.get('notes'):
        summary += f"**Notes:** {reconciliation.get('notes')}\n\n"

    summary += "---\n\n"

    return summary


def _format_asset_information(input_data: Dict) -> str:
    """Format asset information section."""
    section = "## Asset Information\n\n"

    section += f"**Asset Type:** {input_data.get('asset_type', 'Not specified')}\n\n"

    # Specifications
    if 'specifications' in input_data:
        specs = input_data['specifications']
        section += "**Specifications:**\n"
        for key, value in specs.items():
            formatted_key = key.replace('_', ' ').title()
            section += f"- {formatted_key}: {value}\n"
        section += "\n"

    section += "---\n\n"

    return section


def _format_rcn_section(rcn_results: Dict) -> str:
    """Format replacement cost new section."""
    section = "## Replacement Cost New (RCN)\n\n"

    section += "### Cost Breakdown\n\n"

    # Create breakdown table
    breakdown_data = [
        {'component': 'Materials', 'amount': rcn_results.get('materials', 0)},
        {'component': 'Labor', 'amount': rcn_results.get('labor', 0)},
        {'component': 'Direct Costs (Materials + Labor)', 'amount': rcn_results.get('direct_costs', 0)},
        {'component': f"Overhead ({rcn_results.get('overhead_percentage', 0):.1%})",
         'amount': rcn_results.get('overhead', 0)},
        {'component': 'Subtotal', 'amount': rcn_results.get('subtotal', 0)},
        {'component': f"Profit ({rcn_results.get('profit_percentage', 0):.1%})",
         'amount': rcn_results.get('profit', 0)},
        {'component': '**TOTAL RCN**', 'amount': rcn_results.get('replacement_cost_new', 0)}
    ]

    section += format_markdown_table(
        breakdown_data,
        ['component', 'amount'],
        ['left', 'right']
    )

    section += "\n\n"
    section += "### Calculation Method\n\n"
    section += "```\n"
    section += f"Direct Costs     = Materials + Labor\n"
    section += f"                 = ${rcn_results.get('materials', 0):,.2f} + ${rcn_results.get('labor', 0):,.2f}\n"
    section += f"                 = ${rcn_results.get('direct_costs', 0):,.2f}\n\n"
    section += f"Overhead         = Direct Costs × {rcn_results.get('overhead_percentage', 0):.1%}\n"
    section += f"                 = ${rcn_results.get('direct_costs', 0):,.2f} × {rcn_results.get('overhead_percentage', 0):.1%}\n"
    section += f"                 = ${rcn_results.get('overhead', 0):,.2f}\n\n"
    section += f"Subtotal         = Direct Costs + Overhead\n"
    section += f"                 = ${rcn_results.get('subtotal', 0):,.2f}\n\n"
    section += f"Profit           = Subtotal × {rcn_results.get('profit_percentage', 0):.1%}\n"
    section += f"                 = ${rcn_results.get('subtotal', 0):,.2f} × {rcn_results.get('profit_percentage', 0):.1%}\n"
    section += f"                 = ${rcn_results.get('profit', 0):,.2f}\n\n"
    section += f"RCN              = Subtotal + Profit\n"
    section += f"                 = ${rcn_results.get('replacement_cost_new', 0):,.2f}\n"
    section += "```\n\n"

    section += "---\n\n"

    return section


def _format_depreciation_section(
    physical_dep: Dict,
    functional_obs: Dict,
    external_obs: Dict,
    total_dep: Dict
) -> str:
    """Format depreciation analysis section."""
    section = "## Depreciation Analysis\n\n"

    # Physical Depreciation
    section += "### 1. Physical Depreciation\n\n"
    section += f"**Method:** {physical_dep.get('method', 'Age/Life')}\n\n"
    section += f"**Actual Age:** {physical_dep.get('actual_age', 0)} years\n\n"
    section += f"**Effective Age:** {physical_dep.get('effective_age', 0)} years\n\n"
    section += f"**Economic Life:** {physical_dep.get('economic_life', 0)} years\n\n"
    section += f"**Remaining Life:** {physical_dep.get('remaining_life', 0)} years "
    section += f"({physical_dep.get('percent_remaining', 0):.1f}% remaining)\n\n"
    section += f"**Physical Condition:** {physical_dep.get('condition_rating', 'N/A')}\n\n"
    section += f"**Depreciation Rate:** {physical_dep.get('depreciation_rate', 0):.2%}\n\n"
    section += f"**Physical Depreciation:** ${physical_dep.get('physical_depreciation', 0):,.2f}\n\n"

    if physical_dep.get('variance_significant'):
        section += f"**⚠️ Note:** {physical_dep.get('recommendation', '')}\n\n"

    # Functional Obsolescence
    section += "### 2. Functional Obsolescence\n\n"
    section += f"**Severity:** {functional_obs.get('severity', 'None')}\n\n"
    section += f"**Description:** {functional_obs.get('description', 'N/A')}\n\n"
    section += f"**Obsolescence Rate:** {functional_obs.get('obsolescence_rate', 0):.2%}\n\n"
    section += f"**Functional Obsolescence:** ${functional_obs.get('functional_obsolescence', 0):,.2f}\n\n"

    if functional_obs.get('examples'):
        section += "**Typical Examples:**\n"
        for example in functional_obs['examples']:
            section += f"- {example}\n"
        section += "\n"

    # External Obsolescence
    section += "### 3. External Obsolescence\n\n"
    section += f"**Severity:** {external_obs.get('severity', 'None')}\n\n"
    section += f"**Description:** {external_obs.get('description', 'N/A')}\n\n"
    section += f"**Obsolescence Rate:** {external_obs.get('obsolescence_rate', 0):.2%}\n\n"
    section += f"**External Obsolescence:** ${external_obs.get('external_obsolescence', 0):,.2f}\n\n"

    if external_obs.get('examples'):
        section += "**Typical Examples:**\n"
        for example in external_obs['examples']:
            section += f"- {example}\n"
        section += "\n"

    # Total Depreciation Summary
    section += "### Total Depreciation Summary\n\n"

    depreciation_data = [
        {'category': 'Physical Depreciation',
         'amount': total_dep.get('physical_depreciation', 0),
         'percentage': f"{total_dep['breakdown_percentages']['physical']:.1f}%"},
        {'category': 'Functional Obsolescence',
         'amount': total_dep.get('functional_obsolescence', 0),
         'percentage': f"{total_dep['breakdown_percentages']['functional']:.1f}%"},
        {'category': 'External Obsolescence',
         'amount': total_dep.get('external_obsolescence', 0),
         'percentage': f"{total_dep['breakdown_percentages']['external']:.1f}%"},
        {'category': '**TOTAL DEPRECIATION**',
         'amount': total_dep.get('total_depreciation', 0),
         'percentage': '100.0%'}
    ]

    section += format_markdown_table(
        depreciation_data,
        ['category', 'amount', 'percentage'],
        ['left', 'right', 'right']
    )

    section += "\n\n"
    section += f"**Total Depreciation Rate:** {total_dep.get('total_depreciation_rate', 0):.2%}\n\n"
    section += f"**Depreciated Replacement Cost:** ${total_dep.get('depreciated_replacement_cost', 0):,.2f}\n\n"

    section += "---\n\n"

    return section


def _format_reconciliation_section(reconciliation: Dict) -> str:
    """Format market reconciliation section."""
    section = "## Market Reconciliation\n\n"

    if not reconciliation.get('market_approach_available'):
        section += "**Market Data:** Not available\n\n"
        section += f"**Conclusion:** {reconciliation.get('notes', 'Cost approach only')}\n\n"
        section += "---\n\n"
        return section

    # Market data available
    section += f"**Comparable Sales Analyzed:** {reconciliation.get('relevant_sales_count', 0)}\n\n"

    # Market statistics
    stats = reconciliation.get('market_statistics', {})
    section += "### Market Statistics\n\n"

    stats_data = [
        {'metric': 'Count', 'value': stats.get('count', 0)},
        {'metric': 'Mean', 'value': f"${stats.get('mean', 0):,.2f}"},
        {'metric': 'Median', 'value': f"${stats.get('median', 0):,.2f}"},
        {'metric': 'Minimum', 'value': f"${stats.get('min', 0):,.2f}"},
        {'metric': 'Maximum', 'value': f"${stats.get('max', 0):,.2f}"},
        {'metric': 'Range', 'value': f"${stats.get('range', 0):,.2f}"},
        {'metric': 'Std Deviation', 'value': f"${stats.get('std_dev', 0):,.2f}"}
    ]

    section += format_markdown_table(
        stats_data,
        ['metric', 'value'],
        ['left', 'right']
    )

    section += "\n\n"

    # Comparable sales detail
    if reconciliation.get('comparable_sales_detail'):
        section += "### Comparable Sales Detail\n\n"

        comps = reconciliation['comparable_sales_detail']
        section += format_markdown_table(
            comps,
            ['comp_number', 'sale_price', 'asset_type', 'condition'],
            ['center', 'right', 'left', 'left']
        )
        section += "\n\n"

    # Reconciliation analysis
    section += "### Reconciliation Analysis\n\n"
    section += f"**Cost Approach Value:** ${reconciliation.get('cost_approach_value', 0):,.2f}\n\n"
    section += f"**Market Median:** ${stats.get('median', 0):,.2f}\n\n"
    section += f"**Variance:** ${reconciliation.get('variance_amount', 0):,.2f} "
    section += f"({reconciliation.get('variance_percentage', 0):+.1f}%)\n\n"
    section += f"**Reconciliation Method:** {reconciliation.get('reconciliation_method', 'N/A')}\n\n"
    section += f"**Reconciled Value:** ${reconciliation.get('reconciled_value', 0):,.2f}\n\n"
    section += f"**Confidence Level:** {reconciliation.get('confidence_level', 'Medium')}\n\n"

    if reconciliation.get('notes'):
        section += f"**Analysis:** {reconciliation.get('notes')}\n\n"

    section += "---\n\n"

    return section


def _format_conclusion_section(total_dep: Dict, reconciliation: Dict) -> str:
    """Format valuation conclusion section."""
    section = "## Valuation Conclusion\n\n"

    rcn = total_dep.get('replacement_cost_new', 0)
    total_depreciation = total_dep.get('total_depreciation', 0)
    depreciated_cost = total_dep.get('depreciated_replacement_cost', 0)
    reconciled_value = reconciliation.get('reconciled_value', depreciated_cost)

    section += "### Cost Approach Summary\n\n"
    section += f"**Replacement Cost New:** ${rcn:,.2f}\n\n"
    section += f"**Less: Total Depreciation:** ${total_depreciation:,.2f}\n\n"
    section += f"**Depreciated Replacement Cost:** ${depreciated_cost:,.2f}\n\n"

    if reconciliation.get('market_approach_available'):
        section += "\n### Final Reconciled Value\n\n"
        section += f"**Indicated Value:** ${reconciled_value:,.2f}\n\n"
        section += f"**Confidence Level:** {reconciliation.get('confidence_level', 'Medium')}\n\n"
    else:
        section += "\n### Indicated Value\n\n"
        section += f"**Indicated Value (Cost Approach):** ${depreciated_cost:,.2f}\n\n"
        section += f"**Note:** Market data not available for reconciliation.\n\n"

    section += "---\n\n"

    return section


def _format_methodology_notes() -> str:
    """Format methodology notes section."""
    section = "## Methodology Notes\n\n"

    section += "### Cost Approach\n\n"
    section += "The cost approach is based on the principle of substitution: a prudent investor "
    section += "would pay no more for a property than the cost to acquire a substitute property "
    section += "of equivalent utility.\n\n"

    section += "**Formula:**\n"
    section += "```\n"
    section += "Value = Replacement Cost New (RCN) - Total Depreciation\n"
    section += "```\n\n"

    section += "**Replacement Cost New Components:**\n"
    section += "- Direct costs (materials and labor)\n"
    section += "- Indirect costs (overhead and profit)\n\n"

    section += "**Depreciation Components:**\n"
    section += "- Physical depreciation (wear and tear)\n"
    section += "- Functional obsolescence (design inefficiency)\n"
    section += "- External obsolescence (market/regulatory factors)\n\n"

    section += "### Market Reconciliation\n\n"
    section += "When market data is available, the cost approach is reconciled with comparable sales. "
    section += "Market data provides direct evidence of what buyers and sellers are willing to accept "
    section += "in actual transactions.\n\n"

    section += "---\n\n"
    section += f"*Report generated on {eastern_timestamp()} by infrastructure_cost_calculator.py*\n"

    return section


def format_summary_table(results: Dict) -> str:
    """
    Format one-line summary table for quick reference.

    Args:
        results: Complete results dictionary

    Returns:
        Markdown table with key values

    Example:
        >>> summary = format_summary_table(results)
        >>> print(summary)
    """
    table_data = [{
        'rcn': results.get('rcn_results', {}).get('replacement_cost_new', 0),
        'depreciation': results.get('total_depreciation', {}).get('total_depreciation', 0),
        'depreciated_cost': results.get('total_depreciation', {}).get('depreciated_replacement_cost', 0),
        'reconciled_value': results.get('reconciliation', {}).get('reconciled_value', 0),
        'confidence': results.get('reconciliation', {}).get('confidence_level', 'N/A')
    }]

    return format_markdown_table(
        table_data,
        ['rcn', 'depreciation', 'depreciated_cost', 'reconciled_value', 'confidence'],
        ['right', 'right', 'right', 'right', 'center']
    )
