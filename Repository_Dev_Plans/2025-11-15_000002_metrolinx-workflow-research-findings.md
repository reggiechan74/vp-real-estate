# Metrolinx Expropriation Workflow: Research Findings

**Research Date:** 2025-11-15
**Focus:** Ontario expropriation process, document templates, FOI-released materials
**Purpose:** Understand workflow to build automated toolkit

---

## Executive Summary

Researched publicly available expropriation documents from Metrolinx, Ontario government forms, and FOI-released materials to understand the property acquisition approval workflow. Identified 8 core document types and extracted the data flow from reference plan → appraisal → approval memo → expropriation registration.

**Key Finding:** The Metrolinx approval memo workflow requires automated extraction of:
- PIN (Property Identification Number) from reference plans
- Legal description from survey documents
- Market value from appraisal reports
- Project details from briefing materials
- Statutory compliance from Expropriations Act forms

---

## The Metrolinx Property Acquisition Workflow

### Phase 1: Planning and Surveying

**Input Documents:**
1. **Project Overview** - Transit project description, corridor requirements, construction timeline
2. **Reference Plan** (R-Plan) - Ontario Land Surveyor survey showing:
   - Property boundaries
   - Parts designation (Part 1, Part 2, etc.)
   - Easement areas to be acquired
   - Existing easements with registration numbers
   - Surveyor's certificate and signature

**Key Data Elements to Extract:**
- **Property Identification Number (PIN)** - 9-digit unique identifier (e.g., 10126-0418 (LT))
  - Format: `[Block Identifier]-[Parcel Identifier]([Registry Type])`
  - Example: `035891086` and `035890964` (Newmarket property)
- **Legal Description** - Written description of land
  - Example: "Part Lot 91 Concession 1 (NK) WYS, designated as Part 1 65R-25710"
- **Municipal Address** - Street address for identification
  - Example: "16780 Yonge Street, Newmarket, Ontario"
- **Parts on Plan** - Reference plan part numbers
  - Example: "Part 1 on Plan 66R-14738" or "Parts 1, 2, and 3 on Plan 55R-42315"
- **Easement Type** - Nature of interest being acquired
  - Permanent easement (transmission line, utility corridor)
  - Temporary easement (construction access, launch shaft)
  - Temporary subsurface easement (tunnel boring, underground works)

### Phase 2: Valuation (Appraisal)

**Input Document:**
3. **Expropriation Appraisal Report** - Prepared by certified appraiser (AACI designation)

**Report Structure (CUSPAP Compliant):**

**Part 1: Introduction**
- Purpose and Intended Use of Report
- Scope of Work
- Date of Valuation
- Property Identification (PIN, legal description, municipal address)
- Property Rights Appraised (fee simple, easement, leasehold)
- Client Identification (Metrolinx, Infrastructure Ontario)

**Part 2: Factual Data**
- Property Description
  - Land area (total and part being taken)
  - Zoning and official plan designation
  - Site improvements (buildings, structures, landscaping)
  - Access and services (road frontage, utilities)
- Market Area Analysis
  - Demographics and economic trends
  - Supply and demand conditions
  - Recent sales activity in area
- Highest and Best Use Analysis
  - As if vacant
  - As improved
  - Impact of partial taking on remainder

**Part 3: Valuation Analysis**

**For Permanent Easements (Fee Simple Basis):**
- Market Value of Entire Property (before taking)
- Market Value of Remainder Property (after taking)
- Severance Damages
- Injurious Affection Damages
- **Total Compensation = Before Value - After Value**

**For Temporary Easements:**
- Market Rent for Similar Land Use
- Term of Easement (construction period)
- Present Value of Rental Stream
- Disturbance Damages

**Valuation Approaches Used:**
1. **Direct Comparison (Sales Comparison Approach)**
   - Comparable sales (minimum 3-5 comps)
   - Adjustments for:
     - Time of sale
     - Location/access
     - Size (larger parcels = lower $/acre)
     - Zoning and highest & best use
     - Services and improvements
   - Adjusted value per acre/SF

2. **Income Approach** (if applicable)
   - Agricultural rent capitalization
   - Commercial lease income
   - Discount rate and capitalization rate

3. **Cost Approach** (for specialty properties)
   - Land value + depreciated building value
   - Replacement cost new
   - Physical, functional, economic depreciation

