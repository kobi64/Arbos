import pytest

from exchanges.xt_native_order_book_provider import (
    XTNativeOrderBookProvider,
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
            "best_bid": 63094.99,
            "best_ask": 63095.00,
            "bids": [
                [63094.99, 23.31624],
                [63094.97, 0.35580],
            ],
            "asks": [
                [63095.00, 12.14463],
                [63095.09, 0.43631],
            ],
            "bid_timestamps": [
                1700000000000,
                1700000000000,
            ],
            "ask_timestamps": [
                1700000000000,
                1700000000000,
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
    return XTNativeOrderBookProvider(
        adapter=FakeAdapter(),
    )


def test_snapshot_returns_standard_book():
    result = build_provider().snapshot(
        "BTC/USDT",
        limit=20,
    )

    assert result[
        "exchange"
    ] == "xt"

    assert result[
        "symbol"
    ] == "BTC/USDT"

    assert result[
        "best_bid"
    ] == 63094.99

    assert result[
        "best_ask"
    ] == 63095.00

    assert result[
        "bids"
    ][0] == [
        63094.99,
        23.31624,
    ]

    assert result[
        "asks"
    ][0] == [
        63095.00,
        12.14463,
    ]


def test_snapshot_preserves_timestamp_metadata():
    result = build_provider().snapshot(
        "BTC/USDT"
    )

    assert result[
        "bid_timestamps"
    ][0] == 1700000000000

    assert result[
        "ask_timestamps"
    ][0] == 1700000000000


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
    provider = XTNativeOrderBookProvider(
        adapter=FailedAdapter(),
    )

    with pytest.raises(
        RuntimeError,
        match="XT order book unavailable",
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
        XTNativeOrderBookProvider(
            adapter=None,
        )
