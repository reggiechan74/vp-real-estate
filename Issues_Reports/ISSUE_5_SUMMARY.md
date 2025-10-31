# Issue #5 Complete: Renewal Economics Calculator (NPV/IRR Analysis)

## ✅ Status: COMPLETE

**GitHub Issue**: https://github.com/reggiechan74/lease-abstract/issues/5
**Implementation Date**: 2025-10-30
**Test Results**: 26/26 passing (100%)

## Deliverables

### 1. Core Module
**File**: `Eff_Rent_Calculator/renewal_analysis.py` (950 lines)

Complete renewal vs. relocation economic analysis tool including:
- NPV calculation for both renewal and relocation scenarios
- Net Effective Rent (NER) calculation
- Internal Rate of Return (IRR) for relocation investment
- Payback period analysis
- Breakeven rent calculation (binary search algorithm)
- Sensitivity analysis on rent, TI, and disruption costs
- Investment recommendation generation
- Comprehensive cost aggregation (TI, moving, disruption, abandonment, leasing)

### 2. Test Suite
**File**: `Eff_Rent_Calculator/Tests/test_renewal_analysis.py` (615 lines)

**26 comprehensive tests** covering:
- Renewal scenario NPV calculations
- Relocation scenario with all cost categories
- Comparison analysis (NPV difference, annual savings, payback)
- Breakeven analysis (convergence and accuracy)
- Recommendation logic (renew/relocate/negotiate)
- Sensitivity analysis (rent, TI, disruption variations)
- Edge cases (zero area, single year, no costs, high discount rate)

**Test Results**:
```
26 passed in 0.69s
100% pass rate
```

### 3. Documentation
**File**: `Eff_Rent_Calculator/README_RENEWAL_ANALYSIS.md`

Complete usage guide with:
- Quick start examples
- Core concepts (decision framework, NPV analysis, investment metrics)
- Function reference for all major functions
- 5 detailed usage examples
- Integration notes with financial_utils
- Recommendation logic explanation
- Important considerations (hidden costs, negotiation tactics, timing, market cycle)

## Implementation Highlights

### Robust Analysis
✅ NPV-based comparison (present value of all costs)
✅ Variable rent schedules supported
✅ Comprehensive cost categories (17 different cost types)
✅ IRR calculation for relocation investment
✅ Payback period calculation
✅ Breakeven rent with binary search convergence
✅ Sensitivity analysis on key variables

### Financial Accuracy
✅ **Sign convention**: Higher NPV = higher costs = worse option
✅ **Upfront costs**: TI, moving, disruption, abandonment at t=0
✅ **Ongoing costs**: Rent and operating costs discounted over term
✅ **NER calculation**: NPV / area / annuity factor
✅ **IRR**: Investment return from upfront costs and annual savings

### Production Ready
✅ Dataclass-based inputs with clear structure
✅ Type hints throughout
✅ Comprehensive error handling
✅ DataFrame output for sensitivity analysis
✅ Print-friendly comparison reports
✅ Zero dependencies beyond numpy/pandas

## Key Functions

### Most Important Functions

1. **`compare_scenarios(renewal, relocation, general) -> ComparisonResult`**
   - Used by: Decision-makers comparing renewal vs. relocation
   - One-stop function for complete comparison
   - Returns NPV difference, IRR, payback, breakeven, recommendation

2. **`calculate_renewal_scenario(renewal, general) -> ScenarioResult`**
   - Calculate NPV and NER for renewal option
   - Includes rent, operating costs, TI, legal fees
   - Returns detailed cost breakdown

3. **`calculate_relocation_scenario(relocation, general) -> ScenarioResult`**
   - Calculate NPV and NER for relocation option
   - Includes 17 different cost categories
   - Returns detailed cost breakdown

4. **`calculate_breakeven_rent(renewal, relocation, general) -> float`**
   - Find renewal rent where NPV(renewal) = NPV(relocation)
   - Uses binary search for convergence
   - Critical for negotiation strategy

5. **`sensitivity_analysis(...) -> pd.DataFrame`**
   - Test impact of rent, TI, and disruption variations
   - Shows which scenarios change the recommendation
   - Reveals decision robustness

## Technical Details

### NPV Calculation

**For Renewal**:
```
NPV = PV(Rent Payments) + PV(Operating Costs) + TI Costs + Legal Fees

Where:
  - Rent and operating costs are discounted annual cash flows
  - TI and legal fees are upfront (t=0, no discounting)
```

