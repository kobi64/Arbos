"""
ArbOS™

EX-358
Real 100-Coin Public WebSocket Benchmark

Automatically discovers 100 common active USDT spot assets
across KuCoin, Bitget and HTX.

Then benchmarks:

300 market subscriptions
600 ordered cross-exchange routes
shared market cache
dependency dispatch
coalesced work queue
parallel route workers

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

REQUESTED_COINS = 100

FEE_RATES = {
    "kucoin": 0.001,
    "bitget": 0.001,
    "htx": 0.002,
}

STARTING_USDT = 100.0
WORKER_COUNT = 16


def eligible_usdt_assets(
    markets,
):
    result = set()

    for symbol, market in (
        markets or {}
    ).items():
        if market.get("spot") is not True:
            continue

        if market.get("active") is False:
            continue

        if str(
            market.get("quote") or ""
        ).upper() != "USDT":
            continue

        base = str(
            market.get("base") or ""
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

        result.add(
            base
        )

    return result


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
        "route_type": (
            "cross_exchange"
        ),

        # Backward-compatible route owner.
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
            STARTING_USDT
        ),

        "source_fee_rate": (
            FEE_RATES[
                source_exchange
            ]
        ),

        "destination_fee_rate": (
            FEE_RATES[
                destination_exchange
            ]
        ),

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

    print(
        "=============================================="
    )
    print(
        " ArbOS EX-358 — 100 COIN WEBSOCKET BENCHMARK"
    )
    print(
        "=============================================="
    )
    print()
    print(
        "Discovering common active USDT spot assets..."
    )

    overall_started = (
        time.perf_counter()
    )

    try:
        discovery_started = (
            time.perf_counter()
        )

        market_results = (
            await asyncio.gather(
                *[
                    exchange.load_markets()
                    for exchange
                    in exchanges.values()
                ]
            )
        )

        discovery_seconds = (
            time.perf_counter()
            - discovery_started
        )

        eligible = {}

        for (
            exchange_id,
            markets,
        ) in zip(
            EXCHANGE_IDS,
            market_results,
        ):
            eligible[
                exchange_id
            ] = eligible_usdt_assets(
                markets
            )

        common_assets = set.intersection(
            *[
                eligible[
                    exchange_id
                ]
                for exchange_id
                in EXCHANGE_IDS
            ]
        )

        preferred = [
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

        selected = []

        for coin in preferred:
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

        selected = selected[
            :REQUESTED_COINS
        ]

        if (
            len(selected)
            < REQUESTED_COINS
        ):
            raise RuntimeError(
                "fewer than 100 common "
                "active USDT spot assets"
            )

        engine = (
            EventDrivenSharedCacheScanEngine(
                worker_factory=(
                    QueuedCrossExchangeSharedCacheRouteWorker
                ),
                worker_count=(
                    WORKER_COUNT
                ),
                max_queue_size=(
                    100000
                ),
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
            exchange_id: [
                f"{coin}/USDT"
                for coin in selected
            ]
            for exchange_id
            in EXCHANGE_IDS
        }

        runtime = (
            EventDrivenPublicFeedRuntime(
                engine=engine,
                exchanges=exchanges,
                exchange_symbols=(
                    exchange_symbols
                ),
            )
        )

        print()
        print(
            "Common eligible assets:",
            len(common_assets),
        )
        print(
            "Selected coins:",
            len(selected),
        )
        print(
            "Market subscriptions:",
            (
                len(selected)
                * len(EXCHANGE_IDS)
            ),
        )
        print(
            "Registered ordered routes:",
            registered,
        )
        print(
            "Workers:",
            WORKER_COUNT,
        )
        print(
            "LIVE TRADING: DISABLED"
        )
        print()

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

        total_engine_seconds = (
            feed_seconds
            + worker_seconds
        )

        overall_seconds = (
            time.perf_counter()
            - overall_started
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
            "exchange_count": (
                len(EXCHANGE_IDS)
            ),
            "coin_count": (
                len(selected)
            ),
            "common_eligible_coin_count": (
                len(common_assets)
            ),
            "market_subscription_count": (
                len(selected)
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
            "filled_route_count": (
                len(filled)
            ),
            "profitable_route_count": (
                len(profitable)
            ),
            "failure_count": (
                len(failures)
            ),
            "worker_count": (
                processing.get(
                    "worker_count"
                )
            ),
            "discovery_seconds": round(
                discovery_seconds,
                4,
            ),
            "feed_seconds": round(
                feed_seconds,
                4,
            ),
            "worker_seconds": round(
                worker_seconds,
                4,
            ),
            "engine_seconds": round(
                total_engine_seconds,
                4,
            ),
            "overall_seconds": round(
                overall_seconds,
                4,
            ),
            "selected_coins": (
                selected
            ),
            "feeds": (
                feed_summary
            ),
            "top_raw_spreads": (
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
    asyncio.run(
        main()
    )
