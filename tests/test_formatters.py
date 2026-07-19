"""
Tests for formatter modules.

This module tests:
- utils/formatters.py (JSON-RPC response formatting)
- systems/ziwei/formatter.py (Ziwei chart/fortune/palace formatting)
- systems/bazi/formatter.py (Bazi chart/fortune/element formatting)

Requirements: 2.4
"""

from datetime import datetime
from typing import Any, Dict

import pytest

from mingli_mcp.systems.bazi.formatter import BaziFormatter
from mingli_mcp.systems.ziwei.formatter import ZiweiFormatter
from mingli_mcp.utils.formatters import format_error_response, format_success_response

# ============================================================================
# JSON-RPC Response Formatting Tests (utils/formatters.py)
# ============================================================================


class TestFormatErrorResponse:
    """Tests for format_error_response function."""

    def test_error_response_with_request_id(self):
        """Error response includes request_id when provided."""
        response = format_error_response(
            error_code=-32600, error_message="Invalid Request", request_id=1
        )

        assert response["jsonrpc"] == "2.0"
        assert response["error"]["code"] == -32600
        assert response["error"]["message"] == "Invalid Request"
        assert response["id"] == 1

    def test_error_response_without_request_id(self):
        """Error response omits id when request_id is None."""
        response = format_error_response(
            error_code=-32700, error_message="Parse error", request_id=None
        )

        assert response["jsonrpc"] == "2.0"
        assert response["error"]["code"] == -32700
        assert response["error"]["message"] == "Parse error"
        assert "id" not in response

    def test_error_response_with_string_request_id(self):
        """Error response handles string request_id."""
        response = format_error_response(
            error_code=-32601, error_message="Method not found", request_id="abc-123"
        )

        assert response["id"] == "abc-123"


class TestFormatSuccessResponse:
    """Tests for format_success_response function."""

    def test_success_response_with_dict_result(self):
        """Success response with dictionary result."""
        result = {"tools": [{"name": "test_tool"}]}
        response = format_success_response(result=result, request_id=1)

        assert response["jsonrpc"] == "2.0"
        assert response["result"] == result
        assert response["id"] == 1

    def test_success_response_with_list_result(self):
        """Success response with list result."""
        result = [1, 2, 3]
        response = format_success_response(result=result, request_id=2)

        assert response["result"] == result

    def test_success_response_without_request_id(self):
        """Success response omits id when request_id is None."""
        response = format_success_response(result="ok", request_id=None)

        assert response["jsonrpc"] == "2.0"
        assert response["result"] == "ok"
        assert "id" not in response

    def test_success_response_with_null_result(self):
        """Success response handles None result."""
        response = format_success_response(result=None, request_id=1)

        assert response["result"] is None


# ============================================================================
# Ziwei Formatter Tests (systems/ziwei/formatter.py)
# ============================================================================


