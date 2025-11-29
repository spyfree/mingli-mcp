"""
Bazi tool handlers tests.

Tests for get_bazi_chart, get_bazi_fortune, analyze_bazi_element handlers.
Requirements: 2.2
"""

import json

import pytest

from core.exceptions import ValidationError
from mcp.tools.bazi_handlers import (
    handle_analyze_bazi_element,
    handle_get_bazi_chart,
    handle_get_bazi_fortune,
)


class TestGetBaziChart:
    """Tests for get_bazi_chart handler."""

    def test_returns_markdown_by_default(self, sample_birth_info_dict):
        """get_bazi_chart should return markdown format by default."""
        args = {
            "date": sample_birth_info_dict["date"],
            "time_index": sample_birth_info_dict["time_index"],
            "gender": sample_birth_info_dict["gender"],
        }

        result = handle_get_bazi_chart(args)

        assert isinstance(result, str)
        assert "#" in result  # Markdown headers

    def test_returns_json_when_requested(self, sample_birth_info_dict):
        """get_bazi_chart should return JSON when format=json."""
        args = {
            "date": sample_birth_info_dict["date"],
            "time_index": sample_birth_info_dict["time_index"],
            "gender": sample_birth_info_dict["gender"],
            "format": "json",
        }

        result = handle_get_bazi_chart(args)

        # Should be valid JSON
        data = json.loads(result)
        assert "eight_char" in data
        assert "pillars" in data

    def test_raises_error_for_missing_date(self, sample_birth_info_dict):
        """get_bazi_chart should raise error when date is missing."""
        args = {
            "time_index": sample_birth_info_dict["time_index"],
            "gender": sample_birth_info_dict["gender"],
        }

        with pytest.raises(ValidationError):
            handle_get_bazi_chart(args)

    def test_raises_error_for_missing_time_index(self, sample_birth_info_dict):
        """get_bazi_chart should raise error when time_index is missing."""
        args = {
            "date": sample_birth_info_dict["date"],
            "gender": sample_birth_info_dict["gender"],
        }

        with pytest.raises(ValidationError):
            handle_get_bazi_chart(args)

    def test_raises_error_for_missing_gender(self, sample_birth_info_dict):
        """get_bazi_chart should raise error when gender is missing."""
        args = {
            "date": sample_birth_info_dict["date"],
            "time_index": sample_birth_info_dict["time_index"],
        }

        with pytest.raises(ValidationError):
            handle_get_bazi_chart(args)

    def test_raises_error_for_invalid_date(self, sample_birth_info_dict):
        """get_bazi_chart should raise error for invalid date."""
        args = {
            "date": "1800-01-01",  # Out of range
            "time_index": sample_birth_info_dict["time_index"],
            "gender": sample_birth_info_dict["gender"],
        }

        with pytest.raises(ValidationError):
            handle_get_bazi_chart(args)

    def test_raises_error_for_invalid_time_index(self, sample_birth_info_dict):
        """get_bazi_chart should raise error for invalid time_index."""
        args = {
            "date": sample_birth_info_dict["date"],
            "time_index": 15,  # Invalid
            "gender": sample_birth_info_dict["gender"],
        }

        with pytest.raises(ValidationError):
            handle_get_bazi_chart(args)

    def test_raises_error_for_invalid_gender(self, sample_birth_info_dict):
        """get_bazi_chart should raise error for invalid gender."""
        args = {
            "date": sample_birth_info_dict["date"],
            "time_index": sample_birth_info_dict["time_index"],
            "gender": "invalid",
        }

        with pytest.raises(ValidationError):
            handle_get_bazi_chart(args)


class TestGetBaziFortune:
    """Tests for get_bazi_fortune handler."""

    def test_returns_markdown_by_default(self, sample_birth_info_dict):
        """get_bazi_fortune should return markdown format by default."""
        args = {
            "birth_date": sample_birth_info_dict["date"],
            "time_index": sample_birth_info_dict["time_index"],
            "gender": sample_birth_info_dict["gender"],
        }

        result = handle_get_bazi_fortune(args)

        assert isinstance(result, str)
        assert "#" in result  # Markdown headers

    def test_returns_json_when_requested(self, sample_birth_info_dict):
        """get_bazi_fortune should return JSON when format=json."""
        args = {
            "birth_date": sample_birth_info_dict["date"],
            "time_index": sample_birth_info_dict["time_index"],
            "gender": sample_birth_info_dict["gender"],
            "format": "json",
        }

        result = handle_get_bazi_fortune(args)

        # Should be valid JSON
        data = json.loads(result)
        assert "query_date" in data
        assert "da_yun" in data

    def test_accepts_query_date(self, sample_birth_info_dict):
        """get_bazi_fortune should accept a query_date parameter."""
        args = {
            "birth_date": sample_birth_info_dict["date"],
            "time_index": sample_birth_info_dict["time_index"],
            "gender": sample_birth_info_dict["gender"],
            "query_date": "2024-06-15",
            "format": "json",
        }

        result = handle_get_bazi_fortune(args)
        data = json.loads(result)

        assert "2024-06-15" in data["query_date"]

    def test_raises_error_for_missing_birth_date(self, sample_birth_info_dict):
        """get_bazi_fortune should raise error when birth_date is missing."""
        args = {
            "time_index": sample_birth_info_dict["time_index"],
            "gender": sample_birth_info_dict["gender"],
        }

        with pytest.raises(ValidationError):
            handle_get_bazi_fortune(args)


class TestAnalyzeBaziElement:
    """Tests for analyze_bazi_element handler."""

    def test_returns_markdown_by_default(self, sample_birth_info_dict):
        """analyze_bazi_element should return markdown format by default."""
        args = {
            "birth_date": sample_birth_info_dict["date"],
            "time_index": sample_birth_info_dict["time_index"],
            "gender": sample_birth_info_dict["gender"],
        }

        result = handle_analyze_bazi_element(args)

        assert isinstance(result, str)
        assert "#" in result  # Markdown headers

    def test_returns_json_when_requested(self, sample_birth_info_dict):
        """analyze_bazi_element should return JSON when format=json."""
        args = {
            "birth_date": sample_birth_info_dict["date"],
            "time_index": sample_birth_info_dict["time_index"],
            "gender": sample_birth_info_dict["gender"],
            "format": "json",
        }

        result = handle_analyze_bazi_element(args)

        # Should be valid JSON
        data = json.loads(result)
        assert "day_master" in data
        assert "scores" in data
        assert "balance" in data

    def test_raises_error_for_missing_birth_date(self, sample_birth_info_dict):
        """analyze_bazi_element should raise error when birth_date is missing."""
        args = {
            "time_index": sample_birth_info_dict["time_index"],
            "gender": sample_birth_info_dict["gender"],
        }

        with pytest.raises(ValidationError):
            handle_analyze_bazi_element(args)

    def test_element_analysis_contains_five_elements(self, sample_birth_info_dict):
        """analyze_bazi_element should contain all five elements."""
        args = {
            "birth_date": sample_birth_info_dict["date"],
            "time_index": sample_birth_info_dict["time_index"],
            "gender": sample_birth_info_dict["gender"],
            "format": "json",
        }

        result = handle_analyze_bazi_element(args)
        data = json.loads(result)

        # Check that all five elements are present in scores
        expected_elements = {"木", "火", "土", "金", "水"}
        actual_elements = set(data["scores"].keys())

        assert expected_elements == actual_elements
