"""Command-line entry point: `allratestoday-deepseek` runs an interactive REPL."""

from __future__ import annotations

import argparse
import sys

from .agent import DeepSeekCurrencyAgent, run_chat


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="allratestoday-deepseek",
        description="Interactive DeepSeek chat with real-time currency tools.",
    )
    parser.add_argument("--model", default="deepseek-chat", help="DeepSeek model (default: deepseek-chat).")
    parser.add_argument(
        "--ask",
        metavar="QUESTION",
        help="Ask a single question and exit, instead of starting the REPL.",
    )
    args = parser.parse_args(argv)

    try:
        agent = DeepSeekCurrencyAgent(model=args.model)
    except RuntimeError as err:
        print(f"error: {err}", file=sys.stderr)
        return 2

    try:
        if args.ask:
            print(agent.ask(args.ask))
            return 0
        print(
            "allratestoday-deepseek — type a question, or :q to quit.\n"
            "Try: 'What's USD to EUR now?' or 'Convert 250 GBP to JPY'.\n"
        )
        run_chat(agent, iter(lambda: input("you: "), ""))
        return 0
    finally:
        agent.close()


if __name__ == "__main__":
    raise SystemExit(main())
