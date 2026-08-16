import pytest

from exchanges.binance_native_market_source import (
    BinanceNativeMarketSource,
)


class FakeClient:
    def __init__(
        self,
        payload=None,
        error=None,
    ):
        self.payload = payload
        self.error = error
        self.calls = 0

    def fetch_exchange_info(self):
        self.calls += 1

        if self.error is not None:
            raise self.error

        return self.payload


def test_lists_active_spot_markets():
    client = FakeClient({
        "timezone": "UTC",
        "symbols": [
            {
                "symbol": "BTCUSDT",
                "status": "TRADING",
                "baseAsset": "BTC",
                "quoteAsset": "USDT",
                "isSpotTradingAllowed": True,
                "filters": [
                    {
                        "filterType": "PRICE_FILTER",
                        "tickSize": "0.01000000",
                    },
                    {
                        "filterType": "LOT_SIZE",
                        "minQty": "0.00001000",
                        "stepSize": "0.00001000",
                    },
                ],
            }
        ],
    })

    source = BinanceNativeMarketSource(
        client=client,
    )

    markets = source.list_markets()

    assert markets == [
        {
            "symbol": "BTC/USDT",
            "native_symbol": "BTCUSDT",
            "base": "BTC",
            "quote": "USDT",
            "active": True,
            "tick_size": "0.01000000",
            "lot_size": "0.00001000",
            "min_amount": "0.00001000",
        }
    ]

    assert client.calls == 1


def test_filters_non_trading_markets():
    source = BinanceNativeMarketSource(
        client=FakeClient({
            "symbols": [
                {
                    "symbol": "ABCUSDT",
                    "status": "BREAK",
                    "baseAsset": "ABC",
                    "quoteAsset": "USDT",
                    "isSpotTradingAllowed": True,
                    "filters": [],
                }
            ],
        })
    )

    assert source.list_markets() == []


def test_filters_non_spot_markets():
    source = BinanceNativeMarketSource(
        client=FakeClient({
            "symbols": [
                {
                    "symbol": "ABCUSDT",
                    "status": "TRADING",
                    "baseAsset": "ABC",
                    "quoteAsset": "USDT",
                    "isSpotTradingAllowed": False,
                    "filters": [],
                }
            ],
        })
    )

    assert source.list_markets() == []


def test_missing_filters_are_allowed():
    source = BinanceNativeMarketSource(
        client=FakeClient({
            "symbols": [
                {
                    "symbol": "ABCUSDT",
                    "status": "TRADING",
                    "baseAsset": "ABC",
                    "quoteAsset": "USDT",
                    "isSpotTradingAllowed": True,
                    "filters": [],
                }
            ],
        })
    )

    result = source.list_markets()[0]

    assert result["tick_size"] is None
    assert result["lot_size"] is None
    assert result["min_amount"] is None


def test_invalid_payload_fails_closed():
    source = BinanceNativeMarketSource(
        client=FakeClient({
            "symbols": None,
        })
    )

    with pytest.raises(
        RuntimeError,
        match="Binance exchange info unavailable",
    ):
        source.list_markets()


def test_client_failure_is_wrapped():
    source = BinanceNativeMarketSource(
        client=FakeClient(
            error=RuntimeError(
                "network down"
            )
        )
    )

    with pytest.raises(
        RuntimeError,
        match="Binance exchange info unavailable",
    ):
        source.list_markets()


def test_requires_client():
    with pytest.raises(
        ValueError,
        match="client is required",
    ):
        BinanceNativeMarketSource(
            client=None,
        )
