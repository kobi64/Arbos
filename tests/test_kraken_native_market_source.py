import pytest

from exchanges.kraken_native_market_source import (
    KrakenNativeMarketSource,
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

    def fetch_asset_pairs(self):
        self.calls += 1

        if self.error is not None:
            raise self.error

        return self.payload


def build_payload():
    return {
        "error": [],
        "result": {
            "XBTUSDT": {
                "altname": "XBTUSDT",
                "wsname": "XBT/USDT",
                "base": "XXBT",
                "quote": "USDT",
                "pair_decimals": 1,
                "lot_decimals": 8,
                "ordermin": "0.0001",
                "status": "online",
            },
            "ETHUSDT": {
                "altname": "ETHUSDT",
                "wsname": "ETH/USDT",
                "base": "XETH",
                "quote": "USDT",
                "pair_decimals": 2,
                "lot_decimals": 8,
                "ordermin": "0.001",
                "status": "online",
            },
        },
    }


def test_lists_active_spot_markets():
    client = FakeClient(
        payload=build_payload(),
    )

    source = KrakenNativeMarketSource(
        client=client,
    )

    markets = source.list_markets()

    assert len(markets) == 2

    assert markets[0] == {
        "symbol": "BTC/USDT",
        "native_symbol": "XBTUSDT",
        "base": "BTC",
        "quote": "USDT",
        "active": True,
        "price_precision": 1,
        "amount_precision": 8,
        "min_amount": 0.0001,
    }

    assert markets[1] == {
        "symbol": "ETH/USDT",
        "native_symbol": "ETHUSDT",
        "base": "ETH",
        "quote": "USDT",
        "active": True,
        "price_precision": 2,
        "amount_precision": 8,
        "min_amount": 0.001,
    }

    assert client.calls == 1


def test_xbt_is_normalized_to_btc():
    source = KrakenNativeMarketSource(
        client=FakeClient(
            payload=build_payload(),
        )
    )

    markets = source.list_markets()

    assert markets[0]["base"] == "BTC"
    assert markets[0]["symbol"] == "BTC/USDT"


def test_offline_market_is_filtered():
    payload = build_payload()

    payload["result"]["XBTUSDT"][
        "status"
    ] = "offline"

    source = KrakenNativeMarketSource(
        client=FakeClient(
            payload=payload,
        )
    )

    markets = source.list_markets()

    assert len(markets) == 1
    assert markets[0]["symbol"] == "ETH/USDT"


def test_wsname_is_used_for_canonical_pair():
    payload = {
        "error": [],
        "result": {
            "XXBTZUSD": {
                "altname": "XBTUSD",
                "wsname": "XBT/USD",
                "base": "XXBT",
                "quote": "ZUSD",
                "pair_decimals": 1,
                "lot_decimals": 8,
                "ordermin": "0.0001",
                "status": "online",
            }
        },
    }

    source = KrakenNativeMarketSource(
        client=FakeClient(
            payload=payload,
        )
    )

    market = source.list_markets()[0]

    assert market["symbol"] == "BTC/USD"
    assert market["native_symbol"] == "XBTUSD"
    assert market["base"] == "BTC"
    assert market["quote"] == "USD"


def test_api_error_fails_closed():
    source = KrakenNativeMarketSource(
        client=FakeClient(
            payload={
                "error": [
                    "EService:Unavailable"
                ],
                "result": {},
            }
        )
    )

    with pytest.raises(
        RuntimeError,
        match="Kraken asset pairs unavailable",
    ):
        source.list_markets()


def test_invalid_payload_fails_closed():
    source = KrakenNativeMarketSource(
        client=FakeClient(
            payload=None,
        )
    )

    with pytest.raises(
        RuntimeError,
        match="Kraken asset pairs unavailable",
    ):
        source.list_markets()


def test_client_failure_is_wrapped():
    source = KrakenNativeMarketSource(
        client=FakeClient(
            error=RuntimeError(
                "network down"
            )
        )
    )

    with pytest.raises(
        RuntimeError,
        match="Kraken asset pairs unavailable",
    ):
        source.list_markets()


def test_client_is_required():
    with pytest.raises(
        ValueError,
        match="client is required",
    ):
        KrakenNativeMarketSource(
            client=None,
        )
