from core.ex373_stress_summary_reporter import (
    build_stress_summary,
    render_stress_summary,
)


def _runtime_status():
    return {
        "exchange_count": 9,
        "exchanges": [
            "binance",
            "bitget",
            "bybit",
            "coinex",
            "gate",
            "kucoin",
            "okx",
            "poloniex",
            "xt",
        ],
        "symbol_count": 543,
        "pending_route_count": 0,
        "registered_route_count": 3274,
        "paper_only": True,
        "live_order_submitted": False,
    }


def _cycle_results():
    return [
        {
            "symbol_count": 60,
            "completed_updates": 300,
            "failed_updates": 0,
            "initial_failed_updates": 2,
            "recovery_attempts": 2,
            "recovered_updates": 2,
            "unrecovered_failures": 0,
            "paper_only": True,
            "live_order_submitted": False,
        },
        {
            "symbol_count": 40,
            "completed_updates": 198,
            "failed_updates": 2,
            "initial_failed_updates": 3,
            "recovery_attempts": 1,
            "recovered_updates": 1,
            "unrecovered_failures": 2,
            "paper_only": True,
            "live_order_submitted": False,
        },
    ]


def test_build_summary_aggregates_results():
    summary = build_stress_summary(
        requested_coins=100,
        cycles_per_symbol=5,
        runtime_status=_runtime_status(),
        exchange_ids=["binance", "xt"],
        cycle_results=_cycle_results(),
    )

    assert summary["requested_coins"] == 100
    assert summary["exchange_count"] == 9
    assert summary["market_subscriptions"] == 543
    assert summary["registered_routes"] == 3274
    assert summary["pending_routes"] == 0
    assert summary["completed_updates"] == 498
    assert summary["failed_updates"] == 2
    assert summary["initial_failed_updates"] == 5
    assert summary["recovery_attempts"] == 3
    assert summary["recovered_updates"] == 3
    assert summary["unrecovered_failures"] == 2


def test_summary_is_paper_safe():
    summary = build_stress_summary(
        requested_coins=100,
        cycles_per_symbol=5,
        runtime_status=_runtime_status(),
        exchange_ids=["binance", "xt"],
        cycle_results=_cycle_results(),
    )

    assert summary["paper_only"] is True
    assert summary["live_order_submitted"] is False


def test_summary_passes_when_runtime_drains_and_no_final_failures():
    results = _cycle_results()
    results[1]["failed_updates"] = 0
    results[1]["unrecovered_failures"] = 0

    summary = build_stress_summary(
        requested_coins=100,
        cycles_per_symbol=5,
        runtime_status=_runtime_status(),
        exchange_ids=["binance", "xt"],
        cycle_results=results,
    )

    assert summary["result"] == "PASS"


def test_summary_warns_when_feed_failures_remain():
    summary = build_stress_summary(
        requested_coins=100,
        cycles_per_symbol=5,
        runtime_status=_runtime_status(),
        exchange_ids=["binance", "xt"],
        cycle_results=_cycle_results(),
    )

    assert summary["result"] == "WARN"


def test_summary_fails_if_routes_remain_pending():
    status = _runtime_status()
    status["pending_route_count"] = 7

    summary = build_stress_summary(
        requested_coins=100,
        cycles_per_symbol=5,
        runtime_status=status,
        exchange_ids=["binance", "xt"],
        cycle_results=[],
    )

    assert summary["result"] == "FAIL"


def test_summary_fails_if_live_order_flag_is_true():
    status = _runtime_status()
    status["live_order_submitted"] = True

    summary = build_stress_summary(
        requested_coins=100,
        cycles_per_symbol=5,
        runtime_status=status,
        exchange_ids=["binance"],
        cycle_results=[],
    )

    assert summary["result"] == "FAIL"


def test_render_contains_compact_final_report():
    summary = build_stress_summary(
        requested_coins=100,
        cycles_per_symbol=5,
        runtime_status=_runtime_status(),
        exchange_ids=["binance", "xt"],
        cycle_results=_cycle_results(),
    )

    rendered = render_stress_summary(summary)

    assert "FINAL STRESS TEST REPORT" in rendered
    assert "Requested coins" in rendered
    assert "Market subscriptions" in rendered
    assert "Registered routes" in rendered
    assert "Completed updates" in rendered
    assert "Pending routes" in rendered
    assert "PAPER ONLY" in rendered
    assert "WARN" in rendered


def test_cancelled_cycle_result_is_counted_as_unrecovered_failure():
    import asyncio

    from core.ex373_stress_summary_reporter import (
        build_stress_summary,
    )

    summary = build_stress_summary(
        requested_coins=100,
        cycles_per_symbol=5,
        runtime_status={
            "exchange_count": 9,
            "symbol_count": 543,
            "registered_route_count": 3274,
            "pending_route_count": 0,
            "paper_only": True,
            "live_order_submitted": False,
        },
        exchange_ids=[
            "kucoin",
            "bitget",
            "gate",
            "xt",
            "coinex",
            "poloniex",
            "okx",
            "bybit",
            "binance",
        ],
        cycle_results=[
            asyncio.CancelledError()
        ],
    )

    assert summary["failed_updates"] == 1
    assert summary["unrecovered_failures"] == 1
    assert summary["result"] == "WARN"


def test_cancelled_error_is_not_an_exception_subclass():
    import asyncio

    cancelled = asyncio.CancelledError()

    assert not isinstance(
        cancelled,
        Exception,
    )
    assert isinstance(
        cancelled,
        BaseException,
    )
