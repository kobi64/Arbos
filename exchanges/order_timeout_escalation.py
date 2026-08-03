"""
ArbOS™
EX-059
Order Timeout & Escalation Engine
"""


class OrderTimeoutEscalationEngine:
    def __init__(
        self,
        warning_seconds=30.0,
        timeout_seconds=60.0,
    ):
        if timeout_seconds <= warning_seconds:
            raise ValueError(
                "timeout_seconds must exceed warning_seconds"
            )

        self.warning_seconds = float(warning_seconds)
        self.timeout_seconds = float(timeout_seconds)

    def evaluate(self, elapsed_seconds):
        elapsed_seconds = float(elapsed_seconds)

        if elapsed_seconds < 0:
            raise ValueError(
                "elapsed_seconds cannot be negative"
            )

        remaining_seconds = max(
            0.0,
            self.timeout_seconds - elapsed_seconds,
        )

        if elapsed_seconds >= self.timeout_seconds:
            return {
                "state": "TIMED_OUT",
                "escalate": True,
                "reason": "TIMEOUT_EXCEEDED",
                "remaining_seconds": 0.0,
            }

        if elapsed_seconds >= self.warning_seconds:
            return {
                "state": "WARNING",
                "escalate": False,
                "reason": "WARNING_THRESHOLD_REACHED",
                "remaining_seconds": remaining_seconds,
            }

        return {
            "state": "OK",
            "escalate": False,
            "reason": None,
            "remaining_seconds": remaining_seconds,
        }
