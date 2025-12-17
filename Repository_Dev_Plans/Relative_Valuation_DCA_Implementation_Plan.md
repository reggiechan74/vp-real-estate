# Implementation Plan: MCDA Sales Comparison for Fee Simple Valuation

## Multi-Criteria Decision Analysis (MCDA) Approach to Direct Comparison

**Version:** 1.0
**Date:** December 2025
**Status:** Planning
**Estimated Effort:** 3-5 days

---

## 1. Executive Summary

This document outlines the implementation plan for a new slash command `/mcda-sales-comparison` that applies the Multi-Criteria Decision Analysis (MCDA) methodology to fee simple sales valuation. This approach is **distinct from traditional paired-sales DCA** - it uses ordinal ranking and score-to-price mapping rather than dollar adjustment derivation. The implementation will **reuse significant components** from the existing `/relative-valuation` leasing tool while adapting for sales-specific requirements.

### Naming Convention Rationale

| Term | Meaning |
|------|---------|
| **MCDA** | Multi-Criteria Decision Analysis - the underlying methodology |
| **Traditional DCA** | Paired-sales adjustment approach (dollar adjustments per characteristic) |
| **MCDA Sales Comparison** | This implementation - ordinal ranking with score-to-price mapping |

### Key Differences from Leasing Tool

| Aspect | Leasing (`/relative-valuation`) | Sales (`/mcda-sales-comparison`) |
|--------|--------------------------------|----------------------------|
| **Dependent variable** | Asking rent ($/SF/year) | Sale price ($/SF or total) |
| **Output** | Competitive ranking + pricing strategy | Indicated market value |
| **Score interpretation** | "Top 3 to win deals" | "Score maps to price" |
| **Primary use case** | Marketing/pricing decisions | Appraisal/valuation |
| **Regulatory context** | None | USPAP/CUSPAP compliance |

### Reusable Components (70% of codebase)

| Component | Reuse Level | Notes |
|-----------|-------------|-------|
| Ranking engine | 90% | Add optional hybrid rank+distance scoring to mitigate magnitude loss |
| Weight application | 100% | Same MCDA math |
| Input schema validation | 80% | Add sale price, remove rent fields |
| Distance calculator | 100% | Same API |
| Report generator | 50% | Different output format |
| Sensitivity analysis | 90% | Adapt for value instead of rank; include leave-one-out impacts |
| Statistical analysis | 80% | Add regression/monotone fit for score-to-price |

---

## 2. Architecture Overview

### 2.1 File Structure

```
/workspaces/lease-abstract/
├── .claude/
│   └── commands/
│       └── Valuation/
│           └── mcda-sales-comparison.md     # NEW: Slash command definition
│
├── MCDA_Sales_Comparison/                    # NEW: Calculator directory
│   ├── mcda_sales_calculator.py             # NEW: Main calculator (adapts relative_valuation_calculator.py)
│   ├── ranking_engine.py                    # SHARED: Import from Relative_Valuation
│   ├── weight_profiles.py                   # ADAPTED: Sales-specific weights
│   ├── score_to_price.py                    # NEW: Score-to-price mapping (interpolation + regression)
│   ├── validation.py                        # ADAPTED: Sales-specific validation
│   ├── schema_template.json                 # NEW: Sales input schema
│   ├── SCHEMA.md                            # NEW: Schema documentation
│   ├── pdf_style.css                        # SHARED: Import from Relative_Valuation
│   └── tests/
│       └── test_mcda_sales_calculator.py    # NEW: Unit tests
│
├── Relative_Valuation/                       # EXISTING
│   ├── relative_valuation_calculator.py     # Source for adaptation
│   ├── ranking_engine.py                    # Will be shared
│   ├── calculate_distances.py               # Will be shared
│   ├── weight_profiles.py                   # Source for adaptation
│   ├── schema_template.json                 # Source for adaptation
│   └── ...
│
└── Shared_Utils/                             # EXISTING
    ├── financial_utils.py                   # NPV, regression utilities
    └── statistics_utils.py                  # R², confidence intervals
```

### 2.2 Module Dependencies

