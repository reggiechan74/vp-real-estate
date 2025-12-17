#!/usr/bin/env python3
"""
Unit Tests for CUSPAP-Compliant Paired Sales Analyzer

Tests cover:
- Transaction verification (arm's-length, financing)
- Paired sales isolation methodology
- Quality-weighted reconciliation
- Disclosure tracking
- Edge cases and error handling

Author: Claude Code
Created: 2025-12-16
"""

import unittest
import json
from datetime import date
from paired_sales_analyzer import (
    PairedSalesAnalyzer,
    PairedSalesResult,
    CUSPAPDisclosure,
    TransactionAdjustment,
    DerivedAdjustments,
    DisclosureCategory,
    DerivationMethod,
    safe_mean,
    safe_median,
    safe_stdev,
    coefficient_of_variation
)


class TestSafeStatistics(unittest.TestCase):
    """Test safe statistics functions."""

    def test_safe_mean_empty(self):
        """Empty list returns None."""
        self.assertIsNone(safe_mean([]))

    def test_safe_mean_valid(self):
        """Valid list returns correct mean."""
        self.assertEqual(safe_mean([1, 2, 3, 4, 5]), 3.0)

    def test_safe_median_empty(self):
        """Empty list returns None."""
        self.assertIsNone(safe_median([]))

    def test_safe_median_valid(self):
        """Valid list returns correct median."""
        self.assertEqual(safe_median([1, 2, 3, 4, 5]), 3)

    def test_safe_stdev_insufficient(self):
        """Single value returns None."""
        self.assertIsNone(safe_stdev([5]))

    def test_safe_stdev_valid(self):
        """Valid list returns correct stdev."""
        result = safe_stdev([1, 2, 3, 4, 5])
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 1.5811, places=3)

    def test_coefficient_of_variation(self):
        """CV calculation."""
        # CV = stdev / mean
        result = coefficient_of_variation([10, 10, 10, 10])  # No variation
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 0.0, places=3)


class TestTransactionVerification(unittest.TestCase):
    """Test arm's-length and financing verification."""

    def setUp(self):
        """Set up test data."""
        self.subject = {
            'address': '100 Test Street',
            'property_type': 'industrial',
            'property_rights': 'fee_simple',
            'size_sf': 50000
        }

    def test_arms_length_exclusion(self):
        """Non-arm's-length sale without quantification is excluded."""
        comparables = [
            {
                'address': '200 Test Ave',
                'sale_price': 5000000,
                'sale_date': '2024-06-01',
                'size_sf': 50000,
                'property_rights': 'fee_simple',
                'conditions_of_sale': {'arms_length': False}  # No motivation_discount_pct
            },
            {
                'address': '300 Test Blvd',
                'sale_price': 4500000,
                'sale_date': '2024-06-15',
                'size_sf': 50000,
                'property_rights': 'fee_simple',
                'conditions_of_sale': {'arms_length': True}
            },
            {
                'address': '400 Test Rd',
                'sale_price': 4800000,
                'sale_date': '2024-07-01',
                'size_sf': 50000,
                'property_rights': 'fee_simple'
            }
        ]

        analyzer = PairedSalesAnalyzer(comparables, self.subject)
        analyzer.comparables = analyzer._verify_and_adjust_transactions()

        # Should have excluded one non-arm's-length sale
        self.assertEqual(len(analyzer.comparables), 2)

        # Check disclosure was added
        exclusion_disclosures = [
            d for d in analyzer.disclosures
            if 'excluded as non-arm' in d.description.lower()
        ]
        self.assertEqual(len(exclusion_disclosures), 1)

    def test_arms_length_adjustment(self):
        """Non-arm's-length sale with quantified discount is adjusted."""
        comparables = [
            {
                'address': '200 Test Ave',
                'sale_price': 5000000,
                'sale_date': '2024-06-01',
                'size_sf': 50000,
                'property_rights': 'fee_simple',
                'conditions_of_sale': {
                    'arms_length': False,
                    'motivation_discount_pct': 10  # 10% below market
                }
            },
            {
                'address': '300 Test Blvd',
                'sale_price': 4500000,
                'sale_date': '2024-06-15',
                'size_sf': 50000,
                'property_rights': 'fee_simple'
            }
        ]

        analyzer = PairedSalesAnalyzer(comparables, self.subject)
        analyzer.comparables = analyzer._verify_and_adjust_transactions()

        # Sale should be adjusted, not excluded
        self.assertEqual(len(analyzer.comparables), 2)

        # Find the adjusted comparable
        adjusted_comp = next(c for c in analyzer.comparables if '200 Test Ave' in c['address'])
        self.assertEqual(adjusted_comp['sale_price'], 5500000)  # 5M + 10% = 5.5M
        self.assertEqual(adjusted_comp['_original_price'], 5000000)

    def test_financing_adjustment(self):
        """Below-market financing triggers cash equivalency adjustment."""
        comparables = [
            {
                'address': '200 Test Ave',
                'sale_price': 5000000,
                'sale_date': '2024-06-01',
                'size_sf': 50000,
                'property_rights': 'fee_simple',
                'financing': {
                    'type': 'seller_vtb',
                    'rate': 3.0,        # Below market
                    'market_rate': 6.0,  # Market rate
                    'loan_amount': 3000000,
                    'term_years': 5
                }
            },
            {
                'address': '300 Test Blvd',
                'sale_price': 4500000,
                'sale_date': '2024-06-15',
                'size_sf': 50000,
                'property_rights': 'fee_simple',
                'financing': {'type': 'cash'}
            }
        ]

        analyzer = PairedSalesAnalyzer(comparables, self.subject)
        analyzer.comparables = analyzer._verify_and_adjust_transactions()

        # Both should be verified
        self.assertEqual(len(analyzer.comparables), 2)

        # VTB sale should have financing adjustment (negative)
        vtb_comp = next(c for c in analyzer.comparables if '200 Test Ave' in c['address'])
        self.assertIn('financing', vtb_comp.get('_adjustments', {}))
        self.assertLess(vtb_comp['sale_price'], 5000000)  # Adjusted down


