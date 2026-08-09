"""
ArbOS™
EX-157
Controlled Test Trade Order Submission Boundary

Accepts an authorised staged test-trade order intent and
creates an internal ArbOS order record only.

This module does not submit live exchange orders.
"""

from exchanges.exchange_order_management_engine import (
    ExchangeOrderManagementEngine,
)


class ControlledTestTradeOrderSubmissionBoundary:
    def __init__(self):
        self._orders = ExchangeOrderManagementEngine()
        self._consumed_intents = set()

    def submit(
        self,
        order_intent,
    ):
        if order_intent is None:
            raise ValueError(
                "order_intent is required"
            )

        if order_intent.get(
            "live_order_submitted"
        ) is True:
            return {
                "accepted": False,
                "reason": "live_order_already_submitted",
                "live_order_submitted": True,
            }

        if order_intent.get(
            "intent_ready"
        ) is not True:
            return {
                "accepted": False,
                "reason": "order_intent_not_ready",
                "live_order_submitted": False,
            }

        if order_intent.get(
            "test_trade"
        ) is not True:
            return {
                "accepted": False,
                "reason": "test_trade_required",
                "live_order_submitted": False,
            }

        intent_key = (
            order_intent.get("route_id"),
            order_intent.get("approval_id"),
            order_intent.get("permission_id"),
            order_intent.get("exchange"),
            order_intent.get("symbol"),
            order_intent.get("side"),
            float(
                order_intent.get(
                    "amount",
                    0.0,
                )
            ),
        )

        if intent_key in self._consumed_intents:
            return {
                "accepted": False,
                "reason": "duplicate_order_intent_blocked",
                "live_order_submitted": False,
            }

        exchange = str(
            order_intent.get(
                "exchange",
                "",
            )
        ).strip()

        symbol = str(
            order_intent.get(
                "symbol",
                "",
            )
        ).strip().upper()

        side = str(
            order_intent.get(
                "side",
                "",
            )
        ).strip().upper()

        amount = float(
            order_intent.get(
                "amount",
                0.0,
            )
        )

        order = self._orders.create_order(
            exchange=exchange,
            symbol=symbol,
            side=side,
            amount=amount,
        )

        self._consumed_intents.add(
            intent_key
        )

        return {
            "accepted": True,
            "reason": "test_trade_order_record_created",
            "order_id": order["order_id"],
            "route_id": order_intent.get(
                "route_id"
            ),
            "approval_id": order_intent.get(
                "approval_id"
            ),
            "permission_id": order_intent.get(
                "permission_id"
            ),
            "test_trade": True,
            "live_order_submitted": False,
        }

    def get_order(
        self,
        order_id,
    ):
        return self._orders.get_order(
            order_id
        )
