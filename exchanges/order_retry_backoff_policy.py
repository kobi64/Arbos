"""
ArbOS™
EX-058
Order Retry & Backoff Policy Engine
"""


class OrderRetryBackoffPolicy:
    RETRYABLE_ERRORS = {
        "TIMEOUT",
        "RATE_LIMIT",
        "TEMPORARY_UNAVAILABLE",
        "NETWORK_ERROR",
    }

    def __init__(
        self,
        max_attempts=3,
        base_delay_seconds=1.0,
        max_delay_seconds=30.0,
    ):
        self.max_attempts = max_attempts
        self.base_delay_seconds = base_delay_seconds
        self.max_delay_seconds = max_delay_seconds

    def evaluate(
        self,
        attempt,
        error_type,
        execution_uncertain=False,
    ):
        if attempt <= 0:
            raise ValueError("attempt must be positive")

        if execution_uncertain:
            return {
                "retry": False,
                "escalate": True,
                "delay_seconds": 0.0,
                "reason": "EXECUTION_STATE_UNCERTAIN",
            }

        if error_type not in self.RETRYABLE_ERRORS:
            return {
                "retry": False,
                "escalate": True,
                "delay_seconds": 0.0,
                "reason": "NON_RETRYABLE_ERROR",
            }

        if attempt >= self.max_attempts:
            return {
                "retry": False,
                "escalate": True,
                "delay_seconds": 0.0,
                "reason": "MAX_ATTEMPTS_REACHED",
            }

        delay = self.base_delay_seconds * (2 ** (attempt - 1))
        delay = min(delay, self.max_delay_seconds)

        return {
            "retry": True,
            "escalate": False,
            "delay_seconds": delay,
            "reason": "RETRY_ALLOWED",
        }
