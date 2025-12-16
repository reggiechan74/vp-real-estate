#!/usr/bin/env python3
"""
Test Suite for MCDA Sales Comparison Main Calculator

Tests cover:
- Property ranking on individual characteristics
- Composite score calculation with weights
- Full analysis pipeline (load → rank → score → price)
- Output structure validation

TDD Approach: Write tests first, then implement mcda_sales_calculator.py
"""

import pytest
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


# =============================================================================
# TEST DATA FIXTURES
# =============================================================================

@pytest.fixture
def sample_input_data():
    """Sample input data structure for testing"""
    return {
        "analysis_date": "2025-12-16",
        "valuation_date": "2025-01-15",
        "market_area": "Greater Hamilton Industrial",
        "property_type": "industrial",
        "subject_property": {
            "address": "2550 Industrial Parkway North, Hamilton, ON",
            "building_sf": 50000,
            "lot_size_acres": 5.0,
            "clear_height_feet": 28,
            "loading_docks_total": 6,
            "year_built": 2005,
            "effective_age_years": 15,
            "condition": "average",
            "location_score": 75,
            "highway_frontage": True
        },
        "comparable_sales": [
            {
                "id": "COMP_1",
                "address": "2480 Industrial Parkway North, Hamilton, ON",
                "sale_price": 4650000,
                "sale_date": "2024-09-15",
                "building_sf": 48500,
                "lot_size_acres": 4.9,
                "clear_height_feet": 28,
                "loading_docks_total": 6,
                "year_built": 2006,
                "effective_age_years": 14,
                "condition": "average",
                "location_score": 76,
                "highway_frontage": True,
                "property_rights": "fee_simple",
                "financing": {"type": "cash"},
                "conditions_of_sale": {"arms_length": True}
            },
            {
                "id": "COMP_2",
                "address": "2650 Parkdale Avenue North, Hamilton, ON",
                "sale_price": 4100000,
                "sale_date": "2024-07-22",
                "building_sf": 52000,
                "lot_size_acres": 5.2,
                "clear_height_feet": 26,
                "loading_docks_total": 6,
                "year_built": 2004,
                "effective_age_years": 16,
                "condition": "average",
                "location_score": 70,
                "highway_frontage": False,
                "property_rights": "fee_simple",
                "financing": {"type": "cash"},
                "conditions_of_sale": {"arms_length": True}
            },
            {
                "id": "COMP_3",
                "address": "2320 Industrial Parkway North, Hamilton, ON",
                "sale_price": 4850000,
                "sale_date": "2024-06-10",
                "building_sf": 47000,
                "lot_size_acres": 4.7,
                "clear_height_feet": 30,
                "loading_docks_total": 7,
                "year_built": 2008,
                "effective_age_years": 12,
                "condition": "good",
                "location_score": 78,
                "highway_frontage": True,
                "property_rights": "fee_simple",
                "financing": {"type": "cash"},
                "conditions_of_sale": {"arms_length": True}
            },
            {
                "id": "COMP_4",
                "address": "1150 South Service Road, Stoney Creek, ON",
                "sale_price": 4400000,
                "sale_date": "2024-08-05",
                "building_sf": 50000,
                "lot_size_acres": 5.0,
                "clear_height_feet": 28,
                "loading_docks_total": 6,
                "year_built": 2003,
                "effective_age_years": 17,
                "condition": "average",
                "location_score": 72,
                "highway_frontage": True,
                "property_rights": "fee_simple",
                "financing": {"type": "cash"},
                "conditions_of_sale": {"arms_length": True}
            }
        ],
        "market_parameters": {
            "appreciation_rate_annual": 3.5
        }
    }


# =============================================================================
# RANKING TESTS
# =============================================================================

