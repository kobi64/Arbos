from core.ex374_feed_start_pressure_diagnostic import (
    EXCHANGE_IDS,
    POLICIES,
    REQUESTED_COINS,
    build_policy_summary,
)


def test_ex374_targets_residual_timeout_venues():
    assert EXCHANGE_IDS == [
        "gate",
        "coinex",
        "poloniex",
    ]


def test_ex374_uses_bounded_symbol_sample():
    assert REQUESTED_COINS == 30


def test_ex374_defines_pressure_and_controlled_policies():
    assert set(POLICIES) == {
        "pressure",
        "controlled",
    }

    assert POLICIES["pressure"] == {
        "batch_size": 30,
        "gap_seconds": 0.0,
        "retry_delay_seconds": 1.0,
    }

    assert POLICIES["controlled"] == {
        "batch_size": 5,
        "gap_seconds": 1.0,
        "retry_delay_seconds": 3.0,
    }


def test_policy_summary_reports_reliability_delta():
    pressure = {
        "final_success_percent": 80.0,
        "first_pass_failed": 8,
        "final_failed": 6,
    }

    controlled = {
        "final_success_percent": 96.0,
        "first_pass_failed": 3,
        "final_failed": 1,
    }

    result = build_policy_summary(
        exchange_id="gate",
        pressure=pressure,
        controlled=controlled,
    )

    assert result == {
        "exchange_id": "gate",
        "pressure_final_success_percent": 80.0,
        "controlled_final_success_percent": 96.0,
        "success_delta_percent": 16.0,
        "pressure_first_pass_failed": 8,
        "controlled_first_pass_failed": 3,
        "pressure_final_failed": 6,
        "controlled_final_failed": 1,
        "controlled_policy_improved": True,
        "paper_only": True,
        "live_order_submitted": False,
    }


def test_run_policy_batches_symbols_and_reports_failures():
    import asyncio

    from core.ex374_feed_start_pressure_diagnostic import (
        run_policy,
    )

    class FakeExchange:
        def __init__(self):
            self.calls = []
            self.attempts = {}

        async def watch_order_book(self, symbol):
            self.calls.append(symbol)

            count = self.attempts.get(symbol, 0) + 1
            self.attempts[symbol] = count

            if symbol == "ETH/USDT" and count == 1:
                raise TimeoutError()

            return {
                "bids": [[1.0, 1.0]],
                "asks": [[1.1, 1.0]],
            }

    exchange = FakeExchange()

    result = asyncio.run(
        run_policy(
            exchange=exchange,
            exchange_id="gate",
            symbols=[
                "BTC/USDT",
                "ETH/USDT",
                "SOL/USDT",
            ],
            batch_size=2,
            gap_seconds=0.0,
            retry_delay_seconds=0.0,
        )
    )

    assert result["exchange_id"] == "gate"
    assert result["symbol_count"] == 3
    assert result["first_pass_success"] == 2
    assert result["first_pass_failed"] == 1
    assert result["recovered_on_retry"] == 1
    assert result["final_success"] == 3
    assert result["final_failed"] == 0
    assert result["final_success_percent"] == 100.0
    assert result["final_error_counts"] == {}
    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False


def test_compare_policies_runs_both_profiles_and_builds_summary():
    import asyncio

    from core.ex374_feed_start_pressure_diagnostic import (
        compare_policies,
    )

    class FakeExchange:
        def __init__(self):
            self.calls = []

        async def watch_order_book(self, symbol):
            self.calls.append(symbol)

            return {
                "bids": [[1.0, 1.0]],
                "asks": [[1.1, 1.0]],
            }

    exchange = FakeExchange()

    result = asyncio.run(
        compare_policies(
            exchange=exchange,
            exchange_id="gate",
            symbols=[
                "BTC/USDT",
                "ETH/USDT",
                "SOL/USDT",
            ],
        )
    )

    assert result["exchange_id"] == "gate"

    assert result["pressure"][
        "final_success_percent"
    ] == 100.0

    assert result["controlled"][
        "final_success_percent"
    ] == 100.0

    assert result["summary"][
        "success_delta_percent"
    ] == 0.0

    assert result["summary"][
        "controlled_policy_improved"
    ] is False

    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False

    assert len(exchange.calls) == 6