**Part 4: Reconciliation and Final Value Estimate**
- Weight given to each approach
- Final market value conclusion
- Certification and limiting conditions

**Key Data Elements to Extract:**
- **Market Value (Before)** - Value of entire property
- **Market Value (After)** - Value of remainder after taking
- **Severance Damages** - Loss due to division of property
- **Injurious Affection** - Loss due to proximity/construction impacts
- **Disturbance Damages** - Business losses, relocation costs
- **Total Compensation** - Statutory compensation under Expropriations Act
- **Appraisal Date** - Effective date of valuation
- **Appraiser Name and Designation** - AACI, P.App, CRA

### Phase 3: Statutory Compliance (Expropriations Act)

**Input Documents:**
4. **Form 2 - Notice of Application for Approval to Expropriate**
   - Served on all registered property owners
   - Published in accordance with s. 6(1) of Expropriations Act
   - Identifies land to be expropriated by reference plan and parts

5. **Inquiry Officer Report** (if objections filed)
   - Independent review of expropriation necessity
   - Recommendations on whether approval should be granted
   - Consideration of property owner objections
   - Example: Victor L. Freidin Q.C. report for Eglinton Crosstown (Dec 19, 2012)

**Key Data Elements:**
- **Statutory Authority** - Legal power to expropriate
  - Example: "Public Transportation and Highway Improvement Act, s. 32"
  - Example: "Metrolinx Act, 2006, s. 21"
- **Approving Authority** - Body that grants approval
  - Example: City of Toronto Council (for temporary easements)
  - Example: Lieutenant Governor in Council (for major expropriations)
- **Inquiry Officer Recommendation** - Support or oppose expropriation
- **Objections Filed** - Number and nature of property owner objections

### Phase 4: Internal Approval (Approval Memo / Briefing Note)

**Output Document:**
6. **Approval Memo / Briefing Note** - Executive summary for decision-makers

**Structure (Based on City of Toronto Delegated Approval Form):**

**Section 1: Project Identification**
- Project Name: (e.g., "Eglinton Crosstown LRT")
- Location: (e.g., "1065 and 1071 Eglinton Avenue West")
- Approval Authority: (e.g., "City Council", "Metrolinx Board")
- Date Prepared: [YYYY-MM-DD]

**Section 2: Property Details**
- **Municipal Address:** [Street address]
- **Legal Description:** [Lot, Concession, Part on Plan]
- **Property Identification Number (PIN):** [9-digit PIN]
- **Registered Owner(s):** [Name(s) from title search]
- **Property Type:** [Residential, Commercial, Industrial, Vacant Land, Agricultural]

**Section 3: Interest Being Acquired**
- **Type of Interest:** [Permanent Easement / Temporary Easement / Fee Simple]
- **Area:** [Square meters or hectares]
- **Purpose:** [Brief description of project need]
  - Example: "Temporary subsurface easement for tunnel boring machine launch shaft and crossover track construction"
- **Reference Plan:** [Plan number and parts]
  - Example: "Parts 1 and 2 on Plan 66R-14738"
- **Duration:** [Permanent / Temporary for X months]

**Section 4: Valuation Summary**
| Component | Amount |
|-----------|--------|
| Market Value (Before) | $[X,XXX,XXX] |
| Market Value (After) | $[X,XXX,XXX] |
| Severance Damages | $[XX,XXX] |
| Injurious Affection | $[XX,XXX] |
| Disturbance Damages | $[XX,XXX] |
| **Total Compensation (Statutory Offer)** | **$[X,XXX,XXX]** |

- **Appraisal Date:** [YYYY-MM-DD]
- **Appraiser:** [Name, Designation (AACI)]
- **Appraisal Firm:** [Company name]

**Section 5: Negotiation Status**
- **Offer Made:** [Date and amount]
- **Owner's Counter-Offer:** [Date and amount, if any]
- **Negotiation History:** [Brief summary of discussions]
- **Settlement Recommendation:** [Recommended amount and rationale]
- **Settlement Authority:** [Who has authority to approve this amount]

**Section 6: Project Impact**
- **Project Timeline:** [Critical path impact if not acquired]
- **Construction Start Date:** [Target date]
- **Consequences of Delay:** [Cost, schedule impact]
- **Alternative Options:** [Other routes, design changes, cost comparison]

