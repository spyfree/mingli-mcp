## Zi Wei Dou Shu and BaZi Chinese astrology MCP

Generate deterministic Chinese birth-chart data for AI agents through a hosted
Streamable HTTP MCP server. Mingli MCP combines Zi Wei Dou Shu (紫微斗数 / Purple
Star Astrology) and BaZi (八字 / Four Pillars of Destiny) in one endpoint. It is
designed for Claude, Cursor, VS Code, custom agents, and applications that need
structured calculations instead of an LLM inventing a chart from prose.

The service calculates 12-palace Zi Wei charts and stars, fortune periods,
palace details, Four Pillars, Ten Gods, hidden stems, and five-element balance.
Results can be returned as JSON or readable Markdown.

## What can this Chinese astrology MCP do?

| Tool | Result |
| --- | --- |
| `get_ziwei_chart` | Zi Wei Dou Shu chart with 12 palaces and star placements |
| `get_ziwei_fortune` | Decadal, yearly, monthly, daily, and hourly periods |
| `analyze_ziwei_palace` | Focused analysis of one palace and its stars |
| `get_bazi_chart` | Four Pillars, Ten Gods, hidden stems, and five elements |
| `get_bazi_fortune` | Simplified 10-year age-period marker and annual stem/branch |
| `analyze_bazi_element` | Element strength, balance, and missing elements |
| `list_fortune_systems` | Discover the implemented Zi Wei and BaZi systems |

Zi Wei palace and star terminology supports six locale codes: Simplified and
Traditional Chinese, English, Japanese, Korean, and Vietnamese. Some basic-info
keys remain Chinese. BaZi chart labels are currently primarily Chinese. Its
fortune tool reports a simplified 10-year age-period marker, not a full Da Yun
stem/branch sequence.

## Connect in 60 seconds

Use the Standby endpoint with your Apify API token:

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

Every client stores remote MCP configuration differently. Keep the token in the
client's secret storage and never commit it to source control.

Verify tool discovery without creating a paid event:

```bash
curl --request POST \
  --url https://spyfree--mingli-mcp.apify.actor/mcp \
  --header "Authorization: Bearer $APIFY_TOKEN" \
  --header "Content-Type: application/json" \
  --header "Accept: application/json, text/event-stream" \
  --data '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

## BaZi Four Pillars API example

This successful `tools/call` creates one billable event:

```json
{
  "jsonrpc": "2.0",
  "id": 2,
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
}
```

Abridged real chart data:

```json
{
  "solar_date": "1992-08-16",
  "eight_char": "壬申 戊申 甲子 戊辰",
  "day_master": "甲",
  "wu_xing": {
    "scores": { "金": 2, "木": 1, "水": 2, "火": 0, "土": 3 }
  }
}
```

## Zi Wei Dou Shu API example

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "analyze_ziwei_palace",
    "arguments": {
      "birth_date": "1990-01-01",
      "time_index": 6,
      "gender": "男",
      "palace_name": "财帛宫",
      "calendar": "solar",
      "format": "markdown"
    }
  }
}
```

More copy-ready requests cover Zi Wei charts and fortune cycles, BaZi luck
cycles, five-element analysis, natural-language prompts, and real abridged
responses in the [complete Apify MCP guide](https://github.com/spyfree/mingli-mcp/blob/main/docs/APIFY_MCP_GUIDE.md).

## More tool call examples

Use each object as the `params` value of a `tools/call` request.

```json
{
  "name": "get_ziwei_chart",
  "arguments": {
    "date": "1990-01-01",
    "time_index": 6,
    "gender": "男",
    "calendar": "solar",
    "language": "en-US",
    "format": "json"
  }
}
```

```json
{
  "name": "get_ziwei_fortune",
  "arguments": {
    "birth_date": "1990-01-01",
    "time_index": 6,
    "gender": "男",
    "query_date": "2027-03-01",
    "format": "json"
  }
}
```

```json
{
  "name": "get_bazi_fortune",
  "arguments": {
    "birth_date": "1992-08-16",
    "time_index": 4,
    "gender": "女",
    "query_date": "2027-03-01",
    "format": "json"
  }
}
```

```json
{
  "name": "analyze_bazi_element",
  "arguments": {
    "birth_date": "1992-08-16",
    "time_index": 4,
    "gender": "女",
    "format": "json"
  }
}
```

## Input conventions and true solar time

`time_index` represents the traditional two-hour branch: `0` is early 子时,
`1` is 丑时, through `11` for 亥时; `12` is late 子时. Solar and lunar calendar
inputs are supported. The birth-chart tools also expose optional longitude,
precise birth hour/minute, and `use_solar_time` fields for true-solar-time
correction.

## Pricing

The current dollar amount is always shown in the Store Pricing tab.

- MCP initialization, `tools/list`, and other discovery requests do not create
  this Actor's paid event.
- Each successful `tools/call` creates one `tool-call` event.
- Invalid or failed tool calls are not charged by this Actor.
- If Apify cannot confirm the charge, the result is withheld and an MCP error is
  returned.

The Actor runs in Standby mode with a fixed 256 MB memory cap to keep hosting
costs low.

## Privacy, limitations, and responsible use

Birth dates, times, locations, and gender can be personal data. Send only data
you are authorized to process, avoid names and unrelated identifiers, and review
Apify's privacy and retention controls before production use. The application is
stateless and does not write charts to its own database, although the hosting
platform can retain operational metadata.

These calculations are for cultural study, software experimentation, and
entertainment. They do not make guaranteed predictions and must not replace
medical, legal, financial, employment, or other professional decisions.

For source code, self-hosting, and support, visit the
[GitHub repository](https://github.com/spyfree/mingli-mcp) or open a
[GitHub issue](https://github.com/spyfree/mingli-mcp/issues).
