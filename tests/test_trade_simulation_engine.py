from exchanges.trade_simulation_engine import TradeSimulationEngine


def test_create_simulator():
    simulator = TradeSimulationEngine()

    assert simulator is not None


def test_create_virtual_balance():
    simulator = TradeSimulationEngine()

    balance = simulator.create_balance(
        asset="USDT",
        amount=10000,
    )

    assert balance["amount"] == 10000


def test_simulate_profitable_trade():
    simulator = TradeSimulationEngine()

    result = simulator.simulate_trade(
        input_asset="USDT",
        output_asset="BTC",
        amount=1000,
        expected_return=1020,
        fees=2,
        slippage=1,
    )

    assert result["profit"] == 17


def test_simulate_failed_trade():
    simulator = TradeSimulationEngine()

    result = simulator.simulate_trade(
        input_asset="USDT",
        output_asset="TOKEN",
        amount=1000,
        expected_return=990,
        fees=2,
        slippage=1,
    )

    assert result["success"] is False


def test_simulation_history():
    simulator = TradeSimulationEngine()

    simulator.simulate_trade(
        input_asset="USDT",
        output_asset="BTC",
        amount=500,
        expected_return=510,
        fees=1,
        slippage=1,
    )

    history = simulator.get_history()

    assert len(history) == 2


def test_slippage_reduces_return():
    simulator = TradeSimulationEngine()

    result = simulator.simulate_trade(
        input_asset="USDT",
        output_asset="BTC",
        amount=1000,
        expected_return=1100,
        fees=0,
        slippage=5,
    )

    assert result["final_return"] == 1095


def test_fee_deduction():
    simulator = TradeSimulationEngine()

    result = simulator.simulate_trade(
        input_asset="USDT",
        output_asset="BTC",
        amount=1000,
        expected_return=1100,
        fees=10,
        slippage=0,
    )

    assert result["final_return"] == 1090


def test_trade_contains_route_details():
    simulator = TradeSimulationEngine()

    result = simulator.simulate_trade(
        input_asset="USDT",
        output_asset="BTC",
        amount=1000,
        expected_return=1050,
        fees=1,
        slippage=1,
    )

    assert result["input_asset"] == "USDT"
