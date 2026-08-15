import pytest

from exchanges.xt_verification_adapter import (
    XTVerificationAdapter,
)


class FakeClient:
    def fetch_order_book(
        self,
        symbol,
        limit=20,
    ):
        return {
            "rc": 0,
            "mc": "SUCCESS",
            "result": {
                "symbol": "btc_usdt",
                "timestamp": 1700000000000,
                "lastUpdateId": 12345,
                "bids": [
                    ["63094.99", "23.31624"],
                    ["63094.97", "0.35580"],
                ],
                "asks": [
                    ["63095.00", "12.14463"],
                    ["63095.09", "0.43631"],
                ],
            },
        }


class FailedClient:
    def fetch_order_book(
        self,
        symbol,
        limit=20,
    ):
        return {
            "rc": 1,
            "mc": "FAILED",
            "result": None,
        }


def test_client_is_required():
    with pytest.raises(
        ValueError,
        match="client is required",
    ):
        XTVerificationAdapter(
            client=None,
        )


def test_fetches_verified_order_book():
    adapter = XTVerificationAdapter(
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
    ] == 63094.99

    assert result[
        "best_ask"
    ] == 63095.00


def test_levels_are_normalized_to_floats():
    adapter = XTVerificationAdapter(
        client=FakeClient(),
    )

    result = adapter.fetch_order_book(
        "BTC/USDT"
    )

    assert result[
        "bids"
    ][0] == [
        63094.99,
        23.31624,
    ]

    assert result[
        "asks"
    ][0] == [
        63095.00,
        12.14463,
    ]


def test_snapshot_timestamp_is_preserved():
    adapter = XTVerificationAdapter(
        client=FakeClient(),
    )

    result = adapter.fetch_order_book(
        "BTC/USDT"
    )

    assert result[
        "bid_timestamps"
    ][0] == 1700000000000

    assert result[
        "ask_timestamps"
    ][0] == 1700000000000


def test_failed_fetch_fails_closed():
    adapter = XTVerificationAdapter(
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
