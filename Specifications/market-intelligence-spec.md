# Market Intelligence Agent - Specification Plan

## Agent Overview

**Name**: `market-intelligence`

**Purpose**: Market research, competitive analysis, and data-driven market insights for commercial real estate portfolio strategy. Complements `leasing-expert` by providing deep market context, competitive intelligence, and predictive analytics.

**Distinct Value**: While `leasing-expert` uses market context for deal evaluation, `market-intelligence` specializes in systematic market data collection, competitive property analysis, trend forecasting, and strategic market positioning.

**Geography**: Supports both Canadian and U.S. markets with mirrored data pipelines for each.

## Core Competencies

### 1. Market Data Collection
- Systematic extraction from broker reports (CBRE, Colliers, JLL, Cushman)
- MLS data aggregation and normalization
- Transaction data compilation (sales, leases)
- Construction pipeline tracking (supply analysis)
- Historical market data archiving and trending

### 2. Competitive Property Analysis
- Comp property identification and profiling
- Amenity and feature comparison matrices
- Rent and concession benchmarking
- Occupancy and tenant mix analysis
- Building quality and age adjustments

### 3. Market Trend Forecasting
- Absorption rate projections
- Vacancy rate forecasting
- Rent growth modeling
- Supply pipeline impact analysis
- Economic indicator correlation (GDP, employment, interest rates)

### 4. Submarket Analysis
- Geographic market segmentation
- Submarket performance comparison
- Location quality scoring (transportation, amenities, demographics)
- Trade area analysis and drive-time polygons
- Demographic and employment data integration

### 5. Strategic Intelligence
- Market opportunity identification (undersupplied submarkets, emerging trends)
- Competitive threat assessment
- Tenant demand analysis by industry/size
- Market cycle positioning (early/mid/late expansion, contraction)
- Entry/exit timing recommendations

## Division of Labor: Claude Code vs Python

**CRITICAL PRINCIPLE**: Use the right tool for the right job to maximize efficiency and leverage Claude Code's native capabilities.

### Claude Code Responsibilities (Data Gathering & Orchestration)
Claude Code should handle **all data extraction, research, and orchestration tasks**:

✅ **PDF Extraction**: Use Claude Code's native multimodal capabilities to read broker reports and market documents
  - CBRE, Colliers, JLL, Cushman & Wakefield market reports
  - MLS listing PDFs and marketing materials
  - Transaction data, appraisals, market surveys
  - More efficient than Python PDF libraries (PyPDF2, pdfplumber)
  - Direct visual understanding of tables, charts, maps, and complex layouts

✅ **Web Research**: Use WebSearch and WebFetch tools for market intelligence
  - Broker websites, public market reports, economic data portals
  - REIT disclosures, press releases, market news
  - Municipal building permit portals, zoning information
  - NO Python requests/BeautifulSoup - use Claude's native tools

✅ **API Integration**: Use Claude Code to orchestrate API calls and MCP servers
  - Call Census, BLS, FRED, Statistics Canada, CMHC, Bank of Canada APIs
  - Leverage MCP servers when available for specialized data sources
  - Handle authentication, rate limiting, error handling at orchestration layer
  - Transform API responses into structured JSON for Python

✅ **Data Normalization**: Transform extracted data into structured JSON for Python
  - Standardize units ($/SF/year, SF vs SM, etc.)
  - Validate addresses, coordinates, property types
  - Handle missing data, outliers, inconsistent formats
  - Create consistent data schemas for downstream calculations

✅ **Workflow Orchestration**: Coordinate multi-step market analyses
  - Invoke slash commands, trigger Python calculations, synthesize outputs
  - Manage dependencies between extraction → calculation → reporting
  - Handle errors, iterate on assumptions, generate final reports

### Python Responsibilities (Quantitative Analysis & Visualization)
Python should **only** be used for computational tasks requiring numerical libraries:

✅ **Statistical Analysis**: Time series, regression, forecasting models
  - ARIMA/Prophet for rent growth and vacancy forecasting
  - Regression analysis for economic correlation
  - Statistical validation and hypothesis testing

✅ **Geospatial Calculations**: Location scoring, distance calculations, trade area analysis
  - Drive-time polygon calculations using geopandas/shapely
  - Distance matrices, proximity scoring
  - Geographic clustering and density analysis

✅ **Competitive Scoring**: Quantitative benchmarking and ranking
  - Multi-criteria decision analysis (MCDA) scoring
  - Statistical benchmarking with adjustments
  - Percentile ranking, z-scores, normalization

✅ **Data Visualization**: Charts, maps, dashboards
  - Plotly/Seaborn for market trend charts
  - Folium for interactive geographic maps
  - Dashboard generation (Dash/Streamlit)
  - Export visualizations for reports

### Anti-Patterns to Avoid

❌ **DO NOT use Python for PDF extraction**
  - Python PDF libraries (pdfplumber, PyPDF2, pypdf) are fragile
  - Broker reports have complex layouts (tables, charts, maps)
  - Claude Code's multimodal vision is superior
  - Example: Don't write `pdfplumber.open(cbre_report.pdf)` when Claude can read it directly

❌ **DO NOT use Python for web scraping/fetching**
  - Claude Code has WebFetch and WebSearch tools
  - Python requests/BeautifulSoup adds unnecessary complexity
  - Respect ToS by using Claude's built-in tools
  - Example: Don't write `requests.get(broker_url)` when Claude can WebFetch

❌ **DO NOT use Python for API orchestration**
  - Claude Code should handle API calls and credential management
  - Python only processes the JSON data Claude provides
  - Claude handles rate limiting, caching, error handling
  - Example: Claude calls Census API → passes JSON to Python for analysis

❌ **DO NOT use Python for simple data transformations**
  - Claude Code can normalize addresses, standardize units, clean data
  - Reserve Python for complex statistical transformations
  - Example: Don't write Python to convert $/SF/month → $/SF/year; Claude can do this

### Workflow Pattern: Claude → Python → Claude

**Optimal pattern for market intelligence workflows**:

1. **Claude Code**: Extract data from PDFs, APIs, web sources
   - Read broker reports using Read tool
   - Call Census/BLS/FRED/Statistics Canada/CMHC APIs using WebFetch or Bash
   - Extract MLS listings from PDFs
   - Normalize into structured JSON

2. **Python**: Perform quantitative analysis
   - Load normalized JSON data
   - Run statistical models (forecasting, regression, clustering)
   - Generate geospatial calculations
   - Create visualizations
   - Export results JSON

