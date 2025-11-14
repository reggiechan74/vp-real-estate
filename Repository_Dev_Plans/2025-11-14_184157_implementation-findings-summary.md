# Implementation Findings Summary
## Date: 2025-11-14
## Branch: fix/critical-calculator-bugs

### Overview
Of the 4 reported "critical bugs" in the implementation plan, **only 1 was actually a bug**. The other 3 were false positives where the implementation was correct but misunderstood.

---

## Bug Investigation Results

### 1. ❌ IFRS 16 Amortization Schedule - FALSE POSITIVE

**Reported Issue**: "miscalculates interest for beginning-of-period payments"

**Finding**: **NO BUG EXISTS**

**Explanation**:
- The implementation correctly treats annuity-due leases in IFRS 16 context
- Period 0: First payment at commencement goes entirely to principal (correct)
- Periods 1+: The `calculate_lease_liability` function (line 150) treats remaining payments as **ordinary annuity** (`timing='end'`)
- This is correct because after the first payment, the liability represents the PV of REMAINING payments from the lease's perspective
- Amortization schedule correctly uses `interest = opening * monthly_rate` for all periods 1+
- Tests pass, final balance reaches zero, accounting reconciles perfectly

**Validation**: All existing tests pass without modification

**File**: `IFRS16_Calculator/ifrs16_calculator.py`

---

### 2. ❌ Rental Yield Curve Solver - FALSE POSITIVE

**Reported Issue**: "amortizes the blended PV over the wrong term"

**Finding**: **NO BUG EXISTS**

**Explanation**:
- Line 186 uses `self.inputs.base_term_months` which is CORRECT
- The methodology calculates: "What rate over the FULL BASE TERM (with ability to terminate early) gives the same NPV?"
- Example: 4-year spot rate = rate charged for full 60 months with option to terminate at 48 months
- Changing to `term_months` would break the entire methodology
- Test validation: ALL tests pass and match Chan (2016) academic paper exactly (100% accuracy across 10 test cases)

**Validation**: All validation tests pass, matches published academic reference

**File**: `Rental_Yield_Curve/rental_yield_curve.py`

---

### 3. ✅ Rollover Scenario Model - CONFIRMED BUG, FIXED

**Reported Issue**: "assumes entire portfolio goes vacant regardless of renewal rates"

**Finding**: **BUG CONFIRMED AND FIXED**

**Root Cause**:
- Line 396-398: Calculated `expected_vacancy_rent = total_rent * (downtime / 12.0)`
- Line 410: `noi_delta = -item.total_annual_rent * (downtime_months / 12.0)`
- Line 425: `expected_vacancy_sf=total_sf  # All space has downtime`
- **Completely ignored `renewal_rate`** - assumed 100% of portfolio goes vacant!

**Fix Implemented**:
1. Added `renewal_downtime_months` parameter to `Assumptions` class (default 0)
2. Calculate `churn_rate = 1 - renewal_rate`
3. `expected_vacancy_sf = total_sf * churn_rate` (only churning space is vacant)
4. Use weighted downtime: `(churn_rate * downtime_months) + (renewal_rate * renewal_downtime_months)`
5. Apply weighted downtime to all NOI calculations

**Impact**:
- **Before Fix**: Base scenario (65% renewal) showed 100,000 SF vacant, $3MM rent loss
- **After Fix**: Base scenario correctly shows 35,000 SF vacant (35% churn), $1.05MM rent loss
- Reduction of ~65% in reported vacancy exposure!

**Validation**: All 37 tests pass after updating test to match corrected behavior

**Files Modified**:
- `Rollover_Analysis/rollover_calculator.py` (lines 53-81, 385-440)
- `Rollover_Analysis/Tests/test_rollover_calculator.py` (lines 514-541)

---

### 4. ✅ Relative Valuation Filters - CONFIRMED BUGS, FIXED

**Reported Issue**: "can remove subject property entirely and fabricate rent/TMI cuts"

**Finding**: **TWO BUGS CONFIRMED AND FIXED**

