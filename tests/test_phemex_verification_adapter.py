import pytest

from exchanges.phemex_verification_adapter import (
    PhemexVerificationAdapter,
)


class FakeClient:
    def fetch_order_book(
        self,
        symbol,
        limit=30,
    ):
        return {
            "error": None,
            "id": 0,
            "result": {
                "book": {
                    "asks": [
                        [
                            6305469000000,
                            5966600,
                        ],
                    ],
                    "bids": [
                        [
                            6305468000000,
                            4264100,
                        ],
                    ],
                },
                "depth": 30,
                "sequence": 40398521651,
                "symbol": "sBTCUSDT",
                "timestamp": (
                    1786845356093279821
                ),
                "type": "snapshot",
            },
        }


class FailedClient:
    def fetch_order_book(
        self,
        symbol,
        limit=30,
    ):
        raise RuntimeError(
            "spot book unavailable"
        )


def test_client_is_required():
    with pytest.raises(
        ValueError,
        match="client is required",
    ):
        PhemexVerificationAdapter(
            client=None,
            price_scale=8,
            quantity_scale=8,
        )


def test_scale_must_be_non_negative():
    with pytest.raises(
        ValueError,
        match="price_scale must be non-negative",
    ):
        PhemexVerificationAdapter(
            client=FakeClient(),
            price_scale=-1,
            quantity_scale=8,
        )


def test_normalizes_scaled_phemex_levels():
    adapter = PhemexVerificationAdapter(
        client=FakeClient(),
        price_scale=8,
        quantity_scale=8,
    )

    result = adapter.fetch_order_book(
        "BTC/USDT"
    )

    assert result[
        "verification_available"
    ] is True

    assert result["verified"] is True

    assert result["best_bid"] == (
        63054.68
    )

    assert result["best_ask"] == (
        63054.69
    )

    assert result["bids"] == [
        [
            63054.68,
            0.042641,
        ]
    ]

    assert result["asks"] == [
        [
            63054.69,
            0.059666,
        ]
    ]


def test_timestamp_is_preserved():
    adapter = PhemexVerificationAdapter(
        client=FakeClient(),
        price_scale=8,
        quantity_scale=8,
    )

    result = adapter.fetch_order_book(
        "BTC/USDT"
    )

    assert result[
        "bid_timestamps"
    ] == [
        1786845356093279821
    ]

    assert result[
        "ask_timestamps"
    ] == [
        1786845356093279821
    ]


def test_native_spot_symbol_is_preserved():
    adapter = PhemexVerificationAdapter(
        client=FakeClient(),
        price_scale=8,
        quantity_scale=8,
    )

    result = adapter.fetch_order_book(
        "BTC/USDT"
    )

    assert result[
        "native_symbol"
    ] == "sBTCUSDT"


def test_failed_fetch_fails_closed():
    adapter = PhemexVerificationAdapter(
        client=FailedClient(),
        price_scale=8,
        quantity_scale=8,
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


def test_crossed_book_fails_closed():
    class CrossedClient:
        def fetch_order_book(
            self,
            symbol,
            limit=30,
        ):
            return {
                "error": None,
                "result": {
                    "book": {
                        "asks": [
                            [
                                6300000000000,
                                100000000,
                            ],
                        ],
                        "bids": [
                            [
                                6310000000000,
                                100000000,
                            ],
                        ],
                    },
                    "symbol": "sBTCUSDT",
                    "timestamp": 1,
                },
            }

    adapter = PhemexVerificationAdapter(
        client=CrossedClient(),
        price_scale=8,
        quantity_scale=8,
    )

    result = adapter.fetch_order_book(
        "BTC/USDT"
    )

    assert result["verified"] is False
    assert result[
        "verification_available"
    ] is False


def test_paper_safe_flags_are_preserved():
    adapter = PhemexVerificationAdapter(
        client=FakeClient(),
        price_scale=8,
        quantity_scale=8,
    )

    result = adapter.fetch_order_book(
        "BTC/USDT"
    )

    assert result["paper_only"] is True
    assert result[
        "live_order_submitted"
    ] is False


def test_uses_market_specific_scale_resolver():
    class Resolver:
        def resolve(
            self,
            symbol,
        ):
            assert symbol == "ABC/USDT"

            return {
                "native_symbol": "sABCUSDT",
                "price_scale": 5,
                "quantity_scale": 6,
            }

    class Client:
        def fetch_order_book(
            self,
            symbol,
            limit=30,
        ):
            return {
                "error": None,
                "result": {
                    "book": {
                        "asks": [
                            [
                                123460,
                                2500000,
                            ],
                        ],
                        "bids": [
                            [
                                123450,
                                1500000,
                            ],
                        ],
                    },
                    "symbol": "sABCUSDT",
                    "timestamp": 123,
                },
            }

    adapter = PhemexVerificationAdapter(
        client=Client(),
        scale_resolver=Resolver(),
    )

    result = adapter.fetch_order_book(
        "ABC/USDT"
    )

    assert result["verified"] is True
    assert result["best_bid"] == 1.2345
    assert result["best_ask"] == 1.2346

    assert result["bids"] == [
        [
            1.2345,
            1.5,
        ]
    ]

    assert result["asks"] == [
        [
            1.2346,
            2.5,
        ]
    ]


def test_scale_resolver_failure_fails_closed():
    class Resolver:
        def resolve(
            self,
            symbol,
        ):
            raise RuntimeError(
                "Phemex spot scale unavailable"
            )

    adapter = PhemexVerificationAdapter(
        client=FakeClient(),
        scale_resolver=Resolver(),
    )

    result = adapter.fetch_order_book(
        "UNKNOWN/USDT"
    )

    assert result["verified"] is False
    assert result[
        "verification_available"
    ] is False


def test_requires_scales_or_resolver():
    with pytest.raises(
        ValueError,
        match=(
            "scales or scale_resolver "
            "are required"
        ),
    ):
        PhemexVerificationAdapter(
            client=FakeClient(),
        )
