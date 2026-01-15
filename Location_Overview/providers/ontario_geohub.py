"""
Ontario GeoHub Provider Module

Queries Ontario GeoHub (Land Information Ontario) for provincial plan overlays:
- Greenbelt Plan
- Growth Plan
- Oak Ridges Moraine
- Niagara Escarpment Plan
- Natural Heritage System

These plans overlay all Ontario municipalities.
"""

import time
import asyncio
from typing import Dict, Any, Optional

import httpx

from .base import BaseProvider, ProviderResult, ProviderStatus


class OntarioGeoHubProvider(BaseProvider):
    """
    Query Ontario GeoHub for provincial plan overlays.

    Uses ArcGIS REST API endpoints from Land Information Ontario.
    Provincial plans apply to all Ontario municipalities.
    """

    name = "Ontario GeoHub"
    base_url = "https://ws.lioservices.lrc.gov.on.ca/arcgis1071a/rest/services"
    rate_limit = 5.0  # requests per second
    cache_ttl = 86400 * 30  # 30 days (plans don't change often)

    # ArcGIS layer endpoints for provincial plans
    # These are the authoritative data sources from Land Information Ontario
    LAYERS = {
        "greenbelt": "/LIO_Open_Data/LIO_Open14/MapServer/24",  # Greenbelt Designation
        "growth_plan": "/LIO_Open_Data/LIO_Open14/MapServer/26",  # Growth Plan Boundary
        "orm": "/LIO_Open_Data/LIO_Open14/MapServer/40",  # Oak Ridges Moraine
        "niagara_escarpment": "/LIO_Open_Data/LIO_Open14/MapServer/36",  # Niagara Escarpment Plan
        "natural_heritage": "/LIO_Open_Data/LIO_Open14/MapServer/34",  # Natural Heritage System
    }

    # Fallback URLs if primary doesn't work
    FALLBACK_LAYERS = {
        "greenbelt": "/LIO_OPEN_DATA/Greenbelt_Designation/MapServer/0",
        "growth_plan": "/LIO_OPEN_DATA/Growth_Plan_Boundary/MapServer/0",
    }

    async def query(
        self,
        lat: float,
        lon: float,
        **kwargs,
    ) -> ProviderResult:
        """
        Query all provincial plan layers for a point.

        Args:
            lat: Latitude (WGS84)
            lon: Longitude (WGS84)

        Returns:
            ProviderResult with provincial plan data
        """
        start_time = time.time()

        results = {
            "greenbelt_area": False,
            "greenbelt_designation": None,
            "growth_plan_area": None,
            "oak_ridges_moraine": False,
            "orm_designation": None,
            "niagara_escarpment": False,
            "nec_designation": None,
            "natural_heritage": False,
        }
        warnings = []
        errors = []

        try:
            # Query each layer in parallel
            tasks = []
            layer_names = []

            for plan_name, layer_path in self.LAYERS.items():
                tasks.append(self._query_layer(lat, lon, layer_path))
                layer_names.append(plan_name)

            layer_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for plan_name, layer_result in zip(layer_names, layer_results):
                if isinstance(layer_result, Exception):
                    warnings.append(f"{plan_name}: {str(layer_result)}")
                    continue

                if layer_result:
                    self._update_results(results, plan_name, layer_result)

            response_time = (time.time() - start_time) * 1000

            return self._make_result(
                success=True,
                data=results,
                response_time_ms=response_time,
                warnings=warnings,
                metadata={
                    "layers_queried": len(self.LAYERS),
                    "errors": errors,
                    "queried_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                },
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return self._make_result(
                success=False,
                error=str(e),
                response_time_ms=response_time,
            )

    async def _query_layer(
        self,
        lat: float,
        lon: float,
        layer_path: str,
        timeout: float = 15.0,
    ) -> Optional[Dict[str, Any]]:
        """
        Query a single ArcGIS layer.

        Args:
            lat: Latitude
            lon: Longitude
            layer_path: Path to the layer endpoint
            timeout: Request timeout

        Returns:
            Layer query result or None
        """
        url = f"{self.base_url}{layer_path}/query"

        # ArcGIS REST API query parameters
        params = {
            "geometry": f"{lon},{lat}",
            "geometryType": "esriGeometryPoint",
            "inSR": "4326",  # WGS84
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": "*",
            "returnGeometry": "false",
            "f": "json",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    params=params,
                    timeout=timeout,
                    headers={"User-Agent": "LocationOverview/1.0"},
                )
                response.raise_for_status()
                return response.json()

        except httpx.TimeoutException:
            raise TimeoutError(f"Timeout querying {layer_path}")
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"HTTP {e.response.status_code} from {layer_path}")
        except Exception as e:
            raise RuntimeError(f"Error querying {layer_path}: {str(e)}")

    def _update_results(
        self,
        results: Dict[str, Any],
        plan_name: str,
        layer_result: Dict[str, Any],
    ) -> None:
        """
        Update results dict based on layer query response.

        Args:
            results: Results dictionary to update
            plan_name: Name of the plan (greenbelt, growth_plan, etc.)
            layer_result: ArcGIS query response
        """
        features = layer_result.get("features", [])
        if not features:
            return

        # Get attributes from first feature
        attributes = features[0].get("attributes", {})

        if plan_name == "greenbelt":
            results["greenbelt_area"] = True
            # Try different field names that might be used
            designation = (
                attributes.get("DESIGNATION_E")
                or attributes.get("DESIGNATION")
                or attributes.get("GB_DESIGN")
                or attributes.get("GREENBELT_DESIGNATION")
            )
            results["greenbelt_designation"] = designation

        elif plan_name == "growth_plan":
            # Growth Plan areas: Built-up, Designated Greenfield, Rural
            area_type = (
                attributes.get("PLAN_AREA_E")
                or attributes.get("AREA_TYPE")
                or attributes.get("GP_AREA")
            )
            results["growth_plan_area"] = area_type

        elif plan_name == "orm":
            results["oak_ridges_moraine"] = True
            designation = (
                attributes.get("DESIGNATION_E")
                or attributes.get("ORM_DESIGN")
                or attributes.get("DESIGNATION")
            )
            results["orm_designation"] = designation

        elif plan_name == "niagara_escarpment":
            results["niagara_escarpment"] = True
            designation = (
                attributes.get("DESIGNATION_E")
                or attributes.get("NEC_DESIGN")
                or attributes.get("DESIGNATION")
            )
            results["nec_designation"] = designation

        elif plan_name == "natural_heritage":
            results["natural_heritage"] = True

    def is_applicable(self, municipality: str) -> bool:
        """
        Provincial plans apply to all Ontario municipalities.

        Args:
            municipality: Municipality name

        Returns:
            Always True for Ontario locations
        """
        return True

    async def get_greenbelt_status(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Convenience method to check just Greenbelt status.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Dict with greenbelt_area and greenbelt_designation
        """
        result = await self._query_layer(lat, lon, self.LAYERS["greenbelt"])

        if not result or not result.get("features"):
            return {"greenbelt_area": False, "greenbelt_designation": None}

        attributes = result["features"][0].get("attributes", {})
        return {
            "greenbelt_area": True,
            "greenbelt_designation": attributes.get("DESIGNATION_E"),
        }
