"""
ArbOS™
EX-153
Approved Test Trade Handoff

Validates that an explicitly approved staged test trade
matches the prepared trade package and is ready to be
handed to the later execution boundary.

This module does not submit live orders.
"""


class ApprovedTestTradeHandoff:
    def prepare(
        self,
        staged_package,
        approval_result,
    ):
        if staged_package is None:
            raise ValueError(
                "staged_package is required"
            )

        if approval_result is None:
            raise ValueError(
                "approval_result is required"
            )

        if staged_package.get(
            "live_order_submitted"
        ) is True:
            return {
                "handoff_ready": False,
                "reason": "live_order_already_submitted",
                "live_order_submitted": True,
            }

        if staged_package.get("prepared") is not True:
            return {
                "handoff_ready": False,
                "reason": "test_trade_package_not_prepared",
                "live_order_submitted": False,
            }

        if (
            approval_result.get("approved") is not True
            or approval_result.get("status") != "approved"
        ):
            return {
                "handoff_ready": False,
                "reason": "manual_approval_required",
                "live_order_submitted": False,
            }

        trade_package = staged_package.get(
            "trade_package",
            {},
        )

        trade = trade_package.get(
            "trade",
            {},
        )

        approval_summary = approval_result.get(
            "trade_summary",
            {},
        )

        prepared_amount = float(
            trade.get(
                "trade_amount",
                0.0,
            )
        )

        approved_amount = float(
            approval_summary.get(
                "trade_amount",
                0.0,
            )
        )

        if prepared_amount != approved_amount:
            return {
                "handoff_ready": False,
                "reason": "approved_trade_amount_mismatch",
                "live_order_submitted": False,
            }

        prepared_asset = str(
            trade.get(
                "asset",
                "",
            )
        ).strip().upper()

        approved_asset = str(
            approval_summary.get(
                "asset",
                "",
            )
        ).strip().upper()

        if prepared_asset != approved_asset:
            return {
                "handoff_ready": False,
                "reason": "approved_asset_mismatch",
                "live_order_submitted": False,
            }

        return {
            "handoff_ready": True,
            "reason": "approved_test_trade_ready",
            "route_id": staged_package.get(
                "route_id"
            ),
            "route_type": staged_package.get(
                "route_type"
            ),
            "approval_id": approval_result.get(
                "approval_id"
            ),
            "asset": prepared_asset,
            "trade_amount": prepared_amount,
            "trade_package": trade_package,
            "live_order_submitted": False,
        }
