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

## Division of Labor: Claude Code vs Python

**CRITICAL PRINCIPLE**: Use the right tool for the right job to maximize efficiency and leverage Claude Code's native capabilities.

### Claude Code Responsibilities (Data Gathering & Orchestration)
Claude Code should handle **all data extraction, research, and orchestration tasks**:

✅ **PDF Extraction**: Use Claude Code's native multimodal capabilities to read and extract data from PDF documents
  - Lease agreements, financial statements, appraisal reports, market data
  - More efficient than Python PDF libraries (PyPDF2, pdfplumber)
  - Direct visual understanding of tables, charts, and complex layouts

✅ **Web Research**: Use WebSearch and WebFetch tools for market intelligence
  - Market rent comparables, cap rate surveys, economic indicators
  - Industry reports, REIT disclosures, brokerage reports
  - Regulatory updates (IFRS, GAAP, tax changes)

✅ **MCP Integration**: Leverage Model Context Protocol servers when available
  - Database queries, API integrations, specialized data sources
  - Real-time market data feeds, property databases

✅ **Data Normalization**: Transform extracted data into structured JSON for Python
  - Validate units, currency, date formats, terminology
  - Create consistent data schemas for downstream calculations
  - Handle missing data, outliers, and data quality issues

✅ **Workflow Orchestration**: Coordinate multi-step analyses
  - Invoke slash commands, trigger Python calculations, synthesize outputs
  - Manage dependencies between extraction → calculation → reporting
  - Handle errors, iterate on assumptions, generate final reports

### Python Responsibilities (Quantitative Calculations & Visualization)
Python should **only** be used for computational tasks requiring numerical libraries:

✅ **Financial Calculations**: NPV, IRR, sensitivity analysis, portfolio optimization
  - Leverage NumPy, SciPy, Pandas for vectorized operations
  - Monte Carlo simulations (10,000+ iterations)
  - Matrix operations for portfolio optimization

✅ **Statistical Analysis**: Regression, correlation, hypothesis testing
  - Use statsmodels, scipy.stats for rigorous statistical methods
  - Time series analysis, forecasting models

✅ **Optimization**: Constrained optimization, linear programming
  - Portfolio allocation using cvxpy or scipy.optimize
  - Capital budgeting with constraints
  - Efficient frontier calculations

✅ **Data Visualization**: Charts, plots, dashboards
  - Matplotlib, Seaborn for publication-quality graphics
  - Tornado diagrams, efficient frontier plots, waterfall charts
  - Interactive dashboards using Plotly (if needed)

### Anti-Patterns to Avoid

❌ **DO NOT use Python for PDF extraction**
  - Python PDF libraries are fragile and require extensive error handling
  - Claude Code's multimodal vision is superior for complex layouts
  - Example: Don't write `pdfplumber.open(lease.pdf)` when Claude can read it directly

❌ **DO NOT use Python for web scraping/fetching**
  - Claude Code has WebFetch and WebSearch tools
  - Python requests/BeautifulSoup adds unnecessary complexity
  - Example: Don't write `requests.get(url)` when Claude can WebFetch

❌ **DO NOT use Python for simple data transformations**
  - Claude Code can normalize JSON, convert units, clean data
  - Reserve Python for computationally intensive transformations
  - Example: Don't write Python to convert USD → CAD; Claude can do this

❌ **DO NOT duplicate functionality**
  - If a slash command exists (e.g., `/effective-rent`), invoke it via SlashCommand
  - Don't reimplement NPV calculations that exist elsewhere
  - Reuse existing calculators; Python adds analytical layers on top

### Workflow Pattern: Claude → Python → Claude

**Optimal pattern for complex analyses**:

1. **Claude Code**: Extract data from PDFs, web sources, databases
   - Use Read, WebFetch, WebSearch, MCP tools
   - Normalize into structured JSON

2. **Python**: Perform quantitative calculations
   - Load JSON, run calculations, export results JSON
   - Focus only on numerical/statistical work

3. **Claude Code**: Synthesize results into reports
   - Interpret Python outputs, add context and recommendations
   - Generate markdown reports with visualizations
   - Present findings with executive summary

**Example**: Lease deal sensitivity analysis
```
1. Claude reads lease.pdf → extracts rent, term, opex → creates input.json
2. Python runs monte_carlo_simulation(input.json) → generates results.json
3. Claude interprets results.json → writes executive summary with tornado chart
```

