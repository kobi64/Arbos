import pytest

from exchanges.okx_native_market_source import (
    OKXNativeMarketSource,
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

    def fetch_instruments(self):
        self.calls += 1

        if self.error is not None:
            raise self.error

        return self.payload


def test_lists_live_spot_markets():
    client = FakeClient(
        {
            "code": "0",
            "msg": "",
            "data": [
                {
                    "instType": "SPOT",
                    "instId": "BTC-USDT",
                    "baseCcy": "BTC",
                    "quoteCcy": "USDT",
                    "state": "live",
                    "tickSz": "0.1",
                    "lotSz": "0.00000001",
                    "minSz": "0.00001",
                },
                {
                    "instType": "SPOT",
                    "instId": "ETH-USDT",
                    "baseCcy": "ETH",
                    "quoteCcy": "USDT",
                    "state": "live",
                    "tickSz": "0.01",
                    "lotSz": "0.000001",
                    "minSz": "0.0001",
                },
            ],
        }
    )

    source = OKXNativeMarketSource(
        client=client,
    )

    markets = source.list_markets()

    assert markets == [
        {
            "symbol": "BTC/USDT",
            "native_symbol": "BTC-USDT",
            "base": "BTC",
            "quote": "USDT",
            "active": True,
            "tick_size": "0.1",
            "lot_size": "0.00000001",
            "min_amount": "0.00001",
        },
        {
            "symbol": "ETH/USDT",
            "native_symbol": "ETH-USDT",
            "base": "ETH",
            "quote": "USDT",
            "active": True,
            "tick_size": "0.01",
            "lot_size": "0.000001",
            "min_amount": "0.0001",
        },
    ]

    assert client.calls == 1


def test_filters_non_live_markets():
    client = FakeClient(
        {
            "code": "0",
            "data": [
                {
                    "instType": "SPOT",
                    "instId": "ABC-USDT",
                    "baseCcy": "ABC",
                    "quoteCcy": "USDT",
                    "state": "suspend",
                    "tickSz": "0.01",
                    "lotSz": "1",
                    "minSz": "1",
                },
            ],
        }
    )

    source = OKXNativeMarketSource(
        client=client,
    )

    assert source.list_markets() == []


def test_rejects_exchange_error_code():
    source = OKXNativeMarketSource(
        client=FakeClient(
            {
                "code": "50000",
                "msg": "error",
                "data": [],
            }
        )
    )

    with pytest.raises(
        RuntimeError,
        match="OKX instruments unavailable",
    ):
        source.list_markets()


def test_rejects_invalid_payload():
    source = OKXNativeMarketSource(
        client=FakeClient(
            {
                "code": "0",
                "data": None,
            }
        )
    )

    with pytest.raises(
        RuntimeError,
        match="OKX instruments unavailable",
    ):
        source.list_markets()


def test_client_failure_is_wrapped():
    source = OKXNativeMarketSource(
        client=FakeClient(
            error=RuntimeError(
                "network down"
            )
        )
    )

    with pytest.raises(
        RuntimeError,
        match="OKX instruments unavailable",
    ):
        source.list_markets()


def test_requires_client():
    with pytest.raises(
        ValueError,
        match="client is required",
    ):
        OKXNativeMarketSource(
            client=None,
        )
