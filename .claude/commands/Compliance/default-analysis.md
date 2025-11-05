---
description: Assess potential lease defaults, calculate cure periods, analyze landlord remedies, and draft default notices
argument-hint: <lease-path> <default-description>
allowed-tools: WebSearch, WebFetch, Read, Write, Bash
---

You are a commercial lease enforcement specialist. Your task is to analyze potential default situations, determine applicable cure periods, assess landlord remedies available, calculate damages, and draft appropriate default notices.

## Input

The user will provide:
1. **Lease document or abstract** - Path to lease with default provisions
2. **Default situation description** - What breach has occurred or is occurring
3. **Supporting documentation (optional)** - Evidence of default (payment records, photos, correspondence)

**Arguments**: {{args}}

## Process

### Step 1: Identify Jurisdiction and Applicable Legislation

**Extract Jurisdiction from Lease:**
- Review lease document for property address and governing law clause
- Identify province/state where premises are located
- Note any specific governing law provisions in the lease

**Look Up Applicable Commercial Tenancies Legislation:**

**REQUIRED**: Use the **WebSearch** tool to research the current version of the applicable commercial tenancies statute for the identified jurisdiction.

**REQUIRED**: Use the **WebFetch** tool to retrieve and analyze the full text of the relevant statutory provisions from official government sources (e.g., CanLII, provincial/state legislature websites).

Based on jurisdiction, research the applicable statute:

**Canada:**
- Ontario: *Commercial Tenancies Act, R.S.O. 1990, c. L.7*
- Alberta: *Law of Property Act, R.S.A. 2000, c. L-7* (Part 4)
- British Columbia: *Commercial Tenancy Act, S.B.C. 2020, c. 4*
- Quebec: *Civil Code of Quebec* (Art. 1851-1891)
- Manitoba: *The Real Property Act, C.C.S.M. c. R30* (Part 3)
- Saskatchewan: *The Residential Tenancies Act, 2006* (commercial excluded)
- Nova Scotia: Common law (no specific commercial tenancies statute)
- Other provinces: Research applicable legislation

**United States:**
- Each state has different commercial lease laws
- Many states follow common law with some statutory modifications
- Research applicable state statutes for commercial leases
- Check for Uniform Commercial Code (UCC) provisions if applicable

**Research Process:**

1. **WebSearch** for: "[Jurisdiction] commercial tenancies act [current year]" or "[Jurisdiction] landlord tenant commercial lease statute"
   - Find official government sources (CanLII for Canada, state legislature sites for US)
   - Identify the current statute name and citation
   - Find links to official statute text

2. **WebFetch** the statute URL to extract:
   - Default and termination provisions
   - Notice requirements
   - Landlord remedy provisions (distress, re-entry, etc.)
   - Tenant protection provisions (relief from forfeiture, cure rights)
   - Damage limitation provisions
   - Any provisions that override or restrict lease terms

3. If statute is lengthy, focus **WebFetch** on specific sections:
   - Table of contents or index (to identify relevant sections)
   - Default and termination sections
   - Remedies sections
   - Notice requirement sections
   - Tenant protection sections

**Extract Key Statutory Provisions:**

For the identified jurisdiction, extract:

1. **Statutory Default Provisions:**
   - What constitutes default under the statute
   - Any mandatory cure periods
   - Notice requirements imposed by law
   - Prohibited lease clauses

2. **Statutory Landlord Remedies:**
   - Distress/distraint rights (if still permitted)
   - Re-entry rights and restrictions
   - Self-help remedies (lockout, utilities cutoff)
   - Remedies that require court order
   - Limitations on lease remedies

3. **Statutory Tenant Protections:**
   - Minimum cure periods
   - Relief from forfeiture provisions
   - Restrictions on landlord remedies
   - Required notice procedures
   - Dispute resolution mechanisms

4. **Mitigation Requirements:**
   - Landlord's duty to mitigate damages
   - Statutory limitations on damage claims
   - Re-letting obligations

**Example Statutory Extract (Ontario):**

```markdown
## Commercial Tenancies Act, R.S.O. 1990, c. L.7 - Key Provisions

### Distress for Rent (s. 19-30):
- Landlord may distrain goods on premises for rent arrears
- Minimum 5 days before sale
- Exempt goods: tools of trade (first $2,000), clothing, bedding
- Tenant may apply to court to stop distress

### Relief from Forfeiture (s. 20):
- Court may grant relief if tenant pays arrears + costs
- Discretionary remedy even after re-entry
- Consider tenant's conduct and landlord's prejudice

### Re-entry Limitations:
- Landlord cannot use force to re-enter
- Must obtain court order (writ of possession) if tenant resists
- Peaceable re-entry permitted if premises vacant

### Overholding Tenant (s. 32):
- Tenant liable for damages if holding over without consent
- Damages = 2x fair market rent during overholding period

### Notice Requirements:
- No statutory minimum for commercial defaults
- Common law requires reasonable notice
- Lease provisions typically control
```

