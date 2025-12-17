"""
Location Overview Main Module

Entry point for the /location-overview slash command.
Orchestrates geocoding, provider queries, and report generation.
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from pathlib import Path

from .config import get_config, Config
from .input.parser import parse_input, InputType
from .input.normalizer import normalize_address
from .input.municipality_detector import detect_municipality
from .input.validators import validate_coordinates, validate_input
from .geocoding.nominatim import NominatimGeocoder, GeocodingResult, GeocodingError
from .geocoding.cache import GeocodingCache
from .providers.ontario_geohub import OntarioGeoHubProvider
from .providers.toronto_opendata import TorontoOpenDataProvider
from .providers.overpass import OverpassProvider
# Phase 2 providers
from .providers.heritage import HeritageProvider
from .providers.brownfields import BrownfieldsProvider
from .providers.trca import TRCAProvider
from .providers.ottawa_arcgis import OttawaArcGISProvider
from .providers.gtfs import GTFSProvider
from .providers.census import CensusProvider
from .aggregator.engine import AggregationEngine, AggregationResult
from .aggregator.merger import ResultMerger
from .aggregator.validator import CompletenessValidator
from .schemas.location_data import LocationOverview, create_empty_location_overview
from .output.formatter import ReportGenerator


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class LocationOverviewResult:
    """Result from location overview generation."""

    success: bool
    report_path: Optional[str] = None
    overview: Optional[LocationOverview] = None
    summary: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    warnings: list = None
    execution_time_ms: float = 0.0

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


async def location_overview(
    input_str: str,
    output_format: str = "markdown",
    save_report: bool = True,
    config: Optional[Config] = None,
) -> LocationOverviewResult:
    """
    Generate a location overview for a PIN or address.

    This is the main entry point for the /location-overview command.

    Args:
        input_str: PIN (9 digits) or municipal address
        output_format: "markdown" or "json"
        save_report: Whether to save the report to file
        config: Optional configuration override

    Returns:
        LocationOverviewResult with report path and/or data

    Example:
        >>> result = await location_overview("100 Queen Street West, Toronto")
        >>> print(result.report_path)
        Reports/2025-01-15_143022_location_overview_100_queen_street_west_toronto.md
    """
    import time

    start_time = time.time()
    config = config or get_config()
    warnings = []

    try:
        # Step 1: Parse and validate input
        logger.info(f"Processing input: {input_str}")
        parsed = parse_input(input_str)

        if not parsed.is_valid:
            return LocationOverviewResult(
                success=False,
                error=f"Invalid input: {parsed.validation_message}",
                execution_time_ms=(time.time() - start_time) * 1000,
            )

        # Step 2: Handle PIN vs Address
        if parsed.input_type == InputType.PIN:
            # For PIN, we would need to look up coordinates via OnLand or Teranet
            # For MVP, we'll return an error as this requires paid services
            return LocationOverviewResult(
                success=False,
                error="PIN lookup requires OnLand/Teranet integration (Phase 3). Please provide a municipal address.",
                execution_time_ms=(time.time() - start_time) * 1000,
            )

        # Step 3: Normalize address
        normalized_address = normalize_address(parsed.value)
        logger.info(f"Normalized address: {normalized_address}")

        # Step 4: Geocode address
        geocoder = NominatimGeocoder(
            user_agent=config.geocoding.nominatim_user_agent,
            timeout=config.geocoding.nominatim_timeout,
        )

        try:
            geocode_result = await geocoder.geocode(normalized_address)
        except GeocodingError as e:
            return LocationOverviewResult(
                success=False,
                error=f"Geocoding failed: {str(e)}",
                execution_time_ms=(time.time() - start_time) * 1000,
            )

        if geocode_result is None:
            return LocationOverviewResult(
                success=False,
                error=f"Address not found: {parsed.value}. Please check the address and try again.",
                execution_time_ms=(time.time() - start_time) * 1000,
            )

        lat, lon = geocode_result.latitude, geocode_result.longitude
        logger.info(f"Geocoded to: {lat}, {lon}")

        # Step 5: Validate coordinates are in Ontario
        coord_validation = validate_coordinates(lat, lon)
        if not coord_validation.is_valid:
            return LocationOverviewResult(
                success=False,
                error=f"Location not in Ontario: {coord_validation.errors[0]}",
                execution_time_ms=(time.time() - start_time) * 1000,
            )
        warnings.extend(coord_validation.warnings)

        # Step 6: Detect municipality
        municipality, data_provider = detect_municipality(lat, lon)
        logger.info(f"Detected municipality: {municipality}")

        # Step 7: Initialize and run providers
        engine = AggregationEngine(timeout=config.default_timeout)

        # Phase 1 providers (MVP) - always enabled
        engine.register_provider(OntarioGeoHubProvider())
        engine.register_provider(TorontoOpenDataProvider())
        engine.register_provider(OverpassProvider())

        # Phase 2 providers (Enhanced) - can be disabled via config
        if config.providers.heritage_enabled:
            engine.register_provider(HeritageProvider())
        if config.providers.brownfields_enabled:
            engine.register_provider(BrownfieldsProvider())
        if config.providers.trca_enabled:
            engine.register_provider(TRCAProvider())
        if config.providers.ottawa_enabled:
            engine.register_provider(OttawaArcGISProvider())
        if config.providers.gtfs_enabled:
            engine.register_provider(GTFSProvider())
        if config.providers.census_enabled:
            engine.register_provider(CensusProvider())

        aggregation_result = await engine.execute(lat, lon, municipality)
        logger.info(
            f"Providers: {len(aggregation_result.providers_succeeded)} succeeded, "
            f"{len(aggregation_result.providers_failed)} failed"
        )

        warnings.extend(aggregation_result.warnings)

        # Step 8: Merge results into LocationOverview
        merger = ResultMerger()
        overview = merger.merge(
            aggregation_result.data,
            {
                "address": geocode_result.display_name,
                "latitude": lat,
                "longitude": lon,
                "municipality": municipality,
                "pin": None,  # Not available for address input
            },
        )

        # Add provider errors as warnings
        for error in aggregation_result.errors:
            overview.add_warning(error)

        # Step 9: Validate completeness
        validator = CompletenessValidator()
        is_valid, validation_errors, validation_warnings = validator.validate(overview)
        warnings.extend(validation_warnings)

        completeness_score = validator.calculate_completeness_score(overview)
        logger.info(f"Completeness score: {completeness_score:.1f}%")

        # Step 10: Generate report
        generator = ReportGenerator(
            output_dir=config.output.reports_directory,
        )

        report_path = None
        if save_report:
            if output_format == "json":
                report_path = generator.generate_json(overview)
            else:
                report_path = generator.generate_markdown(overview)

            logger.info(f"Report saved to: {report_path}")

        # Generate summary
        summary = generator.get_report_summary(overview)
        summary["completeness_score"] = completeness_score

        execution_time = (time.time() - start_time) * 1000

        return LocationOverviewResult(
            success=True,
            report_path=report_path,
            overview=overview,
            summary=summary,
            warnings=warnings,
            execution_time_ms=execution_time,
        )

    except Exception as e:
        logger.exception(f"Error generating location overview: {e}")
        return LocationOverviewResult(
            success=False,
            error=f"Internal error: {str(e)}",
            execution_time_ms=(time.time() - start_time) * 1000,
        )


def run_location_overview(
    input_str: str,
    output_format: str = "markdown",
    save_report: bool = True,
) -> LocationOverviewResult:
    """
    Synchronous wrapper for location_overview.

    Args:
        input_str: PIN or address
        output_format: "markdown" or "json"
        save_report: Whether to save report

    Returns:
        LocationOverviewResult
    """
    return asyncio.run(
        location_overview(input_str, output_format, save_report)
    )


# CLI interface
def main():
    """Command-line interface for location overview."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate location overview for Ontario properties",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python -m Location_Overview.main "100 Queen Street West, Toronto"
    python -m Location_Overview.main --format json "150 King Street West, Toronto"
    python -m Location_Overview.main --no-save "123 Main Street, Mississauga"
        """,
    )

    parser.add_argument(
        "input",
        help="PIN (9 digits) or municipal address",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save report to file",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    print(f"\n🔍 Generating location overview for: {args.input}\n")

    result = run_location_overview(
        args.input,
        output_format=args.format,
        save_report=not args.no_save,
    )

    if result.success:
        print(f"✅ Success!")
        print(f"   Execution time: {result.execution_time_ms:.0f}ms")

        if result.report_path:
            print(f"   Report saved to: {result.report_path}")

        if result.summary:
            print(f"\n📊 Summary:")
            print(f"   Address: {result.summary.get('address')}")
            print(f"   Municipality: {result.summary.get('municipality')}")
            print(f"   Zoning: {result.summary.get('zoning', 'N/A')}")
            print(f"   Greenbelt: {'Yes' if result.summary.get('greenbelt') else 'No'}")
            print(f"   Growth Plan: {result.summary.get('growth_plan', 'N/A')}")
            print(f"   Amenities found: {result.summary.get('amenities_count', 0)}")
            print(f"   Completeness: {result.summary.get('completeness_score', 0):.1f}%")

        if result.warnings:
            print(f"\n⚠️ Warnings ({len(result.warnings)}):")
            for w in result.warnings[:5]:
                print(f"   - {w}")
            if len(result.warnings) > 5:
                print(f"   ... and {len(result.warnings) - 5} more")
    else:
        print(f"❌ Failed: {result.error}")

    return 0 if result.success else 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
