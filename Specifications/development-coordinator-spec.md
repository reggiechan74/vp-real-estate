# Development Coordinator Agent - Specification Plan

## Agent Overview

**Name**: `development-coordinator`

**Purpose**: Development project management, build-to-suit leasing, ground lease structuring, and construction coordination for commercial real estate projects. Complements `reggie-chan-vp` by specializing in development-specific leasing, construction management, and entitlement processes.

**Distinct Value**: While `reggie-chan-vp` handles stabilized asset leasing, `development-coordinator` specializes in ground leases, build-to-suit transactions, construction budgeting, development feasibility, entitlements, and coordinating the development process from land acquisition through project completion.

## Core Competencies

### 1. Ground Lease Structuring
- Ground lease vs fee simple acquisition analysis
- Ground rent determination and escalations
- Subordination vs unsubordinated ground leases
- Ground lease valuation and capitalization
- Tenant's leasehold improvements on ground lease
- Ground lease renewal and purchase options

### 2. Build-to-Suit (BTS) Leasing
- BTS lease negotiation and structuring
- Development agreement provisions
- Design-build vs design-bid-build coordination
- Tenant specification requirements
- Cost responsibility allocation (base building vs TI)
- Turnkey delivery vs cost-plus structures

### 3. Construction Management
- Construction schedule development and tracking
- Budget management and cost control
- Change order processing and approval
- Quality control and inspections
- Contractor coordination and oversight
- Substantial completion certification

### 4. Work Letter Development
- Tenant improvement specifications
- Construction standards and materials
- Allowable vs excluded costs
- Construction timeline and milestones
- Approval processes and authorities
- Landlord work vs tenant work demarcation

### 5. Entitlements and Permitting
- Zoning analysis and variance applications
- Building permit acquisition
- Site plan approval coordination
- Environmental clearances
- Development agreement negotiations with municipalities
- Conditional use permits and special approvals

### 6. Development Feasibility
- Highest and best use analysis
- Development pro forma modeling
- Residual land value calculations
- Financing structure evaluation
- Risk assessment and mitigation
- Go/no-go decision support

## Division of Labor: Claude Code vs Python

**CRITICAL PRINCIPLE**: Use the right tool for the right job to maximize efficiency and leverage Claude Code's native capabilities.

### Claude Code Responsibilities (Document Analysis & Research)
Claude Code should handle **all document reading, data extraction, and research tasks**:

✅ **Document Reading**: Use Claude Code's native multimodal capabilities to read development documents
  - Ground lease agreements, BTS lease agreements, development agreements
  - Construction contracts, architectural plans, specifications
  - Permit applications, zoning ordinances, environmental reports
  - Work letters, tenant improvement scopes, contractor bids
  - More efficient than Python PDF libraries - direct visual understanding of plans, drawings, tables

✅ **Web Research**: Use WebSearch and WebFetch tools for development intelligence
  - Construction cost benchmarks, contractor pricing, material costs
  - Zoning codes, municipal permit requirements, development fees
  - Market comparable rents for feasibility analysis
  - Environmental regulations, building code requirements

✅ **Data Extraction**: Extract key data from development documents
  - Ground rent schedules, escalation clauses, purchase options
  - Construction budgets, cost breakdowns, payment schedules
  - Construction schedules, milestones, completion dates
  - TI allowances, cost caps, allowable expenses
  - Permit timelines, approval requirements, fee schedules

✅ **Data Normalization**: Transform extracted data into structured JSON for Python
  - Standardize units ($/SF, cost categories, schedule durations)
  - Validate addresses, legal descriptions, zoning classifications
  - Create consistent data schemas for downstream calculations
  - Handle missing data, estimate ranges, flag uncertainties

✅ **Workflow Orchestration**: Coordinate multi-step development analyses
  - Invoke slash commands, trigger Python calculations, synthesize outputs
  - Manage dependencies between feasibility → design → construction → stabilization
  - Handle errors, iterate on assumptions, generate final reports

### Python Responsibilities (Quantitative Analysis & Scheduling)
Python should **only** be used for computational tasks requiring numerical/algorithmic libraries:

✅ **Financial Calculations**: Development pro formas, NPV, IRR, residual land value
  - Leverage NumPy, Pandas for multi-period cash flow modeling
  - Development yield, profit margin, equity multiple calculations
  - Construction financing models (draw schedules, interest calculations)

✅ **Schedule Analysis**: CPM/PERT scheduling, critical path analysis
  - Use NetworkX for graph-based schedule networks
  - Float calculations, schedule compression analysis
  - Earned value analysis, schedule variance calculations

✅ **Cost Modeling**: Construction budget analysis, cost allocation, variance analysis
  - TI allowance calculations, over-allowance amortization
  - Cost escalation modeling, contingency analysis
  - Change order impact analysis

✅ **Optimization**: Ground lease vs fee simple comparison, scenario analysis
  - NPV comparison of alternatives (ground lease vs purchase)
  - Sensitivity analysis on development pro formas
  - Highest and best use scenario ranking

✅ **Data Visualization**: Gantt charts, cost curves, sensitivity charts
  - Construction schedule visualizations
  - Development pro forma waterfalls
  - Cost variance charts

### Anti-Patterns to Avoid

❌ **DO NOT use Python for document extraction**
  - Development documents (leases, contracts, plans) have complex layouts
  - Claude Code's multimodal vision is superior for reading architectural drawings, site plans, specifications
  - Example: Don't write PDF extraction code for ground lease agreements when Claude can read them directly

❌ **DO NOT use Python for web research**
  - Claude Code has WebSearch and WebFetch tools
  - Researching zoning codes, permit requirements, construction costs should use Claude's tools
  - Example: Don't write web scrapers for municipal permit websites when Claude can WebFetch

❌ **DO NOT use Python for simple data transformations**
  - Claude Code can normalize addresses, convert units, standardize cost categories
  - Reserve Python for complex calculations (CPM scheduling, multi-period cash flows)
  - Example: Don't write Python to convert $/SF to total cost; Claude can do this

❌ **DO NOT duplicate functionality**
  - If existing calculators handle NPV/IRR (Shared_Utils), use them
  - Don't reimplement financial calculations that exist elsewhere
  - Python adds development-specific logic on top of existing utilities

### Workflow Pattern: Claude → Python → Claude

**Optimal pattern for development analyses**:

1. **Claude Code**: Extract data from documents and research
   - Read ground lease agreements, BTS contracts, construction documents
   - Research zoning codes, permit requirements, construction costs via WebSearch
   - Extract key terms and normalize into structured JSON

2. **Python**: Perform quantitative analysis
   - Load normalized JSON data
   - Run development calculations (pro formas, CPM schedules, cost models)
   - Generate visualizations (Gantt charts, cost curves)
   - Export results JSON

3. **Claude Code**: Synthesize results into recommendations
   - Interpret Python outputs, add development context
   - Combine quantitative results with qualitative risk assessment
   - Generate markdown reports with visualizations
   - Present findings with go/no-go recommendations

**Example**: Ground lease vs fee simple decision
```
1. Claude reads ground lease agreement.pdf → extracts ground rent, term, escalations → creates ground_lease_terms.json
2. Claude researches comparable land sales → creates land_market_data.json
3. Python runs ground_lease_vs_fee_simple() → calculates NPV of both options → generates comparison_results.json
4. Claude interprets results → writes recommendation memo with financing implications and strategic considerations
```

