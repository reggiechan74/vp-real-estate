# RELATIVE VALUATION MODEL METHODOLOGY & FRAMEWORK (UPDATED)

**Report Date**: December 16, 2025  
**Analysis Types**: Competitive Market Positioning (Leasing) + Ordinal Ranking DCA (Sales)  
**Methodology**: Multi-Criteria Weighted Ranking with Hybrid Rank+Distance Scoring and Monotone Score-to-Price Mapping  
**Applications**: Industrial & Office Commercial Real Estate (leasing and fee simple valuation)

---

## EXECUTIVE SUMMARY

This framework formalizes a unified MCDA approach for both leasing competitiveness and sales valuation. It:
- Ranks subject and comparables on key attributes using weighted scores.
- Preserves magnitude via optional hybrid rank+distance/quantile scoring to avoid flattening big gaps.
- Normalizes sale prices to cash-equivalent terms and valuation date; enforces monotone score-to-price mapping with leave-one-out (LOO) stability checks for small samples.
- Calibrates weights empirically (cross-validated) and reports uncertainty bands.

**Interpretation shorthand:**
- Leasing: Lower weighted score → higher probability to win the deal. Aim for Top 3.
- Sales: Lower weighted score → higher quality; map score to $/SF via interpolation (n<7) or monotone/robust regression (n≥7). Require monotone relationship and report LOO ranges.

---

## METHODOLOGY OVERVIEW

### Four-Step Core (Leasing and Sales)
```
Step 1: Data Collection & Normalization
        - Physical, locational, financial attributes
        - For sales: cash-equivalent price + time adjustment to valuation date
        - Standardize units; handle missing data via median imputation (flagged)

Step 2: Weighting
        - Start from property-type defaults
        - Calibrate via cross-validated error minimization; report 10th–90th pct ranges

Step 3: Scoring & Ranking
        - Rank each variable (ascending/descending rules)
        - Optional hybrid rank+distance/quantile scoring to retain magnitude
        - Apply weights → composite score; lower = better

Step 4: Mapping & Validation
        - Leasing: rank position → deal probability guidance
        - Sales: score-to-price mapping via interpolation (small n) or monotone/robust regression
        - Validate with R² + LOO R², monotonicity check, residuals, sensitivity (±10% weights)
```

### Fundamental Equation (Composite Score)
```
S_i = Σ (w_j * r_ij)
```
where `w_j` are weights, `r_ij` are ranks or hybrid scores. Lower `S_i` = better.

---

## STEP 1: DATA COLLECTION & NORMALIZATION

- **Physical**: year built/effective age, clear height, % office, building SF, lot size, parking ratio, loading docks/doors, building class.
- **Locational**: distance to subject/market centroid, location score, highway frontage.
- **Financial (Leasing)**: net rent, TMI, gross rent, incentives (optional), effective rent if incentive data present.
- **Financial (Sales)**: sale price, price/SF, sale date, property rights, financing terms, conditions of sale.

**Normalization (Sales)**:
- Cash-equivalent price adjustment for non-market financing.
- Time/market conditions adjustment to valuation date.
- Exclude/flag non–arm’s-length or atypical rights; document adjustments.

**Missing data**: median imputation within peer group when necessary; flag imputed fields. Avoid defaulting to worst rank to prevent bias from reporting gaps.

---

## STEP 2: WEIGHTING

- Use property-type defaults (industrial, office, flex) consistent with prior framework.
- Provide calibrated weights via cross-validated error minimization on historical outcomes (leases won/lost or sale price fit). Report 10th–90th percentile weight ranges to show uncertainty.
- Allow tenant/persona-specific weight packs (e.g., 3PL logistics vs. professional office).

---

## STEP 3: SCORING & RANKING

**Ranking rules**:
- Ascending (lower is better): rent, TMI, age, distance, price, area mismatch.
- Descending (higher is better): clear height, docks, parking, condition, location score.
- Context: % office, building size proximity, etc.

**Hybrid rank+distance/quantile option**:
- Convert values to percentiles/z-scores (capped) or add normalized distance within variable range to preserve magnitude differences that pure ranks would flatten.

**Composite score**:
- Weighted sum of per-variable ranks/scores. Lower = better quality/competitiveness.

---

## STEP 4: MAPPING & VALIDATION

