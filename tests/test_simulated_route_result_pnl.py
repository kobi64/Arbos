import pytest

from core.simulated_route_result_pnl import (
    SimulatedRouteResultPnL,
)


def completed_route():
    return {
        "completed": True,
        "route_complete": True,
        "reason": "simulated_multi_leg_route_complete",
        "route_id": "ROUTE-001",
        "approval_id": "ARB-001",
        "permission_id": "PERM-001",
        "completed_leg_number": 3,
        "total_legs": 3,
        "final_symbol": "ETH/USDT",
        "final_side": "sell",
        "final_filled_quantity": 0.328125,
        "final_notional": 1050.0,
        "final_output_amount": 1050.0,
        "test_trade": True,
        "simulated": True,
        "paper_trade": True,
        "live_order_submitted": False,
    }


def test_completed_route_is_evaluated():
    evaluator = SimulatedRouteResultPnL()

    result = evaluator.evaluate(
        completion_record=completed_route(),
        starting_value=1000.0,
        minimum_profit_percent=2.0,
    )

    assert result["evaluated"] is True
    assert (
        result["reason"]
        == "simulated_route_pnl_evaluated"
    )


def test_final_output_becomes_gross_final_value():
    evaluator = SimulatedRouteResultPnL()

    result = evaluator.evaluate(
        completion_record=completed_route(),
        starting_value=1000.0,
        minimum_profit_percent=2.0,
    )

    assert (
        result["pnl"]["gross_final_value"]
        == 1050.0
    )


def test_costs_are_applied_by_existing_pnl_engine():
    evaluator = SimulatedRouteResultPnL()

    result = evaluator.evaluate(
        completion_record=completed_route(),
        starting_value=1000.0,
        trading_fees=5.0,
        transfer_fees=2.0,
        other_costs=3.0,
        minimum_profit_percent=2.0,
    )

    assert result["pnl"]["total_costs"] == 10.0
    assert result["pnl"]["net_final_value"] == 1040.0
    assert result["pnl"]["net_profit"] == 40.0
    assert result["pnl"]["profit_percent"] == 4.0
    assert result["pnl"]["profitable"] is True


def test_costs_can_remove_route_profit():
    evaluator = SimulatedRouteResultPnL()

    record = completed_route()
    record["final_output_amount"] = 1030.0

    result = evaluator.evaluate(
        completion_record=record,
        starting_value=1000.0,
        trading_fees=15.0,
        transfer_fees=10.0,
        other_costs=5.0,
        minimum_profit_percent=2.0,
    )

    assert result["pnl"]["net_final_value"] == 1000.0
    assert result["pnl"]["net_profit"] == 0.0
    assert result["pnl"]["profitable"] is False


def test_incomplete_route_is_blocked():
    evaluator = SimulatedRouteResultPnL()

    record = completed_route()
    record["route_complete"] = False

    result = evaluator.evaluate(
        completion_record=record,
        starting_value=1000.0,
    )

    assert result["evaluated"] is False
    assert result["reason"] == "completed_route_required"


def test_uncompleted_record_is_blocked():
    evaluator = SimulatedRouteResultPnL()

    record = completed_route()
    record["completed"] = False

    result = evaluator.evaluate(
        completion_record=record,
        starting_value=1000.0,
    )

    assert result["evaluated"] is False
    assert result["reason"] == "completed_route_required"


def test_non_simulated_route_is_blocked():
    evaluator = SimulatedRouteResultPnL()

    record = completed_route()
    record["simulated"] = False

    result = evaluator.evaluate(
        completion_record=record,
        starting_value=1000.0,
    )

    assert result["evaluated"] is False
    assert result["reason"] == "simulated_route_required"


def test_live_submission_is_blocked():
    evaluator = SimulatedRouteResultPnL()

    record = completed_route()
    record["live_order_submitted"] = True

    result = evaluator.evaluate(
        completion_record=record,
        starting_value=1000.0,
    )

    assert result["evaluated"] is False
    assert result["reason"] == "live_order_already_submitted"
    assert result["live_order_submitted"] is True


