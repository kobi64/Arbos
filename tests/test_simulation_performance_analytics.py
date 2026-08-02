from exchanges.simulation_performance_analytics import SimulationPerformanceAnalytics


def test_create_analytics():
    analytics = SimulationPerformanceAnalytics()

    assert analytics is not None


def test_record_successful_trade():
    analytics = SimulationPerformanceAnalytics()

    analytics.record_result(
        profit=25,
        success=True,
    )

    summary = analytics.get_summary()

    assert summary["successful_trades"] == 1


def test_record_failed_trade():
    analytics = SimulationPerformanceAnalytics()

    analytics.record_result(
        profit=-5,
        success=False,
    )

    summary = analytics.get_summary()

    assert summary["failed_trades"] == 1


def test_total_trades_count():
    analytics = SimulationPerformanceAnalytics()

    analytics.record_result(
        profit=10,
        success=True,
    )

    analytics.record_result(
        profit=-2,
        success=False,
    )

    summary = analytics.get_summary()

    assert summary["total_trades"] == 2


def test_win_rate_calculation():
    analytics = SimulationPerformanceAnalytics()

    analytics.record_result(
        profit=10,
        success=True,
    )

    analytics.record_result(
        profit=5,
        success=True,
    )

    analytics.record_result(
        profit=-1,
        success=False,
    )

    summary = analytics.get_summary()

    assert summary["win_rate"] == 66.67


def test_average_profit():
    analytics = SimulationPerformanceAnalytics()

    analytics.record_result(
        profit=10,
        success=True,
    )

    analytics.record_result(
        profit=20,
        success=True,
    )

    summary = analytics.get_summary()

    assert summary["average_profit"] == 15


def test_empty_summary():
    analytics = SimulationPerformanceAnalytics()

    summary = analytics.get_summary()

    assert summary["total_trades"] == 0


def test_history_available():
    analytics = SimulationPerformanceAnalytics()

    analytics.record_result(
        profit=5,
        success=True,
    )

    history = analytics.get_history()

    assert len(history) == 1
