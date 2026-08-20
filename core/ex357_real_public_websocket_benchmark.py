"""
ArbOS™

EX-357
Real Public WebSocket Shared-Cache Benchmark

25 coins x 3 exchanges.

Public market data only.
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


EXCHANGE_IDS = [
    "kucoin",
    "bitget",
    "htx",
]

COINS = [
    "BTC",
    "ETH",
    "ADA",
    "DOGE",
    "XRP",
    "SOL",
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

FEE_RATES = {
    "kucoin": 0.001,
    "bitget": 0.001,
    "htx": 0.002,
}

STARTING_USDT = 100.0


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

        # Backward-compatible route owner.
        "exchange_id": source_exchange,

        "source_exchange": source_exchange,
        "destination_exchange": (
            destination_exchange
        ),

        "symbol": symbol,

        "starting_value": STARTING_USDT,

        "source_fee_rate": (
            FEE_RATES[source_exchange]
        ),

        "destination_fee_rate": (
            FEE_RATES[destination_exchange]
        ),

        "legs": [
            {
                "exchange_id": source_exchange,
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


async def main():
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

    engine = EventDrivenSharedCacheScanEngine(
        worker_factory=(
            QueuedCrossExchangeSharedCacheRouteWorker
        ),
        worker_count=8,
        max_queue_size=10000,
    )

    registered = 0

    for source_exchange in EXCHANGE_IDS:
        for destination_exchange in EXCHANGE_IDS:
            if (
                source_exchange
                == destination_exchange
            ):
                continue

            for coin in COINS:
                engine.register_route(
                    build_route(
                        source_exchange,
                        destination_exchange,
                        coin,
                    )
                )

                registered += 1

    exchange_symbols = {
        exchange_id: [
            f"{coin}/USDT"
            for coin in COINS
        ]
        for exchange_id in EXCHANGE_IDS
    }

    runtime = EventDrivenPublicFeedRuntime(
        engine=engine,
        exchanges=exchanges,
        exchange_symbols=exchange_symbols,
    )

    print(
        "=============================================="
    )
    print(
        " ArbOS EX-357 — 25-COIN WEBSOCKET BENCHMARK"
    )
    print(
        "=============================================="
    )
    print()
    print(
        "Exchanges:",
        ", ".join(EXCHANGE_IDS),
    )
    print(
        "Coins:",
        len(COINS),
    )
    print(
        "Market subscriptions:",
        len(COINS) * len(EXCHANGE_IDS),
    )
    print(
        "Registered ordered routes:",
        registered,
    )
    print(
        "Workers:",
        8,
    )
    print(
        "Starting simulated capital:",
        STARTING_USDT,
        "USDT",
    )
    print(
        "LIVE TRADING: DISABLED"
    )
    print()

    started = time.perf_counter()

    try:
        managers = runtime.managers

        feed_started = time.perf_counter()

        feed_results = await asyncio.gather(
            *[
                manager.run_cycles(
                    cycles_per_symbol=1
                )
                for manager in (
                    managers.values()
                )
            ],
            return_exceptions=True,
        )

        feed_elapsed = (
            time.perf_counter()
            - feed_started
        )

        pending_before_workers = (
            engine.work_queue.pending_count()
        )

        worker_started = time.perf_counter()

        processing = (
            runtime.process_pending()
        )

        worker_elapsed = (
            time.perf_counter()
            - worker_started
        )

        total_elapsed = (
            time.perf_counter()
            - started
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
            if item.get("filled") is True
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

        failures = [
            item
            for item in results
            if item.get("filled") is not True
        ]

        feed_summary = []

        for exchange_id, result in zip(
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
            else:
                feed_summary.append({
                    "exchange_id": (
                        exchange_id
                    ),
                    "ready": True,
                    "completed_updates": (
                        result.get(
                            "completed_updates"
                        )
                    ),
                    "failed_updates": (
                        result.get(
                            "failed_updates"
                        )
                    ),
                })

        summary = {
            "exchange_count": len(
                EXCHANGE_IDS
            ),
            "coin_count": len(
                COINS
            ),
            "market_subscription_count": (
                len(COINS)
                * len(EXCHANGE_IDS)
            ),
            "registered_route_count": (
                registered
            ),
            "pending_routes_before_workers": (
                pending_before_workers
            ),
            "processed_route_count": (
                processing.get(
                    "processed_count"
                )
            ),
            "filled_route_count": len(
                filled
            ),
            "profitable_route_count": len(
                profitable
            ),
            "failure_count": len(
                failures
            ),
            "worker_count": (
                processing.get(
                    "worker_count"
                )
            ),
            "feed_seconds": round(
                feed_elapsed,
                4,
            ),
            "worker_seconds": round(
                worker_elapsed,
                4,
            ),
            "total_seconds": round(
                total_elapsed,
                4,
            ),
            "old_serial_baseline_seconds": (
                113.740
            ),
            "speedup_vs_old_baseline": (
                round(
                    113.740
                    / total_elapsed,
                    2,
                )
                if total_elapsed > 0
                else None
            ),
            "feeds": feed_summary,
            "best_profitable_routes": (
                profitable[:10]
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

        print(
            json.dumps(
                summary,
                indent=2,
                default=str,
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
    asyncio.run(main())
