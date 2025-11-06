"""
Real Options Valuation Calculator for Commercial Real Estate Leases

This module implements Black-Scholes option pricing adapted for real estate,
valuing embedded lease options (renewal, expansion, termination, purchase).

Based on:
- Black & Scholes (1973) - "The Pricing of Options and Corporate Liabilities"
- Grenadier (1995) - "Valuing Lease Contracts: A Real-Options Approach"

Author: Claude Code
Date: 2025-11-06
Version: 1.0.0
"""

import math
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from scipy.stats import norm
import numpy as np


@dataclass
class OptionParameters:
    """Parameters for a single option valuation"""
    option_type: str  # 'call' or 'put'
    option_name: str  # e.g., 'Renewal Option #1', 'Expansion', 'Termination'
    underlying_value: float  # S: Current value of underlying asset ($)
    strike_price: float  # K: Exercise/strike price ($)
    time_to_expiration: float  # T: Years until option expires
    volatility: float  # σ: Annual volatility (decimal, e.g., 0.12 for 12%)
    risk_free_rate: float  # r: Annual risk-free rate (decimal, e.g., 0.05 for 5%)

    # Optional adjustments
    utilization_probability: float = 1.0  # For expansion options (0-1)
    termination_fee: float = 0.0  # For termination options ($)

    # Additional context
    rentable_area_sf: Optional[float] = None
    option_term_years: Optional[float] = None


@dataclass
class OptionGreeks:
    """Option Greeks - sensitivity measures"""
    delta: float  # ∂V/∂S - sensitivity to underlying price
    gamma: float  # ∂²V/∂S² - rate of change of delta
    vega: float  # ∂V/∂σ - sensitivity to volatility (per 1% change)
    theta: float  # ∂V/∂T - time decay (per year)
    rho: float  # ∂V/∂r - sensitivity to interest rate (per 1% change)


@dataclass
class OptionValuation:
    """Results of option valuation"""
    option_name: str
    option_type: str
    option_value: float  # Total option value ($)
    option_value_per_sf: Optional[float]  # Value per square foot ($/sf)
    probability_itm: float  # Probability of being in-the-money (%)

    # Black-Scholes intermediate values
    d1: float
    d2: float

    # Option Greeks
    greeks: OptionGreeks

    # Input parameters (for reference)
    underlying_value: float
    strike_price: float
    time_to_expiration: float
    volatility: float
    risk_free_rate: float


@dataclass
class SensitivityAnalysis:
    """Sensitivity analysis results"""
    base_value: float

    # Volatility sensitivity
    volatility_scenarios: List[Dict[str, float]]  # [{volatility, value}, ...]

    # Market rent sensitivity
    market_rent_scenarios: List[Dict[str, float]]  # [{change_pct, value}, ...]

    # Time decay
    time_decay_schedule: List[Dict[str, float]]  # [{years_remaining, value}, ...]


@dataclass
class PortfolioOptionValuation:
    """Aggregate valuation of all options in a lease"""
    analysis_date: str
    property_address: str
    rentable_area_sf: float

    # Individual option valuations
    options: List[OptionValuation]

    # Total portfolio metrics
    total_option_value: float
    total_value_per_sf: float
    total_as_pct_of_property: Optional[float] = None

    # Sensitivity analysis
    sensitivity: Optional[SensitivityAnalysis] = None

    # Market context
    market_rent_psf: Optional[float] = None
    base_rent_psf: Optional[float] = None
    rent_premium_psf: Optional[float] = None
    annualized_option_value: Optional[float] = None


# =============================================================================
# BLACK-SCHOLES CORE FUNCTIONS
# =============================================================================

def cumulative_normal_distribution(x: float) -> float:
    """
    Cumulative normal distribution N(x)

    Uses scipy.stats.norm.cdf() for accuracy to 15+ decimal places.

    Args:
        x: Standard normal variable

    Returns:
        Probability that standard normal ≤ x
    """
    return norm.cdf(x)


