import pytest

from exchanges.coinbase_native_market_source import (
    CoinbaseNativeMarketSource,
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

    def fetch_products(self):
        self.calls += 1

        if self.error is not None:
            raise self.error

        return self.payload


def test_lists_online_spot_markets():
    client = FakeClient([
        {
            "id": "BTC-USD",
            "base_currency": "BTC",
            "quote_currency": "USD",
            "quote_increment": "0.01",
            "base_increment": "0.00000001",
            "status": "online",
            "trading_disabled": False,
        },
        {
            "id": "ETH-USD",
            "base_currency": "ETH",
            "quote_currency": "USD",
            "quote_increment": "0.01",
            "base_increment": "0.00000001",
            "status": "online",
            "trading_disabled": False,
        },
    ])

    source = CoinbaseNativeMarketSource(
        client=client,
    )

    markets = source.list_markets()

    assert markets == [
        {
            "symbol": "BTC/USD",
            "native_symbol": "BTC-USD",
            "base": "BTC",
            "quote": "USD",
            "active": True,
            "tick_size": "0.01",
            "lot_size": "0.00000001",
            "min_amount": "0.00000001",
        },
        {
            "symbol": "ETH/USD",
            "native_symbol": "ETH-USD",
            "base": "ETH",
            "quote": "USD",
            "active": True,
            "tick_size": "0.01",
            "lot_size": "0.00000001",
            "min_amount": "0.00000001",
        },
    ]

    assert client.calls == 1


def test_filters_non_online_markets():
    source = CoinbaseNativeMarketSource(
        client=FakeClient([
            {
                "id": "ABC-USD",
                "base_currency": "ABC",
                "quote_currency": "USD",
                "quote_increment": "0.01",
                "base_increment": "1",
                "status": "offline",
                "trading_disabled": False,
            }
        ])
    )

    assert source.list_markets() == []


def test_filters_trading_disabled_markets():
    source = CoinbaseNativeMarketSource(
        client=FakeClient([
            {
                "id": "ABC-USD",
                "base_currency": "ABC",
                "quote_currency": "USD",
                "quote_increment": "0.01",
                "base_increment": "1",
                "status": "online",
                "trading_disabled": True,
            }
        ])
    )

    assert source.list_markets() == []


def test_missing_precision_fields_are_allowed():
    source = CoinbaseNativeMarketSource(
        client=FakeClient([
            {
                "id": "ABC-USD",
                "base_currency": "ABC",
                "quote_currency": "USD",
                "status": "online",
                "trading_disabled": False,
            }
        ])
    )

    result = source.list_markets()[0]

    assert result["tick_size"] is None
    assert result["lot_size"] is None
    assert result["min_amount"] is None


def test_invalid_payload_fails_closed():
    source = CoinbaseNativeMarketSource(
        client=FakeClient(
            payload=None,
        )
    )

    with pytest.raises(
        RuntimeError,
        match="Coinbase products unavailable",
    ):
        source.list_markets()


def test_client_failure_is_wrapped():
    source = CoinbaseNativeMarketSource(
        client=FakeClient(
            error=RuntimeError(
                "network down"
            )
        )
    )

    with pytest.raises(
        RuntimeError,
        match="Coinbase products unavailable",
    ):
        source.list_markets()


def test_requires_client():
    with pytest.raises(
        ValueError,
        match="client is required",
    ):
        CoinbaseNativeMarketSource(
            client=None,
        )
