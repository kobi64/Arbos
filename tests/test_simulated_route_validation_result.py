import pytest

from core.simulated_route_validation_result import (
    SimulatedRouteValidationResult,
)


def profitable_pnl_record():
    return {
        "evaluated": True,
        "reason": "simulated_route_pnl_evaluated",
        "route_id": "ROUTE-001",
        "approval_id": "ARB-001",
        "permission_id": "PERM-001",
        "completed_leg_number": 3,
        "total_legs": 3,
        "final_symbol": "ETH/USDT",
        "final_side": "sell",
        "pnl": {
            "starting_value": 1000.0,
            "gross_final_value": 1050.0,
            "trading_fees": 5.0,
            "transfer_fees": 2.0,
            "other_costs": 3.0,
            "total_costs": 10.0,
            "net_final_value": 1040.0,
            "net_profit": 40.0,
            "profit_percent": 4.0,
            "profitable": True,
            "reason": "ok",
        },
        "test_trade": True,
        "simulated": True,
        "paper_trade": True,
        "live_order_submitted": False,
    }


def test_profitable_simulated_route_is_accepted():
    validator = SimulatedRouteValidationResult()

    result = validator.validate(
        profitable_pnl_record()
    )

    assert result["validated"] is True
    assert result["accepted"] is True
    assert (
        result["reason"]
        == "simulated_route_validation_passed"
    )


def test_unprofitable_route_is_rejected():
    validator = SimulatedRouteValidationResult()

    record = profitable_pnl_record()
    record["pnl"]["profitable"] = False
    record["pnl"]["net_profit"] = 5.0
    record["pnl"]["profit_percent"] = 0.5
    record["pnl"]["reason"] = (
        "below_minimum_profit"
    )

    result = validator.validate(
        record
    )

    assert result["validated"] is True
    assert result["accepted"] is False
    assert (
        result["reason"]
        == "simulated_route_not_profitable"
    )


def test_profit_details_are_preserved():
    validator = SimulatedRouteValidationResult()

    result = validator.validate(
        profitable_pnl_record()
    )

    assert result["net_profit"] == 40.0
    assert result["profit_percent"] == 4.0
    assert result["profitability_reason"] == "ok"


def test_control_identifiers_are_preserved():
    validator = SimulatedRouteValidationResult()

    result = validator.validate(
        profitable_pnl_record()
    )

    assert result["route_id"] == "ROUTE-001"
    assert result["approval_id"] == "ARB-001"
    assert result["permission_id"] == "PERM-001"


def test_completion_metadata_is_preserved():
    validator = SimulatedRouteValidationResult()

    result = validator.validate(
        profitable_pnl_record()
    )

    assert result["completed_leg_number"] == 3
    assert result["total_legs"] == 3
    assert result["final_symbol"] == "ETH/USDT"
    assert result["final_side"] == "sell"


def test_unevaluated_pnl_is_blocked():
    validator = SimulatedRouteValidationResult()

    record = profitable_pnl_record()
    record["evaluated"] = False

    result = validator.validate(
        record
    )

    assert result["validated"] is False
    assert result["accepted"] is False
    assert result["reason"] == "evaluated_pnl_required"


def test_non_simulated_route_is_blocked():
    validator = SimulatedRouteValidationResult()

    record = profitable_pnl_record()
    record["simulated"] = False

    result = validator.validate(
        record
    )

    assert result["validated"] is False
    assert result["accepted"] is False
    assert result["reason"] == "simulated_route_required"


def test_non_test_trade_is_blocked():
    validator = SimulatedRouteValidationResult()

    record = profitable_pnl_record()
    record["test_trade"] = False

    result = validator.validate(
        record
    )

    assert result["validated"] is False
    assert result["accepted"] is False
    assert result["reason"] == "test_trade_required"


def test_live_submission_is_blocked():
    validator = SimulatedRouteValidationResult()

    record = profitable_pnl_record()
    record["live_order_submitted"] = True

    result = validator.validate(
        record
    )

    assert result["validated"] is False
    assert result["accepted"] is False
    assert result["reason"] == "live_order_already_submitted"
    assert result["live_order_submitted"] is True


def test_simulation_safety_flags_are_preserved():
    validator = SimulatedRouteValidationResult()

    result = validator.validate(
        profitable_pnl_record()
    )

    assert result["test_trade"] is True
    assert result["simulated"] is True
    assert result["paper_trade"] is True
    assert result["live_order_submitted"] is False


def test_missing_record_is_rejected():
    validator = SimulatedRouteValidationResult()

    with pytest.raises(
        ValueError,
        match="pnl_record is required",
    ):
        validator.validate(
            None
        )


def test_missing_nested_pnl_is_rejected():
    validator = SimulatedRouteValidationResult()

    record = profitable_pnl_record()
    record.pop("pnl")

    with pytest.raises(
        ValueError,
        match="pnl is required",
    ):
        validator.validate(
            record
        )


def test_existing_gate_validation_is_reused():
    validator = SimulatedRouteValidationResult()

    record = profitable_pnl_record()
    record["pnl"].pop(
        "profit_percent"
    )

    with pytest.raises(
        ValueError,
        match="profit_percent is required",
    ):
        validator.validate(
            record
        )
