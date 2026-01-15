#!/usr/bin/env python3
"""
Board Resolution Language Generation Module
Generates formal board resolution language based on approval type and project details.
"""

from typing import Dict, Optional


def generate_resolution_language(
    governance: Dict,
    project: Dict,
    financial: Dict
) -> str:
    """
    Generate formal board resolution language.

    Args:
        governance: Governance requirements dict
            {'approval_type': 'authorization', 'recommendation': '...', ...}
        project: Project details dict
            {'name': '...', 'description': '...', ...}
        financial: Financial details dict
            {'total_cost': 250000, 'funding_source': '...', ...}

    Returns:
        Formatted board resolution text
    """
    approval_type = governance.get('approval_type', 'authorization')
    project_name = project.get('name', 'Project')
    total_cost = financial.get('total_cost', 0)
    funding_source = financial.get('funding_source', 'operating_budget')

    # Get custom resolution if provided
    if 'resolution_draft' in governance and governance['resolution_draft']:
        return governance['resolution_draft']

    # Generate standard resolution based on approval type
    if approval_type == 'authorization':
        return _generate_authorization_resolution(project_name, total_cost, funding_source, governance)

    elif approval_type == 'ratification':
        return _generate_ratification_resolution(project_name, total_cost, governance)

    elif approval_type == 'delegation':
        return _generate_delegation_resolution(project_name, total_cost, governance)

    elif approval_type == 'information_only':
        return _generate_information_resolution(project_name, governance)

    else:
        return f"BE IT RESOLVED that the Board approves the recommendation regarding {project_name}."


def _generate_authorization_resolution(
    project_name: str,
    total_cost: float,
    funding_source: str,
    governance: Dict
) -> str:
    """Generate authorization resolution."""
    resolution = "BE IT RESOLVED that:\n\n"

    resolution += f"1. The Board authorizes management to proceed with {project_name} "
    resolution += f"at a total cost not to exceed ${total_cost:,.2f};\n\n"

    # Add funding source clause
    funding_text = {
        'operating_budget': 'from the current operating budget',
        'capital_budget': 'from the capital budget',
        'debt': 'through debt financing',
        'reserves': 'from accumulated reserves',
        'mixed': 'from approved sources'
    }
    resolution += f"2. Funding shall be drawn {funding_text.get(funding_source, 'from approved sources')};\n\n"

    # Add delegation clause if authority limits specified
    if 'authority_limits' in governance:
        limits = governance['authority_limits']
        if 'contract_limit' in limits:
            contract_limit = limits['contract_limit']
            resolution += f"3. The Chief Executive Officer is authorized to execute contracts "
            resolution += f"up to ${contract_limit:,.2f} without further Board approval; and\n\n"
            resolution += f"4. Management shall report back to the Board upon completion of the project."
        else:
            resolution += f"3. Management shall report back to the Board upon completion of the project."
    else:
        resolution += f"3. Management shall report back to the Board upon completion of the project."

    return resolution


def _generate_ratification_resolution(
    project_name: str,
    total_cost: float,
    governance: Dict
) -> str:
    """Generate ratification resolution for actions already taken."""
    resolution = "BE IT RESOLVED that:\n\n"

    resolution += f"1. The Board ratifies the actions of management in proceeding with {project_name} "
    resolution += f"at a total cost of ${total_cost:,.2f};\n\n"

    resolution += f"2. The Board confirms that the actions taken were in the best interests "
    resolution += f"of the organization and necessary under the circumstances; and\n\n"

    resolution += f"3. The Board directs management to ensure all appropriate approvals "
    resolution += f"are obtained prospectively for similar transactions."

    return resolution


def _generate_delegation_resolution(
    project_name: str,
    total_cost: float,
    governance: Dict
) -> str:
    """Generate delegation resolution."""
    resolution = "BE IT RESOLVED that:\n\n"

    authority_limits = governance.get('authority_limits', {})
    contract_limit = authority_limits.get('contract_limit', total_cost)

    resolution += f"1. The Board delegates authority to the Chief Executive Officer to "
    resolution += f"approve expenditures related to {project_name} "
    resolution += f"up to a maximum of ${contract_limit:,.2f};\n\n"

    resolution += f"2. The Chief Executive Officer shall ensure all expenditures are within "
    resolution += f"approved budget allocations;\n\n"

    resolution += f"3. The Chief Executive Officer shall report quarterly to the Board on "
    resolution += f"expenditures made under this delegated authority; and\n\n"

    resolution += f"4. This delegation shall remain in effect until revoked by the Board."

    return resolution


def _generate_information_resolution(project_name: str, governance: Dict) -> str:
    """Generate information-only resolution (acknowledgment)."""
    resolution = "BE IT RESOLVED that:\n\n"

    resolution += f"The Board acknowledges receipt of the information regarding {project_name} "
    resolution += f"and directs management to provide updates as the project progresses."

    return resolution


def format_approval_recommendation(governance: Dict) -> str:
    """
    Format the approval recommendation section.

    Args:
        governance: Governance requirements dict

    Returns:
        Formatted recommendation text
    """
    recommendation = governance.get('recommendation', 'Approve as presented')
    approval_type = governance.get('approval_type', 'authorization')

    text = "## Recommendation\n\n"

    # Add context based on approval type
    if approval_type == 'authorization':
        text += "**Recommendation:** That the Board authorize the project as outlined in this memorandum.\n\n"
    elif approval_type == 'ratification':
        text += "**Recommendation:** That the Board ratify the actions taken by management.\n\n"
    elif approval_type == 'delegation':
        text += "**Recommendation:** That the Board delegate authority as outlined below.\n\n"
    elif approval_type == 'information_only':
        text += "**Recommendation:** That the Board receive this information.\n\n"

    text += f"**Rationale:** {recommendation}\n\n"

    return text


def format_compliance_requirements(governance: Dict) -> str:
    """
    Format compliance requirements section if present.

    Args:
        governance: Governance requirements dict

    Returns:
        Formatted compliance requirements or empty string
    """
    if 'compliance_requirements' not in governance or not governance['compliance_requirements']:
        return ""

    text = "### Compliance Requirements\n\n"

    for requirement in governance['compliance_requirements']:
        text += f"- {requirement}\n"

    text += "\n"
    return text


def format_authority_limits(governance: Dict) -> str:
    """
    Format authority limits and delegation section if present.

    Args:
        governance: Governance requirements dict

    Returns:
        Formatted authority limits or empty string
    """
    if 'authority_limits' not in governance:
        return ""

    limits = governance['authority_limits']
    text = "### Authority Limits\n\n"

    if 'approval_level' in limits:
        level_text = {
            'staff': 'Staff Level',
            'ceo': 'Chief Executive Officer',
            'board_committee': 'Board Committee',
            'full_board': 'Full Board'
        }
        text += f"**Required Approval Level:** {level_text.get(limits['approval_level'], limits['approval_level'])}\n\n"

    if 'contract_limit' in limits:
        text += f"**Contract Authority Limit:** ${limits['contract_limit']:,.2f}\n\n"
        text += "Contracts exceeding this amount require additional Board approval.\n\n"

    return text


def format_stakeholder_consultation(governance: Dict) -> str:
    """
    Format stakeholder consultation summary if present.

    Args:
        governance: Governance requirements dict

    Returns:
        Formatted stakeholder consultation or empty string
    """
    if 'stakeholder_consultation' not in governance or not governance['stakeholder_consultation']:
        return ""

    text = "### Stakeholder Consultation\n\n"
    text += f"{governance['stakeholder_consultation']}\n\n"

    return text