```
┌─────────────────────────────────────────────────────────────────┐
│                  MCDA SALES COMPARISON CALCULATOR               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐   ┌─────────────────┐                    │
│  │ Slash Command    │──▶│ Main Calculator │                    │
│  │ /mcda-sales-     │   │ mcda_sales_     │                    │
│  │   comparison     │   │ calculator.py   │                    │
│  └──────────────────┘   └────────┬────────┘                    │
│                                   │                             │
│            ┌──────────────────────┼──────────────────────┐      │
│            │                      │                      │      │
│            ▼                      ▼                      ▼      │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │  ranking_engine │    │ score_to_price  │    │  validation │ │
│  │  (SHARED)       │    │ (NEW)           │    │  (ADAPTED)  │ │
│  └─────────────────┘    └─────────────────┘    └─────────────┘ │
│            │                      │                      │      │
│            │                      ▼                      │      │
│            │           ┌─────────────────┐               │      │
│            │           │ Shared_Utils/   │               │      │
│            │           │ statistics_utils│               │      │
│            │           └─────────────────┘               │      │
│            │                                                    │
│            ▼                                                    │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │ weight_profiles │    │calculate_distances                   │
│  │ (ADAPTED)       │    │ (SHARED)        │                    │
│  └─────────────────┘    └─────────────────┘                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Component Specifications

### 3.1 Slash Command: `/mcda-sales-comparison`

**File:** `.claude/commands/Valuation/mcda-sales-comparison.md`

**Frontmatter:**
```yaml
---
description: Ordinal Ranking DCA - ranks subject against comparable sales using weighted MCDA methodology, maps composite score to indicated market value
argument-hint: <sales-data-path> [--output <report-path>]
allowed-tools: Read, Write, Bash
---
```

**Key Sections:**

1. **Objective:** Determine indicated fee simple market value using ordinal ranking methodology
2. **Input Processing:** Extract subject + comparable sales from PDF/JSON
3. **Ranking Engine:** Rank all properties on each characteristic
4. **Score Calculation:** Apply weights, compute composite scores
5. **Score-to-Price Mapping:** Interpolation or regression to derive value
6. **Validation:** R², residual analysis, sensitivity testing
7. **Report Generation:** USPAP/CUSPAP compliant markdown report

### 3.2 Main Calculator: `mcda_sales_calculator.py`

**Adaptation from:** `Relative_Valuation/relative_valuation_calculator.py`

**Key Changes:**

| Function | Leasing Version | Sales Version |
|----------|-----------------|---------------|
| `load_data()` | Loads asking rent | Loads sale price, sale date |
| `rank_properties()` | Identical | Identical (import from shared) |
| `calculate_scores()` | Identical | Identical |
| `apply_scoring_transform()` | - | Optional hybrid rank+distance/quantile scoring to preserve magnitude |
| `normalize_prices()` | - | Normalize to cash-equivalent and valuation date |
| `determine_position()` | Returns rank # | Returns indicated value |
| `generate_report()` | Competitive positioning | Valuation report |
| **NEW** `score_to_price_mapping()` | - | Interpolation + regression |
| **NEW** `compliance_disclosure()` | - | USPAP/CUSPAP statements |

**CLI Interface:**
```bash
python3 MCDA_Sales_Comparison/mcda_sales_calculator.py \
  --input Reports/YYYY-MM-DD_HHMMSS_mcda_sales_input.json \
  --output Reports/YYYY-MM-DD_HHMMSS_mcda_sales_report.md \
  --output-json Reports/YYYY-MM-DD_HHMMSS_mcda_sales_output.json \
  --mapping-method [interpolation|regression|both] \
  --property-type [industrial|office|retail] \
  --stats
```

### 3.3 Score-to-Price Mapping: `score_to_price.py` (NEW)

**Functions:**

```python
def interpolate_value(subject_score: float, comparables: List[Dict]) -> Dict:
    """
    Linear interpolation between bracketing comparables.

    Returns:
        {
            'indicated_value_psf': float,
            'indicated_value_total': float,
            'lower_bracket': Dict,  # Comparable with score just below subject
            'upper_bracket': Dict,  # Comparable with score just above subject
            'interpolation_factor': float,  # 0-1, position between brackets
            'confidence': str  # 'high' if tight brackets, 'medium' otherwise
        }
    """

