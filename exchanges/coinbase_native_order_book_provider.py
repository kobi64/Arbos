"""
ArbOS™
EX-235
Coinbase Native Order Book Provider

Connects the verified Coinbase Level-2 order-book adapter to the
standard ArbOS™ snapshot(symbol, limit) interface.

Read-only market data.
No authentication.
No transfers.
No live orders.
"""


class CoinbaseNativeOrderBookProvider:
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

        # Coinbase verification currently uses Level 2.
        level = 2

        result = (
            self._adapter.fetch_order_book(
                symbol,
                level=level,
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
                "Coinbase order book unavailable: "
                f"{reason}"
            )

        return {
            "exchange": "coinbase",
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
            "sequence_id": result.get(
                "sequence_id"
            ),
            "paper_only": True,
            "live_order_submitted": False,
        }
