from core.live_multi_source_intelligence_factory import (
    LiveMultiSourceIntelligenceFactory,
)
from core.live_multi_source_intelligence_cycle import (
    LiveMultiSourceIntelligenceCycle,
)
from core.multi_source_external_intelligence_orchestrator import (
    MultiSourceExternalIntelligenceOrchestrator,
)


def test_factory_builds_live_cycle():
    factory = LiveMultiSourceIntelligenceFactory()

    cycle = factory.build()

    assert isinstance(
        cycle,
        LiveMultiSourceIntelligenceCycle,
    )


def test_factory_builds_multi_source_orchestrator():
    factory = LiveMultiSourceIntelligenceFactory()

    orchestrator = factory.build_orchestrator()

    assert isinstance(
        orchestrator,
        MultiSourceExternalIntelligenceOrchestrator,
    )


def test_factory_registers_all_three_external_sources():
    factory = LiveMultiSourceIntelligenceFactory()

    orchestrator = factory.build_orchestrator()

    sources = set(
        orchestrator._coordinators.keys()
    )

    assert sources == {
        "coinmarketgap",
        "sharpe",
        "finder",
    }


def test_factory_builds_paper_safe_cycle():
    factory = LiveMultiSourceIntelligenceFactory()

    cycle = factory.build(
        clock=lambda: 1000.0,
    )

    assert cycle is not None


def test_factory_accepts_shared_tracker_and_correlator():
    class FakeTracker:
        pass

    class FakeCorrelator:
        pass

    tracker = FakeTracker()
    correlator = FakeCorrelator()

    factory = LiveMultiSourceIntelligenceFactory()

    orchestrator = factory.build_orchestrator(
        tracker=tracker,
        correlator=correlator,
    )

    coordinators = (
        orchestrator._coordinators
    )

    for coordinator in coordinators.values():
        assert coordinator._tracker is tracker
        assert coordinator._correlator is correlator
