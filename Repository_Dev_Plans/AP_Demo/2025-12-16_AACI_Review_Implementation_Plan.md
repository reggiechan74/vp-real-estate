# Implementation Plan: AACI Review Response - Comparable Sales Adjustment Methodology

**Document:** Implementation Plan
**Date:** December 16, 2025
**Author:** Claude Code
**Status:** DRAFT - Pending Approval
**Related Issue:** AACI-style desk review identified material defects blocking sign-off
**Version:** 2.0 (Updated based on detailed technical review)

---

## Executive Summary

An AACI-style technical review identified **5 material defects** that break reproducibility and defensibility:

1. **Derived factors computed but NOT PASSED to modules** (Critical bug)
2. **Grid rates don't match factor table** (Symptom of #1)
3. **Effective age stated without rationale**
4. **Location methodology inconsistent across comparables**
5. **Weighting mischaracterized as "inverse"**

**Root Cause:** Line 724-746 in `comparable_sales_calculator.py` passes `self.market` (original input) instead of `self.effective_factors` (merged derived factors) to all adjustment modules.

**Impact:** The reported "derived factors" table (showing $4.00/ft/SF clear height, 3.0%/yr depreciation) does NOT match the actual adjustments applied in grids (which use module defaults of $1.5/ft/SF, 1.0%/yr).

**Fix Complexity:** Low - 7 lines changed for root cause, plus documentation fixes.

---

## Issue Breakdown

### Issue #1: CRITICAL - Derived Factors Not Passed to Modules

**Evidence from AACI Review:**
> Fact: Factor table states **Clear Height = $4.00/ft/SF**, **Age Depreciation = 3.0%/yr**
> Fact: Grids apply materially different rates: clear height is applied as **$1.5/ft/SF**; age is applied as **1.0%/yr**

**Root Cause Analysis:**

The calculator correctly:
1. Derives factors via paired sales analysis
2. Maps derived names to module parameter names via `parameter_mapping.py`
3. Merges into `self.effective_factors` with correct priority (derived > defaults)
4. Logs "Applied 9 derived factors (name-mapped)"

But then **passes the wrong dictionary**:

```python
# Line 724-746 - THE BUG
adjustments.extend(land.calculate_adjustments(
    self.subject, comparable, base_price, self.market, property_type))  # WRONG: self.market
#                                          ^^^^^^^^^^^
# Should be: self.effective_factors

# Same bug repeated for all 7 modules:
# - land.calculate_adjustments(..., self.market, ...)
# - site.calculate_adjustments(..., self.market, ...)
# - industrial_building.calculate_adjustments(..., self.market, ...)
# - office_building.calculate_adjustments(..., self.market, ...)
# - building_general.calculate_adjustments(..., self.market, ...)
# - special_features.calculate_adjustments(..., self.market, ...)
# - zoning_legal.calculate_adjustments(..., self.market, ...)
```

**Why it appeared to work:**
- `self.market` contains user-provided values like `appreciation_rate_annual: 3.5`
- These override defaults correctly
- But derived factors (not in original input) fall back to module defaults

**The fix is 7 lines:**

```python
# Change self.market → self.effective_factors in all 7 module calls
adjustments.extend(land.calculate_adjustments(
    self.subject, comparable, base_price, self.effective_factors, property_type))
```

---

### Issue #2: HIGH - Grid Rates Don't Match Factor Table (SYMPTOM)

This is a symptom of Issue #1. Once #1 is fixed, this resolves automatically.

**Verification after fix:**

| Factor | Derived Value | Should Apply | Currently Applies |
|--------|--------------|--------------|-------------------|
| Clear Height | $4.00/ft/SF | $4.00/ft/SF | ~~$1.50/ft/SF~~ |
| Age Depreciation | 3.0%/yr | 3.0%/yr | ~~1.0%/yr~~ |
| Condition | 13.49%/level | 13.49%/level | ~~6.0%/level~~ |
| Loading Dock | $75,000/dock | $52,500/$30,000/$105,000* | ~~$25,000/$15,000/$50,000~~ |

