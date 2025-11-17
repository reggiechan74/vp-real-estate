"""
Depreciation Analysis Module

Calculates physical, functional, and external obsolescence for infrastructure assets.
"""

from typing import Dict, Optional


def calculate_physical_depreciation(
    depreciation_data: Dict,
    replacement_cost_new: float
) -> Dict:
    """
    Calculate physical depreciation using age/life method and observed condition.

    Physical depreciation reflects wear and tear from use and exposure.

    Methods:
    1. Age/Life Method: (Effective Age ÷ Economic Life) × RCN
    2. Observed Condition Method: Based on physical inspection

    Args:
        depreciation_data: Dictionary with:
            - age_years: Actual age of asset
            - effective_age_years: Age reflecting condition (may differ from actual)
            - economic_life_years: Total economic life expectancy
            - physical_condition: 'Excellent', 'Good', 'Fair', 'Poor', 'Very Poor'
        replacement_cost_new: RCN value

    Returns:
        Dictionary with:
            - method: Depreciation method used
            - effective_age: Effective age in years
            - economic_life: Economic life in years
            - depreciation_rate: Percentage depreciated
            - physical_depreciation: Dollar amount
            - remaining_life: Years of remaining life
            - condition_rating: Physical condition assessment

    Example:
        >>> data = {
        ...     'age_years': 15,
        ...     'effective_age_years': 12,
        ...     'economic_life_years': 50,
        ...     'physical_condition': 'Good'
        ... }
        >>> dep = calculate_physical_depreciation(data, 289100)
        >>> print(f"Physical depreciation: ${dep['physical_depreciation']:,.2f}")
        Physical depreciation: $69,384.00
    """
    effective_age = depreciation_data.get('effective_age_years', 0)
    economic_life = depreciation_data.get('economic_life_years', 1)
    condition = depreciation_data.get('physical_condition', 'Good')

    # Age/Life Method
    if economic_life <= 0:
        raise ValueError(f"economic_life_years must be positive, got {economic_life}")

    # Cap effective age at economic life (100% depreciation maximum)
    capped_effective_age = min(effective_age, economic_life)
    depreciation_rate = capped_effective_age / economic_life

    # Calculate physical depreciation
    age_life_depreciation = replacement_cost_new * depreciation_rate

    # Observed Condition Method (as validation/adjustment)
    condition_factors = {
        'Excellent': 0.05,  # Nearly new condition
        'Good': 0.15,       # Well maintained, normal wear
        'Fair': 0.35,       # Some deferred maintenance
        'Poor': 0.60,       # Significant deferred maintenance
        'Very Poor': 0.85   # Near end of life, major issues
    }

    condition_depreciation_rate = condition_factors.get(condition, 0.15)
    condition_depreciation = replacement_cost_new * condition_depreciation_rate

    # Use age/life as primary method, condition as reasonableness check
    # If significant variance, flag for review
    variance = abs(age_life_depreciation - condition_depreciation)
    variance_significant = variance > (replacement_cost_new * 0.10)  # >10% variance

    # Calculate remaining life
    remaining_life = max(economic_life - effective_age, 0)
    percent_remaining = (remaining_life / economic_life) * 100 if economic_life > 0 else 0

    return {
        'method': 'Age/Life (Primary) with Condition Validation',
        'effective_age': effective_age,
        'actual_age': depreciation_data.get('age_years', effective_age),
        'economic_life': economic_life,
        'remaining_life': remaining_life,
        'percent_remaining': percent_remaining,
        'depreciation_rate': depreciation_rate,
        'physical_depreciation': age_life_depreciation,
        'condition_rating': condition,
        'condition_based_depreciation': condition_depreciation,
        'variance_significant': variance_significant,
        'variance_amount': variance,
        'recommendation': (
            'Age/life method and condition assessment are consistent' if not variance_significant
            else 'REVIEW: Significant variance between age/life and condition methods - verify effective age'
        )
    }


def calculate_functional_obsolescence(
    functional_obsolescence_value: float,
    replacement_cost_new: float,
    specifications: Optional[Dict] = None
) -> Dict:
    """
    Calculate functional obsolescence.

    Functional obsolescence reflects:
    - Design inefficiency
    - Excess capacity
    - Technological obsolescence
    - Operational inefficiency

    Args:
        functional_obsolescence_value: Dollar amount or percentage of functional obsolescence
        replacement_cost_new: RCN value
        specifications: Optional asset specifications for context

    Returns:
        Dictionary with functional obsolescence analysis

    Example:
        >>> func_obs = calculate_functional_obsolescence(15000, 289100)
        >>> print(f"Functional obsolescence: ${func_obs['functional_obsolescence']:,.2f}")
        Functional obsolescence: $15,000.00
    """
    # If value is between 0-1, treat as percentage
    if 0 < functional_obsolescence_value <= 1:
        functional_obsolescence = replacement_cost_new * functional_obsolescence_value
        obsolescence_rate = functional_obsolescence_value
    else:
        # Treat as dollar amount
        functional_obsolescence = functional_obsolescence_value
        obsolescence_rate = functional_obsolescence / replacement_cost_new if replacement_cost_new > 0 else 0

    # Categorize severity
    if obsolescence_rate == 0:
        severity = 'None'
        description = 'No functional obsolescence identified'
    elif obsolescence_rate < 0.05:
        severity = 'Minor'
        description = 'Minor design inefficiencies or excess capacity'
    elif obsolescence_rate < 0.15:
        severity = 'Moderate'
        description = 'Moderate functional obsolescence - design or capacity issues'
    elif obsolescence_rate < 0.30:
        severity = 'Substantial'
        description = 'Substantial functional obsolescence - significant design limitations'
    else:
        severity = 'Severe'
        description = 'Severe functional obsolescence - major technological or design deficiencies'

    return {
        'functional_obsolescence': functional_obsolescence,
        'obsolescence_rate': obsolescence_rate,
        'severity': severity,
        'description': description,
        'examples': _get_functional_obsolescence_examples(severity)
    }


def calculate_external_obsolescence(
    external_obsolescence_value: float,
    replacement_cost_new: float,
    market_data: Optional[Dict] = None
) -> Dict:
    """
    Calculate external obsolescence.

    External obsolescence reflects:
    - Market conditions
    - Regulatory changes
    - Economic conditions
    - Location factors
    - Environmental factors

    Args:
        external_obsolescence_value: Dollar amount or percentage of external obsolescence
        replacement_cost_new: RCN value
        market_data: Optional market context

    Returns:
        Dictionary with external obsolescence analysis

    Example:
        >>> ext_obs = calculate_external_obsolescence(25000, 289100)
        >>> print(f"External obsolescence: ${ext_obs['external_obsolescence']:,.2f}")
        External obsolescence: $25,000.00
    """
    # If value is between 0-1, treat as percentage
    if 0 < external_obsolescence_value <= 1:
        external_obsolescence = replacement_cost_new * external_obsolescence_value
        obsolescence_rate = external_obsolescence_value
    else:
        # Treat as dollar amount
        external_obsolescence = external_obsolescence_value
        obsolescence_rate = external_obsolescence / replacement_cost_new if replacement_cost_new > 0 else 0

    # Categorize severity
    if obsolescence_rate == 0:
        severity = 'None'
        description = 'No external obsolescence identified'
    elif obsolescence_rate < 0.05:
        severity = 'Minor'
        description = 'Minor market or regulatory impacts'
    elif obsolescence_rate < 0.15:
        severity = 'Moderate'
        description = 'Moderate external obsolescence - market or regulatory pressures'
    elif obsolescence_rate < 0.30:
        severity = 'Substantial'
        description = 'Substantial external obsolescence - significant market changes'
    else:
        severity = 'Severe'
        description = 'Severe external obsolescence - major economic or regulatory impacts'

    return {
        'external_obsolescence': external_obsolescence,
        'obsolescence_rate': obsolescence_rate,
        'severity': severity,
        'description': description,
        'examples': _get_external_obsolescence_examples(severity)
    }


def calculate_total_depreciation(
    physical_dep: Dict,
    functional_obs: Dict,
    external_obs: Dict,
    replacement_cost_new: float
) -> Dict:
    """
    Calculate total depreciation from all sources.

    Args:
        physical_dep: Physical depreciation results
        functional_obs: Functional obsolescence results
        external_obs: External obsolescence results
        replacement_cost_new: RCN value

    Returns:
        Dictionary with total depreciation summary

    Example:
        >>> total = calculate_total_depreciation(phys, func, ext, 289100)
        >>> print(f"Depreciated value: ${total['depreciated_replacement_cost']:,.2f}")
        Depreciated value: $179,716.00
    """
    physical_amount = physical_dep.get('physical_depreciation', 0)
    functional_amount = functional_obs.get('functional_obsolescence', 0)
    external_amount = external_obs.get('external_obsolescence', 0)

    total_depreciation = physical_amount + functional_amount + external_amount
    total_depreciation_rate = total_depreciation / replacement_cost_new if replacement_cost_new > 0 else 0

    depreciated_replacement_cost = replacement_cost_new - total_depreciation

    return {
        'replacement_cost_new': replacement_cost_new,
        'physical_depreciation': physical_amount,
        'functional_obsolescence': functional_amount,
        'external_obsolescence': external_amount,
        'total_depreciation': total_depreciation,
        'total_depreciation_rate': total_depreciation_rate,
        'depreciated_replacement_cost': depreciated_replacement_cost,
        'breakdown_percentages': {
            'physical': (physical_amount / total_depreciation * 100) if total_depreciation > 0 else 0,
            'functional': (functional_amount / total_depreciation * 100) if total_depreciation > 0 else 0,
            'external': (external_amount / total_depreciation * 100) if total_depreciation > 0 else 0
        }
    }


def _get_functional_obsolescence_examples(severity: str) -> list:
    """Get example causes of functional obsolescence by severity."""
    examples = {
        'None': ['No functional issues identified'],
        'Minor': [
            'Slight excess capacity',
            'Minor design inefficiencies',
            'Non-critical outdated components'
        ],
        'Moderate': [
            'Moderate excess capacity',
            'Inefficient layout or design',
            'Outdated but functional technology'
        ],
        'Substantial': [
            'Significant excess capacity',
            'Major design limitations',
            'Obsolete technology requiring replacement soon'
        ],
        'Severe': [
            'Extreme overcapacity',
            'Fundamentally flawed design',
            'Technology no longer supported',
            'Requires complete modernization'
        ]
    }
    return examples.get(severity, [])


def _get_external_obsolescence_examples(severity: str) -> list:
    """Get example causes of external obsolescence by severity."""
    examples = {
        'None': ['No external factors identified'],
        'Minor': [
            'Minor regulatory changes',
            'Temporary market softness',
            'Minor location disadvantages'
        ],
        'Moderate': [
            'New regulations requiring future modifications',
            'Declining demand in service area',
            'Environmental compliance costs'
        ],
        'Substantial': [
            'Major regulatory restrictions',
            'Significant market decline',
            'Competing infrastructure built',
            'Environmental remediation required'
        ],
        'Severe': [
            'Regulatory prohibition imminent',
            'Market collapse',
            'Stranded asset due to policy changes',
            'Severe environmental contamination'
        ]
    }
    return examples.get(severity, [])