**Section 7: Statutory Compliance**
- **Statutory Authority:** [Enabling legislation]
- **Form 2 Served:** [Date]
- **Inquiry Officer Report:** [Filed / Not Required]
- **Approval Granted:** [Date and approving authority]
- **Registration Deadline:** [3 months from approval date]

**Section 8: Risk Assessment**
- **Expropriation Hearing Risk:** [Low / Medium / High]
  - Likelihood owner will not settle and will proceed to hearing
  - Potential award range based on comparable hearing awards
  - Legal costs and timeline if hearing proceeds
- **Political Risk:** [Low / Medium / High]
  - Media attention, community opposition, election cycle
- **Title Risk:** [Any title defects, unregistered interests, survey gaps]
- **Environmental Risk:** [Phase I/II ESA, contamination, remediation costs]

**Section 9: Financial Authority**
- **Budget Allocation:** [Project budget line item]
- **Funds Available:** [Yes / No / Subject to approval]
- **Settlement Range:** [Minimum to maximum authorized]
- **Approval Required From:** [Title of decision-maker]

**Section 10: Recommendations**
- [ ] Approve statutory offer of $[X,XXX,XXX]
- [ ] Authorize negotiation up to $[X,XXX,XXX]
- [ ] Proceed to expropriation if settlement not reached by [date]
- [ ] Register expropriation plan by [date] (within 3-month window)

**Section 11: Attachments**
- Appendix A: Reference Plan (Plan XXR-XXXXX)
- Appendix B: Appraisal Report
- Appendix C: Inquiry Officer Report (if applicable)
- Appendix D: Site Map / Aerial Photo
- Appendix E: Title Search (Parcel Register)
- Confidential Attachment: Settlement negotiation details (if commercially sensitive)

**Prepared by:** [Name, Title]
**Reviewed by:** [Name, Title]
**Approved by:** [Name, Title]
**Date:** [YYYY-MM-DD]

### Phase 5: Expropriation and Registration

**Output Documents:**
7. **Form 6 - Certificate of Approval** (endorsed on expropriation plan)
   - Certifies approval by approving authority
   - Sets out interests being taken
   - Must reference Parts on plan clearly

8. **Form 7 - Notice of Expropriation**
   - Served on registered owners within 30 days of plan registration
   - Includes copy of appraisal report
   - Statutory offer of compensation

**Registration Requirements:**
- Expropriation plan must be registered **within 3 months of approval**
- Plan must comply with Ontario Regulation 43/96 (Registry Act) and O. Reg 216/10 (Surveyors Act)
- Plan must show:
  - Title block with "Expropriations Act" and statutory authority
  - Surveyor's certificate and signature
  - Written statement of land and interests expropriated
  - Existing easements with registration numbers
  - Authority signature confirming signing officers

---

## Document Templates Found (FOI / Public Sources)

### Available from Ontario Central Forms Repository:
1. **Form 2 - Notice of Application for Approval to Expropriate** (004-0412e)
2. **Form 6 - Certificate of Approval** (004-0416)
3. **Form 7 - Notice of Expropriation** (004-0409e)
4. **Client Guide: Expropriation Plans** (ontario.ca/land-registration)

### Available from City of Toronto:
5. **Delegated Approval Form** (Union Station example: 2021-074)
   - 6-page structured template
   - Covers property details, valuation, statutory compliance, recommendations
6. **City Solicitor Report Template** (Eglinton Crosstown example: 2013.CC30.4)
   - Report to Council with appendices (reference plan, appraisal, inquiry officer report)

### Available from Federal Government (PSPC):
7. **Valuation Guidelines** (March 2007, Office of the Chief Appraiser)
   - Expropriation appraisal report formats
   - Partial taking report structure
   - Valuation of interests

### Not Publicly Available (Would Need FOI Request):
- Metrolinx internal approval memo template
- Metrolinx board briefing note format
- Infrastructure Ontario approval workflow documents
- Metrolinx settlement negotiation guidelines
- Internal valuation review checklists

---

## Data Extraction Requirements (For Toolkit Automation)

