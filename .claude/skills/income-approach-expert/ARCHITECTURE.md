# Income Approach Land Valuation Calculator - Architecture Documentation

## Design Philosophy

**Modular Architecture:** Thin orchestration layer with specialized, testable modules
- **Main Calculator:** <400 lines (actual: 223 non-comment lines)
- **Modules:** Single-responsibility components
- **Shared Utils:** Reuse existing financial and reporting utilities
- **Testability:** 20 comprehensive unit tests (100% pass rate)

## File Structure

\`\`\`
income-approach-expert/
├── land_capitalization_calculator.py (323 lines) - Main orchestration
├── modules/
│   ├── __init__.py (18 lines)           - Package exports
│   ├── validators.py (152 lines)        - Input validation
│   ├── rent_analysis.py (65 lines)      - Market rent analysis
│   ├── cap_rate_selection.py (132 lines) - 3 cap rate methods
│   ├── income_reconciliation.py (104 lines) - Reconciliation logic
│   └── output_formatters.py (252 lines) - Report generation
├── samples/
│   ├── telecom_tower_site_input.json    - Full-featured example
│   └── simple_land_lease_input.json     - Minimal example
├── tests/
│   └── test_land_capitalization_calculator.py (370 lines, 20 tests)
├── README.md                            - Full documentation
├── QUICKSTART.md                        - 10-minute getting started
└── ARCHITECTURE.md                      - This file
\`\`\`

**Total:** 1,046 lines of production code (excluding tests)

## Component Design

### 1. Main Calculator (land_capitalization_calculator.py)

**Responsibilities:**
- CLI argument parsing
- Input/output file handling
- Orchestration of calculation workflow
- Error handling and user feedback

**Key Functions:**
- \`calculate_noi()\` - NOI calculation
- \`calculate_income_value()\` - Value = NOI ÷ Cap Rate
- \`process_valuation()\` - Main workflow orchestrator
- \`main()\` - CLI entry point

**Design Pattern:** Thin orchestration layer
- No business logic
- Delegates to specialized modules
- Focuses on workflow coordination

### 2. Validators Module (modules/validators.py)

**Responsibilities:**
- Input data structure validation
- Data type checking
- Range validation
- Error message generation

**Key Functions:**
- \`validate_input_data()\` - Main validation entry point
- \`_validate_land_rent()\` - Land rent section validation
- \`_validate_market_data()\` - Market data validation
- \`_validate_operating_expenses()\` - Expense validation

**Validation Rules:**
- Required fields must be present
- Numeric values must be positive
- Cap rate range: low < high, both 0-1
- At least 1 comparable rent and 1 comparable sale

### 3. Rent Analysis Module (modules/rent_analysis.py)

**Responsibilities:**
- Comparable rent processing
- Statistical analysis
- Subject rent comparison
- Market rent conclusion

**Key Functions:**
- \`analyze_market_rent()\` - Main analysis function

**Algorithm:**
1. Extract rent values from comparables
2. Calculate statistics (mean, median, min, max, range)
3. Compare subject rent to market range
4. If within range → use subject rent
5. If outside range → use market median
6. Calculate variance from market

### 4. Cap Rate Selection Module (modules/cap_rate_selection.py)

**Responsibilities:**
- Market extraction cap rate calculation
- Band of investment method (optional)
- Buildup method (optional)
- Cap rate reconciliation

**Key Functions:**
- \`select_capitalization_rate()\` - Main selection function

**Three Methods:**

**Method 1: Market Extraction (Primary)**
\`\`\`python
cap_rate = noi / sale_price
\`\`\`
- Extract from each comparable sale
- Calculate statistics (mean, median, range)
- Select median as primary indicator

**Method 2: Band of Investment (Supporting)**
\`\`\`python
cap_rate = (LTV × Debt_Yield) + (Equity% × Equity_Yield)
\`\`\`
- Requires financing data
- Validates market extraction
- Reports variance

**Method 3: Buildup (Supporting)**
\`\`\`python
cap_rate = Risk_Free + Liquidity + Inflation + Business_Risk
\`\`\`
- Requires risk components
- Theoretical validation
- Reports variance

**Reconciliation:**
- Primary reliance on market extraction median
- Validate against cap_rate_range
- Adjust to range if outside bounds
- Compare with supporting methods

### 5. Income Reconciliation Module (modules/income_reconciliation.py)

**Responsibilities:**
- Reconcile income vs. sales comparison approach
- Variance analysis
- Final value conclusion
- Sensitivity analysis

**Key Functions:**
- \`reconcile_with_sales_comparison()\` - Main reconciliation

**Reconciliation Logic:**
\`\`\`
Variance ≤ 10%:    Use income approach value
Variance 10-20%:   Use average of both approaches
Variance > 20%:    Use income approach, flag for investigation
\`\`\`

**Sensitivity Analysis:**
- Test cap rate adjustments: -0.5%, -0.25%, 0%, +0.25%, +0.5%
- Calculate value impact
- Report percentage variance
- Assess risk exposure

### 6. Output Formatters Module (modules/output_formatters.py)

**Responsibilities:**
- Markdown report generation
- Table formatting
- Timestamped filename generation
- Report structure

**Key Functions:**
- \`format_report()\` - Main report generator

**Report Sections:**
1. Document Header (title, subtitle, metadata)
2. Executive Summary (final value, key inputs)
3. Market Rent Analysis (comparables, statistics, conclusion)
4. Cap Rate Selection (3 methods, reconciliation)
5. NOI Calculation (income, expenses, net)
6. Land Value by Income Approach (formula, calculation)
7. Reconciliation (variance, final value)
8. Sensitivity Analysis (cap rate impact table)
9. Assumptions and Limiting Conditions
10. Footer (timestamp, version)

**Uses Shared Utils:**
- \`eastern_timestamp()\` - ET timestamps
- \`format_markdown_table()\` - Table formatting
- \`generate_document_header()\` - Header generation

## Data Flow

\`\`\`
1. Input JSON
   ↓
2. validate_input_data() → Validated data
   ↓
3. analyze_market_rent() → Market rent analysis
   ↓
4. select_capitalization_rate() → Cap rate analysis
   ↓
5. calculate_noi() → NOI calculation
   ↓
6. calculate_income_value() → Income approach value
   ↓
7. reconcile_with_sales_comparison() → Reconciliation & sensitivity
   ↓
8. format_report() → Markdown report
   ↓
9. Output: JSON results + Markdown report
\`\`\`

## Integration with Shared Utilities

### Shared_Utils/financial_utils.py
**Available (not currently used):**
- \`npv()\`, \`irr()\` - For future DCF extensions
- \`present_value()\` - For lease escalation modeling
- \`calculate_financial_ratios()\` - For tenant analysis

**Future Use Cases:**
- Multi-year lease escalation modeling
- DCF vs. direct capitalization comparison
- Risk-adjusted discount rates

### Shared_Utils/report_utils.py
**Currently Used:**
- \`eastern_timestamp()\` - Timestamped filenames
- \`format_markdown_table()\` - Table formatting
- \`generate_document_header()\` - Report headers

**Format:**
- Reports: \`YYYY-MM-DD_HHMMSS_income_approach_{site_type}.md\`
- Complies with CLAUDE.md file naming requirements

## Testing Strategy

### Unit Test Coverage (20 tests)

**TestValidators (5 tests):**
- Valid input acceptance
- Missing required fields
- Invalid data types
- Range violations
- Empty collections

**TestRentAnalysis (3 tests):**
- Rent statistics calculation
- Subject within range
- Subject outside range

**TestCapRateSelection (4 tests):**
- Market extraction
- Cap rate within range
- Band of investment method
- Buildup method

**TestNOICalculation (1 test):**
- NOI calculation accuracy

**TestIncomeValue (3 tests):**
- Income value calculation
- Zero cap rate error
- Negative cap rate error

**TestReconciliation (3 tests):**
- Within 10% variance
- 10-20% variance
- Sensitivity analysis

**TestEndToEnd (1 test):**
- Full workflow integration

**Test Results:** 20/20 passing (100%)

## Performance Characteristics

**Input Validation:** O(n) where n = number of comparables
**Rent Analysis:** O(n) where n = number of comparable rents
**Cap Rate Selection:** O(m) where m = number of comparable sales
**Reconciliation:** O(1) constant time
**Report Generation:** O(n + m) combined comparables

**Typical Performance:**
- 4 rent comps + 3 sale comps: <0.1 seconds
- 20 rent comps + 10 sale comps: <0.2 seconds
- Report generation: <0.5 seconds

## Extension Points

### 1. Multiple Income Scenarios
\`\`\`python
scenarios = ['base', 'upside', 'downside']
for scenario in scenarios:
    noi = calculate_scenario_noi(scenario)
    value = calculate_income_value(noi, cap_rate)
\`\`\`

### 2. Lease Escalation Modeling
\`\`\`python
from Shared_Utils.financial_utils import present_value

escalated_rents = model_rent_escalations(base_rent, term, escalation_rate)
pv_rent_stream = present_value(escalated_rents, discount_rate)
\`\`\`

### 3. DCF Analysis
\`\`\`python
from Shared_Utils.financial_utils import npv, irr

cash_flows = project_cash_flows(rent, expenses, term)
dcf_value = npv(cash_flows, discount_rate)
\`\`\`

### 4. Monte Carlo Risk Analysis
\`\`\`python
import numpy as np

cap_rate_samples = np.random.normal(cap_rate_mean, cap_rate_std, 10000)
value_distribution = noi / cap_rate_samples
percentiles = np.percentile(value_distribution, [5, 50, 95])
\`\`\`

### 5. Market Rent Adjustments
\`\`\`python
adjustments = {
    'size': -0.05,        # -5% for smaller size
    'location': 0.10,     # +10% for superior location
    'condition': -0.03    # -3% for inferior condition
}
adjusted_rent = apply_adjustments(base_rent, adjustments)
\`\`\`

## Error Handling Strategy

### Input Validation Errors
- Comprehensive validation before calculation
- Detailed error messages with field names
- Early exit on validation failure

### Calculation Errors
- Division by zero protection (cap rate)
- Negative value detection
- Range bound checking

### File I/O Errors
- Missing file detection
- Invalid JSON handling
- Permission errors
- Path validation

### Example Error Messages
\`\`\`
ERROR: Input validation failed:
  - Missing required field: site_type
  - land_rent.annual_rent must be positive
  - market_data.cap_rate_range.low must be less than high
\`\`\`

## Design Decisions

### Why Modular Architecture?
- **Testability:** Each module can be tested independently
- **Maintainability:** Single-responsibility principle
- **Extensibility:** Easy to add new cap rate methods
- **Reusability:** Modules can be used in other calculators

### Why Three Cap Rate Methods?
- **Market Extraction:** Primary method based on actual sales
- **Band of Investment:** Validates with financing perspective
- **Buildup:** Validates with risk analysis perspective
- **Reconciliation:** Increases confidence in conclusion

### Why Sensitivity Analysis?
- **Risk Assessment:** Shows value volatility
- **Decision Support:** Helps understand cap rate impact
- **Communication:** Demonstrates due diligence

### Why Reconciliation Logic?
- **Quality Control:** Flags significant variances
- **Professional Standards:** Follows appraisal best practices
- **Transparency:** Documents weighting rationale

## Dependencies

**Standard Library:**
- json - Input/output parsing
- sys - System interaction
- os - File path handling
- argparse - CLI argument parsing
- statistics - Statistical calculations

**Internal:**
- Shared_Utils/report_utils - Report formatting
- Shared_Utils/financial_utils - Financial calculations (optional)

**No External Dependencies:** Pure Python 3.8+ implementation

## Compliance

### CLAUDE.md Requirements
✓ Timestamped reports: \`YYYY-MM-DD_HHMMSS_*.md\`
✓ Reports/ directory output
✓ Shared_Utils integration
✓ Modular architecture
✓ Comprehensive testing

### Architectural Requirements
✓ Main calculator <400 lines (actual: 223)
✓ Modular design with separate concerns
✓ Import from Shared_Utils
✓ Complete functionality delivered

## Version History

**v1.0 (2025-11-17)**
- Initial release
- 3 cap rate methods
- Reconciliation logic
- Sensitivity analysis
- 20 unit tests
- Complete documentation

---

**Maintainer:** Claude Code
**Created:** 2025-11-17
**Last Updated:** 2025-11-17
