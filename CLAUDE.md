# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Commercial real estate lease analysis toolkit with:
1. **Lease abstraction** - Standardized templates (industrial/office)
2. **Financial calculators** - NER, NPV, breakeven analysis
3. **Rental yield curve** - Term structure pricing using implied options
4. **Slash commands** - Automated workflows via Claude Code

## Repository Structure

```
/workspaces/lease-abstract/
├── Eff_Rent_Calculator/              # Financial calculators
│   ├── eff_rent_calculator.py        # NER/NPV/breakeven calculator
│   ├── rental_yield_curve.py         # Term structure calculator
│   ├── test_yield_curve_validation.py  # Validation tests
│   ├── README.md                     # Calculator documentation
│   ├── RENTAL_YIELD_CURVE_README.md  # Yield curve docs
│   ├── BAF_INPUT_FORMAT.md           # JSON format reference
│   ├── Rental_Term_Structure_Formal_Paper.md  # Academic paper (LaTeX)
│   ├── baf_input_*.json              # Example inputs
│   └── deals/                        # Generated deal inputs
├── Planning/                         # Source lease documents
├── Templates/                        # Lease abstract templates (Industrial/Office)
├── Reports/                          # Generated abstracts & analysis
└── .claude/commands/                 # Slash commands
    ├── abstract-lease.md
    ├── effective-rent.md
    ├── compare-amendment.md
    ├── compare-offers.md
    └── compare-precedent.md
```

## Quick Start: Abstracting a Lease

### Using the /abstract-lease Command

The fastest way to abstract a lease is using the `/abstract-lease` slash command:

```
/abstract-lease path/to/lease.docx
/abstract-lease path/to/lease.md
/abstract-lease https://example.com/lease.pdf
```

This command will:
1. Automatically load the document (converting from DOCX if needed)
2. Determine if it's an industrial or office lease
3. Extract all information following the appropriate 24-section template
4. Provide a complete markdown abstract with analysis

### Using the /effective-rent Command

For financial analysis of lease deals using the Ponzi Rental Rate (PRR) framework:

```
/effective-rent path/to/lease-offer.pdf
/effective-rent path/to/lease.docx path/to/ti-quote.pdf
```

This command will:
1. Extract all financial terms from the lease document (rent, TI, commissions, free rent)
2. Extract costs from quote/invoice PDFs (if provided)
3. Generate JSON input file in `Eff_Rent_Calculator/deals/`
4. Run the effective rent calculator
5. Create comprehensive investment analysis report in `Reports/`

The report includes:
- Net Effective Rent (NER) and Gross Effective Rent (GER)
- NPV analysis (rent vs. costs)
- Breakeven analysis (unlevered, levered, with capital recovery)
- Investment recommendation (Approve/Negotiate/Reject)
- Sensitivity analysis
- All assumptions and limitations documented

### Rental Yield Curve Calculator

Generate rental rates for any lease term using implied termination options:

```bash
cd Eff_Rent_Calculator
python3 rental_yield_curve.py --base-term 60 --base-rate 8.00 --mtm-multiplier 1.25
```

**Use for**: Pricing non-standard lease terms (e.g., tenant wants 3-year instead of 5-year).

**Key concept**: Landlord indifferent between (A) base rate for N months + MTM for remainder vs (B) X rate for full term with termination option after N months. Solves for X.

**See**: `Eff_Rent_Calculator/RENTAL_YIELD_CURVE_README.md` for details.

## Document Processing Workflow

### Converting Lease Documents to Markdown

Use Microsoft's `markitdown` tool (already installed) to convert Word documents to markdown:

```bash
# Install markitdown with docx support (if not already installed)
pip install 'markitdown[docx]'

# Convert a single lease document
markitdown document.docx -o output.md

# Convert all Word docs in a directory
for file in *.docx; do
    markitdown "$file" -o "${file%.docx}.md"
done
```

**Note**: The `markitdown` package requires the `[docx]` extra to process Word documents. Ensure this is installed before attempting to convert DOCX files.

## Template Architecture

The project provides two sets of lease abstract templates for different property types:

### Industrial Leases
- **Location**: `Templates/Industrial/`
- **Measurement Standard**: ANSI/BOMA Z65.2-2012 - Method A (Industrial Buildings)
- **Typical Use**: Manufacturing, warehouse, distribution, industrial operations

### Office Leases
- **Location**: `Templates/Office/`
- **Measurement Standard**: ANSI/BOMA Office Buildings Standard
- **Typical Use**: Office space, professional services
- **Business Hours**: Typically 8 AM - 6 PM Mon-Fri, 9 AM - 5 PM Sat

### Template Formats

Each property type has three template formats:

1. **Markdown Template** (`*_template.md`)
   - Human-readable format for manual abstraction
   - 24 major sections covering all lease aspects
   - Includes document info, parties, premises, term, rent, obligations, etc.

2. **JSON Template** (`*_template.json`)
   - Structured data format for programmatic use
   - Pre-filled with null/empty values
   - Mirrors markdown structure in JSON

