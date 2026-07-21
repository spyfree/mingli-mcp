# Apify Chinese Astrology MCP Guide

Mingli MCP provides Zi Wei Dou Shu (紫微斗数 / Purple Star Astrology) and Bazi
(八字 / Four Pillars of Destiny) calculations through a hosted Streamable HTTP
MCP endpoint. Use it from an AI client without installing Python or keeping a
local server running.

## Endpoint and authentication

- Endpoint: `https://spyfree--mingli-mcp.apify.actor/mcp`
- Method: `POST`
- Authentication: Apify API token in the `Authorization` header
- Transport: Streamable HTTP MCP

Create or copy a token in the Apify Console, then keep it in your client or
secret manager. Do not commit a real token to Git.

## MCP client configuration

Many remote-MCP clients accept a configuration shaped like this:

```json
{
  "mcpServers": {
    "mingli": {
      "url": "https://spyfree--mingli-mcp.apify.actor/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_APIFY_TOKEN"
      }
    }
  }
}
```

The exact file name and header syntax vary by client. If a client cannot send
custom headers, use its documented secret or remote-MCP authentication flow.

## Verify the connection with curl

Set your token locally:

```bash
export APIFY_TOKEN="your-token"
```

List available tools. Discovery requests are not charged by this Actor:

```bash
curl --request POST \
  --url https://spyfree--mingli-mcp.apify.actor/mcp \
  --header "Authorization: Bearer $APIFY_TOKEN" \
  --header "Content-Type: application/json" \
  --header "Accept: application/json, text/event-stream" \
  --data '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'
```

Call the lightweight system-listing tool. Unlike `tools/list`, this is a
successful `tools/call` and therefore creates one billable `tool-call` event:

```bash
curl --request POST \
  --url https://spyfree--mingli-mcp.apify.actor/mcp \
  --header "Authorization: Bearer $APIFY_TOKEN" \
  --header "Content-Type: application/json" \
  --header "Accept: application/json, text/event-stream" \
  --data '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "list_fortune_systems",
      "arguments": {}
    }
  }'
```

Generate a Bazi / Four Pillars chart:

```bash
curl --request POST \
  --url https://spyfree--mingli-mcp.apify.actor/mcp \
  --header "Authorization: Bearer $APIFY_TOKEN" \
  --header "Content-Type: application/json" \
  --header "Accept: application/json, text/event-stream" \
  --data '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "get_bazi_chart",
      "arguments": {
        "date": "1992-08-16",
        "time_index": 4,
        "gender": "女",
        "calendar": "solar",
        "format": "json"
      }
    }
  }'
```

