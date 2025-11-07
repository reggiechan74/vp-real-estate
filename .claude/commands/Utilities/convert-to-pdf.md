---
description: Convert markdown files to PDF format with optional output path specification
argument-hint: <markdown-file-path> [output-path]
allowed-tools: Read, Bash
---

You are a document conversion specialist. Your task is to convert markdown files to professionally formatted PDF documents using the available conversion tools.

## Input

The user will provide:
- **Required**: A markdown file path (e.g., `/path/to/document.md`)
- **Optional**: Custom output path (e.g., `/path/to/output.pdf`)

**Arguments provided**: {{args}}

## Conversion Process

### Step 1: Parse Arguments

Extract the input file path and optional output path from the arguments:
- First argument is always the input markdown file path
- Second argument (if present) is the custom output PDF path
- If no output path is provided, use the same directory and filename with `.pdf` extension

### Step 2: Validate Input File

1. Check that the input file exists and has `.md` or `.markdown` extension
2. If the file doesn't exist, inform the user and exit
3. Verify the file is readable

### Step 3: Determine Output Path

If output path is not specified:
- Use the same directory as the input file
- Replace the file extension with `.pdf`
- Example: `/path/to/README.md` → `/path/to/README.pdf`

If output path is specified:
- Ensure the directory exists, create if needed
- Ensure the filename ends with `.pdf` extension

### Step 4: Convert to PDF

Use `pandoc` with `wkhtmltopdf` engine for the conversion:

```bash
pandoc <input-file> -o <output-file> --pdf-engine=wkhtmltopdf
```

**Important notes:**
- The conversion preserves markdown formatting including headers, code blocks, lists, and tables
- SVG images may show warnings but the PDF will still be created
- The process may take 10-30 seconds depending on document size

### Step 5: Verify and Report

1. Check that the output PDF was created successfully using `ls -lh <output-file>`
2. Report the output location and file size to the user
3. If conversion fails, explain the error and suggest alternatives

## Error Handling

If conversion fails:
1. Check if pandoc is installed: `which pandoc`
2. Check if wkhtmltopdf is installed: `which wkhtmltopdf`
3. If tools are missing, inform the user they need to install them
4. Provide the exact error message from the conversion attempt

## Example Usage

**Basic conversion:**
```
/convert-to-pdf /workspaces/project/README.md
# Output: /workspaces/project/README.pdf
```

**Custom output path:**
```
/convert-to-pdf /workspaces/project/README.md /workspaces/docs/project-readme.pdf
# Output: /workspaces/docs/project-readme.pdf
```

**Batch conversion (multiple files):**
```
/convert-to-pdf /workspaces/docs/*.md
# Converts all .md files in the directory to PDF
```

## Success Criteria

- PDF file is created at the specified or default location
- File size is reported to confirm successful creation
- User receives clear confirmation of the output location
- Any warnings during conversion are mentioned but don't prevent success

## Response Format

Provide a concise response showing:
1. Input file processed
2. Output location
3. File size
4. Any warnings (if applicable)

Example:
```
✓ Successfully converted README.md to PDF

Output: /workspaces/lease-abstract/README.pdf (122KB)
```
