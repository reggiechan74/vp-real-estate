"""
Report Formatter Module

Generates location overview reports using Jinja2 templates.
Supports markdown and JSON output formats.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import asdict

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..schemas.location_data import LocationOverview


class ReportGenerator:
    """
    Generate location overview reports from LocationOverview data.

    Supports:
    - Markdown format (default, for appraisal reports)
    - JSON format (for API responses and data exchange)
    """

    DEFAULT_TEMPLATE_DIR = Path(__file__).parent / "templates"
    DEFAULT_OUTPUT_DIR = Path("Reports")

    def __init__(
        self,
        template_dir: Optional[str] = None,
        output_dir: Optional[str] = None,
    ):
        """
        Initialize report generator.

        Args:
            template_dir: Directory containing Jinja2 templates
            output_dir: Directory for generated reports
        """
        self.template_dir = Path(template_dir) if template_dir else self.DEFAULT_TEMPLATE_DIR
        self.output_dir = Path(output_dir) if output_dir else self.DEFAULT_OUTPUT_DIR

        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def generate_markdown(
        self,
        data: LocationOverview,
        filename: Optional[str] = None,
        save: bool = True,
    ) -> str:
        """
        Generate markdown report from LocationOverview.

        Args:
            data: LocationOverview data
            filename: Optional custom filename (without extension)
            save: Whether to save to file

        Returns:
            Generated markdown content
        """
        template = self.env.get_template("location_overview.md.j2")

        # Render template
        content = template.render(
            property_id=data.property_id,
            planning=data.planning,
            provincial_plans=data.provincial_plans,
            neighbourhood=data.neighbourhood,
            environmental=data.environmental,
            market=data.market,
            transport=data.transport,
            regional_context=data.regional_context,
            generated_at=data.generated_at,
            data_sources=data.data_sources,
            warnings=data.warnings,
            errors=data.errors,
        )

        if save:
            output_path = self._save_report(content, data, filename, "md")
            return str(output_path)

        return content

    def generate_json(
        self,
        data: LocationOverview,
        filename: Optional[str] = None,
        save: bool = True,
        pretty: bool = True,
    ) -> str:
        """
        Generate JSON report from LocationOverview.

        Args:
            data: LocationOverview data
            filename: Optional custom filename (without extension)
            save: Whether to save to file
            pretty: Whether to format JSON with indentation

        Returns:
            Generated JSON content or file path
        """
        # Convert to dictionary
        json_data = data.to_dict()

        # Serialize to JSON
        indent = 2 if pretty else None
        content = json.dumps(json_data, indent=indent, default=str)

        if save:
            output_path = self._save_report(content, data, filename, "json")
            return str(output_path)

        return content

    def _save_report(
        self,
        content: str,
        data: LocationOverview,
        filename: Optional[str],
        extension: str,
    ) -> Path:
        """
        Save report to file with timestamp prefix.

        Args:
            content: Report content
            data: LocationOverview for filename generation
            filename: Optional custom filename
            extension: File extension (md, json)

        Returns:
            Path to saved file
        """
        # Generate filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

        if filename:
            full_filename = f"{timestamp}_{filename}.{extension}"
        else:
            address_slug = self._slugify(data.property_id.address)
            full_filename = f"{timestamp}_location_overview_{address_slug}.{extension}"

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Save file
        output_path = self.output_dir / full_filename
        output_path.write_text(content, encoding="utf-8")

        return output_path

    def _slugify(self, text: str, max_length: int = 50) -> str:
        """
        Convert text to URL-safe slug.

        Args:
            text: Text to convert
            max_length: Maximum slug length

        Returns:
            Slugified text
        """
        import re

        # Convert to lowercase
        text = text.lower()

        # Remove special characters
        text = re.sub(r"[^\w\s-]", "", text)

        # Replace whitespace with underscores
        text = re.sub(r"[-\s]+", "_", text)

        # Trim to max length
        text = text[:max_length].rstrip("_")

        return text

    def get_report_summary(self, data: LocationOverview) -> Dict[str, Any]:
        """
        Generate a summary of the report contents.

        Useful for API responses and quick previews.

        Args:
            data: LocationOverview data

        Returns:
            Summary dictionary
        """
        return {
            "address": data.property_id.address,
            "municipality": data.property_id.municipality,
            "coordinates": {
                "latitude": data.property_id.latitude,
                "longitude": data.property_id.longitude,
            },
            "zoning": data.planning.zoning_designation,
            "greenbelt": data.provincial_plans.greenbelt_area,
            "growth_plan": data.provincial_plans.growth_plan_area,
            "amenities_count": len(data.neighbourhood.amenities),
            "transit_access": data.neighbourhood.transit_accessibility,
            "warnings_count": len(data.warnings),
            "errors_count": len(data.errors),
            "generated_at": data.generated_at.isoformat(),
        }
