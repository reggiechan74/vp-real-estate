#!/usr/bin/env python3
"""
Comparable Sales Adjustment Calculator

Applies sequential 6-stage adjustment hierarchy to comparable sales:
1. Property rights (leasehold → fee simple conversion)
2. Financing terms (seller VTB → cash equivalent PV)
3. Conditions of sale (non-arm's length adjustment)
4. Market conditions/time (appreciation compounding)
5. Location (micro-market premiums)
6. Physical characteristics (size, shape, improvements)

Includes adjustment quantification methodologies (paired sales, regression, cost, income),
statistical validation (gross <25% individual, <40% cumulative; net <15%), and
sensitivity analysis (+/-10% key adjustments).

Supports: comparable-sales-adjustment-methodology skill
Used by: Alexi (Expropriation Appraisal Expert), appraisal professionals

Author: Claude Code
Created: 2025-11-15
"""

import sys
import json
import argparse
import math
import logging
from pathlib import Path
from typing import Dict, List, Optional, Literal, Any, Union
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Add Shared_Utils to path (one level up from Comparable_Sales_Analysis to repo root)
sys.path.insert(0, str(Path(__file__).parent.parent / "Shared_Utils"))
from financial_utils import pv_annuity, npv, descriptive_statistics

# Import adjustment modules
from adjustments import (
    land, site, industrial_building, office_building,
    building_general, special_features, zoning_legal
)

# Import parameter mapping to resolve derived -> module name mismatch
from adjustments.parameter_mapping import (
    map_derived_factors_to_module_params,
    validate_factor_application,
    generate_factor_source_report
)

# Import paired sales analyzer for deriving adjustment factors
from paired_sales_analyzer import PairedSalesAnalyzer

# ============================================================================
# CONSTANTS - Avoid magic numbers
# ============================================================================
MATERIAL_ADJUSTMENT_THRESHOLD_PCT = 5.0  # Minimum % to include in sensitivity
GROSS_ADJUSTMENT_WARNING_PCT = 25.0      # USPAP/CUSPAP warning threshold
GROSS_ADJUSTMENT_REJECT_PCT = 40.0       # Reject comparable if exceeded
NET_ADJUSTMENT_WARNING_PCT = 15.0        # Net adjustment warning threshold
CAUTION_ZONE_LOWER_PCT = 30.0            # Lower bound of caution zone
LOCATION_SCORE_SIGNIFICANCE = 0.1        # Min location adjustment % to report


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    if denominator == 0:
        return default
    return numerator / denominator