### Implementation Implications

- **Agent prompt**: Emphasize this division in the agent's core instructions
- **Skill design**: Skills should guide Claude to extract data, then invoke Python for calculations
- **Python modules**: All .py files consume JSON inputs, produce JSON outputs - NO document parsing libraries
- **Testing**: Validate that document reading happens in Claude, Python only gets JSON
- **Documentation**: Clearly show which tool handles each step in examples

---

## Required Claude Code Skills

### Priority 1: Essential Skills (Create First)

#### 1. **ground-lease-structuring-expert**

**Description**: Expert in ground lease agreements where tenant leases land and constructs improvements. Use when analyzing ground lease vs fee simple acquisition, structuring ground rent and escalations, evaluating subordination provisions, calculating leasehold vs fee simple value, negotiating ground lease purchase options, or advising on unsubordinated ground lease structures. Key terms include ground lease, ground rent, leasehold interest, fee simple, subordination, unsubordinated ground lease, leasehold improvements, ground lease subordination, residual land value, ground lease renewal.

**What it does**:
- Analyzes ground lease vs fee simple economics
- Structures ground rent (fixed, percentage of revenue, percentage of land value)
- Evaluates subordination implications for financing
- Calculates present value of ground lease obligations
- Structures purchase options and renewal terms
- Advises on lender requirements for ground lease financing

**Python functions needed**:
```python
# ground_lease_analysis.py
def ground_lease_vs_fee_simple(land_price, ground_rent, term, discount_rate)
def calculate_ground_rent(land_value, cap_rate, escalation_method)
def leasehold_value(fee_simple_value, ground_lease_pv, improvements_value)
def subordination_impact_analysis(loan_terms, ground_lease_terms)
def ground_lease_purchase_option(land_value_growth, option_terms)
def unsubordinated_lease_financing(ltv_max, dscr_requirements)
```

Residual land value modeling is centralized in `development_feasibility.py`; ground lease workflows call that module instead of duplicating calculations.

**JSON I/O Contract**:
- **Input (from Claude)** – single JSON document with explicit units:
```json
{
  "land_price": 10000000,
  "ground_lease_terms": {
    "rent_schedule": [
      {"year": 1, "rent": 500000},
      {"year": 2, "rent": 510000}
    ],
    "term_years": 75,
    "escalation": {"type": "fixed", "rate": 0.02}
  },
  "fee_simple_terms": {
    "acquisition_price": 10000000,
    "capex": 2500000
  },
  "discount_rate": 0.085,
  "financing": {"ltv": 0.65, "interest_rate": 0.065}
}
```
- **Output (to Claude)** – JSON only, no narrative text:
```json
{
  "module": "ground_lease_analysis",
  "version": "1.0",
  "ground_lease_vs_fee_simple": {
    "ground_lease_npv": -4120000,
    "fee_simple_npv": -3900000,
    "recommendation": "fee_simple"
  },
  "subordination_impact_analysis": {
    "subordinated_ltv": 0.7,
    "unsubordinated_ltv": 0.52,
    "debt_capacity_delta": -3250000
  }
}
```

---

#### 2. **build-to-suit-expert**

**Description**: Expert in build-to-suit lease agreements where landlord constructs custom building for tenant. Use when negotiating BTS lease terms, structuring development agreements, allocating construction cost responsibility, defining tenant specifications and approval rights, evaluating turnkey vs cost-plus delivery, negotiating completion guarantees, or structuring long-term BTS leases. Key terms include build-to-suit, BTS lease, development agreement, tenant specifications, turnkey delivery, cost-plus, base building cost, TI allowance, substantial completion, punch list, completion guarantee, design-build.

**What it does**:
- Structures BTS lease economics (rent tied to actual costs vs market)
- Defines scope of landlord's work vs tenant's work
- Creates approval processes for design and construction
- Allocates cost overrun responsibility
- Structures delivery schedules with liquidated damages
- Coordinates design-build vs design-bid-build approaches

**Python functions needed**:
```python
# build_to_suit_analysis.py
def bts_rent_calculation(land_cost, hard_costs, soft_costs, return_requirement)
def turnkey_vs_cost_plus_comparison(estimated_costs, contingency, risk_allocation)
def completion_schedule_analysis(milestones, liquidated_damages, tenant_impact)
def cost_allocation_model(base_building, shell, ti_work, responsibility_matrix)
def bts_vs_speculative_economics(bts_terms, spec_lease_terms, market_conditions)
def design_approval_timeline(design_phases, approval_cycles, construction_schedule)
```

**JSON I/O Contract**:
- **Input** – normalized BTS payload with consistent cost units ($) and durations (days):
```json
{
  "project_id": "BTS-DC-1001",
  "site": {"land_cost": 2000000, "building_sf": 100000},
  "costs": {
    "hard_costs": 8000000,
    "soft_costs": 1200000,
    "contingency_pct": 0.08
  },
  "tenant_requirements": {
    "spec_level": "Class A",
    "delivery_type": "turnkey"
  },
  "schedule": {
    "milestones": [
      {"name": "Foundation", "duration_days": 45},
      {"name": "TCO", "duration_days": 300}
    ],
    "liquidated_damages_per_day": 2000
  },
  "return_requirement": 0.07
}
```
- **Output** – single JSON document summarizing calculations per function:
```json
{
  "module": "build_to_suit_analysis",
  "version": "1.0",
  "bts_rent_calculation": {
    "required_noi": 791000,
    "rent_psf": 7.91,
    "market_spread_psf": -0.59
  },
  "turnkey_vs_cost_plus_comparison": {
    "turnkey_rent_psf": 8.25,
    "cost_plus_rent_psf": 7.60,
    "risk_owner": {
      "turnkey": "landlord",
      "cost_plus": "tenant"
    }
  },
  "completion_schedule_analysis": {
    "critical_milestones": ["Foundation", "TCO"],
    "ld_exposure": 42000
  }
}
```

---

#### 3. **construction-management-expert**

**Description**: Expert in construction project management, scheduling, budgeting, and quality control for commercial real estate development. Use when developing construction schedules, tracking project budgets, managing change orders, coordinating contractor activities, monitoring quality control, analyzing critical path, or evaluating construction delays and impacts. Key terms include CPM schedule, critical path, change order, construction budget, cost overrun, substantial completion, punch list, progress payments, contractor coordination, schedule acceleration, liquidated damages.

**What it does**:
- Creates and tracks CPM (Critical Path Method) schedules
- Monitors construction budget vs actual with variance analysis
- Evaluates change order impacts on cost and schedule
- Identifies critical path activities and float
- Analyzes schedule delays and acceleration options
- Tracks progress payments and lien waivers

**Python functions needed**:
```python
# construction_management.py
def critical_path_analysis(activities, dependencies, durations)
def schedule_variance_analysis(baseline_schedule, actual_progress, current_date)
def change_order_impact(base_budget, base_schedule, change_order_details)
def progress_payment_calculation(completed_work, retention_percentage, prior_payments)
def schedule_acceleration_cost(current_schedule, target_completion, acceleration_rates)
def substantial_completion_checklist(punch_list_items, priority_weights)
def construction_budget_tracker(budget_items, committed_costs, actual_costs)
def earned_value_analysis(planned_value, earned_value, actual_cost)
```

