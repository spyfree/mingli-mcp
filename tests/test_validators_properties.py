#!/usr/bin/env python3
"""
Property-based tests for validators using Hypothesis.

This module contains property-based tests that verify universal properties
of the validation functions across a wide range of inputs.
"""

from datetime import date

from hypothesis import assume, given, settings
from hypothesis import strategies as st

from core.exceptions import DateRangeError, ValidationError
from utils.validators import (
    MAX_YEAR,
    MIN_YEAR,
    validate_date,
    validate_date_range,
    validate_time_index,
)

# ============================================================================
# Hypothesis Strategies
# ============================================================================

# Strategy for valid dates within the supported range (1900-2100)
valid_dates_in_range = st.dates(min_value=date(MIN_YEAR, 1, 1), max_value=date(MAX_YEAR, 12, 31))

# Strategy for dates before the supported range
dates_before_range = st.dates(min_value=date(1, 1, 1), max_value=date(MIN_YEAR - 1, 12, 31))

# Strategy for dates after the supported range
dates_after_range = st.dates(min_value=date(MAX_YEAR + 1, 1, 1), max_value=date(9999, 12, 31))

# Strategy for valid time indices (0-12)
valid_time_indices = st.integers(min_value=0, max_value=12)

# Strategy for invalid time indices (outside 0-12)
invalid_time_indices_low = st.integers(max_value=-1)
invalid_time_indices_high = st.integers(min_value=13)

# Strategy for leap years within range
leap_years_in_range = st.sampled_from(
    [y for y in range(MIN_YEAR, MAX_YEAR + 1) if (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)]
)

# Strategy for non-leap years within range
non_leap_years_in_range = st.sampled_from(
    [
        y
        for y in range(MIN_YEAR, MAX_YEAR + 1)
        if not ((y % 4 == 0 and y % 100 != 0) or (y % 400 == 0))
    ]
)


# ============================================================================
# Property Tests for Date Validation
# ============================================================================


class TestDateValidationProperties:
    """Property-based tests for date validation functions."""

    @given(d=valid_dates_in_range)
    @settings(max_examples=100)
    def test_valid_dates_in_range_accepted(self, d: date):
        """
        **Feature: code-quality-improvements, Property 1: Valid dates in range are accepted**

        For any date in YYYY-MM-DD format where year is between 1900 and 2100
        (inclusive), and the date is a valid calendar date, the validation
        function should accept it without raising an error.

        **Validates: Requirements 4.1**
        """
        date_str = d.strftime("%Y-%m-%d")
        # validate_date should return True
        assert validate_date(date_str) is True
        # validate_date_range should not raise
        validate_date_range(date_str)

    @given(d=dates_before_range)
    @settings(max_examples=100)
    def test_dates_before_range_rejected(self, d: date):
        """
        **Feature: code-quality-improvements, Property 2: Invalid dates outside range are rejected**

        For any date where the year is less than 1900, the validation function
        should raise a DateRangeError or ValidationError (for years < 1000 which
        produce non-4-digit year strings).

        **Validates: Requirements 3.2**
        """
        # Use zero-padded format to ensure 4-digit year
        date_str = f"{d.year:04d}-{d.month:02d}-{d.day:02d}"
        try:
            validate_date_range(date_str)
            assert False, f"Expected DateRangeError for date {date_str}"
        except DateRangeError:
            pass  # Expected

    @given(d=dates_after_range)
    @settings(max_examples=100)
    def test_dates_after_range_rejected(self, d: date):
        """
        **Feature: code-quality-improvements, Property 2: Invalid dates outside range are rejected**

        For any date where the year is greater than 2100, the validation function
        should raise a DateRangeError.

        **Validates: Requirements 3.2**
        """
        date_str = d.strftime("%Y-%m-%d")
        try:
            validate_date_range(date_str)
            assert False, f"Expected DateRangeError for date {date_str}"
        except DateRangeError:
            pass  # Expected


class TestLeapYearProperties:
    """Property-based tests for leap year validation."""

    @given(year=leap_years_in_range)
    @settings(max_examples=100)
    def test_leap_year_feb_29_accepted(self, year: int):
        """
        **Feature: code-quality-improvements, Property 6: Leap year February 29 validation**

        For any leap year (divisible by 4, except centuries not divisible by 400),
        February 29 should be accepted as a valid date.

        **Validates: Requirements 3.5**
        """
        date_str = f"{year:04d}-02-29"
        assert validate_date(date_str) is True
        # Should not raise
        validate_date_range(date_str)

    @given(year=non_leap_years_in_range)
    @settings(max_examples=100)
    def test_non_leap_year_feb_29_rejected(self, year: int):
        """
        **Feature: code-quality-improvements, Property 7: Non-leap year February 29 rejection**

        For any non-leap year, February 29 should be rejected with a ValidationError.

        **Validates: Requirements 3.6**
        """
        date_str = f"{year:04d}-02-29"
        # validate_date should return False for invalid calendar date
        assert validate_date(date_str) is False


# ============================================================================
# Property Tests for Time Index Validation
# ============================================================================


class TestTimeIndexProperties:
    """Property-based tests for time index validation."""

    @given(index=valid_time_indices)
    @settings(max_examples=100)
    def test_valid_time_indices_accepted(self, index: int):
        """
        For any time_index value from 0 to 12 (inclusive), the validation
        function should return True.

        **Validates: Requirements 3.3**
        """
        assert validate_time_index(index) is True

    @given(index=invalid_time_indices_low)
    @settings(max_examples=100)
    def test_negative_time_indices_rejected(self, index: int):
        """
        For any negative time_index value, the validation function should
        return False.

        **Validates: Requirements 3.3**
        """
        assert validate_time_index(index) is False

    @given(index=invalid_time_indices_high)
    @settings(max_examples=100)
    def test_high_time_indices_rejected(self, index: int):
        """
        For any time_index value greater than 12, the validation function
        should return False.

        **Validates: Requirements 3.3**
        """
        assert validate_time_index(index) is False

    @given(index=valid_time_indices)
    @settings(max_examples=100)
    def test_string_time_indices_accepted(self, index: int):
        """
        For any valid time_index as a string, the validation function should
        return True (since it converts to int internally).

        **Validates: Requirements 3.3**
        """
        assert validate_time_index(str(index)) is True
