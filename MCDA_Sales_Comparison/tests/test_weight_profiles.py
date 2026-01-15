#!/usr/bin/env python3
"""
Test Suite for MCDA Sales Comparison Weight Profiles

Tests cover:
- Weight profile retrieval by property type
- Weight normalization (sum to 1.0)
- Dynamic weight allocation based on available data
- Variable direction configuration

TDD Approach: Write tests first, then implement weight_profiles.py
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestSalesWeightProfiles:
    """Tests for SALES_WEIGHT_PROFILES retrieval"""

    def test_industrial_default_profile_exists(self):
        """Industrial default profile should exist"""
        from weight_profiles import get_sales_weight_profile

        profile = get_sales_weight_profile('industrial_default')
        assert profile is not None
        assert len(profile) > 0

    def test_industrial_logistics_profile_exists(self):
        """Industrial logistics profile should exist"""
        from weight_profiles import get_sales_weight_profile

        profile = get_sales_weight_profile('industrial_logistics')
        assert profile is not None

    def test_industrial_manufacturing_profile_exists(self):
        """Industrial manufacturing profile should exist"""
        from weight_profiles import get_sales_weight_profile

        profile = get_sales_weight_profile('industrial_manufacturing')
        assert profile is not None

    def test_office_default_profile_exists(self):
        """Office default profile should exist"""
        from weight_profiles import get_sales_weight_profile

        profile = get_sales_weight_profile('office_default')
        assert profile is not None

    def test_unknown_profile_returns_default(self):
        """Unknown profile should return industrial_default"""
        from weight_profiles import get_sales_weight_profile

        profile = get_sales_weight_profile('unknown_profile')
        default = get_sales_weight_profile('industrial_default')
        assert profile == default


class TestWeightNormalization:
    """Tests for weight normalization (must sum to 1.0)"""

    def test_industrial_default_sums_to_one(self):
        """Industrial default weights should sum to 1.0"""
        from weight_profiles import get_sales_weight_profile

        profile = get_sales_weight_profile('industrial_default')
        total = sum(profile.values())
        assert total == pytest.approx(1.0, rel=0.01)

    def test_industrial_logistics_sums_to_one(self):
        """Industrial logistics weights should sum to 1.0"""
        from weight_profiles import get_sales_weight_profile

        profile = get_sales_weight_profile('industrial_logistics')
        total = sum(profile.values())
        assert total == pytest.approx(1.0, rel=0.01)

    def test_office_default_sums_to_one(self):
        """Office default weights should sum to 1.0"""
        from weight_profiles import get_sales_weight_profile

        profile = get_sales_weight_profile('office_default')
        total = sum(profile.values())
        assert total == pytest.approx(1.0, rel=0.01)

    def test_normalize_custom_weights(self):
        """Custom weights should be normalized to sum to 1.0"""
        from weight_profiles import normalize_weights

        custom = {
            'location_score': 20,
            'clear_height_feet': 15,
            'condition': 15
        }
        normalized = normalize_weights(custom)
        total = sum(normalized.values())
        assert total == pytest.approx(1.0, rel=0.01)

    def test_normalize_handles_percentages(self):
        """Weights specified as percentages should be handled"""
        from weight_profiles import normalize_weights

        custom = {
            'location_score': 40,  # 40%
            'clear_height_feet': 30,  # 30%
            'condition': 30  # 30%
        }
        normalized = normalize_weights(custom)
        total = sum(normalized.values())
        assert total == pytest.approx(1.0, rel=0.01)
        assert normalized['location_score'] == pytest.approx(0.4, rel=0.01)


class TestDynamicWeightAllocation:
    """Tests for dynamic weight allocation based on available data"""

    def test_allocate_with_all_vars_available(self):
        """All variables available should use base weights"""
        from weight_profiles import allocate_dynamic_weights

        available = {
            'location_score': True,
            'clear_height_feet': True,
            'condition': True,
            'effective_age_years': True,
            'loading_docks_total': True
        }
        base_weights = {
            'location_score': 0.20,
            'clear_height_feet': 0.15,
            'condition': 0.15,
            'effective_age_years': 0.15,
            'loading_docks_total': 0.10
        }
        result = allocate_dynamic_weights(available, base_weights)

        # All variables should be present
        for var in available:
            assert var in result

        # Should sum to approximately 1.0 (redistributed)
        assert sum(result.values()) == pytest.approx(1.0, rel=0.01)

    def test_allocate_redistributes_missing_vars(self):
        """Missing variables should have weight redistributed"""
        from weight_profiles import allocate_dynamic_weights

        available = {
            'location_score': True,
            'clear_height_feet': True,
            'condition': False,  # Not available
            'effective_age_years': True,
            'loading_docks_total': False  # Not available
        }
        base_weights = {
            'location_score': 0.20,
            'clear_height_feet': 0.20,
            'condition': 0.20,
            'effective_age_years': 0.20,
            'loading_docks_total': 0.20
        }
        result = allocate_dynamic_weights(available, base_weights)

        # Missing variables should not be in result
        assert 'condition' not in result or result['condition'] == 0
        assert 'loading_docks_total' not in result or result['loading_docks_total'] == 0

        # Available variables should have increased weights
        available_sum = sum(v for k, v in result.items() if available.get(k, False))
        assert available_sum == pytest.approx(1.0, rel=0.01)

    def test_allocate_empty_availability(self):
        """Empty availability should return empty or equal weights"""
        from weight_profiles import allocate_dynamic_weights

        available = {}
        base_weights = {
            'location_score': 0.50,
            'condition': 0.50
        }
        result = allocate_dynamic_weights(available, base_weights)

        # Should handle gracefully (empty dict or equal distribution)
        assert isinstance(result, dict)


class TestVariableDirection:
    """Tests for variable ranking direction configuration"""

    def test_get_variable_directions(self):
        """Variable directions should be properly configured"""
        from weight_profiles import get_variable_directions

        directions = get_variable_directions()

        # Higher is better (ascending=False for ranking)
        assert directions.get('clear_height_feet') == 'higher_is_better'
        assert directions.get('parking_ratio') == 'higher_is_better'
        assert directions.get('loading_docks_total') == 'higher_is_better'
        assert directions.get('location_score') == 'higher_is_better'

        # Lower is better (ascending=True for ranking)
        assert directions.get('effective_age_years') == 'lower_is_better'
        assert directions.get('building_size_sf') == 'closer_to_subject'

    def test_direction_for_condition(self):
        """Condition should be ordinal (excellent=1 is best)"""
        from weight_profiles import get_variable_directions

        directions = get_variable_directions()
        # Condition is encoded as ordinal: excellent=1, good=2, avg=3, fair=4, poor=5
        assert directions.get('condition') == 'lower_is_better'


class TestKeyVariablesForSales:
    """Tests for sales-specific key variables"""

    def test_industrial_has_key_variables(self):
        """Industrial profile should have key variables"""
        from weight_profiles import get_sales_weight_profile

        profile = get_sales_weight_profile('industrial_default')

        # Key variables for industrial sales
        expected_vars = [
            'location_score',
            'clear_height_feet',
            'condition',
            'effective_age_years',
            'loading_docks_total'
        ]

        for var in expected_vars:
            assert var in profile, f"Missing expected variable: {var}"

    def test_office_has_key_variables(self):
        """Office profile should have key variables"""
        from weight_profiles import get_sales_weight_profile

        profile = get_sales_weight_profile('office_default')

        # Key variables for office sales
        expected_vars = [
            'location_score',
            'building_class',
            'condition',
            'effective_age_years',
            'parking_ratio'
        ]

        for var in expected_vars:
            assert var in profile, f"Missing expected variable: {var}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
