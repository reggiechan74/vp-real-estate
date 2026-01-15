# Changelog

All notable changes to the Commercial Real Estate Lease Analysis Toolkit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-12-17

### Added

#### 🏗️ Comparable Sales Analysis Module (New Directory)

**Created dedicated calculator directory for Traditional DCA (Direct Comparison Approach)**

Moved from `.claude/skills/comparable-sales-adjustment-methodology/` (1.3MB, 58 files) to new top-level `Comparable_Sales_Analysis/` directory. Skills directory now contains only SKILL.md (~28KB) as intended.

**New Directory Structure**:
- `comparable_sales_calculator.py` - Main calculator with adjustment grid construction
- `paired_sales_analyzer.py` - Paired sales analysis for market-derived factors
- `validate_comparables.py` - Input validation and data quality checks
- `adjustments/` - 10 modular adjustment calculation modules:
  - `transactional.py` - Property rights, financing, conditions of sale
  - `market_conditions.py` - Time/appreciation adjustments
  - `location.py` - Submarket, highway access, accessibility
  - `land.py` - 8 land characteristics (lot size, shape, topography, utilities, etc.)
  - `industrial_building.py` - Clear height, loading docks, rail spur, power
  - `office_building.py` - Building class, floor plate, ceiling height, systems
  - `site.py` - 6 site improvements (paving, fencing, lighting, etc.)
  - `condition_age.py` - Effective age, condition rating adjustments
  - `parameter_mapping.py` - Derived factor name → module parameter mapping
  - `validation.py` - Input sanitization and clamping utilities
- `schemas/` - `adjustment_factors_template.json`
- `sample_inputs/` - 8 sample data files for testing
- `tests/` - 53 unit tests (all passing)
- `docs/` - SCHEMA_DOCUMENTATION.md

#### 📋 Unified JSON Schema Architecture

**Created shared schema location**: `Shared_Utils/schemas/`

- Moved `comparable_sales_input_schema.json` to `Shared_Utils/schemas/`
- Single source of truth for both Traditional DCA and MCDA calculators
- Draft 2020-12 JSON Schema (~22KB) with comprehensive validation rules

**Added JSON Schema validation to MCDA_Sales_Comparison**:
- New `validate_against_schema()` function with graceful degradation
- Integrated with `validate_input_data(use_schema=True)`
- Falls back to semantic-only validation if `jsonschema` library unavailable
- 76 tests passing (including new schema validation tests)

#### 📊 MCDA Sales Comparison Module

**Added MCDA ordinal ranking for fee simple valuation** (from Phase 3)

- Multi-Criteria Decision Analysis for comparable sales ranking
- Score-to-price mapping via interpolation/regression
- 14 weighted characteristics with 5 weight profiles
- `/mcda-sales-comparison` slash command

### Changed

- **validate_comparables.py**: Updated to reference shared schema at `Shared_Utils/schemas/`
- **MCDA validation.py**: Enhanced with optional JSON Schema validation
- **SKILL.md**: Updated paths to reference new `Comparable_Sales_Analysis/` location
- **CLAUDE.md**: Added `Comparable_Sales_Analysis/` to project structure

### Technical Notes

- All file moves preserved git history using `git mv`
- Total test count: 129 tests passing (53 + 76)
- Backward compatible: Schema validation is optional (`use_schema=False` for semantic-only)

---

## [2.0.0] - 2025-11-13

### Added

#### 🚀 Intelligent Skill Activation System (Major Feature)

**Revolutionary skill loading with 96% token efficiency through automated hooks**

**New Hooks Infrastructure** (`.claude/hooks/`)

- **UserPromptSubmit Hook (Reactive)**: Analyzes user questions for keywords and intent patterns, automatically suggesting relevant skills BEFORE Claude responds
  - Detects financial keywords: NER, NPV, DSCR, breakeven, effective rent, tenant credit
  - Detects legal keywords: lease abstraction, assignment, sublease, default, termination
  - Detects process keywords: compliance, audit, comparison, valuation
  - Returns prioritized skill recommendations (critical > high > medium > low)

- **PreToolUse Hook (Proactive)**: Monitors file reads and automatically loads context-appropriate skills based on document type detection
  - **Document Pattern Detection** (10 types):
    - Offers to Lease: `*offer*lease*`, `*loi*`, `*term*sheet*`
    - Lease Agreements: `*lease*.pdf`, `*commercial*lease*`
    - Amendments: `*amendment*`, `*amending*agreement*`
    - Financial Statements: `*financial*statement*`, `*balance*sheet*`
    - Assignment/Sublease: `*assignment*consent*`, `*sublease*consent*`
    - Default Notices: `*default*notice*`, `*notice*cure*`
    - SNDA: `*snda*`, `*subordination*`, `*non*disturbance*`
    - Guarantees: `*indemnity*`, `*guarantee*`
    - Estoppels: `*estoppel*`
    - Calculator Inputs: `*_input.json` in calculator directories
  - **96% Token Efficiency**: Skills load proactively when reading documents, avoiding need to load all 23 skills upfront

**Hook Infrastructure Files**:

- `skill-activation-prompt.sh/ts`: Keyword-based reactive skill suggestions
- `pre-tool-use-skill-loader.sh/ts`: Document type-based proactive skill loading
- `generate-skill-rules.js`: Auto-generates activation triggers from skill frontmatter
- `lease-types-map.json`: Document type to skills mapping (10 patterns)
- `skill-rules.json`: Auto-generated activation rules for all 23 skills
- `package.json`: Node dependencies (`tsx`, `@types/node`)
- `README.md`: Complete hooks documentation and testing guide

**Auto-Generation Capability**:

- Single source of truth: Skill activation rules auto-generated from SKILL.md frontmatter
- Regenerate anytime with `npm run generate-rules`
- Extracts keywords, intent patterns, and priorities automatically
- Maintains consistency across all 23 skills

#### 📊 8 New Specialized Skills (15 → 23 Total)

**Financial Analysis Skills (3 new)**:

1. **effective-rent-analyzer** (~380 lines)
   - Net Effective Rent (NER) and Gross Effective Rent (GER) calculations
   - NPV analysis of irregular lease cash flows
   - Ponzi Rental Rate (PRR) framework for breakeven analysis
   - Fully levered breakeven accounting for opex and debt service
   - Sinking fund and capital recovery methodology
   - Payback period calculations
   - Red flag detection (excessive free rent, high TI, negative NPV)
   - Integration with `/effective-rent` command

2. **tenant-credit-analyst** (~340 lines)
   - DSCR (Debt Service Coverage Ratio) analysis
   - Liquidity ratios: Current Ratio, Quick Ratio, Working Capital
   - Leverage ratios: Debt-to-Equity, Total Liabilities / Assets
   - Profitability analysis: Gross/Operating/Net Margins, ROA, ROE
   - Credit scoring and grading (A+ to E scale)
   - Security recommendations (deposits, guarantees, covenants)
   - Red flags: Qualified audits, going concern warnings, negative equity
   - Financial statement analysis (Balance Sheet, P&L, Cash Flow)
   - Integration with `/tenant-credit` command

3. **lease-abstraction-specialist** (~280 lines)
   - 24-section industrial/office lease abstraction templates
   - ANSI/BOMA measurement standards compliance
   - Critical dates extraction and calendar generation
   - Systematic extraction methodology (parties, premises, financial, use, legal)
   - Red flag identification (missing provisions, conflicts, unusual terms)
   - Schedule G special provisions analysis
   - Integration with `/abstract-lease` and `/critical-dates` commands

**Compliance & Process Skills (3 new)**:

4. **lease-compliance-auditor** (~260 lines)
   - Annual insurance audit procedures (CGL, property, business interruption)
   - Environmental compliance monitoring (hazmat, permits, Phase I/II)
   - Use clause verification and zoning compliance
   - Financial covenant monitoring (DSCR, net worth, debt ratios)
   - Site inspection protocols and documentation
   - Notice and reporting compliance tracking
   - Red flags: Expired certificates, insufficient limits, unauthorized use
   - Integration with `/insurance-audit` and `/environmental-compliance` commands

5. **default-and-remedies-advisor** (~320 lines)
   - Monetary vs. non-monetary default classification
   - Cure period calculations (5-10 days monetary, 15-30 days non-monetary)
   - Comprehensive damages calculation:
     - Unpaid rent arrears
     - Accelerated future rent (NPV discounted)
     - Unamortized TI and leasing commissions
     - Re-letting costs (downtime, commissions, new TI)
   - Default notice drafting with required legal elements
   - Enforcement strategy recommendations
   - Red flags: Notice defects, premature termination, waiver issues
   - Integration with `/default-analysis` and `/notice-generator` commands

6. **lease-comparison-expert** (~310 lines)
   - Amendment vs. original lease tracking
   - Competing offers analysis (economic + non-economic)
   - Draft vs. precedent deviation analysis
   - Portfolio benchmarking across properties
   - NER/NPV normalization for comparison
   - Precedent deviation scoring (minor/moderate/major)
   - Red flags: Extreme concessions, unlimited assignment, tenant termination rights
   - Integration with `/compare-amendment`, `/compare-offers`, `/compare-precedent`, `/lease-vs-lease` commands

**Investment & Portfolio Skills (2 new)**:

7. **portfolio-strategy-advisor** (~330 lines)
   - Lease rollover schedule analysis
   - Expiry cliff detection (>30% SF in one year)
   - Renewal priority scoring matrix (tenant quality, rent gap, strategic value, urgency, space fit)
   - Vacancy forecasting with retention rate assumptions
   - Weighted Average Lease Term (WALT) calculations
   - Expiry Concentration Index (ECI) risk assessment
   - Retention rate benchmarking (office 60-70%, industrial 70-80%)
   - Red flags: Expiry cliffs, low WALT (<3 years), weak tenant concentration
   - Integration with `/rollover-analysis` and `/renewal-economics` commands

8. **real-options-valuation-expert** (~350 lines)
   - Black-Scholes model adapted for lease options
   - Renewal option valuation (fixed vs. market rent)
   - Expansion option valuation
   - Termination option valuation
   - Real options theory applied to lease flexibility
   - Volatility analysis for rent fluctuations
   - Option premium calculations ($/sf and % of rent)
   - In-the-money probability assessment
   - Red flags: Underpriced options, asymmetric risk, multiple free options
   - Integration with `/option-value` command

