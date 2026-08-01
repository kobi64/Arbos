"""
ArbOS™
EX-017
Trade Size Validation

Validates that a proposed trade size is positive and remains
within configured minimum and maximum execution limits.
"""


class TradeSizeValidation:

    @staticmethod
    def validate(
        trade_size: float,
        min_trade_size: float,
        max_trade_size: float,
    ):
        if min_trade_size > max_trade_size:
            raise ValueError("min_trade_size cannot exceed max_trade_size")

        if trade_size <= 0:
            return {
                "valid": False,
                "reason": "non_positive_trade_size",
            }

        if trade_size < min_trade_size:
            return {
                "valid": False,
                "reason": "below_minimum",
            }

        if trade_size > max_trade_size:
            return {
                "valid": False,
                "reason": "above_maximum",
            }

        return {
            "valid": True,
            "reason": None,
        }
