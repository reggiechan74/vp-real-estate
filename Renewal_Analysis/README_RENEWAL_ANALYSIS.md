# Renewal Economics Calculator

**File**: `renewal_analysis.py`
**Status**: ✅ Complete
**Tests**: 26/26 passing (100%)
**Coverage**: Comprehensive unit tests in `Tests/test_renewal_analysis.py`

## Overview

Comprehensive financial analysis tool for comparing lease renewal vs. relocation decisions. Calculates NPV, IRR, NER, breakeven points, and payback periods to provide data-driven recommendations for lease renewal negotiations.

## Quick Start

```python
from renewal_analysis import (
    RenewalScenario,
    RelocationScenario,
    GeneralInputs,
    compare_scenarios,
    print_comparison_report
)

# Define renewal option
renewal = RenewalScenario(
    annual_rent_psf=[25.00, 25.75, 26.50, 27.25, 28.00],  # 3% escalation
    ti_allowance_psf=15.00,
    additional_ti_psf=20.00,  # Need $20/sf, landlord offers $15/sf
    term_years=5,
    operating_costs_psf=8.00,
    legal_fees=5000
)

# Define relocation option
relocation = RelocationScenario(
    annual_rent_psf=[23.00, 23.69, 24.40, 25.13, 25.88],  # Lower base, 3% escalation
    ti_allowance_psf=25.00,
    ti_requirement_psf=40.00,  # Need $40/sf for new space
    term_years=5,
    operating_costs_psf=8.00,
    moving_costs=50000,
    it_moving_costs=25000,
    downtime_days=10,
    daily_revenue=10000,
    unamortized_improvements=75000,
    legal_fees=15000
)

# General parameters
general = GeneralInputs(
    rentable_area_sf=20000,
    discount_rate=0.10,
    current_rent_psf=24.00,
    market_rent_psf=23.00
)

# Compare scenarios
comparison = compare_scenarios(renewal, relocation, general)

# Print report
print_comparison_report(comparison)

# Access results
print(f"Recommendation: {comparison.recommendation}")
print(f"NPV Difference: ${comparison.npv_difference:,.2f}")
print(f"Payback Period: {comparison.payback_period_years:.1f} years")
```

## Core Concepts

### Decision Framework

The renewal economics calculator helps answer: **"Should we renew our current lease or relocate to a new space?"**

This decision involves balancing:
- **Ongoing costs** (rent, operating expenses)
- **Upfront costs** (TI, moving, disruption)
- **Long-term value** (NPV, IRR)
- **Risk** (business disruption, customer loss)

### NPV-Based Analysis

All costs are expressed as **present values** to enable apples-to-apples comparison:

```
NPV = PV(Rent) + PV(Operating Costs) + Upfront Costs

Where upfront costs are already at t=0 (no discounting needed)
```

**Sign convention**: Higher NPV = Higher costs = Worse option

### Investment Metrics

**Net Effective Rent (NER)**:
- NPV divided by area and annuitized over the lease term
- Represents the equivalent annual cost per square foot
- Enables comparison across different lease structures

**Internal Rate of Return (IRR)**:
- Return on investment from relocating
- Calculated from upfront relocation costs and annual savings
- Should exceed hurdle rate (typically 15%)

**Payback Period**:
- Years to recover upfront relocation costs from annual savings
- Simple metric: Upfront costs / Annual savings
- Shorter = Better (< 3 years is attractive)

### Breakeven Analysis

**Breakeven Rent**: The renewal rent at which NPV(Renewal) = NPV(Relocation)

If current renewal offer is:
- **Above breakeven**: Renewal is expensive → Consider relocation
- **Below breakeven**: Renewal is attractive → Stay
- **At breakeven**: Marginal → Negotiate or consider qualitative factors

## Input Classes

### RenewalScenario

Parameters for the lease renewal option.

```python
RenewalScenario(
    annual_rent_psf: List[float],          # Rent schedule ($/sf/year)
    ti_allowance_psf: float = 0.0,         # Landlord TI allowance ($/sf)
    additional_ti_psf: float = 0.0,        # Additional TI needed ($/sf)
    term_years: int = 5,                   # Lease term (years)
    operating_costs_psf: float = 0.0,      # Annual operating costs ($/sf)
    legal_fees: float = 0.0,               # Legal fees ($)
    renovation_costs_psf: float = 0.0,     # Renovation costs ($/sf)
    scenario_name: str = "Renewal"
)
```

**Key points**:
- `annual_rent_psf` is a list allowing variable rent schedules
- Net TI cost = `additional_ti_psf` - `ti_allowance_psf`
- Operating costs typically $4-10/sf for industrial, $10-20/sf for office

