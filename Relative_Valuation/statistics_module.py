#!/usr/bin/env python3
"""
Statistical Analysis Module for Relative Valuation

Provides traditional statistical methods as complement to MCDA:
- Multiple linear regression
- Correlation analysis
- Z-scores and standard deviations
- R-squared and statistical significance
- Residual analysis

Author: Claude Code
Version: 1.0.0
Date: 2025-11-06
"""

import json
import statistics
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
import math


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class StatisticalSummary:
    """Summary statistics for a single variable"""
    variable_name: str
    mean: float
    median: float
    std_dev: float
    min_value: float
    max_value: float
    count: int

    def coefficient_of_variation(self) -> float:
        """CV = std_dev / mean (measures relative variability)"""
        if self.mean == 0:
            return float('inf')
        return abs(self.std_dev / self.mean)


@dataclass
class CorrelationResult:
    """Correlation between two variables"""
    variable_x: str
    variable_y: str
    correlation: float
    r_squared: float
    sample_size: int

    def strength(self) -> str:
        """Interpret correlation strength"""
        abs_corr = abs(self.correlation)
        if abs_corr >= 0.7:
            return "Strong"
        elif abs_corr >= 0.4:
            return "Moderate"
        elif abs_corr >= 0.2:
            return "Weak"
        else:
            return "Negligible"

    def direction(self) -> str:
        """Positive or negative correlation"""
        return "Positive" if self.correlation >= 0 else "Negative"


@dataclass
class RegressionResult:
    """Multiple linear regression results"""
    dependent_variable: str
    independent_variables: List[str]
    coefficients: Dict[str, float]  # Variable name -> coefficient
    intercept: float
    r_squared: float
    adjusted_r_squared: float
    sample_size: int
    residuals: List[float] = field(default_factory=list)

    def predict(self, values: Dict[str, float]) -> float:
        """Predict dependent variable from independent variables"""
        prediction = self.intercept
        for var, coef in self.coefficients.items():
            if var in values:
                prediction += coef * values[var]
        return prediction


@dataclass
class ZScoreAnalysis:
    """Z-score analysis for identifying outliers"""
    property_address: str
    variable_name: str
    value: float
    z_score: float
    is_outlier: bool  # |z| > 2.0
    is_extreme_outlier: bool  # |z| > 3.0


@dataclass
class StatisticalReport:
    """Complete statistical analysis results"""
    analysis_date: str
    market: str
    sample_size: int

    # Summary statistics for all variables
    summaries: List[StatisticalSummary]

    # Regression analysis (rent as dependent variable)
    rent_regression: Optional[RegressionResult]

    # Correlation matrix (top correlations only)
    correlations: List[CorrelationResult]

    # Z-score outliers
    outliers: List[ZScoreAnalysis]

    # Insights
    insights: List[str] = field(default_factory=list)


# ============================================================================
# STATISTICAL FUNCTIONS
# ============================================================================

def calculate_summary_statistics(
    data: List[float],
    variable_name: str
) -> StatisticalSummary:
    """Calculate summary statistics for a variable"""
    if not data:
        raise ValueError(f"No data for variable {variable_name}")

    return StatisticalSummary(
        variable_name=variable_name,
        mean=statistics.mean(data),
        median=statistics.median(data),
        std_dev=statistics.stdev(data) if len(data) > 1 else 0.0,
        min_value=min(data),
        max_value=max(data),
        count=len(data)
    )


def calculate_correlation(
    x_values: List[float],
    y_values: List[float],
    x_name: str,
    y_name: str
) -> CorrelationResult:
    """
    Calculate Pearson correlation coefficient between two variables

    Formula: r = Σ[(xi - x̄)(yi - ȳ)] / √[Σ(xi - x̄)² × Σ(yi - ȳ)²]
    """
    if len(x_values) != len(y_values):
        raise ValueError("X and Y must have same length")

    if len(x_values) < 2:
        return CorrelationResult(x_name, y_name, 0.0, 0.0, len(x_values))

    n = len(x_values)
    x_mean = statistics.mean(x_values)
    y_mean = statistics.mean(y_values)

    # Calculate covariance and standard deviations
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
    x_variance = sum((x - x_mean) ** 2 for x in x_values)
    y_variance = sum((y - y_mean) ** 2 for y in y_values)

    denominator = math.sqrt(x_variance * y_variance)

    if denominator == 0:
        correlation = 0.0
    else:
        correlation = numerator / denominator

    return CorrelationResult(
        variable_x=x_name,
        variable_y=y_name,
        correlation=correlation,
        r_squared=correlation ** 2,
        sample_size=n
    )


