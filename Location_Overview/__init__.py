"""
Location Overview Module

A slash command that generates comprehensive location overviews for Ontario properties,
suitable for inclusion in CUSPAP-compliant appraisal reports.

Features:
- Dual input support: 9-digit Ontario PIN or municipal address
- Multi-source integration: Ontario GeoHub, Toronto Open Data, Overpass API
- Provincial plan detection: Greenbelt, Growth Plan, Oak Ridges Moraine
- Zoning analysis: designation, permitted uses, Official Plan policies
- Neighbourhood analysis: amenities, transit, surrounding uses
- CUSPAP compliance: formatted per appraisal report standards

Usage:
    /location-overview <PIN|address>
    /location-overview 100 Queen Street West, Toronto
    /location-overview 123456789
"""

__version__ = "1.0.0"
__author__ = "Lease Abstract Toolkit"

from .main import location_overview, LocationOverviewResult

__all__ = ["location_overview", "LocationOverviewResult", "__version__"]
