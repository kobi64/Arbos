from core.public_live_multi_path_pipeline_factory import (
    PublicLiveMultiPathPipelineFactory,
)
from core.live_multi_path_paper_scan import (
    LiveMultiPathPaperScan,
)


class FakeExchange:
    pass


def test_builds_live_multi_path_paper_pipeline():
    factory = PublicLiveMultiPathPipelineFactory()

    scanner = factory.build(
        source_exchange=FakeExchange(),
        destination_exchange=FakeExchange(),
    )

    assert isinstance(
        scanner,
        LiveMultiPathPaperScan,
    )


def test_builds_pipeline_with_digifinex_destination():
    class DigiFinexExchange:
        id = "digifinex"

    scanner = (
        PublicLiveMultiPathPipelineFactory()
        .build(
            source_exchange=FakeExchange(),
            destination_exchange=(
                DigiFinexExchange()
            ),
        )
    )

    assert isinstance(
        scanner,
        LiveMultiPathPaperScan,
    )


from core.internal_multi_bridge_scan_coordinator import (
    InternalMultiBridgeScanCoordinator,
)


def test_builds_standalone_internal_scanner():
    factory = PublicLiveMultiPathPipelineFactory()

    scanner = factory.build_internal(
        exchange=FakeExchange(),
    )

    assert isinstance(
        scanner,
        InternalMultiBridgeScanCoordinator,
    )


def test_full_pipeline_reuses_internal_builder():
    class TrackingFactory(
        PublicLiveMultiPathPipelineFactory
    ):
        def __init__(self):
            self.internal_calls = []

        def build_internal(
            self,
            exchange,
        ):
            self.internal_calls.append(
                exchange
            )

            return super().build_internal(
                exchange=exchange
            )

    source = FakeExchange()
    destination = FakeExchange()

    factory = TrackingFactory()

    scanner = factory.build(
        source_exchange=source,
        destination_exchange=destination,
    )

    assert isinstance(
        scanner,
        LiveMultiPathPaperScan,
    )

    assert factory.internal_calls == [
        source,
    ]


from core.multi_path_arbitrage_integration_coordinator import (
    MultiPathArbitrageIntegrationCoordinator,
)


def test_builds_standalone_cross_exchange_coordinator():
    factory = PublicLiveMultiPathPipelineFactory()

    coordinator = factory.build_cross_exchange(
        destination_exchange=FakeExchange(),
    )

    assert isinstance(
        coordinator,
        MultiPathArbitrageIntegrationCoordinator,
    )


def test_full_pipeline_reuses_cross_exchange_builder():
    class TrackingFactory(
        PublicLiveMultiPathPipelineFactory
    ):
        def __init__(self):
            self.cross_calls = []

        def build_cross_exchange(
            self,
            destination_exchange,
        ):
            self.cross_calls.append(
                destination_exchange
            )

            return super().build_cross_exchange(
                destination_exchange=(
                    destination_exchange
                )
            )

    source = FakeExchange()
    destination = FakeExchange()

    factory = TrackingFactory()

    scanner = factory.build(
        source_exchange=source,
        destination_exchange=destination,
    )

    assert isinstance(
        scanner,
        LiveMultiPathPaperScan,
    )

    assert factory.cross_calls == [
        destination,
    ]
