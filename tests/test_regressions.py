"""
Regression tests for bugs found during the project review.

Each test here pins down a defect that was verified to reproduce before the fix.
"""

from datetime import datetime

import pytest

from mingli_mcp.core.exceptions import ValidationError
from mingli_mcp.mcp_server.protocol import ProtocolHandler
from mingli_mcp.mcp_server.server import MingliMCPServer
from mingli_mcp.mcp_server.tools import ToolRegistry
from mingli_mcp.systems import get_system

PING = {"jsonrpc": "2.0", "id": 1, "method": "ping"}


@pytest.fixture
def server():
    """A server instance without touching the transport layer."""
    instance = MingliMCPServer.__new__(MingliMCPServer)
    instance.protocol_handler = ProtocolHandler()
    instance.tool_registry = ToolRegistry()
    instance.transport = None
    instance.http_cors_origins = None
    return instance


# ============================================================================
# Malformed JSON-RPC must not kill the session
# ============================================================================


class TestMalformedJsonRpc:
    """A valid-JSON but non-object message used to raise AttributeError.

    On stdio that exception escaped the message loop and terminated the whole
    session, so every later request went unanswered and the client hung.
    """

    @pytest.mark.parametrize("payload", [[], "hi", 123, None, True, [{"method": "ping"}]])
    def test_non_object_message_returns_invalid_request(self, server, payload):
        response = server.handle_request(payload)

        assert response is not None
        assert response["error"]["code"] == -32600
        assert response["id"] is None

    @pytest.mark.parametrize("bad_method", [42, None, ["ping"], {"a": 1}])
    def test_non_string_method_returns_invalid_request(self, server, bad_method):
        response = server.handle_request({"jsonrpc": "2.0", "id": 7, "method": bad_method})

        assert response["error"]["code"] == -32600
        assert response["id"] == 7

    def test_server_still_serves_requests_after_malformed_message(self, server):
        assert server.handle_request(PING)["result"] == {}
        server.handle_request([])
        assert server.handle_request(PING)["result"] == {}

    def test_stdio_loop_survives_malformed_message(self, server, monkeypatch, capsys):
        """The stdio loop must still answer request 2 after a bad message."""
        import json

        from mingli_mcp.transports.stdio_transport import StdioTransport

        lines = iter(
            [
                json.dumps(PING) + "\n",
                "[]\n",
                json.dumps({"jsonrpc": "2.0", "id": 2, "method": "ping"}) + "\n",
                "",  # EOF
            ]
        )
        monkeypatch.setattr("sys.stdin.readline", lambda: next(lines))

        transport = StdioTransport()
        transport.set_message_handler(server.handle_request)
        transport.start()

        emitted = [json.loads(line) for line in capsys.readouterr().out.splitlines() if line]
        assert [r.get("id") for r in emitted] == [1, None, 2]
        assert emitted[1]["error"]["code"] == -32600

    def test_stdio_loop_survives_handler_exception(self, monkeypatch, capsys):
        """Even an exploding handler must not end the session."""
        import json

        from mingli_mcp.transports.stdio_transport import StdioTransport

        lines = iter([json.dumps(PING) + "\n", json.dumps(PING) + "\n", ""])
        monkeypatch.setattr("sys.stdin.readline", lambda: next(lines))

        transport = StdioTransport()
        transport.set_message_handler(lambda _msg: (_ for _ in ()).throw(RuntimeError("boom")))
        transport.start()

        emitted = [json.loads(line) for line in capsys.readouterr().out.splitlines() if line]
        assert len(emitted) == 2
        assert all(r["error"]["code"] == -32603 for r in emitted)


# ============================================================================
# JSON-RPC response shape
# ============================================================================


def test_error_response_always_carries_id(server):
    """JSON-RPC 2.0: the id member is REQUIRED, null when undetectable."""
    response = server.handle_request({"jsonrpc": "2.0", "id": 3, "method": "no_such_method"})

    assert "id" in response
    assert response["id"] == 3


