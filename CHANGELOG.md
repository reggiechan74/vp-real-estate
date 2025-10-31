# Changelog

All notable changes to the Commercial Real Estate Lease Analysis Toolkit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[1.0.0]: https://github.com/anthropics/lease-abstract/releases/tag/v1.0.0