def black_scholes_d1_d2(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float
) -> Tuple[float, float]:
    """
    Calculate d1 and d2 for Black-Scholes formula

    d1 = [ln(S/K) + (r + σ²/2)T] / (σ√T)
    d2 = d1 - σ√T

    Args:
        S: Current value of underlying asset
        K: Strike price
        T: Time to expiration (years)
        r: Risk-free rate (annual)
        sigma: Volatility (annual)

    Returns:
        Tuple of (d1, d2)

    Raises:
        ValueError: If T <= 0 or sigma <= 0
    """
    if T <= 0:
        raise ValueError(f"Time to expiration must be positive, got {T}")
    if sigma <= 0:
        raise ValueError(f"Volatility must be positive, got {sigma}")
    if S <= 0:
        raise ValueError(f"Underlying value must be positive, got {S}")
    if K <= 0:
        raise ValueError(f"Strike price must be positive, got {K}")

    sqrt_T = math.sqrt(T)

    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * sqrt_T)
    d2 = d1 - sigma * sqrt_T

    return d1, d2


def black_scholes_call(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float
) -> float:
    """
    Black-Scholes call option pricing formula

    C = S × N(d1) - K × e^(-rT) × N(d2)

    Args:
        S: Current value of underlying asset
        K: Strike price
        T: Time to expiration (years)
        r: Risk-free rate (annual)
        sigma: Volatility (annual)

    Returns:
        Call option value
    """
    d1, d2 = black_scholes_d1_d2(S, K, T, r, sigma)

    N_d1 = cumulative_normal_distribution(d1)
    N_d2 = cumulative_normal_distribution(d2)

    call_value = S * N_d1 - K * math.exp(-r * T) * N_d2

    return call_value


def black_scholes_put(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float
) -> float:
    """
    Black-Scholes put option pricing formula

    P = K × e^(-rT) × N(-d2) - S × N(-d1)

    Args:
        S: Current value of underlying asset
        K: Strike price
        T: Time to expiration (years)
        r: Risk-free rate (annual)
        sigma: Volatility (annual)

    Returns:
        Put option value
    """
    d1, d2 = black_scholes_d1_d2(S, K, T, r, sigma)

    N_neg_d1 = cumulative_normal_distribution(-d1)
    N_neg_d2 = cumulative_normal_distribution(-d2)

    put_value = K * math.exp(-r * T) * N_neg_d2 - S * N_neg_d1

    return put_value


# =============================================================================
# OPTION GREEKS
# =============================================================================

def calculate_option_greeks(
    option_type: str,
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    d1: float,
    d2: float
) -> OptionGreeks:
    """
    Calculate all option Greeks (sensitivity measures)

    Greeks:
    - Delta (Δ): ∂V/∂S - change in option value per $1 change in underlying
    - Gamma (Γ): ∂²V/∂S² - rate of change of delta
    - Vega (ν): ∂V/∂σ - change per 1% change in volatility
    - Theta (θ): ∂V/∂T - time decay per year
    - Rho (ρ): ∂V/∂r - change per 1% change in interest rate

    Args:
        option_type: 'call' or 'put'
        S, K, T, r, sigma: Black-Scholes parameters
        d1, d2: Pre-calculated d1 and d2 values

    Returns:
        OptionGreeks dataclass with all sensitivity measures
    """
    sqrt_T = math.sqrt(T)
    N_d1 = cumulative_normal_distribution(d1)
    N_d2 = cumulative_normal_distribution(d2)

    # Standard normal PDF at d1: φ(d1) = (1/√2π) × e^(-d1²/2)
    phi_d1 = (1 / math.sqrt(2 * math.pi)) * math.exp(-0.5 * d1**2)

    # Delta: ∂V/∂S
    if option_type == 'call':
        delta = N_d1
    else:  # put
        delta = N_d1 - 1

    # Gamma: ∂²V/∂S² (same for call and put)
    gamma = phi_d1 / (S * sigma * sqrt_T)

    # Vega: ∂V/∂σ (same for call and put)
    # Returns change per 1% (0.01) change in volatility
    vega = S * phi_d1 * sqrt_T / 100  # Divide by 100 to get per 1% change

    # Theta: ∂V/∂T (per year)
    if option_type == 'call':
        theta = (-(S * phi_d1 * sigma) / (2 * sqrt_T)
                 - r * K * math.exp(-r * T) * N_d2)
    else:  # put
        theta = (-(S * phi_d1 * sigma) / (2 * sqrt_T)
                 + r * K * math.exp(-r * T) * cumulative_normal_distribution(-d2))

    # Rho: ∂V/∂r (per 1% change in interest rate)
    if option_type == 'call':
        rho = K * T * math.exp(-r * T) * N_d2 / 100  # Divide by 100 for per 1%
    else:  # put
        rho = -K * T * math.exp(-r * T) * cumulative_normal_distribution(-d2) / 100

    return OptionGreeks(
        delta=delta,
        gamma=gamma,
        vega=vega,
        theta=theta,
        rho=rho
    )


