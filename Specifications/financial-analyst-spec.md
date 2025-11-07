# Financial Analyst Agent - Specification Plan

## Agent Overview

**Name**: `financial-analyst`

**Purpose**: Deep financial modeling, investment analysis, and quantitative decision support for commercial real estate portfolios. Complements `leasing-expert` by providing sophisticated financial analysis beyond deal-level economics.

**Distinct Value**: While `leasing-expert` focuses on lease structure and deal negotiation, `financial-analyst` specializes in complex financial modeling, portfolio-level analytics, accounting compliance, and investment performance measurement.

## Core Competencies

### 1. Investment Analysis
- Multi-scenario NPV and IRR modeling
- Sensitivity analysis and stress testing
- Monte Carlo simulations for risk quantification
- Capital budgeting and allocation across assets
- Investment committee presentation materials

### 2. Lease Accounting (IFRS 16 / ASC 842)
- Lease liability calculations
- Right-of-use (ROU) asset amortization
- Journal entries and disclosure schedules
- Transition from IAS 17 to IFRS 16
- Portfolio-level accounting roll-ups

### 3. Portfolio Financial Analytics
- Portfolio-level cash flow modeling
- Waterfall distribution calculations
- Promote structure modeling (GP/LP splits)
- Asset-level and portfolio-level returns
- Variance analysis (budget vs actual)

### 4. Financial Reporting
- IFRS/GAAP compliant reporting
- Investor communications and reports
- Financial statement preparation
- KPI dashboards and performance metrics
- Management reports and presentations

### 5. Risk Analytics
- Value at Risk (VaR) calculations
- Stress testing under adverse scenarios
- Credit risk modeling and tenant default probability
- Market risk exposure analysis
- Portfolio diversification metrics

## Required Claude Code Skills

### Priority 1: Essential Skills (Create First)

#### 1. **sensitivity-analysis-expert**

**Description**: Expert in financial sensitivity analysis, scenario modeling, and stress testing. Use when evaluating how changes in key assumptions affect investment returns, running what-if scenarios, stress testing under adverse conditions, tornado diagrams for variable importance, or quantifying downside risk. Key terms include sensitivity analysis, scenario analysis, stress testing, Monte Carlo simulation, tornado diagram, base case, downside case, upside case, breakeven analysis, elasticity.

**What it does**:
- Identifies critical variables driving investment returns
- Runs multi-scenario analysis (base/bull/bear cases)
- Performs Monte Carlo simulations (1,000-10,000 iterations)
- Creates tornado diagrams showing variable impact
- Quantifies probability of outcomes (P10, P50, P90)
- Stress tests under recession/interest rate shock scenarios

**Python functions needed**:
```python
# sensitivity_analysis.py
def one_way_sensitivity(base_inputs, variable_range, calc_function)
def two_way_sensitivity(base_inputs, var1_range, var2_range, calc_function)
def monte_carlo_simulation(distributions, calc_function, iterations=10000)
def tornado_diagram_data(variables, ranges, calc_function)
def scenario_comparison(scenarios_dict, calc_function)
def calculate_var(returns, confidence_level=0.95)
```

---

#### 2. **portfolio-optimization-expert**

**Description**: Expert in portfolio construction, optimization, and diversification analysis using modern portfolio theory. Use when constructing optimal asset portfolios, balancing risk and return, analyzing portfolio diversification, calculating efficient frontier, optimizing capital allocation across multiple assets, or evaluating portfolio rebalancing strategies. Key terms include Markowitz optimization, efficient frontier, Sharpe ratio, portfolio variance, correlation matrix, diversification benefit, risk-adjusted returns, mean-variance optimization.

**What it does**:
- Constructs efficient frontier (risk-return tradeoff)
- Calculates optimal portfolio weights given constraints
- Analyzes portfolio diversification and concentration risk
- Computes risk-adjusted performance metrics (Sharpe, Sortino, Treynor)
- Recommends capital allocation across assets
- Evaluates correlation and covariance structures

**Python functions needed**:
```python
# portfolio_optimization.py
def efficient_frontier(returns, covariance_matrix, num_portfolios=1000)
def optimal_portfolio(returns, cov_matrix, target_return=None, constraints={})
def sharpe_ratio(returns, risk_free_rate=0.02)
def sortino_ratio(returns, risk_free_rate=0.02)
def portfolio_var(weights, cov_matrix)
def correlation_matrix(returns_df)
def concentration_risk(weights, threshold=0.2)
def diversification_ratio(weights, volatilities, cov_matrix)
```

---

#### 3. **capital-budgeting-expert**

**Description**: Expert in capital allocation, project evaluation, and capital budgeting decisions. Use when evaluating competing capital projects, setting hurdle rates, analyzing capital rationing decisions, ranking investment opportunities, evaluating capital structure decisions, or allocating limited capital across multiple assets. Key terms include hurdle rate, WACC, capital rationing, NPV ranking, IRR ranking, profitability index, payback period, capital allocation, investment decision criteria.

