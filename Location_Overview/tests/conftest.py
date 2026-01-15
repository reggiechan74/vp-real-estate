"""
Pytest Configuration and Fixtures

Shared fixtures for Location Overview tests.
"""

import pytest
import pytest_asyncio
from typing import Dict, Any

from Location_Overview.config import Config, reset_config


# pytest-asyncio configuration is in pytest.ini (asyncio_mode = auto)


@pytest.fixture
def test_config():
    """Create a test configuration."""
    reset_config()
    return Config()


@pytest.fixture
def toronto_address() -> str:
    """Sample Toronto address for testing."""
    return "100 Queen Street West, Toronto"


@pytest.fixture
def toronto_coordinates() -> Dict[str, float]:
    """Sample Toronto coordinates."""
    return {"latitude": 43.6532, "longitude": -79.3832}


@pytest.fixture
def valid_pin() -> str:
    """Valid Ontario PIN for testing."""
    return "123456789"


@pytest.fixture
def mock_geocoding_result() -> Dict[str, Any]:
    """Mock geocoding response."""
    return {
        "place_id": 123456,
        "lat": "43.6532",
        "lon": "-79.3832",
        "display_name": "100 Queen Street West, Toronto, ON, Canada",
        "address": {
            "house_number": "100",
            "road": "Queen Street West",
            "city": "Toronto",
            "state": "Ontario",
            "country": "Canada",
        },
        "osm_id": 12345678,
        "osm_type": "node",
    }


@pytest.fixture
def mock_toronto_zoning() -> Dict[str, Any]:
    """Mock Toronto zoning response."""
    return {
        "ZN_ZONE": "CR 3.0",
        "ZN_CATEGORY": "Commercial Residential",
        "OVERLAY": "None",
    }


@pytest.fixture
def mock_overpass_response() -> Dict[str, Any]:
    """Mock Overpass API response."""
    return {
        "elements": [
            {
                "type": "node",
                "id": 1,
                "lat": 43.6540,
                "lon": -79.3840,
                "tags": {"name": "Test School", "amenity": "school"},
            },
            {
                "type": "node",
                "id": 2,
                "lat": 43.6535,
                "lon": -79.3835,
                "tags": {"name": "Test Park", "leisure": "park"},
            },
            {
                "type": "node",
                "id": 3,
                "lat": 43.6530,
                "lon": -79.3830,
                "tags": {"name": "Subway Station", "railway": "subway_entrance"},
            },
        ]
    }


@pytest.fixture
def mock_provincial_plans() -> Dict[str, Any]:
    """Mock Ontario GeoHub response."""
    return {
        "greenbelt_area": False,
        "greenbelt_designation": None,
        "growth_plan_area": "Built-up Area",
        "oak_ridges_moraine": False,
        "orm_designation": None,
        "niagara_escarpment": False,
        "nec_designation": None,
        "natural_heritage": False,
    }


@pytest.fixture
def sample_addresses():
    """Collection of test addresses covering different scenarios."""
    return {
        "toronto_downtown": "100 Queen Street West, Toronto",
        "toronto_midtown": "1 Eglinton Avenue East, Toronto",
        "mississauga": "200 City Centre Drive, Mississauga",
        "ottawa": "110 Laurier Avenue West, Ottawa",
        "with_unit": "Suite 500, 100 King Street West, Toronto",
        "abbreviated": "100 Queen St W, Toronto",
        "no_city": "100 Queen Street West",
        "invalid": "xyz123",
    }