### RelocationScenario

Parameters for the relocation option.

```python
RelocationScenario(
    annual_rent_psf: List[float],           # Rent schedule ($/sf/year)
    ti_allowance_psf: float = 0.0,          # Landlord TI allowance ($/sf)
    ti_requirement_psf: float = 0.0,        # TI needed for new space ($/sf)
    term_years: int = 5,                    # Lease term (years)
    operating_costs_psf: float = 0.0,       # Annual operating costs ($/sf)

    # Moving costs
    moving_costs: float = 0.0,              # Physical move ($)
    it_moving_costs: float = 0.0,           # IT/telecom relocation ($)
    signage_costs: float = 0.0,             # New signage ($)

    # Disruption costs
    downtime_days: float = 0.0,             # Business downtime (days)
    daily_revenue: float = 0.0,             # Average daily revenue ($)
    customer_loss_pct: float = 0.0,         # % customers lost (decimal)

    # Abandonment costs
    unamortized_improvements: float = 0.0,  # Abandoned improvements ($)
    restoration_costs: float = 0.0,         # Restore old premises ($)

    # Leasing costs
    legal_fees: float = 0.0,                # Legal fees ($)
    due_diligence_costs: float = 0.0,       # Surveys, environmental ($)
    broker_fees: float = 0.0,               # Broker fees ($)

    scenario_name: str = "Relocation"
)
```

**Key points**:
- Net TI cost = `ti_requirement_psf` - `ti_allowance_psf`
- Disruption cost = `downtime_days × daily_revenue + customer_loss_pct × annual_revenue`
- All upfront costs are incurred at t=0

### GeneralInputs

Parameters common to both scenarios.

```python
GeneralInputs(
    rentable_area_sf: float,                # Rentable area (sf)
    discount_rate: float = 0.10,            # Annual discount rate (10% default)
    current_rent_psf: float = 0.0,          # Current rent for reference ($/sf)
    market_rent_psf: float = 0.0,           # Current market rent ($/sf)
)
```

**Discount rate guidance**:
- **10%**: Standard corporate hurdle rate
- **8%**: Conservative / low-risk tenants
- **12-15%**: Aggressive / high-risk situations
- Use company's WACC if available

## Output Classes

### ScenarioResult

Results for a single scenario (renewal or relocation).

```python
@dataclass
class ScenarioResult:
    scenario_name: str

    # Total cash flows
    total_rent_payments: float
    total_operating_costs: float
    total_ti_costs: float
    total_other_costs: float
    total_cash_outflows: float

    # Present values
    pv_rent: float
    pv_operating_costs: float
    pv_ti_costs: float
    pv_other_costs: float
    npv: float                              # Total NPV

    # Effective rent
    net_effective_rent_psf: float           # NER ($/sf/year)
    gross_effective_rent_psf: float         # GER ($/sf/year)

    # Annual cash flows
    annual_cash_flows: List[float]

    # Detailed breakdown
    cost_breakdown: Dict[str, float]
```

### ComparisonResult

Comparison of renewal vs. relocation.

```python
@dataclass
class ComparisonResult:
    renewal_result: ScenarioResult
    relocation_result: ScenarioResult

    # Comparison metrics
    npv_difference: float                   # Relocation NPV - Renewal NPV
    ner_difference_psf: float               # Relocation NER - Renewal NER

    # Investment metrics
    relocation_irr: Optional[float]         # IRR of relocation investment
    payback_period_years: Optional[float]   # Years to recover costs
    annual_savings: float                   # Annual cash savings

    # Breakeven analysis
    breakeven_rent_psf: Optional[float]     # Renewal rent at equal NPV
    current_margin_psf: Optional[float]     # Buffer in current offer

    # Recommendation
    recommendation: Literal['RENEW', 'RELOCATE', 'NEGOTIATE']
    recommendation_notes: str
```

## Functions

### 1. calculate_renewal_scenario()

Calculate NPV and NER for renewal scenario.

```python
def calculate_renewal_scenario(
    renewal: RenewalScenario,
    general: GeneralInputs
) -> ScenarioResult
```

**Example**:
```python
renewal = RenewalScenario(
    annual_rent_psf=[25.00] * 5,
    ti_allowance_psf=15.00,
    additional_ti_psf=20.00,
    term_years=5,
    operating_costs_psf=8.00
)

general = GeneralInputs(
    rentable_area_sf=10000,
    discount_rate=0.10
)

result = calculate_renewal_scenario(renewal, general)

print(f"Renewal NPV: ${result.npv:,.2f}")
print(f"Renewal NER: ${result.net_effective_rent_psf:,.2f} /sf/year")
```