*Applied via ratio allocation (70%/40%/140% of aggregate)

---

### Issue #3: MEDIUM - Effective Age Stated Without Rationale

**Evidence from AACI Review:**
> Fact: Year built is **2005** and valuation date is **Jan 15, 2025**.
> Fact: Effective age is stated as **15 years** with no support.
> Inference: A 15-year effective age implies substantial renewal/condition justification.

**Problem:**
- Chronological age = 2025 - 2005 = 20 years
- Stated effective age = 15 years (5-year reduction)
- No documentation of renovations/upgrades justifying reduction

**Fix:** Add effective age rationale section to report template:

```markdown
### Effective Age Determination

| Attribute | Value | Source |
|-----------|-------|--------|
| **Year Built** | 2005 | Property records |
| **Chronological Age** | 20 years | Calculated (valuation date - year built) |
| **Effective Age Applied** | 15 years | Input data |
| **Variance** | -5 years | Requires justification |

**Rationale for Effective Age Variance:**

⚠️ **DISCLOSURE REQUIRED:** Effective age (15 years) differs from chronological age (20 years) by 5 years.

[Select applicable rationale:]
- **Documented renovations:** [List renovations with dates that justify reduced effective age]
- **Superior maintenance program:** [Evidence of maintenance exceeding industry standard]
- **Input data as provided:** Effective age taken from input without independent verification

If effective age variance cannot be justified, use chronological age or add extraordinary assumption.
```

---

### Issue #4: MEDIUM - Location Methodology Inconsistent

**Evidence from AACI Review:**
> Fact: Highway frontage premium **22.59%** is applied to Comps 2 and 5; "location score" deltas are sometimes applied (Comp 4) and sometimes explicitly suppressed (Comps 2 and 5) to avoid double-counting.
> Inference: The rule set is inconsistent across comps, creating a high risk of hidden double-counting or selective adjustment.

**Current Logic (as implemented):**

```python
# When highway frontage differs:
if subject_highway != comp_highway:
    # Apply highway frontage premium
    # DO NOT apply location score (to avoid double-counting)

# When highway frontage is same:
else:
    # Apply location score adjustment
```

**The issue:** This creates inconsistent treatment:
- Comps 2 & 5: Get 22.59% highway adjustment, NO location score adjustment
- Comps 1, 3, 4, 6: Get location score adjustment (1-4.6%), NO highway adjustment

**Why this matters:** The location score for Comps 2 & 5 (70 and 68) vs subject (75) represents a real difference that IS partially captured by highway, but not entirely. A property without highway frontage AND a lower location score has two separate deficiencies.

**Required fix - enforce deterministic hierarchy in code:**

1. **Update `_calculate_location_adjustment` in `comparable_sales_calculator.py` (lines 526-704).**
   - Keep the three-component hierarchy, but replace the binary suppression with a **residual location-score adjustment** so that when highway status differs, only the portion of the score differential not attributable to highway frontage is applied.
   - Implement a constant attribution factor (recommended: 7 points based on current dataset) and expose it via `self.effective_factors` so paired-sales evidence can override it.
   - Result: Comps 2 and 5 will receive a smaller, but non-zero, score adjustment reflecting the remaining location deficiency beyond highway access.

2. **Add a verbose log + markdown disclosure** any time residual scoring is triggered (e.g., "Location score applied on residual basis: +3 points after highway attribution") so reviewers can trace the math.

3. **Regression Test:** Re-run `test_comparable_sales_calculator.py::test_location_adjustments_non_linear_model` (or add one) to cover the new residual logic. Snapshot expected adjustments for cases with/without highway differences to prevent regression.

**Alternative (simpler, document limitation):**

Keep current logic but add explicit disclosure:

