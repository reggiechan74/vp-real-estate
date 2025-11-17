"""
Input Validation Module
Validates encumbrance discount calculator inputs and ensures data integrity
"""

from typing import Dict, List, Optional, TypedDict
from datetime import datetime


class PropertyData(TypedDict):
    """Property data structure"""
    pin: str
    address: str
    total_area_acres: float
    unencumbered_value: float
    zoning: Optional[str]
    highest_best_use: Optional[str]


class EncumbranceData(TypedDict):
    """Individual encumbrance data structure"""
    type: str
    area_acres: float
    impact_percentage: Optional[float]
    voltage: Optional[str]
    width_feet: Optional[float]
    length_feet: Optional[float]
    description: Optional[str]


class AgriculturalImpacts(TypedDict):
    """Agricultural impact data structure"""
    annual_crop_loss: float
    cap_rate: float
    operational_inefficiency_pct: Optional[float]


class PairedSale(TypedDict):
    """Paired sales comparable data"""
    address: str
    sale_price: float
    sale_date: str
    area_acres: float
    has_encumbrance: bool
    encumbrance_type: Optional[str]
    encumbrance_area_acres: Optional[float]


class EncumbranceInput(TypedDict):
    """Complete input structure"""
    property: PropertyData
    encumbrances: List[EncumbranceData]
    agricultural_impacts: Optional[AgriculturalImpacts]
    paired_sales: Optional[List[PairedSale]]
    marketability_factors: Optional[Dict]


# Encumbrance type validation ranges
ENCUMBRANCE_RANGES = {
    'transmission_easement': {
        'min': 0.05,
        'max': 0.15,
        'typical': 0.10,
        'description': 'Transmission line easement (5-15%)'
    },
    'pipeline_easement': {
        'min': 0.10,
        'max': 0.20,
        'typical': 0.15,
        'description': 'Pipeline easement (10-20%)'
    },
    'drainage_easement': {
        'min': 0.02,
        'max': 0.08,
        'typical': 0.05,
        'description': 'Drainage easement (2-8%)'
    },
    'access_easement': {
        'min': 0.02,
        'max': 0.08,
        'typical': 0.05,
        'description': 'Access easement (2-8%)'
    },
    'conservation_easement': {
        'min': 0.20,
        'max': 0.50,
        'typical': 0.35,
        'description': 'Conservation easement (20-50%)'
    },
    'telecom_easement': {
        'min': 0.03,
        'max': 0.10,
        'typical': 0.06,
        'description': 'Telecommunications easement (3-10%)'
    }
}


