---
description: Abstract a commercial lease document (office or industrial) using standardized templates
---

You are a commercial real estate lease abstraction expert. Your task is to abstract the lease document provided by the user following the standardized templates in this repository.

## Input

The user will provide a lease document as either:
- A file path (e.g., `/path/to/lease.docx` or `/path/to/lease.md`)
- A URL to a lease document

**Optional Arguments:**
- `-json` - Output in JSON format instead of markdown (saves as .json file)

**Document provided**: {{args}}

## Parse Arguments

First, check if the arguments contain `-json`:
- If `-json` is present, set output format to JSON and remove `-json` from the document path/URL
- Otherwise, set output format to Markdown (default)

## Format Philosophy

**Markdown Format (default):**
- **Purpose**: Quick executive review, human-readable summary
- **Style**: Concise, bullet points, facts only, minimal elaboration
- **Length**: ~30-40KB target (50-60% shorter than comprehensive)
- **Audience**: Business users, executives, quick review
- **Example style**:
  ```
  - **Landlord**: Temple CB, LLC, 4350 Temple City Blvd, El Monte, CA 91731
  - **Tenant**: Okra Energy, Inc. (same address - related party transaction)
  - **Term**: 2013-12-01 to 2020-05-31 (6.5 years)
  - **Rent**: Graduated $0-$70K/month (6 months free, then $30K-$70K)
  ```

**JSON Format (-json flag):**
- **Purpose**: Data integration, programmatic analysis, comprehensive record
- **Style**: Complete detail, all extracted information, structured data
- **Length**: ~50-60KB (comprehensive)
- **Audience**: Databases, lease management systems, analytics tools
- **Example style**: Full nested objects with all available data points

## Process

### Step 1: Load the Document

1. If the argument is a file path:
   - If it's a `.docx` file, first convert it to markdown using `markitdown`
   - Then read the markdown content
2. If the argument is a URL:
   - Use WebFetch to retrieve the document content
3. If the document is very large (>256KB), read it in sections

### Step 2: Determine Lease Type

Analyze the document to determine if this is an:
- **Industrial Lease** - Look for: warehouse, manufacturing, industrial use, loading docks, industrial measurement standards (ANSI/BOMA Z65.2-2012)
- **Office Lease** - Look for: office use, professional services, office measurement standards (ANSI/BOMA Office)

Load the appropriate template based on output format:

**If Markdown output (default):**
- `Templates/Industrial/industrial_lease_abstract_template.md` for industrial leases
- `Templates/Office/office_lease_abstract_template.md` for office leases

**If JSON output (-json flag):**
- `Templates/Industrial/industrial_lease_abstract_template.json` for industrial leases
- `Templates/Office/office_lease_abstract_template.json` for office leases
- Also reference the schema: `Templates/Industrial/industrial_lease_abstract_schema.json` or `Templates/Office/office_lease_abstract_schema.json`

### Step 3: Extract Information

Read through the lease document and extract ALL information for each of the 24 sections.

**For Markdown Output (Concise):**
- Lead with 2-3 sentence Executive Summary covering: property, parties, term, rent, key provisions
- Add "Key Terms at a Glance" section with critical facts in brief bullets
- For each of the 24 sections, use short bullets stating facts directly
- Omit lengthy explanations, examples, and verbose descriptions
- Limit Key Issues & Risks to top 5 red flags, top 5-7 favorable, top 5-7 unfavorable, top 10 review items

**For JSON Output (Comprehensive):**
- Populate all fields in the JSON template
- Include complete detail and all extracted information
- Use proper data types throughout

**24 Sections to Extract:**

