import pytest

from exchanges.coinbase_verification_adapter import (
    CoinbaseVerificationAdapter,
)


class FakeClient:
    def fetch_order_book(
        self,
        product_id,
        level=2,
    ):
        return {
            "sequence": 123456789,
            "bids": [
                ["62990.24", "0.10232494", 6],
                ["62989.73", "0.10547465", 1],
            ],
            "asks": [
                ["62990.25", "0.20000000", 2],
                ["62990.26", "0.10000000", 1],
            ],
        }

    def fetch_ticker(
        self,
        product_id,
    ):
        return {
            "bid": "62990.24",
            "ask": "62990.25",
            "price": "62990.25",
            "time": "2026-08-16T06:30:24Z",
        }


def test_client_is_required():
    with pytest.raises(
        ValueError,
        match="client is required",
    ):
        CoinbaseVerificationAdapter(
            client=None,
        )


def test_normalizes_verified_order_book():
    adapter = CoinbaseVerificationAdapter(
        client=FakeClient(),
    )

    result = adapter.fetch_order_book(
        "BTC/USD"
    )

    assert result[
        "verification_available"
    ] is True

    assert result["verified"] is True
    assert result["best_bid"] == 62990.24
    assert result["best_ask"] == 62990.25

    assert result["bids"][0] == [
        62990.24,
        0.10232494,
    ]

    assert result["asks"][0] == [
        62990.25,
        0.2,
    ]


def test_native_symbol_is_normalized():
    adapter = CoinbaseVerificationAdapter(
        client=FakeClient(),
    )

    result = adapter.fetch_order_book(
        " btc/usd "
    )

    assert result[
        "native_symbol"
    ] == "BTC-USD"


def test_sequence_is_preserved():
    adapter = CoinbaseVerificationAdapter(
        client=FakeClient(),
    )

    result = adapter.fetch_order_book(
        "BTC/USD"
    )

    assert result[
        "sequence_id"
    ] == 123456789


def test_ticker_mismatch_fails_closed():
    class MismatchClient(FakeClient):
        def fetch_ticker(
            self,
            product_id,
        ):
            return {
                "bid": "62000",
                "ask": "62001",
            }

    adapter = CoinbaseVerificationAdapter(
        client=MismatchClient(),
    )

    result = adapter.fetch_order_book(
        "BTC/USD"
    )

    assert result["verified"] is False

    assert result[
        "verification_available"
    ] is False


def test_crossed_book_fails_closed():
    class CrossedClient(FakeClient):
        def fetch_order_book(
            self,
            product_id,
            level=2,
        ):
            return {
                "sequence": 1,
                "bids": [
                    ["100.1", "1", 1],
                ],
                "asks": [
                    ["100.0", "1", 1],
                ],
            }

    adapter = CoinbaseVerificationAdapter(
        client=CrossedClient(),
    )

    result = adapter.fetch_order_book(
        "BTC/USD"
    )

    assert result["verified"] is False


def test_empty_book_fails_closed():
    class EmptyClient(FakeClient):
        def fetch_order_book(
            self,
            product_id,
            level=2,
        ):
            return {
                "sequence": 1,
                "bids": [],
                "asks": [],
            }

    adapter = CoinbaseVerificationAdapter(
        client=EmptyClient(),
    )

    result = adapter.fetch_order_book(
        "BTC/USD"
    )

    assert result["verified"] is False


def test_fetch_failure_fails_closed():
    class FailedClient:
        def fetch_order_book(
            self,
            product_id,
            level=2,
        ):
            raise RuntimeError(
                "book unavailable"
            )

        def fetch_ticker(
            self,
            product_id,
        ):
            raise RuntimeError(
                "ticker unavailable"
            )

    adapter = CoinbaseVerificationAdapter(
        client=FailedClient(),
    )

    result = adapter.fetch_order_book(
        "BTC/USD"
    )

    assert result[
        "verification_available"
    ] is False

    assert result["verified"] is False


def test_paper_safe_flags_are_preserved():
    adapter = CoinbaseVerificationAdapter(
        client=FakeClient(),
    )

    result = adapter.fetch_order_book(
        "BTC/USD"
    )

    assert result["paper_only"] is True

    assert result[
        "live_order_submitted"
    ] is False
