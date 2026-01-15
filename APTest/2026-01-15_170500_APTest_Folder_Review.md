# APTest Folder Review Report

**Prepared for:** Alex Pitt
**Date:** January 15, 2026
**Purpose:** Location Overview Analysis Data Package Review

---

## Executive Summary

The `/workspaces/lease-abstract/APTest` folder contains a comprehensive data package for **321 Humberline Drive, Etobicoke, Ontario** - an industrial property that was the subject of an appraisal or location overview analysis with an **effective date of February 2020**. The package includes title documents, MPAC assessment reports, site inspection photographs, and comparable sales data from Urbanation.

---

## Folder Structure Overview

```
APTest/
├── .gitignore                    # Standard Python/data gitignore
├── Property_name.md              # Subject property identifier
├── SP Details/                   # Site inspection photos (136 files, 634 MB)
├── SP Docs/                      # Source property documents (7 files)
└── Urbannation Data/             # Comparable sales reports (31 files)
```

---

## 1. Subject Property Identification

**File:** `Property_name.md`

| Attribute | Value |
|-----------|-------|
| **Address** | 321 Humberline Drive, Etobicoke, Ontario |
| **Effective Date** | February 2020 |

---

## 2. Source Property Documents (`SP Docs/`)

This folder contains **7 documents** totaling approximately 6.4 MB of official property records:

### 2.1 MPAC Reports

| Document | Size | Description |
|----------|------|-------------|
| **MPAC Detail Report.PDF** | 5.8 KB | Basic property assessment summary |
| **MPAC Basic Industrial Report.pdf** | 253 KB | Detailed industrial property report with building specs |

**Key Property Data from MPAC:**

| Attribute | Value |
|-----------|-------|
| Roll Number | 1919044460003000000 |
| Property Code | 520 - Standard Industrial |
| Site Area | 1.70 acres |
| Frontage | 186.66 ft |
| Zoning | IC2 |
| Year Built | 1978 |
| Assessed Value (Jan 1, 2016) | $3,167,000 |
| Latest Sale (Jan 2001) | $1,250,000 |

**Building Configuration (from MPAC):**

| Year Built | Floor Level | Clear Height | Interior Finish | Building Area |
|------------|-------------|--------------|-----------------|---------------|
| 1978 | 1 | 20 ft | - | 25,030 sf |
| 1978 | 1 | 13 ft | - | 2,304 sf |
| 1978 | 1 | 9 ft | 750 sf | - |

**Total Building Area:** ~27,334 sf (warehouse + auxiliary)

### 2.2 Title Documents

| Document | Size | Description |
|----------|------|-------------|
| **Parcel Register.pdf** | 136 KB | Land Titles parcel register (PIN 07367-0027) |
| **Parcel Register (1).pdf** | 136 KB | Duplicate copy |
| **Geowarehouse.pdf** | 5.3 MB | Comprehensive GeoWarehouse Property Report |

**Title Chain Summary:**

| Date | Instrument | Type | Amount | Parties |
|------|------------|------|--------|---------|
| 1971/08/13 | EB387062 | Transfer Easement | - | To: Canadian National Railway |
| 1977/02/22 | EB473411 | Transfer | *Deleted* | To: St. Lawrence Chemical |
| 2001/01/10 | E386101 | Transfer | $1,250,000 | St. Lawrence Chemical Inc. → CAD-TEK Tool Design Ltd. |
| 2005/06/02 | AT821206 | Name Change | - | CAD-TEK Tool Design Ltd. → CAD-TEK Holdings Inc. |
| 2017/12/20 | AT4764856 | Charge | $4,194,000 | To: Royal Bank of Canada |
| 2017/12/20 | AT4764858 | No Assign Rent | - | To: Royal Bank of Canada |

**Current Owner:** CAD-TEK Holdings Inc.

**Encumbrance:** CN Rail Easement (EB387062) - Right of way for industrial lead track

### 2.3 Registered Instruments

| Document | Size | Description |
|----------|------|-------------|
| **instrument_E386101.PDF** | 133 KB | Transfer/Deed of Land (2001 sale) |
| **instrument_EB387062.PDF** | 136 KB | CN Rail Easement Grant (1971) |