**JSON I/O Contract**:
- **Input** – CPM-ready JSON with ISO dates and duration units specified:
```json
{
  "project_id": "IND-35",
  "activities": [
    {"id": "A", "name": "Site Work", "duration_days": 30},
    {"id": "B", "name": "Foundation", "duration_days": 45, "predecessors": ["A"]}
  ],
  "baseline_start": "2024-01-01",
  "current_date": "2024-03-15",
  "actual_progress": [
    {"activity_id": "A", "percent_complete": 100},
    {"activity_id": "B", "percent_complete": 40}
  ],
  "budget": {
    "planned_value": 5200000,
    "earned_value": 4300000,
    "actual_cost": 4700000
  },
  "acceleration_targets": {"target_completion": "2024-12-15"}
}
```
- **Output** – JSON containing schedule + cost diagnostics and optional visualization payloads:
```json
{
  "module": "construction_management",
  "critical_path_analysis": {
    "critical_path": ["A", "B", "C", "F", "I"],
    "project_duration_days": 386,
    "float_summary": {"non_critical": [{"activity_id": "H", "total_float_days": 12}]}
  },
  "schedule_variance_analysis": {
    "baseline_completion": "2024-12-01",
    "forecast_completion": "2024-12-22",
    "variance_days": 21
  },
  "earned_value_analysis": {
    "cpi": 0.91,
    "spi": 0.83,
    "estimate_at_completion": 5725275
  }
}
```

---

#### 4. **work-letter-expert**

**Description**: Expert in work letter agreements specifying tenant improvement construction scope, standards, and responsibilities. Use when drafting work letters, defining landlord vs tenant construction responsibilities, establishing TI allowances and allowable costs, setting construction standards and materials, creating approval processes for tenant plans, structuring over-allowance rent adjustments, or coordinating construction schedules. Key terms include work letter, tenant improvements, TI allowance, base building, shell condition, landlord's work, tenant's work, construction standards, allowable costs, over-allowance, substantial completion, as-built drawings.

**What it does**:
- Defines scope of landlord's work (base building, shell, core improvements)
- Structures TI allowances ($/SF, total dollar cap, allowable cost categories)
- Establishes construction standards (materials, systems, finishes)
- Creates approval workflows for tenant construction documents
- Allocates responsibility for design costs, permits, and fees
- Defines punch list and completion procedures

**Python functions needed**:
```python
# work_letter_analysis.py
def ti_allowance_calculator(space_size, allowance_per_sf, cost_categories)
def over_allowance_rent_adjustment(excess_costs, amortization_term, interest_rate)
def landlord_tenant_work_allocation(total_scope, responsibility_matrix)
def construction_schedule_coordination(landlord_milestones, tenant_milestones, dependencies)
def allowable_cost_verification(submitted_costs, allowable_categories, caps)
def ti_amortization_schedule(ti_investment, lease_term, interest_rate)
def shell_vs_turnkey_cost_comparison(shell_costs, turnkey_costs, tenant_requirements)
```

**JSON I/O Contract**:
- **Input** – normalized tenant improvement summary (currency in USD, area in SF):
```json
{
  "premises": {"suite": "200", "size_sf": 10000},
  "allowances": {
    "base_allowance_psf": 30,
    "tenant_request_psf": 50,
    "allowable_categories": ["HVAC", "Electrical", "Drywall"]
  },
  "lease_terms": {"amortization_term_years": 7, "interest_rate": 0.06},
  "responsibility_matrix": {
    "landlord": ["base_building", "core"],
    "tenant": ["specialty_fixtures"]
  },
  "submitted_costs": [
    {"category": "HVAC", "amount": 120000},
    {"category": "Furniture", "amount": 40000}
  ]
}
```
- **Output** – JSON with allowable costs, over-allowance rent impact, and schedule coordination data:
```json
{
  "module": "work_letter_analysis",
  "ti_allowance_calculator": {
    "base_allowance_total": 300000,
    "tenant_budget_total": 500000,
    "over_allowance": 200000
  },
  "over_allowance_rent_adjustment": {
    "annual_payment": 34500,
    "rent_increase_psf": 3.45
  },
  "allowable_cost_verification": {
    "approved_costs": 120000,
    "flagged_costs": [
      {"category": "Furniture", "amount": 40000, "reason": "excluded_category"}
    ]
  }
}
```

---

### Priority 2: Supporting Skills (Create After Priority 1)

#### 5. **entitlement-permitting-expert**

**Description**: Expert in land use entitlements, zoning analysis, and development permitting processes. Use when analyzing zoning compliance, obtaining building permits, navigating site plan approvals, securing conditional use permits, negotiating development agreements with municipalities, obtaining environmental clearances, or evaluating entitlement risk and timelines. Key terms include zoning, variance, conditional use permit, site plan approval, building permit, development agreement, environmental clearance, FAR (floor area ratio), height restrictions, parking requirements, setbacks, density.

**What it does**:
- Analyzes zoning compliance and identifies variances needed
- Maps entitlement process with timeline and risk assessment
- Evaluates conditional use permit requirements
- Coordinates environmental review (Phase I/II, Environmental Assessment)
- Structures development agreements with municipalities
- Assesses impact fees and exactions

**Python functions needed**:
```python
# entitlement_analysis.py
def zoning_compliance_checker(site_characteristics, zoning_requirements)
def entitlement_timeline_model(permit_types, approval_sequences, typical_durations)
def development_fee_calculator(project_size, fee_schedules, impact_categories)
def far_analysis(site_area, allowable_far, proposed_building_size)
def parking_requirement_analysis(use_types, parking_ratios, shared_parking_factors)
def variance_probability_assessment(variance_type, planning_policies, precedents)
def environmental_clearance_scope(site_conditions, project_type, regulatory_requirements)
```

**JSON I/O Contract**:
- **Input** – jurisdiction-aware payload referencing zoning code citations and durations in days:
```json
{
  "site": {
    "address": "123 Commerce Dr",
    "jurisdiction": "Austin, TX",
    "acreage": 4.2,
    "zoning": "LI"
  },
  "proposed_program": {
    "use": "industrial",
    "density_far": 0.55,
    "parking_ratio": 1.5
  },
  "zoning_requirements": {
    "max_far": 0.6,
    "min_parking_ratio": 1.25,
    "height_limit_ft": 60
  },
  "permits_needed": [
    {"name": "Site Plan", "duration_days": 120},
    {"name": "Building Permit", "duration_days": 60, "dependencies": ["Site Plan"]}
  ],
  "environmental": {"phase_required": "Phase I", "known_conditions": ["former_fill"]}
}
```
- **Output** – JSON summarizing compliance gaps and entitlement schedule:
```json
{
  "module": "entitlement_analysis",
  "zoning_compliance_checker": {
    "compliant": true,
    "variances_required": [],
    "notes": "Height within limit, FAR below threshold"
  },
  "entitlement_timeline_model": {
    "critical_sequence": ["Site Plan", "Building Permit", "TCO"],
    "duration_days": 210,
    "risk_adjusted_duration_days": 252,
    "risk_factors": [{"permit": "Site Plan", "probability": 0.3, "impact_days": 30}]
  },
  "environmental_clearance_scope": {
    "required_actions": ["Phase I ESA"],
    "escalation_trigger": "Evidence of contamination"
  }
}
```