class TestPairSimilarity(unittest.TestCase):
    """Test paired sales similarity assessment."""

    def setUp(self):
        """Set up test data."""
        self.subject = {
            'address': '100 Test Street',
            'property_type': 'industrial',
            'size_sf': 50000
        }
        self.comparables = [
            {
                'address': 'Comp A',
                'sale_price': 5000000,
                'sale_date': '2024-06-01',
                'size_sf': 50000,
                'year_built': 2010,
                'location_submarket': 'East Industrial',
                'zoning': 'M2',
                'property_rights': 'fee_simple'
            },
            {
                'address': 'Comp B',
                'sale_price': 4500000,
                'sale_date': '2024-07-01',
                'size_sf': 52000,  # 4% larger - within strict threshold
                'year_built': 2012,  # 2 years newer - within strict threshold
                'location_submarket': 'East Industrial',
                'zoning': 'M2',
                'property_rights': 'fee_simple'
            },
            {
                'address': 'Comp C',
                'sale_price': 4000000,
                'sale_date': '2024-06-15',
                'size_sf': 80000,  # 60% larger - outside threshold
                'year_built': 2000,  # 10 years older - at threshold edge
                'location_submarket': 'West Industrial',
                'zoning': 'M1',
                'property_rights': 'fee_simple'
            }
        ]

    def test_strict_similarity_valid_pair(self):
        """Similar properties pass strict threshold."""
        analyzer = PairedSalesAnalyzer(
            self.comparables[:2],
            self.subject,
            strict_mode=True
        )
        analyzer.comparables = self.comparables[:2]
        analyzer._normalize_prices()

        is_valid, score, notes = analyzer._is_similar_pair(
            analyzer.comparables[0],
            analyzer.comparables[1],
            exclude_characteristic='condition'
        )

        self.assertTrue(is_valid)
        self.assertGreater(score, 0.7)  # High similarity

    def test_strict_similarity_invalid_pair(self):
        """Dissimilar properties fail strict threshold."""
        analyzer = PairedSalesAnalyzer(
            [self.comparables[0], self.comparables[2]],
            self.subject,
            strict_mode=True
        )
        analyzer.comparables = [self.comparables[0], self.comparables[2]]
        analyzer._normalize_prices()

        is_valid, score, notes = analyzer._is_similar_pair(
            analyzer.comparables[0],
            analyzer.comparables[1],
            exclude_characteristic='condition'
        )

        self.assertFalse(is_valid)  # Should fail strict thresholds


