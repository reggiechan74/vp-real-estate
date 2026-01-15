"""
Result Merger Module

Combines results from multiple providers into a unified LocationOverview.
Handles conflict resolution based on source priority.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from math import atan2, degrees

from ..schemas.location_data import (
    LocationOverview,
    PropertyIdentification,
    PlanningFramework,
    ProvincialPlans,
    NeighbourhoodAnalysis,
    EnvironmentalFactors,
    MarketContext,
    TransportInfo,
    Amenity,
    SurroundingUse,
    DataSource,
)


class ResultMerger:
    """
    Merges provider results into unified LocationOverview.

    Priority order (highest to lowest):
    1. Paid/authoritative sources (MPAC, Teranet)
    2. Municipal open data (Toronto Open Data, Ottawa ArcGIS)
    3. Provincial data (Ontario GeoHub)
    4. Global data (Overpass API)
    5. Inferred/default values
    """

    # Source priority (higher = more authoritative)
    SOURCE_PRIORITY = {
        # Phase 3 (paid)
        "MPAC Propertyline": 100,
        "Teranet": 100,
        # Phase 2 (municipal/regulatory)
        "Toronto Open Data": 80,
        "Ottawa Open Data": 80,
        "Mississauga Open Data": 80,
        "Hamilton Open Data": 80,
        "Heritage Registry": 75,
        "Brownfields ESR": 75,
        "TRCA Conservation": 75,
        # Phase 1
        "Ontario GeoHub": 70,
        "Transit GTFS": 65,
        "Census Demographics": 60,
        "Overpass API": 50,
        "default": 0,
    }

    def __init__(self):
        """Initialize the result merger."""
        self.conflicts = []

    def merge(
        self,
        provider_results: Dict[str, Dict[str, Any]],
        base_info: Dict[str, Any],
    ) -> LocationOverview:
        """
        Merge provider results into LocationOverview.

        Args:
            provider_results: Dict mapping provider names to their results
            base_info: Base property information (address, lat, lon, municipality)

        Returns:
            Merged LocationOverview
        """
        self.conflicts = []

        # Create base overview
        overview = LocationOverview(
            property_id=self._create_property_id(base_info, provider_results),
            planning=self._merge_planning(provider_results),
            provincial_plans=self._merge_provincial_plans(provider_results),
            neighbourhood=self._merge_neighbourhood(provider_results, base_info),
            environmental=self._merge_environmental(provider_results),
            market=self._merge_market(provider_results),
            transport=self._merge_transport(provider_results),
            regional_context=self._generate_regional_context(base_info),
            generated_at=datetime.now(),
        )

        # Add data sources
        for provider_name in provider_results.keys():
            overview.add_data_source(
                name=provider_name,
                source_type="API" if "API" in provider_name else "Open Data",
            )

        # Add conflict warnings
        for conflict in self.conflicts:
            overview.add_warning(conflict)

        return overview

    def _create_property_id(
        self,
        base_info: Dict[str, Any],
        provider_results: Dict[str, Dict[str, Any]],
    ) -> PropertyIdentification:
        """Create PropertyIdentification from base info and provider data."""
        # Get neighbourhood from municipal data providers
        toronto_data = provider_results.get("Toronto Open Data", {})
        ottawa_data = provider_results.get("Ottawa Open Data", {})
        mississauga_data = provider_results.get("Mississauga Open Data", {})
        hamilton_data = provider_results.get("Hamilton Open Data", {})

        # Prefer municipality-specific data
        municipality = base_info.get("municipality", "").lower()

        if municipality in ["toronto", "city of toronto"]:
            ward = toronto_data.get("ward")
            ward_name = toronto_data.get("ward_name")
            neighbourhood = toronto_data.get("neighbourhood_name")
            neighbourhood_id = toronto_data.get("neighbourhood_id")
        elif municipality in ["ottawa", "city of ottawa"]:
            ward = ottawa_data.get("ward")
            ward_name = ottawa_data.get("ward_name")
            neighbourhood = ottawa_data.get("neighbourhood_name")
            neighbourhood_id = ottawa_data.get("neighbourhood_id")
        elif municipality in ["mississauga", "city of mississauga"]:
            ward = mississauga_data.get("ward")
            ward_name = mississauga_data.get("ward_name")
            neighbourhood = mississauga_data.get("neighbourhood_name")
            neighbourhood_id = mississauga_data.get("neighbourhood_id")
        elif municipality in ["hamilton", "city of hamilton"]:
            ward = hamilton_data.get("ward")
            ward_name = hamilton_data.get("ward_name")
            neighbourhood = hamilton_data.get("neighbourhood_name")
            neighbourhood_id = hamilton_data.get("neighbourhood_id")
        else:
            # Try to find data from any available provider
            ward = (toronto_data.get("ward") or ottawa_data.get("ward")
                    or mississauga_data.get("ward") or hamilton_data.get("ward"))
            ward_name = (toronto_data.get("ward_name") or ottawa_data.get("ward_name")
                        or mississauga_data.get("ward_name") or hamilton_data.get("ward_name"))
            neighbourhood = (toronto_data.get("neighbourhood_name") or ottawa_data.get("neighbourhood_name")
                            or mississauga_data.get("neighbourhood_name") or hamilton_data.get("neighbourhood_name"))
            neighbourhood_id = (toronto_data.get("neighbourhood_id") or ottawa_data.get("neighbourhood_id")
                               or mississauga_data.get("neighbourhood_id") or hamilton_data.get("neighbourhood_id"))

        return PropertyIdentification(
            address=base_info.get("address", ""),
            municipality=base_info.get("municipality", ""),
            latitude=base_info.get("latitude", 0.0),
            longitude=base_info.get("longitude", 0.0),
            pin=base_info.get("pin"),
            ward=ward,
            ward_name=ward_name,
            neighbourhood=neighbourhood,
            neighbourhood_id=neighbourhood_id,
        )

    def _merge_planning(
        self,
        provider_results: Dict[str, Dict[str, Any]],
    ) -> PlanningFramework:
        """Merge planning data from providers."""
        planning = PlanningFramework()

        # Get data from all municipal providers
        toronto_data = provider_results.get("Toronto Open Data", {})
        ottawa_data = provider_results.get("Ottawa Open Data", {})
        mississauga_data = provider_results.get("Mississauga Open Data", {})
        hamilton_data = provider_results.get("Hamilton Open Data", {})

        # Find first available municipal data (in priority order)
        if toronto_data and toronto_data.get("zoning_designation"):
            planning.zoning_designation = toronto_data.get("zoning_designation")
            planning.zoning_category = toronto_data.get("zoning_category")
            planning.permitted_uses = toronto_data.get("permitted_uses", [])
            planning.official_plan_designation = toronto_data.get("official_plan_designation")
            planning.official_plan_policies = toronto_data.get("official_plan_policies", [])
            planning.secondary_plan = toronto_data.get("secondary_plan")
            planning.secondary_plan_policies = toronto_data.get("secondary_plan_policies", [])
            planning.governing_bylaw = "569-2013 (Toronto)"

        elif ottawa_data and ottawa_data.get("zoning_designation"):
            planning.zoning_designation = ottawa_data.get("zoning_designation")
            planning.zoning_category = ottawa_data.get("zoning_category")
            planning.permitted_uses = ottawa_data.get("permitted_uses", [])
            planning.official_plan_designation = ottawa_data.get("official_plan_designation")
            planning.official_plan_policies = ottawa_data.get("official_plan_policies", [])
            planning.secondary_plan = ottawa_data.get("secondary_plan")
            planning.secondary_plan_policies = ottawa_data.get("secondary_plan_policies", [])
            planning.governing_bylaw = "2008-250 (Ottawa)"
            if ottawa_data.get("zoning_exception"):
                planning.holding_provisions = [f"Exception {ottawa_data['zoning_exception']}"]

        elif mississauga_data and mississauga_data.get("zoning_designation"):
            planning.zoning_designation = mississauga_data.get("zoning_designation")
            planning.zoning_category = mississauga_data.get("zoning_category")
            planning.permitted_uses = mississauga_data.get("permitted_uses", [])
            planning.official_plan_designation = mississauga_data.get("official_plan_designation")
            planning.official_plan_policies = mississauga_data.get("official_plan_policies", [])
            planning.secondary_plan = mississauga_data.get("secondary_plan")
            planning.secondary_plan_policies = mississauga_data.get("secondary_plan_policies", [])
            planning.governing_bylaw = "0225-2007 (Mississauga)"
            if mississauga_data.get("zoning_exception"):
                planning.holding_provisions = [f"Exception {mississauga_data['zoning_exception']}"]

        elif hamilton_data and hamilton_data.get("zoning_designation"):
            planning.zoning_designation = hamilton_data.get("zoning_designation")
            planning.zoning_category = hamilton_data.get("zoning_category")
            planning.permitted_uses = hamilton_data.get("permitted_uses", [])
            planning.official_plan_designation = hamilton_data.get("official_plan_designation")
            planning.official_plan_policies = hamilton_data.get("official_plan_policies", [])
            planning.secondary_plan = hamilton_data.get("secondary_plan")
            planning.secondary_plan_policies = hamilton_data.get("secondary_plan_policies", [])
            planning.governing_bylaw = "05-200 (Hamilton)"
            if hamilton_data.get("zoning_exception"):
                planning.holding_provisions = [f"Exception {hamilton_data['zoning_exception']}"]

        return planning

    def _merge_provincial_plans(
        self,
        provider_results: Dict[str, Dict[str, Any]],
    ) -> ProvincialPlans:
        """Merge provincial plan data from Ontario GeoHub."""
        plans = ProvincialPlans()

        geohub_data = provider_results.get("Ontario GeoHub", {})

        if geohub_data:
            plans.greenbelt_area = geohub_data.get("greenbelt_area", False)
            plans.greenbelt_designation = geohub_data.get("greenbelt_designation")
            plans.growth_plan_area = geohub_data.get("growth_plan_area")
            plans.oak_ridges_moraine = geohub_data.get("oak_ridges_moraine", False)
            plans.orm_designation = geohub_data.get("orm_designation")
            plans.niagara_escarpment = geohub_data.get("niagara_escarpment", False)
            plans.nec_designation = geohub_data.get("nec_designation")
            plans.natural_heritage = geohub_data.get("natural_heritage", False)

        return plans

    def _merge_neighbourhood(
        self,
        provider_results: Dict[str, Dict[str, Any]],
        base_info: Optional[Dict[str, Any]] = None,
    ) -> NeighbourhoodAnalysis:
        """Merge neighbourhood analysis from multiple sources."""
        neighbourhood = NeighbourhoodAnalysis()

        # Extract base coordinates for surrounding uses analysis
        base_lat = base_info.get("latitude", 0.0) if base_info else 0.0
        base_lon = base_info.get("longitude", 0.0) if base_info else 0.0

        # Get Toronto or Ottawa data for neighbourhood name
        toronto_data = provider_results.get("Toronto Open Data", {})
        ottawa_data = provider_results.get("Ottawa Open Data", {})

        if toronto_data and toronto_data.get("neighbourhood_name"):
            neighbourhood.neighbourhood_name = toronto_data.get("neighbourhood_name")
            neighbourhood.neighbourhood_id = toronto_data.get("neighbourhood_id")
            neighbourhood.neighbourhood_source = "City of Toronto Open Data"
        elif ottawa_data and ottawa_data.get("neighbourhood_name"):
            neighbourhood.neighbourhood_name = ottawa_data.get("neighbourhood_name")
            neighbourhood.neighbourhood_id = ottawa_data.get("neighbourhood_id")
            neighbourhood.neighbourhood_source = "City of Ottawa Open Data"

        # Phase 2: Census demographics data
        census_data = provider_results.get("Census Demographics", {})
        if census_data:
            neighbourhood.census_year = census_data.get("census_year", 2021)
            neighbourhood.population = census_data.get("population")

            # Format population growth
            if census_data.get("population_growth"):
                neighbourhood.population_growth = f"{census_data['population_growth']}%"

            # Format density
            if census_data.get("density_per_sqkm"):
                neighbourhood.density = f"{census_data['density_per_sqkm']:,.0f} per sq km"

            # Format income
            if census_data.get("median_income"):
                neighbourhood.median_income = f"${census_data['median_income']:,.0f}"

            # Format tenure
            if census_data.get("renter_percentage"):
                neighbourhood.renter_share = f"{census_data['renter_percentage']}%"

            # Format housing type
            if census_data.get("apartment_percentage"):
                neighbourhood.highrise_share = f"{census_data['apartment_percentage']}%"

            # Update neighbourhood name from census if not already set
            if not neighbourhood.neighbourhood_name and census_data.get("neighbourhood_name"):
                neighbourhood.neighbourhood_name = census_data.get("neighbourhood_name")

        # Get Overpass data for amenities
        overpass_data = provider_results.get("Overpass API", {})
        if overpass_data:
            # Convert amenity dicts to Amenity objects
            raw_amenities = overpass_data.get("amenities", [])
            neighbourhood.amenities = [
                Amenity(
                    name=a.get("name", "Unknown"),
                    type=a.get("type", "unknown"),
                    category=a.get("category", "other"),
                    distance_m=a.get("distance_m", 0),
                    address=a.get("address"),
                    lat=a.get("lat"),
                    lon=a.get("lon"),
                )
                for a in raw_amenities[:30]  # Limit to 30 amenities
            ]

            neighbourhood.transit_accessibility = overpass_data.get(
                "transit_accessibility", ""
            )
            neighbourhood.walkability_notes = overpass_data.get("walkability_notes", "")

            # Generate character description from amenities
            summary = overpass_data.get("summary", {})
            neighbourhood.character_description = self._generate_character_description(
                summary, neighbourhood.neighbourhood_name
            )

            # Generate surrounding uses from amenity data
            neighbourhood.surrounding_uses = self._analyze_surrounding_uses(
                raw_amenities, base_lat, base_lon
            )

        return neighbourhood

    def _analyze_surrounding_uses(
        self,
        amenities: List[Dict[str, Any]],
        origin_lat: float,
        origin_lon: float,
    ) -> List[SurroundingUse]:
        """
        Analyze amenities to determine surrounding land uses by direction.

        Uses bearing calculation to categorize amenities into cardinal directions,
        then determines dominant land use for each direction.

        Args:
            amenities: List of amenity dictionaries with lat/lon
            origin_lat: Subject property latitude
            origin_lon: Subject property longitude

        Returns:
            List of SurroundingUse objects for each cardinal direction
        """
        # Cardinal directions with bearing ranges
        directions = {
            "N": (337.5, 22.5),
            "NE": (22.5, 67.5),
            "E": (67.5, 112.5),
            "SE": (112.5, 157.5),
            "S": (157.5, 202.5),
            "SW": (202.5, 247.5),
            "W": (247.5, 292.5),
            "NW": (292.5, 337.5),
        }

        # Land use mappings from amenity categories
        category_to_land_use = {
            "education": "Institutional",
            "healthcare": "Institutional",
            "recreation": "Parks/Open Space",
            "shopping": "Commercial",
            "transit": "Transportation",
            "services": "Commercial/Institutional",
            "food": "Commercial",
            "other": "Mixed Use",
        }

        # Collect amenities by direction
        direction_amenities: Dict[str, List[Dict]] = {d: [] for d in directions}

        for amenity in amenities:
            a_lat = amenity.get("lat")
            a_lon = amenity.get("lon")
            if not (a_lat and a_lon):
                continue

            bearing = self._calculate_bearing(origin_lat, origin_lon, a_lat, a_lon)
            direction = self._bearing_to_direction(bearing, directions)
            direction_amenities[direction].append(amenity)

        # Determine dominant land use for each direction
        surrounding_uses = []
        for direction in ["N", "E", "S", "W"]:  # Primary cardinals only for cleaner output
            amenities_in_dir = direction_amenities[direction]

            if not amenities_in_dir:
                # Check adjacent directions
                adjacent = {
                    "N": ["NE", "NW"],
                    "E": ["NE", "SE"],
                    "S": ["SE", "SW"],
                    "W": ["NW", "SW"],
                }
                for adj_dir in adjacent[direction]:
                    amenities_in_dir.extend(direction_amenities[adj_dir])

            if amenities_in_dir:
                # Count categories
                category_counts: Dict[str, int] = {}
                for a in amenities_in_dir:
                    cat = a.get("category", "other")
                    category_counts[cat] = category_counts.get(cat, 0) + 1

                # Find dominant category
                dominant_cat = max(category_counts, key=category_counts.get) if category_counts else "other"
                land_use = category_to_land_use.get(dominant_cat, "Mixed Use")

                # Build description from nearest amenities
                nearest = sorted(amenities_in_dir, key=lambda x: x.get("distance_m", 9999))[:3]
                descriptions = [a.get("name", "Unknown") for a in nearest if a.get("name")]
                description = ", ".join(descriptions) if descriptions else f"{land_use} uses"

                surrounding_uses.append(
                    SurroundingUse(
                        direction=direction,
                        land_use=land_use,
                        description=description,
                    )
                )
            else:
                # No data for this direction
                surrounding_uses.append(
                    SurroundingUse(
                        direction=direction,
                        land_use="Unknown",
                        description="Insufficient data",
                    )
                )

        return surrounding_uses

    def _calculate_bearing(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:
        """
        Calculate bearing from point 1 to point 2.

        Args:
            lat1, lon1: Origin coordinates
            lat2, lon2: Destination coordinates

        Returns:
            Bearing in degrees (0-360)
        """
        from math import radians, sin, cos

        lat1_r = radians(lat1)
        lat2_r = radians(lat2)
        dlon = radians(lon2 - lon1)

        x = sin(dlon) * cos(lat2_r)
        y = cos(lat1_r) * sin(lat2_r) - sin(lat1_r) * cos(lat2_r) * cos(dlon)

        bearing = degrees(atan2(x, y))
        return (bearing + 360) % 360

    def _bearing_to_direction(
        self,
        bearing: float,
        directions: Dict[str, Tuple[float, float]],
    ) -> str:
        """
        Convert bearing to cardinal/intercardinal direction.

        Args:
            bearing: Bearing in degrees (0-360)
            directions: Dict mapping direction to (min, max) bearing range

        Returns:
            Direction string (N, NE, E, etc.)
        """
        for direction, (min_b, max_b) in directions.items():
            if direction == "N":
                # N spans 337.5-360 and 0-22.5
                if bearing >= min_b or bearing < max_b:
                    return direction
            elif min_b <= bearing < max_b:
                return direction
        return "N"  # Default

    def _generate_character_description(
        self,
        amenity_summary: Dict[str, Dict],
        neighbourhood_name: Optional[str],
    ) -> str:
        """Generate a character description from amenity data."""
        parts = []

        if neighbourhood_name:
            parts.append(f"Located in {neighbourhood_name}.")

        # Describe based on amenity mix
        categories_present = list(amenity_summary.keys())

        if "education" in categories_present:
            edu_count = amenity_summary["education"].get("count", 0)
            parts.append(f"Educational facilities nearby ({edu_count} within search radius).")

        if "shopping" in categories_present:
            shop_count = amenity_summary["shopping"].get("count", 0)
            nearest = amenity_summary["shopping"].get("nearest_m")
            if nearest and nearest <= 500:
                parts.append(f"Convenient shopping access with {shop_count} options nearby.")

        if "recreation" in categories_present:
            rec_count = amenity_summary["recreation"].get("count", 0)
            parts.append(f"Recreation amenities available ({rec_count} parks/facilities).")

        if "transit" in categories_present:
            transit_count = amenity_summary["transit"].get("count", 0)
            parts.append(f"Transit-served location with {transit_count} stops nearby.")

        if not parts:
            return "Neighbourhood character assessment not available from current data sources."

        return " ".join(parts)

    def _merge_environmental(
        self,
        provider_results: Dict[str, Dict[str, Any]],
    ) -> EnvironmentalFactors:
        """Merge environmental factors from providers."""
        env = EnvironmentalFactors()

        # Phase 2: Heritage data
        heritage_data = provider_results.get("Heritage Registry", {})
        if heritage_data:
            env.heritage_designated = heritage_data.get("heritage_designated", False)
            env.heritage_type = heritage_data.get("designation_type")
            # Add heritage district info if in HCD
            hcd = heritage_data.get("heritage_district")
            if hcd and hcd.get("in_hcd"):
                env.heritage_designated = True
                env.heritage_type = "Part V - Heritage Conservation District"

        # Phase 2: Brownfields ESR data
        brownfields_data = provider_results.get("Brownfields ESR", {})
        if brownfields_data:
            env.brownfield_record = brownfields_data.get("brownfield_record", False)
            env.rsc_number = brownfields_data.get("rsc_number")

        # Phase 2: TRCA Conservation data
        trca_data = provider_results.get("TRCA Conservation", {})
        if trca_data:
            env.floodplain = trca_data.get("floodplain", False)
            env.floodplain_type = trca_data.get("floodplain_type")
            env.wetland = trca_data.get("wetland", False)
            env.valley_corridor = trca_data.get("valley_corridor", False) or trca_data.get("in_regulated_area", False)

        return env

    def _merge_market(
        self,
        provider_results: Dict[str, Dict[str, Any]],
    ) -> MarketContext:
        """Merge market context from providers."""
        # For MVP, return default values (MPAC in Phase 3)
        return MarketContext(
            development_activity="Development activity data not available in current version."
        )

    def _merge_transport(
        self,
        provider_results: Dict[str, Dict[str, Any]],
    ) -> TransportInfo:
        """Merge transportation info from providers."""
        transport = TransportInfo()

        # Phase 2: GTFS transit data (more detailed than Overpass)
        gtfs_data = provider_results.get("Transit GTFS", {})
        if gtfs_data:
            # Rapid transit (subway/LRT)
            if gtfs_data.get("nearest_subway"):
                subway = gtfs_data["nearest_subway"]
                transport.rapid_transit = f"{subway.get('name')} ({subway.get('distance_m')}m)"
            elif gtfs_data.get("nearest_lrt"):
                lrt = gtfs_data["nearest_lrt"]
                transport.rapid_transit = f"{lrt.get('name')} ({lrt.get('distance_m')}m)"

            # Regional transit (GO)
            if gtfs_data.get("nearest_go_station"):
                go = gtfs_data["nearest_go_station"]
                transport.regional_transit = f"{go.get('name')} ({go.get('distance_m')}m)"

            # Transit score as walk_transit_bike_scores
            if gtfs_data.get("transit_score"):
                transport.walk_transit_bike_scores = f"Transit Score: {gtfs_data['transit_score']}/100"

        # Fallback to Overpass data if GTFS not available
        if not transport.rapid_transit:
            overpass_data = provider_results.get("Overpass API", {})
            if overpass_data:
                transport.rapid_transit = self._extract_rapid_transit(overpass_data)

        return transport

    def _extract_rapid_transit(self, overpass_data: Dict[str, Any]) -> Optional[str]:
        """Extract rapid transit info from Overpass amenities."""
        amenities = overpass_data.get("amenities", [])

        # Find subway/rail stations
        transit_stations = [
            a for a in amenities
            if a.get("type") in ["station", "subway_entrance", "train_station"]
        ]

        if transit_stations:
            closest = min(transit_stations, key=lambda x: x.get("distance_m", 9999))
            return f"{closest.get('name', 'Transit station')} ({closest.get('distance_m')}m)"

        return None

    def _generate_regional_context(self, base_info: Dict[str, Any]) -> str:
        """Generate regional context description."""
        municipality = base_info.get("municipality", "")

        contexts = {
            "Toronto": "The subject property is located in Toronto, Ontario's capital city and largest municipality with a population of approximately 2.9 million (2021 Census). Toronto serves as the economic centre of Canada and is characterized by diverse neighbourhoods, extensive transit infrastructure, and a mix of residential, commercial, and employment uses.",
            "Mississauga": "The subject property is located in Mississauga, Ontario's sixth-largest city and part of the Greater Toronto Area (GTA). Mississauga has a population of approximately 717,000 and serves as a major employment centre with significant office, industrial, and retail development.",
            "Ottawa": "The subject property is located in Ottawa, Ontario's second-largest city and the national capital. Ottawa has a population of approximately 1 million and is characterized by government employment, technology sector growth, and bilingual heritage.",
            "Brampton": "The subject property is located in Brampton, a rapidly growing city in the GTA with a population of approximately 656,000. Brampton features significant industrial and logistics development along major highway corridors.",
            "Hamilton": "The subject property is located in Hamilton, a city at the western end of Lake Ontario with a population of approximately 570,000. Hamilton has transitioned from heavy manufacturing to a diversified economy including healthcare, education, and technology.",
        }

        return contexts.get(
            municipality,
            f"The subject property is located in {municipality}, Ontario."
        )

    def get_conflicts(self) -> List[str]:
        """Get list of data conflicts encountered during merge."""
        return self.conflicts
