#!/usr/bin/env python3
"""
Test Suite for MCDA Sales Comparison Validation Module

Tests cover:
- Input data validation
- Sale price validation
- Transaction validation (property rights, financing, conditions)
- Cash equivalent adjustments
- Time/market condition adjustments
- Monotonicity validation for score-to-price mapping

TDD Approach: Write tests first, then implement validation.py to pass them.
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestSalePriceValidation:
    """Tests for validate_sale_price() function"""

    def test_valid_sale_price_typical_industrial(self):
        """Industrial property with typical PSF should pass validation"""
        from validation import validate_sale_price

        comparable = {
            'sale_price': 4650000,
            'building_sf': 48500,
            'property_type': 'industrial'
        }
        errors = validate_sale_price(comparable)
        assert len(errors) == 0, f"Unexpected errors: {errors}"

    def test_sale_price_too_low_industrial(self):
        """Industrial property with <$20/SF should trigger warning"""
        from validation import validate_sale_price

        comparable = {
            'sale_price': 500000,
            'building_sf': 50000,  # $10/SF
            'property_type': 'industrial'
        }
        errors = validate_sale_price(comparable)
        assert len(errors) > 0
        assert any('outside typical range' in e.lower() for e in errors)

    def test_sale_price_too_high_industrial(self):
        """Industrial property with >$500/SF should trigger warning"""
        from validation import validate_sale_price

        comparable = {
            'sale_price': 30000000,
            'building_sf': 50000,  # $600/SF
            'property_type': 'industrial'
        }
        errors = validate_sale_price(comparable)
        assert len(errors) > 0

    def test_valid_sale_price_typical_office(self):
        """Office property with typical PSF should pass validation"""
        from validation import validate_sale_price

        comparable = {
            'sale_price': 15000000,
            'building_sf': 50000,  # $300/SF
            'property_type': 'office'
        }
        errors = validate_sale_price(comparable)
        assert len(errors) == 0


class TestTransactionValidation:
    """Tests for validate_transaction() function"""

    def test_valid_fee_simple_cash_arms_length(self):
        """Standard fee simple, cash, arm's length transaction should pass"""
        from validation import validate_transaction

        comparable = {
            'property_rights': 'fee_simple',
            'financing': {'type': 'cash'},
            'conditions_of_sale': {'arms_length': True}
        }
        errors, warnings = validate_transaction(comparable)
        assert len(errors) == 0
        assert len(warnings) == 0

    def test_leased_fee_warning(self):
        """Leased fee interest should generate warning"""
        from validation import validate_transaction

        comparable = {
            'property_rights': 'leased_fee',
            'financing': {'type': 'cash'},
            'conditions_of_sale': {'arms_length': True}
        }
        errors, warnings = validate_transaction(comparable)
        assert len(errors) == 0
        assert len(warnings) > 0
        assert any('non-fee simple' in w.lower() for w in warnings)

    def test_seller_financing_warning(self):
        """Seller financing should generate warning"""
        from validation import validate_transaction

        comparable = {
            'property_rights': 'fee_simple',
            'financing': {'type': 'seller_vtb', 'rate': 4.0, 'market_rate': 6.5},
            'conditions_of_sale': {'arms_length': True}
        }
        errors, warnings = validate_transaction(comparable)
        assert len(errors) == 0
        assert len(warnings) > 0
        assert any('cash equivalent' in w.lower() or 'seller' in w.lower() for w in warnings)

    def test_non_arms_length_error(self):
        """Non-arm's length sale should generate error (exclude from analysis)"""
        from validation import validate_transaction

        comparable = {
            'property_rights': 'fee_simple',
            'financing': {'type': 'cash'},
            'conditions_of_sale': {'arms_length': False}
        }
        errors, warnings = validate_transaction(comparable)
        assert len(errors) > 0
        assert any("non-arm's length" in e.lower() for e in errors)