def regression_value(subject_score: float, comparables: List[Dict], method: str = "ols") -> Dict:
    """
    Fit price vs. score with monotonic constraint preference; fall back to OLS.

    method options:
      - "monotone": isotonic/monotone regression (preferred for small n, enforces decreasing price with score)
      - "ols": ordinary least squares
      - "theil_sen": robust slope estimate for small n

    Returns:
        {
            'indicated_value_psf': float,
            'indicated_value_total': float,
            'alpha': float,  # Intercept (if applicable)
            'beta': float,   # Slope (should be negative)
            'r_squared': float,
            'std_error': float,
            'confidence_interval_95': Tuple[float, float],
            'residuals': List[Dict],          # Per-comparable residuals
            'outliers': List[Dict],           # Residuals > 2 std dev
            'loo_r_squared': float,           # Leave-one-out R²
            'loo_value_range_psf': Tuple[float,float],  # Subject prediction min/max across LOO
            'method_used': str                # Final method applied
        }
    """

def reconcile_methods(interpolation: Dict, regression: Dict) -> Dict:
    """
    Reconcile interpolation and regression results.

    Returns:
        {
            'indicated_value_psf': float,  # Weighted average
            'indicated_value_total': float,
            'method_weights': Dict,  # {'interpolation': 0.5, 'regression': 0.5}
            'reconciliation_rationale': str
        }
    """

# Small-sample guidance: default to interpolation for n<7; if regression used with small n, apply monotone or Theil-Sen fit and report LOO ranges to show instability.
```

### 3.4 Weight Profiles: `weight_profiles.py` (ADAPTED)

**Adaptation from:** `Relative_Valuation/weight_profiles.py`

**Sales-Specific Profiles:**

```python
SALES_WEIGHT_PROFILES = {
    'industrial_default': {
        'location_score': 0.20,
        'clear_height_feet': 0.15,
        'condition': 0.15,
        'effective_age_years': 0.15,
        'loading_docks_total': 0.10,
        'highway_frontage': 0.10,
        'lot_size_acres': 0.05,
        'building_size_sf': 0.05,  # Closer to subject = better
        'office_finish_pct': 0.05
    },

    'industrial_logistics': {
        'location_score': 0.15,
        'clear_height_feet': 0.20,  # Increased for logistics
        'condition': 0.12,
        'effective_age_years': 0.12,
        'loading_docks_total': 0.15,  # Increased for logistics
        'highway_frontage': 0.12,
        'lot_size_acres': 0.08,  # Trailer staging
        'building_size_sf': 0.03,
        'office_finish_pct': 0.03
    },

    'industrial_manufacturing': {
        'location_score': 0.15,
        'clear_height_feet': 0.18,
        'condition': 0.15,
        'effective_age_years': 0.12,
        'loading_docks_total': 0.08,
        'highway_frontage': 0.08,
        'lot_size_acres': 0.06,
        'building_size_sf': 0.05,
        'power_amps': 0.08,      # Manufacturing-specific
        'crane': 0.05           # Manufacturing-specific
    },

    'office_default': {
        'location_score': 0.25,
        'building_class': 0.18,
        'condition': 0.15,
        'effective_age_years': 0.12,
        'parking_ratio': 0.12,
        'floor_plate_efficiency': 0.08,
        'ceiling_height': 0.05,
        'building_size_sf': 0.05
    }
}
```

**Calibration:** Provide a helper to calibrate weights to local market by minimizing out-of-sample error (cross-validated) and report 10th–90th percentile bootstrap weight ranges instead of only point weights.

### 3.5 Input Schema: `schema_template.json` (ADAPTED)

**Key Differences from Leasing Schema:**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "MCDA Sales Comparison Input Schema",
  "type": "object",
  "required": ["analysis_date", "valuation_date", "subject_property", "comparable_sales"],
  "properties": {
    "analysis_date": { "type": "string", "format": "date" },
    "valuation_date": { "type": "string", "format": "date" },
    "market_area": { "type": "string" },
    "property_type": { "enum": ["industrial", "office", "retail"] },

    "subject_property": {
      "type": "object",
      "required": ["address", "building_sf", "is_subject"],
      "properties": {
        "address": { "type": "string" },
        "building_sf": { "type": "number", "minimum": 0 },
        "lot_size_acres": { "type": "number", "minimum": 0 },
        "clear_height_feet": { "type": "number", "minimum": 0 },
        "loading_docks_dock_high": { "type": "integer", "minimum": 0 },
        "loading_docks_grade_level": { "type": "integer", "minimum": 0 },
        "year_built": { "type": "integer" },
        "effective_age_years": { "type": "number", "minimum": 0 },
        "condition": { "enum": ["excellent", "good", "average", "fair", "poor"] },
        "location_score": { "type": "number", "minimum": 0, "maximum": 100 },
        "highway_frontage": { "type": "boolean" },
        "is_subject": { "const": true }
      }
    },

    "comparable_sales": {
      "type": "array",
      "minItems": 3,
      "maxItems": 20,
      "items": {
        "type": "object",
        "required": ["address", "sale_price", "sale_date", "building_sf"],
        "properties": {
          "address": { "type": "string" },
          "sale_price": { "type": "number", "minimum": 0 },
          "sale_date": { "type": "string", "format": "date" },
          "property_rights": { "enum": ["fee_simple", "leasehold", "leased_fee"] },
          "financing": {
            "type": "object",
            "properties": {
              "type": { "enum": ["cash", "conventional", "seller_vtb"] },
              "rate": { "type": "number" },
              "market_rate": { "type": "number" }
            }
          },
          "conditions_of_sale": {
            "type": "object",
            "properties": {
              "arms_length": { "type": "boolean" },
              "motivation_discount_pct": { "type": "number" }
            }
          },
          "cash_equivalent_adjustment_pct": { "type": "number", "description": "Applied to derive cash equivalent price if financing non-market" },
          "time_adjustment_pct": { "type": "number", "description": "Market conditions adjustment to valuation date, if pre-computed" },
          "building_sf": { "type": "number", "minimum": 0 },
          "is_subject": { "const": false }
        }
      }
    },

    "weights": {
      "type": "object",
      "description": "Custom weights (must sum to 1.0) or empty for defaults"
    },

    "mapping_method": {
      "enum": ["interpolation", "regression", "both"],
      "default": "both"
    }
  }
}
```

