import pytest

from core.simulated_multi_leg_route_completion import (
    SimulatedMultiLegRouteCompletion,
)


def final_fill():
    return {
        "fill_captured": True,
        "reason": "simulated_test_trade_fill_captured",
        "status": "FILLED",
        "simulated": True,
        "paper_trade": True,
        "paper_order_id": "PAPER-000003",
        "order_id": "order-3",
        "route_id": "ROUTE-001",
        "approval_id": "ARB-001",
        "permission_id": "PERM-001",
        "filled_quantity": 0.2,
        "average_price": 3200.0,
        "notional": 640.0,
        "test_trade": True,
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


def test_final_leg_completes_simulated_route():
    completer = SimulatedMultiLegRouteCompletion()

    result = completer.complete(
        final_fill=final_fill(),
        route=route(),
        completed_leg_number=3,
    )

    assert result["completed"] is True
    assert result["route_complete"] is True
    assert (
        result["reason"]
        == "simulated_multi_leg_route_complete"
    )
    assert result["completed_leg_number"] == 3
    assert result["total_legs"] == 3


def test_final_sell_output_uses_notional():
    completer = SimulatedMultiLegRouteCompletion()

    result = completer.complete(
        final_fill=final_fill(),
        route=route(),
        completed_leg_number=3,
    )

    assert result["final_side"] == "sell"
    assert result["final_output_amount"] == 640.0
    assert result["final_notional"] == 640.0


def test_final_buy_output_uses_filled_quantity():
    completer = SimulatedMultiLegRouteCompletion()

    test_route = route()
    test_route["legs"][-1]["side"] = "buy"

    result = completer.complete(
        final_fill=final_fill(),
        route=test_route,
        completed_leg_number=3,
    )

    assert result["final_side"] == "buy"
    assert result["final_output_amount"] == 0.2


def test_non_final_leg_does_not_complete_route():
    completer = SimulatedMultiLegRouteCompletion()

    result = completer.complete(
        final_fill=final_fill(),
        route=route(),
        completed_leg_number=2,
    )

    assert result["completed"] is False
    assert result["route_complete"] is False
    assert result["reason"] == "final_leg_required"
    assert result["total_legs"] == 3


def test_route_id_must_match_final_fill():
    completer = SimulatedMultiLegRouteCompletion()

    fill = final_fill()
    fill["route_id"] = "OTHER-ROUTE"

    result = completer.complete(
        final_fill=fill,
        route=route(),
        completed_leg_number=3,
    )

    assert result["completed"] is False
    assert result["reason"] == "route_id_mismatch"


def test_uncaptured_final_fill_is_blocked():
    completer = SimulatedMultiLegRouteCompletion()

    fill = final_fill()
    fill["fill_captured"] = False

    result = completer.complete(
        final_fill=fill,
        route=route(),
        completed_leg_number=3,
    )

    assert result["completed"] is False
    assert result["reason"] == "captured_fill_required"


def test_live_submission_is_blocked():
    completer = SimulatedMultiLegRouteCompletion()

    fill = final_fill()
    fill["live_order_submitted"] = True

    result = completer.complete(
        final_fill=fill,
        route=route(),
        completed_leg_number=3,
    )

    assert result["completed"] is False
    assert result["reason"] == "live_order_already_submitted"
    assert result["live_order_submitted"] is True


def test_empty_route_is_rejected():
    completer = SimulatedMultiLegRouteCompletion()

    test_route = {
        "route_id": "ROUTE-001",
        "legs": [],
    }

    result = completer.complete(
        final_fill=final_fill(),
        route=test_route,
        completed_leg_number=0,
    )

    assert result["completed"] is False
    assert result["reason"] == "route_legs_required"


def test_control_identifiers_are_preserved():
    completer = SimulatedMultiLegRouteCompletion()

    result = completer.complete(
        final_fill=final_fill(),
        route=route(),
        completed_leg_number=3,
    )

    assert result["route_id"] == "ROUTE-001"
    assert result["approval_id"] == "ARB-001"
    assert result["permission_id"] == "PERM-001"
    assert result["test_trade"] is True
    assert result["simulated"] is True
    assert result["paper_trade"] is True
    assert result["live_order_submitted"] is False


def test_final_leg_identity_is_recorded():
    completer = SimulatedMultiLegRouteCompletion()

    result = completer.complete(
        final_fill=final_fill(),
        route=route(),
        completed_leg_number=3,
    )

    assert result["final_symbol"] == "ETH/USDT"
    assert result["final_side"] == "sell"
    assert result["final_filled_quantity"] == 0.2


def test_missing_final_fill_is_rejected():
    completer = SimulatedMultiLegRouteCompletion()

    with pytest.raises(
        ValueError,
        match="final_fill is required",
    ):
        completer.complete(
            final_fill=None,
            route=route(),
            completed_leg_number=3,
        )


def test_missing_route_is_rejected():
    completer = SimulatedMultiLegRouteCompletion()

    with pytest.raises(
        ValueError,
        match="route is required",
    ):
        completer.complete(
            final_fill=final_fill(),
            route=None,
            completed_leg_number=3,
        )
