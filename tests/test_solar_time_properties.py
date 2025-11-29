#!/usr/bin/env python3
"""
Property-based tests for solar time calculations using Hypothesis.

This module contains property-based tests that verify universal properties
of the solar time calculation functions across a wide range of inputs.
"""

from datetime import datetime
from hypothesis import given, strategies as st, settings

from utils.solar_time import (
    BEIJING_LONGITUDE,
    MINUTES_PER_DEGREE,
    calculate_solar_time_offset,
    beijing_to_solar_time,
    calculate_time_index,
    adjust_time_index_for_solar_time,
)


# ============================================================================
# Hypothesis Strategies
# ============================================================================

# Strategy for valid longitude values (-180 to 180)
valid_longitudes = st.floats(
    min_value=-180.0, max_value=180.0, allow_nan=False, allow_infinity=False
)

# Strategy for typical Chinese longitude values (73.5 to 135.0 - China's span)
chinese_longitudes = st.floats(
    min_value=73.5, max_value=135.0, allow_nan=False, allow_infinity=False
)

# Strategy for valid hours (0-23)
valid_hours = st.integers(min_value=0, max_value=23)

# Strategy for valid minutes (0-59)
valid_minutes = st.integers(min_value=0, max_value=59)

# Strategy for valid time indices (0-12)
valid_time_indices = st.integers(min_value=0, max_value=12)

# Strategy for datetime values
valid_datetimes = st.datetimes(
    min_value=datetime(1900, 1, 1, 0, 0), max_value=datetime(2100, 12, 31, 23, 59)
)


# ============================================================================
# Property Tests for Solar Time Offset
# ============================================================================


class TestSolarTimeOffsetProperties:
    """Property-based tests for solar time offset calculation."""

    @given(longitude=valid_longitudes)
    @settings(max_examples=100)
    def test_solar_time_offset_determinism(self, longitude: float):
        """
        **Feature: code-quality-improvements, Property 5: Solar time offset determinism**

        For any longitude value between -180 and 180, the solar time offset
        calculation should be deterministic (same input always produces same
        output) and within expected bounds (±720 minutes, corresponding to
        ±12 hours).

        **Validates: Requirements 4.4**
        """
        # Calculate offset twice to verify determinism
        offset1 = calculate_solar_time_offset(longitude)
        offset2 = calculate_solar_time_offset(longitude)

        # Determinism: same input produces same output
        assert offset1 == offset2, (
            f"Non-deterministic result for longitude {longitude}: " f"{offset1} != {offset2}"
        )

        # Bounds check: offset should be within ±720 minutes (±12 hours)
        # Maximum offset occurs at longitude extremes:
        # At -180°: (-180 - 120) * 4 = -1200 minutes
        # At +180°: (180 - 120) * 4 = 240 minutes
        # So actual bounds are -1200 to +240 for valid longitudes
        max_offset = (180.0 - BEIJING_LONGITUDE) * MINUTES_PER_DEGREE
        min_offset = (-180.0 - BEIJING_LONGITUDE) * MINUTES_PER_DEGREE

        assert min_offset <= offset1 <= max_offset, (
            f"Offset {offset1} out of bounds [{min_offset}, {max_offset}] "
            f"for longitude {longitude}"
        )

    @given(longitude=valid_longitudes)
    @settings(max_examples=100)
    def test_solar_time_offset_is_integer(self, longitude: float):
        """
        For any longitude, the solar time offset should be an integer
        (rounded from the calculation).

        **Validates: Requirements 4.4**
        """
        offset = calculate_solar_time_offset(longitude)
        assert isinstance(
            offset, int
        ), f"Offset should be integer, got {type(offset)} for longitude {longitude}"

    @given(longitude=valid_longitudes)
    @settings(max_examples=100)
    def test_solar_time_offset_formula_consistency(self, longitude: float):
        """
        For any longitude, the offset should match the expected formula:
        offset = round((longitude - 120) * 4)

        **Validates: Requirements 4.4**
        """
        offset = calculate_solar_time_offset(longitude)
        expected = round((longitude - BEIJING_LONGITUDE) * MINUTES_PER_DEGREE)

        assert offset == expected, (
            f"Offset {offset} doesn't match expected {expected} " f"for longitude {longitude}"
        )

    def test_standard_longitude_zero_offset(self):
        """
        At the standard Beijing longitude (120°E), the offset should be exactly 0.

        **Validates: Requirements 4.4**
        """
        offset = calculate_solar_time_offset(BEIJING_LONGITUDE)
        assert offset == 0, f"Expected 0 offset at standard longitude, got {offset}"


# ============================================================================
# Property Tests for Beijing to Solar Time Conversion
# ============================================================================


