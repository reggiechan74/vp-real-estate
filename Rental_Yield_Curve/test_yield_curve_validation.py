"""
Validation Test for Rental Yield Curve Calculator

Validates calculator output against the original paper:
Chan, R. (2016). "Deconstruction the Rental Rate Term Structure Model Using Implied Options."

All values are from the paper's Example (page 4, Summary table).
"""

from rental_yield_curve import RentalYieldCurveCalculator, YieldCurveInputs


def test_paper_validation():
    """
    Validate calculator against all values from the paper's summary table

    Expected values from paper (page 4):
    - 5-Year Spot Rate: $8.00 (base case)
    - 4-Year Spot Rate: $8.32 ($0.32 change, 4.06%)
    - 3-Year Spot Rate: $8.68 ($0.36 change, 4.31%)
    - 2-Year Spot Rate: $9.08 ($0.40 change, 4.56%)
    - 18 Month Spot Rate: $9.29 ($0.21 change, 2.35%)
    - 12 Month Spot Rate: $9.52 ($0.22 change, 2.41%)
    - 9 Month Spot Rate: $9.63 ($0.12 change, 1.22%)
    - 6 Month Spot Rate: $9.75 ($0.12 change, 1.24%)
    - 3 Month Spot Rate: $9.87 ($0.12 change, 1.25%)
    - 1 Month Spot Rate: $10.00 ($0.13 change, 1.27%)
    """

    # Setup inputs matching the paper
    inputs = YieldCurveInputs(
        base_term_months=60,  # 5 years
        base_rate_psf=8.00,
        mtm_multiplier=1.25,  # 125% = $10.00
        nominal_discount_rate=0.10  # 10%
    )

    calc = RentalYieldCurveCalculator(inputs)

    # Expected values from paper
    test_cases = [
        # (term_months, expected_rate, expected_change, expected_pct_change)
        (60, 8.00, 0.00, 0.0000),  # 5-Year (base)
        (48, 8.32, 0.32, 0.0406),  # 4-Year
        (36, 8.68, 0.68, 0.0850),  # 3-Year (paper shows $0.36 change from 4Y, $0.68 from base)
        (24, 9.08, 1.08, 0.1350),  # 2-Year
        (18, 9.29, 1.29, 0.1613),  # 18 Month
        (12, 9.52, 1.52, 0.1900),  # 12 Month
        (9, 9.63, 1.63, 0.2038),   # 9 Month
        (6, 9.75, 1.75, 0.2188),   # 6 Month
        (3, 9.87, 1.87, 0.2338),   # 3 Month
        (1, 10.00, 2.00, 0.2500),  # 1 Month (MTM)
    ]

    print("\n" + "="*100)
    print("VALIDATION TEST: Rental Yield Curve Calculator vs. Paper")
    print("="*100)
    print(f"\nPaper Reference: Chan (2016) - Summary Table (Page 4)")
    print(f"\nBase Case: 5-year at $8.00/sf, MTM at $10.00/sf (125%), 10% discount\n")
    print("-"*100)
    print(f"{'Term':<15} {'Paper Rate':<15} {'Calc Rate':<15} {'Match':<10} {'Change':<15} {'% Change':<15}")
    print("-"*100)

    all_pass = True
    tolerance = 0.01  # Allow $0.01/sf tolerance for rounding

    for term_months, expected_rate, expected_change, expected_pct in test_cases:
        actual_rate = calc.calculate_term_rate(term_months)
        actual_change = actual_rate - 8.00
        actual_pct = actual_change / 8.00

        # Check if within tolerance
        rate_match = abs(actual_rate - expected_rate) < tolerance
        change_match = abs(actual_change - expected_change) < tolerance

        match_str = "✓ PASS" if rate_match and change_match else "✗ FAIL"
        if not (rate_match and change_match):
            all_pass = False

        # Format term
        if term_months == 60:
            term_str = "5 Years"
        elif term_months == 48:
            term_str = "4 Years"
        elif term_months == 36:
            term_str = "3 Years"
        elif term_months == 24:
            term_str = "2 Years"
        elif term_months == 18:
            term_str = "18 Months"
        elif term_months == 12:
            term_str = "12 Months"
        elif term_months < 12:
            term_str = f"{term_months} Months"
        else:
            term_str = f"{term_months}mo"

        print(f"{term_str:<15} ${expected_rate:<14.2f} ${actual_rate:<14.2f} {match_str:<10} "
              f"${actual_change:<14.2f} {actual_pct:<14.2%}")

    print("-"*100)

    if all_pass:
        print("\n✓ ALL TESTS PASSED - Calculator matches paper exactly!")
        print("\nValidation: 100% accuracy across all 10 test cases")
    else:
        print("\n✗ SOME TESTS FAILED - Calculator does not match paper")

    print("="*100 + "\n")

    assert all_pass


