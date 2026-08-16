import pytest

from exchanges.bingx_native_market_source import (
    BingXNativeMarketSource,
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

    def fetch_symbols(self):
        self.calls += 1

        if self.error is not None:
            raise self.error

        return self.payload


def build_payload():
    return {
        "fetch_complete": True,
        "symbols": [
            {
                "symbol": "BTC-USDT",
                "minQty": 0.00001,
                "maxQty": 1000,
                "minNotional": 1,
                "maxNotional": 1000000,
                "status": 1,
                "tickSize": 0.01,
                "stepSize": 0.00001,
            },
            {
                "symbol": "ETH-USDT",
                "minQty": 0.0001,
                "maxQty": 10000,
                "minNotional": 1,
                "maxNotional": 1000000,
                "status": 1,
                "tickSize": 0.01,
                "stepSize": 0.0001,
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

    source = BingXNativeMarketSource(
        client=client,
    )

    markets = source.list_markets()

    assert len(markets) == 2

    assert markets[0] == {
        "symbol": "BTC/USDT",
        "native_symbol": "BTC-USDT",
        "base": "BTC",
        "quote": "USDT",
        "active": True,
        "min_amount": 0.00001,
        "min_notional": 1.0,
        "tick_size": 0.01,
        "step_size": 0.00001,
    }

    assert markets[1][
        "symbol"
    ] == "ETH/USDT"

    assert client.calls == 1


def test_inactive_market_is_filtered():
    payload = build_payload()

    payload["symbols"][0][
        "status"
    ] = 0

    source = BingXNativeMarketSource(
        client=FakeClient(
            payload=payload,
        )
    )

    markets = source.list_markets()

    assert len(markets) == 1

    assert markets[0][
        "symbol"
    ] == "ETH/USDT"


def test_invalid_symbol_is_skipped():
    payload = build_payload()

    payload["symbols"].append({
        "symbol": "INVALID",
        "status": 1,
    })

    source = BingXNativeMarketSource(
        client=FakeClient(
            payload=payload,
        )
    )

    markets = source.list_markets()

    assert len(markets) == 2


def test_numeric_metadata_is_normalized():
    payload = build_payload()

    payload["symbols"][0][
        "minQty"
    ] = "0.00001"

    payload["symbols"][0][
        "minNotional"
    ] = "1"

    source = BingXNativeMarketSource(
        client=FakeClient(
            payload=payload,
        )
    )

    market = source.list_markets()[0]

    assert market["min_amount"] == 0.00001
    assert market["min_notional"] == 1.0


def test_failed_fetch_fails_closed():
    source = BingXNativeMarketSource(
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
        match="BingX symbols unavailable",
    ):
        source.list_markets()


def test_invalid_payload_fails_closed():
    source = BingXNativeMarketSource(
        client=FakeClient(
            payload=None,
        )
    )

    with pytest.raises(
        RuntimeError,
        match="BingX symbols unavailable",
    ):
        source.list_markets()


def test_client_failure_is_wrapped():
    source = BingXNativeMarketSource(
        client=FakeClient(
            error=RuntimeError(
                "network down"
            )
        )
    )

    with pytest.raises(
        RuntimeError,
        match="BingX symbols unavailable",
    ):
        source.list_markets()


def test_requires_client():
    with pytest.raises(
        ValueError,
        match="client is required",
    ):
        BingXNativeMarketSource(
            client=None,
        )
