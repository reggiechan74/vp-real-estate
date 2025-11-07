# Market Intelligence Agent - Specification Plan

## Agent Overview

**Name**: `market-intelligence`

**Purpose**: Market research, competitive analysis, and data-driven market insights for commercial real estate portfolio strategy. Complements `leasing-expert` by providing deep market context, competitive intelligence, and predictive analytics.

**Distinct Value**: While `leasing-expert` uses market context for deal evaluation, `market-intelligence` specializes in systematic market data collection, competitive property analysis, trend forecasting, and strategic market positioning.

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

## Required Claude Code Skills

### Priority 1: Essential Skills (Create First)

#### 1. **market-data-extraction-expert**

**Description**: Expert in extracting, parsing, and normalizing market data from broker reports, MLS listings, and commercial real estate documents. Use when processing CBRE/Colliers market reports, extracting data from PDF rent surveys, parsing MLS availability listings, normalizing data across sources, identifying data quality issues, or building market databases. Key terms include PDF extraction, data normalization, broker reports, MLS data, market survey, vacancy data, asking rent, net effective rent, data cleaning, OCR.

**What it does**:
- Extracts tables and data from broker marketing PDFs
- Parses MLS listing data into structured format
- Normalizes data across different broker formats
- Identifies and flags data quality issues
- Builds time-series market databases
- Handles OCR for scanned documents

**Python functions needed**:
```python
# market_data_extraction.py
def extract_tables_from_pdf(pdf_path, table_patterns)
def parse_mls_listing(listing_text, property_type)
def normalize_property_size(size_string, unit_type)
def normalize_rent_format(rent_string, basis="psf_year")
def clean_address_data(address_dict, geocode=True)
def detect_data_quality_issues(data_df, rules)
def merge_data_sources(sources_list, deduplication_rules)
def build_time_series(historical_data, frequency="quarterly")
```

---

#### 2. **competitive-analysis-expert**

**Description**: Expert in competitive property analysis, benchmarking, and market positioning for commercial real estate assets. Use when identifying comparable properties, benchmarking rents and concessions, analyzing competitive amenities and features, evaluating market positioning, assessing competitive threats, or building competitive intelligence profiles. Key terms include comparable properties, competitive set, market positioning, amenity analysis, rent benchmarking, concession comparison, competitive advantage, market share, tenant mix, occupancy rates.

**What it does**:
- Identifies true comparable properties (location, size, quality, age)
- Builds competitive set profiles with detailed amenities
- Benchmarks rent, concessions, and lease terms
- Analyzes tenant mix and credit quality across comps
- Scores competitive positioning (location, quality, services)
- Identifies competitive gaps and opportunities

**Python functions needed**:
```python
# competitive_analysis.py
def identify_comparables(subject_property, market_inventory, criteria)
def amenity_comparison_matrix(properties_list, amenity_categories)
def rent_benchmarking(subject_rent, comp_rents, adjustments)
def concession_analysis(properties_list, metric="months_free_rent")
def tenant_mix_comparison(subject_tenants, comp_tenants)
def competitive_positioning_score(subject, comps, weights)
def market_share_analysis(portfolio_properties, total_market)
def competitive_gap_analysis(subject_features, comp_features)
```

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

**Description**: Expert in analyzing commercial real estate transaction data including sales and lease comps for market valuation. Use when analyzing recent sales transactions, extracting lease comps, calculating cap rates and price per square foot, evaluating transaction volume trends, identifying buyer/seller profiles, or benchmarking transaction terms. Key terms include sales comps, lease comps, cap rate, price per SF, transaction volume, buyer profile, comparable sales, market liquidity, going-in cap rate, terminal cap rate.

**What it does**:
- Analyzes recent sales transaction comps
- Extracts and normalizes lease transaction data
- Calculates cap rates and price per SF metrics
- Tracks transaction volume and velocity
- Identifies buyer/seller trends and profiles
- Benchmarks transaction terms (earnest money, due diligence, closing timeline)

**Python functions needed**:
```python
# transaction_analysis.py
def sales_comp_analysis(subject_property, sales_data, adjustment_factors)
def calculate_cap_rate(noi, sale_price)
def price_per_sf_distribution(sales_data, property_type, period)
def transaction_volume_trend(historical_transactions, frequency="quarterly")
def buyer_seller_profile(transactions, buyer_types, seller_types)
def lease_comp_extraction(lease_transactions, filters)
def going_in_vs_terminal_cap(pro_forma_data, holding_period)
def market_liquidity_index(transaction_volume, inventory, time_on_market)
```

