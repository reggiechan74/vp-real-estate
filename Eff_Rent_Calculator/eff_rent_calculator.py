"""
Business Approval Form (BAF) Calculator
Commercial Lease Analysis Tool

This script calculates Net Effective Rent (NER), Gross Effective Rent (GER),
NPV analysis, and breakeven thresholds for commercial lease deals.

Theoretical Foundation:
---------------------
Implements the Ponzi Rental Rate (PRR) framework from:

Chan, R. (2015). "Understanding the Ponzi Rental Rate: The Challenges with
Using Net Effective Rents to Analyze Prospective Lease Deals within Real
Estate Investment Trusts." Real Estate Finance, Vol. 32, No. 2, pp. 48-61.

The PRR provides objective breakeven rental rates based on acquisition cost
and financing terms, accounting for dividends, debt service, and building
depreciation via the Inwood sinking fund method.
"""

import numpy as np
import numpy_financial as npf
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime, date
import json
import sys
import argparse
from pathlib import Path


@dataclass
class LeaseTerms:
    """Input parameters for lease analysis"""

    # Property details
    property_type: str = "industrial"  # "industrial" or "office"
    unit_number: str = ""
    area_sf: float = 10000.0
    tenant_name: str = ""
    trade_name: str = ""

    # Lease term
    lease_start_date: date = None
    lease_term_months: int = 120
    operating_costs_psf: float = 14.14

    # Fixturing period
    fixturing_term_months: int = 3

    # Annual rent schedule (psf) - up to 10 years
    rent_schedule_psf: List[float] = field(default_factory=lambda: [14.5] * 10)

    # Number of months for each rent period (default 12 for each year)
    rent_period_months: List[int] = field(default_factory=lambda: [12] * 10)

    # Costs and incentives
    tenant_cash_allowance_psf: float = 30.0  # or absolute amount
    landlord_work: float = 0.0  # absolute amount
    amortized_tenant_work: float = 0.0
    pm_override_fee: float = 0.0

    # Leasing commissions - Two methods supported:
    # Method 1 (Office): Flat $/sf per year (e.g., $2/sf × 5 years = $10/sf total)
    # Method 2 (Industrial): Percentage of annual net rent (e.g., 6% year 1, 2% subsequent)

    # Office method (flat $/sf)
    listing_agent_commission_psf: float = 0.0
    tenant_rep_commission_psf: float = 0.0

    # Industrial method (percentage of net rent)
    listing_agent_year1_pct: float = 0.0
    listing_agent_subsequent_pct: float = 0.0
    tenant_rep_year1_pct: float = 0.0
    tenant_rep_subsequent_pct: float = 0.0

    # Free rent periods
    net_free_rent_months: float = 3.0
    gross_free_rent_months: float = 0.0

    # Discount rate
    nominal_discount_rate: float = 0.10  # 10%

    # Investment parameters (for breakeven analysis)
    gla_building_sf: float = 58679.0
    acquisition_cost: float = 6104553.0
    going_in_ltv: float = 0.5117554
    mortgage_amortization_months: int = 300
    dividend_yield: float = 0.0675
    interest_cost: float = 0.0302
    principal_payment_rate: float = 0.026713


@dataclass
class CalculationResults:
    """Results of BAF calculations"""

    # NPV calculations
    npv_net_rent: float = 0.0
    npv_costs: float = 0.0
    npv_lease_deal: float = 0.0

    # Net Effective Rent
    ner_lease_term_only: float = 0.0
    ner_with_fixturing: float = 0.0

    # Gross Effective Rent
    ger_lease_term_only: float = 0.0
    ger_with_fixturing: float = 0.0

    # Other metrics
    effective_term_years: float = 0.0
    incentives_pct_year1_gross: float = 0.0
    breakeven_months: float = 0.0

    # Breakeven analysis
    unlevered_breakeven_ner: float = 0.0
    io_levered_breakeven_ner: float = 0.0
    fully_levered_breakeven_ner: float = 0.0
    unlevered_breakeven_with_caprec: float = 0.0
    fully_levered_breakeven_with_caprec: float = 0.0
    sinking_fund_requirement_psf: float = 0.0

    # Detailed breakdowns
    rent_pv_by_year: List[float] = field(default_factory=list)
    cost_breakdown: dict = field(default_factory=dict)


