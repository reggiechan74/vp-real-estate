# Relative Valuation Field Enhancement Analysis

**Date**: 2025-11-05
**Branch**: feature/enhance-valuation-variables
**Analyst**: Commercial Real Estate Leasing Expert

---

## EXECUTIVE SUMMARY

After analyzing the Mississauga industrial MLS dataset (23 properties), we've identified **8 high-impact fields** consistently available in MLS reports that should be added to the relative valuation model to improve competitive positioning accuracy.

**Current Variables**: 15 (9 core + 6 optional)
**Proposed Total**: 23 (9 core + 14 optional)
**New Variables**: 8

---

## CURRENT STATE

### Currently Tracked (15 variables)

**Core Variables (9):**
1. Net Asking Rent ($/SF) - 16% weight
2. Parking Ratio (spaces/1,000 SF) - 15% weight
3. TMI ($/SF) - 14% weight
4. Clear Height (ft) - 8% weight
5. % Office Space - 8% weight
6. Distance (km) - 8% weight
7. Area Difference (SF) - 8% weight
8. Year Built - 6% weight
9. Class (A/B/C) - 5% weight

**Optional Variables (6):**
10. Shipping Doors - Truck Level (TL) - 4% weight
11. Shipping Doors - Drive-In (DI) - 3% weight
12. Power (Amps) - 3% weight
13. Trailer Parking (Y/N) - 2% weight
14. Secure Shipping (Y/N) - 0% weight (no data)
15. Excess Land (Y/N) - 0% weight (no data)

---

## RECOMMENDED ADDITIONS

### HIGH PRIORITY (Add Immediately)

#### 1. **Bay Depth (ft)** - CRITICAL
**MLS Field**: `Bay Size` (e.g., "55 x 52" → 55 ft)
**Extraction**: Parse first number from "Bay Size" field
**Sample Values**: 40 ft, 44 ft, 52 ft, 55 ft, 56 ft
**Proposed Weight**: 5%

