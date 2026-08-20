"""
ArbOS™

EX-352
Metadata adapter reuse regression.

Proves that exchange-level network metadata adapters are
constructed once per preparer/exchange pair rather than
once per coin.
"""

from core.public_live_multi_path_input_preparer import (
    PublicLiveMultiPathInputPreparer,
)


class FakeExchange:
    def __init__(self, exchange_id):
        self.id = exchange_id


class CountingFactory:
    def __init__(self):
        self.calls = []
        self.adapters = {}

    def build(self, exchange):
        self.calls.append(
            exchange.id
        )

        return self.adapters.setdefault(
            exchange.id,
            object(),
        )


def test_network_metadata_adapters_are_cached_per_pair():
    source = FakeExchange("kucoin")
    destination = FakeExchange("htx")

    network_factory = CountingFactory()
    identity_factory = CountingFactory()

    preparer = (
        PublicLiveMultiPathInputPreparer(
            source_exchange=source,
            destination_exchange=destination,
            network_metadata_adapter_factory=(
                network_factory
            ),
            network_identity_metadata_adapter_factory=(
                identity_factory
            ),
        )
    )

    first_network = (
        preparer._network_adapters()
    )
    second_network = (
        preparer._network_adapters()
    )

    first_identity = (
        preparer._identity_adapters()
    )
    second_identity = (
        preparer._identity_adapters()
    )

    assert first_network == second_network
    assert first_identity == second_identity

    assert network_factory.calls == [
        "kucoin",
        "htx",
    ]

    assert identity_factory.calls == [
        "kucoin",
        "htx",
    ]


def test_repeated_adapter_access_does_not_rebuild_metadata():
    source = FakeExchange("htx")
    destination = FakeExchange("bitget")

    network_factory = CountingFactory()
    identity_factory = CountingFactory()

    preparer = (
        PublicLiveMultiPathInputPreparer(
            source_exchange=source,
            destination_exchange=destination,
            network_metadata_adapter_factory=(
                network_factory
            ),
            network_identity_metadata_adapter_factory=(
                identity_factory
            ),
        )
    )

    for _ in range(100):
        preparer._network_adapters()
        preparer._identity_adapters()

    assert len(
        network_factory.calls
    ) == 2

    assert len(
        identity_factory.calls
    ) == 2
