"""
ArbOS™

EX-364
HTX Native BBO Feed

Production public best-bid/best-ask WebSocket feed.

Uses:
    wss://api.huobi.pro/ws
    market.<symbol>.bbo

The feed submits normalized market snapshots directly
into ArbOS LiveMarketDataIntakeService.

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


class HTXNativeBBOFeed:
    DEFAULT_URL = (
        "wss://api.huobi.pro/ws"
    )

    def __init__(
        self,
        intake_service,
        symbols,
        websocket_url=None,
        session_factory=None,
    ):
        if intake_service is None:
            raise ValueError(
                "intake_service is required"
            )

        symbols = [
            str(symbol)
            .strip()
            .upper()
            for symbol in (
                symbols
                or []
            )
            if str(symbol).strip()
        ]

        if not symbols:
            raise ValueError(
                "symbols are required"
            )

        self._intake = (
            intake_service
        )

        self._symbols = list(
            dict.fromkeys(
                symbols
            )
        )

        self._websocket_url = (
            str(
                websocket_url
                or self.DEFAULT_URL
            )
            .strip()
        )

        if not self._websocket_url:
            raise ValueError(
                "websocket_url is required"
            )

        self._session_factory = (
            session_factory
            or aiohttp.ClientSession
        )

        self._sequence = 0

    @staticmethod
    def _native_symbol(
        symbol,
    ):
        value = (
            str(symbol)
            .strip()
            .lower()
            .replace("/", "")
            .replace("-", "")
            .replace("_", "")
        )

        if not value:
            raise ValueError(
                "symbol is required"
            )

        return value

    @staticmethod
    def _decode_message(
        message,
    ):
        if (
            message.type
            == aiohttp.WSMsgType.BINARY
        ):
            raw = gzip.decompress(
                message.data
            )

            return json.loads(
                raw.decode(
                    "utf-8"
                )
            )

        if (
            message.type
            == aiohttp.WSMsgType.TEXT
        ):
            return json.loads(
                message.data
            )

        return None

    @staticmethod
    def _extract_symbol_from_channel(
        channel,
    ):
        channel = str(
            channel
            or ""
        ).strip().lower()

        prefix = "market."
        suffix = ".bbo"

        if (
            not channel.startswith(
                prefix
            )
            or not channel.endswith(
                suffix
            )
        ):
            return None

        native = channel[
            len(prefix):
            -len(suffix)
        ]

        if not native:
            return None

        return native

    def _symbol_mapping(self):
        return {
            self._native_symbol(
                symbol
            ): symbol
            for symbol
            in self._symbols
        }

    def _normalize_bbo(
        self,
        payload,
        symbol_mapping,
    ):
        if not isinstance(
            payload,
            dict,
        ):
            return None

        channel = str(
            payload.get(
                "ch"
            )
            or ""
        )

        native = (
            self._extract_symbol_from_channel(
                channel
            )
        )

        if native is None:
            return None

        symbol = (
            symbol_mapping.get(
                native
            )
        )

        if symbol is None:
            return None

        tick = (
            payload.get(
                "tick"
            )
            or {}
        )

        try:
            best_bid = float(
                tick.get(
                    "bid"
                )
            )

            best_ask = float(
                tick.get(
                    "ask"
                )
            )

            bid_size = float(
                tick.get(
                    "bidSize",
                    0.0,
                )
                or 0.0
            )

            ask_size = float(
                tick.get(
                    "askSize",
                    0.0,
                )
                or 0.0
            )

        except (
            TypeError,
            ValueError,
        ):
            return None

        if (
            best_bid <= 0
            or best_ask <= 0
        ):
            return None

        if best_bid >= best_ask:
            return None

        self._sequence += 1

        timestamp = (
            tick.get(
                "ts"
            )
            or payload.get(
                "ts"
            )
        )

        if timestamp is None:
            timestamp = (
                time.time()
                * 1000.0
            )

        return {
            "exchange_id": "htx",
            "symbol": symbol,
            "sequence": (
                self._sequence
            ),
            "timestamp": (
                float(timestamp)
                / 1000.0
            ),
            "bid": best_bid,
            "ask": best_ask,
            "best_bid": best_bid,
            "best_ask": best_ask,
            "bid_size": bid_size,
            "ask_size": ask_size,
            "bids": [
                [
                    best_bid,
                    bid_size,
                ]
            ],
            "asks": [
                [
                    best_ask,
                    ask_size,
                ]
            ],
            "source": (
                "htx_native_bbo"
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

    async def _subscribe(
        self,
        websocket,
    ):
        for symbol in self._symbols:
            native = (
                self._native_symbol(
                    symbol
                )
            )

            await websocket.send_json({
                "sub": (
                    f"market."
                    f"{native}"
                    f".bbo"
                ),
                "id": (
                    f"arbos-{native}"
                ),
            })

    async def run_once(
        self,
        duration_seconds=5.0,
    ):
        duration_seconds = float(
            duration_seconds
        )

        if duration_seconds <= 0:
            raise ValueError(
                "duration_seconds must be positive"
            )

        symbol_mapping = (
            self._symbol_mapping()
        )

        started = (
            time.monotonic()
        )

        subscription_acks = 0
        submitted_updates = 0
        malformed_messages = 0
        ping_count = 0
        received_symbols = set()

        async with (
            self._session_factory()
            as session
        ):
            async with session.ws_connect(
                self._websocket_url,
                heartbeat=None,
            ) as websocket:

                await self._subscribe(
                    websocket
                )

                deadline = (
                    time.monotonic()
                    + duration_seconds
                )

                while (
                    time.monotonic()
                    < deadline
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
                                websocket.receive(),
                                timeout=min(
                                    remaining,
                                    1.0,
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

                    try:
                        payload = (
                            self._decode_message(
                                message
                            )
                        )
                    except Exception:
                        malformed_messages += 1
                        continue

                    if not isinstance(
                        payload,
                        dict,
                    ):
                        continue

                    if "ping" in payload:
                        ping_count += 1

                        await websocket.send_json({
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

                    snapshot = (
                        self._normalize_bbo(
                            payload,
                            symbol_mapping,
                        )
                    )

                    if snapshot is None:
                        continue

                    self._intake.submit(
                        snapshot
                    )

                    submitted_updates += 1

                    received_symbols.add(
                        snapshot[
                            "symbol"
                        ]
                    )

        missing_symbols = sorted(
            set(
                self._symbols
            )
            - received_symbols
        )

        return {
            "exchange_id": "htx",
            "requested_symbol_count": (
                len(
                    self._symbols
                )
            ),
            "subscription_acks": (
                subscription_acks
            ),
            "submitted_update_count": (
                submitted_updates
            ),
            "received_symbol_count": (
                len(
                    received_symbols
                )
            ),
            "missing_symbol_count": (
                len(
                    missing_symbols
                )
            ),
            "missing_symbols": (
                missing_symbols
            ),
            "malformed_message_count": (
                malformed_messages
            ),
            "ping_count": ping_count,
            "seconds": round(
                time.monotonic()
                - started,
                4,
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }
