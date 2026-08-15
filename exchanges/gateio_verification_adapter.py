"""
ArbOS™
EX-224
Gate.io Verification Adapter

Normalizes Gate.io native order-book depth into the
standard ArbOS verification representation.

Read-only.
No authentication.
No orders.
No transfers.
"""


class GateIOVerificationAdapter:
    def __init__(self, client):
        if client is None:
            raise ValueError(
                "client is required"
            )

        self._client = client

    @staticmethod
    def _normalize_levels(levels):
        normalized = []
        timestamps = []

        for level in levels:
            if (
                not isinstance(level, (list, tuple))
                or len(level) < 2
            ):
                raise ValueError(
                    "invalid order book level"
                )

            price = float(level[0])
            quantity = float(level[1])

            if price <= 0:
                raise ValueError(
                    "price must be positive"
                )

            if quantity < 0:
                raise ValueError(
                    "quantity must not be negative"
                )

            normalized.append([
                price,
                quantity,
            ])

            timestamps.append(
                level[2]
                if len(level) >= 3
                else None
            )

        return normalized, timestamps

    def fetch_order_book(
        self,
        symbol,
        limit=20,
    ):
        raw = self._client.fetch_order_book(
            symbol,
            limit=limit,
        )

        if raw.get(
            "fetch_complete"
        ) is not True:
            return {
                "verification_available": False,
                "verified": False,
                "symbol": symbol,
                "best_bid": None,
                "best_ask": None,
                "bids": [],
                "asks": [],
                "bid_timestamps": [],
                "ask_timestamps": [],
                "reason": raw.get(
                    "reason",
                    "order_book_unavailable",
                ),
                "paper_only": True,
                "live_order_submitted": False,
            }

        try:
            bids, bid_timestamps = (
                self._normalize_levels(
                    raw.get(
                        "bids",
                        [],
                    )
                )
            )

            asks, ask_timestamps = (
                self._normalize_levels(
                    raw.get(
                        "asks",
                        [],
                    )
                )
            )

            if not bids or not asks:
                raise ValueError(
                    "empty order book"
                )

            best_bid = bids[0][0]
            best_ask = asks[0][0]

            if best_bid >= best_ask:
                raise ValueError(
                    "crossed or locked order book"
                )

            return {
                "verification_available": True,
                "verified": True,
                "symbol": symbol,
                "best_bid": best_bid,
                "best_ask": best_ask,
                "bids": bids,
                "asks": asks,
                "bid_timestamps": bid_timestamps,
                "ask_timestamps": ask_timestamps,
                "reason": None,
                "paper_only": True,
                "live_order_submitted": False,
            }

        except Exception as exc:
            return {
                "verification_available": False,
                "verified": False,
                "symbol": symbol,
                "best_bid": None,
                "best_ask": None,
                "bids": [],
                "asks": [],
                "bid_timestamps": [],
                "ask_timestamps": [],
                "reason": (
                    f"{type(exc).__name__}: {exc}"
                ),
                "paper_only": True,
                "live_order_submitted": False,
            }
