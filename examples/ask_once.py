"""Ask DeepSeek a single currency question and print the answer.

    DEEPSEEK_API_KEY=sk-... python examples/ask_once.py "What's USD to EUR right now?"
"""
from __future__ import annotations

import sys

from allratestoday_deepseek import DeepSeekCurrencyAgent


def main() -> int:
    question = " ".join(sys.argv[1:]) or "What is the current USD to EUR exchange rate?"
    with DeepSeekCurrencyAgent() as agent:
        print(agent.ask(question))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
