"""
ArbOS™

EX-374
Exchange Feed Start Pressure Diagnostic

Diagnostic configuration and result comparison helpers.

Public market data only.
No authentication.
No transfers.
No live orders.
"""


EXCHANGE_IDS = [
    "gate",
    "coinex",
    "poloniex",
]


REQUESTED_COINS = 30


POLICIES = {
    "pressure": {
        "batch_size": 30,
        "gap_seconds": 0.0,
        "retry_delay_seconds": 1.0,
    },
    "controlled": {
        "batch_size": 5,
        "gap_seconds": 1.0,
        "retry_delay_seconds": 3.0,
    },
}


def build_policy_summary(
    exchange_id,
    pressure,
    controlled,
):
    pressure_success = float(
        pressure["final_success_percent"]
    )

    controlled_success = float(
        controlled["final_success_percent"]
    )

    return {
        "exchange_id": str(
            exchange_id
        ).strip().lower(),
        "pressure_final_success_percent": (
            pressure_success
        ),
        "controlled_final_success_percent": (
            controlled_success
        ),
        "success_delta_percent": round(
            controlled_success
            - pressure_success,
            2,
        ),
        "pressure_first_pass_failed": int(
            pressure["first_pass_failed"]
        ),
        "controlled_first_pass_failed": int(
            controlled["first_pass_failed"]
        ),
        "pressure_final_failed": int(
            pressure["final_failed"]
        ),
        "controlled_final_failed": int(
            controlled["final_failed"]
        ),
        "controlled_policy_improved": (
            controlled_success
            > pressure_success
        ),
        "paper_only": True,
        "live_order_submitted": False,
    }


import asyncio
import time


async def _watch_once(
    exchange,
    symbol,
):
    started = time.perf_counter()

    try:
        book = await exchange.watch_order_book(
            symbol
        )

        bids = (
            book.get("bids")
            if isinstance(book, dict)
            else None
        ) or []

        asks = (
            book.get("asks")
            if isinstance(book, dict)
            else None
        ) or []

        if not bids or not asks:
            raise ValueError(
                "order_book_unavailable"
            )

        return {
            "symbol": symbol,
            "success": True,
            "seconds": round(
                time.perf_counter()
                - started,
                4,
            ),
            "error_type": None,
            "error": None,
        }

    except Exception as exc:
        return {
            "symbol": symbol,
            "success": False,
            "seconds": round(
                time.perf_counter()
                - started,
                4,
            ),
            "error_type": type(exc).__name__,
            "error": str(exc),
        }


async def _run_batches(
    exchange,
    symbols,
    batch_size,
    gap_seconds,
):
    results = []

    for offset in range(
        0,
        len(symbols),
        batch_size,
    ):
        batch = symbols[
            offset:
            offset + batch_size
        ]

        batch_results = await asyncio.gather(
            *[
                _watch_once(
                    exchange,
                    symbol,
                )
                for symbol in batch
            ]
        )

        results.extend(
            batch_results
        )

        if (
            offset + batch_size
            < len(symbols)
            and gap_seconds > 0
        ):
            await asyncio.sleep(
                gap_seconds
            )

    return results


async def run_policy(
    exchange,
    exchange_id,
    symbols,
    batch_size,
    gap_seconds,
    retry_delay_seconds,
):
    first_pass = await _run_batches(
        exchange=exchange,
        symbols=symbols,
        batch_size=batch_size,
        gap_seconds=gap_seconds,
    )

    failed_symbols = [
        item["symbol"]
        for item in first_pass
        if item["success"] is not True
    ]

    successful_first = (
        len(first_pass)
        - len(failed_symbols)
    )

    retry_results = []

    if failed_symbols:
        if retry_delay_seconds > 0:
            await asyncio.sleep(
                retry_delay_seconds
            )

        retry_results = await _run_batches(
            exchange=exchange,
            symbols=failed_symbols,
            batch_size=max(
                1,
                min(
                    5,
                    batch_size,
                ),
            ),
            gap_seconds=1.0,
        )

    recovered_symbols = {
        item["symbol"]
        for item in retry_results
        if item["success"] is True
    }

    final_failures = [
        item
        for item in first_pass
        if (
            item["success"] is not True
            and item["symbol"]
            not in recovered_symbols
        )
    ]

    final_success = (
        successful_first
        + len(recovered_symbols)
    )

    error_counts = {}

    for item in final_failures:
        key = (
            item["error_type"]
            or "Unknown"
        )

        error_counts[key] = (
            error_counts.get(
                key,
                0,
            )
            + 1
        )

    symbol_count = len(symbols)

    return {
        "exchange_id": str(
            exchange_id
        ).strip().lower(),
        "symbol_count": symbol_count,
        "first_pass_success": (
            successful_first
        ),
        "first_pass_failed": (
            len(failed_symbols)
        ),
        "recovered_on_retry": (
            len(recovered_symbols)
        ),
        "final_success": (
            final_success
        ),
        "final_failed": (
            len(final_failures)
        ),
        "final_success_percent": round(
            (
                final_success
                / symbol_count
                * 100.0
            ),
            2,
        ),
        "final_error_counts": (
            error_counts
        ),
        "final_failures": (
            final_failures
        ),
        "paper_only": True,
        "live_order_submitted": False,
    }


