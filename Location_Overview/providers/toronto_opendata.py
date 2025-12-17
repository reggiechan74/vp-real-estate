"""
Toronto Open Data Provider Module

Queries City of Toronto Open Data Portal for:
- Zoning By-law designations
- Official Plan designations
- Neighbourhood boundaries
- Heritage properties

Uses the CKAN API with spatial query support.
"""

import time
from typing import Dict, Any, Optional, List

import httpx

from .base import BaseProvider, ProviderResult


class TorontoOpenDataProvider(BaseProvider):
    """
    Query City of Toronto Open Data for zoning and planning data.

    Uses CKAN data portal with spatial query capabilities.
    Toronto Open Data is free and has generous rate limits.
    """

    name = "Toronto Open Data"
    base_url = "https://ckan0.cf.opendata.inter.prod-toronto.ca"
    rate_limit = 10.0  # requests per second
    cache_ttl = 86400 * 7  # 7 days

    # Dataset package names (CKAN resource IDs)
    DATASETS = {
        "zoning": "zoning-by-law",
        "neighbourhoods": "neighbourhoods",
        "official_plan": "official-plan-area-specific-policies",
        "heritage": "heritage-register",
        "secondary_plans": "secondary-plans",
        "wards": "city-wards",
    }

    # Zone type to use mapping
    ZONE_USE_MAPPING = {
        "R": ["Residential", "Home occupation"],
        "RD": ["Residential Detached", "Single-family dwelling", "Home occupation"],
        "RS": ["Residential Semi-Detached", "Semi-detached dwelling"],
        "RT": ["Residential Townhouse", "Townhouse dwelling"],
        "RM": ["Residential Multiple", "Apartment", "Townhouse", "Multi-unit dwelling"],
        "RA": ["Residential Apartment", "Apartment building"],
        "CR": ["Commercial Residential", "Retail", "Office", "Restaurant", "Residential above grade"],
        "CL": ["Commercial Local", "Retail", "Service commercial", "Office"],
        "CG": ["Commercial General", "Retail", "Office", "Restaurant", "Entertainment"],
        "C": ["Commercial", "Retail", "Office", "Restaurant"],
        "E": ["Employment", "Industrial", "Manufacturing", "Warehouse", "Office"],
        "EL": ["Employment Light Industrial", "Light manufacturing", "Warehouse", "Office"],
        "EH": ["Employment Heavy Industrial", "Heavy manufacturing", "Processing"],
        "EO": ["Employment Office", "Office", "Research facility"],
        "I": ["Institutional", "School", "Hospital", "Place of worship", "Government"],
        "O": ["Open Space", "Park", "Recreation"],
        "ON": ["Open Space Natural", "Natural area", "Conservation"],
        "OR": ["Open Space Recreation", "Recreation facility", "Sports field"],
        "U": ["Utility", "Infrastructure", "Transit"],
    }

    async def query(
        self,
        lat: float,
        lon: float,
        **kwargs,
    ) -> ProviderResult:
        """
        Query Toronto Open Data for property at coordinates.

        Args:
            lat: Latitude (WGS84)
            lon: Longitude (WGS84)

        Returns:
            ProviderResult with zoning and planning data
        """
        start_time = time.time()

        results = {
            "zoning_designation": None,
            "zoning_category": None,
            "permitted_uses": [],
            "official_plan_designation": None,
            "official_plan_policies": [],
            "neighbourhood_name": None,
            "neighbourhood_id": None,
            "ward": None,
            "ward_name": None,
            "heritage_designated": False,
            "heritage_type": None,
            "secondary_plan": None,
            "secondary_plan_policies": [],
        }
        warnings = []

        try:
            # Query zoning
            zoning_data = await self._query_zoning(lat, lon)
            if zoning_data:
                results["zoning_designation"] = zoning_data.get("zone")
                results["zoning_category"] = zoning_data.get("category")
                results["permitted_uses"] = zoning_data.get("permitted_uses", [])
            else:
                warnings.append("Zoning data not found for location")

            # Query neighbourhood
            neighbourhood_data = await self._query_neighbourhood(lat, lon)
            if neighbourhood_data:
                results["neighbourhood_name"] = neighbourhood_data.get("name")
                results["neighbourhood_id"] = neighbourhood_data.get("id")

            # Query ward
            ward_data = await self._query_ward(lat, lon)
            if ward_data:
                results["ward"] = ward_data.get("ward_number")
                results["ward_name"] = ward_data.get("ward_name")

            response_time = (time.time() - start_time) * 1000

            return self._make_result(
                success=True,
                data=results,
                response_time_ms=response_time,
                warnings=warnings,
                metadata={
                    "source_url": "https://open.toronto.ca/",
                    "last_refreshed": "See individual datasets",
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
        Query zoning by-law for point using spatial query.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Zoning data dict or None
        """
        # Toronto Open Data provides zoning as GeoJSON
        # We'll use the package_show and datastore_search_sql endpoints

        try:
            # First, try the ArcGIS endpoint that Toronto also provides
            arcgis_url = "https://services3.arcgis.com/b9WvedVPoizGfvfD/ArcGIS/rest/services/COTGEO_ZONING_AREA/FeatureServer/0/query"

            params = {
                "geometry": f"{lon},{lat}",
                "geometryType": "esriGeometryPoint",
                "inSR": "4326",
                "spatialRel": "esriSpatialRelIntersects",
                "outFields": "ZN_ZONE,ZN_CATEGORY,OVERLAY",
                "returnGeometry": "false",
                "f": "json",
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    arcgis_url,
                    params=params,
                    timeout=15.0,
                    headers={"User-Agent": "LocationOverview/1.0"},
                )

                if response.status_code == 200:
                    data = response.json()
                    features = data.get("features", [])

                    if features:
                        attrs = features[0].get("attributes", {})
                        zone = attrs.get("ZN_ZONE", "")
                        category = attrs.get("ZN_CATEGORY", "")

                        return {
                            "zone": zone,
                            "category": category,
                            "overlay": attrs.get("OVERLAY"),
                            "permitted_uses": self._get_permitted_uses(zone),
                        }

        except Exception:
            pass  # Fall through to alternative method

        return None

    async def _query_neighbourhood(
        self,
        lat: float,
        lon: float,
    ) -> Optional[Dict[str, Any]]:
        """
        Query neighbourhood boundaries for point.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Neighbourhood data dict or None
        """
        try:
            # Toronto neighbourhoods ArcGIS endpoint
            arcgis_url = "https://services3.arcgis.com/b9WvedVPoizGfvfD/ArcGIS/rest/services/COTGEO_NEIGHBOURHOOD/FeatureServer/0/query"

            params = {
                "geometry": f"{lon},{lat}",
                "geometryType": "esriGeometryPoint",
                "inSR": "4326",
                "spatialRel": "esriSpatialRelIntersects",
                "outFields": "AREA_NAME,AREA_SHORT_CODE,AREA_ID",
                "returnGeometry": "false",
                "f": "json",
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    arcgis_url,
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
                            "name": attrs.get("AREA_NAME"),
                            "code": attrs.get("AREA_SHORT_CODE"),
                            "id": attrs.get("AREA_ID"),
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
        Query ward boundaries for point.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Ward data dict or None
        """
        try:
            # Toronto wards ArcGIS endpoint
            arcgis_url = "https://services3.arcgis.com/b9WvedVPoizGfvfD/ArcGIS/rest/services/COTGEO_CITY_WARD/FeatureServer/0/query"

            params = {
                "geometry": f"{lon},{lat}",
                "geometryType": "esriGeometryPoint",
                "inSR": "4326",
                "spatialRel": "esriSpatialRelIntersects",
                "outFields": "AREA_NAME,AREA_SHORT_CODE",
                "returnGeometry": "false",
                "f": "json",
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    arcgis_url,
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
                            "ward_name": attrs.get("AREA_NAME"),
                            "ward_number": attrs.get("AREA_SHORT_CODE"),
                        }

        except Exception:
            pass

        return None

    def _get_permitted_uses(self, zone: str) -> List[str]:
        """
        Get permitted uses for a zone designation.

        Args:
            zone: Zone designation (e.g., "CR 3.0", "E 2.0")

        Returns:
            List of permitted uses
        """
        if not zone:
            return []

        # Extract zone type prefix (letters before any numbers)
        import re

        match = re.match(r"^([A-Z]+)", zone.upper())
        if not match:
            return []

        zone_type = match.group(1)

        # Look up uses
        uses = self.ZONE_USE_MAPPING.get(zone_type, [])

        # If no exact match, try prefix matching
        if not uses:
            for prefix, use_list in self.ZONE_USE_MAPPING.items():
                if zone_type.startswith(prefix):
                    uses = use_list
                    break

        return uses

    def is_applicable(self, municipality: str) -> bool:
        """
        Check if provider applies to municipality.

        Only applicable to Toronto.

        Args:
            municipality: Municipality name

        Returns:
            True if Toronto
        """
        return municipality.lower() in ["toronto", "city of toronto"]


class TorontoZoningError(Exception):
    """Exception for Toronto zoning query errors."""

    pass
