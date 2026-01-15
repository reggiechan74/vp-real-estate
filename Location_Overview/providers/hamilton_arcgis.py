"""
Hamilton ArcGIS Provider Module

Queries City of Hamilton Open Data via ArcGIS REST services for:
- Zoning by-law designations (By-law 05-200)
- Urban Hamilton Official Plan land use designations
- Secondary Plan areas
- Ward boundaries
- Neighbourhood boundaries

Hamilton uses ArcGIS Online for its Open Data platform.
"""

import time
from typing import Dict, Any, Optional, List

import httpx

from .base import BaseProvider, ProviderResult


class HamiltonArcGISProvider(BaseProvider):
    """
    Query Hamilton municipal data via ArcGIS REST services.

    Uses City of Hamilton Open Data Portal endpoints.
    """

    name = "Hamilton Open Data"
    base_url = "https://services5.arcgis.com/HLVgOJ5XDQjq6S9y/ArcGIS/rest/services"
    rate_limit = 2.0  # 2 requests per second
    cache_ttl = 86400 * 7  # 7 days

    # Layer endpoints (Hamilton Open Data)
    ZONING_URL = f"{base_url}/Zoning/FeatureServer/0/query"
    OFFICIAL_PLAN_URL = f"{base_url}/Urban_Land_Use_Designation/FeatureServer/0/query"
    SECONDARY_PLAN_URL = f"{base_url}/Secondary_Plan_Area/FeatureServer/0/query"
    WARDS_URL = f"{base_url}/Wards/FeatureServer/0/query"

    # Zoning category mappings for Hamilton By-law 05-200
    ZONE_CATEGORIES = {
        "R": "Residential",
        "D": "Downtown",
        "C": "Commercial",
        "I": "Industrial",
        "M": "Major Institutional",
        "P": "Parks and Open Space",
        "A": "Agricultural",
        "RU": "Rural",
        "E": "Environmental",
        "U": "Utilities",
    }

    async def query(
        self,
        lat: float,
        lon: float,
        radius_m: int = 50,
        **kwargs,
    ) -> ProviderResult:
        """
        Query Hamilton municipal data for location.

        Args:
            lat: Latitude (WGS84)
            lon: Longitude (WGS84)
            radius_m: Search radius (default 50m for point lookup)

        Returns:
            ProviderResult with zoning and planning data
        """
        start_time = time.time()
        warnings = []

        results = {
            "zoning_designation": None,
            "zoning_category": None,
            "permitted_uses": [],
            "official_plan_designation": None,
            "official_plan_policies": [],
            "secondary_plan": None,
            "secondary_plan_policies": [],
            "ward": None,
            "ward_name": None,
            "neighbourhood_name": None,
            "neighbourhood_id": None,
        }

        try:
            # Query all layers
            zoning_data = await self._query_zoning(lat, lon)
            op_data = await self._query_official_plan(lat, lon)
            secondary_data = await self._query_secondary_plan(lat, lon)
            ward_data = await self._query_ward(lat, lon)

            # Merge zoning results
            if zoning_data:
                results["zoning_designation"] = zoning_data.get("zone_code")
                results["zoning_category"] = zoning_data.get("zone_category")
                results["permitted_uses"] = zoning_data.get("permitted_uses", [])
                results["zoning_exception"] = zoning_data.get("exception")

            # Merge Official Plan results
            if op_data:
                results["official_plan_designation"] = op_data.get("designation")
                results["official_plan_policies"] = op_data.get("policies", [])

            # Merge Secondary Plan results
            if secondary_data:
                results["secondary_plan"] = secondary_data.get("plan_name")
                results["secondary_plan_policies"] = secondary_data.get("policies", [])

            # Merge ward results
            if ward_data:
                results["ward"] = ward_data.get("ward_number")
                results["ward_name"] = ward_data.get("ward_name")
                # Hamilton wards also serve as neighbourhood identification
                results["neighbourhood_name"] = ward_data.get("ward_name")

            response_time = (time.time() - start_time) * 1000

            return self._make_result(
                success=True,
                data=results,
                response_time_ms=response_time,
                warnings=warnings,
                metadata={
                    "source_url": "https://open.hamilton.ca",
                    "governing_bylaw": "05-200 (Hamilton)",
                },
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return self._make_result(
                success=False,
                error=str(e),
                response_time_ms=response_time,
            )

    async def _query_zoning(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Query Hamilton zoning layer."""
        try:
            params = {
                "geometry": f"{lon},{lat}",
                "geometryType": "esriGeometryPoint",
                "inSR": "4326",
                "spatialRel": "esriSpatialRelIntersects",
                "outFields": "*",
                "returnGeometry": "false",
                "f": "json",
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.ZONING_URL,
                    params=params,
                    timeout=15.0,
                    headers={"User-Agent": "LocationOverview/1.0"},
                )

                if response.status_code == 200:
                    data = response.json()
                    features = data.get("features", [])

                    if features:
                        attrs = features[0].get("attributes", {})
                        zone_code = (
                            attrs.get("ZONE_NAME")
                            or attrs.get("ZONE_CODE")
                            or attrs.get("ZONING")
                        )

                        return {
                            "zone_code": zone_code,
                            "zone_category": self._categorize_zone(zone_code),
                            "exception": attrs.get("EXCEPTION") or attrs.get("SITE_SPECIFIC"),
                            "permitted_uses": self._get_permitted_uses(zone_code),
                        }

        except Exception:
            pass

        return None

    async def _query_official_plan(
        self,
        lat: float,
        lon: float,
    ) -> Optional[Dict[str, Any]]:
        """Query Hamilton Urban Official Plan layer."""
        try:
            params = {
                "geometry": f"{lon},{lat}",
                "geometryType": "esriGeometryPoint",
                "inSR": "4326",
                "spatialRel": "esriSpatialRelIntersects",
                "outFields": "*",
                "returnGeometry": "false",
                "f": "json",
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.OFFICIAL_PLAN_URL,
                    params=params,
                    timeout=15.0,
                    headers={"User-Agent": "LocationOverview/1.0"},
                )

                if response.status_code == 200:
                    data = response.json()
                    features = data.get("features", [])

                    if features:
                        attrs = features[0].get("attributes", {})
                        designation = (
                            attrs.get("LAND_USE")
                            or attrs.get("DESIGNATION")
                            or attrs.get("SCHEDULE_B")
                        )

                        return {
                            "designation": designation,
                            "policies": self._get_op_policies(designation),
                        }

        except Exception:
            pass

        return None

    async def _query_secondary_plan(
        self,
        lat: float,
        lon: float,
    ) -> Optional[Dict[str, Any]]:
        """Query Hamilton Secondary Plan layer."""
        try:
            params = {
                "geometry": f"{lon},{lat}",
                "geometryType": "esriGeometryPoint",
                "inSR": "4326",
                "spatialRel": "esriSpatialRelIntersects",
                "outFields": "*",
                "returnGeometry": "false",
                "f": "json",
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.SECONDARY_PLAN_URL,
                    params=params,
                    timeout=15.0,
                    headers={"User-Agent": "LocationOverview/1.0"},
                )

                if response.status_code == 200:
                    data = response.json()
                    features = data.get("features", [])

                    if features:
                        attrs = features[0].get("attributes", {})
                        plan_name = attrs.get("NAME") or attrs.get("PLAN_NAME")

                        return {
                            "plan_name": plan_name,
                            "plan_number": attrs.get("SEC_PLAN_NO"),
                            "policies": [],  # Would require document extraction
                        }

        except Exception:
            pass

        return None

    async def _query_ward(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Query Hamilton ward boundaries."""
        try:
            params = {
                "geometry": f"{lon},{lat}",
                "geometryType": "esriGeometryPoint",
                "inSR": "4326",
                "spatialRel": "esriSpatialRelIntersects",
                "outFields": "*",
                "returnGeometry": "false",
                "f": "json",
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.WARDS_URL,
                    params=params,
                    timeout=15.0,
                    headers={"User-Agent": "LocationOverview/1.0"},
                )

                if response.status_code == 200:
                    data = response.json()
                    features = data.get("features", [])

                    if features:
                        attrs = features[0].get("attributes", {})
                        return {
                            "ward_number": attrs.get("WARD") or attrs.get("WARD_NUM"),
                            "ward_name": attrs.get("WARD_NAME") or attrs.get("NAME"),
                        }

        except Exception:
            pass

        return None

    def _categorize_zone(self, zone_code: Optional[str]) -> str:
        """Map zone code to category."""
        if not zone_code:
            return "Unknown"

        # Extract base zone from code (e.g., "R1" -> "R", "C2" -> "C")
        base = ""
        for char in zone_code.upper():
            if char.isalpha():
                base += char
            else:
                break

        return self.ZONE_CATEGORIES.get(base, "Mixed Use")

    def _get_permitted_uses(self, zone_code: Optional[str]) -> List[str]:
        """Get permitted uses for zone code."""
        if not zone_code:
            return []

        category = self._categorize_zone(zone_code)

        # Common permitted uses by category for Hamilton
        uses_by_category = {
            "Residential": ["Single-detached dwelling", "Home occupation", "Bed and breakfast"],
            "Downtown": [
                "Mixed-use building",
                "Office",
                "Retail",
                "Residential",
                "Entertainment",
            ],
            "Commercial": [
                "Retail store",
                "Office",
                "Restaurant",
                "Personal service establishment",
            ],
            "Industrial": [
                "Manufacturing",
                "Warehouse",
                "Distribution centre",
                "Salvage yard",
            ],
            "Major Institutional": [
                "Hospital",
                "University",
                "Government office",
                "Cultural facility",
            ],
            "Parks and Open Space": ["Park", "Recreation facility", "Community garden"],
            "Agricultural": ["Farm", "Agricultural operation", "Farm-related commercial"],
            "Rural": ["Rural residential", "Farm", "Agri-tourism"],
        }

        return uses_by_category.get(category, ["See zoning by-law for permitted uses"])

    def _get_op_policies(self, designation: Optional[str]) -> List[str]:
        """Get Official Plan policies for designation."""
        if not designation:
            return []

        designation_lower = designation.lower() if designation else ""

        if "residential" in designation_lower:
            return [
                "Protect stable residential neighbourhoods",
                "Direct intensification to nodes and corridors",
                "Support complete communities",
            ]
        elif "employment" in designation_lower or "industrial" in designation_lower:
            return [
                "Protect employment lands from conversion",
                "Support economic development and job creation",
            ]
        elif "commercial" in designation_lower:
            return [
                "Support commercial development serving local needs",
                "Encourage transit-supportive development",
            ]
        elif "downtown" in designation_lower:
            return [
                "Revitalize downtown Hamilton",
                "Encourage mixed-use high-density development",
                "Support transit-oriented development",
            ]
        elif "institutional" in designation_lower:
            return [
                "Support major institutional uses",
                "Encourage integration with surrounding areas",
            ]

        return []

    def is_applicable(self, municipality: str) -> bool:
        """
        Check if this provider is applicable for the municipality.

        Args:
            municipality: Municipality name

        Returns:
            True for Hamilton
        """
        return municipality.lower() in [
            "hamilton",
            "city of hamilton",
        ]
