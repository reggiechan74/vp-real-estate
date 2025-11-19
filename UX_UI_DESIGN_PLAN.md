# Complete UI/UX Design Plan for VP Real Estate Platform

## Executive Summary

This document expands Gemini's initial UI/UX concept to encompass the **entire scope** of your institutional real estate platform. Your repository contains far more than 3 calculators - it's a comprehensive suite of 25+ slash commands, 10 financial calculators, 41+ specialized skills, and 3 AI personas.

**Scale of Platform:**
- **25 Slash Commands** across 6 categories
- **10 Financial Calculators** (Effective Rent, Credit, IFRS16, Renewal, Variance, Options, Rollover, Default, Relative Valuation, MLS)
- **41+ Specialized Skills** (commercial leases, assignments, indemnities, negotiations, valuations, expropriation, etc.)
- **3 AI Personas** (Adam/Analyst, Reggie/VP, Dennis/Advisor)
- **24-Section Lease Abstraction** (Industrial & Office templates)
- **4 Document Comparison Tools**
- **7 Compliance & Legal Tools**

---

## Phase 1: Expanded UI/UX Design Philosophy

### 1.1 Design Philosophy (Enhanced)

**Vibe:** Institutional Real Estate Excellence
- Clean, high-contrast, data-dense but scannable
- Professional Bloomberg Terminal meets modern SaaS
- "Serious money, serious tools" aesthetic
- Zero fluff, maximum information density
- Keyboard-first power user workflows

