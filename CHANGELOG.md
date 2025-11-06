# Changelog

All notable changes to the Commercial Real Estate Lease Analysis Toolkit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2025-11-06

### Added

#### Relative Valuation Enhancements

**Weights Configuration System** - External JSON-based weight management with tenant persona support

- **weights_loader.py** - External weights configuration loader module
  - Loads persona-specific weights from `weights_config.json`
  - Schema validation using `weights_config_schema.json`
  - Supports 4 built-in personas: default, 3pl, manufacturing, office
  - Custom config file path support via `--weights-config` parameter
  - Automatic fallback to hardcoded defaults if config unavailable

- **weights_config.json** - Weight configuration with tenant personas
  - **Default/Balanced** (11 variables, 65-17-12-6% allocation)
  - **3PL/Distribution** - Emphasizes bay depth, clear height, shipping doors, trailer parking
  - **Manufacturing** - Emphasizes clear height, power, crane, rail access
  - **Office** - Emphasizes office space, class, HVAC, distance, parking

- **weights_config_schema.json** - JSON Schema for weight validation
  - Enforces structure: persona, name, description, weights object
  - Validates all 25 variable fields with float values
  - Ensures proper weight normalization

- **WEIGHTS_CONFIG_GUIDE.md** - Comprehensive configuration documentation
  - How to create custom weight profiles
  - Persona comparison matrix
  - Weight allocation philosophy
  - Testing and validation procedures

- **RANKING_METHODOLOGY.md** - Detailed methodology documentation
  - Competition ranking (1-2-2-4 method) explanation
  - Tie handling and Excel RANK function equivalence
  - Dynamic weight redistribution algorithm
  - Mathematical proofs and examples

**Auto-Load Default Weights** - Eliminates "Missing required field: weights" error

- Modified `load_comparable_data()` to automatically load default weights when not provided in input JSON
- Weights field now optional in input JSON (auto-loads default persona if missing)
- Seamless workflow: no need to manually add weights to JSON files
- Clear informational messages when defaults are loaded

**Complete Weights Transparency in Reports**

- Added `weights_used` field to `CompetitiveAnalysis` dataclass
- **Methodology section** now displays all weights in sortable table (highest to lowest)
- Mathematical verification: "✅ Weights sum to 100.0% - calculation verified"
- Shows actual dynamic weights used after redistribution (not just base weights)

**Improved PDF Report Formatting**

- **Page Break Controls** (`pdf_style.css`)
  - Headers (h1, h2, h3) stay with their content (`page-break-after: avoid`)
  - Tables remain intact without breaking (`page-break-inside: avoid`)
  - Table rows won't break mid-row
  - `.no-break` CSS class for critical sections

- **GAP ANALYSIS Section Protection**
  - Wrapped entire section in `<div class="no-break">` container
  - Ensures gap analysis table and recommendations stay together on same page

- **Increased White Space**
  - Major section headers (h2) now have 20px top margin (up from 8px)
  - Improved visual separation between SUBJECT PROPERTY ANALYSIS, GAP ANALYSIS, RECOMMENDED ACTIONS, METHODOLOGY, and LIMITATIONS sections

**Command-Line Persona Support**

- `--persona` flag: Choose from default, 3pl, manufacturing, office
- `--weights-config` flag: Path to custom weights configuration file
- Persona weights override JSON weights (highest priority)
- Examples:
  ```bash
  # Use 3PL persona weights
  python relative_valuation_calculator.py --input data.json --output report.md --persona 3pl

  # Use custom config file
  python relative_valuation_calculator.py --input data.json --output report.md --weights-config custom.json
  ```

### Changed

#### Relative Valuation Calculator

- **Weight Loading Priority** (lowest to highest):
  1. Auto-loaded defaults (if no weights in JSON)
  2. Explicit JSON weights (if provided)
  3. Command-line persona override (--persona flag, highest priority)

- Updated `get_tenant_persona_weights()` function:
  - Added `config_path` optional parameter
  - Attempts to load from weights_loader module (relative then absolute import)
  - Falls back to hardcoded defaults if external config unavailable
  - Returns informative messages about weight source

