# Cleanup Plan: comparable-sales-adjustment-methodology Skill Directory

**Date:** 2025-12-17
**Status:** Proposed
**Author:** Claude Code

---

## Executive Summary

The `.claude/skills/comparable-sales-adjustment-methodology/` directory has grown beyond its intended scope. A skills directory should contain **only a SKILL.md file** (~12KB) describing domain expertise, but this directory contains a full calculator implementation (1.3MB) including Python modules, tests, sample data, and output directories.

---

## Current State Analysis

### Directory Size Comparison

| Directory | Expected Size | Actual Size | Issue |
|-----------|---------------|-------------|-------|
| `effective-rent-analyzer/` | ~12KB | 12KB | ✅ Correct (SKILL.md only) |
| `commercial-lease-expert/` | ~12KB | ~15KB | ✅ Correct (SKILL.md only) |
| `comparable-sales-adjustment-methodology/` | ~12KB | **1.3MB** | ❌ 108x oversized |

### Current Contents (58 files)

#### What Belongs (Keep in Skills)
| File | Size | Purpose |
|------|------|---------|
| `SKILL.md` | 23KB | Skill definition and instructions |

#### What Doesn't Belong (Move Out)

**Python Calculators (5,288 lines total):**
| File | Lines | Purpose |
|------|-------|---------|
| `comparable_sales_calculator.py` | 1,300 | Main comparable sales calculator |
| `paired_sales_analyzer.py` | 1,948 | Paired sales analysis tool |
| `validate_comparables.py` | 575 | Input validation utility |
| `test_comparable_sales_calculator.py` | 872 | Unit tests |
| `test_paired_sales_analyzer.py` | 593 | Unit tests |

**Adjustments Module (9 files, ~90KB):**
- `__init__.py`, `building_general.py`, `industrial_building.py`
- `land.py`, `office_building.py`, `parameter_mapping.py`
- `site.py`, `special_features.py`, `validation.py`, `zoning_legal.py`

**Data Files:**
| Category | Files | Purpose |
|----------|-------|---------|
| Sample Inputs | 8 JSON files | Test/example data |
| Schema | `comparable_sales_input_schema.json` | Input validation |
| Templates | `adjustment_factors_template.json` | Configuration |
| Documentation | `SCHEMA_DOCUMENTATION.md`, `VALIDATOR_README.md` | Technical docs |

**Generated/Cache (Delete):**
| Directory | Contents | Purpose |
|-----------|----------|---------|
| `__pycache__/` | 4 .pyc files | Python bytecode |
| `.pytest_cache/` | Cache files | Test cache |
| `inputs/` | 1 timestamped JSON | Test inputs |
| `results/` | 7 timestamped JSON | Test outputs |

---

## Solution: New `Comparable_Sales_Analysis/` Directory

Create a new top-level directory following the existing pattern (e.g., `Eff_Rent_Calculator/`, `Credit_Analysis/`):

```
Comparable_Sales_Analysis/
├── README.md                           # From VALIDATOR_README.md content
├── __init__.py                         # New
├── comparable_sales_calculator.py      # Main calculator
├── paired_sales_analyzer.py            # Paired sales tool
├── validate_comparables.py             # Validation utility
├── adjustments/                        # Adjustment modules
│   ├── __init__.py
│   ├── building_general.py
│   ├── industrial_building.py
│   ├── land.py
│   ├── office_building.py
│   ├── parameter_mapping.py
│   ├── site.py
│   ├── special_features.py
│   ├── validation.py
│   └── zoning_legal.py
├── schemas/                            # JSON schemas
│   ├── comparable_sales_input_schema.json
│   └── adjustment_factors_template.json
├── sample_inputs/                      # Sample data
│   ├── sample_industrial_comps.json
│   ├── sample_industrial_comps_ENHANCED.json
│   ├── sample_industrial_comps_tight.json
│   ├── sample_industrial_comps_unified.json
│   ├── sample_industrial_rail_yard.json
│   ├── sample_office_class_a.json
│   ├── sample_office_class_b.json
│   └── sample_office_class_c.json
├── tests/                              # Test suite
│   ├── test_comparable_sales_calculator.py
│   └── test_paired_sales_analyzer.py
└── docs/                               # Documentation
    └── SCHEMA_DOCUMENTATION.md
```

### Rationale

1. **Different methodologies:** MCDA uses ordinal ranking; this uses dollar adjustments
2. **Different use cases:** MCDA for heterogeneous sets; traditional DCA for standard appraisals
3. **Clearer naming:** Users searching for "comparable sales" find the right tool
4. **Follows existing patterns:** Matches `Credit_Analysis/`, `Renewal_Analysis/`, etc.