# ============================================================================
# Bazi lunar calendar handling
# ============================================================================


class TestBaziLunarCalendar:
    """Bazi used to ignore is_leap_month and mislabel the lunar date as solar."""

    LEAP_INPUT = {
        "date": "2020-04-15",
        "time_index": 6,
        "gender": "男",
        "calendar": "lunar",
    }

    def test_leap_month_changes_the_chart(self):
        bazi = get_system("bazi")

        normal = bazi.get_chart({**self.LEAP_INPUT, "is_leap_month": False})
        leap = bazi.get_chart({**self.LEAP_INPUT, "is_leap_month": True})

        assert "闰四月" in leap["lunar_date"]
        assert "闰" not in normal["lunar_date"]
        assert normal["solar_date"] != leap["solar_date"]

    def test_solar_date_is_the_real_solar_date(self):
        """For lunar input, solar_date must be converted, not echoed back."""
        bazi = get_system("bazi")

        chart = bazi.get_chart({**self.LEAP_INPUT, "is_leap_month": False})

        assert chart["solar_date"] == "2020-05-07"
        assert chart["solar_date"] != self.LEAP_INPUT["date"]

    def test_solar_input_round_trips_unchanged(self):
        bazi = get_system("bazi")

        chart = bazi.get_chart({"date": "2000-08-16", "time_index": 6, "gender": "女"})

        assert chart["solar_date"] == "2000-08-16"

    def test_bazi_and_ziwei_agree_on_leap_month_solar_date(self):
        """The two systems disagreed because only ziwei honoured is_leap_month."""
        bazi_chart = get_system("bazi").get_chart({**self.LEAP_INPUT, "is_leap_month": True})
        ziwei_chart = get_system("ziwei").get_chart({**self.LEAP_INPUT, "is_leap_month": True})

        bazi_solar = bazi_chart["solar_date"]
        ziwei_solar = ziwei_chart["basic_info"]["阳历日期"]

        # ziwei renders without zero padding (2020-6-6)
        assert [int(p) for p in bazi_solar.split("-")] == [int(p) for p in ziwei_solar.split("-")]


# ============================================================================
# Input validation
# ============================================================================


class TestBirthInfoValidation:
    """These used to surface as TypeError (-32603) or be silently ignored."""

    BASE = {"date": "2000-08-16", "time_index": 6, "gender": "男"}

    @pytest.mark.parametrize("system_name", ["ziwei", "bazi"])
    def test_non_numeric_time_index_raises_validation_error(self, system_name):
        system = get_system(system_name)

        with pytest.raises(ValidationError):
            system.get_chart({**self.BASE, "time_index": "六"})

    @pytest.mark.parametrize("system_name", ["ziwei", "bazi"])
    def test_string_time_index_is_coerced_to_int(self, system_name):
        """ "6" passes validation, so it must not reach the calculation as a str."""
        system = get_system(system_name)

        assert system.get_chart({**self.BASE, "time_index": "6"})

    @pytest.mark.parametrize("bad_index", [6.5, 0.5, True])
    def test_fractional_or_bool_time_index_is_rejected(self, bad_index):
        """6.5 used to be silently truncated to 6 by int(); True counted as 1."""
        system = get_system("bazi")

        with pytest.raises(ValidationError):
            system.get_chart({**self.BASE, "time_index": bad_index})

    def test_integral_float_time_index_is_accepted(self):
        """JSON clients may legitimately send 6.0 for the integer 6."""
        assert get_system("bazi").get_chart({**self.BASE, "time_index": 6.0})

    @pytest.mark.parametrize("bad_calendar", ["LUNAR", "Solar", "gregorian", "", None, 1])
    def test_invalid_calendar_is_rejected(self, bad_calendar):
        system = get_system("ziwei")

        with pytest.raises(ValidationError):
            system.get_chart({**self.BASE, "calendar": bad_calendar})

    @pytest.mark.parametrize("longitude", [-181, 181, 1e9, "116.4", True])
    def test_out_of_range_longitude_is_rejected(self, longitude):
        system = get_system("ziwei")

        with pytest.raises(ValidationError):
            system.get_chart({**self.BASE, "use_solar_time": True, "longitude": longitude})

    @pytest.mark.parametrize(
        ("key", "value"), [("birth_hour", 24), ("birth_hour", -1), ("birth_minute", 60)]
    )
    def test_out_of_range_birth_time_is_rejected(self, key, value):
        system = get_system("ziwei")

        with pytest.raises(ValidationError):
            system.get_chart({**self.BASE, "use_solar_time": True, "longitude": 116.4, key: value})

    def test_solar_time_without_longitude_is_rejected(self):
        """Silently skipping the correction hides a caller mistake."""
        system = get_system("ziwei")

        with pytest.raises(ValidationError):
            system.get_chart({**self.BASE, "use_solar_time": True})


