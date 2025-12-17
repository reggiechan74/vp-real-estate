"""
GTFS Transit Provider Module

Queries transit data from GTFS (General Transit Feed Specification) sources:
- TTC (Toronto Transit Commission)
- Metrolinx/GO Transit
- OC Transpo (Ottawa)
- MiWay (Mississauga)
- Other regional transit agencies

Provides detailed transit accessibility information beyond OSM data.
"""

import time
from typing import Dict, Any, Optional, List
from math import radians, cos, sin, sqrt, atan2

import httpx

from .base import BaseProvider, ProviderResult


class GTFSProvider(BaseProvider):
    """
    Query transit data from multiple GTFS sources.

    Provides:
    - Nearby transit stops (by mode)
    - Service frequency
    - Route information
    - Rapid transit (subway, LRT) accessibility
    - Regional transit (GO) accessibility
    """

    name = "Transit GTFS"
    base_url = "https://transitfeeds.com"
    rate_limit = 5.0  # requests per second
    cache_ttl = 86400  # 24 hours (schedules change frequently)

    # Transit agency endpoints
    AGENCY_ENDPOINTS = {
        "ttc": {
            "name": "TTC",
            "gtfs_url": "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action",
            "stops_layer": "ttc-stops",
        },
        "metrolinx": {
            "name": "GO Transit / UP Express",
            "gtfs_url": "https://www.gotransit.com/static_files/gotransit/assets/GTFS",
        },
        "octranspo": {
            "name": "OC Transpo",
            "gtfs_url": "https://www.octranspo.com/files/google_transit.zip",
        },
        "miway": {
            "name": "MiWay",
            "gtfs_url": "https://www.miway.ca/Data/GoogleTransit/google_transit.zip",
        },
    }

    # Rapid transit lines (for premium service detection)
    RAPID_TRANSIT = {
        "toronto": {
            "subway": ["1 Yonge-University", "2 Bloor-Danforth", "3 Scarborough", "4 Sheppard"],
            "lrt": ["5 Eglinton", "6 Finch West"],
            "streetcar": ["501", "504", "509", "510", "511", "512"],
        },
        "ottawa": {
            "lrt": ["Confederation Line", "Trillium Line"],
        },
    }

    async def query(
        self,
        lat: float,
        lon: float,
        radius_m: int = 1000,
        **kwargs,
    ) -> ProviderResult:
        """
        Query transit accessibility for location.

        Args:
            lat: Latitude (WGS84)
            lon: Longitude (WGS84)
            radius_m: Search radius in meters

        Returns:
            ProviderResult with transit data
        """
        start_time = time.time()
        warnings = []

        results = {
            "transit_stops": [],
            "rapid_transit": [],
            "regional_transit": [],
            "nearest_subway": None,
            "nearest_lrt": None,
            "nearest_go_station": None,
            "nearest_bus_stop": None,
            "transit_score": None,
            "service_summary": None,
        }

        try:
            municipality = kwargs.get("municipality", "").lower()

            # Query TTC if in Toronto
            if municipality in ["toronto", "city of toronto"]:
                ttc_result = await self._query_ttc_stops(lat, lon, radius_m)
                if ttc_result:
                    results["transit_stops"].extend(ttc_result.get("stops", []))
                    if ttc_result.get("nearest_subway"):
                        results["nearest_subway"] = ttc_result["nearest_subway"]
                    if ttc_result.get("nearest_streetcar"):
                        results["nearest_lrt"] = ttc_result["nearest_streetcar"]

            # Query GO Transit (GTA-wide)
            if municipality in ["toronto", "mississauga", "brampton", "markham", "vaughan",
                               "richmond hill", "oakville", "burlington", "hamilton",
                               "oshawa", "whitby", "ajax", "pickering"]:
                go_result = await self._query_go_stations(lat, lon, radius_m * 3)  # Wider radius for GO
                if go_result:
                    results["regional_transit"].extend(go_result.get("stations", []))
                    if go_result.get("nearest_station"):
                        results["nearest_go_station"] = go_result["nearest_station"]

            # Query OC Transpo if in Ottawa
            if municipality in ["ottawa", "city of ottawa"]:
                oc_result = await self._query_octranspo(lat, lon, radius_m)
                if oc_result:
                    results["transit_stops"].extend(oc_result.get("stops", []))
                    if oc_result.get("nearest_lrt"):
                        results["nearest_lrt"] = oc_result["nearest_lrt"]

            # Calculate transit score
            results["transit_score"] = self._calculate_transit_score(results)
            results["service_summary"] = self._generate_service_summary(results)

            # Find nearest bus stop
            bus_stops = [s for s in results["transit_stops"] if s.get("type") == "bus"]
            if bus_stops:
                results["nearest_bus_stop"] = min(bus_stops, key=lambda x: x.get("distance_m", float("inf")))

            response_time = (time.time() - start_time) * 1000

            return self._make_result(
                success=True,
                data=results,
                response_time_ms=response_time,
                warnings=warnings,
                metadata={
                    "source": "Municipal GTFS feeds",
                    "note": "Transit schedules subject to change",
                },
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return self._make_result(
                success=False,
                error=str(e),
                response_time_ms=response_time,
            )

    async def _query_ttc_stops(
        self,
        lat: float,
        lon: float,
        radius_m: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Query TTC stops via Toronto Open Data.

        Args:
            lat: Latitude
            lon: Longitude
            radius_m: Search radius

        Returns:
            TTC stops data or None
        """
        # TTC stops ArcGIS layer
        ttc_url = "https://services3.arcgis.com/b9WvedVPoizGfvfD/ArcGIS/rest/services/COTGEO_TTC_STOPS/FeatureServer/0/query"

        try:
            params = {
                "geometry": f"{lon},{lat}",
                "geometryType": "esriGeometryPoint",
                "inSR": "4326",
                "spatialRel": "esriSpatialRelIntersects",
                "distance": radius_m,
                "units": "esriSRUnit_Meter",
                "outFields": "*",
                "returnGeometry": "true",
                "f": "json",
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    ttc_url,
                    params=params,
                    timeout=15.0,
                    headers={"User-Agent": "LocationOverview/1.0"},
                )

                if response.status_code == 200:
                    data = response.json()
                    features = data.get("features", [])

                    stops = []
                    nearest_subway = None
                    nearest_streetcar = None

                    for feature in features:
                        attrs = feature.get("attributes", {})
                        geom = feature.get("geometry", {})

                        stop_lat = geom.get("y")
                        stop_lon = geom.get("x")

                        if stop_lat and stop_lon:
                            distance = self._haversine(lat, lon, stop_lat, stop_lon)
                        else:
                            distance = None

                        stop_type = self._classify_ttc_stop(attrs)

                        stop = {
                            "name": attrs.get("STOP_NAME"),
                            "stop_id": attrs.get("STOP_ID"),
                            "type": stop_type,
                            "routes": attrs.get("ROUTES", "").split(",") if attrs.get("ROUTES") else [],
                            "distance_m": round(distance) if distance else None,
                            "lat": stop_lat,
                            "lon": stop_lon,
                        }
                        stops.append(stop)

                        # Track nearest of each type
                        if stop_type == "subway" and distance:
                            if not nearest_subway or distance < nearest_subway.get("distance_m", float("inf")):
                                nearest_subway = stop
                        elif stop_type == "streetcar" and distance:
                            if not nearest_streetcar or distance < nearest_streetcar.get("distance_m", float("inf")):
                                nearest_streetcar = stop

                    # Sort by distance
                    stops.sort(key=lambda x: x.get("distance_m") or float("inf"))

                    return {
                        "stops": stops[:20],  # Limit results
                        "nearest_subway": nearest_subway,
                        "nearest_streetcar": nearest_streetcar,
                    }

        except Exception:
            pass

        return None

    async def _query_go_stations(
        self,
        lat: float,
        lon: float,
        radius_m: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Query GO Transit stations.

        Args:
            lat: Latitude
            lon: Longitude
            radius_m: Search radius

        Returns:
            GO station data or None
        """
        # Metrolinx GO stations layer
        go_url = "https://services1.arcgis.com/qAo1OsXi67xESFfi/ArcGIS/rest/services/GO_Transit_Stations/FeatureServer/0/query"

        try:
            params = {
                "geometry": f"{lon},{lat}",
                "geometryType": "esriGeometryPoint",
                "inSR": "4326",
                "spatialRel": "esriSpatialRelIntersects",
                "distance": radius_m,
                "units": "esriSRUnit_Meter",
                "outFields": "*",
                "returnGeometry": "true",
                "f": "json",
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    go_url,
                    params=params,
                    timeout=15.0,
                    headers={"User-Agent": "LocationOverview/1.0"},
                )

                if response.status_code == 200:
                    data = response.json()
                    features = data.get("features", [])

                    stations = []
                    nearest_station = None

                    for feature in features:
                        attrs = feature.get("attributes", {})
                        geom = feature.get("geometry", {})

                        station_lat = geom.get("y")
                        station_lon = geom.get("x")

                        if station_lat and station_lon:
                            distance = self._haversine(lat, lon, station_lat, station_lon)
                        else:
                            distance = None

                        station = {
                            "name": attrs.get("STATION_NAME") or attrs.get("Name"),
                            "type": "go_station",
                            "lines": attrs.get("LINES", "").split(",") if attrs.get("LINES") else [],
                            "distance_m": round(distance) if distance else None,
                            "parking": attrs.get("PARKING_SPACES"),
                            "accessible": attrs.get("ACCESSIBLE") == "Y",
                        }
                        stations.append(station)

                        if distance and (not nearest_station or distance < nearest_station.get("distance_m", float("inf"))):
                            nearest_station = station

                    stations.sort(key=lambda x: x.get("distance_m") or float("inf"))

                    return {
                        "stations": stations[:5],
                        "nearest_station": nearest_station,
                    }

        except Exception:
            pass

        return None

    async def _query_octranspo(
        self,
        lat: float,
        lon: float,
        radius_m: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Query OC Transpo stops.

        Args:
            lat: Latitude
            lon: Longitude
            radius_m: Search radius

        Returns:
            OC Transpo data or None
        """
        # Ottawa transit stops layer
        oc_url = "https://maps.ottawa.ca/arcgis/rest/services/Transit_Stops/MapServer/0/query"

        try:
            params = {
                "geometry": f"{lon},{lat}",
                "geometryType": "esriGeometryPoint",
                "inSR": "4326",
                "spatialRel": "esriSpatialRelIntersects",
                "distance": radius_m,
                "units": "esriSRUnit_Meter",
                "outFields": "*",
                "returnGeometry": "true",
                "f": "json",
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    oc_url,
                    params=params,
                    timeout=15.0,
                    headers={"User-Agent": "LocationOverview/1.0"},
                )

                if response.status_code == 200:
                    data = response.json()
                    features = data.get("features", [])

                    stops = []
                    nearest_lrt = None

                    for feature in features:
                        attrs = feature.get("attributes", {})
                        geom = feature.get("geometry", {})

                        stop_lat = geom.get("y")
                        stop_lon = geom.get("x")

                        if stop_lat and stop_lon:
                            distance = self._haversine(lat, lon, stop_lat, stop_lon)
                        else:
                            distance = None

                        # Determine stop type
                        stop_type = "bus"
                        routes = attrs.get("ROUTES", "")
                        if "Line 1" in routes or "Line 2" in routes or "Confederation" in routes:
                            stop_type = "lrt"

                        stop = {
                            "name": attrs.get("STOP_NAME"),
                            "stop_id": attrs.get("STOP_CODE"),
                            "type": stop_type,
                            "routes": routes.split(",") if routes else [],
                            "distance_m": round(distance) if distance else None,
                        }
                        stops.append(stop)

                        if stop_type == "lrt" and distance:
                            if not nearest_lrt or distance < nearest_lrt.get("distance_m", float("inf")):
                                nearest_lrt = stop

                    stops.sort(key=lambda x: x.get("distance_m") or float("inf"))

                    return {
                        "stops": stops[:20],
                        "nearest_lrt": nearest_lrt,
                    }

        except Exception:
            pass

        return None

    def _classify_ttc_stop(self, attrs: Dict[str, Any]) -> str:
        """
        Classify TTC stop by type.

        Args:
            attrs: Stop attributes

        Returns:
            Stop type (subway, streetcar, bus)
        """
        stop_type = attrs.get("STOP_TYPE", "").lower()
        routes = attrs.get("ROUTES", "").upper()

        if "subway" in stop_type or any(line in routes for line in ["LINE 1", "LINE 2", "LINE 3", "LINE 4"]):
            return "subway"
        elif "streetcar" in stop_type or any(sc in routes for sc in ["501", "504", "509", "510", "511", "512"]):
            return "streetcar"
        else:
            return "bus"

    def _calculate_transit_score(self, results: Dict[str, Any]) -> int:
        """
        Calculate transit accessibility score (0-100).

        Args:
            results: Transit query results

        Returns:
            Transit score
        """
        score = 0

        # Subway/LRT within walking distance (major boost)
        if results.get("nearest_subway"):
            dist = results["nearest_subway"].get("distance_m", float("inf"))
            if dist <= 500:
                score += 40
            elif dist <= 1000:
                score += 25

        if results.get("nearest_lrt"):
            dist = results["nearest_lrt"].get("distance_m", float("inf"))
            if dist <= 500:
                score += 30
            elif dist <= 1000:
                score += 20

        # GO station (regional connectivity)
        if results.get("nearest_go_station"):
            dist = results["nearest_go_station"].get("distance_m", float("inf"))
            if dist <= 1000:
                score += 15
            elif dist <= 2000:
                score += 10

        # Bus stops
        if results.get("nearest_bus_stop"):
            dist = results["nearest_bus_stop"].get("distance_m", float("inf"))
            if dist <= 200:
                score += 15
            elif dist <= 500:
                score += 10

        # Total stops nearby (service frequency proxy)
        total_stops = len(results.get("transit_stops", []))
        score += min(total_stops * 2, 20)  # Cap at 20 points

        return min(score, 100)

    def _generate_service_summary(self, results: Dict[str, Any]) -> str:
        """
        Generate human-readable transit service summary.

        Args:
            results: Transit query results

        Returns:
            Service summary string
        """
        parts = []

        if results.get("nearest_subway"):
            subway = results["nearest_subway"]
            parts.append(f"Subway: {subway.get('name')} ({subway.get('distance_m')}m)")

        if results.get("nearest_lrt"):
            lrt = results["nearest_lrt"]
            parts.append(f"LRT: {lrt.get('name')} ({lrt.get('distance_m')}m)")

        if results.get("nearest_go_station"):
            go = results["nearest_go_station"]
            parts.append(f"GO: {go.get('name')} ({go.get('distance_m')}m)")

        if results.get("nearest_bus_stop"):
            bus = results["nearest_bus_stop"]
            parts.append(f"Bus: {bus.get('name')} ({bus.get('distance_m')}m)")

        total = len(results.get("transit_stops", []))
        if total:
            parts.append(f"{total} transit stops within search radius")

        return "; ".join(parts) if parts else "No transit service data available"

    def _haversine(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:
        """Calculate distance between two points in meters."""
        R = 6371000

        phi1, phi2 = radians(lat1), radians(lat2)
        delta_phi = radians(lat2 - lat1)
        delta_lambda = radians(lon2 - lon1)

        a = sin(delta_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(delta_lambda / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return R * c

    def is_applicable(self, municipality: str) -> bool:
        """
        GTFS provider is applicable to municipalities with transit service.

        Args:
            municipality: Municipality name

        Returns:
            True for municipalities with known GTFS data
        """
        supported = [
            "toronto", "ottawa", "mississauga", "brampton", "markham",
            "vaughan", "richmond hill", "oakville", "burlington",
            "hamilton", "oshawa", "whitby", "ajax", "pickering",
        ]
        return municipality.lower() in supported