class BAFCalculator:
    """Calculator for Business Approval Form lease analysis"""

    def __init__(self, terms: LeaseTerms):
        self.terms = terms
        self.monthly_discount_rate = terms.nominal_discount_rate / 12

    def calculate_pv(self, payment: float, periods: int, months_offset: int = 0) -> float:
        """
        Calculate present value of a payment stream

        Args:
            payment: Monthly payment amount
            periods: Number of periods (months)
            months_offset: Months already elapsed (for multi-year discounting)

        Returns:
            Present value
        """
        if periods == 0:
            return 0.0

        # PV formula: PV = payment * ((1 - (1 + r)^-n) / r) * (1 + r)
        # Excel PV with type=1 (payment at beginning of period)
        r = self.monthly_discount_rate
        pv = -npf.pv(r, periods, payment, 0, 1)  # type=1 for beginning of period

        # Discount for months already elapsed (using monthly compounding)
        # Excel formula: PV / (1 + monthly_rate)^months_elapsed
        if months_offset > 0:
            pv = pv / ((1 + r) ** months_offset)

        return pv

    def calculate_pmt(self, pv: float, periods: int, rate: Optional[float] = None) -> float:
        """
        Calculate payment from present value

        Args:
            pv: Present value
            periods: Number of periods
            rate: Interest rate (defaults to monthly discount rate)

        Returns:
            Periodic payment
        """
        if rate is None:
            rate = self.monthly_discount_rate

        # PMT formula with type=1 (payment at beginning of period)
        return -npf.pmt(rate, periods, pv, 0, 1)

    def calculate_rent_npv(self) -> tuple:
        """
        Calculate NPV of rent payments

        Returns:
            Tuple of (total_npv, pv_by_year)
        """
        rent_pvs = []
        cumulative_months = 0

        for i, (rent_psf, months) in enumerate(zip(
            self.terms.rent_schedule_psf[:10],
            self.terms.rent_period_months[:10]
        )):
            if months == 0:
                rent_pvs.append(0.0)
                continue

            # Calculate annual rent
            annual_rent = rent_psf * self.terms.area_sf

            # Calculate monthly payment
            monthly_payment = annual_rent / 12

            # Calculate PV for this period with monthly compounding discount
            # For year 2+, discount by the number of months that have already elapsed
            pv = self.calculate_pv(monthly_payment, int(months), cumulative_months)

            rent_pvs.append(pv)
            cumulative_months += months

        total_npv = sum(rent_pvs)
        return total_npv, rent_pvs

    def _calculate_industrial_commission(self, year1_pct: float, subsequent_pct: float) -> float:
        """
        Calculate PV of industrial-style commission (percentage of net rent per year)

        Industrial commissions are calculated as:
        - Year 1: year1_pct × Year 1 net rent
        - Years 2+: subsequent_pct × each subsequent year's net rent

        Each year's commission is discounted to PV based on when it's earned.
        Commissions are typically paid at lease signing (upfront), so we discount
        to month 0 for year 1, and to the start of each subsequent year.

        Args:
            year1_pct: Commission percentage for year 1 (e.g., 0.06 for 6%)
            subsequent_pct: Commission percentage for years 2+ (e.g., 0.02 for 2%)

        Returns:
            Total PV of commission payments
        """
        total_commission_pv = 0.0
        cumulative_months = 0

        for i, (rent_psf, months) in enumerate(zip(
            self.terms.rent_schedule_psf[:10],
            self.terms.rent_period_months[:10]
        )):
            if months == 0:
                break

            # Annual rent for this period
            annual_rent = rent_psf * self.terms.area_sf

            # Determine commission percentage
            commission_pct = year1_pct if i == 0 else subsequent_pct

            # Commission amount for this year
            commission = annual_rent * commission_pct

            # Discount to present value
            # Commission is paid at start of each year (month 0, 12, 24, etc.)
            if cumulative_months == 0:
                # Year 1 commission paid at signing (no discounting)
                commission_pv = commission
            else:
                # Subsequent commissions paid at start of each year
                # Discount from that point back to month 0
                discount_factor = (1 + self.monthly_discount_rate) ** cumulative_months
                commission_pv = commission / discount_factor

            total_commission_pv += commission_pv
            cumulative_months += months

            # Stop if we've reached the lease term
            if cumulative_months >= self.terms.lease_term_months:
                break

        return total_commission_pv

    def calculate_costs(self) -> dict:
        """
        Calculate present value of all costs

        Supports two commission methods:
        - Office: Flat $/sf per year (e.g., $2/sf × 5 years = $10/sf)
        - Industrial: Percentage of annual net rent (e.g., 6% year 1, 2% subsequent)

        Returns:
            Dictionary with cost breakdown
        """
        area = self.terms.area_sf

        costs = {
            'tenant_cash_allowance': self.terms.tenant_cash_allowance_psf * area,
            'landlord_work': self.terms.landlord_work,
            'amortized_tenant_work': self.terms.amortized_tenant_work,
            'pm_override_fee': self.terms.pm_override_fee,
        }

        # Calculate leasing commissions based on method
        # Check if industrial (percentage) method is being used
        using_industrial_method = (
            self.terms.listing_agent_year1_pct > 0 or
            self.terms.listing_agent_subsequent_pct > 0 or
            self.terms.tenant_rep_year1_pct > 0 or
            self.terms.tenant_rep_subsequent_pct > 0
        )

        if using_industrial_method:
            # Industrial method: Calculate percentage of each year's net rent
            listing_commission = self._calculate_industrial_commission(
                self.terms.listing_agent_year1_pct,
                self.terms.listing_agent_subsequent_pct
            )
            tenant_rep_commission = self._calculate_industrial_commission(
                self.terms.tenant_rep_year1_pct,
                self.terms.tenant_rep_subsequent_pct
            )
            costs['listing_agent'] = listing_commission
            costs['tenant_rep'] = tenant_rep_commission
        else:
            # Office method: Flat $/sf
            costs['listing_agent'] = self.terms.listing_agent_commission_psf * area
            costs['tenant_rep'] = self.terms.tenant_rep_commission_psf * area

        # Calculate PV of free rent
        # Note: calculate_pv returns positive PV, which represents cost to landlord
        if self.terms.net_free_rent_months > 0:
            year1_rent = self.terms.rent_schedule_psf[0]
            monthly_rent = (year1_rent * area) / 12
            costs['net_free_rent_pv'] = self.calculate_pv(
                monthly_rent,
                int(self.terms.net_free_rent_months)
            )
        else:
            costs['net_free_rent_pv'] = 0.0

        if self.terms.gross_free_rent_months > 0:
            year1_gross = self.terms.rent_schedule_psf[0] + self.terms.operating_costs_psf
            monthly_gross = (year1_gross * area) / 12
            costs['gross_free_rent_pv'] = self.calculate_pv(
                monthly_gross,
                int(self.terms.gross_free_rent_months)
            )
        else:
            costs['gross_free_rent_pv'] = 0.0

        # Convert to per sf for NPV calculation
        costs_psf = {k: -v / area for k, v in costs.items()}

        return costs, costs_psf

    def calculate_ner(self, npv_lease_deal_psf: float) -> tuple:
        """
        Calculate Net Effective Rent

        Args:
            npv_lease_deal_psf: NPV of lease deal per square foot

        Returns:
            Tuple of (ner_lease_term_only, ner_with_fixturing)
        """
        # NER for lease term only
        # Pass positive NPV; calculate_pmt will negate npf.pmt result to get positive rent
        ner_lease_term = self.calculate_pmt(
            npv_lease_deal_psf,
            self.terms.lease_term_months
        ) * 12

        # NER including fixturing period
        # More complex calculation accounting for free period during fixturing
        total_term = self.terms.lease_term_months + self.terms.fixturing_term_months

        # PV at start of fixturing
        pv_at_fixturing_start = self.calculate_pv(
            0,  # No payment during fixturing
            self.terms.fixturing_term_months
        )

        # PV of operating costs during fixturing
        monthly_op_costs = self.terms.operating_costs_psf / 12
        pv_op_costs_fixturing = -self.calculate_pv(
            monthly_op_costs,
            self.terms.fixturing_term_months
        )

        # Adjusted NPV for fixturing period calculation
        # This matches Excel formula: PMT(rate, total_term, PV(rate, fix_term, 0, npv) - PV(rate, fix_term, op_costs), 0, 1)
        pv1 = -npf.pv(self.monthly_discount_rate, self.terms.fixturing_term_months, 0, npv_lease_deal_psf, 0)
        pv2 = -npf.pv(self.monthly_discount_rate, self.terms.fixturing_term_months, monthly_op_costs, 0, 1)

        ner_with_fixturing = self.calculate_pmt(
            pv1 - pv2,  # Don't negate
            total_term
        ) * 12

        return ner_lease_term, ner_with_fixturing

    def calculate_ger(self, npv_net_rent_psf: float, costs_psf: dict) -> tuple:
        """
        Calculate Gross Effective Rent (includes operating costs)

        GER represents the TENANT's perspective: what they effectively pay.
        Includes: rent + operating costs - tenant benefits received
        Excludes: leasing commissions (landlord pays these, not tenant)

        IMPORTANT NUANCE: Net Free Rent vs Gross Free Rent
        - Net Free Rent: Tenant pays $0 base rent but DOES pay operating costs
        - Gross Free Rent: Tenant pays NOTHING (no base rent, no op costs)

        Args:
            npv_net_rent_psf: NPV of net rent per sf
            costs_psf: Cost breakdown per sf

        Returns:
            Tuple of (ger_lease_term_only, ger_with_fixturing)
        """
        # For GER, we need to add operating costs to the rent
        # Calculate NPV of operating costs
        monthly_op_costs = self.terms.operating_costs_psf / 12

        op_costs_pv = 0.0
        cumulative_months = 0

        for months in self.terms.rent_period_months[:10]:
            if months == 0:
                break
            pv = self.calculate_pv(monthly_op_costs, int(months), cumulative_months)
            op_costs_pv += pv
            cumulative_months += months

            if cumulative_months >= self.terms.lease_term_months:
                break

        # CRITICAL: If there's gross free rent, subtract the op costs during those months
        # because tenant didn't pay them (and they're included in gross_free_rent_pv benefit)
        # Net free rent doesn't require adjustment (tenant still pays op costs during net free rent)
        if self.terms.gross_free_rent_months > 0:
            op_costs_during_gross_free = self.calculate_pv(
                monthly_op_costs,
                int(self.terms.gross_free_rent_months)
            )
            # Subtract these from total op costs (avoid double-counting)
            op_costs_pv -= op_costs_during_gross_free

        # Total NPV for GER includes op costs (adjusted for gross free rent)
        npv_gross_psf = npv_net_rent_psf + op_costs_pv

        # TENANT BENEFITS ONLY (not landlord costs like commissions)
        # Tenant receives: TI allowance, landlord's work, free rent benefit
        # Tenant does NOT benefit from: listing commission, tenant rep commission, PM fees
        tenant_benefit_keys = [
            'tenant_cash_allowance',
            'landlord_work',
            'amortized_tenant_work',
            'net_free_rent_pv',
            'gross_free_rent_pv'
        ]

        tenant_benefits_psf = sum(v for k, v in costs_psf.items() if k in tenant_benefit_keys)
        npv_gross_deal_psf = npv_gross_psf + tenant_benefits_psf

        # Calculate GER
        ger_lease_term = self.calculate_pmt(
            npv_gross_deal_psf,  # Don't negate
            self.terms.lease_term_months
        ) * 12

        # GER with fixturing (simplified - similar to NER calculation)
        total_term = self.terms.lease_term_months + self.terms.fixturing_term_months
        ger_with_fixturing = self.calculate_pmt(
            npv_gross_deal_psf,  # Don't negate
            total_term
        ) * 12

        return ger_lease_term, ger_with_fixturing

    def calculate_breakeven_metrics(self) -> dict:
        """
        Calculate breakeven metrics for investment analysis

        Returns:
            Dictionary with breakeven calculations
        """
        # Calculate key ratios
        acquisition_cost_psf = self.terms.acquisition_cost / self.terms.gla_building_sf
        going_in_mortgage_psf = self.terms.going_in_ltv * acquisition_cost_psf
        going_in_equity_psf = (1 - self.terms.going_in_ltv) * acquisition_cost_psf

        # Mortgage yield
        mortgage_yield = self.terms.principal_payment_rate + self.terms.interest_cost

        # Breakeven calculations
        unlevered_breakeven = self.terms.dividend_yield * acquisition_cost_psf

        dividends_on_equity = self.terms.dividend_yield * going_in_equity_psf
        interest_on_loan = self.terms.interest_cost * going_in_mortgage_psf
        io_levered_breakeven = dividends_on_equity + interest_on_loan

        principal_payment = self.terms.principal_payment_rate * going_in_mortgage_psf
        fully_levered_breakeven = dividends_on_equity + interest_on_loan + principal_payment

        # Sinking fund requirement (capital recovery using Inwood method)
        # Allocate 40% of acquisition cost to building
        building_cost = self.terms.acquisition_cost * 0.40
        building_cost_per_sf = building_cost / self.terms.gla_building_sf

        # Remaining depreciation period (18 years assumed)
        remaining_years = 18
        remaining_months = remaining_years * 12

        # Calculate sinking fund using FV method (Inwood sinking fund)
        # This calculates: "What payment do we need to accumulate to the building cost?"
        # Excel formula: -PMT(rate, periods, 0, FV, 1) * 12
        # Use npf.pmt with FV parameter instead of PV
        monthly_sinking_fund_per_sf = -npf.pmt(
            self.monthly_discount_rate,
            remaining_months,
            0,  # PV = 0 (we're accumulating, not recovering)
            building_cost_per_sf,  # FV = target amount to accumulate
            1  # Annuity due
        )
        sinking_fund_psf = monthly_sinking_fund_per_sf * 12

        # Breakeven with capital recovery
        unlevered_with_caprec = unlevered_breakeven + sinking_fund_psf
        fully_levered_with_caprec = fully_levered_breakeven + sinking_fund_psf

        return {
            'unlevered_breakeven': unlevered_breakeven,
            'io_levered_breakeven': io_levered_breakeven,
            'fully_levered_breakeven': fully_levered_breakeven,
            'sinking_fund_requirement': sinking_fund_psf,
            'unlevered_with_caprec': unlevered_with_caprec,
            'fully_levered_with_caprec': fully_levered_with_caprec,
            'dividends_on_equity': dividends_on_equity,
            'interest_on_loan': interest_on_loan,
            'principal_payment': principal_payment,
        }

    def calculate_all(self) -> CalculationResults:
        """
        Perform all BAF calculations

        Returns:
            CalculationResults object with all metrics
        """
        results = CalculationResults()

        # 1. Calculate NPV of rent
        npv_net_rent, rent_pvs = self.calculate_rent_npv()
        npv_net_rent_psf = npv_net_rent / self.terms.area_sf

        results.npv_net_rent = npv_net_rent_psf
        results.rent_pv_by_year = rent_pvs

        # 2. Calculate costs
        costs, costs_psf = self.calculate_costs()
        total_costs_psf = sum(costs_psf.values())

        results.npv_costs = total_costs_psf
        results.cost_breakdown = costs

        # 3. NPV of lease deal
        npv_lease_deal_psf = npv_net_rent_psf + total_costs_psf
        results.npv_lease_deal = npv_lease_deal_psf

        # 4. Calculate NER
        ner_lease_term, ner_with_fixturing = self.calculate_ner(npv_lease_deal_psf)
        results.ner_lease_term_only = ner_lease_term
        results.ner_with_fixturing = ner_with_fixturing

        # 5. Calculate GER
        ger_lease_term, ger_with_fixturing = self.calculate_ger(npv_net_rent_psf, costs_psf)
        results.ger_lease_term_only = ger_lease_term
        results.ger_with_fixturing = ger_with_fixturing

        # 6. Calculate effective term
        if ner_lease_term != 0:
            results.effective_term_years = npv_lease_deal_psf / ner_lease_term

        # 7. Calculate incentives as % of year 1 gross rent
        year1_gross_rent = self.terms.rent_schedule_psf[0] + self.terms.operating_costs_psf
        total_incentives = (costs['tenant_cash_allowance'] +
                            costs['landlord_work'] +
                            costs['net_free_rent_pv'] +
                            costs['gross_free_rent_pv'])

        if year1_gross_rent != 0:
            results.incentives_pct_year1_gross = total_incentives / (year1_gross_rent * self.terms.area_sf)

        # 8. Breakeven on incentive recovery (months)
        year1_net_rent = self.terms.rent_schedule_psf[0]
        if year1_net_rent + self.terms.operating_costs_psf != 0:
            results.breakeven_months = total_incentives / ((year1_net_rent + self.terms.operating_costs_psf) * self.terms.area_sf / 12)

        # 9. Breakeven analysis
        breakeven = self.calculate_breakeven_metrics()
        results.unlevered_breakeven_ner = breakeven['unlevered_breakeven']
        results.io_levered_breakeven_ner = breakeven['io_levered_breakeven']
        results.fully_levered_breakeven_ner = breakeven['fully_levered_breakeven']
        results.sinking_fund_requirement_psf = breakeven['sinking_fund_requirement']
        results.unlevered_breakeven_with_caprec = breakeven['unlevered_with_caprec']
        results.fully_levered_breakeven_with_caprec = breakeven['fully_levered_with_caprec']

        return results


