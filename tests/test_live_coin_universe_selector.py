import pytest

from core.live_coin_universe_selector import (
    LiveCoinUniverseSelector,
)


def market(
    base,
    *,
    quote="USDT",
    spot=True,
    active=True,
    raw_base=None,
):
    return {
        "base": base,
        "quote": quote,
        "spot": spot,
        "active": active,
        "info": {
            "baseCoin": (
                raw_base
                if raw_base is not None
                else base
            ),
        },
    }


def test_ranks_active_usdt_spot_markets_by_quote_volume():
    selector = LiveCoinUniverseSelector()

    result = selector.select(
        exchange_id="kucoin",
        markets={
            "ETH/USDT": market("ETH"),
            "SOL/USDT": market("SOL"),
            "XRP/USDT": market("XRP"),
        },
        tickers={
            "ETH/USDT": {
                "quoteVolume": 500.0,
            },
            "SOL/USDT": {
                "quoteVolume": 900.0,
            },
            "XRP/USDT": {
                "quoteVolume": 700.0,
            },
        },
        limit=2,
    )

    assert result["coin_assets"] == [
        "SOL",
        "XRP",
    ]


def test_bulk_bid_ask_is_not_required_for_universe_selection():
    selector = LiveCoinUniverseSelector()

    result = selector.select(
        exchange_id="xt",
        markets={
            "BTC/USDT": market("BTC"),
            "ETH/USDT": market("ETH"),
            "SOL/USDT": market("SOL"),
        },
        tickers={
            "BTC/USDT": {
                "quoteVolume": 1000.0,
                "bid": None,
                "ask": None,
            },
            "ETH/USDT": {
                "quoteVolume": 800.0,
                "bid": None,
                "ask": None,
            },
            "SOL/USDT": {
                "quoteVolume": 600.0,
                "bid": None,
                "ask": None,
            },
        },
        limit=3,
    )

    assert result["coin_assets"] == [
        "BTC",
        "ETH",
        "SOL",
    ]

    assert result[
        "bulk_bid_ask_required"
    ] is False


def test_bitget_lowercase_r_prefixed_instruments_are_filtered():
    selector = LiveCoinUniverseSelector()

    result = selector.select(
        exchange_id="bitget",
        markets={
            "RNVDA/USDT": market(
                "RNVDA",
                raw_base="rNVDA",
            ),
            "RSPY/USDT": market(
                "RSPY",
                raw_base="rSPY",
            ),
            "BTC/USDT": market(
                "BTC",
                raw_base="BTC",
            ),
            "ETH/USDT": market(
                "ETH",
                raw_base="ETH",
            ),
        },
        tickers={
            "RNVDA/USDT": {
                "quoteVolume": 900000000.0,
            },
            "RSPY/USDT": {
                "quoteVolume": 800000000.0,
            },
            "BTC/USDT": {
                "quoteVolume": 1000000.0,
            },
            "ETH/USDT": {
                "quoteVolume": 900000.0,
            },
        },
        limit=20,
    )

    assert result["coin_assets"] == [
        "BTC",
        "ETH",
    ]

    assert result[
        "filtered_instrument_count"
    ] == 2


def test_normal_r_coin_is_not_filtered():
    selector = LiveCoinUniverseSelector()

    result = selector.select(
        exchange_id="bitget",
        markets={
            "RAY/USDT": market(
                "RAY",
                raw_base="RAY",
            ),
        },
        tickers={
            "RAY/USDT": {
                "quoteVolume": 1000.0,
            },
        },
        limit=20,
    )

    assert result["coin_assets"] == [
        "RAY",
    ]


def test_non_spot_inactive_and_non_usdt_markets_are_ignored():
    selector = LiveCoinUniverseSelector()

    result = selector.select(
        exchange_id="gate",
        markets={
            "ETH/USDT": market("ETH"),
            "SOL/USDT": market(
                "SOL",
                active=False,
            ),
            "XRP/USDC": market(
                "XRP",
                quote="USDC",
            ),
            "BTC/USDT:USDT": market(
                "BTC",
                spot=False,
            ),
        },
        tickers={
            "ETH/USDT": {
                "quoteVolume": 100.0,
            },
            "SOL/USDT": {
                "quoteVolume": 1000.0,
            },
        },
        limit=20,
    )

    assert result["coin_assets"] == [
        "ETH",
    ]


def test_excluded_assets_are_removed():
    selector = LiveCoinUniverseSelector(
        excluded_assets={
            "USDT",
            "USDC",
            "USD",
        }
    )

    result = selector.select(
        exchange_id="gate",
        markets={
            "USDC/USDT": market("USDC"),
            "ETH/USDT": market("ETH"),
        },
        tickers={
            "USDC/USDT": {
                "quoteVolume": 1000000.0,
            },
            "ETH/USDT": {
                "quoteVolume": 100.0,
            },
        },
        limit=20,
    )

    assert result["coin_assets"] == [
        "ETH",
    ]


def test_limit_must_be_positive():
    selector = LiveCoinUniverseSelector()

    with pytest.raises(
        ValueError,
        match="limit must be positive",
    ):
        selector.select(
            exchange_id="gate",
            markets={},
            tickers={},
            limit=0,
        )


@pytest.mark.parametrize(
    "base",
    [
        "BTC3L",
        "BTC3S",
        "BTC5L",
        "BTC5S",
        "ETH3L",
        "ETH3S",
        "ETH5L",
        "ETH5S",
        "SOL3L",
        "SOL3S",
        "SOL5L",
        "SOL5S",
        "AVAX3L",
        "AVAX3S",
        "AVAX5L",
        "AVAX5S",
        "SKHYNIX3L",
        "SNDK3S",
    ],
)
def test_leveraged_token_suffixes_are_filtered(
    base,
):
    selector = LiveCoinUniverseSelector()

    result = selector.select(
        exchange_id="gate",
        markets={
            f"{base}/USDT": market(base),
            "BTC/USDT": market("BTC"),
        },
        tickers={
            f"{base}/USDT": {
                "quoteVolume": 1000000.0,
            },
            "BTC/USDT": {
                "quoteVolume": 1000.0,
            },
        },
        limit=20,
    )

    assert result["coin_assets"] == [
        "BTC",
    ]

    assert result[
        "filtered_instrument_count"
    ] == 1


@pytest.mark.parametrize(
    "base",
    [
        "2U2",
        "USD1",
        "ETHFI",
        "RAY",
        "SIREN",
        "VANRY",
        "XLM",
        "ZEC",
    ],
)
def test_legitimate_assets_are_not_filtered_by_suffix_rule(
    base,
):
    selector = LiveCoinUniverseSelector()

    result = selector.select(
        exchange_id="gate",
        markets={
            f"{base}/USDT": market(base),
        },
        tickers={
            f"{base}/USDT": {
                "quoteVolume": 1000.0,
            },
        },
        limit=20,
    )

    assert result["coin_assets"] == [
        base,
    ]

    assert result[
        "filtered_instrument_count"
    ] == 0