### Implementation Implications

- **Agent prompt**: Emphasize this division in the agent's core instructions
- **Skill design**: Skills should guide Claude to extract data, then invoke Python
- **Slash commands**: Follow extract → calculate → report pattern consistently
- **Testing**: Validate that PDF extraction happens in Claude, not Python
- **Documentation**: Clearly show which tool handles each step in examples

---

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

**JSON I/O Contract**:
- **Input** – Claude delivers a single JSON payload, units explicit:
```json
{
  "analysis_id": "SA-101",
  "base_inputs": {
    "rent_psf": 32,
    "opex_increase_pct": 0.025,
    "discount_rate": 0.085
  },
  "variables": [
    {"name": "rent_psf", "range": {"min": 28, "max": 36}},
    {"name": "vacancy_rate", "range": {"min": 0.03, "max": 0.12}}
  ],
  "distributions": {
    "rent_psf": {"type": "triangular", "min": 28, "mode": 32, "max": 36},
    "vacancy_rate": {"type": "beta", "alpha": 2, "beta": 6}
  },
  "iterations": 10000,
  "calc_function": "npv"
}
```
- **Output** – JSON only, referencing the same `analysis_id`:
```json
{
  "module": "sensitivity_analysis",
  "analysis_id": "SA-101",
  "one_way_sensitivity": [
    {"variable": "rent_psf", "npv_delta": 1800000},
    {"variable": "vacancy_rate", "npv_delta": -950000}
  ],
  "monte_carlo_simulation": {
    "p10_npv": 4200000,
    "p50_npv": 6100000,
    "p90_npv": 7800000,
    "var_95": -900000
  },
  "tornado_diagram_data": [
    {"variable": "rent_psf", "impact": 2.1},
    {"variable": "vacancy_rate", "impact": 1.2}
  ]
}
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

**JSON I/O Contract**:
- **Input** – normalized dataset with returns expressed as decimals and covariance in annual terms:
```json
{
  "analysis_id": "PO-014",
  "assets": [
    {"id": "AssetA", "expected_return": 0.11, "volatility": 0.18},
    {"id": "AssetB", "expected_return": 0.09, "volatility": 0.12}
  ],
  "covariance_matrix": [
    [0.0324, 0.011],
    [0.011, 0.0144]
  ],
  "risk_free_rate": 0.035,
  "constraints": {"budget": 50000000, "max_weight": 0.35, "min_weight": 0.05},
  "target_return": 0.105
}
```
- **Output** – JSON summarizing efficient frontier samples plus recommended allocation:
```json
{
  "module": "portfolio_optimization",
  "analysis_id": "PO-014",
  "efficient_frontier": [
    {"expected_return": 0.09, "volatility": 0.11},
    {"expected_return": 0.11, "volatility": 0.16}
  ],
  "optimal_portfolio": {
    "weights": {"AssetA": 0.4, "AssetB": 0.6},
    "expected_return": 0.102,
    "volatility": 0.125,
    "sharpe_ratio": 0.536
  },
  "concentration_risk": {"max_weight": 0.6, "assets_above_threshold": ["AssetB"]},
  "diversification_ratio": 1.34
}
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