def format_currency(value: float) -> str:
    """Format value as currency"""
    return f"${value:,.2f}"


def format_percentage(value: float) -> str:
    """Format value as percentage"""
    return f"{value*100:.2f}%"


def load_from_json(json_path: str) -> LeaseTerms:
    """
    Load lease terms from JSON input file

    Args:
        json_path: Path to JSON input file

    Returns:
        LeaseTerms object
    """
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Parse lease start date if provided
    lease_start = None
    if 'lease_terms' in data and 'lease_start_date' in data['lease_terms']:
        date_str = data['lease_terms']['lease_start_date']
        if date_str:
            lease_start = datetime.strptime(date_str, '%Y-%m-%d').date()

    # Build LeaseTerms object
    terms = LeaseTerms(
        # Property info
        unit_number=data.get('property_info', {}).get('unit_number', ''),
        area_sf=data.get('property_info', {}).get('area_sf', 10000.0),

        # Tenant info
        tenant_name=data.get('tenant_info', {}).get('tenant_name', ''),
        trade_name=data.get('tenant_info', {}).get('trade_name', ''),

        # Lease terms
        lease_start_date=lease_start,
        lease_term_months=data.get('lease_terms', {}).get('lease_term_months', 120),
        operating_costs_psf=data.get('lease_terms', {}).get('operating_costs_psf', 0.0),
        fixturing_term_months=data.get('lease_terms', {}).get('fixturing_term_months', 0),

        # Rent schedule
        rent_schedule_psf=data.get('rent_schedule', {}).get('rent_psf_by_year', [0.0] * 10),
        rent_period_months=data.get('rent_schedule', {}).get('months_per_period', [12] * 10),

        # Incentives
        tenant_cash_allowance_psf=data.get('incentives', {}).get('tenant_cash_allowance_psf', 0.0),
        landlord_work=data.get('incentives', {}).get('landlord_work_total', 0.0),
        amortized_tenant_work=data.get('incentives', {}).get('amortized_tenant_work', 0.0),
        net_free_rent_months=data.get('incentives', {}).get('net_free_rent_months', 0.0),
        gross_free_rent_months=data.get('incentives', {}).get('gross_free_rent_months', 0.0),

        # Property type
        property_type=data.get('property_info', {}).get('property_type', 'industrial'),

        # Leasing costs (office method - flat $/sf)
        listing_agent_commission_psf=data.get('leasing_costs', {}).get('listing_agent_commission_psf', 0.0),
        tenant_rep_commission_psf=data.get('leasing_costs', {}).get('tenant_rep_commission_psf', 0.0),

        # Leasing costs (industrial method - percentage)
        listing_agent_year1_pct=data.get('leasing_costs', {}).get('listing_agent_year1_pct', 0.0),
        listing_agent_subsequent_pct=data.get('leasing_costs', {}).get('listing_agent_subsequent_pct', 0.0),
        tenant_rep_year1_pct=data.get('leasing_costs', {}).get('tenant_rep_year1_pct', 0.0),
        tenant_rep_subsequent_pct=data.get('leasing_costs', {}).get('tenant_rep_subsequent_pct', 0.0),

        pm_override_fee=data.get('leasing_costs', {}).get('pm_override_fee', 0.0),

        # Financial assumptions
        nominal_discount_rate=data.get('financial_assumptions', {}).get('nominal_discount_rate', 0.10),

        # Investment parameters
        gla_building_sf=data.get('property_info', {}).get('gla_building_sf',
                        data.get('investment_parameters', {}).get('gla_building_sf', 50000.0)),
        acquisition_cost=data.get('investment_parameters', {}).get('acquisition_cost', 0.0),
        going_in_ltv=data.get('investment_parameters', {}).get('going_in_ltv', 0.5),
        mortgage_amortization_months=data.get('investment_parameters', {}).get('mortgage_amortization_months', 300),
        dividend_yield=data.get('investment_parameters', {}).get('dividend_yield', 0.0675),
        interest_cost=data.get('investment_parameters', {}).get('interest_cost', 0.03),
        principal_payment_rate=data.get('investment_parameters', {}).get('principal_payment_rate', 0.027),
    )

    return terms


