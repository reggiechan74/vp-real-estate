#!/usr/bin/env python3
"""
Relative Valuation Calculator - Multi-Criteria Competitive Positioning Analysis

This module implements a weighted ranking system to determine a subject property's
competitive position within its market comparable set. The methodology ranks properties
from 1 (best) to X (worst) across 9 key variables, then calculates weighted scores
to identify which properties offer the best value proposition to tenants.

Usage:
    python relative_valuation_calculator.py --input data.json --output report.md
    python relative_valuation_calculator.py --input data.json --output-json results.json
    python relative_valuation_calculator.py --interactive

Author: Claude Code
Date: November 5, 2025
Version: 1.0.0 (Phase 1 - MVP)
"""

import json
import argparse
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import sys


@dataclass
class Property:
    """Represents a commercial property in the competitive analysis."""
    address: str
    unit: str
    year_built: int
    clear_height_ft: float
    pct_office_space: float
    parking_ratio: float
    available_sf: float
    net_asking_rent: float
    tmi: float
    class_: int  # 1=A, 2=B, 3=C
    distance_km: float
    area_difference: float = 0.0  # Calculated dynamically
    is_subject: bool = False
    landlord: str = ""

    # Additional property details (used in ranking if available)
    shipping_doors_tl: int = 0  # Truck-level doors
    shipping_doors_di: int = 0  # Drive-in doors
    availability_date: str = ""
    power_amps: int = 0
    trailer_parking: bool = False
    secure_shipping: bool = False
    excess_land: bool = False

    # Ranking results
    rank_year_built: int = 0
    rank_clear_height: int = 0
    rank_pct_office: int = 0
    rank_parking: int = 0
    rank_distance: int = 0
    rank_net_rent: int = 0
    rank_tmi: int = 0
    rank_class: int = 0
    rank_area_diff: int = 0
    rank_shipping_doors_tl: int = 0
    rank_shipping_doors_di: int = 0
    rank_power: int = 0
    rank_trailer_parking: int = 0
    rank_secure_shipping: int = 0
    rank_excess_land: int = 0

    weighted_score: float = 0.0
    final_rank: int = 0


@dataclass
class CompetitiveAnalysis:
    """Results of competitive positioning analysis."""
    analysis_date: str
    market: str
    total_properties: int
    subject_property: Dict[str, Any]
    top_competitors: List[Dict[str, Any]]
    gap_analysis: Dict[str, Any]
    sensitivity_scenarios: List[Dict[str, Any]]
    all_properties: List[Dict[str, Any]]


def load_comparable_data(json_path: str) -> Dict[str, Any]:
    """
    Load comparable data from JSON file.

    Args:
        json_path: Path to JSON file containing comparable data

    Returns:
        Dictionary with analysis_date, market, subject_property, comparables, weights

    Raises:
        FileNotFoundError: If JSON file doesn't exist
        json.JSONDecodeError: If JSON is malformed
    """
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)

        # Validate required fields
        required_fields = ['analysis_date', 'market', 'subject_property', 'comparables', 'weights']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        return data

    except FileNotFoundError:
        print(f"Error: File not found: {json_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {json_path}: {e}")
        sys.exit(1)


def calculate_area_differences(properties: List[Dict[str, Any]], subject_sf: float) -> List[Dict[str, Any]]:
    """
    Calculate absolute difference in area between each property and subject.

    If area_difference is already present in the property data, it will be used as-is.
    This allows for pre-calculated area differences (e.g., from Excel template).

    Args:
        properties: List of property dictionaries
        subject_sf: Square footage of subject property

    Returns:
        List of properties with area_difference field added (if not already present)
    """
    for prop in properties:
        # Only calculate if not already provided
        if 'area_difference' not in prop or prop['area_difference'] is None:
            prop['area_difference'] = abs(prop['available_sf'] - subject_sf)

    return properties


def rank_variable(values: List[float], ascending: bool = True) -> List[int]:
    """
    Rank values from 1 (best) to X (worst), handling ties with minimum rank.

    Uses "competition ranking" (1-2-2-4 method) where tied values receive
    the same rank equal to the minimum position. Matches Excel RANK function.

    Args:
        values: List of numeric values to rank
        ascending: True if lower value = better rank (e.g., rent, distance)
                   False if higher value = better rank (e.g., parking, clear height)

    Returns:
        List of ranks (1 to len(values)), matching input order

    Example:
        values = [10.0, 8.5, 9.0, 8.5]
        ascending = True
        returns = [4, 1, 3, 1]  # Ties get minimum rank
    """
    n = len(values)

    # Create list of (value, original_index) tuples
    indexed_values = [(val, idx) for idx, val in enumerate(values)]

    # Sort by value (ascending or descending based on parameter)
    indexed_values.sort(key=lambda x: x[0], reverse=not ascending)

    # Assign ranks, handling ties with minimum rank (competition ranking)
    # This matches Excel's RANK function behavior
    ranks = [0] * n
    i = 0
    while i < n:
        # Find all values tied with current value
        current_value = indexed_values[i][0]
        j = i
        while j < n and indexed_values[j][0] == current_value:
            j += 1

        # All tied values get the minimum rank (first position)
        # This is the "competition ranking" or "1224" method
        min_rank = i + 1

        for k in range(i, j):
            ranks[indexed_values[k][1]] = min_rank

        i = j

    return ranks


