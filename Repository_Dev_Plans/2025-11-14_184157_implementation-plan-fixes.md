# Implementation Plan – High Priority Fixes (Jan 2025)

## Overview
This plan describes the code changes required to address the four issues found during the repository code review. Including the reasons for each fix makes it clear what failure mode we are eliminating:
1. **IFRS 16 amortization schedule** miscalculates interest for beginning-of-period payments, which makes the amortization schedule diverge from the PV liability and overstates interest expense.
2. **Portfolio rollover scenarios** currently assume the entire portfolio goes vacant regardless of renewal rates, so vacancy exposure and NOI losses are vastly overstated.
3. **Rental yield curve solver** amortizes the blended PV over the wrong term, so rates no longer match the Chan (2016) reference table and the validation suite fails.
4. **Relative valuation filters/sensitivity** can remove the subject property entirely and fabricate rent/TMI cuts when fewer than three comparables survive, producing misleading recommendations.

Each section below lists the objectives, implementation steps, validation strategy, and owners (defaulting to Claude Code unless reassigned).

---

## 1. IFRS 16 Amortization Schedule (IFRS16_Calculator)
**Reason:** When payments are due at the beginning of the period, the current loop still accrues interest on the full opening balance before subtracting the payment. That inflates interest expense, produces non-zero ending balances, and fails to reconcile with the liability computed via present value.

**Objective:** Ensure the annuity-due amortization schedule reflects payment timing (cash first, interest second) so the schedule reconciles with the PV liability.

### Implementation Steps
1. **Refactor payment loop:**
   - In `generate_liability_amortization`, split the logic for `payment_timing == 'beginning'`:
     - For period 0, keep the existing presentation row but do not treat that payment as part of the interest accrual cycle.
     - For periods ≥1, first reduce the opening balance by the period’s payment, then compute interest on the reduced balance for the remainder of the period (Model A). This is the only acceptable approach for annuity-due schedules.
   - Remove the “let me reconsider” block and ensure there is no double-subtraction.
   - Make sure the balance never goes negative; clamp the last row by recomputing the final payment instead of the “minus interest plus interest” hack currently at lines 299‑332.
2. **Shared helper:** If needed, add a small helper to compute period rows for beginning vs. end timing to reduce duplication.
3. **Recalculate cumulative columns:** After fixing the per-period logic, confirm the cumulative interest/principal columns still sum to the column totals; adjust rounding only once when constructing the DataFrame.

### Validation / Tests
- Re-run `pytest Eff_Rent_Calculator/Tests/test_ifrs16_calculator.py -k amortization` and ensure the entire suite passes.
- Capture before/after schedule snippets for a 60‑month, $1,000 lease to confirm the final balance hits zero and the first month interest is exactly $0 when paid in advance.
- Add/keep a regression fixture asserting that the sum of interest across the schedule equals the difference between total cash paid and principal reduction.

---

## 2. Rollover Scenario Model (Rollover_Analysis)
**Reason:** `calculate_scenario_analysis` currently ignores the expiry schedule and renewal rates, treating every scenario as if 100% of the portfolio experiences downtime. That grossly overstates vacancy exposure and misguides risk discussions.

**Objective:** Model downtime and NOI impact using the expiry schedule and scenario-specific renewal rates instead of assuming 100% of the portfolio goes vacant every year.

### Implementation Steps
1. **Add renewal downtime parameter:** Extend `Assumptions` (and CLI/JSON schema) with `renewal_downtime_months` (default 0) so business users can decide whether renewals incur minimal downtime.
2. **Compute expiring exposure per year:**
   - Use the existing `expiry_schedule` list; each item already has `total_sf` and `total_annual_rent`.
3. **Scenario loop changes:**
   - For each scenario, compute the fraction of expiring SF that renews vs. churns (`renewal_rate`, `1 - renewal_rate`).
   - Downtime should apply only to the churn fraction; renewals should use `renewal_downtime_months` (default 0) for their downtime component.
   - `expected_vacancy_sf` → sum of `(item.total_sf * (1 - renewal_rate))` across all future expiry years.
   - `expected_vacancy_rent` → sum of `(item.total_annual_rent * downtime_months/12 * (1 - renewal_rate))`.
4. **NOI delta calculation:**
   - Replace the simple `total_rent * downtime` formula with per-year losses: `noi_delta_year = -item.total_annual_rent * downtime_months/12 * (1 - renewal_rate)`.
   - Discount each `noi_delta_year` using `years_to_expiry` as currently done.
5. **Expose renewal/turnover counts:**
   - Replace the current integer approximations with realistic counts: `leases_renewed = round(item.lease_count * renewal_rate)` if lease counts per year are tracked, or provide total SF/rent-based metrics.
6. **Update data class:** extend `ScenarioResult` if additional metrics (e.g., turnover SF, renewal downtime) are introduced.

### Validation / Tests
- Update `Rollover_Analysis/Tests/test_rollover_calculator.py` to assert that vacancy SF/rent reflect the renewal rate.
- Add a test case with two years of expiries where the renewal rate is 0% to confirm full downtime is applied, and another with 100% renewal to ensure vacancy goes to zero.

---

## 3. Rental Yield Curve Solver (Rental_Yield_Curve)
**Reason:** The solver spreads the blended “firm + MTM” present value over the base 60‑month term even when solving for, e.g., a 36‑month rate. That underprices short-term rents and breaks the documented parity with the Chan (2016) validation data.

**Objective:** When solving for the N‑month spot rate, amortize the blended PV over the correct term (`term_months`), restoring parity with the paper.

