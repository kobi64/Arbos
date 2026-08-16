import pytest

from exchanges.binance_verification_adapter import (
    BinanceVerificationAdapter,
)


class FakeClient:
    def fetch_order_book(
        self,
        symbol,
        limit=20,
    ):
        return {
            "lastUpdateId": 98569939561,
            "bids": [
                [
                    "63043.99000000",
                    "7.78416000",
                ],
                [
                    "63043.98000000",
                    "0.58139000",
                ],
            ],
            "asks": [
                [
                    "63044.00000000",
                    "40.98952000",
                ],
                [
                    "63044.01000000",
                    "0.00115000",
                ],
            ],
        }

    def fetch_book_ticker(
        self,
        symbol,
    ):
        return {
            "symbol": "BTCUSDT",
            "bidPrice": "63043.99000000",
            "bidQty": "7.83416000",
            "askPrice": "63044.00000000",
            "askQty": "40.98952000",
        }


def test_client_is_required():
    with pytest.raises(
        ValueError,
        match="client is required",
    ):
        BinanceVerificationAdapter(
            client=None,
        )


def test_normalizes_verified_order_book():
    adapter = BinanceVerificationAdapter(
        client=FakeClient(),
    )

    result = adapter.fetch_order_book(
        "BTC/USDT"
    )

    assert result[
        "verification_available"
    ] is True

    assert result["verified"] is True
    assert result["best_bid"] == 63043.99
    assert result["best_ask"] == 63044.0

    assert result["bids"][0] == [
        63043.99,
        7.78416,
    ]

    assert result["asks"][0] == [
        63044.0,
        40.98952,
    ]


def test_native_symbol_is_normalized():
    adapter = BinanceVerificationAdapter(
        client=FakeClient(),
    )

    result = adapter.fetch_order_book(
        " btc/usdt "
    )

    assert result[
        "native_symbol"
    ] == "BTCUSDT"


def test_last_update_id_is_preserved():
    adapter = BinanceVerificationAdapter(
        client=FakeClient(),
    )

    result = adapter.fetch_order_book(
        "BTC/USDT"
    )

    assert result[
        "sequence_id"
    ] == 98569939561


def test_ticker_mismatch_fails_closed():
    class MismatchClient(FakeClient):
        def fetch_book_ticker(
            self,
            symbol,
        ):
            return {
                "symbol": "BTCUSDT",
                "bidPrice": "62000",
                "bidQty": "1",
                "askPrice": "62001",
                "askQty": "1",
            }

    adapter = BinanceVerificationAdapter(
        client=MismatchClient(),
    )

    result = adapter.fetch_order_book(
        "BTC/USDT"
    )

    assert result["verified"] is False

    assert result[
        "verification_available"
    ] is False


def test_crossed_book_fails_closed():
    class CrossedClient(FakeClient):
        def fetch_order_book(
            self,
            symbol,
            limit=20,
        ):
            return {
                "lastUpdateId": 1,
                "bids": [
                    [
                        "100.1",
                        "1",
                    ],
                ],
                "asks": [
                    [
                        "100.0",
                        "1",
                    ],
                ],
            }

    adapter = BinanceVerificationAdapter(
        client=CrossedClient(),
    )

    result = adapter.fetch_order_book(
        "BTC/USDT"
    )

    assert result["verified"] is False


def test_empty_book_fails_closed():
    class EmptyClient(FakeClient):
        def fetch_order_book(
            self,
            symbol,
            limit=20,
        ):
            return {
                "lastUpdateId": 1,
                "bids": [],
                "asks": [],
            }

    adapter = BinanceVerificationAdapter(
        client=EmptyClient(),
    )

    result = adapter.fetch_order_book(
        "BTC/USDT"
    )

    assert result["verified"] is False


def test_fetch_failure_fails_closed():
    class FailedClient:
        def fetch_order_book(
            self,
            symbol,
            limit=20,
        ):
            raise RuntimeError(
                "depth unavailable"
            )

        def fetch_book_ticker(
            self,
            symbol,
        ):
            raise RuntimeError(
                "ticker unavailable"
            )

    adapter = BinanceVerificationAdapter(
        client=FailedClient(),
    )

    result = adapter.fetch_order_book(
        "BTC/USDT"
    )

    assert result[
        "verification_available"
    ] is False

    assert result["verified"] is False


def test_paper_safe_flags_are_preserved():
    adapter = BinanceVerificationAdapter(
        client=FakeClient(),
    )

    result = adapter.fetch_order_book(
        "BTC/USDT"
    )

    assert result["paper_only"] is True

    assert result[
        "live_order_submitted"
    ] is False
