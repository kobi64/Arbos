"""
ArbOS™
EX-108
Market Data Freshness Guard
"""

import time


class MarketDataFreshnessGuard:
    def __init__(self, max_age_seconds, clock=None):
        if max_age_seconds < 0:
            raise ValueError("max_age_seconds cannot be negative")

        self._max_age_seconds = float(max_age_seconds)
        self._clock = clock or time.time

    def evaluate(self, symbol, timestamp):
        if symbol is None or not str(symbol).strip():
            raise ValueError("symbol is required")

        now = float(self._clock())
        age_seconds = now - float(timestamp)

        future_timestamp = age_seconds < 0
        fresh = (
            not future_timestamp
            and age_seconds < self._max_age_seconds
        )

        if future_timestamp:
            reason = "market_data_timestamp_in_future"
        elif fresh:
            reason = None
        else:
            reason = "market_data_stale"

        return {
            "symbol": str(symbol).strip(),
            "fresh": fresh,
            "reason": reason,
            "age_seconds": age_seconds,
            "max_age_seconds": self._max_age_seconds,
        }
