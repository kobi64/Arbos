"""
ArbOS™
EX-020
Risk Gate Validation

Final safety gate before an arbitrage opportunity
can proceed toward execution.

Checks:
- Minimum expected profit
- Maximum trade exposure
- Route confidence
- Failed attempt limits
"""


class RiskGateValidation:

    @staticmethod
    def validate(
        expected_profit: float,
        minimum_profit: float,
        trade_size: float,
        maximum_exposure: float,
        confidence_score: float,
        minimum_confidence: float,
        failed_attempts: int,
        maximum_failed_attempts: int,
    ):
        if expected_profit < 0:
            raise ValueError("expected_profit cannot be negative")

        if trade_size < 0:
            raise ValueError("trade_size cannot be negative")

        if maximum_exposure < 0:
            raise ValueError("maximum_exposure cannot be negative")

        if not 0 <= confidence_score <= 1:
            raise ValueError("confidence_score must be between 0 and 1")

        if not 0 <= minimum_confidence <= 1:
            raise ValueError("minimum_confidence must be between 0 and 1")

        if failed_attempts < 0:
            raise ValueError("failed_attempts cannot be negative")

        if maximum_failed_attempts < 0:
            raise ValueError("maximum_failed_attempts cannot be negative")

        if expected_profit < minimum_profit:
            return {
                "valid": False,
                "reason": "insufficient_profit",
            }

        if trade_size > maximum_exposure:
            return {
                "valid": False,
                "reason": "exposure_limit_exceeded",
            }

        if confidence_score < minimum_confidence:
            return {
                "valid": False,
                "reason": "low_confidence",
            }

        if failed_attempts > maximum_failed_attempts:
            return {
                "valid": False,
                "reason": "failure_limit_exceeded",
            }

        return {
            "valid": True,
            "reason": None,
        }