@pytest.mark.parametrize(
    "query", [datetime(1990, 1, 1), datetime(2000, 1, 1)]  # 早于出生年 / 同年但早于出生日
)
def test_bazi_fortune_rejects_query_date_before_birth(query):
    """Used to report age=-10 and '第0个大运' / '-10--1岁'; same-year
    before-birth queries slipped through the year-only check."""
    bazi = get_system("bazi")

    with pytest.raises(ValidationError):
        bazi.get_fortune({"date": "2000-08-16", "time_index": 6, "gender": "男"}, query)


def test_bazi_fortune_accepts_query_on_birth_date():
    bazi = get_system("bazi")

    assert bazi.get_fortune(
        {"date": "2000-08-16", "time_index": 6, "gender": "男"}, datetime(2000, 8, 16)
    )


# ============================================================================
# 晚子时 (late Zi hour) solar-time midpoint
# ============================================================================


class TestLateZiHourMidpoint:
    """Index 12 (23:00-24:00) used to share index 0's midpoint of 00:00."""

    def test_late_zi_midpoint_is_in_the_late_zi_hour(self):
        from mingli_mcp.utils.solar_time import get_time_index_midpoint

        hour, _ = get_time_index_midpoint(12)

        assert hour == 23

    def test_early_and_late_zi_have_distinct_midpoints(self):
        from mingli_mcp.utils.solar_time import get_time_index_midpoint

        assert get_time_index_midpoint(0) != get_time_index_midpoint(12)

    def test_midpoint_maps_back_to_its_own_time_index(self):
        from mingli_mcp.utils.solar_time import calculate_time_index, get_time_index_midpoint

        for index in range(13):
            hour, minute = get_time_index_midpoint(index)
            assert calculate_time_index(hour, minute) == index

    @pytest.mark.parametrize("index", [-1, 13, 99])
    def test_out_of_range_index_raises(self, index):
        from mingli_mcp.utils.solar_time import get_time_index_midpoint

        with pytest.raises(IndexError):
            get_time_index_midpoint(index)


# ============================================================================
# Formatting
# ============================================================================


class TestPalaceLabelFormatting:
    """Palace names already end in 宫, so the markdown printed 命宫宫."""

    def test_chart_markdown_has_no_doubled_palace_suffix(self):
        ziwei = get_system("ziwei")
        chart = ziwei.get_chart({"date": "2000-08-16", "time_index": 6, "gender": "女"})

        markdown = ziwei.formatter.format_chart_markdown(chart)

        assert "宫宫" not in markdown
        assert "### ⭐ 命宫 (" in markdown

    def test_palace_analysis_markdown_has_no_doubled_suffix(self):
        ziwei = get_system("ziwei")
        analysis = ziwei.analyze_palace(
            {"date": "2000-08-16", "time_index": 6, "gender": "女"}, "命宫"
        )

        markdown = ziwei.formatter.format_palace_analysis_markdown(analysis)

        assert "宫宫" not in markdown
        assert markdown.startswith("# 命宫分析")