### 3.6 Validation Module: `validation.py` (ADAPTED)

**Additional Sales-Specific Validations:**

```python
def validate_sale_price(comparable: Dict) -> List[str]:
    """Validate sale price is reasonable."""
    errors = []
    price_psf = comparable['sale_price'] / comparable['building_sf']

    # Industrial typically $50-$200/SF
    if price_psf < 20 or price_psf > 500:
        errors.append(f"Sale price ${price_psf:.2f}/SF outside typical range")

    return errors

def validate_transaction(comparable: Dict) -> List[str]:
    """Validate transaction details for Stage 1-3 adjustments."""
    errors = []
    warnings = []

    # Property rights
    if comparable.get('property_rights') != 'fee_simple':
        warnings.append(f"Non-fee simple interest: {comparable.get('property_rights')}")

    # Financing
    if comparable.get('financing', {}).get('type') == 'seller_vtb':
        warnings.append("Seller financing may require cash equivalent adjustment")

    # Conditions of sale
    if not comparable.get('conditions_of_sale', {}).get('arms_length', True):
        errors.append("Non-arm's length sale - exclude from analysis")

    return errors, warnings

def compute_cash_equivalent(comparable: Dict) -> Dict:
    """Return cash-equivalent price if financing is non-market."""
    adjustment_pct = comparable.get('cash_equivalent_adjustment_pct', 0) or 0
    price = comparable['sale_price'] * (1 + adjustment_pct/100)
    return {
        'cash_equivalent_price': price,
        'adjustment_pct': adjustment_pct,
        'note': "Adjusted for non-market financing" if adjustment_pct else "No adjustment applied"
    }

def validate_time_adjustment(comparable: Dict, valuation_date: str) -> Dict:
    """Calculate time adjustment if needed."""
    from datetime import datetime

    sale_date = datetime.strptime(comparable['sale_date'], '%Y-%m-%d')
    val_date = datetime.strptime(valuation_date, '%Y-%m-%d')

    months_diff = (val_date - sale_date).days / 30.44

    return {
        'months_difference': months_diff,
        'requires_time_adjustment': abs(months_diff) > 3,
        'suggested_adjustment_pct': months_diff * 0.3 if abs(months_diff) > 3 else 0  # ~3.5%/year
    }

def validate_monotonicity(scores_prices: List[Tuple[float, float]]) -> Dict:
    """
    Check monotonic decreasing relationship (better score -> higher price).
    Returns violations count and magnitude to trigger monotone fit fallback.
    """
    violations = 0
    for i in range(1, len(scores_prices)):
        if scores_prices[i][0] < scores_prices[i-1][0] and scores_prices[i][1] <= scores_prices[i-1][1]:
            continue
        if scores_prices[i][0] > scores_prices[i-1][0] and scores_prices[i][1] >= scores_prices[i-1][1]:
            violations += 1
    return {'violations': violations, 'requires_monotone_fit': violations > 0}
```

