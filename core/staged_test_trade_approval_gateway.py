"""
ArbOS™
EX-152
Staged Test Trade Approval Gateway

Creates and manages the manual approval checkpoint for a
prepared staged validation trade.

This module does not submit live orders.
"""

from exchanges.manual_approval import (
    ManualApproval,
)


class StagedTestTradeApprovalGateway:
    def __init__(self):
        self._pending_approval_ids = set()

    def request(
        self,
        staged_package,
    ):
        if staged_package is None:
            raise ValueError(
                "staged_package is required"
            )

        if staged_package.get("prepared") is not True:
            return {
                "approved": False,
                "status": "blocked",
                "reason": (
                    "test_trade_package_not_prepared"
                ),
                "live_order_submitted": False,
            }

        if staged_package.get(
            "live_order_submitted"
        ) is True:
            return {
                "approved": False,
                "status": "blocked",
                "reason": (
                    "live_order_already_submitted"
                ),
                "live_order_submitted": True,
            }

        trade_package = staged_package.get(
            "trade_package",
            {},
        )

        trade = trade_package.get(
            "trade",
            {},
        )

        asset = str(
            trade.get("asset", "")
        ).strip().upper()

        buy_exchange = str(
            trade.get(
                "buy_exchange",
                "",
            )
        ).strip()

        sell_exchange = str(
            trade.get(
                "sell_exchange",
                "",
            )
        ).strip()

        route = (
            f"{buy_exchange} -> "
            f"{sell_exchange}"
        )

        result = ManualApproval.request(
            asset=asset,
            trade_amount=float(
                trade.get(
                    "trade_amount",
                    0.0,
                )
            ),
            route=route,
            expected_profit=float(
                trade.get(
                    "expected_profit",
                    0.0,
                )
            ),
            net_profit=float(
                trade.get(
                    "net_profit",
                    0.0,
                )
            ),
        )

        self._pending_approval_ids.add(
            result["approval_id"]
        )

        return {
            **result,
            "route_id": staged_package.get(
                "route_id"
            ),
            "route_type": staged_package.get(
                "route_type"
            ),
            "live_order_submitted": False,
        }

    def approve(
        self,
        approval_id,
    ):
        if approval_id not in self._pending_approval_ids:
            return {
                "approved": False,
                "status": "not_found",
                "approval_id": approval_id,
                "live_order_submitted": False,
            }

        result = ManualApproval.approve(
            approval_id=approval_id
        )

        if result.get("approved") is True:
            self._pending_approval_ids.discard(
                approval_id
            )

        return {
            **result,
            "live_order_submitted": False,
        }

    def reject(
        self,
        approval_id,
        reason,
    ):
        if approval_id not in self._pending_approval_ids:
            return {
                "approved": False,
                "status": "not_found",
                "approval_id": approval_id,
                "live_order_submitted": False,
            }

        result = ManualApproval.reject(
            approval_id=approval_id,
            reason=reason,
        )

        self._pending_approval_ids.discard(
            approval_id
        )

        return {
            **result,
            "live_order_submitted": False,
        }