def test_longitude_formats_west_as_w():
    """Western longitudes used to be printed as e.g. -74.0°E."""
    from mingli_mcp.utils.solar_time import format_longitude

    assert format_longitude(116.4) == "116.4°E"
    assert format_longitude(-74.0) == "74.0°W"
    assert format_longitude(0) == "0°"


def test_solar_time_info_uses_west_notation():
    from mingli_mcp.utils.solar_time import format_solar_time_info

    info = format_solar_time_info(datetime(2000, 8, 16, 12, 0), -74.0, "纽约")

    assert "74.0°W" in info
    assert "-74.0°E" not in info


# ============================================================================
# Rate limiter bookkeeping
# ============================================================================


class TestRateLimiterReadOnlyQueries:
    """defaultdict access made read-only queries create entries."""

    def test_get_remaining_does_not_create_entries(self):
        from mingli_mcp.utils.rate_limiter import RateLimiter

        limiter = RateLimiter(max_requests=5)

        assert limiter.get_remaining("1.2.3.4") == 5
        assert limiter.requests == {}

    def test_get_reset_time_does_not_create_entries(self):
        from mingli_mcp.utils.rate_limiter import RateLimiter

        limiter = RateLimiter()

        assert limiter.get_reset_time("5.6.7.8") is None
        assert limiter.requests == {}

    def test_stats_client_count_is_not_inflated_by_queries(self):
        from mingli_mcp.utils.rate_limiter import RateLimiter

        limiter = RateLimiter()
        limiter.is_allowed("real-client")
        limiter.get_remaining("probe-a")
        limiter.get_reset_time("probe-b")

        assert limiter.get_stats()["total_clients"] == 1


# ============================================================================
# Base system interface
# ============================================================================


def test_analyze_element_is_part_of_the_base_interface():
    """Handlers call analyze_element through BaseFortuneSystem."""
    from mingli_mcp.core.base_system import BaseFortuneSystem

    assert hasattr(BaseFortuneSystem, "analyze_element")

    with pytest.raises(NotImplementedError):
        get_system("ziwei").analyze_element({"date": "2000-08-16", "time_index": 6, "gender": "女"})


# ============================================================================
# 八字四柱换柱边界（立春 / 节）
# ============================================================================


class TestPillarBoundaries:
    """四柱曾用 Lunar.get*InGanZhi()，其换柱边界不是八字口径。

    年柱按农历新年换年（应按立春），月柱边界不是精确的节时刻。
    实测约 2.1% 的命例年柱错误、1.75% 月柱错误。
    """

    @pytest.mark.parametrize(
        ("date", "expected_year_pillar", "expected_zodiac"),
        [
            ("2003-02-01", "壬午", "马"),  # 2003立春在2/4，之前仍属壬午年
            ("2025-02-01", "甲辰", "龙"),  # 2025立春在2/3
            ("1923-02-15", "癸亥", "猪"),  # 立春后已换年
            ("2000-08-16", "庚辰", "龙"),  # 远离边界，不受影响
        ],
    )
    def test_year_pillar_switches_at_lichun(self, date, expected_year_pillar, expected_zodiac):
        chart = get_system("bazi").get_chart({"date": date, "time_index": 3, "gender": "男"})

        assert chart["pillars"]["year"]["pillar"] == expected_year_pillar
        assert chart["zodiac"] == expected_zodiac

    @pytest.mark.parametrize(
        ("date", "time_index", "expected_month_pillar"),
        [
            ("1999-07-07", 3, "庚午"),  # 小暑当天但在交节时刻之前
            ("2009-10-08", 5, "癸酉"),  # 寒露当天
            ("2000-08-16", 6, "甲申"),  # 远离边界
        ],
    )
    def test_month_pillar_switches_at_jie(self, date, time_index, expected_month_pillar):
        chart = get_system("bazi").get_chart(
            {"date": date, "time_index": time_index, "gender": "男"}
        )

        assert chart["pillars"]["month"]["pillar"] == expected_month_pillar

    @pytest.mark.parametrize(
        ("date", "time_index", "expected_year_pillar", "expected_zodiac"),
        [
            ("2003-02-01", 3, "壬午", "马"),  # 立春前，按天粒度即可区分
            # 2024-02-04 立春 16:26 当天：生肖曾按天换（getYearShengXiaoByLiChun），
            # 而年柱按精确时刻换，立春时刻之前的时辰两者会自相矛盾
            ("2024-02-04", 5, "癸卯", "兔"),  # 巳时(10:00) 在立春时刻之前
            ("2024-02-04", 9, "甲辰", "龙"),  # 酉时(18:00) 在立春时刻之后
        ],
    )
    def test_zodiac_agrees_with_year_pillar(
        self, date, time_index, expected_year_pillar, expected_zodiac
    ):
        """生肖必须与年柱同源，包括立春当天的精确时刻边界。"""
        from mingli_mcp.systems.bazi.bazi_system import BaziSystem

        chart = get_system("bazi").get_chart(
            {"date": date, "time_index": time_index, "gender": "男"}
        )
        zhi = chart["pillars"]["year"]["zhi"]

        assert chart["pillars"]["year"]["pillar"] == expected_year_pillar
        assert chart["zodiac"] == expected_zodiac
        assert chart["zodiac"] == BaziSystem.SHENG_XIAO[BaziSystem.ZHI.index(zhi)]


