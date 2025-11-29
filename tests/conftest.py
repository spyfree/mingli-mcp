"""
Shared pytest fixtures for Mingli MCP Server tests.

This module provides common test fixtures for birth_info, dates, and other
test data used across multiple test modules.
"""

from datetime import date, datetime
from typing import Any, Dict

import pytest

from core.birth_info import BirthInfo

# ============================================================================
# Birth Info Fixtures
# ============================================================================


@pytest.fixture
def sample_birth_info_dict() -> Dict[str, Any]:
    """Standard birth info dictionary for testing."""
    return {
        "date": "2000-08-16",
        "time_index": 2,  # 寅时
        "gender": "女",
        "calendar": "solar",
    }


@pytest.fixture
def sample_birth_info(sample_birth_info_dict) -> BirthInfo:
    """Standard BirthInfo object for testing."""
    return BirthInfo.from_dict(sample_birth_info_dict)


@pytest.fixture
def male_birth_info_dict() -> Dict[str, Any]:
    """Male birth info dictionary for testing."""
    return {
        "date": "1990-05-15",
        "time_index": 6,  # 午时
        "gender": "男",
        "calendar": "solar",
    }


@pytest.fixture
def male_birth_info(male_birth_info_dict) -> BirthInfo:
    """Male BirthInfo object for testing."""
    return BirthInfo.from_dict(male_birth_info_dict)


@pytest.fixture
def lunar_birth_info_dict() -> Dict[str, Any]:
    """Lunar calendar birth info dictionary for testing."""
    return {
        "date": "2000-07-17",
        "time_index": 2,
        "gender": "女",
        "calendar": "lunar",
        "is_leap_month": False,
    }


@pytest.fixture
def lunar_birth_info(lunar_birth_info_dict) -> BirthInfo:
    """Lunar calendar BirthInfo object for testing."""
    return BirthInfo.from_dict(lunar_birth_info_dict)


@pytest.fixture
def solar_time_birth_info_dict() -> Dict[str, Any]:
    """Birth info with solar time correction for testing."""
    return {
        "date": "2000-08-16",
        "time_index": 6,
        "gender": "女",
        "calendar": "solar",
        "longitude": 116.4,  # Beijing
        "latitude": 39.9,
        "use_solar_time": True,
        "birth_hour": 12,
        "birth_minute": 0,
    }


@pytest.fixture
def solar_time_birth_info(solar_time_birth_info_dict) -> BirthInfo:
    """BirthInfo with solar time correction for testing."""
    return BirthInfo.from_dict(solar_time_birth_info_dict)


# ============================================================================
# Date Fixtures
# ============================================================================


@pytest.fixture
def valid_date_str() -> str:
    """A valid date string within supported range."""
    return "2000-08-16"


@pytest.fixture
def min_valid_date_str() -> str:
    """Minimum valid date string (boundary)."""
    return "1900-01-01"


@pytest.fixture
def max_valid_date_str() -> str:
    """Maximum valid date string (boundary)."""
    return "2100-12-31"


@pytest.fixture
def invalid_date_before_range() -> str:
    """Date before supported range."""
    return "1899-12-31"


@pytest.fixture
def invalid_date_after_range() -> str:
    """Date after supported range."""
    return "2101-01-01"


@pytest.fixture
def leap_year_feb_29() -> str:
    """February 29 in a leap year."""
    return "2000-02-29"


@pytest.fixture
def non_leap_year_feb_29() -> str:
    """February 29 in a non-leap year (invalid)."""
    return "2001-02-29"


# ============================================================================
# Time Index Fixtures
# ============================================================================


@pytest.fixture
def valid_time_indices() -> list:
    """All valid time indices (0-12)."""
    return list(range(13))


@pytest.fixture
def time_index_names() -> Dict[int, str]:
    """Mapping of time indices to Chinese names."""
    return {
        0: "早子时",
        1: "丑时",
        2: "寅时",
        3: "卯时",
        4: "辰时",
        5: "巳时",
        6: "午时",
        7: "未时",
        8: "申时",
        9: "酉时",
        10: "戌时",
        11: "亥时",
        12: "晚子时",
    }


# ============================================================================
# Language Fixtures
# ============================================================================


@pytest.fixture
def supported_languages() -> list:
    """List of supported language codes."""
    return ["zh-CN", "zh-TW", "en-US", "ja-JP", "ko-KR", "vi-VN"]


@pytest.fixture
def unsupported_language() -> str:
    """An unsupported language code."""
    return "fr-FR"


# ============================================================================
# Longitude/Latitude Fixtures (for solar time tests)
# ============================================================================


@pytest.fixture
def beijing_coordinates() -> Dict[str, float]:
    """Beijing coordinates."""
    return {"longitude": 116.4, "latitude": 39.9}


@pytest.fixture
def urumqi_coordinates() -> Dict[str, float]:
    """Urumqi coordinates (significant time difference from Beijing)."""
    return {"longitude": 87.6, "latitude": 43.8}


@pytest.fixture
def shanghai_coordinates() -> Dict[str, float]:
    """Shanghai coordinates."""
    return {"longitude": 121.5, "latitude": 31.2}


# ============================================================================
# Query Date Fixtures
# ============================================================================


@pytest.fixture
def current_datetime() -> datetime:
    """Current datetime for fortune queries."""
    return datetime.now()


@pytest.fixture
def sample_query_date() -> datetime:
    """A fixed query date for reproducible tests."""
    return datetime(2024, 1, 15, 12, 0, 0)
