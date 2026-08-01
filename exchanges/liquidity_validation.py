"""
ArbOS™
EX-019
Liquidity Validation

Validates whether available market liquidity is sufficient
to support a proposed arbitrage trade size.
"""


class LiquidityValidation:

    @staticmethod
    def validate(
        trade_size: float,
        available_liquidity: float,
        minimum_liquidity_ratio: float,
    ):
        if minimum_liquidity_ratio < 0:
            raise ValueError("minimum_liquidity_ratio cannot be negative")

        if trade_size <= 0:
            return {
                "valid": False,
                "reason": "non_positive_trade_size",
            }

        required_liquidity = trade_size / minimum_liquidity_ratio \
            if minimum_liquidity_ratio > 0 else float("inf")

        if available_liquidity < required_liquidity:
            return {
                "valid": False,
                "reason": "insufficient_liquidity",
            }

        return {
            "valid": True,
            "reason": None,
        }
