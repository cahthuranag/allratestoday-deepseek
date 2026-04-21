"""Thin typed wrapper over the AllRatesToday REST API."""

from __future__ import annotations

import os
from typing import Any, Literal, Optional

import httpx

DEFAULT_BASE_URL = "https://allratestoday.com/api"
USER_AGENT = "allratestoday-deepseek/0.2.0"

Period = Literal["1d", "7d", "30d", "1y"]


class AllRatesTodayError(RuntimeError):
    """Raised when the AllRatesToday API returns a non-2xx response."""

    def __init__(self, message: str, status: Optional[int] = None, body: Any = None):
        super().__init__(message)
        self.status = status
        self.body = body


class AllRatesTodayClient:
    """Minimal client for the public AllRatesToday endpoints.

    The `/rate`, `/historical-rates`, `/v1/symbols`, and `/news` endpoints are
    public and need no API key. The `/v1/rates` multi-target endpoint needs a
    bearer token, passed via ``api_key`` or the ``ALLRATES_API_KEY`` env var.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 15.0,
    ):
        self.api_key = api_key or os.environ.get("ALLRATES_API_KEY")
        self.base_url = (base_url or os.environ.get("ALLRATES_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self._client = httpx.Client(timeout=timeout, headers={"User-Agent": USER_AGENT})

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "AllRatesTodayClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _get(self, path: str, params: dict[str, str], require_auth: bool = False) -> Any:
        headers = {"Accept": "application/json"}
        if require_auth:
            if not self.api_key:
                raise AllRatesTodayError(
                    "This endpoint requires an AllRatesToday API key. "
                    "Set ALLRATES_API_KEY or pass api_key= to the client."
                )
            headers["Authorization"] = f"Bearer {self.api_key}"
        elif self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        clean = {k: v for k, v in params.items() if v is not None and v != ""}
        resp = self._client.get(self.base_url + path, params=clean, headers=headers)
        try:
            body = resp.json()
        except Exception:
            body = resp.text
        if resp.status_code >= 400:
            message = (
                body.get("error") if isinstance(body, dict) and "error" in body else f"HTTP {resp.status_code}"
            )
            raise AllRatesTodayError(message, status=resp.status_code, body=body)
        return body

    # ---- Public endpoints (no auth) ---------------------------------------

    def get_rate(self, source: str, target: str) -> dict[str, Any]:
        """GET /rate — single mid-market rate for a pair."""
        return self._get("/rate", {"source": source.upper(), "target": target.upper()})

    def list_symbols(self) -> dict[str, Any]:
        """GET /v1/symbols — supported currencies."""
        return self._get("/v1/symbols", {})

    # ---- Authenticated ----------------------------------------------------

    def get_historical_rates(self, source: str, target: str, period: Period = "7d") -> dict[str, Any]:
        """GET /historical-rates — time series over 1d/7d/30d/1y. Requires API key."""
        return self._get(
            "/historical-rates",
            {"source": source.upper(), "target": target.upper(), "period": period},
            require_auth=True,
        )

    def get_rates(
        self,
        source: str,
        target: str,
        time: Optional[str] = None,
        group: Optional[Literal["hour", "day", "week", "month"]] = None,
    ) -> Any:
        """GET /v1/rates — multi-target (comma-separated) with higher limits.

        Example: ``client.get_rates("USD", "EUR,GBP,JPY")``.
        """
        return self._get(
            "/v1/rates",
            {"source": source.upper(), "target": target.upper(), "time": time, "group": group},
            require_auth=True,
        )

    # ---- Convenience ------------------------------------------------------

    def convert(self, source: str, target: str, amount: float) -> dict[str, Any]:
        """Fetch the pair rate and multiply. Not a separate endpoint."""
        data = self.get_rate(source, target)
        rate = float(data["rate"])
        return {
            "source": source.upper(),
            "target": target.upper(),
            "amount": amount,
            "rate": rate,
            "result": round(amount * rate, 4),
        }