1. **Document Information** - Create abstract metadata
2. **Parties** - Landlord, Tenant, Indemnifier/Guarantor names and addresses
3. **Premises** - Property address, unit number, rentable area, measurement standard, permitted use
4. **Term** - Commencement date, expiry date, term length, fixturing period, renewal options
5. **Rent** - Basic rent schedule (by year), escalations, additional rent (operating costs, taxes, management fee), proportionate share, payment terms
6. **Deposits & Security** - Rent deposit amount and terms, letter of credit requirements
7. **Operating Costs & Taxes** - Lease type (net/gross), included/excluded items, base year, gross-up provisions, tax payment method
8. **Use & Operations** - Permitted uses, prohibited uses, business hours, signage rights
9. **Maintenance & Repairs** - Landlord obligations (structural, roof, common areas, HVAC), tenant obligations (interior, janitorial, repairs under threshold)
10. **Alterations & Improvements** - Landlord's work, tenant's work, approval requirements, ownership of improvements
11. **Insurance & Indemnity** - Tenant insurance requirements (CGL, property, business interruption), waiver of subrogation, indemnification provisions
12. **Damage & Destruction** - Landlord repair obligations, time to repair, termination rights, rent abatement provisions
13. **Assignment & Subletting** - Transfer restrictions, consent requirements, landlord's recapture rights, profit sharing, permitted transfers
14. **Default & Remedies** - Events of default (non-payment grace period, breach cure period), landlord remedies, interest on late payments
15. **Services & Utilities** - Utilities provided by landlord, tenant responsibility, separately metered utilities, after-hours HVAC
16. **Environmental** - Compliance obligations, hazardous substances restrictions, remediation responsibility
17. **Subordination & Attornment** - Subordination to mortgages, SNDA requirements, registration provisions
18. **Notices** - Notice requirements (form, delivery method), notice addresses for landlord and tenant
19. **End of Term** - Surrender condition, removal of improvements, overholding rent (typically 150-200% of last month), cleaning requirements
20. **Special Provisions** - Any custom terms, particularly from Schedule G
21. **Schedules & Exhibits** - List which schedules are attached (A-J), summarize key items
22. **Critical Dates Summary** - Create a table of critical dates with notice requirements
23. **Financial Obligations Summary** - Calculate initial costs and estimated monthly costs
24. **Key Issues & Risks** - Identify favorable terms, unfavorable terms/risks, items requiring further review

### Step 4: Pay Special Attention To

**Financial Terms:**
- Exact rent amounts by year (annual, monthly, rate per sq ft)
- Escalation method and frequency
- Operating cost caps or limitations
- Tax allocation method
- Management fee percentage and basis

**Critical Dates:**
- Lease commencement and expiry dates
- Delivery date vs commencement date
- Renewal option notice deadlines (calculate backward from expiry)
- All dates requiring tenant action

**Proportionate Share:**
- Extract the rentable area of premises
- Extract total building rentable area
- Calculate percentage if stated as fraction

**Special Provisions (Schedule G):**
- This often contains the most important custom terms
- May override standard lease provisions
- Look for fixturing periods, rent-free periods, landlord work, special rights

**Standard Schedules:**
- Note which schedules (A-J) are referenced and attached
- Summarize any critical items from schedules

**Definitions:**
- The lease will have a detailed Definitions section
- Use these definitions to understand terms like "Operating Costs", "Realty Taxes", "Premises", "Common Facilities"

### Step 5: Output Format

**If Markdown Output (default):**

Provide a **CONCISE** lease abstract in markdown format. The output should be clear and complete but avoid verbosity:

1. **Executive Summary** (new) - Brief 3-5 sentence overview of the lease
2. **Document Information** - Basic metadata only
3. **Key Terms at a Glance** (new) - Bullet point summary of most critical terms:
   - Parties, Property, Term, Base Rent, Lease Type
   - Major provisions (purchase options, termination rights, etc.)
