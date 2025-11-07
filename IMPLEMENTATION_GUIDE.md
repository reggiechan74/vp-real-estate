# Lease Management Toolkit – Implementation Guide

This guide complements `README.md` by diving deeper into day-to-day operations, workflow orchestration, and governance for the Commercial Real Estate Lease Management Toolkit. It is written for leasing managers, asset managers, and operations teams who intend to institutionalize the toolkit across a portfolio.

---

## 1. Audience & Objectives

| Role | Why this guide matters |
|------|------------------------|
| Leasing Managers | Operate the PDF → JSON → Python → report pipeline end-to-end, understand data requirements, and communicate outputs. |
| Asset Managers | Coordinate portfolio-level analytics (renewals, rollover, credit exposure) and integrate results into asset plans. |
| Legal & Compliance | Understand deliverables from expert skills and workflows to support approvals, notices, and documentation. |
| Finance & Accounting | Leverage calculators (IFRS 16, effective rent, variance) for reporting and budgeting cycles. |

This document focuses on operational excellence: reliable inputs, consistent execution, validation practices, and cross-team communication.

---

## 2. Toolkit Components (Detailed)

**Prerequisites**: This toolkit requires **Claude Code** (Anthropic's official CLI) to run slash commands and automated workflows. See `README.md` for installation instructions. Direct calculator usage via Python is possible without Claude Code, but slash commands provide the complete integrated experience.

### 2.1 Automation Spine
- **Slash Commands** (`.claude/commands/`): 24 commands organized by Abstraction, Financial Analysis, Accounting, Comparison, Compliance. Each command encapsulates extraction prompts, JSON templates, script execution, and reporting instructions.
- **Expert Skills** (`.claude/skills/`): 15 senior-level knowledge bases that supply negotiation guidance, checklists, and risk commentary.
- **Python Calculators**:
  - `Eff_Rent_Calculator/eff_rent_calculator.py` – Net/Gross Effective Rent, Ponzi Rental Rate (PRR), breakeven.
  - `Credit_Analysis/credit_analysis.py` – Credit ratios, scoring, PD/LGD, security recommendations.
  - `IFRS16_Calculator/ifrs16_calculator.py` – Liability & ROU asset measurement with CSV schedules.
  - `Renewal_Analysis/renewal_analysis.py` – Renewal vs relocation economics.
  - `Rental_Variance/rental_variance_calculator.py` – Three-way variance decomposition.
  - `Rental_Yield_Curve/rental_yield_curve.py` – Term structure modelling.
  - `Relative_Valuation/relative_valuation_calculator.py` – MCDA competitive positioning with up to 25 variables (9 core + 16 optional) and dynamic weighting.
- **Templates** (`Templates/Industrial`, `Templates/Office`): 24-section abstract formats in Markdown, JSON, and JSON Schema ensure consistent reporting.
- **Reports Folder** (`Reports/`): All outputs must be timestamped using `YYYY-MM-DD_HHMMSS_[description].md`.

### 2.2 Supporting Utilities
- `Shared_Utils/financial_utils.py`: Shared PV, IRR, ratio calculations (58 unit tests).
- `convert_formulas.py` / `convert_to_latex.py`: Utilities for documentation conversion.
- `skillsdevdocs/Relative Valuation Template for newsletter.xlsx`: Source data for initial relative valuation samples.

---

## 3. Operational Playbooks

### 3.1 Abstraction & Critical Dates
1. **Preparation**:
   - Ensure lease documents are OCR-ed (searchable PDF) or DOCX.
   - Gather any amendments or side letters.
2. **Execution**:
   ```bash
   /abstract-lease path/to/lease.pdf
   /critical-dates path/to/lease.pdf
   ```
3. **Outputs**:
   - Markdown abstract in `Reports/`.
   - JSON structured data for downstream calculators.
4. **Quality Checks**:
   - Confirm 24 sections populated, especially rent schedule, renewal options, and security provisions.
   - Validate critical dates align with source lease (commencement, expiry, notice deadlines).

### 3.2 Deal Economics (Effective Rent)
1. Run `/effective-rent` (slash command) or the CLI wrapper for batch processing.
2. Required data (from abstract or LOI):
   - Rent schedule (annual $/sf).
   - Incentives (TI, cash allowances, free rent).
   - Leasing costs (commissions, PM override).
   - Investment parameters for PRR (acquisition cost, LTV, debt service assumptions).
3. Review report sections:
   - NER/GER history and breakeven thresholds.
   - PRR analysis vs. target return.
   - Sensitivity scenarios.
4. Deliverable: Use the summary to brief executives on approve/renegotiate decisions.

### 3.3 IFRS 16 / ASC 842 Accounting
1. Prepare lease payment schedules (`ifrs16_inputs/*.json` format).  
2. Execute:
   ```bash
   python IFRS16_Calculator/run_ifrs16_analysis.py ifrs16_inputs/sample_input.json
   ```
3. Outputs:
   - JSON summary (`*_results.json`).
   - CSV schedules: amortization, depreciation, annual P&L.
4. Controls:
   - Tie opening balances to GL.
   - Reconcile total payments vs. lease contract.
   - Document discount rate assumptions.

### 3.4 Tenant Credit Workflow
1. Extract financial statements using `/tenant-credit` (supports PDF uploads).  
2. Validate JSON input (`credit_inputs/`) for multi-year data.  
3. Run `run_credit_analysis.py`.  
4. Interpret:
   - Sectioned ratio analysis (liquidity, leverage, profitability).
   - Credit rating & PD.
   - Security recommendations (amount, instrument).
5. Communicate results alongside lease proposals to align risk mitigation with deal terms.

### 3.5 Renewal & Portfolio Analytics
- `/renewal-economics`: Evaluate renew vs relocate including relocation capex, downtime assumptions, IRR.
- `/rollover-analysis`: Portfolio expiry risk, enabling forward-looking leasing plans.
- `/rental-variance`: Annual variance decompositions for budget vs actual reporting.

### 3.6 Competitive Positioning (Relative Valuation)
1. **Preparation**:
   - Gather comparable property data (CoStar, broker packages, market surveys).
   - Ensure data includes: address, year built, clear height, warehouse %, parking ratio, available SF, rent, TMI, class.
   - Optional fields if available: shipping doors (TL/DI), power (amps), availability date, trailer parking, secure shipping, excess land.
   - Identify subject property (distance = 0).

2. **Execution**:
   ```bash
   /relative-valuation --full [subject-address] path/to/comparables.pdf
   ```
   Or direct calculator:
   ```bash
   python Relative_Valuation/relative_valuation_calculator.py \
     --input input.json \
     --output report.md \
     --output-json results.json \
     --full
   ```

3. **Data Quality Critical**:
   - **% Office Space**: PDF shows "% Warehouse Space" - must convert: `(100 - warehouse%) / 100` stored as decimal (0.11 not 11.0).
   - **Distance Calculation**: Run `calculate_distances.py` if distances missing (requires `DISTANCEMATRIX_API_KEY`).
   - **Class Mapping**: A=1, B=2, C=3.
   - **Shipping Doors**: Parse format "X TL Y DI" into separate TL and DI fields.

4. **Outputs**:
   - Markdown report with competitive status, rankings, gap analysis.
   - JSON results with full property data and weighted scores.
   - **Landscape PDF** with 13-column comparison table.

5. **Dynamic Weighting**:
   - System uses up to 25 variables (9 core + 16 optional).
   - If optional variables missing, weights redistribute proportionally among available variables.
   - Report shows which variables were used in analysis and their weights.

6. **Interpretation**:
   - **Rank #1-3**: Highly competitive (70-90% deal-winning probability) - maintain pricing.
   - **Rank #4-10**: Marginally competitive (30-50%) - consider rent reduction or incentives.
   - **Rank #11+**: Weak position (<30%) - aggressive pricing adjustment or repositioning needed.

7. **Deliverable**: Use competitive ranking and sensitivity scenarios to inform pricing strategy and investment committee presentations.

### 3.7 Compliance & Notices
- `/assignment-consent`, `/default-analysis`, `/notice-generator`, etc., produce ready-to-deliver narratives and document checklists.
- Integrate outputs with legal counsel review before communication.

---

## 4. Data Management & Input Standards

| Data Type | Source | Expected Format | Notes |
|-----------|--------|-----------------|-------|
| Lease abstracts | `/abstract-lease` | Markdown + JSON | Keep stored in `Reports/` for easy retrieval. |
| Rent schedules | LOI/lease/estoppels | Annual $/sf (JSON) | Convert monthly totals to annualized $/sf before loading calculators. |
| Incentives | LOI, land-lord quotes | Dollar amounts | Distinguish between landlord work (cash) vs amortized tenant work. |
| Financial statements | Tenant PDFs, Excel | JSON via credit workflow | Ensure multi-year data labeled consistently (YYYY). |
| Distance data | Distancematrix.ai | JSON `distance_km` | API returns meters – divide by 1,000. Store API key in `DISTANCEMATRIX_API_KEY`. |
| Market comps | CoStar, broker packages | JSON via `/relative-valuation` | **Critical**: Convert warehouse % → office % as decimal. See special requirements below. |

**Special Requirements for Relative Valuation Data**:

| Field | Source Format | JSON Format | Notes |
|-------|--------------|-------------|-------|
| `pct_office_space` | PDF shows "89% Warehouse" | `0.11` (decimal) | **CRITICAL**: Calculate `(100 - 89) / 100 = 0.11`. Never store as `11.0`. |
| `class` | A/B/C | 1/2/3 (integer) | Map A→1, B→2, C→3 |
| `shipping_doors_tl` | "13 TL 1 DI" | `13` (integer) | Extract truck-level doors count |
| `shipping_doors_di` | "13 TL 1 DI" | `1` (integer) | Extract drive-in doors count |
| `power_amps` | "4,000" or "4000 amps" | `4000` (integer) | Remove commas, extract number |
| `trailer_parking` | "Yes" or blank | `true`/`false` (boolean) | True if "Yes", false otherwise |
| `secure_shipping` | "Yes"/"Y" or blank | `true`/`false` (boolean) | True if present, false otherwise |
| `excess_land` | "Yes" or blank | `true`/`false` (boolean) | True if "Yes", false otherwise |
| `availability_date` | "Immediate", "Jan-26", "Q4 2025" | String as-is | Keep original format |
| `distance_km` | Calculate via API | Float (kilometers) | Subject property = `0.0`, others via Distancematrix.ai |

**Naming Conventions**:
- JSON input files: `module/input_YYYY-MM-DD_HHMMSS.json`.
- Reports: `Reports/YYYY-MM-DD_HHMMSS_[description].md`.
- Use Eastern Time for timestamps to match existing repository standards.

---

## 5. Governance & Quality Assurance

1. **Version Control**  
   - Commit JSON inputs and reports to maintain audit trails.  
   - Tag releases when adopting new calculator logic.

2. **Testing**  
   - Run `pytest` before deploying updated calculators or workflows.  
   - Add regression tests when customizing formulas.

3. **Peer Review**  
   - Have a second reviewer validate critical outputs: NER, IFRS schedules, credit ratings.  
   - For legal outputs (notices, consents), obtain legal counsel approval.

4. **Change Management**  
   - Document assumptions in report headers (discount rates, growth factors, vacancy).  
   - Log modifications in `CHANGELOG.md`.

5. **Secure Storage**  
   - Store confidential inputs and outputs in access-controlled locations.  
   - Rotate API keys regularly (Distancematrix.ai, future integrations).

---

## 6. Customization & Integration

### 6.1 Adjusting Calculator Defaults
- Edit default assumptions in dataclasses (e.g., `Eff_Rent_Calculator/eff_rent_calculator.py` → `LeaseTerms`).  
- Maintain overrides in input JSON rather than hardcoding when possible.

### 6.2 Building New Workflows
1. Copy an existing command file (e.g., `.claude/commands/Financial_Analysis/market-comparison.md`).  
2. Update frontmatter, extraction checklist, and execution script.  
3. Link to a Python runner script (place under appropriate module).  
4. Add documentation in `README.md` or this guide’s appendix.  
5. Write smoke tests or sample JSON inputs to validate.

### 6.3 API Integrations
- **Distances**: Distancematrix.ai nonprofit tier (`https://api.distancematrix.ai/distancematrix`). Store token in `DISTANCEMATRIX_API_KEY`.  
- **Market Data**: Placeholder for CoStar/LoopNet—plan to add ingestion scripts in `Relative_Valuation/`.  
- **Document storage**: Integrate with DMS or cloud storage by pointing slash command outputs to mounted directories.

---

## 7. Troubleshooting

| Issue | Likely Cause | Resolution |
|-------|--------------|-----------|
| Slash command hangs | Large PDFs or non-OCR docs | Convert to text-searchable PDFs before rerunning. |
| Calculator raises key error | Mismatch between JSON keys and expected schema | Validate against template JSON (see module README). |
| Unexpected NER/NPV values | Rent schedule units incorrect | Ensure values are annual $/sf and periods sum to lease term. |
| IFRS calculator fails | Negative or zero discount rate / missing payments | Validate input schedule export; check for zero-payment months. |
| Credit score looks off | Missing multi-year data or currency mismatch | Verify JSON contains consistent historical entries. |
| Distance calculations missing | API key not loaded or quota exceeded | Export `DISTANCEMATRIX_API_KEY`; monitor 1,000 element quota. |

---

## 8. Best Practices Cheat Sheet

- **Automate early**: Trigger abstraction and credit workflows as soon as new deals arrive—downstream work depends on structured data.  
- **Centralize inputs**: Maintain a dedicated `inputs/` subfolder per module to avoid stale data.  
- **Document assumptions**: Every report should note discount rates, inflation factors, or market adjustments.  
- **Bundle outputs**: When presenting to leadership, package Markdown reports with CSV schedules for quick review.  
- **Schedule reviews**: Weekly QA standup to spot-check outputs and address data gaps.  
- **Measure impact**: Track hours saved per workflow to quantify the 40–50% productivity gain in internal reporting.

---

## 9. Appendices

### A. Command Reference by Lifecycle Stage

| Stage | Commands | Primary Output |
|-------|----------|----------------|
| Origination | `/abstract-lease`, `/effective-rent`, `/tenant-credit`, `/recommendation-memo` | Abstract, NER report, credit memo, VTS approval memo |
| Negotiation | `/market-comparison`, `/option-value`, `/notice-generator`, `/relative-valuation` | Market benchmarks, option valuation, draft notices, competitive positioning |
| Execution | `/assignment-consent`, `/work-letter`, `/environmental-compliance` | Legal checklists & commentaries |
| Administration | `/critical-dates`, `/rental-variance`, `/rollover-analysis` | Schedules, variance breakdown, expiry dashboard |
| Accounting | `/ifrs16-calculation` | ROU asset, liability schedules, journal entries |

### B. Sample Directory Layout (Engagement)

```
engagements/
├── 2025-02-14_acme_renewal/
│   ├── inputs/
│   │   ├── abstract_input.json
│   │   ├── eff_rent_input.json
│   │   └── renewal_input.json
│   ├── reports/
│   │   ├── 2025-02-14_101500_lease_abstract_acme.md
│   │   ├── 2025-02-14_102200_effective_rent_acme.md
│   │   └── 2025-02-14_103000_renewal_analysis_acme.md
│   └── supporting_docs/
│       ├── lease.pdf
│       ├── ti_quote.pdf
│       └── tenant_financials.pdf
└── 2025-03-01_portfolio_rollover/
    └── reports/2025-03-01_090015_rollover_analysis.md
```

### C. Key Files for Reference
- `README.md` – High-level overview and quick start.  
- `CLAUDE.md` – Detailed automation directory map.  
- Module-specific READMEs within each calculator directory.  
- `Relative_Valuation/` – Current Phase 1 implementation plan (`Reports/2025-11-05_125603_relative_valuation_phase1_implementation_plan.md`).

---

## 10. Maintenance Checklist

- [ ] Run unit tests (`pytest`) before each release.  
- [ ] Update `CHANGELOG.md` and bump `VERSION` when calculators or workflows change materially.  
- [ ] Review API quotas (Distancematrix.ai) monthly.  
- [ ] Archive completed engagement folders to long-term storage.  
- [ ] Conduct semi-annual audits comparing toolkit outputs with manual benchmark calculations.  
- [ ] Refresh expert skills content annually to capture legal/market updates.

---

By following this guide, teams can deploy the toolkit confidently, maintain governance standards, and consistently deliver the productivity gains highlighted in the README. For questions or enhancements, open an issue in the repository or coordinate with the maintainers.