### 2. calculate_relocation_scenario()

Calculate NPV and NER for relocation scenario.

```python
def calculate_relocation_scenario(
    relocation: RelocationScenario,
    general: GeneralInputs
) -> ScenarioResult
```

**Example**:
```python
relocation = RelocationScenario(
    annual_rent_psf=[23.00] * 5,  # Lower rent
    ti_requirement_psf=40.00,
    ti_allowance_psf=25.00,
    moving_costs=50000,
    downtime_days=10,
    daily_revenue=10000
)

result = calculate_relocation_scenario(relocation, general)

print(f"Upfront costs: ${result.total_ti_costs + result.total_other_costs:,.2f}")
print(f"Relocation NPV: ${result.npv:,.2f}")
```

### 3. compare_scenarios()

Comprehensive comparison of renewal vs. relocation.

```python
def compare_scenarios(
    renewal: RenewalScenario,
    relocation: RelocationScenario,
    general: GeneralInputs
) -> ComparisonResult
```

**Example**:
```python
comparison = compare_scenarios(renewal, relocation, general)

print(f"Recommendation: {comparison.recommendation}")
print(f"NPV Difference: ${comparison.npv_difference:,.2f}")

if comparison.npv_difference > 0:
    print("Relocation costs more")
else:
    print("Relocation saves money")

if comparison.relocation_irr:
    print(f"IRR: {comparison.relocation_irr:.2%}")

if comparison.payback_period_years:
    print(f"Payback: {comparison.payback_period_years:.1f} years")
```

### 4. calculate_breakeven_rent()

Find renewal rent where NPV(Renewal) = NPV(Relocation).

```python
def calculate_breakeven_rent(
    renewal: RenewalScenario,
    relocation: RelocationScenario,
    general: GeneralInputs
) -> Optional[float]
```

**Example**:
```python
breakeven = calculate_breakeven_rent(renewal, relocation, general)

print(f"Breakeven renewal rent: ${breakeven:,.2f} /sf/year")

if renewal.annual_rent_psf[0] < breakeven:
    print("Current offer is below breakeven - renewal is attractive")
else:
    print(f"Current offer is ${renewal.annual_rent_psf[0] - breakeven:,.2f} above breakeven")
```

**Uses binary search** to converge on breakeven rent within 0.1% tolerance.

### 5. sensitivity_analysis()

Test impact of key variables on recommendation.

```python
def sensitivity_analysis(
    renewal: RenewalScenario,
    relocation: RelocationScenario,
    general: GeneralInputs,
    variables: List[str] = ['rent', 'ti', 'disruption'],
    variation_pct: float = 0.10  # ±10%
) -> pd.DataFrame
```

**Example**:
```python
sensitivity = sensitivity_analysis(
    renewal, relocation, general,
    variables=['rent', 'ti', 'disruption'],
    variation_pct=0.10  # ±10%
)

print(sensitivity)
```

**Output columns**:
- `Variable`: Variable being tested
- `Variation`: Percentage change (e.g., "+10%")
- `Renewal_NPV`: Renewal NPV for this scenario
- `Relocation_NPV`: Relocation NPV for this scenario
- `NPV_Difference`: Difference
- `Recommendation`: RENEW / RELOCATE / NEGOTIATE

**Supported variables**:
- `'rent'`: Renewal rent sensitivity
- `'ti'`: Relocation TI sensitivity
- `'disruption'`: Disruption cost sensitivity
- `'moving'`: Moving cost sensitivity

### 6. print_comparison_report()

Print formatted comparison report.

```python
def print_comparison_report(comparison: ComparisonResult)
```

**Example output**:
```
================================================================================
RENEWAL vs. RELOCATION ECONOMIC ANALYSIS
================================================================================

SCENARIO 1: RENEWAL
Total Cash Outflows: $3,555,000.00
  Rent payments: $2,650,000.00
  Operating costs: $800,000.00
  TI costs: $100,000.00

Net Present Value: $2,970,330.92
Net Effective Rent: $3.12 /sf/year

SCENARIO 2: RELOCATION
Total Cash Outflows: $3,890,000.00
  Rent payments: $2,442,000.00
  TI costs: $300,000.00
  Other costs: $348,000.00

Net Present Value: $3,340,350.11
Net Effective Rent: $3.51 /sf/year

COMPARISON & INVESTMENT METRICS
NPV Difference: $370,019.19
  → Relocation costs $370,019 MORE

Annual Savings: $41,600
Payback Period: 15.6 years
Breakeven Renewal Rent: $30.47 /sf/year

RECOMMENDATION: RENEW
Relocation costs $370,019 more in NPV terms. Long payback period.
Consider qualitative factors: location, brand, employees, growth.
================================================================================
```

