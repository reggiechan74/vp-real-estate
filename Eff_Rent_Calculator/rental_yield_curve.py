"""
Rental Rate Term Structure Calculator
Based on Implied Termination Options

Theoretical Foundation:
-----------------------
Chan, R. (2016). "Deconstruction the Rental Rate Term Structure Model
Using Implied Options." Draft 2016-02-12.

This calculator generates a rental "yield curve" showing appropriate rental rates
for different lease terms based on the concept of implied termination options.

Key Concept:
------------
The longer the lease term, the lower the rent (inverted yield curve). Landlords
charge a premium for shorter terms because:
- Greater leasing risk (search costs for new tenant)
- No forward visibility on rental income
- Tenant has maximum flexibility (valuable option to terminate)

Method:
-------
Starting with a base case (e.g., 5-year rate at $8.00/sf and MTM rate at $10.00/sf),
we calculate shorter term rates by working backwards:

- 4-year rate = 5-year rate with option to terminate after year 4
- Landlord indifferent between:
  * $8.00/sf for 4 years, then $10.00/sf MTM for 1 year
  * $X/sf for 5 years with monthly termination option after year 4

The $X that makes these equivalent is the 4-year spot rate.

Usage:
------
python3 rental_yield_curve.py --base-term 60 --base-rate 8.00 --mtm-multiplier 1.25 --discount-rate 0.10
"""

import numpy as np
import numpy_financial as npf
from dataclasses import dataclass
from typing import List, Dict
import argparse
import json
from datetime import datetime


@dataclass
class YieldCurveInputs:
    """Input parameters for rental yield curve calculation"""
    base_term_months: int = 60  # Longest term available (e.g., 5 years = 60 months)
    base_rate_psf: float = 8.00  # Market rate for base term
    mtm_multiplier: float = 1.25  # MTM rate as multiple of base (typically 1.25-1.50)
    nominal_discount_rate: float = 0.10  # Annual discount rate (10%)

    @property
    def mtm_rate_psf(self) -> float:
        """Month-to-month rate (typically 125%-150% of base)"""
        return self.base_rate_psf * self.mtm_multiplier

    @property
    def monthly_discount_rate(self) -> float:
        """Monthly discount rate"""
        return self.nominal_discount_rate / 12


@dataclass
class TermStructurePoint:
    """Single point on the rental yield curve"""
    term_months: int
    rate_psf: float
    change_from_base: float
    pct_change_from_base: float

    @property
    def term_years(self) -> float:
        """Term in years"""
        return self.term_months / 12