class TestQualityWeightedReconciliation(unittest.TestCase):
    """Test quality-weighted reconciliation."""

    def setUp(self):
        """Set up test data."""
        self.subject = {'address': 'Test', 'property_type': 'industrial', 'size_sf': 50000}
        self.comparables = [
            {'address': f'Comp {i}', 'sale_price': 5000000, 'sale_date': '2024-06-01', 'size_sf': 50000}
            for i in range(5)
        ]

    def test_weighted_reconciliation(self):
        """Higher similarity pairs get more weight."""
        analyzer = PairedSalesAnalyzer(self.comparables, self.subject)

        adjustments = [10.0, 12.0, 8.0]
        similarity_scores = [0.9, 0.5, 0.6]  # First pair much better

        reconciled = analyzer._quality_weighted_reconciliation(adjustments, similarity_scores)

        # Weighted average should be closer to 10 (high similarity pair)
        # Simple average would be 10.0
        # Weighted: (10*0.9 + 12*0.5 + 8*0.6) / (0.9 + 0.5 + 0.6) = 19.8 / 2.0 = 9.9
        self.assertIsNotNone(reconciled)
        self.assertAlmostEqual(reconciled, 9.9, places=1)

    def test_equal_weights(self):
        """Equal similarity scores produce simple mean."""
        analyzer = PairedSalesAnalyzer(self.comparables, self.subject)

        adjustments = [10.0, 12.0, 8.0]
        similarity_scores = [0.8, 0.8, 0.8]

        reconciled = analyzer._quality_weighted_reconciliation(adjustments, similarity_scores)
        simple_mean = sum(adjustments) / len(adjustments)

        self.assertAlmostEqual(reconciled, simple_mean, places=3)


class TestDisclosureTracking(unittest.TestCase):
    """Test CUSPAP disclosure tracking."""

    def setUp(self):
        """Set up test data."""
        self.subject = {'address': 'Test', 'property_type': 'industrial', 'size_sf': 50000}

    def test_limited_data_disclosure(self):
        """Limited comparables triggers disclosure."""
        comparables = [
            {'address': 'Comp 1', 'sale_price': 5000000, 'sale_date': '2024-06-01', 'size_sf': 50000},
            {'address': 'Comp 2', 'sale_price': 4500000, 'sale_date': '2024-07-01', 'size_sf': 50000}
        ]

        analyzer = PairedSalesAnalyzer(comparables, self.subject)

        # Should have disclosure about limited data
        data_limit_disclosures = [
            d for d in analyzer.disclosures
            if d.category == DisclosureCategory.DATA_LIMITATION
        ]
        self.assertGreater(len(data_limit_disclosures), 0)

    def test_industry_default_disclosure(self):
        """Using industry default triggers disclosure."""
        comparables = [
            {'address': 'Comp 1', 'sale_price': 5000000, 'sale_date': '2024-06-01', 'size_sf': 50000},
            {'address': 'Comp 2', 'sale_price': 4500000, 'sale_date': '2024-07-01', 'size_sf': 50000}
        ]

        analyzer = PairedSalesAnalyzer(comparables, self.subject)
        result = analyzer._create_default_result(
            'test_characteristic',
            'percent',
            5.0,
            'Test source'
        )

        # Should have non-market-derived disclosure
        self.assertFalse(result.market_supported)
        self.assertEqual(result.derivation_method, DerivationMethod.INDUSTRY_DEFAULT)

        non_market_disclosures = [
            d for d in analyzer.disclosures
            if d.category == DisclosureCategory.NON_MARKET_DERIVED
        ]
        self.assertGreater(len(non_market_disclosures), 0)

    def test_disclosure_report_generation(self):
        """Disclosure report is properly generated."""
        comparables = [
            {'address': f'Comp {i}', 'sale_price': 5000000 + i*100000, 'sale_date': '2024-06-01', 'size_sf': 50000}
            for i in range(5)
        ]

        analyzer = PairedSalesAnalyzer(comparables, self.subject)
        analyzer.analyze_all()

        report = analyzer.get_cuspap_disclosure_report()

        self.assertIn('CUSPAP DISCLOSURE REPORT', report)
        self.assertIn('TRANSACTION VERIFICATION SUMMARY', report)
        self.assertIn('Property Type: industrial', report)


