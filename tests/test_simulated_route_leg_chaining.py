import pytest

from core.simulated_route_leg_chaining import (
    SimulatedRouteLegChaining,
)


def captured_fill():
    return {
        "fill_captured": True,
        "reason": "simulated_test_trade_fill_captured",
        "status": "FILLED",
        "simulated": True,
        "paper_trade": True,
        "paper_order_id": "PAPER-000001",
        "order_id": "order-1",
        "route_id": "ROUTE-001",
        "approval_id": "ARB-001",
        "permission_id": "PERM-001",
        "filled_quantity": 0.01,
        "average_price": 62000.0,
        "notional": 620.0,
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


def test_buy_fill_output_becomes_next_leg_quantity():
    chainer = SimulatedRouteLegChaining()

    result = chainer.chain(
        fill_record=captured_fill(),
        route=route(),
        completed_leg_number=1,
    )

    assert result["ready"] is True
    assert result["reason"] == "next_simulated_leg_ready"
    assert result["next_leg_number"] == 2
    assert result["next_leg"]["symbol"] == "ETH/BTC"
    assert result["next_leg"]["side"] == "buy"
    assert result["next_leg"]["quantity"] == 0.01


def test_sell_fill_output_uses_notional():
    chainer = SimulatedRouteLegChaining()

    fill = captured_fill()
    fill["filled_quantity"] = 0.2
    fill["average_price"] = 3200.0
    fill["notional"] = 640.0

    result = chainer.chain(
        fill_record=fill,
        route=route(),
        completed_leg_number=2,
        completed_leg_side="sell",
    )

    assert result["ready"] is True
    assert result["next_leg_number"] == 3
    assert result["next_leg"]["quantity"] == 640.0


def test_final_leg_returns_route_complete():
    chainer = SimulatedRouteLegChaining()

    result = chainer.chain(
        fill_record=captured_fill(),
        route=route(),
        completed_leg_number=3,
    )

    assert result["ready"] is False
    assert result["route_complete"] is True
    assert result["reason"] == "simulated_route_complete"
    assert result["live_order_submitted"] is False


def test_route_id_must_match_fill():
    chainer = SimulatedRouteLegChaining()

    fill = captured_fill()
    fill["route_id"] = "OTHER-ROUTE"

    result = chainer.chain(
        fill_record=fill,
        route=route(),
        completed_leg_number=1,
    )

    assert result["ready"] is False
    assert result["reason"] == "route_id_mismatch"


def test_uncaptured_fill_is_blocked():
    chainer = SimulatedRouteLegChaining()

    fill = captured_fill()
    fill["fill_captured"] = False

    result = chainer.chain(
        fill_record=fill,
        route=route(),
        completed_leg_number=1,
    )

    assert result["ready"] is False
    assert result["reason"] == "captured_fill_required"


def test_live_submission_is_blocked():
    chainer = SimulatedRouteLegChaining()

    fill = captured_fill()
    fill["live_order_submitted"] = True

    result = chainer.chain(
        fill_record=fill,
        route=route(),
        completed_leg_number=1,
    )

    assert result["ready"] is False
    assert result["reason"] == "live_order_already_submitted"
    assert result["live_order_submitted"] is True


def test_control_identifiers_are_preserved():
    chainer = SimulatedRouteLegChaining()

    result = chainer.chain(
        fill_record=captured_fill(),
        route=route(),
        completed_leg_number=1,
    )

    assert result["route_id"] == "ROUTE-001"
    assert result["approval_id"] == "ARB-001"
    assert result["permission_id"] == "PERM-001"
    assert result["test_trade"] is True
    assert result["live_order_submitted"] is False


def test_missing_fill_is_rejected():
    chainer = SimulatedRouteLegChaining()

    with pytest.raises(
        ValueError,
        match="fill_record is required",
    ):
        chainer.chain(
            fill_record=None,
            route=route(),
            completed_leg_number=1,
        )


def test_missing_route_is_rejected():
    chainer = SimulatedRouteLegChaining()

    with pytest.raises(
        ValueError,
        match="route is required",
    ):
        chainer.chain(
            fill_record=captured_fill(),
            route=None,
            completed_leg_number=1,
        )