def test_select_common_symbols_prefers_priority_assets_then_sorts_rest():
    from core.ex374_feed_start_pressure_diagnostic import (
        select_common_symbols,
    )

    markets = {
        "gate": {
            "BTC/USDT": {
                "spot": True,
                "active": True,
                "quote": "USDT",
                "base": "BTC",
            },
            "ETH/USDT": {
                "spot": True,
                "active": True,
                "quote": "USDT",
                "base": "ETH",
            },
            "ADA/USDT": {
                "spot": True,
                "active": True,
                "quote": "USDT",
                "base": "ADA",
            },
            "XYZ/USDT": {
                "spot": True,
                "active": True,
                "quote": "USDT",
                "base": "XYZ",
            },
        },
        "coinex": {
            "BTC/USDT": {
                "spot": True,
                "active": True,
                "quote": "USDT",
                "base": "BTC",
            },
            "ETH/USDT": {
                "spot": True,
                "active": True,
                "quote": "USDT",
                "base": "ETH",
            },
            "ADA/USDT": {
                "spot": True,
                "active": True,
                "quote": "USDT",
                "base": "ADA",
            },
            "XYZ/USDT": {
                "spot": True,
                "active": True,
                "quote": "USDT",
                "base": "XYZ",
            },
        },
        "poloniex": {
            "BTC/USDT": {
                "spot": True,
                "active": True,
                "quote": "USDT",
                "base": "BTC",
            },
            "ETH/USDT": {
                "spot": True,
                "active": True,
                "quote": "USDT",
                "base": "ETH",
            },
            "ADA/USDT": {
                "spot": True,
                "active": True,
                "quote": "USDT",
                "base": "ADA",
            },
            "XYZ/USDT": {
                "spot": True,
                "active": True,
                "quote": "USDT",
                "base": "XYZ",
            },
        },
    }

    result = select_common_symbols(
        market_maps=markets,
        requested_coins=3,
    )

    assert result == [
        "BTC/USDT",
        "ETH/USDT",
        "ADA/USDT",
    ]


def test_run_diagnostic_loads_markets_selects_common_symbols_and_compares():
    import asyncio

    from core.ex374_feed_start_pressure_diagnostic import (
        run_diagnostic,
    )

    class FakeExchange:
        def __init__(self):
            self.calls = []

        async def load_markets(self):
            return {
                "BTC/USDT": {
                    "spot": True,
                    "active": True,
                    "quote": "USDT",
                    "base": "BTC",
                },
                "ETH/USDT": {
                    "spot": True,
                    "active": True,
                    "quote": "USDT",
                    "base": "ETH",
                },
                "ADA/USDT": {
                    "spot": True,
                    "active": True,
                    "quote": "USDT",
                    "base": "ADA",
                },
            }

        async def watch_order_book(self, symbol):
            self.calls.append(symbol)

            return {
                "bids": [[1.0, 1.0]],
                "asks": [[1.1, 1.0]],
            }

    exchanges = {
        "gate": FakeExchange(),
        "coinex": FakeExchange(),
        "poloniex": FakeExchange(),
    }

    result = asyncio.run(
        run_diagnostic(
            exchanges=exchanges,
            requested_coins=3,
        )
    )

    assert result["symbols"] == [
        "BTC/USDT",
        "ETH/USDT",
        "ADA/USDT",
    ]

    assert set(result["venues"]) == {
        "gate",
        "coinex",
        "poloniex",
    }

    for exchange_id in [
        "gate",
        "coinex",
        "poloniex",
    ]:
        assert result["venues"][
            exchange_id
        ]["pressure"][
            "final_success_percent"
        ] == 100.0

        assert result["venues"][
            exchange_id
        ]["controlled"][
            "final_success_percent"
        ] == 100.0

    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False


