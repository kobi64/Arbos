import pytest

from core.live_paper_repeat_scale_cycle_orchestration import (
    LivePaperRepeatScaleCycleOrchestration,
)
from core.staged_test_trade_execution_permission import (
    StagedTestTradeExecutionPermission,
)


class FakeSnapshotEngine:
    def __init__(self):
        self.timestamp = 1000

    def snapshot(
        self,
        symbol,
        limit=None,
    ):
        self.timestamp += 1

        books = {
            "BTC/USDT": {
                "bids": [[61900.0, 10.0]],
                "asks": [[62000.0, 10.0]],
            },
            "ETH/BTC": {
                "bids": [[0.049, 100.0]],
                "asks": [[0.05, 100.0]],
            },
            "ETH/USDT": {
                "bids": [[3200.0, 100.0]],
                "asks": [[3210.0, 100.0]],
            },
        }

        book = books[symbol]

        return {
            "symbol": symbol,
            "bids": book["bids"],
            "asks": book["asks"],
            "timestamp": self.timestamp,
        }


def permission(
    trade_amount=250.0,
):
    return {
        "permission_id": "PERM-002",
        "route_id": "ROUTE-001",
        "approval_id": "ARB-002",
        "asset": "BTC",
        "trade_amount": trade_amount,
        "permission_granted": True,
        "status": (
            "execution_permission_granted"
        ),
        "live_order_submitted": False,
    }


def route():
    return {
        "route_id": "ROUTE-001",
        "legs": [
            {
                "symbol": "BTC/USDT",
                "side": "buy",
            },
            {
                "symbol": "ETH/BTC",
                "side": "buy",
            },
            {
                "symbol": "ETH/USDT",
                "side": "sell",
            },
        ],
    }


def portfolio():
    return {
        "total_capital": 1000.0,
        "reserved_capital": 0.0,
        "asset_exposure": {
            "BTC": 0.10,
        },
        "max_asset_exposure": 0.25,
        "open_routes": 0,
        "max_open_routes": 3,
    }


def orchestrator():
    return (
        LivePaperRepeatScaleCycleOrchestration(
            FakeSnapshotEngine()
        )
    )


def execute(
    permission_result=None,
    portfolio_result=None,
    starting_value=250.0,
    additional_exposure=0.05,
):
    return orchestrator().execute(
        permission_result=(
            permission()
            if permission_result is None
            else permission_result
        ),
        execution_id="EXEC-171-001",
        route=route(),
        portfolio=(
            portfolio()
            if portfolio_result is None
            else portfolio_result
        ),
        asset="BTC",
        additional_exposure=(
            additional_exposure
        ),
        starting_value=starting_value,
    )


def test_permitted_repeat_scale_route_completes():
    result = execute()

    assert result["executed"] is True
    assert result["status"] == "COMPLETED"
    assert (
        result["reason"]
        == "live_paper_repeat_scale_cycle_completed"
    )


def test_atomic_multi_leg_route_is_executed():
    result = execute()

    assert len(result["legs"]) == 3

    assert (
        result["legs"][0]["symbol"]
        == "BTC/USDT"
    )
    assert (
        result["legs"][1]["symbol"]
        == "ETH/BTC"
    )
    assert (
        result["legs"][2]["symbol"]
        == "ETH/USDT"
    )


def test_leg_output_is_chained_to_next_leg():
    result = execute()

    first = result["legs"][0]
    second = result["legs"][1]
    third = result["legs"][2]

    assert (
        second["input_amount"]
        == first["output_amount"]
    )

    assert (
        third["input_amount"]
        == second["output_amount"]
    )


def test_final_value_is_returned():
    result = execute()

    assert result["final_value"] > 0


def test_atomic_snapshot_flag_is_preserved():
    result = execute()

    for leg in result["legs"]:
        assert leg["atomic_snapshot"] is True


def test_permission_id_is_preserved():
    result = execute()

    assert result["permission_id"] == "PERM-002"


def test_approval_id_is_preserved():
    result = execute()

    assert result["approval_id"] == "ARB-002"


def test_trade_amount_is_preserved():
    result = execute()

    assert result["trade_amount"] == 250.0


def test_execution_permission_is_required():
    granted = permission()
    granted["permission_granted"] = False

    result = execute(
        permission_result=granted
    )

    assert result["executed"] is False
    assert (
        result["reason"]
        == "execution_permission_required"
    )


def test_permission_status_must_match_real_gate():
    granted = permission()
    granted["status"] = (
        "awaiting_execution_permission"
    )

    result = execute(
        permission_result=granted
    )

    assert result["executed"] is False
    assert (
        result["reason"]
        == "execution_permission_status_required"
    )


def test_live_submitted_permission_is_blocked():
    granted = permission()
    granted["live_order_submitted"] = True

    result = execute(
        permission_result=granted
    )

    assert result["executed"] is False
    assert (
        result["reason"]
        == "live_order_already_submitted"
    )


def test_permission_id_is_required():
    granted = permission()
    granted["permission_id"] = ""

    result = execute(
        permission_result=granted
    )

    assert result["executed"] is False
    assert result["reason"] == "permission_id_required"


