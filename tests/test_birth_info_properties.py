#!/usr/bin/env python3
"""
Property-based tests for BirthInfo using Hypothesis.

This module contains property-based tests that verify universal properties
of the BirthInfo class across a wide range of inputs.
"""

from datetime import date
from hypothesis import given, strategies as st, settings, assume

from core.birth_info import BirthInfo
from utils.validators import MIN_YEAR, MAX_YEAR


# ============================================================================
# Hypothesis Strategies for BirthInfo Fields
# ============================================================================

# Strategy for valid dates within the supported range (1900-2100)
valid_dates = st.dates(
    min_value=date(MIN_YEAR, 1, 1),
    max_value=date(MAX_YEAR, 12, 31)
).map(lambda d: d.strftime("%Y-%m-%d"))

# Strategy for valid time indices (0-12)
valid_time_indices = st.integers(min_value=0, max_value=12)

# Strategy for valid gender values
valid_genders = st.sampled_from(["男", "女"])

# Strategy for valid calendar types
valid_calendars = st.sampled_from(["solar", "lunar"])

# Strategy for is_leap_month boolean
is_leap_month_values = st.booleans()

# Strategy for valid longitude values (-180 to 180)
valid_longitudes = st.floats(min_value=-180.0, max_value=180.0, allow_nan=False, allow_infinity=False)

# Strategy for valid latitude values (-90 to 90)
valid_latitudes = st.floats(min_value=-90.0, max_value=90.0, allow_nan=False, allow_infinity=False)

# Strategy for valid birth hours (0-23)
valid_birth_hours = st.integers(min_value=0, max_value=23)

# Strategy for valid birth minutes (0-59)
valid_birth_minutes = st.integers(min_value=0, max_value=59)

# Strategy for optional longitude (None or valid value)
optional_longitudes = st.one_of(st.none(), valid_longitudes)

# Strategy for optional latitude (None or valid value)
optional_latitudes = st.one_of(st.none(), valid_latitudes)

# Strategy for optional birth hour (None or valid value)
optional_birth_hours = st.one_of(st.none(), valid_birth_hours)

# Strategy for optional birth minute (None or valid value)
optional_birth_minutes = st.one_of(st.none(), valid_birth_minutes)


# ============================================================================
# Composite Strategies for BirthInfo
# ============================================================================

@st.composite
def birth_info_without_solar_time(draw):
    """
    Strategy for generating valid BirthInfo objects without solar time.
    
    This generates BirthInfo with the required fields only, without
    any solar time correction fields.
    """
    return BirthInfo(
        date=draw(valid_dates),
        time_index=draw(valid_time_indices),
        gender=draw(valid_genders),
        calendar=draw(valid_calendars),
        is_leap_month=draw(is_leap_month_values),
    )


@st.composite
def birth_info_with_solar_time(draw):
    """
    Strategy for generating valid BirthInfo objects with solar time enabled.
    
    When use_solar_time is True, longitude is required. This strategy
    ensures all solar time constraints are satisfied.
    """
    return BirthInfo(
        date=draw(valid_dates),
        time_index=draw(valid_time_indices),
        gender=draw(valid_genders),
        calendar=draw(valid_calendars),
        is_leap_month=draw(is_leap_month_values),
        longitude=draw(valid_longitudes),
        latitude=draw(optional_latitudes),
        use_solar_time=True,
        birth_hour=draw(optional_birth_hours),
        birth_minute=draw(optional_birth_minutes),
    )


@st.composite
def birth_info_any(draw):
    """
    Strategy for generating any valid BirthInfo object.
    
    This can generate BirthInfo with or without solar time correction,
    covering the full range of valid configurations.
    """
    use_solar = draw(st.booleans())
    
    if use_solar:
        # When using solar time, longitude is required
        return BirthInfo(
            date=draw(valid_dates),
            time_index=draw(valid_time_indices),
            gender=draw(valid_genders),
            calendar=draw(valid_calendars),
            is_leap_month=draw(is_leap_month_values),
            longitude=draw(valid_longitudes),
            latitude=draw(optional_latitudes),
            use_solar_time=True,
            birth_hour=draw(optional_birth_hours),
            birth_minute=draw(optional_birth_minutes),
        )
    else:
        # Without solar time, longitude/latitude are optional
        longitude = draw(optional_longitudes)
        return BirthInfo(
            date=draw(valid_dates),
            time_index=draw(valid_time_indices),
            gender=draw(valid_genders),
            calendar=draw(valid_calendars),
            is_leap_month=draw(is_leap_month_values),
            longitude=longitude,
            latitude=draw(optional_latitudes) if longitude is not None else None,
            use_solar_time=False,
            birth_hour=draw(optional_birth_hours),
            birth_minute=draw(optional_birth_minutes),
        )


@st.composite
def birth_info_dict_strategy(draw):
    """
    Strategy for generating valid BirthInfo dictionaries.
    
    This generates dictionaries that can be passed to BirthInfo.from_dict().
    """
    use_solar = draw(st.booleans())
    
    data = {
        "date": draw(valid_dates),
        "time_index": draw(valid_time_indices),
        "gender": draw(valid_genders),
        "calendar": draw(valid_calendars),
        "is_leap_month": draw(is_leap_month_values),
    }
    
    if use_solar:
        data["longitude"] = draw(valid_longitudes)
        data["use_solar_time"] = True
        # Optionally add latitude
        if draw(st.booleans()):
            data["latitude"] = draw(valid_latitudes)
        # Optionally add birth time
        if draw(st.booleans()):
            data["birth_hour"] = draw(valid_birth_hours)
            data["birth_minute"] = draw(valid_birth_minutes)
    else:
        # Optionally add longitude/latitude without solar time
        if draw(st.booleans()):
            data["longitude"] = draw(valid_longitudes)
            if draw(st.booleans()):
                data["latitude"] = draw(valid_latitudes)
    
    return data


# ============================================================================
# Property Tests for BirthInfo
# ============================================================================

class TestBirthInfoProperties:
    """Property-based tests for BirthInfo class."""

    @given(info=birth_info_without_solar_time())
    @settings(max_examples=100)
    def test_birth_info_creation_valid(self, info: BirthInfo):
        """
        For any valid combination of BirthInfo fields, the object should
        be created successfully without raising exceptions.
        """
        # If we got here, the object was created successfully
        assert info.date is not None
        assert 0 <= info.time_index <= 12
        assert info.gender in ["男", "女"]
        assert info.calendar in ["solar", "lunar"]

    @given(info=birth_info_any())
    @settings(max_examples=100)
    def test_time_range_always_valid(self, info: BirthInfo):
        """
        For any valid BirthInfo, get_time_range() should return a non-empty
        string in the expected format.
        """
        time_range = info.get_time_range()
        assert isinstance(time_range, str)
        assert len(time_range) > 0
        assert ":" in time_range  # Should contain time format

    @given(info=birth_info_any())
    @settings(max_examples=100)
    def test_time_name_always_valid(self, info: BirthInfo):
        """
        For any valid BirthInfo, get_time_name() should return a non-empty
        Chinese time period name.
        """
        time_name = info.get_time_name()
        assert isinstance(time_name, str)
        assert len(time_name) > 0
        # Should be one of the valid time names
        valid_names = [
            "早子时", "丑时", "寅时", "卯时", "辰时", "巳时",
            "午时", "未时", "申时", "酉时", "戌时", "亥时", "晚子时"
        ]
        assert time_name in valid_names
