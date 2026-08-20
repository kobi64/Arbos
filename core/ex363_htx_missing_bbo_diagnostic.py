"""
ArbOS™

EX-363
HTX Missing BBO Diagnostic

Investigates symbols that acknowledged the native HTX
market.$symbol.bbo subscription but did not emit usable
BBO during EX-362.

Checks:
1. HTX native symbol catalogue state
2. HTX native REST order-book depth
3. isolated native BBO WebSocket subscription

Public market data only.
No authentication.
No transfers.
No live orders.
"""

import asyncio
import gzip
import json
import time

import aiohttp
import requests


WS_URL = "wss://api.huobi.pro/ws"
REST_URL = "https://api.huobi.pro"

SYMBOLS = [
    "OP/USDT",
    "FIL/USDT",
    "AB/USDT",
    "ACE/USDT",
    "AMP/USDT",
    "API3/USDT",
    "ARTY/USDT",
    "ATWO/USDT",
    "AVAIL/USDT",
    "BAL/USDT",
    "BANANA/USDT",
]


def native_symbol(symbol):
    return (
        str(symbol)
        .strip()
        .lower()
        .replace("/", "")
        .replace("-", "")
        .replace("_", "")
    )


def decode_message(message):
    if message.type == aiohttp.WSMsgType.BINARY:
        raw = gzip.decompress(
            message.data
        )

        return json.loads(
            raw.decode("utf-8")
        )

    if message.type == aiohttp.WSMsgType.TEXT:
        return json.loads(
            message.data
        )

    return None


def fetch_catalogue():
    response = requests.get(
        f"{REST_URL}/v1/common/symbols",
        timeout=10,
    )

    response.raise_for_status()

    payload = response.json()

    result = {}

    for item in payload.get(
        "data",
        [],
    ):
        symbol = str(
            item.get(
                "symbol",
                "",
            )
        ).lower()

        if not symbol:
            continue

        result[symbol] = {
            "state": item.get(
                "state"
            ),
            "api_trading": item.get(
                "api-trading"
            ),
            "base": item.get(
                "base-currency"
            ),
            "quote": item.get(
                "quote-currency"
            ),
        }

    return result


def fetch_depth(symbol):
    native = native_symbol(
        symbol
    )

    started = time.perf_counter()

    try:
        response = requests.get(
            f"{REST_URL}/market/depth",
            params={
                "symbol": native,
                "type": "step0",
                "depth": 20,
            },
            timeout=10,
        )

        response.raise_for_status()

        payload = response.json()

        tick = (
            payload.get(
                "tick"
            )
            or {}
        )

        bids = (
            tick.get(
                "bids"
            )
            or []
        )

        asks = (
            tick.get(
                "asks"
            )
            or []
        )

        best_bid = (
            float(
                bids[0][0]
            )
            if bids
            else None
        )

        best_ask = (
            float(
                asks[0][0]
            )
            if asks
            else None
        )

        return {
            "rest_success": (
                payload.get(
                    "status"
                )
                == "ok"
            ),
            "best_bid": best_bid,
            "best_ask": best_ask,
            "bid_levels": len(
                bids
            ),
            "ask_levels": len(
                asks
            ),
            "seconds": round(
                time.perf_counter()
                - started,
                4,
            ),
            "reason": None,
        }

    except Exception as exc:
        return {
            "rest_success": False,
            "best_bid": None,
            "best_ask": None,
            "bid_levels": 0,
            "ask_levels": 0,
            "seconds": round(
                time.perf_counter()
                - started,
                4,
            ),
            "reason": (
                f"{type(exc).__name__}: "
                f"{exc}"
            ),
        }