---

## 4. Report Output Specification

### 4.1 Markdown Report Structure

```markdown
# MCDA Sales Comparison Analysis: Ordinal Ranking Approach

**Subject Property:** [Address]
**Valuation Date:** [Date]
**Analysis Date:** [Date]
**Property Type:** [Industrial/Office]

---

## Executive Summary

### Indicated Market Value

| Metric | Value |
|--------|-------|
| **Indicated Value** | $X,XXX,XXX |
| **Price per SF** | $XX.XX |
| **Composite Score** | X.XX |
| **Confidence Level** | [High/Medium] |

### Methodology Summary
- **Comparables Analyzed:** X sales
- **Mapping Method:** [Interpolation/Regression/Monotone/Both]
- **R² / LOO R² (if regression):** X.XX / X.XX
- **Monotonic Check:** [Pass/Monotone fit applied]
- **Score Range:** X.XX - X.XX

---

## Subject Property Description

[Property details table]

---

## Comparable Sales Data

### Raw Data Table

| # | Address | Sale Date | Sale Price | $/SF | Bldg SF | Clear Ht | Docks | Cond | Age | Location |
|---|---------|-----------|------------|------|---------|----------|-------|------|-----|----------|

### Verification Notes
- All sales verified as fee simple, cash equivalent, arm's length
- Cash-equivalent adjustments: [Applied/Not required]
- Time/market condition adjustments: [Applied/Not required]

## Pre-Processing and Normalization
- Sale prices normalized to cash-equivalent terms and valuation date
- Units standardized (SF, $/SF, feet)
- Missing attributes imputed from peer medians (flagged) or excluded

---

## Ordinal Ranking Analysis

### Variable Rankings (1 = Best)

| Property | Clear Ht | Docks | Condition | Age | Location | Highway | **Wtd Score** |
|----------|----------|-------|-----------|-----|----------|---------|---------------|

### Weight Profile Used

| Variable | Weight | Direction | Rationale |
|----------|--------|-----------|-----------|

**Calibration:** Weights calibrated via cross-validated error minimization; report 10th–90th percentile range when available.

### Composite Score Calculation

[Detailed calculation for each property]

---

## Score-to-Price Mapping

### Method 1: Linear Interpolation

[Interpolation details and calculation]

### Method 2: OLS Regression

| Statistic | Value |
|-----------|-------|
| α (Intercept) | $XXX.XX |
| β (Slope) | -$XX.XX per score unit |
| R² | X.XX |
| LOO R² | X.XX |
| Std Error | $X.XX |
| 95% CI | $XX.XX - $XX.XX |
| Method Used | [Monotone/OLS/Theil-Sen] |

### Regression Plot

```
$/SF
$XXX ┤ ● Comp A
     │    ● Comp B
$XXX ┤       ★ SUBJECT
     │          ● Comp C
$XXX ┤             ● Comp D
     └──┬────┬────┬────┬────
       1.0  2.0  3.0  4.0
              Composite Score