async def compare_policies(
    exchange,
    exchange_id,
    symbols,
):
    pressure = await run_policy(
        exchange=exchange,
        exchange_id=exchange_id,
        symbols=symbols,
        **POLICIES["pressure"],
    )

    controlled = await run_policy(
        exchange=exchange,
        exchange_id=exchange_id,
        symbols=symbols,
        **POLICIES["controlled"],
    )

    summary = build_policy_summary(
        exchange_id=exchange_id,
        pressure=pressure,
        controlled=controlled,
    )

    return {
        "exchange_id": str(
            exchange_id
        ).strip().lower(),
        "pressure": pressure,
        "controlled": controlled,
        "summary": summary,
        "paper_only": True,
        "live_order_submitted": False,
    }


PREFERRED_COINS = [
    "BTC",
    "ETH",
    "SOL",
    "XRP",
    "DOGE",
    "ADA",
    "BNB",
    "TRX",
    "LINK",
    "LTC",
    "BCH",
    "DOT",
    "AVAX",
    "UNI",
    "ATOM",
    "ETC",
    "NEAR",
    "APT",
    "ARB",
    "OP",
    "FIL",
    "ICP",
    "AAVE",
    "SUI",
    "INJ",
    "TIA",
    "SEI",
    "TON",
    "XLM",
    "HBAR",
]


def _eligible_usdt_assets(
    markets,
):
    assets = set()

    for market in (
        markets or {}
    ).values():
        if market.get("spot") is not True:
            continue

        if market.get("active") is False:
            continue

        if str(
            market.get("quote")
            or ""
        ).upper() != "USDT":
            continue

        base = str(
            market.get("base")
            or ""
        ).strip().upper()

        if not base:
            continue

        if base in {
            "USDT",
            "USDC",
            "USD",
        }:
            continue

        if base.endswith(
            (
                "3L",
                "3S",
                "5L",
                "5S",
            )
        ):
            continue

        assets.add(
            base
        )

    return assets


def select_common_symbols(
    market_maps,
    requested_coins,
):
    eligible_sets = [
        _eligible_usdt_assets(
            markets
        )
        for markets in (
            market_maps or {}
        ).values()
    ]

    if not eligible_sets:
        return []

    common = set.intersection(
        *eligible_sets
    )

    selected = []

    for coin in PREFERRED_COINS:
        if (
            coin in common
            and coin not in selected
        ):
            selected.append(
                coin
            )

        if (
            len(selected)
            >= requested_coins
        ):
            break

    if (
        len(selected)
        < requested_coins
    ):
        for coin in sorted(
            common
        ):
            if coin in selected:
                continue

            selected.append(
                coin
            )

            if (
                len(selected)
                >= requested_coins
            ):
                break

    return [
        f"{coin}/USDT"
        for coin in selected
    ]


async def run_diagnostic(
    exchanges,
    requested_coins=REQUESTED_COINS,
):
    market_maps = {}

    for exchange_id in EXCHANGE_IDS:
        exchange = exchanges[
            exchange_id
        ]

        market_maps[
            exchange_id
        ] = await exchange.load_markets()

    symbols = select_common_symbols(
        market_maps=market_maps,
        requested_coins=requested_coins,
    )

    venue_results = {}

    for exchange_id in EXCHANGE_IDS:
        venue_results[
            exchange_id
        ] = await compare_policies(
            exchange=exchanges[
                exchange_id
            ],
            exchange_id=exchange_id,
            symbols=symbols,
        )

    return {
        "symbols": symbols,
        "venues": venue_results,
        "paper_only": True,
        "live_order_submitted": False,
    }