class TestPropertyRanking:
    """Tests for rank_properties() function"""

    def test_rank_higher_is_better(self, sample_input_data):
        """Higher values should rank better for 'higher_is_better' variables"""
        from mcda_sales_calculator import rank_properties

        # Add subject to the list for ranking
        all_properties = sample_input_data['comparable_sales'] + [sample_input_data['subject_property']]

        rankings = rank_properties(all_properties, 'clear_height_feet', 'higher_is_better')

        # COMP_3 has 30ft (highest) should rank 1
        # Find COMP_3's rank
        comp3_rank = rankings[sample_input_data['comparable_sales'][2]['address']]
        assert comp3_rank == 1

    def test_rank_lower_is_better(self, sample_input_data):
        """Lower values should rank better for 'lower_is_better' variables"""
        from mcda_sales_calculator import rank_properties

        all_properties = sample_input_data['comparable_sales'] + [sample_input_data['subject_property']]

        rankings = rank_properties(all_properties, 'effective_age_years', 'lower_is_better')

        # COMP_3 has 12 years (lowest) should rank 1
        comp3_rank = rankings[sample_input_data['comparable_sales'][2]['address']]
        assert comp3_rank == 1

    def test_rank_handles_ties(self, sample_input_data):
        """Ties should be ranked with average rank"""
        from mcda_sales_calculator import rank_properties

        all_properties = sample_input_data['comparable_sales'] + [sample_input_data['subject_property']]

        # Clear height: COMP_1, COMP_4, and Subject all have 28ft
        rankings = rank_properties(all_properties, 'clear_height_feet', 'higher_is_better')

        # Tied properties should have same rank (average of their positions)
        comp1_rank = rankings[sample_input_data['comparable_sales'][0]['address']]
        comp4_rank = rankings[sample_input_data['comparable_sales'][3]['address']]
        subject_rank = rankings[sample_input_data['subject_property']['address']]

        assert comp1_rank == comp4_rank == subject_rank


# =============================================================================
# COMPOSITE SCORE TESTS
# =============================================================================

class TestCompositeScore:
    """Tests for calculate_composite_scores() function"""

    def test_composite_score_calculation(self, sample_input_data):
        """Composite score should be weighted sum of variable ranks"""
        from mcda_sales_calculator import calculate_composite_scores

        all_properties = sample_input_data['comparable_sales'] + [sample_input_data['subject_property']]

        weights = {
            'location_score': 0.30,
            'clear_height_feet': 0.25,
            'effective_age_years': 0.25,
            'highway_frontage': 0.20
        }

        scores = calculate_composite_scores(all_properties, weights)

        # All properties should have scores
        assert len(scores) == len(all_properties)

        # Scores should be positive
        for addr, score in scores.items():
            assert score > 0, f"Score for {addr} should be positive"

    def test_subject_score_included(self, sample_input_data):
        """Subject property should be included in scoring"""
        from mcda_sales_calculator import calculate_composite_scores

        all_properties = sample_input_data['comparable_sales'] + [sample_input_data['subject_property']]

        weights = {'location_score': 0.50, 'clear_height_feet': 0.50}

        scores = calculate_composite_scores(all_properties, weights)

        subject_addr = sample_input_data['subject_property']['address']
        assert subject_addr in scores

    def test_lower_score_indicates_better_property(self, sample_input_data):
        """Lower composite score should indicate better property"""
        from mcda_sales_calculator import calculate_composite_scores

        # COMP_3 is the best (highest clear height, lowest age, highest location)
        all_properties = sample_input_data['comparable_sales'] + [sample_input_data['subject_property']]

        weights = {
            'location_score': 0.33,
            'clear_height_feet': 0.33,
            'effective_age_years': 0.34
        }

        scores = calculate_composite_scores(all_properties, weights)

        # COMP_3 should have lowest (best) score
        comp3_addr = sample_input_data['comparable_sales'][2]['address']
        comp3_score = scores[comp3_addr]

        # Should be among the lowest scores
        all_scores = list(scores.values())
        assert comp3_score == min(all_scores), "COMP_3 should have lowest (best) score"


