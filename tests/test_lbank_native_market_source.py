import pytest

from exchanges.lbank_native_market_source import (
    LBankNativeMarketSource,
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
            "btc_usdt",
            "eth_usdt",
            "trx_eth",
            "dgb_usdt",
            "btc3l_usdt",
            "btc3s_usdt",
        ],
        "market_count": 6,
        "reason": None,
        "paper_only": True,
        "live_order_submitted": False,
    }


def test_lists_standard_spot_markets():
    client = FakeClient(
        payload=build_payload(),
    )

    source = LBankNativeMarketSource(
        client=client,
    )

    markets = source.list_markets()

    assert len(markets) == 4

    assert markets[0] == {
        "symbol": "BTC/USDT",
        "native_symbol": "btc_usdt",
        "base": "BTC",
        "quote": "USDT",
        "active": True,
    }

    assert markets[1][
        "symbol"
    ] == "ETH/USDT"

    assert markets[2][
        "symbol"
    ] == "TRX/ETH"

    assert markets[3][
        "symbol"
    ] == "DGB/USDT"

    assert client.calls == 1


def test_leveraged_tokens_are_filtered():
    source = LBankNativeMarketSource(
        client=FakeClient(
            payload=build_payload(),
        )
    )

    markets = source.list_markets()

    symbols = [
        market["symbol"]
        for market in markets
    ]

    assert "BTC3L/USDT" not in symbols
    assert "BTC3S/USDT" not in symbols


def test_symbols_are_normalized_to_uppercase():
    payload = build_payload()

    payload["markets"] = [
        "BtC_UsDt",
    ]

    source = LBankNativeMarketSource(
        client=FakeClient(
            payload=payload,
        )
    )

    market = source.list_markets()[0]

    assert market[
        "native_symbol"
    ] == "btc_usdt"

    assert market[
        "symbol"
    ] == "BTC/USDT"


def test_invalid_symbol_is_skipped():
    payload = build_payload()

    payload["markets"].extend([
        "",
        "INVALID",
        None,
    ])

    source = LBankNativeMarketSource(
        client=FakeClient(
            payload=payload,
        )
    )

    markets = source.list_markets()

    assert len(markets) == 4


def test_multiple_underscores_are_skipped():
    payload = build_payload()

    payload["markets"].append(
        "abc_def_usdt"
    )

    source = LBankNativeMarketSource(
        client=FakeClient(
            payload=payload,
        )
    )

    markets = source.list_markets()

    assert len(markets) == 4


def test_failed_fetch_fails_closed():
    source = LBankNativeMarketSource(
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
        match="LBank markets unavailable",
    ):
        source.list_markets()


def test_invalid_payload_fails_closed():
    source = LBankNativeMarketSource(
        client=FakeClient(
            payload=None,
        )
    )

    with pytest.raises(
        RuntimeError,
        match="LBank markets unavailable",
    ):
        source.list_markets()


def test_markets_must_be_list():
    source = LBankNativeMarketSource(
        client=FakeClient(
            payload={
                "fetch_complete": True,
                "markets": {},
            }
        )
    )

    with pytest.raises(
        RuntimeError,
        match="LBank markets unavailable",
    ):
        source.list_markets()


def test_client_failure_is_wrapped():
    source = LBankNativeMarketSource(
        client=FakeClient(
            error=RuntimeError(
                "network down"
            )
        )
    )

    with pytest.raises(
        RuntimeError,
        match="LBank markets unavailable",
    ):
        source.list_markets()


def test_requires_client():
    with pytest.raises(
        ValueError,
        match="client is required",
    ):
        LBankNativeMarketSource(
            client=None,
        )
