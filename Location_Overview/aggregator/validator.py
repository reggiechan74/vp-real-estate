"""
Completeness Validator Module

Validates that LocationOverview contains required data for CUSPAP compliance.
Flags missing data and generates warnings.
"""

from typing import List, Tuple
from dataclasses import fields

from ..schemas.location_data import LocationOverview


class CompletenessValidator:
    """
    Validates completeness of LocationOverview for CUSPAP compliance.

    Checks for:
    - Required fields populated
    - Minimum data coverage
    - CUSPAP-required sections
    """

    # Fields that must be populated for minimum viable report
    REQUIRED_FIELDS = [
        "property_id.address",
        "property_id.municipality",
        "property_id.latitude",
        "property_id.longitude",
    ]

    # Fields that should be populated if data is available
    RECOMMENDED_FIELDS = [
        "planning.zoning_designation",
        "provincial_plans.growth_plan_area",
        "neighbourhood.transit_accessibility",
    ]

    # CUSPAP minimum requirements
    CUSPAP_REQUIREMENTS = [
        ("property_id.address", "Property address is required for CUSPAP compliance"),
        ("planning.zoning_designation", "Zoning designation should be included per CUSPAP"),
        ("data_sources", "Data sources must be documented for CUSPAP compliance"),
    ]

    def validate(self, overview: LocationOverview) -> Tuple[bool, List[str], List[str]]:
        """
        Validate LocationOverview completeness.

        Args:
            overview: LocationOverview to validate

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        errors = []
        warnings = []

        # Check required fields
        for field_path in self.REQUIRED_FIELDS:
            value = self._get_nested_field(overview, field_path)
            if value is None or value == "" or value == 0:
                errors.append(f"Required field missing: {field_path}")

        # Check recommended fields
        for field_path in self.RECOMMENDED_FIELDS:
            value = self._get_nested_field(overview, field_path)
            if value is None or value == "":
                warnings.append(f"Recommended field missing: {field_path}")

        # Check CUSPAP requirements
        for field_path, message in self.CUSPAP_REQUIREMENTS:
            value = self._get_nested_field(overview, field_path)
            if value is None or value == "" or (isinstance(value, list) and len(value) == 0):
                warnings.append(message)

        # Check data sources
        if not overview.data_sources:
            warnings.append("No data sources documented - add sources for traceability")

        # Check for critical warnings in the overview itself
        if overview.errors:
            for error in overview.errors:
                errors.append(f"Provider error: {error}")

        is_valid = len(errors) == 0

        return is_valid, errors, warnings

    def _get_nested_field(self, obj, field_path: str):
        """
        Get a nested field value using dot notation.

        Args:
            obj: Object to get field from
            field_path: Dot-separated path (e.g., "property_id.address")

        Returns:
            Field value or None
        """
        parts = field_path.split(".")
        current = obj

        for part in parts:
            if hasattr(current, part):
                current = getattr(current, part)
            elif isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        return current

    def calculate_completeness_score(self, overview: LocationOverview) -> float:
        """
        Calculate a completeness score (0-100).

        Args:
            overview: LocationOverview to score

        Returns:
            Completeness score as percentage
        """
        total_checks = 0
        passed_checks = 0

        # Score required fields (weight: 2x)
        for field_path in self.REQUIRED_FIELDS:
            total_checks += 2
            value = self._get_nested_field(overview, field_path)
            if value is not None and value != "" and value != 0:
                passed_checks += 2

        # Score recommended fields (weight: 1x)
        for field_path in self.RECOMMENDED_FIELDS:
            total_checks += 1
            value = self._get_nested_field(overview, field_path)
            if value is not None and value != "":
                passed_checks += 1

        # Score data sources
        total_checks += 1
        if overview.data_sources:
            passed_checks += 1

        # Score amenities
        total_checks += 1
        if overview.neighbourhood.amenities:
            passed_checks += 1

        # Score provincial plans
        total_checks += 1
        if overview.provincial_plans.growth_plan_area:
            passed_checks += 1

        if total_checks == 0:
            return 0.0

        return (passed_checks / total_checks) * 100

    def get_missing_sections(self, overview: LocationOverview) -> List[str]:
        """
        Get list of sections with missing data.

        Args:
            overview: LocationOverview to check

        Returns:
            List of section names with missing data
        """
        missing = []

        # Check planning
        if not overview.planning.zoning_designation:
            missing.append("Zoning")
        if not overview.planning.official_plan_designation:
            missing.append("Official Plan")

        # Check provincial plans (check if any are populated)
        provincial = overview.provincial_plans
        if not any([
            provincial.greenbelt_area,
            provincial.growth_plan_area,
            provincial.oak_ridges_moraine,
            provincial.niagara_escarpment,
        ]):
            missing.append("Provincial Plans")

        # Check neighbourhood
        if not overview.neighbourhood.amenities:
            missing.append("Amenities")
        if not overview.neighbourhood.transit_accessibility:
            missing.append("Transit")

        # Check environmental
        # (Most environmental data is false by default, so we don't flag it as missing)

        return missing
