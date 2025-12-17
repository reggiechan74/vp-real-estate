"""
TRCA (Toronto and Region Conservation Authority) Provider Module

Queries conservation authority data for:
- Regulated areas (floodplains, wetlands, valleys)
- Development permit requirements
- Natural hazards (erosion, slope stability)
- Natural heritage features

Conservation Authority jurisdiction varies by watershed:
- TRCA: Toronto, parts of York, Peel, Durham
- CVC: Credit Valley (Mississauga, Brampton, Caledon)
- LSRCA: Lake Simcoe Region
- CLOCA: Central Lake Ontario
"""

import time
from typing import Dict, Any, Optional, List

import httpx

from .base import BaseProvider, ProviderResult


class TRCAProvider(BaseProvider):
    """
    Query Toronto and Region Conservation Authority for regulated areas.

    TRCA regulates development within:
    - Floodplains (Regulatory Flood Standard)
    - Wetlands and watercourses
    - Valley and stream corridors
    - Lake Ontario shoreline
    - Areas of natural hazard

    Development in regulated areas requires a permit under O.Reg. 166/06.
    """

    name = "TRCA Conservation"
    base_url = "https://trca.ca"
    rate_limit = 2.0  # requests per second
    cache_ttl = 86400 * 30  # 30 days (regulated areas rarely change)

    # TRCA GIS Services
    TRCA_ARCGIS_URL = "https://services1.arcgis.com/eFVV1UwCgvUdT8Px/ArcGIS/rest/services"

    # Conservation Authority boundaries (approximate, by municipality)
    CA_JURISDICTION = {
        "trca": ["toronto", "markham", "vaughan", "richmond hill", "ajax", "pickering"],
        "cvc": ["mississauga", "brampton", "caledon", "orangeville"],
        "lsrca": ["newmarket", "aurora", "east gwillimbury", "georgina"],
        "cloca": ["whitby", "oshawa", "clarington"],
        "hrca": ["hamilton", "burlington", "grimsby"],
    }

    # Layer IDs for different regulated features
    LAYERS = {
        "regulated_area": "TRCA_Regulation_Limit",
        "floodplain": "TRCA_Flood_Hazard",
        "erosion": "TRCA_Erosion_Hazard",
        "watercourse": "TRCA_Watercourse",
        "wetland": "TRCA_Wetland",
    }

    async def query(
        self,
        lat: float,
        lon: float,
        **kwargs,
    ) -> ProviderResult:
        """
        Query conservation authority regulated areas for location.

        Args:
            lat: Latitude (WGS84)
            lon: Longitude (WGS84)

        Returns:
            ProviderResult with regulated area data
        """
        start_time = time.time()
        warnings = []

        results = {
            "in_regulated_area": False,
            "conservation_authority": None,
            "permit_required": False,
            "floodplain": False,
            "floodplain_type": None,
            "flood_fringe": False,
            "flood_special_policy": False,
            "erosion_hazard": False,
            "wetland": False,
            "wetland_type": None,
            "valley_corridor": False,
            "watercourse_setback": None,
            "natural_heritage": False,
            "regulatory_notes": [],
        }

        try:
            municipality = kwargs.get("municipality", "").lower()

            # Determine which conservation authority has jurisdiction
            ca = self._get_conservation_authority(municipality)
            results["conservation_authority"] = ca

            if ca == "trca":
                # Query TRCA regulated areas
                trca_result = await self._query_trca_regulated(lat, lon)
                if trca_result:
                    results.update(trca_result)

                # Query TRCA flood hazard
                flood_result = await self._query_trca_flood(lat, lon)
                if flood_result:
                    results.update(flood_result)

                # Query TRCA wetlands
                wetland_result = await self._query_trca_wetland(lat, lon)
                if wetland_result:
                    results.update(wetland_result)

            elif ca == "cvc":
                # Query Credit Valley Conservation
                cvc_result = await self._query_cvc_regulated(lat, lon)
                if cvc_result:
                    results.update(cvc_result)

            else:
                # For other CAs, query Ontario-wide natural heritage layers
                provincial_result = await self._query_provincial_natural_heritage(lat, lon)
                if provincial_result:
                    results.update(provincial_result)

            # Set permit required flag
            results["permit_required"] = (
                results["in_regulated_area"] or
                results["floodplain"] or
                results["wetland"] or
                results["erosion_hazard"]
            )

            # Add regulatory notes
            if results["permit_required"]:
                results["regulatory_notes"].append(
                    f"Development permit may be required from {ca.upper() if ca else 'Conservation Authority'}"
                )
            if results["floodplain"]:
                results["regulatory_notes"].append(
                    "Property in floodplain - verify flood insurance availability"
                )
            if results["wetland"]:
                results["regulatory_notes"].append(
                    "Wetland on or adjacent to property - environmental assessment required"
                )

            response_time = (time.time() - start_time) * 1000

            return self._make_result(
                success=True,
                data=results,
                response_time_ms=response_time,
                warnings=warnings,
                metadata={
                    "conservation_authority": ca,
                    "source": f"{'TRCA' if ca == 'trca' else 'Conservation Authority'} GIS",
                    "note": "Development in regulated areas requires permit under O.Reg. 166/06",
                },
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return self._make_result(
                success=False,
                error=str(e),
                response_time_ms=response_time,
            )

    async def _query_trca_regulated(
        self,
        lat: float,
        lon: float,
    ) -> Optional[Dict[str, Any]]:
        """
        Query TRCA Regulation Limit layer.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Regulated area data or None
        """
        url = f"{self.TRCA_ARCGIS_URL}/TRCA_Regulation_Limit/FeatureServer/0/query"

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
                    url,
                    params=params,
                    timeout=15.0,
                    headers={"User-Agent": "LocationOverview/1.0"},
                )

                if response.status_code == 200:
                    data = response.json()
                    features = data.get("features", [])

                    if features:
                        return {
                            "in_regulated_area": True,
                            "valley_corridor": True,
                        }

        except Exception:
            pass

        return None

    async def _query_trca_flood(
        self,
        lat: float,
        lon: float,
    ) -> Optional[Dict[str, Any]]:
        """
        Query TRCA Flood Hazard layer.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Flood hazard data or None
        """
        url = f"{self.TRCA_ARCGIS_URL}/TRCA_Flood_Hazard/FeatureServer/0/query"

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
                    url,
                    params=params,
                    timeout=15.0,
                    headers={"User-Agent": "LocationOverview/1.0"},
                )

                if response.status_code == 200:
                    data = response.json()
                    features = data.get("features", [])

                    if features:
                        attrs = features[0].get("attributes", {})
                        flood_type = attrs.get("FLOOD_TYPE", "").lower()

                        return {
                            "floodplain": True,
                            "floodplain_type": self._parse_flood_type(flood_type),
                            "flood_fringe": "fringe" in flood_type,
                            "flood_special_policy": "special" in flood_type,
                            "in_regulated_area": True,
                        }

        except Exception:
            pass

        return None

    async def _query_trca_wetland(
        self,
        lat: float,
        lon: float,
    ) -> Optional[Dict[str, Any]]:
        """
        Query TRCA Wetland layer.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Wetland data or None
        """
        url = f"{self.TRCA_ARCGIS_URL}/TRCA_Wetland/FeatureServer/0/query"

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
                    url,
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
                            "wetland": True,
                            "wetland_type": attrs.get("WETLAND_TYPE", "Evaluated Wetland"),
                            "in_regulated_area": True,
                            "natural_heritage": True,
                        }

        except Exception:
            pass

        return None

    async def _query_cvc_regulated(
        self,
        lat: float,
        lon: float,
    ) -> Optional[Dict[str, Any]]:
        """
        Query Credit Valley Conservation regulated areas.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            CVC regulated area data or None
        """
        # CVC ArcGIS services
        url = "https://services1.arcgis.com/DwLTn0u9VBSZvUPe/ArcGIS/rest/services/CVC_Regulation_Limit/FeatureServer/0/query"

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
                    url,
                    params=params,
                    timeout=15.0,
                    headers={"User-Agent": "LocationOverview/1.0"},
                )

                if response.status_code == 200:
                    data = response.json()
                    features = data.get("features", [])

                    if features:
                        return {
                            "in_regulated_area": True,
                            "conservation_authority": "cvc",
                        }

        except Exception:
            pass

        return None

    async def _query_provincial_natural_heritage(
        self,
        lat: float,
        lon: float,
    ) -> Optional[Dict[str, Any]]:
        """
        Query provincial natural heritage layers.

        Uses Ontario GeoHub for province-wide coverage.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Natural heritage data or None
        """
        # Query provincial significant wetlands
        wetland_url = "https://ws.lioservices.lrc.gov.on.ca/arcgis1071a/rest/services/LIO_Open_Data/LIO_Open14/MapServer/38/query"

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
                    wetland_url,
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
                            "wetland": True,
                            "wetland_type": attrs.get("WETLAND_TYPE", "Provincially Significant Wetland"),
                            "natural_heritage": True,
                        }

        except Exception:
            pass

        return None

    def _get_conservation_authority(self, municipality: str) -> Optional[str]:
        """
        Determine conservation authority jurisdiction.

        Args:
            municipality: Municipality name

        Returns:
            Conservation authority code or None
        """
        municipality_lower = municipality.lower()

        for ca, municipalities in self.CA_JURISDICTION.items():
            if any(m in municipality_lower for m in municipalities):
                return ca

        return None

    def _parse_flood_type(self, flood_type: str) -> str:
        """
        Parse flood hazard type to human-readable description.

        Args:
            flood_type: Raw flood type value

        Returns:
            Human-readable flood type
        """
        flood_type_lower = flood_type.lower()

        if "regulatory" in flood_type_lower or "100" in flood_type_lower:
            return "Regulatory Flood (100-year)"
        elif "fringe" in flood_type_lower:
            return "Flood Fringe (safe fill)"
        elif "special" in flood_type_lower:
            return "Special Policy Area"
        elif "floodway" in flood_type_lower:
            return "Floodway (no development)"
        else:
            return "Flood Hazard"

    def is_applicable(self, municipality: str) -> bool:
        """
        TRCA provider applicable to municipalities within CA jurisdiction.

        Args:
            municipality: Municipality name

        Returns:
            True if within CA jurisdiction
        """
        # Currently supports TRCA and CVC jurisdictions
        # Returns True for all to enable provincial fallback
        return True