---

#### 6. **development-feasibility-expert**

**Description**: Expert in development feasibility analysis, highest and best use evaluation, and development pro forma modeling. Use when analyzing development opportunities, calculating residual land value, modeling development pro formas, evaluating alternative development scenarios, assessing development risk, calculating development yields and returns, or structuring development financing. Key terms include development pro forma, residual land value, highest and best use, development yield, construction cost, soft costs, stabilized NOI, development timeline, construction financing, merchant builder, value-add development.

**What it does**:
- Builds comprehensive development pro formas (land through stabilization)
- Calculates residual land value (what land is worth given development economics)
- Evaluates multiple development scenarios (office vs industrial, heights, densities)
- Models construction and permanent financing structures
- Assesses development risk and sensitivity analysis
- Calculates development yields (yield on cost, profit margins)

**Python functions needed**:
```python
# development_feasibility.py
def development_pro_forma(land_cost, hard_costs, soft_costs, timeline, financing_structure)
def residual_land_value(stabilized_value, development_costs, developer_profit_requirement)
def highest_best_use_analysis(site_attributes, zoning, market_demand, development_scenarios)
def development_yield_calculation(stabilized_noi, total_development_cost)
def construction_financing_model(draw_schedule, interest_rate, origination_fees, term)
def development_irr(cash_flows_by_period, land_acquisition_date, stabilization_date)
def sensitivity_analysis_development(base_pro_forma, variable_ranges)
def merchant_builder_model(development_costs, hold_period, exit_cap_rate, leverage)
```

**JSON I/O Contract**:
- **Input** – scenario bundle with explicit timeline and financing assumptions:
```json
{
  "project_id": "IND-Lot12",
  "land_cost": 2500000,
  "hard_costs": [
    {"category": "Site Work", "amount": 900000},
    {"category": "Shell", "amount": 5500000}
  ],
  "soft_costs": 0.18,
  "timeline": {
    "periods_months": [
      {"phase": "Pre-Dev", "months": 6},
      {"phase": "Construction", "months": 12},
      {"phase": "Lease-Up", "months": 6}
    ],
    "stabilization_date": "2026-06-30"
  },
  "financing_structure": {
    "ltv": 0.6,
    "interest_rate": 0.07,
    "draw_schedule": [0.1, 0.2, 0.3, 0.25, 0.15]
  },
  "revenue_assumptions": {
    "noi_at_stabilization": 1200000,
    "exit_cap_rate": 0.055
  },
  "scenario_tests": {
    "rent_psf": {"min": 9, "base": 10, "max": 11},
    "cap_rate": {"min": 0.051, "base": 0.055, "max": 0.06}
  }
}
```
- **Output** – JSON summarizing pro forma, residual, IRR, and sensitivity tables:
```json
{
  "module": "development_feasibility",
  "development_pro_forma": {
    "sources_uses": {
      "sources": {"debt": 7800000, "equity": 5200000},
      "uses": {"land": 2500000, "hard_costs": 6400000, "soft_costs": 1152000, "contingency": 326000}
    },
    "cash_flow": [
      {"period": "Month 0", "equity": -5200000},
      {"period": "Month 24", "sale_proceeds": 21818182}
    ]
  },
  "residual_land_value": {
    "residual_value": 2860000,
    "assumed_profit_margin": 0.20
  },
  "development_irr": {
    "project_irr": 0.23,
    "equity_multiple": 2.1
  },
  "sensitivity_analysis_development": [
    {"metric": "rent_psf", "value": 9, "project_irr": 0.18},
    {"metric": "rent_psf", "value": 11, "project_irr": 0.27}
  ]
}
```

---

## Existing Calculators Integration

### Leverage Existing:
1. **Eff_Rent_Calculator** - For stabilized property analysis
   - Agent will add development phase modeling leading to stabilization

2. **IFRS16_Calculator** - For lease accounting
   - Agent will add ground lease accounting treatment

3. **Financial_Utils** - For NPV, IRR calculations
   - Agent will use for development pro forma analysis

4. **Option_Valuation** - For real options
   - Agent will add development option value (option to develop, option to defer)

### New Python Modules to Create:

```
/Development_Management/
├── __init__.py
├── ground_lease_analysis.py        # Ground lease economics, subordination
├── build_to_suit_analysis.py       # BTS lease structuring, delivery models
├── construction_management.py      # CPM scheduling, budget tracking, change orders
├── work_letter_analysis.py         # TI allowances, cost allocation, over-allowance
├── entitlement_analysis.py         # Zoning, permits, approvals, timelines
├── development_feasibility.py      # Pro formas, residual land value, HBU
└── Tests/
    ├── test_ground_lease_analysis.py
    ├── test_build_to_suit_analysis.py
    ├── test_construction_management.py
    ├── test_work_letter_analysis.py
    ├── test_entitlement_analysis.py
    └── test_development_feasibility.py
```

---

## Agent Architecture

### Agent File Structure

