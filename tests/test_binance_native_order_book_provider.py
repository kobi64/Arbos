import pytest

from exchanges.binance_native_order_book_provider import (
    BinanceNativeOrderBookProvider,
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
            "native_symbol": "BTCUSDT",
            "best_bid": 63043.99,
            "best_ask": 63044.0,
            "bids": [
                [
                    63043.99,
                    7.78416,
                ],
            ],
            "asks": [
                [
                    63044.0,
                    40.98952,
                ],
            ],
            "bid_timestamps": [],
            "ask_timestamps": [],
            "sequence_id": 98569939561,
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
            "reason": "depth unavailable",
            "paper_only": True,
            "live_order_submitted": False,
        }


def build_provider():
    return BinanceNativeOrderBookProvider(
        adapter=FakeAdapter(),
    )


def test_snapshot_returns_standard_book():
    result = build_provider().snapshot(
        "BTC/USDT"
    )

    assert result["exchange"] == "binance"
    assert result["symbol"] == "BTC/USDT"
    assert result["native_symbol"] == (
        "BTCUSDT"
    )

    assert result["best_bid"] == 63043.99
    assert result["best_ask"] == 63044.0

    assert result["bids"] == [
        [
            63043.99,
            7.78416,
        ]
    ]

    assert result["asks"] == [
        [
            63044.0,
            40.98952,
        ]
    ]


def test_snapshot_preserves_sequence_id():
    result = build_provider().snapshot(
        "BTC/USDT"
    )

    assert result[
        "sequence_id"
    ] == 98569939561


def test_snapshot_is_paper_safe():
    result = build_provider().snapshot(
        "BTC/USDT"
    )

    assert result["paper_only"] is True

    assert result[
        "live_order_submitted"
    ] is False


def test_unavailable_book_raises():
    provider = BinanceNativeOrderBookProvider(
        adapter=FailedAdapter(),
    )

    with pytest.raises(
        RuntimeError,
        match="Binance order book unavailable",
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
        BinanceNativeOrderBookProvider(
            adapter=None,
        )
