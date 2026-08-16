import pytest

from exchanges.coinex_verification_adapter import (
    CoinExVerificationAdapter,
)


class FakeClient:
    def fetch_order_book(
        self,
        symbol,
        limit=20,
    ):
        return {
            "code": 0,
            "data": {
                "depth": {
                    "asks": [
                        ["63044", "0.03977209"],
                        ["63045", "0.00158618"],
                    ],
                    "bids": [
                        ["63043", "0.80432751"],
                        ["63042", "0.10088271"],
                    ],
                    "checksum": 2639840070,
                    "last": "63043",
                    "updated_at": 1786843279189,
                },
                "is_full": True,
                "market": "BTCUSDT",
            },
            "message": "OK",
        }


class FailedClient:
    def fetch_order_book(
        self,
        symbol,
        limit=20,
    ):
        return {
            "code": 1,
            "data": None,
            "message": "FAILED",
        }


def test_client_is_required():
    with pytest.raises(
        ValueError,
        match="client is required",
    ):
        CoinExVerificationAdapter(
            client=None,
        )


def test_fetches_verified_order_book():
    adapter = CoinExVerificationAdapter(
        client=FakeClient(),
    )

    result = adapter.fetch_order_book(
        "BTC/USDT",
        limit=20,
    )

    assert result[
        "verification_available"
    ] is True

    assert result[
        "verified"
    ] is True

    assert result[
        "best_bid"
    ] == 63043.0

    assert result[
        "best_ask"
    ] == 63044.0


def test_levels_are_normalized_to_floats():
    adapter = CoinExVerificationAdapter(
        client=FakeClient(),
    )

    result = adapter.fetch_order_book(
        "BTC/USDT"
    )

    assert result[
        "bids"
    ][0] == [
        63043.0,
        0.80432751,
    ]

    assert result[
        "asks"
    ][0] == [
        63044.0,
        0.03977209,
    ]


def test_updated_at_is_preserved():
    adapter = CoinExVerificationAdapter(
        client=FakeClient(),
    )

    result = adapter.fetch_order_book(
        "BTC/USDT"
    )

    assert result[
        "bid_timestamps"
    ][0] == 1786843279189

    assert result[
        "ask_timestamps"
    ][0] == 1786843279189


def test_failed_fetch_fails_closed():
    adapter = CoinExVerificationAdapter(
        client=FailedClient(),
    )

    result = adapter.fetch_order_book(
        "BTC/USDT"
    )

    assert result[
        "verification_available"
    ] is False

    assert result[
        "verified"
    ] is False

    assert result[
        "bids"
    ] == []

    assert result[
        "asks"
    ] == []

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False