**Compare Lease vs Statute:**

Create comparison table:

| Provision | Lease Requirement | Statutory Requirement | Governs | Notes |
|-----------|-------------------|----------------------|---------|-------|
| Monetary default cure | 5 days | None (common law) | Lease | Enforceable |
| Non-monetary cure | 30 days | None specified | Lease | Enforceable |
| Distress rights | Permitted | Permitted (s.19 CTA) | Both | Follow statute procedure |
| Relief from forfeiture | Not mentioned | Court discretion (s.20) | Statute | Cannot contract out |
| Lockout/force | Permitted | Prohibited if resisted | Statute | Lease clause void |
| Mitigation | Not specified | Common law duty | Statute | Implied obligation |

**Flag Statutory Overrides:**

Identify any lease provisions that may be void or unenforceable due to statutory restrictions:

- ⚠️ **Warning**: Lease clause permitting forcible re-entry may be void if statute prohibits
- ⚠️ **Warning**: Lease waiver of relief from forfeiture may not be enforceable (court has discretion)
- ⚠️ **Warning**: Check if statute requires specific notice format/delivery method

### Step 2: Identify Type of Default

**Monetary Defaults:**
- Non-payment of rent
- Non-payment of additional rent (operating costs, taxes)
- Non-payment of utilities
- Non-payment of insurance premiums
- Non-payment of other charges

**Non-Monetary Defaults:**
- Unauthorized assignment or subletting
- Prohibited use of premises
- Failure to maintain premises
- Failure to carry required insurance
- Abandonment of premises
- Nuisance or illegal activity
- Structural alterations without consent
- Breach of environmental covenants
- Failure to provide financial statements
- Violation of exclusive use provisions

**Insolvency Events:**
- Bankruptcy filing
- Receivership
- Assignment for benefit of creditors
- Winding-up proceedings
- Material adverse change in financial condition

### Step 3: Extract Default Provisions from Lease

**For Each Default Type, Extract:**

**Cure Period:**
- Monetary defaults: Typically 5-10 days
- Non-monetary defaults: Typically 15-30 days
- Insolvency events: Often no cure period (immediate default)
- Notice requirements: Written notice required? Delivery method?

**Landlord Remedies:**
- Right to terminate lease
- Right to re-enter and take possession
- Right to distrain (seize tenant goods)
- Right to lockout
- Right to perform tenant's obligations and charge cost
- Right to draw on security deposit
- Right to claim damages
- Right to accelerate rent
- Specific remedies for specific defaults

**Damage Calculations:**
- Rent to end of term
- Costs to re-lease (commissions, TI)
- Rent differential (if re-let at lower rent)
- Acceleration provisions
- Liquidated damages
- Mitigation obligations

**Example Extract:**

```markdown
## Default Provisions (Lease Section X)

### Events of Default:
1. Non-payment of rent: 5 days after written notice
2. Non-payment of additional rent: 10 days after written notice
3. Breach of covenants: 30 days after written notice to cure
4. Bankruptcy/insolvency: Immediate default, no cure
5. Abandonment: Immediate default after notice

### Landlord Remedies:
- Terminate lease and re-enter
- Distrain tenant goods
- Sue for damages
- Accelerate all rent to end of term
- Draw on security deposit
- Perform obligations and charge tenant

### Damages:
- Rent to end of term
- Less rent received from re-letting
- Plus re-letting costs (legal, broker, TI)
- Plus landlord's costs (legal fees, enforcement)
```

### Step 4: Analyze Specific Default Situation

Based on user's description, determine:

**Default Classification:**
- Type: [Monetary / Non-Monetary / Insolvency]
- Severity: [Material / Technical / Minor]
- Duration: [Ongoing / One-time / Repeated]
- Tenant responsiveness: [Cooperative / Uncooperative / No response]

**Cure Period Calculation:**

```
Default Occurred: YYYY-MM-DD
Notice Delivered: YYYY-MM-DD
Cure Period: X days from notice
Cure Deadline: YYYY-MM-DD
Days Remaining: X days
Status: [Within cure / Past cure / No cure available]
```

**Evidence of Default:**
- Documentation available: [Yes/No]
- Strength of evidence: [Strong / Moderate / Weak]
- Tenant's likely defenses: [List potential defenses]
- Landlord's position strength: [Strong / Moderate / Weak]

### Step 5: Calculate Potential Damages

**For Monetary Default (Unpaid Rent):**

