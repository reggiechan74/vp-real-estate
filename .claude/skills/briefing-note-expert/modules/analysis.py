#!/usr/bin/env python3
"""
Briefing Note Analysis Module
Decision-focused analysis for executive briefing notes
"""

from typing import Dict, List, Optional
import sys
import os

# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
skills_dir = os.path.dirname(os.path.dirname(current_dir))
root_dir = os.path.dirname(os.path.dirname(skills_dir))
sys.path.insert(0, root_dir)

# Optional imports - only used for property assembly context
try:
    from Shared_Utils.risk_utils import assess_holdout_risk, litigation_risk_assessment
    RISK_UTILS_AVAILABLE = True
except ImportError:
    RISK_UTILS_AVAILABLE = False


def analyze_decision_urgency(data: Dict) -> Dict:
    """
    Analyze decision urgency based on timeline and constraints.

    Args:
        data: Briefing note input data

    Returns:
        Dict with urgency analysis
            {
                'urgency_level': 'high',
                'urgency_score': 85,
                'timeline_pressure': {...},
                'key_constraints': [...]
            }
    """
    urgency_level = data.get('urgency', 'medium')
    urgency_score_map = {'low': 30, 'medium': 60, 'high': 90}
    urgency_score = urgency_score_map.get(urgency_level, 60)

    # Adjust score based on timeline
    timeline_pressure = {}
    background = data.get('background', {})
    project_timeline = background.get('project_timeline', {})

    if 'critical_deadline' in project_timeline:
        timeline_pressure['has_critical_deadline'] = True
        urgency_score = min(urgency_score + 10, 100)
    else:
        timeline_pressure['has_critical_deadline'] = False

    # Check for key milestones
    milestones = project_timeline.get('key_milestones', [])
    pending_milestones = [m for m in milestones if m.get('status') == 'pending']

    timeline_pressure['pending_milestones_count'] = len(pending_milestones)
    if len(pending_milestones) > 3:
        urgency_score = min(urgency_score + 5, 100)

    # Identify key constraints
    key_constraints = []

    if urgency_level == 'high':
        key_constraints.append('High urgency decision required')

    if timeline_pressure.get('has_critical_deadline'):
        key_constraints.append(f"Critical deadline: {project_timeline.get('critical_deadline')}")

    if pending_milestones:
        key_constraints.append(f"{len(pending_milestones)} pending milestone(s)")

    # Check financial constraints
    financial = data.get('financial_summary', {})
    budget_comparison = financial.get('budget_comparison', {})

    if budget_comparison.get('variance', 0) > 0:
        variance_pct = budget_comparison.get('variance_pct', 0)
        if variance_pct > 10:
            key_constraints.append(f"Budget overrun: {variance_pct:.1f}%")

    return {
        'urgency_level': urgency_level,
        'urgency_score': urgency_score,
        'timeline_pressure': timeline_pressure,
        'key_constraints': key_constraints
    }


