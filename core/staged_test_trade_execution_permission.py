"""
ArbOS™
EX-154
Staged Test Trade Execution Permission

Creates and grants a single-use execution permission for an
approved staged test-trade handoff.

This module does not execute trades or submit live orders.
"""

import math


class StagedTestTradeExecutionPermission:
    def __init__(self):
        self._counter = 0
        self._pending = {}

    def create(
        self,
        handoff_result,
    ):
        if handoff_result is None:
            raise ValueError(
                "handoff_result is required"
            )

        if handoff_result.get(
            "live_order_submitted"
        ) is True:
            return {
                "permission_granted": False,
                "status": "blocked",
                "reason": "live_order_already_submitted",
                "live_order_submitted": True,
            }

        if handoff_result.get(
            "handoff_ready"
        ) is not True:
            return {
                "permission_granted": False,
                "status": "blocked",
                "reason": "handoff_not_ready",
                "live_order_submitted": False,
            }

        identity = {}

        for field in (
            "route_id",
            "approval_id",
            "asset",
            "buy_exchange",
            "sell_exchange",
        ):
            value = handoff_result.get(field)

            if (
                not isinstance(value, str)
                or not value.strip()
            ):
                return {
                    "permission_granted": False,
                    "status": "blocked",
                    "reason": f"{field}_required",
                    "live_order_submitted": False,
                }

            normalized = value.strip()

            if field == "asset":
                normalized = normalized.upper()

            identity[field] = normalized

        raw_trade_amount = handoff_result.get(
            "trade_amount",
            0.0,
        )

        if isinstance(raw_trade_amount, bool):
            return {
                "permission_granted": False,
                "status": "blocked",
                "reason": "invalid_trade_amount",
                "live_order_submitted": False,
            }

        try:
            trade_amount = float(
                raw_trade_amount
            )
        except (
            TypeError,
            ValueError,
            OverflowError,
        ):
            return {
                "permission_granted": False,
                "status": "blocked",
                "reason": "invalid_trade_amount",
                "live_order_submitted": False,
            }

        if (
            not math.isfinite(trade_amount)
            or trade_amount <= 0
        ):
            return {
                "permission_granted": False,
                "status": "blocked",
                "reason": "invalid_trade_amount",
                "live_order_submitted": False,
            }

        self._counter += 1

        permission_id = (
            f"PERM-{self._counter:03d}"
        )

        record = {
            "permission_id": permission_id,
            "route_id": identity["route_id"],
            "approval_id": identity["approval_id"],
            "asset": identity["asset"],
            "buy_exchange": identity["buy_exchange"],
            "sell_exchange": identity["sell_exchange"],
            "trade_amount": trade_amount,
        }

        self._pending[
            permission_id
        ] = record

        return {
            **record,
            "permission_granted": False,
            "status": (
                "awaiting_execution_permission"
            ),
            "live_order_submitted": False,
        }

    def grant(
        self,
        permission_id,
        trade_amount,
    ):
        if permission_id not in self._pending:
            return {
                "permission_id": permission_id,
                "permission_granted": False,
                "status": "not_found",
                "live_order_submitted": False,
            }

        record = self._pending[
            permission_id
        ]

        expected_amount = record[
            "trade_amount"
        ]

        if isinstance(trade_amount, bool):
            return {
                **record,
                "permission_granted": False,
                "status": "blocked",
                "reason": "invalid_trade_amount",
                "live_order_submitted": False,
            }

        try:
            supplied_amount = float(
                trade_amount
            )
        except (
            TypeError,
            ValueError,
            OverflowError,
        ):
            return {
                **record,
                "permission_granted": False,
                "status": "blocked",
                "reason": "invalid_trade_amount",
                "live_order_submitted": False,
            }

        if (
            not math.isfinite(supplied_amount)
            or supplied_amount <= 0
        ):
            return {
                **record,
                "permission_granted": False,
                "status": "blocked",
                "reason": "invalid_trade_amount",
                "live_order_submitted": False,
            }

        if supplied_amount != expected_amount:
            return {
                **record,
                "permission_granted": False,
                "status": "blocked",
                "reason": "trade_amount_mismatch",
                "live_order_submitted": False,
            }

        self._pending.pop(
            permission_id,
            None,
        )

        return {
            **record,
            "permission_granted": True,
            "status": (
                "execution_permission_granted"
            ),
            "live_order_submitted": False,
        }