def save_results_to_file(terms: LeaseTerms, results: CalculationResults,
                         output_path: str, deal_name: str = "Lease Deal"):
    """
    Save calculation results to JSON file

    Args:
        terms: LeaseTerms object
        results: CalculationResults object
        output_path: Path for output file
        deal_name: Name of the deal
    """
    output = {
        'deal_name': deal_name,
        'calculation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'inputs': {
            'property': {
                'unit': terms.unit_number,
                'area_sf': terms.area_sf,
                'tenant': terms.tenant_name,
            },
            'lease_terms': {
                'term_months': terms.lease_term_months,
                'fixturing_months': terms.fixturing_term_months,
                'operating_costs_psf': terms.operating_costs_psf,
            },
            'rent_schedule_psf': terms.rent_schedule_psf[:10],
            'discount_rate': terms.nominal_discount_rate,
        },
        'results': {
            'npv_analysis': {
                'npv_net_rent_psf': round(results.npv_net_rent, 2),
                'npv_costs_psf': round(results.npv_costs, 2),
                'npv_lease_deal_psf': round(results.npv_lease_deal, 2),
            },
            'effective_rent': {
                'ner_lease_term_only': round(results.ner_lease_term_only, 2),
                'ner_with_fixturing': round(results.ner_with_fixturing, 2),
                'ger_lease_term_only': round(results.ger_lease_term_only, 2),
                'ger_with_fixturing': round(results.ger_with_fixturing, 2),
            },
            'metrics': {
                'effective_term_years': round(results.effective_term_years, 2),
                'incentives_pct_year1_gross': round(results.incentives_pct_year1_gross, 4),
                'breakeven_months': round(results.breakeven_months, 2),
            },
            'breakeven_analysis': {
                'unlevered_breakeven': round(results.unlevered_breakeven_ner, 2),
                'io_levered_breakeven': round(results.io_levered_breakeven_ner, 2),
                'fully_levered_breakeven': round(results.fully_levered_breakeven_ner, 2),
                'sinking_fund_requirement_psf': round(results.sinking_fund_requirement_psf, 2),
                'unlevered_with_caprec': round(results.unlevered_breakeven_with_caprec, 2),
                'fully_levered_with_caprec': round(results.fully_levered_breakeven_with_caprec, 2),
            },
            'investment_assessment': {
                'proposed_ner': round(results.ner_lease_term_only, 2),
                'meets_unlevered_breakeven': bool(results.ner_lease_term_only >= results.unlevered_breakeven_ner),
                'meets_io_levered_breakeven': bool(results.ner_lease_term_only >= results.io_levered_breakeven_ner),
                'meets_fully_levered_breakeven': bool(results.ner_lease_term_only >= results.fully_levered_breakeven_ner),
                'meets_unlevered_with_caprec': bool(results.ner_lease_term_only >= results.unlevered_breakeven_with_caprec),
                'meets_fully_levered_with_caprec': bool(results.ner_lease_term_only >= results.fully_levered_breakeven_with_caprec),
            },
            'cost_breakdown': {
                k: round(v, 2) for k, v in results.cost_breakdown.items()
            }
        }
    }

    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ Results saved to: {output_path}")