**What it does**:
- Ranks multiple investment opportunities using consistent criteria
- Calculates Weighted Average Cost of Capital (WACC)
- Solves capital rationing problems (limited budget)
- Recommends optimal project portfolio given constraints
- Evaluates make-vs-buy and lease-vs-buy decisions
- Performs equivalent annual cost (EAC) analysis

**Python functions needed**:
```python
# capital_budgeting.py
def calculate_wacc(equity_weight, equity_cost, debt_weight, debt_cost, tax_rate)
def profitability_index(npv, initial_investment)
def payback_period(cash_flows)
def discounted_payback(cash_flows, discount_rate)
def equivalent_annual_cost(npv, periods, discount_rate)
def capital_rationing_optimizer(projects, budget_constraint)
def npv_profile(cash_flows, discount_rates)
def crossover_rate(cash_flows_a, cash_flows_b)
```

---

#### 4. **cash-flow-modeling-expert**

**Description**: Expert in complex multi-period cash flow modeling, waterfall distributions, and promote structures for real estate investments. Use when modeling property-level or portfolio-level cash flows, calculating waterfall distributions between GP/LP, modeling preferred returns and promote structures, analyzing cash-on-cash returns, modeling refinancing scenarios, or evaluating equity multiple distributions. Key terms include waterfall, promote, carried interest, preferred return, hurdle rate, GP/LP split, cash-on-cash return, equity multiple, IRR calculation, distribution waterfall.

**What it does**:
- Models complex multi-period cash flows (acquisition to exit)
- Calculates waterfall distributions (LP pref return → return of capital → GP promote)
- Models promote structures (20% carry after 8% hurdle)
- Analyzes cash-on-cash and IRR at asset and portfolio levels
- Models refinancing scenarios and cash extraction
- Calculates equity multiples and realized returns

**Python functions needed**:
```python
# cash_flow_modeling.py
def waterfall_distribution(cash_available, lp_capital, gp_capital, pref_return, promote_rate)
def calculate_equity_multiple(distributions, equity_invested)
def cash_on_cash_return(annual_cash_flow, equity_invested)
def property_level_cash_flows(noi, debt_service, capex, reserve_requirements)
def portfolio_cash_flows(properties_list, aggregation_rules)
def refinancing_analysis(current_ltv, new_ltv, property_value, interest_rate)
def promote_calculation(irr_achieved, hurdle_rates, promote_tiers)
def distribution_timing(cash_flows, frequency="quarterly")
```

---

### Priority 2: Supporting Skills (Create After Priority 1)

#### 5. **financial-reporting-expert**

**Description**: Expert in IFRS/GAAP financial reporting, investor communications, and performance measurement for real estate portfolios. Use when preparing financial statements, generating investor reports, calculating standardized performance metrics (GIPS, NCREIF), analyzing variance to budget, creating management dashboards, or preparing audit documentation. Key terms include IFRS, GAAP, financial statements, investor reporting, NOI, FFO, AFFO, NAV, mark-to-market, fair value, variance analysis, KPI dashboard.

**What it does**:
- Generates IFRS/GAAP compliant financial statements
- Calculates standard real estate performance metrics (NOI, FFO, AFFO, NAV)
- Creates investor reports with standardized disclosures
- Performs budget vs actual variance analysis
- Generates executive dashboards and KPIs
- Prepares audit support documentation

**Python functions needed**:
```python
# financial_reporting.py
def calculate_noi(revenues, operating_expenses)
def calculate_ffo(net_income, depreciation, gains_on_sale)
def calculate_affo(ffo, maintenance_capex, leasing_costs)
def calculate_nav(property_values, liabilities, outstanding_shares)
def variance_analysis(actual, budget, threshold=0.05)
def kpi_dashboard(portfolio_data, period)
def investor_report_generator(portfolio_data, period, template)
```

---

#### 6. **credit-risk-modeling-expert**

**Description**: Expert in credit risk analysis, default probability estimation, and tenant credit scoring for commercial real estate. Use when assessing tenant default probability, calculating expected loss, modeling credit migration, setting credit limits, analyzing portfolio credit concentration, or evaluating credit enhancement strategies. Key terms include probability of default (PD), loss given default (LGD), expected loss, credit scoring, Altman Z-score, Merton model, credit concentration, credit VaR.

**What it does**:
- Estimates tenant probability of default (PD)
- Calculates expected loss (PD × LGD × Exposure)
- Models credit rating migrations
- Analyzes portfolio credit concentration risk
- Recommends credit enhancement (guarantees, LCs)
- Calculates credit Value at Risk (CVaR)

