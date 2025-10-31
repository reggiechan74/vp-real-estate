# LaTeX Conversion Guide for GitHub Markdown

## Status

**All Major Sections Completed:**

- ✅ Section 2.3: Stochastic Processes and Risk-Neutral Valuation (lines 61-177)
  - Rental Rate Dynamics (GBM, OU, CIR processes)
  - Property Value Dynamics
  - Risk-Neutral Valuation
  - Net Effective Rent (NER) Framework
  - Option-Adjusted Lease Spread (OALS)

- ✅ Section 3.4: Renewal Option Mathematics (lines 215-308)
  - Black-Scholes formulas for renewal options
  - Comparative statics
  - Numerical example

- ✅ Section 4.4: Termination Option Mathematics (lines 346-439)
  - Break option pricing
  - Default boundary analysis
  - First-passage time distributions
  - Numerical example

- ✅ Section 5.4: Rent Review Mechanisms (lines 471-613)
  - Upward-only rent reviews
  - Market rent resets
  - CPI-indexed escalations
  - Numerical example with Black-Scholes calculations

- ✅ Section 8.1: Black-Scholes Framework (lines 693-852)
  - European call/put option formulas
  - Adaptations for real estate
  - Put-call parity
  - Greeks (Delta, Gamma, Vega, Theta, Rho)
  - Numerical example with Greeks calculations

- ✅ Section 8.2: Binomial Lattice Models (lines 855-1037)
  - CRR binomial model
  - Backward induction algorithm
  - Convergence analysis
  - Trinomial lattice extension
  - Numerical example

- ✅ Section 8.3: Monte Carlo Simulation (lines 1039-1217)
  - GBM path simulation
  - Payoff calculations
  - Variance reduction techniques (antithetic variates, control variates)
  - Standard error and confidence intervals

- ✅ Section 8.4: Volatility Estimation (lines 1230-1427)
  - Historical volatility (log-returns method)
  - GARCH(1,1) model
  - Cross-sectional estimation
  - Implied volatility (Newton-Raphson)
  - REIT-based proxies
  - Geltner unsmoothing method
  - Volatility term structure

**Conversion Complete:** All major mathematical formulas have been converted to GitHub-compatible LaTeX format.

## GitHub LaTeX Syntax

### Display Math (Block Equations)
```latex
$$
equation here
$$
```

### Inline Math
```latex
$x = y + z$
```

## Common Conversions Needed

### Greek Letters
- μ → `\mu`
- σ → `\sigma`
- δ → `\delta`
- κ → `\kappa`
- θ → `\theta`
- λ → `\lambda`
- ρ → `\rho`
- φ → `\phi`
- Γ → `\Gamma`
- Δ → `\Delta`
- Θ → `\Theta`
- Φ → `\Phi`

### Subscripts & Superscripts
- `R_0` → `R_0` (already correct if in math mode)
- `T₁` → `T_1`
- `e^(-rT)` → `e^{-rT}`
- `σ²` → `\sigma^2`

### Operators
- × → `\times`
- √ → `\sqrt{}`
- ∑ → `\sum`
- ∫ → `\int`
- ≥ → `\geq`
- ≤ → `\leq`
- ≈ → `\approx`
- ≠ → `\neq`
- → → `\to` or `\rightarrow`

### Functions
- `max[...]` → `\max\left[...\right]`
- `ln(x)` → `\ln(x)`
- `exp(x)` → `\exp(x)` or `e^{x}`
- `E^Q[...]` → `\mathbb{E}^{\mathbb{Q}}\left[...\right]`

### Fractions
```latex
[a + b]/[c + d]  →  \frac{a + b}{c + d}
```

### Summations
```latex
Σ[i=1 to N]  →  \sum_{i=1}^{N}
```

### Integrals
```latex
∫[0,T]  →  \int_0^T
```

## Example Conversions

### Before:
```
V_renewal = e^(-rT₁) × E^Q[max(A₁ - A₂ - C_relocation, 0)]
```

### After:
```latex
$$V_{\text{renewal}} = e^{-rT_1} \times \mathbb{E}^{\mathbb{Q}}\left[\max(A_1 - A_2 - C_{\text{relocation}}, 0)\right]$$
```

### Before:
```
dR(t) = μR(t)dt + σR(t)dW(t)
```

### After:
```latex
$$dR(t) = \mu R(t)dt + \sigma R(t)dW(t)$$
```

### Before:
```
σ̂ = √(1/(n-2) × Σ[i=2 to n] (r_i - r̄)²) × √(1/Δt)
```

### After:
```latex
$$\hat{\sigma} = \sqrt{\frac{1}{n-2} \times \sum_{i=2}^{n} (r_i - \bar{r})^2} \times \sqrt{\frac{1}{\Delta t}}$$
```

## Automated Conversion Script

A Python script `convert_to_latex.py` has been created to help with bulk conversion.
However, manual review is required for complex formulas.

### Usage:
```bash
python3 convert_to_latex.py
# Review output file: Real_Estate_Lease_Options_Pricing_Research_latex.md
# If acceptable, replace original:
mv Real_Estate_Lease_Options_Pricing_Research_latex.md Real_Estate_Lease_Options_Pricing_Research.md
```

## Manual Conversion Priority

**High Priority** (most visible/important):
1. Section 8.1: Black-Scholes formulas (d1, d2, option pricing)
2. Section 3.4: Renewal option valuation
3. Section 5.4: Rent review pricing (upward-only calls)
4. Section 8.2: Binomial lattice construction

**Medium Priority**:
5. Section 4.4: Termination/default boundary
6. Section 8.3: Monte Carlo algorithm
7. Section 8.4: Volatility estimation formulas

**Low Priority** (numerical examples - can remain in code blocks):
8. Numerical calculation examples
9. Step-by-step computations

## Testing LaTeX Rendering

After conversion, test GitHub rendering by:
1. Committing changes to GitHub
2. Viewing the markdown file on GitHub web interface
3. Checking that all $$ blocks render correctly

Common rendering issues:
- Unmatched braces `{}` - Use `\{` and `\}` for literal braces
- Backslashes - Need proper escaping in some contexts
- Special characters in subscripts - Wrap in braces `_{\text{name}}`

## Next Steps

1. Run `convert_to_latex.py` for bulk conversion
2. Manually review and fix complex formulas
3. Test rendering on GitHub
4. Iterate as needed

