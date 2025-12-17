# Linear Infrastructure & Property Acquisition Toolkit

## User Guide

**Version 2.1.0** | December 2025

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Meet the Infrastructure Team](#2-meet-the-infrastructure-team)
3. [When to Use Each Agent](#3-when-to-use-each-agent)
4. [Infrastructure Agent Deep Dives](#4-infrastructure-agent-deep-dives)
5. [Agent Collaboration Patterns](#5-agent-collaboration-patterns)
6. [Slash Commands Reference](#6-slash-commands-reference)
7. [Calculator Documentation](#7-calculator-documentation)
8. [Workflow Examples](#8-workflow-examples)
9. [Best Practices](#9-best-practices)
10. [Quick Reference](#10-quick-reference)

---

## 1. Introduction

### What is the Linear Infrastructure Toolkit?

The Linear Infrastructure Toolkit is a specialized extension of the commercial real estate platform designed for **property acquisition professionals** working on:

- **Transit corridors** (subway, LRT, commuter rail stations)
- **Utility transmission** (hydro lines, pipelines, transformer stations)
- **Highway expansion** (partial takings, access modifications)
- **Agricultural easements** (permanent rights-of-way through farmland)

### How It Differs from Commercial Leasing

| Aspect | Commercial Leasing (Reggie's Team) | Infrastructure Acquisition (New Team) |
|--------|-----------------------------------|---------------------------------------|
| **Primary Activity** | Lease negotiation & asset management | Property/easement acquisition |
| **Legal Framework** | Commercial Tenancies Act | Ontario Expropriations Act |
| **Typical Transaction** | 5-10 year lease term | Permanent acquisition or easement |
| **Counterparty** | Commercial tenants | Landowners, farmers, homeowners |
| **Volume** | Individual properties | Multi-parcel corridors (10-100+) |
| **Timeline Driver** | Market conditions | Statutory deadlines |
| **Fallback Option** | Find another tenant | Expropriation (compulsory acquisition) |

### Two Distinct Teams

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXISTING: Commercial Leasing                  │
│                      "The Triumvirate"                          │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐                     │
│  │ Reggie  │    │  Adam   │    │ Dennis  │                     │
│  │   VP    │    │ Analyst │    │ Advisor │                     │
│  └─────────┘    └─────────┘    └─────────┘                     │
│  Complex deals   Routine work   Strategic wisdom               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  NEW: Infrastructure Acquisition                 │
│                   "The Infrastructure Quintet"                  │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │  Alexi  │ │ Christi │ │  Katy   │ │  Shadi  │ │  Stevi  │  │
│  │Valuation│ │  Legal  │ │ Transit │ │ Utility │ │Compliance│  │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘  │
│                                                                 │
│  ┌─────────┐ ┌─────────┐                                       │
│  │  Benji  │ │  Anni   │  Legal Specialists                    │
│  │   CTA   │ │   RTA   │                                       │
│  └─────────┘ └─────────┘                                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Meet the Infrastructure Team

### The Infrastructure Quintet

These five agents handle all aspects of linear infrastructure and property acquisition:

#### Alexi - Expropriation Appraisal & Valuation Expert

| Attribute | Details |
|-----------|---------|
| **Designation** | AACI (Accredited Appraiser Canadian Institute) |
| **Model** | Sonnet |
| **Expertise** | Before/after valuation, easement valuation, comparable sales, severance damages, injurious affection |
| **Standards** | CUSPAP-compliant reporting |

**Core Question**: *"What is this property/easement worth?"*

**Signature**: *— Alexi | Expropriation Appraisal Expert, AACI*

---

#### Christi - Expropriation Law Specialist

| Attribute | Details |
|-----------|---------|
| **Specialization** | Ontario Expropriations Act, compensation law, procedural requirements |
| **Model** | Opus (deep legal analysis) |
| **Expertise** | Legal entitlement, settlement strategy, hearing preparation, procedural challenges |
| **Focus** | Legal framework, not valuation calculations |

**Core Question**: *"Is the owner legally entitled to this compensation?"*

**Signature**: *— Christi | Expropriation Law Specialist*

---

#### Katy - Transit Corridor Specialist

| Attribute | Details |
|-----------|---------|
| **Specialization** | Transit station acquisitions, public consultation, stakeholder management |
| **Model** | Sonnet |
| **Expertise** | Expropriation process execution, community relations, political navigation |
| **Focus** | Operational execution, not legal advice |

**Core Question**: *"How do we execute this transit station acquisition?"*

**Signature**: *— Katy | Transit Corridor Specialist*

---

#### Shadi - Utility Transmission Corridor Specialist

| Attribute | Details |
|-----------|---------|
| **Specialization** | Hydro/utility corridors, farmer negotiations, multi-parcel logistics |
| **Model** | Sonnet |
| **Expertise** | Permanent easement negotiations, agricultural land, 50-100+ parcel management |
| **Focus** | Farmer relations and corridor logistics |

**Core Question**: *"How do we negotiate this transmission line corridor through farmland?"*

**Signature**: *— Shadi | Utility Corridor Specialist*

---

#### Stevi - Compliance Enforcer & Deadline Watchdog

| Attribute | Details |
|-----------|---------|
| **Specialization** | Statutory deadlines, procedural compliance, Forms 1-12 verification |
| **Model** | Haiku (fast compliance checks) |
| **Expertise** | 3-month registration, Form 2/7 service, deadline tracking, audit trails |
| **Personality** | Zero tolerance for missed deadlines |

**Core Question**: *"Are we compliant? What deadlines are we facing?"*

**Signature**: *— Stevi | Compliance Enforcer*

---

### The Legal Specialists

Two additional agents for tenancy law questions:

#### Benji - Ontario Commercial Tenancies Act Specialist

| Attribute | Details |
|-----------|---------|
| **Specialization** | Commercial Tenancies Act, landlord/tenant disputes, lease enforcement |
| **Model** | Opus |
| **Expertise** | Assignment/subletting, distress for rent, relief from forfeiture |

**Use When**: Commercial lease disputes, CTA interpretation, landlord remedies

**Signature**: *— Benji | Commercial Tenancies Act Specialist*

---

#### Anni - Ontario Residential Tenancies Act Specialist

| Attribute | Details |
|-----------|---------|
| **Specialization** | Residential Tenancies Act, LTB procedures, eviction law |
| **Model** | Opus |
| **Expertise** | Tenant rights, eviction procedures, rent control |

**Use When**: Residential tenancy questions, LTB applications, RTA interpretation

**Signature**: *— Anni | Residential Tenancies Act Specialist*

---

## 3. When to Use Each Agent

### Decision Tree

```
What type of question do you have?
│
├─► VALUATION: "What's it worth?"
│   └─► ALEXI (easement value, severance damages, comparable sales)
│
├─► LEGAL: "What are we entitled to?"
│   ├─► Expropriation law → CHRISTI
│   ├─► Commercial tenancy → BENJI
│   └─► Residential tenancy → ANNI
│
├─► OPERATIONS: "How do we execute?"
│   ├─► Transit station acquisition → KATY
│   └─► Utility corridor/farmland → SHADI
│
└─► COMPLIANCE: "Are we on track?"
    └─► STEVI (deadlines, forms, procedural compliance)
```

### Agent Selection by Question Type

| If Your Question Is About... | Ask... | Example Query |
|------------------------------|--------|---------------|
| Easement or property value | **Alexi** | "What's this transmission line easement worth?" |
| Severance damages | **Alexi** | "Calculate severance damages for this partial taking" |
| Comparable sales analysis | **Alexi** | "Run a comparable sales analysis for 123 Main St" |
| Legal entitlement to compensation | **Christi** | "Is injurious affection compensable in this case?" |
| Procedural validity | **Christi** | "Is this Form 2 service defective?" |
| Settlement vs. hearing strategy | **Christi** | "Should we settle or proceed to hearing?" |
| Transit station acquisition process | **Katy** | "Plan the acquisition for the new LRT station" |
| Public consultation design | **Katy** | "Design a community consultation for this project" |
| Farmer/agricultural negotiations | **Shadi** | "How do I approach this farmer about an easement?" |
| Multi-parcel corridor logistics | **Shadi** | "Manage 75 acquisitions along this transmission line" |
| Statutory deadlines | **Stevi** | "What deadlines am I facing on this file?" |
| Form completeness | **Stevi** | "Is this Form 7 complete?" |
| Commercial lease dispute | **Benji** | "Can the landlord distrain for unpaid rent?" |
| Residential eviction | **Anni** | "What's the process for an N4 application?" |

### Common Handoffs

| Starting Agent | Hands Off To | When |
|----------------|--------------|------|
| Shadi | Alexi | Needs easement or compensation valuation |
| Katy | Alexi | Needs property appraisal for settlement offer |
| Katy | Christi | Needs legal review of settlement terms |
| Shadi | Christi | Needs easement agreement drafted |
| Any agent | Stevi | Needs deadline tracking or compliance check |
| Alexi | Christi | Valuation complete, need legal entitlement analysis |

---

## 4. Infrastructure Agent Deep Dives

### Alexi - Expropriation Appraisal & Valuation Expert

#### Valuation Methodologies

**1. Before/After Method** (Primary for partial takings)
```
Market value BEFORE taking:  $2,500,000
Market value AFTER taking:   $1,850,000
                             ──────────
Total compensation:          $650,000

Breakdown:
├── Land taken (fee simple):  $200,000
└── Severance damages:        $450,000
```

**2. Easement Valuation** (Three approaches)

| Method | Best For | Typical Range |
|--------|----------|---------------|
| Percentage of Fee | Utility easements | 5-35% of fee value |
| Income Capitalization | Agricultural land | Based on lost income |
| Before/After | Complex impacts | Full impact measurement |

**3. Comparable Sales Analysis**
- 49 adjustment factors across 8 categories
- Transactional, market conditions, location, land, building, site, condition/age
- MCDA ordinal ranking available for complex comparisons

#### Integrated Commands

| Command | Purpose |
|---------|---------|
| `/easement-valuation` | Calculate easement value using multiple methods |
| `/comparable-sales-analysis` | Traditional DCA with adjustment grid |
| `/mcda-sales-comparison` | MCDA ordinal ranking for fee simple |
| `/partial-taking-analysis` | Before/after with severance damages |

#### Example Queries

```
"Alexi, value this permanent transmission line easement (60m wide, 15 acres)"

"Alexi, calculate severance damages for the remainder parcel after the highway widening"

"Alexi, run a comparable sales analysis for the subject property at 456 Industrial Road"

"Alexi, what's the percentage of fee for a telecom tower easement on agricultural land?"
```

---

### Christi - Expropriation Law Specialist

#### Legal Framework Expertise

**Ontario Expropriations Act Sections:**
- **s.13** - Market value determination
- **s.14** - Special value to owner
- **s.18(1)** - Disturbance damages
- **s.18(2)** - Injurious affection
- **s.19** - Business losses
- **s.20** - Interest on compensation
- **s.25-32** - Hearing procedures

#### Compensation Entitlement Analysis

| Compensation Type | Legal Test | Christi's Role |
|-------------------|------------|----------------|
| Market Value | Fair market value at valuation date | Confirms HBU, special purchaser exclusion |
| Disturbance Damages | Reasonable costs arising from taking | Analyzes what's legally recoverable |
| Injurious Affection | Antrim four-part test | Applies legal framework |
| Business Losses | Direct & proximate cause | Assesses compensability |

#### Integrated Commands

| Command | Purpose |
|---------|---------|
| `/expropriation-compensation` | Full statutory compensation calculation |
| `/injurious-affection-analysis` | Quantify construction/proximity damages |
| `/partial-taking-analysis` | Before/after with legal framework |
| `/settlement-analysis` | Settlement vs. hearing decision |

#### Example Queries

```
"Christi, is this procedural defect fatal to the expropriation?"

"Christi, analyze whether these business losses are compensable under s.19"

"Christi, should we settle at $750,000 or proceed to hearing?"

"Christi, draft the legal framework section for Alexi's appraisal report"
```

---

### Katy - Transit Corridor Specialist

#### Operational Expertise

**Expropriation Process Execution:**
1. Approval memo preparation (executive/board review)
2. Form 1 (Notice of Application for Approval)
3. Inquiry Officer hearing coordination
4. Form 2 service (Notice of Expropriation)
5. Form 7 (Notice of Approval) distribution
6. Settlement negotiation or hearing preparation

**Public Consultation Design:**
- Open houses and town halls
- Small group stakeholder meetings
- Political briefings (councillors, ministers)
- Media management and crisis communications

**Stakeholder Categories:**
| Stakeholder | Katy's Approach |
|-------------|-----------------|
| Affected property owners | Empathetic, settlement-focused |
| Community groups | Transparent, accommodation-oriented |
| Politicians | Proactive briefings, early engagement |
| Media | Prepared messaging, crisis protocols |
| Indigenous communities | Respectful consultation, duty compliance |

#### Integrated Commands

| Command | Purpose |
|---------|---------|
| `/transit-station-scoring` | TOD site alternative evaluation |
| `/public-consultation-summary` | Summarize stakeholder feedback |
| `/briefing-note` | Executive briefing preparation |
| `/board-memo` | Board approval documentation |
| `/negotiation-strategy` | Settlement approach planning |

#### Example Queries

```
"Katy, plan the acquisition process for the new subway station at Queen & University"

"Katy, design a public consultation program for this LRT extension"

"Katy, draft an approval memo for the settlement at $1.2M"

"Katy, how do I handle organized NIMBY opposition at next week's town hall?"
```

---

### Shadi - Utility Transmission Corridor Specialist

#### Operational Expertise

**Transmission Line Easements:**
| Voltage | Typical Corridor Width | Impact Level |
|---------|------------------------|--------------|
| 115kV | 20-30m | Moderate |
| 230kV | 35-50m | Significant |
| 500kV | 60-80m | Substantial |

**Agricultural Negotiation Psychology:**
- Understand crop cycles and seasonal timing
- Respect multi-generational farm operations
- Address equipment navigation concerns
- Negotiate crop loss compensation fairly
- Build trust through agricultural knowledge

**Multi-Parcel Corridor Management:**
- 50-100+ parcels per transmission line project
- Phased acquisition strategy
- Critical path identification (holdout risk)
- Parallel negotiation streams

#### Integrated Commands

| Command | Purpose |
|---------|---------|
| `/cropland-compensation-analysis` | Agricultural easement compensation |
| `/right-of-way-analysis` | ROW area and encumbrance calculation |
| `/easement-valuation` | Value utility easements |
| `/negotiation-strategy` | Owner-specific approach |

#### Example Queries

```
"Shadi, how do I approach the 75 farmers along this 500kV transmission corridor?"

"Shadi, negotiate the easement with the Smith family farm - they've owned it for 4 generations"

"Shadi, calculate annual cropland compensation under the Ontario model"

"Shadi, develop a phased acquisition strategy for the 50-parcel corridor"
```

---

### Stevi - Compliance Enforcer & Deadline Watchdog

#### Deadline Tracking System

**Critical Statutory Deadlines:**

| Deadline | Trigger Event | Consequence of Miss |
|----------|---------------|---------------------|
| 3-month registration | Expropriation approval | Approval expires, must restart |
| Form 2 service | Registration | Owner not bound to elect |
| 30-day appeal | Tribunal decision | Appeal rights lost |
| 90-day appraisal exchange | Before hearing | Evidence excluded |

**Forms 1-12 Verification Checklist:**
- [ ] All mandatory fields completed
- [ ] Proper signatures and authorization
- [ ] Correct service method
- [ ] Proof of service attached
- [ ] Supporting documentation included
- [ ] Legal description accurate
- [ ] Registered owner correctly identified

#### Escalation Protocol

| Days Remaining | Stevi's Action |
|----------------|----------------|
| 30+ days | Standard tracking, weekly reminder |
| 14-30 days | Daily monitoring, supervisor notification |
| 7-14 days | Urgent alerts, executive escalation |
| < 7 days | Emergency mode, all hands on deck |
| MISSED | Incident report, recovery assessment |

#### Example Queries

```
"Stevi, what deadlines am I facing on the Highway 401 file?"

"Stevi, is this Form 2 properly served?"

"Stevi, verify the Forms 1-12 are complete for the tribunal filing"

"Stevi, create a deadline tracker for our 25 active acquisitions"
```

---

## 5. Agent Collaboration Patterns

### Pattern 1: Transit Station Acquisition

```
┌─────────────────────────────────────────────────────────────┐
│                    TRANSIT STATION WORKFLOW                  │
└─────────────────────────────────────────────────────────────┘

  KATY                 ALEXI              CHRISTI            STEVI
    │                    │                   │                 │
    ├──► Site selection  │                   │                 │
    │    Public consult  │                   │                 │
    │                    │                   │                 │
    ├─────────────────►  │                   │                 │
    │   "Need valuation" │                   │                 │
    │                    ├──► Appraisal      │                 │
    │                    │    Before/after   │                 │
    │                    │                   │                 │
    │                    ├───────────────►   │                 │
    │                    │  "Legal review"   │                 │
    │                    │                   ├──► Entitlement  │
    │                    │                   │    analysis     │
    │                    │                   │                 │
    │                    │                   ├─────────────►   │
    │                    │                   │  "Compliance"   │
    │                    │                   │                 ├──► Deadline
    │◄──────────────────┼───────────────────┼─────────────────┤    tracking
    │   Ready to settle  │                   │                 │
    │                    │                   │                 │
    ├──► Negotiate       │                   │                 │
    │    settlement      │                   ├──► Draft        │
    │                    │                   │    agreement    │
    │                    │                   │                 │
    ├──► Execute         │                   │                 │
         & close         │                   │                 │
```

### Pattern 2: Transmission Line Corridor

```
┌─────────────────────────────────────────────────────────────┐
│              TRANSMISSION LINE CORRIDOR WORKFLOW             │
└─────────────────────────────────────────────────────────────┘

  SHADI                ALEXI              CHRISTI            STEVI
    │                    │                   │                 │
    ├──► Corridor        │                   │                 │
    │    strategy        │                   │                 │
    │    (50+ parcels)   │                   │                 │
    │                    │                   │                 │
    │  For each parcel:  │                   │                 │
    ├─────────────────►  │                   │                 │
    │   "Value easement" │                   │                 │
    │                    ├──► Easement       │                 │
    │                    │    valuation      │                 │
    │                    │    (% of fee)     │                 │
    │                    │                   │                 │
    │◄──────────────────┤                   │                 │
    │   Value provided   │                   │                 │
    │                    │                   │                 │
    ├──► Negotiate       │                   │                 │
    │    with farmer     │                   │                 │
    │                    │                   │                 │
    │  If settlement:    │                   │                 │
    ├───────────────────────────────────►   │                 │
    │   "Draft easement agreement"          │                 │
    │                    │                   ├──► Legal        │
    │                    │                   │    drafting     │
    │                    │                   │                 │
    │  Throughout:       │                   │                 │
    ├───────────────────────────────────────────────────────► │
    │   "Track deadlines for all 50 parcels"                  │
    │                    │                   │                 ├──► Portfolio
    │                    │                   │                 │    tracking
```

### Pattern 3: Valuation + Legal Entitlement

```
┌─────────────────────────────────────────────────────────────┐
│              VALUATION + LEGAL ENTITLEMENT                   │
└─────────────────────────────────────────────────────────────┘

  USER                 ALEXI              CHRISTI
    │                    │                   │
    ├──► "What am I      │                   │
    │    entitled to?"   │                   │
    │                    │                   │
    │  VALUE question:   │                   │
    ├─────────────────►  │                   │
    │                    ├──► Calculates:    │
    │                    │    - Market value │
    │                    │    - Severance    │
    │                    │    - Injurious    │
    │                    │                   │
    │  ENTITLEMENT question:                 │
    ├───────────────────────────────────►   │
    │                    │                   ├──► Analyzes:
    │                    │                   │    - Legal basis
    │                    │                   │    - Case law
    │                    │                   │    - Risk
    │                    │                   │
    │◄──────────────────┼───────────────────┤
    │   Complete answer: │                   │
    │   VALUE + LEGAL    │                   │
```

---

## 6. Slash Commands Reference

### Expropriation Commands

| Command | Purpose | Primary Agent |
|---------|---------|---------------|
| `/expropriation-compensation` | Full statutory compensation (s.13, s.18, s.20) | Christi |
| `/injurious-affection-analysis` | Construction/proximity damages | Alexi + Christi |
| `/partial-taking-analysis` | Before/after with severance | Alexi |

### Infrastructure Commands

| Command | Purpose | Primary Agent |
|---------|---------|---------------|
| `/cropland-compensation-analysis` | Agricultural easement compensation | Shadi |
| `/right-of-way-analysis` | ROW area and encumbrance calculation | Shadi |

### Process Commands

| Command | Purpose | Primary Agent |
|---------|---------|---------------|
| `/board-memo` | Board approval documentation | Katy |
| `/briefing-note` | Executive briefing preparation | Katy |
| `/settlement-analysis` | Settlement vs. hearing decision | Christi |
| `/expropriation-timeline` | PERT/CPM project timeline | Katy + Stevi |
| `/public-consultation-summary` | Summarize stakeholder feedback | Katy |
| `/negotiation-strategy` | Owner-specific approach | Shadi/Katy |

### Specialized Commands

| Command | Purpose | Primary Agent |
|---------|---------|---------------|
| `/cost-approach-infrastructure` | Replacement cost for specialized assets | Alexi |
| `/environmental-due-diligence` | Phase I/II ESA summary | Environmental skill |
| `/income-approach-land` | Land rent capitalization | Alexi |
| `/title-analysis` | Encumbrances, easements, restrictions | Title skill |
| `/utility-conflict-analysis` | Utility relocation requirements | Shadi |

### Transit Commands

| Command | Purpose | Primary Agent |
|---------|---------|---------------|
| `/transit-station-scoring` | TOD site alternative evaluation | Katy |

### Valuation Commands

| Command | Purpose | Primary Agent |
|---------|---------|---------------|
| `/easement-valuation` | Calculate easement value (3 methods) | Alexi |
| `/comparable-sales-analysis` | Traditional DCA with 49 adjustments | Alexi |
| `/mcda-sales-comparison` | MCDA ordinal ranking | Alexi |

---

## 7. Calculator Documentation

### Comparable Sales Analysis Calculator

**Location**: `Comparable_Sales_Analysis/`

**Purpose**: Traditional Direct Comparison Approach (DCA) with quantified dollar adjustments

**49 Adjustment Factors in 8 Categories:**

| Category | Adjustments |
|----------|-------------|
| Transactional | Property rights, financing, conditions of sale |
| Market Conditions | Time/appreciation (monthly compounding) |
| Location | Submarket, highway access, accessibility |
| Land | Lot size, shape, topography, utilities, drainage, flood, environmental, soil |
| Industrial Building | Clear height, loading docks, drive-in doors, rail spur, power, office ratio, HVAC, sprinklers |
| Office Building | Class, floor plate, ceiling height, elevators, HVAC, parking ratio, amenities, lobby |
| Site | Paving, fencing, lighting, landscaping, stormwater, yard area |
| Condition/Age | Effective age, condition rating |

**Usage**:
```bash
/comparable-sales-analysis <subject-property.json> [comp1.json] [comp2.json] ...
```

### MCDA Sales Comparison Calculator

**Location**: `MCDA_Sales_Comparison/`

**Purpose**: Multi-Criteria Decision Analysis for ordinal ranking when dollar adjustments are uncertain

**14 Weighted Characteristics**:
- Location quality, size, age, condition, access, visibility
- Building quality, site improvements, utilities, zoning conformity
- Environmental status, market conditions, financing, motivation

**5 Weight Profiles**:
- Industrial-Standard, Office-Standard, Retail-Standard
- Location-Dominant, Physical-Dominant

**Usage**:
```bash
/mcda-sales-comparison <input.json> --profile industrial-standard
```

### Shared Schema

**Location**: `Shared_Utils/schemas/comparable_sales_input_schema.json`

Both calculators use the same JSON Schema (Draft 2020-12) for input validation, ensuring consistency across valuation approaches.

---

## 8. Workflow Examples

### Example 1: Transit Station Expropriation

**Scenario**: New LRT station requires acquisition of 3 commercial properties

**Workflow**:
1. **Katy**: Design public consultation, prepare approval memo
2. **Alexi**: Appraise all 3 properties using before/after method
3. **Christi**: Review legal entitlement, draft settlement terms
4. **Stevi**: Track 3-month registration deadline
5. **Katy**: Negotiate settlements, execute closings

```
User: "Katy, we need to acquire 123, 125, and 127 Main Street for the new LRT station"

Katy: [Plans acquisition timeline, identifies stakeholders, designs consultation]

User: "Alexi, value all three properties"

Alexi: [Provides before/after valuations with severance analysis]

User: "Christi, review the settlement terms for 123 Main"

Christi: [Analyzes legal entitlement, recommends settlement structure]

User: "Stevi, what deadlines are we facing?"

Stevi: [Creates deadline tracker for all three properties]
```

### Example 2: 500kV Transmission Line Corridor

**Scenario**: 75 agricultural parcels along 50km transmission corridor

**Workflow**:
1. **Shadi**: Develop phased acquisition strategy, prioritize critical parcels
2. **Alexi**: Value easements using percentage of fee method
3. **Shadi**: Negotiate with each farmer (seasonal timing awareness)
4. **Christi**: Draft easement agreements for settlements
5. **Stevi**: Track all 75 parcels, flag deadline risks

```
User: "Shadi, plan the acquisition strategy for the Bruce-Milton transmission line"

Shadi: [Develops corridor strategy, identifies holdout risks, phases negotiations]

User: "Alexi, value the easement for Parcel 23 (150-acre farm)"

Alexi: [Calculates easement value at 15% of fee plus crop compensation]

User: "Shadi, the farmer at Parcel 23 is resistant - he's farmed this land for 40 years"

Shadi: [Provides negotiation approach considering generational attachment]

User: "Stevi, give me a status report on all 75 parcels"

Stevi: [Portfolio status: 45 settled, 20 in negotiation, 10 at risk of expropriation]
```

### Example 3: Partial Taking with Severance Damages

**Scenario**: Highway widening takes 20% of industrial property

**Workflow**:
1. **Alexi**: Before/after valuation, quantify severance damages
2. **Christi**: Analyze legal entitlement to severance
3. **Stevi**: Verify procedural compliance

```
User: "Alexi, the highway widening takes 2 acres from a 10-acre industrial site"

Alexi:
- Before value: $5,000,000
- After value: $3,200,000
- Total compensation: $1,800,000
  - Land taken: $1,000,000
  - Severance damages: $800,000 (access impairment, reduced truck circulation)

User: "Christi, is the severance damage legally supportable?"

Christi: [Confirms severance is compensable under s.18(1), cites supporting case law]
```

### Example 4: Agricultural Easement with OFA Guidance

**Scenario**: Pipeline easement through cash crop farm

**Workflow**:
1. **Shadi**: Negotiate easement terms with farmer
2. **Alexi**: Value using income capitalization (lost crop revenue)
3. **Use cropland compensation skill** for OFA-aligned compensation structure

```
User: "Shadi, negotiate a 30m pipeline easement through a 500-acre corn/soybean operation"

Shadi: [Approaches farmer with seasonal awareness, addresses equipment concerns]

User: "/cropland-compensation-analysis"

[Calculates one-time vs. annual compensation, compares Ontario and Alberta models]
```

### Example 5: Settlement vs. Hearing Decision

**Scenario**: Owner demands $2M, our appraisal says $1.2M

**Workflow**:
1. **Alexi**: Confirm valuation methodology and supportability
2. **Christi**: Analyze hearing risk, probability-weighted outcomes
3. **Katy/Shadi**: Execute negotiation strategy

```
User: "Christi, should we settle at $1.5M or proceed to hearing?"

Christi: [Analyzes:
- Probability of winning at hearing: 70%
- Expected hearing cost: $150,000
- Time delay: 18 months
- Probability-weighted outcome: $1.38M
- Recommendation: Settle at $1.4M to avoid hearing risk]
```

---

## 9. Best Practices

### Statutory Compliance

**Critical Deadlines (Never Miss These)**:
| Deadline | Consequence | Stevi's Alert Level |
|----------|-------------|---------------------|
| 3-month registration | Approval expires | CRITICAL |
| Form 2 service timing | Procedural defect | HIGH |
| 30-day appeal window | Rights forfeited | CRITICAL |
| 90-day appraisal exchange | Evidence excluded | HIGH |

**Forms Verification**:
- Always have Stevi verify Forms 1-12 before submission
- Double-check legal descriptions against title
- Confirm registered owner identification
- Attach proof of service

### Valuation Methodology Selection

| Situation | Recommended Method | Agent |
|-----------|-------------------|-------|
| Partial taking | Before/after | Alexi |
| Utility easement (simple) | Percentage of fee | Alexi |
| Agricultural easement | Income capitalization + % of fee | Alexi |
| Fee simple with good comps | Comparable sales (DCA) | Alexi |
| Fee simple with uncertain adjustments | MCDA ordinal ranking | Alexi |
| Specialized infrastructure | Cost approach | Alexi |

### Negotiation Strategies by Owner Type

| Owner Type | Approach | Lead Agent |
|------------|----------|------------|
| Farmer (multi-generational) | Respect legacy, seasonal timing | Shadi |
| Commercial property owner | Financial focus, business impact | Katy |
| Residential homeowner | Empathy, relocation assistance | Katy |
| Developer | Opportunity cost, future value | Katy/Shadi |
| Institutional investor | Professional, efficient process | Katy |

### CUSPAP Disclosure Requirements

When using industry defaults instead of market-derived factors:
- Document the source of the default
- Disclose in the appraisal report
- Explain why market evidence was unavailable
- Consider sensitivity analysis

---

## 10. Quick Reference

### Agent Selection Cheat Sheet

| I need to... | Ask... |
|--------------|--------|
| Value an easement | Alexi |
| Calculate severance damages | Alexi |
| Run comparable sales | Alexi |
| Check legal entitlement | Christi |
| Draft settlement agreement | Christi |
| Assess hearing risk | Christi |
| Plan transit acquisition | Katy |
| Run public consultation | Katy |
| Negotiate with farmers | Shadi |
| Manage corridor (50+ parcels) | Shadi |
| Track deadlines | Stevi |
| Verify form completeness | Stevi |
| Commercial tenancy question | Benji |
| Residential tenancy question | Anni |

### Command Quick Reference

```bash
# Valuation
/easement-valuation <input.json>
/comparable-sales-analysis <subject.json> [comps...]
/mcda-sales-comparison <input.json> --profile <profile>

# Expropriation
/expropriation-compensation <input.json>
/partial-taking-analysis <input.json>
/injurious-affection-analysis <input.json>

# Process
/briefing-note <input.json>
/board-memo <input.json>
/settlement-analysis <input.json>
/expropriation-timeline <milestones.json>

# Infrastructure
/cropland-compensation-analysis <input.json>
/right-of-way-analysis <corridor.json>
/transit-station-scoring <sites.json>
```

### Statutory Deadline Timeline

```
Day 0: Expropriation approval granted
  │
  ├── Day 90: Registration deadline (3 months)
  │     │
  │     └── CRITICAL: Approval expires if not registered
  │
  ├── Day 90: Form 2 service (within 3 months of registration)
  │
  ├── Day 180: Form 3 election (3 months from Form 2)
  │
  └── Hearing: Variable (typically 12-24 months from Form 3)
        │
        ├── Day -90: Appraisal exchange deadline
        │
        └── Day +30: Appeal deadline (from decision)
```

### Forms 1-12 Quick Guide

| Form | Purpose | Critical Elements |
|------|---------|-------------------|
| Form 1 | Notice of Application | Legal description, registered owner |
| Form 2 | Notice of Expropriation | Service proof, timing |
| Form 3 | Election of Compensation | Owner's response deadline |
| Form 4 | Notice of Application for Approval | Publication requirements |
| Form 5 | Application for Approval | Supporting materials |
| Form 6 | Approval of Expropriation | Authorization, conditions |
| Form 7 | Notice of Approval | Service on all owners |
| Forms 8-12 | Tribunal/court forms | Varies by proceeding |

---

## Appendix: Skills Reference

### Infrastructure Skills (24 total)

<details>
<summary>Click to expand full skills list</summary>

**Valuation & Appraisal**
- `easement-valuation-methods`
- `comparable-sales-adjustment-methodology`
- `cost-approach-expert`
- `income-approach-expert`
- `severance-damages-quantification`
- `injurious-affection-assessment`

**Legal & Compliance**
- `ontario-expropriations-act-statutory-interpretation`
- `expropriation-compensation-entitlement-analysis`
- `expropriation-procedural-defect-analysis`
- `expropriation-statutory-deadline-tracking`
- `forms-1-12-completeness-verification`

**Process & Operations**
- `expropriation-timeline-expert`
- `land-assembly-expert`
- `settlement-analysis-expert`
- `public-consultation-process-design`
- `stakeholder-management-expert`
- `nimby-objection-analysis-response`

**Corridor-Specific**
- `transit-station-site-acquisition-strategy`
- `transmission-line-technical-specifications`
- `right-of-way-expert`
- `agricultural-easement-negotiation-frameworks`
- `cropland-out-of-production-agreements`
- `negotiation-expert-infrastructure`

**Due Diligence**
- `environmental-due-diligence-expert`
- `title-expert`

</details>

---

*This guide is part of the Linear Infrastructure Toolkit v2.1.0. For commercial leasing documentation, see the main README.md and CLAUDE.md files.*