**Transfer E386101 Details (2001 Sale):**
- Transferor: St. Lawrence Chemical Inc.
- Transferee: CAD-TEK Tool Design Ltd.
- Consideration: $1,250,000
- Land Transfer Tax: $17,285
- Legal Description: Part of Lot 37, Concession 3, Northern Division Fronting the Humber, Parts 7 & 8 on Plan 64R-5014

**Easement EB387062 Details (1971):**
- Grantor: Kagera Holdings Limited
- Grantee: Canadian National Railway Company
- Purpose: Right of way to construct, operate, and maintain an Industrial Lead Track
- Consideration: $2.00
- Area: Approximately 1.008 acres

### 2.4 GeoWarehouse Property Report (7 pages)

**Report Generated:** September 26, 2019 by Mark Penney, MPR Advisors

**Comprehensive Property Profile:**

| Category | Details |
|----------|---------|
| **PIN** | 073670027 |
| **LRO** | Metropolitan Toronto (80) |
| **Registration Type** | Certified (Land Titles) |
| **Ownership Type** | Freehold |
| **Lot Area** | 74,658.41 sf (1.71 acres) |
| **Perimeter** | 1,309.06 ft |
| **Lot Dimensions** | 381.06 ft x 20.15 ft x 197.0 ft x 186.88 ft |

**Demographics (Neighbourhood):**
- Population: 611
- Avg. Household Income: $73,462
- Home Ownership: 85%
- Dominant Language: English (52%)
- Employment Rate: 66%

---

## 3. Site Inspection Photos (`SP Details/`)

This folder contains **136 files** (135 JPG photos + 1 MOV video) totaling **634 MB** of site inspection documentation.

### Photo Summary

| Attribute | Value |
|-----------|-------|
| **Total Files** | 136 |
| **Photo Files** | 135 JPG |
| **Video Files** | 1 MOV |
| **Total Size** | 634 MB |
| **Date Taken** | January 28, 2020 |
| **Time Range** | 14:52 - 16:04 |

### Photo Categories (Based on Timestamps)

The photos appear to document a comprehensive site inspection conducted on **January 28, 2020**, capturing:

| Time Window | Likely Content |
|-------------|----------------|
| 14:52 - 15:00 | Arrival/exterior approach shots |
| 15:00 - 15:10 | Building exterior - front facade |
| 15:39 - 15:42 | Building exterior - side views |
| 15:50 - 15:58 | Interior inspection / rear areas |
| 15:59 - 16:04 | Departure / final exterior shots |

### Sample Photo Analysis

From the sample photo reviewed (2020-01-28 15.00.12.jpg):
- Shows industrial building with concrete block construction
- Visible railroad siding adjacent to property (confirms CN Rail easement)
- Winter conditions (January) with some snow visible
- Typical 1970s-era industrial building design

---

## 4. Comparable Sales Data (`Urbannation Data/`)

This folder contains **31 Urbanation industrial building sale reports** covering properties in Etobicoke, Mississauga, and Brampton - serving as comparable sales for the subject property analysis.

### File Inventory

| # | Property Address | Municipality | Format |
|---|-----------------|--------------|--------|
| 1 | 55 Brydon Drive | Etobicoke | PDF |
| 2 | 70 Galaxy Boulevard | Etobicoke | JPG |
| 3 | 88 Horner Avenue | Etobicoke | JPG |
| 4 | 105 Brockhouse Road | Etobicoke | JPG |
| 5 | 105 Clairpoint Crescent | Etobicoke | JPG |
| 6 | 190 Norseman Street | Etobicoke | JPG |
| 7 | 255 Carrier Drive | Etobicoke | JPG |
| 8 | 324 Traders Boulevard East | Mississauga | JPG |
| 9 | 370 Brunel Road | Mississauga | JPG |
| 10 | 380 Orenda Road | Brampton | JPG |
| 11 | 400 Ambassador Drive | Mississauga | JPG |
| 12 | 750 Gana Court | Mississauga | JPG |
| 13 | 1039 Cardiff Boulevard | Mississauga | JPG |
| 14 | 1830 Meyerside Drive | Mississauga | JPG |
| 15 | 2395 Lucknow Drive | Mississauga | JPG |
| 16 | 3121 Universal Drive | Mississauga | JPG |
| 17 | 5145 Satellite Drive | Mississauga | JPG |
| 18 | 5195 Tomken Road | Mississauga | JPG |
| 19 | 5228 Everest Drive | Mississauga | JPG |
| 20 | 5240 Bradco Boulevard | Mississauga | JPG |
| 21 | 5672 McAdam Road | Mississauga | JPG |
| 22 | 5915 Wallace Street | Mississauga | JPG |
| 23 | 5926 Shawson Drive | Mississauga | JPG |
| 24 | 5939 Wallace Street | Mississauga | JPG |
| 25 | 6295 Kestrel Road | Mississauga | JPG |
| 26 | 6605 Kestrel Road | Mississauga | JPG |
| 27 | 6691 Edwards Boulevard | Mississauga | JPG |
| 28 | 7361 Pacific Circle | Mississauga | JPG |
| 29 | 7440 Tranmere Drive | Mississauga | JPG |
| 30 | 7491 Pacific Circle | Mississauga | JPG |

