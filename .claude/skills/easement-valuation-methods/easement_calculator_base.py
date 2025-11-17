#!/usr/bin/env python3
"""
Easement Valuation Calculator - Base Class

Abstract base class containing shared valuation logic for all easement types.
Subclasses implement domain-specific percentage calculations and adjustments.

Shared methodologies:
1. Percentage of Fee Method (framework - subclass provides base percentages)
2. Income Capitalization Method (productivity loss basis)
3. Before/After Comparison Method
4. TCE Rate-of-Return Method (for temporary construction easements)
5. Dynamic Reconciliation Weights
6. Sensitivity Analysis

Supports: easement-valuation-methods skill
Used by: hydro_easement_calculator, rail_easement_calculator, pipeline_easement_calculator

Author: Claude Code
Created: 2025-11-17
Version: 2.0.0
"""

import sys
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add Shared_Utils to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "Shared_Utils"))
from financial_utils import pv_annuity, npv, annual_to_monthly_rate


class EasementCalculatorBase(ABC):
    """
    Abstract base class for easement valuation calculators.

    Subclasses must implement:
    - get_base_percentage(): Domain-specific base percentage calculation
    - get_domain_specific_adjustments(): Domain-specific percentage adjustments (optional)
    """

    def __init__(self, input_data: Dict):
        """Initialize calculator with input data."""
        self.data = input_data
        self.property_data = input_data['property']
        self.easement_data = input_data['easement']
        self.market_data = input_data['market_parameters']
        self.results = {}

    @abstractmethod
    def get_base_percentage(self) -> float:
        """
        Get domain-specific base percentage for easement type.

        Subclasses implement this based on:
        - Hydro: voltage_kv (10-22.5%)
        - Rail: rail_type + train frequency (15-25%)
        - Pipeline: pipeline_type + pressure (10-18%)

        Returns:
            float: Base percentage (e.g., 17.5 for 17.5%)
        """
        pass

    def get_domain_specific_adjustments(self) -> Dict[str, float]:
        """
        Get domain-specific percentage adjustments (optional override).

        Subclasses can override for infrastructure-specific adjustments:
        - Hydro: EMF concerns, tower placement
        - Rail: Noise, vibration, grade crossings
        - Pipeline: Depth, diameter, leak risk

        Returns:
            Dict[str, float]: {adjustment_name: percentage_value}
        """
        return {}

    def is_temporary_construction_easement(self) -> bool:
        """
        Determine if this is a TCE requiring rate-of-return methodology.

        TCE criteria:
        - term = 'tce' OR
        - (term = 'temporary' AND duration_days < 1095 days / 3 years)
        """
        term = self.easement_data.get('term', 'perpetual')

        if term == 'tce':
            return True

        if term == 'temporary':
            duration_days = self.easement_data.get('duration_days')
            if duration_days and duration_days < 1095:  # Less than 3 years
                return True

        return False

    def calculate_percentage_of_fee(self) -> Dict:
        """
        Calculate easement value as percentage of fee simple value.

        Framework method that:
        1. Calls subclass get_base_percentage() for domain-specific base
        2. Applies shared adjustments (width, restrictions, term, HBU)
        3. Applies domain-specific adjustments from subclass
        4. Clamps to reasonable range (5-35%)
        5. Calculates easement value

        Returns:
            Dict with method details and easement_value
        """
        fee_simple_value = self.property_data['fee_simple_value']
        easement_area_acres = self.easement_data['area_acres']

        # Get base percentage from subclass (domain-specific)
        base_pct = self.get_base_percentage()

        # Shared adjustments
        width_adjustment = self._calculate_width_adjustment()
        restriction_adjustment = self._calculate_restriction_adjustment()
        term_adjustment = self._calculate_term_adjustment()
        hbu_adjustment = self._calculate_hbu_impact_adjustment()

        # Domain-specific adjustments (from subclass)
        domain_adjustments = self.get_domain_specific_adjustments()
        domain_adjustment_total = sum(domain_adjustments.values())

        # Final percentage
        final_percentage = (
            base_pct +
            width_adjustment +
            restriction_adjustment +
            term_adjustment +
            hbu_adjustment +
            domain_adjustment_total
        )

        # Clamp to reasonable range (5-35%)
        final_percentage = max(5.0, min(35.0, final_percentage))

        # Calculate value
        value_per_acre = fee_simple_value / self.property_data['total_acres']
        easement_value = value_per_acre * easement_area_acres * (final_percentage / 100)

        adjustments = {
            'width': width_adjustment,
            'restrictions': restriction_adjustment,
            'term': term_adjustment,
            'highest_and_best_use': hbu_adjustment
        }

        # Add domain-specific adjustments
        adjustments.update(domain_adjustments)

        return {
            'method': 'Percentage of Fee',
            'base_percentage': base_pct,
            'adjustments': adjustments,
            'final_percentage': final_percentage,
            'fee_simple_value_per_acre': value_per_acre,
            'easement_area_acres': easement_area_acres,
            'easement_value': easement_value
        }

    def _calculate_width_adjustment(self) -> float:
        """Calculate adjustment based on easement width (shared logic)."""
        width_m = self.easement_data.get('width_meters', 0)

        # Wider easements have greater impact
        if width_m >= 100:
            return 3.0  # Very wide (500kV corridors)
        elif width_m >= 60:
            return 2.0  # Wide (230kV corridors)
        elif width_m >= 40:
            return 1.0  # Moderate (115kV corridors)
        elif width_m >= 20:
            return 0.0  # Standard (69kV corridors)
        else:
            return -1.0  # Narrow (telecom, utilities)

    def _calculate_restriction_adjustment(self) -> float:
        """Calculate adjustment based on use restrictions (shared logic)."""
        restrictions = self.easement_data.get('restrictions', [])

        adjustment = 0.0

        restriction_impacts = {
            'no_buildings': 2.0,
            'no_trees': 1.5,
            'height_restrictions': 1.0,
            'access_limitations': 1.5,
            'excavation_prohibited': 1.0
        }

        for restriction in restrictions:
            adjustment += restriction_impacts.get(restriction, 0.0)

        return min(adjustment, 5.0)  # Cap at +5%

    def _calculate_term_adjustment(self) -> float:
        """Calculate adjustment based on easement term (shared logic)."""
        term = self.easement_data.get('term', 'perpetual')

        if term == 'perpetual':
            return 0.0  # No adjustment
        elif term in ['temporary', 'tce']:
            # For short-term permanent easements (NOT TCEs which use different methodology)
            years = self.easement_data.get('term_years', 10)
            if years <= 5:
                return -8.0  # Very temporary
            elif years <= 10:
                return -5.0  # Short term
            elif years <= 25:
                return -3.0  # Medium term
            else:
                return -1.0  # Long term (approaching perpetual)
        return 0.0

    def _calculate_hbu_impact_adjustment(self) -> float:
        """Calculate adjustment based on impact to highest and best use (shared logic)."""
        hbu_impact = self.easement_data.get('hbu_impact', 'moderate')

        impacts = {
            'none': -2.0,          # Minimal impact to HBU
            'minor': 0.0,          # Some impact but HBU still achievable
            'moderate': 2.0,       # Moderate impact to HBU
            'major': 5.0,          # Significant impact to HBU
            'precludes_development': 8.0  # Prevents development entirely
        }

        return impacts.get(hbu_impact, 2.0)

    def calculate_income_capitalization(self) -> Dict:
        """
        Calculate easement value using income capitalization method (shared logic).

        FIXED (v2.0): Uses productivity_loss_pct instead of ambiguous easement_rent_factor.

        Methodology:
        1. Determine annual rent per acre for land WITHOUT easement
        2. Calculate annual LOSS from easement (productivity_loss_pct × annual_rent)
        3. Capitalize annual loss to present value

        Example:
        - Annual rent: $300/acre
        - Productivity loss: 20% (towers, restricted areas)
        - Annual loss: $300 × 20% = $60/acre
        - Cap rate: 4.5%
        - Easement value: $60 ÷ 0.045 = $1,333/acre
        """
        easement_area_acres = self.easement_data['area_acres']

        # Annual rent per acre (market-based)
        annual_rent_per_acre = self.market_data.get('annual_rent_per_acre')

        if annual_rent_per_acre is None:
            # Estimate from comparable land rents if not provided
            annual_rent_per_acre = self._estimate_rental_rate()

        # Total annual rent for affected area (WITHOUT easement)
        annual_rent_gross = annual_rent_per_acre * easement_area_acres

        # Capitalization rate
        cap_rate = self.market_data['cap_rate']

        # FIXED: Use productivity_loss_pct instead of easement_rent_factor
        # Represents percentage of productivity/rent LOST due to easement
        productivity_loss_pct = self.easement_data.get('productivity_loss_pct')

        # Backward compatibility: check for old parameter name
        if productivity_loss_pct is None:
            productivity_loss_pct = self.easement_data.get('easement_rent_factor', 0.20)

        # Calculate annual rent LOSS (this is what gets capitalized)
        annual_rent_loss = annual_rent_gross * productivity_loss_pct

        # Capitalize loss to value
        easement_value = annual_rent_loss / cap_rate

        return {
            'method': 'Income Capitalization',
            'annual_rent_per_acre': annual_rent_per_acre,
            'easement_area_acres': easement_area_acres,
            'annual_rent_gross': annual_rent_gross,
            'productivity_loss_pct': productivity_loss_pct,
            'annual_rent_loss': annual_rent_loss,
            'cap_rate': cap_rate,
            'easement_value': easement_value,
            'notes': 'Easement value = (Annual Rent Loss) ÷ Cap Rate'
        }

    def _estimate_rental_rate(self) -> float:
        """Estimate annual rent per acre based on land value and cap rate (shared logic)."""
        fee_simple_value = self.property_data['fee_simple_value']
        total_acres = self.property_data['total_acres']
        cap_rate = self.market_data['cap_rate']

        value_per_acre = fee_simple_value / total_acres
        estimated_rent_per_acre = value_per_acre * cap_rate

        return estimated_rent_per_acre

    def calculate_tce_rate_of_return(self) -> Dict:
        """
        Calculate Temporary Construction Easement using rate-of-return method (shared logic).

        NEW (v2.0): Implements TCE methodology from SKILL.md Phase 1 enhancement.

        Formula: TCE Value = (Land Value × Annual Rate × Duration ÷ 365)
                           + Restoration Costs
                           + Business Losses

        Industry standard rates:
        - 6%: Conservative (government agencies)
        - 10%: Industry standard (most common)
        - 12%+: High disruption sites
        """
        if not self.is_temporary_construction_easement():
            return None

        # Land value affected
        total_acres = self.property_data.get('total_acres', self.easement_data['area_acres'])
        fee_simple_value = self.property_data['fee_simple_value']

        # For partial area TCEs, prorate land value
        if total_acres > 0:
            value_per_acre = fee_simple_value / total_acres
            affected_land_value = value_per_acre * self.easement_data['area_acres']
        else:
            affected_land_value = fee_simple_value

        # Annual rate of return (default 10% if not specified)
        annual_rate = self.market_data.get('tce_annual_rate', 0.10)

        # Duration in days
        duration_days = self.easement_data.get('duration_days', 90)

        # Calculate rental value
        rental_value = affected_land_value * annual_rate * (duration_days / 365)

        # Additional compensation components
        restoration_costs = self.easement_data.get('restoration_costs', 0)
        business_losses = self.easement_data.get('business_losses', 0)

        # Total TCE value
        total_tce_value = rental_value + restoration_costs + business_losses

        # Duration category
        if duration_days < 30:
            duration_category = 'short'
        elif duration_days <= 365:
            duration_category = 'medium'
        else:
            duration_category = 'long'

        return {
            'method': 'TCE Rate-of-Return',
            'affected_land_value': affected_land_value,
            'annual_rate': annual_rate,
            'duration_days': duration_days,
            'duration_category': duration_category,
            'rental_value': rental_value,
            'restoration_costs': restoration_costs,
            'business_losses': business_losses,
            'total_tce_value': total_tce_value,
            'notes': f'TCE = (${affected_land_value:,.0f} × {annual_rate:.1%} × {duration_days}/365) + ${restoration_costs:,.0f} + ${business_losses:,.0f}'
        }

    def calculate_before_after(self) -> Dict:
        """
        Calculate easement value using before/after comparison method (shared logic).

        Property value before easement - Property value after easement = Easement value
        """
        # Value before (from input)
        value_before = self.property_data['fee_simple_value']

        # Value after (requires analysis of impact)
        # This can come from input or be calculated
        value_after_input = self.property_data.get('value_after_easement')

        if value_after_input is not None:
            value_after = value_after_input
        else:
            # Estimate value after based on percentage of fee method
            pct_method = self.calculate_percentage_of_fee()
            value_after = value_before - pct_method['easement_value']

        easement_value = value_before - value_after

        # As percentage
        percentage_loss = (easement_value / value_before) * 100

        return {
            'method': 'Before/After Comparison',
            'value_before': value_before,
            'value_after': value_after,
            'easement_value': easement_value,
            'percentage_loss': percentage_loss
        }

    def _get_dynamic_weights(self) -> Dict[str, float]:
        """
        Determine reconciliation weights based on easement characteristics (shared logic).

        NEW (v2.0): Implements dynamic weighting per USPAP/CUSPAP professional judgment.

        Subclasses can override for domain-specific weight logic.
        """
        easement_type = self.easement_data.get('type')

        # Allow user override
        user_weights = self.market_data.get('reconciliation_weights')
        if user_weights:
            return user_weights

        # Default: Balanced weighting
        return {
            'percentage_of_fee': 0.40,
            'income_capitalization': 0.30,
            'before_after': 0.30,
            'reasoning': 'Default: Balanced weighting across methods'
        }

    def sensitivity_analysis(self) -> Dict:
        """
        Perform sensitivity analysis on key assumptions (shared logic).

        NEW (v2.0): Implements sensitivity framework from SKILL.md Phase 1.

        Tests:
        - Cap rate ±1%
        - Productivity loss ±5%
        """
        base_cap_rate = self.market_data['cap_rate']
        base_productivity = self.easement_data.get('productivity_loss_pct', 0.20)

        scenarios = []

        # Cap rate sensitivity (±1%)
        for delta in [-0.01, 0, 0.01]:
            self.market_data['cap_rate'] = base_cap_rate + delta
            income_result = self.calculate_income_capitalization()
            scenarios.append({
                'variable': 'cap_rate',
                'value': base_cap_rate + delta,
                'delta': delta,
                'easement_value': income_result['easement_value']
            })

        # Reset cap rate
        self.market_data['cap_rate'] = base_cap_rate

        # Productivity loss sensitivity (±5%)
        for delta in [-0.05, 0, 0.05]:
            self.easement_data['productivity_loss_pct'] = base_productivity + delta
            income_result = self.calculate_income_capitalization()
            scenarios.append({
                'variable': 'productivity_loss_pct',
                'value': base_productivity + delta,
                'delta': delta,
                'easement_value': income_result['easement_value']
            })

        # Reset productivity
        self.easement_data['productivity_loss_pct'] = base_productivity

        # Calculate range
        values = [s['easement_value'] for s in scenarios]

        return {
            'method': 'Sensitivity Analysis',
            'scenarios': scenarios,
            'value_range': {
                'low': min(values),
                'high': max(values),
                'spread': max(values) - min(values),
                'spread_pct': ((max(values) - min(values)) / min(values)) * 100 if min(values) > 0 else 0
            }
        }

    def calculate_all_methods(self) -> Dict:
        """
        Calculate easement value using all applicable methods (shared logic).

        ENHANCED (v2.0):
        - Routes TCEs to rate-of-return method
        - Uses dynamic reconciliation weights
        - Includes sensitivity analysis
        """
        # Check if TCE
        is_tce = self.is_temporary_construction_easement()

        if is_tce:
            # TCE: Use rate-of-return method
            tce_method = self.calculate_tce_rate_of_return()

            return {
                'property': self.property_data,
                'easement': self.easement_data,
                'market_parameters': self.market_data,
                'easement_classification': 'Temporary Construction Easement (TCE)',
                'valuation_method': tce_method,
                'calculation_date': datetime.now().isoformat(),
                'calculator_version': '2.0.0',
                'calculator_type': self.__class__.__name__
            }

        # Permanent easement: Use all three methods
        pct_method = self.calculate_percentage_of_fee()
        income_method = self.calculate_income_capitalization()
        before_after_method = self.calculate_before_after()

        # Dynamic reconciliation weights
        weights_data = self._get_dynamic_weights()
        reasoning = weights_data.pop('reasoning', 'Professional judgment based on easement type')
        weights = weights_data

        reconciled_value = (
            pct_method['easement_value'] * weights['percentage_of_fee'] +
            income_method['easement_value'] * weights['income_capitalization'] +
            before_after_method['easement_value'] * weights['before_after']
        )

        # Sensitivity analysis
        sensitivity = self.sensitivity_analysis()

        return {
            'property': self.property_data,
            'easement': self.easement_data,
            'market_parameters': self.market_data,
            'easement_classification': 'Permanent Easement',
            'valuation_methods': {
                'percentage_of_fee': pct_method,
                'income_capitalization': income_method,
                'before_after': before_after_method
            },
            'reconciliation': {
                'weights': weights,
                'weighting_reasoning': reasoning,
                'reconciled_value': reconciled_value,
                'value_range': {
                    'low': min(pct_method['easement_value'],
                              income_method['easement_value'],
                              before_after_method['easement_value']),
                    'high': max(pct_method['easement_value'],
                               income_method['easement_value'],
                               before_after_method['easement_value'])
                }
            },
            'sensitivity_analysis': sensitivity,
            'calculation_date': datetime.now().isoformat(),
            'calculator_version': '2.0.0',
            'calculator_type': self.__class__.__name__
        }
