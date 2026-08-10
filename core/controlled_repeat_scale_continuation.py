"""
ArbOS™
EX-173
Controlled Repeat / Scale Continuation

Combines completed live-paper feedback, cycle limits, and the
existing repeat/scale cycle integration to prepare the next
controlled staged-test cycle.

The next cycle still requires:
- fresh route / market revalidation
- fresh manual approval
- fresh execution permission

This module does not approve, authorize, or submit live orders.
"""

from core.repeat_scale_cycle_limits import (
    RepeatScaleCycleLimits,
)
from core.repeat_scale_cycle_integration import (
    RepeatScaleCycleIntegration,
)


class ControlledRepeatScaleContinuation:
    def __init__(self):
        self._limits = RepeatScaleCycleLimits()
        self._cycle = RepeatScaleCycleIntegration()
        self._history = []

    def prepare_next(
        self,
        feedback_result,
        repeat_count,
        scale_count,
        cumulative_trade_amount,
        max_repeats,
        max_scale_steps,
        max_cumulative_trade_amount,
        circuit_breaker_result,
        portfolio_risk_result,
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
    ):
        if feedback_result is None:
            raise ValueError(
                "feedback_result is required"
            )

        if feedback_result.get(
            "live_order_submitted"
        ) is True:
            return self._record(
                {
                    "continuation_ready": False,
                    "hard_stop": True,
                    "stage": "FEEDBACK",
                    "reason": (
                        "live_order_already_submitted"
                    ),
                    "live_order_submitted": True,
                }
            )

        if feedback_result.get(
            "feedback_complete"
        ) is not True:
            return self._record(
                {
                    "continuation_ready": False,
                    "hard_stop": True,
                    "stage": "FEEDBACK",
                    "reason": (
                        "completed_feedback_required"
                    ),
                    "live_order_submitted": False,
                }
            )

        decision_result = feedback_result.get(
            "decision_result"
        )

        if decision_result is None:
            return self._record(
                {
                    "continuation_ready": False,
                    "hard_stop": True,
                    "stage": "DECISION",
                    "reason": (
                        "feedback_decision_required"
                    ),
                    "live_order_submitted": False,
                }
            )

        decision = str(
            decision_result.get(
                "decision",
                "",
            )
        ).strip().upper()

        if (
            decision == "STOP"
            or decision_result.get("allowed")
            is not True
        ):
            return self._record(
                {
                    "continuation_ready": False,
                    "hard_stop": True,
                    "stage": "DECISION",
                    "reason": decision_result.get(
                        "reason",
                        "repeat_scale_stopped",
                    ),
                    "decision_result": (
                        decision_result
                    ),
                    "live_order_submitted": False,
                }
            )

        if decision not in {
            "REPEAT_SAME_SIZE",
            "SCALE_UP",
        }:
            return self._record(
                {
                    "continuation_ready": False,
                    "hard_stop": True,
                    "stage": "DECISION",
                    "reason": (
                        "repeat_or_scale_decision_required"
                    ),
                    "decision_result": (
                        decision_result
                    ),
                    "live_order_submitted": False,
                }
            )

        current_trade_size = float(
            feedback_result.get(
                "starting_value",
                0.0,
            )
        )

        next_trade_size = float(
            decision_result.get(
                "next_trade_size",
                0.0,
            )
        )

        if current_trade_size <= 0:
            raise ValueError(
                "feedback starting_value must be positive"
            )

        if next_trade_size <= 0:
            return self._record(
                {
                    "continuation_ready": False,
                    "hard_stop": True,
                    "stage": "DECISION",
                    "reason": (
                        "next_trade_size_required"
                    ),
                    "decision_result": (
                        decision_result
                    ),
                    "live_order_submitted": False,
                }
            )

        limit_result = self._limits.evaluate(
            repeat_count=repeat_count,
            scale_count=scale_count,
            cumulative_trade_amount=(
                cumulative_trade_amount
            ),
            next_trade_amount=next_trade_size,
            max_repeats=max_repeats,
            max_scale_steps=max_scale_steps,
            max_cumulative_trade_amount=(
                max_cumulative_trade_amount
            ),
            circuit_breaker_result=(
                circuit_breaker_result
            ),
            portfolio_risk_result=(
                portfolio_risk_result
            ),
        )

        if limit_result.get(
            "allowed"
        ) is not True:
            return self._record(
                {
                    "continuation_ready": False,
                    "hard_stop": True,
                    "stage": "LIMITS",
                    "reason": limit_result.get(
                        "reason"
                    ),
                    "decision_result": (
                        decision_result
                    ),
                    "limit_result": limit_result,
                    "live_order_submitted": False,
                }
            )

        effective_max_trade_size = float(
            max_trade_size
        )

        scale_suppressed = False

        if (
            decision == "SCALE_UP"
            and limit_result.get(
                "scale_allowed"
            )
            is not True
        ):
            # EX-169 allows the route to continue but
            # prohibits another scale step. Restrict the
            # EX-168 decision boundary to the current size,
            # causing its existing scale-limit fallback to
            # prepare a same-size repeat.
            effective_max_trade_size = (
                current_trade_size
            )
            scale_suppressed = True

        validation_result = (
            feedback_result.get(
                "validation_result"
            )
        )

        if validation_result is None:
            return self._record(
                {
                    "continuation_ready": False,
                    "hard_stop": True,
                    "stage": "FEEDBACK",
                    "reason": (
                        "validation_result_required"
                    ),
                    "limit_result": limit_result,
                    "live_order_submitted": False,
                }
            )

        successful_test_count = int(
            decision_result.get(
                "successful_test_count",
                0,
            )
        )

        next_cycle = (
            self._cycle.prepare_approval(
                validation_result=(
                    validation_result
                ),
                current_trade_size=(
                    current_trade_size
                ),
                successful_test_count=(
                    successful_test_count
                ),
                required_successes_for_scale=(
                    required_successes_for_scale
                ),
                scale_multiplier=scale_multiplier,
                min_trade_size=min_trade_size,
                max_trade_size=(
                    effective_max_trade_size
                ),
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

        if next_cycle.get(
            "cycle_ready"
        ) is not True:
            return self._record(
                {
                    "continuation_ready": False,
                    "hard_stop": False,
                    "stage": "NEXT_CYCLE",
                    "reason": next_cycle.get(
                        "reason"
                    ),
                    "decision_result": (
                        decision_result
                    ),
                    "limit_result": limit_result,
                    "next_cycle": next_cycle,
                    "scale_suppressed": (
                        scale_suppressed
                    ),
                    "live_order_submitted": (
                        next_cycle.get(
                            "live_order_submitted",
                            False,
                        )
                    ),
                }
            )

        resulting_decision = (
            next_cycle.get(
                "decision"
            )
        )

        next_scale_count = int(
            scale_count
        )

        if (
            resulting_decision == "SCALE_UP"
            and not scale_suppressed
        ):
            next_scale_count += 1

        result = {
            "continuation_ready": True,
            "hard_stop": False,
            "stage": "AWAITING_FRESH_APPROVAL",
            "reason": (
                "controlled_repeat_scale_continuation_ready"
            ),
            "route_id": next_cycle.get(
                "route_id"
            ),
            "decision": resulting_decision,
            "trade_amount": next_cycle.get(
                "trade_amount"
            ),
            "repeat_count": int(
                repeat_count
            ),
            "next_repeat_count": (
                limit_result.get(
                    "next_repeat_count"
                )
            ),
            "scale_count": int(
                scale_count
            ),
            "next_scale_count": (
                next_scale_count
            ),
            "scale_suppressed": (
                scale_suppressed
            ),
            "projected_cumulative_trade_amount": (
                limit_result.get(
                    "projected_cumulative_trade_amount"
                )
            ),
            "decision_result": (
                decision_result
            ),
            "limit_result": limit_result,
            "next_cycle": next_cycle,
            "fresh_revalidation_required": True,
            "manual_approval_required": True,
            "approval_granted": False,
            "fresh_execution_permission_required": True,
            "permission_granted": False,
            "test_trade": True,
            "simulated": True,
            "paper_trade": True,
            "live_order_submitted": False,
        }

        return self._record(result)

    def history(self):
        return [
            dict(record)
            for record in self._history
        ]

    def _record(self, result):
        self._history.append(
            dict(result)
        )
        return dict(result)