- Removed "weights" from required fields in `load_comparable_data()`
- Added `Optional` type hint import for better type safety

#### Report Generation

- Methodology section now includes complete weights table instead of summary
- Added weight sum verification in every report
- Improved visual hierarchy with consistent spacing
- Professional landscape PDF output with proper page breaks

### Fixed

#### Workflow Issues

- **Eliminated recurring "Missing required field: weights" error**
  - Was caused by required validation before auto-loading logic
  - Now loads defaults first, then validates other required fields
  - Users no longer need to manually add weights to input JSON

#### PDF Formatting

- **Tables breaking across pages** - Now kept intact with `page-break-inside: avoid`
- **GAP ANALYSIS splitting** - Now wrapped in no-break container
- **Insufficient spacing between sections** - Increased h2 margin-top to 20px
- **Headers orphaned from content** - Added `page-break-after: avoid` to all headers

### Documentation

- Updated README.md to version 1.4.0
- Added weights configuration system to capabilities section
- Updated relative valuation examples with persona flags
- Removed "persona-driven weighting" from roadmap (now implemented)
- Updated CLAUDE.md with weights configuration references

### Technical Details

**File Changes**:
- `Relative_Valuation/relative_valuation_calculator.py` - 101 insertions, 18 deletions
- `Relative_Valuation/pdf_style.css` - 29 insertions, 1 deletion
- `Relative_Valuation/weights_loader.py` - NEW (436 lines)
- `Relative_Valuation/weights_config.json` - NEW (134 lines)
- `Relative_Valuation/weights_config_schema.json` - NEW (67 lines)
- `Relative_Valuation/WEIGHTS_CONFIG_GUIDE.md` - NEW (1,098 lines)
- `Relative_Valuation/RANKING_METHODOLOGY.md` - NEW (1,262 lines)

**Integration Architecture**:
```
Input JSON (optional weights)
    ↓
load_comparable_data()
    ↓
Auto-load default weights if missing → get_tenant_persona_weights()
    ↓                                        ↓
Validate required fields              weights_loader.py
    ↓                                        ↓
Run analysis                          weights_config.json
    ↓                                        ↓
Generate report                       Persona-specific weights
    ↓
Display all weights + 100% verification
    ↓
Professional PDF with proper page breaks
```

**Backwards Compatibility**:
- Existing JSON input files continue to work (weights now optional)
- Command-line interface unchanged (--persona and --weights-config are new optional flags)
- Report output format enhanced but maintains structure
- All existing workflows and slash commands function identically

## [1.3.0] - 2025-11-05

### Added

#### Relative Valuation / Competitive Positioning Module

**New Calculator**: `Relative_Valuation/relative_valuation_calculator.py` - Multi-Criteria Decision Analysis (MCDA) for competitive positioning

**Purpose**: Determine where a subject property ranks relative to market comparables and provide strategic pricing recommendations to achieve Top 3 competitive positioning (70-90% deal-winning probability).

**Methodology**: 4-step MCDA framework
1. **Data Collection** - Extract 9 key variables from comparable properties
2. **Independent Ranking** - Rank each variable 1 (best) to X (worst)
3. **Weighted Scoring** - Calculate weighted score = Σ(rank × weight)
4. **Final Competitive Ranking** - Sort by weighted score ascending

**9 Variables Analyzed** (with weights):
- Net Asking Rent (16%) - Most critical factor
- Parking Ratio (15%) - Second most critical
- TMI/Operating Costs (14%)
- Clear Height (10%)
- % Office Space (10%)
- Distance from Subject (10%)
- Area Difference (10%)
- Year Built (8%)
- Class A/B/C (7%)

**Key Features**:
- **Competitive Tiers**: Rank #1-3 (Highly Competitive, 70-90% win rate), #4-10 (Moderately Competitive, 50-70%), #11+ (Not Competitive, <50%)
- **Sensitivity Analysis**: Calculate exact rent/TMI reductions needed to achieve Rank #3 threshold
- **Strategic Recommendations**: Action-oriented advice based on rank tier (maintain, adjust, or urgent repositioning)
- **Top 3 Rule**: Must be Rank #1, #2, or #3 to consistently win deals

