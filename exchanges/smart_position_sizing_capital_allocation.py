"""
ArbOS™
EX-095
Smart Position Sizing & Capital Allocation Engine
"""

import math


class SmartPositionSizingCapitalAllocation:
    def calculate(
        self,
        available_balance,
        risk_maximum_trade,
        user_trade_cap,
        liquidity_trade_cap,
        min_trade_size,
        quantity_step,
    ):
        if available_balance <= 0:
            raise ValueError("available_balance must be positive")

        if quantity_step <= 0:
            raise ValueError("quantity_step must be positive")

        caps = {
            "available_balance": float(available_balance),
            "risk_maximum_trade": float(risk_maximum_trade),
            "user_trade_cap": float(user_trade_cap),
            "liquidity_trade_cap": float(liquidity_trade_cap),
        }

        limiting_factor = min(caps, key=caps.get)
        raw_trade_size = caps[limiting_factor]

        steps = math.floor(raw_trade_size / quantity_step)
        recommended_trade_size = steps * quantity_step
        recommended_trade_size = round(recommended_trade_size, 12)

        if recommended_trade_size < min_trade_size:
            return {
                "valid": False,
                "reason": "below_minimum_trade_size",
                "recommended_trade_size": recommended_trade_size,
                "limiting_factor": limiting_factor,
            }

        return {
            "valid": True,
            "reason": None,
            "recommended_trade_size": recommended_trade_size,
            "limiting_factor": limiting_factor,
        }
