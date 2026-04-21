"""Low-level example: drive DeepSeek's tool calls yourself (no agent wrapper).

Useful if you're integrating AllRatesToday tools into an existing DeepSeek
workflow that already has its own conversation-management code.

    DEEPSEEK_API_KEY=sk-... python examples/raw_tool_call.py
"""
from __future__ import annotations

import os

from openai import OpenAI

from allratestoday_deepseek import AllRatesTodayClient, TOOLS, dispatch_tool


def main() -> int:
    llm = OpenAI(
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url="https://api.deepseek.com",
    )
    rates = AllRatesTodayClient()

    messages = [
        {"role": "system", "content": "You answer currency questions using the provided tools."},
        {"role": "user", "content": "Convert 2500 USD to EUR."},
    ]

    while True:
        resp = llm.chat.completions.create(
            model="deepseek-chat", messages=messages, tools=TOOLS, tool_choice="auto"
        )
        msg = resp.choices[0].message
        if not msg.tool_calls:
            print(msg.content)
            return 0

        messages.append(
            {
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in msg.tool_calls
                ],
            }
        )
        for tc in msg.tool_calls:
            result = dispatch_tool(rates, tc.function.name, tc.function.arguments)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": tc.function.name,
                    "content": result,
                }
            )


if __name__ == "__main__":
    raise SystemExit(main())
