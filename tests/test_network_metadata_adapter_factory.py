from exchanges.ccxt_network_metadata_adapter import (
    CCXTNetworkMetadataAdapter,
)
from exchanges.network_metadata_adapter_factory import (
    NetworkMetadataAdapterFactory,
)
from exchanges.weex_network_metadata_adapter import (
    WeexNetworkMetadataAdapter,
)


class FakeExchange:
    def __init__(self, exchange_id):
        self.id = exchange_id

    def load_currencies(self):
        return {}


class FakeWeexProvider:
    pass


def test_weex_builds_weex_network_adapter():
    factory = NetworkMetadataAdapterFactory(
        weex_provider_factory=(
            lambda exchange: FakeWeexProvider()
        )
    )

    adapter = factory.build(
        FakeExchange("weex")
    )

    assert isinstance(
        adapter,
        WeexNetworkMetadataAdapter,
    )


def test_non_weex_exchange_uses_ccxt_adapter():
    factory = NetworkMetadataAdapterFactory()

    adapter = factory.build(
        FakeExchange("kucoin")
    )

    assert isinstance(
        adapter,
        CCXTNetworkMetadataAdapter,
    )


def test_unknown_exchange_uses_ccxt_adapter():
    factory = NetworkMetadataAdapterFactory()

    adapter = factory.build(
        FakeExchange("unknown")
    )

    assert isinstance(
        adapter,
        CCXTNetworkMetadataAdapter,
    )


def test_exchange_id_is_normalized():
    factory = NetworkMetadataAdapterFactory(
        weex_provider_factory=(
            lambda exchange: FakeWeexProvider()
        )
    )

    adapter = factory.build(
        FakeExchange(" WEEX ")
    )

    assert isinstance(
        adapter,
        WeexNetworkMetadataAdapter,
    )


def test_missing_exchange_is_rejected():
    factory = NetworkMetadataAdapterFactory()

    try:
        factory.build(None)
        assert False
    except ValueError as exc:
        assert str(exc) == "exchange is required"


def test_custom_weex_provider_factory_is_used():
    marker = object()
    calls = []

    def provider_factory(exchange):
        calls.append(exchange)
        return marker

    factory = NetworkMetadataAdapterFactory(
        weex_provider_factory=(
            provider_factory
        )
    )

    exchange = FakeExchange("weex")

    adapter = factory.build(
        exchange
    )

    assert calls == [
        exchange
    ]

    assert adapter._provider is marker
