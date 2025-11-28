"""
Ziwei tool handlers tests.

Tests for get_ziwei_chart, get_ziwei_fortune, analyze_ziwei_palace handlers.
Requirements: 2.2
"""

import pytest
import json

from mcp.tools.ziwei_handlers import (
    handle_get_ziwei_chart,
    handle_get_ziwei_fortune,
    handle_analyze_ziwei_palace,
)
from core.exceptions import ValidationError


class TestGetZiweiChart:
    """Tests for get_ziwei_chart handler."""

    def test_returns_markdown_by_default(self, sample_birth_info_dict):
        """get_ziwei_chart should return markdown format by default."""
        args = {
            "date": sample_birth_info_dict["date"],
            "time_index": sample_birth_info_dict["time_index"],
            "gender": sample_birth_info_dict["gender"],
        }
        
        result = handle_get_ziwei_chart(args)
        
        assert isinstance(result, str)
        assert "#" in result  # Markdown headers

    def test_returns_json_when_requested(self, sample_birth_info_dict):
        """get_ziwei_chart should return JSON when format=json."""
        args = {
            "date": sample_birth_info_dict["date"],
            "time_index": sample_birth_info_dict["time_index"],
            "gender": sample_birth_info_dict["gender"],
            "format": "json",
        }
        
        result = handle_get_ziwei_chart(args)
        
        # Should be valid JSON
        data = json.loads(result)
        assert "system" in data
        assert "palaces" in data

    def test_raises_error_for_missing_date(self, sample_birth_info_dict):
        """get_ziwei_chart should raise error when date is missing."""
        args = {
            "time_index": sample_birth_info_dict["time_index"],
            "gender": sample_birth_info_dict["gender"],
        }
        
        with pytest.raises(ValidationError):
            handle_get_ziwei_chart(args)

    def test_raises_error_for_missing_time_index(self, sample_birth_info_dict):
        """get_ziwei_chart should raise error when time_index is missing."""
        args = {
            "date": sample_birth_info_dict["date"],
            "gender": sample_birth_info_dict["gender"],
        }
        
        with pytest.raises(ValidationError):
            handle_get_ziwei_chart(args)

    def test_raises_error_for_missing_gender(self, sample_birth_info_dict):
        """get_ziwei_chart should raise error when gender is missing."""
        args = {
            "date": sample_birth_info_dict["date"],
            "time_index": sample_birth_info_dict["time_index"],
        }
        
        with pytest.raises(ValidationError):
            handle_get_ziwei_chart(args)

    def test_raises_error_for_invalid_date(self, sample_birth_info_dict):
        """get_ziwei_chart should raise error for invalid date."""
        args = {
            "date": "1800-01-01",  # Out of range
            "time_index": sample_birth_info_dict["time_index"],
            "gender": sample_birth_info_dict["gender"],
        }
        
        with pytest.raises(ValidationError):
            handle_get_ziwei_chart(args)

    def test_raises_error_for_invalid_time_index(self, sample_birth_info_dict):
        """get_ziwei_chart should raise error for invalid time_index."""
        args = {
            "date": sample_birth_info_dict["date"],
            "time_index": 15,  # Invalid
            "gender": sample_birth_info_dict["gender"],
        }
        
        with pytest.raises(ValidationError):
            handle_get_ziwei_chart(args)

    def test_raises_error_for_invalid_gender(self, sample_birth_info_dict):
        """get_ziwei_chart should raise error for invalid gender."""
        args = {
            "date": sample_birth_info_dict["date"],
            "time_index": sample_birth_info_dict["time_index"],
            "gender": "invalid",
        }
        
        with pytest.raises(ValidationError):
            handle_get_ziwei_chart(args)


class TestGetZiweiFortune:
    """Tests for get_ziwei_fortune handler."""

    def test_returns_markdown_by_default(self, sample_birth_info_dict):
        """get_ziwei_fortune should return markdown format by default."""
        args = {
            "birth_date": sample_birth_info_dict["date"],
            "time_index": sample_birth_info_dict["time_index"],
            "gender": sample_birth_info_dict["gender"],
        }
        
        result = handle_get_ziwei_fortune(args)
        
        assert isinstance(result, str)
        assert "#" in result  # Markdown headers

    def test_returns_json_when_requested(self, sample_birth_info_dict):
        """get_ziwei_fortune should return JSON when format=json."""
        args = {
            "birth_date": sample_birth_info_dict["date"],
            "time_index": sample_birth_info_dict["time_index"],
            "gender": sample_birth_info_dict["gender"],
            "format": "json",
        }
        
        result = handle_get_ziwei_fortune(args)
        
        # Should be valid JSON
        data = json.loads(result)
        assert "query_date" in data

    def test_accepts_query_date(self, sample_birth_info_dict):
        """get_ziwei_fortune should accept a query_date parameter."""
        args = {
            "birth_date": sample_birth_info_dict["date"],
            "time_index": sample_birth_info_dict["time_index"],
            "gender": sample_birth_info_dict["gender"],
            "query_date": "2024-06-15",
            "format": "json",
        }
        
        result = handle_get_ziwei_fortune(args)
        data = json.loads(result)
        
        assert "2024-06-15" in data["query_date"]

    def test_raises_error_for_missing_birth_date(self, sample_birth_info_dict):
        """get_ziwei_fortune should raise error when birth_date is missing."""
        args = {
            "time_index": sample_birth_info_dict["time_index"],
            "gender": sample_birth_info_dict["gender"],
        }
        
        with pytest.raises(ValidationError):
            handle_get_ziwei_fortune(args)


class TestAnalyzeZiweiPalace:
    """Tests for analyze_ziwei_palace handler."""

    def test_returns_markdown_by_default(self, sample_birth_info_dict):
        """analyze_ziwei_palace should return markdown format by default."""
        args = {
            "birth_date": sample_birth_info_dict["date"],
            "time_index": sample_birth_info_dict["time_index"],
            "gender": sample_birth_info_dict["gender"],
            "palace_name": "命宫",
        }
        
        result = handle_analyze_ziwei_palace(args)
        
        assert isinstance(result, str)
        assert "#" in result  # Markdown headers

    def test_returns_json_when_requested(self, sample_birth_info_dict):
        """analyze_ziwei_palace should return JSON when format=json."""
        args = {
            "birth_date": sample_birth_info_dict["date"],
            "time_index": sample_birth_info_dict["time_index"],
            "gender": sample_birth_info_dict["gender"],
            "palace_name": "命宫",
            "format": "json",
        }
        
        result = handle_analyze_ziwei_palace(args)
        
        # Should be valid JSON
        data = json.loads(result)
        assert "palace_name" in data

    def test_raises_error_for_missing_palace_name(self, sample_birth_info_dict):
        """analyze_ziwei_palace should raise error when palace_name is missing."""
        args = {
            "birth_date": sample_birth_info_dict["date"],
            "time_index": sample_birth_info_dict["time_index"],
            "gender": sample_birth_info_dict["gender"],
        }
        
        with pytest.raises(ValidationError):
            handle_analyze_ziwei_palace(args)

    def test_analyzes_different_palaces(self, sample_birth_info_dict):
        """analyze_ziwei_palace should work for different palace names."""
        palaces = ["命宫", "财帛宫", "官禄宫"]
        
        for palace in palaces:
            args = {
                "birth_date": sample_birth_info_dict["date"],
                "time_index": sample_birth_info_dict["time_index"],
                "gender": sample_birth_info_dict["gender"],
                "palace_name": palace,
                "format": "json",
            }
            
            result = handle_analyze_ziwei_palace(args)
            data = json.loads(result)
            
            assert data["palace_name"] == palace
