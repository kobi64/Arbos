import pytest

from core.public_live_multi_path_input_preparer import (
    PublicLiveMultiPathInputPreparer,
)


class FakeExchange:
    def __init__(self, destination=False):
        self.destination = destination

    def load_markets(self):
        return {
            "COINX/USDT": {
                "spot": True,
                "active": True,
            },
            "COINX/BTC": {
                "spot": True,
                "active": True,
            },
            "BTC/USDT": {
                "spot": True,
                "active": True,
            },
        }

    def load_currencies(self):
        return {
            "COINX": {
                "code": "COINX",
                "deposit": True,
                "withdraw": True,
                "networks": {
                    "ARBITRUM": {
                        "deposit": True,
                        "withdraw": True,
                        "fee": 1.0,
                    },
                },
            },
            "BTC": {
                "code": "BTC",
                "deposit": True,
                "withdraw": True,
                "networks": {
                    "BTC": {
                        "deposit": True,
                        "withdraw": True,
                        "fee": 0.0001,
                    },
                },
            },
        }

    def fetch_order_book(self, symbol, limit=None):
        books = {
            "COINX/USDT": {
                "bids": [[0.99, 10000.0]],
                "asks": [[1.00, 10000.0]],
            },
            "COINX/BTC": {
                "bids": [[0.00002, 10000.0]],
                "asks": [[0.000021, 10000.0]],
            },
            "BTC/USDT": {
                "bids": [[50000.0, 10.0]],
                "asks": [[50010.0, 10.0]],
            },
        }

        result = dict(books[symbol])
        result["symbol"] = symbol
        result["timestamp"] = None
        result["datetime"] = None
        return result


def test_prepares_real_cross_exchange_inputs():
    preparer = PublicLiveMultiPathInputPreparer(
        source_exchange=FakeExchange(),
        destination_exchange=FakeExchange(destination=True),
    )

    result = preparer.prepare(
        source_exchange_id="source",
        destination_exchange_id="destination",
        coin_asset="COINX",
        starting_usdt_value=100.0,
        source_fee_rate=0.001,
    )

    assert result["coin_asset"] == "COINX"
    assert result["coin_amount"] == pytest.approx(99.9)

    assert "COINX" in result["source_networks"]
    assert "COINX" in result["destination_networks"]

    assert "BTC" in result["source_networks"]
    assert "BTC" in result["destination_networks"]

    assert result["bridge_quotes"]["BTC"]["method"] == "spot"
    assert (
        result["bridge_quotes"]["BTC"]["output_amount"]
        == pytest.approx(0.001996002)
    )


def test_prepares_network_identity_records():
    preparer = PublicLiveMultiPathInputPreparer(
        source_exchange=FakeExchange(),
        destination_exchange=FakeExchange(
            destination=True
        ),
    )

    result = preparer.prepare(
        source_exchange_id="source",
        destination_exchange_id="destination",
        coin_asset="COINX",
        starting_usdt_value=100.0,
        source_fee_rate=0.001,
    )

    assert (
        "COINX"
        in result[
            "source_network_identity_records"
        ]
    )

    assert (
        "COINX"
        in result[
            "destination_network_identity_records"
        ]
    )

    assert (
        "BTC"
        in result[
            "source_network_identity_records"
        ]
    )

    assert (
        "BTC"
        in result[
            "destination_network_identity_records"
        ]
    )


class FakeSourceBuyQuote:
    def __init__(self):
        self.calls = []

    def quote(
        self,
        coin_asset,
        starting_usdt_value,
        source_fee_rate,
        max_slippage_percent,
    ):
        self.calls.append({
            "coin_asset": coin_asset,
            "starting_usdt_value": (
                starting_usdt_value
            ),
            "source_fee_rate": (
                source_fee_rate
            ),
            "max_slippage_percent": (
                max_slippage_percent
            ),
        })

        return {
            "filled": True,
            "coin_asset": coin_asset,
            "coin_amount": 98.5,
            "starting_usdt_value": (
                starting_usdt_value
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }


def test_uses_depth_aware_source_buy_when_supplied():
    source_buy = FakeSourceBuyQuote()

    preparer = PublicLiveMultiPathInputPreparer(
        source_exchange=FakeExchange(),
        destination_exchange=FakeExchange(
            destination=True
        ),
        source_buy_quote=source_buy,
    )

    result = preparer.prepare(
        source_exchange_id="source",
        destination_exchange_id="destination",
        coin_asset="COINX",
        starting_usdt_value=100.0,
        source_fee_rate=0.001,
        max_slippage_percent=0.5,
    )

    assert result["coin_amount"] == 98.5

    assert source_buy.calls == [
        {
            "coin_asset": "COINX",
            "starting_usdt_value": 100.0,
            "source_fee_rate": 0.001,
            "max_slippage_percent": 0.5,
        },
    ]

    assert result[
        "source_buy_depth_aware"
    ] is True

    assert result[
        "source_buy_result"
    ]["filled"] is True


class RejectedSourceBuyQuote:
    def quote(
        self,
        coin_asset,
        starting_usdt_value,
        source_fee_rate,
        max_slippage_percent,
    ):
        return {
            "filled": False,
            "reason": "slippage_exceeded",
            "coin_asset": coin_asset,
            "coin_amount": 0.0,
            "paper_only": True,
            "live_order_submitted": False,
        }


def test_rejected_depth_aware_source_buy_stops_preparation():
    preparer = PublicLiveMultiPathInputPreparer(
        source_exchange=FakeExchange(),
        destination_exchange=FakeExchange(
            destination=True
        ),
        source_buy_quote=RejectedSourceBuyQuote(),
    )

    result = preparer.prepare(
        source_exchange_id="source",
        destination_exchange_id="destination",
        coin_asset="COINX",
        starting_usdt_value=100.0,
        source_fee_rate=0.001,
        max_slippage_percent=0.5,
    )

    assert result[
        "prepare_complete"
    ] is False

    assert result[
        "reason"
    ] == "source_buy_slippage_exceeded"

    assert result["coin_amount"] == 0.0

    assert result[
        "source_buy_result"
    ]["filled"] is False

    assert result[
        "live_order_submitted"
    ] is False


def test_legacy_best_ask_source_buy_remains_supported():
    preparer = PublicLiveMultiPathInputPreparer(
        source_exchange=FakeExchange(),
        destination_exchange=FakeExchange(
            destination=True
        ),
    )

    result = preparer.prepare(
        source_exchange_id="source",
        destination_exchange_id="destination",
        coin_asset="COINX",
        starting_usdt_value=100.0,
        source_fee_rate=0.001,
    )

    assert result["coin_amount"] == pytest.approx(
        99.9
    )

    assert result.get(
        "source_buy_depth_aware",
        False,
    ) is False
