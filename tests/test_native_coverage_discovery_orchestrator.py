from exchanges.native_coverage_discovery_orchestrator import (
    NativeCoverageDiscoveryOrchestrator,
)


class FakeRegistry:
    pass


class FakeExchange:
    def __init__(self, exchange_id):
        self.id = exchange_id


class FakeNativeSource:
    pass


class FakeScanner:
    def __init__(self, result):
        self.result = result
        self.entries = None

    def scan(self, entries):
        self.entries = entries
        return self.result


class FakePrioritizer:
    def __init__(self, result):
        self.result = result
        self.audits = None

    def prioritize(self, audits):
        self.audits = audits
        return self.result


def test_orchestrates_scan_and_priority():
    audits = [
        {
            "exchange_id": "digifinex",
            "verified_raw_only_count": 513,
            "fallback_coverage": "AVAILABLE",
        },
        {
            "exchange_id": "gate",
            "verified_raw_only_count": 0,
            "fallback_coverage": "NOT_REQUIRED",
        },
    ]

    scanner = FakeScanner({
        "exchange_count": 2,
        "successful_exchange_count": 2,
        "failed_exchange_count": 0,
        "failed_exchanges": [],
        "audits": audits,
        "ranked_exchanges": audits,
        "scan_complete": True,
        "live_order_submitted": False,
    })

    priority_result = {
        "priority_count": 2,
        "excluded_exchange_count": 0,
        "priorities": [
            {
                "exchange_id": "digifinex",
                "implementation_status": "IMPLEMENTED",
            },
            {
                "exchange_id": "gate",
                "implementation_status": "NOT_REQUIRED",
            },
        ],
        "excluded_exchanges": [],
        "priority_complete": True,
        "live_order_submitted": False,
    }

    prioritizer = FakePrioritizer(
        priority_result
    )

    entries = [
        {
            "exchange": FakeExchange(
                "digifinex"
            ),
            "native_market_source": (
                FakeNativeSource()
            ),
        },
        {
            "exchange": FakeExchange(
                "gate"
            ),
            "native_market_source": (
                FakeNativeSource()
            ),
        },
    ]

    result = (
        NativeCoverageDiscoveryOrchestrator(
            fallback_registry=FakeRegistry(),
            scanner=scanner,
            prioritizer=prioritizer,
        ).run(entries)
    )

    assert scanner.entries is entries
    assert prioritizer.audits is audits

    assert result["exchange_count"] == 2
    assert result["successful_exchange_count"] == 2
    assert result["failed_exchange_count"] == 0

    assert result["audits"] is audits

    assert result["priorities"] == (
        priority_result["priorities"]
    )

    assert result["orchestration_complete"] is True
    assert result["live_order_submitted"] is False


def test_preserves_failed_exchange_evidence():
    failed = {
        "exchange_id": "broken",
        "scan_failed": True,
        "error_type": "TimeoutError",
        "error": "public API timeout",
    }

    healthy = {
        "exchange_id": "gate",
        "scan_failed": False,
        "verified_raw_only_count": 0,
        "fallback_coverage": "NOT_REQUIRED",
    }

    scanner = FakeScanner({
        "exchange_count": 2,
        "successful_exchange_count": 1,
        "failed_exchange_count": 1,
        "failed_exchanges": [failed],
        "audits": [
            failed,
            healthy,
        ],
        "ranked_exchanges": [
            healthy,
        ],
        "scan_complete": True,
        "live_order_submitted": False,
    })

    prioritizer = FakePrioritizer({
        "priority_count": 1,
        "excluded_exchange_count": 1,
        "priorities": [
            {
                "exchange_id": "gate",
                "implementation_status": (
                    "NOT_REQUIRED"
                ),
            },
        ],
        "excluded_exchanges": [
            failed,
        ],
        "priority_complete": True,
        "live_order_submitted": False,
    })

    result = (
        NativeCoverageDiscoveryOrchestrator(
            fallback_registry=FakeRegistry(),
            scanner=scanner,
            prioritizer=prioritizer,
        ).run([
            {
                "exchange": FakeExchange(
                    "broken"
                ),
                "native_market_source": (
                    FakeNativeSource()
                ),
            },
            {
                "exchange": FakeExchange(
                    "gate"
                ),
                "native_market_source": (
                    FakeNativeSource()
                ),
            },
        ])
    )

    assert result["failed_exchange_count"] == 1
    assert result["failed_exchanges"] == [
        failed
    ]

    assert result[
        "excluded_exchange_count"
    ] == 1

    assert result[
        "excluded_exchanges"
    ] == [
        failed
    ]


def test_empty_entries_are_supported():
    scanner = FakeScanner({
        "exchange_count": 0,
        "successful_exchange_count": 0,
        "failed_exchange_count": 0,
        "failed_exchanges": [],
        "audits": [],
        "ranked_exchanges": [],
        "scan_complete": True,
        "live_order_submitted": False,
    })

    prioritizer = FakePrioritizer({
        "priority_count": 0,
        "excluded_exchange_count": 0,
        "priorities": [],
        "excluded_exchanges": [],
        "priority_complete": True,
        "live_order_submitted": False,
    })

    result = (
        NativeCoverageDiscoveryOrchestrator(
            fallback_registry=FakeRegistry(),
            scanner=scanner,
            prioritizer=prioritizer,
        ).run([])
    )

    assert result["exchange_count"] == 0
    assert result["priorities"] == []
    assert result["orchestration_complete"] is True


def test_requires_entries():
    orchestrator = (
        NativeCoverageDiscoveryOrchestrator(
            fallback_registry=FakeRegistry(),
            scanner=FakeScanner({}),
            prioritizer=FakePrioritizer({}),
        )
    )

    try:
        orchestrator.run(None)
        assert False
    except ValueError as exc:
        assert str(exc) == "entries are required"


def test_requires_fallback_registry():
    try:
        NativeCoverageDiscoveryOrchestrator(
            fallback_registry=None
        )
        assert False
    except ValueError as exc:
        assert str(exc) == (
            "fallback_registry is required"
        )


def test_never_submits_live_order():
    scanner = FakeScanner({
        "exchange_count": 0,
        "successful_exchange_count": 0,
        "failed_exchange_count": 0,
        "failed_exchanges": [],
        "audits": [],
        "ranked_exchanges": [],
        "scan_complete": True,
        "live_order_submitted": False,
    })

    prioritizer = FakePrioritizer({
        "priority_count": 0,
        "excluded_exchange_count": 0,
        "priorities": [],
        "excluded_exchanges": [],
        "priority_complete": True,
        "live_order_submitted": False,
    })

    result = (
        NativeCoverageDiscoveryOrchestrator(
            fallback_registry=FakeRegistry(),
            scanner=scanner,
            prioritizer=prioritizer,
        ).run([])
    )

    assert result["live_order_submitted"] is False
