#!/usr/bin/env python3
"""
Convert mathematical formulas in markdown from code blocks to LaTeX format.
GitHub-compatible LaTeX using $$ for display math and $ for inline math.
"""

import re

def main():
    filename = '/workspaces/lease-abstract/Real_Estate_Lease_Options_Pricing_Research.md'

    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Process line by line
    lines = content.split('\n')
    output_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Skip lines before 180 (already converted)
        if i < 180:
            output_lines.append(line)
            i += 1
            continue

        # Check if this is a code block start
        if line.strip() == '```':
            # Look ahead to find the closing ```
            j = i + 1
            formula_lines = []
            found_end = False

            while j < len(lines):
                if lines[j].strip() == '```':
                    found_end = True
                    break
                formula_lines.append(lines[j])
                j += 1

            if found_end and formula_lines:
                formula_text = '\n'.join(formula_lines).strip()

                # Check if this looks like a formula (not code)
                is_code = any(keyword in formula_text for keyword in [
                    'For i =', 'If (', 'Else:', 'def ', 'class ', 'import ',
                    'return ', '#', 'While ', 'End', 'Then', 'Loop'
                ])

                if not is_code and not formula_text.startswith('$$'):
                    # Convert to LaTeX
                    latex_formula = convert_formula(formula_text)
                    output_lines.append(latex_formula)
                    i = j + 1  # Skip past the closing ```
                    continue

        output_lines.append(line)
        i += 1

    # Write output
    output_filename = filename.replace('.md', '_latex.md')
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))

    print(f"Converted file written to: {output_filename}")
    print("Please review the changes before replacing the original file.")

def convert_formula(text):
    """Convert a formula string to LaTeX format."""

    # Handle multiline formulas
    if '\n' in text and not text.startswith('$$'):
        # Each line might be a separate equation
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if len(lines) == 1:
            return '$$' + latex_format(lines[0]) + '$$'
        else:
            # Multiple equations
            latex_lines = [latex_format(line) for line in lines]
            return '$$' + '$$\n$$'.join(latex_lines) + '$$'

    return '$$' + latex_format(text) + '$$'

def latex_format(formula):
    """Apply LaTeX formatting to a single formula."""

    # Character replacements
    replacements = {
        '×': r'\times',
        '≥': r'\geq',
        '≤': r'\leq',
        '≠': r'\neq',
        '≈': r'\approx',
        '→': r'\to',
        '√': r'\sqrt',
        '∫': r'\int',
        '∑': r'\sum',
        'Σ': r'\sum',
        '∈': r'\in',
        '∉': r'\notin',
        '∞': r'\infty',
        'μ': r'\mu',
        'σ': r'\sigma',
        'δ': r'\delta',
        'κ': r'\kappa',
        'θ': r'\theta',
        'ρ': r'\rho',
        'ν': r'\nu',
        'Γ': r'\Gamma',
        'Δ': r'\Delta',
        'Θ': r'\Theta',
        'Φ': r'\Phi',
        'ω': r'\omega',
        'λ': r'\lambda',
        'β': r'\beta',
        'α': r'\alpha',
        'φ': r'\phi',
        'π': r'\pi',
        'τ': r'\tau',
    }

    for old, new in replacements.items():
        formula = formula.replace(old, new)

    # Convert E^Q to \mathbb{E}^{\mathbb{Q}}
    formula = re.sub(r'E\^Q\[', r'\\mathbb{E}^{\\mathbb{Q}}\\left[', formula)
    formula = formula.replace(']', r'\\right]') if r'\left[' in formula else formula

    # Convert subscripts with special chars (T₁ -> T_1, etc.)
    formula = formula.replace('₁', '_1').replace('₂', '_2').replace('₃', '_3')
    formula = formula.replace('₄', '_4').replace('₅', '_5').replace('₀', '_0')

    # Convert function names
    formula = re.sub(r'\bln\(', r'\\ln(', formula)
    formula = re.sub(r'\bexp\(', r'\\exp(', formula)
    formula = re.sub(r'\bmax\[', r'\\max\\left[', formula)
    formula = re.sub(r'\bmin\[', r'\\min\\left[', formula)
    formula = re.sub(r'\bmax\(', r'\\max(', formula)
    formula = re.sub(r'\bmin\(', r'\\min(', formula)

    # Convert summation notation
    formula = re.sub(r'Σ\[i=(\d+) to (\d+)\]', r'\\sum_{i=\1}^{\2}', formula)
    formula = re.sub(r'\\sum\[i=(\d+) to (\d+)\]', r'\\sum_{i=\1}^{\2}', formula)
    formula = re.sub(r'\\sum\[i=(\d+) to N\]', r'\\sum_{i=\1}^{N}', formula)
    formula = re.sub(r'\\sum\[i=(\d+) to N₂\]', r'\\sum_{i=\1}^{N_2}', formula)
    formula = re.sub(r'\\sum\[([^\]]+)\]', r'\\sum_{\1}', formula)

    # Convert integral notation
    formula = re.sub(r'∫\[(\d+),(\d+)\]', r'\\int_{\1}^{\2}', formula)
    formula = re.sub(r'∫\[0,T\]', r'\\int_0^T', formula)

    # Wrap fractions
    # Simple pattern: [numerator]/[denominator]
    formula = re.sub(r'\[([^\]]+)\]/\[([^\]]+)\]', r'\\frac{\1}{\2}', formula)

    # Convert common expressions
    formula = formula.replace('e^(-r', r'e^{-r')
    formula = formula.replace('e^(-', r'e^{-')
    formula = formula.replace('e^(', r'e^{')
    formula = formula.replace('(1-', r'(1 - ')
    formula = formula.replace('1-p', r'1-p')  # Leave this as-is for probabilities

    # Text subscripts
    formula = re.sub(r'_([a-zA-Z]+[0-9]*)', r'_{\1}', formula)
    formula = re.sub(r'\^([a-zA-Z0-9]+)', r'^{\1}', formula)

    # Special functions
    formula = formula.replace('N(d_1)', r'N(d_1)')
    formula = formula.replace('N(d_2)', r'N(d_2)')

    # Clean up spacing
    formula = re.sub(r'\s*×\s*', r' \\times ', formula)

    return formula

if __name__ == '__main__':
    main()
