"""
ArbOS™
EX-106
Scanner Health Monitor
"""

import time


class ScannerHealthMonitor:
    def __init__(
        self,
        heartbeat_timeout_seconds,
        max_latency_ms,
        clock=None,
    ):
        if heartbeat_timeout_seconds < 0:
            raise ValueError("heartbeat_timeout_seconds cannot be negative")

        if max_latency_ms < 0:
            raise ValueError("max_latency_ms cannot be negative")

        self._heartbeat_timeout_seconds = float(
            heartbeat_timeout_seconds
        )
        self._max_latency_ms = float(max_latency_ms)
        self._clock = clock or time.time
        self._scanners = {}

    def record_heartbeat(
        self,
        scanner_id,
        latency_ms,
        opportunities_found,
    ):
        if scanner_id is None or not str(scanner_id).strip():
            raise ValueError("scanner_id is required")

        if latency_ms < 0:
            raise ValueError("latency_ms cannot be negative")

        scanner_id = str(scanner_id).strip()
        now = float(self._clock())
        latency_ms = float(latency_ms)
        opportunities_found = int(opportunities_found)

        record = self._scanners.setdefault(
            scanner_id,
            {
                "last_heartbeat": now,
                "heartbeats": 0,
                "total_latency_ms": 0.0,
                "opportunities_found": 0,
            },
        )

        record["last_heartbeat"] = now
        record["heartbeats"] += 1
        record["total_latency_ms"] += latency_ms
        record["opportunities_found"] += opportunities_found

        healthy = latency_ms <= self._max_latency_ms

        return {
            "scanner_id": scanner_id,
            "healthy": healthy,
            "reason": None if healthy else "latency_exceeded",
        }

    def check_health(self, scanner_id):
        record = self._scanners.get(scanner_id)

        if record is None:
            raise ValueError("scanner not found")

        elapsed = float(self._clock()) - record["last_heartbeat"]

        if elapsed > self._heartbeat_timeout_seconds:
            return {
                "scanner_id": scanner_id,
                "healthy": False,
                "reason": "heartbeat_timeout",
            }

        return {
            "scanner_id": scanner_id,
            "healthy": True,
            "reason": None,
        }

    def statistics(self, scanner_id):
        record = self._scanners.get(scanner_id)

        if record is None:
            raise ValueError("scanner not found")

        return {
            "scanner_id": scanner_id,
            "heartbeats": record["heartbeats"],
            "opportunities_found": record["opportunities_found"],
            "average_latency_ms": (
                record["total_latency_ms"] / record["heartbeats"]
            ),
        }
