#!/usr/bin/env python3
"""
Unit Tests for Utility Conflict Analyzer
Tests all modules and integration workflow
"""

import unittest
import json
import os
import sys
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from modules.validators import validate_input_data, sanitize_input
from modules.conflict_detection import (
    detect_conflicts, classify_severity, generate_conflict_matrix
)
from modules.relocation_design import generate_relocation_requirements
from modules.cost_estimation import estimate_relocation_costs


class TestValidators(unittest.TestCase):
    """Test input validation module"""

    def test_valid_input(self):
        """Test validation with valid input"""
        valid_data = {
            'project_alignment': {
                'type': 'transit_station',
                'location': {'x': 0, 'y': 0}
            },
            'existing_utilities': [
                {
                    'utility_type': 'Gas main',
                    'owner': 'Enbridge',
                    'location': {'x': 10, 'y': 5}
                }
            ]
        }

        is_valid, errors = validate_input_data(valid_data)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_missing_required_keys(self):
        """Test validation with missing required keys"""
        invalid_data = {
            'project_alignment': {
                'type': 'transit_station'
            }
        }

        is_valid, errors = validate_input_data(invalid_data)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)

    def test_invalid_project_type(self):
        """Test validation with invalid project type"""
        invalid_data = {
            'project_alignment': {
                'type': 'invalid_type',
                'location': {'x': 0, 'y': 0}
            },
            'existing_utilities': [
                {
                    'utility_type': 'Gas main',
                    'owner': 'Enbridge',
                    'location': {'x': 10, 'y': 5}
                }
            ]
        }

        is_valid, errors = validate_input_data(invalid_data)
        self.assertFalse(is_valid)

    def test_sanitize_input(self):
        """Test input sanitization"""
        data = {
            'project_alignment': {
                'type': 'transit_station',
                'location': {'x': 0, 'y': 0}
            },
            'existing_utilities': []
        }

        sanitized = sanitize_input(data)
        self.assertIn('design_constraints', sanitized)
        self.assertIn('horizontal_clearance_min', sanitized['design_constraints'])


class TestConflictDetection(unittest.TestCase):
    """Test conflict detection module"""

    def setUp(self):
        """Set up test data"""
        self.project_alignment = {
            'type': 'transit_station',
            'location': {'x': 0, 'y': 0, 'excavation_depth': 20}
        }

        self.utilities = [
            {
                'utility_type': 'Gas main',
                'owner': 'Enbridge',
                'size': '12-inch high pressure',
                'location': {'x': 3, 'y': 2},
                'depth': 3.5
            },
            {
                'utility_type': 'Water main',
                'owner': 'City',
                'location': {'x': 8, 'y': 5},
                'depth': 2.8
            }
        ]

        self.design_constraints = {
            'horizontal_clearance_min': 5.0,
            'vertical_clearance_min': 3.0,
            'protection_zone_width': 10.0
        }

    def test_detect_conflicts(self):
        """Test conflict detection"""
        conflicts = detect_conflicts(
            self.project_alignment,
            self.utilities,
            self.design_constraints
        )

        self.assertIsInstance(conflicts, list)
        self.assertGreater(len(conflicts), 0)

    def test_classify_severity(self):
        """Test severity classification"""
        conflict = {
            'utility_type': 'Gas main',
            'conflict_type': 'Horizontal clearance violation',
            'shortfall': 6.0
        }

        utility = {
            'utility_type': 'Gas main',
            'size': 'high pressure'
        }

        severity = classify_severity(conflict, utility)
        self.assertIn(severity, ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'])

    def test_generate_conflict_matrix(self):
        """Test conflict matrix generation"""
        conflicts = [
            {
                'owner': 'Enbridge',
                'severity': 'CRITICAL',
                'utility_type': 'Gas main'
            },
            {
                'owner': 'Enbridge',
                'severity': 'HIGH',
                'utility_type': 'Gas main'
            },
            {
                'owner': 'City',
                'severity': 'MEDIUM',
                'utility_type': 'Water main'
            }
        ]

        matrix = generate_conflict_matrix(conflicts)
        self.assertIn('Enbridge', matrix)
        self.assertIn('City', matrix)
        self.assertEqual(matrix['Enbridge']['total'], 2)


class TestRelocationDesign(unittest.TestCase):
    """Test relocation design module"""

    def setUp(self):
        """Set up test data"""
        self.conflicts = [
            {
                'utility_id': 'Enbridge - Gas main',
                'owner': 'Enbridge',
                'severity': 'CRITICAL',
                'utility_type': 'Gas main'
            }
        ]

        self.utilities = [
            {
                'utility_type': 'Gas main',
                'owner': 'Enbridge',
                'size': '12-inch high pressure',
                'location': {'x': 3, 'y': 2}
            }
        ]

    def test_generate_relocation_requirements(self):
        """Test relocation requirements generation"""
        requirements = generate_relocation_requirements(
            self.conflicts,
            self.utilities
        )

        self.assertIsInstance(requirements, list)
        self.assertGreater(len(requirements), 0)

        # Check structure
        req = requirements[0]
        self.assertIn('utility_id', req)
        self.assertIn('relocation_type', req)
        self.assertIn('design_requirements', req)
        self.assertIn('approval_agencies', req)
        self.assertIn('estimated_duration', req)


class TestCostEstimation(unittest.TestCase):
    """Test cost estimation module"""

    def setUp(self):
        """Set up test data"""
        self.relocation_requirements = [
            {
                'utility_id': 'Enbridge - Gas main',
                'utility_type': 'Gas main',
                'owner': 'Enbridge',
                'conflict_count': 1,
                'max_severity': 'CRITICAL'
            }
        ]

        self.utilities = [
            {
                'utility_type': 'Gas main',
                'owner': 'Enbridge',
                'size': '12-inch high pressure',
                'relocation_length_km': 0.5
            }
        ]

    def test_estimate_relocation_costs(self):
        """Test cost estimation"""
        cost_estimate = estimate_relocation_costs(
            self.relocation_requirements,
            self.utilities
        )

        self.assertIn('utility_costs', cost_estimate)
        self.assertIn('total_range', cost_estimate)
        self.assertIn('contingency', cost_estimate)

        # Check cost ranges
        total = cost_estimate['total_range']
        self.assertGreater(total['high'], total['low'])
        self.assertGreater(total['low'], 0)


class TestIntegration(unittest.TestCase):
    """Integration tests with sample data"""

    def test_full_workflow_transit_station(self):
        """Test complete workflow with transit station sample"""
        sample_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'samples',
            'transit_station_input.json'
        )

        if not os.path.exists(sample_path):
            self.skipTest("Sample file not found")

        with open(sample_path, 'r') as f:
            data = json.load(f)

        # Validate
        is_valid, errors = validate_input_data(data)
        self.assertTrue(is_valid, f"Validation errors: {errors}")

        # Sanitize
        data = sanitize_input(data)

        # Detect conflicts
        conflicts = detect_conflicts(
            data['project_alignment'],
            data['existing_utilities'],
            data['design_constraints']
        )
        self.assertGreater(len(conflicts), 0)

        # Generate requirements
        requirements = generate_relocation_requirements(
            conflicts,
            data['existing_utilities']
        )
        self.assertGreater(len(requirements), 0)

        # Estimate costs
        cost_estimate = estimate_relocation_costs(
            requirements,
            data['existing_utilities']
        )
        self.assertGreater(cost_estimate['total_range']['low'], 0)


def run_tests():
    """Run all tests"""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == '__main__':
    run_tests()
