# CODEBASE HEALTH REVIEW – RECOMMENDATION PLAN

**Assessment Date**: November 5, 2025  
**Reviewer**: Codex (automated code review)

---

## TEST RUN STATUS
- `python -m pytest` → ✅ 138 passed, ⚠️ 14 warnings (RuntimeWarning overflow in `Shared_Utils/financial_utils.py:189-193`, PytestReturnNotNone in `Rental_Yield_Curve/test_yield_curve_validation.py:176` & `:54`).

---

## TOP PRIORITIES (NEXT 1–2 SPRINTS)
1. **Stabilize shared financial utilities** – add the missing `scipy` dependency (`Shared_Utils/financial_utils.py:18` vs `requirements.txt`) and harden IRR math to eliminate overflow warnings.
2. **Restore configurable weighting in relative valuation** – respect user-supplied weights when allocating dynamic weights (`Relative_Valuation/relative_valuation_calculator.py:256-330` currently ignores `base_weights`).
3. **Normalize shared-module imports** – replace `sys.path.insert` patterns (`Credit_Analysis/credit_analysis.py:34`, `Renewal_Analysis/renewal_analysis.py:29`, `IFRS16_Calculator/ifrs16_calculator.py:31`) with package-relative imports by promoting `Shared_Utils` to an installable package.
4. **Clean test hygiene** – convert boolean returns to `assert` statements in `Rental_Yield_Curve/test_yield_curve_validation.py:54` and `:176`, and add regression coverage for the dynamic weight bug before refactoring.

---

## DETAILED RECOMMENDATIONS

### 1. Shared Financial Utilities Hardening
- **Issue**: `scipy.optimize.newton` is imported at `Shared_Utils/financial_utils.py:18`, but `requirements.txt` omits `scipy`, leading to runtime failures on fresh installs.
- **Actions**:
  - Append `scipy>=1.11.0` to `requirements.txt`.
  - Guard the IRR solver: cap step size / fall back to `numpy_financial.irr` when Newton diverges, and catch overflow/invalid iterations to provide actionable errors.
  - Add a stress-test in `Eff_Rent_Calculator/Tests/test_financial_utils.py` that reproduces the prior overflow to confirm the fix.

### 2. Relative Valuation Weight Configuration
- **Issue**: `allocate_dynamic_weights` disregards the `base_weights` parameter, so JSON-provided weights are never honored.
- **Actions**:
  - Merge `base_weights` with the default schema before redistributing missing-variable weight.
  - Extend `Relative_Valuation/sample_input.json` with a non-default weight to validate behavior.
  - Add unit coverage (new `Relative_Valuation/tests/test_weights.py`) to assert weight normalization across optional-variable combinations.

### 3. Module Packaging & Import Hygiene
- **Issue**: Multiple calculators mutate `sys.path`, which is brittle for CLI usage and packaging.
- **Actions**:
  - Convert the repo into a namespace package (e.g., `setup.cfg` with `src/` layout) or add `__init__.py` files and relative imports.
  - Update runner scripts (`Credit_Analysis/run_credit_analysis.py`, etc.) to import via package paths.
  - Document installation (`pip install -e .`) in `README.md` once packaging lands.

### 4. Test & QA Enhancements
- **Issue**: Pytest warnings reduce signal-to-noise and mask regressions.
- **Actions**:
  - Replace `return bool` with explicit assertions in `Rental_Yield_Curve/test_yield_curve_validation.py`.
  - Enable `-W error::RuntimeWarning` in CI once IRR fix ships to prevent silent math issues.
  - Relocate module tests from `Eff_Rent_Calculator/Tests/` into a top-level `tests/` package for consistency (deferred until packaging revamp).

### 5. Backlog / Housekeeping
- Drop committed `__pycache__/` directories and ensure `.gitignore` is respected.
- Consolidate duplicate reference assets (e.g., `Relative_Valuation/relative_valuation_calculator_backup.py`) or mark them clearly as archives.
- Introduce typed configuration objects (Pydantic or `dataclasses-json`) for calculators to improve validation of CLI inputs.

---

## VALIDATION PLAN
- Re-run `python -m pytest` with warnings elevated once fixes are in place.
- Add targeted integration runs for relative valuation (fixture exercising custom weights) and shared utilities (stress-case IRR).
- For packaging work, exercise CLI entry points from a clean virtual environment created via `python -m venv`.

---

## RISKS IF DEFERRED
- Missing dependency or unstable IRR solver may break production workflows on clean deploys.
- Relative valuation outputs remain insensitive to user-configured strategy weights, reducing trust in recommendations.
- Path-munging imports complicate automation / deployment pipelines and obscure dependency boundaries.
- Warning-laden test suite can hide future regressions in numerical analysis modules.

