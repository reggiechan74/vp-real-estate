"""
Rental Variance Decomposition Calculator
Commercial Lease Portfolio Variance Analysis Tool

This script decomposes rental revenue variances into three components:
1. Rate Variance - Impact of changes in rental rates ($/sf/year)
2. Area Variance - Impact of changes in leased area (sf)
3. Term Variance - Impact of changes in lease timing (months)

Theoretical Foundation:
---------------------
Total Variance = Actual Revenue - Budgeted Revenue
              = (A × B × C) - (D × E × F)

Where:
    A = Actual Rate ($/sf/year)
    B = Actual Area (sf)
    C = Actual Term (months)
    D = Budgeted Rate ($/sf/year)
    E = Budgeted Area (sf)
    F = Budgeted Term (months)

Variance Decomposition:
1. Rate Variance  = (B × C) × (A - D) = Actual Area × Actual Term × Rate Difference
2. Area Variance  = (C × D) × (B - E) = Budget Rate × Actual Term × Area Difference
3. Term Variance  = (D × E) × (C - F) = Budget Rate × Budget Area × Term Difference

Mathematical Proof:
Total = (BC)(A-D) + (CD)(B-E) + (DE)(C-F)
      = ABC - BCD + BCD - CDE + CDE - DEF
      = ABC - DEF ✓
"""

import json
import sys
import argparse
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime, date
from pathlib import Path


@dataclass
class ActualBudget:
    """Actual or Budget lease terms"""
    start_date: str
    end_date: str
    term_months: float
    rate_psf_year: float
    area_sf: float

    def revenue(self) -> float:
        """Calculate total revenue: Rate × Area × Term"""
        # Convert annual rate to monthly, multiply by months and area
        monthly_rate = self.rate_psf_year / 12.0
        return monthly_rate * self.area_sf * self.term_months


@dataclass
class VarianceItem:
    """Single tenant variance calculation"""
    tenant_name: str
    unit_number: str
    actual: ActualBudget
    budget: ActualBudget
    manual_adjustment: float = 0.0
    notes: str = ""

    def calculate_variances(self) -> Dict[str, float]:
        """
        Calculate variance decomposition

        Returns:
            Dictionary with variance components
        """
        # Extract values for readability
        A = self.actual.rate_psf_year
        B = self.actual.area_sf
        C = self.actual.term_months
        D = self.budget.rate_psf_year
        E = self.budget.area_sf
        F = self.budget.term_months

        # Convert annual rates to monthly for calculation
        A_monthly = A / 12.0
        D_monthly = D / 12.0

        # Calculate component variances
        # Note: Using monthly rates to get variance in dollars
        rate_variance = (B * C) * (A_monthly - D_monthly)
        area_variance = (C * D_monthly) * (B - E)
        term_variance = (D_monthly * E) * (C - F)

        # Calculate actual and budget revenues
        actual_revenue = self.actual.revenue()
        budget_revenue = self.budget.revenue()
        total_variance = actual_revenue - budget_revenue

        # Add manual adjustment
        total_with_adjustment = total_variance + self.manual_adjustment

        # Calculate component reconciliation
        calculated_total = rate_variance + area_variance + term_variance

        return {
            'rate_variance': rate_variance,
            'area_variance': area_variance,
            'term_variance': term_variance,
            'manual_adjustment': self.manual_adjustment,
            'total_variance': total_variance,
            'total_with_adjustment': total_with_adjustment,
            'calculated_total': calculated_total,
            'reconciliation_diff': abs(calculated_total - total_variance),
            'actual_revenue': actual_revenue,
            'budget_revenue': budget_revenue,
            # Percentage changes
            'rate_change_pct': ((A - D) / D * 100) if D != 0 else 0,
            'area_change_pct': ((B - E) / E * 100) if E != 0 else 0,
            'term_change_pct': ((C - F) / F * 100) if F != 0 else 0,
            'revenue_change_pct': ((actual_revenue - budget_revenue) / budget_revenue * 100) if budget_revenue != 0 else 0
        }


@dataclass
class VarianceAnalysisInput:
    """Input data for variance analysis"""
    analysis_date: str
    period_start: str
    period_end: str
    period_months: int
    property_info: Dict[str, any]
    variance_items: List[Dict]
    notes: str = ""


@dataclass
class VarianceAnalysisResults:
    """Results of variance analysis"""

    # Summary totals
    total_rate_variance: float = 0.0
    total_area_variance: float = 0.0
    total_term_variance: float = 0.0
    total_manual_adjustment: float = 0.0
    total_variance: float = 0.0
    total_actual_revenue: float = 0.0
    total_budget_revenue: float = 0.0

    # Detailed results by tenant
    tenant_results: List[Dict] = field(default_factory=list)

    # Reconciliation
    reconciliation_check: bool = True
    reconciliation_difference: float = 0.0