```markdown
### Location Adjustment Methodology

**Rule Applied:** When highway frontage status differs between subject and comparable, only the highway frontage premium is applied. Location score differential is NOT separately adjusted to avoid double-counting, as highway frontage is considered the dominant location factor and materially correlates with location score.

**Limitation:** This binary approach may understate adjustments for comparables with BOTH inferior highway access AND materially lower location scores. Sensitivity analysis recommended for such comparables.

| Comp | Highway Differs | Location Score Diff | Adjustment Applied | Note |
|------|-----------------|---------------------|-------------------|------|
| 2 | Yes (subj has, comp doesn't) | +5 points | Highway only (+22.6%) | Score diff NOT applied |
| 5 | Yes (subj has, comp doesn't) | +7 points | Highway only (+22.6%) | Score diff NOT applied |
```

---

### Issue #5: MEDIUM - Weighting Mischaracterized as "Inverse"

**Evidence from AACI Review:**
> Fact: Weights are set as 200/150/100 and summed as "900%," then divided by 9.0.
> Inference: Nothing shown makes this "inverse" to uncertainty, adjustment magnitude, variance, or any objective metric. It is discretionary weighting presented as algorithmic.

**Current Description (misleading):**
> "Inverse net adjustment with validation status filters"

**Actual Logic:**

```python
if validation_status == 'REJECT':
    weight = 0.0  # Excluded
elif validation_status == 'CAUTION':
    weight = 0.5  # Half weight
elif net_adj_pct < 5:
    weight = 2.0  # Double weight for minimal adjustments
elif net_adj_pct < 10:
    weight = 1.5  # 50% bonus
else:
    weight = 1.0  # Normal
```

**Fix - Accurate Description:**

```markdown
### Weighting Methodology

**Method:** Threshold-Based Discretionary Weighting (NOT inverse-variance)

Weights are assigned based on net adjustment magnitude thresholds:

| Net Adjustment Range | Weight | Rationale |
|---------------------|--------|-----------|
| < 5% (Excellent) | 2.0 (22.2% normalized) | Minimal adjustments indicate high comparability |
| 5-10% (Good) | 1.5 (16.7% normalized) | Small adjustments, good comparability |
| 10-25% (Acceptable) | 1.0 (11.1% normalized) | Moderate adjustments, standard weight |
| 25-40% (Caution) | 0.5 (5.6% normalized) | Large adjustments, reduced reliability |
| > 40% (Reject) | 0.0 (excluded) | Comparable not sufficiently similar |

**Limitations:**
- Weights are threshold-based, not continuously inverse to adjustment magnitude
- A comparable with 4.9% net adjustment gets double weight; 5.1% gets 1.5x (cliff effect)
- Method is industry-accepted (Appraisal Institute guidance) but not mathematically "inverse"

**Alternative Methods (not implemented):**
- True inverse-variance: weight = 1 / (adjustment_pct)²
- Bracketing weights: emphasize comparables above and below subject value
- Equal weights: simplest, most defensible in litigation
```

---

## Additional Issues (From AACI Review)

### Issue #6: LOW - Compliance Section Overclaims

**Evidence:**
> The report claims **USPAP/CUSPAP/IVS compliance** while being "Prepared By: Claude Code" and lacks normal appraisal report elements.

**Fix:** Replace compliance claims with accurate scope statement:

**Action Items:**

1. **Update the Markdown generator in `comparable_sales_calculator.py` (report build section) so the emitted section is titled `### Methodology Framework` and uses the accurate scope statement above.**
   - This ensures every newly generated report (e.g., `/Reports/2025-12-16_213936_comparable_sales_analysis.md`) immediately reflects the corrected disclosure.
2. **Retrofit existing signed-off artifacts.**
   - After updating the generator, rerun the calculator against `sample_industrial_comps_tight.json` and overwrite both `Reports/2025-12-16_213936_comparable_sales_analysis.md` and `Reports/2025-12-16_161000_comparable_sales_analysis.md` (or whichever deliverables will be distributed) so the published copies no longer show the overclaim.
