"""Checks for public package metadata and tool discovery schemas."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_json(name: str):
    with (ROOT / name).open(encoding="utf-8") as file:
        return json.load(file)


def test_all_birth_chart_tools_expose_solar_time_inputs():
    """MCP clients must discover the advertised true-solar-time options."""
    from mingli_mcp.mcp_server.tools.definitions import get_all_tool_definitions

    tools = {tool["name"]: tool for tool in get_all_tool_definitions()}
    birth_tools = {
        "get_ziwei_chart",
        "get_ziwei_fortune",
        "analyze_ziwei_palace",
        "get_bazi_chart",
        "get_bazi_fortune",
        "analyze_bazi_element",
    }

    for name in birth_tools:
        properties = tools[name]["inputSchema"]["properties"]
        assert {"longitude", "use_solar_time", "birth_hour", "birth_minute"} <= properties.keys()


def test_distribution_metadata_versions_match_runtime():
    """Public package manifests should not advertise stale server versions."""
    import mingli_mcp

    package = _load_json("package.json")
    server = _load_json("server.json")

    assert package["version"] == mingli_mcp.__version__
    assert server["version"] == mingli_mcp.__version__
