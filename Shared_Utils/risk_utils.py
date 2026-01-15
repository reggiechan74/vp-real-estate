#!/usr/bin/env python3
"""
Risk Assessment Utilities Module
Provides shared functions for holdout risk assessment, litigation risk analysis,
probability distributions, Monte Carlo simulation, and sensitivity analysis.

Used by:
- settlement_analyzer.py
- negotiation_settlement_calculator.py
- land_assembly_calculator.py
"""

from typing import Dict, List, Optional, Tuple
import random
import statistics


def assess_holdout_risk(owner_profile: Dict) -> Dict:
    """
    Calculate holdout risk score (0-30) from motivation/sophistication/alternatives.

    Holdout risk is the probability that an owner will refuse reasonable offers
    and force expropriation proceedings.

    Args:
        owner_profile: Dict with owner characteristics
            {
                'motivation': {
                    'financial_need': 'low',  # low/medium/high
                    'emotional_attachment': 'high',  # low/medium/high
                    'business_impact': 'critical'  # minimal/moderate/critical
                },
                'sophistication': {
                    'real_estate_experience': 'high',  # low/medium/high
                    'legal_representation': True,
                    'previous_negotiations': 3
                },
                'alternatives': {
                    'relocation_options': 'limited',  # many/some/limited/none
                    'financial_flexibility': 'low',
                    'timeline_pressure': 'low'  # low/medium/high
                }
            }

    Returns:
        Dict containing holdout risk assessment (0-30 scale)
            {
                'total_score': 22,
                'risk_level': 'HIGH',
                'breakdown': {
                    'motivation_score': 9,
                    'sophistication_score': 8,
                    'alternatives_score': 5
                },
                'factors': [...],
                'mitigation_strategies': [...]
            }
    """
    # Score motivation (0-12)
    motivation = owner_profile.get('motivation', {})
    motivation_score = 0

    # Financial need (inverse scoring - high need = low holdout)
    financial_need_scores = {'low': 4, 'medium': 2, 'high': 0}
    motivation_score += financial_need_scores.get(
        motivation.get('financial_need', 'medium'), 2
    )

    # Emotional attachment (high attachment = high holdout)
    emotional_scores = {'low': 0, 'medium': 2, 'high': 4}
    motivation_score += emotional_scores.get(
        motivation.get('emotional_attachment', 'medium'), 2
    )

    # Business impact (critical impact = high holdout)
    business_scores = {'minimal': 0, 'moderate': 2, 'critical': 4}
    motivation_score += business_scores.get(
        motivation.get('business_impact', 'moderate'), 2
    )

    # Score sophistication (0-10)
    sophistication = owner_profile.get('sophistication', {})
    sophistication_score = 0

    # Real estate experience (high experience = higher holdout)
    experience_scores = {'low': 1, 'medium': 3, 'high': 5}
    sophistication_score += experience_scores.get(
        sophistication.get('real_estate_experience', 'medium'), 3
    )

    # Legal representation (increases holdout)
    if sophistication.get('legal_representation', False):
        sophistication_score += 3

    # Previous negotiations (experience increases holdout)
    prev_negotiations = sophistication.get('previous_negotiations', 0)
    if prev_negotiations >= 3:
        sophistication_score += 2
    elif prev_negotiations >= 1:
        sophistication_score += 1

    # Score alternatives (0-8)
    alternatives = owner_profile.get('alternatives', {})
    alternatives_score = 0

    # Relocation options (fewer options = higher holdout)
    relocation_scores = {'many': 0, 'some': 2, 'limited': 4, 'none': 6}
    alternatives_score += relocation_scores.get(
        alternatives.get('relocation_options', 'some'), 2
    )

    # Financial flexibility (low flexibility = lower holdout - need money)
    flexibility_scores = {'high': 2, 'medium': 1, 'low': 0}
    alternatives_score += flexibility_scores.get(
        alternatives.get('financial_flexibility', 'medium'), 1
    )

    # Timeline pressure (high pressure = lower holdout - need to move)
    # This is inverse scoring
    timeline_scores = {'low': 2, 'medium': 1, 'high': 0}
    alternatives_score += timeline_scores.get(
        alternatives.get('timeline_pressure', 'medium'), 1
    )

    # Calculate total (max 30)
    total_score = min(motivation_score + sophistication_score + alternatives_score, 30)

    # Determine risk level
    if total_score >= 20:
        risk_level = 'CRITICAL'
        probability = 0.7  # 70% chance of holdout
    elif total_score >= 15:
        risk_level = 'HIGH'
        probability = 0.5  # 50% chance
    elif total_score >= 10:
        risk_level = 'MEDIUM'
        probability = 0.3  # 30% chance
    else:
        risk_level = 'LOW'
        probability = 0.15  # 15% chance

    # Identify key factors
    factors = []
    if motivation_score >= 8:
        factors.append('Strong emotional/business motivations to resist')
    if sophistication_score >= 7:
        factors.append('Sophisticated owner with legal representation')
    if alternatives_score >= 6:
        factors.append('Limited alternatives increase resistance')

    # Mitigation strategies
    mitigation_strategies = []
    if motivation.get('emotional_attachment') == 'high':
        mitigation_strategies.append('Emphasize fair compensation and respectful process')
    if alternatives.get('relocation_options') in ['limited', 'none']:
        mitigation_strategies.append('Provide relocation assistance and finder services')
    if sophistication.get('real_estate_experience') == 'high':
        mitigation_strategies.append('Use market comparables and professional appraisals')
    if motivation.get('business_impact') == 'critical':
        mitigation_strategies.append('Negotiate transition timeline and business continuity')

    return {
        'total_score': total_score,
        'risk_level': risk_level,
        'holdout_probability': probability,
        'breakdown': {
            'motivation_score': motivation_score,
            'sophistication_score': sophistication_score,
            'alternatives_score': alternatives_score
        },
        'factors': factors,
        'mitigation_strategies': mitigation_strategies
    }


