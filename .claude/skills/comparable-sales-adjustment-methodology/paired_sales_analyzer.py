#!/usr/bin/env python3
"""
CUSPAP-Compliant Paired Sales Analyzer

Derives adjustment factors from comparable sales data using the paired sales
isolation method in accordance with:
- CUSPAP 2024 (Canadian Uniform Standards of Professional Appraisal Practice)
- USPAP Standards Rule 1-1(a), 1-1(b), 1-4(a)
- Fannie Mae Selling Guide B4-1.3-09

Methodology (CUSPAP 6.2.15-6.2.17 compliant):
1. Verify arm's-length status and apply conditions of sale adjustments
2. Apply cash equivalency adjustments for non-market financing
3. Find pairs that are nearly identical except for ONE characteristic
4. Calculate price differential attributable to that characteristic
5. Validate with multiple pairs and apply quality-weighted reconciliation
6. Track and disclose all extraordinary assumptions and limiting conditions

References:
- Appraisal Institute of Canada: https://www.aicanada.ca/about-aic/cuspap/
- The Appraisal of Real Estate, 15th Edition, Chapter 14
- Fannie Mae Selling Guide: https://selling-guide.fanniemae.com/sel/b4-1.3-09/

Author: Claude Code
Created: 2025-12-16
CUSPAP Compliance: 2024 Edition
"""

import json
import logging
import math
from typing import Dict, List, Optional, Tuple, Any, Callable
from datetime import datetime, date
from dataclasses import dataclass, field
from statistics import mean, stdev, median, StatisticsError
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


# =============================================================================
# CUSPAP DISCLOSURE CATEGORIES
# =============================================================================

class DisclosureCategory(Enum):
    """CUSPAP-required disclosure categories."""
    EXTRAORDINARY_ASSUMPTION = "extraordinary_assumption"
    HYPOTHETICAL_CONDITION = "hypothetical_condition"
    LIMITING_CONDITION = "limiting_condition"
    DATA_LIMITATION = "data_limitation"
    METHODOLOGY_LIMITATION = "methodology_limitation"
    NON_MARKET_DERIVED = "non_market_derived_adjustment"


class DerivationMethod(Enum):
    """Adjustment derivation methods with CUSPAP compliance indicators."""
    PAIRED_SALES_ISOLATION = "paired_sales_isolation"  # Preferred - market derived
    TIME_SERIES_REGRESSION = "time_series_regression"  # Market derived
    REPEAT_SALES = "repeat_sales"  # Market derived
    SUBMARKET_AVERAGE = "submarket_average_comparison"  # Market derived, lower confidence
    COST_APPROACH = "cost_approach"  # Secondary support
    INDUSTRY_DEFAULT = "industry_default"  # Requires disclosure
    APPRAISER_JUDGMENT = "appraiser_judgment"  # Requires disclosure


# =============================================================================
# SAFE STATISTICS FUNCTIONS
# =============================================================================

def safe_mean(values: List[float]) -> Optional[float]:
    """Calculate mean with empty list protection."""
    if not values:
        return None
    return mean(values)


def safe_median(values: List[float]) -> Optional[float]:
    """Calculate median with empty list protection."""
    if not values:
        return None
    return median(values)


def safe_stdev(values: List[float]) -> Optional[float]:
    """Calculate standard deviation with insufficient data protection."""
    if len(values) < 2:
        return None
    try:
        return stdev(values)
    except StatisticsError:
        return None


def coefficient_of_variation(values: List[float]) -> Optional[float]:
    """Calculate CV (stdev/mean) as measure of adjustment reliability."""
    if len(values) < 2:
        return None
    m = safe_mean(values)
    s = safe_stdev(values)
    if m is None or s is None or m == 0:
        return None
    return abs(s / m)


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class CUSPAPDisclosure:
    """A CUSPAP-required disclosure item."""
    category: DisclosureCategory
    description: str
    impact: str  # How this affects the analysis
    recommendation: str  # Recommended action or interpretation


@dataclass
class PairedSalesResult:
    """Result of a paired sales analysis for one characteristic (CUSPAP-compliant)."""
    characteristic: str
    pairs_found: int
    adjustments_derived: List[float]
    mean_adjustment: Optional[float]
    median_adjustment: Optional[float]
    stdev_adjustment: Optional[float]
    coefficient_of_variation: Optional[float]  # CV for reliability assessment
    confidence: str  # 'high', 'medium', 'low', 'insufficient', 'default'
    derivation_method: DerivationMethod
    pair_details: List[Dict]
    unit: str  # 'percent', 'per_sf', 'per_unit', 'lump_sum'
    reconciled_adjustment: Optional[float]  # Quality-weighted reconciliation
    disclosures: List[CUSPAPDisclosure] = field(default_factory=list)
    market_supported: bool = True  # False triggers disclosure requirement


@dataclass
class TransactionAdjustment:
    """Adjustments applied to a comparable sale for CUSPAP compliance."""
    comparable_address: str
    original_price: float
    adjusted_price: float
    adjustments_applied: Dict[str, float]  # adjustment_type -> amount
    is_arms_length: bool
    financing_type: str
    excluded: bool = False
    exclusion_reason: Optional[str] = None


@dataclass
class DerivedAdjustments:
    """All derived adjustment factors from paired sales analysis."""
    market_appreciation_rate: Optional[PairedSalesResult] = None
    size_adjustment_per_sf: Optional[PairedSalesResult] = None
    lot_size_adjustment_per_acre: Optional[PairedSalesResult] = None
    highway_frontage_premium: Optional[PairedSalesResult] = None
    condition_adjustment_per_level: Optional[PairedSalesResult] = None
    clear_height_adjustment_per_foot: Optional[PairedSalesResult] = None
    loading_dock_value: Optional[PairedSalesResult] = None
    rail_spur_premium: Optional[PairedSalesResult] = None
    building_class_adjustment: Optional[PairedSalesResult] = None
    age_depreciation_per_year: Optional[PairedSalesResult] = None
    submarket_differentials: Dict[str, float] = field(default_factory=dict)


# =============================================================================
# MAIN ANALYZER CLASS
# =============================================================================

