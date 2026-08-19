"""
ArbOS™
EX-168
Repeat / Scale Cycle Integration

Coordinates the controlled repeat/scale staged-test cycle.

Stage 1:
validated simulated route
    -> repeat/scale decision
    -> fresh market/route revalidation
    -> fresh manual approval request

Stage 2:
fresh manual approval
    -> execution-permission handoff

The manual approval boundary remains explicit between stages.

This module does not grant execution permission or submit orders.
"""

from core.controlled_repeat_scale_decision import (
    ControlledRepeatScaleDecision,
)
from core.fresh_repeat_scale_revalidation import (
    FreshRepeatScaleRevalidation,
)
from core.revalidated_repeat_scale_approval_handoff import (
    RevalidatedRepeatScaleApprovalHandoff,
)
from core.fresh_repeat_scale_execution_permission_handoff import (
    FreshRepeatScaleExecutionPermissionHandoff,
)


class RepeatScaleCycleIntegration:
    def prepare_approval(
        self,
        validation_result,
        current_trade_size,
        successful_test_count,
        required_successes_for_scale,
        scale_multiplier,
        min_trade_size,
        max_trade_size,
        source_networks,
        destination_networks,
        transfer_amount,
        available_liquidity,
        minimum_liquidity_ratio,
        expected_price,
        current_price,
        max_slippage_percent,
        asset,
        buy_exchange,
        sell_exchange,
        expected_profit,
        estimated_fees,
        slippage_allowance,
        market_provenance_binding=None,
    ):
        if validation_result is None:
            raise ValueError(
                "validation_result is required"
            )

        decision_result = (
            ControlledRepeatScaleDecision().decide(
                validation_result=validation_result,
                current_trade_size=current_trade_size,
                successful_test_count=successful_test_count,
                required_successes_for_scale=(
                    required_successes_for_scale
                ),
                scale_multiplier=scale_multiplier,
                min_trade_size=min_trade_size,
                max_trade_size=max_trade_size,
            )
        )

        if decision_result.get("allowed") is not True:
            return {
                "cycle_ready": False,
                "stage": "DECISION",
                "reason": decision_result.get(
                    "reason"
                ),
                "decision_result": decision_result,
                "live_order_submitted": (
                    decision_result.get(
                        "live_order_submitted",
                        False,
                    )
                ),
            }

        revalidation_result = (
            FreshRepeatScaleRevalidation().revalidate(
                decision_result=decision_result,
                source_networks=source_networks,
                destination_networks=(
                    destination_networks
                ),
                transfer_amount=transfer_amount,
                available_liquidity=(
                    available_liquidity
                ),
                minimum_liquidity_ratio=(
                    minimum_liquidity_ratio
                ),
                expected_price=expected_price,
                current_price=current_price,
                max_slippage_percent=(
                    max_slippage_percent
                ),
                market_provenance_binding=(
                    market_provenance_binding
                ),
            )
        )

        if (
            revalidation_result.get("revalidated")
            is not True
        ):
            return {
                "cycle_ready": False,
                "stage": "REVALIDATION",
                "reason": revalidation_result.get(
                    "reason"
                ),
                "decision_result": decision_result,
                "revalidation_result": (
                    revalidation_result
                ),
                "live_order_submitted": (
                    revalidation_result.get(
                        "live_order_submitted",
                        False,
                    )
                ),
            }

        approval_handoff = (
            RevalidatedRepeatScaleApprovalHandoff()
            .prepare(
                revalidation_result=(
                    revalidation_result
                ),
                asset=asset,
                buy_exchange=buy_exchange,
                sell_exchange=sell_exchange,
                expected_profit=expected_profit,
                estimated_fees=estimated_fees,
                slippage_allowance=(
                    slippage_allowance
                ),
            )
        )

        if (
            approval_handoff.get("approval_ready")
            is not True
        ):
            return {
                "cycle_ready": False,
                "stage": "APPROVAL_HANDOFF",
                "reason": approval_handoff.get(
                    "reason"
                ),
                "decision_result": decision_result,
                "revalidation_result": (
                    revalidation_result
                ),
                "approval_handoff": approval_handoff,
                "live_order_submitted": (
                    approval_handoff.get(
                        "live_order_submitted",
                        False,
                    )
                ),
            }

        return {
            "cycle_ready": True,
            "stage": "AWAITING_FRESH_APPROVAL",
            "reason": (
                "repeat_scale_cycle_awaiting_fresh_approval"
            ),
            "route_id": approval_handoff.get(
                "route_id"
            ),
            "decision": approval_handoff.get(
                "decision"
            ),
            "trade_amount": approval_handoff.get(
                "trade_amount"
            ),
            "decision_result": decision_result,
            "revalidation_result": (
                revalidation_result
            ),
            "approval_handoff": approval_handoff,
            "manual_approval_required": True,
            "approval_granted": False,
            "permission_granted": False,
            "test_trade": True,
            "simulated": True,
            "live_order_submitted": False,
        }

    def prepare_permission(
        self,
        cycle_result,
        approval_result,
    ):
        if cycle_result is None:
            raise ValueError(
                "cycle_result is required"
            )

        if approval_result is None:
            raise ValueError(
                "approval_result is required"
            )

        if cycle_result.get(
            "live_order_submitted"
        ) is True:
            return {
                "cycle_ready": False,
                "permission_handoff_ready": False,
                "stage": "BLOCKED",
                "reason": "live_order_already_submitted",
                "live_order_submitted": True,
            }

        if cycle_result.get(
            "cycle_ready"
        ) is not True:
            return {
                "cycle_ready": False,
                "permission_handoff_ready": False,
                "stage": "BLOCKED",
                "reason": "prepared_cycle_required",
                "live_order_submitted": False,
            }

        if (
            cycle_result.get("stage")
            != "AWAITING_FRESH_APPROVAL"
        ):
            return {
                "cycle_ready": False,
                "permission_handoff_ready": False,
                "stage": "BLOCKED",
                "reason": (
                    "fresh_approval_stage_required"
                ),
                "live_order_submitted": False,
            }

        approval_handoff = cycle_result.get(
            "approval_handoff"
        )

        if approval_handoff is None:
            return {
                "cycle_ready": False,
                "permission_handoff_ready": False,
                "stage": "BLOCKED",
                "reason": "approval_handoff_required",
                "live_order_submitted": False,
            }

        permission_handoff = (
            FreshRepeatScaleExecutionPermissionHandoff()
            .prepare(
                approval_handoff=approval_handoff,
                approval_result=approval_result,
            )
        )

        if (
            permission_handoff.get("handoff_ready")
            is not True
        ):
            return {
                "cycle_ready": False,
                "permission_handoff_ready": False,
                "stage": "PERMISSION_HANDOFF",
                "reason": permission_handoff.get(
                    "reason"
                ),
                "permission_handoff": (
                    permission_handoff
                ),
                "live_order_submitted": (
                    permission_handoff.get(
                        "live_order_submitted",
                        False,
                    )
                ),
            }

        return {
            "cycle_ready": True,
            "permission_handoff_ready": True,
            "stage": (
                "AWAITING_EXECUTION_PERMISSION"
            ),
            "reason": (
                "repeat_scale_cycle_permission_handoff_ready"
            ),
            "route_id": permission_handoff.get(
                "route_id"
            ),
            "decision": permission_handoff.get(
                "decision"
            ),
            "approval_id": permission_handoff.get(
                "approval_id"
            ),
            "trade_amount": permission_handoff.get(
                "trade_amount"
            ),
            "permission_handoff": (
                permission_handoff
            ),
            "fresh_execution_permission_required": (
                True
            ),
            "permission_granted": False,
            "test_trade": True,
            "simulated": True,
            "live_order_submitted": False,
        }
