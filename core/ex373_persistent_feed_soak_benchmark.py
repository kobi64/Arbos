"""
ArbOS™
EX-373
Multi-Exchange Event-Driven Benchmark

Venue-aware discovery and route construction for the
multi-exchange public paper scanner.

Paper only.
No authentication.
No transfers.
No live orders.
"""

import ccxt.pro as ccxtpro

from core.ccxt_future_lifecycle_guard import (
    install_ccxt_future_lifecycle_guard,
)
from core.ccxt_spawn_lifecycle_guard import (
    install_ccxt_spawn_lifecycle_guard,
)

from core.event_driven_shared_cache_scan_engine import (
    EventDrivenSharedCacheScanEngine,
)
from core.event_driven_public_feed_runtime import (
    EventDrivenPublicFeedRuntime,
)
from core.queued_cross_exchange_shared_cache_route_worker import (
    QueuedCrossExchangeSharedCacheRouteWorker,
)
from core.persistent_route_worker_pool import (
    PersistentRouteWorkerPool,
)
from exchanges.order_retry_backoff_policy import (
    OrderRetryBackoffPolicy,
)
from core.scanner_health_monitor import (
    ScannerHealthMonitor,
)
from core.exchange_connectivity_supervisor import (
    ExchangeConnectivitySupervisor,
)
from core.live_feed_health_supervisor import (
    LiveFeedHealthSupervisor,
)


REQUESTED_COINS = 100
WORKER_COUNT = 16
STARTING_VALUE = 100.0
CYCLES_PER_SYMBOL = 5

# Persistent soak configuration.
# These values are benchmark-local and do not claim
# verified production-profile status.
SOAK_DURATION_SECONDS = 120.0
HEALTH_SNAPSHOT_INTERVAL_SECONDS = 30.0

BENCHMARK_HEARTBEAT_TIMEOUT_SECONDS = {
    "kucoin": 30.0,
    "bitget": 30.0,
    "gate": 30.0,
    "xt": 60.0,
    "coinex": 30.0,
    "poloniex": 30.0,
    "okx": 30.0,
    "bybit": 30.0,
    "binance": 30.0,
}
BENCHMARK_MAX_LATENCY_MS = 1000.0

PER_EXCHANGE_LIMIT = 100

CYCLE_TIMEOUT_SECONDS = {
    "binance": 30.0,
    "kucoin": 20.0,
    "xt": 30.0,
}

SUBSCRIPTION_START_STAGGER_SECONDS = {
    "binance": 0.5,
    "bitget": 0.10,
    "gate": 0.10,
    "kucoin": 0.25,
    "poloniex": 0.10,
    "xt": 1.00,
}

MAX_CONCURRENT_SYMBOL_STARTS = {
    "kucoin": 4,
    "bitget": 6,
    "gate": 4,
    "xt": 2,
    "coinex": 6,
    "poloniex": 4,
    "okx": 8,
    "bybit": 6,
    "binance": 3,
}

EXCHANGE_IDS = [
    "kucoin",
    "bitget",
    "gate",
    "xt",
    "coinex",
    "poloniex",
    "okx",
    "bybit",
    "binance",
]

RECOVERY_ATTEMPTS = {
    exchange_id: (
        2
        if exchange_id == "kucoin"
        else 1
    )
    for exchange_id in EXCHANGE_IDS
}