async def main(
    exchanges=None,
    requested_coins=REQUESTED_COINS,
):
    created_exchanges = False

    if exchanges is None:
        import ccxt.pro as ccxtpro

        exchanges = {
            exchange_id: getattr(
                ccxtpro,
                exchange_id,
            )({
                "enableRateLimit": True,
            })
            for exchange_id in EXCHANGE_IDS
        }

        created_exchanges = True

    try:
        result = await run_diagnostic(
            exchanges=exchanges,
            requested_coins=requested_coins,
        )

        return result

    finally:
        await asyncio.gather(
            *[
                exchange.close()
                for exchange
                in exchanges.values()
            ],
            return_exceptions=True,
        )


if __name__ == "__main__":
    import json

    result = asyncio.run(
        main()
    )

    print(
        json.dumps(
            result,
            indent=2,
            sort_keys=True,
        )
    )


async def run_sustained_rounds(
    exchange,
    exchange_id,
    symbols,
    rounds,
    cycle_timeout_seconds,
    round_gap_seconds,
    recovery_attempts,
):
    from core.ccxt_pro_live_order_book_feed import (
        CCXTProLiveOrderBookFeed,
    )
    from core.ccxt_pro_multi_symbol_feed_manager import (
        CCXTProMultiSymbolFeedManager,
    )

    if rounds <= 0:
        raise ValueError(
            "rounds must be positive"
        )

    class DiagnosticIntake:
        def submit(self, snapshot):
            return {
                "accepted": True,
                "snapshot": snapshot,
            }

    feed = CCXTProLiveOrderBookFeed(
        exchange=exchange,
        intake_service=DiagnosticIntake(),
    )

    manager = CCXTProMultiSymbolFeedManager(
        feed=feed,
        exchange=exchange,
        symbols=symbols,
        retry_delay_seconds=0.0,
        cycle_timeout_seconds=(
            cycle_timeout_seconds
        ),
        recovery_attempts=(
            recovery_attempts
        ),
        recovery_delay_seconds=0.0,
    )

    round_results = []

    total_completed_updates = 0
    total_failed_updates = 0

    for round_number in range(
        1,
        rounds + 1,
    ):
        result = await manager.run_cycles(
            cycles_per_symbol=1
        )

        record = dict(result)
        record["round_number"] = (
            round_number
        )

        round_results.append(
            record
        )

        total_completed_updates += int(
            result["completed_updates"]
        )

        total_failed_updates += int(
            result["failed_updates"]
        )

        if (
            round_number < rounds
            and round_gap_seconds > 0
        ):
            await asyncio.sleep(
                round_gap_seconds
            )

    return {
        "exchange_id": str(
            exchange_id
        ).strip().lower(),
        "round_count": rounds,
        "symbol_count": len(symbols),
        "rounds": round_results,
        "total_completed_updates": (
            total_completed_updates
        ),
        "total_failed_updates": (
            total_failed_updates
        ),
        "paper_only": True,
        "live_order_submitted": False,
    }


async def run_sustained_diagnostic(
    exchanges,
    requested_coins=REQUESTED_COINS,
    rounds=3,
    cycle_timeout_seconds=20.0,
    round_gap_seconds=0.0,
    recovery_attempts=0,
):
    market_maps = {}

    for exchange_id in EXCHANGE_IDS:
        market_maps[
            exchange_id
        ] = await exchanges[
            exchange_id
        ].load_markets()

    symbols = select_common_symbols(
        market_maps=market_maps,
        requested_coins=requested_coins,
    )

    venue_results = {}

    for exchange_id in EXCHANGE_IDS:
        venue_results[
            exchange_id
        ] = await run_sustained_rounds(
            exchange=exchanges[
                exchange_id
            ],
            exchange_id=exchange_id,
            symbols=symbols,
            rounds=rounds,
            cycle_timeout_seconds=(
                cycle_timeout_seconds
            ),
            round_gap_seconds=(
                round_gap_seconds
            ),
            recovery_attempts=(
                recovery_attempts
            ),
        )

    return {
        "symbols": symbols,
        "venues": venue_results,
        "paper_only": True,
        "live_order_submitted": False,
    }


def should_restart_session(
    symbol_count,
    failed_updates,
):
    symbol_count = int(symbol_count)
    failed_updates = int(failed_updates)

    if symbol_count <= 0:
        return False

    if failed_updates < 5:
        return False

    failure_ratio = (
        failed_updates
        / symbol_count
    )

    return failure_ratio >= 0.5