### Geographic Distribution

| Municipality | Count |
|--------------|-------|
| Mississauga | 22 |
| Etobicoke | 7 |
| Brampton | 1 |
| **Total** | **30** |

### Sample Comparable Analysis

**70 Galaxy Boulevard, Etobicoke** (Sale Date: November 1, 2019)

| Attribute | Value |
|-----------|-------|
| Sale Price | $5,500,000 |
| Land Area | 1.45 acres @ $3,793,103/acre |
| Building Area | 23,690 sf @ $232/sf |
| Office Area | 18,690 sf |
| Industrial Area | 5,000 sf |
| Site Density | 37% |
| Zoning | Employment Industrial (E 1.0) |

**55 Brydon Drive, Etobicoke** (Sale Date: May 8, 2018)

| Attribute | Value |
|-----------|-------|
| Sale Price | $3,900,000 |
| Land Area | 1.40 acres @ $2,785,714/acre |
| Building Area | 16,415 sf @ $238/sf |
| Year Built | 1966 |
| Clear Height | 12-15 ft |
| Site Density | 28% |
| Zoning | Employment Industrial (E 1.0) |

---

## 5. Data Quality Assessment

### Strengths

| Aspect | Assessment |
|--------|------------|
| **Title Documentation** | Complete chain of title with registered instruments |
| **Assessment Data** | Current MPAC reports with building specifications |
| **Site Photos** | Extensive documentation (136 files) from single inspection date |
| **Comparables** | 30 industrial sales in relevant geographic area |

### Data Gaps / Considerations

| Issue | Impact |
|-------|--------|
| Photo organization | Files use timestamp names only - no descriptive naming |
| Comparable date range | Unknown - need to verify sale dates align with effective date |
| Subject building details | Limited interior specifications in available documents |
| Environmental reports | No Phase I/II ESA documents present |

---

## 6. Suitability for Location Overview Analysis

This data package appears **well-suited** for a Location Overview analysis with the following components available:

| Component | Status | Source |
|-----------|--------|--------|
| Subject Property Identification | ✅ Complete | MPAC, Title Docs |
| Legal Description | ✅ Complete | Parcel Register |
| Ownership History | ✅ Complete | Title Chain |
| Building Specifications | ✅ Partial | MPAC Basic Industrial Report |
| Site Inspection Documentation | ✅ Extensive | 136 photos/video |
| Comparable Sales | ✅ Comprehensive | 30 Urbanation reports |
| Encumbrances | ✅ Documented | CN Rail Easement |
| Demographic Data | ✅ Available | GeoWarehouse Report |

### Recommended Next Steps

1. **Organize Site Photos** - Rename files with descriptive identifiers
2. **Extract Comparable Data** - Build comparison grid from Urbanation reports
3. **Verify Sale Dates** - Ensure comparables align with Feb 2020 effective date
4. **Building Inspection** - Confirm current condition matches 2020 photos
5. **Environmental Review** - Obtain Phase I ESA if not previously completed

---

## Appendix A: File Statistics

| Folder | Files | Size | Types |
|--------|-------|------|-------|
| Root | 2 | <1 KB | .gitignore, .md |
| SP Details | 136 | 634 MB | .jpg (135), .mov (1) |
| SP Docs | 7 | 6.4 MB | .pdf (7) |
| Urbannation Data | 31 | 6.6 MB | .jpg (30), .pdf (1) |
| **Total** | **176** | **~647 MB** | |

---

*Report generated by Claude Code for Alex Pitt's Location Overview Analysis preparation.*