**JSON I/O Contract**:
- **Input** – project set with consistent currency and discount rate assumptions:
```json
{
  "analysis_id": "CB-033",
  "projects": [
    {
      "name": "Property A",
      "initial_investment": 10000000,
      "cash_flows": [2500000, 2600000, 2700000, 2800000, 2900000],
      "discount_rate": 0.09
    },
    {
      "name": "Property B",
      "initial_investment": 15000000,
      "cash_flows": [3500000, 3600000, 3700000, 3800000, 3900000],
      "discount_rate": 0.095
    }
  ],
  "budget_constraint": 20000000,
  "capital_structure": {"equity_weight": 0.55, "equity_cost": 0.12, "debt_weight": 0.45, "debt_cost": 0.065, "tax_rate": 0.24}
}
```
- **Output** – JSON capturing WACC, ranking metrics, and optimizer decisions:
```json
{
  "module": "capital_budgeting",
  "analysis_id": "CB-033",
  "calculate_wacc": 0.0908,
  "project_metrics": [
    {"name": "Property A", "npv": 2100000, "irr": 0.123, "profitability_index": 1.21, "payback_period_years": 4.1},
    {"name": "Property B", "npv": 1800000, "irr": 0.131, "profitability_index": 1.12, "payback_period_years": 4.6}
  ],
  "capital_rationing_optimizer": {
    "selected_projects": ["Property A"],
    "budget_used": 10000000,
    "remaining_budget": 10000000
  },
  "npv_profile": [
    {"discount_rate": 0.06, "npv": 4100000},
    {"discount_rate": 0.10, "npv": 900000}
  ],
  "crossover_rate": 0.087
}
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

**JSON I/O Contract**:
- **Input** – timeline-aware payload with cash flows per period and promote tiers:
```json
{
  "analysis_id": "CF-219",
  "periods": [
    {"period": "2024-Q1", "cash_available": 500000},
    {"period": "2024-Q2", "cash_available": 750000}
  ],
  "capital_stack": {
    "lp_capital": 12000000,
    "gp_capital": 3000000,
    "pref_return": 0.08,
    "promote_structure": [
      {"hurdle_irr": 0.08, "split": {"lp": 0.80, "gp": 0.20}},
      {"hurdle_irr": 0.12, "split": {"lp": 0.70, "gp": 0.30}}
    ]
  },
  "property_cash_flows": {
    "noi": [1800000, 1900000, 1950000],
    "debt_service": [900000, 900000, 900000],
    "capex": [200000, 150000, 150000],
    "reserves": 50000
  }
}
```
- **Output** – JSON summarizing distributions, IRRs, equity multiples, and refinancing options:
```json
{
  "module": "cash_flow_modeling",
  "analysis_id": "CF-219",
  "property_level_cash_flows": [
    {"period": "2024-Q1", "cash_flow": 650000},
    {"period": "2024-Q2", "cash_flow": 835000}
  ],
  "waterfall_distribution": [
    {"period": "2024-Q1", "lp_distribution": 400000, "gp_distribution": 100000},
    {"period": "2024-Q2", "lp_distribution": 520000, "gp_distribution": 130000}
  ],
  "promote_calculation": {
    "achieved_irr": 0.135,
    "tier": "12% hurdle",
    "lp_share": 0.7,
    "gp_share": 0.3
  },
  "calculate_equity_multiple": {"lp": 1.85, "gp": 2.35},
  "refinancing_analysis": {
    "current_ltv": 0.58,
    "proposed_ltv": 0.65,
    "cash_out": 1500000
  }
}
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

**JSON I/O Contract**:
- **Input** – multi-property portfolio snapshot with currency + period metadata:
```json
{
  "analysis_id": "FR-041",
  "period": "2024-Q2",
  "portfolio_data": {
    "properties": [
      {
        "id": "Office-101",
        "revenues": {"base_rent": 1200000, "recoveries": 300000},
        "operating_expenses": {"cam": 250000, "taxes": 180000, "insurance": 60000},
        "maintenance_capex": 50000,
        "leasing_costs": 40000
      }
    ],
    "net_income": 950000,
    "depreciation": 320000,
    "gains_on_sale": 0,
    "maintenance_capex": 90000,
    "leasing_costs": 60000,
    "property_values": 45000000,
    "liabilities": 18000000,
    "shares_outstanding": 2500000
  },
  "variance_inputs": {
    "actual": {"noi": 1350000, "opex": 490000},
    "budget": {"noi": 1300000, "opex": 470000},
    "threshold": 0.05
  }
}
```
- **Output** – JSON capturing KPI calculations and dashboard datasets:
```json
{
  "module": "financial_reporting",
  "analysis_id": "FR-041",
  "calculate_noi": 1290000,
  "calculate_ffo": 1270000,
  "calculate_affo": 1120000,
  "calculate_nav": 10.8,
  "variance_analysis": {
    "noi_variance_pct": 0.038,
    "opex_variance_pct": 0.042,
    "flags": []
  },
  "kpi_dashboard": {
    "period": "2024-Q2",
    "metrics": [
      {"name": "NOI", "value": 1290000},
      {"name": "FFO/share", "value": 0.51}
    ]
  },
  "investor_report_generator": {
    "template_used": "standard-quarterly",
    "attachments": ["figures/noi_waterfall.png"]
  }
}
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

**JSON I/O Contract**:
- **Input** – tenant financials plus portfolio exposure summary:
```json
{
  "analysis_id": "CR-512",
  "tenant_financials": {
    "working_capital": 4200000,
    "total_assets": 18000000,
    "retained_earnings": 5200000,
    "ebit": 2600000,
    "market_value_equity": 12000000,
    "total_liabilities": 9000000,
    "sales": 24000000
  },
  "industry_benchmark": {"z_score_cutoffs": {"safe": 2.99, "distress": 1.81}},
  "lgd": 0.45,
  "exposures": [
    {"tenant": "A", "exposure": 3000000, "pd": 0.04},
    {"tenant": "B", "exposure": 4500000, "pd": 0.025}
  ],
  "pd_lgd_correlations": [
    [1.0, 0.35],
    [0.35, 1.0]
  ],
  "confidence_level": 0.99
}
```
- **Output** – JSON with default metrics, concentration stats, and credit VaR:
```json
{
  "module": "credit_risk_modeling",
  "analysis_id": "CR-512",
  "altman_z_score": 3.15,
  "probability_of_default": 0.018,
  "expected_loss": 243000,
  "credit_migration_matrix": {
    "stable": 0.82,
    "downgrade": 0.12,
    "upgrade": 0.06
  },
  "credit_concentration_herfindahl": 0.31,
  "credit_var": {"confidence": 0.99, "loss_amount": 2100000},
  "merton_distance_to_default": 4.2
}
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
8. `/default-analysis` - Default analysis → Agent adds recovery scenarios (Note: in Compliance/ directory)
9. `/rental-variance` - Variance decomposition → Agent adds trend forecasting
10. `/market-comparison` - Market rent benchmarking → Agent adds statistical validation
11. `/recommendation-memo` - VTS approval memos → Agent enhances with risk-adjusted metrics