async def watch_one(symbol):
    native = native_symbol(
        symbol
    )

    started = time.perf_counter()

    result = {
        "websocket_ack": False,
        "bbo_received": False,
        "best_bid": None,
        "best_ask": None,
        "bid_size": None,
        "ask_size": None,
        "seconds": None,
        "message_count": 0,
        "reason": None,
    }

    try:
        async with (
            aiohttp.ClientSession()
            as session
        ):
            async with session.ws_connect(
                WS_URL,
                heartbeat=None,
                receive_timeout=5.0,
            ) as ws:

                await ws.send_json({
                    "sub": (
                        f"market."
                        f"{native}"
                        f".bbo"
                    ),
                    "id": (
                        f"arbos-{native}"
                    ),
                })

                deadline = (
                    time.monotonic()
                    + 12.0
                )

                while (
                    time.monotonic()
                    < deadline
                ):
                    remaining = (
                        deadline
                        - time.monotonic()
                    )

                    try:
                        message = (
                            await asyncio.wait_for(
                                ws.receive(),
                                timeout=min(
                                    remaining,
                                    3.0,
                                ),
                            )
                        )
                    except asyncio.TimeoutError:
                        continue

                    if message.type in {
                        aiohttp.WSMsgType.CLOSE,
                        aiohttp.WSMsgType.CLOSED,
                        aiohttp.WSMsgType.ERROR,
                    }:
                        break

                    payload = decode_message(
                        message
                    )

                    if not isinstance(
                        payload,
                        dict,
                    ):
                        continue

                    result[
                        "message_count"
                    ] += 1

                    if "ping" in payload:
                        await ws.send_json({
                            "pong": (
                                payload[
                                    "ping"
                                ]
                            )
                        })
                        continue

                    if (
                        payload.get(
                            "status"
                        )
                        == "ok"
                        and "subbed"
                        in payload
                    ):
                        result[
                            "websocket_ack"
                        ] = True
                        continue

                    channel = str(
                        payload.get(
                            "ch"
                        )
                        or ""
                    )

                    if not channel.endswith(
                        ".bbo"
                    ):
                        continue

                    tick = (
                        payload.get(
                            "tick"
                        )
                        or {}
                    )

                    try:
                        bid = float(
                            tick.get(
                                "bid"
                            )
                        )

                        ask = float(
                            tick.get(
                                "ask"
                            )
                        )

                        bid_size = float(
                            tick.get(
                                "bidSize"
                            )
                        )

                        ask_size = float(
                            tick.get(
                                "askSize"
                            )
                        )

                    except (
                        TypeError,
                        ValueError,
                    ):
                        continue

                    if (
                        bid <= 0
                        or ask <= 0
                    ):
                        continue

                    result.update({
                        "bbo_received": True,
                        "best_bid": bid,
                        "best_ask": ask,
                        "bid_size": bid_size,
                        "ask_size": ask_size,
                    })

                    break

    except Exception as exc:
        result["reason"] = (
            f"{type(exc).__name__}: "
            f"{exc}"
        )

    result["seconds"] = round(
        time.perf_counter()
        - started,
        4,
    )

    return result


async def main():
    print(
        "=============================================="
    )
    print(
        " ArbOS EX-363 — HTX MISSING BBO DIAGNOSTIC"
    )
    print(
        "=============================================="
    )
    print(
        "LIVE TRADING: DISABLED"
    )
    print()

    catalogue = fetch_catalogue()

    rows = []

    for symbol in SYMBOLS:
        native = native_symbol(
            symbol
        )

        print(
            f"Testing {symbol}..."
        )

        catalogue_record = (
            catalogue.get(
                native,
                {}
            )
        )

        depth = fetch_depth(
            symbol
        )

        websocket = (
            await watch_one(
                symbol
            )
        )

        row = {
            "symbol": symbol,
            "native_symbol": native,
            "catalogue_state": (
                catalogue_record.get(
                    "state"
                )
            ),
            "api_trading": (
                catalogue_record.get(
                    "api_trading"
                )
            ),
            "rest_depth": depth,
            "isolated_websocket": (
                websocket
            ),
        }

        rows.append(
            row
        )

    summary = {
        "symbol_count": len(
            SYMBOLS
        ),
        "rest_depth_available": len([
            row
            for row in rows
            if (
                row[
                    "rest_depth"
                ][
                    "rest_success"
                ]
                is True
            )
        ]),
        "isolated_bbo_available": len([
            row
            for row in rows
            if (
                row[
                    "isolated_websocket"
                ][
                    "bbo_received"
                ]
                is True
            )
        ]),
        "results": rows,
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


if __name__ == "__main__":
    asyncio.run(
        main()
    )
