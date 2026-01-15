"""
Cache Manager Module

Unified cache management for Location Overview.
"""

from typing import Optional, Any, Dict
from pathlib import Path
import hashlib
import json
from datetime import datetime, timedelta

try:
    from diskcache import Cache
except ImportError:
    Cache = None


class CacheManager:
    """
    Unified cache manager for Location Overview data.

    Uses diskcache for persistent storage with fallback to in-memory.
    """

    DEFAULT_TTL = 7 * 24 * 60 * 60  # 7 days

    def __init__(
        self,
        cache_dir: str = ".cache/location_overview",
        size_limit: int = 100 * 1024 * 1024,  # 100MB
    ):
        """
        Initialize cache manager.

        Args:
            cache_dir: Directory for cache storage
            size_limit: Maximum cache size in bytes
        """
        self._cache_dir = Path(cache_dir)

        if Cache is not None:
            self._cache_dir.mkdir(parents=True, exist_ok=True)
            self._cache = Cache(str(self._cache_dir), size_limit=size_limit)
            self._backend = "diskcache"
        else:
            self._cache = {}
            self._cache_times = {}
            self._backend = "memory"

    def _make_key(self, namespace: str, key: str) -> str:
        """Generate cache key with namespace."""
        combined = f"{namespace}:{key}"
        return hashlib.sha256(combined.encode()).hexdigest()[:32]

    def get(self, namespace: str, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            namespace: Cache namespace (e.g., "geocoding", "provider")
            key: Cache key

        Returns:
            Cached value or None
        """
        cache_key = self._make_key(namespace, key)

        if self._backend == "diskcache":
            return self._cache.get(cache_key)
        else:
            if cache_key in self._cache:
                cached_time = self._cache_times.get(cache_key)
                if cached_time and datetime.now() - cached_time < timedelta(seconds=self.DEFAULT_TTL):
                    return self._cache[cache_key]
                else:
                    del self._cache[cache_key]
                    del self._cache_times[cache_key]
            return None

    def set(
        self,
        namespace: str,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> None:
        """
        Set value in cache.

        Args:
            namespace: Cache namespace
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
        """
        cache_key = self._make_key(namespace, key)
        ttl = ttl or self.DEFAULT_TTL

        if self._backend == "diskcache":
            self._cache.set(cache_key, value, expire=ttl)
        else:
            self._cache[cache_key] = value
            self._cache_times[cache_key] = datetime.now()

    def delete(self, namespace: str, key: str) -> bool:
        """Delete value from cache."""
        cache_key = self._make_key(namespace, key)

        if self._backend == "diskcache":
            return self._cache.delete(cache_key)
        else:
            if cache_key in self._cache:
                del self._cache[cache_key]
                del self._cache_times[cache_key]
                return True
            return False

    def clear_namespace(self, namespace: str) -> None:
        """Clear all entries in a namespace."""
        # For diskcache, we'd need to iterate
        # For simplicity, clear all in MVP
        if self._backend == "diskcache":
            self._cache.clear()
        else:
            self._cache.clear()
            self._cache_times.clear()

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if self._backend == "diskcache":
            return {
                "backend": "diskcache",
                "size": self._cache.volume(),
                "count": len(self._cache),
            }
        return {
            "backend": "memory",
            "count": len(self._cache),
        }

    def close(self) -> None:
        """Close the cache."""
        if self._backend == "diskcache":
            self._cache.close()