def validate_input(data: Dict) -> tuple[bool, List[str], EncumbranceInput]:
    """
    Validate encumbrance discount calculator input data.

    Args:
        data: Raw input dictionary

    Returns:
        Tuple of (is_valid, error_messages, validated_data)

    Raises:
        ValueError: If critical validation fails
    """
    errors = []
    warnings = []

    # Validate property data
    if 'property' not in data:
        errors.append("Missing required 'property' section")
        return False, errors, None

    property_data = data['property']

    # Required property fields
    required_property = ['pin', 'address', 'total_area_acres', 'unencumbered_value']
    for field in required_property:
        if field not in property_data:
            errors.append(f"Missing required property field: {field}")

    # Validate numeric values
    if 'total_area_acres' in property_data:
        if property_data['total_area_acres'] <= 0:
            errors.append("total_area_acres must be positive")

    if 'unencumbered_value' in property_data:
        if property_data['unencumbered_value'] <= 0:
            errors.append("unencumbered_value must be positive")

    # Validate encumbrances
    if 'encumbrances' not in data or not data['encumbrances']:
        errors.append("At least one encumbrance is required")
        return False, errors, None

    total_encumbered_area = 0
    for idx, enc in enumerate(data['encumbrances']):
        # Required fields
        if 'type' not in enc:
            errors.append(f"Encumbrance {idx+1}: Missing 'type' field")
            continue

        if 'area_acres' not in enc:
            errors.append(f"Encumbrance {idx+1}: Missing 'area_acres' field")
            continue

        # Validate encumbrance type
        enc_type = enc['type']
        if enc_type not in ENCUMBRANCE_RANGES:
            warnings.append(
                f"Encumbrance {idx+1}: Unknown type '{enc_type}'. "
                f"Known types: {', '.join(ENCUMBRANCE_RANGES.keys())}"
            )

        # Validate area
        enc_area = enc['area_acres']
        if enc_area <= 0:
            errors.append(f"Encumbrance {idx+1}: area_acres must be positive")

        total_encumbered_area += enc_area

        # Validate impact percentage if provided
        if 'impact_percentage' in enc:
            impact = enc['impact_percentage']
            if not 0 <= impact <= 100:
                errors.append(
                    f"Encumbrance {idx+1}: impact_percentage must be between 0 and 100"
                )

            # Check if within typical range for type
            if enc_type in ENCUMBRANCE_RANGES:
                ranges = ENCUMBRANCE_RANGES[enc_type]
                impact_decimal = impact / 100
                if impact_decimal < ranges['min'] or impact_decimal > ranges['max']:
                    warnings.append(
                        f"Encumbrance {idx+1}: {impact}% is outside typical range "
                        f"for {enc_type} ({ranges['min']*100}-{ranges['max']*100}%)"
                    )

    # Check total encumbered area vs property area
    if 'total_area_acres' in property_data:
        if total_encumbered_area > property_data['total_area_acres']:
            errors.append(
                f"Total encumbered area ({total_encumbered_area:.2f} acres) "
                f"exceeds property area ({property_data['total_area_acres']:.2f} acres)"
            )

    # Validate agricultural impacts (optional)
    if 'agricultural_impacts' in data and data['agricultural_impacts']:
        ag_impacts = data['agricultural_impacts']

        if 'annual_crop_loss' in ag_impacts:
            if ag_impacts['annual_crop_loss'] < 0:
                errors.append("annual_crop_loss cannot be negative")

        if 'cap_rate' in ag_impacts:
            cap_rate = ag_impacts['cap_rate']
            if not 0 < cap_rate <= 1:
                errors.append("cap_rate must be between 0 and 1 (decimal form)")
            if cap_rate < 0.03 or cap_rate > 0.15:
                warnings.append(
                    f"cap_rate {cap_rate*100}% is outside typical range (3-15%)"
                )

    # Validate paired sales (optional)
    if 'paired_sales' in data and data['paired_sales']:
        for idx, sale in enumerate(data['paired_sales']):
            required_sale_fields = ['address', 'sale_price', 'sale_date',
                                   'area_acres', 'has_encumbrance']
            for field in required_sale_fields:
                if field not in sale:
                    errors.append(f"Paired sale {idx+1}: Missing '{field}' field")

            if 'sale_price' in sale and sale['sale_price'] <= 0:
                errors.append(f"Paired sale {idx+1}: sale_price must be positive")

            if 'area_acres' in sale and sale['area_acres'] <= 0:
                errors.append(f"Paired sale {idx+1}: area_acres must be positive")

            # Validate date format
            if 'sale_date' in sale:
                try:
                    datetime.strptime(sale['sale_date'], '%Y-%m-%d')
                except ValueError:
                    errors.append(
                        f"Paired sale {idx+1}: sale_date must be YYYY-MM-DD format"
                    )

    # Return validation results
    is_valid = len(errors) == 0

    # Print warnings if any
    if warnings and is_valid:
        print("\n⚠️  VALIDATION WARNINGS:")
        for warning in warnings:
            print(f"   - {warning}")
        print()

    return is_valid, errors, data if is_valid else None


def get_default_impact_percentage(encumbrance_type: str) -> float:
    """
    Get default impact percentage for encumbrance type.

    Args:
        encumbrance_type: Type of encumbrance

    Returns:
        Typical impact percentage (as percentage, not decimal)
    """
    if encumbrance_type in ENCUMBRANCE_RANGES:
        return ENCUMBRANCE_RANGES[encumbrance_type]['typical'] * 100
    return 10.0  # Conservative default


def get_encumbrance_range(encumbrance_type: str) -> Dict:
    """
    Get valid range for encumbrance type.

    Args:
        encumbrance_type: Type of encumbrance

    Returns:
        Dictionary with min, max, typical, description
    """
    return ENCUMBRANCE_RANGES.get(
        encumbrance_type,
        {
            'min': 0.05,
            'max': 0.20,
            'typical': 0.10,
            'description': 'Unknown encumbrance type (5-20% default)'
        }
    )
