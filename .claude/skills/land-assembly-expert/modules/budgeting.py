#!/usr/bin/env python3
"""
Budget Calculation Module for Land Assembly Calculator
Implements budget logic using shared land_assembly_utils
"""

import sys
from pathlib import Path

# Add parent directory to path for shared utilities
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'Shared_Utils'))

from land_assembly_utils import (
    multi_parcel_budget,
    cost_of_delay,
    resource_allocation_plan,
    contingency_budget
)
from typing import Dict, List


def calculate_budget(parcels: List[Dict], contingencies: Dict) -> Dict:
    """
    Calculate multi-parcel acquisition budget.

    Wrapper around shared multi_parcel_budget function.

    Args:
        parcels: List of parcel dictionaries
        contingencies: Contingency rates dict

    Returns:
        Budget analysis dict
    """
    return multi_parcel_budget(parcels, contingencies)


def calculate_delay_cost(delayed_parcels: List[Dict], project_impact: Dict) -> Dict:
    """
    Calculate cost of delay for parcels.

    Wrapper around shared cost_of_delay function.

    Args:
        delayed_parcels: List of delayed parcels
        project_impact: Project impact parameters

    Returns:
        Cost of delay analysis dict
    """
    return cost_of_delay(delayed_parcels, project_impact)


def calculate_resource_allocation(parcels: List[Dict], resources: Dict) -> Dict:
    """
    Calculate resource allocation plan.

    Wrapper around shared resource_allocation_plan function.

    Args:
        parcels: List of parcels
        resources: Resource availability dict

    Returns:
        Resource allocation plan dict
    """
    return resource_allocation_plan(parcels, resources)


def calculate_contingency(parcels: List[Dict], risk_factors: Dict) -> Dict:
    """
    Calculate contingency budget.

    Wrapper around shared contingency_budget function.

    Args:
        parcels: List of parcels
        risk_factors: Risk factor percentages

    Returns:
        Contingency budget dict
    """
    return contingency_budget(parcels, risk_factors)


def format_budget_output(budget_result: Dict) -> str:
    """
    Format budget analysis for markdown output.

    Args:
        budget_result: Result from multi_parcel_budget

    Returns:
        Formatted markdown string
    """
    output = []

    output.append("## Budget Analysis\n")

    # Summary
    output.append("### Budget Summary")
    output.append(f"- **Base Budget:** ${budget_result['base_budget']:,.0f}")
    output.append(f"- **Total Contingencies:** ${budget_result['total_contingencies']:,.0f}")
    output.append(f"- **Total Budget:** ${budget_result['total_budget']:,.0f}")
    output.append(f"- **Contingency Rate:** {budget_result['contingency_rate']:.1f}%")
    output.append(f"- **Per Parcel Average:** ${budget_result['per_parcel_avg']:,.0f}\n")

    # Contingency breakdown
    output.append("### Contingency Breakdown")
    contingencies = budget_result['contingencies']
    output.append(f"- **Valuation Uncertainty:** ${contingencies['valuation_uncertainty']:,.0f}")
    output.append(f"- **Negotiation Premium:** ${contingencies['negotiation_premium']:,.0f}")
    output.append(f"- **Litigation Reserve:** ${contingencies['litigation_reserve']:,.0f}")
    output.append(f"- **Inflation Adjustment:** ${contingencies['inflation_adjustment']:,.0f}")
    output.append(f"- **Professional Fees:** ${contingencies['professional_fees']:,.0f}\n")

    # Budget by criticality
    if budget_result.get('budget_by_criticality'):
        output.append("### Budget by Criticality Level\n")
        output.append("| Criticality | Count | Base Value | % of Total |")
        output.append("|-------------|-------|------------|------------|")

        for level in ['critical', 'high', 'medium', 'low']:
            if level in budget_result['budget_by_criticality']:
                data = budget_result['budget_by_criticality'][level]
                output.append(
                    f"| {level.capitalize()} | {data['count']} | "
                    f"${data['base_value']:,.0f} | {data['percentage']:.1f}% |"
                )

    return '\n'.join(output)


def format_resource_output(resource_result: Dict) -> str:
    """
    Format resource allocation for markdown output.

    Args:
        resource_result: Result from resource_allocation_plan

    Returns:
        Formatted markdown string
    """
    output = []

    output.append("## Resource Allocation Plan\n")

    # Total days required
    output.append("### Total Days Required")
    days = resource_result['total_days_required']
    output.append(f"- **Appraisal:** {days['appraisal']:,.0f} days")
    output.append(f"- **Negotiation:** {days['negotiation']:,.0f} days")
    output.append(f"- **Legal:** {days['legal']:,.0f} days\n")

    # Timeline with resources
    output.append("### Timeline with Current Resources")
    timeline = resource_result['timeline_with_resources']
    output.append(f"- **Appraisal Phase:** {timeline['appraisal_phase_days']:,.0f} days ({timeline['appraisal_phase_days'] / 30:.1f} months)")
    output.append(f"- **Negotiation Phase:** {timeline['negotiation_phase_days']:,.0f} days ({timeline['negotiation_phase_days'] / 30:.1f} months)")
    output.append(f"- **Legal Phase:** {timeline['legal_phase_days']:,.0f} days ({timeline['legal_phase_days'] / 30:.1f} months)\n")

    # Cost breakdown
    output.append("### Cost Breakdown")
    costs = resource_result['cost_breakdown']
    output.append(f"- **Appraisal Costs:** ${costs['appraisal']:,.0f}")
    output.append(f"- **Negotiation Costs:** ${costs['negotiation']:,.0f}")
    output.append(f"- **Legal Costs:** ${costs['legal']:,.0f}")
    output.append(f"- **Total Professional Services:** ${resource_result['total_cost']:,.0f}\n")

    # Resource utilization
    output.append("### Resource Utilization")
    util = resource_result['resource_utilization']
    output.append(f"- **Appraisers:** {util['appraisers']:.1f}% of year")
    output.append(f"- **Negotiators:** {util['negotiators']:.1f}% of year")
    output.append(f"- **Legal Staff:** {util['legal']:.1f}% of year")

    return '\n'.join(output)


def format_delay_cost_output(delay_result: Dict) -> str:
    """
    Format cost of delay analysis for markdown output.

    Args:
        delay_result: Result from cost_of_delay

    Returns:
        Formatted markdown string
    """
    if 'error' in delay_result:
        return f"## Cost of Delay Analysis\n\n**Error:** {delay_result['error']}"

    output = []

    output.append("## Cost of Delay Analysis\n")

    output.append("### Delay Cost Summary")
    output.append(f"- **Delay Period:** {delay_result['delay_days']} days")
    output.append(f"- **Number of Delayed Parcels:** {delay_result['num_delayed_parcels']}")
    output.append(f"- **Total Value of Delayed Parcels:** ${delay_result['total_value_delayed_parcels']:,.0f}\n")

    output.append("### Cost Components")
    output.append(f"- **Interest Carrying Cost:** ${delay_result['interest_carrying_cost']:,.0f}")
    output.append(f"- **Construction Delay Cost:** ${delay_result['construction_delay_cost']:,.0f}")
    output.append(f"- **Revenue Loss:** ${delay_result['revenue_loss']:,.0f}")
    output.append(f"- **Total Delay Cost:** ${delay_result['total_delay_cost']:,.0f}")
    output.append(f"- **Cost per Delayed Parcel:** ${delay_result['delay_cost_per_parcel']:,.0f}")

    return '\n'.join(output)
