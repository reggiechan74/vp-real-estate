# Work Letter Generator

Generate comprehensive work letter from Tenant Improvement (TI) provisions in lease documents.

## Purpose

Extract landlord and tenant work obligations from lease schedules, create construction timeline with milestones, define approval processes, and generate formal work letter documenting responsibilities and cost allocation.

## Usage

```bash
/work-letter path/to/lease.pdf
/work-letter path/to/lease.docx path/to/schedule-c.pdf
/work-letter path/to/lease.pdf --include-budget path/to/ti-budget.xlsx
```

## Input

- **Required**: Lease document (PDF or DOCX)
- **Optional**: Separate Schedule C (Landlord's and Tenant's Work)
- **Optional**: TI budget or cost estimate spreadsheet
- **Optional**: Timeline constraints or target dates

## Output

- Formal work letter document in `Reports/YYYY-MM-DD_HHMMSS_[tenant]_work_letter.md`
- Construction timeline with milestones
- Approval process flowchart
- Cost allocation summary
- Responsibility matrix (landlord vs. tenant)

---

## Workflow

### Step 1: Parse Input Arguments

```bash
# Parse command arguments
LEASE_PATH="$1"
SCHEDULE_C_PATH="${2:-}"
TI_BUDGET_PATH="${3:-}"

# Validate required file
if [ ! -f "$LEASE_PATH" ]; then
    echo "Error: Lease document not found: $LEASE_PATH"
    exit 1
fi

echo "Analyzing lease document: $LEASE_PATH"
[ -n "$SCHEDULE_C_PATH" ] && echo "Schedule C document: $SCHEDULE_C_PATH"
[ -n "$TI_BUDGET_PATH" ] && echo "TI budget: $TI_BUDGET_PATH"
```

### Step 2: Load and Analyze Lease Documents

Load the lease document and any supplementary files using the Read tool.

**Primary focus areas:**

1. **Schedule C: Landlord's and Tenant's Work**
   - Landlord's base building work
   - Tenant improvement allowance (TIA)
   - Tenant's additional work
   - Work completion standards

2. **Construction Timeline Provisions**
   - Lease commencement date
   - Substantial completion definition
   - Early occupancy provisions
   - Delay penalties/rent abatement

3. **Approval Process**
   - Plan submission requirements
   - Approval timelines
   - Change order procedures
   - Final inspection and acceptance

4. **Cost Allocation**
   - TI allowance amount ($ per sf or lump sum)
   - Landlord-funded work
   - Tenant-funded work
   - Cost overrun responsibility

5. **Permits and Compliance**
   - Building permit responsibility
   - Code compliance requirements
   - Certificate of occupancy

**Extract key information:**
- Parties (landlord, tenant, contractor names)
- Premises description and area
- TI allowance amount and terms
- Work categories and responsibilities
- Timeline milestones and deadlines
- Approval authorities and processes
- Cost allocation rules
- Insurance and bonding requirements

### Step 3: Extract Landlord's Work

**Identify landlord's obligations:**

**Base Building Work** (typically before tenant occupancy):
- Shell and core construction
- HVAC systems (up to demising walls)
- Electrical service (to panel)
- Plumbing (to premises)
- Fire protection systems
- Common area improvements
- Building standard finishes

**Landlord-Funded TI Work**:
- Items covered by TI allowance
- Allowable cost categories
- Non-allowable costs (often: moving, FF&E, IT)
- Payment process and timing

**Example extraction format:**
```markdown
### Landlord's Work

#### Base Building (Pre-Delivery)
- [ ] HVAC system to demising walls (RTU capacity: X tons)
- [ ] Electrical service to tenant panel (400A, 120/208V)
- [ ] Plumbing rough-in to premises boundary
- [ ] Fire sprinkler system (NFPA 13)
- [ ] Demising walls to deck (unpainted drywall)
- [ ] Concrete floor slab (level, sealed)

#### Tenant Improvement Allowance
- **Amount**: $XX.XX per rentable SF ($XXX,XXX total)
- **Allowable Costs**:
  - Architectural and engineering fees
  - Permit fees and charges
  - Construction hard costs
  - Project management fees (up to X%)
- **Non-Allowable Costs**:
  - Furniture, fixtures, and equipment (FF&E)
  - Moving and relocation costs
  - IT and telecommunications equipment
  - Security systems and equipment

#### Landlord Responsibilities
- Obtain building permits
- Coordinate base building work
- Review and approve tenant plans
- Manage TI allowance disbursement
- Final inspection and acceptance
```