# ============================================================================
# 八字大运（此前是 age // 10 的占位实现）
# ============================================================================


class TestBaziDaYun:
    """大运此前只是按年龄除以10分段，没有干支、起运和顺逆排。"""

    FEMALE = {"date": "2000-08-16", "time_index": 6, "gender": "女"}
    MALE = {"date": "2000-08-16", "time_index": 6, "gender": "男"}

    def _fortune(self, birth_info, year=2026):
        return get_system("bazi").get_fortune(birth_info, datetime(year, 7, 25))

    def test_direction_follows_year_stem_and_gender(self):
        """阳年男顺排，阳年女逆排（2000年为庚辰，庚属阳）。"""
        assert self._fortune(self.MALE)["da_yun_direction"] == "顺排"
        assert self._fortune(self.FEMALE)["da_yun_direction"] == "逆排"

    def test_qi_yun_is_derived_from_solar_term_distance(self):
        fortune = self._fortune(self.FEMALE)
        qi_yun = fortune["qi_yun"]

        assert qi_yun["solar_date"] == "2003-08-05"
        assert (qi_yun["years"], qi_yun["months"], qi_yun["days"]) == (2, 11, 20)
        assert "起运" in qi_yun["description"]

    def test_da_yun_stems_step_through_the_sixty_cycle(self):
        """大运干支自月柱起逐位推移，不是十年一个空标签。"""
        from mingli_mcp.systems.bazi.bazi_system import BaziSystem

        jiazi = [BaziSystem.GAN[i % 10] + BaziSystem.ZHI[i % 12] for i in range(60)]
        fortune = self._fortune(self.FEMALE)
        month_pillar = fortune["basic_chart"]["pillars"]["month"]["pillar"]
        base = jiazi.index(month_pillar)

        real = [e for e in fortune["da_yun_list"] if not e["is_pre_start"]]
        assert [e["gan_zhi"] for e in real[:4]] == [jiazi[(base - n) % 60] for n in range(1, 5)]

    def test_pre_start_period_is_flagged_not_a_da_yun(self):
        fortune = self._fortune(self.FEMALE)
        first = fortune["da_yun_list"][0]

        assert first["is_pre_start"] is True
        assert first["gan_zhi"] == ""
        assert "小运" in first["description"]

    def test_each_da_yun_spans_ten_years_and_is_contiguous(self):
        entries = self._fortune(self.FEMALE)["da_yun_list"]

        for previous, following in zip(entries, entries[1:]):
            assert following["start_age"] == previous["end_age"] + 1
            assert following["start_year"] == previous["end_year"] + 1
        for entry in entries:
            if not entry["is_pre_start"]:
                assert entry["end_age"] - entry["start_age"] == 9

    def test_current_da_yun_matches_the_query_year(self):
        for year in (2005, 2015, 2026, 2040):
            current = self._fortune(self.FEMALE, year)["da_yun"]
            assert current["start_year"] <= year <= current["end_year"]

    def test_da_yun_carries_ten_deities(self):
        current = self._fortune(self.FEMALE)["da_yun"]

        assert current["gan_zhi"] == "辛巳"
        assert current["deities"]["gan"] == "正财"
        assert current["deities"]["zhi"] == ["比肩", "食神", "偏财"]

    def test_liu_nian_carries_deities_and_nominal_age(self):
        fortune = self._fortune(self.FEMALE)

        assert fortune["liu_nian"]["gan_zhi"] == "丙午"
        assert fortune["liu_nian"]["deities"]["gan"] == "比肩"
        assert fortune["nominal_age"] == fortune["age"] + 1

    def test_legacy_fortune_keys_are_preserved(self):
        """旧字段仍需存在，避免破坏既有调用方。"""
        fortune = self._fortune(self.FEMALE)

        assert {"query_date", "age", "day_master", "da_yun", "liu_nian", "basic_chart"} <= set(
            fortune
        )
        assert {"age_range", "description"} <= set(fortune["da_yun"])
        assert {"year", "gan_zhi", "zodiac"} <= set(fortune["liu_nian"])

    def test_markdown_renders_da_yun_table(self):
        from mingli_mcp.systems.bazi.formatter import BaziFormatter

        markdown = BaziFormatter().format_fortune_markdown(self._fortune(self.FEMALE))

        assert "## 大运一览" in markdown
        assert "辛巳" in markdown
        assert "起运" in markdown
        assert "逆排" in markdown

    def test_markdown_still_renders_legacy_shape(self):
        """旧结构（无大运列表/起运）也要能渲染，不能KeyError。"""
        from mingli_mcp.systems.bazi.formatter import BaziFormatter

        legacy = {
            "query_date": "2024-01-15",
            "age": 24,
            "day_master": "丙",
            "da_yun": {"description": "乙酉大运", "age_range": "22-31岁"},
            "liu_nian": {"year": 2024, "gan_zhi": "甲辰", "zodiac": "龙"},
            "basic_chart": {"eight_char": "庚辰 甲申 丙寅 庚寅"},
        }

        markdown = BaziFormatter().format_fortune_markdown(legacy)

        assert "乙酉大运" in markdown
        assert "甲辰" in markdown


