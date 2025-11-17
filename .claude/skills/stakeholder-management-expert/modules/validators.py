#!/usr/bin/env python3
"""
Input Validation Module for Consultation Summarizer
Validates input JSON against schema and business rules.
"""

import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime


def validate_input(data: Dict) -> Tuple[bool, Optional[str]]:
    """
    Validate consultation input data.

    Args:
        data: Input dictionary with meeting info, comments, and categories

    Returns:
        Tuple of (is_valid, error_message)
            (True, None) if valid
            (False, "error message") if invalid
    """
    # Check required top-level keys
    required_keys = ['meeting_info', 'comments', 'theme_categories']
    for key in required_keys:
        if key not in data:
            return False, f"Missing required key: {key}"

    # Validate meeting_info
    valid, error = _validate_meeting_info(data['meeting_info'])
    if not valid:
        return False, f"meeting_info validation failed: {error}"

    # Validate comments
    valid, error = _validate_comments(data['comments'])
    if not valid:
        return False, f"comments validation failed: {error}"

    # Validate theme_categories
    valid, error = _validate_theme_categories(data['theme_categories'])
    if not valid:
        return False, f"theme_categories validation failed: {error}"

    # Validate priorities if present
    if 'priorities' in data:
        valid, error = _validate_priorities(
            data['priorities'],
            data['theme_categories']
        )
        if not valid:
            return False, f"priorities validation failed: {error}"

    return True, None


def _validate_meeting_info(meeting_info: Dict) -> Tuple[bool, Optional[str]]:
    """Validate meeting_info section."""
    # Check required fields
    if 'meeting_date' not in meeting_info:
        return False, "missing meeting_date"

    if 'attendance' not in meeting_info:
        return False, "missing attendance"

    # Validate date format
    try:
        datetime.strptime(meeting_info['meeting_date'], '%Y-%m-%d')
    except ValueError:
        return False, f"invalid date format: {meeting_info['meeting_date']} (expected YYYY-MM-DD)"

    # Validate attendance
    if not isinstance(meeting_info['attendance'], int):
        return False, f"attendance must be integer, got {type(meeting_info['attendance'])}"

    if meeting_info['attendance'] < 0:
        return False, f"attendance must be non-negative, got {meeting_info['attendance']}"

    return True, None


def _validate_comments(comments: List) -> Tuple[bool, Optional[str]]:
    """Validate comments array."""
    if not isinstance(comments, list):
        return False, f"comments must be array, got {type(comments)}"

    if len(comments) == 0:
        return False, "comments array is empty"

    # Check each comment
    for idx, comment in enumerate(comments):
        if not isinstance(comment, str):
            return False, f"comment at index {idx} must be string, got {type(comment)}"

        if len(comment) == 0:
            return False, f"comment at index {idx} is empty"

        if len(comment) > 2000:
            return False, f"comment at index {idx} exceeds 2000 character limit"

    return True, None


def _validate_theme_categories(categories: Dict) -> Tuple[bool, Optional[str]]:
    """Validate theme_categories object."""
    if not isinstance(categories, dict):
        return False, f"theme_categories must be object, got {type(categories)}"

    if len(categories) == 0:
        return False, "theme_categories is empty"

    # Check each category
    for theme, keywords in categories.items():
        if not isinstance(keywords, list):
            return False, f"keywords for theme '{theme}' must be array, got {type(keywords)}"

        if len(keywords) == 0:
            return False, f"keywords array for theme '{theme}' is empty"

        for idx, keyword in enumerate(keywords):
            if not isinstance(keyword, str):
                return False, f"keyword at index {idx} for theme '{theme}' must be string"

            if len(keyword) == 0:
                return False, f"keyword at index {idx} for theme '{theme}' is empty"

    return True, None


def _validate_priorities(priorities: Dict, categories: Dict) -> Tuple[bool, Optional[str]]:
    """Validate priorities object."""
    if not isinstance(priorities, dict):
        return False, f"priorities must be object, got {type(priorities)}"

    # Check each priority
    for theme, priority in priorities.items():
        # Check theme exists in categories
        if theme not in categories:
            return False, f"priority theme '{theme}' not found in theme_categories"

        # Check priority value
        if not isinstance(priority, int):
            return False, f"priority for '{theme}' must be integer, got {type(priority)}"

        if priority < 1 or priority > 5:
            return False, f"priority for '{theme}' must be 1-5, got {priority}"

    return True, None


def validate_demographics(demographics: Dict) -> Tuple[bool, Optional[str]]:
    """
    Validate demographics section.

    Args:
        demographics: Demographics dictionary

    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_fields = [
        'residents', 'business_owners', 'property_owners',
        'elected_officials', 'advocacy_groups', 'other'
    ]

    for field, value in demographics.items():
        if field not in valid_fields:
            return False, f"unknown demographic field: {field}"

        if not isinstance(value, int):
            return False, f"{field} must be integer, got {type(value)}"

        if value < 0:
            return False, f"{field} must be non-negative, got {value}"

    return True, None


def validate_output_options(options: Dict) -> Tuple[bool, Optional[str]]:
    """
    Validate output_options section.

    Args:
        options: Output options dictionary

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate include_quotes
    if 'include_quotes' in options:
        if not isinstance(options['include_quotes'], bool):
            return False, f"include_quotes must be boolean"

    # Validate max_quotes_per_sentiment
    if 'max_quotes_per_sentiment' in options:
        value = options['max_quotes_per_sentiment']
        if not isinstance(value, int):
            return False, f"max_quotes_per_sentiment must be integer"
        if value < 1 or value > 20:
            return False, f"max_quotes_per_sentiment must be 1-20, got {value}"

    # Validate include_commitments
    if 'include_commitments' in options:
        if not isinstance(options['include_commitments'], bool):
            return False, f"include_commitments must be boolean"

    # Validate output_format
    if 'output_format' in options:
        if options['output_format'] not in ['markdown', 'json']:
            return False, f"output_format must be 'markdown' or 'json'"

    return True, None