## Usage Examples

### Example 1: Simple Renewal vs. Relocation

```python
# Current space: 10,000 sf at $25/sf
# Renewal offer: $27/sf with 3% escalations
# Market rent: $24/sf with 3% escalations

renewal = RenewalScenario(
    annual_rent_psf=[27.00, 27.81, 28.64, 29.50, 30.39],
    term_years=5
)

relocation = RelocationScenario(
    annual_rent_psf=[24.00, 24.72, 25.46, 26.23, 27.01],
    ti_requirement_psf=35.00,
    ti_allowance_psf=25.00,
    moving_costs=50000
)

general = GeneralInputs(
    rentable_area_sf=10000,
    discount_rate=0.10
)

comparison = compare_scenarios(renewal, relocation, general)
print_comparison_report(comparison)
```

### Example 2: Complex Relocation Analysis

```python
# Relocation with significant disruption
relocation = RelocationScenario(
    annual_rent_psf=[22.00] * 5,
    ti_requirement_psf=45.00,
    ti_allowance_psf=30.00,

    # Moving costs
    moving_costs=75000,           # Physical move
    it_moving_costs=40000,        # IT infrastructure
    signage_costs=15000,          # New signage

    # Disruption
    downtime_days=15,             # 3 weeks downtime
    daily_revenue=25000,          # $25k/day revenue
    customer_loss_pct=0.05,       # Lose 5% of customers

    # Abandonment
    unamortized_improvements=100000,  # Abandoned TI
    restoration_costs=25000,          # Restore old space

    # Leasing
    legal_fees=20000,
    due_diligence_costs=15000
)

# Total upfront costs: ~$350k
# Need significant rent savings to justify!
```

### Example 3: Breakeven Negotiation Strategy

```python
# Calculate breakeven to guide negotiation
comparison = compare_scenarios(renewal, relocation, general)

breakeven = comparison.breakeven_rent_psf
current_offer = renewal.annual_rent_psf[0]

if current_offer > breakeven:
    target_rent = breakeven - 1.00  # $1/sf buffer
    savings = (current_offer - target_rent) * general.rentable_area_sf

    print(f"Current offer: ${current_offer:.2f} /sf")
    print(f"Breakeven: ${breakeven:.2f} /sf")
    print(f"Target rent: ${target_rent:.2f} /sf")
    print(f"Negotiate for ${current_offer - target_rent:.2f} /sf reduction")
    print(f"Annual savings if achieved: ${savings:,.0f}")
```

### Example 4: Sensitivity Analysis for Decision Confidence

```python
# Test sensitivity to key assumptions
sensitivity = sensitivity_analysis(
    renewal, relocation, general,
    variables=['rent', 'ti', 'disruption'],
    variation_pct=0.15  # ±15% for broader range
)

# Count how many scenarios support each recommendation
recommendations = sensitivity['Recommendation'].value_counts()
print("\nRecommendation frequency:")
print(recommendations)

# If recommendation changes under small variations, decision is marginal
if len(recommendations) > 1:
    print("\n⚠ Decision is sensitive to assumptions - negotiate aggressively!")
else:
    print("\n✓ Recommendation is robust across scenarios")
```

### Example 5: Multi-Year Escalation Modeling

```python
# Model complex escalation structures
year1_rent = 25.00

# Years 1-2: Fixed
# Years 3-5: 3% escalations
renewal_rents = [
    25.00,  # Year 1
    25.00,  # Year 2
    25.75,  # Year 3 (3% increase)
    26.52,  # Year 4 (3% increase)
    27.32   # Year 5 (3% increase)
]

renewal = RenewalScenario(
    annual_rent_psf=renewal_rents,
    term_years=5
)

# Market rent with CPI escalations (estimated at 2.5%)
market_year1 = 23.50
relocation_rents = [
    market_year1 * (1.025 ** i) for i in range(5)
]

relocation = RelocationScenario(
    annual_rent_psf=relocation_rents,
    term_years=5
)
```

## Integration with Financial Utilities

The renewal calculator uses these functions from `financial_utils.py`:

```python
from financial_utils import (
    npv,                    # Calculate NPV of cash flows
    irr,                    # Calculate IRR
    annual_to_monthly_rate, # Convert rates for annuity factor
    annuity_factor,         # Calculate annuity factor for NER
    safe_divide             # Safe division handling
)
```

