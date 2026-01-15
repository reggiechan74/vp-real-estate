"""
Configuration Module

Centralized configuration for the Location Overview module.
Handles API keys, rate limits, cache settings, and timeouts.
"""

import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from pathlib import Path


@dataclass
class GeocodingConfig:
    """Configuration for geocoding services."""

    nominatim_user_agent: str = "LocationOverview/1.0 (lease-abstract-toolkit)"
    nominatim_rate_limit: float = 1.0  # requests per second
    nominatim_timeout: float = 10.0
    google_api_key: Optional[str] = None  # Optional fallback
    cache_ttl: int = 7 * 24 * 60 * 60  # 7 days


@dataclass
class ProviderConfig:
    """Configuration for data providers."""

    # ═══════════════════════════════════════════════════════════════════════
    # Phase 1 Providers (MVP)
    # ═══════════════════════════════════════════════════════════════════════

    # Ontario GeoHub
    ontario_geohub_rate_limit: float = 5.0
    ontario_geohub_timeout: float = 15.0
    ontario_geohub_cache_ttl: int = 30 * 24 * 60 * 60  # 30 days

    # Toronto Open Data
    toronto_rate_limit: float = 10.0
    toronto_timeout: float = 15.0
    toronto_cache_ttl: int = 7 * 24 * 60 * 60  # 7 days

    # Overpass API
    overpass_rate_limit: float = 1.0  # Conservative
    overpass_timeout: float = 60.0
    overpass_cache_ttl: int = 7 * 24 * 60 * 60  # 7 days
    overpass_search_radius: int = 1500  # meters

    # ═══════════════════════════════════════════════════════════════════════
    # Phase 2 Providers (Enhanced)
    # ═══════════════════════════════════════════════════════════════════════

    # Heritage Provider
    heritage_rate_limit: float = 1.0
    heritage_timeout: float = 15.0
    heritage_cache_ttl: int = 30 * 24 * 60 * 60  # 30 days (designations rarely change)
    heritage_enabled: bool = True

    # Brownfields ESR Provider
    brownfields_rate_limit: float = 1.0
    brownfields_timeout: float = 15.0
    brownfields_cache_ttl: int = 7 * 24 * 60 * 60  # 7 days
    brownfields_search_radius: int = 250  # meters
    brownfields_enabled: bool = True

    # TRCA Conservation Provider
    trca_rate_limit: float = 2.0
    trca_timeout: float = 15.0
    trca_cache_ttl: int = 30 * 24 * 60 * 60  # 30 days
    trca_enabled: bool = True

    # Ottawa ArcGIS Provider
    ottawa_rate_limit: float = 5.0
    ottawa_timeout: float = 15.0
    ottawa_cache_ttl: int = 7 * 24 * 60 * 60  # 7 days
    ottawa_enabled: bool = True

    # GTFS Transit Provider
    gtfs_rate_limit: float = 5.0
    gtfs_timeout: float = 15.0
    gtfs_cache_ttl: int = 24 * 60 * 60  # 24 hours (schedules change)
    gtfs_search_radius: int = 1000  # meters
    gtfs_enabled: bool = True

    # Census Demographics Provider
    census_rate_limit: float = 2.0
    census_timeout: float = 15.0
    census_cache_ttl: int = 90 * 24 * 60 * 60  # 90 days (census data stable)
    census_enabled: bool = True


@dataclass
class CacheConfig:
    """Configuration for caching."""

    enabled: bool = True
    directory: str = ".cache/location_overview"
    size_limit: int = 100 * 1024 * 1024  # 100MB
    default_ttl: int = 7 * 24 * 60 * 60  # 7 days


@dataclass
class OutputConfig:
    """Configuration for output generation."""

    reports_directory: str = "Reports"
    template_directory: Optional[str] = None  # Use default
    timestamp_format: str = "%Y-%m-%d_%H%M%S"
    default_format: str = "markdown"  # markdown or json


@dataclass
class Config:
    """
    Main configuration class for Location Overview.

    Load from environment variables or use defaults.
    """

    geocoding: GeocodingConfig = field(default_factory=GeocodingConfig)
    providers: ProviderConfig = field(default_factory=ProviderConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    output: OutputConfig = field(default_factory=OutputConfig)

    # Global settings
    default_timeout: float = 30.0
    max_parallel_providers: int = 5
    debug: bool = False
    log_level: str = "INFO"

    @classmethod
    def from_environment(cls) -> "Config":
        """
        Create configuration from environment variables.

        Environment variables:
        - LO_NOMINATIM_USER_AGENT: Nominatim user agent string
        - LO_GOOGLE_API_KEY: Google Geocoding API key (optional)
        - LO_CACHE_ENABLED: Enable/disable caching (true/false)
        - LO_CACHE_DIRECTORY: Cache directory path
        - LO_REPORTS_DIRECTORY: Reports output directory
        - LO_DEBUG: Enable debug mode (true/false)
        - LO_LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR)

        Returns:
            Config instance
        """
        config = cls()

        # Geocoding
        if user_agent := os.environ.get("LO_NOMINATIM_USER_AGENT"):
            config.geocoding.nominatim_user_agent = user_agent
        if google_key := os.environ.get("LO_GOOGLE_API_KEY"):
            config.geocoding.google_api_key = google_key

        # Cache
        if cache_enabled := os.environ.get("LO_CACHE_ENABLED"):
            config.cache.enabled = cache_enabled.lower() == "true"
        if cache_dir := os.environ.get("LO_CACHE_DIRECTORY"):
            config.cache.directory = cache_dir

        # Output
        if reports_dir := os.environ.get("LO_REPORTS_DIRECTORY"):
            config.output.reports_directory = reports_dir

        # Global
        if debug := os.environ.get("LO_DEBUG"):
            config.debug = debug.lower() == "true"
        if log_level := os.environ.get("LO_LOG_LEVEL"):
            config.log_level = log_level.upper()

        return config

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        from dataclasses import asdict

        return asdict(self)


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get the global configuration instance.

    Creates from environment on first call.

    Returns:
        Config instance
    """
    global _config
    if _config is None:
        _config = Config.from_environment()
    return _config


def set_config(config: Config) -> None:
    """
    Set the global configuration instance.

    Args:
        config: Config instance to use
    """
    global _config
    _config = config


def reset_config() -> None:
    """Reset global configuration (for testing)."""
    global _config
    _config = None
