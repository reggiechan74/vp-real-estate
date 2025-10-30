---
description: Generate estoppel certificate from lease abstract - pre-populate tenant representations for lender/purchaser due diligence
---

You are a commercial real estate transaction specialist. Generate an estoppel certificate from a lease abstract, pre-populating all standard tenant representations required for property financing or sale transactions.

## Input

1. **Lease abstract** - Current lease summary with all key terms
2. **As of date** - Date for certificate (default: current date)

**Arguments**: {{args}}

## Process

### Step 1: Extract Key Lease Information

From lease abstract, extract:
- Lease date
- Commencement date
- Current expiry date
- Current rent (base + additional)
- Security deposit amount
- Outstanding defaults (if any)
- Amendments/modifications
- Options (renewal, expansion, termination)
- Special provisions

### Step 2: Generate Estoppel Certificate

Create comprehensive estoppel certificate:

```markdown
TENANT ESTOPPEL CERTIFICATE

TO: [LENDER/PURCHASER NAME]
    [ADDRESS]

AND TO: [LANDLORD NAME]
         [ADDRESS]

DATE: [DATE]

RE: LEASE DATED [DATE] FOR PREMISES AT [ADDRESS] (THE "LEASE")

The undersigned [TENANT NAME] ("Tenant") hereby certifies to [Lender/Purchaser] and to [Landlord] as follows:

1. LEASE IDENTIFICATION

The Tenant is the tenant under a lease dated [DATE] (the "Original Lease") with [LANDLORD NAME] as landlord, for premises located at [ADDRESS], comprising approximately [X,XXX] square feet of rentable area (the "Premises").

2. AMENDMENTS

The Lease has been amended/modified as follows:

[X] No amendments or modifications
[ ] Amendment dated [DATE] re: [DESCRIPTION]
[ ] Amendment dated [DATE] re: [DESCRIPTION]

The Original Lease, together with all amendments and modifications, is referred to as the "Lease."

3. LEASE TERM

(a) Commencement Date: [DATE]
(b) Current Expiry Date: [DATE]
(c) Renewal Options: [X] option(s) to renew for [X] year(s) each
(d) Notice Required: [X] months prior to expiry
(e) Renewal Rent: [Fixed / Market / Greater of fixed or market]

4. RENT

Current rent payable under the Lease is:

(a) Base Rent: $[XXX,XXX] per annum ($[XX,XXX] per month)
(b) Base Rent per Square Foot: $[XX.XX] per square foot per annum
(c) Additional Rent (estimated): $[XX,XXX] per annum
(d) Total Annual Rent: $[XXX,XXX]
(e) Next Rent Increase: [DATE] to $[XXX,XXX]

All rent has been paid to [DATE]. No rent has been prepaid beyond [DATE].

5. SECURITY DEPOSIT

(a) Rent Deposit: $[XX,XXX] (representing [X] months' base rent)
(b) Letter of Credit: $[XX,XXX] in favor of Landlord
(c) Other Security: [DESCRIBE OR NONE]

The security deposit is held by Landlord. No portion has been applied to rent or other obligations. No claims have been made against the security deposit.

6. LEASE IN GOOD STANDING

(a) The Lease is in full force and effect and has not been cancelled, terminated, or surrendered.

(b) The Lease constitutes the entire agreement between Landlord and Tenant. There are no side letters, oral agreements, or other understandings modifying the Lease.

(c) Tenant has accepted possession of the Premises and is in occupancy.

(d) Landlord has completed all work required under the Lease.

(e) All tenant improvement allowances have been paid [OR $[XXX,XXX] remains owing to Tenant].

7. NO DEFAULTS

(a) To Tenant's knowledge, neither Tenant nor Landlord is in default under the Lease.

(b) No event has occurred which, with notice or lapse of time, would constitute a default by Tenant or Landlord.

(c) Tenant has no knowledge of any defenses, setoffs, or counterclaims against enforcement of the Lease.

(d) Tenant has not given or received any notice of default.

[ALTERNATIVE IF DEFAULTS EXIST:]
(a) The following defaults exist under the Lease: [DESCRIBE]
(b) [DESCRIBE STATUS AND CURE EFFORTS]

8. NO OFFSETS OR CLAIMS

Tenant has no claims against Landlord and no right of offset or deduction from rent, except:

[X] None
[ ] [DESCRIBE ANY OFFSETS OR CLAIMS]

9. OPTIONS

(a) Renewal Options: [X] option(s) to renew for [X] years each, exercisable by notice [X] months before expiry. [None have been exercised / First option has been exercised - renewal term to [DATE]]

(b) Expansion Options: [DESCRIBE OR NONE]

(c) Termination Options: [DESCRIBE OR NONE]

(d) Purchase Options: [DESCRIBE OR NONE]

(e) Right of First Refusal/Offer: [DESCRIBE OR NONE]

10. ASSIGNMENT AND SUBLETTING

(a) Tenant has [not] assigned the Lease or sublet any portion of the Premises.

[IF ASSIGNED/SUBLET:]
(b) [DESCRIBE ASSIGNMENT/SUBLEASE WITH DATE AND LANDLORD CONSENT]

11. TENANT IMPROVEMENTS

(a) All tenant improvements and leasehold improvements required under the Lease have been completed.

(b) Tenant owns all trade fixtures and removable equipment. Landlord has no claim to Tenant's personal property.

(c) [IF APPLICABLE: Tenant has financed leasehold improvements in the amount of $[XXX,XXX] with [LENDER] pursuant to security agreement dated [DATE]]

12. ENVIRONMENTAL

To Tenant's knowledge:

(a) Tenant has not used, generated, stored, or disposed of any hazardous substances on the Premises except in compliance with all laws and the Lease.

(b) Tenant has not received any environmental notices, orders, or complaints regarding the Premises.

(c) No environmental contamination exists at the Premises caused by Tenant's operations.

13. INSURANCE

(a) Tenant maintains all insurance required under the Lease.

(b) All insurance premiums are current and paid.

(c) No insurance claims have been made [OR describe any claims].

14. FINANCIAL OBLIGATIONS CURRENT

(a) All rent, additional rent, and other charges under the Lease are current and paid.

(b) Tenant has delivered all financial statements required under the Lease.

(c) Tenant is in compliance with all financial covenants.

15. LANDLORD OBLIGATIONS PERFORMED

(a) Landlord has performed all of its obligations under the Lease.

(b) All services required to be provided by Landlord are being provided.

(c) No deficiencies exist in Landlord's performance.

16. USE OF PREMISES

(a) Tenant uses the Premises for: [DESCRIBE PERMITTED USE]

(b) This use complies with all applicable laws, zoning, and the Lease.

(c) Tenant has obtained all necessary permits and licenses.

17. PARKING

Tenant has the right to [X] parking spaces [in designated/visitor locations]. All parking rights under the Lease are being provided.

18. FINANCIAL CONDITION

[IF REQUIRED BY LENDER/PURCHASER:]

Tenant certifies that:

(a) Tenant is a [corporation/partnership] duly organized and validly existing under the laws of [JURISDICTION].

(b) Tenant is solvent and able to pay its debts as they become due.

(c) No bankruptcy, insolvency, or similar proceedings have been commenced by or against Tenant.

(d) There has been no material adverse change in Tenant's financial condition since [DATE OF LAST FINANCIAL STATEMENTS].

19. RELIANCE

Tenant acknowledges that this Certificate is being relied upon by:

(a) [LENDER NAME] in connection with [LOAN/FINANCING] secured by the property
(b) [PURCHASER NAME] in connection with [PURCHASE] of the property

Tenant consents to [Lender/Purchaser] relying on this Certificate in making its decision to [provide financing/complete purchase].

20. AUTHORITY

The undersigned is authorized to execute this Certificate on behalf of Tenant and has personal knowledge of the matters certified herein.

21. SURVIVAL

The certifications herein shall survive [closing of the loan/completion of the purchase] and shall not merge therein.

DATED this [DAY] day of [MONTH], [YEAR].

[TENANT LEGAL NAME]

Per: _________________________
Name: [NAME]
Title: [TITLE]

Per: _________________________  [If corporate seal required]
Name: [NAME]
Title: [TITLE]
```