def print_results(terms: LeaseTerms, results: CalculationResults, deal_name: str = ""):
    """Print formatted results"""

    print("="*80)
    if deal_name:
        print(f"BUSINESS APPROVAL FORM (BAF) - {deal_name}")
    else:
        print("BUSINESS APPROVAL FORM (BAF) - CALCULATION RESULTS")
    print("="*80)
    print()

    print(f"Property: Unit {terms.unit_number}, {terms.area_sf:,.0f} sf")
    print(f"Tenant: {terms.tenant_name}")
    print(f"Lease Term: {terms.lease_term_months} months")
    print(f"Fixturing Period: {terms.fixturing_term_months} months")
    print(f"Operating Costs: ${terms.operating_costs_psf:.2f}/sf")
    print(f"Discount Rate: {format_percentage(terms.nominal_discount_rate)}")
    print()

    print("-"*80)
    print("NET PRESENT VALUE ANALYSIS")
    print("-"*80)
    print(f"NPV of Net Rent:        ${results.npv_net_rent:>12.2f} /sf")
    print(f"NPV of Costs:           ${results.npv_costs:>12.2f} /sf")
    print(f"NPV of Lease Deal:      ${results.npv_lease_deal:>12.2f} /sf")
    print()

    print("-"*80)
    print("EFFECTIVE RENT ANALYSIS")
    print("-"*80)
    print(f"NER (Lease Term Only):         ${results.ner_lease_term_only:>12.2f} /sf/year")
    print(f"NER (incl. Fixturing Period):  ${results.ner_with_fixturing:>12.2f} /sf/year")
    print(f"GER (Lease Term Only):         ${results.ger_lease_term_only:>12.2f} /sf/year")
    print(f"GER (incl. Fixturing Period):  ${results.ger_with_fixturing:>12.2f} /sf/year")
    print()
    print(f"Effective Term: {results.effective_term_years:.2f} years")
    print(f"Incentives as % of Year 1 Gross Rent: {format_percentage(results.incentives_pct_year1_gross)}")
    print(f"Breakeven on Incentive Recovery: {results.breakeven_months:.2f} months")
    print()

    print("-"*80)
    print("BREAKEVEN ANALYSIS")
    print("-"*80)
    print(f"Unlevered Breakeven NER:                ${results.unlevered_breakeven_ner:>12.2f} /sf/year")
    print(f"Interest-Only Levered Breakeven NER:    ${results.io_levered_breakeven_ner:>12.2f} /sf/year")
    print(f"Fully Levered Breakeven NER:            ${results.fully_levered_breakeven_ner:>12.2f} /sf/year")
    print()
    print(f"Sinking Fund Requirement:               ${results.sinking_fund_requirement_psf:>12.2f} /sf/year")
    print(f"Unlevered Breakeven w/ Cap Recovery:    ${results.unlevered_breakeven_with_caprec:>12.2f} /sf/year")
    print(f"Fully Levered Breakeven w/ Cap Recovery:${results.fully_levered_breakeven_with_caprec:>12.2f} /sf/year")
    print()

    print("-"*80)
    print("INVESTMENT ASSESSMENT")
    print("-"*80)

    # Compare NER to breakeven thresholds
    ner = results.ner_lease_term_only

    checks = [
        ("Unlevered Breakeven", results.unlevered_breakeven_ner),
        ("I/O Levered Breakeven", results.io_levered_breakeven_ner),
        ("Fully Levered Breakeven", results.fully_levered_breakeven_ner),
        ("Unlevered B/E w/CapRec", results.unlevered_breakeven_with_caprec),
        ("Fully Levered B/E w/CapRec", results.fully_levered_breakeven_with_caprec),
    ]

    for name, threshold in checks:
        status = "✓ MET" if ner >= threshold else "✗ FAIL"
        print(f"{name:40s} ${threshold:>8.2f}  {status}")

    print()
    print(f"Proposed Deal NER: ${ner:.2f}/sf/year")
    print()

    print("-"*80)
    print("COST BREAKDOWN")
    print("-"*80)
    for cost_name, cost_value in results.cost_breakdown.items():
        if cost_value != 0:
            print(f"{cost_name:40s} {format_currency(cost_value):>15s}")
    print()

    print("="*80)


