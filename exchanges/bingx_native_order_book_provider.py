"""
ArbOS™
EX-222
BingX Native Order Book Provider

Connects the verified BingX order-book adapter to the
standard ArbOS™ snapshot(symbol, limit) interface.

Read-only market data.
No authentication.
No transfers.
No live orders.
"""


class BingXNativeOrderBookProvider:
    def __init__(
        self,
        adapter,
    ):
        if adapter is None:
            raise ValueError(
                "adapter is required"
            )

        self._adapter = adapter

    def snapshot(
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

        if limit is None:
            limit = 20

        result = (
            self._adapter.fetch_order_book(
                symbol,
                limit=limit,
            )
        )

        if (
            result.get(
                "verification_available"
            )
            is not True
            or result.get(
                "verified"
            )
            is not True
        ):
            reason = result.get(
                "reason",
                "unknown",
            )

            raise RuntimeError(
                "BingX order book unavailable: "
                f"{reason}"
            )

        return {
            "exchange": "bingx",
            "symbol": symbol,
            "timestamp": result.get(
                "timestamp"
            ),
            "last_update_id": result.get(
                "last_update_id"
            ),
            "best_bid": result.get(
                "best_bid"
            ),
            "best_ask": result.get(
                "best_ask"
            ),
            "bids": result.get(
                "bids",
                [],
            ),
            "asks": result.get(
                "asks",
                [],
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }
