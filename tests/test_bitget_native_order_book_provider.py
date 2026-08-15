import pytest

from exchanges.bitget_native_order_book_provider import (
    BitgetNativeOrderBookProvider,
)


class FakeAdapter:
    def fetch_order_book(
        self,
        symbol,
        limit=20,
    ):
        return {
            "verification_available": True,
            "verified": True,
            "symbol": "BTC/USDT",
            "best_bid": 63038.5,
            "best_ask": 63039.0,
            "bids": [
                [63038.5, 0.047],
                [63038.4, 0.107],
            ],
            "asks": [
                [63039.0, 0.070],
                [63044.5, 0.427],
            ],
            "bid_timestamps": [
                "1700000000000",
                "1700000000000",
            ],
            "ask_timestamps": [
                "1700000000000",
                "1700000000000",
            ],
            "reason": None,
            "paper_only": True,
            "live_order_submitted": False,
        }


class FailedAdapter:
    def fetch_order_book(
        self,
        symbol,
        limit=20,
    ):
        return {
            "verification_available": False,
            "verified": False,
            "symbol": "BTC/USDT",
            "best_bid": None,
            "best_ask": None,
            "bids": [],
            "asks": [],
            "bid_timestamps": [],
            "ask_timestamps": [],
            "reason": "order_book_unavailable",
            "paper_only": True,
            "live_order_submitted": False,
        }


def build_provider():
    return BitgetNativeOrderBookProvider(
        adapter=FakeAdapter(),
    )


def test_snapshot_returns_standard_book():
    result = build_provider().snapshot(
        "BTC/USDT",
        limit=20,
    )

    assert result[
        "exchange"
    ] == "bitget"

    assert result[
        "symbol"
    ] == "BTC/USDT"

    assert result[
        "best_bid"
    ] == 63038.5

    assert result[
        "best_ask"
    ] == 63039.0

    assert result[
        "bids"
    ][0] == [
        63038.5,
        0.047,
    ]

    assert result[
        "asks"
    ][0] == [
        63039.0,
        0.070,
    ]


def test_snapshot_preserves_timestamp_metadata():
    result = build_provider().snapshot(
        "BTC/USDT"
    )

    assert result[
        "bid_timestamps"
    ][0] == "1700000000000"

    assert result[
        "ask_timestamps"
    ][0] == "1700000000000"


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


def test_unavailable_book_raises():
    provider = BitgetNativeOrderBookProvider(
        adapter=FailedAdapter(),
    )

    with pytest.raises(
        RuntimeError,
        match="Bitget order book unavailable",
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


def test_adapter_is_required():
    with pytest.raises(
        ValueError,
        match="adapter is required",
    ):
        BitgetNativeOrderBookProvider(
            adapter=None,
        )