# =============================================================================
# OPTION VALUATION
# =============================================================================

def value_option(params: OptionParameters) -> OptionValuation:
    """
    Value a single option using Black-Scholes

    Args:
        params: OptionParameters with all required inputs

    Returns:
        OptionValuation with complete results
    """
    S = params.underlying_value
    K = params.strike_price
    T = params.time_to_expiration
    r = params.risk_free_rate
    sigma = params.volatility

    # Calculate d1 and d2
    d1, d2 = black_scholes_d1_d2(S, K, T, r, sigma)

    # Calculate option value
    if params.option_type == 'call':
        option_value = black_scholes_call(S, K, T, r, sigma)
    elif params.option_type == 'put':
        option_value = black_scholes_put(S, K, T, r, sigma)
    else:
        raise ValueError(f"option_type must be 'call' or 'put', got {params.option_type}")

    # Apply utilization probability adjustment (for expansion options)
    if params.utilization_probability < 1.0:
        option_value *= params.utilization_probability

    # Calculate probability of being in-the-money
    if params.option_type == 'call':
        prob_itm = cumulative_normal_distribution(d2) * 100  # Convert to percentage
    else:  # put
        prob_itm = cumulative_normal_distribution(-d2) * 100

    # Calculate Greeks
    greeks = calculate_option_greeks(params.option_type, S, K, T, r, sigma, d1, d2)

    # Calculate per-SF value if area provided
    option_value_per_sf = None
    if params.rentable_area_sf and params.rentable_area_sf > 0:
        option_value_per_sf = option_value / params.rentable_area_sf

    return OptionValuation(
        option_name=params.option_name,
        option_type=params.option_type,
        option_value=option_value,
        option_value_per_sf=option_value_per_sf,
        probability_itm=prob_itm,
        d1=d1,
        d2=d2,
        greeks=greeks,
        underlying_value=S,
        strike_price=K,
        time_to_expiration=T,
        volatility=sigma,
        risk_free_rate=r
    )


# =============================================================================
# SENSITIVITY ANALYSIS
# =============================================================================

def sensitivity_analysis_volatility(
    params: OptionParameters,
    volatility_scenarios: List[float]
) -> List[Dict[str, float]]:
    """
    Analyze sensitivity to volatility changes

    Args:
        params: Base option parameters
        volatility_scenarios: List of volatility levels to test (e.g., [0.05, 0.10, 0.15, 0.20])

    Returns:
        List of {volatility, option_value} dictionaries
    """
    results = []

    for vol in volatility_scenarios:
        params_copy = OptionParameters(
            option_type=params.option_type,
            option_name=params.option_name,
            underlying_value=params.underlying_value,
            strike_price=params.strike_price,
            time_to_expiration=params.time_to_expiration,
            volatility=vol,  # Varied parameter
            risk_free_rate=params.risk_free_rate,
            utilization_probability=params.utilization_probability,
            termination_fee=params.termination_fee,
            rentable_area_sf=params.rentable_area_sf,
            option_term_years=params.option_term_years
        )

        valuation = value_option(params_copy)

        results.append({
            'volatility': vol,
            'volatility_pct': vol * 100,
            'option_value': valuation.option_value
        })

    return results


