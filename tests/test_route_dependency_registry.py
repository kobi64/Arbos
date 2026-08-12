import pytest

from core.route_dependency_registry import (
    RouteDependencyRegistry,
)


def sample_route():
    return {
        "route_id": "R-ETH-BTC",
        "exchange_id": "kucoin",
        "starting_value": 100.0,
        "fee_rate": 0.001,
        "max_slippage_percent": 0.5,
        "legs": [
            {
                "symbol": "ETH/USDT",
                "side": "buy",
            },
            {
                "symbol": "ETH/BTC",
                "side": "sell",
            },
            {
                "symbol": "BTC/USDT",
                "side": "sell",
            },
        ],
    }


def test_registers_and_returns_route():
    registry = RouteDependencyRegistry()

    result = registry.register(
        sample_route()
    )

    assert result["registered"] is True
    assert result["route_id"] == "R-ETH-BTC"

    route = registry.get(
        "R-ETH-BTC"
    )

    assert route["exchange_id"] == "kucoin"
    assert len(route["legs"]) == 3


def test_derives_market_dependencies_from_route_legs():
    registry = RouteDependencyRegistry()

    registry.register(
        sample_route()
    )

    markets = registry.markets_for_route(
        "R-ETH-BTC"
    )

    assert markets == [
        ("kucoin", "BTC/USDT"),
        ("kucoin", "ETH/BTC"),
        ("kucoin", "ETH/USDT"),
    ]


def test_routes_for_market_returns_all_dependents():
    registry = RouteDependencyRegistry()

    registry.register(
        sample_route()
    )

    second = sample_route()
    second["route_id"] = "R-SOL-BTC"
    second["legs"] = [
        {
            "symbol": "SOL/USDT",
            "side": "buy",
        },
        {
            "symbol": "SOL/BTC",
            "side": "sell",
        },
        {
            "symbol": "BTC/USDT",
            "side": "sell",
        },
    ]

    registry.register(
        second
    )

    assert registry.routes_for_market(
        exchange_id="kucoin",
        symbol="BTC/USDT",
    ) == [
        "R-ETH-BTC",
        "R-SOL-BTC",
    ]


def test_route_reads_are_copy_safe():
    registry = RouteDependencyRegistry()

    registry.register(
        sample_route()
    )

    first = registry.get(
        "R-ETH-BTC"
    )

    first["legs"][0][
        "symbol"
    ] = "BROKEN"

    second = registry.get(
        "R-ETH-BTC"
    )

    assert second["legs"][0][
        "symbol"
    ] == "ETH/USDT"


def test_duplicate_route_id_is_rejected():
    registry = RouteDependencyRegistry()

    registry.register(
        sample_route()
    )

    with pytest.raises(
        ValueError,
        match="route_id already registered",
    ):
        registry.register(
            sample_route()
        )


def test_route_id_is_required():
    registry = RouteDependencyRegistry()

    route = sample_route()
    route.pop("route_id")

    with pytest.raises(
        ValueError,
        match="route_id is required",
    ):
        registry.register(route)


def test_exchange_id_is_required():
    registry = RouteDependencyRegistry()

    route = sample_route()
    route.pop("exchange_id")

    with pytest.raises(
        ValueError,
        match="exchange_id is required",
    ):
        registry.register(route)


def test_route_legs_are_required():
    registry = RouteDependencyRegistry()

    route = sample_route()
    route["legs"] = []

    with pytest.raises(
        ValueError,
        match="route legs are required",
    ):
        registry.register(route)


def test_unknown_route_returns_none():
    registry = RouteDependencyRegistry()

    assert registry.get(
        "UNKNOWN"
    ) is None


def test_route_count_tracks_registered_routes():
    registry = RouteDependencyRegistry()

    registry.register(
        sample_route()
    )

    assert registry.route_count() == 1
