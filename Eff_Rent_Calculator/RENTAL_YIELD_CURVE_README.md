# Rental Rate Term Structure Calculator

A Python tool for calculating rental rates across different lease terms using the **implied termination option methodology**.

## Theoretical Foundation

**Original Paper**: Chan, R. (2016). "Deconstruction the Rental Rate Term Structure Model Using Implied Options." Draft 2016-02-12.

**Formal Academic Paper**: See `Rental_Term_Structure_Formal_Paper.md` (in this folder) for the complete mathematical treatment with LaTeX equations, proofs, and formal derivations.

## Overview

In commercial real estate, **longer lease terms command lower rents** (inverted yield curve). This is the opposite of interest rates where longer terms typically have higher rates. The reason:

- **Month-to-month leases** carry maximum landlord risk:
  - Space is tied up but can't be immediately re-leased
  - No forward visibility on rental income
  - Continuous search costs for replacement tenants
  - Tenant has maximum flexibility (valuable termination option)

- **Long-term leases** reduce landlord risk:
  - Predictable income stream
  - Lower search/vacancy costs
  - Tenant commitment

## The Methodology

### Key Insight

Unlike bonds where you can bootstrap forward rates, **commercial real estate has no forward lease market**. You cannot combine a 2-year spot rate with a 3-year forward rate to calculate a 5-year spot rate.

Instead, we use **implied termination options** to construct the rental yield curve.

### How It Works

Starting with a base case:
- **5-year spot rate**: $8.00/sf (market rate for longest term)
- **Month-to-month rate**: $10.00/sf (typically 125%-150% of base rate)
- **Discount rate**: 10% annually

To find the **4-year spot rate**:

1. Calculate NPV of: $8.00 for 48 months + $10.00 MTM for 12 months
2. Find rate X where: NPV of X for 60 months = that NPV
3. X = $8.32/sf = the 4-year spot rate

**Interpretation**: A tenant signing a 5-year lease at $8.32 with the option to terminate after 4 years is equivalent in value to signing a 4-year lease at $8.00 and then rolling month-to-month at $10.00.

Repeat this process for every term from 1 month to 60 months.

## Installation

```bash
cd Eff_Rent_Calculator
# No additional dependencies beyond numpy and numpy-financial
```

## Usage

### Basic Usage (Default Parameters)

```bash
python3 rental_yield_curve.py
```

**Output**: Yield curve for 5-year base at $8.00, MTM at 125%, 10% discount

### Custom Parameters

```bash
python3 rental_yield_curve.py \
  --base-term 120 \
  --base-rate 15.00 \
  --mtm-multiplier 1.40 \
  --discount-rate 0.08
```

### Generate Curve for All Months

```bash
python3 rental_yield_curve.py --all-months
```

Generates rates for every single month from 1 to base term (e.g., all 60 months).

### Save to Custom Output File

```bash
python3 rental_yield_curve.py -o my_custom_curve.json
```

## Example Output

```
================================================================================
RENTAL RATE TERM STRUCTURE (YIELD CURVE)
================================================================================

Base Case:
  60-Month Spot Rate: $8.00/sf/year
  Month-to-Month Rate: $10.00/sf/year (125% of base)
  Discount Rate: 10.00% annually (0.8333% monthly)

--------------------------------------------------------------------------------
Term                 Rate ($/sf/year)     Change          % Change
--------------------------------------------------------------------------------
1 Month (MTM)        $10.00              $+2.00          +25.00%
3 Months             $9.87               $+1.87          +23.43%
6 Months             $9.75               $+1.75          +21.90%
9 Months             $9.63               $+1.63          +20.41%
1 Year               $9.52               $+1.52          +18.96%
18 Months (1.5 yrs)  $9.29               $+1.29          +16.16%
2 Years              $9.08               $+1.08          +13.49%
3 Years              $8.68               $+0.68          +8.54%
4 Years              $8.32               $+0.32          +4.06%
5 Years              $8.00               $+0.00          +0.00%
================================================================================
```

## Validation Against Paper

The calculator has been validated against the original paper's examples:

| Term | Paper Rate | Calculator | Match |
|------|------------|------------|-------|
| 5-Year | $8.00 | $8.00 | ✓ |
| 4-Year | $8.32 | $8.32 | ✓ |
| 3-Year | $8.68 | $8.68 | ✓ |
| 2-Year | $9.08 | $9.08 | ✓ |
| 18-Month | $9.29 | $9.29 | ✓ |
| 12-Month | $9.52 | $9.52 | ✓ |
| 9-Month | $9.63 | $9.63 | ✓ |
| 6-Month | $9.75 | $9.75 | ✓ |
| 3-Month | $9.87 | $9.87 | ✓ |
| 1-Month | $10.00 | $10.00 | ✓ |

**100% accuracy** across all test cases.

## Use Cases

### 1. Lease Negotiation

**Scenario**: Tenant wants 3-year term instead of proposed 5-year term.

**Without yield curve**: Guess at appropriate rent adjustment
**With yield curve**: Know that 3-year rate should be $8.68 vs. $8.00 for 5-year (+8.5%)

### 2. Offer Menu

**Scenario**: Present tenant with multiple term options at proper pricing.

**Example**:
- 5 years at $8.00/sf
- 4 years at $8.32/sf
- 3 years at $8.68/sf
- 2 years at $9.08/sf

### 3. Renewal Negotiations

**Scenario**: Existing tenant on 3-year lease wants to renew for only 1 year.

**With yield curve**: Know the appropriate premium for the shorter renewal term.

### 4. Portfolio Analysis

**Scenario**: Understand pricing across different lease terms in your portfolio.

## Caveats and Limitations

As noted in the original paper:

1. **Incentives excluded**: TI allowances and free rent deliberately excluded for clarity. Can be layered on top but changes math slightly.

2. **Commissions excluded**: Not normally paid on MTM leases. Including them would change true NER.

3. **Negotiation reality**: Tenant may not be as financially sophisticated. Use as guideline, not absolute pricing.

4. **No market assumptions**: No inflation or changing market conditions assumed during term.

5. **Simplified option model**: Uses practical approach rather than complex Black-Scholes. Tenant's termination right is:
   - Not a pure European option (can't exercise only at end)
   - Not a pure American option (can't sell lease back)
   - A go-forward monthly rollover right

## JSON Output Format

```json
{
  "calculation_date": "2025-10-30 19:45:00",
  "inputs": {
    "base_term_months": 60,
    "base_rate_psf": 8.00,
    "mtm_multiplier": 1.25,
    "mtm_rate_psf": 10.00,
    "discount_rate": 0.10
  },
  "yield_curve": [
    {
      "term_months": 48,
      "term_years": 4.0,
      "rate_psf": 8.32,
      "change_from_base": 0.32,
      "pct_change_from_base": 0.0406
    },
    ...
  ]
}
```

## Command-Line Arguments

```
--base-term MONTHS        Base lease term in months (default: 60)
--base-rate RATE          Base term rental rate $/sf/year (default: 8.00)
--mtm-multiplier MULT     MTM rate as multiple of base (default: 1.25 = 125%)
--discount-rate RATE      Annual discount rate (default: 0.10 = 10%)
--all-months              Generate rates for all months (not just key terms)
-o, --output FILE         Output JSON file path
```

## Technical Details

### NPV Calculation

- Uses **annuity due** (type=1) - payments at beginning of period
- **Monthly compounding** for all cash flows
- Consistent with `eff_rent_calculator.py` methodology

### Algorithm

```python
# For N-month term:
1. pv_firm = PV(base_rate for N months)
2. pv_mtm = PV(MTM rate for (base_term - N) months, starting at month N+1)
3. target_pv = pv_firm + pv_mtm
4. term_rate = annualized_pmt(target_pv, base_term months)
```

## Integration with NER Calculator

The rental yield curve can inform the **Net Effective Rent calculator** (`eff_rent_calculator.py`) by:

1. Providing market-appropriate base rents for different terms
2. Validating proposed rents against term structure
3. Calculating opportunity cost of shorter vs. longer terms

## References

1. Chan, R. (2016). "Deconstruction the Rental Rate Term Structure Model Using Implied Options." Draft 2016-02-12.

2. Chan, R. (2015). "Understanding the Ponzi Rental Rate: The Challenges with Using Net Effective Rents to Analyze Prospective Lease Deals within Real Estate Investment Trusts." *Real Estate Finance*, Vol. 32, No. 2, pp. 48-61.

---

**Last Updated**: 2025-10-30
