---
description: Compare an inbound offer against the previous outbound offer to track negotiation movement
---

You are a commercial real estate lease negotiation expert. Your task is to compare an inbound offer (received from the other party) against the previous outbound offer (sent by your side) to identify what's changed, who's moving, and provide strategic recommendations for the next counteroffer.

## Input

The user will provide two arguments:

1. **Inbound Offer**: The offer just received from the other party
2. **Outbound Offer**: The previous offer sent by your side

**Arguments provided**: {{args}}

## Parse Arguments

Extract the two required arguments from {{args}}:
- **First argument**: Path to the inbound offer (e.g., `offers/landlord-counteroffer-02.pdf`)
- **Second argument**: Path to the outbound offer (e.g., `offers/tenant-offer-01.pdf`)

If only one argument is provided, ask the user for the missing offer.

## Determine Perspective

From the file names, context, or document content, determine:
- **Your Side**: Are you representing Landlord or Tenant?
- **Their Side**: Who sent the inbound offer?
- **Round Number**: What negotiation round is this?

Look for clues:
- File names: "landlord-offer", "tenant-counteroffer"
- Document headers: "Tenant's Proposal", "Landlord's Response"
- Signatory: Who is expected to sign this document?

## Process

### Step 1: Load and Parse Both Offers

1. **Load Outbound Offer** (what you sent):
   - Convert to markdown if needed
   - Extract all proposed terms by category
   - Note any positions taken, requests made, or concessions offered

2. **Load Inbound Offer** (what they sent back):
   - Convert to markdown if needed
   - Extract all proposed terms by category
   - Identify their responses to your positions

### Step 2: Categorize Key Deal Terms

Organize terms into these categories for comparison:

**Financial Terms:**
- Base rent (amounts, schedule, escalations)
- Additional rent (operating costs, taxes, CAM, insurance)
- Security deposit / letter of credit
- Rent-free periods / abatement
- Tenant improvement allowance / construction costs
- Rent commencement vs. possession dates

**Term & Renewal:**
- Lease term length
- Commencement and expiry dates
- Renewal options (number, length, rent determination)
- Early termination rights
- Extension options

**Space & Use:**
- Premises description / square footage
- Permitted use / restrictions
- Exclusive use rights
- Expansion rights / ROFR
- Contraction rights

**Construction & Improvements:**
- Landlord's work / obligations
- Tenant's work / obligations
- Allowances and cost-sharing
- Completion deadlines
- Construction management

**Operating Obligations:**
- Operating costs allocation
- Tax responsibilities
- Insurance requirements and minimums
- Maintenance and repair obligations
- Utilities (who pays, separately metered)
- Services provided by landlord

**Flexibility & Control:**
- Assignment rights
- Subletting rights
- Consent requirements (reasonable/absolute)
- Profit sharing on transfers
- Change of control provisions

**Risk Allocation:**
- Indemnification scope
- Insurance coverage levels
- Damage and destruction provisions
- Condemnation provisions
- Force majeure

**Default & Remedies:**
- Default cure periods
- Remedies available
- Limitations of liability
- Dispute resolution

**Special Provisions:**
- Purchase options
- Rights of first refusal / first offer
- Co-tenancy provisions
- Parking rights
- Signage rights
- Hours of operation

### Step 3: Compare Term by Term

For each category and each specific term:

**Identify the Movement:**

1. **Accepted** ✓: Their offer matches your outbound position
2. **Rejected** ✗: Their offer ignores or explicitly rejects your position
3. **Countered** ⟷: They propose a different value/approach
4. **Partially Accepted** ◐: They move toward your position but not all the way
5. **New Issue** ⊕: They raised something not in your outbound offer
6. **Withdrawn** ⊖: Something from your outbound that's not in their inbound

**For Each Changed Term, Capture:**
- **Your Outbound Position**: What you proposed
- **Their Inbound Position**: What they're now proposing
- **Movement Direction**: Who moved (you/them/both/neither)
- **Distance**: How far apart are the positions?
- **Standard Market**: What's typical in the market?
- **Winner**: Who's getting the better position?
- **Strategic Importance**: How important is this term to the overall deal?

### Step 4: Analyze Negotiation Dynamics

**Calculate Concession Scores:**

For each party, track:
- **Number of points won**: Terms that moved your direction
- **Number of points lost**: Terms where you had to concede
- **Number of points unchanged**: Stalemates
- **Value of concessions**: Dollar impact where quantifiable

