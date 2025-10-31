---
description: Generate calendar/reminders for all critical lease dates - option notices, renewals, rent reviews, expirations
---

You are a commercial lease administration specialist. Your task is to extract all critical dates from lease documents, create a comprehensive calendar of deadlines, and generate reminder schedules to ensure no important dates are missed.

## Input

The user will provide:
1. **Lease document(s)** - One or more lease abstracts or full leases
2. **Output format (optional)** - Calendar format preference (iCal, CSV, markdown)

**Arguments**: {{args}}

## Process

### Step 1: Extract All Critical Dates

For each lease document, extract:

**Lease Term Dates:**
- Lease execution date
- Lease commencement date
- Rent commencement date (if different)
- Initial term expiry date
- Extension option expiry dates (if exercised)
- Final possible expiry date (all options)

**Option Exercise Deadlines:**
- Renewal option notice deadlines (each option period)
- Expansion option notice deadlines
- Termination option notice deadlines
- Purchase option exercise deadlines
- Right of first refusal deadlines

**Rent and Financial Dates:**
- Rent increase effective dates
- Rent review dates (market review, CPI adjustment)
- Operating cost reconciliation due dates
- Tax reconciliation due dates
- Security deposit review/adjustment dates
- Letter of credit renewal dates

**Insurance and Compliance:**
- Insurance certificate renewal dates
- Insurance policy expiry dates
- Environmental audit due dates
- Financial statement delivery deadlines (quarterly, annual)
- Business license renewal dates

**Maintenance and Inspections:**
- HVAC maintenance schedule dates
- Fire safety inspection dates
- Elevator inspection dates
- Building audit dates
- Lease compliance inspection dates

**Special Provisions:**
- Fixturing period end date
- Construction completion deadlines
- Landlord work completion deadlines
- Co-tenancy cure period deadlines
- Exclusive use provision dates
- Sign installation deadline

**Default and Cure Period Tracking:**
- Rent payment due dates (monthly/quarterly)
- Cure period deadlines (if default occurs)
- Notice periods for various violations

### Step 2: Calculate Reminder Dates

For each critical date, calculate multiple reminder dates:

**Standard Reminder Schedule:**
- 180 days before (6 months)
- 120 days before (4 months)
- 90 days before (3 months)
- 60 days before (2 months)
- 30 days before (1 month)
- 14 days before (2 weeks)
- 7 days before (1 week)
- 3 days before
- 1 day before
- Day of event

**Custom Reminder Schedules:**

**For Option Notices (Critical):**
- 1 year before deadline
- 9 months before
- 6 months before
- 3 months before
- 2 months before
- 1 month before
- 2 weeks before
- 1 week before
- 3 days before
- Day before
- Day of deadline

**For Lease Expiry (Planning Required):**
- 24 months before (start strategic planning)
- 18 months before (engage broker if relocating)
- 12 months before (option notice typically due)
- 9 months before
- 6 months before (finalize decision)
- 3 months before (execute documents)
- 1 month before (move planning)
- Day of expiry

**For Recurring Events (e.g., Monthly Rent):**
- 5 days before due date
- 2 days before due date
- Day of due date
- 1 day after (if not paid - warning)

### Step 3: Categorize and Prioritize

**Priority Levels:**

**CRITICAL (P1) - Cannot Miss:**
- Option exercise deadlines
- Lease expiration dates
- Termination notice deadlines
- Purchase option deadlines
- Insurance renewal deadlines

**HIGH (P2) - Important for Compliance:**
- Rent payment due dates
- Financial statement delivery
- Operating cost reconciliation
- Tax payment deadlines
- Maintenance requirements

**MEDIUM (P3) - Important for Planning:**
- Rent review dates
- Budget planning dates
- Inspection schedules
- Reporting deadlines

**LOW (P4) - Administrative:**
- File review dates
- Internal audit dates
- Policy review dates

### Step 4: Create Master Calendar

Generate comprehensive calendar with all dates:

**Markdown Table Format:**

| Date | Event Type | Description | Priority | Advance Notice | Action Required | Responsible Party |
|------|------------|-------------|----------|----------------|-----------------|-------------------|
| YYYY-MM-DD | Rent Due | Month 1 rent payment | P2 | 5 days | Pay rent $X,XXX | Tenant |
| YYYY-MM-DD | Option Notice | 1st renewal notice deadline | P1 | 12 months | Deliver notice or lose option | Tenant |
| YYYY-MM-DD | Rent Increase | Year 2 rent escalation | P3 | 30 days | Update payment amount | Tenant |
| YYYY-MM-DD | Lease Expiry | Initial term ends | P1 | 24 months | Renew or relocate decision | Tenant |

### Step 5: Generate Reminder Schedule

Create detailed reminder schedule:

**For Each Critical Date:**

```markdown
### [Event Name] - YYYY-MM-DD

**Event:** [Description]
**Priority:** [P1/P2/P3/P4]
**Action Required:** [What must be done]
**Responsible:** [Who must act]
**Consequence of Missing:** [Impact]

**Reminder Schedule:**
- 180 days before (YYYY-MM-DD): Initial planning notification
- 120 days before (YYYY-MM-DD): Start preparation
- 90 days before (YYYY-MM-DD): Gather required information/documents
- 60 days before (YYYY-MM-DD): Draft notice/prepare action
- 30 days before (YYYY-MM-DD): Review and finalize
- 14 days before (YYYY-MM-DD): Executive approval
- 7 days before (YYYY-MM-DD): Final review
- 3 days before (YYYY-MM-DD): Deliver notice/take action
- 1 day before (YYYY-MM-DD): Confirm delivery/completion
- Day of (YYYY-MM-DD): EVENT DATE - Verify completion
```

### Step 6: Create iCalendar File

Generate `.ics` file for import to Outlook, Google Calendar, etc.:

```ics
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Claude Code//Lease Critical Dates//EN
CALNAME:Lease Critical Dates - [Property Address]
TIMEZONE:America/Toronto

BEGIN:VEVENT
UID:[unique-id]@lease-abstract
DTSTAMP:[timestamp]
DTSTART:[YYYYMMDD]
SUMMARY:[Event Name]
DESCRIPTION:[Detailed description including action required, consequences, etc.]
LOCATION:[Property Address]
PRIORITY:[1-9]
STATUS:CONFIRMED
BEGIN:VALARM
TRIGGER:-P180D
DESCRIPTION:6 months until [Event]
ACTION:DISPLAY
END:VALARM
BEGIN:VALARM
TRIGGER:-P90D
DESCRIPTION:3 months until [Event]
ACTION:DISPLAY
END:VALARM
BEGIN:VALARM
TRIGGER:-P30D
DESCRIPTION:1 month until [Event]
ACTION:DISPLAY
END:VALARM
BEGIN:VALARM
TRIGGER:-P7D
DESCRIPTION:1 week until [Event]
ACTION:DISPLAY
END:VALARM
BEGIN:VALARM
TRIGGER:-P1D
DESCRIPTION:Tomorrow: [Event]
ACTION:DISPLAY
END:VALARM
END:VEVENT

[Repeat for each event]

END:VCALENDAR
```

### Step 7: Create CSV Export

Generate CSV file for import to Excel, lease management software:

```csv
Date,Event_Type,Description,Priority,Property,Tenant,Action_Required,Responsible_Party,Reminder_180d,Reminder_90d,Reminder_30d,Reminder_7d,Reminder_1d,Consequence_If_Missed,Notes
YYYY-MM-DD,Option_Notice,First renewal option notice deadline,P1,[Address],[Tenant],Deliver renewal notice,Tenant,YYYY-MM-DD,YYYY-MM-DD,YYYY-MM-DD,YYYY-MM-DD,YYYY-MM-DD,Lose renewal option - forced to relocate or accept market rent,[Notes]
YYYY-MM-DD,Rent_Due,Month 1 rent payment,P2,[Address],[Tenant],Pay rent $X XXX,Tenant,,,YYYY-MM-DD,YYYY-MM-DD,YYYY-MM-DD,Late fee + potential default,[Notes]
...
```

