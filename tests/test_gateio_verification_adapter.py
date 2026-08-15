import pytest

from exchanges.gateio_verification_adapter import (
    GateIOVerificationAdapter,
)


class FakeClient:
    def fetch_order_book(
        self,
        symbol,
        limit=20,
    ):
        return {
            "fetch_complete": True,
            "symbol": "BTC_USDT",
            "bids": [
                ["63038.5", "0.047"],
                ["63038.4", "0.107"],
            ],
            "asks": [
                ["63039.0", "0.070"],
                ["63044.5", "0.427"],
            ],
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
            "symbol": "BTC_USDT",
            "bids": [],
            "asks": [],
            "reason": "exchange_error",
            "paper_only": True,
            "live_order_submitted": False,
        }


def test_client_is_required():
    with pytest.raises(
        ValueError,
        match="client is required",
    ):
        GateIOVerificationAdapter(
            client=None,
        )


def test_fetches_verified_order_book():
    adapter = GateIOVerificationAdapter(
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
    ] == 63038.5

    assert result[
        "best_ask"
    ] == 63039.0

    assert len(
        result["bids"]
    ) == 2

    assert len(
        result["asks"]
    ) == 2


def test_levels_are_normalized_to_floats():
    adapter = GateIOVerificationAdapter(
        client=FakeClient(),
    )

    result = adapter.fetch_order_book(
        "BTC/USDT"
    )

    assert result[
        "bids"
    ][0] == [
        63038.5,
        0.047,
    ]

    assert result[
        "asks"
    ][0] == [
        63039.0,
        0.070,
    ]


def test_gateio_levels_without_timestamps_are_preserved_as_none():
    adapter = GateIOVerificationAdapter(
        client=FakeClient(),
    )

    result = adapter.fetch_order_book(
        "BTC/USDT"
    )

    assert result[
        "bid_timestamps"
    ][0] is None

    assert result[
        "ask_timestamps"
    ][0] is None


def test_failed_fetch_fails_closed():
    adapter = GateIOVerificationAdapter(
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
