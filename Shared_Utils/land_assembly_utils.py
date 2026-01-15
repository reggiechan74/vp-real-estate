#!/usr/bin/env python3
"""
Land Assembly Utilities Module
Provides shared functions for multi-parcel corridor acquisition budgeting,
phasing strategy, cost of delay analysis, and resource allocation.

Used by:
- land_assembly_calculator.py
- negotiation_strategy_planner.py
- project_timeline_calculator.py
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import statistics


def calculate_phasing_strategy(
    parcels: List[Dict],
    priorities: Dict[str, int]
) -> Dict:
    """
    Determine acquisition phasing (critical parcels first, parallel tracks).

    Args:
        parcels: List of parcel dicts
            [
                {
                    'id': 'P001',
                    'address': '123 Main St',
                    'area_sqm': 5000,
                    'estimated_value': 500000,
                    'criticality': 'critical',  # critical/high/medium/low
                    'complexity': 'medium',  # low/medium/high
                    'holdout_risk': 0.4
                },
                ...
            ]
        priorities: Dict with priority weights
            {'criticality': 0.5, 'holdout_risk': 0.3, 'complexity': 0.2}

    Returns:
        Dict containing phasing strategy
            {
                'phases': [
                    {
                        'phase': 1,
                        'parcels': ['P001', 'P003', ...],
                        'rationale': 'Critical parcels with high holdout risk',
                        'parallel_track': True
                    },
                    ...
                ],
                'parallel_tracks': [...],
                'total_parcels': 50
            }
    """
    # Calculate priority score for each parcel
    scored_parcels = []
    for parcel in parcels:
        # Criticality score
        criticality_scores = {'critical': 100, 'high': 75, 'medium': 50, 'low': 25}
        criticality_score = criticality_scores.get(parcel.get('criticality', 'medium'), 50)

        # Holdout risk score (higher risk = earlier acquisition)
        holdout_score = parcel.get('holdout_risk', 0.3) * 100

        # Complexity score (inverse - lower complexity = earlier)
        complexity_scores = {'low': 25, 'medium': 50, 'high': 75}
        complexity_score = 100 - complexity_scores.get(parcel.get('complexity', 'medium'), 50)

        # Weighted total
        total_score = (
            criticality_score * priorities.get('criticality', 0.5) +
            holdout_score * priorities.get('holdout_risk', 0.3) +
            complexity_score * priorities.get('complexity', 0.2)
        )

        scored_parcels.append({
            **parcel,
            'priority_score': round(total_score, 2),
            'scores': {
                'criticality': criticality_score,
                'holdout_risk': round(holdout_score, 2),
                'complexity': complexity_score
            }
        })

    # Sort by priority score (descending)
    scored_parcels.sort(key=lambda p: p['priority_score'], reverse=True)

    # Create phases (groups of parcels)
    # Phase 1: Top 20% or all critical parcels
    # Phase 2: Next 30% (high priority)
    # Phase 3: Next 30% (medium priority)
    # Phase 4: Remaining 20% (low priority)

    num_parcels = len(scored_parcels)
    phase_1_size = max(int(num_parcels * 0.2), len([p for p in parcels if p.get('criticality') == 'critical']))
    phase_2_size = int(num_parcels * 0.3)
    phase_3_size = int(num_parcels * 0.3)

    phases = []

    # Phase 1: Critical parcels
    phase_1_parcels = scored_parcels[:phase_1_size]
    phases.append({
        'phase': 1,
        'parcels': [p['id'] for p in phase_1_parcels],
        'count': len(phase_1_parcels),
        'rationale': 'Critical parcels - highest priority, acquired first',
        'parallel_track': True,  # Can acquire multiple in parallel
        'avg_priority_score': round(statistics.mean([p['priority_score'] for p in phase_1_parcels]), 1),
        'estimated_duration_days': 90,  # 3 months per parcel
        'criticality_breakdown': _count_by_field(phase_1_parcels, 'criticality')
    })

    # Phase 2: High priority
    phase_2_parcels = scored_parcels[phase_1_size:phase_1_size + phase_2_size]
    if phase_2_parcels:
        phases.append({
            'phase': 2,
            'parcels': [p['id'] for p in phase_2_parcels],
            'count': len(phase_2_parcels),
            'rationale': 'High priority parcels - acquired after critical parcels secured',
            'parallel_track': True,
            'avg_priority_score': round(statistics.mean([p['priority_score'] for p in phase_2_parcels]), 1),
            'estimated_duration_days': 120,  # 4 months
            'criticality_breakdown': _count_by_field(phase_2_parcels, 'criticality')
        })

    # Phase 3: Medium priority
    phase_3_parcels = scored_parcels[phase_1_size + phase_2_size:phase_1_size + phase_2_size + phase_3_size]
    if phase_3_parcels:
        phases.append({
            'phase': 3,
            'parcels': [p['id'] for p in phase_3_parcels],
            'count': len(phase_3_parcels),
            'rationale': 'Medium priority parcels - flexibility in timing',
            'parallel_track': False,  # Sequential acquisition
            'avg_priority_score': round(statistics.mean([p['priority_score'] for p in phase_3_parcels]), 1),
            'estimated_duration_days': 150,  # 5 months
            'criticality_breakdown': _count_by_field(phase_3_parcels, 'criticality')
        })

    # Phase 4: Remaining parcels
    phase_4_parcels = scored_parcels[phase_1_size + phase_2_size + phase_3_size:]
    if phase_4_parcels:
        phases.append({
            'phase': 4,
            'parcels': [p['id'] for p in phase_4_parcels],
            'count': len(phase_4_parcels),
            'rationale': 'Low priority parcels - acquired last',
            'parallel_track': False,
            'avg_priority_score': round(statistics.mean([p['priority_score'] for p in phase_4_parcels]), 1),
            'estimated_duration_days': 180,  # 6 months
            'criticality_breakdown': _count_by_field(phase_4_parcels, 'criticality')
        })

    # Identify parallel tracks (parcels that can be acquired simultaneously)
    parallel_tracks = _identify_parallel_tracks(scored_parcels, max_parallel=5)

    return {
        'phases': phases,
        'parallel_tracks': parallel_tracks,
        'total_parcels': num_parcels,
        'scored_parcels': scored_parcels[:10],  # Top 10 for reference
        'total_duration_estimate_days': sum(p.get('estimated_duration_days', 0) for p in phases)
    }


def _count_by_field(parcels: List[Dict], field: str) -> Dict:
    """Count parcels by a specific field."""
    counts = {}
    for parcel in parcels:
        value = parcel.get(field, 'unknown')
        counts[value] = counts.get(value, 0) + 1
    return counts


def _identify_parallel_tracks(parcels: List[Dict], max_parallel: int = 5) -> List[Dict]:
    """Identify parcels that can be acquired in parallel."""
    # Group by criticality for parallel acquisition
    critical = [p for p in parcels if p.get('criticality') == 'critical']
    high = [p for p in parcels if p.get('criticality') == 'high']

    tracks = []
    if critical:
        tracks.append({
            'track_name': 'Critical Track',
            'parcels': [p['id'] for p in critical[:max_parallel]],
            'rationale': 'Critical parcels acquired simultaneously'
        })

    if high:
        tracks.append({
            'track_name': 'High Priority Track',
            'parcels': [p['id'] for p in high[:max_parallel]],
            'rationale': 'High priority parcels in parallel after critical'
        })

    return tracks


def multi_parcel_budget(
    parcels: List[Dict],
    contingencies: Dict[str, float]
) -> Dict:
    """
    Budget for 10-100+ parcel acquisitions with contingencies.

    Args:
        parcels: List of parcel dicts with estimated values
        contingencies: Dict with contingency rates
            {
                'valuation_uncertainty': 0.10,  # 10% contingency for valuation
                'negotiation_premium': 0.05,    # 5% for negotiation
                'litigation_reserve': 0.15,     # 15% for potential litigation
                'inflation': 0.03               # 3% annual inflation
            }

    Returns:
        Dict containing budget analysis
            {
                'base_budget': 10000000,
                'contingencies': {...},
                'total_budget': 13500000,
                'per_parcel_avg': 270000,
                'budget_breakdown': [...]
            }
    """
    # Calculate base budget
    base_budget = sum(p.get('estimated_value', 0) for p in parcels)
    num_parcels = len(parcels)

    # Calculate contingencies
    valuation_contingency = base_budget * contingencies.get('valuation_uncertainty', 0.10)
    negotiation_premium = base_budget * contingencies.get('negotiation_premium', 0.05)
    litigation_reserve = base_budget * contingencies.get('litigation_reserve', 0.15)

    # Inflation adjustment (assume 18 month average timeline)
    inflation_rate = contingencies.get('inflation', 0.03)
    years = 1.5  # 18 months
    inflation_adjustment = base_budget * (inflation_rate * years)

    # Professional fees (appraisal, legal, environmental)
    appraisal_fees = num_parcels * contingencies.get('appraisal_cost_per_parcel', 5000)
    legal_fees = num_parcels * contingencies.get('legal_cost_per_parcel', 3000)
    environmental_fees = num_parcels * contingencies.get('environmental_cost_per_parcel', 2000)

    total_professional_fees = appraisal_fees + legal_fees + environmental_fees

    # Total budget
    total_contingencies = (
        valuation_contingency +
        negotiation_premium +
        litigation_reserve +
        inflation_adjustment +
        total_professional_fees
    )

    total_budget = base_budget + total_contingencies

    # Per parcel average
    per_parcel_avg = total_budget / num_parcels if num_parcels > 0 else 0

    # Budget breakdown by phase
    budget_by_criticality = {}
    for criticality in ['critical', 'high', 'medium', 'low']:
        crit_parcels = [p for p in parcels if p.get('criticality') == criticality]
        if crit_parcels:
            budget_by_criticality[criticality] = {
                'count': len(crit_parcels),
                'base_value': sum(p.get('estimated_value', 0) for p in crit_parcels),
                'percentage': round(
                    sum(p.get('estimated_value', 0) for p in crit_parcels) / base_budget * 100, 1
                ) if base_budget > 0 else 0
            }

    return {
        'base_budget': round(base_budget, 2),
        'contingencies': {
            'valuation_uncertainty': round(valuation_contingency, 2),
            'negotiation_premium': round(negotiation_premium, 2),
            'litigation_reserve': round(litigation_reserve, 2),
            'inflation_adjustment': round(inflation_adjustment, 2),
            'professional_fees': round(total_professional_fees, 2)
        },
        'total_contingencies': round(total_contingencies, 2),
        'total_budget': round(total_budget, 2),
        'per_parcel_avg': round(per_parcel_avg, 2),
        'budget_by_criticality': budget_by_criticality,
        'contingency_rate': round((total_contingencies / base_budget) * 100, 1) if base_budget > 0 else 0
    }


def cost_of_delay(
    delayed_parcels: List[Dict],
    project_impact: Dict
) -> Dict:
    """
    Calculate cost of delay (interest, project timeline, opportunity cost).

    Args:
        delayed_parcels: List of parcels that may be delayed
        project_impact: Dict with project cost parameters
            {
                'interest_rate': 0.05,  # 5% annual interest
                'construction_cost_per_day': 50000,
                'revenue_loss_per_day': 25000,
                'project_start_delay_days': 90
            }

    Returns:
        Dict containing cost of delay analysis
            {
                'interest_carrying_cost': 125000,
                'construction_delay_cost': 4500000,
                'revenue_loss': 2250000,
                'total_delay_cost': 6875000,
                'delay_cost_per_parcel': 137500
            }
    """
    num_parcels = len(delayed_parcels)
    if num_parcels == 0:
        return {'error': 'No delayed parcels provided'}

    # Total value of delayed parcels
    total_value = sum(p.get('estimated_value', 0) for p in delayed_parcels)

    # Interest carrying cost
    interest_rate = project_impact.get('interest_rate', 0.05)
    delay_days = project_impact.get('project_start_delay_days', 90)
    delay_years = delay_days / 365

    interest_cost = total_value * interest_rate * delay_years

    # Construction delay cost
    construction_cost_per_day = project_impact.get('construction_cost_per_day', 50000)
    construction_delay_cost = construction_cost_per_day * delay_days

    # Revenue loss (project can't open on time)
    revenue_loss_per_day = project_impact.get('revenue_loss_per_day', 0)
    revenue_loss = revenue_loss_per_day * delay_days

    # Total delay cost
    total_delay_cost = interest_cost + construction_delay_cost + revenue_loss

    # Per parcel
    delay_cost_per_parcel = total_delay_cost / num_parcels if num_parcels > 0 else 0

    return {
        'interest_carrying_cost': round(interest_cost, 2),
        'construction_delay_cost': round(construction_delay_cost, 2),
        'revenue_loss': round(revenue_loss, 2),
        'total_delay_cost': round(total_delay_cost, 2),
        'delay_cost_per_parcel': round(delay_cost_per_parcel, 2),
        'delay_days': delay_days,
        'num_delayed_parcels': num_parcels,
        'total_value_delayed_parcels': round(total_value, 2)
    }


def resource_allocation_plan(
    parcels: List[Dict],
    resources: Dict
) -> Dict:
    """
    Allocate appraisers, negotiators, legal support across parcels.

    Args:
        parcels: List of parcels
        resources: Dict with available resources
            {
                'appraisers': 3,
                'negotiators': 5,
                'legal_staff': 2,
                'appraisal_days_per_parcel': 10,
                'negotiation_days_per_parcel': 30,
                'legal_days_per_parcel': 5
            }

    Returns:
        Dict containing resource allocation plan
            {
                'total_appraisal_days': 500,
                'total_negotiation_days': 1500,
                'total_legal_days': 250,
                'timeline_with_resources': {
                    'appraisal_phase': 167,  # days with 3 appraisers
                    'negotiation_phase': 300,  # days with 5 negotiators
                    'legal_phase': 125  # days with 2 legal staff
                }
            }
    """
    num_parcels = len(parcels)

    # Calculate total days required
    appraisal_days = num_parcels * resources.get('appraisal_days_per_parcel', 10)
    negotiation_days = num_parcels * resources.get('negotiation_days_per_parcel', 30)
    legal_days = num_parcels * resources.get('legal_days_per_parcel', 5)

    # Calculate timeline with available resources
    num_appraisers = resources.get('appraisers', 1)
    num_negotiators = resources.get('negotiators', 1)
    num_legal = resources.get('legal_staff', 1)

    appraisal_phase_days = appraisal_days / num_appraisers if num_appraisers > 0 else appraisal_days
    negotiation_phase_days = negotiation_days / num_negotiators if num_negotiators > 0 else negotiation_days
    legal_phase_days = legal_days / num_legal if num_legal > 0 else legal_days

    # Calculate cost
    daily_rates = resources.get('daily_rates', {
        'appraiser': 1500,
        'negotiator': 1200,
        'legal': 2000
    })

    appraisal_cost = appraisal_days * daily_rates.get('appraiser', 1500)
    negotiation_cost = negotiation_days * daily_rates.get('negotiator', 1200)
    legal_cost = legal_days * daily_rates.get('legal', 2000)

    total_cost = appraisal_cost + negotiation_cost + legal_cost

    # Resource utilization
    utilization = {
        'appraisers': round((appraisal_phase_days / 365) * 100, 1),  # % of year utilized
        'negotiators': round((negotiation_phase_days / 365) * 100, 1),
        'legal': round((legal_phase_days / 365) * 100, 1)
    }

    return {
        'total_days_required': {
            'appraisal': round(appraisal_days, 1),
            'negotiation': round(negotiation_days, 1),
            'legal': round(legal_days, 1)
        },
        'timeline_with_resources': {
            'appraisal_phase_days': round(appraisal_phase_days, 1),
            'negotiation_phase_days': round(negotiation_phase_days, 1),
            'legal_phase_days': round(legal_phase_days, 1)
        },
        'total_cost': round(total_cost, 2),
        'cost_breakdown': {
            'appraisal': round(appraisal_cost, 2),
            'negotiation': round(negotiation_cost, 2),
            'legal': round(legal_cost, 2)
        },
        'resource_utilization': utilization,
        'num_parcels': num_parcels
    }


def contingency_budget(
    parcels: List[Dict],
    risk_factors: Dict[str, float]
) -> Dict:
    """
    Calculate contingency budget (price escalation, litigation reserves).

    Args:
        parcels: List of parcels
        risk_factors: Dict with risk percentages
            {
                'price_escalation': 0.05,  # 5% annual escalation
                'litigation_rate': 0.20,  # 20% of parcels may litigate
                'litigation_cost_multiplier': 1.5  # 50% premium for litigation
            }

    Returns:
        Dict containing contingency budget
    """
    base_value = sum(p.get('estimated_value', 0) for p in parcels)
    num_parcels = len(parcels)

    # Price escalation contingency
    escalation_rate = risk_factors.get('price_escalation', 0.05)
    escalation_years = risk_factors.get('acquisition_timeline_years', 2)
    price_escalation = base_value * escalation_rate * escalation_years

    # Litigation reserve
    litigation_rate = risk_factors.get('litigation_rate', 0.20)
    litigation_multiplier = risk_factors.get('litigation_cost_multiplier', 1.5)
    expected_litigation_parcels = num_parcels * litigation_rate
    litigation_value = base_value * litigation_rate
    litigation_premium = litigation_value * (litigation_multiplier - 1)

    # Total contingency
    total_contingency = price_escalation + litigation_premium

    return {
        'base_value': round(base_value, 2),
        'price_escalation_contingency': round(price_escalation, 2),
        'litigation_reserve': round(litigation_premium, 2),
        'total_contingency': round(total_contingency, 2),
        'contingency_percentage': round((total_contingency / base_value) * 100, 1) if base_value > 0 else 0,
        'expected_litigation_parcels': round(expected_litigation_parcels, 1)
    }