### Step 4: Extract Tenant's Work

**Identify tenant's obligations:**

**Tenant-Designed Work**:
- Space planning and design
- Working drawings preparation
- Engineer stamped drawings
- Interior finishes selection

**Tenant Construction Work**:
- Interior partitions and doors
- Floor and wall finishes
- Ceilings and lighting
- HVAC distribution
- Electrical outlets and data
- Plumbing fixtures
- Special systems (security, AV, kitchen)

**Tenant-Funded Work** (beyond TI allowance):
- Upgrades beyond building standard
- Additional HVAC capacity
- Supplemental electrical service
- Specialized flooring/finishes
- Custom millwork/cabinetry

**Example extraction format:**
```markdown
### Tenant's Work

#### Design Obligations
- [ ] Engage architect/space planner
- [ ] Prepare space plan for landlord approval
- [ ] Prepare working drawings and specifications
- [ ] Obtain engineer stamps (structural, MEP)
- [ ] Submit drawings to landlord (by: DATE)

#### Construction Scope
- [ ] Interior demising walls and partitions
- [ ] Interior doors and hardware
- [ ] Floor coverings (carpet, tile, etc.)
- [ ] Wall finishes (paint, wallcovering)
- [ ] Ceiling grid and tiles
- [ ] Lighting fixtures
- [ ] HVAC diffusers and controls
- [ ] Electrical outlets and switches
- [ ] Data/telecom cabling
- [ ] Plumbing fixtures
- [ ] Kitchen/break room equipment
- [ ] Security system
- [ ] Signage (interior and exterior)

#### Tenant-Funded Items
- All costs exceeding TI allowance
- FF&E (furniture, fixtures, equipment)
- Moving and relocation expenses
- IT equipment and cabling
- Cost overruns due to tenant changes
```

### Step 5: Generate Construction Timeline

Create a comprehensive timeline with milestones and dependencies.

**Key milestones to identify:**

1. **Pre-Construction Phase**
   - Lease execution date
   - Tenant hires architect/designer
   - Space plan submission
   - Space plan approval
   - Working drawings submission
   - Working drawings approval
   - Permit application submission

2. **Construction Phase**
   - Building permit issuance
   - Construction commencement
   - Rough-in inspections
   - MEP rough-in complete
   - Drywall installation
   - Finishes installation
   - Punch list inspection

3. **Completion Phase**
   - Substantial completion
   - Final inspection
   - Certificate of occupancy
   - Tenant acceptance
   - Lease commencement

**Timeline format:**
```markdown
## Construction Timeline

### Phase 1: Design and Permitting (Weeks 1-8)

| Week | Milestone | Party | Deliverable | Due Date |
|------|-----------|-------|-------------|----------|
| 1 | Lease Execution | Both | Signed lease | MM/DD/YYYY |
| 2 | Architect Engaged | Tenant | Design contract | +2 weeks |
| 4 | Space Plan Submitted | Tenant | Space plan drawings | +4 weeks |
| 5 | Space Plan Approved | Landlord | Written approval | +1 week |
| 8 | Working Drawings Submitted | Tenant | Construction docs | +3 weeks |
| 10 | Drawings Approved | Landlord | Written approval | +2 weeks |
| 12 | Permit Application | Landlord | Permit submission | +2 weeks |

### Phase 2: Construction (Weeks 13-24)

| Week | Milestone | Party | Deliverable | Due Date |
|------|-----------|-------|-------------|----------|
| 13 | Building Permit Issued | Authority | Approved permit | +1 week |
| 14 | Construction Start | Contractor | Notice to proceed | +1 week |
| 16 | Rough-In Complete | Contractor | MEP rough-in | +2 weeks |
| 18 | Drywall Complete | Contractor | Framing inspection | +2 weeks |
| 20 | Finishes 50% | Contractor | Progress inspection | +2 weeks |
| 22 | Punch List Inspection | Landlord | Punch list | +2 weeks |
| 24 | Substantial Completion | Contractor | Final inspection | +2 weeks |

### Phase 3: Closeout (Weeks 25-26)

| Week | Milestone | Party | Deliverable | Due Date |
|------|-----------|-------|-------------|----------|
| 25 | Punch List Complete | Contractor | Final sign-off | +1 week |
| 26 | Certificate of Occupancy | Authority | CO issued | +1 week |
| 26 | Tenant Acceptance | Tenant | Written acceptance | Same day |
| 26 | Lease Commencement | Both | Rent begins | MM/DD/YYYY |

**Critical Path Items:**
- Working drawings approval (potential 2-4 week delay if revisions needed)
- Building permit issuance (variable timing, plan 2-4 weeks)
- Long-lead items (HVAC equipment, custom millwork, special finishes)

**Float/Buffer:**
- Design phase: 2 weeks recommended
- Permit phase: 2 weeks recommended
- Construction phase: 1 week per major trade
```