**Identify Patterns:**
- Are they accepting your financial terms but pushing back on flexibility?
- Are they giving ground on minor issues but holding firm on major ones?
- Are they introducing new issues as trade-offs?
- Are negotiations moving toward agreement or further apart?

**Assess Negotiation Position:**
- **Strong**: You're winning most points, they're making concessions
- **Weak**: They're winning most points, you're making concessions
- **Balanced**: Roughly equal give and take
- **Stalled**: Little to no movement from either side

### Step 5: Identify Deal-Breakers vs. Trading Chips

**Classify Each Open Issue:**

**Deal-Breakers (Likely):**
- Issues where both parties are far apart and neither budging
- Terms that fundamentally change the economics
- Rights/obligations that go to core business model
- Issues explicitly labeled as "must-have" or "unacceptable"

**Trading Chips:**
- Issues where positions are stated but may be negotiable
- Terms where one party has moved slightly (showing flexibility)
- Lower-value items that could be traded for bigger wins
- Areas where market standard provides middle ground

**Quick Wins:**
- Items where positions are very close
- Terms where one party hasn't pushed back
- Administrative or clarification issues

### Step 6: Provide Strategic Analysis

**For Your Side's Next Counteroffer:**

**What to Accept:**
- Terms where they've met your position
- Terms where their position is better than market and acceptable
- Terms where continued fighting isn't worth it strategically

**What to Reject:**
- Terms that are deal-breakers
- Terms far from market standard
- Terms where you have strong leverage

**What to Counter:**
- Terms where there's room for compromise
- Terms where you can propose creative alternatives
- Terms where you're willing to trade for something else

**What to Add:**
- New issues to raise
- Clarifications needed
- Trade proposals ("We'll accept X if you accept Y")

**Leverage Analysis:**
- What leverage points do you have?
- What leverage points do they have?
- How does the market favor your position?
- Time pressure considerations

### Step 7: Output Format

Provide a comprehensive offer comparison report in markdown format:

## Offer Comparison Report Structure

