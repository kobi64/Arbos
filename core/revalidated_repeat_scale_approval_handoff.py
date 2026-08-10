"""
ArbOS™
EX-166
Revalidated Repeat / Scale Approval Handoff

Converts a successful fresh repeat/scale revalidation into a
new manual-approval request.

Previous approval and permission identifiers are retained only
for audit lineage. They do not authorize the new trade.

This module does not approve, authorize, or submit orders.
"""


class RevalidatedRepeatScaleApprovalHandoff:
    def prepare(
        self,
        revalidation_result,
        asset,
        buy_exchange,
        sell_exchange,
        expected_profit,
        estimated_fees,
        slippage_allowance,
    ):
        if revalidation_result is None:
            raise ValueError(
                "revalidation_result is required"
            )

        if revalidation_result.get(
            "live_order_submitted"
        ) is True:
            return {
                "prepared": False,
                "approval_ready": False,
                "reason": "live_order_already_submitted",
                "live_order_submitted": True,
            }

        if revalidation_result.get(
            "revalidated"
        ) is not True:
            return {
                "prepared": False,
                "approval_ready": False,
                "reason": "fresh_revalidation_required",
                "live_order_submitted": False,
            }

        if revalidation_result.get(
            "allowed"
        ) is not True:
            return {
                "prepared": False,
                "approval_ready": False,
                "reason": "revalidated_trade_not_allowed",
                "live_order_submitted": False,
            }

        if revalidation_result.get(
            "status"
        ) != "REVALIDATED":
            return {
                "prepared": False,
                "approval_ready": False,
                "reason": "revalidated_status_required",
                "live_order_submitted": False,
            }

        if revalidation_result.get(
            "fresh_approval_required"
        ) is not True:
            return {
                "prepared": False,
                "approval_ready": False,
                "reason": "fresh_approval_requirement_missing",
                "live_order_submitted": False,
            }

        if revalidation_result.get(
            "approval_granted"
        ) is True:
            return {
                "prepared": False,
                "approval_ready": False,
                "reason": "fresh_approval_must_be_ungranted",
                "live_order_submitted": False,
            }

        if revalidation_result.get(
            "permission_granted"
        ) is True:
            return {
                "prepared": False,
                "approval_ready": False,
                "reason": "execution_permission_must_be_ungranted",
                "live_order_submitted": False,
            }

        trade_amount = float(
            revalidation_result.get(
                "next_trade_size",
                0.0,
            )
        )

        if trade_amount <= 0:
            return {
                "prepared": False,
                "approval_ready": False,
                "reason": "invalid_trade_amount",
                "live_order_submitted": False,
            }

        asset = str(asset).strip().upper()
        buy_exchange = str(
            buy_exchange
        ).strip()
        sell_exchange = str(
            sell_exchange
        ).strip()

        if not asset:
            raise ValueError(
                "asset is required"
            )

        if not buy_exchange:
            raise ValueError(
                "buy_exchange is required"
            )

        if not sell_exchange:
            raise ValueError(
                "sell_exchange is required"
            )

        approval_request = {
            "route_id": revalidation_result.get(
                "route_id"
            ),
            "decision": revalidation_result.get(
                "decision"
            ),
            "asset": asset,
            "buy_exchange": buy_exchange,
            "sell_exchange": sell_exchange,
            "trade_amount": trade_amount,
            "expected_profit": float(
                expected_profit
            ),
            "estimated_fees": float(
                estimated_fees
            ),
            "slippage_allowance": float(
                slippage_allowance
            ),
            "network": revalidation_result.get(
                "network"
            ),
            "withdraw_fee": revalidation_result.get(
                "withdraw_fee"
            ),
            "transfer_net_amount": (
                revalidation_result.get(
                    "transfer_net_amount"
                )
            ),
        }

        return {
            "prepared": True,
            "approval_ready": True,
            "reason": (
                "fresh_repeat_scale_approval_ready"
            ),
            "route_id": revalidation_result.get(
                "route_id"
            ),
            "decision": revalidation_result.get(
                "decision"
            ),
            "trade_amount": trade_amount,
            "approval_request": approval_request,
            "previous_approval_id": (
                revalidation_result.get(
                    "previous_approval_id"
                )
            ),
            "previous_permission_id": (
                revalidation_result.get(
                    "previous_permission_id"
                )
            ),
            "manual_approval_required": True,
            "fresh_approval_required": True,
            "approval_granted": False,
            "fresh_execution_permission_required": True,
            "permission_granted": False,
            "test_trade": True,
            "simulated": True,
            "live_order_submitted": False,
        }
