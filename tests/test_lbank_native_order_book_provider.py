import pytest

from exchanges.lbank_native_order_book_provider import (
    LBankNativeOrderBookProvider,
)


class FakeClient:
    def fetch_order_book(
        self,
        symbol,
        limit=20,
    ):
        return {
            "fetch_complete": True,
            "symbol": "btc_usdt",
            "bids": [
                ["63144.62", "5.64875"],
                ["63144.61", "0.00547"],
            ],
            "asks": [
                ["63144.63", "2.04678"],
                ["63144.64", "0.00181"],
            ],
            "timestamp": 1700000000000,
            "paper_only": True,
            "live_order_submitted": False,
        }


class FakeAdapter:
    def normalize_order_book(
        self,
        payload,
    ):
        return {
            "available": True,
            "symbol": payload["symbol"],
            "timestamp": payload["timestamp"],
            "best_bid": 63144.62,
            "best_ask": 63144.63,
            "bids": [
                {
                    "price": 63144.62,
                    "quantity": 5.64875,
                },
                {
                    "price": 63144.61,
                    "quantity": 0.00547,
                },
            ],
            "asks": [
                {
                    "price": 63144.63,
                    "quantity": 2.04678,
                },
                {
                    "price": 63144.64,
                    "quantity": 0.00181,
                },
            ],
            "paper_only": True,
            "live_order_submitted": False,
        }


def build_provider():
    return LBankNativeOrderBookProvider(
        client=FakeClient(),
        adapter=FakeAdapter(),
    )


def test_snapshot_returns_standard_book():
    result = build_provider().snapshot(
        "BTC/USDT",
        limit=20,
    )

    assert result[
        "exchange"
    ] == "lbank"

    assert result[
        "symbol"
    ] == "BTC/USDT"

    assert result[
        "best_bid"
    ] == 63144.62

    assert result[
        "best_ask"
    ] == 63144.63

    assert result[
        "bids"
    ][0] == [
        63144.62,
        5.64875,
    ]

    assert result[
        "asks"
    ][0] == [
        63144.63,
        2.04678,
    ]


def test_snapshot_preserves_timestamp():
    result = build_provider().snapshot(
        "BTC/USDT"
    )

    assert result[
        "timestamp"
    ] == 1700000000000


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
    class FailedAdapter:
        def normalize_order_book(
            self,
            payload,
        ):
            return {
                "available": False,
                "reason": "request_failed",
            }

    provider = LBankNativeOrderBookProvider(
        client=FakeClient(),
        adapter=FailedAdapter(),
    )

    with pytest.raises(
        RuntimeError,
        match="LBank order book unavailable",
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
        LBankNativeOrderBookProvider(
            client=None,
            adapter=FakeAdapter(),
        )


def test_adapter_is_required():
    with pytest.raises(
        ValueError,
        match="adapter is required",
    ):
        LBankNativeOrderBookProvider(
            client=FakeClient(),
            adapter=None,
        )
