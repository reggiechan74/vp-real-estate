# Default Damage Calculator - Methodology

**Version**: 1.0.0
**Date**: 2025-11-06
**Author**: Claude Code

---

## Table of Contents

1. [Overview](#overview)
2. [Legal Framework](#legal-framework)
3. [Accelerated Rent NPV](#accelerated-rent-npv)
4. [Re-leasing Costs](#re-leasing-costs)
5. [Lost Rent During Downtime](#lost-rent-during-downtime)
6. [Mitigation Credits](#mitigation-credits)
7. [Bankruptcy Scenarios](#bankruptcy-scenarios)
8. [Worked Examples](#worked-examples)
9. [Assumptions and Limitations](#assumptions-and-limitations)
10. [References](#references)

---

## Overview

The Default Damage Calculator quantifies landlord damages arising from tenant default under commercial lease agreements. The methodology implements standard real estate finance principles combined with bankruptcy law provisions to estimate:

1. **Immediate Damages** - Unpaid rent, additional rent, late fees
2. **Future Damages** - Present value of remaining lease payments
3. **Re-leasing Costs** - Transaction costs to secure replacement tenant
4. **Mitigation Credits** - Offsets from security deposits and re-leasing
5. **Bankruptcy Recovery** - Expected recovery under insolvency proceedings

All calculations use **present value discounting** to reflect the time value of money.

---

## Legal Framework

### Common Law Damages

Under common law, landlord may recover:

1. **Rent arrears** - All unpaid rent through date of termination
2. **Accelerated rent** - Present value of remaining lease term
3. **Re-leasing costs** - Reasonable costs to mitigate damages
4. **Lost rent** - Vacancy period before re-leasing

**Key Principle**: Landlord has **duty to mitigate** damages by making reasonable efforts to re-lease premises.

### Statutory Framework

**United States**:
- Bankruptcy Code §502(b)(6) - Caps landlord claims in bankruptcy
- State landlord-tenant laws (varies by jurisdiction)

**Canada**:
- *Commercial Tenancies Act*, R.S.O. 1990, c. L.7 (Ontario)
- *Bankruptcy and Insolvency Act*, R.S.C. 1985, c. B-3
- Common law mitigation duty (*Highway Properties Ltd. v. Kelly, Douglas & Co.*)

---

## Accelerated Rent NPV

### Formula

Present value of all remaining lease payments from default date to lease expiry:

```
NPV = Σ(t=1 to T) [PMT / (1 + r)^t]
```

Where:
- `NPV` = Net present value of accelerated rent
- `PMT` = Total monthly payment (base rent + additional rent)
- `r` = Monthly discount rate
- `T` = Remaining months on lease term
- `t` = Payment period (1, 2, 3, ..., T)

### Discount Rate Conversion

Annual discount rate must be converted to monthly:

```
r_monthly = (1 + r_annual)^(1/12) - 1
```

**Example**: 10% annual rate
```
r_monthly = (1.10)^(1/12) - 1 = 0.007974 (0.7974% per month)
```

### Annuity Formula (Simplified)

For constant payments, the sum simplifies to the present value of annuity formula:

```
NPV = PMT × [(1 - (1 + r)^-T) / r]
```

**Derivation**:

Starting with geometric series:
```
S = a + ar + ar² + ... + ar^(n-1)
```

For present value:
```
PV = PMT/(1+r) + PMT/(1+r)² + ... + PMT/(1+r)^T
```

Let `v = 1/(1+r)`, then:
```
PV = PMT × v + PMT × v² + ... + PMT × v^T
PV = PMT × v × (1 - v^T) / (1 - v)
PV = PMT × [1/(1+r)] × [1 - 1/(1+r)^T] / [1 - 1/(1+r)]
PV = PMT × [(1 - (1+r)^-T) / r]
```

### Worked Example

**Given**:
- Monthly rent: $25,000
- Additional rent (monthly): $6,250 (= $75,000/12)
- Total monthly: $31,250
- Remaining months: 36
- Annual discount rate: 10%

**Step 1**: Convert annual rate to monthly
```
r_monthly = (1.10)^(1/12) - 1 = 0.007974
```

**Step 2**: Calculate NPV
```
NPV = 31,250 × [(1 - 1.007974^-36) / 0.007974]
NPV = 31,250 × [(1 - 0.7473) / 0.007974]
NPV = 31,250 × [0.2527 / 0.007974]
NPV = 31,250 × 31.689
NPV = $990,281
```

**Verification**:
- Undiscounted total: $31,250 × 36 = $1,125,000
- NPV: $990,281
- **Discount**: $134,719 (12.0%)

---

## Re-leasing Costs

### Components

#### 1. Tenant Improvements (TI)

Allowance provided to new tenant for build-out:

```
TI_Cost = Rentable_SF × TI_Allowance_per_SF
```

**Typical Values**:
- Industrial: $10-20/SF
- Office (Class A): $40-80/SF
- Office (Class B): $20-40/SF
- Retail: $30-60/SF

#### 2. Leasing Commissions

Broker commission as percentage of total lease value:

```
Commission = (Annual_Rent × Lease_Term_Years) × Commission_Pct
```

**Typical Commission Rates**:
- Industrial: 4-6% of total lease value
- Office: 4-6% of total lease value
- Retail: 5-8% of total lease value

**Common Structure**:
- 3% paid at lease execution
- 2% paid at occupancy
- Total: 5%

#### 3. Legal Fees

Fixed costs for new lease preparation:

```
Legal_Fees = Fixed_Amount
```

**Typical Values**: $5,000-$15,000 depending on complexity

#### 4. Total Re-leasing Cost

```
Total_Cost = TI_Cost + Commission + Legal_Fees
```

### Worked Example

**Given**:
- Rentable area: 50,000 SF
- TI allowance: $15/SF
- Market rent: $7.00/SF ($350,000 annual)
- New lease term: 5 years
- Commission rate: 5%
- Legal fees: $5,000

**Calculation**:
```
TI_Cost    = 50,000 × $15.00 = $750,000
Commission = ($350,000 × 5) × 0.05 = $87,500
Legal      = $5,000
Total      = $750,000 + $87,500 + $5,000 = $842,500
```

---

## Lost Rent During Downtime

### Formula

Simple product of monthly rent and expected vacancy period:

```
Lost_Rent = Monthly_Rent × Downtime_Months
```

### Downtime Assumptions

**Typical Industrial**:
- Small (< 25,000 SF): 3-6 months
- Medium (25,000-100,000 SF): 6-9 months
- Large (> 100,000 SF): 9-18 months

**Typical Office**:
- Small suite (< 5,000 SF): 3-6 months
- Medium floor (5,000-20,000 SF): 6-12 months
- Large multi-floor (> 20,000 SF): 12-24 months

**Factors Affecting Downtime**:
1. Market conditions (tenant vs. landlord market)
2. Property location and quality
3. Size of space
4. Required TI scope
5. Seasonality (Q4 typically slower)

### Worked Example

**Given**:
- Monthly rent: $25,000
- Expected downtime: 6 months

**Calculation**:
```
Lost_Rent = $25,000 × 6 = $150,000
```

---

## Mitigation Credits

### Security Deposit

Direct offset against damages (typically applied first):

```
Credit_Security = Security_Deposit_Amount
```

**Application Order** (typical):
1. Unpaid rent
2. Damages to premises
3. Other lease defaults
4. Balance (if any) returned to tenant

### Re-lease Rent Credit

Present value of new lease rent that overlaps with old lease term.

#### Formula

```
Credit_NPV = PV(New_Rent, from t=D+1 to T)
```

Where:
- `D` = Downtime months
- `T` = Remaining months on old lease
- Overlap period = `T - D` months

#### Calculation Steps

**Step 1**: Determine overlap period
```
Overlap = max(0, Remaining_Months - Downtime_Months)
```

**Step 2**: Calculate PV of overlap rent (starting after downtime)
```
PV_Overlap = New_Monthly_Rent × [(1 - (1+r)^-Overlap) / r]
```

**Step 3**: Discount back to present (account for downtime delay)
```
Credit_NPV = PV_Overlap × (1 + r)^-Downtime
```

### Worked Example

**Given**:
- Old lease remaining: 36 months
- Downtime: 6 months
- Old monthly rent: $25,000
- New monthly rent (market): $30,000
- Discount rate: 10% annual (0.7974% monthly)

**Step 1**: Overlap period
```
Overlap = 36 - 6 = 30 months
```

**Step 2**: PV of 30 months of new rent
```
PV_Overlap = 30,000 × [(1 - 1.007974^-30) / 0.007974]
PV_Overlap = 30,000 × 26.223
PV_Overlap = $786,690
```

**Step 3**: Discount back 6 months to present
```
Credit_NPV = 786,690 × (1.007974)^-6
Credit_NPV = 786,690 × 0.9536
Credit_NPV = $750,180
```

**Interpretation**:
- Landlord re-leases at $30k/month (higher than old $25k)
- New tenant pays for 30 of the 36 remaining months
- Credit offsets future accelerated rent claim

---

## Bankruptcy Scenarios

### §502(b)(6) Statutory Cap (United States)

Bankruptcy Code §502(b)(6) limits landlord claims when trustee rejects lease:

> "the lessor's damages for termination...shall not exceed...the rent reserved by the lease, without acceleration, for the greater of one year, or 15 percent, not to exceed three years, of the remaining term of the lease..."

### Formula

```
Statutory_Cap = max(One_Year_Rent, Fifteen_Pct_Rent)
```

Where:
```
One_Year_Rent = 12 × Total_Monthly_Rent

Fifteen_Pct_Rent = 0.15 × min(Remaining_Months, 36) × Total_Monthly_Rent
```

### Claim Structure

#### 1. Priority Administrative Claim (60 days)

Post-petition rent for actual use before rejection:

```
Priority_Claim = 2 × Total_Monthly_Rent
```

**Recovery Rate**: Typically 100% (administrative expense priority)

#### 2. Unsecured Claim (Capped)

Remaining damages subject to statutory cap:

```
Unsecured_Claim = min(Gross_Damages - Priority_Claim, Statutory_Cap)
```

**Recovery Rate**: Varies widely (0-40%, typically 10-30%)

### Expected Recovery

```
Expected_Recovery = (Priority_Claim × Priority_Rate) +
                    (Unsecured_Claim × Unsecured_Rate)
```

### Worked Example

**Given**:
- Monthly rent: $25,000
- Additional rent (monthly): $6,250
- Total monthly: $31,250
- Remaining months: 36
- Gross damages: $1,957,077
- Priority recovery rate: 100%
- Unsecured recovery rate: 20%

**Step 1**: Calculate priority claim (60 days)
```
Priority_Claim = 2 × $31,250 = $62,500
```

**Step 2**: Calculate statutory cap
```
One_Year_Rent = 12 × $31,250 = $375,000

Fifteen_Pct_Rent = 0.15 × min(36, 36) × $31,250
                 = 0.15 × 36 × $31,250
                 = $168,750

Statutory_Cap = max($375,000, $168,750) = $375,000
```

**Step 3**: Calculate unsecured claim
```
Unsecured_Claim = min($1,957,077 - $62,500, $375,000)
                = min($1,894,577, $375,000)
                = $375,000 (capped)
```

**Step 4**: Expected recovery
```
Expected_Recovery = ($62,500 × 1.00) + ($375,000 × 0.20)
                  = $62,500 + $75,000
                  = $137,500
```

**Step 5**: Expected loss
```
Expected_Loss = $1,957,077 - $137,500 = $1,819,577
```

**Recovery Rate**: 7.0% of gross damages

### Canada: Bankruptcy and Insolvency Act

**Key Differences**:
1. **No statutory cap** on landlord claims (unlike US §502(b)(6))
2. **3-month accelerated rent** recoverable (BIA s. 65.2)
3. **Mitigation duty** still applies
4. Lower priority (ordinary unsecured creditor)
5. Recovery rates typically 5-20% in CCAA proceedings

---

## Worked Examples

### Example 1: Complete Default Calculation

**Scenario**:
- Industrial lease, 36 months remaining
- Tenant fails to pay November rent ($25,000)
- Market conditions: slight uptick (7% market vs. 6% current)

**Inputs**:
```
Property:           123 Industrial Parkway, Mississauga
Tenant:             Acme Distribution Ltd.
Rentable Area:      50,000 SF
Current Rent:       $25,000/month ($6.00/SF)
Additional Rent:    $75,000/year ($6,250/month)
Security Deposit:   $50,000
Remaining Months:   36
Market Rent:        $7.00/SF ($350,000/year, $29,167/month)
TI Allowance:       $15/SF
Commission:         5%
Legal Fees:         $5,000
Downtime:           6 months
Discount Rate:      10% annual
```

**Calculations**:

**1. Immediate Damages**:
```
Unpaid Rent = $25,000
```

**2. Accelerated Rent (NPV)**:
```
Total Monthly = $25,000 + $6,250 = $31,250
r_monthly = 0.007974
NPV = $31,250 × [(1 - 1.007974^-36) / 0.007974]
    = $31,250 × 31.689
    = $990,281
```

**3. Lost Rent (Downtime)**:
```
Lost_Rent = $25,000 × 6 = $150,000
```

**4. Re-leasing Costs**:
```
TI_Cost    = 50,000 × $15 = $750,000
Commission = ($350,000 × 5) × 0.05 = $87,500
Legal      = $5,000
Total      = $842,500
```

**5. Gross Damages**:
```
Gross = $25,000 + $990,281 + $150,000 + $842,500
      = $2,007,781
```

**6. Mitigation Credits**:

Security deposit:
```
Credit_Security = $50,000
```

Re-lease rent (30 months overlap at $29,167/month):
```
PV_Overlap = $29,167 × [(1 - 1.007974^-30) / 0.007974]
           = $29,167 × 26.223
           = $764,868

Credit_NPV = $764,868 × (1.007974)^-6
           = $764,868 × 0.9536
           = $729,367
```

Total credits:
```
Total_Credits = $50,000 + $729,367 = $779,367
```

**7. Net Damages**:
```
Net = $2,007,781 - $779,367 = $1,228,414
```

**8. Bankruptcy Scenario**:
```
Priority_Claim = 2 × $31,250 = $62,500

Statutory_Cap = max(12 × $31,250, 0.15 × 36 × $31,250)
              = max($375,000, $168,750)
              = $375,000

Unsecured_Claim = min($2,007,781 - $62,500, $375,000)
                = $375,000

Expected_Recovery = ($62,500 × 1.00) + ($375,000 × 0.20)
                  = $137,500

Expected_Loss = $2,007,781 - $137,500 = $1,870,281

Recovery_Rate = 6.8%
```

### Example 2: Below-Market Lease (Lower Mitigation)

**Scenario**: Tenant paying $8/SF in market where rent has dropped to $6/SF

**Modified Inputs**:
- Current rent: $33,333/month ($8.00/SF)
- Market rent: $6.00/SF ($300,000/year, $25,000/month)

**Key Changes**:

Re-lease credit is LOWER (market rent < current rent):
```
PV_Overlap = $25,000 × 26.223 = $655,575
Credit_NPV = $655,575 × 0.9536 = $625,077
```

Net damages are HIGHER (less mitigation):
```
Gross = $33,333 + $1,042,000 + $199,998 + $817,500 = $2,092,831
Credits = $50,000 + $625,077 = $675,077
Net = $2,092,831 - $675,077 = $1,417,754
```

**Insight**: Below-market leases have lower mitigation credits, increasing net damages.

### Example 3: Short Remaining Term

**Scenario**: Only 6 months remaining when default occurs

**Modified Inputs**:
- Remaining months: 6
- Downtime: 6 months (same as remaining)

**Key Changes**:

Accelerated rent is MUCH LOWER:
```
NPV = $31,250 × [(1 - 1.007974^-6) / 0.007974]
    = $31,250 × 5.864
    = $183,250
```

Lost rent during downtime:
```
Lost_Rent = $25,000 × 6 = $150,000
```

Re-lease credit is ZERO (no overlap):
```
Overlap = 6 - 6 = 0 months
Credit_NPV = $0
```

Net damages:
```
Gross = $25,000 + $183,250 + $150,000 + $842,500 = $1,200,750
Credits = $50,000 + $0 = $50,000
Net = $1,200,750 - $50,000 = $1,150,750
```

**Insight**: Short remaining terms reduce accelerated rent but eliminate mitigation credit if downtime ≥ remaining term.

---

## Assumptions and Limitations

### Assumptions

1. **Constant Rent**: Assumes flat rent (no escalations, rent steps, or CPI adjustments)
2. **Single Discount Rate**: Uses one rate for all cash flows (reality: different rates for different risk profiles)
3. **Deterministic Downtime**: Fixed downtime estimate (reality: stochastic process)
4. **Market Rent Known**: Assumes perfect knowledge of current market rent
5. **Full Mitigation**: Assumes landlord can re-lease at market rent
6. **No Guarantees**: Doesn't account for personal guarantees or letters of credit
7. **Flat Additional Rent**: Assumes constant additional rent (taxes/opex may vary)

### Limitations

1. **Market Dynamics**: Cannot predict future market rent changes
2. **Lease-Up Risk**: Re-leasing may take longer than estimated
3. **Credit Risk**: New tenant may also default
4. **Legal Costs**: Litigation costs not included in basic calculation
5. **Improvement Condition**: Doesn't account for tenant damage beyond normal wear
6. **Partial Payments**: Doesn't model partial rent payments or payment plans
7. **Bankruptcy Complexity**: Simplified bankruptcy model (doesn't capture all nuances)

### Sensitivity Analysis

**Key Sensitivity Factors**:

| Factor | Change | Impact on Net Damages |
|--------|--------|----------------------|
| Discount Rate | +2% | -5% to -8% |
| Downtime | +3 months | +$75,000 (for $25k/mo rent) |
| Market Rent | -$1/SF | +$150,000 (mitigation credit reduction) |
| TI Allowance | +$5/SF | +$250,000 (for 50k SF) |
| Bankruptcy Recovery | +10% | -$37,500 (unsecured claim only) |

**Recommendation**: Run multiple scenarios (pessimistic/base/optimistic) to bound expected damages.

---

## References

### Legal Authorities

**United States**:
1. 11 U.S.C. §502(b)(6) - Bankruptcy Code landlord claim cap
2. 11 U.S.C. §365 - Executory contract rejection
3. 11 U.S.C. §503(b) - Administrative expenses
4. *In re Joshua Slocum Ltd.*, 922 F.2d 1081 (3d Cir. 1990) - §502(b)(6) interpretation
5. *In re Handy Andy Home Improvement Centers*, 144 F.3d 1125 (7th Cir. 1998)

**Canada**:
1. *Highway Properties Ltd. v. Kelly, Douglas & Co.*, [1971] S.C.R. 562 - Mitigation duty
2. *Bankruptcy and Insolvency Act*, R.S.C. 1985, c. B-3, s. 65.2 - Disclaimer
3. *Commercial Tenancies Act*, R.S.O. 1990, c. L.7 - Ontario landlord remedies
4. *Cavendish Investing Ltd. v. Kasten Realty Advisors Inc.*, 2014 ONSC 4571

### Real Estate Finance

1. Geltner, D., Miller, N., Clayton, J., & Eichholtz, P. (2014). *Commercial Real Estate Analysis and Investments* (3rd ed.). OnCourse Learning.
2. Brueggeman, W. B., & Fisher, J. D. (2015). *Real Estate Finance and Investments* (15th ed.). McGraw-Hill Education.
3. DiPasquale, D., & Wheaton, W. C. (1996). *Urban Economics and Real Estate Markets*. Prentice Hall.

### Bankruptcy

1. Norton, W. L. (2021). *Norton Bankruptcy Law and Practice* (3rd ed.). Thomson Reuters.
2. Tabb, C. J. (2016). *The Law of Bankruptcy* (4th ed.). Foundation Press.
3. Warren, E., & Westbrook, J. L. (2009). *The Law of Debtors and Creditors* (6th ed.). Wolters Kluwer.

### Market Data Sources

1. CoStar - Commercial real estate market data
2. CBRE Research - Market reports and rent surveys
3. Colliers International - Industrial and office market reports
4. Altus Group - Canadian commercial real estate data
5. Real Capital Analytics - Transaction data

---

## Appendix: Mathematical Derivations

### A. Present Value of Annuity

**Objective**: Derive closed-form solution for PV of constant payments

**Setup**:
```
PV = Σ(t=1 to n) [PMT / (1 + r)^t]
```

**Derivation**:

Let `v = 1/(1+r)` (discount factor):
```
PV = PMT·v + PMT·v² + PMT·v³ + ... + PMT·v^n
PV = PMT·v·(1 + v + v² + ... + v^(n-1))
```

Geometric series sum: `1 + x + x² + ... + x^(n-1) = (1 - x^n)/(1 - x)`

Therefore:
```
PV = PMT·v·[(1 - v^n)/(1 - v)]
```

Substitute `v = 1/(1+r)`:
```
PV = PMT·[1/(1+r)]·[(1 - 1/(1+r)^n) / (1 - 1/(1+r))]
```

Simplify denominator:
```
1 - 1/(1+r) = [(1+r) - 1]/(1+r) = r/(1+r)
```

Therefore:
```
PV = PMT·[1/(1+r)]·[(1 - (1+r)^-n) / (r/(1+r))]
PV = PMT·[1/(1+r)]·[(1 - (1+r)^-n)·(1+r)/r]
PV = PMT·[(1 - (1+r)^-n) / r]
```

**Final Formula**:
```
PV = PMT × [(1 - (1 + r)^-n) / r]
```

### B. Delayed Annuity (Mitigation Credit)

**Objective**: PV of annuity starting after delay period

**Setup**:
- Delay: D periods
- Annuity: n payments of PMT
- Discount rate: r

**Solution**:
```
Step 1: Calculate PV at end of delay (t=D)
  PV_D = PMT × [(1 - (1+r)^-n) / r]

Step 2: Discount back to present (t=0)
  PV_0 = PV_D × (1 + r)^-D
```

**Combined Formula**:
```
PV = PMT × [(1 - (1+r)^-n) / r] × (1 + r)^-D
```

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-06
**Next Review**: 2026-05-01
