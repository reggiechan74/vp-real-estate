"""
Nominatim Geocoding Module

OpenStreetMap Nominatim geocoding client with rate limiting and caching.
Respects Nominatim usage policy: max 1 request per second, custom User-Agent.
"""

import asyncio
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

import httpx

from .cache import GeocodingCache, CachedGeocodingResult


@dataclass
class GeocodingResult:
    """Result from geocoding operation."""

    latitude: float
    longitude: float
    display_name: str
    address_components: Dict[str, str]
    osm_id: Optional[int] = None
    osm_type: Optional[str] = None
    place_id: Optional[int] = None
    cached: bool = False
    response_time_ms: float = 0.0


class NominatimGeocoder:
    """
    OpenStreetMap Nominatim geocoding client.

    Respects usage policy:
    - Max 1 request per second
    - Custom User-Agent required
    - No bulk geocoding
    """

    BASE_URL = "https://nominatim.openstreetmap.org"
    RATE_LIMIT = 1.0  # 1 request per second (free tier)
    DEFAULT_TIMEOUT = 10.0  # seconds

    def __init__(
        self,
        user_agent: str = "LocationOverview/1.0 (lease-abstract-toolkit)",
        cache: Optional[GeocodingCache] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        """
        Initialize Nominatim geocoder.

        Args:
            user_agent: User-Agent string (required by Nominatim policy)
            cache: Optional GeocodingCache instance
            timeout: Request timeout in seconds
        """
        self.user_agent = user_agent
        self.cache = cache or GeocodingCache()
        self.timeout = timeout
        self._last_request = 0.0
        self._lock = asyncio.Lock()

    async def _rate_limit(self) -> None:
        """Enforce rate limiting (1 req/sec)."""
        async with self._lock:
            now = time.time()
            elapsed = now - self._last_request
            if elapsed < self.RATE_LIMIT:
                await asyncio.sleep(self.RATE_LIMIT - elapsed)
            self._last_request = time.time()

    async def geocode(
        self,
        address: str,
        use_cache: bool = True,
        country_codes: str = "ca",
    ) -> Optional[GeocodingResult]:
        """
        Forward geocode an address to coordinates.

        Args:
            address: Address string to geocode
            use_cache: Whether to use cached results
            country_codes: ISO 3166-1 country codes (default: Canada)

        Returns:
            GeocodingResult or None if not found
        """
        # Check cache first
        if use_cache:
            cached = self.cache.get(address, "forward")
            if cached:
                return GeocodingResult(
                    latitude=cached.latitude,
                    longitude=cached.longitude,
                    display_name=cached.display_name,
                    address_components=cached.address_components,
                    osm_id=cached.osm_id,
                    osm_type=cached.osm_type,
                    cached=True,
                    response_time_ms=0.0,
                )

        # Rate limit
        await self._rate_limit()

        start_time = time.time()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/search",
                    params={
                        "q": address,
                        "format": "json",
                        "addressdetails": 1,
                        "limit": 1,
                        "countrycodes": country_codes,
                    },
                    headers={"User-Agent": self.user_agent},
                    timeout=self.timeout,
                )
                response.raise_for_status()
                results = response.json()

            response_time = (time.time() - start_time) * 1000

            if not results:
                return None

            result = results[0]
            geocoding_result = GeocodingResult(
                latitude=float(result["lat"]),
                longitude=float(result["lon"]),
                display_name=result["display_name"],
                address_components=result.get("address", {}),
                osm_id=int(result.get("osm_id", 0)) or None,
                osm_type=result.get("osm_type"),
                place_id=int(result.get("place_id", 0)) or None,
                cached=False,
                response_time_ms=response_time,
            )

            # Cache the result
            if use_cache:
                cached_result = CachedGeocodingResult(
                    latitude=geocoding_result.latitude,
                    longitude=geocoding_result.longitude,
                    display_name=geocoding_result.display_name,
                    address_components=geocoding_result.address_components,
                    osm_id=geocoding_result.osm_id,
                    osm_type=geocoding_result.osm_type,
                    cached_at=datetime.now().isoformat(),
                    source="nominatim",
                )
                self.cache.set(address, cached_result, "forward")

            return geocoding_result

        except httpx.HTTPStatusError as e:
            raise GeocodingError(f"Nominatim HTTP error: {e.response.status_code}") from e
        except httpx.TimeoutException:
            raise GeocodingError("Nominatim request timed out")
        except Exception as e:
            raise GeocodingError(f"Geocoding failed: {str(e)}") from e

    async def reverse(
        self,
        lat: float,
        lon: float,
        use_cache: bool = True,
    ) -> Optional[GeocodingResult]:
        """
        Reverse geocode coordinates to address.

        Args:
            lat: Latitude
            lon: Longitude
            use_cache: Whether to use cached results

        Returns:
            GeocodingResult or None if not found
        """
        cache_key = f"{lat:.6f},{lon:.6f}"

        # Check cache
        if use_cache:
            cached = self.cache.get(cache_key, "reverse")
            if cached:
                return GeocodingResult(
                    latitude=cached.latitude,
                    longitude=cached.longitude,
                    display_name=cached.display_name,
                    address_components=cached.address_components,
                    osm_id=cached.osm_id,
                    osm_type=cached.osm_type,
                    cached=True,
                    response_time_ms=0.0,
                )

        # Rate limit
        await self._rate_limit()

        start_time = time.time()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/reverse",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "format": "json",
                        "addressdetails": 1,
                    },
                    headers={"User-Agent": self.user_agent},
                    timeout=self.timeout,
                )
                response.raise_for_status()
                result = response.json()

            response_time = (time.time() - start_time) * 1000

            if "error" in result:
                return None

            geocoding_result = GeocodingResult(
                latitude=float(result["lat"]),
                longitude=float(result["lon"]),
                display_name=result["display_name"],
                address_components=result.get("address", {}),
                osm_id=int(result.get("osm_id", 0)) or None,
                osm_type=result.get("osm_type"),
                place_id=int(result.get("place_id", 0)) or None,
                cached=False,
                response_time_ms=response_time,
            )

            # Cache the result
            if use_cache:
                cached_result = CachedGeocodingResult(
                    latitude=geocoding_result.latitude,
                    longitude=geocoding_result.longitude,
                    display_name=geocoding_result.display_name,
                    address_components=geocoding_result.address_components,
                    osm_id=geocoding_result.osm_id,
                    osm_type=geocoding_result.osm_type,
                    cached_at=datetime.now().isoformat(),
                    source="nominatim",
                )
                self.cache.set(cache_key, cached_result, "reverse")

            return geocoding_result

        except httpx.HTTPStatusError as e:
            raise GeocodingError(f"Nominatim HTTP error: {e.response.status_code}") from e
        except httpx.TimeoutException:
            raise GeocodingError("Nominatim request timed out")
        except Exception as e:
            raise GeocodingError(f"Reverse geocoding failed: {str(e)}") from e


class GeocodingError(Exception):
    """Exception raised for geocoding errors."""

    pass