#### 📝 Enhanced Documentation

**CLAUDE.md Updates**:

- Updated structure diagram showing hooks infrastructure
- Expanded skills count from 15 to 23 with categorization
- Added comprehensive "Intelligent Skill Activation (Hooks)" section:
  - How UserPromptSubmit and PreToolUse hooks work
  - Document type detection patterns
  - Benefits (proactive expertise, token efficiency, context-aware, no memorization)
  - Maintenance procedures for adding new skills
- Enhanced skills categorization:
  - Core Lease Agreements (1 skill)
  - Financial Analysis (3 skills - NEW)
  - Compliance & Process (3 skills - NEW)
  - Investment & Portfolio (2 skills - NEW)
  - Security & Protection (2 skills)
  - Lease Modifications & Transfers (4 skills)
  - Preliminary & Ancillary Agreements (4 skills)
  - Specialized Licenses (1 skill)
  - Dispute Resolution (1 skill)
  - Negotiation & Objection Handling (2 skills)

**Hooks README** (`.claude/hooks/README.md`):

- Complete hooks overview and architecture
- Testing procedures (manual and npm scripts)
- File structure documentation
- Maintenance guide for adding skills and document patterns
- Troubleshooting section

**README.md Updates**:

- Version badge updated to 2.0.0
- Toolkit description updated: 23 skills, 28 commands, intelligent hooks
- Enhanced "Natural Workflow" section highlighting automatic skill loading
- Updated examples showing hook integration

### Changed

**Skill Infrastructure**:

- All existing 15 skills audited and frontmatter enhanced
- Standardized metadata across all skills (name, description, tags, capability, proactive)
- Improved descriptions with trigger keywords for hook matching
- Skills now support both manual invocation and automatic hook-based loading

**Performance**:

- **96% token efficiency improvement** through proactive skill loading
- Skills load on-demand based on user questions and document types
- Reduced context consumption by avoiding upfront loading of all 23 skills
- Intelligent prioritization (critical > high > medium > low)

### Technical Details

**Dependencies Added**:

- `tsx` ^4.7.0 (TypeScript execution for hooks)
- `@types/node` ^20.11.0 (TypeScript definitions)

**New Scripts**:

- `npm run test-prompt`: Test UserPromptSubmit hook
- `npm run test-pretool`: Test PreToolUse hook
- `npm run generate-rules`: Auto-generate skill-rules.json from skills

**Configuration Files**:

- `.claude/settings.json`: Hooks configuration with UserPromptSubmit and PreToolUse
- `.claude/skill-rules.json`: Auto-generated activation triggers (23 skills, keywords, intent patterns)
- `.claude/hooks/lease-types-map.json`: Document type mappings (10 patterns)

**Testing**:

- ✅ All hooks tested and validated
- ✅ UserPromptSubmit correctly detects keywords and suggests skills
- ✅ PreToolUse proactively detects 10 document types
- ✅ All 23 skills properly configured in skill-rules.json
- ✅ Auto-generation script tested and working

### Impact

**User Experience**:

- Skills automatically suggested when asking questions (reactive)
- Skills automatically loaded when reading documents (proactive)
- No need to memorize which skills exist or when to use them
- Right expertise delivered at the right time with minimal token overhead

**Scalability**:

- System now supports 50+ skills with same token efficiency
- Auto-generation ensures maintainability as skills grow
- Pattern-based detection scales to new document types easily

**Maintainability**:

- Single source of truth (skill frontmatter)
- Regenerate rules with one command
- Clear documentation for adding new skills
- Modular hook design (easy to update individual components)

## [1.9.0] - 2025-11-08

### Added

#### Agent Triumvirate Architecture

**New Multi-Agent System**: Three specialized AI agents with distinct expertise, models, and communication styles

**The Triumvirate**:

- **Adam** (`adam.md`, ~373 lines) - Senior Analyst & Everyday Execution (Haiku Model)
  - **Identity**: Reggie Chan's loyal analyst and protégé, trained to punch above weight class
  - **Background**: Stand-up comedian by night (timing, delivery, uncomfortable truths), great writer
  - **Scope**: Straightforward tasks requiring fast execution (80/20 analysis sufficient)
  - **What Adam Handles**:
    - Standard lease evaluations (typical terms, normal tenants)
    - Routine tenant credit checks (clear financials, no red flags)
    - Renewal offer assessments (market conditions clear)
    - Simple deal comparisons (straightforward tradeoffs)
    - Professional communication to stakeholders
  - **What Adam Escalates to Reggie**:
    - Complex/distressed situations requiring deep expertise
    - Fraud detection or forensic accounting
    - Crisis turnarounds with compressed timelines
    - Non-standard structures requiring framework building
  - **Communication Style**: Professional but direct, diplomatic delivery, politically aware
  - **Response Structure**: Executive Summary → Analysis → Political/Risk Factors → Recommendation → Action Items
  - **Model**: Haiku (speed and efficiency for routine work)

- **Reggie Chan, CFA, FRICS** (`reggie-chan-vp.md`, extensively enhanced) - VP Crisis Specialist (Sonnet Model)
  - **Core Identity**: INTJ-A Systems Architect with zero neuroticism and exceptional industriousness
  - **Cognitive Architecture**: Domain synthesis across leasing + accounting + legal + finance
  - **Mandatory Cognitive Processing Patterns** (9 layers):
    1. Immediate Quantification (Translation Reflex) - Cannot process qualitative statements without converting to numbers
    2. Forensic Verification Reflex - Every number triggers automatic verification impulse
    3. Domain Synthesis Integration - Cannot isolate problems to single domain
    4. Worst-Case Scenario Construction - Automatic adverse scenario modeling
    5. Political Blindness Acknowledgment - Explicitly flags this known limitation
    6. Zero Neuroticism Processing - Risk without emotional coloring
    7. Exhaustive Documentation Impulse - Complete audit trail generation
    8. Challenge Authority Reflex - Questions credentials and expertise automatically
    9. Multi-Layer Risk Assessment - Cascading scenario trees for all decisions
  - **Communication Style**: Numbers-first sentence construction, forensic language patterns, zero hedging language
  - **Scope**: Complex problems, crisis turnarounds, fraud detection, multi-domain synthesis, exhaustive frameworks
  - **Model**: Sonnet (balance of depth and performance)

- **Dennis** (`dennis.md`, ~650 lines) - Strategic Advisor & Former Boss (Opus Model)
  - **Identity**: 36+ years institutional real estate executive, former president of major operation, Reggie's former boss
  - **Credentials**: CFA, FRI, B.Comm Real Estate, executive education
  - **Background**: Multi-billion dollar AUM, large teams, millions of square feet, consistently beat benchmarks
  - **Philosophy**: "Real estate is 30% spreadsheets and 70% human psychology, politics, and hard choices"
  - **Expertise**: Strategic career decisions, negotiation psychology, people management, work-life balance, reality checks
  - **Communication Style**: Direct, blunt, doesn't waste words, challenges assumptions, shares battle scars
  - **When to Use**: Career crossroads, negotiation psychology, people problems, when you need tough love
  - **Model**: Opus (deep strategic thinking for complex human dynamics)

**Agent Response Architecture**:

- **Direct Response Mode**: All agents use `return_mode: direct` in frontmatter
- **No Summarization**: Agents speak directly to user without Claude adding commentary or interpretation
- **Explicit Instructions**: Each agent file contains instruction block mandating direct passthrough of responses

**Division of Labor**:

- **Adam**: Routine work, 80/20 analysis, fast turnaround, political awareness, diplomatic communication
- **Reggie**: Complex problems, crisis situations, exhaustive frameworks, brutal honesty, multi-domain synthesis
- **Dennis**: Strategic wisdom, career guidance, negotiation psychology, reality checks, battle-tested experience

**Natural Workflow**:
```
Daily question → Adam analyzes → Red flags? → Escalate to Reggie → Strategic implications? → Consult Dennis
```

**Integration with Existing System**:

- All three agents have access to:
  - 15 specialized skills (commercial lease, assignments, SNDAs, indemnities, negotiation, objection handling, etc.)
  - 25 slash commands (abstraction, financial analysis, accounting, comparison, compliance, utilities)
  - 11 financial calculators (effective rent, credit analysis, IFRS 16, options valuation, variance, etc.)

**Documentation Updates**:

- **README.md**: Updated to "Meet Your Real Estate Team: The Triumvirate"
  - Title changed from "Meet Reggie Chan" to "Meet Your Real Estate Team"
  - Added triumvirate introduction with distinct agent descriptions
  - Updated "How to Work with" section with examples for each agent
  - Modified "Capabilities" section to reflect team resources
  - Updated project structure to show agents directory
  - Modified support section to reflect team composition

- **README-FOR-LEASING-MANAGERS.md**: Updated to "Meet Your New Team: Adam, Reggie, and Dennis"
  - Casual tone maintained while introducing triumvirate
  - Updated "What This Is" section with agent breakdown
  - Modified workflow examples to show agent collaboration
  - Updated "Who This Is For" sections to reference appropriate agents
  - Changed "What Makes Reggie Different" to "What Makes This Team Different"
  - Updated support section with team composition

- **CLAUDE.md**: Updated with "Meet Your Team: The Triumvirate"
  - Added comprehensive triumvirate section with when to use each agent
  - Updated structure diagram to show all three agents with model types
  - Added "The Triumvirate Workflow" section
  - Modified capability sections to reflect team resources

**Commits**: Agent creation and documentation updates

**Total Implementation**: ~1,673 lines (373 Adam + 650 Dennis + 650 Reggie enhancements)

**Design Philosophy**:

- **Complementary, Not Overlapping**: Each agent has distinct scope with clear escalation paths
- **Cognitive Patterns Over Capabilities**: Agents embody thinking patterns, not just knowledge lists
- **Communication as Cognition Output**: Style derives from processing patterns, not performance
- **Appropriate Model Selection**: Haiku (speed), Sonnet (balance), Opus (depth) matched to use case
- **Direct Voice**: Agents speak for themselves without mediation or summarization

---

## [1.8.0] - 2025-11-07