class TestZiweiFormatter:
    """Tests for ZiweiFormatter class."""

    @pytest.fixture
    def formatter(self):
        """Create a ZiweiFormatter instance."""
        return ZiweiFormatter()

    @pytest.fixture
    def sample_chart_data(self) -> Dict[str, Any]:
        """Sample chart data for testing."""
        return {
            "system": "紫微斗数",
            "basic_info": {
                "阳历日期": "2000-08-16",
                "农历日期": "庚辰年七月十七",
                "四柱": "庚辰 甲申 丙寅 庚寅",
                "时辰": "寅时",
                "时间段": "03:00-05:00",
                "星座": "狮子座",
                "生肖": "龙",
                "命宫地支": "午",
                "身宫地支": "戌",
                "命主": "廉贞",
                "身主": "天相",
                "五行局": "火六局",
            },
            "palaces": [
                {
                    "name": "命宫",
                    "is_body_palace": False,
                    "is_original_palace": True,
                    "heavenly_stem": "壬",
                    "earthly_branch": "午",
                    "major_stars": [{"name": "紫微", "type": "major", "brightness": "庙"}],
                    "minor_stars": [{"name": "左辅", "type": "minor", "brightness": ""}],
                    "adjective_stars": [{"name": "天魁", "type": "adjective", "brightness": ""}],
                    "changsheng12": "长生",
                    "boshi12": "博士",
                    "stage": {"range": [22, 31], "heavenly_stem": "壬"},
                }
            ],
            "metadata": {
                "generated_at": "2024-01-15T12:00:00",
                "version": "1.0.0",
            },
        }

    @pytest.fixture
    def sample_fortune_data(self) -> Dict[str, Any]:
        """Sample fortune data for testing."""
        return {
            "query_date": "2024-01-15",
            "solar_date": "2024-01-15",
            "lunar_date": "癸卯年腊月初五",
            "decadal": {
                "name": "大限",
                "index": 3,
                "heavenly_stem": "壬",
                "earthly_branch": "午",
                "palace_names": ["命宫", "父母宫", "福德宫"],
                "mutagen": ["化禄", "化权"],
                "age": "22-31岁",
            },
            "yearly": {
                "name": "流年",
                "index": 0,
                "heavenly_stem": "甲",
                "earthly_branch": "辰",
                "palace_names": ["财帛宫", "官禄宫"],
            },
        }

    @pytest.fixture
    def sample_palace_analysis(self) -> Dict[str, Any]:
        """Sample palace analysis data for testing."""
        return {
            "palace_name": "命宫",
            "is_body_palace": True,
            "is_original_palace": True,
            "heavenly_stem": "壬",
            "earthly_branch": "午",
            "major_stars": [{"name": "紫微", "brightness": "庙"}],
            "minor_stars": [{"name": "左辅", "brightness": ""}],
            "adjective_stars": [{"name": "天魁"}],
            "changsheng12": "长生",
            "boshi12": "博士",
            "stage": {"range": [22, 31]},
            "basic_info": {"命主": "廉贞"},
        }

    # Chart formatting tests
    def test_format_chart_markdown_contains_system(self, formatter, sample_chart_data):
        """Chart markdown contains system name."""
        md = formatter.format_chart_markdown(sample_chart_data)
        assert "紫微斗数" in md

    def test_format_chart_markdown_contains_basic_info(self, formatter, sample_chart_data):
        """Chart markdown contains all basic info fields."""
        md = formatter.format_chart_markdown(sample_chart_data)

        for key in sample_chart_data["basic_info"]:
            assert key in md

    def test_format_chart_markdown_contains_palace_section(self, formatter, sample_chart_data):
        """Chart markdown contains palace section."""
        md = formatter.format_chart_markdown(sample_chart_data)
        assert "十二宫详情" in md

    def test_format_chart_markdown_contains_palace_name(self, formatter, sample_chart_data):
        """Chart markdown contains palace names."""
        md = formatter.format_chart_markdown(sample_chart_data)
        assert "命宫" in md

    def test_format_chart_markdown_contains_stars(self, formatter, sample_chart_data):
        """Chart markdown contains star information."""
        md = formatter.format_chart_markdown(sample_chart_data)
        assert "紫微" in md
        assert "主星" in md

    # Fortune formatting tests
    def test_format_fortune_markdown_contains_query_date(self, formatter, sample_fortune_data):
        """Fortune markdown contains query date."""
        md = formatter.format_fortune_markdown(sample_fortune_data)
        assert sample_fortune_data["query_date"] in md

    def test_format_fortune_markdown_contains_decadal(self, formatter, sample_fortune_data):
        """Fortune markdown contains decadal (大限) section."""
        md = formatter.format_fortune_markdown(sample_fortune_data)
        assert "大限" in md

    def test_format_fortune_markdown_contains_yearly(self, formatter, sample_fortune_data):
        """Fortune markdown contains yearly (流年) section."""
        md = formatter.format_fortune_markdown(sample_fortune_data)
        assert "流年" in md

    def test_format_fortune_markdown_contains_palace_names(self, formatter, sample_fortune_data):
        """Fortune markdown contains palace names sequence."""
        md = formatter.format_fortune_markdown(sample_fortune_data)
        assert "宫位顺序" in md

    def test_format_fortune_markdown_contains_mutagen(self, formatter, sample_fortune_data):
        """Fortune markdown contains mutagen (四化) when present."""
        md = formatter.format_fortune_markdown(sample_fortune_data)
        assert "四化" in md
        assert "化禄" in md

    # Palace analysis formatting tests
    def test_format_palace_analysis_markdown_contains_palace_name(
        self, formatter, sample_palace_analysis
    ):
        """Palace analysis markdown contains palace name."""
        md = formatter.format_palace_analysis_markdown(sample_palace_analysis)
        assert "命宫" in md

    def test_format_palace_analysis_markdown_shows_body_palace_marker(
        self, formatter, sample_palace_analysis
    ):
        """Palace analysis markdown shows body palace marker."""
        md = formatter.format_palace_analysis_markdown(sample_palace_analysis)
        assert "⭐身宫" in md

    def test_format_palace_analysis_markdown_shows_original_palace_marker(
        self, formatter, sample_palace_analysis
    ):
        """Palace analysis markdown shows original palace marker."""
        md = formatter.format_palace_analysis_markdown(sample_palace_analysis)
        assert "🏠来因宫" in md

    def test_format_palace_analysis_markdown_contains_stars_section(
        self, formatter, sample_palace_analysis
    ):
        """Palace analysis markdown contains stars section."""
        md = formatter.format_palace_analysis_markdown(sample_palace_analysis)
        assert "星曜配置" in md
        assert "主星" in md

    def test_format_palace_analysis_markdown_contains_changsheng12(
        self, formatter, sample_palace_analysis
    ):
        """Palace analysis markdown contains changsheng12."""
        md = formatter.format_palace_analysis_markdown(sample_palace_analysis)
        assert "长生十二神" in md

    def test_format_palace_analysis_markdown_contains_stage_range(
        self, formatter, sample_palace_analysis
    ):
        """Palace analysis markdown contains stage age range."""
        md = formatter.format_palace_analysis_markdown(sample_palace_analysis)
        assert "大限" in md
        assert "22" in md
        assert "31" in md


