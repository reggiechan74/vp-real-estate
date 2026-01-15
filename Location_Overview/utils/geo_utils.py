"""
Geographic Utilities Module

Coordinate transformations and distance calculations.
"""

from math import radians, cos, sin, sqrt, atan2
from typing import Tuple, Optional

try:
    from pyproj import Transformer, CRS
except ImportError:
    Transformer = None
    CRS = None


def haversine_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """
    Calculate distance between two points using Haversine formula.

    Args:
        lat1, lon1: First point (WGS84)
        lat2, lon2: Second point (WGS84)

    Returns:
        Distance in meters
    """
    R = 6371000  # Earth radius in meters

    phi1, phi2 = radians(lat1), radians(lat2)
    delta_phi = radians(lat2 - lat1)
    delta_lambda = radians(lon2 - lon1)

    a = sin(delta_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(delta_lambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def transform_coordinates(
    x: float,
    y: float,
    from_crs: str,
    to_crs: str = "EPSG:4326",
) -> Tuple[float, float]:
    """
    Transform coordinates between coordinate systems.

    Common CRS codes:
    - EPSG:4326 - WGS84 (lat/lon)
    - EPSG:3857 - Web Mercator
    - EPSG:2019 - MTM Zone 9 (Ottawa area)
    - EPSG:2020 - MTM Zone 10 (Toronto area)

    Args:
        x: X coordinate (or longitude)
        y: Y coordinate (or latitude)
        from_crs: Source CRS (e.g., "EPSG:3857")
        to_crs: Target CRS (default: WGS84)

    Returns:
        Tuple of (x, y) in target CRS
    """
    if Transformer is None:
        # If pyproj not available, assume WGS84
        return x, y

    transformer = Transformer.from_crs(from_crs, to_crs, always_xy=True)
    return transformer.transform(x, y)


def validate_wgs84(lat: float, lon: float) -> bool:
    """
    Check if coordinates are valid WGS84.

    Args:
        lat: Latitude
        lon: Longitude

    Returns:
        True if valid
    """
    return -90 <= lat <= 90 and -180 <= lon <= 180


def is_in_ontario(lat: float, lon: float) -> bool:
    """
    Check if coordinates are within Ontario bounds.

    Args:
        lat: Latitude
        lon: Longitude

    Returns:
        True if in Ontario
    """
    # Approximate Ontario bounding box
    ONTARIO_LAT_MIN = 41.6
    ONTARIO_LAT_MAX = 56.9
    ONTARIO_LON_MIN = -95.2
    ONTARIO_LON_MAX = -74.3

    return (
        ONTARIO_LAT_MIN <= lat <= ONTARIO_LAT_MAX
        and ONTARIO_LON_MIN <= lon <= ONTARIO_LON_MAX
    )


def meters_to_degrees(meters: float, latitude: float) -> float:
    """
    Convert meters to degrees at a given latitude.

    Useful for creating bounding boxes.

    Args:
        meters: Distance in meters
        latitude: Reference latitude

    Returns:
        Approximate degrees
    """
    # At equator, 1 degree ≈ 111,320 meters
    # Adjust for latitude
    meters_per_degree = 111320 * cos(radians(latitude))
    return meters / meters_per_degree if meters_per_degree > 0 else 0


def create_bounding_box(
    lat: float,
    lon: float,
    radius_m: float,
) -> Tuple[float, float, float, float]:
    """
    Create a bounding box around a point.

    Args:
        lat: Center latitude
        lon: Center longitude
        radius_m: Radius in meters

    Returns:
        Tuple of (min_lon, min_lat, max_lon, max_lat)
    """
    delta_lat = meters_to_degrees(radius_m, lat)
    delta_lon = meters_to_degrees(radius_m, lat) / cos(radians(lat)) if cos(radians(lat)) > 0 else delta_lat

    return (
        lon - delta_lon,  # min_lon
        lat - delta_lat,  # min_lat
        lon + delta_lon,  # max_lon
        lat + delta_lat,  # max_lat
    )
