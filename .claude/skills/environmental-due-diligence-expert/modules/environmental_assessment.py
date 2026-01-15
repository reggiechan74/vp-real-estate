#!/usr/bin/env python3
"""
Environmental Assessment Module
Provides functions for parsing Phase I/II ESA findings and scoring contamination risk.

Author: Claude Code
Created: 2025-11-17
"""

from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


def parse_phase_i_findings(phase_1_data: Dict) -> Dict:
    """
    Parse Phase I ESA findings.

    Args:
        phase_1_data: Phase I ESA data dictionary
            {
                'findings': ['AST present', 'Historical dry cleaner'],
                'recs': [{...}],
                'data_gaps': [...]
            }

    Returns:
        Dict containing parsed Phase I findings
            {
                'findings_count': 2,
                'findings': [...],
                'recs_count': 1,
                'recs': [...],
                'data_gaps_count': 0,
                'requires_phase_2': True,
                'risk_indicators': [...]
            }
    """
    findings = phase_1_data.get('findings', [])
    recs = phase_1_data.get('recs', [])
    data_gaps = phase_1_data.get('data_gaps', [])

    # Identify risk indicators from findings
    risk_indicators = []
    high_risk_keywords = [
        'ust', 'underground storage tank', 'ast', 'above ground storage tank',
        'dry cleaner', 'gas station', 'auto repair', 'chemical', 'industrial',
        'manufacturing', 'landfill', 'waste', 'spill', 'staining', 'odor'
    ]

    for finding in findings:
        finding_lower = str(finding).lower()
        for keyword in high_risk_keywords:
            if keyword in finding_lower:
                risk_indicators.append({
                    'finding': finding,
                    'keyword': keyword,
                    'severity': 'HIGH' if keyword in ['ust', 'underground storage tank', 'dry cleaner'] else 'MEDIUM'
                })
                break

    # Determine if Phase II is required
    requires_phase_2 = len(recs) > 0 or len(risk_indicators) > 0

    return {
        'findings_count': len(findings),
        'findings': findings,
        'recs_count': len(recs),
        'recs': recs,
        'data_gaps_count': len(data_gaps),
        'data_gaps': data_gaps,
        'requires_phase_2': requires_phase_2,
        'risk_indicators': risk_indicators,
        'risk_indicator_count': len(risk_indicators)
    }


def parse_phase_ii_results(phase_2_data: Dict) -> Dict:
    """
    Parse Phase II ESA results.

    Args:
        phase_2_data: Phase II ESA data dictionary
            {
                'soil_samples': [{...}],
                'groundwater_samples': [{...}],
                'exceedances': [...],
                'contaminants': ['Petroleum hydrocarbons', 'VOCs']
            }

    Returns:
        Dict containing parsed Phase II results
            {
                'soil_samples_count': 5,
                'groundwater_samples_count': 3,
                'exceedances_count': 2,
                'exceedances': [...],
                'contaminants': [...],
                'contamination_severity': 'MEDIUM'
            }
    """
    soil_samples = phase_2_data.get('soil_samples', [])
    groundwater_samples = phase_2_data.get('groundwater_samples', [])
    exceedances = phase_2_data.get('exceedances', [])
    contaminants = phase_2_data.get('contaminants', [])

    # Determine contamination severity
    contamination_severity = _assess_contamination_severity(exceedances, contaminants)

    return {
        'soil_samples_count': len(soil_samples),
        'soil_samples': soil_samples,
        'groundwater_samples_count': len(groundwater_samples),
        'groundwater_samples': groundwater_samples,
        'exceedances_count': len(exceedances),
        'exceedances': exceedances,
        'contaminants': contaminants,
        'contaminants_count': len(contaminants),
        'contamination_severity': contamination_severity
    }


