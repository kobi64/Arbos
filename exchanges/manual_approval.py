"""
ArbOS™
EX-023
Manual Approval Layer

Human-in-the-loop safety checkpoint before trade execution.

Responsibilities:
- Create approval requests
- Store pending approvals
- Approve valid trades
- Reject trades with reason
"""

import math


class ManualApproval:

    _pending_requests = {}

    @classmethod
    def request(
        cls,
        asset: str,
        trade_amount: float,
        route: str,
        expected_profit: float,
        net_profit: float,
    ):
        if not isinstance(asset, str) or not asset.strip():
            raise ValueError("asset is required")

        if isinstance(trade_amount, bool):
            raise ValueError("invalid trade amount")

        try:
            trade_amount = float(trade_amount)
        except (TypeError, ValueError, OverflowError):
            raise ValueError("invalid trade amount")

        if (
            not math.isfinite(trade_amount)
            or trade_amount <= 0
        ):
            raise ValueError("invalid trade amount")

        if not isinstance(route, str) or not route.strip():
            raise ValueError("route is required")

        if (
            isinstance(expected_profit, bool)
            or isinstance(net_profit, bool)
        ):
            raise ValueError(
                "profit must be a finite non-negative number"
            )

        try:
            expected_profit = float(expected_profit)
            net_profit = float(net_profit)
        except (TypeError, ValueError, OverflowError):
            raise ValueError(
                "profit must be a finite non-negative number"
            )

        if (
            not math.isfinite(expected_profit)
            or not math.isfinite(net_profit)
            or expected_profit < 0
            or net_profit < 0
        ):
            raise ValueError(
                "profit must be a finite non-negative number"
            )

        approval_id = f"ARB-{len(cls._pending_requests) + 1:03d}"

        trade_summary = {
            "asset": asset,
            "trade_amount": trade_amount,
            "route": route,
            "expected_profit": expected_profit,
            "net_profit": net_profit,
        }

        cls._pending_requests[approval_id] = trade_summary

        return {
            "approval_id": approval_id,
            "approved": False,
            "status": "awaiting_approval",
            "trade_summary": trade_summary,
        }

    @classmethod
    def approve(cls, approval_id: str):
        if approval_id not in cls._pending_requests:
            return {
                "approved": False,
                "status": "not_found",
            }

        return {
            "approved": True,
            "status": "approved",
            "approval_id": approval_id,
            "trade_summary": cls._pending_requests[approval_id],
        }

    @classmethod
    def reject(cls, approval_id: str, reason: str):
        return {
            "approved": False,
            "status": "rejected",
            "approval_id": approval_id,
            "reason": reason,
        }
