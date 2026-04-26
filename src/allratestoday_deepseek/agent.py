"""A tiny tool-calling agent that lets DeepSeek answer currency questions."""

from __future__ import annotations

import os
from typing import Any, Iterable, Optional

from openai import OpenAI

from .client import AllRatesTodayClient
from .tools import TOOLS, dispatch_tool

DEFAULT_MODEL = "deepseek-chat"
DEFAULT_BASE_URL = "https://api.deepseek.com"

SYSTEM_PROMPT = (
    "You are a helpful assistant with access to real-time currency exchange-rate tools "
    "backed by the AllRatesToday API. When a user asks about a current rate, a conversion, "
    "historical rates, or the list of supported currencies, call the appropriate tool "
    "rather than guessing. Always cite the rate and the currencies you used."
)


class DeepSeekCurrencyAgent:
    """Wraps the OpenAI SDK pointed at DeepSeek, with AllRatesToday tools attached."""

    def __init__(
        self,
        deepseek_api_key: Optional[str] = None,
        allrates_api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        base_url: str = DEFAULT_BASE_URL,
        system_prompt: str = SYSTEM_PROMPT,
        max_tool_rounds: int = 6,
    ):
        key = deepseek_api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not key:
            raise RuntimeError(
                "Missing DeepSeek API key. Set DEEPSEEK_API_KEY or pass deepseek_api_key= "
                "to DeepSeekCurrencyAgent()."
            )
        self.llm = OpenAI(api_key=key, base_url=base_url)
        self.model = model
        self.client = AllRatesTodayClient(api_key=allrates_api_key)
        self.system_prompt = system_prompt
        self.max_tool_rounds = max_tool_rounds

    def ask(self, question: str, history: Optional[list[dict[str, Any]]] = None) -> str:
        """One-shot: send ``question``, let DeepSeek call tools, return the final answer."""
        messages: list[dict[str, Any]] = [{"role": "system", "content": self.system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": question})

        for _ in range(self.max_tool_rounds):
            resp = self.llm.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
            )
            msg = resp.choices[0].message

            if not msg.tool_calls:
                return msg.content or ""

            # Record the assistant message that asked for tool calls
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

            # Execute each tool and append its result
            for tc in msg.tool_calls:
                result = dispatch_tool(self.client, tc.function.name, tc.function.arguments)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "name": tc.function.name,
                        "content": result,
                    }
                )

        raise RuntimeError(
            f"DeepSeek kept calling tools past max_tool_rounds={self.max_tool_rounds}. Increase the limit."
        )

    def close(self) -> None:
        self.client.close()

    def __enter__(self) -> "DeepSeekCurrencyAgent":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def run_chat(agent: DeepSeekCurrencyAgent, stream_in: Iterable[str]) -> None:
    """Simple REPL helper used by the CLI and the interactive example."""
    history: list[dict[str, Any]] = []
    for user_text in stream_in:
        user_text = user_text.strip()
        if not user_text or user_text.lower() in {"exit", "quit", ":q"}:
            break
        answer = agent.ask(user_text, history=history)
        history.append({"role": "user", "content": user_text})
        history.append({"role": "assistant", "content": answer})
        print(f"\nassistant: {answer}\n")
