# Infrastructure Cost Calculator - Architecture Documentation

## Design Principles

### 1. Modular Architecture

**Thin Orchestration Layer:**
- Main calculator: 366 lines (target: <400 lines)
- Acts as coordinator, not implementation
- Imports specialized modules for each function

**Specialized Modules:**
```
validators.py (254 lines)
├── Input validation
├── Schema verification
└── Business rule enforcement

replacement_cost.py (204 lines)
├── RCN calculation
├── Unit cost analysis
└── Inflation adjustments

depreciation_analysis.py (337 lines)
├── Physical depreciation (age/life + condition)
├── Functional obsolescence
├── External obsolescence
└── Total depreciation reconciliation

cost_reconciliation.py (324 lines)
├── Market reconciliation logic
├── Confidence scoring
└── Statistical analysis

output_formatters.py (423 lines)
├── Markdown report generation
├── Tables and formatting
└── Section builders
```

**Total:** ~1,576 lines of modular code + 366 line orchestrator

### 2. Separation of Concerns

**Each module has single responsibility:**

- **validators.py:** Know if input is valid (not what to do with it)
- **replacement_cost.py:** Calculate RCN (not depreciation)
- **depreciation_analysis.py:** Calculate depreciation (not market reconciliation)
- **cost_reconciliation.py:** Reconcile approaches (not generate reports)
- **output_formatters.py:** Format output (not perform calculations)

**Benefits:**
- Easy to test in isolation
- Easy to modify one aspect without breaking others
- Clear dependencies and data flow
- Reusable components

### 3. Shared Utilities Integration

**Import from parent project:**
```python
from Shared_Utils.report_utils import (
    eastern_timestamp,           # Consistent timestamps
    format_markdown_table,       # Professional tables
    generate_document_header     # Standard headers
)
```

**Planned integration:**
```python
from Shared_Utils.financial_utils import (
    npv,                         # For income approach integration
    irr,                         # For investment analysis
    descriptive_statistics       # For comp analysis
)
```

**Benefits:**
- Code reuse across project
- Consistent formatting and timestamps
- Shared validation and utilities
- Single source of truth for common functions

## Data Flow

### Input Processing

```
JSON Input File
    ↓
validate_input() → Tuple[bool, List[errors]]
    ↓
(if valid) → calculate_infrastructure_cost()
    ↓
Results Dictionary
```

### Calculation Pipeline

```
1. Replacement Cost New
   calculate_replacement_cost_new(costs)
   ├── Direct Costs (materials + labor)
   ├── Overhead (% of direct)
   ├── Profit (% of subtotal)
   └── → RCN

2. Physical Depreciation
   calculate_physical_depreciation(data, rcn)
   ├── Age/Life method (primary)
   ├── Condition method (validation)
   ├── Variance check
   └── → Physical Depreciation

3. Functional Obsolescence
   calculate_functional_obsolescence(value, rcn, specs)
   ├── Convert to dollar amount
   ├── Calculate severity
   └── → Functional Obsolescence

4. External Obsolescence
   calculate_external_obsolescence(value, rcn, market)
   ├── Convert to dollar amount
   ├── Calculate severity
   └── → External Obsolescence

5. Total Depreciation
   calculate_total_depreciation(physical, functional, external, rcn)
   ├── Sum all depreciation
   ├── Calculate percentages
   └── → Depreciated Replacement Cost

6. Market Reconciliation
   reconcile_with_market(depreciated_cost, market_data, asset_type)
   ├── Calculate market statistics
   ├── Compare cost vs market
   ├── Apply reconciliation rules
   └── → Reconciled Value

7. Confidence Scoring
   calculate_confidence_score(cost, market, depreciation)
   ├── Market data quality (+/- 20)
   ├── Depreciation quality (+/- 15)
   ├── Age/life reasonableness (+/- 10)
   ├── Obsolescence documentation (+5)
   └── → Confidence Score (0-100)
```

### Output Generation

```
Results Dictionary
    ↓
format_cost_report(...)
    ├── Executive Summary
    ├── Asset Information
    ├── RCN Breakdown
    ├── Depreciation Analysis
    ├── Market Reconciliation
    ├── Valuation Conclusion
    └── Methodology Notes
    ↓
Markdown Report + Optional JSON
```

