import pytest

from exchanges.coinbase_native_order_book_provider import (
    CoinbaseNativeOrderBookProvider,
)


class FakeAdapter:
    def fetch_order_book(
        self,
        product_id,
        level=2,
    ):
        return {
            "verification_available": True,
            "verified": True,
            "symbol": "BTC/USD",
            "native_symbol": "BTC-USD",
            "best_bid": 62990.24,
            "best_ask": 62990.25,
            "bids": [
                [
                    62990.24,
                    0.10232494,
                ],
            ],
            "asks": [
                [
                    62990.25,
                    0.2,
                ],
            ],
            "bid_timestamps": [],
            "ask_timestamps": [],
            "sequence_id": 123456789,
            "reason": None,
            "paper_only": True,
            "live_order_submitted": False,
        }


class FailedAdapter:
    def fetch_order_book(
        self,
        product_id,
        level=2,
    ):
        return {
            "verification_available": False,
            "verified": False,
            "symbol": "BTC/USD",
            "native_symbol": None,
            "best_bid": None,
            "best_ask": None,
            "bids": [],
            "asks": [],
            "bid_timestamps": [],
            "ask_timestamps": [],
            "sequence_id": None,
            "reason": "book unavailable",
            "paper_only": True,
            "live_order_submitted": False,
        }


def build_provider():
    return CoinbaseNativeOrderBookProvider(
        adapter=FakeAdapter(),
    )


def test_snapshot_returns_standard_book():
    result = build_provider().snapshot(
        "BTC/USD"
    )

    assert result["exchange"] == "coinbase"
    assert result["symbol"] == "BTC/USD"
    assert result["native_symbol"] == (
        "BTC-USD"
    )

    assert result["best_bid"] == 62990.24
    assert result["best_ask"] == 62990.25

    assert result["bids"] == [
        [
            62990.24,
            0.10232494,
        ]
    ]

    assert result["asks"] == [
        [
            62990.25,
            0.2,
        ]
    ]


def test_snapshot_preserves_sequence_id():
    result = build_provider().snapshot(
        "BTC/USD"
    )

    assert result[
        "sequence_id"
    ] == 123456789


def test_snapshot_is_paper_safe():
    result = build_provider().snapshot(
        "BTC/USD"
    )

    assert result["paper_only"] is True

    assert result[
        "live_order_submitted"
    ] is False


def test_unavailable_book_raises():
    provider = CoinbaseNativeOrderBookProvider(
        adapter=FailedAdapter(),
    )

    with pytest.raises(
        RuntimeError,
        match="Coinbase order book unavailable",
    ):
        provider.snapshot(
            "BTC/USD"
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
        CoinbaseNativeOrderBookProvider(
            adapter=None,
        )
