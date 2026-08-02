import pytest

from exchanges.smart_route_selection import SmartRouteSelection


def test_create_route_selector():
    selector = SmartRouteSelection()

    assert selector is not None


def test_add_route_candidate():
    selector = SmartRouteSelection()

    result = selector.add_route(
        route_id="ROUTE-001",
        profit=30,
        reliability=94,
        duration=35,
    )

    assert result["route_id"] == "ROUTE-001"


def test_add_multiple_routes():
    selector = SmartRouteSelection()

    selector.add_route(
        route_id="ROUTE-A",
        profit=30,
        reliability=94,
        duration=35,
    )

    selector.add_route(
        route_id="ROUTE-B",
        profit=45,
        reliability=60,
        duration=90,
    )

    assert len(selector.get_routes()) == 2


def test_select_best_route():
    selector = SmartRouteSelection()

    selector.add_route(
        route_id="ROUTE-A",
        profit=30,
        reliability=94,
        duration=35,
    )

    selector.add_route(
        route_id="ROUTE-B",
        profit=45,
        reliability=60,
        duration=90,
    )

    result = selector.select_best_route()

    assert result["route_id"] == "ROUTE-A"


def test_route_selection_balances_profit_and_reliability():
    selector = SmartRouteSelection()

    selector.add_route(
        route_id="HIGH-PROFIT",
        profit=100,
        reliability=40,
        duration=120,
    )

    selector.add_route(
        route_id="BALANCED",
        profit=50,
        reliability=90,
        duration=30,
    )

    result = selector.select_best_route()

    assert result["route_id"] == "BALANCED"


def test_selection_reason_generated():
    selector = SmartRouteSelection()

    selector.add_route(
        route_id="ROUTE-001",
        profit=25,
        reliability=95,
        duration=25,
    )

    result = selector.select_best_route()

    assert "reason" in result


def test_selection_score_generated():
    selector = SmartRouteSelection()

    selector.add_route(
        route_id="ROUTE-001",
        profit=25,
        reliability=95,
        duration=25,
    )

    result = selector.select_best_route()

    assert result["score"] > 0


def test_selection_history_recorded():
    selector = SmartRouteSelection()

    selector.add_route(
        route_id="ROUTE-001",
        profit=25,
        reliability=95,
        duration=25,
    )

    selector.select_best_route()

    history = selector.get_history()

    assert len(history) == 2
