"""
ArbOS™
EX-373 Stress Summary Reporter

Compact reporting for sustained public-feed stress tests.

Reporting only.
Paper safe.
No authentication.
No transfers.
No live orders.
"""


def build_stress_summary(
    *,
    requested_coins,
    cycles_per_symbol,
    runtime_status,
    exchange_ids,
    cycle_results,
):
    completed_updates = 0
    failed_updates = 0
    initial_failed_updates = 0
    recovery_attempts = 0
    recovered_updates = 0
    unrecovered_failures = 0

    for result in cycle_results:
        if isinstance(result, BaseException):
            failed_updates += 1
            unrecovered_failures += 1
            continue

        completed_updates += int(
            result.get("completed_updates", 0)
        )
        failed_updates += int(
            result.get("failed_updates", 0)
        )
        initial_failed_updates += int(
            result.get("initial_failed_updates", 0)
        )
        recovery_attempts += int(
            result.get("recovery_attempts", 0)
        )
        recovered_updates += int(
            result.get("recovered_updates", 0)
        )
        unrecovered_failures += int(
            result.get("unrecovered_failures", 0)
        )

    paper_only = bool(
        runtime_status.get("paper_only") is True
    )

    live_order_submitted = bool(
        runtime_status.get(
            "live_order_submitted",
            False,
        )
    )

    pending_routes = int(
        runtime_status.get(
            "pending_route_count",
            0,
        )
    )

    if (
        not paper_only
        or live_order_submitted
        or pending_routes != 0
    ):
        result = "FAIL"
    elif (
        failed_updates > 0
        or unrecovered_failures > 0
    ):
        result = "WARN"
    else:
        result = "PASS"

    return {
        "requested_coins": int(requested_coins),
        "cycles_per_symbol": int(
            cycles_per_symbol
        ),
        "exchange_count": int(
            runtime_status.get(
                "exchange_count",
                len(exchange_ids),
            )
        ),
        "exchanges": list(exchange_ids),
        "market_subscriptions": int(
            runtime_status.get(
                "symbol_count",
                0,
            )
        ),
        "registered_routes": int(
            runtime_status.get(
                "registered_route_count",
                0,
            )
        ),
        "pending_routes": pending_routes,
        "completed_updates": completed_updates,
        "failed_updates": failed_updates,
        "initial_failed_updates": (
            initial_failed_updates
        ),
        "recovery_attempts": recovery_attempts,
        "recovered_updates": recovered_updates,
        "unrecovered_failures": (
            unrecovered_failures
        ),
        "paper_only": paper_only,
        "live_order_submitted": (
            live_order_submitted
        ),
        "result": result,
    }


def render_stress_summary(summary):
    lines = [
        "=" * 60,
        " ArbOS™ EX-373 — FINAL STRESS TEST REPORT",
        "=" * 60,
        "",
        (
            f"{'Requested coins':30}"
            f"{summary['requested_coins']:>10}"
        ),
        (
            f"{'Cycles per symbol':30}"
            f"{summary['cycles_per_symbol']:>10}"
        ),
        (
            f"{'Exchanges':30}"
            f"{summary['exchange_count']:>10}"
        ),
        (
            f"{'Market subscriptions':30}"
            f"{summary['market_subscriptions']:>10}"
        ),
        (
            f"{'Registered routes':30}"
            f"{summary['registered_routes']:>10}"
        ),
        "",
        (
            f"{'Completed updates':30}"
            f"{summary['completed_updates']:>10}"
        ),
        (
            f"{'Initial failed updates':30}"
            f"{summary['initial_failed_updates']:>10}"
        ),
        (
            f"{'Recovery attempts':30}"
            f"{summary['recovery_attempts']:>10}"
        ),
        (
            f"{'Recovered updates':30}"
            f"{summary['recovered_updates']:>10}"
        ),
        (
            f"{'Final failed updates':30}"
            f"{summary['failed_updates']:>10}"
        ),
        (
            f"{'Unrecovered failures':30}"
            f"{summary['unrecovered_failures']:>10}"
        ),
        (
            f"{'Pending routes':30}"
            f"{summary['pending_routes']:>10}"
        ),
        "",
        (
            f"{'PAPER ONLY':30}"
            f"{str(summary['paper_only']).upper():>10}"
        ),
        (
            f"{'LIVE ORDERS SUBMITTED':30}"
            f"{str(summary['live_order_submitted']).upper():>10}"
        ),
        "",
        (
            f"{'RESULT':30}"
            f"{summary['result']:>10}"
        ),
        "=" * 60,
    ]

    return "\n".join(lines)
