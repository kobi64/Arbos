import pytest

from exchanges.okx_verification_adapter import (
    OKXVerificationAdapter,
)


class FakeClient:
    def fetch_order_book(
        self,
        symbol,
        limit=20,
    ):
        return {
            "code": "0",
            "msg": "",
            "data": [
                {
                    "asks": [
                        [
                            "63053.1",
                            "1.72838554",
                            "0",
                            "25",
                        ],
                    ],
                    "bids": [
                        [
                            "63053",
                            "0.61001039",
                            "0",
                            "9",
                        ],
                    ],
                    "ts": "1786859533954",
                    "seqId": 79790738998,
                }
            ],
        }


class FailedClient:
    def fetch_order_book(
        self,
        symbol,
        limit=20,
    ):
        raise RuntimeError(
            "OKX book unavailable"
        )


def test_client_is_required():
    with pytest.raises(
        ValueError,
        match="client is required",
    ):
        OKXVerificationAdapter(
            client=None,
        )


def test_normalizes_okx_order_book():
    adapter = OKXVerificationAdapter(
        client=FakeClient(),
    )

    result = adapter.fetch_order_book(
        "BTC/USDT"
    )

    assert result[
        "verification_available"
    ] is True

    assert result["verified"] is True

    assert result["best_bid"] == 63053.0
    assert result["best_ask"] == 63053.1

    assert result["bids"] == [
        [
            63053.0,
            0.61001039,
        ]
    ]

    assert result["asks"] == [
        [
            63053.1,
            1.72838554,
        ]
    ]


def test_timestamp_is_preserved():
    adapter = OKXVerificationAdapter(
        client=FakeClient(),
    )

    result = adapter.fetch_order_book(
        "BTC/USDT"
    )

    assert result[
        "bid_timestamps"
    ] == [
        1786859533954
    ]

    assert result[
        "ask_timestamps"
    ] == [
        1786859533954
    ]


def test_native_symbol_is_normalized():
    adapter = OKXVerificationAdapter(
        client=FakeClient(),
    )

    result = adapter.fetch_order_book(
        " btc/usdt "
    )

    assert result[
        "native_symbol"
    ] == "BTC-USDT"


def test_exchange_error_fails_closed():
    class ErrorClient:
        def fetch_order_book(
            self,
            symbol,
            limit=20,
        ):
            return {
                "code": "50000",
                "msg": "error",
                "data": [],
            }

    adapter = OKXVerificationAdapter(
        client=ErrorClient(),
    )

    result = adapter.fetch_order_book(
        "BTC/USDT"
    )

    assert result[
        "verification_available"
    ] is False

    assert result["verified"] is False
    assert result["bids"] == []
    assert result["asks"] == []


def test_failed_fetch_fails_closed():
    adapter = OKXVerificationAdapter(
        client=FailedClient(),
    )

    result = adapter.fetch_order_book(
        "BTC/USDT"
    )

    assert result[
        "verification_available"
    ] is False

    assert result["verified"] is False


def test_crossed_book_fails_closed():
    class CrossedClient:
        def fetch_order_book(
            self,
            symbol,
            limit=20,
        ):
            return {
                "code": "0",
                "data": [
                    {
                        "asks": [
                            [
                                "63000",
                                "1",
                                "0",
                                "1",
                            ],
                        ],
                        "bids": [
                            [
                                "63100",
                                "1",
                                "0",
                                "1",
                            ],
                        ],
                        "ts": "1",
                    }
                ],
            }

    adapter = OKXVerificationAdapter(
        client=CrossedClient(),
    )

    result = adapter.fetch_order_book(
        "BTC/USDT"
    )

    assert result["verified"] is False

    assert result[
        "verification_available"
    ] is False


def test_empty_book_fails_closed():
    class EmptyClient:
        def fetch_order_book(
            self,
            symbol,
            limit=20,
        ):
            return {
                "code": "0",
                "data": [
                    {
                        "asks": [],
                        "bids": [],
                        "ts": "1",
                    }
                ],
            }

    adapter = OKXVerificationAdapter(
        client=EmptyClient(),
    )

    result = adapter.fetch_order_book(
        "BTC/USDT"
    )

    assert result["verified"] is False


def test_paper_safe_flags_are_preserved():
    adapter = OKXVerificationAdapter(
        client=FakeClient(),
    )

    result = adapter.fetch_order_book(
        "BTC/USDT"
    )

    assert result["paper_only"] is True

    assert result[
        "live_order_submitted"
    ] is False
