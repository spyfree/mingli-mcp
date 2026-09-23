"""
全语言回归矩阵：7 个工具 × 6 种语言 × 3 组出生资料

咨询站点给每个工具都传 language=<界面语言>。09-23 发现 analyze_ziwei_palace 在
zh-CN 以外的语言全部报「未找到宫位」（宫名被 iztro 本地化，匹配却用简体规范名），
上线很久没人发现，因为测试只跑 zh-CN。这组测试走完整的 tools/call 链路，
并要求同一出生资料在不同语言下结构一致（宫位顺序、干支位置、主星数量）。
"""

import json
from datetime import datetime, timedelta

import pytest

from mingli_mcp.mcp_server.server import MingliMCPServer
from mingli_mcp.utils.validators import SUPPORTED_LANGUAGES

LANGUAGES = ["zh-CN", "zh-TW", "ja-JP", "ko-KR", "vi-VN", "en-US"]

BIRTHS = {
    "solar_regular": {"birth_date": "2000-08-16", "time_index": 2, "gender": "女"},
    # 晚子时（23:00-23:59）：八字按子初换日，日柱进位次日
    "late_zi_hour": {"birth_date": "1995-03-10", "time_index": 12, "gender": "男"},
    # 农历闰月：2020 年闰四月
    "lunar_leap_month": {
        "birth_date": "2020-04-15",
        "time_index": 6,
        "gender": "女",
        "calendar": "lunar",
        "is_leap_month": True,
    },
}

TOOLS = [
    "get_ziwei_chart",
    "get_ziwei_fortune",
    "analyze_ziwei_palace",
    "get_bazi_chart",
    "get_bazi_fortune",
    "analyze_bazi_element",
    "list_fortune_systems",
]

EXTRA_ARGS = {
    "get_ziwei_fortune": {"query_date": "2026-09-23"},
    "get_bazi_fortune": {"query_date": "2026-09-23"},
    "analyze_ziwei_palace": {"palace_name": "官禄宫"},
}


@pytest.fixture(scope="module")
def server():
    return MingliMCPServer()


def call_tool(server, name, arguments):
    response = server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        }
    )
    assert "error" not in response, response
    result = response["result"]
    assert not result.get("isError"), result["content"][0]["text"]
    return result["content"][0]["text"]


def call_json(server, name, birth, language, **extra):
    args = {**birth, "language": language, "format": "json", **EXTRA_ARGS.get(name, {}), **extra}
    return json.loads(call_tool(server, name, args))


def test_matrix_covers_every_registered_tool_and_language(server):
    assert sorted(TOOLS) == sorted(d["name"] for d in server.tool_registry.get_definitions())
    assert sorted(LANGUAGES) == sorted(SUPPORTED_LANGUAGES)


@pytest.mark.parametrize("birth_id", BIRTHS)
@pytest.mark.parametrize("language", LANGUAGES)
@pytest.mark.parametrize("tool", TOOLS)
def test_every_tool_succeeds_in_every_language(server, tool, language, birth_id):
    birth = BIRTHS[birth_id] if tool != "list_fortune_systems" else {}
    args = {**birth, "language": language, **EXTRA_ARGS.get(tool, {})}
    if tool != "list_fortune_systems":
        args["format"] = "json"
    text = call_tool(server, tool, args)
    assert text

    if tool == "get_ziwei_chart":
        chart = json.loads(text)
        assert len(chart["palaces"]) == 12
        assert len(chart["flying_sihua"]) == 12
    elif tool == "get_bazi_chart":
        chart = json.loads(text)
        assert set(chart["pillars"]) == {"year", "month", "day", "hour"}
        assert isinstance(chart["relations"], list)
    elif tool == "analyze_ziwei_palace":
        assert json.loads(text)["palace_key"] == "careerPalace"


# ----------------------------------------------------------------------------
# 结构一致性：同一出生资料，不同语言只换显示文字
# ----------------------------------------------------------------------------


def _ziwei_structure(chart):
    return [
        (
            palace["key"],
            palace["heavenly_stem_zh"],
            palace["earthly_branch_zh"],
            len(palace["major_stars"]),
            [star["key"] for star in palace["major_stars"]],
            [star["key"] for star in palace["minor_stars"]],
        )
        for palace in chart["palaces"]
    ]