**Python functions needed**:
```python
# credit_risk_modeling.py
def altman_z_score(financial_ratios)
def probability_of_default(z_score, industry_benchmark)
def expected_loss(pd, lgd, exposure)
def credit_migration_matrix(historical_ratings)
def credit_concentration_herfindahl(exposures)
def credit_var(portfolio_exposures, pd_lgd_correlations, confidence=0.95)
def merton_distance_to_default(equity_value, debt, volatility, risk_free_rate, time)
```

---

## Existing Calculators Integration

The agent will **integrate** with existing calculators but add analytical layers:

### Already Available (Use via SlashCommand):
1. `/effective-rent` - Basic deal economics → Agent adds sensitivity analysis
2. `/ifrs16-calculation` - Lease accounting → Agent adds portfolio roll-ups
3. `/tenant-credit` - Basic credit scoring → Agent adds default probability modeling
4. `/renewal-economics` - Renewal NPV → Agent adds Monte Carlo risk analysis
5. `/option-value` - Real options (Black-Scholes) → Agent adds multi-option portfolios
6. `/relative-valuation` - MCDA ranking → Agent adds statistical validation
7. `/rollover-analysis` - Lease expiry timing → Agent adds refinancing analysis
8. `/default-calculation` - Default damages → Agent adds recovery scenarios
9. `/rental-variance` - Variance decomposition → Agent adds trend forecasting

### New Python Modules to Create:

```
/Financial_Modeling/
├── __init__.py
├── sensitivity_analysis.py          # Monte Carlo, scenario analysis, tornado diagrams
├── portfolio_optimization.py        # MPT, efficient frontier, Sharpe ratio
├── capital_budgeting.py            # WACC, NPV ranking, capital rationing
├── cash_flow_modeling.py           # Waterfall, promote, equity multiple
├── financial_reporting.py          # IFRS/GAAP, investor reports, KPIs
├── credit_risk_modeling.py         # PD, LGD, expected loss, credit VaR
└── Tests/
    ├── test_sensitivity_analysis.py
    ├── test_portfolio_optimization.py
    ├── test_capital_budgeting.py
    └── test_cash_flow_modeling.py
```

## Agent Architecture

### Agent File Structure

```markdown
---
name: financial-analyst
description: Deep financial modeling, investment analysis, and portfolio analytics specialist. Use when performing sensitivity analysis, portfolio optimization, capital budgeting, waterfall calculations, financial reporting, or risk analytics. Expert in NPV/IRR modeling, Monte Carlo simulation, IFRS 16 accounting, and investor reporting.
tools: Read, Glob, Grep, Write, Bash, SlashCommand, TodoWrite, Skill
model: inherit
---

# Financial Analyst Sub-Agent

You are a senior financial analyst specializing in commercial real estate investment analysis...

## Core Responsibilities
[Similar structure to leasing-expert but focused on quantitative analysis]

## Specialized Skills Available
- sensitivity-analysis-expert
- portfolio-optimization-expert
- capital-budgeting-expert
- cash-flow-modeling-expert
- financial-reporting-expert
- credit-risk-modeling-expert

## Workflow Integration
[How to use skills + slash commands + Python calculators together]
```

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1)
1. ✅ Create agent specification (this document)
2. Create `financial-analyst.md` agent file
3. Create `/Financial_Modeling/` directory structure
4. Implement `sensitivity_analysis.py` core functions
5. Create `sensitivity-analysis-expert` skill

### Phase 2: Core Skills (Week 2)
1. Implement `portfolio_optimization.py`
2. Create `portfolio-optimization-expert` skill
3. Implement `capital_budgeting.py`
4. Create `capital-budgeting-expert` skill
5. Add unit tests for all modules

### Phase 3: Advanced Features (Week 3)
1. Implement `cash_flow_modeling.py`
2. Create `cash-flow-modeling-expert` skill
3. Create integration examples combining multiple calculators
4. Build sample workflows and test cases

### Phase 4: Reporting & Documentation (Week 4)
1. Implement `financial_reporting.py`
2. Create `financial-reporting-expert` skill
3. Add comprehensive documentation
4. Create example reports and investor decks
5. Integration testing with `leasing-expert`

---

## Sample Use Cases

### Use Case 1: Lease Deal Evaluation with Risk Analysis
**User**: "Evaluate this lease deal with sensitivity analysis"

**Workflow**:
1. Agent uses `/effective-rent` to get base case NPV/IRR
2. Invokes `sensitivity-analysis-expert` skill
3. Runs `monte_carlo_simulation()` varying rent, vacancy, opex
4. Generates report with P10/P50/P90 outcomes
5. Creates tornado diagram showing variable impact

### Use Case 2: Portfolio Optimization
**User**: "I have $50M to deploy across 5 opportunities. Optimize allocation."

