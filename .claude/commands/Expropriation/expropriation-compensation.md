---
description: Calculate statutory compensation under Ontario Expropriations Act (s.13 market value, s.18 disturbance, s.20 interest)
---

# Expropriation Compensation

Calculate comprehensive statutory compensation under the Ontario Expropriations Act with full compliance for market value (s.13), disturbance damages (s.18), injurious affection (s.18(2)), and interest calculations (s.20).

## Calculator Integration

**Python Calculator**: `.claude/skills/expropriation-compensation-entitlement-analysis/expropriation_compensation_calculator.py`
**Skill**: `expropriation-compensation-entitlement-analysis`
**Related Skills**: `ontario-expropriations-act-statutory-interpretation`, `expropriation-procedural-defect-analysis`
**Shared Utils**: `Shared_Utils/financial_utils.py` (NPV, interest calculations)

## Purpose

Generate complete statutory compensation breakdown for expropriation under the Ontario Expropriations Act, including:
- Market value assessment (s.13 OEA)
- Disturbance damages (s.18 OEA) - moving costs, business losses, professional fees
- Injurious affection to remainder (s.18(2) OEA) - if partial taking
- Interest calculations (s.20 OEA) - from registration to payment
- Compliance validation with OEA statutory requirements

## Usage

```bash
/expropriation-compensation <property-data-path> [--output <report-path>]
```

## Arguments

- `<property-data-path>`: Path to property data JSON file (or PDF to extract from)
- `[--output]`: Optional output path for compensation report (default: timestamped in Reports/)

## Input Format

The property data JSON should include:

```json
{
  "property_details": {
    "address": "123 Main Street, Toronto, ON",
    "legal_description": "Lot 45, Plan 1234",
    "property_type": "commercial",
    "area_sf": 15000,
    "area_acres": 0.34
  },
  "market_value_assessment": {
    "fee_simple_value": 2500000,
    "valuation_date": "2025-01-15",
    "highest_best_use": "commercial_retail",
    "comp_sales_basis": true
  },
  "taking_details": {
    "taking_type": "full_taking",
    "area_taken_sf": 15000,
    "registration_date": "2025-01-15",
    "possession_date": "2025-03-01"
  },
  "disturbance_damages": {
    "moving_costs": 15000,
    "business_losses": {
      "revenue_loss_months": 3,
      "monthly_net_income": 8000,
      "mitigation_recovery_pct": 50
    },
    "professional_fees": {
      "legal": 25000,
      "appraisal": 15000,
      "accounting": 5000
    },
    "fixtures_equipment_loss": 50000
  },
  "injurious_affection": {
    "has_remainder": false,
    "construction_impacts": 0,
    "permanent_impacts": 0
  },
  "financial_parameters": {
    "interest_rate_pct": 6.0,
    "payment_date": "2025-06-01"
  }
}
```

## Workflow

1. **Load and validate input**
   - Read property data from JSON or extract from PDF
   - Validate required fields and OEA compliance
   - Load skill: `expropriation-compensation-entitlement-analysis`

2. **Run calculator**
   ```bash
   cd .claude/skills/expropriation-compensation-entitlement-analysis
   python expropriation_compensation_calculator.py <input-json> --output results.json
   ```

3. **Parse calculator output**
   - Total statutory compensation
   - Component breakdown (s.13, s.18, s.18(2), s.20)
   - Compliance validation results
   - Interest calculations

4. **Generate compensation report**
   - Executive summary with total compensation
   - Detailed breakdown by OEA section
   - Timeline (registration → possession → payment)
   - Interest accrual calculations
   - Statutory compliance checklist

5. **Return formatted report**
   - Save to Reports/ with timestamp prefix
   - Display summary to user
   - Provide calculation details and methodology

## Example

```bash
# Calculate compensation for commercial property
/expropriation-compensation expropriation_samples/commercial_full_taking.json

# With custom output path
/expropriation-compensation expropriation_samples/residential_partial.json --output Reports/2025-11-15_expropriation_123_main.md
```

## Output Format

**Console Summary:**
```
================================================================================
EXPROPRIATION COMPENSATION REPORT
Property: 123 Main Street, Toronto, ON
================================================================================

STATUTORY COMPENSATION BREAKDOWN:
--------------------------------------------------------------------------------
s.13 Market Value:                    $2,500,000
s.18 Disturbance Damages:             $  127,000
  - Moving costs:                     $   15,000
  - Business losses (3 months):       $   12,000
  - Professional fees:                $   45,000
  - Fixtures/equipment:               $   50,000
  - Reinstatement costs:              $    5,000

s.18(2) Injurious Affection:          $        0  (full taking)

s.20 Interest (6.0% from Jan 15):     $   65,833
  - Days: 137 (Jan 15 - Jun 1)
  - Daily rate: $480.55

TOTAL STATUTORY COMPENSATION:         $2,692,833
================================================================================

Timeline:
  Registration Date: January 15, 2025
  Possession Date:   March 1, 2025
  Payment Date:      June 1, 2025
  Interest Period:   137 days

✓ OEA Compliance: All statutory requirements satisfied
✓ Report saved to: Reports/2025-11-15_143022_expropriation_compensation_123_main.md
```

**Detailed Report** (markdown file in Reports/):
- Property identification and legal description
- Market value methodology and comparable sales
- Disturbance damages itemization with supporting documentation
- Injurious affection analysis (if applicable)
- Interest calculations with daily breakdown
- Total compensation summary
- Payment timeline and statutory deadlines
- OEA compliance checklist

## Calculator Output Structure

The calculator returns:
```json
{
  "total_compensation": 2692833,
  "market_value_s13": 2500000,
  "disturbance_damages_s18": 127000,
  "injurious_affection_s18_2": 0,
  "interest_s20": 65833,
  "breakdown": {
    "disturbance_components": {
      "moving_costs": 15000,
      "business_losses": 12000,
      "professional_fees": 45000,
      "fixtures_equipment": 50000,
      "reinstatement": 5000
    }
  },
  "timeline": {
    "registration_date": "2025-01-15",
    "possession_date": "2025-03-01",
    "payment_date": "2025-06-01",
    "interest_days": 137
  },
  "compliance_validation": {
    "s13_compliant": true,
    "s18_compliant": true,
    "s20_compliant": true,
    "all_requirements_met": true
  }
}
```

## Related Commands

- `/partial-taking-analysis` - For partial acquisitions with severance
- `/injurious-affection-analysis` - For detailed construction impact assessment
- `/easement-valuation` - For easement-only acquisitions

## Related Calculators

- `expropriation_compensation_calculator.py` - Main statutory calculator
- `injurious_affection_calculator.py` - For s.18(2) impacts
- `Shared_Utils/financial_utils.py` - Interest and NPV calculations

## Related Skills

- **expropriation-compensation-entitlement-analysis** - Legal framework and statutory requirements
- **ontario-expropriations-act-statutory-interpretation** - OEA compliance and case law
- **expropriation-procedural-defect-analysis** - Process compliance validation

## Notes

- All calculations comply with Ontario Expropriations Act statutory requirements
- Interest calculated from registration date to payment date (s.20 OEA)
- Disturbance damages must be reasonable and caused by expropriation (s.18)
- Market value based on highest and best use at valuation date (s.13)
- Professional fees limited to reasonable amounts for appraisal, legal, accounting