def _flying_structure(chart):
    return [
        (
            item["palace_key"],
            [(t["mutagen"], t["star_key"], t["to_palace_key"]) for t in item["transforms"]],
        )
        for item in chart["flying_sihua"]
    ]


@pytest.mark.parametrize("birth_id", BIRTHS)
def test_ziwei_chart_structure_is_language_independent(server, birth_id):
    baseline = call_json(server, "get_ziwei_chart", BIRTHS[birth_id], "zh-CN")
    for language in LANGUAGES[1:]:
        chart = call_json(server, "get_ziwei_chart", BIRTHS[birth_id], language)
        assert _ziwei_structure(chart) == _ziwei_structure(baseline), language
        assert _flying_structure(chart) == _flying_structure(baseline), language
        # 规范键和简体名不随语言变化
        assert [p["name_zh"] for p in chart["palaces"]] == [
            p["name_zh"] for p in baseline["palaces"]
        ]


@pytest.mark.parametrize("birth_id", BIRTHS)
@pytest.mark.parametrize("language", LANGUAGES)
def test_every_palace_resolves_in_every_language(server, birth_id, language):
    """每个宫都能在每种语言下分析，且结果就是命盘里同 key 的那个宫。

    按规范名匹配本地化宫名（7a24079 之前的逻辑）会在这里全部失败。
    """
    chart = call_json(server, "get_ziwei_chart", BIRTHS[birth_id], language)
    by_key = {palace["key"]: palace for palace in chart["palaces"]}
    for canonical in (
        "命宫",
        "兄弟宫",
        "夫妻宫",
        "子女宫",
        "财帛宫",
        "疾厄宫",
        "迁移宫",
        "交友宫",
        "官禄宫",
        "田宅宫",
        "福德宫",
        "父母宫",
    ):
        analysis = call_json(
            server, "analyze_ziwei_palace", BIRTHS[birth_id], language, palace_name=canonical
        )
        palace = by_key[analysis["palace_key"]]
        assert analysis["palace_name_zh"] == canonical
        assert analysis["palace_name"] == palace["name"]
        assert analysis["heavenly_stem"] == palace["heavenly_stem"]
        assert analysis["major_stars"] == palace["major_stars"]


@pytest.mark.parametrize("birth_id", BIRTHS)
def test_bazi_structure_is_language_independent(server, birth_id):
    baseline = call_json(server, "get_bazi_chart", BIRTHS[birth_id], "zh-CN")
    baseline_fortune = call_json(server, "get_bazi_fortune", BIRTHS[birth_id], "zh-CN")
    for language in LANGUAGES[1:]:
        chart = call_json(server, "get_bazi_chart", BIRTHS[birth_id], language)
        assert chart["pillars"] == baseline["pillars"]
        # relations 是机器校验字段：type 和汉字不随 language 变化
        assert chart["relations"] == baseline["relations"]
        fortune = call_json(server, "get_bazi_fortune", BIRTHS[birth_id], language)
        assert fortune["relations_with_natal"] == baseline_fortune["relations_with_natal"]
        assert [d["gan_zhi"] for d in fortune["da_yun_list"]] == [
            d["gan_zhi"] for d in baseline_fortune["da_yun_list"]
        ]


# ----------------------------------------------------------------------------
# query_year：periods 连续覆盖整个公历年
# ----------------------------------------------------------------------------


@pytest.mark.parametrize("tool", ["get_ziwei_fortune", "get_bazi_fortune"])
@pytest.mark.parametrize("language", LANGUAGES)
def test_query_year_periods_cover_the_whole_year(server, tool, language):
    birth = BIRTHS["solar_regular"]
    args = {**birth, "language": language, "format": "json", "query_year": 2026}
    result = json.loads(call_tool(server, tool, args))

    periods = result["periods"]
    assert periods[0]["valid_from"] == "2026-01-01"
    assert periods[-1]["valid_until_exclusive"] == "2027-01-01"
    for previous, current in zip(periods, periods[1:]):
        assert previous["valid_until_exclusive"] == current["valid_from"]
    for period in periods:
        start = datetime.strptime(period["valid_from"], "%Y-%m-%d")
        end = datetime.strptime(period["valid_until_exclusive"], "%Y-%m-%d")
        assert end - start >= timedelta(days=1)
        if tool == "get_bazi_fortune":
            assert isinstance(period["relations_with_natal"], list)
