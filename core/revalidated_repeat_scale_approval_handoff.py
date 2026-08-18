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


import math


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

        raw_trade_amount = revalidation_result.get(
            "next_trade_size",
            0.0,
        )

        if isinstance(raw_trade_amount, bool):
            return {
                "prepared": False,
                "approval_ready": False,
                "reason": "invalid_trade_amount",
                "live_order_submitted": False,
            }

        try:
            trade_amount = float(raw_trade_amount)
        except (TypeError, ValueError, OverflowError):
            return {
                "prepared": False,
                "approval_ready": False,
                "reason": "invalid_trade_amount",
                "live_order_submitted": False,
            }

        if (
            not math.isfinite(trade_amount)
            or trade_amount <= 0
        ):
            return {
                "prepared": False,
                "approval_ready": False,
                "reason": "invalid_trade_amount",
                "live_order_submitted": False,
            }

        def finite_number(
            value,
            field,
            *,
            non_negative=False,
        ):
            requirement = (
                "finite non-negative number"
                if non_negative
                else "finite number"
            )

            if isinstance(value, bool):
                raise ValueError(
                    f"{field} must be a {requirement}"
                )

            try:
                number = float(value)
            except (
                TypeError,
                ValueError,
                OverflowError,
            ):
                raise ValueError(
                    f"{field} must be a {requirement}"
                ) from None

            if not math.isfinite(number):
                raise ValueError(
                    f"{field} must be a {requirement}"
                )

            if non_negative and number < 0:
                raise ValueError(
                    f"{field} must be a {requirement}"
                )

            return number

        expected_profit = finite_number(
            expected_profit,
            "expected_profit",
        )
        if expected_profit <= 0:
            return {
                "prepared": False,
                "approval_ready": False,
                "reason": "non_positive_expected_profit",
                "live_order_submitted": False,
            }

        estimated_fees = finite_number(
            estimated_fees,
            "estimated_fees",
            non_negative=True,
        )
        slippage_allowance = finite_number(
            slippage_allowance,
            "slippage_allowance",
            non_negative=True,
        )

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

        raw_route_id = revalidation_result.get(
            "route_id"
        )

        if (
            not isinstance(raw_route_id, str)
            or not raw_route_id.strip()
        ):
            return {
                "prepared": False,
                "approval_ready": False,
                "reason": "route_id_required",
                "live_order_submitted": False,
            }

        route_id = raw_route_id.strip()

        raw_previous_approval_id = (
            revalidation_result.get(
                "previous_approval_id"
            )
        )
        raw_previous_permission_id = (
            revalidation_result.get(
                "previous_permission_id"
            )
        )

        if (
            not isinstance(
                raw_previous_approval_id,
                str,
            )
            or not raw_previous_approval_id.strip()
            or not isinstance(
                raw_previous_permission_id,
                str,
            )
            or not raw_previous_permission_id.strip()
        ):
            return {
                "prepared": False,
                "approval_ready": False,
                "reason": (
                    "invalid_previous_authorization_identity"
                ),
                "live_order_submitted": False,
            }

        previous_approval_id = (
            raw_previous_approval_id.strip()
        )
        previous_permission_id = (
            raw_previous_permission_id.strip()
        )

        approval_request = {
            "route_id": route_id,
            "decision": revalidation_result.get(
                "decision"
            ),
            "asset": asset,
            "buy_exchange": buy_exchange,
            "sell_exchange": sell_exchange,
            "trade_amount": trade_amount,
            "expected_profit": expected_profit,
            "estimated_fees": estimated_fees,
            "slippage_allowance": slippage_allowance,
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
            "route_id": route_id,
            "decision": revalidation_result.get(
                "decision"
            ),
            "trade_amount": trade_amount,
            "approval_request": approval_request,
            "previous_approval_id": (
                previous_approval_id
            ),
            "previous_permission_id": (
                previous_permission_id
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
