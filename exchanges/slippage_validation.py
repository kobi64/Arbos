"""
ArbOS™
EX-018
Slippage Validation

Validates whether the actual execution price remains
within the acceptable slippage tolerance compared with
the expected market price.
"""

import math


class SlippageValidation:

    @staticmethod
    def validate(
        expected_price: float,
        execution_price: float,
        max_slippage_percent: float,
    ):
        values = (
            ("expected_price", expected_price),
            ("execution_price", execution_price),
            ("max_slippage_percent", max_slippage_percent),
        )

        normalized = {}

        for field, value in values:
            if isinstance(value, bool):
                raise ValueError(
                    f"{field} must be a finite number"
                )

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

            normalized[field] = number

        expected_price = normalized["expected_price"]
        execution_price = normalized["execution_price"]
        max_slippage_percent = normalized[
            "max_slippage_percent"
        ]

        if expected_price <= 0:
            raise ValueError("expected_price must be positive")

        if execution_price < 0:
            raise ValueError(
                "execution_price cannot be negative"
            )

        if max_slippage_percent < 0:
            raise ValueError(
                "max_slippage_percent cannot be negative"
            )

        # Price improvement is always acceptable.
        if execution_price >= expected_price:
            return {
                "valid": True,
                "reason": None,
            }

        slippage_percent = (
            (expected_price - execution_price)
            / expected_price
        ) * 100

        if slippage_percent > max_slippage_percent:
            return {
                "valid": False,
                "reason": "slippage_exceeded",
            }

        return {
            "valid": True,
            "reason": None,
        }
