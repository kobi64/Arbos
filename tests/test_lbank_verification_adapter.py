from exchanges.lbank_verification_adapter import (
    LBankVerificationAdapter,
)


def test_normalizes_order_book():
    adapter = LBankVerificationAdapter()

    result = adapter.normalize_order_book({
        "fetch_complete": True,
        "symbol": "btc_usdt",
        "bids": [
            ["63144.62", "5.64875"],
            ["63144.61", "0.00547"],
        ],
        "asks": [
            ["63144.63", "2.04678"],
            ["63144.64", "0.00181"],
        ],
        "timestamp": 1700000000000,
    })

    assert result[
        "available"
    ] is True

    assert result[
        "symbol"
    ] == "btc_usdt"

    assert result[
        "best_bid"
    ] == 63144.62

    assert result[
        "best_ask"
    ] == 63144.63

    assert result[
        "bids"
    ][0] == {
        "price": 63144.62,
        "quantity": 5.64875,
    }

    assert result[
        "asks"
    ][0] == {
        "price": 63144.63,
        "quantity": 2.04678,
    }


def test_preserves_timestamp():
    adapter = LBankVerificationAdapter()

    result = adapter.normalize_order_book({
        "fetch_complete": True,
        "symbol": "btc_usdt",
        "bids": [["1", "2"]],
        "asks": [["2", "3"]],
        "timestamp": 1700000000000,
    })

    assert result[
        "timestamp"
    ] == 1700000000000


def test_failed_fetch_is_unavailable():
    adapter = LBankVerificationAdapter()

    result = adapter.normalize_order_book({
        "fetch_complete": False,
        "symbol": "btc_usdt",
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


def test_empty_book_is_unavailable():
    adapter = LBankVerificationAdapter()

    result = adapter.normalize_order_book({
        "fetch_complete": True,
        "symbol": "btc_usdt",
        "bids": [],
        "asks": [],
    })

    assert result[
        "available"
    ] is False

    assert result[
        "reason"
    ] == "empty_order_book"


def test_invalid_level_is_unavailable():
    adapter = LBankVerificationAdapter()

    result = adapter.normalize_order_book({
        "fetch_complete": True,
        "symbol": "btc_usdt",
        "bids": [["bad", "1"]],
        "asks": [["2", "1"]],
    })

    assert result[
        "available"
    ] is False


def test_adapter_is_paper_safe():
    adapter = LBankVerificationAdapter()

    result = adapter.normalize_order_book({
        "fetch_complete": True,
        "symbol": "btc_usdt",
        "bids": [["1", "2"]],
        "asks": [["2", "3"]],
    })

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False
