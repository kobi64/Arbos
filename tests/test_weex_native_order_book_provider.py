import pytest

from exchanges.weex_native_order_book_provider import (
    WeexNativeOrderBookProvider,
)


class FakeWeexProvider:
    def __init__(self):
        self.calls = []

    def get_order_book(
        self,
        symbol,
        limit=200,
    ):
        self.calls.append({
            "symbol": symbol,
            "limit": limit,
        })

        return {
            "exchange": "weex",
            "available": True,
            "symbol": symbol,
            "best_bid": 0.1000,
            "best_ask": 0.1010,
            "bids": [
                {
                    "price": 0.1000,
                    "quantity": 100.0,
                },
            ],
            "asks": [
                {
                    "price": 0.1010,
                    "quantity": 50.0,
                },
            ],
            "paper_only": True,
            "live_order_submitted": False,
        }


def test_snapshot_converts_ccxt_symbol_for_weex():
    backend = FakeWeexProvider()

    provider = WeexNativeOrderBookProvider(
        provider=backend,
    )

    result = provider.snapshot(
        "FIR/USDT",
        limit=200,
    )

    assert backend.calls == [
        {
            "symbol": "FIRUSDT",
            "limit": 200,
        }
    ]

    assert result[
        "symbol"
    ] == "FIR/USDT"


def test_snapshot_exposes_standard_book_levels():
    provider = WeexNativeOrderBookProvider(
        provider=FakeWeexProvider(),
    )

    result = provider.snapshot(
        "FIR/USDT"
    )

    assert result[
        "bids"
    ] == [
        [0.1000, 100.0],
    ]

    assert result[
        "asks"
    ] == [
        [0.1010, 50.0],
    ]


def test_snapshot_is_paper_safe():
    provider = WeexNativeOrderBookProvider(
        provider=FakeWeexProvider(),
    )

    result = provider.snapshot(
        "FIR/USDT"
    )

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False


def test_unavailable_book_raises():
    class UnavailableProvider:
        def get_order_book(
            self,
            symbol,
            limit=200,
        ):
            return {
                "available": False,
                "reason": "request_failed",
            }

    provider = WeexNativeOrderBookProvider(
        provider=UnavailableProvider(),
    )

    with pytest.raises(
        RuntimeError,
        match="WEEX order book unavailable",
    ):
        provider.snapshot(
            "FIR/USDT"
        )


def test_symbol_is_required():
    provider = WeexNativeOrderBookProvider(
        provider=FakeWeexProvider(),
    )

    with pytest.raises(
        ValueError,
        match="symbol is required",
    ):
        provider.snapshot("")


def test_provider_is_required():
    with pytest.raises(
        ValueError,
        match="provider is required",
    ):
        WeexNativeOrderBookProvider(
            provider=None
        )
