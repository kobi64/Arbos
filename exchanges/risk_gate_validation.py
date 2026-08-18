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

import math


class RiskGateValidation:

    @staticmethod
    def _number(value, field):
        if isinstance(value, bool):
            raise ValueError(f"{field} must be a finite number")

        try:
            number = float(value)
        except (TypeError, ValueError, OverflowError):
            raise ValueError(
                f"{field} must be a finite number"
            ) from None

        if not math.isfinite(number):
            raise ValueError(
                f"{field} must be a finite number"
            )

        return number

    @staticmethod
    def _failure_count(value):
        if isinstance(value, bool):
            raise ValueError(
                "failed attempt counts must be non-negative integers"
            )

        if not isinstance(value, int) or value < 0:
            raise ValueError(
                "failed attempt counts must be non-negative integers"
            )

        return value

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
        expected_profit = RiskGateValidation._number(
            expected_profit,
            "expected_profit",
        )
        minimum_profit = RiskGateValidation._number(
            minimum_profit,
            "minimum_profit",
        )
        trade_size = RiskGateValidation._number(
            trade_size,
            "trade_size",
        )
        maximum_exposure = RiskGateValidation._number(
            maximum_exposure,
            "maximum_exposure",
        )
        confidence_score = RiskGateValidation._number(
            confidence_score,
            "confidence_score",
        )
        minimum_confidence = RiskGateValidation._number(
            minimum_confidence,
            "minimum_confidence",
        )

        failed_attempts = RiskGateValidation._failure_count(
            failed_attempts
        )
        maximum_failed_attempts = RiskGateValidation._failure_count(
            maximum_failed_attempts
        )

        if expected_profit < 0:
            raise ValueError("expected_profit cannot be negative")

        if minimum_profit < 0:
            raise ValueError("minimum_profit cannot be negative")

        if trade_size < 0:
            raise ValueError("trade_size cannot be negative")

        if maximum_exposure < 0:
            raise ValueError("maximum_exposure cannot be negative")

        if not 0 <= confidence_score <= 1:
            raise ValueError(
                "confidence_score must be between 0 and 1"
            )

        if not 0 <= minimum_confidence <= 1:
            raise ValueError(
                "minimum_confidence must be between 0 and 1"
            )

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