### New Python Modules to Create:

```
/Financial_Modeling/
├── __init__.py
├── sensitivity_analysis.py          # Monte Carlo, scenario analysis, tornado diagrams
├── portfolio_optimization.py        # MPT, efficient frontier, Sharpe ratio
├── capital_budgeting.py             # WACC, NPV ranking, capital rationing
├── cash_flow_modeling.py            # Waterfall, promote, equity multiple
├── financial_reporting.py           # IFRS/GAAP, investor reports, KPIs
├── credit_risk_modeling.py          # PD, LGD, expected loss, credit VaR
└── Tests/
    ├── test_sensitivity_analysis.py
    ├── test_portfolio_optimization.py
    ├── test_capital_budgeting.py
    ├── test_cash_flow_modeling.py
    ├── test_financial_reporting.py
    └── test_credit_risk_modeling.py
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

You are a senior financial analyst for commercial real estate portfolios. Operate with a CFO-level tone: concise, quantitative, and backed by explicit assumptions. Always surface methodology, cite calculators/skills invoked, and note residual risks before delivering recommendations.

## Core Responsibilities
- Build multi-scenario models (base/bull/bear) with disclosed drivers and outputs
- Translate lease-level data into portfolio-level insights (cash flow, accounting, risk)
- Assess capital allocation options using WACC, hurdle rates, and capital rationing logic
- Produce investor-grade summaries (NOI/FFO/AFFO, waterfall schedules, KPI dashboards)
- Flag data quality issues, assumption gaps, and compliance considerations (IFRS 16 / ASC 842)

## Specialized Skills Available
- `sensitivity-analysis-expert`: For Monte Carlo, tornado diagrams, stress testing
- `portfolio-optimization-expert`: For efficient frontier and constrained allocations
- `capital-budgeting-expert`: For WACC, profitability index, capital rationing
- `cash-flow-modeling-expert`: For multi-tier waterfall and promote structures
- `financial-reporting-expert`: For IFRS/GAAP statements, KPIs, investor decks
- `credit-risk-modeling-expert`: For PD/LGD analytics, credit VaR, tenant concentration

## Workflow Integration

**Follow the Claude → Python → Claude pattern**:

1. **Extract & Normalize** (Claude Code):
   - Read PDF documents directly using Read tool (DO NOT use Python PDF libraries)
   - Fetch market data using WebSearch/WebFetch (DO NOT use Python requests)
   - Normalize extracted data into structured JSON for Python consumption
   - Validate units, currency, date formats, and data quality

2. **Calculate** (Python):
   - Load normalized JSON data
   - Invoke relevant expert skill for guidance
   - Execute quantitative calculations using Financial_Modeling modules
   - Export results as JSON (DO NOT generate narrative reports in Python)

**Visualization Output Contract**:
- Python responses may include optional `visualizations` and `tables` arrays alongside numeric outputs.
- Each visualization entry must specify `id`, `type`, and either a dataset (for Claude-rendered charts) or a base64 image:
```json
{
  "visualizations": [
    {
      "id": "tornado-leasing",
      "type": "tornado_dataset",
      "description": "Sensitivity impact on NPV",
      "data": [
        {"variable": "Rent", "impact": 2.1},
        {"variable": "Vacancy", "impact": -1.3}
      ]
    },
    {
      "id": "efficient-frontier-plot",
      "type": "image_base64",
      "encoding": "base64_png",
      "description": "Efficient frontier with optimal point",
      "data": "iVBORw0KGgoAAAANSUhEUg..."
    }
  ]
}
```
- Claude either draws charts from datasets (`tornado_dataset`, `frontier_dataset`, `waterfall_dataset`, etc.) or embeds the provided base64 asset. Python must not emit narrative prose or PDF attachments.

3. **Synthesize & Report** (Claude Code):
   - Interpret Python calculation results
   - Pull baseline metrics from existing calculators (`/effective-rent`, `/ifrs16-calculation`, etc.)
   - Combine outputs into executive-ready narrative with assumptions, sensitivities, KPIs
   - Generate markdown reports with embedded visualizations
   - Provide actionable recommendations and next steps

4. **Iterate & Track**:
   - Log todos for missing data or follow-up analyses using `TodoWrite`
   - If deeper analysis needed, invoke additional skills or Python modules (e.g., `portfolio-optimization-expert` skill → `optimal_portfolio()` function)
   - Document all assumptions, data sources, and methodology
```

