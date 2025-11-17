# Slash Commands

Automated workflows for commercial real estate lease analysis, property valuation, and infrastructure expropriation.

## Structure

Commands are organized into 11 categories (39 total):

### 1. Abstraction (2 commands)

Extract and structure lease data from documents.

- **`/abstract-lease`** - Extract key terms using 24-section template (industrial/office)
- **`/critical-dates`** - Extract timeline and critical dates

### 2. Financial Analysis (10 commands)

Economic calculations and investment analysis.

- **`/effective-rent`** - NER, NPV, breakeven analysis (Ponzi Rental Rate framework)
- **`/renewal-economics`** - Renewal vs. relocation NPV analysis
- **`/tenant-credit`** - Credit scoring and risk assessment
- **`/option-value`** - Real options valuation (Black-Scholes)
- **`/market-comparison`** - Market rent benchmarking
- **`/rollover-analysis`** - Portfolio lease expiry analysis
- **`/rental-variance`** - Rental variance decomposition by rate, area, and term
- **`/relative-valuation`** - MCDA competitive positioning with 25 variables, tenant personas, and landscape PDF reports
- **`/extract-mls`** - Extract MLS property data to professional Excel spreadsheet (auto-detect subject, perfect formatting)
- **`/recommendation-memo`** - VTS approval memo with tenant analysis, financial covenant review, and deal terms comparison

### 3. Accounting (1 command)

Lease accounting under international standards.

- **`/ifrs16-calculation`** - IFRS 16/ASC 842 lease accounting (liability, ROU asset, schedules)

### 4. Comparison (4 commands)

Compare lease documents to identify changes and deviations.

- **`/compare-amendment`** - Compare amendment against original lease
- **`/compare-offers`** - Compare inbound vs. outbound offers
- **`/compare-precedent`** - Compare draft against standard form
- **`/lease-vs-lease`** - General lease-to-lease comparison

### 5. Compliance (7 commands)

Legal compliance, documentation, and notices.

- **`/assignment-consent`** - Assignment and subletting consent analysis
- **`/default-analysis`** - Default provisions and cure periods
- **`/environmental-compliance`** - Environmental obligations and compliance
- **`/estoppel-certificate`** - Estoppel certificate generation
- **`/insurance-audit`** - Insurance requirement verification
- **`/notice-generator`** - Generate lease notices (renewal, termination, etc.)
- **`/work-letter`** - Generate work letter from TI provisions

### 6. Valuation (2 commands)

Property valuation and comparable sales analysis.

- **`/easement-valuation`** - Value permanent or temporary easements using percentage of fee (5-35% voltage-based), income capitalization, and before/after comparison methods
- **`/comparable-sales-analysis`** - Construct adjustment grid with sequential 6-stage methodology (property rights → financing → conditions → time → location → physical), calculate 49 physical adjustments, validate gross/net limits, generate USPAP/CUSPAP compliant reconciliation

### 7. Expropriation (3 commands)

Statutory compensation and partial taking analysis under Ontario Expropriations Act.

- **`/expropriation-compensation`** - Calculate statutory compensation (s.13 market value, s.18 disturbance damages, s.18(2) injurious affection, s.20 interest) with OEA compliance validation
- **`/partial-taking-analysis`** - Before/after method for partial acquisitions with severance damages (access, shape, utility, farm ops) and injurious affection assessment
- **`/injurious-affection-analysis`** - Quantify construction and proximity impacts (noise dBA modeling, dust PM2.5/PM10, vibration PPV, traffic disruption, business losses, visual impairment)

### 8. Infrastructure (2 commands)

Agricultural easements and right-of-way analysis for transmission lines, pipelines, and transit corridors.

- **`/cropland-compensation-analysis`** - Compare Ontario one-time vs. Alberta annual vs. Farmer Required compensation models for agricultural easements with NPV analysis over 50 years (headlands, aerial spray, precision ag, labor, equipment damage)
- **`/right-of-way-analysis`** - Calculate ROW area, encumbrance impact, and easement compensation for utility transmission (69kV-500kV), pipeline, and transit corridors

