"""
ArbOS™

EX-362
HTX Native BBO WebSocket Diagnostic

Tests HTX native public spot WebSocket:
    market.$symbol.bbo

Goal:
- 100 active USDT spot markets
- native best bid/ask only
- no REST order-book synchronization
- no CCXT Pro order-book snapshot dependency

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

import ccxt


REQUESTED_COINS = 100

WS_URL = "wss://api.huobi.pro/ws"

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
    if message.type == (
        aiohttp.WSMsgType.BINARY
    ):
        raw = gzip.decompress(
            message.data
        )

        return json.loads(
            raw.decode("utf-8")
        )

    if message.type == (
        aiohttp.WSMsgType.TEXT
    ):
        return json.loads(
            message.data
        )

    return None


def parse_bbo(payload):
    if not isinstance(
        payload,
        dict,
    ):
        return None

    channel = str(
        payload.get("ch")
        or ""
    ).strip()

    if not channel.endswith(
        ".bbo"
    ):
        return None

    tick = payload.get(
        "tick"
    )

    if not isinstance(
        tick,
        dict,
    ):
        return None

    bid = tick.get(
        "bid"
    )

    ask = tick.get(
        "ask"
    )

    bid_size = tick.get(
        "bidSize"
    )

    ask_size = tick.get(
        "askSize"
    )

    try:
        # HTX spot BBO format:
        # bid/ask are scalar prices and
        # bidSize/askSize are scalar sizes.
        #
        # Also tolerate the older/alternate
        # [price, size] representation.

        if isinstance(
            bid,
            (list, tuple),
        ):
            if len(bid) < 2:
                return None

            best_bid = float(
                bid[0]
            )

            bid_size = float(
                bid[1]
            )

        else:
            best_bid = float(
                bid
            )

            bid_size = float(
                bid_size
            )

        if isinstance(
            ask,
            (list, tuple),
        ):
            if len(ask) < 2:
                return None

            best_ask = float(
                ask[0]
            )

            ask_size = float(
                ask[1]
            )

        else:
            best_ask = float(
                ask
            )

            ask_size = float(
                ask_size
            )

    except (
        TypeError,
        ValueError,
    ):
        return None

    if (
        best_bid <= 0
        or best_ask <= 0
        or bid_size < 0
        or ask_size < 0
    ):
        return None

    return {
        "channel": channel,
        "symbol": tick.get(
            "symbol"
        ),
        "best_bid": best_bid,
        "best_ask": best_ask,
        "bid_size": bid_size,
        "ask_size": ask_size,
        "timestamp": (
            tick.get(
                "quoteTime"
            )
            or tick.get(
                "ts"
            )
            or payload.get(
                "ts"
            )
        ),
        "sequence": (
            tick.get(
                "seqId"
            )
            or tick.get(
                "version"
            )
        ),
    }


async def main():
    print(
        "=============================================="
    )
    print(
        " ArbOS EX-362 — HTX NATIVE BBO TEST"
    )
    print(
        "=============================================="
    )
    print(
        "LIVE TRADING: DISABLED"
    )
    print()

    exchange = ccxt.htx({
        "enableRateLimit": True,
    })

    try:
        markets = exchange.load_markets()
    finally:
        exchange.close()

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

    if len(symbols) < REQUESTED_COINS:
        raise RuntimeError(
            "fewer than 100 eligible HTX symbols"
        )

    print(
        "Selected symbols:",
        len(symbols),
    )

    print(
        "WebSocket:",
        WS_URL,
    )

    print()

    symbol_by_native = {
        native_symbol(symbol): symbol
        for symbol in symbols
    }

    received = {}

    subscription_acks = 0

    malformed_bbo = 0

    other_messages = 0

    started = time.perf_counter()

    timeout_seconds = 30.0

    async with (
        aiohttp.ClientSession()
        as session
    ):
        async with session.ws_connect(
            WS_URL,
            heartbeat=None,
            receive_timeout=10.0,
        ) as ws:

            for index, symbol in enumerate(
                symbols
            ):
                native = native_symbol(
                    symbol
                )

                await ws.send_json({
                    "sub": (
                        f"market."
                        f"{native}"
                        f".bbo"
                    ),
                    "id": (
                        f"arbos-{index}"
                    ),
                })

                # Small subscription pacing.
                if (
                    (index + 1) % 20
                    == 0
                ):
                    await asyncio.sleep(
                        0.2
                    )

            deadline = (
                time.monotonic()
                + timeout_seconds
            )

            while (
                len(received)
                < len(symbols)
            ):
                remaining = (
                    deadline
                    - time.monotonic()
                )

                if remaining <= 0:
                    break

                try:
                    message = (
                        await asyncio.wait_for(
                            ws.receive(),
                            timeout=min(
                                5.0,
                                remaining,
                            ),
                        )
                    )

                except asyncio.TimeoutError:
                    continue

                if message.type in {
                    aiohttp.WSMsgType.CLOSED,
                    aiohttp.WSMsgType.CLOSE,
                    aiohttp.WSMsgType.ERROR,
                }:
                    break

                try:
                    payload = (
                        decode_message(
                            message
                        )
                    )
                except Exception:
                    malformed_bbo += 1
                    continue

                if not isinstance(
                    payload,
                    dict,
                ):
                    continue

                # HTX heartbeat.
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
                    subscription_acks += 1
                    continue

                parsed = parse_bbo(
                    payload
                )

                if parsed is None:
                    other_messages += 1
                    continue

                channel = parsed[
                    "channel"
                ]

                parts = (
                    channel.split(".")
                )

                if len(parts) < 3:
                    malformed_bbo += 1
                    continue

                native = parts[1]

                symbol = (
                    symbol_by_native.get(
                        native
                    )
                )

                if symbol is None:
                    other_messages += 1
                    continue

                received[
                    symbol
                ] = {
                    "symbol": symbol,
                    **parsed,
                }

    elapsed = (
        time.perf_counter()
        - started
    )

    missing = [
        symbol
        for symbol in symbols
        if symbol not in received
    ]

    samples = list(
        received.values()
    )[:10]

    result = {
        "requested_symbol_count": (
            len(symbols)
        ),
        "subscription_acks": (
            subscription_acks
        ),
        "received_bbo_count": (
            len(received)
        ),
        "received_percent": round(
            (
                len(received)
                / len(symbols)
                * 100.0
            ),
            2,
        ),
        "missing_count": (
            len(missing)
        ),
        "missing_symbols": (
            missing
        ),
        "malformed_bbo_count": (
            malformed_bbo
        ),
        "other_message_count": (
            other_messages
        ),
        "seconds": round(
            elapsed,
            4,
        ),
        "sample_bbo": (
            samples
        ),
        "paper_only": True,
        "live_order_submitted": False,
    }

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
            result,
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
