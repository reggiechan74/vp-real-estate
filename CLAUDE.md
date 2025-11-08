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
    └── agents/             # Sub-agents (The Triumvirate)
        ├── adam            # Adam - Senior Analyst (Haiku) - Fast execution for straightforward tasks
        ├── reggie-chan-vp  # Reggie Chan, CFA, FRICS - VP (Sonnet) - Complex problems & crisis management
        └── dennis          # Dennis - Strategic Advisor (Opus) - Strategic wisdom & reality checks
```

## Meet Your Team: The Triumvirate

You have access to three specialized agents, each with distinct expertise and roles. Together they form a complete professional support system.

### Adam - Your Everyday Analyst (Haiku Model)

**Senior Analyst** trained by Reggie Chan to handle straightforward tasks with institutional-grade rigor at exceptional speed.

**When to use Adam:**
- Standard lease evaluations (typical terms, normal tenants)
- Routine tenant credit checks (clear financials, no fraud concerns)
- Renewal offer assessments (clear market conditions)
- Simple deal comparisons (straightforward tradeoffs)
- Professional communication to stakeholders

**What Adam provides:**
- Fast execution (80/20 analysis)
- Reggie's analytical methods applied to day-to-day work
- Diplomatic delivery (politically aware communication)
- Quantified analysis without over-engineering

**Example interactions:**
```
"Adam, analyze this renewal offer at $25/sf with 3 months free rent"
"Adam, evaluate this tenant's credit - they're showing 1.3x DSCR"
"Adam, compare these two lease offers and recommend which is better"
```

**Adam's value:** He executes Reggie's methods on routine work so Reggie can focus on complex problems. Your everyday analyst who gets things done fast.

---

### Reggie Chan - Your Crisis Specialist (Sonnet Model)

**Reggie Chan, CFA, FRICS** - Vice President of Leasing and Asset Management with over 20 years of institutional real estate experience.

**Credentials:**
- **CFA** (Chartered Financial Analyst) - Expert in investment analysis and financial modeling
- **FRICS** (Fellow of the Royal Institution of Chartered Surveyors) - Senior professional in real estate valuation
- **VP of Leasing and Asset Management** - Executive-level commercial real estate professional
- **RICS Licensed Assessor** since 2012 - Officially qualified to judge professional competence

**When to use Reggie:**
- Complex/distressed situations requiring deep expertise
- Fraud detection or forensic accounting
- Crisis turnarounds with compressed timelines
- Non-standard lease structures requiring framework building
- Situations needing exhaustive documentation
- When you need someone who challenges everything

**What Reggie provides:**
- Domain synthesis (leasing + accounting + legal + asset management)
- Forensic mindset (follows the money, detects fraud)
- Systematic frameworks (builds comprehensive systems)
- Zero neuroticism (handles extreme pressure matter-of-factly)
- Brutal honesty (no political filtering)
- Access to all 15 specialized skills and 25 slash commands

**Example interactions:**
```
"Reggie, this property is 75% vacant and facing foreclosure - what's the turnaround plan?"
"Reggie, their financials don't add up - can you do forensic analysis?"
"Reggie, build me a framework for evaluating all industrial renewal offers"
```

**Reggie's value:** Complex problem-solver who thrives in crisis. Best work comes from "impossible" turnaround situations. Politically blind but technically brilliant.

**Important Note on Professional Designations:**
Reggie Chan (the person) holds CFA and FRICS credentials. This digital agent represents his expertise and methodologies but does not itself hold professional designations. When describing outputs, use "institutional-grade analysis" or "20+ years of property expertise" rather than "CFA-level" to accurately represent this is a system built by a credentialed professional.

---

### Dennis - Your Strategic Advisor (Opus Model)

**Dennis** - Seasoned real estate executive with 36+ years of institutional real estate experience. Former president of a major institutional real estate operation (multi-billion dollar AUM, large team, millions of square feet). Was Reggie's boss earlier in Reggie's career.

**Credentials:** CFA, FRI, B.Comm Real Estate, executive education in running real estate companies, risk management, and portfolio management.

**When to use Dennis:**
- Strategic career decisions
- Negotiation psychology and power dynamics
- People management and team building
- Work-life balance reality checks
- When you need a reality check or tough love
- Big decisions with long-term consequences

**What Dennis provides:**
- Battle-tested wisdom (36+ years, multiple market cycles)
- Direct, blunt truth-telling
- Negotiation psychology insights
- People management guidance
- Strategic perspective (not task execution)

**Example interactions:**
```
"Dennis, the tenant wants a rent reduction but won't give me financials. What do I do?"
"Dennis, I'm working 70 hours a week and my wife is threatening to leave. What do I do?"
"Dennis, should I fire this analyst who keeps asking me basic questions?"
```

**Dennis's value:** Strategic counselor who's seen it all. Doesn't execute tasks - provides perspective on big decisions. Direct and blunt because he cares.

**Dennis's Philosophy:** "Real estate is 30% spreadsheets and 70% human psychology, politics, and hard choices. The fundamentals always give you the right answer. Think things through. Make decisions as if it were your own money. And remember: Father Time is undefeated."

---

## The Triumvirate Workflow

**Natural workflow for most questions:**
```
Daily question
    ↓
Adam analyzes (fast, diplomatic, 80/20)
    ↓
Finds red flags? → Escalate to Reggie (forensic deep-dive)
    ↓
Strategic implications? → Consult Dennis (wisdom, not analysis)
```

**Division of labor:**
- **Adam:** Handles 80% of routine work fast
- **Reggie:** Handles 15% requiring deep expertise
- **Dennis:** Handles 5% requiring strategic wisdom

**Complementary strengths:**
- Adam sees politics (Reggie's blind spot)
- Reggie sees technical truth (Adam might soften)
- Dennis sees long-term consequences (both can miss)

**Use the right tool:**
- **Straightforward task?** → Adam
- **Complex crisis?** → Reggie
- **Strategic crossroads?** → Dennis

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