### 9. Transit (1 command)

Transit station site evaluation and scoring.

- **`/transit-station-scoring`** - Systematic evaluation of transit station site alternatives using TOD potential (density, mix, walkability), multi-modal connections, acquisition complexity, community impact, and holdout risk (normalized 0-100 scoring with 4-tier recommendations)

### 10. Process (6 commands)

Executive reporting and project management for infrastructure acquisitions.

- **`/briefing-note`** - Generate executive briefing note (1-2 pages, decision-focused) for infrastructure acquisition projects
- **`/board-memo`** - Board approval memo with comprehensive financial summary, risk analysis, and board resolution language
- **`/public-consultation-summary`** - Summarize stakeholder feedback and response strategy from public meetings and written submissions
- **`/expropriation-timeline`** - Generate critical path timeline with Ontario Expropriations Act regulatory deadlines using PERT/CPM methodology
- **`/negotiation-strategy`** - Develop negotiation approach and settlement range based on owner psychology and property characteristics
- **`/settlement-analysis`** - Analyze settlement scenarios vs. hearing risk with probability-weighted outcomes and expected value comparison

### 11. Utilities (1 command)

Document conversion and utility tools.

- **`/convert-to-pdf`** - Convert markdown files to professionally formatted PDF documents

## Usage

All commands follow the **PDF → JSON → Python → Report** workflow:

1. **Extract** data from PDF/DOCX documents
2. **Generate** JSON input files
3. **Run** Python calculators
4. **Create** timestamped markdown reports in `Reports/` folder

### Example

```bash
# Financial analysis
/effective-rent path/to/lease.pdf

# IFRS 16 accounting
/ifrs16-calculation path/to/lease.pdf 5.5

# Tenant credit
/tenant-credit path/to/financials.pdf

# Lease comparison
/compare-amendment path/to/amendment.pdf path/to/original.pdf
```

## Output Locations

- **JSON Inputs**: `[Calculator]/[type]_inputs/`
- **CSV Schedules**: `[Calculator]/[type]_inputs/`
- **Reports**: `Reports/YYYY-MM-DD_HHMMSS_[description].md`

## Calculator Directories

Commands invoke Python calculators in these directories:

**Commercial Real Estate:**
- **Effective Rent**: `Eff_Rent_Calculator/`
- **IFRS 16**: `IFRS16_Calculator/`
- **Tenant Credit**: `Credit_Analysis/`
- **Renewal Economics**: `Renewal_Analysis/`
- **Rental Variance**: `Rental_Variance/`
- **Shared Utilities**: `Shared_Utils/`

**Property Valuation:**
- **Comparable Sales**: `.claude/skills/comparable-sales-adjustment-methodology/`
- **Easement Valuation**: `.claude/skills/easement-valuation-methods/`

**Expropriation & Infrastructure:**
- **Expropriation Compensation**: `.claude/skills/expropriation-compensation-entitlement-analysis/`
- **Severance Damages**: `.claude/skills/severance-damages-quantification/`
- **Injurious Affection**: `.claude/skills/injurious-affection-assessment/`
- **Cropland Compensation**: `.claude/skills/cropland-out-of-production-agreements/`

**Transit Planning:**
- **Transit Station Scoring**: `.claude/skills/transit-station-site-acquisition-strategy/`

## Development

To add a new slash command:

1. Create `[name].md` in appropriate subfolder
2. Include frontmatter with description
3. Define input format and workflow steps
4. Create corresponding Python script (if needed)
5. Test end-to-end workflow

## Notes

- All reports use Eastern Time timestamps
- Commands automatically detect lease type (industrial/office)
- Most commands support both PDF and DOCX input
- JSON schemas available for validation
