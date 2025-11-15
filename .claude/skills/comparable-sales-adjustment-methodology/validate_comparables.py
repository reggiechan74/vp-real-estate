#!/usr/bin/env python3
"""
Comparable Sales JSON Validation Script

Validates LLM-extracted comparable sales data against JSON schema and performs
additional data quality checks. Provides detailed error reporting and optional
auto-correction of common LLM extraction issues.

Usage:
    python validate_comparables.py input.json
    python validate_comparables.py input.json --fix --output fixed.json
    python validate_comparables.py input.json --verbose
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime, date
import re

try:
    from jsonschema import validate, ValidationError, Draft202012Validator
except ImportError:
    print("ERROR: jsonschema library not found. Install with: pip install jsonschema")
    sys.exit(1)


class ComparableValidator:
    """Validates and optionally fixes LLM-extracted comparable sales JSON data."""

    def __init__(self, schema_path: str = "comparable_sales_input_schema.json"):
        """Initialize validator with JSON schema."""
        self.schema_path = Path(schema_path)
        self.schema = self._load_schema()
        self.errors = []
        self.warnings = []
        self.fixes_applied = []

    def _load_schema(self) -> Dict:
        """Load JSON schema from file."""
        if not self.schema_path.exists():
            raise FileNotFoundError(
                f"Schema file not found: {self.schema_path}\n"
                f"Current directory: {Path.cwd()}"
            )

        with open(self.schema_path, 'r') as f:
            return json.load(f)

    def validate(self, data: Dict, fix: bool = False) -> Tuple[bool, Dict]:
        """
        Validate JSON data against schema and perform quality checks.

        Args:
            data: JSON data to validate
            fix: If True, attempt to auto-fix common issues

        Returns:
            Tuple of (is_valid, corrected_data)
        """
        self.errors = []
        self.warnings = []
        self.fixes_applied = []

        # Apply auto-fixes if requested
        if fix:
            data = self._auto_fix(data)

        # 1. Schema validation
        is_schema_valid = self._validate_schema(data)

        # 2. Semantic validation (even if schema fails, collect all issues)
        self._validate_semantics(data)

        # 3. Data quality checks
        self._check_data_quality(data)

        # Overall validity
        is_valid = is_schema_valid and len(self.errors) == 0

        return is_valid, data

    def _validate_schema(self, data: Dict) -> bool:
        """Validate against JSON schema."""
        try:
            validate(instance=data, schema=self.schema)
            return True
        except ValidationError as e:
            # Parse the error for user-friendly message
            error_path = " → ".join(str(p) for p in e.path) if e.path else "root"
            self.errors.append({
                'type': 'SCHEMA_VIOLATION',
                'severity': 'ERROR',
                'location': error_path,
                'message': e.message,
                'validator': e.validator,
                'value': str(e.instance)[:100] if hasattr(e, 'instance') else None
            })
            return False

    def _validate_semantics(self, data: Dict) -> None:
        """Validate semantic rules beyond schema constraints."""

        # Check valuation date vs sale dates
        if 'market_parameters' in data and 'valuation_date' in data['market_parameters']:
            valuation_date = self._parse_date(data['market_parameters']['valuation_date'])

            if valuation_date and 'comparable_sales' in data:
                for i, comp in enumerate(data['comparable_sales']):
                    if 'sale_date' in comp:
                        sale_date = self._parse_date(comp['sale_date'])
                        if sale_date and sale_date > valuation_date:
                            self.warnings.append({
                                'type': 'FUTURE_SALE',
                                'severity': 'WARNING',
                                'location': f'comparable_sales[{i}].sale_date',
                                'message': f'Sale date ({comp["sale_date"]}) is after valuation date ({data["market_parameters"]["valuation_date"]})',
                                'value': comp.get('address', f'Comp {i+1}')
                            })

        # Check property type consistency
        if 'subject_property' in data and 'property_type' in data['subject_property']:
            subject_type = data['subject_property']['property_type']

            # Warn if industrial-specific fields present on office property
            if subject_type == 'office':
                industrial_fields = ['clear_height_feet', 'loading_docks_dock_high', 'rail_spur']
                for field in industrial_fields:
                    if field in data['subject_property']:
                        self.warnings.append({
                            'type': 'FIELD_MISMATCH',
                            'severity': 'WARNING',
                            'location': f'subject_property.{field}',
                            'message': f'Industrial field "{field}" present on office property',
                            'value': data['subject_property'][field]
                        })

            # Warn if office-specific fields present on industrial property
            if subject_type == 'industrial':
                office_fields = ['building_class', 'floor_plate_efficiency_pct', 'elevator_count']
                for field in office_fields:
                    if field in data['subject_property']:
                        self.warnings.append({
                            'type': 'FIELD_MISMATCH',
                            'severity': 'WARNING',
                            'location': f'subject_property.{field}',
                            'message': f'Office field "{field}" present on industrial property',
                            'value': data['subject_property'][field]
                        })

        # Check financing consistency
        if 'comparable_sales' in data:
            for i, comp in enumerate(data['comparable_sales']):
                if 'financing' in comp:
                    fin = comp['financing']
                    if fin.get('type') == 'seller_vtb':
                        # VTB should have rate, market_rate, term, and loan_amount
                        missing = []
                        for field in ['rate', 'market_rate', 'term_years', 'loan_amount']:
                            if field not in fin:
                                missing.append(field)
                        if missing:
                            self.warnings.append({
                                'type': 'INCOMPLETE_FINANCING',
                                'severity': 'WARNING',
                                'location': f'comparable_sales[{i}].financing',
                                'message': f'Seller VTB financing missing fields: {", ".join(missing)}',
                                'value': comp.get('address', f'Comp {i+1}')
                            })

    def _check_data_quality(self, data: Dict) -> None:
        """Check data quality and reasonableness."""

        # Check for suspiciously low/high values
        if 'comparable_sales' in data:
            for i, comp in enumerate(data['comparable_sales']):
                # Sale price reasonableness
                if 'sale_price' in comp:
                    price = comp['sale_price']
                    # Skip if not a number (will be caught by schema validation)
                    if not isinstance(price, (int, float)):
                        continue
                    if price < 100000:
                        self.warnings.append({
                            'type': 'SUSPICIOUS_VALUE',
                            'severity': 'WARNING',
                            'location': f'comparable_sales[{i}].sale_price',
                            'message': f'Sale price seems unusually low: ${price:,.0f}',
                            'value': comp.get('address', f'Comp {i+1}')
                        })
                    elif price > 500000000:
                        self.warnings.append({
                            'type': 'SUSPICIOUS_VALUE',
                            'severity': 'WARNING',
                            'location': f'comparable_sales[{i}].sale_price',
                            'message': f'Sale price seems unusually high: ${price:,.0f}',
                            'value': comp.get('address', f'Comp {i+1}')
                        })

                # Building size reasonableness
                if 'building_sf' in comp:
                    sf = comp['building_sf']
                    # Skip if not a number (will be caught by schema validation)
                    if not isinstance(sf, (int, float)):
                        continue
                    if sf > 0 and 'sale_price' in comp and isinstance(comp['sale_price'], (int, float)):
                        price_per_sf = comp['sale_price'] / sf
                        if price_per_sf < 10:
                            self.warnings.append({
                                'type': 'SUSPICIOUS_VALUE',
                                'severity': 'WARNING',
                                'location': f'comparable_sales[{i}]',
                                'message': f'Price per SF seems unusually low: ${price_per_sf:.2f}/SF',
                                'value': comp.get('address', f'Comp {i+1}')
                            })
                        elif price_per_sf > 1000:
                            self.warnings.append({
                                'type': 'SUSPICIOUS_VALUE',
                                'severity': 'WARNING',
                                'location': f'comparable_sales[{i}]',
                                'message': f'Price per SF seems unusually high: ${price_per_sf:.2f}/SF',
                                'value': comp.get('address', f'Comp {i+1}')
                            })

        # Check for required market parameters
        if 'market_parameters' in data:
            params = data['market_parameters']
            recommended = ['location_premium_per_point', 'lot_adjustment_per_acre']
            missing = [p for p in recommended if p not in params]
            if missing:
                self.warnings.append({
                    'type': 'MISSING_RECOMMENDED',
                    'severity': 'INFO',
                    'location': 'market_parameters',
                    'message': f'Recommended parameters missing: {", ".join(missing)}',
                    'value': 'May result in less accurate adjustments'
                })

    def _auto_fix(self, data: Dict) -> Dict:
        """Attempt to auto-fix common LLM extraction issues."""

        # Fix 1: Normalize date formats
        data = self._fix_dates(data)

        # Fix 2: Normalize enum values (case, underscores)
        data = self._fix_enums(data)

        # Fix 3: Convert string numbers to actual numbers
        data = self._fix_numeric_strings(data)

        # Fix 4: Remove null/None values
        data = self._remove_nulls(data)

        # Fix 5: Fix boolean strings
        data = self._fix_booleans(data)

        return data

    def _fix_dates(self, data: Dict) -> Dict:
        """Fix date format issues."""

        def fix_date_value(val: Any) -> Any:
            if not isinstance(val, str):
                return val

            # Try common date formats
            formats = [
                '%Y-%m-%d',
                '%m/%d/%Y',
                '%d/%m/%Y',
                '%Y/%m/%d',
                '%m-%d-%Y',
                '%d-%m-%Y',
                '%B %d, %Y',
                '%b %d, %Y',
            ]

            for fmt in formats:
                try:
                    dt = datetime.strptime(val, fmt)
                    fixed = dt.strftime('%Y-%m-%d')
                    if fixed != val:
                        self.fixes_applied.append(f'Date format: "{val}" → "{fixed}"')
                    return fixed
                except ValueError:
                    continue

            return val

        # Fix valuation_date
        if 'market_parameters' in data and 'valuation_date' in data['market_parameters']:
            data['market_parameters']['valuation_date'] = fix_date_value(
                data['market_parameters']['valuation_date']
            )

        # Fix sale_date in comparables
        if 'comparable_sales' in data:
            for comp in data['comparable_sales']:
                if 'sale_date' in comp:
                    comp['sale_date'] = fix_date_value(comp['sale_date'])

        return data

    def _fix_enums(self, data: Dict) -> Dict:
        """Fix enum value formatting (case, spaces to underscores)."""

        def normalize_enum(val: Any) -> Any:
            if not isinstance(val, str):
                return val

            # Convert to lowercase and replace spaces/hyphens with underscores
            fixed = val.lower().replace(' ', '_').replace('-', '_')

            # Remove multiple consecutive underscores
            fixed = re.sub(r'_+', '_', fixed)

            if fixed != val:
                self.fixes_applied.append(f'Enum format: "{val}" → "{fixed}"')

            return fixed

        # Fields that should be enums
        enum_fields = {
            'property_type', 'property_rights', 'topography', 'utilities', 'drainage',
            'flood_zone', 'environmental_status', 'soil_quality', 'fencing',
            'paving_condition', 'site_lighting', 'landscaping', 'stormwater_management',
            'construction_quality', 'functional_utility', 'energy_certification',
            'architectural_appeal', 'hvac_system', 'building_class', 'crane_system',
            'specialized_hvac', 'condition', 'type'
        }

        def fix_object_enums(obj: Dict) -> Dict:
            for key, val in obj.items():
                if key in enum_fields and isinstance(val, str):
                    obj[key] = normalize_enum(val)
                elif isinstance(val, dict):
                    obj[key] = fix_object_enums(val)
                elif isinstance(val, list):
                    obj[key] = [fix_object_enums(item) if isinstance(item, dict) else item for item in val]
            return obj

        return fix_object_enums(data)

    def _fix_numeric_strings(self, data: Dict) -> Dict:
        """Convert string numbers to actual numbers."""

        def fix_value(val: Any) -> Any:
            if not isinstance(val, str):
                return val

            # Try to parse as number
            val_clean = val.replace(',', '').replace('$', '').strip()

            try:
                # Try integer first
                if '.' not in val_clean:
                    fixed = int(val_clean)
                    if str(val) != str(fixed):
                        self.fixes_applied.append(f'String to int: "{val}" → {fixed}')
                    return fixed
                else:
                    fixed = float(val_clean)
                    if str(val) != str(fixed):
                        self.fixes_applied.append(f'String to float: "{val}" → {fixed}')
                    return fixed
            except ValueError:
                return val

        def fix_object_numbers(obj: Dict) -> Dict:
            for key, val in obj.items():
                if isinstance(val, str) and not key.startswith('_comment'):
                    obj[key] = fix_value(val)
                elif isinstance(val, dict):
                    obj[key] = fix_object_numbers(val)
                elif isinstance(val, list):
                    obj[key] = [fix_object_numbers(item) if isinstance(item, dict) else fix_value(item) for item in val]
            return obj

        return fix_object_numbers(data)

    def _remove_nulls(self, data: Dict) -> Dict:
        """Remove null/None values that cause schema validation issues."""

        def clean_object(obj: Any) -> Any:
            if isinstance(obj, dict):
                cleaned = {}
                for key, val in obj.items():
                    if val is not None:
                        cleaned[key] = clean_object(val)
                    else:
                        self.fixes_applied.append(f'Removed null field: {key}')
                return cleaned
            elif isinstance(obj, list):
                return [clean_object(item) for item in obj if item is not None]
            else:
                return obj

        return clean_object(data)

    def _fix_booleans(self, data: Dict) -> Dict:
        """Convert string booleans to actual booleans."""

        def fix_value(val: Any) -> Any:
            if isinstance(val, str):
                val_lower = val.lower().strip()
                if val_lower in ('true', 'yes', 'y', '1'):
                    self.fixes_applied.append(f'String to bool: "{val}" → True')
                    return True
                elif val_lower in ('false', 'no', 'n', '0'):
                    self.fixes_applied.append(f'String to bool: "{val}" → False')
                    return False
            return val

        def fix_object_bools(obj: Dict) -> Dict:
            for key, val in obj.items():
                if isinstance(val, str):
                    obj[key] = fix_value(val)
                elif isinstance(val, dict):
                    obj[key] = fix_object_bools(val)
                elif isinstance(val, list):
                    obj[key] = [fix_object_bools(item) if isinstance(item, dict) else fix_value(item) for item in val]
            return obj

        return fix_object_bools(data)

    def _parse_date(self, date_str: str) -> Optional[date]:
        """Parse date string to date object."""
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return None

    def print_report(self, verbose: bool = False) -> None:
        """Print validation report."""

        print("\n" + "=" * 70)
        print("COMPARABLE SALES JSON VALIDATION REPORT")
        print("=" * 70)

        # Summary
        error_count = len(self.errors)
        warning_count = len(self.warnings)
        fix_count = len(self.fixes_applied)

        if error_count == 0 and warning_count == 0:
            print("\n✅ VALIDATION PASSED - No errors or warnings")
        elif error_count == 0:
            print(f"\n⚠️  VALIDATION PASSED WITH WARNINGS - {warning_count} warning(s)")
        else:
            print(f"\n❌ VALIDATION FAILED - {error_count} error(s), {warning_count} warning(s)")

        # Fixes applied
        if fix_count > 0:
            print(f"\n🔧 AUTO-FIXES APPLIED: {fix_count}")
            if verbose:
                for fix in self.fixes_applied[:10]:  # Show first 10
                    print(f"   • {fix}")
                if len(self.fixes_applied) > 10:
                    print(f"   ... and {len(self.fixes_applied) - 10} more")

        # Errors
        if self.errors:
            print("\n" + "─" * 70)
            print("ERRORS:")
            print("─" * 70)
            for i, error in enumerate(self.errors, 1):
                print(f"\n{i}. [{error['type']}] {error['location']}")
                print(f"   {error['message']}")
                if verbose and error.get('value'):
                    print(f"   Value: {error['value']}")

        # Warnings
        if self.warnings:
            print("\n" + "─" * 70)
            print("WARNINGS:")
            print("─" * 70)
            for i, warning in enumerate(self.warnings, 1):
                severity_icon = "⚠️ " if warning['severity'] == 'WARNING' else "ℹ️ "
                print(f"\n{i}. {severity_icon}[{warning['type']}] {warning['location']}")
                print(f"   {warning['message']}")
                if verbose and warning.get('value'):
                    print(f"   Value: {warning['value']}")

        print("\n" + "=" * 70 + "\n")


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description='Validate LLM-extracted comparable sales JSON data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic validation
  python validate_comparables.py input.json

  # Auto-fix common issues and save corrected file
  python validate_comparables.py input.json --fix --output fixed.json

  # Verbose output with detailed error messages
  python validate_comparables.py input.json --verbose

  # Custom schema location
  python validate_comparables.py input.json --schema custom_schema.json
        """
    )

    parser.add_argument(
        'input_file',
        type=str,
        help='Path to JSON file to validate'
    )

    parser.add_argument(
        '--schema',
        type=str,
        default='comparable_sales_input_schema.json',
        help='Path to JSON schema file (default: comparable_sales_input_schema.json)'
    )

    parser.add_argument(
        '--fix',
        action='store_true',
        help='Attempt to auto-fix common LLM extraction issues'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Path to save corrected JSON (only used with --fix)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed error messages and fix details'
    )

    args = parser.parse_args()

    # Load input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        sys.exit(1)

    try:
        with open(input_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in input file: {e}")
        sys.exit(1)

    # Validate
    validator = ComparableValidator(schema_path=args.schema)
    is_valid, corrected_data = validator.validate(data, fix=args.fix)

    # Print report
    validator.print_report(verbose=args.verbose)

    # Save corrected file if requested
    if args.fix and args.output:
        output_path = Path(args.output)
        with open(output_path, 'w') as f:
            json.dump(corrected_data, f, indent=2)
        print(f"💾 Corrected JSON saved to: {output_path}\n")

    # Exit with appropriate code
    sys.exit(0 if is_valid else 1)


if __name__ == '__main__':
    main()
