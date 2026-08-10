"""
ArbOS™
EX-172
Live Paper Repeat / Scale Result Feedback

Converts a completed EX-171 live-market paper execution result
into the existing simulated route P&L and validation contracts,
then produces the next controlled repeat/scale decision.

This module performs paper-result feedback only.
It does not approve, authorize, or submit live exchange orders.
"""

from core.simulated_route_result_pnl import (
    SimulatedRouteResultPnL,
)
from core.simulated_route_validation_result import (
    SimulatedRouteValidationResult,
)
from core.controlled_repeat_scale_decision import (
    ControlledRepeatScaleDecision,
)


class LivePaperRepeatScaleResultFeedback:
    def __init__(self):
        self._pnl = SimulatedRouteResultPnL()
        self._validator = (
            SimulatedRouteValidationResult()
        )
        self._decision = (
            ControlledRepeatScaleDecision()
        )
        self._history = []

    def evaluate(
        self,
        execution_result,
        starting_value,
        successful_test_count,
        required_successes_for_scale,
        scale_multiplier,
        min_trade_size,
        max_trade_size,
        trading_fees=0.0,
        transfer_fees=0.0,
        other_costs=0.0,
        minimum_profit_percent=0.0,
    ):
        if execution_result is None:
            raise ValueError(
                "execution_result is required"
            )

        if execution_result.get(
            "live_order_submitted"
        ) is True:
            return self._blocked(
                "live_order_already_submitted",
                live_order_submitted=True,
            )

        if execution_result.get(
            "executed"
        ) is not True:
            return self._blocked(
                "completed_paper_execution_required"
            )

        if execution_result.get(
            "paper_only"
        ) is not True:
            return self._blocked(
                "paper_only_execution_required"
            )

        if execution_result.get(
            "simulated"
        ) is not True:
            return self._blocked(
                "simulated_execution_required"
            )

        if execution_result.get(
            "paper_trade"
        ) is not True:
            return self._blocked(
                "paper_trade_required"
            )

        if execution_result.get(
            "test_trade"
        ) is not True:
            return self._blocked(
                "test_trade_required"
            )

        if execution_result.get(
            "status"
        ) != "COMPLETED":
            return self._blocked(
                "completed_paper_execution_required"
            )

        starting_value = float(
            starting_value
        )

        if starting_value <= 0:
            raise ValueError(
                "starting_value must be positive"
            )

        trade_amount = float(
            execution_result.get(
                "trade_amount",
                0.0,
            )
        )

        if trade_amount <= 0:
            return self._blocked(
                "trade_amount_required"
            )

        if trade_amount != starting_value:
            return self._blocked(
                "starting_value_trade_amount_mismatch"
            )

        legs = execution_result.get(
            "legs"
        ) or []

        if not legs:
            return self._blocked(
                "completed_route_legs_required"
            )

        final_leg = legs[-1]

        final_value = float(
            execution_result.get(
                "final_value",
                0.0,
            )
        )

        if final_value <= 0:
            return self._blocked(
                "final_value_required"
            )

        completion_record = {
            "completed": True,
            "route_complete": True,
            "reason": (
                "live_paper_repeat_scale_route_complete"
            ),
            "route_id": execution_result.get(
                "route_id"
            ),
            "approval_id": execution_result.get(
                "approval_id"
            ),
            "permission_id": execution_result.get(
                "permission_id"
            ),
            "completed_leg_number": len(legs),
            "total_legs": len(legs),
            "final_symbol": final_leg.get(
                "symbol"
            ),
            "final_side": final_leg.get(
                "side"
            ),
            "final_filled_quantity": (
                final_leg.get(
                    "output_amount"
                )
            ),
            "final_notional": final_value,
            "final_output_amount": final_value,
            "test_trade": True,
            "simulated": True,
            "paper_trade": True,
            "live_order_submitted": False,
        }

        pnl_result = self._pnl.evaluate(
            completion_record=completion_record,
            starting_value=starting_value,
            trading_fees=trading_fees,
            transfer_fees=transfer_fees,
            other_costs=other_costs,
            minimum_profit_percent=(
                minimum_profit_percent
            ),
        )

        validation_result = (
            self._validator.validate(
                pnl_result
            )
        )

        decision_result = (
            self._decision.decide(
                validation_result=(
                    validation_result
                ),
                current_trade_size=(
                    starting_value
                ),
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
            )
        )

        result = {
            "feedback_complete": True,
            "reason": (
                "live_paper_repeat_scale_feedback_complete"
            ),
            "route_id": execution_result.get(
                "route_id"
            ),
            "approval_id": execution_result.get(
                "approval_id"
            ),
            "permission_id": execution_result.get(
                "permission_id"
            ),
            "starting_value": starting_value,
            "final_value": final_value,
            "completion_record": (
                completion_record
            ),
            "pnl_result": pnl_result,
            "validation_result": (
                validation_result
            ),
            "decision_result": (
                decision_result
            ),
            "test_trade": True,
            "simulated": True,
            "paper_trade": True,
            "live_order_submitted": False,
        }

        self._history.append(
            dict(result)
        )

        return dict(result)

    def history(self):
        return [
            dict(record)
            for record in self._history
        ]

    def _blocked(
        self,
        reason,
        live_order_submitted=False,
    ):
        result = {
            "feedback_complete": False,
            "reason": reason,
            "test_trade": True,
            "simulated": True,
            "paper_trade": True,
            "live_order_submitted": (
                live_order_submitted
            ),
        }

        self._history.append(
            dict(result)
        )

        return result