class VarianceCalculator:
    """Calculator for rental variance decomposition"""

    def __init__(self, input_data: VarianceAnalysisInput):
        self.input = input_data
        self.variance_items: List[VarianceItem] = []
        self._parse_variance_items()

    def _parse_variance_items(self):
        """Parse JSON input into VarianceItem objects"""
        for item_data in self.input.variance_items:
            actual = ActualBudget(**item_data['actual'])
            budget = ActualBudget(**item_data['budget'])

            item = VarianceItem(
                tenant_name=item_data['tenant_name'],
                unit_number=item_data['unit_number'],
                actual=actual,
                budget=budget,
                manual_adjustment=item_data.get('manual_adjustment', 0.0),
                notes=item_data.get('notes', '')
            )
            self.variance_items.append(item)

    def calculate_all(self) -> VarianceAnalysisResults:
        """
        Calculate variance decomposition for all tenants

        Returns:
            VarianceAnalysisResults with all calculations
        """
        results = VarianceAnalysisResults()

        for item in self.variance_items:
            variances = item.calculate_variances()

            # Add to totals
            results.total_rate_variance += variances['rate_variance']
            results.total_area_variance += variances['area_variance']
            results.total_term_variance += variances['term_variance']
            results.total_manual_adjustment += variances['manual_adjustment']
            results.total_variance += variances['total_variance']
            results.total_actual_revenue += variances['actual_revenue']
            results.total_budget_revenue += variances['budget_revenue']

            # Store detailed results
            tenant_result = {
                'tenant_name': item.tenant_name,
                'unit_number': item.unit_number,
                'actual': {
                    'rate_psf_year': item.actual.rate_psf_year,
                    'area_sf': item.actual.area_sf,
                    'term_months': item.actual.term_months,
                    'start_date': item.actual.start_date,
                    'end_date': item.actual.end_date,
                    'revenue': variances['actual_revenue']
                },
                'budget': {
                    'rate_psf_year': item.budget.rate_psf_year,
                    'area_sf': item.budget.area_sf,
                    'term_months': item.budget.term_months,
                    'start_date': item.budget.start_date,
                    'end_date': item.budget.end_date,
                    'revenue': variances['budget_revenue']
                },
                'variances': variances,
                'notes': item.notes
            }
            results.tenant_results.append(tenant_result)

        # Reconciliation check
        calculated_from_components = (
            results.total_rate_variance +
            results.total_area_variance +
            results.total_term_variance
        )
        results.reconciliation_difference = abs(calculated_from_components - results.total_variance)
        results.reconciliation_check = results.reconciliation_difference < 0.01  # Allow $0.01 rounding

        return results

    def print_summary(self, results: VarianceAnalysisResults):
        """Print formatted summary to console"""

        print("\n" + "="*80)
        print("RENTAL VARIANCE ANALYSIS SUMMARY")
        print("="*80)

        print(f"\nProperty: {self.input.property_info.get('property_name', 'N/A')}")
        print(f"Period: {self.input.period_start} to {self.input.period_end} ({self.input.period_months} months)")
        print(f"Analysis Date: {self.input.analysis_date}")

        print("\n" + "-"*80)
        print("REVENUE SUMMARY")
        print("-"*80)
        print(f"Budget Revenue:        ${results.total_budget_revenue:>15,.2f}")
        print(f"Actual Revenue:        ${results.total_actual_revenue:>15,.2f}")
        print(f"Total Variance:        ${results.total_variance:>15,.2f}  ", end="")
        if results.total_variance >= 0:
            print("(Favorable)")
        else:
            print("(Unfavorable)")

        print("\n" + "-"*80)
        print("VARIANCE DECOMPOSITION")
        print("-"*80)

        total_abs = abs(results.total_variance) if results.total_variance != 0 else 1

        print(f"Rate Variance:         ${results.total_rate_variance:>15,.2f}  ", end="")
        print(f"({abs(results.total_rate_variance)/total_abs*100:>5.1f}%)")

        print(f"Area Variance:         ${results.total_area_variance:>15,.2f}  ", end="")
        print(f"({abs(results.total_area_variance)/total_abs*100:>5.1f}%)")

        print(f"Term Variance:         ${results.total_term_variance:>15,.2f}  ", end="")
        print(f"({abs(results.total_term_variance)/total_abs*100:>5.1f}%)")

        if results.total_manual_adjustment != 0:
            print(f"Manual Adjustments:    ${results.total_manual_adjustment:>15,.2f}")

        print(f"{'─'*80}")
        print(f"Total (Calculated):    ${results.total_variance:>15,.2f}")

        print("\n" + "-"*80)
        print("RECONCILIATION CHECK")
        print("-"*80)
        calculated = results.total_rate_variance + results.total_area_variance + results.total_term_variance
        print(f"Sum of Components:     ${calculated:>15,.2f}")
        print(f"Direct Variance:       ${results.total_variance:>15,.2f}")
        print(f"Difference:            ${results.reconciliation_difference:>15,.2f}  ", end="")
        if results.reconciliation_check:
            print("✓ RECONCILED")
        else:
            print("✗ CHECK REQUIRED")

        print("\n" + "-"*80)
        print("TENANT-BY-TENANT SUMMARY")
        print("-"*80)
        print(f"{'Tenant':<25} {'Unit':<10} {'Rate Var':<12} {'Area Var':<12} {'Term Var':<12} {'Total':<12}")
        print("-"*80)

        for tenant in results.tenant_results:
            var = tenant['variances']
            print(f"{tenant['tenant_name']:<25} {tenant['unit_number']:<10} "
                  f"${var['rate_variance']:>10,.0f}  "
                  f"${var['area_variance']:>10,.0f}  "
                  f"${var['term_variance']:>10,.0f}  "
                  f"${var['total_variance']:>10,.0f}")

        print("="*80 + "\n")