```

### Reconciliation

| Method | Indicated $/SF | Weight | Contribution |
|--------|----------------|--------|--------------|
| Interpolation | $XX.XX | XX% | $X.XX |
| Regression | $XX.XX | XX% | $X.XX |
| **Reconciled** | **$XX.XX** | 100% | |

---

## Validation and Quality Control

### R² Analysis
[Interpretation of model fit]

### Monotonicity Check
- Violations detected: X
- Monotone fit applied: [Yes/No]

### Residual Analysis
[Table of residuals, outlier identification]

### Sensitivity Analysis

| Scenario | Weight Change | Subject Score | Indicated Value | Change |
|----------|---------------|---------------|-----------------|--------|

### Leave-One-Out Stability
- Subject indicated $/SF range across LOO: $XX.XX - $YY.YY
- Max absolute change vs. full model: $ZZ.ZZ/SF

---

## Compliance and Disclosure

### Methodology Statement

> This analysis applies the Ordinal Ranking Direct Comparison Approach, a Multi-Criteria
> Decision Analysis (MCDA) methodology that formalizes qualitative/relative comparison grids, compliant with USPAP Standards Rule 1-4 and
> CUSPAP Practice Standard 6.2. [Full disclosure statement]

### Limiting Conditions

1. [Standard limiting conditions]

### Extraordinary Assumptions

1. [If any]

---

## Value Conclusion

Based on the Ordinal Ranking Direct Comparison Approach, the indicated fee simple
market value of the subject property as of [Valuation Date] is:

## **$X,XXX,XXX**

| Metric | Value |
|--------|-------|
| Total Value | $X,XXX,XXX |
| Price per SF | $XX.XX |
| Confidence | [High/Medium] |

---

## Appendices

### A. Comparable Sale Photographs
### B. Location Map
### C. Statistical Output
### D. Input/Output Files
```

---

## 5. Development Tasks

### Phase 1: Core Infrastructure (Day 1)

| Task | Description | Effort | Dependencies |
|------|-------------|--------|--------------|
| 1.1 | Create `MCDA_Sales_Comparison/` directory structure | 0.5h | None |
| 1.2 | Adapt `schema_template.json` for sales data | 1h | 1.1 |
| 1.3 | Create `SCHEMA.md` documentation | 1h | 1.2 |
| 1.4 | Symlink/import shared modules from `Relative_Valuation/` | 0.5h | 1.1 |
| 1.5 | Create `weight_profiles.py` with sales-specific weights | 1h | 1.1 |
| 1.6 | Add hybrid rank+distance scoring toggle in ranking engine | 1h | 1.4 |

### Phase 2: Score-to-Price Module (Day 2)

| Task | Description | Effort | Dependencies |
|------|-------------|--------|--------------|
| 2.1 | Implement `interpolate_value()` function | 2h | Phase 1 |
| 2.2 | Implement `regression_value()` with monotone/OLS/Theil-Sen options | 3h | Phase 1 |
| 2.3 | Implement leave-one-out metrics and bootstrap CI | 2h | 2.2 |
| 2.4 | Implement `reconcile_methods()` function | 1h | 2.1, 2.2 |
| 2.5 | Unit tests for score-to-price module (monotonicity, LOO) | 1h | 2.1-2.4 |

### Phase 3: Main Calculator (Day 3)

| Task | Description | Effort | Dependencies |
|------|-------------|--------|--------------|
| 3.1 | Adapt `mcda_sales_calculator.py` from leasing version | 3h | Phase 2 |
| 3.2 | Implement cash-equivalent and time adjustment normalization | 1h | 3.1 |
| 3.3 | Implement sales-specific validation (incl. monotonicity trigger) | 1h | 3.1 |
| 3.4 | Implement compliance disclosure generator | 1h | 3.1 |
| 3.5 | Add CLI argument parsing | 1h | 3.1 |
| 3.6 | Integration tests with sample data | 2h | 3.1-3.5 |

### Phase 4: Slash Command & Reports (Day 4)

| Task | Description | Effort | Dependencies |
|------|-------------|--------|--------------|
| 4.1 | Create `/mcda-sales-comparison` slash command | 2h | Phase 3 |
| 4.2 | Implement markdown report generator | 3h | Phase 3 |
| 4.3 | Add regression plot ASCII art | 1h | 4.2 |
| 4.4 | Adapt PDF styling from leasing version | 1h | 4.2 |
| 4.5 | End-to-end testing with Hamilton data | 1h | 4.1-4.4 |

### Phase 5: Documentation & Polish (Day 5)

| Task | Description | Effort | Dependencies |
|------|-------------|--------|--------------|
| 5.1 | Write `README.md` for MCDA_Sales_Comparison/ | 1h | Phase 4 |
| 5.2 | Add to CLAUDE.md documentation | 0.5h | Phase 4 |
| 5.3 | Create sample input files | 1h | Phase 4 |
| 5.4 | Performance testing (large datasets) | 1h | Phase 4 |
| 5.5 | Code review and cleanup | 2h | 5.1-5.4 |

---

## 6. Files to Create/Modify

### 6.1 New Files

