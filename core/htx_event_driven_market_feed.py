"""
ArbOS™

EX-365
HTX Event-Driven Market Feed

Venue-specific HTX public market-data bridge.

Primary:
HTX native WebSocket BBO.

Fallback:
HTX public REST depth for bootstrap / missing BBO only.

Read-only.
No authentication.
No transfers.
No live orders.
"""

import time

from exchanges.htx_native_bbo_feed import (
    HTXNativeBBOFeed,
)
from exchanges.htx_public_spot_client import (
    HTXPublicSpotClient,
)


class HTXEventDrivenMarketFeed:
    def __init__(
        self,
        intake_service,
        native_feed=None,
        rest_client=None,
    ):
        if intake_service is None:
            raise ValueError(
                "intake_service is required"
            )

        self._intake = intake_service

        self._native_feed = (
            native_feed
            if native_feed is not None
            else HTXNativeBBOFeed()
        )

        self._rest_client = (
            rest_client
            if rest_client is not None
            else HTXPublicSpotClient()
        )

        self._sequence = 0

    @staticmethod
    def _normalize_symbol(
        symbol,
    ):
        value = str(
            symbol or ""
        ).strip().upper()

        if not value:
            raise ValueError(
                "symbol is required"
            )

        return value

    def _next_sequence(self):
        self._sequence += 1
        return self._sequence

    def submit_bbo(
        self,
        update,
    ):
        if not isinstance(
            update,
            dict,
        ):
            raise ValueError(
                "update must be a dict"
            )

        symbol = self._normalize_symbol(
            update.get("symbol")
        )

        bid = float(
            update.get(
                "best_bid",
                update.get("bid"),
            )
        )

        ask = float(
            update.get(
                "best_ask",
                update.get("ask"),
            )
        )

        if bid <= 0:
            raise ValueError(
                "bid must be positive"
            )

        if ask <= 0:
            raise ValueError(
                "ask must be positive"
            )

        if bid >= ask:
            raise ValueError(
                "crossed or locked market"
            )

        timestamp = update.get(
            "timestamp"
        )

        if timestamp is None:
            timestamp = time.time()

        sequence = update.get(
            "sequence"
        )

        if sequence is None:
            sequence = (
                self._next_sequence()
            )

        snapshot = {
            "exchange_id": "htx",
            "symbol": symbol,
            "sequence": sequence,
            "timestamp": timestamp,
            "bid": bid,
            "ask": ask,
            "best_bid": bid,
            "best_ask": ask,
            "bids": [
                [
                    bid,
                    float(
                        update.get(
                            "bid_size",
                            0.0,
                        )
                        or 0.0
                    ),
                ],
            ],
            "asks": [
                [
                    ask,
                    float(
                        update.get(
                            "ask_size",
                            0.0,
                        )
                        or 0.0
                    ),
                ],
            ],
            "market_data_source": (
                "HTX_NATIVE_BBO"
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

        return self._intake.submit(
            snapshot
        )

    def bootstrap_symbol(
        self,
        symbol,
        limit=20,
    ):
        symbol = self._normalize_symbol(
            symbol
        )

        result = (
            self._rest_client
            .fetch_order_book(
                symbol,
                limit=limit,
            )
        )

        if (
            result.get(
                "fetch_complete"
            )
            is not True
        ):
            return {
                "submitted": False,
                "exchange_id": "htx",
                "symbol": symbol,
                "reason": result.get(
                    "reason",
                    "rest_depth_unavailable",
                ),
                "paper_only": True,
                "live_order_submitted": False,
            }

        bids = (
            result.get("bids")
            or []
        )

        asks = (
            result.get("asks")
            or []
        )

        if not bids or not asks:
            return {
                "submitted": False,
                "exchange_id": "htx",
                "symbol": symbol,
                "reason": (
                    "rest_depth_empty"
                ),
                "paper_only": True,
                "live_order_submitted": False,
            }

        bid = float(
            bids[0][0]
        )

        ask = float(
            asks[0][0]
        )

        if (
            bid <= 0
            or ask <= 0
            or bid >= ask
        ):
            return {
                "submitted": False,
                "exchange_id": "htx",
                "symbol": symbol,
                "reason": (
                    "rest_depth_invalid"
                ),
                "paper_only": True,
                "live_order_submitted": False,
            }

        timestamp = result.get(
            "timestamp"
        )

        if timestamp is None:
            timestamp = time.time()

        snapshot = {
            "exchange_id": "htx",
            "symbol": symbol,
            "sequence": (
                self._next_sequence()
            ),
            "timestamp": timestamp,
            "bid": bid,
            "ask": ask,
            "best_bid": bid,
            "best_ask": ask,
            "bids": bids,
            "asks": asks,
            "market_data_source": (
                "HTX_REST_DEPTH_BOOTSTRAP"
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }

        dispatch = (
            self._intake.submit(
                snapshot
            )
        )

        return {
            "submitted": True,
            "exchange_id": "htx",
            "symbol": symbol,
            "snapshot": snapshot,
            "dispatch": dispatch,
            "reason": None,
            "paper_only": True,
            "live_order_submitted": False,
        }

    def bootstrap_symbols(
        self,
        symbols,
        limit=20,
    ):
        results = []

        for symbol in symbols:
            results.append(
                self.bootstrap_symbol(
                    symbol,
                    limit=limit,
                )
            )

        return {
            "exchange_id": "htx",
            "requested_count": len(
                list(symbols)
            )
            if not isinstance(
                symbols,
                list,
            )
            else len(symbols),
            "submitted_count": sum(
                1
                for result in results
                if result.get(
                    "submitted"
                ) is True
            ),
            "results": results,
            "paper_only": True,
            "live_order_submitted": False,
        }