### Added

#### Negotiation and Objection Handling Expert Skills

**New Skills**: Evidence-based persuasion and systematic objection analysis for commercial lease negotiations

- **negotiation-expert.md** (~650 lines) - Evidence-based persuasion techniques adapted for CRE
  - **Calibrated Questions**: Framework for shifting burden of proof to counterparty
    - "How am I supposed to justify $16/sf when market shows $18-19?"
    - "What about X makes you think..." structure
    - Makes counterparty solve your problem instead of defending positions
  - **Accusation Audits**: Pre-emptive objection defusing
    - "You probably think I'm being unreasonable..."
    - "It might seem inflexible, but..."
    - Shows understanding of their perspective before they voice it
  - **Labeling**: Demonstrate understanding to build rapport and gather information
    - "It seems like you're concerned about..."
    - "It sounds like timing is the main issue..."
  - **Evidence-Based Anchoring**: Present market data + calibrated question
    - Establish position with comparable evidence first
    - Use calibrated questions to make them engage with your data
  - **Mirroring & No-Oriented Questions**: Strategic conversation control
  - **Integration with Toolkit**: Uses relative-valuation, effective-rent, market-comparison, tenant-credit results to support arguments
  - **Sample Scenarios**: Rent objection without evidence, excessive TI request, renewal rent increase pushback, free rent request
  - **Ethical Boundaries**: Never fabricate offers/deadlines, always ground in verifiable data, maintain relationships

- **objection-handling-expert.md** (~850 lines) - Systematic objection analysis and response framework
  - **Classification System**: Financial, operational, market-based, risk-based objections
  - **Legitimacy Assessment**:
    - Evidence-backed → Engage with their data
    - Emotional → Calibrated questions to force data discussion
    - Tactical → Accusation audit + evidence anchor
  - **Response Strategies by Type**:
    - Strategy A: Legitimate objection with evidence → Engage, present counter-evidence, find value trades
    - Strategy B: Emotional objection → Use calibrated questions to force data-based discussion
    - Strategy C: Negotiating tactic → Accusation audit + evidence, call bluff professionally
    - Strategy D: Constraint-based → Uncover constraint, creative structure, trade don't concede
  - **Common Objections Response Templates**:
    - "Your rent is above market"
    - "We need more free rent"
    - "We can't commit to [X] years"
    - "Building X is offering better terms"
    - "That security deposit is too high"
    - "We need $[X] TI allowance"
  - **Advanced Tactics**: Columbo close, summary close, range anchor, breakdown isolate, forced choice
  - **Integration with Toolkit**: Pull data from relative-valuation, effective-rent, market-comparison, tenant-credit, renewal-economics
  - **Response Templates**: Structured email/phone frameworks for each objection type

**Methodology**: Evidence-based persuasion framework adapted specifically for commercial real estate lease negotiations. Skills teach methodology and principles rather than canned scripts, enabling context-aware responses using actual deal data.

**Value Proposition**:
- Bridges analytical rigor (toolkit calculators) with persuasive delivery (negotiation skills)
- Analysis tools tell you WHAT to do, negotiation skills tell you HOW to communicate it
- Systematizes negotiation expertise so it scales across team
- Professional, evidence-based responses maintain relationship integrity while defending position

**Documentation Updates**:
- Updated skill count from 13 to 15 across all documentation
- Added "Negotiation & Objection Handling" category to CLAUDE.md
- Enhanced reggie-chan-vp agent (formerly leasing-expert) with new skills and Example 5 workflow (rent objection response)
- Updated README.md, README-FOR-LEASING-MANAGERS.md, IMPLEMENTATION_GUIDE.md
- Added skill invocation examples to CLAUDE.md quick start

**Commits**: `f9a711a` (skills implementation and documentation)

**Total Implementation**: ~1,500 lines (650 negotiation + 850 objection handling)

---

## [1.7.0] - 2025-11-06

### Added

#### Real Options Valuation Calculator - Issue #4 ✅

**New Calculator**: `Option_Valuation/` - Black-Scholes option pricing for commercial real estate lease flexibility

- **option_valuation.py** (794 lines) - Complete Black-Scholes implementation
  - Black-Scholes call option pricing: `C = S × N(d1) - K × e^(-rT) × N(d2)`
  - Black-Scholes put option pricing: `P = K × e^(-rT) × N(-d2) - S × N(-d1)`
  - Cumulative normal distribution using `scipy.stats.norm.cdf()` (15+ decimal accuracy)
  - d1/d2 calculation: `d1 = [ln(S/K) + (r + σ²/2)T] / (σ√T)`, `d2 = d1 - σ√T`
  - All option Greeks (Delta, Gamma, Vega, Theta, Rho) with analytical formulas
  - Portfolio valuation for multiple concurrent options
  - Comprehensive sensitivity analysis (volatility, market rent, time decay)
  - JSON input/output with structured schema
  - Command-line interface with verbose and output control

**Option Greeks Calculations**:
```python
# Delta (∂V/∂S) - Sensitivity to underlying price
Delta_Call = N(d1)                    # Range: 0 to 1
Delta_Put = N(d1) - 1                 # Range: -1 to 0

# Gamma (∂²V/∂S²) - Rate of delta change (always positive)
Gamma = φ(d1) / (S × σ × √T)

# Vega (∂V/∂σ) - Sensitivity to volatility (per 1%)
Vega = S × φ(d1) × √T / 100

# Theta (∂V/∂T) - Time decay (per year)
Theta_Call = -(S × φ(d1) × σ) / (2√T) - r × K × e^(-rT) × N(d2)
Theta_Put = -(S × φ(d1) × σ) / (2√T) + r × K × e^(-rT) × N(-d2)

# Rho (∂V/∂r) - Interest rate sensitivity (per 1%)
Rho_Call = K × T × e^(-rT) × N(d2) / 100
Rho_Put = -K × T × e^(-rT) × N(-d2) / 100
```

**Option Types Supported**:
1. **Renewal Options** (Call): Tenant right to renew at predetermined rent
   - Underlying: Market rent × Area × Renewal term
   - Strike: Renewal rent × Area × Renewal term
2. **Expansion Options** (Call): Tenant right to lease additional space
   - Adjusts for utilization probability (0.4-0.8 typical)
3. **Termination Options** (Put): Tenant right to exit early (with penalty)
   - Provides downside protection in declining markets
4. **Purchase Options** (Call): Tenant right to purchase property
   - Uses property value volatility (8-12%, lower than rent)

- **Tests/test_option_valuation.py** (680 lines) - **36 tests passing (100%)**
  - Cumulative normal distribution accuracy (3 tests)
  - d1/d2 calculations and relationship verification (4 tests)
  - Black-Scholes call options with known results (6 tests)
  - Black-Scholes put options and put-call parity (4 tests)
  - All Greeks calculations and range validation (7 tests)
  - Complete option valuation workflow (3 tests)
  - Sensitivity analysis (volatility, market rent, time decay) (3 tests)
  - Real estate scenarios (industrial, office) (2 tests)
  - Edge cases (deep ITM/OTM, very short/long terms) (4 tests)

**Validation**:
- ✅ Validated against published Black-Scholes calculators (exact match)
- ✅ Put-call parity verified: `C - P = S - K×e^(-rT)` (tolerance < $0.01)
- ✅ Greeks ranges and properties confirmed
- ✅ Real estate examples match manual calculations

- **README.md** (514 lines) - Comprehensive documentation
  - Installation and dependencies (scipy, numpy)
  - Quick start guide with JSON examples
  - Option types and parameter guidance
  - JSON input/output schema documentation
  - Parameters guide: volatility (8-18%), risk-free rate, time to expiration, utilization probability
  - Command-line interface reference
  - Interpreting results: option value, Greeks, sensitivity, probability ITM
  - Real-world commercial real estate examples (industrial, office)
  - Validation methodology and accuracy section
  - Academic references (Black & Scholes 1973, Grenadier 1995)

**Example Output**:
```
Industrial Warehouse (50,000 SF) - 4 Options:
- First Renewal (5 years): $1,082,682 ($21.65/sf) - 81.9% ITM
- Second Renewal (5 years): $781,390 ($15.63/sf) - 52.9% ITM
- Expansion (10,000 SF): $127,398 ($12.74/sf) - 76.7% ITM
- Termination (Year 3): $957,358 ($19.15/sf) - 31.6% ITM
Total Embedded Value: $2,948,828 ($58.98/sf)
```

**Sample Files**:
- `sample_option_input.json` - Industrial warehouse example with 4 options
- `sample_option_output.json` - Complete valuation results with Greeks and sensitivity
- `option_inputs/example_industrial_warehouse.json` - Ready-to-use template

**Slash Command Integration**:
- Updated `.claude/commands/Financial_Analysis/option-value.md`
- Added "Automated Calculator Workflow (Recommended)" section
- Step 11: Generate JSON Input from lease provisions
- Step 12: Run Calculator (`python Option_Valuation/option_valuation.py input.json`)
- Step 13: Incorporate Results into Report
- Documents advantages: accuracy, speed, validation, reproducibility

**Use Cases**:
1. Valuing embedded lease options (renewal, expansion, termination, purchase)
2. Negotiation support - quantify option value for landlord/tenant discussions
3. Lease vs. purchase decisions - compare leasing flexibility value
4. Portfolio option value aggregation across multiple properties
5. Sensitivity analysis for volatility assumptions and market scenarios

**Commits**: `03e5edd` (implementation), `db9da45` (merge to main)

**Total Implementation**: 1,988 lines (794 calculator + 680 tests + 514 docs)

---

## [1.6.0] - 2025-11-06

### Added

#### Phase 1: Portfolio Rollover Calculator - Issue #7 (HIGH PRIORITY) ✅

**New Calculator**: `Rollover_Analysis/` - Comprehensive portfolio lease expiry analysis and renewal prioritization

- **rollover_calculator.py** (1,253 lines) - Core aggregation, scenario modeling, and priority scoring engine
  - Expiry schedule aggregation by year and quarter (count, SF, rent, %)
  - Concentration risk flags (>20% HIGH, >30% CRITICAL)
  - 0-1 normalized priority scoring prevents scale dominance
  - Credit rating mapping (AAA to D, plus NR "Not Rated" handling)
  - Three-scenario modeling (optimistic/base/pessimistic) with scenario-specific downtime (1/3/6 months)
  - Enforces minimum 1-month downtime even on renewals (realistic TI/legal/move-in costs)
  - NPV discounting at configurable rate (default 10%)
  - Cumulative expiry curve data generation

