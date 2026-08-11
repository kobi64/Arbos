from exchanges.htx_native_market_source import (
    HTXNativeMarketSource,
)


class FakeExchange:
    def publicGetCommonSymbols(self):
        return {
            "status": "ok",
            "data": [
                {
                    "symbol": "animeusdt",
                    "base-currency": "anime",
                    "quote-currency": "usdt",
                    "state": "online",
                    "api-trading": "enabled",
                    "min-order-amt": "1",
                    "min-order-value": "1",
                    "price-precision": 6,
                    "amount-precision": 4,
                },
                {
                    "symbol": "omgeth",
                    "base-currency": "omg",
                    "quote-currency": "eth",
                    "state": "offline",
                    "api-trading": "enabled",
                    "min-order-amt": "0.01",
                    "min-order-value": "0.001",
                    "price-precision": 6,
                    "amount-precision": 4,
                },
                {
                    "symbol": "haltusdt",
                    "base-currency": "halt",
                    "quote-currency": "usdt",
                    "state": "suspend",
                    "api-trading": "disabled",
                    "min-order-amt": "1",
                    "min-order-value": "1",
                    "price-precision": 4,
                    "amount-precision": 2,
                },
            ],
        }


class FailedExchange:
    def publicGetCommonSymbols(self):
        raise RuntimeError(
            "native catalogue unavailable"
        )


def test_fetches_htx_native_catalogue():
    result = HTXNativeMarketSource(
        FakeExchange()
    ).fetch()

    assert result["fetch_complete"] is True
    assert result["exchange_id"] == "htx"

    assert result["symbols"] == [
        "ANIME/USDT",
        "OMG/ETH",
        "HALT/USDT",
    ]


def test_normalizes_htx_market_status():
    result = HTXNativeMarketSource(
        FakeExchange()
    ).fetch()

    markets = result["markets"]

    assert markets[0]["status"] == "TRADING"
    assert markets[1]["status"] == "SUSPENDED"
    assert markets[2]["status"] == "SUSPENDED"


def test_preserves_htx_market_metadata():
    result = HTXNativeMarketSource(
        FakeExchange()
    ).fetch()

    market = result["markets"][0]

    assert market["minimum_amount"] == "1"
    assert market["minimum_value"] == "1"
    assert market["price_precision"] == 6
    assert market["amount_precision"] == 4
    assert market["api_trading"] == "enabled"

    assert market["order_types"] == [
        "LIMIT",
        "MARKET",
    ]

    assert market["raw"]["symbol"] == (
        "animeusdt"
    )


def test_failed_native_fetch_is_fail_closed():
    result = HTXNativeMarketSource(
        FailedExchange()
    ).fetch()

    assert result["fetch_complete"] is False
    assert result["symbols"] == []
    assert result["markets"] == []


def test_requires_exchange():
    try:
        HTXNativeMarketSource(None)
        assert False
    except ValueError as exc:
        assert str(exc) == "exchange is required"
