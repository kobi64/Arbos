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
        fresh = age_seconds < self._max_age_seconds

        return {
            "symbol": str(symbol).strip(),
            "fresh": fresh,
            "reason": None if fresh else "market_data_stale",
            "age_seconds": age_seconds,
            "max_age_seconds": self._max_age_seconds,
        }
