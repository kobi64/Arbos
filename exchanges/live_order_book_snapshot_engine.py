"""
ArbOS™
EX-090
Live Order Book Snapshot Engine
"""


class LiveOrderBookSnapshotEngine:
    def __init__(self, exchange):
        self._exchange = exchange

    def snapshot(self, symbol, limit=None):
        if symbol is None or not str(symbol).strip():
            raise ValueError("symbol is required")

        order_book = self._exchange.fetch_order_book(
            str(symbol).strip(),
            limit=limit,
        )

        bids = order_book.get("bids") or []
        asks = order_book.get("asks") or []

        if not bids or not asks:
            raise ValueError("order book unavailable")

        return {
            "symbol": str(symbol).strip(),
            "bids": bids,
            "asks": asks,
            "best_bid": float(bids[0][0]),
            "best_ask": float(asks[0][0]),
            "timestamp": order_book.get("timestamp"),
            "datetime": order_book.get("datetime"),
        }
