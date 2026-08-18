"""
ArbOS™
EX-174
End-to-End Live Market Paper Cycle Controller

Coordinates one complete controlled paper-trading cycle:

fresh execution permission
    -> live-market atomic paper execution
    -> P&L / validation / repeat-scale feedback
    -> controlled continuation preparation

Any next cycle still stops at the fresh manual-approval boundary.

This module never submits a live exchange order.
"""

from core.live_paper_repeat_scale_cycle_orchestration import (
    LivePaperRepeatScaleCycleOrchestration,
)
from core.live_paper_repeat_scale_result_feedback import (
    LivePaperRepeatScaleResultFeedback,
)
from core.controlled_repeat_scale_continuation import (
    ControlledRepeatScaleContinuation,
)
from core.repeat_scale_market_provenance import (
    RepeatScaleMarketProvenance,
)


class EndToEndLiveMarketPaperCycleController:
    def __init__(self, snapshot_engine):
        if snapshot_engine is None:
            raise ValueError(
                "snapshot_engine is required"
            )

        self._market_provenance = (
            RepeatScaleMarketProvenance(
                snapshot_engine
            )
        )

        self._execution = (
            LivePaperRepeatScaleCycleOrchestration(
                snapshot_engine
            )
        )
        self._feedback = (
            LivePaperRepeatScaleResultFeedback()
        )
        self._continuation = (
            ControlledRepeatScaleContinuation()
        )
        self._history = []

    def run_cycle(
        self,
        permission_result,
        execution_id,
        route,
        portfolio,
        asset,
        additional_exposure,
        starting_value,
        successful_test_count,
        required_successes_for_scale,
        scale_multiplier,
        min_trade_size,
        max_trade_size,
        repeat_count,
        scale_count,
        cumulative_trade_amount,
        max_repeats,
        max_scale_steps,
        max_cumulative_trade_amount,
        circuit_breaker_result,
        portfolio_risk_result,
        source_networks,
        destination_networks,
        transfer_amount,
        available_liquidity,
        minimum_liquidity_ratio,
        expected_price,
        current_price,
        max_slippage_percent,
        buy_exchange,
        sell_exchange,
        expected_profit,
        estimated_fees,
        slippage_allowance,
        trading_fees=0.0,
        transfer_fees=0.0,
        other_costs=0.0,
        minimum_profit_percent=0.0,
    ):
        if permission_result is None:
            raise ValueError(
                "permission_result is required"
            )

        execution_result = (
            self._execution.execute(
                permission_result=(
                    permission_result
                ),
                execution_id=execution_id,
                route=route,
                portfolio=portfolio,
                asset=asset,
                additional_exposure=(
                    additional_exposure
                ),
                starting_value=starting_value,
            )
        )

        if execution_result.get(
            "executed"
        ) is not True:
            return self._record({
                "cycle_complete": False,
                "stage": "EXECUTION",
                "reason": execution_result.get(
                    "reason"
                ),
                "execution_result": (
                    execution_result
                ),
                "test_trade": True,
                "simulated": True,
                "paper_trade": True,
                "live_order_submitted": (
                    execution_result.get(
                        "live_order_submitted",
                        False,
                    )
                ),
            })

        feedback_result = (
            self._feedback.evaluate(
                execution_result=(
                    execution_result
                ),
                starting_value=starting_value,
                successful_test_count=(
                    successful_test_count
                ),
                required_successes_for_scale=(
                    required_successes_for_scale
                ),
                scale_multiplier=(
                    scale_multiplier
                ),
                min_trade_size=min_trade_size,
                max_trade_size=max_trade_size,
                trading_fees=trading_fees,
                transfer_fees=transfer_fees,
                other_costs=other_costs,
                minimum_profit_percent=(
                    minimum_profit_percent
                ),
            )
        )

        if feedback_result.get(
            "feedback_complete"
        ) is not True:
            return self._record({
                "cycle_complete": False,
                "stage": "FEEDBACK",
                "reason": feedback_result.get(
                    "reason"
                ),
                "execution_result": (
                    execution_result
                ),
                "feedback_result": (
                    feedback_result
                ),
                "test_trade": True,
                "simulated": True,
                "paper_trade": True,
                "live_order_submitted": (
                    feedback_result.get(
                        "live_order_submitted",
                        False,
                    )
                ),
            })

        decision_record = (
            feedback_result.get(
                "decision_result"
            )
            or {}
        )

        decision_name = str(
            decision_record.get(
                "decision",
                "",
            )
        ).strip().upper()

        market_provenance = None

        revalidation_available_liquidity = (
            available_liquidity
        )
        revalidation_expected_price = (
            expected_price
        )
        revalidation_current_price = (
            current_price
        )

        if (
            decision_record.get("allowed")
            is True
            and decision_name
            in {
                "REPEAT_SAME_SIZE",
                "SCALE_UP",
            }
        ):
            fresh_market = (
                self._market_provenance.capture(
                    route=route,
                    trade_amount=(
                        decision_record.get(
                            "next_trade_size",
                            starting_value,
                        )
                    ),
                )
            )

            revalidation_available_liquidity = (
                fresh_market[
                    "available_liquidity"
                ]
            )
            revalidation_expected_price = (
                fresh_market[
                    "expected_price"
                ]
            )
            revalidation_current_price = (
                fresh_market[
                    "current_price"
                ]
            )
            market_provenance = (
                fresh_market[
                    "market_provenance"
                ]
            )

        continuation_result = (
            self._continuation.prepare_next(
                feedback_result=(
                    feedback_result
                ),
                repeat_count=repeat_count,
                scale_count=scale_count,
                cumulative_trade_amount=(
                    cumulative_trade_amount
                ),
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
                required_successes_for_scale=(
                    required_successes_for_scale
                ),
                scale_multiplier=(
                    scale_multiplier
                ),
                min_trade_size=min_trade_size,
                max_trade_size=max_trade_size,
                source_networks=(
                    source_networks
                ),
                destination_networks=(
                    destination_networks
                ),
                transfer_amount=(
                    transfer_amount
                ),
                available_liquidity=(
                    revalidation_available_liquidity
                ),
                minimum_liquidity_ratio=(
                    minimum_liquidity_ratio
                ),
                expected_price=(
                    revalidation_expected_price
                ),
                current_price=(
                    revalidation_current_price
                ),
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

        if market_provenance is not None:
            continuation_result = dict(
                continuation_result
            )
            continuation_result[
                "market_provenance"
            ] = dict(
                market_provenance
            )

        return self._record({
            "cycle_complete": True,
            "stage": (
                continuation_result.get(
                    "stage"
                )
            ),
            "reason": (
                "end_to_end_live_market_paper_cycle_complete"
            ),
            "route_id": (
                execution_result.get(
                    "route_id"
                )
            ),
            "approval_id": (
                execution_result.get(
                    "approval_id"
                )
            ),
            "permission_id": (
                execution_result.get(
                    "permission_id"
                )
            ),
            "execution_result": (
                execution_result
            ),
            "feedback_result": (
                feedback_result
            ),
            "continuation_result": (
                continuation_result
            ),
            "next_cycle_ready": (
                continuation_result.get(
                    "continuation_ready",
                    False,
                )
            ),
            "hard_stop": (
                continuation_result.get(
                    "hard_stop",
                    False,
                )
            ),
            "test_trade": True,
            "simulated": True,
            "paper_trade": True,
            "live_order_submitted": False,
        })

    def history(self):
        return [
            dict(record)
            for record in self._history
        ]

    def total_reserved(self):
        return (
            self._execution.total_reserved()
        )

    def _record(self, result):
        self._history.append(
            dict(result)
        )
        return dict(result)