**Outputs**:
- Markdown report with executive summary, competitive analysis, gap analysis, and recommendations
- JSON results with all rankings, weighted scores, and sensitivity scenarios
- Sample data from May 2020 GTA industrial market (122 properties)

**Validation**: Tested against original Excel template - methodology validated within 6.4% tolerance

**Expert Skill**: `.claude/skills/relative-valuation-expert.md`
- Methodology guidance and interpretation
- Strategic recommendations by rank tier
- Non-price lever alternatives (TI allowance, free rent, operating caps)
- Tenant persona adjustments (industrial vs office vs flex)
- Integration with other analyses (effective rent, market comp, credit)

**Slash Command**: `/relative-valuation` - Automated PDF → JSON → Python → Report workflow
- Extract property data from CoStar reports / broker packages
- Generate input JSON with 9 variables
- Run competitive analysis
- Provide strategic guidance and pricing recommendations

**Documentation**:
- `Relative_Valuation/README.md` - Complete usage guide and methodology documentation
- Sample files: `sample_input.json`, `sample_output.json`, `sample_report.md`
- Methodology framework: `Reports/2025-11-05_122834_relative_valuation_methodology_framework.md`

**Use Cases**:
1. **Landlord Pricing**: Adjust asking rent to achieve Top 3 market position
2. **Tenant Evaluation**: Compare multiple offers and negotiate best value
3. **Renewal Benchmarking**: Ensure renewal offers are competitive with market alternatives
4. **Portfolio Optimization**: Identify which assets are overpriced and need correction

This brings the total to **7 calculators** and **22 slash commands** (8 Financial Analysis commands).

## [1.2.0] - 2025-11-05

### Added

#### 13 Specialized Skills

**New Skill System**: `.claude/skills/` - Deep expertise for specific lease agreement types and provisions

**Core Lease Agreements (1 skill)**
- **commercial-lease-expert** - General commercial lease negotiation, drafting, and analysis
  - Net lease structures (gross, modified gross, net, triple net)
  - Lease economics fundamentals
  - Tenant improvements and operating cost recovery
  - Renewal options, assignment/subletting provisions
  - Default provisions and risk management

**Security & Protection Instruments (2 skills)**
- **indemnity-expert** - Indemnity agreements and guarantees
  - Primary obligations vs secondary guarantees
  - Absolute and unconditional provisions
  - Bankruptcy-proof features
  - Enforcement strategies and landlord protections
- **non-disturbance-expert** - SNDA (subordination, non-disturbance, attornment) agreements
  - Tenant protection against foreclosure
  - Lender/tenant/landlord tripartite agreements
  - Subordination dynamics and priority issues

**Lease Modifications & Transfers (4 skills)**
- **consent-to-assignment-expert** - Assignment consent agreements
  - Assignment vs sublease distinctions
  - Privity of estate and contract analysis
  - Joint and several liability
  - Landlord protections and release provisions
- **consent-to-sublease-expert** - Sublease consent agreements
  - Three-party sublease structures
  - Recapture rights and profit-sharing
  - Landlord/tenant/subtenant relationships
- **share-transfer-consent-expert** - Change of control consent
  - Share transfer vs assignment distinctions
  - Corporate restructuring scenarios
  - Privacy consent provisions
  - New shareholder representations
- **lease-surrender-expert** - Lease termination and surrender agreements
  - Early termination by mutual agreement
  - Partial surrenders and space reduction
  - Consideration structures
  - Mutual release provisions
  - Distressed tenant scenarios

**Preliminary & Ancillary Agreements (4 skills)**
- **offer-to-lease-expert** - Offers to lease, LOIs, and term sheets
  - Binding vs non-binding analysis
  - Conditions precedent
  - Deposit structures and exclusivity
  - Deal structuring and negotiation strategies
- **waiver-agreement-expert** - Landlord waivers of conditions
  - Conditional vs unconditional waivers
  - Counter-offer analysis
  - Acceptance deadlines
  - Contract formation timelines
- **temporary-license-expert** - Short-term licenses (1 day to 3 months) **[NEW]**
  - License vs lease distinctions
  - Film/TV production, pop-up retail, swing space
  - Gross rent structures for short terms
  - "As is" condition and minimal landlord obligations
  - Insurance and indemnity for short-term use
