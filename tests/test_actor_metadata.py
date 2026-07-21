"""Checks for the public Apify Actor definition and interactive API examples."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ACTOR_DIR = ROOT / ".actor"


def _load_json(name: str):
    with (ACTOR_DIR / name).open(encoding="utf-8") as file:
        return json.load(file)


def test_actor_definition_links_store_schemas_and_caps_memory():
    """The deployed Actor should expose its real Standby surface at minimum memory."""
    actor = _load_json("actor.json")

    assert actor["usesStandbyMode"] is True
    assert actor["webServerMcpPath"] == "/mcp"
    assert actor["minMemoryMbytes"] == actor["maxMemoryMbytes"] == 256
    assert actor["input"] == "./input_schema.json"
    assert actor["readme"] == "./README.md"
    assert actor["output"] == "./output_schema.json"
    assert actor["webServerSchema"] == "./web_server_openapi.json"


def test_standby_output_schema_does_not_claim_persisted_results():
    """MCP responses are live HTTP output, not fictional dataset records."""
    output = _load_json("output_schema.json")

    assert output["actorOutputSchemaVersion"] == 1
    assert output["properties"] == {}
    assert "/mcp" in output["description"]


def test_store_readme_is_long_form_and_does_not_add_a_second_h1():
    """Apify supplies the page H1, while the Store copy still needs useful depth."""
    readme = (ACTOR_DIR / "README.md").read_text(encoding="utf-8")

    assert not any(line.startswith("# ") for line in readme.splitlines())
    assert len(readme.split()) >= 300
    assert "Zi Wei Dou Shu" in readme
    assert "BaZi" in readme
    assert "## Pricing" in readme


def test_openapi_schema_documents_mcp_examples_relative_to_standby_base():
    """The Store Standby tab should expose valid JSON-RPC examples."""
    schema = _load_json("web_server_openapi.json")
    examples = schema["paths"]["/"]["post"]["requestBody"]["content"][
        "application/json"
    ]["examples"]

    assert schema["openapi"] == "3.0.3"
    assert set(schema["paths"]) == {"/"}
    assert "/mcp Standby base URL" in schema["paths"]["/"]["post"]["description"]
    assert examples["listTools"]["value"]["method"] == "tools/list"
    assert examples["baziChart"]["value"]["params"]["name"] == "get_bazi_chart"
    assert "YOUR_APIFY_TOKEN" not in json.dumps(schema)
    assert '"type": "null"' not in json.dumps(schema)


def test_all_birth_chart_tools_expose_solar_time_inputs():
    """MCP clients must be able to discover the advertised true-solar-time options."""
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