3. **Claude Code**: Synthesize results into market intelligence
   - Interpret Python outputs, add market context
   - Combine quantitative results with qualitative insights
   - Generate markdown reports with embedded visualizations
   - Present findings with executive summary and recommendations

**Example**: Market rent forecasting
```
1. Claude reads CBRE Q4 2024 report.pdf → extracts historical rent data → creates rents.json
2. Claude calls FRED API → gets GDP, employment data → creates economic_indicators.json
3. Python loads JSONs → runs ARIMA forecast → generates forecast_results.json with confidence intervals
4. Claude interprets results → writes market report with forecast chart and strategic implications
```

### Implementation Implications

- **Skill design**: Skills guide Claude to extract data first, then invoke Python for calculations
- **Python modules**: All .py files consume JSON inputs, produce JSON outputs - NO PDF/web libraries
- **API wrappers**: Minimal - Claude handles API calls, Python just processes data
- **Testing**: Validate that extraction happens in Claude, Python only gets JSON
- **Documentation**: Clearly show which tool handles each step

---

## Required Claude Code Skills

### Priority 1: Essential Skills (Create First)

#### 1. **market-data-normalization-expert**

**Description**: Expert in normalizing and validating market data extracted by Claude Code from broker reports, MLS listings, and market documents. Use when standardizing property sizes and units, normalizing rent formats, validating addresses and coordinates, detecting data quality issues, merging data from multiple sources, or building time-series market databases. Key terms include data normalization, unit conversion, data validation, quality checks, time series, data merging, standardization, geocoding, outlier detection.

**What it does**:
- **Normalizes property data** that Claude has extracted from PDFs (NOT extracting from PDFs itself)
- Standardizes units (SF to SM, $/SF/month to $/SF/year, etc.)
- Validates addresses, coordinates, property classifications
- Detects outliers and data quality issues using statistical methods
- Merges data from multiple sources with deduplication logic
- Builds time-series databases from historical data

**Important**: This skill does NOT extract from PDFs. Claude Code reads PDFs and passes raw extracted data to Python for normalization.

**Python functions needed**:
```python
# market_data_normalization.py (renamed from market_data_extraction.py)
# NOTE: All functions receive JSON data already extracted by Claude Code

def normalize_property_size(size_value, from_unit, to_unit="sf")
def normalize_rent_format(rent_value, from_basis, to_basis="psf_year")
def validate_address_data(address_dict, geocode=True)
def detect_outliers(data_df, column, method="iqr", threshold=1.5)
def detect_data_quality_issues(data_df, validation_rules)
def merge_data_sources(sources_list, deduplication_rules, conflict_resolution="latest")
def build_time_series(historical_data, date_column, value_column, frequency="quarterly")
def standardize_property_type(property_type_string, taxonomy="standard")
```

---

#### 2. **competitive-analysis-expert**

**Description**: Expert in competitive property analysis, benchmarking, and market positioning for commercial real estate assets. Use when analyzing lease concessions, comparing tenant mix across properties, identifying competitive gaps, or calculating market share. Leverages existing Relative_Valuation module for comp identification, amenity comparison, and positioning scores. Key terms include concession analysis, tenant mix, competitive gap, market share, free rent, TI allowance, tenant quality, occupancy comparison.

**What it does**:
- Analyzes lease concessions (free rent, TI allowances, rent abatement)
- Compares tenant mix and credit quality across competitive properties
- Identifies competitive gaps (missing amenities, service deficiencies)
- Calculates portfolio market share by submarket
- **Leverages existing functionality:** Uses `/relative-valuation` for comp identification, amenity ranking, and competitive positioning scores (no duplication)

**Python functions needed (extends Relative_Valuation module):**
```python
# Add to Relative_Valuation/relative_valuation_calculator.py (extends existing)
# NOTE: Do NOT duplicate existing functions (identify_comparables, amenity_comparison_matrix,
# rent_benchmarking, competitive_positioning_score - these already exist in Relative_Valuation)

def concession_analysis(properties_list, metric="months_free_rent")  # NEW
def tenant_mix_comparison(subject_tenants, comp_tenants)  # NEW
def competitive_gap_analysis(subject_features, comp_features)  # NEW
def market_share_analysis(portfolio_properties, total_market)  # NEW
```