def sensitivity_analysis_market_rent(
    params: OptionParameters,
    market_rent_changes: List[float]
) -> List[Dict[str, float]]:
    """
    Analyze sensitivity to market rent changes

    Args:
        params: Base option parameters
        market_rent_changes: List of % changes (e.g., [-0.20, -0.10, 0, 0.10, 0.20, 0.50])

    Returns:
        List of {change_pct, new_underlying, option_value} dictionaries
    """
    results = []
    base_underlying = params.underlying_value

    for change_pct in market_rent_changes:
        new_underlying = base_underlying * (1 + change_pct)

        params_copy = OptionParameters(
            option_type=params.option_type,
            option_name=params.option_name,
            underlying_value=new_underlying,  # Varied parameter
            strike_price=params.strike_price,
            time_to_expiration=params.time_to_expiration,
            volatility=params.volatility,
            risk_free_rate=params.risk_free_rate,
            utilization_probability=params.utilization_probability,
            termination_fee=params.termination_fee,
            rentable_area_sf=params.rentable_area_sf,
            option_term_years=params.option_term_years
        )

        valuation = value_option(params_copy)

        results.append({
            'change_pct': change_pct,
            'change_pct_display': change_pct * 100,
            'new_underlying_value': new_underlying,
            'option_value': valuation.option_value
        })

    return results


def sensitivity_analysis_time_decay(
    params: OptionParameters,
    time_points: List[float]
) -> List[Dict[str, float]]:
    """
    Analyze time decay (theta) over life of option

    Args:
        params: Base option parameters
        time_points: List of years remaining (e.g., [5.0, 4.0, 3.0, 2.0, 1.0, 0.5, 0.25])

    Returns:
        List of {years_remaining, option_value, annual_decay} dictionaries
    """
    results = []
    previous_value = None
    previous_time = None

    for T in sorted(time_points, reverse=True):  # Sort descending (furthest to nearest)
        if T <= 0:
            continue

        params_copy = OptionParameters(
            option_type=params.option_type,
            option_name=params.option_name,
            underlying_value=params.underlying_value,
            strike_price=params.strike_price,
            time_to_expiration=T,  # Varied parameter
            volatility=params.volatility,
            risk_free_rate=params.risk_free_rate,
            utilization_probability=params.utilization_probability,
            termination_fee=params.termination_fee,
            rentable_area_sf=params.rentable_area_sf,
            option_term_years=params.option_term_years
        )

        valuation = value_option(params_copy)

        # Calculate annual decay from previous period
        annual_decay = None
        if previous_value is not None and previous_time is not None:
            time_diff = previous_time - T
            if time_diff > 0:
                annual_decay = (previous_value - valuation.option_value) / time_diff

        results.append({
            'years_remaining': T,
            'option_value': valuation.option_value,
            'annual_decay': annual_decay if annual_decay is not None else 0
        })

        previous_value = valuation.option_value
        previous_time = T

    return results


def perform_full_sensitivity_analysis(
    params: OptionParameters,
    volatility_scenarios: Optional[List[float]] = None,
    market_rent_changes: Optional[List[float]] = None,
    time_points: Optional[List[float]] = None
) -> SensitivityAnalysis:
    """
    Perform comprehensive sensitivity analysis

    Args:
        params: Base option parameters
        volatility_scenarios: Volatility levels to test (default: [0.05, 0.10, 0.15, 0.20])
        market_rent_changes: Market rent % changes (default: [-0.20, -0.10, 0, 0.10, 0.20, 0.50])
        time_points: Years remaining to test (default: based on T)

    Returns:
        SensitivityAnalysis with complete results
    """
    # Default scenarios if not provided
    if volatility_scenarios is None:
        volatility_scenarios = [0.05, 0.10, 0.15, 0.20]

    if market_rent_changes is None:
        market_rent_changes = [-0.20, -0.10, 0, 0.10, 0.20, 0.50]

    if time_points is None:
        T = params.time_to_expiration
        if T >= 5:
            time_points = [T, T-1, T-2, T-3, T-4, T-5]
        elif T >= 2:
            time_points = [T, T * 0.75, T * 0.50, T * 0.25]
        else:
            time_points = [T, T * 0.5, T * 0.25]
        time_points = [t for t in time_points if t > 0]

    # Base valuation
    base_valuation = value_option(params)

    # Run sensitivity analyses
    vol_sensitivity = sensitivity_analysis_volatility(params, volatility_scenarios)
    market_sensitivity = sensitivity_analysis_market_rent(params, market_rent_changes)
    time_sensitivity = sensitivity_analysis_time_decay(params, time_points)

    return SensitivityAnalysis(
        base_value=base_valuation.option_value,
        volatility_scenarios=vol_sensitivity,
        market_rent_scenarios=market_sensitivity,
        time_decay_schedule=time_sensitivity
    )