3. **Add a changelog entry referencing the AACI review item so downstream reviewers know why the language changed.**

---

## Implementation Plan

### Phase 1: Critical Bug Fix (Priority 1)

**Effort:** 15 minutes
**Risk:** Low (simple parameter change)

**Task 1.1: Fix Module Parameter Passing**

**File:** `comparable_sales_calculator.py`
**Lines:** 724-746

**Change:**
```python
# BEFORE (bug)
adjustments.extend(land.calculate_adjustments(
    self.subject, comparable, base_price, self.market, property_type))

# AFTER (fixed)
adjustments.extend(land.calculate_adjustments(
    self.subject, comparable, base_price, self.effective_factors, property_type))
```

**Apply to all 7 module calls:**
- Line 724-725: `land.calculate_adjustments`
- Line 727-728: `site.calculate_adjustments`
- Line 732-733: `industrial_building.calculate_adjustments`
- Line 735-736: `office_building.calculate_adjustments`
- Line 739-740: `building_general.calculate_adjustments`
- Line 742-743: `special_features.calculate_adjustments`
- Line 745-746: `zoning_legal.calculate_adjustments`

**Verification:**
```bash
# Run analysis and grep for applied rates
python3 comparable_sales_calculator.py sample_industrial_comps_tight.json --verbose 2>&1 | grep -E "depreciation|clear.*height"

# Expected: Grid should show 3.0% depreciation, $4.00 clear height (or bounded values)
# Before fix: Shows 1.0% depreciation, $1.50 clear height
```

---

**Task 1.2: Fix Location Adjustment Residual Logic**

**File:** `comparable_sales_calculator.py`
**Lines:** 526-704

**Change Overview:**
- Introduce a `highway_score_attribution` factor (default 7 points, overrideable via market parameters).
- When `subject_highway != comp_highway`, compute `residual_score_diff = (subject_score - comp_score) - attribution`.
- Apply the non-linear tier adjustment using the residual so the grid reflects the remaining deficiency.
- Extend the returned metadata so the markdown generator can note "residual" vs "full" applications.

**Verification:**
```bash
pytest .claude/skills/comparable-sales-adjustment-methodology/test_comparable_sales_calculator.py -k location
# plus manual run to confirm comps 2 & 5 now show a small additional location score component
python3 .claude/skills/comparable-sales-adjustment-methodology/comparable_sales_calculator.py \
    .claude/skills/comparable-sales-adjustment-methodology/sample_industrial_comps_tight.json --verbose | \
    grep -A3 "Location score"
```

---

### Phase 2: Documentation & Output Updates (Priority 2)

**Effort:** 30 minutes
**Risk:** None (documentation only)

**Task 2.1: Add Effective Age Rationale Section**

**File:** `.claude/commands/Valuation/comparable-sales-analysis.md`

Add after Building Characteristics table:

```markdown
### Effective Age Analysis

| Parameter | Value |
|-----------|-------|
| Year Built | [YYYY] |
| Chronological Age | [XX] years (as of valuation date) |
| Effective Age Applied | [XX] years |
| Variance | [±X] years |

**Effective Age Rationale:**

[If variance ≠ 0:]
⚠️ **Justification Required:** Effective age differs from chronological age by [X] years.

Supporting evidence:
- [ ] Documented renovations: [list with dates]
- [ ] Maintenance records reviewed
- [ ] Physical inspection confirms condition
- [ ] Input data accepted as provided (requires disclosure)

[If variance = 0:]
Effective age equals chronological age. No adjustment for superior/inferior maintenance.
```

**Task 2.2: Add Location Methodology Disclosure**

Add to Location Adjustment section:

