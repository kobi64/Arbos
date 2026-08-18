"""
ArbOS™
EX-157
Controlled Test Trade Order Submission Boundary

Accepts an authorised staged test-trade order intent and
creates an internal ArbOS order record only.

This module does not submit live exchange orders.
"""

import math

from exchanges.exchange_order_management_engine import (
    ExchangeOrderManagementEngine,
)


class ControlledTestTradeOrderSubmissionBoundary:
    def __init__(self):
        self._orders = ExchangeOrderManagementEngine()
        self._consumed_intents = set()
        self._destination_bindings = {}

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

        identity = {}

        for field in (
            "route_id",
            "approval_id",
            "permission_id",
            "asset",
        ):
            value = order_intent.get(
                field
            )

            if (
                not isinstance(value, str)
                or not value.strip()
            ):
                return {
                    "accepted": False,
                    "reason": f"{field}_required",
                    "live_order_submitted": False,
                }

            normalized = value.strip()

            if field == "asset":
                normalized = normalized.upper()

            identity[field] = normalized

        destination = {}

        for field in (
            "exchange",
            "symbol",
            "buy_exchange",
            "sell_exchange",
        ):
            value = order_intent.get(
                field
            )

            if (
                not isinstance(value, str)
                or not value.strip()
            ):
                return {
                    "accepted": False,
                    "reason": f"{field}_required",
                    "live_order_submitted": False,
                }

            normalized = value.strip()

            if field in (
                "exchange",
                "buy_exchange",
                "sell_exchange",
                "symbol",
            ):
                normalized = normalized.upper()

            destination[field] = normalized

        side_value = order_intent.get(
            "side"
        )

        if (
            not isinstance(side_value, str)
            or not side_value.strip()
        ):
            return {
                "accepted": False,
                "reason": "side_required",
                "live_order_submitted": False,
            }

        side = side_value.strip().upper()

        exchange = destination["exchange"]
        buy_exchange = destination["buy_exchange"]
        sell_exchange = destination["sell_exchange"]

        if (
            side == "BUY"
            and exchange != buy_exchange
        ):
            return {
                "accepted": False,
                "reason": "buy_exchange_mismatch",
                "live_order_submitted": False,
            }

        if (
            side == "SELL"
            and exchange != sell_exchange
        ):
            return {
                "accepted": False,
                "reason": "sell_exchange_mismatch",
                "live_order_submitted": False,
            }

        raw_amount = order_intent.get(
            "amount",
            0.0,
        )

        if isinstance(raw_amount, bool):
            return {
                "accepted": False,
                "reason": "invalid_order_amount",
                "live_order_submitted": False,
            }

        try:
            amount = float(
                raw_amount
            )
        except (
            TypeError,
            ValueError,
            OverflowError,
        ):
            return {
                "accepted": False,
                "reason": "invalid_order_amount",
                "live_order_submitted": False,
            }

        if (
            not math.isfinite(amount)
            or amount <= 0
        ):
            return {
                "accepted": False,
                "reason": "invalid_order_amount",
                "live_order_submitted": False,
            }

        symbol = destination["symbol"]

        intent_key = (
            identity["route_id"],
            identity["approval_id"],
            identity["permission_id"],
            exchange,
            symbol,
            side,
            amount,
        )

        if intent_key in self._consumed_intents:
            return {
                "accepted": False,
                "reason": "duplicate_order_intent_blocked",
                "live_order_submitted": False,
            }

        order = self._orders.create_order(
            exchange=exchange,
            symbol=symbol,
            side=side,
            amount=amount,
        )

        self._destination_bindings[
            order["order_id"]
        ] = {
            "exchange": exchange,
            "buy_exchange": buy_exchange,
            "sell_exchange": sell_exchange,
        }

        self._consumed_intents.add(
            intent_key
        )

        return {
            "accepted": True,
            "reason": "test_trade_order_record_created",
            "order_id": order["order_id"],
            "route_id": identity["route_id"],
            "approval_id": identity["approval_id"],
            "permission_id": identity["permission_id"],
            "test_trade": True,
            "live_order_submitted": False,
        }

    def get_order(
        self,
        order_id,
    ):
        order = self._orders.get_order(
            order_id
        )

        if order is None:
            return None

        binding = self._destination_bindings.get(
            order_id
        )

        if binding is None:
            return order

        result = dict(order)
        result.update(binding)

        return result