def test_main_runs_diagnostic_and_closes_injected_exchanges():
    import asyncio

    from core.ex374_feed_start_pressure_diagnostic import (
        main,
    )

    class FakeExchange:
        def __init__(self):
            self.closed = False

        async def load_markets(self):
            return {
                "BTC/USDT": {
                    "spot": True,
                    "active": True,
                    "quote": "USDT",
                    "base": "BTC",
                },
            }

        async def watch_order_book(self, symbol):
            return {
                "bids": [[1.0, 1.0]],
                "asks": [[1.1, 1.0]],
            }

        async def close(self):
            self.closed = True

    exchanges = {
        "gate": FakeExchange(),
        "coinex": FakeExchange(),
        "poloniex": FakeExchange(),
    }

    result = asyncio.run(
        main(
            exchanges=exchanges,
            requested_coins=1,
        )
    )

    assert result["symbols"] == [
        "BTC/USDT",
    ]

    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False

    assert all(
        exchange.closed is True
        for exchange in exchanges.values()
    )


def test_run_sustained_rounds_reports_each_round_and_totals():
    import asyncio

    from core.ex374_feed_start_pressure_diagnostic import (
        run_sustained_rounds,
    )

    class FakeExchange:
        id = "poloniex"

        def __init__(self):
            self.calls = 0

        async def watch_order_book(
            self,
            symbol,
            limit=None,
        ):
            self.calls += 1

            if (
                symbol == "ETH/USDT"
                and self.calls == 4
            ):
                raise TimeoutError(
                    "simulated sustained timeout"
                )

            return {
                "bids": [[1.0, 1.0]],
                "asks": [[1.1, 1.0]],
            }

    exchange = FakeExchange()

    result = asyncio.run(
        run_sustained_rounds(
            exchange=exchange,
            exchange_id="poloniex",
            symbols=[
                "BTC/USDT",
                "ETH/USDT",
            ],
            rounds=3,
            cycle_timeout_seconds=1.0,
            round_gap_seconds=0.0,
            recovery_attempts=0,
        )
    )

    assert result["exchange_id"] == "poloniex"
    assert result["round_count"] == 3
    assert result["symbol_count"] == 2

    assert len(result["rounds"]) == 3

    assert result["rounds"][0]["failed_updates"] == 0
    assert result["rounds"][1]["failed_updates"] == 1
    assert result["rounds"][2]["failed_updates"] == 0

    assert result["total_completed_updates"] == 5
    assert result["total_failed_updates"] == 1

    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False


def test_run_sustained_diagnostic_runs_all_target_venues():
    import asyncio

    from core.ex374_feed_start_pressure_diagnostic import (
        run_sustained_diagnostic,
    )

    class FakeExchange:
        def __init__(self, exchange_id):
            self.id = exchange_id

        async def load_markets(self):
            return {
                "BTC/USDT": {
                    "spot": True,
                    "active": True,
                    "quote": "USDT",
                    "base": "BTC",
                },
                "ETH/USDT": {
                    "spot": True,
                    "active": True,
                    "quote": "USDT",
                    "base": "ETH",
                },
            }

        async def watch_order_book(
            self,
            symbol,
            limit=None,
        ):
            return {
                "bids": [[1.0, 1.0]],
                "asks": [[1.1, 1.0]],
            }

    exchanges = {
        exchange_id: FakeExchange(
            exchange_id
        )
        for exchange_id in [
            "gate",
            "coinex",
            "poloniex",
        ]
    }

    result = asyncio.run(
        run_sustained_diagnostic(
            exchanges=exchanges,
            requested_coins=2,
            rounds=3,
            cycle_timeout_seconds=1.0,
            round_gap_seconds=0.0,
            recovery_attempts=0,
        )
    )

    assert result["symbols"] == [
        "BTC/USDT",
        "ETH/USDT",
    ]

    assert set(result["venues"]) == {
        "gate",
        "coinex",
        "poloniex",
    }

    for exchange_id in result["venues"]:
        venue = result["venues"][
            exchange_id
        ]

        assert venue[
            "round_count"
        ] == 3

        assert venue[
            "total_completed_updates"
        ] == 6

        assert venue[
            "total_failed_updates"
        ] == 0

    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False