def load_json_input(file_path: str) -> VarianceAnalysisInput:
    """Load and parse JSON input file"""
    with open(file_path, 'r') as f:
        data = json.load(f)

    return VarianceAnalysisInput(**data)


def save_json_results(results: VarianceAnalysisResults, file_path: str):
    """Save results to JSON file"""
    results_dict = {
        'summary': {
            'total_budget_revenue': results.total_budget_revenue,
            'total_actual_revenue': results.total_actual_revenue,
            'total_variance': results.total_variance,
            'total_rate_variance': results.total_rate_variance,
            'total_area_variance': results.total_area_variance,
            'total_term_variance': results.total_term_variance,
            'total_manual_adjustment': results.total_manual_adjustment,
            'reconciliation_check': results.reconciliation_check,
            'reconciliation_difference': results.reconciliation_difference
        },
        'tenant_results': results.tenant_results
    }

    with open(file_path, 'w') as f:
        json.dump(results_dict, f, indent=2)

    print(f"Results saved to: {file_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Rental Variance Decomposition Calculator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python rental_variance_calculator.py input.json
  python rental_variance_calculator.py input.json -o results.json
  python rental_variance_calculator.py input.json --output results.json --verbose

Variance Formula:
  Total Variance = (A×B×C) - (D×E×F)
  Rate Variance  = (B×C) × (A-D)
  Area Variance  = (C×D) × (B-E)
  Term Variance  = (D×E) × (C-F)

  Where: A=Actual Rate, B=Actual Area, C=Actual Term
         D=Budget Rate, E=Budget Area, F=Budget Term
        """
    )

    parser.add_argument(
        'input_file',
        help='Path to JSON input file'
    )

    parser.add_argument(
        '-o', '--output',
        help='Path to JSON output file (optional)',
        default=None
    )

    parser.add_argument(
        '-v', '--verbose',
        help='Print detailed tenant-by-tenant breakdown',
        action='store_true'
    )

    args = parser.parse_args()

    # Load input
    try:
        input_data = load_json_input(args.input_file)
    except Exception as e:
        print(f"Error loading input file: {e}", file=sys.stderr)
        sys.exit(1)

    # Calculate variances
    calculator = VarianceCalculator(input_data)
    results = calculator.calculate_all()

    # Print summary
    calculator.print_summary(results)

    # Print detailed breakdown if verbose
    if args.verbose:
        print("\n" + "="*80)
        print("DETAILED TENANT ANALYSIS")
        print("="*80)

        for tenant in results.tenant_results:
            print(f"\n{tenant['tenant_name']} - {tenant['unit_number']}")
            print("-"*80)

            actual = tenant['actual']
            budget = tenant['budget']
            var = tenant['variances']

            print(f"\nBudget: ${budget['rate_psf_year']:.2f}/sf/yr × {budget['area_sf']:.0f} sf × {budget['term_months']:.1f} mo = ${budget['revenue']:,.2f}")
            print(f"Actual: ${actual['rate_psf_year']:.2f}/sf/yr × {actual['area_sf']:.0f} sf × {actual['term_months']:.1f} mo = ${actual['revenue']:,.2f}")
            print(f"\nVariance Decomposition:")
            print(f"  Rate:  ({actual['area_sf']:.0f} × {actual['term_months']:.1f}) × (${actual['rate_psf_year']:.2f} - ${budget['rate_psf_year']:.2f})/12 = ${var['rate_variance']:,.2f}")
            print(f"  Area:  ({actual['term_months']:.1f} × ${budget['rate_psf_year']:.2f}/12) × ({actual['area_sf']:.0f} - {budget['area_sf']:.0f}) = ${var['area_variance']:,.2f}")
            print(f"  Term:  (${budget['rate_psf_year']:.2f}/12 × {budget['area_sf']:.0f}) × ({actual['term_months']:.1f} - {budget['term_months']:.1f}) = ${var['term_variance']:,.2f}")

            if var['manual_adjustment'] != 0:
                print(f"  Manual: ${var['manual_adjustment']:,.2f}")

            print(f"\nTotal Variance: ${var['total_variance']:,.2f}")

            if tenant['notes']:
                print(f"\nNotes: {tenant['notes']}")

    # Save results if output file specified
    if args.output:
        try:
            save_json_results(results, args.output)
        except Exception as e:
            print(f"Error saving output file: {e}", file=sys.stderr)
            sys.exit(1)

    print("\nAnalysis complete.")

    # Exit with status code based on reconciliation
    if not results.reconciliation_check:
        print("\nWARNING: Variance components do not reconcile exactly.", file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
