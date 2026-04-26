# AllRatesToday × DeepSeek

English | [简体中文](./README-zh-CN.md)

> Give DeepSeek chat and agents real-time access to currency exchange rates and historical data — via function calling.

DeepSeek's Chat Completions API is OpenAI-compatible, so the same tool-calling mechanism works. This package ships ready-to-use tool schemas and a thin agent wrapper that lets DeepSeek answer questions like:

- *"What's USD to EUR right now?"*
- *"Convert 1000 GBP to JPY."*
- *"How has USD/INR moved over the last 30 days?"*
- *"List every supported currency."*

Powered by the [AllRatesToday API](https://allratestoday.com) — 160+ currencies, mid-market rates from Reuters/Refinitiv, public endpoints that need no API key.

## Install

```bash
pip install allratestoday-deepseek
```

## Quick start — one-shot

```bash
export DEEPSEEK_API_KEY=sk-...      # from platform.deepseek.com/api_keys
allratestoday-deepseek --ask "What is 2500 USD in EUR right now?"
```

## Quick start — interactive chat

```bash
allratestoday-deepseek
# or:
python examples/chat.py
```

## Library usage

```python
from allratestoday_deepseek import DeepSeekCurrencyAgent

with DeepSeekCurrencyAgent() as agent:
    print(agent.ask("How many Japanese Yen is 500 Swiss Francs?"))
```

Need finer control? Use the tool schemas directly with the OpenAI SDK pointed at DeepSeek — see `examples/raw_tool_call.py`.

## Tools exposed

| Tool | API key | Description |
|---|---|---|
| `get_exchange_rate` | no | Current mid-market rate between two currencies. |
| `convert_currency` | no | Convert an amount between two currencies at the live rate. |
| `get_historical_rates` | yes | Rate history over `1d`, `7d`, `30d`, or `1y`. |
| `list_currencies` | no | All supported currencies with codes, names, symbols. |

Public tools (`get_exchange_rate`, `convert_currency`, `list_currencies`) work without a key. Set `ALLRATES_API_KEY` for historical data and multi-target queries.

## Environment variables

| Variable | Required? | Purpose |
|---|---|---|
| `DEEPSEEK_API_KEY` | yes | Your DeepSeek API key. |
| `ALLRATES_API_KEY` | no | AllRatesToday API key (for higher limits). Get one at [allratestoday.com/register](https://allratestoday.com/register). |
| `ALLRATES_BASE_URL` | no | Override the API base URL (default `https://allratestoday.com/api`). |

## How it works

1. You send DeepSeek a question.
2. The agent calls `chat.completions.create(..., tools=TOOLS)` — DeepSeek receives all 5 tool schemas.
3. If DeepSeek decides it needs a rate, it emits a `tool_call` (e.g. `get_exchange_rate(source="USD", target="EUR")`).
4. The agent runs the tool against the AllRatesToday API and passes the JSON result back.
5. DeepSeek produces a final natural-language answer, citing the live rate.

No hallucinated rates — the agent never answers without calling the tool first.

## Compatibility

- DeepSeek models that support function calling (`deepseek-chat`, `deepseek-reasoner`).
- Python 3.9+.
- Works on Linux, macOS, and Windows.

## Related

- **MCP server**: [`@allratestoday/mcp-server`](https://www.npmjs.com/package/@allratestoday/mcp-server) — for Claude Code, Cursor, and Claude Desktop.
- **JavaScript SDK**: [`@allratestoday/sdk`](https://www.npmjs.com/package/@allratestoday/sdk) — raw SDK for any Node.js or browser app.
- **Docs**: [allratestoday.com/developers](https://allratestoday.com/developers)

## License

MIT — see [LICENSE](./LICENSE).