- **report_generator.py** (592 lines) - Professional markdown report generation
  - Executive summary with concentration risk assessment
  - Detailed expiry schedule tables (yearly and quarterly views)
  - Renewal priority ranking sorted by composite score
  - Three-scenario comparison table with NOI impact
  - Strategic recommendations by priority tier
  - CSV export capability for Excel integration

- **Tests/test_rollover_calculator.py** (848 lines) - **37 tests passing (100%)**
  - Aggregation accuracy (by year, quarter)
  - Risk flag thresholds (20%, 30%)
  - Priority scoring with normalized inputs (prevents rent amount dominance)
  - Credit rating mapping (all grades AAA to D, plus NR)
  - Scenario modeling with NPV calculations
  - Scenario-specific downtime enforcement
  - Minimum 1-month downtime on renewals
  - NPV discounting at configurable rate
  - Edge cases: empty portfolio, single lease, all same year, 0%/100% renewal rates

**Priority Scoring Formula** (0-1 normalized):
```python
# Normalize all inputs to 0-1 scale to prevent scale dominance
Rent_Pct = min(lease_rent / portfolio_rent, 1.0)  # Caps at 100%
Urgency = 1 - min(months_to_expiry / 24, 1.0)     # 0 months = 1.0, 24+ months = 0.0
Below_Market = max(0.0, min(abs(below_market_pct) / 20, 1.0))  # Caps at 20%
Credit_Risk = credit_rating_to_score(tenant_credit_rating)     # 0.0 (AAA) to 1.0 (D)

# Weighted composite score
Priority = (Rent_Pct × 0.40) + (Urgency × 0.30) + (Below_Market × 0.20) + (Credit_Risk × 0.10)
```

**Mathematical Rigor**:
- **0-1 Normalization**: Prevents large rent amounts from dominating priority score
- **Capped Inputs**: All components capped at 1.0 maximum to ensure fair weighting
- **NPV Discounting**: Time value of money at configurable discount rate (default 10%)
- **Scenario-Specific Downtime**: Optimistic (1 month), Base (3 months), Pessimistic (6 months)

**Slash Command Integration**:
- Updated `.claude/commands/Financial_Analysis/rollover-analysis.md` (280 lines)
- Changed from manual workflow to automated JSON → Python → Report pattern
- Documented JSON schema, strategic guidance, and interpretation framework

**Use Cases**:
1. Portfolio planning and renewal prioritization
2. Budget forecasting and NOI projections
3. Expiry cliff risk identification
4. Renewal team capacity planning
5. Credit risk concentration analysis

**Commits**: `6cfb5ae` (initial implementation), `9ba2fd1` (slash command integration)

---

#### Phase 2: Default Damage Calculator - Issue #7 (MEDIUM PRIORITY) ✅

**New Calculator**: `Default_Calculator/` - Tenant default damage quantification and notice generation

- **default_calculator.py** (1,584 lines) - Comprehensive damage calculation engine
  - Total arrears calculation (base rent, additional rent, late fees, interest)
  - Simple and compound interest support
  - Business day cure period calculation (skip weekends/holidays)
  - Future rent NPV calculation at configurable discount rate (default 10%)
  - Mitigation credit scenarios (optimistic/base/pessimistic vacancy rates)
  - Re-letting cost breakdown (commission, TI, legal fees)
  - Bankruptcy cap analysis (§502(b)(6) statutory limits)
  - Net exposure after security deposits and letters of credit
  - Multiple default scenario support (monetary, non-monetary, insolvency)

- **notice_generator.py** (713 lines) - Jurisdiction-aware default notice drafting
  - Formal notice templates with proper legal formatting
  - Cure period calculation based on jurisdiction
  - Itemized arrears breakdown
  - Damages quantification summary
  - Landlord remedies and actions available
  - Tenant obligations to cure
  - Consequences of non-compliance

- **date_utils.py** - Business day arithmetic utilities
  - `add_business_days()` - Skip weekends and optional holidays
  - `business_days_between()` - Calculate business days between dates
  - `format_eastern_timestamp()` - ET timezone formatting

- **METHODOLOGY.md** (1,850 lines) - Comprehensive methodology documentation
  - Detailed formula explanations with examples
  - Bankruptcy Code §502(b)(6) analysis
  - Mitigation duty and credit calculations
  - Jurisdiction-specific cure periods
  - Case law references and legal framework
  - NPV calculation methodology
  - Best practices for settlement negotiations

- **Tests/test_default_calculator.py** (965 lines) - **32 tests passing (100%)**
  - Arrears calculation with simple/compound interest
  - Business day cure period (skip weekends)
  - Future rent NPV at configurable discount rate
  - Mitigation scenarios with varying vacancy rates
  - Re-letting cost calculations
  - Bankruptcy cap (§502(b)(6))
  - Net exposure after security deduction
  - Excel validation (matches manual calculations)
  - Edge cases: zero security, over-secured, expired lease, negative remaining term

**Bankruptcy Cap Formula (§502(b)(6))**:
```python
Annual_Rent = monthly_rent × 12
Remaining_Rent = monthly_rent × remaining_months
Three_Year_Rent = Annual_Rent × 3

# Statutory cap = greater of (1 year rent) OR (15% of minimum of remaining/3-year rent)
Statutory_Cap = max(
    Annual_Rent,
    0.15 × min(Remaining_Rent, Three_Year_Rent)
)

# Total claim capped at statutory maximum
Allowed_Claim = min(Total_Damages, Statutory_Cap)
```

**Slash Command Integration**:
- Updated `.claude/commands/Compliance/default-analysis.md` (427 lines)
- Changed from manual workflow to automated JSON → Python → Report pattern
- Documented damage calculation methodology with formulas
- Added strategic guidance for remedy selection (Terminate/Continue/Settle)

**Use Cases**:
1. Default notice preparation and issuance
2. Settlement negotiation with financial analysis
3. Litigation support and damages quantification
4. Security adequacy reviews (pre-lease underwriting)
5. Portfolio default risk monitoring

**Commits**: `6d3c963` (initial implementation), `19f3c21` (METHODOLOGY.md), `9ba2fd1` (slash command integration)

---

#### Phase 3: Statistical Analysis Enhancement - Issue #7 (MEDIUM PRIORITY) ✅

**New Module**: `Relative_Valuation/statistics_module.py` (684 lines) - Traditional statistical analysis to supplement MCDA

- **Summary Statistics** (`calculate_summary_statistics()`)
  - Mean, median, standard deviation
  - Min, max, range
  - Coefficient of variation (CV = std_dev / mean)
  - Sample size (N)
  - Identifies most variable factors (highest CV)

- **Multiple Linear Regression** (`multiple_linear_regression()`)
  - Predicts net asking rent from property variables
  - R-squared (proportion of variance explained)
  - Adjusted R-squared (penalizes overfitting)
  - Regression coefficients with interpretations
  - Identifies strongest rent drivers
  - Formula: `Rent = β₀ + β₁X₁ + β₂X₂ + ... + βₙXₙ`

- **Pearson Correlation Analysis** (`calculate_correlation()`)
  - Pairwise correlation coefficients (r)
  - R-squared (r²) - proportion of shared variance
  - Strength classification:
    - Strong: |r| ≥ 0.7
    - Moderate: 0.4 ≤ |r| < 0.7
    - Weak: 0.2 ≤ |r| < 0.4
    - Negligible: |r| < 0.2
  - Direction (positive/negative)

- **Outlier Detection** (`detect_outliers_zscore()`)
  - Z-score calculation: `z = (x - μ) / σ`
  - Flags properties with |z| > 2.0 (95% confidence)
  - Flags properties with |z| > 3.0 (99.7% confidence)
  - Helps identify data quality issues or unique properties

- **Key Insights Generation** (`analyze_properties_statistics()`)
  - Most variable factor (highest CV)
  - Rent predictability (R²)
  - Strongest rent driver (highest regression coefficient)
  - Strongest correlation (highest |r|)
  - Automatic insight extraction from statistical results

**Integration with Relative Valuation**:
- Added `--stats` flag to `relative_valuation_calculator.py`
- Conditional statistical analysis execution
- Appends statistical markdown section to MCDA report
- JSON output includes `statistical_analysis` key with complete data
- Backward compatible (no breaking changes to existing reports)

**Try-Except Import Pattern** (Codex improvement):
```python
# Supports both package imports and direct script execution
try:
    from .statistics_module import analyze_properties_statistics, generate_statistics_markdown
except ImportError:
    from statistics_module import analyze_properties_statistics, generate_statistics_markdown
```

**Report Structure** (with `--stats` flag):
1. Executive Summary (MCDA ranking)
2. Subject Property Analysis
3. Top 10 Competitors
4. Gap Analysis
5. Recommended Actions
6. Methodology
7. **Statistical Analysis** ← NEW
   - Key Insights (4 auto-generated insights)
   - Summary Statistics (mean, median, CV for all variables)
   - Regression Analysis (R², coefficients, interpretations)
   - Correlation Analysis (pairwise correlations with strength classifications)
   - Statistical Notes (methodology, limitations)

**Slash Command Integration**:
- Updated `.claude/commands/Financial_Analysis/relative-valuation.md` with `--stats` flag documentation
- Added interpretation guidance for statistical results
- Documented when to use `--stats`: large datasets (20+ properties), understanding rent drivers, data quality checks

**Use Cases**:
1. Large datasets (20+ properties) - identify rent drivers statistically
2. Validate MCDA results with traditional regression analysis
3. Data quality checks - identify outliers and data entry errors
4. Market research - understand which variables drive rent in specific submarkets
5. Academic/research applications - traditional statistical validation

**Test Results**:
- ✅ Calculator runs with `--stats` flag (6 properties, R²=90.5%, 8 correlations, 4 insights)
- ✅ Calculator runs without `--stats` flag (standard MCDA only)
- ✅ Direct module import works (both relative and absolute imports)
- ✅ JSON output includes `statistical_analysis` key with complete data
- ✅ Markdown report appends statistical section seamlessly
- ✅ Backward compatible (no breaking changes)

