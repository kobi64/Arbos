"""
ArbOS™
EX-222
BingX Verification Adapter

Normalizes BingX public spot order-book data into
the standard ArbOS™ verification structure.

Read-only.
No authentication.
No transfers.
No live orders.
"""


class BingXVerificationAdapter:
    def __init__(
        self,
        client,
    ):
        if client is None:
            raise ValueError(
                "client is required"
            )

        self._client = client

    def fetch_order_book(
        self,
        symbol,
        limit=20,
    ):
        raw = self._client.fetch_order_book(
            symbol,
            limit=limit,
        )

        if (
            raw.get(
                "fetch_complete"
            )
            is not True
        ):
            return {
                "verification_available": False,
                "verified": False,
                "symbol": raw.get(
                    "symbol"
                ),
                "best_bid": None,
                "best_ask": None,
                "bids": [],
                "asks": [],
                "timestamp": raw.get(
                    "timestamp"
                ),
                "last_update_id": raw.get(
                    "last_update_id"
                ),
                "reason": raw.get(
                    "reason",
                    "order_book_unavailable",
                ),
                "paper_only": True,
                "live_order_submitted": False,
            }

        bids = self._normalize_levels(
            raw.get(
                "bids",
                [],
            )
        )

        asks = self._normalize_levels(
            raw.get(
                "asks",
                [],
            )
        )

        if (
            not bids
            or not asks
        ):
            return {
                "verification_available": False,
                "verified": False,
                "symbol": raw.get(
                    "symbol"
                ),
                "best_bid": None,
                "best_ask": None,
                "bids": [],
                "asks": [],
                "timestamp": raw.get(
                    "timestamp"
                ),
                "last_update_id": raw.get(
                    "last_update_id"
                ),
                "reason": "empty_order_book",
                "paper_only": True,
                "live_order_submitted": False,
            }

        return {
            "verification_available": True,
            "verified": True,
            "symbol": raw.get(
                "symbol"
            ),
            "best_bid": bids[0][0],
            "best_ask": asks[0][0],
            "bids": bids,
            "asks": asks,
            "timestamp": raw.get(
                "timestamp"
            ),
            "last_update_id": raw.get(
                "last_update_id"
            ),
            "reason": None,
            "paper_only": True,
            "live_order_submitted": False,
        }

    @staticmethod
    def _normalize_levels(
        levels,
    ):
        result = []

        for level in levels:
            if (
                not isinstance(
                    level,
                    (list, tuple),
                )
                or len(level) < 2
            ):
                continue

            try:
                price = float(
                    level[0]
                )
                quantity = float(
                    level[1]
                )
            except (
                TypeError,
                ValueError,
            ):
                continue

            if (
                price <= 0
                or quantity < 0
            ):
                continue

            result.append([
                price,
                quantity,
            ])

        return result
