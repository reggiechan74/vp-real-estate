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
├── Option_Valuation/       # Real options valuation (Black-Scholes) for lease flexibility
├── Rollover_Analysis/      # Portfolio lease expiry and renewal prioritization
├── Default_Calculator/     # Tenant default damage quantification
├── Relative_Valuation/     # MCDA competitive positioning (25 variables) + statistical analysis
├── MLS_Extractor/          # MLS PDF to Excel extraction with subject highlighting
├── Planning/               # Source lease documents
├── Templates/              # Industrial/Office lease templates (24 sections, MD/JSON/Schema)
├── Reports/                # Generated abstracts & analysis (timestamp prefix required)
└── .claude/                # Claude Code configuration
    ├── commands/           # Slash commands (25 commands in 6 categories)
    │   ├── Abstraction/        # abstract-lease, critical-dates
    │   ├── Financial_Analysis/ # effective-rent, renewal-economics, tenant-credit, option-value, rental-variance, etc.
    │   ├── Accounting/         # ifrs16-calculation
    │   ├── Comparison/         # compare-amendment, compare-offers, compare-precedent, lease-vs-lease
    │   ├── Compliance/         # assignment-consent, default-analysis, estoppel-certificate, etc.
    │   └── Utilities/          # convert-to-pdf
    ├── skills/             # Expert skills (15 specialized skills - auto-invoked)
    │   ├── Core: commercial-lease-expert/
    │   ├── Security: indemnity-expert/, non-disturbance-expert/
    │   ├── Transfers: consent-to-assignment-expert/, consent-to-sublease-expert/,
    │   │             share-transfer-consent-expert/, lease-surrender-expert/
    │   ├── Preliminary: offer-to-lease-expert/, waiver-agreement-expert/,
    │   │                temporary-license-expert/, storage-agreement-expert/
    │   ├── Specialized: telecom-licensing-expert/
    │   ├── Dispute: lease-arbitration-expert/
    │   └── Negotiation: negotiation-expert/, objection-handling-expert/
    └── agents/             # Sub-agents
        ├── reggie-chan-vp  # Reggie Chan, CFA, FRICS - VP of Leasing & Asset Management (20+ years)
        └── dennis          # Dennis - Strategic Advisor & Former Boss (36+ years, Opus model)
```

## Meet Reggie Chan - Your Leasing & Asset Management Expert

**Reggie Chan, CFA, FRICS** is your Vice President of Leasing and Asset Management with over 20 years of institutional real estate experience.

### Credentials
- **CFA** (Chartered Financial Analyst) - Expert in investment analysis and financial modeling
- **FRICS** (Fellow of the Royal Institution of Chartered Surveyors) - Senior professional in real estate valuation
- **VP of Leasing and Asset Management** - Executive-level commercial real estate professional

**Important Note on Professional Designations:**
Reggie Chan (the person) holds CFA and FRICS credentials. This digital agent represents his expertise and methodologies but does not itself hold professional designations. When describing the agent's outputs, use terms like "institutional-grade analysis" or "20+ years of property expertise" rather than "CFA-level" or "FRICS-equivalent" to accurately represent that this is a system built by a credentialed professional, not a credentialed entity itself.

### How to Work with Reggie
Simply address **"Reggie"** in your message to activate expert leasing and asset management guidance. Reggie provides:
- Lease deal evaluation and structuring advice
- Portfolio strategy and asset management recommendations
- Tenant credit assessment and risk analysis
- Negotiation strategy and objection handling
- Access to all 15 specialized skills and 24 slash commands

### Example Interactions
```
"Reggie, what do you think of this renewal offer?"
"Reggie, help me evaluate this tenant's creditworthiness"
"Reggie, how should I respond to their rent objection?"
```

Reggie combines institutional-grade analytical rigor with deep property expertise to deliver sophisticated deal evaluation balancing financial returns, risk management, and strategic positioning.

## Meet Dennis - Your Strategic Advisor

**Dennis** is a seasoned real estate executive with 36+ years of institutional real estate experience. Former president of a major institutional real estate operation (multi-billion dollar AUM, large team, millions of square feet), he consistently beat benchmarks and survived multiple market cycles. He was Reggie's boss earlier in Reggie's career and taught him many of the fundamentals he uses today.

**Credentials**: CFA, FRI, B.Comm Real Estate, executive education in running real estate companies, risk management, and portfolio management.

### When to Use Dennis vs. Reggie

**Ask Reggie for:**
- Financial analysis and NPV calculations
- Lease abstraction and compliance
- Credit scoring and IFRS 16 accounting
- Technical deal evaluation

**Ask Dennis for:**
- Strategic career decisions
- Negotiation psychology and power dynamics
- People management and team building
- Work-life balance reality checks
- When you need a reality check or tough love

### How to Work with Dennis

Simply address **"Dennis"** in your messages. He uses the **Opus model** for deep strategic thinking.

### Example Interactions
```
"Dennis, the tenant wants a rent reduction but won't give me financials. What do I do?"

