# CLAUDE.md

Commercial real estate lease analysis toolkit: abstraction, financial analysis, and rental yield curves.

## Structure

```
├── Shared_Utils/           # Shared financial utilities (NPV, IRR, PV, ratios, statistics)
├── Eff_Rent_Calculator/    # Effective rent, NPV, breakeven analysis
├── Rental_Yield_Curve/     # Term structure pricing using implied termination options
├── Rental_Variance/        # Rental variance decomposition (rate, area, term)
├── IFRS16_Calculator/      # IFRS 16/ASC 842 lease accounting (liability, ROU asset, schedules)
├── Credit_Analysis/        # Tenant credit scoring and financial analysis
├── Renewal_Analysis/       # Renewal vs. relocation economic analysis
├── Planning/               # Source lease documents
├── Templates/              # Industrial/Office lease templates (24 sections, MD/JSON/Schema)
├── Reports/                # Generated abstracts & analysis (timestamp prefix required)
└── .claude/                # Claude Code configuration
    ├── commands/           # Slash commands (21 commands in 5 categories)
    │   ├── Abstraction/        # abstract-lease, critical-dates
    │   ├── Financial_Analysis/ # effective-rent, renewal-economics, tenant-credit, option-value, rental-variance, etc.
    │   ├── Accounting/         # ifrs16-calculation
    │   ├── Comparison/         # compare-amendment, compare-offers, compare-precedent, lease-vs-lease
    │   └── Compliance/         # assignment-consent, default-analysis, estoppel-certificate, etc.
    ├── skills/             # Expert skills (13 specialized skills)
    │   ├── Core: commercial-lease-expert
    │   ├── Security: indemnity-expert, non-disturbance-expert
    │   ├── Transfers: consent-to-assignment, consent-to-sublease, share-transfer-consent, lease-surrender
    │   ├── Preliminary: offer-to-lease, waiver-agreement, temporary-license, storage-agreement
    │   ├── Specialized: telecom-licensing-expert
    │   └── Dispute: lease-arbitration-expert
    └── agents/             # Sub-agents
        └── leasing-expert  # Leasing specialist with skill integration
```

## File Naming: Reports Folder

**CRITICAL**: All files in `Reports/` MUST use timestamp prefix:

**Format**: `YYYY-MM-DD_HHMMSS_[filename].md` (Eastern Time)

**Example**: `2025-10-31_143022_lease_abstract_acme_corp.md`

## Slash Commands (22 total)

All commands follow **PDF → JSON → Python → Report** automated workflow.

### Abstraction (2)
- `/abstract-lease` - Extract lease terms using 24-section template
- `/critical-dates` - Extract timeline and critical dates

### Financial Analysis (9)
- `/effective-rent` - NER, NPV, breakeven (Ponzi Rental Rate)
- `/renewal-economics` - Renewal vs. relocation NPV analysis
- `/tenant-credit` - Credit scoring and risk assessment
- `/option-value` - Real options valuation (Black-Scholes)
- `/market-comparison` - Market rent benchmarking
- `/rollover-analysis` - Portfolio lease expiry analysis
- `/rental-variance` - Rental variance decomposition by rate, area, and term
- `/relative-valuation` - MCDA competitive positioning with 25 variables, personas, and filters
- `/recommendation-memo` - VTS approval memo with tenant analysis and deal comparison

### Accounting (1)
- `/ifrs16-calculation` - IFRS 16/ASC 842 lease accounting

### Comparison (4)
- `/compare-amendment` - Amendment vs. original lease
- `/compare-offers` - Inbound vs. outbound offers
- `/compare-precedent` - Draft vs. standard form
- `/lease-vs-lease` - General lease comparison

### Compliance (7)
- `/assignment-consent` - Assignment/subletting analysis
- `/default-analysis` - Default provisions and cure periods
- `/environmental-compliance` - Environmental obligations
- `/estoppel-certificate` - Estoppel generation
- `/insurance-audit` - Insurance requirement verification
- `/notice-generator` - Generate lease notices
- `/work-letter` - Generate work letter from TI provisions

**See**: `.claude/commands/README.md` for detailed documentation

## Specialized Skills (13 total)

Use the Skill tool to invoke deep expertise on specific agreement types:

### Core Lease Agreements
- **commercial-lease-expert** - General lease negotiation, net lease structures, deal structuring

### Security & Protection
- **indemnity-expert** - Indemnity agreements, bankruptcy-proof provisions
- **non-disturbance-expert** - SNDA agreements, foreclosure protection

### Lease Modifications & Transfers
- **consent-to-assignment-expert** - Assignment consent, privity analysis
- **consent-to-sublease-expert** - Sublease consent, three-party structures
- **share-transfer-consent-expert** - Change of control, corporate restructuring
- **lease-surrender-expert** - Early termination, mutual release

### Preliminary & Ancillary Agreements
- **offer-to-lease-expert** - Offers to lease, LOIs, term sheets
- **waiver-agreement-expert** - Conditional waivers, counter-offers
- **temporary-license-expert** - Short-term licenses (1 day - 3 months)
- **storage-agreement-expert** - Storage lockers, ancillary space

### Specialized Licenses
- **telecom-licensing-expert** - Carrier access, CRTC compliance

### Dispute Resolution
- **lease-arbitration-expert** - Arbitration agreements, rent determination

## Quick Start Examples

```bash
# Lease abstraction
/abstract-lease path/to/lease.docx

# Financial analysis
/effective-rent path/to/lease.pdf
/tenant-credit path/to/financials.pdf
/rental-variance path/to/variance_data.xlsx

# IFRS 16 accounting
/ifrs16-calculation path/to/lease.pdf 5.5

# Renewal economics
/renewal-economics path/to/current-lease.pdf

# Invoke expert skills
# (Use Skill tool in Claude Code)
Skill -> commercial-lease-expert    # For general lease review
Skill -> temporary-license-expert   # For short-term license agreements
Skill -> consent-to-assignment-expert # For assignment consent requests

# Convert DOCX to markdown
markitdown document.docx -o output.md
```

## Templates

**Industrial**: `Templates/Industrial/` (ANSI/BOMA Z65.2-2012 Method A)
**Office**: `Templates/Office/` (ANSI/BOMA Office Buildings Standard)

Each has: `*_template.md`, `*_template.json`, `*_schema.json`

## JSON Schema Standards

When creating JSON schema validation documents (not data templates), follow these requirements:

**Schema Version**: Use JSON Schema **Draft 2020-12** or **Draft-07**
- Specify `"$schema"` at document root
- Draft 2020-12: `"$schema": "https://json-schema.org/draft/2020-12/schema"`
- Draft-07: `"$schema": "http://json-schema.org/draft-07/schema#"`

**Required Elements**:
1. **Object Structure**: Define `type`, `properties`, `additionalProperties`
2. **Type Definitions**: Specify data types for all fields (string, number, integer, boolean, array, object)
3. **Required Properties**: List mandatory fields in `required` array
4. **Validation Rules**: Add constraints appropriate to field type:
   - Numbers: `minimum`, `maximum`, `exclusiveMinimum`, `exclusiveMaximum`
   - Strings: `minLength`, `maxLength`, `pattern`, `format`, `enum`
   - Arrays: `minItems`, `maxItems`, `uniqueItems`
   - Objects: `minProperties`, `maxProperties`

**Example Structure**:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.com/schemas/my-schema.json",
  "title": "Schema Title",
  "description": "Schema description",
  "type": "object",
  "required": ["field1", "field2"],
  "properties": {
    "field1": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Field description"
    }
  },
  "additionalProperties": false
}
```

**Naming Convention**: Use `*_schema.json` suffix for validation schemas, `*_template.json` for data templates

## Key Lease Provisions

**Net Lease**: Tenant pays base rent + proportionate share of opex/taxes/mgmt fees
**Proportionate Share**: Rentable Area ÷ Total Building Area
**Standard Schedules**: A-J (Legal, Plan, Work, Deposit, Environmental, Rules, Special Provisions, Indemnity, PAD, LC)
**Schedule G**: Special Provisions - often contains critical custom terms that override standard provisions

**Typical Values**:
- Management fees: 5% (multi-tenant), 3% (single/landlord), 2.75% (single/tenant)
- Default cure: 5-10 days (rent), 15-30 days (covenants)
- Insurance: $2M-$5M CGL, replacement cost property, 12mo business interruption

## Reference

`Planning/Multi_Tenant_Industrial.md` and `Planning/Multi_Tenant_Office.md` - Full Minden Gross templates (2000+ lines)
