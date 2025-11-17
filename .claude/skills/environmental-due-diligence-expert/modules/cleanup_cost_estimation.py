#!/usr/bin/env python3
"""
Cleanup Cost Estimation Module
Provides functions for estimating cleanup costs and calculating NPV.

Author: Claude Code
Created: 2025-11-17
"""

from typing import Dict, List, Optional
import logging
import sys
import os

# Add Shared_Utils to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from Shared_Utils.financial_utils import npv, present_value

logger = logging.getLogger(__name__)


def estimate_cleanup_costs(
    phase_2_data: Optional[Dict] = None,
    cleanup_scenarios: Optional[Dict] = None
) -> Dict:
    """
    Estimate cleanup costs across different scenarios.

    Args:
        phase_2_data: Phase II ESA results (optional)
        cleanup_scenarios: Predefined cleanup cost scenarios (optional)
            {
                'risk_assessment': {'cost_low': 50000, 'cost_high': 150000},
                'remediation': {'cost_low': 200000, 'cost_high': 500000},
                'brownfield': {'cost_low': 500000, 'cost_high': 1000000}
            }

    Returns:
        Dict containing cost estimates
            {
                'recommended_scenario': 'remediation',
                'scenarios': {
                    'risk_assessment': {...},
                    'remediation': {...},
                    'brownfield': {...}
                },
                'total_range': {'low': 200000, 'high': 500000},
                'most_likely': 350000
            }
    """
    scenarios = {}

    # Default cost ranges if not provided
    default_scenarios = {
        'risk_assessment': {
            'description': 'Phase II ESA + Risk Assessment only',
            'cost_low': 50000,
            'cost_high': 150000,
            'timeline_months': 3,
            'suitable_for': 'Minor contamination, low risk levels'
        },
        'remediation': {
            'description': 'Active remediation (excavation, soil treatment)',
            'cost_low': 100000,
            'cost_high': 500000,
            'timeline_months': 9,
            'suitable_for': 'Moderate contamination, localized impacts'
        },
        'brownfield': {
            'description': 'Brownfield redevelopment (extensive remediation)',
            'cost_low': 200000,
            'cost_high': 1000000,
            'timeline_months': 18,
            'suitable_for': 'Severe contamination, regulatory complexity'
        }
    }

    # Merge with provided scenarios
    if cleanup_scenarios:
        for scenario_name, scenario_data in cleanup_scenarios.items():
            if scenario_name in default_scenarios:
                default_scenarios[scenario_name].update(scenario_data)

    # Calculate most likely cost for each scenario (midpoint)
    for scenario_name, scenario_data in default_scenarios.items():
        cost_low = scenario_data.get('cost_low', 0)
        cost_high = scenario_data.get('cost_high', 0)
        most_likely = (cost_low + cost_high) / 2

        scenarios[scenario_name] = {
            **scenario_data,
            'most_likely': most_likely,
            'range_width': cost_high - cost_low
        }

    # Recommend scenario based on Phase II data
    recommended_scenario = _recommend_cleanup_scenario(phase_2_data, scenarios)

    # Get total range for recommended scenario
    recommended_data = scenarios[recommended_scenario]
    total_range = {
        'low': recommended_data['cost_low'],
        'high': recommended_data['cost_high']
    }
    most_likely = recommended_data['most_likely']

    return {
        'recommended_scenario': recommended_scenario,
        'scenarios': scenarios,
        'total_range': total_range,
        'most_likely': most_likely,
        'timeline_months': recommended_data['timeline_months']
    }