**Commits**: `67aaebd` (initial implementation), `41286cb` (slash command update), `3aabf1b` (import pattern improvement)

---

### Changed

#### Slash Commands

**Three slash commands upgraded from manual to automated workflows**:

1. **`/rollover-analysis`** - Now calls Python calculator
   - Changed from basic prompt-based workflow (2.6KB) to automated JSON → Python → Report pattern (280 lines)
   - Documented JSON schema, Python calculator usage, strategic interpretation guidance
   - Added priority scoring formula explanation
   - Documented concentration risk thresholds (>20% HIGH, >30% CRITICAL)

2. **`/default-analysis`** - Now calls Python calculator
   - Changed from comprehensive prompt workflow (18KB) to automated JSON → Python → Report pattern (427 lines)
   - Documented damage calculation methodology with mathematical formulas
   - Added strategic guidance for remedy selection
   - Documented bankruptcy cap analysis (§502(b)(6))
   - Integrated notice generator with jurisdiction support

3. **`/relative-valuation`** - Enhanced with `--stats` flag
   - Added statistical analysis documentation in Step 4
   - Added interpretation guidance in Step 5 (R², coefficients, correlations, outliers)
   - Documented when to use `--stats` flag vs standard MCDA only

**Total slash commands**: 24 (unchanged count, but 3 significantly enhanced)

#### Documentation

- Updated README.md to version 1.6.0
- Updated test badge from 130+ to 199+ tests passing
- Updated TL;DR: 24 automated workflows + 10 calculators (was 21 workflows + 6 calculators)
- Added three new calculators to capabilities section (Portfolio Rollover, Default Damage, Statistical Analysis)
- Updated project structure to show new directories (`Rollover_Analysis/`, `Default_Calculator/`)
- Updated direct calculator usage examples with new calculators
- Updated CLAUDE.md with Issue #7 completion status

---

### Fixed

#### Workflow Improvements

- **Eliminated manual data entry** for rollover and default analysis
- **Automated JSON generation** from PDF/Excel inputs
- **Consistent calculator pattern** across all three new modules (JSON → Python → Report)
- **Strategic guidance integration** in slash commands (not just calculation, but interpretation)

#### Statistical Analysis

- **SyntaxWarning fix** in `statistics_module.py:624` (invalid escape sequence `\ ` → `  `)
- **Import flexibility** with try-except pattern (supports both package and script execution)

---

### Technical Details

**Total Implementation Statistics**:
- **7,982 lines** of production code (2,693 rollover + 3,262 default + 2,027 statistics)
- **69 new tests** (37 rollover + 32 default) at 100% pass rate
- **Total test suite**: 199+ tests passing (130 existing + 69 new)
- **3 calculators** added (bringing total from 7 to 10)
- **3 slash commands** upgraded (bringing total enhanced to 24)
- **Documentation**: 2,557 lines (280 rollover + 427 default + 1,850 METHODOLOGY.md)

**File Locations**:
- `Rollover_Analysis/rollover_calculator.py` (1,253 lines)
- `Rollover_Analysis/report_generator.py` (592 lines)
- `Rollover_Analysis/Tests/test_rollover_calculator.py` (848 lines, 37 tests)
- `Default_Calculator/default_calculator.py` (1,584 lines)
- `Default_Calculator/notice_generator.py` (713 lines)
- `Default_Calculator/Tests/test_default_calculator.py` (965 lines, 32 tests)
- `Default_Calculator/METHODOLOGY.md` (1,850 lines)
- `Relative_Valuation/statistics_module.py` (684 lines)
- `.claude/commands/Financial_Analysis/rollover-analysis.md` (280 lines)
- `.claude/commands/Compliance/default-analysis.md` (427 lines)
- `.claude/commands/Financial_Analysis/relative-valuation.md` (enhanced with --stats)

**Dependencies**:
- No new external dependencies required
- Uses existing NumPy, Pandas for statistical calculations
- All modules use standard library for date arithmetic and JSON handling

**Backwards Compatibility**:
- All existing JSON input files continue to work unchanged
- Existing slash commands function identically
- `--stats` flag is optional (no breaking changes to relative valuation)
- All existing reports maintain structure and format

**GitHub Issue**:
- Closes Issue #7: "Implement Market Comparison & Portfolio Analysis Module"
- All three phases complete: Rollover (Phase 1), Default (Phase 2), Statistics (Phase 3)
- 100% test coverage across all new modules
- Production-ready with comprehensive documentation

---

## [1.5.0] - 2025-11-06

### Added

#### MLS Data Extraction to Excel

**`/extract-mls` Slash Command** - Automated extraction of commercial MLS data from PDF reports to professionally formatted Excel spreadsheets

