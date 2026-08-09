"""
ArbOS™
EX-165
Fresh Repeat / Scale Revalidation

Revalidates current route, transfer, liquidity, and slippage
conditions before a repeated or scaled staged test trade may
progress toward fresh approval.

This module does not approve, authorize, or submit orders.
"""

from exchanges.route_validator import RouteValidator
from exchanges.transfer_feasibility import TransferFeasibility
from exchanges.liquidity_validation import LiquidityValidation
from exchanges.slippage_validation import SlippageValidation


class FreshRepeatScaleRevalidation:
    def revalidate(
        self,
        decision_result,
        source_networks,
        destination_networks,
        transfer_amount,
        available_liquidity,
        minimum_liquidity_ratio,
        expected_price,
        current_price,
        max_slippage_percent,
    ):
        if decision_result is None:
            raise ValueError(
                "decision_result is required"
            )

        if decision_result.get(
            "live_order_submitted"
        ) is True:
            return {
                "revalidated": False,
                "allowed": False,
                "status": "BLOCKED",
                "reason": "live_order_already_submitted",
                "live_order_submitted": True,
            }

        if decision_result.get(
            "allowed"
        ) is not True:
            return {
                "revalidated": False,
                "allowed": False,
                "status": "BLOCKED",
                "reason": "allowed_decision_required",
                "live_order_submitted": False,
            }

        decision = str(
            decision_result.get(
                "decision",
                "",
            )
        ).strip().upper()

        if decision not in {
            "REPEAT_SAME_SIZE",
            "SCALE_UP",
        }:
            return {
                "revalidated": False,
                "allowed": False,
                "status": "BLOCKED",
                "reason": "repeat_or_scale_decision_required",
                "live_order_submitted": False,
            }

        if decision_result.get(
            "fresh_revalidation_required"
        ) is not True:
            return {
                "revalidated": False,
                "allowed": False,
                "status": "BLOCKED",
                "reason": "fresh_revalidation_not_required",
                "live_order_submitted": False,
            }

        next_trade_size = float(
            decision_result.get(
                "next_trade_size",
                0.0,
            )
        )

        if next_trade_size <= 0:
            return {
                "revalidated": False,
                "allowed": False,
                "status": "BLOCKED",
                "reason": "invalid_next_trade_size",
                "live_order_submitted": False,
            }

        route_result = (
            RouteValidator.validate_transfer_route(
                source_networks,
                destination_networks,
            )
        )

        if route_result.executable is not True:
            return {
                "revalidated": False,
                "allowed": False,
                "status": "BLOCKED",
                "reason": "route_not_executable",
                "route_id": decision_result.get(
                    "route_id"
                ),
                "next_trade_size": next_trade_size,
                "live_order_submitted": False,
            }

        selected_network = None

        for network in source_networks:
            if (
                str(network.network).upper()
                == str(route_result.network).upper()
            ):
                selected_network = network
                break

        if selected_network is None:
            return {
                "revalidated": False,
                "allowed": False,
                "status": "BLOCKED",
                "reason": "selected_network_not_found",
                "route_id": decision_result.get(
                    "route_id"
                ),
                "next_trade_size": next_trade_size,
                "live_order_submitted": False,
            }

        transfer_result = (
            TransferFeasibility.evaluate(
                amount=float(
                    transfer_amount
                ),
                network=selected_network,
            )
        )

        if transfer_result.feasible is not True:
            return {
                "revalidated": False,
                "allowed": False,
                "status": "BLOCKED",
                "reason": "transfer_not_feasible",
                "transfer_reason": (
                    transfer_result.reason
                ),
                "route_id": decision_result.get(
                    "route_id"
                ),
                "network": route_result.network,
                "next_trade_size": next_trade_size,
                "live_order_submitted": False,
            }

        liquidity_result = (
            LiquidityValidation.validate(
                trade_size=next_trade_size,
                available_liquidity=float(
                    available_liquidity
                ),
                minimum_liquidity_ratio=float(
                    minimum_liquidity_ratio
                ),
            )
        )

        if liquidity_result["valid"] is not True:
            return {
                "revalidated": False,
                "allowed": False,
                "status": "BLOCKED",
                "reason": "liquidity_revalidation_failed",
                "liquidity_reason": (
                    liquidity_result["reason"]
                ),
                "route_id": decision_result.get(
                    "route_id"
                ),
                "network": route_result.network,
                "next_trade_size": next_trade_size,
                "live_order_submitted": False,
            }

        slippage_result = (
            SlippageValidation.validate(
                expected_price=float(
                    expected_price
                ),
                execution_price=float(
                    current_price
                ),
                max_slippage_percent=float(
                    max_slippage_percent
                ),
            )
        )

        if slippage_result["valid"] is not True:
            return {
                "revalidated": False,
                "allowed": False,
                "status": "BLOCKED",
                "reason": "slippage_revalidation_failed",
                "slippage_reason": (
                    slippage_result["reason"]
                ),
                "route_id": decision_result.get(
                    "route_id"
                ),
                "network": route_result.network,
                "next_trade_size": next_trade_size,
                "live_order_submitted": False,
            }

        return {
            "revalidated": True,
            "allowed": True,
            "status": "REVALIDATED",
            "reason": "fresh_repeat_scale_revalidation_passed",
            "decision": decision,
            "route_id": decision_result.get(
                "route_id"
            ),
            "previous_approval_id": (
                decision_result.get(
                    "approval_id"
                )
            ),
            "previous_permission_id": (
                decision_result.get(
                    "permission_id"
                )
            ),
            "next_trade_size": next_trade_size,
            "network": route_result.network,
            "withdraw_fee": (
                route_result.withdraw_fee
            ),
            "transfer_net_amount": (
                transfer_result.net_amount
            ),
            "fresh_approval_required": True,
            "fresh_execution_permission_required": True,
            "approval_granted": False,
            "permission_granted": False,
            "test_trade": True,
            "simulated": True,
            "live_order_submitted": False,
        }
