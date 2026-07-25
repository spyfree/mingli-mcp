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


def test_bazi_fortune_rejects_query_date_before_birth():
    """Used to report age=-10 and '第0个大运' / '-10--1岁'."""
    bazi = get_system("bazi")

    with pytest.raises(ValidationError):
        bazi.get_fortune(
            {"date": "2000-08-16", "time_index": 6, "gender": "男"}, datetime(1990, 1, 1)
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
