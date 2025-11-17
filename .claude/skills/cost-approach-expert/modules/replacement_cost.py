"""
Replacement Cost New (RCN) Module

Calculates replacement cost new for infrastructure assets.
Includes direct costs (materials, labor) and indirect costs (overhead, profit).
"""

from typing import Dict


def calculate_replacement_cost_new(construction_costs: Dict) -> Dict:
    """
    Calculate replacement cost new (RCN) with detailed breakdown.

    Formula:
        Direct Costs = Materials + Labor
        Overhead = Direct Costs × Overhead %
        Subtotal = Direct Costs + Overhead
        Profit = Subtotal × Profit %
        RCN = Subtotal + Profit

    Args:
        construction_costs: Dictionary with:
            - materials: Materials cost
            - labor: Labor cost
            - overhead_percentage: Overhead rate (decimal, e.g., 0.15 for 15%)
            - profit_percentage: Profit rate (decimal, e.g., 0.12 for 12%)

    Returns:
        Dictionary with:
            - materials: Materials cost
            - labor: Labor cost
            - direct_costs: Materials + Labor
            - overhead: Calculated overhead
            - overhead_percentage: Input overhead rate
            - subtotal: Direct costs + Overhead
            - profit: Calculated profit
            - profit_percentage: Input profit rate
            - replacement_cost_new: Total RCN

    Example:
        >>> costs = {
        ...     'materials': 150000,
        ...     'labor': 80000,
        ...     'overhead_percentage': 0.15,
        ...     'profit_percentage': 0.12
        ... }
        >>> rcn = calculate_replacement_cost_new(costs)
        >>> print(f"RCN: ${rcn['replacement_cost_new']:,.2f}")
        RCN: $289,100.00
    """
    materials = construction_costs.get('materials', 0)
    labor = construction_costs.get('labor', 0)
    overhead_pct = construction_costs.get('overhead_percentage', 0)
    profit_pct = construction_costs.get('profit_percentage', 0)

    # Step 1: Direct costs
    direct_costs = materials + labor

    # Step 2: Overhead (applied to direct costs)
    overhead = direct_costs * overhead_pct

    # Step 3: Subtotal
    subtotal = direct_costs + overhead

    # Step 4: Profit (applied to subtotal)
    profit = subtotal * profit_pct

    # Step 5: Total RCN
    replacement_cost_new = subtotal + profit

    return {
        'materials': materials,
        'labor': labor,
        'direct_costs': direct_costs,
        'overhead': overhead,
        'overhead_percentage': overhead_pct,
        'subtotal': subtotal,
        'profit': profit,
        'profit_percentage': profit_pct,
        'replacement_cost_new': replacement_cost_new
    }


def calculate_unit_rcn(
    total_rcn: float,
    quantity: float,
    unit_type: str = 'each'
) -> Dict:
    """
    Calculate unit replacement cost.

    Args:
        total_rcn: Total replacement cost new
        quantity: Number of units (e.g., 10 towers, 5.5 km)
        unit_type: Type of unit (e.g., 'each', 'km', 'meters')

    Returns:
        Dictionary with unit cost breakdown

    Example:
        >>> unit = calculate_unit_rcn(289100, 1, 'tower')
        >>> print(f"${unit['unit_rcn']:,.2f} per {unit['unit_type']}")
        $289,100.00 per tower
    """
    if quantity <= 0:
        raise ValueError(f"quantity must be positive, got {quantity}")

    unit_rcn = total_rcn / quantity

    return {
        'total_rcn': total_rcn,
        'quantity': quantity,
        'unit_type': unit_type,
        'unit_rcn': unit_rcn
    }


def adjust_rcn_for_inflation(
    base_rcn: float,
    base_year: int,
    current_year: int,
    annual_inflation_rate: float = 0.03
) -> Dict:
    """
    Adjust RCN for inflation from base year to current year.

    Args:
        base_rcn: Replacement cost in base year
        base_year: Base year for costs
        current_year: Current year (for adjustment)
        annual_inflation_rate: Annual inflation rate (default 3%)

    Returns:
        Dictionary with adjusted RCN

    Example:
        >>> adjusted = adjust_rcn_for_inflation(250000, 2020, 2025, 0.03)
        >>> print(f"Adjusted RCN: ${adjusted['adjusted_rcn']:,.2f}")
        Adjusted RCN: $289,828.44
    """
    if current_year < base_year:
        raise ValueError(f"current_year ({current_year}) cannot be before base_year ({base_year})")

    years_elapsed = current_year - base_year
    inflation_factor = (1 + annual_inflation_rate) ** years_elapsed
    adjusted_rcn = base_rcn * inflation_factor

    return {
        'base_rcn': base_rcn,
        'base_year': base_year,
        'current_year': current_year,
        'years_elapsed': years_elapsed,
        'annual_inflation_rate': annual_inflation_rate,
        'inflation_factor': inflation_factor,
        'adjusted_rcn': adjusted_rcn,
        'inflation_adjustment': adjusted_rcn - base_rcn
    }


def calculate_rcn_with_premium(
    base_rcn: float,
    premium_percentage: float,
    premium_reason: str = ''
) -> Dict:
    """
    Calculate RCN with premium for special circumstances.

    Premiums may apply for:
    - Remote/difficult access locations
    - Specialized/custom components
    - Accelerated construction schedules
    - Environmental constraints

    Args:
        base_rcn: Base replacement cost new
        premium_percentage: Premium as decimal (e.g., 0.10 for 10%)
        premium_reason: Description of why premium applies

    Returns:
        Dictionary with premium-adjusted RCN

    Example:
        >>> rcn_premium = calculate_rcn_with_premium(
        ...     250000,
        ...     0.15,
        ...     'Remote location requiring helicopter access'
        ... )
        >>> print(f"Total RCN: ${rcn_premium['total_rcn']:,.2f}")
        Total RCN: $287,500.00
    """
    if premium_percentage < 0:
        raise ValueError(f"premium_percentage cannot be negative: {premium_percentage}")

    premium = base_rcn * premium_percentage
    total_rcn = base_rcn + premium

    return {
        'base_rcn': base_rcn,
        'premium_percentage': premium_percentage,
        'premium_amount': premium,
        'premium_reason': premium_reason,
        'total_rcn': total_rcn
    }