```markdown
---
name: development-coordinator
description: Development project management, build-to-suit leasing, and construction coordination specialist. Use when structuring ground leases, negotiating build-to-suit agreements, managing construction schedules and budgets, coordinating tenant improvements, navigating entitlements and permitting, or evaluating development feasibility. Expert in ground lease subordination, BTS lease economics, construction management, and development pro formas.
tools: Read, Glob, Grep, Write, Bash, SlashCommand, TodoWrite, Skill
model: inherit
---

# Development Coordinator Sub-Agent

You are a senior development manager specializing in commercial real estate development projects...

## Core Responsibilities

### Ground Lease Structuring
- Analyze ground lease vs fee simple economics
- Structure ground rent and escalations
- Evaluate subordination implications
- Negotiate ground lease terms and purchase options

### Build-to-Suit Coordination
- Structure BTS lease agreements
- Coordinate design-build process
- Allocate cost responsibilities
- Manage delivery schedules and completion

### Construction Management
- Develop and track construction schedules (CPM)
- Monitor budgets and process change orders
- Coordinate contractor activities
- Ensure quality control and substantial completion

### Work Letter Development
- Draft tenant improvement specifications
- Structure TI allowances and allowable costs
- Define landlord vs tenant work scope
- Coordinate construction approvals

### Entitlements and Permitting
- Navigate zoning and land use approvals
- Coordinate building permit process
- Obtain environmental clearances
- Negotiate development agreements

### Development Feasibility
- Model development pro formas
- Calculate residual land value
- Evaluate highest and best use
- Assess development risk and returns

## Specialized Skills Available
- ground-lease-structuring-expert
- build-to-suit-expert
- construction-management-expert
- work-letter-expert
- entitlement-permitting-expert
- development-feasibility-expert

## Workflow Integration

**Follow the Claude → Python → Claude pattern**:

1. **Extract & Research** (Claude Code):
   - Read development documents using Read tool (ground leases, BTS agreements, construction contracts, permits, plans, specifications) - DO NOT use Python PDF libraries
   - Research zoning codes, permit requirements, construction costs using WebSearch/WebFetch - DO NOT use Python web scraping
   - Extract key terms, schedules, budgets, specifications from documents
   - Normalize extracted data into structured JSON for Python consumption
   - Validate data quality, standardize units ($/SF, durations, cost categories)

2. **Calculate & Analyze** (Python):
   - Load normalized JSON data
   - Invoke relevant expert skill for guidance on analysis approach
   - Execute quantitative calculations using Development_Management modules:
     - Ground lease NPV analysis, subordination impact modeling
     - BTS rent calculation, turnkey vs cost-plus comparison
     - CPM scheduling, critical path analysis, schedule compression
     - TI allowance calculations, over-allowance amortization
     - Development pro formas, residual land value, IRR calculations
   - Generate visualizations (Gantt charts, pro forma waterfalls, cost curves)
   - Export results as JSON - DO NOT generate narrative documents in Python

**Visualization Output Contract**:
- Python returns a single JSON object with optional `tables` and `visualizations` arrays. Every visualization declares how Claude should render it:
```json
{
  "visualizations": [
    {
      "id": "gantt-foundation-delay",
      "type": "gantt_dataset",
      "description": "Baseline vs current schedule",
      "data": {
        "activities": [
          {"name": "Foundation", "baseline_start": "2024-02-01", "baseline_finish": "2024-03-17", "forecast_finish": "2024-04-07"}
        ]
      }
    },
    {
      "id": "proforma-waterfall",
      "type": "image_base64",
      "description": "Equity vs debt sources",
      "encoding": "base64_png",
      "data": "iVBORw0KGgoAAAANSUhEUg..."
    }
  ]
}
```
- Claude either draws charts from datasets (`gantt_dataset`, `scatter_dataset`, etc.) or embeds pre-rendered base64 PNG/SVG blobs. No narratives or PDFs should originate from Python.

3. **Synthesize & Document** (Claude Code):
   - Interpret Python calculation results
   - Add development context, risk assessment, qualitative factors
   - Combine with existing calculator outputs if relevant (e.g., use `/effective-rent` for stabilized analysis)
   - Generate markdown reports, term sheets, work letters with embedded visualizations
   - Provide actionable recommendations with supporting analysis

4. **Iterate & Track**:
   - Use TodoWrite to track project milestones, approvals, pending tasks
   - Document assumptions, data sources, methodology
   - Update construction schedules, budgets, pro formas as project evolves
   - Coordinate with other agents (reggie-chan-vp for stabilized leasing, financial-analyst for risk analysis, market-intelligence for feasibility inputs)

**Integration with existing calculators**:
- Use `Shared_Utils` for NPV/IRR calculations (don't duplicate)
- Use `/effective-rent` for stabilized property analysis post-development
- Use financial-analyst for sensitivity analysis on development pro formas
- Use market-intelligence for market rent inputs to feasibility analysis
```

---

## Sample Use Cases

### Use Case 1: Ground Lease vs Fee Simple Decision
**User**: "Should we buy the land ($10M) or do a ground lease ($500K/year rent)?"

**Workflow** (Claude → Python → Claude):
1. **Claude extracts data**: Read proposed ground lease agreement.pdf → extract ground rent ($500K/year), term (75 years), escalations (2%/year), subordination provisions, purchase options
2. **Claude researches comps**: WebSearch for comparable land sales → find $10M fee simple price
3. **Claude normalizes**: Create `ground_lease_scenario.json` and `fee_simple_scenario.json` with cash flows, financing assumptions
4. **Claude invokes skill**: `ground-lease-structuring-expert` guides analysis framework (subordination impact, leasehold valuation)
5. **Python calculates**: Run `ground_lease_vs_fee_simple()` → NPV comparison over 75 years, leasehold vs fee simple valuation
6. **Python analyzes**: Run `subordination_impact_analysis()` → model financing constraints (subordinated: 70% LTV, unsubordinated: 55% LTV)
7. **Python exports**: Save `ground_lease_analysis.json` with NPV comparison, financing impact, IRR sensitivity
8. **Claude synthesizes**: Generate recommendation memo with NPV analysis (ground lease saves $2M NPV), financing trade-offs (55% LTV vs 70% LTV), risk assessment (ground rent escalation risk, renewal risk), and strategic recommendation (ground lease preferred if construction financing available at 55% LTV)

### Use Case 2: Build-to-Suit Lease Structuring
**User**: "Tenant wants 100,000 SF warehouse built to their specs. How do we structure the BTS lease?"

**Workflow** (Claude → Python → Claude):
1. **Claude extracts requirements**: Read tenant's Letter of Intent.pdf and specification document → extract size (100,000 SF), tenant improvements (high-cube warehouse, ESFR sprinklers, 50' clear height), delivery date (18 months)
2. **Claude researches costs**: WebSearch for industrial construction costs in the market → find $80/SF hard cost benchmark
3. **Claude estimates budget**: Land owned at $2M book value, hard costs $8M ($80/SF), soft costs $1M (12.5%), financing $300K (construction interest)
4. **Claude normalizes**: Create `bts_project_inputs.json` with land, costs, tenant specs, financing assumptions, return requirement (7%)
5. **Claude invokes skill**: `build-to-suit-expert` guides BTS lease structure (turnkey vs cost-plus, risk allocation, approval checkpoints)
6. **Python calculates**: Run `bts_rent_calculation()` → $11.3M total investment × 7% return = $791K NOI → $7.91/SF NNN rent
7. **Python compares**: Run `turnkey_vs_cost_plus_comparison()` → model turnkey (fixed rent) vs cost-plus (rent tied to actual costs)
8. **Python exports**: Save `bts_lease_structure.json` with rent calculation, risk allocation matrix, delivery schedule
9. **Claude synthesizes**: Generate BTS lease term sheet with 15-year initial term, $7.91/SF NNN rent, turnkey delivery, development agreement with 3 design checkpoints (schematic, DD, CD), cost overrun allocation (base building = landlord, tenant changes = tenant), 6-month free rent for fit-up, substantial completion definition and liquidated damages ($2,000/day after month 18)

### Use Case 3: Construction Schedule Management
**User**: "Construction is 3 weeks behind. Analyze impact and acceleration options."

**Workflow** (Claude → Python → Claude):
1. **Claude extracts baseline**: Read original construction schedule.pdf → extract baseline activities, durations, dependencies, critical path
2. **Claude extracts current status**: Read monthly construction progress report.pdf → extract actual progress, delays, completion percentages
3. **Claude identifies issue**: Foundation work is 3 weeks behind schedule (21 days delay on critical path activity)
4. **Claude normalizes**: Create `construction_schedule.json` with baseline activities, current progress, delay information
5. **Claude invokes skill**: `construction-management-expert` guides CPM analysis and acceleration options
6. **Python calculates**: Run `critical_path_analysis()` → confirm foundation is on critical path (zero float)
7. **Python analyzes**: Run `schedule_variance_analysis()` → calculate impact: 21-day delay pushes completion from day 365 to day 386
8. **Python evaluates options**: Run `schedule_acceleration_cost()` → model overtime ($120K), additional crews ($150K), prefabrication ($90K)
9. **Python exports**: Save `schedule_recovery_options.json` with acceleration costs, revised completion dates
10. **Claude synthesizes**: Generate schedule recovery recommendation: Prefabrication option ($90K) recovers 3 weeks, avoids $42K liquidated damages ($2K/day × 21 days), maintains tenant relationship. Net cost $48K vs doing nothing (pay $42K penalty + tenant relationship damage). Recommend prefabrication with revised completion date of day 365 (on-time).