class TestBeijingToSolarTimeProperties:
    """Property-based tests for Beijing to solar time conversion."""

    @given(dt=valid_datetimes, longitude=chinese_longitudes)
    @settings(max_examples=100)
    def test_solar_time_conversion_determinism(self, dt: datetime, longitude: float):
        """
        For any datetime and longitude, the conversion should be deterministic.

        **Validates: Requirements 4.4**
        """
        solar1 = beijing_to_solar_time(dt, longitude)
        solar2 = beijing_to_solar_time(dt, longitude)

        assert solar1 == solar2, (
            f"Non-deterministic conversion for {dt} at {longitude}: " f"{solar1} != {solar2}"
        )

    @given(dt=valid_datetimes, longitude=valid_longitudes)
    @settings(max_examples=100)
    def test_solar_time_offset_applied_correctly(self, dt: datetime, longitude: float):
        """
        The solar time should differ from Beijing time by exactly the
        calculated offset.

        **Validates: Requirements 4.4**
        """
        solar_time = beijing_to_solar_time(dt, longitude)
        offset_minutes = calculate_solar_time_offset(longitude)

        # Calculate the actual difference in minutes
        diff = solar_time - dt
        actual_diff_minutes = diff.total_seconds() / 60

        assert actual_diff_minutes == offset_minutes, (
            f"Solar time difference {actual_diff_minutes} doesn't match "
            f"offset {offset_minutes} for longitude {longitude}"
        )


# ============================================================================
# Property Tests for Time Index Calculation
# ============================================================================


class TestTimeIndexProperties:
    """Property-based tests for time index calculation."""

    @given(hour=valid_hours, minute=valid_minutes)
    @settings(max_examples=100)
    def test_time_index_in_valid_range(self, hour: int, minute: int):
        """
        For any valid hour and minute, the time index should be in range 0-12.

        **Validates: Requirements 4.2**
        """
        index = calculate_time_index(hour, minute)
        assert 0 <= index <= 12, f"Time index {index} out of range for {hour:02d}:{minute:02d}"

    @given(hour=valid_hours, minute=valid_minutes)
    @settings(max_examples=100)
    def test_time_index_determinism(self, hour: int, minute: int):
        """
        For any hour and minute, the time index calculation should be deterministic.

        **Validates: Requirements 4.2**
        """
        index1 = calculate_time_index(hour, minute)
        index2 = calculate_time_index(hour, minute)

        assert index1 == index2, (
            f"Non-deterministic time index for {hour:02d}:{minute:02d}: " f"{index1} != {index2}"
        )

    @given(minute=valid_minutes)
    @settings(max_examples=100)
    def test_early_zi_hour(self, minute: int):
        """
        Hour 0 (00:00-00:59) should always map to early Zi (index 0).

        **Validates: Requirements 4.2**
        """
        index = calculate_time_index(0, minute)
        assert index == 0, f"Hour 0 should be early Zi (0), got {index}"

    @given(minute=valid_minutes)
    @settings(max_examples=100)
    def test_late_zi_hour(self, minute: int):
        """
        Hour 23 (23:00-23:59) should always map to late Zi (index 12).

        **Validates: Requirements 4.2**
        """
        index = calculate_time_index(23, minute)
        assert index == 12, f"Hour 23 should be late Zi (12), got {index}"


# ============================================================================
# Property Tests for Adjusted Time Index
# ============================================================================


class TestAdjustedTimeIndexProperties:
    """Property-based tests for solar time adjusted time index."""

    @given(hour=valid_hours, minute=valid_minutes, longitude=chinese_longitudes)
    @settings(max_examples=100)
    def test_adjusted_time_index_in_valid_range(self, hour: int, minute: int, longitude: float):
        """
        For any valid hour, minute, and longitude, the adjusted time index
        should be in range 0-12.

        **Validates: Requirements 4.2, 4.4**
        """
        index, solar_hour, solar_minute = adjust_time_index_for_solar_time(hour, minute, longitude)

        assert 0 <= index <= 12, (
            f"Adjusted time index {index} out of range for "
            f"{hour:02d}:{minute:02d} at longitude {longitude}"
        )
        assert 0 <= solar_hour <= 23, f"Solar hour {solar_hour} out of range"
        assert 0 <= solar_minute <= 59, f"Solar minute {solar_minute} out of range"

    @given(hour=valid_hours, minute=valid_minutes, longitude=chinese_longitudes)
    @settings(max_examples=100)
    def test_adjusted_time_index_determinism(self, hour: int, minute: int, longitude: float):
        """
        For any inputs, the adjusted time index calculation should be deterministic.

        **Validates: Requirements 4.4**
        """
        result1 = adjust_time_index_for_solar_time(hour, minute, longitude)
        result2 = adjust_time_index_for_solar_time(hour, minute, longitude)

        assert result1 == result2, (
            f"Non-deterministic result for {hour:02d}:{minute:02d} at {longitude}: "
            f"{result1} != {result2}"
        )

    @given(hour=valid_hours, minute=valid_minutes)
    @settings(max_examples=100)
    def test_standard_longitude_no_adjustment(self, hour: int, minute: int):
        """
        At the standard Beijing longitude (120°E), the adjusted time index
        should equal the original time index.

        **Validates: Requirements 4.4**
        """
        original_index = calculate_time_index(hour, minute)
        adjusted_index, solar_hour, solar_minute = adjust_time_index_for_solar_time(
            hour, minute, BEIJING_LONGITUDE
        )

        assert adjusted_index == original_index, (
            f"At standard longitude, adjusted index {adjusted_index} should equal "
            f"original {original_index} for {hour:02d}:{minute:02d}"
        )
        assert solar_hour == hour, (
            f"At standard longitude, solar hour {solar_hour} should equal " f"original {hour}"
        )
        assert solar_minute == minute, (
            f"At standard longitude, solar minute {solar_minute} should equal " f"original {minute}"
        )
