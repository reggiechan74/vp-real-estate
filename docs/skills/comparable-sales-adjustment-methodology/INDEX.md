# Comparable Sales Adjustment Methodology - Documentation

**Skill Location**: `/.claude/skills/comparable-sales-adjustment-methodology/`
**Last Updated**: 2025-11-15

---

## Documentation Overview

This folder contains development documentation and enhancement history for the comparable sales adjustment methodology skill. These files are **not required** for the skill to function - they serve as reference and development documentation.

---

## Files in This Folder

### Usage & Getting Started
- **[README.md](README.md)** - Usage instructions, CLI examples, and quick start guide

### Development & Enhancement Documentation
- **[INTEGRATION_STATUS.md](INTEGRATION_STATUS.md)** - Current integration status (all 49 adjustments integrated)
- **[ENHANCEMENT_SUMMARY.md](ENHANCEMENT_SUMMARY.md)** - Complete enhancement task summary (Nov 15, 2025)
- **[ADJUSTMENT_ANALYSIS.md](ADJUSTMENT_ANALYSIS.md)** - Comprehensive analysis of all 49 adjustment categories

### Compliance Documentation
- **[CUSPAP_USPAP_COMPLIANCE.md](CUSPAP_USPAP_COMPLIANCE.md)** - Full USPAP 2024 & CUSPAP 2024 compliance report (850+ lines)

---

## Active Skill Files

The following files remain in the skill folder (`/.claude/skills/comparable-sales-adjustment-methodology/`) and are actively used:

### Core Skill Files
- **`SKILL.md`** - Skill definition and methodology (loaded by Claude Code)
- **`comparable_sales_calculator.py`** - Main calculator engine (2,023 lines, 49 adjustments)

### Sample Input Templates
- **`sample_industrial_comps.json`** - Original format (backward compatible)
- **`sample_industrial_comps_ENHANCED.json`** - Enhanced format with all 49 adjustment fields

---

## Quick Reference

### What Was Built
- ✅ Complete 49-adjustment comparable sales calculator
- ✅ USPAP 2024 & CUSPAP 2024 compliant
- ✅ Property-type specific logic (industrial vs office)
- ✅ Sequential 6-stage adjustment hierarchy
- ✅ Statistical validation and weighting

### Key Features
- **Land Characteristics** (8): Lot size, shape, topography, utilities, drainage, flood, environmental, soil
- **Site Improvements** (6): Paving, fencing, lighting, landscaping, stormwater, yard
- **Industrial Building** (10): Clear height, loading docks, column spacing, floor load, ESFR, etc.
- **Office Building** (8): Floor plate efficiency, parking, building class, ceiling height, elevators, etc.
- **Building General** (6): Age, construction quality, functional utility, energy efficiency, HVAC, etc.
- **Special Features** (6): Rail spur, crane systems, heavy power, truck scales, specialized HVAC, generator
- **Zoning/Legal** (5): Zoning, FAR, variance, non-conforming use, lot coverage

### Usage
```bash
# From skill folder
cd /.claude/skills/comparable-sales-adjustment-methodology/

# Run calculator
python comparable_sales_calculator.py sample_industrial_comps_ENHANCED.json --output results.json --verbose
```

---

## Document History

| Date | File | Purpose |
|------|------|---------|
| 2025-11-15 | README.md | Original usage documentation |
| 2025-11-15 | ADJUSTMENT_ANALYSIS.md | Research and analysis of all 49 adjustments |
| 2025-11-15 | CUSPAP_USPAP_COMPLIANCE.md | Compliance verification report |
| 2025-11-15 | ENHANCEMENT_SUMMARY.md | Task completion summary |
| 2025-11-15 | INTEGRATION_STATUS.md | Integration status tracking |
| 2025-11-15 | INDEX.md | This file |

---

## For Developers

If you're enhancing this skill:
1. Read `ADJUSTMENT_ANALYSIS.md` for methodology details
2. Check `INTEGRATION_STATUS.md` for current implementation status
3. Review `CUSPAP_USPAP_COMPLIANCE.md` for compliance requirements
4. Reference `ENHANCEMENT_SUMMARY.md` for development history
5. Use `README.md` for usage examples

---

## Contact

**Skill Type**: Appraisal/Valuation
**Complexity**: Advanced
**Status**: Production-Ready
**Compliance**: USPAP 2024, CUSPAP 2024, IVS