def detect_available_variables(properties: List[Dict[str, Any]]) -> Dict[str, bool]:
    """
    Detect which optional variables have data across the property set.

    A variable is considered "available" if:
    - For numeric fields: at least 50% of properties have non-zero values
    - For boolean fields: at least one property has True
    - For string fields: at least 50% have non-empty strings

    Args:
        properties: List of property dictionaries

    Returns:
        Dictionary mapping variable names to availability (True/False)
    """
    total = len(properties)
    threshold = total * 0.5  # 50% threshold

    # Core variables (always included)
    available = {
        'year_built': True,
        'clear_height_ft': True,
        'pct_office_space': True,
        'parking_ratio': True,
        'distance_km': True,
        'net_asking_rent': True,
        'tmi': True,
        'class': True,
        'area_difference': True
    }

    # Optional variables - check if data is available
    # Shipping doors TL
    tl_count = sum(1 for p in properties if p.get('shipping_doors_tl', 0) > 0)
    available['shipping_doors_tl'] = tl_count >= threshold

    # Shipping doors DI
    di_count = sum(1 for p in properties if p.get('shipping_doors_di', 0) > 0)
    available['shipping_doors_di'] = di_count >= threshold

    # Power
    power_count = sum(1 for p in properties if p.get('power_amps', 0) > 0)
    available['power_amps'] = power_count >= threshold

    # Trailer parking (boolean)
    trailer_count = sum(1 for p in properties if p.get('trailer_parking', False))
    available['trailer_parking'] = trailer_count > 0

    # Secure shipping (boolean)
    secure_count = sum(1 for p in properties if p.get('secure_shipping', False))
    available['secure_shipping'] = secure_count > 0

    # Excess land (boolean)
    excess_count = sum(1 for p in properties if p.get('excess_land', False))
    available['excess_land'] = excess_count > 0

    return available


def allocate_dynamic_weights(available_vars: Dict[str, bool],
                            base_weights: Dict[str, float]) -> Dict[str, float]:
    """
    Dynamically allocate weights based on which variables have data.

    Base weight allocation (when all optional vars available):
    - Net Rent: 14%
    - Parking: 13%
    - TMI: 12%
    - Clear Height: 9%
    - % Office: 9%
    - Distance: 9%
    - Area Diff: 9%
    - Year Built: 7%
    - Class: 6%
    - Shipping TL: 4%
    - Shipping DI: 3%
    - Power: 3%
    - Trailer Parking: 2%
    - Secure Shipping: 2%
    - Excess Land: 2%
    Total: 100%

    If optional variables are missing, their weights are redistributed
    proportionally among available variables.

    Args:
        available_vars: Dictionary of variable availability
        base_weights: Base weights from input (may be overridden)

    Returns:
        Adjusted weights that sum to 1.0
    """
    # Define default weights when no custom schema provided
    default_weights = {
        'net_asking_rent': 0.14,
        'parking_ratio': 0.13,
        'tmi': 0.12,
        'clear_height_ft': 0.09,
        'pct_office_space': 0.09,
        'distance_km': 0.09,
        'area_difference': 0.09,
        'year_built': 0.07,
        'class': 0.06,
        'shipping_doors_tl': 0.04,
        'shipping_doors_di': 0.03,
        'power_amps': 0.03,
        'trailer_parking': 0.02,
        'secure_shipping': 0.02,
        'excess_land': 0.02
    }

    # Helper to normalise a provided weight mapping to sum to 1.0
    def normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
        clean_weights = {
            key: float(value)
            for key, value in weights.items()
            if value is not None
        }

        if not clean_weights:
            return {}

        # Detect percentage style inputs (e.g., 16 for 16%)
        if any(abs(val) > 1 for val in clean_weights.values()):
            clean_weights = {k: v / 100.0 for k, v in clean_weights.items()}

        total = sum(clean_weights.values())
        if total <= 0:
            return {}

        return {k: v / total for k, v in clean_weights.items()}

    # Establish baseline weights: either custom (normalised) or defaults
    normalized_custom = normalize_weights(base_weights or {})
    if normalized_custom:
        baseline_weights = normalized_custom.copy()
        # Ensure all known variables exist in baseline (default to 0 for unspecified)
        for var in default_weights:
            baseline_weights.setdefault(var, 0.0)
    else:
        baseline_weights = default_weights.copy()

    # Guarantee every available variable has an entry
    for var in available_vars:
        baseline_weights.setdefault(var, 0.0)

    # Normalise baseline to avoid drift when defaults are extended
    baseline_total = sum(baseline_weights.values())
    if baseline_total <= 0:
        # If everything zero, fall back to equal weighting among available vars
        available_count = sum(1 for is_avail in available_vars.values() if is_avail)
        if available_count == 0:
            return {}
        equal_weight = round(1.0 / available_count, 4)
        return {
            var: equal_weight
            for var, is_avail in available_vars.items()
            if is_avail
        }

    baseline_weights = {
        k: v / baseline_total
        for k, v in baseline_weights.items()
    }

    # Restrict to variables that are actually available
    available_weights = {
        var: baseline_weights.get(var, 0.0)
        for var, is_avail in available_vars.items()
        if is_avail
    }

    total_available = sum(available_weights.values())
    if total_available <= 0:
        num_available = len(available_weights)
        if num_available == 0:
            return {}
        equal_weight = round(1.0 / num_available, 4)
        return {var: equal_weight for var in available_weights}

    return {
        var: round(weight / total_available, 4)
        for var, weight in available_weights.items()
    }


