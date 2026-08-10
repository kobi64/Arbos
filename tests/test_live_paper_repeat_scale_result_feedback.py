import pytest

from core.live_paper_repeat_scale_result_feedback import (
    LivePaperRepeatScaleResultFeedback,
)


def completed_execution(
    starting_value=250.0,
    final_value=262.5,
):
    return {
        "executed": True,
        "paper_only": True,
        "reason": (
            "live_paper_repeat_scale_cycle_completed"
        ),
        "route_id": "ROUTE-001",
        "approval_id": "ARB-002",
        "permission_id": "PERM-002",
        "trade_amount": starting_value,
        "status": "COMPLETED",
        "final_value": final_value,
        "legs": [
            {
                "leg_number": 1,
                "symbol": "BTC/USDT",
                "side": "buy",
                "input_amount": 250.0,
                "output_amount": 0.004,
                "atomic_snapshot": True,
            },
            {
                "leg_number": 2,
                "symbol": "ETH/BTC",
                "side": "buy",
                "input_amount": 0.004,
                "output_amount": 0.08,
                "atomic_snapshot": True,
            },
            {
                "leg_number": 3,
                "symbol": "ETH/USDT",
                "side": "sell",
                "input_amount": 0.08,
                "output_amount": final_value,
                "atomic_snapshot": True,
            },
        ],
        "test_trade": True,
        "simulated": True,
        "paper_trade": True,
        "live_order_submitted": False,
    }


def evaluate(
    execution_result=None,
    starting_value=250.0,
    successful_test_count=0,
    required_successes_for_scale=2,
    scale_multiplier=2.0,
    min_trade_size=100.0,
    max_trade_size=1000.0,
    minimum_profit_percent=2.0,
    trading_fees=0.0,
    transfer_fees=0.0,
    other_costs=0.0,
):
    service = (
        LivePaperRepeatScaleResultFeedback()
    )

    return service.evaluate(
        execution_result=(
            completed_execution()
            if execution_result is None
            else execution_result
        ),
        starting_value=starting_value,
        successful_test_count=(
            successful_test_count
        ),
        required_successes_for_scale=(
            required_successes_for_scale
        ),
        scale_multiplier=scale_multiplier,
        min_trade_size=min_trade_size,
        max_trade_size=max_trade_size,
        minimum_profit_percent=(
            minimum_profit_percent
        ),
        trading_fees=trading_fees,
        transfer_fees=transfer_fees,
        other_costs=other_costs,
    )


def test_completed_execution_produces_feedback():
    result = evaluate()

    assert result["feedback_complete"] is True
    assert (
        result["reason"]
        == "live_paper_repeat_scale_feedback_complete"
    )


def test_completion_record_is_normalized():
    result = evaluate()
    record = result["completion_record"]

    assert record["completed"] is True
    assert record["route_complete"] is True
    assert record["completed_leg_number"] == 3
    assert record["total_legs"] == 3
    assert record["final_symbol"] == "ETH/USDT"
    assert record["final_side"] == "sell"
    assert record["final_output_amount"] == 262.5


def test_control_identifiers_are_preserved():
    result = evaluate()

    assert result["route_id"] == "ROUTE-001"
    assert result["approval_id"] == "ARB-002"
    assert result["permission_id"] == "PERM-002"


def test_pnl_is_calculated_from_execution_result():
    result = evaluate()

    pnl = result["pnl_result"]["pnl"]

    assert pnl["starting_value"] == 250.0
    assert pnl["gross_final_value"] == 262.5
    assert pnl["net_profit"] == 12.5
    assert pnl["profit_percent"] == 5.0
    assert pnl["profitable"] is True


def test_costs_flow_into_existing_pnl_engine():
    result = evaluate(
        trading_fees=2.0,
        transfer_fees=1.0,
        other_costs=0.5,
    )

    pnl = result["pnl_result"]["pnl"]

    assert pnl["total_costs"] == 3.5
    assert pnl["net_final_value"] == 259.0
    assert pnl["net_profit"] == 9.0