def test_should_restart_session_requires_venue_wide_failure():
    from core.ex374_feed_start_pressure_diagnostic import (
        should_restart_session,
    )

    assert (
        should_restart_session(
            symbol_count=30,
            failed_updates=30,
        )
        is True
    )

    assert (
        should_restart_session(
            symbol_count=30,
            failed_updates=16,
        )
        is True
    )

    assert (
        should_restart_session(
            symbol_count=30,
            failed_updates=15,
        )
        is True
    )

    assert (
        should_restart_session(
            symbol_count=30,
            failed_updates=4,
        )
        is False
    )

    assert (
        should_restart_session(
            symbol_count=30,
            failed_updates=9,
        )
        is False
    )

    assert (
        should_restart_session(
            symbol_count=6,
            failed_updates=3,
        )
        is False
    )



def test_run_rounds_with_session_replacement_replaces_degraded_session():
    import asyncio

    from core.ex374_feed_start_pressure_diagnostic import (
        run_rounds_with_session_replacement,
    )

    symbols = [
        f"COIN{i}/USDT"
        for i in range(10)
    ]

    class FakeExchange:
        id = "poloniex"

        def __init__(self, fail_first_round=False):
            self.fail_first_round = (
                fail_first_round
            )
            self.calls = 0
            self.closed = False

        async def load_markets(self):
            return {
                symbol: {
                    "spot": True,
                    "active": True,
                    "quote": "USDT",
                    "base": symbol.split("/")[0],
                }
                for symbol in symbols
            }

        async def watch_order_book(
            self,
            symbol,
            limit=None,
        ):
            self.calls += 1

            if (
                self.fail_first_round
                and self.calls <= 5
            ):
                raise TimeoutError(
                    "degraded session"
                )

            return {
                "bids": [[1.0, 1.0]],
                "asks": [[1.1, 1.0]],
            }

        async def close(self):
            self.closed = True

    created = []

    def exchange_factory():
        exchange = FakeExchange(
            fail_first_round=(
                len(created) == 0
            )
        )
        created.append(exchange)
        return exchange

    result = asyncio.run(
        run_rounds_with_session_replacement(
            exchange_factory=exchange_factory,
            exchange_id="poloniex",
            symbols=symbols,
            rounds=2,
            cycle_timeout_seconds=1.0,
            round_gap_seconds=0.0,
            recovery_attempts=0,
        )
    )

    assert result["exchange_id"] == "poloniex"
    assert result["round_count"] == 2
    assert result["session_restart_count"] == 1

    assert result["rounds"][0][
        "failed_updates"
    ] == 5

    assert result["rounds"][0][
        "session_restarted_after_round"
    ] is True

    assert result["rounds"][1][
        "failed_updates"
    ] == 0

    assert len(created) == 2
    assert created[0].closed is True
    assert created[1].closed is True

    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False


def test_classify_feed_health_separates_symbol_and_session_degradation():
    from core.ex374_feed_start_pressure_diagnostic import (
        classify_feed_health,
    )

    assert (
        classify_feed_health(
            symbol_count=30,
            failed_updates=0,
        )
        == "healthy"
    )

    assert (
        classify_feed_health(
            symbol_count=30,
            failed_updates=4,
        )
        == "symbol_degraded"
    )

    assert (
        classify_feed_health(
            symbol_count=30,
            failed_updates=5,
        )
        == "symbol_degraded"
    )

    assert (
        classify_feed_health(
            symbol_count=30,
            failed_updates=14,
        )
        == "symbol_degraded"
    )

    assert (
        classify_feed_health(
            symbol_count=30,
            failed_updates=15,
        )
        == "session_degraded"
    )

    assert (
        classify_feed_health(
            symbol_count=30,
            failed_updates=30,
        )
        == "session_degraded"
    )


