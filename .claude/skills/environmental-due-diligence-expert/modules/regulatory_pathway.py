#!/usr/bin/env python3
"""
Regulatory Pathway Module
Provides functions for determining MOE approval pathways and timelines.

Author: Claude Code
Created: 2025-11-17
"""

from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


def determine_regulatory_pathway(
    phase_2_data: Optional[Dict] = None,
    risk_level: str = 'MEDIUM'
) -> Dict:
    """
    Determine MOE regulatory pathway based on contamination findings.

    Ontario pathways:
    - Clean Site: No exceedances, no filing required
    - Tier 1: Risk Assessment pathway (contamination below Tier 1 limits)
    - Tier 2: Site-specific Risk Assessment (contamination exceeds Tier 1)
    - Remedial Work Plan: Active remediation required

    Args:
        phase_2_data: Phase II ESA results (optional)
        risk_level: Overall contamination risk level ('HIGH', 'MEDIUM', 'LOW')

    Returns:
        Dict containing regulatory pathway determination
            {
                'pathway': 'Tier 1 Risk Assessment',
                'filing_required': True,
                'qp_required': True,
                'rsr_required': True,
                'description': '...',
                'requirements': [...]
            }
    """
    if not phase_2_data or len(phase_2_data.get('exceedances', [])) == 0:
        # Clean site
        return {
            'pathway': 'Clean Site',
            'filing_required': False,
            'qp_required': False,
            'rsr_required': False,
            'description': 'No contamination exceedances - no MOE filing required',
            'requirements': [
                'Maintain Phase I and Phase II ESA reports',
                'Update environmental records upon closing'
            ],
            'complexity': 'LOW'
        }

    # Get contamination details
    exceedances_count = len(phase_2_data.get('exceedances', []))
    contaminants = phase_2_data.get('contaminants', [])

    # Check for high-risk indicators requiring Tier 2 or RWP
    high_risk_contaminants = ['vocs', 'heavy metals', 'pcb', 'dnapl']
    has_high_risk = any(
        any(risk in str(c).lower() for risk in high_risk_contaminants)
        for c in contaminants
    )

    groundwater_impacted = phase_2_data.get('groundwater_samples_count', 0) > 0

    # Determine pathway
    if risk_level == 'HIGH' or has_high_risk or groundwater_impacted:
        if exceedances_count >= 5 or groundwater_impacted:
            # Remedial Work Plan or Tier 2
            return {
                'pathway': 'Tier 2 Site-Specific Risk Assessment',
                'filing_required': True,
                'qp_required': True,
                'rsr_required': True,
                'description': 'Significant contamination requiring site-specific risk assessment or active remediation',
                'requirements': [
                    'Retain Qualified Person (QP) - environmental consultant',
                    'File Record of Site Condition (RSC) with MOE',
                    'Conduct detailed site-specific risk assessment',
                    'Prepare remedial action plan if needed',
                    'Implement risk management measures',
                    'Obtain Certificate of Property Use'
                ],
                'complexity': 'HIGH',
                'alternative_pathway': 'Remedial Work Plan (active remediation)'
            }
        else:
            # Tier 1 with elevated risk
            return {
                'pathway': 'Tier 1 Risk Assessment',
                'filing_required': True,
                'qp_required': True,
                'rsr_required': True,
                'description': 'Moderate contamination manageable through risk assessment',
                'requirements': [
                    'Retain Qualified Person (QP) - environmental consultant',
                    'File Record of Site Condition (RSC) with MOE',
                    'Conduct Tier 1 risk assessment',
                    'Implement risk management measures (if needed)',
                    'Obtain Certificate of Property Use'
                ],
                'complexity': 'MEDIUM'
            }
    else:
        # Low to medium risk - Tier 1
        return {
            'pathway': 'Tier 1 Risk Assessment',
            'filing_required': True,
            'qp_required': True,
            'rsr_required': True,
            'description': 'Minor contamination manageable through standard risk assessment',
            'requirements': [
                'Retain Qualified Person (QP) - environmental consultant',
                'File Record of Site Condition (RSC) with MOE',
                'Conduct Tier 1 risk assessment',
                'Obtain Certificate of Property Use'
            ],
            'complexity': 'MEDIUM'
        }


