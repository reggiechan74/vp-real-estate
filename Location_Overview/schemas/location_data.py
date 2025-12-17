"""
Location Data Models Module

Dataclasses for structured location overview data.
These models represent the complete data structure for a location overview report.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class PropertyIdentification:
    """
    Property identification information.

    Contains the basic identifying information for a property.
    """

    address: str
    municipality: str
    latitude: float
    longitude: float
    pin: Optional[str] = None
    legal_description: Optional[str] = None
    ward: Optional[str] = None
    ward_name: Optional[str] = None
    neighbourhood: Optional[str] = None
    neighbourhood_id: Optional[int] = None


@dataclass
class PlanningFramework:
    """
    Planning and zoning information.

    Contains Official Plan and zoning by-law designations.
    """

    zoning_designation: Optional[str] = None
    zoning_category: Optional[str] = None
    permitted_uses: List[str] = field(default_factory=list)
    official_plan_designation: Optional[str] = None
    official_plan_policies: List[str] = field(default_factory=list)
    secondary_plan: Optional[str] = None
    secondary_plan_policies: List[str] = field(default_factory=list)
    secondary_plan_amendment: Optional[str] = None
    site_plan_control: bool = False
    holding_provisions: List[str] = field(default_factory=list)
    governing_bylaw: Optional[str] = None
    major_projects: Optional[str] = None


@dataclass
class ProvincialPlans:
    """
    Provincial plan overlay information.

    Contains status for Greenbelt, Growth Plan, Oak Ridges Moraine,
    Niagara Escarpment, and Natural Heritage System.
    """

    greenbelt_area: bool = False
    greenbelt_designation: Optional[str] = None
    growth_plan_area: Optional[str] = None  # Built-up, Designated Greenfield, Rural
    oak_ridges_moraine: bool = False
    orm_designation: Optional[str] = None
    niagara_escarpment: bool = False
    nec_designation: Optional[str] = None
    natural_heritage: bool = False


@dataclass
class SurroundingUse:
    """
    Surrounding land use in a cardinal direction.
    """

    direction: str  # N, S, E, W, NE, NW, SE, SW
    land_use: str
    description: str


@dataclass
class Amenity:
    """
    A nearby amenity (school, hospital, park, transit, shopping, etc.).
    """

    name: str
    type: str  # school, hospital, park, transit, shopping, etc.
    category: str  # education, healthcare, recreation, transit, shopping, services
    distance_m: int
    address: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None


@dataclass
class TransportInfo:
    """
    Transportation and access information.
    """

    rapid_transit: Optional[str] = None
    regional_transit: Optional[str] = None
    cycling_network: Optional[str] = None
    walk_transit_bike_scores: Optional[str] = None


@dataclass
class NeighbourhoodAnalysis:
    """
    Neighbourhood context and amenity analysis.
    """

    neighbourhood_name: Optional[str] = None
    neighbourhood_id: Optional[int] = None
    neighbourhood_source: Optional[str] = None
    census_year: Optional[int] = None
    population: Optional[int] = None
    population_growth: Optional[str] = None
    density: Optional[str] = None
    median_income: Optional[str] = None
    renter_share: Optional[str] = None
    highrise_share: Optional[str] = None
    profile_notes: Optional[str] = None
    character_description: str = ""
    surrounding_uses: List[SurroundingUse] = field(default_factory=list)
    amenities: List[Amenity] = field(default_factory=list)
    transit_accessibility: str = ""
    walkability_notes: str = ""
    bia_note: Optional[str] = None
    parks_note: Optional[str] = None


@dataclass
class EnvironmentalFactors:
    """
    Environmental constraints and designations.
    """

    floodplain: bool = False
    floodplain_type: Optional[str] = None  # Regulatory, Special Policy Area
    wetland: bool = False
    valley_corridor: bool = False
    heritage_designated: bool = False
    heritage_type: Optional[str] = None  # Part IV, Part V (HCD)
    brownfield_record: bool = False
    rsc_number: Optional[str] = None
    servicing: Dict[str, bool] = field(
        default_factory=lambda: {
            "water": True,
            "sewer": True,
            "gas": True,
            "hydro": True,
        }
    )


@dataclass
class MarketContext:
    """
    Market and assessment context.
    """

    assessment_value: Optional[float] = None
    assessment_year: Optional[int] = None
    property_class: Optional[str] = None
    recent_permits: List[Dict[str, Any]] = field(default_factory=list)
    development_activity: str = ""
    development_activity_details: str = ""


@dataclass
class DataSource:
    """
    Information about a data source used in the report.
    """

    name: str
    type: str  # API, scraped, third-party
    last_updated: Optional[str] = None
    link: Optional[str] = None


@dataclass
class LocationOverview:
    """
    Complete location overview data model.

    This is the primary data structure that contains all information
    for a location overview report.
    """

    property_id: PropertyIdentification
    planning: PlanningFramework
    provincial_plans: ProvincialPlans
    neighbourhood: NeighbourhoodAnalysis
    environmental: EnvironmentalFactors
    market: MarketContext
    transport: TransportInfo = field(default_factory=TransportInfo)
    regional_context: str = ""

    generated_at: datetime = field(default_factory=datetime.now)
    data_sources: List[DataSource] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the location overview
        """
        from dataclasses import asdict

        data = asdict(self)
        # Convert datetime to ISO string
        data["generated_at"] = self.generated_at.isoformat()
        return data

    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        if warning not in self.warnings:
            self.warnings.append(warning)

    def add_error(self, error: str) -> None:
        """Add an error message."""
        if error not in self.errors:
            self.errors.append(error)

    def add_data_source(
        self,
        name: str,
        source_type: str,
        last_updated: Optional[str] = None,
        link: Optional[str] = None,
    ) -> None:
        """Add a data source to the list."""
        source = DataSource(
            name=name,
            type=source_type,
            last_updated=last_updated,
            link=link,
        )
        # Avoid duplicates
        if not any(s.name == name for s in self.data_sources):
            self.data_sources.append(source)


def create_empty_location_overview(
    address: str,
    lat: float,
    lon: float,
    municipality: str,
) -> LocationOverview:
    """
    Create an empty LocationOverview with basic property identification.

    Args:
        address: Property address
        lat: Latitude
        lon: Longitude
        municipality: Municipality name

    Returns:
        LocationOverview with property_id populated
    """
    return LocationOverview(
        property_id=PropertyIdentification(
            address=address,
            municipality=municipality,
            latitude=lat,
            longitude=lon,
        ),
        planning=PlanningFramework(),
        provincial_plans=ProvincialPlans(),
        neighbourhood=NeighbourhoodAnalysis(),
        environmental=EnvironmentalFactors(),
        market=MarketContext(),
        transport=TransportInfo(),
    )