3. **JSON Schema** (`*_schema.json`)
   - Validation schema for JSON abstracts
   - Defines data types, required fields, enums
   - Use for automated validation of extracted data

## Template Sections Overview

Both industrial and office templates include 24 comprehensive sections:

1. **Document Information** - Metadata about the abstract
2. **Parties** - Landlord, Tenant, Indemnifier/Guarantor
3. **Premises** - Property details, area, permitted use
4. **Term** - Dates, renewal options, early termination
5. **Rent** - Basic rent schedule, escalations, additional rent
6. **Deposits & Security** - Rent deposits, letters of credit
7. **Operating Costs & Taxes** - Net lease provisions, cost allocations
8. **Use & Operations** - Permitted/prohibited uses, hours, signage
9. **Maintenance & Repairs** - Landlord vs tenant obligations
10. **Alterations & Improvements** - Work requirements, ownership
11. **Insurance & Indemnity** - Coverage requirements, liability
12. **Damage & Destruction** - Casualty provisions, rent abatement
13. **Assignment & Subletting** - Transfer restrictions, consent
14. **Default & Remedies** - Events of default, landlord remedies
15. **Services & Utilities** - What's provided, tenant responsibility
16. **Environmental** - Compliance, hazardous substances
17. **Subordination & Attornment** - SNDA, registration
18. **Notices** - Requirements and addresses
19. **End of Term** - Surrender requirements, overholding
20. **Special Provisions** - Custom terms
21. **Schedules & Exhibits** - Attached documents (A-J)
22. **Critical Dates Summary** - Timeline table
23. **Financial Obligations Summary** - Cost breakdown
24. **Key Issues & Risks** - Favorable/unfavorable terms analysis

## Working with Lease Documents

### Abstracting a New Lease

1. Convert the source document to markdown if in Word format
2. Identify the lease type (Industrial vs Office)
3. Use the appropriate template from `Templates/`
4. Extract key terms following the 24-section structure
5. For JSON output, validate against the corresponding schema

### Key Lease Terms to Extract

**Critical Financial Terms:**
- Basic rent amounts and schedule (by year)
- Rent escalation method (fixed %, CPI, market review)
- Operating costs allocation (proportionate share)
- Realty taxes responsibility
- Management fees
- Security deposits and letters of credit

**Critical Dates:**
- Commencement date
- Delivery date (if different)
- Expiry date
- Renewal option notice deadlines
- Term length

**Critical Obligations:**
- Maintenance responsibilities (landlord vs tenant)
- Insurance requirements and minimum coverage
- Permitted use restrictions
- Assignment/subletting consent requirements
- Default cure periods

### Standard Schedules in Multi-Tenant Leases

Most commercial leases include these standard schedules:
- **Schedule A**: Legal Description of Project
- **Schedule B**: Outline Plan of Premises
- **Schedule C**: Landlord's and Tenant's Work
- **Schedule D**: Rent Deposit Agreement
- **Schedule E**: Environmental Questionnaire
- **Schedule F**: Rules and Regulations
- **Schedule G**: Special Provisions (often contains key custom terms)
- **Schedule H**: Indemnity Agreement
- **Schedule I**: Pre-Authorized Debit (PAD) Authorization
- **Schedule J**: Letter of Credit Agreement

**Important**: Always review Schedule G (Special Provisions) carefully, as it often contains custom terms that override standard lease provisions.

## Lease Type Characteristics

### Net Leases
Both templates are based on "Net Lease" structures where the tenant pays:
- Base rent
- Proportionate share of operating costs
- Proportionate share of realty taxes
- Management fees
- Utilities (often separately metered)

This differs from "Gross Leases" where operating costs are included in base rent.

### Proportionate Share Calculation
```
Proportionate Share = Rentable Area of Premises / Total Rentable Area of Building
```

This percentage determines the tenant's share of common area costs, taxes, and other pass-through expenses.

## Common Lease Provisions to Note

**Measurement Standards:**
- Industrial: ANSI/BOMA Z65.2-2012 Method A
- Office: ANSI/BOMA Office Buildings Standard

**Typical Management Fees:**
- Multi-tenant building: 5% of gross project amounts or gross rent
- Single tenant (landlord managed): 3% of rent
- Single tenant (tenant managed): 2.75% of rent

**Typical Default Cure Periods:**
- Non-payment of rent: Usually 5-10 days
- Other covenant breaches: Usually 15-30 days
- Bankruptcy/insolvency: Often immediate default

**Insurance Minimums:**
- Commercial General Liability: Typically $2M-$5M
- Property Insurance: Replacement cost of improvements
- Business interruption: Often 12 months minimum

## Reference Documents

The `Planning/` directory contains reference lease documents:
- **Multi_Tenant_Industrial.md** - Full industrial lease template (Minden Gross)
- **Multi_Tenant_Office.md** - Full office lease template (Minden Gross)

These are comprehensive 2000+ line documents showing the full structure and detailed provisions of standard Canadian multi-tenant net leases. Use these as reference when:
- Understanding specific clause language
- Identifying standard vs custom provisions
- Verifying terminology and definitions
- Understanding the relationship between different lease sections
