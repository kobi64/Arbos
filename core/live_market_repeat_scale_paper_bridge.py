"""
ArbOS™
EX-170
Live Market Repeat / Scale Paper Bridge

Bridges a freshly granted repeat/scale staged-test execution
permission into the existing live-market paper execution engine.

Real market prices may be consumed.
Execution remains simulated and paper-only.

This module never submits a live exchange order.
"""

from exchanges.live_market_paper_bridge import (
    LiveMarketPaperBridge,
)


class LiveMarketRepeatScalePaperBridge:
    def __init__(self, market_data_provider):
        if market_data_provider is None:
            raise ValueError(
                "market_data_provider is required"
            )

        self._bridge = LiveMarketPaperBridge(
            market_data_provider
        )
        self._history = []

    def execute(
        self,
        permission_result,
        order,
    ):
        if permission_result is None:
            raise ValueError(
                "permission_result is required"
            )

        if order is None:
            raise ValueError(
                "order is required"
            )

        if permission_result.get(
            "live_order_submitted"
        ) is True:
            return self._blocked(
                "live_order_already_submitted"
            )

        if permission_result.get(
            "permission_granted"
        ) is not True:
            return self._blocked(
                "execution_permission_required"
            )

        if (
            permission_result.get("status")
            != "execution_permission_granted"
        ):
            return self._blocked(
                "execution_permission_status_required"
            )

        permission_id = permission_result.get(
            "permission_id"
        )

        if (
            permission_id is None
            or not str(permission_id).strip()
        ):
            return self._blocked(
                "permission_id_required"
            )

        approval_id = permission_result.get(
            "approval_id"
        )

        if (
            approval_id is None
            or not str(approval_id).strip()
        ):
            return self._blocked(
                "approval_id_required"
            )

        permitted_amount = float(
            permission_result.get(
                "trade_amount",
                0.0,
            )
        )

        if permitted_amount <= 0:
            return self._blocked(
                "invalid_permitted_trade_amount"
            )

        try:
            order_amount = float(
                order.get(
                    "trade_amount",
                    order.get("quantity"),
                )
            )
        except (TypeError, ValueError):
            order_amount = 0.0

        if order_amount <= 0:
            return self._blocked(
                "invalid_order_trade_amount"
            )

        if order_amount != permitted_amount:
            return self._blocked(
                "permitted_trade_amount_mismatch"
            )

        symbol = order.get("symbol")

        if (
            symbol is None
            or not str(symbol).strip()
        ):
            raise ValueError(
                "symbol is required"
            )

        side = str(
            order.get("side", "")
        ).strip().lower()

        if side not in {
            "buy",
            "sell",
        }:
            raise ValueError(
                "valid side is required"
            )

        paper_order = dict(order)
        paper_order["symbol"] = (
            str(symbol).strip().upper()
        )
        paper_order["side"] = side
        paper_order["quantity"] = order_amount
        paper_order["trade_amount"] = (
            order_amount
        )
        paper_order["approval_id"] = (
            approval_id
        )
        paper_order["permission_id"] = (
            permission_id
        )
        paper_order["test_trade"] = True
        paper_order["simulated"] = True
        paper_order["paper_trade"] = True
        paper_order["live_order_submitted"] = False

        execution = self._bridge.execute(
            paper_order
        )

        if execution.get(
            "live_order_submitted"
        ) is True:
            return self._blocked(
                "paper_boundary_violated"
            )

        record = {
            "executed": True,
            "paper_only": True,
            "reason": (
                "live_market_repeat_scale_paper_executed"
            ),
            "approval_id": approval_id,
            "permission_id": permission_id,
            "trade_amount": permitted_amount,
            "symbol": paper_order["symbol"],
            "side": side,
            "market_price": execution.get(
                "market_price"
            ),
            "execution": execution,
            "test_trade": True,
            "simulated": True,
            "paper_trade": True,
            "live_order_submitted": False,
        }

        self._history.append(
            dict(record)
        )

        return dict(record)

    def history(self):
        return [
            dict(record)
            for record in self._history
        ]

    @staticmethod
    def _blocked(reason):
        return {
            "executed": False,
            "paper_only": True,
            "reason": reason,
            "test_trade": True,
            "simulated": True,
            "paper_trade": True,
            "live_order_submitted": False,
        }
