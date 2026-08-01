"""
ArbOS™
EX-018
Slippage Validation

Validates whether the actual execution price remains
within the acceptable slippage tolerance compared with
the expected market price.
"""


class SlippageValidation:

    @staticmethod
    def validate(
        expected_price: float,
        execution_price: float,
        max_slippage_percent: float,
    ):
        if expected_price <= 0:
            raise ValueError("expected_price must be positive")

        if max_slippage_percent < 0:
            raise ValueError("max_slippage_percent cannot be negative")

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