def calculate_weighted_score(property_data: Dict[str, Any],
                              ranks: Dict[str, int],
                              weights: Dict[str, float]) -> float:
    """
    Calculate weighted score = Σ(rank × weight) for all variables.

    Lower weighted score = better competitive position (fewer negative rank points).

    Args:
        property_data: Property dictionary with all attributes
        ranks: Dictionary of variable ranks (e.g., {'year_built': 20, 'clear_height_ft': 44})
        weights: Dictionary of variable weights (e.g., {'year_built': 0.08, 'clear_height_ft': 0.10})

    Returns:
        Weighted score (float)

    Example:
        ranks = {'year_built': 54, 'clear_height_ft': 44, 'pct_office_space': 73,
                 'parking_ratio': 3, 'distance_km': 44, 'net_asking_rent': 7,
                 'tmi': 59, 'class': 15, 'area_difference': 68}
        weights = {'year_built': 0.08, 'clear_height_ft': 0.10, 'pct_office_space': 0.10,
                   'parking_ratio': 0.15, 'distance_km': 0.10, 'net_asking_rent': 0.16,
                   'tmi': 0.14, 'class': 0.07, 'area_difference': 0.10}

        Score = (54×0.08) + (44×0.10) + (73×0.10) + (3×0.15) + (44×0.10) +
                (7×0.16) + (59×0.14) + (15×0.07) + (68×0.10)
              = 4.32 + 4.4 + 7.3 + 0.45 + 4.4 + 1.12 + 8.26 + 1.05 + 6.8
              = 38.10
    """
    score = 0.0

    # Variable name mapping from weights dict to ranks dict
    # Weights use shortened names, ranks use full field names from property
    variable_mapping = {
        'year_built': 'year_built',
        'clear_height_ft': 'clear_height_ft',
        'pct_office_space': 'pct_office_space',
        'parking_ratio': 'parking_ratio',
        'distance_km': 'distance_km',
        'net_asking_rent': 'net_asking_rent',
        'tmi': 'tmi',
        'class': 'class',
        'area_difference': 'area_difference',
        'shipping_doors_tl': 'shipping_doors_tl',
        'shipping_doors_di': 'shipping_doors_di',
        'power_amps': 'power_amps',
        'trailer_parking': 'trailer_parking',
        'secure_shipping': 'secure_shipping',
        'excess_land': 'excess_land'
    }

    for weight_key, rank_key in variable_mapping.items():
        if weight_key in weights and rank_key in ranks:
            score += ranks[rank_key] * weights[weight_key]

    return round(score, 2)


def run_sensitivity_analysis(subject: Dict[str, Any],
                              all_properties: List[Dict[str, Any]],
                              weights: Dict[str, float],
                              subject_weighted_score: float,
                              rank_3_score: float) -> List[Dict[str, Any]]:
    """
    Run rent/TMI reduction scenarios to calculate rank improvements.

    Calculates how much rent or TMI reduction is needed to move subject property
    to Rank #3 (competitive threshold).

    Args:
        subject: Subject property dictionary
        all_properties: List of all properties (for re-ranking simulation)
        weights: Variable weights
        subject_weighted_score: Current weighted score of subject
        rank_3_score: Weighted score of property ranked #3

    Returns:
        List of scenario dictionaries with estimated impacts
    """
    scenarios = []

    # Calculate gap to Rank #3
    gap_points = subject_weighted_score - rank_3_score

    if gap_points <= 0:
        # Already at or better than Rank #3
        return scenarios

    # Scenario 1: Net Rent Reduction
    # Net rent weighted at 16%, so gap_points / 0.16 = rank improvement needed
    # Estimate: Each ~$0.05/sf reduction = ~1 rank improvement (market dependent)
    # Conservative estimate: Use $0.05/sf per rank
    net_rent_weight = weights.get('net_asking_rent', 0.16)
    ranks_needed = gap_points / net_rent_weight if net_rent_weight > 0 else 0
    rent_reduction = round(ranks_needed * 0.05, 2)  # $0.05/sf per rank

    scenarios.append({
        "scenario": "Net Rent Reduction",
        "reduction_amount": rent_reduction,
        "new_net_asking_rent": round(subject['net_asking_rent'] - rent_reduction, 2),
        "estimated_new_rank": 3,
        "estimated_new_score": round(rank_3_score, 2),
        "explanation": f"Reduce rent by ${rent_reduction}/sf to close {gap_points:.2f} point gap"
    })

    # Scenario 2: TMI Reduction
    # TMI weighted at 14%
    tmi_weight = weights.get('tmi', 0.14)
    ranks_needed_tmi = gap_points / tmi_weight if tmi_weight > 0 else 0
    tmi_reduction = round(ranks_needed_tmi * 0.05, 2)

    scenarios.append({
        "scenario": "TMI Reduction",
        "reduction_amount": tmi_reduction,
        "new_tmi": round(subject['tmi'] - tmi_reduction, 2),
        "estimated_new_rank": 4,  # TMI has less weight than rent, so might only get to #4
        "estimated_new_score": round(rank_3_score + 0.2, 2),
        "explanation": f"Reduce TMI by ${tmi_reduction}/sf (negotiate with property manager)"
    })

    # Scenario 3: Combined Rent + TMI Reduction (smaller amounts)
    combined_rent_reduction = round(rent_reduction * 0.5, 2)
    combined_tmi_reduction = round(tmi_reduction * 0.5, 2)

    scenarios.append({
        "scenario": "Combined Rent + TMI Reduction",
        "rent_reduction": combined_rent_reduction,
        "tmi_reduction": combined_tmi_reduction,
        "new_net_asking_rent": round(subject['net_asking_rent'] - combined_rent_reduction, 2),
        "new_tmi": round(subject['tmi'] - combined_tmi_reduction, 2),
        "estimated_new_rank": 3,
        "estimated_new_score": round(rank_3_score, 2),
        "explanation": f"Split adjustment: ${combined_rent_reduction}/sf rent + ${combined_tmi_reduction}/sf TMI"
    })

    return scenarios