**Color Palette: "Navy & Slate Pro"**
- **Primary**: Deep Navy `#0f172a` (Trust, Finance, Authority)
- **Secondary Gold**: Bronze/Gold `#d97706` (Reggie's Insights, Warnings)
- **Secondary Blue**: Steel Blue `#3b82f6` (Adam's Analysis, Information)
- **Secondary Sage**: Sage Green `#059669` (Dennis's Wisdom, Success)
- **Background**: Light Grey `#f8fafc` (Canvas)
- **Card Background**: Pure White `#ffffff`
- **Text Primary**: Charcoal `#1e293b`
- **Text Secondary**: Slate `#64748b`
- **Danger**: Crimson `#dc2626` (Defaults, Risks)
- **Warning**: Amber `#f59e0b` (Attention Required)
- **Success**: Emerald `#10b981` (Approved, Complete)

**Typography:**
- **Headings**: Inter Bold (Modern, Professional)
- **Body**: Inter Regular (Highly readable)
- **Data/Numbers**: JetBrains Mono (Monospaced for financial data)
- **Legal Text**: Georgia (Traditional, authoritative)

**Data Density Principles:**
1. **Information Hierarchy**: Critical data always visible above fold
2. **Progressive Disclosure**: Details expand on demand
3. **Scannable Tables**: Zebra striping, hover states, sortable columns
4. **Smart Defaults**: Pre-fill forms with intelligent defaults
5. **Keyboard Shortcuts**: Power users never need the mouse

---

## Phase 2: Complete Information Architecture

### 2.1 Navigation Structure

**Primary Navigation (Left Sidebar - Collapsible)**

```
┌─────────────────────────────────────┐
│ 🏢 VP REAL ESTATE PLATFORM          │
├─────────────────────────────────────┤
│ 🏠 Dashboard                        │
├─────────────────────────────────────┤
│ 👥 THE TEAM ROOM                    │
│   ├─ 💬 Chat with Adam (Analyst)    │
│   ├─ 💼 Chat with Reggie (VP)       │
│   └─ 🎯 Chat with Dennis (Advisor)  │
├─────────────────────────────────────┤
│ 📊 FINANCIAL ANALYSIS               │
│   ├─ 💰 Effective Rent Calculator   │
│   ├─ 📈 Renewal Economics           │
│   ├─ 🏦 Tenant Credit Analysis      │
│   ├─ 📉 Option Valuation            │
│   ├─ 📊 Market Comparison           │
│   ├─ 📅 Rollover Analysis           │
│   ├─ 📏 Rental Variance             │
│   ├─ 🎯 Relative Valuation (MCDA)   │
│   ├─ 🏠 MLS Extractor               │
│   └─ 📝 Recommendation Memo         │
├─────────────────────────────────────┤
│ 📄 LEASE PROCESSING                 │
│   ├─ 📋 Lease Abstraction           │
│   ├─ 📅 Critical Dates Extraction   │
│   ├─ 🔄 Compare Amendment           │
│   ├─ ⚖️  Compare Offers             │
│   ├─ 📑 Compare to Precedent        │
│   └─ 📊 Lease vs Lease              │
├─────────────────────────────────────┤
│ ⚖️  COMPLIANCE & LEGAL              │
│   ├─ ✅ Assignment Consent          │
│   ├─ ⚠️  Default Analysis           │
│   ├─ 🌱 Environmental Compliance    │
│   ├─ 📜 Estoppel Certificate        │
│   ├─ 🛡️  Insurance Audit            │
│   ├─ 📨 Notice Generator            │
│   └─ 🔨 Work Letter Generator       │
├─────────────────────────────────────┤
│ 📊 ACCOUNTING                       │
│   └─ 📚 IFRS 16 Calculator          │
├─────────────────────────────────────┤
│ 🗄️  REPORTS VAULT                   │
│   ├─ 📁 Browse Reports              │
│   ├─ 🔍 Search Reports              │
│   └─ 📥 Export Archive              │
├─────────────────────────────────────┤
│ ⚙️  UTILITIES                       │
│   ├─ 📄 PDF Converter               │
│   └─ 📋 Templates Library           │
└─────────────────────────────────────┘
```

### 2.2 User Personas & Journeys

**Persona 1: Sarah - VP of Leasing (Power User)**
- **Goals**: Quick deal analysis, portfolio oversight, strategic decisions
- **Journey**: Dashboard → Effective Rent → Reggie Chat → Approve Deal
- **Pain Points**: Needs speed, hates repetitive data entry
- **Features**: Keyboard shortcuts, bulk uploads, API access

**Persona 2: Mike - Asset Manager (Compliance)**
- **Goals**: Risk assessment, compliance audits, documentation
- **Journey**: Insurance Audit → Default Analysis → Generate Notices
- **Pain Points**: Must ensure nothing falls through cracks
- **Features**: Checklists, alerts, audit trails

**Persona 3: Jenny - Junior Analyst (Learning)**
- **Goals**: Learn the business, run standard analyses, get mentorship
- **Journey**: Chat with Adam → Run Calculator → Review Report
- **Pain Points**: Doesn't know which tool to use when
- **Features**: Tooltips, guided workflows, Adam's explanations

---

## Phase 3: Enhanced Sitemap & Page Designs

### 3.1 Dashboard (Home Page)

**Layout: 3-Column Grid**

**Column 1 (Left): Portfolio Metrics**
```
┌────────────────────────────────┐
│ PORTFOLIO OVERVIEW             │
├────────────────────────────────┤
│ 📊 Total GLA: 2.4M SF          │
│ 💰 Total ARR: $48.2M           │
│ 📈 Occupancy: 94.2%            │
│ 📅 WALT: 4.8 years             │
│ ⚠️  Expiries (12mo): 18 leases  │
│ 🔴 Defaults: 2 tenants         │
└────────────────────────────────┘
```

**Column 2 (Center): Quick Actions**
```
┌────────────────────────────────┐
│ QUICK ACTIONS                  │
├────────────────────────────────┤
│ [📤 Upload Lease Document]     │
│ [💬 Ask Reggie a Question]     │
│ [📊 Run Effective Rent]        │
│ [📋 Abstract New Lease]        │
└────────────────────────────────┘

┌────────────────────────────────┐
│ RECENT ACTIVITY                │
├────────────────────────────────┤
│ ✅ 2h ago: Effective Rent      │
│    (Acme Corp Renewal)         │
│ ⏳ 4h ago: Credit Analysis     │
│    (TechStart Inc)             │
│ 📄 Yesterday: Lease Abstract   │
│    (Warehouse 401K)            │
└────────────────────────────────┘
```

**Column 3 (Right): Alerts & Insights**
```
┌────────────────────────────────┐
│ ⚠️  ATTENTION REQUIRED         │
├────────────────────────────────┤
│ 🔴 Default Notice Due:         │
│    Tenant XYZ (Bldg 5)         │
│    Due: Nov 21, 2025           │
│                                │
│ 🟡 Option Exercise Window:     │
│    ABC Corp Renewal            │
│    Deadline: Dec 1, 2025       │
│                                │
│ 🟢 Insurance Renewal:          │
│    Portfolio Policy            │
│    Review by: Dec 15, 2025     │
└────────────────────────────────┘
```

### 3.2 The Team Room (Enhanced Chat Interface)

**Layout: Full Width, Split View**

**Persona Selector (Top Bar)**
```
┌──────────────────────────────────────────────────────────────┐
│ SELECT YOUR ADVISOR:                                         │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐                      │
│ │   ADAM   │ │  REGGIE  │ │  DENNIS  │  [Upload File 📎]   │
│ │ Analyst  │ │    VP    │ │ Advisor  │                      │
│ │  (Fast)  │ │ (Expert) │ │ (Mentor) │  [Clear Chat 🗑️]     │
│ └──────────┘ └──────────┘ └──────────┘                      │
└──────────────────────────────────────────────────────────────┘
```

**Persona-Specific System Prompts:**

**Adam (Analyst) - Blue Theme**
- Avatar: 👔 Blue tie icon
- Prompt: "I'm Adam, your Senior Analyst. I handle day-to-day deal analysis with institutional rigor. I'm fast, diplomatic, and quantify everything. What can I analyze for you?"
- Response Style: Concise bullet points, clear recommendations, 80/20 analysis
- Use Cases: Standard lease reviews, routine credit checks, simple deal comps

**Reggie (VP) - Gold Theme**
- Avatar: 💼 Briefcase icon
- Prompt: "I'm Reggie Chan, CFA, FRICS. Over 20 years managing institutional portfolios. I specialize in complex situations, crisis turnarounds, and forensic analysis. What challenge are we solving?"
- Response Style: Deep analysis, exhaustive documentation, brutally honest
- Use Cases: Distressed assets, fraud detection, complex negotiations, crisis situations

**Dennis (Advisor) - Sage Theme**
- Avatar: 🎯 Compass icon
- Prompt: "I'm Dennis. I've seen 36 years of this business - multiple cycles, countless deals, every mistake in the book. Skip the BS - what's really going on and what do you need to decide?"
- Response Style: Blunt wisdom, strategic perspective, psychological insights
- Use Cases: Career decisions, negotiation psychology, people management, reality checks

**Chat Features:**
- File upload (PDF/DOCX/Excel/Images)
- Code blocks with syntax highlighting
- Tables render as proper HTML tables
- Charts/graphs render inline
- Download conversation as PDF
- Share permalink to conversation
- Voice input option

### 3.3 Financial Analysis Module (Deep Dive)

#### 3.3.1 Effective Rent Calculator

**Page Layout: Form + Results Split View**

**Left Panel: Input Form**
```
┌──────────────────────────────────┐
│ EFFECTIVE RENT CALCULATOR        │
├──────────────────────────────────┤
│ Deal Parameters                  │
│ Base Rent ($/SF/Year): [30.00]   │
│ Rentable Area (SF): [10,000]     │
│ Lease Term (Months): [60]        │
│                                  │
│ Tenant Incentives                │
│ Free Rent (Months): [3]          │
│ TI Allowance ($/SF): [25.00]     │
│ Moving Allowance ($): [10,000]   │
│ Leasing Commission (%): [5.0]    │
│                                  │
│ Landlord Economics               │
│ Discount Rate (%): [6.5]         │
│ Property Tax ($/SF): [4.50]      │
│ OpEx ($/SF): [8.00]              │
│ Management Fee (%): [5.0]        │
│                                  │
│ [Calculate NER] [Reset] [Save]   │
└──────────────────────────────────┘
```

**Right Panel: Dynamic Results**
```
┌──────────────────────────────────┐
│ RESULTS SUMMARY                  │
├──────────────────────────────────┤
│ Net Effective Rent: $27.14/SF    │
│ Gross Effective Rent: $28.50/SF  │
│ NPV (Landlord): $1,247,893       │
│ IRR: 7.8%                        │
│ Breakeven Rent: $26.12/SF        │
│                                  │
│ [View Cash Flow] [Export Excel]  │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│ CASH FLOW ANALYSIS (Chart)       │
├──────────────────────────────────┤
│  📊 Plotly Interactive Chart     │
│  - Monthly Cash Flow             │
│  - Cumulative NPV                │
│  - Breakeven Timeline            │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│ SENSITIVITY ANALYSIS (Heatmap)   │
├──────────────────────────────────┤
│  🔥 Base Rent vs TI Allowance    │
│  Shows NER impact across ranges  │
└──────────────────────────────────┘
```

#### 3.3.2 Tenant Credit Analysis

**Form Sections:**
1. **Company Information** (Name, Industry, Years Operating)
2. **Financial Ratios** (DSCR, Current Ratio, Debt/EBITDA, ICR)
3. **Revenue Metrics** (ARR, Growth Rate, Gross Margin)
4. **Qualitative Factors** (Management, Market Position, Lease % of Revenue)

**Output: Credit Scorecard**
```
┌────────────────────────────────────────┐
│ CREDIT SCORE: 72/100                   │
│ RATING: B+ (Acceptable Risk)           │
├────────────────────────────────────────┤
│ Financial Health: ████████░░ 8/10      │
│ Cash Flow Coverage: ██████░░░░ 6/10    │
│ Revenue Stability: ████████░░ 8/10     │
│ Management Quality: ███████░░░ 7/10    │
├────────────────────────────────────────┤
│ RECOMMENDED SECURITY:                  │
│ ✓ Personal Guarantee Required          │
│ ✓ Security Deposit: 6 months rent      │
│ ✓ Quarterly Financial Reporting        │
│ ⚠️  Consider Parent Company Guarantee  │
└────────────────────────────────────────┘
```

#### 3.3.3 Relative Valuation (MCDA)

**The Power Tool: 25-Variable Competitive Positioning**

**Interface: Variable Sliders + Real-time Scoring**
```
┌─────────────────────────────────────────┐
│ COMPETITIVE POSITIONING MATRIX          │
├─────────────────────────────────────────┤
│ Location Variables (Weight: 30%)        │
│ ├─ Highway Access: ████████░░ 8        │
│ ├─ Transit Access: ██████░░░░ 6        │
│ ├─ Labor Market: ████████░░ 8          │
│                                         │
│ Building Variables (Weight: 25%)        │
│ ├─ Clear Height: ███████░░░ 7          │
│ ├─ Column Spacing: ████████░░ 8        │
│ ├─ Loading Doors: ██████░░░░ 6         │
│                                         │
│ Financial Variables (Weight: 25%)       │
│ ├─ Rent ($/SF): ███████░░░ 7           │
│ ├─ OpEx ($/SF): ████████░░ 8           │
│ ├─ TI Allowance: ██████░░░░ 6          │
│                                         │
│ ... (22 more variables)                 │
├─────────────────────────────────────────┤
│ OVERALL SCORE: 7.3/10                   │
│ MARKET POSITION: Above Average          │
│                                         │
│ [Generate Landscape PDF Report]         │
└─────────────────────────────────────────┘
```

**Output: Competitive Landscape Visualization**
- Scatter plot: Price vs Quality
- Radar chart: 25-variable fingerprint
- Ranking table: Subject vs 5 comparables
- Persona-specific insights (Tech Tenant, Logistics, Manufacturing)

---

### 3.4 Lease Processing Module

#### 3.4.1 Lease Abstraction Tool

**Layout: Upload + Side-by-Side Viewer**

**Upload Zone (Top)**
```
┌─────────────────────────────────────────┐
│ 📄 LEASE ABSTRACTION                    │
├─────────────────────────────────────────┤
│ Drag & Drop PDF/DOCX or [Browse Files]  │
│                                         │
│ Property Type: (•) Industrial          │
│                ( ) Office              │
│                                         │
│ [Run Abstraction] [Use Template]       │
└─────────────────────────────────────────┘
```

**Results: Split View**
- **Left**: Original PDF with highlighted sections
- **Right**: 24-Section Abstract (Editable)

**24 Sections:**
1. Basic Info (Address, Landlord, Tenant, Term)
2. Premises (Rentable Area, Use Clause)
3. Rent Schedule (Base Rent, Escalations)
4. Additional Rent (Operating Expenses, Taxes, Utilities)
5. Proportionate Share
6. Security Deposit
7. Tenant Improvements
8. Renewal Options
9. Expansion Options
10. Termination Options
11. Assignment & Subletting
12. Use Restrictions
13. Exclusivity Clauses
14. Parking
15. Signage
16. Insurance Requirements
17. Environmental Obligations
18. Default Provisions
19. Remedies
20. Indemnification
21. SNDA (Subordination, Non-Disturbance, Attornment)
22. Critical Dates
23. Special Provisions (Schedule G)
24. Exhibits/Schedules

**Export Options:**
- PDF (formatted)
- Excel spreadsheet
- JSON (for API integration)
- Add to Portfolio Database

#### 3.4.2 Document Comparison Suite

**4 Comparison Types:**

**A. Compare Amendment**
- Input: Amendment + Original Lease
- Output: Redline showing changes + Impact analysis

**B. Compare Offers**
- Input: Inbound Offer + Your Last Offer
- Output: Movement tracking table (who moved how much on each term)

**C. Compare to Precedent**
- Input: Draft Lease + Your Standard Form
- Output: Deviations report with risk scoring

**D. Lease vs Lease (Portfolio Consistency)**
- Input: Any 2 leases
- Output: Side-by-side comparison across 24 sections

**Comparison View:**
```
┌────────────────────┬────────────────────┐
│ ORIGINAL           │ AMENDED            │
├────────────────────┼────────────────────┤
│ Base Rent: $25/SF  │ Base Rent: $27/SF  │
│ Term: 5 years      │ Term: 7 years      │
│ Free Rent: 2 mos   │ Free Rent: 3 mos   │
│ TI: $20/SF         │ TI: $25/SF         │
└────────────────────┴────────────────────┘

IMPACT ANALYSIS:
✓ NER improved from $23.14 to $24.83 (+7.3%)
⚠️ Term extended requires board approval
⚠️ TI increase adds $50K to capital budget
```

---

### 3.5 Compliance & Legal Module

#### 3.5.1 Assignment Consent Analyzer

**Workflow:**
1. Upload: Current Lease + Assignment Request
2. Analysis:
   - Is assignment permitted?
   - Reasonable withholding grounds?
   - Recapture rights?
   - Financial strength of proposed assignee?
3. Output: Consent recommendation + Draft consent agreement

#### 3.5.2 Default Analysis Tool

**Inputs:**
- Lease document
- Description of default event
- Tenant's proposed cure

**Outputs:**
- Cure period calculation (automatic)
- Available remedies (distress, termination, damages)
- Draft Notice to Cure
- Projected damages if uncured
- Litigation risk assessment

#### 3.5.3 Notice Generator

**Template Library:**
- Notice of Default
- Notice to Cure
- Termination Notice
- Renewal Option Exercise
- Expansion Notice
- Rent Adjustment Notice
- Insurance Non-Compliance
- Environmental Violation

**Smart Features:**
- Auto-fill from lease abstract
- Calculate critical dates
- Track delivery requirements
- Generate certified mail labels

---

### 3.6 Reports Vault

**Features:**
- **Search**: Full-text search across all reports
- **Filters**: By date, property, tenant, report type
- **Tags**: Auto-tag reports by content (e.g., "High Risk", "Board Approval", "Renewal")
- **Export**: Bulk export to ZIP
- **Share**: Generate secure share links
- **Archive**: Auto-archive reports >2 years old

**View Options:**
- List view (sortable table)
- Card view (thumbnail previews)
- Timeline view (chronological)

---

## Phase 4: Enhanced Gemini Prompt

### 4.1 Complete Prompt for Gemini

```markdown
I have a **comprehensive Python-based Institutional Real Estate AI Platform**. The repository contains:

- **10 Financial Calculators** (Effective Rent, Credit Analysis, IFRS 16, Renewal Economics, Rental Variance, Option Valuation, Rollover Analysis, Default Calculator, Relative Valuation, MLS Extractor)
- **25 Slash Commands** across 6 categories (Abstraction, Financial Analysis, Accounting, Comparison, Compliance, Utilities)
- **41+ Specialized Skills** (Commercial leases, assignments, subletting, indemnities, SNDA, negotiations, valuations, appraisals, expropriation, infrastructure)
- **3 AI Personas** with distinct roles: Adam (Fast Analyst), Reggie (Crisis Expert), Dennis (Strategic Advisor)
- **24-Section Lease Abstraction** (Industrial & Office templates with BOMA standards)
- **Document Comparison Tools** (4 types: Amendment, Offers, Precedent, Lease-to-Lease)
- **Compliance Suite** (7 tools: Assignment consent, Default analysis, Environmental, Estoppel, Insurance, Notices, Work letters)

I want you to build a **production-grade Streamlit application** (`app.py`) that serves as the complete UI for this institutional platform.

---

### 1. Repository Structure & Context

```
lease-abstract/
├── Shared_Utils/              # Financial utilities (NPV, IRR, PV, ratios, stats)
├── Eff_Rent_Calculator/       # Effective Rent, NPV, breakeven (Ponzi framework)
├── Credit_Analysis/           # Tenant credit scoring & risk assessment
├── Rental_Variance/           # Rental variance decomposition (rate, area, term)
├── IFRS16_Calculator/         # IFRS 16/ASC 842 lease accounting
├── Renewal_Analysis/          # Renewal vs relocation economics
├── Option_Valuation/          # Real options (Black-Scholes) for lease flexibility
├── Rollover_Analysis/         # Portfolio lease expiry & renewal prioritization
├── Default_Calculator/        # Tenant default damage quantification
├── Relative_Valuation/        # MCDA competitive positioning (25 variables)
├── MLS_Extractor/             # MLS PDF to Excel extraction
├── Sample_Inputs/             # Sample lease documents for testing
├── Templates/                 # Industrial/Office lease templates (24 sections)
├── Reports/                   # Generated abstracts & analysis (timestamped)
└── .claude/
    ├── commands/              # 25 slash commands in 6 categories
    ├── skills/                # 41+ specialized expert skills
    └── agents/                # 3 AI personas (Adam, Reggie, Dennis)
```

---

### 2. UI Requirements - COMPLETE PLATFORM

Build a **multi-page Streamlit app** with professional institutional design:

#### **A. Navigation Structure (Sidebar)**

```
🏠 Dashboard
─────────────────
👥 THE TEAM ROOM
  ├─ Chat with Adam (Analyst)
  ├─ Chat with Reggie (VP)
  └─ Chat with Dennis (Advisor)
─────────────────
📊 FINANCIAL ANALYSIS
  ├─ Effective Rent Calculator
  ├─ Renewal Economics
  ├─ Tenant Credit Analysis
  ├─ Option Valuation
  ├─ Market Comparison
  ├─ Rollover Analysis
  ├─ Rental Variance
  ├─ Relative Valuation (MCDA)
  ├─ MLS Extractor
  └─ Recommendation Memo
─────────────────
📄 LEASE PROCESSING
  ├─ Lease Abstraction (24 sections)
  ├─ Critical Dates Extraction
  ├─ Compare Amendment
  ├─ Compare Offers
  ├─ Compare to Precedent
  └─ Lease vs Lease
─────────────────
⚖️ COMPLIANCE & LEGAL
  ├─ Assignment Consent
  ├─ Default Analysis
  ├─ Environmental Compliance
  ├─ Estoppel Certificate
  ├─ Insurance Audit
  ├─ Notice Generator
  └─ Work Letter Generator
─────────────────
📊 ACCOUNTING
  └─ IFRS 16 Calculator
─────────────────
🗄️ REPORTS VAULT
  ├─ Browse Reports
  ├─ Search Reports
  └─ Export Archive
─────────────────
⚙️ UTILITIES
  ├─ PDF Converter
  └─ Templates Library
```

---

### 3. Specific Page Implementations

#### **3.1 Dashboard Page**

Create a 3-column layout:

**Column 1: Portfolio Metrics** (Use `st.metric`)
- Total GLA (Square Feet)
- Total Annual Rent Revenue (ARR)
- Portfolio Occupancy %
- Weighted Average Lease Term (WALT)
- Leases Expiring (Next 12 Months)
- Defaults Count

**Column 2: Quick Actions** (Large buttons)
- Upload Lease Document
- Ask Reggie a Question
- Run Effective Rent Calculator
- Abstract New Lease

**Column 3: Alerts** (Color-coded cards)
- 🔴 Critical: Default notices due
- 🟡 Warning: Option exercise deadlines
- 🟢 Info: Insurance renewals

#### **3.2 The Team Room (Enhanced Chat)**

**Persona Selector:**
- Use `st.radio` or `st.tabs` to select: Adam | Reggie | Dennis
- Each persona has distinct:
  - Avatar icon
  - System prompt
  - Response style
  - Color theme

**Chat Features:**
- File uploader (PDF/DOCX/Excel) using `st.file_uploader`
- Chat history using `st.chat_message`
- Streaming responses with `st.write_stream`
- Download conversation button
- Clear chat button

**Persona Prompts:**
- **Adam**: "I'm Adam, your Senior Analyst. Fast, diplomatic, quantitative. What can I analyze?"
- **Reggie**: "Reggie Chan, CFA, FRICS. 20+ years institutional experience. Crisis specialist. What's the challenge?"
- **Dennis**: "Dennis. 36 years, multiple cycles. Skip the BS - what do you need to decide?"

#### **3.3 Effective Rent Calculator**

**Layout: Two columns** (`st.columns([1, 1])`)

**Left Column: Input Form** (Use `st.number_input` for all fields)
- Deal Parameters:
  - Base Rent ($/SF/Year)
  - Rentable Area (SF)
  - Lease Term (Months)
- Tenant Incentives:
  - Free Rent (Months)
  - TI Allowance ($/SF)
  - Moving Allowance ($)
  - Leasing Commission (%)
- Landlord Economics:
  - Discount Rate (%)
  - Property Tax ($/SF)
  - OpEx ($/SF)
  - Management Fee (%)

**Right Column: Results** (Display after "Calculate" button)
- Use `st.metric` for:
  - Net Effective Rent ($/SF)
  - Gross Effective Rent ($/SF)
  - NPV (Landlord)
  - IRR (%)
  - Breakeven Rent ($/SF)
- **Plotly Chart 1**: Monthly Cash Flow (Bar chart)
- **Plotly Chart 2**: Sensitivity Heatmap (Base Rent vs TI Allowance)
- **Export button**: Download results as Excel

#### **3.4 Lease Abstraction Tool**

**Layout: Full width**

**Upload Section:**
- Drag & drop file uploader
- Radio buttons: Industrial | Office
- "Run Abstraction" button

**Results Section (after processing):**
- **Two columns** (`st.columns([1, 1])`):
  - Left: Display uploaded PDF using `st.components.v1.iframe` (or link)
  - Right: 24-section abstract in expandable sections using `st.expander`

**24 Sections** (each in its own expander):
1. Basic Info
2. Premises
3. Rent Schedule
4. Additional Rent
5. Proportionate Share
6. Security Deposit
7. Tenant Improvements
8. Renewal Options
9. Expansion Options
10. Termination Options
... (continue for all 24)

**Export buttons:**
- Download PDF
- Download Excel
- Download JSON

#### **3.5 Tenant Credit Analysis**

**Input Form Sections** (Use `st.form` for better UX):
1. **Company Information**:
   - Company Name (text_input)
   - Industry (selectbox)
   - Years Operating (number_input)

2. **Financial Ratios**:
   - DSCR (number_input, help text: "Debt Service Coverage Ratio")
   - Current Ratio (number_input)
   - Debt/EBITDA (number_input)
   - Interest Coverage Ratio (number_input)

3. **Revenue Metrics**:
   - Annual Revenue (number_input)
   - Revenue Growth Rate % (slider, 0-100)
   - Gross Margin % (slider, 0-100)

**Output (after calculation):**
- **Large metric**: Credit Score (0-100) with color coding
  - 80-100: Green (A rating)
  - 60-79: Yellow (B rating)
  - 40-59: Orange (C rating)
  - <40: Red (D rating)
- **Progress bars** for sub-scores:
  - Financial Health (st.progress)
  - Cash Flow Coverage
  - Revenue Stability
  - Management Quality
- **Recommendations card**:
  - Security requirements (checkboxes)
  - Suggested guarantee structure

#### **3.6 Relative Valuation (MCDA)**

**The Power Tool: 25 Variables**

**Interface:**
- Use `st.slider` for each variable (0-10 scale)
- **Organized in expandable sections**:
  - Location Variables (5 sliders)
  - Building Variables (5 sliders)
  - Financial Variables (5 sliders)
  - Operational Variables (5 sliders)
  - Market Variables (5 sliders)

**Real-time Scoring** (updates as sliders change):
- Overall Score (st.metric, large)
- Category scores (4 columns with st.metric)

**Visualizations** (Plotly):
1. **Radar Chart**: 25-variable fingerprint
2. **Scatter Plot**: Price vs Quality positioning
3. **Ranking Table**: Subject vs Comparables

**Export:**
- Generate Landscape PDF Report (button)
- Download data as Excel

#### **3.7 Document Comparison Tools**

**4 Sub-pages** (use st.tabs):
- Tab 1: Compare Amendment
- Tab 2: Compare Offers
- Tab 3: Compare to Precedent
- Tab 4: Lease vs Lease

**Each tab has:**
- Two file uploaders (Document A, Document B)
- "Run Comparison" button
- **Results in 2-column layout**:
  - Left: Document A excerpts
  - Right: Document B excerpts
- Highlighted differences (use colored st.markdown)
- **Impact Analysis card** (bullet points)

#### **3.8 Compliance Tools (7 Tools)**

**Assignment Consent Page:**
- Upload current lease
- Upload assignment request
- "Analyze" button
- **Output:**
  - ✅ / ❌ Assignment permitted?
  - List of concerns (if any)
  - Recommended conditions
  - Draft consent letter (in st.text_area, editable)

**Default Analysis Page:**
- Upload lease
- Text area: Describe default event
- "Analyze" button
- **Output:**
  - Cure period (calculated, with countdown)
  - Available remedies (checkboxes)
  - Draft Notice to Cure (downloadable)
  - Projected damages table

**Notice Generator Page:**
- Dropdown: Select notice type (8 types)
- Form: Auto-filled from lease (editable)
- "Generate Notice" button
- Output: Formatted letter (downloadable Word/PDF)

**Other tools** (Estoppel, Insurance Audit, Environmental, Work Letter):
- Similar pattern: Upload → Form → Generate → Download

#### **3.9 IFRS 16 Calculator**

**Input Form:**
- Upload lease PDF or enter manually:
  - Lease payments (table input or CSV upload)
  - Discount rate (%)
  - Lease term (months)
- "Calculate" button

**Output:**
- **Metrics:**
  - Lease Liability ($)
  - Right-of-Use Asset ($)
- **Tables:**
  - Amortization schedule (DataFrame displayed with st.dataframe)
  - Journal entries
- **Chart:**
  - Liability vs ROU Asset over time (Plotly line chart)
- **Export:**
  - Download Excel workbook with all schedules

#### **3.10 Reports Vault**

**Search & Filter Section:**
- Text input: Search reports (full-text)
- Date range picker (st.date_input)
- Multi-select: Filter by tags (e.g., "Renewal", "High Risk", "Board Approval")

**Display Options:**
- Radio: List View | Card View | Timeline View

**List View** (default):
- DataFrame with columns:
  - Timestamp
  - Report Type
  - Property/Tenant
  - Tags
  - Actions (View, Download, Delete buttons)
- Sortable by clicking columns

**Card View:**
- Grid of cards (use st.columns([1,1,1]))
- Each card shows:
  - Thumbnail (if PDF)
  - Title
  - Date
  - Download button

**Selected Report Viewer:**
- When clicked, display report in:
  - st.markdown (if .md file)
  - st.components.v1.iframe (if PDF)
  - st.dataframe (if CSV/Excel)

---

### 4. Styling & Theme

**Page Config:**
```python
st.set_page_config(
    page_title="VP Real Estate Platform",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

**Custom CSS (inject via st.markdown):**
```css
/* Navy & Slate Professional Theme */
:root {
    --primary-navy: #0f172a;
    --gold-accent: #d97706;
    --steel-blue: #3b82f6;
    --sage-green: #059669;
    --background: #f8fafc;
    --card-bg: #ffffff;
}

/* Sidebar styling - use stable data-testid selector */
section[data-testid="stSidebar"] {
    background-color: var(--primary-navy);
}

section[data-testid="stSidebar"] > div {
    background-color: var(--primary-navy);
}

/* Metric cards */
.stMetric {
    background-color: var(--card-bg);
    padding: 1rem;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

/* Buttons */
.stButton button {
    background-color: var(--steel-blue);
    color: white;
    font-weight: 600;
}

/* Headers */
h1, h2, h3 {
    color: var(--primary-navy);
    font-family: 'Inter', sans-serif;
}
```

---

### 5. Code Structure Requirements

**File Organization:**
```
app.py                    # Main entry point (navigation logic)
pages/
├── 01_Dashboard.py       # Home page with metrics
├── 02_Team_Room.py       # Chat interface
├── 03_Effective_Rent.py  # Calculator pages (10 total)
├── ...
├── 13_Lease_Abstract.py  # Processing tools
├── ...
├── 20_Reports_Vault.py   # Reports browser
utils/
├── dummy_functions.py    # Placeholder calculation functions
├── styling.py            # CSS injection functions
├── charts.py             # Plotly chart templates
└── personas.py           # AI persona definitions
```

**Main app.py Structure:**
```python
import streamlit as st

# Page config (Main landing page)
st.set_page_config(
    page_title="VP Real Estate Platform",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS
from utils.styling import inject_custom_css
inject_custom_css()

# This is the main landing page (Dashboard)
st.title("🏢 VP Real Estate Platform")
st.markdown("### Welcome to your Institutional Real Estate Command Center")

# Dashboard content goes here (metrics, quick actions, etc.)
# ... (See Dashboard implementation in Section 3.1)

# NOTE: All other pages are automatically loaded from the pages/ directory
# Streamlit creates navigation automatically based on files in pages/
# Each file in pages/ becomes a separate page in the app
```

**Important: How Streamlit Multi-Page Apps Work**

Streamlit automatically creates navigation from files in the `pages/` directory:
- Files are sorted by filename (use prefixes like `01_`, `02_` to control order)
- Navigation appears in the sidebar automatically
- Each file must have `st.set_page_config()` at the top
- No manual routing needed - Streamlit handles it all
- Example: `pages/01_Dashboard.py` becomes "Dashboard" in the sidebar

**Dummy Functions (for now):**
```python
# utils/dummy_functions.py

import pandas as pd
import numpy as np
import time

def calculate_effective_rent(base_rent, area, term, free_rent, ti_allowance, discount_rate):
    """Placeholder for Effective Rent calculation"""
    time.sleep(1)  # Simulate processing

    # Mock results
    ner = base_rent * 0.9
    ger = base_rent * 0.95
    npv = base_rent * area * term / 12
    irr = discount_rate + 1.5

    return {
        "ner": ner,
        "ger": ger,
        "npv": npv,
        "irr": irr,
        "breakeven": ner * 0.96
    }

def calculate_credit_score(dscr, current_ratio, debt_ebitda, revenue_growth):
    """Placeholder for Credit Analysis"""
    time.sleep(1)

    # Weighted scoring
    score = (dscr * 20) + (current_ratio * 15) + (10 if debt_ebitda < 3 else 5) + (revenue_growth * 0.3)
    score = min(score, 100)

    rating = "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "D"

    return {
        "score": round(score, 1),
        "rating": rating,
        "financial_health": round(score * 0.8, 1),
        "cash_flow": round(dscr * 10, 1),
        "revenue_stability": round(revenue_growth * 0.5, 1)
    }

def run_lease_abstraction(uploaded_file, lease_type):
    """Placeholder for Lease Abstraction"""
    time.sleep(2)

    # Mock 24-section abstract
    abstract = {
        "Basic Info": {
            "Landlord": "ABC Properties Inc.",
            "Tenant": "XYZ Corp.",
            "Property": "123 Industrial Parkway",
            "Commencement": "2025-01-01",
            "Expiry": "2030-12-31"
        },
        "Premises": {
            "Rentable Area": "10,000 SF",
            "Use": "Warehousing and distribution"
        },
        "Rent Schedule": {
            "Year 1-2": "$25.00/SF",
            "Year 3-4": "$26.25/SF",
            "Year 5-6": "$27.50/SF"
        },
        # ... (continue for all 24 sections)
    }

    return abstract

def compare_documents(doc1, doc2, comparison_type):
    """Placeholder for Document Comparison"""
    time.sleep(1.5)

    differences = [
        {"section": "Base Rent", "original": "$25/SF", "amended": "$27/SF", "impact": "+8% rent increase"},
        {"section": "Term", "original": "5 years", "amended": "7 years", "impact": "Extended term requires board approval"},
        {"section": "TI Allowance", "original": "$20/SF", "amended": "$25/SF", "impact": "+$50K capital required"}
    ]

    return differences
```

---

### 6. Visual Enhancements

**Charts (use Plotly for interactivity):**

**Cash Flow Chart Example:**
```python
import plotly.graph_objects as go

def create_cash_flow_chart(monthly_data):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly_data['month'],
        y=monthly_data['cash_flow'],
        name='Monthly Cash Flow',
        marker_color='#3b82f6'
    ))
    fig.update_layout(
        title='Monthly Cash Flow Analysis',
        xaxis_title='Month',
        yaxis_title='Cash Flow ($)',
        hovermode='x'
    )
    return fig
```

**Sensitivity Heatmap Example:**
```python
import plotly.express as px
import numpy as np

def create_sensitivity_heatmap():
    # Generate sensitivity data
    rent_range = np.linspace(20, 35, 10)
    ti_range = np.linspace(15, 35, 10)

    ner_matrix = np.outer(rent_range, 1 - (ti_range / 100))

    fig = px.imshow(
        ner_matrix,
        labels=dict(x="TI Allowance ($/SF)", y="Base Rent ($/SF)", color="NER"),
        x=ti_range,
        y=rent_range,
        color_continuous_scale="RdYlGn"
    )
    fig.update_layout(title="NER Sensitivity Analysis")
    return fig
```

**Radar Chart for MCDA:**
```python
def create_radar_chart(variables, scores):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=variables,
        fill='toself',
        name='Subject Property'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=False,
        title="25-Variable Property Fingerprint"
    )
    return fig
```

---

### 7. Data Handling

**Session State (for persistence across pages):**
```python
# Initialize session state
if 'portfolio_data' not in st.session_state:
    st.session_state.portfolio_data = {
        'total_gla': 2_400_000,
        'arr': 48_200_000,
        'occupancy': 94.2,
        'walt': 4.8,
        'expiries_12mo': 18,
        'defaults': 2
    }

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = {
        'adam': [],
        'reggie': [],
        'dennis': []
    }

if 'recent_reports' not in st.session_state:
    st.session_state.recent_reports = []
```

**File Upload Handling:**
```python
uploaded_file = st.file_uploader("Upload Lease", type=['pdf', 'docx'])

if uploaded_file:
    # Save to temp directory
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp.write(uploaded_file.read())
        file_path = tmp.name

    # Process file
    results = process_lease(file_path)

    # Display results
    st.success(f"Processed: {uploaded_file.name}")
```

---

### 8. Performance & UX

**Loading States:**
```python
with st.spinner('Calculating effective rent...'):
    results = calculate_effective_rent(...)
st.success('Calculation complete!')
```

**Progress Bars for long operations:**
```python
progress_bar = st.progress(0)
for i in range(100):
    time.sleep(0.01)
    progress_bar.progress(i + 1)
st.success('Lease abstraction complete!')
```

**Caching for performance:**
```python
@st.cache_data
def load_portfolio_data():
    # Expensive operation
    return pd.read_csv('portfolio.csv')

@st.cache_resource
def load_ml_model():
    # Load heavy model once
    return joblib.load('credit_model.pkl')
```

---

### 9. Requirements File

**requirements.txt:**
```
streamlit>=1.28.0
plotly>=5.17.0
pandas>=2.1.0
numpy>=1.25.0
openpyxl>=3.1.0
python-docx>=1.0.0
PyPDF2>=3.0.0
markdown>=3.4.0
jinja2>=3.1.0
```

---

### 10. Deliverables

Please provide:

1. **Full `app.py`** (main entry point with navigation)
2. **10+ page files** in `pages/` directory:
   - Dashboard
   - Team Room (Chat)
   - All 10 Financial Analysis tools
   - Lease Abstraction
   - Document Comparison (4 types)
   - 7 Compliance tools
   - IFRS 16 Calculator
   - Reports Vault
3. **utils/ directory** with:
   - dummy_functions.py (all placeholder calculations)
   - styling.py (CSS injection)
   - charts.py (Plotly chart templates)
   - personas.py (AI persona definitions)
4. **requirements.txt**
5. **README.md** with setup instructions

**Goals:**
- Fully functional, clickable UI (even with dummy backend)
- Professional institutional design (Navy & Slate theme)
- All 25+ tools have dedicated pages with proper forms
- Charts and visualizations for all calculators
- File upload/download working
- Navigation structure complete

This should be a production-ready UI that I can immediately run with `streamlit run app.py` and then wire up the actual Python calculators as Phase 2.
```

---

## Phase 5: Implementation Roadmap

### 5.1 Development Phases

**Phase 1: Foundation (Week 1)**
- Feed prompt to Gemini, generate initial codebase
- Set up project structure
- Implement navigation skeleton
- Build Dashboard page
- Test dummy functions

**Phase 2: Core Tools (Week 2-3)**
- Implement all 10 Financial Analysis pages
- Build Lease Abstraction tool
- Create Document Comparison suite
- Wire up dummy data flows

**Phase 3: Compliance & Reports (Week 4)**
- Implement 7 Compliance tools
- Build Reports Vault with search
- Add IFRS 16 Calculator
- Test all workflows end-to-end

**Phase 4: AI Integration (Week 5-6)**
- Integrate Team Room with actual LLM backend
- Connect calculators to real Python modules
- Test file processing pipelines
- Implement proper error handling

**Phase 5: Polish & Deploy (Week 7-8)**
- Performance optimization
- Add keyboard shortcuts
- Implement user authentication
- Deploy to cloud (Streamlit Cloud, AWS, or Azure)
- User acceptance testing

### 5.2 Technical Architecture

**Frontend: Streamlit**
- Multi-page app structure
- Session state management
- Custom CSS theming
- Plotly visualizations

**Backend Options:**
1. **Option A: Direct Python Integration** (Simplest)
   - Import calculator modules directly
   - Run synchronously in Streamlit
   - Good for MVP

2. **Option B: FastAPI Backend** (Scalable)
   - Streamlit frontend calls FastAPI endpoints
   - Async processing with task queues
   - Better for production scale

3. **Option C: Hybrid** (Recommended)
   - Simple calculators: Direct import
   - Complex/slow tools: API endpoints
   - Best of both worlds

**Data Layer:**
- SQLite for development (portfolio data, reports metadata)
- PostgreSQL for production
- S3/Azure Blob for document storage
- Redis for caching

**AI Integration:**
- OpenAI API for persona chat
- LangChain for document processing
- Vector database (Pinecone/Weaviate) for semantic search

### 5.3 Deployment Options

**Option 1: Streamlit Cloud (Fastest)**
- Free tier available
- One-click deploy from GitHub
- Limited resources (1GB RAM, 1 CPU)
- Good for demos/MVP

**Option 2: AWS (Scalable)**
- ECS Fargate for containerized Streamlit
- RDS PostgreSQL for data
- S3 for documents
- CloudFront for CDN
- Cost: ~$200-500/month

**Option 3: Azure (Enterprise)**
- App Service for Streamlit
- Azure SQL Database
- Blob Storage for documents
- Application Insights for monitoring
- Cost: ~$300-600/month

---

## Phase 6: Success Metrics & KPIs

**User Engagement:**
- Daily Active Users (DAU)
- Average session duration
- Tools used per session
- Return rate (weekly)

**Business Impact:**
- Time saved per lease analysis (target: 50% reduction)
- Error rate in manual calculations (target: 80% reduction)
- Deal velocity increase (target: 30% faster closings)
- Portfolio visibility improvement (qualitative)

**Technical Performance:**
- Page load time <2 seconds
- Calculator response time <5 seconds
- Search results <1 second
- 99.9% uptime

---

## Phase 7: Future Enhancements

**V2.0 Features:**
- Mobile responsive design
- Multi-tenant support (white-label for different firms)
- API access for third-party integrations
- Advanced analytics & BI dashboards
- Automated email reports
- Calendar integration for critical dates
- Workflow automation (approval chains)

**V3.0 Features:**
- Predictive analytics (ML for tenant default prediction)
- Market data integration (CoStar, REIS APIs)
- Document OCR with AI extraction
- Voice commands ("Hey Reggie, what's my occupancy?")
- Slack/Teams integration
- Mobile app (iOS/Android)

---

## Conclusion

This expanded UI/UX plan transforms Gemini's basic concept into a **complete institutional real estate platform**. By feeding the enhanced prompt to Gemini, you'll receive production-ready code that covers:

✅ All 25 slash commands with dedicated interfaces
✅ 10 financial calculators with visualizations
✅ 3 AI personas with distinct chat experiences
✅ Complete lease processing & abstraction suite
✅ 7 compliance & legal tools
✅ Reports vault with search & analytics
✅ Professional institutional design (Navy & Slate)
✅ Scalable architecture ready for backend integration

The result: A powerful, professional platform that VP Leasing teams can use immediately, with room to grow into a full enterprise solution.

**Next Step:** Copy the Enhanced Gemini Prompt (Section 4.1) and feed it to Gemini Pro to generate your production codebase.