def litigation_risk_assessment(case_factors: Dict) -> Dict:
    """
    Assess litigation probability and expected duration.

    Args:
        case_factors: Dict with case characteristics
            {
                'valuation_gap': 50000,  # Difference in valuations
                'property_value': 200000,
                'owner_risk_profile': 'HIGH',  # From assess_holdout_risk
                'legal_complexity': 'medium',  # low/medium/high
                'precedent_clarity': 'clear',  # clear/mixed/unclear
                'jurisdiction_history': 'owner_favorable'  # owner_favorable/neutral/buyer_favorable
            }

    Returns:
        Dict containing litigation risk analysis
            {
                'litigation_probability': 0.6,
                'expected_duration_months': 18,
                'expected_cost': 85000,
                'risk_factors': [...],
                'duration_range': {'best': 12, 'likely': 18, 'worst': 30}
            }
    """
    # Base litigation probability
    valuation_gap = case_factors.get('valuation_gap', 0)
    property_value = case_factors.get('property_value', 1)
    gap_percentage = (valuation_gap / property_value) * 100 if property_value > 0 else 0

    # Probability based on valuation gap
    if gap_percentage < 10:
        base_prob = 0.2
    elif gap_percentage < 20:
        base_prob = 0.4
    elif gap_percentage < 30:
        base_prob = 0.6
    else:
        base_prob = 0.8

    # Adjust for owner risk profile
    risk_profile = case_factors.get('owner_risk_profile', 'MEDIUM')
    risk_multipliers = {'LOW': 0.5, 'MEDIUM': 1.0, 'HIGH': 1.5, 'CRITICAL': 2.0}
    base_prob *= risk_multipliers.get(risk_profile, 1.0)

    # Adjust for legal complexity
    complexity = case_factors.get('legal_complexity', 'medium')
    complexity_adj = {'low': -0.1, 'medium': 0, 'high': 0.15}
    base_prob += complexity_adj.get(complexity, 0)

    # Adjust for precedent clarity
    precedent = case_factors.get('precedent_clarity', 'clear')
    precedent_adj = {'clear': -0.15, 'mixed': 0, 'unclear': 0.2}
    base_prob += precedent_adj.get(precedent, 0)

    # Cap at 0.95
    litigation_probability = min(base_prob, 0.95)

    # Estimate duration (months)
    base_duration = 12  # Base case

    # Adjust for complexity
    complexity_duration = {'low': -3, 'medium': 0, 'high': 6}
    base_duration += complexity_duration.get(complexity, 0)

    # Adjust for precedent clarity
    precedent_duration = {'clear': -2, 'mixed': 0, 'unclear': 4}
    base_duration += precedent_duration.get(precedent, 0)

    # Adjust for jurisdiction
    jurisdiction = case_factors.get('jurisdiction_history', 'neutral')
    jurisdiction_duration = {'buyer_favorable': -2, 'neutral': 0, 'owner_favorable': 3}
    base_duration += jurisdiction_duration.get(jurisdiction, 0)

    expected_duration = max(base_duration, 6)  # Minimum 6 months

    # Duration scenarios
    duration_range = {
        'best': max(expected_duration * 0.7, 6),
        'likely': expected_duration,
        'worst': expected_duration * 1.5
    }

    # Estimate costs (legal + expert fees)
    # $5k-10k per month depending on complexity
    cost_per_month = {'low': 5000, 'medium': 7500, 'high': 10000}
    monthly_cost = cost_per_month.get(complexity, 7500)
    expected_cost = monthly_cost * expected_duration

    # Identify risk factors
    risk_factors = []
    if gap_percentage > 25:
        risk_factors.append(f'Large valuation gap ({gap_percentage:.0f}%)')
    if risk_profile in ['HIGH', 'CRITICAL']:
        risk_factors.append(f'{risk_profile} holdout risk profile')
    if complexity == 'high':
        risk_factors.append('High legal complexity')
    if precedent == 'unclear':
        risk_factors.append('Unclear legal precedent')
    if jurisdiction == 'owner_favorable':
        risk_factors.append('Owner-favorable jurisdiction history')

    return {
        'litigation_probability': round(litigation_probability, 3),
        'expected_duration_months': round(expected_duration, 1),
        'expected_cost': round(expected_cost, 2),
        'risk_factors': risk_factors,
        'duration_range': {
            'best': round(duration_range['best'], 1),
            'likely': round(duration_range['likely'], 1),
            'worst': round(duration_range['worst'], 1)
        },
        'cost_range': {
            'best': round(monthly_cost * duration_range['best'], 2),
            'likely': round(expected_cost, 2),
            'worst': round(monthly_cost * duration_range['worst'], 2)
        }
    }