def analyze_alternatives(data: Dict) -> Dict:
    """
    Analyze alternatives and compare to recommendation.

    Args:
        data: Briefing note input data

    Returns:
        Dict with alternatives analysis
            {
                'alternatives_count': 2,
                'recommended_cost': 1800000,
                'cost_comparison': [...],
                'key_differentiators': [...]
            }
    """
    analysis_data = data.get('analysis', {})
    alternatives = analysis_data.get('alternatives_considered', [])

    financial = data.get('financial_summary', {})
    recommended_cost = financial.get('total_cost', 0)

    # Cost comparison
    cost_comparison = []
    for alt in alternatives:
        alt_cost = alt.get('cost', 0)
        cost_diff = alt_cost - recommended_cost
        cost_diff_pct = (cost_diff / recommended_cost * 100) if recommended_cost > 0 else 0

        cost_comparison.append({
            'alternative': alt.get('alternative', 'Unnamed'),
            'cost': alt_cost,
            'cost_vs_recommended': cost_diff,
            'cost_vs_recommended_pct': cost_diff_pct,
            'timeline_impact': alt.get('timeline_impact', 'Unknown')
        })

    # Sort by cost
    cost_comparison.sort(key=lambda x: x['cost'])

    # Identify key differentiators
    key_differentiators = []

    # Cost differentiator
    if cost_comparison:
        min_cost_alt = cost_comparison[0]
        max_cost_alt = cost_comparison[-1]

        cost_range = max_cost_alt['cost'] - min_cost_alt['cost']
        cost_range_pct = (cost_range / recommended_cost * 100) if recommended_cost > 0 else 0

        if cost_range_pct > 20:
            key_differentiators.append(
                f"Significant cost variation across alternatives: ${cost_range:,.0f} ({cost_range_pct:.1f}%)"
            )

    # Timeline differentiator
    timeline_impacts = set(alt.get('timeline_impact', 'Unknown') for alt in alternatives)
    if len(timeline_impacts) > 1:
        key_differentiators.append(f"Varying timeline impacts: {', '.join(timeline_impacts)}")

    # Pros/cons balance
    for alt in alternatives:
        pros = alt.get('pros', [])
        cons = alt.get('cons', [])

        if len(pros) == 0 and len(cons) > 2:
            key_differentiators.append(
                f"{alt.get('alternative')}: Significant drawbacks identified"
            )
        elif len(pros) > 2 and len(cons) == 0:
            key_differentiators.append(
                f"{alt.get('alternative')}: Strong alternative with few drawbacks"
            )

    return {
        'alternatives_count': len(alternatives),
        'recommended_cost': recommended_cost,
        'cost_comparison': cost_comparison,
        'key_differentiators': key_differentiators
    }


def analyze_strategic_alignment(data: Dict) -> Dict:
    """
    Analyze strategic alignment and benefits.

    Args:
        data: Briefing note input data

    Returns:
        Dict with strategic analysis
            {
                'strategic_score': 75,
                'benefits_count': 4,
                'precedents_count': 2,
                'alignment_summary': '...'
            }
    """
    analysis_data = data.get('analysis', {})

    strategic_rationale = analysis_data.get('strategic_rationale', '')
    benefits = analysis_data.get('benefits', [])
    precedents = analysis_data.get('precedents', [])

    # Calculate strategic score
    strategic_score = 50  # Base score

    # Adjust for rationale presence
    if strategic_rationale and len(strategic_rationale) > 50:
        strategic_score += 15

    # Adjust for benefits
    if len(benefits) >= 3:
        strategic_score += 20
    elif len(benefits) >= 1:
        strategic_score += 10

    # Adjust for precedents
    if len(precedents) >= 2:
        strategic_score += 15
    elif len(precedents) >= 1:
        strategic_score += 10

    strategic_score = min(strategic_score, 100)

    # Generate alignment summary
    alignment_summary = ""

    if strategic_rationale:
        alignment_summary += f"Strategic Rationale: {strategic_rationale[:150]}"
        if len(strategic_rationale) > 150:
            alignment_summary += "..."
        alignment_summary += "\n\n"

    if benefits:
        alignment_summary += f"Key Benefits ({len(benefits)}):\n"
        for idx, benefit in enumerate(benefits[:3], 1):
            alignment_summary += f"{idx}. {benefit}\n"
        if len(benefits) > 3:
            alignment_summary += f"... and {len(benefits) - 3} more\n"
        alignment_summary += "\n"

    if precedents:
        alignment_summary += f"Supporting Precedents ({len(precedents)}):\n"
        for precedent in precedents[:2]:
            alignment_summary += f"- {precedent.get('project', 'Unknown')}: {precedent.get('outcome', 'N/A')}\n"
        if len(precedents) > 2:
            alignment_summary += f"... and {len(precedents) - 2} more\n"

    return {
        'strategic_score': strategic_score,
        'benefits_count': len(benefits),
        'precedents_count': len(precedents),
        'alignment_summary': alignment_summary.strip()
    }


