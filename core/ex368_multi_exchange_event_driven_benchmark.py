"""
ArbOS™
EX-368
Multi-Exchange Event-Driven Benchmark

Venue-aware discovery and route construction for the
multi-exchange public paper scanner.

Paper only.
No authentication.
No transfers.
No live orders.
"""

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
from exchanges.order_retry_backoff_policy import (
    OrderRetryBackoffPolicy,
)


REQUESTED_COINS = 100
WORKER_COUNT = 16
STARTING_VALUE = 100.0

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
    print(" ArbOS EX-368 — MULTI-EXCHANGE EVENT BENCHMARK")
    print("==============================================")
    print("LIVE TRADING: DISABLED")
    print("PUBLIC DATA ONLY")
    print()

    exchanges = {
        exchange_id: getattr(
            ccxtpro,
            exchange_id,
        )({
            "enableRateLimit": True,
        })
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
            "EX-368 topology discovery completed."
        )

        bounded_symbols = (
            build_bounded_exchange_symbols(
                exchange_symbols,
                per_exchange_limit=5,
            )
        )

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
                backoff_policies=(
                    backoff_policies
                ),
                order_book_limits=(
                    order_book_limits
                ),
                cycle_timeout_seconds={
                    "xt": 15.0,
                },
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

        cycle_results = await asyncio.gather(
            *(
                manager.run_cycles(
                    cycles_per_symbol=1
                )
                for manager
                in managers.values()
            ),
            return_exceptions=True,
        )

        print()
        print("=== VENUE CYCLE RESULTS ===")

        for (
            exchange_id,
            result,
        ) in zip(
            managers.keys(),
            cycle_results,
        ):
            print(
                f"{exchange_id:12}",
                result,
            )

        processing = (
            runtime.process_pending()
        )

        print()
        print("=== ROUTE PROCESSING ===")
        print(processing)

        print()
        print("=== RUNTIME STATUS ===")
        print(runtime.status())

    finally:
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