| File | Purpose | LOC Est. |
|------|---------|----------|
| `.claude/commands/Valuation/mcda-sales-comparison.md` | Slash command definition | 400 |
| `MCDA_Sales_Comparison/mcda_sales_calculator.py` | Main calculator | 600 |
| `MCDA_Sales_Comparison/score_to_price.py` | Score-to-price mapping | 250 |
| `MCDA_Sales_Comparison/weight_profiles.py` | Sales weight profiles | 150 |
| `MCDA_Sales_Comparison/validation.py` | Sales-specific validation | 200 |
| `MCDA_Sales_Comparison/schema_template.json` | Input schema | 200 |
| `MCDA_Sales_Comparison/SCHEMA.md` | Schema documentation | 300 |
| `MCDA_Sales_Comparison/README.md` | Module documentation | 200 |
| `MCDA_Sales_Comparison/tests/test_mcda_sales_calculator.py` | Unit tests | 300 |
| `MCDA_Sales_Comparison/sample_industrial_sales.json` | Sample input | 150 |

**Total New Code:** ~2,750 LOC

### 6.2 Shared Files (Symlink or Import)

| Source | Usage |
|--------|-------|
| `Relative_Valuation/ranking_engine.py` | Import ranking functions |
| `Relative_Valuation/calculate_distances.py` | Import distance API |
| `Relative_Valuation/pdf_style.css` | Copy for PDF generation |
| `Shared_Utils/statistics_utils.py` | Import regression utilities |

### 6.3 Modified Files

| File | Change | LOC Est. |
|------|--------|----------|
| `CLAUDE.md` | Add `/mcda-sales-comparison` to command list | +20 |
| `.claude/hooks/skill-rules.json` | Add mcda-sales-comparison triggers | +10 |

---

## 7. Testing Plan

### 7.1 Unit Tests

| Test | Description |
|------|-------------|
| `test_mcda_ranking_industrial()` | Verify ranking logic for industrial properties |
| `test_interpolation_basic()` | Basic interpolation between 2 comparables |
| `test_interpolation_ties()` | Handling of tied scores |
| `test_regression_fit()` | Verify regression coefficients |
| `test_regression_outliers()` | Outlier detection (>2σ) |
| `test_confidence_interval()` | 95% CI calculation |
| `test_monotonicity_detection()` | Detect violations and trigger monotone fit |
| `test_leave_one_out_range()` | LOO subject value range reported |
| `test_hybrid_rank_distance_scoring()` | Hybrid scoring preserves ordering and intensity |
| `test_cash_equivalent_adjustment()` | Cash-equivalent normalization applied |
| `test_time_adjustment()` | Time/market condition adjustment suggested correctly |
| `test_weight_validation()` | Weights sum to 1.0 |
| `test_schema_validation()` | JSON schema compliance |

### 7.2 Integration Tests

| Test | Description | Data |
|------|-------------|------|
| `test_mcda_hamilton_industrial()` | Full analysis with Hamilton data | `sample_industrial_comps_tight.json` |
| `test_mcda_vs_traditional_dca()` | Compare to traditional DCA result | Hamilton data |
| `test_large_dataset()` | 20+ comparables | Synthetic data |
| `test_office_properties()` | Office property type | Sample office data |

### 7.3 Validation Tests

| Test | Expected Result |
|------|-----------------|
| Hamilton Industrial | Indicated value within 5% of traditional DCA ($4.6M) |
| R² threshold | R² > 0.70 (report LOO R²) for regression mapping |
| Sensitivity | <5% value change with ±10% weight change |
| Monotonicity | No violations or monotone fit applied; LOO range within ±5% |

---

## 8. Sample Input/Output

### 8.1 Sample Input JSON