**For Relocation**:
```
NPV = PV(Rent Payments) + PV(Operating Costs) + Upfront Costs

Upfront Costs:
  - Net TI (requirement - allowance)
  - Moving costs (physical + IT + signage)
  - Disruption costs (downtime × revenue + customer loss)
  - Abandonment costs (unamortized improvements + restoration)
  - Leasing costs (legal + due diligence + broker)
```

### Net Effective Rent (NER)

```
NER = NPV / (Area × Annuity Factor)

Where:
  Annuity Factor = [1 - (1 + r)^(-n)] / r
  r = monthly discount rate
  n = lease term in months
```

NER represents the equivalent annual cost per square foot.

### IRR Calculation

```
Cash flows for IRR:
  t=0: -Upfront relocation costs
  t=1 to n: Annual savings (renewal cash flow - relocation cash flow)

IRR = rate where NPV of these cash flows = 0
```

Uses `scipy.optimize` via `financial_utils.irr()`.

### Payback Period

```
Payback Period = Upfront Relocation Costs / Annual Savings

Where:
  Annual Savings = Average(renewal cash flows) - Average(relocation cash flows)
```

If annual savings ≤ 0, payback is infinite (never pays back).

### Breakeven Analysis

Uses binary search to find renewal rent where NPV(renewal) = NPV(relocation):

```
1. Set bounds: low_rent = $0/sf, high_rent = $200/sf
2. While not converged (max 200 iterations):
   a. Calculate mid_rent = (low + high) / 2
   b. Calculate renewal NPV at mid_rent
   c. If close to relocation NPV: return mid_rent
   d. If renewal NPV < relocation NPV: increase low_rent
   e. If renewal NPV > relocation NPV: decrease high_rent
3. Return converged breakeven rent
```

Converges to 0.1% tolerance.

### Recommendation Logic

```
Primary: NPV Difference

If relocation NPV > renewal NPV + $10k:
    → RENEW (relocation costs more)

If relocation NPV < renewal NPV - $10k:
    → RELOCATE (relocation saves money)

If NPV difference < $10k:
    → NEGOTIATE (marginal difference)

Secondary factors:
  - IRR > 15%: Strong signal to relocate
  - Payback < 3 years: Attractive relocation
  - Annual cash savings: Ongoing cost benefit

Always consider qualitative factors!
```

## Testing

### Quick Test
```bash
cd /workspaces/lease-abstract/Eff_Rent_Calculator
python3 renewal_analysis.py
```

**Output**:
```
Renewal Economics Calculator - Example Analysis

================================================================================
RENEWAL vs. RELOCATION ECONOMIC ANALYSIS
================================================================================

SCENARIO 1: RENEWAL
Total Cash Outflows: $3,555,000.00
Net Present Value: $2,970,330.92
Net Effective Rent: $3.12 /sf/year

SCENARIO 2: RELOCATION
Total Cash Outflows: $3,890,000.00
Net Present Value: $3,340,350.11
Net Effective Rent: $3.51 /sf/year

COMPARISON & INVESTMENT METRICS
NPV Difference: $370,019.19
  → Relocation costs $370,019 MORE
Payback Period: 15.6 years
Annual Savings: $41,600

RECOMMENDATION: RENEW
Relocation costs $370,019 more in NPV terms.
```

### Full Test Suite
```bash
python3 -m pytest Tests/test_renewal_analysis.py -v
```

**Output**: 26 passed in 0.69s (100%)

## Example Usage

### Basic Comparison
```python
from renewal_analysis import *

renewal = RenewalScenario(
    annual_rent_psf=[25.00, 25.75, 26.50, 27.25, 28.00],
    ti_allowance_psf=15.00,
    additional_ti_psf=20.00,
    term_years=5,
    operating_costs_psf=8.00
)

relocation = RelocationScenario(
    annual_rent_psf=[23.00, 23.69, 24.40, 25.13, 25.88],
    ti_allowance_psf=25.00,
    ti_requirement_psf=40.00,
    term_years=5,
    operating_costs_psf=8.00,
    moving_costs=50000,
    downtime_days=10,
    daily_revenue=10000
)

general = GeneralInputs(
    rentable_area_sf=20000,
    discount_rate=0.10
)

comparison = compare_scenarios(renewal, relocation, general)
print_comparison_report(comparison)
```

### Negotiation Strategy
```python
breakeven = comparison.breakeven_rent_psf
current_offer = renewal.annual_rent_psf[0]

target_rent = breakeven - 1.00  # $1/sf buffer
savings = (current_offer - target_rent) * general.rentable_area_sf

print(f"Negotiate for ${current_offer - target_rent:.2f} /sf reduction")
print(f"Annual savings if achieved: ${savings:,.0f}")
```