def identify_recognized_environmental_conditions(
    phase_1_data: Optional[Dict] = None,
    phase_2_data: Optional[Dict] = None
) -> List[Dict]:
    """
    Identify Recognized Environmental Conditions (RECs) from Phase I/II data.

    Args:
        phase_1_data: Phase I ESA data (optional)
        phase_2_data: Phase II ESA data (optional)

    Returns:
        List of REC dictionaries
            [
                {
                    'source': 'Phase I',
                    'description': 'AST present with staining',
                    'severity': 'HIGH',
                    'requires_action': True
                },
                ...
            ]
    """
    recs = []

    # Extract Phase I RECs
    if phase_1_data:
        phase_1_recs = phase_1_data.get('recs', [])
        for rec in phase_1_recs:
            recs.append({
                'source': 'Phase I ESA',
                'description': rec.get('description', str(rec)),
                'severity': rec.get('severity', 'MEDIUM'),
                'requires_action': True,
                'type': 'REC'
            })

        # Also check findings for potential RECs
        findings = phase_1_data.get('findings', [])
        high_risk_findings = [
            f for f in findings
            if any(keyword in str(f).lower() for keyword in ['ust', 'spill', 'staining', 'odor'])
        ]
        for finding in high_risk_findings:
            recs.append({
                'source': 'Phase I ESA - Finding',
                'description': finding,
                'severity': 'HIGH',
                'requires_action': True,
                'type': 'Potential REC'
            })

    # Extract Phase II RECs (exceedances)
    if phase_2_data:
        exceedances = phase_2_data.get('exceedances', [])
        for exceedance in exceedances:
            recs.append({
                'source': 'Phase II ESA',
                'description': exceedance.get('description', str(exceedance)),
                'severity': exceedance.get('severity', 'HIGH'),
                'requires_action': True,
                'type': 'Confirmed REC',
                'contaminant': exceedance.get('contaminant', 'Unknown'),
                'exceedance_factor': exceedance.get('exceedance_factor', 'N/A')
            })

    return recs


