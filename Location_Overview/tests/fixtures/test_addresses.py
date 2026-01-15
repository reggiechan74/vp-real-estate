"""
Test Addresses and Expected Results

Standard test data for Location Overview testing.
"""

# Addresses for testing geocoding and municipality detection
TEST_ADDRESSES = [
    {
        "input": "100 Queen Street West, Toronto",
        "expected_municipality": "Toronto",
        "expected_lat": 43.6532,
        "expected_lon": -79.3832,
        "expected_zone_prefix": "CR",
        "description": "Toronto City Hall area",
    },
    {
        "input": "110 Laurier Avenue West, Ottawa",
        "expected_municipality": "Ottawa",
        "expected_lat": 45.4215,
        "expected_lon": -75.7000,
        "description": "Parliament Hill area",
    },
    {
        "input": "200 City Centre Drive, Mississauga",
        "expected_municipality": "Mississauga",
        "expected_lat": 43.5930,
        "expected_lon": -79.6418,
        "description": "Square One area",
    },
    {
        "input": "1 Yonge Street, Toronto",
        "expected_municipality": "Toronto",
        "expected_lat": 43.6426,
        "expected_lon": -79.3760,
        "description": "Waterfront area",
    },
]

# PINs for testing
TEST_PINS = [
    {
        "input": "123456789",
        "formatted": "12345-6789",
        "is_valid": True,
    },
    {
        "input": "12345-6789",
        "formatted": "12345-6789",
        "is_valid": True,
    },
    {
        "input": "000001234",
        "is_valid": False,
        "reason": "Block number cannot be 00000",
    },
    {
        "input": "12345",
        "is_valid": False,
        "reason": "Too short",
    },
]

# Addresses in special plan areas for testing provincial plans
TEST_PROVINCIAL_PLANS = [
    {
        "description": "Location in Greenbelt",
        "expected_greenbelt": True,
        "expected_orm": False,
    },
    {
        "description": "Location in Growth Plan Built-up Area",
        "expected_growth_plan": "Built-up Area",
    },
]

# Expected amenity types from Overpass API
EXPECTED_AMENITY_CATEGORIES = [
    "education",
    "healthcare",
    "recreation",
    "shopping",
    "transit",
    "services",
]
