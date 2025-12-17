# Deep Research Report: AI-Enhanced Automation for Infrastructure & Expropriation Appraisal

**Prepared:** December 16, 2025
**Reference:** Alex Pitt Project Charter
**Purpose:** Technical Feasibility & Implementation Research

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Existing Repository Capabilities](#2-existing-repository-capabilities)
3. [R-Plan OCR Extraction Technologies](#3-r-plan-ocr-extraction-technologies)
4. [GeoWarehouse & TREB API Integration](#4-geowarehouse--treb-api-integration)
5. [AI Vision for Property Description](#5-ai-vision-for-property-description)
6. [Adjustment Quantification Methodologies](#6-adjustment-quantification-methodologies)
7. [Ontario Legal Framework Analysis](#7-ontario-legal-framework-analysis)
8. [Hydro One Transmission Corridor Specifics](#8-hydro-one-transmission-corridor-specifics)
9. [CUSPAP Compliance Considerations](#9-cuspap-compliance-considerations)
10. [Phase-by-Phase Implementation Analysis](#10-phase-by-phase-implementation-analysis)
11. [Risk Assessment](#11-risk-assessment)
12. [Recommended Technology Stack](#12-recommended-technology-stack)
13. [Next Steps & Action Items](#13-next-steps--action-items)

---

## 1. Executive Summary

This research validates the technical feasibility of the AI-Enhanced Automation Pipeline proposed in Alex Pitt's Project Charter. Key findings:

### Critical Discovery: Existing Infrastructure

**The repository already contains substantial expropriation and infrastructure capabilities that were not accounted for in the original SOW.** This represents a significant acceleration opportunity:

- **5 Specialized Infrastructure Agents** (Alexi, Christi, Katy, Shadi, Stevi)
- **56 Expert Skills** including 28+ directly relevant to expropriation
- **44 Slash Commands** with expropriation-specific functionality
- **8 Specialized Calculators** (easement, cost approach, income approach, comparable sales)

### Feasibility Assessment

| Phase | SOW Component | Feasibility | Implementation Path |
|-------|--------------|-------------|---------------------|
| **Phase 1** | Area & Economic Overviews | ✅ **HIGH** | LLM with structured prompts |
| **Phase 1** | Visual Property Description | ✅ **HIGH** | Claude Vision / GPT-4V |
| **Phase 2** | R-Plan OCR Extraction | ⚠️ **MEDIUM** | Custom pipeline with Google Document AI |
| **Phase 2** | Pre-Flight Document Check | ✅ **HIGH** | Existing Stevi agent + folder validation |
| **Phase 2** | API Integration | ⚠️ **MEDIUM** | RETS protocol (not REST); requires realtor partnership |
| **Phase 3** | Dynamic Adjustment Chart | ✅ **HIGH** | Extend existing comparable-sales-adjustment-methodology skill |
| **Phase 3** | Easement Factor Logic | ✅ **ALREADY EXISTS** | v2.1 calculators operational |
| **Phase 4** | Formatting Guardrails | ✅ **HIGH** | LLM-based style enforcement |
| **Phase 4** | Memo Generator | ✅ **ALREADY EXISTS** | board-memo-expert, briefing-note-expert skills |

### ROI Revision

Given existing infrastructure, the implementation timeline and cost can be significantly reduced:

- **Phase 1 Pilot:** 1-2 weeks (vs. 1 month originally)
- **Phase 2 Build:** 2-3 weeks (vs. 1 month originally)
- **Phase 3 Integration:** 2 weeks (core functionality already exists)
- **Phase 4 Polish:** 1 week (templates exist)

**Total: 6-8 weeks vs. original 3-month estimate**

---

## 2. Existing Repository Capabilities

### 2.1 The Infrastructure Acquisition Team

The repository contains five specialized agents designed specifically for infrastructure and expropriation work:

#### Alexi - Expropriation Appraisal Expert, AACI (Sonnet Model)
**Location:** `.claude/agents/alexi`

| Capability | Direct Relevance to SOW |
|------------|------------------------|
| Before/after valuation methodology | Phase 3: Valuation Support |
| Comparable sales adjustment grids | Phase 3: Dynamic Adjustment Chart |
| Severance damages quantification | Phase 3: Easement Factor Logic |
| Injurious affection assessment | Corridor project-specific |
| CUSPAP-compliant report generation | Phase 4: Output & QC |

#### Christi - Expropriation Law Specialist (Opus Model)
**Location:** `.claude/agents/christi`

| Capability | Direct Relevance to SOW |
|------------|------------------------|
| Ontario Expropriations Act mastery (ss.1-49) | All phases |
| Compensation framework (s.13, s.18, s.18(2)) | Phase 3: Valuation Support |
| Forms 1-12 compliance | Phase 2: Pre-Flight Check |
| Settlement strategy | Corridor project negotiations |

#### Katy - Transit Corridor Specialist (Sonnet Model)
**Location:** `.claude/agents/katy`

| Capability | Direct Relevance to SOW |
|------------|------------------------|
| Expropriation process execution | Metrolinx project-specific |
| Approval memo drafting | Phase 4: Memo Generator |
| Multi-stakeholder coordination | Corridor project management |
| Forms 1-12 preparation | Phase 2: Pre-Flight Check |

#### Shadi - Utility Transmission Corridor Specialist (Sonnet Model)
**Location:** `.claude/agents/shadi`

| Capability | Direct Relevance to SOW |
|------------|------------------------|
| Permanent easement negotiations | Hydro One corridor projects |
| Agricultural land impact assessment | Farm property valuations |
| Multi-parcel corridor logistics (50-100+) | 100-property corridor projects |
| Technical specifications (voltage, clearances) | Phase 3: Easement Factor Logic |

#### Stevi - Compliance Enforcer & Deadline Watchdog (Haiku Model)
**Location:** `.claude/agents/stevi`

| Capability | Direct Relevance to SOW |
|------------|------------------------|
| Statutory deadline tracking | Phase 2: Pre-Flight Check |
| Procedural compliance verification | Phase 4: Quality Control |
| Forms 1-12 completeness verification | Phase 2: Pre-Flight Check |
| Zero-tolerance deadline enforcement | Corridor project timeline management |

### 2.2 Specialized Skills (56 Total, 28+ Relevant)

#### Expropriation-Specific Skills

| Skill | File Location | SOW Relevance |
|-------|---------------|---------------|
| `expropriation-compensation-entitlement-analysis` | `.claude/skills/` | Phase 3 |
| `expropriation-procedural-defect-analysis` | `.claude/skills/` | Phase 4 QC |
| `expropriation-statutory-deadline-tracking` | `.claude/skills/` | Phase 2 |
| `expropriation-timeline-expert` | `.claude/skills/` | Project management |
| `severance-damages-quantification` | `.claude/skills/` | Phase 3 |
| `injurious-affection-assessment` | `.claude/skills/` | Phase 3 |
| `forms-1-12-completeness-verification` | `.claude/skills/` | Phase 2 |

#### Valuation Methodology Skills

| Skill | File Location | Calculator |
|-------|---------------|------------|
| `easement-valuation-methods` | `.claude/skills/easement-valuation-methods/` | `hydro_easement_calculator.py`, `rail_easement_calculator.py`, `pipeline_easement_calculator.py` |
| `cost-approach-expert` | `.claude/skills/cost-approach-expert/` | `infrastructure_cost_calculator.py` |
| `income-approach-expert` | `.claude/skills/income-approach-expert/` | `land_capitalization_calculator.py` |
| `comparable-sales-adjustment-methodology` | `.claude/skills/` | 49-variable adjustment grid |

#### Infrastructure & Corridor Skills

| Skill | Purpose |
|-------|---------|
| `agricultural-easement-negotiation-frameworks` | Farm operation impact + compensation |
| `cropland-out-of-production-agreements` | Annual compensation models (ON/AB/Farmer) |
| `right-of-way-expert` | ROW area calculation + compensation |
| `transmission-line-technical-specifications` | Voltage requirements, tower spacing |
| `land-assembly-expert` | Multi-parcel corridor budgeting |
| `environmental-due-diligence-expert` | Phase I/II ESA, contamination |

### 2.3 Existing Calculators

| Calculator | Location | Functionality |
|------------|----------|---------------|
| **Hydro Easement Calculator** | `easement-valuation-methods/hydro_easement_calculator.py` | Voltage-based % of fee (25-40% by voltage: 69kV-500kV) |
| **Rail Easement Calculator** | `easement-valuation-methods/rail_easement_calculator.py` | Rail type-based (28-40%: heavy freight to BRT) |
| **Pipeline Easement Calculator** | `easement-valuation-methods/pipeline_easement_calculator.py` | Pipeline type-based (25-40%: crude to sewer) |
| **Infrastructure Cost Calculator** | `cost-approach-expert/infrastructure_cost_calculator.py` | RCN less depreciation for towers, telecom, substations |
| **Land Capitalization Calculator** | `income-approach-expert/land_capitalization_calculator.py` | Land value from rent capitalization |
| **Expropriation Calculator** | | s.13, s.18, s.18(2), s.20 interest |

### 2.4 Existing Slash Commands (44 Total)

**Expropriation-Specific:**
- `/expropriation-compensation` - Statutory compensation calculation
- `/partial-taking-analysis` - Before/after with severance damages
- `/injurious-affection-analysis` - Construction/proximity impacts

**Infrastructure:**
- `/cropland-compensation-analysis` - Agricultural easement compensation
- `/right-of-way-analysis` - ROW area, encumbrance, easement compensation
- `/easement-valuation` - Easement value using 3 methods

**Reporting:**
- `/briefing-note` - Executive brief (1-2 pages)
- `/board-memo` - Board approval documentation
- `/expropriation-timeline` - Critical path with OEA deadlines

---

## 3. R-Plan OCR Extraction Technologies

### 3.1 Understanding Ontario Reference Plans

Reference Plans (R-Plans) are legal survey documents with specific structural elements:

#### Schedule Structure (O.Reg. 43/96)
```
┌─────────────────────────────────────────────────────────────┐
│                    REFERENCE PLAN LAYOUT                     │
├─────────────────────────────────────────────────────────────┤
│  TWO SCHEDULES (top right corner):                          │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │ REGISTRY SCHEDULE│  │ LAND TITLES      │                 │
│  │ - PART numbers   │  │ SCHEDULE         │                 │
│  │ - Subdivision    │  │ - PART numbers   │                 │
│  │   units          │  │ - Parcel numbers │                 │
│  │ - Instrument #s  │  │ - Property IDs   │                 │
│  │ - Property IDs   │  │                  │                 │
│  └──────────────────┘  └──────────────────┘                 │
├─────────────────────────────────────────────────────────────┤
│  PARTS DESIGNATION:                                          │
│  - Part 1 = Fee Simple (taking)                              │
│  - Part 2 = Easement lands                                   │
│  - Part 3 = Remainder lands                                  │
│  - Part 4 = Road widenings                                   │
├─────────────────────────────────────────────────────────────┤
│  AREA CALCULATIONS:                                          │
│  - Metes and bounds descriptions                             │
│  - Bearings (e.g., N45°30'E)                                 │
│  - Distances (metres/feet)                                   │
│  - Areas (hectares, square metres, acres)                    │
└─────────────────────────────────────────────────────────────┘
```

#### Data Extraction Requirements

| Field | Format | Extraction Challenge |
|-------|--------|---------------------|
| Part Numbers | "Part 1", "Part 2" | Low - consistent format |
| Areas | "0.045 ha", "450.0 m²" | Medium - unit variations |
| Legal Descriptions | Metes and bounds | High - complex text |
| Bearings | "N45°30'15"E" | High - special characters |
| PIN References | 9-digit format | Low - consistent |
| Instrument Numbers | Variable formats | Medium - historical variations |

### 3.2 OCR Technology Comparison

| Technology | Strengths | Weaknesses | Cost | Recommendation |
|------------|-----------|------------|------|----------------|
| **Google Document AI** | Custom training, best accuracy on complex layouts | Higher cost at scale | $1.50/1000 pages | **Best for R-Plans** |
| **AWS Textract** | Good structured data extraction | No custom training | $1.50/1000 pages | Good alternative |
| **Azure Document Intelligence** | Strong on tables/forms | Less flexible | Variable | For standardized forms |
| **Claude Vision** | Excellent reasoning, context understanding | Not purpose-built for OCR | Per-token | **Supplement for complex parsing** |
| **Tesseract** | Free, local | Poor on scanned/noisy docs | Free | Fallback only |

### 3.3 Recommended R-Plan Extraction Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                R-PLAN EXTRACTION PIPELINE                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 1: Pre-Processing                                      │
│ - PDF quality assessment (DPI check)                         │
│ - Deskewing and noise reduction                              │
│ - Page segmentation (identify schedule locations)            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 2: Primary OCR (Google Document AI)                    │
│ - Extract text with bounding boxes                           │
│ - Identify table structures                                  │
│ - Extract handwritten annotations                            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 3: Structured Parsing (Custom Python)                  │
│ - Regex patterns for Part numbers                            │
│ - Area unit normalization (ha → m² → acres)                  │
│ - Bearing standardization (DMS → decimal degrees)            │
│ - PIN validation (checksum verification)                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 4: LLM Verification (Claude)                           │
│ - Context-aware error correction                             │
│ - Legal description interpretation                           │
│ - Cross-reference Part numbers with areas                    │
│ - Flag ambiguities for human review                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 5: JSON Output                                         │
│ {                                                            │
│   "reference_plan": "R-1234567",                             │
│   "municipality": "City of Toronto",                         │
│   "parts": [                                                 │
│     {                                                        │
│       "part_number": 1,                                      │
│       "description": "Fee Simple Taking",                    │
│       "area_ha": 0.045,                                      │
│       "area_m2": 450.0,                                      │
│       "pin": "123456789"                                     │
│     }                                                        │
│   ]                                                          │
│ }                                                            │
└─────────────────────────────────────────────────────────────┘
```

### 3.4 Implementation Estimate

| Component | Development Time | Accuracy Target |
|-----------|------------------|-----------------|
| Pre-processing module | 1 week | N/A |
| Google Document AI integration | 1 week | 95%+ raw text |
| Custom parsing logic | 2 weeks | 99%+ Part/Area |
| LLM verification layer | 1 week | 99.5%+ final |
| Testing & validation | 1 week | 99.9% critical fields |

**Total: 6 weeks for production-ready R-Plan extraction**

---

## 4. GeoWarehouse & TREB API Integration

### 4.1 GeoWarehouse Access Options

**Platform Overview:**
- **Owner:** Teranet Inc.
- **Data:** Authoritative Ontario property information (title, ownership, sales history)
- **Access:** Web-based platform for licensed professionals

#### Integration Challenges

| Challenge | Impact | Mitigation |
|-----------|--------|------------|
| No public API documented | Cannot automate bulk downloads | Contact Teranet for enterprise access |
| Web-based access only | Manual data entry required | Consider RPA (robotic process automation) |
| Subscription required | Cost per search/report | Bundle with project budget |

#### Recent Developments (2024-2025)

- **LandLogic Partnership:** AI-powered zoning intelligence now embedded in GeoWarehouse
- **GoVeyance Integration:** End-to-end conveyancing platform coming to Ontario by end of 2025
- **MPAC Data Integration:** Premium property data attributes and reports now available

#### Recommended Approach

```
Option 1: Enterprise API Access (Preferred)
├── Contact Teranet directly: 416-360-5263
├── Request developer/enterprise access documentation
└── Expected: REST API or bulk data export capabilities

Option 2: RPA Automation (Fallback)
├── Use browser automation (Selenium/Playwright)
├── Automate search and download workflows
├── Requires careful compliance with ToS
└── Less reliable than API access

Option 3: Manual with Batch Processing
├── Manually download reports in bulk
├── Use LLM to extract structured data from PDFs
└── Higher labor but lower technical risk
```

### 4.2 TREB MLS API Access

**Platform:** Toronto Regional Real Estate Board (TRREB)
**Access URL:** https://trebapi.torontomls.net

#### Access Requirements

| Requirement | Details |
|-------------|---------|
| TRREB Membership | Only registered TRREB realtors can directly access |
| Developer Partnership | Must work through a realtor partner |
| Data Protocol | RETS (Real Estate Transaction Standard), not REST |
| PropTx RESO Web API | Alternative at query.ampre.ca |

#### Data Available

| Data Type | Availability | Retention |
|-----------|--------------|-----------|
| Active Listings | Full access | Real-time |
| Sold Prices | Available | 2 years historical |
| Rental Rates | Available | 2 years historical |
| Days on Market | Available | 2 years historical |
| Photos/Media | Available | Current listings |

#### Integration Options

| Option | Complexity | Compliance | Recommended For |
|--------|------------|------------|-----------------|
| **PropTx RESO Web API** | Medium | TRREB-approved | Production use |
| **Direct RETS Client** | High | Requires partnership | Full control |
| **Third-party plugins** | Low | Check ToS carefully | Quick pilot |

#### Compliance Warning

> "All boards have very strict rules about how you access and handle the data. Scraping or any other type of data capturing or storing is prohibited unless an agreement is signed."

**Recommendation:** Establish formal data access agreement with TRREB before implementing any automation.

### 4.3 Alternative Data Sources

| Source | Data Type | Access Method |
|--------|-----------|---------------|
| **MPAC (via GeoWarehouse)** | Assessment data, property characteristics | GeoWarehouse subscription |
| **Onland (registry)** | Title documents, registered instruments | Direct subscription |
| **Municipal Open Data** | Zoning, permits, planning | Public APIs (free) |
| **Statistics Canada** | Census, demographics | Public APIs (free) |

---

## 5. AI Vision for Property Description

### 5.1 Vision Model Capabilities

The SOW proposes using AI to "read" property photos and draft improvements descriptions. Current capabilities:

#### Claude Vision (Anthropic)

| Capability | Accuracy | Use Case |
|------------|----------|----------|
| Building type identification | High | "Single-story brick bungalow" |
| Material identification | High | "Asphalt shingles", "vinyl siding" |
| Condition assessment | Medium | "Average wear", "well-maintained" |
| Feature detection | High | "Detached garage", "covered porch" |
| Multi-image reasoning | High | Cross-reference multiple photos |

**Example Prompt:**
```
Analyze these property photos and draft an Improvements Description
for an appraisal report. Include:
- Building type and style
- Exterior materials (walls, roof, foundation)
- Condition assessment (excellent/good/average/fair/poor)
- Notable features (garage, porches, outbuildings)
- Estimated age range based on architectural style

Photos: [1-15 uploaded]
```

#### GPT-4 Vision (OpenAI)

| Capability | Accuracy | Use Case |
|------------|----------|----------|
| Similar to Claude | Comparable | Alternative/comparison |
| Better integration with Azure | N/A | Enterprise deployments |

#### Restb.ai (Specialized Real Estate)

| Capability | Accuracy | Use Case |
|------------|----------|----------|
| Property condition models | High | AVM error reduction (9.2%) |
| Feature detection | Very High | Room types, amenities |
| Duplicate detection | Very High | Listing quality control |
| Watermark/logo detection | Very High | Compliance |

**Key Metric:** Blackstone subsidiary saves $1M+ annually with automated property descriptions

### 5.2 Implementation Architecture

```
┌─────────────────────────────────────────────────────────────┐
│           PROPERTY PHOTO DESCRIPTION PIPELINE                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 1: Photo Upload & Organization                         │
│ - Secure folder upload                                       │
│ - Auto-categorize: exterior/interior/aerial/detail          │
│ - Quality check (resolution, lighting)                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 2: Multi-Photo Vision Analysis (Claude Vision)         │
│ - Process all photos as single context                       │
│ - Extract: materials, condition, features                    │
│ - Generate structured JSON output                            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 3: Report Text Generation                              │
│ - Convert JSON to narrative prose                            │
│ - Apply client style guide                                   │
│ - Insert into report template                                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ OUTPUT: Draft Improvements Description                       │
│                                                              │
│ "The subject features a single-story brick bungalow          │
│ constructed circa 1960 with average wear. The roof           │
│ comprises asphalt shingles in fair condition with            │
│ approximately 10-15 years remaining life. A detached         │
│ two-car garage with concrete block construction is           │
│ located at the rear of the property..."                      │
└─────────────────────────────────────────────────────────────┘
```

### 5.3 Time Savings Estimate

| Task | Current Manual | With AI Vision | Savings |
|------|---------------|----------------|---------|
| Photo review | 15 min | 2 min | 87% |
| Draft description | 30 min | 3 min (review only) | 90% |
| **Total** | **45 min** | **5 min** | **89%** |

---

## 6. Adjustment Quantification Methodologies

### 6.1 The "Arrow Converter" Problem

The SOW identifies a critical issue: qualitative adjustments ("Trust me, bro" arrows) lack defensibility in litigation.

#### Current State
```
Comparable 1: Similar location    → [=]
Comparable 2: Superior location   → [↓]  (Why -10%? Says who?)
Comparable 3: Inferior condition  → [↑]  (How much? Evidence?)
```

#### Target State
```
Comparable 1: Location adjustment: 0% (within 500m, same zoning)
Comparable 2: Location adjustment: -10% (backed by paired sales analysis)
              └── Paired Sales Evidence: 123 Main vs 456 Oak = -9.8%
              └── Regression Analysis: Distance coefficient = -0.02/km
Comparable 3: Condition adjustment: +8% (depreciation calculation)
              └── Cost Analysis: $25,000 deferred maintenance ÷ $312,500 = 8%
```

### 6.2 Existing Repository Capability

The `comparable-sales-adjustment-methodology` skill already provides:

#### 6-Stage Sequential Adjustment Process
1. Property Rights Adjusted Price
2. Financing Terms Adjusted Price
3. Conditions of Sale Adjusted Price
4. Market Conditions (Time) Adjusted Price
5. Location Adjusted Price
6. Physical Characteristics Adjusted Price

#### 49 Physical Adjustment Variables
Organized into categories:
- Site characteristics
- Building characteristics
- Improvement condition
- Functional utility
- External factors

### 6.3 Proposed "Shadow Calculation" Enhancement

```python
# Conceptual implementation of the Dynamic Adjustment Chart

class AdjustmentCalculator:
    """
    Converts qualitative arrows to quantified adjustments
    with documented justification.
    """

    def __init__(self, firm_database: dict, market_data: dict):
        self.firm_db = firm_database  # Historical adjustment library
        self.market = market_data     # Current market conditions

    def calculate_location_adjustment(
        self,
        subject: Property,
        comparable: Property,
        method: str = "paired_sales"
    ) -> AdjustmentResult:
        """
        Quantify location adjustment with evidence.

        Methods:
        - paired_sales: Find matching sales pairs
        - regression: Use hedonic model
        - proxy: Use distance/accessibility metrics
        """

        if method == "paired_sales":
            pairs = self.find_paired_sales(subject.location, comparable.location)
            adjustment = self.calculate_from_pairs(pairs)

        elif method == "regression":
            coefficient = self.market["location_coefficient"]
            distance_km = self.calculate_distance(subject, comparable)
            adjustment = coefficient * distance_km

        return AdjustmentResult(
            adjustment_pct=adjustment,
            method=method,
            evidence=pairs or coefficient,
            confidence=self.calculate_confidence(method, len(pairs)),
            justification_text=self.generate_justification(adjustment, method)
        )
```

### 6.4 USPAP/CUSPAP Compliance Requirements

| Requirement | Implementation |
|-------------|----------------|
| Market evidence support | Store paired sales database |
| Method transparency | Document method selection logic |
| Adjustment documentation | Generate audit trail |
| Reconciliation | Weight by confidence scores |
| Credible results | Validate against market benchmarks |

---

## 7. Ontario Legal Framework Analysis

### 7.1 Expropriations Act Compensation Structure

#### Section 13 - Basis of Compensation

```
┌─────────────────────────────────────────────────────────────┐
│         ONTARIO EXPROPRIATIONS ACT COMPENSATION              │
│                      (Section 13)                            │
└─────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
    ┌───────────┐   ┌───────────┐   ┌───────────┐
    │  MARKET   │   │DISTURBANCE│   │ INJURIOUS │
    │   VALUE   │   │  DAMAGES  │   │ AFFECTION │
    │  (s.14)   │   │   (s.18)  │   │ (s.18(2)) │
    └───────────┘   └───────────┘   └───────────┘
         │               │               │
         ▼               ▼               ▼
    ┌───────────┐   ┌───────────┐   ┌───────────┐
    │- Open     │   │- Relocation│  │- Partial  │
    │  market   │   │  costs    │   │  taking   │
    │- Willing  │   │- Moving   │   │  damage   │
    │  seller   │   │  expenses │   │- Construct│
    │- Willing  │   │- Legal    │   │  impacts  │
    │  buyer    │   │  costs    │   │- Permanent│
    │- Valuation│   │- 5% allow.│   │  proximity│
    │  date     │   │- Business │   │           │
    └───────────┘   │  losses   │   └───────────┘
                    └───────────┘
                         │
                         ▼
                    ┌───────────┐
                    │   PLUS:   │
                    │ INTEREST  │
                    │  (s.20)   │
                    │  6-12%    │
                    └───────────┘
```

#### Section 14 - Market Value Definition

> "The market value of land expropriated is the amount that the land might be expected to realize if sold in the open market by a willing seller to a willing buyer."

**Key Principles:**
1. Valuation as of the "valuation date" (usually expropriation date)
2. Ignore post-valuation date appreciation/depreciation
3. Disregard the scheme that gave rise to expropriation
4. No enhancement or diminution due to the project

#### Section 18 - Disturbance Damages

**Allowable Disturbance Damages:**
| Category | Calculation |
|----------|-------------|
| Relocation costs | Reasonable moving expenses |
| Legal/survey costs | Costs acquiring replacement premises |
| 5% allowance (residential) | 5% × market value for inconvenience |
| Improvement value | Value not reflected in market value |
| Business losses | From relocation necessitated by expropriation |

**Note:** Interest NOT applied to disturbance damages.

#### Section 20 - Interest

| Condition | Rate |
|-----------|------|
| Standard rate | 6% per year |
| Owner-caused delay | May reduce below 6% |
| Authority-caused delay | May increase up to 12% |
| Start date | When owner ceases residence/productive use |

### 7.2 Forms 1-12 Compliance

The repository's Stevi agent already tracks these, but for reference:

| Form | Purpose | Critical Timeline |
|------|---------|-------------------|
| Form 1 | Notice of Application for Approval | Initial notice |
| Form 2 | Notice of Hearing | 3 months before hearing |
| Form 3 | Certificate of Approval | After approval granted |
| Form 4 | Notice of Expropriation | Registration requirement |
| Form 5 | Registered Owner's Election | Owner response |
| Form 6 | Notice of Abandonment | If authority abandons |
| Form 7 | Notice of Possession | Date of possession |
| Form 8-12 | Various procedural forms | Variable |

---

## 8. Hydro One Transmission Corridor Specifics

### 8.1 "Across the Fence" Valuation Method

For hydro corridor secondary land uses, the "across the fence" method is applied:

```
Market Value of ROW = Market Value of Adjacent Land (unimproved)
                    × Area of ROW
                    × Easement Discount Factor
```

**Key Principle:** The ROW value is an extension of the adjacent lot, assuming unimproved land.

### 8.2 Existing Easement Calculator (v2.1)

The repository's `hydro_easement_calculator.py` already implements voltage-based discounts:

| Voltage | Base Discount | Adjustment Factors |
|---------|--------------|-------------------|
| 69 kV | 25% | EMF, tower placement, vegetation |
| 115 kV | 28% | + building proximity |
| 230 kV | 32% | + access roads |
| 345 kV | 36% | + construction impacts |
| 500 kV | 40% | Full range |

**Adjustment Factors Available:**
- EMF concerns (+0-5%)
- Tower placement on parcel (+0-5%)
- Vegetation restrictions (+0-5%)
- Access road requirements (+0-3%)
- Building proximity setbacks (+0-5%)

### 8.3 Value Diminution Research

Based on case law and market studies:

| Scenario | Value Diminution Range |
|----------|----------------------|
| Existing corridor | -4.76% to -54.23% |
| New corridor (no prior) | -10.5% to -46.65% |
| Distance-based | Greater distance = lower diminution |

**Key Case:** *Lazar v. Hydro One* - OMB concluded -30% injurious affection (not appealed).

### 8.4 Ontario Federation of Agriculture (OFA) Guidance

Recent OFA resources (May 2024):

- **Cropland Out of Production Factsheet:** Compensation models for ongoing productivity loss
- **Easements on Farm Properties Webinar (April 2024):** Negotiation guidance
- **Letter to Attorney General (June 2024):** Expropriation reform concerns

---

## 9. CUSPAP Compliance Considerations

### 9.1 Overview

All appraisals in Canada by AIC members must comply with CUSPAP (Canadian Uniform Standards of Professional Appraisal Practice).

**Current Version:** CUSPAP 2024 (effective January 1, 2024)

### 9.2 AVM and AI Integration Rules

#### Definitions

| Term | CUSPAP Definition |
|------|-------------------|
| **AVM** | "A computer program that analyzes data used in an automated process that may include regression, adaptive estimation, neural network, expert reasoning and artificial [intelligence]" |
| **Appraiser-Assisted AVM** | "An automated valuation model (AVM) that requires appraiser judgment in developing and setting parameters for comparable data search and final reconciliation processes" |

#### Key Requirement

> "The output of an AVM becomes a value when a Member applies judgment to the output."

**Implication for SOW:** All AI-generated outputs must be reviewed and approved by a designated appraiser. The AI assists but does not replace professional judgment.

### 9.3 AVM Output Validation

CUSPAP 2024 added "AVM Output Validation" as a consulting assignment type:

- Used to determine if AVM data output supports intended use
- Distinct from mass appraisal
- Considered Appraiser-Assisted AVM

### 9.4 Documentation Requirements

For AI-assisted appraisals:

| Requirement | Implementation |
|-------------|----------------|
| Method disclosure | Document AI tools used |
| Data sources | List automated data sources |
| Human oversight | Record appraiser review/approval |
| Quality control | Document validation process |
| Limitations | State AI model limitations |

---

## 10. Phase-by-Phase Implementation Analysis

### Phase 1: "Low Hanging Fruit" (Immediate Wins)

#### 1A. Automated Area & Economic Overviews

| Aspect | Analysis |
|--------|----------|
| **Technical Feasibility** | ✅ HIGH - LLM text generation is mature |
| **Data Sources** | Statistics Canada (free), municipal open data |
| **Existing Capability** | Partial - general LLM available |
| **Implementation Time** | 1 week for templates + prompts |
| **Risk** | LOW - human review required anyway |

**Recommended Approach:**
```
Input: Municipality + Project Context
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│ DATA AGGREGATION                                             │
│ - Pull census data (population, growth rates)               │
│ - Pull economic indicators (employment, major employers)    │
│ - Pull transit context (proximity, planned projects)        │
│ - Pull interest rate environment (BoC rate, mortgage rates) │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│ LLM SYNTHESIS                                                │
│ - Generate 1-2 page overview                                 │
│ - Apply client-specific style                                │
│ - Insert into report template                                │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
Output: Draft Area Overview (ready for appraiser review)
```

#### 1B. Visual Property Description (AI Vision)

| Aspect | Analysis |
|--------|----------|
| **Technical Feasibility** | ✅ HIGH - Claude Vision/GPT-4V proven |
| **Data Sources** | Site photos (analyst-provided) |
| **Existing Capability** | Repository has Claude integration |
| **Implementation Time** | 1 week for prompts + pipeline |
| **Risk** | LOW - review mandatory |

**Implementation:** See Section 5 above.

### Phase 2: Data Pipeline & "Before/After" Framework

#### 2A. R-Plan & Legal Extraction (OCR Module)

| Aspect | Analysis |
|--------|----------|
| **Technical Feasibility** | ⚠️ MEDIUM - Custom pipeline required |
| **Data Sources** | PDF R-Plans from Land Registry |
| **Existing Capability** | MLS extractor exists (adaptable) |
| **Implementation Time** | 6 weeks (see Section 3) |
| **Risk** | MEDIUM - accuracy critical for legal docs |

**Implementation:** See Section 3 above.

#### 2B. The "Pre-Flight" Check

| Aspect | Analysis |
|--------|----------|
| **Technical Feasibility** | ✅ HIGH - Folder validation is simple |
| **Existing Capability** | ✅ **ALREADY EXISTS** - Stevi agent |
| **Implementation Time** | 1 week to adapt Stevi for this use case |
| **Risk** | LOW |

**Required Documents Checklist:**
```python
REQUIRED_DOCUMENTS = {
    "pin_search": ["*.pdf", "pin*.pdf"],           # Property identification
    "r_plan": ["R-*.pdf", "reference_plan*.pdf"],  # Reference plan
    "zoning_map": ["zoning*.pdf", "*zoning*.jpg"], # Zoning map
    "official_plan": ["official_plan*.pdf"],       # Official plan
    "title_search": ["title*.pdf", "parcel*.pdf"], # Title documents
    "photos": ["*.jpg", "*.png", "IMG_*.jpg"],     # Site photos (min 10)
}
```

#### 2C. API Integration

| Aspect | Analysis |
|--------|----------|
| **Technical Feasibility** | ⚠️ MEDIUM - Requires partnerships |
| **GeoWarehouse** | No public API; contact Teranet for enterprise |
| **TREB MLS** | RETS protocol; requires realtor partnership |
| **Implementation Time** | 4-8 weeks (includes partnership setup) |
| **Risk** | MEDIUM - dependent on third-party agreements |

### Phase 3: Valuation Support & Logic Standardization

#### 3A. Dynamic Adjustment Chart ("Arrow Converter")

| Aspect | Analysis |
|--------|----------|
| **Technical Feasibility** | ✅ HIGH |
| **Existing Capability** | ✅ **PARTIALLY EXISTS** - comparable-sales-adjustment-methodology skill |
| **Implementation Time** | 2 weeks to add quantification + justification |
| **Risk** | LOW-MEDIUM - needs validation against firm historical data |

**Enhancement Required:**
1. Add "Shadow Calculation" module
2. Build justification text generator
3. Integrate firm's historical adjustment database
4. Add confidence scoring

#### 3B. Easement Factor Logic

| Aspect | Analysis |
|--------|----------|
| **Technical Feasibility** | ✅ HIGH |
| **Existing Capability** | ✅ **ALREADY EXISTS** - v2.1 easement calculators |
| **Implementation Time** | 1 week to integrate with workflow |
| **Risk** | LOW |

**Available Calculators:**
- `hydro_easement_calculator.py` (69kV-500kV, 25-40%)
- `rail_easement_calculator.py` (heavy freight to BRT, 28-40%)
- `pipeline_easement_calculator.py` (crude to sewer, 25-40%)

### Phase 4: Output & Quality Control ("The Shield")

#### 4A. The "Interceptor" (Formatting Guardrails)

| Aspect | Analysis |
|--------|----------|
| **Technical Feasibility** | ✅ HIGH |
| **Existing Capability** | LLM-based style enforcement possible |
| **Implementation Time** | 2 weeks |
| **Risk** | LOW |

**Client Style Guide Examples:**
```yaml
metrolinx_style:
  definitions:
    - "Metrolinx" not "METROLINX" or "metrolinx"
    - "Ontario Line" not "Ontario line" or "ontario line"
  citations:
    format: "[Author, Year, page]"
  punctuation:
    prefer: "colon" over "semicolon" in lists

hydro_one_style:
  terminology:
    - "transmission corridor" not "hydro corridor"
    - "statutory easement" with specific reference
```

#### 4B. Memo Generator

| Aspect | Analysis |
|--------|----------|
| **Technical Feasibility** | ✅ HIGH |
| **Existing Capability** | ✅ **ALREADY EXISTS** - board-memo-expert, briefing-note-expert skills |
| **Implementation Time** | 1 week to add Metrolinx-specific template |
| **Risk** | LOW |

**Existing Commands:**
- `/briefing-note` - 1-2 page executive brief
- `/board-memo` - Board approval documentation

---

## 11. Risk Assessment

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| R-Plan OCR accuracy issues | Medium | High | Multi-stage validation, human review required |
| API access denied (GeoWarehouse/TREB) | Medium | Medium | Fallback to manual download + LLM extraction |
| AI hallucination in legal descriptions | Low | High | Cross-reference with source documents, mandatory review |
| Integration complexity | Medium | Medium | Phased implementation, extensive testing |

### Compliance Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| CUSPAP violation | Low | High | Document AI as tool, appraiser judgment required |
| Data privacy breach | Low | Very High | Enterprise-grade LLM environment, no data logging |
| Metrolinx format rejection | Medium | Medium | Interceptor style enforcement, template validation |

### Operational Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| User adoption resistance | Medium | Medium | Demonstrate time savings, gradual rollout |
| Dependency on AI tools | Medium | Medium | Maintain manual fallback procedures |
| Cost overrun | Low | Medium | Fixed-fee phases, clear scope boundaries |

### Risk Matrix

```
                    IMPACT
                 Low    Medium    High
           ┌─────────┬─────────┬─────────┐
    High   │         │         │         │
           ├─────────┼─────────┼─────────┤
P   Medium │         │ API     │ R-Plan  │
R          │         │ Access  │ Accuracy│
O          │         │ Adoption│         │
B   ───────├─────────┼─────────┼─────────┤
           │         │         │ CUSPAP  │
    Low    │         │ Cost    │ AI Error│
           │         │         │ Privacy │
           └─────────┴─────────┴─────────┘
```

---

## 12. Recommended Technology Stack

### Core Infrastructure

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **LLM (Text)** | Claude Opus 4.5 / Sonnet | Already integrated in repository |
| **LLM (Vision)** | Claude Vision | Multi-modal reasoning |
| **OCR** | Google Document AI | Best accuracy on complex layouts |
| **Structured Extraction** | Custom Python + Pydantic | Type-safe JSON schemas |
| **Workflow** | Existing agent framework | Leverage Alexi, Christi, Stevi |

### Data Pipeline

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **PDF Processing** | PyMuPDF + pdf2image | High-quality text/image extraction |
| **Document Storage** | Local filesystem | Secure, no cloud dependency |
| **Data Validation** | JSON Schema + Pydantic | Enforce structure |
| **Calculations** | Existing Python calculators | v2.1 already production-ready |

### Integration Layer

| Component | Technology | Status |
|-----------|------------|--------|
| **GeoWarehouse** | TBD (contact Teranet) | Requires enterprise agreement |
| **TREB MLS** | PropTx RESO Web API | Requires realtor partnership |
| **Teraview** | Manual + LLM extraction | Fallback approach |

### Output Generation

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Report Templates** | Markdown + Pandoc | Flexible, version-controlled |
| **PDF Generation** | `/convert-to-pdf` command | Already exists |
| **Style Enforcement** | LLM-based Interceptor | Client-specific rules |

---

## 13. Next Steps & Action Items

### Immediate (Week 1)

| Action | Owner | Deliverable |
|--------|-------|-------------|
| Review this research document | Alex Pitt | Feedback/approval |
| Identify pilot project | Alex Pitt | 1 active corridor project |
| Obtain sample R-Plans | Alex Pitt | 10+ representative R-Plans for testing |
| Contact Teranet | Alex Pitt | Enterprise API inquiry |

### Short-term (Weeks 2-4)

| Action | Owner | Deliverable |
|--------|-------|-------------|
| Implement Phase 1A (Area Overviews) | Dev Team | Working prototype |
| Implement Phase 1B (Photo Descriptions) | Dev Team | Working prototype |
| Adapt Stevi for Pre-Flight checks | Dev Team | Folder validation script |
| Begin R-Plan OCR development | Dev Team | Stage 1-2 pipeline |

### Medium-term (Weeks 5-8)

| Action | Owner | Deliverable |
|--------|-------|-------------|
| Complete R-Plan OCR pipeline | Dev Team | Production-ready extraction |
| Enhance adjustment quantification | Dev Team | Shadow Calculation module |
| Integrate easement calculators | Dev Team | Workflow integration |
| Client style guide implementation | Dev Team | Interceptor rules |

### Validation (Weeks 8-10)

| Action | Owner | Deliverable |
|--------|-------|-------------|
| Retroactive benchmark testing | Alex Pitt + Dev | Accuracy metrics on completed files |
| Live pilot on active project | Alex Pitt | Real-world validation |
| CUSPAP compliance review | AIC member | Compliance sign-off |
| ROI documentation | Alex Pitt | Time savings evidence |

---

## Appendix A: Source References

### Research Sources

1. [GeoWarehouse - Teranet](https://www2.geowarehouse.ca) - Ontario property data platform
2. [Teranet Real Estate Solutions](https://www.teranet.ca/real-estate-solutions/) - Data integration options
3. [LandLogic + Teranet Partnership](https://www.landlogic.ai/latest-updates/smarter-land-decisions) - AI zoning intelligence
4. [Pat Arlia - TREB Data Access](https://pat-arlia.medium.com/navigating-the-toronto-real-estate-boards-treb-s-data-exchange-522b728b4009) - RETS protocol guide
5. [TRREB API Access](https://trebapi.torontomls.net/) - Direct API portal
6. [PropTx RESO Web API](https://webapp.proptx.ca) - Alternative MLS access
7. [OCR Benchmarking - Springer](https://link.springer.com/article/10.1007/s42001-021-00149-1) - Textract vs Document AI
8. [AWS Textract](https://aws.amazon.com/textract/) - OCR capabilities
9. [Unstract - LLM Document Extraction](https://unstract.com/blog/comparing-approaches-for-using-llms-for-structured-data-extraction-from-pdfs/) - Structured extraction methods
10. [Restb.ai - Real Estate AI](https://restb.ai/) - Property photo analysis
11. [C3 AI Property Appraisal](https://c3.ai/products/c3-ai-property-appraisal/) - Enterprise appraisal AI
12. [Claude AI for Real Estate](https://arunprakash.ai/posts/anthropic-claude3-industry-usecases/real_estate.html) - Vision capabilities
13. [Ontario Expropriations Act](https://www.ontario.ca/laws/statute/90e26) - Statutory framework
14. [Sullivan Mahoney - Expropriation Compensation](https://sullivanmahoney.com/expropriation-what-compensation-is-an-owner-entitled-to/) - Legal analysis
15. [OEA Q&A](https://www.oea.on.ca/qanda.aspx) - Ontario Expropriation Association
16. [Unified LLP - Expropriation](https://unifiedllp.com/determining-market-value-in-expropriation-compensation-claims-expropriation-lawyer-toronto/) - Highest & best use
17. [AIC - Across the Fence Method](https://www.aicanada.ca/article/an-across-the-fence-approach-for-valuing-a-right-of-way-across-a-hydro-corridor/) - ROW valuation
18. [OFA - Hydro One Transmission](https://ofa.on.ca/resources/southwestern-ontario-hydro-one-transmission-line-projects/) - Agricultural impacts
19. [Lansink - Power Corridor Study](https://lansink.ca/market-study-power-corridors-april-2013/) - Value diminution research
20. [Infrastructure Ontario - PSLUP](https://www.infrastructureontario.ca/en/what-we-do/real-estate-services/surplus-properties-sales-program-overview/pslup---frequently-asked-questions/) - Secondary land use
21. [OEB Decision EB-2024-0155](https://www.rds.oeb.ca/CMWebDrawer/Record/875410/File/document) - Easement compensation
22. [CUSPAP 2024](https://www.aicanada.ca/about-aic/cuspap/) - Canadian appraisal standards
23. [AIC - AVM Definition](https://www.aicanada.ca/resource-library/automated-valuation-model-avm/) - AI in appraisal
24. [Ontario Land Registry - Reference Plans](https://www.ontario.ca/land-registration/97005-combined-reference-plans) - R-Plan requirements
25. [O.Reg. 43/96](https://www.canlii.org/en/on/laws/regu/o-reg-43-96/latest/o-reg-43-96.html) - Surveys, Plans and Descriptions
26. [Protect Your Boundaries - R-Plan Guide](https://www.protectyourboundaries.ca/referenceplan.html) - R-Plan structure

---

## Appendix B: Repository Asset Inventory

### Agents (Infrastructure-Specific)
- `.claude/agents/alexi` - Expropriation Appraisal Expert
- `.claude/agents/christi` - Expropriation Law Specialist
- `.claude/agents/katy` - Transit Corridor Specialist
- `.claude/agents/shadi` - Utility Transmission Corridor Specialist
- `.claude/agents/stevi` - Compliance Enforcer

### Skills (Valuation & Expropriation)
- `.claude/skills/easement-valuation-methods/`
- `.claude/skills/cost-approach-expert/`
- `.claude/skills/income-approach-expert/`
- `.claude/skills/comparable-sales-adjustment-methodology/`
- `.claude/skills/expropriation-compensation-entitlement-analysis/`
- `.claude/skills/severance-damages-quantification/`
- `.claude/skills/injurious-affection-assessment/`
- `.claude/skills/forms-1-12-completeness-verification/`

### Calculators
- `hydro_easement_calculator.py`
- `rail_easement_calculator.py`
- `pipeline_easement_calculator.py`
- `infrastructure_cost_calculator.py`
- `land_capitalization_calculator.py`
- `expropriation_calculator.py`

### Commands
- `/expropriation-compensation`
- `/partial-taking-analysis`
- `/injurious-affection-analysis`
- `/easement-valuation`
- `/briefing-note`
- `/board-memo`

---

*End of Research Document*