def test_identify_persistently_failing_symbols_counts_across_rounds():
    from core.ex374_feed_start_pressure_diagnostic import (
        identify_persistently_failing_symbols,
    )

    rounds = [
        {
            "failures": [
                {"symbol": "FIL/USDT"},
                {"symbol": "INJ/USDT"},
                {"symbol": "ACT/USDT"},
            ]
        },
        {
            "failures": [
                {"symbol": "FIL/USDT"},
                {"symbol": "INJ/USDT"},
                {"symbol": "ACT/USDT"},
                {"symbol": "AEVO/USDT"},
            ]
        },
        {
            "failures": [
                {"symbol": "FIL/USDT"},
                {"symbol": "ACT/USDT"},
                {"symbol": "AEVO/USDT"},
            ]
        },
        {
            "failures": [
                {"symbol": "FIL/USDT"},
                {"symbol": "INJ/USDT"},
            ]
        },
    ]

    result = identify_persistently_failing_symbols(
        rounds=rounds,
        minimum_failed_rounds=3,
    )

    assert result == {
        "FIL/USDT": 4,
        "INJ/USDT": 3,
        "ACT/USDT": 3,
    }


def test_build_symbol_quarantine_marks_only_persistent_failures():
    from core.ex374_feed_start_pressure_diagnostic import (
        build_symbol_quarantine,
    )

    persistent = {
        "FIL/USDT": 5,
        "INJ/USDT": 4,
        "ACT/USDT": 3,
        "AEVO/USDT": 2,
    }

    result = build_symbol_quarantine(
        persistent_failures=persistent,
        minimum_failed_rounds=3,
    )

    assert result == {
        "FIL/USDT": {
            "failed_rounds": 5,
            "quarantined": True,
            "reason": "persistent_symbol_timeout",
        },
        "INJ/USDT": {
            "failed_rounds": 4,
            "quarantined": True,
            "reason": "persistent_symbol_timeout",
        },
        "ACT/USDT": {
            "failed_rounds": 3,
            "quarantined": True,
            "reason": "persistent_symbol_timeout",
        },
    }


def test_build_ex374_health_summary_combines_session_and_symbol_findings():
    from core.ex374_feed_start_pressure_diagnostic import (
        build_ex374_health_summary,
    )

    rounds = [
        {
            "failed_updates": 0,
            "failures": [],
        },
        {
            "failed_updates": 5,
            "failures": [
                {"symbol": "FIL/USDT"},
                {"symbol": "INJ/USDT"},
                {"symbol": "ACE/USDT"},
                {"symbol": "ACT/USDT"},
                {"symbol": "AEVO/USDT"},
            ],
        },
        {
            "failed_updates": 4,
            "failures": [
                {"symbol": "FIL/USDT"},
                {"symbol": "INJ/USDT"},
                {"symbol": "ACT/USDT"},
                {"symbol": "AEVO/USDT"},
            ],
        },
        {
            "failed_updates": 3,
            "failures": [
                {"symbol": "FIL/USDT"},
                {"symbol": "INJ/USDT"},
                {"symbol": "ACT/USDT"},
            ],
        },
    ]

    result = build_ex374_health_summary(
        symbol_count=30,
        rounds=rounds,
        minimum_failed_rounds=3,
    )

    assert result["feed_health"] == "symbol_degraded"

    assert result["persistent_failures"] == {
        "FIL/USDT": 3,
        "INJ/USDT": 3,
        "ACT/USDT": 3,
    }

    assert result["quarantine"] == {
        "FIL/USDT": {
            "failed_rounds": 3,
            "quarantined": True,
            "reason": "persistent_symbol_timeout",
        },
        "INJ/USDT": {
            "failed_rounds": 3,
            "quarantined": True,
            "reason": "persistent_symbol_timeout",
        },
        "ACT/USDT": {
            "failed_rounds": 3,
            "quarantined": True,
            "reason": "persistent_symbol_timeout",
        },
    }

    assert result["paper_only"] is True
    assert result["live_order_submitted"] is False