```markdown
# LEASE OFFER COMPARISON REPORT
## [Property Address]

---

## Executive Summary

**Negotiation Status**: [Round X of negotiations]
**Overall Assessment**: [Moving toward agreement / Stalled / Moving apart / Major breakthroughs]
**Your Position**: [Strong / Balanced / Weak]

**Key Movements This Round:**
- [3-5 bullet points on most significant changes]

**Bottom Line**: [1-2 sentences on whether the deal is progressing and overall recommendation]

---

## Offer Information

**Your Side**: [Landlord / Tenant]
**Their Side**: [Tenant / Landlord]

**Outbound Offer (Your Proposal):**
- **Date**: [Date]
- **Document**: [Filename]
- **Round**: [Round number]

**Inbound Offer (Their Response):**
- **Date**: [Date]
- **Document**: [Filename]
- **Round**: [Round number]
- **Turnaround Time**: [Days between offers]

---

## Scorecard Summary

| Category | Terms Changed | You Won | They Won | Compromised | New Issues | Still Open |
|----------|---------------|---------|----------|-------------|------------|------------|
| Financial | X | X | X | X | X | X |
| Term & Renewal | X | X | X | X | X | X |
| Flexibility | X | X | X | X | X | X |
| Risk Allocation | X | X | X | X | X | X |
| **TOTALS** | **X** | **X** | **X** | **X** | **X** | **X** |

**Overall Score**: [Your wins vs. their wins - who's ahead?]

---

## Financial Terms Comparison

### Base Rent

**Your Outbound Position:**
```
[What you proposed for rent - include schedule, escalations]
```

**Their Inbound Position:**
```
[What they're now proposing]
```

**Analysis:**
- **Status**: ✓ Accepted / ✗ Rejected / ⟷ Countered / ◐ Partial / ⊕ New / ⊖ Withdrawn
- **Movement**: [They moved $X toward you / You need to move $X toward them / No movement]
- **Distance**: $[X] per month / [Y]% apart
- **Market Standard**: [What's typical]
- **Winner**: [Landlord / Tenant / Balanced]
- **Strategic Importance**: 🔴 Critical / 🟡 Important / 🟢 Minor
- **$ Impact (NPV)**: $[X] over term

**Recommendation**:
- [ ] Accept their position
- [ ] Counter at $[X]
- [ ] Hold firm at your position
- [ ] Trade for concession on [other term]

---

[Repeat for each financial term: Additional Rent, Security Deposit, Free Rent, TI Allowance, etc.]

---

## Term & Renewal Comparison

[Same structure for term length, renewal options, early termination, etc.]

---

## Space & Use Comparison

[Same structure for permitted use, exclusivity, expansion rights, etc.]

---

## Construction & Improvements Comparison

[Same structure for landlord's work, tenant's work, allowances, etc.]

---

## Operating Obligations Comparison

[Same structure for operating costs, taxes, insurance, maintenance, etc.]

---

## Flexibility & Control Comparison

[Same structure for assignment, subletting, change of control, etc.]

---

## Risk Allocation Comparison

[Same structure for indemnification, insurance limits, casualty, etc.]

---

## Default & Remedies Comparison

[Same structure for cure periods, remedies, dispute resolution, etc.]

---

## Special Provisions Comparison

[Same structure for purchase options, ROFR, co-tenancy, parking, signage, etc.]

---

## New Issues Raised

### Issues They Added (Not in Your Outbound)

1. **[Issue Name]**
   - **Their Position**: [What they're proposing]
   - **Market Standard**: [Is this typical?]
   - **Why They Want It**: [Likely motivation]
   - **Impact on You**: [How it affects your position]
   - **Recommendation**: Accept / Reject / Counter with [alternative]

[Repeat for each new issue]

### Issues You Raised That They Ignored

1. **[Issue Name]**
   - **Your Position**: [What you proposed]
   - **Their Response**: [Silent / Explicitly rejected]
   - **Importance**: [Why you need this]
   - **Recommendation**: [Re-raise / Drop / Modify proposal]

[Repeat for each ignored issue]

---

## Movement Analysis

### Terms Moving Your Direction ✓

| Term | Your Position | Their Movement | Remaining Gap |
|------|---------------|----------------|---------------|
| [Term] | [Value] | [How they moved] | [What's left] |

**Analysis**: [Are they giving ground on your key priorities?]

### Terms Moving Their Direction ✗

| Term | Their Position | Your Movement Needed | Strategic Cost |
|------|----------------|---------------------|----------------|
| [Term] | [Value] | [What they want] | [Impact on you] |

**Analysis**: [Are you losing on key priorities?]

### Stalemates (No Movement) ⊗

| Term | Your Position | Their Position | Gap |
|------|---------------|----------------|-----|
| [Term] | [Value] | [Value] | [Difference] |

**Analysis**: [Which stalemates are deal-breakers vs. tradeable?]

---

## Deal Economics Summary

### Financial Impact of Changes

| Item | Your Proposal | Their Counter | Difference | NPV Impact |
|------|---------------|---------------|------------|------------|
| Base Rent | $X/month | $Y/month | $Z/month | $A |
| Free Rent | X months | Y months | Z months | $B |
| TI Allowance | $X | $Y | $Z | $C |
| Operating Costs | [Your split] | [Their split] | [Difference] | $D |
| **NET IMPACT** | | | | **$[TOTAL]** |

**Bottom Line**: Their inbound offer is [better/worse] than your outbound by approximately **$[X]** over the lease term.

---

## Leverage Analysis

### Your Leverage Points

**Market Leverage:**
- [Vacancy rates, supply/demand, market rents, etc.]

**Property-Specific Leverage:**
- [Property condition, location, tenant mix, etc.]

**Timing Leverage:**
- [Lease expiration, space needs, moving deadlines, etc.]

**Relationship Leverage:**
- [Existing tenant, expansion, renewal, etc.]

**How to Use It**: [Specific strategies]

### Their Leverage Points

**Market Leverage:**
- [What favors their position]

**Property-Specific Leverage:**
- [What gives them advantage]

**Timing Leverage:**
- [Time pressures on your side]

**How They're Using It**: [What you're seeing in their positions]

**How to Counter**: [Specific strategies]

---

## Deal-Breakers vs. Trading Chips

### Likely Deal-Breakers 🔴

**Your Side:**
1. [Term]: [Why this is critical / Walk-away threshold]
2. [Term]: [Why this is critical / Walk-away threshold]

**Their Side (Inferred):**
1. [Term]: [Evidence they won't budge]
2. [Term]: [Evidence they won't budge]

**Strategy**: [How to address these]

### Trading Chips 🔄

**You Can Offer:**
1. [Term]: [What you'd trade] → **In exchange for**: [What you want]
2. [Term]: [What you'd trade] → **In exchange for**: [What you want]

**They Might Offer (Propose):**
1. [Term]: [What they might trade] → **In exchange for**: [What they want]

**Strategy**: [Proposed trade packages]

### Quick Wins ✓

**Issues Close to Resolution:**
1. [Term]: [Small gap, easy to close]
2. [Term]: [Administrative fix]

**Strategy**: [Accept these to build momentum]

---

## Negotiation Patterns Observed

**What They're Doing:**
- [Pattern 1]: [E.g., "Accepting financial terms but fighting flexibility"]
- [Pattern 2]: [E.g., "Introducing new issues as distractions"]
- [Pattern 3]: [E.g., "Making small moves on multiple fronts"]

**What This Tells Us:**
- [Interpretation of their strategy]
- [Their true priorities]
- [Where they'll likely compromise]

**Your Response Strategy:**
- [How to respond effectively]

---

## Strategic Recommendations

### Overall Recommendation

- [ ] **Accept** - This is a good deal, take it
- [ ] **Counter** - Close enough to be worth one more round
- [ ] **Stand Firm** - Don't give more ground, they need to move
- [ ] **Walk Away** - Positions too far apart, not worth pursuing
- [ ] **Request Meeting** - Too complex for document exchange, need discussion

### Recommended Next Steps

**Priority 1 - Must Address:**
1. [Specific action on specific term]
2. [Specific action on specific term]
3. [Specific action on specific term]

**Priority 2 - Should Address:**
1. [Specific action on specific term]
2. [Specific action on specific term]

**Priority 3 - Nice to Have:**
1. [Specific action on specific term]

### Proposed Counteroffer Strategy

**Terms to Accept** ✓
- [Term]: [Why accepting]
- [Term]: [Why accepting]

**Terms to Reject** ✗
- [Term]: [Why rejecting] → **Counter with**: [Alternative]
- [Term]: [Why rejecting] → **Counter with**: [Alternative]

**Terms to Counter** ⟷
- [Term]: **Move from** [your position] **to** [compromise position]
- [Term]: **Move from** [your position] **to** [compromise position]

**New Terms to Introduce** ⊕
- [Term]: [Proposal]
- [Term]: [Proposal]

**Trade Proposals** 🔄
- "We'll accept [X] if you accept [Y]"
- "We'll move to [A] on [term 1] if you move to [B] on [term 2]"

**Cover Letter Key Messages:**
- [Message 1]: [What to emphasize]
- [Message 2]: [What to downplay]
- [Message 3]: [What to frame as fair compromise]

---

## Risk Assessment

### Risks of Accepting Current Offer

**Financial Risks:**
- [Specific risk with $ impact]

**Operational Risks:**
- [Specific risk with operational impact]

**Legal Risks:**
- [Specific risk with legal exposure]

**Market Risks:**
- [Specific risk with market conditions]

### Risks of Continuing to Negotiate

**Time Risk:**
- [Risk of delays, losing other opportunities]

**Relationship Risk:**
- [Risk of souring relationship, losing deal]

**Market Risk:**
- [Risk of market changes affecting leverage]

**Opportunity Cost:**
- [Other deals lost while negotiating this one]

### Recommended Risk Mitigation

- [Specific action to reduce risk]
- [Specific action to reduce risk]

---

## Market Comparison

### How This Offer Compares to Market

| Term | Their Offer | Market Standard | Assessment |
|------|-------------|-----------------|------------|
| Base Rent | $X/SF | $Y/SF | Above/Below/At Market |
| Free Rent | X months | Y months | Better/Worse/Standard |
| TI Allowance | $X/SF | $Y/SF | Better/Worse/Standard |
| Term | X years | Y years | Longer/Shorter/Standard |
| Renewal Options | X options | Y options | More/Less/Standard |

**Overall Market Position**: This offer is [X]% above/below market standards.

**Market Leverage**: [How to use market data in negotiation]

---

## Timeline Considerations

**Proposed Deadlines in Offer:**
- [Deadline 1]: [Date and requirement]
- [Deadline 2]: [Date and requirement]

**Your Constraints:**
- [Constraint 1]: [Date and why]
- [Constraint 2]: [Date and why]

**Recommended Response Timeline:**
- **Respond by**: [Date] - [Rationale]
- **Request meeting by**: [Date] - [If applicable]
- **Target execution**: [Date] - [Goal]

---

## Negotiation Checklist

Before sending your counteroffer:

**Content Verification:**
- [ ] Every term from their inbound is addressed (accepted/rejected/countered)
- [ ] Every term from your outbound is either accepted by them or re-raised
- [ ] New issues are responded to with clear positions
- [ ] All numbers are correct and consistent
- [ ] All dates are accurate and achievable
- [ ] Legal names and property descriptions are accurate

**Strategic Verification:**
- [ ] Concessions align with your priorities (giving on low-value, holding on high-value)
- [ ] Trade proposals are clearly articulated
- [ ] Walk-away issues are protected
- [ ] Quick wins are captured to build momentum
- [ ] Tone is professional and collaborative (not adversarial)
- [ ] Message frames your movements as fair and reasonable

**Process Verification:**
- [ ] Internal approvals obtained for new positions
- [ ] Decision-makers aware of trade-offs
- [ ] Response timeline is reasonable
- [ ] Cover letter drafted explaining key positions
- [ ] Follow-up plan in place (meeting, call, next exchange)

---

## Appendices

### Appendix A: Side-by-Side Offer Comparison

[Complete term-by-term table showing both offers]

### Appendix B: Full Text of Inbound Offer

[Complete text of their offer]

### Appendix C: Full Text of Outbound Offer

[Complete text of your offer]

### Appendix D: Negotiation History

[If there were prior rounds, show the evolution]

---

**END OF COMPARISON REPORT**

Prepared by: Claude Code | Date: [Date] | Round: [X]
```

---

## Quality Checklist

Before presenting the comparison report, verify:

**Loading & Analysis:**
- [ ] Both offers loaded successfully
- [ ] Your side vs. their side correctly identified
- [ ] Round number and sequence established
- [ ] All key terms extracted and categorized

**Comparison:**
- [ ] Every term in your outbound is addressed (accepted/rejected/countered)
- [ ] Every term in their inbound is captured and analyzed
- [ ] Movement direction correctly identified for each term
- [ ] New issues they raised are flagged
- [ ] Issues you raised that they ignored are flagged

**Strategic Analysis:**
- [ ] Scorecard accurately reflects wins/losses/compromises
- [ ] Financial impact calculated (where quantifiable)
- [ ] Leverage points identified for both sides
- [ ] Deal-breakers vs. trading chips classified
- [ ] Negotiation patterns identified
- [ ] Market standards researched and included

**Recommendations:**
- [ ] Clear recommendation provided (accept/counter/stand firm/walk)
- [ ] Specific counteroffer strategy outlined
- [ ] Trade proposals clearly articulated
- [ ] Risk assessment complete
- [ ] Timeline and next steps clear
- [ ] Checklist for next counteroffer provided

---

## Special Considerations

**Understanding Negotiation Tactics:**

1. **Salami Tactics**: They make tiny concessions on many fronts to appear reasonable without giving meaningful ground
   - **Counter**: Focus on key issues, don't get distracted by minor movement

2. **Anchoring**: They start with an extreme position to make their real target seem reasonable
   - **Counter**: Re-anchor with market standards and comparables

3. **Good Cop/Bad Cop**: Different people from their team take different positions
   - **Counter**: Stay focused on the offer terms, not the personalities

4. **Deadline Pressure**: They impose tight deadlines to force concessions
   - **Counter**: Set your own timeline based on real constraints, not artificial ones

5. **Nibbling**: After major issues are resolved, they ask for "one more small thing"
   - **Counter**: Be clear about what's final, resist reopening settled issues

6. **New Issues**: They introduce new issues late in negotiation
   - **Counter**: Distinguish legitimate issues from negotiation tactics

**Reading Between the Lines:**

- **Quick turnaround** = High interest or pressure on them
- **Slow turnaround** = Less interest, shopping other deals, or internal approval issues
- **Accepting most financial terms** = They need the space, financial terms less critical
- **Fighting flexibility clauses** = They want a locked-in tenant/landlord
- **Adding complexity** = They want negotiation leverage or specific business needs
- **Simplifying terms** = They want a quick deal

**When to Request a Meeting:**

Request an in-person or video meeting when:
- Positions are far apart on key issues (better to discuss than exchange documents)
- There are complex trade-offs to explore (real-time discussion helps)
- Relationship is getting adversarial (tone is hard to control in documents)
- Multiple interdependent issues need package solutions
- Creative solutions need brainstorming
- You're close to a deal and want to close momentum

**Cultural Considerations:**

- Some parties prefer very formal, complete proposals
- Others prefer quick iterations on key issues only
- Match their style while maintaining your substance

**Documentation Tips:**

- Keep a negotiation log tracking all offers and movements
- Save all versions with clear dating and round numbers
- Note verbal conversations and meetings that supplement written offers

---

## Begin Analysis

Now proceed to compare the offers provided in the arguments: {{args}}