class TestConfidenceLevels(unittest.TestCase):
    """Test confidence level determination."""

    def setUp(self):
        """Set up test data."""
        self.subject = {'address': 'Test', 'property_type': 'industrial', 'size_sf': 50000}
        self.comparables = [
            {'address': f'Comp {i}', 'sale_price': 5000000, 'sale_date': '2024-06-01', 'size_sf': 50000}
            for i in range(5)
        ]

    def test_high_confidence(self):
        """5+ pairs with low CV = high confidence."""
        analyzer = PairedSalesAnalyzer(self.comparables, self.subject)

        confidence = analyzer._determine_confidence(
            n_pairs=5,
            cv=0.15,  # Low CV
            adjustments=[10, 11, 10, 11, 10]
        )

        self.assertEqual(confidence, 'high')

    def test_medium_confidence(self):
        """3-4 pairs = medium confidence."""
        analyzer = PairedSalesAnalyzer(self.comparables, self.subject)

        confidence = analyzer._determine_confidence(
            n_pairs=3,
            cv=0.25,
            adjustments=[10, 12, 11]
        )

        self.assertEqual(confidence, 'medium')

    def test_single_pair_confidence(self):
        """Single pair = single_pair confidence."""
        analyzer = PairedSalesAnalyzer(self.comparables, self.subject)

        confidence = analyzer._determine_confidence(
            n_pairs=1,
            cv=None,
            adjustments=[10]
        )

        self.assertEqual(confidence, 'single_pair')


