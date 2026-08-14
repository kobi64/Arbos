import pytest

from exchanges.mexc_verification_adapter import (
    MexcVerificationAdapter,
)


def test_normalizes_order_book():
    adapter = MexcVerificationAdapter()

    result = adapter.normalize_order_book({
        "fetch_complete": True,
        "symbol": "BTCUSDT",
        "bids": [
            ["15.00000", "49999.00000"],
            ["14.90000", "25000.00000"],
        ],
        "asks": [
            ["15.10000", "100.00000"],
            ["15.20000", "200.00000"],
        ],
    })

    assert result[
        "available"
    ] is True

    assert result[
        "symbol"
    ] == "BTCUSDT"

    assert result[
        "best_bid"
    ] == 15.0

    assert result[
        "best_ask"
    ] == 15.1

    assert result[
        "bids"
    ] == [
        {
            "price": 15.0,
            "quantity": 49999.0,
        },
        {
            "price": 14.9,
            "quantity": 25000.0,
        },
    ]

    assert result[
        "asks"
    ] == [
        {
            "price": 15.1,
            "quantity": 100.0,
        },
        {
            "price": 15.2,
            "quantity": 200.0,
        },
    ]

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False


def test_unavailable_order_book_fails_closed():
    adapter = MexcVerificationAdapter()

    result = adapter.normalize_order_book({
        "fetch_complete": False,
        "symbol": "BTCUSDT",
        "bids": [],
        "asks": [],
        "reason": "request_failed",
    })

    assert result[
        "available"
    ] is False

    assert result[
        "reason"
    ] == "request_failed"

    assert result[
        "bids"
    ] == []

    assert result[
        "asks"
    ] == []


def test_invalid_level_is_rejected():
    adapter = MexcVerificationAdapter()

    with pytest.raises(
        ValueError,
        match="order book level must contain price and quantity",
    ):
        adapter.normalize_order_book({
            "fetch_complete": True,
            "symbol": "BTCUSDT",
            "bids": [
                ["15.0"],
            ],
            "asks": [
                ["15.1", "100"],
            ],
        })


def test_non_positive_values_are_rejected():
    adapter = MexcVerificationAdapter()

    with pytest.raises(
        ValueError,
        match="price and quantity must be positive",
    ):
        adapter.normalize_order_book({
            "fetch_complete": True,
            "symbol": "BTCUSDT",
            "bids": [
                ["15.0", "0"],
            ],
            "asks": [
                ["15.1", "100"],
            ],
        })