"Dennis, I'm working 70 hours a week and my wife is threatening to leave. What do I do?"

"Dennis, should I fire this analyst who keeps asking me basic questions?"
```

Dennis is direct, blunt, and doesn't waste words. He'll challenge your assumptions, share battle scars from 30 years in the business, and make you think through your decisions. He cares deeply about people—that's why he's hard on them.

**Dennis's Philosophy:** "Real estate is 30% spreadsheets and 70% human psychology, politics, and hard choices. The fundamentals always give you the right answer. Think things through. Make decisions as if it were your own money. And remember: Father Time is undefeated."

## File Naming: Reports Folder

**CRITICAL**: All files in `Reports/` MUST use timestamp prefix:

**Format**: `YYYY-MM-DD_HHMMSS_[filename].md` (Eastern Time)

**Example**: `2025-10-31_143022_lease_abstract_acme_corp.md`

## Slash Commands (25 total)

All commands follow **PDF → JSON → Python → Report** automated workflow (except utilities).

### Abstraction (2)
- `/abstract-lease` - Extract lease terms using 24-section template
- `/critical-dates` - Extract timeline and critical dates

### Financial Analysis (10)
- `/effective-rent` - NER, NPV, breakeven (Ponzi Rental Rate)
- `/renewal-economics` - Renewal vs. relocation NPV analysis
- `/tenant-credit` - Credit scoring and risk assessment
- `/option-value` - Real options valuation (Black-Scholes)
- `/market-comparison` - Market rent benchmarking
- `/rollover-analysis` - Portfolio lease expiry analysis
- `/rental-variance` - Rental variance decomposition by rate, area, and term
- `/relative-valuation` - MCDA competitive positioning with 25 variables, personas, and filters
- `/recommendation-memo` - VTS approval memo with tenant analysis and deal comparison
- `/extract-mls` - Extract MLS data to professionally formatted Excel with subject highlighting

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

### Utilities (1)
- `/convert-to-pdf` - Convert markdown files to PDF format

**See**: `.claude/commands/README.md` for detailed documentation

## Specialized Skills (15 total)

Skills are **automatically invoked** through progressive disclosure - when your request matches a skill's description, Claude automatically loads the expertise. No manual invocation required.

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

### Negotiation & Objection Handling
- **negotiation-expert** - Evidence-based persuasion, calibrated questions, accusation audits
- **objection-handling-expert** - Objection analysis, response strategies, value-creating solutions

## Quick Start Examples

```bash
# Ask Reggie for expert leasing advice
# Just address "Reggie" in your message:
"Reggie, evaluate this renewal offer at $25/sf with 3 months free rent"
"Reggie, what security should I require for this tech startup tenant?"
"Reggie, help me respond to their objection about rent being too high"

# Lease abstraction
/abstract-lease path/to/lease.docx

# Financial analysis
/effective-rent path/to/lease.pdf
/tenant-credit path/to/financials.pdf
/rental-variance path/to/variance_data.xlsx
/option-value path/to/lease.pdf

# MLS extraction to Excel
/extract-mls path/to/mls_report.pdf --subject="2550 Stanfield"

# IFRS 16 accounting
/ifrs16-calculation path/to/lease.pdf 5.5

# Renewal economics
/renewal-economics path/to/current-lease.pdf

# Real options valuation (direct calculator usage)
python Option_Valuation/option_valuation.py \
  Option_Valuation/option_inputs/example_industrial_warehouse.json \
  --output results.json \
  --verbose

# Skills activate automatically based on your questions
# Example: "How do I negotiate rent with a difficult tenant?"
# → negotiation-expert skill loads automatically
# Example: "Review this assignment consent agreement"
# → consent-to-assignment-expert skill loads automatically

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
