#!/usr/bin/env python3
"""
Calculate distances from subject property to all comparables using Distancematrix.ai API.

This script:
1. Reads input JSON with property addresses
2. Identifies the subject property
3. Calls Distancematrix.ai API to calculate driving distances
4. Updates all properties with distance_km values
5. Saves updated JSON

API Documentation: https://distancematrix.ai/
Free tier: 1,000 elements/month
"""

import json
import sys
import os
import requests
import argparse
from typing import Dict, List, Any


def load_json(file_path: str) -> Dict[str, Any]:
    """Load JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)


def save_json(data: Dict[str, Any], file_path: str):
    """Save JSON file."""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


def format_address(address: str, unit: str = None) -> str:
    """
    Format address for API call.

    Note: Unit is NOT appended because the building is at the same location
    regardless of unit, and appending the unit breaks geocoding API calls.
    """
    return address


def calculate_distance(origin: str, destination: str, api_key: str) -> float:
    """
    Calculate driving distance between two addresses using Distancematrix.ai API.

    Args:
        origin: Origin address
        destination: Destination address
        api_key: Distancematrix.ai API key

    Returns:
        Distance in kilometers (float)

    Raises:
        Exception if API call fails
    """
    url = "https://api.distancematrix.ai/maps/api/distancematrix/json"

    params = {
        'origins': origin,
        'destinations': destination,
        'key': api_key,
        'mode': 'driving'  # Can also be: walking, bicycling, transit
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(f"API request failed with status {response.status_code}: {response.text}")

    data = response.json()

    # Check API response status
    if data.get('status') != 'OK':
        raise Exception(f"API returned error: {data.get('status')} - {data.get('error_message', 'Unknown error')}")

    # Extract distance from response
    rows = data.get('rows', [])
    if not rows:
        raise Exception("No distance data in API response")

    elements = rows[0].get('elements', [])
    if not elements:
        raise Exception("No distance elements in API response")

    element = elements[0]

    if element.get('status') != 'OK':
        raise Exception(f"Distance calculation failed: {element.get('status')}")

    # Get distance in meters and convert to kilometers
    distance_meters = element.get('distance', {}).get('value', 0)
    distance_km = distance_meters / 1000.0

    return round(distance_km, 1)


def add_distances_to_json(input_json: Dict[str, Any], api_key: str, verbose: bool = False) -> Dict[str, Any]:
    """
    Add distance_km to all properties in the JSON.

    Args:
        input_json: Input JSON data structure
        api_key: Distancematrix.ai API key
        verbose: Print progress messages

    Returns:
        Updated JSON with distance_km values
    """
    # Get subject property
    subject = input_json.get('subject_property')
    if not subject:
        raise ValueError("No subject_property found in JSON")

    subject_address = format_address(subject.get('address', ''), subject.get('unit', ''))

    if not subject_address:
        raise ValueError("Subject property has no address")

    if verbose:
        print(f"Subject property: {subject_address}")
        print()

    # Set subject distance to 0.0
    subject['distance_km'] = 0.0

    # Process all comparables
    comparables = input_json.get('comparables', [])
    total = len(comparables)

    if verbose:
        print(f"Calculating distances for {total} comparables...")
        print()

    for i, comp in enumerate(comparables, 1):
        comp_address = format_address(comp.get('address', ''), comp.get('unit', ''))

        if not comp_address:
            if verbose:
                print(f"[{i}/{total}] Skipping property with no address")
            comp['distance_km'] = 0.0
            continue

        try:
            distance = calculate_distance(subject_address, comp_address, api_key)
            comp['distance_km'] = distance

            if verbose:
                print(f"[{i}/{total}] {comp_address[:50]:<50} -> {distance:>6.1f} km")

        except Exception as e:
            if verbose:
                print(f"[{i}/{total}] ERROR: {comp_address[:50]:<50} -> {str(e)}")

            # Set to 0.0 on error to avoid breaking the analysis
            comp['distance_km'] = 0.0

    if verbose:
        print()
        print("✓ Distance calculations complete!")

    return input_json


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Calculate distances from subject property to all comparables using Distancematrix.ai API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Calculate distances and save to new file
  python calculate_distances.py --input data.json --output data_with_distances.json --api-key YOUR_KEY

  # Use API key from environment variable
  export DISTANCEMATRIX_API_KEY=your_key_here
  python calculate_distances.py --input data.json --output data_with_distances.json

  # Overwrite original file
  python calculate_distances.py --input data.json --output data.json --api-key YOUR_KEY

  # Verbose mode to see progress
  python calculate_distances.py --input data.json --output data_with_distances.json --verbose

API Key:
  Get a free API key at https://distancematrix.ai/
  Free tier: 1,000 elements/month
  Set environment variable: export DISTANCEMATRIX_API_KEY=your_key_here
        """
    )

    parser.add_argument('--input', '-i', required=True,
                        help='Input JSON file path')
    parser.add_argument('--output', '-o', required=True,
                        help='Output JSON file path (can be same as input to overwrite)')
    parser.add_argument('--api-key', '-k',
                        help='Distancematrix.ai API key (or set DISTANCEMATRIX_API_KEY env var)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Print progress messages')

    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or os.environ.get('DISTANCEMATRIX_API_KEY')

    if not api_key:
        print("ERROR: API key not provided!")
        print()
        print("Provide API key via:")
        print("  1. --api-key flag: python calculate_distances.py --api-key YOUR_KEY")
        print("  2. Environment variable: export DISTANCEMATRIX_API_KEY=your_key_here")
        print()
        print("Get a free API key at https://distancematrix.ai/")
        sys.exit(1)

    # Load input JSON
    if args.verbose:
        print(f"Loading: {args.input}")
        print()

    try:
        data = load_json(args.input)
    except Exception as e:
        print(f"ERROR: Failed to load input file: {e}")
        sys.exit(1)

    # Calculate distances
    try:
        updated_data = add_distances_to_json(data, api_key, verbose=args.verbose)
    except Exception as e:
        print(f"ERROR: Distance calculation failed: {e}")
        sys.exit(1)

    # Save output JSON
    try:
        save_json(updated_data, args.output)
        if args.verbose:
            print()
        print(f"✓ Saved to: {args.output}")
    except Exception as e:
        print(f"ERROR: Failed to save output file: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