**Workflow**:
1. Agent uses `/effective-rent` on each opportunity
2. Invokes `portfolio-optimization-expert` skill
3. Calculates correlation matrix and efficient frontier
4. Runs `optimal_portfolio()` with $50M constraint
5. Recommends allocation maximizing Sharpe ratio

### Use Case 3: Waterfall Distribution
**User**: "Calculate distributions for this promote structure: 8% pref, 15% promote after 12% IRR"

**Workflow**:
1. Invokes `cash-flow-modeling-expert` skill
2. Models quarterly cash flows from property operations
3. Runs `waterfall_distribution()` with specified hurdles
4. Calculates LP vs GP distributions over holding period
5. Generates distribution schedule and equity multiples

### Use Case 4: Capital Allocation Decision
**User**: "Should we invest in Property A (12% IRR, $10M) or Property B (14% IRR, $15M)? Budget is $20M."

**Workflow**:
1. Invokes `capital-budgeting-expert` skill
2. Calculates profitability index for each
3. Runs `capital_rationing_optimizer()` with $20M constraint
4. Considers risk-adjusted returns and strategic fit
5. Recommends optimal allocation

---

## Skill Development Guidelines

Following Claude Code best practices for skill creation:

### Skill Structure (Per Claude Guidelines):

```markdown
---
name: [skill-name]
description: Expert in [topic]. Use when [scenario 1], [scenario 2], [scenario 3]. Key terms include [term1], [term2], [term3].
tags: [relevant-tags]
capability: [one-line capability statement]
proactive: true
---

# Concise Skill Content

## What is [Concept]?
[2-3 sentence plain language definition]

## When to Use
[3-5 specific scenarios with bullet points]

## Key Concepts
[Essential concepts only, no redundancy]

## Common Calculations
[Core formulas with explanations]

## Practical Examples
[1-2 concrete examples, no more]

## Pitfalls
[3-5 common mistakes to avoid]

---

**This skill activates when you**:
- [Specific trigger 1]
- [Specific trigger 2]
- [Specific trigger 3]
```

### Key Principles:
1. **Concise**: 200-400 lines MAX (not 1,000+)
2. **Clear "Use when:"** in description with specific scenarios
3. **Key terms**: List 8-12+ terms users would naturally say
4. **No redundancy**: Don't repeat information across skills
5. **Actionable**: Focus on what to do, not just theory
6. **Examples**: One clear example > five mediocre ones

---

## Dependencies

### Python Packages (Add to requirements.txt):
```python
# Optimization and numerical methods
scipy>=1.14.0  # Already included - used for optimization
cvxpy>=1.5.0  # NEW - Convex optimization for portfolio problems

# Statistical analysis
statsmodels>=0.14.0  # NEW - Statistical modeling, time series

# Visualization (optional but recommended)
matplotlib>=3.9.0  # NEW - Plotting for reports
seaborn>=0.13.0  # NEW - Statistical visualizations
```

### New Slash Commands to Create:

```bash
/sensitivity-analysis <deal-path> [--variables] [--scenarios]
/portfolio-optimize <opportunities-path> <budget> [--constraints]
/capital-allocation <projects-path> <budget> [--ranking-method]
/waterfall-calc <cash-flows-path> <promote-structure>
/credit-var <portfolio-path> [--confidence-level]
```

---

## Success Metrics

Agent is successful when it can:

✅ Run Monte Carlo simulations with 10,000+ iterations in <60 seconds
✅ Optimize 10-asset portfolios with constraints (budget, concentration limits)
✅ Calculate complex waterfall distributions with multiple tiers
✅ Generate IFRS 16 compliant accounting for 100+ lease portfolio
✅ Perform variance analysis comparing budget vs actual across portfolio
✅ Integrate seamlessly with leasing-expert for holistic deal evaluation
✅ Produce investor-grade reports and presentations

---

## Documentation Deliverables

1. **Agent README**: Overview, capabilities, when to use vs leasing-expert
2. **Skills Documentation**: Detailed guide for each skill (6 skills)
3. **Python Module Docs**: Docstrings and usage examples for all functions
4. **Integration Guide**: How to combine agent + skills + calculators
5. **Example Workflows**: 10+ end-to-end scenarios with code
6. **Testing Guide**: Unit tests, integration tests, validation procedures

---

## Next Steps

1. **Review & Approve Spec**: Get user approval on this specification
2. **Create Agent File**: Write `financial-analyst.md` based on spec
3. **Implement Priority 1 Skills**: sensitivity-analysis, portfolio-optimization, capital-budgeting, cash-flow-modeling
4. **Build Python Modules**: Create Financial_Modeling/ with core functions
5. **Integration Testing**: Test agent + skills + existing calculators
6. **Documentation**: Write comprehensive guides and examples

**Estimated Timeline**: 3-4 weeks for full implementation
**Lines of Code**: ~2,000-3,000 lines Python + 1,500-2,000 lines skills/docs