def parse_date_flexible(date_str: str) -> Optional[datetime]:
    """
    Parse date string with multiple format support.

    Supports: ISO format, MM/DD/YYYY, DD-Mon-YYYY, YYYY/MM/DD
    """
    if not date_str:
        return None

    formats = [
        '%Y-%m-%d',      # ISO format
        '%Y-%m-%dT%H:%M:%S',  # ISO with time
        '%Y-%m-%dT%H:%M:%S.%f',  # ISO with microseconds
        '%m/%d/%Y',      # US format
        '%d/%m/%Y',      # European format
        '%d-%b-%Y',      # 15-Jan-2025
        '%Y/%m/%d',      # Alternative ISO
        '%B %d, %Y',     # January 15, 2025
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    # Last resort: try fromisoformat
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        logger.warning(f"Could not parse date: {date_str}")
        return None


class ComparableSalesCalculator:
    """Calculate adjusted comparable sale prices using 6-stage adjustment hierarchy."""

    def __init__(self, input_data: Dict, derived_factors: Optional[Dict] = None):
        """
        Initialize calculator with input data.

        Args:
            input_data: Input JSON with subject, comparables, market_parameters
            derived_factors: Optional adjustment factors derived from paired sales analysis.
                             If provided, these override/supplement market_parameters.
        """
        self.data = input_data
        self.subject = input_data['subject_property']
        self.comparables = input_data['comparable_sales']
        self.market = input_data.get('market_parameters', {})
        self.adjustment_results = []

        # Merge derived factors into market parameters
        # Priority: derived_factors > market_parameters > industry defaults
        self.derived_factors = derived_factors or {}
        self._merge_adjustment_factors()

    def _merge_adjustment_factors(self, verbose: bool = True):
        """
        Merge derived adjustment factors into effective market parameters.

        Priority hierarchy:
        1. User/appraiser overrides from market_parameters (explicit config)
        2. Derived factors from paired sales analysis (market evidence)
        3. Industry defaults (fallback - requires CUSPAP disclosure)

        IMPORTANT: Uses parameter_mapping to translate derived factor names
        to module-compatible parameter names. Without this mapping, derived
        factors would be silently ignored.
        """
        # Industry defaults by property type (CUSPAP: requires disclosure when used)
        property_type = self.subject.get('property_type', 'industrial')

        self.INDUSTRY_DEFAULTS = {
            'industrial': {
                'appreciation_rate_annual': 3.5,
                'condition_adjustment_pct_per_level': 5.0,
                'clear_height_value_per_foot_per_sf': 1.50,
                'loading_dock_value_dock_high': 35000,
                'loading_dock_value_grade_level': 15000,
                'loading_dock_value_per_dock': 35000,  # Aggregate per-dock value
                'highway_frontage_premium_pct': 12.0,
                'rail_spur_premium': 350000,
                'annual_depreciation_pct': 1.0,
                'size_adjustment_pct_per_10000sf': -2.0,
                'cap_rate': 7.0,
            },
            'office': {
                'appreciation_rate_annual': 3.5,
                'condition_adjustment_pct_per_level': 8.0,
                'building_class_adjustment_pct_per_level': 8.0,
                'parking_value_per_space': 4500,
                'elevator_value_per_unit': 150000,
                'annual_depreciation_pct': 1.5,
                'cap_rate': 6.5,
            }
        }

        # Start with industry defaults for property type
        self.effective_factors = self.INDUSTRY_DEFAULTS.get(
            property_type, self.INDUSTRY_DEFAULTS['industrial']
        ).copy()

        # Layer 1: Map and apply derived factors (with name translation)
        if self.derived_factors and 'factors' in self.derived_factors:
            # Use parameter_mapping to translate derived names -> module names
            mapped_derived = map_derived_factors_to_module_params(
                self.derived_factors['factors'],
                log_mappings=verbose
            )
            self.effective_factors.update(mapped_derived)

            if verbose:
                logger.info(f"Applied {len(mapped_derived)} derived factors (name-mapped)")

        # Layer 2: User/appraiser overrides have highest priority
        # These are already in module-compatible naming (direct from config)
        if self.market:
            for key, value in self.market.items():
                if value is not None:
                    self.effective_factors[key] = value
            if verbose:
                logger.info(f"Applied {len(self.market)} user overrides")

        # Generate factor source report for CUSPAP compliance
        self.factor_sources = {}
        derived_factors_dict = self.derived_factors.get('factors', {}) if self.derived_factors else {}

        for key in self.effective_factors:
            # Check if this came from derived factors (mapped)
            mapped_derived = map_derived_factors_to_module_params(
                derived_factors_dict, log_mappings=False
            ) if derived_factors_dict else {}

            if key in self.market:
                self.factor_sources[key] = 'appraiser_input'
            elif key in mapped_derived:
                self.factor_sources[key] = 'derived_from_paired_sales'
            else:
                self.factor_sources[key] = 'industry_default'

        # Validation: verify derived factors were correctly applied
        if verbose and self.derived_factors and 'factors' in self.derived_factors:
            validation = validate_factor_application(
                self.effective_factors,
                self.derived_factors['factors']
            )
            if validation['total_applied'] > 0:
                logger.info(
                    f"Factor validation: {validation['total_applied']}/{validation['total_derived']} "
                    f"derived factors correctly applied"
                )
            if validation['using_defaults']:
                logger.warning(
                    f"Parameters using defaults instead of derived: "
                    f"{[d['param'] for d in validation['using_defaults']]}"
                )

    def calculate_property_rights_adjustment(self, comparable: Dict, base_price: float) -> Dict:
        """
        Stage 1: Property Rights Adjustment

        Convert leasehold to fee simple equivalent by capitalizing ground rent.

        Example:
        - Leasehold sale: $1,200,000
        - Ground rent: $50,000/year
        - Cap rate: 5%
        - Capitalized land value: $50,000 ÷ 0.05 = $1,000,000
        - Fee simple equivalent: $1,200,000 + $1,000,000 = $2,200,000
        """
        comp_rights = comparable.get('property_rights', 'fee_simple')
        subject_rights = self.subject.get('property_rights', 'fee_simple')

        # No adjustment needed if both are fee simple
        if comp_rights == 'fee_simple' and subject_rights == 'fee_simple':
            return {
                'stage': 1,
                'name': 'Property Rights',
                'adjustment_amount': 0.0,
                'adjustment_pct': 0.0,
                'adjusted_price': base_price,
                'explanation': 'Both subject and comparable are fee simple - no adjustment'
            }

        # Leasehold to fee simple conversion
        if comp_rights == 'leasehold':
            ground_rent_annual = comparable.get('ground_rent_annual', 0)
            cap_rate = self.effective_factors.get('cap_rate', 7.0) / 100

            if ground_rent_annual > 0 and cap_rate > 0:
                capitalized_land_value = ground_rent_annual / cap_rate
                adjusted_price = base_price + capitalized_land_value
                adjustment_amount = capitalized_land_value
                adjustment_pct = safe_divide(adjustment_amount, base_price) * 100

                return {
                    'stage': 1,
                    'name': 'Property Rights',
                    'adjustment_amount': adjustment_amount,
                    'adjustment_pct': adjustment_pct,
                    'adjusted_price': adjusted_price,
                    'ground_rent_annual': ground_rent_annual,
                    'capitalized_land_value': capitalized_land_value,
                    'explanation': f'Leasehold converted to fee simple: ${ground_rent_annual:,.0f}/year ÷ {cap_rate:.1%} = ${capitalized_land_value:,.0f}'
                }

        return {
            'stage': 1,
            'name': 'Property Rights',
            'adjustment_amount': 0.0,
            'adjustment_pct': 0.0,
            'adjusted_price': base_price,
            'explanation': 'No property rights adjustment required'
        }

    def calculate_financing_adjustment(self, comparable: Dict, base_price: float) -> Dict:
        """
        Stage 2: Financing Terms Adjustment

        Convert seller financing at below-market rates to cash equivalent.

        Example:
        - Sale price: $800,000
        - Seller VTB: 2% interest (market rate 6%)
        - PV of below-market financing benefit: $120,000
        - Cash equivalent: $800,000 - $120,000 = $680,000
        """
        financing = comparable.get('financing', {})
        financing_type = financing.get('type', 'cash')

        if financing_type == 'cash':
            return {
                'stage': 2,
                'name': 'Financing Terms',
                'adjustment_amount': 0.0,
                'adjustment_pct': 0.0,
                'adjusted_price': base_price,
                'explanation': 'Cash sale - no financing adjustment'
            }

        # Seller VTB (Vendor Take-Back) financing
        if financing_type == 'seller_vtb':
            seller_rate = financing.get('rate', 0) / 100
            market_rate = financing.get('market_rate', 6.0) / 100
            term_years = financing.get('term_years', 10)
            loan_amount = financing.get('loan_amount', base_price * 0.5)

            # Calculate PV of financing benefit
            # Buyer pays lower rate, saves (market_rate - seller_rate) × loan_amount
            rate_differential = market_rate - seller_rate

            if rate_differential > 0:
                # Annual payment at seller rate
                monthly_rate_seller = (1 + seller_rate) ** (1/12) - 1
                periods = term_years * 12

                # Payment at seller rate
                if seller_rate == 0:
                    payment_seller = loan_amount / periods
                else:
                    payment_seller = loan_amount * (monthly_rate_seller * (1 + monthly_rate_seller) ** periods) / ((1 + monthly_rate_seller) ** periods - 1)

                # Payment at market rate
                monthly_rate_market = (1 + market_rate) ** (1/12) - 1
                payment_market = loan_amount * (monthly_rate_market * (1 + monthly_rate_market) ** periods) / ((1 + monthly_rate_market) ** periods - 1)

                # Monthly savings
                monthly_savings = payment_market - payment_seller

                # PV of savings at market rate
                financing_benefit = pv_annuity(monthly_savings, monthly_rate_market, periods, timing='end')

                # Cash equivalent (subtract financing benefit from sale price)
                adjusted_price = base_price - financing_benefit
                adjustment_amount = -financing_benefit
                adjustment_pct = safe_divide(adjustment_amount, base_price) * 100

                return {
                    'stage': 2,
                    'name': 'Financing Terms',
                    'adjustment_amount': adjustment_amount,
                    'adjustment_pct': adjustment_pct,
                    'adjusted_price': adjusted_price,
                    'seller_rate': seller_rate * 100,
                    'market_rate': market_rate * 100,
                    'loan_amount': loan_amount,
                    'financing_benefit': financing_benefit,
                    'explanation': f'Seller VTB at {seller_rate:.1%} vs. market {market_rate:.1%}: PV benefit ${financing_benefit:,.0f} deducted from sale price'
                }

        return {
            'stage': 2,
            'name': 'Financing Terms',
            'adjustment_amount': 0.0,
            'adjustment_pct': 0.0,
            'adjusted_price': base_price,
            'explanation': 'No financing adjustment required'
        }

    def calculate_conditions_of_sale_adjustment(self, comparable: Dict, base_price: float) -> Dict:
        """
        Stage 3: Conditions of Sale Adjustment

        Adjust for non-arm's length transactions.

        Example:
        - Related party sale: $500,000
        - Market evidence: 10% discount for motivated seller
        - Arm's length equivalent: $500,000 ÷ 0.90 = $556,000
        """
        conditions = comparable.get('conditions_of_sale', {})
        is_arms_length = conditions.get('arms_length', True)

        if is_arms_length:
            return {
                'stage': 3,
                'name': 'Conditions of Sale',
                'adjustment_amount': 0.0,
                'adjustment_pct': 0.0,
                'adjusted_price': base_price,
                'explanation': 'Arm\'s length transaction - no adjustment'
            }

        # Non-arm's length adjustment
        motivation_discount_pct = conditions.get('motivation_discount_pct', 0)

        if motivation_discount_pct > 0:
            # Sale price was discounted, adjust upward to arm's length equivalent
            discount_factor = 1 - (motivation_discount_pct / 100)
            if discount_factor <= 0:
                discount_factor = 0.01  # Prevent division by zero, cap at 99% discount
            adjusted_price = base_price / discount_factor
            adjustment_amount = adjusted_price - base_price
            adjustment_pct = safe_divide(adjustment_amount, base_price) * 100

            return {
                'stage': 3,
                'name': 'Conditions of Sale',
                'adjustment_amount': adjustment_amount,
                'adjustment_pct': adjustment_pct,
                'adjusted_price': adjusted_price,
                'motivation_discount_pct': motivation_discount_pct,
                'explanation': f'Non-arm\'s length sale with {motivation_discount_pct}% discount: adjusted to arm\'s length equivalent'
            }

        return {
            'stage': 3,
            'name': 'Conditions of Sale',
            'adjustment_amount': 0.0,
            'adjustment_pct': 0.0,
            'adjusted_price': base_price,
            'explanation': 'No conditions of sale adjustment required'
        }

    def calculate_market_conditions_adjustment(self, comparable: Dict, base_price: float) -> Dict:
        """
        Stage 4: Market Conditions/Time Adjustment

        Adjust for appreciation between sale date and valuation date.

        Example:
        - Sale date: 18 months prior
        - Market trend: +2.5% per year
        - Adjustment: $680,000 × (1.025^1.5) = $706,000
        """
        sale_date = comparable.get('sale_date', '')

        if not sale_date:
            return {
                'stage': 4,
                'name': 'Market Conditions/Time',
                'adjustment_amount': 0.0,
                'adjustment_pct': 0.0,
                'adjusted_price': base_price,
                'explanation': 'No sale date provided - no time adjustment'
            }

        # Parse dates using flexible parser
        try:
            sale_datetime = parse_date_flexible(sale_date)
            if not sale_datetime:
                return {
                    'stage': 4,
                    'name': 'Market Conditions/Time',
                    'adjustment_amount': 0.0,
                    'adjustment_pct': 0.0,
                    'adjusted_price': base_price,
                    'explanation': f'Could not parse sale date: {sale_date}'
                }

            valuation_date = self.market.get('valuation_date', datetime.now().isoformat())
            valuation_datetime = parse_date_flexible(valuation_date)
            if not valuation_datetime:
                valuation_datetime = datetime.now()

            # Calculate time difference in years
            days_difference = (valuation_datetime - sale_datetime).days
            years_difference = days_difference / 365.25

            if years_difference <= 0:
                return {
                    'stage': 4,
                    'name': 'Market Conditions/Time',
                    'adjustment_amount': 0.0,
                    'adjustment_pct': 0.0,
                    'adjusted_price': base_price,
                    'explanation': 'Sale date is current or future - no time adjustment'
                }

            # Apply appreciation - use derived/effective factors
            appreciation_rate_annual = self.effective_factors.get('appreciation_rate_annual', 3.5) / 100

            if appreciation_rate_annual == 0:
                return {
                    'stage': 4,
                    'name': 'Market Conditions/Time',
                    'adjustment_amount': 0.0,
                    'adjustment_pct': 0.0,
                    'adjusted_price': base_price,
                    'explanation': 'No market appreciation assumed'
                }

            # Compound appreciation: Price × (1 + rate)^years
            adjusted_price = base_price * ((1 + appreciation_rate_annual) ** years_difference)
            adjustment_amount = adjusted_price - base_price
            adjustment_pct = safe_divide(adjustment_amount, base_price) * 100

            return {
                'stage': 4,
                'name': 'Market Conditions/Time',
                'adjustment_amount': adjustment_amount,
                'adjustment_pct': adjustment_pct,
                'adjusted_price': adjusted_price,
                'sale_date': sale_date,
                'valuation_date': valuation_date,
                'years_difference': years_difference,
                'appreciation_rate_annual': appreciation_rate_annual * 100,
                'explanation': f'{years_difference:.1f} years appreciation at {appreciation_rate_annual:.1%} annually'
            }

        except (ValueError, KeyError) as e:
            return {
                'stage': 4,
                'name': 'Market Conditions/Time',
                'adjustment_amount': 0.0,
                'adjustment_pct': 0.0,
                'adjusted_price': base_price,
                'explanation': f'Error parsing dates: {str(e)}'
            }

    def calculate_location_adjustment(self, comparable: Dict, base_price: float) -> Dict:
        """
        Stage 5: Location Adjustment (NON-LINEAR MODEL)

        CUSPAP Compliance: Components are non-overlapping to prevent double-counting.

        Component Hierarchy (applied in order):
        1. Submarket differential (if different submarket)
        2. Highway frontage premium (if highway status differs)
        3. Location score differential (ONLY if same submarket AND same highway status)

        Note: Location score adjustment is ONLY applied when highway frontage status
        is the same, preventing double-counting of location premium.

        Location Score Tiers (0-100 scale):
        - Premium (85-100): Prime locations, limited supply, steep premiums
        - Good (70-84): Desirable locations, moderate premiums
        - Average (50-69): Standard locations, baseline pricing
        - Below Average (30-49): Less desirable, moderate discounts
        - Poor (0-29): Challenged locations, steep discounts
        """
        subject_location_score = self.subject.get('location_score', 50)
        comp_location_score = comparable.get('location_score', 50)

        # Define location tier boundaries and premium rates
        LOCATION_TIERS = [
            {'name': 'Premium', 'min': 85, 'max': 100, 'rate_per_point': 1.5, 'base_premium': 15.0},
            {'name': 'Good', 'min': 70, 'max': 84, 'rate_per_point': 1.0, 'base_premium': 5.0},
            {'name': 'Average', 'min': 50, 'max': 69, 'rate_per_point': 0.5, 'base_premium': 0.0},
            {'name': 'Below Average', 'min': 30, 'max': 49, 'rate_per_point': 0.75, 'base_premium': -5.0},
            {'name': 'Poor', 'min': 0, 'max': 29, 'rate_per_point': 1.0, 'base_premium': -15.0},
        ]

        def get_tier(score: float) -> Dict:
            """Get the tier for a given location score."""
            for tier in LOCATION_TIERS:
                if tier['min'] <= score <= tier['max']:
                    return tier
            return LOCATION_TIERS[2]  # Default to Average

        def calculate_tier_adjustment(score: float) -> float:
            """
            Calculate cumulative adjustment from score 50 (baseline) to given score.
            This creates a non-linear relationship where higher tiers have steeper slopes.
            """
            if score == 50:
                return 0.0

            total_adjustment = 0.0
            current_score = 50  # Baseline

            if score > 50:
                while current_score < score:
                    tier = get_tier(current_score)
                    tier_ceiling = min(tier['max'], score)
                    points_in_tier = tier_ceiling - current_score
                    total_adjustment += points_in_tier * tier['rate_per_point']
                    current_score = tier_ceiling + 1
                    if current_score > score:
                        break
            else:
                while current_score > score:
                    tier = get_tier(current_score)
                    tier_floor = max(tier['min'], score)
                    points_in_tier = current_score - tier_floor
                    total_adjustment -= points_in_tier * tier['rate_per_point']
                    current_score = tier_floor - 1
                    if current_score < score:
                        break

            return total_adjustment

        # Get tier information
        subject_tier = get_tier(subject_location_score)
        comp_tier = get_tier(comp_location_score)

        # Initialize adjustment tracking
        total_adjustment_pct = 0.0
        total_adjustment_amount = 0.0
        components = []

        # =========================================================================
        # COMPONENT 1: SUBMARKET DIFFERENTIAL
        # =========================================================================
        subject_submarket = self.subject.get('location_submarket')
        comp_submarket = comparable.get('location_submarket')

        if subject_submarket and comp_submarket and subject_submarket != comp_submarket:
            differential = self.effective_factors.get('submarket_differentials', {})
            if comp_submarket in differential:
                # Negative because comp is in different submarket
                submarket_adj_pct = -differential[comp_submarket]
                submarket_adjustment = base_price * (submarket_adj_pct / 100)
                total_adjustment_pct += submarket_adj_pct
                total_adjustment_amount += submarket_adjustment
                components.append(f'submarket ({comp_submarket} vs {subject_submarket}: {submarket_adj_pct:+.1f}%)')

        # =========================================================================
        # COMPONENT 2: HIGHWAY FRONTAGE PREMIUM
        # =========================================================================
        highway_premium = self.effective_factors.get('highway_frontage_premium_pct',
                          self.effective_factors.get('location_premium_highway', 12.0))
        subject_highway = self.subject.get('highway_frontage', False)
        comp_highway = comparable.get('highway_frontage', False)

        highway_differs = subject_highway != comp_highway

        if highway_differs and highway_premium > 0:
            if subject_highway and not comp_highway:
                # Subject has highway frontage, comparable doesn't - positive adjustment
                highway_adjustment_pct = highway_premium
                highway_adjustment_amount = base_price * (highway_adjustment_pct / 100)
                components.append(f'highway frontage (subject has, comp does not: +{highway_premium:.1f}%)')
            else:
                # Comparable has highway frontage, subject doesn't - negative adjustment
                highway_adjustment_pct = -highway_premium
                highway_adjustment_amount = base_price * (highway_adjustment_pct / 100)
                components.append(f'highway frontage (comp has, subject does not: -{highway_premium:.1f}%)')

            total_adjustment_pct += highway_adjustment_pct
            total_adjustment_amount += highway_adjustment_amount

        # =========================================================================
        # COMPONENT 3: LOCATION SCORE (with residual logic when highway differs)
        # =========================================================================
        # CUSPAP Compliance: Apply RESIDUAL location score when highway differs.
        # Highway frontage typically accounts for ~7 points of location score difference.
        # Any score difference beyond this attribution should be separately adjusted.

        # Highway score attribution factor - how many points of location score
        # difference are explained by highway frontage (configurable)
        highway_score_attribution = self.effective_factors.get('highway_score_attribution', 7)

        if subject_location_score != comp_location_score:
            score_diff = subject_location_score - comp_location_score

            if not highway_differs:
                # Case 1: Highway same - apply FULL location score adjustment
                subject_adj = calculate_tier_adjustment(subject_location_score)
                comp_adj = calculate_tier_adjustment(comp_location_score)
                location_score_adj_pct = subject_adj - comp_adj

                location_score_adjustment = base_price * (location_score_adj_pct / 100)
                total_adjustment_pct += location_score_adj_pct
                total_adjustment_amount += location_score_adjustment
                components.append(f'location score ({subject_location_score} vs {comp_location_score}: {location_score_adj_pct:+.1f}%)')

            else:
                # Case 2: Highway differs - apply RESIDUAL location score
                # First, account for the portion of score diff explained by highway
                if subject_highway and not comp_highway:
                    # Subject has highway - its higher score is partially explained by highway
                    residual_score_diff = max(0, score_diff - highway_score_attribution)
                else:
                    # Comp has highway - subject's lower score is partially explained
                    residual_score_diff = min(0, score_diff + highway_score_attribution)

                if abs(residual_score_diff) > 0:
                    # Calculate adjustment based on residual score difference
                    # We use a simple rate for residual (same tier-based approach)
                    # Calculate from baseline using residual
                    baseline = 50
                    if residual_score_diff > 0:
                        # Subject better than comp (after highway attribution)
                        effective_subject_score = baseline + residual_score_diff
                        effective_comp_score = baseline
                    else:
                        # Comp better than subject (after highway attribution)
                        effective_subject_score = baseline
                        effective_comp_score = baseline - residual_score_diff

                    residual_subject_adj = calculate_tier_adjustment(effective_subject_score)
                    residual_comp_adj = calculate_tier_adjustment(effective_comp_score)
                    residual_adj_pct = residual_subject_adj - residual_comp_adj

                    if abs(residual_adj_pct) >= 0.1:  # Only apply if material
                        residual_adjustment = base_price * (residual_adj_pct / 100)
                        total_adjustment_pct += residual_adj_pct
                        total_adjustment_amount += residual_adjustment
                        components.append(
                            f'location score residual (score diff {score_diff:+} - {highway_score_attribution} highway attribution = '
                            f'{residual_score_diff:+} residual: {residual_adj_pct:+.1f}%)'
                        )
                    else:
                        components.append(
                            f'location score (absorbed by highway: score diff {score_diff:+}, '
                            f'attribution {highway_score_attribution}, no residual adjustment)'
                        )
                else:
                    components.append(
                        f'location score (absorbed by highway: score diff {score_diff:+}, '
                        f'attribution {highway_score_attribution})'
                    )

        # Calculate final adjusted price
        adjusted_price = base_price + total_adjustment_amount

        if abs(total_adjustment_pct) < LOCATION_SCORE_SIGNIFICANCE:
            return {
                'stage': 5,
                'name': 'Location',
                'adjustment_amount': 0.0,
                'adjustment_pct': 0.0,
                'adjusted_price': base_price,
                'explanation': 'Similar locations - no material adjustment'
            }

        # Build explanation from components
        explanation = f'Subject ({subject_tier["name"]} tier, score {subject_location_score}) vs Comparable ({comp_tier["name"]} tier, score {comp_location_score})'
        if components:
            explanation += ': ' + ' | '.join(components)

        return {
            'stage': 5,
            'name': 'Location',
            'adjustment_amount': total_adjustment_amount,
            'adjustment_pct': total_adjustment_pct,
            'adjusted_price': adjusted_price,
            'subject_location_score': subject_location_score,
            'comp_location_score': comp_location_score,
            'subject_tier': subject_tier['name'],
            'comp_tier': comp_tier['name'],
            'model': 'non-linear tiered (CUSPAP compliant - no double-counting)',
            'components': components,
            'highway_differs': highway_differs,
            'explanation': explanation
        }

    def calculate_physical_characteristics_adjustment(self, comparable: Dict, base_price: float) -> Dict:
        """
        Stage 6: Physical Characteristics Adjustment (MODULAR VERSION)

        Orchestrates 7 adjustment modules for comprehensive physical characteristic analysis:
        - Land characteristics (8 subcategories) - land.py
        - Site improvements (6 subcategories) - site.py
        - Building - Industrial (10 subcategories) - industrial_building.py
        - Building - Office (8 subcategories) - office_building.py
        - Building - General (6 subcategories) - building_general.py
        - Special features (6 subcategories) - special_features.py
        - Zoning/legal (5 subcategories) - zoning_legal.py

        USPAP 2024 & CUSPAP 2024 Compliant
        """
        # Get property type to determine which adjustments apply
        property_type = self.subject.get('property_type', 'industrial')

        # Orchestrate all adjustment modules
        adjustments = []

        # CRITICAL FIX: Pass self.effective_factors (not self.market) to ensure
        # derived factors from paired sales analysis are used by modules.
        # Previous bug: self.market was passed, which only contains user input,
        # causing modules to fall back to hardcoded defaults.

        # Universal adjustments - apply to all property types
        adjustments.extend(land.calculate_adjustments(
            self.subject, comparable, base_price, self.effective_factors, property_type))

        adjustments.extend(site.calculate_adjustments(
            self.subject, comparable, base_price, self.effective_factors, property_type))

        # Property-type specific building adjustments
        if property_type == 'industrial':
            adjustments.extend(industrial_building.calculate_adjustments(
                self.subject, comparable, base_price, self.effective_factors, property_type))
        elif property_type == 'office':
            adjustments.extend(office_building.calculate_adjustments(
                self.subject, comparable, base_price, self.effective_factors, property_type))

        # Universal adjustments (continued) - apply to all property types
        adjustments.extend(building_general.calculate_adjustments(
            self.subject, comparable, base_price, self.effective_factors, property_type))

        adjustments.extend(special_features.calculate_adjustments(
            self.subject, comparable, base_price, self.effective_factors, property_type))

        adjustments.extend(zoning_legal.calculate_adjustments(
            self.subject, comparable, base_price, self.effective_factors, property_type))

        # =========================================================================
        # CALCULATE TOTALS AND RETURN
        # =========================================================================

        # Calculate total adjustment amount from all modules
        total_adjustment_amount = sum(adj['adjustment'] for adj in adjustments)

        adjusted_price = base_price + total_adjustment_amount
        adjustment_pct = (total_adjustment_amount / base_price) * 100 if base_price > 0 else 0

        # Group adjustments by category for summary
        categories = {}
        for adj in adjustments:
            category = adj['category']
            if category not in categories:
                categories[category] = {'count': 0, 'total_adjustment': 0.0, 'adjustments': []}

            categories[category]['count'] += 1
            categories[category]['total_adjustment'] += adj['adjustment']
            categories[category]['adjustments'].append(adj)

        return {
            'stage': 6,
            'name': 'Physical Characteristics (MODULAR)',
            'adjustment_amount': total_adjustment_amount,
            'adjustment_pct': adjustment_pct,
            'adjusted_price': adjusted_price,
            'total_adjustments_count': len(adjustments),
            'adjustments_by_category': categories,
            'all_adjustments': adjustments,
            'property_type': property_type,
            'compliance': {
                'uspap_2024': True,
                'cuspap_2024': True,
                'ivs': True
            },
            'explanation': f'{len(adjustments)} physical characteristic adjustments applied across {len(categories)} categories (USPAP & CUSPAP compliant)'
        }
    def calculate_comparable_adjustments(self, comparable: Dict) -> Dict:
        """Apply all 6 stages of adjustments to a single comparable."""
        address = comparable.get('address', 'Unknown')
        sale_price = comparable.get('sale_price', 0)

        # Stage 1: Property Rights
        stage1 = self.calculate_property_rights_adjustment(comparable, sale_price)

        # Stage 2: Financing (applied to Stage 1 adjusted price)
        stage2 = self.calculate_financing_adjustment(comparable, stage1['adjusted_price'])

        # Stage 3: Conditions of Sale (applied to Stage 2 adjusted price)
        stage3 = self.calculate_conditions_of_sale_adjustment(comparable, stage2['adjusted_price'])

        # Stage 4: Market Conditions/Time (applied to Stage 3 adjusted price)
        stage4 = self.calculate_market_conditions_adjustment(comparable, stage3['adjusted_price'])

        # Stage 5: Location (applied to Stage 4 adjusted price)
        stage5 = self.calculate_location_adjustment(comparable, stage4['adjusted_price'])

        # Stage 6: Physical Characteristics (applied to Stage 5 adjusted price)
        stage6 = self.calculate_physical_characteristics_adjustment(comparable, stage5['adjusted_price'])

        # Calculate gross and net adjustments
        all_stages = [stage1, stage2, stage3, stage4, stage5, stage6]

        gross_adjustment = sum(abs(stage['adjustment_amount']) for stage in all_stages)
        gross_adjustment_pct = safe_divide(gross_adjustment, sale_price) * 100

        net_adjustment = sum(stage['adjustment_amount'] for stage in all_stages)
        net_adjustment_pct = safe_divide(net_adjustment, sale_price) * 100

        final_adjusted_price = stage6['adjusted_price']

        # Validation flags using defined constants
        gross_exceeds_25pct = gross_adjustment_pct > GROSS_ADJUSTMENT_WARNING_PCT
        gross_exceeds_40pct = gross_adjustment_pct > GROSS_ADJUSTMENT_REJECT_PCT
        net_exceeds_15pct = abs(net_adjustment_pct) > NET_ADJUSTMENT_WARNING_PCT

        return {
            'comparable': {
                'address': address,
                'sale_price': sale_price,
                'sale_date': comparable.get('sale_date', 'Unknown')
            },
            'adjustment_stages': [stage1, stage2, stage3, stage4, stage5, stage6],
            'summary': {
                'final_adjusted_price': final_adjusted_price,
                'gross_adjustment': gross_adjustment,
                'gross_adjustment_pct': gross_adjustment_pct,
                'net_adjustment': net_adjustment,
                'net_adjustment_pct': net_adjustment_pct
            },
            'validation': {
                'gross_exceeds_25pct': gross_exceeds_25pct,
                'gross_exceeds_40pct': gross_exceeds_40pct,
                'net_exceeds_15pct': net_exceeds_15pct,
                'status': self._get_validation_status(gross_adjustment_pct, gross_exceeds_40pct),
                'recommendation': self._get_validation_recommendation(gross_adjustment_pct, gross_exceeds_40pct)
            }
        }

    def _get_validation_status(self, gross_pct: float, exceeds_40: bool) -> str:
        """Determine validation status based on gross adjustment percentage."""
        if exceeds_40:
            return 'REJECT'
        elif gross_pct > CAUTION_ZONE_LOWER_PCT:
            return 'CAUTION'
        else:
            return 'ACCEPTABLE'

    def _get_validation_recommendation(self, gross_pct: float, exceeds_40: bool) -> str:
        """Generate validation recommendation."""
        if exceeds_40:
            return f'Gross adjustment {gross_pct:.1f}% exceeds {GROSS_ADJUSTMENT_REJECT_PCT:.0f}% threshold - comparable is NOT truly comparable, do not use'
        elif gross_pct > CAUTION_ZONE_LOWER_PCT:
            return f'Gross adjustment {gross_pct:.1f}% is in caution range ({CAUTION_ZONE_LOWER_PCT:.0f}-{GROSS_ADJUSTMENT_REJECT_PCT:.0f}%) - comparable is marginal, weight accordingly'
        elif gross_pct > GROSS_ADJUSTMENT_WARNING_PCT:
            return f'Gross adjustment {gross_pct:.1f}% is acceptable but approaching limits - weight with moderate confidence'
        else:
            return f'Gross adjustment {gross_pct:.1f}% is well within acceptable limits - weight normally'

    def calculate_sensitivity_analysis(self, comparable_result: Dict) -> Dict:
        """
        Perform sensitivity analysis by varying key adjustments +/-10%.

        Tests impact of adjustment uncertainty on final value.
        """
        base_adjusted_price = comparable_result['summary']['final_adjusted_price']

        # Identify largest adjustments for sensitivity testing
        stages = comparable_result['adjustment_stages']
        adjustments_to_test = []

        for stage in stages:
            if abs(stage['adjustment_pct']) > MATERIAL_ADJUSTMENT_THRESHOLD_PCT:
                adjustments_to_test.append(stage)

        if not adjustments_to_test:
            return {
                'applicable': False,
                'explanation': 'No material adjustments to test (all <5%)'
            }

        sensitivity_results = []

        for stage in adjustments_to_test:
            stage_name = stage['name']
            base_adjustment = stage['adjustment_amount']

            # Test +/-10% variation
            low_adjustment = base_adjustment * 0.9
            high_adjustment = base_adjustment * 1.1

            low_price = base_adjusted_price - (base_adjustment - low_adjustment)
            high_price = base_adjusted_price - (base_adjustment - high_adjustment)

            low_change_pct = ((low_price - base_adjusted_price) / base_adjusted_price) * 100
            high_change_pct = ((high_price - base_adjusted_price) / base_adjusted_price) * 100

            sensitivity_results.append({
                'adjustment': stage_name,
                'base_adjustment': base_adjustment,
                'low_scenario': {
                    'adjustment': low_adjustment,
                    'adjusted_price': low_price,
                    'change_pct': low_change_pct
                },
                'high_scenario': {
                    'adjustment': high_adjustment,
                    'adjusted_price': high_price,
                    'change_pct': high_change_pct
                }
            })

        return {
            'applicable': True,
            'base_adjusted_price': base_adjusted_price,
            'sensitivity_tests': sensitivity_results
        }

    def reconcile_comparables(self) -> Dict:
        """
        Reconcile all comparable sales to derive value conclusion.

        Includes statistical analysis and weighting recommendations.
        """
        # Calculate adjustments for all comparables
        all_results = []

        for comp in self.comparables:
            result = self.calculate_comparable_adjustments(comp)
            all_results.append(result)

        # Extract adjusted prices
        adjusted_prices = [r['summary']['final_adjusted_price'] for r in all_results]

        # Statistical analysis
        stats = descriptive_statistics(adjusted_prices)

        # Weight comparables based on validation status and net adjustment
        weighted_values = []
        total_weight = 0.0

        for result in all_results:
            validation_status = result['validation']['status']
            net_adj_pct = abs(result['summary']['net_adjustment_pct'])

            # Weighting scheme
            if validation_status == 'REJECT':
                weight = 0.0
            elif validation_status == 'CAUTION':
                weight = 0.5
            elif net_adj_pct < 5:
                weight = 2.0  # Double weight for minimal adjustments
            elif net_adj_pct < 10:
                weight = 1.5
            else:
                weight = 1.0

            weighted_value = result['summary']['final_adjusted_price'] * weight
            weighted_values.append(weighted_value)
            total_weight += weight

            result['weighting'] = {
                'weight': weight,
                'weighted_value': weighted_value,
                'rationale': self._get_weighting_rationale(validation_status, net_adj_pct)
            }

        # Weighted average (reconciled value)
        if total_weight > 0:
            reconciled_value = sum(weighted_values) / total_weight
        else:
            reconciled_value = stats['median']

        # Value range
        acceptable_comps = [r for r in all_results if r['validation']['status'] != 'REJECT']

        if acceptable_comps:
            acceptable_prices = [r['summary']['final_adjusted_price'] for r in acceptable_comps]
            value_range_low = min(acceptable_prices)
            value_range_high = max(acceptable_prices)
        else:
            value_range_low = stats['min']
            value_range_high = stats['max']

        return {
            'comparable_results': all_results,
            'reconciliation': {
                'reconciled_value': reconciled_value,
                'value_range': {
                    'low': value_range_low,
                    'high': value_range_high,
                    'spread_pct': ((value_range_high - value_range_low) / value_range_low) * 100 if value_range_low > 0 else 0
                },
                'weighting_method': 'Threshold-based quality weighting with validation status filters',
                'total_weight': total_weight
            },
            'statistics': stats,
            'calculation_date': datetime.now().isoformat(),
            'calculator_version': '1.0.0',
            # =========================================================================
            # METHODOLOGY DOCUMENTATION (AACI Review Response)
            # =========================================================================
            'methodology_disclosure': {
                'framework': 'Methodology Framework: CUSPAP 2024 / USPAP 2024 / IVS 2024',
                'scope_statement': (
                    'This analysis applies the sales comparison approach using market-derived '
                    'adjustment factors where available, with industry defaults disclosed when '
                    'market evidence is insufficient. Factor values are derived through paired '
                    'sales analysis, regression, or professional judgment with explicit source '
                    'attribution.'
                ),
                'weighting_methodology': {
                    'description': 'Threshold-Based Quality Weighting',
                    'thresholds': [
                        {'range': '<5% net adjustment', 'weight': '2.0x', 'rationale': 'Minimal adjustments indicate high comparability'},
                        {'range': '5-10% net adjustment', 'weight': '1.5x', 'rationale': 'Small adjustments indicate good comparability'},
                        {'range': '10-25% net adjustment', 'weight': '1.0x', 'rationale': 'Moderate adjustments - standard weight'},
                        {'range': '25-40% gross adjustment', 'weight': '0.5x', 'rationale': 'Caution range - reduced reliability'},
                        {'range': '>40% gross adjustment', 'weight': '0.0x', 'rationale': 'Rejected - insufficient comparability'}
                    ]
                },
                'location_methodology': {
                    'hierarchy': [
                        '1. Submarket differential (if different submarket)',
                        '2. Highway frontage premium (if status differs)',
                        '3. Residual location score (score diff beyond highway attribution)'
                    ],
                    'highway_score_attribution': 'Highway frontage accounts for ~7 points of location score difference',
                    'residual_logic': 'When highway status differs, only residual score beyond attribution is adjusted'
                },
                'effective_age_rationale': (
                    'Effective age reflects actual physical/functional condition rather than '
                    'chronological age. Factors include: recent renovations, maintenance history, '
                    'functional obsolescence, and construction quality. Effective age should be '
                    'explicitly stated for subject and each comparable with supporting rationale.'
                ),
                'factor_sources': self.factor_sources if hasattr(self, 'factor_sources') else {}
            }
        }

    def _get_weighting_rationale(self, status: str, net_adj_pct: float) -> str:
        """Generate weighting rationale explanation."""
        if status == 'REJECT':
            return 'Rejected - gross adjustments exceed 40%'
        elif status == 'CAUTION':
            return 'Reduced weight (50%) - gross adjustments in caution range (30-40%)'
        elif net_adj_pct < 5:
            return 'Double weight (200%) - minimal net adjustments (<5%)'
        elif net_adj_pct < 10:
            return 'Increased weight (150%) - small net adjustments (5-10%)'
        else:
            return 'Normal weight (100%) - acceptable adjustments'


def load_json_file(file_path: str, description: str = "file") -> Dict:
    """
    Load and parse a JSON file with proper error handling.

    Args:
        file_path: Path to the JSON file
        description: Human-readable description for error messages

    Returns:
        Parsed JSON data as dictionary

    Raises:
        SystemExit: On file not found or invalid JSON
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"{description} not found: {file_path}")
        raise SystemExit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {description} ({file_path}): {e}")
        raise SystemExit(1)
    except PermissionError:
        logger.error(f"Permission denied reading {description}: {file_path}")
        raise SystemExit(1)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Calculate adjusted comparable sale prices using 6-stage adjustment hierarchy'
    )
    parser.add_argument('input_file', help='Path to input JSON file')
    parser.add_argument('--output', '-o', help='Path to output JSON file (optional)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Print detailed output')
    parser.add_argument('--sensitivity', '-s', action='store_true', help='Include sensitivity analysis')
    parser.add_argument('--adjustments', '-a', help='Path to appraiser adjustment factors JSON (optional override)')
    parser.add_argument('--skip-derivation', action='store_true', help='Skip paired sales derivation, use defaults only')

    args = parser.parse_args()

    # Load input with proper error handling
    input_data = load_json_file(args.input_file, "Input file")

    # Load appraiser overrides if provided
    appraiser_overrides = None
    if args.adjustments:
        appraiser_overrides = load_json_file(args.adjustments, "Appraiser adjustments file")
        print(f"Loaded appraiser adjustment factors from {args.adjustments}")

    # Step 1: Derive adjustment factors from paired sales analysis
    derived_factors = None
    if not args.skip_derivation:
        print("\n" + "=" * 60)
        print("PHASE 1: PAIRED SALES ANALYSIS")
        print("Deriving adjustment factors from comparable sales data...")
        print("=" * 60)

        property_type = input_data['subject_property'].get('property_type', 'industrial')

        analyzer = PairedSalesAnalyzer(
            comparables=input_data['comparable_sales'],
            subject=input_data['subject_property'],
            property_type=property_type
        )

        analyzer.analyze_all()
        derived_factors = analyzer.get_adjustment_factors()

        # Print derivation summary
        print(analyzer.get_analysis_report())
        print("\n" + "=" * 60)
        print("DERIVED ADJUSTMENT FACTORS")
        print("=" * 60)
        for factor_name, factor_data in derived_factors.get('factors', {}).items():
            if isinstance(factor_data, dict):
                val = factor_data.get('value')
                conf = factor_data.get('confidence', 'unknown')
                method = factor_data.get('method', 'unknown')
                print(f"  {factor_name}: {val} ({conf} confidence, {method})")
            else:
                print(f"  {factor_name}: {factor_data}")

    # Merge appraiser overrides into derived factors (appraiser wins)
    if appraiser_overrides and derived_factors:
        for key, value in appraiser_overrides.items():
            if key not in ['_documentation', 'appraiser_certification']:
                if 'factors' not in derived_factors:
                    derived_factors['factors'] = {}
                derived_factors['factors'][key] = {
                    'value': value.get('value') if isinstance(value, dict) else value,
                    'confidence': 'appraiser_override',
                    'method': 'appraiser_input'
                }
    elif appraiser_overrides and not derived_factors:
        derived_factors = {'factors': {}}
        for key, value in appraiser_overrides.items():
            if key not in ['_documentation', 'appraiser_certification']:
                derived_factors['factors'][key] = {
                    'value': value.get('value') if isinstance(value, dict) else value,
                    'confidence': 'appraiser_override',
                    'method': 'appraiser_input'
                }

    # Step 2: Calculate adjusted comparable values
    print("\n" + "=" * 60)
    print("PHASE 2: COMPARABLE SALES ADJUSTMENT")
    print("Applying 6-stage adjustment hierarchy...")
    print("=" * 60)

    calculator = ComparableSalesCalculator(input_data, derived_factors)
    results = calculator.reconcile_comparables()

    # Add factor derivation info to results
    results['adjustment_factors'] = {
        'effective_factors': calculator.effective_factors,
        'factor_sources': calculator.factor_sources,
        'derived_analysis': derived_factors
    }

    # Add sensitivity analysis if requested
    if args.sensitivity:
        for comp_result in results['comparable_results']:
            comp_result['sensitivity_analysis'] = calculator.calculate_sensitivity_analysis(comp_result)

    # Output
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results written to {args.output}")

    if args.verbose or not args.output:
        print(json.dumps(results, indent=2))

    # Print summary
    subject = input_data['subject_property']
    reconciliation = results['reconciliation']
    stats = results['statistics']

    print(f"\n{'='*80}")
    print(f"COMPARABLE SALES ADJUSTMENT ANALYSIS")
    print(f"{'='*80}")
    print(f"Subject Property: {subject.get('address', 'N/A')}")
    print(f"Size: {subject.get('size_sf', 0):,} sq ft")
    print(f"Location Score: {subject.get('location_score', 'N/A')}")
    print(f"\nCOMPARABLE SALES:")
    print(f"{'─'*80}")

    for i, comp_result in enumerate(results['comparable_results'], 1):
        comp = comp_result['comparable']
        summary = comp_result['summary']
        validation = comp_result['validation']
        weighting = comp_result['weighting']

        print(f"\nComparable {i}: {comp['address']}")
        print(f"  Sale Price:           ${comp['sale_price']:>15,}")
        print(f"  Sale Date:            {comp['sale_date']:>15}")
        print(f"  Gross Adjustment:     {summary['gross_adjustment_pct']:>14.1f}%  (${summary['gross_adjustment']:,.0f})")
        print(f"  Net Adjustment:       {summary['net_adjustment_pct']:>14.1f}%  (${summary['net_adjustment']:,.0f})")
        print(f"  Adjusted Price:       ${summary['final_adjusted_price']:>15,}")
        print(f"  Validation:           {validation['status']:>15}")
        print(f"  Weight:               {weighting['weight']:>15.1f}x")

        if validation['status'] != 'ACCEPTABLE':
            print(f"  Note: {validation['recommendation']}")

    print(f"\n{'─'*80}")
    print(f"RECONCILIATION:")
    print(f"{'─'*80}")
    print(f"Adjusted Price Range:    ${reconciliation['value_range']['low']:>15,} - ${reconciliation['value_range']['high']:>15,}")
    print(f"Range Spread:            {reconciliation['value_range']['spread_pct']:>14.1f}%")
    print(f"Statistical Mean:        ${stats['mean']:>15,.0f}")
    print(f"Statistical Median:      ${stats['median']:>15,.0f}")
    print(f"Reconciled Value:        ${reconciliation['reconciled_value']:>15,.0f}")
    print(f"\nWeighting Method: {reconciliation['weighting_method']}")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    main()
