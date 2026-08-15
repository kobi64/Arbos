import pytest

from exchanges.bingx_verification_adapter import (
    BingXVerificationAdapter,
)


class FakeClient:
    def fetch_order_book(
        self,
        symbol,
        limit=20,
    ):
        return {
            "fetch_complete": True,
            "symbol": "BTC-USDT",
            "bids": [
                ["63000.00", "1.25"],
                ["62999.00", "2.00"],
            ],
            "asks": [
                ["63001.00", "1.50"],
                ["63002.00", "2.50"],
            ],
            "timestamp": 1700000000000,
            "last_update_id": 12345,
            "reason": None,
            "paper_only": True,
            "live_order_submitted": False,
        }


class FailedClient:
    def fetch_order_book(
        self,
        symbol,
        limit=20,
    ):
        return {
            "fetch_complete": False,
            "symbol": "BTC-USDT",
            "bids": [],
            "asks": [],
            "timestamp": None,
            "last_update_id": None,
            "reason": "exchange_error",
            "paper_only": True,
            "live_order_submitted": False,
        }


def test_client_is_required():
    with pytest.raises(
        ValueError,
        match="client is required",
    ):
        BingXVerificationAdapter(
            client=None,
        )


def test_fetches_verified_order_book():
    adapter = BingXVerificationAdapter(
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
    ] == 63000.0

    assert result[
        "best_ask"
    ] == 63001.0

    assert len(
        result["bids"]
    ) == 2

    assert len(
        result["asks"]
    ) == 2

    assert result[
        "timestamp"
    ] == 1700000000000


def test_levels_are_normalized_to_floats():
    adapter = BingXVerificationAdapter(
        client=FakeClient(),
    )

    result = adapter.fetch_order_book(
        "BTC/USDT"
    )

    assert result["bids"][0] == [
        63000.0,
        1.25,
    ]

    assert result["asks"][0] == [
        63001.0,
        1.5,
    ]


def test_failed_fetch_fails_closed():
    adapter = BingXVerificationAdapter(
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