### Step 8: Create Next 12 Months Summary

Generate quick-reference for upcoming deadlines:

```markdown
## Critical Dates - Next 12 Months

### This Month ([Month YYYY])
- [Date]: [Event] - [Priority] - [Action Required]
- [Date]: [Event] - [Priority] - [Action Required]

### Next Month ([Month YYYY])
- [Date]: [Event] - [Priority] - [Action Required]

### [Month YYYY]
- [Date]: [Event] - [Priority] - [Action Required]

[Continue for 12 months]

### Priority 1 (CRITICAL) Events in Next 12 Months: X
### Priority 2 (HIGH) Events in Next 12 Months: X
### Total Events in Next 12 Months: X
```

### Step 9: Generate Timeline Visualization

Create visual timeline (ASCII or markdown):

```
Lease Timeline for [Property Address]
================================================================================

Year 1 (YYYY-MM to YYYY-MM)
|--Commence--|--Rent Due (Monthly)--|--Insurance Renewal--|--Year End--|
   YYYY-MM                                                    YYYY-MM

Year 2 (YYYY-MM to YYYY-MM)
|--Rent Increase--|--Financial Statements--|--Rent Due--|--Year End--|
   YYYY-MM                                                YYYY-MM

Year 3 (YYYY-MM to YYYY-MM)
|--Rent Increase--|--RENEWAL NOTICE DUE**--|--Rent Due--|--Year End--|
   YYYY-MM         YYYY-MM (12 mo before)                YYYY-MM

Year 4 (YYYY-MM to YYYY-MM)
|--Rent Increase--|--Rent Due--|--LEASE EXPIRY**--|
   YYYY-MM                      YYYY-MM

** CRITICAL DEADLINE
================================================================================
```

### Step 10: Generate Comprehensive Report

Create detailed report in `/workspaces/lease-abstract/Reports/`:
`[property]_critical_dates_[date].md`

And supporting files:
- `[property]_critical_dates.ics` (iCalendar)
- `[property]_critical_dates.csv` (Excel import)

**Report Structure:**