def generate_competitive_report(results: CompetitiveAnalysis, output_path: str, full: bool = False):
    """
    Generate professional markdown report with rankings and recommendations.

    Args:
        results: CompetitiveAnalysis dataclass with all analysis results
        output_path: Path to output markdown file
        full: If True, show all competitors; if False, show top 10 only (default)
    """
    subject = results.subject_property

    # Determine competitive status and deal-winning probability
    rank = subject['final_rank']
    if rank <= 3:
        status = "HIGHLY COMPETITIVE"
        probability = "70-90%"
        status_emoji = "✅"
        interpretation = "Your property is in the TOP 3 - you are well-positioned to win deals at current pricing."
    elif rank <= 10:
        status = "MARGINALLY COMPETITIVE"
        probability = "30-50%"
        status_emoji = "⚠️"
        interpretation = f"{rank - 3} properties offer better value. You MUST reduce rent or increase incentives to compete."
    elif rank <= 20:
        status = "WEAK POSITION"
        probability = "10-25%"
        status_emoji = "❌"
        interpretation = f"SERIOUS COMPETITIVE DISADVANTAGE. {rank - 3} properties offer superior value - major price reduction required."
    else:
        status = "NOT COMPETITIVE"
        probability = "<10%"
        status_emoji = "🚫"
        interpretation = f"FUNDAMENTALLY UNCOMPETITIVE. Consider repositioning, capital investment, or exit strategy."

    report = f"""# RELATIVE VALUATION ANALYSIS - COMPETITIVE POSITIONING REPORT

**Report Date**: {results.analysis_date}
**Market**: {results.market}
**Total Comparables Analyzed**: {results.total_properties}
**Subject Property**: {subject['address']} {subject.get('unit', '')}

---

## 🎯 EXECUTIVE SUMMARY

### **Competitive Position**

| Metric | Value |
|--------|-------|
| **Final Ranking** | **#{subject['final_rank']} out of {results.total_properties}** |
| **Weighted Score** | **{subject['weighted_score']:.2f}** (lower is better) |
| **Competitive Status** | {status_emoji} **{status}** |
| **Deal-Winning Probability** | **{probability}** |

### **Interpretation**

{interpretation}

---

## 📊 SUBJECT PROPERTY ANALYSIS

### **Property Details**

| Attribute | Value |
|-----------|-------|
| **Address** | {subject['address']} |
| **Unit** | {subject.get('unit', 'N/A')} |
| **Year Built** | {subject.get('year_built', 'N/A')} |
| **Clear Height** | {subject.get('clear_height_ft', 'N/A')} ft |
| **% Office Space** | {subject.get('pct_office_space', 0) * 100:.1f}% |
| **Parking Ratio** | {subject.get('parking_ratio', 'N/A')} spaces/1,000 sf |
| **Available SF** | {subject.get('available_sf', 'N/A'):,.0f} |
| **Net Asking Rent** | ${subject.get('net_asking_rent', 0):.2f}/sf |
| **TMI** | ${subject.get('tmi', 0):.2f}/sf |
| **Gross Rent** | ${(subject.get('net_asking_rent', 0) + subject.get('tmi', 0)):.2f}/sf |
| **Class** | {'A' if subject.get('class', 2) == 1 else 'B' if subject.get('class', 2) == 2 else 'C'} |"""

    # Add optional fields if available
    if subject.get('shipping_doors_tl'):
        report += f"\n| **Shipping Doors (Truck-Level)** | {subject.get('shipping_doors_tl', 0)} |"
    if subject.get('shipping_doors_di'):
        report += f"\n| **Shipping Doors (Drive-In)** | {subject.get('shipping_doors_di', 0)} |"
    if subject.get('power_amps'):
        report += f"\n| **Power** | {subject.get('power_amps', 0)} amps |"
    if subject.get('availability_date'):
        report += f"\n| **Availability Date** | {subject.get('availability_date', '')} |"
    report += f"\n| **Trailer Parking** | {'Yes' if subject.get('trailer_parking', False) else 'No'} |"
    report += f"\n| **Secure Shipping** | {'Yes' if subject.get('secure_shipping', False) else 'No'} |"
    report += f"\n| **Excess Land** | {'Yes' if subject.get('excess_land', False) else 'No'} |"

    report += f"""

### **Variable Rankings**

| Variable | Rank | Interpretation |
|----------|------|----------------|
| Year Built | {subject.get('rank_year_built', 'N/A')} | {'Excellent' if subject.get('rank_year_built', 999) <= 20 else 'Good' if subject.get('rank_year_built', 999) <= 50 else 'Moderate' if subject.get('rank_year_built', 999) <= 80 else 'Poor'} |
| Clear Height | {subject.get('rank_clear_height', 'N/A')} | {'Excellent' if subject.get('rank_clear_height', 999) <= 20 else 'Good' if subject.get('rank_clear_height', 999) <= 50 else 'Moderate' if subject.get('rank_clear_height', 999) <= 80 else 'Poor'} |
| % Office Space | {subject.get('rank_pct_office', 'N/A')} | {'Excellent' if subject.get('rank_pct_office', 999) <= 20 else 'Good' if subject.get('rank_pct_office', 999) <= 50 else 'Moderate' if subject.get('rank_pct_office', 999) <= 80 else 'Poor'} |
| Parking Ratio | {subject.get('rank_parking', 'N/A')} | {'Excellent' if subject.get('rank_parking', 999) <= 20 else 'Good' if subject.get('rank_parking', 999) <= 50 else 'Moderate' if subject.get('rank_parking', 999) <= 80 else 'Poor'} |
| Distance | {subject.get('rank_distance', 'N/A')} | Subject property (0 km - center point) |
| **Net Rent** | **{subject.get('rank_net_rent', 'N/A')}** | **16% weight - most critical for competitiveness** |
| **TMI** | **{subject.get('rank_tmi', 'N/A')}** | **14% weight - affects total occupancy cost** |
| Class | {subject.get('rank_class', 'N/A')} | {'Excellent' if subject.get('rank_class', 999) <= 20 else 'Good' if subject.get('rank_class', 999) <= 50 else 'Moderate' if subject.get('rank_class', 999) <= 80 else 'Poor'} |
| Area Difference | {subject.get('rank_area_diff', 'N/A')} | {'Excellent' if subject.get('rank_area_diff', 999) <= 20 else 'Good' if subject.get('rank_area_diff', 999) <= 50 else 'Moderate' if subject.get('rank_area_diff', 999) <= 80 else 'Poor'} size match |

**Lower rank number = better competitive position for that variable.**

---

## 🏆 {'ALL' if full else 'TOP 10'} COMPETITORS

These properties offer the best value propositions in the market:

| Rank | Property | Area (SF) | Net Rent | TMI | Gross Rent | Clear Ht | Ship TL | Ship DI | Power | Trailer | Avail Date | Score |
|------|----------|-----------|----------|-----|------------|----------|---------|---------|-------|---------|------------|-------|
"""

    # Add competitors (top 10 or all based on --full flag)
    competitors_to_show = results.all_properties if full else results.top_competitors
    for comp in competitors_to_show:
        # Format optional fields
        area_sf = f"{comp.get('available_sf', 0):,.0f}"
        clear_ht = f"{comp.get('clear_height_ft', 0):.0f} ft"
        ship_tl = comp.get('shipping_doors_tl', 0) if comp.get('shipping_doors_tl') else '-'
        ship_di = comp.get('shipping_doors_di', 0) if comp.get('shipping_doors_di') else '-'
        power = f"{comp.get('power_amps', 0)}" if comp.get('power_amps') else '-'
        trailer = 'Yes' if comp.get('trailer_parking', False) else 'No'
        avail = comp.get('availability_date', '-')

        report += f"| {comp['final_rank']} | {comp['address']} {comp.get('unit', '')} | {area_sf} | ${comp.get('net_asking_rent', 0):.2f} | ${comp.get('tmi', 0):.2f} | ${comp.get('gross_rent', 0):.2f} | {clear_ht} | {ship_tl} | {ship_di} | {power} | {trailer} | {avail} | {comp['weighted_score']:.2f} |\n"

    # Gap Analysis
    gap = results.gap_analysis
    report += f"""

---

## 📉 GAP ANALYSIS

### **Distance to Competitive Threshold (Rank #3)**

| Metric | Value |
|--------|-------|
| **Subject Weighted Score** | {subject['weighted_score']:.2f} |
| **Rank #3 Weighted Score** | {gap.get('rank_3_score', 'N/A'):.2f} |
| **Rank #3 Property** | {gap.get('rank_3_property', 'N/A')} |
| **Gap to Close** | **{gap.get('gap_to_rank_3', 0):.2f} points** |

**To achieve Rank #3 and become competitive, subject must improve weighted score by {gap.get('gap_to_rank_3', 0):.2f} points.**

---

## 💡 RECOMMENDED ACTIONS

### **Sensitivity Analysis: Pricing Adjustments to Achieve Rank #3**

"""

    # Add sensitivity scenarios
    for i, scenario in enumerate(results.sensitivity_scenarios, 1):
        report += f"### **Option {i}: {scenario['scenario']}**\n\n"

        if 'reduction_amount' in scenario:
            report += f"- **Reduction**: ${scenario['reduction_amount']:.2f}/sf\n"
            if 'new_net_asking_rent' in scenario:
                report += f"- **New Net Rent**: ${scenario['new_net_asking_rent']:.2f}/sf\n"
            if 'new_tmi' in scenario:
                report += f"- **New TMI**: ${scenario['new_tmi']:.2f}/sf\n"

        if 'rent_reduction' in scenario and 'tmi_reduction' in scenario:
            report += f"- **Rent Reduction**: ${scenario['rent_reduction']:.2f}/sf\n"
            report += f"- **TMI Reduction**: ${scenario['tmi_reduction']:.2f}/sf\n"
            report += f"- **New Net Rent**: ${scenario['new_net_asking_rent']:.2f}/sf\n"
            report += f"- **New TMI**: ${scenario['new_tmi']:.2f}/sf\n"

        report += f"- **Estimated New Rank**: #{scenario['estimated_new_rank']}\n"
        report += f"- **Estimated New Score**: {scenario['estimated_new_score']:.2f}\n"
        report += f"- **Explanation**: {scenario.get('explanation', '')}\n\n"

    # Final recommendations
    if rank <= 3:
        recommendation = """### **RECOMMENDATION: HOLD OR INCREASE PRICING**

Your property is in the Top 3 - you have strong competitive positioning. Consider:
- **Hold current pricing** and maintain selectivity on tenant quality
- **Increase rent by $0.25-0.50/sf** if market velocity is strong
- **Minimize concessions** - offer standard TI only (no above-market incentives)
- **Favor landlord-friendly lease terms** (shorter free rent, higher deposits)
"""
    elif rank <= 10:
        recommendation = f"""### **RECOMMENDATION: REDUCE PRICING OR INCREASE INCENTIVES**

You are ranked #{rank} - **{rank - 3} properties offer better value**. To compete effectively:
- **Implement Option 1** (recommended): Reduce net rent by indicated amount
- **Alternative**: Offer above-market TI allowance (${gap.get('gap_to_rank_3', 0) * 5:.2f}/sf)
- **Alternative**: Increase free rent period (add {int(gap.get('gap_to_rank_3', 0) / 2)} months)
- **Monitor market**: Re-run analysis in 60 days if no LOI activity
"""
    else:
        recommendation = f"""### **RECOMMENDATION: AGGRESSIVE PRICING REDUCTION OR REPOSITIONING**

You are ranked #{rank} - **SERIOUS COMPETITIVE DISADVANTAGE**. Consider:
- **Aggressive rent reduction**: ${gap.get('gap_to_rank_3', 0) * 0.10:.2f}/sf or more
- **Capital investment**: Address structural weaknesses (parking, clear height, building age)
- **Reposition**: Convert to alternative use (self-storage, last-mile delivery, etc.)
- **Exit strategy**: Sell to value-add investor or owner-user

Price reduction alone may not be sufficient to overcome structural disadvantages.
"""

    report += recommendation

    # Methodology footnote
    report += f"""
---

## 📖 METHODOLOGY

This analysis uses a **multi-criteria weighted ranking system** to objectively assess competitive position:

1. **Data Collection**: Extract 9 key variables from comparable evidence
2. **Variable Weighting**: Assign importance weights totaling 100% (Net Rent 16%, Parking 15%, TMI 14%, etc.)
3. **Independent Ranking**: Rank each variable 1 (best) to X (worst) across all properties
4. **Weighted Score Calculation**: Sum of (rank × weight) for all variables
5. **Final Re-Ranking**: Sort properties by weighted score (lower = better)

**Key Variables**:
- **Net Asking Rent** (16%) - Most critical factor
- **Parking Ratio** (15%) - Essential for industrial/suburban office
- **TMI** (14%) - Total occupancy cost driver
- **Clear Height, % Office, Distance, Year Built, Area Match** (8-10% each)
- **Class** (7%) - Quality tier

**Lower weighted score = fewer negative rank points = better competitive position**

---

## ⚠️ LIMITATIONS

- Model excludes qualitative factors (landlord reputation, property management quality, amenities)
- Weights represent average tenant priorities; individual tenants may weight factors differently
- Asking rents may not reflect net effective rents after concessions
- Rankings are point-in-time snapshots; market conditions change

**Validation**: Always confirm model results with market intelligence from brokers and recent lease transactions.

---

**END OF REPORT**

*Generated by: Relative Valuation Calculator v1.0.0*
*Analysis Date: {results.analysis_date}*
*Report Generated: {datetime.now(ZoneInfo('America/New_York')).strftime('%Y-%m-%d %H:%M:%S')} ET*
"""

    # Write report to file
    with open(output_path, 'w') as f:
        f.write(report)

    print(f"\n✅ Report generated: {output_path}")