## Module Interfaces

### validators.py

**Public Functions:**
```python
validate_input(data: Dict) -> Tuple[bool, List[str]]
validate_construction_costs(costs: Dict) -> Tuple[bool, List[str]]
validate_depreciation_data(depreciation: Dict) -> Tuple[bool, List[str]]
validate_market_data(market_data: Optional[Dict]) -> Tuple[bool, List[str]]
validate_specifications(specs: Optional[Dict]) -> Tuple[bool, List[str]]
```

**Returns:**
- Tuple of (is_valid, error_messages)
- Empty error list if valid
- Does not raise exceptions (returns errors for reporting)

### replacement_cost.py

**Public Functions:**
```python
calculate_replacement_cost_new(costs: Dict) -> Dict
calculate_unit_rcn(total: float, quantity: float, unit: str) -> Dict
adjust_rcn_for_inflation(base: float, base_year: int, current: int, rate: float) -> Dict
calculate_rcn_with_premium(base: float, premium: float, reason: str) -> Dict
```

**Returns:**
- Dictionary with detailed breakdown
- All intermediate values included
- Percentages and amounts clearly separated

### depreciation_analysis.py

**Public Functions:**
```python
calculate_physical_depreciation(data: Dict, rcn: float) -> Dict
calculate_functional_obsolescence(value: float, rcn: float, specs: Optional[Dict]) -> Dict
calculate_external_obsolescence(value: float, rcn: float, market: Optional[Dict]) -> Dict
calculate_total_depreciation(physical: Dict, functional: Dict, external: Dict, rcn: float) -> Dict
```

**Smart Input Handling:**
- Accepts dollar amounts or percentages (0-1)
- Auto-detects based on value range
- Converts to standardized format

**Returns:**
- Detailed breakdown dictionaries
- Includes severity classifications
- Provides examples and recommendations

### cost_reconciliation.py

**Public Functions:**
```python
reconcile_with_market(depreciated_cost: float, market_data: Optional[Dict], asset_type: str) -> Dict
calculate_confidence_score(cost: float, market_data: Optional[Dict], depreciation: Dict) -> Dict
```

**Reconciliation Logic:**
- No market data: Cost approach only
- Close agreement (<10%): Average
- Cost high (>20%): Market emphasized
- Market high (>20%): Verify quality
- Moderate (10-20%): Weighted average

**Returns:**
- Reconciliation analysis
- Market statistics
- Comparable sales detail
- Confidence assessment

### output_formatters.py

**Public Functions:**
```python
format_cost_report(...) -> str  # Full markdown report
format_summary_table(results: Dict) -> str  # One-line summary
```

**Private Functions:**
```python
_format_executive_summary(...)
_format_asset_information(...)
_format_rcn_section(...)
_format_depreciation_section(...)
_format_reconciliation_section(...)
_format_conclusion_section(...)
_format_methodology_notes()
```

**Features:**
- Professional markdown formatting
- Tables with alignment
- Code blocks for calculations
- Consistent section structure

## Testing Strategy

### Unit Tests (17 tests)

**validators.py tests:**
- Valid inputs pass
- Missing fields detected
- Negative values rejected
- Business rules enforced

**replacement_cost.py tests:**
- Basic RCN calculation correct
- Zero overhead/profit handled
- Edge cases covered

**depreciation_analysis.py tests:**
- Age/life method accurate
- Fully depreciated assets (100%)
- Percentage vs dollar input
- Severity classifications
- Total depreciation reconciliation

**cost_reconciliation.py tests:**
- No market data handled
- Market reconciliation logic
- Statistics calculated correctly

**Integration tests:**
- Complete workflow (transmission tower)
- No market data workflow (pipeline)
- All modules work together

### Test Coverage

```
TestValidators (4 tests)
├── Valid construction costs
├── Missing required fields
├── Negative values
└── Effective age > economic life

TestReplacementCost (2 tests)
├── Basic RCN calculation
└── Zero overhead/profit

TestDepreciationAnalysis (6 tests)
├── Physical depreciation (age/life)
├── Fully depreciated asset
├── Functional obsolescence (percentage)
├── Functional obsolescence (dollar)
├── External obsolescence (none)
└── Total depreciation

TestCostReconciliation (2 tests)
├── No market data
└── With market data

TestIntegration (2 tests)
├── Transmission tower (complete workflow)
└── Pipeline (no market data)
```

**Run tests:**
```bash
python tests/test_calculator.py
# Expected: Ran 17 tests in ~0.03s - OK
```

## Error Handling

### Validation Errors

**Strategy:** Validate early, fail fast with clear messages

```python
valid, errors = validate_input(data)
if not valid:
    error_msg = "Input validation failed:\n" + "\n".join(f"  - {err}" for err in errors)
    raise ValueError(error_msg)
```

**Benefits:**
- User sees all validation errors at once (not just first)
- Clear indication of what's wrong
- No partial calculations with invalid data

### Calculation Errors

**Strategy:** Graceful handling with sensible defaults

```python
# Division by zero
if denominator == 0:
    return default_value  # or handle specially

# Missing optional data
market_data = input_data.get('market_data', None)
if market_data is None:
    # Use cost approach only
    return {...}
```

**Benefits:**
- Calculator doesn't crash on edge cases
- Missing optional data handled gracefully
- Warnings for unusual situations

### Output Errors

**Strategy:** Ensure output directory exists

```python
os.makedirs(os.path.dirname(output_path), exist_ok=True)
```

## Performance Considerations

### Current Performance

**Typical execution time:**
- Input validation: <1ms
- RCN calculation: <1ms
- Depreciation analysis: <1ms
- Market reconciliation: <1ms
- Report generation: ~5ms
- **Total: ~10ms per asset**

**Test results:**
```
17 tests in 0.028s
≈ 1.6ms per test (includes setup/teardown)
```

### Optimization Opportunities

**Not currently needed, but if required:**

1. **Batch Processing:**
   - Process multiple assets in single run
   - Shared market data lookups
   - Parallel calculation (multiprocessing)

2. **Caching:**
   - Cache market statistics for asset type
   - Reuse comparable analysis
   - Pre-calculate lookup tables

3. **Lazy Loading:**
   - Only load modules when needed
   - Defer expensive calculations
   - Stream report generation

## Extension Points

### Adding New Depreciation Methods

**Current:** Age/Life + Condition

**Future additions:**
```python
# In depreciation_analysis.py

def calculate_physical_depreciation_breakdown(data, rcn):
    """Calculate using detailed breakdown method."""
    # Structural: Curable
    # Structural: Incurable
    # Short-lived items
    # Long-lived items
    pass

def calculate_physical_depreciation_market_extraction(sales, rcn):
    """Calculate from market data (paired sales)."""
    # Extract depreciation from comparable sales
    pass
```

**Integration:** Add to total_depreciation() with method selection parameter

### Adding Income Approach

**Implementation location:** New module `income_capitalization.py`

```python
def capitalize_easement_income(annual_rent, cap_rate, term):
    """Capitalize annual easement payments."""
    # Calculate present value of income stream
    # Compare to cost approach
    pass

def reconcile_cost_and_income(cost_value, income_value):
    """Reconcile cost and income approaches."""
    # Weight based on reliability
    pass
```

**Integration:** Add to reconciliation module as third approach

### Adding Sensitivity Analysis

**Implementation location:** New module `sensitivity_analysis.py`

```python
def analyze_depreciation_sensitivity(base_input, ranges):
    """Test depreciation rate scenarios."""
    # Vary effective age +/- 20%
    # Vary economic life +/- 20%
    # Calculate impact on value
    pass

def analyze_market_sensitivity(base_input, ranges):
    """Test market reconciliation scenarios."""
    # Vary market median +/- 10%
    # Test different reconciliation weights
    pass
```

**Integration:** Optional analysis after base calculation

## Dependencies

### Python Standard Library

```python
import json           # Input/output
import sys            # Path manipulation
import os             # File operations
import argparse       # CLI interface
from typing import *  # Type hints
```

### Project Dependencies

```python
from Shared_Utils.report_utils import (
    eastern_timestamp,
    format_markdown_table,
    generate_document_header
)
```

### Third-Party Dependencies

**Current:** None required

**Optional (for future enhancements):**
- `numpy` - Advanced statistical analysis
- `pandas` - Tabular data manipulation
- `scipy` - Regression analysis
- `matplotlib` - Visualization

## File Organization

