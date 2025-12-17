"""
Municipality Detector Module

Detects municipality from coordinates using bounding box matching.
Returns appropriate data provider for the detected municipality.
"""

from typing import Tuple, Optional, Dict
from dataclasses import dataclass


@dataclass
class MunicipalityConfig:
    """Configuration for a municipality including bounding box and data provider."""

    name: str
    bbox: Tuple[float, float, float, float]  # (min_lon, min_lat, max_lon, max_lat)
    data_provider: str
    region: str  # GTA, Eastern Ontario, etc.


# Ontario municipality bounding boxes (approximate)
# Format: (min_lon, min_lat, max_lon, max_lat)
MUNICIPALITY_CONFIGS: Dict[str, MunicipalityConfig] = {
    "Toronto": MunicipalityConfig(
        name="Toronto",
        bbox=(-79.6393, 43.5810, -79.1153, 43.8554),
        data_provider="toronto_opendata",
        region="GTA",
    ),
    "Ottawa": MunicipalityConfig(
        name="Ottawa",
        bbox=(-76.3555, 44.9620, -75.2466, 45.5375),
        data_provider="ottawa_arcgis",
        region="Eastern Ontario",
    ),
    "Mississauga": MunicipalityConfig(
        name="Mississauga",
        bbox=(-79.7756, 43.4675, -79.5079, 43.6532),
        data_provider="peel_opendata",
        region="GTA",
    ),
    "Brampton": MunicipalityConfig(
        name="Brampton",
        bbox=(-79.8830, 43.6167, -79.6590, 43.7838),
        data_provider="peel_opendata",
        region="GTA",
    ),
    "Hamilton": MunicipalityConfig(
        name="Hamilton",
        bbox=(-80.2042, 43.1761, -79.6418, 43.4676),
        data_provider="hamilton_opendata",
        region="Golden Horseshoe",
    ),
    "Markham": MunicipalityConfig(
        name="Markham",
        bbox=(-79.4617, 43.7926, -79.1832, 44.0047),
        data_provider="york_opendata",
        region="GTA",
    ),
    "Vaughan": MunicipalityConfig(
        name="Vaughan",
        bbox=(-79.6810, 43.7500, -79.4000, 43.9500),
        data_provider="york_opendata",
        region="GTA",
    ),
    "Richmond Hill": MunicipalityConfig(
        name="Richmond Hill",
        bbox=(-79.5200, 43.8300, -79.3600, 43.9700),
        data_provider="york_opendata",
        region="GTA",
    ),
    "Oakville": MunicipalityConfig(
        name="Oakville",
        bbox=(-79.7730, 43.3900, -79.5600, 43.5200),
        data_provider="halton_opendata",
        region="GTA",
    ),
    "Burlington": MunicipalityConfig(
        name="Burlington",
        bbox=(-79.9500, 43.2800, -79.7300, 43.4400),
        data_provider="halton_opendata",
        region="GTA",
    ),
    "Oshawa": MunicipalityConfig(
        name="Oshawa",
        bbox=(-78.9500, 43.8200, -78.7700, 43.9500),
        data_provider="durham_opendata",
        region="GTA",
    ),
    "Whitby": MunicipalityConfig(
        name="Whitby",
        bbox=(-78.9800, 43.8000, -78.8500, 43.9800),
        data_provider="durham_opendata",
        region="GTA",
    ),
    "Ajax": MunicipalityConfig(
        name="Ajax",
        bbox=(-79.0800, 43.8100, -78.9600, 43.9000),
        data_provider="durham_opendata",
        region="GTA",
    ),
    "Pickering": MunicipalityConfig(
        name="Pickering",
        bbox=(-79.1800, 43.7800, -79.0200, 43.9500),
        data_provider="durham_opendata",
        region="GTA",
    ),
    "Kitchener": MunicipalityConfig(
        name="Kitchener",
        bbox=(-80.5800, 43.3700, -80.3800, 43.4900),
        data_provider="waterloo_opendata",
        region="Waterloo Region",
    ),
    "Waterloo": MunicipalityConfig(
        name="Waterloo",
        bbox=(-80.6200, 43.4300, -80.4800, 43.5200),
        data_provider="waterloo_opendata",
        region="Waterloo Region",
    ),
    "Cambridge": MunicipalityConfig(
        name="Cambridge",
        bbox=(-80.4200, 43.3000, -80.2600, 43.4500),
        data_provider="waterloo_opendata",
        region="Waterloo Region",
    ),
    "London": MunicipalityConfig(
        name="London",
        bbox=(-81.4000, 42.8800, -81.1000, 43.0800),
        data_provider="london_opendata",
        region="Southwestern Ontario",
    ),
    "Guelph": MunicipalityConfig(
        name="Guelph",
        bbox=(-80.3200, 43.5000, -80.1500, 43.6000),
        data_provider="guelph_opendata",
        region="Southwestern Ontario",
    ),
    "Barrie": MunicipalityConfig(
        name="Barrie",
        bbox=(-79.7500, 44.3200, -79.6000, 44.4300),
        data_provider="barrie_opendata",
        region="Simcoe County",
    ),
    "Kingston": MunicipalityConfig(
        name="Kingston",
        bbox=(-76.6500, 44.1800, -76.4000, 44.3200),
        data_provider="kingston_opendata",
        region="Eastern Ontario",
    ),
    "Windsor": MunicipalityConfig(
        name="Windsor",
        bbox=(-83.1200, 42.2500, -82.8800, 42.3500),
        data_provider="windsor_opendata",
        region="Southwestern Ontario",
    ),
    "St. Catharines": MunicipalityConfig(
        name="St. Catharines",
        bbox=(-79.3200, 43.1200, -79.1500, 43.2300),
        data_provider="niagara_opendata",
        region="Niagara Region",
    ),
    "Niagara Falls": MunicipalityConfig(
        name="Niagara Falls",
        bbox=(-79.1500, 43.0200, -79.0000, 43.1500),
        data_provider="niagara_opendata",
        region="Niagara Region",
    ),
}