- **storage-agreement-expert** - Storage locker and ancillary agreements
  - Month-to-month storage arrangements
  - Simplified rent structures
  - Use restrictions and limited services

**Specialized Licenses & Infrastructure (1 skill)**
- **telecom-licensing-expert** - Telecommunications carrier access licenses
  - Carrier building access and equipment installation
  - Riser/conduit rights
  - CRTC regulatory compliance
  - Co-location arrangements

**Dispute Resolution (1 skill)**
- **lease-arbitration-expert** - Arbitration agreement drafting
  - Renewal rent determination frameworks
  - Arbitrator selection procedures
  - Baseball vs conventional arbitration
  - Cost allocation and enforceable awards

**Skill Features**:
- ✅ Standardized frontmatter (name, description, tags, capability, proactive)
- ✅ Comprehensive legal and practical guidance
- ✅ Risk analysis from both landlord and tenant perspectives
- ✅ Drafting checklists and negotiation strategies
- ✅ Common mistakes to avoid
- ✅ Sample language and workflow guidance

### Changed

#### Leasing Expert Agent

- **Updated**: `.claude/agents/leasing-expert.md` now includes complete skill inventory
- **Added**: "Specialized Skills Available" section with 13 skills organized by category
- **Added**: "When to Use Which Tool" guidance for both skills and slash commands
- **Added**: Workflow integration examples combining skills with slash commands
- **Updated**: Agent approach to include skill identification and invocation steps

**Agent Workflow Integration Examples**:
1. **Assignment Request**: `consent-to-assignment-expert` + `/tenant-credit` + `/compare-offers`
2. **Renewal Negotiation**: `/renewal-economics` + `lease-arbitration-expert` + `/market-comparison`
3. **Early Termination**: `lease-surrender-expert` + `/effective-rent` + `/rollover-analysis`
4. **New Lease**: `offer-to-lease-expert` + `/effective-rent` + `commercial-lease-expert` + `indemnity-expert`

#### Documentation

- Updated README.md to include skills section and version 1.2.0
- Updated CLAUDE.md with skills structure
- Reorganized features to list skills before calculators
- Added skills to project structure diagram
- Updated statistics: 13 expert skills, 25+ documentation files

### Fixed

#### Skill Frontmatter Standardization

- **6 skills** had missing frontmatter entirely (storage, surrender, share-transfer, sublease-consent, offer-to-lease, temporary-license)
- **7 skills** had incomplete frontmatter (indemnity, non-disturbance, arbitration, commercial-lease, telecom, waiver, assignment-consent)
- All 13 skills now have complete, consistent frontmatter:
  - `name`: Kebab-case identifier
  - `description`: Brief summary of expertise
  - `tags`: Array of relevant keywords
  - `capability`: Detailed description of what the skill provides
  - `proactive: true`: Enables proactive suggestion

### Technical Details

**Skill Invocation**:
```bash
# Invoke skill using Skill tool in Claude Code
Skill tool -> command: "temporary-license-expert"
```

**Skill Organization**:
```
.claude/skills/
├── Core: commercial-lease-expert
├── Security: indemnity-expert, non-disturbance-expert
├── Transfers: consent-to-assignment, consent-to-sublease, share-transfer-consent, lease-surrender
├── Preliminary: offer-to-lease, waiver-agreement, temporary-license, storage-agreement
├── Specialized: telecom-licensing-expert
└── Dispute: lease-arbitration-expert
```

**Integration with Existing Tools**:
- Skills complement slash commands (skills = expertise, commands = automation)
- Skills work with calculators (skills = analysis, calculators = computation)
- Skills integrate with leasing-expert agent for comprehensive guidance

## [1.1.0] - 2025-11-05

### Added

#### Rental Variance Analysis Module

**New Calculator**: `Rental_Variance/` - Three-way variance decomposition for rental revenue analysis