### Step 6: Define Approval Process

Document the approval workflow for plans, changes, and costs.

**Plan Approval Process:**
```markdown
## Approval Process

### 1. Space Plan Approval

**Submission Requirements:**
- Scale drawings (1/4" = 1'-0")
- Room labels and dimensions
- Door schedule
- Furniture layout (conceptual)
- Finish schedule (conceptual)

**Review Timeline:**
- Landlord review: 5 business days
- One round of revisions included
- Additional revisions: 3 business days each

**Approval Criteria:**
- Compliance with building code
- No adverse impact on building systems
- Consistent with lease use provisions
- No structural modifications without engineer approval

### 2. Working Drawings Approval

**Submission Requirements:**
- Architectural plans (full construction set)
- Structural engineering (if modifications)
- Mechanical, electrical, plumbing (MEP) plans
- Fire protection plan
- Engineer stamps/seals (all disciplines)
- Specification manual
- Cost estimate

**Review Timeline:**
- Landlord review: 10 business days
- One round of revisions included
- Additional revisions: 5 business days each

**Approval Criteria:**
- Code compliance (IBC, local amendments)
- Building system capacity adequate
- Landlord consent for all penetrations
- Sprinkler system modifications approved
- HVAC load calculations verified
- Electrical load within capacity
- No hazardous materials

### 3. Change Order Process

**When Required:**
- Any deviation from approved drawings
- Additional work beyond original scope
- Material or finish substitutions
- Cost increases exceeding $X,XXX

**Submission Requirements:**
- Written change order request
- Revised drawings (if applicable)
- Cost impact statement (+ or -)
- Schedule impact analysis

**Review Timeline:**
- Emergency changes: 1 business day
- Non-emergency changes: 3 business days
- Landlord approval required for:
  - Structural changes
  - Building system impacts
  - Cost increases exceeding TI allowance

**Cost Allocation Rules:**
- Tenant-requested changes: Tenant pays 100%
- Error/omission corrections: Per contract terms
- Unforeseen conditions: Per lease provisions
- Code compliance upgrades: Landlord pays (if not tenant-caused)
```

### Step 7: Document Cost Allocation

Create clear allocation of costs between landlord and tenant.

