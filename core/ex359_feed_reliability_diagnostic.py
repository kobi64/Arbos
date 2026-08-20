"""
ArbOS™

EX-359A
Real Public WebSocket Feed Reliability Diagnostic

Purpose:
- diagnose EX-358 missing WebSocket snapshots
- respect existing conservative feed batch sizes
- capture symbol-level exception details
- compare KuCoin, Bitget and HTX

Public market data only.
No authentication.
No transfers.
No live orders.
"""

import asyncio
import json
import time

import ccxt.pro as ccxtpro

from core.verified_production_feed_profiles import (
    VerifiedProductionFeedProfiles,
)


EXCHANGE_IDS = [
    "kucoin",
    "bitget",
    "htx",
]

REQUESTED_COINS = 100

PREFERRED = [
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


def eligible_usdt_assets(markets):
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

        result.add(base)

    return result


async def watch_symbol(
    exchange,
    exchange_id,
    symbol,
):
    started = time.perf_counter()

    try:
        book = await exchange.watch_order_book(
            symbol
        )

        elapsed = (
            time.perf_counter()
            - started
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
                "order book unavailable"
            )

        return {
            "exchange_id": exchange_id,
            "symbol": symbol,
            "success": True,
            "seconds": round(
                elapsed,
                4,
            ),
            "best_bid": float(
                bids[0][0]
            ),
            "best_ask": float(
                asks[0][0]
            ),
            "error_type": None,
            "error": None,
        }

    except Exception as exc:
        elapsed = (
            time.perf_counter()
            - started
        )

        return {
            "exchange_id": exchange_id,
            "symbol": symbol,
            "success": False,
            "seconds": round(
                elapsed,
                4,
            ),
            "error_type": (
                type(exc).__name__
            ),
            "error": str(exc),
        }


async def run_exchange(
    exchange,
    exchange_id,
    symbols,
    batch_size,
):
    results = []

    started = time.perf_counter()

    for offset in range(
        0,
        len(symbols),
        batch_size,
    ):
        batch = symbols[
            offset:
            offset + batch_size
        ]

        batch_number = (
            offset // batch_size
            + 1
        )

        print(
            f"{exchange_id}: "
            f"batch {batch_number} "
            f"({len(batch)} symbols)",
            flush=True,
        )

        batch_results = (
            await asyncio.gather(
                *[
                    watch_symbol(
                        exchange,
                        exchange_id,
                        symbol,
                    )
                    for symbol in batch
                ]
            )
        )

        results.extend(
            batch_results
        )

        # Small subscription pacing gap.
        if (
            offset + batch_size
            < len(symbols)
        ):
            await asyncio.sleep(1.0)

    elapsed = (
        time.perf_counter()
        - started
    )

    successful = [
        item
        for item in results
        if item["success"]
    ]

    failed = [
        item
        for item in results
        if not item["success"]
    ]

    error_counts = {}

    for item in failed:
        key = item[
            "error_type"
        ]

        error_counts[key] = (
            error_counts.get(
                key,
                0,
            )
            + 1
        )

    return {
        "exchange_id": exchange_id,
        "batch_size": batch_size,
        "symbol_count": len(symbols),
        "successful": len(
            successful
        ),
        "failed": len(
            failed
        ),
        "success_percent": round(
            (
                len(successful)
                / len(symbols)
                * 100.0
            ),
            2,
        ),
        "seconds": round(
            elapsed,
            4,
        ),
        "error_counts": error_counts,
        "failures": failed,
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

    profiles = (
        VerifiedProductionFeedProfiles()
    )

    profile_map = {
        "kucoin": profiles.kucoin(),
        "bitget": profiles.bitget(),
        "htx": profiles.htx(),
    }

    print(
        "=============================================="
    )
    print(
        " ArbOS EX-359A — FEED RELIABILITY DIAGNOSTIC"
    )
    print(
        "=============================================="
    )
    print(
        "LIVE TRADING: DISABLED"
    )
    print()

    try:
        markets = await asyncio.gather(
            *[
                exchanges[
                    exchange_id
                ].load_markets()
                for exchange_id
                in EXCHANGE_IDS
            ]
        )

        eligible = {
            exchange_id:
            eligible_usdt_assets(
                market_data
            )
            for exchange_id, market_data
            in zip(
                EXCHANGE_IDS,
                markets,
            )
        }

        common = set.intersection(
            *[
                eligible[
                    exchange_id
                ]
                for exchange_id
                in EXCHANGE_IDS
            ]
        )

        selected = []

        for coin in PREFERRED:
            if (
                coin in common
                and coin not in selected
            ):
                selected.append(coin)

        for coin in sorted(common):
            if coin in selected:
                continue

            selected.append(coin)

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
                "fewer than 100 common assets"
            )

        symbols = [
            f"{coin}/USDT"
            for coin in selected
        ]

        print(
            "Common eligible assets:",
            len(common),
        )
        print(
            "Selected symbols:",
            len(symbols),
        )
        print()

        # Run exchanges independently so one venue's
        # subscription pressure cannot distort another.
        summaries = []

        for exchange_id in EXCHANGE_IDS:
            profile = profile_map[
                exchange_id
            ]

            batch_size = int(
                profile[
                    "max_symbols_per_batch"
                ]
            )

            print(
                "----------------------------------------------"
            )
            print(
                exchange_id.upper(),
                "batch size:",
                batch_size,
            )
            print(
                "----------------------------------------------"
            )

            summary = await run_exchange(
                exchange=exchanges[
                    exchange_id
                ],
                exchange_id=exchange_id,
                symbols=symbols,
                batch_size=batch_size,
            )

            summaries.append(
                summary
            )

            print(
                json.dumps(
                    summary,
                    indent=2,
                )
            )
            print()

        final = {
            "requested_coin_count": (
                REQUESTED_COINS
            ),
            "results": summaries,
            "paper_only": True,
            "live_order_submitted": False,
        }

        print(
            "=============================================="
        )
        print(
            " FINAL DIAGNOSTIC SUMMARY"
        )
        print(
            "=============================================="
        )

        print(
            json.dumps(
                final,
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
    asyncio.run(main())