```markdown
### Location Adjustment Methodology

**Component Hierarchy (Non-Overlapping):**

1. **Submarket Differential** - Applied when subject and comparable in different submarkets
2. **Highway Frontage Premium** - Applied when highway access status differs
3. **Location Score** - Applied when highway status is SAME (to avoid double-counting)

**Disclosure:** When highway frontage differs, location score adjustment is suppressed because highway access is the dominant location factor and empirically correlates with location score. This binary approach may understate adjustments for comparables with multiple inferior location attributes.

**Comparables Affected by This Rule:**
| Comp | Highway Differs | Score Diff | Score Adjustment | Note |
|------|-----------------|------------|------------------|------|
| 2 | Yes | +5 | NOT APPLIED | Captured by highway premium |
| 5 | Yes | +7 | NOT APPLIED | Captured by highway premium |
```

**Task 2.3: Fix Weighting Description**

Replace "Inverse net adjustment" with accurate description:

```markdown
### Reconciliation Weighting

**Method:** Threshold-Based Quality Weighting

| Quality Tier | Net Adj Range | Multiplier | Normalized Example* |
|--------------|---------------|------------|--------------------|
| Excellent | < 5% | 2.0x | 22.2% (2.0 ÷ 9.0) |
| Good | 5-10% | 1.5x | 16.7% (1.5 ÷ 9.0) |
| Acceptable | 10-25% | 1.0x | 11.1% (1.0 ÷ 9.0) |
| Caution | 25-40% | 0.5x | 5.6% (0.5 ÷ 9.0) |
| Reject | > 40% | 0.0x | Excluded |

*Example assumes total multiplier sum of 9.0, matching the sample reconciliation table.

**Note:** This is threshold-based weighting, not continuously inverse to adjustment magnitude.
```

**Task 2.4: Replace Compliance Claims**

1. Update `.claude/commands/Valuation/comparable-sales-analysis.md` so future runs use the Methodology Framework disclosure.
2. Update the Markdown generation logic (same file as Task 1.2) to emit the new section.
3. Regenerate impacted reports (`Reports/2025-12-16_213936_*` et al.) after code changes.

---

### Phase 3: Validation (Priority 3)

**Effort:** 20 minutes

**Task 3.1: Re-run Analysis**

```bash
cd /workspaces/lease-abstract/.claude/skills/comparable-sales-adjustment-methodology/

# Run with verbose output
python3 comparable_sales_calculator.py sample_industrial_comps_tight.json \
    --output results/post_fix_validation.json \
    --verbose --sensitivity
```

**Task 3.2: Verify Grid Rates Match Derived Factors**

Check that:
1. Clear height adjustment uses $4.00/ft/SF (or bounded $4.00)
2. Age depreciation uses 3.0%/yr (or bounded 3.0%)
3. Condition adjustment uses 13.49%/level
4. Loading dock uses derived aggregate value with ratio allocation

**Task 3.3: Verify Reconciled Value Changes**

The reconciled value WILL change after fix because:
- Higher clear height adjustment ($4.00 vs $1.50/ft/SF)
- Higher depreciation rate (3.0% vs 1.0%/yr)
- Higher condition adjustment (13.49% vs 6.0%/level)

Document the value change and explain it's due to correct application of market-derived factors.

---

## File Change Summary

| File | Change Type | Lines | Priority |
|------|-------------|-------|----------|
| `comparable_sales_calculator.py` | Bug fixes + location residual logic + scope statement | ~60 | 1 |
| `.claude/commands/Valuation/comparable-sales-analysis.md` | Documentation | ~100 | 2 |
| `Reports/2025-12-16_213936_comparable_sales_analysis.md` (and siblings) | Regenerated output | n/a | 2 |

**Total Code Change:** ~60 lines
**Total Documentation Change:** ~100 lines + regenerated reports

---

## Verification Checklist

After implementing all changes:

- [ ] **Bug Fix Verified:** Grid rates match effective_factors values
- [ ] **Residual Location Logic:** Highway + score differentials now show residual adjustments and corresponding disclosure line
- [ ] **Effective Age:** Rationale section present in report template
- [ ] **Location Method:** Disclosure added explaining suppression rule
- [ ] **Weighting:** Accurately described as threshold-based, not inverse
- [ ] **Compliance:** Markdown generator emits Methodology Framework scope statement
- [ ] **Reports Updated:** Regenerated `Reports/*.md` artifacts so external deliverables reflect the new disclosure
- [ ] **Values Changed:** Documented that reconciled value changed due to fix
- [ ] **Test Suite:** All tests pass (no regression)

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Reconciled value changes significantly | **High** | Medium | Document as expected - correct application of derived factors |
| Location methodology challenge | Medium | Medium | Added disclosure explains rationale |
| Effective age questioned | Medium | Low | Template now requires justification |

---

## Approval

- [ ] Root cause analysis approved
- [ ] 7-line bug fix approved
- [ ] Documentation changes approved
- [ ] Value change acknowledgment
- [ ] Ready to implement

**Approved By:** _________________ **Date:** _________________

---

## Appendix: Code Change Details

### A. Exact Lines to Change in comparable_sales_calculator.py

```python
# Line 724-725
# BEFORE:
adjustments.extend(land.calculate_adjustments(
    self.subject, comparable, base_price, self.market, property_type))
# AFTER:
adjustments.extend(land.calculate_adjustments(
    self.subject, comparable, base_price, self.effective_factors, property_type))

# Line 727-728
# BEFORE:
adjustments.extend(site.calculate_adjustments(
    self.subject, comparable, base_price, self.market, property_type))
# AFTER:
adjustments.extend(site.calculate_adjustments(
    self.subject, comparable, base_price, self.effective_factors, property_type))

# Line 732-733
# BEFORE:
adjustments.extend(industrial_building.calculate_adjustments(
    self.subject, comparable, base_price, self.market, property_type))
# AFTER:
adjustments.extend(industrial_building.calculate_adjustments(
    self.subject, comparable, base_price, self.effective_factors, property_type))

# Line 735-736
# BEFORE:
adjustments.extend(office_building.calculate_adjustments(
    self.subject, comparable, base_price, self.market, property_type))
# AFTER:
adjustments.extend(office_building.calculate_adjustments(
    self.subject, comparable, base_price, self.effective_factors, property_type))

# Line 739-740
# BEFORE:
adjustments.extend(building_general.calculate_adjustments(
    self.subject, comparable, base_price, self.market, property_type))
# AFTER:
adjustments.extend(building_general.calculate_adjustments(
    self.subject, comparable, base_price, self.effective_factors, property_type))

# Line 742-743
# BEFORE:
adjustments.extend(special_features.calculate_adjustments(
    self.subject, comparable, base_price, self.market, property_type))
# AFTER:
adjustments.extend(special_features.calculate_adjustments(
    self.subject, comparable, base_price, self.effective_factors, property_type))

# Line 745-746
# BEFORE:
adjustments.extend(zoning_legal.calculate_adjustments(
    self.subject, comparable, base_price, self.market, property_type))
# AFTER:
adjustments.extend(zoning_legal.calculate_adjustments(
    self.subject, comparable, base_price, self.effective_factors, property_type))
```

### B. Expected Value Impact

After fix, the reconciled value will change because adjustments will use higher rates:

| Adjustment | Before Fix | After Fix | Impact Direction |
|------------|------------|-----------|------------------|
| Clear Height | $1.50/ft/SF | $4.00/ft/SF | Larger adjustments |
| Depreciation | 1.0%/yr | 3.0%/yr | Larger age adjustments |
| Condition | 6.0%/level | 13.49%/level | Larger condition adjustments |
| Loading Dock | $25k/$15k/$50k | $52.5k/$30k/$105k | Larger dock adjustments |

**Net Effect:** Comparable properties that are INFERIOR to subject will be adjusted UPWARD more. Superior properties adjusted DOWNWARD more. This should TIGHTEN the adjusted price range if comparables bracket the subject correctly.