### Use Case 4: TI Allowance Structuring
**User**: "Tenant needs $50/SF in improvements. We're offering $30/SF allowance. Structure over-allowance terms."

**Workflow**:
1. Invokes `work-letter-expert` skill
2. Defines allowable costs (excludes furniture, equipment, data cabling)
3. Runs `ti_allowance_calculator()`: 10,000 SF × $30/SF = $300K landlord pays
4. Tenant needs $50/SF × 10,000 SF = $500K → Over-allowance = $200K
5. Runs `over_allowance_rent_adjustment()`: $200K amortized over 7 years at 6% = $34.5K/year = $3.45/SF/year rent increase
6. **Generates work letter with $30/SF base allowance + $3.45/SF over-allowance rent for tenant's enhanced improvements**

### Use Case 5: Development Feasibility Analysis
**User**: "We own a 2-acre industrial site. Should we develop speculatively or hold?"

**Workflow**:
1. Invokes `development-feasibility-expert` skill
2. Runs `highest_best_use_analysis()`: Zoning allows 100,000 SF warehouse (50% FAR)
3. Builds development pro forma:
   - Land (owned): $0 cash outlay (opportunity cost $2M)
   - Hard costs: $80/SF × 100,000 SF = $8M
   - Soft costs: 15% = $1.2M
   - Financing: 60% LTV construction loan at 7%
   - Timeline: 12 months construction + 6 months lease-up
4. Calculates stabilized value: Market rent $10/SF NNN, 95% occupied, 5.5% cap rate
   - Stabilized NOI: $950K → Value $17.3M
5. Runs `development_yield_calculation()`: $950K NOI / $9.2M total cost = 10.3% yield on cost
6. Runs `development_irr()`: 18-month project, exit sale at $17.3M = 25% IRR
7. **Recommendation**: Proceed with speculative development - 10.3% yield on cost exceeds market cap rate by 480 bps, 25% IRR exceeds hurdle**

---

## Python Dependencies

### Add to requirements.txt:

```python
# Core numerical computation (REQUIRED)
numpy>=1.26.0
pandas>=2.2.0
scipy>=1.14.0

# Project management and scheduling (REQUIRED)
networkx>=3.2  # NEW - Graph algorithms for CPM/PERT scheduling, critical path analysis
python-gantt>=0.6.0  # OPTIONAL - Gantt chart generation for visualization

# Visualization (REQUIRED for construction schedules and pro formas)
matplotlib>=3.9.0
plotly>=5.20.0
seaborn>=0.13.0

# Geospatial (for site analysis) - Already in market-intelligence spec
# geopandas>=0.14.0  # Geographic data analysis
# folium>=0.16.0     # Interactive maps
# shapely>=2.0.0     # Geometric operations
```

### Explicitly EXCLUDED Libraries:
```python
# ❌ DO NOT ADD - Claude Code handles these tasks natively

# Document parsing (Claude Code's Read tool is superior)
# pdfplumber  # ❌ Use Claude's Read tool for contracts, leases, plans
# PyPDF2      # ❌ Use Claude's Read tool for construction documents
# pypdf       # ❌ Use Claude's Read tool for permits, specifications
# camelot-py  # ❌ Use Claude's Read tool for cost tables
# tabula-py   # ❌ Use Claude's Read tool for schedule tables

# Web scraping (Claude Code's WebFetch/WebSearch tools are better)
# requests    # ❌ Use Claude's WebFetch/Bash for researching zoning codes, permit requirements
# beautifulsoup4  # ❌ Use Claude's WebFetch tool for municipal websites
# selenium    # ❌ Use Claude's WebFetch tool for permit portals
```

### Rationale for Exclusions:
- **Document parsing**: Development documents (ground leases, BTS agreements, construction contracts, architectural plans, specifications) have complex layouts that Claude's multimodal vision handles better than Python PDF libraries
- **Web research**: Researching zoning codes, permit requirements, construction costs should use Claude's WebSearch/WebFetch to respect ToS and avoid scraping complexity
- **Data extraction**: Claude extracts data from documents and normalizes to JSON; Python only performs calculations on the normalized data

### Existing Libraries (Already Available):
- `pandas`, `numpy` - Data manipulation, time series
- `scipy` - Optimization and numerical methods
- `matplotlib`, `plotly` - Visualization
- Financial calculation libraries from existing calculators (`Shared_Utils`)

---

## Integration with Other Agents

### Coordination with Leasing-Expert:
- **Transition point**: Development-coordinator handles pre-construction and construction phase; reggie-chan-vp takes over at stabilization
- **BTS leases**: Development-coordinator structures initial BTS lease; reggie-chan-vp handles renewals and amendments
- **Ground leases**: Development-coordinator structures ground lease; reggie-chan-vp handles operations

### Coordination with Financial-Analyst:
- **Development pro formas**: Development-coordinator builds base case; financial-analyst adds sensitivity/Monte Carlo
- **Financing analysis**: Development-coordinator structures construction/perm loans; financial-analyst optimizes capital structure
- **Risk assessment**: Development-coordinator identifies development risks; financial-analyst quantifies risk-adjusted returns

### Coordination with Market-Intelligence:
- **Site selection**: Market-intelligence identifies markets/submarkets; development-coordinator evaluates specific sites
- **Feasibility**: Market-intelligence provides demand data; development-coordinator models supply/development economics
- **HBU analysis**: Market-intelligence provides market context; development-coordinator calculates development scenarios

---

## Slash Command Interfaces

Each slash command accepts a single JSON payload appended to the command text (wrap payloads in single quotes when invoking from chat). Commands write their calculation JSON to `Development_Management/results/<analysis_id>.json` and surface the path for Claude to read.

### `/ground-lease-analysis`
- **Payload schema**:
```json
{
  "site_data": {"market": "Phoenix", "land_price": 9500000},
  "ground_lease_terms": {"rent": 500000, "term_years": 75, "escalation": 0.02},
  "discount_rate": 0.085,
  "fee_simple_option": {"acquisition_price": 10000000}
}
```
- **Sample response**:
```json
{
  "command": "/ground-lease-analysis",
  "analysis_id": "GL-202",
  "result_file": "Development_Management/results/gl-202.json"
}
```

### `/bts-lease-structure`
- **Payload schema**:
```json
{
  "tenant_requirements": {"building_sf": 120000, "spec_level": "Class A"},
  "development_costs": {"land": 2200000, "hard": 9000000, "soft": 1600000},
  "delivery_models": ["turnkey", "cost_plus"],
  "return_requirement": 0.07
}
```
- **Sample response**:
```json
{
  "command": "/bts-lease-structure",
  "analysis_id": "BTS-18",
  "result_file": "Development_Management/results/bts-18.json"
}
```

