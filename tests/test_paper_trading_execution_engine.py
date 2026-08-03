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