**Integration with existing code:**
- ✅ Use existing `Relative_Valuation/relative_valuation_calculator.py` for comp identification (already has 25-variable ranking)
- ✅ Use existing MCDA scoring for competitive positioning (don't duplicate)
- ✅ Add only NEW functions for concession/tenant mix analysis

---

#### 3. **market-forecasting-expert**

**Description**: Expert in commercial real estate market forecasting using time series analysis, regression modeling, and economic indicators. Use when forecasting rent growth, projecting vacancy rates, modeling absorption trends, analyzing supply pipeline impact, correlating economic indicators with market performance, or evaluating market cycle timing. Key terms include time series forecasting, ARIMA, regression analysis, absorption rate, vacancy forecast, rent growth projection, supply pipeline, market cycle, leading indicators, correlation analysis.

**What it does**:
- Forecasts rent growth using historical trends and economic data
- Projects vacancy rates considering supply pipeline
- Models absorption rates by property type and submarket
- Analyzes correlation between economic indicators and market metrics
- Identifies market cycle position (expansion/contraction)
- Quantifies forecast uncertainty (confidence intervals)

**Python functions needed**:
```python
# market_forecasting.py
def forecast_rent_growth(historical_rents, periods=8, method="arima")
def forecast_vacancy(historical_vacancy, supply_pipeline, absorption)
def absorption_model(deliveries, demand_drivers, lag_periods)
def economic_correlation_matrix(market_data, economic_indicators)
def market_cycle_classifier(metrics_dict, thresholds)
def regression_forecast(dependent_var, independent_vars, forecast_periods)
def confidence_intervals(forecast, confidence_level=0.95)
def supply_demand_gap_analysis(supply_pipeline, demand_forecast)
```

---

#### 4. **submarket-comparison-expert**

**Description**: Expert in geographic submarket analysis, location scoring, and trade area evaluation for commercial real estate. Use when comparing submarket performance, scoring location quality, analyzing demographic profiles, evaluating transportation access, calculating drive-time trade areas, assessing employment centers proximity, or identifying emerging submarkets. Key terms include submarket analysis, location scoring, demographics, drive time, trade area, employment density, transportation access, walkability score, amenity density, emerging markets.

**What it does**:
- Compares performance metrics across submarkets (rent, vacancy, absorption)
- Scores location quality (transportation, amenities, demographics)
- Analyzes trade areas using drive-time polygons
- Evaluates demographic and employment characteristics
- Identifies emerging/declining submarkets
- Recommends optimal locations for acquisition/development

**Python functions needed**:
```python
# submarket_comparison.py
def submarket_performance_matrix(submarkets_data, metrics_list)
def location_quality_score(location_data, weights, scoring_model)
def drive_time_trade_area(location_coords, drive_times=[5, 10, 15])
def demographic_profile(trade_area_polygon, census_data)
def employment_density_analysis(trade_area, employment_data)
def transportation_score(location, transit_data, highway_access)
def amenity_density(location, radius, amenity_types)
def submarket_trend_classifier(historical_data, trend_threshold)
```

---

### Priority 2: Supporting Skills (Create After Priority 1)

#### 5. **data-visualization-expert**

**Description**: Expert in creating compelling data visualizations, interactive dashboards, and presentation-ready charts for market analysis. Use when creating market reports, building interactive dashboards, generating executive presentations, visualizing geographic data on maps, creating time series trend charts, or producing investor-facing market materials. Key terms include data visualization, dashboard, heat map, time series chart, scatter plot, geographic mapping, interactive charts, executive presentation, infographics.

**What it does**:
- Creates presentation-quality charts and graphs
- Builds interactive dashboards (Plotly Dash, Streamlit)
- Generates geographic heat maps and choropleth maps
- Produces time series trend visualizations
- Designs executive-ready market summary slides
- Exports visualizations for reports and presentations

**Python functions needed**:
```python
# data_visualization.py
def market_summary_dashboard(market_data, property_type, period)
def rent_growth_time_series(historical_rents, forecast=None)
def vacancy_heat_map(submarket_data, geographic_boundaries)
def competitive_radar_chart(subject_property, comps, dimensions)
def supply_pipeline_waterfall(deliveries_by_quarter, demand_absorption)
def scatter_plot_with_regression(x_data, y_data, labels)
def geographic_bubble_map(locations, size_metric, color_metric)
def export_for_powerpoint(chart_object, filename, format="png")
```

---

#### 6. **transaction-analysis-expert**

**Description**: Expert in analyzing commercial real estate transaction data including sales and lease comps for market valuation. Use when analyzing recent sales transactions, extracting lease comps, evaluating transaction volume trends, identifying buyer/seller profiles, calculating market liquidity metrics, or analyzing price per SF distributions. Leverages existing Shared_Utils for cap rate calculations. Key terms include sales comps, lease comps, cap rate, price per SF, transaction volume, buyer profile, comparable sales, market liquidity, going-in cap rate, terminal cap rate.

**What it does**:
- Analyzes recent sales transaction comps with adjustment factors
- Extracts and normalizes lease transaction data
- Tracks transaction volume and velocity trends
- Identifies buyer/seller trends and profiles
- Calculates market liquidity metrics
- Analyzes price per SF distributions and trends
- **Leverages existing functionality:** Uses `Shared_Utils.financial_utils.calculate_cap_rate()` (no duplication)

**Python functions needed**:
```python
# transaction_analysis.py
from Shared_Utils.financial_utils import calculate_cap_rate  # REUSE existing - DO NOT duplicate

def sales_comp_analysis(subject_property, sales_data, adjustment_factors)  # NEW
def price_per_sf_distribution(sales_data, property_type, period)  # NEW
def transaction_volume_trend(historical_transactions, frequency="quarterly")  # NEW
def buyer_seller_profile(transactions, buyer_types, seller_types)  # NEW
def lease_comp_extraction(lease_transactions, filters)  # NEW
def going_in_vs_terminal_cap(pro_forma_data, holding_period)  # NEW
def market_liquidity_index(transaction_volume, inventory, time_on_market)  # NEW
```

**Integration with existing code:**
- ✅ Import `calculate_cap_rate()` from `Shared_Utils/financial_utils.py` (don't duplicate)
- ✅ All new functions focus on market-level transaction analysis, not individual cap rate math

---

## API Access & Data Sources

Agent must support both U.S. and Canadian portfolios, so each workflow should call out an equivalent data source north and south of the border. All paid subscriptions and API credentials (CoStar, Altus, CMHC, Google, etc.) are owned and provisioned by the user; the agent only reads credentials from environment variables or the secrets manager.

### Commercial Data Providers (Subscription Required)

#### Tier 1: Premium APIs ($$$$)
1. **CoStar API**
   - **Coverage**: Comprehensive US commercial real estate data
   - **Data**: Properties, comps, tenants, market analytics, forecasts
   - **Cost**: $50K-$200K+/year enterprise subscription
   - **Integration**: RESTful API with rate limits
   - **Priority**: HIGH if budget available

2. **Real Capital Analytics (RCA)**
   - **Coverage**: Transaction data (sales, portfolios)
   - **Data**: Cap rates, pricing, buyer/seller profiles
   - **Cost**: $30K-$100K+/year
   - **Integration**: Data exports, limited API
   - **Priority**: MEDIUM for transaction analysis

3. **REIS (Moody's Analytics)**
   - **Coverage**: Market trends and forecasts
   - **Data**: Vacancy, rent, absorption, supply
   - **Cost**: $20K-$80K+/year
   - **Integration**: Data exports, Excel plugin
   - **Priority**: MEDIUM for forecasting

#### Tier 2: Broker Research (Free/Low Cost)
1. **CBRE Research Reports**
   - **Coverage**: Major markets, quarterly updates
   - **Data**: Market snapshots, trends, forecasts
   - **Cost**: Free (public reports) or relationship-based
   - **Integration**: PDF extraction required
   - **Priority**: HIGH (best free source)

2. **Colliers Market Reports**
   - **Coverage**: Select markets, quarterly
   - **Data**: Vacancy, rent, inventory
   - **Cost**: Free (public website)
   - **Integration**: PDF extraction
   - **Priority**: HIGH

3. **JLL Research**
   - **Coverage**: Global markets
   - **Data**: Market trends, forecasts
   - **Cost**: Free (public)
   - **Integration**: PDF extraction
   - **Priority**: MEDIUM

4. **Cushman & Wakefield**
   - **Coverage**: Major markets
   - **Data**: Market snapshots
   - **Cost**: Free (public)
   - **Integration**: PDF extraction
   - **Priority**: MEDIUM

#### Tier 3: Government & Public APIs (Free)

1. **US Census Bureau API**
   - **Coverage**: Demographics, employment, economics
   - **Data**: Population, income, education, employment
   - **Cost**: FREE
   - **Integration**: RESTful API, well-documented
   - **Priority**: HIGH for demographic analysis
   - **API Key**: Required (free)
   - **Docs**: https://www.census.gov/data/developers/data-sets.html

2. **Bureau of Labor Statistics (BLS) API**
   - **Coverage**: Employment, wages, CPI
   - **Data**: Employment trends by MSA, industry wages
   - **Cost**: FREE
   - **Integration**: RESTful API
   - **Priority**: HIGH for economic correlation
   - **API Key**: Required (free)
   - **Docs**: https://www.bls.gov/developers/

3. **FRED (Federal Reserve Economic Data) API**
   - **Coverage**: Economic indicators
   - **Data**: GDP, interest rates, unemployment, inflation
   - **Cost**: FREE
   - **Integration**: RESTful API
   - **Priority**: HIGH for forecasting
   - **API Key**: Required (free)
   - **Docs**: https://fred.stlouisfed.org/docs/api/fred/

4. **Google Places API**
   - **Coverage**: Location data, amenities
   - **Data**: Nearby amenities, transit, ratings
   - **Cost**: FREE tier (limited), then pay-per-use
   - **Integration**: RESTful API
   - **Priority**: MEDIUM for location scoring
   - **API Key**: Required

5. **OpenStreetMap (Overpass API)**
   - **Coverage**: Geographic/mapping data
   - **Data**: Roads, transit, points of interest
   - **Cost**: FREE
   - **Integration**: RESTful API, rate limited
   - **Priority**: MEDIUM for mapping
   - **API Key**: Not required

#### Tier 3B: Canadian Government & Public APIs (Free/Low Cost)

1. **Statistics Canada Web Data Service**
   - **Coverage**: National demographic, labour, and economic tables
   - **Data**: CANSIM tables for population, employment, GDP by metro, building permits
   - **Cost**: FREE
   - **Integration**: REST/JSON, supports bulk table downloads
   - **Priority**: HIGH for Canadian demographic/economic inputs
   - **API Key**: Not required

2. **CMHC Housing Market Information Portal**
   - **Coverage**: Rental market surveys, construction/absorption
   - **Data**: Vacancy, rents, completions for major Canadian CMAs
   - **Cost**: FREE (registration for bulk download)
   - **Integration**: CSV/Excel exports; automate via authenticated HTTPS
   - **Priority**: HIGH for Canadian supply/demand modeling

3. **Bank of Canada Valet API**
   - **Coverage**: Macro-economic and interest rate series
   - **Data**: Policy rate, bond yields, exchange rates
   - **Cost**: FREE
   - **Integration**: JSON API with date filters
   - **Priority**: MEDIUM for forecasting Canadian cap rates
   - **Docs**: https://www.bankofcanada.ca/valet/

4. **Provincial / Municipal Open Data (e.g., Ontario Data Catalogue, City of Toronto, City of Vancouver)**
   - **Coverage**: Assessment rolls, building permits, zoning, mobility, amenities
   - **Data**: Parcel data, development applications, transit feeds, points of interest
   - **Cost**: FREE
   - **Integration**: Mix of REST APIs and CSV exports; respect municipal terms
   - **Priority**: MEDIUM for location scoring and pipeline tracking

5. **Altus InSite / REALNet (Subscription)**
   - **Coverage**: Canadian commercial inventory, transactions, construction pipeline
   - **Data**: Rent comps, vacancy, deal velocity for industrial/office assets
   - **Cost**: $$$ (enterprise subscription handled by user)
   - **Integration**: Data downloads / API (depending on contract)
   - **Priority**: HIGH when available for Tier-1 Canadian markets

#### Tier 4: MLS & Local Sources (Varies)

1. **Local Commercial MLS Systems**
   - **Coverage**: Regional (e.g., TREB Commercial, LoopNet)
   - **Data**: Listings, leases, sales
   - **Cost**: Varies (subscription or member access)
   - **Integration**: Often manual/scraping (no official API)
   - **Priority**: HIGH for local markets
   - **Note**: Respect Terms of Service

2. **Municipal Building Permit Data**
   - **Coverage**: Local jurisdictions
   - **Data**: Construction permits, development pipeline
   - **Cost**: FREE (public records)
   - **Integration**: Varies (some have APIs, most are portals)
   - **Priority**: MEDIUM for supply pipeline

---

## Python Modules & Libraries

### New Dependencies (Add to requirements.txt):

```python
# Core numerical computation (REQUIRED)
numpy>=1.26.0
pandas>=2.2.0
scipy>=1.14.0

# Geospatial analysis (REQUIRED)
geopandas>=0.14.0  # NEW - Geographic data analysis
folium>=0.16.0  # NEW - Interactive maps
shapely>=2.0.0  # NEW - Geometric operations

# Time series forecasting (REQUIRED)
statsmodels>=0.14.0  # Already in financial-analyst spec
prophet>=1.1.0  # NEW - Facebook's forecasting library (heavy - requires C++ toolchain)

# Advanced visualization (REQUIRED)
plotly>=5.20.0  # NEW - Interactive charts
seaborn>=0.13.0  # NEW - Statistical visualizations
dash>=2.17.0  # OPTIONAL - Web dashboards

# API access - MINIMAL wrappers only
fredapi>=0.5.0  # NEW - Federal Reserve Economic Data wrapper
census>=0.8.0  # NEW - US Census Bureau API wrapper
# NOTE: Claude Code should orchestrate API calls; these are lightweight helpers only

# Excel integration (existing)
openpyxl>=3.1.0  # Excel read/write
```

### Explicitly EXCLUDED Libraries:
```python
# ❌ DO NOT ADD - Claude Code handles these tasks natively

# PDF extraction (Claude Code's Read tool is superior)
# pdfplumber  # ❌ Use Claude's Read tool instead
# PyPDF2      # ❌ Use Claude's Read tool instead
# pypdf       # ❌ Use Claude's Read tool instead
# camelot-py  # ❌ Use Claude's Read tool instead
# tabula-py   # ❌ Use Claude's Read tool instead

# Web scraping (Claude Code's WebFetch/WebSearch tools are better)
# requests    # ❌ Use Claude's WebFetch/Bash for API calls
# beautifulsoup4  # ❌ Use Claude's WebFetch tool instead
# selenium    # ❌ Use Claude's WebFetch tool instead
# scrapy      # ❌ Use Claude's WebFetch tool instead

# OCR (Claude Code has multimodal vision)
# pytesseract # ❌ Use Claude's Read tool with vision
# pdf2image   # ❌ Use Claude's Read tool instead
```

### Rationale for Exclusions:
- **PDF extraction**: Claude's multimodal vision directly reads complex broker reports (tables, charts, maps) more accurately than brittle Python PDF parsers
- **Web scraping**: Claude's WebFetch respects ToS and rate limits; Python scraping adds legal/technical risk
- **API calls**: Claude orchestrates API calls (auth, rate limiting, caching); Python only processes the JSON responses
- **OCR**: Claude's vision understands scanned documents; no need for pytesseract

### Infrastructure Requirements for Heavy Dependencies
- `prophet` pulls in `cmdstanpy` and requires a working C++ toolchain (gcc/g++ ≥ 9, make) plus ~1 GB of disk for compiled Stan models. Recommend baking these into the Docker image or leveraging a build stage that installs `build-essential`, `gfortran`, and `libomp`.
- `geopandas`, `shapely`, and `folium` rely on native GEOS/PROJ/GDAL libraries. Use an Ubuntu 22.04 (or Alpine edge with musl tweaks) base image that preinstalls `gdal-bin`, `libgdal-dev`, `libgeos-dev`, and `proj-bin` to avoid pip wheel compilation failures.
- Visualization stacks (`plotly`, `dash`) benefit from Node.js or `xvfb` only when server-side rendering screenshots. Document whether dashboards run inside the agent container or an external Dash service and provision CPU/GPU accordingly.
- For local development, publish a `poetry export`/`requirements.txt` plus a sample `Dockerfile` that mirrors CI so contributors are not forced to install heavy GIS/Stan toolchains on their laptops.

---

## New Python Modules to Create

**IMPORTANT**: These modules contain ONLY calculation/analysis logic. Claude Code handles all PDF extraction, web fetching, and API calls.

```
/Market_Intelligence/
├── __init__.py
├── market_data_normalization.py    # Data standardization, validation, quality checks (NOT PDF extraction)
├── market_forecasting.py          # Time series models (ARIMA, Prophet), regression, statistical forecasting
├── submarket_comparison.py        # Geographic analysis, location scoring algorithms, trade area calculations
├── data_visualization.py          # Chart/map generation (Plotly, Folium, Seaborn)
├── transaction_analysis.py        # Sales comp analysis, transaction trends, liquidity metrics (imports cap_rate from Shared_Utils)
└── Tests/
    ├── test_market_data_normalization.py  # Test unit conversions, validation rules, outlier detection
    ├── test_market_forecasting.py         # Test ARIMA/Prophet models with known datasets
    ├── test_submarket_comparison.py       # Test location scoring, distance calculations
    ├── test_data_visualization.py         # Plotly spec validation + snapshot regression
    └── test_transaction_analysis.py       # Transaction volume, buyer/seller profiles, liquidity metrics
```

**Extended existing modules (not new files)**:
- ✅ `Relative_Valuation/relative_valuation_calculator.py` - Add concession_analysis(), tenant_mix_comparison(), competitive_gap_analysis(), market_share_analysis()

**Removed from structure**:
- ❌ `competitive_analysis.py` - **DUPLICATE** - extend existing Relative_Valuation module instead (60% overlap with existing MCDA ranking)
- ❌ `api_integrations/` directory - Claude Code handles API calls directly using Bash/WebFetch
- ❌ `broker_report_parser.py` - Claude Code reads PDFs directly
- ❌ API wrapper modules (census_api.py, bls_api.py, etc.) - Claude orchestrates; Python only processes JSON

**Testing approach**:
- All tests use **JSON input fixtures** (not PDFs or live API calls)
- Visualization tests assert Plotly/Folium JSON specs or PNG snapshot comparisons
- Forecast tests use known historical datasets with verified results
- No tests should read PDFs or make HTTP requests (mocked or real)

---

## Integration with Existing Tools

### Leverage & Extend Existing Modules:

1. **Relative_Valuation** (`relative_valuation_calculator.py`) and `/relative-valuation` command - MCDA ranking
   - **EXTEND** with new functions: `concession_analysis()`, `tenant_mix_comparison()`, `competitive_gap_analysis()`, `market_share_analysis()`
   - **REUSE** existing comp identification, amenity comparison matrix, rent benchmarking, competitive positioning score (25-variable MCDA)
   - **DO NOT DUPLICATE** - 60% of proposed competitive_analysis.py already exists here

2. **MLS_Extractor** (`excel_formatter.py`) and `/extract-mls` command - MLS PDF to Excel extraction
   - Agent will enhance with additional normalization and market-level aggregation

3. **Shared_Utils** (`financial_utils.py`) - Financial calculations
   - **REUSE** existing `calculate_cap_rate()`, `npv()`, `irr()` functions
   - **DO NOT DUPLICATE** - import these functions in transaction_analysis.py
   - Agent adds market-level analytics on top of these building blocks

**Note**: The agent does NOT require new slash commands. It works by:
1. Using **existing slash commands** (e.g., `/extract-mls`, `/relative-valuation`) for data extraction and baseline analysis
2. Invoking **skills** (e.g., `market-data-normalization-expert`, `competitive-analysis-expert`) for analytical guidance
3. Calling **Python modules** directly (e.g., `submarket_performance_matrix()`, `forecast_rent_growth()`) for advanced calculations
4. Synthesizing results into comprehensive market intelligence reports

This approach avoids duplication and leverages existing infrastructure while adding sophisticated market analytics capabilities through the Python modules and skills.

---

## Agent Architecture

### Agent File Structure

```markdown
---
name: market-intelligence
description: Market research, competitive analysis, and data-driven insights specialist. Use when analyzing market trends, identifying comparable properties, forecasting market metrics, comparing submarkets, extracting data from broker reports, or evaluating competitive positioning. Expert in market data collection, competitive intelligence, and predictive analytics.
tools: Read, Glob, Grep, Write, Bash, SlashCommand, TodoWrite, Skill, WebFetch
model: inherit
---

# Market Intelligence Sub-Agent

You are a senior market research analyst specializing in commercial real estate market intelligence...

## Core Responsibilities

### Market Data Collection
- Systematically extract and normalize data from broker reports, MLS, and public sources
- Build and maintain market databases with historical trends
- Track supply pipeline and construction activity
- Monitor transaction activity (sales and leases)

### Competitive Intelligence
- Identify and profile competitive properties
- Benchmark rents, concessions, and terms
- Analyze tenant mix and occupancy across comp set
- Assess competitive positioning and market share

### Market Analytics
- Forecast rent growth and vacancy trends
- Model absorption and supply-demand dynamics
- Analyze submarket performance and demographics
- Identify market opportunities and risks

### Strategic Insights
- Recommend market entry/exit timing
- Identify undersupplied submarkets or niches
- Assess competitive threats and opportunities
- Support acquisition and disposition decisions

## Specialized Skills Available
- market-data-normalization-expert
- competitive-analysis-expert
- market-forecasting-expert
- submarket-comparison-expert
- data-visualization-expert
- transaction-analysis-expert

## Workflow Integration

**Follow the Claude → Python → Claude pattern**:

1. **Extract & Research** (Claude Code):
   - Read broker reports, MLS PDFs, market documents using Read tool (DO NOT use Python PDF libraries)
   - Call APIs (Census, BLS, FRED, Statistics Canada, CMHC, Bank of Canada) using Bash or WebFetch (DO NOT use Python requests)
   - Search web for market intelligence using WebSearch/WebFetch (DO NOT use Python web scraping)
   - Normalize extracted data into structured JSON for Python consumption
   - Validate data quality, standardize units, handle missing values

2. **Analyze & Calculate** (Python):
   - Load normalized JSON data
   - Invoke relevant expert skill for guidance
   - Execute quantitative analysis using Market_Intelligence modules:
     - Statistical forecasting (ARIMA, Prophet, regression)
     - Geospatial calculations (location scoring, trade areas)
     - Competitive benchmarking and MCDA ranking
     - Data visualization (Plotly charts, Folium maps)
   - Export results as JSON (DO NOT generate narrative reports in Python)

3. **Synthesize & Report** (Claude Code):
   - Interpret Python analysis results
   - Add market context, qualitative insights, strategic implications
   - Combine with existing calculator outputs if relevant
   - Generate markdown reports with embedded visualizations
   - Provide actionable recommendations with supporting evidence

4. **Iterate & Monitor**:
   - Track API usage and costs using `TodoWrite`
   - Cache API responses to minimize repeat calls
   - Update market databases with new data
   - Document assumptions, data sources, methodology

## API Access & Data Sources
All API calls orchestrated by Claude Code using Bash/WebFetch. Python only processes the JSON responses.
- Census, BLS, FRED, Statistics Canada, CMHC, Bank of Canada (free government APIs)
- Google Places (free tier, then pay-per-use)
- CoStar, RCA, Altus (enterprise subscriptions, if available)
- Broker reports (CBRE, Colliers, JLL, C&W) via PDF extraction
```

---

## Sample Use Cases

### Use Case 1: Market Entry Analysis
**User**: "Should we enter the Mississauga industrial market? Analyze opportunity."

**Workflow** (Claude → Python → Claude):
1. **Claude extracts data**: Read CBRE/Colliers Mississauga Q4 2024 reports (PDFs) → extract vacancy, rent, absorption, supply pipeline
2. **Claude fetches economic data**: Call Statistics Canada API (using Bash) → get employment/GDP data for Mississauga CMA → create `economic_indicators.json`
3. **Claude normalizes**: Create `mississauga_market.json` with standardized units, property types, date formats
4. **Claude invokes skill**: `submarket-comparison-expert` guides comparison methodology
5. **Python calculates**: Run `submarket_performance_matrix()` comparing Mississauga vs other GTA submarkets
6. **Claude invokes skill**: `market-forecasting-expert` guides forecast approach
7. **Python forecasts**: Run ARIMA model on historical rents/vacancy → generate `forecast_results.json` with confidence intervals
8. **Claude invokes skill**: `competitive-analysis-expert` guides competitive profiling
9. **Python analyzes**: Calculate competitive density, market concentration metrics
10. **Claude synthesizes**: Generate comprehensive market entry report with recommendation (Enter/Don't Enter), risk assessment, optimal timing, and strategic positioning advice

### Use Case 2: Competitive Benchmarking
**User**: "How does our 2550 Stanfield property compare to competition?"

**Workflow** (Claude → Python → Claude):
1. **Claude extracts subject data**: Read property file for 2550 Stanfield → extract size, rent, amenities, tenant profile
2. **Claude identifies comps**: Use WebSearch to find competitive properties within 5km radius
3. **Claude extracts comp data**: Use `/extract-mls` slash command → get MLS listings data → read competitive property marketing PDFs
4. **Claude normalizes**: Create `subject_property.json` and `competitive_set.json` with standardized features, rents, concessions
5. **Claude invokes existing command**: Use `/relative-valuation` with comp data → get MCDA ranking and competitive positioning score
6. **Claude invokes skill**: `competitive-analysis-expert` guides concession and gap analysis methodology
7. **Python calculates**: Run `concession_analysis()` for free rent/TI analysis, `competitive_gap_analysis()` for feature gaps (uses extended Relative_Valuation module)
8. **Python exports**: Save `benchmarking_results.json` with MCDA ranking results, concession analysis, amenity gaps
9. **Claude synthesizes**: Generate competitive positioning report combining MCDA scores with concession analysis and gap findings (e.g., "Ranked #3 of 8 comps, competitors have truck courts, we don't, average 3 months free rent vs our 2 months"), recommendations for amenity improvements, and rent optimization strategy

### Use Case 3: Rent Growth Forecasting
**User**: "Forecast Markham office rent growth for next 2 years"

**Workflow** (Claude → Python → Claude):
1. **Claude extracts historical data**: Read CBRE/Colliers reports (10 years) → extract Markham office rent time series
2. **Claude fetches economic data**: Call FRED API (using Bash with `curl`) → get GDP, employment, interest rates → create `economic_indicators.json`
3. **Claude fetches supply data**: Read municipal building permit data → extract Markham office construction pipeline (500K SF delivering in 18 months)
4. **Claude normalizes**: Create `markham_rents.json` with quarterly historical rents, economic correlations, supply schedule
5. **Claude invokes skill**: `market-forecasting-expert` guides model selection (ARIMA vs Prophet vs regression)
6. **Python forecasts**: Run ARIMA model on rent time series → calculate economic correlation matrix → adjust for supply impact
7. **Python exports**: Save `rent_forecast.json` with 8-quarter forecast, confidence intervals (P10/P50/P90), supply-adjusted scenarios
8. **Claude synthesizes**: Generate forecast report: +2.5% Year 1, +1.8% Year 2 (base case) with upside/downside scenarios, explain supply pipeline dampening effect, provide strategic implications for lease negotiations

### Use Case 4: Transaction Comp Analysis
**User**: "What are recent industrial sales comps for our Milton property?"

**Workflow** (Claude → Python → Claude):
1. **Claude searches transactions**: Use WebSearch for "Milton industrial sales 2024" → identify recent transactions
2. **Claude extracts transaction data**: Read broker transaction reports, RCA data exports (PDFs) → extract sale price, cap rate, $/SF, buyer/seller, property details
3. **Claude identifies subject**: Read Milton property file → extract NOI, size, age, location attributes
4. **Claude normalizes**: Create `milton_subject.json` and `sales_comps.json` with standardized property attributes, financial metrics
5. **Claude invokes skill**: `transaction-analysis-expert` guides adjustment methodology
6. **Python calculates**: Run `sales_comp_analysis()` with adjustments for size, age, location, quality → calculate adjusted cap rates and $/SF
7. **Python analyzes**: Calculate `transaction_volume_trend()`, `buyer_seller_profile()` for market context
8. **Python exports**: Save `comp_analysis.json` with adjusted metrics, market benchmarks
9. **Claude synthesizes**: Generate comp analysis report: Market cap rate 5.8% (5 comps, adjusted), subject estimated at 5.6% (premium location), transaction velocity analysis, buyer profile insights, valuation recommendation

---

## Implementation Roadmap

**CRITICAL**: All phases must follow the Claude → Python → Claude pattern. Python modules should ONLY contain calculation/analysis logic, not PDF extraction, web scraping, or API orchestration.

### Phase 1: Foundation (Week 1)
1. ✅ Create agent specification (this document)
2. Create `market-intelligence.md` agent file with explicit division of labor instructions
3. Set up `/Market_Intelligence/` directory structure
4. Implement `market_data_normalization.py` core functions (calculations only, no PDF parsing)
5. Create `market-data-normalization-expert` skill (guides Claude to extract data, then invoke Python for normalization)
6. Publish reproducible environment (Dockerfile/devcontainer) with GIS libs + Stan toolchain for geopandas/prophet support
7. **Validation**: Verify no Python modules import pdfplumber, PyPDF2, pypdf, requests, beautifulsoup4, or selenium

### Phase 2: Competitive Analysis Extensions (Week 2)
1. **EXTEND** existing `Relative_Valuation/relative_valuation_calculator.py` (DO NOT create new competitive_analysis.py)
2. Add new functions: `concession_analysis()`, `tenant_mix_comparison()`, `competitive_gap_analysis()`, `market_share_analysis()`
3. Create `competitive-analysis-expert` skill (references extended Relative_Valuation module)
4. Build integration with existing MLS_Extractor for concession data
5. Add unit tests to `Relative_Valuation/tests/` for new functions
6. **Validation**: Confirm no duplication of existing comp identification, amenity comparison, or MCDA scoring functions

### Phase 3: Forecasting & Analytics (Week 3)
1. Implement `market_forecasting.py` with ARIMA/regression
2. Create `market-forecasting-expert` skill
3. Implement `submarket_comparison.py`
4. Create `submarket-comparison-expert` skill
5. Integrate Census, BLS, FRED, Statistics Canada, CMHC, and Bank of Canada APIs

### Phase 4: Visualization & APIs (Week 4)
1. Implement `data_visualization.py` with Plotly/Folium
2. Create `data-visualization-expert` skill
3. Implement all API integrations (Census, BLS, FRED, Google Places, Statistics Canada, CMHC, Bank of Canada)
4. Build example dashboards and interactive reports
5. Comprehensive documentation and examples

### Phase 5: Transaction Analysis (Week 5)
1. Implement `transaction_analysis.py`
2. Create `transaction-analysis-expert` skill
3. Integration testing across all skills
4. Performance optimization
5. Production deployment

---

## Data Management Strategy

### Data Storage
```
/Market_Intelligence/
├── data/
│   ├── broker_reports/           # CBRE, Colliers PDFs (archived)
│   ├── mls_listings/             # Extracted MLS data
│   ├── transactions/             # Sales and lease comps
│   ├── economic_indicators/      # Census, BLS, FRED, Statistics Canada, CMHC data (cached)
│   └── time_series_db/           # Historical market metrics
└── cache/
    ├── api_cache/                # API responses (1-7 day TTL)
    └── processed_data/           # Normalized datasets
```

### Data Refresh Strategy
- **Broker reports**: Manual upload, quarterly parsing
- **MLS data**: Weekly refresh (if API available) or manual
- **Economic indicators**: Monthly refresh via U.S. (Census/BLS/FRED) and Canadian (Statistics Canada/CMHC/Bank of Canada) APIs (automated)
- **Transaction data**: Quarterly compilation
- **Cache TTL**: 1 day for fast-changing, 7 days for stable data

### Data Quality
- Automated validation rules for extracted data
- Flagging of outliers and anomalies
- Version control for data processing scripts
- Audit trail for data transformations

### Security & Compliance Controls
- Encrypt all persisted datasets and caches at rest (e.g., S3 SSE or encrypted volumes) and enforce TLS 1.2+ in transit.
- Store API keys and OAuth tokens exclusively in the secrets manager (Vault, AWS Secrets Manager); never commit them to the repo or logs.
- Apply role-based access control: read-only analysts, read/write data engineers, and restricted production-service accounts.
- Define retention windows (e.g., 18 months for raw MLS extracts, 36 months for normalized time series) and automated purges for expired or sensitive tenant data.
- Enable audit logging for data access and transformations, integrating with SOC2/ISO reporting where applicable.

---

## API Rate Limits & Cost Management

### Free API Tiers (Usage Limits):
- **Census API**: 500 requests/day (typically sufficient)
- **BLS API**: 500 queries/day, 50 requests/query
- **FRED API**: Unlimited requests (fair use)
- **Google Places**: $200/month credit (~28,000 requests), then $0.017/request

### Cost Mitigation Strategies:
1. **Caching**: Cache API responses for 1-30 days depending on data freshness requirements
2. **Batch requests**: Combine multiple queries where possible
3. **Rate limiting**: Implement exponential backoff and respect limits
4. **Fallback**: Use cached data if API limit reached

### Monitoring:
```python
# api_usage_monitor.py
def track_api_usage(api_name, endpoint, response_code, cost=0.0)
def daily_usage_report()
def alert_on_limit_approaching(threshold=0.8)
```

---

## Success Metrics

Agent is successful when it can:

### Functional Capabilities
✅ Extract market data from 90%+ of broker PDF reports (Claude Code reads PDFs, Python normalizes)
✅ Identify relevant comps within 10km radius with 95%+ accuracy
✅ Forecast rent growth with ≤2% MAPE on a rolling 8-quarter walk-forward backtest (per submarket with ≥20 quarters of history and quarterly retraining)
✅ Generate comprehensive market reports in <5 minutes
✅ Score location quality with objective, replicable methodology
✅ Build competitive intelligence database covering 500+ properties
✅ Integrate seamlessly with leasing-expert and financial-analyst agents
✅ Produce investor-grade market research and presentations

**Backtesting cadence**: Retrain and evaluate forecasts quarterly, report QA metrics per asset class/submarket, and require at least 10 eligible markets before declaring the metric met.

### Architectural Compliance (Division of Labor)
✅ **Zero Python PDF libraries**: No imports of pdfplumber, PyPDF2, pypdf, camelot-py, or tabula-py in any module
✅ **Zero Python web scraping libraries**: No imports of requests, beautifulsoup4, selenium, or scrapy
✅ **Zero Python OCR libraries**: No imports of pytesseract or pdf2image
✅ **Claude handles extraction**: All PDF reading done via Claude's Read tool with multimodal vision
✅ **Claude handles web research**: All web searches done via WebSearch/WebFetch tools
✅ **Claude orchestrates APIs**: All API calls made by Claude using Bash/WebFetch; Python only processes JSON responses
✅ **Python focused on analysis**: All .py files contain only normalization, statistical, geospatial, or visualization functions
✅ **JSON I/O contracts**: All Python modules consume JSON inputs and produce JSON outputs
✅ **Claude synthesizes reports**: All narrative reports, strategic insights, and recommendations generated by Claude, not Python
✅ **No API wrappers**: Minimal or no Python API wrapper modules (fredapi/census exceptions allowed as lightweight helpers)

---

## Documentation Deliverables

1. **Agent README**: Overview, capabilities, when to use
2. **Skills Documentation**: Detailed guide for each skill (6 skills)
3. **API Integration Guide**: Setup, authentication, rate limits, best practices
4. **Python Module Docs**: Docstrings and usage examples
5. **Data Dictionary**: All data fields, sources, update frequencies
6. **Example Workflows**: 15+ end-to-end scenarios
7. **Troubleshooting Guide**: Common issues and solutions

---

## Risk Considerations

### Data Access Risks:
- **No CoStar subscription**: Limits comprehensive market coverage → Mitigate with broker reports + MLS
- **MLS access varies**: Not all markets have accessible data → Focus on major markets with good broker coverage
- **API changes**: Public APIs can deprecate endpoints → Version pin and monitor deprecation notices
- **Web scraping ToS**: Some sites prohibit scraping → Only scrape with permission or use public APIs

### Data Quality Risks:
- **Inconsistent formats**: Broker reports vary widely → Build robust parsing with error handling
- **Stale data**: Quarterly reports lag real-time → Supplement with more frequent MLS updates
- **Geographic gaps**: Rural markets poorly covered → Focus on institutional markets (major MSAs)
- **Transaction opacity**: Private sales not reported → Acknowledge limitations in analysis

### Compliance Risks:
- **Copyright**: Broker reports may be copyrighted → Only use for internal analysis, not redistribution
- **Terms of Service**: Violating website ToS → Respect robots.txt and rate limits
- **Data privacy**: Tenant information may be sensitive → Anonymize where appropriate

---

## Next Steps

1. **Review & Approve Spec**: Get user approval on scope and approach
2. **API Key Setup**: User procures and manages credentials/subscriptions for Census, BLS, FRED, Statistics Canada, CMHC, Bank of Canada, Google Places, Altus/CoStar (as available) and stores them in the secrets manager
3. **Create Agent File**: Write `market-intelligence.md` based on spec
4. **Implement Priority 1 Skills**: market-data-extraction, competitive-analysis, market-forecasting, submarket-comparison
5. **Build API Integrations**: Census, BLS, FRED, Statistics Canada, CMHC, Bank of Canada, Google Places wrappers with caching
6. **Integration Testing**: Test agent + skills + APIs + existing tools
7. **Documentation**: Write comprehensive guides and examples

**Estimated Timeline**: 4-5 weeks for full implementation
**Lines of Code**: ~3,000-4,000 lines Python + 2,000-2,500 lines skills/docs
**API Keys Required**: Census (free), BLS (free), FRED (free), Google Places (free tier)

---

## Appendix: API Authentication Setup

### Quick Start Guide

```bash
# 1. Register for free API keys
# Census API: https://api.census.gov/data/key_signup.html
# BLS API: https://data.bls.gov/registrationEngine/
# FRED API: https://fred.stlouisfed.org/docs/api/api_key.html
# Google Places: https://console.cloud.google.com/
# CMHC Portal: https://www.cmhc-schl.gc.ca/en/professionals/housing-markets-data-and-research/housing-data/data-tables
# Bank of Canada Valet (no key required): https://www.bankofcanada.ca/valet/
# Statistics Canada (no key required, but create account for bulk downloads): https://www.statcan.gc.ca/en/developers

# 2. Create .env file (never commit to git)
cat > .env << 'EOF'
CENSUS_API_KEY=your_census_key_here
BLS_API_KEY=your_bls_key_here
FRED_API_KEY=your_fred_key_here
GOOGLE_PLACES_API_KEY=your_google_key_here
EOF

# 3. Add python-dotenv to requirements.txt (only read secrets injected by the user)
echo "python-dotenv>=1.0.0" >> requirements.txt

# 4. Load in Python
from dotenv import load_dotenv
load_dotenv()
census_key = os.getenv('CENSUS_API_KEY')
```

### API Documentation Links:
- Census: https://www.census.gov/data/developers/guidance/api-user-guide.html
- BLS: https://www.bls.gov/developers/api_signature_v2.htm
- FRED: https://fred.stlouisfed.org/docs/api/fred/
- Google Places: https://developers.google.com/maps/documentation/places/web-service