def detect_municipality(lat: float, lon: float) -> Tuple[str, str]:
    """
    Detect municipality from coordinates using bounding box matching.

    Args:
        lat: Latitude (WGS84)
        lon: Longitude (WGS84)

    Returns:
        Tuple of (municipality_name, data_provider_id)
    """
    for municipality, config in MUNICIPALITY_CONFIGS.items():
        bbox = config.bbox
        # Check if point is within bounding box
        if bbox[0] <= lon <= bbox[2] and bbox[1] <= lat <= bbox[3]:
            return config.name, config.data_provider

    # Default to generic Ontario provider if no match
    return "Ontario", "generic_municipal"


def get_municipality_config(municipality_name: str) -> Optional[MunicipalityConfig]:
    """
    Get configuration for a specific municipality.

    Args:
        municipality_name: Name of the municipality

    Returns:
        MunicipalityConfig or None if not found
    """
    return MUNICIPALITY_CONFIGS.get(municipality_name)


def get_region(lat: float, lon: float) -> str:
    """
    Get the region name for coordinates.

    Args:
        lat: Latitude
        lon: Longitude

    Returns:
        Region name (e.g., "GTA", "Eastern Ontario")
    """
    municipality, _ = detect_municipality(lat, lon)
    config = get_municipality_config(municipality)
    return config.region if config else "Ontario"


def is_gta(lat: float, lon: float) -> bool:
    """
    Check if coordinates are within the Greater Toronto Area.

    Args:
        lat: Latitude
        lon: Longitude

    Returns:
        True if in GTA
    """
    municipality, _ = detect_municipality(lat, lon)
    config = get_municipality_config(municipality)
    return config.region == "GTA" if config else False


def get_supported_municipalities() -> list:
    """
    Get list of all supported municipalities.

    Returns:
        List of municipality names
    """
    return list(MUNICIPALITY_CONFIGS.keys())


def get_municipalities_by_region(region: str) -> list:
    """
    Get municipalities in a specific region.

    Args:
        region: Region name (e.g., "GTA", "Eastern Ontario")

    Returns:
        List of municipality names in that region
    """
    return [
        name for name, config in MUNICIPALITY_CONFIGS.items() if config.region == region
    ]
