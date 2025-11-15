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
sensitivity analysis (±10% key adjustments).

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
        Stage 6: Physical Characteristics Adjustment

        Adjust for size, condition, improvements, etc.

        Example:
        - Subject: 10,000 sq ft
        - Comparable: 15,000 sq ft
        - Size adjustment: -$3/sq ft for each sq ft over 10,000 (economies of scale)
        """
        adjustments = []
        total_adjustment_amount = 0.0

        # Size adjustment
        subject_size = self.subject.get('size_sf', 0)
        comp_size = comparable.get('size_sf', 0)

        if subject_size > 0 and comp_size > 0:
            size_diff = subject_size - comp_size

            # Market-based size adjustment (e.g., $3/sq ft for economies of scale)
            size_adjustment_per_sf = self.market.get('size_adjustment_per_sf', 3.0)

            # Economies of scale: larger parcels trade at lower $/sf
            # If comparable is larger (size_diff < 0), adjust down
            # If comparable is smaller (size_diff > 0), adjust up
            size_adjustment = size_diff * size_adjustment_per_sf
            total_adjustment_amount += size_adjustment

            adjustments.append({
                'characteristic': 'Size',
                'subject_value': subject_size,
                'comp_value': comp_size,
                'adjustment': size_adjustment,
                'explanation': f'Size differential: {size_diff:+,} sq ft × ${size_adjustment_per_sf}/sq ft'
            })

        # Condition adjustment
        condition_hierarchy = {'poor': 1, 'fair': 2, 'average': 3, 'good': 4, 'excellent': 5}
        subject_condition = self.subject.get('condition', 'average')
        comp_condition = comparable.get('condition', 'average')

        subject_condition_score = condition_hierarchy.get(subject_condition, 3)
        comp_condition_score = condition_hierarchy.get(comp_condition, 3)

        condition_diff = subject_condition_score - comp_condition_score

        if condition_diff != 0:
            # Market-based condition adjustment (e.g., 5% per condition level)
            condition_adjustment_pct = self.market.get('condition_adjustment_pct_per_level', 5.0)
            condition_adjustment = base_price * (condition_diff * condition_adjustment_pct / 100)
            total_adjustment_amount += condition_adjustment

            adjustments.append({
                'characteristic': 'Condition',
                'subject_value': subject_condition,
                'comp_value': comp_condition,
                'adjustment': condition_adjustment,
                'explanation': f'Condition differential: {condition_diff:+} levels × {condition_adjustment_pct}%'
            })

        # Calculate totals
        adjusted_price = base_price + total_adjustment_amount
        adjustment_pct = (total_adjustment_amount / base_price) * 100 if base_price > 0 else 0

        return {
            'stage': 6,
            'name': 'Physical Characteristics',
            'adjustment_amount': total_adjustment_amount,
            'adjustment_pct': adjustment_pct,
            'adjusted_price': adjusted_price,
            'adjustments': adjustments,
            'explanation': f'{len(adjustments)} physical characteristic adjustments applied'
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
        Perform sensitivity analysis by varying key adjustments ±10%.

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

            # Test ±10% variation
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