class TestOutputFormats(unittest.TestCase):
    """Test output format generation."""

    def setUp(self):
        """Set up test data with full analysis."""
        self.subject = {
            'address': '100 Test Street',
            'property_type': 'industrial',
            'size_sf': 50000,
            'location_submarket': 'East Industrial'
        }
        self.comparables = [
            {
                'address': f'Comp {i}',
                'sale_price': 5000000 + i*100000,
                'sale_date': f'2024-0{i+1}-15',
                'size_sf': 50000 + i*1000,
                'year_built': 2010 + i,
                'condition': 'good',
                'property_rights': 'fee_simple'
            }
            for i in range(5)
        ]

    def test_adjustment_factors_json(self):
        """JSON output has required structure."""
        analyzer = PairedSalesAnalyzer(self.comparables, self.subject)
        analyzer.analyze_all()

        factors = analyzer.get_adjustment_factors()

        # Check required top-level keys
        self.assertIn('derivation_date', factors)
        self.assertIn('valuation_date', factors)
        self.assertIn('property_type', factors)
        self.assertIn('cuspap_compliant', factors)
        self.assertIn('factors', factors)
        self.assertIn('disclosures', factors)

        self.assertTrue(factors['cuspap_compliant'])

    def test_adjustment_factor_structure(self):
        """Each factor has required fields."""
        analyzer = PairedSalesAnalyzer(self.comparables, self.subject)
        analyzer.analyze_all()

        factors = analyzer.get_adjustment_factors()

        # Check structure of at least one factor
        if factors['factors']:
            sample_factor = list(factors['factors'].values())[0]

            if isinstance(sample_factor, dict) and 'value' in sample_factor:
                self.assertIn('confidence', sample_factor)
                self.assertIn('method', sample_factor)
                self.assertIn('market_supported', sample_factor)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def test_empty_comparables_raises(self):
        """Empty comparables list raises ValueError."""
        subject = {'address': 'Test', 'property_type': 'industrial', 'size_sf': 50000}

        with self.assertRaises(ValueError):
            PairedSalesAnalyzer([], subject)

    def test_no_subject_raises(self):
        """Missing subject raises ValueError."""
        comparables = [
            {'address': 'Comp 1', 'sale_price': 5000000, 'sale_date': '2024-06-01', 'size_sf': 50000}
        ]

        with self.assertRaises(ValueError):
            PairedSalesAnalyzer(comparables, None)

    def test_missing_prices_handled(self):
        """Comparables with missing prices are excluded."""
        subject = {'address': 'Test', 'property_type': 'industrial', 'size_sf': 50000}
        comparables = [
            {'address': 'Comp 1', 'sale_date': '2024-06-01', 'size_sf': 50000},  # No price
            {'address': 'Comp 2', 'sale_price': 5000000, 'sale_date': '2024-06-15', 'size_sf': 50000},
            {'address': 'Comp 3', 'sale_price': 4800000, 'sale_date': '2024-07-01', 'size_sf': 50000}
        ]

        analyzer = PairedSalesAnalyzer(comparables, subject)
        analyzer.comparables = analyzer._verify_and_adjust_transactions()

        # Only 2 should remain (one excluded for missing price)
        self.assertEqual(len(analyzer.comparables), 2)

    def test_standard_mode_thresholds(self):
        """Standard mode uses more permissive thresholds."""
        subject = {'address': 'Test', 'property_type': 'industrial', 'size_sf': 50000}
        comparables = [
            {'address': 'Comp 1', 'sale_price': 5000000, 'sale_date': '2024-06-01', 'size_sf': 50000},
            {'address': 'Comp 2', 'sale_price': 4500000, 'sale_date': '2024-07-01', 'size_sf': 50000}
        ]

        analyzer_strict = PairedSalesAnalyzer(comparables, subject, strict_mode=True)
        analyzer_standard = PairedSalesAnalyzer(comparables, subject, strict_mode=False)

        # Standard should have more permissive size threshold
        self.assertGreater(
            analyzer_standard.thresholds['size_sf_pct'],
            analyzer_strict.thresholds['size_sf_pct']
        )


class TestIntegration(unittest.TestCase):
    """Integration tests with sample data files."""

    def test_full_analysis_pipeline(self):
        """Full analysis pipeline completes without error."""
        subject = {
            'address': '100 Industrial Way',
            'property_type': 'industrial',
            'size_sf': 75000,
            'year_built': 2015,
            'condition': 'good',
            'clear_height_feet': 28,
            'loading_docks_dock_high': 6,
            'highway_frontage': True,
            'location_submarket': 'East Industrial'
        }

        comparables = [
            {
                'address': f'{100 + i*100} Industrial Ave',
                'sale_price': 7000000 + i*200000,
                'sale_date': f'2024-0{min(i+3, 9)}-{10 + i}',
                'size_sf': 70000 + i*5000,
                'year_built': 2012 + i,
                'condition': ['fair', 'average', 'good', 'good', 'excellent'][i % 5],
                'clear_height_feet': 24 + i,
                'loading_docks_dock_high': 4 + i,
                'highway_frontage': i % 2 == 0,
                'location_submarket': 'East Industrial',
                'property_rights': 'fee_simple',
                'zoning': 'M2'
            }
            for i in range(6)
        ]

        analyzer = PairedSalesAnalyzer(comparables, subject)
        results = analyzer.analyze_all()

        # Check that analysis completed
        self.assertIsInstance(results, DerivedAdjustments)

        # Check that reports can be generated
        analysis_report = analyzer.get_analysis_report()
        self.assertIn('PAIRED SALES ANALYSIS', analysis_report)

        disclosure_report = analyzer.get_cuspap_disclosure_report()
        self.assertIn('CUSPAP DISCLOSURE REPORT', disclosure_report)

        factors = analyzer.get_adjustment_factors()
        self.assertIn('factors', factors)


if __name__ == '__main__':
    unittest.main(verbosity=2)
