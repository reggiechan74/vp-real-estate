"""
Unit Tests for Input Parser

Tests for PIN/address detection and validation.
"""

import pytest

from Location_Overview.input.parser import (
    detect_input_type,
    validate_pin,
    parse_input,
    format_pin,
    InputType,
)


class TestDetectInputType:
    """Tests for detect_input_type function."""

    def test_valid_pin_no_separator(self):
        """Test detection of PIN without separators."""
        input_type, value = detect_input_type("123456789")
        assert input_type == InputType.PIN
        assert value == "123456789"

    def test_valid_pin_with_dash(self):
        """Test detection of PIN with dash separator."""
        input_type, value = detect_input_type("12345-6789")
        assert input_type == InputType.PIN
        assert value == "123456789"

    def test_valid_pin_with_space(self):
        """Test detection of PIN with space separator."""
        input_type, value = detect_input_type("12345 6789")
        assert input_type == InputType.PIN
        assert value == "123456789"

    def test_address_simple(self):
        """Test detection of simple address."""
        input_type, value = detect_input_type("100 Queen Street West, Toronto")
        assert input_type == InputType.ADDRESS
        assert "100 Queen Street West" in value

    def test_address_with_unit(self):
        """Test detection of address with unit number."""
        input_type, value = detect_input_type("Suite 100, 150 King Street, Toronto")
        assert input_type == InputType.ADDRESS

    def test_empty_input(self):
        """Test handling of empty input."""
        input_type, value = detect_input_type("")
        assert input_type == InputType.UNKNOWN
        assert value == ""

    def test_whitespace_only(self):
        """Test handling of whitespace input."""
        input_type, value = detect_input_type("   ")
        assert input_type == InputType.UNKNOWN


class TestValidatePin:
    """Tests for validate_pin function."""

    def test_valid_pin(self):
        """Test validation of valid PIN."""
        is_valid, message = validate_pin("123456789")
        assert is_valid
        assert "Valid" in message

    def test_invalid_pin_too_short(self):
        """Test validation of too-short PIN."""
        is_valid, message = validate_pin("12345")
        assert not is_valid
        assert "9 digits" in message

    def test_invalid_pin_too_long(self):
        """Test validation of too-long PIN."""
        is_valid, message = validate_pin("1234567890")
        assert not is_valid

    def test_invalid_pin_letters(self):
        """Test validation of PIN with letters."""
        is_valid, message = validate_pin("12345678A")
        assert not is_valid

    def test_invalid_pin_zero_block(self):
        """Test validation of PIN with zero block number."""
        is_valid, message = validate_pin("000001234")
        assert not is_valid
        assert "Block" in message

    def test_empty_pin(self):
        """Test validation of empty PIN."""
        is_valid, message = validate_pin("")
        assert not is_valid


class TestParseInput:
    """Tests for parse_input function."""

    def test_parse_valid_address(self):
        """Test parsing valid address."""
        result = parse_input("100 Queen Street West, Toronto")
        assert result.input_type == InputType.ADDRESS
        assert result.is_valid
        assert result.original == "100 Queen Street West, Toronto"

    def test_parse_valid_pin(self):
        """Test parsing valid PIN."""
        result = parse_input("123456789")
        assert result.input_type == InputType.PIN
        assert result.is_valid
        assert result.value == "123456789"

    def test_parse_invalid_pin(self):
        """Test parsing invalid PIN."""
        result = parse_input("000001234")
        assert result.input_type == InputType.PIN
        assert not result.is_valid

    def test_parse_short_address(self):
        """Test parsing too-short address."""
        result = parse_input("abc")
        assert result.input_type == InputType.ADDRESS
        assert not result.is_valid

    def test_parse_empty(self):
        """Test parsing empty input."""
        result = parse_input("")
        assert not result.is_valid
        assert "empty" in result.validation_message.lower()


class TestFormatPin:
    """Tests for format_pin function."""

    def test_format_valid_pin(self):
        """Test formatting valid PIN."""
        formatted = format_pin("123456789")
        assert formatted == "12345-6789"

    def test_format_already_formatted(self):
        """Test formatting already-formatted PIN."""
        formatted = format_pin("12345-6789")
        assert formatted == "12345-6789"

    def test_format_invalid_pin(self):
        """Test formatting invalid PIN returns original."""
        formatted = format_pin("12345")
        assert formatted == "12345"
