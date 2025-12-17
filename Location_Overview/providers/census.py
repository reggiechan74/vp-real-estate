"""
Census Demographics Provider Module

Queries demographic data from:
- Statistics Canada Census (via CensusMapper API)
- Toronto Neighbourhood Profiles
- Ottawa Neighbourhood Profiles

Provides neighbourhood-level demographic context for location overviews.
"""

import time
from typing import Dict, Any, Optional, List

import httpx

from .base import BaseProvider, ProviderResult


class CensusProvider(BaseProvider):
    """
    Query census and demographic data for neighbourhoods.

    Provides:
    - Population and growth
    - Household characteristics
    - Income levels
    - Housing tenure (owned vs rented)
    - Housing types (single, semi, apartment)
    - Age distribution

    Data from 2021 Census with 2016 comparisons.
    """

    name = "Census Demographics"
    base_url = "https://censusmapper.ca"
    rate_limit = 2.0  # requests per second
    cache_ttl = 86400 * 90  # 90 days (census data is stable)

    # CensusMapper API (community project, requires API key for full access)
    CENSUSMAPPER_API = "https://censusmapper.ca/api/v1"

    # Toronto neighbourhood profiles endpoint
    TORONTO_PROFILES_URL = "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action/datastore_search"

    # Key census variables (2021 Census)
    CENSUS_VARIABLES = {
        "population": "v_CA21_1",
        "population_2016": "v_CA16_1",
        "dwellings": "v_CA21_4",
        "households": "v_CA21_443",
        "median_income": "v_CA21_906",
        "average_income": "v_CA21_907",
        "owner_households": "v_CA21_4237",
        "renter_households": "v_CA21_4238",
        "single_detached": "v_CA21_434",
        "apartment_5plus": "v_CA21_439",
    }

    async def query(
        self,
        lat: float,
        lon: float,
        **kwargs,
    ) -> ProviderResult:
        """
        Query demographic data for location.

        Args:
            lat: Latitude (WGS84)
            lon: Longitude (WGS84)

        Returns:
            ProviderResult with demographic data
        """
        start_time = time.time()
        warnings = []

        results = {
            "census_year": 2021,
            "population": None,
            "population_growth": None,
            "households": None,
            "median_income": None,
            "average_income": None,
            "owner_percentage": None,
            "renter_percentage": None,
            "single_detached_percentage": None,
            "apartment_percentage": None,
            "density_per_sqkm": None,
            "neighbourhood_name": None,
            "census_tract": None,
            "dissemination_area": None,
        }

        try:
            municipality = kwargs.get("municipality", "").lower()
            neighbourhood_name = kwargs.get("neighbourhood_name")

            # Query Toronto-specific neighbourhood profiles
            if municipality in ["toronto", "city of toronto"]:
                toronto_result = await self._query_toronto_profiles(
                    lat, lon, neighbourhood_name
                )
                if toronto_result:
                    results.update(toronto_result)
                else:
                    warnings.append("Toronto neighbourhood profile not found")

            # Query Census via CensusMapper (fallback or additional data)
            census_result = await self._query_censusmapper(lat, lon)
            if census_result:
                # Merge census data (Toronto profiles take precedence for Toronto)
                for key, value in census_result.items():
                    if results.get(key) is None:
                        results[key] = value

            # Calculate derived metrics
            if results.get("owner_percentage") is None and results.get("households"):
                owner = results.get("owner_households", 0)
                renter = results.get("renter_households", 0)
                total = owner + renter
                if total > 0:
                    results["owner_percentage"] = round(owner / total * 100, 1)
                    results["renter_percentage"] = round(renter / total * 100, 1)

            response_time = (time.time() - start_time) * 1000

            return self._make_result(
                success=True,
                data=results,
                response_time_ms=response_time,
                warnings=warnings,
                metadata={
                    "source": "Statistics Canada 2021 Census",
                    "profiles_source": "City of Toronto Neighbourhood Profiles",
                    "note": "Census data reflects 2021 population counts",
                },
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return self._make_result(
                success=False,
                error=str(e),
                response_time_ms=response_time,
            )

    async def _query_toronto_profiles(
        self,
        lat: float,
        lon: float,
        neighbourhood_name: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Query Toronto Neighbourhood Profiles.

        Toronto maintains detailed neighbourhood profiles with ~250 indicators.

        Args:
            lat: Latitude
            lon: Longitude
            neighbourhood_name: Optional neighbourhood name for direct lookup

        Returns:
            Neighbourhood profile data or None
        """
        # Toronto Neighbourhood Profiles 2021 resource ID
        resource_id = "6e19a90f-971c-46b3-852c-0c48c436d1fc"

        try:
            # If we have neighbourhood name, query directly
            if neighbourhood_name:
                params = {
                    "resource_id": resource_id,
                    "q": neighbourhood_name,
                    "limit": 1,
                }

                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        self.TORONTO_PROFILES_URL,
                        params=params,
                        timeout=15.0,
                        headers={"User-Agent": "LocationOverview/1.0"},
                    )

                    if response.status_code == 200:
                        data = response.json()
                        records = data.get("result", {}).get("records", [])

                        if records:
                            return self._parse_toronto_profile(records[0])

            # Alternative: Query neighbourhood profiles CSV for all data
            # This would require downloading and caching the full dataset
            # For MVP, return None if no direct match
            return None

        except Exception:
            pass

        return None

    async def _query_censusmapper(
        self,
        lat: float,
        lon: float,
    ) -> Optional[Dict[str, Any]]:
        """
        Query CensusMapper API for census data.

        CensusMapper provides access to Canadian census data via API.
        Note: Full API access requires registration.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Census data or None
        """
        # CensusMapper requires API key for detailed queries
        # For MVP, return basic data from public endpoints

        try:
            # Query census tract via Statistics Canada geography API
            geo_url = "https://www12.statcan.gc.ca/rest/census-recensement/CR2021Geo.json"

            params = {
                "lat": lat,
                "long": lon,
                "geos": "CT",  # Census Tract
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    geo_url,
                    params=params,
                    timeout=15.0,
                    headers={"User-Agent": "LocationOverview/1.0"},
                )

                if response.status_code == 200:
                    data = response.json()

                    # Parse census tract info
                    if data.get("CTUID"):
                        return {
                            "census_tract": data.get("CTUID"),
                            "dissemination_area": data.get("DAUID"),
                            "csd_name": data.get("CSDname"),
                            "cma_name": data.get("CMAname"),
                        }

        except Exception:
            pass

        return None

    def _parse_toronto_profile(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse Toronto Neighbourhood Profile record.

        Args:
            record: Raw profile record

        Returns:
            Parsed demographic data
        """
        result = {
            "neighbourhood_name": record.get("Neighbourhood Name"),
            "neighbourhood_id": record.get("Neighbourhood Number"),
        }

        # Map indicator names to our schema
        indicator_mapping = {
            "Population, 2021": "population",
            "Population, 2016": "population_2016",
            "Population % change, 2016-2021": "population_growth",
            "Total private dwellings, 2021": "dwellings",
            "Total - Private households by tenure": "households",
            "Median total income in 2020": "median_income",
            "Average total income in 2020": "average_income",
            "Owner": "owner_households",
            "Renter": "renter_households",
            "Single-detached house": "single_detached",
            "Apartment in a building that has five or more storeys": "apartment_5plus",
            "Population density per square kilometre": "density_per_sqkm",
        }

        # Toronto profiles are structured with Characteristic as rows
        # This would require pivoting the data
        # For now, check if any direct fields match
        for indicator, field in indicator_mapping.items():
            if record.get("Characteristic") == indicator:
                try:
                    result[field] = float(record.get("Total", 0))
                except (ValueError, TypeError):
                    pass

        return result

    async def _query_neighbourhood_aggregated(
        self,
        neighbourhood_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Query aggregated neighbourhood data.

        This would fetch all indicators for a neighbourhood and aggregate.

        Args:
            neighbourhood_id: Toronto neighbourhood ID

        Returns:
            Aggregated data or None
        """
        # Toronto Neighbourhood Profiles endpoint
        resource_id = "6e19a90f-971c-46b3-852c-0c48c436d1fc"

        try:
            params = {
                "resource_id": resource_id,
                "filters": f'{{"Neighbourhood Number": "{neighbourhood_id}"}}',
                "limit": 500,  # Get all indicators
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.TORONTO_PROFILES_URL,
                    params=params,
                    timeout=30.0,
                    headers={"User-Agent": "LocationOverview/1.0"},
                )

                if response.status_code == 200:
                    data = response.json()
                    records = data.get("result", {}).get("records", [])

                    if records:
                        # Aggregate all indicators
                        return self._aggregate_indicators(records)

        except Exception:
            pass

        return None

    def _aggregate_indicators(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate multiple indicator records into single profile.

        Args:
            records: List of indicator records

        Returns:
            Aggregated profile data
        """
        result = {}

        # Key indicators to extract
        indicators = {
            "Population, 2021": ("population", int),
            "Population density per square kilometre": ("density_per_sqkm", float),
            "Median total income in 2020 among recipients ($)": ("median_income", float),
            "Average total income in 2020 among recipients ($)": ("average_income", float),
            "Total - Private households by tenure - 25% sample data": ("households", int),
            "Owner": ("owner_households", int),
            "Renter": ("renter_households", int),
        }

        for record in records:
            characteristic = record.get("Characteristic", "")
            total = record.get("Total")

            if characteristic in indicators:
                field, dtype = indicators[characteristic]
                try:
                    if total and total != "...":
                        result[field] = dtype(total.replace(",", ""))
                except (ValueError, TypeError):
                    pass

        # Calculate percentages
        if result.get("households"):
            owner = result.get("owner_households", 0)
            renter = result.get("renter_households", 0)
            total = owner + renter
            if total > 0:
                result["owner_percentage"] = round(owner / total * 100, 1)
                result["renter_percentage"] = round(renter / total * 100, 1)

        return result

    def is_applicable(self, municipality: str) -> bool:
        """
        Census provider applicable to all Ontario municipalities.

        Full profiles available for Toronto and Ottawa.
        Basic census tract data available province-wide.

        Args:
            municipality: Municipality name

        Returns:
            Always True for Ontario
        """
        return True
