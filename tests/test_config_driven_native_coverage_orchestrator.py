from exchanges.config_driven_native_coverage_orchestrator import (
    ConfigDrivenNativeCoverageOrchestrator,
)


class FakeExchange:
    def __init__(self, exchange_id):
        self.id = exchange_id


class FakeEntryFactory:
    def __init__(self, result):
        self.result = result
        self.exchanges = None

    def build(self, exchanges):
        self.exchanges = exchanges
        return self.result


class FakeOrchestrator:
    def __init__(self, result):
        self.result = result
        self.entries = None

    def run(self, entries):
        self.entries = entries
        return self.result


def test_builds_entries_and_runs_orchestrator():
    exchanges = {
        "gate": FakeExchange("gate"),
        "digifinex": FakeExchange("digifinex"),
    }

    entries = [
        {
            "exchange": exchanges["gate"],
            "native_market_source": object(),
        },
        {
            "exchange": exchanges["digifinex"],
            "native_market_source": object(),
        },
    ]

    factory = FakeEntryFactory({
        "entry_count": 2,
        "entries": entries,
        "unsupported_exchange_count": 0,
        "unsupported_exchange_ids": [],
        "invalid_exchange_count": 0,
        "build_complete": True,
        "live_order_submitted": False,
    })

    orchestration_result = {
        "exchange_count": 2,
        "successful_exchange_count": 2,
        "failed_exchange_count": 0,
        "priorities": [],
        "orchestration_complete": True,
        "live_order_submitted": False,
    }

    orchestrator = FakeOrchestrator(
        orchestration_result
    )

    result = (
        ConfigDrivenNativeCoverageOrchestrator(
            fallback_registry=object(),
            entry_factory=factory,
            orchestrator=orchestrator,
        ).run(exchanges)
    )

    assert factory.exchanges is exchanges
    assert orchestrator.entries is entries

    assert result["entry_count"] == 2
    assert result["exchange_count"] == 2
    assert result["orchestration_complete"] is True
    assert result["live_order_submitted"] is False


def test_preserves_factory_diagnostics():
    factory = FakeEntryFactory({
        "entry_count": 1,
        "entries": [],
        "unsupported_exchange_count": 2,
        "unsupported_exchange_ids": [
            "alpha",
            "beta",
        ],
        "invalid_exchange_count": 1,
        "build_complete": True,
        "live_order_submitted": False,
    })

    orchestrator = FakeOrchestrator({
        "exchange_count": 0,
        "successful_exchange_count": 0,
        "failed_exchange_count": 0,
        "priorities": [],
        "orchestration_complete": True,
        "live_order_submitted": False,
    })

    result = (
        ConfigDrivenNativeCoverageOrchestrator(
            fallback_registry=object(),
            entry_factory=factory,
            orchestrator=orchestrator,
        ).run({})
    )

    assert result[
        "unsupported_exchange_count"
    ] == 2

    assert result[
        "unsupported_exchange_ids"
    ] == [
        "alpha",
        "beta",
    ]

    assert result[
        "invalid_exchange_count"
    ] == 1


def test_requires_exchanges():
    wrapper = ConfigDrivenNativeCoverageOrchestrator(
        fallback_registry=object(),
        entry_factory=FakeEntryFactory({}),
        orchestrator=FakeOrchestrator({}),
    )

    try:
        wrapper.run(None)
        assert False
    except ValueError as exc:
        assert str(exc) == "exchanges are required"


def test_requires_fallback_registry():
    try:
        ConfigDrivenNativeCoverageOrchestrator(
            fallback_registry=None
        )
        assert False
    except ValueError as exc:
        assert str(exc) == (
            "fallback_registry is required"
        )


def test_configuration_wrapper_is_research_only():
    factory = FakeEntryFactory({
        "entry_count": 0,
        "entries": [],
        "unsupported_exchange_count": 0,
        "unsupported_exchange_ids": [],
        "invalid_exchange_count": 0,
        "build_complete": True,
        "live_order_submitted": False,
    })

    orchestrator = FakeOrchestrator({
        "exchange_count": 0,
        "successful_exchange_count": 0,
        "failed_exchange_count": 0,
        "priorities": [],
        "orchestration_complete": True,
        "live_order_submitted": False,
    })

    result = (
        ConfigDrivenNativeCoverageOrchestrator(
            fallback_registry=object(),
            entry_factory=factory,
            orchestrator=orchestrator,
        ).run({})
    )

    assert result["live_order_submitted"] is False


def test_default_factory_configures_digifinex_depth_provider():
    from exchanges.verified_digifinex_order_book_provider import (
        VerifiedDigiFinexOrderBookProvider,
    )

    class CaptureOrchestrator:
        def __init__(self):
            self.entries = None

        def run(self, entries):
            self.entries = entries

            return {
                "exchange_count": len(entries),
                "successful_exchange_count": (
                    len(entries)
                ),
                "failed_exchange_count": 0,
                "priorities": [],
                "orchestration_complete": True,
                "live_order_submitted": False,
            }

    digifinex = FakeExchange(
        "digifinex"
    )

    capture = CaptureOrchestrator()

    wrapper = (
        ConfigDrivenNativeCoverageOrchestrator(
            fallback_registry=object(),
            orchestrator=capture,
        )
    )

    result = wrapper.run({
        "digifinex": digifinex,
    })

    assert result["entry_count"] == 1

    entry = capture.entries[0]

    assert isinstance(
        entry["order_book_provider"],
        VerifiedDigiFinexOrderBookProvider,
    )

    assert entry["depth_sample_size"] == 20
