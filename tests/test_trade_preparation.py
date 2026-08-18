import pytest

from exchanges.trade_preparation import TradePreparation


def test_creates_trade_plan_successfully():
    result = TradePreparation.prepare(
        asset="BTC",
        buy_exchange="ExchangeA",
        sell_exchange="ExchangeB",
        trade_amount=1000.0,
        expected_profit=25.0,
        estimated_fees=5.0,
        slippage_allowance=2.0,
    )

    assert result["ready"] is True
    assert result["trade"]["asset"] == "BTC"
    assert result["trade"]["trade_amount"] == 1000.0


def test_calculates_net_expected_profit():
    result = TradePreparation.prepare(
        asset="ETH",
        buy_exchange="ExchangeA",
        sell_exchange="ExchangeB",
        trade_amount=2000.0,
        expected_profit=50.0,
        estimated_fees=10.0,
        slippage_allowance=5.0,
    )

    assert result["trade"]["net_profit"] == 35.0


def test_preserves_execution_route():
    result = TradePreparation.prepare(
        asset="SOL",
        buy_exchange="ExchangeA",
        sell_exchange="ExchangeB",
        trade_amount=500.0,
        expected_profit=20.0,
        estimated_fees=2.0,
        slippage_allowance=1.0,
    )

    assert result["trade"]["buy_exchange"] == "ExchangeA"
    assert result["trade"]["sell_exchange"] == "ExchangeB"


def test_rejects_zero_trade_amount():
    result = TradePreparation.prepare(
        asset="BTC",
        buy_exchange="ExchangeA",
        sell_exchange="ExchangeB",
        trade_amount=0,
        expected_profit=20.0,
        estimated_fees=2.0,
        slippage_allowance=1.0,
    )

    assert result["ready"] is False
    assert result["reason"] == "invalid_trade_amount"


def test_rejects_negative_profit():
    with pytest.raises(ValueError):
        TradePreparation.prepare(
            asset="BTC",
            buy_exchange="ExchangeA",
            sell_exchange="ExchangeB",
            trade_amount=1000.0,
            expected_profit=-5.0,
            estimated_fees=2.0,
            slippage_allowance=1.0,
        )


def test_rejects_missing_asset():
    with pytest.raises(ValueError):
        TradePreparation.prepare(
            asset="",
            buy_exchange="ExchangeA",
            sell_exchange="ExchangeB",
            trade_amount=1000.0,
            expected_profit=20.0,
            estimated_fees=2.0,
            slippage_allowance=1.0,
        )


def test_rejects_negative_fees():
    with pytest.raises(ValueError):
        TradePreparation.prepare(
            asset="BTC",
            buy_exchange="ExchangeA",
            sell_exchange="ExchangeB",
            trade_amount=1000.0,
            expected_profit=20.0,
            estimated_fees=-1.0,
            slippage_allowance=1.0,
        )


def test_trade_plan_contains_approval_summary():
    result = TradePreparation.prepare(
        asset="USDT",
        buy_exchange="ExchangeA",
        sell_exchange="ExchangeB",
        trade_amount=3000.0,
        expected_profit=100.0,
        estimated_fees=10.0,
        slippage_allowance=5.0,
    )

    assert "approval_summary" in result


@pytest.mark.parametrize(
    "trade_amount",
    [
        None,
        "not-a-number",
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_prepare_rejects_invalid_numeric_trade_amount(
    trade_amount,
):
    result = TradePreparation.prepare(
        asset="BTC",
        buy_exchange="ExchangeA",
        sell_exchange="ExchangeB",
        trade_amount=trade_amount,
        expected_profit=20.0,
        estimated_fees=2.0,
        slippage_allowance=1.0,
    )

    assert result == {
        "ready": False,
        "reason": "invalid_trade_amount",
    }


@pytest.mark.parametrize(
    "field,value",
    [
        ("expected_profit", None),
        ("expected_profit", "not-a-number"),
        ("expected_profit", float("nan")),
        ("expected_profit", float("inf")),
        ("expected_profit", float("-inf")),
        ("estimated_fees", None),
        ("estimated_fees", "not-a-number"),
        ("estimated_fees", float("nan")),
        ("estimated_fees", float("inf")),
        ("estimated_fees", float("-inf")),
        ("slippage_allowance", None),
        ("slippage_allowance", "not-a-number"),
        ("slippage_allowance", float("nan")),
        ("slippage_allowance", float("inf")),
        ("slippage_allowance", float("-inf")),
    ],
)
def test_prepare_rejects_invalid_numeric_economic_values(
    field,
    value,
):
    kwargs = {
        "asset": "BTC",
        "buy_exchange": "ExchangeA",
        "sell_exchange": "ExchangeB",
        "trade_amount": 1000.0,
        "expected_profit": 20.0,
        "estimated_fees": 2.0,
        "slippage_allowance": 1.0,
    }
    kwargs[field] = value

    with pytest.raises(ValueError):
        TradePreparation.prepare(**kwargs)


def test_prepare_rejects_boolean_trade_amount():
    result = TradePreparation.prepare(
        asset="BTC",
        buy_exchange="ExchangeA",
        sell_exchange="ExchangeB",
        trade_amount=True,
        expected_profit=20.0,
        estimated_fees=2.0,
        slippage_allowance=1.0,
    )

    assert result == {
        "ready": False,
        "reason": "invalid_trade_amount",
    }


@pytest.mark.parametrize(
    "field",
    [
        "expected_profit",
        "estimated_fees",
        "slippage_allowance",
    ],
)
def test_prepare_rejects_boolean_economic_values(field):
    kwargs = {
        "asset": "BTC",
        "buy_exchange": "ExchangeA",
        "sell_exchange": "ExchangeB",
        "trade_amount": 1000.0,
        "expected_profit": 20.0,
        "estimated_fees": 2.0,
        "slippage_allowance": 1.0,
    }
    kwargs[field] = True

    with pytest.raises(ValueError):
        TradePreparation.prepare(**kwargs)