def test_npv_calculation():
    """
    Validate the specific NPV calculation from the paper (page 2)

    Paper shows for 4-year calculation:
    - Years 1-4: $8.00/sf ($0.67/month)
    - Year 5: $10.00/sf ($0.83/month)
    - Present values: $7.65, $6.92, $6.27, $5.67, $6.42
    - Total NPV: $32.92
    - Equivalent 5-year rate: $8.32
    """

    inputs = YieldCurveInputs(
        base_term_months=60,
        base_rate_psf=8.00,
        mtm_multiplier=1.25,
        nominal_discount_rate=0.10
    )

    calc = RentalYieldCurveCalculator(inputs)

    print("\n" + "="*80)
    print("NPV CALCULATION VALIDATION (Paper Page 2)")
    print("="*80)
    print("\nScenario: 4 years at $8.00, then 1 year at $10.00 MTM")
    print("\nExpected from paper:")
    print("  Year 1-4 PVs: $7.65, $6.92, $6.27, $5.67")
    print("  Year 5 PV: $6.42")
    print("  Total NPV: $32.92")
    print("  Equivalent 5-year rate: $8.32")

    # Calculate PV of 4 years at $8.00
    pv_firm = calc.calculate_pv(8.00, 48)

    # Calculate PV of 1 year at $10.00 starting at month 49
    pv_mtm = calc.calculate_pv(10.00, 12, 48)

    # Total NPV
    total_npv = pv_firm + pv_mtm

    # Equivalent rate over 60 months
    equiv_rate = calc.calculate_pmt_from_pv(total_npv, 60)

    print(f"\nCalculator results:")
    print(f"  PV of 48 months at $8.00: ${pv_firm:.2f}")
    print(f"  PV of 12 months at $10.00: ${pv_mtm:.2f}")
    print(f"  Total NPV: ${total_npv:.2f}")
    print(f"  Equivalent 5-year rate: ${equiv_rate:.2f}")

    # Check against paper
    npv_match = abs(total_npv - 32.92) < 0.10  # Allow $0.10 tolerance
    rate_match = abs(equiv_rate - 8.32) < 0.01  # Allow $0.01 tolerance

    if npv_match and rate_match:
        print(f"\n✓ NPV calculation matches paper!")
    else:
        print(f"\n✗ NPV calculation does not match paper")
        print(f"  NPV diff: ${abs(total_npv - 32.92):.2f}")
        print(f"  Rate diff: ${abs(equiv_rate - 8.32):.2f}")

    print("="*80 + "\n")

    assert npv_match and rate_match


if __name__ == '__main__':
    print("\n" + "#"*100)
    print("RENTAL YIELD CURVE CALCULATOR - VALIDATION SUITE")
    print("#"*100)

    # Run validation tests
    test1_pass = test_npv_calculation()
    test2_pass = test_paper_validation()

    # Summary
    print("\n" + "="*100)
    print("VALIDATION SUMMARY")
    print("="*100)
    print(f"NPV Calculation Test: {'✓ PASS' if test1_pass else '✗ FAIL'}")
    print(f"Full Yield Curve Test: {'✓ PASS' if test2_pass else '✗ FAIL'}")

    if test1_pass and test2_pass:
        print(f"\n{'✓'*3} ALL VALIDATION TESTS PASSED {'✓'*3}")
        print("\nThe calculator produces results identical to the paper's methodology.")
    else:
        print(f"\n{'✗'*3} SOME VALIDATION TESTS FAILED {'✗'*3}")

    print("="*100 + "\n")