**Rationale**:
- Directly impacts racking efficiency and storage density
- Deeper bays (52'+ ) accommodate double-deep pallet racking
- Standard 53' trailers require 54'+ bays for efficient unloading
- Critical for 3PL and distribution users
- More predictive of operational efficiency than % office space

**Ranking**: Descending (deeper is better)

---

#### 2. **Lot Size (Acres)** - HIGH IMPACT
**MLS Field**: `Lot Irreg` or `Lot Size Area`
**Sample Values**: 4.95 acres, 6 acres, 11.112 acres, 37.6 acres
**Proposed Weight**: 4%

**Rationale**:
- Expansion potential - critical for growing tenants
- Outdoor storage capability for materials, trailers, equipment
- Future development rights (additional buildings, expansions)
- Bargaining power in negotiations (more flexibility = higher value)
- Differentiates otherwise identical buildings

**Ranking**: Descending (larger lots better)

---

#### 3. **HVAC Coverage** - IMPORTANT
**MLS Field**: `A/C` (Y/Part/N)
**Sample Values**: Y (full), Part (partial), N (none)
**Proposed Weight**: 3%
**Data Type**: Ordinal (Y=1, Part=2, N=3)

**Rationale**:
- Worker comfort = productivity and retention
- Some products require climate control (electronics, food, pharma)
- Insurance requirements for certain goods
- Increasingly important in hot summers
- Partial A/C (office only) vs full building is major differentiator

**Ranking**: Ascending (Y=1 ranks best, N=3 ranks worst)

---

#### 4. **Sprinkler Type** - INSURANCE IMPACT
**MLS Field**: `Sprinklers` + `Client Remks` (ESFR notation)
**Sample Values**:
- ESFR (Early Suppression Fast Response) = 1
- Standard (Y) = 2
- None (N) = 3

**Proposed Weight**: 3%

**Rationale**:
- ESFR allows 40'+ clear heights and high-piled storage
- 20-30% insurance premium reduction with ESFR
- Commodity storage requirements (Class I-IV)
- Fire marshal approval for certain uses
- Mentioned prominently in marketing materials (795 Hazelhurst, 587 Avonhead)

**Ranking**: Ascending (ESFR=1 best, None=3 worst)

---

#### 5. **Building Age (Years)** - CONDITION PROXY
**MLS Field**: Calculated from `Year Built`
**Calculation**: `2025 - Year Built`
**Sample Values**: 0 years (new), 5 years, 15 years, 25 years
**Proposed Weight**: 4%

**Rationale**:
- More intuitive than "Year Built" for tenants
- Directly correlates with:
  - Deferred maintenance costs
  - Energy efficiency (newer = better insulation, LED lighting)
  - Layout efficiency (modern vs legacy floorplans)
  - Technology infrastructure (fiber, EV charging)
- Replace "Year Built" in rankings

**Ranking**: Ascending (newer = lower age = better)

---

#### 6. **Rail Access** - NICHE BUT CRITICAL
**MLS Field**: `Rail` (Y/N)
**Sample Values**: Y (rail siding), N (no rail)
**Proposed Weight**: 2%

**Rationale**:
- Deal-breaker for certain industries (bulk commodities, automotive, manufacturing)
- Very rare in modern industrial (only ~2% of buildings)
- Commands premium rent when required
- Zero value for non-rail users, but absolute requirement for rail users
- Binary: you either have it or you don't

**Ranking**: Descending (Y=1, N=0)

---

#### 7. **Crane Capability** - MANUFACTURING ESSENTIAL
**MLS Field**: `Crane` (Y/N)
**Sample Values**: Y (overhead crane), N (no crane)
**Proposed Weight**: 2%

**Rationale**:
- Essential for heavy manufacturing and assembly
- Expensive retrofit (~$50K-200K+ depending on capacity)
- Limits tenant pool but commands premium for those who need it
- Structural requirement (building must be designed for loads)
- Common in older industrial, rare in new distribution buildings

**Ranking**: Descending (Y=1, N=0)

---

#### 8. **Occupancy Status** - IMMEDIATE AVAILABILITY
**MLS Field**: `Occup` (Vacant/Tenant)
**Sample Values**: Vacant, Tenant
**Proposed Weight**: 2%
**Data Type**: Binary (Vacant=1, Tenant=2)

**Rationale**:
- Vacant = immediate occupancy (30-60 days)
- Tenant-occupied = 6-12 month delay until possession
- Time value of money - lost revenue during waiting period
- Tenant may not vacate (deal risk)
- Critical for time-sensitive relocations

**Ranking**: Ascending (Vacant=1 better than Tenant=2)

---

## MEDIUM PRIORITY (Consider for Phase 2)

#### 9. **Grade Level Doors**
**Field**: `Grade Level`
**Weight**: 2%
**Rationale**: Courier vans, small trucks, less critical than TL doors

#### 10. **Days on Market (DOM)**
**Field**: `DOM`
**Weight**: 2%
**Rationale**: Landlord motivation indicator, negotiation leverage

#### 11. **Zoning Classification**
**Field**: `Zoning`
**Weight**: 2%
**Rationale**: Permitted use restrictions, but usually pre-screened

---

## REVISED WEIGHTING SCHEME

### Option A: Add 8 new variables, redistribute weights

| Variable | Current | Proposed | Change |
|----------|---------|----------|--------|
| **CORE VARIABLES (9)** | | | |
| Net Asking Rent | 16% | 11% | -5% |
| Parking Ratio | 15% | 10% | -5% |
| TMI | 14% | 9% | -5% |
| Clear Height | 8% | 7% | -1% |
| % Office Space | 8% | 7% | -1% |
| Distance | 8% | 7% | -1% |
| Area Difference | 8% | 7% | -1% |
| Building Age (was Year Built) | 6% | 4% | -2% |
| Class | 5% | 5% | 0% |
| **OPTIONAL - EXISTING (6)** | | | |
| Shipping Doors (TL) | 4% | 4% | 0% |
| Shipping Doors (DI) | 3% | 3% | 0% |
| Power (Amps) | 3% | 3% | 0% |
| Trailer Parking | 2% | 2% | 0% |
| Secure Shipping | 0% | 0% | 0% |
| Excess Land | 0% | 0% | 0% |
| **OPTIONAL - NEW (8)** | | | |
| Bay Depth | - | 5% | +5% |
| Lot Size (Acres) | - | 4% | +4% |
| HVAC Coverage | - | 3% | +3% |
| Sprinkler Type | - | 3% | +3% |
| Rail Access | - | 2% | +2% |
| Crane | - | 2% | +2% |
| Occupancy Status | - | 2% | +2% |
| Grade Level Doors | - | 0% | +0% (Phase 2) |
| **TOTAL** | **100%** | **100%** | |

**Allocation check**: Core variables move from 88% → 67% (−21%), existing optional fields remain at 12%, and the seven new optional fields receive the reallocated 21%. Building Age replaces Year Built within the core bucket, so its 6% → 4% adjustment is already included in the core reduction. Totals reconcile to 100%.

---

## EXTRACTION REQUIREMENTS

### New JSON Schema Fields

```json
{
  "bay_depth_ft": 55.0,           // Parse from "Bay Size" (55 x 52 → 55)
  "lot_size_acres": 11.112,       // From "Lot Irreg" or "Lot Size Area"
  "hvac_coverage": 1,             // Y=1, Part=2, N=3 (ordinal)
  "sprinkler_type": 1,            // ESFR=1, Standard=2, None=3 (ordinal)
  "building_age_years": 5,        // Calculated: 2025 - year_built
  "rail_access": false,           // Boolean
  "crane": false,                 // Boolean
  "occupancy_status": 1,          // Vacant=1, Tenant=2 (ordinal)
  "grade_level_doors": 0,         // Integer (Phase 2)
  "days_on_market": 119           // Integer (Phase 2)
}
```

### Extraction Logic

#### Bay Depth
```python
# requires: import re
bay_size = (property.get('Bay Size') or '').replace('×', 'x')  # supports "55 X 52" / "55x52"
match = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*[xX]', bay_size)
if match:
    bay_depth_ft = float(match.group(1))
```

#### Lot Size
```python
# requires: import re

def parse_lot_size(raw: str) -> float | None:
    if not raw:
        return None
    cleaned = raw.replace(',', '').strip().lower()
    match = re.match(r'([0-9]+(?:\.[0-9]+)?)', cleaned)
    if not match:
        return None
    value = float(match.group(1))
    if 'sq ft' in cleaned or 'sqft' in cleaned:
        return value / 43560  # convert square feet to acres
    if 'acre' in cleaned:
        return value
    return None

lot_irreg = property.get('Lot Irreg', '')  # e.g., "11.112 acres" or "484,280 Sq Ft"
lot_size_area = property.get('Lot Size Area', '')  # e.g., "6 Acres"

lot_size_acres = parse_lot_size(lot_irreg) or parse_lot_size(lot_size_area)
```

#### HVAC Coverage
```python
ac = property.get('A/C', 'N')
hvac_coverage = {'Y': 1, 'Part': 2, 'N': 3}.get(ac, 3)
```

#### Sprinkler Type
```python
sprinklers = property.get('Sprinklers', 'N')
client_remarks = property.get('Client Remks', '')

if 'ESFR' in client_remarks or 'esfr' in client_remarks.lower():
    sprinkler_type = 1  # ESFR
elif sprinklers == 'Y':
    sprinkler_type = 2  # Standard
else:
    sprinkler_type = 3  # None
```

#### Building Age
```python
analysis_year = 2025  # align with report date or pass in analysis metadata
year_built_raw = property.get('year_built')
if year_built_raw is not None and str(year_built_raw).strip():
    building_age_years = analysis_year - int(str(year_built_raw).strip())
else:
    building_age_years = None
```

Always prefer sourcing `analysis_year` from the comparable file's `analysis_date` field so results remain consistent regardless of when the code runs.

---

## IMPACT ANALYSIS

### Expected Ranking Changes

Based on the Mississauga dataset, adding these 8 variables will likely:

1. **Improve rank** for properties with:
   - ESFR sprinklers (795 Hazelhurst, 587 Avonhead, 560 Slate)
   - Deep bays 54'+ (795 Hazelhurst 55', 745 Hazelhurst 55', 6525 Mississauga 56')
   - Large lots 10+ acres (587 Avonhead 37.6 acres)
   - Full A/C (795 Hazelhurst, 745 Hazelhurst, 6525 Mississauga)
   - Vacant status (immediate occupancy)

