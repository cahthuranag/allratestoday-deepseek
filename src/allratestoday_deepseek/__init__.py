"""Plug real-time currency exchange rates into DeepSeek via tool calling."""

from .client import AllRatesTodayClient, AllRatesTodayError
from .tools import TOOLS, dispatch_tool
from .agent import DeepSeekCurrencyAgent

__all__ = [
    "AllRatesTodayClient",
    "AllRatesTodayError",
    "TOOLS",
    "dispatch_tool",
    "DeepSeekCurrencyAgent",
]
__version__ = "0.1.0"
