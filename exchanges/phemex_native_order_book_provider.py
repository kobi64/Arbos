"""
ArbOS™
EX-232
Phemex Native Order Book Provider

Connects the verified Phemex spot-order-book adapter to the
standard ArbOS™ snapshot(symbol, limit) interface.

Read-only market data.
No authentication.
No transfers.
No live orders.
"""


class PhemexNativeOrderBookProvider:
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
            limit = 30

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
                "Phemex order book unavailable: "
                f"{reason}"
            )

        return {
            "exchange": "phemex",
            "symbol": symbol,
            "native_symbol": result.get(
                "native_symbol"
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
            "bid_timestamps": result.get(
                "bid_timestamps",
                [],
            ),
            "ask_timestamps": result.get(
                "ask_timestamps",
                [],
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }
