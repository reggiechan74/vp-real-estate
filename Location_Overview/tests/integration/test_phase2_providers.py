"""
Integration Tests for Phase 2 Providers

Tests the Phase 2 providers with real API calls to verify:
- Provider initialization and configuration
- Query execution and result parsing
- Error handling and graceful degradation
- Municipality applicability filtering
"""

import pytest
import asyncio
from typing import Dict, Any

# Import Phase 2 providers
from Location_Overview.providers.heritage import HeritageProvider
from Location_Overview.providers.brownfields import BrownfieldsProvider
from Location_Overview.providers.trca import TRCAProvider
from Location_Overview.providers.ottawa_arcgis import OttawaArcGISProvider
from Location_Overview.providers.gtfs import GTFSProvider
from Location_Overview.providers.census import CensusProvider
from Location_Overview.providers.base import ProviderResult, ProviderStatus


# Test coordinates
TORONTO_DOWNTOWN = (43.6532, -79.3832)  # Downtown Toronto (King & Bay)
TORONTO_DISTILLERY = (43.6503, -79.3596)  # Distillery District (heritage)
OTTAWA_DOWNTOWN = (45.4215, -75.6972)  # Downtown Ottawa
MISSISSAUGA_SQUARE_ONE = (43.5931, -79.6418)  # Square One
MARKHAM_MAIN = (43.8561, -79.3370)  # Markham Main Street


class TestHeritageProvider:
    """Tests for HeritageProvider."""

    @pytest.fixture
    def provider(self):
        return HeritageProvider()

    def test_init(self, provider):
        """Test provider initialization."""
        assert provider.name == "Heritage Registry"
        assert provider.rate_limit == 1.0
        assert provider.cache_ttl == 86400 * 30

    def test_is_applicable(self, provider):
        """Test municipality applicability."""
        assert provider.is_applicable("Toronto") is True
        assert provider.is_applicable("Ottawa") is True
        assert provider.is_applicable("Markham") is True

    @pytest.mark.asyncio
    async def test_query_toronto_heritage_area(self, provider):
        """Test query in heritage-rich area (Distillery District)."""
        lat, lon = TORONTO_DISTILLERY
        result = await provider.query(lat, lon, municipality="Toronto")

        assert isinstance(result, ProviderResult)
        assert result.source == "Heritage Registry"
        # Note: Actual heritage status depends on API response

    @pytest.mark.asyncio
    async def test_query_result_structure(self, provider):
        """Test query returns expected data structure."""
        lat, lon = TORONTO_DOWNTOWN
        result = await provider.query(lat, lon, municipality="Toronto")

        assert result.success is True or result.error is not None
        if result.success and result.data:
            assert "heritage_designated" in result.data
            assert "designation_type" in result.data


class TestBrownfieldsProvider:
    """Tests for BrownfieldsProvider."""

    @pytest.fixture
    def provider(self):
        return BrownfieldsProvider()

    def test_init(self, provider):
        """Test provider initialization."""
        assert provider.name == "Brownfields ESR"
        assert provider.rate_limit == 1.0

    def test_is_applicable(self, provider):
        """Test municipality applicability - province-wide."""
        assert provider.is_applicable("Toronto") is True
        assert provider.is_applicable("Ottawa") is True
        assert provider.is_applicable("Thunder Bay") is True

    @pytest.mark.asyncio
    async def test_query_toronto(self, provider):
        """Test query in Toronto."""
        lat, lon = TORONTO_DOWNTOWN
        result = await provider.query(lat, lon, municipality="Toronto")

        assert isinstance(result, ProviderResult)
        assert result.source == "Brownfields ESR"

    @pytest.mark.asyncio
    async def test_query_result_structure(self, provider):
        """Test query returns expected data structure."""
        lat, lon = TORONTO_DOWNTOWN
        result = await provider.query(lat, lon, municipality="Toronto")

        if result.success and result.data:
            assert "brownfield_record" in result.data
            assert "rsc_filed" in result.data
            assert "esr_search_url" in result.data


