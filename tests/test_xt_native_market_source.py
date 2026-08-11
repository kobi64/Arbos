from exchanges.xt_native_market_source import (
    XTNativeMarketSource,
)


class FakeExchange:
    def publicSpotGetSymbol(self):
        return {
            "rc": 0,
            "result": {
                "time": 123,
                "version": "1",
                "symbols": [
                    {
                        "id": 640,
                        "symbol": "xt_usdt",
                        "displayName": "XT/USDT",
                        "state": "ONLINE",
                        "tradingEnabled": True,
                        "openapiEnabled": True,
                        "baseCurrency": "xt",
                        "quoteCurrency": "usdt",
                        "pricePrecision": 4,
                        "quantityPrecision": 2,
                        "orderTypes": [
                            "LIMIT",
                            "MARKET",
                        ],
                        "filters": [
                            {
                                "filter": "QUOTE_QTY",
                                "min": "1",
                            },
                        ],
                    },
                    {
                        "id": 999,
                        "symbol": "old_usdt",
                        "displayName": "OLD/USDT",
                        "state": "OFFLINE",
                        "tradingEnabled": False,
                        "openapiEnabled": False,
                        "baseCurrency": "old",
                        "quoteCurrency": "usdt",
                        "pricePrecision": 5,
                        "quantityPrecision": 3,
                        "orderTypes": [
                            "LIMIT",
                        ],
                        "filters": [],
                    },
                ],
            },
        }


class FailedExchange:
    def publicSpotGetSymbol(self):
        raise RuntimeError(
            "native catalogue unavailable"
        )


def test_fetches_xt_native_catalogue():
    result = XTNativeMarketSource(
        FakeExchange()
    ).fetch()

    assert result["fetch_complete"] is True
    assert result["exchange_id"] == "xt"

    assert result["symbols"] == [
        "XT/USDT",
        "OLD/USDT",
    ]


def test_normalizes_xt_market_status():
    result = XTNativeMarketSource(
        FakeExchange()
    ).fetch()

    markets = result["markets"]

    assert markets[0]["status"] == "TRADING"
    assert markets[1]["status"] == "SUSPENDED"


def test_preserves_xt_market_metadata():
    result = XTNativeMarketSource(
        FakeExchange()
    ).fetch()

    market = result["markets"][0]

    assert market["price_precision"] == 4
    assert market["amount_precision"] == 2
    assert market["minimum_value"] == "1"

    assert market["order_types"] == [
        "LIMIT",
        "MARKET",
    ]

    assert market["native_market_id"] == 640
    assert market["raw"]["symbol"] == "xt_usdt"


def test_failed_native_fetch_is_fail_closed():
    result = XTNativeMarketSource(
        FailedExchange()
    ).fetch()

    assert result["fetch_complete"] is False
    assert result["symbols"] == []
    assert result["markets"] == []


def test_requires_exchange():
    try:
        XTNativeMarketSource(None)
        assert False
    except ValueError as exc:
        assert str(exc) == "exchange is required"
