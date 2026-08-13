import pytest

from core.live_multi_source_intelligence_cycle import (
    LiveMultiSourceIntelligenceCycle,
)


class FakeOrchestrator:
    def __init__(self):
        self.calls = 0

    def run_once(self):
        self.calls += 1

        return {
            "source_count": 3,
            "successful_source_count": 3,
            "failed_source_count": 0,
            "failed_sources": [],
            "candidate_count": 4,
            "unique_opportunity_count": 3,
            "consensus_opportunity_count": 1,
            "candidates": [],
            "opportunities": [
                {
                    "opportunity_key": (
                        "COTI:kucoin:digifinex"
                    ),
                    "coin": "COTI",
                    "buy_exchange": "kucoin",
                    "sell_exchange": "digifinex",
                    "sources": [
                        "coinmarketgap",
                        "finder",
                    ],
                    "source_count": 2,
                    "signal_count": 2,
                    "verification_required": True,
                    "arbos_verified": False,
                    "executable": False,
                },
                {
                    "opportunity_key": (
                        "VANRY:bingx:kucoin"
                    ),
                    "coin": "VANRY",
                    "buy_exchange": "bingx",
                    "sell_exchange": "kucoin",
                    "sources": ["finder"],
                    "source_count": 1,
                    "signal_count": 1,
                    "verification_required": True,
                    "arbos_verified": False,
                    "executable": False,
                },
                {
                    "opportunity_key": (
                        "FLOW:htx:okx"
                    ),
                    "coin": "FLOW",
                    "buy_exchange": "htx",
                    "sell_exchange": "okx",
                    "sources": ["finder"],
                    "source_count": 1,
                    "signal_count": 1,
                    "verification_required": True,
                    "arbos_verified": False,
                    "executable": False,
                },
            ],
            "verification_queue": [],
            "verification_queue_count": 0,
            "source_results": {
                "coinmarketgap": {
                    "fetch_complete": True,
                    "candidate_count": 1,
                },
                "sharpe": {
                    "fetch_complete": True,
                    "candidate_count": 0,
                },
                "finder": {
                    "fetch_complete": True,
                    "candidate_count": 3,
                },
            },
            "paper_only": True,
            "live_order_submitted": False,
        }


def test_live_cycle_runs_orchestrator_once():
    orchestrator = FakeOrchestrator()

    cycle = LiveMultiSourceIntelligenceCycle(
        orchestrator=orchestrator,
        clock=lambda: 1000.0,
    )

    cycle.run_once()

    assert orchestrator.calls == 1


def test_live_cycle_reports_source_counts():
    cycle = LiveMultiSourceIntelligenceCycle(
        orchestrator=FakeOrchestrator(),
        clock=lambda: 1000.0,
    )

    result = cycle.run_once()

    assert result["source_count"] == 3
    assert result["successful_source_count"] == 3
    assert result["failed_source_count"] == 0


def test_live_cycle_reports_candidate_totals():
    cycle = LiveMultiSourceIntelligenceCycle(
        orchestrator=FakeOrchestrator(),
        clock=lambda: 1000.0,
    )

    result = cycle.run_once()

    assert result["candidate_count"] == 4
    assert result["unique_opportunity_count"] == 3
    assert result["consensus_opportunity_count"] == 1


def test_live_cycle_preserves_per_source_results():
    cycle = LiveMultiSourceIntelligenceCycle(
        orchestrator=FakeOrchestrator(),
        clock=lambda: 1000.0,
    )

    result = cycle.run_once()

    sources = result["source_results"]

    assert sources[
        "coinmarketgap"
    ]["candidate_count"] == 1

    assert sources[
        "sharpe"
    ]["candidate_count"] == 0

    assert sources[
        "finder"
    ]["candidate_count"] == 3


def test_live_cycle_preserves_ranked_opportunities():
    cycle = LiveMultiSourceIntelligenceCycle(
        orchestrator=FakeOrchestrator(),
        clock=lambda: 1000.0,
    )

    result = cycle.run_once()

    opportunities = result["opportunities"]

    assert opportunities[0][
        "opportunity_key"
    ] == "COTI:kucoin:digifinex"

    assert opportunities[0][
        "source_count"
    ] == 2


def test_live_cycle_records_cycle_timestamp():
    cycle = LiveMultiSourceIntelligenceCycle(
        orchestrator=FakeOrchestrator(),
        clock=lambda: 1234.5,
    )

    result = cycle.run_once()

    assert result[
        "cycle_observed_at"
    ] == 1234.5


def test_live_cycle_rejects_missing_orchestrator():
    with pytest.raises(
        ValueError,
        match="orchestrator is required",
    ):
        LiveMultiSourceIntelligenceCycle(
            orchestrator=None
        )


def test_live_cycle_is_paper_safe():
    cycle = LiveMultiSourceIntelligenceCycle(
        orchestrator=FakeOrchestrator(),
        clock=lambda: 1000.0,
    )

    result = cycle.run_once()

    assert result["paper_only"] is True
    assert result[
        "live_order_submitted"
    ] is False


def test_live_cycle_does_not_mark_external_leads_verified():
    cycle = LiveMultiSourceIntelligenceCycle(
        orchestrator=FakeOrchestrator(),
        clock=lambda: 1000.0,
    )

    result = cycle.run_once()

    for opportunity in result[
        "opportunities"
    ]:
        assert opportunity[
            "arbos_verified"
        ] is False

        assert opportunity[
            "executable"
        ] is False

        assert opportunity[
            "verification_required"
        ] is True