class TestTRCAProvider:
    """Tests for TRCAProvider."""

    @pytest.fixture
    def provider(self):
        return TRCAProvider()

    def test_init(self, provider):
        """Test provider initialization."""
        assert provider.name == "TRCA Conservation"
        assert provider.rate_limit == 2.0

    def test_is_applicable(self, provider):
        """Test municipality applicability."""
        assert provider.is_applicable("Toronto") is True
        assert provider.is_applicable("Mississauga") is True
        assert provider.is_applicable("Markham") is True

    def test_get_conservation_authority(self, provider):
        """Test CA jurisdiction detection."""
        assert provider._get_conservation_authority("toronto") == "trca"
        assert provider._get_conservation_authority("mississauga") == "cvc"
        assert provider._get_conservation_authority("markham") == "trca"

    @pytest.mark.asyncio
    async def test_query_toronto(self, provider):
        """Test query in Toronto."""
        lat, lon = TORONTO_DOWNTOWN
        result = await provider.query(lat, lon, municipality="Toronto")

        assert isinstance(result, ProviderResult)
        assert result.source == "TRCA Conservation"

    @pytest.mark.asyncio
    async def test_query_result_structure(self, provider):
        """Test query returns expected data structure."""
        lat, lon = TORONTO_DOWNTOWN
        result = await provider.query(lat, lon, municipality="Toronto")

        if result.success and result.data:
            assert "in_regulated_area" in result.data
            assert "floodplain" in result.data
            assert "conservation_authority" in result.data


class TestOttawaArcGISProvider:
    """Tests for OttawaArcGISProvider."""

    @pytest.fixture
    def provider(self):
        return OttawaArcGISProvider()

    def test_init(self, provider):
        """Test provider initialization."""
        assert provider.name == "Ottawa Open Data"
        assert provider.rate_limit == 5.0

    def test_is_applicable(self, provider):
        """Test municipality applicability - Ottawa only."""
        assert provider.is_applicable("Ottawa") is True
        assert provider.is_applicable("City of Ottawa") is True
        assert provider.is_applicable("Toronto") is False
        assert provider.is_applicable("Mississauga") is False

    @pytest.mark.asyncio
    async def test_query_ottawa_downtown(self, provider):
        """Test query in downtown Ottawa."""
        lat, lon = OTTAWA_DOWNTOWN
        result = await provider.query(lat, lon)

        assert isinstance(result, ProviderResult)
        assert result.source == "Ottawa Open Data"

    @pytest.mark.asyncio
    async def test_query_result_structure(self, provider):
        """Test query returns expected data structure."""
        lat, lon = OTTAWA_DOWNTOWN
        result = await provider.query(lat, lon)

        if result.success and result.data:
            assert "zoning_designation" in result.data
            assert "permitted_uses" in result.data
            assert "ward" in result.data

    def test_zone_category_mapping(self, provider):
        """Test zone category mapping."""
        assert provider._get_zone_category("R1A") == "Residential"
        assert provider._get_zone_category("GM") == "General Mixed Use"
        assert provider._get_zone_category("IL") == "Light Industrial"


class TestGTFSProvider:
    """Tests for GTFSProvider."""

    @pytest.fixture
    def provider(self):
        return GTFSProvider()

    def test_init(self, provider):
        """Test provider initialization."""
        assert provider.name == "Transit GTFS"
        assert provider.rate_limit == 5.0
        assert provider.cache_ttl == 24 * 60 * 60  # 24 hours

    def test_is_applicable(self, provider):
        """Test municipality applicability."""
        assert provider.is_applicable("Toronto") is True
        assert provider.is_applicable("Ottawa") is True
        assert provider.is_applicable("Mississauga") is True
        assert provider.is_applicable("Thunder Bay") is False

    @pytest.mark.asyncio
    async def test_query_toronto_downtown(self, provider):
        """Test query in transit-rich downtown Toronto."""
        lat, lon = TORONTO_DOWNTOWN
        result = await provider.query(lat, lon, municipality="Toronto")

        assert isinstance(result, ProviderResult)
        assert result.source == "Transit GTFS"

    @pytest.mark.asyncio
    async def test_query_result_structure(self, provider):
        """Test query returns expected data structure."""
        lat, lon = TORONTO_DOWNTOWN
        result = await provider.query(lat, lon, municipality="Toronto")

        if result.success and result.data:
            assert "transit_stops" in result.data
            assert "transit_score" in result.data
            assert "service_summary" in result.data

    def test_transit_score_calculation(self, provider):
        """Test transit score calculation."""
        # Mock results with subway nearby
        results = {
            "nearest_subway": {"name": "King Station", "distance_m": 200},
            "nearest_bus_stop": {"name": "King & Bay", "distance_m": 50},
            "transit_stops": [{"type": "bus"}, {"type": "bus"}, {"type": "subway"}],
        }
        score = provider._calculate_transit_score(results)
        assert score > 0
        assert score <= 100