def test_control_identifiers_are_preserved():
    evaluator = SimulatedRouteResultPnL()

    result = evaluator.evaluate(
        completion_record=completed_route(),
        starting_value=1000.0,
    )

    assert result["route_id"] == "ROUTE-001"
    assert result["approval_id"] == "ARB-001"
    assert result["permission_id"] == "PERM-001"


def test_route_completion_metadata_is_preserved():
    evaluator = SimulatedRouteResultPnL()

    result = evaluator.evaluate(
        completion_record=completed_route(),
        starting_value=1000.0,
    )

    assert result["completed_leg_number"] == 3
    assert result["total_legs"] == 3
    assert result["final_symbol"] == "ETH/USDT"
    assert result["final_side"] == "sell"


def test_simulation_safety_flags_are_preserved():
    evaluator = SimulatedRouteResultPnL()

    result = evaluator.evaluate(
        completion_record=completed_route(),
        starting_value=1000.0,
    )

    assert result["test_trade"] is True
    assert result["simulated"] is True
    assert result["paper_trade"] is True
    assert result["live_order_submitted"] is False


def test_missing_completion_record_is_rejected():
    evaluator = SimulatedRouteResultPnL()

    with pytest.raises(
        ValueError,
        match="completion_record is required",
    ):
        evaluator.evaluate(
            completion_record=None,
            starting_value=1000.0,
        )


def test_invalid_starting_value_uses_existing_validation():
    evaluator = SimulatedRouteResultPnL()

    with pytest.raises(
        ValueError,
        match="starting_value must be positive",
    ):
        evaluator.evaluate(
            completion_record=completed_route(),
            starting_value=0.0,
        )


def test_negative_cost_uses_existing_validation():
    evaluator = SimulatedRouteResultPnL()

    with pytest.raises(
        ValueError,
        match="costs must be non-negative",
    ):
        evaluator.evaluate(
            completion_record=completed_route(),
            starting_value=1000.0,
            trading_fees=-1.0,
        )


def test_missing_final_output_amount_does_not_masquerade_as_zero():
    evaluator = SimulatedRouteResultPnL()

    record = completed_route()
    del record["final_output_amount"]

    result = evaluator.evaluate(
        completion_record=record,
        starting_value=1000.0,
    )

    assert result["evaluated"] is False
    assert result["reason"] == "final_output_amount_required"
    assert result["live_order_submitted"] is False


def test_explicit_none_final_output_amount_is_rejected():
    evaluator = SimulatedRouteResultPnL()

    record = completed_route()
    record["final_output_amount"] = None

    result = evaluator.evaluate(
        completion_record=record,
        starting_value=1000.0,
    )

    assert result["evaluated"] is False
    assert result["reason"] == "final_output_amount_required"
    assert result["live_order_submitted"] is False


def test_invalid_final_output_amount_is_rejected():
    evaluator = SimulatedRouteResultPnL()

    record = completed_route()
    record["final_output_amount"] = "not-a-number"

    result = evaluator.evaluate(
        completion_record=record,
        starting_value=1000.0,
    )

    assert result["evaluated"] is False
    assert result["reason"] == "final_output_amount_invalid"
    assert result["live_order_submitted"] is False


@pytest.mark.parametrize(
    "final_output_amount",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
        -1.0,
    ],
)
def test_non_finite_or_negative_final_output_amount_is_rejected(
    final_output_amount,
):
    evaluator = SimulatedRouteResultPnL()

    record = completed_route()
    record["final_output_amount"] = final_output_amount

    result = evaluator.evaluate(
        completion_record=record,
        starting_value=1000.0,
    )

    assert result["evaluated"] is False
    assert result["reason"] == "final_output_amount_invalid"
    assert result["live_order_submitted"] is False


def test_genuine_zero_final_output_amount_remains_numeric_zero():
    evaluator = SimulatedRouteResultPnL()

    record = completed_route()
    record["final_output_amount"] = 0.0

    result = evaluator.evaluate(
        completion_record=record,
        starting_value=1000.0,
    )

    assert result["evaluated"] is True
    assert result["pnl"]["gross_final_value"] == 0.0