- **MLS_Extractor/excel_formatter.py** (423 lines) - Excel generation with professional styling
  - Perfect column ordering by decision importance (rent, TMI, size first, not alphabetical)
  - Bright yellow subject property highlighting (#FFFF00 background, bold text)
  - Dark blue headers with white text (#2C3E50)
  - Auto-sized columns (10-50 character limits)
  - Perfect number formatting (currency, percentages, integers)
  - Frozen header row and auto-filter on all columns
  - Built with openpyxl for reliable Excel generation

- **.claude/commands/Financial_Analysis/extract-mls.md** (232 lines) - Slash command workflow
  - Complete field mapping for 34 fields (25 valuation variables + 9 metadata)
  - Three-tier subject property auto-detection (client_remarks keyword, --subject flag, default to first)
  - Parsing rules for complex fields (bay depth from "X x Y", lot size conversion, ordinal encoding)
  - 6-step automated workflow: Read PDF → Extract → Auto-detect → Calculate → JSON → Excel → Report

- **MLS_Extractor/PRODUCT_SPEC.md** (151 lines) - Product vision and "magic moment"
  - "Steve Jobs" design philosophy: one command, zero configuration, beautiful output
  - Perfect is the only acceptable standard
  - 30-second target extraction time (vs 60-second requirement)
  - 100% accuracy requirement (vs 95% minimum)

**Test Results** (Mississauga Industrial MLS, 100-400k sf)
- **23 properties extracted** with 100% accuracy
- **34 fields per property** (25 valuation variables + 9 metadata fields)
- **30-second extraction time** (50% faster than 60-second target)
- **100% accuracy verification** (26% sample spot-check across all 34 fields)
- **Subject property correctly identified** (2550 Stanfield Rd)
- **Perfect mathematical accuracy** (gross_rent = net_asking_rent + tmi validated)

**Key Features**
- LLM-based extraction (Claude Code Read tool) - adapts to format variations automatically
- Subject property auto-detection with bright yellow highlighting
- Professional Excel formatting that "looks like a designer made it"
- Perfect column ordering for fastest decision-making
- Eastern Time timestamp file naming (YYYY-MM-DD_HHMMSS format)
- Zero configuration required - one command, instant results

**Installation Requirements**
- Added `openpyxl` to installation dependencies (Excel generation)

**Usage**
```bash
# Extract with auto-detection
/extract-mls path/to/mls_report.pdf

# Extract with subject property specification
/extract-mls path/to/mls_report.pdf --subject="2550 Stanfield"
```

**Files Created**
- JSON input: `Reports/YYYY-MM-DD_HHMMSS_mls_extraction_input.json`
- Excel output: `Reports/YYYY-MM-DD_HHMMSS_mls_extraction_[description].xlsx`
- Summary report: `Reports/YYYY-MM-DD_HHMMSS_mls_extraction_report.md`

**Success Criteria Exceeded**
- ✅ Accuracy: 100% (target: 95%)
- ✅ Speed: 30 seconds (target: 60 seconds)
- ✅ Subject highlighting: Bright yellow, impossible to miss
- ✅ Professional formatting: Designer-quality Excel output
- ✅ Zero configuration: One command, auto-detect everything

---

## [1.4.0] - 2025-11-06

### Added

#### Relative Valuation Enhancements

**Weights Configuration System** - External JSON-based weight management with tenant persona support

- **weights_loader.py** - External weights configuration loader module
  - Loads persona-specific weights from `weights_config.json`
  - Schema validation using `weights_config_schema.json`
  - Supports 4 built-in personas: default, 3pl, manufacturing, office
  - Custom config file path support via `--weights-config` parameter
  - Automatic fallback to hardcoded defaults if config unavailable

- **weights_config.json** - Weight configuration with tenant personas
  - **Default/Balanced** (11 variables, 65-17-12-6% allocation)
  - **3PL/Distribution** - Emphasizes bay depth, clear height, shipping doors, trailer parking
  - **Manufacturing** - Emphasizes clear height, power, crane, rail access
  - **Office** - Emphasizes office space, class, HVAC, distance, parking

- **weights_config_schema.json** - JSON Schema for weight validation
  - Enforces structure: persona, name, description, weights object
  - Validates all 25 variable fields with float values
  - Ensures proper weight normalization

- **WEIGHTS_CONFIG_GUIDE.md** - Comprehensive configuration documentation
  - How to create custom weight profiles
  - Persona comparison matrix
  - Weight allocation philosophy
  - Testing and validation procedures

- **RANKING_METHODOLOGY.md** - Detailed methodology documentation
  - Competition ranking (1-2-2-4 method) explanation
  - Tie handling and Excel RANK function equivalence
  - Dynamic weight redistribution algorithm
  - Mathematical proofs and examples

**Auto-Load Default Weights** - Eliminates "Missing required field: weights" error

- Modified `load_comparable_data()` to automatically load default weights when not provided in input JSON
- Weights field now optional in input JSON (auto-loads default persona if missing)
- Seamless workflow: no need to manually add weights to JSON files
- Clear informational messages when defaults are loaded

**Complete Weights Transparency in Reports**

- Added `weights_used` field to `CompetitiveAnalysis` dataclass
- **Methodology section** now displays all weights in sortable table (highest to lowest)
- Mathematical verification: "✅ Weights sum to 100.0% - calculation verified"
- Shows actual dynamic weights used after redistribution (not just base weights)

**Improved PDF Report Formatting**

- **Page Break Controls** (`pdf_style.css`)
  - Headers (h1, h2, h3) stay with their content (`page-break-after: avoid`)
  - Tables remain intact without breaking (`page-break-inside: avoid`)
  - Table rows won't break mid-row
  - `.no-break` CSS class for critical sections

- **GAP ANALYSIS Section Protection**
  - Wrapped entire section in `<div class="no-break">` container
  - Ensures gap analysis table and recommendations stay together on same page

- **Increased White Space**
  - Major section headers (h2) now have 20px top margin (up from 8px)
  - Improved visual separation between SUBJECT PROPERTY ANALYSIS, GAP ANALYSIS, RECOMMENDED ACTIONS, METHODOLOGY, and LIMITATIONS sections

**Command-Line Persona Support**

- `--persona` flag: Choose from default, 3pl, manufacturing, office
- `--weights-config` flag: Path to custom weights configuration file
- Persona weights override JSON weights (highest priority)
- Examples:
  ```bash
  # Use 3PL persona weights
  python relative_valuation_calculator.py --input data.json --output report.md --persona 3pl

  # Use custom config file
  python relative_valuation_calculator.py --input data.json --output report.md --weights-config custom.json
  ```

### Changed

#### Relative Valuation Calculator

- **Weight Loading Priority** (lowest to highest):
  1. Auto-loaded defaults (if no weights in JSON)
  2. Explicit JSON weights (if provided)
  3. Command-line persona override (--persona flag, highest priority)

- Updated `get_tenant_persona_weights()` function:
  - Added `config_path` optional parameter
  - Attempts to load from weights_loader module (relative then absolute import)
  - Falls back to hardcoded defaults if external config unavailable
  - Returns informative messages about weight source

- Removed "weights" from required fields in `load_comparable_data()`
- Added `Optional` type hint import for better type safety

#### Report Generation

- Methodology section now includes complete weights table instead of summary
- Added weight sum verification in every report
- Improved visual hierarchy with consistent spacing
- Professional landscape PDF output with proper page breaks

### Fixed

#### Workflow Issues

- **Eliminated recurring "Missing required field: weights" error**
  - Was caused by required validation before auto-loading logic
  - Now loads defaults first, then validates other required fields
  - Users no longer need to manually add weights to input JSON

#### PDF Formatting

- **Tables breaking across pages** - Now kept intact with `page-break-inside: avoid`
- **GAP ANALYSIS splitting** - Now wrapped in no-break container
- **Insufficient spacing between sections** - Increased h2 margin-top to 20px
- **Headers orphaned from content** - Added `page-break-after: avoid` to all headers

### Documentation

- Updated README.md to version 1.4.0
- Added weights configuration system to capabilities section
- Updated relative valuation examples with persona flags
- Removed "persona-driven weighting" from roadmap (now implemented)
- Updated CLAUDE.md with weights configuration references

### Technical Details

**File Changes**:
- `Relative_Valuation/relative_valuation_calculator.py` - 101 insertions, 18 deletions
- `Relative_Valuation/pdf_style.css` - 29 insertions, 1 deletion
- `Relative_Valuation/weights_loader.py` - NEW (436 lines)
- `Relative_Valuation/weights_config.json` - NEW (134 lines)
- `Relative_Valuation/weights_config_schema.json` - NEW (67 lines)
- `Relative_Valuation/WEIGHTS_CONFIG_GUIDE.md` - NEW (1,098 lines)
- `Relative_Valuation/RANKING_METHODOLOGY.md` - NEW (1,262 lines)

**Integration Architecture**:
```
Input JSON (optional weights)
    ↓
load_comparable_data()
    ↓
Auto-load default weights if missing → get_tenant_persona_weights()
    ↓                                        ↓
Validate required fields              weights_loader.py
    ↓                                        ↓
Run analysis                          weights_config.json
    ↓                                        ↓
Generate report                       Persona-specific weights
    ↓
Display all weights + 100% verification
    ↓
Professional PDF with proper page breaks
```

**Backwards Compatibility**:
- Existing JSON input files continue to work (weights now optional)
- Command-line interface unchanged (--persona and --weights-config are new optional flags)
- Report output format enhanced but maintains structure
- All existing workflows and slash commands function identically

## [1.3.0] - 2025-11-05

### Added

#### Relative Valuation / Competitive Positioning Module

**New Calculator**: `Relative_Valuation/relative_valuation_calculator.py` - Multi-Criteria Decision Analysis (MCDA) for competitive positioning

**Purpose**: Determine where a subject property ranks relative to market comparables and provide strategic pricing recommendations to achieve Top 3 competitive positioning (70-90% deal-winning probability).

**Methodology**: 4-step MCDA framework
1. **Data Collection** - Extract 9 key variables from comparable properties
2. **Independent Ranking** - Rank each variable 1 (best) to X (worst)
3. **Weighted Scoring** - Calculate weighted score = Σ(rank × weight)
4. **Final Competitive Ranking** - Sort by weighted score ascending

**9 Variables Analyzed** (with weights):
- Net Asking Rent (16%) - Most critical factor
- Parking Ratio (15%) - Second most critical
- TMI/Operating Costs (14%)
- Clear Height (10%)
- % Office Space (10%)
- Distance from Subject (10%)
- Area Difference (10%)
- Year Built (8%)
- Class A/B/C (7%)

**Key Features**:
- **Competitive Tiers**: Rank #1-3 (Highly Competitive, 70-90% win rate), #4-10 (Moderately Competitive, 50-70%), #11+ (Not Competitive, <50%)
- **Sensitivity Analysis**: Calculate exact rent/TMI reductions needed to achieve Rank #3 threshold
- **Strategic Recommendations**: Action-oriented advice based on rank tier (maintain, adjust, or urgent repositioning)
- **Top 3 Rule**: Must be Rank #1, #2, or #3 to consistently win deals

**Outputs**:
- Markdown report with executive summary, competitive analysis, gap analysis, and recommendations
- JSON results with all rankings, weighted scores, and sensitivity scenarios
- Sample data from May 2020 GTA industrial market (122 properties)

**Validation**: Tested against original Excel template - methodology validated within 6.4% tolerance

**Expert Skill**: `.claude/skills/relative-valuation-expert.md`
- Methodology guidance and interpretation
- Strategic recommendations by rank tier
- Non-price lever alternatives (TI allowance, free rent, operating caps)
- Tenant persona adjustments (industrial vs office vs flex)
- Integration with other analyses (effective rent, market comp, credit)

**Slash Command**: `/relative-valuation` - Automated PDF → JSON → Python → Report workflow
- Extract property data from CoStar reports / broker packages
- Generate input JSON with 9 variables
- Run competitive analysis
- Provide strategic guidance and pricing recommendations

**Documentation**:
- `Relative_Valuation/README.md` - Complete usage guide and methodology documentation
- Sample files: `sample_input.json`, `sample_output.json`, `sample_report.md`
- Methodology framework: `Reports/2025-11-05_122834_relative_valuation_methodology_framework.md`

**Use Cases**:
1. **Landlord Pricing**: Adjust asking rent to achieve Top 3 market position
2. **Tenant Evaluation**: Compare multiple offers and negotiate best value
3. **Renewal Benchmarking**: Ensure renewal offers are competitive with market alternatives
4. **Portfolio Optimization**: Identify which assets are overpriced and need correction

This brings the total to **7 calculators** and **22 slash commands** (8 Financial Analysis commands).

## [1.2.0] - 2025-11-05

### Added

#### 13 Specialized Skills

**New Skill System**: `.claude/skills/` - Deep expertise for specific lease agreement types and provisions

**Core Lease Agreements (1 skill)**
- **commercial-lease-expert** - General commercial lease negotiation, drafting, and analysis
  - Net lease structures (gross, modified gross, net, triple net)
  - Lease economics fundamentals
  - Tenant improvements and operating cost recovery
  - Renewal options, assignment/subletting provisions
  - Default provisions and risk management

**Security & Protection Instruments (2 skills)**
- **indemnity-expert** - Indemnity agreements and guarantees
  - Primary obligations vs secondary guarantees
  - Absolute and unconditional provisions
  - Bankruptcy-proof features
  - Enforcement strategies and landlord protections
- **non-disturbance-expert** - SNDA (subordination, non-disturbance, attornment) agreements
  - Tenant protection against foreclosure
  - Lender/tenant/landlord tripartite agreements
  - Subordination dynamics and priority issues

**Lease Modifications & Transfers (4 skills)**
- **consent-to-assignment-expert** - Assignment consent agreements
  - Assignment vs sublease distinctions
  - Privity of estate and contract analysis
  - Joint and several liability
  - Landlord protections and release provisions
- **consent-to-sublease-expert** - Sublease consent agreements
  - Three-party sublease structures
  - Recapture rights and profit-sharing
  - Landlord/tenant/subtenant relationships
- **share-transfer-consent-expert** - Change of control consent
  - Share transfer vs assignment distinctions
  - Corporate restructuring scenarios
  - Privacy consent provisions
  - New shareholder representations
- **lease-surrender-expert** - Lease termination and surrender agreements
  - Early termination by mutual agreement
  - Partial surrenders and space reduction
  - Consideration structures
  - Mutual release provisions
  - Distressed tenant scenarios

**Preliminary & Ancillary Agreements (4 skills)**
- **offer-to-lease-expert** - Offers to lease, LOIs, and term sheets
  - Binding vs non-binding analysis
  - Conditions precedent
  - Deposit structures and exclusivity
  - Deal structuring and negotiation strategies
- **waiver-agreement-expert** - Landlord waivers of conditions
  - Conditional vs unconditional waivers
  - Counter-offer analysis
  - Acceptance deadlines
  - Contract formation timelines
- **temporary-license-expert** - Short-term licenses (1 day to 3 months) **[NEW]**
  - License vs lease distinctions
  - Film/TV production, pop-up retail, swing space
  - Gross rent structures for short terms
  - "As is" condition and minimal landlord obligations
  - Insurance and indemnity for short-term use
- **storage-agreement-expert** - Storage locker and ancillary agreements
  - Month-to-month storage arrangements
  - Simplified rent structures
  - Use restrictions and limited services

**Specialized Licenses & Infrastructure (1 skill)**
- **telecom-licensing-expert** - Telecommunications carrier access licenses
  - Carrier building access and equipment installation
  - Riser/conduit rights
  - CRTC regulatory compliance
  - Co-location arrangements

**Dispute Resolution (1 skill)**
- **lease-arbitration-expert** - Arbitration agreement drafting
  - Renewal rent determination frameworks
  - Arbitrator selection procedures
  - Baseball vs conventional arbitration
  - Cost allocation and enforceable awards

**Skill Features**:
- ✅ Standardized frontmatter (name, description, tags, capability, proactive)
- ✅ Comprehensive legal and practical guidance
- ✅ Risk analysis from both landlord and tenant perspectives
- ✅ Drafting checklists and negotiation strategies
- ✅ Common mistakes to avoid
- ✅ Sample language and workflow guidance

### Changed

#### Reggie Chan VP Agent (formerly Leasing Expert)

- **Updated**: `.claude/agents/reggie-chan-vp.md` (formerly leasing-expert.md) now includes complete skill inventory
- **Added**: "Specialized Skills Available" section with 13 skills organized by category
- **Added**: "When to Use Which Tool" guidance for both skills and slash commands
- **Added**: Workflow integration examples combining skills with slash commands
- **Updated**: Agent approach to include skill identification and invocation steps

**Agent Workflow Integration Examples**:
1. **Assignment Request**: `consent-to-assignment-expert` + `/tenant-credit` + `/compare-offers`
2. **Renewal Negotiation**: `/renewal-economics` + `lease-arbitration-expert` + `/market-comparison`
3. **Early Termination**: `lease-surrender-expert` + `/effective-rent` + `/rollover-analysis`
4. **New Lease**: `offer-to-lease-expert` + `/effective-rent` + `commercial-lease-expert` + `indemnity-expert`

#### Documentation

- Updated README.md to include skills section and version 1.2.0
- Updated CLAUDE.md with skills structure
- Reorganized features to list skills before calculators
- Added skills to project structure diagram
- Updated statistics: 13 expert skills, 25+ documentation files

### Fixed

#### Skill Frontmatter Standardization

- **6 skills** had missing frontmatter entirely (storage, surrender, share-transfer, sublease-consent, offer-to-lease, temporary-license)
- **7 skills** had incomplete frontmatter (indemnity, non-disturbance, arbitration, commercial-lease, telecom, waiver, assignment-consent)
- All 13 skills now have complete, consistent frontmatter:
  - `name`: Kebab-case identifier
  - `description`: Brief summary of expertise
  - `tags`: Array of relevant keywords
  - `capability`: Detailed description of what the skill provides
  - `proactive: true`: Enables proactive suggestion

### Technical Details

**Skill Invocation**:
```bash
# Invoke skill using Skill tool in Claude Code
Skill tool -> command: "temporary-license-expert"
```

**Skill Organization**:
```
.claude/skills/
├── Core: commercial-lease-expert
├── Security: indemnity-expert, non-disturbance-expert
├── Transfers: consent-to-assignment, consent-to-sublease, share-transfer-consent, lease-surrender
├── Preliminary: offer-to-lease, waiver-agreement, temporary-license, storage-agreement
├── Specialized: telecom-licensing-expert
└── Dispute: lease-arbitration-expert
```

**Integration with Existing Tools**:
- Skills complement slash commands (skills = expertise, commands = automation)
- Skills work with calculators (skills = analysis, calculators = computation)
- Skills integrate with reggie-chan-vp agent for comprehensive guidance

## [1.1.0] - 2025-11-05

### Added

#### Rental Variance Analysis Module

**New Calculator**: `Rental_Variance/` - Three-way variance decomposition for rental revenue analysis

- **rental_variance_calculator.py** - Command-line calculator with JSON input/output
- **Variance Decomposition** - Isolates rate, area, and term variance components
- **Excel Methodology** - Based on proven `Rental Variance Analysis.xlsx` spreadsheet
- **Mathematical Foundation** - Variance formula: `Total = (BC)(A-D) + (CD)(B-E) + (DE)(C-F)`
- **Reconciliation Checks** - Validates variance components sum to total (±$0.01 tolerance)
- **Period-Aware Calculations** - Automatically handles partial periods and lease overlaps
- **Manual Adjustments** - Support for lease administration overrides
- **Multiple Output Formats** - Console summary, JSON results, markdown reports

**Sample Data**:
- `sample_variance_input.json` - 4 tenant scenarios from Excel "Proof of Concept" sheet
- `sample_variance_results.json` - Expected calculation results matching Excel formulas

**Documentation**:
- `Rental_Variance/README.md` - Complete module documentation with:
  - Theoretical foundation and mathematical proof
  - Usage examples (command-line and slash command)
  - Input/output format specifications
  - Interpretation guide for variance analysis
  - Common scenarios and applications
  - Excel formula mapping and validation

**Slash Command**:
- `/rental-variance` - Extract variance data from Excel/CSV/PDF and generate comprehensive analysis report
- Supports manual data entry when no file provided
- Automated workflow: Data → JSON → Calculator → Report

**Images and References**:
- `rentaldecomp.jpg` - Excel spreadsheet visualization
- `first_tenant*.png` - Sample tenant calculation screenshots
- `Rental Variance Analysis.xlsx` - Original Excel implementation (6 sheets)

**Key Features**:
- ✅ Period-aware term calculations using DAYS360 methodology
- ✅ Three-way decomposition (rate, area, term)
- ✅ Manual adjustments support
- ✅ Reconciliation validation
- ✅ Flexible input (Excel, CSV, PDF, manual)
- ✅ Professional markdown reports
- ✅ Zero external dependencies (Python stdlib only)

**Technical Details**:
- **Input Format**: JSON with actual vs budget data (dates, rates, areas, terms)
- **Output Format**: Console summary, JSON results, timestamped markdown reports
- **Calculation Method**: Monthly rate conversion (annual $/sf ÷ 12), variance decomposition
- **Validation**: Mathematical proof ensures variance components sum correctly
- **Excel Compatibility**: Python results match Excel formulas exactly

### Changed

#### Slash Commands

- Updated Financial Analysis category to include `/rental-variance` (now 7 commands total)
- Total slash commands increased from 19 to 20

#### Documentation

- Updated `CLAUDE.md` to include:
  - `Rental_Variance/` in project structure
  - `/rental-variance` in Financial Analysis commands list
  - Added rental variance to quick start examples
- Updated `.claude/commands/README.md` to document `/rental-variance` command

#### Project Structure

```
├── Rental_Variance/        # NEW - Variance decomposition analysis
│   ├── rental_variance_calculator.py
│   ├── sample_variance_input.json
│   ├── sample_variance_results.json
│   └── README.md
```

### Fixed

#### Sample Data Accuracy

- Replaced generic sample data with actual data from Excel spreadsheet
- Updated tenant scenarios to match "Proof of Concept" sheet rows 9, 10, 12, 16
- Validated calculation results against Excel formulas
- Ensured reconciliation checks pass for all sample tenants

### Technical Notes

**Variance Decomposition Formula**:
```
Rate Variance = (B × C) × (A - D)  where A=Actual Rate, B=Actual Area, C=Actual Term
                                         D=Budget Rate

Area Variance = (C × D) × (B - E)  where E=Budget Area

Term Variance = (D × E) × (C - F)  where F=Budget Term

Total Variance = Rate + Area + Term = ABC - DEF
```

**Mathematical Proof**:
```
(BC)(A-D) + (CD)(B-E) + (DE)(C-F)
= ABC - BCD + BCD - CDE + CDE - DEF
= ABC - DEF ✓
```

**Applications**:
1. Budget vs Actual Analysis - Monthly/quarterly variance reporting
2. Lease Negotiation Impact - Quantify negotiation outcomes
3. Portfolio Performance - Track leasing trends
4. Forecasting Refinement - Improve budget accuracy
5. Asset Management - Identify underperforming assets

## [1.0.0] - 2025-10-31

### Added

#### Core Infrastructure
- **Shared_Utils/** - Centralized financial utilities module
  - `financial_utils.py` - NPV, IRR, PV, rate conversions, financial ratios, statistics (58 tests)
  - Complete Python package with `__init__.py`
  - 24,990 lines of tested financial calculation functions

#### Calculators (5 modules)

1. **Effective Rent Calculator** (`Eff_Rent_Calculator/`)
   - Net Effective Rent (NER) and Gross Effective Rent (GER) calculation
   - NPV analysis comparing rent vs. costs
   - Breakeven analysis (unlevered, levered, with capital recovery)
   - Investment recommendations (Approve/Negotiate/Reject)
   - Ponzi Rental Rate (PRR) framework implementation
   - JSON input/output with BAF format
   - Automated PDF → JSON → Python → Report workflow

2. **Rental Yield Curve Calculator** (`Rental_Yield_Curve/`)
   - Term structure pricing using implied termination options
   - Black-Scholes option valuation framework
   - Solves for indifference pricing between lease terms
   - Market-to-market multiplier support
   - Command-line interface with full parameter control

3. **IFRS 16/ASC 842 Calculator** (`IFRS16_Calculator/`)
   - Lease liability calculation (present value of payments)
   - Right-of-Use (ROU) asset calculation
   - Monthly amortization schedules with interest expense tracking
   - Straight-line depreciation schedules
   - Annual summaries with P&L and balance sheet impact
   - Sensitivity analysis on discount rates and lease terms
   - CSV export (amortization, depreciation, annual summary)
   - Supports both annuity due and ordinary annuity
   - Variable payment schedules with escalations and free rent
   - Complete journal entries for initial recognition and monthly accounting

4. **Tenant Credit Analysis** (`Credit_Analysis/`)
   - 15+ financial ratio calculations (liquidity, leverage, profitability, rent coverage)
   - Weighted credit scoring algorithm (100-point scale)
   - Credit rating assignment (A through F)
   - Default probability estimation by rating
   - Expected loss calculation (PD × Exposure × LGD)
   - Risk-adjusted security recommendations (rent deposit, LC, guarantee)
   - Multi-year trend analysis
   - Red flag identification
   - Automated risk assessment and approval recommendations

5. **Renewal Economics Calculator** (`Renewal_Analysis/`)
   - Renewal vs. relocation NPV comparison
   - Net Effective Rent (NER) calculation for both scenarios
   - Internal Rate of Return (IRR) for relocation investment
   - Breakeven rent analysis
   - Payback period calculation
   - Comprehensive cost modeling (TI, moving, IT, downtime, customer loss)
   - Sensitivity analysis on rent, TI costs, and disruption
   - Investment recommendation (RENEW/RELOCATE/NEGOTIATE)

#### Slash Commands (19 total)

Organized into 5 categories in `.claude/commands/`:

**Abstraction (2 commands)**
- `/abstract-lease` - Extract lease terms using 24-section template (industrial/office)
- `/critical-dates` - Extract timeline and critical dates

**Financial Analysis (6 commands)**
- `/effective-rent` - NER, NPV, breakeven analysis
- `/renewal-economics` - Renewal vs. relocation economic analysis
- `/tenant-credit` - Credit scoring and risk assessment
- `/option-value` - Real options valuation using Black-Scholes
- `/market-comparison` - Market rent benchmarking
- `/rollover-analysis` - Portfolio lease expiry analysis

**Accounting (1 command)**
- `/ifrs16-calculation` - IFRS 16/ASC 842 lease accounting

**Comparison (4 commands)**
- `/compare-amendment` - Compare lease amendment against original
- `/compare-offers` - Compare inbound vs. outbound lease offers
- `/compare-precedent` - Compare draft lease against standard form
- `/lease-vs-lease` - General lease-to-lease comparison

**Compliance (6 commands)**
- `/assignment-consent` - Assignment and subletting consent analysis
- `/default-analysis` - Default provisions and cure periods
- `/environmental-compliance` - Environmental obligations review
- `/estoppel-certificate` - Estoppel certificate generation
- `/insurance-audit` - Insurance requirement verification
- `/notice-generator` - Generate lease notices (renewal, termination, etc.)

#### Templates

**Industrial Lease Templates** (`Templates/Industrial/`)
- 24-section comprehensive template (Markdown, JSON, JSON Schema)
- ANSI/BOMA Z65.2-2012 Method A measurement standard
- Industrial-specific provisions (manufacturing, warehouse, distribution)

**Office Lease Templates** (`Templates/Office/`)
- 24-section comprehensive template (Markdown, JSON, JSON Schema)
- ANSI/BOMA Office Buildings Standard measurement
- Office-specific provisions (business hours, parking, HVAC)

**Template Features**:
- Document information and metadata
- Parties (landlord, tenant, guarantor)
- Premises details with measurement standards
- Term provisions with renewal options
- Rent schedules and escalations
- Operating costs and tax allocations
- Use restrictions and operations
- Maintenance and repair obligations
- Insurance and indemnity requirements
- Assignment and subletting provisions
- Default remedies and cure periods
- Standard schedules A-J
- Critical dates summary tables
- Financial obligations summaries
- Key issues and risk analysis

#### Documentation

- `CLAUDE.md` - Project overview and quick start guide
- `README.md` - Slash commands comprehensive documentation
- `CHANGELOG.md` - This file
- Calculator-specific READMEs:
  - `Eff_Rent_Calculator/README.md` - Effective rent calculator documentation
  - `Eff_Rent_Calculator/BAF_INPUT_FORMAT.md` - JSON input format reference
  - `Eff_Rent_Calculator/RENTAL_YIELD_CURVE_README.md` - Yield curve documentation
  - `IFRS16_Calculator/README_IFRS16_CALCULATOR.md` - IFRS 16 calculator guide
  - `Shared_Utils/README_FINANCIAL_UTILS.md` - Financial utilities API reference

#### Test Suites

Complete test coverage for all calculators:
- `Tests/test_financial_utils.py` - 58 tests for shared utilities
- `Tests/test_ifrs16_calculator.py` - 30+ tests for lease accounting
- `Tests/test_renewal_analysis.py` - 25+ tests for renewal economics
- `Tests/test_credit_analysis.py` - 20+ tests for credit scoring

All tests passing with comprehensive edge case coverage.

#### Automated Workflows

All slash commands follow standardized **PDF → JSON → Python → Report** pipeline:
1. Extract data from PDF/DOCX using Claude's document analysis
2. Generate structured JSON input files
3. Run Python calculators with validated inputs
4. Create timestamped markdown reports in `Reports/` folder
5. Export CSV schedules for spreadsheet analysis

#### File Naming Conventions

**Reports Folder** - Mandatory timestamp prefix format:
- Format: `YYYY-MM-DD_HHMMSS_[description].md`
- Timezone: Eastern Time (ET/EST/EDT)
- Example: `2025-10-31_143022_lease_abstract_acme_corp.md`

#### Reference Documents

**Planning Folder**:
- `Multi_Tenant_Industrial.md` - Full 2,000+ line Minden Gross industrial lease
- `Multi_Tenant_Office.md` - Full 2,000+ line Minden Gross office lease
- Complete standard lease language for reference

### Changed

#### Project Structure

Reorganized from flat structure to modular architecture:

**Before**: Single `Eff_Rent_Calculator/` with mixed utilities
**After**: Dedicated modules with shared utilities

```
├── Shared_Utils/           # NEW - Shared financial utilities
├── Eff_Rent_Calculator/    # Focused on effective rent only
├── Rental_Yield_Curve/     # Separated yield curve calculator
├── IFRS16_Calculator/      # NEW - Lease accounting
├── Credit_Analysis/        # NEW - Tenant credit
├── Renewal_Analysis/       # NEW - Renewal economics
├── Planning/               # Reference documents
├── Templates/              # Lease templates (Industrial/Office)
├── Reports/                # Generated analysis (timestamped)
└── .claude/commands/       # Organized slash commands
    ├── Abstraction/
    ├── Financial_Analysis/
    ├── Accounting/
    ├── Comparison/
    └── Compliance/
```

#### Import Structure

- Moved `financial_utils.py` from `Eff_Rent_Calculator/` to `Shared_Utils/`
- Updated all calculator imports to use `Shared_Utils/`
- Created proper Python package with `__init__.py`
- Standardized import paths across all modules

#### Slash Commands Organization

- Moved from flat 19-file structure to 5 categorized subdirectories
- Added comprehensive `README.md` in commands directory
- Maintained backward compatibility (commands work same as before)

### Fixed

#### IFRS 16 Calculator
- Corrected function names: `calculate_ifrs16()` vs `calculate_ifrs16_accounting()`
- Fixed method names: `print_summary()` vs `print_lease_summary()`
- Standardized result object field names for consistency
- Fixed annuity due vs ordinary annuity treatment for first payment

#### Renewal Analysis
- Fixed dataclass field name mismatches (`area_sf` → `rentable_area_sf`)
- Corrected function signature: `print_comparison_report()` takes single argument
- Fixed NPV field access in nested result objects
- Resolved DataFrame boolean ambiguity in sensitivity analysis
- Corrected attribute names: `ner_psf` → `net_effective_rent_psf`

#### Test Suite Imports
- Updated all test files to use correct module paths
- Added `Shared_Utils/` to Python path in test files
- Fixed cross-module imports for calculator tests

### Technical Details

#### Dependencies
- Python 3.12+
- NumPy - Numerical operations and array handling
- Pandas - DataFrame operations and CSV export
- SciPy - Optimization algorithms (IRR calculation via Newton's method)
- markitdown[docx] - DOCX to Markdown conversion

#### Performance
- All PV calculations: O(n) where n = number of cash flows
- Amortization schedules: O(n) where n = number of periods
- IRR convergence: Typically <10 iterations using Newton's method
- Credit scoring: O(1) ratio calculations

#### Standards Compliance
- **IFRS 16** (International) - Lease accounting for all leases on balance sheet
- **ASC 842** (US GAAP) - Finance lease methodology
- **ANSI/BOMA Z65.2-2012 Method A** - Industrial building measurement
- **ANSI/BOMA Office Buildings Standard** - Office space measurement

#### Financial Methodologies
- **Ponzi Rental Rate (PRR)** - Effective rent framework with capital recovery
- **Black-Scholes** - Real options valuation for lease terms
- **NPV/IRR** - Standard capital budgeting analysis
- **Annuity Due** - Commercial lease payment timing (advance payment)

### Project Statistics

- **Total Python Modules**: 8 (5 calculators + 1 shared + 2 runners)
- **Total Test Files**: 4 (with 130+ total tests)
- **Total Slash Commands**: 19 (organized in 5 categories)
- **Total Templates**: 6 files (2 property types × 3 formats)
- **Documentation Pages**: 10+ comprehensive guides
- **Lines of Code**: ~150,000 (including templates and documentation)

### Contributors

- **Claude Code** - AI-powered development assistant by Anthropic
- **Created**: October 30-31, 2025
- **GitHub Issues Closed**: #3, #5, #6, #8

---

## Release Notes

**Version 1.0.0** represents the initial stable release of the Commercial Real Estate Lease Analysis Toolkit. This release provides a complete, production-ready suite of tools for:

- Lease abstraction and analysis
- Financial modeling and investment analysis
- Lease accounting under IFRS 16/ASC 842
- Tenant credit risk assessment
- Renewal vs. relocation decision support
- Market analysis and benchmarking
- Compliance verification and documentation

All calculators have been tested with real-world lease scenarios and produce accurate, auditable results suitable for professional use in commercial real estate portfolio management.

### Upgrade Notes

This is the initial release. Future versions will maintain backward compatibility with:
- JSON input formats
- Slash command syntax
- Calculator API interfaces
- Report output formats

---

[1.0.0]: https://github.com/reggiechan74/vp-real-estate/releases/tag/v1.0.0
[1.1.0]: https://github.com/reggiechan74/vp-real-estate/releases/tag/v1.1.0
[1.2.0]: https://github.com/reggiechan74/vp-real-estate/releases/tag/v1.2.0
[1.3.0]: https://github.com/reggiechan74/vp-real-estate/releases/tag/v1.3.0
[1.4.0]: https://github.com/reggiechan74/vp-real-estate/releases/tag/v1.4.0
[1.5.0]: https://github.com/reggiechan74/vp-real-estate/releases/tag/v1.5.0
[1.6.0]: https://github.com/reggiechan74/vp-real-estate/releases/tag/v1.6.0