### From Reference Plan (R-Plan):
```json
{
  "reference_plan": {
    "plan_number": "66R-14738",
    "registry_office": "66",
    "surveyor_name": "John Smith, OLS",
    "survey_date": "2024-09-15",
    "parts": [
      {
        "part_number": 1,
        "area_sqm": 2500,
        "description": "Permanent easement for transmission line",
        "dimensions": "50m x 50m"
      },
      {
        "part_number": 2,
        "area_sqm": 1000,
        "description": "Temporary construction easement",
        "dimensions": "25m x 40m"
      }
    ],
    "existing_easements": [
      {
        "registration_number": "AT1234567",
        "type": "Utility easement",
        "retained": true
      }
    ]
  }
}
```

### From Property Title Search:
```json
{
  "property": {
    "pin": "10126-0418",
    "registry_type": "LT",
    "legal_description": "Lot 91, Concession 1 (NK) WYS, Part 1 on Plan 65R-25710",
    "municipal_address": "16780 Yonge Street, Newmarket, ON L3Y 4Z1",
    "registered_owners": [
      {
        "name": "ABC Properties Inc.",
        "ownership_type": "Fee Simple",
        "registration_date": "2015-03-20"
      }
    ],
    "encumbrances": [
      {
        "type": "Mortgage",
        "registration_number": "AT9876543",
        "holder": "TD Canada Trust"
      },
      {
        "type": "Easement",
        "registration_number": "AT1234567",
        "description": "Hydro One utility corridor"
      }
    ]
  }
}
```

### From Appraisal Report:
```json
{
  "appraisal": {
    "property_pin": "10126-0418",
    "appraisal_date": "2024-10-01",
    "appraiser": {
      "name": "Jane Doe",
      "designation": "AACI, P.App",
      "firm": "Suncorp Valuations Ltd."
    },
    "valuation": {
      "market_value_before": 1500000,
      "market_value_after": 1350000,
      "severance_damages": 50000,
      "injurious_affection": 25000,
      "disturbance_damages": 15000,
      "total_compensation": 240000
    },
    "approaches_used": [
      "Direct Comparison",
      "Income Capitalization"
    ],
    "comparable_sales": [
      {
        "address": "123 Main St",
        "sale_date": "2024-05-15",
        "sale_price": 1450000,
        "size_acres": 10.5,
        "price_per_acre": 138095,
        "adjustments": {
          "time": 1.02,
          "location": 0.98,
          "size": 1.05,
          "adjusted_value": 147500
        }
      }
    ],
    "highest_best_use": {
      "before": "Industrial development",
      "after": "Industrial development (reduced developable area)"
    }
  }
}
```

### From Project Overview:
```json
{
  "project": {
    "name": "Eglinton Crosstown LRT",
    "authority": "Metrolinx",
    "statutory_basis": "Metrolinx Act, 2006, s. 21",
    "project_type": "Transit expansion",
    "purpose": "Construction of tunnel boring machine launch shaft and crossover track",
    "construction_start": "2025-03-01",
    "construction_duration_months": 18,
    "critical_path_impact": "6 month delay if not acquired by 2025-01-01",
    "budget_allocation": "Property Acquisition - Capital Project #2024-LRT-EC-045"
  }
}
```

---

## Automated Workflow Design

### Input: User provides 3-4 documents
1. Reference Plan (PDF from surveyor)
2. Appraisal Report (PDF from appraiser)
3. Title Search (PDF or XML from Teranet OnLand)
4. Project Overview (internal brief or Excel with project details)

### Processing: Extract structured data
```python
# Pseudo-code workflow
def generate_approval_memo(reference_plan_pdf, appraisal_pdf, title_search_pdf, project_data):
    # Step 1: Extract PIN and legal description from title search
    property_data = extract_property_identifiers(title_search_pdf)
    pin = property_data['pin']
    legal_description = property_data['legal_description']
    owners = property_data['registered_owners']

    # Step 2: Extract parts and areas from reference plan
    plan_data = extract_reference_plan(reference_plan_pdf)
    parts = plan_data['parts']
    total_area = sum([part['area_sqm'] for part in parts])

    # Step 3: Extract valuation from appraisal
    appraisal_data = extract_appraisal_values(appraisal_pdf)
    compensation = appraisal_data['total_compensation']
    breakdown = appraisal_data['valuation']

    # Step 4: Combine project details
    project = project_data

    # Step 5: Generate approval memo
    memo = generate_memo_template(
        property=property_data,
        plan=plan_data,
        appraisal=appraisal_data,
        project=project
    )

    return memo
```