def test_profitable_result_is_validated():
    result = evaluate()

    validation = result[
        "validation_result"
    ]

    assert validation["validated"] is True
    assert validation["accepted"] is True


def test_unprofitable_result_is_rejected():
    result = evaluate(
        execution_result=(
            completed_execution(
                final_value=251.0
            )
        ),
        minimum_profit_percent=2.0,
    )

    validation = result[
        "validation_result"
    ]

    assert validation["validated"] is True
    assert validation["accepted"] is False


def test_success_requests_same_size_repeat_before_scale_threshold():
    result = evaluate(
        successful_test_count=0,
        required_successes_for_scale=2,
    )

    decision = result[
        "decision_result"
    ]

    assert (
        decision["decision"]
        == "REPEAT_SAME_SIZE"
    )
    assert decision["allowed"] is True
    assert decision["next_trade_size"] == 250.0


def test_success_can_progress_to_scale_up():
    result = evaluate(
        successful_test_count=2,
        required_successes_for_scale=2,
        scale_multiplier=2.0,
    )

    decision = result[
        "decision_result"
    ]

    assert decision["decision"] == "SCALE_UP"
    assert decision["allowed"] is True
    assert decision["next_trade_size"] == 500.0
    assert decision["scale_applied"] is True


def test_scale_respects_max_trade_size():
    result = evaluate(
        starting_value=600.0,
        execution_result=(
            completed_execution(
                starting_value=600.0,
                final_value=630.0,
            )
        ),
        successful_test_count=2,
        required_successes_for_scale=2,
        scale_multiplier=2.0,
        max_trade_size=1000.0,
    )

    decision = result[
        "decision_result"
    ]

    assert (
        decision["decision"]
        == "REPEAT_SAME_SIZE"
    )
    assert decision["reason"] == "scale_limit_reached"
    assert decision["next_trade_size"] == 600.0


def test_unprofitable_route_stops_repeat_scale():
    result = evaluate(
        execution_result=(
            completed_execution(
                final_value=251.0
            )
        ),
        minimum_profit_percent=2.0,
    )

    decision = result[
        "decision_result"
    ]

    assert decision["decision"] == "STOP"
    assert decision["allowed"] is False
    assert (
        decision["reason"]
        == "successful_test_route_required"
    )


def test_next_cycle_requires_fresh_controls():
    result = evaluate(
        successful_test_count=2,
    )

    decision = result[
        "decision_result"
    ]

    assert (
        decision["fresh_revalidation_required"]
        is True
    )
    assert (
        decision["fresh_approval_required"]
        is True
    )
    assert (
        decision[
            "fresh_execution_permission_required"
        ]
        is True
    )


def test_live_submission_is_blocked():
    record = completed_execution()
    record["live_order_submitted"] = True

    result = evaluate(
        execution_result=record
    )

    assert result["feedback_complete"] is False
    assert (
        result["reason"]
        == "live_order_already_submitted"
    )
    assert result["live_order_submitted"] is True


def test_unexecuted_result_is_blocked():
    record = completed_execution()
    record["executed"] = False

    result = evaluate(
        execution_result=record
    )

    assert result["feedback_complete"] is False
    assert (
        result["reason"]
        == "completed_paper_execution_required"
    )


def test_non_paper_only_result_is_blocked():
    record = completed_execution()
    record["paper_only"] = False

    result = evaluate(
        execution_result=record
    )

    assert result["feedback_complete"] is False
    assert (
        result["reason"]
        == "paper_only_execution_required"
    )


def test_non_simulated_result_is_blocked():
    record = completed_execution()
    record["simulated"] = False

    result = evaluate(
        execution_result=record
    )

    assert result["feedback_complete"] is False
    assert (
        result["reason"]
        == "simulated_execution_required"
    )


