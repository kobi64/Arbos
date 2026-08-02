import pytest

from exchanges.exchange_simulation import ExchangeSimulation


def test_create_simulation():
    simulator = ExchangeSimulation(
        exchange_name="HTX"
    )

    assert simulator.exchange_name == "HTX"


def test_simulate_market_order():
    simulator = ExchangeSimulation(
        exchange_name="HTX"
    )

    result = simulator.simulate_order(
        symbol="BTC/USDT",
        side="BUY",
        amount=100,
    )

    assert result["status"] == "filled"
    assert result["symbol"] == "BTC/USDT"


def test_simulate_sell_order():
    simulator = ExchangeSimulation(
        exchange_name="GateIO"
    )

    result = simulator.simulate_order(
        symbol="ETH/USDT",
        side="SELL",
        amount=50,
    )

    assert result["side"] == "SELL"


def test_invalid_side_rejected():
    simulator = ExchangeSimulation(
        exchange_name="HTX"
    )

    with pytest.raises(ValueError):
        simulator.simulate_order(
            symbol="BTC/USDT",
            side="INVALID",
            amount=100,
        )


def test_partial_fill_simulation():
    simulator = ExchangeSimulation(
        exchange_name="HTX"
    )

    result = simulator.simulate_partial_fill(
        order_id="SIM-001",
        filled_amount=50,
        requested_amount=100,
    )

    assert result["status"] == "partial_fill"
    assert result["filled_amount"] == 50


def test_failed_order_simulation():
    simulator = ExchangeSimulation(
        exchange_name="HTX"
    )

    result = simulator.simulate_failure(
        order_id="SIM-002",
        reason="insufficient_liquidity",
    )

    assert result["status"] == "failed"
    assert result["reason"] == "insufficient_liquidity"


def test_get_simulation_history():
    simulator = ExchangeSimulation(
        exchange_name="Bitget"
    )

    simulator.simulate_order(
        symbol="SOL/USDT",
        side="BUY",
        amount=25,
    )

    result = simulator.get_history()

    assert isinstance(result, list)
    assert len(result) >= 1


def test_missing_exchange_rejected():
    with pytest.raises(ValueError):
        ExchangeSimulation(
            exchange_name=""
        )