```
Rent Owing:
- Base rent unpaid: $XX,XXX (X months × $X,XXX)
- Additional rent unpaid: $X,XXX
- Late fees: $XXX
- Interest (X% per annum): $XXX
- Total current arrears: $XX,XXX

If Lease Terminated:
- Remaining term: X months
- Future rent: $XXX,XXX
- Less: Mitigation (re-let at $XX,XXX): $(XX,XXX)
- Re-letting costs (commission, TI): $XX,XXX
- Legal and enforcement costs: $X,XXX
- Total potential damages: $XXX,XXX

Security Available:
- Rent deposit: $XX,XXX
- Letter of credit: $XX,XXX
- Total security: $XX,XXX
- Net exposure: $XX,XXX (damages - security)
```

**For Non-Monetary Default:**

```
Cost to Remedy:
- Landlord's cost to cure tenant's breach: $XX,XXX
- Lost rent during cure period: $X,XXX
- Damages to property: $XX,XXX
- Legal costs: $X,XXX
- Total damages: $XX,XXX

Plus:
- Option to terminate and pursue damages as above
```

### Step 6: Assess Landlord Remedies

**Available Remedies (In Order of Severity):**

1. **Notice and Cure Period**
   - Least aggressive
   - Give tenant opportunity to cure
   - Required before other remedies (unless waived in lease)
   - Preserves lease and tenant relationship

2. **Draw on Security**
   - Apply rent deposit to arrears
   - Draw on letter of credit
   - Requires notice to tenant
   - Tenant must replenish security

3. **Perform Obligation and Charge Back**
   - Landlord performs tenant's obligation (e.g., repairs, insurance)
   - Charge cost to tenant as additional rent
   - Collect as you would collect rent