class RentalYieldCurveCalculator:
    """
    Calculate rental rates for all lease terms using implied termination options

    The methodology works backwards from the longest term:
    1. Base term (e.g., 60 months) has market rate (e.g., $8.00/sf)
    2. MTM rate is premium multiple (e.g., 125% = $10.00/sf)
    3. For each shorter term, find rate that creates NPV equivalence:
       - Pay shorter rate for N months, then MTM for remainder
       - This equals paying base rate for full term
    """

    def __init__(self, inputs: YieldCurveInputs):
        self.inputs = inputs
        self.monthly_rate = inputs.monthly_discount_rate

    def calculate_pv(self, payment_psf: float, months: int, offset_months: int = 0) -> float:
        """
        Calculate present value of monthly rent stream

        Args:
            payment_psf: Monthly rent per square foot
            months: Number of months
            offset_months: Months to discount back (for future cash flows)

        Returns:
            Present value per square foot
        """
        if months == 0:
            return 0.0

        # Annualize the payment for input (payment is annual $/sf)
        monthly_payment = payment_psf / 12

        # PV with annuity due (type=1, payment at beginning of period)
        pv = -npf.pv(self.monthly_rate, months, monthly_payment, 0, 1)

        # Discount for offset
        if offset_months > 0:
            pv = pv / ((1 + self.monthly_rate) ** offset_months)

        return pv

    def calculate_pmt_from_pv(self, pv_psf: float, months: int) -> float:
        """
        Calculate annual payment per sf from present value

        Args:
            pv_psf: Present value per square foot
            months: Number of months

        Returns:
            Annual rent per square foot
        """
        # Calculate monthly payment
        monthly_payment = -npf.pmt(self.monthly_rate, months, pv_psf, 0, 1)

        # Annualize
        return monthly_payment * 12

    def calculate_term_rate(self, term_months: int) -> float:
        """
        Calculate rental rate for a specific term using implied options

        Logic (from paper):
        -------------------
        A tenant willing to pay the N-month rate for N months, then roll MTM for
        the remainder, should produce the same NPV as paying the base rate for
        the full base term.

        Example: If 5-year rate is $8.00 and MTM is $10.00:
        - 4-year rate X is found where: NPV(X for 48mo + $10 for 12mo) = NPV($8 for 60mo)
        - Answer: X = $8.32

        The N-month spot rate must be HIGHER than the base rate (inverted curve).

        Args:
            term_months: Lease term in months

        Returns:
            Annual rental rate per square foot
        """
        if term_months >= self.inputs.base_term_months:
            return self.inputs.base_rate_psf

        if term_months <= 1:
            return self.inputs.mtm_rate_psf

        # Calculate NPV of: base rate for N months + MTM for remainder
        pv_firm_period = self.calculate_pv(
            self.inputs.base_rate_psf,
            term_months
        )

        mtm_months = self.inputs.base_term_months - term_months
        pv_mtm_period = self.calculate_pv(
            self.inputs.mtm_rate_psf,
            mtm_months,
            term_months  # Discount back from future start
        )

        # Total NPV of this blended cash flow
        target_pv = pv_firm_period + pv_mtm_period

        # Find rate X where: NPV(X for base_term months) = target_pv
        # This X is the N-month spot rate (rate for base term with N-month termination option)
        term_rate = self.calculate_pmt_from_pv(target_pv, self.inputs.base_term_months)

        return term_rate

    def generate_yield_curve(self, terms_list: List[int] = None) -> List[TermStructurePoint]:
        """
        Generate complete rental yield curve

        Args:
            terms_list: List of terms (in months) to calculate. If None, uses standard terms.

        Returns:
            List of TermStructurePoint objects
        """
        if terms_list is None:
            # Standard terms: every month for first year, then major milestones
            terms_list = [
                1, 3, 6, 9, 12,  # Monthly to 1 year
                18, 24, 36, 48,  # 1.5, 2, 3, 4 years
                self.inputs.base_term_months  # Base term
            ]
            # Remove any terms longer than base
            terms_list = [t for t in terms_list if t <= self.inputs.base_term_months]

        curve = []
        base_rate = self.inputs.base_rate_psf

        for term in sorted(terms_list):
            rate = self.calculate_term_rate(term)
            change = rate - base_rate
            pct_change = (change / base_rate) if base_rate != 0 else 0.0

            point = TermStructurePoint(
                term_months=term,
                rate_psf=rate,
                change_from_base=change,
                pct_change_from_base=pct_change
            )
            curve.append(point)

        return curve

    def generate_full_curve_all_months(self) -> List[TermStructurePoint]:
        """
        Generate yield curve for every single month from 1 to base_term

        Returns:
            List of TermStructurePoint for all months
        """
        all_months = list(range(1, self.inputs.base_term_months + 1))
        return self.generate_yield_curve(all_months)