def estimate_regulatory_timeline(
    pathway_data: Dict,
    expedited: bool = False
) -> Dict:
    """
    Estimate regulatory timeline for MOE approval process.

    Args:
        pathway_data: Output from determine_regulatory_pathway()
        expedited: Whether to use expedited processing (default False)

    Returns:
        Dict containing timeline estimates
            {
                'total_months': 9,
                'phases': [
                    {'phase': 'QP Retention', 'duration_months': 1},
                    {'phase': 'Risk Assessment', 'duration_months': 3},
                    ...
                ],
                'critical_path': [...],
                'contingency_months': 2
            }
    """
    pathway = pathway_data.get('pathway', 'Clean Site')
    complexity = pathway_data.get('complexity', 'LOW')

    if pathway == 'Clean Site':
        # No regulatory timeline
        return {
            'total_months': 0,
            'phases': [],
            'critical_path': [],
            'contingency_months': 0,
            'description': 'No MOE approval process required'
        }

    # Define phases based on pathway
    if pathway == 'Tier 1 Risk Assessment':
        phases = [
            {'phase': 'QP Retention & Contract', 'duration_months': 0.5, 'critical': True},
            {'phase': 'Risk Assessment Preparation', 'duration_months': 2.0, 'critical': True},
            {'phase': 'RSC Filing with MOE', 'duration_months': 0.5, 'critical': True},
            {'phase': 'MOE Review & Acknowledgment', 'duration_months': 2.0, 'critical': True},
            {'phase': 'Certificate of Property Use', 'duration_months': 1.0, 'critical': True}
        ]
        base_timeline = 6.0
        contingency = 2.0

    elif pathway == 'Tier 2 Site-Specific Risk Assessment':
        phases = [
            {'phase': 'QP Retention & Contract', 'duration_months': 0.5, 'critical': True},
            {'phase': 'Site-Specific Risk Assessment', 'duration_months': 4.0, 'critical': True},
            {'phase': 'Remedial Action Plan (if needed)', 'duration_months': 2.0, 'critical': False},
            {'phase': 'Risk Management Measures', 'duration_months': 3.0, 'critical': True},
            {'phase': 'RSC Filing with MOE', 'duration_months': 0.5, 'critical': True},
            {'phase': 'MOE Review & Acknowledgment', 'duration_months': 3.0, 'critical': True},
            {'phase': 'Certificate of Property Use', 'duration_months': 1.0, 'critical': True}
        ]
        base_timeline = 12.0
        contingency = 4.0

    else:
        # Generic timeline
        phases = [
            {'phase': 'QP Retention', 'duration_months': 0.5, 'critical': True},
            {'phase': 'Assessment & Planning', 'duration_months': 2.0, 'critical': True},
            {'phase': 'MOE Filing & Review', 'duration_months': 2.0, 'critical': True}
        ]
        base_timeline = 4.5
        contingency = 1.5

    # Adjust for expedited processing
    if expedited:
        for phase in phases:
            phase['duration_months'] *= 0.8  # 20% reduction
        base_timeline *= 0.8
        contingency *= 0.7

    # Calculate total
    total_months = sum(p['duration_months'] for p in phases)
    total_with_contingency = total_months + contingency

    # Identify critical path
    critical_path = [p for p in phases if p.get('critical', False)]

    return {
        'total_months': round(total_months, 1),
        'total_with_contingency': round(total_with_contingency, 1),
        'phases': phases,
        'critical_path': critical_path,
        'contingency_months': round(contingency, 1),
        'expedited': expedited,
        'pathway': pathway
    }


