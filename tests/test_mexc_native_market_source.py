import pytest

from exchanges.mexc_native_market_source import (
    MexcNativeMarketSource,
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


def build_payload():
    return {
        "fetch_complete": True,
        "symbols": [
            {
                "symbol": "BTCUSDT",
                "status": "1",
                "baseAsset": "BTC",
                "quoteAsset": "USDT",
                "baseAssetPrecision": 8,
                "quoteAssetPrecision": 8,
                "baseSizePrecision": "0.000001",
                "quoteAmountPrecisionMarket": "0.000001",
                "maxQuoteAmount": "1000000",
                "isSpotTradingAllowed": True,
                "orderTypes": [
                    "LIMIT",
                    "MARKET",
                ],
            },
            {
                "symbol": "ETHUSDT",
                "status": "1",
                "baseAsset": "ETH",
                "quoteAsset": "USDT",
                "baseAssetPrecision": 8,
                "quoteAssetPrecision": 8,
                "baseSizePrecision": "0.0001",
                "quoteAmountPrecisionMarket": "0.0001",
                "maxQuoteAmount": "1000000",
                "isSpotTradingAllowed": True,
                "orderTypes": [
                    "LIMIT",
                    "MARKET",
                ],
            },
        ],
        "reason": None,
        "paper_only": True,
        "live_order_submitted": False,
    }


def test_lists_active_spot_markets():
    client = FakeClient(
        payload=build_payload(),
    )

    source = MexcNativeMarketSource(
        client=client,
    )

    markets = source.list_markets()

    assert len(markets) == 2

    assert markets[0] == {
        "symbol": "BTC/USDT",
        "native_symbol": "BTCUSDT",
        "base": "BTC",
        "quote": "USDT",
        "active": True,
        "amount_precision": 8,
        "price_precision": 8,
        "min_amount": 0.000001,
        "order_types": [
            "LIMIT",
            "MARKET",
        ],
    }

    assert markets[1][
        "symbol"
    ] == "ETH/USDT"

    assert client.calls == 1


def test_disabled_spot_market_is_filtered():
    payload = build_payload()

    payload["symbols"][0][
        "isSpotTradingAllowed"
    ] = False

    source = MexcNativeMarketSource(
        client=FakeClient(
            payload=payload,
        )
    )

    markets = source.list_markets()

    assert len(markets) == 1

    assert markets[0][
        "symbol"
    ] == "ETH/USDT"


def test_non_active_status_is_filtered():
    payload = build_payload()

    payload["symbols"][0][
        "status"
    ] = "0"

    source = MexcNativeMarketSource(
        client=FakeClient(
            payload=payload,
        )
    )

    markets = source.list_markets()

    assert len(markets) == 1

    assert markets[0][
        "symbol"
    ] == "ETH/USDT"


def test_invalid_market_entry_is_skipped():
    payload = build_payload()

    payload["symbols"].append({
        "symbol": "",
        "status": "1",
        "baseAsset": "",
        "quoteAsset": "",
        "isSpotTradingAllowed": True,
    })

    source = MexcNativeMarketSource(
        client=FakeClient(
            payload=payload,
        )
    )

    markets = source.list_markets()

    assert len(markets) == 2


def test_failed_fetch_fails_closed():
    source = MexcNativeMarketSource(
        client=FakeClient(
            payload={
                "fetch_complete": False,
                "symbols": [],
                "reason": "HTTP 500",
            }
        )
    )

    with pytest.raises(
        RuntimeError,
        match="MEXC exchange info unavailable",
    ):
        source.list_markets()


def test_invalid_payload_fails_closed():
    source = MexcNativeMarketSource(
        client=FakeClient(
            payload=None,
        )
    )

    with pytest.raises(
        RuntimeError,
        match="MEXC exchange info unavailable",
    ):
        source.list_markets()


def test_client_failure_is_wrapped():
    source = MexcNativeMarketSource(
        client=FakeClient(
            error=RuntimeError(
                "network down"
            )
        )
    )

    with pytest.raises(
        RuntimeError,
        match="MEXC exchange info unavailable",
    ):
        source.list_markets()


def test_requires_client():
    with pytest.raises(
        ValueError,
        match="client is required",
    ):
        MexcNativeMarketSource(
            client=None,
        )
