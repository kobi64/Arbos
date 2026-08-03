import pytest

from exchanges.dry_run_execution_adapter import (
    DryRunExecutionAdapter,
)


@pytest.fixture
def adapter():
    return DryRunExecutionAdapter()


def market_order():
    return {
        "symbol": "BTC/USDT",
        "side": "buy",
        "order_type": "market",
        "quantity": 0.01,
        "reference_price": 62000.0,
    }


def test_market_order_is_simulated(adapter):
    result = adapter.execute(market_order())

    assert result["status"] == "FILLED"
    assert result["simulated"] is True
    assert result["filled_quantity"] == 0.01


def test_market_order_uses_reference_price(adapter):
    result = adapter.execute(market_order())

    assert result["average_price"] == 62000.0


def test_limit_buy_fills_when_price_is_reachable(adapter):
    order = market_order()
    order["order_type"] = "limit"
    order["limit_price"] = 62500.0

    result = adapter.execute(order)

    assert result["status"] == "FILLED"


def test_limit_buy_remains_open_when_price_is_too_low(adapter):
    order = market_order()
    order["order_type"] = "limit"
    order["limit_price"] = 61000.0

    result = adapter.execute(order)

    assert result["status"] == "OPEN"
    assert result["filled_quantity"] == 0.0


def test_limit_sell_fills_when_price_is_reachable(adapter):
    order = market_order()
    order["side"] = "sell"
    order["order_type"] = "limit"
    order["limit_price"] = 61500.0

    result = adapter.execute(order)

    assert result["status"] == "FILLED"


def test_limit_sell_remains_open_when_price_is_too_high(adapter):
    order = market_order()
    order["side"] = "sell"
    order["order_type"] = "limit"
    order["limit_price"] = 63000.0

    result = adapter.execute(order)

    assert result["status"] == "OPEN"


def test_notional_is_calculated(adapter):
    result = adapter.execute(market_order())

    assert result["notional"] == 620.0


def test_none_order_is_rejected(adapter):
    with pytest.raises(ValueError, match="order is required"):
        adapter.execute(None)


def test_missing_reference_price_is_rejected(adapter):
    order = market_order()
    del order["reference_price"]

    with pytest.raises(ValueError, match="reference_price is required"):
        adapter.execute(order)


def test_invalid_quantity_is_rejected(adapter):
    order = market_order()
    order["quantity"] = 0

    with pytest.raises(ValueError, match="quantity must be positive"):
        adapter.execute(order)
