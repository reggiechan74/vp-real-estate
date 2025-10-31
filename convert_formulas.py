#!/usr/bin/env python3
"""Convert code-block formulas to LaTeX format in markdown file."""

import re
import sys

def convert_formula_block(text):
    """Convert a code block formula to LaTeX display math."""
    # Remove leading/trailing whitespace
    text = text.strip()

    # Skip if already in LaTeX
    if text.startswith('$$') or text.startswith('$'):
        return text

    # Skip if it's not a formula (contains code keywords)
    code_keywords = ['For', 'If', 'Else', 'While', 'def', 'class', 'import', 'return', '#']
    if any(text.startswith(kw) for kw in code_keywords):
        return f"```\n{text}\n```"

    # Convert common patterns
    text = text.replace('×', r'\times')
    text = text.replace('≥', r'\geq')
    text = text.replace('≤', r'\leq')
    text = text.replace('≠', r'\neq')
    text = text.replace('≈', r'\approx')
    text = text.replace('→', r'\to')
    text = text.replace('√', r'\sqrt')
    text = text.replace('∫', r'\int')
    text = text.replace('Σ', r'\sum')
    text = text.replace('∈', r'\in')
    text = text.replace('∉', r'\notin')
    text = text.replace('∞', r'\infty')

    # Convert subscripts and superscripts
    text = re.sub(r'_(\w+)', r'_{\1}', text)
    text = re.sub(r'\^(\w+)', r'^{\1}', text)

    # Convert common functions
    text = re.sub(r'\bln\b', r'\ln', text)
    text = re.sub(r'\bexp\b', r'\exp', text)
    text = re.sub(r'\bmax\b', r'\max', text)
    text = re.sub(r'\bmin\b', r'\min', text)
    text = re.sub(r'\bsin\b', r'\sin', text)
    text = re.sub(r'\bcos\b', r'\cos', text)

    return f"$${text}$$"

def process_file(filename):
    """Process markdown file and convert formulas."""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    result = []
    in_code_block = False
    code_block_content = []
    code_block_start = 0

    for i, line in enumerate(lines):
        # Skip first 180 lines (already converted)
        if i < 180:
            result.append(line)
            continue

        # Detect code block boundaries
        if line.strip() == '```':
            if not in_code_block:
                # Starting a code block
                in_code_block = True
                code_block_content = []
                code_block_start = i
            else:
                # Ending a code block - process it
                formula_text = '\n'.join(code_block_content)
                converted = convert_formula_block(formula_text)

                # If it's now LaTeX, don't use code block markers
                if converted.startswith('$$'):
                    result.append(converted)
                else:
                    result.append('```')
                    result.append(formula_text)
                    result.append('```')

                in_code_block = False
                code_block_content = []
        elif in_code_block:
            code_block_content.append(line)
        else:
            result.append(line)

    return '\n'.join(result)

if __name__ == '__main__':
    filename = '/workspaces/lease-abstract/Real_Estate_Lease_Options_Pricing_Research.md'
    converted = process_file(filename)

    # Write to output file
    with open(filename + '.converted', 'w', encoding='utf-8') as f:
        f.write(converted)

    print(f"Converted file written to {filename}.converted")
    print("Review the changes and then rename if acceptable")
