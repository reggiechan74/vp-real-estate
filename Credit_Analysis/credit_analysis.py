"""
Tenant Credit Analysis Calculator

Performs comprehensive credit analysis for commercial real estate tenants including:
- Financial ratio analysis (15+ ratios)
- Weighted credit scoring (100-point scale)
- Credit rating assignment (A-F)
- Default probability estimation
- Expected loss calculation
- Risk-adjusted security recommendations
- Multi-year trend analysis

Key Features:
- Liquidity, leverage, profitability, and rent coverage ratios
- Weighted scoring algorithm with financial, business, credit, and lease factors
- Statistical default probabilities by rating
- Expected loss = PD × Exposure × LGD
- Security step-down schedules
- Red flag identification

Author: Claude Code
Created: 2025-10-30
GitHub Issue: #6
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Literal
from dataclasses import dataclass, field

from Shared_Utils.financial_utils import calculate_financial_ratios, safe_divide


@dataclass
class FinancialData:
    """
    Financial statement data for a single year.
    """
    year: int

    # Balance sheet
    current_assets: float = 0.0
    total_assets: float = 0.0
    inventory: float = 0.0
    cash_and_equivalents: float = 0.0
    current_liabilities: float = 0.0
    total_liabilities: float = 0.0
    shareholders_equity: float = 0.0

    # Income statement
    revenue: float = 0.0
    gross_profit: float = 0.0
    ebit: float = 0.0
    ebitda: float = 0.0
    net_income: float = 0.0
    interest_expense: float = 0.0

    # Lease-specific
    annual_rent: float = 0.0


@dataclass
class CreditInputs:
    """
    Input parameters for tenant credit analysis.
    """
    # Financial data (3 years recommended)
    financial_data: List[FinancialData]  # Most recent first

    # Tenant information
    tenant_name: str = "Tenant"
    industry: str = "Unknown"
    years_in_business: int = 0

    # Credit history
    credit_score: Optional[int] = None  # 300-850 scale
    payment_history: Literal['excellent', 'good', 'fair', 'poor'] = 'good'

    # Lease terms
    lease_term_years: int = 5
    use_criticality: Literal['mission-critical', 'important', 'discretionary'] = 'important'

    # Industry characteristics
    industry_stability: Literal['stable', 'moderate', 'volatile'] = 'moderate'

    # Security currently held
    current_security: float = 0.0  # Rent deposit or LC amount
    security_type: str = "None"


@dataclass
class CreditScore:
    """
    Credit scoring breakdown.
    """
    # Component scores
    financial_strength_score: float  # 0-40
    business_quality_score: float    # 0-30
    credit_history_score: float      # 0-20
    lease_specific_score: float      # 0-10

    # Total
    total_score: float               # 0-100

    # Rating
    credit_rating: Literal['A', 'B', 'C', 'D', 'F']

    # Component details
    score_breakdown: Dict[str, float]


@dataclass
class RiskAssessment:
    """
    Risk assessment results.
    """
    # Probability and loss
    probability_of_default: float    # 0-1
    exposure_at_default: float       # Total rent over term
    loss_given_default: float        # 0-1 (1 - recovery rate)
    expected_loss: float             # Dollar amount

    # Security recommendations
    recommended_security: float      # Dollar amount
    security_coverage_ratio: float   # Security / Expected loss
    security_type_recommendation: str

    # Step-down schedule
    stepdown_schedule: pd.DataFrame


@dataclass
class TrendAnalysis:
    """
    Multi-year trend analysis.
    """
    # Trends
    revenue_trend: Literal['improving', 'stable', 'deteriorating']
    profitability_trend: Literal['improving', 'stable', 'deteriorating']
    liquidity_trend: Literal['improving', 'stable', 'deteriorating']
    leverage_trend: Literal['improving', 'stable', 'deteriorating']

    # Year-over-year changes
    yoy_revenue_change_pct: List[float]
    yoy_income_change_pct: List[float]
    yoy_ratio_changes: Dict[str, List[float]]

    # Overall assessment
    overall_trend: Literal['improving', 'stable', 'deteriorating']


@dataclass
class CreditAnalysisResult:
    """
    Complete credit analysis results.
    """
    # Input data
    tenant_name: str
    analysis_date: str

    # Financial ratios (most recent year)
    financial_ratios: Dict[str, Optional[float]]

    # Credit scoring
    credit_score: CreditScore

    # Risk assessment
    risk_assessment: RiskAssessment

    # Trend analysis
    trend_analysis: TrendAnalysis

    # Red flags
    red_flags: List[str]

    # Recommendation
    approval_recommendation: Literal['APPROVE', 'APPROVE_WITH_CONDITIONS', 'DECLINE']
    recommendation_notes: str


# ============================================================================
# FINANCIAL RATIO THRESHOLDS
# ============================================================================

# Target thresholds for ratio scoring
RATIO_THRESHOLDS = {
    # Liquidity (higher is better)
    'current_ratio': {'excellent': 2.0, 'good': 1.5, 'fair': 1.2, 'poor': 1.0},
    'quick_ratio': {'excellent': 1.5, 'good': 1.0, 'fair': 0.8, 'poor': 0.5},
    'cash_ratio': {'excellent': 0.5, 'good': 0.3, 'fair': 0.2, 'poor': 0.1},

    # Leverage (lower is better)
    'debt_to_equity': {'excellent': 0.5, 'good': 1.0, 'fair': 1.5, 'poor': 2.0},
    'debt_to_assets': {'excellent': 0.3, 'good': 0.5, 'fair': 0.7, 'poor': 0.8},

    # Profitability (higher is better)
    'net_profit_margin': {'excellent': 0.15, 'good': 0.10, 'fair': 0.05, 'poor': 0.02},
    'roa': {'excellent': 0.10, 'good': 0.05, 'fair': 0.02, 'poor': 0.01},
    'roe': {'excellent': 0.20, 'good': 0.15, 'fair': 0.10, 'poor': 0.05},

    # Rent coverage (higher is better)
    'ebitda_to_rent': {'excellent': 3.0, 'good': 2.0, 'fair': 1.5, 'poor': 1.0},
    'rent_to_revenue': {'excellent': 0.05, 'good': 0.08, 'fair': 0.12, 'poor': 0.15},  # Lower is better!

    # Interest coverage (higher is better)
    'interest_coverage': {'excellent': 5.0, 'good': 3.0, 'fair': 2.0, 'poor': 1.5},
}

# Default probabilities by credit rating (5-year cumulative)
DEFAULT_PROBABILITIES = {
    'A': 0.025,   # 2.5% - Excellent
    'B': 0.10,    # 10% - Good
    'C': 0.225,   # 22.5% - Moderate
    'D': 0.40,    # 40% - Weak
    'F': 0.60     # 60% - Poor
}


# ============================================================================
# SCORING FUNCTIONS
# ============================================================================

def score_ratio(ratio_value: Optional[float], ratio_name: str, reverse: bool = False) -> float:
    """
    Score a financial ratio on a 0-10 scale based on thresholds.

    Args:
        ratio_value: The ratio value
        ratio_name: Name of the ratio
        reverse: True if lower values are better (e.g., debt ratios)

    Returns:
        Score from 0-10
    """
    if ratio_value is None:
        return 0.0

    if ratio_name not in RATIO_THRESHOLDS:
        return 5.0  # Default mid-score for unknown ratios

    thresholds = RATIO_THRESHOLDS[ratio_name]

    if reverse:
        # Lower is better (debt ratios)
        if ratio_value <= thresholds['excellent']:
            return 10.0
        elif ratio_value <= thresholds['good']:
            return 8.0
        elif ratio_value <= thresholds['fair']:
            return 5.0
        elif ratio_value <= thresholds['poor']:
            return 3.0
        else:
            return 0.0
    else:
        # Higher is better (most ratios)
        # Exception: rent_to_revenue (lower is better)
        if ratio_name == 'rent_to_revenue':
            if ratio_value <= thresholds['excellent']:
                return 10.0
            elif ratio_value <= thresholds['good']:
                return 8.0
            elif ratio_value <= thresholds['fair']:
                return 5.0
            elif ratio_value <= thresholds['poor']:
                return 3.0
            else:
                return 0.0
        else:
            if ratio_value >= thresholds['excellent']:
                return 10.0
            elif ratio_value >= thresholds['good']:
                return 8.0
            elif ratio_value >= thresholds['fair']:
                return 5.0
            elif ratio_value >= thresholds['poor']:
                return 3.0
            else:
                return 0.0


def calculate_credit_score(
    ratios: Dict[str, Optional[float]],
    inputs: CreditInputs
) -> CreditScore:
    """
    Calculate weighted credit score (0-100 scale).

    Args:
        ratios: Financial ratios dictionary
        inputs: Credit inputs

    Returns:
        CreditScore with breakdown
    """
    breakdown = {}

    # ========================================================================
    # Financial Strength (40 points)
    # ========================================================================

    # Current ratio (0-10)
    current_ratio_score = score_ratio(ratios.get('current_ratio'), 'current_ratio')
    breakdown['current_ratio'] = current_ratio_score

    # Debt-to-equity (0-10, reverse scoring)
    debt_equity_score = score_ratio(ratios.get('debt_to_equity'), 'debt_to_equity', reverse=True)
    breakdown['debt_to_equity'] = debt_equity_score

    # Profitability - average of margin and ROE (0-10)
    margin_score = score_ratio(ratios.get('net_profit_margin'), 'net_profit_margin')
    roe_score = score_ratio(ratios.get('roe'), 'roe')
    profitability_score = (margin_score + roe_score) / 2
    breakdown['profitability'] = profitability_score

    # EBITDA-to-rent (0-10)
    ebitda_rent_score = score_ratio(ratios.get('ebitda_to_rent'), 'ebitda_to_rent')
    breakdown['ebitda_to_rent'] = ebitda_rent_score

    financial_strength = current_ratio_score + debt_equity_score + profitability_score + ebitda_rent_score

    # ========================================================================
    # Business Quality (30 points)
    # ========================================================================

    # Years in business (0-10)
    if inputs.years_in_business >= 10:
        years_score = 10.0
    elif inputs.years_in_business >= 5:
        years_score = 7.0
    elif inputs.years_in_business >= 2:
        years_score = 4.0
    else:
        years_score = 0.0
    breakdown['years_in_business'] = years_score

    # Industry stability (0-10)
    industry_map = {'stable': 10.0, 'moderate': 6.0, 'volatile': 3.0}
    industry_score = industry_map.get(inputs.industry_stability, 6.0)
    breakdown['industry_stability'] = industry_score

    # Financial trend (0-10) - will be calculated from trend analysis
    # For now, use placeholder
    trend_score = 6.0  # Will be updated if multi-year data available
    breakdown['financial_trend'] = trend_score

    business_quality = years_score + industry_score + trend_score

    # ========================================================================
    # Credit History (20 points)
    # ========================================================================

    # Payment history (0-10)
    payment_map = {'excellent': 10.0, 'good': 7.0, 'fair': 4.0, 'poor': 0.0}
    payment_score = payment_map.get(inputs.payment_history, 7.0)
    breakdown['payment_history'] = payment_score

    # Credit score (0-10)
    if inputs.credit_score:
        if inputs.credit_score >= 750:
            credit_score_points = 10.0
        elif inputs.credit_score >= 650:
            credit_score_points = 7.0
        elif inputs.credit_score >= 550:
            credit_score_points = 4.0
        else:
            credit_score_points = 0.0
    else:
        credit_score_points = 5.0  # Default if not provided
    breakdown['credit_score'] = credit_score_points

    credit_history = payment_score + credit_score_points

    # ========================================================================
    # Lease-Specific (10 points)
    # ========================================================================

    # Rent as % of revenue (0-5, lower is better)
    rent_revenue = ratios.get('rent_to_revenue', 0)
    if rent_revenue and rent_revenue <= 0.05:
        rent_pct_score = 5.0
    elif rent_revenue and rent_revenue <= 0.10:
        rent_pct_score = 3.0
    else:
        rent_pct_score = 0.0
    breakdown['rent_pct_of_revenue'] = rent_pct_score

    # Use criticality (0-5)
    use_map = {'mission-critical': 5.0, 'important': 3.0, 'discretionary': 0.0}
    use_score = use_map.get(inputs.use_criticality, 3.0)
    breakdown['use_criticality'] = use_score

    lease_specific = rent_pct_score + use_score

    # ========================================================================
    # Total Score and Rating
    # ========================================================================

    total_score = financial_strength + business_quality + credit_history + lease_specific

    # Assign credit rating
    if total_score >= 80:
        rating = 'A'
    elif total_score >= 60:
        rating = 'B'
    elif total_score >= 40:
        rating = 'C'
    elif total_score >= 20:
        rating = 'D'
    else:
        rating = 'F'

    return CreditScore(
        financial_strength_score=financial_strength,
        business_quality_score=business_quality,
        credit_history_score=credit_history,
        lease_specific_score=lease_specific,
        total_score=total_score,
        credit_rating=rating,
        score_breakdown=breakdown
    )


# ============================================================================
# RISK ASSESSMENT
# ============================================================================

def calculate_risk_assessment(
    credit_score: CreditScore,
    inputs: CreditInputs
) -> RiskAssessment:
    """
    Calculate default probability, expected loss, and security requirements.

    Args:
        credit_score: Credit score result
        inputs: Credit inputs

    Returns:
        RiskAssessment with probability, loss, and security recommendations
    """
    # Get most recent financial data
    recent_financials = inputs.financial_data[0] if inputs.financial_data else None

    # Probability of default based on credit rating
    pd = DEFAULT_PROBABILITIES.get(credit_score.credit_rating, 0.30)

    # Exposure at default = Total rent over lease term
    annual_rent = recent_financials.annual_rent if recent_financials else 0.0
    ead = annual_rent * inputs.lease_term_years

    # Loss given default (1 - recovery rate)
    # Recovery comes from security + re-leasing
    # Assume 30-50% recovery depending on rating
    recovery_map = {'A': 0.50, 'B': 0.40, 'C': 0.30, 'D': 0.20, 'F': 0.10}
    recovery_rate = recovery_map.get(credit_score.credit_rating, 0.30)
    lgd = 1 - recovery_rate

    # Expected loss = PD × EAD × LGD
    expected_loss = pd * ead * lgd

    # Security recommendation
    # Target: Cover expected loss + cushion + re-leasing costs

    # Cushion: 1-2 months rent based on rating
    cushion_months = {'A': 0, 'B': 1, 'C': 1.5, 'D': 2, 'F': 3}
    cushion = cushion_months.get(credit_score.credit_rating, 1) * annual_rent / 12

    # Re-leasing costs: Commission + downtime + TI
    # Estimate: 6-12 months rent depending on market
    releasing_months = {'A': 3, 'B': 6, 'C': 9, 'D': 12, 'F': 15}
    releasing_costs = releasing_months.get(credit_score.credit_rating, 6) * annual_rent / 12

    # Total recommended security
    recommended_security = expected_loss + cushion + releasing_costs

    # Coverage ratio
    if expected_loss > 0:
        coverage_ratio = recommended_security / expected_loss
    else:
        coverage_ratio = 0.0

    # Security type recommendation
    if credit_score.credit_rating in ['A', 'B']:
        if recommended_security <= annual_rent:
            security_type = f"Rent Deposit: ${recommended_security:,.0f} ({recommended_security/(annual_rent/12):.1f} months)"
        else:
            security_type = f"Letter of Credit: ${recommended_security:,.0f} (step-down after Year 2)"
    else:
        security_type = f"Letter of Credit: ${recommended_security:,.0f} (step-down after Year 3)"

    # Generate step-down schedule
    stepdown = generate_stepdown_schedule(
        initial_security=recommended_security,
        annual_rent=annual_rent,
        lease_term=inputs.lease_term_years,
        credit_rating=credit_score.credit_rating
    )

    return RiskAssessment(
        probability_of_default=pd,
        exposure_at_default=ead,
        loss_given_default=lgd,
        expected_loss=expected_loss,
        recommended_security=recommended_security,
        security_coverage_ratio=coverage_ratio,
        security_type_recommendation=security_type,
        stepdown_schedule=stepdown
    )


def generate_stepdown_schedule(
    initial_security: float,
    annual_rent: float,
    lease_term: int,
    credit_rating: str
) -> pd.DataFrame:
    """
    Generate security step-down schedule.

    Args:
        initial_security: Initial security amount
        annual_rent: Annual rent
        lease_term: Lease term in years
        credit_rating: Credit rating

    Returns:
        DataFrame with step-down schedule
    """
    schedule = []

    # Step-down strategy based on rating
    if credit_rating in ['A', 'B']:
        # Faster step-down for better credits
        for year in range(lease_term + 1):
            if year == 0:
                amount = initial_security
            elif year <= 2:
                amount = initial_security
            elif year <= 4:
                amount = initial_security * 0.75
            else:
                amount = initial_security * 0.50

            schedule.append({
                'Year': year,
                'Security_Required': amount,
                'Months_Rent_Equivalent': amount / (annual_rent / 12) if annual_rent > 0 else 0
            })
    else:
        # Slower step-down for weaker credits
        for year in range(lease_term + 1):
            if year == 0:
                amount = initial_security
            elif year <= 3:
                amount = initial_security
            else:
                amount = initial_security * 0.75

            schedule.append({
                'Year': year,
                'Security_Required': amount,
                'Months_Rent_Equivalent': amount / (annual_rent / 12) if annual_rent > 0 else 0
            })

    df = pd.DataFrame(schedule)

    # Round
    df['Security_Required'] = df['Security_Required'].round(2)
    df['Months_Rent_Equivalent'] = df['Months_Rent_Equivalent'].round(1)

    return df


# ============================================================================
# TREND ANALYSIS
# ============================================================================

def analyze_trends(inputs: CreditInputs) -> TrendAnalysis:
    """
    Analyze multi-year financial trends.

    Args:
        inputs: Credit inputs with multi-year financials

    Returns:
        TrendAnalysis with trend directions
    """
    if len(inputs.financial_data) < 2:
        # Not enough data for trend analysis
        return TrendAnalysis(
            revenue_trend='stable',
            profitability_trend='stable',
            liquidity_trend='stable',
            leverage_trend='stable',
            yoy_revenue_change_pct=[],
            yoy_income_change_pct=[],
            yoy_ratio_changes={},
            overall_trend='stable'
        )

    # Sort by year (most recent first)
    sorted_data = sorted(inputs.financial_data, key=lambda x: x.year, reverse=True)

    # Calculate year-over-year changes
    yoy_revenue = []
    yoy_income = []

    for i in range(len(sorted_data) - 1):
        current = sorted_data[i]
        previous = sorted_data[i + 1]

        # Revenue change
        if previous.revenue > 0:
            rev_change = (current.revenue - previous.revenue) / previous.revenue
            yoy_revenue.append(rev_change)

        # Income change
        if previous.net_income != 0:
            income_change = (current.net_income - previous.net_income) / abs(previous.net_income)
            yoy_income.append(income_change)

    # Classify trends
    revenue_trend = classify_trend(yoy_revenue)
    profitability_trend = classify_trend(yoy_income)

    # Calculate ratios for each year to see liquidity/leverage trends
    ratio_changes = {}

    # For simplicity, just check most recent vs oldest
    if len(sorted_data) >= 2:
        recent_ratios = calculate_financial_ratios({
            'current_assets': sorted_data[0].current_assets,
            'current_liabilities': sorted_data[0].current_liabilities,
            'total_liabilities': sorted_data[0].total_liabilities,
            'shareholders_equity': sorted_data[0].shareholders_equity,
            'revenue': sorted_data[0].revenue,
            'net_income': sorted_data[0].net_income,
            'ebitda': sorted_data[0].ebitda,
            'annual_rent': sorted_data[0].annual_rent,
            'total_assets': sorted_data[0].total_assets
        })

        old_ratios = calculate_financial_ratios({
            'current_assets': sorted_data[-1].current_assets,
            'current_liabilities': sorted_data[-1].current_liabilities,
            'total_liabilities': sorted_data[-1].total_liabilities,
            'shareholders_equity': sorted_data[-1].shareholders_equity,
            'revenue': sorted_data[-1].revenue,
            'net_income': sorted_data[-1].net_income,
            'ebitda': sorted_data[-1].ebitda,
            'annual_rent': sorted_data[-1].annual_rent,
            'total_assets': sorted_data[-1].total_assets
        })

        # Liquidity trend (current ratio)
        if old_ratios.get('current_ratio') and recent_ratios.get('current_ratio'):
            liquidity_change = recent_ratios['current_ratio'] - old_ratios['current_ratio']
            liquidity_trend = 'improving' if liquidity_change > 0.1 else ('deteriorating' if liquidity_change < -0.1 else 'stable')
        else:
            liquidity_trend = 'stable'

        # Leverage trend (debt-to-equity, lower is better)
        if old_ratios.get('debt_to_equity') and recent_ratios.get('debt_to_equity'):
            leverage_change = old_ratios['debt_to_equity'] - recent_ratios['debt_to_equity']
            leverage_trend = 'improving' if leverage_change > 0.1 else ('deteriorating' if leverage_change < -0.1 else 'stable')
        else:
            leverage_trend = 'stable'
    else:
        liquidity_trend = 'stable'
        leverage_trend = 'stable'

    # Overall trend
    trends = [revenue_trend, profitability_trend, liquidity_trend, leverage_trend]
    improving_count = trends.count('improving')
    deteriorating_count = trends.count('deteriorating')

    if improving_count >= 3:
        overall = 'improving'
    elif deteriorating_count >= 3:
        overall = 'deteriorating'
    else:
        overall = 'stable'

    return TrendAnalysis(
        revenue_trend=revenue_trend,
        profitability_trend=profitability_trend,
        liquidity_trend=liquidity_trend,
        leverage_trend=leverage_trend,
        yoy_revenue_change_pct=yoy_revenue,
        yoy_income_change_pct=yoy_income,
        yoy_ratio_changes=ratio_changes,
        overall_trend=overall
    )


def classify_trend(yoy_changes: List[float]) -> Literal['improving', 'stable', 'deteriorating']:
    """
    Classify trend based on year-over-year changes.

    Args:
        yoy_changes: List of YoY percentage changes

    Returns:
        Trend classification
    """
    if not yoy_changes:
        return 'stable'

    avg_change = np.mean(yoy_changes)

    if avg_change > 0.05:  # >5% average growth
        return 'improving'
    elif avg_change < -0.05:  # >5% average decline
        return 'deteriorating'
    else:
        return 'stable'


# ============================================================================
# RED FLAGS
# ============================================================================

def identify_red_flags(
    ratios: Dict[str, Optional[float]],
    credit_score: CreditScore,
    trend: TrendAnalysis,
    inputs: CreditInputs
) -> List[str]:
    """
    Identify credit red flags.

    Args:
        ratios: Financial ratios
        credit_score: Credit score result
        trend: Trend analysis
        inputs: Credit inputs

    Returns:
        List of red flag descriptions
    """
    flags = []

    # Liquidity red flags
    current_ratio = ratios.get('current_ratio', 0)
    if current_ratio and current_ratio < 1.0:
        flags.append(f"⚠ Current ratio below 1.0 ({current_ratio:.2f}) - liquidity concerns")

    # Leverage red flags
    debt_equity = ratios.get('debt_to_equity', 0)
    if debt_equity and debt_equity > 2.0:
        flags.append(f"⚠ Debt-to-equity above 2.0 ({debt_equity:.2f}) - high leverage")

    # Profitability red flags
    net_margin = ratios.get('net_profit_margin', 0)
    if net_margin and net_margin < 0:
        flags.append(f"⚠ Negative profit margin ({net_margin:.1%}) - unprofitable")

    # Rent coverage red flags
    ebitda_rent = ratios.get('ebitda_to_rent', 0)
    if ebitda_rent and ebitda_rent < 1.5:
        flags.append(f"⚠ EBITDA/Rent below 1.5x ({ebitda_rent:.2f}x) - weak rent coverage")

    rent_revenue = ratios.get('rent_to_revenue', 0)
    if rent_revenue and rent_revenue > 0.15:
        flags.append(f"⚠ Rent exceeds 15% of revenue ({rent_revenue:.1%}) - high occupancy cost")

    # Trend red flags
    if trend.revenue_trend == 'deteriorating':
        flags.append("⚠ Revenue declining year-over-year")

    if trend.profitability_trend == 'deteriorating':
        flags.append("⚠ Profitability declining year-over-year")

    # Credit score red flags
    if credit_score.total_score < 40:
        flags.append(f"⚠ Low credit score ({credit_score.total_score:.0f}/100) - high risk")

    # Years in business
    if inputs.years_in_business < 2:
        flags.append("⚠ Less than 2 years in business - startup risk")

    # Payment history
    if inputs.payment_history in ['fair', 'poor']:
        flags.append("⚠ Poor payment history - collection risk")

    return flags


# ============================================================================
# MAIN ANALYSIS FUNCTION
# ============================================================================

def analyze_tenant_credit(inputs: CreditInputs) -> CreditAnalysisResult:
    """
    Perform complete tenant credit analysis.

    Args:
        inputs: CreditInputs with financial data

    Returns:
        CreditAnalysisResult with complete analysis
    """
    from datetime import datetime

    # Get most recent financial data
    if not inputs.financial_data:
        raise ValueError("No financial data provided")

    recent_financials = inputs.financial_data[0]

    # Calculate financial ratios
    ratios = calculate_financial_ratios({
        'current_assets': recent_financials.current_assets,
        'total_assets': recent_financials.total_assets,
        'inventory': recent_financials.inventory,
        'cash_and_equivalents': recent_financials.cash_and_equivalents,
        'current_liabilities': recent_financials.current_liabilities,
        'total_liabilities': recent_financials.total_liabilities,
        'shareholders_equity': recent_financials.shareholders_equity,
        'revenue': recent_financials.revenue,
        'gross_profit': recent_financials.gross_profit,
        'ebit': recent_financials.ebit,
        'ebitda': recent_financials.ebitda,
        'net_income': recent_financials.net_income,
        'interest_expense': recent_financials.interest_expense,
        'annual_rent': recent_financials.annual_rent
    })

    # Calculate credit score
    credit_score = calculate_credit_score(ratios, inputs)

    # Calculate risk assessment
    risk_assessment = calculate_risk_assessment(credit_score, inputs)

    # Analyze trends
    trend_analysis = analyze_trends(inputs)

    # Update credit score with trend
    if trend_analysis.overall_trend == 'improving':
        credit_score.score_breakdown['financial_trend'] = 10.0
        credit_score.business_quality_score += 4.0  # Adjust from placeholder
        credit_score.total_score += 4.0
    elif trend_analysis.overall_trend == 'deteriorating':
        credit_score.score_breakdown['financial_trend'] = 0.0
        credit_score.business_quality_score -= 6.0  # Adjust from placeholder
        credit_score.total_score -= 6.0

    # Re-assign rating after trend adjustment
    if credit_score.total_score >= 80:
        credit_score.credit_rating = 'A'
    elif credit_score.total_score >= 60:
        credit_score.credit_rating = 'B'
    elif credit_score.total_score >= 40:
        credit_score.credit_rating = 'C'
    elif credit_score.total_score >= 20:
        credit_score.credit_rating = 'D'
    else:
        credit_score.credit_rating = 'F'

    # Identify red flags
    red_flags = identify_red_flags(ratios, credit_score, trend_analysis, inputs)

    # Generate recommendation
    recommendation, notes = generate_approval_recommendation(
        credit_score,
        risk_assessment,
        red_flags,
        inputs
    )

    return CreditAnalysisResult(
        tenant_name=inputs.tenant_name,
        analysis_date=datetime.now().strftime('%Y-%m-%d'),
        financial_ratios=ratios,
        credit_score=credit_score,
        risk_assessment=risk_assessment,
        trend_analysis=trend_analysis,
        red_flags=red_flags,
        approval_recommendation=recommendation,
        recommendation_notes=notes
    )


def generate_approval_recommendation(
    credit_score: CreditScore,
    risk: RiskAssessment,
    red_flags: List[str],
    inputs: CreditInputs
) -> Tuple[Literal['APPROVE', 'APPROVE_WITH_CONDITIONS', 'DECLINE'], str]:
    """
    Generate approval recommendation.

    Args:
        credit_score: Credit score
        risk: Risk assessment
        red_flags: List of red flags
        inputs: Credit inputs

    Returns:
        Tuple of (recommendation, notes)
    """
    notes = []

    # Rating-based decision
    if credit_score.credit_rating in ['A', 'B']:
        if len(red_flags) == 0:
            recommendation = 'APPROVE'
            notes.append(f"Excellent/Good credit rating ({credit_score.credit_rating}, {credit_score.total_score:.0f}/100).")
        else:
            recommendation = 'APPROVE_WITH_CONDITIONS'
            notes.append(f"Good credit rating ({credit_score.credit_rating}) but {len(red_flags)} red flags identified.")
    elif credit_score.credit_rating == 'C':
        recommendation = 'APPROVE_WITH_CONDITIONS'
        notes.append(f"Moderate credit rating ({credit_score.credit_rating}, {credit_score.total_score:.0f}/100).")
    else:
        recommendation = 'DECLINE'
        notes.append(f"Weak credit rating ({credit_score.credit_rating}, {credit_score.total_score:.0f}/100).")

    # Security assessment
    if risk.recommended_security > inputs.current_security:
        shortfall = risk.recommended_security - inputs.current_security
        notes.append(f"Require additional security of ${shortfall:,.0f}.")
        notes.append(f"Total recommended security: ${risk.recommended_security:,.0f}.")
        notes.append(f"{risk.security_type_recommendation}")

        if recommendation == 'APPROVE':
            recommendation = 'APPROVE_WITH_CONDITIONS'
    else:
        notes.append(f"Current security of ${inputs.current_security:,.0f} is adequate.")

    # Red flags
    if red_flags:
        notes.append(f"\n{len(red_flags)} red flags identified:")
        for flag in red_flags[:3]:  # Top 3
            notes.append(f"  {flag}")

    # Risk metrics
    notes.append(f"\nRisk metrics:")
    notes.append(f"  - Probability of default: {risk.probability_of_default:.1%}")
    notes.append(f"  - Expected loss: ${risk.expected_loss:,.0f}")
    notes.append(f"  - Security coverage: {risk.security_coverage_ratio:.1f}x")

    recommendation_text = " ".join(notes)

    return recommendation, recommendation_text


# ============================================================================
# REPORTING
# ============================================================================

def print_credit_report(result: CreditAnalysisResult):
    """Print formatted credit analysis report."""
    print("\n" + "="*80)
    print("TENANT CREDIT ANALYSIS REPORT")
    print("="*80)

    print(f"\nTenant: {result.tenant_name}")
    print(f"Analysis Date: {result.analysis_date}")

    # Financial ratios
    print("\n" + "-"*80)
    print("FINANCIAL RATIOS (Most Recent Year)")
    print("-"*80)

    print("\nLiquidity:")
    print(f"  Current Ratio: {result.financial_ratios.get('current_ratio', 0):.2f}")
    print(f"  Quick Ratio: {result.financial_ratios.get('quick_ratio', 0):.2f}")
    print(f"  Cash Ratio: {result.financial_ratios.get('cash_ratio', 0):.2f}")

    print("\nLeverage:")
    print(f"  Debt-to-Equity: {result.financial_ratios.get('debt_to_equity', 0):.2f}")
    print(f"  Debt-to-Assets: {result.financial_ratios.get('debt_to_assets', 0):.2f}")

    print("\nProfitability:")
    print(f"  Net Profit Margin: {result.financial_ratios.get('net_profit_margin', 0):.1%}")
    print(f"  ROA: {result.financial_ratios.get('roa', 0):.1%}")
    print(f"  ROE: {result.financial_ratios.get('roe', 0):.1%}")

    print("\nRent Coverage:")
    print(f"  EBITDA-to-Rent: {result.financial_ratios.get('ebitda_to_rent', 0):.2f}x")
    print(f"  Rent-to-Revenue: {result.financial_ratios.get('rent_to_revenue', 0):.1%}")

    # Credit score
    print("\n" + "-"*80)
    print("CREDIT SCORE")
    print("-"*80)

    cs = result.credit_score
    print(f"\nTotal Score: {cs.total_score:.0f} / 100")
    print(f"Credit Rating: {cs.credit_rating}")

    print(f"\nScore Breakdown:")
    print(f"  Financial Strength: {cs.financial_strength_score:.0f} / 40")
    print(f"  Business Quality: {cs.business_quality_score:.0f} / 30")
    print(f"  Credit History: {cs.credit_history_score:.0f} / 20")
    print(f"  Lease-Specific: {cs.lease_specific_score:.0f} / 10")

    # Risk assessment
    print("\n" + "-"*80)
    print("RISK ASSESSMENT")
    print("-"*80)

    risk = result.risk_assessment
    print(f"\nProbability of Default: {risk.probability_of_default:.1%}")
    print(f"Exposure at Default: ${risk.exposure_at_default:,.0f}")
    print(f"Expected Loss: ${risk.expected_loss:,.0f}")

    print(f"\nSecurity Recommendation:")
    print(f"  Recommended Amount: ${risk.recommended_security:,.0f}")
    print(f"  Type: {risk.security_type_recommendation}")
    print(f"  Coverage Ratio: {risk.security_coverage_ratio:.1f}x")

    # Trend analysis
    print("\n" + "-"*80)
    print("TREND ANALYSIS")
    print("-"*80)

    trend = result.trend_analysis
    print(f"\nOverall Trend: {trend.overall_trend.upper()}")
    print(f"  Revenue: {trend.revenue_trend.capitalize()}")
    print(f"  Profitability: {trend.profitability_trend.capitalize()}")
    print(f"  Liquidity: {trend.liquidity_trend.capitalize()}")
    print(f"  Leverage: {trend.leverage_trend.capitalize()}")

    # Red flags
    if result.red_flags:
        print("\n" + "-"*80)
        print("RED FLAGS")
        print("-"*80)
        for flag in result.red_flags:
            print(f"\n{flag}")

    # Recommendation
    print("\n" + "="*80)
    print(f"RECOMMENDATION: {result.approval_recommendation}")
    print("="*80)
    print(f"\n{result.recommendation_notes}")

    print("\n" + "="*80)


if __name__ == "__main__":
    # Example credit analysis
    print("Tenant Credit Analysis Calculator - Example\n")

    # Example: Evaluate a tenant with 3 years of financials
    financials = [
        FinancialData(
            year=2024,
            current_assets=450000,
            total_assets=2000000,
            inventory=100000,
            cash_and_equivalents=150000,
            current_liabilities=250000,
            total_liabilities=1200000,
            shareholders_equity=800000,
            revenue=5000000,
            gross_profit=1500000,
            ebit=400000,
            ebitda=500000,
            net_income=250000,
            interest_expense=80000,
            annual_rent=240000
        ),
        FinancialData(
            year=2023,
            current_assets=400000,
            total_assets=1800000,
            current_liabilities=280000,
            total_liabilities=1100000,
            shareholders_equity=700000,
            revenue=4500000,
            ebitda=450000,
            net_income=220000,
            annual_rent=230000
        ),
        FinancialData(
            year=2022,
            current_assets=350000,
            total_assets=1600000,
            current_liabilities=300000,
            total_liabilities=1000000,
            shareholders_equity=600000,
            revenue=4000000,
            ebitda=400000,
            net_income=200000,
            annual_rent=220000
        )
    ]

    inputs = CreditInputs(
        financial_data=financials,
        tenant_name="Example Corp",
        industry="Professional Services",
        years_in_business=8,
        credit_score=720,
        payment_history='excellent',
        lease_term_years=5,
        use_criticality='important',
        industry_stability='stable',
        current_security=20000,
        security_type="Rent Deposit"
    )

    # Perform analysis
    result = analyze_tenant_credit(inputs)

    # Print report
    print_credit_report(result)

    # Show step-down schedule
    print("\n" + "-"*80)
    print("SECURITY STEP-DOWN SCHEDULE")
    print("-"*80)
    print("\n" + result.risk_assessment.stepdown_schedule.to_string(index=False))

    print("\n✓ Example analysis complete!")
