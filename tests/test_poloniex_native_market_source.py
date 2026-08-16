import pytest

from exchanges.poloniex_native_market_source import (
    PoloniexNativeMarketSource,
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

    def fetch_markets(self):
        self.calls += 1

        if self.error is not None:
            raise self.error

        return self.payload


def build_payload():
    return {
        "fetch_complete": True,
        "markets": [
            {
                "symbol": "BTC_USDT",
                "baseCurrencyName": "BTC",
                "quoteCurrencyName": "USDT",
                "state": "NORMAL",
            },
            {
                "symbol": "ETH_USDT",
                "baseCurrencyName": "ETH",
                "quoteCurrencyName": "USDT",
                "state": "NORMAL",
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

    source = PoloniexNativeMarketSource(
        client=client,
    )

    markets = source.list_markets()

    assert len(markets) == 2

    assert markets[0] == {
        "symbol": "BTC/USDT",
        "native_symbol": "BTC_USDT",
        "base": "BTC",
        "quote": "USDT",
        "active": True,
    }

    assert markets[1][
        "symbol"
    ] == "ETH/USDT"

    assert client.calls == 1


def test_non_normal_market_is_filtered():
    payload = build_payload()

    payload["markets"][0][
        "state"
    ] = "OFFLINE"

    source = PoloniexNativeMarketSource(
        client=FakeClient(
            payload=payload,
        )
    )

    markets = source.list_markets()

    assert len(markets) == 1

    assert markets[0][
        "symbol"
    ] == "ETH/USDT"


def test_market_fields_are_normalized_to_uppercase():
    payload = build_payload()

    payload["markets"][0] = {
        "symbol": "btc_usdt",
        "baseCurrencyName": "btc",
        "quoteCurrencyName": "usdt",
        "state": "normal",
    }

    source = PoloniexNativeMarketSource(
        client=FakeClient(
            payload=payload,
        )
    )

    market = source.list_markets()[0]

    assert market[
        "native_symbol"
    ] == "BTC_USDT"

    assert market[
        "symbol"
    ] == "BTC/USDT"

    assert market[
        "base"
    ] == "BTC"

    assert market[
        "quote"
    ] == "USDT"


def test_invalid_market_entry_is_skipped():
    payload = build_payload()

    payload["markets"].append({
        "state": "NORMAL",
    })

    source = PoloniexNativeMarketSource(
        client=FakeClient(
            payload=payload,
        )
    )

    markets = source.list_markets()

    assert len(markets) == 2


def test_inconsistent_symbol_is_skipped():
    payload = build_payload()

    payload["markets"].append({
        "symbol": "SOL_BTC",
        "baseCurrencyName": "SOL",
        "quoteCurrencyName": "USDT",
        "state": "NORMAL",
    })

    source = PoloniexNativeMarketSource(
        client=FakeClient(
            payload=payload,
        )
    )

    markets = source.list_markets()

    assert len(markets) == 2


def test_failed_fetch_fails_closed():
    source = PoloniexNativeMarketSource(
        client=FakeClient(
            payload={
                "fetch_complete": False,
                "markets": [],
                "reason": "HTTP 500",
            }
        )
    )

    with pytest.raises(
        RuntimeError,
        match="Poloniex markets unavailable",
    ):
        source.list_markets()


def test_invalid_payload_fails_closed():
    source = PoloniexNativeMarketSource(
        client=FakeClient(
            payload=None,
        )
    )

    with pytest.raises(
        RuntimeError,
        match="Poloniex markets unavailable",
    ):
        source.list_markets()


def test_markets_must_be_list():
    source = PoloniexNativeMarketSource(
        client=FakeClient(
            payload={
                "fetch_complete": True,
                "markets": {},
            }
        )
    )

    with pytest.raises(
        RuntimeError,
        match="Poloniex markets unavailable",
    ):
        source.list_markets()


def test_client_failure_is_wrapped():
    source = PoloniexNativeMarketSource(
        client=FakeClient(
            error=RuntimeError(
                "network down"
            )
        )
    )

    with pytest.raises(
        RuntimeError,
        match="Poloniex markets unavailable",
    ):
        source.list_markets()


def test_requires_client():
    with pytest.raises(
        ValueError,
        match="client is required",
    ):
        PoloniexNativeMarketSource(
            client=None,
        )