```markdown
# Critical Lease Dates Calendar
## [Property Address] - [Tenant Name]

**Generated:** [Date]
**Lease Term:** [Start Date] to [End Date]
**Total Critical Dates Tracked:** XX

---

## Executive Summary

**Lease Overview:**
- Property: [Address]
- Tenant: [Tenant Name]
- Commencement: YYYY-MM-DD
- Current Expiry: YYYY-MM-DD
- Final Expiry (with options): YYYY-MM-DD

**Upcoming Critical Deadlines (Next 90 Days):**
1. [Date] - [Event] - **[X days away]**
2. [Date] - [Event] - **[X days away]**
3. [Date] - [Event] - **[X days away]**

**Most Critical Upcoming Deadline:**
**[Event Name] - [Date] ([X days/months away])**

**Action Required:** [Description]
**Consequence if Missed:** [Impact]

---

## Next 12 Months - All Dates

[Month-by-month breakdown as shown in Step 8]

---

## Complete Critical Dates Calendar

### Priority 1 (CRITICAL) - Cannot Miss

| Date | Event | Action Required | Notice Period | Consequence if Missed | Status |
|------|-------|-----------------|---------------|----------------------|--------|
| YYYY-MM-DD | 1st Renewal Option Notice | Deliver written notice | 12 months | Lose renewal option | [Upcoming/Completed] |
| YYYY-MM-DD | Insurance Policy Renewal | Renew or replace policy | 30 days | Breach of lease, no coverage | [Upcoming/Completed] |
| YYYY-MM-DD | Lease Expiry | Vacate or exercise renewal | N/A | Holdover, potential damages | [Upcoming/Completed] |

### Priority 2 (HIGH) - Important for Compliance

| Date | Event | Action Required | Notice Period | Consequence if Missed | Status |
|------|-------|-----------------|---------------|----------------------|--------|
| Monthly | Rent Payment | Pay base rent + additional rent | 1st of month | Late fee, default | [Recurring] |
| YYYY-MM-DD | Annual Financial Statements | Deliver audited financials | 90 days after YE | Covenant breach | [Upcoming/Completed] |
| YYYY-MM-DD | Operating Cost Reconciliation | Review and pay/receive adjustment | 30 days | Disputes, non-payment | [Upcoming/Completed] |

### Priority 3 (MEDIUM) - Important for Planning

| Date | Event | Action Required | Notice Period | Consequence if Missed | Status |
|------|-------|-----------------|---------------|----------------------|--------|
| YYYY-MM-DD | Rent Increase | Update payment amount | 30 days notice | Underpayment | [Upcoming/Completed] |
| YYYY-MM-DD | Market Rent Review | Engage appraiser | 6 months | Unfavorable determination | [Upcoming/Completed] |

### Priority 4 (LOW) - Administrative

| Date | Event | Action Required | Notice Period | Consequence if Missed | Status |
|------|-------|-----------------|---------------|----------------------|--------|
| YYYY-MM-DD | Annual file review | Review lease compliance | N/A | Internal only | [Upcoming/Completed] |

---

## Detailed Event Information

### Event: First Renewal Option Notice Deadline

**Date:** YYYY-MM-DD
**Priority:** P1 - CRITICAL
**Days Until Deadline:** XXX days

**Description:**
Tenant must deliver written notice to Landlord of intention to exercise first renewal option for additional 5-year term. Notice must be delivered no later than 12 months before current expiry date (YYYY-MM-DD).

**Action Required:**
1. Decide by [3 months before]: Renew at this location or relocate?
2. If renewing: Draft renewal notice
3. Obtain executive approval
4. Deliver notice via registered mail/courier
5. Retain proof of delivery

**Notice Requirements:**
- Must be in writing
- Must be signed by authorized officer
- Must be delivered to: [Landlord address from lease]
- Delivery methods accepted: [Registered mail, courier, personal delivery]
- Must state: "Tenant exercises its renewal option for [X]-year term"

**Consequence if Missed:**
- Renewal option is LOST permanently
- Tenant must vacate at expiry or negotiate new lease at market terms
- Landlord has no obligation to offer renewal
- Forced relocation or unfavorable market rent

**Documents Needed:**
- Copy of lease (verify exact notice requirements)
- Renewal notice letter (draft provided in Appendix)
- Corporate authorization (board resolution if required)
- Proof of delivery

**Estimated Cost of Missing:**
- Relocation costs: $XXX,XXX
- Business disruption: $XX,XXX
- Lost rent differential (if market > renewal): $XX,XXX/year
- Total: $XXX,XXX+

**Reminder Schedule:**
- [ ] 12 months before (YYYY-MM-DD): Start renewal analysis
- [ ] 9 months before (YYYY-MM-DD): Engage broker if considering relocation
- [ ] 6 months before (YYYY-MM-DD): Complete renewal vs relocate analysis
- [ ] 4 months before (YYYY-MM-DD): Make decision
- [ ] 3 months before (YYYY-MM-DD): Draft notice
- [ ] 2 months before (YYYY-MM-DD): Obtain approvals
- [ ] 1 month before (YYYY-MM-DD): Review and finalize notice
- [ ] 2 weeks before (YYYY-MM-DD): Final review
- [ ] 1 week before (YYYY-MM-DD): Sign and prepare for delivery
- [ ] 3 days before (YYYY-MM-DD): Deliver notice
- [ ] Day of deadline (YYYY-MM-DD): CONFIRM DELIVERY COMPLETED

**Status:** [Not Started / In Progress / Completed]
**Responsible Party:** [Name/Department]
**Last Updated:** [Date]

[Repeat similar detail for each critical event]

---

## Recurring Events

### Monthly Rent Payments

**Due Date:** 1st day of each month
**Amount:**
- Base Rent: $X,XXX
- Operating Costs: $X,XXX
- Total: $X,XXX

**Payment Method:** [PAD / Wire / Cheque]
**Payment To:** [Landlord/Property Manager details]

**Reminder Schedule:**
- 5 business days before: Prepare payment
- 2 business days before: Approve payment
- Day before: Initiate payment
- Due date: Verify payment received
- 1 day after: If not received, follow up immediately

**Late Payment Consequences:**
- Late fee: $XXX or X% of rent
- Interest: X% per annum
- Default if unpaid X days after due date
- Landlord remedies: Distress, lockout, termination

### Quarterly Financial Statement Delivery

**Due Dates:**
- Q1 (Jan-Mar): May 15
- Q2 (Apr-Jun): Aug 15
- Q3 (Jul-Sep): Nov 15
- Q4 (Oct-Dec): Feb 15 (following year)

**Requirements:**
- Unaudited balance sheet and income statement
- Signed by CFO or senior officer
- Format: [PDF, hard copy, both]
- Deliver to: [Landlord address]

**Reminder Schedule:**
- 30 days before: Request financials from accounting
- 15 days before: Review financials
- 7 days before: Obtain signature
- 3 days before: Deliver to landlord
- Day of: Confirm receipt

---

## Annual Timeline

### Year 1 (YYYY-MM to YYYY-MM)

| Month | Date | Event | Priority | Action |
|-------|------|-------|----------|--------|
| Month 1 | YYYY-MM-DD | Lease Commencement | - | Move in |
| Month 1 | YYYY-MM-01 | First Rent Payment | P2 | Pay $X,XXX |
| Month 3 | YYYY-MM-DD | Fixturing Period Ends | P2 | Open for business |
| Month 6 | YYYY-MM-DD | Insurance Renewal | P1 | Renew policy |
| Month 12 | YYYY-MM-DD | Financial Statements | P2 | Deliver audited FS |
| Month 12 | YYYY-MM-DD | Operating Cost Reconciliation | P2 | Review & pay |

[Repeat for each year]

### Year 5 (YYYY-MM to YYYY-MM) - CRITICAL YEAR

| Month | Date | Event | Priority | Action |
|-------|------|-------|----------|--------|
| Month 1 | YYYY-MM-DD | **RENEWAL NOTICE DEADLINE** | **P1** | **Deliver notice** |
| Month 12 | YYYY-MM-DD | Rent Increase (Year 6 if renewed) | P3 | Update payment |
| Month 13 | YYYY-MM-DD | **LEASE EXPIRY** | **P1** | **Vacate or renewal starts** |

---

## Visualization: Lease Timeline

[Include ASCII timeline as shown in Step 9]

---

## Notice Templates

### Renewal Option Exercise Notice Template

```
[Date]