---

## API Access & Data Sources

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
# Geospatial analysis
geopandas>=0.14.0  # NEW - Geographic data analysis
folium>=0.16.0  # NEW - Interactive maps
shapely>=2.0.0  # NEW - Geometric operations

# Time series forecasting
statsmodels>=0.14.0  # Already in financial-analyst spec
prophet>=1.1.0  # NEW - Facebook's forecasting library

# Advanced visualization
plotly>=5.20.0  # NEW - Interactive charts
dash>=2.17.0  # NEW - Web dashboards (optional)

# API access
fredapi>=0.5.0  # NEW - Federal Reserve Economic Data
census>=0.8.0  # NEW - US Census Bureau API wrapper
```

### Existing Libraries (Already Available):
- `pandas`, `numpy` - Data manipulation
- `requests`, `beautifulsoup4` - Web scraping
- `markitdown`, `pypdf` - PDF processing
- `openpyxl` - Excel integration
- `scipy` - Statistical functions

---

## New Python Modules to Create

```
/Market_Intelligence/
├── __init__.py
├── market_data_extraction.py       # PDF parsing, data normalization
├── competitive_analysis.py         # Comp identification, benchmarking
├── market_forecasting.py          # Time series, regression, ARIMA
├── submarket_comparison.py        # Geographic analysis, location scoring
├── data_visualization.py          # Charts, maps, dashboards
├── transaction_analysis.py        # Sales/lease comps, cap rates
├── api_integrations/
│   ├── __init__.py
│   ├── census_api.py              # US Census data
│   ├── bls_api.py                 # Bureau of Labor Statistics
│   ├── fred_api.py                # Federal Reserve Economic Data
│   ├── google_places_api.py       # Google Places/Maps
│   └── broker_report_parser.py    # CBRE/Colliers PDF parser
└── Tests/
    ├── test_market_data_extraction.py
    ├── test_competitive_analysis.py
    ├── test_market_forecasting.py
    └── test_submarket_comparison.py
```

---

## Integration with Existing Tools

### Leverage Existing:
1. **MLS_Extractor** (`excel_formatter.py`) - Already extracts MLS PDFs to Excel
   - Agent will enhance with additional normalization and analysis

2. **Relative_Valuation** (`relative_valuation_calculator.py`) - MCDA ranking
   - Agent will add market context and competitive intelligence layer

3. **Shared_Utils** (`financial_utils.py`) - Statistical functions
   - Agent will use existing statistical utilities

### New Slash Commands to Create:

```bash
/extract-market-data <pdf-path> [--source-type] [--property-type]
/competitive-analysis <subject-property> <market-area> [--radius]
/forecast-market <submarket> <metric> [--periods]
/submarket-comparison <submarkets-list> [--metrics]
/location-score <address> [--factors]
/transaction-comps <subject-property> <transaction-type> [--period]
```

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
- market-data-extraction-expert
- competitive-analysis-expert
- market-forecasting-expert
- submarket-comparison-expert
- data-visualization-expert
- transaction-analysis-expert

## API Access & Data Sources
[Integration with Census, BLS, FRED, Google Places, broker reports]

## Workflow Integration
[How to use skills + APIs + slash commands + existing calculators]
```

---

## Sample Use Cases

### Use Case 1: Market Entry Analysis
**User**: "Should we enter the Mississauga industrial market? Analyze opportunity."

**Workflow**:
1. Invokes `market-data-extraction-expert` to extract CBRE/Colliers Mississauga reports
2. Invokes `submarket-comparison-expert` to compare Mississauga vs other GTA submarkets
3. Uses Census API to get demographic/employment data
4. Invokes `market-forecasting-expert` to project vacancy and rent growth
5. Invokes `competitive-analysis-expert` to profile existing competition
6. Generates comprehensive market entry report with recommendation

### Use Case 2: Competitive Benchmarking
**User**: "How does our 2550 Stanfield property compare to competition?"