# ============================================================================
# 藏干十神（此前代码注释为"简化处理"，未实现）
# ============================================================================


class TestHiddenStemDeities:
    def test_chart_exposes_hidden_stem_deities(self):
        chart = get_system("bazi").get_chart(
            {"date": "2000-08-16", "time_index": 6, "gender": "女"}
        )

        assert chart["zhi_deities"]["year"] == ["食神", "正印", "正官"]
        assert chart["zhi_deities"]["month"] == ["偏财", "七杀", "食神"]

    def test_hidden_deities_align_with_hidden_stems(self):
        chart = get_system("bazi").get_chart(
            {"date": "1985-03-20", "time_index": 4, "gender": "男"}
        )

        for pillar in ("year", "month", "day", "hour"):
            assert len(chart["zhi_deities"][pillar]) == len(chart["zhi_cang_gan"][pillar])

    def test_hidden_deities_match_the_reference_library(self):
        """与lunar_python的十神实现交叉验证。"""
        from lunar_python import Solar

        chart = get_system("bazi").get_chart(
            {"date": "2000-08-16", "time_index": 6, "gender": "女"}
        )
        eight_char = Solar.fromYmdHms(2000, 8, 16, 11, 0, 0).getLunar().getEightChar()

        assert chart["zhi_deities"]["year"] == eight_char.getYearShiShenZhi()
        assert chart["zhi_deities"]["month"] == eight_char.getMonthShiShenZhi()
        assert chart["zhi_deities"]["day"] == eight_char.getDayShiShenZhi()

    def test_markdown_renders_hidden_stem_deities(self):
        from mingli_mcp.systems.bazi.formatter import BaziFormatter

        chart = get_system("bazi").get_chart(
            {"date": "2000-08-16", "time_index": 6, "gender": "女"}
        )
        markdown = BaziFormatter().format_chart_markdown(chart)

        assert "## 藏干十神" in markdown
        assert "戊(食神)" in markdown


