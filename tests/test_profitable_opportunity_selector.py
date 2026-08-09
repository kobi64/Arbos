import pytest

from core.profitable_opportunity_selector import (
    ProfitableOpportunitySelector,
)


def test_selects_only_routes_above_minimum_profit():
    selector = ProfitableOpportunitySelector()

    routes = [
        {
            "route_id": "ROUTE-A",
            "route_type": "internal_triangle",
            "executable": True,
            "net_final_value": 101.2,
            "net_profit": 1.2,
            "net_profit_percent": 1.2,
        },
        {
            "route_id": "ROUTE-B",
            "route_type": "direct_cross_exchange",
            "executable": True,
            "net_final_value": 100.4,
            "net_profit": 0.4,
            "net_profit_percent": 0.4,
        },
        {
            "route_id": "ROUTE-C",
            "route_type": "bridge_cross_exchange",
            "executable": True,
            "net_final_value": 99.8,
            "net_profit": -0.2,
            "net_profit_percent": -0.2,
        },
    ]

    result = selector.select(
        routes=routes,
        starting_value=100.0,
        minimum_profit_percent=0.5,
    )

    assert result["profitable_route_count"] == 1
    assert result["best_profitable_route"]["route_id"] == "ROUTE-A"

    assert (
        result["best_profitable_internal"]["route_id"]
        == "ROUTE-A"
    )

    assert result["best_profitable_cross_exchange"] is None

    assert [
        route["route_id"]
        for route in result["profitable_routes"]
    ] == ["ROUTE-A"]


def test_selects_best_profitable_cross_exchange_separately():
    selector = ProfitableOpportunitySelector()

    routes = [
        {
            "route_id": "INTERNAL",
            "route_type": "internal_triangle",
            "executable": True,
            "net_final_value": 101.0,
            "net_profit": 1.0,
            "net_profit_percent": 1.0,
        },
        {
            "route_id": "DIRECT",
            "route_type": "direct_cross_exchange",
            "executable": True,
            "net_final_value": 100.8,
            "net_profit": 0.8,
            "net_profit_percent": 0.8,
        },
        {
            "route_id": "BRIDGE",
            "route_type": "bridge_cross_exchange",
            "executable": True,
            "net_final_value": 100.6,
            "net_profit": 0.6,
            "net_profit_percent": 0.6,
        },
    ]

    result = selector.select(
        routes=routes,
        starting_value=100.0,
        minimum_profit_percent=0.5,
    )

    assert result["profitable_route_count"] == 3
    assert (
        result["best_profitable_cross_exchange"]["route_id"]
        == "DIRECT"
    )


def test_returns_no_profitable_route_when_threshold_not_met():
    selector = ProfitableOpportunitySelector()

    result = selector.select(
        routes=[
            {
                "route_id": "LOSS",
                "route_type": "internal_triangle",
                "executable": True,
                "net_final_value": 99.5,
                "net_profit": -0.5,
                "net_profit_percent": -0.5,
            },
        ],
        starting_value=100.0,
        minimum_profit_percent=0.5,
    )

    assert result["profitable_route_count"] == 0
    assert result["best_profitable_route"] is None
    assert result["best_profitable_internal"] is None
    assert result["best_profitable_cross_exchange"] is None
    assert result["profitable_routes"] == []


def test_invalid_minimum_profit_is_rejected():
    selector = ProfitableOpportunitySelector()

    with pytest.raises(
        ValueError,
        match="minimum_profit_percent must be non-negative",
    ):
        selector.select(
            routes=[],
            starting_value=100.0,
            minimum_profit_percent=-0.1,
        )
