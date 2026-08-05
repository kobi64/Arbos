"""
ArbOS™
EX-110
Exchange Rate Limiter
"""

import time


class ExchangeRateLimiter:
    def __init__(
        self,
        max_requests,
        window_seconds,
        clock=None,
    ):
        if max_requests <= 0:
            raise ValueError("max_requests must be positive")

        if window_seconds < 0:
            raise ValueError("window_seconds cannot be negative")

        self._max_requests = int(max_requests)
        self._window_seconds = float(window_seconds)
        self._clock = clock or time.time
        self._windows = {}

    def allow_request(self, exchange_id):
        if exchange_id is None or not str(exchange_id).strip():
            raise ValueError("exchange_id is required")

        exchange_id = str(exchange_id).strip()
        now = float(self._clock())
        window = self._windows.get(exchange_id)

        if (
            window is None
            or now - window["started_at"] >= self._window_seconds
        ):
            window = {
                "started_at": now,
                "count": 0,
            }
            self._windows[exchange_id] = window

        if window["count"] >= self._max_requests:
            retry_after = max(
                self._window_seconds - (now - window["started_at"]),
                0.0,
            )

            return {
                "exchange_id": exchange_id,
                "allowed": False,
                "reason": "rate_limit_reached",
                "remaining_requests": 0,
                "retry_after_seconds": retry_after,
            }

        window["count"] += 1
        remaining = self._max_requests - window["count"]

        return {
            "exchange_id": exchange_id,
            "allowed": True,
            "reason": None,
            "remaining_requests": remaining,
            "retry_after_seconds": 0.0,
        }
