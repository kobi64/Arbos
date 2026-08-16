import pytest

from exchanges.okx_native_order_book_provider import (
    OKXNativeOrderBookProvider,
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
            "native_symbol": "BTC-USDT",
            "best_bid": 63053.0,
            "best_ask": 63053.1,
            "bids": [
                [
                    63053.0,
                    0.61001039,
                ],
            ],
            "asks": [
                [
                    63053.1,
                    1.72838554,
                ],
            ],
            "bid_timestamps": [
                1786859533954,
            ],
            "ask_timestamps": [
                1786859533954,
            ],
            "sequence_id": 79790738998,
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
            "native_symbol": None,
            "best_bid": None,
            "best_ask": None,
            "bids": [],
            "asks": [],
            "bid_timestamps": [],
            "ask_timestamps": [],
            "sequence_id": None,
            "reason": "order_book_unavailable",
            "paper_only": True,
            "live_order_submitted": False,
        }


def build_provider():
    return OKXNativeOrderBookProvider(
        adapter=FakeAdapter(),
    )


def test_snapshot_returns_standard_book():
    result = build_provider().snapshot(
        "BTC/USDT"
    )

    assert result["exchange"] == "okx"
    assert result["symbol"] == "BTC/USDT"
    assert result["native_symbol"] == (
        "BTC-USDT"
    )

    assert result["best_bid"] == 63053.0
    assert result["best_ask"] == 63053.1

    assert result["bids"] == [
        [
            63053.0,
            0.61001039,
        ]
    ]

    assert result["asks"] == [
        [
            63053.1,
            1.72838554,
        ]
    ]


def test_snapshot_preserves_timestamps():
    result = build_provider().snapshot(
        "BTC/USDT"
    )

    assert result[
        "bid_timestamps"
    ] == [
        1786859533954
    ]

    assert result[
        "ask_timestamps"
    ] == [
        1786859533954
    ]


def test_snapshot_preserves_sequence_id():
    result = build_provider().snapshot(
        "BTC/USDT"
    )

    assert result[
        "sequence_id"
    ] == 79790738998


def test_snapshot_is_paper_safe():
    result = build_provider().snapshot(
        "BTC/USDT"
    )

    assert result["paper_only"] is True

    assert result[
        "live_order_submitted"
    ] is False


def test_unavailable_book_raises():
    provider = OKXNativeOrderBookProvider(
        adapter=FailedAdapter(),
    )

    with pytest.raises(
        RuntimeError,
        match="OKX order book unavailable",
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
        OKXNativeOrderBookProvider(
            adapter=None,
        )
