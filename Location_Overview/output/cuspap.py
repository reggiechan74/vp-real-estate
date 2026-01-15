"""
CUSPAP Compliance Validator Module

Validates LocationOverview reports against CUSPAP (Canadian Uniform Standards
of Professional Appraisal Practice) requirements for location descriptions.

CUSPAP Section 7.2.2 requires location descriptions to include:
- Legal description (or reference)
- Municipal address
- Property identification (PIN, Roll Number, etc.)
- Neighbourhood and surrounding area description
- Relevant planning/zoning information
- Environmental factors affecting value

This module checks report completeness and flags missing elements.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class ComplianceLevel(Enum):
    """CUSPAP compliance level assessment."""

    FULL = "full"  # All required elements present
    SUBSTANTIAL = "substantial"  # Most required elements, minor gaps
    PARTIAL = "partial"  # Significant gaps
    INSUFFICIENT = "insufficient"  # Missing critical elements


@dataclass
class ComplianceIssue:
    """A single compliance issue identified."""

    category: str
    element: str
    severity: str  # "required", "recommended", "optional"
    message: str
    suggestion: Optional[str] = None


@dataclass
class CUSPAPComplianceReport:
    """CUSPAP compliance validation report."""

    compliance_level: ComplianceLevel
    score: float  # 0-100
    issues: List[ComplianceIssue] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "compliance_level": self.compliance_level.value,
            "score": self.score,
            "issues": [
                {
                    "category": i.category,
                    "element": i.element,
                    "severity": i.severity,
                    "message": i.message,
                    "suggestion": i.suggestion,
                }
                for i in self.issues
            ],
            "warnings": self.warnings,
            "recommendations": self.recommendations,
        }


class CUSPAPValidator:
    """
    Validates location overview data against CUSPAP requirements.

    CUSPAP 2024 Section 7.2.2 Location Description Requirements:
    1. Identification of the property (address, legal description, PIN)
    2. Description of the neighbourhood and immediate surroundings
    3. Disclosure of zoning and permitted uses
    4. Environmental factors that may affect value
    5. Access and transportation
    6. Services and utilities availability
    """

    # Required elements (must be present)
    REQUIRED_ELEMENTS = {
        "property_id.address": "Municipal address",
        "property_id.municipality": "Municipality name",
        "property_id.latitude": "Geographic coordinates (latitude)",
        "property_id.longitude": "Geographic coordinates (longitude)",
        "planning.zoning_designation": "Zoning designation",
    }

    # Recommended elements (should be present where available)
    RECOMMENDED_ELEMENTS = {
        "property_id.neighbourhood": "Neighbourhood identification",
        "planning.official_plan_designation": "Official Plan designation",
        "neighbourhood.character_description": "Neighbourhood character description",
        "neighbourhood.surrounding_uses": "Surrounding land uses",
        "environmental.heritage_designated": "Heritage designation status",
        "transport.rapid_transit": "Transit accessibility",
    }

    # Optional elements (enhance report quality)
    OPTIONAL_ELEMENTS = {
        "property_id.pin": "Property Identification Number (PIN)",
        "property_id.legal_description": "Legal description",
        "planning.secondary_plan": "Secondary Plan",
        "planning.permitted_uses": "Permitted uses",
        "provincial_plans.greenbelt_area": "Provincial plan overlays",
        "environmental.floodplain": "Floodplain status",
        "environmental.brownfield_record": "Environmental Site Registry status",
        "market.assessment_value": "Assessment value",
    }

    # Element weights for scoring
    WEIGHTS = {
        "required": 3.0,
        "recommended": 2.0,
        "optional": 1.0,
    }

    def validate(self, location_overview) -> CUSPAPComplianceReport:
        """
        Validate a LocationOverview against CUSPAP requirements.

        Args:
            location_overview: LocationOverview object to validate

        Returns:
            CUSPAPComplianceReport with compliance assessment
        """
        issues = []
        present_count = {"required": 0, "recommended": 0, "optional": 0}
        total_count = {"required": 0, "recommended": 0, "optional": 0}

        # Check required elements
        for path, description in self.REQUIRED_ELEMENTS.items():
            total_count["required"] += 1
            value = self._get_nested_value(location_overview, path)
            if self._is_empty(value):
                issues.append(
                    ComplianceIssue(
                        category="Property Identification",
                        element=path,
                        severity="required",
                        message=f"Missing required element: {description}",
                        suggestion=f"Add {description.lower()} to the location overview",
                    )
                )
            else:
                present_count["required"] += 1

        # Check recommended elements
        for path, description in self.RECOMMENDED_ELEMENTS.items():
            total_count["recommended"] += 1
            value = self._get_nested_value(location_overview, path)
            if self._is_empty(value):
                issues.append(
                    ComplianceIssue(
                        category="Location Description",
                        element=path,
                        severity="recommended",
                        message=f"Missing recommended element: {description}",
                        suggestion=f"Consider adding {description.lower()}",
                    )
                )
            else:
                present_count["recommended"] += 1

        # Check optional elements
        for path, description in self.OPTIONAL_ELEMENTS.items():
            total_count["optional"] += 1
            value = self._get_nested_value(location_overview, path)
            if not self._is_empty(value):
                present_count["optional"] += 1

        # Calculate weighted score
        score = self._calculate_score(present_count, total_count)

        # Determine compliance level
        compliance_level = self._determine_compliance_level(score, issues)

        # Generate recommendations
        recommendations = self._generate_recommendations(issues)

        # Generate warnings
        warnings = self._generate_warnings(location_overview)

        return CUSPAPComplianceReport(
            compliance_level=compliance_level,
            score=score,
            issues=issues,
            warnings=warnings,
            recommendations=recommendations,
        )

    def _get_nested_value(self, obj: Any, path: str) -> Any:
        """
        Get a nested value from an object using dot notation.

        Args:
            obj: Object to traverse
            path: Dot-separated path (e.g., "property_id.address")

        Returns:
            Value at path or None
        """
        parts = path.split(".")
        current = obj

        for part in parts:
            if current is None:
                return None
            if hasattr(current, part):
                current = getattr(current, part)
            elif isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        return current

    def _is_empty(self, value: Any) -> bool:
        """Check if a value is empty/missing."""
        if value is None:
            return True
        if isinstance(value, str) and not value.strip():
            return True
        if isinstance(value, (list, dict)) and len(value) == 0:
            return True
        if isinstance(value, (int, float)) and value == 0:
            # Special case: coordinates of 0,0 are likely missing
            return True
        return False

    def _calculate_score(
        self,
        present: Dict[str, int],
        total: Dict[str, int],
    ) -> float:
        """
        Calculate weighted compliance score.

        Args:
            present: Count of present elements by severity
            total: Count of total elements by severity

        Returns:
            Score from 0-100
        """
        weighted_present = (
            present["required"] * self.WEIGHTS["required"]
            + present["recommended"] * self.WEIGHTS["recommended"]
            + present["optional"] * self.WEIGHTS["optional"]
        )
        weighted_total = (
            total["required"] * self.WEIGHTS["required"]
            + total["recommended"] * self.WEIGHTS["recommended"]
            + total["optional"] * self.WEIGHTS["optional"]
        )

        if weighted_total == 0:
            return 0.0

        return round((weighted_present / weighted_total) * 100, 1)

    def _determine_compliance_level(
        self,
        score: float,
        issues: List[ComplianceIssue],
    ) -> ComplianceLevel:
        """
        Determine overall compliance level.

        Args:
            score: Weighted compliance score
            issues: List of compliance issues

        Returns:
            ComplianceLevel enum value
        """
        required_issues = [i for i in issues if i.severity == "required"]

        if required_issues:
            # Any missing required element drops to partial or insufficient
            if len(required_issues) >= 3:
                return ComplianceLevel.INSUFFICIENT
            return ComplianceLevel.PARTIAL

        if score >= 90:
            return ComplianceLevel.FULL
        elif score >= 70:
            return ComplianceLevel.SUBSTANTIAL
        elif score >= 50:
            return ComplianceLevel.PARTIAL
        else:
            return ComplianceLevel.INSUFFICIENT

    def _generate_recommendations(
        self,
        issues: List[ComplianceIssue],
    ) -> List[str]:
        """Generate actionable recommendations from issues."""
        recommendations = []

        # Group by severity
        required = [i for i in issues if i.severity == "required"]
        recommended = [i for i in issues if i.severity == "recommended"]

        if required:
            recommendations.append(
                f"Priority: Address {len(required)} missing required elements"
            )

        if recommended:
            recommendations.append(
                f"Enhancement: Consider adding {len(recommended)} recommended elements for a more complete report"
            )

        # Specific recommendations
        if any("neighbourhood" in i.element.lower() for i in issues):
            recommendations.append(
                "Add neighbourhood description with character, building types, and surrounding uses"
            )

        if any("surrounding_uses" in i.element for i in issues):
            recommendations.append(
                "Include surrounding land uses for all cardinal directions (N, S, E, W)"
            )

        return recommendations

    def _generate_warnings(self, location_overview) -> List[str]:
        """Generate warnings about potential issues."""
        warnings = []

        # Check for data source attribution
        if hasattr(location_overview, "data_sources"):
            if not location_overview.data_sources:
                warnings.append(
                    "No data sources attributed - CUSPAP requires disclosure of sources"
                )

        # Check for limiting conditions
        if hasattr(location_overview, "warnings"):
            if not location_overview.warnings:
                pass  # No warning needed

        # Check coordinate validity
        if hasattr(location_overview, "property_id"):
            lat = getattr(location_overview.property_id, "latitude", 0)
            lon = getattr(location_overview.property_id, "longitude", 0)
            if lat and lon:
                # Check if coordinates are within Ontario bounds
                if not (41.7 < lat < 56.9 and -95.2 < lon < -74.3):
                    warnings.append(
                        "Coordinates appear to be outside Ontario - verify location"
                    )

        return warnings


def validate_location_overview(location_overview) -> CUSPAPComplianceReport:
    """
    Convenience function to validate a LocationOverview.

    Args:
        location_overview: LocationOverview object

    Returns:
        CUSPAPComplianceReport
    """
    validator = CUSPAPValidator()
    return validator.validate(location_overview)