## Validation

### Test Coverage

**26 comprehensive tests** covering:
- ✅ Renewal scenario NPV calculations
- ✅ Relocation scenario with upfront costs
- ✅ Comparison metrics (NPV difference, savings, payback)
- ✅ Breakeven rent calculation
- ✅ Recommendation generation logic
- ✅ Sensitivity analysis
- ✅ Edge cases (zero area, single year, no costs, high discount rate)

Run tests:
```bash
cd /workspaces/lease-abstract/Eff_Rent_Calculator
python3 -m pytest Tests/test_renewal_analysis.py -v
```

### Excel Validation

Key validation points:
- ✅ NPV calculations match Excel NPV() function
- ✅ IRR calculations match Excel IRR() function
- ✅ Annuity factor calculations match Excel PV() function
- ✅ Payback period matches simple division

## Recommendation Logic

The calculator generates recommendations based on:

### Primary Factor: NPV Difference

```
If NPV_Difference > $10,000:
    → RENEW (relocation costs significantly more)

If NPV_Difference < -$10,000:
    → RELOCATE (relocation saves significantly)

If -$10,000 ≤ NPV_Difference ≤ $10,000:
    → NEGOTIATE (marginal difference)
```

### Secondary Factors:

**IRR threshold** (if relocation has positive IRR > 15%):
- Strong signal to consider relocation even if NPV marginal

**Payback period**:
- < 3 years: Attractive
- 3-5 years: Moderate
- \> 5 years: Long (may not justify risk)

**Annual cash flow savings**:
- Positive: Relocation has lower ongoing costs
- Negative: Renewal has lower ongoing costs

### Qualitative Factors (Always Consider):

The calculator always notes:
- Strategic location advantages
- Brand/visibility impact
- Employee commute/satisfaction
- Future growth capacity
- Market conditions and alternatives

**These cannot be quantified but are critical to the decision!**

## Important Considerations

### 1. Hidden Relocation Costs

Ensure you include ALL costs:
- **Downtime revenue loss**: Often underestimated
- **Customer/client loss**: Can be 2-10% during move
- **Employee turnover**: Some employees won't relocate
- **Unamortized improvements**: Sunk costs become real costs
- **IT infrastructure**: Servers, phones, internet setup
- **Permits and licenses**: New location may require new permits
- **Address changes**: Business cards, website, marketing materials

**Pro tip**: Add 20-30% contingency to estimated relocation costs

### 2. Renewal Negotiation Tactics

Use the breakeven rent as leverage:

1. **Calculate breakeven** before negotiation
2. **Set target** at breakeven minus buffer (e.g., $2/sf)
3. **Present analysis** to landlord showing you've evaluated alternatives
4. **Request concessions**:
   - Lower rent
   - More TI allowance
   - Free rent periods
   - Termination options
   - Tenant improvement amortization

### 3. Timing Considerations

**When to start analysis**:
- 12-18 months before lease expiry (large spaces)
- 6-12 months before expiry (small spaces)
- Earlier if market is tight

**Negotiation timeline**:
- Market survey: 2-3 months
- Site selection: 2-4 months
- Lease negotiation: 1-3 months
- TI design/build: 3-6 months

**Total**: 8-16 months for relocation

### 4. Market Cycle Impact

**Landlord's market** (low vacancy):
- Renewal rent may exceed market rent
- Fewer concessions available
- Relocation may be attractive despite costs

**Tenant's market** (high vacancy):
- Can negotiate aggressively on renewal
- Strong TI allowances available
- Renewal often better than relocation

### 5. Lease Term Strategy

**Longer terms** (7-10 years):
- Better TI allowances
- Lower rent (landlord certainty premium)
- Amortize relocation costs over longer period
- But less flexibility

**Shorter terms** (3-5 years):
- More flexibility
- Higher rent
- Less TI
- Easier to justify relocation

**Hybrid**: 5 year firm + 5 year option

## Dependencies

```python
import numpy as np           # Numerical operations
import pandas as pd          # DataFrames for results
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Literal
```

Plus custom module:
```python
from financial_utils import npv, irr, annual_to_monthly_rate, annuity_factor, safe_divide
```

## Author

Generated by Claude Code
Date: 2025-10-30
GitHub Issue: #5

## References

- `financial_utils.py` - Shared NPV/IRR calculation module
- `eff_rent_calculator.py` - NER calculation methodology
- GitHub Issue #5: Renewal Economics Calculator requirements
