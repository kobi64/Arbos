from core.ex371_multi_exchange_50_coin_benchmark import (
    CYCLE_TIMEOUT_SECONDS,
    EXCHANGE_IDS,
    PER_EXCHANGE_LIMIT,
    REQUESTED_COINS,
    SUBSCRIPTION_START_STAGGER_SECONDS,
    build_bounded_exchange_symbols,
    build_bounded_route_pairs,
)


def test_ex371_scaling_contract():
    assert REQUESTED_COINS == 100
    assert PER_EXCHANGE_LIMIT == 50
    assert len(EXCHANGE_IDS) == 9


def test_ex371_exchange_startup_profiles():
    assert CYCLE_TIMEOUT_SECONDS == {
        "binance": 30.0,
        "kucoin": 20.0,
        "xt": 30.0,
    }

    assert (
        SUBSCRIPTION_START_STAGGER_SECONDS
        == {
            "binance": 0.5,
            "bitget": 0.10,
            "kucoin": 0.10,
            "xt": 0.75,
        }
    )


def test_ex371_bounded_symbols_limit_each_exchange():
    symbols = {
        "kucoin": [
            f"COIN{i}/USDT"
            for i in range(60)
        ],
        "binance": [
            f"COIN{i}/USDT"
            for i in range(60)
        ],
    }

    bounded = build_bounded_exchange_symbols(
        symbols,
        per_exchange_limit=(
            PER_EXCHANGE_LIMIT
        ),
    )

    assert len(bounded["kucoin"]) == 50
    assert len(bounded["binance"]) == 50


def test_ex371_route_builder_uses_shared_bounded_markets():
    bounded = {
        "kucoin": [
            "BTC/USDT",
            "ETH/USDT",
        ],
        "binance": [
            "BTC/USDT",
            "SOL/USDT",
        ],
        "okx": [
            "BTC/USDT",
        ],
    }

    routes = build_bounded_route_pairs(
        bounded
    )

    assert set(routes) == {
        ("kucoin", "binance", "BTC"),
        ("kucoin", "okx", "BTC"),
        ("binance", "kucoin", "BTC"),
        ("binance", "okx", "BTC"),
        ("okx", "kucoin", "BTC"),
        ("okx", "binance", "BTC"),
    }
