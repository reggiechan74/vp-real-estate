# Development Coordinator Agent - Specification Plan

## Agent Overview

**Name**: `development-coordinator`

**Purpose**: Development project management, build-to-suit leasing, ground lease structuring, and construction coordination for commercial real estate projects. Complements `leasing-expert` by specializing in development-specific leasing, construction management, and entitlement processes.

**Distinct Value**: While `leasing-expert` handles stabilized asset leasing, `development-coordinator` specializes in ground leases, build-to-suit transactions, construction budgeting, development feasibility, entitlements, and coordinating the development process from land acquisition through project completion.

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
def residual_land_value(stabilized_noi, building_cost, return_requirements)
def ground_lease_purchase_option(land_value_growth, option_terms)
def unsubordinated_lease_financing(ltv_max, dscr_requirements)
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
[How to use skills + construction tools + existing calculators]
```

---

## Sample Use Cases

### Use Case 1: Ground Lease vs Fee Simple Decision
**User**: "Should we buy the land ($10M) or do a ground lease ($500K/year rent)?"

**Workflow**:
1. Invokes `ground-lease-structuring-expert` skill
2. Runs `ground_lease_vs_fee_simple()` comparing NPV of both options
3. Evaluates subordination implications for construction financing
4. Calculates leasehold value vs fee simple value
5. Analyzes ground lease renewal and purchase option value
6. **Recommendation**: Fee simple at 5% cap rate vs ground lease at 5.5% "cap rate" → Ground lease saves $2M NPV but limits financing to 55% LTV vs 70% LTV

### Use Case 2: Build-to-Suit Lease Structuring
**User**: "Tenant wants 100,000 SF warehouse built to their specs. How do we structure the BTS lease?"

**Workflow**:
1. Invokes `build-to-suit-expert` skill
2. Calculates land cost + construction cost + financing + return requirement
3. Runs `bts_rent_calculation()`: Land $2M + Hard costs $8M + Soft costs $1M = $11M → 7% return = $770K NOI → $7.70/SF NNN rent
4. Structures development agreement (landlord builds to tenant specs, turnkey delivery)
5. Defines approval process (3 checkpoints: schematic, design development, construction documents)
6. Allocates risk (cost overruns on base building = landlord, tenant changes = tenant)
7. **Generates BTS lease term sheet with 15-year initial term, 7.70/SF NNN rent, turnkey delivery, 6-month free rent for fit-up**

### Use Case 3: Construction Schedule Management
**User**: "Construction is 3 weeks behind. Analyze impact and acceleration options."

**Workflow**:
1. Invokes `construction-management-expert` skill
2. Runs `critical_path_analysis()` to identify critical activities
3. Runs `schedule_variance_analysis()`: 3 weeks behind on foundation work (critical path)
4. Evaluates acceleration options: overtime, additional crews, prefabrication
5. Runs `schedule_acceleration_cost()`: Recover 3 weeks = $120K additional cost
6. Analyzes liquidated damages: $2K/day × 21 days = $42K penalty if not accelerated
7. **Recommendation**: Accelerate foundation work ($120K cost avoids $42K penalty + maintains tenant relationship, net cost $78K)**

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

## New Python Dependencies

### Add to requirements.txt:

```python
# Project management and scheduling
networkx>=3.2  # NEW - Graph algorithms for CPM/PERT scheduling
python-gantt>=0.6.0  # NEW - Gantt chart generation (optional)

# Geospatial (for site analysis)
# Already in market-intelligence: geopandas, folium, shapely
```

### Existing Libraries (Already Available):
- `pandas`, `numpy` - Data manipulation
- `scipy` - Optimization and numerical methods
- `matplotlib`, `plotly` - Visualization
- Financial calculation libraries from existing calculators

---

## Integration with Other Agents

### Coordination with Leasing-Expert:
- **Transition point**: Development-coordinator handles pre-construction and construction phase; leasing-expert takes over at stabilization
- **BTS leases**: Development-coordinator structures initial BTS lease; leasing-expert handles renewals and amendments
- **Ground leases**: Development-coordinator structures ground lease; leasing-expert handles operations

### Coordination with Financial-Analyst:
- **Development pro formas**: Development-coordinator builds base case; financial-analyst adds sensitivity/Monte Carlo
- **Financing analysis**: Development-coordinator structures construction/perm loans; financial-analyst optimizes capital structure
- **Risk assessment**: Development-coordinator identifies development risks; financial-analyst quantifies risk-adjusted returns

### Coordination with Market-Intelligence:
- **Site selection**: Market-intelligence identifies markets/submarkets; development-coordinator evaluates specific sites
- **Feasibility**: Market-intelligence provides demand data; development-coordinator models supply/development economics
- **HBU analysis**: Market-intelligence provides market context; development-coordinator calculates development scenarios

---

## New Slash Commands to Create:

```bash
/ground-lease-analysis <site-data> <ground-lease-terms>
/bts-lease-structure <tenant-requirements> <development-costs>
/construction-schedule <activities-list> [--dependencies]
/work-letter-draft <premises-data> <ti-scope> <allowance>
/entitlement-timeline <project-type> <jurisdiction> [--complexity]
/development-proforma <site-data> <development-scenario>
/residual-land-value <noi-projection> <development-costs>
```

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1)
1. ✅ Create agent specification (this document)
2. Create `development-coordinator.md` agent file
3. Set up `/Development_Management/` directory structure
4. Implement `ground_lease_analysis.py` core functions
5. Create `ground-lease-structuring-expert` skill

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

### Phase 4: Entitlements (Week 4)
1. Implement `entitlement_analysis.py`
2. Create `entitlement-permitting-expert` skill
3. Build zoning compliance checker
4. Create entitlement timeline templates by jurisdiction

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

✅ Structure ground lease vs fee simple comparison with full NPV analysis
✅ Build comprehensive BTS lease term sheets with cost allocation
✅ Generate CPM construction schedules with critical path identification
✅ Draft detailed work letters with TI allowance structures
✅ Model entitlement timelines with probability-weighted outcomes
✅ Build development pro formas from land acquisition through stabilization
✅ Calculate residual land values for acquisition decisions
✅ Integrate seamlessly with leasing-expert, financial-analyst, and market-intelligence
✅ Produce construction-ready documents and developer-grade analyses

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