[Landlord Name]
[Landlord Address]

Dear [Landlord Name]:

Re: Exercise of Renewal Option - [Property Address]

This letter serves as formal notice that [Tenant Legal Name] ("Tenant") hereby exercises its option to renew the Lease dated [Lease Date] (the "Lease") for the premises located at [Property Address] (the "Premises").

Pursuant to Section [X] of the Lease, Tenant exercises its [first/second] option to renew for an additional term of [X] years, commencing on [Renewal Start Date] and expiring on [Renewal End Date].

All other terms and conditions of the Lease shall remain in full force and effect, except as modified by the renewal provisions set out in Section [X] of the Lease.

Please acknowledge receipt of this notice and confirm the renewal rent for the renewal term in accordance with the Lease provisions.

Yours truly,

[Tenant Legal Name]

Per: _________________________
Name: [Authorized Signatory]
Title: [Title]

cc: [Property Manager, if applicable]
```

[Include templates for other common notices]

---

## Implementation Instructions

### Setting Up Reminders

**Option 1: Import iCalendar File**
1. Locate file: `[property]_critical_dates.ics`
2. Open with Outlook/Google Calendar/Apple Calendar
3. Import to main calendar or create separate "Lease Dates" calendar
4. Configure reminder defaults
5. Share calendar with relevant team members

**Option 2: Import CSV to Excel**
1. Open file: `[property]_critical_dates.csv`
2. Import to Excel
3. Set up conditional formatting for upcoming dates
4. Create pivot table for monthly view
5. Set up Excel reminders (via macros or manual)

**Option 3: Import to Lease Management Software**
1. Export data in required format
2. Map fields to software requirements
3. Import and verify all dates
4. Configure automated reminder emails

### Assigning Responsibilities

| Event Type | Responsible Party | Backup |
|------------|------------------|--------|
| Option Notices | [Name/Dept] | [Name/Dept] |
| Rent Payments | [Name/Dept] | [Name/Dept] |
| Financial Reporting | [Name/Dept] | [Name/Dept] |
| Insurance | [Name/Dept] | [Name/Dept] |
| Maintenance | [Name/Dept] | [Name/Dept] |

### Monthly Review Process

**First Monday of Each Month:**
1. Review critical dates for next 90 days
2. Verify all upcoming deadlines assigned
3. Confirm reminder systems functioning
4. Update status of recently completed items
5. Flag any missed deadlines for immediate action

---

## Appendices

### A. All Dates Sorted Chronologically

[Complete list of every single date from lease, sorted chronologically]

### B. All Dates by Category

**Lease Term & Options:**
- [All term/option dates]

**Financial:**
- [All financial dates]

**Compliance:**
- [All compliance dates]

**Maintenance:**
- [All maintenance dates]

### C. Source Lease Provisions

[References to specific lease sections for each critical date]

### D. Risk Assessment

| Event | Likelihood of Missing | Impact if Missed | Risk Score | Mitigation |
|-------|----------------------|------------------|------------|------------|
| Renewal notice | Low (if calendar used) | Very High (forced relocation) | HIGH | Multiple reminders, executive oversight |
| Rent payment | Very Low (recurring) | High (default risk) | MEDIUM | PAD, automated reminders |
| Insurance renewal | Low | Very High (no coverage) | HIGH | Agent reminder, calendar alert |

---

## Change Log

| Date | Change | Reason | Updated By |
|------|--------|--------|------------|
| [Date] | Initial calendar created | New lease executed | Claude Code |
| [Date] | [Future updates] | | |

---

**Calendar Generated:** [Timestamp]
**Next Review Date:** [30 days from generation]
**Maintained By:** [Department/Person]
**Contact:** [Email/Phone]
```

## Important Guidelines

1. **Comprehensive Extraction:**
   - Extract EVERY date from lease (don't miss any)
   - Include both specific dates and recurring events
   - Calculate option notice deadlines correctly
   - Account for business days vs calendar days

2. **Robust Reminder System:**
   - Multiple reminders for critical dates
   - Earlier warnings for events requiring planning
   - Different cadence for different priority levels
   - Escalation if approaching deadline

3. **User-Friendly Outputs:**
   - Generate multiple formats (markdown, iCal, CSV)
   - Clear prioritization and categorization
   - Visual timeline for quick reference
   - Ready-to-use notice templates

4. **Practical Implementation:**
   - Make it easy to import to calendar systems
   - Assign responsibilities
   - Include consequence of missing each deadline
   - Provide estimated costs of non-compliance

## Example Usage

```
/critical-dates /path/to/lease_abstract.md
/critical-dates /path/to/lease1.md /path/to/lease2.md /path/to/lease3.md
```

This will extract all critical dates, generate comprehensive calendar with reminders, and create iCal/CSV files for import to calendar and project management systems.

Begin the analysis now with the provided lease document(s).