### `/construction-schedule`
- **Payload schema**:
```json
{
  "activities": [
    {"id": "A", "name": "Site Work", "duration_days": 30},
    {"id": "B", "name": "Foundation", "duration_days": 45, "predecessors": ["A"]}
  ],
  "baseline_start": "2024-01-15",
  "current_date": "2024-03-20",
  "acceleration_targets": {"target_completion": "2024-12-15"}
}
```
- **Sample response**:
```json
{
  "command": "/construction-schedule",
  "analysis_id": "SCH-55",
  "visualizations": ["gantt-foundation-delay"],
  "result_file": "Development_Management/results/schedule-55.json"
}
```

### `/work-letter-draft`
- **Payload schema**:
```json
{
  "premises": {"suite": "1200", "size_sf": 15000},
  "ti_scope": {"allowable_categories": ["HVAC", "Electrical"], "requested_psf": 55},
  "allowance": {"base_psf": 35, "amortization_term_years": 8, "interest_rate": 0.065}
}
```
- **Sample response**:
```json
{
  "command": "/work-letter-draft",
  "analysis_id": "WL-09",
  "result_file": "Development_Management/results/work-letter-09.json"
}
```

### `/entitlement-timeline`
- **Payload schema**:
```json
{
  "project_type": "Industrial",
  "jurisdiction": "Austin, TX",
  "permit_stack": [
    {"name": "Site Plan", "duration_days": 120},
    {"name": "Building Permit", "duration_days": 60, "dependencies": ["Site Plan"]}
  ],
  "complexity": "high"
}
```
- **Sample response**:
```json
{
  "command": "/entitlement-timeline",
  "analysis_id": "ENT-31",
  "result_file": "Development_Management/results/entitlement-31.json"
}
```

### `/development-proforma` (alias `/residual-land-value`)
- **Payload schema**:
```json
{
  "site_data": {"land_cost": 2500000, "acreage": 2.5},
  "development_scenario": {"product_type": "Industrial", "size_sf": 100000},
  "noi_projection": {"stabilized_noi": 1200000, "exit_cap_rate": 0.055},
  "cost_stack": {"hard_costs": 8000000, "soft_costs_pct": 0.15}
}
```
- **Sample response**:
```json
{
  "command": "/development-proforma",
  "analysis_id": "DEV-77",
  "visualizations": ["proforma-waterfall"],
  "result_file": "Development_Management/results/dev-77.json"
}
```

---

## Implementation Roadmap

**CRITICAL**: All phases must follow the Claude → Python → Claude pattern. Python modules should ONLY contain calculation/analysis logic, not document parsing or web scraping.

### Phase 1: Foundation (Week 1)
1. ✅ Create agent specification (this document)
2. Create `development-coordinator.md` agent file with explicit division of labor instructions
3. Set up `/Development_Management/` directory structure
4. Implement `ground_lease_analysis.py` core functions (calculations only, no document parsing)
5. Create `ground-lease-structuring-expert` skill (guides Claude to extract lease terms, then invoke Python for NPV analysis)
6. **Validation**: Verify no Python modules import pdfplumber, PyPDF2, pypdf, requests, beautifulsoup4, or selenium

### Phase 2: BTS & Construction (Week 2)
1. Implement `build_to_suit_analysis.py`
2. Create `build-to-suit-expert` skill
3. Implement `construction_management.py` with CPM scheduling
4. Create `construction-management-expert` skill
5. Add unit tests

### Phase 3: Work Letters & TI (Week 3)
1. Implement `work_letter_analysis.py`
2. Create `work-letter-expert` skill
3. Build work letter templates and examples
4. Integration with existing TI analysis tools
5. Add `test_work_letter_analysis.py` covering allowance math, over-allowance amortization, and allowable-cost validation

### Phase 4: Entitlements (Week 4)
1. Implement `entitlement_analysis.py`
2. Create `entitlement-permitting-expert` skill
3. Build zoning compliance checker
4. Create entitlement timeline templates by jurisdiction
5. Add `test_entitlement_analysis.py` covering zoning compliance edge cases and timeline risk modeling

### Phase 5: Feasibility & Pro Formas (Week 5)
1. Implement `development_feasibility.py`
2. Create `development-feasibility-expert` skill
3. Build comprehensive development pro forma models
4. Integration testing across all skills
5. Documentation and examples

---

## Data Requirements

### Construction Data:
```
/Development_Management/
├── data/
│   ├── cost_databases/              # RSMeans data, local cost databases
│   ├── construction_schedules/      # Template schedules by property type
│   ├── contractor_bids/             # Historical bid data
│   └── permit_timelines/            # Permit duration by jurisdiction
└── templates/
    ├── ground_lease_templates/      # Ground lease agreement forms
    ├── bts_lease_templates/         # BTS lease and development agreement forms
    ├── work_letter_templates/       # Work letter templates by property type
    └── development_proforma_templates/
```

### Construction Cost Data Sources:

#### Commercial Sources (Subscription):
1. **RSMeans (Gordian)**
   - **Coverage**: Construction cost data by location and building type
   - **Cost**: $500-$2,000/year
   - **Priority**: HIGH - industry standard

2. **Marshall & Swift**
   - **Coverage**: Building cost data and valuation
   - **Cost**: Subscription-based
   - **Priority**: MEDIUM

#### Free/Public Sources:
1. **Historical project data** (internal)
2. **Contractor bid databases** (build over time)
3. **Municipal permit fee schedules** (public records)
4. **USACE (US Army Corps of Engineers) cost indices** (free)

---

## Construction Scheduling Methodology

### Critical Path Method (CPM):

```python
# Example CPM network for industrial development
activities = {
    'A': {'name': 'Site Work', 'duration': 30, 'predecessors': []},
    'B': {'name': 'Foundation', 'duration': 45, 'predecessors': ['A']},
    'C': {'name': 'Structure', 'duration': 90, 'predecessors': ['B']},
    'D': {'name': 'Envelope', 'duration': 60, 'predecessors': ['C']},
    'E': {'name': 'MEP Rough-In', 'duration': 75, 'predecessors': ['C']},
    'F': {'name': 'Interior Finishes', 'duration': 60, 'predecessors': ['D', 'E']},
    'G': {'name': 'MEP Finish', 'duration': 30, 'predecessors': ['F']},
    'H': {'name': 'Site Completion', 'duration': 20, 'predecessors': ['D']},
    'I': {'name': 'Punchlist', 'duration': 15, 'predecessors': ['G', 'H']},
}

# Calculate critical path, early start, late start, float
# Identify activities that can be accelerated
# Model schedule compression scenarios
```

---

## Ground Lease Considerations

### Subordination vs Unsubordinated:

**Subordinated Ground Lease**:
- Ground lease subordinate to leasehold mortgage
- Allows conventional financing (70-75% LTV)
- Ground lessor at risk if leaseholder defaults on mortgage
- Ground lessor typically requires: strong tenant credit, substantial improvements, protective provisions

**Unsubordinated Ground Lease**:
- Ground lease SENIOR to leasehold mortgage
- Limits financing (40-60% LTV of leasehold value, not fee simple)
- Ground lessor protected in foreclosure (lease survives)
- More common for institutional ground lessors