### Implementation Steps
1. **Fix `calculate_term_rate`:** Change the final line from `calculate_pmt_from_pv(target_pv, self.inputs.base_term_months)` to `calculate_pmt_from_pv(target_pv, term_months)`.
2. **Guard term length:** Raise a clear `ValueError` if `term_months <= 0` to prevent divide-by-zero issues.
3. **Audit helper functions:** Ensure `calculate_pv` and `calculate_pmt_from_pv` correctly treat `payment_psf` as annual rent and that the monthly conversions still align with the paper after the fix.
4. **Documentation:** Update the module docstring comment to clarify that the PV is re-spread over the shorter term.

### Validation / Tests
- Run `pytest Rental_Yield_Curve/test_yield_curve_validation.py` and confirm both validation tests pass.
- Manually compare the output of `rental_yield_curve.py --base-term 60 --base-rate 8 --mtm-multiplier 1.25` before/after; ensure the table matches the Chan summary.

---

## 4. Relative Valuation Filters & Sensitivity (Relative_Valuation)
**Reason:** Applying must-have filters to the combined property list can drop the subject entirely, and when fewer than three comparables remain the gap analysis still fabricates rent/TMI reductions using a meaningless `rank_3_score` of zero. Analysts then see nonsensical “reduce rent by $X” recommendations and no subject property in the rankings.

**Objective:** Ensure the subject never gets filtered out and suppress/clarify sensitivity data when there are fewer than three valid comparables. Also align sensitivity weights with the dynamic weights used for ranking.

### Implementation Steps
1. **Filter handling:**
   - Only apply `apply_must_have_filters` to the comparables list. Always append the subject back in before ranking, even if it fails filters.
   - If the subject lacks required fields or fails must-have filters, set a `subject_rank_status` flag (e.g., "Not Ranked – Missing [fields]") so the report surfaces the issue instead of producing an unreliable rank.
   - Optionally store `subject_filter_failures` to highlight gaps in the report instead of dropping the record.
2. **Gap analysis guard:**
   - When `len(all_properties_data) < 3`, set `gap_analysis['rank_3_score'] = None` and skip calling `run_sensitivity_analysis`.
   - If all comparables fail filters, display “No market comparables met criteria” and suppress ranking-based recommendations entirely.
   - Update the markdown report to display “N/A (insufficient comparables)” in the gap table and sensitivity section.
3. **Sensitivity weights:** Pass `dynamic_weights` into `run_sensitivity_analysis` so the rank deltas are computed with the same weights used for scoring.
4. **Tests / fixtures:** If test coverage exists (e.g., `Relative_Valuation/tests/test_weights.py`), add new unit tests to cover filtering, missing-data handling, and gap logic (may require a new test module).

### Validation / Manual QA
- Run a sample JSON with a strict filter that the subject fails; ensure the subject still appears in rankings and the report explains the missing requirement.
- Run a dataset with only two comparables and confirm the “Rank #3 gap” is reported as N/A and no scenarios are generated.
- Run a case where no comparables survive filters and confirm the report states that no market comparables met criteria.

---

## Cross-Cutting Considerations
- **Backward compatibility / legacy mode:** These fixes will change previously generated numbers. Expose a `--legacy-mode` flag (default off) in IFRS 16 Calculator and Rollover Analysis so teams can reproduce historical outputs when auditing past approvals. Yield Curve and Relative Valuation produce analysis outputs rather than accounting records, so legacy mode is not required.
- **Documentation & changelog:** Update each calculator's README plus the top-level CHANGELOG to describe the behavior change and why it was necessary. Refresh any sample outputs that now differ.
- **Integration / regression testing:** Beyond unit tests, run end-to-end smoke tests (e.g., sample lease abstraction workflow) to ensure dependent reports still render correctly. Pay special attention to any downstream consumers of the rollover scenarios or IFRS schedules.
- **Error handling:** Validate inputs before running calculations (e.g., months > 0, renewal rates in [0, 1] inclusive where 0 = 0% renewal and 1 = 100% renewal, MTM multiplier > 0). Raise descriptive errors so analysts understand the fix rather than seeing generic stack traces.
- **Communication plan:** Notify stakeholders that outputs (especially IFRS schedules and rollover summaries) will change and explain the benefits.

---

## Pre-Implementation Checklist
- [ ] Create feature branch: `fix/critical-calculator-bugs`
- [ ] Review current test coverage baseline for all four calculators
- [ ] Generate "before" outputs for comparison:
  - [ ] IFRS 16: 60-month, $1,000/mo lease with beginning-of-period payments
  - [ ] Rollover: Sample portfolio with mixed renewal rates
  - [ ] Yield Curve: Chan (2016) validation table output
  - [ ] Relative Valuation: Sample with subject failing filters
- [ ] Notify stakeholders of upcoming changes (draft communication)
- [ ] Document current behavior/bugs in issue tracker (if applicable)

---

## Timeline & Ownership
| Task | Est. Effort | Owner |
|------|-------------|-------|
| IFRS 16 amortization fix + tests | 0.5 day | Claude Code |
| Rollover scenario rewrite + tests | 0.75 day | Claude Code |
| Rental yield curve correction + validation | 0.25 day | Claude Code |
| Relative valuation filter/sensitivity updates + tests/docs | 0.75 day | Claude Code |
| Integration / regression testing + documentation + changelog updates | 0.75 day | Claude Code |

Total estimated engineering time: **~3.0 days** including testing, documentation, and communication buffer.
