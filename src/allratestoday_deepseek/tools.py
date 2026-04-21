"""OpenAI/DeepSeek function-calling tool schemas + dispatcher.

DeepSeek's Chat Completions API is OpenAI-compatible, so the same ``tools=``
argument format works. These schemas follow that format.
"""

from __future__ import annotations

import json
from typing import Any

from .client import AllRatesTodayClient

CCY = {
    "type": "string",
    "description": "ISO 4217 currency code (e.g. USD, EUR, GBP).",
    "minLength": 3,
    "maxLength": 3,
}


TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_exchange_rate",
            "description": "Get the current mid-market exchange rate between two currencies. No API key required.",
            "parameters": {
                "type": "object",
                "properties": {"source": CCY, "target": CCY},
                "required": ["source", "target"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "convert_currency",
            "description": "Convert an amount from one currency to another at the current mid-market rate.",
            "parameters": {
                "type": "object",
                "properties": {
                    "source": CCY,
                    "target": CCY,
                    "amount": {"type": "number", "description": "Amount in the source currency."},
                },
                "required": ["source", "target", "amount"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_historical_rates",
            "description": (
                "Get historical exchange-rate data points for a currency pair over a period. "
                "Periods: 1d (hourly), 7d (daily), 30d (daily), 1y (weekly). No API key required."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "source": CCY,
                    "target": CCY,
                    "period": {
                        "type": "string",
                        "enum": ["1d", "7d", "30d", "1y"],
                        "default": "7d",
                    },
                },
                "required": ["source", "target"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_currencies",
            "description": "List all supported currencies with code, name, and symbol.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_financial_news",
            "description": "Get the latest financial and currency-market news from major sources.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
]


def dispatch_tool(client: AllRatesTodayClient, name: str, arguments: str | dict[str, Any]) -> str:
    """Run a tool by name with JSON-or-dict arguments. Returns a JSON string.

    DeepSeek returns ``tool_calls[i].function.arguments`` as a JSON string, so
    this helper accepts either that raw string or an already-parsed dict.
    """
    args = json.loads(arguments) if isinstance(arguments, str) else (arguments or {})
    try:
        if name == "get_exchange_rate":
            data = client.get_rate(args["source"], args["target"])
        elif name == "convert_currency":
            data = client.convert(args["source"], args["target"], float(args["amount"]))
        elif name == "get_historical_rates":
            data = client.get_historical_rates(args["source"], args["target"], args.get("period", "7d"))
        elif name == "list_currencies":
            data = client.list_symbols()
        elif name == "get_financial_news":
            data = client.get_news()
        else:
            return json.dumps({"error": f"unknown tool: {name}"})
    except Exception as err:  # noqa: BLE001 — return errors to the model as content
        return json.dumps({"error": str(err)})
    return json.dumps(data, default=str)
