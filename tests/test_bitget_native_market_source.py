from exchanges.bitget_native_market_source import (
    BitgetNativeMarketSource,
)


class FakeExchange:
    def publicSpotGetV2SpotPublicSymbols(self):
        return {
            "code": "00000",
            "msg": "success",
            "data": [
                {
                    "symbol": "GOATUSDT",
                    "baseCoin": "GOAT",
                    "quoteCoin": "USDT",
                    "status": "online",
                    "minTradeAmount": "0",
                    "minTradeUSDT": "1",
                    "pricePrecision": "5",
                    "quantityPrecision": "2",
                },
                {
                    "symbol": "GHOUSDT",
                    "baseCoin": "GHO",
                    "quoteCoin": "USDT",
                    "status": "halt",
                    "minTradeAmount": "0",
                    "minTradeUSDT": "1",
                    "pricePrecision": "4",
                    "quantityPrecision": "2",
                },
            ],
        }


class FailedExchange:
    def publicSpotGetV2SpotPublicSymbols(self):
        raise RuntimeError(
            "native catalogue unavailable"
        )


def test_fetches_bitget_native_catalogue():
    result = BitgetNativeMarketSource(
        FakeExchange()
    ).fetch()

    assert result["fetch_complete"] is True
    assert result["exchange_id"] == "bitget"

    assert result["symbols"] == [
        "GOAT/USDT",
        "GHO/USDT",
    ]


def test_normalizes_bitget_status():
    result = BitgetNativeMarketSource(
        FakeExchange()
    ).fetch()

    markets = result["markets"]

    assert markets[0]["status"] == "TRADING"
    assert markets[1]["status"] == "SUSPENDED"


def test_preserves_bitget_metadata():
    result = BitgetNativeMarketSource(
        FakeExchange()
    ).fetch()

    market = result["markets"][0]

    assert market["minimum_amount"] == "0"
    assert market["minimum_value"] == "1"
    assert market["price_precision"] == "5"
    assert market["amount_precision"] == "2"

    assert market["order_types"] == [
        "LIMIT",
        "MARKET",
    ]

    assert market["raw"]["symbol"] == (
        "GOATUSDT"
    )


def test_failed_native_fetch_is_fail_closed():
    result = BitgetNativeMarketSource(
        FailedExchange()
    ).fetch()

    assert result["fetch_complete"] is False
    assert result["symbols"] == []
    assert result["markets"] == []


def test_requires_exchange():
    try:
        BitgetNativeMarketSource(None)
        assert False
    except ValueError as exc:
        assert str(exc) == "exchange is required"