def run_analysis(data: Dict[str, Any]) -> CompetitiveAnalysis:
    """
    Run complete relative valuation analysis.

    Args:
        data: Dictionary with analysis_date, market, subject_property, comparables, weights

    Returns:
        CompetitiveAnalysis results object
    """
    print("\n🔍 Running Relative Valuation Analysis...")

    # Extract components
    analysis_date = data['analysis_date']
    market = data['market']
    subject_data = data['subject_property']
    comparables_data = data['comparables']
    weights = data['weights']

    # Combine subject + comparables into single list
    all_properties_data = [subject_data] + comparables_data

    # Calculate area differences
    subject_sf = subject_data['available_sf']
    all_properties_data = calculate_area_differences(all_properties_data, subject_sf)

    print(f"   Loaded {len(all_properties_data)} properties")
    print(f"   Subject: {subject_data['address']} {subject_data.get('unit', '')}")

    # Detect available optional variables
    print("\n   Detecting available variables...")
    available_vars = detect_available_variables(all_properties_data)
    num_available = sum(1 for v in available_vars.values() if v)
    print(f"   Using {num_available} of 15 possible variables")

    # Allocate weights dynamically based on available data
    dynamic_weights = allocate_dynamic_weights(available_vars, weights)
    print(f"   Dynamic weights calculated:")
    for var, weight in sorted(dynamic_weights.items(), key=lambda x: -x[1]):
        print(f"      {var}: {weight:.1%}")

    # Extract values for each variable
    year_builts = [p['year_built'] for p in all_properties_data]
    clear_heights = [p['clear_height_ft'] for p in all_properties_data]
    pct_offices = [p['pct_office_space'] for p in all_properties_data]
    parking_ratios = [p['parking_ratio'] for p in all_properties_data]
    distances = [p['distance_km'] for p in all_properties_data]
    net_rents = [p['net_asking_rent'] for p in all_properties_data]
    tmis = [p['tmi'] for p in all_properties_data]
    classes = [p.get('class', 2) for p in all_properties_data]
    area_diffs = [p['area_difference'] for p in all_properties_data]

    # Rank each variable
    # Variables where LOWER = BETTER (ascending=True): rent, TMI, distance, class, area_diff
    # Variables where HIGHER = BETTER (ascending=False): clear_height, parking, % office, year_built, shipping doors, power, boolean amenities
    print("\n   Ranking variables...")

    ranks_year_built = rank_variable(year_builts, ascending=False)  # Newer (higher year) = better
    ranks_clear_height = rank_variable(clear_heights, ascending=False)  # Higher = better
    ranks_pct_office = rank_variable(pct_offices, ascending=False)  # Higher = better (for office users)
    ranks_parking = rank_variable(parking_ratios, ascending=False)  # More parking = better
    ranks_distance = rank_variable(distances, ascending=True)  # Closer (lower km) = better
    ranks_net_rent = rank_variable(net_rents, ascending=True)  # Lower rent = better
    ranks_tmi = rank_variable(tmis, ascending=True)  # Lower TMI = better
    ranks_class = rank_variable(classes, ascending=True)  # Lower class number (A=1) = better
    ranks_area_diff = rank_variable(area_diffs, ascending=True)  # Smaller difference = better

    # Rank optional variables if available
    ranks_shipping_tl = None
    ranks_shipping_di = None
    ranks_power = None
    ranks_trailer_parking = None
    ranks_secure_shipping = None
    ranks_excess_land = None

    if available_vars.get('shipping_doors_tl', False):
        shipping_tl_values = [p.get('shipping_doors_tl', 0) for p in all_properties_data]
        ranks_shipping_tl = rank_variable(shipping_tl_values, ascending=False)  # More doors = better

    if available_vars.get('shipping_doors_di', False):
        shipping_di_values = [p.get('shipping_doors_di', 0) for p in all_properties_data]
        ranks_shipping_di = rank_variable(shipping_di_values, ascending=False)  # More doors = better

    if available_vars.get('power_amps', False):
        power_values = [p.get('power_amps', 0) for p in all_properties_data]
        ranks_power = rank_variable(power_values, ascending=False)  # More power = better

    if available_vars.get('trailer_parking', False):
        trailer_values = [1 if p.get('trailer_parking', False) else 0 for p in all_properties_data]
        ranks_trailer_parking = rank_variable(trailer_values, ascending=False)  # True = better

    if available_vars.get('secure_shipping', False):
        secure_values = [1 if p.get('secure_shipping', False) else 0 for p in all_properties_data]
        ranks_secure_shipping = rank_variable(secure_values, ascending=False)  # True = better

    if available_vars.get('excess_land', False):
        excess_values = [1 if p.get('excess_land', False) else 0 for p in all_properties_data]
        ranks_excess_land = rank_variable(excess_values, ascending=False)  # True = better

    # Calculate weighted scores
    print("   Calculating weighted scores...")
    for i, prop in enumerate(all_properties_data):
        # Build ranks_dict with core variables
        ranks_dict = {
            'year_built': ranks_year_built[i],
            'clear_height_ft': ranks_clear_height[i],
            'pct_office_space': ranks_pct_office[i],
            'parking_ratio': ranks_parking[i],
            'distance_km': ranks_distance[i],
            'net_asking_rent': ranks_net_rent[i],
            'tmi': ranks_tmi[i],
            'class': ranks_class[i],
            'area_difference': ranks_area_diff[i]
        }

        # Add optional variable ranks if available
        if ranks_shipping_tl is not None:
            ranks_dict['shipping_doors_tl'] = ranks_shipping_tl[i]
        if ranks_shipping_di is not None:
            ranks_dict['shipping_doors_di'] = ranks_shipping_di[i]
        if ranks_power is not None:
            ranks_dict['power_amps'] = ranks_power[i]
        if ranks_trailer_parking is not None:
            ranks_dict['trailer_parking'] = ranks_trailer_parking[i]
        if ranks_secure_shipping is not None:
            ranks_dict['secure_shipping'] = ranks_secure_shipping[i]
        if ranks_excess_land is not None:
            ranks_dict['excess_land'] = ranks_excess_land[i]

        # Assign core variable ranks to property
        prop['rank_year_built'] = int(ranks_year_built[i])
        prop['rank_clear_height'] = int(ranks_clear_height[i])
        prop['rank_pct_office'] = int(ranks_pct_office[i])
        prop['rank_parking'] = int(ranks_parking[i])
        prop['rank_distance'] = int(ranks_distance[i])
        prop['rank_net_rent'] = int(ranks_net_rent[i])
        prop['rank_tmi'] = int(ranks_tmi[i])
        prop['rank_class'] = int(ranks_class[i])
        prop['rank_area_diff'] = int(ranks_area_diff[i])

        # Assign optional variable ranks to property
        prop['rank_shipping_doors_tl'] = int(ranks_shipping_tl[i]) if ranks_shipping_tl else 0
        prop['rank_shipping_doors_di'] = int(ranks_shipping_di[i]) if ranks_shipping_di else 0
        prop['rank_power'] = int(ranks_power[i]) if ranks_power else 0
        prop['rank_trailer_parking'] = int(ranks_trailer_parking[i]) if ranks_trailer_parking else 0
        prop['rank_secure_shipping'] = int(ranks_secure_shipping[i]) if ranks_secure_shipping else 0
        prop['rank_excess_land'] = int(ranks_excess_land[i]) if ranks_excess_land else 0

        # Calculate weighted score using DYNAMIC weights
        prop['weighted_score'] = calculate_weighted_score(prop, ranks_dict, dynamic_weights)

    # Sort by weighted score (ascending - lower is better)
    all_properties_data.sort(key=lambda x: x['weighted_score'])

    # Assign final ranks
    for i, prop in enumerate(all_properties_data):
        prop['final_rank'] = i + 1
        prop['gross_rent'] = round(prop['net_asking_rent'] + prop['tmi'], 2)

    print("   Final rankings assigned")

    # Find subject property
    subject_result = next((p for p in all_properties_data if p.get('is_subject', False)), None)
    if not subject_result:
        raise ValueError("Subject property not found in results (check is_subject flag)")

    subject_rank = subject_result['final_rank']
    print(f"\n   ✅ Subject Property Rank: #{subject_rank} out of {len(all_properties_data)}")
    print(f"   Weighted Score: {subject_result['weighted_score']:.2f}")

    # Get top 10 competitors
    top_10 = all_properties_data[:10]

    # Gap analysis
    if len(all_properties_data) >= 3:
        rank_3_property = all_properties_data[2]
        gap_to_rank_3 = subject_result['weighted_score'] - rank_3_property['weighted_score']
        gap_analysis = {
            'gap_to_rank_3': round(gap_to_rank_3, 2),
            'rank_3_score': round(rank_3_property['weighted_score'], 2),
            'rank_3_property': f"{rank_3_property['address']} {rank_3_property.get('unit', '')}"
        }
    else:
        gap_analysis = {
            'gap_to_rank_3': 0.0,
            'rank_3_score': 0.0,
            'rank_3_property': 'N/A'
        }

    # Run sensitivity analysis
    print("\n   Running sensitivity analysis...")
    sensitivity_scenarios = run_sensitivity_analysis(
        subject_result,
        all_properties_data,
        weights,
        subject_result['weighted_score'],
        gap_analysis['rank_3_score']
    )

    # Build results object
    results = CompetitiveAnalysis(
        analysis_date=analysis_date,
        market=market,
        total_properties=len(all_properties_data),
        subject_property=subject_result,
        top_competitors=top_10,
        gap_analysis=gap_analysis,
        sensitivity_scenarios=sensitivity_scenarios,
        all_properties=all_properties_data
    )

    return results


