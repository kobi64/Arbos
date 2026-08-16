import pytest

from exchanges.ourbit_native_market_source import (
    OurbitNativeMarketSource,
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
                "symbol": "BTCUSDT",
                "status": "ENABLED",
                "baseAsset": "BTC",
                "quoteAsset": "USDT",
                "permissions": ["SPOT"],
                "isSpotTradingAllowed": False,
            },
            {
                "symbol": "ETHUSDT",
                "status": "ENABLED",
                "baseAsset": "ETH",
                "quoteAsset": "USDT",
                "permissions": ["SPOT"],
                "isSpotTradingAllowed": False,
            },
        ],
        "market_count": 2,
        "reason": None,
        "paper_only": True,
        "live_order_submitted": False,
    }


def test_lists_enabled_spot_markets():
    client = FakeClient(
        payload=build_payload(),
    )

    source = OurbitNativeMarketSource(
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
    }

    assert markets[1][
        "symbol"
    ] == "ETH/USDT"

    assert client.calls == 1


def test_disabled_market_is_filtered():
    payload = build_payload()

    payload["markets"][0][
        "status"
    ] = "DISABLED"

    source = OurbitNativeMarketSource(
        client=FakeClient(
            payload=payload,
        )
    )

    markets = source.list_markets()

    assert len(markets) == 1

    assert markets[0][
        "symbol"
    ] == "ETH/USDT"


def test_non_spot_permission_is_filtered():
    payload = build_payload()

    payload["markets"][0][
        "permissions"
    ] = ["MARGIN"]

    source = OurbitNativeMarketSource(
        client=FakeClient(
            payload=payload,
        )
    )

    markets = source.list_markets()

    assert len(markets) == 1

    assert markets[0][
        "symbol"
    ] == "ETH/USDT"


def test_is_spot_trading_allowed_false_does_not_filter():
    payload = build_payload()

    payload["markets"][0][
        "isSpotTradingAllowed"
    ] = False

    source = OurbitNativeMarketSource(
        client=FakeClient(
            payload=payload,
        )
    )

    markets = source.list_markets()

    assert markets[0][
        "symbol"
    ] == "BTC/USDT"


def test_market_fields_are_normalized_to_uppercase():
    payload = build_payload()

    payload["markets"][0] = {
        "symbol": "btcusdt",
        "status": "enabled",
        "baseAsset": "btc",
        "quoteAsset": "usdt",
        "permissions": ["spot"],
        "isSpotTradingAllowed": False,
    }

    source = OurbitNativeMarketSource(
        client=FakeClient(
            payload=payload,
        )
    )

    market = source.list_markets()[0]

    assert market[
        "native_symbol"
    ] == "BTCUSDT"

    assert market[
        "symbol"
    ] == "BTC/USDT"

    assert market[
        "base"
    ] == "BTC"

    assert market[
        "quote"
    ] == "USDT"


def test_inconsistent_native_symbol_is_skipped():
    payload = build_payload()

    payload["markets"].append({
        "symbol": "SOLBTC",
        "status": "ENABLED",
        "baseAsset": "SOL",
        "quoteAsset": "USDT",
        "permissions": ["SPOT"],
    })

    source = OurbitNativeMarketSource(
        client=FakeClient(
            payload=payload,
        )
    )

    markets = source.list_markets()

    assert len(markets) == 2


def test_invalid_market_entry_is_skipped():
    payload = build_payload()

    payload["markets"].extend([
        None,
        {},
        "BTCUSDT",
    ])

    source = OurbitNativeMarketSource(
        client=FakeClient(
            payload=payload,
        )
    )

    markets = source.list_markets()

    assert len(markets) == 2


def test_failed_fetch_fails_closed():
    source = OurbitNativeMarketSource(
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
        match="Ourbit markets unavailable",
    ):
        source.list_markets()


def test_invalid_payload_fails_closed():
    source = OurbitNativeMarketSource(
        client=FakeClient(
            payload=None,
        )
    )

    with pytest.raises(
        RuntimeError,
        match="Ourbit markets unavailable",
    ):
        source.list_markets()


def test_markets_must_be_list():
    source = OurbitNativeMarketSource(
        client=FakeClient(
            payload={
                "fetch_complete": True,
                "markets": {},
            }
        )
    )

    with pytest.raises(
        RuntimeError,
        match="Ourbit markets unavailable",
    ):
        source.list_markets()


def test_client_failure_is_wrapped():
    source = OurbitNativeMarketSource(
        client=FakeClient(
            error=RuntimeError(
                "network down"
            )
        )
    )

    with pytest.raises(
        RuntimeError,
        match="Ourbit markets unavailable",
    ):
        source.list_markets()


def test_requires_client():
    with pytest.raises(
        ValueError,
        match="client is required",
    ):
        OurbitNativeMarketSource(
            client=None,
        )
