"""
ArbOS™

EX-366
Real 100-Coin Venue-Aware Event-Driven Benchmark

Purpose:
Benchmark the new high-throughput architecture using:

- KuCoin public WebSocket feed
- Bitget public WebSocket feed
- HTX native BBO WebSocket feed
- HTX REST depth only as bootstrap/fallback
- shared market-data cache
- event-driven route dispatch
- parallel route workers

Paper only.
No authentication.
No transfers.
No live orders.
"""

import asyncio
import json
import time

import ccxt.pro as ccxtpro

from core.event_driven_shared_cache_scan_engine import (
    EventDrivenSharedCacheScanEngine,
)
from core.event_driven_public_feed_runtime import (
    EventDrivenPublicFeedRuntime,
)
from core.queued_cross_exchange_shared_cache_route_worker import (
    QueuedCrossExchangeSharedCacheRouteWorker,
)
from core.htx_event_driven_market_feed import (
    HTXEventDrivenMarketFeed,
)
from exchanges.htx_native_bbo_feed import (
    HTXNativeBBOFeed,
)
from exchanges.htx_public_spot_client import (
    HTXPublicSpotClient,
)
from exchanges.order_retry_backoff_policy import (
    OrderRetryBackoffPolicy,
)


REQUESTED_COINS = 100
WORKER_COUNT = 16
STARTING_VALUE = 100.0

EXCHANGE_IDS = [
    "kucoin",
    "bitget",
    "htx",
]

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
    "ALGO",
    "VET",
]


def build_route(
    source_exchange,
    destination_exchange,
    coin,
):
    symbol = f"{coin}/USDT"

    return {
        "route_id": (
            f"{source_exchange.upper()}-"
            f"{destination_exchange.upper()}-"
            f"{coin}"
        ),
        "route_type": "cross_exchange",
        "exchange_id": source_exchange,
        "source_exchange": source_exchange,
        "destination_exchange": (
            destination_exchange
        ),
        "symbol": symbol,
        "starting_value": STARTING_VALUE,
        "source_fee_rate": 0.001,
        "destination_fee_rate": 0.001,
        "legs": [
            {
                "exchange_id": source_exchange,
                "symbol": symbol,
                "side": "buy",
            },
            {
                "exchange_id": destination_exchange,
                "symbol": symbol,
                "side": "sell",
            },
        ],
        "paper_only": True,
        "live_order_submitted": False,
    }


async def load_active_usdt_assets(
    exchange,
):
    markets = await exchange.load_markets()

    return {
        str(
            market.get(
                "base",
                "",
            )
        ).strip().upper()
        for market in markets.values()
        if (
            market.get("spot") is True
            and str(
                market.get(
                    "quote",
                    "",
                )
            ).strip().upper()
            == "USDT"
            and market.get(
                "active",
                True,
            )
            is not False
        )
    }


def select_coins(
    common_assets,
):
    selected = []

    for coin in PREFERRED_COINS:
        if (
            coin in common_assets
            and coin not in selected
        ):
            selected.append(
                coin
            )

    for coin in sorted(
        common_assets
    ):
        if coin in selected:
            continue

        selected.append(
            coin
        )

        if (
            len(selected)
            >= REQUESTED_COINS
        ):
            break

    return selected[
        :REQUESTED_COINS
    ]