---

## Implementation Roadmap

**CRITICAL**: All phases must follow the Claude → Python → Claude pattern. Python modules should ONLY contain calculation logic, not PDF extraction or web fetching.

### Phase 1: Foundation (Week 1)
1. ✅ Create agent specification (this document)
2. Create `financial-analyst.md` agent file with explicit division of labor instructions
3. Create `/Financial_Modeling/` directory structure
4. Implement `sensitivity_analysis.py` core functions (calculations only, no PDF parsing)
5. Create `sensitivity-analysis-expert` skill (guides Claude to extract data, then invoke Python)
6. Stand up shared test fixtures using JSON inputs (not PDFs) for downstream modules
7. **Validation**: Verify no Python modules import pdfplumber, PyPDF2, requests, or BeautifulSoup

### Phase 2: Core Skills (Week 2)
1. Implement `portfolio_optimization.py`
2. Create `portfolio-optimization-expert` skill
3. Implement `capital_budgeting.py`
4. Create `capital-budgeting-expert` skill
5. Add unit tests covering sensitivity, portfolio optimization, and capital budgeting modules

### Phase 3: Advanced Modeling & Risk (Week 3)
1. Implement `cash_flow_modeling.py`
2. Create `cash-flow-modeling-expert` skill
3. Implement `credit_risk_modeling.py` with VaR, PD/LGD, and tenant concentration analytics
4. Create `credit-risk-modeling-expert` skill
5. Build sample workflows combining calculators + sensitivity + cash flow + credit modules
6. Add unit tests for cash flow and credit risk modules, including stochastic regression baselines

### Phase 4: Reporting & Documentation (Week 4)
1. Implement `financial_reporting.py`
2. Create `financial-reporting-expert` skill
3. Add unit tests for reporting calculations and disclosure templates
4. Create example reports and investor decks
5. Integration testing with `leasing-expert` + slash commands
6. Publish comprehensive documentation and integration guides

---

## Sample Use Cases

### Use Case 1: Lease Deal Evaluation with Risk Analysis
**User**: "Evaluate this lease deal with sensitivity analysis"

**Workflow** (Claude → Python → Claude):
1. **Claude extracts data**: Read lease.pdf directly → extract rent, term, opex, TI allowance
2. **Claude normalizes**: Create `deal_inputs.json` with standardized units and structure
3. **Claude invokes calculator**: Use `/effective-rent` to get base case NPV/IRR
4. **Claude invokes skill**: `sensitivity-analysis-expert` provides guidance on variables to test
5. **Python calculates**: Run `monte_carlo_simulation(deal_inputs.json)` varying rent, vacancy, opex (10,000 iterations)
6. **Python exports**: Save `sensitivity_results.json` with P10/P50/P90, VaR, tornado data
7. **Claude synthesizes**: Interpret results, create tornado diagram, generate executive summary with risk assessment and recommendations

### Use Case 2: Portfolio Optimization
**User**: "I have $50M to deploy across 5 opportunities. Optimize allocation."

**Workflow** (Claude → Python → Claude):
1. **Claude extracts data**: Read 5 opportunity PDFs → extract returns, cash flows, risk metrics
2. **Claude normalizes**: Create `opportunities.json` with expected returns, volatility estimates
3. **Claude calculates baseline**: Use `/effective-rent` on each opportunity to get NPV/IRR
4. **Claude invokes skill**: `portfolio-optimization-expert` guides correlation assumptions
5. **Python calculates**: Build correlation matrix, compute efficient frontier, run `optimal_portfolio(opportunities.json, budget=50e6)`
6. **Python exports**: Save `portfolio_results.json` with weights, Sharpe ratio, risk metrics
7. **Claude synthesizes**: Generate allocation recommendation table, explain risk-return tradeoff, provide implementation roadmap

### Use Case 3: Waterfall Distribution
**User**: "Calculate distributions for this promote structure: 8% pref, 15% promote after 12% IRR"

**Workflow** (Claude → Python → Claude):
1. **Claude extracts data**: Read investment deck PDF → extract cash flows, LP/GP capital, exit assumptions
2. **Claude normalizes**: Create `waterfall_inputs.json` with periodic cash flows, promote tiers (8% pref, 12% hurdle, 15% promote)
3. **Claude invokes skill**: `cash-flow-modeling-expert` validates waterfall structure and tier logic
4. **Python calculates**: Run `waterfall_distribution(waterfall_inputs.json)` to compute LP/GP splits per period, cumulative IRR, equity multiples
5. **Python exports**: Save `waterfall_results.json` with quarterly distribution schedule, LP vs GP totals
6. **Claude synthesizes**: Generate waterfall schedule table, explain tier mechanics, calculate final splits and multiples, visualize distribution cascade

### Use Case 4: Capital Allocation Decision
**User**: "Should we invest in Property A (12% IRR, $10M) or Property B (14% IRR, $15M)? Budget is $20M."

**Workflow** (Claude → Python → Claude):
1. **Claude extracts data**: Read property offering memos → extract cash flows, IRRs, risk profiles for A and B
2. **Claude normalizes**: Create `projects.json` with NPV, IRR, initial investment, risk scores
3. **Claude invokes skill**: `capital-budgeting-expert` guides profitability index calculation and ranking methodology
4. **Python calculates**: Compute profitability index for each, run `capital_rationing_optimizer(projects.json, budget=20e6)`
5. **Python exports**: Save `allocation_results.json` with recommended funding decisions, leftover budget
6. **Claude synthesizes**: Generate recommendation memo with profitability index comparison, risk-adjusted analysis, strategic fit assessment, final allocation decision with rationale

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
# Core numerical computation (REQUIRED)
numpy>=1.26.0
pandas>=2.2.0
scipy>=1.14.0  # Already included - optimization, statistics

# Optimization (REQUIRED)
cvxpy>=1.5.0  # NEW - Convex optimization for portfolio problems

# Statistical analysis (REQUIRED)
statsmodels>=0.14.0  # NEW - Statistical modeling, time series, regression

