from exchanges.ccxt_network_identity_metadata_adapter import (
    CCXTNetworkIdentityMetadataAdapter,
)
from exchanges.network_identity_metadata_adapter_factory import (
    NetworkIdentityMetadataAdapterFactory,
)
from exchanges.poloniex_network_identity_metadata_adapter import (
    PoloniexNetworkIdentityMetadataAdapter,
)


class FakeExchange:
    def __init__(self, exchange_id):
        self.id = exchange_id
        self.currencies = {}

    def load_currencies(self):
        return {}

    def load_markets(self):
        self.currencies = {}
        return {}


class FakePoloniexProvider:
    pass


def test_poloniex_builds_native_identity_adapter():
    factory = NetworkIdentityMetadataAdapterFactory(
        poloniex_provider_factory=(
            lambda exchange: FakePoloniexProvider()
        )
    )

    adapter = factory.build(
        FakeExchange("poloniex")
    )

    assert isinstance(
        adapter,
        PoloniexNetworkIdentityMetadataAdapter,
    )


def test_non_poloniex_exchange_uses_ccxt_identity_adapter():
    factory = NetworkIdentityMetadataAdapterFactory()

    adapter = factory.build(
        FakeExchange("kucoin")
    )

    assert isinstance(
        adapter,
        CCXTNetworkIdentityMetadataAdapter,
    )


def test_unknown_exchange_uses_ccxt_identity_adapter():
    factory = NetworkIdentityMetadataAdapterFactory()

    adapter = factory.build(
        FakeExchange("unknown")
    )

    assert isinstance(
        adapter,
        CCXTNetworkIdentityMetadataAdapter,
    )


def test_exchange_id_is_normalized():
    factory = NetworkIdentityMetadataAdapterFactory(
        poloniex_provider_factory=(
            lambda exchange: FakePoloniexProvider()
        )
    )

    adapter = factory.build(
        FakeExchange(" POLONIEX ")
    )

    assert isinstance(
        adapter,
        PoloniexNetworkIdentityMetadataAdapter,
    )


def test_missing_exchange_is_rejected():
    factory = NetworkIdentityMetadataAdapterFactory()

    try:
        factory.build(None)
        assert False
    except ValueError as exc:
        assert str(exc) == "exchange is required"


def test_custom_poloniex_provider_factory_is_used():
    marker = object()
    calls = []

    def provider_factory(exchange):
        calls.append(exchange)
        return marker

    factory = NetworkIdentityMetadataAdapterFactory(
        poloniex_provider_factory=(
            provider_factory
        )
    )

    exchange = FakeExchange(
        "poloniex"
    )

    adapter = factory.build(
        exchange
    )

    assert calls == [
        exchange
    ]

    assert adapter._provider is marker