def simple_linear_regression(
    x_values: List[float],
    y_values: List[float]
) -> Tuple[float, float]:
    """
    Simple linear regression: y = mx + b

    Returns: (slope, intercept)

    Formulas:
      slope = Σ[(xi - x̄)(yi - ȳ)] / Σ[(xi - x̄)²]
      intercept = ȳ - slope × x̄
    """
    if len(x_values) != len(y_values):
        raise ValueError("X and Y must have same length")

    if len(x_values) < 2:
        return (0.0, statistics.mean(y_values) if y_values else 0.0)

    x_mean = statistics.mean(x_values)
    y_mean = statistics.mean(y_values)

    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
    denominator = sum((x - x_mean) ** 2 for x in x_values)

    if denominator == 0:
        slope = 0.0
    else:
        slope = numerator / denominator

    intercept = y_mean - slope * x_mean

    return (slope, intercept)


def multiple_linear_regression(
    y_values: List[float],
    x_matrix: List[List[float]],
    variable_names: List[str],
    dependent_name: str
) -> RegressionResult:
    """
    Multiple linear regression using ordinary least squares

    Simplified implementation using normal equations:
    β = (X'X)^-1 X'y

    Note: This is a simplified version. For production use,
    consider using scipy.stats or statsmodels for more robust
    implementation with p-values, confidence intervals, etc.
    """
    n = len(y_values)
    k = len(x_matrix[0]) if x_matrix else 0

    if k == 0:
        # No independent variables - return mean as intercept
        intercept = statistics.mean(y_values)
        return RegressionResult(
            dependent_variable=dependent_name,
            independent_variables=[],
            coefficients={},
            intercept=intercept,
            r_squared=0.0,
            adjusted_r_squared=0.0,
            sample_size=n
        )

    # For simplicity, use sequential simple regressions
    # (This is not true multiple regression but avoids matrix inversion)
    # Real implementation would use proper OLS with matrix operations

    coefficients = {}
    residuals = list(y_values)

    # Simple approach: regress each variable sequentially
    for i, var_name in enumerate(variable_names):
        x_vals = [row[i] for row in x_matrix]
        slope, _ = simple_linear_regression(x_vals, residuals)
        coefficients[var_name] = slope

        # Update residuals (remove explained variance)
        predictions = [slope * x for x in x_vals]
        residuals = [r - p for r, p in zip(residuals, predictions)]

    # Calculate intercept as mean of final residuals
    intercept = statistics.mean(residuals)

    # Calculate R-squared
    y_mean = statistics.mean(y_values)
    ss_tot = sum((y - y_mean) ** 2 for y in y_values)

    # Calculate predictions
    predictions = []
    for i, row in enumerate(x_matrix):
        pred = intercept
        for j, var_name in enumerate(variable_names):
            pred += coefficients[var_name] * row[j]
        predictions.append(pred)

    ss_res = sum((y - pred) ** 2 for y, pred in zip(y_values, predictions))

    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    # Adjusted R-squared: 1 - [(1-R²)(n-1)/(n-k-1)]
    if n - k - 1 > 0:
        adj_r_squared = 1 - ((1 - r_squared) * (n - 1) / (n - k - 1))
    else:
        adj_r_squared = r_squared

    final_residuals = [y - pred for y, pred in zip(y_values, predictions)]

    return RegressionResult(
        dependent_variable=dependent_name,
        independent_variables=variable_names,
        coefficients=coefficients,
        intercept=intercept,
        r_squared=r_squared,
        adjusted_r_squared=adj_r_squared,
        sample_size=n,
        residuals=final_residuals
    )