# Example usage
if __name__ == "__main__":
    # Set up command-line argument parser
    parser = argparse.ArgumentParser(
        description='BAF Calculator - Business Approval Form for Lease Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with JSON input file
  python baf_calculator.py input_deal.json

  # Save results to specific output file
  python baf_calculator.py input_deal.json -o results.json

  # Use example files
  python baf_calculator.py baf_input_simple.json
  python baf_calculator.py baf_input_example.json
        """
    )

    parser.add_argument('input_file',
                        help='JSON input file with deal parameters (required)')
    parser.add_argument('-o', '--output', default=None,
                        help='Output file path for results (JSON)')
    parser.add_argument('--no-print', action='store_true',
                        help='Suppress console output')

    args = parser.parse_args()

    # Load from JSON file (required)
    try:
        # Load from JSON
        terms = load_from_json(args.input_file)

        # Extract deal name from JSON if available
        with open(args.input_file, 'r') as f:
            input_data = json.load(f)
            deal_name = input_data.get('deal_name', Path(args.input_file).stem)

        if not args.no_print:
            print(f"✓ Loaded input from: {args.input_file}\n")

    except FileNotFoundError:
        print(f"ERROR: Input file not found: {args.input_file}")
        print(f"\nUsage: python baf_calculator.py <input_file.json>")
        print(f"\nExample files:")
        print(f"  python baf_calculator.py baf_input_simple.json")
        print(f"  python baf_calculator.py baf_input_example.json")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in input file: {e}")
        print(f"\nValidate your JSON:")
        print(f"  python -m json.tool {args.input_file}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to load input file: {e}")
        sys.exit(1)

    # Calculate
    calculator = BAFCalculator(terms)
    results = calculator.calculate_all()

    # Print results to console
    if not args.no_print:
        print_results(terms, results, deal_name)

    # Save to output file if specified
    if args.output:
        save_results_to_file(terms, results, args.output, deal_name)
    elif args.input_file and not args.no_print:
        # Auto-generate output filename from input
        output_path = Path(args.input_file).stem + "_results.json"
        save_results_to_file(terms, results, output_path, deal_name)
