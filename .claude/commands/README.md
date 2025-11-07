# Slash Commands

Automated workflows for commercial real estate lease analysis.

## Structure

Commands are organized into 6 categories (25 total):

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

### 6. Utilities (1 command)

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

- **Effective Rent**: `Eff_Rent_Calculator/`
- **IFRS 16**: `IFRS16_Calculator/`
- **Tenant Credit**: `Credit_Analysis/`
- **Renewal Economics**: `Renewal_Analysis/`
- **Rental Variance**: `Rental_Variance/`
- **Shared Utilities**: `Shared_Utils/`

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
