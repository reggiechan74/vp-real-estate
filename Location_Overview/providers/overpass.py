"""
Overpass API Provider Module

Queries OpenStreetMap via Overpass API for nearby amenities:
- Schools (elementary, secondary, colleges, universities)
- Healthcare (hospitals, clinics, pharmacies)
- Recreation (parks, playgrounds, sports centres)
- Shopping (supermarkets, malls, markets)
- Transit (bus stations, subway entrances, train stations)
- Services (banks, post offices, libraries)

Uses Overpass QL for efficient spatial queries.
"""

import time
from typing import Dict, Any, List, Optional
from math import radians, cos, sin, sqrt, atan2

import httpx

from .base import BaseProvider, ProviderResult


class OverpassProvider(BaseProvider):
    """
    Query OpenStreetMap via Overpass API for nearby amenities.

    Respects Overpass API guidelines:
    - Reasonable query sizes
    - Timeout handling
    - Rate limiting
    """

    name = "Overpass API"
    base_url = "https://overpass-api.de/api/interpreter"
    rate_limit = 1.0  # 1 request per second (conservative)
    cache_ttl = 86400 * 7  # 7 days

    # Alternative endpoints if primary is overloaded
    FALLBACK_URLS = [
        "https://overpass.kumi.systems/api/interpreter",
        "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    ]

    # Amenity types to query, organized by category
    AMENITY_TYPES = {
        "education": ["school", "kindergarten", "college", "university", "library"],
        "healthcare": ["hospital", "clinic", "pharmacy", "doctors", "dentist"],
        "recreation": ["park", "playground", "sports_centre", "swimming_pool", "fitness_centre"],
        "shopping": ["supermarket", "mall", "convenience", "marketplace", "department_store"],
        "transit": ["bus_station", "subway_entrance", "train_station", "ferry_terminal"],
        "services": ["bank", "post_office", "community_centre", "fire_station", "police"],
        "food": ["restaurant", "cafe", "fast_food"],
    }

    # Type to category mapping (reverse lookup)
    TYPE_TO_CATEGORY = {
        amenity: category
        for category, amenities in AMENITY_TYPES.items()
        for amenity in amenities
    }

    async def query(
        self,
        lat: float,
        lon: float,
        radius_m: int = 1500,
        **kwargs,
    ) -> ProviderResult:
        """
        Query nearby amenities within radius.

        Args:
            lat: Latitude (WGS84)
            lon: Longitude (WGS84)
            radius_m: Search radius in meters (default: 1500m)

        Returns:
            ProviderResult with amenity data
        """
        start_time = time.time()

        try:
            # Build Overpass QL query
            query = self._build_query(lat, lon, radius_m)

            # Try primary endpoint, then fallbacks
            data = await self._execute_query(query)

            if data is None:
                return self._make_result(
                    success=False,
                    error="All Overpass API endpoints failed",
                    response_time_ms=(time.time() - start_time) * 1000,
                )

            # Parse and categorize results
            amenities = self._parse_amenities(data, lat, lon)

            # Generate summary statistics
            summary = self._summarize_amenities(amenities)

            # Get transit accessibility assessment
            transit_assessment = self._assess_transit(amenities)

            # Get walkability notes
            walkability = self._assess_walkability(amenities, summary)

            response_time = (time.time() - start_time) * 1000

            return self._make_result(
                success=True,
                data={
                    "amenities": amenities[:50],  # Limit to top 50 by distance
                    "summary": summary,
                    "transit_accessibility": transit_assessment,
                    "walkability_notes": walkability,
                    "total_found": len(amenities),
                    "search_radius_m": radius_m,
                },
                response_time_ms=response_time,
                metadata={
                    "source": "OpenStreetMap via Overpass API",
                    "attribution": "© OpenStreetMap contributors",
                },
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return self._make_result(
                success=False,
                error=str(e),
                response_time_ms=response_time,
            )

    async def _execute_query(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Execute Overpass query with fallback endpoints.

        Args:
            query: Overpass QL query string

        Returns:
            Query result or None if all endpoints fail
        """
        endpoints = [self.base_url] + self.FALLBACK_URLS

        for endpoint in endpoints:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        endpoint,
                        data={"data": query},
                        timeout=60.0,
                        headers={"User-Agent": "LocationOverview/1.0"},
                    )

                    if response.status_code == 200:
                        return response.json()

            except Exception:
                continue  # Try next endpoint

        return None

    def _build_query(self, lat: float, lon: float, radius_m: int) -> str:
        """
        Build Overpass QL query for amenities.

        Args:
            lat: Latitude
            lon: Longitude
            radius_m: Search radius in meters

        Returns:
            Overpass QL query string
        """
        # Build amenity filter from all types
        all_amenities = [
            amenity for amenities in self.AMENITY_TYPES.values() for amenity in amenities
        ]
        amenity_filter = "|".join(all_amenities)

        return f"""
        [out:json][timeout:30];
        (
          // Amenities (schools, hospitals, banks, etc.)
          node["amenity"~"{amenity_filter}"](around:{radius_m},{lat},{lon});
          way["amenity"~"{amenity_filter}"](around:{radius_m},{lat},{lon});

          // Leisure facilities (parks, playgrounds, sports)
          node["leisure"~"park|playground|sports_centre|swimming_pool|fitness_centre"](around:{radius_m},{lat},{lon});
          way["leisure"~"park|playground|sports_centre|swimming_pool|fitness_centre"](around:{radius_m},{lat},{lon});

          // Public transport
          node["public_transport"="station"](around:{radius_m},{lat},{lon});
          node["railway"~"station|subway_entrance"](around:{radius_m},{lat},{lon});
          node["highway"="bus_stop"](around:{radius_m},{lat},{lon});

          // Shopping
          node["shop"~"supermarket|mall|department_store|convenience"](around:{radius_m},{lat},{lon});
          way["shop"~"supermarket|mall|department_store|convenience"](around:{radius_m},{lat},{lon});
        );
        out body center;
        """

    def _parse_amenities(
        self,
        data: Dict[str, Any],
        origin_lat: float,
        origin_lon: float,
    ) -> List[Dict[str, Any]]:
        """
        Parse Overpass response into amenity list.

        Args:
            data: Overpass API response
            origin_lat: Origin latitude for distance calculation
            origin_lon: Origin longitude for distance calculation

        Returns:
            List of amenity dictionaries sorted by distance
        """
        amenities = []

        for element in data.get("elements", []):
            tags = element.get("tags", {})

            # Get coordinates (nodes have lat/lon, ways have center)
            if element["type"] == "node":
                elem_lat = element.get("lat")
                elem_lon = element.get("lon")
            else:
                center = element.get("center", {})
                elem_lat = center.get("lat")
                elem_lon = center.get("lon")

            if not (elem_lat and elem_lon):
                continue

            # Calculate distance
            distance = self._haversine(origin_lat, origin_lon, elem_lat, elem_lon)

            # Determine type and category
            amenity_type = self._get_amenity_type(tags)
            category = self._categorize_amenity(amenity_type, tags)

            if not amenity_type:
                continue

            # Get name (use type if no name)
            name = tags.get("name") or tags.get("brand") or f"Unnamed {amenity_type.replace('_', ' ').title()}"

            amenities.append({
                "name": name,
                "type": amenity_type,
                "category": category,
                "distance_m": round(distance),
                "lat": elem_lat,
                "lon": elem_lon,
                "address": tags.get("addr:street", ""),
                "osm_id": element.get("id"),
                "osm_type": element.get("type"),
            })

        # Sort by distance
        amenities.sort(key=lambda x: x["distance_m"])

        return amenities

    def _get_amenity_type(self, tags: Dict[str, str]) -> Optional[str]:
        """
        Extract amenity type from OSM tags.

        Args:
            tags: OSM element tags

        Returns:
            Amenity type string or None
        """
        # Check various tag keys in priority order
        for key in ["amenity", "leisure", "public_transport", "railway", "shop", "highway"]:
            value = tags.get(key)
            if value:
                return value

        return None

    def _categorize_amenity(self, amenity_type: str, tags: Dict[str, str]) -> str:
        """
        Map amenity type to category.

        Args:
            amenity_type: OSM amenity type
            tags: OSM element tags

        Returns:
            Category string
        """
        # Check direct mapping
        if amenity_type in self.TYPE_TO_CATEGORY:
            return self.TYPE_TO_CATEGORY[amenity_type]

        # Check for transit types
        if amenity_type in ["station", "subway_entrance", "bus_stop", "train_station"]:
            return "transit"

        # Check for parks/leisure
        if amenity_type in ["park", "playground", "sports_centre", "swimming_pool", "fitness_centre"]:
            return "recreation"

        return "other"

    def _summarize_amenities(self, amenities: List[Dict]) -> Dict[str, Dict]:
        """
        Create summary statistics by category.

        Args:
            amenities: List of amenity dictionaries

        Returns:
            Summary dict with counts and nearest distances
        """
        summary = {}

        for amenity in amenities:
            cat = amenity["category"]
            if cat not in summary:
                summary[cat] = {
                    "count": 0,
                    "nearest_m": float("inf"),
                    "nearest_name": None,
                }

            summary[cat]["count"] += 1
            if amenity["distance_m"] < summary[cat]["nearest_m"]:
                summary[cat]["nearest_m"] = amenity["distance_m"]
                summary[cat]["nearest_name"] = amenity["name"]

        # Convert infinite to None for JSON
        for cat in summary:
            if summary[cat]["nearest_m"] == float("inf"):
                summary[cat]["nearest_m"] = None

        return summary

    def _assess_transit(self, amenities: List[Dict]) -> str:
        """
        Assess transit accessibility based on nearby transit options.

        Args:
            amenities: List of amenity dictionaries

        Returns:
            Transit accessibility description
        """
        transit_amenities = [a for a in amenities if a["category"] == "transit"]

        if not transit_amenities:
            return "Limited transit access - no transit stops found within search radius"

        # Find closest transit
        closest = min(transit_amenities, key=lambda x: x["distance_m"])
        total_stops = len(transit_amenities)

        if closest["distance_m"] <= 200:
            if closest["type"] in ["station", "subway_entrance"]:
                return f"Excellent transit access - {closest['name']} ({closest['type'].replace('_', ' ')}) {closest['distance_m']}m away, {total_stops} transit options nearby"
            return f"Good transit access - bus stop {closest['distance_m']}m away, {total_stops} transit options nearby"
        elif closest["distance_m"] <= 500:
            return f"Moderate transit access - nearest transit {closest['distance_m']}m away, {total_stops} options within search area"
        else:
            return f"Fair transit access - nearest transit {closest['distance_m']}m away"

    def _assess_walkability(
        self,
        amenities: List[Dict],
        summary: Dict[str, Dict],
    ) -> str:
        """
        Generate walkability notes based on amenity mix.

        Args:
            amenities: List of amenity dictionaries
            summary: Category summary

        Returns:
            Walkability description
        """
        notes = []

        # Check for essential services within walking distance (500m)
        categories_within_500m = []
        for cat, data in summary.items():
            if data["nearest_m"] and data["nearest_m"] <= 500:
                categories_within_500m.append(cat)

        if len(categories_within_500m) >= 4:
            notes.append("Highly walkable area with diverse amenities within 500m")
        elif len(categories_within_500m) >= 2:
            notes.append("Moderately walkable with some amenities nearby")
        else:
            notes.append("Limited walkability - few amenities within walking distance")

        # Specific notes
        if "shopping" in summary and summary["shopping"]["nearest_m"]:
            if summary["shopping"]["nearest_m"] <= 500:
                notes.append(f"Grocery/shopping: {summary['shopping']['nearest_name']} ({summary['shopping']['nearest_m']}m)")

        if "education" in summary and summary["education"]["nearest_m"]:
            if summary["education"]["nearest_m"] <= 1000:
                notes.append(f"School nearby: {summary['education']['nearest_name']} ({summary['education']['nearest_m']}m)")

        if "healthcare" in summary and summary["healthcare"]["nearest_m"]:
            notes.append(f"Healthcare: {summary['healthcare']['nearest_name']} ({summary['healthcare']['nearest_m']}m)")

        if "recreation" in summary and summary["recreation"]["nearest_m"]:
            if summary["recreation"]["nearest_m"] <= 500:
                notes.append(f"Park/recreation: {summary['recreation']['nearest_name']} ({summary['recreation']['nearest_m']}m)")

        return ". ".join(notes) if notes else "Amenity assessment not available"

    def _haversine(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:
        """
        Calculate distance between two points using Haversine formula.

        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates

        Returns:
            Distance in meters
        """
        R = 6371000  # Earth radius in meters

        phi1, phi2 = radians(lat1), radians(lat2)
        delta_phi = radians(lat2 - lat1)
        delta_lambda = radians(lon2 - lon1)

        a = sin(delta_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(delta_lambda / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return R * c

    def is_applicable(self, municipality: str) -> bool:
        """
        Overpass API works globally.

        Args:
            municipality: Municipality name

        Returns:
            Always True
        """
        return True
