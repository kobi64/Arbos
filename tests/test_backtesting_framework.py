from exchanges.backtesting_framework import BacktestingFramework


def test_create_backtester():
    backtester = BacktestingFramework()

    assert backtester is not None


def test_add_trade_result():
    backtester = BacktestingFramework()

    backtester.add_trade(
        profit=25,
        success=True,
    )

    summary = backtester.get_summary()

    assert summary["total_trades"] == 1


def test_multiple_trade_results():
    backtester = BacktestingFramework()

    backtester.add_trade(
        profit=10,
        success=True,
    )

    backtester.add_trade(
        profit=-5,
        success=False,
    )

    summary = backtester.get_summary()

    assert summary["total_trades"] == 2


def test_total_profit_calculation():
    backtester = BacktestingFramework()

    backtester.add_trade(
        profit=20,
        success=True,
    )

    backtester.add_trade(
        profit=30,
        success=True,
    )

    summary = backtester.get_summary()

    assert summary["total_profit"] == 50


def test_success_count():
    backtester = BacktestingFramework()

    backtester.add_trade(
        profit=10,
        success=True,
    )

    backtester.add_trade(
        profit=-2,
        success=False,
    )

    summary = backtester.get_summary()

    assert summary["successful_trades"] == 1


def test_failed_count():
    backtester = BacktestingFramework()

    backtester.add_trade(
        profit=-10,
        success=False,
    )

    summary = backtester.get_summary()

    assert summary["failed_trades"] == 1


def test_empty_backtest():
    backtester = BacktestingFramework()

    summary = backtester.get_summary()

    assert summary["total_trades"] == 0


def test_trade_history_available():
    backtester = BacktestingFramework()

    backtester.add_trade(
        profit=5,
        success=True,
    )

    history = backtester.get_history()

    assert len(history) == 1
