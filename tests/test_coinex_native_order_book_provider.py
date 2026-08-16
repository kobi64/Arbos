import pytest

from exchanges.coinex_native_order_book_provider import (
    CoinExNativeOrderBookProvider,
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
            "best_bid": 63043.0,
            "best_ask": 63044.0,
            "bids": [
                [63043.0, 0.80432751],
                [63042.0, 0.10088271],
            ],
            "asks": [
                [63044.0, 0.03977209],
                [63045.0, 0.00158618],
            ],
            "bid_timestamps": [
                1786843279189,
                1786843279189,
            ],
            "ask_timestamps": [
                1786843279189,
                1786843279189,
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
    return CoinExNativeOrderBookProvider(
        adapter=FakeAdapter(),
    )


def test_snapshot_returns_standard_book():
    result = build_provider().snapshot(
        "BTC/USDT",
        limit=20,
    )

    assert result["exchange"] == "coinex"
    assert result["symbol"] == "BTC/USDT"
    assert result["best_bid"] == 63043.0
    assert result["best_ask"] == 63044.0

    assert result["bids"][0] == [
        63043.0,
        0.80432751,
    ]

    assert result["asks"][0] == [
        63044.0,
        0.03977209,
    ]


def test_snapshot_preserves_timestamp_metadata():
    result = build_provider().snapshot(
        "BTC/USDT"
    )

    assert result[
        "bid_timestamps"
    ][0] == 1786843279189

    assert result[
        "ask_timestamps"
    ][0] == 1786843279189


def test_snapshot_is_paper_safe():
    result = build_provider().snapshot(
        "BTC/USDT"
    )

    assert result["paper_only"] is True
    assert result[
        "live_order_submitted"
    ] is False


def test_unavailable_book_raises():
    provider = CoinExNativeOrderBookProvider(
        adapter=FailedAdapter(),
    )

    with pytest.raises(
        RuntimeError,
        match="CoinEx order book unavailable",
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
        CoinExNativeOrderBookProvider(
            adapter=None,
        )