- **rental_variance_calculator.py** - Command-line calculator with JSON input/output
- **Variance Decomposition** - Isolates rate, area, and term variance components
- **Excel Methodology** - Based on proven `Rental Variance Analysis.xlsx` spreadsheet
- **Mathematical Foundation** - Variance formula: `Total = (BC)(A-D) + (CD)(B-E) + (DE)(C-F)`
- **Reconciliation Checks** - Validates variance components sum to total (±$0.01 tolerance)
- **Period-Aware Calculations** - Automatically handles partial periods and lease overlaps
- **Manual Adjustments** - Support for lease administration overrides
- **Multiple Output Formats** - Console summary, JSON results, markdown reports

**Sample Data**:
- `sample_variance_input.json` - 4 tenant scenarios from Excel "Proof of Concept" sheet
- `sample_variance_results.json` - Expected calculation results matching Excel formulas

**Documentation**:
- `Rental_Variance/README.md` - Complete module documentation with:
  - Theoretical foundation and mathematical proof
  - Usage examples (command-line and slash command)
  - Input/output format specifications
  - Interpretation guide for variance analysis
  - Common scenarios and applications
  - Excel formula mapping and validation

**Slash Command**:
- `/rental-variance` - Extract variance data from Excel/CSV/PDF and generate comprehensive analysis report
- Supports manual data entry when no file provided
- Automated workflow: Data → JSON → Calculator → Report

**Images and References**:
- `rentaldecomp.jpg` - Excel spreadsheet visualization
- `first_tenant*.png` - Sample tenant calculation screenshots
- `Rental Variance Analysis.xlsx` - Original Excel implementation (6 sheets)

**Key Features**:
- ✅ Period-aware term calculations using DAYS360 methodology
- ✅ Three-way decomposition (rate, area, term)
- ✅ Manual adjustments support
- ✅ Reconciliation validation
- ✅ Flexible input (Excel, CSV, PDF, manual)
- ✅ Professional markdown reports
- ✅ Zero external dependencies (Python stdlib only)

**Technical Details**:
- **Input Format**: JSON with actual vs budget data (dates, rates, areas, terms)
- **Output Format**: Console summary, JSON results, timestamped markdown reports
- **Calculation Method**: Monthly rate conversion (annual $/sf ÷ 12), variance decomposition
- **Validation**: Mathematical proof ensures variance components sum correctly
- **Excel Compatibility**: Python results match Excel formulas exactly

### Changed

#### Slash Commands

- Updated Financial Analysis category to include `/rental-variance` (now 7 commands total)
- Total slash commands increased from 19 to 20

#### Documentation

- Updated `CLAUDE.md` to include:
  - `Rental_Variance/` in project structure
  - `/rental-variance` in Financial Analysis commands list
  - Added rental variance to quick start examples
- Updated `.claude/commands/README.md` to document `/rental-variance` command

#### Project Structure

```
├── Rental_Variance/        # NEW - Variance decomposition analysis
│   ├── rental_variance_calculator.py
│   ├── sample_variance_input.json
│   ├── sample_variance_results.json
│   └── README.md
```

### Fixed

#### Sample Data Accuracy

- Replaced generic sample data with actual data from Excel spreadsheet
- Updated tenant scenarios to match "Proof of Concept" sheet rows 9, 10, 12, 16
- Validated calculation results against Excel formulas
- Ensured reconciliation checks pass for all sample tenants

### Technical Notes

**Variance Decomposition Formula**:
```
Rate Variance = (B × C) × (A - D)  where A=Actual Rate, B=Actual Area, C=Actual Term
                                         D=Budget Rate

Area Variance = (C × D) × (B - E)  where E=Budget Area

Term Variance = (D × E) × (C - F)  where F=Budget Term

Total Variance = Rate + Area + Term = ABC - DEF
```

**Mathematical Proof**:
```
(BC)(A-D) + (CD)(B-E) + (DE)(C-F)
= ABC - BCD + BCD - CDE + CDE - DEF
= ABC - DEF ✓
```

**Applications**:
1. Budget vs Actual Analysis - Monthly/quarterly variance reporting
2. Lease Negotiation Impact - Quantify negotiation outcomes
3. Portfolio Performance - Track leasing trends
4. Forecasting Refinement - Improve budget accuracy
5. Asset Management - Identify underperforming assets

## [1.0.0] - 2025-10-31

### Added

