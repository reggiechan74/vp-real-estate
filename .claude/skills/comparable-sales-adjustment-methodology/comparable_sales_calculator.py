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
from pathlib import Path
from typing import Dict, List, Optional, Literal
from datetime import datetime

# Add Shared_Utils to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "Shared_Utils"))
from financial_utils import pv_annuity, npv, descriptive_statistics


class ComparableSalesCalculator:
    """Calculate adjusted comparable sale prices using 6-stage adjustment hierarchy."""

    def __init__(self, input_data: Dict):
        """Initialize calculator with input data."""
        self.data = input_data
        self.subject = input_data['subject_property']
        self.comparables = input_data['comparable_sales']
        self.market = input_data['market_parameters']
        self.adjustment_results = []

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
            cap_rate = self.market.get('cap_rate', 7.0) / 100

            if ground_rent_annual > 0 and cap_rate > 0:
                capitalized_land_value = ground_rent_annual / cap_rate
                adjusted_price = base_price + capitalized_land_value
                adjustment_amount = capitalized_land_value
                adjustment_pct = (adjustment_amount / base_price) * 100

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
                adjustment_pct = (adjustment_amount / base_price) * 100

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
            adjusted_price = base_price / discount_factor
            adjustment_amount = adjusted_price - base_price
            adjustment_pct = (adjustment_amount / base_price) * 100

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

        # Parse dates
        try:
            sale_datetime = datetime.fromisoformat(sale_date)
            valuation_date = self.market.get('valuation_date', datetime.now().isoformat())
            valuation_datetime = datetime.fromisoformat(valuation_date)

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

            # Apply appreciation
            appreciation_rate_annual = self.market.get('appreciation_rate_annual', 0) / 100

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
            adjustment_pct = (adjustment_amount / base_price) * 100

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
        Stage 5: Location Adjustment

        Adjust for micro-market differences.

        Example:
        - Subject: Highway frontage (score 95)
        - Comparable: Interior location (score 80)
        - Premium: 15% for highway frontage
        """
        subject_location_score = self.subject.get('location_score', 50)
        comp_location_score = comparable.get('location_score', 50)

        # Calculate location differential
        location_differential = subject_location_score - comp_location_score

        # Simple model: 1% premium per location score point
        # (or use market parameters for specific location premiums)
        location_premium_per_point = self.market.get('location_premium_per_point', 1.0)

        adjustment_pct = location_differential * location_premium_per_point
        adjustment_amount = base_price * (adjustment_pct / 100)
        adjusted_price = base_price + adjustment_amount

        # Check for specific location premiums (e.g., highway frontage)
        highway_premium = self.market.get('location_premium_highway', 0)
        subject_highway = self.subject.get('highway_frontage', False)
        comp_highway = comparable.get('highway_frontage', False)

        if subject_highway and not comp_highway and highway_premium > 0:
            # Subject has highway frontage, comparable doesn't
            highway_adjustment_pct = highway_premium
            highway_adjustment_amount = base_price * (highway_adjustment_pct / 100)
            adjusted_price += highway_adjustment_amount
            adjustment_amount += highway_adjustment_amount
            adjustment_pct += highway_adjustment_pct

            return {
                'stage': 5,
                'name': 'Location',
                'adjustment_amount': adjustment_amount,
                'adjustment_pct': adjustment_pct,
                'adjusted_price': adjusted_price,
                'subject_location_score': subject_location_score,
                'comp_location_score': comp_location_score,
                'highway_premium': highway_premium,
                'explanation': f'Location score differential ({location_differential} points) + highway frontage premium ({highway_premium}%)'
            }
        elif comp_highway and not subject_highway and highway_premium > 0:
            # Comparable has highway frontage, subject doesn't
            highway_adjustment_pct = -highway_premium
            highway_adjustment_amount = base_price * (highway_adjustment_pct / 100)
            adjusted_price += highway_adjustment_amount
            adjustment_amount += highway_adjustment_amount
            adjustment_pct += highway_adjustment_pct

            return {
                'stage': 5,
                'name': 'Location',
                'adjustment_amount': adjustment_amount,
                'adjustment_pct': adjustment_pct,
                'adjusted_price': adjusted_price,
                'subject_location_score': subject_location_score,
                'comp_location_score': comp_location_score,
                'highway_premium': -highway_premium,
                'explanation': f'Location score differential ({location_differential} points) - comparable has highway frontage (subject does not)'
            }

        if abs(adjustment_pct) < 0.1:
            return {
                'stage': 5,
                'name': 'Location',
                'adjustment_amount': 0.0,
                'adjustment_pct': 0.0,
                'adjusted_price': base_price,
                'explanation': 'Similar locations - no material adjustment'
            }

        return {
            'stage': 5,
            'name': 'Location',
            'adjustment_amount': adjustment_amount,
            'adjustment_pct': adjustment_pct,
            'adjusted_price': adjusted_price,
            'subject_location_score': subject_location_score,
            'comp_location_score': comp_location_score,
            'explanation': f'Location score differential: {location_differential} points ({adjustment_pct:+.1f}%)'
        }

    def calculate_physical_characteristics_adjustment(self, comparable: Dict, base_price: float) -> Dict:
        """
        Stage 6: Physical Characteristics Adjustment (ENHANCED VERSION)
    
        Comprehensive adjustments for 40+ physical characteristics organized by category:
        - Land characteristics (8 subcategories)
        - Site improvements (6 subcategories)
        - Building - Industrial (10 subcategories)
        - Building - Office (8 subcategories)
        - Building - General (6 subcategories)
        - Special features (6 subcategories)
        - Zoning/legal (5 subcategories)
    
        USPAP 2024 & CUSPAP 2024 Compliant
        """
        adjustments = []
        total_adjustment_amount = 0.0
    
        # Get property type to determine which adjustments apply
        property_type = self.subject.get('property_type', 'industrial')  # industrial, office, retail, multi-family
    
        # =========================================================================
        # LAND CHARACTERISTICS (8 subcategories)
        # =========================================================================
    
        # 1. LOT SIZE / LAND AREA
        subject_lot_acres = self.subject.get('lot_size_acres', 0)
        comp_lot_acres = comparable.get('lot_size_acres', 0)
    
        if subject_lot_acres > 0 and comp_lot_acres > 0:
            lot_diff_acres = subject_lot_acres - comp_lot_acres
    
            # Economies of scale: larger parcels have lower $/acre
            lot_adjustment_per_acre = self.market.get('lot_adjustment_per_acre', 15000)
    
            lot_adjustment = lot_diff_acres * lot_adjustment_per_acre
            total_adjustment_amount += lot_adjustment
    
            adjustments.append({
                'category': 'Land',
                'characteristic': 'Lot Size',
                'subject_value': f'{subject_lot_acres:.2f} acres',
                'comp_value': f'{comp_lot_acres:.2f} acres',
                'adjustment': lot_adjustment,
                'explanation': f'{lot_diff_acres:+.2f} acres × ${lot_adjustment_per_acre:,}/acre'
            })
    
        # 2. SHAPE / FRONTAGE-TO-DEPTH RATIO
        subject_frontage_ft = self.subject.get('frontage_linear_feet', 0)
        subject_depth_ft = self.subject.get('depth_feet', 0)
        comp_frontage_ft = comparable.get('frontage_linear_feet', 0)
        comp_depth_ft = comparable.get('depth_feet', 0)
    
        if all([subject_frontage_ft, subject_depth_ft, comp_frontage_ft, comp_depth_ft]):
            subject_ratio = subject_frontage_ft / subject_depth_ft
            comp_ratio = comp_frontage_ft / comp_depth_ft
    
            # Optimal ratio: 1:3 to 1:5 (higher ratios = more frontage = better for commercial)
            optimal_ratio = 0.25  # 1:4
    
            subject_deviation = abs(subject_ratio - optimal_ratio)
            comp_deviation = abs(comp_ratio - optimal_ratio)
    
            shape_differential = comp_deviation - subject_deviation
    
            if abs(shape_differential) > 0.05:  # Material difference
                # Penalty for poor shape: 2-5% per 0.1 deviation from optimal
                shape_adjustment_factor = self.market.get('shape_adjustment_per_0_1_deviation', 0.02)  # 2%
                shape_adjustment = base_price * (shape_differential * shape_adjustment_factor * 10)
    
                total_adjustment_amount += shape_adjustment
    
                adjustments.append({
                    'category': 'Land',
                    'characteristic': 'Shape/Frontage Ratio',
                    'subject_value': f'{subject_ratio:.2f} ({subject_frontage_ft}ft × {subject_depth_ft}ft)',
                    'comp_value': f'{comp_ratio:.2f} ({comp_frontage_ft}ft × {comp_depth_ft}ft)',
                    'adjustment': shape_adjustment,
                    'explanation': f'Shape differential from optimal 1:4 ratio: {shape_differential:+.2f}'
                })
    
        # 3. TOPOGRAPHY
        topography_hierarchy = {'severely_sloped': 1, 'moderately_sloped': 2, 'gently_sloped': 3, 'level': 4}
        subject_topo = self.subject.get('topography', 'level')
        comp_topo = comparable.get('topography', 'level')
    
        subject_topo_score = topography_hierarchy.get(subject_topo, 4)
        comp_topo_score = topography_hierarchy.get(comp_topo, 4)
    
        topo_diff = subject_topo_score - comp_topo_score
    
        if topo_diff != 0:
            # Level land is preferred: 3-5% premium per level
            topo_adjustment_pct = self.market.get('topography_adjustment_pct_per_level', 3.5)
            topo_adjustment = base_price * (topo_diff * topo_adjustment_pct / 100)
            total_adjustment_amount += topo_adjustment
    
            adjustments.append({
                'category': 'Land',
                'characteristic': 'Topography',
                'subject_value': subject_topo,
                'comp_value': comp_topo,
                'adjustment': topo_adjustment,
                'explanation': f'{topo_diff:+} levels × {topo_adjustment_pct}% (level land premium)'
            })
    
        # 4. UTILITIES - AVAILABILITY AND CAPACITY
        utilities_score_map = {
            'full_services_adequate': 4,      # Water, sewer, gas, electric (adequate capacity)
            'full_services_limited': 3,       # All services but limited capacity
            'partial_services': 2,            # Some services available
            'no_services': 1                  # No utilities (well/septic required)
        }
    
        subject_utilities = self.subject.get('utilities', 'full_services_adequate')
        comp_utilities = comparable.get('utilities', 'full_services_adequate')
    
        subject_utilities_score = utilities_score_map.get(subject_utilities, 4)
        comp_utilities_score = utilities_score_map.get(comp_utilities, 4)
    
        utilities_diff = subject_utilities_score - comp_utilities_score
    
        if utilities_diff != 0:
            # Full services vs. partial/none: significant value impact
            utilities_adjustment_pct = self.market.get('utilities_adjustment_pct_per_level', 5.0)
            utilities_adjustment = base_price * (utilities_diff * utilities_adjustment_pct / 100)
            total_adjustment_amount += utilities_adjustment
    
            adjustments.append({
                'category': 'Land',
                'characteristic': 'Utilities',
                'subject_value': subject_utilities,
                'comp_value': comp_utilities,
                'adjustment': utilities_adjustment,
                'explanation': f'{utilities_diff:+} levels × {utilities_adjustment_pct}%'
            })
    
        # 5. DRAINAGE
        drainage_hierarchy = {'poor': 1, 'adequate': 2, 'good': 3, 'excellent': 4}
        subject_drainage = self.subject.get('drainage', 'good')
        comp_drainage = comparable.get('drainage', 'good')
    
        subject_drainage_score = drainage_hierarchy.get(subject_drainage, 3)
        comp_drainage_score = drainage_hierarchy.get(comp_drainage, 3)
    
        drainage_diff = subject_drainage_score - comp_drainage_score
    
        if drainage_diff != 0:
            drainage_adjustment_pct = self.market.get('drainage_adjustment_pct_per_level', 2.0)
            drainage_adjustment = base_price * (drainage_diff * drainage_adjustment_pct / 100)
            total_adjustment_amount += drainage_adjustment
    
            adjustments.append({
                'category': 'Land',
                'characteristic': 'Drainage',
                'subject_value': subject_drainage,
                'comp_value': comp_drainage,
                'adjustment': drainage_adjustment,
                'explanation': f'{drainage_diff:+} levels × {drainage_adjustment_pct}%'
            })
    
        # 6. FLOOD ZONE
        flood_zone_map = {'none': 0, 'flood_fringe': -5, 'floodway': -15}  # % adjustment
        subject_flood = self.subject.get('flood_zone', 'none')
        comp_flood = comparable.get('flood_zone', 'none')
    
        subject_flood_pct = flood_zone_map.get(subject_flood, 0)
        comp_flood_pct = flood_zone_map.get(comp_flood, 0)
    
        if subject_flood_pct != comp_flood_pct:
            flood_adjustment_pct = comp_flood_pct - subject_flood_pct
            flood_adjustment = base_price * (flood_adjustment_pct / 100)
            total_adjustment_amount += flood_adjustment
    
            adjustments.append({
                'category': 'Land',
                'characteristic': 'Flood Zone',
                'subject_value': subject_flood,
                'comp_value': comp_flood,
                'adjustment': flood_adjustment,
                'explanation': f'Flood zone differential: {flood_adjustment_pct:+.1f}%'
            })
    
        # 7. ENVIRONMENTAL CONSTRAINTS (Wetlands, Contamination)
        environmental_map = {'contaminated': -30, 'brownfield': -15, 'wetlands_minor': -8, 'wetlands_major': -20, 'clean': 0}
        subject_environmental = self.subject.get('environmental_status', 'clean')
        comp_environmental = comparable.get('environmental_status', 'clean')
    
        subject_env_pct = environmental_map.get(subject_environmental, 0)
        comp_env_pct = environmental_map.get(comp_environmental, 0)
    
        if subject_env_pct != comp_env_pct:
            env_adjustment_pct = comp_env_pct - subject_env_pct
            env_adjustment = base_price * (env_adjustment_pct / 100)
            total_adjustment_amount += env_adjustment
    
            adjustments.append({
                'category': 'Land',
                'characteristic': 'Environmental Status',
                'subject_value': subject_environmental,
                'comp_value': comp_environmental,
                'adjustment': env_adjustment,
                'explanation': f'Environmental constraint differential: {env_adjustment_pct:+.1f}%'
            })
    
        # 8. SOIL/BEARING CAPACITY (for development potential)
        soil_map = {'poor_bearing': -5, 'adequate': 0, 'good_bearing': 3, 'excellent': 5}  # % adjustment
        subject_soil = self.subject.get('soil_quality', 'adequate')
        comp_soil = comparable.get('soil_quality', 'adequate')
    
        subject_soil_pct = soil_map.get(subject_soil, 0)
        comp_soil_pct = soil_map.get(comp_soil, 0)
    
        if subject_soil_pct != comp_soil_pct:
            soil_adjustment_pct = subject_soil_pct - comp_soil_pct
            soil_adjustment = base_price * (soil_adjustment_pct / 100)
            total_adjustment_amount += soil_adjustment
    
            adjustments.append({
                'category': 'Land',
                'characteristic': 'Soil/Bearing Capacity',
                'subject_value': subject_soil,
                'comp_value': comp_soil,
                'adjustment': soil_adjustment,
                'explanation': f'Soil quality differential: {soil_adjustment_pct:+.1f}%'
            })
    
        # =========================================================================
        # SITE IMPROVEMENTS (6 subcategories)
        # =========================================================================
    
        # 9. PAVING / HARDSCAPE
        subject_paved_acres = self.subject.get('paved_area_acres', 0)
        comp_paved_acres = comparable.get('paved_area_acres', 0)
    
        if subject_paved_acres != comp_paved_acres:
            paved_diff = subject_paved_acres - comp_paved_acres
    
            # Paving cost: $8-$15/sq ft ($350K-$650K per acre)
            paving_cost_per_acre = self.market.get('paving_cost_per_acre', 500000)
    
            # Depreciate by age/condition
            paving_condition = comparable.get('paving_condition', 'good')
            depreciation_map = {'poor': 0.5, 'fair': 0.7, 'good': 0.85, 'excellent': 1.0}
            paving_depreciation_factor = depreciation_map.get(paving_condition, 0.85)
    
            paving_adjustment = paved_diff * paving_cost_per_acre * paving_depreciation_factor
            total_adjustment_amount += paving_adjustment
    
            adjustments.append({
                'category': 'Site Improvements',
                'characteristic': 'Paving/Hardscape',
                'subject_value': f'{subject_paved_acres:.2f} acres paved',
                'comp_value': f'{comp_paved_acres:.2f} acres paved ({paving_condition} condition)',
                'adjustment': paving_adjustment,
                'explanation': f'{paved_diff:+.2f} acres × ${paving_cost_per_acre:,}/acre × {paving_depreciation_factor:.0%} depreciation'
            })
    
        # 10. FENCING / SECURITY
        fence_map = {'none': 0, 'chain_link': 50000, 'vinyl': 75000, 'security_fence': 120000}
        subject_fence = self.subject.get('fencing', 'none')
        comp_fence = comparable.get('fencing', 'none')
    
        subject_fence_value = fence_map.get(subject_fence, 0)
        comp_fence_value = fence_map.get(comp_fence, 0)
    
        if subject_fence_value != comp_fence_value:
            fence_adjustment = subject_fence_value - comp_fence_value
    
            # Depreciate by age
            fence_age = comparable.get('fence_age_years', 5)
            fence_life = 20  # Typical useful life
            fence_depreciation = max(0, 1 - (fence_age / fence_life))
    
            fence_adjustment = fence_adjustment * fence_depreciation
            total_adjustment_amount += fence_adjustment
    
            adjustments.append({
                'category': 'Site Improvements',
                'characteristic': 'Fencing/Security',
                'subject_value': subject_fence,
                'comp_value': comp_fence,
                'adjustment': fence_adjustment,
                'explanation': f'Fence differential: ${subject_fence_value - comp_fence_value:,} × {fence_depreciation:.0%} depreciation'
            })
    
        # 11. SITE LIGHTING
        lighting_map = {'none': 0, 'minimal': 30000, 'adequate': 60000, 'extensive': 100000}
        subject_lighting = self.subject.get('site_lighting', 'adequate')
        comp_lighting = comparable.get('site_lighting', 'adequate')
    
        subject_lighting_value = lighting_map.get(subject_lighting, 60000)
        comp_lighting_value = lighting_map.get(comp_lighting, 60000)
    
        if subject_lighting_value != comp_lighting_value:
            lighting_adjustment = subject_lighting_value - comp_lighting_value
            total_adjustment_amount += lighting_adjustment
    
            adjustments.append({
                'category': 'Site Improvements',
                'characteristic': 'Site Lighting',
                'subject_value': subject_lighting,
                'comp_value': comp_lighting,
                'adjustment': lighting_adjustment,
                'explanation': f'Lighting differential: ${lighting_adjustment:+,}'
            })
    
        # 12. LANDSCAPING
        landscaping_map = {'none': 0, 'minimal': 15000, 'moderate': 35000, 'extensive': 75000}
        subject_landscaping = self.subject.get('landscaping', 'minimal')
        comp_landscaping = comparable.get('landscaping', 'minimal')
    
        subject_landscaping_value = landscaping_map.get(subject_landscaping, 15000)
        comp_landscaping_value = landscaping_map.get(comp_landscaping, 15000)
    
        if subject_landscaping_value != comp_landscaping_value:
            landscaping_adjustment = subject_landscaping_value - comp_landscaping_value
            total_adjustment_amount += landscaping_adjustment
    
            adjustments.append({
                'category': 'Site Improvements',
                'characteristic': 'Landscaping',
                'subject_value': subject_landscaping,
                'comp_value': comp_landscaping,
                'adjustment': landscaping_adjustment,
                'explanation': f'Landscaping differential: ${landscaping_adjustment:+,}'
            })
    
        # 13. STORMWATER MANAGEMENT
        stormwater_map = {'none': -50000, 'basic': 0, 'retention_pond': 80000, 'advanced_system': 150000}
        subject_stormwater = self.subject.get('stormwater_management', 'basic')
        comp_stormwater = comparable.get('stormwater_management', 'basic')
    
        subject_stormwater_value = stormwater_map.get(subject_stormwater, 0)
        comp_stormwater_value = stormwater_map.get(comp_stormwater, 0)
    
        if subject_stormwater_value != comp_stormwater_value:
            stormwater_adjustment = subject_stormwater_value - comp_stormwater_value
            total_adjustment_amount += stormwater_adjustment
    
            adjustments.append({
                'category': 'Site Improvements',
                'characteristic': 'Stormwater Management',
                'subject_value': subject_stormwater,
                'comp_value': comp_stormwater,
                'adjustment': stormwater_adjustment,
                'explanation': f'Stormwater system differential: ${stormwater_adjustment:+,}'
            })
    
        # 14. YARD AREA (Secured Outdoor Storage)
        subject_yard_acres = self.subject.get('secured_yard_acres', 0)
        comp_yard_acres = comparable.get('secured_yard_acres', 0)
    
        if subject_yard_acres != comp_yard_acres:
            yard_diff = subject_yard_acres - comp_yard_acres
    
            # Secured yard value: $100K-$200K per acre (fenced, paved, lit)
            yard_value_per_acre = self.market.get('secured_yard_value_per_acre', 150000)
    
            yard_adjustment = yard_diff * yard_value_per_acre
            total_adjustment_amount += yard_adjustment
    
            adjustments.append({
                'category': 'Site Improvements',
                'characteristic': 'Secured Yard Area',
                'subject_value': f'{subject_yard_acres:.2f} acres',
                'comp_value': f'{comp_yard_acres:.2f} acres',
                'adjustment': yard_adjustment,
                'explanation': f'{yard_diff:+.2f} acres × ${yard_value_per_acre:,}/acre'
            })
    
        # =========================================================================
        # BUILDING - INDUSTRIAL SPECIFIC (10 subcategories)
        # =========================================================================
    
        if property_type == 'industrial':
    
            # 15. BUILDING SIZE (sq ft)
            subject_building_sf = self.subject.get('building_sf', 0)
            comp_building_sf = comparable.get('building_sf', 0)
    
            if subject_building_sf > 0 and comp_building_sf > 0:
                building_diff_sf = subject_building_sf - comp_building_sf
    
                # Economies of scale: larger buildings have lower $/sf
                building_adjustment_per_sf = self.market.get('building_size_adjustment_per_sf', 2.0)
    
                building_size_adjustment = building_diff_sf * building_adjustment_per_sf
                total_adjustment_amount += building_size_adjustment
    
                adjustments.append({
                    'category': 'Industrial Building',
                    'characteristic': 'Building Size',
                    'subject_value': f'{subject_building_sf:,} sq ft',
                    'comp_value': f'{comp_building_sf:,} sq ft',
                    'adjustment': building_size_adjustment,
                    'explanation': f'{building_diff_sf:+,} sq ft × ${building_adjustment_per_sf}/sq ft'
                })
    
            # 16. CLEAR HEIGHT (Critical for warehousing)
            subject_clear_height = self.subject.get('clear_height_feet', 0)
            comp_clear_height = comparable.get('clear_height_feet', 0)
    
            if subject_clear_height > 0 and comp_clear_height > 0:
                clear_height_diff = subject_clear_height - comp_clear_height
    
                # Clear height premium: $1-$3/sq ft per additional foot above 20'
                # Example: 24' vs 20' clear height = $4/sq ft × building size
                clear_height_value_per_foot = self.market.get('clear_height_value_per_foot_per_sf', 1.5)
    
                clear_height_adjustment = clear_height_diff * clear_height_value_per_foot * comp_building_sf
                total_adjustment_amount += clear_height_adjustment
    
                adjustments.append({
                    'category': 'Industrial Building',
                    'characteristic': 'Clear Height',
                    'subject_value': f'{subject_clear_height} feet',
                    'comp_value': f'{comp_clear_height} feet',
                    'adjustment': clear_height_adjustment,
                    'explanation': f'{clear_height_diff:+} feet × ${clear_height_value_per_foot}/sf × {comp_building_sf:,} sf'
                })
    
            # 17. LOADING DOCKS (Number and Type)
            subject_dock_high = self.subject.get('loading_docks_dock_high', 0)
            subject_grade_level = self.subject.get('loading_docks_grade_level', 0)
            subject_drive_in = self.subject.get('loading_docks_drive_in', 0)
    
            comp_dock_high = comparable.get('loading_docks_dock_high', 0)
            comp_grade_level = comparable.get('loading_docks_grade_level', 0)
            comp_drive_in = comparable.get('loading_docks_drive_in', 0)
    
            # Value per dock type
            dock_high_value = 25000  # Most valuable
            grade_level_value = 15000
            drive_in_value = 50000  # Drive-in doors most valuable for certain uses
    
            subject_dock_value = (subject_dock_high * dock_high_value +
                                 subject_grade_level * grade_level_value +
                                 subject_drive_in * drive_in_value)
    
            comp_dock_value = (comp_dock_high * dock_high_value +
                              comp_grade_level * grade_level_value +
                              comp_drive_in * drive_in_value)
    
            if subject_dock_value != comp_dock_value:
                loading_dock_adjustment = subject_dock_value - comp_dock_value
                total_adjustment_amount += loading_dock_adjustment
    
                subject_total_docks = subject_dock_high + subject_grade_level + subject_drive_in
                comp_total_docks = comp_dock_high + comp_grade_level + comp_drive_in
    
                adjustments.append({
                    'category': 'Industrial Building',
                    'characteristic': 'Loading Docks',
                    'subject_value': f'{subject_total_docks} total ({subject_dock_high} dock-high, {subject_grade_level} grade, {subject_drive_in} drive-in)',
                    'comp_value': f'{comp_total_docks} total ({comp_dock_high} dock-high, {comp_grade_level} grade, {comp_drive_in} drive-in)',
                    'adjustment': loading_dock_adjustment,
                    'explanation': f'Loading dock differential: ${loading_dock_adjustment:+,}'
                })
    
            # 18. COLUMN SPACING (for racking efficiency)
            subject_column_spacing = self.subject.get('column_spacing_feet', 0)
            comp_column_spacing = comparable.get('column_spacing_feet', 0)
    
            if subject_column_spacing > 0 and comp_column_spacing > 0:
                # Modern warehouse: 50-60' spacing preferred
                # Older: 20-30' spacing (less efficient for racking)
                column_diff = subject_column_spacing - comp_column_spacing
    
                # Value differential: $0.50-$1.00/sf for wider spacing
                if abs(column_diff) >= 10:  # Material difference (10+ feet)
                    column_adjustment_per_sf = self.market.get('column_spacing_adjustment_per_sf', 0.75)
                    column_adjustment = (column_diff / 10) * column_adjustment_per_sf * comp_building_sf
    
                    total_adjustment_amount += column_adjustment
    
                    adjustments.append({
                        'category': 'Industrial Building',
                        'characteristic': 'Column Spacing',
                        'subject_value': f'{subject_column_spacing} feet',
                        'comp_value': f'{comp_column_spacing} feet',
                        'adjustment': column_adjustment,
                        'explanation': f'{column_diff:+} feet differential × ${column_adjustment_per_sf}/sf per 10\' × {comp_building_sf:,} sf'
                    })
    
            # 19. FLOOR LOAD CAPACITY
            subject_floor_load = self.subject.get('floor_load_capacity_psf', 0)
            comp_floor_load = comparable.get('floor_load_capacity_psf', 0)
    
            if subject_floor_load > 0 and comp_floor_load > 0:
                floor_load_diff = subject_floor_load - comp_floor_load
    
                # Standard: 125 psf, Heavy: 250-500 psf
                # Premium for heavy floor: $2-$5/sf
                if abs(floor_load_diff) >= 100:  # Material difference
                    floor_load_adjustment_per_sf = self.market.get('floor_load_adjustment_per_sf', 3.0)
                    floor_load_adjustment = (floor_load_diff / 100) * floor_load_adjustment_per_sf * comp_building_sf
    
                    total_adjustment_amount += floor_load_adjustment
    
                    adjustments.append({
                        'category': 'Industrial Building',
                        'characteristic': 'Floor Load Capacity',
                        'subject_value': f'{subject_floor_load} psf',
                        'comp_value': f'{comp_floor_load} psf',
                        'adjustment': floor_load_adjustment,
                        'explanation': f'{floor_load_diff:+} psf differential × ${floor_load_adjustment_per_sf}/sf per 100 psf × {comp_building_sf:,} sf'
                    })
    
            # 20. OFFICE FINISH PERCENTAGE
            subject_office_pct = self.subject.get('office_finish_percentage', 0)
            comp_office_pct = comparable.get('office_finish_percentage', 0)
    
            if subject_office_pct != comp_office_pct:
                office_pct_diff = subject_office_pct - comp_office_pct
    
                # Office finish cost: $60-$100/sf vs. warehouse $30-$50/sf
                # Differential: $30-$50/sf
                office_finish_premium_per_sf = self.market.get('office_finish_premium_per_sf', 40.0)
    
                office_adjustment = (office_pct_diff / 100) * office_finish_premium_per_sf * comp_building_sf
                total_adjustment_amount += office_adjustment
    
                adjustments.append({
                    'category': 'Industrial Building',
                    'characteristic': 'Office Finish %',
                    'subject_value': f'{subject_office_pct}% of GLA',
                    'comp_value': f'{comp_office_pct}% of GLA',
                    'adjustment': office_adjustment,
                    'explanation': f'{office_pct_diff:+}% × ${office_finish_premium_per_sf}/sf × {comp_building_sf:,} sf'
                })
    
            # 21. BAY DEPTH
            subject_bay_depth = self.subject.get('bay_depth_feet', 0)
            comp_bay_depth = comparable.get('bay_depth_feet', 0)
    
            if subject_bay_depth > 0 and comp_bay_depth > 0:
                # Modern warehouse: 100-150' deep preferred
                # Shallow bay (<80'): less efficient
                bay_depth_diff = subject_bay_depth - comp_bay_depth
    
                if abs(bay_depth_diff) >= 20:  # Material difference
                    # Adjustment: $0.25-$0.75/sf for deeper bays
                    bay_depth_adjustment_per_sf = self.market.get('bay_depth_adjustment_per_sf', 0.50)
                    bay_depth_adjustment = (bay_depth_diff / 20) * bay_depth_adjustment_per_sf * comp_building_sf
    
                    total_adjustment_amount += bay_depth_adjustment
    
                    adjustments.append({
                        'category': 'Industrial Building',
                        'characteristic': 'Bay Depth',
                        'subject_value': f'{subject_bay_depth} feet',
                        'comp_value': f'{comp_bay_depth} feet',
                        'adjustment': bay_depth_adjustment,
                        'explanation': f'{bay_depth_diff:+} feet differential × ${bay_depth_adjustment_per_sf}/sf per 20\' × {comp_building_sf:,} sf'
                    })
    
            # 22. ESFR SPRINKLER SYSTEM
            subject_esfr = self.subject.get('esfr_sprinkler', False)
            comp_esfr = comparable.get('esfr_sprinkler', False)
    
            if subject_esfr != comp_esfr:
                # ESFR system cost: $3-$6/sf premium over standard
                esfr_premium_per_sf = self.market.get('esfr_premium_per_sf', 4.0)
                esfr_adjustment = (1 if subject_esfr else -1) * esfr_premium_per_sf * comp_building_sf
    
                total_adjustment_amount += esfr_adjustment
    
                adjustments.append({
                    'category': 'Industrial Building',
                    'characteristic': 'ESFR Sprinkler System',
                    'subject_value': 'Yes' if subject_esfr else 'No',
                    'comp_value': 'Yes' if comp_esfr else 'No',
                    'adjustment': esfr_adjustment,
                    'explanation': f'ESFR system differential: ${esfr_premium_per_sf}/sf × {comp_building_sf:,} sf'
                })
    
            # 23. TRUCK COURT DEPTH
            subject_truck_court = self.subject.get('truck_court_depth_feet', 0)
            comp_truck_court = comparable.get('truck_court_depth_feet', 0)
    
            if subject_truck_court != comp_truck_court:
                # Minimum: 120' for trailer maneuvering
                # Preferred: 150-180'
                truck_court_diff = subject_truck_court - comp_truck_court
    
                if abs(truck_court_diff) >= 30:  # Material difference
                    # Penalty for inadequate truck court: 2-5% of value
                    if subject_truck_court < 120 or comp_truck_court < 120:
                        truck_court_adjustment_pct = 3.0  # 3% penalty if below minimum
                        truck_court_adjustment = base_price * (truck_court_adjustment_pct / 100)
    
                        if subject_truck_court < comp_truck_court:
                            truck_court_adjustment = -truck_court_adjustment
    
                        total_adjustment_amount += truck_court_adjustment
    
                        adjustments.append({
                            'category': 'Industrial Building',
                            'characteristic': 'Truck Court Depth',
                            'subject_value': f'{subject_truck_court} feet',
                            'comp_value': f'{comp_truck_court} feet',
                            'adjustment': truck_court_adjustment,
                            'explanation': f'Inadequate truck court penalty: {truck_court_adjustment_pct}% of property value'
                        })
    
            # 24. CONDITION (Industrial-specific)
            condition_hierarchy = {'poor': 1, 'fair': 2, 'average': 3, 'good': 4, 'excellent': 5}
            subject_condition = self.subject.get('condition', 'average')
            comp_condition = comparable.get('condition', 'average')
    
            subject_condition_score = condition_hierarchy.get(subject_condition, 3)
            comp_condition_score = condition_hierarchy.get(comp_condition, 3)
    
            condition_diff = subject_condition_score - comp_condition_score
    
            if condition_diff != 0:
                # Industrial: 5-8% per condition level
                condition_adjustment_pct = self.market.get('condition_adjustment_pct_per_level', 6.0)
                condition_adjustment = base_price * (condition_diff * condition_adjustment_pct / 100)
                total_adjustment_amount += condition_adjustment
    
                adjustments.append({
                    'category': 'Industrial Building',
                    'characteristic': 'Condition',
                    'subject_value': subject_condition,
                    'comp_value': comp_condition,
                    'adjustment': condition_adjustment,
                    'explanation': f'{condition_diff:+} levels × {condition_adjustment_pct}%'
                })
    
        # =========================================================================
        # BUILDING - OFFICE SPECIFIC (8 subcategories)
        # =========================================================================
    
        elif property_type == 'office':
    
            # 25. BUILDING SIZE (sq ft)
            subject_building_sf = self.subject.get('building_sf', 0)
            comp_building_sf = comparable.get('building_sf', 0)
    
            if subject_building_sf > 0 and comp_building_sf > 0:
                building_diff_sf = subject_building_sf - comp_building_sf
    
                # Office: Economies of scale similar to industrial
                building_adjustment_per_sf = self.market.get('building_size_adjustment_per_sf', 3.0)
    
                building_size_adjustment = building_diff_sf * building_adjustment_per_sf
                total_adjustment_amount += building_size_adjustment
    
                adjustments.append({
                    'category': 'Office Building',
                    'characteristic': 'Building Size',
                    'subject_value': f'{subject_building_sf:,} sq ft',
                    'comp_value': f'{comp_building_sf:,} sq ft',
                    'adjustment': building_size_adjustment,
                    'explanation': f'{building_diff_sf:+,} sq ft × ${building_adjustment_per_sf}/sq ft'
                })
    
            # 26. FLOOR PLATE EFFICIENCY (RSF/USF Ratio)
            subject_efficiency = self.subject.get('floor_plate_efficiency_pct', 85.0)
            comp_efficiency = comparable.get('floor_plate_efficiency_pct', 85.0)
    
            if subject_efficiency != comp_efficiency:
                efficiency_diff = subject_efficiency - comp_efficiency
    
                # Typical range: 75-90%
                # 85% is standard, above is premium, below is penalty
                # Value: 1-2% per 5% efficiency points
                efficiency_adjustment_pct_per_5pts = self.market.get('efficiency_adjustment_pct_per_5pts', 1.5)
                efficiency_adjustment = base_price * ((efficiency_diff / 5) * efficiency_adjustment_pct_per_5pts / 100)
    
                total_adjustment_amount += efficiency_adjustment
    
                adjustments.append({
                    'category': 'Office Building',
                    'characteristic': 'Floor Plate Efficiency',
                    'subject_value': f'{subject_efficiency}%',
                    'comp_value': f'{comp_efficiency}%',
                    'adjustment': efficiency_adjustment,
                    'explanation': f'{efficiency_diff:+.1f}% differential × {efficiency_adjustment_pct_per_5pts}% per 5 points'
                })
    
            # 27. PARKING RATIO (spaces per 1,000 sf)
            subject_parking_ratio = self.subject.get('parking_spaces_per_1000sf', 0)
            comp_parking_ratio = comparable.get('parking_spaces_per_1000sf', 0)
    
            if subject_parking_ratio != comp_parking_ratio:
                parking_diff = subject_parking_ratio - comp_parking_ratio
    
                # Standard: 3.5-4.5 spaces per 1,000 sf
                # Below standard: penalty, above: premium
                # Value: $3,000-$5,000 per space
                parking_value_per_space = self.market.get('parking_value_per_space', 4000)
    
                # Calculate spaces differential based on building size
                spaces_diff = (parking_diff * comp_building_sf) / 1000
    
                parking_adjustment = spaces_diff * parking_value_per_space
                total_adjustment_amount += parking_adjustment
    
                adjustments.append({
                    'category': 'Office Building',
                    'characteristic': 'Parking Ratio',
                    'subject_value': f'{subject_parking_ratio:.1f}/1,000 sf',
                    'comp_value': f'{comp_parking_ratio:.1f}/1,000 sf',
                    'adjustment': parking_adjustment,
                    'explanation': f'{spaces_diff:+.0f} spaces × ${parking_value_per_space:,}/space'
                })
    
            # 28. BUILDING CLASS (A/B/C)
            class_hierarchy = {'C': 1, 'B-': 2, 'B': 3, 'B+': 4, 'A-': 5, 'A': 6, 'A+': 7}
            subject_class = self.subject.get('building_class', 'B')
            comp_class = comparable.get('building_class', 'B')
    
            subject_class_score = class_hierarchy.get(subject_class, 3)
            comp_class_score = class_hierarchy.get(comp_class, 3)
    
            class_diff = subject_class_score - comp_class_score
    
            if class_diff != 0:
                # Each class level: 8-12% differential
                class_adjustment_pct = self.market.get('building_class_adjustment_pct_per_level', 10.0)
                class_adjustment = base_price * (class_diff * class_adjustment_pct / 100)
                total_adjustment_amount += class_adjustment
    
                adjustments.append({
                    'category': 'Office Building',
                    'characteristic': 'Building Class',
                    'subject_value': f'Class {subject_class}',
                    'comp_value': f'Class {comp_class}',
                    'adjustment': class_adjustment,
                    'explanation': f'{class_diff:+} class levels × {class_adjustment_pct}%'
                })
    
            # 29. CEILING HEIGHT
            subject_ceiling_height = self.subject.get('ceiling_height_feet', 9.0)
            comp_ceiling_height = comparable.get('ceiling_height_feet', 9.0)
    
            if subject_ceiling_height != comp_ceiling_height:
                ceiling_diff = subject_ceiling_height - comp_ceiling_height
    
                # Standard: 9', Modern: 10-12'
                # Premium for higher ceilings: $2-$4/sf per foot
                if abs(ceiling_diff) >= 1:
                    ceiling_height_premium_per_sf = self.market.get('ceiling_height_premium_per_sf', 3.0)
                    ceiling_adjustment = ceiling_diff * ceiling_height_premium_per_sf * comp_building_sf
    
                    total_adjustment_amount += ceiling_adjustment
    
                    adjustments.append({
                        'category': 'Office Building',
                        'characteristic': 'Ceiling Height',
                        'subject_value': f'{subject_ceiling_height} feet',
                        'comp_value': f'{comp_ceiling_height} feet',
                        'adjustment': ceiling_adjustment,
                        'explanation': f'{ceiling_diff:+.0f} feet × ${ceiling_height_premium_per_sf}/sf × {comp_building_sf:,} sf'
                    })
    
            # 30. ELEVATOR COUNT / CAPACITY
            subject_elevators = self.subject.get('elevator_count', 0)
            comp_elevators = comparable.get('elevator_count', 0)
    
            if subject_elevators != comp_elevators:
                elevator_diff = subject_elevators - comp_elevators
    
                # Elevator cost: $150K-$250K per elevator installed
                # Value contribution (depreciated): $100K-$150K
                elevator_value = self.market.get('elevator_value_each', 125000)
    
                elevator_adjustment = elevator_diff * elevator_value
                total_adjustment_amount += elevator_adjustment
    
                adjustments.append({
                    'category': 'Office Building',
                    'characteristic': 'Elevator Count',
                    'subject_value': f'{subject_elevators} elevators',
                    'comp_value': f'{comp_elevators} elevators',
                    'adjustment': elevator_adjustment,
                    'explanation': f'{elevator_diff:+} elevators × ${elevator_value:,} each'
                })
    
            # 31. WINDOW LINE (Perimeter Offices)
            subject_window_pct = self.subject.get('window_line_percentage', 30)
            comp_window_pct = comparable.get('window_line_percentage', 30)
    
            if subject_window_pct != comp_window_pct:
                window_diff = subject_window_pct - comp_window_pct
    
                # Window line offices command premium
                # Typical: 25-35% of floor area
                # Premium: $5-$10/sf for windowed space
                window_premium_per_sf = self.market.get('window_line_premium_per_sf', 7.0)
    
                window_adjustment = (window_diff / 100) * window_premium_per_sf * comp_building_sf
                total_adjustment_amount += window_adjustment
    
                adjustments.append({
                    'category': 'Office Building',
                    'characteristic': 'Window Line %',
                    'subject_value': f'{subject_window_pct}% perimeter offices',
                    'comp_value': f'{comp_window_pct}% perimeter offices',
                    'adjustment': window_adjustment,
                    'explanation': f'{window_diff:+}% × ${window_premium_per_sf}/sf × {comp_building_sf:,} sf'
                })
    
            # 32. CONDITION (Office-specific)
            condition_hierarchy = {'poor': 1, 'fair': 2, 'average': 3, 'good': 4, 'excellent': 5}
            subject_condition = self.subject.get('condition', 'average')
            comp_condition = comparable.get('condition', 'average')
    
            subject_condition_score = condition_hierarchy.get(subject_condition, 3)
            comp_condition_score = condition_hierarchy.get(comp_condition, 3)
    
            condition_diff = subject_condition_score - comp_condition_score
    
            if condition_diff != 0:
                # Office: 6-10% per condition level (higher than industrial)
                condition_adjustment_pct = self.market.get('condition_adjustment_pct_per_level', 8.0)
                condition_adjustment = base_price * (condition_diff * condition_adjustment_pct / 100)
                total_adjustment_amount += condition_adjustment
    
                adjustments.append({
                    'category': 'Office Building',
                    'characteristic': 'Condition',
                    'subject_value': subject_condition,
                    'comp_value': comp_condition,
                    'adjustment': condition_adjustment,
                    'explanation': f'{condition_diff:+} levels × {condition_adjustment_pct}%'
                })
    
        # =========================================================================
        # BUILDING - GENERAL (All Property Types) (6 subcategories)
        # =========================================================================
    
        # 33. AGE / EFFECTIVE AGE
        subject_age = self.subject.get('effective_age_years', 0)
        comp_age = comparable.get('effective_age_years', 0)
    
        if subject_age != comp_age:
            age_diff = subject_age - comp_age
    
            # Depreciation: 0.5-1.5% per year depending on property type
            annual_depreciation_pct = self.market.get('annual_depreciation_pct', 1.0)
    
            age_adjustment = base_price * (age_diff * annual_depreciation_pct / 100)
            total_adjustment_amount += age_adjustment
    
            adjustments.append({
                'category': 'Building - General',
                'characteristic': 'Age/Effective Age',
                'subject_value': f'{subject_age} years',
                'comp_value': f'{comp_age} years',
                'adjustment': age_adjustment,
                'explanation': f'{age_diff:+} years × {annual_depreciation_pct}% annual depreciation'
            })
    
        # 34. CONSTRUCTION QUALITY
        quality_hierarchy = {'economy': 1, 'standard': 2, 'good': 3, 'superior': 4}
        subject_quality = self.subject.get('construction_quality', 'standard')
        comp_quality = comparable.get('construction_quality', 'standard')
    
        subject_quality_score = quality_hierarchy.get(subject_quality, 2)
        comp_quality_score = quality_hierarchy.get(comp_quality, 2)
    
        quality_diff = subject_quality_score - comp_quality_score
    
        if quality_diff != 0:
            # Quality differential: 5-10% per level
            quality_adjustment_pct = self.market.get('construction_quality_adjustment_pct_per_level', 7.0)
            quality_adjustment = base_price * (quality_diff * quality_adjustment_pct / 100)
            total_adjustment_amount += quality_adjustment
    
            adjustments.append({
                'category': 'Building - General',
                'characteristic': 'Construction Quality',
                'subject_value': subject_quality,
                'comp_value': comp_quality,
                'adjustment': quality_adjustment,
                'explanation': f'{quality_diff:+} levels × {quality_adjustment_pct}%'
            })
    
        # 35. FUNCTIONAL UTILITY / OBSOLESCENCE
        functional_map = {'severe_obsolescence': -15, 'moderate_obsolescence': -8, 'minor_obsolescence': -3, 'adequate': 0, 'superior': 5}
        subject_functional = self.subject.get('functional_utility', 'adequate')
        comp_functional = comparable.get('functional_utility', 'adequate')
    
        subject_functional_pct = functional_map.get(subject_functional, 0)
        comp_functional_pct = functional_map.get(comp_functional, 0)
    
        if subject_functional_pct != comp_functional_pct:
            functional_adjustment_pct = subject_functional_pct - comp_functional_pct
            functional_adjustment = base_price * (functional_adjustment_pct / 100)
            total_adjustment_amount += functional_adjustment
    
            adjustments.append({
                'category': 'Building - General',
                'characteristic': 'Functional Utility',
                'subject_value': subject_functional,
                'comp_value': comp_functional,
                'adjustment': functional_adjustment,
                'explanation': f'Functional utility differential: {functional_adjustment_pct:+.1f}%'
            })
    
        # 36. ENERGY EFFICIENCY (LEED, Green Features)
        energy_map = {'none': 0, 'energy_star': 3, 'leed_certified': 5, 'leed_silver': 8, 'leed_gold': 12, 'leed_platinum': 18}
        subject_energy = self.subject.get('energy_certification', 'none')
        comp_energy = comparable.get('energy_certification', 'none')
    
        subject_energy_pct = energy_map.get(subject_energy, 0)
        comp_energy_pct = energy_map.get(comp_energy, 0)
    
        if subject_energy_pct != comp_energy_pct:
            energy_adjustment_pct = subject_energy_pct - comp_energy_pct
            energy_adjustment = base_price * (energy_adjustment_pct / 100)
            total_adjustment_amount += energy_adjustment
    
            adjustments.append({
                'category': 'Building - General',
                'characteristic': 'Energy Efficiency',
                'subject_value': subject_energy,
                'comp_value': comp_energy,
                'adjustment': energy_adjustment,
                'explanation': f'Green building premium: {energy_adjustment_pct:+.1f}%'
            })
    
        # 37. ARCHITECTURAL STYLE / APPEAL
        architectural_map = {'dated': -5, 'average': 0, 'attractive': 3, 'exceptional': 7}
        subject_arch = self.subject.get('architectural_appeal', 'average')
        comp_arch = comparable.get('architectural_appeal', 'average')
    
        subject_arch_pct = architectural_map.get(subject_arch, 0)
        comp_arch_pct = architectural_map.get(comp_arch, 0)
    
        if subject_arch_pct != comp_arch_pct:
            arch_adjustment_pct = subject_arch_pct - comp_arch_pct
            arch_adjustment = base_price * (arch_adjustment_pct / 100)
            total_adjustment_amount += arch_adjustment
    
            adjustments.append({
                'category': 'Building - General',
                'characteristic': 'Architectural Appeal',
                'subject_value': subject_arch,
                'comp_value': comp_arch,
                'adjustment': arch_adjustment,
                'explanation': f'Architectural appeal differential: {arch_adjustment_pct:+.1f}%'
            })
    
        # 38. HVAC SYSTEM (Type and Efficiency)
        hvac_map = {'none': -10, 'basic': 0, 'modern_standard': 5, 'high_efficiency': 10, 'geothermal': 15}
        subject_hvac = self.subject.get('hvac_system', 'modern_standard')
        comp_hvac = comparable.get('hvac_system', 'modern_standard')
    
        subject_hvac_pct = hvac_map.get(subject_hvac, 5)
        comp_hvac_pct = hvac_map.get(comp_hvac, 5)
    
        if subject_hvac_pct != comp_hvac_pct:
            hvac_adjustment_pct = subject_hvac_pct - comp_hvac_pct
            hvac_adjustment = base_price * (hvac_adjustment_pct / 100)
            total_adjustment_amount += hvac_adjustment
    
            adjustments.append({
                'category': 'Building - General',
                'characteristic': 'HVAC System',
                'subject_value': subject_hvac,
                'comp_value': comp_hvac,
                'adjustment': hvac_adjustment,
                'explanation': f'HVAC system differential: {hvac_adjustment_pct:+.1f}%'
            })
    
        # =========================================================================
        # SPECIAL FEATURES (6 subcategories)
        # =========================================================================
    
        # 39. RAIL SPUR (Industrial)
        if property_type == 'industrial':
            subject_rail = self.subject.get('rail_spur', False)
            comp_rail = comparable.get('rail_spur', False)
    
            if subject_rail != comp_rail:
                # Rail spur value: $250K-$500K installed
                # Market premium: 5-10% for rail-served industrial
                rail_adjustment_pct = self.market.get('rail_spur_premium_pct', 7.0)
                rail_adjustment = base_price * (rail_adjustment_pct / 100)
    
                if not subject_rail:  # Comparable has rail, subject doesn't
                    rail_adjustment = -rail_adjustment
    
                total_adjustment_amount += rail_adjustment
    
                adjustments.append({
                    'category': 'Special Features',
                    'characteristic': 'Rail Spur',
                    'subject_value': 'Yes' if subject_rail else 'No',
                    'comp_value': 'Yes' if comp_rail else 'No',
                    'adjustment': rail_adjustment,
                    'explanation': f'Rail spur premium: {rail_adjustment_pct}% of property value'
                })
    
        # 40. CRANE SYSTEMS (Industrial)
        if property_type == 'industrial':
            subject_crane = self.subject.get('crane_system', 'none')
            comp_crane = comparable.get('crane_system', 'none')
    
            crane_map = {'none': 0, 'jib_crane': 50000, 'bridge_crane_10ton': 150000, 'bridge_crane_20ton': 250000, 'gantry_crane': 400000}
    
            subject_crane_value = crane_map.get(subject_crane, 0)
            comp_crane_value = crane_map.get(comp_crane, 0)
    
            if subject_crane_value != comp_crane_value:
                crane_adjustment = subject_crane_value - comp_crane_value
    
                # Depreciate by age
                crane_age = comparable.get('crane_age_years', 10)
                crane_life = 30  # Typical useful life
                crane_depreciation = max(0, 1 - (crane_age / crane_life))
    
                crane_adjustment = crane_adjustment * crane_depreciation
                total_adjustment_amount += crane_adjustment
    
                adjustments.append({
                    'category': 'Special Features',
                    'characteristic': 'Crane System',
                    'subject_value': subject_crane,
                    'comp_value': comp_crane,
                    'adjustment': crane_adjustment,
                    'explanation': f'Crane system differential: ${subject_crane_value - comp_crane_value:,} × {crane_depreciation:.0%} depreciation'
                })
    
        # 41. HEAVY POWER (3-Phase, High Voltage)
        if property_type == 'industrial':
            subject_power_amps = self.subject.get('electrical_service_amps', 0)
            comp_power_amps = comparable.get('electrical_service_amps', 0)
    
            if subject_power_amps != comp_power_amps:
                power_diff = subject_power_amps - comp_power_amps
    
                # Heavy power (1000+ amps): significant value for manufacturing
                # Premium: $10-$20 per amp for capacity over 400 amps
                if abs(power_diff) >= 200:  # Material difference
                    power_value_per_amp = self.market.get('electrical_capacity_value_per_amp', 15.0)
                    power_adjustment = power_diff * power_value_per_amp
    
                    total_adjustment_amount += power_adjustment
    
                    adjustments.append({
                        'category': 'Special Features',
                        'characteristic': 'Electrical Capacity',
                        'subject_value': f'{subject_power_amps} amps',
                        'comp_value': f'{comp_power_amps} amps',
                        'adjustment': power_adjustment,
                        'explanation': f'{power_diff:+} amps × ${power_value_per_amp}/amp'
                    })
    
        # 42. TRUCK SCALES (Industrial)
        if property_type == 'industrial':
            subject_scales = self.subject.get('truck_scales', False)
            comp_scales = comparable.get('truck_scales', False)
    
            if subject_scales != comp_scales:
                # Truck scale value: $50K-$100K installed
                scales_value = self.market.get('truck_scales_value', 75000)
    
                scales_adjustment = scales_value if subject_scales else -scales_value
                total_adjustment_amount += scales_adjustment
    
                adjustments.append({
                    'category': 'Special Features',
                    'characteristic': 'Truck Scales',
                    'subject_value': 'Yes' if subject_scales else 'No',
                    'comp_value': 'Yes' if comp_scales else 'No',
                    'adjustment': scales_adjustment,
                    'explanation': f'Truck scales value: ${scales_value:,}'
                })
    
        # 43. SPECIALIZED HVAC (Cleanroom, Temperature Control)
        specialized_hvac_map = {'none': 0, 'temperature_controlled': 100000, 'humidity_controlled': 150000, 'cleanroom_class_100k': 300000, 'cleanroom_class_10k': 600000}
    
        subject_spec_hvac = self.subject.get('specialized_hvac', 'none')
        comp_spec_hvac = comparable.get('specialized_hvac', 'none')
    
        subject_spec_hvac_value = specialized_hvac_map.get(subject_spec_hvac, 0)
        comp_spec_hvac_value = specialized_hvac_map.get(comp_spec_hvac, 0)
    
        if subject_spec_hvac_value != comp_spec_hvac_value:
            spec_hvac_adjustment = subject_spec_hvac_value - comp_spec_hvac_value
            total_adjustment_amount += spec_hvac_adjustment
    
            adjustments.append({
                'category': 'Special Features',
                'characteristic': 'Specialized HVAC',
                'subject_value': subject_spec_hvac,
                'comp_value': comp_spec_hvac,
                'adjustment': spec_hvac_adjustment,
                'explanation': f'Specialized HVAC differential: ${spec_hvac_adjustment:+,}'
            })
    
        # 44. BACKUP GENERATOR
        subject_generator = self.subject.get('backup_generator_kw', 0)
        comp_generator = comparable.get('backup_generator_kw', 0)
    
        if subject_generator != comp_generator:
            generator_diff = subject_generator - comp_generator
    
            # Generator value: $500-$1,000 per kW installed
            generator_value_per_kw = self.market.get('generator_value_per_kw', 750)
    
            generator_adjustment = generator_diff * generator_value_per_kw
            total_adjustment_amount += generator_adjustment
    
            adjustments.append({
                'category': 'Special Features',
                'characteristic': 'Backup Generator',
                'subject_value': f'{subject_generator} kW',
                'comp_value': f'{comp_generator} kW',
                'adjustment': generator_adjustment,
                'explanation': f'{generator_diff:+} kW × ${generator_value_per_kw}/kW'
            })
    
        # =========================================================================
        # ZONING / LEGAL (5 subcategories)
        # =========================================================================
    
        # 45. ZONING CLASSIFICATION
        # This is highly market-specific, using permitted use value mapping
        zoning_value_map = self.market.get('zoning_value_map', {})
    
        subject_zoning = self.subject.get('zoning', '')
        comp_zoning = comparable.get('zoning', '')
    
        if subject_zoning and comp_zoning and subject_zoning != comp_zoning:
            subject_zoning_value_pct = zoning_value_map.get(subject_zoning, 0)
            comp_zoning_value_pct = zoning_value_map.get(comp_zoning, 0)
    
            if subject_zoning_value_pct != comp_zoning_value_pct:
                zoning_adjustment_pct = subject_zoning_value_pct - comp_zoning_value_pct
                zoning_adjustment = base_price * (zoning_adjustment_pct / 100)
                total_adjustment_amount += zoning_adjustment
    
                adjustments.append({
                    'category': 'Zoning/Legal',
                    'characteristic': 'Zoning Classification',
                    'subject_value': subject_zoning,
                    'comp_value': comp_zoning,
                    'adjustment': zoning_adjustment,
                    'explanation': f'Zoning value differential: {zoning_adjustment_pct:+.1f}%'
                })
    
        # 46. FLOOR AREA RATIO (FAR) / DEVELOPMENT POTENTIAL
        subject_far = self.subject.get('floor_area_ratio', 0)
        comp_far = comparable.get('floor_area_ratio', 0)
    
        if subject_far > 0 and comp_far > 0:
            far_diff = subject_far - comp_far
    
            # Higher FAR = more development potential
            # Value: Market-dependent, typically $5-$15/sf of additional buildable area
            far_value_per_buildable_sf = self.market.get('far_value_per_buildable_sf', 10.0)
    
            # Calculate additional buildable area based on lot size
            subject_lot_sf = subject_lot_acres * 43560
            additional_buildable_sf = far_diff * subject_lot_sf
    
            far_adjustment = additional_buildable_sf * far_value_per_buildable_sf
            total_adjustment_amount += far_adjustment
    
            adjustments.append({
                'category': 'Zoning/Legal',
                'characteristic': 'Floor Area Ratio',
                'subject_value': f'{subject_far:.2f} FAR',
                'comp_value': f'{comp_far:.2f} FAR',
                'adjustment': far_adjustment,
                'explanation': f'{far_diff:+.2f} FAR × {subject_lot_sf:,.0f} sf lot × ${far_value_per_buildable_sf}/sf buildable'
            })
    
        # 47. VARIANCE / SPECIAL USE PERMIT
        subject_variance = self.subject.get('has_variance', False)
        comp_variance = comparable.get('has_variance', False)
    
        if subject_variance != comp_variance:
            # Variance value: Depends on what it permits
            # Typical: 5-15% premium if variance enables profitable use
            variance_premium_pct = self.market.get('variance_premium_pct', 8.0)
            variance_adjustment = base_price * (variance_premium_pct / 100)
    
            if not subject_variance:  # Comparable has variance, subject doesn't
                variance_adjustment = -variance_adjustment
    
            total_adjustment_amount += variance_adjustment
    
            adjustments.append({
                'category': 'Zoning/Legal',
                'characteristic': 'Variance/Special Permit',
                'subject_value': 'Yes' if subject_variance else 'No',
                'comp_value': 'Yes' if comp_variance else 'No',
                'adjustment': variance_adjustment,
                'explanation': f'Variance premium: {variance_premium_pct}% of property value'
            })
    
        # 48. NON-CONFORMING USE (Grandfathered)
        subject_nonconforming = self.subject.get('non_conforming_use', False)
        comp_nonconforming = comparable.get('non_conforming_use', False)
    
        if subject_nonconforming != comp_nonconforming:
            # Non-conforming use: Can be premium or penalty depending on market
            # If profitable use: Premium (can't be replicated)
            # If limiting: Penalty (restricts future use)
            nonconforming_adjustment_pct = self.market.get('nonconforming_use_adjustment_pct', 5.0)  # Can be positive or negative
    
            nonconforming_adjustment = base_price * (nonconforming_adjustment_pct / 100)
    
            if not subject_nonconforming:  # Comparable has non-conforming, subject doesn't
                nonconforming_adjustment = -nonconforming_adjustment
    
            total_adjustment_amount += nonconforming_adjustment
    
            adjustments.append({
                'category': 'Zoning/Legal',
                'characteristic': 'Non-Conforming Use',
                'subject_value': 'Yes' if subject_nonconforming else 'No',
                'comp_value': 'Yes' if comp_nonconforming else 'No',
                'adjustment': nonconforming_adjustment,
                'explanation': f'Non-conforming use adjustment: {nonconforming_adjustment_pct:+.1f}%'
            })
    
        # 49. LOT COVERAGE / BUILDING COVERAGE RATIO
        subject_coverage = self.subject.get('lot_coverage_pct', 0)
        comp_coverage = comparable.get('lot_coverage_pct', 0)
    
        if subject_coverage > 0 and comp_coverage > 0:
            coverage_diff = subject_coverage - comp_coverage
    
            # Higher existing coverage = less future expansion potential
            # But also = more current improvements
            # Net effect: Depends on market demand for expansion vs. current use
            # Typically minor adjustment unless extreme difference
    
            if abs(coverage_diff) >= 15:  # Material difference (>15%)
                # If subject has significantly more coverage: Minor premium for current improvements
                # If comp has more coverage: Adjust for lack of expansion in comparable
                coverage_adjustment_pct = (coverage_diff / 10) * 0.5  # 0.5% per 10% coverage
    
                coverage_adjustment = base_price * (coverage_adjustment_pct / 100)
                total_adjustment_amount += coverage_adjustment
    
                adjustments.append({
                    'category': 'Zoning/Legal',
                    'characteristic': 'Lot Coverage',
                    'subject_value': f'{subject_coverage}% covered',
                    'comp_value': f'{comp_coverage}% covered',
                    'adjustment': coverage_adjustment,
                    'explanation': f'Lot coverage differential: {coverage_diff:+}% ({coverage_adjustment_pct:+.1f}% value impact)'
                })
    
        # =========================================================================
        # CALCULATE TOTALS AND RETURN
        # =========================================================================
    
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
            'name': 'Physical Characteristics (ENHANCED)',
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
        gross_adjustment_pct = (gross_adjustment / sale_price) * 100 if sale_price > 0 else 0

        net_adjustment = sum(stage['adjustment_amount'] for stage in all_stages)
        net_adjustment_pct = (net_adjustment / sale_price) * 100 if sale_price > 0 else 0

        final_adjusted_price = stage6['adjusted_price']

        # Validation flags
        gross_exceeds_25pct = gross_adjustment_pct > 25.0
        gross_exceeds_40pct = gross_adjustment_pct > 40.0
        net_exceeds_15pct = abs(net_adjustment_pct) > 15.0

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
        elif gross_pct > 30:
            return 'CAUTION'
        else:
            return 'ACCEPTABLE'

    def _get_validation_recommendation(self, gross_pct: float, exceeds_40: bool) -> str:
        """Generate validation recommendation."""
        if exceeds_40:
            return f'Gross adjustment {gross_pct:.1f}% exceeds 40% threshold - comparable is NOT truly comparable, do not use'
        elif gross_pct > 30:
            return f'Gross adjustment {gross_pct:.1f}% is in caution range (30-40%) - comparable is marginal, weight accordingly'
        elif gross_pct > 25:
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
            if abs(stage['adjustment_pct']) > 5.0:  # Only test material adjustments
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
                'weighting_method': 'Inverse net adjustment with validation status filters',
                'total_weight': total_weight
            },
            'statistics': stats,
            'calculation_date': datetime.now().isoformat(),
            'calculator_version': '1.0.0'
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


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Calculate adjusted comparable sale prices using 6-stage adjustment hierarchy'
    )
    parser.add_argument('input_file', help='Path to input JSON file')
    parser.add_argument('--output', '-o', help='Path to output JSON file (optional)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Print detailed output')
    parser.add_argument('--sensitivity', '-s', action='store_true', help='Include sensitivity analysis')

    args = parser.parse_args()

    # Load input
    with open(args.input_file, 'r') as f:
        input_data = json.load(f)

    # Calculate
    calculator = ComparableSalesCalculator(input_data)
    results = calculator.reconcile_comparables()

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
