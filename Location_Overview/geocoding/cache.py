"""
Geocoding Cache Module

Disk-based caching for geocoding results to reduce API calls and improve performance.
Uses diskcache for persistent storage.
"""

import hashlib
import json
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path

try:
    from diskcache import Cache
except ImportError:
    Cache = None


@dataclass
class CachedGeocodingResult:
    """Cached geocoding result with metadata."""

    latitude: float
    longitude: float
    display_name: str
    address_components: Dict[str, str]
    osm_id: Optional[int]
    osm_type: Optional[str]
    cached_at: str
    source: str = "nominatim"


class GeocodingCache:
    """
    Disk-based cache for geocoding results.

    Uses diskcache for persistent storage with configurable TTL.
    Falls back to in-memory dict if diskcache not available.
    """

    DEFAULT_TTL = 7 * 24 * 60 * 60  # 7 days in seconds
    CACHE_DIR = ".cache/geocoding"

    def __init__(
        self,
        cache_dir: Optional[str] = None,
        ttl: int = DEFAULT_TTL,
        size_limit: int = 100 * 1024 * 1024,  # 100MB
    ):
        """
        Initialize geocoding cache.

        Args:
            cache_dir: Directory for cache storage
            ttl: Time-to-live in seconds (default: 7 days)
            size_limit: Maximum cache size in bytes
        """
        self.ttl = ttl
        self.size_limit = size_limit

        if cache_dir is None:
            cache_dir = self.CACHE_DIR

        self._cache_dir = Path(cache_dir)

        if Cache is not None:
            self._cache_dir.mkdir(parents=True, exist_ok=True)
            self._cache = Cache(str(self._cache_dir), size_limit=size_limit)
        else:
            # Fallback to in-memory dict
            self._cache = {}
            self._cache_times = {}

    def _make_key(self, query: str, query_type: str = "forward") -> str:
        """
        Generate cache key from query string.

        Args:
            query: The geocoding query
            query_type: "forward" or "reverse"

        Returns:
            Hash-based cache key
        """
        normalized = query.lower().strip()
        key_str = f"{query_type}:{normalized}"
        return hashlib.sha256(key_str.encode()).hexdigest()[:32]

    def get(self, query: str, query_type: str = "forward") -> Optional[CachedGeocodingResult]:
        """
        Get cached geocoding result.

        Args:
            query: The geocoding query
            query_type: "forward" or "reverse"

        Returns:
            CachedGeocodingResult or None if not cached/expired
        """
        key = self._make_key(query, query_type)

        if Cache is not None:
            result = self._cache.get(key)
            if result is not None:
                return CachedGeocodingResult(**result)
        else:
            # In-memory fallback
            if key in self._cache:
                cached_time = self._cache_times.get(key)
                if cached_time and datetime.now() - cached_time < timedelta(seconds=self.ttl):
                    return CachedGeocodingResult(**self._cache[key])
                else:
                    # Expired
                    del self._cache[key]
                    del self._cache_times[key]

        return None

    def set(
        self,
        query: str,
        result: CachedGeocodingResult,
        query_type: str = "forward",
        ttl: Optional[int] = None,
    ) -> None:
        """
        Cache a geocoding result.

        Args:
            query: The geocoding query
            result: The result to cache
            query_type: "forward" or "reverse"
            ttl: Optional custom TTL
        """
        key = self._make_key(query, query_type)
        ttl = ttl or self.ttl
        data = asdict(result)

        if Cache is not None:
            self._cache.set(key, data, expire=ttl)
        else:
            # In-memory fallback
            self._cache[key] = data
            self._cache_times[key] = datetime.now()

    def delete(self, query: str, query_type: str = "forward") -> bool:
        """
        Delete a cached result.

        Args:
            query: The geocoding query
            query_type: "forward" or "reverse"

        Returns:
            True if deleted, False if not found
        """
        key = self._make_key(query, query_type)

        if Cache is not None:
            return self._cache.delete(key)
        else:
            if key in self._cache:
                del self._cache[key]
                del self._cache_times[key]
                return True
            return False

    def clear(self) -> None:
        """Clear all cached results."""
        if Cache is not None:
            self._cache.clear()
        else:
            self._cache.clear()
            self._cache_times.clear()

    def stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        if Cache is not None:
            return {
                "size": self._cache.volume(),
                "count": len(self._cache),
                "directory": str(self._cache_dir),
                "backend": "diskcache",
            }
        else:
            return {
                "count": len(self._cache),
                "backend": "memory",
            }

    def close(self) -> None:
        """Close the cache (cleanup)."""
        if Cache is not None:
            self._cache.close()