class TestCensusProvider:
    """Tests for CensusProvider."""

    @pytest.fixture
    def provider(self):
        return CensusProvider()

    def test_init(self, provider):
        """Test provider initialization."""
        assert provider.name == "Census Demographics"
        assert provider.rate_limit == 2.0
        assert provider.cache_ttl == 90 * 24 * 60 * 60  # 90 days

    def test_is_applicable(self, provider):
        """Test municipality applicability - province-wide."""
        assert provider.is_applicable("Toronto") is True
        assert provider.is_applicable("Ottawa") is True
        assert provider.is_applicable("Thunder Bay") is True

    @pytest.mark.asyncio
    async def test_query_toronto(self, provider):
        """Test query in Toronto."""
        lat, lon = TORONTO_DOWNTOWN
        result = await provider.query(lat, lon, municipality="Toronto")

        assert isinstance(result, ProviderResult)
        assert result.source == "Census Demographics"

    @pytest.mark.asyncio
    async def test_query_result_structure(self, provider):
        """Test query returns expected data structure."""
        lat, lon = TORONTO_DOWNTOWN
        result = await provider.query(lat, lon, municipality="Toronto")

        if result.success and result.data:
            assert "census_year" in result.data


class TestProviderIntegration:
    """Integration tests across multiple providers."""

    @pytest.mark.asyncio
    async def test_all_providers_toronto(self):
        """Test all applicable providers for Toronto location."""
        lat, lon = TORONTO_DOWNTOWN
        municipality = "Toronto"

        providers = [
            HeritageProvider(),
            BrownfieldsProvider(),
            TRCAProvider(),
            GTFSProvider(),
            CensusProvider(),
        ]

        results = []
        for provider in providers:
            if provider.is_applicable(municipality):
                result = await provider.query(lat, lon, municipality=municipality)
                results.append((provider.name, result))

        # All applicable providers should return results
        assert len(results) >= 4

        for name, result in results:
            assert isinstance(result, ProviderResult)
            assert result.source == name

    @pytest.mark.asyncio
    async def test_all_providers_ottawa(self):
        """Test all applicable providers for Ottawa location."""
        lat, lon = OTTAWA_DOWNTOWN
        municipality = "Ottawa"

        providers = [
            HeritageProvider(),
            BrownfieldsProvider(),
            TRCAProvider(),
            OttawaArcGISProvider(),
            GTFSProvider(),
            CensusProvider(),
        ]

        results = []
        for provider in providers:
            if provider.is_applicable(municipality):
                result = await provider.query(lat, lon, municipality=municipality)
                results.append((provider.name, result))

        # Ottawa should have OttawaArcGIS provider
        provider_names = [name for name, _ in results]
        assert "Ottawa Open Data" in provider_names

    @pytest.mark.asyncio
    async def test_graceful_degradation(self):
        """Test providers handle invalid coordinates gracefully."""
        # Coordinates outside Ontario
        lat, lon = (0.0, 0.0)  # Null Island

        providers = [
            HeritageProvider(),
            BrownfieldsProvider(),
            TRCAProvider(),
            OttawaArcGISProvider(),
            GTFSProvider(),
            CensusProvider(),
        ]

        for provider in providers:
            result = await provider.query(lat, lon, municipality="Unknown")
            # Should not raise exceptions
            assert isinstance(result, ProviderResult)
            # May fail but should fail gracefully
            if not result.success:
                assert result.error is not None


# Fixtures for pytest-asyncio
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