**Cost allocation matrix:**
```markdown
## Cost Allocation

### TI Allowance Summary

**Total TI Allowance**: $XX.XX per rentable SF
**Premises Area**: X,XXX rentable SF
**Total Allowance**: $XXX,XXX

**Disbursement Terms:**
- Progress payments tied to construction milestones
- Lien waivers required for all payments
- Final 10% withheld until substantial completion
- Payment within 30 days of invoice (with documentation)

### Allowable vs. Non-Allowable Costs

| Cost Category | Allowable? | Paid By | Notes |
|---------------|------------|---------|-------|
| **Design & Engineering** |
| Architectural fees | Yes | TI Allowance | Up to X% of hard costs |
| MEP engineering | Yes | TI Allowance | Included in arch fees or separate |
| Structural engineering | Yes | TI Allowance | If required for tenant work |
| Space planning | Yes | TI Allowance | Initial design only |
| **Permits & Fees** |
| Building permit | Yes | TI Allowance | Landlord obtains |
| Plan check fees | Yes | TI Allowance | Municipality charges |
| Impact fees | No | Tenant | If triggered by tenant use |
| **Hard Costs** |
| General contractor | Yes | TI Allowance | Competitive bid required |
| Demolition | Yes | TI Allowance | Of existing improvements |
| Framing & drywall | Yes | TI Allowance | Building standard |
| Electrical | Yes | TI Allowance | Standard outlets/switches |
| HVAC distribution | Yes | TI Allowance | Diffusers, controls |
| Plumbing | Yes | TI Allowance | Standard fixtures |
| Painting | Yes | TI Allowance | One color per room |
| Flooring | Partial | TI Allowance | Carpet up to $X/sy, tile up to $X/sf |
| Ceilings | Yes | TI Allowance | Standard 2x2 grid |
| Lighting | Yes | TI Allowance | Building standard fixtures |
| **Specialty Items** |
| Custom millwork | No | Tenant | Unless building standard |
| Kitchen equipment | No | Tenant | Appliances, cabinets beyond std |
| Security system | No | Tenant | Card access, cameras, alarm |
| AV equipment | No | Tenant | All AV and presentation systems |
| IT cabling | Partial | TI Allowance | Data drops up to X per 1,000 SF |
| **Soft Costs** |
| Project management | Yes | TI Allowance | Up to X% of hard costs |
| Construction insurance | Yes | TI Allowance | Builder's risk |
| Testing & inspection | Yes | TI Allowance | Required by code |
| **Non-Allowable** |
| Furniture | No | Tenant | All furniture, fixtures, equipment |
| Window treatments | No | Tenant | Blinds, shades, curtains |
| Moving expenses | No | Tenant | All relocation costs |
| Telecommunications | No | Tenant | Phone system, internet |
| Signage (exterior) | No | Tenant | Per building standards |

### Cost Overrun Responsibility

**Tenant Responsible For:**
- All costs exceeding TI allowance
- Costs due to tenant-requested changes
- Costs due to tenant delays
- Upgrades beyond building standard
- Premium for accelerated schedule

**Landlord Responsible For:**
- Base building defects/deficiencies
- Errors in landlord-provided info
- Delays due to landlord approval process (beyond agreed timelines)
- Code compliance changes (if not tenant-caused)
```

### Step 8: Generate Work Letter Document

Create comprehensive work letter document with Eastern Time timestamp.

**Report filename**: `Reports/YYYY-MM-DD_HHMMSS_[tenant_name]_work_letter.md`

Use bash to generate timestamp:
```bash
TZ='America/New_York' date '+%Y-%m-%d_%H%M%S'
```

