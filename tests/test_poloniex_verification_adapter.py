import pytest

from exchanges.poloniex_verification_adapter import (
    PoloniexVerificationAdapter,
)


def test_normalizes_flat_order_book():
    adapter = PoloniexVerificationAdapter()

    result = adapter.normalize_order_book({
        "fetch_complete": True,
        "symbol": "FIR_USDT",
        "bids": [
            "0.100",
            "75",
            "0.099",
            "125",
        ],
        "asks": [
            "0.101",
            "50",
            "0.102",
            "100",
        ],
    })

    assert result["available"] is True
    assert result["symbol"] == "FIR_USDT"

    assert result["best_bid"] == 0.100
    assert result["best_ask"] == 0.101

    assert result["bids"] == [
        {
            "price": 0.100,
            "quantity": 75.0,
        },
        {
            "price": 0.099,
            "quantity": 125.0,
        },
    ]

    assert result["asks"] == [
        {
            "price": 0.101,
            "quantity": 50.0,
        },
        {
            "price": 0.102,
            "quantity": 100.0,
        },
    ]

    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False


def test_unavailable_order_book_fails_closed():
    adapter = PoloniexVerificationAdapter()

    result = adapter.normalize_order_book({
        "fetch_complete": False,
        "symbol": "FIR_USDT",
        "bids": [],
        "asks": [],
        "reason": "HTTP failure",
    })

    assert result["available"] is False
    assert result["reason"] == "HTTP failure"
    assert result["bids"] == []
    assert result["asks"] == []
    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False


def test_odd_flat_depth_is_rejected():
    adapter = PoloniexVerificationAdapter()

    with pytest.raises(
        ValueError,
        match="depth must contain price/quantity pairs",
    ):
        adapter.normalize_order_book({
            "fetch_complete": True,
            "symbol": "BTC_USDT",
            "bids": [
                "1",
                "2",
                "3",
            ],
            "asks": [
                "4",
                "5",
            ],
        })


def test_non_positive_depth_values_are_rejected():
    adapter = PoloniexVerificationAdapter()

    with pytest.raises(
        ValueError,
        match="price and quantity must be positive",
    ):
        adapter.normalize_order_book({
            "fetch_complete": True,
            "symbol": "BTC_USDT",
            "bids": [
                "1",
                "0",
            ],
            "asks": [
                "2",
                "3",
            ],
        })