---

## Implementation Steps

### Phase 1: Create New Directory Structure

```bash
# 1. Create new top-level directory
mkdir -p /workspaces/lease-abstract/Comparable_Sales_Analysis/{adjustments,schemas,sample_inputs,tests,docs}

# 2. Create __init__.py
echo '"""Comparable Sales Analysis Calculator - Traditional DCA with dollar adjustments."""' > /workspaces/lease-abstract/Comparable_Sales_Analysis/__init__.py
```

### Phase 2: Move Files

```bash
# Source directory shorthand
SRC=/workspaces/lease-abstract/.claude/skills/comparable-sales-adjustment-methodology
DEST=/workspaces/lease-abstract/Comparable_Sales_Analysis

# Move Python files
mv $SRC/comparable_sales_calculator.py $DEST/
mv $SRC/paired_sales_analyzer.py $DEST/
mv $SRC/validate_comparables.py $DEST/

# Move adjustments module
mv $SRC/adjustments/*.py $DEST/adjustments/

# Move schemas
mv $SRC/comparable_sales_input_schema.json $DEST/schemas/
mv $SRC/adjustment_factors_template.json $DEST/schemas/

# Move sample inputs
mv $SRC/sample_*.json $DEST/sample_inputs/

# Move tests
mv $SRC/test_*.py $DEST/tests/

# Move documentation
mv $SRC/SCHEMA_DOCUMENTATION.md $DEST/docs/
mv $SRC/VALIDATOR_README.md $DEST/README.md
```

### Phase 3: Clean Up Caches

```bash
# Delete generated/cache directories
rm -rf $SRC/__pycache__
rm -rf $SRC/.pytest_cache
rm -rf $SRC/adjustments/__pycache__
rm -rf $SRC/inputs
rm -rf $SRC/results
```

### Phase 4: Update SKILL.md References

Update the SKILL.md file to reference the new location:

**Before:**
```markdown
**File**: `comparable_sales_calculator.py` (located in same folder as this SKILL.md)
```

**After:**
```markdown
**File**: `/workspaces/lease-abstract/Comparable_Sales_Analysis/comparable_sales_calculator.py`

### Usage

**Command-line**:
```bash
cd /workspaces/lease-abstract/Comparable_Sales_Analysis/
python comparable_sales_calculator.py input.json --output results.json --verbose
```
```

### Phase 5: Update CLAUDE.md

Add the new directory to the repository structure:

```markdown
├── Comparable_Sales_Analysis/  # Traditional DCA comparable sales (dollar adjustments)
```

### Phase 6: Verify

```bash
# Run tests from new location
cd /workspaces/lease-abstract/Comparable_Sales_Analysis
pytest tests/ -v

# Verify skill directory is clean
ls -la /workspaces/lease-abstract/.claude/skills/comparable-sales-adjustment-methodology/
# Should only show: SKILL.md
```

---

## Files to Delete (Not Move)

These are generated files that will be recreated:

| File/Directory | Reason |
|----------------|--------|
| `__pycache__/` | Python bytecode (auto-generated) |
| `.pytest_cache/` | Pytest cache (auto-generated) |
| `adjustments/__pycache__/` | Python bytecode (auto-generated) |
| `inputs/*.json` | Timestamped test inputs (transient) |
| `results/*.json` | Timestamped test outputs (transient) |

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Broken imports | Update any import statements referencing old path |
| Slash command failures | Update `/Valuation/comparable-sales-analysis.md` if it exists |
| Test failures | Run full test suite after migration |
| Documentation drift | Update SKILL.md with new paths |

---

## Validation Checklist

After implementation:

- [ ] New `Comparable_Sales_Analysis/` directory exists with all files
- [ ] `pytest Comparable_Sales_Analysis/tests/ -v` passes
- [ ] Calculator runs: `python Comparable_Sales_Analysis/comparable_sales_calculator.py --help`
- [ ] Skills directory contains only `SKILL.md`
- [ ] `SKILL.md` references correct paths
- [ ] `CLAUDE.md` updated with new directory
- [ ] Git status shows clean moves (not delete + add)

---

## Summary

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Skill directory size | 1.3MB | ~25KB | -98% |
| Files in skill dir | 58 | 1 | -98% |
| Calculator accessible | ✅ | ✅ | Preserved |
| Follows conventions | ❌ | ✅ | Fixed |
| Tests runnable | ✅ | ✅ | Preserved |