**Work letter structure:**
```markdown
# WORK LETTER

**Property**: [Address]
**Landlord**: [Landlord Name]
**Tenant**: [Tenant Name]
**Premises**: Suite [Number], [Area] rentable SF
**Date**: [Generated Date]

---

## 1. DEFINITIONS

**Building Standard**: The standard of materials and finishes as described in Exhibit [X] to the Lease.

**Substantial Completion**: The Premises are substantially complete when (a) the Tenant Improvements have been constructed in accordance with the approved Working Drawings, (b) a certificate of occupancy has been issued, (c) all building systems are operational, and (d) only minor punch list items remain.

**TI Allowance**: The tenant improvement allowance provided by Landlord in the amount of $[XX.XX] per rentable square foot, totaling $[XXX,XXX].

**Working Drawings**: The final architectural and engineering construction documents for the Tenant Improvements, approved by Landlord and stamped by licensed professionals.

---

## 2. SCOPE OF WORK

### 2.1 Landlord's Base Building Work

Landlord shall deliver the Premises with the following base building improvements:

[EXTRACTED LANDLORD WORK LIST]

**Target Delivery Date**: [Date]

### 2.2 Tenant Improvement Allowance

Landlord shall provide Tenant with a tenant improvement allowance of:
- **Rate**: $[XX.XX] per rentable square foot
- **Total**: $[XXX,XXX] ([Area] SF × $[XX.XX]/SF)

**Allowable Costs**: [List from extraction]

**Non-Allowable Costs**: [List from extraction]

**Disbursement**: Progress payments upon submission of invoices, lien waivers, and evidence of work completion. Final 10% withheld until substantial completion.

### 2.3 Tenant's Work

Tenant shall perform the following work at Tenant's expense:

[EXTRACTED TENANT WORK LIST]

**Tenant-Funded Costs**: All costs exceeding the TI Allowance.

---

## 3. DESIGN AND APPROVAL PROCESS

### 3.1 Space Plan Phase

**Tenant Obligations**:
- Engage licensed architect/designer
- Prepare space plan showing layout, rooms, doors, finishes
- Submit space plan to Landlord by [Date]

**Landlord Review**:
- Review period: 5 business days
- Approval based on: code compliance, building system capacity, lease use compliance
- One round of revisions included

**Deliverables**: Approved space plan stamped "Approved by Landlord"

### 3.2 Working Drawings Phase

**Tenant Obligations**:
- Prepare full construction documents (architectural, structural, MEP)
- Obtain engineer stamps/seals from licensed professionals
- Include specifications, finish schedule, door/hardware schedule
- Submit working drawings to Landlord by [Date]

**Landlord Review**:
- Review period: 10 business days
- Approval based on: code compliance, building system impacts, structural integrity
- One round of revisions included

**Deliverables**: Approved working drawings stamped "Approved for Construction"

### 3.3 Permitting

**Landlord Responsibilities**:
- Submit permit application to building department
- Pay permit fees (from TI Allowance)
- Coordinate with building officials
- Obtain building permit

**Timeline**: Permit issuance within [X] weeks of submission (estimate)

### 3.4 Change Orders

**Process**:
1. Tenant or Contractor identifies required change
2. Submit written change order with cost and schedule impact
3. Landlord review: 3 business days (1 day for emergencies)
4. Landlord approval required for structural, building system, or cost impacts
5. Approved change orders incorporated into project

**Cost Allocation**: Tenant-requested changes paid by Tenant. Error corrections per contract terms.

---

## 4. CONSTRUCTION TIMELINE

[INSERT DETAILED TIMELINE FROM STEP 5]

**Key Dates**:
- Lease Execution: [Date]
- Space Plan Approval Target: [Date]
- Working Drawings Approval Target: [Date]
- Building Permit Target: [Date]
- Construction Start Target: [Date]
- Substantial Completion Target: [Date]
- Lease Commencement Date: [Date]

**Critical Path**: [List critical path items]

---

## 5. CONSTRUCTION STANDARDS

### 5.1 General Contractor

**Selection**: [Landlord-selected / Tenant-selected from approved list / Competitive bid]

**Requirements**:
- Licensed general contractor in [State]
- General liability insurance: $[X]M
- Workers compensation insurance: Statutory limits
- Payment and performance bonds: [Required/Not required]

### 5.2 Construction Requirements

**Working Hours**: [Days/hours, typically M-F 7am-6pm, Sat 8am-5pm]

**Site Conditions**:
- Keep premises clean and orderly
- Daily trash removal
- Dust containment (occupied building)
- Noise restrictions (occupied building)
- Protect adjacent spaces and common areas

**Safety**:
- OSHA compliance required
- Safety meetings as required
- Incident reporting within 24 hours
- No smoking on premises

**Coordination**:
- Weekly construction meetings
- 48-hour notice for inspections
- Coordinate with building management for:
  - Elevator use
  - Loading dock access
  - Utility shutdowns
  - After-hours access

### 5.3 Quality Standards

**Materials**: New, first quality, specified brands or approved equals

**Workmanship**: Performed by skilled tradespersons in accordance with industry standards

**Code Compliance**: All work per current building code, ADA, energy code, fire code

**Inspections**: Required inspections by building department and Landlord's representative

---

## 6. SUBSTANTIAL COMPLETION

### 6.1 Requirements

The Premises shall be deemed substantially complete when:
1. All work per approved Working Drawings is complete (except minor punch list)
2. Certificate of occupancy issued by building department
3. All building systems operational (HVAC, electrical, plumbing, fire/life safety)
4. Premises are clean and ready for tenant occupancy
5. Final lien waivers provided by all contractors and suppliers

### 6.2 Inspection Process

**Substantial Completion Inspection**:
- Landlord and Tenant conduct joint inspection
- Punch list items identified (minor items only)
- Landlord issues substantial completion certificate

**Punch List Completion**:
- Contractor completes punch list items within [X] days
- Final inspection and acceptance

**Certificate of Occupancy**:
- Landlord obtains CO from building department
- Copy provided to Tenant

### 6.3 Tenant Acceptance

Tenant shall accept the Premises upon substantial completion. Acceptance does not waive:
- Completion of punch list items
- Latent defects discovered within [X] months
- Warranty obligations

---

## 7. PAYMENT PROCEDURES

### 7.1 Draw Schedule

**Progress Payments**: Monthly or upon completion of milestones:
- 25% upon rough-in inspection passed
- 50% upon drywall/framing complete
- 75% upon finishes substantially complete
- 90% upon substantial completion
- 10% final payment upon completion of punch list

### 7.2 Payment Documentation

Each draw request must include:
- AIA G702/G703 Application and Certificate for Payment (or equivalent)
- Detailed invoices from all contractors and suppliers
- Unconditional lien waivers for all prior payments
- Conditional lien waivers for current payment
- Photos documenting work progress
- Proof of insurance (if not already on file)

### 7.3 Payment Timing

Landlord shall review draw requests and pay within [30] days of receipt of complete documentation.

### 7.4 Cost Overruns

**Tenant Responsibility**: Tenant shall pay all costs exceeding the TI Allowance:
- Pay directly to contractors, or
- Reimburse Landlord within [X] days of invoice

**Landlord Responsibility**: Landlord shall pay costs due to:
- Base building defects
- Landlord-caused delays (beyond agreed review periods)
- Changes required by code (if not tenant-caused)

---

## 8. INSURANCE AND LIABILITY

### 8.1 During Construction

**Builder's Risk Insurance**: [Landlord/Tenant] shall maintain builder's risk insurance covering all work in progress, materials, and improvements.

**General Liability**: Contractor shall maintain commercial general liability insurance of not less than $[X]M per occurrence.

**Workers Compensation**: Contractor shall maintain workers compensation insurance per statutory requirements.

**Additional Insured**: Landlord and [Property Manager] shall be named as additional insureds on all policies.

### 8.2 Warranty

**Contractor Warranty**: One year warranty on all labor and materials from substantial completion.

**Extended Warranties**: Manufacturer warranties for equipment (HVAC, etc.) assigned to Tenant.

**Latent Defects**: Tenant may report latent defects discovered within [X] months of substantial completion.

---

## 9. DEFAULT AND REMEDIES

### 9.1 Tenant Default

Tenant shall be in default if:
- Failure to submit space plan or working drawings within agreed timelines
- Failure to approve contractors or materials within reasonable time
- Failure to pay cost overruns when due
- Interference with construction progress

**Landlord Remedies**:
- Complete work and charge Tenant
- Delay lease commencement (with rent obligation beginning at original date)
- Pursue remedies under Lease

### 9.2 Landlord Default

Landlord shall be in default if:
- Failure to approve submittals within agreed timelines (without cause)
- Failure to obtain building permit (after reasonable efforts)
- Failure to disburse TI Allowance per approved draws

**Tenant Remedies**:
- Delay lease commencement until substantial completion (without early rent obligation)
- Complete work and offset against TI Allowance
- Other remedies under Lease

---

## 10. GENERAL PROVISIONS

### 10.1 Incorporation into Lease

This Work Letter is incorporated into and made part of the Lease. In case of conflict, this Work Letter controls over the Lease for construction matters.

### 10.2 Amendments

Amendments to this Work Letter must be in writing and signed by both parties.

### 10.3 Governing Law

This Work Letter shall be governed by the laws of [State].

### 10.4 Time is of the Essence

Time is of the essence for all dates and deadlines in this Work Letter.

---

## EXHIBITS

**Exhibit A**: Premises Floor Plan
**Exhibit B**: Building Standard Finishes
**Exhibit C**: Landlord's Base Building Work (detailed specifications)
**Exhibit D**: TI Allowance Budget (allowable cost categories)
**Exhibit E**: General Contractor Requirements
**Exhibit F**: Construction Rules and Regulations

---

## ACKNOWLEDGMENT

**LANDLORD**:

[Landlord Name]

By: ____________________________
Name: [Name]
Title: [Title]
Date: ______________


**TENANT**:

[Tenant Name]

By: ____________________________
Name: [Name]
Title: [Title]
Date: ______________

---

*Generated by Commercial Lease Analysis Toolkit v1.0.0*
*Date: [Generation Date and Time] Eastern Time*
*This work letter is based on provisions extracted from the lease dated [Lease Date].*
*Review by qualified legal counsel is recommended before execution.*
```