def print_yield_curve(curve: List[TermStructurePoint], inputs: YieldCurveInputs):
    """Print formatted yield curve table"""

    print("\n" + "="*80)
    print("RENTAL RATE TERM STRUCTURE (YIELD CURVE)")
    print("="*80)
    print(f"\nBase Case:")
    print(f"  {inputs.base_term_months}-Month Spot Rate: ${inputs.base_rate_psf:.2f}/sf/year")
    print(f"  Month-to-Month Rate: ${inputs.mtm_rate_psf:.2f}/sf/year ({inputs.mtm_multiplier:.0%} of base)")
    print(f"  Discount Rate: {inputs.nominal_discount_rate:.2%} annually ({inputs.monthly_discount_rate:.4%} monthly)")

    print("\n" + "-"*80)
    print(f"{'Term':<20} {'Rate ($/sf/year)':<20} {'Change':<15} {'% Change':<15}")
    print("-"*80)

    for point in curve:
        if point.term_months == 1:
            term_str = f"{point.term_months} Month (MTM)"
        elif point.term_months < 12:
            term_str = f"{point.term_months} Months"
        elif point.term_months == 12:
            term_str = f"1 Year"
        elif point.term_months % 12 == 0:
            term_str = f"{point.term_months // 12} Years"
        else:
            term_str = f"{point.term_months} Months ({point.term_years:.1f} yrs)"

        change_str = f"${point.change_from_base:+.2f}"
        pct_str = f"{point.pct_change_from_base:+.2%}"

        print(f"{term_str:<20} ${point.rate_psf:<18.2f} {change_str:<15} {pct_str:<15}")

    print("="*80)


def save_results_to_json(curve: List[TermStructurePoint], inputs: YieldCurveInputs, output_path: str):
    """Save yield curve results to JSON file"""

    output = {
        "calculation_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "inputs": {
            "base_term_months": inputs.base_term_months,
            "base_rate_psf": inputs.base_rate_psf,
            "mtm_multiplier": inputs.mtm_multiplier,
            "mtm_rate_psf": inputs.mtm_rate_psf,
            "discount_rate": inputs.nominal_discount_rate,
        },
        "yield_curve": [
            {
                "term_months": point.term_months,
                "term_years": point.term_years,
                "rate_psf": round(point.rate_psf, 2),
                "change_from_base": round(point.change_from_base, 2),
                "pct_change_from_base": round(point.pct_change_from_base, 4),
            }
            for point in curve
        ]
    }

    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ Results saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Calculate rental rate term structure using implied termination options',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Default 5-year base at $8.00/sf, 125% MTM, 10% discount
  python3 rental_yield_curve.py

  # Custom parameters
  python3 rental_yield_curve.py --base-term 120 --base-rate 15.00 --mtm-multiplier 1.40 --discount-rate 0.08

  # Generate curve for all months (1-60)
  python3 rental_yield_curve.py --all-months

  # Save to specific output file
  python3 rental_yield_curve.py -o my_yield_curve.json
        """
    )

    parser.add_argument('--base-term', type=int, default=60,
                       help='Base lease term in months (default: 60)')
    parser.add_argument('--base-rate', type=float, default=8.00,
                       help='Base term rental rate $/sf/year (default: 8.00)')
    parser.add_argument('--mtm-multiplier', type=float, default=1.25,
                       help='MTM rate as multiple of base (default: 1.25 = 125%%)')
    parser.add_argument('--discount-rate', type=float, default=0.10,
                       help='Annual discount rate (default: 0.10 = 10%%)')
    parser.add_argument('--all-months', action='store_true',
                       help='Generate rates for all months (not just key terms)')
    parser.add_argument('-o', '--output', type=str,
                       help='Output JSON file path (default: rental_yield_curve_results.json)')

    args = parser.parse_args()

    # Create inputs
    inputs = YieldCurveInputs(
        base_term_months=args.base_term,
        base_rate_psf=args.base_rate,
        mtm_multiplier=args.mtm_multiplier,
        nominal_discount_rate=args.discount_rate
    )

    # Create calculator
    calc = RentalYieldCurveCalculator(inputs)

    # Generate curve
    if args.all_months:
        curve = calc.generate_full_curve_all_months()
        print(f"\n✓ Generated yield curve for all {len(curve)} months")
    else:
        curve = calc.generate_yield_curve()

    # Print results
    print_yield_curve(curve, inputs)

    # Save to JSON
    output_path = args.output or 'rental_yield_curve_results.json'
    save_results_to_json(curve, inputs, output_path)


if __name__ == '__main__':
    main()
