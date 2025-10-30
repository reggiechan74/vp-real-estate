# Commercial Lease Abstraction & Analysis Toolkit

A comprehensive toolkit for abstracting, analyzing, and comparing commercial real estate lease documents. This repository includes templates, slash commands, and financial calculators for industrial and office leases.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Effective Rent Calculator](#effective-rent-calculator)
- [Rental Yield Curve Calculator](#rental-yield-curve-calculator)
- [Slash Commands](#slash-commands)
- [Project Structure](#project-structure)

## Overview

This toolkit provides:

1. **Standardized lease abstract templates** (Industrial & Office)
2. **Claude Code slash commands** for automated lease analysis
3. **Effective Rent Calculator** - Python tool for Net Effective Rent (NER), NPV, and breakeven analysis
4. **Rental Yield Curve Calculator** - Generate rental rates for any lease term using implied termination options
5. **Document comparison tools** for amendments, offers, and precedent forms

## Installation

### Prerequisites

- Python 3.8+
- pip
- Claude Code (for slash commands)

### Setup

```bash
# For DOCX conversion support
pip install 'markitdown[docx]'

# For calculator (see Eff_Rent_Calculator/)
cd Eff_Rent_Calculator
pip install -r requirements.txt
```

## Quick Start

### 1. Abstract a Lease

```bash
/abstract-lease path/to/lease.docx
```

For JSON output:
```bash
/abstract-lease path/to/lease.md -json
```

### 2. Calculate Financial Metrics

```bash
cd Eff_Rent_Calculator
python3 eff_rent_calculator.py baf_input_simple.json
```

See `Eff_Rent_Calculator/README.md` for complete documentation.

## Effective Rent Calculator

A Python tool for comprehensive lease financial analysis:

- **Net Effective Rent (NER)** - Annuity due of present value of net rent cash flows
- **Gross Effective Rent (GER)** - Includes operating costs
- **NPV Analysis** - Discounted cash flows at monthly compounding
- **Breakeven Analysis** - Unlevered, levered, with capital recovery (Inwood sinking fund)

### Quick Start

```bash
cd Eff_Rent_Calculator
python3 eff_rent_calculator.py baf_input_simple.json
```

### Documentation

See `Eff_Rent_Calculator/` folder for:
- `README.md` - Complete documentation
- `BAF_INPUT_FORMAT.md` - JSON format reference
- `baf_input_simple.json` - Example input template
- `baf_input_example.json` - Full 10-year industrial lease example
- `baf_input_test2.json` - Complex varied rent schedule example

### Key Features

✅ **Validated calculations** - tested against industry-standard Excel models
✅ **JSON input** - no code editing required
✅ **Complete analysis** - NPV, NER, GER, breakeven, investment assessment
✅ **Production ready** - fully tested and documented

### Theoretical Foundation

The calculator implements the **Ponzi Rental Rate (PRR)** framework:

Chan, R. (2015). "Understanding the Ponzi Rental Rate: The Challenges with Using Net Effective Rents to Analyze Prospective Lease Deals within Real Estate Investment Trusts." *Real Estate Finance*, Vol. 32, No. 2, pp. 48-61.

The PRR provides objective breakeven rental rates that account for dividends, debt service, and building depreciation—not just subjective market expectations. See `Eff_Rent_Calculator/README.md` for detailed theoretical discussion.

## Rental Yield Curve Calculator

A Python tool for generating rental rates across different lease terms using **implied termination options**:

- **Term Structure Pricing** - Calculate fair rent for any lease term from 1 month to max term
- **Inverted Yield Curve** - Longer terms = lower rents (opposite of bonds)
- **Implied Options** - Uses economic equivalence between short-term + MTM vs. long-term with termination option
- **Negotiation Tool** - Objective framework for pricing non-standard lease terms

### Quick Start

```bash
cd Eff_Rent_Calculator

# Default: 5-year base at $8.00, 125% MTM
python3 rental_yield_curve.py

# Custom parameters
python3 rental_yield_curve.py --base-term 120 --base-rate 15.00 --mtm-multiplier 1.40

# Generate all months
python3 rental_yield_curve.py --all-months
```

### Example Output

| Term | Rate ($/sf/year) | Premium over 5-year |
|------|------------------|---------------------|
| 1 Month | $10.00 | +25.0% |
| 6 Months | $9.75 | +21.9% |
| 1 Year | $9.52 | +19.0% |
| 2 Years | $9.08 | +13.5% |
| 3 Years | $8.68 | +8.5% |
| 4 Years | $8.32 | +4.1% |
| 5 Years | $8.00 | 0.0% |

### Theoretical Foundation

Chan, R. (2016). "Deconstruction the Rental Rate Term Structure Model Using Implied Options." Draft 2016-02-12.

See `Eff_Rent_Calculator/Rental_Term_Structure_Formal_Paper.md` for full academic treatment with mathematical proofs.

**Key Insight**: A tenant is indifferent between paying $8.00 for 4 years then $10.00 MTM for 1 year versus paying $8.32 for 5 years with monthly termination option after year 4. The $0.32 premium is the value of the embedded termination option.

### Use Cases

- **Negotiation**: Tenant wants 3-year term instead of 5-year? Know the fair premium ($8.68 vs $8.00)
- **Offer Menu**: Present multiple term options at proper pricing
- **Portfolio Mix**: Optimize tenant mix across different terms
- **Renewal Pricing**: Fair rates for shorter renewal terms

### Documentation

See `Eff_Rent_Calculator/` folder for:
- `RENTAL_YIELD_CURVE_README.md` - Complete documentation
- `rental_yield_curve.py` - Standalone calculator
- `test_yield_curve_validation.py` - Validation against paper (100% accuracy)
- `Rental_Term_Structure_Formal_Paper.md` - Formal academic paper with LaTeX math
- `industrial_10yr_yield_curve.json` - Example output (10-year industrial)

## Slash Commands

### /abstract-lease

Abstract a commercial lease into standardized 24-section format.

```bash
/abstract-lease path/to/lease.docx        # Concise markdown
/abstract-lease path/to/lease.md -json    # Comprehensive JSON
```

### /effective-rent

Analyze lease deal economics using the Ponzi Rental Rate framework. Extracts financial terms from lease documents and quotes, runs NPV/NER analysis, and generates investment recommendation report.

```bash
/effective-rent path/to/lease-offer.pdf
/effective-rent path/to/lease.docx path/to/ti-quote.pdf
```

**Process:**
1. Extracts all financial terms (rent, TI, commissions, free rent, etc.)
2. Generates JSON input file in `Eff_Rent_Calculator/deals/`
3. Runs effective rent calculator
4. Creates comprehensive markdown report in `Reports/`

**Output:**
- Net Effective Rent (NER) calculation
- NPV analysis (rent vs. costs)
- Breakeven analysis (unlevered, levered, with capital recovery)
- Investment recommendation (Approve/Negotiate/Reject)
- Sensitivity analysis

**Features:**
- Extracts from lease documents and quote PDFs
- Calculates objective breakeven thresholds
- Accounts for dividends, debt service, and building depreciation
- Provides actionable investment recommendations
- Documents all assumptions and limitations

### /compare-amendment

Compare lease amendment against original + previous amendments.

```bash
/compare-amendment amendment.docx ./lease-history/
```

Features:
- Verifies recitals accuracy
- Tracks cumulative changes
- Identifies conflicts
- Business impact analysis

### /compare-offers

Compare inbound vs outbound negotiation offers.

```bash
/compare-offers inbound-offer.docx outbound-offer.docx
```

Features:
- Movement tracking (Accepted/Rejected/Countered)
- Negotiation scorecard
- Strategic recommendations

### /compare-precedent

Compare draft lease against standard precedent form.

```bash
/compare-precedent draft-lease.docx standard-form.docx
```

Features:
- Section-by-section comparison
- Identifies deviations
- Priority categorization (Tier 1/2/3)
- Negotiation strategy


## Project Structure

```
lease-abstract/
├── README.md                       # This file
├── CLAUDE.md                       # Claude Code project instructions
│
├── Eff_Rent_Calculator/            # Financial calculators
│   ├── eff_rent_calculator.py      # NER/NPV/breakeven calculator
│   ├── rental_yield_curve.py       # Term structure calculator
│   ├── test_yield_curve_validation.py  # Validation tests
│   ├── README.md                   # Calculator documentation
│   ├── RENTAL_YIELD_CURVE_README.md  # Yield curve docs
│   ├── BAF_INPUT_FORMAT.md         # JSON format reference
│   ├── Rental_Term_Structure_Formal_Paper.md  # Academic paper
│   ├── baf_input_simple.json       # Example: Office 5-year
│   ├── baf_input_example.json      # Example: Industrial 10-year
│   ├── baf_input_test2.json        # Example: Complex rent schedule
│   └── deals/                      # Generated deal analysis inputs
│
├── .claude/commands/               # Slash commands
│   ├── abstract-lease.md
│   ├── effective-rent.md
│   ├── compare-amendment.md
│   ├── compare-offers.md
│   └── compare-precedent.md
│
├── Templates/                      # Lease abstract templates
│   ├── Industrial/
│   │   ├── industrial_lease_abstract_template.md
│   │   ├── industrial_lease_abstract_template.json
│   │   └── industrial_lease_abstract_schema.json
│   └── Office/
│       ├── office_lease_abstract_template.md
│       ├── office_lease_abstract_template.json
│       └── office_lease_abstract_schema.json
│
├── Planning/                       # Source lease documents
│   ├── Multi_Tenant_Industrial.md  # Reference: Industrial lease
│   └── Multi_Tenant_Office.md      # Reference: Office lease
│
└── Reports/                        # Generated abstracts & analysis
```

---

**Last Updated:** 2025-10-30