### Output: Approval Memo (Markdown + PDF)
- Auto-populated from extracted data
- Structured sections (10 sections as outlined above)
- Appendices attached (reference plan, appraisal, title search)
- Ready for executive review and signature

### Slash Command:
```bash
/approval-memo <reference-plan.pdf> <appraisal.pdf> <title-search.pdf> --project=<project.json>
```

**Result:** Approval memo generated in 30 seconds vs. 2 hours manual preparation

---

## Key Insights for Toolkit Development

### 1. **PIN Extraction is Critical**
- 9-digit unique identifier (e.g., `10126-0418`)
- Appears in title search, appraisal, and reference plan
- Must be extracted accurately for property matching

### 2. **Legal Description Varies by Registry System**
- **Metes and Bounds** (older): "Starting at the northeast corner of Lot 91..."
- **Reference Plan** (modern): "Part 1 on Plan 66R-14738"
- Both may coexist; reference plan is preferred for clarity

### 3. **Valuation Has Multiple Components**
- Not just "market value" - must break down:
  - Market value before
  - Market value after
  - Severance
  - Injurious affection
  - Disturbance
- Toolkit must extract each component separately

### 4. **Approval Memo Requires Cross-Document Data Synthesis**
- PIN from title search
- Legal description from title or reference plan
- Parts from reference plan
- Valuation from appraisal
- Project details from internal brief
- **Challenge:** No single document contains everything

### 5. **Statutory Compliance is Non-Negotiable**
- 3-month registration deadline from approval date
- Form 2, 6, 7 must be served/registered in specific sequence
- Toolkit should flag deadlines and compliance requirements

### 6. **Appraisal Standards are Well-Defined**
- CUSPAP (Canadian Uniform Standards of Professional Appraisal Practice)
- AIC forms (Appraisal Institute of Canada)
- Federal guidelines (PSPC Valuation Guidelines)
- **Opportunity:** Standardized structure makes extraction easier

---

## Next Steps for Toolkit Implementation

### Phase 1 (Immediate - Dec 2025):
1. **Build PDF extraction pipelines** for:
   - Title search (Teranet OnLand format)
   - Reference plan (surveyor PDFs)
   - Appraisal report (CUSPAP format)
2. **Create JSON schemas** for extracted data
3. **Develop approval memo template** (Markdown + PDF generation)
4. **Test with sample documents** (need to acquire via FOI or create synthetic examples)

### Phase 2 (Q1 2026):
1. **Implement `/approval-memo` command**
2. **Build `/easement-valuation` calculator** (percentage of fee, before/after)
3. **Create `expropriation-expert` skill** (statutory compliance advisor)
4. **Add deadline tracking** (3-month registration window)

### Phase 3 (Q2 2026):
1. **API integration with Teranet OnLand** (automated title searches)
2. **GeoWarehouse integration** (property mapping and zoning)
3. **Workflow automation** (track acquisitions from offer → settlement → registration)

---

## FOI Request Recommendations

To obtain actual Metrolinx templates and workflow documents, submit FOI requests for:

1. **Internal approval memo templates** used for property acquisitions (2020-2024)
2. **Board briefing note format** for expropriation approvals
3. **Settlement negotiation guidelines** and authority limits
4. **Appraisal review checklist** used by Metrolinx staff
5. **Expropriation timeline tracking tools** (Excel or project management tools)

**Send to:** FOI@metrolinx.com
**Fee:** $5.00 per request
**Response time:** 30 days

---

## Comparable Jurisdictions

Consider researching workflows from:
- **Hydro One Networks** - Transmission line easement acquisitions
- **Enbridge Gas** - Pipeline right-of-way acquisitions
- **Ministry of Transportation (MTO)** - Highway widening expropriations
- **Infrastructure Ontario** - Bundled P3 project property acquisitions

**Rationale:** Similar workflows, may have public templates or FOI-released materials

---

*Research compiled: 2025-11-15*
*Next review: After FOI responses received*
*Status: Ready to begin Phase 1 implementation*