**Financial Impact**:
```python
# Subordinated ground lease
fee_simple_value = 10_000_000
leasehold_mortgage = 0.70 * fee_simple_value  # $7M loan available

# Unsubordinated ground lease
leasehold_value = 7_500_000  # Discounted due to ground rent obligation
leasehold_mortgage = 0.50 * leasehold_value  # $3.75M loan available

# Difference in leverage: $3.25M less debt capacity
```

---

## Build-to-Suit Economics

### Rent Calculation Model:

```python
# Typical BTS rent calculation
land_cost = 2_000_000
hard_costs = 8_000_000
soft_costs = 1_000_000  # 10-15% of hard costs
financing_cost = 300_000  # Construction loan interest
total_investment = land_cost + hard_costs + soft_costs + financing_cost
# = $11.3M

developer_return_requirement = 0.07  # 7% yield on cost
required_noi = total_investment * developer_return_requirement
# = $791K NOI

building_size = 100_000  # SF
bts_rent = required_noi / building_size
# = $7.91/SF NNN

# Compare to market rent: $8.50/SF
# BTS rent 7% below market = reasonable (no lease-up risk, long-term tenant)
```

### Turnkey vs Cost-Plus:

**Turnkey** (Fixed Price):
- Landlord quotes fixed rent based on estimated costs
- Landlord bears cost overrun risk
- Tenant gets price certainty
- Landlord includes contingency (5-10%)

**Cost-Plus**:
- Rent tied to actual construction costs
- Tenant bears cost overrun risk
- Landlord passes through actual costs + developer fee
- More transparent but less certainty for tenant

---

## Success Metrics

Agent is successful when it can:

### Functional Capabilities
✅ Structure ground lease vs fee simple comparison with full NPV analysis and subordination impact
✅ Build comprehensive BTS lease term sheets with cost allocation and risk assignment
✅ Generate CPM construction schedules with critical path identification and float analysis
✅ Draft detailed work letters with TI allowance structures and over-allowance amortization
✅ Model entitlement timelines with probability-weighted outcomes and risk assessment
✅ Build development pro formas from land acquisition through stabilization with IRR/yield calculations
✅ Calculate residual land values for acquisition decisions using discounted cash flow
✅ Integrate seamlessly with reggie-chan-vp, financial-analyst, and market-intelligence agents
✅ Produce construction-ready documents and developer-grade analyses

### Architectural Compliance (Division of Labor)
✅ **Zero Python document parsing libraries**: No imports of pdfplumber, PyPDF2, pypdf, camelot-py, or tabula-py in any module
✅ **Zero Python web scraping libraries**: No imports of requests, beautifulsoup4, selenium, or scrapy
✅ **Claude handles document reading**: All reading of ground leases, BTS agreements, construction contracts, permits, plans, specifications done via Claude's Read tool
✅ **Claude handles web research**: All research for zoning codes, permit requirements, construction costs done via WebSearch/WebFetch
✅ **Python focused on calculations**: All .py files contain only financial calculations, CPM scheduling, cost modeling, and optimization
✅ **JSON I/O contracts**: All Python modules consume JSON inputs (already extracted/normalized by Claude) and produce JSON outputs
✅ **Claude synthesizes reports**: All narrative reports, recommendations, term sheets, and work letters generated by Claude, not Python
✅ **Reuses existing utilities**: Development modules leverage Shared_Utils for NPV/IRR instead of duplicating financial calculations

---

## Documentation Deliverables

1. **Agent README**: Overview, capabilities, when to use vs other agents
2. **Skills Documentation**: Detailed guide for each skill (6 skills)
3. **Python Module Docs**: Docstrings and usage examples for all functions
4. **Template Library**: Ground leases, BTS leases, work letters, development agreements
5. **Construction Standards**: Material specs, construction requirements by property type
6. **Example Pro Formas**: Office, industrial, retail development models
7. **Integration Guide**: How to coordinate with other agents
8. **Testing Guide**: Unit tests, integration tests, validation procedures

---

## Risk Considerations

### Construction Risks:
- **Cost overruns**: Mitigation via contingencies, cost tracking, change order management
- **Schedule delays**: Mitigation via CPM scheduling, float analysis, liquidated damages
- **Quality issues**: Mitigation via inspections, testing, punch lists
- **Contractor default**: Mitigation via bonding, financial reviews, replacement contractors

### Entitlement Risks:
- **Zoning approval denial**: Mitigation via pre-application meetings, variance strategy
- **Permit delays**: Mitigation via timeline tracking, expediting, concurrent reviews
- **Neighborhood opposition**: Mitigation via community engagement, design modifications
- **Environmental issues**: Mitigation via Phase I/II ESAs, remediation plans

### Financial Risks:
- **Construction financing gap**: Mitigation via equity contributions, mezzanine debt
- **Lease-up delays**: Mitigation via pre-leasing, absorption models, holding reserves
- **Market deterioration**: Mitigation via sensitivity analysis, exit strategies
- **Cost escalation**: Mitigation via material price locks, GMP contracts

### Ground Lease Risks:
- **Subordination limits financing**: Mitigation via unsubordinated structure or lender negotiation
- **Ground rent escalations**: Mitigation via CPI caps, fixed escalations
- **Ground lease expiration**: Mitigation via long initial term (75-99 years), renewal options
- **Purchase option disputes**: Mitigation via clear valuation methodology

---

## Next Steps

1. **Review & Approve Spec**: Get user approval on scope and approach
2. **Create Agent File**: Write `development-coordinator.md` based on spec
3. **Implement Priority 1 Skills**: ground-lease, BTS, construction-mgmt, work-letter
4. **Build Python Modules**: Ground lease analysis, BTS economics, CPM scheduling
5. **Create Template Library**: Ground leases, BTS leases, work letters
6. **Integration Testing**: Test agent + skills + other agents
7. **Documentation**: Write comprehensive guides and examples

**Estimated Timeline**: 4-5 weeks for full implementation
**Lines of Code**: ~2,500-3,500 lines Python + 2,000-2,500 lines skills/docs
**Templates Required**: 10-15 legal templates (ground lease, BTS, work letter, development agreement)

---

## Appendix: Development Pro Forma Template

### Standard Development Pro Forma Structure:

```
ACQUISITION PHASE
├── Land Acquisition Cost
├── Closing Costs (title, legal, brokerage)
└── Due Diligence (Phase I/II ESA, surveys)

PREDEVELOPMENT PHASE
├── Architectural & Engineering
├── Entitlements (zoning, permits, impact fees)
├── Legal & Accounting
└── Project Management

CONSTRUCTION PHASE
├── Site Work (demo, grading, utilities)
├── Building Hard Costs (structure, envelope, MEP)
├── Tenant Improvements (if build-to-suit)
├── FF&E (if applicable)
├── Contingency (5-10%)
└── Construction Period Interest & Fees

LEASE-UP PHASE
├── Leasing Commissions
├── Marketing & Advertising
├── TI Allowances (if speculative)
├── Free Rent (lost income during lease-up)
└── Operating Expenses (pre-stabilization)

EXIT / STABILIZATION
├── Stabilized NOI (Year 1)
├── Exit Cap Rate or Hold Scenario
├── Sale Proceeds (if merchant builder)
└── Development Profit / IRR Calculation
```

This structure forms the basis for `development_pro_forma()` function and development-feasibility-expert skill.
