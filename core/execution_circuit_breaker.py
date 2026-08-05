"""
ArbOS™
EX-109
Execution Circuit Breaker
"""

import time


class ExecutionCircuitBreaker:
    def __init__(
        self,
        failure_threshold,
        recovery_timeout_seconds,
        clock=None,
    ):
        if failure_threshold <= 0:
            raise ValueError("failure_threshold must be positive")

        if recovery_timeout_seconds < 0:
            raise ValueError("recovery_timeout_seconds cannot be negative")

        self._failure_threshold = int(failure_threshold)
        self._recovery_timeout_seconds = float(
            recovery_timeout_seconds
        )
        self._clock = clock or time.time
        self._state = "CLOSED"
        self._failure_count = 0
        self._opened_at = None

    def record_failure(self, reason):
        now = float(self._clock())

        if self._state == "HALF_OPEN":
            self._failure_count += 1
            self._state = "OPEN"
            self._opened_at = now

            return {
                "state": self._state,
                "failure_count": self._failure_count,
                "allowed": False,
                "reason": reason,
            }

        self._failure_count += 1

        if self._failure_count >= self._failure_threshold:
            self._state = "OPEN"
            self._opened_at = now

        return {
            "state": self._state,
            "failure_count": self._failure_count,
            "allowed": self._state != "OPEN",
            "reason": reason,
        }

    def allow_execution(self):
        if self._state == "OPEN":
            elapsed = float(self._clock()) - self._opened_at

            if elapsed >= self._recovery_timeout_seconds:
                self._state = "HALF_OPEN"
                return {
                    "allowed": True,
                    "state": self._state,
                    "reason": None,
                }

            return {
                "allowed": False,
                "state": self._state,
                "reason": "circuit_open",
            }

        return {
            "allowed": True,
            "state": self._state,
            "reason": None,
        }

    def record_success(self):
        self._state = "CLOSED"
        self._failure_count = 0
        self._opened_at = None

        return {
            "state": self._state,
            "failure_count": self._failure_count,
            "allowed": True,
        }

    def status(self):
        return {
            "state": self._state,
            "failure_count": self._failure_count,
            "allowed": self._state != "OPEN",
        }