4. **All 24 sections** - Use concise bullet points, not lengthy paragraphs
   - State facts directly without unnecessary elaboration
   - Use "Not specified" for missing information (don't explain why)
   - Avoid repetitive phrasing
   - Combine related items where possible
5. **Critical Dates Summary** - Table format (keep as is)
6. **Financial Obligations Summary** - Table format (keep as is)
7. **Key Issues & Risks** - Concise bullet points only:
   - Critical red flags (top 5 only)
   - Most favorable terms (top 5-7 only)
   - Most unfavorable terms (top 5-7 only)
   - Top 10 items requiring review only

**Conciseness Guidelines for Markdown:**
- Use bullet points and tables instead of paragraphs wherever possible
- Eliminate explanatory text - just state the facts
- Remove examples and "note" sections unless critical
- Don't repeat information across sections
- Each bullet should be one line when possible
- Aim for 50-60% reduction in length compared to comprehensive format

**If JSON Output (-json flag):**

Provide the completed lease abstract in JSON format following the JSON template structure. Ensure:

1. All fields from the JSON template are populated
2. Use proper JSON data types:
   - Strings for text fields
   - Numbers (not strings) for numeric values (rent amounts, square footage, percentages)
   - Booleans (true/false) for yes/no fields
   - Arrays for lists
   - null for values that are not specified
3. Follow the structure exactly as defined in the JSON template
4. Ensure valid JSON syntax (proper quotes, commas, brackets)
5. Format dates as ISO 8601 strings (YYYY-MM-DD)
6. For the `keyIssuesAndRisks` section, populate arrays with string descriptions

**Important Guidelines:**

**Both Formats:**
- Extract ACTUAL values from the lease - do not leave template placeholders
- For dates, use consistent format: YYYY-MM-DD (ISO 8601)
- Calculate totals where requested (initial costs, monthly costs)
- Quote specific section/article numbers when referencing provisions

**Markdown-Specific (Concise Output):**
- State "Not specified" for missing information (no explanation needed)
- Use bullet points and tables - minimize paragraphs
- No repetition across sections
- Eliminate verbose explanations - state facts only
- Top issues only in Key Issues & Risks section (not comprehensive lists)
- Remove narrative commentary unless critical
- Target 30-40KB file size (vs 60-70KB comprehensive)

**JSON-Specific (Comprehensive Output):**
- Use null for missing numbers, "" for missing text, [] for missing lists, false for missing booleans
- Numbers without currency symbols (e.g., 5000.00)
- All data properly typed (numbers as numbers, booleans as true/false, not strings)
- Complete detail in all arrays (not truncated)

### Step 6: Save the Abstract

After completing the abstract, save it to the Reports folder:

1. Create a filename based on the property location and lease date
   - **For Markdown**: `[Location]_Lease_Abstract_[Date].md`
   - **For JSON**: `[Location]_Lease_Abstract_[Date].json`
   - Example: `El_Monte_Lease_Abstract_2013-12-01.md` or `El_Monte_Lease_Abstract_2013-12-01.json`
   - Use underscores instead of spaces
   - Include the lease commencement date if available

2. Save the file to `/workspaces/lease-abstract/Reports/[filename]`
   - Create the Reports directory if it doesn't exist using: `mkdir -p /workspaces/lease-abstract/Reports`
   - Use the Write tool to save the complete abstract
   - For JSON files, ensure the output is properly formatted and valid JSON

3. Confirm the save was successful and provide the file path to the user

## Quality Checklist

Before presenting the abstract, verify:

- [ ] Lease type correctly identified (Industrial vs Office)
- [ ] All parties identified with full legal names
- [ ] Premises address, unit number, and square footage extracted
- [ ] Full term dates extracted (commencement and expiry)
- [ ] Complete rent schedule extracted (all years)
- [ ] Proportionate share calculated or extracted
- [ ] All deposits and security requirements identified
- [ ] Insurance requirements specified with dollar amounts
- [ ] Critical dates table/array completed with notice requirements
- [ ] Financial obligations summary calculated
- [ ] Key issues and risks analysis provided

**Additional JSON-specific checks (if -json flag used):**
- [ ] Valid JSON syntax (no trailing commas, proper quotes)
- [ ] All numeric values are numbers, not strings
- [ ] All boolean values are true/false, not strings
- [ ] Dates formatted as YYYY-MM-DD strings
- [ ] Arrays used for lists (not comma-separated strings)
- [ ] null used for missing numeric/object values
- [ ] Empty string ("") used for missing text values
- [ ] Empty arrays ([]) used for missing list values
- [ ] JSON structure matches the template exactly

## Begin Abstraction

Now proceed to abstract the lease document provided: {{args}}
