from core.route_dependency_registry import (
    RouteDependencyRegistry,
)


def cross_route():
    return {
        "route_id": "K-B-ADA",
        "route_type": "cross_exchange",
        "exchange_id": "kucoin",
        "source_exchange": "kucoin",
        "destination_exchange": "bitget",
        "symbol": "ADA/USDT",
        "starting_value": 100.0,
        "source_fee_rate": 0.001,
        "destination_fee_rate": 0.001,
        "legs": [
            {
                "exchange_id": "kucoin",
                "symbol": "ADA/USDT",
                "side": "buy",
            },
            {
                "exchange_id": "bitget",
                "symbol": "ADA/USDT",
                "side": "sell",
            },
        ],
    }


def test_registry_tracks_both_exchange_dependencies():
    registry = RouteDependencyRegistry()

    registry.register(
        cross_route()
    )

    assert registry.markets_for_route(
        "K-B-ADA"
    ) == [
        ("bitget", "ADA/USDT"),
        ("kucoin", "ADA/USDT"),
    ]


def test_source_market_update_affects_cross_route():
    registry = RouteDependencyRegistry()
    registry.register(cross_route())

    assert registry.routes_for_market(
        "kucoin",
        "ADA/USDT",
    ) == [
        "K-B-ADA"
    ]


def test_destination_market_update_affects_cross_route():
    registry = RouteDependencyRegistry()
    registry.register(cross_route())

    assert registry.routes_for_market(
        "bitget",
        "ADA/USDT",
    ) == [
        "K-B-ADA"
    ]


def test_old_single_exchange_route_remains_supported():
    registry = RouteDependencyRegistry()

    registry.register({
        "route_id": "OLD",
        "exchange_id": "kucoin",
        "legs": [
            {
                "symbol": "BTC/USDT",
                "side": "buy",
            },
        ],
    })

    assert registry.markets_for_route(
        "OLD"
    ) == [
        ("kucoin", "BTC/USDT")
    ]
