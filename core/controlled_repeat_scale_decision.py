"""
ArbOS™
EX-164
Controlled Repeat / Scale Decision

Uses a successful simulated route validation result to recommend
whether a staged test route should stop, repeat at the same size,
or progress to a controlled larger test size.

This module does not approve, authorize, or submit orders.
"""

from exchanges.trade_size_validation import (
    TradeSizeValidation,
)


class ControlledRepeatScaleDecision:
    def decide(
        self,
        validation_result,
        current_trade_size,
        successful_test_count,
        required_successes_for_scale,
        scale_multiplier,
        min_trade_size,
        max_trade_size,
    ):
        if validation_result is None:
            raise ValueError(
                "validation_result is required"
            )

        if validation_result.get(
            "live_order_submitted"
        ) is True:
            return {
                "decision": "STOP",
                "allowed": False,
                "reason": "live_order_already_submitted",
                "live_order_submitted": True,
            }

        if validation_result.get(
            "validated"
        ) is not True:
            return {
                "decision": "STOP",
                "allowed": False,
                "reason": "validated_route_required",
                "live_order_submitted": False,
            }

        if validation_result.get(
            "accepted"
        ) is not True:
            return {
                "decision": "STOP",
                "allowed": False,
                "reason": "successful_test_route_required",
                "live_order_submitted": False,
            }

        if validation_result.get(
            "simulated"
        ) is not True:
            return {
                "decision": "STOP",
                "allowed": False,
                "reason": "simulated_route_required",
                "live_order_submitted": False,
            }

        if validation_result.get(
            "test_trade"
        ) is not True:
            return {
                "decision": "STOP",
                "allowed": False,
                "reason": "test_trade_required",
                "live_order_submitted": False,
            }

        route_id = validation_result.get(
            "route_id"
        )
        approval_id = validation_result.get(
            "approval_id"
        )
        permission_id = validation_result.get(
            "permission_id"
        )

        if (
            not isinstance(route_id, str)
            or not route_id.strip()
            or not isinstance(approval_id, str)
            or not approval_id.strip()
            or not isinstance(permission_id, str)
            or not permission_id.strip()
        ):
            return {
                "decision": "STOP",
                "allowed": False,
                "reason": "invalid_validation_identity",
                "live_order_submitted": False,
            }

        route_id = route_id.strip()
        approval_id = approval_id.strip()
        permission_id = permission_id.strip()

        current_trade_size = float(
            current_trade_size
        )
        successful_test_count = int(
            successful_test_count
        )
        required_successes_for_scale = int(
            required_successes_for_scale
        )
        scale_multiplier = float(
            scale_multiplier
        )
        min_trade_size = float(
            min_trade_size
        )
        max_trade_size = float(
            max_trade_size
        )

        if successful_test_count < 0:
            raise ValueError(
                "successful_test_count must be non-negative"
            )

        if required_successes_for_scale <= 0:
            raise ValueError(
                "required_successes_for_scale must be positive"
            )

        if scale_multiplier <= 1.0:
            raise ValueError(
                "scale_multiplier must be greater than 1"
            )

        current_size_check = (
            TradeSizeValidation.validate(
                trade_size=current_trade_size,
                min_trade_size=min_trade_size,
                max_trade_size=max_trade_size,
            )
        )

        if current_size_check["valid"] is not True:
            return {
                "decision": "STOP",
                "allowed": False,
                "reason": "current_trade_size_invalid",
                "trade_size_reason": (
                    current_size_check["reason"]
                ),
                "live_order_submitted": False,
            }

        common = {
            "route_id": route_id,
            "approval_id": approval_id,
            "permission_id": permission_id,
            "current_trade_size": (
                current_trade_size
            ),
            "successful_test_count": (
                successful_test_count
            ),
            "required_successes_for_scale": (
                required_successes_for_scale
            ),
            "net_profit": validation_result.get(
                "net_profit"
            ),
            "profit_percent": (
                validation_result.get(
                    "profit_percent"
                )
            ),
            "fresh_revalidation_required": True,
            "fresh_approval_required": True,
            "fresh_execution_permission_required": True,
            "test_trade": True,
            "simulated": True,
            "live_order_submitted": False,
        }

        if (
            successful_test_count
            < required_successes_for_scale
        ):
            return {
                **common,
                "decision": "REPEAT_SAME_SIZE",
                "allowed": True,
                "reason": (
                    "additional_successful_test_required"
                ),
                "next_trade_size": (
                    current_trade_size
                ),
                "scale_applied": False,
            }

        proposed_trade_size = (
            current_trade_size
            * scale_multiplier
        )

        proposed_size_check = (
            TradeSizeValidation.validate(
                trade_size=proposed_trade_size,
                min_trade_size=min_trade_size,
                max_trade_size=max_trade_size,
            )
        )

        if proposed_size_check["valid"] is not True:
            return {
                **common,
                "decision": "REPEAT_SAME_SIZE",
                "allowed": True,
                "reason": "scale_limit_reached",
                "next_trade_size": (
                    current_trade_size
                ),
                "proposed_trade_size": (
                    proposed_trade_size
                ),
                "trade_size_reason": (
                    proposed_size_check["reason"]
                ),
                "scale_applied": False,
            }

        return {
            **common,
            "decision": "SCALE_UP",
            "allowed": True,
            "reason": "controlled_scale_up_ready",
            "next_trade_size": (
                proposed_trade_size
            ),
            "proposed_trade_size": (
                proposed_trade_size
            ),
            "scale_applied": True,
        }
