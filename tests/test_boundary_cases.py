#!/usr/bin/env python3
"""
Comprehensive boundary condition tests for input validation.

This module tests edge cases at the limits of valid input ranges for:
- Date boundaries (1900-01-01 to 2100-12-31)
- Time index boundaries (0 to 12)
- Lunar leap month validation

Requirements: 3.1, 3.2, 3.3, 3.4
"""

import pytest

from core.birth_info import BirthInfo
from core.exceptions import DateRangeError, ValidationError
from utils.validators import (
    validate_date,
    validate_date_range,
    validate_time_index,
)


class TestDateBoundaries:
    """
    Date boundary tests for the supported range (1900-2100).

    Requirements: 3.1, 3.2
    """

    def test_minimum_valid_date(self):
        """Test that 1900-01-01 (minimum boundary) is accepted."""
        # Should not raise any exception
        validate_date_range("1900-01-01")
        assert validate_date("1900-01-01") is True

    def test_maximum_valid_date(self):
        """Test that 2100-12-31 (maximum boundary) is accepted."""
        # Should not raise any exception
        validate_date_range("2100-12-31")
        assert validate_date("2100-12-31") is True

    def test_date_just_before_minimum(self):
        """Test that 1899-12-31 (one day before minimum) is rejected."""
        with pytest.raises(DateRangeError) as exc_info:
            validate_date_range("1899-12-31")
        error_msg = str(exc_info.value)
        assert "1899-12-31" in error_msg  # Should include the invalid value
        assert "1900" in error_msg and "2100" in error_msg  # Should include valid range

    def test_date_just_after_maximum(self):
        """Test that 2101-01-01 (one day after maximum) is rejected."""
        with pytest.raises(DateRangeError) as exc_info:
            validate_date_range("2101-01-01")
        error_msg = str(exc_info.value)
        assert "2101-01-01" in error_msg  # Should include the invalid value
        assert "1900" in error_msg and "2100" in error_msg  # Should include valid range

    def test_year_1899_rejected(self):
        """Test that any date in year 1899 is rejected."""
        with pytest.raises(DateRangeError):
            validate_date_range("1899-06-15")

    def test_year_2101_rejected(self):
        """Test that any date in year 2101 is rejected."""
        with pytest.raises(DateRangeError):
            validate_date_range("2101-06-15")

    def test_first_day_of_valid_range(self):
        """Test first day of each boundary year."""
        validate_date_range("1900-01-01")
        validate_date_range("2100-01-01")

    def test_last_day_of_valid_range(self):
        """Test last day of each boundary year."""
        validate_date_range("1900-12-31")
        validate_date_range("2100-12-31")

    def test_leap_year_february_29_valid(self):
        """Test February 29 in leap years is accepted (Requirements: 3.5)."""
        # 2000 is a leap year (divisible by 400)
        assert validate_date("2000-02-29") is True
        # 2004 is a leap year (divisible by 4, not century)
        assert validate_date("2004-02-29") is True
        # 2020 is a leap year
        assert validate_date("2020-02-29") is True

    def test_non_leap_year_february_29_invalid(self):
        """Test February 29 in non-leap years is rejected (Requirements: 3.6)."""
        # 2001 is not a leap year
        assert validate_date("2001-02-29") is False
        # 1900 is not a leap year (century not divisible by 400)
        assert validate_date("1900-02-29") is False
        # 2100 is not a leap year (century not divisible by 400)
        assert validate_date("2100-02-29") is False

    def test_century_leap_year_rules(self):
        """Test century leap year rules (divisible by 400)."""
        # 2000 is a leap year (divisible by 400)
        assert validate_date("2000-02-29") is True
        # 1900 is NOT a leap year (divisible by 100 but not 400)
        assert validate_date("1900-02-29") is False


class TestTimeIndexBoundaries:
    """
    Time index boundary tests for valid range (0-12).

    Requirements: 3.3
    """

    def test_early_zi_hour_valid(self):
        """Test time_index 0 (early Zi hour, 23:00-01:00) is valid."""
        assert validate_time_index(0) is True

    def test_late_zi_hour_valid(self):
        """Test time_index 12 (late Zi hour, 23:00-01:00) is valid."""
        assert validate_time_index(12) is True

    def test_negative_time_index_invalid(self):
        """Test time_index -1 (below minimum) is invalid."""
        assert validate_time_index(-1) is False

    def test_time_index_above_maximum_invalid(self):
        """Test time_index 13 (above maximum) is invalid."""
        assert validate_time_index(13) is False

    def test_all_valid_time_indices(self):
        """Test all valid time indices (0-12) are accepted."""
        for i in range(13):
            assert validate_time_index(i) is True, f"time_index {i} should be valid"

    def test_large_invalid_time_index(self):
        """Test very large time_index values are rejected."""
        assert validate_time_index(100) is False
        assert validate_time_index(1000) is False

    def test_negative_large_time_index(self):
        """Test very negative time_index values are rejected."""
        assert validate_time_index(-100) is False
        assert validate_time_index(-1000) is False

    def test_string_time_index_conversion(self):
        """Test string time_index values are properly converted."""
        assert validate_time_index("0") is True
        assert validate_time_index("12") is True
        assert validate_time_index("-1") is False
        assert validate_time_index("13") is False

    def test_invalid_string_time_index(self):
        """Test non-numeric string time_index values are rejected."""
        assert validate_time_index("invalid") is False
        assert validate_time_index("") is False
        assert validate_time_index("abc") is False

    def test_none_time_index(self):
        """Test None time_index is rejected."""
        assert validate_time_index(None) is False

    def test_float_time_index(self):
        """Test float time_index values."""
        # Float that converts to valid int
        assert validate_time_index(6.0) is True
        assert validate_time_index(0.0) is True
        assert validate_time_index(12.0) is True


