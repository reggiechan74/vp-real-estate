# Injurious Affection Calculator - Refactoring & Enhancement Plan

## Executive Summary

Transform the injurious affection calculator from a functional but monolithic 900-line script into a production-grade, modular, fully-validated calculation engine suitable for professional expropriation work.

**Duration**: 2-4 days (phased implementation)
**Effort**: ~16-24 hours
**Risk**: Low (maintain backward compatibility)
**Priority**: High (critical calculation accuracy for construction impact damages)

**Success Pattern**: Following the proven refactoring methodology from severance damages calculator (943 → 360 lines, 62% reduction).

---

## Table of Contents

1. [Current State Analysis](#current-state-analysis)
2. [Goals & Success Criteria](#goals--success-criteria)
3. [Proposed Architecture](#proposed-architecture)
4. [Implementation Phases](#implementation-phases)
5. [File Structure](#file-structure)
6. [Testing Strategy](#testing-strategy)
7. [Timeline & Milestones](#timeline--milestones)

---

## Current State Analysis

### File Metrics

- **Size**: 900 lines (comparable to severance pre-refactor)
- **Functions**: 11 functions (6 assessment + 1 orchestrator + 2 I/O + 2 utility)
- **Dataclasses**: 13 (well-structured, keep as-is)
- **Type Coverage**: ~95% (excellent, maintain)
- **Test Coverage**: 0% ❌ (critical gap)
- **Input Validation**: 0% ❌ (critical gap)

### Strengths to Preserve

✅ Clean dataclass architecture (13 result classes)
✅ Strong type hinting throughout
✅ Modular assessment functions (6 impact types)
✅ Good domain expertise (noise, dust, vibration, traffic, business, visual)
✅ JSON I/O infrastructure
✅ CLI interface

### Critical Issues to Fix

❌ No unit tests (high risk for financial calculations)
❌ No input validation (crashes on malformed input)
❌ **20+ magic numbers** scattered in code
❌ Division by zero risks (5+ locations)
❌ No JSON schema
❌ Minimal error handling
❌ No logging/audit trail

### Code Quality Issues

⚠️ Magic numbers in assessment functions (thresholds, rates, costs)
⚠️ Hardcoded constants (should be configurable)
⚠️ Inconsistent default handling
⚠️ Limited calculation methodology documentation
⚠️ No sensitivity analysis capability

---

## Goals & Success Criteria

### Primary Goals

**1. Production Hardening**
- ✅ 90%+ unit test coverage
- ✅ 100% input validation with JSON schema
- ✅ Zero unhandled exceptions
- ✅ Comprehensive error messages

**2. Code Quality**
- ✅ All magic numbers centralized in configuration
- ✅ All division operations protected
- ✅ Consistent error handling patterns
- ✅ Logging throughout calculation pipeline

**3. Maintainability**
- ✅ Modular architecture (separate files for each impact type)
- ✅ Clear separation of concerns
- ✅ Comprehensive documentation
- ✅ Easy to extend (new impact types, property types)

**4. Professional Features**
- ✅ Automated validation script with auto-fix
- ✅ Sensitivity analysis capability
- ✅ Detailed calculation explanations
- ✅ Audit trail generation

### Success Criteria

| Metric | Current | Target | Verification |
|--------|---------|--------|--------------|
| **Test Coverage** | 0% | 90%+ | `pytest --cov` |
| **Input Validation** | None | 100% | JSON schema + tests |
| **Error Handling** | 10% | 95%+ | Code review + tests |
| **Magic Numbers** | 20+ | 0 | Grep for hardcoded floats |
| **Main File Size** | 900 lines | ~300 lines | wc -l |
| **Documentation** | Partial | Complete | README + docstrings |

---

## Proposed Architecture

### Modular Structure

```
injurious-affection-assessment/
├── injurious_affection_calculator.py   # Main orchestrator (~300 lines)
├── config/
│   ├── __init__.py
│   ├── constants.py                    # All magic numbers centralized
│   └── thresholds.py                   # Impact thresholds and criteria
├── impacts/
│   ├── __init__.py
│   ├── noise.py                        # Noise impact assessment (~150 lines)
│   ├── dust.py                         # Dust/air quality assessment (~100 lines)
│   ├── vibration.py                    # Vibration damage assessment (~100 lines)
│   ├── traffic.py                      # Traffic disruption assessment (~120 lines)
│   ├── business.py                     # Business loss assessment (~120 lines)
│   └── visual.py                       # Visual impairment assessment (~80 lines)
├── models/
│   ├── __init__.py
│   ├── property_data.py                # PropertyDetails, ConstructionActivity, NoiseEquipment
│   ├── market_parameters.py            # MarketParameters dataclass
│   └── impact_results.py               # All result dataclasses (6 types + summary)
├── utils/
│   ├── __init__.py
│   ├── calculations.py                 # Shared calculation utilities
│   └── acoustic.py                     # Noise attenuation calculations
├── tests/
│   ├── __init__.py
│   ├── test_noise_impacts.py           # 6 tests
│   ├── test_dust_impacts.py            # 4 tests
│   ├── test_vibration_impacts.py       # 4 tests
│   ├── test_traffic_impacts.py         # 5 tests
│   ├── test_business_impacts.py        # 5 tests
│   ├── test_visual_impacts.py          # 3 tests
│   ├── test_integration.py             # 5 end-to-end tests
│   └── fixtures/                       # Test data JSON files
│       ├── residential_construction.json
│       ├── commercial_traffic.json
│       ├── industrial_minimal.json
│       ├── severe_vibration.json
│       └── combined_impacts.json
├── injurious_affection_input_schema.json  # JSON Schema for validation
├── validate_injurious.py                  # Validation script with auto-fix
├── SCHEMA_DOCUMENTATION.md                # Schema reference
├── VALIDATOR_README.md                    # Validation guide
└── SKILL.md                               # Updated with calculator integration
```

### Data Flow

```
Input JSON
    ↓
Validation (schema + auto-fix)
    ↓
Parsing (models/property_data.py)
    ↓
Main Calculator (injurious_affection_calculator.py)
    ↓
Impact Modules (impacts/*)
    ├── noise.py
    ├── dust.py
    ├── vibration.py
    ├── traffic.py
    ├── business.py
    └── visual.py
    ↓
Results Assembly (models/impact_results.py)
    ↓
Output (JSON + CLI report)
```

---

## Implementation Phases

### Phase 1: Foundation (Day 1 - 5 hours)

**Goal**: Set up modular structure and centralize configuration

**Tasks**:

1.1. **Create Directory Structure**
```bash
mkdir -p config impacts models utils tests tests/fixtures
touch config/__init__.py impacts/__init__.py models/__init__.py utils/__init__.py tests/__init__.py
```

1.2. **Extract Configuration** (config/constants.py)
```python
"""Centralized calculation constants for injurious affection"""

from dataclasses import dataclass

@dataclass
class CalculationConstants:
    """All hardcoded values centralized here"""

    # =========================================================================
    # NOISE IMPACT THRESHOLDS (dBA)
    # =========================================================================
    RESIDENTIAL_MODERATE_THRESHOLD_DBA: float = 65.0
    RESIDENTIAL_SEVERE_THRESHOLD_DBA: float = 75.0
    COMMERCIAL_MODERATE_THRESHOLD_DBA: float = 70.0
    COMMERCIAL_SEVERE_THRESHOLD_DBA: float = 80.0
    INDUSTRIAL_THRESHOLD_DBA: float = 85.0
    DEFAULT_BACKGROUND_NOISE_DBA: float = 50.0

    # =========================================================================
    # RENT REDUCTION PERCENTAGES
    # =========================================================================
    RESIDENTIAL_MODERATE_RENT_REDUCTION_PCT: float = 0.075  # 7.5%
    RESIDENTIAL_SEVERE_RENT_REDUCTION_PCT: float = 0.20     # 20%
    COMMERCIAL_MODERATE_RENT_REDUCTION_PCT: float = 0.055   # 5.5%
    COMMERCIAL_SEVERE_RENT_REDUCTION_PCT: float = 0.125     # 12.5%

    # =========================================================================
    # DUST CLEANING COSTS
    # =========================================================================
    RESIDENTIAL_CLEANING_COST: float = 200.0      # Per event
    COMMERCIAL_CLEANING_COST: float = 1000.0      # Per event
    HIGH_IMPACT_CLEANING_FREQUENCY_WEEKS: int = 1    # Weekly
    MODERATE_IMPACT_CLEANING_FREQUENCY_WEEKS: int = 2  # Bi-weekly
    LOW_IMPACT_CLEANING_FREQUENCY_WEEKS: int = 4     # Monthly

    # =========================================================================
    # VIBRATION THRESHOLDS AND COSTS
    # =========================================================================
    COSMETIC_DAMAGE_THRESHOLD_MMS: float = 5.0    # Peak particle velocity
    STRUCTURAL_DAMAGE_THRESHOLD_MMS: float = 12.0  # Peak particle velocity
    COSMETIC_REPAIR_COST: float = 2500.0
    STRUCTURAL_REPAIR_MULTIPLIER: float = 10.0    # 10x cosmetic

    # =========================================================================
    # TRAFFIC / BUSINESS PARAMETERS
    # =========================================================================
    DEFAULT_SALES_CONVERSION_RATE: float = 0.02   # 2% of traffic
    DEFAULT_TRANSACTION_VALUE: float = 50.0
    DEFAULT_GROSS_MARGIN_PCT: float = 0.40        # 40%

    # =========================================================================
    # VISUAL IMPACT PARAMETERS
    # =========================================================================
    MINOR_VISUAL_IMPACT_PCT: float = 0.02         # 2%
    MODERATE_VISUAL_IMPACT_PCT: float = 0.05      # 5%
    SEVERE_VISUAL_IMPACT_PCT: float = 0.10        # 10%

    # =========================================================================
    # CAPITALIZATION AND TIME PARAMETERS
    # =========================================================================
    DEFAULT_CAP_RATE: float = 0.08                # 8%
    MONTHS_PER_YEAR: int = 12
    WEEKS_PER_YEAR: int = 52
    BUSINESS_DAYS_PER_YEAR: int = 250

    # =========================================================================
    # ACOUSTIC CALCULATIONS
    # =========================================================================
    NOISE_REFERENCE_DISTANCE_M: float = 15.0      # Reference measurement distance
    NOISE_ATTENUATION_DB_PER_DOUBLING: float = 6.0  # dB reduction per distance doubling

# Global instance
CONSTANTS = CalculationConstants()
```

1.3. **Extract Data Models** (models/property_data.py, models/impact_results.py)

1.4. **Create Shared Utilities** (utils/calculations.py, utils/acoustic.py)

**Deliverables**:
- ✅ Directory structure created
- ✅ config/constants.py with all magic numbers
- ✅ models/ with dataclasses
- ✅ utils/ with safe calculation utilities
- ✅ All files have proper imports and `__init__.py`

---

### Phase 2: Modularize Calculations (Day 1-2 - 7 hours)

**Goal**: Extract calculation functions into separate modules

**Tasks**:

2.1. **Create impacts/noise.py** (~150 lines)
```python
"""
Noise impact damage calculations

Calculates damages from construction noise including:
- Noise attenuation modeling (distance-based)
- Impact severity classification (moderate vs. severe)
- Rent reduction calculations (temporary loss)
"""

import logging
from models.property_data import PropertyDetails, ConstructionActivity
from models.market_parameters import MarketParameters
from models.impact_results import NoiseImpactResult
from config.constants import CONSTANTS
from utils.acoustic import calculate_noise_attenuation

logger = logging.getLogger(__name__)

def assess_noise_impact(...) -> NoiseImpactResult:
    """Calculate all noise-related damages"""
    # Implementation with logging and error handling
```

2.2. **Create impacts/dust.py** (~100 lines)
2.3. **Create impacts/vibration.py** (~100 lines)
2.4. **Create impacts/traffic.py** (~120 lines)
2.5. **Create impacts/business.py** (~120 lines)
2.6. **Create impacts/visual.py** (~80 lines)

2.7. **Update Main Calculator** (injurious_affection_calculator.py)
```python
"""Injurious Affection Calculator - Main Orchestrator (REFACTORED)"""

from impacts import (
    assess_noise_impact,
    assess_dust_impact,
    assess_vibration_impact,
    assess_traffic_impact,
    assess_business_loss,
    assess_visual_impact
)

def calculate_injurious_affection(...) -> InjuriousAffectionSummary:
    """Calculate complete injurious affection damages (MODULAR VERSION)"""

    # Calculate each impact type using modules
    noise_impact = assess_noise_impact(...)
    dust_impact = assess_dust_impact(...)
    vibration_impact = assess_vibration_impact(...)
    traffic_impact = assess_traffic_impact(...)
    business_loss = assess_business_loss(...)
    visual_impact = assess_visual_impact(...)

    # Assemble summary
    summary = InjuriousAffectionSummary(...)
    summary.calculate_totals()

    return summary
```

**Deliverables**:
- ✅ impacts/noise.py (150 lines)
- ✅ impacts/dust.py (100 lines)
- ✅ impacts/vibration.py (100 lines)
- ✅ impacts/traffic.py (120 lines)
- ✅ impacts/business.py (120 lines)
- ✅ impacts/visual.py (80 lines)
- ✅ Main calculator reduced to ~300 lines
- ✅ All modules use centralized constants
- ✅ All division operations protected
- ✅ Logging added throughout

---

### Phase 3: Testing Infrastructure (Day 2-3 - 8 hours)

**Goal**: Achieve 90%+ test coverage

**Test Fixtures**:

1. **residential_construction.json** - Residential property with severe noise/dust
2. **commercial_traffic.json** - Commercial with traffic disruption
3. **industrial_minimal.json** - Industrial with minimal impacts
4. **severe_vibration.json** - Vibration damage scenario
5. **combined_impacts.json** - Multiple impact types

**Test Coverage Target**:
```
impacts/noise.py       95% coverage
impacts/dust.py        92% coverage
impacts/vibration.py   90% coverage
impacts/traffic.py     93% coverage
impacts/business.py    92% coverage
impacts/visual.py      88% coverage
Overall:               90%+ coverage
```

**Deliverables**:
- ✅ 5 test fixture JSON files
- ✅ tests/test_noise_impacts.py (6 tests)
- ✅ tests/test_dust_impacts.py (4 tests)
- ✅ tests/test_vibration_impacts.py (4 tests)
- ✅ tests/test_traffic_impacts.py (5 tests)
- ✅ tests/test_business_impacts.py (5 tests)
- ✅ tests/test_visual_impacts.py (3 tests)
- ✅ tests/test_integration.py (5 end-to-end tests)
- ✅ pytest.ini configuration
- ✅ All tests passing

---

### Phase 4: Validation & Schema (Day 3 - 4 hours)

**Goal**: Add JSON schema and validation script with auto-fix

**JSON Schema**: `injurious_affection_input_schema.json`

Key validation rules:
- Property type enum validation
- Noise level ranges (dBA)
- Vibration thresholds (mm/s)
- Percentage validations (0-100%)
- Required vs. optional fields

**Validation Script**: `validate_injurious.py`

Auto-fix capabilities:
- Add default market parameters
- Set default background noise levels
- Add missing optional fields
- Convert string numbers to floats
- Validate equipment lists

**Deliverables**:
- ✅ injurious_affection_input_schema.json (JSON Schema Draft 2020-12)
- ✅ validate_injurious.py (validation script with auto-fix)
- ✅ SCHEMA_DOCUMENTATION.md (field reference)
- ✅ VALIDATOR_README.md (usage guide)

---

### Phase 5: Documentation & Integration (Day 3-4 - 3 hours)

**Goal**: Update all documentation and integrate with SKILL.md

**Updates**:
- SKILL.md: Add calculator usage section
- README.md: Update with v2.0.0 features
- Add calculator architecture diagram
- Document sample scenarios
- Create quick start guide

**Deliverables**:
- ✅ SKILL.md updated with calculator integration
- ✅ README.md updated with v2.0.0 features
- ✅ All documentation cross-referenced

---

### Phase 6: Final Testing & Polish (Day 4 - 3 hours)

**Goal**: End-to-end validation, performance testing, edge cases

**Tests**:
- Zero impact scenarios (no damages)
- Maximum impact scenarios (all damage types)
- Edge cases (zero distances, extreme noise levels)
- Backward compatibility (match original results)
- Performance benchmarks (<100ms per calculation)

**Deliverables**:
- ✅ 10 edge case tests passing
- ✅ Performance under 100ms
- ✅ Error messages user-friendly
- ✅ 100% backward compatibility

---

## File Structure (Final)

```
injurious-affection-assessment/
├── injurious_affection_calculator.py  # Main orchestrator (~300 lines) ✅ REFACTORED
├── config/
│   ├── __init__.py
│   ├── constants.py                   # Centralized magic numbers
│   └── thresholds.py                  # Impact thresholds
├── impacts/
│   ├── __init__.py
│   ├── noise.py                       # Noise assessment (150 lines)
│   ├── dust.py                        # Dust assessment (100 lines)
│   ├── vibration.py                   # Vibration assessment (100 lines)
│   ├── traffic.py                     # Traffic assessment (120 lines)
│   ├── business.py                    # Business loss (120 lines)
│   └── visual.py                      # Visual impact (80 lines)
├── models/
│   ├── __init__.py
│   ├── property_data.py               # Input data models
│   ├── market_parameters.py           # Market assumptions
│   └── impact_results.py              # Result dataclasses
├── utils/
│   ├── __init__.py
│   ├── calculations.py                # Shared math utilities
│   └── acoustic.py                    # Noise calculations
├── tests/
│   ├── __init__.py
│   ├── test_noise_impacts.py          # 6 tests
│   ├── test_dust_impacts.py           # 4 tests
│   ├── test_vibration_impacts.py      # 4 tests
│   ├── test_traffic_impacts.py        # 5 tests
│   ├── test_business_impacts.py       # 5 tests
│   ├── test_visual_impacts.py         # 3 tests
│   ├── test_integration.py            # 5 tests
│   └── fixtures/
│       ├── residential_construction.json
│       ├── commercial_traffic.json
│       ├── industrial_minimal.json
│       ├── severe_vibration.json
│       └── combined_impacts.json
├── injurious_affection_input_schema.json  # JSON Schema
├── validate_injurious.py                  # Validation script
├── SCHEMA_DOCUMENTATION.md                # Schema reference
├── VALIDATOR_README.md                    # Validation guide
├── REFACTORING_PLAN.md                    # This document
├── SKILL.md                               # Updated skill documentation
├── README.md                              # Project README
├── pytest.ini                             # Pytest configuration
├── .gitignore                             # Git ignore patterns
└── injurious_affection_calculator_original.py  # v1.0.0 backup

Total Files: 32+
Total Lines: ~2,200 (from 900 monolithic)
Test Coverage: 90%+
Magic Numbers: 0 (all centralized)
```

---

## Testing Strategy

### Test Categories

**Unit Tests** (27 tests)
- impacts/noise.py: 6 tests
- impacts/dust.py: 4 tests
- impacts/vibration.py: 4 tests
- impacts/traffic.py: 5 tests
- impacts/business.py: 5 tests
- impacts/visual.py: 3 tests

**Integration Tests** (5 tests)
- End-to-end JSON → calculation → output
- Each test fixture scenario

**Validation Tests** (5 tests)
- Schema validation
- Auto-fix functionality
- Error handling

**Performance Tests** (2 tests)
- Calculation speed
- Memory usage

**Edge Case Tests** (10 tests)
- Zero impact scenarios
- Extreme values
- Missing optional fields
- Division by zero protection

---

## Timeline & Milestones

### Week 1: Core Refactoring

**Day 1** (5-7 hours)
- ✅ Phase 1: Foundation (directory structure, config extraction)
- ✅ Phase 2: Modularization (extract impact modules)
- **Milestone**: Code compiles and runs

**Day 2-3** (10-12 hours)
- ✅ Phase 3: Testing Infrastructure (27 unit tests)
- ✅ Phase 4: Validation & Schema
- **Milestone**: 90% test coverage, schema validation working

**Day 4** (3-5 hours)
- ✅ Phase 5: Documentation & Integration
- **Milestone**: SKILL.md updated, README complete

**Day 4-5** (2-3 hours)
- ✅ Phase 6: Final Testing & Polish
- **Milestone**: Production ready

### Total Effort: 20-27 hours (2-4 days)

---

## Success Metrics

### Code Quality Metrics

| Metric | Before | Target | Verification |
|--------|--------|--------|--------------|
| **Test Coverage** | 0% | 90%+ | pytest --cov |
| **Magic Numbers** | 20+ | 0 | grep -r "\\b[0-9]\\+\\.[0-9]\\+\\b" |
| **Input Validation** | None | 100% | Schema + tests |
| **Error Handling** | 10% | 95%+ | Code review |
| **File Size (main)** | 900 lines | ~300 lines | wc -l |
| **Module Count** | 1 | 15+ | ls -R |
| **Documentation** | Partial | Complete | Review |

### Functional Metrics

- ✅ All original calculations produce same results (±$0.01)
- ✅ All sample files process successfully
- ✅ Validation script catches 100% of schema violations
- ✅ Auto-fix corrects 80%+ of common issues
- ✅ Performance < 100ms per calculation
- ✅ Zero unhandled exceptions

---

## Risk Mitigation

### Technical Risks

**Risk 1: Breaking Changes**
- **Mitigation**: Maintain backward compatibility
- **Test**: Run original samples, compare outputs
- **Rollback**: Keep original in git history

**Risk 2: Calculation Errors**
- **Mitigation**: Comprehensive unit tests
- **Test**: Verify against manual calculations
- **Validation**: Cross-check with original implementation

**Risk 3: Performance Degradation**
- **Mitigation**: Performance tests
- **Benchmark**: < 100ms per calculation
- **Optimization**: Profile if needed

---

## Conclusion

This refactoring plan transforms the injurious affection calculator from a functional script into a production-grade calculation engine with:

✅ **90%+ test coverage** (from 0%)
✅ **100% input validation** (from none)
✅ **Modular architecture** (6 impact modules)
✅ **Zero magic numbers** (all centralized)
✅ **Comprehensive documentation**
✅ **Professional features** (schema, validation, auto-fix)

**Timeline**: 2-4 days (20-27 hours)
**Risk**: Low (backward compatible)
**Value**: High (production hardening for financial calculations)

The refactoring follows proven patterns from the severance damages calculator refactoring (943 → 360 lines, 62% reduction) while addressing injurious affection-specific requirements.

---

**Document Version**: 1.0.0
**Date**: 2025-11-15
**Author**: Claude Code
**Status**: Ready for Implementation
**Pattern**: Based on successful severance-damages-quantification refactoring