def test_approval_id_is_required():
    granted = permission()
    granted["approval_id"] = ""

    result = execute(
        permission_result=granted
    )

    assert result["executed"] is False
    assert result["reason"] == "approval_id_required"


def test_exact_permitted_amount_is_required():
    result = execute(
        permission_result=permission(
            trade_amount=500.0
        ),
        starting_value=250.0,
    )

    assert result["executed"] is False
    assert (
        result["reason"]
        == "permitted_trade_amount_mismatch"
    )


def test_scaled_amount_can_execute_when_permission_matches():
    result = execute(
        permission_result=permission(
            trade_amount=500.0
        ),
        starting_value=500.0,
    )

    assert result["executed"] is True
    assert result["trade_amount"] == 500.0


def test_portfolio_exposure_failure_blocks_route():
    risky = portfolio()
    risky["asset_exposure"]["BTC"] = 0.24

    result = execute(
        portfolio_result=risky,
        additional_exposure=0.05,
    )

    assert result["executed"] is False
    assert result["reason"] == "asset_exposure_exceeded"


def test_concurrent_route_limit_blocks_route():
    risky = portfolio()
    risky["open_routes"] = 3
    risky["max_open_routes"] = 3

    result = execute(
        portfolio_result=risky
    )

    assert result["executed"] is False
    assert (
        result["reason"]
        == "concurrent_route_limit_reached"
    )


def test_insufficient_capital_blocks_route():
    risky = portfolio()
    risky["reserved_capital"] = 900.0

    result = execute(
        portfolio_result=risky,
        starting_value=250.0,
    )

    assert result["executed"] is False
    assert (
        result["reason"]
        == "insufficient_unreserved_capital"
    )


def test_capital_reservation_is_released():
    service = orchestrator()

    result = service.execute(
        permission_result=permission(),
        execution_id="EXEC-171-002",
        route=route(),
        portfolio=portfolio(),
        asset="BTC",
        additional_exposure=0.05,
        starting_value=250.0,
    )

    assert result["executed"] is True
    assert result["reservation_released"] is True
    assert service.total_reserved() == 0.0


def test_real_single_use_permission_output_is_accepted():
    gate = (
        StagedTestTradeExecutionPermission()
    )

    request = gate.create(
        handoff_result={
            "handoff_ready": True,
            "route_id": "ROUTE-001",
            "approval_id": "ARB-002",
            "asset": "BTC",
            "trade_amount": 250.0,
            "live_order_submitted": False,
        }
    )

    granted = gate.grant(
        permission_id=request[
            "permission_id"
        ],
        trade_amount=250.0,
    )

    result = execute(
        permission_result=granted
    )

    assert granted["permission_granted"] is True
    assert result["executed"] is True


def test_missing_permission_result_is_rejected():
    with pytest.raises(
        ValueError,
        match="permission_result is required",
    ):
        orchestrator().execute(
            permission_result=None,
            execution_id="EXEC-171-003",
            route=route(),
            portfolio=portfolio(),
            asset="BTC",
            additional_exposure=0.05,
            starting_value=250.0,
        )


def test_missing_route_is_rejected():
    with pytest.raises(
        ValueError,
        match="route is required",
    ):
        orchestrator().execute(
            permission_result=permission(),
            execution_id="EXEC-171-004",
            route=None,
            portfolio=portfolio(),
            asset="BTC",
            additional_exposure=0.05,
            starting_value=250.0,
        )


def test_invalid_starting_value_is_rejected():
    with pytest.raises(
        ValueError,
        match="starting_value must be positive",
    ):
        execute(
            permission_result=permission(
                trade_amount=250.0
            ),
            starting_value=0.0,
        )


def test_snapshot_engine_is_required():
    with pytest.raises(
        ValueError,
        match="snapshot_engine is required",
    ):
        LivePaperRepeatScaleCycleOrchestration(
            None
        )


def test_success_is_recorded_in_history():
    service = orchestrator()

    service.execute(
        permission_result=permission(),
        execution_id="EXEC-171-005",
        route=route(),
        portfolio=portfolio(),
        asset="BTC",
        additional_exposure=0.05,
        starting_value=250.0,
    )

    assert len(service.history()) == 1
    assert service.history()[0]["executed"] is True


def test_risk_rejection_is_recorded_in_history():
    service = orchestrator()

    risky = portfolio()
    risky["asset_exposure"]["BTC"] = 0.24

    service.execute(
        permission_result=permission(),
        execution_id="EXEC-171-006",
        route=route(),
        portfolio=risky,
        asset="BTC",
        additional_exposure=0.05,
        starting_value=250.0,
    )

    assert len(service.history()) == 1
    assert service.history()[0]["executed"] is False


def test_entire_orchestration_remains_paper_only():
    result = execute()

    assert result["paper_only"] is True
    assert result["test_trade"] is True
    assert result["simulated"] is True
    assert result["paper_trade"] is True
    assert result["live_order_submitted"] is False
