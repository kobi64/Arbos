from core.native_coverage_application import (
    NativeCoverageApplication,
)


class FakeExchange:
    def __init__(self, config=None):
        self.config = config or {}


class FakeCCXT:
    gate = FakeExchange
    kucoin = FakeExchange


class FakeCoverageOrchestrator:
    def __init__(self):
        self.exchanges = None

    def run(self, exchanges):
        self.exchanges = exchanges
        return {
            "entry_count": len(exchanges),
            "exchange_count": len(exchanges),
            "successful_exchange_count": len(exchanges),
            "failed_exchange_count": 0,
            "priorities": [],
            "orchestration_complete": True,
            "live_order_submitted": False,
        }


def test_builds_exchange_set_and_runs_coverage():
    orchestrator = FakeCoverageOrchestrator()

    app = NativeCoverageApplication(
        ccxt_module=FakeCCXT,
        fallback_registry=object(),
        exchange_ids=[
            "gate",
            "kucoin",
        ],
        coverage_orchestrator=orchestrator,
    )

    result = app.run()

    assert sorted(
        orchestrator.exchanges.keys()
    ) == [
        "gate",
        "kucoin",
    ]

    assert result["exchange_count"] == 2
    assert result["orchestration_complete"] is True


def test_disabled_exchange_is_not_run():
    orchestrator = FakeCoverageOrchestrator()

    app = NativeCoverageApplication(
        ccxt_module=FakeCCXT,
        fallback_registry=object(),
        exchange_ids=[
            "gate",
            "kucoin",
        ],
        coverage_orchestrator=orchestrator,
    )

    app.set_enabled(
        "kucoin",
        False,
    )

    result = app.run()

    assert sorted(
        orchestrator.exchanges.keys()
    ) == [
        "gate",
    ]

    assert result["exchange_count"] == 1


def test_requires_ccxt_module():
    try:
        NativeCoverageApplication(
            ccxt_module=None,
            fallback_registry=object(),
        )
        assert False
    except ValueError as exc:
        assert str(exc) == (
            "ccxt_module is required"
        )


def test_requires_fallback_registry():
    try:
        NativeCoverageApplication(
            ccxt_module=FakeCCXT,
            fallback_registry=None,
        )
        assert False
    except ValueError as exc:
        assert str(exc) == (
            "fallback_registry is required"
        )


def test_application_is_research_only():
    orchestrator = FakeCoverageOrchestrator()

    app = NativeCoverageApplication(
        ccxt_module=FakeCCXT,
        fallback_registry=object(),
        exchange_ids=[],
        coverage_orchestrator=orchestrator,
    )

    result = app.run()

    assert result["live_order_submitted"] is False


class FakeHealthReporter:
    def __init__(self):
        self.coverage_result = None

    def build(self, coverage_result):
        self.coverage_result = coverage_result
        return {
            "status": "HEALTHY",
            "healthy": True,
            "report_complete": True,
            "live_order_submitted": False,
        }


def test_run_health_report_builds_from_application_result():
    orchestrator = FakeCoverageOrchestrator()
    reporter = FakeHealthReporter()

    app = NativeCoverageApplication(
        ccxt_module=FakeCCXT,
        fallback_registry=object(),
        exchange_ids=[
            "gate",
            "kucoin",
        ],
        coverage_orchestrator=orchestrator,
        health_reporter=reporter,
    )

    report = app.run_health_report()

    assert reporter.coverage_result[
        "configured_exchange_count"
    ] == 2

    assert report["status"] == "HEALTHY"
    assert report["healthy"] is True


def test_run_contract_is_unchanged_when_health_reporter_exists():
    orchestrator = FakeCoverageOrchestrator()
    reporter = FakeHealthReporter()

    app = NativeCoverageApplication(
        ccxt_module=FakeCCXT,
        fallback_registry=object(),
        exchange_ids=[
            "gate",
        ],
        coverage_orchestrator=orchestrator,
        health_reporter=reporter,
    )

    result = app.run()

    assert result["exchange_count"] == 1
    assert "status" not in result
    assert reporter.coverage_result is None


def test_health_report_is_research_only():
    app = NativeCoverageApplication(
        ccxt_module=FakeCCXT,
        fallback_registry=object(),
        exchange_ids=[],
        coverage_orchestrator=FakeCoverageOrchestrator(),
        health_reporter=FakeHealthReporter(),
    )

    report = app.run_health_report()

    assert report["live_order_submitted"] is False


class FakeHealthHistoryStore:
    def __init__(self):
        self.report = None

    def append(self, health_report):
        self.report = health_report
        return {
            "stored": True,
            "timestamp": 1234.0,
            "status": health_report.get(
                "status"
            ),
            "live_order_submitted": False,
        }


def test_run_and_record_health_report_persists_report():
    orchestrator = FakeCoverageOrchestrator()
    reporter = FakeHealthReporter()
    history_store = FakeHealthHistoryStore()

    app = NativeCoverageApplication(
        ccxt_module=FakeCCXT,
        fallback_registry=object(),
        exchange_ids=[
            "gate",
            "kucoin",
        ],
        coverage_orchestrator=orchestrator,
        health_reporter=reporter,
        health_history_store=history_store,
    )

    result = app.run_and_record_health_report()

    assert history_store.report["status"] == (
        "HEALTHY"
    )

    assert result["stored"] is True
    assert result["timestamp"] == 1234.0
    assert result["status"] == "HEALTHY"


def test_recording_does_not_change_existing_health_report_contract():
    orchestrator = FakeCoverageOrchestrator()
    reporter = FakeHealthReporter()
    history_store = FakeHealthHistoryStore()

    app = NativeCoverageApplication(
        ccxt_module=FakeCCXT,
        fallback_registry=object(),
        exchange_ids=[
            "gate",
        ],
        coverage_orchestrator=orchestrator,
        health_reporter=reporter,
        health_history_store=history_store,
    )

    report = app.run_health_report()

    assert report["status"] == "HEALTHY"
    assert history_store.report is None


def test_run_and_record_requires_history_store():
    app = NativeCoverageApplication(
        ccxt_module=FakeCCXT,
        fallback_registry=object(),
        exchange_ids=[],
        coverage_orchestrator=FakeCoverageOrchestrator(),
        health_reporter=FakeHealthReporter(),
    )

    try:
        app.run_and_record_health_report()
        assert False
    except ValueError as exc:
        assert str(exc) == (
            "health_history_store is required"
        )
