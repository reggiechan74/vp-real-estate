#!/usr/bin/env python3
"""
Extract sample data from Excel template and convert to JSON format.

This script reads the Relative Valuation Template Excel file and extracts
the first 20-30 properties to create a sample input JSON file for testing.
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path


def extract_sample_data(excel_path: str, output_path: str, num_properties: int = 25):
    """
    Extract sample data from Excel template and save as JSON.

    Args:
        excel_path: Path to Excel template file
        output_path: Path to save JSON output
        num_properties: Number of properties to extract (default: 25)
    """
    # Read Excel file with proper header row (row 4, index 4)
    print(f"Reading Excel file: {excel_path}")
    df = pd.read_excel(excel_path, header=4)  # Header at row 4

    print(f"\nColumns: {list(df.columns)[:17]}")
    print(f"Shape before cleaning: {df.shape}")

    # Find the column name for Address (might have leading/trailing spaces)
    address_col = [col for col in df.columns if 'Address' in str(col)]
    if address_col:
        address_col = address_col[0]
        print(f"Found address column: '{address_col}'")
    else:
        # Column names might not have loaded correctly, use first column
        address_col = df.columns[0]
        print(f"Using first column as address: '{address_col}'")

    # Clean up data - keep only rows with valid addresses
    df = df[df[address_col].notna()].copy()

    # Remove rows where address looks like header text (but keep "SUBJECT PROPERTY")
    # Only filter out if it contains both "Address" (header row indicator)
    df = df[~df[address_col].astype(str).str.contains('^Address$', case=False, na=False, regex=True)].copy()

    print(f"Rows with valid addresses: {len(df)}")

    # Extract first N properties
    sample_df = df.head(num_properties).copy()

    # Helper function to find column
    def find_col(pattern):
        for col in df.columns:
            if pattern.lower() in str(col).lower():
                return col
        return None

    # Map column names
    col_map = {
        'address': find_col('address'),
        'unit': find_col('unit'),
        'year_built': find_col('year built'),
        'clear_height': find_col('clear height'),
        'office': find_col('office'),
        'parking': find_col('parking'),
        'available': find_col('available'),
        'area_diff': find_col('difference in area'),
        'distance': find_col('distance'),
        'net_rent': find_col('net asking'),
        'tmi': find_col('tmi'),
        'class': find_col('class')
    }

    print(f"\nColumn mapping:")
    for key, val in col_map.items():
        print(f"  {key}: {val}")

    # Read weights from row 2 (index 2)
    weights_df = pd.read_excel(excel_path, header=None, skiprows=2, nrows=1)
    weights = {
        "year_built": float(weights_df.iloc[0, 18]) if pd.notna(weights_df.iloc[0, 18]) else 0.08,
        "clear_height_ft": float(weights_df.iloc[0, 19]) if pd.notna(weights_df.iloc[0, 19]) else 0.10,
        "pct_office_space": float(weights_df.iloc[0, 20]) if pd.notna(weights_df.iloc[0, 20]) else 0.10,
        "parking_ratio": float(weights_df.iloc[0, 21]) if pd.notna(weights_df.iloc[0, 21]) else 0.15,
        "distance_km": float(weights_df.iloc[0, 22]) if pd.notna(weights_df.iloc[0, 22]) else 0.10,
        "net_asking_rent": float(weights_df.iloc[0, 23]) if pd.notna(weights_df.iloc[0, 23]) else 0.16,
        "tmi": float(weights_df.iloc[0, 24]) if pd.notna(weights_df.iloc[0, 24]) else 0.14,
        "class": float(weights_df.iloc[0, 25]) if pd.notna(weights_df.iloc[0, 25]) else 0.07,
        "area_difference": float(weights_df.iloc[0, 26]) if pd.notna(weights_df.iloc[0, 26]) else 0.10
    }

    print(f"\nWeights extracted: {weights}")
    print(f"Total weight: {sum(weights.values()):.2f}")

    # Convert to JSON format
    properties = []

    for idx, row in sample_df.iterrows():
        # Determine if this is the subject property
        # Subject property is identified by address "SUBJECT PROPERTY" or distance = 0
        address_val = str(row[col_map['address']]) if col_map['address'] and pd.notna(row[col_map['address']]) else ""
        distance_val = float(row[col_map['distance']]) if col_map['distance'] and pd.notna(row[col_map['distance']]) else None

        is_subject = (address_val == "SUBJECT PROPERTY") or (distance_val == 0.0)

        # Parse class (A=1, B=2, C=3)
        class_col = col_map['class']
        class_val = row[class_col] if class_col else 2
        if pd.notna(class_val):
            if isinstance(class_val, str):
                if 'A' in class_val.upper():
                    class_num = 1
                elif 'B' in class_val.upper():
                    class_num = 2
                elif 'C' in class_val.upper():
                    class_num = 3
                else:
                    class_num = int(float(class_val))
            else:
                class_num = int(float(class_val))
        else:
            class_num = 2  # Default to B

        # Build property dict
        # NOTE: Use actual distance and area_diff from Excel
        # The Excel may have a different reference point for distance
        # and may have pre-calculated area differences
        prop = {
            "address": str(row[col_map['address']]) if col_map['address'] and pd.notna(row[col_map['address']]) else "",
            "unit": str(row[col_map['unit']]) if col_map['unit'] and pd.notna(row[col_map['unit']]) else "",
            "year_built": int(float(row[col_map['year_built']])) if col_map['year_built'] and pd.notna(row[col_map['year_built']]) else 1980,
            "clear_height_ft": float(row[col_map['clear_height']]) if col_map['clear_height'] and pd.notna(row[col_map['clear_height']]) else 16.0,
            "pct_office_space": float(row[col_map['office']]) if col_map['office'] and pd.notna(row[col_map['office']]) else 0.20,
            "parking_ratio": float(row[col_map['parking']]) if col_map['parking'] and pd.notna(row[col_map['parking']]) else 1.5,
            "available_sf": int(float(row[col_map['available']])) if col_map['available'] and pd.notna(row[col_map['available']]) else 2000,
            "area_difference": int(float(row[col_map['area_diff']])) if col_map['area_diff'] and pd.notna(row[col_map['area_diff']]) else 0,
            "distance_km": float(row[col_map['distance']]) if col_map['distance'] and pd.notna(row[col_map['distance']]) else 0.0,
            "net_asking_rent": float(row[col_map['net_rent']]) if col_map['net_rent'] and pd.notna(row[col_map['net_rent']]) else 9.0,
            "tmi": float(row[col_map['tmi']]) if col_map['tmi'] and pd.notna(row[col_map['tmi']]) else 5.0,
            "class": class_num,
            "is_subject": bool(is_subject)  # Ensure proper boolean type
        }

        properties.append(prop)

    # Separate subject from comparables
    subject = next(p for p in properties if p['is_subject'])
    comparables = [p for p in properties if not p['is_subject']]

    # Build final JSON structure
    result = {
        "analysis_date": "2020-05-07",
        "market": "Greater Toronto Area - Industrial",
        "subject_property": subject,
        "comparables": comparables,
        "weights": weights
    }

    # Save to JSON
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\n✓ Sample data extracted successfully")
    print(f"  Subject property: {subject['address']}, Unit {subject['unit']}")
    print(f"  Comparables: {len(comparables)}")
    print(f"  Output saved to: {output_path}")

    return result


if __name__ == "__main__":
    excel_path = "/workspaces/lease-abstract/skillsdevdocs/Relative Valuation Template for newsletter.xlsx"
    output_path = "/workspaces/lease-abstract/Relative_Valuation/sample_input.json"

    extract_sample_data(excel_path, output_path)