#### Core Infrastructure
- **Shared_Utils/** - Centralized financial utilities module
  - `financial_utils.py` - NPV, IRR, PV, rate conversions, financial ratios, statistics (58 tests)
  - Complete Python package with `__init__.py`
  - 24,990 lines of tested financial calculation functions

#### Calculators (5 modules)

1. **Effective Rent Calculator** (`Eff_Rent_Calculator/`)
   - Net Effective Rent (NER) and Gross Effective Rent (GER) calculation
   - NPV analysis comparing rent vs. costs
   - Breakeven analysis (unlevered, levered, with capital recovery)
   - Investment recommendations (Approve/Negotiate/Reject)
   - Ponzi Rental Rate (PRR) framework implementation
   - JSON input/output with BAF format
   - Automated PDF → JSON → Python → Report workflow

2. **Rental Yield Curve Calculator** (`Rental_Yield_Curve/`)
   - Term structure pricing using implied termination options
   - Black-Scholes option valuation framework
   - Solves for indifference pricing between lease terms
   - Market-to-market multiplier support
   - Command-line interface with full parameter control

3. **IFRS 16/ASC 842 Calculator** (`IFRS16_Calculator/`)
   - Lease liability calculation (present value of payments)
   - Right-of-Use (ROU) asset calculation
   - Monthly amortization schedules with interest expense tracking
   - Straight-line depreciation schedules
   - Annual summaries with P&L and balance sheet impact
   - Sensitivity analysis on discount rates and lease terms
   - CSV export (amortization, depreciation, annual summary)
   - Supports both annuity due and ordinary annuity
   - Variable payment schedules with escalations and free rent
   - Complete journal entries for initial recognition and monthly accounting

4. **Tenant Credit Analysis** (`Credit_Analysis/`)
   - 15+ financial ratio calculations (liquidity, leverage, profitability, rent coverage)
   - Weighted credit scoring algorithm (100-point scale)
   - Credit rating assignment (A through F)
   - Default probability estimation by rating
   - Expected loss calculation (PD × Exposure × LGD)
   - Risk-adjusted security recommendations (rent deposit, LC, guarantee)
   - Multi-year trend analysis
   - Red flag identification
   - Automated risk assessment and approval recommendations

5. **Renewal Economics Calculator** (`Renewal_Analysis/`)
   - Renewal vs. relocation NPV comparison
   - Net Effective Rent (NER) calculation for both scenarios
   - Internal Rate of Return (IRR) for relocation investment
   - Breakeven rent analysis
   - Payback period calculation
   - Comprehensive cost modeling (TI, moving, IT, downtime, customer loss)
   - Sensitivity analysis on rent, TI costs, and disruption
   - Investment recommendation (RENEW/RELOCATE/NEGOTIATE)

#### Slash Commands (19 total)

Organized into 5 categories in `.claude/commands/`:

**Abstraction (2 commands)**
- `/abstract-lease` - Extract lease terms using 24-section template (industrial/office)
- `/critical-dates` - Extract timeline and critical dates

**Financial Analysis (6 commands)**
- `/effective-rent` - NER, NPV, breakeven analysis
- `/renewal-economics` - Renewal vs. relocation economic analysis
- `/tenant-credit` - Credit scoring and risk assessment
- `/option-value` - Real options valuation using Black-Scholes
- `/market-comparison` - Market rent benchmarking
- `/rollover-analysis` - Portfolio lease expiry analysis

**Accounting (1 command)**
- `/ifrs16-calculation` - IFRS 16/ASC 842 lease accounting

**Comparison (4 commands)**
- `/compare-amendment` - Compare lease amendment against original
- `/compare-offers` - Compare inbound vs. outbound lease offers
- `/compare-precedent` - Compare draft lease against standard form
- `/lease-vs-lease` - General lease-to-lease comparison

**Compliance (6 commands)**
- `/assignment-consent` - Assignment and subletting consent analysis
- `/default-analysis` - Default provisions and cure periods
- `/environmental-compliance` - Environmental obligations review
- `/estoppel-certificate` - Estoppel certificate generation
- `/insurance-audit` - Insurance requirement verification
- `/notice-generator` - Generate lease notices (renewal, termination, etc.)

#### Templates

**Industrial Lease Templates** (`Templates/Industrial/`)
- 24-section comprehensive template (Markdown, JSON, JSON Schema)
- ANSI/BOMA Z65.2-2012 Method A measurement standard
- Industrial-specific provisions (manufacturing, warehouse, distribution)

**Office Lease Templates** (`Templates/Office/`)
- 24-section comprehensive template (Markdown, JSON, JSON Schema)
- ANSI/BOMA Office Buildings Standard measurement
- Office-specific provisions (business hours, parking, HVAC)

**Template Features**:
- Document information and metadata
- Parties (landlord, tenant, guarantor)
- Premises details with measurement standards
- Term provisions with renewal options
- Rent schedules and escalations
- Operating costs and tax allocations
- Use restrictions and operations
- Maintenance and repair obligations
- Insurance and indemnity requirements
- Assignment and subletting provisions
- Default remedies and cure periods
- Standard schedules A-J
- Critical dates summary tables
- Financial obligations summaries
- Key issues and risk analysis

#### Documentation

- `CLAUDE.md` - Project overview and quick start guide
- `README.md` - Slash commands comprehensive documentation
- `CHANGELOG.md` - This file
- Calculator-specific READMEs:
  - `Eff_Rent_Calculator/README.md` - Effective rent calculator documentation
  - `Eff_Rent_Calculator/BAF_INPUT_FORMAT.md` - JSON input format reference
  - `Eff_Rent_Calculator/RENTAL_YIELD_CURVE_README.md` - Yield curve documentation
  - `IFRS16_Calculator/README_IFRS16_CALCULATOR.md` - IFRS 16 calculator guide
  - `Shared_Utils/README_FINANCIAL_UTILS.md` - Financial utilities API reference

#### Test Suites

Complete test coverage for all calculators:
- `Tests/test_financial_utils.py` - 58 tests for shared utilities
- `Tests/test_ifrs16_calculator.py` - 30+ tests for lease accounting
- `Tests/test_renewal_analysis.py` - 25+ tests for renewal economics
- `Tests/test_credit_analysis.py` - 20+ tests for credit scoring

All tests passing with comprehensive edge case coverage.

#### Automated Workflows

All slash commands follow standardized **PDF → JSON → Python → Report** pipeline:
1. Extract data from PDF/DOCX using Claude's document analysis
2. Generate structured JSON input files
3. Run Python calculators with validated inputs
4. Create timestamped markdown reports in `Reports/` folder
5. Export CSV schedules for spreadsheet analysis

#### File Naming Conventions

**Reports Folder** - Mandatory timestamp prefix format:
- Format: `YYYY-MM-DD_HHMMSS_[description].md`
- Timezone: Eastern Time (ET/EST/EDT)
- Example: `2025-10-31_143022_lease_abstract_acme_corp.md`

#### Reference Documents

**Planning Folder**:
- `Multi_Tenant_Industrial.md` - Full 2,000+ line Minden Gross industrial lease
- `Multi_Tenant_Office.md` - Full 2,000+ line Minden Gross office lease
- Complete standard lease language for reference

### Changed

#### Project Structure

Reorganized from flat structure to modular architecture:

**Before**: Single `Eff_Rent_Calculator/` with mixed utilities
**After**: Dedicated modules with shared utilities

```
├── Shared_Utils/           # NEW - Shared financial utilities
├── Eff_Rent_Calculator/    # Focused on effective rent only
├── Rental_Yield_Curve/     # Separated yield curve calculator
├── IFRS16_Calculator/      # NEW - Lease accounting
├── Credit_Analysis/        # NEW - Tenant credit
├── Renewal_Analysis/       # NEW - Renewal economics
├── Planning/               # Reference documents
├── Templates/              # Lease templates (Industrial/Office)
├── Reports/                # Generated analysis (timestamped)
└── .claude/commands/       # Organized slash commands
    ├── Abstraction/
    ├── Financial_Analysis/
    ├── Accounting/
    ├── Comparison/
    └── Compliance/
```

#### Import Structure

- Moved `financial_utils.py` from `Eff_Rent_Calculator/` to `Shared_Utils/`
- Updated all calculator imports to use `Shared_Utils/`
- Created proper Python package with `__init__.py`
- Standardized import paths across all modules

#### Slash Commands Organization

- Moved from flat 19-file structure to 5 categorized subdirectories
- Added comprehensive `README.md` in commands directory
- Maintained backward compatibility (commands work same as before)

### Fixed

#### IFRS 16 Calculator
- Corrected function names: `calculate_ifrs16()` vs `calculate_ifrs16_accounting()`
- Fixed method names: `print_summary()` vs `print_lease_summary()`
- Standardized result object field names for consistency
- Fixed annuity due vs ordinary annuity treatment for first payment

#### Renewal Analysis
- Fixed dataclass field name mismatches (`area_sf` → `rentable_area_sf`)
- Corrected function signature: `print_comparison_report()` takes single argument
- Fixed NPV field access in nested result objects
- Resolved DataFrame boolean ambiguity in sensitivity analysis
- Corrected attribute names: `ner_psf` → `net_effective_rent_psf`

#### Test Suite Imports
- Updated all test files to use correct module paths
- Added `Shared_Utils/` to Python path in test files
- Fixed cross-module imports for calculator tests

### Technical Details

#### Dependencies
- Python 3.12+
- NumPy - Numerical operations and array handling
- Pandas - DataFrame operations and CSV export
- SciPy - Optimization algorithms (IRR calculation via Newton's method)
- markitdown[docx] - DOCX to Markdown conversion

#### Performance
- All PV calculations: O(n) where n = number of cash flows
- Amortization schedules: O(n) where n = number of periods
- IRR convergence: Typically <10 iterations using Newton's method
- Credit scoring: O(1) ratio calculations

#### Standards Compliance
- **IFRS 16** (International) - Lease accounting for all leases on balance sheet
- **ASC 842** (US GAAP) - Finance lease methodology
- **ANSI/BOMA Z65.2-2012 Method A** - Industrial building measurement
- **ANSI/BOMA Office Buildings Standard** - Office space measurement

#### Financial Methodologies
- **Ponzi Rental Rate (PRR)** - Effective rent framework with capital recovery
- **Black-Scholes** - Real options valuation for lease terms
- **NPV/IRR** - Standard capital budgeting analysis
- **Annuity Due** - Commercial lease payment timing (advance payment)

### Project Statistics

- **Total Python Modules**: 8 (5 calculators + 1 shared + 2 runners)
- **Total Test Files**: 4 (with 130+ total tests)
- **Total Slash Commands**: 19 (organized in 5 categories)
- **Total Templates**: 6 files (2 property types × 3 formats)
- **Documentation Pages**: 10+ comprehensive guides
- **Lines of Code**: ~150,000 (including templates and documentation)

### Contributors

- **Claude Code** - AI-powered development assistant by Anthropic
- **Created**: October 30-31, 2025
- **GitHub Issues Closed**: #3, #5, #6, #8

---

## Release Notes

**Version 1.0.0** represents the initial stable release of the Commercial Real Estate Lease Analysis Toolkit. This release provides a complete, production-ready suite of tools for:

- Lease abstraction and analysis
- Financial modeling and investment analysis
- Lease accounting under IFRS 16/ASC 842
- Tenant credit risk assessment
- Renewal vs. relocation decision support
- Market analysis and benchmarking
- Compliance verification and documentation

All calculators have been tested with real-world lease scenarios and produce accurate, auditable results suitable for professional use in commercial real estate portfolio management.

### Upgrade Notes

This is the initial release. Future versions will maintain backward compatibility with:
- JSON input formats
- Slash command syntax
- Calculator API interfaces
- Report output formats

---

[1.0.0]: https://github.com/reggiechan74/leasing-expert/releases/tag/v1.0.0
[1.1.0]: https://github.com/reggiechan74/leasing-expert/releases/tag/v1.1.0
[1.2.0]: https://github.com/reggiechan74/leasing-expert/releases/tag/v1.2.0
[1.3.0]: https://github.com/reggiechan74/leasing-expert/releases/tag/v1.3.0
[1.4.0]: https://github.com/reggiechan74/leasing-expert/releases/tag/v1.4.0