# =============================================================================
# FULL ANALYSIS TESTS
# =============================================================================

class TestFullAnalysis:
    """Tests for run_analysis() function"""

    def test_analysis_returns_complete_results(self, sample_input_data):
        """Full analysis should return complete result structure"""
        from mcda_sales_calculator import run_analysis

        results = run_analysis(sample_input_data)

        # Check required output keys
        assert 'subject_property' in results
        assert 'comparable_analysis' in results
        assert 'composite_scores' in results
        assert 'value_indication' in results
        assert 'analysis_summary' in results

    def test_analysis_includes_psf_values(self, sample_input_data):
        """Analysis should calculate PSF values for comparables"""
        from mcda_sales_calculator import run_analysis

        results = run_analysis(sample_input_data)

        for comp in results['comparable_analysis']:
            assert 'price_psf' in comp
            assert comp['price_psf'] > 0

    def test_analysis_indicates_value_range(self, sample_input_data):
        """Analysis should provide value range (not just point estimate)"""
        from mcda_sales_calculator import run_analysis

        results = run_analysis(sample_input_data)

        assert 'indicated_value_psf' in results['value_indication']
        assert 'value_range_psf' in results['value_indication']

        low, high = results['value_indication']['value_range_psf']
        indicated = results['value_indication']['indicated_value_psf']

        # Indicated should be within range
        assert low <= indicated <= high

    def test_analysis_calculates_total_value(self, sample_input_data):
        """Analysis should calculate total indicated value"""
        from mcda_sales_calculator import run_analysis

        results = run_analysis(sample_input_data)

        psf = results['value_indication']['indicated_value_psf']
        total = results['value_indication']['indicated_value_total']
        building_sf = sample_input_data['subject_property']['building_sf']

        assert total == pytest.approx(psf * building_sf, rel=0.01)


# =============================================================================
# OUTPUT STRUCTURE TESTS
# =============================================================================

class TestOutputStructure:
    """Tests for output structure and format"""

    def test_comparable_analysis_includes_rankings(self, sample_input_data):
        """Each comparable should have variable rankings"""
        from mcda_sales_calculator import run_analysis

        results = run_analysis(sample_input_data)

        for comp in results['comparable_analysis']:
            assert 'variable_ranks' in comp
            # Should have ranks for key variables
            assert len(comp['variable_ranks']) > 0

    def test_analysis_summary_structure(self, sample_input_data):
        """Analysis summary should have required fields"""
        from mcda_sales_calculator import run_analysis

        results = run_analysis(sample_input_data)

        summary = results['analysis_summary']
        assert 'analysis_date' in summary
        assert 'property_type' in summary
        assert 'comparables_used' in summary
        assert 'weights_profile' in summary
        assert 'methodology' in summary

    def test_output_json_serializable(self, sample_input_data):
        """Results should be JSON serializable"""
        from mcda_sales_calculator import run_analysis

        results = run_analysis(sample_input_data)

        # Should not raise exception
        json_str = json.dumps(results)
        assert len(json_str) > 0


# =============================================================================
# EDGE CASES
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling"""

    def test_handles_missing_optional_fields(self, sample_input_data):
        """Should handle missing optional fields gracefully"""
        from mcda_sales_calculator import run_analysis

        # Remove some optional fields
        for comp in sample_input_data['comparable_sales']:
            if 'office_finish_pct' in comp:
                del comp['office_finish_pct']

        # Should not raise exception
        results = run_analysis(sample_input_data)
        assert results['value_indication']['indicated_value_psf'] is not None

    def test_minimum_comparables(self, sample_input_data):
        """Should work with minimum 3 comparables"""
        from mcda_sales_calculator import run_analysis

        # Keep only 3 comparables
        sample_input_data['comparable_sales'] = sample_input_data['comparable_sales'][:3]

        results = run_analysis(sample_input_data)
        assert results['value_indication']['indicated_value_psf'] is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