RECOVERY_DELAY_SECONDS = {
    exchange_id: 1.0
    for exchange_id in EXCHANGE_IDS
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


def create_exchanges():
    return {
        exchange_id: getattr(
            ccxtpro,
            exchange_id,
        )({
            "enableRateLimit": True,
        })
        for exchange_id in EXCHANGE_IDS
    }


async def load_active_usdt_assets(exchange):
    markets = await exchange.load_markets()

    assets = set()

    for market in markets.values():
        if not market:
            continue

        if market.get("quote") != "USDT":
            continue

        if market.get("spot") is not True:
            continue

        if market.get("active") is False:
            continue

        base = market.get("base")

        if base:
            assets.add(
                str(base).upper()
            )

    return assets


def build_asset_venues(asset_sets):
    result = {}

    for exchange_id, assets in asset_sets.items():
        for asset in assets:
            result.setdefault(
                asset,
                set(),
            ).add(exchange_id)

    return result


def select_shared_coins(
    asset_venues,
    requested=REQUESTED_COINS,
):
    eligible = {
        coin
        for coin, venues in asset_venues.items()
        if len(venues) >= 2
    }

    selected = []

    for coin in PREFERRED_COINS:
        if coin in eligible:
            selected.append(coin)

    for coin in sorted(eligible):
        if coin not in selected:
            selected.append(coin)

        if len(selected) >= requested:
            break

    return selected[:requested]


def build_exchange_symbols(
    selected,
    asset_sets,
):
    return {
        exchange_id: [
            f"{coin}/USDT"
            for coin in selected
            if coin in assets
        ]
        for exchange_id, assets
        in asset_sets.items()
    }


def build_bounded_exchange_symbols(
    exchange_symbols,
    per_exchange_limit,
):
    if per_exchange_limit <= 0:
        raise ValueError(
            "per_exchange_limit must be positive"
        )

    return {
        exchange_id: list(symbols)[
            :per_exchange_limit
        ]
        for exchange_id, symbols
        in exchange_symbols.items()
    }


def build_bounded_route_pairs(
    exchange_symbols,
):
    asset_venues = {}

    for exchange_id, symbols in (
        exchange_symbols.items()
    ):
        for symbol in symbols:
            coin = str(symbol).split(
                "/",
                1,
            )[0].strip().upper()

            if not coin:
                continue

            asset_venues.setdefault(
                coin,
                set(),
            ).add(exchange_id)

    routes = []

    for coin, venues in (
        asset_venues.items()
    ):
        ordered_venues = sorted(
            venues
        )

        if len(ordered_venues) < 2:
            continue

        for source in ordered_venues:
            for destination in ordered_venues:
                if source == destination:
                    continue

                routes.append(
                    (
                        source,
                        destination,
                        coin,
                    )
                )

    return routes


def build_route_pairs(
    selected,
    asset_venues,
):
    routes = []

    for coin in selected:
        venues = sorted(
            asset_venues.get(
                coin,
                set(),
            )
        )

        for source in venues:
            for destination in venues:
                if source == destination:
                    continue

                routes.append(
                    (
                        source,
                        destination,
                        coin,
                    )
                )

    return routes


async def discover_topology(exchanges):
    asset_sets = {}

    for exchange_id, exchange in exchanges.items():
        asset_sets[exchange_id] = (
            await load_active_usdt_assets(
                exchange
            )
        )

    asset_venues = build_asset_venues(
        asset_sets
    )

    selected = select_shared_coins(
        asset_venues
    )

    exchange_symbols = (
        build_exchange_symbols(
            selected,
            asset_sets,
        )
    )

    route_pairs = build_route_pairs(
        selected,
        asset_venues,
    )

    return {
        "asset_sets": asset_sets,
        "asset_venues": asset_venues,
        "selected": selected,
        "exchange_symbols": exchange_symbols,
        "route_pairs": route_pairs,
    }


async def main():
    import asyncio
    import time
    import ccxt.pro as ccxtpro

    print("==============================================")
    print(" ArbOS EX-373 — 100-COIN NINE-EXCHANGE SCALING BENCHMARK")
    print("==============================================")
    print("LIVE TRADING: DISABLED")
    print("PUBLIC DATA ONLY")
    print()

    install_ccxt_future_lifecycle_guard()

    exchanges = {
        exchange_id: (
            install_ccxt_spawn_lifecycle_guard(
                getattr(
                    ccxtpro,
                    exchange_id,
                )({
                    "enableRateLimit": True,
                })
            )
        )
        for exchange_id in EXCHANGE_IDS
    }

    started = time.perf_counter()

    try:
        print("Discovering venue topology...")

        topology = await discover_topology(
            exchanges
        )

        selected = topology["selected"]
        exchange_symbols = (
            topology["exchange_symbols"]
        )
        route_pairs = topology["route_pairs"]

        print(
            "Exchange count:",
            len(exchanges),
        )
        print(
            "Selected shared coins:",
            len(selected),
        )
        print(
            "Directed route pairs:",
            len(route_pairs),
        )

        print()
        print("=== VENUE SYMBOL COUNTS ===")

        for exchange_id in EXCHANGE_IDS:
            print(
                f"{exchange_id:12}",
                len(
                    exchange_symbols.get(
                        exchange_id,
                        []
                    )
                ),
            )

        print()
        print(
            "Discovery seconds:",
            round(
                time.perf_counter()
                - started,
                3,
            ),
        )

        print()
        print(
            "EX-373 topology discovery completed."
        )

        bounded_symbols = (
            build_bounded_exchange_symbols(
                exchange_symbols,
                per_exchange_limit=PER_EXCHANGE_LIMIT,
            )
        )

        # EX-373 feed-health exclusion:
        # XT advertises AAPLX/USDT as active spot,
        # but isolated CCXT Pro order-book testing
        # produced no snapshot within 30 seconds.
        if "xt" in bounded_symbols:
            bounded_symbols["xt"] = [
                symbol
                for symbol in bounded_symbols["xt"]
                if symbol != "AAPLX/USDT"
            ]

        # EX-373 feed-health exclusion:
        # KuCoin advertises AMP/USDT as active spot,
        # but isolated CCXT Pro order-book testing
        # produced no snapshot within 30 seconds.
        if "kucoin" in bounded_symbols:
            bounded_symbols["kucoin"] = [
                symbol
                for symbol in bounded_symbols["kucoin"]
                if symbol != "AMP/USDT"
            ]

        bounded_route_pairs = (
            build_bounded_route_pairs(
                bounded_symbols
            )
        )

        engine = (
            EventDrivenSharedCacheScanEngine(
                worker_factory=(
                    QueuedCrossExchangeSharedCacheRouteWorker
                ),
                worker_count=WORKER_COUNT,
                max_queue_size=100000,
            )
        )

        for (
            source_exchange,
            destination_exchange,
            coin,
        ) in bounded_route_pairs:
            symbol = f"{coin}/USDT"

            engine.register_route(
                {
                    "route_id": (
                        f"{source_exchange.upper()}-"
                        f"{destination_exchange.upper()}-"
                        f"{coin}"
                    ),
                    "route_type": "cross_exchange",
                    "exchange_id": (
                        source_exchange
                    ),
                    "source_exchange": (
                        source_exchange
                    ),
                    "destination_exchange": (
                        destination_exchange
                    ),
                    "symbol": symbol,
                    "starting_value": (
                        STARTING_VALUE
                    ),
                    "source_fee_rate": 0.001,
                    "destination_fee_rate": 0.001,
                    "legs": [
                        {
                            "exchange_id": (
                                source_exchange
                            ),
                            "symbol": symbol,
                            "side": "buy",
                        },
                        {
                            "exchange_id": (
                                destination_exchange
                            ),
                            "symbol": symbol,
                            "side": "sell",
                        },
                    ],
                    "paper_only": True,
                    "live_order_submitted": False,
                }
            )

        health_supervisors = {}
        scanner_health_monitors = {}

        for exchange_id in EXCHANGE_IDS:
            heartbeat_timeout = (
                BENCHMARK_HEARTBEAT_TIMEOUT_SECONDS[
                    exchange_id
                ]
            )

            scanner_health_monitor = (
                ScannerHealthMonitor(
                    heartbeat_timeout_seconds=(
                        heartbeat_timeout
                    ),
                    max_latency_ms=(
                        BENCHMARK_MAX_LATENCY_MS
                    ),
                )
            )

            scanner_health_monitors[
                exchange_id
            ] = scanner_health_monitor

            connectivity_supervisor = (
                ExchangeConnectivitySupervisor(
                    disconnect_timeout_seconds=(
                        heartbeat_timeout
                    ),
                    max_latency_ms=(
                        BENCHMARK_MAX_LATENCY_MS
                    ),
                )
            )

            health_supervisors[
                exchange_id
            ] = LiveFeedHealthSupervisor(
                scanner_health_monitor=(
                    scanner_health_monitor
                ),
                connectivity_supervisor=(
                    connectivity_supervisor
                ),
            )

        backoff_policies = {
            exchange_id: (
                OrderRetryBackoffPolicy(
                    base_delay_seconds=1.0,
                    max_delay_seconds=30.0,
                )
            )
            for exchange_id in EXCHANGE_IDS
        }

        order_book_limits = {
            "bybit": 50,
        }

        runtime = (
            EventDrivenPublicFeedRuntime(
                engine=engine,
                exchanges=exchanges,
                exchange_symbols=(
                    bounded_symbols
                ),
                health_supervisors=(
                    health_supervisors
                ),
                backoff_policies=(
                    backoff_policies
                ),
                order_book_limits=(
                    order_book_limits
                ),
                cycle_timeout_seconds=(
                    CYCLE_TIMEOUT_SECONDS
                ),
                subscription_start_stagger_seconds=(
                    SUBSCRIPTION_START_STAGGER_SECONDS
                ),
                max_concurrent_symbol_starts=(
                    MAX_CONCURRENT_SYMBOL_STARTS
                ),
                recovery_attempts=(
                    RECOVERY_ATTEMPTS
                ),
                recovery_delay_seconds=(
                    RECOVERY_DELAY_SECONDS
                ),
            )
        )

        print()
        print(
            "=== BOUNDED WEBSOCKET TEST ==="
        )
        print(
            "Registered routes:",
            len(bounded_route_pairs),
        )
        print(
            "Subscribed symbols:",
            sum(
                len(symbols)
                for symbols
                in bounded_symbols.values()
            ),
        )

        managers = runtime.managers

        print()
        print(
            "=== PERSISTENT FEED SOAK TEST ==="
        )
        print(
            "Soak duration seconds:",
            SOAK_DURATION_SECONDS,
        )
        print(
            "Health snapshot interval seconds:",
            HEALTH_SNAPSHOT_INTERVAL_SECONDS,
        )

        persistent_route_pool = (
            PersistentRouteWorkerPool(
                worker_count=WORKER_COUNT,
                work_queue=(
                    engine.work_queue
                ),
                market_cache=(
                    engine.market_cache
                ),
                route_registry=(
                    engine.route_registry
                ),
                worker_factory=(
                    QueuedCrossExchangeSharedCacheRouteWorker
                ),
                idle_sleep_seconds=0.005,
            )
        )

        print()
        print("=== START PERSISTENT MANAGERS ===")

        start_results = await asyncio.gather(
            *(
                manager.start()
                for manager
                in managers.values()
            ),
            return_exceptions=True,
        )

        for (
            exchange_id,
            result,
        ) in zip(
            managers.keys(),
            start_results,
        ):
            print(
                f"{exchange_id:12}",
                result,
            )

        print()
        print(
            "=== START PERSISTENT ROUTE WORKERS ==="
        )

        route_pool_start = (
            persistent_route_pool.start()
        )

        print(
            route_pool_start
        )

        soak_started = time.perf_counter()

        snapshot_number = 0

        while True:
            elapsed = (
                time.perf_counter()
                - soak_started
            )

            remaining = (
                SOAK_DURATION_SECONDS
                - elapsed
            )

            if remaining <= 0:
                break

            sleep_seconds = min(
                HEALTH_SNAPSHOT_INTERVAL_SECONDS,
                remaining,
            )

            await asyncio.sleep(
                sleep_seconds
            )

            snapshot_number += 1

            elapsed = (
                time.perf_counter()
                - soak_started
            )

            print()
            print(
                "=== HEALTH SNAPSHOT "
                f"{snapshot_number} "
                f"@ {elapsed:.1f}s ==="
            )

            total_symbols = 0
            total_fresh = 0
            total_stale = 0
            total_initializing = 0
            total_completed = 0
            total_failed = 0

            for (
                exchange_id,
                manager,
            ) in managers.items():
                stats = manager.statistics()

                monitor = (
                    scanner_health_monitors[
                        exchange_id
                    ]
                )

                fresh_symbols = []
                stale_symbols = []
                initializing_symbols = []
                symbol_status = {}

                for symbol in manager.symbols:
                    scanner_id = (
                        f"{exchange_id}:{symbol}"
                    )

                    status = monitor.status(
                        scanner_id
                    )

                    symbol_status[
                        symbol
                    ] = status

                    state = status[
                        "state"
                    ]

                    if state == "FRESH":
                        fresh_symbols.append(
                            symbol
                        )
                    elif state == "STALE":
                        stale_symbols.append(
                            symbol
                        )
                    else:
                        initializing_symbols.append(
                            symbol
                        )

                symbols = len(
                    manager.symbols
                )

                fresh = len(
                    fresh_symbols
                )

                stale = len(
                    stale_symbols
                )

                initializing = len(
                    initializing_symbols
                )

                completed = int(
                    stats.get(
                        "completed_updates",
                        0,
                    )
                    or 0
                )

                failed = int(
                    stats.get(
                        "failed_updates",
                        0,
                    )
                    or 0
                )

                total_symbols += symbols
                total_fresh += fresh
                total_stale += stale
                total_initializing += initializing
                total_completed += completed
                total_failed += failed

                print(
                    f"{exchange_id:12} "
                    f"symbols={symbols:3} "
                    f"fresh={fresh:3} "
                    f"stale={stale:3} "
                    f"initializing={initializing:3} "
                    f"updates={completed:7} "
                    f"failures={failed:5} "
                    f"running="
                    f"{stats.get('running')}"
                )

                if stale_symbols:
                    print(
                        "  STALE:",
                        ", ".join(
                            stale_symbols[:20]
                        ),
                    )

                    if len(stale_symbols) > 20:
                        print(
                            "  ... plus",
                            len(stale_symbols) - 20,
                            "more",
                        )

                if initializing_symbols:
                    print(
                        "  INITIALIZING:",
                        ", ".join(
                            initializing_symbols[:20]
                        ),
                    )

                    if (
                        len(initializing_symbols)
                        > 20
                    ):
                        print(
                            "  ... plus",
                            len(
                                initializing_symbols
                            ) - 20,
                            "more",
                        )

            route_stats = (
                persistent_route_pool
                .statistics()
            )

            print(
                "Route processing:",
                {
                    "worker_count": (
                        route_stats[
                            "worker_count"
                        ]
                    ),
                    "processed_routes": (
                        route_stats[
                            "processed_count"
                        ]
                    ),
                    "routes_per_second": (
                        route_stats[
                            "routes_per_second"
                        ]
                    ),
                    "pending_routes": (
                        route_stats[
                            "pending_count"
                        ]
                    ),
                    "alive_threads": (
                        route_stats[
                            "alive_thread_count"
                        ]
                    ),
                    "worker_errors": (
                        route_stats[
                            "worker_error_count"
                        ]
                    ),
                    "running": (
                        route_stats[
                            "running"
                        ]
                    ),
                },
            )

            print(
                "Snapshot totals:",
                {
                    "symbols": total_symbols,
                    "fresh": total_fresh,
                    "stale": total_stale,
                    "initializing": (
                        total_initializing
                    ),
                    "completed_updates": (
                        total_completed
                    ),
                    "failed_updates": (
                        total_failed
                    ),
                    "pending_routes": (
                        engine.work_queue
                        .pending_count()
                    ),
                    "paper_only": True,
                    "live_order_submitted": False,
                },
            )

        print()
        print(
            "=== END-OF-SOAK ROUTE STATISTICS ==="
        )

        print(
            persistent_route_pool
            .statistics()
        )

        print()
        print("=== FINAL MANAGER STATISTICS ===")

        for (
            exchange_id,
            manager,
        ) in managers.items():
            print(
                f"{exchange_id:12}",
                manager.statistics(),
            )

        print()
        print("=== STOP PERSISTENT MANAGERS ===")

        stop_results = await asyncio.gather(
            *(
                manager.stop()
                for manager
                in managers.values()
            ),
            return_exceptions=True,
        )

        for (
            exchange_id,
            result,
        ) in zip(
            managers.keys(),
            stop_results,
        ):
            print(
                f"{exchange_id:12}",
                result,
            )

        print()
        print(
            "=== STOP PERSISTENT ROUTE WORKERS ==="
        )

        route_pool_stop = (
            persistent_route_pool.stop(
                join_timeout_seconds=10.0
            )
        )

        print(
            route_pool_stop
        )

        print()
        print(
            "=== FINAL ROUTE PROCESSING STATISTICS ==="
        )

        print(
            persistent_route_pool
            .statistics()
        )

        print()
        print(
            "=== POST-STOP RUNNING CHECK ==="
        )

        for (
            exchange_id,
            manager,
        ) in managers.items():
            print(
                f"{exchange_id:12} "
                f"running={manager.is_running()}"
            )

        print()
        print(
            "Persistent soak seconds:",
            round(
                time.perf_counter()
                - soak_started,
                3,
            ),
        )

        print()
        print("=== RUNTIME STATUS ===")
        print(runtime.status())

    finally:
        # Final lifecycle safety net.
        #
        # Managers normally drain CCXT spawned tasks
        # during stop(). If execution exits early,
        # drain remaining exchange-owned spawn tasks
        # before closing exchange resources.
        await asyncio.gather(
            *(
                exchange.drain_spawn_tasks(
                    cancel=True
                )
                for exchange
                in exchanges.values()
                if getattr(
                    exchange,
                    "drain_spawn_tasks",
                    None,
                )
                is not None
            ),
            return_exceptions=True,
        )

        await asyncio.gather(
            *(
                exchange.close()
                for exchange
                in exchanges.values()
            ),
            return_exceptions=True,
        )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