# =============================================================================
# PORTFOLIO VALUATION
# =============================================================================

def value_option_portfolio(
    options: List[OptionParameters],
    property_address: str,
    rentable_area_sf: float,
    perform_sensitivity: bool = True,
    market_rent_psf: Optional[float] = None,
    base_rent_psf: Optional[float] = None
) -> PortfolioOptionValuation:
    """
    Value a portfolio of lease options

    Args:
        options: List of OptionParameters for all options in lease
        property_address: Property address
        rentable_area_sf: Total rentable area
        perform_sensitivity: Whether to run sensitivity analysis on first option
        market_rent_psf: Current market rent ($/sf/year)
        base_rent_psf: Base lease rent ($/sf/year)

    Returns:
        PortfolioOptionValuation with aggregate results
    """
    # Value each option
    valuations = [value_option(opt) for opt in options]

    # Calculate total value
    total_value = sum(v.option_value for v in valuations)
    total_value_per_sf = total_value / rentable_area_sf if rentable_area_sf > 0 else 0

    # Calculate rent premium if market rent provided
    rent_premium_psf = None
    if market_rent_psf is not None and base_rent_psf is not None:
        rent_premium_psf = base_rent_psf - market_rent_psf

    # Sensitivity analysis on first option (typically renewal, most significant)
    sensitivity = None
    if perform_sensitivity and len(options) > 0:
        sensitivity = perform_full_sensitivity_analysis(options[0])

    return PortfolioOptionValuation(
        analysis_date=datetime.now().strftime('%Y-%m-%d'),
        property_address=property_address,
        rentable_area_sf=rentable_area_sf,
        options=valuations,
        total_option_value=total_value,
        total_value_per_sf=total_value_per_sf,
        sensitivity=sensitivity,
        market_rent_psf=market_rent_psf,
        base_rent_psf=base_rent_psf,
        rent_premium_psf=rent_premium_psf
    )


# =============================================================================
# JSON I/O
# =============================================================================

def load_options_from_json(json_path: str) -> Tuple[List[OptionParameters], Dict]:
    """
    Load option parameters from JSON file

    Expected JSON structure:
    {
        "property_address": "123 Main St",
        "rentable_area_sf": 50000,
        "market_rent_psf": 16.50,
        "base_rent_psf": 17.00,
        "options": [
            {
                "option_type": "call",
                "option_name": "Renewal Option #1",
                "underlying_value": 825000,
                "strike_price": 800000,
                "time_to_expiration": 5.0,
                "volatility": 0.12,
                "risk_free_rate": 0.05,
                ...
            }
        ]
    }

    Returns:
        Tuple of (list of OptionParameters, metadata dict)
    """
    with open(json_path, 'r') as f:
        data = json.load(f)

    options_list = []
    for opt_data in data.get('options', []):
        opt = OptionParameters(
            option_type=opt_data['option_type'],
            option_name=opt_data['option_name'],
            underlying_value=opt_data['underlying_value'],
            strike_price=opt_data['strike_price'],
            time_to_expiration=opt_data['time_to_expiration'],
            volatility=opt_data['volatility'],
            risk_free_rate=opt_data['risk_free_rate'],
            utilization_probability=opt_data.get('utilization_probability', 1.0),
            termination_fee=opt_data.get('termination_fee', 0.0),
            rentable_area_sf=data.get('rentable_area_sf'),
            option_term_years=opt_data.get('option_term_years')
        )
        options_list.append(opt)

    metadata = {
        'property_address': data.get('property_address', ''),
        'rentable_area_sf': data.get('rentable_area_sf', 0),
        'market_rent_psf': data.get('market_rent_psf'),
        'base_rent_psf': data.get('base_rent_psf')
    }

    return options_list, metadata