---

## Step 9: Summary Output

Provide summary of generated work letter.

**Output format:**
```markdown
## Work Letter Generated Successfully

**Files Created**:
- Reports/[timestamp]_[tenant]_work_letter.md

**Key Provisions Extracted**:

**TI Allowance**:
- Amount: $[XX.XX]/SF ($[XXX,XXX] total)
- Allowable costs: [X] categories identified
- Non-allowable costs: [X] categories identified

**Landlord's Work**:
- Base building: [X] items
- TI allowance management and disbursement
- Permit procurement and approvals

**Tenant's Work**:
- Design obligations: [X] deliverables
- Construction scope: [X] work items
- Tenant-funded upgrades: [X] categories

**Timeline**:
- Design phase: [X] weeks
- Permitting phase: [X] weeks
- Construction phase: [X] weeks
- Total duration: [X] weeks
- Target completion: [Date]

**Critical Milestones**:
1. Space plan approval: [Date]
2. Working drawings approval: [Date]
3. Building permit: [Date]
4. Substantial completion: [Date]
5. Lease commencement: [Date]

**Approval Process**:
- Space plan review: [X] days
- Working drawings review: [X] days
- Change orders: [X] days
- [X] revision rounds included

**Cost Allocation**:
- TI Allowance covers: [%] of estimated costs
- Tenant-funded: [%] of estimated costs
- Estimated total project cost: $[XXX,XXX]

**Next Steps**:
1. Review work letter with legal counsel
2. Finalize construction timeline with contractor
3. Engage architect/designer if not already done
4. Begin space planning process
5. Schedule kick-off meeting with all parties

**Important Dates to Calendar**:
- Space plan submission deadline: [Date]
- Working drawings submission deadline: [Date]
- Construction start (target): [Date]
- Substantial completion (target): [Date]
- Lease commencement date: [Date]

**Recommendations**:
- [ ] Engage experienced commercial architect familiar with [building type]
- [ ] Obtain cost estimate to compare against TI allowance
- [ ] Identify long-lead items (HVAC, custom elements) early
- [ ] Build 2-week buffer into design and permit phases
- [ ] Clarify any ambiguous cost allocation items with landlord
- [ ] Review building standards exhibit carefully
- [ ] Understand change order cost implications

---

⚠️ **IMPORTANT**: This work letter is based on automated extraction from lease documents.
It should be reviewed and approved by qualified legal counsel before execution.
Verify all dates, amounts, and responsibilities against the original lease agreement.
```

