import math

"""
ArbOS™
EX-155
Controlled Test Trade Execution Adapter

Consumes a granted staged test-trade execution permission
and applies the existing ControlledExecutionManager checks.

This adapter authorises only. It does not submit live orders.
"""

from exchanges.controlled_execution_manager import (
    ControlledExecutionManager,
)


class ControlledTestTradeExecutionAdapter:
    def __init__(
        self,
        max_trade_size=1000.0,
    ):
        self._manager = ControlledExecutionManager(
            max_trade_size=max_trade_size
        )

    def authorise(
        self,
        permission_result,
    ):
        if permission_result is None:
            raise ValueError(
                "permission_result is required"
            )

        if permission_result.get(
            "live_order_submitted"
        ) is True:
            return {
                "authorised": False,
                "reason": "live_order_already_submitted",
                "live_order_submitted": True,
            }

        identity = {}

        for field in (
            "permission_id",
            "route_id",
            "approval_id",
            "asset",
            "buy_exchange",
            "sell_exchange",
        ):
            value = permission_result.get(
                field
            )

            if (
                not isinstance(value, str)
                or not value.strip()
            ):
                return {
                    "authorised": False,
                    "reason": f"{field}_required",
                    "live_order_submitted": False,
                }

            normalized = value.strip()

            if field == "asset":
                normalized = normalized.upper()

            identity[field] = normalized

        raw_trade_amount = permission_result.get(
            "trade_amount",
            0.0,
        )

        if isinstance(raw_trade_amount, bool):
            return {
                "authorised": False,
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
                "authorised": False,
                "reason": "invalid_trade_amount",
                "live_order_submitted": False,
            }

        if (
            not math.isfinite(trade_amount)
            or trade_amount <= 0
        ):
            return {
                "authorised": False,
                "reason": "invalid_trade_amount",
                "live_order_submitted": False,
            }

        permission_granted = (
            permission_result.get(
                "permission_granted"
            ) is True
            and permission_result.get(
                "status"
            ) == "execution_permission_granted"
        )

        self._manager.set_trade_ready(True)
        self._manager.set_approved(True)
        self._manager.set_execution_permission(
            permission_granted
        )

        execution = self._manager.execute(
            trade_size=trade_amount
        )

        return {
            "authorised": bool(
                execution.get("executed")
            ),
            "reason": execution.get(
                "reason"
            ),
            "permission_id": identity["permission_id"],
            "route_id": identity["route_id"],
            "approval_id": identity["approval_id"],
            "asset": identity["asset"],
            "buy_exchange": identity[
                "buy_exchange"
            ],
            "sell_exchange": identity[
                "sell_exchange"
            ],
            "trade_amount": trade_amount,
            "live_order_submitted": False,
        }
