from core.ex370_multi_exchange_25_coin_benchmark import (
    CYCLE_TIMEOUT_SECONDS,
    EXCHANGE_IDS,
    PER_EXCHANGE_LIMIT,
    REQUESTED_COINS,
    SUBSCRIPTION_START_STAGGER_SECONDS,
    build_bounded_exchange_symbols,
    build_bounded_route_pairs,
)


def test_ex370_scaling_contract():
    assert REQUESTED_COINS == 100
    assert PER_EXCHANGE_LIMIT == 25
    assert len(EXCHANGE_IDS) == 9


def test_ex370_binance_and_xt_startup_profiles():
    assert CYCLE_TIMEOUT_SECONDS == {
        "binance": 30.0,
        "xt": 30.0,
    }

    assert (
        SUBSCRIPTION_START_STAGGER_SECONDS
        == {
            "binance": 0.5,
            "xt": 0.75,
        }
    )


def test_ex370_bounded_symbols_limit_each_exchange():
    symbols = {
        "kucoin": [
            f"COIN{i}/USDT"
            for i in range(30)
        ],
        "binance": [
            f"COIN{i}/USDT"
            for i in range(30)
        ],
    }

    bounded = build_bounded_exchange_symbols(
        symbols,
        per_exchange_limit=(
            PER_EXCHANGE_LIMIT
        ),
    )

    assert len(bounded["kucoin"]) == 25
    assert len(bounded["binance"]) == 25


def test_ex370_route_builder_uses_shared_bounded_markets():
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