class TestLunarLeapMonthBoundaries:
    """
    Lunar leap month validation tests.

    Requirements: 3.4
    """

    def test_valid_lunar_date_without_leap_month(self):
        """Test valid lunar date without leap month flag."""
        birth_info = BirthInfo(
            date="2000-08-16",
            time_index=6,
            gender="女",
            calendar="lunar",
            is_leap_month=False,
        )
        assert birth_info.calendar == "lunar"
        assert birth_info.is_leap_month is False

    def test_valid_lunar_date_with_leap_month(self):
        """Test valid lunar date with leap month flag."""
        birth_info = BirthInfo(
            date="2000-08-16",
            time_index=6,
            gender="女",
            calendar="lunar",
            is_leap_month=True,
        )
        assert birth_info.calendar == "lunar"
        assert birth_info.is_leap_month is True

    def test_solar_date_ignores_leap_month(self):
        """Test that solar calendar ignores is_leap_month flag."""
        # is_leap_month should be ignored for solar calendar
        birth_info = BirthInfo(
            date="2000-08-16",
            time_index=6,
            gender="女",
            calendar="solar",
            is_leap_month=True,  # This should be ignored for solar
        )
        assert birth_info.calendar == "solar"
        # The flag is stored but should be ignored in calculations

    def test_leap_month_default_false(self):
        """Test that is_leap_month defaults to False."""
        birth_info = BirthInfo(
            date="2000-08-16",
            time_index=6,
            gender="女",
        )
        assert birth_info.is_leap_month is False

    def test_lunar_calendar_with_various_time_indices(self):
        """Test lunar calendar works with all valid time indices."""
        for time_index in range(13):
            birth_info = BirthInfo(
                date="2000-08-16",
                time_index=time_index,
                gender="男",
                calendar="lunar",
                is_leap_month=False,
            )
            assert birth_info.time_index == time_index

    def test_invalid_calendar_type(self):
        """Test that invalid calendar type raises error."""
        with pytest.raises(ValueError) as exc_info:
            BirthInfo(
                date="2000-08-16",
                time_index=6,
                gender="女",
                calendar="gregorian",  # Invalid calendar type
            )
        assert "solar" in str(exc_info.value) or "lunar" in str(exc_info.value)


class TestBirthInfoBoundaries:
    """
    BirthInfo boundary tests combining multiple validations.

    Requirements: 3.1, 3.3, 3.4
    """

    def test_birth_info_with_minimum_date(self):
        """Test BirthInfo creation with minimum valid date."""
        birth_info = BirthInfo(
            date="1900-01-01",
            time_index=0,
            gender="男",
        )
        assert birth_info.date == "1900-01-01"

    def test_birth_info_with_maximum_date(self):
        """Test BirthInfo creation with maximum valid date."""
        birth_info = BirthInfo(
            date="2100-12-31",
            time_index=12,
            gender="女",
        )
        assert birth_info.date == "2100-12-31"

    def test_birth_info_with_boundary_time_indices(self):
        """Test BirthInfo with boundary time indices."""
        # Early Zi hour
        birth_info_early = BirthInfo(
            date="2000-08-16",
            time_index=0,
            gender="男",
        )
        assert birth_info_early.time_index == 0
        assert birth_info_early.get_time_name() == "早子时"

        # Late Zi hour
        birth_info_late = BirthInfo(
            date="2000-08-16",
            time_index=12,
            gender="女",
        )
        assert birth_info_late.time_index == 12
        assert birth_info_late.get_time_name() == "晚子时"

    def test_birth_info_invalid_time_index_below(self):
        """Test BirthInfo rejects time_index below 0."""
        with pytest.raises(ValueError) as exc_info:
            BirthInfo(
                date="2000-08-16",
                time_index=-1,
                gender="男",
            )
        assert "0-12" in str(exc_info.value)

    def test_birth_info_invalid_time_index_above(self):
        """Test BirthInfo rejects time_index above 12."""
        with pytest.raises(ValueError) as exc_info:
            BirthInfo(
                date="2000-08-16",
                time_index=13,
                gender="女",
            )
        assert "0-12" in str(exc_info.value)

    def test_birth_info_invalid_gender(self):
        """Test BirthInfo rejects invalid gender."""
        with pytest.raises(ValueError):
            BirthInfo(
                date="2000-08-16",
                time_index=6,
                gender="male",  # Invalid - should be "男" or "女"
            )

    def test_birth_info_invalid_date_format(self):
        """Test BirthInfo rejects invalid date format."""
        with pytest.raises(ValueError) as exc_info:
            BirthInfo(
                date="2000/08/16",  # Wrong format
                time_index=6,
                gender="男",
            )
        assert "YYYY-MM-DD" in str(exc_info.value)

    def test_birth_info_time_range_boundaries(self):
        """Test time range strings for boundary time indices."""
        birth_info_0 = BirthInfo(date="2000-08-16", time_index=0, gender="男")
        birth_info_12 = BirthInfo(date="2000-08-16", time_index=12, gender="女")

        # Both early and late Zi hour should have same time range
        assert birth_info_0.get_time_range() == "23:00~01:00"
        assert birth_info_12.get_time_range() == "23:00~01:00"
