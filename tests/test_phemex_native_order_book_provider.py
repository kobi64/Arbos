import pytest

from exchanges.phemex_native_order_book_provider import (
    PhemexNativeOrderBookProvider,
)


class FakeAdapter:
    def fetch_order_book(
        self,
        symbol,
        limit=30,
    ):
        return {
            "verification_available": True,
            "verified": True,
            "symbol": "BTC/USDT",
            "native_symbol": "sBTCUSDT",
            "best_bid": 63054.68,
            "best_ask": 63054.69,
            "bids": [
                [
                    63054.68,
                    0.042641,
                ],
            ],
            "asks": [
                [
                    63054.69,
                    0.059666,
                ],
            ],
            "bid_timestamps": [
                1786845356093279821,
            ],
            "ask_timestamps": [
                1786845356093279821,
            ],
            "reason": None,
            "paper_only": True,
            "live_order_submitted": False,
        }


class FailedAdapter:
    def fetch_order_book(
        self,
        symbol,
        limit=30,
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
            "reason": "order_book_unavailable",
            "paper_only": True,
            "live_order_submitted": False,
        }


def build_provider():
    return PhemexNativeOrderBookProvider(
        adapter=FakeAdapter(),
    )


def test_snapshot_returns_standard_book():
    result = build_provider().snapshot(
        "BTC/USDT"
    )

    assert result["exchange"] == "phemex"
    assert result["symbol"] == "BTC/USDT"
    assert result["native_symbol"] == (
        "sBTCUSDT"
    )

    assert result["best_bid"] == 63054.68
    assert result["best_ask"] == 63054.69

    assert result["bids"] == [
        [
            63054.68,
            0.042641,
        ]
    ]

    assert result["asks"] == [
        [
            63054.69,
            0.059666,
        ]
    ]


def test_snapshot_preserves_timestamps():
    result = build_provider().snapshot(
        "BTC/USDT"
    )

    assert result[
        "bid_timestamps"
    ] == [
        1786845356093279821
    ]

    assert result[
        "ask_timestamps"
    ] == [
        1786845356093279821
    ]


def test_snapshot_is_paper_safe():
    result = build_provider().snapshot(
        "BTC/USDT"
    )

    assert result["paper_only"] is True
    assert result[
        "live_order_submitted"
    ] is False


def test_unavailable_book_raises():
    provider = PhemexNativeOrderBookProvider(
        adapter=FailedAdapter(),
    )

    with pytest.raises(
        RuntimeError,
        match="Phemex order book unavailable",
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
        PhemexNativeOrderBookProvider(
            adapter=None,
        )