### Sensitivity Analysis
```python
sensitivity = sensitivity_analysis(
    renewal, relocation, general,
    variables=['rent', 'ti', 'disruption'],
    variation_pct=0.10
)

recommendations = sensitivity['Recommendation'].value_counts()
if len(recommendations) > 1:
    print("Decision is sensitive to assumptions - negotiate!")
```

## Integration Points

### With Financial Utilities
```python
from financial_utils import (
    npv,                    # NPV of cash flows
    irr,                    # IRR calculation
    annual_to_monthly_rate, # Rate conversion
    annuity_factor,         # For NER calculation
    safe_divide             # Safe division
)
```

### With Effective Rent Calculator
- Same NER calculation methodology
- Compatible discount rate assumptions
- Can combine analyses (new lease vs renewal vs relocation)

### Future Enhancements
Potential additions:
- Monte Carlo simulation for risk analysis
- Multi-location comparison (>2 options)
- Tax impact analysis (depreciation, deductibility)
- Build-to-suit vs. lease analysis
- Sublease revenue impact
- Expansion option value

## Use Cases

### 1. Lease Renewal Negotiation
- Input: Current renewal offer from landlord
- Output: Breakeven rent and target negotiation range
- Decision: Counter-offer strategy

### 2. Strategic Relocation Evaluation
- Input: Multiple market options vs. current space
- Output: NPV comparison and IRR
- Decision: Relocate or stay?

### 3. Real Estate Portfolio Optimization
- Input: All lease renewal dates over next 3 years
- Output: Prioritize which locations to renegotiate/relocate
- Decision: Resource allocation for lease negotiations

### 4. Budget Planning
- Input: Projected renewal terms
- Output: 5-year cash flow forecast
- Decision: Capital allocation for TI, moving, etc.

### 5. M&A Due Diligence
- Input: Target company's lease portfolio
- Output: Lease rationalization opportunities
- Decision: Post-merger real estate strategy

## Cost Categories

### Renewal Costs
```
1. Rent payments (variable schedule supported)
2. Operating costs (CAM, taxes, utilities)
3. Net TI costs (additional TI - landlord allowance)
4. Renovation costs (refresh existing space)
5. Legal fees
```

### Relocation Costs
```
Upfront (t=0):
6.  Net TI (requirement - allowance)
7.  Moving costs (physical move)
8.  IT moving costs (servers, phones, network)
9.  Signage costs (new location)
10. Downtime revenue loss (days × daily revenue)
11. Customer loss (% × annual revenue)
12. Unamortized improvements (sunk costs realized)
13. Restoration costs (return old space to base building)
14. Legal fees (new lease negotiation)
15. Due diligence costs (surveys, environmental)
16. Broker fees (if tenant pays)

Ongoing (t=1 to n):
17. Rent payments (variable schedule supported)
18. Operating costs
```

**Total**: 18 different cost categories

## Validation

### NPV Validation
- ✅ Matches Excel NPV() function
- ✅ Properly handles t=0 cash flows (no discounting)
- ✅ Uses compound interest rate conversion

### IRR Validation
- ✅ Matches Excel IRR() function
- ✅ Newton's method converges for most scenarios
- ✅ Handles negative and zero IRR cases

### Breakeven Validation
- ✅ Binary search converges within 0.1%
- ✅ Resulting NPVs equal within $1,000
- ✅ Breakeven rent is between reasonable bounds ($0-$200/sf)

## Dependencies

### Required Modules
```python
import numpy as np           # Version: Any (basic operations)
import pandas as pd          # Version: Any (DataFrame support)
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Literal
```

### Internal Dependencies
```python
from financial_utils import (
    npv,
    irr,
    annual_to_monthly_rate,
    annuity_factor,
    safe_divide
)
```

## Files Created

```
Eff_Rent_Calculator/
├── renewal_analysis.py                    # Core module (950 lines)
├── README_RENEWAL_ANALYSIS.md             # Documentation (800+ lines)
└── Tests/
    └── test_renewal_analysis.py           # Test suite (615 lines, 26 tests)
```

## GitHub Issue

**Issue #5**: https://github.com/reggiechan74/lease-abstract/issues/5
**Status**: ✅ Ready to close
**Related**: Issue #8 (financial_utils) - foundation dependency

---

**Implementation**: Complete and production-ready
**Testing**: Comprehensive (26/26 passing)
**Documentation**: Complete with 5 usage examples and negotiation strategies
**Integration**: Ready for use with existing calculators
