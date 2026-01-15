# Accuracy Review: Location Overview Report

**Report Reviewed:** `2026-01-15_172500_location_overview_narrative_321_humberline_drive.md`

**Review Date:** January 15, 2026

**Reviewer:** Quality Control

---

## Verification Summary

| Category | Items Checked | Verified ✓ | Discrepancies ⚠️ | Errors ❌ |
|----------|---------------|------------|------------------|----------|
| Property Identification | 12 | 11 | 1 | 0 |
| Building Specifications | 9 | 7 | 2 | 0 |
| Title/Ownership | 8 | 8 | 0 | 0 |
| Valuation Data | 12 | 12 | 0 | 0 |
| Site Inspection | 6 | 5 | 1 | 0 |
| **TOTAL** | **47** | **43** | **4** | **0** |

**Overall Accuracy Score: 91.5%** (43/47 fully verified)

---

## Section-by-Section Verification

### 1. Property Identification

| Claim | Source | Status |
|-------|--------|--------|
| Address: 321 Humberline Drive, Etobicoke | Property_name.md, GeoWarehouse | ✓ Verified |
| PIN: 073670027 | GeoWarehouse p.2 | ✓ Verified |
| Roll Number: 1919044460003000000 | MPAC Report | ✓ Verified |
| Legal Description: PT LT 37 CON 3... | GeoWarehouse p.2 | ✓ Verified |
| Coordinates: 43.7416°N, 79.6197°W | API Module output | ✓ Verified |
| Ward 01 (Etobicoke North) | API Module output | ✓ Verified |
| LRO: Metropolitan Toronto (80) | GeoWarehouse p.2 | ✓ Verified |
| Registration Type: Certified (Land Titles) | GeoWarehouse p.2 | ✓ Verified |
| Owner: CAD-TEK Holdings Inc. | GeoWarehouse p.2 | ✓ Verified |
| Name change: June 2005 | Folder Review (AT821206) | ✓ Verified |
| Purchase: Jan 2001 for $1,250,000 | GeoWarehouse p.3 | ✓ Verified |
| **Postal Code: M9W 5T6** | GeoWarehouse p.2 shows M9W5T6; API shows M9W 0A6 | ⚠️ Minor discrepancy |

**Notes:** The postal code discrepancy (M9W 5T6 vs M9W 0A6) is minor - both are valid for the area. GeoWarehouse (2019) used in report.

---

### 2. Building Specifications

| Claim | Source | Status |
|-------|--------|--------|
| Building Area: 27,334 SF | MPAC (25,030 + 2,304 = 27,334), Avison Young | ✓ Verified |
| Lot Size: 1.70 acres | MPAC, GeoWarehouse | ✓ Verified |
| Lot Size: 74,658 SF | GeoWarehouse p.3 (74,658.41 sq.ft) | ✓ Verified |
| Year Built: 1978 | MPAC | ✓ Verified |
| Frontage: 186.66 ft | MPAC, GeoWarehouse | ✓ Verified |
| Office Component: ~10% | Image_Index (Avison Young) | ✓ Verified |
| Loading: 3 truck-level + 1 drive-in | Image_Index (Avison Young) | ✓ Verified |
| **Clear Height: 18-20 ft** | MPAC shows 20 ft; Avison Young shows 18 ft | ⚠️ Discrepancy |
| **Zoning: IC2** | See detailed analysis below | ⚠️ **REQUIRES CORRECTION** |

#### Clear Height Discrepancy Analysis:
- **MPAC Report:** Shows main building at 20 ft clear height
- **Avison Young (per Image_Index):** States "Clear Height: 18'"
- **Report states:** "18-20 ft" and "Warehouse Clear Height: 18-20 ft"

**Assessment:** The report's range of "18-20 ft" is a reasonable reconciliation, but the Avison Young report (being a formal valuation from the effective date) should take precedence. **Recommend changing to "18 ft" as primary specification.**

#### Zoning Discrepancy Analysis - **CRITICAL**:

| Source | Zoning Stated |
|--------|---------------|
| Image_Index (Avison Young photos, line 44) | "E1 zoning" |
| Folder Review (line 59) | "IC2" |
| MPAC Report | Not specified |
| Report states | "IC2 under the former City of Etobicoke Zoning Code" |

**Analysis:**
- **E1** is from City-wide Zoning By-law 569-2013 (harmonized zoning)
- **IC2** is from former Etobicoke Zoning Code Chapter 304 (legacy zoning)

The Avison Young valuation report (dated around February 2020) states E1 zoning. This suggests the property may have been harmonized into the City-wide by-law. The Folder Review's "IC2" notation appears to be an error - it was listed under "Key Property Data from MPAC" but MPAC reports don't actually show zoning.

**Recommendation:** Verify current zoning status with City of Toronto. The report should either:
1. State "E1 (Employment Industrial) under City-wide Zoning By-law 569-2013" per Avison Young, OR
2. Acknowledge both designations: "E1 under City-wide By-law 569-2013 (or IC2 under legacy Etobicoke Code if not harmonized)"

---

### 3. Title & Ownership

| Claim | Source | Status |
|-------|--------|--------|
| Easement EB387062 | GeoWarehouse p.2, Folder Review | ✓ Verified |
| Registered August 13, 1971 | Folder Review | ✓ Verified |
| Grantor: Kagera Holdings Limited | Folder Review | ✓ Verified |
| Grantee: Canadian National Railway | Folder Review | ✓ Verified |
| Consideration: $2.00 | Folder Review | ✓ Verified |
| Easement area: ~1.008 acres | Folder Review | ✓ Verified |
| RBC Charge: $4,194,000 (Dec 2017) | Folder Review (AT4764856) | ✓ Verified |
| Previous owner: St. Lawrence Chemical | GeoWarehouse p.3 | ✓ Verified |