class TestCashEquivalentAdjustment:
    """Tests for compute_cash_equivalent() function"""

    def test_no_adjustment_needed(self):
        """Cash transaction needs no adjustment"""
        from validation import compute_cash_equivalent

        comparable = {
            'sale_price': 4650000,
            'cash_equivalent_adjustment_pct': 0
        }
        result = compute_cash_equivalent(comparable)
        assert result['cash_equivalent_price'] == 4650000
        assert result['adjustment_pct'] == 0

    def test_positive_adjustment(self):
        """Below-market financing requires positive adjustment"""
        from validation import compute_cash_equivalent

        comparable = {
            'sale_price': 4650000,
            'cash_equivalent_adjustment_pct': -5.0  # 5% discount for below-market financing
        }
        result = compute_cash_equivalent(comparable)
        assert result['cash_equivalent_price'] == pytest.approx(4417500, rel=0.001)
        assert result['adjustment_pct'] == -5.0

    def test_missing_adjustment_defaults_to_zero(self):
        """Missing adjustment should default to 0"""
        from validation import compute_cash_equivalent

        comparable = {'sale_price': 4650000}
        result = compute_cash_equivalent(comparable)
        assert result['cash_equivalent_price'] == 4650000


class TestTimeAdjustment:
    """Tests for validate_time_adjustment() function"""

    def test_recent_sale_no_adjustment(self):
        """Sale within 3 months of valuation date needs no adjustment"""
        from validation import validate_time_adjustment

        comparable = {'sale_date': '2024-11-15'}
        valuation_date = '2025-01-15'
        result = validate_time_adjustment(comparable, valuation_date)

        assert result['requires_time_adjustment'] == False
        assert result['suggested_adjustment_pct'] == 0

    def test_older_sale_requires_adjustment(self):
        """Sale more than 3 months before valuation requires adjustment"""
        from validation import validate_time_adjustment

        comparable = {'sale_date': '2024-05-15'}
        valuation_date = '2025-01-15'
        result = validate_time_adjustment(comparable, valuation_date)

        assert result['requires_time_adjustment'] == True
        assert result['months_difference'] > 6
        # 8 months * 0.3%/month ≈ 2.4%
        assert result['suggested_adjustment_pct'] > 2.0

    def test_future_sale_date(self):
        """Sale date after valuation date should handle gracefully"""
        from validation import validate_time_adjustment

        comparable = {'sale_date': '2025-03-15'}
        valuation_date = '2025-01-15'
        result = validate_time_adjustment(comparable, valuation_date)

        # Negative months difference (future sale)
        assert result['months_difference'] < 0


class TestMonotonicityValidation:
    """Tests for validate_monotonicity() function"""

    def test_perfect_monotonic_decreasing(self):
        """Perfect monotonic relationship (better score = higher price)"""
        from validation import validate_monotonicity

        # Lower score = better property = higher price
        scores_prices = [
            (1.0, 120.0),  # Best property, highest price
            (2.0, 100.0),
            (3.0, 90.0),
            (4.0, 80.0),   # Worst property, lowest price
        ]
        result = validate_monotonicity(scores_prices)
        assert result['violations'] == 0
        assert result['requires_monotone_fit'] == False

    def test_monotonicity_violations(self):
        """Data with monotonicity violations should be detected"""
        from validation import validate_monotonicity

        # Score 3.0 has higher price than score 2.0 - violation
        scores_prices = [
            (1.0, 120.0),
            (2.0, 85.0),   # Lower price
            (3.0, 100.0),  # Higher price - VIOLATION
            (4.0, 80.0),
        ]
        result = validate_monotonicity(scores_prices)
        assert result['violations'] > 0
        assert result['requires_monotone_fit'] == True

    def test_ties_in_scores(self):
        """Tied scores should be handled gracefully"""
        from validation import validate_monotonicity

        scores_prices = [
            (1.0, 120.0),
            (2.0, 100.0),
            (2.0, 95.0),   # Tied score, slightly lower price - OK
            (3.0, 85.0),
        ]
        result = validate_monotonicity(scores_prices)
        # Ties at same score are acceptable
        assert result['requires_monotone_fit'] == False or result['violations'] == 0