def generate_executive_recommendation(data: Dict) -> str:
    """
    Generate executive recommendation text combining all analysis.

    Args:
        data: Briefing note input data

    Returns:
        Formatted recommendation text
    """
    recommendation = data.get('recommendation', '')
    rationale = data.get('rationale', '')

    financial = data.get('financial_summary', {})
    total_cost = financial.get('total_cost', 0)

    # Get analysis
    urgency_analysis = analyze_decision_urgency(data)
    strategic_analysis = analyze_strategic_alignment(data)
    alternatives_analysis = analyze_alternatives(data)

    # Build recommendation text
    rec_text = f"## Recommendation\n\n"
    rec_text += f"**{recommendation}**\n\n"

    if rationale:
        rec_text += f"**Rationale:** {rationale}\n\n"

    rec_text += f"**Financial Impact:** ${total_cost:,.2f}\n\n"

    # Add urgency context
    rec_text += f"**Decision Urgency:** {urgency_analysis['urgency_level'].upper()}"
    if urgency_analysis['key_constraints']:
        rec_text += f" - {urgency_analysis['key_constraints'][0]}"
    rec_text += "\n\n"

    # Add strategic alignment
    if strategic_analysis['benefits_count'] > 0:
        rec_text += f"**Strategic Benefits:** {strategic_analysis['benefits_count']} key benefits identified"
        if strategic_analysis['precedents_count'] > 0:
            rec_text += f", {strategic_analysis['precedents_count']} supporting precedent(s)"
        rec_text += "\n\n"

    # Add alternatives context
    if alternatives_analysis['alternatives_count'] > 0:
        rec_text += f"**Alternatives Considered:** {alternatives_analysis['alternatives_count']} alternative(s) evaluated"

        # Find most cost-effective alternative
        if alternatives_analysis['cost_comparison']:
            cheapest = alternatives_analysis['cost_comparison'][0]
            if cheapest['cost'] < total_cost:
                savings = total_cost - cheapest['cost']
                rec_text += f" (lowest cost option would save ${savings:,.0f} but "
                # Get cons for cheapest alternative
                analysis_data = data.get('analysis', {})
                alternatives = analysis_data.get('alternatives_considered', [])
                cheapest_alt = next((a for a in alternatives if a.get('alternative') == cheapest['alternative']), None)
                if cheapest_alt and cheapest_alt.get('cons'):
                    rec_text += f"has significant drawbacks: {cheapest_alt['cons'][0]}"
                else:
                    rec_text += "was rejected for strategic reasons"
                rec_text += ")"

        rec_text += "\n\n"

    return rec_text


def calculate_overall_risk_score(risks: List[Dict]) -> Dict:
    """
    Calculate overall risk score from individual risks.

    Args:
        risks: List of risk dictionaries

    Returns:
        Dict with overall risk assessment
            {
                'overall_score': 65,
                'risk_level': 'MEDIUM',
                'critical_count': 0,
                'high_count': 2,
                'medium_count': 3,
                'low_count': 1
            }
    """
    if not risks:
        return {
            'overall_score': 0,
            'risk_level': 'LOW',
            'critical_count': 0,
            'high_count': 0,
            'medium_count': 0,
            'low_count': 0
        }

    # Count by severity
    severity_counts = {
        'CRITICAL': 0,
        'HIGH': 0,
        'MEDIUM': 0,
        'LOW': 0
    }

    severity_weights = {
        'CRITICAL': 100,
        'HIGH': 70,
        'MEDIUM': 40,
        'LOW': 15
    }

    total_weighted_score = 0

    for risk in risks:
        severity = risk.get('severity', 'MEDIUM')
        severity_counts[severity] += 1

        # Weight by probability if available
        probability = risk.get('probability', 0.5)
        base_score = severity_weights.get(severity, 40)
        weighted_score = base_score * probability

        total_weighted_score += weighted_score

    # Calculate overall score (average)
    overall_score = total_weighted_score / len(risks) if len(risks) > 0 else 0

    # Determine overall risk level
    if severity_counts['CRITICAL'] > 0 or overall_score >= 80:
        risk_level = 'CRITICAL'
    elif severity_counts['HIGH'] >= 2 or overall_score >= 60:
        risk_level = 'HIGH'
    elif severity_counts['HIGH'] >= 1 or overall_score >= 35:
        risk_level = 'MEDIUM'
    else:
        risk_level = 'LOW'

    return {
        'overall_score': round(overall_score, 1),
        'risk_level': risk_level,
        'critical_count': severity_counts['CRITICAL'],
        'high_count': severity_counts['HIGH'],
        'medium_count': severity_counts['MEDIUM'],
        'low_count': severity_counts['LOW']
    }