def probability_distribution(
    scenarios: List[Dict],
    distribution_type: str = 'discrete'
) -> Dict:
    """
    Generate probability distributions (normal, triangular, discrete).

    Args:
        scenarios: List of scenario dicts with values and probabilities
        distribution_type: 'normal', 'triangular', or 'discrete'

    Returns:
        Dict containing distribution parameters
    """
    if distribution_type == 'discrete':
        # Discrete distribution - use scenarios as given
        return {
            'type': 'discrete',
            'scenarios': scenarios,
            'mean': sum(s['value'] * s['probability'] for s in scenarios),
            'scenarios_count': len(scenarios)
        }

    # For continuous distributions, extract values
    values = [s['value'] for s in scenarios]

    if distribution_type == 'triangular':
        # Triangular distribution (min, most_likely, max)
        return {
            'type': 'triangular',
            'min': min(values),
            'most_likely': values[len(values) // 2] if len(values) >= 3 else statistics.mean(values),
            'max': max(values),
            'mean': (min(values) + max(values) + values[len(values) // 2]) / 3 if len(values) >= 3 else statistics.mean(values)
        }

    elif distribution_type == 'normal':
        # Normal distribution (mean, std dev)
        mean = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0

        return {
            'type': 'normal',
            'mean': round(mean, 2),
            'std_dev': round(std_dev, 2),
            'confidence_95pct': {
                'lower': round(mean - 1.96 * std_dev, 2),
                'upper': round(mean + 1.96 * std_dev, 2)
            }
        }

    return {'error': f'Unknown distribution type: {distribution_type}'}


def monte_carlo_simulation(
    variables: Dict[str, Dict],
    iterations: int = 1000,
    seed: Optional[int] = None
) -> Dict:
    """
    Monte Carlo simulation for uncertain variables.

    Args:
        variables: Dict of variable distributions
            {
                'settlement_amount': {
                    'type': 'triangular',
                    'min': 150000,
                    'most_likely': 175000,
                    'max': 200000
                },
                'legal_costs': {
                    'type': 'normal',
                    'mean': 50000,
                    'std_dev': 10000
                }
            }
        iterations: Number of simulation iterations (default 1000)
        seed: Random seed for reproducibility

    Returns:
        Dict containing simulation results
            {
                'iterations': 1000,
                'results': {
                    'settlement_amount': {
                        'mean': 175432,
                        'std_dev': 15234,
                        'percentiles': {'p10': 155000, 'p50': 175000, 'p90': 195000}
                    },
                    ...
                }
            }
    """
    if seed is not None:
        random.seed(seed)

    # Run simulation
    simulation_results = {var: [] for var in variables}

    for _ in range(iterations):
        for var_name, dist in variables.items():
            dist_type = dist.get('type', 'normal')

            if dist_type == 'triangular':
                value = random.triangular(
                    dist.get('min', 0),
                    dist.get('max', 100),
                    dist.get('most_likely', 50)
                )
            elif dist_type == 'normal':
                value = random.gauss(
                    dist.get('mean', 0),
                    dist.get('std_dev', 1)
                )
            elif dist_type == 'uniform':
                value = random.uniform(
                    dist.get('min', 0),
                    dist.get('max', 100)
                )
            else:
                value = dist.get('mean', 0)  # Fallback to deterministic

            simulation_results[var_name].append(value)

    # Calculate statistics
    results = {}
    for var_name, values in simulation_results.items():
        sorted_values = sorted(values)
        results[var_name] = {
            'mean': round(statistics.mean(values), 2),
            'std_dev': round(statistics.stdev(values), 2) if len(values) > 1 else 0,
            'min': round(min(values), 2),
            'max': round(max(values), 2),
            'percentiles': {
                'p10': round(sorted_values[int(iterations * 0.10)], 2),
                'p25': round(sorted_values[int(iterations * 0.25)], 2),
                'p50': round(sorted_values[int(iterations * 0.50)], 2),
                'p75': round(sorted_values[int(iterations * 0.75)], 2),
                'p90': round(sorted_values[int(iterations * 0.90)], 2)
            }
        }

    return {
        'iterations': iterations,
        'seed': seed,
        'results': results
    }


def sensitivity_analysis(
    base_case: Dict,
    variables: Dict[str, List[float]],
    ranges: Dict[str, Tuple[float, float]]
) -> Dict:
    """
    Sensitivity analysis showing impact of variable changes.

    Args:
        base_case: Base case calculation result
            {'total_cost': 250000, 'settlement': 200000, 'legal_costs': 50000}
        variables: Variables to test
            {'settlement': [180000, 200000, 220000], 'legal_costs': [40000, 50000, 60000]}
        ranges: Percentage ranges to test
            {'settlement': (-10, 10), 'legal_costs': (-20, 20)}

    Returns:
        Dict containing sensitivity analysis
            {
                'base_case': {...},
                'sensitivity': {
                    'settlement': {
                        'impact_per_percent': 2000,
                        'elasticity': 0.8,
                        'scenarios': [...]
                    }
                }
            }
    """
    base_value = base_case.get('total_cost', 0)
    sensitivity = {}

    for var_name, test_values in variables.items():
        if len(test_values) < 3:
            continue

        # Calculate impact at different values
        low_val, mid_val, high_val = test_values[0], test_values[1], test_values[2]
        low_result = base_value - (mid_val - low_val)
        high_result = base_value + (high_val - mid_val)

        # Impact per 1% change
        pct_range = ranges.get(var_name, (-10, 10))
        impact_per_pct = (high_result - low_result) / (pct_range[1] - pct_range[0])

        # Elasticity (% change in output / % change in input)
        pct_change_output = ((high_result - base_value) / base_value) * 100 if base_value > 0 else 0
        pct_change_input = pct_range[1]
        elasticity = pct_change_output / pct_change_input if pct_change_input != 0 else 0

        sensitivity[var_name] = {
            'base_value': mid_val,
            'impact_per_percent': round(impact_per_pct, 2),
            'elasticity': round(elasticity, 4),
            'scenarios': [
                {'value': low_val, 'result': round(low_result, 2), 'change_pct': pct_range[0]},
                {'value': mid_val, 'result': round(base_value, 2), 'change_pct': 0},
                {'value': high_val, 'result': round(high_result, 2), 'change_pct': pct_range[1]}
            ],
            'interpretation': (
                'High sensitivity' if abs(elasticity) > 1 else
                'Medium sensitivity' if abs(elasticity) > 0.5 else
                'Low sensitivity'
            )
        }

    # Rank by impact
    ranked = sorted(
        sensitivity.items(),
        key=lambda x: abs(x[1]['impact_per_percent']),
        reverse=True
    )

    return {
        'base_case': base_case,
        'sensitivity': sensitivity,
        'ranked_by_impact': [var for var, _ in ranked],
        'most_sensitive_variable': ranked[0][0] if ranked else None
    }