### Leasing (Competitive Positioning)
- Sort by composite score; interpret tiers:
  - Ranks 1–3: highly competitive (≈70–90% win probability)
  - Ranks 4–10: marginal; price/incentive action needed
  - Ranks 11+: weak; major pricing or repositioning
- Sensitivity: test ±10% weight shifts; report score and implied action changes.

### Sales (Ordinal Ranking DCA)
- Preferred for n<7: **Linear interpolation** between bracketing comps.
- For n≥7 or when relationship is noisy: **Monotone regression** (isotonic) or **Theil–Sen/robust OLS**; enforce decreasing price with worse scores.
- Report: R² and LOO R², 95% CI, subject LOO value range, residuals, outliers (>2σ).
- Monotonicity check: if violations, force monotone fit and disclose.

### Pre-processing disclosure (Sales)
- Cash-equivalent adjustment applied? [Yes/No, pct]
- Time adjustment applied? [Yes/No, pct per month/year]
- Atypical rights excluded/adjusted? [List]

---

## OUTPUT & REPORTING

**Leasing summary**:
- Subject rank, score, tier, and recommended price/incentive actions.
- Sensitivity table (weight tweaks) and scenario table (rent/TMI/incentive moves).

**Sales summary**:
- Subject score, bracketing comps, indicated $/SF (interpolation and monotone/robust regression), reconciled value, confidence band.
- Fit stats: R² / LOO R², monotonicity result, outliers list.

**Weights**:
- Show point weights plus calibrated range (10th–90th pct).

**Data quality**:
- Imputed fields flagged; excluded comps listed with reasons.

---

## GOVERNANCE & CALIBRATION

- Quarterly refresh weights using outcomes (leases won/lost; sale price residuals). Limit weight shifts to guardrails (e.g., ±3 p.p. per refresh).
- Log every run: inputs, weights used, overrides, calibration version, adjustments applied.
- Require human confirmation before recommending large pricing changes (e.g., >$1.00/sf net or >5% of concluded value).

---

## QUICK ACTION CHECKLIST

- [ ] Normalize prices: cash-equivalent and time-adjust to valuation date (sales).
- [ ] Handle missing data with median imputation (flagged); remove non–arm’s-length comps.
- [ ] Choose scoring mode: pure rank or hybrid rank+distance (use hybrid when attribute gaps are wide).
- [ ] Select weight pack; calibrate if historical data is available; note range.
- [ ] Run monotonicity check on score-to-price; apply monotone fit if violated.
- [ ] Report R² + LOO R², LOO subject value range, residuals, outliers.
- [ ] Document sensitivity (±10% weights) and action recommendations.

---

## APPENDIX A: DEFAULT WEIGHT HINTS (LEASING)

Industrial (typical):
- Net Rent 16%, TMI 14%, Parking 15%, Clear Height 12%, Distance 12%, % Office 8%, Year Built 8%, Area Mismatch 10%, Class 5%

Office (suburban):
- Net Rent 18%, TMI 15%, Parking 12%, Distance 12%, % Office 15%, Year Built 8%, Clear Height 5%, Area Mismatch 10%, Class 5%

Flex/R&D:
- Net Rent 15%, TMI 12%, Parking 15%, Clear Height 10%, Distance 10%, % Office 12%, Year Built 10%, Area Mismatch 10%, Class 6%

Persona packs (examples):
- 3PL Logistics: ↑ Clear Height/Doors/Parking, ↓ % Office; keep Net Rent moderate.
- Image-sensitive Office: ↑ Class/% Office/Transit Distance, ↓ Clear Height.

---

## APPENDIX B: SCORE-TO-PRICE FUNCTIONS (SALES)

- `interpolate_value(subject_score, comps)`: linear interpolation between bracketing comp scores/prices; returns indicated $/SF, total, and bracket IDs.
- `regression_value(subject_score, comps, method="monotone|theil_sen|ols")`: returns indicated $/SF/total, α/β (if applicable), R², LOO R², CI, residuals, outliers, LOO value range, method used.
- `reconcile_methods(interp, reg)`: weighted blend with rationale; default to interpolation for n<7 or low fit.

---

**Status**: Framework refreshed to align with Ordinal Ranking DCA updates (monotone fit, magnitude-aware scoring, calibration, normalization).  
**Analyst**: [To be completed]  
**Next Review**: Q1 2026 calibration cycle.
