import pytest

from exchanges.route_reliability_scoring import RouteReliabilityScoring


def test_create_route_scoring():
    scorer = RouteReliabilityScoring(
        route_id="USDT-TOKEN-BTC"
    )

    assert scorer is not None


def test_record_successful_route_execution():
    scorer = RouteReliabilityScoring(
        route_id="ROUTE-001"
    )

    result = scorer.record_execution(
        success=True,
        profit=18.40,
        slippage=0.18,
        duration=31,
    )

    assert result["success"] is True


def test_record_failed_route_execution():
    scorer = RouteReliabilityScoring(
        route_id="ROUTE-002"
    )

    result = scorer.record_execution(
        success=False,
        profit=0,
        slippage=1.5,
        duration=60,
    )

    assert result["success"] is False


def test_calculate_success_rate():
    scorer = RouteReliabilityScoring(
        route_id="ROUTE-003"
    )

    scorer.record_execution(
        success=True,
        profit=20,
        slippage=0.2,
        duration=30,
    )

    scorer.record_execution(
        success=True,
        profit=15,
        slippage=0.1,
        duration=25,
    )

    scorer.record_execution(
        success=False,
        profit=0,
        slippage=1,
        duration=50,
    )

    result = scorer.success_rate()

    assert result == 66.67


def test_average_profit():
    scorer = RouteReliabilityScoring(
        route_id="ROUTE-004"
    )

    scorer.record_execution(
        success=True,
        profit=20,
        slippage=0.2,
        duration=30,
    )

    scorer.record_execution(
        success=True,
        profit=30,
        slippage=0.3,
        duration=40,
    )

    result = scorer.average_profit()

    assert result == 25


def test_average_slippage():
    scorer = RouteReliabilityScoring(
        route_id="ROUTE-005"
    )

    scorer.record_execution(
        success=True,
        profit=20,
        slippage=0.2,
        duration=30,
    )

    scorer.record_execution(
        success=True,
        profit=30,
        slippage=0.4,
        duration=40,
    )

    result = scorer.average_slippage()

    assert result == 0.3


def test_generate_reliability_score():
    scorer = RouteReliabilityScoring(
        route_id="ROUTE-006"
    )

    scorer.record_execution(
        success=True,
        profit=25,
        slippage=0.1,
        duration=30,
    )

    result = scorer.reliability_score()

    assert result > 0


def test_route_history_recorded():
    scorer = RouteReliabilityScoring(
        route_id="ROUTE-007"
    )

    scorer.record_execution(
        success=True,
        profit=15,
        slippage=0.2,
        duration=20,
    )

    history = scorer.get_history()

    assert len(history) == 2
