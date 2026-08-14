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


def test_weex_source_uses_network_metadata_factory():
    from exchanges.network_metadata_adapter_factory import (
        NetworkMetadataAdapterFactory,
    )

    class FakeNetworkAdapter:
        def __init__(self):
            self.calls = []

        def get_networks(self, coin):
            self.calls.append(coin)
            return []

    source_adapter = FakeNetworkAdapter()
    destination_adapter = FakeNetworkAdapter()

    class FakeFactory:
        def __init__(self):
            self.calls = []

        def build(self, exchange):
            self.calls.append(exchange)

            if getattr(exchange, "id", "") == "weex":
                return source_adapter

            return destination_adapter

    factory = FakeFactory()

    source_exchange = type(
        "WeexExchange",
        (),
        {"id": "weex"},
    )()

    destination_exchange = type(
        "KuCoinExchange",
        (),
        {"id": "kucoin"},
    )()

    preparer = PublicLiveMultiPathInputPreparer(
        source_exchange=source_exchange,
        destination_exchange=destination_exchange,
        network_metadata_adapter_factory=factory,
    )

    assert preparer._network_metadata_adapter_factory is factory


def test_network_metadata_factory_defaults_when_not_supplied():
    preparer = PublicLiveMultiPathInputPreparer(
        source_exchange=object(),
        destination_exchange=object(),
    )

    assert (
        preparer._network_metadata_adapter_factory
        is not None
    )






def test_preparer_preserves_network_metadata_status():
    class MetadataAwareAdapter:
        def __init__(
            self,
            available,
            reason=None,
        ):
            self.available = available
            self.reason = reason

        def get_networks(
            self,
            coin,
        ):
            return []

        def describe_networks(
            self,
            coin,
        ):
            return {
                "coin": coin,
                "available": True,
                "network_metadata_available": (
                    self.available
                ),
                "network_metadata_reason": (
                    self.reason
                ),
                "transfer_verification_available": (
                    self.available
                ),
                "networks": [],
                "paper_only": True,
                "live_order_submitted": False,
            }

    source_adapter = MetadataAwareAdapter(
        available=False,
        reason="empty_network_list",
    )

    destination_adapter = MetadataAwareAdapter(
        available=True,
    )

    class FakeFactory:
        def build(
            self,
            exchange,
        ):
            if getattr(
                exchange,
                "destination",
                False,
            ):
                return destination_adapter

            return source_adapter

    source_exchange = FakeExchange()
    destination_exchange = FakeExchange(
        destination=True
    )

    preparer = PublicLiveMultiPathInputPreparer(
        source_exchange=source_exchange,
        destination_exchange=destination_exchange,
        network_metadata_adapter_factory=(
            FakeFactory()
        ),
    )

    result = preparer.prepare(
        source_exchange_id="weex",
        destination_exchange_id="gateio",
        coin_asset="COINX",
        starting_usdt_value=100.0,
        source_fee_rate=0.001,
    )

    source_status = result[
        "source_network_metadata"
    ]["COINX"]

    destination_status = result[
        "destination_network_metadata"
    ]["COINX"]

    assert source_status[
        "network_metadata_available"
    ] is False

    assert source_status[
        "network_metadata_reason"
    ] == "empty_network_list"

    assert source_status[
        "transfer_verification_available"
    ] is False

    assert destination_status[
        "network_metadata_available"
    ] is True


def test_legacy_network_adapter_gets_safe_metadata_status():
    class LegacyAdapter:
        def get_networks(
            self,
            coin,
        ):
            return []

    class LegacyFactory:
        def build(
            self,
            exchange,
        ):
            return LegacyAdapter()

    preparer = PublicLiveMultiPathInputPreparer(
        source_exchange=FakeExchange(),
        destination_exchange=FakeExchange(
            destination=True
        ),
        network_metadata_adapter_factory=(
            LegacyFactory()
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
        result[
            "source_network_metadata"
        ]["COINX"][
            "transfer_verification_available"
        ]
        is False
    )

    assert (
        result[
            "source_network_metadata"
        ]["COINX"][
            "network_metadata_reason"
        ]
        == "network_metadata_unavailable"
    )


def test_poloniex_uses_network_identity_metadata_factory():
    class FakeIdentityAdapter:
        def get_records(
            self,
            coin,
        ):
            return []

    source_adapter = FakeIdentityAdapter()
    destination_adapter = FakeIdentityAdapter()

    class FakeIdentityFactory:
        def __init__(self):
            self.calls = []

        def build(
            self,
            exchange,
        ):
            self.calls.append(
                exchange
            )

            if getattr(
                exchange,
                "id",
                "",
            ) == "poloniex":
                return source_adapter

            return destination_adapter

    identity_factory = (
        FakeIdentityFactory()
    )

    source_exchange = type(
        "PoloniexExchange",
        (),
        {
            "id": "poloniex",
        },
    )()

    destination_exchange = type(
        "GateExchange",
        (),
        {
            "id": "gate",
        },
    )()

    preparer = PublicLiveMultiPathInputPreparer(
        source_exchange=source_exchange,
        destination_exchange=destination_exchange,
        network_identity_metadata_adapter_factory=(
            identity_factory
        ),
    )

    assert (
        preparer
        ._network_identity_metadata_adapter_factory
        is identity_factory
    )


def test_network_identity_metadata_factory_defaults_when_not_supplied():
    preparer = PublicLiveMultiPathInputPreparer(
        source_exchange=object(),
        destination_exchange=object(),
    )

    assert (
        preparer
        ._network_identity_metadata_adapter_factory
        is not None
    )
