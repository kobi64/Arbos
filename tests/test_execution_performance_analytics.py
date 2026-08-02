import pytest

from exchanges.execution_performance_analytics import ExecutionPerformanceAnalytics


def test_create_performance_analytics():
    analytics = ExecutionPerformanceAnalytics(
        execution_id="ARB-001"
    )

    assert analytics is not None


def test_record_successful_execution():
    analytics = ExecutionPerformanceAnalytics(
        execution_id="ARB-002"
    )

    result = analytics.record_execution(
        status="success",
        profit=24.72,
        duration=42,
    )

    assert result["status"] == "success"


def test_record_failed_execution():
    analytics = ExecutionPerformanceAnalytics(
        execution_id="ARB-003"
    )

    result = analytics.record_execution(
        status="failed",
        profit=0,
        duration=30,
    )

    assert result["status"] == "failed"


def test_calculate_average_profit():
    analytics = ExecutionPerformanceAnalytics(
        execution_id="ARB-004"
    )

    analytics.record_execution(
        status="success",
        profit=20,
        duration=30,
    )

    analytics.record_execution(
        status="success",
        profit=30,
        duration=40,
    )

    result = analytics.average_profit()

    assert result == 25


def test_calculate_success_rate():
    analytics = ExecutionPerformanceAnalytics(
        execution_id="ARB-005"
    )

    analytics.record_execution(
        status="success",
        profit=10,
        duration=20,
    )

    analytics.record_execution(
        status="failed",
        profit=0,
        duration=25,
    )

    result = analytics.success_rate()

    assert result == 50


def test_record_slippage():
    analytics = ExecutionPerformanceAnalytics(
        execution_id="ARB-006"
    )

    result = analytics.record_slippage(
        expected_profit=25,
        actual_profit=24.5,
    )

    assert result["slippage"] == 0.5


def test_route_score():
    analytics = ExecutionPerformanceAnalytics(
        execution_id="ARB-007"
    )

    analytics.record_execution(
        status="success",
        profit=25,
        duration=40,
    )

    result = analytics.route_score()

    assert result > 0


def test_execution_history_recorded():
    analytics = ExecutionPerformanceAnalytics(
        execution_id="ARB-008"
    )

    analytics.record_execution(
        status="success",
        profit=15,
        duration=20,
    )

    history = analytics.get_history()

    assert len(history) == 2
