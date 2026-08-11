import pytest

from exchanges.kucoin_native_order_book_source import (
    KuCoinNativeOrderBookSource,
)


class FakeExchange:
    def publicGetMarketOrderbookLevel220(
        self,
        params,
    ):
        assert params == {
            "symbol": "COTI-USDT",
        }

        return {
            "code": "200000",
            "data": {
                "time": 123456789,
                "sequence": "100",
                "bids": [
                    ["0.00951", "11532.24"],
                    ["0.00950", "12624.93"],
                ],
                "asks": [
                    ["0.00953", "5308.23"],
                    ["0.00955", "17933.16"],
                ],
            },
        }


class FailedExchange:
    def publicGetMarketOrderbookLevel220(
        self,
        params,
    ):
        raise RuntimeError("native failure")


def test_fetches_native_order_book():
    result = KuCoinNativeOrderBookSource(
        FakeExchange()
    ).snapshot(
        "COTI/USDT"
    )

    assert result["symbol"] == "COTI/USDT"

    assert result["bids"] == [
        [0.00951, 11532.24],
        [0.00950, 12624.93],
    ]

    assert result["asks"] == [
        [0.00953, 5308.23],
        [0.00955, 17933.16],
    ]


def test_preserves_timestamp_and_sequence():
    result = KuCoinNativeOrderBookSource(
        FakeExchange()
    ).snapshot(
        "COTI/USDT"
    )

    assert result["timestamp"] == 123456789
    assert result["sequence"] == "100"


def test_marks_native_market_source():
    result = KuCoinNativeOrderBookSource(
        FakeExchange()
    ).snapshot(
        "COTI/USDT"
    )

    assert result["market_source"] == (
        "KUCOIN_NATIVE"
    )


def test_converts_symbol_to_native_format():
    result = KuCoinNativeOrderBookSource(
        FakeExchange()
    ).snapshot(
        " coti/usdt "
    )

    assert result["symbol"] == "COTI/USDT"


def test_native_failure_is_propagated():
    source = KuCoinNativeOrderBookSource(
        FailedExchange()
    )

    with pytest.raises(
        RuntimeError,
        match="native failure",
    ):
        source.snapshot(
            "COTI/USDT"
        )


def test_requires_exchange():
    with pytest.raises(
        ValueError,
        match="exchange is required",
    ):
        KuCoinNativeOrderBookSource(
            None
        )


def test_requires_symbol():
    source = KuCoinNativeOrderBookSource(
        FakeExchange()
    )

    with pytest.raises(
        ValueError,
        match="symbol is required",
    ):
        source.snapshot("")
