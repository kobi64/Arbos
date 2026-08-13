import pytest

from core.multi_source_external_intelligence_orchestrator import (
    MultiSourceExternalIntelligenceOrchestrator,
)


class FakeCoordinator:
    def __init__(
        self,
        source,
        candidates=None,
        fetch_complete=True,
    ):
        self.source = source
        self._candidates = (
            list(candidates)
            if candidates is not None
            else []
        )
        self._fetch_complete = fetch_complete
        self.calls = 0

    def run_once(self):
        self.calls += 1

        return {
            "fetch_complete": self._fetch_complete,
            "candidate_count": len(
                self._candidates
            ),
            "duplicate_count": 0,
            "candidates": list(
                self._candidates
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }


def candidate(
    source,
    key,
    coin="COTI",
    buy_exchange="kucoin",
    sell_exchange="bitget",
    spread=10.0,
):
    return {
        "source": source,
        "source_signal_id": (
            f"{source}-1"
        ),
        "signal_key": (
            f"{source}:{source}-1"
        ),
        "opportunity_key": key,
        "coin": coin,
        "buy_exchange": buy_exchange,
        "sell_exchange": sell_exchange,
        "reported_spread_percent": spread,
        "reported_status": "reported",
        "arbos_verified": False,
        "executable": False,
        "verification_required": True,
    }


def test_runs_all_registered_sources():
    cmg = FakeCoordinator(
        "coinmarketgap"
    )
    sharpe = FakeCoordinator(
        "sharpe"
    )
    finder = FakeCoordinator(
        "finder"
    )

    orchestrator = (
        MultiSourceExternalIntelligenceOrchestrator(
            coordinators={
                "coinmarketgap": cmg,
                "sharpe": sharpe,
                "finder": finder,
            }
        )
    )

    result = orchestrator.run_once()

    assert cmg.calls == 1
    assert sharpe.calls == 1
    assert finder.calls == 1

    assert result[
        "source_count"
    ] == 3


def test_combines_candidates_from_all_sources():
    orchestrator = (
        MultiSourceExternalIntelligenceOrchestrator(
            coordinators={
                "coinmarketgap": FakeCoordinator(
                    "coinmarketgap",
                    candidates=[
                        candidate(
                            "coinmarketgap",
                            "COTI:kucoin:bitget",
                        )
                    ],
                ),
                "sharpe": FakeCoordinator(
                    "sharpe",
                    candidates=[
                        candidate(
                            "sharpe",
                            "VANRY:bingx:kucoin",
                            coin="VANRY",
                            buy_exchange="bingx",
                            sell_exchange="kucoin",
                        )
                    ],
                ),
            }
        )
    )

    result = orchestrator.run_once()

    assert result[
        "candidate_count"
    ] == 2

    sources = {
        item["source"]
        for item in result[
            "candidates"
        ]
    }

    assert sources == {
        "coinmarketgap",
        "sharpe",
    }


def test_same_opportunity_from_multiple_sources_is_grouped():
    key = "COTI:kucoin:bitget"

    orchestrator = (
        MultiSourceExternalIntelligenceOrchestrator(
            coordinators={
                "coinmarketgap": FakeCoordinator(
                    "coinmarketgap",
                    candidates=[
                        candidate(
                            "coinmarketgap",
                            key,
                            spread=9.8,
                        )
                    ],
                ),
                "sharpe": FakeCoordinator(
                    "sharpe",
                    candidates=[
                        candidate(
                            "sharpe",
                            key,
                            spread=10.5,
                        )
                    ],
                ),
            }
        )
    )

    result = orchestrator.run_once()

    assert result[
        "unique_opportunity_count"
    ] == 1

    group = result[
        "opportunities"
    ][0]

    assert group[
        "opportunity_key"
    ] == key

    assert group[
        "sources"
    ] == [
        "coinmarketgap",
        "sharpe",
    ]

    assert group[
        "source_count"
    ] == 2

    assert group[
        "signal_count"
    ] == 2


def test_consensus_opportunity_gets_higher_priority():
    consensus_key = (
        "COTI:kucoin:bitget"
    )

    single_key = (
        "VANRY:bingx:kucoin"
    )

    orchestrator = (
        MultiSourceExternalIntelligenceOrchestrator(
            coordinators={
                "coinmarketgap": FakeCoordinator(
                    "coinmarketgap",
                    candidates=[
                        candidate(
                            "coinmarketgap",
                            consensus_key,
                        ),
                        candidate(
                            "coinmarketgap",
                            single_key,
                            coin="VANRY",
                            buy_exchange="bingx",
                            sell_exchange="kucoin",
                            spread=20.0,
                        ),
                    ],
                ),
                "sharpe": FakeCoordinator(
                    "sharpe",
                    candidates=[
                        candidate(
                            "sharpe",
                            consensus_key,
                        )
                    ],
                ),
            }
        )
    )

    result = orchestrator.run_once()

    ranked = result[
        "opportunities"
    ]

    assert ranked[0][
        "opportunity_key"
    ] == consensus_key

    assert ranked[0][
        "source_count"
    ] == 2

    assert ranked[1][
        "source_count"
    ] == 1


def test_failed_source_does_not_block_other_sources():
    good = FakeCoordinator(
        "finder",
        candidates=[
            candidate(
                "finder",
                "FLOW:htx:okx",
                coin="FLOW",
                buy_exchange="htx",
                sell_exchange="okx",
            )
        ],
    )

    failed = FakeCoordinator(
        "sharpe",
        fetch_complete=False,
    )

    orchestrator = (
        MultiSourceExternalIntelligenceOrchestrator(
            coordinators={
                "finder": good,
                "sharpe": failed,
            }
        )
    )

    result = orchestrator.run_once()

    assert result[
        "candidate_count"
    ] == 1

    assert result[
        "failed_source_count"
    ] == 1

    assert result[
        "failed_sources"
    ] == [
        "sharpe",
    ]


def test_source_results_are_preserved():
    orchestrator = (
        MultiSourceExternalIntelligenceOrchestrator(
            coordinators={
                "finder": FakeCoordinator(
                    "finder",
                ),
            }
        )
    )

    result = orchestrator.run_once()

    assert "finder" in result[
        "source_results"
    ]

    assert result[
        "source_results"
    ][
        "finder"
    ][
        "fetch_complete"
    ] is True


def test_empty_coordinator_mapping_is_rejected():
    with pytest.raises(
        ValueError,
        match="coordinators are required",
    ):
        MultiSourceExternalIntelligenceOrchestrator(
            coordinators={}
        )


def test_none_coordinator_is_rejected():
    with pytest.raises(
        ValueError,
        match=(
            "coordinator is required for sharpe"
        ),
    ):
        MultiSourceExternalIntelligenceOrchestrator(
            coordinators={
                "sharpe": None,
            }
        )


def test_orchestrator_is_paper_safe():
    orchestrator = (
        MultiSourceExternalIntelligenceOrchestrator(
            coordinators={
                "finder": FakeCoordinator(
                    "finder"
                ),
            }
        )
    )

    result = orchestrator.run_once()

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False


def test_source_exception_does_not_block_other_sources():
    class ExplodingCoordinator:
        def run_once(self):
            raise RuntimeError(
                "source exploded"
            )

    good = FakeCoordinator(
        "finder",
        candidates=[
            candidate(
                "finder",
                "FLOW:htx:okx",
                coin="FLOW",
                buy_exchange="htx",
                sell_exchange="okx",
            )
        ],
    )

    orchestrator = (
        MultiSourceExternalIntelligenceOrchestrator(
            coordinators={
                "coinmarketgap": ExplodingCoordinator(),
                "finder": good,
            }
        )
    )

    result = orchestrator.run_once()

    assert result[
        "candidate_count"
    ] == 1

    assert result[
        "failed_source_count"
    ] == 1

    assert result[
        "failed_sources"
    ] == [
        "coinmarketgap",
    ]

    failed = result[
        "source_results"
    ][
        "coinmarketgap"
    ]

    assert failed[
        "fetch_complete"
    ] is False

    assert failed[
        "reason"
    ] == "coordinator_exception"


def test_exception_details_are_preserved_for_audit():
    class ExplodingCoordinator:
        def run_once(self):
            raise RuntimeError(
                "network unavailable"
            )

    orchestrator = (
        MultiSourceExternalIntelligenceOrchestrator(
            coordinators={
                "sharpe": ExplodingCoordinator(),
            }
        )
    )

    result = orchestrator.run_once()

    failed = result[
        "source_results"
    ][
        "sharpe"
    ]

    assert failed[
        "reason"
    ] == "coordinator_exception"

    assert (
        "network unavailable"
        in failed["error"]
    )


def test_consensus_survives_failure_of_third_source():
    key = "COTI:kucoin:bitget"

    class ExplodingCoordinator:
        def run_once(self):
            raise RuntimeError(
                "temporary failure"
            )

    orchestrator = (
        MultiSourceExternalIntelligenceOrchestrator(
            coordinators={
                "coinmarketgap": FakeCoordinator(
                    "coinmarketgap",
                    candidates=[
                        candidate(
                            "coinmarketgap",
                            key,
                        )
                    ],
                ),
                "sharpe": FakeCoordinator(
                    "sharpe",
                    candidates=[
                        candidate(
                            "sharpe",
                            key,
                        )
                    ],
                ),
                "finder": ExplodingCoordinator(),
            }
        )
    )

    result = orchestrator.run_once()

    assert result[
        "consensus_opportunity_count"
    ] == 1

    assert result[
        "opportunities"
    ][0][
        "source_count"
    ] == 2

    assert result[
        "failed_sources"
    ] == [
        "finder",
    ]


def test_verification_queue_prioritizes_multi_source_consensus():
    consensus_key = (
        "COTI:kucoin:bitget"
    )

    single_key = (
        "VANRY:bingx:kucoin"
    )

    orchestrator = (
        MultiSourceExternalIntelligenceOrchestrator(
            coordinators={
                "coinmarketgap": FakeCoordinator(
                    "coinmarketgap",
                    candidates=[
                        candidate(
                            "coinmarketgap",
                            consensus_key,
                            spread=6.0,
                        ),
                        candidate(
                            "coinmarketgap",
                            single_key,
                            coin="VANRY",
                            buy_exchange="bingx",
                            sell_exchange="kucoin",
                            spread=40.0,
                        ),
                    ],
                ),
                "sharpe": FakeCoordinator(
                    "sharpe",
                    candidates=[
                        candidate(
                            "sharpe",
                            consensus_key,
                            spread=5.8,
                        )
                    ],
                ),
            }
        )
    )

    result = orchestrator.run_once()

    queue = result[
        "verification_queue"
    ]

    assert queue[0][
        "opportunity_key"
    ] == consensus_key

    assert queue[0][
        "source_count"
    ] == 2

    assert queue[1][
        "opportunity_key"
    ] == single_key


def test_three_source_consensus_beats_two_source_consensus():
    three_key = (
        "COTI:kucoin:bitget"
    )

    two_key = (
        "FLOW:htx:okx"
    )

    orchestrator = (
        MultiSourceExternalIntelligenceOrchestrator(
            coordinators={
                "coinmarketgap": FakeCoordinator(
                    "coinmarketgap",
                    candidates=[
                        candidate(
                            "coinmarketgap",
                            three_key,
                        ),
                        candidate(
                            "coinmarketgap",
                            two_key,
                            coin="FLOW",
                            buy_exchange="htx",
                            sell_exchange="okx",
                        ),
                    ],
                ),
                "sharpe": FakeCoordinator(
                    "sharpe",
                    candidates=[
                        candidate(
                            "sharpe",
                            three_key,
                        ),
                        candidate(
                            "sharpe",
                            two_key,
                            coin="FLOW",
                            buy_exchange="htx",
                            sell_exchange="okx",
                        ),
                    ],
                ),
                "finder": FakeCoordinator(
                    "finder",
                    candidates=[
                        candidate(
                            "finder",
                            three_key,
                        )
                    ],
                ),
            }
        )
    )

    result = orchestrator.run_once()

    queue = result[
        "verification_queue"
    ]

    assert queue[0][
        "opportunity_key"
    ] == three_key

    assert queue[0][
        "source_count"
    ] == 3

    assert queue[1][
        "source_count"
    ] == 2


def test_queue_assigns_explicit_priority_rank():
    orchestrator = (
        MultiSourceExternalIntelligenceOrchestrator(
            coordinators={
                "finder": FakeCoordinator(
                    "finder",
                    candidates=[
                        candidate(
                            "finder",
                            "FLOW:htx:okx",
                            coin="FLOW",
                            buy_exchange="htx",
                            sell_exchange="okx",
                        )
                    ],
                ),
            }
        )
    )

    result = orchestrator.run_once()

    queue = result[
        "verification_queue"
    ]

    assert queue[0][
        "priority_rank"
    ] == 1


def test_queue_candidates_remain_unverified_until_arbos_checks_them():
    orchestrator = (
        MultiSourceExternalIntelligenceOrchestrator(
            coordinators={
                "finder": FakeCoordinator(
                    "finder",
                    candidates=[
                        candidate(
                            "finder",
                            "FLOW:htx:okx",
                            coin="FLOW",
                            buy_exchange="htx",
                            sell_exchange="okx",
                        )
                    ],
                ),
            }
        )
    )

    result = orchestrator.run_once()

    item = result[
        "verification_queue"
    ][0]

    assert item[
        "arbos_verified"
    ] is False

    assert item[
        "executable"
    ] is False

    assert item[
        "verification_required"
    ] is True


class FakeVerificationBridge:
    def __init__(self):
        self.calls = []

    def verify(
        self,
        candidate,
        starting_usdt_value,
        source_fee_rate,
        destination_fee_rate,
        max_slippage_percent=0.5,
        minimum_profit_percent=0.0,
    ):
        self.calls.append({
            "candidate": dict(candidate),
            "starting_usdt_value": starting_usdt_value,
            "source_fee_rate": source_fee_rate,
            "destination_fee_rate": destination_fee_rate,
            "max_slippage_percent": max_slippage_percent,
            "minimum_profit_percent": minimum_profit_percent,
        })

        return {
            **candidate,
            "arbos_verified": True,
            "executable": True,
            "verification_required": False,
            "verified_net_profit_percent": 2.0,
            "paper_only": True,
            "live_order_submitted": False,
        }


def test_verifies_queue_in_priority_order():
    consensus_key = "COTI:kucoin:bitget"
    single_key = "VANRY:bingx:kucoin"

    orchestrator = (
        MultiSourceExternalIntelligenceOrchestrator(
            coordinators={
                "coinmarketgap": FakeCoordinator(
                    "coinmarketgap",
                    candidates=[
                        candidate(
                            "coinmarketgap",
                            consensus_key,
                            spread=6.0,
                        ),
                        candidate(
                            "coinmarketgap",
                            single_key,
                            coin="VANRY",
                            buy_exchange="bingx",
                            sell_exchange="kucoin",
                            spread=40.0,
                        ),
                    ],
                ),
                "sharpe": FakeCoordinator(
                    "sharpe",
                    candidates=[
                        candidate(
                            "sharpe",
                            consensus_key,
                            spread=5.8,
                        )
                    ],
                ),
            }
        )
    )

    ingestion = orchestrator.run_once()

    bridge = FakeVerificationBridge()

    result = orchestrator.verify_queue(
        ingestion["verification_queue"],
        bridge=bridge,
        fee_rates={
            "kucoin": 0.001,
            "bitget": 0.001,
            "bingx": 0.001,
        },
        starting_usdt_value=300.0,
        max_slippage_percent=0.5,
        minimum_profit_percent=0.5,
    )

    assert bridge.calls[0][
        "candidate"
    ][
        "opportunity_key"
    ] == consensus_key

    assert bridge.calls[1][
        "candidate"
    ][
        "opportunity_key"
    ] == single_key

    assert result[
        "verified_count"
    ] == 2


def test_queue_verification_uses_exchange_fee_rates():
    orchestrator = (
        MultiSourceExternalIntelligenceOrchestrator(
            coordinators={
                "finder": FakeCoordinator(
                    "finder",
                    candidates=[
                        candidate(
                            "finder",
                            "FLOW:htx:okx",
                            coin="FLOW",
                            buy_exchange="htx",
                            sell_exchange="okx",
                        )
                    ],
                ),
            }
        )
    )

    ingestion = orchestrator.run_once()

    bridge = FakeVerificationBridge()

    orchestrator.verify_queue(
        ingestion["verification_queue"],
        bridge=bridge,
        fee_rates={
            "htx": 0.002,
            "okx": 0.001,
        },
        starting_usdt_value=300.0,
    )

    call = bridge.calls[0]

    assert call[
        "source_fee_rate"
    ] == 0.002

    assert call[
        "destination_fee_rate"
    ] == 0.001


def test_missing_fee_rate_is_rejected():
    orchestrator = (
        MultiSourceExternalIntelligenceOrchestrator(
            coordinators={
                "finder": FakeCoordinator(
                    "finder",
                    candidates=[
                        candidate(
                            "finder",
                            "FLOW:htx:okx",
                            coin="FLOW",
                            buy_exchange="htx",
                            sell_exchange="okx",
                        )
                    ],
                ),
            }
        )
    )

    ingestion = orchestrator.run_once()

    with pytest.raises(
        ValueError,
        match="fee rate is required for okx",
    ):
        orchestrator.verify_queue(
            ingestion["verification_queue"],
            bridge=FakeVerificationBridge(),
            fee_rates={
                "htx": 0.002,
            },
            starting_usdt_value=300.0,
        )


def test_verification_results_preserve_priority_rank():
    orchestrator = (
        MultiSourceExternalIntelligenceOrchestrator(
            coordinators={
                "finder": FakeCoordinator(
                    "finder",
                    candidates=[
                        candidate(
                            "finder",
                            "FLOW:htx:okx",
                            coin="FLOW",
                            buy_exchange="htx",
                            sell_exchange="okx",
                        )
                    ],
                ),
            }
        )
    )

    ingestion = orchestrator.run_once()

    result = orchestrator.verify_queue(
        ingestion["verification_queue"],
        bridge=FakeVerificationBridge(),
        fee_rates={
            "htx": 0.002,
            "okx": 0.001,
        },
        starting_usdt_value=300.0,
    )

    assert result[
        "results"
    ][0][
        "priority_rank"
    ] == 1


def test_queue_verification_remains_paper_safe():
    orchestrator = (
        MultiSourceExternalIntelligenceOrchestrator(
            coordinators={
                "finder": FakeCoordinator(
                    "finder",
                    candidates=[
                        candidate(
                            "finder",
                            "FLOW:htx:okx",
                            coin="FLOW",
                            buy_exchange="htx",
                            sell_exchange="okx",
                        )
                    ],
                ),
            }
        )
    )

    ingestion = orchestrator.run_once()

    result = orchestrator.verify_queue(
        ingestion["verification_queue"],
        bridge=FakeVerificationBridge(),
        fee_rates={
            "htx": 0.002,
            "okx": 0.001,
        },
        starting_usdt_value=300.0,
    )

    assert result[
        "paper_only"
    ] is True

    assert result[
        "live_order_submitted"
    ] is False


def test_verification_failure_does_not_stop_queue():
    class SelectivelyFailingBridge:
        def __init__(self):
            self.calls = []

        def verify(
            self,
            candidate,
            starting_usdt_value,
            source_fee_rate,
            destination_fee_rate,
            max_slippage_percent=0.5,
            minimum_profit_percent=0.0,
        ):
            self.calls.append(
                candidate["opportunity_key"]
            )

            if (
                candidate["opportunity_key"]
                == "COTI:kucoin:bitget"
            ):
                raise RuntimeError(
                    "market unavailable"
                )

            return {
                **candidate,
                "arbos_verified": True,
                "executable": True,
                "verification_required": False,
                "verified_net_profit_percent": 1.5,
                "paper_only": True,
                "live_order_submitted": False,
            }

    orchestrator = (
        MultiSourceExternalIntelligenceOrchestrator(
            coordinators={
                "finder": FakeCoordinator(
                    "finder"
                ),
            }
        )
    )

    queue = [
        {
            "priority_rank": 1,
            "opportunity_key": "COTI:kucoin:bitget",
            "coin": "COTI",
            "buy_exchange": "kucoin",
            "sell_exchange": "bitget",
            "arbos_verified": False,
            "executable": False,
            "verification_required": True,
        },
        {
            "priority_rank": 2,
            "opportunity_key": "VANRY:bingx:kucoin",
            "coin": "VANRY",
            "buy_exchange": "bingx",
            "sell_exchange": "kucoin",
            "arbos_verified": False,
            "executable": False,
            "verification_required": True,
        },
    ]

    bridge = SelectivelyFailingBridge()

    result = orchestrator.verify_queue(
        queue,
        bridge=bridge,
        fee_rates={
            "kucoin": 0.001,
            "bitget": 0.001,
            "bingx": 0.001,
        },
        starting_usdt_value=300.0,
    )

    assert bridge.calls == [
        "COTI:kucoin:bitget",
        "VANRY:bingx:kucoin",
    ]

    assert result[
        "attempted_count"
    ] == 2

    assert result[
        "verified_count"
    ] == 1

    assert result[
        "failed_verification_count"
    ] == 1


def test_failed_verification_is_preserved_for_audit():
    class ExplodingBridge:
        def verify(self, *args, **kwargs):
            raise RuntimeError(
                "withdrawal unavailable"
            )

    orchestrator = (
        MultiSourceExternalIntelligenceOrchestrator(
            coordinators={
                "finder": FakeCoordinator(
                    "finder"
                ),
            }
        )
    )

    queue = [{
        "priority_rank": 1,
        "opportunity_key": "FLOW:htx:okx",
        "coin": "FLOW",
        "buy_exchange": "htx",
        "sell_exchange": "okx",
        "arbos_verified": False,
        "executable": False,
        "verification_required": True,
    }]

    result = orchestrator.verify_queue(
        queue,
        bridge=ExplodingBridge(),
        fee_rates={
            "htx": 0.002,
            "okx": 0.001,
        },
        starting_usdt_value=300.0,
    )

    assert result[
        "failed_verification_count"
    ] == 1

    failure = result[
        "verification_failures"
    ][0]

    assert failure[
        "opportunity_key"
    ] == "FLOW:htx:okx"

    assert failure[
        "priority_rank"
    ] == 1

    assert failure[
        "reason"
    ] == "verification_exception"

    assert (
        "withdrawal unavailable"
        in failure["error"]
    )


def test_failed_verification_is_never_marked_executable():
    class ExplodingBridge:
        def verify(self, *args, **kwargs):
            raise RuntimeError(
                "verification failed"
            )

    orchestrator = (
        MultiSourceExternalIntelligenceOrchestrator(
            coordinators={
                "finder": FakeCoordinator(
                    "finder"
                ),
            }
        )
    )

    queue = [{
        "priority_rank": 1,
        "opportunity_key": "FLOW:htx:okx",
        "coin": "FLOW",
        "buy_exchange": "htx",
        "sell_exchange": "okx",
        "arbos_verified": False,
        "executable": False,
        "verification_required": True,
    }]

    result = orchestrator.verify_queue(
        queue,
        bridge=ExplodingBridge(),
        fee_rates={
            "htx": 0.002,
            "okx": 0.001,
        },
        starting_usdt_value=300.0,
    )

    failure = result[
        "verification_failures"
    ][0]

    assert failure[
        "arbos_verified"
    ] is False

    assert failure[
        "executable"
    ] is False

    assert failure[
        "verification_required"
    ] is True


def test_verification_failure_result_remains_paper_safe():
    class ExplodingBridge:
        def verify(self, *args, **kwargs):
            raise RuntimeError("boom")

    orchestrator = (
        MultiSourceExternalIntelligenceOrchestrator(
            coordinators={
                "finder": FakeCoordinator(
                    "finder"
                ),
            }
        )
    )

    queue = [{
        "priority_rank": 1,
        "opportunity_key": "FLOW:htx:okx",
        "coin": "FLOW",
        "buy_exchange": "htx",
        "sell_exchange": "okx",
        "arbos_verified": False,
        "executable": False,
        "verification_required": True,
    }]

    result = orchestrator.verify_queue(
        queue,
        bridge=ExplodingBridge(),
        fee_rates={
            "htx": 0.002,
            "okx": 0.001,
        },
        starting_usdt_value=300.0,
    )

    assert result["paper_only"] is True
    assert result[
        "live_order_submitted"
    ] is False


def test_verification_queue_can_be_limited():
    orchestrator = (
        MultiSourceExternalIntelligenceOrchestrator(
            coordinators={
                "finder": FakeCoordinator(
                    "finder"
                ),
            }
        )
    )

    queue = [
        {
            "priority_rank": 1,
            "opportunity_key": "COTI:kucoin:bitget",
            "coin": "COTI",
            "buy_exchange": "kucoin",
            "sell_exchange": "bitget",
            "arbos_verified": False,
            "executable": False,
            "verification_required": True,
        },
        {
            "priority_rank": 2,
            "opportunity_key": "VANRY:bingx:kucoin",
            "coin": "VANRY",
            "buy_exchange": "bingx",
            "sell_exchange": "kucoin",
            "arbos_verified": False,
            "executable": False,
            "verification_required": True,
        },
        {
            "priority_rank": 3,
            "opportunity_key": "FLOW:htx:okx",
            "coin": "FLOW",
            "buy_exchange": "htx",
            "sell_exchange": "okx",
            "arbos_verified": False,
            "executable": False,
            "verification_required": True,
        },
    ]

    bridge = FakeVerificationBridge()

    result = orchestrator.verify_queue(
        queue,
        bridge=bridge,
        fee_rates={
            "kucoin": 0.001,
            "bitget": 0.001,
            "bingx": 0.001,
            "htx": 0.002,
            "okx": 0.001,
        },
        starting_usdt_value=300.0,
        max_opportunities=2,
    )

    assert result[
        "attempted_count"
    ] == 2

    assert len(
        bridge.calls
    ) == 2

    assert bridge.calls[0][
        "candidate"
    ][
        "priority_rank"
    ] == 1

    assert bridge.calls[1][
        "candidate"
    ][
        "priority_rank"
    ] == 2


def test_limit_reports_deferred_opportunities():
    orchestrator = (
        MultiSourceExternalIntelligenceOrchestrator(
            coordinators={
                "finder": FakeCoordinator(
                    "finder"
                ),
            }
        )
    )

    queue = [
        {
            "priority_rank": 1,
            "opportunity_key": "COTI:kucoin:bitget",
            "coin": "COTI",
            "buy_exchange": "kucoin",
            "sell_exchange": "bitget",
            "arbos_verified": False,
            "executable": False,
            "verification_required": True,
        },
        {
            "priority_rank": 2,
            "opportunity_key": "FLOW:htx:okx",
            "coin": "FLOW",
            "buy_exchange": "htx",
            "sell_exchange": "okx",
            "arbos_verified": False,
            "executable": False,
            "verification_required": True,
        },
    ]

    result = orchestrator.verify_queue(
        queue,
        bridge=FakeVerificationBridge(),
        fee_rates={
            "kucoin": 0.001,
            "bitget": 0.001,
            "htx": 0.002,
            "okx": 0.001,
        },
        starting_usdt_value=300.0,
        max_opportunities=1,
    )

    assert result[
        "deferred_count"
    ] == 1

    assert result[
        "deferred_opportunities"
    ][0][
        "opportunity_key"
    ] == "FLOW:htx:okx"


def test_no_limit_verifies_entire_queue():
    orchestrator = (
        MultiSourceExternalIntelligenceOrchestrator(
            coordinators={
                "finder": FakeCoordinator(
                    "finder"
                ),
            }
        )
    )

    queue = [
        {
            "priority_rank": 1,
            "opportunity_key": "COTI:kucoin:bitget",
            "coin": "COTI",
            "buy_exchange": "kucoin",
            "sell_exchange": "bitget",
            "arbos_verified": False,
            "executable": False,
            "verification_required": True,
        },
        {
            "priority_rank": 2,
            "opportunity_key": "FLOW:htx:okx",
            "coin": "FLOW",
            "buy_exchange": "htx",
            "sell_exchange": "okx",
            "arbos_verified": False,
            "executable": False,
            "verification_required": True,
        },
    ]

    result = orchestrator.verify_queue(
        queue,
        bridge=FakeVerificationBridge(),
        fee_rates={
            "kucoin": 0.001,
            "bitget": 0.001,
            "htx": 0.002,
            "okx": 0.001,
        },
        starting_usdt_value=300.0,
    )

    assert result[
        "attempted_count"
    ] == 2

    assert result[
        "deferred_count"
    ] == 0


def test_max_opportunities_must_be_positive():
    orchestrator = (
        MultiSourceExternalIntelligenceOrchestrator(
            coordinators={
                "finder": FakeCoordinator(
                    "finder"
                ),
            }
        )
    )

    with pytest.raises(
        ValueError,
        match="max_opportunities must be positive",
    ):
        orchestrator.verify_queue(
            [],
            bridge=FakeVerificationBridge(),
            fee_rates={},
            starting_usdt_value=300.0,
            max_opportunities=0,
        )
