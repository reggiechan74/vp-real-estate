"""Data providers for location overview information."""

from .base import BaseProvider, ProviderResult, ProviderConfig, ProviderStatus

# Phase 1 providers (MVP)
from .ontario_geohub import OntarioGeoHubProvider
from .toronto_opendata import TorontoOpenDataProvider
from .overpass import OverpassProvider

# Phase 2 providers (Enhanced)
from .heritage import HeritageProvider
from .brownfields import BrownfieldsProvider
from .trca import TRCAProvider
from .ottawa_arcgis import OttawaArcGISProvider
from .gtfs import GTFSProvider
from .census import CensusProvider

__all__ = [
    # Base classes
    "BaseProvider",
    "ProviderResult",
    "ProviderConfig",
    "ProviderStatus",
    # Phase 1 providers
    "OntarioGeoHubProvider",
    "TorontoOpenDataProvider",
    "OverpassProvider",
    # Phase 2 providers
    "HeritageProvider",
    "BrownfieldsProvider",
    "TRCAProvider",
    "OttawaArcGISProvider",
    "GTFSProvider",
    "CensusProvider",
]
