from core.ex368_multi_exchange_event_driven_benchmark import (
    EXCHANGE_IDS,
    build_asset_venues,
    build_exchange_symbols,
    build_route_pairs,
    select_shared_coins,
)


def test_ex368_has_nine_target_exchanges():
    assert EXCHANGE_IDS == [
        "kucoin",
        "bitget",
        "gate",
        "xt",
        "coinex",
        "poloniex",
        "okx",
        "bybit",
        "binance",
    ]


def test_asset_venue_map_preserves_partial_overlap():
    asset_sets = {
        "kucoin": {"BTC", "ETH", "AAA"},
        "bitget": {"BTC", "ETH", "BBB"},
        "gate": {"BTC", "AAA"},
    }

    result = build_asset_venues(
        asset_sets
    )

    assert result["BTC"] == {
        "kucoin",
        "bitget",
        "gate",
    }

    assert result["ETH"] == {
        "kucoin",
        "bitget",
    }

    assert result["AAA"] == {
        "kucoin",
        "gate",
    }

    assert result["BBB"] == {
        "bitget",
    }


def test_selection_requires_two_venues_not_all_venues():
    asset_venues = {
        "BTC": {"kucoin", "bitget"},
        "ETH": {"kucoin", "gate"},
        "AAA": {"gate", "xt"},
        "BBB": {"kucoin"},
    }

    selected = select_shared_coins(
        asset_venues,
        requested=100,
    )

    assert "BTC" in selected
    assert "ETH" in selected
    assert "AAA" in selected
    assert "BBB" not in selected


def test_exchange_symbols_are_venue_specific():
    selected = [
        "BTC",
        "ETH",
        "AAA",
    ]

    asset_sets = {
        "kucoin": {
            "BTC",
            "ETH",
        },
        "gate": {
            "BTC",
            "AAA",
        },
    }

    result = build_exchange_symbols(
        selected,
        asset_sets,
    )

    assert result == {
        "kucoin": [
            "BTC/USDT",
            "ETH/USDT",
        ],
        "gate": [
            "BTC/USDT",
            "AAA/USDT",
        ],
    }


def test_routes_exist_only_between_venues_listing_coin():
    selected = [
        "BTC",
        "AAA",
    ]

    asset_venues = {
        "BTC": {
            "kucoin",
            "bitget",
            "gate",
        },
        "AAA": {
            "gate",
            "xt",
        },
    }

    routes = set(
        build_route_pairs(
            selected,
            asset_venues,
        )
    )

    assert (
        "kucoin",
        "bitget",
        "BTC",
    ) in routes

    assert (
        "bitget",
        "kucoin",
        "BTC",
    ) in routes

    assert (
        "gate",
        "xt",
        "AAA",
    ) in routes

    assert (
        "xt",
        "gate",
        "AAA",
    ) in routes

    assert (
        "kucoin",
        "xt",
        "AAA",
    ) not in routes


def test_three_venue_coin_creates_six_directed_routes():
    routes = build_route_pairs(
        ["BTC"],
        {
            "BTC": {
                "kucoin",
                "bitget",
                "gate",
            }
        },
    )

    assert len(routes) == 6


def test_build_bounded_exchange_symbols_limits_each_venue():
    from core.ex368_multi_exchange_event_driven_benchmark import (
        build_bounded_exchange_symbols,
    )

    exchange_symbols = {
        "kucoin": [
            "BTC/USDT",
            "ETH/USDT",
            "SOL/USDT",
        ],
        "bitget": [
            "BTC/USDT",
            "XRP/USDT",
        ],
    }

    result = build_bounded_exchange_symbols(
        exchange_symbols,
        per_exchange_limit=2,
    )

    assert result == {
        "kucoin": [
            "BTC/USDT",
            "ETH/USDT",
        ],
        "bitget": [
            "BTC/USDT",
            "XRP/USDT",
        ],
    }


def test_build_bounded_exchange_symbols_rejects_bad_limit():
    from core.ex368_multi_exchange_event_driven_benchmark import (
        build_bounded_exchange_symbols,
    )

    import pytest

    with pytest.raises(
        ValueError,
        match="per_exchange_limit must be positive",
    ):
        build_bounded_exchange_symbols(
            {
                "kucoin": [
                    "BTC/USDT",
                ],
            },
            per_exchange_limit=0,
        )


def test_build_bounded_route_pairs_uses_only_subscribed_markets():
    from core.ex368_multi_exchange_event_driven_benchmark import (
        build_bounded_route_pairs,
    )

    exchange_symbols = {
        "kucoin": [
            "BTC/USDT",
            "ETH/USDT",
        ],
        "bitget": [
            "BTC/USDT",
            "SOL/USDT",
        ],
        "gate": [
            "BTC/USDT",
            "ETH/USDT",
        ],
    }

    routes = build_bounded_route_pairs(
        exchange_symbols
    )

    assert (
        "kucoin",
        "bitget",
        "BTC",
    ) in routes

    assert (
        "bitget",
        "kucoin",
        "BTC",
    ) in routes

    assert (
        "kucoin",
        "gate",
        "ETH",
    ) in routes

    assert (
        "gate",
        "kucoin",
        "ETH",
    ) in routes

    assert (
        "kucoin",
        "bitget",
        "ETH",
    ) not in routes

    # BTC exists on 3 venues:
    # 3 * 2 = 6 directed routes.
    #
    # ETH exists on 2 venues:
    # 2 directed routes.
    #
    # SOL exists on only one venue:
    # 0 routes.
    assert len(routes) == 8


def test_build_bounded_route_pairs_ignores_single_venue_coin():
    from core.ex368_multi_exchange_event_driven_benchmark import (
        build_bounded_route_pairs,
    )

    routes = build_bounded_route_pairs(
        {
            "kucoin": [
                "BTC/USDT",
            ],
            "bitget": [
                "ETH/USDT",
            ],
        }
    )

    assert routes == []
