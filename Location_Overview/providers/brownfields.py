"""
Brownfields Environmental Site Registry Provider Module

Queries the Ontario Environmental Site Registry (ESR) for:
- Records of Site Condition (RSC)
- Contaminated sites records
- Phase I/II ESA filing status
- Cleanup status and acknowledgments

The ESR is maintained by the Ministry of the Environment, Conservation and Parks (MECP).
"""

import time
import re
from typing import Dict, Any, Optional, List
from urllib.parse import urlencode

import httpx

from .base import BaseProvider, ProviderResult


class BrownfieldsProvider(BaseProvider):
    """
    Query Ontario Environmental Site Registry for contamination records.

    The ESR contains:
    - Records of Site Condition (RSC) filed under O.Reg. 153/04
    - Property use changes requiring environmental assessment
    - Contamination acknowledgments and cleanup documentation

    This is critical data for any property transaction or development.
    """

    name = "Brownfields ESR"
    base_url = "https://www.ontario.ca/page/environmental-site-registry"
    rate_limit = 1.0  # 1 request per second (conservative for government site)
    cache_ttl = 86400 * 7  # 7 days

    # ESR Search API (unofficial, may require scraping)
    ESR_SEARCH_URL = "https://www.lioapplications.lrc.gov.on.ca/ESR/index.html"

    # Toronto specific brownfield data
    TORONTO_BROWNFIELD_URL = "https://services3.arcgis.com/b9WvedVPoizGfvfD/ArcGIS/rest/services"

    async def query(
        self,
        lat: float,
        lon: float,
        radius_m: int = 250,
        **kwargs,
    ) -> ProviderResult:
        """
        Query Environmental Site Registry for location.

        Args:
            lat: Latitude (WGS84)
            lon: Longitude (WGS84)
            radius_m: Search radius in meters (default 250m)

        Returns:
            ProviderResult with ESR data
        """
        start_time = time.time()
        warnings = []

        results = {
            "brownfield_record": False,
            "rsc_filed": False,
            "rsc_number": None,
            "rsc_date": None,
            "rsc_type": None,
            "property_use": None,
            "contamination_noted": False,
            "cleanup_status": None,
            "nearby_brownfields": [],
            "esr_search_url": None,
        }

        try:
            municipality = kwargs.get("municipality", "").lower()

            # Query Ontario ESR via web service
            esr_result = await self._query_ontario_esr(lat, lon, radius_m)
            if esr_result:
                results.update(esr_result)

            # Query Toronto-specific brownfield layers if applicable
            if municipality in ["toronto", "city of toronto"]:
                toronto_result = await self._query_toronto_brownfields(lat, lon, radius_m)
                if toronto_result:
                    # Merge results, ESR takes precedence for direct hits
                    if not results["brownfield_record"]:
                        results.update(toronto_result)
                    else:
                        results["nearby_brownfields"].extend(
                            toronto_result.get("nearby_brownfields", [])
                        )

            # Generate ESR search URL for manual verification
            results["esr_search_url"] = self._generate_esr_search_url(lat, lon)

            if not results["brownfield_record"] and not results["nearby_brownfields"]:
                # No records found, add note
                warnings.append(
                    "No ESR records found. Manual search recommended at ontario.ca/esr"
                )

            response_time = (time.time() - start_time) * 1000

            return self._make_result(
                success=True,
                data=results,
                response_time_ms=response_time,
                warnings=warnings,
                metadata={
                    "source": "Ontario Environmental Site Registry",
                    "source_url": "https://www.ontario.ca/page/environmental-site-registry",
                    "note": "RSC data under O.Reg. 153/04. Manual verification recommended.",
                },
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return self._make_result(
                success=False,
                error=str(e),
                response_time_ms=response_time,
            )

    async def _query_ontario_esr(
        self,
        lat: float,
        lon: float,
        radius_m: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Query Ontario ESR via LIO services.

        Args:
            lat: Latitude
            lon: Longitude
            radius_m: Search radius

        Returns:
            ESR data or None
        """
        # Ontario LIO ESR layer
        esr_url = "https://ws.lioservices.lrc.gov.on.ca/arcgis1071a/rest/services/LIO_Open_Data/LIO_Open14/MapServer/15/query"

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
                    esr_url,
                    params=params,
                    timeout=15.0,
                    headers={"User-Agent": "LocationOverview/1.0"},
                )

                if response.status_code == 200:
                    data = response.json()
                    features = data.get("features", [])

                    if features:
                        # Found ESR records
                        direct_hit = None
                        nearby = []

                        for feature in features:
                            attrs = feature.get("attributes", {})
                            record = self._parse_esr_record(attrs)

                            # Check if this is a direct hit (within 50m)
                            # TODO: Calculate actual distance if geometry provided
                            if len(features) == 1:
                                direct_hit = record
                            else:
                                nearby.append(record)

                        if direct_hit:
                            return {
                                "brownfield_record": True,
                                "rsc_filed": direct_hit.get("rsc_filed"),
                                "rsc_number": direct_hit.get("rsc_number"),
                                "rsc_date": direct_hit.get("rsc_date"),
                                "rsc_type": direct_hit.get("rsc_type"),
                                "property_use": direct_hit.get("property_use"),
                                "contamination_noted": direct_hit.get("contamination_noted"),
                                "cleanup_status": direct_hit.get("cleanup_status"),
                                "nearby_brownfields": nearby,
                            }
                        elif nearby:
                            return {
                                "brownfield_record": False,
                                "nearby_brownfields": nearby,
                            }

        except Exception:
            pass  # Graceful degradation

        return None

    async def _query_toronto_brownfields(
        self,
        lat: float,
        lon: float,
        radius_m: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Query Toronto-specific brownfield data.

        Toronto maintains additional brownfield tracking beyond provincial ESR.

        Args:
            lat: Latitude
            lon: Longitude
            radius_m: Search radius

        Returns:
            Toronto brownfield data or None
        """
        # Toronto Environmental Reports layer
        toronto_url = "https://services3.arcgis.com/b9WvedVPoizGfvfD/ArcGIS/rest/services/COTGEO_CONTAMINATED_SITES/FeatureServer/0/query"

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
                    toronto_url,
                    params=params,
                    timeout=15.0,
                    headers={"User-Agent": "LocationOverview/1.0"},
                )

                if response.status_code == 200:
                    data = response.json()
                    features = data.get("features", [])

                    if features:
                        nearby = []
                        for feature in features:
                            attrs = feature.get("attributes", {})
                            nearby.append({
                                "address": attrs.get("ADDRESS"),
                                "site_name": attrs.get("SITE_NAME"),
                                "status": attrs.get("STATUS"),
                                "contaminant_type": attrs.get("CONTAMINANT_TYPE"),
                            })

                        return {"nearby_brownfields": nearby}

        except Exception:
            pass

        return None

    def _parse_esr_record(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse ESR record from attributes.

        Args:
            attrs: Feature attributes

        Returns:
            Parsed record dict
        """
        return {
            "rsc_filed": True,
            "rsc_number": attrs.get("RSC_NUMBER") or attrs.get("SITE_ID"),
            "rsc_date": attrs.get("RSC_DATE") or attrs.get("FILING_DATE"),
            "rsc_type": attrs.get("RSC_TYPE") or attrs.get("RECORD_TYPE"),
            "property_use": attrs.get("PROPERTY_USE") or attrs.get("LAND_USE"),
            "contamination_noted": attrs.get("CONTAMINATION") == "Y",
            "cleanup_status": attrs.get("CLEANUP_STATUS") or attrs.get("STATUS"),
            "address": attrs.get("ADDRESS") or attrs.get("SITE_ADDRESS"),
            "municipality": attrs.get("MUNICIPALITY"),
        }

    def _generate_esr_search_url(self, lat: float, lon: float) -> str:
        """
        Generate URL for manual ESR search.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            ESR search URL
        """
        # The ESR doesn't support coordinate search directly
        # Return the main search page
        return "https://www.lioapplications.lrc.gov.on.ca/ESR/index.html"

    def is_applicable(self, municipality: str) -> bool:
        """
        ESR provider is applicable to all Ontario municipalities.

        Args:
            municipality: Municipality name

        Returns:
            Always True for Ontario
        """
        return True
