import pytest

from exchanges.weex_native_market_source import (
    WeexNativeMarketSource,
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
            "BTCUSDT",
            "ETHUSDT",
            "SOLUSDC",
            "ETHBTC",
        ],
        "symbol_count": 4,
        "paper_only": True,
        "live_order_submitted": False,
    }


def test_lists_native_spot_markets():
    client = FakeClient(
        payload=build_payload(),
    )

    source = WeexNativeMarketSource(
        client=client,
    )

    markets = source.list_markets()

    assert len(markets) == 4

    assert markets[0] == {
        "symbol": "BTC/USDT",
        "native_symbol": "BTCUSDT",
        "base": "BTC",
        "quote": "USDT",
        "active": True,
    }

    assert markets[1][
        "symbol"
    ] == "ETH/USDT"

    assert markets[2][
        "symbol"
    ] == "SOL/USDC"

    assert markets[3][
        "symbol"
    ] == "ETH/BTC"

    assert client.calls == 1


def test_symbols_are_normalized_to_uppercase():
    payload = build_payload()

    payload["symbols"] = [
        "btcusdt",
    ]

    source = WeexNativeMarketSource(
        client=FakeClient(
            payload=payload,
        )
    )

    markets = source.list_markets()

    assert markets[0][
        "native_symbol"
    ] == "BTCUSDT"

    assert markets[0][
        "symbol"
    ] == "BTC/USDT"


def test_unknown_quote_symbol_is_skipped():
    payload = build_payload()

    payload["symbols"].append(
        "UNKNOWNXYZ"
    )

    source = WeexNativeMarketSource(
        client=FakeClient(
            payload=payload,
        )
    )

    markets = source.list_markets()

    assert len(markets) == 4


def test_empty_symbol_is_skipped():
    payload = build_payload()

    payload["symbols"].extend([
        "",
        None,
    ])

    source = WeexNativeMarketSource(
        client=FakeClient(
            payload=payload,
        )
    )

    markets = source.list_markets()

    assert len(markets) == 4


def test_failed_fetch_fails_closed():
    source = WeexNativeMarketSource(
        client=FakeClient(
            payload={
                "fetch_complete": False,
                "reason": "request_failed",
            }
        )
    )

    with pytest.raises(
        RuntimeError,
        match="WEEX symbols unavailable",
    ):
        source.list_markets()


def test_invalid_payload_fails_closed():
    source = WeexNativeMarketSource(
        client=FakeClient(
            payload=None,
        )
    )

    with pytest.raises(
        RuntimeError,
        match="WEEX symbols unavailable",
    ):
        source.list_markets()


def test_symbols_must_be_list():
    source = WeexNativeMarketSource(
        client=FakeClient(
            payload={
                "fetch_complete": True,
                "symbols": {},
            }
        )
    )

    with pytest.raises(
        RuntimeError,
        match="WEEX symbols unavailable",
    ):
        source.list_markets()


def test_client_failure_is_wrapped():
    source = WeexNativeMarketSource(
        client=FakeClient(
            error=RuntimeError(
                "network down"
            )
        )
    )

    with pytest.raises(
        RuntimeError,
        match="WEEX symbols unavailable",
    ):
        source.list_markets()


def test_requires_client():
    with pytest.raises(
        ValueError,
        match="client is required",
    ):
        WeexNativeMarketSource(
            client=None,
        )