```
cost-approach-expert/
├── infrastructure_cost_calculator.py    # Main (366 lines)
├── modules/                              # Modular components
│   ├── __init__.py                      # Exports (34 lines)
│   ├── validators.py                    # Validation (254 lines)
│   ├── replacement_cost.py              # RCN (204 lines)
│   ├── depreciation_analysis.py         # Depreciation (337 lines)
│   ├── cost_reconciliation.py           # Reconciliation (324 lines)
│   └── output_formatters.py             # Reports (423 lines)
├── samples/                              # Test data
│   ├── transmission_tower.json          # With market data
│   ├── pipeline_segment.json            # No market data
│   └── substation.json                  # High depreciation
├── tests/                                # Test suite
│   └── test_calculator.py               # 17 unit tests
├── Reports/                              # Generated reports
│   └── YYYY-MM-DD_HHMMSS_*.md
├── README.md                             # Complete documentation
├── QUICK_START.md                        # Getting started guide
└── ARCHITECTURE.md                       # This file
```

## Design Decisions

### Why Modular Design?

**Decision:** Separate modules vs single file

**Rationale:**
- **Maintainability:** Easy to find and fix issues
- **Testability:** Unit test each module independently
- **Reusability:** Import specific functions elsewhere
- **Clarity:** Each file has clear purpose
- **Growth:** Add modules without affecting others

**Trade-offs:**
- More files to manage (mitigated by clear structure)
- Import overhead (negligible - ~1ms)
- **Benefit >> Cost**

### Why Validation Module?

**Decision:** Separate validation from calculation

**Rationale:**
- **Fail Fast:** Catch errors before calculation
- **Clear Errors:** User sees all issues at once
- **Reusability:** Validate in other contexts
- **Testing:** Test validation independently

**Alternative considered:** Validate inside each calculation function
**Rejected because:** Redundant validation, unclear error source

### Why Separate Reconciliation Module?

**Decision:** cost_reconciliation.py instead of in output_formatters.py

**Rationale:**
- **Logic vs Display:** Reconciliation is analysis, not formatting
- **Testability:** Test reconciliation logic independently
- **Reusability:** Use reconciliation without report generation
- **Clarity:** Clear what's calculation vs presentation

### Why Keep Shared_Utils Import?

**Decision:** Import from parent project vs copy code

**Rationale:**
- **DRY:** Don't Repeat Yourself
- **Consistency:** Same timestamps across all reports
- **Maintenance:** Fix bugs in one place
- **Standards:** Enforce project-wide standards

**Trade-offs:**
- Dependency on parent project (acceptable - this is a sub-module)
- Import path complexity (mitigated by sys.path.insert)

## Future Architecture

### Phase 2: Income Approach Integration

```
infrastructure_cost_calculator.py
├── modules/
│   ├── [existing modules]
│   ├── income_capitalization.py         # NEW
│   └── approach_reconciliation.py       # NEW (3-way)
```

### Phase 3: Batch Processing

```
batch_cost_calculator.py                 # NEW
├── infrastructure_cost_calculator.py (API mode)
└── modules/
    └── batch_processor.py               # NEW
```

### Phase 4: Advanced Analysis

```
modules/
├── [existing modules]
├── sensitivity_analysis.py              # NEW
├── market_extraction.py                 # NEW
└── statistical_validation.py            # NEW
```

## Lessons Learned

### What Worked Well

1. **Modular design:** Easy to develop and test incrementally
2. **Clear interfaces:** Each module has obvious inputs/outputs
3. **Validation first:** Caught errors early in testing
4. **Comprehensive tests:** Found edge cases during development

### What Could Be Improved

1. **Type hints:** More comprehensive type annotations
2. **Logging:** Add logging module for debugging
3. **Configuration:** External config file for defaults
4. **Documentation:** Inline docstring examples

### Best Practices Demonstrated

1. **Single Responsibility:** Each module does one thing
2. **Dependency Injection:** Pass dependencies, don't import
3. **Fail Fast:** Validate early, fail with clear errors
4. **Test Driven:** Tests written alongside implementation
5. **Documentation:** README, QUICK_START, ARCHITECTURE docs

---

**Architecture Documentation v1.0**
**Author:** Claude Code
**Last Updated:** 2025-11-17
