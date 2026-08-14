import pytest

from exchanges.poloniex_native_order_book_provider import (
    PoloniexNativeOrderBookProvider,
)


class FakeClient:
    def __init__(self):
        self.calls = []

    def fetch_order_book(
        self,
        symbol,
        limit=20,
    ):
        self.calls.append({
            "symbol": symbol,
            "limit": limit,
        })

        return {
            "fetch_complete": True,
            "symbol": symbol,
            "bids": [
                "0.100",
                "75",
                "0.099",
                "125",
            ],
            "asks": [
                "0.101",
                "50",
                "0.102",
                "100",
            ],
            "paper_only": True,
            "live_order_submitted": False,
        }


class FakeAdapter:
    def normalize_order_book(
        self,
        result,
    ):
        return {
            "available": True,
            "symbol": result["symbol"],
            "best_bid": 0.100,
            "best_ask": 0.101,
            "bids": [
                {
                    "price": 0.100,
                    "quantity": 75.0,
                },
                {
                    "price": 0.099,
                    "quantity": 125.0,
                },
            ],
            "asks": [
                {
                    "price": 0.101,
                    "quantity": 50.0,
                },
                {
                    "price": 0.102,
                    "quantity": 100.0,
                },
            ],
            "paper_only": True,
            "live_order_submitted": False,
        }


def build_provider():
    return PoloniexNativeOrderBookProvider(
        client=FakeClient(),
        adapter=FakeAdapter(),
    )


def test_snapshot_converts_ccxt_symbol_to_poloniex():
    client = FakeClient()

    provider = PoloniexNativeOrderBookProvider(
        client=client,
        adapter=FakeAdapter(),
    )

    result = provider.snapshot(
        "FIR/USDT",
        limit=20,
    )

    assert client.calls == [
        {
            "symbol": "FIR_USDT",
            "limit": 20,
        },
    ]

    assert result[
        "symbol"
    ] == "FIR/USDT"


def test_snapshot_exposes_standard_levels():
    result = build_provider().snapshot(
        "FIR/USDT"
    )

    assert result["bids"] == [
        [0.100, 75.0],
        [0.099, 125.0],
    ]

    assert result["asks"] == [
        [0.101, 50.0],
        [0.102, 100.0],
    ]

    assert result[
        "best_bid"
    ] == 0.100

    assert result[
        "best_ask"
    ] == 0.101


def test_snapshot_is_paper_safe():
    result = build_provider().snapshot(
        "FIR/USDT"
    )

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False


def test_unavailable_order_book_raises():
    class FailedAdapter:
        def normalize_order_book(
            self,
            result,
        ):
            return {
                "available": False,
                "reason": "request_failed",
            }

    provider = PoloniexNativeOrderBookProvider(
        client=FakeClient(),
        adapter=FailedAdapter(),
    )

    with pytest.raises(
        RuntimeError,
        match="Poloniex order book unavailable",
    ):
        provider.snapshot(
            "FIR/USDT"
        )


def test_symbol_is_required():
    with pytest.raises(
        ValueError,
        match="symbol is required",
    ):
        build_provider().snapshot("")


def test_client_is_required():
    with pytest.raises(
        ValueError,
        match="client is required",
    ):
        PoloniexNativeOrderBookProvider(
            client=None,
            adapter=FakeAdapter(),
        )


def test_adapter_is_required():
    with pytest.raises(
        ValueError,
        match="adapter is required",
    ):
        PoloniexNativeOrderBookProvider(
            client=FakeClient(),
            adapter=None,
        )
