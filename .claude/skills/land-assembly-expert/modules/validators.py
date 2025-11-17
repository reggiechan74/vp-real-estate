#!/usr/bin/env python3
"""
Input Validation Module for Land Assembly Calculator
Validates JSON input against schema and business rules
"""

from typing import Dict, List, Tuple
import json
from pathlib import Path


def validate_input(data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate input data against business rules.

    Args:
        data: Input data dictionary

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Validate required fields
    required_fields = ['project_name', 'parcels', 'priorities', 'resources', 'contingencies']
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    if errors:
        return False, errors

    # Validate parcels
    parcels = data.get('parcels', [])
    if not parcels:
        errors.append("At least one parcel is required")

    for i, parcel in enumerate(parcels):
        # Check required parcel fields
        required_parcel_fields = ['id', 'address', 'estimated_value', 'criticality']
        for field in required_parcel_fields:
            if field not in parcel:
                errors.append(f"Parcel {i}: Missing required field '{field}'")

        # Validate parcel ID format
        if 'id' in parcel and not parcel['id'].startswith('P'):
            errors.append(f"Parcel {i}: ID must start with 'P' (e.g., P001)")

        # Validate estimated value
        if 'estimated_value' in parcel and parcel['estimated_value'] < 0:
            errors.append(f"Parcel {parcel.get('id', i)}: estimated_value must be >= 0")

        # Validate criticality
        valid_criticality = ['critical', 'high', 'medium', 'low']
        if 'criticality' in parcel and parcel['criticality'] not in valid_criticality:
            errors.append(
                f"Parcel {parcel.get('id', i)}: criticality must be one of {valid_criticality}"
            )

        # Validate complexity if present
        if 'complexity' in parcel:
            valid_complexity = ['low', 'medium', 'high']
            if parcel['complexity'] not in valid_complexity:
                errors.append(
                    f"Parcel {parcel.get('id', i)}: complexity must be one of {valid_complexity}"
                )

        # Validate holdout_risk if present
        if 'holdout_risk' in parcel:
            risk = parcel['holdout_risk']
            if not (0 <= risk <= 1):
                errors.append(
                    f"Parcel {parcel.get('id', i)}: holdout_risk must be between 0.0 and 1.0"
                )

    # Validate priorities sum to 1.0
    priorities = data.get('priorities', {})
    if priorities:
        priority_sum = (
            priorities.get('criticality', 0) +
            priorities.get('holdout_risk', 0) +
            priorities.get('complexity', 0)
        )
        if not (0.99 <= priority_sum <= 1.01):  # Allow small floating point error
            errors.append(
                f"Priorities must sum to 1.0 (currently {priority_sum:.3f})"
            )

    # Validate resources
    resources = data.get('resources', {})
    if resources:
        if resources.get('appraisers', 0) < 1:
            errors.append("At least 1 appraiser is required")
        if resources.get('negotiators', 0) < 1:
            errors.append("At least 1 negotiator is required")

    # Validate contingencies
    contingencies = data.get('contingencies', {})
    for key in ['valuation_uncertainty', 'negotiation_premium', 'litigation_reserve', 'inflation']:
        if key in contingencies:
            value = contingencies[key]
            if not (0 <= value <= 1):
                errors.append(f"Contingency '{key}' must be between 0.0 and 1.0")

    return len(errors) == 0, errors


def validate_json_schema(data: Dict, schema_path: str = None) -> Tuple[bool, List[str]]:
    """
    Validate input against JSON schema.

    Args:
        data: Input data dictionary
        schema_path: Path to JSON schema file (optional)

    Returns:
        Tuple of (is_valid, error_messages)
    """
    try:
        import jsonschema
        from jsonschema import validate

        # Load schema
        if schema_path is None:
            schema_path = Path(__file__).parent.parent / 'land_assembly_input_schema.json'

        with open(schema_path, 'r') as f:
            schema = json.load(f)

        # Validate
        validate(instance=data, schema=schema)
        return True, []

    except ImportError:
        # jsonschema not available, skip schema validation
        return True, ["JSON schema validation skipped (jsonschema module not installed)"]

    except jsonschema.exceptions.ValidationError as e:
        return False, [f"Schema validation error: {e.message}"]

    except Exception as e:
        return False, [f"Schema validation error: {str(e)}"]


def load_and_validate_input(json_path: str) -> Tuple[Dict, List[str]]:
    """
    Load and validate input JSON file.

    Args:
        json_path: Path to input JSON file

    Returns:
        Tuple of (data, warnings)

    Raises:
        ValueError: If validation fails
    """
    # Load JSON
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        raise ValueError(f"Input file not found: {json_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")

    warnings = []

    # Validate against schema
    schema_valid, schema_errors = validate_json_schema(data)
    if not schema_valid:
        raise ValueError(f"Schema validation failed:\n" + "\n".join(schema_errors))

    # Validate business rules
    rules_valid, rule_errors = validate_input(data)
    if not rules_valid:
        raise ValueError(f"Validation failed:\n" + "\n".join(rule_errors))

    # Add defaults for optional fields
    data = add_defaults(data)

    # Generate warnings
    parcels = data.get('parcels', [])
    if len(parcels) < 10:
        warnings.append(f"Only {len(parcels)} parcels - consider if this is a land assembly (10+ parcels typical)")

    critical_count = sum(1 for p in parcels if p.get('criticality') == 'critical')
    if critical_count == 0:
        warnings.append("No critical parcels defined - phasing may not be optimal")

    return data, warnings


def add_defaults(data: Dict) -> Dict:
    """
    Add default values for optional fields.

    Args:
        data: Input data dictionary

    Returns:
        Updated data with defaults
    """
    # Add defaults for parcels
    for parcel in data.get('parcels', []):
        if 'complexity' not in parcel:
            parcel['complexity'] = 'medium'
        if 'holdout_risk' not in parcel:
            parcel['holdout_risk'] = 0.3
        if 'area_sqm' not in parcel:
            parcel['area_sqm'] = 0

    # Add defaults for resources
    resources = data.get('resources', {})
    if 'legal_staff' not in resources:
        resources['legal_staff'] = 2
    if 'appraisal_days_per_parcel' not in resources:
        resources['appraisal_days_per_parcel'] = 10
    if 'negotiation_days_per_parcel' not in resources:
        resources['negotiation_days_per_parcel'] = 30
    if 'legal_days_per_parcel' not in resources:
        resources['legal_days_per_parcel'] = 5

    if 'daily_rates' not in resources:
        resources['daily_rates'] = {
            'appraiser': 1500,
            'negotiator': 1200,
            'legal': 2000
        }

    # Add defaults for contingencies
    contingencies = data.get('contingencies', {})
    defaults = {
        'valuation_uncertainty': 0.10,
        'negotiation_premium': 0.05,
        'litigation_reserve': 0.15,
        'inflation': 0.03,
        'appraisal_cost_per_parcel': 5000,
        'legal_cost_per_parcel': 3000,
        'environmental_cost_per_parcel': 2000
    }
    for key, value in defaults.items():
        if key not in contingencies:
            contingencies[key] = value

    # Add defaults for delay analysis
    if 'delay_analysis' not in data:
        data['delay_analysis'] = {}

    delay_defaults = {
        'interest_rate': 0.05,
        'construction_cost_per_day': 50000,
        'revenue_loss_per_day': 0,
        'project_start_delay_days': 90
    }
    for key, value in delay_defaults.items():
        if key not in data['delay_analysis']:
            data['delay_analysis'][key] = value

    return data
