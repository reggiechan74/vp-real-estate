"""
Unit Tests for Municipality Detector

Tests for coordinate-based municipality detection.
"""

import pytest

from Location_Overview.input.municipality_detector import (
    detect_municipality,
    get_municipality_config,
    get_region,
    is_gta,
    get_supported_municipalities,
    get_municipalities_by_region,
)


class TestDetectMunicipality:
    """Tests for detect_municipality function."""

    def test_detect_toronto(self):
        """Test detection of Toronto."""
        # Downtown Toronto coordinates
        municipality, provider = detect_municipality(43.6532, -79.3832)
        assert municipality == "Toronto"
        assert provider == "toronto_opendata"

    def test_detect_mississauga(self):
        """Test detection of Mississauga."""
        # Square One area
        municipality, provider = detect_municipality(43.5932, -79.6418)
        assert municipality == "Mississauga"

    def test_detect_ottawa(self):
        """Test detection of Ottawa."""
        # Parliament Hill area
        municipality, provider = detect_municipality(45.4215, -75.6972)
        assert municipality == "Ottawa"

    def test_detect_unknown(self):
        """Test detection of unknown location."""
        # Location outside defined municipalities
        municipality, provider = detect_municipality(50.0, -85.0)
        assert municipality == "Ontario"
        assert provider == "generic_municipal"


class TestGetMunicipalityConfig:
    """Tests for get_municipality_config function."""

    def test_get_toronto_config(self):
        """Test getting Toronto configuration."""
        config = get_municipality_config("Toronto")
        assert config is not None
        assert config.name == "Toronto"
        assert config.data_provider == "toronto_opendata"

    def test_get_nonexistent_config(self):
        """Test getting non-existent municipality."""
        config = get_municipality_config("NonexistentCity")
        assert config is None


class TestGetRegion:
    """Tests for get_region function."""

    def test_gta_region(self):
        """Test GTA region detection."""
        region = get_region(43.6532, -79.3832)  # Toronto
        assert region == "GTA"

    def test_eastern_ontario(self):
        """Test Eastern Ontario detection."""
        region = get_region(45.4215, -75.6972)  # Ottawa
        assert region == "Eastern Ontario"


class TestIsGta:
    """Tests for is_gta function."""

    def test_toronto_is_gta(self):
        """Test that Toronto is in GTA."""
        assert is_gta(43.6532, -79.3832) is True

    def test_mississauga_is_gta(self):
        """Test that Mississauga is in GTA."""
        assert is_gta(43.5932, -79.6418) is True

    def test_ottawa_not_gta(self):
        """Test that Ottawa is not in GTA."""
        assert is_gta(45.4215, -75.6972) is False


class TestGetSupportedMunicipalities:
    """Tests for get_supported_municipalities function."""

    def test_includes_major_cities(self):
        """Test that major cities are included."""
        municipalities = get_supported_municipalities()
        assert "Toronto" in municipalities
        assert "Ottawa" in municipalities
        assert "Mississauga" in municipalities
        assert "Hamilton" in municipalities

    def test_returns_list(self):
        """Test that function returns a list."""
        municipalities = get_supported_municipalities()
        assert isinstance(municipalities, list)
        assert len(municipalities) > 0


class TestGetMunicipalitiesByRegion:
    """Tests for get_municipalities_by_region function."""

    def test_gta_municipalities(self):
        """Test getting GTA municipalities."""
        gta = get_municipalities_by_region("GTA")
        assert "Toronto" in gta
        assert "Mississauga" in gta
        assert "Markham" in gta

    def test_eastern_ontario(self):
        """Test getting Eastern Ontario municipalities."""
        eastern = get_municipalities_by_region("Eastern Ontario")
        assert "Ottawa" in eastern

    def test_empty_region(self):
        """Test non-existent region."""
        result = get_municipalities_by_region("NonexistentRegion")
        assert result == []