**Workflow**:
1. Invokes `competitive-analysis-expert` to identify comps within 5km
2. Uses `/extract-mls` to get current listings data
3. Invokes `competitive-analysis-expert` to build amenity comparison matrix
4. Benchmarks rent ($12.50/SF vs market $11.80/SF → 6% premium)
5. Identifies competitive gaps (e.g., competitors have truck courts, we don't)
6. Generates competitive positioning report with recommendations

### Use Case 3: Rent Growth Forecasting
**User**: "Forecast Markham office rent growth for next 2 years"

**Workflow**:
1. Invokes `market-data-extraction-expert` to compile historical Markham office rents (10 years)
2. Uses FRED API to get economic indicators (GDP, employment, rates)
3. Invokes `market-forecasting-expert` to build ARIMA forecast model
4. Analyzes correlation between economic indicators and rent growth
5. Considers supply pipeline impact (500K SF delivering in 18 months)
6. Generates forecast: +2.5% Year 1, +1.8% Year 2 with confidence intervals

### Use Case 4: Transaction Comp Analysis
**User**: "What are recent industrial sales comps for our Milton property?"

**Workflow**:
1. Invokes `transaction-analysis-expert` to identify sales within 10km, last 12 months
2. Extracts transaction data from broker reports and public records
3. Calculates cap rates and $/SF metrics with adjustments
4. Analyzes buyer profiles and transaction velocity
5. Benchmarks subject property against comps
6. Generates comp analysis: Market cap rate 5.8%, subject estimated at 5.6% (premium location)

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1)
1. ✅ Create agent specification (this document)
2. Create `market-intelligence.md` agent file
3. Set up `/Market_Intelligence/` directory structure
4. Implement `market_data_extraction.py` core functions
5. Create `market-data-extraction-expert` skill

### Phase 2: Competitive Analysis (Week 2)
1. Implement `competitive_analysis.py`
2. Create `competitive-analysis-expert` skill
3. Build integration with existing MLS_Extractor
4. Create example competitive analysis reports
5. Add unit tests

### Phase 3: Forecasting & Analytics (Week 3)
1. Implement `market_forecasting.py` with ARIMA/regression
2. Create `market-forecasting-expert` skill
3. Implement `submarket_comparison.py`
4. Create `submarket-comparison-expert` skill
5. Integrate Census, BLS, FRED APIs

### Phase 4: Visualization & APIs (Week 4)
1. Implement `data_visualization.py` with Plotly/Folium
2. Create `data-visualization-expert` skill
3. Implement all API integrations (Census, BLS, FRED, Google Places)
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
│   ├── economic_indicators/      # Census, BLS, FRED data (cached)
│   └── time_series_db/           # Historical market metrics
└── cache/
    ├── api_cache/                # API responses (1-7 day TTL)
    └── processed_data/           # Normalized datasets
```

### Data Refresh Strategy
- **Broker reports**: Manual upload, quarterly parsing
- **MLS data**: Weekly refresh (if API available) or manual
- **Economic indicators**: Monthly refresh via APIs (automated)
- **Transaction data**: Quarterly compilation
- **Cache TTL**: 1 day for fast-changing, 7 days for stable data

### Data Quality
- Automated validation rules for extracted data
- Flagging of outliers and anomalies
- Version control for data processing scripts
- Audit trail for data transformations

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

✅ Extract market data from 90%+ of broker PDF reports automatically
✅ Identify relevant comps within 10km radius with 95%+ accuracy
✅ Forecast rent growth within ±2% of actual (backtested)
✅ Generate comprehensive market reports in <5 minutes
✅ Score location quality with objective, replicable methodology
✅ Build competitive intelligence database covering 500+ properties
✅ Integrate seamlessly with leasing-expert and financial-analyst agents
✅ Produce investor-grade market research and presentations

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
2. **API Key Setup**: Register for Census, BLS, FRED, Google Places APIs
3. **Create Agent File**: Write `market-intelligence.md` based on spec
4. **Implement Priority 1 Skills**: market-data-extraction, competitive-analysis, market-forecasting, submarket-comparison
5. **Build API Integrations**: Census, BLS, FRED wrappers with caching
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

# 2. Create .env file (never commit to git)
cat > .env << 'EOF'
CENSUS_API_KEY=your_census_key_here
BLS_API_KEY=your_bls_key_here
FRED_API_KEY=your_fred_key_here
GOOGLE_PLACES_API_KEY=your_google_key_here
EOF

# 3. Add python-dotenv to requirements.txt
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
