"""Geocoding module for address-to-coordinate conversion."""

from .nominatim import NominatimGeocoder, GeocodingResult
from .cache import GeocodingCache

__all__ = ["NominatimGeocoder", "GeocodingResult", "GeocodingCache"]