async def main():
    overall_started = (
        time.perf_counter()
    )

    exchanges = {
        "kucoin": ccxtpro.kucoin({
            "enableRateLimit": True,
        }),
        "bitget": ccxtpro.bitget({
            "enableRateLimit": True,
        }),
        "htx": ccxtpro.htx({
            "enableRateLimit": True,
        }),
    }

    try:
        print(
            "=============================================="
        )
        print(
            " ArbOS EX-366 — 100 COIN VENUE-AWARE BENCHMARK"
        )
        print(
            "=============================================="
        )
        print(
            "LIVE TRADING: DISABLED"
        )
        print()

        discovery_started = (
            time.perf_counter()
        )

        asset_sets = {}

        for (
            exchange_id,
            exchange,
        ) in exchanges.items():
            asset_sets[
                exchange_id
            ] = (
                await load_active_usdt_assets(
                    exchange
                )
            )

        common_assets = set.intersection(
            *asset_sets.values()
        )

        selected = select_coins(
            common_assets
        )

        if (
            len(selected)
            < REQUESTED_COINS
        ):
            raise RuntimeError(
                "fewer than 100 common "
                "active USDT spot assets"
            )

        discovery_seconds = (
            time.perf_counter()
            - discovery_started
        )

        engine = (
            EventDrivenSharedCacheScanEngine(
                worker_factory=(
                    QueuedCrossExchangeSharedCacheRouteWorker
                ),
                worker_count=(
                    WORKER_COUNT
                ),
                max_queue_size=100000,
            )
        )

        registered = 0

        for source_exchange in (
            EXCHANGE_IDS
        ):
            for destination_exchange in (
                EXCHANGE_IDS
            ):
                if (
                    source_exchange
                    == destination_exchange
                ):
                    continue

                for coin in selected:
                    engine.register_route(
                        build_route(
                            source_exchange,
                            destination_exchange,
                            coin,
                        )
                    )

                    registered += 1

        exchange_symbols = {
            "kucoin": [
                f"{coin}/USDT"
                for coin in selected
            ],
            "bitget": [
                f"{coin}/USDT"
                for coin in selected
            ],
        }

        backoff_policies = {
            "kucoin": OrderRetryBackoffPolicy(
                base_delay_seconds=1.0,
                max_delay_seconds=30.0,
            ),
            "bitget": OrderRetryBackoffPolicy(
                base_delay_seconds=1.0,
                max_delay_seconds=30.0,
            ),
        }

        runtime = (
            EventDrivenPublicFeedRuntime(
                engine=engine,
                exchanges={
                    "kucoin": (
                        exchanges["kucoin"]
                    ),
                    "bitget": (
                        exchanges["bitget"]
                    ),
                },
                exchange_symbols=(
                    exchange_symbols
                ),
                backoff_policies=(
                    backoff_policies
                ),
            )
        )

        htx_feed = (
            HTXEventDrivenMarketFeed(
                intake_service=(
                    runtime.intake_service
                ),
                native_feed=(
                    HTXNativeBBOFeed(
                        intake_service=(
                            runtime.intake_service
                        ),
                        symbols=[
                            f"{coin}/USDT"
                            for coin in selected
                        ],
                    )
                ),
                rest_client=(
                    HTXPublicSpotClient()
                ),
            )
        )

        print(
            "Common eligible assets:",
            len(common_assets),
        )
        print(
            "Selected coins:",
            len(selected),
        )
        print(
            "Registered ordered routes:",
            registered,
        )
        print(
            "Workers:",
            WORKER_COUNT,
        )
        print()

        #
        # --------------------------------------------------
        # HTX bootstrap
        # --------------------------------------------------
        #

        htx_bootstrap_started = (
            time.perf_counter()
        )

        htx_bootstrap = (
            htx_feed.bootstrap_symbols(
                [
                    f"{coin}/USDT"
                    for coin in selected
                ],
                limit=20,
            )
        )

        htx_bootstrap_seconds = (
            time.perf_counter()
            - htx_bootstrap_started
        )

        #
        # --------------------------------------------------
        # KuCoin + Bitget feed collection
        # --------------------------------------------------
        #

        feed_started = (
            time.perf_counter()
        )

        managers = (
            runtime.managers
        )

        feed_results = (
            await asyncio.gather(
                *[
                    manager.run_cycles(
                        cycles_per_symbol=1
                    )
                    for manager
                    in managers.values()
                ],
                return_exceptions=True,
            )
        )

        feed_seconds = (
            time.perf_counter()
            - feed_started
        )

        pending_before_workers = (
            engine.work_queue
            .pending_count()
        )

        worker_started = (
            time.perf_counter()
        )

        processing = (
            runtime.process_pending()
        )

        worker_seconds = (
            time.perf_counter()
            - worker_started
        )

        results = (
            processing.get(
                "results",
                [],
            )
            or []
        )

        filled = [
            item
            for item in results
            if item.get(
                "filled"
            ) is True
        ]

        failures = [
            item
            for item in results
            if item.get(
                "filled"
            ) is not True
        ]

        profitable = sorted(
            [
                item
                for item in filled
                if float(
                    item.get(
                        "net_profit",
                        0.0,
                    )
                ) > 0
            ],
            key=lambda item: float(
                item.get(
                    "net_profit",
                    0.0,
                )
            ),
            reverse=True,
        )

        # ==========================================
        # EX-368
        # Route failure classification
        # ==========================================

        failures_by_reason = {}
        failures_by_exchange = {}
        failures_by_exchange_pair = {}
        failure_samples = []

        for failure in failures:
            reason = str(
                failure.get(
                    "reason",
                    "unknown_failure",
                )
                or "unknown_failure"
            )

            failures_by_reason[reason] = (
                failures_by_reason.get(
                    reason,
                    0,
                )
                + 1
            )

            failing_exchange = str(
                failure.get(
                    "exchange_id",
                    "unknown",
                )
                or "unknown"
            ).strip().lower()

            failures_by_exchange[
                failing_exchange
            ] = (
                failures_by_exchange.get(
                    failing_exchange,
                    0,
                )
                + 1
            )

            route_id = str(
                failure.get(
                    "route_id",
                    "",
                )
                or ""
            )

            parts = route_id.split(
                "-",
                2,
            )

            if len(parts) >= 2:
                source_exchange = (
                    parts[0].strip().lower()
                )
                destination_exchange = (
                    parts[1].strip().lower()
                )

                pair = (
                    f"{source_exchange}"
                    f"->{destination_exchange}"
                )
            else:
                source_exchange = (
                    "unknown"
                )
                destination_exchange = (
                    "unknown"
                )
                pair = "unknown"

            failures_by_exchange_pair[
                pair
            ] = (
                failures_by_exchange_pair.get(
                    pair,
                    0,
                )
                + 1
            )

            if len(failure_samples) < 20:
                failure_samples.append({
                    "route_id": route_id,
                    "source_exchange": (
                        source_exchange
                    ),
                    "destination_exchange": (
                        destination_exchange
                    ),
                    "failing_exchange": (
                        failing_exchange
                    ),
                    "symbol": (
                        failure.get(
                            "symbol"
                        )
                        or failure.get(
                            "trigger_symbol"
                        )
                    ),
                    "reason": reason,
                })

        feed_summary = []

        for (
            exchange_id,
            result,
        ) in zip(
            managers.keys(),
            feed_results,
        ):
            if isinstance(
                result,
                Exception,
            ):
                feed_summary.append({
                    "exchange_id": (
                        exchange_id
                    ),
                    "ready": False,
                    "error": (
                        f"{type(result).__name__}: "
                        f"{result}"
                    ),
                })

                continue

            feed_summary.append({
                "exchange_id": (
                    exchange_id
                ),
                "ready": True,
                "completed_updates": (
                    result.get(
                        "completed_updates",
                        0,
                    )
                ),
                "failed_updates": (
                    result.get(
                        "failed_updates",
                        0,
                    )
                ),
            })

        overall_seconds = (
            time.perf_counter()
            - overall_started
        )

        output = {
            "exchange_count": 3,
            "coin_count": len(
                selected
            ),
            "common_eligible_coin_count": (
                len(common_assets)
            ),
            "registered_route_count": (
                registered
            ),
            "worker_count": (
                WORKER_COUNT
            ),
            "discovery_seconds": round(
                discovery_seconds,
                4,
            ),
            "htx_bootstrap_seconds": round(
                htx_bootstrap_seconds,
                4,
            ),
            "htx_bootstrap_submitted": (
                htx_bootstrap.get(
                    "submitted_count",
                    0,
                )
            ),
            "feed_seconds": round(
                feed_seconds,
                4,
            ),
            "pending_routes_before_workers": (
                pending_before_workers
            ),
            "worker_seconds": round(
                worker_seconds,
                4,
            ),
            "processed_route_count": (
                len(results)
            ),
            "filled_route_count": (
                len(filled)
            ),
            "profitable_route_count": (
                len(profitable)
            ),
            "failure_count": (
                len(failures)
            ),
            "failures_by_reason": dict(
                sorted(
                    failures_by_reason.items(),
                    key=lambda item: (
                        -item[1],
                        item[0],
                    ),
                )
            ),
            "failures_by_exchange": dict(
                sorted(
                    failures_by_exchange.items(),
                    key=lambda item: (
                        -item[1],
                        item[0],
                    ),
                )
            ),
            "failures_by_exchange_pair": dict(
                sorted(
                    failures_by_exchange_pair.items(),
                    key=lambda item: (
                        -item[1],
                        item[0],
                    ),
                )
            ),
            "failure_samples": (
                failure_samples
            ),
            "overall_seconds": round(
                overall_seconds,
                4,
            ),
            "ex358_baseline_seconds": (
                66.3876
            ),
            "speedup_vs_ex358": round(
                (
                    66.3876
                    / overall_seconds
                ),
                2,
            ),
            "feeds": (
                feed_summary
            ),
            "best_profitable_routes": (
                profitable[:10]
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

        print(
            json.dumps(
                output,
                indent=2,
            )
        )

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
    asyncio.run(
        main()
    )
