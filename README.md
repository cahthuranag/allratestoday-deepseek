# AllRatesToday × DeepSeek — allratestoday-deepseek

Give DeepSeek chat and agents real-time access to currency exchange rates and historical data, via function calling. Ships ready-to-use OpenAI-format tool schemas, a thin agent wrapper, and a CLI — for anyone building a DeepSeek app that must not hallucinate a rate.

[![Powered by AllRatesToday](https://img.shields.io/badge/Powered%20by-AllRatesToday-orange.svg)](https://allratestoday.com)
[![PyPI](https://img.shields.io/pypi/v/allratestoday-deepseek?label=PyPI&color=3775a9)](https://pypi.org/project/allratestoday-deepseek/)
[![CI](https://github.com/AllRates-Today/allratestoday-deepseek/actions/workflows/ci.yml/badge.svg)](https://github.com/AllRates-Today/allratestoday-deepseek/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![API Status](https://img.shields.io/badge/API-Status-brightgreen)](https://allratestoday.com/status)

English | [简体中文](./README-zh-CN.md)

DeepSeek's Chat Completions API is OpenAI-compatible, so the standard `tools=` mechanism works unchanged. This package wires four currency tools into that mechanism so DeepSeek can answer questions like:

- *"What's USD to EUR right now?"*
- *"Convert 1000 GBP to JPY."*
- *"How has USD/INR moved over the last 30 days?"*
- *"List every supported currency."*

Rates come from the [AllRatesToday API](https://allratestoday.com) — 160 currencies, mid-market rates sourced from institutional interbank market data.

## 🚀 Features

- 🧰 **Four tool schemas** — `get_exchange_rate`, `convert_currency`, `get_historical_rates`, `list_currencies`, in OpenAI/DeepSeek function-calling format (`TOOLS`)
- 🤖 **Agent wrapper** — `DeepSeekCurrencyAgent` runs the full tool-call loop for you (up to `max_tool_rounds`, default 6)
- 💻 **CLI** — `allratestoday-deepseek` for an interactive REPL or a one-shot `--ask`
- 🔧 **Bring your own loop** — import `TOOLS` and `dispatch_tool` and drive the OpenAI SDK yourself
- 🌍 **160 currencies** — mid-market rates plus `1d` / `7d` / `30d` / `1y` history
- 🪶 **Two dependencies** — `openai` and `httpx`, nothing else
- 🚫 **No hallucinated rates** — the system prompt instructs the model to call a tool rather than guess

## 🔑 Get your API key

Two keys are involved:

| Variable | Required? | Purpose |
|---|---|---|
| `DEEPSEEK_API_KEY` | Yes | Your DeepSeek key, from [platform.deepseek.com/api_keys](https://platform.deepseek.com/api_keys). Without it `DeepSeekCurrencyAgent()` raises `RuntimeError`. |
| `ALLRATES_API_KEY` | Yes for rate lookups | Your AllRatesToday key. Get a free one at [allratestoday.com/register](https://allratestoday.com/register). |
| `ALLRATES_BASE_URL` | No | Override the API base URL (default `https://allratestoday.com/api`). |

Only `list_currencies` (`GET /api/v1/symbols`) answers without an AllRatesToday key. Rate, conversion and historical lookups all return `401` unauthenticated, so set `ALLRATES_API_KEY` for any real use.

## 📦 Installation

```bash
pip install allratestoday-deepseek
```

Python 3.9+. From a checkout, `pip install -e ".[dev]"` also installs `pytest` and `ruff`.

## 🏁 Quick start

One-shot question:

```bash
export DEEPSEEK_API_KEY=sk-...
export ALLRATES_API_KEY=art_live_...
allratestoday-deepseek --ask "What is 2500 USD in EUR right now?"
```

Interactive chat (type `:q`, `exit`, `quit` or a blank line to leave):

```bash
allratestoday-deepseek
allratestoday-deepseek --model deepseek-reasoner
```

As a library:

```python
from allratestoday_deepseek import DeepSeekCurrencyAgent

with DeepSeekCurrencyAgent() as agent:
    print(agent.ask("How many Japanese Yen is 500 Swiss Francs?"))
```

Multi-turn, keeping your own history:

```python
from allratestoday_deepseek import DeepSeekCurrencyAgent

history = []
with DeepSeekCurrencyAgent(model="deepseek-chat") as agent:
    answer = agent.ask("What is USD to EUR?", history=history)
    history += [
        {"role": "user", "content": "What is USD to EUR?"},
        {"role": "assistant", "content": answer},
    ]
    print(agent.ask("And to GBP?", history=history))
```

Runnable examples live in [`examples/`](examples/):

```bash
python examples/ask_once.py "What's USD to EUR right now?"   # one question, then exit
python examples/chat.py                                      # interactive REPL
python examples/raw_tool_call.py                             # drive the tool loop yourself
```

## 📚 API reference

### Tools exposed to the model

| Tool | AllRatesToday key | Parameters | Description |
|---|---|---|---|
| `get_exchange_rate` | Yes | `source`, `target` | Current mid-market rate for a pair. |
| `convert_currency` | Yes | `source`, `target`, `amount` | Fetches the pair rate and multiplies — not a separate endpoint. |
| `get_historical_rates` | Yes | `source`, `target`, `period` (`1d`/`7d`/`30d`/`1y`, default `7d`) | Time series: `1d` hourly, `7d`/`30d` daily, `1y` weekly. |
| `list_currencies` | No | — | Every supported currency with code, name and symbol. |

### `DeepSeekCurrencyAgent`

```python
DeepSeekCurrencyAgent(
    deepseek_api_key=None,       # falls back to $DEEPSEEK_API_KEY
    allrates_api_key=None,       # falls back to $ALLRATES_API_KEY
    model="deepseek-chat",
    base_url="https://api.deepseek.com",
    system_prompt=SYSTEM_PROMPT,
    max_tool_rounds=6,
)
```

| Member | Description |
|---|---|
| `ask(question, history=None)` | Runs the tool-call loop and returns the final answer string. |
| `close()` | Closes the underlying HTTP client. Also available via `with`. |
| `run_chat(agent, stream_in)` | Module-level REPL helper over an iterable of user lines. |

### `AllRatesTodayClient`

Thin `httpx` wrapper over the REST API, usable on its own.

| Method | Endpoint | Auth |
|---|---|---|
| `get_rate(source, target)` | `GET /rate` | Key required by the API |
| `list_symbols()` | `GET /v1/symbols` | None |
| `get_historical_rates(source, target, period="7d")` | `GET /historical-rates` | Bearer key |
| `get_rates(source, target, time=None, group=None)` | `GET /v1/rates` — comma-separated targets, `group` of `hour`/`day`/`week`/`month` | Bearer key |
| `convert(source, target, amount)` | Convenience — `get_rate` × amount, rounded to 4 dp | Key required by the API |

### Tool plumbing

```python
from allratestoday_deepseek import TOOLS, dispatch_tool, AllRatesTodayClient

client = AllRatesTodayClient()                       # reads $ALLRATES_API_KEY
result = dispatch_tool(client, "get_exchange_rate", '{"source":"USD","target":"EUR"}')
```

`TOOLS` is the list you pass as `tools=` to `chat.completions.create`. `dispatch_tool` accepts DeepSeek's raw JSON-string arguments or an already-parsed dict, and always returns a JSON string suitable for a `role: "tool"` message.

## 🗺️ Currencies covered

160 currencies as returned by `list_currencies`, including
🇺🇸 `USD` · 🇪🇺 `EUR` · 🇬🇧 `GBP` · 🇯🇵 `JPY` · 🇨🇭 `CHF` · 🇨🇦 `CAD` · 🇦🇺 `AUD` · 🇳🇿 `NZD` · 🇮🇳 `INR` · 🇨🇳 `CNY` · 🇧🇷 `BRL` · 🇲🇽 `MXN` · 🇹🇷 `TRY` · 🇿🇦 `ZAR` · 🇸🇬 `SGD` · 🇭🇰 `HKD` · 🇰🇷 `KRW` · 🇦🇪 `AED` · 🇱🇰 `LKR` · 🇳🇬 `NGN`.

## 🛡️ Error handling

Tool failures are never raised into the model's face — `dispatch_tool` catches them and returns `{"error": "..."}` as the tool result, so DeepSeek can explain or retry.

```python
from allratestoday_deepseek import AllRatesTodayClient, AllRatesTodayError

try:
    AllRatesTodayClient().get_historical_rates("USD", "EUR", "30d")
except AllRatesTodayError as err:
    print(err.status, err.body)
```

| Raised | When |
|---|---|
| `RuntimeError` | No DeepSeek key found when constructing the agent. |
| `RuntimeError` | The model kept calling tools past `max_tool_rounds` — raise the limit. |
| `AllRatesTodayError` | Any non-2xx from the API; carries `.status` and `.body`. |
| `AllRatesTodayError` | An authenticated endpoint was called with no AllRatesToday key. |

Common API statuses: `401` missing or invalid key · `429` rate limit or monthly quota exceeded · `5xx` upstream error.

## 💡 Notes

**How a question is answered**

1. You send DeepSeek a question through `agent.ask()`.
2. The agent calls `chat.completions.create(..., tools=TOOLS, tool_choice="auto")` — DeepSeek receives all four tool schemas.
3. If it needs data, it emits a `tool_call` such as `get_exchange_rate(source="USD", target="EUR")`.
4. The agent runs that tool against the AllRatesToday API and appends the JSON result as a `role: "tool"` message.
5. Steps 2–4 repeat until DeepSeek answers in natural language, citing the live rate — or `max_tool_rounds` is hit.

**Compatibility** — any DeepSeek model that supports function calling; `deepseek-chat` is the default and `deepseek-reasoner` is selectable with `--model`. CI exercises Python 3.9, 3.11 and 3.12 on Ubuntu.

**Rate caching** — every `get_exchange_rate` or `convert_currency` tool call is one API request, and each request counts toward your monthly quota. Cache aggressively if the same pair is asked for repeatedly.

## 🔗 Links

- **Website:** [allratestoday.com](https://allratestoday.com)
- **API docs:** [allratestoday.com/docs](https://allratestoday.com/docs)
- **Free API key:** [allratestoday.com/register](https://allratestoday.com/register)
- **Developer guide:** [allratestoday.com/developers](https://allratestoday.com/developers)
- **Status:** [allratestoday.com/status](https://allratestoday.com/status)
- **Support:** [allratestoday.com/contact](https://allratestoday.com/contact)
- **MCP server:** [`@allratestoday/mcp-server`](https://www.npmjs.com/package/@allratestoday/mcp-server) — for Claude Code, Cursor and Claude Desktop
- **JavaScript SDK:** [`@allratestoday/sdk`](https://www.npmjs.com/package/@allratestoday/sdk)

## 📜 License

MIT — see [LICENSE](./LICENSE).