---

### 4. Valuation Data (from Avison Young photos)

| Claim | Image_Index Reference | Status |
|-------|----------------------|--------|
| Opinion of Value: $6,833,500-$6,970,170 | Line 43, 159 | ✓ Verified |
| PSF Range: $250-$255 | Line 43, 159 | ✓ Verified |
| Recommended Listing: $7,100,000 ($260 psf) | Line 43, 166 | ✓ Verified |
| Expected Sale: $6,900,000 ($253 psf) | Line 43, 166 | ✓ Verified |
| Replacement Cost: $6,067,761 ($222 psf) | Line 43, 163 | ✓ Verified |
| Comparable avg: $230 PSF | Line 164 | ✓ Verified |
| Comparable range: $191-$260 PSF | Line 164 | ✓ Verified |
| 255 Carrier Drive: 30,571 SF @ $191 | Line 167 | ✓ Verified |
| 380 Orenda Road: 25,704 SF @ $243 | Line 167 | ✓ Verified |
| 55 Brydon Drive: 17,080 SF @ $228 | Line 167 | ✓ Verified |
| Oxford Street: 22,000 SF @ $260 | Line 167 | ✓ Verified |
| Land Value: $2.1M-$2.3M/acre | Line 163 | ✓ Verified |

---

### 5. Site Inspection Data

| Claim | Image_Index Reference | Status |
|-------|----------------------|--------|
| Inspection Date: January 28, 2020 | Line 4 | ✓ Verified |
| Time Range: 14:52 - 16:05 | Line 12 | ✓ Verified |
| Weather: Overcast, winter, patchy snow | Line 5 | ✓ Verified |
| Tenant: CAD-TEK Holdings Inc. | Line 14 | ✓ Verified |
| Equipment: DANLY 250-ton, Bliss, YSD, TAKUMI V22A | Lines 289-296 | ✓ Verified |
| **Photo Count: 135 photographs + 1 video** | Header says 135; body says 122/123 | ⚠️ Source inconsistency |

**Photo Count Analysis:**
The Image_Index has internal inconsistencies:
- Line 6: "Total Files: 135 photographs + 1 video (MOV)"
- Line 66-67: Summary table shows "Total: 123"
- Line 12: "122 usable photographs"

The report uses "135 photographs and 1 video file" from the Image_Index header. This is acceptable given the source's own inconsistency, but could note "approximately 135 photos" to acknowledge uncertainty.

---

### 6. Neighbour Directions

| Direction | Report States | Image_Index (line 307) | Status |
|-----------|---------------|------------------------|--------|
| North | 315 Humberline (EFI/Prodigy) | 315 Humberline | ✓ Matches source |
| South | Batch plant | Industrial (batch plant) | ✓ Matches source |
| West | Modern warehouse (2018-2019) | Modern Warehouse | ✓ Matches source |
| East | KPMG/Polyair office campus | KPMG/Polyair | ✓ Matches source |

**Note:** While 315 being "north" of 321 seems counterintuitive for street numbering, the site inspection documentation explicitly states this configuration. Verified as matching source.

---

## Corrections Required

### 1. Zoning (HIGH PRIORITY)

**Current text (line 59):**
> "The subject property is zoned IC2 under the former City of Etobicoke Zoning Code (Chapter 304)"

**Recommended correction:**
> "The subject property is zoned E1 (Employment Industrial) under City-wide Zoning By-law 569-2013, as confirmed by the 2020 Avison Young valuation. The property may alternatively be referenced as IC2 under the legacy Etobicoke Zoning Code Chapter 304 for properties not yet harmonized into the City-wide by-law. Verification with the City of Toronto Planning Department is recommended."

### 2. Clear Height (MEDIUM PRIORITY)

**Current text (line 109):**
> "Warehouse Clear Height: 18-20 ft"

**Recommended correction:**
> "Warehouse Clear Height: 18 ft (per Avison Young valuation)"

**Rationale:** The Avison Young report from the effective date states 18 ft. MPAC shows 20 ft but MPAC measurements can differ from functional clear heights. Use the valuation report figure.

### 3. Photo Count (LOW PRIORITY - OPTIONAL)

**Current text (line 192):**
> "producing 135 photographs and 1 video file"

**Recommended correction:**
> "producing approximately 135 photographs and 1 video file (122 usable images per detailed analysis)"

---

## Items NOT Requiring Correction

The following items were specifically verified and require no changes:

1. All valuation figures match Avison Young documentation exactly
2. All title/ownership information matches GeoWarehouse and registered instruments
3. All building specifications (except clear height) match MPAC
4. Equipment and condition observations match Image_Index photo descriptions
5. Neighbour descriptions match site inspection documentation
6. Environmental screening results consistent with API data
7. Market context accurately reflects web research findings

---

## Conclusion

The location overview report demonstrates **high accuracy (91.5%)** with source documentation. The identified discrepancies are:

1. **Zoning designation** - requires correction from IC2 to E1 (or acknowledgment of both)
2. **Clear height** - recommend standardizing to 18 ft per Avison Young
3. **Photo count** - minor source document inconsistency (informational only)
4. **Postal code** - minor discrepancy between sources (acceptable)

**Overall Assessment:** The report is suitable for use with the recommended zoning correction applied. All financial, legal, and physical property data has been verified against authoritative sources.

---

*Review completed: January 15, 2026*
