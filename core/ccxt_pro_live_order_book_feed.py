"""
ArbOS™
EX-206
CCXT Pro Live Order Book Feed

Consumes public CCXT Pro WebSocket order-book updates,
normalizes them into ArbOS™ live-market snapshots, and
submits accepted updates into the live market data intake
pipeline.

Maintains an ArbOS-local monotonic sequence per feed
instance while preserving the exchange/native nonce as
source_sequence.

Public market data only.
No authentication.
No transfers.
No live orders.
"""

import time


class CCXTProLiveOrderBookFeed:
    def __init__(
        self,
        exchange,
        intake_service,
        clock=None,
    ):
        if exchange is None:
            raise ValueError(
                "exchange is required"
            )

        if intake_service is None:
            raise ValueError(
                "intake_service is required"
            )

        self._exchange = exchange
        self._intake_service = (
            intake_service
        )
        self._clock = (
            clock
            if clock is not None
            else time.time
        )

        self._sequence = 0

    async def watch_once(
        self,
        symbol,
        limit=None,
    ):
        symbol = str(
            symbol
            or ""
        ).strip().upper()

        if not symbol:
            raise ValueError(
                "symbol is required"
            )

        order_book = await (
            self._exchange.watch_order_book(
                symbol,
                limit=limit,
            )
        )

        if not isinstance(
            order_book,
            dict,
        ):
            raise ValueError(
                "order book unavailable"
            )

        bids = (
            order_book.get(
                "bids"
            )
            or []
        )

        asks = (
            order_book.get(
                "asks"
            )
            or []
        )

        if not bids or not asks:
            raise ValueError(
                "order book unavailable"
            )

        self._sequence += 1

        timestamp = order_book.get(
            "timestamp"
        )

        if timestamp is None:
            timestamp = float(
                self._clock()
            )

        exchange_id = str(
            getattr(
                self._exchange,
                "id",
                "",
            )
            or ""
        ).strip().lower()

        if not exchange_id:
            raise ValueError(
                "exchange_id is required"
            )

        best_bid = float(
            bids[0][0]
        )

        best_ask = float(
            asks[0][0]
        )

        snapshot = {
            "exchange_id": (
                exchange_id
            ),
            "symbol": symbol,
            "sequence": (
                self._sequence
            ),
            "source_sequence": (
                order_book.get(
                    "nonce"
                )
            ),
            "timestamp": timestamp,
            "datetime": (
                order_book.get(
                    "datetime"
                )
            ),
            "bids": bids,
            "asks": asks,
            "best_bid": (
                best_bid
            ),
            "best_ask": (
                best_ask
            ),
            "bid": best_bid,
            "ask": best_ask,
            "paper_only": True,
            "live_order_submitted": False,
        }

        result = (
            self._intake_service.submit(
                snapshot
            )
        )

        return {
            **result,
            "exchange_id": (
                exchange_id
            ),
            "symbol": symbol,
            "sequence": (
                self._sequence
            ),
            "source_sequence": (
                order_book.get(
                    "nonce"
                )
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }
