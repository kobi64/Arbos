"""
ArbOS™
EX-156
Controlled Test Trade Order Intent

Builds an inspectable order intent from an authorised staged
test trade.

This module does not submit live orders.
"""


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

        side = str(side).strip().lower()

        if side not in self.VALID_SIDES:
            raise ValueError(
                "side must be buy or sell"
            )

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

        return {
            "intent_ready": True,
            "reason": "order_intent_ready",
            "exchange": str(exchange).strip(),
            "symbol": str(symbol).strip().upper(),
            "side": side,
            "amount": float(
                execution_result.get(
                    "trade_amount",
                    0.0,
                )
            ),
            "asset": execution_result.get(
                "asset"
            ),
            "route_id": execution_result.get(
                "route_id"
            ),
            "approval_id": execution_result.get(
                "approval_id"
            ),
            "permission_id": execution_result.get(
                "permission_id"
            ),
            "test_trade": True,
            "live_order_submitted": False,
        }
