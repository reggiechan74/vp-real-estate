"""
Unit Tests for Address Normalizer

Tests for address standardization and normalization.
"""

import pytest

from Location_Overview.input.normalizer import (
    normalize_address,
    extract_municipality,
    extract_postal_code,
    standardize_address_components,
)


class TestNormalizeAddress:
    """Tests for normalize_address function."""

    def test_expand_street_abbreviation(self):
        """Test expansion of street abbreviations."""
        result = normalize_address("100 Queen St W, Toronto")
        assert "Street" in result
        assert "West" in result

    def test_expand_multiple_abbreviations(self):
        """Test expansion of multiple abbreviations."""
        result = normalize_address("100 King St E, Toronto")
        assert "Street" in result
        assert "East" in result

    def test_add_ontario_canada(self):
        """Test addition of Ontario, Canada."""
        result = normalize_address("100 Queen Street, Toronto")
        assert "Ontario" in result
        assert "Canada" in result

    def test_already_has_province(self):
        """Test handling when province already specified."""
        result = normalize_address("100 Queen Street, Toronto, ON")
        assert result.count("Ontario") <= 1 or "ON" in result

    def test_clean_whitespace(self):
        """Test whitespace cleaning."""
        result = normalize_address("100   Queen    Street,  Toronto")
        assert "  " not in result

    def test_no_expansion_option(self):
        """Test without abbreviation expansion."""
        result = normalize_address("100 Queen St, Toronto", expand_abbreviations=False)
        assert "St" in result  # Should not be expanded

    def test_empty_address(self):
        """Test empty address handling."""
        result = normalize_address("")
        assert result == ""


class TestExtractMunicipality:
    """Tests for extract_municipality function."""

    def test_extract_toronto(self):
        """Test extraction of Toronto."""
        result = extract_municipality("100 Queen Street, Toronto")
        assert result == "Toronto"

    def test_extract_mississauga(self):
        """Test extraction of Mississauga."""
        result = extract_municipality("200 City Centre Drive, Mississauga")
        assert result == "Mississauga"

    def test_extract_ottawa(self):
        """Test extraction of Ottawa."""
        result = extract_municipality("110 Laurier Avenue, Ottawa")
        assert result == "Ottawa"

    def test_no_municipality(self):
        """Test when no municipality found."""
        result = extract_municipality("100 Main Street")
        assert result is None


class TestExtractPostalCode:
    """Tests for extract_postal_code function."""

    def test_extract_valid_postal_code(self):
        """Test extraction of valid postal code."""
        result = extract_postal_code("100 Queen Street, Toronto, ON M5H 2N2")
        assert result == "M5H 2N2"

    def test_extract_no_space_postal_code(self):
        """Test extraction of postal code without space."""
        result = extract_postal_code("100 Queen Street, Toronto M5H2N2")
        assert result == "M5H 2N2"

    def test_no_postal_code(self):
        """Test when no postal code present."""
        result = extract_postal_code("100 Queen Street, Toronto")
        assert result is None

    def test_lowercase_postal_code(self):
        """Test extraction of lowercase postal code."""
        result = extract_postal_code("100 Queen Street, Toronto m5h 2n2")
        assert result == "M5H 2N2"  # Should be uppercase


class TestStandardizeAddressComponents:
    """Tests for standardize_address_components function."""

    def test_extract_street_number(self):
        """Test extraction of street number."""
        result = standardize_address_components("100 Queen Street, Toronto")
        assert result["street_number"] == "100"

    def test_extract_unit_number(self):
        """Test extraction of unit number."""
        result = standardize_address_components("Unit 5, 100 Queen Street, Toronto")
        assert result["unit"] == "5"

    def test_extract_suite_number(self):
        """Test extraction of suite number."""
        result = standardize_address_components("Suite 500, 100 King Street, Toronto")
        assert result["unit"] == "500"

    def test_extract_municipality(self):
        """Test extraction of municipality."""
        result = standardize_address_components("100 Queen Street, Toronto")
        assert result["municipality"] == "Toronto"

    def test_extract_province(self):
        """Test extraction of province."""
        result = standardize_address_components("100 Queen Street, Toronto, Ontario")
        assert result["province"] == "Ontario"

    def test_extract_postal_code(self):
        """Test extraction of postal code."""
        result = standardize_address_components("100 Queen Street, Toronto M5H 2N2")
        assert result["postal_code"] == "M5H 2N2"