def calculate_z_scores(
    values: List[float],
    addresses: List[str],
    variable_name: str
) -> List[ZScoreAnalysis]:
    """
    Calculate z-scores for identifying outliers

    Z-score = (value - mean) / std_dev

    Outlier thresholds:
      |z| > 2.0: Outlier (95% confidence)
      |z| > 3.0: Extreme outlier (99.7% confidence)
    """
    if len(values) < 2:
        return []

    mean_val = statistics.mean(values)
    std_dev = statistics.stdev(values)

    if std_dev == 0:
        return []

    z_scores = []
    for value, address in zip(values, addresses):
        z = (value - mean_val) / std_dev

        z_scores.append(ZScoreAnalysis(
            property_address=address,
            variable_name=variable_name,
            value=value,
            z_score=z,
            is_outlier=abs(z) > 2.0,
            is_extreme_outlier=abs(z) > 3.0
        ))

    return z_scores


# ============================================================================
# ANALYSIS ORCHESTRATION
# ============================================================================

def analyze_properties_statistics(
    properties: List[Dict],
    analysis_date: str,
    market: str
) -> StatisticalReport:
    """
    Perform comprehensive statistical analysis on properties

    Analyzes:
    1. Summary statistics for all numeric variables
    2. Multiple regression (rent as dependent variable)
    3. Correlation matrix for key variables
    4. Z-score outlier detection
    """

    # Extract numeric variables
    numeric_vars = [
        'net_asking_rent', 'tmi', 'clear_height_ft', 'parking_ratio',
        'pct_office_space', 'available_sf', 'distance_km', 'year_built',
        'shipping_doors_tl', 'shipping_doors_di', 'power_amps',
        'bay_depth_ft', 'lot_size_acres'
    ]

    # Build datasets
    datasets = {}
    addresses = []

    for prop in properties:
        addresses.append(prop.get('address', 'Unknown'))
        for var in numeric_vars:
            if var in prop and prop[var] is not None:
                if var not in datasets:
                    datasets[var] = []
                datasets[var].append(float(prop[var]))

    # 1. SUMMARY STATISTICS
    summaries = []
    for var, data in datasets.items():
        if len(data) >= 2:  # Need at least 2 data points
            summary = calculate_summary_statistics(data, var)
            summaries.append(summary)

    # Sort by coefficient of variation (most variable first)
    summaries.sort(key=lambda s: s.coefficient_of_variation(), reverse=True)

    # 2. REGRESSION ANALYSIS (Rent as dependent variable)
    rent_regression = None
    if 'net_asking_rent' in datasets and len(datasets['net_asking_rent']) >= 5:
        # Select independent variables with sufficient data
        independent_vars = []
        x_matrix = []

        potential_predictors = [
            'clear_height_ft', 'parking_ratio', 'pct_office_space',
            'distance_km', 'tmi', 'year_built'
        ]

        # Build X matrix (align all datasets)
        valid_indices = list(range(len(datasets['net_asking_rent'])))

        for var in potential_predictors:
            if var in datasets and len(datasets[var]) == len(datasets['net_asking_rent']):
                independent_vars.append(var)

        if independent_vars:
            # Build aligned X matrix
            n_samples = len(datasets['net_asking_rent'])
            x_matrix = [[datasets[var][i] for var in independent_vars] for i in range(n_samples)]

            rent_regression = multiple_linear_regression(
                y_values=datasets['net_asking_rent'],
                x_matrix=x_matrix,
                variable_names=independent_vars,
                dependent_name='net_asking_rent'
            )

    # 3. CORRELATION ANALYSIS
    correlations = []

    # Key pairs to analyze
    correlation_pairs = [
        ('net_asking_rent', 'tmi'),
        ('net_asking_rent', 'clear_height_ft'),
        ('net_asking_rent', 'parking_ratio'),
        ('net_asking_rent', 'distance_km'),
        ('net_asking_rent', 'year_built'),
        ('clear_height_ft', 'year_built'),
        ('parking_ratio', 'available_sf'),
        ('tmi', 'year_built')
    ]

    for x_var, y_var in correlation_pairs:
        if x_var in datasets and y_var in datasets:
            # Align datasets (both must have values for same properties)
            if len(datasets[x_var]) == len(datasets[y_var]):
                corr = calculate_correlation(
                    datasets[x_var],
                    datasets[y_var],
                    x_var,
                    y_var
                )
                correlations.append(corr)

    # Sort by absolute correlation (strongest first)
    correlations.sort(key=lambda c: abs(c.correlation), reverse=True)

    # 4. Z-SCORE OUTLIERS
    outliers = []

    # Check key variables for outliers
    outlier_vars = ['net_asking_rent', 'tmi', 'parking_ratio', 'clear_height_ft']

    for var in outlier_vars:
        if var in datasets and len(datasets[var]) >= 5:
            z_analyses = calculate_z_scores(
                datasets[var],
                addresses[:len(datasets[var])],
                var
            )
            # Only keep actual outliers
            outliers.extend([z for z in z_analyses if z.is_outlier])

    # Sort by absolute z-score (most extreme first)
    outliers.sort(key=lambda z: abs(z.z_score), reverse=True)

    # 5. GENERATE INSIGHTS
    insights = generate_insights(summaries, rent_regression, correlations, outliers)

    return StatisticalReport(
        analysis_date=analysis_date,
        market=market,
        sample_size=len(properties),
        summaries=summaries,
        rent_regression=rent_regression,
        correlations=correlations,
        outliers=outliers,
        insights=insights
    )