def score_contamination_risk(
    phase_1_data: Optional[Dict] = None,
    phase_2_data: Optional[Dict] = None,
    cleanup_scenarios: Optional[Dict] = None
) -> Dict:
    """
    Score overall contamination risk (HIGH/MEDIUM/LOW).

    Scoring criteria:
    - Severity of contamination (Phase II results)
    - Number of RECs and exceedances
    - Regulatory complexity
    - Remediation feasibility
    - Financial impact

    Args:
        phase_1_data: Phase I ESA data (optional)
        phase_2_data: Phase II ESA data (optional)
        cleanup_scenarios: Cleanup cost scenarios (optional)

    Returns:
        Dict containing risk score and breakdown
            {
                'total_score': 75,
                'risk_level': 'HIGH',
                'breakdown': {
                    'contamination_severity_score': 25,
                    'regulatory_complexity_score': 20,
                    'remediation_feasibility_score': 15,
                    'financial_impact_score': 15
                },
                'factors': [...],
                'recommendations': [...]
            }
    """
    # Initialize scores (max 100)
    contamination_severity_score = 0  # Max 30
    regulatory_complexity_score = 0   # Max 25
    remediation_feasibility_score = 0 # Max 25
    financial_impact_score = 0        # Max 20

    # Score contamination severity (0-30)
    if phase_2_data:
        exceedances_count = len(phase_2_data.get('exceedances', []))
        contaminants = phase_2_data.get('contaminants', [])

        # Exceedances count
        if exceedances_count >= 5:
            contamination_severity_score += 15
        elif exceedances_count >= 3:
            contamination_severity_score += 10
        elif exceedances_count >= 1:
            contamination_severity_score += 5

        # Contaminant types
        high_risk_contaminants = ['vocs', 'volatile organic compounds', 'heavy metals', 'pcb', 'dnapl']
        for contaminant in contaminants:
            if any(risk in str(contaminant).lower() for risk in high_risk_contaminants):
                contamination_severity_score += 5
                break

        # Severity assessment
        severity = phase_2_data.get('contamination_severity', 'MEDIUM')
        severity_scores = {'LOW': 5, 'MEDIUM': 10, 'HIGH': 15}
        contamination_severity_score += severity_scores.get(severity, 10)

    elif phase_1_data:
        # Phase I only - lower severity score
        recs_count = len(phase_1_data.get('recs', []))
        if recs_count >= 3:
            contamination_severity_score = 15
        elif recs_count >= 1:
            contamination_severity_score = 10

    # Cap at 30
    contamination_severity_score = min(contamination_severity_score, 30)

    # Score regulatory complexity (0-25)
    if phase_2_data and phase_2_data.get('exceedances'):
        # Confirmed contamination = regulatory pathway required
        regulatory_complexity_score = 15

        # High complexity for certain contaminants
        contaminants = phase_2_data.get('contaminants', [])
        if any('heavy metal' in str(c).lower() or 'pcb' in str(c).lower() for c in contaminants):
            regulatory_complexity_score += 5

        # Groundwater contamination adds complexity
        if phase_2_data.get('groundwater_samples_count', 0) > 0:
            regulatory_complexity_score += 5

    elif phase_1_data and phase_1_data.get('recs'):
        # RECs suggest likely regulatory pathway
        regulatory_complexity_score = 10

    # Cap at 25
    regulatory_complexity_score = min(regulatory_complexity_score, 25)

    # Score remediation feasibility (inverse - higher score = less feasible = higher risk) (0-25)
    if phase_2_data:
        # Groundwater contamination is harder to remediate
        if phase_2_data.get('groundwater_samples_count', 0) > 0:
            remediation_feasibility_score += 10

        # Multiple contaminant types
        if len(phase_2_data.get('contaminants', [])) >= 3:
            remediation_feasibility_score += 8
        elif len(phase_2_data.get('contaminants', [])) >= 2:
            remediation_feasibility_score += 5

        # High exceedance factors
        exceedances = phase_2_data.get('exceedances', [])
        for exceedance in exceedances:
            factor = exceedance.get('exceedance_factor', 1)
            if isinstance(factor, (int, float)) and factor > 10:
                remediation_feasibility_score += 7
                break

    # Cap at 25
    remediation_feasibility_score = min(remediation_feasibility_score, 25)

    # Score financial impact (0-20)
    if cleanup_scenarios:
        # Check highest likely cost
        max_cost = 0
        for scenario_name, scenario_data in cleanup_scenarios.items():
            if isinstance(scenario_data, dict):
                high_cost = scenario_data.get('cost_high', 0)
                max_cost = max(max_cost, high_cost)

        # Score based on cost ranges
        if max_cost >= 1000000:  # $1M+
            financial_impact_score = 20
        elif max_cost >= 500000:  # $500K+
            financial_impact_score = 15
        elif max_cost >= 200000:  # $200K+
            financial_impact_score = 10
        elif max_cost >= 100000:  # $100K+
            financial_impact_score = 5

    # Cap at 20
    financial_impact_score = min(financial_impact_score, 20)

    # Calculate total score
    total_score = (
        contamination_severity_score +
        regulatory_complexity_score +
        remediation_feasibility_score +
        financial_impact_score
    )

    # Determine risk level
    if total_score >= 70:
        risk_level = 'HIGH'
    elif total_score >= 40:
        risk_level = 'MEDIUM'
    else:
        risk_level = 'LOW'

    # Identify key factors
    factors = []
    if contamination_severity_score >= 20:
        factors.append('Significant contamination confirmed in Phase II')
    if regulatory_complexity_score >= 15:
        factors.append('Complex regulatory pathway required')
    if remediation_feasibility_score >= 15:
        factors.append('Remediation challenges (groundwater/multiple contaminants)')
    if financial_impact_score >= 15:
        factors.append('High financial impact ($500K+ cleanup costs)')

    # Generate recommendations
    recommendations = []
    if risk_level == 'HIGH':
        recommendations.append('Require seller indemnity for environmental liabilities')
        recommendations.append('Obtain environmental insurance (pollution liability)')
        recommendations.append('Negotiate significant purchase price reduction')
        recommendations.append('Consider walk-away rights if costs exceed threshold')
    elif risk_level == 'MEDIUM':
        recommendations.append('Negotiate cost-sharing for remediation')
        recommendations.append('Holdback 150-200% of estimated cleanup costs')
        recommendations.append('Require seller cooperation with regulatory filings')
    else:
        recommendations.append('Standard environmental representations and warranties')
        recommendations.append('Minimal holdback or seller cooperation for Phase II')

    return {
        'total_score': total_score,
        'risk_level': risk_level,
        'breakdown': {
            'contamination_severity_score': contamination_severity_score,
            'regulatory_complexity_score': regulatory_complexity_score,
            'remediation_feasibility_score': remediation_feasibility_score,
            'financial_impact_score': financial_impact_score
        },
        'factors': factors,
        'recommendations': recommendations
    }


def _assess_contamination_severity(exceedances: List, contaminants: List[str]) -> str:
    """
    Assess contamination severity from exceedances and contaminant types.

    Args:
        exceedances: List of exceedance dictionaries
        contaminants: List of contaminant names

    Returns:
        Severity level: 'HIGH', 'MEDIUM', or 'LOW'
    """
    if len(exceedances) >= 5:
        return 'HIGH'

    # Check for high-risk contaminants
    high_risk = ['vocs', 'volatile organic compounds', 'heavy metals', 'pcb', 'dnapl', 'benzene']
    for contaminant in contaminants:
        if any(risk in str(contaminant).lower() for risk in high_risk):
            return 'HIGH'

    if len(exceedances) >= 2:
        return 'MEDIUM'

    if len(exceedances) >= 1:
        return 'MEDIUM'

    return 'LOW'
