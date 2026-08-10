import pytest

from exchanges.verified_exchange_market_registry import (
    VerifiedExchangeMarketRegistry,
)


def registry():
    return VerifiedExchangeMarketRegistry()


def comparison():
    return {
        "markets": [
            {
                "symbol": "BTC/USDT",
                "status": "MATCHED",
            },
            {
                "symbol": "COTI/USDT",
                "status": "RAW_ONLY",
            },
            {
                "symbol": "OLD/USDT",
                "status": "CCXT_ONLY",
            },
        ]
    }


def native_markets():
    return [
        {
            "symbol": "COTI/USDT",
            "status": "TRADING",
            "order_types": [
                "LIMIT",
                "MARKET",
            ],
            "minimum_amount": 1,
            "minimum_value": 2,
            "price_precision": 6,
            "amount_precision": 2,
        }
    ]


def test_matched_market_is_verified():
    result = registry().build(
        exchange_id="digifinex",
        comparison_result=comparison(),
        native_markets=native_markets(),
    )

    symbols = {
        item["symbol"]
        for item in result[
            "verified_markets"
        ]
    }

    assert "BTC/USDT" in symbols


def test_trading_raw_only_market_is_verified():
    result = registry().build(
        exchange_id="digifinex",
        comparison_result=comparison(),
        native_markets=native_markets(),
    )

    verified = {
        item["symbol"]: item
        for item in result[
            "verified_markets"
        ]
    }

    coti = verified["COTI/USDT"]

    assert coti["verified"] is True
    assert coti["source"] == "RAW_ONLY"
    assert (
        coti["reason"]
        == "native_market_trading"
    )


def test_ccxt_only_market_requires_review():
    result = registry().build(
        exchange_id="digifinex",
        comparison_result=comparison(),
        native_markets=native_markets(),
    )

    rejected = {
        item["symbol"]: item
        for item in result[
            "rejected_markets"
        ]
    }

    assert (
        rejected["OLD/USDT"]["reason"]
        == "ccxt_only_requires_review"
    )


def test_non_trading_raw_market_is_rejected():
    markets = native_markets()
    markets[0]["status"] = "SUSPENDED"

    result = registry().build(
        exchange_id="digifinex",
        comparison_result=comparison(),
        native_markets=markets,
    )

    rejected = {
        item["symbol"]: item
        for item in result[
            "rejected_markets"
        ]
    }

    assert (
        rejected["COTI/USDT"]["reason"]
        == "native_market_not_tradable"
    )


def test_raw_market_without_order_types_is_rejected():
    markets = native_markets()
    markets[0]["order_types"] = []

    result = registry().build(
        exchange_id="digifinex",
        comparison_result=comparison(),
        native_markets=markets,
    )

    rejected = {
        item["symbol"]: item
        for item in result[
            "rejected_markets"
        ]
    }

    assert "COTI/USDT" in rejected


def test_missing_native_metadata_is_rejected():
    result = registry().build(
        exchange_id="digifinex",
        comparison_result=comparison(),
        native_markets=[],
    )

    rejected = {
        item["symbol"]: item
        for item in result[
            "rejected_markets"
        ]
    }

    assert (
        rejected["COTI/USDT"]["reason"]
        == "native_metadata_required"
    )


def test_registry_never_submits_live_order():
    result = registry().build(
        exchange_id="digifinex",
        comparison_result=comparison(),
        native_markets=native_markets(),
    )

    assert result[
        "live_order_submitted"
    ] is False


def test_missing_exchange_id_is_rejected():
    with pytest.raises(
        ValueError,
        match="exchange_id is required",
    ):
        registry().build(
            exchange_id="",
            comparison_result={},
            native_markets=[],
        )


def test_missing_comparison_is_rejected():
    with pytest.raises(
        ValueError,
        match="comparison_result is required",
    ):
        registry().build(
            exchange_id="digifinex",
            comparison_result=None,
            native_markets=[],
        )


def test_missing_native_markets_is_rejected():
    with pytest.raises(
        ValueError,
        match="native_markets is required",
    ):
        registry().build(
            exchange_id="digifinex",
            comparison_result={},
            native_markets=None,
        )