---

## Key Guidelines

### TI Allowance Analysis

**Common allowance ranges** (market dependent):
- Office (Class A): $50-$100/SF
- Office (Class B): $30-$60/SF
- Industrial: $5-$15/SF
- Retail: $25-$75/SF

**Allowable vs. Non-Allowable**:
- Generally allowable: Hard costs, architectural fees, permits, standard finishes
- Generally non-allowable: FF&E, moving, IT equipment, premium finishes

### Timeline Considerations

**Typical phases**:
- Space plan: 2-4 weeks (including approval)
- Working drawings: 4-8 weeks (including approval)
- Permitting: 2-6 weeks (varies by jurisdiction)
- Construction: 8-16 weeks (varies by scope)

**Add buffer for**:
- First-time space planning (tenant learning curve)
- Complex MEP requirements
- Structural modifications
- Occupied building restrictions

### Approval Process

**Landlord typically reviews for**:
- Building code compliance
- Building system capacity (HVAC, electrical, plumbing)
- Structural integrity
- Impact on other tenants
- Aesthetic standards (if applicable)

**Common rejection reasons**:
- Inadequate HVAC load calculations
- Insufficient electrical capacity
- Non-compliant egress/life safety
- Unauthorized structural modifications

### Cost Management

**Protect against overruns**:
- Obtain detailed cost estimate early
- Identify upgrade costs before finalizing design
- Build contingency (10-15% of construction cost)
- Understand change order cost implications
- Track TI allowance utilization carefully

**Common unexpected costs**:
- Unforeseen conditions (asbestos, structural issues)
- Code compliance upgrades
- Utility capacity upgrades
- Extended project duration carrying costs

### Construction Coordination

**Critical for occupied buildings**:
- Work hour restrictions
- Noise and dust control
- Elevator and loading dock scheduling
- Protection of adjacent spaces
- Tenant/occupant notifications

---

## Notes

- Always extract Schedule C (Landlord's and Tenant's Work) from lease
- TI allowance terms vary widely - read carefully
- Building standard definitions are critical for cost allocation
- Approval timelines are often "deemed approved" if landlord doesn't respond
- Construction timelines should include realistic buffers
- Work letter should be consistent with lease terms but provide more detail
- Legal review essential before execution - this is a binding document

---

**Generated**: 2025-10-31
**Category**: Compliance
**Related Commands**: /abstract-lease, /critical-dates, /notice-generator
