"""Input processing module for PIN and address handling."""

from .parser import detect_input_type, validate_pin, InputType
from .normalizer import normalize_address
from .municipality_detector import detect_municipality

__all__ = [
    "detect_input_type",
    "validate_pin",
    "InputType",
    "normalize_address",
    "detect_municipality",
]