### Step 3: Create Landlord Verification Checklist

Generate checklist for landlord to verify tenant's representations:

| Item | Tenant Certified | Landlord Verified | Discrepancies |
|------|------------------|-------------------|---------------|
| Lease dates | ✓ | ✓ | None |
| Current rent amount | ✓ | ✓ | None |
| Security deposit amount | ✓ | ✓ | None |
| No defaults | ✓ | [ ] | [CHECK] |
| Rent paid to [date] | ✓ | [ ] | [CHECK] |
| No amendments | ✓ | [ ] | [CHECK] |
| Insurance current | ✓ | [ ] | [CHECK] |
| Options status | ✓ | [ ] | [CHECK] |

### Step 4: Generate Supporting Documents

Create package including:
- Completed estoppel certificate (ready for tenant signature)
- Landlord verification checklist
- Instructions to tenant for completion
- Timeline for execution
- Copy of lease abstract for tenant reference

## Important Guidelines

1. **Accuracy is Critical:**
   - Verify all information against lease
   - Don't assume - confirm every fact
   - Flag items requiring verification
   - Note any uncertainties

2. **Standard Certifications:**
   - Lease in full force and effect
   - No defaults
   - Rent current
   - No side agreements
   - No offsets or claims
   - Landlord obligations performed

3. **Lender-Specific Requirements:**
   - Some lenders require specific language
   - Financial condition certifications may be required
   - Subordination acknowledgment may be needed
   - Non-disturbance provisions may be referenced

4. **Timing:**
   - Estoppels typically required within 10-30 days
   - Coordinate with transaction closing
   - Plan for tenant review time
   - Allow for corrections/revisions

## Example Usage

```
/estoppel-certificate /path/to/lease_abstract.md
/estoppel-certificate /path/to/lease_abstract.md 2025-11-15
```

This will generate a complete estoppel certificate pre-populated from the lease abstract, ready for tenant signature.

Begin certificate generation with provided lease information.
