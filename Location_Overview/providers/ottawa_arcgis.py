"""
Ottawa ArcGIS Provider Module

Queries City of Ottawa Open Data for:
- Zoning designations
- Official Plan designations
- Secondary plans
- Ward and neighbourhood boundaries

Ottawa uses ArcGIS Online and CKAN for open data.
"""

import time
import re
from typing import Dict, Any, Optional, List

import httpx

from .base import BaseProvider, ProviderResult


class OttawaArcGISProvider(BaseProvider):
    """
    Query City of Ottawa Open Data for zoning and planning data.

    Uses Ottawa's ArcGIS REST services for spatial queries.
    """

    name = "Ottawa Open Data"
    base_url = "https://maps.ottawa.ca/arcgis/rest/services"
    rate_limit = 5.0  # requests per second
    cache_ttl = 86400 * 7  # 7 days

    # ArcGIS service endpoints
    ZONING_URL = "https://maps.ottawa.ca/arcgis/rest/services/Zoning/MapServer/0/query"
    OFFICIAL_PLAN_URL = "https://maps.ottawa.ca/arcgis/rest/services/Official_Plan/MapServer/0/query"
    WARDS_URL = "https://maps.ottawa.ca/arcgis/rest/services/Wards/MapServer/0/query"
    NEIGHBOURHOODS_URL = "https://maps.ottawa.ca/arcgis/rest/services/Neighbourhoods/MapServer/0/query"

    # Ottawa zoning to use mapping
    ZONE_USE_MAPPING = {
        "R1": ["Residential Detached", "Single detached dwelling"],
        "R2": ["Residential Detached", "Single detached", "Semi-detached"],
        "R3": ["Residential Multiple", "Duplex", "Triplex", "Fourplex"],
        "R4": ["Residential Multiple", "Low-rise apartment", "Townhouse"],
        "R5": ["Residential Apartment", "Apartment building"],
        "RM": ["Mixed Use", "Residential", "Small-scale commercial"],
        "GM": ["General Mixed Use", "Retail", "Office", "Residential"],
        "TM": ["Traditional Mainstreet", "Retail", "Office", "Residential"],
        "AM": ["Arterial Mainstreet", "Commercial", "Residential"],
        "MC": ["Mixed Use Centre", "High-density", "Retail", "Office", "Residential"],
        "MD": ["Mixed Use Downtown", "High-density", "Commercial", "Residential"],
        "LC": ["Local Commercial", "Retail", "Service commercial"],
        "GM": ["General Mixed Use", "Commercial", "Residential"],
        "IL": ["Light Industrial", "Light manufacturing", "Warehouse"],
        "IH": ["Heavy Industrial", "Heavy manufacturing", "Processing"],
        "IP": ["Industrial Park", "Office", "Light industrial"],
        "I1": ["Minor Institutional", "School", "Place of worship"],
        "I2": ["Major Institutional", "Hospital", "College", "Government"],
        "O1": ["Parks and Open Space", "Park", "Recreation"],
        "EP": ["Environmental Protection", "Conservation"],
        "AG": ["Agricultural", "Farming", "Agricultural uses"],
        "RU": ["Rural Countryside", "Rural residential", "Agriculture"],
        "VM": ["Village Mixed Use", "Village commercial", "Residential"],
        "V1": ["Village Residential First Density"],
        "V2": ["Village Residential Second Density"],
        "V3": ["Village Residential Third Density"],
    }

    async def query(
        self,
        lat: float,
        lon: float,
        **kwargs,
    ) -> ProviderResult:
        """
        Query Ottawa Open Data for property at coordinates.

        Args:
            lat: Latitude (WGS84)
            lon: Longitude (WGS84)

        Returns:
            ProviderResult with zoning and planning data
        """
        start_time = time.time()
        warnings = []

        results = {
            "zoning_designation": None,
            "zoning_category": None,
            "zoning_exception": None,
            "permitted_uses": [],
            "official_plan_designation": None,
            "official_plan_policies": [],
            "secondary_plan": None,
            "secondary_plan_area": None,
            "neighbourhood_name": None,
            "neighbourhood_id": None,
            "ward": None,
            "ward_name": None,
            "councillor": None,
        }

        try:
            # Query zoning
            zoning_data = await self._query_zoning(lat, lon)
            if zoning_data:
                results["zoning_designation"] = zoning_data.get("zone")
                results["zoning_category"] = zoning_data.get("category")
                results["zoning_exception"] = zoning_data.get("exception")
                results["permitted_uses"] = zoning_data.get("permitted_uses", [])
            else:
                warnings.append("Zoning data not found for location")

            # Query Official Plan
            op_data = await self._query_official_plan(lat, lon)
            if op_data:
                results["official_plan_designation"] = op_data.get("designation")
                results["official_plan_policies"] = op_data.get("policies", [])
                results["secondary_plan"] = op_data.get("secondary_plan")
                results["secondary_plan_area"] = op_data.get("secondary_plan_area")

            # Query ward
            ward_data = await self._query_ward(lat, lon)
            if ward_data:
                results["ward"] = ward_data.get("ward_number")
                results["ward_name"] = ward_data.get("ward_name")
                results["councillor"] = ward_data.get("councillor")

            # Query neighbourhood
            neighbourhood_data = await self._query_neighbourhood(lat, lon)
            if neighbourhood_data:
                results["neighbourhood_name"] = neighbourhood_data.get("name")
                results["neighbourhood_id"] = neighbourhood_data.get("id")

            response_time = (time.time() - start_time) * 1000

            return self._make_result(
                success=True,
                data=results,
                response_time_ms=response_time,
                warnings=warnings,
                metadata={
                    "source_url": "https://open.ottawa.ca/",
                    "by_law": "City of Ottawa Zoning By-law 2008-250",
                },
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return self._make_result(
                success=False,
                error=str(e),
                response_time_ms=response_time,
            )

    async def _query_zoning(
        self,
        lat: float,
        lon: float,
    ) -> Optional[Dict[str, Any]]:
        """
        Query Ottawa zoning by-law for point.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Zoning data dict or None
        """
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

                        # Parse zone code
                        zone_code = attrs.get("ZONE_CODE") or attrs.get("ZONE")
                        exception = attrs.get("EXCEPTION_NUMBER") or attrs.get("EXCEPTION")

                        return {
                            "zone": zone_code,
                            "category": self._get_zone_category(zone_code),
                            "exception": exception if exception else None,
                            "permitted_uses": self._get_permitted_uses(zone_code),
                            "subzone": attrs.get("SUBZONE"),
                            "suffix": attrs.get("SUFFIX"),
                        }

        except Exception:
            pass

        return None

    async def _query_official_plan(
        self,
        lat: float,
        lon: float,
    ) -> Optional[Dict[str, Any]]:
        """
        Query Ottawa Official Plan designation.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Official Plan data or None
        """
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

                        return {
                            "designation": attrs.get("DESIGNATION") or attrs.get("OP_DESIGNATION"),
                            "secondary_plan": attrs.get("SECONDARY_PLAN"),
                            "secondary_plan_area": attrs.get("SECONDARY_PLAN_AREA"),
                            "policies": [],
                        }

        except Exception:
            pass

        return None

    async def _query_ward(
        self,
        lat: float,
        lon: float,
    ) -> Optional[Dict[str, Any]]:
        """
        Query Ottawa ward boundaries.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Ward data or None
        """
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
                            "ward_number": attrs.get("WARD_NUM") or attrs.get("WARD_NUMBER"),
                            "ward_name": attrs.get("WARD_NAME_EN") or attrs.get("WARD_NAME"),
                            "councillor": attrs.get("COUNCILLOR"),
                        }

        except Exception:
            pass

        return None

    async def _query_neighbourhood(
        self,
        lat: float,
        lon: float,
    ) -> Optional[Dict[str, Any]]:
        """
        Query Ottawa neighbourhood boundaries.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Neighbourhood data or None
        """
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
                    self.NEIGHBOURHOODS_URL,
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
                            "name": attrs.get("NAME_EN") or attrs.get("NAME"),
                            "id": attrs.get("ONS_ID") or attrs.get("NEIGHBOURHOOD_ID"),
                        }

        except Exception:
            pass

        return None

    def _get_zone_category(self, zone_code: str) -> str:
        """
        Get zone category from zone code.

        Args:
            zone_code: Ottawa zone code

        Returns:
            Zone category description
        """
        if not zone_code:
            return "Unknown"

        zone_prefix = re.match(r"^([A-Z]+)", zone_code.upper())
        if not zone_prefix:
            return "Unknown"

        prefix = zone_prefix.group(1)

        category_map = {
            "R": "Residential",
            "RM": "Residential Mixed",
            "GM": "General Mixed Use",
            "TM": "Traditional Mainstreet",
            "AM": "Arterial Mainstreet",
            "MC": "Mixed Use Centre",
            "MD": "Mixed Use Downtown",
            "LC": "Local Commercial",
            "IL": "Light Industrial",
            "IH": "Heavy Industrial",
            "IP": "Industrial Park",
            "I": "Institutional",
            "O": "Open Space",
            "EP": "Environmental Protection",
            "AG": "Agricultural",
            "RU": "Rural",
            "VM": "Village Mixed Use",
            "V": "Village Residential",
        }

        return category_map.get(prefix, "Mixed Use")

    def _get_permitted_uses(self, zone_code: str) -> List[str]:
        """
        Get permitted uses for Ottawa zone.

        Args:
            zone_code: Ottawa zone code

        Returns:
            List of permitted uses
        """
        if not zone_code:
            return []

        zone_prefix = re.match(r"^([A-Z]+\d?)", zone_code.upper())
        if not zone_prefix:
            return []

        prefix = zone_prefix.group(1)

        # Try exact match first, then prefix
        uses = self.ZONE_USE_MAPPING.get(prefix, [])

        if not uses:
            # Try first two characters
            prefix_short = prefix[:2]
            uses = self.ZONE_USE_MAPPING.get(prefix_short, [])

        return uses

    def is_applicable(self, municipality: str) -> bool:
        """
        Check if provider applies to municipality.

        Only applicable to Ottawa.

        Args:
            municipality: Municipality name

        Returns:
            True if Ottawa
        """
        return municipality.lower() in ["ottawa", "city of ottawa"]