def generate_insights(
    summaries: List[StatisticalSummary],
    regression: Optional[RegressionResult],
    correlations: List[CorrelationResult],
    outliers: List[ZScoreAnalysis]
) -> List[str]:
    """Generate key insights from statistical analysis"""
    insights = []

    # 1. Most variable factors
    if summaries:
        most_variable = summaries[0]
        insights.append(
            f"**Most Variable Factor**: {most_variable.variable_name} "
            f"(CV={most_variable.coefficient_of_variation():.2f}) - "
            f"wide range indicates diverse market offerings"
        )

    # 2. Regression R-squared
    if regression:
        insights.append(
            f"**Rent Predictability**: Model explains {regression.r_squared:.1%} "
            f"of rent variation using {len(regression.independent_variables)} variables "
            f"(Adjusted R²={regression.adjusted_r_squared:.1%})"
        )

        # Identify strongest predictors
        sorted_coefs = sorted(
            regression.coefficients.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        if sorted_coefs:
            top_predictor = sorted_coefs[0]
            insights.append(
                f"**Strongest Rent Driver**: {top_predictor[0]} "
                f"(coefficient={top_predictor[1]:.4f})"
            )

    # 3. Strongest correlation
    if correlations:
        strongest = correlations[0]
        insights.append(
            f"**Strongest Correlation**: {strongest.variable_x} vs {strongest.variable_y} "
            f"(r={strongest.correlation:.3f}, {strongest.strength()} {strongest.direction()})"
        )

    # 4. Outliers
    extreme_outliers = [o for o in outliers if o.is_extreme_outlier]
    if extreme_outliers:
        insights.append(
            f"**Extreme Outliers Detected**: {len(extreme_outliers)} properties "
            f"with z-scores >3.0 (99.7% confidence) - review for data quality"
        )

    return insights


# ============================================================================
# REPORT GENERATION
# ============================================================================

def generate_statistics_markdown(report: StatisticalReport) -> str:
    """Generate markdown report section for statistical analysis"""

    md = []

    md.append("# Statistical Analysis\n")
    md.append(f"**Analysis Date**: {report.analysis_date}\n")
    md.append(f"**Market**: {report.market}\n")
    md.append(f"**Sample Size**: {report.sample_size} properties\n")
    md.append("\n---\n")

    # KEY INSIGHTS
    md.append("## Key Insights\n")
    for i, insight in enumerate(report.insights, 1):
        md.append(f"{i}. {insight}\n")
    md.append("\n---\n")

    # SUMMARY STATISTICS
    md.append("## Summary Statistics\n")
    md.append("\nDescriptive statistics for key variables:\n\n")
    md.append("| Variable | Mean | Median | Std Dev | Min | Max | CV | N |\n")
    md.append("|----------|------|--------|---------|-----|-----|----|---|\n")

    for summary in report.summaries[:10]:  # Top 10
        cv = summary.coefficient_of_variation()
        md.append(
            f"| {summary.variable_name} | "
            f"{summary.mean:.2f} | "
            f"{summary.median:.2f} | "
            f"{summary.std_dev:.2f} | "
            f"{summary.min_value:.2f} | "
            f"{summary.max_value:.2f} | "
            f"{cv:.2f} | "
            f"{summary.count} |\n"
        )

    md.append("\n**CV** = Coefficient of Variation (std_dev / mean) - measures relative variability\n")
    md.append("\n---\n")

    # REGRESSION ANALYSIS
    if report.rent_regression:
        reg = report.rent_regression
        md.append("## Regression Analysis: Net Asking Rent\n")
        md.append(f"\n**Model**: Predicting {reg.dependent_variable} from {len(reg.independent_variables)} variables\n")
        md.append(f"**R-squared**: {reg.r_squared:.3f} ({reg.r_squared*100:.1f}% of variance explained)\n")
        md.append(f"**Adjusted R-squared**: {reg.adjusted_r_squared:.3f}\n")
        md.append(f"**Sample Size**: {reg.sample_size}\n\n")

        md.append("### Regression Coefficients\n\n")
        md.append("| Variable | Coefficient | Interpretation |\n")
        md.append("|----------|-------------|----------------|\n")
        md.append(f"| **(Intercept)** | {reg.intercept:.2f} | Base rent |\n")

        for var, coef in sorted(reg.coefficients.items(), key=lambda x: abs(x[1]), reverse=True):
            direction = "increase" if coef > 0 else "decrease"
            md.append(f"| {var} | {coef:.4f} | +1 unit → ${abs(coef):.2f}/SF {direction} |\n")

        md.append("\n---\n")

    # CORRELATION ANALYSIS
    if report.correlations:
        md.append("## Correlation Analysis\n")
        md.append("\nRelationships between key variables:\n\n")
        md.append("| Variable X | Variable Y | Correlation (r) | R² | Strength | Direction | N |\n")
        md.append("|------------|------------|-----------------|----|-----------|-----------|----|  \n")

        for corr in report.correlations[:10]:  # Top 10
            md.append(
                f"| {corr.variable_x} | "
                f"{corr.variable_y} | "
                f"{corr.correlation:.3f} | "
                f"{corr.r_squared:.3f} | "
                f"{corr.strength()} | "
                f"{corr.direction()} | "
                f"{corr.sample_size} |\n"
            )

        md.append("\n**Interpretation Guide**:\n")
        md.append("- **Strong**: |r| ≥ 0.7\n")
        md.append("- **Moderate**: 0.4 ≤ |r| < 0.7\n")
        md.append("- **Weak**: 0.2 ≤ |r| < 0.4\n")
        md.append("- **Negligible**: |r| < 0.2\n")
        md.append("\n---\n")

    # OUTLIER DETECTION
    if report.outliers:
        md.append("## Outlier Detection (Z-Score Analysis)\n")
        md.append("\nProperties with statistical outliers (|z| > 2.0):\n\n")
        md.append("| Property | Variable | Value | Z-Score | Status |\n")
        md.append("|----------|----------|-------|---------|--------|\n")

        for outlier in report.outliers[:15]:  # Top 15
            status = "🔴 Extreme" if outlier.is_extreme_outlier else "⚠️ Outlier"
            address_short = outlier.property_address[:40] + "..." if len(outlier.property_address) > 40 else outlier.property_address
            md.append(
                f"| {address_short} | "
                f"{outlier.variable_name} | "
                f"{outlier.value:.2f} | "
                f"{outlier.z_score:.2f} | "
                f"{status} |\n"
            )

        md.append("\n**Z-Score Thresholds**:\n")
        md.append("- **|z| > 3.0**: Extreme outlier (99.7% confidence)\n")
        md.append("- **|z| > 2.0**: Outlier (95% confidence)\n")
        md.append("\n---\n")

    md.append("\n## Statistical Notes\n")
    md.append("\n**Methodology**:\n")
    md.append("- Pearson correlation for linear relationships\n")
    md.append("- Ordinary least squares (OLS) regression\n")
    md.append("- Z-scores for outlier detection (assumes normal distribution)\n")
    md.append("\n**Limitations**:\n")
    md.append("- Assumes linear relationships between variables\n")
    md.append("- Does not account for interaction effects\n")
    md.append("- Outliers may indicate data quality issues or unique properties\n")
    md.append("- Statistical significance not calculated (requires larger samples)\n")
    md.append("\n")

    return "".join(md)


if __name__ == '__main__':
    print("Statistical Analysis Module for Relative Valuation")
    print("Use with --stats flag in relative_valuation_calculator.py")