**Bug #1: Subject Can Be Filtered Out**
- **Root Cause**: Line 1203 applied `apply_must_have_filters()` to ALL properties including subject
- **Impact**: If subject failed must-have filters (e.g., missing rail_access), it was excluded entirely
- **Example**: Subject without rail access → removed from analysis → nonsensical results
- **Fix**: Separate subject from comparables, only filter comparables, always retain subject with warning

**Bug #2: Bogus Sensitivity with < 4 Properties**
- **Root Cause**: Lines 1461-1484 set `rank_3_score = 0.0` when < 3 comparables exist, but sensitivity analysis ALWAYS ran
- **Impact**:
  - `gap_points = subject_score - 0 = 5.71` (huge bogus gap!)
  - `rent_reduction = (5.71/0.16) × 0.05 = $1.78/sf` (nonsense recommendation!)
- **Example**: Subject ranked #3 out of 3 total → gap to rank #3 = gap to self = 0 → bogus sensitivity
- **Fix**:
  - Require 4+ properties (subject + 3 comparables) for gap analysis
  - Change rank_3_score from 0.0 to None when insufficient data
  - Skip sensitivity analysis entirely when rank_3_score is None

**Validation**:
- Tested with edge case: subject fails filters, only 2 comparables
- ✅ Subject retained with warning about filter failures
- ✅ Sensitivity analysis correctly skipped with clear messaging

**Files Modified**:
- `Relative_Valuation/relative_valuation_calculator.py` (lines 1199-1225, 1478-1510, 957-961, 1009-1017)
- Added test case: `Relative_Valuation/test_fix_edge_cases.json`

---

## Summary Statistics

| Component | Status | Tests | Impact |
|-----------|--------|-------|--------|
| IFRS 16 | ✅ Correct | All pass | None - working as designed |
| Yield Curve | ✅ Correct | 100% match to academic paper | None - working as designed |
| Rollover | 🔧 Fixed | 37/37 pass | Major - 65% reduction in overstated vacancy |
| Relative Val | 🔧 Fixed (2 bugs) | Edge cases verified | Critical - prevented subject removal & bogus recommendations |

---

## Lessons Learned

1. **Validate claimed bugs before implementing fixes** - 2 out of 4 reported bugs were false positives
2. **Test-driven verification** - Tests passing is strong evidence of correctness
3. **Understand the domain** - IFRS 16 annuity-due treatment requires accounting knowledge
4. **Academic validation** - Yield Curve matching Chan (2016) paper proves correctness
5. **Edge case testing is critical** - Relative Valuation bugs only surfaced with < 4 properties

---

## Actual Changes Made

### Code Changes
1. `Rollover_Analysis/rollover_calculator.py`:
   - Added `renewal_downtime_months: int = 0` parameter
   - Fixed vacancy calculations to respect renewal rates
   - Added validation for new parameter

2. `Rollover_Analysis/Tests/test_rollover_calculator.py`:
   - Updated test expectations to match corrected behavior

3. `Relative_Valuation/relative_valuation_calculator.py`:
   - Separated subject from comparables before filtering (lines 1205-1225)
   - Fixed gap analysis to require 4+ properties (lines 1478-1510)
   - Updated report generation to handle None values (lines 957-961, 1009-1017)

4. Added test case: `Relative_Valuation/test_fix_edge_cases.json`

### Documentation Changes
- Created `implementation-findings-summary.md` documenting all findings
- Enhanced `implementation-plan-fixes.md` with pre-implementation checklist

---

## Recommendation

**DO NOT** implement the IFRS 16 or Yield Curve "fixes" from the implementation plan. They would break correctly functioning code.

**COMPLETED**: All actual bugs have been fixed:
- ✅ Rollover Analysis: Vacancy calculations now respect renewal rates
- ✅ Relative Valuation: Subject can't be filtered out, no more bogus sensitivity scenarios

**Final Status**: 2 real bugs fixed (Rollover + Relative Val), 2 false positives identified (IFRS 16 + Yield Curve)