Generate a Zi Wei Dou Shu birth chart using `en-US` palace and star terminology:

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "get_ziwei_chart",
    "arguments": {
      "date": "1990-01-01",
      "time_index": 6,
      "gender": "男",
      "calendar": "solar",
      "language": "en-US",
      "format": "markdown"
    }
  }
}
```

### Four more schema-valid tool calls

Each object below is the `params` value for a `tools/call` JSON-RPC request. A
successful call creates one billable `tool-call` event.

Zi Wei fortune cycles:

```json
{
  "name": "get_ziwei_fortune",
  "arguments": {
    "birth_date": "1990-01-01",
    "time_index": 6,
    "gender": "男",
    "calendar": "solar",
    "query_date": "2027-03-01",
    "language": "en-US",
    "format": "json"
  }
}
```

Zi Wei palace analysis:

```json
{
  "name": "analyze_ziwei_palace",
  "arguments": {
    "birth_date": "1990-01-01",
    "time_index": 6,
    "gender": "男",
    "palace_name": "财帛宫",
    "calendar": "solar",
    "language": "zh-CN",
    "format": "markdown"
  }
}
```

Bazi simplified 10-year age period and annual stem/branch:

```json
{
  "name": "get_bazi_fortune",
  "arguments": {
    "birth_date": "1992-08-16",
    "time_index": 4,
    "gender": "女",
    "calendar": "solar",
    "query_date": "2027-03-01",
    "format": "json"
  }
}
```

Bazi five-element analysis:

```json
{
  "name": "analyze_bazi_element",
  "arguments": {
    "birth_date": "1992-08-16",
    "time_index": 4,
    "gender": "女",
    "calendar": "solar",
    "format": "json"
  }
}
```

### Abridged real responses

Tool results use MCP `content`. When JSON format is requested,
`result.content[0].text` contains a JSON string. These examples are shortened
from real local calls using the inputs above.

Zi Wei Dou Shu chart:

```json
{
  "system": "紫微斗数",
  "basic_info": {
    "阳历日期": "1990-01-01",
    "四柱": "庚午年己丑月乙亥日 壬午时",
    "时辰": "午时"
  },
  "palaces": [
    {
      "name": "Soul",
      "heavenly_stem": "Gui",
      "earthly_branch": "Wei",
      "major_stars": [
        { "name": "Tiantong", "brightness": "Prosperous" },
        { "name": "Jumen", "brightness": "Neutral" }
      ]
    }
  ]
}
```

Bazi chart:

```json
{
  "solar_date": "1992-08-16",
  "lunar_date": "一九九二年七月十八",
  "eight_char": "壬申 戊申 甲子 戊辰",
  "day_master": "甲",
  "wu_xing": {
    "scores": { "金": 2, "木": 1, "水": 2, "火": 0, "土": 3 }
  }
}
```

## Available tools

| Tool | Purpose |
| --- | --- |
| `get_ziwei_chart` | Generate a Zi Wei Dou Shu chart with 12 palaces and stars |
| `get_ziwei_fortune` | Calculate decadal, yearly, monthly, daily, and hourly periods |
| `analyze_ziwei_palace` | Analyze the star configuration of a selected palace |
| `get_bazi_chart` | Generate Four Pillars, Ten Gods, hidden stems, and five elements |
| `get_bazi_fortune` | Return a simplified 10-year age period and annual stem/branch |
| `analyze_bazi_element` | Analyze five-element strength, balance, and missing elements |
| `list_fortune_systems` | List the systems available on the server |

Zi Wei Dou Shu palace and star terminology supports `zh-CN`, `zh-TW`, `en-US`,
`ja-JP`, `ko-KR`, and `vi-VN`; some basic-info keys remain Chinese. Bazi
currently accepts the same language parameter for API consistency, but its
underlying chart labels are primarily Chinese. Its fortune response uses a
simplified 10-year age-period marker rather than a full Da Yun stem/branch
sequence.

## Prompt examples

Use concrete, structured birth data for the most reliable tool selection:

- `Create a Zi Wei Dou Shu chart for 1990-01-01, 午时 (time_index 6), male, solar calendar, using en-US palace and star terms.`
- `排一个 1992-08-16 辰时（time_index 4）出生、女、阳历的八字，返回 JSON。`
- `分析 1988-06-12 子时男命八字的五行强弱，并列出缺失五行。`
- `For this Zi Wei chart, analyze the 财帛 palace and summarize its major and minor stars.`
- `Calculate the Zi Wei fortune periods for 2027-03-01; separate decadal, yearly, monthly, daily, and hourly results.`

The `time_index` value is a two-hour traditional Chinese time branch: `0` is
early 子时, `1` is 丑时, through `11` for 亥时; `12` is late 子时.

## Pricing and runtime behavior

This Actor uses Apify Standby mode and a fixed 256 MB memory limit to minimize
idle infrastructure cost. The Store pricing panel is the source of truth for
the current price.

- `tools/list`, initialization, and other discovery requests do not create the
  Actor's paid event.
- Each successful `tools/call` creates one `tool-call` event.
- A failed tool call is not charged by the Actor.
- If Apify cannot confirm the charge, the server returns an MCP error instead
  of an unbilled result.

## Privacy and limitations

Birth dates, times, and gender are personal data. Send only data you are
authorized to process, avoid names or unrelated identifiers, and review Apify's
privacy and retention settings before production use. The server is stateless
at the application layer and does not write chart results to its own database,
but the hosting platform can retain operational request and run metadata.

The calculations are intended for cultural study, software experimentation,
and entertainment. They do not make factual predictions and must not replace
medical, legal, financial, employment, or other professional decisions.

## Self-hosted alternative

The project is open source. To avoid hosted usage charges, run it locally:

```bash
uvx mingli-mcp
```

See the [quick start guide](QUICK_START.md) for Cursor, Claude Code, Docker, and
source-install options.
