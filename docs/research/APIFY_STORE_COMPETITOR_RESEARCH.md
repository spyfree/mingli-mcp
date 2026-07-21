# Apify Store competitor research: Mingli MCP

Checked: **2026-07-21**

## Executive summary

The closest public Apify Store competition is small and very new. Three direct
competitors were found: a Chinese BaZi chart API, a Korean Saju MCP server, and a
Korean Saju calculator. Their public Actor records show only 1–2 total users and
4–12 total runs each at the time of checking, so there is not yet an established
category leader ([BaZi Chart API record](https://api.apify.com/v2/acts/kelvin.kwong~bazi-chart-api),
[Saju MCP record](https://api.apify.com/v2/acts/motivated_picnic~saju-mcp),
[Korean Saju Calculator record](https://api.apify.com/v2/acts/minji_k~manseryeok-calculator)).

No relevant Zi Wei Dou Shu / 紫微斗数 Actor surfaced in the reviewed public Store
search results. That is a search observation, not proof that none exists: Store
results can change and Apify states that ranking is quality-driven and Console
search is personalized ([Store search documentation](https://docs.apify.com/console/store),
[quality-score documentation](https://docs.apify.com/actors/publishing/quality-score)).

The strongest positioning is therefore not “another BaZi calculator.” It is:

> **A Chinese astrology MCP combining Zi Wei Dou Shu and BaZi in one API, with
> charts, fortune cycles, palace analysis, and five-element analysis. Zi Wei
> palace/star terminology supports six locale codes; BaZi labels are primarily
> Chinese.**

This is materially broader than the three direct competitors' public positioning:
one focuses on Chinese BaZi charts, while the other two focus on Korean Saju
([BaZi Chart API Store page](https://apify.com/kelvin.kwong/bazi-chart-api),
[Saju MCP Store page](https://apify.com/motivated_picnic/saju-mcp),
[Korean Saju Calculator Store page](https://apify.com/minji_k/manseryeok-calculator)).

## Method

Only primary sources were used: Apify's public Store API, Actor detail/API pages,
and official Apify documentation. The public Store API was checked for these
queries: [zi wei](https://api.apify.com/v2/store?search=zi%20wei&limit=20),
[ziwei](https://api.apify.com/v2/store?search=ziwei&limit=20),
[紫微斗数](https://api.apify.com/v2/store?search=%E7%B4%AB%E5%BE%AE%E6%96%97%E6%95%B0&limit=20),
[bazi](https://api.apify.com/v2/store?search=bazi&limit=20),
[八字](https://api.apify.com/v2/store?search=%E5%85%AB%E5%AD%97&limit=20),
[four pillars](https://api.apify.com/v2/store?search=four%20pillars&limit=20),
[chinese astrology](https://api.apify.com/v2/store?search=chinese%20astrology&limit=20),
[chinese horoscope](https://api.apify.com/v2/store?search=chinese%20horoscope&limit=20),
[birth chart](https://api.apify.com/v2/store?search=birth%20chart&limit=20),
[astrology](https://api.apify.com/v2/store?search=astrology&limit=20),
[horoscope](https://api.apify.com/v2/store?search=horoscope&limit=20),
[fortune telling](https://api.apify.com/v2/store?search=fortune%20telling&limit=20),
and [tarot](https://api.apify.com/v2/store?search=tarot&limit=20).

For each query, the first 20 relevance-ranked results were reviewed. Direct Actor
records were then queried separately because a newly public Actor can have a live
detail page before it is prominent in relevance search. Public usage figures are
point-in-time signals, not audited revenue or demand figures.

## Direct competitors

| Actor | Positioning | Public pricing | Usage signal on 2026-07-21 | Competitive implication |
|---|---|---:|---:|---|
| [BaZi Chart API (八字排盤)](https://apify.com/kelvin.kwong/bazi-chart-api) | Chinese Four Pillars chart JSON: stems/branches, hidden stems, Na Yin, Ten Gods, five elements, luck cycles, current-year pillar; Traditional Chinese, Simplified Chinese, and English; Standby REST API | **$0.01 per generated chart** | 1 user, 9 runs, 0 monthly active users | Closest Chinese BaZi API competitor. Strong structured-output example, but no Zi Wei positioning and not presented as a dedicated multi-tool MCP server. |
| [Saju MCP Server](https://apify.com/motivated_picnic/saju-mcp) | Streamable HTTP MCP for Korean Saju/BaZi; calculate, interpret, compatibility, and daily fortune; 10 languages; returns human-readable text and `structuredContent` | **$0.05 per tool call** | 1 user, 4 runs, 0 monthly active users | Closest protocol-level competitor. Its strongest differentiators are compatibility, daily fortune, multilingual interpretation, and explicit structured MCP results. |
| [Korean Saju (Four Pillars) Calculator](https://apify.com/minji_k/manseryeok-calculator) | Deterministic Korean Saju chart using astronomical calculations; true solar time, five elements, Ten Gods, sinsal, luck cycles; structured dataset output | **$0.03 per successful calculation** | 2 users, 12 runs, 1 monthly active user | Strong correctness narrative and explicit true-solar-time support, but focused on Korean terminology and a run/dataset workflow rather than a combined Chinese astrology MCP. |

The prices, event definitions, categories, and usage figures above come from the
Actors' public API records: [BaZi Chart API](https://api.apify.com/v2/acts/kelvin.kwong~bazi-chart-api),
[Saju MCP](https://api.apify.com/v2/acts/motivated_picnic~saju-mcp), and
[Korean Saju Calculator](https://api.apify.com/v2/acts/minji_k~manseryeok-calculator).

### What the direct competitors do well

- **Concrete, deterministic output:** both calculator-style competitors show
  substantial JSON examples instead of only promising a reading
  ([BaZi example](https://apify.com/kelvin.kwong/bazi-chart-api),
  [Korean Saju example](https://apify.com/minji_k/manseryeok-calculator)).
- **Accuracy conventions:** the BaZi Actor documents lunar calendars, leap months,
  timezone handling, Zi-hour conventions, and limitations; the Korean calculator
  emphasizes astronomical calculations and true solar time
  ([BaZi conventions](https://apify.com/kelvin.kwong/bazi-chart-api),
  [Korean calculator methodology](https://apify.com/minji_k/manseryeok-calculator)).
- **Agent-ready semantics:** the Saju MCP explicitly documents four tool names,
  example inputs, supported clients, and `structuredContent`
  ([Saju MCP documentation](https://apify.com/motivated_picnic/saju-mcp)).
- **Transparent unit pricing:** all three describe the billable event in user terms
  such as chart, calculation, or tool call; their public API records expose the
  exact event price and description
  ([BaZi pricing record](https://api.apify.com/v2/acts/kelvin.kwong~bazi-chart-api),
  [Saju pricing record](https://api.apify.com/v2/acts/motivated_picnic~saju-mcp),
  [Korean calculator pricing record](https://api.apify.com/v2/acts/minji_k~manseryeok-calculator)).

## Adjacent competitors

These Actors compete for broader astrology/fortune-telling discovery, but not for
the same Chinese metaphysics workflow.

| Actor | Adjacent category | Public pricing and usage signal on 2026-07-21 |
|---|---|---|
| [Daily Horoscope API](https://apify.com/akash9078/daily-horoscope-api) | Western zodiac daily predictions | $0.001 primary horoscope item in its current pricing record; 15 total users, 299 runs, 3 monthly active users ([API record](https://api.apify.com/v2/acts/akash9078~daily-horoscope-api)). |
| [Horoscope Zodiac Scraper](https://apify.com/hanamira/zodiac-oracle) | Daily/weekly/monthly/yearly horoscope content for all 12 signs | $0.004 dataset item; 14 users, 228 runs, 1 monthly active user ([API record](https://api.apify.com/v2/acts/hanamira~zodiac-oracle)). |
| [Horoscope API](https://apify.com/vivid_astronaut/horoscope) | Generic horoscope API wrapper | $0.005 dataset item; 2 users, 177 runs, 0 monthly active users ([API record](https://api.apify.com/v2/acts/vivid_astronaut~horoscope)). |
| [AI Palmistry Agent](https://apify.com/saadithya/ai-palmistry-analyzer) | Image-based symbolic palm reading | $0.05 per palm reading; 39 users, 260 runs, 0 monthly active users ([API record](https://api.apify.com/v2/acts/saadithya~ai-palmistry-analyzer)). |
| [Tarot API Scraper](https://apify.com/velvety_bedbug/tarot-api-scraper) | Tarot card data and random draws | $0.003 per result item plus its listed Actor-start event; 2 users, 18 runs, 1 monthly active user ([API record](https://api.apify.com/v2/acts/velvety_bedbug~tarot-api-scraper)). |

The adjacent group shows more accumulated usage than the direct BaZi/Saju group,
but still modest adoption. The strongest usage signal in this reviewed set belongs
to the palmistry Actor at 39 total users; this is an adjacent entertainment Agent,
not a birth-chart or MCP substitute
([AI Palmistry API record](https://api.apify.com/v2/acts/saadithya~ai-palmistry-analyzer)).

## Whitespace and recommended positioning

### Defensible whitespace

1. **Zi Wei Dou Shu is the lead differentiator.** None of the relevant reviewed
   Store results positions itself as a Zi Wei Dou Shu / 紫微斗数 service. Lead with
   Zi Wei in the visible title while retaining “BaZi,” “Four Pillars,” and
   “Chinese astrology” for adjacent discovery.
2. **One MCP, two systems.** The direct competitors each center on BaZi/Saju. Mingli
   already exposes Zi Wei charts and fortune/palace tools alongside BaZi chart,
   fortune, and element tools ([project README](../../README.md)).
3. **Chinese-first semantics with global access.** Zi Wei palace and star terms
   support six locale codes, while BaZi labels remain primarily Chinese. Combined
   with JSON/Markdown formats, this can bridge Chinese metaphysics terms and
   international developer integration ([project README](../../README.md)).
4. **Tool-level workflow, not a single calculator.** Market the seven explicit
   tools and what an Agent can do across multiple turns, rather than describing the
   product only as a “fortune-telling server” ([project README](../../README.md)).
5. **Transparent methodology and limits.** Match competitors by documenting time
   boundaries, calendar conventions, true-solar-time behavior, supported date
   range, deterministic versus interpretive fields, and known limitations. Avoid
   marketing the placeholder Western astrology interface as an implemented feature
   because the README marks it as reserved/not implemented ([project README](../../README.md)).

### Proposed display information

Apify recommends a 40–50 character Actor name, a 40–50 character SEO name, an
approximately 300-character Store description, and a 145–155 character SEO
description ([naming guidance](https://docs.apify.com/academy/actor-marketing-playbook/actor-basics/name-your-actor),
[description guidance](https://docs.apify.com/academy/actor-marketing-playbook/actor-basics/actor-description)).

**Actor name (43 characters)**

> Zi Wei Dou Shu & BaZi Chinese Astrology MCP

**SEO name (44 characters)**

> Chinese Astrology MCP: Zi Wei Dou Shu & BaZi

**Actor description**

> Chinese astrology MCP server and API for Zi Wei Dou Shu (紫微斗数) and BaZi (八字 / Four Pillars). Generate 12-palace star charts, fortune cycles, palace readings, Four Pillars, Ten Gods, and five-element analysis for AI agents.

**SEO description (154 characters)**

> Generate Zi Wei Dou Shu and BaZi birth charts, Four Pillars, fortune cycles, palace readings, and five-element analysis through MCP or API for AI agents.

**Recommended categories, in priority order**

1. `MCP_SERVERS`
2. `AI`
3. `DEVELOPER_TOOLS`

If `MCP_SERVERS` is not offered in the publication form, use `AGENTS` as the
fallback. The recommendation follows the product's primary delivery mechanism;
direct competitors currently use combinations of AI, Agents, Developer Tools,
Automation, and Other in their public Actor records
([BaZi record](https://api.apify.com/v2/acts/kelvin.kwong~bazi-chart-api),
[Saju MCP record](https://api.apify.com/v2/acts/motivated_picnic~saju-mcp),
[Korean calculator record](https://api.apify.com/v2/acts/minji_k~manseryeok-calculator)).

### Keyword map

Use keywords naturally; do not repeat every variant in every section. Apify advises
putting the most relevant keyword in the first paragraph and using search-aligned
H2/H3 headings without sacrificing readability
([official SEO guide](https://docs.apify.com/academy/actor-marketing-playbook/promote-your-actor/seo)).

| Priority | Keywords | Where to use |
|---|---|---|
| Primary | `Zi Wei Dou Shu`, `紫微斗数`, `BaZi`, `八字`, `Chinese astrology MCP` | Title, first paragraph, one H2, SEO description |
| High intent | `Four Pillars API`, `Chinese birth chart API`, `BaZi calculator`, `Zi Wei Dou Shu API`, `astrology MCP server` | Feature and API headings, examples, FAQ |
| Feature | `12 palaces`, `Four Pillars of Destiny`, `Ten Gods`, `five elements`, `fortune periods`, `annual stem/branch`, `true solar time` | Capability table and output examples; describe the current BaZi 10-year marker as simplified rather than a full Da Yun sequence |
| Integration | `Claude MCP`, `Cursor MCP`, `VS Code MCP`, `Streamable HTTP MCP`, `AI agent tool` | Quickstart and integration examples |
| Multilingual | `Chinese astrology API English`, `中文八字 API`, `紫微斗数 API`, `Japanese`, `Korean`, `Vietnamese` | Language section; use only supported languages |
| Long tail | `generate Zi Wei Dou Shu chart`, `calculate BaZi Four Pillars`, `Chinese astrology API for AI agents` | FAQ headings and example prompts |

Do not optimize around generic `astrology`, `horoscope`, `fortune telling`, or
`tarot` alone. The reviewed search results for those terms are dominated by Western
zodiac, palmistry, tarot, or unrelated listings
([astrology results](https://api.apify.com/v2/store?search=astrology&limit=20),
[horoscope results](https://api.apify.com/v2/store?search=horoscope&limit=20),
[fortune-telling results](https://api.apify.com/v2/store?search=fortune%20telling&limit=20),
[tarot results](https://api.apify.com/v2/store?search=tarot&limit=20)).

## Store README and examples plan

Apify treats an Actor README as its Store landing page and recommends at least 300
words, a clear intro, feature/use-case sections, input and output examples, pricing,
support, and keyword-aware H2/H3 headings; the page already has an H1, so the
README should not add another H1
([official README guide](https://docs.apify.com/academy/actor-marketing-playbook/actor-basics/how-to-create-an-actor-readme)).

### Recommended structure

1. **English-first opening (80–120 words)**
   - Say “Zi Wei Dou Shu and BaZi Chinese astrology MCP” in the first sentence.
   - State the concrete result: charts and deterministic analysis data for AI
     agents and applications.
   - Follow with a short Chinese summary rather than making the whole landing page
     Chinese-only.
2. **What this Chinese astrology MCP can do**
   - A compact seven-tool table: tool name, system, result, typical Agent prompt.
   - Separate deterministic chart computation from interpretive/advisory output.
3. **Why use Mingli instead of a generic LLM**
   - Explain calendar/chart computation, consistent tool schemas, multilingual
     terminology, JSON mode, and true-solar-time option.
   - Document methodology and limitations rather than making unverifiable accuracy
     superlatives.
4. **60-second MCP quickstart**
   - Apify Standby URL with bearer-token placeholder.
   - Claude Desktop / Claude Code, Cursor or VS Code configuration.
   - `tools/list` verification request.
5. **Zi Wei Dou Shu API examples**
   - Full chart: birth date, time index, gender, calendar, language.
   - Fortune cycle query.
   - Palace analysis query.
   - Include one abridged real response.
6. **BaZi / Four Pillars API examples**
   - BaZi chart request and abridged response.
   - Luck-cycle request.
   - Five-element analysis request.
7. **Example AI prompts**
   - “Generate a Zi Wei Dou Shu chart for ...”
   - “Calculate the BaZi Four Pillars and five-element balance for ...”
   - “Analyze the Career Palace in English ...”
   - “Compare the current annual cycle with the natal chart ...”
8. **Languages, conventions, and limitations**
   - Supported languages, calendars, Zi-hour/time-index convention, true solar
     time, date range, leap-month handling, and timezone/city assumptions.
9. **Pricing**
   - “Charged once per successful MCP tool call; discovery and failed calls are not
     charged.” Link to the Store Pricing tab for the current dollar amount so the
     README cannot become stale.
10. **Privacy, responsible-use disclaimer, and support**
    - Tell users what birth data is processed/stored.
    - Position readings as cultural/entertainment information, not medical,
      financial, legal, or guaranteed predictive advice.
    - Link GitHub issues and the public Apify Issues tab.
11. **FAQ with long-tail search questions**
    - “What is the difference between Zi Wei Dou Shu and BaZi?”
    - “Can an AI Agent calculate a Chinese birth chart through MCP?”
    - “Does the BaZi API support lunar dates and true solar time?”
    - “Which MCP clients can call this Actor?”

### Example quality requirements

- Use real tool names and schema-valid payloads from `tools/list`, not pseudocode.
- Show one compact input and one abridged output for both Zi Wei and BaZi.
- Include both a natural-language Agent prompt and the equivalent JSON tool input.
- Use placeholder tokens such as `$APIFY_TOKEN`; never paste a real token.
- Explain that a successful tool call is billable before the first paid example.
- Keep the main landing page focused on users; move local installation,
  contribution, package building, and internal architecture into a “Develop
  locally” section or separate developer document.
- Add a 60–90 second demo video after the textual quickstart. Apify's README guide
  says a video can improve search performance
  ([official README guide](https://docs.apify.com/academy/actor-marketing-playbook/actor-basics/how-to-create-an-actor-readme)).

## Does output schema matter for this Standby MCP Actor?

**Yes, but it is secondary to the MCP and web-server schemas.**

An Actor output schema describes data stored in datasets and key-value stores; it
also appears in the run API and helps users and Agents understand stored results.
Apify explicitly recommends defining an empty output schema even when an Actor
stores no run output, so successful completion is not mistaken for missing output
([output-schema documentation](https://docs.apify.com/actors/development/actor-definition/output-schema)).

This Actor's actual product response is the live Streamable HTTP `/mcp` exchange,
not a default dataset. Apify recognizes a Standby MCP server through
`usesStandbyMode` and `webServerMcpPath`, and MCP clients connect directly to that
path ([Actor definition reference](https://docs.apify.com/actors/development/actor-definition/actor-json),
[MCP deployment guide](https://docs.apify.com/sdk/python/docs/next/guides/mcp-servers)).
Therefore, a dataset-shaped output schema should **not** pretend that MCP tool
responses are stored Actor output.

Recommended implementation order:

1. Keep `webServerMcpPath: "/mcp"` and accurate MCP tool input schemas.
2. Add a `webServerSchema` OpenAPI file for `/health` and the documented HTTP
   surface where useful. Apify uses this schema to render an interactive Standby
   tab with endpoint and request/response documentation
   ([web-server-schema documentation](https://docs.apify.com/actors/development/actor-definition/web-server-schema)).
3. Add an honest empty output schema:

   ```json
   {
     "actorOutputSchemaVersion": 1,
     "title": "Mingli MCP Server output",
     "description": "This Standby Actor returns results through the /mcp endpoint and does not persist a default dataset.",
     "properties": {}
   }
   ```

4. If the Actor later adds task-style report generation and persists reports, then
   replace the empty schema with dataset/key-value-store links for those reports.
5. Consider returning MCP `structuredContent` alongside readable text. This is not
   an Apify output-schema replacement, but it would match the strongest direct MCP
   competitor's agent-consumption story
   ([Saju MCP Store page](https://apify.com/motivated_picnic/saju-mcp)).

## Implementation plan

### Phase 1 — Publication essentials

- Update Actor name, Store description, SEO name, SEO description, and categories
  with the proposed copy.
- Refactor the Store README to the English-first structure above while retaining a
  concise Chinese introduction and linking the existing detailed Chinese docs.
- Add valid Apify Standby MCP quickstart instructions and six real examples: three
  Zi Wei, three BaZi.
- Add pricing behavior, data/privacy notes, methodology/limitations, disclaimer,
  and support links.
- Ensure Display information, Sample input, Monetization, and Actor permissions use
  terminology consistent with the README. Apify includes text congruence,
  reliability, ease of use, pricing transparency, and trustworthiness in the Actor
  quality score, which correlates with Store and MCP `search-actors` visibility
  ([quality-score documentation](https://docs.apify.com/actors/publishing/quality-score)).

### Phase 2 — Machine-readable discovery

- Add a truthful empty output schema.
- Add/validate a `webServerSchema` for the Standby HTTP surface.
- Verify the MCP tool names, descriptions, argument constraints, and JSON-mode
  outputs are concise enough for Agents.
- Add MCP `structuredContent` if the current protocol layer only returns JSON as a
  text string.
- Add an English screenshot or short demo showing a real Agent request and tool
  result.

### Phase 3 — Publish and measure

- Publish, then verify the public card, Store README, Pricing tab, MCP endpoint, and
  all example payloads. Apify's publication guide says the public Store search is
  the final verification point after publishing
  ([publication guide](https://docs.apify.com/actors/publishing/publish)).
- Record weekly rank checks for the primary queries and track total users,
  30-day users, successful/failed runs, saves, reviews, and support issues.
- Watch Actor quality recommendations after launch; Apify recalculates the score
  several times per day and uses related factors in Store and MCP search ranking
  ([quality-score documentation](https://docs.apify.com/actors/publishing/quality-score)).
- Re-check direct competitors and pricing monthly during the first quarter because
  all three direct competitors are newly listed and their adoption/pricing can
  change quickly.

## Final recommendation

Publish around the narrow promise **“Zi Wei Dou Shu + BaZi Chinese astrology MCP”**,
not generic horoscope or fortune telling. The Store currently has direct BaZi/Saju
competition but no surfaced Zi Wei specialist in the reviewed searches. Mingli can
own that gap by making Zi Wei the headline, BaZi the adjacent high-intent keyword,
and MCP/API integration the buyer-facing product. The immediate priority is a
clear English Store landing page with real requests and outputs; machine-readable
web/output schemas and MCP structured results should follow immediately after.