# ============================================================================
# 工具调用指标（metrics.py 此前是从未接入的死代码）
# ============================================================================


class TestToolCallMetrics:
    """utils/metrics.py 有198行实现但从未被服务器调用，/stats也不暴露。"""

    @pytest.fixture(autouse=True)
    def _reset_metrics(self):
        from mingli_mcp.utils.metrics import get_metrics

        get_metrics().reset()
        yield
        get_metrics().reset()

    def _call(self, server, tool, args):
        return server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": tool, "arguments": args},
            }
        )

    def test_successful_tool_call_is_recorded(self, server):
        from mingli_mcp.utils.metrics import get_metrics

        self._call(
            server, "get_bazi_chart", {"date": "2000-08-16", "time_index": 6, "gender": "女"}
        )
        summary = get_metrics().get_summary()

        assert summary["total_requests"] == 1
        assert summary["successful_requests"] == 1
        assert summary["system_calls"]["bazi"] == 1
        assert summary["method_calls"]["bazi.get_chart"] == 1

    def test_failed_tool_call_records_error_type(self, server):
        from mingli_mcp.utils.metrics import get_metrics

        self._call(server, "get_bazi_chart", {"date": "2000-08-16", "time_index": 6, "gender": "X"})
        summary = get_metrics().get_summary()

        assert summary["failed_requests"] == 1
        assert summary["error_counts"]["ValidationError"] == 1

    def test_unknown_tool_is_recorded(self, server):
        from mingli_mcp.utils.metrics import get_metrics

        self._call(server, "no_such_tool", {})

        assert get_metrics().get_summary()["error_counts"]["UnknownTool"] == 1

    @pytest.mark.parametrize(
        ("tool", "expected"),
        [
            ("get_ziwei_chart", ("ziwei", "get_chart")),
            ("get_bazi_fortune", ("bazi", "get_fortune")),
            ("analyze_ziwei_palace", ("ziwei", "analyze_palace")),
            ("analyze_bazi_element", ("bazi", "analyze_element")),
            ("list_fortune_systems", ("server", "list_fortune_systems")),
            (None, ("server", "unknown")),
        ],
    )
    def test_tool_name_splits_into_system_and_method(self, tool, expected):
        assert MingliMCPServer._split_tool_name(tool) == expected

    def test_stats_endpoint_exposes_tool_metrics(self, server):
        from fastapi.testclient import TestClient

        from mingli_mcp.transports.http_transport import HttpTransport

        transport = HttpTransport(host="127.0.0.1", port=8080, api_key="k")
        transport.set_message_handler(server.handle_request)
        client = TestClient(transport.app)

        auth = {"Authorization": "Bearer k"}
        response = client.post(
            "/mcp",
            headers=auth,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "get_bazi_chart",
                    "arguments": {"date": "2000-08-16", "time_index": 6, "gender": "女"},
                },
            },
        )
        assert response.status_code == 200
        payload = client.get("/stats", headers=auth).json()

        assert payload["tool_calls"]["total_requests"] == 1
        assert payload["tool_calls"]["method_calls"]["bazi.get_chart"] == 1
        assert payload["tool_calls"]["average_response_time"] >= 0
