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
