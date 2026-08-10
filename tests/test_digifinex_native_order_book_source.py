import pytest

from exchanges.digifinex_native_order_book_source import (
    DigiFinexNativeOrderBookSource,
)


class FakeExchange:
    def __init__(self):
        self.calls = []

    def publicSpotGetOrderBook(
        self,
        params,
    ):
        self.calls.append(params)

        return {
            "code": 0,
            "asks": [
                [0.01164, 78810],
                [0.01163, 54060],
            ],
            "bids": [
                [0.01142, 15715],
                [0.01141, 41999.5],
            ],
            "date": 1786370171,
        }


class SnakeCaseExchange:
    def public_spot_get_order_book(
        self,
        params,
    ):
        return {
            "code": 0,
            "asks": [[1.01, 100.0]],
            "bids": [[0.99, 100.0]],
            "date": 123,
        }


def test_fetches_native_coti_order_book():
    exchange = FakeExchange()

    source = DigiFinexNativeOrderBookSource(
        exchange
    )

    result = source.snapshot(
        "COTI/USDT"
    )

    assert exchange.calls == [
        {
            "symbol": "coti_usdt",
        }
    ]

    assert result["symbol"] == (
        "COTI/USDT"
    )

    assert result["best_bid"] == (
        0.01142
    )

    assert result["best_ask"] == (
        0.01163
    )

    assert result["market_source"] == (
        "DIGIFINEX_NATIVE"
    )

    assert (
        result["live_order_submitted"]
        is False
    )


def test_supports_snake_case_method():
    result = (
        DigiFinexNativeOrderBookSource(
            SnakeCaseExchange()
        ).snapshot(
            "TOKEN/USDT"
        )
    )

    assert result["best_bid"] == 0.99
    assert result["best_ask"] == 1.01


def test_rejects_empty_symbol():
    source = DigiFinexNativeOrderBookSource(
        FakeExchange()
    )

    with pytest.raises(
        ValueError,
        match="symbol is required",
    ):
        source.snapshot("")


def test_rejects_invalid_symbol_shape():
    source = DigiFinexNativeOrderBookSource(
        FakeExchange()
    )

    with pytest.raises(
        ValueError,
        match="symbol must be BASE/QUOTE",
    ):
        source.snapshot("COTI")


def test_rejects_empty_book():
    class EmptyExchange:
        def publicSpotGetOrderBook(
            self,
            params,
        ):
            return {
                "code": 0,
                "asks": [],
                "bids": [],
            }

    source = DigiFinexNativeOrderBookSource(
        EmptyExchange()
    )

    with pytest.raises(
        ValueError,
        match="order book unavailable",
    ):
        source.snapshot(
            "COTI/USDT"
        )


def test_missing_exchange_is_rejected():
    with pytest.raises(
        ValueError,
        match="exchange is required",
    ):
        DigiFinexNativeOrderBookSource(
            None
        )