class PairedSalesAnalyzer:
    """
    CUSPAP-Compliant Paired Sales Analyzer.

    Analyzes comparable sales to derive adjustment factors using the paired sales
    method in accordance with CUSPAP 2024 Standards Rules 6.2.15-6.2.17.

    Key CUSPAP Requirements Implemented:
    - 6.2.15: Describe and analyze all data relevant to the assignment
    - 6.2.16: Describe and apply appraisal procedures, support exclusions
    - 6.2.17: Detail reasoning supporting analyses, opinions, conclusions

    Attributes:
        comparables: List of comparable sale dictionaries
        subject: Subject property dictionary
        property_type: 'industrial' or 'office'
        strict_mode: If True, uses tighter thresholds for true paired sales
        valuation_date: Date of valuation for time adjustments
    """

    # -------------------------------------------------------------------------
    # CUSPAP-COMPLIANT SIMILARITY THRESHOLDS
    # -------------------------------------------------------------------------
    # Per The Appraisal of Real Estate: "nearly identical except for one key difference"

    # Standard thresholds (more permissive, requires disclosure)
    STANDARD_THRESHOLDS = {
        'size_sf_pct': 0.20,           # Within 20% of each other
        'lot_size_acres_pct': 0.25,    # Within 25%
        'year_built_years': 10,        # Within 10 years
        'sale_date_months': 12,        # Within 12 months (Fannie Mae guidance)
        'similarity_pass_rate': 0.60,  # 60% of checks must pass
    }

    # Strict thresholds (preferred for true paired sales)
    STRICT_THRESHOLDS = {
        'size_sf_pct': 0.10,           # Within 10% - nearly identical
        'lot_size_acres_pct': 0.15,    # Within 15%
        'year_built_years': 5,         # Within 5 years
        'sale_date_months': 6,         # Within 6 months (preferred)
        'similarity_pass_rate': 0.80,  # 80% of checks must pass
    }

    # -------------------------------------------------------------------------
    # CONFIDENCE THRESHOLDS
    # -------------------------------------------------------------------------
    # Per paired sales best practices: "The more pairs analyzed, the more supportable"

    MIN_PAIRS_HIGH_CONFIDENCE = 5      # Strong market support
    MIN_PAIRS_MEDIUM_CONFIDENCE = 3    # Adequate market support
    MIN_PAIRS_LOW_CONFIDENCE = 2       # Minimal market support (requires disclosure)
    MIN_PAIRS_SINGLE = 1               # Single pair (requires strong disclosure)

    # Coefficient of variation thresholds for reliability
    CV_HIGH_RELIABILITY = 0.20         # CV < 20% = high reliability
    CV_MEDIUM_RELIABILITY = 0.35       # CV < 35% = medium reliability

    # -------------------------------------------------------------------------
    # INDUSTRY DEFAULTS (CUSPAP requires disclosure when used)
    # -------------------------------------------------------------------------
    # These are fallback values that trigger EXTRAORDINARY_ASSUMPTION disclosure

    INDUSTRY_DEFAULTS = {
        'industrial': {
            'appreciation_rate_annual_pct': 3.5,
            'condition_per_level_pct': 5.0,
            'clear_height_per_foot_per_sf': 1.50,
            'loading_dock_dock_high': 35000,
            'loading_dock_grade_level': 15000,
            'highway_frontage_pct': 12.0,
            'rail_spur_lump': 350000,
            'age_depreciation_pct_per_year': 1.0,
            'size_adjustment_pct_per_10000sf': -2.0,
        },
        'office': {
            'appreciation_rate_annual_pct': 3.5,
            'condition_per_level_pct': 8.0,
            'building_class_per_level_pct': 8.0,
            'parking_per_space': 4500,
            'elevator_per_unit': 150000,
            'age_depreciation_pct_per_year': 1.5,
            'leed_premium': {'Certified': 2, 'Silver': 4, 'Gold': 6, 'Platinum': 10},
        }
    }

    # Source documentation for industry defaults (CUSPAP disclosure requirement)
    INDUSTRY_DEFAULT_SOURCES = {
        'appreciation_rate_annual_pct': 'Historical CPI + real estate premium estimate',
        'condition_per_level_pct': 'Marshall & Swift depreciation tables',
        'clear_height_per_foot_per_sf': 'Industrial building cost manuals',
        'loading_dock_dock_high': 'RS Means construction cost data',
        'highway_frontage_pct': 'Prior market extraction studies',
        'rail_spur_lump': 'Railway siding installation costs',
        'age_depreciation_pct_per_year': 'Marshall & Swift age-life depreciation',
    }

    def __init__(
        self,
        comparables: List[Dict],
        subject: Dict,
        property_type: str = 'industrial',
        strict_mode: bool = True,
        valuation_date: Optional[str] = None
    ):
        """
        Initialize CUSPAP-compliant paired sales analyzer.

        Args:
            comparables: List of comparable sale dictionaries
            subject: Subject property dictionary
            property_type: 'industrial' or 'office'
            strict_mode: If True, uses tighter thresholds for true paired sales isolation
            valuation_date: Date of valuation (YYYY-MM-DD), defaults to today
        """
        self.raw_comparables = comparables  # Preserve original data
        self.comparables = []  # Will hold verified/adjusted comparables
        self.subject = subject
        self.property_type = property_type
        self.strict_mode = strict_mode
        self.thresholds = self.STRICT_THRESHOLDS if strict_mode else self.STANDARD_THRESHOLDS
        self.valuation_date = self._parse_date(valuation_date) if valuation_date else date.today()

        self.derived = DerivedAdjustments()
        self.analysis_log: List[str] = []
        self.disclosures: List[CUSPAPDisclosure] = []
        self.transaction_adjustments: List[TransactionAdjustment] = []

        # Validate inputs
        self._validate_inputs()

    def _validate_inputs(self):
        """Validate input data meets minimum requirements."""
        if not self.raw_comparables:
            raise ValueError("At least one comparable sale is required")

        if len(self.raw_comparables) < 3:
            self._add_disclosure(
                DisclosureCategory.DATA_LIMITATION,
                f"Only {len(self.raw_comparables)} comparable sales provided",
                "Limited data may reduce reliability of derived adjustments",
                "Consider expanding search area or time frame for additional comparables"
            )

        if not self.subject:
            raise ValueError("Subject property data is required")

        # Validate required fields in comparables
        for i, comp in enumerate(self.raw_comparables):
            if not comp.get('sale_price'):
                logger.warning(f"Comparable {i+1} missing sale_price - will be excluded")
            if not comp.get('sale_date'):
                logger.warning(f"Comparable {i+1} missing sale_date - will be excluded")

    # -------------------------------------------------------------------------
    # CUSPAP DISCLOSURE SYSTEM
    # -------------------------------------------------------------------------

    def _add_disclosure(
        self,
        category: DisclosureCategory,
        description: str,
        impact: str,
        recommendation: str
    ):
        """Add a CUSPAP-required disclosure."""
        disclosure = CUSPAPDisclosure(
            category=category,
            description=description,
            impact=impact,
            recommendation=recommendation
        )
        self.disclosures.append(disclosure)
        self._log(f"  ⚠️ DISCLOSURE ({category.value}): {description}")

    # -------------------------------------------------------------------------
    # ARM'S-LENGTH AND FINANCING VERIFICATION (CUSPAP CRITICAL)
    # -------------------------------------------------------------------------

    def _verify_and_adjust_transactions(self) -> List[Dict]:
        """
        CUSPAP-compliant transaction verification and adjustment.

        Per CUSPAP 6.2.15 and Fannie Mae B4-1.3-09:
        1. Verify arm's-length status
        2. Apply cash equivalency adjustments for non-market financing
        3. Adjust for conditions of sale
        4. Exclude or disclose non-arm's-length transactions

        Returns:
            List of verified and adjusted comparable sales
        """
        self._log("\n" + "=" * 60)
        self._log("TRANSACTION VERIFICATION (CUSPAP 6.2.15)")
        self._log("=" * 60)

        verified_comps = []
        excluded_count = 0
        adjusted_count = 0

        for comp in self.raw_comparables:
            address = comp.get('address', f"Unknown ({comp.get('sale_date', 'no date')})")
            original_price = comp.get('sale_price', 0)

            if not original_price or original_price <= 0:
                self._log(f"  EXCLUDED: {address} - No valid sale price")
                excluded_count += 1
                continue

            adjusted_price = original_price
            adjustments_applied = {}
            excluded = False
            exclusion_reason = None

            # Check arm's-length status
            conditions = comp.get('conditions_of_sale', {})
            is_arms_length = conditions.get('arms_length', True)  # Default True if not specified

            if not is_arms_length:
                # Check if motivation discount is quantified
                motivation_discount = conditions.get('motivation_discount_pct', 0)

                if motivation_discount > 0:
                    # Apply adjustment to bring to market equivalent
                    adjustment = original_price * (motivation_discount / 100)
                    adjusted_price += adjustment
                    adjustments_applied['conditions_of_sale'] = adjustment
                    adjusted_count += 1
                    self._log(f"  ADJUSTED: {address} - Non-arm's-length, +{motivation_discount}% = ${adjustment:,.0f}")
                else:
                    # Cannot quantify - exclude with disclosure
                    excluded = True
                    exclusion_reason = "Non-arm's-length transaction without quantifiable adjustment"
                    excluded_count += 1
                    self._log(f"  EXCLUDED: {address} - Non-arm's-length, cannot quantify")
                    self._add_disclosure(
                        DisclosureCategory.DATA_LIMITATION,
                        f"Sale at {address} excluded as non-arm's-length",
                        "Reduces available paired sales data",
                        "Verify transaction details if possible for potential inclusion"
                    )

            # Check financing terms (cash equivalency)
            financing = comp.get('financing', {})
            financing_type = financing.get('type', 'cash')

            if financing_type in ['seller_vtb', 'assumable'] and not excluded:
                rate = financing.get('rate', 0)
                market_rate = financing.get('market_rate', 0)
                loan_amount = financing.get('loan_amount', 0)
                term_years = financing.get('term_years', 0)

                if rate > 0 and market_rate > 0 and loan_amount > 0 and rate < market_rate:
                    # Below-market financing - calculate cash equivalency adjustment
                    # Simplified PV adjustment for rate differential
                    rate_diff = market_rate - rate
                    if term_years > 0:
                        # Approximate adjustment as PV of rate savings
                        annual_savings = loan_amount * (rate_diff / 100)
                        # Simple approximation: savings * term * discount factor
                        adjustment = -annual_savings * term_years * 0.6  # Negative adjustment
                        adjusted_price += adjustment
                        adjustments_applied['financing'] = adjustment
                        adjusted_count += 1
                        self._log(f"  ADJUSTED: {address} - Below-market financing, {adjustment:,.0f}")
                elif rate == 0 and market_rate == 0 and financing_type == 'seller_vtb':
                    # VTB without rate info - disclose but don't exclude
                    self._add_disclosure(
                        DisclosureCategory.DATA_LIMITATION,
                        f"Sale at {address} has seller VTB financing without rate details",
                        "Cash equivalency adjustment could not be calculated",
                        "Consider as potentially inflated price; weight accordingly"
                    )

            # Record transaction adjustment
            trans_adj = TransactionAdjustment(
                comparable_address=address,
                original_price=original_price,
                adjusted_price=adjusted_price,
                adjustments_applied=adjustments_applied,
                is_arms_length=is_arms_length,
                financing_type=financing_type,
                excluded=excluded,
                exclusion_reason=exclusion_reason
            )
            self.transaction_adjustments.append(trans_adj)

            if not excluded:
                # Update comparable with adjusted price
                adjusted_comp = comp.copy()
                adjusted_comp['sale_price'] = adjusted_price
                adjusted_comp['_original_price'] = original_price
                adjusted_comp['_adjustments'] = adjustments_applied
                verified_comps.append(adjusted_comp)

        self._log(f"\n  Summary: {len(verified_comps)} verified, {adjusted_count} adjusted, {excluded_count} excluded")

        if len(verified_comps) < 3:
            self._add_disclosure(
                DisclosureCategory.DATA_LIMITATION,
                f"Only {len(verified_comps)} comparables remain after verification",
                "Limited pairs available for analysis",
                "Results should be corroborated with other valuation approaches"
            )

        return verified_comps

    # -------------------------------------------------------------------------
    # MAIN ANALYSIS
    # -------------------------------------------------------------------------

    def analyze_all(self) -> DerivedAdjustments:
        """
        Run all paired sales analyses and return derived adjustments.

        CUSPAP Compliance:
        - 6.2.15: All data analyzed and documented
        - 6.2.16: Procedures described, exclusions supported
        - 6.2.17: Reasoning detailed for each conclusion
        """
        self._log("=" * 60)
        self._log("CUSPAP-COMPLIANT PAIRED SALES ANALYSIS")
        self._log(f"Property Type: {self.property_type}")
        self._log(f"Raw Comparables: {len(self.raw_comparables)}")
        self._log(f"Valuation Date: {self.valuation_date}")
        self._log(f"Mode: {'STRICT' if self.strict_mode else 'STANDARD'} thresholds")
        self._log("=" * 60)

        # Step 1: Verify transactions (arm's length, financing)
        self.comparables = self._verify_and_adjust_transactions()

        if len(self.comparables) < 2:
            self._add_disclosure(
                DisclosureCategory.METHODOLOGY_LIMITATION,
                "Insufficient verified comparables for paired sales analysis",
                "Cannot derive market-supported adjustments",
                "Use cost approach or expand comparable search"
            )
            return self.derived

        # Step 2: Normalize prices to per-SF basis
        self._normalize_prices()

        # Step 3: Derive adjustments using paired sales
        self._log("\n" + "=" * 60)
        self._log("ADJUSTMENT DERIVATION")
        self._log("=" * 60)

        # Time/market conditions (may use regression - disclosed separately)
        self.derived.market_appreciation_rate = self._derive_time_adjustment()

        # Physical characteristics - true paired sales
        self.derived.size_adjustment_per_sf = self._derive_size_adjustment()
        self.derived.highway_frontage_premium = self._derive_highway_frontage()
        self.derived.condition_adjustment_per_level = self._derive_condition_adjustment()
        self.derived.age_depreciation_per_year = self._derive_age_depreciation()

        # Property-type specific
        if self.property_type == 'industrial':
            self.derived.clear_height_adjustment_per_foot = self._derive_clear_height()
            self.derived.loading_dock_value = self._derive_loading_dock_value()
            self.derived.rail_spur_premium = self._derive_rail_spur_premium()
        elif self.property_type == 'office':
            self.derived.building_class_adjustment = self._derive_building_class()

        # Location analysis (submarket comparison - disclosed as different method)
        self.derived.submarket_differentials = self._derive_submarket_differentials()

        # Final summary
        self._log("\n" + "=" * 60)
        self._log("ANALYSIS COMPLETE")
        self._log(f"Total Disclosures: {len(self.disclosures)}")
        self._log("=" * 60)

        return self.derived

    def _normalize_prices(self):
        """Add normalized $/SF price to each comparable."""
        self._log("\n--- Price Normalization ---")
        missing_data_count = 0

        for comp in self.comparables:
            size = comp.get('size_sf') or comp.get('building_sf')
            sale_price = comp.get('sale_price')

            if size and size > 0 and sale_price and sale_price > 0:
                comp['price_per_sf'] = sale_price / size
                self._log(f"  {comp.get('address', 'Unknown')}: ${comp['price_per_sf']:.2f}/SF")
            else:
                missing_data_count += 1
                address = comp.get('address', 'Unknown')
                logger.warning(f"Cannot calculate $/SF for: {address}")

        if missing_data_count > 0:
            self._log(f"  ⚠️ {missing_data_count} comparable(s) missing size data")

    # -------------------------------------------------------------------------
    # UTILITY METHODS
    # -------------------------------------------------------------------------

    def _log(self, message: str):
        """Add to analysis log."""
        self.analysis_log.append(message)

    def _parse_date(self, date_val) -> date:
        """Parse date from string or return as-is."""
        if isinstance(date_val, str):
            return datetime.strptime(date_val, '%Y-%m-%d').date()
        if isinstance(date_val, datetime):
            return date_val.date()
        return date_val

    def _months_between(self, date1, date2) -> float:
        """Calculate months between two dates."""
        d1 = self._parse_date(date1)
        d2 = self._parse_date(date2)
        return abs((d2.year - d1.year) * 12 + (d2.month - d1.month))

    # -------------------------------------------------------------------------
    # PAIR SIMILARITY ASSESSMENT (CUSPAP-COMPLIANT)
    # -------------------------------------------------------------------------

    def _is_similar_pair(
        self,
        comp1: Dict,
        comp2: Dict,
        exclude_characteristic: str
    ) -> Tuple[bool, float, List[str]]:
        """
        Check if two comparables are similar enough to form a valid pair,
        excluding the characteristic being analyzed.

        Per The Appraisal of Real Estate: Properties must be "nearly identical
        except for one key difference."

        Returns:
            Tuple of (is_valid_pair, similarity_score, similarity_notes)
        """
        similarity_score = 0.0
        checks_passed = 0
        total_checks = 0
        similarity_notes = []

        # Size similarity
        size1 = comp1.get('size_sf') or comp1.get('building_sf', 0)
        size2 = comp2.get('size_sf') or comp2.get('building_sf', 0)
        if size1 > 0 and size2 > 0 and exclude_characteristic != 'size_sf':
            total_checks += 1
            size_diff_pct = abs(size1 - size2) / max(size1, size2)
            if size_diff_pct <= self.thresholds['size_sf_pct']:
                checks_passed += 1
                similarity_score += 1 - size_diff_pct
                similarity_notes.append(f"Size: {size_diff_pct*100:.1f}% diff ✓")
            else:
                similarity_notes.append(f"Size: {size_diff_pct*100:.1f}% diff ✗")

        # Year built similarity
        year1 = comp1.get('year_built', 0)
        year2 = comp2.get('year_built', 0)
        if year1 > 0 and year2 > 0 and exclude_characteristic != 'year_built':
            total_checks += 1
            year_diff = abs(year1 - year2)
            if year_diff <= self.thresholds['year_built_years']:
                checks_passed += 1
                similarity_score += 1 - (year_diff / self.thresholds['year_built_years'])
                similarity_notes.append(f"Age: {year_diff}yr diff ✓")
            else:
                similarity_notes.append(f"Age: {year_diff}yr diff ✗")

        # Sale date proximity
        if comp1.get('sale_date') and comp2.get('sale_date'):
            total_checks += 1
            months_diff = self._months_between(comp1['sale_date'], comp2['sale_date'])
            if months_diff <= self.thresholds['sale_date_months']:
                checks_passed += 1
                similarity_score += 1 - (months_diff / self.thresholds['sale_date_months'])
                similarity_notes.append(f"Time: {months_diff:.0f}mo diff ✓")
            else:
                similarity_notes.append(f"Time: {months_diff:.0f}mo diff ✗")

        # Submarket
        if comp1.get('location_submarket') and comp2.get('location_submarket'):
            if exclude_characteristic != 'location_submarket':
                total_checks += 1
                if comp1['location_submarket'] == comp2['location_submarket']:
                    checks_passed += 1
                    similarity_score += 1.0
                    similarity_notes.append("Submarket: same ✓")
                else:
                    similarity_notes.append("Submarket: different ✗")

        # Zoning
        if comp1.get('zoning') and comp2.get('zoning'):
            total_checks += 1
            if comp1['zoning'] == comp2['zoning']:
                checks_passed += 1
                similarity_score += 1.0
                similarity_notes.append("Zoning: same ✓")
            else:
                similarity_notes.append("Zoning: different ✗")

        # Property rights (critical for CUSPAP)
        rights1 = comp1.get('property_rights', 'fee_simple')
        rights2 = comp2.get('property_rights', 'fee_simple')
        if rights1 and rights2:
            total_checks += 1
            if rights1 == rights2:
                checks_passed += 1
                similarity_score += 1.0
                similarity_notes.append("Rights: same ✓")
            else:
                similarity_notes.append("Rights: different ✗")

        # Calculate pass rate
        pass_rate = checks_passed / total_checks if total_checks > 0 else 0
        is_valid = pass_rate >= self.thresholds['similarity_pass_rate']
        normalized_score = similarity_score / total_checks if total_checks > 0 else 0

        return is_valid, normalized_score, similarity_notes

    def _find_pairs_differing_in(
        self,
        characteristic: str,
        value_getter: Callable[[Dict], Optional[Any]]
    ) -> List[Tuple[Dict, Dict, float, float, List[str]]]:
        """
        Find pairs of comparables that differ primarily in one characteristic.

        CUSPAP Requirement: Properties must be nearly identical except for
        the characteristic being analyzed.

        Returns:
            List of (comp1, comp2, value_difference, similarity_score, notes) tuples
        """
        pairs = []

        for i, comp1 in enumerate(self.comparables):
            for comp2 in self.comparables[i+1:]:
                # Check if they differ in the target characteristic
                val1 = value_getter(comp1)
                val2 = value_getter(comp2)

                if val1 is None or val2 is None:
                    continue

                if val1 == val2:
                    continue  # No difference in target characteristic

                # Check if similar in other respects
                is_valid, similarity, notes = self._is_similar_pair(comp1, comp2, characteristic)

                if is_valid and similarity >= 0.5:
                    # Calculate value difference
                    if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                        diff = val2 - val1
                    else:
                        diff = 1 if val2 else -1  # Boolean or categorical

                    pairs.append((comp1, comp2, diff, similarity, notes))

        return pairs

    # -------------------------------------------------------------------------
    # CONFIDENCE AND RECONCILIATION (CUSPAP-COMPLIANT)
    # -------------------------------------------------------------------------

    def _determine_confidence(
        self,
        n_pairs: int,
        cv: Optional[float],
        adjustments: List[float]
    ) -> str:
        """
        Determine confidence level based on sample size and variability.

        Per CUSPAP: "The more paired sales analyzed, the more supportable the adjustment."
        """
        if n_pairs >= self.MIN_PAIRS_HIGH_CONFIDENCE:
            if cv is not None and cv < self.CV_HIGH_RELIABILITY:
                return 'high'
            elif cv is not None and cv < self.CV_MEDIUM_RELIABILITY:
                return 'medium'
            return 'medium'
        elif n_pairs >= self.MIN_PAIRS_MEDIUM_CONFIDENCE:
            return 'medium'
        elif n_pairs >= self.MIN_PAIRS_LOW_CONFIDENCE:
            return 'low'
        elif n_pairs >= self.MIN_PAIRS_SINGLE:
            return 'single_pair'
        return 'insufficient'

    def _quality_weighted_reconciliation(
        self,
        adjustments: List[float],
        similarity_scores: List[float]
    ) -> Optional[float]:
        """
        CUSPAP-compliant quality-weighted reconciliation.

        Per The Appraisal of Real Estate: Reconciliation should consider the
        quality and reliability of each data point, not just statistical measures.

        Weights adjustments by pair similarity score.
        """
        if not adjustments or not similarity_scores:
            return None

        if len(adjustments) != len(similarity_scores):
            return safe_mean(adjustments)  # Fallback to simple mean

        # Weighted average: better pairs get more weight
        total_weight = sum(similarity_scores)
        if total_weight == 0:
            return safe_mean(adjustments)

        weighted_sum = sum(adj * score for adj, score in zip(adjustments, similarity_scores))
        return weighted_sum / total_weight

    def _create_result(
        self,
        characteristic: str,
        unit: str,
        pairs: List[Tuple],
        adjustments: List[float],
        similarity_scores: List[float],
        pair_details: List[Dict],
        method: DerivationMethod = DerivationMethod.PAIRED_SALES_ISOLATION
    ) -> PairedSalesResult:
        """Create a standardized PairedSalesResult with CUSPAP compliance."""

        mean_adj = safe_mean(adjustments) if adjustments else None
        med_adj = safe_median(adjustments) if adjustments else None
        std_adj = safe_stdev(adjustments) if adjustments else None
        cv = coefficient_of_variation(adjustments) if adjustments else None
        reconciled = self._quality_weighted_reconciliation(adjustments, similarity_scores)

        confidence = self._determine_confidence(len(pairs), cv, adjustments)

        result_disclosures = []
        market_supported = True

        # Add disclosures based on confidence
        if confidence == 'single_pair':
            result_disclosures.append(CUSPAPDisclosure(
                category=DisclosureCategory.DATA_LIMITATION,
                description=f"Single pair available for {characteristic} adjustment",
                impact="Adjustment reliability cannot be statistically validated",
                recommendation="Corroborate with cost approach or secondary market data"
            ))
            self._add_disclosure(
                DisclosureCategory.DATA_LIMITATION,
                f"Single pair for {characteristic}",
                "Cannot validate statistically",
                "Corroborate with other methods"
            )
        elif confidence == 'low':
            result_disclosures.append(CUSPAPDisclosure(
                category=DisclosureCategory.DATA_LIMITATION,
                description=f"Only {len(pairs)} pairs for {characteristic} adjustment",
                impact="Limited statistical confidence",
                recommendation="Consider expanding comparable search"
            ))

        if cv is not None and cv > self.CV_MEDIUM_RELIABILITY:
            result_disclosures.append(CUSPAPDisclosure(
                category=DisclosureCategory.METHODOLOGY_LIMITATION,
                description=f"High variability in {characteristic} adjustments (CV={cv:.1%})",
                impact="Adjustments show inconsistent market reaction",
                recommendation="Review outliers; consider market segmentation"
            ))

        return PairedSalesResult(
            characteristic=characteristic,
            pairs_found=len(pairs),
            adjustments_derived=adjustments,
            mean_adjustment=round(mean_adj, 2) if mean_adj is not None else None,
            median_adjustment=round(med_adj, 2) if med_adj is not None else None,
            stdev_adjustment=round(std_adj, 2) if std_adj is not None else None,
            coefficient_of_variation=round(cv, 3) if cv is not None else None,
            confidence=confidence,
            derivation_method=method,
            pair_details=pair_details,
            unit=unit,
            reconciled_adjustment=round(reconciled, 2) if reconciled is not None else None,
            disclosures=result_disclosures,
            market_supported=market_supported
        )

    def _create_default_result(
        self,
        characteristic: str,
        unit: str,
        default_value: float,
        source: str
    ) -> PairedSalesResult:
        """Create a result using industry defaults with required CUSPAP disclosure."""

        self._add_disclosure(
            DisclosureCategory.NON_MARKET_DERIVED,
            f"Using industry default for {characteristic}: {default_value}",
            "Adjustment not derived from current market data",
            f"Source: {source}. Verify appropriateness for local market."
        )

        return PairedSalesResult(
            characteristic=characteristic,
            pairs_found=0,
            adjustments_derived=[],
            mean_adjustment=default_value,
            median_adjustment=None,
            stdev_adjustment=None,
            coefficient_of_variation=None,
            confidence='default',
            derivation_method=DerivationMethod.INDUSTRY_DEFAULT,
            pair_details=[],
            unit=unit,
            reconciled_adjustment=default_value,
            disclosures=[CUSPAPDisclosure(
                category=DisclosureCategory.NON_MARKET_DERIVED,
                description=f"Industry default used for {characteristic}",
                impact="Not market-derived; may not reflect local conditions",
                recommendation=f"Source: {source}"
            )],
            market_supported=False
        )

    # -------------------------------------------------------------------------
    # ADJUSTMENT DERIVATION METHODS
    # -------------------------------------------------------------------------

    def _derive_time_adjustment(self) -> PairedSalesResult:
        """
        Derive market appreciation rate.

        Note: Uses time-series regression, not paired sales.
        This is disclosed as a different methodology per CUSPAP.
        """
        self._log("\n--- Time/Market Conditions Adjustment ---")
        self._log("  Method: Time-series regression (not paired sales)")

        # Get sales with dates and prices
        valid_sales = []
        earliest_date = None

        for comp in self.comparables:
            if comp.get('sale_date') and comp.get('price_per_sf'):
                sale_date = self._parse_date(comp['sale_date'])
                if earliest_date is None or sale_date < earliest_date:
                    earliest_date = sale_date

        reference_date = earliest_date or self.valuation_date

        for comp in self.comparables:
            if comp.get('sale_date') and comp.get('price_per_sf'):
                sale_date = self._parse_date(comp['sale_date'])
                days_from_start = (sale_date - reference_date).days
                valid_sales.append({
                    'days': days_from_start,
                    'price_per_sf': comp['price_per_sf'],
                    'address': comp.get('address', 'Unknown')
                })

        if len(valid_sales) < 3:
            self._log(f"  Insufficient data ({len(valid_sales)} sales) - using industry default")
            return self._create_default_result(
                'market_appreciation',
                'percent_annual',
                self.INDUSTRY_DEFAULTS[self.property_type]['appreciation_rate_annual_pct'],
                self.INDUSTRY_DEFAULT_SOURCES.get('appreciation_rate_annual_pct', 'Industry estimate')
            )

        # Linear regression
        n = len(valid_sales)
        sum_x = sum(s['days'] for s in valid_sales)
        sum_y = sum(s['price_per_sf'] for s in valid_sales)
        sum_xy = sum(s['days'] * s['price_per_sf'] for s in valid_sales)
        sum_x2 = sum(s['days'] ** 2 for s in valid_sales)

        denominator = n * sum_x2 - sum_x ** 2
        if denominator == 0:
            slope = 0
            self._log("  Warning: Zero variance in time - cannot calculate trend")
        else:
            slope = (n * sum_xy - sum_x * sum_y) / denominator

        # Convert to annual percentage
        mean_price = sum_y / n
        if mean_price > 0:
            daily_rate = slope / mean_price
            annual_rate = daily_rate * 365 * 100
        else:
            annual_rate = self.INDUSTRY_DEFAULTS[self.property_type]['appreciation_rate_annual_pct']

        # Bound to reasonable range with disclosure if bounded
        original_rate = annual_rate
        annual_rate = max(-10, min(15, annual_rate))
        if annual_rate != original_rate:
            self._add_disclosure(
                DisclosureCategory.METHODOLOGY_LIMITATION,
                f"Time adjustment bounded from {original_rate:.1f}% to {annual_rate:.1f}%",
                "Extreme value constrained to reasonable range",
                "Review market conditions for unusual appreciation/depreciation"
            )

        # Calculate R-squared for confidence
        mean_y = sum_y / n
        ss_tot = sum((s['price_per_sf'] - mean_y) ** 2 for s in valid_sales)
        intercept = (sum_y - slope * sum_x) / n
        ss_res = sum((s['price_per_sf'] - (intercept + slope * s['days'])) ** 2 for s in valid_sales)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        confidence = 'high' if r_squared > 0.7 and n >= 5 else 'medium' if r_squared > 0.4 else 'low'

        self._log(f"  Sales analyzed: {n}")
        self._log(f"  Date range: {reference_date} to {max(self._parse_date(s['sale_date']) for s in self.comparables if s.get('sale_date'))}")
        self._log(f"  Derived annual rate: {annual_rate:.2f}%")
        self._log(f"  R-squared: {r_squared:.3f}")
        self._log(f"  Confidence: {confidence}")

        return PairedSalesResult(
            characteristic='market_appreciation',
            pairs_found=n,
            adjustments_derived=[annual_rate],
            mean_adjustment=round(annual_rate, 2),
            median_adjustment=round(annual_rate, 2),
            stdev_adjustment=None,
            coefficient_of_variation=None,
            confidence=confidence,
            derivation_method=DerivationMethod.TIME_SERIES_REGRESSION,
            pair_details=[{'address': s['address'], 'price_psf': round(s['price_per_sf'], 2), 'days': s['days']} for s in valid_sales],
            unit='percent_annual',
            reconciled_adjustment=round(annual_rate, 2),
            disclosures=[CUSPAPDisclosure(
                category=DisclosureCategory.METHODOLOGY_LIMITATION,
                description="Time adjustment derived from regression, not paired sales",
                impact="Method assumes linear appreciation over analysis period",
                recommendation="Verify with local market trend data"
            )],
            market_supported=True
        )

    def _derive_size_adjustment(self) -> PairedSalesResult:
        """Derive size adjustment (economies of scale) from paired sales."""
        self._log("\n--- Size Adjustment (Economies of Scale) ---")

        def get_size(comp):
            return comp.get('size_sf') or comp.get('building_sf')

        pairs = self._find_pairs_differing_in('size_sf', get_size)

        if len(pairs) < self.MIN_PAIRS_SINGLE:
            self._log(f"  Insufficient pairs ({len(pairs)}) - using industry default")
            default_val = self.INDUSTRY_DEFAULTS[self.property_type].get('size_adjustment_pct_per_10000sf', -2.0)
            return self._create_default_result(
                'size_sf',
                'percent_per_10000sf',
                default_val,
                'Industry economies of scale estimate'
            )

        adjustments = []
        similarity_scores = []
        pair_details = []

        for comp1, comp2, size_diff, similarity, notes in pairs:
            price1 = comp1.get('price_per_sf', 0)
            price2 = comp2.get('price_per_sf', 0)
            price_diff = price2 - price1

            if size_diff != 0 and price1 > 0 and price2 > 0:
                # Adjustment per 10,000 SF as percentage
                adj_per_10k_sf = (price_diff / abs(size_diff)) * 10000
                avg_price = (price1 + price2) / 2
                adj_pct_per_10k = (adj_per_10k_sf / avg_price) * 100

                adjustments.append(adj_pct_per_10k)
                similarity_scores.append(similarity)
                pair_details.append({
                    'comp1': comp1.get('address'),
                    'comp1_size': get_size(comp1),
                    'comp2': comp2.get('address'),
                    'comp2_size': get_size(comp2),
                    'size_diff_sf': size_diff,
                    'price_diff_psf': round(price_diff, 2),
                    'adjustment_pct_per_10k': round(adj_pct_per_10k, 2),
                    'similarity': round(similarity, 2),
                    'notes': notes
                })

        if not adjustments:
            return self._create_default_result(
                'size_sf', 'percent_per_10000sf', -2.0, 'No valid pairs found'
            )

        result = self._create_result(
            'size_sf', 'percent_per_10000sf',
            pairs, adjustments, similarity_scores, pair_details
        )

        # Bound extreme values with disclosure (economies of scale: -8% to +2% per 10,000 SF)
        if result.reconciled_adjustment is not None:
            original = result.reconciled_adjustment
            # Reasonable range: economies of scale typically negative, bounded positive
            bounded = max(-8.0, min(2.0, original))
            if bounded != original:
                self._add_disclosure(
                    DisclosureCategory.METHODOLOGY_LIMITATION,
                    f"Size adjustment bounded from {original:.1f}% to {bounded:.1f}% per 10,000 SF",
                    "Derived value outside reasonable economies of scale range",
                    "Value constrained to -8% to +2% per 10,000 SF based on typical industrial market behavior"
                )
                result.reconciled_adjustment = bounded

        self._log(f"  Pairs found: {len(pairs)}")
        self._log(f"  Mean adjustment: {result.mean_adjustment}% per 10,000 SF" if result.mean_adjustment else "  Mean: N/A")
        self._log(f"  Reconciled: {result.reconciled_adjustment}%" if result.reconciled_adjustment else "  Reconciled: N/A")
        self._log(f"  CV: {result.coefficient_of_variation:.1%}" if result.coefficient_of_variation else "  CV: N/A")
        self._log(f"  Confidence: {result.confidence}")

        return result

    def _derive_highway_frontage(self) -> PairedSalesResult:
        """Derive highway frontage premium from paired sales."""
        self._log("\n--- Highway Frontage Premium ---")

        # Find pairs where one has highway frontage, one doesn't
        pairs = []
        for i, comp1 in enumerate(self.comparables):
            for comp2 in self.comparables[i+1:]:
                front1 = comp1.get('highway_frontage')
                front2 = comp2.get('highway_frontage')

                if front1 is None or front2 is None:
                    continue
                if front1 == front2:
                    continue

                is_valid, similarity, notes = self._is_similar_pair(comp1, comp2, 'highway_frontage')
                if is_valid:
                    # Order: without frontage first, with frontage second
                    if front1:
                        pairs.append((comp2, comp1, 1, similarity, notes))
                    else:
                        pairs.append((comp1, comp2, 1, similarity, notes))

        if len(pairs) < self.MIN_PAIRS_SINGLE:
            self._log(f"  Insufficient pairs ({len(pairs)}) - using industry default")
            default_val = self.INDUSTRY_DEFAULTS[self.property_type].get('highway_frontage_pct', 12.0)
            return self._create_default_result(
                'highway_frontage', 'percent_premium', default_val,
                'Prior market extraction studies'
            )

        adjustments = []
        similarity_scores = []
        pair_details = []

        for no_front, with_front, _, similarity, notes in pairs:
            price_no = no_front.get('price_per_sf', 0)
            price_yes = with_front.get('price_per_sf', 0)

            if price_no > 0:
                premium_pct = ((price_yes - price_no) / price_no) * 100
                adjustments.append(premium_pct)
                similarity_scores.append(similarity)
                pair_details.append({
                    'without_frontage': no_front.get('address'),
                    'with_frontage': with_front.get('address'),
                    'price_psf_without': round(price_no, 2),
                    'price_psf_with': round(price_yes, 2),
                    'premium_pct': round(premium_pct, 1),
                    'similarity': round(similarity, 2),
                    'notes': notes
                })

        if not adjustments:
            return self._create_default_result(
                'highway_frontage', 'percent_premium', 12.0, 'No valid pairs found'
            )

        result = self._create_result(
            'highway_frontage', 'percent_premium',
            pairs, adjustments, similarity_scores, pair_details
        )

        self._log(f"  Pairs found: {len(pairs)}")
        self._log(f"  Mean premium: {result.mean_adjustment:.1f}%" if result.mean_adjustment else "  Mean: N/A")
        self._log(f"  Reconciled: {result.reconciled_adjustment:.1f}%" if result.reconciled_adjustment else "  Reconciled: N/A")
        self._log(f"  Confidence: {result.confidence}")

        return result

    def _derive_condition_adjustment(self) -> PairedSalesResult:
        """Derive condition adjustment per level from paired sales."""
        self._log("\n--- Condition Adjustment ---")

        condition_order = ['poor', 'fair', 'average', 'good', 'excellent']

        def get_condition_level(comp):
            cond = comp.get('condition', '').lower()
            if cond in condition_order:
                return condition_order.index(cond)
            return None

        pairs = []
        for i, comp1 in enumerate(self.comparables):
            for comp2 in self.comparables[i+1:]:
                level1 = get_condition_level(comp1)
                level2 = get_condition_level(comp2)

                if level1 is None or level2 is None:
                    continue
                if level1 == level2:
                    continue

                is_valid, similarity, notes = self._is_similar_pair(comp1, comp2, 'condition')
                if is_valid:
                    pairs.append((comp1, comp2, level2 - level1, similarity, notes))

        if len(pairs) < self.MIN_PAIRS_SINGLE:
            self._log(f"  Insufficient pairs ({len(pairs)}) - using industry default")
            default_val = self.INDUSTRY_DEFAULTS[self.property_type].get('condition_per_level_pct', 5.0)
            return self._create_default_result(
                'condition', 'percent_per_level', default_val,
                self.INDUSTRY_DEFAULT_SOURCES.get('condition_per_level_pct', 'Marshall & Swift')
            )

        adjustments = []
        similarity_scores = []
        pair_details = []

        for comp1, comp2, level_diff, similarity, notes in pairs:
            price1 = comp1.get('price_per_sf', 0)
            price2 = comp2.get('price_per_sf', 0)
            avg_price = (price1 + price2) / 2

            if avg_price > 0 and level_diff != 0:
                price_diff_pct = ((price2 - price1) / avg_price) * 100
                adj_per_level = price_diff_pct / level_diff
                adjustments.append(adj_per_level)
                similarity_scores.append(similarity)
                pair_details.append({
                    'comp1': comp1.get('address'),
                    'comp1_condition': comp1.get('condition'),
                    'comp2': comp2.get('address'),
                    'comp2_condition': comp2.get('condition'),
                    'level_diff': level_diff,
                    'adjustment_per_level_pct': round(adj_per_level, 1),
                    'similarity': round(similarity, 2),
                    'notes': notes
                })

        if not adjustments:
            return self._create_default_result(
                'condition', 'percent_per_level', 5.0, 'No valid pairs found'
            )

        result = self._create_result(
            'condition', 'percent_per_level',
            pairs, adjustments, similarity_scores, pair_details
        )

        # Bound extreme values with disclosure
        if result.reconciled_adjustment is not None:
            original = result.reconciled_adjustment
            bounded = max(2, min(15, original))
            if bounded != original:
                self._add_disclosure(
                    DisclosureCategory.METHODOLOGY_LIMITATION,
                    f"Condition adjustment bounded from {original:.1f}% to {bounded:.1f}%",
                    "Value constrained to reasonable range (2-15% per level)",
                    "Review comparables for unusual condition impacts"
                )
                result.reconciled_adjustment = bounded

        self._log(f"  Pairs found: {len(pairs)}")
        self._log(f"  Mean adjustment: {result.mean_adjustment:.1f}% per level" if result.mean_adjustment else "  Mean: N/A")
        self._log(f"  Reconciled: {result.reconciled_adjustment:.1f}%" if result.reconciled_adjustment else "  Reconciled: N/A")
        self._log(f"  Confidence: {result.confidence}")

        return result

    def _derive_age_depreciation(self) -> PairedSalesResult:
        """Derive age depreciation rate from paired sales."""
        self._log("\n--- Age Depreciation ---")

        pairs = self._find_pairs_differing_in('year_built', lambda c: c.get('year_built'))

        if len(pairs) < self.MIN_PAIRS_SINGLE:
            self._log(f"  Insufficient pairs ({len(pairs)}) - using industry default")
            default_val = self.INDUSTRY_DEFAULTS[self.property_type].get('age_depreciation_pct_per_year', 1.0)
            return self._create_default_result(
                'age_depreciation', 'percent_per_year', default_val,
                self.INDUSTRY_DEFAULT_SOURCES.get('age_depreciation_pct_per_year', 'Marshall & Swift age-life')
            )

        adjustments = []
        similarity_scores = []
        pair_details = []

        for comp1, comp2, year_diff, similarity, notes in pairs:
            price1 = comp1.get('price_per_sf', 0)
            price2 = comp2.get('price_per_sf', 0)
            avg_price = (price1 + price2) / 2

            if avg_price > 0 and year_diff != 0:
                price_diff_pct = ((price2 - price1) / avg_price) * 100
                # year_diff is positive if comp2 is newer
                adj_per_year = abs(price_diff_pct / year_diff)
                adjustments.append(adj_per_year)
                similarity_scores.append(similarity)
                pair_details.append({
                    'comp1': comp1.get('address'),
                    'comp1_year': comp1.get('year_built'),
                    'comp2': comp2.get('address'),
                    'comp2_year': comp2.get('year_built'),
                    'year_diff': year_diff,
                    'depreciation_per_year_pct': round(adj_per_year, 2),
                    'similarity': round(similarity, 2),
                    'notes': notes
                })

        if not adjustments:
            return self._create_default_result(
                'age_depreciation', 'percent_per_year', 1.0, 'No valid pairs found'
            )

        result = self._create_result(
            'age_depreciation', 'percent_per_year',
            pairs, adjustments, similarity_scores, pair_details
        )

        # Bound extreme values
        if result.reconciled_adjustment is not None:
            original = result.reconciled_adjustment
            bounded = max(0.5, min(3.0, original))
            if bounded != original:
                self._add_disclosure(
                    DisclosureCategory.METHODOLOGY_LIMITATION,
                    f"Age depreciation bounded from {original:.2f}% to {bounded:.2f}%",
                    "Value constrained to reasonable range (0.5-3% per year)",
                    "Review comparables for unusual depreciation patterns"
                )
                result.reconciled_adjustment = bounded

        self._log(f"  Pairs found: {len(pairs)}")
        self._log(f"  Mean depreciation: {result.mean_adjustment:.2f}% per year" if result.mean_adjustment else "  Mean: N/A")
        self._log(f"  Reconciled: {result.reconciled_adjustment:.2f}%" if result.reconciled_adjustment else "  Reconciled: N/A")
        self._log(f"  Confidence: {result.confidence}")

        return result

    def _derive_clear_height(self) -> PairedSalesResult:
        """Derive clear height adjustment for industrial properties."""
        self._log("\n--- Clear Height Adjustment ---")

        def get_clear_height(comp):
            return comp.get('clear_height_feet')

        pairs = self._find_pairs_differing_in('clear_height_feet', get_clear_height)

        if len(pairs) < self.MIN_PAIRS_SINGLE:
            self._log(f"  Insufficient pairs ({len(pairs)}) - using cost approach default")
            default_val = self.INDUSTRY_DEFAULTS['industrial'].get('clear_height_per_foot_per_sf', 1.50)
            return self._create_default_result(
                'clear_height', 'dollars_per_foot_per_sf', default_val,
                'Industrial building cost manuals'
            )

        adjustments = []
        similarity_scores = []
        pair_details = []

        for comp1, comp2, height_diff, similarity, notes in pairs:
            price_diff = comp2.get('price_per_sf', 0) - comp1.get('price_per_sf', 0)
            if height_diff != 0:
                adj_per_foot = price_diff / height_diff
                adjustments.append(adj_per_foot)
                similarity_scores.append(similarity)
                pair_details.append({
                    'comp1': comp1.get('address'),
                    'comp1_height': comp1.get('clear_height_feet'),
                    'comp2': comp2.get('address'),
                    'comp2_height': comp2.get('clear_height_feet'),
                    'height_diff': height_diff,
                    'adjustment_per_foot_psf': round(adj_per_foot, 2),
                    'similarity': round(similarity, 2),
                    'notes': notes
                })

        if not adjustments:
            return self._create_default_result(
                'clear_height', 'dollars_per_foot_per_sf', 1.50, 'No valid pairs found'
            )

        result = self._create_result(
            'clear_height', 'dollars_per_foot_per_sf',
            pairs, adjustments, similarity_scores, pair_details
        )

        # Bound extreme values with disclosure ($0.50 - $4.00 per foot per SF)
        if result.reconciled_adjustment is not None:
            original = result.reconciled_adjustment
            # Reasonable range based on cost approach support and market evidence
            bounded = max(0.50, min(4.00, original))
            if bounded != original:
                self._add_disclosure(
                    DisclosureCategory.METHODOLOGY_LIMITATION,
                    f"Clear height adjustment bounded from ${original:.2f} to ${bounded:.2f}/ft/SF",
                    "Derived value outside reasonable range",
                    "Value constrained to $0.50-$4.00/ft/SF based on cost approach support"
                )
                result.reconciled_adjustment = bounded

        self._log(f"  Pairs found: {len(pairs)}")
        self._log(f"  Mean adjustment: ${result.mean_adjustment:.2f}/ft/SF" if result.mean_adjustment else "  Mean: N/A")
        self._log(f"  Reconciled: ${result.reconciled_adjustment:.2f}/ft/SF" if result.reconciled_adjustment else "  Reconciled: N/A")
        self._log(f"  Confidence: {result.confidence}")

        return result

    def _derive_loading_dock_value(self) -> PairedSalesResult:
        """Derive loading dock value for industrial properties."""
        self._log("\n--- Loading Dock Value ---")

        def get_total_docks(comp):
            dock_high = comp.get('loading_docks_dock_high', 0) or 0
            grade = comp.get('loading_docks_grade_level', 0) or 0
            return dock_high + grade

        pairs = self._find_pairs_differing_in('loading_docks', get_total_docks)

        if len(pairs) < self.MIN_PAIRS_SINGLE:
            self._log(f"  Insufficient pairs ({len(pairs)}) - using cost approach default")
            default_val = self.INDUSTRY_DEFAULTS['industrial'].get('loading_dock_dock_high', 35000)
            return self._create_default_result(
                'loading_docks', 'dollars_per_dock', default_val,
                'RS Means construction cost data'
            )

        adjustments = []
        similarity_scores = []
        pair_details = []

        for comp1, comp2, dock_diff, similarity, notes in pairs:
            price_diff = comp2.get('sale_price', 0) - comp1.get('sale_price', 0)
            if dock_diff != 0:
                value_per_dock = price_diff / dock_diff
                adjustments.append(value_per_dock)
                similarity_scores.append(similarity)
                pair_details.append({
                    'comp1': comp1.get('address'),
                    'comp1_docks': get_total_docks(comp1),
                    'comp2': comp2.get('address'),
                    'comp2_docks': get_total_docks(comp2),
                    'dock_diff': dock_diff,
                    'value_per_dock': round(value_per_dock, 0),
                    'similarity': round(similarity, 2),
                    'notes': notes
                })

        if not adjustments:
            return self._create_default_result(
                'loading_docks', 'dollars_per_dock', 35000, 'No valid pairs found'
            )

        result = self._create_result(
            'loading_docks', 'dollars_per_dock',
            pairs, adjustments, similarity_scores, pair_details
        )

        # Bound extreme values with disclosure ($15,000 - $75,000 per dock)
        if result.reconciled_adjustment is not None:
            original = result.reconciled_adjustment
            # Reasonable range for Hamilton industrial market based on cost approach
            bounded = max(15000, min(75000, original))
            if bounded != original:
                self._add_disclosure(
                    DisclosureCategory.METHODOLOGY_LIMITATION,
                    f"Loading dock value bounded from ${original:,.0f} to ${bounded:,.0f} per dock",
                    "Derived value outside reasonable range for typical industrial",
                    "Value constrained to $15,000-$75,000 per dock based on cost approach support"
                )
                result.reconciled_adjustment = bounded

        self._log(f"  Pairs found: {len(pairs)}")
        self._log(f"  Mean value: ${result.mean_adjustment:,.0f}/dock" if result.mean_adjustment else "  Mean: N/A")
        self._log(f"  Reconciled: ${result.reconciled_adjustment:,.0f}/dock" if result.reconciled_adjustment else "  Reconciled: N/A")
        self._log(f"  Confidence: {result.confidence}")

        return result

    def _derive_rail_spur_premium(self) -> PairedSalesResult:
        """Derive rail spur premium for industrial properties."""
        self._log("\n--- Rail Spur Premium ---")

        pairs = []
        for i, comp1 in enumerate(self.comparables):
            for comp2 in self.comparables[i+1:]:
                rail1 = comp1.get('rail_spur')
                rail2 = comp2.get('rail_spur')

                if rail1 is None or rail2 is None:
                    continue
                if rail1 == rail2:
                    continue

                is_valid, similarity, notes = self._is_similar_pair(comp1, comp2, 'rail_spur')
                if is_valid:
                    if rail1:
                        pairs.append((comp2, comp1, 1, similarity, notes))
                    else:
                        pairs.append((comp1, comp2, 1, similarity, notes))

        if len(pairs) < self.MIN_PAIRS_SINGLE:
            self._log(f"  Insufficient pairs ({len(pairs)}) - using cost approach default")
            default_val = self.INDUSTRY_DEFAULTS['industrial'].get('rail_spur_lump', 350000)
            return self._create_default_result(
                'rail_spur', 'dollars_lump_sum', default_val,
                'Railway siding installation cost estimates'
            )

        adjustments = []
        similarity_scores = []
        pair_details = []

        for no_rail, with_rail, _, similarity, notes in pairs:
            price_diff = with_rail.get('sale_price', 0) - no_rail.get('sale_price', 0)
            adjustments.append(price_diff)
            similarity_scores.append(similarity)
            pair_details.append({
                'without_rail': no_rail.get('address'),
                'with_rail': with_rail.get('address'),
                'premium': round(price_diff, 0),
                'similarity': round(similarity, 2),
                'notes': notes
            })

        if not adjustments:
            return self._create_default_result(
                'rail_spur', 'dollars_lump_sum', 350000, 'No valid pairs found'
            )

        result = self._create_result(
            'rail_spur', 'dollars_lump_sum',
            pairs, adjustments, similarity_scores, pair_details
        )

        self._log(f"  Pairs found: {len(pairs)}")
        self._log(f"  Mean premium: ${result.mean_adjustment:,.0f}" if result.mean_adjustment else "  Mean: N/A")
        self._log(f"  Reconciled: ${result.reconciled_adjustment:,.0f}" if result.reconciled_adjustment else "  Reconciled: N/A")
        self._log(f"  Confidence: {result.confidence}")

        return result

    def _derive_building_class(self) -> PairedSalesResult:
        """Derive building class adjustment for office properties."""
        self._log("\n--- Building Class Adjustment ---")

        class_order = ['C', 'B-', 'B', 'B+', 'A-', 'A', 'A+']

        def get_class_level(comp):
            bclass = comp.get('building_class', '')
            if bclass in class_order:
                return class_order.index(bclass)
            return None

        pairs = []
        for i, comp1 in enumerate(self.comparables):
            for comp2 in self.comparables[i+1:]:
                level1 = get_class_level(comp1)
                level2 = get_class_level(comp2)

                if level1 is None or level2 is None:
                    continue
                if level1 == level2:
                    continue

                is_valid, similarity, notes = self._is_similar_pair(comp1, comp2, 'building_class')
                if is_valid:
                    pairs.append((comp1, comp2, level2 - level1, similarity, notes))

        if len(pairs) < self.MIN_PAIRS_SINGLE:
            self._log(f"  Insufficient pairs ({len(pairs)}) - using industry default")
            default_val = self.INDUSTRY_DEFAULTS['office'].get('building_class_per_level_pct', 8.0)
            return self._create_default_result(
                'building_class', 'percent_per_class_level', default_val,
                'Industry office class premium estimates'
            )

        adjustments = []
        similarity_scores = []
        pair_details = []

        for comp1, comp2, level_diff, similarity, notes in pairs:
            price1 = comp1.get('price_per_sf', 0)
            price2 = comp2.get('price_per_sf', 0)
            avg_price = (price1 + price2) / 2

            if avg_price > 0 and level_diff != 0:
                price_diff_pct = ((price2 - price1) / avg_price) * 100
                adj_per_level = price_diff_pct / level_diff
                adjustments.append(adj_per_level)
                similarity_scores.append(similarity)
                pair_details.append({
                    'comp1': comp1.get('address'),
                    'comp1_class': comp1.get('building_class'),
                    'comp2': comp2.get('address'),
                    'comp2_class': comp2.get('building_class'),
                    'level_diff': level_diff,
                    'adjustment_per_level_pct': round(adj_per_level, 1),
                    'similarity': round(similarity, 2),
                    'notes': notes
                })

        if not adjustments:
            return self._create_default_result(
                'building_class', 'percent_per_class_level', 8.0, 'No valid pairs found'
            )

        result = self._create_result(
            'building_class', 'percent_per_class_level',
            pairs, adjustments, similarity_scores, pair_details
        )

        self._log(f"  Pairs found: {len(pairs)}")
        self._log(f"  Mean adjustment: {result.mean_adjustment:.1f}% per class level" if result.mean_adjustment else "  Mean: N/A")
        self._log(f"  Reconciled: {result.reconciled_adjustment:.1f}%" if result.reconciled_adjustment else "  Reconciled: N/A")
        self._log(f"  Confidence: {result.confidence}")

        return result

    def _derive_submarket_differentials(self) -> Dict[str, float]:
        """
        Derive price differentials between submarkets.

        Note: This uses submarket averaging, NOT paired sales.
        Disclosed as different methodology per CUSPAP.
        """
        self._log("\n--- Submarket Differentials ---")
        self._log("  Method: Submarket average comparison (not paired sales)")

        # Group sales by submarket
        by_submarket = {}
        for comp in self.comparables:
            submarket = comp.get('location_submarket')
            if submarket and comp.get('price_per_sf'):
                if submarket not in by_submarket:
                    by_submarket[submarket] = []
                by_submarket[submarket].append(comp['price_per_sf'])

        if len(by_submarket) < 2:
            self._log("  Insufficient submarket diversity for differential analysis")
            self._add_disclosure(
                DisclosureCategory.DATA_LIMITATION,
                "Insufficient submarket diversity for location differential analysis",
                "Cannot derive market-based location adjustments",
                "Consider qualitative location analysis or expand search area"
            )
            return {}

        # Calculate average $/SF per submarket
        submarket_avgs = {}
        for sm, prices in by_submarket.items():
            if prices:
                avg = safe_mean(prices)
                if avg is not None:
                    submarket_avgs[sm] = avg

        # Find base submarket
        subject_submarket = self.subject.get('location_submarket')
        if subject_submarket and subject_submarket in submarket_avgs:
            base_submarket = subject_submarket
        else:
            base_submarket = max(by_submarket.keys(), key=lambda x: len(by_submarket[x]))

        base_price = submarket_avgs.get(base_submarket)
        if not base_price or base_price <= 0:
            self._log("  Cannot calculate differentials - invalid base submarket price")
            return {}

        # Calculate differentials
        differentials = {}
        for sm, avg_price in submarket_avgs.items():
            if avg_price is not None and base_price > 0:
                diff_pct = ((avg_price - base_price) / base_price) * 100
                differentials[sm] = round(diff_pct, 1)
                sample_size = len(by_submarket[sm])
                self._log(f"  {sm}: {diff_pct:+.1f}% vs {base_submarket} (n={sample_size})")

        # Add methodology disclosure
        self._add_disclosure(
            DisclosureCategory.METHODOLOGY_LIMITATION,
            "Submarket differentials derived from average price comparison, not paired sales",
            "Differentials may reflect factors other than location",
            "Verify with paired sales if similar properties available across submarkets"
        )

        return differentials

    # -------------------------------------------------------------------------
    # OUTPUT METHODS
    # -------------------------------------------------------------------------

    def _generate_scope_of_work(self) -> Dict[str, Any]:
        """
        Generate CUSPAP 2024 Rule 6.2.3 compliant Scope of Work disclosure.

        Per CUSPAP 2024, the scope of work must identify:
        - Problem identification
        - Extent of research and data collection
        - Type and extent of analysis applied
        - Limiting conditions that affect the analysis
        """
        # Count market-derived vs non-market-derived adjustments
        market_derived_count = 0
        non_market_derived_count = 0
        adjustment_characteristics = []

        for name, result in [
            ('market_appreciation', self.derived.market_appreciation_rate),
            ('size_adjustment', self.derived.size_adjustment_per_sf),
            ('highway_frontage', self.derived.highway_frontage_premium),
            ('condition', self.derived.condition_adjustment_per_level),
            ('age_depreciation', self.derived.age_depreciation_per_year),
            ('clear_height', self.derived.clear_height_adjustment_per_foot),
            ('loading_docks', self.derived.loading_dock_value),
            ('rail_spur', self.derived.rail_spur_premium),
            ('building_class', self.derived.building_class_adjustment),
        ]:
            if result is not None:
                if result.market_supported:
                    market_derived_count += 1
                else:
                    non_market_derived_count += 1
                adjustment_characteristics.append({
                    'name': name,
                    'confidence': result.confidence,
                    'method': result.derivation_method.value,
                    'market_supported': result.market_supported
                })

        # Identify data sources used
        data_sources = ['Comparable sales data provided']
        if any(c.get('sale_date') for c in self.comparables):
            data_sources.append('Transaction dates for time adjustment')
        if any(c.get('location_submarket') for c in self.comparables):
            data_sources.append('Submarket classifications')

        # Identify analyses NOT performed
        analyses_not_performed = []
        if self.derived.clear_height_adjustment_per_foot is None or not self.derived.clear_height_adjustment_per_foot.market_supported:
            analyses_not_performed.append('Clear height paired sales analysis (insufficient pairs)')
        if self.derived.rail_spur_premium is None or not self.derived.rail_spur_premium.market_supported:
            analyses_not_performed.append('Rail spur paired sales analysis (insufficient pairs)')

        return {
            'cuspap_rule': '6.2.3',
            'problem_identification': {
                'assignment_type': 'Adjustment factor derivation for comparable sales approach',
                'property_type': self.property_type,
                'valuation_date': self.valuation_date.isoformat(),
                'intended_use': 'Support comparable sales adjustments in property valuation'
            },
            'data_research': {
                'comparables_provided': len(self.raw_comparables),
                'comparables_verified': len(self.comparables),
                'comparables_excluded': len(self.raw_comparables) - len(self.comparables),
                'data_sources': data_sources,
                'search_criteria': 'Comparable sales within provided dataset',
                'time_frame': f'Sales through valuation date {self.valuation_date}'
            },
            'analysis_applied': {
                'primary_method': 'Paired sales isolation method',
                'secondary_methods': ['Time-series regression (for time adjustment)', 'Submarket averaging (for location)'],
                'similarity_thresholds': 'Strict' if self.strict_mode else 'Standard',
                'market_derived_adjustments': market_derived_count,
                'non_market_derived_adjustments': non_market_derived_count,
                'adjustment_characteristics': adjustment_characteristics
            },
            'limiting_conditions': {
                'data_limitations': [
                    d.description for d in self.disclosures
                    if d.category == DisclosureCategory.DATA_LIMITATION
                ],
                'methodology_limitations': [
                    d.description for d in self.disclosures
                    if d.category == DisclosureCategory.METHODOLOGY_LIMITATION
                ],
                'analyses_not_performed': analyses_not_performed,
                'extraordinary_assumptions': [
                    d.description for d in self.disclosures
                    if d.category == DisclosureCategory.EXTRAORDINARY_ASSUMPTION
                ],
                'non_market_derived_items': [
                    d.description for d in self.disclosures
                    if d.category == DisclosureCategory.NON_MARKET_DERIVED
                ]
            },
            'competency_statement': (
                'This analysis was performed using CUSPAP 2024 compliant paired sales '
                'methodology. The analyst has reviewed the data provided and applied '
                'appropriate verification, adjustment, and reconciliation procedures.'
            )
        }

    def get_adjustment_factors(self) -> Dict[str, Any]:
        """Export derived adjustments in format usable by calculator."""
        factors = {
            'derivation_date': datetime.now().isoformat(),
            'valuation_date': self.valuation_date.isoformat(),
            'property_type': self.property_type,
            'comparables_analyzed': len(self.comparables),
            'comparables_excluded': len(self.raw_comparables) - len(self.comparables),
            'analysis_mode': 'strict' if self.strict_mode else 'standard',
            'cuspap_compliant': True,
            'factors': {},
            'disclosures': [],
            # CUSPAP 2024 Rule 6.2.3 - Scope of Work Disclosure
            'scope_of_work': self._generate_scope_of_work()
        }

        # Add adjustment factors
        def add_factor(name, result):
            if result is None:
                return
            factors['factors'][name] = {
                'value': result.reconciled_adjustment or result.mean_adjustment,
                'mean': result.mean_adjustment,
                'median': result.median_adjustment,
                'stdev': result.stdev_adjustment,
                'cv': result.coefficient_of_variation,
                'confidence': result.confidence,
                'method': result.derivation_method.value,
                'pairs_found': result.pairs_found,
                'unit': result.unit,
                'market_supported': result.market_supported
            }

        add_factor('appreciation_rate_annual_pct', self.derived.market_appreciation_rate)
        add_factor('size_adjustment_pct_per_10000sf', self.derived.size_adjustment_per_sf)
        add_factor('highway_frontage_premium_pct', self.derived.highway_frontage_premium)
        add_factor('condition_per_level_pct', self.derived.condition_adjustment_per_level)
        add_factor('age_depreciation_pct_per_year', self.derived.age_depreciation_per_year)
        add_factor('clear_height_per_foot_per_sf', self.derived.clear_height_adjustment_per_foot)
        add_factor('loading_dock_value', self.derived.loading_dock_value)
        add_factor('rail_spur_premium', self.derived.rail_spur_premium)
        add_factor('building_class_per_level_pct', self.derived.building_class_adjustment)

        if self.derived.submarket_differentials:
            factors['factors']['submarket_differentials'] = {
                'values': self.derived.submarket_differentials,
                'confidence': 'medium' if len(self.derived.submarket_differentials) > 2 else 'low',
                'method': DerivationMethod.SUBMARKET_AVERAGE.value,
                'market_supported': True
            }

        # Add disclosures
        for disc in self.disclosures:
            factors['disclosures'].append({
                'category': disc.category.value,
                'description': disc.description,
                'impact': disc.impact,
                'recommendation': disc.recommendation
            })

        return factors

    def get_analysis_report(self) -> str:
        """Return full analysis log as string."""
        return '\n'.join(self.analysis_log)

    def get_cuspap_disclosure_report(self) -> str:
        """Generate CUSPAP-compliant disclosure report."""
        lines = [
            "=" * 70,
            "CUSPAP DISCLOSURE REPORT",
            "=" * 70,
            f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"Valuation Date: {self.valuation_date}",
            f"Property Type: {self.property_type}",
            f"Analysis Mode: {'Strict' if self.strict_mode else 'Standard'}",
            "",
            "TRANSACTION VERIFICATION SUMMARY",
            "-" * 40,
            f"Raw Comparables: {len(self.raw_comparables)}",
            f"Verified Comparables: {len(self.comparables)}",
            f"Excluded: {len(self.raw_comparables) - len(self.comparables)}",
            ""
        ]

        if self.transaction_adjustments:
            lines.append("TRANSACTION ADJUSTMENTS APPLIED")
            lines.append("-" * 40)
            for adj in self.transaction_adjustments:
                status = "EXCLUDED" if adj.excluded else "VERIFIED"
                lines.append(f"  {adj.comparable_address}: {status}")
                if adj.adjustments_applied:
                    for adj_type, amount in adj.adjustments_applied.items():
                        lines.append(f"    - {adj_type}: ${amount:,.0f}")
                if adj.exclusion_reason:
                    lines.append(f"    - Reason: {adj.exclusion_reason}")
            lines.append("")

        if self.disclosures:
            lines.append("REQUIRED DISCLOSURES")
            lines.append("-" * 40)

            by_category = {}
            for disc in self.disclosures:
                cat = disc.category.value
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(disc)

            for category, discs in by_category.items():
                lines.append(f"\n{category.upper().replace('_', ' ')}:")
                for i, disc in enumerate(discs, 1):
                    lines.append(f"  {i}. {disc.description}")
                    lines.append(f"     Impact: {disc.impact}")
                    lines.append(f"     Recommendation: {disc.recommendation}")
        else:
            lines.append("No extraordinary assumptions or limiting conditions identified.")

        lines.append("")
        lines.append("=" * 70)
        lines.append("END OF DISCLOSURE REPORT")
        lines.append("=" * 70)

        return '\n'.join(lines)


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """Standalone execution."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python paired_sales_analyzer.py <input.json> [--strict|--standard]")
        print("\nOptions:")
        print("  --strict   Use strict similarity thresholds (default)")
        print("  --standard Use standard (more permissive) thresholds")
        sys.exit(1)

    # Parse arguments
    input_file = sys.argv[1]
    strict_mode = '--standard' not in sys.argv

    # Load data
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Run analysis
    analyzer = PairedSalesAnalyzer(
        comparables=data['comparable_sales'],
        subject=data['subject_property'],
        property_type=data['subject_property'].get('property_type', 'industrial'),
        strict_mode=strict_mode,
        valuation_date=data.get('market_parameters', {}).get('valuation_date')
    )

    analyzer.analyze_all()

    # Output reports
    print(analyzer.get_analysis_report())
    print("\n")
    print(analyzer.get_cuspap_disclosure_report())
    print("\n" + "=" * 70)
    print("DERIVED ADJUSTMENT FACTORS (JSON)")
    print("=" * 70)
    print(json.dumps(analyzer.get_adjustment_factors(), indent=2))


if __name__ == '__main__':
    main()