4. **Distress (Seize Tenant's Goods)**
   - Seize tenant's property to satisfy arrears
   - Must follow statutory requirements
   - Can be very effective for monetary defaults
   - May damage tenant relationship

5. **Lockout**
   - Change locks and deny access
   - Only if specifically permitted in lease
   - Subject to statutory restrictions
   - High risk if done improperly

6. **Terminate and Re-Enter**
   - Most severe remedy
   - Ends lease and tenant's right to occupy
   - Pursue damages for breach
   - Mitigation obligation to re-let

7. **Sue for Damages**
   - Can sue without terminating (for ongoing defaults)
   - Can sue after terminating (for all damages)
   - Obtain judgment and enforce
   - Consider collectability

**Recommended Remedy Path:**

```
Step 1: Issue formal default notice (required)
        Deadline: Cure within X days

Step 2: If not cured, draw on security (if available)
        Apply to arrears

Step 3: If still not cured, [choose]:
        Option A: Terminate lease and sue for damages
        Option B: Continue lease and sue for specific defaults
        Option C: Distrain/lockout (if available and appropriate)

Recommended: [Option X] because [rationale]
```

### Step 7: Draft Default Notice

**For Monetary Default:**

```markdown
[DATE]

[TENANT LEGAL NAME]
[ADDRESS]

Dear [TENANT]:

RE: DEFAULT NOTICE - NON-PAYMENT OF RENT
    PREMISES: [ADDRESS]
    LEASE DATED: [DATE]

This letter constitutes formal notice that you are in DEFAULT of the Lease dated [DATE] (the "Lease") between [LANDLORD NAME] ("Landlord") and [TENANT NAME] ("Tenant") for the premises located at [ADDRESS] (the "Premises").

EVENT OF DEFAULT:

Pursuant to Section [X] of the Lease, you have failed to pay rent and additional rent when due. Specifically:

- Base rent for [MONTH(S)]: $XX,XXX (due [DATE(S)])
- Additional rent (operating costs): $X,XXX (due [DATE])
- Late fees: $XXX
- Interest: $XXX
- TOTAL ARREARS: $XX,XXX

CURE PERIOD:

Pursuant to Section [X] of the Lease, you have FIVE (5) DAYS from the date of this notice to cure this default by paying the full amount of arrears. Payment must be received by Landlord on or before [DATE] at [TIME].

PAYMENT INSTRUCTIONS:

Payment must be made by:
[X] Certified cheque or bank draft
[X] Wire transfer to: [BANK DETAILS]
[ ] Other: [SPECIFY]

Payment must be delivered to:
[LANDLORD ADDRESS]
Attention: [NAME]

FAILURE TO CURE:

If you fail to cure this default within the cure period, Landlord will exercise its rights and remedies under the Lease and at law, which may include without limitation:

1. Terminating the Lease and re-entering the Premises
2. Seizing your goods and chattels (distress)
3. Drawing on the security deposit/letter of credit
4. Suing for damages including:
   - All arrears
   - Accelerated rent to end of term
   - Re-letting costs (legal, brokerage, tenant improvements)
   - Legal fees and costs on a substantial indemnity basis

CURRENT DAMAGES:

If the Lease is terminated, Landlord's damages (in addition to current arrears) are estimated at:

- Remaining rent to lease expiry ([X] months): $XXX,XXX
- Re-letting costs: $XX,XXX
- Legal fees: $X,XXX
- TOTAL ESTIMATED DAMAGES: $XXX,XXX

Less: Rent deposit of $XX,XXX
NET DAMAGES: $XXX,XXX

These amounts are in addition to current arrears of $XX,XXX.

RESERVE OF RIGHTS:

Nothing in this notice shall constitute a waiver of Landlord's rights or remedies, all of which are expressly reserved. Time is of the essence.

This notice is without prejudice to Landlord's rights to claim additional amounts and to exercise additional remedies as may be available.

Please govern yourself accordingly and take immediate action to cure this default.

Yours truly,

[LANDLORD NAME]

Per: _________________________
Name: [AUTHORIZED SIGNATORY]
Title: [TITLE]

cc: [Guarantor, if applicable]
    [Landlord's legal counsel]

DELIVERY: [Registered mail / Courier / Personal delivery / Email]
```

**For Non-Monetary Default:**

[Similar format, adapted for specific breach type]

### Step 8: Generate Default Analysis Report

Create comprehensive report in `/workspaces/lease-abstract/Reports/`:
`YYYY-MM-DD_HHMMSS_[tenant_name]_default_analysis.md`

**IMPORTANT**: Use Eastern Time timestamp prefix as per project standards.

**Report includes:**
- Summary of default situation
- **Jurisdiction and applicable legislation analysis**
- **Statutory default provisions and remedies**
- **Lease vs. statute comparison**
- **Statutory compliance warnings**
- Lease default provisions
- Cure period analysis
- Landlord remedies available
- Damage calculations
- Recommended action plan
- Draft default notice
- Timeline and next steps
- Risk assessment

### Step 9: Create Action Timeline

**Default Response Timeline:**

| Date | Action | Responsible | Status |
|------|--------|-------------|--------|
| YYYY-MM-DD | Default occurred | - | Completed |
| YYYY-MM-DD | Default identified | Property Manager | Completed |
| YYYY-MM-DD | Legal review | Legal Counsel | In Progress |
| YYYY-MM-DD | Issue default notice | Landlord | Pending |
| YYYY-MM-DD | Cure deadline | Tenant | Pending |
| YYYY-MM-DD | If not cured: Draw on security | Landlord | Pending |
| YYYY-MM-DD | If not cured: Issue termination notice | Landlord | Pending |
| YYYY-MM-DD | If not cured: Re-enter premises | Landlord | Pending |
| YYYY-MM-DD | If not cured: Commence legal action | Legal Counsel | Pending |

## Important Guidelines

1. **Jurisdictional Research:**
   - ALWAYS identify the jurisdiction first
   - Research current applicable legislation using WebSearch
   - Extract relevant statutory provisions
   - Compare statutory requirements to lease provisions
   - Flag any conflicts or statutory overrides

2. **Statutory Compliance:**
   - Statute overrides conflicting lease provisions
   - Cannot contract out of mandatory statutory protections
   - Follow statutory notice and procedure requirements
   - Be aware of tenant's statutory rights (e.g., relief from forfeiture)
   - Remedies prohibited by statute cannot be exercised even if in lease

3. **Strict Compliance with Lease:**
   - Follow notice requirements exactly
   - Provide correct cure period
   - Use required delivery method
   - Reference specific lease sections

4. **Accurate Damage Calculation:**
   - Be precise with amounts owing
   - Include all charges per lease
   - Calculate interest correctly
   - Estimate future damages conservatively

5. **Strategic Remedy Selection:**
   - Consider tenant's financial position
   - Assess collectability of judgment
   - Weigh costs vs. benefits
   - Consider market conditions for re-letting
   - Preserve options (don't waive rights)

6. **Professional Communication:**
   - Formal business tone
   - Clear statement of facts
   - Specific cure requirements
   - Consequences clearly stated
   - Reserve all rights

7. **Legal Review:**
   - Complex defaults should be reviewed by counsel
   - Ensure statutory compliance
   - Avoid self-help remedies unless clearly permitted
   - Document everything

## Example Usage

```
/default-analysis /path/to/lease_abstract.md "Tenant has not paid rent for 3 months ($15,000 in arrears)"
```

This will:
1. Identify the lease jurisdiction and research applicable commercial tenancies legislation
2. Extract statutory default provisions, remedies, and tenant protections
3. Compare lease provisions to statutory requirements and flag conflicts
4. Analyze the specific default situation
5. Calculate cure periods and potential damages
6. Assess available landlord remedies (contractual and statutory)
7. Draft an appropriate default notice that complies with both lease and statute
8. Generate comprehensive default analysis report with action timeline

Begin the analysis now with the provided lease and default situation.