```json
{
  "analysis_date": "2025-12-16",
  "valuation_date": "2025-01-15",
  "market_area": "Greater Hamilton Industrial",
  "property_type": "industrial",

  "subject_property": {
    "address": "2550 Industrial Parkway North, Hamilton, ON",
    "building_sf": 50000,
    "lot_size_acres": 5.0,
    "clear_height_feet": 28,
    "loading_docks_dock_high": 4,
    "loading_docks_grade_level": 2,
    "year_built": 2005,
    "effective_age_years": 15,
    "condition": "average",
    "location_score": 75,
    "highway_frontage": true,
    "is_subject": true
  },

  "comparable_sales": [
    {
      "id": "COMP_1",
      "address": "2480 Industrial Parkway North, Hamilton, ON",
      "sale_price": 4650000,
      "sale_date": "2024-09-15",
      "property_rights": "fee_simple",
      "financing": {"type": "cash"},
      "conditions_of_sale": {"arms_length": true},
      "building_sf": 48500,
      "lot_size_acres": 4.9,
      "clear_height_feet": 28,
      "loading_docks_dock_high": 4,
      "loading_docks_grade_level": 2,
      "effective_age_years": 14,
      "condition": "average",
      "location_score": 76,
      "highway_frontage": true,
      "is_subject": false
    }
  ],

  "weights": {},
  "mapping_method": "both"
}
```

### 8.2 Sample Output JSON

```json
{
  "analysis_metadata": {
    "analysis_date": "2025-12-16",
    "valuation_date": "2025-01-15",
    "methodology": "MCDA Sales Comparison",
    "calculator_version": "1.0.0"
  },

  "subject_analysis": {
    "composite_score": 3.50,
    "score_percentile": 45,
    "bracketing_comparables": {
      "lower": {"id": "COMP_1", "score": 3.10, "price_psf": 95.88},
      "upper": {"id": "COMP_4", "score": 3.90, "price_psf": 88.00}
    }
  },

  "value_indication": {
    "interpolation": {
      "indicated_psf": 91.94,
      "indicated_total": 4597000,
      "confidence": "high"
    },
    "regression": {
      "indicated_psf": 92.20,
      "indicated_total": 4610000,
      "r_squared": 0.72,
      "loo_r_squared": 0.68,
      "loo_value_range_psf": [90.10, 93.40],
      "std_error": 4.85,
      "confidence_interval_95": [82.50, 101.90],
      "method_used": "monotone"
    },
    "reconciled": {
      "indicated_psf": 92.07,
      "indicated_total": 4603500,
      "rounded": 4600000,
      "confidence": "medium-high"
    }
  },

  "rankings": {
    "SUBJECT": {"clear_height": 4, "docks": 3.5, "condition": 4, "age": 4, "location": 4, "highway": 1, "score": 3.50},
    "COMP_1": {"clear_height": 4, "docks": 3.5, "condition": 4, "age": 3, "location": 3, "highway": 1, "score": 3.10}
  },

  "validation": {
    "r_squared": 0.72,
    "loo_r_squared": 0.68,
    "monotonicity": {"violations": 0, "method_used": "monotone"},
    "leave_one_out": {"subject_psf_range": [90.10, 93.40]},
    "outliers": [],
    "sensitivity": {
      "location_plus_10pct": {"score": 3.55, "value_change_pct": -0.8},
      "location_minus_10pct": {"score": 3.45, "value_change_pct": 0.9}
    }
  }
}
```

---

## 9. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| R² too low for regression | Medium | Medium | Fall back to interpolation only |
| Weight sensitivity too high | Low | Medium | Document in report, use narrower weights |
| Small sample (3-4 comps) | Medium | Low | Emphasize interpolation over regression |
| Non-linear/monotonicity violations | Low | Medium | Apply monotone regression; report LOO range |
| Magnitude loss from pure ranks | Medium | Medium | Use hybrid rank+distance/quantile scoring |
| Regulatory acceptance | Medium | Low | Document USPAP/CUSPAP compliance |

---

## 10. Success Criteria

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| Value accuracy vs traditional DCA | Within 5% | Hamilton dataset comparison |
| R² for regression mapping | > 0.70 (report LOO R²) | Statistical output |
| Processing time | < 5 seconds | CLI timing |
| Code reuse from leasing tool | > 60% | LOC analysis |
| Test coverage | > 80% | pytest-cov |
| Documentation completeness | All sections | Manual review |

---

## 11. Future Enhancements

| Enhancement | Priority | Effort |
|-------------|----------|--------|
| Automated weight derivation from sales | Medium | 2 days |
| Non-linear regression options | Low | 1 day |
| Monte Carlo confidence intervals | Low | 1 day |
| Integration with MLS data extraction | Medium | 2 days |
| Batch processing for portfolios | Low | 1 day |
| Interactive web interface | Low | 5 days |

---

**Document Version:** 1.0
**Last Updated:** December 2025
**Author:** Development Planning
**Status:** Ready for Implementation
