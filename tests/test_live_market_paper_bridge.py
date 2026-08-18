import pytest

from exchanges.live_market_paper_bridge import LiveMarketPaperBridge


class FakeMarketDataProvider:
    def __init__(self, prices=None):
        self.prices = prices if prices is not None else {"BTC/USDT": 62000.0}

    def get_price(self, symbol):
        return self.prices.get(symbol)


@pytest.fixture
def bridge():
    return LiveMarketPaperBridge(FakeMarketDataProvider())


def valid_order():
    return {
        "symbol": "BTC/USDT",
        "side": "buy",
        "order_type": "market",
        "quantity": 0.01,
    }


def test_live_price_is_used_for_paper_execution(bridge):
    result = bridge.execute(valid_order())

    assert result["status"] == "FILLED"
    assert result["average_price"] == 62000.0
    assert result["market_price"] == 62000.0


def test_result_remains_paper_trade(bridge):
    result = bridge.execute(valid_order())

    assert result["paper_trade"] is True
    assert result["live_order_submitted"] is False


def test_notional_uses_live_price(bridge):
    result = bridge.execute(valid_order())

    assert result["notional"] == 620.0


def test_provider_is_queried_with_order_symbol():
    provider = FakeMarketDataProvider({"ETH/USDT": 3100.0})
    bridge = LiveMarketPaperBridge(provider)
    order = valid_order()
    order["symbol"] = "ETH/USDT"

    result = bridge.execute(order)

    assert result["average_price"] == 3100.0


def test_missing_market_price_is_rejected():
    bridge = LiveMarketPaperBridge(FakeMarketDataProvider({}))

    with pytest.raises(ValueError, match="market price unavailable"):
        bridge.execute(valid_order())


def test_none_order_is_rejected(bridge):
    with pytest.raises(ValueError, match="order is required"):
        bridge.execute(None)


def test_invalid_quantity_is_rejected(bridge):
    order = valid_order()
    order["quantity"] = 0

    with pytest.raises(ValueError, match="quantity must be positive"):
        bridge.execute(order)
        bridge.execute(order)


def test_missing_symbol_is_rejected(bridge):
    order = valid_order()
    del order["symbol"]

    with pytest.raises(ValueError, match="symbol is required"):
        bridge.execute(order)


def test_history_is_recorded(bridge):
    bridge.execute(valid_order())

    assert len(bridge.history()) == 1


def test_each_execution_gets_unique_paper_order_id(bridge):
    first = bridge.execute(valid_order())
    second = bridge.execute(valid_order())

    assert first["paper_order_id"] != second["paper_order_id"]


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
    bridge,
    quantity,
):
    order = valid_order()
    order["quantity"] = quantity

    with pytest.raises(
        ValueError,
        match="quantity must be positive",
    ):
        bridge.execute(order)


def test_missing_quantity_is_rejected(bridge):
    order = valid_order()
    del order["quantity"]

    with pytest.raises(
        ValueError,
        match="quantity must be positive",
    ):
        bridge.execute(order)


@pytest.mark.parametrize(
    "market_price",
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
def test_invalid_numeric_market_prices_are_rejected(
    market_price,
):
    provider = FakeMarketDataProvider(
        {
            "BTC/USDT": market_price,
        }
    )

    paper_bridge = LiveMarketPaperBridge(
        provider
    )

    with pytest.raises(
        ValueError,
        match="market price unavailable",
    ):
        paper_bridge.execute(
            valid_order()
        )


def test_numeric_strings_are_normalized():
    provider = FakeMarketDataProvider(
        {
            "BTC/USDT": "62000",
        }
    )

    paper_bridge = LiveMarketPaperBridge(
        provider
    )

    order = valid_order()
    order["quantity"] = "0.01"

    result = paper_bridge.execute(
        order
    )

    assert result["filled_quantity"] == 0.01
    assert result["average_price"] == 62000.0
    assert result["notional"] == 620.0
    assert result["market_price"] == 62000.0
