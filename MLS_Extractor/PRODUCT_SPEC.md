# MLS Extraction - Product Specification

**Version**: 1.0
**Date**: 2025-11-06
**Philosophy**: Insanely great. Not good enough. Perfect.

---

## The Magic Moment

User types: `/extract-mls Mississauga_industrial.pdf`

30 seconds later, Excel file opens with:
- **Perfect formatting** - looks like a designer made it
- **Subject property highlighted** - bright yellow, bold, impossible to miss
- **Perfect column order** - most important data first (rent, TMI, size)
- **Zero errors** - every field extracted correctly
- **Professional appearance** - they can send this to their boss immediately

---

## The One Command

```bash
/extract-mls <pdf-path> [--subject="partial address"]
```

**That's it.** No format flags. No configuration. It just works.

**Output**: Always Excel (.xlsx). Always professional. Always perfect.

---

## Perfect Column Order

Columns arranged by **decision importance**, not alphabetically:

| # | Column | Why This Order |
|---|--------|----------------|
| 1 | **Is Subject** | Sort to find your property instantly |
| 2 | **Address** | Where is it? |
| 3 | **Unit** | Which space? |
| 4 | **Available SF** | How much space? |
| 5 | **Net Rent** | MOST CRITICAL - what's the asking price? |
| 6 | **TMI** | Second most critical - what's the opex? |
| 7 | **Gross Rent** | Total occupancy cost (calculated) |
| 8 | **Clear Height** | Critical for industrial users |
| 9 | **Building Age** | How new is it? |
| 10 | **Class** | A/B/C quality tier |
| 11 | **Parking Ratio** | Parking availability |
| 12 | **% Office** | Office vs warehouse mix |
| 13-34 | **Other variables** | Secondary importance |

**Key Decision:** Show Building Age (intuitive), not Year Built (requires calculation).

---

## Perfect Visual Design

### Header Row
- **Background**: Dark blue (#2C3E50)
- **Text**: White, bold, 11pt Calibri
- **Frozen**: Always visible when scrolling
- **Auto-filter**: Enabled on all columns

### Subject Property Row
- **Background**: Bright yellow (#FFFF00)
- **Text**: Bold, dark text
- **Impossible to miss**: Even with 100 properties, you'll spot it instantly

### Data Rows
- **Alternating**: White / light gray (#F8F9FA)
- **Borders**: Subtle light gray lines
- **Font**: 10pt Calibri, professional

### Column Widths
- **Auto-sized**: Fit content perfectly
- **Minimum**: 10 characters
- **Maximum**: 50 characters (no endless wide columns)

### Number Formatting
- **Currency**: `$#,##0.00` (e.g., $13.95)
- **Percentages**: `0.0%` (e.g., 3.0%)
- **Integers**: `#,##0` (e.g., 238,501)
- **Decimals**: `0.0` (e.g., 34.0 ft)

---

## Zero Configuration Philosophy

**Auto-detect everything:**

1. **Subject Property**
   - First, check for "Subject" in Client Remarks
   - If ambiguous or not found, use `--subject` flag with fuzzy matching
   - Default: First property if no subject found

2. **File Naming**
   - Format: `YYYY-MM-DD_HHMMSS_mls_extraction_<market>.xlsx`
   - Market name: Auto-detect from PDF content
   - Timezone: Always Eastern Time

3. **Field Parsing**
   - Bay Depth: Auto-parse "55 x 52" → 55.0
   - Lot Size: Auto-convert sq ft to acres
   - HVAC: Auto-encode Y=1, Partial=2, N=3
   - Building Age: Auto-calculate from year_built

**No user should ever need to specify parsing rules.**

---

## Quality Bar

**Shipping Criteria** (all must be true):

- ✅ 95%+ field extraction accuracy (spot-check 10% sample)
- ✅ Subject property correctly identified 100% of time
- ✅ Excel file opens perfectly in Excel/Sheets/Calc
- ✅ Professional appearance - no embarrassing formatting
- ✅ Zero crashes on malformed PDFs
- ✅ Process 25-property PDF in <60 seconds

**If any criterion fails, we don't ship.**

---

## What We're NOT Building

❌ **CSV output** - Nobody needs it. Excel can export to CSV.
❌ **Multiple format flags** - Complexity for no benefit.
❌ **Manual field mapping** - Should be auto-detected.
❌ **Complex configuration** - One command. Zero configuration.
❌ **Batch processing** - Ship single-file first. Add later if needed.

---

## The Test

Open the Excel file and ask:

> **"Would I be proud to send this to my CEO?"**

If the answer isn't an immediate "yes," it's not done.

---

**END OF SPEC**

*"Design is not just what it looks like and feels like. Design is how it works."*
— Steve Jobs
