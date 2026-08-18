import pytest

from exchanges.paper_trading_execution_engine import (
    PaperTradingExecutionEngine,
)


@pytest.fixture
def engine():
    return PaperTradingExecutionEngine()


def valid_order():
    return {
        "symbol": "BTC/USDT",
        "side": "buy",
        "order_type": "market",
        "quantity": 0.01,
        "price": 62000.0,
    }


def test_market_order_executes(engine):
    result = engine.execute(valid_order())

    assert result["status"] == "FILLED"


def test_order_receives_unique_id(engine):
    first = engine.execute(valid_order())
    second = engine.execute(valid_order())

    assert first["paper_order_id"] != second["paper_order_id"]


def test_execution_is_marked_as_paper(engine):
    result = engine.execute(valid_order())

    assert result["paper_trade"] is True


def test_execution_time_is_recorded(engine):
    result = engine.execute(valid_order())

    assert "executed_at" in result


def test_execution_history_grows(engine):
    engine.execute(valid_order())
    engine.execute(valid_order())

    assert len(engine.history()) == 2


def test_missing_order_is_rejected(engine):
    with pytest.raises(ValueError, match="order is required"):
        engine.execute(None)


def test_invalid_quantity_is_rejected(engine):
    order = valid_order()
    order["quantity"] = 0

    with pytest.raises(ValueError):
        engine.execute(order)


def test_missing_symbol_is_rejected(engine):
    order = valid_order()
    del order["symbol"]

    with pytest.raises(ValueError):
        engine.execute(order)


def test_average_price_matches_order_price(engine):
    result = engine.execute(valid_order())

    assert result["average_price"] == 62000.0


def test_filled_quantity_matches_order_quantity(engine):
    result = engine.execute(valid_order())

    assert result["filled_quantity"] == 0.01


@pytest.mark.parametrize(
    "quantity",
    [
        None,
        "not-a-number",
        float("nan"),
        float("inf"),
        float("-inf"),
        0.0,
        -1.0,
    ],
)
def test_invalid_numeric_quantity_values_are_rejected(
    engine,
    quantity,
):
    order = valid_order()
    order["quantity"] = quantity

    with pytest.raises(
        ValueError,
        match="quantity must be positive",
    ):
        engine.execute(order)


@pytest.mark.parametrize(
    "price",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
        0.0,
        -1.0,
    ],
)
def test_invalid_numeric_price_values_are_rejected(
    engine,
    price,
):
    order = valid_order()
    order["price"] = price

    with pytest.raises(
        ValueError,
        match="price must be positive",
    ):
        engine.execute(order)


@pytest.mark.parametrize(
    "price",
    [
        None,
        "not-a-number",
    ],
)
def test_missing_or_non_numeric_price_is_rejected(
    engine,
    price,
):
    order = valid_order()
    order["price"] = price

    with pytest.raises(
        ValueError,
        match="price is required",
    ):
        engine.execute(order)


def test_numeric_strings_are_normalized_to_floats(engine):
    order = valid_order()
    order["quantity"] = "0.01"
    order["price"] = "62000"

    result = engine.execute(order)

    assert result["filled_quantity"] == 0.01
    assert result["average_price"] == 62000.0
    assert result["notional"] == 620.0
    assert isinstance(result["filled_quantity"], float)
    assert isinstance(result["average_price"], float)
    assert isinstance(result["notional"], float)


def test_successful_execution_outputs_are_finite(engine):
    import math

    result = engine.execute(valid_order())

    assert math.isfinite(result["filled_quantity"])
    assert math.isfinite(result["average_price"])
    assert math.isfinite(result["notional"])


def test_rejected_execution_does_not_change_history(engine):
    order = valid_order()
    order["quantity"] = float("nan")

    with pytest.raises(ValueError):
        engine.execute(order)

    assert engine.history() == []


def test_rejected_execution_does_not_consume_order_id(engine):
    invalid = valid_order()
    invalid["price"] = float("inf")

    with pytest.raises(ValueError):
        engine.execute(invalid)

    result = engine.execute(valid_order())

    assert result["paper_order_id"] == "PAPER-000001"
