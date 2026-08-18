import pytest

from core.simulated_test_trade_fill_capture import (
    SimulatedTestTradeFillCapture,
)


def simulated_fill():
    return {
        "simulated": True,
        "status": "FILLED",
        "paper_trade": True,
        "paper_order_id": "PAPER-000001",
        "filled_quantity": 0.05,
        "average_price": 3200.0,
        "notional": 160.0,
        "market_price": 3200.0,
        "order_id": "order-1",
        "route_id": "DIRECT-ETH",
        "approval_id": "ARB-001",
        "permission_id": "PERM-001",
        "test_trade": True,
        "live_order_submitted": False,
    }


def test_captures_completed_simulated_fill():
    capture = SimulatedTestTradeFillCapture()

    result = capture.capture(
        execution_result=simulated_fill(),
    )

    assert result["fill_captured"] is True
    assert result["reason"] == "simulated_test_trade_fill_captured"
    assert result["status"] == "FILLED"
    assert result["simulated"] is True
    assert result["test_trade"] is True
    assert result["live_order_submitted"] is False


def test_preserves_fill_values():
    capture = SimulatedTestTradeFillCapture()

    result = capture.capture(
        execution_result=simulated_fill(),
    )

    assert result["filled_quantity"] == 0.05
    assert result["average_price"] == 3200.0
    assert result["notional"] == 160.0


def test_preserves_control_identifiers():
    capture = SimulatedTestTradeFillCapture()

    result = capture.capture(
        execution_result=simulated_fill(),
    )

    assert result["paper_order_id"] == "PAPER-000001"
    assert result["order_id"] == "order-1"
    assert result["route_id"] == "DIRECT-ETH"
    assert result["approval_id"] == "ARB-001"
    assert result["permission_id"] == "PERM-001"


def test_non_simulated_execution_is_blocked():
    capture = SimulatedTestTradeFillCapture()

    execution = simulated_fill()
    execution["simulated"] = False

    result = capture.capture(
        execution_result=execution,
    )

    assert result["fill_captured"] is False
    assert result["reason"] == "simulated_execution_required"
    assert result["live_order_submitted"] is False


def test_non_filled_execution_is_not_captured():
    capture = SimulatedTestTradeFillCapture()

    execution = simulated_fill()
    execution["status"] = "OPEN"
    execution["filled_quantity"] = 0.0
    execution["average_price"] = None
    execution["notional"] = 0.0

    result = capture.capture(
        execution_result=execution,
    )

    assert result["fill_captured"] is False
    assert result["reason"] == "simulated_trade_not_filled"
    assert result["live_order_submitted"] is False


def test_non_test_trade_is_blocked():
    capture = SimulatedTestTradeFillCapture()

    execution = simulated_fill()
    execution["test_trade"] = False

    result = capture.capture(
        execution_result=execution,
    )

    assert result["fill_captured"] is False
    assert result["reason"] == "test_trade_required"
    assert result["live_order_submitted"] is False


def test_existing_live_submission_is_blocked():
    capture = SimulatedTestTradeFillCapture()

    execution = simulated_fill()
    execution["live_order_submitted"] = True

    result = capture.capture(
        execution_result=execution,
    )

    assert result["fill_captured"] is False
    assert result["reason"] == "live_order_already_submitted"
    assert result["live_order_submitted"] is True


def test_missing_execution_result_is_rejected():
    capture = SimulatedTestTradeFillCapture()

    with pytest.raises(
        ValueError,
        match="execution_result is required",
    ):
        capture.capture(
            execution_result=None,
        )


def test_fill_record_is_normalized_to_float_values():
    capture = SimulatedTestTradeFillCapture()

    execution = simulated_fill()
    execution["filled_quantity"] = "0.05"
    execution["average_price"] = "3200"
    execution["notional"] = "160"

    result = capture.capture(
        execution_result=execution,
    )

    assert result["filled_quantity"] == 0.05
    assert result["average_price"] == 3200.0
    assert result["notional"] == 160.0


@pytest.mark.parametrize(
    "field",
    [
        "filled_quantity",
        "average_price",
        "notional",
    ],
)
def test_missing_filled_execution_values_are_rejected(field):
    capture = SimulatedTestTradeFillCapture()

    execution = simulated_fill()
    del execution[field]

    result = capture.capture(
        execution_result=execution,
    )

    assert result["fill_captured"] is False
    assert result["reason"] == "invalid_simulated_fill_values"
    assert result["live_order_submitted"] is False


@pytest.mark.parametrize(
    "field",
    [
        "filled_quantity",
        "average_price",
        "notional",
    ],
)
def test_none_filled_execution_values_are_rejected(field):
    capture = SimulatedTestTradeFillCapture()

    execution = simulated_fill()
    execution[field] = None

    result = capture.capture(
        execution_result=execution,
    )

    assert result["fill_captured"] is False
    assert result["reason"] == "invalid_simulated_fill_values"


@pytest.mark.parametrize(
    "field",
    [
        "filled_quantity",
        "average_price",
        "notional",
    ],
)
def test_non_numeric_filled_execution_values_are_rejected(field):
    capture = SimulatedTestTradeFillCapture()

    execution = simulated_fill()
    execution[field] = "not-a-number"

    result = capture.capture(
        execution_result=execution,
    )

    assert result["fill_captured"] is False
    assert result["reason"] == "invalid_simulated_fill_values"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("filled_quantity", 0.0),
        ("filled_quantity", -1.0),
        ("average_price", 0.0),
        ("average_price", -1.0),
        ("notional", -1.0),
    ],
)
def test_invalid_numeric_fill_values_are_rejected(
    field,
    value,
):
    capture = SimulatedTestTradeFillCapture()

    execution = simulated_fill()
    execution[field] = value

    result = capture.capture(
        execution_result=execution,
    )

    assert result["fill_captured"] is False
    assert result["reason"] == "invalid_simulated_fill_values"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("filled_quantity", float("nan")),
        ("filled_quantity", float("inf")),
        ("average_price", float("nan")),
        ("average_price", float("inf")),
        ("notional", float("nan")),
        ("notional", float("inf")),
    ],
)
def test_non_finite_fill_values_are_rejected(
    field,
    value,
):
    capture = SimulatedTestTradeFillCapture()

    execution = simulated_fill()
    execution[field] = value

    result = capture.capture(
        execution_result=execution,
    )

    assert result["fill_captured"] is False
    assert result["reason"] == "invalid_simulated_fill_values"


def test_genuine_numeric_string_fill_values_still_normalize():
    capture = SimulatedTestTradeFillCapture()

    execution = simulated_fill()
    execution["filled_quantity"] = "0.05"
    execution["average_price"] = "3200"
    execution["notional"] = "160"

    result = capture.capture(
        execution_result=execution,
    )

    assert result["fill_captured"] is True
    assert result["filled_quantity"] == 0.05
    assert result["average_price"] == 3200.0
    assert result["notional"] == 160.0