def calculate_npv_cleanup_costs(
    cleanup_costs: Dict,
    discount_rate: float = 0.055,
    payment_timing: str = 'upfront'
) -> Dict:
    """
    Calculate NPV of cleanup costs.

    Args:
        cleanup_costs: Output from estimate_cleanup_costs()
        discount_rate: Discount rate (default 5.5%)
        payment_timing: When costs are incurred
            'upfront' - All costs paid immediately (default)
            'distributed' - Costs paid over project timeline

    Returns:
        Dict containing NPV calculations
            {
                'npv_low': 195000,
                'npv_high': 475000,
                'npv_most_likely': 335000,
                'discount_rate': 0.055,
                'payment_timing': 'upfront'
            }
    """
    total_range = cleanup_costs.get('total_range', {})
    most_likely = cleanup_costs.get('most_likely', 0)
    timeline_months = cleanup_costs.get('timeline_months', 6)

    if payment_timing == 'upfront':
        # No discounting needed - costs paid immediately
        npv_low = total_range.get('low', 0)
        npv_high = total_range.get('high', 0)
        npv_most_likely = most_likely

    else:  # distributed
        # Assume costs distributed evenly over project timeline
        low_cost = total_range.get('low', 0)
        high_cost = total_range.get('high', 0)

        # Create cash flow streams (monthly payments)
        months = timeline_months
        monthly_payment_low = low_cost / months
        monthly_payment_high = high_cost / months
        monthly_payment_likely = most_likely / months

        # Calculate NPV using monthly cash flows
        monthly_rate = discount_rate / 12

        npv_low = sum(
            present_value(monthly_payment_low, monthly_rate, month)
            for month in range(1, months + 1)
        )
        npv_high = sum(
            present_value(monthly_payment_high, monthly_rate, month)
            for month in range(1, months + 1)
        )
        npv_most_likely = sum(
            present_value(monthly_payment_likely, monthly_rate, month)
            for month in range(1, months + 1)
        )

    return {
        'npv_low': round(npv_low, 2),
        'npv_high': round(npv_high, 2),
        'npv_most_likely': round(npv_most_likely, 2),
        'discount_rate': discount_rate,
        'payment_timing': payment_timing,
        'timeline_months': timeline_months,
        'discount_factor': round(npv_most_likely / most_likely, 4) if most_likely > 0 else 1.0
    }


def estimate_cost_by_scenario(
    scenario_name: str,
    contamination_severity: str = 'MEDIUM',
    site_size_sf: Optional[int] = None
) -> Dict:
    """
    Estimate costs for specific cleanup scenario.

    Args:
        scenario_name: 'risk_assessment', 'remediation', or 'brownfield'
        contamination_severity: 'LOW', 'MEDIUM', or 'HIGH'
        site_size_sf: Site size in square feet (optional, for cost scaling)

    Returns:
        Dict containing scenario-specific cost estimate
            {
                'scenario': 'remediation',
                'cost_low': 200000,
                'cost_high': 500000,
                'cost_per_sf': 5.00,
                'adjustments': {...}
            }
    """
    # Base cost ranges
    base_costs = {
        'risk_assessment': {'low': 50000, 'high': 150000},
        'remediation': {'low': 100000, 'high': 500000},
        'brownfield': {'low': 200000, 'high': 1000000}
    }

    if scenario_name not in base_costs:
        raise ValueError(f"Unknown scenario: {scenario_name}")

    base_low = base_costs[scenario_name]['low']
    base_high = base_costs[scenario_name]['high']

    # Adjust for contamination severity
    severity_multipliers = {
        'LOW': 0.7,
        'MEDIUM': 1.0,
        'HIGH': 1.4
    }
    multiplier = severity_multipliers.get(contamination_severity, 1.0)

    cost_low = base_low * multiplier
    cost_high = base_high * multiplier

    # Adjust for site size if provided
    cost_per_sf = None
    if site_size_sf:
        # Typical costs: $5-20/sf for remediation
        if scenario_name == 'risk_assessment':
            cost_per_sf = (cost_low + cost_high) / 2 / site_size_sf
        elif scenario_name == 'remediation':
            cost_per_sf = (cost_low + cost_high) / 2 / site_size_sf
        else:  # brownfield
            cost_per_sf = (cost_low + cost_high) / 2 / site_size_sf

    return {
        'scenario': scenario_name,
        'contamination_severity': contamination_severity,
        'cost_low': round(cost_low, 2),
        'cost_high': round(cost_high, 2),
        'cost_most_likely': round((cost_low + cost_high) / 2, 2),
        'cost_per_sf': round(cost_per_sf, 2) if cost_per_sf else None,
        'site_size_sf': site_size_sf,
        'adjustments': {
            'base_cost_low': base_low,
            'base_cost_high': base_high,
            'severity_multiplier': multiplier
        }
    }


def _recommend_cleanup_scenario(
    phase_2_data: Optional[Dict],
    scenarios: Dict
) -> str:
    """
    Recommend cleanup scenario based on Phase II data.

    Args:
        phase_2_data: Phase II ESA results
        scenarios: Available cleanup scenarios

    Returns:
        Recommended scenario name
    """
    if not phase_2_data:
        # No Phase II data - assume risk assessment only
        return 'risk_assessment'

    # Check exceedances count
    exceedances_count = len(phase_2_data.get('exceedances', []))

    if exceedances_count == 0:
        return 'risk_assessment'
    elif exceedances_count <= 2:
        return 'remediation'
    else:
        # Check for high-risk contaminants
        contaminants = phase_2_data.get('contaminants', [])
        high_risk = ['vocs', 'heavy metals', 'pcb', 'dnapl']

        for contaminant in contaminants:
            if any(risk in str(contaminant).lower() for risk in high_risk):
                return 'brownfield'

        return 'remediation'