class TestInputValidation:
    """Tests for validate_input_data() function (semantic validation)

    Note: These tests use use_schema=False to test MCDA-specific semantic
    validation independently of JSON Schema validation. The MCDA calculator
    has flexible field handling (e.g., valuation_date at root OR in
    market_parameters) that differs from the strict unified schema.

    For JSON Schema validation tests, see test_schema_validation below.
    """

    def test_valid_complete_input(self):
        """Valid input with all required fields should pass semantic validation"""
        from validation import validate_input_data

        data = {
            'analysis_date': '2025-12-16',
            'valuation_date': '2025-01-15',
            'market_area': 'Greater Hamilton Industrial',
            'property_type': 'industrial',
            'subject_property': {
                'address': '2550 Industrial Parkway North, Hamilton, ON',
                'building_sf': 50000,
                'is_subject': True
            },
            'comparable_sales': [
                {
                    'address': '2480 Industrial Parkway North',
                    'sale_price': 4650000,
                    'sale_date': '2024-09-15',
                    'building_sf': 48500,
                    'is_subject': False
                },
                {
                    'address': '2650 Parkdale Avenue North',
                    'sale_price': 4100000,
                    'sale_date': '2024-07-22',
                    'building_sf': 52000,
                    'is_subject': False
                },
                {
                    'address': '2320 Industrial Parkway North',
                    'sale_price': 4850000,
                    'sale_date': '2024-06-10',
                    'building_sf': 47000,
                    'is_subject': False
                }
            ]
        }
        # Test semantic validation only (use_schema=False)
        errors = validate_input_data(data, use_schema=False)
        assert len(errors) == 0, f"Unexpected errors: {errors}"

    def test_missing_required_field(self):
        """Missing required field should fail validation"""
        from validation import validate_input_data

        data = {
            'analysis_date': '2025-12-16',
            # Missing valuation_date
            'subject_property': {
                'address': 'Test',
                'building_sf': 50000
            },
            'comparable_sales': []
        }
        errors = validate_input_data(data)
        assert len(errors) > 0

    def test_insufficient_comparables(self):
        """Less than 3 comparables should fail semantic validation"""
        from validation import validate_input_data

        data = {
            'analysis_date': '2025-12-16',
            'valuation_date': '2025-01-15',
            'subject_property': {
                'address': 'Test',
                'building_sf': 50000
            },
            'comparable_sales': [
                {'address': 'Comp1', 'sale_price': 1000000, 'sale_date': '2024-01-01', 'building_sf': 50000}
            ]
        }
        # Test semantic validation only (use_schema=False)
        errors = validate_input_data(data, use_schema=False)
        assert len(errors) > 0
        assert any('minimum' in e.lower() or '3' in e for e in errors)


class TestSchemaValidation:
    """Tests for JSON Schema validation against unified schema"""

    def test_schema_validation_with_complete_data(self):
        """Complete data matching unified schema should pass schema validation"""
        from validation import validate_against_schema, JSONSCHEMA_AVAILABLE

        if not JSONSCHEMA_AVAILABLE:
            pytest.skip("jsonschema not installed")

        # Data matching the unified schema (all required fields per schema)
        data = {
            'subject_property': {
                'address': '2550 Industrial Parkway North, Hamilton, ON',
                'property_type': 'industrial',
                'property_rights': 'fee_simple',
                'building_sf': 50000,
                'lot_size_acres': 5.0
            },
            'comparable_sales': [
                {
                    'address': '2480 Industrial Parkway North, Hamilton',
                    'sale_price': 4650000,
                    'sale_date': '2024-09-15',
                    'property_rights': 'fee_simple',  # Required by schema
                    'building_sf': 48500
                },
                {
                    'address': '2650 Parkdale Avenue North, Hamilton',
                    'sale_price': 4100000,
                    'sale_date': '2024-07-22',
                    'property_rights': 'fee_simple',  # Required by schema
                    'building_sf': 52000
                },
                {
                    'address': '2320 Industrial Parkway North, Hamilton',
                    'sale_price': 4850000,
                    'sale_date': '2024-06-10',
                    'property_rights': 'fee_simple',  # Required by schema
                    'building_sf': 47000
                }
            ],
            'market_parameters': {
                'valuation_date': '2025-01-15',
                'appreciation_rate_annual': 3.5,
                'cap_rate': 7.0  # Required by schema
            }
        }

        is_valid, errors = validate_against_schema(data)
        assert is_valid, f"Schema validation failed: {errors}"

    def test_schema_validation_missing_market_parameters(self):
        """Missing market_parameters should fail schema validation"""
        from validation import validate_against_schema, JSONSCHEMA_AVAILABLE

        if not JSONSCHEMA_AVAILABLE:
            pytest.skip("jsonschema not installed")

        data = {
            'subject_property': {
                'address': 'Test Address',
                'property_type': 'industrial',
                'property_rights': 'fee_simple'
            },
            'comparable_sales': []
            # Missing market_parameters
        }

        is_valid, errors = validate_against_schema(data)
        assert not is_valid
        assert any('market_parameters' in e for e in errors)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
