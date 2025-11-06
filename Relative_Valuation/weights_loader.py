#!/usr/bin/env python3
"""
Weight Configuration Loader for Relative Valuation Calculator

Loads and validates tenant persona weight configurations from external config files.
Provides fallback to hardcoded defaults if config file unavailable.

Usage:
    from weights_loader import load_weights, list_personas, get_persona_weights

    # Load all personas
    personas = load_weights()

    # Get specific persona
    weights = get_persona_weights("3pl")

    # List available personas
    available = list_personas()

Author: Claude Code
Date: November 6, 2025
Version: 2.0
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import sys


class WeightsConfigError(Exception):
    """Raised when weights configuration is invalid."""
    pass


def get_config_path(custom_path: Optional[str] = None) -> Path:
    """
    Get path to weights configuration file.

    Search order:
    1. Custom path provided via parameter
    2. Environment variable WEIGHTS_CONFIG_PATH
    3. Default: Relative_Valuation/weights_config.json

    Args:
        custom_path: Optional custom path to config file

    Returns:
        Path object to config file
    """
    if custom_path:
        path = Path(custom_path)
        if path.exists():
            return path
        raise FileNotFoundError(f"Custom weights config not found: {custom_path}")

    # Check environment variable
    env_path = os.getenv("WEIGHTS_CONFIG_PATH")
    if env_path:
        path = Path(env_path)
        if path.exists():
            return path
        print(f"[WARNING] WEIGHTS_CONFIG_PATH set but file not found: {env_path}")

    # Default location
    script_dir = Path(__file__).parent
    default_path = script_dir / "weights_config.json"

    if not default_path.exists():
        print(f"[WARNING] Default weights config not found: {default_path}")
        print("[INFO] Falling back to hardcoded default weights")
        return None

    return default_path


def validate_persona_weights(persona_name: str, weights: Dict[str, float],
                             tolerance: float = 0.001) -> bool:
    """
    Validate that persona weights are valid.

    Checks:
    1. All core variables present
    2. All weights are numeric and >= 0
    3. Total weights sum to 1.0 (within tolerance)

    Args:
        persona_name: Name of persona for error messages
        weights: Combined core + optional weights
        tolerance: Maximum deviation from 1.0

    Returns:
        True if valid

    Raises:
        WeightsConfigError: If validation fails
    """
    required_core = [
        'net_asking_rent', 'parking_ratio', 'tmi', 'clear_height_ft',
        'pct_office_space', 'distance_km', 'area_difference',
        'building_age_years', 'class'
    ]

    # Check core variables present
    missing = [var for var in required_core if var not in weights]
    if missing:
        raise WeightsConfigError(
            f"Persona '{persona_name}' missing required core variables: {missing}"
        )

    # Check weights are numeric and non-negative
    for var, weight in weights.items():
        if not isinstance(weight, (int, float)):
            raise WeightsConfigError(
                f"Persona '{persona_name}': weight for '{var}' is not numeric: {weight}"
            )
        if weight < 0:
            raise WeightsConfigError(
                f"Persona '{persona_name}': weight for '{var}' is negative: {weight}"
            )

    # Check total sums to 1.0 (within tolerance)
    total = sum(weights.values())
    if abs(total - 1.0) > tolerance:
        raise WeightsConfigError(
            f"Persona '{persona_name}': weights sum to {total:.4f}, expected 1.0 "
            f"(tolerance: {tolerance})"
        )

    return True


def load_weights(config_path: Optional[str] = None,
                validate: bool = True) -> Dict[str, Dict[str, Any]]:
    """
    Load weight configurations from JSON file.

    Args:
        config_path: Optional path to config file (defaults to weights_config.json)
        validate: Whether to validate weights (default: True)

    Returns:
        Dictionary of persona configurations:
        {
            "default": {
                "name": "Default/Balanced",
                "description": "...",
                "weights": {"net_asking_rent": 0.11, ...}
            },
            "3pl": {...},
            ...
        }

    Raises:
        FileNotFoundError: If config file not found and no fallback
        WeightsConfigError: If config invalid
    """
    path = get_config_path(config_path)

    if path is None:
        print("[INFO] Using hardcoded default weights")
        return get_hardcoded_defaults()

    try:
        with open(path, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise WeightsConfigError(f"Invalid JSON in weights config: {e}")

    # Validate structure
    if 'personas' not in config:
        raise WeightsConfigError("Config missing 'personas' key")

    # Extract validation settings
    validation_config = config.get('validation', {})
    tolerance = validation_config.get('total_weight_tolerance', 0.001)

    # Process each persona
    personas = {}
    for persona_id, persona_data in config['personas'].items():
        # Combine core and optional weights
        combined_weights = {}

        if 'weights' not in persona_data:
            raise WeightsConfigError(f"Persona '{persona_id}' missing 'weights' key")

        core = persona_data['weights'].get('core_variables', {})
        optional = persona_data['weights'].get('optional_variables', {})

        combined_weights.update(core)
        combined_weights.update(optional)

        # Validate if requested
        if validate:
            validate_persona_weights(persona_id, combined_weights, tolerance)

        # Store persona
        personas[persona_id] = {
            'name': persona_data.get('name', persona_id),
            'description': persona_data.get('description', ''),
            'rationale': persona_data.get('rationale', ''),
            'weights': combined_weights
        }

    print(f"[INFO] Loaded {len(personas)} persona(s) from {path}")
    return personas


def get_persona_weights(persona: str = "default",
                       config_path: Optional[str] = None) -> Dict[str, float]:
    """
    Get weights for a specific tenant persona.

    Args:
        persona: Persona name (default, 3pl, manufacturing, office)
        config_path: Optional path to config file

    Returns:
        Dictionary of variable weights

    Raises:
        WeightsConfigError: If persona not found
    """
    personas = load_weights(config_path)

    if persona not in personas:
        available = ', '.join(personas.keys())
        raise WeightsConfigError(
            f"Persona '{persona}' not found. Available: {available}"
        )

    return personas[persona]['weights']


def list_personas(config_path: Optional[str] = None) -> List[Dict[str, str]]:
    """
    List all available tenant personas.

    Args:
        config_path: Optional path to config file

    Returns:
        List of persona info dictionaries:
        [
            {"id": "default", "name": "Default/Balanced", "description": "..."},
            {"id": "3pl", "name": "3PL/Distribution", "description": "..."},
            ...
        ]
    """
    personas = load_weights(config_path)

    return [
        {
            'id': persona_id,
            'name': data['name'],
            'description': data['description']
        }
        for persona_id, data in personas.items()
    ]


def get_hardcoded_defaults() -> Dict[str, Dict[str, Any]]:
    """
    Fallback hardcoded default weights if config file unavailable.

    Returns same structure as load_weights().
    """
    return {
        "default": {
            "name": "Default/Balanced",
            "description": "Balanced weight profile for general industrial tenants",
            "rationale": "Standard allocation for typical industrial tenants",
            "weights": {
                # Core variables (65%)
                'net_asking_rent': 0.11,
                'parking_ratio': 0.09,
                'tmi': 0.09,
                'clear_height_ft': 0.07,
                'pct_office_space': 0.06,
                'distance_km': 0.07,
                'area_difference': 0.07,
                'building_age_years': 0.04,
                'class': 0.05,
                # Existing optional (12%)
                'shipping_doors_tl': 0.04,
                'shipping_doors_di': 0.03,
                'power_amps': 0.03,
                'trailer_parking': 0.02,
                'secure_shipping': 0.00,
                'excess_land': 0.00,
                # Phase 1 optional (17%)
                'bay_depth_ft': 0.04,
                'lot_size_acres': 0.03,
                'hvac_coverage': 0.03,
                'sprinkler_type': 0.03,
                'rail_access': 0.02,
                'crane': 0.02,
                'occupancy_status': 0.00,
                # Phase 2 optional (6%)
                'grade_level_doors': 0.02,
                'days_on_market': 0.02,
                'zoning': 0.02
            }
        }
    }


def export_persona_weights(persona: str, output_path: str,
                          config_path: Optional[str] = None) -> None:
    """
    Export a single persona's weights to a separate JSON file.

    Useful for creating custom persona files or documentation.

    Args:
        persona: Persona name to export
        output_path: Path to output JSON file
        config_path: Optional path to config file
    """
    personas = load_weights(config_path)

    if persona not in personas:
        raise WeightsConfigError(f"Persona '{persona}' not found")

    export_data = {
        "persona": persona,
        "name": personas[persona]['name'],
        "description": personas[persona]['description'],
        "weights": personas[persona]['weights'],
        "total": sum(personas[persona]['weights'].values())
    }

    with open(output_path, 'w') as f:
        json.dump(export_data, f, indent=2)

    print(f"[INFO] Exported persona '{persona}' to {output_path}")


def print_persona_summary(persona: str = "default",
                         config_path: Optional[str] = None) -> None:
    """
    Print a formatted summary of persona weights.

    Args:
        persona: Persona name
        config_path: Optional path to config file
    """
    personas = load_weights(config_path)

    if persona not in personas:
        raise WeightsConfigError(f"Persona '{persona}' not found")

    data = personas[persona]

    print(f"\n{'='*60}")
    print(f"PERSONA: {data['name']}")
    print(f"{'='*60}")
    print(f"\n{data['description']}\n")

    if data['rationale']:
        print(f"RATIONALE: {data['rationale']}\n")

    # Sort by weight descending
    sorted_weights = sorted(data['weights'].items(), key=lambda x: x[1], reverse=True)

    print("WEIGHTS (sorted by importance):")
    print(f"{'Variable':<25} {'Weight':>8} {'Bar':>30}")
    print("-" * 60)

    for var, weight in sorted_weights:
        if weight > 0:  # Only show non-zero weights
            bar = '█' * int(weight * 200)  # Scale for visibility
            print(f"{var:<25} {weight:>7.1%} {bar}")

    total = sum(data['weights'].values())
    print("-" * 60)
    print(f"{'TOTAL':<25} {total:>7.1%}")
    print(f"{'='*60}\n")


# CLI for testing
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Weights Configuration Loader")
    parser.add_argument('--list', action='store_true',
                       help='List all available personas')
    parser.add_argument('--show', type=str, metavar='PERSONA',
                       help='Show weights for a specific persona')
    parser.add_argument('--export', type=str, metavar='PERSONA',
                       help='Export persona to separate JSON file')
    parser.add_argument('--output', type=str,
                       help='Output path for export')
    parser.add_argument('--config', type=str,
                       help='Path to custom config file')
    parser.add_argument('--validate', action='store_true',
                       help='Validate config file')

    args = parser.parse_args()

    try:
        if args.list:
            personas = list_personas(args.config)
            print("\nAvailable Personas:")
            print("-" * 60)
            for p in personas:
                print(f"\n{p['id']}: {p['name']}")
                print(f"  {p['description']}")
            print()

        elif args.show:
            print_persona_summary(args.show, args.config)

        elif args.export:
            if not args.output:
                print("Error: --output required for --export")
                sys.exit(1)
            export_persona_weights(args.export, args.output, args.config)

        elif args.validate:
            personas = load_weights(args.config, validate=True)
            print(f"\n✓ Config valid: {len(personas)} personas loaded")
            for pid, pdata in personas.items():
                total = sum(pdata['weights'].values())
                print(f"  - {pid}: {pdata['name']} (total weight: {total:.4f})")
            print()

        else:
            parser.print_help()

    except (WeightsConfigError, FileNotFoundError) as e:
        print(f"\n[ERROR] {e}\n")
        sys.exit(1)