def test_non_paper_trade_is_blocked():
    record = completed_execution()
    record["paper_trade"] = False

    result = evaluate(
        execution_result=record
    )

    assert result["feedback_complete"] is False
    assert result["reason"] == "paper_trade_required"


def test_non_test_trade_is_blocked():
    record = completed_execution()
    record["test_trade"] = False

    result = evaluate(
        execution_result=record
    )

    assert result["feedback_complete"] is False
    assert result["reason"] == "test_trade_required"


def test_incomplete_status_is_blocked():
    record = completed_execution()
    record["status"] = "PARTIAL"

    result = evaluate(
        execution_result=record
    )

    assert result["feedback_complete"] is False
    assert (
        result["reason"]
        == "completed_paper_execution_required"
    )


def test_trade_amount_must_match_starting_value():
    result = evaluate(
        execution_result=(
            completed_execution(
                starting_value=500.0
            )
        ),
        starting_value=250.0,
    )

    assert result["feedback_complete"] is False
    assert (
        result["reason"]
        == "starting_value_trade_amount_mismatch"
    )


def test_completed_route_legs_are_required():
    record = completed_execution()
    record["legs"] = []

    result = evaluate(
        execution_result=record
    )

    assert result["feedback_complete"] is False
    assert (
        result["reason"]
        == "completed_route_legs_required"
    )


def test_final_value_is_required():
    record = completed_execution()
    record["final_value"] = 0.0

    result = evaluate(
        execution_result=record
    )

    assert result["feedback_complete"] is False
    assert result["reason"] == "final_value_required"


def test_missing_execution_result_is_rejected():
    service = (
        LivePaperRepeatScaleResultFeedback()
    )

    with pytest.raises(
        ValueError,
        match="execution_result is required",
    ):
        service.evaluate(
            execution_result=None,
            starting_value=250.0,
            successful_test_count=0,
            required_successes_for_scale=2,
            scale_multiplier=2.0,
            min_trade_size=100.0,
            max_trade_size=1000.0,
        )


def test_invalid_starting_value_is_rejected():
    with pytest.raises(
        ValueError,
        match="starting_value must be positive",
    ):
        evaluate(
            starting_value=0.0,
        )


def test_successful_feedback_is_recorded():
    service = (
        LivePaperRepeatScaleResultFeedback()
    )

    service.evaluate(
        execution_result=completed_execution(),
        starting_value=250.0,
        successful_test_count=0,
        required_successes_for_scale=2,
        scale_multiplier=2.0,
        min_trade_size=100.0,
        max_trade_size=1000.0,
        minimum_profit_percent=2.0,
    )

    assert len(service.history()) == 1
    assert (
        service.history()[0][
            "feedback_complete"
        ]
        is True
    )


def test_blocked_feedback_is_recorded():
    service = (
        LivePaperRepeatScaleResultFeedback()
    )

    record = completed_execution()
    record["executed"] = False

    service.evaluate(
        execution_result=record,
        starting_value=250.0,
        successful_test_count=0,
        required_successes_for_scale=2,
        scale_multiplier=2.0,
        min_trade_size=100.0,
        max_trade_size=1000.0,
    )

    assert len(service.history()) == 1
    assert (
        service.history()[0][
            "feedback_complete"
        ]
        is False
    )


def test_entire_feedback_path_remains_paper_only():
    result = evaluate()

    assert result["test_trade"] is True
    assert result["simulated"] is True
    assert result["paper_trade"] is True
    assert result["live_order_submitted"] is False

    assert (
        result["completion_record"][
            "live_order_submitted"
        ]
        is False
    )

    assert (
        result["pnl_result"][
            "live_order_submitted"
        ]
        is False
    )

    assert (
        result["validation_result"][
            "live_order_submitted"
        ]
        is False
    )

    assert (
        result["decision_result"][
            "live_order_submitted"
        ]
        is False
    )
