"""
ArbOS™
EX-156
Controlled Test Trade Order Intent

Builds an inspectable order intent from an authorised staged
test trade.

This module does not submit live orders.
"""

import math


class ControlledTestTradeOrderIntent:
    VALID_SIDES = {
        "buy",
        "sell",
    }

    def build(
        self,
        execution_result,
        exchange,
        symbol,
        side,
    ):
        if execution_result is None:
            raise ValueError(
                "execution_result is required"
            )

        if not isinstance(side, str):
            raise ValueError(
                "side must be buy or sell"
            )

        side = side.strip().lower()

        if side not in self.VALID_SIDES:
            raise ValueError(
                "side must be buy or sell"
            )

        if (
            not isinstance(exchange, str)
            or not exchange.strip()
        ):
            raise ValueError(
                "exchange is required"
            )

        if (
            not isinstance(symbol, str)
            or not symbol.strip()
        ):
            raise ValueError(
                "symbol is required"
            )

        exchange = exchange.strip()
        symbol = symbol.strip().upper()

        if execution_result.get(
            "live_order_submitted"
        ) is True:
            return {
                "intent_ready": False,
                "reason": "live_order_already_submitted",
                "live_order_submitted": True,
            }

        if execution_result.get(
            "authorised"
        ) is not True:
            return {
                "intent_ready": False,
                "reason": "execution_not_authorised",
                "live_order_submitted": False,
            }

        identity = {}

        for field in (
            "route_id",
            "approval_id",
            "permission_id",
            "asset",
        ):
            value = execution_result.get(
                field
            )

            if (
                not isinstance(value, str)
                or not value.strip()
            ):
                return {
                    "intent_ready": False,
                    "reason": f"{field}_required",
                    "live_order_submitted": False,
                }

            normalized = value.strip()

            if field == "asset":
                normalized = normalized.upper()

            identity[field] = normalized

        raw_trade_amount = execution_result.get(
            "trade_amount",
            0.0,
        )

        if isinstance(raw_trade_amount, bool):
            return {
                "intent_ready": False,
                "reason": "invalid_trade_amount",
                "live_order_submitted": False,
            }

        try:
            amount = float(
                raw_trade_amount
            )
        except (
            TypeError,
            ValueError,
            OverflowError,
        ):
            return {
                "intent_ready": False,
                "reason": "invalid_trade_amount",
                "live_order_submitted": False,
            }

        if (
            not math.isfinite(amount)
            or amount <= 0
        ):
            return {
                "intent_ready": False,
                "reason": "invalid_trade_amount",
                "live_order_submitted": False,
            }

        return {
            "intent_ready": True,
            "reason": "order_intent_ready",
            "exchange": exchange,
            "symbol": symbol,
            "side": side,
            "amount": amount,
            "asset": identity["asset"],
            "route_id": identity["route_id"],
            "approval_id": identity["approval_id"],
            "permission_id": identity["permission_id"],
            "test_trade": True,
            "live_order_submitted": False,
        }
