import pytest

from exchanges.mexc_native_order_book_provider import (
    MexcNativeOrderBookProvider,
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
            "symbol": "BTCUSDT",
            "bids": [
                ["63000.0", "2.0"],
                ["62990.0", "3.0"],
            ],
            "asks": [
                ["63001.0", "1.5"],
                ["63010.0", "4.0"],
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
            "best_bid": 63000.0,
            "best_ask": 63001.0,
            "bids": [
                {
                    "price": 63000.0,
                    "quantity": 2.0,
                },
                {
                    "price": 62990.0,
                    "quantity": 3.0,
                },
            ],
            "asks": [
                {
                    "price": 63001.0,
                    "quantity": 1.5,
                },
                {
                    "price": 63010.0,
                    "quantity": 4.0,
                },
            ],
            "paper_only": True,
            "live_order_submitted": False,
        }


def build_provider():
    return MexcNativeOrderBookProvider(
        client=FakeClient(),
        adapter=FakeAdapter(),
    )


def test_snapshot_uses_ccxt_style_symbol():
    client = FakeClient()

    provider = MexcNativeOrderBookProvider(
        client=client,
        adapter=FakeAdapter(),
    )

    result = provider.snapshot(
        "BTC/USDT",
        limit=20,
    )

    assert client.calls == [
        {
            "symbol": "BTC/USDT",
            "limit": 20,
        },
    ]

    assert result[
        "symbol"
    ] == "BTC/USDT"


def test_snapshot_exposes_standard_levels():
    result = build_provider().snapshot(
        "BTC/USDT"
    )

    assert result[
        "bids"
    ] == [
        [63000.0, 2.0],
        [62990.0, 3.0],
    ]

    assert result[
        "asks"
    ] == [
        [63001.0, 1.5],
        [63010.0, 4.0],
    ]

    assert result[
        "best_bid"
    ] == 63000.0

    assert result[
        "best_ask"
    ] == 63001.0


def test_snapshot_is_paper_safe():
    result = build_provider().snapshot(
        "BTC/USDT"
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

    provider = MexcNativeOrderBookProvider(
        client=FakeClient(),
        adapter=FailedAdapter(),
    )

    with pytest.raises(
        RuntimeError,
        match="MEXC order book unavailable",
    ):
        provider.snapshot(
            "BTC/USDT"
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
        MexcNativeOrderBookProvider(
            client=None,
            adapter=FakeAdapter(),
        )


def test_adapter_is_required():
    with pytest.raises(
        ValueError,
        match="adapter is required",
    ):
        MexcNativeOrderBookProvider(
            client=FakeClient(),
            adapter=None,
        )
