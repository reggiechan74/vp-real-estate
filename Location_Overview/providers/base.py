"""
Provider Base Class Module

Abstract base class for all data providers with standardized result format,
rate limiting, caching, and error handling.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ProviderStatus(Enum):
    """Status of provider query."""

    SUCCESS = "success"
    PARTIAL = "partial"  # Some data retrieved, some failed
    FAILED = "failed"
    CACHED = "cached"
    RATE_LIMITED = "rate_limited"
    TIMEOUT = "timeout"


@dataclass
class ProviderResult:
    """
    Standard result format for all providers.

    All providers return this format for consistent handling
    in the aggregation engine.
    """

    source: str
    success: bool
    data: Optional[Dict[str, Any]]
    error: Optional[str] = None
    cached: bool = False
    response_time_ms: float = 0.0
    status: ProviderStatus = ProviderStatus.SUCCESS
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderConfig:
    """Configuration for a provider."""

    name: str
    base_url: str
    rate_limit: float  # requests per second
    cache_ttl: int  # seconds
    timeout: float = 30.0  # request timeout
    enabled: bool = True
    api_key: Optional[str] = None
    municipalities: Optional[List[str]] = None  # List of supported municipalities


class BaseProvider(ABC):
    """
    Abstract base class for data providers.

    All providers must implement:
    - query(): Execute the data query
    - is_applicable(): Check if provider applies to municipality
    """

    # Class attributes (override in subclasses)
    name: str = "BaseProvider"
    base_url: str = ""
    rate_limit: float = 1.0  # Default: 1 request per second
    cache_ttl: int = 86400  # Default: 24 hours

    def __init__(
        self,
        config: Optional[ProviderConfig] = None,
        cache: Optional[Any] = None,
    ):
        """
        Initialize provider.

        Args:
            config: Optional provider configuration
            cache: Optional cache instance
        """
        if config:
            self.name = config.name
            self.base_url = config.base_url
            self.rate_limit = config.rate_limit
            self.cache_ttl = config.cache_ttl
            self.timeout = config.timeout
            self.enabled = config.enabled
            self.api_key = config.api_key
            self.municipalities = config.municipalities
        else:
            self.timeout = 30.0
            self.enabled = True
            self.api_key = None
            self.municipalities = None

        self.cache = cache
        self._last_request = 0.0

    @abstractmethod
    async def query(
        self,
        lat: float,
        lon: float,
        **kwargs,
    ) -> ProviderResult:
        """
        Execute query and return standardized result.

        Args:
            lat: Latitude (WGS84)
            lon: Longitude (WGS84)
            **kwargs: Additional query parameters

        Returns:
            ProviderResult with query results
        """
        pass

    @abstractmethod
    def is_applicable(self, municipality: str) -> bool:
        """
        Check if provider applies to given municipality.

        Args:
            municipality: Municipality name

        Returns:
            True if provider has data for this municipality
        """
        pass

    def _make_result(
        self,
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        response_time_ms: float = 0.0,
        cached: bool = False,
        warnings: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ProviderResult:
        """
        Create a standardized ProviderResult.

        Args:
            success: Whether query succeeded
            data: Query result data
            error: Error message if failed
            response_time_ms: Query response time
            cached: Whether result was from cache
            warnings: List of warning messages
            metadata: Additional metadata

        Returns:
            ProviderResult instance
        """
        if success:
            status = ProviderStatus.CACHED if cached else ProviderStatus.SUCCESS
        elif error and "rate limit" in error.lower():
            status = ProviderStatus.RATE_LIMITED
        elif error and "timeout" in error.lower():
            status = ProviderStatus.TIMEOUT
        else:
            status = ProviderStatus.FAILED

        return ProviderResult(
            source=self.name,
            success=success,
            data=data,
            error=error,
            cached=cached,
            response_time_ms=response_time_ms,
            status=status,
            warnings=warnings or [],
            metadata=metadata or {"queried_at": datetime.now().isoformat()},
        )

    def get_cache_key(self, lat: float, lon: float, **kwargs) -> str:
        """
        Generate cache key for query.

        Args:
            lat: Latitude
            lon: Longitude
            **kwargs: Additional parameters

        Returns:
            Cache key string
        """
        key_parts = [self.name, f"{lat:.6f}", f"{lon:.6f}"]
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")
        return ":".join(key_parts)
