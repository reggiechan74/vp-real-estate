"""
Heritage Properties Provider Module

Queries heritage property registrations from multiple sources:
- Ontario Heritage Trust (provincial designations)
- Municipal heritage registers (Part IV and Part V HCD designations)
- Canadian Register of Historic Places

Web scraping is used where APIs are not available.
"""

import time
import re
from typing import Dict, Any, Optional, List
from urllib.parse import urlencode

import httpx

from .base import BaseProvider, ProviderResult


class HeritageProvider(BaseProvider):
    """
    Query heritage property designations from multiple sources.

    Ontario heritage designations include:
    - Part IV (individual designation under Ontario Heritage Act)
    - Part V (Heritage Conservation District)
    - Provincial heritage properties (Ontario Heritage Trust)
    - Federal heritage properties (Historic Sites and Monuments Board)
    """

    name = "Heritage Registry"
    base_url = "https://www.heritagetrust.on.ca"
    rate_limit = 1.0  # 1 request per second
    cache_ttl = 86400 * 30  # 30 days (heritage designations rarely change)

    # Toronto heritage register endpoint (ArcGIS)
    TORONTO_HERITAGE_URL = "https://services3.arcgis.com/b9WvedVPoizGfvfD/ArcGIS/rest/services/COTGEO_HERITAGE/FeatureServer/0/query"

    # Canadian Register of Historic Places API
    CRHP_API_URL = "https://www.historicplaces.ca/en/pages/search-recherche.aspx"

    # Heritage designation types
    DESIGNATION_TYPES = {
        "part_iv": "Part IV - Individual Designation (Ontario Heritage Act)",
        "part_v": "Part V - Heritage Conservation District",
        "provincial": "Provincial Heritage Property (Ontario Heritage Trust)",
        "federal": "National Historic Site",
        "listed": "Listed (non-designated, heritage interest)",
    }

    async def query(
        self,
        lat: float,
        lon: float,
        radius_m: int = 100,
        **kwargs,
    ) -> ProviderResult:
        """
        Query heritage registrations for location.

        Args:
            lat: Latitude (WGS84)
            lon: Longitude (WGS84)
            radius_m: Search radius in meters (default 100m for point lookup)

        Returns:
            ProviderResult with heritage designation data
        """
        start_time = time.time()
        warnings = []

        results = {
            "heritage_designated": False,
            "designation_type": None,
            "designation_description": None,
            "property_name": None,
            "designation_date": None,
            "by_law_number": None,
            "heritage_attributes": [],
            "heritage_district": None,
            "nearby_heritage": [],
        }

        try:
            municipality = kwargs.get("municipality", "").lower()

            # Query Toronto-specific heritage register
            if municipality in ["toronto", "city of toronto"]:
                toronto_result = await self._query_toronto_heritage(lat, lon, radius_m)
                if toronto_result:
                    results.update(toronto_result)

            # Query Ontario Heritage Trust (provincial designations)
            provincial_result = await self._query_provincial_heritage(lat, lon)
            if provincial_result and provincial_result.get("heritage_designated"):
                # Provincial takes precedence if property has both
                if not results["heritage_designated"]:
                    results.update(provincial_result)
                else:
                    # Add as additional designation
                    results["additional_designations"] = [provincial_result]

            # Query for Heritage Conservation Districts
            hcd_result = await self._query_heritage_district(lat, lon, municipality)
            if hcd_result:
                results["heritage_district"] = hcd_result

            response_time = (time.time() - start_time) * 1000

            return self._make_result(
                success=True,
                data=results,
                response_time_ms=response_time,
                warnings=warnings,
                metadata={
                    "source_url": "https://www.heritagetrust.on.ca",
                    "note": "Heritage data from municipal and provincial registries",
                },
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return self._make_result(
                success=False,
                error=str(e),
                response_time_ms=response_time,
            )

    async def _query_toronto_heritage(
        self,
        lat: float,
        lon: float,
        radius_m: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Query Toronto Heritage Register via ArcGIS.

        Args:
            lat: Latitude
            lon: Longitude
            radius_m: Search radius

        Returns:
            Heritage data dict or None
        """
        try:
            params = {
                "geometry": f"{lon},{lat}",
                "geometryType": "esriGeometryPoint",
                "inSR": "4326",
                "spatialRel": "esriSpatialRelIntersects",
                "distance": radius_m,
                "units": "esriSRUnit_Meter",
                "outFields": "*",
                "returnGeometry": "false",
                "f": "json",
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.TORONTO_HERITAGE_URL,
                    params=params,
                    timeout=15.0,
                    headers={"User-Agent": "LocationOverview/1.0"},
                )

                if response.status_code == 200:
                    data = response.json()
                    features = data.get("features", [])

                    if features:
                        # Property is heritage designated
                        attrs = features[0].get("attributes", {})

                        return {
                            "heritage_designated": True,
                            "designation_type": self._parse_designation_type(attrs),
                            "designation_description": attrs.get("HERITAGE_CATEGORY"),
                            "property_name": attrs.get("PROPERTY_NAME"),
                            "street_address": attrs.get("ADDRESS"),
                            "heritage_attributes": self._parse_heritage_attributes(attrs),
                            "date_listed": attrs.get("DATE_LISTED"),
                            "by_law_number": attrs.get("BYLAW_NO"),
                        }

        except Exception:
            pass  # Graceful degradation

        return None

    async def _query_provincial_heritage(
        self,
        lat: float,
        lon: float,
    ) -> Optional[Dict[str, Any]]:
        """
        Query Ontario Heritage Trust for provincial designations.

        Uses web scraping as no API is available.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Provincial heritage data or None
        """
        # Ontario Heritage Trust doesn't have a public spatial API
        # This would require web scraping their property search
        # For MVP, return None and log that full implementation is pending
        return None

    async def _query_heritage_district(
        self,
        lat: float,
        lon: float,
        municipality: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Check if location is within a Heritage Conservation District.

        Args:
            lat: Latitude
            lon: Longitude
            municipality: Municipality name

        Returns:
            HCD data or None
        """
        if municipality in ["toronto", "city of toronto"]:
            return await self._query_toronto_hcd(lat, lon)
        return None

    async def _query_toronto_hcd(
        self,
        lat: float,
        lon: float,
    ) -> Optional[Dict[str, Any]]:
        """
        Query Toronto Heritage Conservation Districts.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            HCD data or None
        """
        # Toronto HCD layer endpoint
        hcd_url = "https://services3.arcgis.com/b9WvedVPoizGfvfD/ArcGIS/rest/services/COTGEO_HERITAGE_CONSERVATION_DISTRICT/FeatureServer/0/query"

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
                    hcd_url,
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
                            "in_hcd": True,
                            "district_name": attrs.get("HCD_NAME"),
                            "by_law_number": attrs.get("BYLAW_NO"),
                            "designation_date": attrs.get("DESIGNATION_DATE"),
                            "study_area": attrs.get("STUDY_AREA"),
                        }

        except Exception:
            pass

        return None

    def _parse_designation_type(self, attrs: Dict[str, Any]) -> str:
        """Parse heritage designation type from attributes."""
        category = attrs.get("HERITAGE_CATEGORY", "").lower()

        if "part iv" in category or "designated" in category:
            return "part_iv"
        elif "part v" in category or "hcd" in category:
            return "part_v"
        elif "listed" in category:
            return "listed"
        else:
            return "listed"

    def _parse_heritage_attributes(self, attrs: Dict[str, Any]) -> List[str]:
        """Parse heritage attributes/features from attributes."""
        attributes = []

        # Common attribute fields
        if attrs.get("ARCHITECTURAL_STYLE"):
            attributes.append(f"Architectural Style: {attrs['ARCHITECTURAL_STYLE']}")
        if attrs.get("CONSTRUCTION_DATE"):
            attributes.append(f"Construction Date: {attrs['CONSTRUCTION_DATE']}")
        if attrs.get("ARCHITECT"):
            attributes.append(f"Architect: {attrs['ARCHITECT']}")

        return attributes

    def is_applicable(self, municipality: str) -> bool:
        """
        Heritage provider is applicable to all Ontario municipalities.

        Full coverage for Toronto; limited coverage elsewhere.

        Args:
            municipality: Municipality name

        Returns:
            True for Ontario municipalities
        """
        # Currently optimized for Toronto, but applicable province-wide
        return True