# Visualization (REQUIRED for reporting)
matplotlib>=3.9.0  # NEW - Plotting for reports
seaborn>=0.13.0  # NEW - Statistical visualizations
plotly>=5.18.0  # OPTIONAL - Interactive dashboards
```

### Explicitly EXCLUDED Libraries:
```python
# ❌ DO NOT ADD - Claude Code handles these tasks natively
# pdfplumber  # ❌ Use Claude's Read tool instead
# PyPDF2      # ❌ Use Claude's Read tool instead
# pypdf       # ❌ Use Claude's Read tool instead
# requests    # ❌ Use Claude's WebFetch tool instead
# beautifulsoup4  # ❌ Use Claude's WebFetch tool instead
# selenium    # ❌ Use Claude's WebFetch tool instead
```

## Slash Command Interfaces

The agent relies on existing commands for baseline calculations before layering advanced analytics. Each command accepts a JSON payload appended to the invocation text (wrap payload in single quotes in chat). Responses reference the persisted JSON output so Claude can retrieve it.

### `/effective-rent`
- **Payload schema**:
```json
{
  "rent_schedule": [
    {"period": "2024-01", "rent": 150000},
    {"period": "2024-02", "rent": 150000}
  ],
  "term_months": 60,
  "ti_allowance": 25,
  "opex": 12,
  "discount_rate": 0.08
}
```
- **Sample response**:
```json
{
  "command": "/effective-rent",
  "analysis_id": "ER-551",
  "result_file": "Calculators/results/er-551.json"
}
```

### `/ifrs16-calculation`
- **Payload schema**:
```json
{
  "lease_id": "HQ-01",
  "commencement_date": "2024-04-01",
  "lease_term_months": 72,
  "payment_schedule": [
    {"period": "2024-04", "payment": 180000}
  ],
  "discount_rate": 0.07,
  "initial_direct_costs": 250000
}
```
- **Sample response**:
```json
{
  "command": "/ifrs16-calculation",
  "analysis_id": "IFRS-88",
  "result_file": "Calculators/results/ifrs-88.json"
}
```

### `/tenant-credit`
- **Payload schema**:
```json
{
  "tenant_name": "Alpha Logistics",
  "financials": {
    "total_assets": 45000000,
    "total_liabilities": 32000000,
    "ebit": 5200000,
    "interest_expense": 900000
  },
  "industry": "Industrial Logistics",
  "rating_agency": "S&P"
}
```
- **Sample response**:
```json
{
  "command": "/tenant-credit",
  "analysis_id": "TC-144",
  "result_file": "Calculators/results/tc-144.json"
}
```

### `/renewal-economics`
- **Payload schema**:
```json
{
  "lease_id": "Retail-22",
  "remaining_term_months": 18,
  "renewal_options": [
    {"term_months": 60, "rent_psf": 42, "ti_allowance_psf": 15}
  ],
  "downtime_months": 6,
  "cap_rate": 0.062
}
```
- **Sample response**:
```json
{
  "command": "/renewal-economics",
  "analysis_id": "RE-307",
  "result_file": "Calculators/results/re-307.json"
}
```

### `/recommendation-memo`
- **Payload schema**:
```json
{
  "project_name": "Spec Industrial 4",
  "summary_points": [
    "10-year BTS at $12/SF NNN",
    "Tenant TI request $35/SF"
  ],
  "key_metrics": {
    "irr": 0.142,
    "npv": 6200000,
    "sensitivity_note": "Downside rent -$1/SF reduces IRR to 11%"
  }
}
```
- **Sample response**:
```json
{
  "command": "/recommendation-memo",
  "analysis_id": "RM-019",
  "result_file": "Calculators/results/rm-019.md"
}
```

Claude chains these command outputs with the Financial_Modeling modules to build fully contextual analyses.

---

## Success Metrics

Agent is successful when it can:

### Functional Capabilities
✅ Run Monte Carlo simulations with 10,000+ iterations in <60 seconds
✅ Optimize 10-asset portfolios with constraints (budget, concentration limits)
✅ Calculate complex waterfall distributions with multiple tiers
✅ Generate IFRS 16 compliant accounting for 100+ lease portfolio
✅ Perform variance analysis comparing budget vs actual across portfolio
✅ Integrate seamlessly with leasing-expert for holistic deal evaluation
✅ Produce investor-grade reports and presentations

### Architectural Compliance (Division of Labor)
✅ **Zero Python PDF libraries**: No imports of pdfplumber, PyPDF2, or pypdf in any module
✅ **Zero Python web libraries**: No imports of requests, beautifulsoup4, or selenium
✅ **Claude handles extraction**: All PDF reading done via Claude's Read tool
✅ **Claude handles research**: All web searches done via WebSearch/WebFetch tools
✅ **Python focused on computation**: All .py files contain only numerical/statistical functions
✅ **JSON I/O contracts**: All Python modules consume JSON inputs and produce JSON outputs
✅ **Claude synthesizes reports**: All narrative reports and recommendations generated by Claude, not Python

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