async def run_rounds_with_session_replacement(
    exchange_factory,
    exchange_id,
    symbols,
    rounds,
    cycle_timeout_seconds,
    round_gap_seconds,
    recovery_attempts,
):
    if rounds <= 0:
        raise ValueError(
            "rounds must be positive"
        )

    exchange = None
    round_results = []

    session_restart_count = 0
    total_completed_updates = 0
    total_failed_updates = 0

    try:
        exchange = exchange_factory()

        await exchange.load_markets()

        for round_number in range(
            1,
            rounds + 1,
        ):
            result = await run_sustained_rounds(
                exchange=exchange,
                exchange_id=exchange_id,
                symbols=symbols,
                rounds=1,
                cycle_timeout_seconds=(
                    cycle_timeout_seconds
                ),
                round_gap_seconds=0.0,
                recovery_attempts=(
                    recovery_attempts
                ),
            )

            record = dict(
                result["rounds"][0]
            )

            record["round_number"] = (
                round_number
            )

            restart_required = (
                should_restart_session(
                    symbol_count=len(symbols),
                    failed_updates=record[
                        "failed_updates"
                    ],
                )
            )

            record[
                "session_restarted_after_round"
            ] = restart_required

            round_results.append(
                record
            )

            total_completed_updates += int(
                record["completed_updates"]
            )

            total_failed_updates += int(
                record["failed_updates"]
            )

            if (
                restart_required
                and round_number < rounds
            ):
                await exchange.close()

                exchange = exchange_factory()

                await exchange.load_markets()

                session_restart_count += 1

            if (
                round_number < rounds
                and round_gap_seconds > 0
            ):
                await asyncio.sleep(
                    round_gap_seconds
                )

        return {
            "exchange_id": str(
                exchange_id
            ).strip().lower(),
            "round_count": rounds,
            "symbol_count": len(symbols),
            "rounds": round_results,
            "session_restart_count": (
                session_restart_count
            ),
            "total_completed_updates": (
                total_completed_updates
            ),
            "total_failed_updates": (
                total_failed_updates
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

    finally:
        if exchange is not None:
            await exchange.close()


def classify_feed_health(
    symbol_count,
    failed_updates,
):
    symbol_count = int(symbol_count)
    failed_updates = int(failed_updates)

    if symbol_count <= 0:
        return "healthy"

    if failed_updates <= 0:
        return "healthy"

    if should_restart_session(
        symbol_count=symbol_count,
        failed_updates=failed_updates,
    ):
        return "session_degraded"

    return "symbol_degraded"


def identify_persistently_failing_symbols(
    rounds,
    minimum_failed_rounds,
):
    minimum_failed_rounds = int(
        minimum_failed_rounds
    )

    counts = {}

    for round_result in rounds or []:
        seen_this_round = set()

        for failure in (
            round_result.get("failures")
            or []
        ):
            symbol = str(
                failure.get("symbol")
                or ""
            ).strip().upper()

            if not symbol:
                continue

            seen_this_round.add(
                symbol
            )

        for symbol in seen_this_round:
            counts[symbol] = (
                counts.get(symbol, 0)
                + 1
            )

    return {
        symbol: count
        for symbol, count
        in counts.items()
        if count >= minimum_failed_rounds
    }


def build_symbol_quarantine(
    persistent_failures,
    minimum_failed_rounds,
):
    minimum_failed_rounds = int(
        minimum_failed_rounds
    )

    result = {}

    for symbol, failed_rounds in (
        persistent_failures or {}
    ).items():
        failed_rounds = int(
            failed_rounds
        )

        if (
            failed_rounds
            < minimum_failed_rounds
        ):
            continue

        result[
            str(symbol).strip().upper()
        ] = {
            "failed_rounds": failed_rounds,
            "quarantined": True,
            "reason": (
                "persistent_symbol_timeout"
            ),
        }

    return result


def build_ex374_health_summary(
    symbol_count,
    rounds,
    minimum_failed_rounds,
):
    rounds = list(
        rounds or []
    )

    latest_failed_updates = 0

    if rounds:
        latest_failed_updates = int(
            rounds[-1].get(
                "failed_updates",
                0,
            )
        )

    feed_health = classify_feed_health(
        symbol_count=symbol_count,
        failed_updates=latest_failed_updates,
    )

    persistent_failures = (
        identify_persistently_failing_symbols(
            rounds=rounds,
            minimum_failed_rounds=(
                minimum_failed_rounds
            ),
        )
    )

    quarantine = build_symbol_quarantine(
        persistent_failures=(
            persistent_failures
        ),
        minimum_failed_rounds=(
            minimum_failed_rounds
        ),
    )

    return {
        "feed_health": feed_health,
        "persistent_failures": (
            persistent_failures
        ),
        "quarantine": quarantine,
        "paper_only": True,
        "live_order_submitted": False,
    }