def generate_approval_requirements(
    pathway_data: Dict,
    timeline_data: Dict
) -> List[Dict]:
    """
    Generate list of approval requirements and deliverables.

    Args:
        pathway_data: Output from determine_regulatory_pathway()
        timeline_data: Output from estimate_regulatory_timeline()

    Returns:
        List of requirement dictionaries
            [
                {
                    'requirement': 'Retain Qualified Person (QP)',
                    'timing': 'Month 1',
                    'responsible': 'Purchaser',
                    'cost_estimate': 150000,
                    'mandatory': True
                },
                ...
            ]
    """
    pathway = pathway_data.get('pathway', 'Clean Site')
    requirements = []

    if pathway == 'Clean Site':
        return requirements

    # Common requirements for all pathways with filing
    if pathway_data.get('qp_required'):
        requirements.append({
            'requirement': 'Retain Qualified Person (QP) - Environmental Consultant',
            'timing': 'Month 1',
            'responsible': 'Purchaser (or negotiated with Vendor)',
            'cost_estimate': 15000,
            'cost_range': '10,000 - 25,000',
            'mandatory': True,
            'description': 'Licensed environmental consultant to oversee process'
        })

    if pathway_data.get('rsr_required'):
        requirements.append({
            'requirement': 'File Record of Site Condition (RSC)',
            'timing': f"Month {int(timeline_data.get('total_months', 6) * 0.6)}",
            'responsible': 'QP on behalf of property owner',
            'cost_estimate': 5000,
            'cost_range': '3,000 - 8,000',
            'mandatory': True,
            'description': 'Official filing with MOE Environmental Site Registry'
        })

    # Pathway-specific requirements
    if pathway == 'Tier 1 Risk Assessment':
        requirements.extend([
            {
                'requirement': 'Tier 1 Risk Assessment Report',
                'timing': 'Months 2-4',
                'responsible': 'QP',
                'cost_estimate': 25000,
                'cost_range': '20,000 - 40,000',
                'mandatory': True,
                'description': 'Generic risk assessment using standard criteria'
            },
            {
                'requirement': 'Certificate of Property Use',
                'timing': f"Month {int(timeline_data.get('total_months', 6))}",
                'responsible': 'MOE',
                'cost_estimate': 2500,
                'cost_range': '2,000 - 3,500',
                'mandatory': True,
                'description': 'MOE acknowledgment of RSC filing'
            }
        ])

    elif pathway == 'Tier 2 Site-Specific Risk Assessment':
        requirements.extend([
            {
                'requirement': 'Site-Specific Risk Assessment',
                'timing': 'Months 2-6',
                'responsible': 'QP',
                'cost_estimate': 60000,
                'cost_range': '50,000 - 100,000',
                'mandatory': True,
                'description': 'Detailed risk assessment tailored to site conditions'
            },
            {
                'requirement': 'Remedial Action Plan (if needed)',
                'timing': 'Months 5-7',
                'responsible': 'QP',
                'cost_estimate': 20000,
                'cost_range': '15,000 - 35,000',
                'mandatory': False,
                'description': 'Plan for active remediation or risk management'
            },
            {
                'requirement': 'Risk Management Measures Implementation',
                'timing': 'Months 7-10',
                'responsible': 'Property Owner / Contractor',
                'cost_estimate': 150000,
                'cost_range': '100,000 - 300,000',
                'mandatory': True,
                'description': 'Physical implementation of risk controls'
            },
            {
                'requirement': 'Certificate of Property Use',
                'timing': f"Month {int(timeline_data.get('total_months', 12))}",
                'responsible': 'MOE',
                'cost_estimate': 2500,
                'cost_range': '2,000 - 3,500',
                'mandatory': True,
                'description': 'MOE acknowledgment of RSC filing'
            }
        ])

    # Add insurance requirement for high-risk pathways
    if pathway == 'Tier 2 Site-Specific Risk Assessment':
        requirements.append({
            'requirement': 'Environmental Pollution Liability Insurance',
            'timing': 'Before closing',
            'responsible': 'Purchaser',
            'cost_estimate': 25000,
            'cost_range': '15,000 - 50,000 annually',
            'mandatory': False,
            'description': 'Insurance coverage for environmental risks'
        })

    return requirements


def calculate_total_regulatory_costs(approval_requirements: List[Dict]) -> Dict:
    """
    Calculate total regulatory compliance costs.

    Args:
        approval_requirements: Output from generate_approval_requirements()

    Returns:
        Dict with cost summary
            {
                'total_estimated': 225000,
                'total_low': 180000,
                'total_high': 310000,
                'breakdown': {...}
            }
    """
    total_estimated = 0
    total_low = 0
    total_high = 0
    breakdown = {}

    for req in approval_requirements:
        cost_estimate = req.get('cost_estimate', 0)
        total_estimated += cost_estimate

        # Parse cost range if available
        cost_range = req.get('cost_range', '')
        if cost_range and '-' in cost_range:
            try:
                parts = cost_range.replace(',', '').split('-')
                low = float(parts[0].strip().replace('$', ''))
                high = float(parts[1].strip().split()[0].replace('$', ''))
                total_low += low
                total_high += high
            except:
                # Fallback to estimate
                total_low += cost_estimate * 0.8
                total_high += cost_estimate * 1.2
        else:
            total_low += cost_estimate * 0.8
            total_high += cost_estimate * 1.2

        breakdown[req['requirement']] = cost_estimate

    return {
        'total_estimated': round(total_estimated, 2),
        'total_low': round(total_low, 2),
        'total_high': round(total_high, 2),
        'breakdown': breakdown,
        'mandatory_count': sum(1 for r in approval_requirements if r.get('mandatory', False)),
        'optional_count': sum(1 for r in approval_requirements if not r.get('mandatory', False))
    }
