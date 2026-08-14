import pytest

from exchanges.ourbit_native_order_book_provider import (
    OurbitNativeOrderBookProvider,
)


class FakeClient:
    def fetch_order_book(
        self,
        symbol,
        limit=20,
    ):
        return {
            "fetch_complete": True,
            "symbol": "BTCUSDT",
            "bids": [
                ["62895.79", "6.319350"],
                ["62895.71", "2.216495"],
            ],
            "asks": [
                ["62895.80", "4.504951"],
                ["62895.87", "2.284189"],
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
            "best_bid": 62895.79,
            "best_ask": 62895.80,
            "bids": [
                {
                    "price": 62895.79,
                    "quantity": 6.319350,
                },
                {
                    "price": 62895.71,
                    "quantity": 2.216495,
                },
            ],
            "asks": [
                {
                    "price": 62895.80,
                    "quantity": 4.504951,
                },
                {
                    "price": 62895.87,
                    "quantity": 2.284189,
                },
            ],
            "paper_only": True,
            "live_order_submitted": False,
        }


def build_provider():
    return OurbitNativeOrderBookProvider(
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
    ] == "ourbit"

    assert result[
        "symbol"
    ] == "BTC/USDT"

    assert result[
        "best_bid"
    ] == 62895.79

    assert result[
        "best_ask"
    ] == 62895.80

    assert result[
        "bids"
    ][0] == [
        62895.79,
        6.319350,
    ]

    assert result[
        "asks"
    ][0] == [
        62895.80,
        4.504951,
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

    provider = OurbitNativeOrderBookProvider(
        client=FakeClient(),
        adapter=FailedAdapter(),
    )

    with pytest.raises(
        RuntimeError,
        match="Ourbit order book unavailable",
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
        OurbitNativeOrderBookProvider(
            client=None,
            adapter=FakeAdapter(),
        )


def test_adapter_is_required():
    with pytest.raises(
        ValueError,
        match="adapter is required",
    ):
        OurbitNativeOrderBookProvider(
            client=FakeClient(),
            adapter=None,
        )
