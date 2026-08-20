"""
ArbOS™

EX-359B
Venue-Specific Public Feed Policy Diagnostic

Tests:
- Bitget smaller paced subscription batches
- HTX smaller batches plus delayed recovery
- 100 common USDT spot symbols

Diagnostic only.
Public market data only.
No authentication.
No transfers.
No live orders.
"""

import asyncio
import json
import time

import ccxt.pro as ccxtpro


REQUESTED_COINS = 100

PREFERRED = [
    "BTC", "ETH", "SOL", "XRP", "DOGE",
    "ADA", "BNB", "TRX", "LINK", "LTC",
    "BCH", "DOT", "AVAX", "UNI", "ATOM",
    "ETC", "NEAR", "APT", "ARB", "OP",
    "FIL", "ICP", "AAVE", "ALGO", "VET",
]


def eligible_assets(markets):
    result = set()

    for market in (markets or {}).values():
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
            ("3L", "3S", "5L", "5S")
        ):
            continue

        result.add(base)

    return result


async def watch_once(
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
            "error_type": (
                type(exc).__name__
            ),
            "error": str(exc),
        }


async def run_batches(
    exchange,
    exchange_id,
    symbols,
    batch_size,
    gap_seconds,
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

        print(
            f"{exchange_id}: batch "
            f"{offset // batch_size + 1} "
            f"({len(batch)} symbols)",
            flush=True,
        )

        batch_results = (
            await asyncio.gather(
                *[
                    watch_once(
                        exchange,
                        symbol,
                    )
                    for symbol in batch
                ]
            )
        )

        results.extend(
            batch_results
        )

        if (
            offset + batch_size
            < len(symbols)
        ):
            await asyncio.sleep(
                gap_seconds
            )

    return (
        results,
        time.perf_counter()
        - started,
    )


async def diagnose(
    exchange,
    exchange_id,
    symbols,
    batch_size,
    gap_seconds,
    retry_delay,
):
    first, first_seconds = (
        await run_batches(
            exchange=exchange,
            exchange_id=exchange_id,
            symbols=symbols,
            batch_size=batch_size,
            gap_seconds=gap_seconds,
        )
    )

    failed_symbols = [
        item["symbol"]
        for item in first
        if item["success"] is not True
    ]

    retry_results = []

    if failed_symbols:
        print(
            f"{exchange_id}: "
            f"retrying {len(failed_symbols)} "
            f"failed symbols after "
            f"{retry_delay}s",
            flush=True,
        )

        await asyncio.sleep(
            retry_delay
        )

        retry_results, _ = (
            await run_batches(
                exchange=exchange,
                exchange_id=(
                    f"{exchange_id}-retry"
                ),
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
        )

    recovered = {
        item["symbol"]
        for item in retry_results
        if item["success"] is True
    }

    final_failures = [
        item
        for item in first
        if (
            item["success"] is not True
            and item["symbol"]
            not in recovered
        )
    ]

    successful_first = sum(
        1
        for item in first
        if item["success"] is True
    )

    final_success = (
        successful_first
        + len(recovered)
    )

    error_counts = {}

    for item in final_failures:
        error_type = (
            item["error_type"]
            or "Unknown"
        )

        error_counts[
            error_type
        ] = (
            error_counts.get(
                error_type,
                0,
            )
            + 1
        )

    return {
        "exchange_id": exchange_id,
        "symbol_count": len(symbols),
        "batch_size": batch_size,
        "gap_seconds": gap_seconds,
        "first_pass_success": (
            successful_first
        ),
        "first_pass_failed": (
            len(failed_symbols)
        ),
        "recovered_on_retry": (
            len(recovered)
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
                / len(symbols)
                * 100.0
            ),
            2,
        ),
        "first_pass_seconds": round(
            first_seconds,
            4,
        ),
        "final_error_counts": (
            error_counts
        ),
        "final_failures": (
            final_failures
        ),
    }


async def main():
    discovery_exchanges = {
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
        market_results = await asyncio.gather(
            *[
                exchange.load_markets()
                for exchange
                in discovery_exchanges.values()
            ]
        )

        eligible = {
            exchange_id:
            eligible_assets(markets)
            for exchange_id, markets
            in zip(
                discovery_exchanges.keys(),
                market_results,
            )
        }

        common = set.intersection(
            *eligible.values()
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

        symbols = [
            f"{coin}/USDT"
            for coin in selected
        ]

        print(
            "=============================================="
        )
        print(
            " ArbOS EX-359B — VENUE FEED POLICY TEST"
        )
        print(
            "=============================================="
        )
        print(
            "Symbols:",
            len(symbols),
        )
        print(
            "LIVE TRADING: DISABLED"
        )
        print()

        # Fresh exchange objects for the actual test.
        bitget = ccxtpro.bitget({
            "enableRateLimit": True,
        })

        htx = ccxtpro.htx({
            "enableRateLimit": True,
        })

        try:
            # Bitget:
            # reduce concurrency from 40 -> 20
            # and pace each batch.
            bitget_result = await diagnose(
                exchange=bitget,
                exchange_id="bitget",
                symbols=symbols,
                batch_size=20,
                gap_seconds=1.5,
                retry_delay=2.0,
            )

            print()
            print(
                "=== BITGET RESULT ==="
            )
            print(
                json.dumps(
                    bitget_result,
                    indent=2,
                )
            )

            print()

            # HTX:
            # snapshot synchronization is expensive;
            # reduce simultaneous initialization.
            htx_result = await diagnose(
                exchange=htx,
                exchange_id="htx",
                symbols=symbols,
                batch_size=10,
                gap_seconds=0.5,
                retry_delay=2.0,
            )

            print()
            print(
                "=== HTX RESULT ==="
            )
            print(
                json.dumps(
                    htx_result,
                    indent=2,
                )
            )

            print()
            print(
                "=============================================="
            )
            print(
                " FINAL"
            )
            print(
                "=============================================="
            )

            print(
                json.dumps(
                    {
                        "bitget": (
                            bitget_result
                        ),
                        "htx": (
                            htx_result
                        ),
                        "paper_only": True,
                        "live_order_submitted": False,
                    },
                    indent=2,
                )
            )

        finally:
            await asyncio.gather(
                bitget.close(),
                htx.close(),
                return_exceptions=True,
            )

    finally:
        await asyncio.gather(
            *[
                exchange.close()
                for exchange
                in discovery_exchanges.values()
            ],
            return_exceptions=True,
        )


if __name__ == "__main__":
    asyncio.run(main())
