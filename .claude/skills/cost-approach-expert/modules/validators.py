"""
Input Validation Module

Validates infrastructure cost calculator inputs against schema and business rules.
"""

from typing import Dict, List, Optional, Any, Tuple


def validate_input(data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate complete input data structure.

    Args:
        data: Complete input dictionary

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> valid, errors = validate_input(input_data)
        >>> if not valid:
        ...     for error in errors:
        ...         print(f"Error: {error}")
    """
    errors = []

    # Required top-level fields
    required_fields = ['asset_type', 'construction_costs', 'depreciation']
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    # Validate construction costs
    if 'construction_costs' in data:
        construction_valid, construction_errors = validate_construction_costs(
            data['construction_costs']
        )
        errors.extend(construction_errors)

    # Validate depreciation data
    if 'depreciation' in data:
        depreciation_valid, depreciation_errors = validate_depreciation_data(
            data['depreciation']
        )
        errors.extend(depreciation_errors)

    # Validate asset type
    if 'asset_type' in data:
        asset_type = data['asset_type']
        valid_types = [
            'Transmission tower',
            'Transmission line',
            'Substation',
            'Pipeline',
            'Pumping station',
            'Storage facility',
            'Access road',
            'Utility corridor',
            'Other infrastructure'
        ]
        if asset_type not in valid_types:
            # Warning only, not error - allow custom types
            pass

    return len(errors) == 0, errors


def validate_construction_costs(costs: Dict) -> Tuple[bool, List[str]]:
    """
    Validate construction cost inputs.

    Args:
        costs: Construction costs dictionary

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> costs = {'materials': 150000, 'labor': 80000}
        >>> valid, errors = validate_construction_costs(costs)
    """
    errors = []

    # Required fields
    required = ['materials', 'labor', 'overhead_percentage', 'profit_percentage']
    for field in required:
        if field not in costs:
            errors.append(f"Missing construction cost field: {field}")

    # Validate numeric values
    numeric_fields = ['materials', 'labor']
    for field in numeric_fields:
        if field in costs:
            value = costs[field]
            if not isinstance(value, (int, float)):
                errors.append(f"{field} must be numeric, got {type(value).__name__}")
            elif value < 0:
                errors.append(f"{field} cannot be negative: {value}")

    # Validate percentages (0-1 range)
    percentage_fields = ['overhead_percentage', 'profit_percentage']
    for field in percentage_fields:
        if field in costs:
            value = costs[field]
            if not isinstance(value, (int, float)):
                errors.append(f"{field} must be numeric, got {type(value).__name__}")
            elif value < 0 or value > 1:
                errors.append(f"{field} must be between 0 and 1: {value}")

    # Business rules
    if 'overhead_percentage' in costs:
        overhead = costs['overhead_percentage']
        if overhead < 0.05 or overhead > 0.25:
            # Warning: typical range is 12-18%
            pass  # Allow but could add warning system

    if 'profit_percentage' in costs:
        profit = costs['profit_percentage']
        if profit < 0.05 or profit > 0.25:
            # Warning: typical range is 10-15%
            pass  # Allow but could add warning system

    return len(errors) == 0, errors


def validate_depreciation_data(depreciation: Dict) -> Tuple[bool, List[str]]:
    """
    Validate depreciation input data.

    Args:
        depreciation: Depreciation data dictionary

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Required fields
    required = ['age_years', 'effective_age_years', 'economic_life_years']
    for field in required:
        if field not in depreciation:
            errors.append(f"Missing depreciation field: {field}")

    # Validate numeric values
    numeric_fields = ['age_years', 'effective_age_years', 'economic_life_years',
                     'functional_obsolescence', 'external_obsolescence']
    for field in numeric_fields:
        if field in depreciation:
            value = depreciation[field]
            if not isinstance(value, (int, float)):
                errors.append(f"{field} must be numeric, got {type(value).__name__}")
            elif value < 0:
                errors.append(f"{field} cannot be negative: {value}")

    # Business rule: effective age <= economic life
    if all(k in depreciation for k in ['effective_age_years', 'economic_life_years']):
        effective_age = depreciation['effective_age_years']
        economic_life = depreciation['economic_life_years']

        if effective_age > economic_life:
            errors.append(
                f"Effective age ({effective_age}) cannot exceed economic life ({economic_life})"
            )

    # Business rule: effective age usually <= actual age
    if all(k in depreciation for k in ['age_years', 'effective_age_years']):
        age = depreciation['age_years']
        effective_age = depreciation['effective_age_years']

        if effective_age > age * 1.5:  # Allow some variance for poor maintenance
            # Warning only - deferred maintenance can increase effective age
            pass

    # Validate physical condition
    if 'physical_condition' in depreciation:
        valid_conditions = ['Excellent', 'Good', 'Fair', 'Poor', 'Very Poor']
        if depreciation['physical_condition'] not in valid_conditions:
            errors.append(
                f"Invalid physical_condition: {depreciation['physical_condition']}. "
                f"Must be one of: {', '.join(valid_conditions)}"
            )

    return len(errors) == 0, errors


def validate_market_data(market_data: Optional[Dict]) -> Tuple[bool, List[str]]:
    """
    Validate market data for reconciliation.

    Args:
        market_data: Optional market data dictionary

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    if market_data is None:
        return True, []  # Market data is optional

    # Validate comparable sales
    if 'comparable_sales' in market_data:
        comps = market_data['comparable_sales']

        if not isinstance(comps, list):
            errors.append("comparable_sales must be a list")
        else:
            for idx, comp in enumerate(comps):
                if not isinstance(comp, dict):
                    errors.append(f"Comparable {idx} must be a dictionary")
                    continue

                # Validate required fields for each comp
                required_comp_fields = ['sale_price', 'asset_type']
                for field in required_comp_fields:
                    if field not in comp:
                        errors.append(f"Comparable {idx} missing field: {field}")

                # Validate sale price
                if 'sale_price' in comp:
                    price = comp['sale_price']
                    if not isinstance(price, (int, float)):
                        errors.append(f"Comparable {idx} sale_price must be numeric")
                    elif price <= 0:
                        errors.append(f"Comparable {idx} sale_price must be positive")

    return len(errors) == 0, errors


def validate_specifications(specs: Optional[Dict]) -> Tuple[bool, List[str]]:
    """
    Validate asset specifications.

    Args:
        specs: Asset specifications dictionary

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    if specs is None:
        return True, []  # Specifications are optional

    # Validate that all values are of expected types
    for key, value in specs.items():
        if not isinstance(value, (str, int, float, bool)):
            errors.append(
                f"Specification '{key}' has invalid type: {type(value).__name__}. "
                "Expected string, number, or boolean."
            )

    return len(errors) == 0, errors