# ============================================================================
# Bazi Formatter Tests (systems/bazi/formatter.py)
# ============================================================================


class TestBaziFormatter:
    """Tests for BaziFormatter class."""

    @pytest.fixture
    def formatter(self):
        """Create a BaziFormatter instance."""
        return BaziFormatter()

    @pytest.fixture
    def sample_chart_data(self) -> Dict[str, Any]:
        """Sample Bazi chart data for testing."""
        return {
            "solar_date": "2000-08-16",
            "lunar_date": "庚辰年七月十七",
            "gender": "女",
            "zodiac": "龙",
            "eight_char": "庚辰 甲申 丙寅 庚寅",
            "pillars": {
                "year": {"gan": "庚", "zhi": "辰", "pillar": "庚辰"},
                "month": {"gan": "甲", "zhi": "申", "pillar": "甲申"},
                "day": {"gan": "丙", "zhi": "寅", "pillar": "丙寅"},
                "hour": {"gan": "庚", "zhi": "寅", "pillar": "庚寅"},
            },
            "day_master": "丙火",
            "deities": {
                "year_gan": "偏财",
                "month_gan": "偏印",
                "day_gan": "日主",
                "hour_gan": "偏财",
            },
            "wu_xing": {
                "description": "金3 木2 水0 火2 土1",
                "scores": {"金": 3, "木": 2, "水": 0, "火": 2, "土": 1},
            },
            "zhi_cang_gan": {
                "year": ["戊", "乙", "癸"],
                "month": ["庚", "壬", "戊"],
                "day": ["甲", "丙", "戊"],
                "hour": ["甲", "丙", "戊"],
            },
        }

    @pytest.fixture
    def sample_fortune_data(self) -> Dict[str, Any]:
        """Sample Bazi fortune data for testing."""
        return {
            "query_date": "2024-01-15",
            "age": 24,
            "day_master": "丙火",
            "da_yun": {
                "description": "乙酉大运",
                "age_range": "22-31岁",
            },
            "liu_nian": {
                "year": 2024,
                "gan_zhi": "甲辰",
                "zodiac": "龙",
            },
            "basic_chart": {
                "eight_char": "庚辰 甲申 丙寅 庚寅",
            },
        }

    @pytest.fixture
    def sample_element_data(self) -> Dict[str, Any]:
        """Sample Bazi element analysis data for testing."""
        return {
            "day_master": "丙",
            "day_master_element": "火",
            "scores": {"金": 3, "木": 2, "水": 0, "火": 2, "土": 1},
            "percentages": {"金": 37.5, "木": 25.0, "水": 0.0, "火": 25.0, "土": 12.5},
            "strongest": {"element": "金", "score": 3},
            "weakest": {"element": "水", "score": 0},
            "missing": ["水"],
            "balance": "五行不平衡",
        }

    # Chart formatting tests
    def test_format_chart_json_returns_dict(self, formatter, sample_chart_data):
        """format_chart with json format returns the data dict."""
        result = formatter.format_chart(sample_chart_data, format_type="json")
        assert result == sample_chart_data

    def test_format_chart_markdown_contains_title(self, formatter, sample_chart_data):
        """Chart markdown contains title."""
        md = formatter.format_chart(sample_chart_data, format_type="markdown")
        assert "八字排盘" in md

    def test_format_chart_markdown_contains_basic_info(self, formatter, sample_chart_data):
        """Chart markdown contains basic info."""
        md = formatter.format_chart(sample_chart_data, format_type="markdown")
        assert sample_chart_data["solar_date"] in md
        assert sample_chart_data["gender"] in md
        assert sample_chart_data["zodiac"] in md

    def test_format_chart_markdown_contains_eight_char(self, formatter, sample_chart_data):
        """Chart markdown contains eight characters."""
        md = formatter.format_chart(sample_chart_data, format_type="markdown")
        assert sample_chart_data["eight_char"] in md

    def test_format_chart_markdown_contains_pillars_table(self, formatter, sample_chart_data):
        """Chart markdown contains pillars table."""
        md = formatter.format_chart(sample_chart_data, format_type="markdown")
        assert "年柱" in md
        assert "月柱" in md
        assert "日柱" in md
        assert "时柱" in md

    def test_format_chart_markdown_contains_day_master(self, formatter, sample_chart_data):
        """Chart markdown contains day master."""
        md = formatter.format_chart(sample_chart_data, format_type="markdown")
        assert "日主" in md
        assert sample_chart_data["day_master"] in md

    def test_format_chart_markdown_contains_deities(self, formatter, sample_chart_data):
        """Chart markdown contains ten gods (十神)."""
        md = formatter.format_chart(sample_chart_data, format_type="markdown")
        assert "十神分析" in md
        assert "偏财" in md
        assert "偏印" in md

    def test_format_chart_markdown_contains_wuxing(self, formatter, sample_chart_data):
        """Chart markdown contains five elements analysis."""
        md = formatter.format_chart(sample_chart_data, format_type="markdown")
        assert "五行分析" in md

    def test_format_chart_markdown_contains_zhi_cang_gan(self, formatter, sample_chart_data):
        """Chart markdown contains hidden stems."""
        md = formatter.format_chart(sample_chart_data, format_type="markdown")
        assert "地支藏干" in md

    # Fortune formatting tests
    def test_format_fortune_json_returns_dict(self, formatter, sample_fortune_data):
        """format_fortune with json format returns the data dict."""
        result = formatter.format_fortune(sample_fortune_data, format_type="json")
        assert result == sample_fortune_data

    def test_format_fortune_markdown_contains_title(self, formatter, sample_fortune_data):
        """Fortune markdown contains title."""
        md = formatter.format_fortune(sample_fortune_data, format_type="markdown")
        assert "八字运势" in md

    def test_format_fortune_markdown_contains_query_info(self, formatter, sample_fortune_data):
        """Fortune markdown contains query information."""
        md = formatter.format_fortune(sample_fortune_data, format_type="markdown")
        assert sample_fortune_data["query_date"] in md
        assert str(sample_fortune_data["age"]) in md

    def test_format_fortune_markdown_contains_da_yun(self, formatter, sample_fortune_data):
        """Fortune markdown contains major luck cycle (大运)."""
        md = formatter.format_fortune(sample_fortune_data, format_type="markdown")
        assert "大运" in md
        assert sample_fortune_data["da_yun"]["description"] in md

    def test_format_fortune_markdown_contains_liu_nian(self, formatter, sample_fortune_data):
        """Fortune markdown contains yearly fortune (流年)."""
        md = formatter.format_fortune(sample_fortune_data, format_type="markdown")
        assert "流年" in md
        assert sample_fortune_data["liu_nian"]["gan_zhi"] in md

    def test_format_fortune_markdown_contains_basic_chart(self, formatter, sample_fortune_data):
        """Fortune markdown contains basic chart."""
        md = formatter.format_fortune(sample_fortune_data, format_type="markdown")
        assert "本命八字" in md

    # Element analysis formatting tests
    def test_format_element_json_returns_dict(self, formatter, sample_element_data):
        """format_element_analysis with json format returns the data dict."""
        result = formatter.format_element_analysis(sample_element_data, format_type="json")
        assert result == sample_element_data

    def test_format_element_markdown_contains_title(self, formatter, sample_element_data):
        """Element analysis markdown contains title."""
        md = formatter.format_element_analysis(sample_element_data, format_type="markdown")
        assert "五行分析" in md

    def test_format_element_markdown_contains_day_master(self, formatter, sample_element_data):
        """Element analysis markdown contains day master info."""
        md = formatter.format_element_analysis(sample_element_data, format_type="markdown")
        assert "日主" in md
        assert sample_element_data["day_master"] in md

    def test_format_element_markdown_contains_scores_table(self, formatter, sample_element_data):
        """Element analysis markdown contains scores table."""
        md = formatter.format_element_analysis(sample_element_data, format_type="markdown")
        assert "五行分数" in md
        assert "金" in md
        assert "木" in md
        assert "水" in md
        assert "火" in md
        assert "土" in md

    def test_format_element_markdown_contains_analysis_results(
        self, formatter, sample_element_data
    ):
        """Element analysis markdown contains analysis results."""
        md = formatter.format_element_analysis(sample_element_data, format_type="markdown")
        assert "最旺五行" in md
        assert "最弱五行" in md
        assert "缺失五行" in md
        assert "平衡度" in md

    def test_format_element_markdown_contains_missing_element_advice(
        self, formatter, sample_element_data
    ):
        """Element analysis markdown contains advice for missing elements."""
        md = formatter.format_element_analysis(sample_element_data, format_type="markdown")
        assert "建议" in md
        assert "水" in md  # Missing element

    def test_format_element_markdown_contains_balance_advice(self, formatter, sample_element_data):
        """Element analysis markdown contains balance advice."""
        md = formatter.format_element_analysis(sample_element_data, format_type="markdown")
        assert "不平衡" in md

    def test_format_element_no_missing_elements(self, formatter):
        """Element analysis handles case with no missing elements."""
        data = {
            "day_master": "丙",
            "day_master_element": "火",
            "scores": {"金": 2, "木": 2, "水": 1, "火": 2, "土": 1},
            "percentages": {"金": 25.0, "木": 25.0, "水": 12.5, "火": 25.0, "土": 12.5},
            "strongest": {"element": "金", "score": 2},
            "weakest": {"element": "水", "score": 1},
            "missing": [],
            "balance": "五行较平衡",
        }
        md = formatter.format_element_analysis(data, format_type="markdown")
        assert "缺失五行" in md
        assert "无" in md