def main():
    """Main entry point for command-line interface."""
    parser = argparse.ArgumentParser(
        description='Relative Valuation Calculator - Competitive Positioning Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate markdown report (top 10 competitors)
  python relative_valuation_calculator.py --input data.json --output report.md

  # Generate markdown report with ALL competitors
  python relative_valuation_calculator.py --input data.json --output report.md --full

  # Generate JSON results only
  python relative_valuation_calculator.py --input data.json --output-json results.json

  # Generate both markdown and JSON with full competitor list
  python relative_valuation_calculator.py --input data.json --output report.md --output-json results.json --full
        """
    )

    parser.add_argument('--input', required=True, help='Path to JSON input file')
    parser.add_argument('--output', help='Path to output markdown report (optional)')
    parser.add_argument('--output-json', help='Path to output JSON results (optional)')
    parser.add_argument('--full', action='store_true', help='Show all competitors in report (default: top 10 only)')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode (not implemented in Phase 1)')

    args = parser.parse_args()

    if args.interactive:
        print("❌ Interactive mode not implemented in Phase 1")
        sys.exit(1)

    if not args.output and not args.output_json:
        print("❌ Error: Must specify --output (markdown) or --output-json (JSON results)")
        sys.exit(1)

    # Load data
    print(f"\n📂 Loading data from: {args.input}")
    data = load_comparable_data(args.input)

    # Run analysis
    results = run_analysis(data)

    # Generate outputs
    if args.output_json:
        with open(args.output_json, 'w') as f:
            json.dump(asdict(results), f, indent=2, default=str)
        print(f"✅ JSON results saved: {args.output_json}")

    if args.output:
        generate_competitive_report(results, args.output, full=args.full)

    print("\n✅ Analysis complete!\n")


if __name__ == '__main__':
    main()
