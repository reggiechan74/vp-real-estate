# Meet Reggie Chan: Your VP of Leasing & Asset Management

[![Version](https://img.shields.io/badge/version-1.8.0-blue.svg)](https://github.com/reggiechan74/leasing-expert/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12%2B-brightgreen.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-235%2B%20passing-success.svg)](Eff_Rent_Calculator/Tests/)
[![Code Style](https://img.shields.io/badge/code%20style-typed-black.svg)](https://docs.python.org/3/library/typing.html)
[![GitHub Stars](https://img.shields.io/github/stars/reggiechan74/leasing-expert?style=social)](https://github.com/reggiechan74/leasing-expert)

**Version 1.8.0** • Released 2025-11-07

## The Digital Embodiment of a 20-Year Real Estate Veteran

This repository and agent system **is** Reggie Chan, CFA, FRICS—a Vice President of Leasing and Asset Management with over two decades of institutional real estate experience.

**It's like having Reggie Chan work for you—for the price of a Claude Code subscription.**

You're not just getting software. You're getting:
- **CFA-level financial analysis** on every deal
- **FRICS property expertise** across industrial and office assets
- **20+ years of negotiation experience** distilled into evidence-based strategies
- **Executive-level judgment** on lease structures, tenant credit, and portfolio risk

Just address "Reggie" in your messages and watch a seasoned VP evaluate your deals, structure your offers, and craft responses to impossible tenant objections—all backed by 11 financial calculators, 15 specialized skills, and 25 automated workflows.

---

### **TL;DR: Survive the Asset Manager's Inquisition. Get to Your Tee Time.**

Every great deal is a war fought on two fronts: one against the market, and the other against the asset manager's love of spreadsheets. You win the first war with instinct and a handshake. You win the second with this.

*   **Speak Fluent Asset Management (Without Knowing a Thing).**
    Your asset manager can sniff out a rounding error from two floors away and lives for the thrill of finding a broken link in your spreadsheet. Reggie generates a pristine, institutional-grade package so clean, so auditable, and so utterly devoid of "cowboy math," they'll have to approve it on the spot—leaving them with nothing to do but quietly admire the model's structural integrity.

*   **The Ultimate Desk Chair to Golf Cart Conversion Kit.**
    Let's be real: that 40–50% weekly time saving isn't going back into optimizing pivot tables. It's for chasing the next deal or lowering your handicap. Reggie's 25 workflows automate the mind-numbing pain of lease abstraction and the tedious hunt for market comps. This isn't just about reclaiming time; it's about reclaiming your commission, your bonus, and your sanity.

*   **Have the Answer Before They Can Even Form the Question.**
    Get ready for the lightning round of impossible questions. *"What's the three-scenario NPV on our portfolio rollover risk for Q3 2026?"* *"What's the Black-Scholes value of that termination option if interest rates shift 50 bps?"* Before, you'd stall. Now, you just smile, type `/run-analysis`, and watch the report materialize in their inbox. It’s the ultimate power move.

It's the perfect unspoken agreement. You hand them the unimpeachable, meticulously documented data they worship. So sure, they win. But you win even more on the back nine.

---

**[README for Leasing Managers](README-FOR-LEASING-MANAGERS.md)** ← Same toolkit, told the way you actually talk.

**[Why I Built This](WHY-I-BUILT-THIS.md)** ← From spreadsheet monk to deal closer. The origin story.

---

## How to Work with Reggie

Simply address **"Reggie"** in your messages to activate your VP of Leasing & Asset Management:

```
"Reggie, what do you think of this renewal offer at $25/sf with 3 months free rent?"

"Reggie, help me evaluate this tenant's creditworthiness—they're a 5-year-old tech startup"

"Reggie, the tenant says our rent is too high. How should I respond?"
```

Reggie has access to:
- **15 specialized skills** for every lease situation (assignments, surrenders, SNDAs, objection handling, etc.)
- **25 slash commands** that automate everything from lease abstraction to IFRS 16 accounting
- **11 financial calculators** including NPV, effective rent, credit scoring, and Black-Scholes option valuation

You get executive-level judgment, CFA financial rigor, and FRICS property expertise—instantly.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Capabilities](#capabilities)
3. [Architecture & Tech Stack](#architecture--tech-stack)
4. [Productivity Impact](#productivity-impact)
5. [Scope & Use Cases](#scope--use-cases)
6. [Roadmap](#roadmap)
7. [Project Structure](#project-structure)
8. [Compliance & Limitations](#compliance--limitations)
9. [Contributing](#contributing)
10. [License & Attribution](#license--attribution)
11. [Support](#support)

---

## Getting Started

### Requirements
- **Claude Code** - Anthropic's official CLI (required for slash-command workflows)
- Python 3.12+ (installed automatically via Claude Code)

### Installation

**Step 1: Install Claude Code**

```bash
# Install Claude Code from https://docs.claude.com/claude-code
# For most systems:
npm install -g @anthropic-ai/claude-code
```

**Step 2: Clone the Repository**

```bash
git clone https://github.com/reggiechan74/leasing-expert.git
cd leasing-expert
```

**Step 3: Install Dependencies via Claude Code**

Open Claude Code in the repository directory and run:

```
Install all the dependencies for this project
```

Claude Code will install:
- Python dependencies: `numpy`, `pandas`, `scipy`, `openpyxl`, `pytest`, `markitdown[docx]`
- PDF generation tools: `pandoc`, `wkhtmltopdf`
- All other required packages

**Alternative: Manual Installation**

If you prefer to install dependencies manually without Claude Code:

```bash
pip install numpy pandas scipy
pip install 'markitdown[docx]'        # document conversion
pip install openpyxl                  # Excel export for MLS extraction
pip install pytest                    # optional: run test suite

# For PDF report generation (relative valuation, etc.)
sudo apt-get install -y pandoc wkhtmltopdf  # Linux/Ubuntu
# Or: brew install pandoc wkhtmltopdf       # macOS
```

*Note: Manual installation limits you to direct calculator usage. Slash commands require Claude Code.*

### First Workflow: Abstract & Analyze

```bash
# 1. Extract lease terms into the 24-section template
/abstract-lease path/to/lease.docx

# 2. Run an effective-rent analysis on the same deal
/effective-rent path/to/lease.pdf

# 3. Extract MLS data to Excel for competitive analysis
/extract-mls path/to/mls_report.pdf --subject="2550 Stanfield"
```

Each command follows the same pipeline:
1. Extract data from PDF/DOCX  
2. Generate validated JSON input  
3. Execute the relevant calculator  
4. Write a timestamped report into `Reports/`

### Direct Calculator Usage

```bash
# Effective Rent / PRR analysis
python Eff_Rent_Calculator/eff_rent_calculator.py baf_input_example.json

# Tenant credit scoring
python Credit_Analysis/run_credit_analysis.py credit_inputs/sample_tenant_2025-10-31_input.json

# IFRS 16 accounting schedules
python IFRS16_Calculator/run_ifrs16_analysis.py ifrs16_inputs/sample_input.json

# Rental variance decomposition
python Rental_Variance/rental_variance_calculator.py sample_variance_input.json -v

# Relative valuation / competitive positioning
python Relative_Valuation/relative_valuation_calculator.py \
  --input data.json \
  --output report.md \
  --output-json results.json \
  --full  # Show all competitors (not just top 10)

# Use tenant persona weights (3pl, manufacturing, office, default)
python Relative_Valuation/relative_valuation_calculator.py \
  --input data.json \
  --output report.md \
  --persona 3pl  # Optimized for distribution/logistics tenants

# With statistical analysis (regression, correlation, outliers)
python Relative_Valuation/relative_valuation_calculator.py \
  --input data.json \
  --output report.md \
  --stats  # Adds traditional statistical analysis section

# Portfolio rollover analysis
python Rollover_Analysis/rollover_calculator.py \
  Rollover_Analysis/rollover_inputs/sample_portfolio.json

python Rollover_Analysis/report_generator.py \
  Rollover_Analysis/rollover_inputs/sample_portfolio.json \
  Reports/YYYY-MM-DD_HHMMSS_rollover_analysis_report.md

# Default damage quantification
python Default_Calculator/default_calculator.py \
  Default_Calculator/default_inputs/sample_default.json

python Default_Calculator/notice_generator.py \
  Default_Calculator/default_inputs/sample_default.json \
  Reports/YYYY-MM-DD_HHMMSS_default_notice.md \
  ontario  # Jurisdiction for legal framework

# Renewal vs. relocation economics
python Renewal_Analysis/run_renewal_analysis.py renewal_inputs/sample_input.json

# Real options valuation (Black-Scholes)
python Option_Valuation/option_valuation.py \
  Option_Valuation/sample_option_input.json \
  --output results.json \
  --verbose
```

### Run the Test Suite

```bash
python -m pytest Eff_Rent_Calculator/Tests/ -v
```

---

## Capabilities

**What Reggie Brings to Your Team**

Reggie Chan's expertise is backed by a complete suite of analytical tools and specialized knowledge systems:

### Reggie's Specialized Skills (15 Expert Systems)
When you ask Reggie about specific situations, he automatically activates the relevant expert system:

- **Core leasing**: Deal structuring and negotiation strategy for industrial/office leases
- **Transfers & modifications**: Assignment consent, sublease analysis, share transfers, surrenders, waivers
- **Security & protection**: Indemnity agreements, SNDA/non-disturbance negotiations
- **Ancillary agreements**: Temporary licenses, storage agreements, telecom licensing
- **Disputes**: Lease arbitration frameworks and rent determination
- **Negotiation & objection handling**: Evidence-based persuasion (calibrated questions, accusation audits, tactical empathy); systematic objection analysis and response strategies

Each skill provides checklists, negotiation angles, risk flags, and recommended language—like having a senior advisor instantly available for every situation. Reggie integrates these skills with quantitative analysis to craft data-driven responses to tenant objections.

### Reggie's Financial Toolkit (11 Analytical Engines)
These are the quantitative tools Reggie uses to back up his recommendations with CFA-level analysis:
1. **Effective Rent Calculator** (`Eff_Rent_Calculator/`)  
   - Inputs: rent schedule (annual $/sf), incentives (TI, cash allowances, free rent), leasing costs, REIT capital assumptions.  
   - Outputs: Net/Gross Effective Rent, NPV vs. costs, breakeven rents, Ponzi Rental Rate comparison, payback, sensitivity tables.  
   - Use Cases: Offer structuring, investment committee packages, renegotiation analysis.
2. **Rental Yield Curve** (`Rental_Yield_Curve/`)  
   - Models implied termination options to build a rent term structure, forecasting market rent shifts across maturities.  
   - Supports “what-if” scenarios for escalation clauses, early termination rights, and renewal probabilities.
3. **Rental Variance Analysis** (`Rental_Variance/`)  
   - Decomposes revenue variance into rate, area, and term components using DAYS360 methodology; reconciles budget vs. actuals with audit-ready tables.  
   - Ideal for monthly/quarterly reporting packs and leasing scorecards.
4. **Relative Valuation Engine** (`Relative_Valuation/`)
   - Weighted MCDA rankings across up to 25 variables (9 core + 16 optional) with dynamic weight allocation based on data availability.
   - Core variables: rent, TMI, parking, clear height, office %, distance, building age, class, area match.
   - Optional variables: shipping doors (TL/DI), power, trailer parking, secure shipping, excess land, bay depth, lot size, HVAC, sprinkler, rail, crane, occupancy, grade-level doors, days on market, zoning.
   - **External Weights Configuration** - JSON-based weight management with 4 tenant personas (default, 3pl, manufacturing, office).
   - **Auto-Load Defaults** - Weights automatically loaded when not provided in input JSON.
   - **Complete Transparency** - All weights displayed in reports with mathematical 100% verification.
   - Outputs competitive status, pricing gap to Top 3, rent/TMI adjustment scenarios, and landscape PDF reports with professional formatting and page break controls.
5. **IFRS 16 / ASC 842 Calculator** (`IFRS16_Calculator/`)  
   - Generates present value of lease liabilities, ROU asset schedules, journal entries, and CSV amortization/depreciation tables.  
   - Used for monthly close, audit support, and disclosure packages.
6. **Tenant Credit Analysis** (`Credit_Analysis/`)  
   - Calculates 15+ ratios, produces a 100-point credit score, assigns rating band, estimates PD/LGD, and recommends security amounts.  
   - Supports underwriting, renewal risk reviews, and portfolio credit surveillance.
7. **Renewal Economics** (`Renewal_Analysis/`)
   - Compares renewal vs. relocation scenarios incorporating relocation capex, downtime, IRR, payback, and blended NER.
   - Guides negotiation stance on expiring leases and capital allocation.
8. **Portfolio Rollover Calculator** (`Rollover_Analysis/`)
   - Aggregates lease expiries by year/quarter with concentration risk flags (>20% HIGH, >30% CRITICAL).
   - Priority scoring (0-1 normalized) based on rent contribution, urgency, below-market status, and credit rating.
   - Three-scenario modeling (optimistic/base/pessimistic) with scenario-specific downtime and NPV discounting.
   - Use Cases: Portfolio planning, renewal prioritization, budget forecasting, expiry cliff risk management.
   - **37 tests passing** (100% coverage) including edge cases (empty portfolio, 0%/100% renewal rates).
9. **Default Damage Calculator** (`Default_Calculator/`)
   - Quantifies landlord damages from tenant defaults: arrears (with interest), future rent NPV, re-letting costs, mitigation credits.
   - Business day cure period calculations with jurisdiction-aware legal framework.
   - Bankruptcy cap analysis (§502(b)(6)) for Chapter 11 scenarios.
   - Net exposure calculation after security deposits and letters of credit.
   - Use Cases: Default notices, settlement negotiations, litigation support, security adequacy reviews.
   - **32 tests passing** (100% coverage) with comprehensive METHODOLOGY.md documentation (1,850 lines).
10. **Statistical Analysis Module** (`Relative_Valuation/statistics_module.py`)
    - Supplements MCDA rankings with traditional statistical analysis (multiple linear regression, correlation, z-scores).
    - Identifies rent drivers, data quality issues, and market outliers.
    - Activated via `--stats` flag on relative valuation calculator.
    - Key Insights: Most variable factor (CV), rent predictability (R²), strongest driver, strongest correlation.
    - Use Cases: Large datasets (20+ properties), understanding rent drivers, validating MCDA results, data quality checks.
11. **Real Options Valuation Calculator** (`Option_Valuation/`)
    - Black-Scholes option pricing for lease flexibility (renewal, expansion, termination, purchase options).
    - Calculates option value, Greeks (Delta, Gamma, Vega, Theta, Rho), and probability in-the-money.
    - Portfolio valuation for multiple concurrent options with sensitivity analysis.
    - JSON input/output with command-line interface for automation.
    - Use Cases: Valuing embedded lease options, negotiation support, lease vs. purchase decisions, portfolio option value aggregation.
    - **36 tests passing** (100% coverage) validated against published Black-Scholes calculators.

### Reggie's Automated Workflows (25 Slash Commands)
Reggie has 25 automated workflows at his disposal. Each slash command packages data extraction instructions, domain expertise, calculator invocation, and report formatting. Commands are grouped into Abstraction (2), Financial Analysis (10), Accounting (1), Comparison (4), Compliance (7), and Utilities (1).

| Category | Command | Primary Output |
|----------|---------|----------------|
| Abstraction | `/abstract-lease` | 24-section lease abstract + JSON schema |
| Abstraction | `/critical-dates` | Timeline of renewals, expiries, and notice trigger dates |
| Financial Analysis | `/effective-rent` | Deal economics report with NER/GER, PRR, sensitivities |
| Financial Analysis | `/tenant-credit` | Credit memo with ratios, PD/LGD, security recommendation |
| Financial Analysis | `/rental-variance` | Budget vs. actual variance decomposition |
| Financial Analysis | `/market-comparison` | Market rent benchmarks and pricing gap analysis |
| Financial Analysis | `/rollover-analysis` | Portfolio expiry risk dashboard with action plan |
| Financial Analysis | `/option-value` | Real options valuation (renewal, expansion, termination) |
| Financial Analysis | `/renewal-economics` | Renewal vs. relocation recommendation matrix |
| Financial Analysis | `/relative-valuation` | Competitive ranking report and pricing adjustments |
| Financial Analysis | `/recommendation-memo` | VTS approval memo with tenant analysis, financial covenant review, deal comparison |
| Financial Analysis | `/extract-mls` | Extract MLS data to professionally formatted Excel with subject property highlighting |
| Accounting | `/ifrs16-calculation` | IFRS/ASC 842 schedules and journal entries |
| Comparison | `/compare-amendment` | Amendment vs. original summary with key deltas |
| Comparison | `/compare-offers` | Side-by-side economics for multiple offers |
| Comparison | `/compare-precedent` | Deviations against standard precedent language |
| Comparison | `/lease-vs-lease` | Clause-by-clause comparison across two leases |
| Compliance | `/assignment-consent` | Consent package checklist, risk commentary |
| Compliance | `/default-analysis` | Default and cure provisions analysis |
| Compliance | `/environmental-compliance` | Environmental obligations summary |
| Compliance | `/estoppel-certificate` | Draft estoppel certificate populated from abstract |
| Compliance | `/insurance-audit` | Insurance requirement verification log |
| Compliance | `/notice-generator` | Draft lease notices (renewal, termination, default) |
| Compliance | `/work-letter` | Work letter outline from TI provisions |
| Utilities | `/convert-to-pdf` | Convert markdown files to professionally formatted PDF |

> **Tip:** Every workflow writes outputs to `Reports/` with standardized timestamps, making it easy to hand off bundles to executives, lenders, or auditors. Review `.claude/commands/README.md` for arguments, required supporting documents, and validation steps.

See `.claude/commands/README.md` for full instructions and input templates.

### Templates & Reporting
- Industrial and office 24-section abstracts (Markdown + JSON + schema).  
- Markdown reports stored in `Reports/YYYY-MM-DD_HHMMSS_[description].md`.  
- CSV exports for amortization schedules, variance breakdowns, and credit outputs.

---

## Architecture & Tech Stack

- **Language**: Python 3.12+, type hinted, modular packages.
- **Core Libraries**: NumPy, Pandas, SciPy, NumPy-Financial.
- **Testing**: Pytest with 235+ passing tests (unit + regression).
- **Workflow Pattern**: PDF → markitdown conversion → structured JSON → calculator → report.
- **Repository Layout**: Shared utilities plus dedicated folders for each calculator. See `CLAUDE.md` for a directory map and automation tooling.

---

## Productivity Impact

- Leasing managers typically spend ~60% of their week on analysis, compliance, and documentation.  
- Automated workflows + calculators cover 70–80% of that effort, unlocking an overall **40–50% reduction in total weekly workload**—often equating to two reclaimed workdays.  
- Expert skills collapse research and drafting cycles from hours to minutes, reducing dependence on senior review bottlenecks.  
- Standardized outputs (JSON, Markdown, CSV) make hand-offs to finance, legal, and executives immediate and auditable.

---

## Scope & Use Cases

### Who Uses It
- **REITs & institutional investors**: full lifecycle leasing, reporting, compliance.  
- **Property & asset managers**: renewals, modifications, expiry management.  
- **Corporate real estate teams**: lease-vs-buy decisions, IFRS/ASC compliance.  
- **Brokers & advisors**: offer preparation, market comparisons, negotiation prep.

### What It Covers
- Deal structuring, LOIs, concession modeling, arbitration prep.  
- Lease drafting support: assignments, indemnities, SNDAs, surrenders, telecom, storage.  
- Financial analytics: NER/GER, NPV, IRR, variance, sensitivity, option value.  
- Accounting: IFRS 16 / ASC 842 liability and ROU asset workflows.  
- Credit risk: scoring, PD/LGD, security recommendations.  
- Lease administration: abstraction, critical dates, notices, amendment tracking.  
- Advanced analytics: term structure modelling, portfolio rollover, market benchmarking.

---

## Roadmap

Short-term priorities:
1. Comparative market analytics (automated comps ingestion and benchmarking).
2. Tenant mix optimisation and portfolio-level dashboards.
3. Expanded API integrations (Distancematrix.ai, CoStar/LoopNet) for automated data refresh.
4. Machine learning-based weight optimization from historical deal outcomes.

---

## Project Structure

```
leasing-expert/
├── Shared_Utils/              # NPV, IRR, ratio utilities
├── Eff_Rent_Calculator/       # Effective rent + yield curve engines
├── IFRS16_Calculator/         # Lease accounting workflows
├── Credit_Analysis/           # Tenant credit scoring
├── Renewal_Analysis/          # Renewal vs relocation modelling
├── Rental_Variance/           # Variance decomposition
├── Relative_Valuation/        # MCDA competitive positioning (25 variables) + statistical analysis
├── Rollover_Analysis/         # Portfolio lease expiry and renewal prioritization
├── Default_Calculator/        # Tenant default damage quantification
├── Option_Valuation/          # Real options valuation (Black-Scholes)
├── MLS_Extractor/             # MLS PDF to Excel with subject highlighting
├── Templates/                 # Lease abstract templates
├── Reports/                   # Timestamped analysis outputs
└── .claude/                   # Automation commands, skills, agents
```

Refer to `CLAUDE.md` for a full breakdown of commands, skills, and agents.

---

## Compliance & Limitations

- This toolkit is **not** legal, accounting, tax, or investment advice.  
- All outputs must be independently verified by qualified professionals.  
- Accuracy is contingent on clean inputs; garbage in → garbage out.  
- Users remain responsible for regulatory compliance, disclosure, and professional judgment.  
- Use at your own risk; see `LICENSE` for full warranty disclaimers.

---

## Contributing

Contributions are welcome—focus on calculators, workflows, templates, documentation, or tests.  
Please:
- Add or update unit tests with every change.  
- Document assumptions and limitations.  
- Follow the established directory structure and coding style.  
- Update `CHANGELOG.md` and relevant READMEs.

---

## License & Attribution

Licensed under **Apache License 2.0**. See `LICENSE` for full terms.  
Key dependencies: Python, NumPy, Pandas, SciPy, markitdown (see respective licenses).  
Academic foundations from R. Chan’s work on Ponzi Rental Rate and rental term structures.

---

## Support

**Version**: 1.8.0 (Released 2025-11-07)
**Your VP of Leasing & Asset Management**: Reggie Chan, CFA, FRICS

For issues and feature requests, open a ticket in the repository.

**Remember**: While Reggie brings 20+ years of institutional experience and sophisticated analytical tools, all outputs should be validated by qualified professionals. This system provides executive-level guidance and analysis—but you remain responsible for final decisions.

⚠️ Always validate model outputs before reliance on material decisions.
