"""Interactive REPL: chat with DeepSeek and let it call AllRatesToday tools.

    DEEPSEEK_API_KEY=sk-... python examples/chat.py
"""
from __future__ import annotations

from allratestoday_deepseek import DeepSeekCurrencyAgent
from allratestoday_deepseek.agent import run_chat


def main() -> int:
    print(
        "AllRatesToday x DeepSeek — interactive chat.\n"
        "Try: 'What is 1000 GBP in INR?' or 'Show me USD/JPY over 30 days'.\n"
        "Type :q or Ctrl+D to exit.\n"
    )
    with DeepSeekCurrencyAgent() as agent:
        run_chat(agent, iter(lambda: input("you: "), ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
