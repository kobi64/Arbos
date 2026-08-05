"""
ArbOS™
EX-107
Exchange Connectivity Supervisor
"""

import time


class ExchangeConnectivitySupervisor:
    def __init__(
        self,
        disconnect_timeout_seconds,
        max_latency_ms,
        clock=None,
    ):
        if disconnect_timeout_seconds < 0:
            raise ValueError("disconnect_timeout_seconds cannot be negative")

        if max_latency_ms < 0:
            raise ValueError("max_latency_ms cannot be negative")

        self._disconnect_timeout_seconds = float(
            disconnect_timeout_seconds
        )
        self._max_latency_ms = float(max_latency_ms)
        self._clock = clock or time.time
        self._exchanges = {}

    def record_heartbeat(
        self,
        exchange_id,
        latency_ms,
        connected,
    ):
        if exchange_id is None or not str(exchange_id).strip():
            raise ValueError("exchange_id is required")

        if latency_ms < 0:
            raise ValueError("latency_ms cannot be negative")

        exchange_id = str(exchange_id).strip()
        latency_ms = float(latency_ms)
        connected = bool(connected)
        now = float(self._clock())

        self._exchanges[exchange_id] = {
            "last_heartbeat": now,
            "latency_ms": latency_ms,
            "connected": connected,
        }

        if not connected:
            return {
                "exchange_id": exchange_id,
                "healthy": False,
                "reason": "exchange_disconnected",
            }

        if latency_ms > self._max_latency_ms:
            return {
                "exchange_id": exchange_id,
                "healthy": False,
                "reason": "latency_exceeded",
            }

        return {
            "exchange_id": exchange_id,
            "healthy": True,
            "reason": None,
        }

    def check_health(self, exchange_id):
        record = self._exchanges.get(exchange_id)

        if record is None:
            raise ValueError("exchange not found")

        if not record["connected"]:
            return {
                "exchange_id": exchange_id,
                "healthy": False,
                "reason": "exchange_disconnected",
            }

        elapsed = float(self._clock()) - record["last_heartbeat"]

        if elapsed > self._disconnect_timeout_seconds:
            return {
                "exchange_id": exchange_id,
                "healthy": False,
                "reason": "connection_timeout",
            }

        if record["latency_ms"] > self._max_latency_ms:
            return {
                "exchange_id": exchange_id,
                "healthy": False,
                "reason": "latency_exceeded",
            }

        return {
            "exchange_id": exchange_id,
            "healthy": True,
            "reason": None,
        }