2. **Hurt rank** for properties with:
   - Shallow bays <45' (520 Abilene, 6975 Pacific)
   - Small lots <5 acres (520 Abilene 4.95 acres)
   - No A/C or Part A/C
   - Tenant-occupied (delayed possession)
   - Older buildings 15+ years (6975 Pacific 16-30 years)

3. **Subject Property (2550 Stanfield Rd Opt 2)** impact:
   - Currently ranks #3 of 23
   - Bay depth not specified in listing → need to research
   - Lot size not specified → multi-tenant building, shared lot
   - A/C: Part → moderate score
   - Sprinklers: Y (not ESFR) → moderate score
   - Building Age: 5 years (2020) → excellent
   - Occupancy: Vacant → excellent
   - **Net impact**: Likely maintain or slightly improve #3 ranking

---

## RECOMMENDATIONS

### Phase 1: Immediate (This Branch)
1. ✅ Add 8 new optional variables to schema
2. ✅ Update extraction logic to parse new fields
3. ✅ Revise weighting algorithm with proposed distribution
4. ✅ Re-run Mississauga analysis with enhanced model
5. ✅ Compare old vs new rankings to validate model

### Phase 2: Future Enhancement
6. Add Days on Market (DOM) - landlord motivation
7. Add Grade Level Doors - alternative shipping
8. Add Zoning classification - use restrictions
9. Create tenant persona weights (3PL vs Manufacturing vs Office)
10. Add "must-have" filters (e.g., Rail=Y for certain users)

---

## VALIDATION PLAN

### Test Cases

**Test 1**: Properties with ESFR sprinklers should rank higher
- 795 Hazelhurst, 587 Avonhead, 560 Slate should improve

**Test 2**: Properties with deep bays (55'+) should rank higher
- 795 Hazelhurst (55' bays) should improve vs 520 Abilene (unknown bays)

**Test 3**: New construction should rank higher than 15+ year old
- 2550 Stanfield (2020) should rank higher than 6975 Pacific (16-30 years old)

**Test 4**: Vacant should rank higher than Tenant-occupied
- All else equal, vacant properties receive 2% of the total weighting via the Occupancy Status variable

---

## NEXT STEPS

1. Review and approve field additions
2. Update JSON schema in Python calculator
3. Update extraction logic in slash command
4. Re-extract Mississauga dataset with new fields
5. Re-run analysis and compare rankings
6. Generate comparison report (old vs new model)
7. Update documentation

---

**END OF ANALYSIS**
