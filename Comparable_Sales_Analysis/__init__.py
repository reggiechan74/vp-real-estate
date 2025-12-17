"""Comparable Sales Analysis Calculator - Traditional DCA with dollar adjustments.

This module implements the traditional Direct Comparison Approach (DCA) methodology
using quantified dollar adjustments for property valuation. It follows the
hierarchical sequence established by AACI/appraisal standards:

    Property Rights → Financing → Conditions of Sale → Market Conditions (Time)
    → Location → Physical Characteristics

Unlike MCDA ordinal ranking (in MCDA_Sales_Comparison/), this calculator applies
specific dollar adjustments from market-extracted evidence (paired sales analysis,
cost analysis, income analysis) to derive indicated values from comparables.

Key Components:
    - comparable_sales_calculator.py: Main calculator with adjustment grid construction
    - paired_sales_analyzer.py: Extract adjustments from paired sales analysis
    - validate_comparables.py: Input validation and data quality checks
    - adjustments/: Modular adjustment calculation by category

Usage:
    python comparable_sales_calculator.py input.json --output results.json --verbose
"""
