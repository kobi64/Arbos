"""
ArbOS™

EX-360
HTX Lightweight Ticker Feed Diagnostic

Tests whether HTX ticker WebSockets provide a reliable
broad-scanning alternative to full synchronized order books.

100 common active USDT markets.

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

    for market in (
        markets or {}
    ).values():

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


async def watch_ticker(
    exchange,
    symbol,
):
    started = time.perf_counter()

    try:
        ticker = await exchange.watch_ticker(
            symbol
        )

        bid = ticker.get("bid")
        ask = ticker.get("ask")
        last = ticker.get("last")

        usable_bbo = (
            bid is not None
            and ask is not None
        )

        return {
            "symbol": symbol,
            "success": True,
            "usable_bbo": usable_bbo,
            "bid": bid,
            "ask": ask,
            "last": last,
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
            "usable_bbo": False,
            "bid": None,
            "ask": None,
            "last": None,
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
    symbols,
    batch_size=20,
    gap_seconds=0.5,
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
            "HTX ticker batch",
            offset // batch_size + 1,
            f"({len(batch)} symbols)",
            flush=True,
        )

        batch_results = await asyncio.gather(
            *[
                watch_ticker(
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
        ):
            await asyncio.sleep(
                gap_seconds
            )

    return (
        results,
        time.perf_counter()
        - started,
    )


async def main():
    htx = ccxtpro.htx({
        "enableRateLimit": True,
    })

    print(
        "=============================================="
    )
    print(
        " ArbOS EX-360 — HTX TICKER FEED TEST"
    )
    print(
        "=============================================="
    )
    print(
        "LIVE TRADING: DISABLED"
    )
    print()

    try:
        markets = await htx.load_markets()

        available = eligible_assets(
            markets
        )

        selected = []

        for coin in PREFERRED:
            if (
                coin in available
                and coin not in selected
            ):
                selected.append(
                    coin
                )

        for coin in sorted(
            available
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

        symbols = [
            f"{coin}/USDT"
            for coin in selected
        ]

        print(
            "Selected symbols:",
            len(symbols),
        )

        print(
            "HTX has watchTicker:",
            bool(
                htx.has.get(
                    "watchTicker"
                )
            ),
        )

        print(
            "HTX has watchTickers:",
            bool(
                htx.has.get(
                    "watchTickers"
                )
            ),
        )

        print()

        results, elapsed = (
            await run_batches(
                exchange=htx,
                symbols=symbols,
                batch_size=20,
                gap_seconds=0.5,
            )
        )

        successful = [
            item
            for item in results
            if item["success"]
        ]

        usable_bbo = [
            item
            for item in successful
            if item["usable_bbo"]
        ]

        failures = [
            item
            for item in results
            if not item["success"]
        ]

        missing_bbo = [
            item["symbol"]
            for item in successful
            if not item["usable_bbo"]
        ]

        errors = {}

        for item in failures:
            name = (
                item["error_type"]
                or "Unknown"
            )

            errors[name] = (
                errors.get(
                    name,
                    0,
                )
                + 1
            )

        summary = {
            "symbol_count": len(
                symbols
            ),
            "successful": len(
                successful
            ),
            "failed": len(
                failures
            ),
            "success_percent": round(
                (
                    len(successful)
                    / len(symbols)
                    * 100.0
                ),
                2,
            ),
            "usable_bid_ask_count": (
                len(usable_bbo)
            ),
            "usable_bid_ask_percent": round(
                (
                    len(usable_bbo)
                    / len(symbols)
                    * 100.0
                ),
                2,
            ),
            "seconds": round(
                elapsed,
                4,
            ),
            "error_counts": errors,
            "missing_bid_ask_symbols": (
                missing_bbo
            ),
            "failures": failures,
            "sample_tickers": (
                usable_bbo[:10]
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

        print()
        print(
            "=============================================="
        )
        print(
            " RESULT"
        )
        print(
            "=============================================="
        )

        print(
            json.dumps(
                summary,
                indent=2,
                default=str,
            )
        )

    finally:
        await htx.close()


if __name__ == "__main__":
    asyncio.run(main())
