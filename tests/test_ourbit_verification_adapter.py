from exchanges.ourbit_verification_adapter import (
    OurbitVerificationAdapter,
)


def test_normalizes_order_book():
    adapter = OurbitVerificationAdapter()

    result = adapter.normalize_order_book({
        "fetch_complete": True,
        "symbol": "BTCUSDT",
        "bids": [
            ["62895.79", "6.319350"],
            ["62895.71", "2.216495"],
        ],
        "asks": [
            ["62895.80", "4.504951"],
            ["62895.87", "2.284189"],
        ],
        "timestamp": 1700000000000,
        "paper_only": True,
        "live_order_submitted": False,
    })

    assert result[
        "available"
    ] is True

    assert result[
        "symbol"
    ] == "BTCUSDT"

    assert result[
        "best_bid"
    ] == 62895.79

    assert result[
        "best_ask"
    ] == 62895.80

    assert result[
        "bids"
    ][0] == {
        "price": 62895.79,
        "quantity": 6.319350,
    }

    assert result[
        "asks"
    ][0] == {
        "price": 62895.80,
        "quantity": 4.504951,
    }


def test_preserves_timestamp():
    adapter = OurbitVerificationAdapter()

    result = adapter.normalize_order_book({
        "fetch_complete": True,
        "symbol": "BTCUSDT",
        "bids": [["1", "2"]],
        "asks": [["2", "3"]],
        "timestamp": 1700000000000,
    })

    assert result[
        "timestamp"
    ] == 1700000000000


def test_failed_fetch_is_unavailable():
    adapter = OurbitVerificationAdapter()

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


def test_empty_book_is_unavailable():
    adapter = OurbitVerificationAdapter()

    result = adapter.normalize_order_book({
        "fetch_complete": True,
        "symbol": "BTCUSDT",
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
    adapter = OurbitVerificationAdapter()

    result = adapter.normalize_order_book({
        "fetch_complete": True,
        "symbol": "BTCUSDT",
        "bids": [["bad", "1"]],
        "asks": [["2", "1"]],
    })

    assert result[
        "available"
    ] is False


def test_adapter_is_paper_safe():
    adapter = OurbitVerificationAdapter()

    result = adapter.normalize_order_book({
        "fetch_complete": True,
        "symbol": "BTCUSDT",
        "bids": [["1", "2"]],
        "asks": [["2", "3"]],
    })

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False
