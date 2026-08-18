"""
ArbOS™
EX-167
Fresh Repeat / Scale Execution Permission Handoff

Validates a fresh manual approval for a revalidated repeat or
scaled staged test trade and prepares the exact handoff shape
required by the existing single-use execution permission gate.

Previous approval and permission identifiers are audit lineage
only and cannot authorize this trade.

This module does not grant execution permission or submit orders.
"""

import math


class FreshRepeatScaleExecutionPermissionHandoff:
    def prepare(
        self,
        approval_handoff,
        approval_result,
    ):
        if approval_handoff is None:
            raise ValueError(
                "approval_handoff is required"
            )

        if approval_result is None:
            raise ValueError(
                "approval_result is required"
            )

        if approval_handoff.get(
            "live_order_submitted"
        ) is True:
            return {
                "handoff_ready": False,
                "reason": "live_order_already_submitted",
                "live_order_submitted": True,
            }

        if approval_handoff.get(
            "prepared"
        ) is not True:
            return {
                "handoff_ready": False,
                "reason": "approval_handoff_not_prepared",
                "live_order_submitted": False,
            }

        if approval_handoff.get(
            "approval_ready"
        ) is not True:
            return {
                "handoff_ready": False,
                "reason": "fresh_approval_not_ready",
                "live_order_submitted": False,
            }

        if approval_handoff.get(
            "fresh_approval_required"
        ) is not True:
            return {
                "handoff_ready": False,
                "reason": "fresh_approval_requirement_missing",
                "live_order_submitted": False,
            }

        if approval_handoff.get(
            "fresh_execution_permission_required"
        ) is not True:
            return {
                "handoff_ready": False,
                "reason": (
                    "fresh_execution_permission_requirement_missing"
                ),
                "live_order_submitted": False,
            }

        if (
            approval_result.get("approved") is not True
            or approval_result.get("status") != "approved"
        ):
            return {
                "handoff_ready": False,
                "reason": "fresh_manual_approval_required",
                "live_order_submitted": False,
            }

        request = approval_handoff.get(
            "approval_request",
            {},
        )

        approval_summary = approval_result.get(
            "trade_summary",
            {},
        )

        raw_requested_amount = request.get(
            "trade_amount",
            0.0,
        )

        if isinstance(raw_requested_amount, bool):
            return {
                "handoff_ready": False,
                "reason": "invalid_requested_trade_amount",
                "live_order_submitted": False,
            }

        try:
            requested_amount = float(
                raw_requested_amount
            )
        except (
            TypeError,
            ValueError,
            OverflowError,
        ):
            return {
                "handoff_ready": False,
                "reason": "invalid_requested_trade_amount",
                "live_order_submitted": False,
            }

        if (
            not math.isfinite(requested_amount)
            or requested_amount <= 0
        ):
            return {
                "handoff_ready": False,
                "reason": "invalid_requested_trade_amount",
                "live_order_submitted": False,
            }

        raw_approved_amount = approval_summary.get(
            "trade_amount",
            0.0,
        )

        if isinstance(raw_approved_amount, bool):
            return {
                "handoff_ready": False,
                "reason": "invalid_approved_trade_amount",
                "live_order_submitted": False,
            }

        try:
            approved_amount = float(
                raw_approved_amount
            )
        except (
            TypeError,
            ValueError,
            OverflowError,
        ):
            return {
                "handoff_ready": False,
                "reason": "invalid_approved_trade_amount",
                "live_order_submitted": False,
            }

        if (
            not math.isfinite(approved_amount)
            or approved_amount <= 0
        ):
            return {
                "handoff_ready": False,
                "reason": "invalid_approved_trade_amount",
                "live_order_submitted": False,
            }

        if requested_amount != approved_amount:
            return {
                "handoff_ready": False,
                "reason": "approved_trade_amount_mismatch",
                "live_order_submitted": False,
            }

        raw_requested_asset = request.get(
            "asset",
            "",
        )

        if not isinstance(
            raw_requested_asset,
            str,
        ):
            return {
                "handoff_ready": False,
                "reason": "requested_asset_required",
                "live_order_submitted": False,
            }

        requested_asset = (
            raw_requested_asset.strip().upper()
        )

        if not requested_asset:
            return {
                "handoff_ready": False,
                "reason": "requested_asset_required",
                "live_order_submitted": False,
            }

        raw_approved_asset = approval_summary.get(
            "asset",
            "",
        )

        if not isinstance(
            raw_approved_asset,
            str,
        ):
            return {
                "handoff_ready": False,
                "reason": "approved_asset_mismatch",
                "live_order_submitted": False,
            }

        approved_asset = (
            raw_approved_asset.strip().upper()
        )

        if requested_asset != approved_asset:
            return {
                "handoff_ready": False,
                "reason": "approved_asset_mismatch",
                "live_order_submitted": False,
            }

        raw_requested_buy_exchange = request.get(
            "buy_exchange",
            "",
        )

        if not isinstance(
            raw_requested_buy_exchange,
            str,
        ):
            return {
                "handoff_ready": False,
                "reason": "requested_buy_exchange_required",
                "live_order_submitted": False,
            }

        requested_buy_exchange = (
            raw_requested_buy_exchange.strip()
        )

        if not requested_buy_exchange:
            return {
                "handoff_ready": False,
                "reason": "requested_buy_exchange_required",
                "live_order_submitted": False,
            }

        raw_requested_sell_exchange = request.get(
            "sell_exchange",
            "",
        )

        if not isinstance(
            raw_requested_sell_exchange,
            str,
        ):
            return {
                "handoff_ready": False,
                "reason": "requested_sell_exchange_required",
                "live_order_submitted": False,
            }

        requested_sell_exchange = (
            raw_requested_sell_exchange.strip()
        )

        if not requested_sell_exchange:
            return {
                "handoff_ready": False,
                "reason": "requested_sell_exchange_required",
                "live_order_submitted": False,
            }

        raw_approved_route = approval_summary.get(
            "route",
            "",
        )

        if not isinstance(
            raw_approved_route,
            str,
        ):
            return {
                "handoff_ready": False,
                "reason": "approved_route_required",
                "live_order_submitted": False,
            }

        approved_route = raw_approved_route.strip()

        if not approved_route:
            return {
                "handoff_ready": False,
                "reason": "approved_route_required",
                "live_order_submitted": False,
            }

        route_parts = [
            part.strip()
            for part in approved_route.split("->")
        ]

        if (
            len(route_parts) != 2
            or not route_parts[0]
            or not route_parts[1]
        ):
            return {
                "handoff_ready": False,
                "reason": "approved_route_required",
                "live_order_submitted": False,
            }

        approved_buy_exchange = route_parts[0]
        approved_sell_exchange = route_parts[1]

        if (
            requested_buy_exchange
            != approved_buy_exchange
        ):
            return {
                "handoff_ready": False,
                "reason": "approved_buy_exchange_mismatch",
                "live_order_submitted": False,
            }

        if (
            requested_sell_exchange
            != approved_sell_exchange
        ):
            return {
                "handoff_ready": False,
                "reason": "approved_sell_exchange_mismatch",
                "live_order_submitted": False,
            }

        raw_route_id = approval_handoff.get(
            "route_id"
        )

        if not isinstance(raw_route_id, str):
            return {
                "handoff_ready": False,
                "reason": "route_id_required",
                "live_order_submitted": False,
            }

        route_id = raw_route_id.strip()

        if not route_id:
            return {
                "handoff_ready": False,
                "reason": "route_id_required",
                "live_order_submitted": False,
            }

        raw_approved_route_id = approval_result.get(
            "route_id",
            route_id,
        )

        approved_route_id = (
            raw_approved_route_id.strip()
            if isinstance(raw_approved_route_id, str)
            else raw_approved_route_id
        )

        if approved_route_id != route_id:
            return {
                "handoff_ready": False,
                "reason": "approved_route_id_mismatch",
                "live_order_submitted": False,
            }

        raw_fresh_approval_id = approval_result.get(
            "approval_id"
        )

        if not isinstance(
            raw_fresh_approval_id,
            str,
        ):
            return {
                "handoff_ready": False,
                "reason": "fresh_approval_id_required",
                "live_order_submitted": False,
            }

        fresh_approval_id = (
            raw_fresh_approval_id.strip()
        )

        if not fresh_approval_id:
            return {
                "handoff_ready": False,
                "reason": "fresh_approval_id_required",
                "live_order_submitted": False,
            }

        previous_approval_id = (
            approval_handoff.get(
                "previous_approval_id"
            )
        )

        normalized_previous_approval_id = (
            previous_approval_id.strip()
            if isinstance(previous_approval_id, str)
            else previous_approval_id
        )

        if (
            normalized_previous_approval_id is not None
            and fresh_approval_id
            == normalized_previous_approval_id
        ):
            return {
                "handoff_ready": False,
                "reason": "previous_approval_id_reuse_blocked",
                "live_order_submitted": False,
            }

        return {
            "handoff_ready": True,
            "reason": (
                "fresh_repeat_scale_permission_handoff_ready"
            ),
            "route_id": route_id,
            "decision": approval_handoff.get(
                "decision"
            ),
            "approval_id": fresh_approval_id,
            "asset": requested_asset,
            "trade_amount": requested_amount,
            "previous_approval_id": (
                normalized_previous_approval_id
            ),
            "previous_permission_id": (
                approval_handoff.get(
                    "previous_permission_id"
                )
            ),
            "fresh_execution_permission_required": True,
            "permission_granted": False,
            "test_trade": True,
            "simulated": True,
            "live_order_submitted": False,
        }
