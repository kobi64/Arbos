import pytest

from exchanges.bingx_native_order_book_provider import (
    BingXNativeOrderBookProvider,
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
            "symbol": "BTC-USDT",
            "best_bid": 63000.0,
            "best_ask": 63001.0,
            "bids": [
                [63000.0, 1.25],
                [62999.0, 2.0],
            ],
            "asks": [
                [63001.0, 1.5],
                [63002.0, 2.5],
            ],
            "timestamp": 1700000000000,
            "last_update_id": 12345,
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
            "symbol": "BTC-USDT",
            "best_bid": None,
            "best_ask": None,
            "bids": [],
            "asks": [],
            "timestamp": None,
            "last_update_id": None,
            "reason": "order_book_unavailable",
            "paper_only": True,
            "live_order_submitted": False,
        }


def build_provider():
    return BingXNativeOrderBookProvider(
        adapter=FakeAdapter(),
    )


def test_snapshot_returns_standard_book():
    result = build_provider().snapshot(
        "BTC/USDT",
        limit=20,
    )

    assert result[
        "exchange"
    ] == "bingx"

    assert result[
        "symbol"
    ] == "BTC/USDT"

    assert result[
        "best_bid"
    ] == 63000.0

    assert result[
        "best_ask"
    ] == 63001.0

    assert result[
        "bids"
    ][0] == [
        63000.0,
        1.25,
    ]

    assert result[
        "asks"
    ][0] == [
        63001.0,
        1.5,
    ]


def test_snapshot_preserves_timestamp_and_update_id():
    result = build_provider().snapshot(
        "BTC/USDT"
    )

    assert result[
        "timestamp"
    ] == 1700000000000

    assert result[
        "last_update_id"
    ] == 12345


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
    provider = BingXNativeOrderBookProvider(
        adapter=FailedAdapter(),
    )

    with pytest.raises(
        RuntimeError,
        match="BingX order book unavailable",
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
        BingXNativeOrderBookProvider(
            adapter=None,
        )