def save_results_to_json(results: PortfolioOptionValuation, output_path: str):
    """
    Save valuation results to JSON file

    Args:
        results: PortfolioOptionValuation results
        output_path: Path to output JSON file
    """
    # Convert dataclasses to dictionaries
    results_dict = asdict(results)

    with open(output_path, 'w') as f:
        json.dump(results_dict, f, indent=2)


# =============================================================================
# COMMAND-LINE INTERFACE
# =============================================================================

def main():
    """Command-line interface for option valuation"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Real Options Valuation Calculator for Commercial Leases'
    )
    parser.add_argument(
        'input_json',
        help='Path to input JSON file with option parameters'
    )
    parser.add_argument(
        '--output',
        help='Path to output JSON file (default: auto-generated)',
        default=None
    )
    parser.add_argument(
        '--no-sensitivity',
        action='store_true',
        help='Skip sensitivity analysis'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Print detailed results to console'
    )

    args = parser.parse_args()

    # Load options from JSON
    print(f"Loading option parameters from {args.input_json}...")
    options, metadata = load_options_from_json(args.input_json)
    print(f"  ✓ Loaded {len(options)} option(s)")

    # Value portfolio
    print("\nValuing option portfolio...")
    results = value_option_portfolio(
        options=options,
        property_address=metadata['property_address'],
        rentable_area_sf=metadata['rentable_area_sf'],
        perform_sensitivity=not args.no_sensitivity,
        market_rent_psf=metadata.get('market_rent_psf'),
        base_rent_psf=metadata.get('base_rent_psf')
    )

    # Generate output filename if not provided
    if args.output is None:
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        args.output = f'option_valuation_results_{timestamp}.json'

    # Save results
    print(f"\nSaving results to {args.output}...")
    save_results_to_json(results, args.output)
    print("  ✓ Results saved")

    # Print summary
    print("\n" + "=" * 70)
    print("OPTION VALUATION SUMMARY")
    print("=" * 70)
    print(f"Property: {results.property_address}")
    print(f"Rentable Area: {results.rentable_area_sf:,.0f} SF")
    print(f"Analysis Date: {results.analysis_date}")
    print()
    print(f"Total Option Value: ${results.total_option_value:,.2f}")
    print(f"Value per SF: ${results.total_value_per_sf:.2f}/sf")
    print()

    print("Individual Options:")
    print("-" * 70)
    for opt in results.options:
        print(f"{opt.option_name} ({opt.option_type}):")
        print(f"  Value: ${opt.option_value:,.2f}", end='')
        if opt.option_value_per_sf:
            print(f" (${opt.option_value_per_sf:.2f}/sf)", end='')
        print()
        print(f"  Probability ITM: {opt.probability_itm:.1f}%")
        print(f"  Greeks: Δ={opt.greeks.delta:.3f}, Γ={opt.greeks.gamma:.6f}, "
              f"ν=${opt.greeks.vega:,.0f}/1%, θ=${opt.greeks.theta:,.0f}/yr")
        print()

    if args.verbose and results.sensitivity:
        print("\nSensitivity Analysis (First Option):")
        print("-" * 70)
        sens = results.sensitivity

        print("\nVolatility Sensitivity:")
        for scenario in sens.volatility_scenarios:
            pct_change = ((scenario['option_value'] / sens.base_value) - 1) * 100
            print(f"  {scenario['volatility_pct']:.0f}%: ${scenario['option_value']:,.2f} "
                  f"({pct_change:+.1f}%)")

        print("\nMarket Rent Sensitivity:")
        for scenario in sens.market_rent_scenarios:
            print(f"  {scenario['change_pct_display']:+.0f}%: ${scenario['option_value']:,.2f}")

    print("=" * 70)
    print(f"\n✓ Analysis complete. Results saved to {args.output}")


if __name__ == '__main__':
    main()
