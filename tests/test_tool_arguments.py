"""
参数别名（P0-2）与工具错误结果（P0-3）

date / birth_date 互为别名；参数和业务错误返回 result.isError=true 与可照做的纠正提示。
"""

import json

import pytest

from mingli_mcp.core.exceptions import ValidationError
from mingli_mcp.mcp_server.server import MingliMCPServer
from mingli_mcp.mcp_server.tools.arguments import normalize_birth_date
from mingli_mcp.mcp_server.tools.definitions import get_all_tool_definitions

BIRTH_TOOLS = [
    "get_ziwei_chart",
    "get_ziwei_fortune",
    "analyze_ziwei_palace",
    "get_bazi_chart",
    "get_bazi_fortune",
    "analyze_bazi_element",
]


@pytest.fixture(scope="module")
def server():
    return MingliMCPServer()


def call(server, name, arguments):
    return server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        }
    )


def base_args(tool, **date):
    args = {"time_index": 2, "gender": "女", "format": "json", **date}
    if tool == "analyze_ziwei_palace":
        args["palace_name"] = "命宫"
    return args


def test_normalize_birth_date():
    assert normalize_birth_date({"date": "2000-08-16"}) == {"birth_date": "2000-08-16"}
    assert normalize_birth_date({"birth_date": "2000-08-16", "date": "2000-08-16"}) == {
        "birth_date": "2000-08-16"
    }
    with pytest.raises(ValidationError, match="取值不同"):
        normalize_birth_date({"birth_date": "2000-08-16", "date": "2000-08-17"})


@pytest.mark.parametrize("tool", BIRTH_TOOLS)
def test_every_tool_accepts_both_names_with_identical_output(server, tool):
    via_date = call(server, tool, base_args(tool, date="2000-08-16"))
    via_birth_date = call(server, tool, base_args(tool, birth_date="2000-08-16"))
    both = call(server, tool, base_args(tool, date="2000-08-16", birth_date="2000-08-16"))

    def text(response):
        assert not response["result"].get("isError"), response
        data = json.loads(response["result"]["content"][0]["text"])
        data.pop("metadata", None)
        return data

    assert text(via_date) == text(via_birth_date) == text(both)


@pytest.mark.parametrize("tool", BIRTH_TOOLS)
def test_conflicting_names_are_a_tool_error(server, tool):
    response = call(server, tool, base_args(tool, date="2000-08-16", birth_date="2001-01-01"))
    assert response["result"]["isError"] is True
    assert "birth_date" in response["result"]["content"][0]["text"]


def test_schema_publishes_birth_date_as_canonical():
    for definition in get_all_tool_definitions():
        if definition["name"] not in BIRTH_TOOLS:
            continue
        schema = definition["inputSchema"]
        assert "birth_date" in schema["required"]
        assert "date" not in schema["required"]
        assert "已弃用，仍接受" in schema["properties"]["date"]["description"]


@pytest.mark.parametrize(
    "arguments,hint",
    [
        ({"birth_date": "2000/08/16"}, "YYYY-MM-DD"),
        ({"birth_date": "1800-01-01"}, "1900-01-01"),
        ({"birth_date": "2000-08-16", "palace_name": "桃花宫"}, "可用值：命宫"),
        ({"birth_date": "2000-08-16", "time_index": 13}, "0-12"),
    ],
)
def test_parameter_errors_are_tool_results_with_corrective_hints(server, arguments, hint):
    args = {"time_index": 2, "gender": "女", "palace_name": "命宫", **arguments}
    response = call(server, "analyze_ziwei_palace", args)
    assert "error" not in response
    assert response["result"]["isError"] is True
    assert hint in response["result"]["content"][0]["text"]


def test_invalid_palace_hint_names_the_canonical_replacements(server):
    args = {"birth_date": "2000-08-16", "time_index": 2, "gender": "女", "palace_name": "桃花宫"}
    text = call(server, "analyze_ziwei_palace", args)["result"]["content"][0]["text"]
    assert "『桃花宫』" in text
    assert "事业→官禄宫" in text


@pytest.mark.parametrize(
    "alias,key",
    [
        ("事业", "careerPalace"),
        ("事业宫", "careerPalace"),
        ("交友", "friendsPalace"),
        ("朋友", "friendsPalace"),
        ("健康", "healthPalace"),
        ("财运", "wealthPalace"),
        ("婚姻", "spousePalace"),
        ("配偶", "spousePalace"),
        ("官祿", "careerPalace"),  # zh-TW 显示名
        ("Quan Lộc", "careerPalace"),  # vi-VN 显示名
        ("thiên di", "surfacePalace"),
        ("관록", "careerPalace"),
        ("career", "careerPalace"),
    ],
)
def test_palace_aliases(server, alias, key):
    args = {
        "birth_date": "2000-08-16",
        "time_index": 2,
        "gender": "女",
        "palace_name": alias,
        "format": "json",
    }
    response = call(server, "analyze_ziwei_palace", args)
    assert json.loads(response["result"]["content"][0]["text"])["palace_key"] == key


def test_unknown_tool_is_still_a_protocol_error(server):
    assert call(server, "no_such_tool", {})["error"]["code"] == -32602
